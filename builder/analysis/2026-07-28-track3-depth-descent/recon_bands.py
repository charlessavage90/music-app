"""DD-P2 reconnaissance: band structure and the Track 2 carry-over candidates.

NOT the pair draw. This measures what the seeded rule will be drawing from, so the
band edges and the "4 Track 2 analysis pairs with famous endpoints" carry-over are
decided against the artifact rather than assumed. Read-only.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/recon_bands.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

FAMOUS_MIN = 0.90          # DD-P1's top decile, used as the band edge
MID_LO, MID_HI = 0.50, 0.90


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore

    from mirror import MirrorContext
    from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    pctl = ctx.pctl
    n = len(store.mbids)
    degree = np.diff(store.offsets)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    print(f"N = {n:,}   E = {len(store.neighbours):,}")
    print(f"degree: min {degree.min()}  median {np.median(degree):.0f}  max {degree.max()}")
    print(f"degree-1 nodes: {int((degree == 1).sum()):,} "
          f"({100.0 * (degree == 1).mean():.2f} %)\n")

    famous = pctl >= FAMOUS_MIN
    mid = (pctl >= MID_LO) & (pctl < MID_HI)
    print(f"band sizes at the pre-registered edges:")
    print(f"  famous (pctl >= {FAMOUS_MIN}): {int(famous.sum()):,}")
    print(f"  mid    (pctl in [{MID_LO}, {MID_HI})): {int(mid.sum()):,}")
    print(f"  mid, excluding degree-1: {int((mid & (degree > 1)).sum()):,}\n")

    print("--- Track 2 pairs, endpoint percentiles (carry-over candidates) ---")
    for label, pairs in (("analysis", ANALYSIS_PAIRS), ("held-out", HELD_OUT_PAIRS)):
        print(f"\n{label}:")
        for a, b in pairs:
            ia, ib = by_name.get(a), by_name.get(b)
            if ia is None or ib is None:
                print(f"  {a} -> {b}: MISSING ENDPOINT")
                continue
            both = "BOTH-FAMOUS" if (famous[ia] and famous[ib]) else ""
            print(f"  {a:<20} -> {b:<16} "
                  f"pctl {pctl[ia]:.4f} / {pctl[ib]:.4f}   "
                  f"deg {degree[ia]:>3} / {degree[ib]:>3}   {both}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
