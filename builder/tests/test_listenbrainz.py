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
    assert first.score > 0


def test_scores_stay_raw_not_per_artist_normalised(source, similar_artists_payload):
    # Regression guard. Per-artist max-normalisation made every artist's top
    # edge 1.0 whether its raw count was 11 or 11,147 (a 1013x spread), so edge
    # strengths were incommensurable across artists and the router preferred
    # meaningless hops between obscure artists (findings 2026-07-21 section 3).
    # Scores must stay raw here; globally comparable, popularity-corrected
    # normalisation happens in the pipeline.
    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert max(n.score for n in neighbours) > 1.0
    scores = [n.score for n in neighbours]
    assert scores == sorted(scores, reverse=True)  # deterministic order


def test_parse_does_not_cap_neighbours(similar_artists_payload):
    # The cap moved to the pipeline, which applies it AFTER the cosine
    # correction reorders neighbours. parse must return the full list so the
    # pipeline can compute an accurate per-artist co-occurrence mass.
    source = ListenBrainzSource(BuilderConfig(max_neighbours_per_artist=10))
    neighbours = source.parse(json.dumps(similar_artists_payload).encode())
    assert len(neighbours) == 100


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
