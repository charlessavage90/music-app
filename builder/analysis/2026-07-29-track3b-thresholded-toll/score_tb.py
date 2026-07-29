"""Track 3b scorer: TB-C1..TB-C6 on the arm walks, per the prereg §6 as amended.

    TB-C1  primary    per cell: (median interior F of arm) - (median interior F of P),
                      Track 2's cell_median form (TB-P1 F12); mean over surviving
                      C1-window cells <= -1.0 log10, >= 75 % of cells negative.
                      Reported twice: all interiors AND matched-only (REQ-Q1(a)).
                      Robustness (i): A11-guard counterfactual (flagged interiors
                      reassigned to P's MATCHED-interior C1-window median, TB-P1 F13)
                      must still pass. (ii): matched-only miss while primary passes ->
                      fixed wording, printed verbatim.
    TB-C2  gradient   PRIMARY per-pair pooling (DD-P3H-2): per pair present at both
                      d5 and d20, delta = median F(d5) - median F(d20); statistic =
                      median over pairs >= 0.5. Pooled variant reported beside.
    TB-C3  gate       TB-G2 holds (checked in run_arms_tb.py; re-asserted here).
    TB-C4  tripwire   median per-hop similarity over INTERIOR hops (both ends
                      interiors, TB-P1 F14/DD-P3H-3) at d >= 10; drop > 0.10 flags.
    TB-C5  reported   (a) interiors below pctl 0.90 at d >= 10 + fame distribution;
                      (b) distinct top-1%-by-degree interiors (REQ-Q1's diagnostic).
    TB-C6  criterion  mean interior count vs P over BOTH windows (C1 window AND d5,
                      TB-P1 F7); a drop > 1.0 in either flags, and TB-R1 requires the
                      passing arm unflagged.

Scored on analysis pairs. Held-out: supplementary, gates nothing. Anchors: descriptive.

Run from `builder/`, after `run_arms_tb.py` and TB-P2b's fame fetch:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/score_tb.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
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
C1_THRESHOLD, C1_MIN_NEG_FRAC = -1.0, 0.75
C2_THRESHOLD = 0.5
C4_FLAG = 0.10
C5_PCTL = 0.90
C6_FLAG = 1.0

WORDING_II = ("the pass is carried substantially by artists with no English "
              "Wikipedia article")


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # TB-G3
    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    pctl = MirrorContext.build(store).pctl
    offsets, neighbours, scores = (np.asarray(store.offsets),
                                   np.asarray(store.neighbours),
                                   np.asarray(store.scores))
    degree = np.diff(offsets)
    top_degree_cut = float(np.percentile(degree, 99.0))

    paths = json.loads((HERE / "tb_paths.json").read_text(encoding="utf-8"))
    fame = json.loads((HERE / "tb_fame.json").read_text(encoding="utf-8"))
    assert paths["artifact_sha256"] == digest
    assert paths["tb_g2_pass"], "TB-C3/TB-G2 failed; the run is void"
    F, rows = fame["fame"], fame["rows"]
    mbids, names = paths["node_mbids"], paths["node_names"]
    arms, splits = paths["arms"], paths["splits"]
    flagged = set(fame["potentially_notable_unmatched"])

    def matched(mbid: str) -> bool:
        return bool(rows[mbid].get("matched"))

    scored_pairs = [p for p in paths["pairs"] if splits[p] in ("analysis", "held_out")]
    analysis = [p for p in scored_pairs if splits[p] == "analysis"]
    held_out = [p for p in scored_pairs if splits[p] == "held_out"]
    anchors = paths["unscored_anchor_pairs"]

    # TB-G4: no blank-named scored interior; the A11 flag is READ, not just carried.
    blank = sorted({mbids[str(n)] for arm in arms for p in scored_pairs
                    for d in paths["snapshots"]
                    for n in (paths["paths"][arm][p][str(d)] or [])[1:-1]
                    if not names[str(n)].strip()})
    assert not blank, f"TB-G4: blank-named scored interior(s): {blank}"

    def cell(arm: str, pair: str, d: int):
        return paths["paths"][arm][pair][str(d)]

    def int_mbids(path) -> list[str]:
        return [mbids[str(n)] for n in path[1:-1]]

    # TB-C1(i)'s constant: P's MATCHED-interior median over analysis C1-window cells.
    p_matched_pool = [F[m] for pair in analysis for d in C1_DEPTHS
                      if (p := cell("P", pair, d))
                      for m in int_mbids(p) if matched(m)]
    counterfactual_F = statistics.median(p_matched_pool)

    def sim(u: int, v: int) -> float:
        row = neighbours[offsets[u]:offsets[u + 1]]
        idx = int(np.nonzero(row == v)[0][0])
        return float(scores[offsets[u] + idx])

    def c1_block(arm: str, pairs_list: list[str], fval) -> dict:
        """Cell-median paired deltas under fame function `fval`(mbid) -> F or None."""
        deltas = []
        for pair in pairs_list:
            for d in C1_DEPTHS:
                pa, pp = cell(arm, pair, d), cell("P", pair, d)
                if not pa or not pp:
                    continue
                fa = [x for m in int_mbids(pa) if (x := fval(m)) is not None]
                fp = [x for m in int_mbids(pp) if (x := fval(m)) is not None]
                if not fa or not fp:
                    continue
                deltas.append(statistics.median(fa) - statistics.median(fp))
        if not deltas:
            return {"mean": None, "neg_frac": None, "n": 0, "pass": False}
        mean = statistics.mean(deltas)
        neg = sum(1 for x in deltas if x < 0) / len(deltas)
        return {"mean": mean, "neg_frac": neg, "n": len(deltas),
                "pass": bool(mean <= C1_THRESHOLD and neg >= C1_MIN_NEG_FRAC)}

    results: dict[str, dict] = {}
    for arm in arms:
        r: dict = {"arm": arm, "w": paths["ws"][arm]}

        # ---- TB-C1, three ways ----
        r["c1_all"] = c1_block(arm, analysis, lambda m: F[m])
        r["c1_matched"] = c1_block(arm, analysis, lambda m: F[m] if matched(m) else None)
        r["c1_counterfactual"] = c1_block(
            arm, analysis, lambda m: counterfactual_F if m in flagged else F[m])
        r["c1_pass"] = bool(r["c1_all"]["pass"] and r["c1_counterfactual"]["pass"])
        r["c1_wording_ii"] = bool(r["c1_all"]["pass"] and not r["c1_matched"]["pass"])

        # A11 exposure of this arm's scored interiors (TB-G4's read).
        ints = {m for pair in analysis for d in C1_DEPTHS
                if (p := cell(arm, pair, d)) for m in int_mbids(p)}
        r["a11"] = {"scored_interiors": len(ints),
                    "unmatched": sum(1 for m in ints if not matched(m)),
                    "flagged": sum(1 for m in ints if m in flagged)}

        # ---- TB-C2: per-pair primary + pooled variant ----
        per_pair = []
        for pair in analysis:
            p5, p20 = cell(arm, pair, 5), cell(arm, pair, 20)
            if not p5 or not p20:
                continue
            per_pair.append(statistics.median([F[m] for m in int_mbids(p5)])
                            - statistics.median([F[m] for m in int_mbids(p20)]))
        r["c2_per_pair"] = statistics.median(per_pair) if per_pair else None
        r["c2_n_pairs"] = len(per_pair)

        def pooled(d: int) -> list[float]:
            return [F[m] for pair in analysis if cell(arm, pair, d) and cell(arm, pair, 5)
                    and cell(arm, pair, 20) for m in int_mbids(cell(arm, pair, d))]
        f5, f20 = pooled(5), pooled(20)
        r["c2_pooled"] = (statistics.median(f5) - statistics.median(f20)) if f5 and f20 else None
        r["c2_pass"] = bool(r["c2_per_pair"] is not None
                            and r["c2_per_pair"] >= C2_THRESHOLD)

        # ---- TB-C4: interior hops only (both ends interiors) ----
        sims = [sim(p[i], p[i + 1])
                for pair in analysis for d in C1_DEPTHS
                if (p := cell(arm, pair, d)) and len(p) >= 4
                for i in range(1, len(p) - 2)]
        r["c4_median_sim"] = statistics.median(sims) if sims else None

        # ---- TB-C5(a): sub-pctl payload + fame distribution; (b): degree diagnostic --
        per_cell, distinct = [], set()
        for pair in analysis:
            for d in C1_DEPTHS:
                p = cell(arm, pair, d)
                if not p:
                    continue
                sub = [n for n in p[1:-1] if pctl[n] < C5_PCTL]
                per_cell.append(len(sub))
                distinct.update(sub)
        r["c5_mean_per_cell"] = statistics.mean(per_cell) if per_cell else None
        r["c5_distinct"] = len(distinct)
        fs = sorted(F[mbids[str(n)]] for n in distinct)
        r["c5_fame_quartiles"] = ([fs[0], fs[len(fs) // 4], fs[len(fs) // 2],
                                   fs[3 * len(fs) // 4], fs[-1]] if fs else None)
        all_ints = {n for pair in analysis for d in C1_DEPTHS
                    if (p := cell(arm, pair, d)) for n in p[1:-1]}
        r["c5b_top_degree_distinct"] = sum(1 for n in all_ints
                                           if degree[n] >= top_degree_cut)

        # ---- TB-C6: both windows ----
        def len_deltas(depths) -> list[float]:
            return [(len(pa) - 2) - (len(pp) - 2)
                    for pair in analysis for d in depths
                    if (pa := cell(arm, pair, d)) and (pp := cell("P", pair, d))]
        c1w, d5w = len_deltas(C1_DEPTHS), len_deltas((5,))
        r["c6_c1_window"] = statistics.mean(c1w) if c1w else None
        r["c6_d5"] = statistics.mean(d5w) if d5w else None
        r["c6_flagged"] = bool((c1w and r["c6_c1_window"] < -C6_FLAG)
                               or (d5w and r["c6_d5"] < -C6_FLAG))
        results[arm] = r

    p_sim = results["P"]["c4_median_sim"]
    for r in results.values():
        r["c4_drop_vs_p"] = p_sim - r["c4_median_sim"]
        r["c4_flagged"] = bool(r["c4_drop_vs_p"] > C4_FLAG)

    # ---- supplementary: held-out (gates nothing) and anchors (descriptive) ----
    supp: dict[str, dict] = {}
    for label, plist in (("held_out", held_out), ("anchors", anchors)):
        supp[label] = {}
        for arm in arms:
            blk = c1_block(arm, plist, lambda m: F[m])
            per_cell = [sum(1 for n in cell(arm, pair, d)[1:-1] if pctl[n] < C5_PCTL)
                        for pair in plist for d in C1_DEPTHS if cell(arm, pair, d)]
            lens = [(len(pa) - 2) - (len(pp) - 2)
                    for pair in plist for d in C1_DEPTHS
                    if (pa := cell(arm, pair, d)) and (pp := cell("P", pair, d))]
            supp[label][arm] = {
                "c1_mean": blk["mean"], "c1_neg_frac": blk["neg_frac"],
                "c5_mean_per_cell": statistics.mean(per_cell) if per_cell else None,
                "len_vs_p": statistics.mean(lens) if lens else None}

    # ---------------- report ----------------
    print(f"artifact {digest[:8]}...  TB-C3/TB-G2: PASS   "
          f"dropped cells: {len(paths['dropped_cells_d7'])}   "
          f"counterfactual F constant = {counterfactual_F:.3f} (P matched median)")
    print(f"scored on {len(analysis)} analysis pairs; {len(held_out)} held-out "
          f"supplementary; {len(anchors)} anchors descriptive\n")
    hdr = (f"{'arm':<7}{'w':>5}{'C1all':>8}{'neg%':>6}{'C1mat':>8}{'C1cf':>8}{'C1?':>5}"
           f"{'C2pp':>7}{'C2pl':>7}{'C2?':>5}{'C5':>6}{'C5b':>5}"
           f"{'C6c1w':>8}{'C6d5':>7}{'flag':>6}{'C4':>7}")
    print(hdr)
    for arm in arms:
        r = results[arm]
        print(f"{arm:<7}{r['w']:>5}"
              f"{r['c1_all']['mean']:>8.3f}{100 * r['c1_all']['neg_frac']:>5.0f}%"
              f"{r['c1_matched']['mean']:>8.3f}{r['c1_counterfactual']['mean']:>8.3f}"
              f"{'PASS' if r['c1_pass'] else '-':>5}"
              f"{r['c2_per_pair']:>7.3f}{r['c2_pooled']:>7.3f}"
              f"{'PASS' if r['c2_pass'] else '-':>5}"
              f"{r['c5_mean_per_cell']:>6.2f}{r['c5b_top_degree_distinct']:>5}"
              f"{r['c6_c1_window']:>+8.2f}{r['c6_d5']:>+7.2f}"
              f"{'LEN' if r['c6_flagged'] else ('SIM' if r['c4_flagged'] else ''):>6}"
              f"{r['c4_median_sim']:>7.3f}")
        if r["c1_wording_ii"]:
            print(f"       ^ TB-C1(ii): {WORDING_II}")

    print("\nvictim-rule counter (TB-P1 F4): sub-decile victims / total, by arm:")
    for arm in arms:
        vs = paths["victim_stats"][arm]
        print(f"  {arm:<7}{vs['sub_decile_victims']:>4}/{vs['victims_total']}")

    print("\nplain-language key, fixed at definition time:")
    print("  TB-C1  after ten or more presses, is the typical middle artist about one")
    print("         full step less known than today's app gives you (all / matched-only")
    print("         / counterfactual; pass needs 'all' AND the counterfactual)")
    print("  TB-C2  does the journey keep getting more obscure as you keep pressing")
    print("         (per-pair primary; pooled variant beside)")
    print("  TB-C5  how many genuinely less-popular artists appeared on screen; C5b:")
    print("         how many are the same well-connected stepping stones (degree)")
    print("  TB-C6  does the journey still have about as many artists in it, at depth")
    print("         AND at five presses  [LEN = flagged; TB-C1 is not descent]")
    print("  TB-C4  do consecutive middle artists still sound like neighbours (warning)")

    (HERE / "tb_scores.json").write_text(
        json.dumps({"artifact_sha256": digest,
                    "thresholds": {"c1": C1_THRESHOLD, "c1_neg_frac": C1_MIN_NEG_FRAC,
                                   "c2": C2_THRESHOLD, "c4_flag": C4_FLAG,
                                   "c5_pctl": C5_PCTL, "c6_flag": C6_FLAG,
                                   "counterfactual_F": counterfactual_F,
                                   "top_degree_cut": top_degree_cut},
                    "wording_ii": WORDING_II,
                    "n_analysis_pairs": len(analysis),
                    "results": results,
                    "supplementary": supp}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print(f"\nwrote {HERE / 'tb_scores.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
