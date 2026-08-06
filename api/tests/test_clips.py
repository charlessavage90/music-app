from artistpath_api.breaker import CatalogueBreaker
from artistpath_api.clips import (
    CatalogueUnavailable, ClipResolver, DynamoClipCache, InMemoryClipCache,
    TrackIdentity,
)
from artistpath_api.config import ApiConfig

CFG = ApiConfig()
MBID = "a" * 36

# A /search response, which carries a FULL artist object and an album block.
# The card's image comes from the album (see clips.py `_album_cover`); the
# artist photograph is kept here because the real response has one, and because
# its presence is what distinguishes this endpoint from /artist/{id}/top.
DEEZER_HIT = {
    "data": [
        {"id": 771, "preview": "https://cdn.deezer/clip.mp3",
         "title": "Paranoid Android",
         "artist": {"name": "Radiohead", "picture_medium": "https://cdn/rh.jpg"},
         "album": {"id": 3, "title": "OK Computer",
                   "cover_medium": "https://cdn/okc.jpg", "type": "album"}}
    ]
}
ITUNES_HIT = {
    "results": [
        {"trackId": 991, "previewUrl": "https://cdn.itunes/clip.m4a",
         "trackName": "Karma Police", "artistName": "Radiohead",
         "artworkUrl100": "https://cdn/itunes.jpg"}
    ]
}

# The C1 defect, from the roadmap's worked example: Deezer's search matches song
# titles as well as artist names, so a search for "The Format" returns a track
# *called* "The Format" by an unrelated artist above the real one.
DEEZER_TITLE_COLLISION = {
    "data": [
        {"id": 1, "preview": "https://cdn.deezer/az.mp3", "title": "The Format",
         "artist": {"name": "AZ", "picture_medium": "https://cdn/az.jpg"}},
        {"id": 2, "preview": "https://cdn.deezer/holy-roller.mp3",
         "title": "Holy Roller",
         "artist": {"name": "The Format", "picture_medium": "https://cdn/tf.jpg"}},
    ]
}


class Boom(Exception):
    """Stands in for httpx raising on a 404, a rate-limit, or a timeout.

    The real fetcher calls `raise_for_status`, so a failing catalogue reaches
    the resolver as an exception — never as a body it can inspect.
    """


def _resolver(responses, cache=None, breaker=None):
    """responses maps a url-substring to the dict it returns.

    A value that is an exception instance is raised instead of returned.
    """
    calls = []

    async def fetch_json(url, params):
        calls.append((url, params))
        for frag, body in responses.items():
            if frag in url:
                if isinstance(body, Exception):
                    raise body
                return body
        return {}

    r = ClipResolver(CFG, cache or InMemoryClipCache(), fetch_json, breaker=breaker)
    r.calls = calls
    return r


# --- resolution ---------------------------------------------------------


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


async def test_deezer_entry_without_preview_is_skipped():
    # A Deezer hit lacking a preview URL must fall through to iTunes.
    no_preview = {"data": [{"id": 3, "preview": "", "title": "X",
                            "artist": {"name": "Radiohead"}}]}
    r = _resolver({"deezer": no_preview, "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"


# --- C1: the clip must belong to the artist we asked for ----------------


async def test_skips_a_title_match_by_the_wrong_artist():
    """C1. 'The Format' returns a *song* called The Format by AZ above the band."""
    r = _resolver({"deezer": DEEZER_TITLE_COLLISION})
    clip = await r.resolve(MBID, "The Format")
    assert clip.preview_url == "https://cdn.deezer/holy-roller.mp3"
    assert clip.title == "Holy Roller"


async def test_asks_deezer_for_more_than_one_result():
    """C1. A one-row response cannot be filtered — the wrong artist is all there is."""
    r = _resolver({"deezer": DEEZER_HIT})
    await r.resolve(MBID, "Radiohead")
    _, params = r.calls[0]
    assert params["limit"] > 1


async def test_no_clip_at_all_beats_a_clip_by_the_wrong_artist():
    """C1. When nothing matches the artist, play nothing rather than someone else."""
    only_wrong = {"data": [{"id": 1, "preview": "https://cdn.deezer/az.mp3",
                            "title": "The Format",
                            "artist": {"name": "AZ"}}]}
    r = _resolver({"deezer": only_wrong, "itunes": {"results": []}})
    assert await r.resolve(MBID, "The Format") is None


async def test_itunes_results_are_matched_on_artist_too():
    """C1. The fallback had no artist check at all, so it had the same defect."""
    wrong_then_right = {
        "results": [
            {"trackId": 1, "previewUrl": "https://cdn.itunes/wrong.m4a",
             "trackName": "The Format", "artistName": "AZ"},
            {"trackId": 2, "previewUrl": "https://cdn.itunes/right.m4a",
             "trackName": "Holy Roller", "artistName": "The Format"},
        ]
    }
    r = _resolver({"deezer": {"data": []}, "itunes": wrong_then_right})
    clip = await r.resolve(MBID, "The Format")
    assert clip.preview_url == "https://cdn.itunes/right.m4a"


async def test_artist_match_ignores_case_and_accents():
    """Real catalogues disagree with MusicBrainz on diacritics and casing."""
    body = {"data": [{"id": 4, "preview": "https://cdn.deezer/bjork.mp3",
                      "title": "Army of Me",
                      "artist": {"name": "BJÖRK"}}]}
    r = _resolver({"deezer": body})
    clip = await r.resolve(MBID, "Bjork")
    assert clip.preview_url == "https://cdn.deezer/bjork.mp3"


# --- C2: identity is cached, the signed URL never is --------------------
#
# Deezer preview URLs are signed and expire in under an hour; the cache holds
# entries for 30 days. Caching the URL is what made every hit past the first
# hour serve dead audio.


async def test_the_cache_never_holds_a_signed_url():
    """C2. The volatile half must not enter a 30-day store."""
    cache = InMemoryClipCache()
    r = _resolver({"deezer": DEEZER_HIT}, cache=cache)
    await r.resolve(MBID, "Radiohead")

    identity = await cache.get(MBID)
    assert identity == TrackIdentity(
        source="deezer", track_id="771",
        title="Paranoid Android", cover_url="https://cdn/okc.jpg",
    )
    assert "clip.mp3" not in repr(identity)


async def test_a_cached_track_gets_a_freshly_signed_url():
    """C2. The URL is re-resolved per request, so it is never the stale one."""
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "771", "Paranoid Android", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/771": {"id": 771, "preview": "https://cdn.deezer/FRESH.mp3"},
    }, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.deezer/FRESH.mp3"
    assert clip.title == "Paranoid Android"


async def test_a_cached_track_is_not_searched_for_again():
    """C2. Identity is stable; only the URL is volatile. Search is the expensive call."""
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "771", "Paranoid Android", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/771": {"preview": "https://cdn.deezer/fresh.mp3"},
    }, cache=cache)

    await r.resolve(MBID, "Radiohead")
    assert not any("search" in url for url, _ in r.calls)


async def test_a_cold_lookup_does_not_pay_for_a_second_round_trip():
    """The search response already carries a signed URL — use it."""
    r = _resolver({"deezer": DEEZER_HIT})
    await r.resolve(MBID, "Radiohead")
    assert len(r.calls) == 1


async def test_an_itunes_track_is_re_resolved_through_itunes():
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("itunes", "991", "Karma Police", "cover.jpg"))
    r = _resolver({
        "itunes.apple.com/lookup": {
            "results": [{"trackId": 991, "previewUrl": "https://cdn.itunes/fresh.m4a"}]
        },
    }, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/fresh.m4a"


async def test_a_track_pulled_from_the_catalogue_is_searched_for_again():
    """Identity is stable but not permanent — a dead id must self-heal."""
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "999", "Gone", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/999": {"error": {"type": "DataException"}},
        "deezer.com/search": DEEZER_HIT,
    }, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.deezer/clip.mp3"
    assert await cache.get(MBID) == TrackIdentity(
        "deezer", "771", "Paranoid Android", "https://cdn/okc.jpg"
    )


async def test_no_clip_when_the_track_is_gone_and_the_artist_has_no_other():
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "999", "Gone", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/999": {},
        "deezer.com/search": {"data": []},
        "itunes": {"results": []},
    }, cache=cache)
    assert await r.resolve(MBID, "Radiohead") is None


# --- C2: the production cache stores the same shape ---------------------


class FakeTable:
    def __init__(self, item=None):
        self.item = item
        self.written = None

    def get_item(self, Key):
        return {"Item": self.item} if self.item else {}

    def put_item(self, Item):
        self.written = Item


async def test_dynamo_cache_writes_identity_and_no_url():
    table = FakeTable()
    await DynamoClipCache(CFG, table).put(
        MBID, TrackIdentity("deezer", "771", "Paranoid Android", "cover.jpg")
    )
    assert table.written["track_id"] == "771"
    assert table.written["source"] == "deezer"
    assert "preview_url" not in table.written


# --- a failing catalogue must never reach the caller -------------------
#
# The production fetcher calls raise_for_status, and nothing in the package
# catches. A clip is decorative: any failure must degrade to a silent card,
# never to a 500. Deezer rate-limits, and a path view fires 8-10 lookups.


async def test_a_deezer_outage_falls_back_to_itunes():
    r = _resolver({"deezer": Boom("429 rate limited"), "itunes": ITUNES_HIT})
    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.itunes/clip.m4a"


async def test_both_catalogues_failing_yields_no_clip_rather_than_an_error():
    r = _resolver({"deezer": Boom("500"), "itunes": Boom("timeout")})
    assert await r.resolve(MBID, "Radiohead") is None


async def test_a_404_on_the_cached_track_re_searches():
    """The self-heal must fire on a raised 404, not only on an error body.

    A track pulled from the catalogue is a 404 — the shape this path will
    actually meet in production.
    """
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "999", "Gone", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/999": Boom("404 not found"),
        "deezer.com/search": DEEZER_HIT,
    }, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")
    assert clip.preview_url == "https://cdn.deezer/clip.mp3"
    assert (await cache.get(MBID)).track_id == "771"


async def test_a_rate_limited_lookup_does_not_evict_a_good_cached_track():
    """A transient failure must not cost us the identity we already had."""
    cache = InMemoryClipCache()
    known = TrackIdentity("deezer", "771", "Paranoid Android", "cover.jpg")
    await cache.put(MBID, known)
    r = _resolver({
        "deezer.com/track/771": Boom("429 rate limited"),
        "deezer.com/search": Boom("429 rate limited"),
        "itunes": Boom("429 rate limited"),
    }, cache=cache)

    assert await r.resolve(MBID, "Radiohead") is None
    assert await cache.get(MBID) == known  # still there for the next request


async def test_a_bug_in_our_own_parsing_is_not_swallowed():
    """Only the network call is guarded. Our own errors must still surface."""
    class Exploding(dict):
        def get(self, *a, **k):
            raise AssertionError("parsing bug")

    async def fetch_json(url, params):
        return Exploding()

    r = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    try:
        await r.resolve(MBID, "Radiohead")
    except AssertionError as e:
        assert "parsing bug" in str(e)
    else:
        raise AssertionError("a parsing bug was swallowed by the network guard")


async def test_dynamo_cache_treats_a_pre_c2_item_as_a_miss():
    """Items written before this fix hold a long-dead signed URL and no track id."""
    stale = {"mbid": MBID, "preview_url": "https://cdn.deezer/expired.mp3",
             "title": "Old", "cover_url": "cover.jpg"}
    assert await DynamoClipCache(CFG, FakeTable(stale)).get(MBID) is None


class ExplodingCache:
    """A cache whose every operation fails, like DynamoDB throttling."""

    def __init__(self, fail_get=True, fail_put=True):
        self.fail_get = fail_get
        self.fail_put = fail_put

    async def get(self, mbid):
        if self.fail_get:
            raise RuntimeError("dynamo unavailable")
        return None

    async def put(self, mbid, identity):
        if self.fail_put:
            raise RuntimeError("dynamo throttled")


_DEEZER_OK = {
    "data": [
        {
            "preview": "https://p.example/x.mp3",
            "id": 5,
            "title": "Song",
            "artist": {"name": "Some Artist", "picture_medium": "cover"},
        }
    ]
}


async def test_a_failing_cache_read_is_treated_as_a_miss():
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return _DEEZER_OK

    resolver = ClipResolver(cfg, ExplodingCache(fail_get=True, fail_put=False), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.preview_url == "https://p.example/x.mp3"


async def test_a_failing_cache_write_still_returns_the_clip():
    """The catalogue lookup already succeeded; losing the clip to a cache
    write failure would discard something we are holding."""
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return _DEEZER_OK

    resolver = ClipResolver(cfg, ExplodingCache(fail_get=False, fail_put=True), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.title == "Song"


async def test_a_null_title_from_the_catalogue_does_not_crash():
    cfg = ApiConfig()

    async def fetch_json(url, params):
        return {
            "data": [
                {
                    "preview": "https://p.example/x.mp3",
                    "id": 5,
                    "title": None,
                    "artist": {"name": "Some Artist", "picture_medium": None},
                }
            ]
        }

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.title == ""
    assert clip.cover_url == ""


async def test_dynamo_cache_round_trips_through_the_resolver():
    """Drives DynamoClipCache through ClipResolver rather than calling it directly.

    The existing FakeTable tests call .get/.put straight, so nothing exercised
    the cache through the code path production uses (TR-11).
    """
    cfg = ApiConfig()
    table = FakeTable(
        item={
            "mbid": "m1",
            "source": "deezer",
            "track_id": "77",
            "title": "T",
            "cover_url": "c",
        }
    )
    cache = DynamoClipCache(cfg, table)

    async def fetch_json(url, params):
        return {"preview": "https://signed.example/x.mp3"}

    resolver = ClipResolver(cfg, cache, fetch_json)
    clip = await resolver.resolve("m1", "Some Artist")
    assert clip is not None
    assert clip.preview_url == "https://signed.example/x.mp3"
    assert clip.title == "T"


# --- a THROTTLED catalogue is not a missing track (PW-3: G3-A4, G3-S2) ------
#
# `_get` swallowed every exception into `{}`, so a 429 looked exactly like a
# 404. `resolve` then fell through cache-hit -> search -> iTunes, so ONE user
# request became TWO Deezer calls plus one iTunes call while Deezer was already
# refusing us. viewer_function.js names that fan-out, in source, as the reason
# the site's shared password exists.
#
# The classification happens in the INJECTED fetcher, not here: naming httpx's
# exception types in clips.py is what the broad `except` exists to avoid.


def _deezer_calls(resolver):
    return [url for url, _ in resolver.calls if "deezer" in url]


async def test_a_throttled_deezer_is_not_asked_again_for_the_same_artist():
    # The cached-identity path re-signs a URL through /track. When that comes
    # back 429, falling through to _search asks the SAME service twice more.
    # One call is the correct number.
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "999", "Song", "cover.jpg"))
    r = _resolver({"deezer": CatalogueUnavailable("429")}, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")

    assert clip is None
    assert len(_deezer_calls(r)) == 1, (
        f"asked a throttled Deezer {len(_deezer_calls(r))} times"
    )


async def test_a_track_that_left_the_catalogue_still_falls_through_to_a_search():
    # The half the fix must not break. A 404 for a withdrawn track is a genuine
    # miss, and re-searching is what keeps the card playable. Only
    # UNAVAILABILITY stops the fall-through.
    cache = InMemoryClipCache()
    await cache.put(MBID, TrackIdentity("deezer", "999", "Gone", "cover.jpg"))
    r = _resolver({
        "deezer.com/track/999": Boom("404 not found"),
        "deezer.com/search": DEEZER_HIT,
    }, cache=cache)

    clip = await r.resolve(MBID, "Radiohead")

    assert clip is not None
    assert clip.preview_url == "https://cdn.deezer/clip.mp3"


async def test_a_throttled_deezer_still_falls_through_to_itunes_on_a_cold_artist():
    # Falling through to a DIFFERENT service is not amplification — it is the
    # fallback working. Only repeat calls to the refusing service are the bug.
    r = _resolver({
        "deezer": CatalogueUnavailable("429"),
        "itunes": ITUNES_HIT,
    })

    clip = await r.resolve(MBID, "Radiohead")

    assert clip is not None
    assert clip.source == "itunes"
    assert len(_deezer_calls(r)) == 1


async def test_an_open_breaker_makes_no_outbound_call_at_all():
    # The point of the whole task. PW-3 made one request cost one call instead
    # of three; without a breaker, a thousand requests still cost a thousand
    # calls to a service that is refusing us, which is what keeps the block in
    # place rather than letting it clear.
    breaker = CatalogueBreaker(threshold=2, cooldown_s=60.0)
    r = _resolver({"deezer": CatalogueUnavailable("429")}, breaker=breaker)

    for _ in range(5):
        await r.resolve(MBID, "Radiohead")

    assert len(_deezer_calls(r)) == 2, (
        f"kept calling a refusing Deezer {len(_deezer_calls(r))} times; "
        "the breaker should have stopped it after 2"
    )


async def test_an_open_deezer_breaker_leaves_itunes_usable():
    # A breaker that silenced every card whenever one catalogue was throttled
    # would be a worse defect than the one being fixed.
    breaker = CatalogueBreaker(threshold=1, cooldown_s=60.0)
    r = _resolver({
        "deezer": CatalogueUnavailable("429"),
        "itunes": ITUNES_HIT,
    }, breaker=breaker)

    await r.resolve(MBID, "Radiohead")          # trips the breaker
    clip = await r.resolve("b" * 36, "Radiohead")

    assert clip is not None and clip.source == "itunes"
    assert len(_deezer_calls(r)) == 1


async def test_a_resolver_built_without_one_still_gets_a_breaker():
    # The wiring, not the guard. build_default_app constructs ClipResolver with
    # no breaker argument and relies on the constructor default to arm one, and
    # every other breaker test INJECTS a breaker — so a default that stopped
    # arming it would leave the whole of PW-4 dead in production with all tests
    # still green. That is G3-Q1's shape exactly, and it is the failure class
    # the Gate 2->3 review named.
    r = _resolver({"deezer": CatalogueUnavailable("429"), "itunes": {}})

    for _ in range(CFG.clip_breaker_threshold + 3):
        await r.resolve(MBID, "Radiohead")

    assert len(_deezer_calls(r)) == CFG.clip_breaker_threshold, (
        f"{len(_deezer_calls(r))} calls to a refusing Deezer with the DEFAULT "
        f"breaker; expected it to stop at {CFG.clip_breaker_threshold}"
    )
