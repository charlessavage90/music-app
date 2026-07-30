"""CB-3: path-level metrics -- what the real router does on a candidate graph.

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md

Structural metrics (CB-2) say what a cap rule does to the GRAPH. They cannot
say what it does to a JOURNEY, and the journey is the product. This module
loads each cell through the API's own GraphStore and routes with the API's own
find_path -- no server, no network, no reimplementation of the cost function.

WHY THIS EXISTS AT ALL -- the unpriced half of MKS-5b
    Removing unbounded hubs is what capfix won its blind listen for, and no
    probe in this project has ever measured hub TRANSIT. GRT-P3 measured the
    benefit side of a looser cap (stranding falls) and explicitly priced no
    hub cost. This is that column. It is a proxy and not a substitute: there
    is NO validated offline proxy for listening coherence here, which CB-4
    must state plainly rather than let a hub-transit number stand in for.

⚠ w_degree_hub IS A LIVE INTERACTING TERM HERE, NOT A CONSTANT
    ApiConfig.w_degree_hub defaults to 0.0, and its comment records why: the
    2026-07-21 baseline found hub traversal topological, and the top-1%-by-
    degree set on the CURRENT CAPPED graph is largely insular micro-genre
    artists, so the term was tuned to no-op against that structure. A looser
    cap moves famous artists into the top-degree set. So the default is inert
    "for a reason the intervention removes" -- exactly the dormant-term shape
    CLAUDE.md's factor-table rule exists to catch. Every read here therefore
    NAMES the weight set it ran under, and CB-4 decides whether a second set
    runs and pre-commits its read.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_paths.py --gate
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402

from cb_metrics import ADOPTED, BANDS, fame_frame, top_degree_node_set  # noqa: E402

SCRATCH = ROOT / "builder" / "scratch"
SEED = 20260730
PAIRS_PER_BAND = 12


def draw_pairs(frame: dict[str, float], present: set[str],
               seed: int = SEED,
               per_band: int = PAIRS_PER_BAND) -> list[tuple[str, str, str]]:
    """Stratified pair draw over the adopted fame frame, fixed seed.

    Returns (pair_class, a, b) triples — THE CLASS LABEL IS LOAD-BEARING.
    CRS-A1 (2026-07-30): the first version returned bare pairs via
    sorted(set(pairs)), which discarded the class each pair was drawn for, so
    CRS-C5 (a count over famous-famous pairs) and CRS-G3 (per-band
    readability) were not computable from the output. Caught by the
    consultant's harness read against the committed prereg, BEFORE any cell
    was scored.

    Classes:
      "<band> x lower"   one endpoint from <band>, one from the lower half
                         (within-lower for the lower band itself)
      "ff-top1pct"       both endpoints from the 0.99-1.0 pool (DD-F1's broad
                         territory)
      "ff-top01pct"      both endpoints from the top 0.1% band alone — kept
                         separate because CS-P0b's zero-downward series is
                         band-dependent (8.2% -> 87.5% inward), so the two
                         famous pools have different expected baselines
                         (CRS-A2).

    Deterministic: same seed, same frame, same triples. Dedup is per class,
    order preserved by construction.
    """
    rng = random.Random(seed)
    by_band: dict[str, list[str]] = {name: [] for name, _lo, _hi in BANDS}
    for mbid, pctl in sorted(frame.items()):
        if mbid not in present:
            continue
        for name, lo, hi in BANDS:
            if lo <= pctl < hi:
                by_band[name].append(mbid)
                break

    triples: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(cls: str, a: str, b: str) -> None:
        row = (cls, a, b)
        if a != b and row not in seen:
            seen.add(row)
            triples.append(row)

    lower = by_band["lower half"]
    for name, _lo, _hi in BANDS:
        pool = by_band[name]
        if len(pool) < 2 or not lower:
            continue
        for _ in range(per_band):
            a = rng.choice(pool)
            b = rng.choice(lower if name != "lower half" else pool)
            add(f"{name} x lower", a, b)

    top_broad = by_band["top 0.1%"] + by_band["top 1%"]
    for _ in range(per_band):
        add("ff-top1pct", rng.choice(top_broad), rng.choice(top_broad))

    top_narrow = by_band["top 0.1%"]
    if len(top_narrow) >= 2:
        for _ in range(per_band):
            add("ff-top01pct", rng.choice(top_narrow), rng.choice(top_narrow))

    return triples


def routable_everywhere(triples, stores: dict[str, GraphStore]) -> list[tuple[str, str, str]]:
    """Keep only pairs whose BOTH endpoints exist in EVERY compared cell.

    Load-bearing: the two archives' crawl frontiers diverge by 31% (GRT-P4),
    so an unfiltered sample would compare routing against coverage and read
    a missing artist as a routing failure.
    """
    return [
        (cls, a, b) for cls, a, b in triples
        if all(a in s.id_by_mbid and b in s.id_by_mbid for s in stores.values())
    ]


def _valid_walk(store: GraphStore, path: list[int]) -> bool:
    """Every consecutive pair is a real edge in this graph's CSR."""
    for u, v in zip(path, path[1:]):
        lo, hi = int(store.offsets[u]), int(store.offsets[u + 1])
        if v not in store.neighbours[lo:hi].tolist():
            return False
    return True


def route_sample(store: GraphStore, triples: list[tuple[str, str, str]],
                 cfg: ApiConfig, frame: dict[str, float],
                 production_top_degree: set[str] | None = None) -> dict:
    """Route every pair and summarise PER PAIR CLASS, then overall.

    CRS-A1 (2026-07-30): the first version pooled every pair into single
    means, which could not express CRS-C5 (a COUNT of famous-famous pairs
    whose first path holds >= 1 sub-decile interior) or CRS-G3 (per-band
    readability). Per-class output is the fix; the overall block is kept for
    the instrument gate and orientation only — no pre-registered read
    consumes it.

    Returns paths too, for determinism checks.
    """
    own_top = top_degree_node_set(store)

    per_class: dict[str, dict] = {}
    routed: list[list[str]] = []

    def blank() -> dict:
        return {"lengths": [], "no_path": 0, "invalid": 0, "hub_own": [],
                "hub_prod": [], "sub_decile": [], "c5_hits": 0, "attempted": 0}

    for cls, a, b in triples:
        bucket = per_class.setdefault(cls, blank())
        bucket["attempted"] += 1
        src, tgt = store.id_by_mbid[a], store.id_by_mbid[b]
        path = find_path(store, src, tgt, [], cfg)
        if path is None:
            bucket["no_path"] += 1
            routed.append([])
            continue
        if not _valid_walk(store, path):
            bucket["invalid"] += 1
        routed.append([store.mbids[i] for i in path])
        bucket["lengths"].append(len(path))
        interior = [store.mbids[i] for i in path[1:-1]]
        if not interior:
            continue
        bucket["hub_own"].append(
            sum(1 for m in interior if m in own_top) / len(interior)
        )
        if production_top_degree is not None:
            bucket["hub_prod"].append(
                sum(1 for m in interior if m in production_top_degree)
                / len(interior)
            )
        sd = sum(1 for m in interior if frame.get(m, 1.0) < 0.90)
        bucket["sub_decile"].append(sd / len(interior))
        if sd >= 1:
            bucket["c5_hits"] += 1

    def mean(xs):
        return round(float(statistics.mean(xs)), 5) if xs else None

    def summarise(b: dict) -> dict:
        return {
            "pairs_attempted": b["attempted"],
            # CRS-G3: a class with < 8 attempted pairs is unreadable for path
            # criteria; the flag travels with the data rather than being
            # recomputed by every consumer.
            "readable_per_CRS_G3": b["attempted"] >= 8,
            "no_path": b["no_path"],
            "invalid_walks": b["invalid"],
            "path_length": {
                "median": float(statistics.median(b["lengths"])) if b["lengths"] else None,
                "mean": mean(b["lengths"]),
                "max": max(b["lengths"]) if b["lengths"] else None,
            },
            # Fraction of interior nodes in a top-1%-by-DEGREE set -- the
            # established PathMetrics.top1pct_degree_frac quantity, reported
            # against two different sets and named for each.
            "top1pct_degree_frac_own": mean(b["hub_own"]),
            "top1pct_degree_frac_production": mean(b["hub_prod"]),
            "sub_decile_interior_share": mean(b["sub_decile"]),
            # CRS-C5's quantity: pairs whose first path holds >= 1 sub-decile
            # interior. A count with its denominator, never a rate alone.
            "pairs_with_sub_decile_interior": b["c5_hits"],
        }

    overall = blank()
    for b in per_class.values():
        for key in ("lengths", "hub_own", "hub_prod", "sub_decile"):
            overall[key].extend(b[key])
        for key in ("no_path", "invalid", "c5_hits", "attempted"):
            overall[key] += b[key]

    return {
        # The weight set is IN THE OUTPUT, never assumed (see module docstring).
        "weights": {k: v for k, v in asdict(cfg).items()
                    if k.startswith("w_") or k.startswith("floor_")
                    or k.startswith("avoid_")},
        "per_class": {cls: summarise(b) for cls, b in sorted(per_class.items())},
        "overall": summarise(overall),
        "_paths": routed,
    }


def gate() -> dict:
    """CB-3's instrument gate: determinism + walk validity (green), and a
    weight perturbation that must MOVE the paths (red).

    A router harness that returns the same answer under any weights is wired
    to nothing; the red half is what proves the cost function is reached.
    """
    frame = fame_frame()
    store = GraphStore.load(ADOPTED)
    present = set(store.id_by_mbid)
    triples = draw_pairs(frame, present)[:20]
    prod_top = top_degree_node_set(store)

    first = route_sample(store, triples, ApiConfig(), frame, prod_top)
    second = route_sample(store, triples, ApiConfig(), frame, prod_top)
    deterministic = first["_paths"] == second["_paths"]
    overall = first["overall"]
    valid = overall["invalid_walks"] == 0
    classes_labelled = all(len(t) == 3 for t in triples) and bool(first["per_class"])

    # Red half: w_sim = 0 removes the similarity reward entirely, so the router
    # optimises a different function and must reach different artists.
    perturbed = route_sample(store, triples, ApiConfig(w_sim=0.0), frame, prod_top)
    moved = sum(1 for a, b in zip(first["_paths"], perturbed["_paths"]) if a != b)

    passed = deterministic and valid and moved > 0 and classes_labelled
    print(f"GREEN determinism: {'PASS' if deterministic else 'FAIL'} "
          f"({len(triples)} pairs, {overall['no_path']} unroutable)")
    print(f"GREEN walk validity: {'PASS' if valid else 'FAIL'} "
          f"({overall['invalid_walks']} invalid)")
    print(f"GREEN class labels: {'PASS' if classes_labelled else 'FAIL'} "
          f"({len(first['per_class'])} classes in output)")
    print(f"RED   w_sim=0 moves paths: {'PASS' if moved else 'FAIL'} "
          f"({moved}/{len(triples)} changed)")
    print(f"      median length {overall['path_length']['median']}, "
          f"hub-transit(own) {overall['top1pct_degree_frac_own']}, "
          f"sub-decile interiors {overall['sub_decile_interior_share']}")

    results = {
        "deterministic": deterministic,
        "walks_valid": valid,
        "class_labels_present": classes_labelled,
        "paths_moved_under_perturbation": moved,
        "gate_passed": passed,
        "production_weights_summary": {
            k: v for k, v in first.items() if not k.startswith("_")
        },
    }
    (HERE / "cb_paths_gate.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    if not args.gate:
        raise SystemExit("cb_paths is a library; --gate runs its instrument check")
    out = gate()
    raise SystemExit(0 if out["gate_passed"] else 1)
