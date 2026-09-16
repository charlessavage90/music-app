"""The section 7 reads this stage's run state licenses, evaluated CLAUSE BY CLAUSE.

THE RUN STATE REACHED IS `complete` AND `sized`, AND NOT `censused`.

  * `complete` -- every cell either built or stopped by `LBA-G2` with its bar recorded (stage 2
    section 7). The lattice was NOT reduced by judgement, which section 7 says would have put
    `complete` out of reach and barred these reads.
  * `sized` -- `LBA-M1`'s boot and query-cost halves were taken on the eight sized arms (stage 2
    section 3b).
  * NOT `censused` -- `LBA-G3` fired at stage 1, so the offline census pass was never started and
    none is owed. `LBA-AM3-1` records the consequence: `LBA-R8` and `LBA-R9` presuppose
    *censused* and are FORMALLY UNREACHABLE within `LBD-S4` as designed.

WHAT MAY THEREFORE BE READ (`LBA-AM3-1`, verbatim): `LBA-R4` on the `P` row and, with `LBA-X6`
beside it, the `U` row; `LBA-R5`; `LBA-R6`; `LBA-R7`. `LBA-R4-V` is restated as ALREADY SETTLED
ON THE COMMITTED RECORD and is never reported as a finding of this design. `LBA-R0` and `LBA-R1`
were taken at stage 2 and are not re-read here.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH. Each read is a CONJUNCTION of clauses, and the failure
mode this project has recorded is a read taken on the clause a session remembered rather than on
all of them. So every clause is evaluated mechanically from the committed JSONs, each with the
figure that decided it, and the verdict is the AND -- never a judgement made while looking at one
number.

NO READ HERE SELECTS AN ARM OR PREFERS A THRESHOLD. `LBA-D2` reserves that to the owner at the
go/no-go stop.

    python -u s3_reads.py
"""

from __future__ import annotations

import json
from pathlib import Path

import s3_common as C

HERE = Path(__file__).resolve().parent

# `LBD-G2`'s bar, carried by `LBA-M3`. One percentage point WITH both controls reported.
LBD_G2_PP = 1.0
# `LBA-R4`'s own absent-share clause: "the absent shares lie within a point of each other".
R4_ABSENT_PP = 1.0


def main() -> None:
    m2 = json.loads((HERE / "s3_m2_served.json").read_text("utf-8"))
    m2a = json.loads((HERE / "s3_m2_armtoarm.json").read_text("utf-8"))
    m3 = json.loads((HERE / "s3_m3.json").read_text("utf-8"))

    absent_share = {a["arm"]: a["absent"]["absent_share_of_V"] for a in m2["arms"]}
    changed_share = {a["arm"]: a["overall"]["changed_share_of_common"] for a in m2["arms"]}
    m3_added = {k: v["added"]["share_le_2_or_absent"] for k, v in m3["arms"].items()}

    out = {
        "run_state": {
            "complete": True, "sized": True, "censused": False,
            "complete_basis": "stage 2 section 7 -- every cell built or stopped by LBA-G2 with "
                              "its bar recorded; the lattice was not reduced by judgement",
            "sized_basis": "stage 2 section 3b -- LBA-M1's boot and query-cost halves, eight arms",
            "censused_basis": "LBA-G3 fired at stage 1; no pass was started and none is owed",
        },
        "reads": {},
    }

    def r4(row: str, arms: list, baseline: str) -> dict:
        """`LBA-R4`: the three thresholds DO NOT separate. A conjunction of three clauses."""
        deltas = {a: round(100 * (m3_added[a] - m3_added[baseline]), 4)
                  for a in arms if a != baseline}
        c1 = all(abs(d) < LBD_G2_PP for d in deltas.values())
        shares = [absent_share[a] for a in arms]
        spread_pp = round(100 * (max(shares) - min(shares)), 4)
        c2 = spread_pp < R4_ABSENT_PP
        # Clause 3 is stage 2's: LBA-G1 fired on NOTHING across all eight sized arms, so it
        # cannot fire differently across any subset of them. Cited, not recomputed.
        c3 = True
        return {
            "read": "LBA-R4 -- the three thresholds DO NOT separate",
            "row": row,
            "clause_1_no_LBD_G2_movement_on_LBA_M3": {
                "holds": c1, "bar_pp": LBD_G2_PP, "deltas_pp_vs_baseline": deltas,
                "baseline": baseline},
            "clause_2_absent_shares_within_a_point": {
                "holds": c2, "bar_pp": R4_ABSENT_PP, "spread_pp": spread_pp,
                "absent_share_of_V": {a: absent_share[a] for a in arms}},
            "clause_3_LBA_G1_does_not_fire_differently": {
                "holds": c3,
                "basis": "stage 2 section 4 -- LBA-G1 fires on NOTHING across the eight sized "
                         "arms, so it cannot fire differently across this row. Cited."},
            "verdict": "READS" if (c1 and c2 and c3) else "DOES NOT READ",
            "why": ("all three clauses hold" if (c1 and c2 and c3) else
                    "a read is a conjunction: "
                    + ", ".join(n for n, h in
                                [("clause 1 (LBA-M3 movement) fails", not c1),
                                 ("clause 2 (absent shares) fails", not c2),
                                 ("clause 3 (LBA-G1) fails", not c3)] if h)),
        }

    out["reads"]["LBA-R4 (P row)"] = r4("P", ["LBA-A4", "LBA-A5", "LBA-A6"], "LBA-A4")
    u = r4("U", ["LBA-A7", "LBA-A8"], "LBA-A7")
    u["LBA-X6"] = ("the U population is a DEPENDENT variable that moves with the threshold, so "
                   "this is not a one-column comparison in the sense the V and P rows are. The "
                   "clause arithmetic is reported; the attribution is not.")
    out["reads"]["LBA-R4 (U row, LBA-X6 beside it)"] = u

    out["reads"]["LBA-R4-V"] = {
        "read": "LBA-R4-V -- the V row is EXCLUDED from LBA-R4 and its outcome was stated in the "
                "pre-registration itself, before stage 1",
        "status": "RESTATED, NEVER REPORTED AS A FINDING OF THIS DESIGN",
        "clause_i_LBA_M3": {
            "unfireable": True,
            "measured_here": {a: m3_added[a] for a in ("LBA-A1", "LBA-A2", "LBA-A3")},
            "note": "1.0 on all three, computed rather than asserted. Every threshold difference "
                    "on this row is identically zero, so the null carries no information (the "
                    "CRS-C3 shape)."},
        "clause_ii_absent_share": {
            "already_resolved_against_the_read": True,
            "spread_pp": round(100 * (max(absent_share[a] for a in ("LBA-A1", "LBA-A3"))
                                      - min(absent_share[a] for a in ("LBA-A1", "LBA-A3"))), 4),
            "note": "LBA-R4-V states this was larger than one point on the committed record "
                    "BEFORE stage 1 ran. This session's independent measurement agrees, which is "
                    "a check on the instrument and NOT a finding."},
        "clause_iii_LBA_M1": "the only live clause, and section 4 records that LBA-M1 measures "
                             "the threshold with far less dynamic range than the population "
                             "(LBA-AM1-O1)",
        "consequence": "no LBA-R4-shaped conclusion may be drawn about the V row. The V row's "
                       "threshold evidence is the arm-to-arm LBA-M2 comparison and nothing else.",
        "V_row_arm_to_arm_LBA_M2": {
            c["base"] + " -> " + c["arm"]: {"R_mean": c["overall"]["R_mean"],
                                            "changed_share": c["overall"][
                                                "changed_share_of_common"],
                                            "overlap_at_10_mean": c["overall"][
                                                "overlap_at_10_mean"]}
            for c in m2a["comparisons"] if c["population_rule"] == "V"},
    }

    # `LBA-R5` is `LBA-R4`'s complement within a population rule.
    for row, arms, baseline in [("P", ["LBA-A4", "LBA-A5", "LBA-A6"], "LBA-A4"),
                                ("U", ["LBA-A7", "LBA-A8"], "LBA-A7")]:
        base = out["reads"][f"LBA-R4 ({row} row)" if row == "P"
                            else "LBA-R4 (U row, LBA-X6 beside it)"]
        out["reads"][f"LBA-R5 ({row} row)"] = {
            "read": "LBA-R5 -- within a population rule, the thresholds DO separate",
            "row": row,
            "verdict": "READS" if base["verdict"] == "DOES NOT READ" else "DOES NOT READ",
            "why": "LBA-R5 is LBA-R4's complement: " + base["why"],
            "cells_side_by_side": {a: {"sentence": C.SENTENCE[a],
                                       "LBA-M3 added share <=2 or absent": m3_added[a],
                                       "LBA-M2 absent share of V": absent_share[a],
                                       "LBA-M2 changed share of common": changed_share[a]}
                                   for a in arms},
            "names_no_preferred_value": "LBA-D2 reserves the threshold to the owner at the stop",
            "LBA-X6": ("travels with this row: the population moves with the threshold"
                       if row == "U" else None),
        }

    # `LBA-R6` / `LBA-R7` -- the population contrast. Both halves are reported; see the note.
    pairs = [("threshold 10", "LBA-A4", "LBA-A7"), ("threshold 7", "LBA-A5", "LBA-A8")]
    out["reads"]["LBA-R6 / LBA-R7 (the P-versus-U contrast)"] = {
        "read": "LBA-R6 -- the population rules separate on LBA-M3 but NOT on LBA-M2's "
                "materially-changed share; LBA-R7 -- they separate on BOTH",
        "scope": "the P-versus-U contrast and never about V -- over V the added-set figure is "
                 "1.0 by construction (LBA-R6's own text)",
        "NOT_one_column": "P -> U changes the population AND the drop filter's STATE, from "
                          "inert-because-applicable to absent-because-REFUSED (section 2.1's "
                          "drop-filter column). No read may call this a population effect "
                          "without naming the filter state beside it.",
        "LBA-M3_half": {
            label: {"P_arm": p, "U_arm": u_,
                    "added_share_le_2_or_absent": {p: m3_added[p], u_: m3_added[u_]},
                    "delta_pp_U_minus_P": round(100 * (m3_added[u_] - m3_added[p]), 4)}
            for label, p, u_ in pairs},
        "LBA-M3_half_bar": "LBD-G2 applies WITHIN a population rule and NEVER across one "
                           "(LBA-M3's own rule), so this contrast is DESCRIPTIVE and carries no "
                           "bar. The magnitudes are reported; no attribution is made.",
        "LBA-M2_half": {
            label: {"changed_share_of_common": {p: changed_share[p], u_: changed_share[u_]},
                    "delta_pp_U_minus_P": round(100 * (changed_share[u_] - changed_share[p]), 4),
                    "absent_share_of_V": {p: absent_share[p], u_: absent_share[u_]}}
            for label, p, u_ in pairs},
        "LBA-M2_half_bar": "NONE. Section 4 fixes LBA-M2 as reported descriptively, no "
                           "threshold, because what counts as too much change is the owner's "
                           "product judgment.",
        "verdict": "NOT ADJUDICABLE BY THIS DESIGN -- see why",
        "why": ("LBA-R6 and LBA-R7 differ ONLY in whether the population rules separate on "
                "LBA-M2's materially-changed share, and NEITHER the read nor LBA-M2 carries an "
                "effect size for that half. Section 4 fixes LBA-M2 as descriptive BY DESIGN and "
                "bars a session from attaching a bar to it. So the branch between these two "
                "reads cannot be decided by any number this document fixed, and a session "
                "choosing one WOULD BE FIXING A THRESHOLD WITH RESULTS IN HAND -- which is the "
                "one thing a pre-registration exists to prevent. Both halves' figures are "
                "reported side by side and the branch is left to the owner, whose judgment it "
                "is under CLAUDE.md's decision table."),
        "LBA-X4_LBA-X5": "travel with every LBA-M2 figure taken against the served map, which is "
                         "both columns of the LBA-M2 half here",
    }

    out["reads"]["LBA-R8 and LBA-R9"] = {
        "status": "FORMALLY UNREACHABLE (LBA-AM3-1)",
        "why": "both presuppose the *censused* run state. Section 7 defines *censused* as the "
               "offline census pass HAVING RUN with the class share MEASURED rather than "
               "estimated. LBA-G3 fired at stage 1, so no pass is started and none is owed, and "
               "no arm will ever reach *censused* within LBD-S4 as designed. Section 7's closing "
               "rule is firm: nothing in the table is reachable before its run state, and a "
               "partial run licenses no read.",
        "what_this_costs": "LBA-R9 is the row that reads 'the numbers say no' and that records "
                           "STOPPING THE LBD- TRACK HERE AS A COMPLETE OUTCOME rather than an "
                           "abandonment. It is the owner's own exit read, and the design as "
                           "executed cannot hand it to him licensed.",
    }

    C.write_json(HERE / "s3_reads.json", out, __file__)
    for name, r in out["reads"].items():
        v = r.get("verdict") or r.get("status")
        print(f"[reads] {name:46} {v}")
        if "why" in r and r.get("verdict") != "READS":
            print(f"         {r['why'][:150]}")


if __name__ == "__main__":
    main()
