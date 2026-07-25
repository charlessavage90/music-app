"""P8b probe 5: is C1's composite robust to the absence-as-fame-floor encoding?

Under A11 an unmatched interior scores F = 0, which on a log10 fan/pageview scale is a
very large outlier -- several units below the least famous artist the proxy can see. C1
is a MEAN over cells of a per-cell MEDIAN, so the question is whether a candidate could
clear C1's -1.0 threshold purely by putting a handful of cells' medians on the floor
while the rest of the grid barely moves.

Answered by arithmetic against P's own cell medians (arm P only; no experimental arm).
C1 has two clauses and this probe shows the second is what does the work.

Run:  PYTHONIOENCODING=utf-8 python -u probe_c1_sensitivity.py
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"

C1_DEPTHS = (10, 15, 20)
C1_MEAN_MAX = -1.0
C1_FRAC_MIN = 0.75


def main() -> int:
    doc = json.loads((HERE / "paths_P.json").read_text(encoding="utf-8"))
    famedoc = json.loads((HERE / "fame_P.json").read_text(encoding="utf-8"))
    F, rows = famedoc["fame"], famedoc["rows"]
    B = math.log10(1.0 + int(json.loads((PROXY / "score.json").read_text(encoding="utf-8"))
                             ["b_unk"]["threshold"]))
    names = doc["node_names"]
    held = set(doc["held_out_pairs"])
    analysis = [p for p in doc["pairs"] if p not in held]
    P = doc["paths"]["P"]

    cell_medians = []
    for pair in analysis:
        for d in C1_DEPTHS:
            path = P[pair][str(d)]
            ints = [names[str(n)] for n in path[1:-1]] if path else []
            if ints:
                cell_medians.append(statistics.median([F[n] for n in ints]))
    n_cells = len(cell_medians)
    total = sum(cell_medians)

    matched_F = sorted(F[n] for n, r in rows.items() if r.get("matched"))
    # how many cells would have to bottom out at median 0 to hit mean dF <= -1.0 alone
    need = C1_MEAN_MAX * -1.0 * n_cells  # required total drop
    # greedily floor the largest-median cells first (the cheapest way to buy the mean)
    k, acc = 0, 0.0
    for m in sorted(cell_medians, reverse=True):
        if acc >= need:
            break
        acc += m
        k += 1

    out = {
        "arm": "P only",
        "n_C1_cells": n_cells,
        "P_cell_median_F": {
            "mean": round(statistics.mean(cell_medians), 4),
            "min": round(min(cell_medians), 4),
            "max": round(max(cell_medians), 4),
        },
        "matched_fame_distribution": {
            "n_matched": len(matched_F),
            "min": round(matched_F[0], 4),
            "p10": round(matched_F[len(matched_F) // 10], 4),
            "median": round(statistics.median(matched_F), 4),
            "max": round(matched_F[-1], 4),
            "fame_floor_for_unmatched": 0.0,
            "gap_floor_to_least_famous_matched": round(matched_F[0], 4),
        },
        "B_unk_fame_units": round(B, 4),
        "C1_clause_interaction": {
            "required_total_drop_for_mean_-1.0": round(need, 4),
            "cells_that_must_bottom_out_at_median_0": k,
            "as_frac_of_cells": round(k / n_cells, 4),
            "C1_frac_negative_required": C1_FRAC_MIN,
            "verdict": (
                f"flooring {k} of {n_cells} cells ({k / n_cells:.0%}) satisfies C1's MEAN "
                f"clause, but C1 also requires dF < 0 in >= {C1_FRAC_MIN:.0%} of cells. "
                "An arm that reaches the floor on a minority of cells and leaves the rest "
                "unchanged therefore FAILS C1. The fraction clause is what stops the "
                "absence encoding buying a pass on a few cells; the two clauses are not "
                "redundant and both are load-bearing."),
        },
    }
    (HERE / "probe_c1_sensitivity.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
