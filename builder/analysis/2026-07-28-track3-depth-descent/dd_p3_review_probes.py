"""DD-P3 protocol review — independent probes over the artifact.

Written by the `ml-graph-analyst` for the DD-P3 review of the Track 3
pre-registration. **Read-only**: it loads `graph-t15-tiebreakfix.bin`, re-derives
quantities the pre-registration and the execution log assert, and prints them. It
edits nothing and writes nothing except stdout.

Sections map to the review questions:
  [0] artifact identity, N, E, degree and pctl distribution
  [B] DD-D3's unsatisfiability arithmetic: sub-decile edge counts for all six
      both-famous Track 2 carry-over candidates, and the 12/36 derivation
  [C] selection effect of the v2 draw-time headroom condition: pair-level
      acceptance rate on an unconditioned Monte-Carlo draw, and the composition
      (pctl / degree) of accepted vs rejected famous endpoints
  [D] does turning the floor off (arms DD-A4 / DD-A5) change the d0 path? i.e. is
      DD-G2 ("every arm's d0 path byte-identical to P's") satisfiable by those arms
  [E] the device's length/descent entanglement: sum-of-pctl over interiors for P's
      delivered path vs the all-obscure BFS path, and the smallest
      `w_known_ramp_pctl` at which the obscure route undercuts P's
  [F] production path length by depth, and the positional fame gradient along P's
      interiors -- both bear on DD-C2's pooled median

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/dd_p3_review_probes.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
TOP_DECILE = 0.90
SLACK = 2


def bfs_path(offsets, neighbours, allowed, src, dst):
    """Fewest-hop src->dst over `allowed`, direct edge masked. Returns the path."""
    if src == dst:
        return [src]
    prev = {src: -1}
    q = deque([src])
    while q:
        u = q.popleft()
        for k in range(offsets[u], offsets[u + 1]):
            v = int(neighbours[k])
            if u == src and v == dst:
                continue
            if v in prev or not allowed[v]:
                continue
            prev[v] = u
            if v == dst:
                p = [dst]
                while p[-1] != src:
                    p.append(prev[p[-1]])
                return p[::-1]
            q.append(v)
    return None


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"[0] artifact {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}  OK")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from arms import SNAPSHOTS
    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk
    from verify_mirror import ANALYSIS_PAIRS

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)
    scores = np.asarray(store.scores, dtype=np.float64)
    degree = np.diff(offsets)
    n = len(store.mbids)
    e_dir = int(offsets[-1])

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    print(f"    N = {n:,}   directed CSR entries = {e_dir:,}   undirected E = {e_dir // 2:,}")
    print(f"    degree: min {degree.min()} p50 {np.median(degree):.0f} "
          f"mean {degree.mean():.2f} p99 {np.percentile(degree, 99):.0f} max {degree.max()}")
    below = pctl < TOP_DECILE
    print(f"    nodes with pctl < 0.90: {below.sum():,} ({100 * below.mean():.2f} %)")

    # sub-decile degree for every node
    src_of = np.repeat(np.arange(n, dtype=np.int64), degree)
    dst_of = neighbours.astype(np.int64)
    sub_deg = np.bincount(src_of[below[dst_of]], minlength=n)

    # ---------------- [B] DD-D3 unsatisfiability ----------------
    print("\n[B] DD-D3 — both-famous Track 2 carry-over candidates")
    carry = [(a, b) for a, b in ANALYSIS_PAIRS
             if pctl[by_name[a]] >= TOP_DECILE and pctl[by_name[b]] >= TOP_DECILE]
    print(f"    both-famous pairs among Track 2 ANALYSIS_PAIRS: {len(carry)}")
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)
    for a, b in carry:
        ia, ib = by_name[a], by_name[b]
        allowed = below.copy()
        allowed[ia] = allowed[ib] = True
        p = bfs_path(offsets, neighbours, allowed, ia, ib)
        print(f"    {a:<18} pctl {pctl[ia]:.4f} deg {degree[ia]:>3} subdeg {sub_deg[ia]:>3}   "
              f"-> {b:<14} pctl {pctl[ib]:.4f} deg {degree[ib]:>3} subdeg {sub_deg[ib]:>3}"
              f"   obscure route: {'NONE' if p is None else len(p) - 1}")
    n_bad = sum(1 for a, b in carry
                if bfs_path(offsets, neighbours,
                            (lambda al, i, j: (al.__setitem__(i, True),
                                               al.__setitem__(j, True), al)[2])(
                                below.copy(), by_name[a], by_name[b]),
                            by_name[a], by_name[b]) is None)
    print(f"    candidates with NO all-obscure route at all: {n_bad}/{len(carry)}")
    print(f"    => any 4 of them contribute 4*3 = 12 lacking cells of "
          f"12 pairs * 3 depths = 36  ->  {12 / 36:.4f} = {100 * 12 / 36:.1f} % vs 30 % trigger")

    # pctl-band share of nodes with zero sub-decile edges (log DD-F1's table)
    print("\n    zero-sub-decile share by pctl band (DD-F1 cross-check):")
    for lo, hi in [(0.90, 0.95), (0.95, 0.99), (0.99, 0.995), (0.995, 0.999), (0.999, 1.01)]:
        m = (pctl >= lo) & (pctl < hi)
        if m.sum():
            print(f"      [{lo:.3f},{hi:.3f})  n={m.sum():>6,}  zero-subdeg "
                  f"{100 * (sub_deg[m] == 0).mean():5.1f} %")

    # ---------------- [C] selection effect of the v2 draw ----------------
    print("\n[C] selection effect of the DD-P1-at-draw-time acceptance rule")
    famous_pool = [i for i in range(n) if degree[i] > 1 and pctl[i] >= 0.90]
    mid_pool = [i for i in range(n) if degree[i] > 1 and 0.50 <= pctl[i] < 0.90]
    print(f"    pools (degree>1): famous {len(famous_pool):,}  mid {len(mid_pool):,}")

    rng = random.Random(11071)
    N_MC = 300
    for label, sp, tp in (("famous->mid", famous_pool, mid_pool),
                          ("mid->mid", mid_pool, mid_pool)):
        acc = 0
        acc_src, rej_src = [], []
        for _ in range(N_MC):
            s, t = rng.choice(sp), rng.choice(tp)
            if s == t:
                continue
            allowed = below.copy()
            allowed[s] = allowed[t] = True
            p = bfs_path(offsets, neighbours, allowed, s, t)
            ok = p is not None
            (acc_src if ok else rej_src).append(s)
            acc += ok
        print(f"    {label:<12} unconditioned acceptance (obscure route exists): "
              f"{acc}/{N_MC} = {100 * acc / N_MC:.1f} %")
        if rej_src:
            print(f"        accepted src: pctl mean {np.mean(pctl[acc_src]):.4f} "
                  f"median {np.median(pctl[acc_src]):.4f}  deg median {np.median(degree[acc_src]):.0f}"
                  f"  subdeg median {np.median(sub_deg[acc_src]):.0f}")
            print(f"        rejected src: pctl mean {np.mean(pctl[rej_src]):.4f} "
                  f"median {np.median(pctl[rej_src]):.4f}  deg median {np.median(degree[rej_src]):.0f}"
                  f"  subdeg median {np.median(sub_deg[rej_src]):.0f}")

    fp = np.array(famous_pool)
    usable = sub_deg[fp] > 0
    print(f"    famous pool: {100 * usable.mean():.1f} % have >=1 sub-decile edge")
    print(f"        usable   pctl mean {pctl[fp[usable]].mean():.4f}  deg mean {degree[fp[usable]].mean():.1f}")
    print(f"        unusable pctl mean {pctl[fp[~usable]].mean():.4f}  deg mean {degree[fp[~usable]].mean():.1f}")
    for lo, hi in [(0.90, 0.93), (0.93, 0.96), (0.96, 0.99), (0.99, 1.01)]:
        m = (pctl[fp] >= lo) & (pctl[fp] < hi)
        if m.sum():
            print(f"        band [{lo:.2f},{hi:.2f}): usable {100 * (sub_deg[fp[m]] > 0).mean():5.1f} % "
                  f"of {m.sum():,}")

    v2 = json.loads((HERE / "pairs_v2.json").read_text(encoding="utf-8"))
    drawn = v2["analysis_pairs"] + v2["held_out_pairs"]
    fam_src = [by_name[e["src"]] for e in drawn if e["group"] == "famous_mid"]
    print(f"    drawn famous endpoints (v2): pctl {sorted(round(float(pctl[i]), 4) for i in fam_src)}")
    print(f"        their sub-decile degrees: {[int(sub_deg[i]) for i in fam_src]} "
          f"of total degrees {[int(degree[i]) for i in fam_src]}")

    # ---------------- [D] floor off at d0 ----------------
    print("\n[D] does w_floor=0 (arms DD-A4/DD-A5) change the d0 path? -> DD-G2")
    cfg_nofloor = cfg.with_(w_floor=0.0)
    all_pairs = [(e["src"], e["dst"]) for e in drawn]
    anchors = [tuple(p.split(" -> ")) for p in v2["unscored_anchor_pairs"]]
    diff = same = 0
    for a, b in all_pairs + anchors:
        s, t = by_name[a], by_name[b]
        p1 = find_path_mirror(store, s, t, [], cfg, ctx)
        p2 = find_path_mirror(store, s, t, [], cfg_nofloor, ctx)
        eq = p1 == p2
        same += eq
        diff += not eq
        if not eq:
            print(f"    DIFFERS  {a} -> {b}: P {len(p1) - 1} hops, floor-off {len(p2) - 1} hops")
    print(f"    d0 identical in {same}/{same + diff} pairs; differs in {diff}")

    # ---------------- [E] the toll's length/descent entanglement ----------------
    print("\n[E] toll = w*k*sum(pctl over interiors): P's path vs the all-obscure route")
    print("    pair                                 k   nP  SP     nOb SOb    dCost   w*")
    an = [(e["src"], e["dst"]) for e in v2["analysis_pairs"]]
    W_HOP, W_SIM, W_JUMP, W_FLOOR, RELAX = 0.02, 3.0, 1.0, 1.0, 0.15
    simlook: dict[tuple[int, int], float] = {}

    def sim_of(u, v):
        key = (u, v)
        if key not in simlook:
            for kk in range(offsets[u], offsets[u + 1]):
                if int(neighbours[kk]) == v:
                    simlook[key] = float(scores[kk])
                    break
            else:
                simlook[key] = float("nan")
        return simlook[key]

    def base_cost(path, s, t, k, hard):
        floor_val = max(0.0, min(pop[s], pop[t]) - RELAX * k)
        c = 0.0
        for u, v in zip(path, path[1:]):
            c += (W_SIM * (1.0 - sim_of(u, v)) + W_JUMP * abs(pop[u] - pop[v])
                  + W_FLOOR * max(0.0, floor_val - pop[v]) + W_HOP)
        return c

    walks = {}
    for a, b in an:
        s, t = by_name[a], by_name[b]
        stats = {"examined": 0, "floor_active": 0}
        paths = walk(store, s, t, cfg, ctx, pop, find_path_mirror, Exclusion, KNOWN, stats)
        walks[(a, b)] = paths
        victims = []
        for d in range(len(paths)):
            p = paths[d]
            if p is None or not p[1:-1]:
                break
            victims.append(min(p[1:-1], key=lambda v: (-pop[v], v)))
        for k in (10, 20):
            p = paths[k]
            if p is None:
                continue
            excl = victims[:k]
            allowed = below.copy()
            allowed[s] = allowed[t] = True
            for v in excl:
                allowed[v] = False
            ob = bfs_path(offsets, neighbours, allowed, s, t)
            if ob is None:
                print(f"    {a[:22]:<22}->{b[:14]:<14} k={k:<3} no obscure route")
                continue
            SP = float(pctl[p[1:-1]].sum())
            SO = float(pctl[ob[1:-1]].sum())
            dc = base_cost(ob, s, t, k, excl) - base_cost(p, s, t, k, excl)
            wstar = dc / (k * (SP - SO)) if SP > SO else float("inf")
            print(f"    {a[:22]:<22}->{b[:14]:<14} k={k:<3} {len(p) - 1:>3} {SP:6.2f} "
                  f"{len(ob) - 1:>3} {SO:6.2f}  {dc:7.3f}  {wstar:.4f}")

    # ---------------- [F] length and positional gradient ----------------
    print("\n[F] production path length by depth, and positional pctl gradient")
    for d in SNAPSHOTS:
        lens = [len(walks[p][d]) - 2 for p in an if walks[p][d]]
        print(f"    d{d:<2} interior count: median {np.median(lens):.1f} "
              f"mean {np.mean(lens):.2f}  range {min(lens)}-{max(lens)}")
    print("    pooled interior pctl by normalised position along P's path (d5 and d20):")
    for d in (5, 20):
        bins = [[] for _ in range(5)]
        for p in an:
            path = walks[p][d]
            if not path:
                continue
            ints = path[1:-1]
            m = len(ints)
            for j, v in enumerate(ints):
                bins[min(4, int(5 * j / m))].append(float(pctl[v]))
        print(f"      d{d:<2} " + "  ".join(
            f"q{i + 1}={np.mean(b):.3f}(n={len(b)})" for i, b in enumerate(bins) if b))
    print("    pooled interior pctl median, d5 vs d20 (the shape DD-C2/C3 uses):")
    for d in (5, 20):
        vals = [float(pctl[v]) for p in an if walks[p][d] for v in walks[p][d][1:-1]]
        print(f"      d{d:<2} n={len(vals):>4}  median {np.median(vals):.4f}  mean {np.mean(vals):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
