"""TB-P1 probe 2 — TB-P3's ceiling construction, and the w -> infinity limit argument.

Read-only. Asserts the artifact sha256 (TB-G3 / DD-G3 discipline).

What it does, per C1-window cell (d in {10,15,20}) on `pairs_v2.json`:

  A. Re-walks production (committed `run_arms.walk` + committed `mirror.py`) and
     reconstructs the victim sequence exactly as `dd_p1_headroom.py` does, so the
     exclusion sets are the ones TB-P3 says it will use.
  B. SELF-CHECK: a plain Dijkstra on production's edge cost, with this probe's own
     implementation, must return P's delivered path. If it does not, every base-cost
     figure below is wrong and nothing else in this file may be read.
  C. TB-P3's ceiling: base-cost-minimal path in the induced sub-decile subgraph
     (endpoints exempt, exclusions applied, direct edge masked).
  D. The same cell's optimum under the ACTUAL ladder doses -- w*k*max(0,pctl-0.90)
     added to production's cost, no subgraph restriction. A static per-cell derivation
     under P's exclusion sets: NOT an arm, NOT a walk, no criterion value. It exists
     only to test whether the finite-dose minimiser lies between P and the limit, which
     is what TB-R3's "no dose can beat the limit" presupposes.
  E. w*, the smallest dose at which the ceiling undercuts P's delivered path (the
     DD-P3-9 construction restated for the thresholded device).
  F. TB-P3's ceiling vs DD-D6's committed LIMIT path (min sum-pctl) -- a different
     member of the same zero-toll family.

Currency notice: percentile (`MirrorContext.pctl`) and cost units throughout. Fame is
reported only where a committed fame table already covers the path; coverage is stated.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_ceiling.py
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
W_HOP = 0.02
W_SIM = 3.0
W_JUMP = 1.0
C1_WINDOW = (10, 15, 20)
LADDER = (0.10, 0.30, 1.00)


def dijkstra(store, pctl, pop, src, dst, allowed, hard, toll_factor):
    """Production cost + toll_factor * max(0, pctl(v) - KNEE) on the relaxation target,
    target exempt. `allowed` is None or a bool mask (endpoints exempted by the caller).
    The direct src->dst edge is masked unconditionally, so every path is guard-compliant.
    Floor term omitted: identically zero at every depth this probe reads (DD-D4).
    """
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
        pu = float(pop[u])
        for k in range(offsets[u], offsets[u + 1]):
            v = int(neighbours[k])
            if v in hard:
                continue
            if u == src and v == dst:
                continue
            if allowed is not None and not allowed[v]:
                continue
            cost = (W_SIM * (1.0 - float(scores[k]))
                    + W_JUMP * abs(pu - float(pop[v]))
                    + W_HOP)
            if toll_factor and v != dst:
                cost += toll_factor * max(0.0, float(pctl[v]) - KNEE)
            nd = d + cost
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


def base_cost(store, pop, path) -> float:
    offsets, neighbours, scores = store.offsets, store.neighbours, store.scores
    total = 0.0
    for u, v in zip(path, path[1:]):
        s = None
        for k in range(offsets[u], offsets[u + 1]):
            if int(neighbours[k]) == v:
                s = float(scores[k])
                break
        assert s is not None, f"edge {u}->{v} absent from CSR"
        total += W_SIM * (1.0 - s) + W_JUMP * abs(float(pop[u]) - float(pop[v])) + W_HOP
    return total


def toll_sum(pctl, path) -> float:
    return sum(max(0.0, float(pctl[v]) - KNEE) for v in path[1:-1])


def n_above(pctl, path) -> int:
    return sum(1 for v in path[1:-1] if float(pctl[v]) > KNEE)


def med_pctl(pctl, path) -> float:
    return statistics.median([float(pctl[v]) for v in path[1:-1]])


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
    pctl = ctx.pctl
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prv = by_name.get(nm)
        if prv is None or pop[i] > pop[prv]:
            by_name[nm] = i

    pairs_doc = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    assert pairs_doc["artifact_sha256"] == digest
    entries = [dict(e, split="analysis") for e in pairs_doc["analysis_pairs"]]
    entries += [dict(e, split="held_out") for e in pairs_doc["held_out_pairs"]]

    below = pctl < KNEE
    dropped = set(json.loads((T3 / "t3_paths.json").read_text(encoding="utf-8"))
                  ["dropped_cells_d7"])

    rows: list[dict] = []
    sc_ok = sc_n = 0
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

        for d in C1_WINDOW:
            key = f"{e['pair']}@d{d}"
            p = paths[d]
            if p is None or key in dropped:
                rows.append({"pair": e["pair"], "split": e["split"], "depth": d,
                             "state": "dropped"})
                continue
            hard = set(victims[:d]) - {src, dst}

            mine = dijkstra(store, pctl, pop, src, dst, None, hard, 0.0)
            sc_n += 1
            sc_ok += int(mine == p)

            allowed = below.copy()
            allowed[src] = allowed[dst] = True
            ceil = dijkstra(store, pctl, pop, src, dst, allowed, hard, 0.0)

            r = {"pair": e["pair"], "split": e["split"], "depth": d, "state": "ok",
                 "p_path": p, "p_int": len(p) - 2, "p_base": base_cost(store, pop, p),
                 "p_toll": toll_sum(pctl, p), "p_med": med_pctl(pctl, p),
                 "p_above": n_above(pctl, p), "ceil": ceil}
            if ceil is not None:
                assert all(float(pctl[v]) < KNEE for v in ceil[1:-1]), "ceiling not sub-decile"
                r.update({"ceil_int": len(ceil) - 2,
                          "ceil_base": base_cost(store, pop, ceil),
                          "ceil_med": med_pctl(pctl, ceil)})
                r["w_star"] = ((r["ceil_base"] - r["p_base"]) / (d * r["p_toll"])
                               if r["p_toll"] > 0 else 0.0)
            for w in LADDER:
                q = dijkstra(store, pctl, pop, src, dst, None, hard, w * d)
                r[f"w{w}"] = {"int": len(q) - 2, "med": med_pctl(pctl, q),
                              "above": n_above(pctl, q), "toll": toll_sum(pctl, q),
                              "base": base_cost(store, pop, q), "path": q}
            rows.append(r)

    print(f"== B. SELF-CHECK: probe cost reproduces P's delivered path on "
          f"{sc_ok}/{sc_n} cells ==")
    assert sc_ok == sc_n, "base-cost implementation disagrees with P — stop"

    an = [r for r in rows if r["split"] == "analysis" and r["state"] == "ok"]
    have = [r for r in an if r["ceil"] is not None]

    print("\n== C/E. TB-P3's ceiling vs P, C1-window ANALYSIS cells ==")
    print(f"{'pair':<40}{'d':>3}{'Pn':>4}{'P>kn':>6}{'Pmed':>8}"
          f"{'Cn':>4}{'Cmed':>8}{'dBase':>8}{'P toll':>8}{'w*':>9}")
    for r in an:
        if r["ceil"] is None:
            print(f"{r['pair'][:39]:<40}{r['depth']:>3}   NO CEILING")
            continue
        print(f"{r['pair'][:39]:<40}{r['depth']:>3}{r['p_int']:>4}{r['p_above']:>6}"
              f"{r['p_med']:8.4f}{r['ceil_int']:>4}{r['ceil_med']:8.4f}"
              f"{r['ceil_base'] - r['p_base']:8.3f}{r['p_toll']:8.3f}{r['w_star']:9.4f}")

    print(f"\n  ceiling exists on {len(have)}/{len(an)} analysis C1-window cells")
    print(f"  interior count  P: mean {statistics.mean(r['p_int'] for r in have):.2f} "
          f"median {statistics.median(r['p_int'] for r in have):.1f}    "
          f"ceiling: mean {statistics.mean(r['ceil_int'] for r in have):.2f} "
          f"median {statistics.median(r['ceil_int'] for r in have):.1f}")
    dlt = [r["ceil_int"] - r["p_int"] for r in have]
    print(f"  mean paired interior-count delta (ceiling - P): {statistics.mean(dlt):+.2f}"
          f"   (TB-C6 flags a drop > 1.0)")
    ls = [(r["p_int"] - r["ceil_int"]) / r["p_int"] for r in have]
    print(f"  DD-D5 decomposition for THIS device: length share = (n_P - n_C)/n_P")
    print(f"    min {min(ls):.3f}  median {statistics.median(ls):.3f}  max {max(ls):.3f}")
    ws = [r["w_star"] for r in have]
    print(f"  w* (dose at which the ceiling undercuts P at that depth): "
          f"min {min(ws):.4f}  median {statistics.median(ws):.4f}  max {max(ws):.4f}")
    for w in LADDER:
        print(f"    w = {w:<5} >= w* on {sum(1 for x in ws if w >= x)}/{len(ws)} cells")

    print("\n== D. finite-dose STATIC optima under P's own exclusion sets ==")
    print("   (one Dijkstra per cell at fixed k; not an arm, not a criterion)")
    cols = ["P"] + [f"w={w}" for w in LADDER] + ["ceiling"]
    def series(fn_p, fn_w, fn_c):
        return [fn_p] + [fn_w(w) for w in LADDER] + [fn_c]
    print(f"{'quantity':<34}" + "".join(f"{c:>11}" for c in cols))
    print(f"{'mean interior count':<34}"
          + "".join(f"{x:11.2f}" for x in series(
              statistics.mean(r["p_int"] for r in have),
              lambda w: statistics.mean(r[f"w{w}"]["int"] for r in have),
              statistics.mean(r["ceil_int"] for r in have))))
    print(f"{'mean of cell-median pctl':<34}"
          + "".join(f"{x:11.4f}" for x in series(
              statistics.mean(r["p_med"] for r in have),
              lambda w: statistics.mean(r[f"w{w}"]["med"] for r in have),
              statistics.mean(r["ceil_med"] for r in have))))
    print(f"{'mean # above-knee interiors':<34}"
          + "".join(f"{x:11.2f}" for x in series(
              statistics.mean(r["p_above"] for r in have),
              lambda w: statistics.mean(r[f"w{w}"]["above"] for r in have), 0.0)))
    print(f"{'mean path toll (pctl units)':<34}"
          + "".join(f"{x:11.4f}" for x in series(
              statistics.mean(r["p_toll"] for r in have),
              lambda w: statistics.mean(r[f"w{w}"]["toll"] for r in have), 0.0)))
    print(f"{'cells identical to P':<34}"
          + "".join(f"{x:11d}" for x in series(
              len(have),
              lambda w: sum(1 for r in have if r[f"w{w}"]["path"] == r["p_path"]), 0)))
    print(f"{'cells identical to the ceiling':<34}"
          + "".join(f"{x:11d}" for x in series(
              0, lambda w: sum(1 for r in have if r[f"w{w}"]["path"] == r["ceil"]),
              len(have))))
    print(f"{'cells strictly between':<34}"
          + "".join(f"{x:11d}" for x in series(
              0,
              lambda w: sum(1 for r in have
                            if r[f"w{w}"]["path"] not in (r["p_path"], r["ceil"])), 0)))

    print("\n== F. TB-P3's ceiling vs DD-D6's committed LIMIT (min sum-pctl) ==")
    gp = json.loads((T3 / "gap_paths.json").read_text(encoding="utf-8"))
    gf = json.loads((T3 / "gap_fame.json").read_text(encoding="utf-8"))["fame"]
    mb = gp["node_mbids"]
    same = diff = 0
    lim_int, ceil_int_l, lim_F, p_F, ceil_F = [], [], [], [], []
    ceil_uncovered = 0
    for r in have:
        lim = gp["paths"]["LIMIT"].get(r["pair"], {}).get(str(r["depth"]))
        pp = gp["paths"]["P"].get(r["pair"], {}).get(str(r["depth"]))
        if not lim or not pp:
            continue
        same += int(lim == r["ceil"])
        diff += int(lim != r["ceil"])
        lim_int.append(len(lim) - 2)
        ceil_int_l.append(r["ceil_int"])
        lim_F.append(statistics.mean(gf[mb[str(v)]] for v in lim[1:-1]))
        p_F.append(statistics.mean(gf[mb[str(v)]] for v in pp[1:-1]))
        try:
            ceil_F.append(statistics.mean(gf[store.mbids[v]] for v in r["ceil"][1:-1]))
        except KeyError:
            ceil_uncovered += 1
    print(f"  cells where the two limit paths are identical: {same}/{same + diff}")
    print(f"  mean interior count   DD-D6 LIMIT {statistics.mean(lim_int):.2f}   "
          f"TB-P3 ceiling {statistics.mean(ceil_int_l):.2f}")
    print(f"  P delivered path      mean interior F {statistics.mean(p_F):.3f}")
    print(f"  DD-D6 LIMIT           mean interior F {statistics.mean(lim_F):.3f}   "
          f"gap {statistics.mean(lim_F) - statistics.mean(p_F):+.3f}")
    print(f"  TB-P3 ceiling: {len(ceil_F)}/{len(ceil_int_l)} cells fully covered by the "
          f"committed fame table ({ceil_uncovered} need TB-P2 fetches)")
    if ceil_F:
        print(f"    on covered cells only, TB-P3 ceiling mean interior F "
              f"{statistics.mean(ceil_F):.3f}")

    out = {"artifact_sha256": digest,
           "note": "TB-P1 probe 2; pctl/cost currency; no new fame fetched",
           "knee": KNEE, "ladder": list(LADDER),
           "cells": [{k: v for k, v in r.items() if k not in ("ceil", "p_path")
                      and not isinstance(v, dict)} for r in rows]}
    (HERE / "tb_p1_ceiling.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {HERE / 'tb_p1_ceiling.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
