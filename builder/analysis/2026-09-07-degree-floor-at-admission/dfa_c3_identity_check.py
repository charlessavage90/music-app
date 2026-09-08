"""`DFA-` §9 — test the saturation identity against Track B's committed record.

WHAT THIS DOES. README §8.1 derived that where at least 1% of nodes sit at the
boundary degree, `top1pct_degree_mass_frac` collapses to

    round(N/100) * C / (total degree)          C = the boundary degree

and therefore cannot see how edges are arranged. Track B's `CRS-C3` criterion uses
that same statistic, and its capped cells are the saturated case. This tests the
identity directly against `cb_scores.json` and asks whether `C3` could have fired
on any selectable cell.

WHY NO ARTIFACT IS OPENED. Each cell's record stores `p99_degree` beside
`max_degree`. `p99 == max` means at least 1% of nodes sit at the maximum, which IS
the saturation condition — so the test needs only the committed JSON. Nothing here
reads a `.bin`, builds a graph, or routes anything.

WHAT IT DOES NOT TOUCH, and each is easy to overrun:
  * `CRS-C4` hub transit is a ROUTING measure over built paths, not a degree
    distribution. It is untouched, it is not saturation-degenerate, and its
    bound-100 finding stands exactly as recorded.
  * NONE of Track B's conclusions is overturned. Its selection rests on its other
    criteria. `C3` was a FLAG, not a gate, by its own pre-registration; a flag that
    could not fire changed no verdict. What changes is the weight a reader should
    give `C3`'s silence.
  * This is NOT evidence about any cap rule. That decision is parked and the
    owner's and owes a blind listen before any adoption.

Track B's own figures are INPUTS here and are cited, never restated: this file and
README §9 own only the derived quantities.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-floor-at-admission/dfa_c3_identity_check.py
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
SCORES = HERE.parent / "2026-07-30-track-b-cap-selection" / "cb_scores.json"

# CRS-C3, from specs/2026-07-30-track-b-cap-selection-preregistration.md: a
# candidate cell is flagged when its top1pct_degree_mass_frac exceeds its
# ARCHIVE'S MK50 cell by >= 50% relative. A flag, explicitly not a gate.
FLAG_RELATIVE = 1.5
BASELINE_CELL = "MK50"


def archive_of(cell_id: str) -> str:
    return "ALG-B" if cell_id.startswith("ALG-B") else "ALG-E"


def main() -> int:
    record = json.loads(SCORES.read_text(encoding="utf-8"))
    cells = record["cells"]
    baseline = {
        a: cells[f"{a}-{BASELINE_CELL}"]["structural"]["hub_structure"][
            "top1pct_degree_mass_frac"
        ]
        for a in ("ALG-B", "ALG-E")
    }

    out: dict = {
        "probe": "DFA- section 9 — does top1pct_degree_mass_frac reduce to "
        "boundary_degree / (100 * mean_degree) on Track B's cells, and could "
        "CRS-C3 have fired on any selectable cell?",
        "reasoning_owner": "this probe's README section 8.1",
        "inputs": {
            "file": str(SCORES),
            "harness_commit_recorded_in_it": record.get("harness_commit"),
            "note": "Track B's figures are INPUTS and are cited, never restated. "
            "Only the derived columns below are owned here.",
        },
        "criterion": {
            "id": "CRS-C3",
            "definition": "flag when a cell's top1pct_degree_mass_frac exceeds "
            "its archive's MK50 cell by >= 50% relative",
            "kind": "a FLAG, not a gate — the pre-registration says so explicitly",
        },
        "cells": [],
    }

    worst_fraction = 0.0
    families: dict[str, list] = {}
    for name, cell in sorted(cells.items()):
        hub = cell["structural"]["hub_structure"]
        nodes = cell["structural"]["nodes"]
        mean_degree = hub["mean_degree"]
        max_degree = hub["max_degree"]
        p99 = hub["p99_degree"]
        reported = hub["top1pct_degree_mass_frac"]

        total_degree = nodes * mean_degree
        cut = round(nodes / 100)
        # Upper bound: every node in the top 1% at the maximum degree. Under
        # saturation this is not a bound but the exact value.
        predicted_hi = cut * max_degree / total_degree
        # Lower bound: every node in the top 1% at the p99 degree.
        predicted_lo = cut * p99 / total_degree
        saturated = p99 == max_degree
        threshold = FLAG_RELATIVE * baseline[archive_of(name)]
        # The most this statistic COULD read on this cell, given only its own
        # bound and mean degree, as a fraction of its own flag threshold.
        headroom = predicted_hi / threshold
        # The mean degree this cell would have needed in order to fire at all.
        mean_needed = cut * max_degree / (threshold * nodes)

        row = {
            "cell": name,
            "rule": cell["rule"],
            "selectable": cell["selectable"],
            "saturated_p99_equals_max": saturated,
            "reported_over_predicted": round(reported / predicted_hi, 5),
            "admissible_window_width_as_fraction_of_upper_bound": round(
                1 - predicted_lo / predicted_hi, 5
            ),
            "reported_inside_its_own_window": predicted_lo <= reported <= predicted_hi * 1.0001,
            "max_possible_over_flag_threshold": round(headroom, 5),
            "mean_degree_needed_to_fire": round(mean_needed, 3),
            "mean_degree_actual_over_needed": round(mean_degree / mean_needed, 3),
        }
        out["cells"].append(row)
        families.setdefault(cell["rule"], []).append(row)
        if cell["selectable"]:
            worst_fraction = max(worst_fraction, headroom)

    out["by_rule_family"] = {
        rule: {
            "cells": len(rows),
            "all_saturated": all(r["saturated_p99_equals_max"] for r in rows),
            "reported_over_predicted_min": min(r["reported_over_predicted"] for r in rows),
            "reported_over_predicted_max": max(r["reported_over_predicted"] for r in rows),
            "worst_relative_error_from_the_identity": round(
                max(abs(r["reported_over_predicted"] - 1) for r in rows), 6
            ),
        }
        for rule, rows in sorted(families.items())
    }

    selectable = [c for c in out["cells"] if c["selectable"]]
    out["CRS_C3_could_it_have_fired"] = {
        "selectable_cells": len(selectable),
        "largest_max_possible_over_threshold_across_selectable_cells": round(
            worst_fraction, 5
        ),
        "range_across_selectable_cells": [
            round(min(c["max_possible_over_flag_threshold"] for c in selectable), 5),
            round(max(c["max_possible_over_flag_threshold"] for c in selectable), 5),
        ],
        "any_selectable_cell_could_have_fired": worst_fraction >= 1.0,
        "cells_that_would_have_fired": [
            {
                "cell": c["cell"],
                "over_threshold_by": c["max_possible_over_flag_threshold"],
                "selectable": c["selectable"],
            }
            for c in out["cells"]
            if c["max_possible_over_flag_threshold"] >= 1.0
        ],
        "reading": "the outcome was fixed by each cell's bound and mean degree "
        "before edge arrangement entered the calculation. On the saturated cells "
        "rearranging edges cannot move the statistic at all; on the others it can "
        "move it by at most the admissible window width",
    }
    out["limits"] = [
        "Says nothing about CRS-C4 hub transit, a routing measure over built "
        "paths. Untouched, not saturation-degenerate, and its finding stands.",
        "Overturns none of Track B's conclusions, which rest on its other "
        "criteria. C3 was a flag, not a gate; a flag that could not fire changed "
        "no verdict. What changes is the weight a reader gives C3's silence.",
        "Not evidence about any cap rule. That decision is parked and the "
        "owner's and owes a blind listen before any adoption.",
    ]

    dest = HERE / "dfa_c3_identity_check.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")

    for rule, summary in out["by_rule_family"].items():
        print(
            f"{rule:<18} cells {summary['cells']:>2}  all saturated "
            f"{str(summary['all_saturated']):<5}  reported/predicted "
            f"{summary['reported_over_predicted_min']:.4f}-"
            f"{summary['reported_over_predicted_max']:.4f}  worst error "
            f"{summary['worst_relative_error_from_the_identity']:.6f}"
        )
    c3 = out["CRS_C3_could_it_have_fired"]
    print(
        f"\nCRS-C3: could any selectable cell have fired? "
        f"{c3['any_selectable_cell_could_have_fired']}  "
        f"(closest reached {100 * c3['largest_max_possible_over_threshold_across_selectable_cells']:.1f}% "
        f"of its own threshold)"
    )
    for c in c3["cells_that_would_have_fired"]:
        print(f"  would have fired: {c['cell']} by {c['over_threshold_by']:.1f}x — "
              f"selectable={c['selectable']}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
