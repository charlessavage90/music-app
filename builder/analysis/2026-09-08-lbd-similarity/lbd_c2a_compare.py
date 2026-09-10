"""`LBD-` Task 4 — the `LBD-G2` comparison between arms, from the per-artist degrees.

Reads the `c2a.degrees.json` each `lbd_reads.py --mode c2a` run writes and computes, per
arm against `LBD-A0` (the baseline for every arm, pre-registration §0):

  * the share of the added set at <= 2 partners, per arm, and its difference from A0 in
    percentage points -- `LBD-G2`'s pair-table effect size is >= 1 pp;
  * the paired sign test over the fixed 29,892: how many artists gained partners, lost, or
    were unchanged, with a two-sided binomial p on gained vs lost;
  * the same, stratified by the `LBD-AM1` residual set and its complement (a reporting
    requirement, no gate of its own), so `R12` can be read side by side;
  * the pre-existing set as the within-arm reference, for `R9`'s shape (graph-level only,
    but reported here so the pair-table figures carry it too).

    cd <worktree> && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 \\
      uv run python -u builder/analysis/2026-09-08-lbd-similarity/lbd_c2a_compare.py \\
        --pairs-root C:/unsung-fast/lbd-pairs
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

INPUTS = Path(r"D:\unsung-large-data\lbd-inputs")
RESIDUAL = INPUTS / "cxr_residual_mbids.txt"
ARMS = ("A0", "A1", "A2", "A3")


def binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided sign-test p for k successes of n at p=0.5 (ties excluded)."""
    if n == 0:
        return float("nan")
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def share_le2(d: dict[str, int]) -> float:
    return sum(1 for v in d.values() if v <= 2) / len(d)


def compare(base: dict[str, int], arm: dict[str, int]) -> dict:
    gained = sum(1 for m in base if arm[m] > base[m])
    lost = sum(1 for m in base if arm[m] < base[m])
    same = len(base) - gained - lost
    return {
        "n": len(base),
        "share_le_2": share_le2(arm),
        "delta_pp_vs_A0": (share_le2(arm) - share_le2(base)) * 100,
        "gained": gained, "lost": lost, "unchanged": same,
        "sign_test_p": binom_two_sided(gained, gained + lost),
        "share_absent": sum(1 for v in arm.values() if v == 0) / len(arm),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    out = args.out or args.pairs_root / "c2a_compare.json"

    residual = {l.strip() for l in RESIDUAL.read_text(encoding="utf-8").splitlines() if l.strip()}
    deg = {a: json.loads((args.pairs_root / a / "c2a.degrees.json").read_text(encoding="utf-8")) for a in ARMS}
    base_added, base_pre = deg["A0"]["added"], deg["A0"]["preexisting"]
    print(f"[compare] added {len(base_added):,}  residual {len(residual):,}  pre-existing {len(base_pre):,}")

    result = {}
    print("\n== added set (all 29,892), vs LBD-A0 — LBD-G2 pair-table bar: >= 1 pp on share <= 2")
    print("  arm   share<=2   delta pp   gained    lost  unchanged   sign-test p   absent")
    for a in ARMS:
        r = compare(base_added, deg[a]["added"])
        result.setdefault(a, {})["whole"] = r
        print(f"  {a}   {r['share_le_2']:.4f}   {r['delta_pp_vs_A0']:+7.2f}   {r['gained']:>6}  {r['lost']:>6}  {r['unchanged']:>9}   {r['sign_test_p']:.3g}   {r['share_absent']:.4f}")

    for name, keep in (("residual (LBD-AM1)", lambda m: m in residual), ("complement", lambda m: m not in residual)):
        print(f"\n== {name}")
        print("  arm   share<=2   delta pp   gained    lost  unchanged   sign-test p   absent")
        b = {m: v for m, v in base_added.items() if keep(m)}
        for a in ARMS:
            r = compare(b, {m: v for m, v in deg[a]["added"].items() if keep(m)})
            result[a][name] = r
            print(f"  {a}   {r['share_le_2']:.4f}   {r['delta_pp_vs_A0']:+7.2f}   {r['gained']:>6}  {r['lost']:>6}  {r['unchanged']:>9}   {r['sign_test_p']:.3g}   {r['share_absent']:.4f}")

    print("\n== pre-existing set (within-arm reference)")
    print("  arm   share<=2   delta pp   gained    lost  unchanged   sign-test p   absent")
    for a in ARMS:
        r = compare(base_pre, deg[a]["preexisting"])
        result[a]["preexisting"] = r
        print(f"  {a}   {r['share_le_2']:.4f}   {r['delta_pp_vs_A0']:+7.2f}   {r['gained']:>6}  {r['lost']:>6}  {r['unchanged']:>9}   {r['sign_test_p']:.3g}   {r['share_absent']:.4f}")

    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\n[compare] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
