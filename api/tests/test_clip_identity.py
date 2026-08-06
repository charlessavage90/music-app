"""Resolving a clip by ARTIST IDENTITY rather than by name (`BYP-13`).

THE DEFECT
The app finds a clip by searching the artist's NAME, so a card can play a clip
by a DIFFERENT ARTIST OF THE SAME NAME. Measured twice on this project: 9.4%
(denominator 160) and 6.1% (denominator 49) of the cases where it could be
checked. `same_artist` cannot help — the wrong artist's name matches exactly,
which is the whole problem.

THE FIX
MusicBrainz records a Deezer artist id for many artists. Asking that artist
directly for a top track involves no name matching at all, so it cannot return
a same-named impostor. The builder carries the ids in the APG1 metadata blob.

WHAT THIS IS NOT
Not a replacement for name search. Where no id is known, or the id yields
nothing playable, the resolver falls back to exactly what it did before, so
behaviour is unchanged for those artists. Over the artists the app actually
delivers on cards, 92.9% of impressions have an id
(builder/analysis/2026-08-02-dsp-ids/).

The amplification rule still governs (G3-A4): when Deezer refuses us, the
resolver must not turn one call into three. A refusal on the id path must skip
Deezer's search too and go straight to iTunes.
"""

from artistpath_api.clips import (
    CatalogueUnavailable, ClipResolver, InMemoryClipCache,
)
from artistpath_api.config import ApiConfig

CFG = ApiConfig()
MBID = "a" * 36
DEEZER_ID = "12345"

# The defect, concretely. Two artists are called "Nirvana": the Seattle band and
# a 1960s British group. A name search returns whichever the catalogue ranks
# first, and `same_artist` accepts it because the name is identical.
WRONG_SAME_NAME_ARTIST = {
    "data": [
        {"id": 1, "preview": "https://cdn.deezer/wrong.mp3",
         "title": "Pentecost Hotel",
         "artist": {"name": "Nirvana", "picture_medium": "https://cdn/uk.jpg"}}
    ]
}
# The id path asks artist 12345 directly, so no other artist can be returned.
#
# ⚠ The artist object here has NO picture key, and that is not an omission.
# Deezer's /artist/{id}/top sends `id`, `name`, `tracklist`, `type` and nothing
# else -- unlike /search above, which sends a full one. This fixture used to
# carry `picture_medium`, and that single invented key hid a live defect for
# four days: the resolver read the card's image from it, every test passed, and
# production served blank squares. Restoring it re-blinds this file.
# The image itself is pinned in test_clip_cover_art.py.
ARTIST_TOP_HIT = {
    "data": [
        {"id": 2, "preview": "https://cdn.deezer/right.mp3",
         "title": "Smells Like Teen Spirit",
         "artist": {"id": 12345, "name": "Nirvana", "type": "artist"},
         "album": {"id": 7, "title": "Nevermind",
                   "cover_medium": "https://cdn/nevermind.jpg", "type": "album"}}
    ]
}
ITUNES_HIT = {
    "results": [
        {"trackId": 991, "previewUrl": "https://cdn.itunes/clip.m4a",
         "trackName": "In Bloom", "artistName": "Nirvana",
         "artworkUrl100": "https://cdn/itunes.jpg"}
    ]
}


class Boom(Exception):
    """The real fetcher calls raise_for_status, so failures arrive as raises."""


def _resolver(responses, cache=None):
    calls = []

    async def fetch_json(url, params):
        calls.append((url, params))
        for frag, body in responses.items():
            if frag in url:
                if isinstance(body, Exception):
                    raise body
                return body
        return {}

    r = ClipResolver(CFG, cache or InMemoryClipCache(), fetch_json)
    r.calls = calls
    return r


def _urls(resolver):
    return [url for url, _params in resolver.calls]


async def test_a_known_id_beats_a_same_named_impostor():
    # THE test. Name search would return the wrong Nirvana and `same_artist`
    # would accept it; the id path returns the right one.
    r = _resolver({"artist/12345/top": ARTIST_TOP_HIT,
                   "deezer.com/search": WRONG_SAME_NAME_ARTIST})
    clip = await r.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn.deezer/right.mp3"
    assert clip.title == "Smells Like Teen Spirit"


async def test_the_id_path_makes_no_name_search_at_all():
    # Not just "the right answer" -- the wrong lookup must not happen. If the
    # search still ran, the fix would be one ranking change away from silently
    # regressing.
    r = _resolver({"artist/12345/top": ARTIST_TOP_HIT,
                   "deezer.com/search": WRONG_SAME_NAME_ARTIST})
    await r.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert not any("search" in url for url in _urls(r))


async def test_no_id_falls_back_to_name_search_unchanged():
    # 52% of the graph has no id. Their behaviour must be exactly what it was.
    r = _resolver({"deezer.com/search": WRONG_SAME_NAME_ARTIST})
    clip = await r.resolve(MBID, "Nirvana")
    assert clip.preview_url == "https://cdn.deezer/wrong.mp3"
    assert not any("/top" in url for url in _urls(r))


async def test_an_id_that_yields_nothing_falls_back_to_name_search():
    # An id exists but Deezer has no playable top track for that artist. In the
    # release-less tail the id path resolved only about half the time, so this
    # is the common case there, not an edge case.
    r = _resolver({"artist/12345/top": {"data": []},
                   "deezer.com/search": WRONG_SAME_NAME_ARTIST})
    clip = await r.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn.deezer/wrong.mp3"


async def test_a_refusal_on_the_id_path_skips_deezer_search():
    # G3-A4: when Deezer is REFUSING us, one call must not become three.
    # Falling through to iTunes is the fallback doing its job; asking Deezer
    # again is the defect. Only CatalogueUnavailable means refusal -- see the
    # stale-id test below for the other kind of failure.
    r = _resolver({"artist/12345/top": CatalogueUnavailable("429"),
                   "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"
    assert not any("deezer.com/search" in url for url in _urls(r))


async def test_a_stale_id_falls_back_to_name_search_rather_than_giving_up():
    # The ids are a frozen 2026-08-02 snapshot, so one can go stale and 404.
    # That is a MISS, not a refusal, and `_get` already draws that distinction
    # -- so the card degrades to today's behaviour instead of going silent.
    # This is the "fails safe" claim in deezer_ids.py, pinned.
    r = _resolver({"artist/12345/top": Boom(),
                   "deezer.com/search": WRONG_SAME_NAME_ARTIST})
    clip = await r.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn.deezer/wrong.mp3"


async def test_an_empty_id_is_treated_as_no_id():
    # The metadata blob carries "" for artists with no id, so the resolver sees
    # empty strings rather than None on every uncovered artist.
    r = _resolver({"deezer.com/search": WRONG_SAME_NAME_ARTIST})
    clip = await r.resolve(MBID, "Nirvana", deezer_artist_id="")
    assert clip.preview_url == "https://cdn.deezer/wrong.mp3"
    assert not any("/top" in url for url in _urls(r))


async def test_the_identity_found_by_id_is_cached_and_replayable():
    # A cached identity costs one lookup on the next request. It must round
    # trip through the cache like a name-found one, or the id path would be
    # paid for on every single card.
    cache = InMemoryClipCache()
    r1 = _resolver({"artist/12345/top": ARTIST_TOP_HIT}, cache=cache)
    await r1.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)

    r2 = _resolver({"track/2": {"preview": "https://cdn.deezer/resigned.mp3"}},
                   cache=cache)
    clip = await r2.resolve(MBID, "Nirvana", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn.deezer/resigned.mp3"
    assert not any("/top" in url for url in _urls(r2))
