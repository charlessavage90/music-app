"""Tests for the `JFX-` statistics module.

**Every test here was shown RED before being kept** — against the unwrapped frozen
estimator for the units, against a naive per-step band for the multiplicity fix, and
against a shared RNG for the seeding. A green test that has never failed is not evidence
(`memory/working-style.md`).

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q \\
      analysis/2026-08-09-jfx-prereg-critique/test_jfx_stats.py`
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "analysis/2026-08-05-unlistenable-class"))

import jfx_stats as J  # noqa: E402
from ulc_exposure import paired_median_ci as frozen_ci  # noqa: E402


# --- AM1.10: the units bug the wrapper exists to fix -----------------------

def test_frozen_estimator_really_does_report_hundredfold():
    """The defect is real. If this ever fails, the wrapper is now pointless."""
    diffs = [1200.0, -300.0, 800.0, 50.0, 2000.0]
    raw = frozen_ci(list(diffs), random.Random(1))
    assert raw["median_diff_pp"] == pytest.approx(80000.0)
    # ...while the true median difference is 800.
    assert sorted(diffs)[len(diffs) // 2] == pytest.approx(800.0)


def test_wrapper_reports_true_units():
    diffs = [1200.0, -300.0, 800.0, 50.0, 2000.0]
    out = J.paired_median_ci(diffs, random.Random(1))
    assert out["median_diff"] == pytest.approx(800.0)
    assert "median_diff_pp" not in out and "ci95_pp" not in out


def test_wrapper_resampling_is_bit_for_bit_the_frozen_one():
    diffs = [0.3, -0.1, 0.22, 0.05, 0.4, -0.02, 0.11]
    a = J.paired_median_ci(diffs, random.Random(7))
    b = frozen_ci(list(diffs), random.Random(7))
    assert a["median_diff"] == pytest.approx(b["median_diff_pp"] / 100.0)
    assert a["ci95"][0] == pytest.approx(b["ci95_pp"][0] / 100.0)
    assert a["ci95"][1] == pytest.approx(b["ci95_pp"][1] / 100.0)


# --- AM1.2: the log ruler --------------------------------------------------

def test_log_fame_is_proportional_not_absolute():
    """Equal FOLD changes give equal log distances; equal absolute ones do not."""
    assert J.log_fame(10_000) - J.log_fame(1_000) == pytest.approx(
        J.log_fame(100_000) - J.log_fame(10_000), abs=1e-3
    )
    # the same absolute drop of 900 is worth very different amounts
    near_top = J.log_fame(100_000) - J.log_fame(99_100)
    near_bottom = J.log_fame(1000) - J.log_fame(100)
    assert near_bottom > 100 * near_top


def test_the_plus_one_distortion_is_bounded_and_only_bites_at_tiny_counts():
    """`AM1.2` claims the `1 +` guard's distortion is negligible at the values
    in play. That is TRUE above ~1,000 listeners and FALSE at the very bottom,
    so it is pinned here rather than left as an adjective.

    The artifact's median is 2,305 and its 10th-percentile cut is 21,268, so
    the material region is well inside the negligible band. Journeys CAN reach
    single-digit-listener artists, where a decade of log distance is off by
    ~3%; that is a known and accepted approximation, not a silent one.
    """
    def decade(v):
        return J.log_fame(v * 10) - J.log_fame(v)

    assert decade(1_000) == pytest.approx(1.0, abs=1e-3)     # negligible
    assert decade(10_000) == pytest.approx(1.0, abs=1e-4)
    assert decade(100) == pytest.approx(1.0, abs=5e-3)
    # the bottom of the range, where it genuinely bites — bounded, not zero
    assert 0.95 < decade(10) < 1.0
    assert 0.7 < decade(1) < 0.95


def test_log_fame_preserves_null_and_handles_zero():
    assert J.log_fame(None) is None          # FAM-AM1.8: never coerced
    assert J.log_fame(0) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        J.log_fame(-1)


def test_log_fame_is_monotone():
    values = [0, 1, 5, 100, 2305, 21268, 455551]
    logged = [J.log_fame(v) for v in values]
    assert logged == sorted(logged)


# --- AM1.10: seeding is order-independent ----------------------------------

def test_seeded_is_stable_and_name_dependent():
    assert J.seeded("C1@d20").random() == J.seeded("C1@d20").random()
    assert J.seeded("C1@d20").random() != J.seeded("C1@d10").random()


def test_seeding_makes_results_independent_of_call_order():
    """Each statistic has its OWN data, which is the real situation: three
    depths are three different samples. A shared RNG then makes each result
    depend on how many draws the statistics before it consumed."""
    rng = random.Random(4242)
    data = {
        f"C1@d{d}": [rng.gauss(0.1, 0.5) for _ in range(40)]
        for d in (0, 5, 20)
    }
    names = list(data)

    forward = {n: J.paired_median_ci(data[n], J.seeded(n)) for n in names}
    backward = {n: J.paired_median_ci(data[n], J.seeded(n)) for n in reversed(names)}
    assert forward == backward

    # Reproducible from the NAME alone, with no harness state involved.
    assert J.paired_median_ci(data["C1@d5"], J.seeded("C1@d5")) == forward["C1@d5"]


def test_shared_rng_order_dependence_is_REAL_but_negligible_at_10k():
    """The honest version of the `AM1.10` claim, after it was overstated.

    The amendment first said a shared RNG would "silently change every later
    interval". **It does not, at the settings in play** — the bootstrap
    distribution of a median over n=40 is highly discrete and 10,000
    replicates converge the percentiles onto the same order statistics
    whatever the RNG offset. Measured below.

    The mechanism is nonetheless real, and shows up once the replicate count
    is low enough for sampling noise to survive. So `seeded()` is kept for
    reproducibility, NOT because it repairs a live defect.
    """
    rng = random.Random(4242)
    data = {f"d{d}": [rng.gauss(0.1, 0.5) for _ in range(40)] for d in (0, 5, 20)}
    names = list(data)

    # (a) at the production replicate count: order changes nothing.
    shared = random.Random(1)
    fwd = {n: frozen_ci(list(data[n]), shared) for n in names}
    shared2 = random.Random(1)
    bwd = {n: frozen_ci(list(data[n]), shared2) for n in reversed(names)}
    assert fwd == bwd, "if this ever fails, AM1.10's negligibility claim is stale"

    # (b) the mechanism exists — drop the replicate count and it appears.
    import ulc_exposure

    original = ulc_exposure.BOOTSTRAP
    try:
        ulc_exposure.BOOTSTRAP = 50
        shared3 = random.Random(1)
        fwd_small = {n: frozen_ci(list(data[n]), shared3) for n in names}
        shared4 = random.Random(1)
        bwd_small = {n: frozen_ci(list(data[n]), shared4) for n in reversed(names)}
        assert fwd_small != bwd_small, (
            "order dependence did not reproduce even at 50 replicates — "
            "this test is vacuous and AM1.10's rationale needs re-checking"
        )
    finally:
        ulc_exposure.BOOTSTRAP = original


# --- AM1.5: the G1b contrast ----------------------------------------------

@pytest.mark.parametrize("d_b,d_a", [(0.67, 1.0), (0.8, 1.0), (0.5, 1.0), (0.4, 0.5)])
def test_contrast_agrees_with_the_ratio_when_denominator_positive(d_b, d_a):
    """T >= 0 iff ratio >= 0.67. Same bar, bounded statistic."""
    assert (J.g1b_contrast(d_b, d_a) >= 0) == ((d_b / d_a) >= 0.67)


def test_contrast_is_bounded_where_the_ratio_explodes():
    """The failure the reparameterisation exists to avoid."""
    tiny_denominator = 1e-9
    ratio = 0.5 / tiny_denominator
    assert ratio > 1e8                      # ratio is unusable
    assert abs(J.g1b_contrast(0.5, tiny_denominator)) < 1.0   # contrast is fine


# --- AM1.6: the simultaneous band actually widens --------------------------

def _flat_gradient_steps(rng, n=100):
    """Three consecutive steps of a truly FLAT gradient — no real change."""
    return [
        {"s1": rng.gauss(0, 1), "s2": rng.gauss(0, 1), "s3": rng.gauss(0, 1)}
        for _ in range(n)
    ]


def test_simultaneous_band_is_wider_than_per_step():
    rng = random.Random(20260809)
    pairs = _flat_gradient_steps(rng)

    def stats(sample):
        return {k: J._median([r[k] for r in sample]) for k in ("s1", "s2", "s3")}

    point = stats(pairs)
    draws = J.joint_bootstrap(pairs, random.Random(1), stats, reps=400)
    band = J.simultaneous_band(draws, point)
    for key in ("s1", "s2", "s3"):
        per_step = J.two_sided(draws[key])
        assert (band[key][1] - band[key][0]) > (per_step[1] - per_step[0])


def test_simultaneous_band_cuts_the_false_stop_rate():
    """The claim `AM1.6` rests on, demonstrated rather than asserted.

    Under a truly flat gradient, the per-step rule fires more often than the
    simultaneous one. This is the RED/GREEN pair for the multiplicity fix.
    """
    naive_fires = simultaneous_fires = 0
    trials = 60
    for t in range(trials):
        rng = random.Random(1000 + t)
        pairs = _flat_gradient_steps(rng, n=60)

        def stats(sample):
            return {k: J._median([r[k] for r in sample]) for k in ("s1", "s2", "s3")}

        point = stats(pairs)
        draws = J.joint_bootstrap(pairs, random.Random(t), stats, reps=250)
        band = J.simultaneous_band(draws, point)
        if any(J.two_sided(draws[k])[0] > 0 for k in ("s1", "s2", "s3")):
            naive_fires += 1
        if any(band[k][0] > 0 for k in ("s1", "s2", "s3")):
            simultaneous_fires += 1
    assert simultaneous_fires <= naive_fires
    assert simultaneous_fires < trials * 0.15


# --- AM1.5: the joint bootstrap keeps the arms paired ----------------------

def test_joint_bootstrap_resamples_pairs_not_values():
    """Both arms must move together, or the correlation that makes the
    contrast cheap is destroyed."""
    pairs = [{"a": float(i), "b": float(i) + 10.0} for i in range(50)]

    def stats(sample):
        return {
            "a": J._median([r["a"] for r in sample]),
            "b": J._median([r["b"] for r in sample]),
        }

    draws = J.joint_bootstrap(pairs, random.Random(3), stats, reps=300)
    # b is a is +10 in EVERY record, so the invariant must survive resampling.
    for i in range(300):
        assert draws["b"][i] - draws["a"][i] == pytest.approx(10.0)


def test_joint_bootstrap_rejects_empty_input():
    with pytest.raises(ValueError):
        J.joint_bootstrap([], random.Random(0), lambda s: {}, reps=10)


# --- AM1.7: the branch-trigger effect sizes exist and are numbers ----------

def test_branch_trigger_effect_sizes_are_pinned():
    assert J.C6_FLOOR_FIRE_PP == 5.0
    assert J.C7_NULL_SHARE_PP == 2.0
    assert J.STEP_RISE_EFFECT_LOG10 == 0.02
    # ~4.7% in listener count, the plain-language figure AM1.6 quotes.
    assert (10 ** J.STEP_RISE_EFFECT_LOG10 - 1) == pytest.approx(0.047, abs=0.001)


# --- the import path itself, which had no consumer to exercise it ----------

def test_jfx_stats_imports_with_only_its_own_directory_on_the_path():
    """`jfx_stats` must resolve the frozen ULC- estimator BY ITSELF.

    Shown red before being kept: the module computed `ROOT` as `parents[2]` of the
    FILE (= `builder/`) and inserted `builder/builder/analysis/...`, which does not
    exist. Every test above passed anyway, because THIS FILE inserts the ULC- path
    at line 22 before importing — so the module's own line was dead in the only
    context that ever ran it.

    A subprocess with a clean `sys.path` is what makes this a real check: importing
    it here could never fail once the test module has already fixed the path.
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, "-c", "import jfx_stats; print(jfx_stats.SEED_NAMESPACE)"],
        cwd=str(HERE), capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"jfx_stats cannot import on its own:\n{result.stderr}"
    )
    assert "JFX-20260809" in result.stdout
