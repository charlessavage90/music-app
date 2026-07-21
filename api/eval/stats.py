"""Paired significance testing for arm-vs-control comparisons.

Every arm routes the SAME endpoint pairs, so per-pair measurements are strongly
correlated. Comparing aggregate means discards that pairing and most of the
power with it. Wilcoxon signed-rank on per-pair deltas is the non-parametric
paired test, which matters because these metrics are heavily skewed.

Holm correction because each metric is compared across several arms; without it
the chance of one arm looking significant by luck rises with the arm count.
"""

from __future__ import annotations

from scipy.stats import wilcoxon


def paired_comparison(control: list[float], candidate: list[float]) -> dict:
    """Wilcoxon signed-rank on per-pair deltas (candidate - control)."""
    if len(control) != len(candidate):
        raise ValueError("control and candidate must be the same length")
    deltas = [b - a for a, b in zip(control, candidate)]
    n = len(deltas)
    ordered = sorted(deltas)
    median = (
        0.0
        if n == 0
        else ordered[n // 2]
        if n % 2
        else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    )
    if n == 0 or all(d == 0 for d in deltas):
        return {"n": n, "median_delta": 0.0, "p_value": 1.0}
    _, p = wilcoxon(candidate, control, zero_method="zsplit")
    return {"n": n, "median_delta": float(median), "p_value": float(p)}


def holm_correct(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni step-down correction. Returns values in input order."""
    m = len(p_values)
    if m == 0:
        return []
    indexed = sorted(enumerate(p_values), key=lambda pair: pair[1])
    corrected = [0.0] * m
    running = 0.0
    for rank, (original_index, p) in enumerate(indexed):
        adjusted = min(1.0, p * (m - rank))
        running = max(running, adjusted)  # enforce monotonicity
        corrected[original_index] = running
    return corrected
