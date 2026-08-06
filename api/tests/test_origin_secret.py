"""The origin secret is what stops App Runner's public URL bypassing the gate.

TR-7: App Runner publishes its own `*.awsapprunner.com` URL and has no OAC
equivalent, so the CloudFront password gate protects the SPA and not the API.
CloudFront injects a shared header on both behaviours; requests arriving any
other way lack it.

Unset, the check must not exist at all — that is local dev and the other 180
tests, none of which set it.
"""

import asyncio
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from artistpath_api.app import create_app
from artistpath_api.clips import ClipResolver, InMemoryClipCache
from artistpath_api.config import ApiConfig
from artistpath_api.search import ArtistSearch
from tests.conftest import make_store

SECRET = "test-origin-secret"

# make_store assigns mbids as f"{i:036d}".
RADIOHEAD, COLDPLAY = f"{0:036d}", f"{2:036d}"

# QUA-3: this suite tested ONE endpoint, and the review's mutations exploited
# exactly that. Narrowing the middleware to GET-only passed 185 tests while
# leaving POST /api/path — the expensive Dijkstra — ungated. Exempting /track
# also passed, and /track is the endpoint whose unrate-limited catalogue calls
# are the gate's stated reason for existing (DEP-4). Every gated route belongs
# here, with the method it actually accepts.
#
# (method, path, json body, status when the header IS present)
GATED_ROUTES = [
    ("GET", "/api/artists/search?q=rad", None, 200),
    ("POST", "/api/path", {"sources": [RADIOHEAD, COLDPLAY]}, 200),
    # 204: the stub resolver below resolves no clip, which is a success.
    ("GET", f"/api/artists/{RADIOHEAD}/track", None, 204),
]
ROUTE_IDS = [f"{method} {path.split('?')[0]}" for method, path, _, _ in GATED_ROUTES]


def _app(secret: str):
    # w_known_ramp_fame_pctl pinned off: the origin gate is the subject, the
    # synthetic store below carries no fame, and since the MSW- adoption of
    # 2026-08-06 create_app refuses a live ramp over a fameless artifact
    # (factor-table-control idiom). Its own tests: test_pathfinding_fame_ramp.py.
    cfg = replace(ApiConfig(), origin_secret=secret, w_known_ramp_fame_pctl=0.0)
    store = make_store(
        names=["Radiohead", "Muse", "Coldplay"],
        pop_raw=[0.9, 0.7, 0.8],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.3)],
    )

    async def fetch_json(url, params):
        return {}

    resolver = ClipResolver(cfg, InMemoryClipCache(), fetch_json)
    return create_app(store, ArtistSearch(store, cfg), resolver, cfg)


def _client(secret: str) -> TestClient:
    return TestClient(_app(secret))


def _raw_asgi_status(app, path: str, headers: list[tuple[bytes, bytes]]) -> int:
    """Drive the app at the ASGI layer, bypassing any client-side validation.

    SEC-1 cannot be reproduced through TestClient: httpx rejects a non-ASCII
    header value client-side with UnicodeEncodeError, before the app is reached.
    A real request has no such client, so the bytes arrive and the app decides
    what to do with them — which is the thing under test.
    """
    sent: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("latin-1"),
        "query_string": b"q=rad",
        "root_path": "",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    asyncio.run(app(scope, receive, send))
    start = next(m for m in sent if m["type"] == "http.response.start")
    return start["status"]


@pytest.mark.parametrize("method,path,body,_served", GATED_ROUTES, ids=ROUTE_IDS)
def test_every_gated_route_refuses_a_request_without_the_header(
    method, path, body, _served
):
    r = _client(SECRET).request(method, path, json=body)
    assert r.status_code == 403


@pytest.mark.parametrize("method,path,body,_served", GATED_ROUTES, ids=ROUTE_IDS)
def test_every_gated_route_refuses_a_request_with_the_wrong_header(
    method, path, body, _served
):
    r = _client(SECRET).request(
        method, path, json=body, headers={"x-origin-secret": "wrong"}
    )
    assert r.status_code == 403


@pytest.mark.parametrize("method,path,body,served", GATED_ROUTES, ids=ROUTE_IDS)
def test_every_gated_route_is_served_with_the_right_header(
    method, path, body, served
):
    # The admitting half. Without it a middleware that refuses everything passes
    # the two above, and the API would be dead behind a gate that "works".
    r = _client(SECRET).request(
        method, path, json=body, headers={"x-origin-secret": SECRET}
    )
    assert r.status_code == served


def test_the_served_search_returns_real_content_not_just_a_status():
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


# --- SEC-1 ------------------------------------------------------------------


def test_a_non_ascii_header_is_refused_rather_than_crashing():
    # SEC-1. Compared as `str`, hmac.compare_digest raises TypeError on a
    # non-ASCII character, so this request returned 500 and wrote a traceback
    # into the telemetry log group — unauthenticated, and remote. It failed
    # closed, so it was never a bypass; it is a log-writing primitive.
    #
    # 0xE9 is a lone latin-1 "é": a byte a client can trivially send and that
    # cannot appear in the generated secret.
    status = _raw_asgi_status(
        _app(SECRET),
        "/api/artists/search",
        [(b"host", b"testserver"), (b"x-origin-secret", b"caf\xe9")],
    )
    assert status == 403


def test_the_raw_asgi_path_agrees_with_the_client_on_the_ordinary_cases():
    # The harness above bypasses httpx, so it needs its own control: if it
    # disagreed with TestClient on the cases both can express, a 403 from it
    # would prove nothing about the app.
    app = _app(SECRET)
    base = [(b"host", b"testserver")]
    assert _raw_asgi_status(app, "/api/artists/search", base) == 403
    assert (
        _raw_asgi_status(
            app, "/api/artists/search", base + [(b"x-origin-secret", b"wrong")]
        )
        == 403
    )
    assert (
        _raw_asgi_status(
            app,
            "/api/artists/search",
            base + [(b"x-origin-secret", SECRET.encode())],
        )
        == 200
    )
    assert _raw_asgi_status(app, "/health", base) == 200
