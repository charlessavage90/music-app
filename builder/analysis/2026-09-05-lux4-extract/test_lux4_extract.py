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


# --- Id normalisation (added during L4-T3 review of the extracted payload) ---


def test_apple_itunes_and_music_shapes_normalise_to_one_id():
    """MusicBrainz records the SAME Apple artist under two URL shapes.

    `music.apple.com/us/artist/name/657515` and
    `itunes.apple.com/us/artist/name/id657515` must not ship as two different
    ids, or the frontend cannot compose one URL template.
    """
    from lux4_extract import normalise_id

    assert normalise_id("apple", "657515") == "657515"
    assert normalise_id("apple", "id657515") == "657515"


def test_a_trailing_fragment_is_stripped_not_shipped():
    from lux4_extract import normalise_id

    assert normalise_id("apple", "id293029227#") == ""


def test_a_spotify_uri_in_a_url_field_is_rejected():
    """Seen in the dump: a `spotify:artist:` URI url-encoded into a URL slot."""
    from lux4_extract import normalise_id

    assert normalise_id("spotify", "artist%3ALost%20Children%20Of%20Babylon") == ""


def test_a_well_formed_spotify_id_survives():
    from lux4_extract import normalise_id

    assert normalise_id("spotify", "0OdUWJ0sBjDrqHygGUXeCF") == "0OdUWJ0sBjDrqHygGUXeCF"


def test_a_rejected_id_does_not_consume_the_slot():
    """The reason this runs during extraction and not as a post-pass.

    `setdefault` keeps the FIRST value stored. If a malformed relation were
    stored, a later valid one for the same artist could never replace it; by
    returning "" the caller skips it and the next relation still wins.
    """
    from lux4_extract import normalise_id

    store: dict[str, str] = {}
    for tail in ("id293029227#", "657515"):
        ident = normalise_id("apple", tail)
        if ident:
            store.setdefault("mbid", ident)
    assert store == {"mbid": "657515"}


def test_an_album_url_is_not_mistaken_for_an_artist():
    """A Spotify ALBUM id is also 22-char base62, so the id shape cannot
    distinguish them -- only the path can. Artist records in the dump do carry
    album relations, so without this an album link ships on an artist card."""
    from lux4_extract import is_artist_url

    assert not is_artist_url("https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3")
    assert is_artist_url("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")


def test_a_playlist_url_is_rejected():
    from lux4_extract import is_artist_url

    assert not is_artist_url("https://open.spotify.com/playlist/37i9dQZF1DX")


def test_apple_artist_urls_are_recognised_in_both_shapes():
    from lux4_extract import is_artist_url

    assert is_artist_url("https://music.apple.com/us/artist/radiohead/657515")
    assert is_artist_url("https://itunes.apple.com/us/artist/radiohead/id657515")


def test_a_date_with_no_year_is_treated_as_absent():
    """MusicBrainz partial dates can omit the YEAR: `????-06-05`. 404 artists
    in the dump carry one, and rendered verbatim they put "????-06-05" on a
    card. A date with no year cannot say when an artist began or ended."""
    from lux4_extract import clean_date, facts_of

    assert clean_date("????-06-05") is None
    assert clean_date("1995") == "1995"
    assert clean_date("1995-06-05") == "1995-06-05"
    assert facts_of({"life-span": {"begin": "????-06-05"}}) == {}


def test_a_yearless_begin_does_not_produce_an_end_pair():
    """The pair is only meaningful alongside a real date. Without this, an
    artist with only a yearless begin would ship `ended: false` and nothing
    to attach it to."""
    from lux4_extract import facts_of

    f = facts_of({"life-span": {"begin": "????-06-05", "ended": False}})
    assert "end" not in f and "ended" not in f


def test_a_real_end_survives_a_yearless_begin():
    from lux4_extract import facts_of

    f = facts_of({"life-span": {"begin": "????-01-01", "end": "2008", "ended": True}})
    assert f == {"end": "2008", "ended": True}
