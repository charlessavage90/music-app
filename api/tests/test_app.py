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

# w_known_ramp_fame_pctl pinned off: these tests exercise routes, payloads and
# error handling over synthetic stores that carry no fame, and since the MSW-
# adoption of 2026-08-06 create_app refuses to boot a live ramp over a fameless
# artifact (factor-table-control idiom). The ramp's own behaviour — routing and
# boot — is tested in test_pathfinding_fame_ramp.py.
CFG = ApiConfig(w_known_ramp_fame_pctl=0.0)


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


# --- LUX-3: index and candidate_count -----------------------------------
#
# _client's fake fetcher answers every call with the SAME body (it is not
# URL-keyed — api-test-fixtures.md), so a two-candidate body needs two rows
# with two DIFFERENT titles here: candidates are now de-duplicated by
# normalised title (clips.py's _dedupe_by_title), and two rows sharing a
# title would collapse to one, making candidate_count == 1.
_TWO_CANDIDATES = {"any": {"data": [
    {"id": 1, "preview": "clip1.mp3", "title": "Song One",
     "artist": {"name": "Radiohead"}},
    {"id": 2, "preview": "clip2.mp3", "title": "Song Two",
     "artist": {"name": "Radiohead"}},
]}}


def test_the_track_endpoint_reports_how_many_candidates_exist():
    client, store = _client(_TWO_CANDIDATES)
    data = client.get(f"/api/artists/{store.mbids[0]}/track").json()
    # _TWO_CANDIDATES carries exactly 2 distinct titles. `>= 1` was unfailable —
    # TrackOut.candidate_count defaults to 1, so the endpoint could ignore
    # resolution.count entirely and this would still pass.
    assert data["candidate_count"] == 2


def test_the_track_endpoint_accepts_an_index():
    client, store = _client(_TWO_CANDIDATES)
    first = client.get(f"/api/artists/{store.mbids[0]}/track?index=0").json()
    second = client.get(f"/api/artists/{store.mbids[0]}/track?index=1").json()
    assert first["title"] != second["title"]


def test_a_negative_index_is_rejected_rather_than_wrapping_backwards():
    """Wrapping is for a STALE index, not a malformed one. Python's modulo would
    quietly turn -1 into the last candidate, which hides a frontend bug."""
    client, store = _client(_TWO_CANDIDATES)
    r = client.get(f"/api/artists/{store.mbids[0]}/track?index=-1")
    assert r.status_code == 422


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


def test_path_returns_the_bypassed_artists_in_press_order():
    # Two interior artists so press order is distinguishable from graph order.
    # A(0)-Mid1(1)-Mid2(2)-B(3) chain, plus a weak direct A-B edge so a path
    # still exists once both interior artists are hard-excluded.
    store = make_store(
        names=["A", "Mid1", "Mid2", "B"],
        pop_raw=[0.5, 0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (0, 3, 0.3)],
    )
    client = _client_over(store)
    a, mid1, mid2, b = store.mbids
    body = client.post(
        "/api/path",
        json={
            "sources": [a, b],
            "exclude": [
                {"id": mid2, "reason": "known"},
                {"id": mid1, "reason": "known"},
            ],
        },
    ).json()
    # Press order, not graph order: the panel draws chronology.
    assert [x["mbid"] for x in body["bypassed"]] == [mid2, mid1]
    assert body["unresolved"] == []


def test_an_mbid_not_in_the_graph_is_reported_rather_than_dropped():
    """LUX-D2. A shared link carrying a stale id used to build a path as if that
    press never happened, invisibly. The request must still succeed — a link
    that works today keeps working — but the id must come back."""
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    r = client.post(
        "/api/path",
        json={
            "sources": [a, b],
            "exclude": [{"id": "not-a-real-mbid", "reason": "known"}],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["unresolved"] == ["not-a-real-mbid"]
    assert data["bypassed"] == []


def test_a_repeated_unresolved_id_is_reported_only_once():
    """A hand-built request repeating one bad id used to yield a duplicate
    entry -- a duplicate React key and a redundant row in the route-history
    panel. `_to_exclusions` dedupes it, preserving first-seen order, the same
    way it already dedupes resolved nodes."""
    client, store = _client()
    a, b = store.mbids[0], store.mbids[2]
    r = client.post(
        "/api/path",
        json={
            "sources": [a, b],
            "exclude": [
                {"id": "not-a-real-mbid", "reason": "known"},
                {"id": "also-not-real", "reason": "known"},
                {"id": "not-a-real-mbid", "reason": "known"},
            ],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["unresolved"] == ["not-a-real-mbid", "also-not-real"]


def test_health_reports_artifact_identity():
    client, store = _client()
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["artists"] == store.artist_count
    assert body["edges"] == len(store.neighbours)
    assert body["graph_sha256"] == store.source_sha256


def test_meta_is_reachable_under_api_and_carries_the_count():
    # UXR-D8: /health is deliberately off /api (App Runner reaches it directly)
    # and CloudFront routes only /api/*, so the landing badge needs THIS route.
    client, store = _client()
    r = client.get("/api/meta")
    assert r.status_code == 200
    body = r.json()
    assert body["artists"] == store.artist_count
    assert body["graph_sha256"] == store.source_sha256


def test_meta_is_a_coroutine_so_it_never_queues_for_a_thread():
    # Same discipline as /health (G3-A1): three in-memory reads, no I/O.
    client, _ = _client()
    route = next(r for r in client.app.routes if getattr(r, "path", "") == "/api/meta")
    assert inspect.iscoroutinefunction(route.endpoint)


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


# --- LUX-4: streaming ids and structured facts on the wire -------------------
#
# ArtistOut is the wire contract the frontend reads, and it appears in FOUR
# positions, not the three the plan names: PathResponse.artists,
# PathResponse.bypassed, GET /api/artists/{mbid}, and GET
# /api/artists/search. All four are fed by app.py's one `artist_out` helper,
# which is why they cannot drift apart — these tests pin that.


def _lux4_store():
    """The three-artist store, with LUX-4 metadata on some artists and not others.

    Radiohead(0) has both ids and full facts; Muse(1) has an apple id only and
    no facts; Coldplay(2) has nothing at all — the population the search
    fallback exists for.
    """
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    store.spotify_ids = ["4Z8W4fKeB5YxbusRsdQVPb", "", ""]
    store.apple_ids = ["657515", "1006922", ""]
    store.artist_facts = [
        {"type": "Group", "country": "GB", "area": "United Kingdom",
         "begin": "1991", "end": None, "ended": False},
        {},
        {},
    ]
    return store


def test_path_artists_carry_links_and_facts():
    store = _lux4_store()
    client = _client_over(store)
    a, c = store.mbids[0], store.mbids[2]
    body = client.post("/api/path", json={"sources": [a, c]}).json()
    first = body["artists"][0]
    assert first["spotify_id"] == "4Z8W4fKeB5YxbusRsdQVPb"
    assert first["apple_id"] == "657515"
    assert first["facts"]["type"] == "Group"
    assert first["facts"]["area"] == "United Kingdom"
    assert first["facts"]["begin"] == "1991"
    assert first["facts"]["ended"] is False


def test_a_missing_id_serialises_as_null_not_as_an_empty_string():
    """The builder records "no id known" as "", but the frontend's contract is
    that NULL means "render a search link". One code path, not two."""
    store = _lux4_store()
    client = _client_over(store)
    body = client.get(f"/api/artists/{store.mbids[1]}").json()
    assert body["spotify_id"] is None      # "" in the artifact
    assert body["apple_id"] == "1006922"
    assert body["facts"] is None           # {} in the artifact


def test_absent_data_serialises_as_null_not_missing():
    """A pre-LUX-4 artifact must still serve — that is the one the app runs on
    until this deploys. The keys are PRESENT and null, so the frontend has one
    code path rather than two."""
    client, store = _client()  # a store carrying no LUX-4 metadata at all
    a, c = store.mbids[0], store.mbids[2]
    body = client.post("/api/path", json={"sources": [a, c]}).json()
    first = body["artists"][0]
    assert "spotify_id" in first and first["spotify_id"] is None
    assert "apple_id" in first and first["apple_id"] is None
    assert "facts" in first and first["facts"] is None


def test_bypassed_artists_carry_them_too():
    """LUX-2's panel renders ArtistOut, so it gets these for free — and a
    regression here would be invisible until someone pressed bypass."""
    store = make_store(
        names=["A", "Mid1", "Mid2", "B"],
        pop_raw=[0.5, 0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (0, 3, 0.3)],
    )
    store.spotify_ids = ["", "mid1-spotify", "", ""]
    client = _client_over(store)
    a, mid1, _mid2, b = store.mbids
    body = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": mid1, "reason": "known"}]},
    ).json()
    assert body["bypassed"][0]["spotify_id"] == "mid1-spotify"
    assert "facts" in body["bypassed"][0]


def test_search_results_carry_them_too():
    """The fourth wire position. Not named in the plan, and free because every
    ArtistOut on this api comes from one helper — pinned so it stays that way."""
    store = _lux4_store()
    client = _client_over(store)
    body = client.get("/api/artists/search", params={"q": "rad"}).json()
    assert body[0]["spotify_id"] == "4Z8W4fKeB5YxbusRsdQVPb"


def test_facts_drop_fields_the_extraction_never_found():
    """L4-D3 renders only what is present. A partial facts dict must not gain
    invented keys on the way out, and must not fail validation either."""
    store = _lux4_store()
    store.artist_facts = [{"type": "Person"}, {}, {}]
    client = _client_over(store)
    facts = client.get(f"/api/artists/{store.mbids[0]}").json()["facts"]
    assert facts["type"] == "Person"
    assert facts["country"] is None and facts["begin"] is None


def test_an_unknown_fact_field_does_not_break_the_api():
    """artifact.py's docstring names artist_facts as the CHEAP place to add a
    fact, so a future artifact will carry a key this ArtistFacts does not know.
    It must be ignored, not raise — otherwise adding a fact in the builder
    takes down every api instance running the older image."""
    store = _lux4_store()
    store.artist_facts = [{"type": "Group", "gender": "not-a-field-here"}, {}, {}]
    client = _client_over(store)
    r = client.get(f"/api/artists/{store.mbids[0]}")
    assert r.status_code == 200
    body = r.json()
    assert body["facts"]["type"] == "Group"
    assert "gender" not in body["facts"]
