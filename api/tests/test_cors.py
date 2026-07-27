"""CORS is off unless something turns it on.

RMD-6 / SEC-1's neighbour: the default was http://localhost:5173 until
2026-07-27, and that dev default was live in production. The stack sets
ARTISTPATH_CORS_ORIGINS to the empty string exactly so this would not happen —
but an empty-valued environment variable does not reach a running App Runner
service, so the API fell back to its default and told browsers that a page on
anyone's dev server could read its responses.

The guarantee therefore moved into ApiConfig, where absence is safe. These tests
hold both halves: the default allows nothing, and an explicit setting still
works.
"""

from dataclasses import replace

from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

DEV_ORIGIN = "http://localhost:5173"


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


def _allowed_origin(cfg, origin: str) -> str | None:
    r = _client(cfg).get(
        "/api/artists/search", params={"q": "rad"}, headers={"Origin": origin}
    )
    assert r.status_code == 200
    return r.headers.get("access-control-allow-origin")


def test_the_default_config_allows_no_origin_at_all():
    # The whole point of RMD-6. If this ever goes back to naming a default
    # origin, that origin is live in production the next time the deployed
    # service drops the variable — which is what happened, and which nothing
    # downstream detected.
    assert ApiConfig().cors_origins == ()
    assert _allowed_origin(ApiConfig(), DEV_ORIGIN) is None


def test_an_explicitly_configured_origin_is_allowed():
    # The admitting half: without it, a config that allows nothing ever would
    # pass the test above and CORS would be silently unusable.
    cfg = replace(ApiConfig(), cors_origins=(DEV_ORIGIN,))
    assert _allowed_origin(cfg, DEV_ORIGIN) == DEV_ORIGIN


def test_cors_absent_for_unlisted_origin():
    cfg = replace(ApiConfig(), cors_origins=(DEV_ORIGIN,))
    assert _allowed_origin(cfg, "http://evil.example") is None
