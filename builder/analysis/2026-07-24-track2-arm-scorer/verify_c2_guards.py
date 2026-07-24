"""Exercise C2's two guards on synthetic cells — because production cannot exercise them.

P contains no nameless interior and its C2 pass rests on no flagged artist, so a run over
production leaves both guards **silent**, and silence is not evidence that a guard works.
This is the same reasoning as `test_acceptance.py`'s "the defect must actually be present,
or the test proves nothing about the check".

Both guards come from the P8b harness review:

  F8  a nameless interior must NOT count as C2 reach. It resolves to the fame floor for
      want of anything to query, so counting it would let an arm bank a pass on a card
      that renders blank. Conservative — it can only make C2 harder.
  F2  a flagged-notable interior DOES count (A11 pre-registered unmatched-as-floor), but
      a pass resting on nothing else must be reported for the owner's one-glance check.
      The distinction matters: excluding these would change the adopted encoding, whereas
      excluding nameless ones fixes an artifact defect.

Offline, no artifact, no network. Run from anywhere:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u verify_c2_guards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "api" / "src"))

from score import C1_DEPTHS, C2_DEPTHS, score_arm  # noqa: E402

B = 5.0          # B_unk for these fixtures
FAMOUS = 7.0     # comfortably above B
OBSCURE = 1.0    # comfortably below B

# Node ids: 0/1 endpoints, then one interior per case.
PLAIN_OBSCURE, NAMELESS, NOTABLE, SECOND_OBSCURE = "10", "11", "12", "13"

MBIDS = {
    "0": "mb-start", "1": "mb-end",
    PLAIN_OBSCURE: "mb-plain", NAMELESS: "mb-blank",
    NOTABLE: "mb-notable", SECOND_OBSCURE: "mb-plain2",
}
NAMES = {
    "0": "Start", "1": "End",
    PLAIN_OBSCURE: "Plain Obscure", NAMELESS: "",
    NOTABLE: "Notable Absent", SECOND_OBSCURE: "Other Obscure",
}
FAME = {
    "mb-start": FAMOUS, "mb-end": FAMOUS,
    "mb-plain": OBSCURE, "mb-blank": 0.0,
    "mb-notable": 0.0, "mb-plain2": OBSCURE,
}
GUARD = {"notable": {"mb-notable"}, "nameless": {"mb-blank"}}

ALL_DEPTHS = sorted({0, 1, 2, 3, 5, 7, *C1_DEPTHS, *C2_DEPTHS})


def _doc(interior_by_pair: dict[str, str | None]) -> dict:
    """One arm 'X' plus 'P', four pairs, the given interior at every depth.

    P is given a famous interior throughout so C1 is well-defined and the arm's C2 is
    the only thing under test.
    """
    pairs = sorted(interior_by_pair)

    def cells(interior):
        path = [0, int(interior), 1] if interior else None
        return {str(d): path for d in ALL_DEPTHS}

    return {
        "snapshots": ALL_DEPTHS,
        "pairs": pairs,
        "held_out_pairs": [],
        "arms": ["P", "X"],
        "node_mbids": MBIDS,
        "node_names": NAMES,
        "paths": {
            "P": {p: cells(PLAIN_OBSCURE) for p in pairs},
            "X": {p: cells(interior_by_pair[p]) for p in pairs},
        },
    }


def _c2(interior_by_pair):
    doc = _doc(interior_by_pair)
    return score_arm("X", doc, FAME, sorted(interior_by_pair), B, GUARD)["C2"]


def main() -> int:
    failures = []

    def check(label, got, want):
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}  {label}\n        got {got!r}")
        if not ok:
            failures.append(f"{label}: got {got!r}, wanted {want!r}")

    print("F8 — a nameless interior must not count as reach")
    c2 = _c2({f"p{i}": NAMELESS for i in range(4)})
    check("4 nameless-only pairs reach nothing", c2["pairs_reached"], 0)
    check("all 4 recorded as nameless-excluded",
          len(c2["nameless_excluded_from_reach"]), 4)
    check("C2 fails on nameless alone", c2["pass"], False)

    print("\nF8 — the same four pairs with a real obscure interior DO reach")
    c2 = _c2({f"p{i}": PLAIN_OBSCURE for i in range(4)})
    check("4 plain-obscure pairs reach", c2["pairs_reached"], 4)
    check("C2 passes at the threshold", c2["pass"], True)
    check("nothing flagged", c2["rests_only_on_flagged_notable"], {})

    print("\nF2 — a flagged-notable interior counts, and is reported")
    c2 = _c2({f"p{i}": NOTABLE for i in range(4)})
    check("flagged interiors still reach (A11's encoding stands)",
          c2["pairs_reached"], 4)
    check("every pair reported as resting only on flagged",
          len(c2["rests_only_on_flagged_notable"]), 4)
    check("C2 passes, but auditably", c2["pass"], True)

    print("\nF2 — a pass with other evidence must NOT be reported as flag-dependent")
    c2 = _c2({"p0": NOTABLE, "p1": PLAIN_OBSCURE,
              "p2": SECOND_OBSCURE, "p3": PLAIN_OBSCURE})
    check("all four reach", c2["pairs_reached"], 4)
    check("only the flag-only pair is reported",
          sorted(c2["rests_only_on_flagged_notable"]), ["p0"])

    print("\nMixed — nameless alongside a real reach does not suppress the pair")
    doc = _doc({"p0": PLAIN_OBSCURE, "p1": NAMELESS, "p2": NAMELESS, "p3": NAMELESS})
    # p1-p3 are nameless-only, so exactly one pair reaches: the guard is subtractive,
    # never additive, which is what "conservative" has to mean.
    c2 = score_arm("X", doc, FAME, ["p0", "p1", "p2", "p3"], B, GUARD)["C2"]
    check("one pair reaches", c2["pairs_reached"], 1)
    check("three nameless exclusions recorded",
          len(c2["nameless_excluded_from_reach"]), 3)

    print()
    if failures:
        print(f"{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("all C2 guard checks passed — both guards demonstrably fire, and the")
    print("nameless guard is subtractive only (it never manufactures a reach).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
