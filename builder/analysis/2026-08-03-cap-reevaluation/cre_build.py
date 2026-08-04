"""The cleaned-substrate build harness and every cell it builds.

`CRE-T5` created this module for the eight non-tag cells; **`CRE-T6` added
`cap_tag_limited`, `build_tag_cell`, `degeneracy_gate` and `s2_shares`** for the
`S2` cells. Both tasks' work lives here because they share one assembly body and
one gate; the header said `CRE-T5` alone until closeout B4 caught it.

**Why a new assembly mirror exists at all.** `cb_build_variants._assemble` is
deliberately frozen **pre-drop** -- its own docstring says *"A post-drop comparison
needs a NEW harness, not an edit to this one"*. Every `CRE-` cell is post-drop
(both drop flags on, held constant), so this module carries the live pipeline body
instead.

`assemble_cleaned` is the body of `artistpath_builder.pipeline.build_from_archive`
**as it stands today**, copied rather than reconstructed, with **exactly one seam**:
the `mutual_knn_cap` invocation is replaced by `cap_step(adjacency, ranking, pop)`,
with `pop` computed upstream of the cap the way `cb_build_variants._assemble` does
(log-scaled score-weighted in-degree -- a VALUE, not a rank, so it is cap-invariant
and identical across every rule cell of one archive).

**The gate is what makes the copy trustworthy, not the care taken copying it.**
`gate()` proves `assemble_cleaned` with the shipped `mutual_knn_cap` at k = 50
serialises **byte-identically** to a direct `build_from_archive` run on the same
archive -- the live pipeline's defaults *are* the cleaned mutual-kNN k=50 cell.
Then k = 49 must differ, so the gate is shown able to fail. **A green failure means
the copy is not the live pipeline: find the drift, do not adjust the gate.**

**Cleanup is held constant, asserted rather than set** (plan Global Constraints):
both drop flags are `BuilderConfig` defaults and a cell with either off is not in
this design.

**Manifests are mirrored into a committed JSON.** `.gitignore` ignores
`builder/scratch/` wholesale, so a sidecar written beside a `.bin` there can never
reach git and the artifact-identity rule would silently lose its record (analyst
m11; the Track B precedent). `cre_builds.json` is the committed copy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

from cre_common import in_dir, use_frozen

use_frozen("track_b", "tag_disc", "rel", "wgt", "wav")

from artistpath_builder.artifact import serialise  # noqa: E402
from artistpath_builder.config import BuilderConfig  # noqa: E402
from artistpath_builder.graph import (  # noqa: E402
    Adjacency,
    Graph,
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats  # noqa: E402
from artistpath_builder.pipeline import (  # noqa: E402
    PRODUCTION_ALGORITHM,
    build_from_archive,
    damped_strength,
    is_special_purpose,
    rescale_scores,
)
from artistpath_builder.sources.listenbrainz import (  # noqa: E402
    ListenBrainzSource,
    harvest_identities,
)
from artistpath_builder.archive import LocalArchive  # noqa: E402
from cb_build_variants import (  # noqa: E402
    ALGORITHMS,
    ARCHIVES,
    ReadOnlyArchive,
    _desc,
    _top_j,
    cap_trimmed_union,
    cap_uncapped,
)
from tas_common import GLOBAL_NEUTRAL_FALLBACK  # noqa: E402

logger = logging.getLogger(__name__)

# parents[2] of the FILE is builder/, not the repo root -- taking it from the
# directory (as cre_common.ROOT does) is what keeps this under the gitignored
# builder/scratch/ tree rather than a stray builder/builder/.
SCRATCH = Path(__file__).resolve().parent.parents[2] / "builder/scratch"
CELLS = SCRATCH / "cre-cells"

# The prereg's supply axis. UC is a STAGED REFERENCE, barred from candidacy.
SUPPLY = {
    "S0": ("MK50", lambda a, r, p: mutual_knn_cap(a, 50, ranking=r)),
    "S0b": ("MK100", lambda a, r, p: mutual_knn_cap(a, 100, ranking=r)),
    "S1": ("TUw-50-50", lambda a, r, p: cap_trimmed_union(
        a, r, p, j=50, d=50, trim="weakest_first")),
    "S3": ("UC", lambda a, r, p: cap_uncapped(a, r, p)),
}
STAGED_BARRED = {"S3"}

# S2 shares S1's shape (TUw-50-50) and differs at exactly one knob: the
# deletion ranking. That is what makes S1 its isolating baseline in §0.2.
TAG_KINDS = ("real", "label_scramble", "vote_scramble")


def _drop_lists(config: BuilderConfig, known: set[str]) -> tuple[set[str], set[str]]:
    from artistpath_builder.featured_credit_drop import (
        load_featured_credit_drop_mbids,
    )
    from artistpath_builder.no_release_drop import load_drop_mbids

    return (load_drop_mbids(config.algorithm) & known,
            load_featured_credit_drop_mbids(config.algorithm) & known)


def assemble_cleaned(config: BuilderConfig, archive, source, cap_step):
    """`pipeline.build_from_archive`'s body with one seam at the cap.

    Returns (Graph, diagnostics). Diagnostics carry `nodes_entering_cap` and the
    §0.3 instrumentation row's affine inputs, `pop_log_low` / `pop_log_high`.
    """
    # Cleanup is held constant across every cell: assert, never set.
    assert config.drop_no_release_tail and config.drop_featured_credit, (
        "CRE holds cleanup constant -- both drop flags on in every cell "
        "(plan Global Constraints). A cell with either off is not in this design."
    )

    if config.algorithm == PRODUCTION_ALGORITHM:
        prefix = f"similar/{source.name}/"
    else:
        prefix = f"similar/{source.name}/{config.algorithm}/"
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix): -len(".json")]
        if "/" in mbid:
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[mbid] = payload

    known = set(payloads)
    identities = harvest_identities(payloads.values())

    if config.filter_special_purpose:
        excluded = {
            mbid
            for mbid, (_name, disambiguation) in identities.items()
            if is_special_purpose(disambiguation)
        }
        known -= excluded
    else:
        excluded = set()

    nameless = {
        mbid
        for mbid, (name, _disambiguation) in identities.items()
        if not name.strip()
    }
    nameless |= known - identities.keys()
    excluded |= nameless
    known -= nameless

    no_release, featured = _drop_lists(config, known)
    excluded |= no_release
    known -= no_release
    excluded |= featured
    known -= featured

    # --- Pass 1 ------------------------------------------------------------
    raw_lists: dict[str, list] = {}
    mass: dict[str, float] = {}
    for mbid in sorted(known):
        neighbours = [
            n
            for n in source.parse(payloads[mbid], exclude_mbid=mbid)
            if n.mbid not in excluded
        ]
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0

    # --- Pass 2 ------------------------------------------------------------
    damping = config.similarity_damping
    scored_adjacency: dict[str, list[tuple[str, float]]] = {}
    for mbid in sorted(known):
        mass_a = mass[mbid]
        scored = [
            (n.mbid, damped_strength(n.score, mass_a, mass[n.mbid], damping))
            for n in raw_lists[mbid]
            if n.mbid in known
        ]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = scored

    flat: list[float] = []
    layout: list[tuple[str, list[str]]] = []
    for mbid, scored in scored_adjacency.items():
        layout.append((mbid, [dst for dst, _ in scored]))
        flat.extend(value for _dst, value in scored)

    rescaled = rescale_scores(
        flat, strategy=config.similarity_rescale, damping=config.similarity_damping
    )

    score_weighted_indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    cursor = 0
    for mbid, dsts in layout:
        edges = {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            cursor += 1
        adjacency[mbid] = edges
        for dst, score in edges.items():
            score_weighted_indegree[dst] += score

    ranking: Adjacency = {
        mbid: {dst: strength for dst, strength in scored}
        for mbid, scored in scored_adjacency.items()
    }

    # Cap-invariant popularity, upstream of every cap, log-scaled to match
    # graph._log_scaled's currency (a VALUE, not a rank) -- cb_build_variants'
    # form, so every rule cell of one archive sees the identical pop.
    logs = {m: math.log1p(max(0.0, score_weighted_indegree[m])) for m in adjacency}
    low, high = (min(logs.values()), max(logs.values())) if logs else (0.0, 0.0)
    span = high - low
    pop = {m: ((v - low) / span if span else 0.0) for m, v in logs.items()}

    nodes_entering_cap = len(adjacency)
    pre_cap_edges = sum(len(e) for e in adjacency.values())

    # ---- THE ONE SEAM -----------------------------------------------------
    adjacency = cap_step(adjacency, ranking, pop)
    # -----------------------------------------------------------------------

    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    stats = [
        ArtistStats(
            mbid=mbid,
            name=identities.get(mbid, ("", ""))[0],
            pop_indegree_scaled=round(score_weighted_indegree[mbid] * 1000),
            listen_count=0,
            disambiguation=identities.get(mbid, ("", ""))[1],
        )
        for mbid in keep
    ]

    from artistpath_builder.deezer_ids import load_deezer_ids

    graph = build_graph(pruned, stats, source.edge_type,
                        deezer_ids=load_deezer_ids())

    kept_logs = [logs[m] for m in keep if m in logs]
    diagnostics = {
        "nodes_entering_cap": nodes_entering_cap,
        "pre_cap_edges": pre_cap_edges,
        "dropped_no_release_tail": len(no_release),
        "dropped_featured_credit": len(featured),
        "nodes_after_prune": len(keep),
        # §0.3 instrumentation row: the affine map's inputs over KEPT nodes.
        "pop_log_low": min(kept_logs) if kept_logs else 0.0,
        "pop_log_high": max(kept_logs) if kept_logs else 0.0,
    }
    return graph, diagnostics


def cap_tag_limited(adjacency, ranking, pop, *, j, d, agree):
    """CRE-S2 (prereg §3.2 + CRE-AM1). ONE knob differs from cap_trimmed_union:
    the ranking that decides which edges an over-budget node loses.

    Deletion key ascending: (strength(u,v) * a_eff(u,v), strength(u,v), _desc(v));
      a_eff = agree.a(u,v) where measured, else the median of u's measured
      values (>= 2, else GLOBAL_NEUTRAL_FALLBACK) -- the committed neutral rule,
      so unlabelled edges rank by LB similarity alone at a neutral level in the
      same pool. Tags re-order the deletion ranking; they never create an edge
      or veto by absence.

    THE MIDDLE KEY ELEMENT IS LOAD-BEARING (analyst M4): agreement is exactly 0
    on ~3.9% of measured edges, and a bare product would order that whole block
    by MBID with similarity playing no part. The strength element keeps
    LB-similarity order inside the zero block and every product tie, and makes
    the degeneracy gate's byte-identity exact by construction.

    Structure, order and determinism are cap_trimmed_union's, unchanged: top-j
    union, symmetrise keep-stronger, then a ceiling of d applied by WHOLE-EDGE
    deletion at over-budget nodes in (-degree, mbid) order.
    """
    keep = _top_j(ranking, adjacency, j, lambda u, v: (-ranking[u][v], v))

    unioned = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)

    def strength(u: str, v: str) -> float:
        return max(ranking.get(u, {}).get(v, float("-inf")),
                   ranking.get(v, {}).get(u, float("-inf")))

    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - d
        if excess <= 0:
            continue
        neighbours = list(result[node])
        measured = {}
        for v in neighbours:
            got = agree.a(node, v)
            if got is not None:
                measured[v] = got
        # The committed neutral rule (frame_pass / tas_select): the median of
        # this node's OWN measured values where there are at least two, else the
        # global fallback. Applied per node, so an unlabelled edge sits at a
        # neutral level inside the same pool it is ranked against.
        neutral = (statistics.median(measured.values()) if len(measured) >= 2
                   else GLOBAL_NEUTRAL_FALLBACK)
        a_eff = {v: measured.get(v, neutral) for v in neighbours}
        doomed = sorted(
            neighbours,
            key=lambda v: (strength(node, v) * a_eff[v],
                           strength(node, v),
                           _desc(v)),
        )[:excess]
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)
    return result


def s2_shares(store, agree) -> dict:
    """Analyst M8: the device is structurally INERT at a node whose neighbour
    pool has fewer than 2 measured agreements -- the per-node neutral median is
    then the global fallback for every neighbour, `a_eff` collapses to one
    constant across the whole pool, and the deletion order reduces to strength.

    So the labelled-node share alone overstates where the device can act. Both
    shares are recorded per cell, and T11 stores them beside any CRE-C5
    attribution field as a licensing constraint the findings note must quote.
    """
    mbids = store.mbids
    labelled = 0
    ge2 = 0
    for u in range(len(mbids)):
        mu = mbids[u]
        if agree.labelled(mu):
            labelled += 1
        measured = 0
        for v, _sim in store.neighbours_of(u):
            if agree.a(mu, mbids[v]) is not None:
                measured += 1
                if measured >= 2:
                    break
        if measured >= 2:
            ge2 += 1
    n = len(mbids)
    return {
        "labelled_node_share": labelled / n,
        "nodes_with_ge2_measured_agreements_share": ge2 / n,
        "device_structurally_inert_node_share": 1.0 - ge2 / n,
    }


def _archive(data_set: str):
    # Every archive open goes through ReadOnlyArchive (GRT-A1, standing): this
    # harness only ever reads, so a put() firing is a bug here, not a finding.
    return ReadOnlyArchive(LocalArchive(ARCHIVES[data_set]))


def _config(data_set: str) -> BuilderConfig:
    return BuilderConfig(algorithm=ALGORITHMS[data_set])


def _source(config: BuilderConfig):
    # The source is config-bound (cli.py:120, cb_build_variants.py:494), so it
    # is constructed from the SAME config the assembly uses -- never a shared
    # default that could carry a different algorithm than the archive sub-tree.
    return ListenBrainzSource(config)


def gate() -> dict:
    """Green twice, red once. cb_build_variants.gate()'s shape, upgraded to the
    live pipeline (drops included)."""
    out: dict = {"greens": {}, "red": {}}
    for data_set in ("ALG-E", "ALG-B"):
        cfg = _config(data_set)
        src = _source(cfg)
        archive = _archive(data_set)
        t0 = time.time()
        mine, diag = assemble_cleaned(
            cfg, archive, src, lambda a, r, p: mutual_knn_cap(a, 50, ranking=r))
        theirs = build_from_archive(cfg, _archive(data_set), src)
        a = hashlib.sha256(serialise(mine)).hexdigest()
        b = hashlib.sha256(serialise(theirs)).hexdigest()
        out["greens"][data_set] = {
            "mirror_sha256": a, "pipeline_sha256": b,
            "identical": a == b, "result": "PASS" if a == b else "FAIL",
            "diagnostics": diag, "seconds": round(time.time() - t0, 1),
        }
        print(f"GREEN {data_set}: {'PASS' if a == b else 'FAIL'}  "
              f"({time.time() - t0:.0f}s)", flush=True)
        if a != b:
            raise SystemExit(
                f"GREEN {data_set} FAILED: the copy is not the live pipeline. "
                f"Find the drift; do NOT adjust the gate."
            )

    cfg = _config("ALG-E")
    off, _ = assemble_cleaned(
        cfg, _archive("ALG-E"), _source(cfg),
        lambda a, r, p: mutual_knn_cap(a, 49, ranking=r))
    c = hashlib.sha256(serialise(off)).hexdigest()
    differs = c != out["greens"]["ALG-E"]["mirror_sha256"]
    out["red"] = {"k": 49, "sha256": c, "differs": differs,
                  "result": "PASS" if differs else "FAIL"}
    print(f"RED k=49: {'PASS' if differs else 'FAIL'}", flush=True)
    if not differs:
        raise SystemExit("RED FAILED: the gate cannot detect a changed cap.")
    return out


def build_cell(data_set: str, supply: str) -> dict:
    label, cap_step = SUPPLY[supply]
    cell = f"{data_set[-1]}-{supply}"          # E-S0, B-S1, ...
    CELLS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cfg = _config(data_set)
    graph, diag = assemble_cleaned(
        cfg, _archive(data_set), _source(cfg), cap_step)
    payload = serialise(graph)
    path = CELLS / f"{cell}.bin"
    path.write_bytes(payload)
    manifest = {
        "cell": cell, "data_set": data_set, "supply": supply,
        "cap_rule": label,
        "staged_reference_barred_from_candidacy": supply in STAGED_BARRED,
        "sha256": hashlib.sha256(payload).hexdigest(),
        # Graph's own accessors (cb_build_variants.py:512-513), not a
        # recount from an attribute the dataclass does not carry.
        "artists": graph.artist_count, "edges": graph.edge_count,
        "path": str(path),
        "drop_flags": {"drop_no_release_tail": True, "drop_featured_credit": True},
        "diagnostics": diag,
        "seconds": round(time.time() - t0, 1),
    }
    (CELLS / f"{cell}.bin.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  {cell:8s} {label:10s} artists={manifest['artists']:6d} "
          f"edges={manifest['edges']:8d} sha={manifest['sha256'][:12]} "
          f"({manifest['seconds']}s)", flush=True)
    return manifest


def build_tag_cell(data_set: str, kind: str) -> dict:
    """S2 = S1's shape with the deletion ranking replaced. Same j, d and trim
    structure, so S1 is its isolating baseline and exactly one column moves."""
    from cre_tags import agreement_table

    cfg = _config(data_set)
    agree = agreement_table(kind, n_artists=None)
    suffix = {"real": "", "label_scramble": "-labelscramble",
              "vote_scramble": "-votescramble"}[kind]
    cell = f"{data_set[-1]}-S2{suffix}"
    CELLS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    graph, diag = assemble_cleaned(
        cfg, _archive(data_set), _source(cfg),
        lambda a, r, p: cap_tag_limited(a, r, p, j=50, d=50, agree=agree))
    payload = serialise(graph)
    (CELLS / f"{cell}.bin").write_bytes(payload)

    # Analyst M8: the device is structurally inert at a node whose whole
    # neighbour pool collapses to one constant, i.e. a node with fewer than 2
    # MEASURED agreements. Recorded per cell as a licensing constraint T11
    # stores beside any CRE-C5 attribution field.
    use_frozen("api_src")
    from artistpath_api.graph_store import GraphStore
    shares = s2_shares(GraphStore.from_bytes(payload), agree)
    manifest = {
        "cell": cell, "data_set": data_set, "supply": "S2",
        "cap_rule": "tag-limited TUw-50-50", "agreement_kind": kind,
        "agreement_seed": 20260803,
        "isolating_baseline": f"{data_set[-1]}-S1",
        "staged_reference_barred_from_candidacy": False,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "artists": graph.artist_count, "edges": graph.edge_count,
        "path": str(CELLS / f"{cell}.bin"),
        "drop_flags": {"drop_no_release_tail": True, "drop_featured_credit": True},
        **shares,
        "diagnostics": diag,
        "seconds": round(time.time() - t0, 1),
    }
    (CELLS / f"{cell}.bin.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  {cell:22s} {kind:15s} artists={manifest['artists']:6d} "
          f"edges={manifest['edges']:8d} "
          f"labelled={manifest['labelled_node_share']:.4f} "
          f"ge2={manifest['nodes_with_ge2_measured_agreements_share']:.4f} "
          f"sha={manifest['sha256'][:12]} ({manifest['seconds']}s)", flush=True)
    return manifest


def degeneracy_gate() -> dict:
    """WAV-0d's pattern on the real build: with an agreement table that is
    undefined everywhere, every a_eff collapses to one constant, so
    cap_tag_limited must reproduce cap_trimmed_union EXACTLY -- byte-identical
    to the committed E-S1 cell. A mismatch means S2 is not one knob away from
    S1 and the §0.2 isolation is broken; stop."""
    from cre_tags import AllNone

    cfg = _config("ALG-E")
    graph, _ = assemble_cleaned(
        cfg, _archive("ALG-E"), _source(cfg),
        lambda a, r, p: cap_tag_limited(a, r, p, j=50, d=50, agree=AllNone()))
    got = hashlib.sha256(serialise(graph)).hexdigest()
    committed = {c["cell"]: c for c in json.loads(
        in_dir("cre_builds.json").read_text(encoding="utf-8"))["cells"]}
    want = committed["E-S1"]["sha256"]
    ok = got == want
    print(f"DEGENERACY GATE: {'PASS' if ok else 'FAIL'}  "
          f"got={got[:12]} want(E-S1)={want[:12]}", flush=True)
    if not ok:
        raise SystemExit(
            "DEGENERACY GATE FAILED: cap_tag_limited with an all-None table is "
            "NOT byte-identical to E-S1. S2 is not one knob away from S1 -- the "
            "§0.2 isolation is broken. Stop."
        )
    return {"gate": "S2 degeneracy", "sha256": got, "expected_E-S1": want,
            "result": "PASS"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--all-nontag", action="store_true")
    ap.add_argument("--degeneracy-gate", action="store_true")
    ap.add_argument("--tag-cells", action="store_true")
    ap.add_argument("--s2-shares", action="store_true")
    args = ap.parse_args()

    if args.gate:
        doc = gate()
        in_dir("cre_build_gate.json").write_text(
            json.dumps(doc, indent=2), encoding="utf-8")
        print("wrote cre_build_gate.json")
    if args.all_nontag:
        manifests = []
        for data_set in ("ALG-E", "ALG-B"):
            for supply in ("S0", "S0b", "S1", "S3"):
                manifests.append(build_cell(data_set, supply))
        in_dir("cre_builds.json").write_text(
            json.dumps({"cells": manifests}, indent=2), encoding="utf-8")
        print(f"wrote cre_builds.json ({len(manifests)} cells)")
    if args.degeneracy_gate:
        doc = degeneracy_gate()
        in_dir("cre_s2_degeneracy_gate.json").write_text(
            json.dumps(doc, indent=2), encoding="utf-8")
        print("wrote cre_s2_degeneracy_gate.json")
    if args.s2_shares:
        from cre_tags import agreement_table
        use_frozen("api_src")
        from artistpath_api.graph_store import GraphStore

        cells = json.loads(
            in_dir("cre_builds.json").read_text(encoding="utf-8"))["cells"]
        for c in cells:
            if c["supply"] != "S2" or "nodes_with_ge2_measured_agreements_share" in c:
                continue
            agree = agreement_table(c["agreement_kind"], n_artists=None)
            store = GraphStore.from_bytes(Path(c["path"]).read_bytes())
            c.update(s2_shares(store, agree))
            Path(c["path"] + ".json").write_text(
                json.dumps(c, indent=2), encoding="utf-8")
            print(f"  {c['cell']:22s} labelled="
                  f"{c['labelled_node_share']:.4f} ge2="
                  f"{c['nodes_with_ge2_measured_agreements_share']:.4f} "
                  f"inert={c['device_structurally_inert_node_share']:.4f}",
                  flush=True)
        in_dir("cre_builds.json").write_text(
            json.dumps({"cells": cells}, indent=2), encoding="utf-8")
        print("updated cre_builds.json with the M8 shares")
    if args.tag_cells:
        # CRE-D1 fired not_supported, so the (D1-branch) cells -- B-S2 and its
        # companions -- DO NOT EXIST. Read from the committed JSON rather than
        # remembered, so the branch cannot drift.
        d1 = json.loads(in_dir("cre_d1.json").read_text(encoding="utf-8"))
        data_sets = ("ALG-E", "ALG-B") if d1["branch"] == "supported" else ("ALG-E",)
        print(f"CRE-D1 branch = {d1['branch']}  ->  tag cells on {data_sets}")
        existing = json.loads(
            in_dir("cre_builds.json").read_text(encoding="utf-8"))["cells"]
        existing = [c for c in existing if c["supply"] != "S2"]
        for data_set in data_sets:
            for kind in TAG_KINDS:
                existing.append(build_tag_cell(data_set, kind))
        in_dir("cre_builds.json").write_text(
            json.dumps({"cells": existing}, indent=2), encoding="utf-8")
        print(f"wrote cre_builds.json ({len(existing)} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
