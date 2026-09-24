"""`build_default_app` — the production wiring — under test (G3-Q1).

Every guard it arms is tested on its own elsewhere: the checksum in
test_artifact_source.py, the Dynamo cache in test_clips.py, the breaker's
default in test_clips.py. What nothing tested was the function that ARMS them,
so each of three one-line mutations — drop the sha256 argument, force the
in-memory cache, drop the HTTP timeout — passed the whole suite. That is the
DEP-24 / QUA-2 shape: every guard tested, the wiring that arms them untested.

No network and no AWS. The graph is the committed 500-node fixture; the
config is injected by replacing the module's `ApiConfig` (its env defaults are
read at import, so monkeypatching the environment after import would change
nothing); the Dynamo cache builds its boto3 resource lazily, so constructing
it touches nothing; and the HTTP client is given a mock transport.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys

import anyio
import httpx
import pytest
from fastapi.testclient import TestClient

import artistpath_api.app as app_module
from artistpath_api.clips import (
    CatalogueUnavailable, ClipResolver, DynamoClipCache, InMemoryClipCache,
)
from artistpath_api.config import ApiConfig
from tests.conftest import FIXTURES

FIXTURE_GRAPH = FIXTURES / "graph-fixture.bin"
FIXTURE_SHA = hashlib.sha256(FIXTURE_GRAPH.read_bytes()).hexdigest()
# Not httpx's own default (5 s) and not ApiConfig's (10 s), so an assertion on
# it can only pass if the configured value was actually passed through.
DISTINCT_TIMEOUT = 7.25


def anyio_run(coro):
    async def _run():
        return await coro

    return anyio.run(_run)


def _cfg(**overrides) -> ApiConfig:
    base = dict(
        graph_path=str(FIXTURE_GRAPH),
        graph_sha256=FIXTURE_SHA,
        # The fixture carries no fame; create_app refuses a live ramp over it.
        w_known_ramp_fame_pctl=0.0,
        clip_cache="memory",
        clip_http_timeout=DISTINCT_TIMEOUT,
    )
    base.update(overrides)
    return ApiConfig(**base)


@pytest.fixture
def wiring(monkeypatch):
    """Run build_default_app under a given config, capturing what it built.

    Returns a function: cfg -> (app, resolver, http_client). Spies subclass
    the real classes, so the objects under test are the real ones.
    """
    resolvers: list[ClipResolver] = []
    clients: list[httpx.AsyncClient] = []
    handler_box: dict = {"handler": lambda request: httpx.Response(200, json={})}

    class SpyResolver(ClipResolver):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            resolvers.append(self)

    class SpyClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            # The transport is the only thing added: the kwargs build_default_app
            # passed (the timeout among them) are kept exactly as given.
            kwargs["transport"] = httpx.MockTransport(
                lambda request: handler_box["handler"](request)
            )
            super().__init__(*args, **kwargs)
            clients.append(self)

    monkeypatch.setattr(app_module, "ClipResolver", SpyResolver)
    monkeypatch.setattr(app_module.httpx, "AsyncClient", SpyClient)

    def build(cfg: ApiConfig, handler=None):
        if handler is not None:
            handler_box["handler"] = handler
        monkeypatch.setattr(app_module, "ApiConfig", lambda: cfg)
        app = app_module.build_default_app()
        assert len(resolvers) == 1 and len(clients) == 1
        return app, resolvers[0], clients[0]

    return build


# --- the graph, and the checksum that guards it ---------------------------------

def test_boots_the_configured_graph_and_reports_its_identity(wiring):
    app, _, _ = wiring(_cfg())
    body = TestClient(app).get("/health").json()
    assert body["artists"] == 500
    assert body["graph_sha256"] == FIXTURE_SHA


def test_refuses_to_boot_on_a_checksum_mismatch(wiring):
    # The production guard (DEP-24): the wrong artifact must not start. If
    # build_default_app stops passing cfg.graph_sha256 to load_graph, this
    # boots and the test fails.
    with pytest.raises(ValueError, match="checksum mismatch"):
        wiring(_cfg(graph_sha256="0" * 64))


def test_an_empty_checksum_still_boots_for_local_development(wiring):
    app, _, _ = wiring(_cfg(graph_sha256=""))
    assert TestClient(app).get("/health").json()["artists"] == 500


# --- the clip cache the config selects ------------------------------------------

def test_dynamo_is_used_when_configured(wiring):
    # Production sets ARTISTPATH_CLIP_CACHE=dynamo. Forcing the in-memory cache
    # would pass every other test and lose the cache on every instance restart.
    _, resolver, _ = wiring(_cfg(clip_cache="dynamo", clip_table_name="t-under-test"))
    cache = resolver._cache
    assert isinstance(cache, DynamoClipCache)
    assert cache._cfg.clip_table_name == "t-under-test"
    assert cache._table is None  # lazily built: booting touched no AWS


def test_memory_is_used_by_default(wiring):
    _, resolver, _ = wiring(_cfg(clip_cache="memory"))
    assert isinstance(resolver._cache, InMemoryClipCache)


# --- the outbound HTTP client ---------------------------------------------------

def test_the_http_client_carries_the_configured_timeout(wiring):
    # Without it httpx's own 5 s default applies silently — and every other
    # test injects fetch_json, so nothing else would notice.
    _, _, client = wiring(_cfg())
    assert client.timeout == httpx.Timeout(DISTINCT_TIMEOUT)


def test_the_resolver_fetches_through_that_client(wiring):
    seen: list[httpx.Request] = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"data": ["ok"]})

    _, resolver, _ = wiring(_cfg(), handler)
    body = anyio_run(resolver._fetch("https://api.deezer.com/search", {"q": "x"}))
    assert body == {"data": ["ok"]}
    assert len(seen) == 1 and seen[0].url.params["q"] == "x"


@pytest.mark.parametrize("status", [429, 500, 503])
def test_throttling_and_server_errors_are_classified_as_unavailable(wiring, status):
    # G3-A4: this classification lives in build_default_app's fetch_json and
    # is what feeds the circuit breaker. Lose it and a throttled catalogue
    # looks like "no clip" — the breaker never opens.
    _, resolver, _ = wiring(_cfg(), lambda request: httpx.Response(status))
    with pytest.raises(CatalogueUnavailable):
        anyio_run(resolver._fetch("https://api.deezer.com/search", {}))


def test_a_404_is_an_ordinary_error_not_unavailability(wiring):
    # A withdrawn track 404s routinely; that must trigger a re-search, not
    # count toward opening the breaker.
    _, resolver, _ = wiring(_cfg(), lambda request: httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        anyio_run(resolver._fetch("https://api.deezer.com/track/1", {}))


# --- the config reaches create_app ----------------------------------------------

def test_the_config_reaches_the_app(wiring):
    # Checked through one setting whose effect is observable from outside: the
    # origin secret gates /api/* (TR-7). If build_default_app handed create_app
    # a fresh default config instead of its own, this would be open.
    app, _, _ = wiring(_cfg(origin_secret="s3cret"))
    client = TestClient(app)
    assert client.get("/api/meta").status_code == 403
    assert client.get("/api/meta", headers={"x-origin-secret": "s3cret"}).status_code == 200


# --- the environment variable names infra sets reach ApiConfig ------------------

def test_the_environment_the_stack_sets_reaches_the_config():
    # infra/tests/test_stack.py pins the NAMES the App Runner service is given;
    # this pins that the api reads those same names. Run in a fresh interpreter
    # because ApiConfig reads the environment at import.
    env = {
        **os.environ,
        "ARTISTPATH_GRAPH": "s3://bucket/graph-x.bin",
        "ARTISTPATH_GRAPH_SHA256": "ab" * 32,
        "ARTISTPATH_CLIP_CACHE": "dynamo",
        "ARTISTPATH_CLIP_TABLE": "table-x",
        "ARTISTPATH_ORIGIN_SECRET": "secret-x",
    }
    code = (
        "from artistpath_api.config import ApiConfig; c = ApiConfig(); "
        "print(c.graph_path, c.graph_sha256, c.clip_cache, c.clip_table_name, "
        "c.origin_secret)"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True,
        check=True,
    ).stdout.split()
    assert out == ["s3://bucket/graph-x.bin", "ab" * 32, "dynamo", "table-x", "secret-x"]
