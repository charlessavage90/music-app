"""TB-P5 probe 3 — auxiliary checks the two main probes do not cover.

  * the A11 flag list vs each row's own `guard.potentially_notable` (is the list the
    scorer reads derivable from the table, or is it a parallel assertion?),
  * degree top-1 % set sizing behind TB-C5(b)'s `top_degree_cut`,
  * a strong-form TB-C1 counterfactual (reclassify EVERY unmatched interior, not only
    the flagged ones) as the sensitivity TB-C1(i) does not run,
  * TB-C2 threshold margins and the pass set under each pooling in the DD-P3H-2 family,
  * the TB-P3 ceiling's cell set vs the arms' scored cell set,
  * the exact-1.0 saturation behind P's TB-C4 baseline.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/tb_p5_probe_aux.py
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

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
C1_DEPTHS = (10, 15, 20)


def med(xs):
    return float(np.median(np.asarray(xs, dtype=np.float64)))


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # TB-G3
    from artistpath_api.graph_store import GraphStore

    store = GraphStore.load(GRAPH)
    offsets = np.asarray(store.offsets, dtype=np.int64)
    degree = np.diff(offsets)
    n = degree.size

    P = json.loads((HERE / "tb_paths.json").read_text(encoding="utf-8"))
    FA = json.loads((HERE / "tb_fame.json").read_text(encoding="utf-8"))
    SC = json.loads((HERE / "tb_scores.json").read_text(encoding="utf-8"))
    G = json.loads((HERE / "tb_p3_gate.json").read_text(encoding="utf-8"))
    F, rows = FA["fame"], FA["rows"]
    flagged = set(FA["potentially_notable_unmatched"])
    mbids = P["node_mbids"]
    splits = P["splits"]
    analysis = [p for p in P["pairs"] if splits[p] == "analysis"]

    out: dict = {"artifact_sha256": digest}

    # --- 1. flag list vs per-row guard -------------------------------------------
    derived, no_guard = set(), []
    for m, r in rows.items():
        g = r.get("guard")
        if g is None:
            if not r.get("matched"):
                no_guard.append(m)
            continue
        if g.get("potentially_notable"):
            derived.add(m)
    out["flag_list"] = {
        "list_len": len(flagged), "derived_from_rows": len(derived),
        "identical": sorted(flagged) == sorted(derived),
        "unmatched_rows_without_guard": len(no_guard),
        "unmatched_total": FA["unmatched"],
        "flag_share_of_unmatched": len(flagged) / FA["unmatched"],
    }

    # --- 2. degree top-1 % sizing -------------------------------------------------
    cut = float(np.percentile(degree, 99.0))
    out["degree"] = {
        "N": int(n), "p99_cut": cut,
        "committed_cut": SC["thresholds"]["top_degree_cut"],
        "nodes_ge_cut": int((degree >= cut).sum()),
        "share_ge_cut_pct": 100.0 * float((degree >= cut).mean()),
        "max_degree": int(degree.max()), "median_degree": float(np.median(degree)),
    }

    def path(arm, pair, d):
        return P["paths"][arm][pair][str(d)]

    def ims(p):
        return [mbids[str(x)] for x in p[1:-1]]

    # --- 3. strong-form counterfactual -------------------------------------------
    pool = [F[m] for p in analysis for d in C1_DEPTHS if (q := path("P", p, d))
            for m in ims(q) if rows[m].get("matched")]
    cf = med(pool)

    def c1_mean(arm, fv):
        cells = []
        for pair in analysis:
            for d in C1_DEPTHS:
                pa, pp = path(arm, pair, d), path("P", pair, d)
                if not pa or not pp:
                    continue
                fa = [y for m in ims(pa) if (y := fv(m)) is not None]
                fp = [y for m in ims(pp) if (y := fv(m)) is not None]
                if fa and fp:
                    cells.append(med(fa) - med(fp))
        return (float(np.mean(cells)),
                sum(1 for x in cells if x < 0) / len(cells), len(cells))

    strong = {}
    for arm in P["arms"]:
        prim = c1_mean(arm, lambda m: F[m])
        weak = c1_mean(arm, lambda m: cf if m in flagged else F[m])
        allun = c1_mean(arm, lambda m: cf if not rows[m].get("matched") else F[m])
        matched_only = c1_mean(arm, lambda m: F[m] if rows[m].get("matched") else None)
        strong[arm] = {
            "primary": prim[0], "cf_flagged_only": weak[0],
            "cf_all_unmatched": allun[0], "matched_only": matched_only[0],
            "cf_flagged_shift": weak[0] - prim[0],
            "cf_all_unmatched_shift": allun[0] - prim[0],
            "primary_margin_vs_-1.0": prim[0] - (-1.0),
            "cf_margin_vs_-1.0": weak[0] - (-1.0),
            "cf_all_unmatched_passes": bool(allun[0] <= -1.0 and allun[1] >= 0.75),
        }
    out["c1_counterfactual_family"] = strong

    # --- 4. TB-C2 pooling family + margins ---------------------------------------
    fam = {}
    for arm in P["arms"]:
        pp, f5, f20 = {}, [], []
        for pair in analysis:
            p5, p20 = path(arm, pair, 5), path(arm, pair, 20)
            if not p5 or not p20:
                continue
            v5, v20 = [F[m] for m in ims(p5)], [F[m] for m in ims(p20)]
            pp[pair] = med(v5) - med(v20)
            f5 += v5
            f20 += v20
        vals = sorted(pp.values())
        fam[arm] = {
            "per_pair_median_PRIMARY": med(vals),
            "per_pair_mean": float(np.mean(vals)),
            "pooled_median": med(f5) - med(f20),
            "pooled_mean": float(np.mean(f5)) - float(np.mean(f20)),
            "sorted_per_pair": vals,
            "median_is_avg_of": [vals[3], vals[4]],
            "margin_vs_0.5": med(vals) - 0.5,
            "range_across_poolings": [
                min(med(vals), float(np.mean(vals)), med(f5) - med(f20),
                    float(np.mean(f5)) - float(np.mean(f20))),
                max(med(vals), float(np.mean(vals)), med(f5) - med(f20),
                    float(np.mean(f5)) - float(np.mean(f20)))],
        }
        fam[arm]["passes_under"] = [
            k for k in ("per_pair_median_PRIMARY", "per_pair_mean", "pooled_median",
                        "pooled_mean") if fam[arm][k] >= 0.5]
    out["c2_pooling_family"] = fam

    # --- 5. ceiling cell set vs arms' cell set -----------------------------------
    ceil_cells = {(c["pair"], c["depth"]) for c in G["cells"]}
    arm_cells = {(p, d) for p in analysis for d in C1_DEPTHS if path("P", p, d)}
    out["cell_sets"] = {
        "ceiling_n": len(ceil_cells), "arms_scored_n": len(arm_cells),
        "in_arms_not_in_ceiling": sorted(f"{p}@d{d}" for p, d in arm_cells - ceil_cells),
        "in_ceiling_not_in_arms": sorted(f"{p}@d{d}" for p, d in ceil_cells - arm_cells),
        "arms_dropped_cells": P["dropped_cells_d7"],
        "ceiling_cells_clearing_-1.0_mean_form":
            sum(1 for c in G["cells"] if c["d_mean_F"] <= -1.0),
        "ceiling_cells_clearing_-1.0_median_form":
            sum(1 for c in G["cells"] if c["d_median_F"] <= -1.0),
        "gate_stat_form": "cell MEAN gap; TB-C1's form is the cell MEDIAN gap",
        "gate_mean_form": G["gate_statistic_mean_of_cell_mean_gap"],
        "gate_median_form": G["variant_mean_of_cell_median_gap"],
        "thin_pair_ceiling_cells": {
            f"{c['pair']}@d{c['depth']}": [c["d_mean_F"], c["d_median_F"]]
            for c in G["cells"]
            if c["pair"] in ("Patti Smith -> Daniel Herskedal",
                            "Openzone Bar -> Gjallarhorn")},
    }

    (HERE / "tb_p5_aux.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
