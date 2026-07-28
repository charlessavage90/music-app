"""ASC-5 discharge: path-level ascent + the X-vs-A7 one-hop isolating contrast.

Decision rules and thresholds live in README.md, committed at 8562d15 BEFORE this
script first ran. Runs NO experimental arm: inputs are the committed stage-1 walks,
the committed scores, and the adopted artifact. BFS geodesics are a structural null
(same class as the P8b review's Q5 edge base rate), not a routed arm.

All fresh figures are in pop_raw / popularity-percentile currency, never fame
(README's currency notice; Phase 1 log §2.11).

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-asc5-path-ascent/asc5_path_ascent.py
"""

from __future__ import annotations

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

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SCORER = ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"

# PLA-G1 reference values: P8b probe_artifact.json Q5, committed 2026-07-24.
G1_NULL, G1_A0, G1_X = 0.4998, 0.8261, 0.8687

from artistpath_api.graph_store import GraphStore  # noqa: E402
from mirror import MirrorContext, SweepConfig  # noqa: E402

out: dict = {}


def one_hop_ascent(store, ctx, pop, sc, dst) -> dict:
    """Q5's exact method (ties -> lowest CSR index; floor dropped), extended to A7."""
    n = len(store.mbids)
    pctl = ctx.pctl
    jscale = ctx.jump_scale_pctl
    counts = {"A0": 0, "A7": 0, "X": 0}
    dpop = {"A0": [], "A7": [], "X": []}
    m = 0
    for u in range(n):
        a, b = int(store.offsets[u]), int(store.offsets[u + 1])
        if a == b:
            continue
        m += 1
        s = sc[a:b]
        vs = dst[a:b]
        dp_raw = np.abs(pop[u] - pop[vs])
        dp_pctl = np.abs(pctl[u] - pctl[vs])
        costs = {
            "A0": 3.0 * (1.0 - s) + 1.0 * dp_raw,
            "A7": 1.5 * (1.0 - s) + 0.3 * jscale * dp_pctl,
            "X": 1.5 * (1.0 - s),
        }
        for arm, c in costs.items():
            v = int(vs[int(np.argmin(c))])
            counts[arm] += int(pop[v] > pop[u])
            dpop[arm].append(pop[v] - pop[u])
    return {
        "nodes_measured": m,
        "null_frac_pop_ascending_over_all_directed_edges":
            float((pop[dst] > pop[np.repeat(np.arange(n),
                                            np.diff(store.offsets))]).mean()),
        "ascent_frac": {k: float(counts[k] / m) for k in counts},
        "mean_dpop_of_cheapest_hop": {k: float(np.mean(dpop[k])) for k in dpop},
    }


def bfs_dist(store, src: int) -> np.ndarray:
    n = len(store.mbids)
    dist = np.full(n, -1, dtype=np.int64)
    dist[src] = 0
    q = deque([src])
    offs, nbrs = store.offsets, store.neighbours
    while q:
        u = q.popleft()
        du = dist[u]
        for i in range(int(offs[u]), int(offs[u + 1])):
            v = int(nbrs[i])
            if dist[v] < 0:
                dist[v] = du + 1
                q.append(v)
    return dist


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"  # PLA-G2
    paths_doc = json.loads((SCORER / "paths.json").read_text(encoding="utf-8"))
    assert paths_doc["artifact_sha256"] == EXPECT, "paths.json artifact mismatch"  # PLA-G2
    scores_doc = json.loads((SCORER / "scores.json").read_text(encoding="utf-8"))

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    assert SweepConfig.production().w_sim == 3.0  # weights the A0 recompute mirrors
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    sc = np.asarray(store.scores, dtype=np.float64)
    dst = np.asarray(store.neighbours, dtype=np.int64)
    deg = np.diff(store.offsets).astype(np.int64)
    pctl = ctx.pctl

    # ---- PLA-G1 + PLA-R3: one-hop -----------------------------------------
    oh = one_hop_ascent(store, ctx, pop, sc, dst)
    g1 = {
        "null": float(round(oh["null_frac_pop_ascending_over_all_directed_edges"], 4)),
        "A0": float(round(oh["ascent_frac"]["A0"], 4)),
        "X": float(round(oh["ascent_frac"]["X"], 4)),
        "expected": {"null": G1_NULL, "A0": G1_A0, "X": G1_X},
    }
    g1["pass"] = bool(g1["null"] == G1_NULL and g1["A0"] == G1_A0
                      and g1["X"] == G1_X)
    out["PLA_G1_reproduction"] = g1
    assert g1["pass"], f"PLA-G1 FAILED — instrument differs from P8b's: {g1}"

    delta = oh["ascent_frac"]["X"] - oh["ascent_frac"]["A7"]
    out["PLA_R3_one_hop"] = {
        **oh,
        "delta_X_minus_A7": delta,
        "read": ("jump price at A7's dilution is NOT a material brake; climb carried "
                 "by the similarity term" if abs(delta) <= 0.02 else
                 "jump term is a real brake even diluted; directional pricing live"
                 if delta >= 0.05 else
                 "jump price PROMOTES climbing; mechanism check required"
                 if delta <= -0.05 else "ambiguous band"),
    }

    # ---- PLA-G3: no degree-1 interior anywhere ----------------------------
    bad = []
    for arm, pairs in paths_doc["paths"].items():
        for pair, depths in pairs.items():
            for d, path in depths.items():
                for v in path[1:-1]:
                    if deg[v] == 1:
                        bad.append((arm, pair, d, v))
    out["PLA_G3_degree1_interiors"] = {"count": len(bad), "cases": bad[:10]}
    assert not bad, f"PLA-G3 FAILED — degree-1 interiors delivered: {bad[:5]}"

    # ---- PLA-R1: delivered d0 vs geodesic null, arm P ----------------------
    P = paths_doc["paths"]["P"]
    per_pair = {}
    diffs = []
    excluded = []
    for pair, depths in P.items():
        path0 = depths["0"]
        A, B = path0[0], path0[-1]
        dA = bfs_dist(store, A)
        dB = bfs_dist(store, B)
        dist_ab = int(dA[B])
        if dist_ab < 2:
            excluded.append({"pair": pair, "geodesic_dist": dist_ab})
            continue
        geo = np.where((dA >= 0) & (dB >= 0) & (dA + dB == dist_ab))[0]
        geo = geo[(geo != A) & (geo != B)]
        delivered = np.array(path0[1:-1], dtype=np.int64)
        row = {
            "geodesic_dist": dist_ab,
            "delivered_hops_d0": len(path0) - 1,
            "geodesic_interior_count": int(len(geo)),
            "delivered_interior_median_pctl": float(np.median(pctl[delivered])),
            "geodesic_interior_median_pctl": float(np.median(pctl[geo])),
        }
        row["diff"] = (row["delivered_interior_median_pctl"]
                       - row["geodesic_interior_median_pctl"])
        per_pair[pair] = row
        diffs.append(row["diff"])
    D = float(np.median(diffs))
    out["PLA_R1_path_level_climb"] = {
        "per_pair": per_pair,
        "pairs_excluded_dist_lt_2": excluded,
        "n_pairs_included": len(diffs),
        "D_median_delivered_minus_geodesic_pctl": D,
        "read": ("climb is a ROUTING CHOICE at path level; ASC-1 reaches the journey"
                 if D >= 0.10 else
                 "ASC-3 COLLAPSES at path level; famous interiors are arithmetic"
                 if D <= 0.03 else "ambiguous band: weakened, not settled"),
    }

    # ---- PLA-R2: context — P's interior pctl by bypass depth ---------------
    by_depth = {}
    for d in map(str, paths_doc["snapshots"]):
        pooled = [pctl[v] for depths in P.values() if d in depths
                  for v in depths[d][1:-1]]
        if pooled:
            by_depth[d] = {
                "n_pairs_with_cell": sum(1 for dp in P.values() if d in dp),
                "n_interiors_pooled": len(pooled),
                "median_pctl": float(np.median(pooled)),
                "min_pctl": float(np.min(pooled)),
            }
    out["PLA_R2_P_interior_pctl_by_depth"] = by_depth

    # ---- PLA-R4: path-level X vs A7 ----------------------------------------
    iso = scores_doc["one_column_contrasts"]["isolating"]["X"]
    assert iso["vs"] == "A7"
    r4a = iso["mean_dF"]
    xp, a7p = paths_doc["paths"]["X"], paths_doc["paths"]["A7"]
    paired = []
    for pair in xp:
        for d in xp[pair]:
            if int(d) >= 10 and pair in a7p and d in a7p[pair]:
                mx = float(np.median(pctl[np.array(xp[pair][d][1:-1])]))
                ma = float(np.median(pctl[np.array(a7p[pair][d][1:-1])]))
                paired.append(mx - ma)
    out["PLA_R4_path_level_X_vs_A7"] = {
        "a_fame_log10_from_committed_scores": r4a,
        "a_source": "scores.json one_column_contrasts.isolating.X (vs A7), exact per F9",
        "b_median_paired_interior_pctl_diff_d_ge_10": float(np.median(paired)),
        "b_mean_paired_interior_pctl_diff_d_ge_10": float(np.mean(paired)),
        "b_n_paired_cells": len(paired),
        "read_a": ("jump price immaterial at path level (|dF| <= 0.1)"
                   if abs(r4a) <= 0.1 else
                   "jump term matters at path depth" if abs(r4a) >= 0.3
                   else "ambiguous band"),
    }

    (HERE / "asc5_path_ascent.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
