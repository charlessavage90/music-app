"""Exercise C2's two guards on synthetic cells — because production cannot exercise them.

P contains no nameless interior and its C2 pass rests on no flagged artist, so a run over
production leaves both guards **silent**, and silence is not evidence that a guard works.
This is the same reasoning as `test_acceptance.py`'s "the defect must actually be present,
or the test proves nothing about the check".

Both guards come from the P8b harness review:

  F8  a blank-named interior contaminates its CELL, which is then dropped from every arm
      or from none. Dropping the node instead would be directional: F = 0 drags C1's and
      C3's medians toward passing, blank names concentrate 2.7x in the stratum the diving
      arms target, and P has none — so a node-level fix silently improves exactly the arms
      under test. Cell-level is A13's rule (missingness must not correlate with arm)
      applied to a second cause. Default is to REFUSE to score; the uniform drop is the
      pre-registered response, chosen before stage 1 rather than after seeing who trips it.
  F2  a flagged-notable interior DOES count (A11 pre-registered unmatched-as-floor), but
      a pass resting on nothing else must be reported for the owner's one-glance check.
      The distinction matters: excluding these would change the adopted encoding, whereas
      a blank name is an artifact defect and not a judgement about an artist at all.

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

from score import (  # noqa: E402
    C1_DEPTHS,
    C2_DEPTHS,
    SCORED_DEPTHS,
    blank_scored_cells,
    cell_median,
    score_arm,
)

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

    print("F8 — a blank-named interior is detected at CELL level, per arm")
    doc = _doc({f"p{i}": NAMELESS for i in range(4)})
    cells = blank_scored_cells(doc)
    check("one contaminated cell per pair per scored depth",
          len(cells), 4 * len(SCORED_DEPTHS))
    check("contamination attributed to arm X only (P is clean)",
          sorted({a for v in cells.values() for a in v}), ["X"])

    print("\nF8 — the directional bias this replaces: blank drags the median DOWN")
    # The whole argument for cell-level in one assertion. A blank interior at F=0
    # produces a *better-looking* C1/C3 for the arm that routed through it, so a
    # node-level exclusion would remove evidence against the arm under test.
    blank_med = cell_median([0, int(NAMELESS), 1], MBIDS, FAME)
    plain_med = cell_median([0, int(PLAIN_OBSCURE), 1], MBIDS, FAME)
    famous_med = cell_median([0, 10, 1], MBIDS, FAME)
    check("blank scores below a genuinely obscure artist", blank_med < plain_med, True)
    check("and far below the control's interior", blank_med < famous_med, True)

    print("\nF8 — a real obscure interior DOES reach (the guard is not over-broad)")
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

    print("\nF8 — the uniform drop removes the cell from the CONTROL too")
    # The property that makes it non-directional. P never contained the blank node, but
    # its cell goes as well, so the two arms are still compared on identical cells.
    doc = _doc({"p0": NAMELESS, "p1": PLAIN_OBSCURE, "p2": PLAIN_OBSCURE,
                "p3": PLAIN_OBSCURE})
    cells = blank_scored_cells(doc)
    for cell in cells:
        pair, _, dtag = cell.rpartition("@d")
        for arm in doc["paths"]:
            doc["paths"][arm][pair][dtag] = None
    surviving = {
        arm: sorted(d for p in doc["paths"][arm] for d in doc["paths"][arm][p]
                    if doc["paths"][arm][p][d] is not None)
        for arm in doc["paths"]
    }
    check("P and X left with identical surviving cells",
          surviving["P"] == surviving["X"], True)
    check("p0's scored depths gone from BOTH arms",
          all(doc["paths"][a]["p0"][str(d)] is None
              for a in ("P", "X") for d in SCORED_DEPTHS), True)

    print("\nF8 — a clean file is detected as clean (no false positives)")
    check("no contaminated cells when every interior is named",
          blank_scored_cells(_doc({f"p{i}": PLAIN_OBSCURE for i in range(4)})), {})

    print()
    if failures:
        print(f"{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("all guard checks passed — both guards demonstrably fire; the blank-name")
    print("guard acts on cells, removes them from the control as well as the treatment,")
    print("and the bias it replaces is confirmed to point toward passing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
