from artistpath_api.clips import Clip, ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig

CFG = ApiConfig()
MBID = "a" * 36

DEEZER_HIT = {
    "data": [
        {"preview": "https://cdn.deezer/clip.mp3",
         "title": "Paranoid Android",
         "artist": {"name": "Radiohead", "picture_medium": "https://cdn/rh.jpg"}}
    ]
}
ITUNES_HIT = {
    "results": [
        {"previewUrl": "https://cdn.itunes/clip.m4a",
         "trackName": "Karma Police",
         "artworkUrl100": "https://cdn/itunes.jpg"}
    ]
}


def _resolver(responses, cache=None):
    """responses maps a url-substring to the dict it returns."""
    calls = []

    async def fetch_json(url, params):
        calls.append((url, params))
        for frag, body in responses.items():
            if frag in url:
                return body
        return {}

    r = ClipResolver(CFG, cache or InMemoryClipCache(), fetch_json)
    r.calls = calls
    return r


async def test_resolves_from_deezer_first():
    r = _resolver({"deezer": DEEZER_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.deezer/clip.mp3"
    assert clip.title == "Paranoid Android"


async def test_falls_back_to_itunes_when_deezer_empty():
    r = _resolver({"deezer": {"data": []}, "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"
    assert clip.title == "Karma Police"


async def test_returns_none_when_no_source_has_a_clip():
    r = _resolver({"deezer": {"data": []}, "itunes": {"results": []}})
    assert await r.resolve(MBID, "Nobody") is None


async def test_cache_hit_skips_the_network():
    cache = InMemoryClipCache()
    cache.put(MBID, Clip("cached.mp3", "Cached", "cover.jpg"))
    r = _resolver({"deezer": DEEZER_HIT}, cache=cache)
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.title == "Cached"
    assert r.calls == []  # never hit the network


async def test_successful_resolution_is_cached():
    cache = InMemoryClipCache()
    r = _resolver({"deezer": DEEZER_HIT}, cache=cache)
    await r.resolve(MBID, "Radiohead")
    assert cache.get(MBID).title == "Paranoid Android"


async def test_deezer_entry_without_preview_is_skipped():
    # A Deezer hit lacking a preview URL must fall through to iTunes.
    no_preview = {"data": [{"preview": "", "title": "X", "artist": {"name": "Y"}}]}
    r = _resolver({"deezer": no_preview, "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"
