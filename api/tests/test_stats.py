import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from stats import holm_correct, paired_comparison  # noqa: E402


def test_paired_comparison_detects_a_consistent_improvement():
    control = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    candidate = [c + 0.05 for c in control]
    result = paired_comparison(control, candidate)
    assert result["n"] == 8
    assert result["median_delta"] == pytest.approx(0.05, abs=1e-9)
    assert result["p_value"] < 0.05


def test_paired_comparison_finds_no_effect_when_there_is_none():
    control = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    candidate = [0.11, 0.19, 0.31, 0.39, 0.51, 0.59, 0.71, 0.79]
    assert paired_comparison(control, candidate)["p_value"] > 0.05


def test_identical_inputs_yield_p_value_one():
    values = [0.1, 0.2, 0.3, 0.4, 0.5]
    result = paired_comparison(values, values)
    assert result["median_delta"] == 0.0
    assert result["p_value"] == 1.0


def test_mismatched_lengths_are_rejected():
    with pytest.raises(ValueError, match="same length"):
        paired_comparison([1.0, 2.0], [1.0])


def test_holm_correction_is_monotone_and_bounded():
    corrected = holm_correct([0.01, 0.02, 0.03])
    assert corrected == sorted(corrected)
    assert all(0.0 <= p <= 1.0 for p in corrected)
    # Smallest p gets the largest multiplier (x3 here).
    assert corrected[0] == pytest.approx(0.03)


def test_holm_correction_preserves_input_order():
    corrected = holm_correct([0.03, 0.01])
    assert corrected[1] < corrected[0]
