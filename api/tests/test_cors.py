from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store


def _client(cfg):
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )
    search = ArtistSearch(store, cfg)

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, search, resolver, cfg))


def test_cors_allows_configured_dev_origin():
    client = _client(ApiConfig())
    r = client.get(
        "/api/artists/search",
        params={"q": "rad"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_absent_for_unlisted_origin():
    client = _client(ApiConfig())
    r = client.get(
        "/api/artists/search",
        params={"q": "rad"},
        headers={"Origin": "http://evil.example"},
    )
    assert "access-control-allow-origin" not in r.headers
