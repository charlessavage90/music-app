"""`CXR-M4` — does the fame ruler COMPRESS, and where?

Follow-up to `cxr_census.py`, which refuted `CXR-P1`'s premise and confirmed its
consequence: 99.9% of the ~29,900 newly added artists carry a measured listener count,
and the artists present in both maps rose a median +0.079 on the fame percentile.

A uniform rise would cost the router nothing — Dijkstra compares differences, and a
constant added to every interior node is a hop toll, not a change of preference. What
would hurt is a rise that is LARGER IN THE MIDDLE THAN AT THE TOP, because that squeezes
the gap between "somebody you might not know" and "somebody everybody knows" — and that
gap is the entire signal the `known` ramp steers on after the obscurity floor is spent
around press five.

This measures the shift against the artist's position in the OLD frame, and then prices
the squeeze in the ramp's own units.

    cd api && UV_LINK_MODE=copy uv run python \
      ../builder/analysis/2026-09-01-cxr-regression-diagnosis/cxr_compression.py

Descriptive only. Nothing is adopted and no criterion is fixed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore

SCRATCH = Path(__file__).resolve().parents[3] / "builder" / "scratch"
OLD = SCRATCH / "graph-msw-tu50.bin"
NEW = SCRATCH / "graph-cxa-adopted.bin"


def main() -> None:
    old = GraphStore.load(OLD)
    new = GraphStore.load(NEW)
    cfg = ApiConfig()

    old_ids = {m: i for i, m in enumerate(old.mbids)}
    common = [m for m in new.mbids if m in old_ids]
    new_ids = {m: i for i, m in enumerate(new.mbids)}

    p_old = old.fame_lb_pctl[np.array([old_ids[m] for m in common])]
    p_new = new.fame_lb_pctl[np.array([new_ids[m] for m in common])]

    print("=" * 74)
    print("CXR-M4  fame-percentile shift by the artist's position in the OLD frame")
    print("=" * 74)
    print(f"{'old band':<14}{'n':>8}{'old mean':>10}{'new mean':>10}{'shift':>9}")
    edges = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99, 1.0001]
    for lo, hi in zip(edges, edges[1:]):
        m = (p_old >= lo) & (p_old < hi)
        if not m.any():
            continue
        print(
            f"{f'{lo:.2f}-{hi:.2f}':<14}{int(m.sum()):>8,}"
            f"{p_old[m].mean():>10.4f}{p_new[m].mean():>10.4f}"
            f"{(p_new[m] - p_old[m]).mean():>+9.4f}"
        )

    print()
    print("=" * 74)
    print("CXR-M4  the squeeze, priced in the ramp's own units")
    print("=" * 74)
    # The ramp adds  w_known_ramp_fame_pctl * n_known * fame_pctl[v]  per interior
    # node. What steers the router is the DIFFERENCE between two candidates, so
    # price the gap between a typical mid-tier artist and a typical famous one.
    w = cfg.w_known_ramp_fame_pctl
    print(f"w_known_ramp_fame_pctl = {w}   (ApiConfig, cited not restated elsewhere)")

    def band_mean(p: np.ndarray, mask: np.ndarray) -> float:
        return float(p[mask].mean())

    mid = (p_old >= 0.40) & (p_old < 0.60)
    famous = p_old >= 0.99
    gap_old = band_mean(p_old, famous) - band_mean(p_old, mid)
    gap_new = band_mean(p_new, famous) - band_mean(p_new, mid)
    print(
        f"\ngap between a top-1% artist and a mid-scale one:"
        f"\n  old frame {gap_old:.4f}    new frame {gap_new:.4f}"
        f"    ({100.0 * (gap_new - gap_old) / gap_old:+.1f}%)"
    )
    for n_known in (5, 10, 20):
        print(
            f"  at {n_known:>2} presses the router's preference for the mid-scale"
            f" artist is worth {w * n_known * gap_old:.5f} old,"
            f" {w * n_known * gap_new:.5f} new"
        )

    # Where the ceiling bites: an artist already at 1.0 cannot rise.
    ceiling = p_old >= 0.999
    print(
        f"\nartists already at the top of the old frame (n={int(ceiling.sum()):,}): "
        f"mean shift {(p_new[ceiling] - p_old[ceiling]).mean():+.4f}"
    )

    # And the other half of the story: the newly added artists are cheap under the
    # ramp but thin in the graph. Price both facts on the same population.
    added_idx = np.array(
        [i for i, m in enumerate(new.mbids) if m not in old_ids], dtype=np.int64
    )
    deg_new = np.diff(new.offsets).astype(np.int64)
    print()
    print("=" * 74)
    print("CXR-M5  the added artists: cheap to want, expensive to reach")
    print("=" * 74)
    print(
        f"added artists' fame percentile: median "
        f"{np.median(new.fame_lb_pctl[added_idx]):.4f}   "
        f"vs pre-existing "
        f"{np.median(new.fame_lb_pctl[np.array([new_ids[m] for m in common])]):.4f}"
    )
    print(
        f"added artists' degree:          median {np.median(deg_new[added_idx]):.0f}"
        f"          vs pre-existing "
        f"{np.median(deg_new[np.array([new_ids[m] for m in common])]):.0f}"
    )
    # A node reachable only through one edge cannot sit in the MIDDLE of a journey
    # at all: a journey enters and leaves every interior artist.
    deg1 = deg_new[added_idx] <= 1
    print(
        f"\nadded artists with degree <= 1: {int(deg1.sum()):,} "
        f"({100.0 * deg1.mean():.2f}%) -- these cannot be an interior card at all,"
        f"\nbecause a journey enters and leaves every artist in the middle."
    )
    common_deg1 = deg_new[np.array([new_ids[m] for m in common])] <= 1
    print(
        f"the same figure for pre-existing artists: {int(common_deg1.sum()):,} "
        f"({100.0 * common_deg1.mean():.2f}%)"
    )


if __name__ == "__main__":
    main()
