"""`L4-T3` — the frozen Spotify/Apple id maps must vouch for themselves."""

import hashlib
import json

from artistpath_builder.dsp_links import (
    APPLE_IDS_SHA256,
    SPOTIFY_IDS_SHA256,
    load_dsp_links,
)


def test_payload_matches_its_own_identity_block():
    """A payload that cannot vouch for itself must not be trusted.

    Same discipline as the drop lists: the sha is recorded in the module and
    recomputed here, so a silently swapped file fails the suite rather than
    shipping.
    """
    spotify, apple = load_dsp_links()
    for mapping, expected in (
        (spotify, SPOTIFY_IDS_SHA256),
        (apple, APPLE_IDS_SHA256),
    ):
        actual = hashlib.sha256(
            json.dumps(sorted(mapping.items()), sort_keys=True).encode()
        ).hexdigest()
        assert actual == expected


def test_a_missing_artist_is_absent_not_empty():
    spotify, _ = load_dsp_links()
    assert "00000000-0000-0000-0000-000000000000" not in spotify


def test_ids_are_tails_not_urls():
    spotify, apple = load_dsp_links()
    for mapping in (spotify, apple):
        for value in list(mapping.values())[:50]:
            assert not value.startswith("http"), value
            assert "/" not in value, value


def test_every_apple_id_is_bare_numeric():
    """The whole map, not a sample -- this is what makes ONE URL template work.

    MusicBrainz records the same Apple artist under `music.apple.com/.../657515`
    and `itunes.apple.com/.../id657515`. Before normalisation the shipped map
    held 20,777 of the first shape and 15,140 of the second, so a frontend
    template could only ever have been right for one of them.
    """
    _, apple = load_dsp_links()
    bad = [v for v in apple.values() if not v.isdigit()]
    assert not bad, bad[:5]


def test_every_spotify_id_is_22_char_base62():
    """Anything else is a malformed relation, and shipping one is a dead link."""
    spotify, _ = load_dsp_links()
    bad = [v for v in spotify.values() if not (len(v) == 22 and v.isalnum())]
    assert not bad, bad[:5]
