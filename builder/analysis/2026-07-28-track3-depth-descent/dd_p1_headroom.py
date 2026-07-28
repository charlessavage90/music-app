"""DD-P1 — depth headroom. Runs BEFORE any arm; can stop the track at DD-R3.

Question, per the pre-registration §4:

    For every pair x C-window depth cell on a P walk: does a guard-compliant path
    exist, within +2 hops of P's delivered length at that cell, whose interiors all
    sit below pctl 0.90, honouring that cell's exclusion set?

If the graph does not offer such a path, no pricing device can route to one, and the
arms are measuring nothing. Branch trigger: > 30 % of C1-window cells lacking headroom
=> re-draw the pair set once; a second failure stops the track at DD-R3.

**The walk is imported from the committed `run_arms.py`, not reimplemented** (prereg
§0). Exclusion sets are reconstructed from the returned paths under the same victim
rule the walker uses, and each reconstruction is asserted to lie in the previous
path's interior, so the reconstruction cannot silently diverge from the walk.

P is production. Walking it is validation, not an experimental arm (P8b precedent).

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/dd_p1_headroom.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

TOP_DECILE = 0.90        # interiors must sit strictly below this
SLACK_HOPS = 2           # "within +2 hops of P's delivered length"
C1_WINDOW = (10, 15, 20) # DD-C1's depths; the branch trigger keys on these
TRIGGER_FRAC = 0.30      # > 30 % of C1-window cells lacking headroom => re-draw


def bfs_hops(offsets, neighbours, allowed, src: int, dst: int) -> int | None:
    """Fewest hops src->dst using only `allowed` nodes, with the direct src->dst edge
    masked so the result is always guard-compliant (>= 1 interior)."""
    if src == dst:
        return 0
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        d = dist[u]
        for k in range(offsets[u], offsets[u + 1]):
            v = int(neighbours[k])
            if u == src and v == dst:
                continue                      # guard G: no direct edge
            if v in dist or not allowed[v]:
                continue
            if v == dst:
                return d + 1
            dist[v] = d + 1
            q.append(v)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default="pairs.json",
                    help="pair-set file in this directory (pairs_v2.json for the "
                         "post-trigger re-draw)")
    ap.add_argument("--out", default="headroom.json")
    args = ap.parse_args()

    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"      # DD-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from arms import SNAPSHOTS
    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    offsets = np.asarray(store.offsets)
    neighbours = np.asarray(store.neighbours)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    doc = json.loads((HERE / args.pairs).read_text(encoding="utf-8"))
    assert doc["artifact_sha256"] == digest, f"{args.pairs} drawn on a different artifact"
    entries = [dict(e, split="analysis") for e in doc["analysis_pairs"]]
    entries += [dict(e, split="held_out") for e in doc["held_out_pairs"]]

    # Guard G ON everywhere, including P (prereg §0).
    cfg = SweepConfig.production().with_(guard_min_intermediary=True)

    below = pctl < TOP_DECILE
    results: list[dict] = []

    for e in entries:
        src, dst = by_name[e["src"]], by_name[e["dst"]]
        stats = {"examined": 0, "floor_active": 0}
        paths = walk(store, src, dst, cfg, ctx, pop, find_path_mirror,
                     Exclusion, KNOWN, stats)

        # Reconstruct the exclusion sequence the walker built, under its own victim
        # rule, and assert each victim really came from the preceding interior.
        victims: list[int] = []
        for d in range(len(paths)):
            p = paths[d]
            if p is None:
                break
            interior = p[1:-1]
            if not interior:
                break
            victims.append(min(interior, key=lambda v: (-pop[v], v)))

        print(f"\n{e['src']} -> {e['dst']}  [{e['group']}/{e['split']}]")
        for d in SNAPSHOTS:
            p = paths[d]
            if p is None:
                results.append({**{k: e[k] for k in ("pair", "group", "split")},
                                "depth": d, "state": "infeasible"})
                print(f"   d{d:<2} P infeasible (cell drops under A13)")
                continue

            excl = victims[:d]
            for v in excl:
                assert v not in (src, dst), "victim rule never excludes an endpoint"
            p_hops = len(p) - 1

            allowed = below.copy()
            allowed[src] = True          # endpoints exempt
            allowed[dst] = True
            for v in excl:
                allowed[v] = False       # honour this cell's exclusion set

            h = bfs_hops(offsets, neighbours, allowed, src, dst)
            ok = h is not None and h <= p_hops + SLACK_HOPS
            results.append({**{k: e[k] for k in ("pair", "group", "split")},
                            "depth": d, "state": "scored", "p_hops": p_hops,
                            "obscure_hops": h, "headroom": bool(ok),
                            "n_excluded": len(excl)})
            mark = "yes" if ok else "NO "
            print(f"   d{d:<2} P={p_hops} hops, obscure-only="
                  f"{h if h is not None else 'unreachable':<12} headroom {mark}")

    # ---- the trigger ----
    scored = [r for r in results if r["state"] == "scored"]
    c1 = [r for r in scored if r["depth"] in C1_WINDOW]
    c1_an = [r for r in c1 if r["split"] == "analysis"]

    def frac(rows):
        if not rows:
            return 0.0, 0, 0
        lack = sum(1 for r in rows if not r["headroom"])
        return lack / len(rows), lack, len(rows)

    f_all, lack_all, n_all = frac(c1)
    f_an, lack_an, n_an = frac(c1_an)
    f_sc, lack_sc, n_sc = frac(scored)

    print("\n" + "=" * 68)
    print(f"all snapshot cells scored : {n_sc}  lacking headroom {lack_sc} "
          f"({100 * f_sc:.1f} %)")
    print(f"C1-window (d 10/15/20)    : {n_all}  lacking headroom {lack_all} "
          f"({100 * f_all:.1f} %)")
    print(f"C1-window, analysis only  : {n_an}  lacking headroom {lack_an} "
          f"({100 * f_an:.1f} %)")
    print(f"infeasible cells (dropped): "
          f"{sum(1 for r in results if r['state'] == 'infeasible')}")
    fired = f_all > TRIGGER_FRAC
    print(f"\nDD-P1 branch trigger (> {100 * TRIGGER_FRAC:.0f} % of C1-window cells): "
          f"{'FIRED — re-draw the pair set once' if fired else 'not fired'}")
    print("=" * 68)

    out = {
        "artifact_sha256": digest,
        "top_decile": TOP_DECILE,
        "slack_hops": SLACK_HOPS,
        "c1_window": list(C1_WINDOW),
        "trigger_frac": TRIGGER_FRAC,
        "trigger_fired": bool(fired),
        "summary": {
            "all_scored": {"n": n_sc, "lacking": lack_sc},
            "c1_window": {"n": n_all, "lacking": lack_all},
            "c1_window_analysis": {"n": n_an, "lacking": lack_an},
            "infeasible": sum(1 for r in results if r["state"] == "infeasible"),
        },
        "cells": results,
    }
    (HERE / args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                 encoding="utf-8")
    print(f"\nwrote {HERE / args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
