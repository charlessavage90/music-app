from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import (
    DISLIKE, KNOWN, Exclusion, avoidance_map, effective_floor, find_path,
)
from tests.conftest import make_store

CFG = ApiConfig()


def test_hard_excluded_artist_never_appears_in_the_path():
    # 0-1-2 and 0-3-2; exclude 1, so the path must go via 3.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 3, 0.7), (3, 2, 0.7)],
    )
    path = find_path(store, 0, 2, [Exclusion(1, DISLIKE)], CFG)
    assert 1 not in path
    assert path == [0, 3, 2]


def test_endpoints_cannot_be_excluded():
    store = make_store(
        names=["A", "B"], popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    # Excluding the target must not delete it or break the path.
    path = find_path(store, 0, 1, [Exclusion(1, DISLIKE)], CFG)
    assert path == [0, 1]


def test_known_relaxes_floor_more_than_dislike():
    base = 0.8
    known = effective_floor(base, [Exclusion(9, KNOWN)], CFG)
    dislike = effective_floor(base, [Exclusion(9, DISLIKE)], CFG)
    assert known < dislike < base


def test_floor_relaxation_is_progressive():
    base = 0.9
    one = effective_floor(base, [Exclusion(1, KNOWN)], CFG)
    two = effective_floor(base, [Exclusion(1, KNOWN), Exclusion(2, KNOWN)], CFG)
    assert two < one < base


def test_floor_never_goes_negative():
    assert effective_floor(0.05, [Exclusion(i, KNOWN) for i in range(20)], CFG) == 0.0


def test_avoidance_penalises_neighbours_of_disliked_artist():
    # Star: 0 at centre, 1/2/3 as neighbours; disliking 0 penalises 1,2,3.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    av = avoidance_map(store, [0], CFG)
    assert av[1] > 0 and av[2] > 0 and av[3] > 0


def test_avoidance_decays_with_distance():
    # Line 0-1-2-3; disliking 0, node 1 (1 hop) penalised more than node 2.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9)],
    )
    av = avoidance_map(store, [0], CFG)
    assert av[1] > av.get(2, 0.0)


def test_avoidance_is_bounded_by_radius():
    store = make_store(
        names=list("ABCDE"), popularity=[0.5] * 5,
        undirected_edges=[(i, i + 1, 0.9) for i in range(4)],
    )
    av = avoidance_map(store, [0], CFG)  # radius 2
    assert 3 not in av and 4 not in av


def test_bypass_reroutes_when_an_alternative_exists():
    # 0-1-3 and 0-2-3; bypassing 1 reroutes via 2 rather than failing.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 3, 0.9), (0, 2, 0.9), (2, 3, 0.9)],
    )
    path = find_path(store, 0, 3, [Exclusion(1, DISLIKE)], CFG)
    assert path is not None and 1 not in path


def test_avoidance_penalised_neighbour_is_still_traversable():
    # Only the *clicked* artist is hard-excluded; its neighbours get a soft
    # penalty but stay routable. Here node 2 is 1's neighbour and the only
    # route to 3, so the path still uses it — soft cost never disconnects
    # (spec 4.3).
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (1, 2, 0.9), (2, 3, 0.9)],
    )
    path = find_path(store, 0, 3, [Exclusion(1, DISLIKE)], CFG)
    assert path == [0, 2, 3]
