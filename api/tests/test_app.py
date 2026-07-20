from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

CFG = ApiConfig()


def _client(clip_responses=None):
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        popularity=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    search = ArtistSearch(store, CFG)

    async def fetch_json(url, params):
        return (clip_responses or {}).get("any", {})

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, search, resolver, CFG)), store


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
    client, store = _client({"any": {"data": [
        {"preview": "clip.mp3", "title": "Song", "artist": {"picture_medium": "c.jpg"}}
    ]}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 200
    assert r.json()["preview_url"] == "clip.mp3"


def test_track_endpoint_204_when_no_clip():
    client, store = _client({"any": {"data": []}})
    r = client.get(f"/api/artists/{store.mbids[0]}/track")
    assert r.status_code == 204
