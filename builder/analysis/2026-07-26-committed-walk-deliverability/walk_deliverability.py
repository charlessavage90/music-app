"""Which artists did the router actually deliver as interior cards?

READ-ONLY re-read of two committed experimental runs. **No routing, no rebuild,
no arm, no adoption** — the same class as `ASC-5` in
`findings/2026-07-25-router-ascent-gradient.md`. Nothing here runs the router;
it reads path node-ids that Track 2 and Track 2F already committed.

Tests the falsifier `SYN-4` fixed in
`findings/2026-07-26-low-degree-synthesis.md`, committed before this ran.

Production-like arm (`P`) only, per the task. `arms.py:87` defines `P` as the
"mirror-and-verify target; user-facing baseline".

Three gates, each of which aborts:
  1. the artifact's sha256 is asserted against the adopted value;
  2. every run file's own recorded `artifact_sha256` must match it, so the
     paths and the degrees are about the same graph;
  3. the id-space gate — `node_names[id]` must equal the artifact's own name at
     that index for every referenced id. If the committed ids are not artifact
     node indices, every degree below would be a lookup of an unrelated artist.

And one void condition, which is an instrument check rather than a result: a
degree-1 artist **cannot** be an interior card (`DRV-4`; census §1). If one
appears, the extraction is wrong and the run is void.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-07-26-committed-walk-deliverability/walk_deliverability.py
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

ADOPTED_SHA256 = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent

RUNS = {
    "track2_stage1": ANALYSIS / "2026-07-24-track2-arm-scorer" / "paths.json",
    "track2_stage2": ANALYSIS / "2026-07-24-track2-arm-scorer" / "paths_stage2.json",
    "track2f": ANALYSIS / "2026-07-25-track2f-toll-ladder" / "paths.json",
}

ARM = "P"

# SYN-4's pre-registered read, restated here so the script and the document
# cannot drift. Shares are of DISTINCT interior artists.
SYN4_EXPECT_BELOW = 0.10  # expected: under 10% below 10 connections
SYN4_FIRES_BELOW = 0.25  # falsifier fires at or above 25%
SYN4_FIRES_DEG2 = 0.05  # or at or above 5% with <= 2 connections


def verify_artifact() -> tuple[GraphStore, np.ndarray]:
    path = Path(ApiConfig().graph_path).resolve()
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    got = digest.hexdigest()
    if got != ADOPTED_SHA256:
        raise SystemExit(
            f"GATE 1 FAILED — not the adopted artifact.\n"
            f"  expected {ADOPTED_SHA256}\n  got      {got}"
        )
    print(f"GATE 1 ok — artifact verified: {path.name}\n  sha256 {got}")
    store = GraphStore.load(str(path))
    degree = np.diff(np.asarray(store.offsets, dtype=np.int64))
    print(f"  nodes {len(store.mbids)}, median degree {int(np.median(degree))}")
    return store, degree


def main() -> None:
    store, degree = verify_artifact()
    n_nodes = len(store.mbids)
    names = list(store.names)

    # ---- gates 2 and 3, then extraction -------------------------------------
    per_run: dict[str, dict] = {}
    for label, path in RUNS.items():
        if not path.exists():
            raise SystemExit(f"missing committed run file: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        if data["artifact_sha256"] != ADOPTED_SHA256:
            raise SystemExit(
                f"GATE 2 FAILED — {label} was run on a different artifact.\n"
                f"  {data['artifact_sha256']}"
            )

        node_names = data["node_names"]
        mismatches = [
            (nid, nm, names[int(nid)])
            for nid, nm in node_names.items()
            if int(nid) >= n_nodes or names[int(nid)] != nm
        ]
        if mismatches:
            raise SystemExit(
                f"GATE 3 FAILED — {label}'s ids are not artifact node indices.\n"
                f"  {len(mismatches)} mismatches, e.g. {mismatches[:3]}"
            )

        if ARM not in data["paths"]:
            raise SystemExit(f"{label} has no arm {ARM!r}: {list(data['paths'])}")

        cells = data["paths"][ARM]
        interior_instances: list[int] = []
        endpoints: set[int] = set()
        n_cells = 0
        for _pair, by_depth in cells.items():
            for _depth, walk in by_depth.items():
                if not walk:
                    continue
                n_cells += 1
                endpoints.add(walk[0])
                endpoints.add(walk[-1])
                interior_instances.extend(walk[1:-1])

        per_run[label] = {
            "cells": n_cells,
            "pairs": len(cells),
            "interior_instances": interior_instances,
            "distinct_interior": sorted(set(interior_instances)),
            "endpoints": sorted(endpoints),
        }
        print(
            f"GATE 2,3 ok — {label}: {n_cells} scored walks over {len(cells)} pairs, "
            f"{len(interior_instances)} interior cards, "
            f"{len(set(interior_instances))} distinct"
        )

    # ---- gate 4: the three runs are NOT independent evidence -----------------
    # `P` is the deterministic production baseline, so the same config over the
    # same pairs on the same artifact must reproduce the same walks. It does,
    # byte for byte. That is a REPRODUCIBILITY check, not three samples — so
    # everything below is computed over ONE copy. Counting the three would
    # inflate every instance figure threefold.
    walk_sets = {
        label: {
            (pair, depth): tuple(walk)
            for pair, by_depth in json.loads(path.read_text(encoding="utf-8"))["paths"][ARM].items()
            for depth, walk in by_depth.items()
            if walk
        }
        for label, path in RUNS.items()
    }
    labels = list(walk_sets)
    identical = all(walk_sets[labels[0]] == walk_sets[o] for o in labels[1:])
    if not identical:
        raise SystemExit(
            "GATE 4 FAILED — the P arm differs between runs. P is the "
            "deterministic baseline; differing walks mean the runs are not "
            "comparable and the combination below would be meaningless."
        )
    print(
        f"GATE 4 ok — the {len(labels)} runs' P arms are BYTE-IDENTICAL "
        "(reproducibility, not three samples). Counting one copy."
    )

    canonical = walk_sets[labels[0]]
    all_instances = [n for walk in canonical.values() for n in walk[1:-1]]
    distinct = sorted(set(all_instances))
    deg_of = {i: int(degree[i]) for i in distinct}

    deg1 = [i for i in distinct if deg_of[i] == 1]
    if deg1:
        raise SystemExit(
            "VOID — a degree-1 artist appears as an interior card, which is "
            "structurally impossible (DRV-4). The extraction is wrong.\n"
            f"  {[(i, names[i]) for i in deg1[:5]]}"
        )
    print(f"VOID CHECK ok — no degree-1 interior card among {len(distinct)} distinct")

    # ---- the numbers --------------------------------------------------------
    inst_degs = [int(degree[i]) for i in all_instances]
    dist_degs = [deg_of[i] for i in distinct]

    below10_distinct = [i for i in distinct if deg_of[i] < 10]
    below3_distinct = [i for i in distinct if deg_of[i] <= 2]
    below10_instances = [d for d in inst_degs if d < 10]

    share_below10 = len(below10_distinct) / len(distinct)
    share_below3 = len(below3_distinct) / len(distinct)

    graph_below10 = int((degree < 10).sum())

    def pct(x: int, n: int) -> str:
        return f"{100.0 * x / n:.2f}%"

    print("\n== MEASURED (arm P — ONE baseline, reproduced identically in 3 runs) ==")
    print(f"distinct interior artists      {len(distinct)}")
    print(f"  as a share of the artifact   {pct(len(distinct), n_nodes)} of {n_nodes}")
    print(f"interior card instances        {len(all_instances)}")
    print(f"minimum degree observed        {min(dist_degs)}")
    print(f"maximum degree observed        {max(dist_degs)}")
    print(f"median degree (distinct)       {int(np.median(dist_degs))}")
    print(f"median degree (instances)      {int(np.median(inst_degs))}")
    print(f"distinct below 10 connections  {len(below10_distinct)} ({pct(len(below10_distinct), len(distinct))})")
    print(f"distinct at <= 2 connections   {len(below3_distinct)} ({pct(len(below3_distinct), len(distinct))})")
    print(f"instances below 10             {len(below10_instances)} ({pct(len(below10_instances), len(all_instances))})")
    print(f"\nstructural null — artifact nodes below 10: {graph_below10} ({pct(graph_below10, n_nodes)})")

    print("\ndegree distribution of distinct interior artists")
    bands = [(1, 2), (3, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 10**9)]
    for lo, hi in bands:
        k = sum(1 for d in dist_degs if lo <= d <= hi)
        label = f"{lo}-{hi}" if hi < 10**9 else f"{lo}+"
        print(f"  {label:>7}  {k:>5}  {pct(k, len(distinct)):>7}")

    print("\nthe ten lowest-degree artists ever delivered as an interior card")
    inst_count = Counter(all_instances)
    for i in sorted(distinct, key=lambda x: deg_of[x])[:10]:
        print(f"  deg {deg_of[i]:>3}  {names[i]}  (delivered {inst_count[i]}x)")

    # The pre-registered caveat, made concrete rather than asserted: what the
    # pair set actually asked the router to do.
    ep = sorted({n for walk in canonical.values() for n in (walk[0], walk[-1])})
    ep_degs = [int(degree[i]) for i in ep]
    print(f"\nendpoints ({len(ep)} distinct) — the pre-registered pair set")
    print(f"  median endpoint degree {int(np.median(ep_degs))}, min {min(ep_degs)}, max {max(ep_degs)}")
    print(f"  endpoints below 10 connections: {sum(1 for d in ep_degs if d < 10)}")

    # ---- SYN-4 --------------------------------------------------------------
    fired_below10 = share_below10 >= SYN4_FIRES_BELOW
    fired_deg2 = share_below3 >= SYN4_FIRES_DEG2
    fired = fired_below10 or fired_deg2
    ambiguous = (not fired) and share_below10 >= SYN4_EXPECT_BELOW

    print("\n== SYN-4 ==")
    print(f"  below-10 share {share_below10:.4f}  (expect <{SYN4_EXPECT_BELOW}, fires >={SYN4_FIRES_BELOW})")
    print(f"  <=2 share      {share_below3:.4f}  (fires >={SYN4_FIRES_DEG2})")
    if fired:
        print("  VERDICT: FALSIFIER FIRED — SYN-1..SYN-3 lose most of their motivation.")
    elif ambiguous:
        print("  VERDICT: AMBIGUOUS BAND — weakened, not refuted.")
    else:
        print("  VERDICT: did not fire — but see the report: a low share is the")
        print("           EXPECTED result on a famous-skewed pair set and is weak")
        print("           confirmation of nothing. This test can fail meaningfully;")
        print("           it cannot pass meaningfully.")

    out = {
        "artifact_sha256": ADOPTED_SHA256,
        "arm": ARM,
        "artifact_nodes": n_nodes,
        "per_run": {
            k: {
                "cells": v["cells"],
                "pairs": v["pairs"],
                "interior_instances": len(v["interior_instances"]),
                "distinct_interior": len(v["distinct_interior"]),
            }
            for k, v in per_run.items()
        },
        "runs_byte_identical": identical,
        "scored_walks": len(canonical),
        "pairs": sorted({p for p, _ in canonical}),
        "distinct_interior": len(distinct),
        "interior_instances": len(all_instances),
        "endpoint_degrees": sorted(ep_degs),
        "min_degree": min(dist_degs),
        "max_degree": max(dist_degs),
        "median_degree_distinct": int(np.median(dist_degs)),
        "distinct_below_10": len(below10_distinct),
        "distinct_le_2": len(below3_distinct),
        "instances_below_10": len(below10_instances),
        "artifact_nodes_below_10": graph_below10,
        "degree_histogram_distinct": dict(sorted(Counter(dist_degs).items())),
        "syn4": {
            "share_below_10": share_below10,
            "share_le_2": share_below3,
            "fired": fired,
            "ambiguous": ambiguous,
        },
    }
    dest = HERE / "deliverability.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
