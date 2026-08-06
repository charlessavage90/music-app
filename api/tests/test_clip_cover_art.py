"""The image on a card, pinned to the SHAPES THE LIVE CATALOGUES ACTUALLY SEND.

THE DEFECT (found in production 2026-08-06, live at musicapp.cmiller.io)
`_from_deezer_artist` read the card's image from `row["artist"]["picture_medium"]`.
Deezer's `/artist/{id}/top` embeds a MINIMAL artist object -- `id`, `name`,
`tracklist`, `type` and nothing else -- so that key is never present and every
clip resolved by id came back with `cover_url == ""`. The clip played; the card
showed a blank square. Verified against the live API: `picture_medium` appeared
on zero of 110 sampled artists' `/top` responses.

Deezer's `/search` DOES carry a full artist object, so the name path kept
working. That is what made the fault look intermittent rather than total: an
artist got an image or not depending on which lookup happened to answer, which
is invisible from the outside. It shipped with the 2026-08-06 map switch,
because the ids that trigger the id path travel inside the artifact and that was
the first artifact to carry them.

THE FIX
Read the ALBUM COVER, which is present on both Deezer responses and needs no
extra request. It also makes all three resolution paths agree: iTunes already
returned album art (`artworkUrl100`), so the resolver had been mixing artist
photographs and album covers without saying so.

WHY THIS FILE EXISTS AT ALL
The pre-existing fixtures in test_clip_identity.py put `picture_medium` on the
`/top` response. Nothing in the suite could fail, because the fake fetcher was
answering with a shape the real service does not send -- exactly the trap
clips.py's own module docstring predicted for these endpoints. So the fixtures
below are deliberately transcribed from live responses, and the `/top` one
carries NO picture keys. Weakening that is reintroducing the defect.
"""

from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig

CFG = ApiConfig()
MBID = "a" * 36
DEEZER_ID = "580"

ARTIST_PHOTO = "https://cdn-images.dzcdn.net/images/artist/22545b72/250x250.jpg"
ALBUM_COVER = "https://cdn-images.dzcdn.net/images/cover/61597432/250x250.jpg"

# Transcribed from https://api.deezer.com/artist/580/top (Aphex Twin), the
# artist that exposed this in production. NOTE THE ARTIST OBJECT: four keys, no
# picture of any size. Adding one here would make this file pass vacuously.
ARTIST_TOP = {
    "data": [
        {
            "id": 3135556,
            "title": "Xtal",
            "preview": "https://cdnt-preview.dzcdn.net/api/1/1/c/3/9/0/xtal.mp3",
            "artist": {
                "id": 580,
                "name": "Aphex Twin",
                "tracklist": "https://api.deezer.com/artist/580/top?limit=50",
                "type": "artist",
            },
            "album": {
                "id": 302127,
                "title": "Selected Ambient Works 85-92",
                "cover_medium": ALBUM_COVER,
                "type": "album",
            },
            "type": "track",
        }
    ]
}

# Transcribed from https://api.deezer.com/search?q=Aphex+Twin. This one DOES
# carry the artist photograph -- which is why the name path never broke, and why
# the two paths disagreed about what a card shows.
NAME_SEARCH = {
    "data": [
        {
            "id": 3135556,
            "title": "Xtal",
            "preview": "https://cdnt-preview.dzcdn.net/api/1/1/c/3/9/0/xtal.mp3",
            "artist": {
                "id": 580,
                "name": "Aphex Twin",
                "picture_medium": ARTIST_PHOTO,
                "type": "artist",
            },
            "album": {
                "id": 302127,
                "title": "Selected Ambient Works 85-92",
                "cover_medium": ALBUM_COVER,
                "type": "album",
            },
            "type": "track",
        }
    ]
}

ITUNES = {
    "results": [
        {
            "trackId": 991,
            "previewUrl": "https://cdn.itunes/clip.m4a",
            "trackName": "Xtal",
            "artistName": "Aphex Twin",
            "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/100x100bb.jpg",
        }
    ]
}


def _resolver(responses, cache=None):
    async def fetch_json(url, params):
        for frag, body in responses.items():
            if frag in url:
                return body
        return {}

    return ClipResolver(CFG, cache or InMemoryClipCache(), fetch_json)


async def test_the_id_path_returns_an_image():
    # THE regression test. Before the fix this was "" and the card rendered a
    # blank square while the clip played perfectly.
    r = _resolver({"artist/580/top": ARTIST_TOP})
    clip = await r.resolve(MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID)
    assert clip.cover_url == ALBUM_COVER


async def test_the_name_path_returns_the_same_kind_of_image():
    # Not merely "an image": the SAME source as the id path. A card must not
    # change appearance based on which lookup happened to answer, which is the
    # inconsistency the production report was actually about.
    r = _resolver({"deezer.com/search": NAME_SEARCH})
    clip = await r.resolve(MBID, "Aphex Twin")
    assert clip.cover_url == ALBUM_COVER
    assert clip.cover_url != ARTIST_PHOTO


async def test_both_deezer_paths_agree_on_the_image():
    # Stated as one assertion because it is the property that was violated, and
    # the two tests above could both pass while drifting apart later.
    by_id = await _resolver({"artist/580/top": ARTIST_TOP}).resolve(
        MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID
    )
    by_name = await _resolver({"deezer.com/search": NAME_SEARCH}).resolve(
        MBID, "Aphex Twin"
    )
    assert by_id.cover_url == by_name.cover_url


async def test_itunes_still_returns_its_album_art_unchanged():
    # The fallback already returned album art. Pinned so the fix is understood
    # as making Deezer agree with iTunes, not as changing all three.
    r = _resolver({"itunes": ITUNES})
    clip = await r.resolve(MBID, "Aphex Twin")
    assert clip.cover_url.endswith("100x100bb.jpg")


async def test_a_track_with_no_album_block_is_silent_not_a_crash():
    # An image is decorative; a card with no image must still play. TrackOut
    # types cover_url as str, so a JSON null reaching the endpoint is a 500 --
    # the same `or ""` reasoning already commented on the title field.
    no_album = {"data": [dict(ARTIST_TOP["data"][0], album=None)]}
    r = _resolver({"artist/580/top": no_album})
    clip = await r.resolve(MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID)
    assert clip.cover_url == ""
    assert clip.preview_url


async def test_a_missing_cover_key_is_silent_not_a_crash():
    # Deezer can send an album block with no cover at all.
    bare = {"data": [dict(ARTIST_TOP["data"][0], album={"id": 1, "type": "album"})]}
    r = _resolver({"artist/580/top": bare})
    clip = await r.resolve(MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID)
    assert clip.cover_url == ""
    assert clip.preview_url


async def test_the_image_survives_a_cache_round_trip():
    # The identity is what gets cached, so a broken image would persist for the
    # full 30-day TTL rather than self-correcting on the next request. That is
    # why the production fault outlives a deploy.
    cache = InMemoryClipCache()
    await _resolver({"artist/580/top": ARTIST_TOP}, cache=cache).resolve(
        MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID
    )
    replay = _resolver({"track/3135556": {"preview": "https://cdn/resigned.mp3"}},
                       cache=cache)
    clip = await replay.resolve(MBID, "Aphex Twin", deezer_artist_id=DEEZER_ID)
    assert clip.preview_url == "https://cdn/resigned.mp3"
    assert clip.cover_url == ALBUM_COVER
