"""P8b probe 1: artifact arithmetic behind four of the harness review's questions.

Runs NO arm. Every quantity here is a property of the artifact or of the cost
function's algebra; nothing routes a path and nothing scores fame.

Questions answered:
  Q1  artifact identity, N, E, degree distribution -- so this review names what it
      measured, per the ml-graph-analyst brief.
  Q2  are edge scores ever > 1.0? (mirror.py tolls on `sim >= 1.0`, the
      pre-registration says "exactly 1.0")
  Q3  the percentile array and A3's mean-matching ratio `jump_scale_pctl`, plus the
      per-edge scale of each jump currency against w_hop.
  Q4  duplicate names -- fame.py keys fame by NAME, score.py counts distinct
      interiors by NAME; how much collapsing does the artifact force?
  Q5  X's bounding claim. The jump term penalises |dpop| SYMMETRICALLY, so setting
      w_jump = 0 removes the price of climbing as well as the price of diving.
      Measured against the only honest null: the base rate of pop-ascending
      directed edges, which is 50 % by construction in a symmetrised graph.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-p8b-harness-review/probe_artifact.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

from artistpath_api.graph_store import GraphStore  # noqa: E402
from mirror import MirrorContext, SweepConfig  # noqa: E402

out: dict = {}


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    cfg = SweepConfig.production()

    n = len(store.mbids)
    e = int(len(store.neighbours))
    deg = np.diff(store.offsets).astype(np.int64)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    sc = np.asarray(store.scores, dtype=np.float64)

    # ---- Q1 ---------------------------------------------------------------
    out["Q1_artifact"] = {
        "file": GRAPH.name,
        "sha256": digest,
        "N": n,
        "E_directed": e,
        "E_undirected": e // 2,
        "degree": {
            "min": int(deg.min()), "max": int(deg.max()),
            "mean": float(deg.mean()), "median": float(np.median(deg)),
            "p99": float(np.percentile(deg, 99)),
        },
    }

    # ---- Q2 ---------------------------------------------------------------
    out["Q2_scores"] = {
        "min": float(sc.min()), "max": float(sc.max()),
        "n_exactly_1": int((sc == 1.0).sum()),
        "n_above_1": int((sc > 1.0).sum()),
        "frac_exactly_1": float((sc == 1.0).mean()),
        "n_in_[0.999,1.0)": int(((sc >= 0.999) & (sc < 1.0)).sum()),
        "verdict": ("`sim >= 1.0` and `sim == 1.0` select the same edge set"
                    if (sc > 1.0).sum() == 0 else "DIVERGE -- scores exceed 1.0"),
    }

    # ---- Q3 ---------------------------------------------------------------
    src = np.repeat(np.arange(n, dtype=np.int64), deg)
    dst = np.asarray(store.neighbours, dtype=np.int64)
    d_raw = np.abs(pop[src] - pop[dst])
    d_pctl = np.abs(ctx.pctl[src] - ctx.pctl[dst])
    out["Q3_currencies"] = {
        "pctl_min": float(ctx.pctl.min()), "pctl_max": float(ctx.pctl.max()),
        "jump_scale_pctl": float(ctx.jump_scale_pctl),
        "mean_abs_dpop_raw": float(d_raw.mean()),
        "mean_abs_dpctl": float(d_pctl.mean()),
        "w_hop": cfg.w_hop,
        # what one mean-sized jump costs, per currency, at w_jump = 1.0
        "mean_jump_cost_raw_in_w_hop": float(d_raw.mean() * 1.0 / cfg.w_hop),
        "mean_jump_cost_pctl_meanmatched_in_w_hop":
            float(d_pctl.mean() * ctx.jump_scale_pctl / cfg.w_hop),
        "mean_jump_cost_pctl_unmatched_in_w_hop": float(d_pctl.mean() / cfg.w_hop),
        # A1u is the unnormalised diagnostic: how much bigger is it?
        "A1u_scale_vs_A1": float(1.0 / ctx.jump_scale_pctl),
    }

    # ---- Q4 ---------------------------------------------------------------
    cnt = Counter(store.names)
    dupes = {nm: c for nm, c in cnt.items() if c > 1}
    out["Q4_duplicate_names"] = {
        "distinct_names": len(cnt),
        "names_shared_by_2plus_nodes": len(dupes),
        "nodes_involved": int(sum(dupes.values())),
        "frac_nodes_with_a_shared_name": float(sum(dupes.values()) / n),
        "worst": sorted(dupes.items(), key=lambda kv: (-kv[1], kv[0]))[:10],
    }

    # ---- Q5 ---------------------------------------------------------------
    # Null: base rate of pop-ascending directed edges. Exactly 50 % (minus ties)
    # in a symmetrised graph, because every undirected edge appears both ways.
    asc_all = float((pop[dst] > pop[src]).mean())

    # Per node, the neighbour that X's cost function prefers (X: cost = w_sim*(1-sim)
    # + w_hop, so argmax sim) vs the one production prefers (full cost, floor at the
    # production base floor of 0 -- i.e. floor term dropped, so this is A0's local
    # preference; A0 == P on 251/252 cells of the gate). Ties -> lowest CSR index,
    # matching how the heap breaks ties.
    x_asc = prod_asc = 0
    x_dpop = []
    prod_dpop = []
    for u in range(n):
        a, b = int(store.offsets[u]), int(store.offsets[u + 1])
        if a == b:
            continue
        s = sc[a:b]
        vs = dst[a:b]
        dp = np.abs(pop[u] - pop[vs])
        cx = cfg.w_sim * (1.0 - s)                       # X, w_jump = 0 (w_sim scales out)
        cp = 3.0 * (1.0 - s) + 1.0 * dp                   # A0 / production weights
        vx = int(vs[int(np.argmin(cx))])
        vp = int(vs[int(np.argmin(cp))])
        x_asc += pop[vx] > pop[u]
        prod_asc += pop[vp] > pop[u]
        x_dpop.append(pop[vx] - pop[u])
        prod_dpop.append(pop[vp] - pop[u])
    m = len(x_dpop)
    out["Q5_X_is_not_a_dive_bound"] = {
        "null_frac_pop_ascending_over_all_directed_edges": asc_all,
        "nodes_measured": m,
        "X_cheapest_hop_ascends_frac": x_asc / m,
        "A0_cheapest_hop_ascends_frac": prod_asc / m,
        "X_mean_dpop_of_cheapest_hop": float(np.mean(x_dpop)),
        "A0_mean_dpop_of_cheapest_hop": float(np.mean(prod_dpop)),
        "note": ("the jump term is |dpop|, symmetric: w_jump = 0 removes the price of "
                 "CLIMBING as well as DIVING, so X is an extreme of the pricing axis, "
                 "not a lower bound on fame"),
    }

    # ---- Q6: toll magnitude is W-dependent --------------------------------
    out["Q6_toll_magnitude"] = {
        "formula": "toll = w_sim * (1 - toll_s)   (mirror.py:178)",
        "w_hop": cfg.w_hop,
        "T1a_s0.95_at_w_sim_3.0_in_w_hop": 3.0 * 0.05 / cfg.w_hop,
        "T1a_s0.95_at_w_sim_1.5_in_w_hop": 1.5 * 0.05 / cfg.w_hop,
        "T1b_s0.80_at_w_sim_3.0_in_w_hop": 3.0 * 0.20 / cfg.w_hop,
        "T1b_s0.80_at_w_sim_1.5_in_w_hop": 1.5 * 0.20 / cfg.w_hop,
        "cells_with_w_sim_1.5": ["A3", "A5", "A6", "A7", "X(ineligible)"],
    }

    (HERE / "probe_artifact.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
