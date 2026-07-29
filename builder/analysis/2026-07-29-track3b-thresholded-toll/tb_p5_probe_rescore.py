"""TB-P5 probe 2 — independent rescoring of TB-C1..TB-C6 from the committed paths.

Does NOT import `score_tb.py`. Reads only `tb_paths.json` + `tb_fame.json` and the
artifact, recomputes every headline figure in `tb_scores.json` by a separate route
(numpy medians rather than `statistics`, different loop structure), and reports the
max absolute discrepancy per figure.

Also computes the sensitivities TB-P5 was asked for and `score_tb.py` does not:
per-pair spread behind TB-C1 (leave-one-pair-out), the two thin-headroom pairs cell by
cell, TB-C6 under a cell-median variant, TB-C2 under the DD-P3H-2 pooling family, and
the A11 unmatched share per arm both distinct- and occurrence-weighted.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p5_probe_rescore.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

C1_DEPTHS = (10, 15, 20)
KNEE = 0.90
THIN = ("Patti Smith -> Daniel Herskedal", "Openzone Bar -> Gjallarhorn")


def med(xs) -> float:
    return float(np.median(np.asarray(xs, dtype=np.float64)))


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # TB-G3
    from artistpath_api.graph_store import GraphStore

    store = GraphStore.load(GRAPH)
    offsets = np.asarray(store.offsets, dtype=np.int64)
    nbrs = np.asarray(store.neighbours, dtype=np.int64)
    scores = np.asarray(store.scores, dtype=np.float64)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    n = pop.size
    vals, inv, counts = np.unique(pop, return_inverse=True, return_counts=True)
    last = np.cumsum(counts) - 1
    pctl = ((last - counts + 1 + last) / 2.0)[inv] / (n - 1)
    degree = np.diff(offsets)
    top_deg_cut = float(np.percentile(degree, 99.0))

    P = json.loads((HERE / "tb_paths.json").read_text(encoding="utf-8"))
    FA = json.loads((HERE / "tb_fame.json").read_text(encoding="utf-8"))
    SC = json.loads((HERE / "tb_scores.json").read_text(encoding="utf-8"))
    assert P["artifact_sha256"] == digest == SC["artifact_sha256"]

    F, rows = FA["fame"], FA["rows"]
    flagged = set(FA["potentially_notable_unmatched"])
    mbids, names = P["node_mbids"], P["node_names"]
    arms, splits = P["arms"], P["splits"]
    analysis = [p for p in P["pairs"] if splits[p] == "analysis"]
    held_out = [p for p in P["pairs"] if splits[p] == "held_out"]

    def path(arm, pair, d):
        return P["paths"][arm][pair][str(d)]

    def ims(p):
        return [mbids[str(x)] for x in p[1:-1]]

    out: dict = {"artifact_sha256": digest, "checks": {}, "disc": {}}
    discs: list[tuple[str, float]] = []

    def rec(label, mine, theirs):
        if mine is None or theirs is None:
            d = 0.0 if mine == theirs else float("inf")
        else:
            d = abs(float(mine) - float(theirs))
        discs.append((label, d))
        return d

    # ---- fame-join integrity ----------------------------------------------------
    all_scored_nodes = {x for arm in arms for p in analysis + held_out
                        for d in P["snapshots"] if (q := path(arm, p, d))
                        for x in q[1:-1]}
    missing_F = sorted({mbids[str(x)] for x in all_scored_nodes
                        if mbids[str(x)] not in F})
    blank_any = sorted(k for k, v in names.items() if not v.strip())
    dup_mbid = len(mbids.values()) - len(set(mbids.values()))
    out["checks"]["fame_join"] = {
        "scored_interior_nodes": len(all_scored_nodes),
        "mbids_missing_from_fame": missing_F,
        "blank_named_nodes_anywhere_in_node_names": len(blank_any),
        "node_names_total": len(names),
        "duplicate_mbids_across_node_ids": dup_mbid,
        "fame_table_n": FA["n"], "fame_matched": FA["matched"],
        "fame_unmatched": FA["unmatched"],
        "flag_list_len": len(flagged),
        "flag_all_unmatched": all(not rows[m].get("matched") for m in flagged),
        "nameless_nodes_in_fame": len(FA["nameless_nodes"]),
    }

    # ---- TB-C1(i) counterfactual constant ---------------------------------------
    pool = [F[m] for p in analysis for d in C1_DEPTHS if (q := path("P", p, d))
            for m in ims(q) if rows[m].get("matched")]
    cf = med(pool)
    rec("counterfactual_F", cf, SC["thresholds"]["counterfactual_F"])
    out["checks"]["counterfactual"] = {
        "pool_n": len(pool), "median": cf,
        "committed": SC["thresholds"]["counterfactual_F"],
        "all_interiors_median_for_contrast":
            med([F[m] for p in analysis for d in C1_DEPTHS
                 if (q := path("P", p, d)) for m in ims(q)]),
    }
    rec("top_degree_cut", top_deg_cut, SC["thresholds"]["top_degree_cut"])

    def c1(arm, pairs, fv):
        cells = []
        for pair in pairs:
            for d in C1_DEPTHS:
                pa, pp = path(arm, pair, d), path("P", pair, d)
                if not pa or not pp:
                    continue
                fa = [y for m in ims(pa) if (y := fv(m)) is not None]
                fp = [y for m in ims(pp) if (y := fv(m)) is not None]
                if not fa or not fp:
                    continue
                cells.append((pair, d, med(fa) - med(fp)))
        if not cells:
            return None
        v = [c[2] for c in cells]
        return {"mean": float(np.mean(v)), "neg_frac": sum(1 for x in v if x < 0) / len(v),
                "n": len(v), "cells": cells}

    per_arm: dict = {}
    for arm in arms:
        r: dict = {}
        a = c1(arm, analysis, lambda m: F[m])
        mt = c1(arm, analysis, lambda m: F[m] if rows[m].get("matched") else None)
        cfb = c1(arm, analysis, lambda m: cf if m in flagged else F[m])
        S = SC["results"][arm]
        for tag, blk, key in (("all", a, "c1_all"), ("matched", mt, "c1_matched"),
                              ("cf", cfb, "c1_counterfactual")):
            rec(f"{arm}.c1_{tag}.mean", blk["mean"], S[key]["mean"])
            rec(f"{arm}.c1_{tag}.negfrac", blk["neg_frac"], S[key]["neg_frac"])
            rec(f"{arm}.c1_{tag}.n", blk["n"], S[key]["n"])
        r["c1"] = {"all": {k: a[k] for k in ("mean", "neg_frac", "n")},
                   "matched": {k: mt[k] for k in ("mean", "neg_frac", "n")},
                   "counterfactual": {k: cfb[k] for k in ("mean", "neg_frac", "n")}}

        # per-pair spread + leave-one-pair-out on the primary
        bypair: dict[str, list[float]] = {}
        for pair, d, v in a["cells"]:
            bypair.setdefault(pair, []).append(v)
        r["c1_per_pair_mean"] = {k: float(np.mean(v)) for k, v in bypair.items()}
        loo = {}
        for pair in bypair:
            keep = [v for p2, d, v in a["cells"] if p2 != pair]
            loo[pair] = {"mean": float(np.mean(keep)),
                         "neg_frac": sum(1 for x in keep if x < 0) / len(keep),
                         "passes": bool(np.mean(keep) <= -1.0
                                        and sum(1 for x in keep if x < 0) / len(keep) >= 0.75)}
        r["c1_leave_one_pair_out"] = loo
        r["c1_thin_pairs_cells"] = {p2: {str(d): v for pp, d, v in a["cells"] if pp == p2}
                                    for p2 in THIN}
        r["c1_cells"] = [[p2, d, v] for p2, d, v in a["cells"]]

        # ---- TB-C2 and the DD-P3H-2 pooling family ------------------------------
        pp_deltas, f5all, f20all = {}, [], []
        for pair in analysis:
            p5, p20 = path(arm, pair, 5), path(arm, pair, 20)
            if not p5 or not p20:
                continue
            v5 = [F[m] for m in ims(p5)]
            v20 = [F[m] for m in ims(p20)]
            pp_deltas[pair] = med(v5) - med(v20)
            f5all += v5
            f20all += v20
        c2pp = med(list(pp_deltas.values()))
        c2pool = med(f5all) - med(f20all)
        rec(f"{arm}.c2_per_pair", c2pp, SC["results"][arm]["c2_per_pair"])
        rec(f"{arm}.c2_pooled", c2pool, SC["results"][arm]["c2_pooled"])
        rec(f"{arm}.c2_n_pairs", len(pp_deltas), SC["results"][arm]["c2_n_pairs"])
        r["c2"] = {
            "per_pair_median": c2pp, "n_pairs": len(pp_deltas),
            "pooled_median": c2pool,
            "per_pair_mean": float(np.mean(list(pp_deltas.values()))),
            "pooled_mean": float(np.mean(f5all)) - float(np.mean(f20all)),
            "per_pair_deltas": pp_deltas,
            "pairs_negative": sum(1 for v in pp_deltas.values() if v < 0),
            "pairs_ge_0p5": sum(1 for v in pp_deltas.values() if v >= 0.5),
        }

        # ---- TB-C4 ---------------------------------------------------------------
        def simval(u, v):
            lo, hi = int(offsets[u]), int(offsets[u + 1])
            row = nbrs[lo:hi]
            j = int(np.nonzero(row == v)[0][0])
            return float(scores[lo + j])
        hops = [simval(q[i], q[i + 1]) for pair in analysis for d in C1_DEPTHS
                if (q := path(arm, pair, d)) and len(q) >= 4
                for i in range(1, len(q) - 2)]
        rec(f"{arm}.c4_median_sim", med(hops), SC["results"][arm]["c4_median_sim"])
        r["c4"] = {"median": med(hops), "n_interior_hops": len(hops),
                   "frac_exactly_1": sum(1 for x in hops if x >= 1.0) / len(hops),
                   "mean": float(np.mean(hops))}

        # ---- TB-C5 ---------------------------------------------------------------
        per_cell, distinct, allints = [], set(), set()
        for pair in analysis:
            for d in C1_DEPTHS:
                q = path(arm, pair, d)
                if not q:
                    continue
                per_cell.append(sum(1 for x in q[1:-1] if pctl[x] < KNEE))
                distinct.update(x for x in q[1:-1] if pctl[x] < KNEE)
                allints.update(q[1:-1])
        rec(f"{arm}.c5_mean_per_cell", float(np.mean(per_cell)),
            SC["results"][arm]["c5_mean_per_cell"])
        rec(f"{arm}.c5_distinct", len(distinct), SC["results"][arm]["c5_distinct"])
        c5b = sum(1 for x in allints if degree[x] >= top_deg_cut)
        rec(f"{arm}.c5b_top_degree", c5b, SC["results"][arm]["c5b_top_degree_distinct"])
        r["c5"] = {"mean_per_cell": float(np.mean(per_cell)), "distinct": len(distinct),
                   "c5b_top_degree_distinct": c5b, "distinct_all_interiors": len(allints)}

        # ---- TB-C6, mean (scored) and cell-median variant -------------------------
        def ld(depths):
            return [(len(pa) - 2) - (len(pq) - 2) for pair in analysis for d in depths
                    if (pa := path(arm, pair, d)) and (pq := path("P", pair, d))]
        c1w, d5w = ld(C1_DEPTHS), ld((5,))
        rec(f"{arm}.c6_c1_window", float(np.mean(c1w)), SC["results"][arm]["c6_c1_window"])
        rec(f"{arm}.c6_d5", float(np.mean(d5w)), SC["results"][arm]["c6_d5"])
        r["c6"] = {"c1_window_mean": float(np.mean(c1w)), "d5_mean": float(np.mean(d5w)),
                   "c1_window_median": med(c1w), "d5_median": med(d5w),
                   "d5_deltas": d5w,
                   "flag_mean": bool(np.mean(c1w) < -1.0 or np.mean(d5w) < -1.0),
                   "flag_cell_median": bool(med(c1w) < -1.0 or med(d5w) < -1.0),
                   "d5_mean_exact_repr": repr(float(np.mean(d5w)))}

        # ---- A11 exposure, distinct and occurrence-weighted -----------------------
        occ = [m for pair in analysis for d in C1_DEPTHS if (q := path(arm, pair, d))
               for m in ims(q)]
        dist_m = set(occ)
        rec(f"{arm}.a11_scored_interiors", len(dist_m),
            SC["results"][arm]["a11"]["scored_interiors"])
        rec(f"{arm}.a11_unmatched", sum(1 for m in dist_m if not rows[m].get("matched")),
            SC["results"][arm]["a11"]["unmatched"])
        rec(f"{arm}.a11_flagged", sum(1 for m in dist_m if m in flagged),
            SC["results"][arm]["a11"]["flagged"])
        r["a11"] = {
            "distinct": len(dist_m),
            "distinct_unmatched": sum(1 for m in dist_m if not rows[m].get("matched")),
            "distinct_unmatched_pct": 100.0 * sum(1 for m in dist_m
                                                  if not rows[m].get("matched")) / len(dist_m),
            "occurrences": len(occ),
            "occ_unmatched": sum(1 for m in occ if not rows[m].get("matched")),
            "occ_unmatched_pct": 100.0 * sum(1 for m in occ
                                             if not rows[m].get("matched")) / len(occ),
            "occ_flagged": sum(1 for m in occ if m in flagged),
            "occ_F_zero_pct": 100.0 * sum(1 for m in occ if F[m] == 0.0) / len(occ),
        }
        per_arm[arm] = r

    # d0 / d1 identity, independently of the runner's own gate print
    d0_diff = {arm: [p for p in P["pairs"] if path(arm, p, 0) != path("P", p, 0)]
               for arm in arms if arm != "P"}
    d1_diff = {arm: [p for p in P["pairs"] if path(arm, p, 1) != path("P", p, 1)]
               for arm in arms if arm != "P"}
    out["checks"]["g2"] = {
        "d0_differing_pairs": {k: v for k, v in d0_diff.items()},
        "d1_differing_count": {k: len(v) for k, v in d1_diff.items()},
        "n_pairs": len(P["pairs"]),
        "d1_differing_scored_only": {
            k: sum(1 for p in v if splits[p] != "anchor") for k, v in d1_diff.items()},
    }

    out["per_arm"] = per_arm
    discs.sort(key=lambda t: -t[1])
    out["disc"] = {"max": discs[0], "top10": discs[:10],
                   "n_figures_compared": len(discs)}
    (HERE / "tb_p5_rescore.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                             encoding="utf-8")

    print(f"artifact {digest[:8]}  figures compared: {len(discs)}  "
          f"MAX |discrepancy| = {discs[0][1]:.3e} ({discs[0][0]})")
    print("top discrepancies:", [(a, f"{b:.2e}") for a, b in discs[:5]])
    print("\nfame join:", json.dumps(out["checks"]["fame_join"], indent=1))
    print("\nTB-G2 d0 differing pairs:", d0_diff)
    print("TB-G2 d1 differing (all 16 pairs):", out["checks"]["g2"]["d1_differing_count"],
          " scored-only:", out["checks"]["g2"]["d1_differing_scored_only"])
    print("\ncounterfactual:", json.dumps(out["checks"]["counterfactual"], indent=1))
    for arm in arms:
        r = per_arm[arm]
        print(f"\n=== {arm} ===")
        print(" C1 :", json.dumps(r["c1"]))
        print(" C2 :", json.dumps({k: v for k, v in r["c2"].items()
                                   if k != "per_pair_deltas"}))
        print("     per-pair deltas:", {k: round(v, 3)
                                        for k, v in r["c2"]["per_pair_deltas"].items()})
        print(" C4 :", json.dumps(r["c4"]))
        print(" C5 :", json.dumps(r["c5"]))
        print(" C6 :", json.dumps(r["c6"]))
        print(" A11:", json.dumps(r["a11"]))
        print(" C1 per-pair means:", {k: round(v, 3)
                                      for k, v in r["c1_per_pair_mean"].items()})
        print(" C1 leave-one-pair-out:", {k: (round(v["mean"], 3), v["passes"])
                                          for k, v in r["c1_leave_one_pair_out"].items()})
        print(" C1 thin-headroom cells:", {k: {d: round(x, 3) for d, x in v.items()}
                                           for k, v in r["c1_thin_pairs_cells"].items()})
    print(f"\nwrote {HERE / 'tb_p5_rescore.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
