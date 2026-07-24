"""P4 step 1b: emit the label sheet in a blind, reproducible order.

The strata are not neutral — S1 is the insular-stratum artists, S4 is deliberately
enriched with off-platform fame. Presenting the sample grouped, or in `sample.json`
order, would show the owner the design and invite him to label the group rather than the
artist. So the order is shuffled once, with a fixed seed, and committed.

Reproducible because he may answer over more than one sitting, and because the mapping
from his answers back to strata must be auditable afterwards rather than reconstructed.

**Prints names only.** No stratum, no popularity, no fan count — none is loaded here, and
at the time this runs none exists on the machine.

Run from anywhere:
    python builder/analysis/2026-07-23-track2-fame-proxy/blind_sheet.py
"""

import json
import random
from pathlib import Path

SEED = 20260723
HERE = Path(__file__).resolve().parent


def main():
    sample = json.loads((HERE / "sample.json").read_text(encoding="utf-8"))
    names = [n for members in sample["strata"].values() for n in members]
    if len(names) != len(set(names)):
        raise SystemExit("strata are not disjoint")

    order = sorted(names)  # sort first so the shuffle does not inherit strata order
    random.Random(SEED).shuffle(order)

    (HERE / "blind_order.json").write_text(
        json.dumps({"seed": SEED, "order": order}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    for i, name in enumerate(order, 1):
        print(f"{i:2d}. {name}")
    print(f"\n{len(order)} artists, seed {SEED} -> blind_order.json")


if __name__ == "__main__":
    main()
