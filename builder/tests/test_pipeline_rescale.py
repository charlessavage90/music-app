import math

import numpy as np
import pytest

from artistpath_builder.pipeline import rescale_scores


def test_p99_log_clip_reproduces_the_legacy_expression_exactly():
    # Byte-identity for the control arm. The legacy expression is
    # min(1, log1p(v) / log1p(p99)), with p99 computed in RAW space —
    # np.percentile with linear interpolation does not commute with log1p.
    values = [float(i) for i in range(1, 201)]
    scale = float(np.percentile(values, 99))
    expected = [min(1.0, math.log1p(v) / math.log1p(scale)) for v in values]
    got = rescale_scores(values, strategy="p99_log_clip", damping=0.0)
    assert got == pytest.approx(expected, abs=0.0)


def test_percentile_rank_is_uniform_and_has_no_ceiling_tie_mass():
    values = [float(i) for i in range(1, 1001)]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.0)
    assert min(got) >= 0.0 and max(got) <= 1.0
    # A rank transform has at most one value at the ceiling, unlike the clip
    # which saturates ~1% of edges by construction.
    assert sum(1 for g in got if g >= 1.0) <= 1
    assert 0.45 <= float(np.median(got)) <= 0.55


def test_percentile_rank_preserves_ordering():
    values = [5.0, 1.0, 3.0, 9.0]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.0)
    assert sorted(range(4), key=lambda i: values[i]) == sorted(
        range(4), key=lambda i: got[i]
    )


def test_percentile_rank_handles_negative_values():
    # Damping in log space produces negatives. A rank transform handles them;
    # the clamp this replaces collapsed them all into one tie at the floor.
    values = [-3.0, -1.0, 0.0, 2.0]
    got = rescale_scores(values, strategy="percentile_rank", damping=0.5)
    assert all(0.0 <= g <= 1.0 for g in got)
    assert got[0] < got[1] < got[2] < got[3]


def test_rescale_never_emits_nan_or_all_zero():
    # The degeneracy guard. Dropping the centring under the clip rescale
    # clamps 99.98% of edges at d=0.5 and makes p99(raw) == 0, which emits nan.
    # That must fail loudly, never ship silently.
    for strategy in ("p99_log_clip", "percentile_rank"):
        for damping in (0.0, 0.25, 0.5, 0.75, 1.0):
            got = rescale_scores(
                [float(i) for i in range(1, 101)], strategy=strategy, damping=damping
            )
            assert not any(math.isnan(g) for g in got), (strategy, damping)
            assert any(g > 0.0 for g in got), (strategy, damping)


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="unknown rescale strategy"):
        rescale_scores([1.0], strategy="nope", damping=0.0)


def test_p99_log_clip_raises_on_degenerate_scale():
    # The degeneracy guard itself. All-zero input drives p99 to exactly 0,
    # which without this raise would divide log1p(v) by log1p(0) == 0 and
    # emit nan for every edge — silently destroying the signal the router
    # uses. It must fail loudly instead.
    with pytest.raises(ValueError, match="degenerate p99"):
        rescale_scores(
            [0.0] * 100, strategy="p99_log_clip", damping=0.5
        )
