import asyncio
import inspect
import json
import threading

import anyio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.pathfinding import DISLIKE
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

CFG = ApiConfig()


def _client(clip_responses=None):
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    search = ArtistSearch(store, CFG)

    async def fetch_json(url, params):
        return (clip_responses or {}).get("any", {})

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, search, resolver, CFG)), store


def _client_over(store):
    """A client over a purpose-built graph, for tests that need a given shape."""

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, ArtistSearch(store, CFG), resolver, CFG))


def test_search_endpoint_returns_matches():
    client, _ = _client()
    r = client.get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Radiohead"


def test_path_endpoint_returns_ordered_artists():
    client, store = _client()
    a, c = store.mbids[0], store.mbids[2]
    r = client.post("/api/path", json={"sources": [a, c], "exclude": []})
    assert r.status_code == 200
    names = [x["name"] for x in r.json()["artists"]]
    assert names[0] == "Radiohead" and names[-1] == "Coldplay"


def test_path_respects_a_typed_exclusion():
    client, store = _client()
    a, b, c = store.mbids
    # Exclude Muse (the smooth middle); path must still connect via the weak edge.
    r = client.post(
        "/api/path",
        json={"sources": [a, c], "exclude": [{"id": b, "reason": "dislike"}]},
    )
    assert r.status_code == 200
    names = [x["name"] for x in r.json()["artists"]]
    assert "Muse" not in names


def test_path_with_unknown_artist_is_404():
    client, _ = _client()
    r = client.post("/api/path", json={"sources": ["z" * 36, "y" * 36], "exclude": []})
    assert r.status_code == 404


def test_path_requires_exactly_two_sources():
    client, store = _client()
    r = client.post("/api/path", json={"sources": [store.mbids[0]], "exclude": []})
    assert r.status_code == 422


def test_track_endpoint_returns_clip():
    # store.mbids[0] is Radiohead; the row must name that artist and carry a
    # track id, since C1 matches on the artist and C2 caches the id.
    client, store = _client({"any": {"data": [
        {"id": 7, "preview": "clip.mp3", "title": "Song",
         "artist": {"name": "Radiohead", "picture_medium": "c.jpg"}}
    ]}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 200
    assert r.json()["preview_url"] == "clip.mp3"


def test_track_endpoint_looks_up_the_requested_artists_own_deezer_id():
    """The wiring, which is where an off-by-one would live (`BYP-13`).

    The resolver is well covered on its own, but nothing pinned that the
    endpoint hands it the id of the artist actually being asked for. Passing a
    fixed or neighbouring node's id would give one artist's card another
    artist's clip — this feature's own failure mode, arriving by a different
    route — and every other test in the suite still passed with that mutation.
    """
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    store.deezer_ids = ["111", "222", "333"]
    urls: list[str] = []

    async def fetch_json(url, params):
        urls.append(url)
        return {"data": [{"id": 7, "preview": "clip.mp3", "title": "Song",
                          "artist": {"name": "Muse", "picture_medium": "c.jpg"}}]}

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    client = TestClient(create_app(store, ArtistSearch(store, CFG), resolver, CFG))

    assert client.get(f"/api/artists/{store.mbids[1]}/track").status_code == 200
    assert any("/artist/222/top" in u for u in urls)
    assert not any("/artist/111/top" in u or "/artist/333/top" in u for u in urls)


def test_track_endpoint_serves_no_clip_rather_than_the_wrong_artist():
    """C1, end to end: a title collision must not reach the card."""
    client, store = _client({"any": {"data": [
        {"id": 8, "preview": "wrong.mp3", "title": "Radiohead",
         "artist": {"name": "Some Other Band"}}
    ]}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 204


def test_track_endpoint_204_not_500_when_the_catalogue_fails():
    """A rate-limited or unreachable catalogue must not 500 the card.

    The production fetcher calls raise_for_status, so this is the shape a
    Deezer 429 actually arrives in. A path view fires 8-10 of these.
    """
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )

    async def fetch_json(url, params):
        raise RuntimeError("429 Too Many Requests")

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    client = TestClient(create_app(store, ArtistSearch(store, CFG), resolver, CFG))

    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 204


def test_track_endpoint_204_when_no_clip():
    client, store = _client({"any": {"data": []}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 204


def test_path_response_reports_a_natural_journey():
    # The existing fixture routes Radiohead -> Muse -> Coldplay: already has a stop.
    client, store = _client()
    a, c = store.mbids[0], store.mbids[2]
    body = client.post("/api/path", json={"sources": [a, c], "exclude": []}).json()
    assert body["stop_rule"] == "natural"
    assert len(body["artists"]) >= 3


def test_path_response_reports_a_forced_stop():
    # Radiohead and Muse are directly connected; Coldplay is the way round.
    client, store = _client()
    a, b = store.mbids[0], store.mbids[1]
    body = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    assert body["stop_rule"] == "forced"
    assert len(body["artists"]) >= 3
    assert [x["name"] for x in body["artists"]][0] == "Radiohead"


def test_path_endpoint_is_409_when_hard_exclusions_disconnect_the_endpoints():
    # C is the only way from A to B; excluding it disconnects them.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 2, 0.9), (2, 1, 0.9)],
    )
    client = _client_over(store)
    a, b, c = store.mbids
    r = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": c, "reason": DISLIKE}]},
    )
    assert r.status_code == 409


def test_path_response_reports_two_artists_with_nothing_between():
    # B's only connection is to A, so no stop can exist between them.
    store = make_store(
        names=list("ABC"), pop_raw=[0.5] * 3,
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    client = _client_over(store)
    a, b = store.mbids[0], store.mbids[1]
    body = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    assert [x["name"] for x in body["artists"]] == ["A", "B"]
    assert body["stop_rule"] == "adjacent_only"


def test_same_artist_for_both_endpoints_is_rejected():
    client, store = _client()
    mbid = store.mbids[0]
    r = client.post("/api/path", json={"sources": [mbid, mbid], "exclude": []})
    assert r.status_code == 422


def test_an_over_long_exclude_list_is_rejected():
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    excludes = [{"id": store.mbids[1], "reason": "dislike"} for _ in range(201)]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": excludes})
    assert r.status_code == 422


def test_duplicate_exclusions_are_collapsed():
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    dupes = [{"id": store.mbids[1], "reason": "dislike"} for _ in range(50)]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": dupes})
    assert r.status_code == 200


def test_an_unrecognised_reason_is_still_coerced_to_dislike():
    """Pins behaviour the deploy design relies on and nothing tested (TR-7).

    Tightening ExclusionIn.reason to a Literal is the natural tidy-up and would
    silently turn this 200 into a 422 for any client sending a stale reason.
    """
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    r = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": store.mbids[1], "reason": "BANANA"}]},
    )
    assert r.status_code == 200


def test_health_reports_artifact_identity():
    client, store = _client()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["artists"] == store.artist_count
    assert body["edges"] == len(store.neighbours)
    assert body["graph_sha256"] == store.source_sha256


def test_path_request_emits_a_telemetry_event(capsys):
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": store.mbids[1], "reason": "known"}]},
        headers={"x-journey-id": "journey-0001"},
    )
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("{")]
    events = [json.loads(ln) for ln in lines]
    path_events = [e for e in events if e["event"] == "path"]
    assert len(path_events) == 1
    ev = path_events[0]
    assert ev["journey_id"] == "journey-0001"
    assert ev["source"]["mbid"] == a
    assert ev["target"]["mbid"] == b
    assert ev["bypass_depth"] == 1
    assert ev["known_count"] == 1
    assert ev["dislike_count"] == 0
    assert ev["stop_rule"] in ("natural", "forced", "adjacent_only")
    assert [p["mbid"] for p in ev["path"]][0] == a
    assert isinstance(ev["duration_ms"], (int, float))
    # The integer must agree with the array it summarises, or every Log Insights
    # aggregate over it is quietly wrong. Pins the currency too: TOTAL artists,
    # not the interior count the UI displays.
    assert ev["path_length"] == len(ev["path"])
    assert ev["path_length"] >= 2


def test_track_request_emits_a_clip_event(capsys):
    client, store = _client()
    client.get(
        f"/api/artists/{store.mbids[0]}/track",
        headers={"x-journey-id": "journey-0002"},
    )
    events = [
        json.loads(ln)
        for ln in capsys.readouterr().out.splitlines()
        if ln.startswith("{")
    ]
    clip_events = [e for e in events if e["event"] == "clip"]
    assert len(clip_events) == 1
    ev = clip_events[0]
    assert ev["journey_id"] == "journey-0002"
    assert ev["mbid"] == store.mbids[0]
    assert ev["resolved"] is False   # the test fetcher returns no clip
    assert ev["source"] is None
    assert isinstance(ev["duration_ms"], (int, float))


# --- request bounds (PW-1: G3-S3, and the amplification half of G3-S4) -------
#
# One task because they are one fix. The 20 MB of CloudWatch the Gate 2->3
# review measured came from unbounded id strings being echoed verbatim into the
# telemetry line, so bounding the strings closes both findings.


def test_an_oversized_sources_array_is_rejected_by_the_schema_not_the_handler():
    # G3-S3: a 2,000,000-element array cost 442 ms and buffered ~70 MB before
    # the `len(...) != 2` check in build_path rejected it. The bound has to be
    # in the schema, which runs before the handler.
    #
    # Asserting `status_code == 422` alone is VACUOUS and passed before this
    # fix existed: build_path already raises 422 for "alpha supports exactly
    # two source artists" — but it raises it AFTER the whole array has been
    # parsed and materialised, which is the entire finding. The two are told
    # apart by the shape of `detail`: FastAPI gives a LIST of pydantic errors
    # for a schema violation and a STRING for HTTPException's message.
    client, _ = _client()
    r = client.post("/api/path", json={"sources": ["x"] * 5000, "exclude": []})
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, list), (
        "rejected by the handler, not the schema — the array was fully "
        f"materialised before anything checked its size: {detail!r}"
    )
    assert any(e["type"] == "too_long" for e in detail), detail


def test_an_oversized_exclusion_id_is_rejected():
    # G3-S4: ExclusionIn.id is echoed verbatim into the telemetry line, so an
    # unbounded string is a log-volume amplifier billed per GB, not only a
    # parse cost. The review measured 1:1 amplification.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": "z" * 5000, "reason": "dislike"}],
        },
    )
    assert r.status_code == 422


def test_an_oversized_exclusion_reason_is_rejected():
    # `reason` is normalised to dislike/known in _to_exclusions, but the RAW
    # value is what app.py logs. Bounding it at the normalisation would not
    # bound the log line.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": store.mbids[1], "reason": "z" * 5000}],
        },
    )
    assert r.status_code == 422


def test_a_body_over_the_limit_is_refused_before_parsing():
    # The schema bounds cannot fire until the whole body has been read into
    # memory. This is the cheap guard in front of that.
    client, _ = _client()
    r = client.post(
        "/api/path",
        content=b'{"sources":[],"exclude":[]}' + b" " * (CFG.max_body_bytes + 1),
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 413


def test_an_ordinary_two_artist_request_still_works():
    # The half a bounds test cannot see on its own: a limit set too tight
    # refuses real traffic, and every test above passes when it does.
    client, store = _client()
    r = client.post(
        "/api/path",
        json={
            "sources": [store.mbids[0], store.mbids[2]],
            "exclude": [{"id": store.mbids[1], "reason": "dislike"}],
        },
    )
    assert r.status_code == 200


# --- /health off the thread pool (PW-2: G3-A1's feedback loop) ---------------


def test_health_is_a_coroutine_so_it_never_queues_for_a_thread():
    # /health shares Starlette's thread pool with build_path. The Gate 2->3
    # review measured it at 22.09 s under 40 concurrent path requests, against
    # App Runner's 5 s health-check timeout — and five misses replace the
    # instance, whose load shifts to the other one, which fails the same way.
    # The site did not degrade under load, it cycled.
    #
    # Asserted by introspection AS WELL AS behaviourally below, because the
    # regression is a single keyword: `async def` reverted to `def` is
    # invisible to every test that does not saturate the pool first.
    client, _ = _client()
    route = next(r for r in client.app.routes if getattr(r, "path", "") == "/health")
    assert inspect.iscoroutinefunction(route.endpoint), (
        "/health is a sync def and will queue behind saturated path requests"
    )


def test_health_answers_while_every_thread_pool_slot_is_occupied():
    """The behavioural half: the property, not the keyword.

    Occupies every thread-pool slot with a blocking sync endpoint, then asks
    for /health. A sync /health cannot answer until a slot frees — the 22.09 s
    the review measured. A coroutine answers off the event loop regardless.
    """
    client, _ = _client()
    app = client.app

    release = threading.Event()

    @app.get("/blocking-probe")
    def blocking_probe():  # sync on purpose: it consumes a pool slot
        release.wait(timeout=10)
        return {"ok": True}

    async def exercise():
        limiter = anyio.to_thread.current_default_thread_limiter()
        original = limiter.total_tokens
        limiter.total_tokens = 2  # saturate cheaply rather than spawning 40
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                blockers = [
                    asyncio.create_task(ac.get("/blocking-probe")) for _ in range(2)
                ]
                await asyncio.sleep(0.2)  # let both claim their slot
                r = await asyncio.wait_for(ac.get("/health"), timeout=2.0)
                assert r.status_code == 200
                release.set()
                await asyncio.gather(*blockers)
        finally:
            release.set()
            limiter.total_tokens = original

    asyncio.run(exercise())


def test_artist_lookup_returns_the_artist():
    client, store = _client()
    r = client.get(f"/api/artists/{store.mbids[0]}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Radiohead"
    assert body["mbid"] == store.mbids[0]


def test_artist_lookup_404s_on_an_unknown_mbid():
    client, _ = _client()
    assert client.get("/api/artists/not-a-real-mbid").status_code == 404


# REGRESSION GUARD, not a red-first test: this passes before the change too.
# It exists because FastAPI matches routes in declaration order, so registering
# {mbid} ahead of `search` would make it swallow the literal path and this is
# the only thing that would notice.
def test_artist_lookup_does_not_shadow_the_search_route():
    client, _ = _client()
    r = client.get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Radiohead"
