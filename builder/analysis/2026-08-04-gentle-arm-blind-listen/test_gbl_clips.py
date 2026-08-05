import asyncio

from gbl_clips import resolve_all


def fake_fetch(responses):
    async def fetch(url, params):
        for frag, body in responses.items():
            if frag in url:
                return body
        return {}
    return fetch


# Shaped against ClipResolver._from_deezer's genuine parse path, not guessed:
# it requires `preview` and `id`, matches the artist by `artist.name` through
# same_artist, and takes the cover from `artist.picture_medium` (NOT
# `album.cover_medium`, which the plan's draft fixture used -- that would have
# left cover_url silently empty while the test still passed).
DEEZER_HIT = {"data": [{"artist": {"name": "Songs: Ohia",
                                   "picture_medium": "https://cdn.example/c.jpg"},
                        "title": "Farewell Transmission",
                        "preview": "https://cdn.example/p.mp3",
                        "id": 1}]}


def test_resolve_all_returns_clip_fields_and_none_on_miss():
    out = asyncio.run(resolve_all(
        [("m1", "Songs: Ohia"), ("m2", "Nobody Anywhere")],
        fetch_json=fake_fetch({"deezer.com": DEEZER_HIT}),
    ))
    assert out["m1"]["preview_url"] == "https://cdn.example/p.mp3"
    assert out["m1"]["title"] == "Farewell Transmission"
    assert out["m1"]["cover_url"] == "https://cdn.example/c.jpg"
    # m2's Deezer search returns the same rows; same_artist rejects them, the
    # iTunes fallback returns {}, so the card is silent rather than wrong.
    assert out["m2"] is None


def test_a_wrong_artist_of_the_same_name_is_not_filtered_here():
    # BYP-13 is live and SHARED by both arms by design (spec §4): the name path
    # is what production uses, and giving one arm a cleaner resolver would make
    # clip quality an arm tell. This test pins that we do not "improve" it.
    out = asyncio.run(resolve_all(
        [("m1", "Songs: Ohia")],
        fetch_json=fake_fetch({"deezer.com": DEEZER_HIT}),
    ))
    assert out["m1"] is not None


def test_every_requested_mbid_gets_a_key_even_when_the_fetcher_explodes():
    async def boom(url, params):
        raise RuntimeError("network gone")

    out = asyncio.run(resolve_all([("m1", "A"), ("m2", "B")], fetch_json=boom))
    assert set(out) == {"m1", "m2"}
    assert out == {"m1": None, "m2": None}
