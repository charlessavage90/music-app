from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import find_path
from tests.conftest import make_store

CFG = ApiConfig()


def test_direct_neighbours_path_is_two_nodes():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG) == [0, 1]


def test_path_endpoints_are_source_and_target():
    # Line graph 0-1-2-3-4; path must start at 0 and end at 4.
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)],
    )
    path = find_path(store, 0, 4, [], CFG)
    assert path[0] == 0 and path[-1] == 4


def test_every_adjacent_pair_in_the_path_is_a_real_edge():
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)] + [(0, 2, 0.2)],
    )
    path = find_path(store, 0, 4, [], CFG)
    edges = set()
    for u in range(store.artist_count):
        for v, _ in store.neighbours_of(u):
            edges.add((u, v))
    for a, b in zip(path, path[1:]):
        assert (a, b) in edges


def test_strong_similarity_is_preferred_over_a_weak_shortcut():
    # 0-2 is a direct but weak (0.1) edge; 0-1-2 is two strong (0.95) edges.
    # With w_sim high and w_hop low, the smooth two-hop route should win.
    store = make_store(
        names=["A", "B", "C"], popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 2, 0.1), (0, 1, 0.95), (1, 2, 0.95)],
    )
    assert find_path(store, 0, 2, [], CFG) == [0, 1, 2]


def test_identical_queries_are_deterministic():
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (1, 3, 0.9), (2, 3, 0.9)],
    )
    a = find_path(store, 0, 3, [], CFG)
    b = find_path(store, 0, 3, [], CFG)
    assert a == b


def test_no_path_when_disconnected_returns_none():
    store = make_store(
        names=["A", "B", "C"], popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],  # C (node 2) is isolated
    )
    assert find_path(store, 0, 2, [], CFG) is None


def test_source_equals_target_is_a_single_node():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert find_path(store, 0, 0, [], CFG) == [0]
