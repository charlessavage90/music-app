"""Track 2F arm definitions: the similarity-ceiling toll as a dose-response ladder.

Pre-registration `docs/superpowers/specs/2026-07-25-track2f-toll-full-strength-preregistration.md`
§0. Declarative and separate from the walker, so the factor table can be read off the
code and checked against the document -- the same discipline `arms.py` applies to Track 2.

**One knob, one column.** Every arm is `A7` (Track 2's W, unchanged) plus a toll
magnitude. `P` and `A0` come along because the scorer needs them: C1 is paired against
`P`, and C5's d0 inspection is referenced to BOTH `P` and `A0` (Track 2 A8).

**Magnitudes are in multiples of `w_hop`, not `toll_s`.** This is the fix for A17(b):
`toll_s` is w_sim-dependent, so one value means two different tolls under two different
W, and §1.4's 7.5x/30x figures were quoted for an S-mag of 3.0 while W carried 1.5.
`toll_hops` names its own basis and is w_sim-independent.

**The two reproduction arms deliberately keep `toll_s`.** The two specifications are not
bit-identical at the same nominal magnitude (1.5*(1-0.80) = 0.29999999999999993 against
15*0.02 = 0.30000000000000004), so an arm whose job is to reproduce a committed run must
be specified exactly as that run was. Their nominal ladder positions are therefore
accurate to ~1e-16 relative, which is far below anything scored.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-07-24-track2-arm-scorer"))

from arms import Arm  # noqa: E402

# Pre-registration §0. Ladder order, ascending. The `toll_s` column is non-None only for
# the two reproduction arms; see the module docstring for why.
#             name        hops    toll_s  baseline     reading
LADDER = [
    ("T1a_rpt",    3.75,   0.95, "A7",       "reproduction of T1a -- must be byte-identical"),
    ("TF1",         7.5,   None, "A7",       "§1.4's INTENDED T1a magnitude (never run)"),
    ("T1b_rpt",      15,   0.80, "TF1",      "reproduction of T1b -- must be byte-identical"),
    ("TF2",          30,   None, "T1b_rpt",  "§1.4's INTENDED TOP -- the headline arm"),
    ("TF3",          60,   None, "TF2",      "one doubling past the intended top"),
    ("TF4",         120,   None, "TF3",      "two doublings past the intended top"),
    ("TFX",        7500,   None, "TF4",      "the ban corner: a BOUND, never a candidate"),
]

# No arm here differs from its baseline by more than one column, so there is nothing that
# cannot be attributed. Empty by construction rather than by omission -- the scorer reads
# this, and an absent name would silently fall back to Track 2's list.
PACKAGE_CONTRASTS: dict[tuple[str, str], str] = {}

# TF-D1's binding value: an edge is "ceiling" iff its stored score is exactly this. The
# p99 clip writes `min(1.0, ...)` (builder `pipeline.py`), so saturation is exact equality.
CEILING_SCORE = 1.0


def build_arms(by_name: dict[str, Arm]) -> list[Arm]:
    """P, A0, A7, then the ladder. `by_name` is Track 2's STAGE1, keyed by arm name."""
    base = by_name["A7"]
    arms = [by_name["P"], by_name["A0"], base]
    for name, hops, toll_s, baseline, reading in LADDER:
        cfg = (base.cfg.with_(toll_s=toll_s) if toll_s is not None
               else base.cfg.with_(toll_hops=float(hops)))
        arms.append(Arm(name, cfg, baseline, reading, adoptable=(name != "TFX")))
    return arms


def factor_table() -> str:
    rows = [f"{'arm':<9} {'toll x w_hop':>12} {'spec':<14} {'baseline':<9} reading",
            f"{'A7':<9} {'0 (off)':>12} {'--':<14} {'--':<9} the ladder's isolating baseline"]
    for name, hops, toll_s, baseline, reading in LADDER:
        spec = f"toll_s={toll_s}" if toll_s is not None else f"toll_hops={hops}"
        rows.append(f"{name:<9} {hops:>12} {spec:<14} {baseline:<9} {reading}")
    return "\n".join(rows)


if __name__ == "__main__":
    print(factor_table())
