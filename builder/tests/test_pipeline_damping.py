import math

import pytest

from artistpath_builder.pipeline import damped_strength


def test_damping_zero_is_plain_log1p():
    assert damped_strength(100.0, 1000.0, 2000.0, damping=0.0) == pytest.approx(
        math.log1p(100.0)
    )


def test_damping_subtracts_log_mass_in_log_space():
    # log1p(cooc) - d * (log m_a + log m_b)
    expected = math.log1p(100.0) - 0.5 * (math.log(1000.0) + math.log(2000.0))
    assert damped_strength(100.0, 1000.0, 2000.0, damping=0.5) == pytest.approx(
        expected
    )


def test_damping_penalises_the_popular_pair_more():
    # Same co-occurrence, different marginals: the popular pair must score lower.
    obscure = damped_strength(50.0, 100.0, 100.0, damping=0.5)
    popular = damped_strength(50.0, 10000.0, 10000.0, damping=0.5)
    assert obscure > popular


def test_negative_results_are_returned_not_clamped():
    # The clamp this replaces collapsed everything below zero into one tie at
    # the floor — the ceiling defect mirrored. The rank rescale handles
    # negatives natively.
    assert damped_strength(1.0, 100000.0, 100000.0, damping=1.0) < 0.0


def test_zero_mass_does_not_raise():
    assert math.isfinite(damped_strength(10.0, 0.0, 0.0, damping=0.5))
