"""`CRE-T5` -- the cleaned-substrate build harness, and the non-tag cells.

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
import sys
import time
from collections import defaultdict
from pathlib import Path

from cre_common import in_dir, use_frozen

use_frozen("track_b")

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
    cap_trimmed_union,
    cap_uncapped,
)

logger = logging.getLogger(__name__)

SCRATCH = Path(__file__).resolve().parents[2] / "builder/scratch"
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--all-nontag", action="store_true")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
