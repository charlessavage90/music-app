import numpy as np
import pytest

from artistpath_builder.fixture import extract_fixture
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
