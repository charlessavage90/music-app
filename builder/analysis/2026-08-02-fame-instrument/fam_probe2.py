"""Addendum to the FAM- design-critique probe: percentile curve, frame arithmetic,
FAM-4 rounding fragility. READ-ONLY, no named-artist lookup."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np

from artistpath_builder.artifact import deserialise

HERE = Path("analysis/2026-07-30-fame-proxy-coverage")
SNAP = HERE / "fp_listenbrainz.json"
SCRATCH = Path("scratch")
FRAME_N = 74_193


def main() -> None:
    d = json.loads(SNAP.read_text(encoding="utf-8"))
    vals = np.array(sorted(v["users"] for v in d.values() if v is not None), np.int64)
    n = len(vals)
    cnt = Counter(vals.tolist())
    uniq = np.array(sorted(cnt), np.int64)
    counts = np.array([cnt[int(v)] for v in uniq], np.int64)
    less = np.concatenate([[0], np.cumsum(counts)[:-1]])
    pctl = (less + (counts + 1) / 2.0) / FRAME_N

    print("== where the bars actually sit, in listener counts ==")
    for q in (0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 0.999):
        i = int(np.searchsorted(pctl, q))
        i = min(i, len(uniq) - 1)
        print(f"  fame_lb_pctl {q:6.3f}  <-> fame_lb_raw ~ {int(uniq[i]):>8,}"
              f"   (artists at or below: {int(less[i]+counts[i]):>6,})")

    print("\n== how many PERCENTILE POINTS a fame drop buys, by starting point ==")
    print("  (this is the currency a bypass-obscurity gradient would be read in)")

    def p_of(v: int) -> float:
        i = int(np.searchsorted(uniq, v, side="right")) - 1
        return float(pctl[max(i, 0)])

    print("  start raw   start pctl   after /2      after /10     after /100")
    for v in (100_000, 30_000, 10_000, 3_000, 1_335, 300, 100, 30):
        print(f"  {v:>9,}   {p_of(v):10.4f}   {p_of(v)-p_of(v//2):+9.4f}    "
              f"{p_of(v)-p_of(max(v//10,1)):+9.4f}    "
              f"{p_of(v)-p_of(max(v//100,1)):+9.4f}")

    print("\n== quantisation: worst-case error from tie atoms, by region ==")
    for lo, hi, label in ((0.0, 0.10, "bottom decile"), (0.10, 0.50, "rest of lower half"),
                          (0.50, 0.90, "upper half"), (0.90, 1.01, "top decile")):
        m = (pctl >= lo) & (pctl < hi)
        if not m.any():
            continue
        atom = counts[m].max() / FRAME_N
        print(f"  {label:20s} distinct pctl values={int(m.sum()):>6,}"
              f"  largest atom={atom:.5f} of frame"
              f"  ({int(counts[m].max())} artists)")

    print("\n== frame arithmetic the prereg asserts ==")
    ad = deserialise((SCRATCH / "graph-t15-tiebreakfix.bin").read_bytes())
    ab = deserialise((SCRATCH / "graph-algb-full.bin").read_bytes())
    A, B = set(ad.mbids), set(ab.mbids)
    print(f"  adopted N          : {len(A):,}   (prereg says 74,193)")
    print(f"  ALG-B full N       : {len(B):,}   (prereg says 68,467)")
    print(f"  union              : {len(A | B):,}   (prereg says 93,067)")
    print(f"  overlap            : {len(A & B):,}")
    print(f"  ALG-B-only         : {len(B - A):,}  = {len(B-A)/len(A|B):.1%} of union"
          "   <- NOT in the fame_lb_pctl frame, and no FAM- criterion inspects them")
    print(f"  adopted-only       : {len(A - B):,}")

    lb = {k: (v["users"] if v else None) for k, v in d.items()}
    ovl = [lb[m] for m in (A & B) if lb.get(m)]
    only = [lb[m] for m in (A - B) if lb.get(m)]
    print(f"\n  median fame_lb_raw, adopted artists ALSO in ALG-B : "
          f"{int(np.median(ovl)):,}  (n={len(ovl):,})")
    print(f"  median fame_lb_raw, adopted artists NOT in ALG-B  : "
          f"{int(np.median(only)):,}  (n={len(only):,})")

    print("\n== FAM-4: rounding fragility of the >=10x filter ==")
    hand = {
        "Lykke Li": 15_000_000, "Beach House": 14_800_000, "New Order": 8_800_000,
        "10cc": 6_700_000, "The Human League": 6_000_000, "Quantic": 2_300_000,
        "Nightmares on Wax": 1_700_000, "NOFX": 1_000_000, "Boards of Canada": 1_000_000,
        "Black Rebel Motorcycle Club": 716_000, "Love": 571_000,
        "Porcupine Tree": 500_000, "Television": 372_000,
        "Captain Beefheart & His Magic Band": 235_000, "Blood Red Shoes": 168_000,
    }
    sig = {a: len(str(v).rstrip("0")) for a, v in hand.items()}
    print("  significant figures as recorded (1 s.f. = +-50% at the extreme):")
    for a, v in sorted(hand.items(), key=lambda kv: -kv[1]):
        print(f"    {a:36s} {v:>10,}  {sig[a]} s.f.")
    ratios = sorted(
        (max(hand[a], hand[b]) / min(hand[a], hand[b]), a, b)
        for a, b in itertools.combinations(hand, 2)
    )
    near = [(r, a, b) for r, a, b in ratios if 6.0 <= r <= 16.0]
    print(f"\n  pairs with ratio in [6x, 16x] -- i.e. whose inclusion in the "
          f"denominator\n  could flip under 1-s.f. rounding: {len(near)}")
    for r, a, b in near:
        mark = "IN " if r >= 10 else "OUT"
        print(f"    {mark} {r:6.2f}x  {a} / {b}")


if __name__ == "__main__":
    main()
