"""DD-D6 — is DD-C1 reachable at ANY device strength? Runs before any arm.

DD-P1 certified headroom in **percentile**; DD-C1 and DD-C2 score in **fame**
(log10 pageviews). Those are different currencies (§2.12), so "an all-sub-decile route
exists" does not entail "a route 1.0 log10 F below production's". This closes that gap
before six arms are run against a threshold that may be unreachable.

**The bound is implementation-independent, which is the point.** The device adds
`w·k·pctl(v)` per interior. As `w -> infinity` the surviving path is the one minimising
`sum of pctl over interiors`, with the base cost breaking ties. That limit path is the
**ceiling on what any `w` can deliver** — no arm can be more obscure than it. So this is
computed directly as a node-weighted Dijkstra rather than through the device, and a bug
in DD-P4's toll cannot flatter or spoil it.

If the ceiling's fame gap against production is well short of DD-C1's -1.0 log10, then
DD-C1 is unreachable at any strength and the dose ladder is answering a question whose
answer is already fixed.

Two modes, because the middle step is network-bound and cached:

    1. --emit   builds `gap_paths.json` in the shape `fame.py` consumes
    2. then:    uv run python ../2026-07-24-track2-arm-scorer/fame.py \
                    --paths <dir>/gap_paths.json --out <dir>/gap_fame.json
    3. --score  joins the two by mbid and reports the gap

The walk is the committed `run_arms.walk`; fame resolution is the committed `fame.py`.
Neither is reimplemented here (prereg §0, amendment A11).

Run from `api/`.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

DEPTHS = (5, 10, 15, 20)      # DD-C2 reads d5; DD-C1 reads d10/15/20
BIG = 1.0e6                   # the w -> infinity limit; base cost then only breaks ties


def min_pctl_path(store, pctl, src: int, dst: int, hard: set[int],
                  cfg, ctx) -> list[int] | None:
    """The w -> infinity limit path: minimise sum(pctl) over interiors, ties on base cost.

    Node potential folded onto the in-edge, target exempt, exactly as the device
    specifies. Guard G is enforced by masking the direct edge, so the result always has
    at least one interior and is comparable with P's guard-on paths.
    """
    # Deliberately NOT routed through `mirror._dijkstra`: at the limit this is a plain
    # Dijkstra on (BIG*pctl(v) + base), and computing it here is what makes the ceiling
    # independent of DD-P4's toll implementation. `base` is bounded by ~20 while
    # BIG*pctl separates by >= 1e6 * 1e-5, so the ordering is the pctl-sum ordering
    # with base as the tie-break.
    offsets, neighbours, scores = store.offsets, store.neighbours, store.scores
    dist = {src: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, float("inf")):
            continue
        for k in range(offsets[u], offsets[u + 1]):
            v = int(neighbours[k])
            if v in hard or (u == src and v == dst):
                continue
            base = cfg.w_sim * (1.0 - float(scores[k])) + cfg.w_hop
            step = base if v == dst else base + BIG * float(pctl[v])
            nd = d + step
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dst not in prev:
        return None
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return path[::-1]


def emit() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # DD-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    doc = json.loads((HERE / "pairs_v2.json").read_text(encoding="utf-8"))
    assert doc["artifact_sha256"] == digest
    entries = [dict(e, split="analysis") for e in doc["analysis_pairs"]]
    entries += [dict(e, split="held_out") for e in doc["held_out_pairs"]]

    per_arm: dict[str, dict[str, dict[str, list | None]]] = {"P": {}, "LIMIT": {}}
    for e in entries:
        src, dst = by_name[e["src"]], by_name[e["dst"]]
        stats = {"examined": 0, "floor_active": 0}
        paths = walk(store, src, dst, cfg, ctx, pop, find_path_mirror,
                     Exclusion, KNOWN, stats)
        victims: list[int] = []
        for p in paths:
            if p is None or not p[1:-1]:
                break
            victims.append(min(p[1:-1], key=lambda v: (-pop[v], v)))

        key = e["pair"]
        per_arm["P"][key] = {}
        per_arm["LIMIT"][key] = {}
        for d in DEPTHS:
            p = paths[d]
            hard = set(victims[:d]) - {src, dst}
            lim = min_pctl_path(store, pctl, src, dst, hard, cfg, ctx)
            per_arm["P"][key][str(d)] = p
            per_arm["LIMIT"][key][str(d)] = lim
            if p and lim:
                print(f"  {e['pair'][:44]:<46} d{d:<2} "
                      f"P {len(p) - 1:>2}h meanPctl {pctl[p[1:-1]].mean():.4f}   "
                      f"LIMIT {len(lim) - 1:>2}h meanPctl {pctl[lim[1:-1]].mean():.4f}")

    seen = {n for arm in per_arm.values() for byd in arm.values()
            for path in byd.values() if path for n in path}
    out = {
        "artifact_sha256": digest,
        "note": "DD-D6 ceiling probe; LIMIT is the w->infinity min-sum-pctl path",
        "snapshots": list(DEPTHS),
        "arms": ["P", "LIMIT"],
        "pairs": [e["pair"] for e in entries],
        "splits": {e["pair"]: e["split"] for e in entries},
        "paths": per_arm,
        "node_names": {str(n): store.names[n] for n in sorted(seen)},
        "node_mbids": {str(n): store.mbids[n] for n in sorted(seen)},
    }
    (HERE / "gap_paths.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    print(f"\nwrote {HERE / 'gap_paths.json'}  ({len(seen):,} distinct nodes)")

    cache_path = ROOT / "builder/analysis/2026-07-24-track2-arm-scorer/fame_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    names = {store.names[n] for n in seen}
    print(f"distinct names {len(names):,}; uncached {len({n for n in names if n not in cache}):,} "
          f"(~1 s each to resolve)")
    return 0


def score() -> int:
    fame_doc = json.loads((HERE / "gap_fame.json").read_text(encoding="utf-8"))
    paths_doc = json.loads((HERE / "gap_paths.json").read_text(encoding="utf-8"))
    F = fame_doc["fame"]
    mbids = paths_doc["node_mbids"]
    names = paths_doc["node_names"]

    # DD-G4's outstanding half: no scored interior may be blank-named.
    blank = sorted({mbids[str(n)] for arm in paths_doc["paths"].values()
                    for byd in arm.values() for path in byd.values() if path
                    for n in path[1:-1] if not names[str(n)].strip()})
    assert not blank, f"DD-G4: blank-named interior(s) in a scored path: {blank}"
    print(f"DD-G4: no blank-named interior in any scored path. OK\n")

    def interior_F(path) -> list[float]:
        return [F[mbids[str(n)]] for n in path[1:-1]]

    rows = []
    for pair in paths_doc["pairs"]:
        for d in paths_doc["snapshots"]:
            p = paths_doc["paths"]["P"][pair][str(d)]
            lim = paths_doc["paths"]["LIMIT"][pair][str(d)]
            if not p or not lim:
                continue
            fp, fl = interior_F(p), interior_F(lim)
            rows.append({"pair": pair, "split": paths_doc["splits"][pair], "depth": d,
                         "p_mean_F": statistics.mean(fp),
                         "limit_mean_F": statistics.mean(fl),
                         "gap": statistics.mean(fl) - statistics.mean(fp),
                         "p_interiors": len(fp), "limit_interiors": len(fl)})

    print(f"{'pair':<40}{'d':>3}{'P meanF':>9}{'ceil meanF':>12}{'gap':>8}"
          f"{'P n':>5}{'ceil n':>7}")
    for r in rows:
        print(f"{r['pair'][:39]:<40}{r['depth']:>3}{r['p_mean_F']:9.3f}"
              f"{r['limit_mean_F']:12.3f}{r['gap']:8.3f}"
              f"{r['p_interiors']:5d}{r['limit_interiors']:7d}")

    for label, sel in (("ALL", rows),
                       ("analysis", [r for r in rows if r["split"] == "analysis"]),
                       ("C1 window (d>=10), analysis",
                        [r for r in rows if r["split"] == "analysis" and r["depth"] >= 10])):
        if not sel:
            continue
        gaps = [r["gap"] for r in sel]
        dlen = [r["limit_interiors"] - r["p_interiors"] for r in sel]
        print(f"\n{label}: n={len(sel)}  mean gap {statistics.mean(gaps):+.3f}  "
              f"median {statistics.median(gaps):+.3f}  "
              f"min {min(gaps):+.3f}  max {max(gaps):+.3f}")
        print(f"    cells reaching DD-C1's -1.0: "
              f"{sum(1 for g in gaps if g <= -1.0)}/{len(gaps)}")
        print(f"    interior-count change (ceiling - P): median {statistics.median(dlen):+.1f}"
              f"  (DD-C6 flags a drop > 1.0)")

    (HERE / "gap_result.json").write_text(
        json.dumps({"artifact_sha256": paths_doc["artifact_sha256"], "cells": rows},
                   indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {HERE / 'gap_result.json'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    raise SystemExit(emit() if a.emit else score() if a.score else 1)
