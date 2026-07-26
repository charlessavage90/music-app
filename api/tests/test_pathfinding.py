from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import (
    DISLIKE,
    KNOWN,
    STOP_ADJACENT_ONLY,
    STOP_FORCED,
    STOP_NATURAL,
    Exclusion,
    find_journey,
    find_path,
)
from tests.conftest import make_store

CFG = ApiConfig()


def test_direct_neighbours_path_is_two_nodes():
    store = make_store(
        names=["A", "B"], pop_raw=[0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG) == [0, 1]


def test_path_endpoints_are_source_and_target():
    # Line graph 0-1-2-3-4; path must start at 0 and end at 4.
    store = make_store(
        names=list("ABCDE"), pop_raw=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)],
    )
    path = find_path(store, 0, 4, [], CFG)
    assert path[0] == 0 and path[-1] == 4


def test_every_adjacent_pair_in_the_path_is_a_real_edge():
    store = make_store(
        names=list("ABCDE"), pop_raw=[0.5] * 5,
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
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 2, 0.1), (0, 1, 0.95), (1, 2, 0.95)],
    )
    assert find_path(store, 0, 2, [], CFG) == [0, 1, 2]


def test_identical_queries_are_deterministic():
    store = make_store(
        names=list("ABCD"), pop_raw=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (1, 3, 0.9), (2, 3, 0.9)],
    )
    a = find_path(store, 0, 3, [], CFG)
    b = find_path(store, 0, 3, [], CFG)
    assert a == b


def test_no_path_when_disconnected_returns_none():
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9)],  # C (node 2) is isolated
    )
    assert find_path(store, 0, 2, [], CFG) is None


def test_source_equals_target_is_a_single_node():
    store = make_store(
        names=["A", "B"], pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert find_path(store, 0, 0, [], CFG) == [0]


def test_w_degree_hub_zero_is_a_noop():
    # Default w_degree_hub=0 must not change routing (the new term is opt-in).
    store = make_store(
        names=list("ABC"), pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 2, 0.1), (0, 1, 0.95), (1, 2, 0.95)],
    )
    from dataclasses import replace
    assert find_path(store, 0, 2, [], replace(CFG, w_degree_hub=0.0)) == [0, 1, 2]


def test_degree_hub_penalty_routes_around_a_hub():
    # 0->1->3 and 0->2->3 are both two strong hops. Node 1 is a hub (wired to
    # 20 extra leaves); node 2 is low-degree. With w_degree_hub high, avoid node 1.
    from dataclasses import replace
    edges = [(0, 1, 0.9), (1, 3, 0.9), (0, 2, 0.9), (2, 3, 0.9)]
    edges += [(1, 10 + i, 0.5) for i in range(20)]  # make node 1 a hub
    store = make_store(
        names=[str(i) for i in range(30)],
        pop_raw=[0.5] * 30,
        undirected_edges=edges,
    )
    # Sanity: node 1 is the hub.
    assert store.degree_hub_penalty[1] > store.degree_hub_penalty[2]
    path = find_path(store, 0, 3, [], replace(CFG, w_degree_hub=5.0))
    assert 1 not in path
    assert path == [0, 2, 3]


def test_forbidden_edge_routes_around_the_direct_link():
    # 0-1 direct and strong; 0-2-1 available. Forbidding 0-1 must use 2.
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG) == [0, 1]
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(0, 1)) == [0, 2, 1]


def test_forbidden_edge_is_undirected():
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    # Given the other way round, the same edge must still be blocked.
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(1, 0)) == [0, 2, 1]


def test_forbidding_the_only_link_yields_no_path():
    # B hangs off A by a single edge, as some real artists do
    # (findings/2026-07-25-mutual-knn-stranding.md, MKS-3).
    store = make_store(
        names=["A", "B", "C"], pop_raw=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    assert find_path(store, 0, 1, [], CFG, forbidden_edge=(0, 1)) is None


def test_omitting_forbidden_edge_changes_nothing():
    store = make_store(
        names=list("ABCDE"), pop_raw=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)] + [(0, 2, 0.2)],
    )
    assert find_path(store, 0, 4, [], CFG) == find_path(
        store, 0, 4, [], CFG, forbidden_edge=None
    )


def test_journey_with_its_own_stop_is_left_alone():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert find_journey(store, 0, 2, [], CFG) == ([0, 1, 2], STOP_NATURAL)


def test_two_neighbours_get_a_stop_forced_between_them():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    path, rule = find_journey(store, 0, 1, [], CFG)
    assert rule == STOP_FORCED
    assert path[0] == 0 and path[-1] == 1
    assert len(path) >= 3


def test_two_neighbours_with_nothing_between_them_fall_back():
    # B's only connection is to A, so no stop can exist.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    assert find_journey(store, 0, 1, [], CFG) == ([0, 1], STOP_ADJACENT_ONLY)


def test_a_stop_is_never_forced_through_a_bypassed_artist():
    # C is the only possible stop, and the user has rejected it.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    excludes = [Exclusion(node=2, reason=DISLIKE)]
    assert find_journey(store, 0, 1, excludes, CFG) == ([0, 1], STOP_ADJACENT_ONLY)


def test_journey_returns_none_when_exclusions_disconnect_the_endpoints():
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 2, 0.9), (2, 1, 0.9)],
    )
    excludes = [Exclusion(node=2, reason=DISLIKE)]
    assert find_journey(store, 0, 1, excludes, CFG) is None


def test_forcing_a_stop_never_drops_the_two_chosen_artists():
    # Excluding an endpoint has never removed it, and the second search must
    # not change that. Design section 6, test 5.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.95), (0, 2, 0.9), (1, 2, 0.9)],
    )
    excludes = [Exclusion(node=0, reason=DISLIKE), Exclusion(node=1, reason=KNOWN)]
    path, _rule = find_journey(store, 0, 1, excludes, CFG)
    assert path[0] == 0 and path[-1] == 1
