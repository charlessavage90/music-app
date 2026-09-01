import math

import numpy as np
import pytest

from artistpath_builder.pipeline import rescale_scores


def test_p99_log_clip_reproduces_the_legacy_expression_exactly():
    # Byte-identity for the control arm. The legacy expression is
    # min(1, log1p(v) / log1p(p99)), with p99 computed in RAW space —
    # np.percentile with linear interpolation does not commute with log1p.
    #
    # Repaired for Task 14: this test was written under Task 13's contract,
    # where rescale_scores's p99_log_clip branch received RAW co-occurrence
    # values directly. Task 14 changes every caller to pass LOG-SPACE values
    # (log1p(cooc) from damped_strength at d=0) and the branch now `expm1`s
    # its input back to raw before reproducing the legacy expression — that
    # is the whole point of Task 14's Step 4. Feeding this test raw integers
    # 1..200 as if they were still the branch's raw-space input (the old
    # fixture) now means log1p(200) ~= 5.3 gets treated as a co-occurrence
    # count and expm1'd back to ~= 199, silently exercising a completely
    # different part of the value range than intended — which is exactly
    # what produced the observed failure (got[0] = 0.00505... instead of
    # 0.13094...): raw=1.0 in the old fixture is now interpreted as
    # log1p(cooc)=1.0, i.e. cooc = expm1(1.0) ~= 1.718, not cooc = 1.0.
    #
    # Fixed by feeding log-space input (log1p of the raw series) and keeping
    # the expected value's derivation anchored to the RAW series, matching
    # how build_from_archive -> damped_strength -> rescale_scores actually
    # composes at d=0.
    raw = [float(i) for i in range(1, 201)]
    values = [math.log1p(v) for v in raw]
    scale = float(np.percentile(raw, 99))
    expected = [min(1.0, math.log1p(v) / math.log1p(scale)) for v in raw]
    got = rescale_scores(values, strategy="p99_log_clip", damping=0.0)
    assert got == pytest.approx(expected, abs=0.0)


def test_rescale_never_emits_nan_or_all_zero():
    # The degeneracy guard. Dropping the centring under the clip rescale
    # clamps 99.98% of edges at d=0.5 and makes p99(raw) == 0, which emits nan.
    # That must fail loudly, never ship silently.
    for damping in (0.0, 0.25, 0.5, 0.75, 1.0):
        got = rescale_scores(
            [float(i) for i in range(1, 101)],
            strategy="p99_log_clip",
            damping=damping,
        )
        assert not any(math.isnan(g) for g in got), damping
        assert any(g > 0.0 for g in got), damping


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="unsupported rescale strategy"):
        rescale_scores([1.0], strategy="nope", damping=0.0)


def test_percentile_rank_was_deleted_and_raises():
    # Phase 2 spec §8 risk 4 / revised plan C-4: the losing option is deleted,
    # not left as a permanently supported mode. percentile_rank lost the blind
    # listening test (execution log §16) and its implementation was removed.
    # A sweep script or stale config naming it must fail loudly rather than
    # silently fall through to the surviving strategy.
    with pytest.raises(ValueError, match="percentile_rank"):
        rescale_scores([1.0, 2.0], strategy="percentile_rank", damping=0.0)


def test_p99_log_clip_raises_on_degenerate_scale():
    # The degeneracy guard itself. All-zero input drives p99 to exactly 0,
    # which without this raise would divide log1p(v) by log1p(0) == 0 and
    # emit nan for every edge — silently destroying the signal the router
    # uses. It must fail loudly instead.
    with pytest.raises(ValueError, match="degenerate p99"):
        rescale_scores(
            [0.0] * 100, strategy="p99_log_clip", damping=0.5
        )


def test_rescale_logs_the_scale_and_the_saturated_share(caplog):
    # CEX-M1: the p99 scale is population-dependent and prices the router's
    # primary term. Comparing two builds needs it as a figure, not a guess.
    import logging

    from artistpath_builder.pipeline import rescale_scores

    # Input is LOG-SPACE (log1p(cooc) from damped_strength at d=0) because
    # that is what every caller passes since Task 14 — the branch expm1s it
    # back to raw. Feeding raw 1000.0 here overflows float on expm1(1000),
    # which is what the value below is avoiding.
    raw = [1.0] * 99 + [1000.0]
    with caplog.at_level(logging.INFO, logger="artistpath_builder.pipeline"):
        rescaled = rescale_scores(
            [math.log1p(v) for v in raw], strategy="p99_log_clip", damping=0.0
        )

    # The population is chosen so exactly one edge saturates: p99 of the raw
    # values interpolates well below 1000, so the top edge clips at 1.0.
    assert rescaled[-1] == 1.0
    assert sum(1 for v in rescaled if v >= 1.0) == 1

    messages = " ".join(record.getMessage() for record in caplog.records)
    assert "p99" in messages
    assert "saturated" in messages
