"""TD-3: what the MEDIAN swap count hides when the reranker is silent.

`TAS-4`'s bar is a median over artists whose candidate list exceeds 50. The
prereg's own `TAS-1` expects genre labels to be present unevenly, and §1's
neutral rule makes the reranker inert wherever labels are missing. So the
realistic swap distribution is zero-inflated: a share `f` of artists reorder,
the rest do not move at all.

This arm holds the per-artist swap size fixed at `n` and varies only `f`, the
share of binding artists the reranker actually touches. One column moves.
It answers whether the median is a safe summary of the quantity `TAS-4` is
trying to bound.

Reuses td_turnover.py wholesale (Capture, mask/score helpers, the same green
instrument check upstream). Nothing is built.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/td_coverage.py --capture <npz>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from td_turnover import (  # noqa: E402
    K,
    Capture,
    mutual_undirected,
    score,
    uniform_field,
)


def mask_partial(cap: Capture, n_swap: int, frac: float, window: int,
                 seed: int) -> np.ndarray:
    """W10-SYM-n applied to a hash-chosen `frac` of the binding nodes."""
    mask = cap.pos < K
    field = uniform_field(cap.s_node, cap.s_cand, cap.n, seed, True)
    rng = np.random.default_rng(seed)
    binding = np.flatnonzero(cap.binds)
    active = binding[rng.random(binding.size) < frac]
    off = cap.offsets
    for u in active:
        a, b = off[u], off[u + 1]
        L = b - a
        dpool = np.arange(max(0, K - window), K)
        ppool = np.arange(K, min(L, K + window))
        m = min(n_swap, dpool.size, ppool.size)
        if m == 0:
            continue
        fd = field[a + dpool]
        fp = field[a + ppool]
        mask[a + dpool[np.argsort(fd, kind="stable")[:m]]] = False
        mask[a + ppool[np.argsort(-fp, kind="stable")[:m]]] = True
    return mask


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--out", default=str(HERE / "td_coverage.json"))
    args = ap.parse_args()

    cap = Capture(Path(args.capture))
    base_mask = cap.pos < K
    base_edges = mutual_undirected(cap, base_mask)

    rows = []
    for n_swap in (2, 5):
        for frac in (0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0):
            r = score(cap, base_mask, base_edges,
                      mask_partial(cap, n_swap, frac, 10, 909),
                      f"W10-SYM-n{n_swap}-f{frac}")
            r["n_swap"] = n_swap
            r["active_share"] = frac
            rows.append(r)
            print(f"n={n_swap} f={frac} done", flush=True)

    Path(args.out).write_text(json.dumps({"arms": rows}, indent=2),
                              encoding="utf-8")
    print("{:<24}{:>7}{:>8}{:>9}{:>9}{:>9}".format(
        "arm", "median", "mean", "lost%", "gain%", "turn%"))
    for r in rows:
        print("{:<24}{:>7.1f}{:>8.3f}{:>9.3f}{:>9.3f}{:>9.3f}".format(
            r["arm"], r["median_swaps_binding"], r["mean_swaps_binding"],
            100 * r["lost_frac"], 100 * r["gained_frac"],
            100 * r["turnover_frac"]))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
