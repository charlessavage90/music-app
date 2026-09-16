"""AN EXPLICITLY UNLICENSED SENSITIVITY -- NOT A READ, NOT A FINDING, NOT IN THE RECORD.

WHAT THIS IS AND WHY IT EXISTS. `LBA-R8` and `LBA-R9` presuppose the *censused* run state and are
FORMALLY UNREACHABLE (`LBA-AM3-1`). The owner, with that unreachability already stated to him,
instructed on 2026-09-15:

    State that LBA-R8 and LBA-R9 presuppose censused and are formally unreachable, and give
    beside that statement what the estimated LBA-M4 would say if it were read as measured,
    labelled so the owner can weigh it.

`LBA-AM3-1` records that instruction as HIS, quoted and dated, and records what it does not do:
IT MAKES NEITHER READ REACHABLE, licenses no section 7 row, and enters the record as no finding.
The distinction between *the owner asked for a sensitivity he can weigh* and *a session took a
barred read* is invisible in the output and survives only in the record -- which is the whole
reason this is a separate, differently named artifact rather than a section of the results.

THREE THINGS THE READER MUST CARRY WITH EVERY NUMBER BELOW.

  1. `LBA-AM3-2`'s DISQUALIFIER FIRED on every arm where `LBA-G4` is evaluable, at a measured
     provenance skew of 51.7 to 71.3 percentage points against a 10-point bar. The within-arm
     comparison below is DISQUALIFIED. That does not make the figure wrong; it makes it
     unattributable, because a dump column has re-entered a comparison `LBA-AM1-A5` had made one
     column wide.
  2. `LBA-X2`'s TWO BOUNDS. (a) Every class figure is an OVER-estimate of what the app cannot
     play, by `ULC-F4`'s mechanism -- the keep-check uses the name-search route while the app
     resolves identity first. On `U` that over-drop is UNBOUNDED, because nobody has measured it
     there. (b) The carried verdicts are un-re-run: both payloads carry verdicts inherited from
     the earlier no-release and featured-credit rules, holding no clip record. Unmeasured, not
     zero.
  3. `LBA-AM3-3`'s COVERAGE SPLIT. On the `U` row the added-beyond-`V` subset's class share is
     measured on a MINORITY of that subset and extrapolated to the rest, where the store's own
     rule is "absence of a field means UNKNOWN, never false."

    python -u s3_unlicensed_sensitivity.py
"""

from __future__ import annotations

import json
from pathlib import Path

import s3_common as C

HERE = Path(__file__).resolve().parent
G4_BAR_PP = 10.0


def main() -> None:
    m4 = json.loads((HERE / "s3_m4.json").read_text("utf-8"))
    m3 = json.loads((HERE / "s3_m3.json").read_text("utf-8"))
    lo, hi = m4["within_class_drop_rate"]["range_never_averaged"]

    arms = {}
    for arm, r in m4["arms"].items():
        g4 = r["LBA-G4"]
        if "delta_pp" not in g4:
            arms[arm] = {"if_read_as_measured": "n/a -- the gate's subject is empty on a V arm"}
            continue
        a = r["added_beyond_V"]
        s4 = m3["arms"][arm]["stratum4_nodes_minus_V_descriptive"]
        cls = a["class_share_of_covered"]
        arms[arm] = {
            "population_rule": r["population_rule"],
            "sentence": r["sentence"],
            "IF_READ_AS_MEASURED_LBA_G4": (
                "would FIRE" if g4["delta_pp"] >= G4_BAR_PP else "would not fire"),
            "delta_pp": g4["delta_pp"],
            "bar_pp": G4_BAR_PP,
            "BUT_IT_IS_DISQUALIFIED": g4["result"],
            "provenance_skew_pp": g4["provenance_skew_pp"],
            "added_beyond_V": {
                "n": a["n"], "covered": a["covered"], "coverage_share": a["coverage_share"],
                "class_share_of_covered": cls,
                "estimated_drop_share_range": [round(cls * lo, 6), round(cls * hi, 6)],
            },
            "LBA_M3_reported_twice_as_LBA_R8_would_require": {
                "measured_share_le_2_or_absent_over_added_set":
                    m3["arms"][arm]["added"]["share_le_2_or_absent"],
                "stratum4_nodes_minus_V_share_le_2_or_absent":
                    s4.get("share_le_2_or_absent"),
                "note": "the discount is the estimated drop range above, applied to the artists "
                        "the arm adds. It is NOT a second measurement -- it is the same estimate "
                        "read a second way, and it inherits every bound in this file.",
            },
        }

    C.write_json(HERE / "s3_unlicensed_sensitivity.json", {
        "STATUS": "EXPLICITLY UNLICENSED SENSITIVITY -- not a read, not a finding, not in the "
                  "record. Requested by the owner 2026-09-15 with the unreachability of LBA-R8 "
                  "and LBA-R9 already stated to him; recorded as his in LBA-AM3-1.",
        "makes_reachable": "NOTHING. LBA-R8 and LBA-R9 remain formally unreachable.",
        "bounds_that_travel_with_every_figure_here": [
            "LBA-AM3-2's disqualifier FIRED on every evaluable arm (skew 51.7-71.3 pp against a "
            "10-point bar). The comparison is disqualified, not wrong -- and not right either.",
            "LBA-X2(a) / ULC-F4: an OVER-estimate of what the app cannot play; UNBOUNDED on U.",
            "LBA-X2(b): the carried verdicts are un-re-run. Unmeasured, not zero.",
            "LBA-AM3-3: on the U row the class share is measured on a MINORITY of the "
            "added-beyond-V subset and extrapolated to the rest.",
        ],
        "within_class_drop_rate_range_never_averaged": [lo, hi],
        "arms": arms,
    }, __file__)

    for arm, r in arms.items():
        if "delta_pp" not in r:
            print(f"[sens] {arm}: n/a (V row)")
            continue
        print(f"[sens] {arm} ({r['population_rule']}): if read as measured LBA-G4 "
              f"{r['IF_READ_AS_MEASURED_LBA_G4']} at {r['delta_pp']:+.2f} pp "
              f"(bar {G4_BAR_PP:.0f}) -- DISQUALIFIED, skew {r['provenance_skew_pp']:.1f} pp; "
              f"added-beyond-V est. drop "
              f"{r['added_beyond_V']['estimated_drop_share_range'][0]:.3f}-"
              f"{r['added_beyond_V']['estimated_drop_share_range'][1]:.3f} "
              f"at coverage {r['added_beyond_V']['coverage_share']:.3f}")


if __name__ == "__main__":
    main()
