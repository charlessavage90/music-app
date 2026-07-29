"""TB-P1 probe 3 — the §0 dormant-term check, TB-P2 sizing, and criterion arithmetic.

Read-only. Asserts the artifact sha256 (TB-G3 / DD-G3 discipline).

  (1) THE VICTIM RULE vs THE SUB-DECILE SUBGRAPH. The walker's victim is the most
      popular interior. On a production walk are those victims top-decile? If they are,
      P's exclusion sets never touch the sub-decile subgraph, while an arm routing
      sub-decile would have its victims drawn FROM that subgraph -- a term inert in the
      baseline for a reason the intervention removes.
  (2) DD-D6's committed LIMIT vs TB-P3's ceiling in pctl currency, to size how much
      weaker the base-cost tie-break is than the min-sum-pctl one.
  (3) TB-P2 sizing: how many of the ceiling's interiors are already in a committed
      mbid-keyed fame table.
  (4) Criterion arithmetic: TB-C1's "24 cells", TB-C4's interior-hop availability.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_dormant.py
"""

from __future__ import annotations

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
T3 = ROOT / "builder" / "analysis" / "2026-07-28-track3-depth-descent"

KNEE = 0.90
W_SIM, W_JUMP, W_HOP = 3.0, 1.0, 0.02
C1_WINDOW = (10, 15, 20)


def dijkstra(store, pop, src, dst, allowed, hard):
    offsets, neighbours, scores = store.offsets, store.neighbours, store.scores
    dist = {src: 0.0}
    prev: dict[int, int] = {}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, float("inf")):
            continue
        pu = float(pop[u])
        for k in range(offsets[u], offsets[u + 1]):
            v = int(neighbours[k])
            if v in hard or (u == src and v == dst):
                continue
            if allowed is not None and not allowed[v]:
                continue
            nd = d + (W_SIM * (1.0 - float(scores[k]))
                      + W_JUMP * abs(pu - float(pop[v])) + W_HOP)
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


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pctl, pop = ctx.pctl, np.asarray(store.pop_raw, dtype=np.float64)
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prv = by_name.get(nm)
        if prv is None or pop[i] > pop[prv]:
            by_name[nm] = i

    pd = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    entries = [dict(e, split="analysis") for e in pd["analysis_pairs"]]
    entries += [dict(e, split="held_out") for e in pd["held_out_pairs"]]
    below = pctl < KNEE
    dropped = set(json.loads((T3 / "t3_paths.json").read_text(encoding="utf-8"))
                  ["dropped_cells_d7"])

    # ---- (1) victims -----------------------------------------------------------
    print("== (1) are production's victims top-decile? (all 12 scored pairs, k=0..19) ==")
    all_vic, sub_vic = 0, 0
    ceilings: dict[tuple[str, int], list[int]] = {}
    for e in entries:
        src, dst = by_name[e["src"]], by_name[e["dst"]]
        stats = {"examined": 0, "floor_active": 0, "guard_fired": 0}
        paths = walk(store, src, dst, cfg, ctx, pop, find_path_mirror,
                     Exclusion, KNOWN, stats)
        victims: list[int] = []
        for p in paths:
            if p is None or not p[1:-1]:
                break
            victims.append(min(p[1:-1], key=lambda v: (-pop[v], v)))
        n_sub = sum(1 for v in victims if float(pctl[v]) < KNEE)
        all_vic += len(victims)
        sub_vic += n_sub
        for d in C1_WINDOW:
            if paths[d] is None or f"{e['pair']}@d{d}" in dropped:
                continue
            allowed = below.copy()
            allowed[src] = allowed[dst] = True
            hard = set(victims[:d]) - {src, dst}
            c = dijkstra(store, pop, src, dst, allowed, hard)
            if c:
                ceilings[(e["pair"], d)] = c
        print(f"   {e['pair'][:47]:<49} victims {len(victims):>2}  "
              f"sub-decile victims {n_sub}")
    print(f"   TOTAL: {sub_vic}/{all_vic} of production's victims are sub-decile "
          f"({100*sub_vic/all_vic:.1f} %)")
    print("   => P's exclusion sets remove nodes the sub-decile subgraph "
          f"{'DOES NOT' if sub_vic == 0 else 'partly'} contain\n")

    # how fast would an all-sub-decile arm eat its own supply?
    print("   Counterfactual sizing: if an arm routes entirely sub-decile, every victim "
          "comes\n   out of the sub-decile subgraph. Ceiling interiors available per "
          "cell (analysis):")
    sizes = [len(c) - 2 for (p, d), c in ceilings.items()]
    print(f"     ceiling interior counts: min {min(sizes)}  median "
          f"{statistics.median(sizes)}  max {max(sizes)}  "
          f"(20 presses remove up to 20 nodes)")

    # ---- (2) LIMIT vs ceiling in pctl -------------------------------------------
    print("\n== (2) DD-D6's LIMIT (min sum-pctl) vs TB-P3's ceiling (min base cost) ==")
    gp = json.loads((T3 / "gap_paths.json").read_text(encoding="utf-8"))
    rows = []
    for (pair, d), c in ceilings.items():
        lim = gp["paths"]["LIMIT"].get(pair, {}).get(str(d))
        if not lim:
            continue
        rows.append((pair, d,
                     statistics.median([float(pctl[v]) for v in lim[1:-1]]),
                     statistics.median([float(pctl[v]) for v in c[1:-1]]),
                     len(lim) - 2, len(c) - 2))
    an_rows = [r for r in rows if r[0] in {e["pair"] for e in entries
                                           if e["split"] == "analysis"}]
    print(f"   analysis C1-window cells compared: {len(an_rows)}")
    print(f"   mean cell-median pctl   LIMIT {statistics.mean(r[2] for r in an_rows):.4f}"
          f"   TB ceiling {statistics.mean(r[3] for r in an_rows):.4f}")
    print(f"   mean interior count     LIMIT {statistics.mean(r[4] for r in an_rows):.2f}"
          f"   TB ceiling {statistics.mean(r[5] for r in an_rows):.2f}")
    print(f"   cells where TB ceiling is LESS obscure (higher median pctl): "
          f"{sum(1 for r in an_rows if r[3] > r[2])}/{len(an_rows)}")

    # ---- (3) TB-P2 sizing -------------------------------------------------------
    print("\n== (3) TB-P2 sizing: fame coverage of the ceiling's interiors ==")
    t3f = json.loads((T3 / "t3_fame.json").read_text(encoding="utf-8"))["fame"]
    gapf = json.loads((T3 / "gap_fame.json").read_text(encoding="utf-8"))["fame"]
    known = set(t3f) | set(gapf)
    ints = {v for c in ceilings.values() for v in c[1:-1]}
    new = {v for v in ints if store.mbids[v] not in known}
    print(f"   distinct ceiling interiors (all 12 pairs, C1 window): {len(ints)}")
    print(f"   already in a committed fame table: {len(ints) - len(new)}")
    print(f"   NEW mbids TB-P2 must fetch: {len(new)}")
    blank = [v for v in ints if not store.names[v].strip()]
    print(f"   blank-named ceiling interiors (TB-G4): {len(blank)}")

    # ---- (4) criterion arithmetic ----------------------------------------------
    print("\n== (4) criterion arithmetic ==")
    an_pairs = [e["pair"] for e in entries if e["split"] == "analysis"]
    n_cells = len(an_pairs) * len(C1_WINDOW)
    n_after = sum(1 for p in an_pairs for d in C1_WINDOW
                  if f"{p}@d{d}" not in dropped)
    print(f"   TB-C1 window cells before any A13 drop: {n_cells}")
    print(f"   after Track 3's own drop set (arms may differ): {n_after}")
    tp = json.loads((T3 / "t3_paths.json").read_text(encoding="utf-8"))["paths"]["P"]
    n_int = [len(tp[p][str(d)]) - 2 for p in an_pairs for d in C1_WINDOW
             if tp[p][str(d)]]
    print(f"   P cells with < 2 interiors (no interior hop for TB-C4): "
          f"{sum(1 for x in n_int if x < 2)}/{len(n_int)}")
    cn = [len(c) - 2 for (p, d), c in ceilings.items() if p in an_pairs]
    print(f"   ceiling cells with < 2 interiors: {sum(1 for x in cn if x < 2)}/{len(cn)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
