"""Design-critique probe for the FAM- pre-registration (2026-08-02).

READ-ONLY. Measures the tie/atom structure of the retained 2026-07-30
ListenBrainz snapshot over the ADOPTED frame, because that is exactly the
distribution FAM-2, FAM-5 and the fame_lb_pctl definition will be evaluated on.

DELIBERATE LIMIT: no artist NAMES are joined here, and no named artist is
looked up. FAM-3 and FAM-4 read specific named artists; computing them now
would pre-empt a committed pre-registration's load-bearing verdict. Their
critique below is structural (pair arithmetic, power) and uses no ruler value.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u <this file>
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path("analysis/2026-07-30-fame-proxy-coverage")
SNAP = HERE / "fp_listenbrainz.json"
ADOPTED = Path("scratch/graph-t15-tiebreakfix.bin")
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
FRAME_N = 74_193


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Rank correlation with average ranks over ties (scipy-free)."""
    def rank(x: np.ndarray) -> np.ndarray:
        order = np.argsort(x, kind="mergesort")
        s = x[order]
        r = np.empty(len(x), dtype=np.float64)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and s[j + 1] == s[i]:
                j += 1
            r[order[i : j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r

    ra, rb = rank(a), rank(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom)


def main() -> None:
    print("== provenance ==")
    got = sha256(ADOPTED)
    print(f"adopted artifact   : {ADOPTED} sha256={got}")
    print(f"matches cb_metrics : {got == ADOPTED_SHA}")
    print(f"snapshot           : {SNAP} sha256={sha256(SNAP)}")

    d = json.loads(SNAP.read_text(encoding="utf-8"))
    nulls = sum(1 for v in d.values() if v is None)
    vals = np.array(
        sorted(v["users"] for v in d.values() if v is not None), dtype=np.int64
    )
    n = len(vals)
    print(f"\n== population ==")
    print(f"keys in snapshot   : {len(d)}   (frame stated in prereg: {FRAME_N})")
    print(f"nulls              : {nulls}")
    print(f"non-null           : {n}  ({n/len(d):.4%})")
    print(f"zeros              : {(vals == 0).sum()}")
    print(f"min/median/max     : {vals.min()} / {np.median(vals)} / {vals.max()}")

    cnt = Counter(vals.tolist())
    print(f"distinct values    : {len(cnt)}")

    print("\n== bottom of the distribution: atoms in raw-count space ==")
    print(" value   artists   frame share   cum frame share")
    cum = 0
    for v in range(0, 26):
        c = cnt.get(v, 0)
        cum += c
        print(f"{v:6d} {c:9d} {c/n:12.4%} {cum/n:16.4%}")

    print("\n== largest tie atoms overall (frame share) ==")
    for v, c in cnt.most_common(10):
        print(f"  value {v:6d}: {c:7d} artists = {c/n:.4%} of non-null frame")

    # ---------------- FAM-2 as written ----------------
    half = n // 2
    lower = vals[:half]
    lcnt = Counter(lower.tolist())
    biggest_v, biggest_c = lcnt.most_common(1)[0]
    print("\n== FAM-2 as written ==")
    print(f"lower half size (n//2)          : {half}")
    print(f"boundary value (vals[half-1])   : {lower[-1]}   next: {vals[half]}")
    tie_at_boundary = cnt.get(int(lower[-1]), 0)
    print(f"artists tied AT boundary value  : {tie_at_boundary}")
    print(f"distinct values in lower half   : {len(lcnt)}   (bar: >= 1000)")
    print(f"largest tied value in lower half: {biggest_v} held by {biggest_c}"
          f" = {biggest_c/half:.4%} of lower half   (bar: < 5%)")
    top5 = lcnt.most_common(5)
    print(f"top-5 atoms combined            : "
          f"{sum(c for _, c in top5)/half:.4%} of lower half   ({top5})")
    print(f"upper bound on distinct values  : median+1 = {int(np.median(vals))+1}"
          "  <- integer counts cannot exceed this in the lower half")

    # ---------------- fame_lb_pctl granularity ----------------
    print("\n== fame_lb_pctl: average rank over ties / frame size ==")
    uniq = np.array(sorted(cnt), dtype=np.int64)
    counts = np.array([cnt[int(v)] for v in uniq], dtype=np.int64)
    less = np.concatenate([[0], np.cumsum(counts)[:-1]])
    avg_rank = less + (counts + 1) / 2.0
    pctl_frame = avg_rank / FRAME_N      # prereg wording: divide by frame size
    pctl_nonnull = avg_rank / n          # the other plausible denominator
    print(f"max pctl under /{FRAME_N} (frame) : {pctl_frame[-1]:.6f}")
    print(f"max pctl under /{n} (non-null)   : {pctl_nonnull[-1]:.6f}")
    print(f"pctl gap between the two defs at the top: "
          f"{pctl_nonnull[-1]-pctl_frame[-1]:.6f}")

    print("\n value   pctl(frame)   step from previous value")
    prev = 0.0
    for v in list(range(0, 13)) + [15, 20, 30, 50, 100]:
        if v in cnt:
            i = int(np.searchsorted(uniq, v))
            print(f"{v:6d} {pctl_frame[i]:13.5f} {pctl_frame[i]-prev:20.5f}")
            prev = pctl_frame[i]

    for band in (0.10, 0.25, 0.50):
        k = int((pctl_frame < band).sum())
        print(f"distinct fame_lb_pctl values below {band:.2f}: {k}")

    print(f"largest single pctl step anywhere: "
          f"{np.diff(np.concatenate([[0.0], pctl_frame])).max():.5f}")

    # ---------------- FAM-5 stress ----------------
    print("\n== FAM-5: what Spearman >= 0.99 can and cannot detect ==")
    rng = np.random.default_rng(20260802)
    base = vals.copy()

    def report(label: str, other: np.ndarray) -> None:
        print(f"  {label:52s} rho = {spearman(base, other):.6f}")

    g = base + rng.poisson(0.005 * base)
    report("realistic 3-day drift (Poisson, 0.5% of u)", g)
    g = base + rng.poisson(0.05 * base)
    report("heavy drift (Poisson, 5% of u)", g)

    for thresh in (10, 100, 1000):
        g = base.copy()
        m = base <= thresh
        perm = rng.permutation(g[m])
        g[m] = perm
        report(f"ordering DESTROYED among artists with u <= {thresh}", g)

    g = base.copy()
    m = np.arange(n) < half
    g[m] = rng.permutation(g[m])
    report("ordering DESTROYED across the whole lower half", g)

    g = base.copy()
    m = base <= 100
    g[m] = rng.integers(1, 101, size=int(m.sum()))
    report("u <= 100 re-drawn uniform 1..100 (garbage tail)", g)

    # ---------------- FAM-4 structural (no ruler values used) ----------------
    print("\n== FAM-4: pair structure from the hand-read table ==")
    hand = {
        "Lykke Li": 15_000_000,
        "Beach House": 14_800_000,
        "New Order": 8_800_000,
        "10cc": 6_700_000,
        "The Human League": 6_000_000,
        "Quantic": 2_300_000,
        "Nightmares on Wax": 1_700_000,
        "NOFX": 1_000_000,
        "Boards of Canada": 1_000_000,
        "Black Rebel Motorcycle Club": 716_000,
        "Love": 571_000,
        "Porcupine Tree": 500_000,
        "Television": 372_000,
        "Captain Beefheart & His Magic Band": 235_000,
        "Blood Red Shoes": 168_000,
    }
    names = list(hand)
    pairs = [
        (a, b)
        for a, b in itertools.combinations(names, 2)
        if max(hand[a], hand[b]) / min(hand[a], hand[b]) >= 10.0
    ]
    print(f"artists in table (FERG excluded)     : {len(names)}")
    print(f"all unordered pairs                  : {len(names)*(len(names)-1)//2}")
    print(f"pairs at >= 10x                      : {len(pairs)}")
    deg = Counter()
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    print("pairs each artist participates in (its blast radius if mis-ranked):")
    for a, k in deg.most_common():
        print(f"  {a:36s} {hand[a]:>10,}  in {k:2d} pairs")
    print(f"artists appearing in NO >=10x pair    : "
          f"{[a for a in names if deg[a]==0]}")
    fails = int(np.ceil(0.10 * len(pairs)))
    print(f"pairs that may be wrong and still pass 90%: "
          f"{len(pairs) - int(np.ceil(0.9*len(pairs)))} of {len(pairs)} "
          f"(>= {fails} wrong fails)")

    # smallest n at which a 90% bar is readable against a coin-flip null
    print("\n  binomial: P(>=90% agreement | ruler is a coin flip) by pair count")
    from math import comb
    for m in (5, 10, 15, 20, 30, 40, 50):
        need = int(np.ceil(0.9 * m))
        p = sum(comb(m, k) for k in range(need, m + 1)) / 2**m
        print(f"    m={m:3d}  need {need:3d}/{m:3d}  p = {p:.6f}")

    # power: how wrong can a ruler be and still pass?
    print("\n  Monte Carlo power: ruler = hand-read x 10^N(0,sigma) per ARTIST")
    for sigma in (0.2, 0.3, 0.5, 0.75, 1.0, 1.5):
        passes = 0
        trials = 20000
        rr = random.Random(7)
        for _ in range(trials):
            noisy = {a: np.log10(v) + rr.gauss(0, sigma) for a, v in hand.items()}
            ok = sum(
                1
                for a, b in pairs
                if (noisy[a] > noisy[b]) == (hand[a] > hand[b])
            )
            if ok / len(pairs) >= 0.9:
                passes += 1
        print(f"    sigma={sigma:4.2f} decades  P(FAM-4 passes) = {passes/trials:.4f}")

    # per-artist single-error sensitivity
    print("\n  single-artist catastrophic error: if ONE artist is read at the")
    print("  wrong end of the scale, how many pairs flip, and does 90% survive?")
    for a in names:
        if deg[a] == 0:
            continue
        flipped = deg[a]
        ok = (len(pairs) - flipped) / len(pairs)
        print(f"    {a:36s} flips {flipped:2d} -> {ok:.1%} "
              f"{'PASS' if ok >= 0.9 else 'FAIL'}")


if __name__ == "__main__":
    main()
