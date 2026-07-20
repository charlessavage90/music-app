import json

import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.seeds import bootstrap_url, parse_bootstrap_page


def test_bootstrap_url_carries_offset_and_count():
    url = bootstrap_url(BuilderConfig(), offset=900, count=100)
    assert "offset=900" in url
    assert "count=100" in url


def test_parses_recorded_real_bootstrap_response(seed_artists_payload):
    artists = parse_bootstrap_page(json.dumps(seed_artists_payload).encode())
    assert len(artists) > 0
    assert all(len(a.mbid) == 36 for a in artists)


def test_bootstrap_drops_artists_without_an_mbid():
    # Sitewide stats include artists MusicBrainz cannot identify. They cannot
    # be graph nodes, because similarity lookups are MBID-keyed.
    payload = json.dumps(
        {
            "payload": {
                "artists": [
                    {"artist_mbid": None, "artist_name": "Unknown"},
                    {"artist_mbid": "a" * 36, "artist_name": "Known"},
                ]
            }
        }
    ).encode()
    assert [a.name for a in parse_bootstrap_page(payload)] == ["Known"]


def test_empty_bootstrap_page_yields_nothing():
    assert parse_bootstrap_page(json.dumps({"payload": {"artists": []}}).encode()) == []


def test_malformed_payload_raises():
    with pytest.raises(ValueError):
        parse_bootstrap_page(b"<html>")
