"""End-to-end checks on the committed 200-artist real-data fixture."""

from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch

CFG = ApiConfig()


def _client(fixture_store):
    search = ArtistSearch(fixture_store, CFG)

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(CFG, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(fixture_store, search, resolver, CFG))


def test_fixture_has_real_artists(fixture_store):
    # 500 since Phase 2 Task 16 regenerated the fixture from the adopted
    # `capfix` graph at the plan's specified --size 500 (was 200).
    assert fixture_store.artist_count == 500
    assert all(len(m) == 36 for m in fixture_store.mbids)


def test_path_between_two_fixture_artists_is_valid(fixture_store):
    client = _client(fixture_store)
    a, b = fixture_store.mbids[0], fixture_store.mbids[-1]
    r = client.post("/api/path", json={"sources": [a, b], "exclude": []})
    assert r.status_code == 200
    artists = r.json()["artists"]
    # Endpoints correct, and every adjacent pair is a real edge.
    assert artists[0]["mbid"] == a and artists[-1]["mbid"] == b
    ids = [fixture_store.id_by_mbid[x["mbid"]] for x in artists]
    edges = {(u, v) for u in range(fixture_store.artist_count)
             for v, _ in fixture_store.neighbours_of(u)}
    for x, y in zip(ids, ids[1:]):
        assert (x, y) in edges


def test_bypass_reroll_excludes_the_artist(fixture_store):
    client = _client(fixture_store)
    a, b = fixture_store.mbids[0], fixture_store.mbids[-1]
    first = client.post("/api/path", json={"sources": [a, b], "exclude": []}).json()
    if len(first["artists"]) < 3:
        return  # need a middle artist to bypass
    middle = first["artists"][1]["mbid"]
    second = client.post(
        "/api/path",
        json={"sources": [a, b], "exclude": [{"id": middle, "reason": "dislike"}]},
    ).json()
    assert middle not in [x["mbid"] for x in second["artists"]]
