"""`find_path_coh` -- the properties that must not drift.

THESE ARE UNIT TESTS ON A SYNTHETIC STORE. `TAS-AM5a`'s equivalence check is a
separate and much stronger thing: the FULL §3 draw against the REAL adopted
artifact, run by `tas_route.main()`. Passing these does NOT discharge it, and a
green result here says nothing about whether the fork matches production.
"""

from __future__ import annotations

import numpy as np
import pytest

from tas_route import agreement_cost_of, find_path_coh


class FakeStore:
    """Four nodes. Two equal-cost routes from 0 to 2: via 1, or via 3.

    Every production term is deliberately symmetric between the two routes --
    same similarity, same popularity, same hub penalty -- so ONLY the genre term
    can decide. That is what makes the routing assertions below attributable.
    """

    def __init__(self):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        self._adj = {
            0: [(1, 0.9), (3, 0.9)],
            1: [(0, 0.9), (2, 0.9)],
            2: [(1, 0.9), (3, 0.9)],
            3: [(0, 0.9), (2, 0.9)],
        }

    def neighbours_of(self, node_id):
        return iter(self._adj[node_id])


@pytest.fixture
def cfg():
    from artistpath_api.config import ApiConfig

    return ApiConfig()


def test_zero_weight_ignores_labels_entirely(cfg):
    # The multiplier on the coherence term is exactly 0, so the labels cannot
    # matter. This is the unit-level shadow of TAS-AM5a.
    store = FakeStore()
    rich = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    assert find_path_coh(store, 0, 2, cfg, rich, 0.0) == \
        find_path_coh(store, 0, 2, cfg, {}, 0.0)


def test_a_dominating_weight_routes_through_the_agreeing_neighbour(cfg):
    # `d` (node 3) is the agreeing neighbour, deliberately the HIGHER id.
    # THIS MATTERS: with the two routes identical on every production term, a
    # tie-break on lowest id picks node 1 -- so an earlier version of this test,
    # which expected [0, 1, 2], PASSED with the coherence term zeroed out. It was
    # green for the wrong reason. Caught by closeout B3 on 2026-08-01; expecting
    # the higher-id route is what makes the coherence term load-bearing here.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}, "d": {"rock"}}
    assert find_path_coh(store, 0, 2, cfg, labels, 1e6 * cfg.w_sim) == [0, 3, 2], \
        "the coherence term did not reach the cost function"


def test_an_unlabelled_candidate_is_not_demoted(cfg):
    # THE NEUTRAL RULE (spec §1): a bare artist takes the per-artist median,
    # never zero. Zero is a positive claim of dissimilarity, and unlabelled
    # artists are disproportionately obscure -- demoting them would push DD-F1
    # the wrong way. Here `d` is bare and `b` is a KNOWN mismatch, so the bare
    # candidate must win.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}}
    assert find_path_coh(store, 0, 2, cfg, labels, 1e6 * cfg.w_sim) == [0, 3, 2], \
        "the bare candidate was demoted below a known mismatch"


def test_agreement_cost_of_sums_one_minus_agreement_along_the_path(cfg):
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    assert agreement_cost_of([0, 1, 2], store, labels) == pytest.approx(0.0)


def test_agreement_cost_of_is_not_trivially_zero(cfg):
    # Guards the assertion above from passing because the function returns 0.0
    # for everything -- the vacuous-green shape.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    assert agreement_cost_of([0, 3, 2], store, labels) > 0.0


def test_source_equals_target_returns_the_single_node(cfg):
    assert find_path_coh(FakeStore(), 2, 2, cfg, {}, 1.0) == [2]
