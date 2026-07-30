"""CB-5: build and score every pre-registered cell, in the prereg's own order.

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md
Pre-registration: docs/superpowers/specs/2026-07-30-track-b-cap-selection-preregistration.md
(`CRS-`). This module ORCHESTRATES; every measurement it reports is produced by
the three gated modules (cb_build_variants, cb_metrics, cb_paths) or defined
verbatim in the prereg (`CRS-C6`, `CRS-H1`, `CRS-H2`, `CRS-G2`, `CRS-A5`).
It computes no criterion verdict — CB-6 reads the JSON this writes.

PHASES, run in this order (the order is load-bearing, CRS-A2):

    --phase dryrun     Scorer shakedown on ALG-E-MK50 alone (the Track A
                       scorer-defect lesson: the fix cannot be shaped by a
                       result that does not exist yet). Pairs restricted to
                       that one cell; nothing here is the scored record.
    --phase build      Build all 24 cells. Existing byte-deterministic cells
                       are kept (the handoff allows keep-or-rebuild). UC cells
                       run under CRS-G4's 30-minute cap in a subprocess so an
                       exhaustion degrades to a diagnostic row, not a crash.
    --phase ties       CRS-H1 tie prevalence + CRS-H2 quota-frame disagreement,
                       one archive per invocation (--archive) to bound memory.
                       The trimmed_union instrumentation is a copy of the gated
                       trim loop and is VALIDATED per cell: its surviving edge
                       set must equal the built artifact's, exactly.
    --phase baseline   Draw the pair set (fixed seed, routable in every cell,
                       drawn once — prereg §0), then score ALG-E-MK50's C5
                       per class FIRST, before any other cell's C5 is opened
                       (CRS-A2). Writes cb_pairs.json + cb_c5_baseline.json.
    --phase score      Everything else: structural + path metrics per cell,
                       CRS-G2 bound verification, CRS-C6 survival split,
                       CRS-A5 endpoint re-verification (+ descriptive
                       companion), merge of the ties files. Writes
                       cb_scores.json. Other cells' C5 values land in the
                       JSON unprinted; they are opened only in CB-6, after
                       the CRS-A2 protocol has resolved.

TIE-PREVALENCE OPERATIONALISATION (CRS-H1 names the quantity, not the formula;
fixed here before any cell's ties are computed):
  A node has a BINDING CUT when its rule discards at least one candidate. The
  cut is TIED when the primary key of the last-kept and first-dropped
  candidates is equal — i.e. the MBID tie-break, not the key, decided the
  survivor. Prevalence = tied cuts / binding cuts.
    mutual_knn / proximity_select: per node's own ranked list at position k.
    trimmed_union weakest_first:   symmetric strength at the deletion boundary.
    trimmed_union banded_quota:    the strength-filled portion's boundary
                                   (reserved slots are popularity-selected and
                                   have no strength cut).
  A cell with prevalence > 20% is flagged tie-dominated (prereg §0 CRS-H1).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_run_cells.py --phase dryrun
"""

from __future__ import annotations

import argparse
import gc
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import deserialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import symmetrise
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

from cb_build_variants import (
    ALGORITHMS,
    ARCHIVES,
    CELLS,
    ReadOnlyArchive,
    _assemble,
    _desc,
    _top_j,
    cell_name,
)
from cb_metrics import ADOPTED, crawled_mbids, fame_frame, score_cell, top_degree_node_set
from cb_paths import draw_pairs, routable_everywhere, route_sample  # noqa: F401 (sys.path side effect)

from artistpath_api.config import ApiConfig  # noqa: E402 — path inserted by cb_paths
from artistpath_api.graph_store import GraphStore  # noqa: E402

HERE = Path(__file__).parent

# Prereg §1: 12 cells per archive, identical grids. The fourth column is the
# CONFIGURED ceiling — the matched-bound key and CRS-G2's expectation. UC has
# none, which is the point of it (plan §0 ruling 3).
GRID: list[tuple[str, str, dict, int | None]] = [
    ("MK50", "mutual_knn", {"k": 50}, 50),
    ("MK60", "mutual_knn", {"k": 60}, 60),
    ("MK75", "mutual_knn", {"k": 75}, 75),
    ("MK100", "mutual_knn", {"k": 100}, 100),
    ("TUw-50-50", "trimmed_union", {"j": 50, "d": 50}, 50),
    ("TUw-50-100", "trimmed_union", {"j": 50, "d": 100}, 100),
    ("TUw-100-100", "trimmed_union", {"j": 100, "d": 100}, 100),
    ("TUq-50-50", "trimmed_union", {"j": 50, "d": 50, "trim": "banded_quota"}, 50),
    ("TUq-50-100", "trimmed_union", {"j": 50, "d": 100, "trim": "banded_quota"}, 100),
    ("PS50", "proximity_select", {"k": 50}, 50),
    ("PS100", "proximity_select", {"k": 100}, 100),
    ("UC", "uncapped", {}, None),
]
ARCHIVE_IDS = ("ALG-E", "ALG-B")
UC_TIMEOUT_SECONDS = 1800  # CRS-G4: ≈ 20× a normal build

PAIRS_FILE = HERE / "cb_pairs.json"
BASELINE_FILE = HERE / "cb_c5_baseline.json"
SCORES_FILE = HERE / "cb_scores.json"
BUILD_LOG = HERE / "cb_build_log.json"
RAW_PATHS_FILE = CELLS / "cb_paths_raw.json"  # gitignored with the cells


def cell_key(archive: str, cid: str) -> str:
    return f"{archive}-{cid}"


def cell_paths(archive: str, rule: str, params: dict) -> tuple[Path, Path]:
    name = cell_name(archive, rule, params)
    return CELLS / f"{name}.bin", CELLS / f"{name}.bin.json"


# --------------------------------------------------------------------------
# --phase build
# --------------------------------------------------------------------------


def phase_build() -> None:
    log: dict[str, dict] = {}
    for archive in ARCHIVE_IDS:
        for cid, rule, params, _bound in GRID:
            key = cell_key(archive, cid)
            bin_path, man_path = cell_paths(archive, rule, params)
            if bin_path.exists() and man_path.exists():
                log[key] = {"status": "kept", "file": bin_path.name}
                print(f"{key:18} kept        {bin_path.name}")
                continue
            cmd = [
                sys.executable, "-u", str(HERE / "cb_build_variants.py"),
                "--archive", archive, "--rule", rule,
                "--params", json.dumps(params),
            ]
            started = time.monotonic()
            try:
                proc = subprocess.run(
                    cmd, capture_output=True, text=True,
                    timeout=UC_TIMEOUT_SECONDS,
                )
                elapsed = round(time.monotonic() - started, 1)
                if proc.returncode != 0:
                    log[key] = {
                        "status": "FAILED", "elapsed_seconds": elapsed,
                        "stderr_tail": proc.stderr.splitlines()[-8:],
                    }
                    print(f"{key:18} FAILED ({elapsed}s) — see cb_build_log.json")
                else:
                    log[key] = {"status": "built", "elapsed_seconds": elapsed,
                                "file": bin_path.name}
                    print(f"{key:18} built {elapsed:7.1f}s  {bin_path.name}")
            except subprocess.TimeoutExpired:
                # CRS-G4: report unbuildable; the degraded reference row is the
                # pre-cap degree diagnostics, taken from the ties capture.
                log[key] = {"status": "UNBUILDABLE_CRS_G4",
                            "timeout_seconds": UC_TIMEOUT_SECONDS}
                print(f"{key:18} UNBUILDABLE per CRS-G4 (>{UC_TIMEOUT_SECONDS}s)")
            except MemoryError:
                log[key] = {"status": "UNBUILDABLE_CRS_G4", "reason": "memory"}
                print(f"{key:18} UNBUILDABLE per CRS-G4 (memory)")
    BUILD_LOG.write_text(json.dumps(log, indent=2, sort_keys=True),
                         encoding="utf-8")


# --------------------------------------------------------------------------
# --phase ties  (CRS-H1, CRS-H2)
# --------------------------------------------------------------------------


class _Captured(Exception):
    """Sentinel: the capturing cap step has what it needs."""


def _capture_pipeline(archive: str) -> tuple[dict, dict, dict]:
    """Run _assemble far enough to grab (adjacency, ranking, pop), then stop.

    The captured objects are the exact inputs every cap rule received during
    the real builds — same code path, same archive, byte-deterministic.
    """
    config = BuilderConfig(algorithm=ALGORITHMS[archive])
    source = ListenBrainzSource(config)
    raw = ReadOnlyArchive(LocalArchive(ARCHIVES[archive]))
    box: dict = {}

    def grab(adjacency, ranking, pop):
        box["a"], box["r"], box["p"] = adjacency, ranking, pop
        raise _Captured

    try:
        _assemble(config, raw, source, grab)
    except _Captured:
        pass
    return box["a"], box["r"], box["p"]


def _rank_cut_ties(adjacency: dict, ranking: dict, pop: dict,
                   key_kind: str, k: int) -> dict:
    """Boundary ties for the two by-construction-bounded families."""
    binding = 0
    tied = 0
    for node, edges in adjacency.items():
        if len(edges) <= k:
            continue
        if key_kind == "mutual":
            order = sorted(edges, key=lambda v: (-ranking[node][v], v))
            primary = lambda v: ranking[node][v]  # noqa: E731
        else:  # popularity_proximity
            order = sorted(edges, key=lambda v: (abs(pop[node] - pop[v]), v))
            primary = lambda v: abs(pop[node] - pop[v])  # noqa: E731
        binding += 1
        if primary(order[k - 1]) == primary(order[k]):
            tied += 1
    share = round(tied / binding, 5) if binding else None
    return {
        "nodes_with_binding_cut": binding,
        "tied_cuts": tied,
        "tied_cut_share": share,
        "tie_dominated_CRS_H1": bool(share is not None and share > 0.20),
    }


def _instrumented_trim(adjacency: dict, ranking: dict, pop: dict, *,
                       j: int, d: int, trim: str, quota: float = 0.2,
                       frame: dict | None = None) -> tuple[dict, dict]:
    """cap_trimmed_union's trim loop, instrumented for CRS-H1/H2.

    A COPY, deliberately: editing the gated module would re-trigger CRS-G1.
    Faithfulness is not assumed — the caller validates the surviving edge set
    against the built artifact, exactly, before any number is reported.
    """
    keep = _top_j(ranking, adjacency, j, lambda u, v: (-ranking[u][v], v))
    unioned: dict = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)
    del unioned
    gc.collect()

    def strength(u: str, v: str) -> float:
        return max(ranking.get(u, {}).get(v, float("-inf")),
                   ranking.get(v, {}).get(u, float("-inf")))

    stats = {"trimmed_nodes": 0, "tied_cuts": 0,
             "reserved_slots": 0, "reserved_sub_decile_adopted_frame": 0}

    if trim == "banded_quota":
        ranked_pop = sorted(pop.values())
        cut_index = int(len(ranked_pop) * 0.9)
        decile_threshold = ranked_pop[min(cut_index, len(ranked_pop) - 1)]
        reserve = int(quota * d)

    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - d
        if excess <= 0:
            continue
        stats["trimmed_nodes"] += 1
        if trim == "weakest_first":
            order = sorted(result[node],
                           key=lambda v: (strength(node, v), _desc(v)))
            doomed = order[:excess]
            if strength(node, order[excess - 1]) == strength(node, order[excess]):
                stats["tied_cuts"] += 1
        else:
            by_strength = sorted(result[node],
                                 key=lambda v: (-strength(node, v), v))
            sub_decile = [v for v in by_strength if pop[v] < decile_threshold]
            reserved = set(sub_decile[:reserve])
            rest = [v for v in by_strength if v not in reserved]
            kept_n = d - len(reserved)
            kept = set(list(reserved) + rest[:kept_n])
            doomed = [v for v in by_strength if v not in kept]
            stats["reserved_slots"] += len(reserved)
            if frame is not None:
                stats["reserved_sub_decile_adopted_frame"] += sum(
                    1 for v in reserved if frame.get(v, 1.0) < 0.90
                )
            if 0 < kept_n < len(rest) and strength(node, rest[kept_n - 1]) == strength(node, rest[kept_n]):
                stats["tied_cuts"] += 1
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)
    return result, stats


def _validate_trim(result: dict, bin_path: Path) -> bool:
    """The instrumented copy's edge set must equal the artifact's, exactly."""
    graph = deserialise(bin_path.read_bytes())
    nodes = set(graph.mbids)
    mine = set()
    for u, edges in result.items():
        if u not in nodes:
            continue
        for v in edges:
            if u < v and v in nodes:
                mine.add((u, v))
    built = set()
    index = {i: m for i, m in enumerate(graph.mbids)}
    import numpy as np
    offsets = np.asarray(graph.offsets)
    neighbours = np.asarray(graph.neighbours)
    for i in range(graph.artist_count):
        u = index[i]
        for kk in range(int(offsets[i]), int(offsets[i + 1])):
            v = index[int(neighbours[kk])]
            if u < v:
                built.add((u, v))
    return mine == built


def phase_ties(archive: str) -> None:
    out_file = HERE / f"cb_ties-{archive}.json"
    frame = fame_frame()
    print(f"capturing {archive} pipeline …")
    adjacency, ranking, pop = _capture_pipeline(archive)
    print(f"  captured: {len(adjacency)} nodes")

    results: dict[str, dict] = {}
    for cid, rule, params, _bound in GRID:
        started = time.monotonic()
        if rule == "mutual_knn":
            row = _rank_cut_ties(adjacency, ranking, pop, "mutual", params["k"])
        elif rule == "proximity_select":
            row = _rank_cut_ties(adjacency, ranking, pop, "proximity", params["k"])
        elif rule == "trimmed_union":
            trim = params.get("trim", "weakest_first")
            result, stats = _instrumented_trim(
                adjacency, ranking, pop,
                j=params["j"], d=params["d"], trim=trim, frame=frame,
            )
            bin_path, _ = cell_paths(archive, rule, params)
            valid = _validate_trim(result, bin_path)
            del result
            gc.collect()
            share = (round(stats["tied_cuts"] / stats["trimmed_nodes"], 5)
                     if stats["trimmed_nodes"] else None)
            row = {
                "nodes_with_binding_cut": stats["trimmed_nodes"],
                "tied_cuts": stats["tied_cuts"],
                "tied_cut_share": share,
                "tie_dominated_CRS_H1": bool(share is not None and share > 0.20),
                "instrumentation_validated_against_artifact": valid,
            }
            if trim == "banded_quota":
                row["CRS_H2_quota_frame_disagreement"] = {
                    "reserved_slots": stats["reserved_slots"],
                    "reserved_sub_decile_under_adopted_frame":
                        stats["reserved_sub_decile_adopted_frame"],
                    "share_sub_decile_under_adopted_frame": round(
                        stats["reserved_sub_decile_adopted_frame"]
                        / stats["reserved_slots"], 5
                    ) if stats["reserved_slots"] else None,
                }
            if not valid:
                row["ERROR"] = ("instrumented trim diverged from the built "
                                "artifact — H1/H2 numbers for this cell are "
                                "not usable")
        else:  # uncapped: no cut, no tie
            row = {"nodes_with_binding_cut": 0, "tied_cuts": 0,
                   "tied_cut_share": None, "tie_dominated_CRS_H1": False,
                   "note": "no cut exists; reference row"}
        row["elapsed_seconds"] = round(time.monotonic() - started, 1)
        results[cell_key(archive, cid)] = row
        print(f"  {cell_key(archive, cid):18} "
              f"binding={row['nodes_with_binding_cut']} "
              f"tied_share={row['tied_cut_share']} "
              f"({row['elapsed_seconds']}s)")

    out_file.write_text(json.dumps(results, indent=2, sort_keys=True),
                        encoding="utf-8")
    print(f"wrote {out_file.name}")


# --------------------------------------------------------------------------
# pair set (prereg §0: fixed seed, drawn once, routable everywhere)
# --------------------------------------------------------------------------


def _load_stores() -> dict[str, GraphStore]:
    stores: dict[str, GraphStore] = {}
    for archive in ARCHIVE_IDS:
        for cid, rule, params, _bound in GRID:
            bin_path, _ = cell_paths(archive, rule, params)
            if not bin_path.exists():
                raise SystemExit(f"cell not built: {bin_path.name} — run --phase build")
            stores[cell_key(archive, cid)] = GraphStore.load(bin_path)
    return stores


def _class_counts(triples) -> dict[str, int]:
    counts: dict[str, int] = {}
    for cls, _a, _b in triples:
        counts[cls] = counts.get(cls, 0) + 1
    return counts


def make_pairs(stores: dict[str, GraphStore], frame: dict) -> list[tuple[str, str, str]]:
    adopted_store = GraphStore.load(ADOPTED)
    drawn = draw_pairs(frame, set(adopted_store.id_by_mbid))
    kept = routable_everywhere(drawn, stores)
    payload = {
        "seed": 20260730,
        "drawn": len(drawn),
        "kept_routable_everywhere": len(kept),
        "per_class_drawn": _class_counts(drawn),
        "per_class_kept": _class_counts(kept),
        "restricted_to_cells": sorted(stores),
        "triples": kept,
    }
    PAIRS_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True),
                          encoding="utf-8")
    print(f"pairs: drawn {len(drawn)}, routable everywhere {len(kept)}")
    for cls, n in sorted(_class_counts(kept).items()):
        readable = "readable" if n >= 8 else "UNREADABLE per CRS-G3"
        print(f"  {cls:22} {n:3}  {readable}")
    return kept


def load_pairs() -> list[tuple[str, str, str]]:
    payload = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))
    return [tuple(t) for t in payload["triples"]]


# --------------------------------------------------------------------------
# --phase dryrun / --phase baseline
# --------------------------------------------------------------------------


def _strip_paths(sample: dict) -> dict:
    return {k: v for k, v in sample.items() if not k.startswith("_")}


def phase_dryrun() -> None:
    """Scorer shakedown on the cheapest cell. NOT the scored record."""
    frame = fame_frame()
    bin_path, man_path = cell_paths("ALG-E", "mutual_knn", {"k": 50})
    store = GraphStore.load(bin_path)
    manifest = json.loads(man_path.read_text(encoding="utf-8"))

    graph = deserialise(bin_path.read_bytes())
    structural = score_cell(
        graph, frame, crawled_mbids("ALG-E"),
        manifest["diagnostics"]["nodes_pre_prune"],
        production_top_degree=top_degree_node_set(graph),
    )
    print("structural: nodes", structural["nodes"], "edges", structural["edges"],
          "max_degree", structural["hub_structure"]["max_degree"],
          "exclusion", structural["component_exclusion"]["exclusion_rate"],
          "lower-half stranded",
          structural["band_stranding"]["lower half"]["stranded_share_of_crawled"])

    triples = [t for t in draw_pairs(frame, set(store.id_by_mbid))
               if t[1] in store.id_by_mbid and t[2] in store.id_by_mbid]
    started = time.monotonic()
    sample = route_sample(store, triples, ApiConfig(), frame,
                          top_degree_node_set(store))
    elapsed = round(time.monotonic() - started, 1)

    overall = sample["overall"]
    print(f"paths: {overall['pairs_attempted']} pairs in {elapsed}s "
          f"({elapsed / max(1, overall['pairs_attempted']):.2f}s/pair), "
          f"no_path={overall['no_path']}, invalid={overall['invalid_walks']}")
    for cls, row in sample["per_class"].items():
        print(f"  {cls:22} n={row['pairs_attempted']:3} "
              f"len_med={row['path_length']['median']} "
              f"hub_own={row['top1pct_degree_frac_own']} "
              f"subdec_share={row['sub_decile_interior_share']} "
              f"C5_hits={row['pairs_with_sub_decile_interior']} "
              f"readable={row['readable_per_CRS_G3']}")
    checks = {
        "class_labels": bool(sample["per_class"]),
        "c5_field_present": all("pairs_with_sub_decile_interior" in r
                                for r in sample["per_class"].values()),
        "readability_flag_present": all("readable_per_CRS_G3" in r
                                        for r in sample["per_class"].values()),
        "weights_recorded": bool(sample["weights"]),
        "no_invalid_walks": overall["invalid_walks"] == 0,
    }
    print("dryrun checks:", checks)
    if not all(checks.values()):
        raise SystemExit("DRYRUN FAILED — fix the scorer before the sweep")


def phase_baseline() -> None:
    """CRS-A2: ALG-E-MK50's C5, per class, before any other cell's C5."""
    frame = fame_frame()
    stores = _load_stores()
    kept = make_pairs(stores, frame)

    key = cell_key("ALG-E", "MK50")
    store = stores[key]
    sample = route_sample(store, kept, ApiConfig(), frame,
                          top_degree_node_set(stores[cell_key("ALG-E", "MK50")]))

    famous = {}
    for cls in ("ff-top1pct", "ff-top01pct"):
        row = sample["per_class"].get(cls)
        famous[cls] = {
            "pairs_attempted": row["pairs_attempted"] if row else 0,
            "pairs_with_sub_decile_interior":
                row["pairs_with_sub_decile_interior"] if row else 0,
            "readable_per_CRS_G3": row["readable_per_CRS_G3"] if row else False,
            "no_path": row["no_path"] if row else 0,
        } if row else {"pairs_attempted": 0, "absent": True}
    payload = {
        "cell": key,
        "protocol": "CRS-A2: per-class baseline scored before any other cell's "
                    "C5 is opened. A class at zero keeps §2's 'any nonzero is "
                    "decisive'; a nonzero class needs a further §8 entry fixing "
                    "its bar blind before any candidate C5 is read.",
        "famous_classes": famous,
        "full_per_class": sample["per_class"],
        "weights": sample["weights"],
    }
    BASELINE_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True),
                             encoding="utf-8")
    print(json.dumps(famous, indent=2, sort_keys=True))
    for cls, row in famous.items():
        n = row.get("pairs_with_sub_decile_interior", 0)
        verdict = ("ZERO — §2 stands as written" if n == 0
                   else "NONZERO — §8 amendment required before any candidate "
                        "C5 is read")
        print(f"{cls}: baseline C5 = {n}/{row.get('pairs_attempted')} → {verdict}")


# --------------------------------------------------------------------------
# CRS-C6 survival split
# --------------------------------------------------------------------------


def _edge_set(store: GraphStore) -> set[tuple[str, str]]:
    import numpy as np
    edges: set[tuple[str, str]] = set()
    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)
    for i in range(len(store.mbids)):
        u = store.mbids[i]
        for kk in range(int(offsets[i]), int(offsets[i + 1])):
            v = store.mbids[int(neighbours[kk])]
            if u < v:
                edges.add((u, v))
    return edges


def c6_survival_split(stores: dict[str, GraphStore], frame: dict) -> dict:
    """Prereg §2 CRS-C6, exactly as fixed: edges of ALG-E-MK50 between artists
    crawled by BOTH archives and present in BOTH MK50 components, split by
    whether the pair is an edge of ALG-B-MK50; compare the groups'
    max-endpoint adopted-frame percentile, medians."""
    e_store = stores[cell_key("ALG-E", "MK50")]
    b_store = stores[cell_key("ALG-B", "MK50")]
    crawled_both = crawled_mbids("ALG-E") & crawled_mbids("ALG-B")
    b_present = set(b_store.id_by_mbid)

    e_edges = _edge_set(e_store)
    b_edges = _edge_set(b_store)

    survivors: list[float] = []
    vanished: list[float] = []
    dropped_no_frame = 0
    for u, v in e_edges:
        if u not in crawled_both or v not in crawled_both:
            continue
        if u not in b_present or v not in b_present:
            continue
        pu, pv = frame.get(u), frame.get(v)
        if pu is None or pv is None:
            dropped_no_frame += 1
            continue
        (survivors if (u, v) in b_edges else vanished).append(max(pu, pv))

    med_s = round(statistics.median(survivors), 5) if survivors else None
    med_v = round(statistics.median(vanished), 5) if vanished else None
    delta_points = (round((med_s - med_v) * 100, 2)
                    if med_s is not None and med_v is not None else None)
    return {
        "definition": "median max-endpoint adopted-frame percentile, "
                      "survivors (edge kept by ALG-B-MK50) vs vanished",
        "population_edges": len(survivors) + len(vanished),
        "survivor_edges": len(survivors),
        "vanished_edges": len(vanished),
        "dropped_endpoint_not_in_adopted_frame": dropped_no_frame,
        "median_max_endpoint_pctl_survivors": med_s,
        "median_max_endpoint_pctl_vanished": med_v,
        "tilt_percentile_points_survivors_minus_vanished": delta_points,
        "material_bar_points": 5.0,
        "direction_precommitted_LBS_4": "survivors tilt famous",
        "_edge_population": {"survivors": survivors, "vanished": vanished},
    }


# --------------------------------------------------------------------------
# CRS-A5: endpoint re-verification + descriptive companion
# --------------------------------------------------------------------------

LB_POPULARITY_URL = "https://api.listenbrainz.org/1/popularity/artist"
RADIOHEAD = "a74b1b7f-71a5-4011-9441-d0b5e4122711"


def a5_reverify() -> dict:
    """The one re-verifying request the amendment authorises."""
    import httpx
    try:
        r = httpx.post(LB_POPULARITY_URL, json={"artist_mbids": [RADIOHEAD]},
                       timeout=30)
        body = r.json() if r.status_code == 200 else None
        ok = (r.status_code == 200 and isinstance(body, list) and body
              and body[0].get("total_user_count") is not None)
        return {"status_code": r.status_code, "confirmed": bool(ok),
                "sample": body[:1] if body else None}
    except Exception as exc:  # noqa: BLE001 — descriptive only, never a veto
        return {"confirmed": False, "error": repr(exc)}


def a5_fetch_counts(mbids: list[str], max_batches: int = 100) -> dict[str, int | None]:
    """Batched total_user_count fetch for the C6 companion. Descriptive only."""
    import httpx
    counts: dict[str, int | None] = {}
    batches = [mbids[i:i + 1000] for i in range(0, len(mbids), 1000)]
    if len(batches) > max_batches:
        raise RuntimeError(f"{len(batches)} batches exceeds cap {max_batches}")
    with httpx.Client(timeout=60) as client:
        for n, batch in enumerate(batches):
            for attempt in range(4):
                r = client.post(LB_POPULARITY_URL, json={"artist_mbids": batch})
                if r.status_code == 429:
                    time.sleep(10.0 * (attempt + 1))
                    continue
                r.raise_for_status()
                for row in r.json():
                    counts[row["artist_mbid"]] = row.get("total_user_count")
                break
            else:
                raise RuntimeError("persistent 429 from popularity endpoint")
            if n + 1 < len(batches):
                time.sleep(1.2)
            if (n + 1) % 10 == 0:
                print(f"  a5 companion: {n + 1}/{len(batches)} batches")
    return counts


def c6_companion(stores: dict[str, GraphStore], frame: dict,
                 split_population: dict) -> dict:
    """C6 re-reported in total_user_count currency. Never fires, never vetoes.

    Caveat carried verbatim from CRS-A5: this table is NOT a fame source; it
    and the Wikipedia proxy under-represent the same artists by the same ~10x,
    so agreement is a shared blind spot, not corroboration.
    """
    e_store = stores[cell_key("ALG-E", "MK50")]
    b_store = stores[cell_key("ALG-B", "MK50")]
    crawled_both = crawled_mbids("ALG-E") & crawled_mbids("ALG-B")
    b_present = set(b_store.id_by_mbid)
    b_edges = _edge_set(b_store)

    needed: set[str] = set()
    rows: list[tuple[str, str, bool]] = []
    for u, v in _edge_set(e_store):
        if (u in crawled_both and v in crawled_both
                and u in b_present and v in b_present
                and frame.get(u) is not None and frame.get(v) is not None):
            rows.append((u, v, (u, v) in b_edges))
            needed.add(u)
            needed.add(v)

    counts = a5_fetch_counts(sorted(needed))
    surv: list[int] = []
    van: list[int] = []
    null_edges = 0
    for u, v, survived in rows:
        cu, cv = counts.get(u), counts.get(v)
        if cu is None or cv is None:
            null_edges += 1
            continue
        (surv if survived else van).append(max(cu, cv))
    return {
        "currency": "total_user_count (ListenBrainz popularity endpoint)",
        "median_max_endpoint_user_count_survivors":
            statistics.median(surv) if surv else None,
        "median_max_endpoint_user_count_vanished":
            statistics.median(van) if van else None,
        "edges_with_null_count": null_edges,
        "artists_fetched": len(counts),
        "caveat": "not a fame source; shares the Wikipedia proxy's ~10x blind "
                  "spot — agreement is a shared blind spot, not corroboration",
    }


# --------------------------------------------------------------------------
# --phase score
# --------------------------------------------------------------------------


def phase_score(skip_a5_companion: bool = False) -> None:
    if not BASELINE_FILE.exists():
        raise SystemExit("CRS-A2: run --phase baseline first")
    frame = fame_frame()
    stores = _load_stores()
    kept = load_pairs()
    pairs_meta = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))

    prod_key = cell_key("ALG-E", "MK50")
    production_top = top_degree_node_set(stores[prod_key])
    crawled = {a: crawled_mbids(a) for a in ARCHIVE_IDS}

    ties: dict[str, dict] = {}
    for archive in ARCHIVE_IDS:
        f = HERE / f"cb_ties-{archive}.json"
        if f.exists():
            ties.update(json.loads(f.read_text(encoding="utf-8")))

    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=HERE)
    cells: dict[str, dict] = {}
    raw_paths: dict[str, list] = {}
    for archive in ARCHIVE_IDS:
        for cid, rule, params, bound in GRID:
            key = cell_key(archive, cid)
            bin_path, man_path = cell_paths(archive, rule, params)
            manifest = json.loads(man_path.read_text(encoding="utf-8"))
            graph = deserialise(bin_path.read_bytes())
            started = time.monotonic()
            structural = score_cell(
                graph, frame, crawled[archive],
                manifest["diagnostics"]["nodes_pre_prune"],
                production_top_degree=production_top,
            )
            sample = route_sample(stores[key], kept, ApiConfig(), frame,
                                  production_top)
            raw_paths[key] = sample["_paths"]
            elapsed = round(time.monotonic() - started, 1)

            max_deg = structural["hub_structure"]["max_degree"]
            g2 = (bool(max_deg <= bound) if bound is not None else None)
            cells[key] = {
                "cell_id": cid,
                "archive": archive,
                "rule": rule,
                "params": params,
                "configured_bound": bound,
                "selectable": manifest["selectable"],
                "manifest": manifest,
                "bound_holds_CRS_G2": g2,
                "structural": structural,
                "paths": _strip_paths(sample),
                "ties_CRS_H1": ties.get(key),
            }
            # Deliberately NOT printing per-class path numbers here: other
            # cells' C5 values stay unopened until CB-6, per CRS-A2.
            print(f"{key:18} scored in {elapsed:6.1f}s  "
                  f"max_deg={max_deg} bound={bound} "
                  f"G2={'n/a' if g2 is None else ('PASS' if g2 else 'FAIL')}")
            del graph
            gc.collect()

    print("computing CRS-C6 survival split …")
    c6 = c6_survival_split(stores, frame)
    edge_population = c6.pop("_edge_population")

    a5 = a5_reverify()
    print(f"CRS-A5 endpoint re-verification: {a5}")
    companion = None
    if a5["confirmed"] and not skip_a5_companion:
        try:
            print("fetching CRS-A5 companion counts …")
            companion = c6_companion(stores, frame, edge_population)
        except Exception as exc:  # noqa: BLE001 — descriptive, never blocks
            companion = {"skipped": repr(exc)}
    elif not a5["confirmed"]:
        companion = {"skipped": "endpoint not confirmed; criterion unaffected "
                                "(descriptive only, per CRS-A5)"}

    out = {
        "harness_commit": head.stdout.strip(),
        "generated_unix": int(time.time()),
        "weights_all_cells": next(iter(cells.values()))["paths"]["weights"],
        "pairs": {k: v for k, v in pairs_meta.items() if k != "triples"},
        "cells": cells,
        "CRS_C6_survival_split": c6,
        "CRS_C6_companion_CRS_A5": companion,
        "CRS_A5_endpoint_reverification": a5,
    }
    SCORES_FILE.write_text(json.dumps(out, indent=2, sort_keys=True),
                           encoding="utf-8")
    RAW_PATHS_FILE.write_text(json.dumps(raw_paths, sort_keys=True),
                              encoding="utf-8")
    g2_fail = [k for k, c in cells.items()
               if c["bound_holds_CRS_G2"] is False]
    print(f"wrote {SCORES_FILE.name} ({len(cells)} cells); "
          f"G2 violations: {g2_fail or 'none'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True,
                        choices=["dryrun", "build", "ties", "baseline", "score"])
    parser.add_argument("--archive", choices=sorted(ARCHIVES),
                        help="ties phase only: which archive to process")
    parser.add_argument("--skip-a5-companion", action="store_true")
    args = parser.parse_args()

    if args.phase == "dryrun":
        phase_dryrun()
    elif args.phase == "build":
        phase_build()
    elif args.phase == "ties":
        if not args.archive:
            raise SystemExit("--phase ties needs --archive")
        phase_ties(args.archive)
    elif args.phase == "baseline":
        phase_baseline()
    else:
        phase_score(skip_a5_companion=args.skip_a5_companion)
