"""Track 3 scorer: DD-C1..DD-C6 on the arm walks.

Criteria and thresholds are fixed by the pre-registration §5 (and DD-C6 by the
execution log §3, adopted before any arm ran). Nothing here chooses a threshold.

    DD-C1  primary    paired mean dF vs P over cells at d in {10,15,20} <= -1.0 log10,
                      with >= 75 % of cells negative
    DD-C2  gradient   median interior F drop d5 -> d20 >= 0.5 log10
    DD-C3  gate       DD-G2 holds (checked in run_arms_t3.py; re-asserted here)
    DD-C4  tripwire   median per-hop similarity at d >= 10 vs P; a drop > 0.10 flags
    DD-C5  reported   interior artists below pctl 0.90 at d >= 10
    DD-C6  control    mean interior count vs P; a drop > 1.0 flags, and DD-C1 may not
                      be read as descent for a flagged arm

**Scored on analysis pairs only.** Held-out is reported separately and gates nothing;
the four all-famous anchors are excluded entirely (they cannot pass DD-P1).

Run from `api/`, after `run_arms_t3.py` and `fame.py`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/score_t3.py
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


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # DD-G3
    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext

    store = GraphStore.load(GRAPH)
    pctl = MirrorContext.build(store).pctl
    offsets, neighbours, scores = (np.asarray(store.offsets),
                                   np.asarray(store.neighbours),
                                   np.asarray(store.scores))

    paths = json.loads((HERE / "t3_paths.json").read_text(encoding="utf-8"))
    fame = json.loads((HERE / "t3_fame.json").read_text(encoding="utf-8"))
    assert paths["artifact_sha256"] == digest
    assert paths["dd_g2_pass"], "DD-C3/DD-G2 failed; §3 says the run is void"
    F, mbids, names = fame["fame"], paths["node_mbids"], paths["node_names"]
    arms, splits = paths["arms"], paths["splits"]

    def sim(u: int, v: int) -> float:
        row = neighbours[offsets[u]:offsets[u + 1]]
        idx = int(np.nonzero(row == v)[0][0])
        return float(scores[offsets[u] + idx])

    scored_pairs = [p for p in paths["pairs"] if splits[p] in ("analysis", "held_out")]
    analysis = [p for p in scored_pairs if splits[p] == "analysis"]

    # DD-G4's outstanding half, on the scored set.
    blank = sorted({mbids[str(n)] for arm in arms for p in scored_pairs
                    for d in paths["snapshots"]
                    for n in (paths["paths"][arm][p][str(d)] or [])[1:-1]
                    if not names[str(n)].strip()})
    assert not blank, f"DD-G4: blank-named scored interior(s): {blank}"

    def cell(arm: str, pair: str, d: int):
        return paths["paths"][arm][pair][str(d)]

    def interiors_F(path) -> list[float]:
        return [F[mbids[str(n)]] for n in path[1:-1]]

    results: dict[str, dict] = {}
    for arm in arms:
        r: dict = {"arm": arm, "ramp": paths["ramps"][arm]}

        # ---- DD-C1 + DD-C6, paired cell-wise against P on analysis pairs ----
        deltas, dlens = [], []
        for pair in analysis:
            for d in C1_DEPTHS:
                pa, pp = cell(arm, pair, d), cell("P", pair, d)
                if not pa or not pp:
                    continue
                deltas.append(statistics.mean(interiors_F(pa))
                              - statistics.mean(interiors_F(pp)))
                dlens.append((len(pa) - 2) - (len(pp) - 2))
        r["c1_mean"] = statistics.mean(deltas) if deltas else None
        r["c1_neg_frac"] = (sum(1 for x in deltas if x < 0) / len(deltas)) if deltas else None
        r["c1_n"] = len(deltas)
        r["c1_pass"] = bool(deltas and r["c1_mean"] <= C1_THRESHOLD
                            and r["c1_neg_frac"] >= C1_MIN_NEG_FRAC)
        r["c6_mean_len_delta"] = statistics.mean(dlens) if dlens else None
        r["c6_flagged"] = bool(dlens and r["c6_mean_len_delta"] < -C6_FLAG)

        # ---- DD-C2: pooled median interior F, d5 -> d20 ----
        def pooled_F(d: int) -> list[float]:
            return [f for pair in analysis if cell(arm, pair, d)
                    for f in interiors_F(cell(arm, pair, d))]
        f5, f20 = pooled_F(5), pooled_F(20)
        r["c2_median_d5"] = statistics.median(f5) if f5 else None
        r["c2_median_d20"] = statistics.median(f20) if f20 else None
        r["c2_drop"] = (r["c2_median_d5"] - r["c2_median_d20"]) if f5 and f20 else None
        r["c2_pass"] = bool(r["c2_drop"] is not None and r["c2_drop"] >= C2_THRESHOLD)

        # ---- DD-C4: median per-hop similarity at d >= 10 (every hop on the path) ----
        sims = [sim(p[i], p[i + 1])
                for pair in analysis for d in C1_DEPTHS
                if (p := cell(arm, pair, d)) for i in range(len(p) - 1)]
        r["c4_median_sim"] = statistics.median(sims) if sims else None

        # ---- DD-C5: obscure artists actually delivered, d >= 10 ----
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
        results[arm] = r

    p_sim = results["P"]["c4_median_sim"]
    for r in results.values():
        r["c4_drop_vs_p"] = p_sim - r["c4_median_sim"]
        r["c4_flagged"] = bool(r["c4_drop_vs_p"] > C4_FLAG)

    # ---------------- report ----------------
    print(f"artifact {digest[:8]}...  DD-C3/DD-G2: PASS   "
          f"dropped cells: {len(paths['dropped_cells_d7'])}")
    print(f"scored on {len(analysis)} analysis pairs; "
          f"{len(paths['unscored_anchor_pairs'])} anchors excluded\n")
    print(f"{'arm':<7}{'w':>6}{'DD-C1':>9}{'neg%':>7}{'C1?':>5}"
          f"{'DD-C2':>8}{'C2?':>5}{'DD-C5':>8}{'DD-C6':>8}{'flag':>6}{'DD-C4':>8}")
    for arm in arms:
        r = results[arm]
        print(f"{arm:<7}{r['ramp']:>6}"
              f"{r['c1_mean']:>9.3f}{100 * r['c1_neg_frac']:>6.0f}%"
              f"{'PASS' if r['c1_pass'] else '-':>5}"
              f"{r['c2_drop']:>8.3f}{'PASS' if r['c2_pass'] else '-':>5}"
              f"{r['c5_mean_per_cell']:>8.2f}"
              f"{r['c6_mean_len_delta']:>+8.2f}{'LEN' if r['c6_flagged'] else '':>6}"
              f"{r['c4_median_sim']:>8.3f}")

    print("\nplain-language key, fixed at definition time:")
    print("  DD-C1  after ten or more presses, is the typical middle artist about one")
    print("         full step less known than today's app gives you")
    print("  DD-C2  does the journey measurably get more obscure as you keep pressing")
    print("  DD-C5  how many genuinely less-popular artists actually appeared on screen")
    print("  DD-C6  does the journey still have about as many artists in it, or did the")
    print("         app just make it shorter  [LEN = flagged; DD-C1 is not descent]")
    print("  DD-C4  do consecutive artists still sound like neighbours (warning only)")

    (HERE / "t3_scores.json").write_text(
        json.dumps({"artifact_sha256": digest,
                    "thresholds": {"c1": C1_THRESHOLD, "c1_neg_frac": C1_MIN_NEG_FRAC,
                                   "c2": C2_THRESHOLD, "c4_flag": C4_FLAG,
                                   "c5_pctl": C5_PCTL, "c6_flag": C6_FLAG},
                    "n_analysis_pairs": len(analysis),
                    "results": results}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print(f"\nwrote {HERE / 't3_scores.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
