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


def _hub_and_ring():
    """A genuine hub (node 0, degree 6) plus a disjoint 5-node ring.

    Node 0 ("A") is a spoke centre for six degree-1 leaves ("B"-"G"). Nodes
    "H"-"L" form a separate 5-cycle at degree 2 each. Unlike `_ring_with_hub`,
    this fixture has a real degree spread (1, 2, 6) so degree-sequence
    preservation is checked on something other than a degree-regular graph.
    Eleven edges is enough that most spoke/ring edge pairs are legal
    double-edge swaps (a spoke and a ring edge never share an endpoint and a
    swap between them can never collide with an existing edge), so the swap
    loop does real work rather than hitting the `m < 2` early return.
    """
    return make_store(
        names=list("ABCDEFGHIJKL"),
        popularity=[0.5] * 12,
        undirected_edges=[
            # Six spokes: hub A (node 0) to leaves B-G (nodes 1-6).
            (0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9),
            (0, 4, 0.9), (0, 5, 0.9), (0, 6, 0.9),
            # A separate 5-cycle: H-I-J-K-L-H (nodes 7-11).
            (7, 8, 0.9), (8, 9, 0.9), (9, 10, 0.9), (10, 11, 0.9), (11, 7, 0.9),
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


def test_rewire_preserves_the_degree_sequence_on_a_graph_with_a_real_hub():
    # Degree sequence by node index, read off the edge list in _hub_and_ring:
    # A(0) has 6 spokes; B-G(1-6) have 1 edge each (their spoke); H-L(7-11)
    # each sit in the 5-cycle, so degree 2 each.
    expected = [6, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    store = _hub_and_ring()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    assert list(np.diff(rewired.offsets)) == expected


def test_rewire_produces_no_self_loops_on_a_graph_with_a_real_hub():
    store = _hub_and_ring()
    rng = np.random.default_rng(7)
    rewired = configuration_model_rewire(store, rng)
    for u in range(rewired.artist_count):
        start, end = int(rewired.offsets[u]), int(rewired.offsets[u + 1])
        assert u not in rewired.neighbours[start:end]
