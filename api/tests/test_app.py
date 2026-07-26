from fastapi.testclient import TestClient

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
