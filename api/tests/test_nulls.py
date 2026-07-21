import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from nulls import configuration_model_rewire, degree_biased_walk  # noqa: E402

from tests.conftest import make_store


def _ring_with_hub():
    return make_store(
        names=list("ABCDE"),
        popularity=[0.5] * 5,
        undirected_edges=[
            (0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (3, 4, 0.9), (4, 0, 0.9),
        ],
    )


def test_degree_biased_walk_returns_requested_length():
    store = _ring_with_hub()
    rng = np.random.default_rng(0)
    walk = degree_biased_walk(store, source=0, length=4, rng=rng)
    assert len(walk) == 4
    assert walk[0] == 0


def test_degree_biased_walk_only_steps_along_real_edges():
    store = _ring_with_hub()
    rng = np.random.default_rng(0)
    walk = degree_biased_walk(store, source=0, length=5, rng=rng)
    for u, v in zip(walk, walk[1:]):
        start, end = int(store.offsets[u]), int(store.offsets[u + 1])
        assert v in store.neighbours[start:end]


def test_rewire_preserves_the_degree_sequence_exactly():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    assert list(np.diff(rewired.offsets)) == list(np.diff(store.offsets))


def test_rewire_preserves_node_count_and_edge_count():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    assert rewired.artist_count == store.artist_count
    assert rewired.neighbours.size == store.neighbours.size


def test_rewire_produces_no_self_loops():
    store = _ring_with_hub()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    for u in range(rewired.artist_count):
        start, end = int(rewired.offsets[u]), int(rewired.offsets[u + 1])
        assert u not in rewired.neighbours[start:end]


def test_rewire_is_deterministic_under_a_fixed_seed():
    store = _ring_with_hub()
    a = configuration_model_rewire(store, np.random.default_rng(11))
    b = configuration_model_rewire(store, np.random.default_rng(11))
    assert np.array_equal(a.neighbours, b.neighbours)
