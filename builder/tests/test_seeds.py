import json

import pytest

from artistpath_builder.config import BuilderConfig
from artistpath_builder.sources.seeds import (
    artist_stats_url,
    bootstrap_url,
    parse_artist_stats,
    parse_bootstrap_page,
)


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


def test_stats_url_contains_mbid_and_listeners_path():
    url = artist_stats_url(BuilderConfig(), "a" * 36)
    assert "a" * 36 in url
    assert url.endswith("/listeners")


def test_parses_recorded_real_stats_response(artist_listeners_payload):
    stats = parse_artist_stats(json.dumps(artist_listeners_payload).encode())
    assert stats is not None
    assert stats.user_count > 0
    assert stats.listen_count > 0
    assert len(stats.mbid) == 36


def test_stats_prefers_user_count_over_listen_count(artist_listeners_payload):
    # Spec 4.1: popularity is distinct listeners, not plays. Guards against
    # someone "simplifying" these back into one field.
    stats = parse_artist_stats(json.dumps(artist_listeners_payload).encode())
    assert stats.user_count != stats.listen_count


def test_stats_for_unknown_artist_returns_none():
    payload = json.dumps({"payload": {"artist_mbid": None}}).encode()
    assert parse_artist_stats(payload) is None


def test_malformed_payload_raises():
    with pytest.raises(ValueError):
        parse_bootstrap_page(b"<html>")
    with pytest.raises(ValueError):
        parse_artist_stats(b"<html>")
