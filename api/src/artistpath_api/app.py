"""FastAPI wiring. The graph, search index, and resolver are injected so the
app is testable without loading a real artifact or touching the network.
"""

from __future__ import annotations

import time

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from artistpath_api.artifact_source import load_graph
from artistpath_api.clips import (
    ClipResolver, DynamoClipCache, InMemoryClipCache,
)
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.models import (
    ArtistOut, ExclusionIn, HealthOut, PathRequest, PathResponse, TrackOut,
)
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion, find_journey
from artistpath_api.search import ArtistSearch
from artistpath_api.telemetry import emit, safe_journey_id


def _to_exclusions(store: GraphStore, raw: list[ExclusionIn]) -> list[Exclusion]:
    """Resolve wire exclusions to node ids, keeping the last reason per artist.

    Deduplicated because avoidance_map takes a max() per node, so a repeated
    dislike already changes nothing — it only costs another graph traversal.
    """
    by_node: dict[int, str] = {}
    for e in raw:
        node = store.id_by_mbid.get(e.id)
        if node is None:
            continue
        by_node[node] = e.reason if e.reason in (DISLIKE, KNOWN) else DISLIKE
    return [Exclusion(node, reason) for node, reason in by_node.items()]


def create_app(
    store: GraphStore,
    search: ArtistSearch,
    resolver: ClipResolver,
    cfg: ApiConfig,
) -> FastAPI:
    app = FastAPI(title="Artist Path API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cfg.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["content-type", "x-journey-id"],
    )

    def artist_out(node: int) -> ArtistOut:
        return ArtistOut(
            mbid=store.mbids[node],
            name=store.names[node],
            disambiguation=store.disambiguations[node],
            # `popularity` is the API's JSON field name, consumed by the
            # frontend (frontend/src/api/types.ts); it stays. The value is raw.
            popularity=float(store.pop_raw[node]),
        )

    @app.get("/api/artists/search")
    def search_artists(q: str) -> list[ArtistOut]:
        return [artist_out(i) for i in search.search(q)]

    @app.post("/api/path")
    def build_path(req: PathRequest, request: Request) -> PathResponse:
        if len(req.sources) != 2:
            raise HTTPException(422, "alpha supports exactly two source artists")
        ids = [store.id_by_mbid.get(m) for m in req.sources]
        if any(i is None for i in ids):
            raise HTTPException(404, "unknown artist")
        source, target = ids
        if source == target:
            raise HTTPException(
                422, "pick two different artists — a journey needs somewhere to go"
            )
        excludes = _to_exclusions(store, req.exclude)
        started = time.perf_counter()
        journey = find_journey(store, source, target, excludes, cfg)
        duration_ms = (time.perf_counter() - started) * 1000.0
        if journey is None:
            raise HTTPException(409, "no path avoiding those artists")
        path, stop_rule = journey

        emit(
            {
                "event": "path",
                "journey_id": safe_journey_id(request.headers.get("x-journey-id")),
                "source": {"mbid": store.mbids[source], "name": store.names[source]},
                "target": {"mbid": store.mbids[target], "name": store.names[target]},
                # The full accumulated list is what makes a walk reconstructible
                # from a single event, without depending on neighbouring records.
                "exclude": [{"id": e.id, "reason": e.reason} for e in req.exclude],
                "bypass_depth": len(req.exclude),
                "dislike_count": sum(1 for e in req.exclude if e.reason == DISLIKE),
                "known_count": sum(1 for e in req.exclude if e.reason == KNOWN),
                # Logged although reproducible from the inputs, so offline
                # analysis can VERIFY that the deployed router reproduces what
                # the user actually saw — config or artifact drift is a failure
                # class this project has met before (DEP-14).
                "path": [
                    {"mbid": store.mbids[n], "name": store.names[n]} for n in path
                ],
                "stop_rule": stop_rule,
                "duration_ms": round(duration_ms, 2),
            }
        )

        return PathResponse(
            artists=[artist_out(n) for n in path], stop_rule=stop_rule
        )

    @app.get("/api/artists/{mbid}/track")
    async def get_track(mbid: str, response: Response):
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        clip = await resolver.resolve(mbid, store.names[node])
        if clip is None:
            response.status_code = 204
            return None
        return TrackOut(
            preview_url=clip.preview_url, title=clip.title, cover_url=clip.cover_url
        )

    @app.get("/health")
    def health() -> HealthOut:
        # Deliberately NOT under /api — App Runner's health checker reaches the
        # origin directly, not through the CloudFront /api/* behaviour.
        return HealthOut(
            status="ok",
            graph_sha256=store.source_sha256,
            artists=store.artist_count,
            edges=len(store.neighbours),
        )

    return app


def build_default_app() -> FastAPI:
    """Production entrypoint: load the real graph and wire live dependencies."""
    cfg = ApiConfig()
    store = load_graph(cfg.graph_path, cfg.graph_sha256)
    search = ArtistSearch(store, cfg)
    client = httpx.AsyncClient(timeout=cfg.clip_http_timeout)

    async def fetch_json(url: str, params: dict) -> dict:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    cache = DynamoClipCache(cfg) if cfg.clip_cache == "dynamo" else InMemoryClipCache()
    resolver = ClipResolver(cfg, cache, fetch_json)
    return create_app(store, search, resolver, cfg)
