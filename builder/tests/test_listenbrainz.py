import json

import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

RADIOHEAD = "a74b1b7f-71a5-4011-9441-d0b5e4122711"


@pytest.fixture
def source():
    return ListenBrainzSource(BuilderConfig())


def test_request_url_includes_mbid_and_algorithm(source):
    url = source.request_url(RADIOHEAD)
    assert RADIOHEAD in url
    assert BuilderConfig().algorithm in url


def test_parses_recorded_real_response(source, similar_artists_payload):
    """Runs against the response recorded from the live API in Task 1."""
    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert len(neighbours) > 0
    first = neighbours[0]
    assert len(first.mbid) == 36
    assert 0.0 <= first.score <= 1.0


def test_scores_are_normalised_to_unit_range(source, similar_artists_payload):
    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert all(0.0 <= n.score <= 1.0 for n in neighbours)
    # The strongest neighbour anchors the scale.
    assert max(n.score for n in neighbours) == pytest.approx(1.0)


def test_neighbour_count_is_capped_by_config(similar_artists_payload):
    source = ListenBrainzSource(BuilderConfig(max_neighbours_per_artist=10))
    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert len(neighbours) == 10


def test_empty_response_yields_no_neighbours(source):
    assert source.parse(b"[]") == []


def test_malformed_payload_raises(source):
    with pytest.raises(ValueError):
        source.parse(b"not json")


def test_self_reference_is_dropped(source):
    # An artist must never be its own neighbour: a self-loop is a zero-cost
    # cycle that pathfinding would happily sit inside.
    payload = (
        b'[{"artist_mbid":"' + RADIOHEAD.encode() + b'","name":"Radiohead","score":99}]'
    )
    assert source.parse(payload, exclude_mbid=RADIOHEAD) == []
