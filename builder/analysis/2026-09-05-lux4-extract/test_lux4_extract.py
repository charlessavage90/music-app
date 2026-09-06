"""Unit tests for the LUX-4 extraction pass. No dump, no artifacts, no network."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lux4_extract import (  # noqa: E402
    KEPT_PLATFORMS,
    DSP,
    facts_of,
    host_of,
    id_tail,
)


def test_spotify_is_a_recognised_platform():
    assert DSP[host_of("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")] == "spotify"


def test_spotify_is_kept_not_filtered_out():
    """The one-line change LUX-4 turns on. Named so a test can assert it."""
    assert "spotify" in KEPT_PLATFORMS
    assert "apple" in KEPT_PLATFORMS


def test_a_query_string_is_stripped_from_the_id_tail():
    """MusicBrainz records Apple links with locale parameters often enough."""
    assert id_tail("https://music.apple.com/us/artist/foo/12345?l=en") == "12345"
    assert id_tail("https://open.spotify.com/artist/abc123/") == "abc123"


def test_facts_omit_absent_fields_rather_than_storing_nulls():
    assert facts_of({"type": "Group"}) == {"type": "Group"}
    assert "country" not in facts_of({"type": "Group"})


def test_an_artist_with_no_facts_yields_an_empty_mapping():
    """`L4-D3`: absence is the empty state. A present-but-empty dict would
    make the frontend render a blank row it cannot distinguish."""
    assert facts_of({}) == {}


def test_ended_false_is_preserved_because_it_is_a_positive_claim():
    """"still active" is not the same as "we do not know"."""
    f = facts_of({"life-span": {"begin": "1995", "end": None, "ended": False}})
    assert f["begin"] == "1995"
    assert f["end"] is None
    assert f["ended"] is False


def test_a_life_span_with_neither_end_nor_begin_adds_no_end_keys():
    assert facts_of({"life-span": {}}) == {}


def test_area_is_flattened_to_its_name():
    assert facts_of({"area": {"name": "United States", "id": "x"}})["area"] == (
        "United States"
    )
