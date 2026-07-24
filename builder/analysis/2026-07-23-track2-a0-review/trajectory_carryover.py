"""Does the floor's d0-d5 influence survive into the scored window (d >= 10)?

The floor term's VALUE is provably zero from d7 (see floor_asymmetry.py part 1). But the
bypass walk is driven by each arm's own paths, so a path the floor changed at d0 changes
which artist is bypassed at d0, and every later cell inherits that. This reads the walks
already recorded by floor_asymmetry.py and asks, per depth 0..20, whether the floor-ON and
floor-OFF twins of the same arm family still differ.

MECHANICAL only: path identity, victim identity, in-graph popularity. Nothing scored.

Run from `api/`:
    PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
        ../builder/analysis/2026-07-23-track2-a0-review/trajectory_carryover.py
"""

import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
FAMILIES = [("P", "A0"), ("A6r", "A6"), ("Xr", "X")]


def main() -> int:
    data = json.loads((OUT / "raw_results.json").read_text(encoding="utf-8"))
    print(f"artifact sha256 {data['artifact_sha256'][:8]}...{data['artifact_sha256'][-7:]}")
    arms = data["arms"]

    print("\n=== cells where floor-ON != floor-OFF, by depth (12 pairs) ===")
    print(f"{'depth':>5} " + " ".join(f"{on + ' vs ' + off:>14}" for on, off in FAMILIES))
    for d in range(0, 21):
        cells = []
        for on, off in FAMILIES:
            diff = tot = 0
            for key in arms[on]:
                ron = [r for r in arms[on][key] if r["depth"] == d]
                roff = [r for r in arms[off][key] if r["depth"] == d]
                if ron and roff:
                    tot += 1
                    if ron[0]["path"] != roff[0]["path"]:
                        diff += 1
            cells.append(f"{diff}/{tot}")
        print(f"{'d' + str(d):>5} " + " ".join(f"{c:>14}" for c in cells))

    print("\n=== per-pair: first depth of divergence, and whether it ever reconverges ===")
    for on, off in FAMILIES:
        print(f"\n-- {on} vs {off} --")
        for key in arms[on]:
            ds = []
            for d in range(0, 21):
                ron = [r for r in arms[on][key] if r["depth"] == d]
                roff = [r for r in arms[off][key] if r["depth"] == d]
                if ron and roff:
                    ds.append(ron[0]["path"] != roff[0]["path"])
            if not any(ds):
                print(f"  {key:<38} identical at all {len(ds)} depths")
            else:
                first = ds.index(True)
                n_diff = sum(ds)
                tail = "yes" if ds[-1] else "NO (reconverged)"
                print(f"  {key:<38} first diff d{first}; differs in {n_diff}/{len(ds)} "
                      f"depths; still differing at d20: {tail}")

    print("\n=== interior count (payload) by depth, pooled over 12 pairs ===")
    print(f"{'depth':>5} " + " ".join(f"{a:>6}" for a, _ in FAMILIES for a in (a, _)))
    for d in (0, 1, 2, 3, 5, 7, 10, 15, 20):
        cells = []
        for on, off in FAMILIES:
            for arm in (on, off):
                tot = sum(r.get("n_interior", 0) for k in arms[arm]
                          for r in arms[arm][k] if r["depth"] == d)
                cells.append(f"{tot:>6}")
        print(f"{'d' + str(d):>5} " + " ".join(cells))

    print("\n=== median-of-cell-medians of interior RAW popularity (in-graph, NOT fame) ===")
    print("Reported to show the floor knob moves path composition, not to score anything.")
    import statistics
    print(f"{'depth':>5} " + " ".join(f"{a:>8}" for on, off in FAMILIES for a in (on, off)))
    for d in (0, 1, 2, 3, 5, 7, 10, 15, 20):
        cells = []
        for on, off in FAMILIES:
            for arm in (on, off):
                vals = [r["median_interior_pop"] for k in arms[arm]
                        for r in arms[arm][k]
                        if r["depth"] == d and "median_interior_pop" in r]
                cells.append(f"{statistics.median(vals):8.4f}" if vals else f"{'-':>8}")
        print(f"{'d' + str(d):>5} " + " ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
