import numpy as np
import pytest

from artistpath_builder.fixture import extract_fixture, most_popular_index
from artistpath_builder.graph import build_graph, symmetrise
from artistpath_builder.models import ArtistStats, EdgeType


def _ring(n: int):
    """A connected ring of n artists, so any subset extraction has options."""
    mbids = [f"{i:036d}" for i in range(n)]
    adjacency = {
        m: {mbids[(i + 1) % n]: 0.9, mbids[(i - 1) % n]: 0.8}
        for i, m in enumerate(mbids)
    }
    stats = [
        ArtistStats(
            mbid=m,
            name=f"Artist {i}",
            user_count=(n - i) * 100,
            listen_count=(n - i) * 700,
        )
        for i, m in enumerate(mbids)
    ]
    return build_graph(symmetrise(adjacency), stats, EdgeType.BEHAVIOURAL), mbids


def test_fixture_has_requested_size():
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert fixture.artist_count == 10


def test_fixture_is_connected():
    # A disconnected fixture would make downstream pathfinding tests
    # fail for reasons that have nothing to do with the code under test.
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for i in range(fixture.offsets[node], fixture.offsets[node + 1]):
            neighbour = int(fixture.neighbours[i])
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    assert len(seen) == fixture.artist_count


def test_fixture_edges_stay_within_bounds():
    graph, mbids = _ring(50)
    fixture = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert np.all(fixture.neighbours < fixture.artist_count)
    assert np.all(fixture.neighbours >= 0)


def test_fixture_is_deterministic():
    graph, mbids = _ring(50)
    a = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    b = extract_fixture(graph, size=10, seed_mbid=mbids[0])
    assert a.mbids == b.mbids


def test_requesting_more_than_available_returns_everything():
    graph, mbids = _ring(5)
    fixture = extract_fixture(graph, size=100, seed_mbid=mbids[0])
    assert fixture.artist_count == 5


def test_unknown_seed_raises():
    graph, _ = _ring(5)
    with pytest.raises(KeyError):
        extract_fixture(graph, size=3, seed_mbid="z" * 36)


def _ring_with_one_popular_artist(n: int, popular: int):
    """A ring where one node is far more popular than the rest.

    `build_graph` derives popularity from `user_count`, which the pipeline
    fills with score-weighted in-degree — so popularity is set here through
    that field, not by adding edges. An earlier version of this helper added
    incoming edges and left `user_count` uniform, which changed nothing and
    made the test assert against a flat popularity array.
    """
    mbids = [f"{i:036d}" for i in range(n)]
    adjacency = {
        m: {mbids[(i + 1) % n]: 0.9, mbids[(i - 1) % n]: 0.8}
        for i, m in enumerate(mbids)
    }
    stats = [
        ArtistStats(
            mbid=m,
            name=f"Artist {i}",
            user_count=100_000 if i == popular else 100,
            listen_count=700,
        )
        for i, m in enumerate(mbids)
    ]
    return build_graph(symmetrise(adjacency), stats, EdgeType.BEHAVIOURAL), mbids


def _ring_with_tied_popularity(n: int):
    """A ring where every artist has identical popularity, so the default
    seed is decided purely by the tie-break. `_ring` cannot test this: its
    user_count strictly decreases, so index 0 wins on popularity outright and
    a tie-break assertion there would pass without exercising the tie-break.
    """
    mbids = [f"{i:036d}" for i in range(n)]
    adjacency = {
        m: {mbids[(i + 1) % n]: 0.9, mbids[(i - 1) % n]: 0.8}
        for i, m in enumerate(mbids)
    }
    stats = [
        ArtistStats(mbid=m, name=f"Artist {i}", user_count=500, listen_count=700)
        for i, m in enumerate(mbids)
    ]
    return build_graph(symmetrise(adjacency), stats, EdgeType.BEHAVIOURAL), mbids


def test_default_seed_is_the_most_popular_artist_not_the_first():
    # The regression this guards: the default used to be mbids[0], an
    # arbitrary artist. That only produced a representative sample because
    # hubs were unbounded and a BFS from anywhere reached them. Mutual k-NN
    # bounds degree, so an arbitrary seed now yields a local cluster - the
    # first fixture built after Phase 2 adoption contained no famous artists
    # at all. The default must therefore pick popularity explicitly.
    graph, mbids = _ring_with_one_popular_artist(20, popular=7)
    assert most_popular_index(graph) == 7
    assert graph.mbids[most_popular_index(graph)] != mbids[0]

    fixture = extract_fixture(graph, size=5)
    assert mbids[7] in fixture.mbids


def test_default_seed_breaks_ties_on_lowest_mbid():
    # Determinism is a hard requirement (spec section 9): byte-identical
    # output for identical input. With popularity genuinely tied, only the
    # tie-break decides the seed, so this fails if it is ever dropped.
    graph, mbids = _ring_with_tied_popularity(10)
    assert len(set(graph.popularity)) == 1, "fixture must actually be tied"
    assert graph.mbids[most_popular_index(graph)] == min(mbids)
    assert extract_fixture(graph, size=4).mbids == extract_fixture(graph, size=4).mbids


def test_explicit_seed_still_overrides_the_default():
    graph, mbids = _ring_with_one_popular_artist(20, popular=7)
    fixture = extract_fixture(graph, size=3, seed_mbid=mbids[15])
    assert mbids[15] in fixture.mbids
