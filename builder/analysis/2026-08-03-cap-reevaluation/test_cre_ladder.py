# test_cre_ladder.py -- the properties that must not drift
from __future__ import annotations

import numpy as np
import pytest

from cre_ladder import journey, victim_key, walk_journey
from cre_mirror import MirrorContext, SweepConfig


class FakeStore:
    """0 -- 1 -- 2 line, detour 0 -- 3 -- 2; CSR-ish surface for the mirror."""

    def __init__(self, sims=None):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.9, 0.5, 0.9, 0.4], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        s = sims or {}
        self._adj = {
            0: [(1, s.get((0, 1), 0.9)), (3, s.get((0, 3), 0.8))],
            1: [(0, s.get((0, 1), 0.9)), (2, s.get((1, 2), 0.9))],
            2: [(1, s.get((1, 2), 0.9)), (3, s.get((2, 3), 0.8))],
            3: [(0, s.get((0, 3), 0.8)), (2, s.get((2, 3), 0.8))],
        }
        self.offsets = np.array([0, 2, 4, 6, 8])
        self.neighbours = np.array([1, 3, 0, 2, 1, 3, 0, 2])

    def neighbours_of(self, u):
        return iter(self._adj[u])


def ctx_for(store, fame_device):
    return MirrorContext.build(store, np.asarray(fame_device, dtype=np.float64))


def test_adjacent_pair_yields_forced_detour_not_a_vanished_cell():
    store = FakeStore()
    store._adj[0].append((2, 0.95)); store._adj[2].append((0, 0.95))
    store.offsets = np.array([0, 3, 5, 8, 10])
    store.neighbours = np.array([1, 3, 2, 0, 2, 1, 3, 0, 0, 2])
    cfg = SweepConfig.production()
    path, kind = journey(store, 0, 2, [], cfg, ctx_for(store, [0.5] * 4))
    assert kind == "forced" and len(path) == 3


def test_victim_is_the_highest_fame_interior_nulls_last():
    fame = np.array([np.nan, 0.2, np.nan, np.nan])
    pop = np.array([0.9, 0.5, 0.9, 0.99])
    key = victim_key(fame, pop, ["a", "b", "c", "d"])
    # 1 is measured (0.2); 3 is null with higher pop -- measured wins.
    assert min([1, 3], key=key) == 1


def test_fame_ramp_reaches_the_cost_function():
    # Make node 1 famous in FAME currency only (pop equal on both routes):
    # at a dominating ramp and k=1, the walk's d1 must route via 3.
    store = FakeStore()
    store.pop_raw = np.array([0.9, 0.5, 0.9, 0.5], dtype=np.float32)
    fame = [0.5, 0.99, 0.5, 0.01]
    cfg = SweepConfig.production().with_(w_known_ramp_fame_pctl=1000.0)
    ctx = ctx_for(store, fame)
    from artistpath_api.pathfinding import KNOWN, Exclusion
    ex = [Exclusion(node=1, reason=KNOWN)]
    path, _ = journey(store, 0, 2, ex, cfg, ctx)
    assert path == [0, 3, 2], "the fame term did not reach the cost function"


def test_walk_always_returns_max_depth_plus_one_entries():
    store = FakeStore()
    cfg = SweepConfig.production()
    fame = np.array([0.5, 0.5, 0.5, 0.5])
    out = walk_journey(store, 0, 2, cfg, ctx_for(store, fame), fame,
                       store.pop_raw, store.mbids)
    from cre_common import MAX_DEPTH
    assert len(out) == MAX_DEPTH + 1
