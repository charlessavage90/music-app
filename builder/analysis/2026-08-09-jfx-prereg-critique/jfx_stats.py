"""`JFX-` statistics: the units fix, the log ruler, and the joint bootstrap.

**Governing document:** `docs/superpowers/specs/2026-08-09-journey-fame-exposure-preregistration.md`,
as amended by `JFX-AM1` — specifically `AM1.2` (log ruler), `AM1.5` (the `G1b` linear
contrast and the joint bootstrap), `AM1.6` (the simultaneous band) and `AM1.10` (units and
seeding). Where this module and the document disagree, **the document governs.**

**The frozen `ULC-` estimator is IMPORTED, never edited.** `paired_median_ci` is correct for
its own use and wrong for ours only in its units: it multiplies by 100 and names its outputs
`median_diff_pp` / `ci95_pp`, because `ULC-`'s statistic was a share. `JFX-`'s is a log
listener count, so as imported it reports a true difference of 0.30 as `30.0 "pp"`.

Two further properties of the frozen function that come along with the import and are pinned
here rather than discovered later:

- `BOOTSTRAP = 10_000` is a module global.
- It takes a **shared** `random.Random`, so in principle every result depends on **call
  order**. `seeded()` below removes that by deriving a per-statistic seed from the
  statistic's own NAME.

  **⚠ The order dependence is real but NEGLIGIBLE at the production replicate count, and
  saying otherwise was an overstatement this module's own test refused to support.** At
  10,000 replicates the bootstrap distribution of a median over n≈40 is discrete enough
  that forward and reverse call order give **identical** intervals; the effect reappears
  around 50 replicates. So `seeded()` is kept for **reproducibility from a name alone**,
  not because it repairs a live defect. `test_shared_rng_order_dependence_is_REAL_but_
  negligible_at_10k` asserts both halves and will fail if either stops holding.
"""
from __future__ import annotations

import hashlib
import math
import random
import statistics
import sys
from pathlib import Path

# parents[2] of the DIRECTORY, matching every sibling script here. It was
# parents[2] of the FILE, which resolves to `builder/` and built the nonexistent
# `builder/builder/analysis/...` — so this module could only ever be imported by
# `test_jfx_stats.py`, which happens to insert the ULC- path itself first. It had
# no other consumer, so nothing else ever executed this line. Found by writing the
# first one.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-05-unlistenable-class"))

from ulc_exposure import BOOTSTRAP, paired_median_ci as _frozen_paired_median_ci  # noqa: E402

#: Fixed for the whole `JFX-` run, so a seed is reproducible from a name alone.
SEED_NAMESPACE = "JFX-20260809"


def seeded(statistic_name: str) -> random.Random:
    """A `random.Random` whose seed is derived from the statistic's NAME.

    `AM1.10`. Makes every interval independent of call order, so adding or
    reordering a statistic cannot perturb another one's interval.
    """
    digest = hashlib.sha256(f"{SEED_NAMESPACE}:{statistic_name}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def log_fame(value: float | int | None) -> float | None:
    """The `AM1.2` ruler: `log10(1 + fame_lb)`. `None` passes through.

    A null is a MEASURED ABSENCE and must never be coerced to a floor
    (`FAM-AM1.8`) — callers exclude it, they do not substitute for it. The
    `1 +` guards a zero listener count, which is a legitimate non-null value
    distinct from a null; at the values in play the distortion is negligible.
    """
    if value is None:
        return None
    if value < 0:
        raise ValueError(f"negative listener count {value!r}")
    return math.log10(1.0 + float(value))


def paired_median_ci(diffs, rng):
    """`ULC-`'s estimator with `JFX-`'s units. `AM1.10`.

    The frozen function is called unchanged and its output rescaled, so the
    resampling is bit-for-bit the frozen one's.
    """
    raw = _frozen_paired_median_ci(list(diffs), rng)
    return {
        "n_pairs": raw["n_pairs"],
        "median_diff": raw["median_diff_pp"] / 100.0,
        "ci95": [raw["ci95_pp"][0] / 100.0, raw["ci95_pp"][1] / 100.0],
    }


def _median(xs) -> float:
    return statistics.median(xs)


def joint_bootstrap(per_pair, rng, statistics_fn, reps: int | None = None):
    """Resample PAIRS, carrying every arm and depth together. `AM1.5`.

    `per_pair` is one opaque record per pair holding that pair's values in both
    arms at all depths. Resampling the pair — not the individual differences —
    is what keeps the arms' correlation intact, and it is what makes the `G1b`
    contrast and the simultaneous band free rather than extra runs.

    `statistics_fn(sample) -> dict[str, float]` computes every statistic of
    interest on one resample. Returns `{name: sorted list of replicate values}`.
    """
    records = list(per_pair)
    n = len(records)
    if n == 0:
        raise ValueError("joint_bootstrap: no pairs")
    draws: dict[str, list[float]] = {}
    for _ in range(BOOTSTRAP if reps is None else reps):
        sample = [records[rng.randrange(n)] for _ in range(n)]
        for name, value in statistics_fn(sample).items():
            draws.setdefault(name, []).append(value)
    return {name: sorted(values) for name, values in draws.items()}


def one_sided_lower(draws: list[float], alpha: float = 0.05) -> float:
    """Lower bound of a one-sided `1 - alpha` percentile interval."""
    return draws[int(alpha * len(draws))]


def two_sided(draws: list[float], alpha: float = 0.05) -> list[float]:
    """Two-sided percentile interval, matching the frozen function's convention."""
    lo = draws[int((alpha / 2) * len(draws))]
    hi = draws[int((1 - alpha / 2) * len(draws)) - 1]
    return [lo, hi]


def g1b_contrast(drop_b: float, drop_a: float, bar: float = 0.67) -> float:
    """`T = D_B - bar * D_A`. `AM1.5`.

    For `D_A > 0`, `T >= 0` is algebraically identical to `D_B / D_A >= bar`,
    but `T` is a linear contrast and its bootstrap distribution is bounded,
    where the ratio's is not. **Report the ratio as a point estimate and the
    interval on `T`, never on the ratio.**
    """
    return drop_b - bar * drop_a


def simultaneous_band(step_draws: dict[str, list[float]], point: dict[str, float],
                      alpha: float = 0.05) -> dict[str, list[float]]:
    """Max-statistic simultaneous band over several steps. `AM1.6`.

    Three step tests plus an overall test at nominal coverage give a simulated
    false-stop rate of 7.5-8.2% against a nominal 5%. This restores family-wise
    5% using the observed correlation, so it is less conservative than
    Bonferroni and costs no extra runs — the replicates already exist.

    `step_draws` and `point` share keys. Returns a band per key.
    """
    names = sorted(step_draws)
    if not names:
        return {}
    n_reps = len(step_draws[names[0]])
    # Studentise by each step's own bootstrap spread, so one wide step does not
    # dominate the maximum purely through scale.
    spread = {}
    for name in names:
        draws = step_draws[name]
        lo, hi = two_sided(draws, alpha)
        spread[name] = max((hi - lo) / 4.0, 1e-12)
    max_dev = []
    for i in range(n_reps):
        max_dev.append(
            max(abs(step_draws[name][i] - point[name]) / spread[name] for name in names)
        )
    max_dev.sort()
    crit = max_dev[int((1 - alpha) * len(max_dev))]
    return {
        name: [point[name] - crit * spread[name], point[name] + crit * spread[name]]
        for name in names
    }


#: `AM1.6`. A step fails only if its simultaneous interval excludes zero AND
#: the rise is at least this, in log10 units (~4.7% in listener count).
STEP_RISE_EFFECT_LOG10 = 0.02

#: `AM1.7`. Branch-trigger effect sizes, in percentage points.
C6_FLOOR_FIRE_PP = 5.0
C7_NULL_SHARE_PP = 2.0
