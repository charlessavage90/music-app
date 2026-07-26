"""FastAPI wiring. The graph, search index, and resolver are injected so the
app is testable without loading a real artifact or touching the network.
"""

from __future__ import annotations

import httpx
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from artistpath_api.clips import (
    ClipResolver, DynamoClipCache, InMemoryClipCache,
)
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.models import (
    ArtistOut, ExclusionIn, PathRequest, PathResponse, TrackOut,
)
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion, find_journey
from artistpath_api.search import ArtistSearch


def _to_exclusions(store: GraphStore, raw: list[ExclusionIn]) -> list[Exclusion]:
    out: list[Exclusion] = []
    for e in raw:
        node = store.id_by_mbid.get(e.id)
        reason = e.reason if e.reason in (DISLIKE, KNOWN) else DISLIKE
        if node is not None:
            out.append(Exclusion(node, reason))
    return out


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
        allow_headers=["content-type"],
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
    def build_path(req: PathRequest) -> PathResponse:
        if len(req.sources) != 2:
            raise HTTPException(422, "alpha supports exactly two source artists")
        ids = [store.id_by_mbid.get(m) for m in req.sources]
        if any(i is None for i in ids):
            raise HTTPException(404, "unknown artist")
        source, target = ids
        excludes = _to_exclusions(store, req.exclude)
        journey = find_journey(store, source, target, excludes, cfg)
        if journey is None:
            raise HTTPException(409, "no path avoiding those artists")
        path, stop_rule = journey
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

    return app


def build_default_app() -> FastAPI:
    """Production entrypoint: load the real graph and wire live dependencies."""
    cfg = ApiConfig()
    store = GraphStore.load(cfg.graph_path)
    search = ArtistSearch(store, cfg)
    client = httpx.AsyncClient(timeout=cfg.clip_http_timeout)

    async def fetch_json(url: str, params: dict) -> dict:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    cache = DynamoClipCache(cfg) if cfg.clip_cache == "dynamo" else InMemoryClipCache()
    resolver = ClipResolver(cfg, cache, fetch_json)
    return create_app(store, search, resolver, cfg)
