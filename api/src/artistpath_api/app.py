"""FastAPI wiring. The graph, search index, and resolver are injected so the
app is testable without loading a real artifact or touching the network.
"""

from __future__ import annotations

import hmac
import time

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from artistpath_api.artifact_source import load_graph
from artistpath_api.clips import (
    CatalogueUnavailable, ClipResolver, DynamoClipCache, InMemoryClipCache,
)
from artistpath_api.config import ApiConfig
from artistpath_api.graph_store import GraphStore
from artistpath_api.models import (
    ArtistFacts, ArtistOut, ExclusionIn, HealthOut, MetaOut, PathRequest, PathResponse,
    TrackOut,
)
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion, find_journey
from artistpath_api.search import ArtistSearch
from artistpath_api.telemetry import emit, safe_journey_id


def _to_exclusions(
    store: GraphStore, raw: list[ExclusionIn]
) -> tuple[list[Exclusion], list[int], list[str]]:
    """Resolve wire exclusions to node ids, keeping the last reason per artist.

    Returns the router's exclusions, the bypassed nodes in PRESS ORDER, and the
    ids that resolved to nothing.

    Deduplicated because avoidance_map takes a max() per node, so a repeated
    dislike already changes nothing — it only costs another graph traversal.
    `unresolved` is deduplicated the same way, preserving first-seen order: a
    hand-built request repeating one bad id would otherwise yield duplicate
    React keys and a redundant row in the route-history panel.

    The unresolved ids used to be discarded silently (LUX-D2). An MBID that is
    not in the graph makes the router build a path as if that press never
    happened; that was invisible until the route-history panel had to draw a
    row for it. They are returned now. The request still succeeds
    deliberately: a shared link that works today must keep working.
    """
    by_node: dict[int, str] = {}
    order: list[int] = []
    unresolved: list[str] = []
    seen_unresolved: set[str] = set()
    for e in raw:
        node = store.id_by_mbid.get(e.id)
        if node is None:
            if e.id not in seen_unresolved:
                seen_unresolved.add(e.id)
                unresolved.append(e.id)
            continue
        if node not in by_node:
            order.append(node)
        by_node[node] = e.reason if e.reason in (DISLIKE, KNOWN) else DISLIKE
    exclusions = [Exclusion(node, reason) for node, reason in by_node.items()]
    return exclusions, order, unresolved


def create_app(
    store: GraphStore,
    search: ArtistSearch,
    resolver: ClipResolver,
    cfg: ApiConfig,
) -> FastAPI:
    # Same philosophy as the graph sha check in build_default_app: a
    # misconfigured artifact refuses to START rather than serving quietly
    # wrong journeys. With the ramp switched on and no fame in the artifact,
    # every "know them already" press would silently do less than it says —
    # the failure would look like a weak feature, not a broken one, which is
    # exactly the kind that survives to production.
    if cfg.w_known_ramp_fame_pctl != 0.0 and store.fame_lb_pctl is None:
        raise ValueError(
            "w_known_ramp_fame_pctl is "
            f"{cfg.w_known_ramp_fame_pctl} but this artifact carries no "
            "fame data (no `fame_lb` key). Build it with the `fame` stage run "
            "over its archive, or set the ramp to 0.0."
        )

    app = FastAPI(title="Artist Path API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cfg.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["content-type", "x-journey-id"],
    )

    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        """Refuse an oversized body before Starlette reads it into memory.

        Content-Length only. A chunked request carrying no such header still
        gets buffered and is bounded only by the schema in models.py — recorded
        as a deferral rather than fixed, because CloudFront and Cloudflare both
        send Content-Length, so the case is currently unreachable, and reading
        the stream to count it would cost more than it is worth (G3-S3).
        """
        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > cfg.max_body_bytes:
            return JSONResponse({"detail": "request body too large"}, status_code=413)
        return await call_next(request)

    if cfg.origin_secret:
        # SEC-1: compared as `str`, hmac.compare_digest raises TypeError on any
        # non-ASCII character, so one byte >127 in this header returned 500 and
        # wrote a traceback into the telemetry log group — an unauthenticated
        # remote way to do that. It failed closed, so it was never a bypass.
        #
        # Comparing BYTES is the fix. It is NOT a simplification of the hmac
        # call, which QUA-13 records as a permanent review-only invariant with
        # no test behind it: the constant-time comparison must stay.
        #
        # Starlette decodes header values as latin-1, so encoding back with
        # latin-1 round-trips the exact bytes that arrived on the wire.
        expected_secret = cfg.origin_secret.encode("utf-8")

        @app.middleware("http")
        async def require_origin_secret(request: Request, call_next):
            # /health is exempt: App Runner's health checker reaches the origin
            # directly rather than through CloudFront, so gating it fails every
            # deploy and rolls it back. See health() below, which is deliberately
            # not under /api for the same reason.
            supplied_secret = request.headers.get("x-origin-secret", "").encode(
                "latin-1", "replace"
            )
            if request.url.path != "/health" and not hmac.compare_digest(
                supplied_secret, expected_secret
            ):
                return JSONResponse({"detail": "forbidden"}, status_code=403)
            return await call_next(request)

    def artist_out(node: int) -> ArtistOut:
        # THE ONLY PLACE ArtistOut IS CONSTRUCTED, and deliberately so: it
        # reaches the wire in four positions — PathResponse.artists,
        # PathResponse.bypassed, GET /api/artists/{mbid} and
        # GET /api/artists/search — and one helper is what stops them drifting.
        # Add a field here, not at a call site.
        facts = store.facts_of(node)
        return ArtistOut(
            mbid=store.mbids[node],
            name=store.names[node],
            disambiguation=store.disambiguations[node],
            # `popularity` is the API's JSON field name, consumed by the
            # frontend (frontend/src/api/types.ts); it stays. The value is raw.
            popularity=float(store.pop_raw[node]),
            # LUX-4. The accessors already normalise the artifact's in-band ""
            # to None; `facts` normalises {} the same way, so "the extraction
            # found nothing" and "this artifact predates LUX-4" arrive on the
            # wire identically. Both render as nothing at all (`L4-D3`).
            spotify_id=store.spotify_id_of(node),
            apple_id=store.apple_id_of(node),
            facts=ArtistFacts(**facts) if facts else None,
        )

    @app.get("/api/artists/search")
    def search_artists(q: str) -> list[ArtistOut]:
        return [artist_out(i) for i in search.search(q)]

    # Registered AFTER /api/artists/search deliberately: FastAPI matches in
    # declaration order, so the reverse makes {mbid} swallow the literal path.
    # A pure in-memory lookup — no network, no pathfinding, no clip resolution.
    # Exists so a cold load from a shared link can name the two endpoint
    # artists on the loading screen, where the URL carries only MBIDs.
    @app.get("/api/artists/{mbid}")
    def get_artist(mbid: str) -> ArtistOut:
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        return artist_out(node)

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
        excludes, bypassed_nodes, unresolved = _to_exclusions(store, req.exclude)
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
                # Count only, not the ids: `exclude` above already carries them
                # verbatim, and this line is billed per GB (G3-S3). A non-zero
                # value means shared links are going stale, which is a fact
                # nothing else can currently report.
                "unresolved_count": len(unresolved),
                # Logged although reproducible from the inputs, so offline
                # analysis can VERIFY that the deployed router reproduces what
                # the user actually saw — config or artifact drift is a failure
                # class this project has met before (DEP-14).
                "path": [
                    {"mbid": store.mbids[n], "name": store.names[n]} for n in path
                ],
                # Redundant with `path`, and deliberately so — the same trade
                # `bypass_depth` already makes against `exclude`. Log Insights
                # cannot aggregate over the length of a JSON array, so without
                # this every `by path_length` query needs an offline pass.
                #
                # TOTAL artists INCLUDING both endpoints. This is NOT the figure
                # the UI shows: the result line counts artists BETWEEN the two
                # chosen (UI-D7), so it reads `path_length - 2`. Hops are
                # `path_length - 1`. Naming the currency here because reading one
                # of these as another is a defect class this project has met
                # three times.
                "path_length": len(path),
                "stop_rule": stop_rule,
                "duration_ms": round(duration_ms, 2),
            }
        )

        return PathResponse(
            artists=[artist_out(n) for n in path],
            stop_rule=stop_rule,
            bypassed=[artist_out(n) for n in bypassed_nodes],
            unresolved=unresolved,
        )

    @app.get("/api/artists/{mbid}/track")
    async def get_track(
        mbid: str,
        request: Request,
        response: Response,
        # ge=0 deliberately: a STALE index wraps inside the resolver, but a
        # NEGATIVE one is a frontend bug, and Python's modulo would quietly
        # turn -1 into the last candidate and hide it.
        index: int = Query(0, ge=0),
    ):
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        started = time.perf_counter()
        resolution = await resolver.resolve(
            mbid, store.names[node], store.deezer_id_of(node), index
        )
        clip = resolution.clip
        duration_ms = (time.perf_counter() - started) * 1000.0

        emit(
            {
                "event": "clip",
                "journey_id": safe_journey_id(request.headers.get("x-journey-id")),
                "mbid": mbid,
                "name": store.names[node],
                "resolved": clip is not None,
                # Which catalogue answered. Three separate mechanisms produce a
                # silent card and they are visually identical; this is what
                # separates them (TR-15).
                "source": clip.source if clip else None,
                # LUX-E4 measures the candidate distribution offline before
                # launch; these two make the same question answerable from real
                # use afterwards, which is the only population that matters.
                "clip_index": index,
                "candidate_count": resolution.count,
                "duration_ms": round(duration_ms, 2),
            }
        )

        if clip is None:
            response.status_code = 204
            return None
        return TrackOut(
            preview_url=clip.preview_url,
            title=clip.title,
            cover_url=clip.cover_url,
            candidate_count=resolution.count,
        )

    @app.get("/health")
    async def health() -> HealthOut:
        # `async def`, deliberately and load-bearingly (G3-A1). A sync def runs
        # in Starlette's thread pool — the SAME pool as build_path — so under
        # concurrent path requests /health queues rather than answers: the
        # Gate 2->3 review measured 22.09 s at 40 concurrent, against App
        # Runner's 5 s health-check timeout. Five misses replace the instance,
        # its load shifts to the other one, which fails identically. The site
        # did not degrade under load, it cycled.
        #
        # Safe on the event loop because this reads three in-memory attributes
        # and does no I/O. search_artists and build_path do NOT qualify: on the
        # event loop they would block every other request.
        #
        # Deliberately NOT under /api — App Runner's health checker reaches the
        # origin directly, not through the CloudFront /api/* behaviour.
        return HealthOut(
            status="ok",
            graph_sha256=store.source_sha256,
            artists=store.artist_count,
            edges=len(store.neighbours),
        )

    @app.get("/api/meta")
    async def meta() -> MetaOut:
        # `async def` for the same reason /health is (G3-A1): in-memory reads
        # only, so it must never queue behind build_path in the thread pool.
        return MetaOut(artists=store.artist_count, graph_sha256=store.source_sha256)

    return app


def build_default_app() -> FastAPI:
    """Production entrypoint: load the real graph and wire live dependencies."""
    cfg = ApiConfig()
    store = load_graph(cfg.graph_path, cfg.graph_sha256)
    search = ArtistSearch(store, cfg)
    client = httpx.AsyncClient(timeout=cfg.clip_http_timeout)

    async def fetch_json(url: str, params: dict) -> dict:
        r = await client.get(url, params=params)
        # The only place in the app that knows httpx status codes, which is why
        # the classification lives here and not in clips.py (G3-A4): that module
        # must not import the transport. 429 is the measured case; 5xx carries
        # the same instruction — stop calling — from a different cause.
        if r.status_code == 429 or r.status_code >= 500:
            raise CatalogueUnavailable(f"{r.status_code} from {url}")
        r.raise_for_status()
        return r.json()

    cache = DynamoClipCache(cfg) if cfg.clip_cache == "dynamo" else InMemoryClipCache()
    resolver = ClipResolver(cfg, cache, fetch_json)
    return create_app(store, search, resolver, cfg)
