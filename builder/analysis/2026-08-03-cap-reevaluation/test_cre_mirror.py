# test_cre_mirror.py -- the copy's own properties, and CRE-G2(b) shown able to go red
from __future__ import annotations

import numpy as np
import pytest

import cre_mirror
from cre_ladder import assert_cost_decomposition, journey
from cre_mirror import MirrorContext, SweepConfig, find_path_mirror, term_breakdown
from test_cre_ladder import FakeStore, ctx_for


def test_fame_ramp_off_is_identical_to_production():
    """CRE-G1(b)'s property in miniature: at w_known_ramp_fame_pctl = 0.0 the
    term is not merely zero, it is never added -- so the copy executes the
    frozen expression and returns the frozen path."""
    store = FakeStore()
    fame = [0.01, 0.99, 0.01, 0.99]  # would dominate if it were live
    ctx = ctx_for(store, fame)
    base = find_path_mirror(store, 0, 2, [], SweepConfig.production(), ctx)
    off = find_path_mirror(store, 0, 2, [],
                           SweepConfig.production().with_(
                               w_known_ramp_fame_pctl=0.0), ctx)
    assert base == off


def test_ramp_is_inert_at_k_zero_even_at_a_dominating_weight():
    """The term is r * k * fame(v): with no `known` bypasses yet, k = 0, so a
    dominating r must still return production's path. This is the half of
    CRE-G1(b) that a `+ 0.0` implementation would pass and a wrong-k one fails."""
    store = FakeStore()
    store.pop_raw = np.array([0.9, 0.5, 0.9, 0.5], dtype=np.float32)
    ctx = ctx_for(store, [0.5, 0.99, 0.5, 0.01])
    base = find_path_mirror(store, 0, 2, [], SweepConfig.production(), ctx)
    hot = find_path_mirror(store, 0, 2, [],
                           SweepConfig.production().with_(
                               w_known_ramp_fame_pctl=1000.0), ctx)
    assert base == hot == [0, 1, 2]


def _decomposition_case():
    """A k=1 ladder step with the ramp live, on the fake store."""
    from artistpath_api.pathfinding import KNOWN, Exclusion
    store = FakeStore()
    store.pop_raw = np.array([0.9, 0.5, 0.9, 0.5], dtype=np.float32)
    cfg = SweepConfig.production().with_(w_known_ramp_fame_pctl=0.3)
    ctx = ctx_for(store, [0.5, 0.99, 0.5, 0.01])
    ex = [Exclusion(node=1, reason=KNOWN)]
    path, _ = journey(store, 0, 2, ex, cfg, ctx)
    return store, ctx, cfg, ex, path


def test_cost_decomposition_passes_on_a_correct_configuration():
    store, ctx, cfg, ex, path = _decomposition_case()
    assert_cost_decomposition(store, ctx, cfg, ex, path)  # must not raise


def test_cost_decomposition_goes_red_when_a_term_is_dropped(monkeypatch):
    """The red half. An assertion never seen to fail is not yet an assertion:
    drop the `hop` term from the breakdown and CRE-G2(b) must fire."""
    store, ctx, cfg, ex, path = _decomposition_case()

    def broken(store_, ctx_, cfg_, excludes_, path_):
        rows = term_breakdown(store_, ctx_, cfg_, excludes_, path_)
        for r in rows:
            r["hop"] = 0.0
        return rows

    # Pinned to clause (1)'s own message, not just "CRE-G2(b) FAILED": a red
    # raised by the replay clause instead would not demonstrate what this test
    # claims to demonstrate.
    monkeypatch.setattr(cre_mirror, "term_breakdown", broken)
    with pytest.raises(SystemExit, match=r"decomposition .* != search cost"):
        assert_cost_decomposition(store, ctx, cfg, ex, path)


def test_cost_decomposition_goes_red_when_the_ramp_is_misweighted(monkeypatch):
    """Clause (2)'s own red: a ramp component that no longer equals
    r * k * sum(fame) over the interiors must fire even though clause (1)
    is satisfied by construction of the tamper."""
    store, ctx, cfg, ex, path = _decomposition_case()

    def broken(store_, ctx_, cfg_, excludes_, path_):
        rows = term_breakdown(store_, ctx_, cfg_, excludes_, path_)
        # Move mass from ramp_fame into sim: the TOTAL is unchanged, so only
        # clause (2) can catch this one.
        for r in rows:
            r["sim"] += r["ramp_fame"]
            r["ramp_fame"] = 0.0
        return rows

    monkeypatch.setattr(cre_mirror, "term_breakdown", broken)
    with pytest.raises(SystemExit, match="ramp component"):
        assert_cost_decomposition(store, ctx, cfg, ex, path)
