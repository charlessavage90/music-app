"""The origin secret is what stops App Runner's public URL bypassing the gate.

TR-7: App Runner publishes its own `*.awsapprunner.com` URL and has no OAC
equivalent, so the CloudFront password gate protects the SPA and not the API.
CloudFront injects a shared header on both behaviours; requests arriving any
other way lack it.

Unset, the check must not exist at all — that is local dev and the other 180
tests, none of which set it.
"""

from dataclasses import replace

from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

SECRET = "test-origin-secret"


def _client(secret: str) -> TestClient:
    cfg = replace(ApiConfig(), origin_secret=secret)
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    return TestClient(create_app(store, ArtistSearch(store, cfg), resolver, cfg))


def test_request_without_the_header_is_refused():
    r = _client(SECRET).get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 403


def test_request_with_the_wrong_header_is_refused():
    r = _client(SECRET).get(
        "/api/artists/search",
        params={"q": "rad"},
        headers={"x-origin-secret": "wrong"},
    )
    assert r.status_code == 403


def test_request_with_the_right_header_is_served():
    r = _client(SECRET).get(
        "/api/artists/search",
        params={"q": "rad"},
        headers={"x-origin-secret": SECRET},
    )
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Radiohead"


def test_health_is_exempt_because_app_runner_probes_the_origin_directly():
    # App Runner's health checker does not come through CloudFront and cannot
    # be given the header. Gating /health makes every deploy fail its health
    # check and roll back.
    r = _client(SECRET).get("/health")
    assert r.status_code == 200


def test_an_empty_secret_disables_the_check_entirely():
    r = _client("").get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 200
