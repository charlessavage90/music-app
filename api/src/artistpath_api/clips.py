"""30-second clip resolution: Deezer primary, iTunes fallback, cached.

The path endpoint never calls this (spec 5.2); clips are resolved per-card on
demand. A missing clip leaves the card unplayable but never alters routing.

Search response shapes verified against the live Deezer and iTunes APIs
(2026-07). The per-track lookup shapes added for C2 (`/track/{id}` and
`/lookup?id=`) are taken from the published API documentation and have NOT
been exercised against the live services — the tests inject a fake fetcher,
so a wrong field name here would pass every test and produce a silent card.
Confirming a clip still plays an hour after page load is the check that
covers it, and it is queued in docs/superpowers/TEST-QUEUE.md.
"""

from __future__ import annotations

import asyncio
import time
import unicodedata
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from artistpath_api.config import ApiConfig

FetchJson = Callable[[str, dict], Awaitable[dict]]


def _fold(name: str) -> str:
    """Casefold, strip accents, and collapse whitespace for artist matching.

    MusicBrainz and the clip catalogues disagree routinely on diacritics and
    casing for the same artist, so an exact comparison would reject correct
    matches and leave the card silent.
    """
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.casefold().split())


def same_artist(candidate: str | None, requested: str) -> bool:
    """Does this search result actually belong to the artist we asked for? (C1)"""
    return bool(candidate) and _fold(candidate) == _fold(requested)


@dataclass(frozen=True, slots=True)
class Clip:
    """What a card plays. Short-lived: `preview_url` is signed and expires."""

    preview_url: str
    title: str
    cover_url: str
    source: str = ""  # "deezer" | "itunes" — for telemetry, not for the wire


@dataclass(frozen=True, slots=True)
class TrackIdentity:
    """The stable half of a clip — safe to cache for 30 days (C2).

    Deliberately holds no signed URL. `source` and `track_id` are enough to
    re-resolve one on demand, which is also what keeps the Gate-3 options
    open: proxying or pre-signing needs a stable track reference, not a URL
    someone cached (roadmap, "the clip architecture has a Gate-3 ceiling").
    """

    source: str  # "deezer" | "itunes"
    track_id: str
    title: str
    cover_url: str


class ClipCache(Protocol):
    async def get(self, mbid: str) -> TrackIdentity | None: ...
    async def put(self, mbid: str, identity: TrackIdentity) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, TrackIdentity] = {}

    async def get(self, mbid: str) -> TrackIdentity | None:
        return self._store.get(mbid)

    async def put(self, mbid: str, identity: TrackIdentity) -> None:
        self._store[mbid] = identity


class DynamoClipCache:
    """Production cache: DynamoDB with a 30-day TTL (spec 5.1).

    Stores track *identity* only. A signed preview URL must never be written
    here: the TTL is 30 days and the signature expires far sooner (measurement:
    the roadmap's confirmed-diagnoses C2), which is what made every cache hit
    past the first hour serve dead audio.

    The boto3 resource is created lazily on first use, so constructing the
    cache (and therefore booting the app) never requires AWS to be reachable.

    Both methods are async and hand the blocking boto3 call to a worker thread.
    The clip endpoint is the only async route in the app, so a synchronous
    round trip here blocks the event loop for every concurrent user (DEP-11).
    asyncio.to_thread is used deliberately in preference to adding aioboto3 —
    a thread fixes this without a new dependency.
    """

    def __init__(self, cfg: ApiConfig, table=None) -> None:
        self._cfg = cfg
        self._table = table

    def _get_table(self):
        if self._table is None:
            import boto3

            self._table = boto3.resource("dynamodb").Table(self._cfg.clip_table_name)
        return self._table

    def _get_sync(self, mbid: str) -> TrackIdentity | None:
        item = self._get_table().get_item(Key={"mbid": mbid}).get("Item")
        # Items written before C2 carry a long-expired URL and no track id.
        # They cannot be re-resolved, so they are a miss and get overwritten.
        if not item or "track_id" not in item:
            return None
        return TrackIdentity(
            source=item["source"],
            track_id=item["track_id"],
            title=item["title"],
            cover_url=item["cover_url"],
        )

    def _put_sync(self, mbid: str, identity: TrackIdentity) -> None:
        ttl = int(time.time()) + self._cfg.clip_ttl_days * 86400
        self._get_table().put_item(
            Item={
                "mbid": mbid,
                "source": identity.source,
                "track_id": identity.track_id,
                "title": identity.title,
                "cover_url": identity.cover_url,
                "ttl": ttl,
            }
        )

    async def get(self, mbid: str) -> TrackIdentity | None:
        return await asyncio.to_thread(self._get_sync, mbid)

    async def put(self, mbid: str, identity: TrackIdentity) -> None:
        await asyncio.to_thread(self._put_sync, mbid, identity)


class ClipResolver:
    def __init__(self, cfg: ApiConfig, cache: ClipCache, fetch_json: FetchJson) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json

    async def _get(self, url: str, params: dict) -> dict:
        """Fetch, treating any failure as "no answer" rather than an error.

        A clip is decorative — it never affects routing — so a catalogue that
        is down, rate-limiting, or missing a track must produce a silent card
        and never a 500. The production fetcher calls `raise_for_status`, so
        failures arrive here as exceptions rather than as inspectable bodies;
        a 404 for a withdrawn track is the common case, and it is what makes
        `resolve`'s re-search fire.

        Rate limiting is the live risk rather than a theoretical one: a single
        path view fires a clip lookup per card (count and consequence: the
        roadmap's "the clip architecture has a Gate-3 ceiling"), and re-signing
        means a *repeat* view now costs a request per card where it used to
        cost none.

        **Only the call is guarded**, deliberately. Wrapping the parsing too
        would swallow our own bugs — a renamed field would look exactly like
        an outage, which is the failure this whole area keeps producing.
        """
        try:
            return await self._fetch(url, params)
        except Exception:
            # Deliberately broad: the fetcher is injected, so this layer
            # cannot name the transport's exception types without coupling
            # to httpx. Observability for this is a Gate 2 item.
            return {}

    async def resolve(self, mbid: str, artist_name: str) -> Clip | None:
        """Resolve a playable clip, re-signing the URL on every request (C2).

        A cached identity costs one lookup. A cold artist costs one search,
        whose response already carries a signed URL — so the common paths are
        one round trip each.
        """
        # A cache failure must never reach the caller. The endpoint's contract
        # is a clip or silence, never a 500 (see this module's docstring), and
        # in production the cache is DynamoDB, which can throttle (DEP-12).
        try:
            identity = await self._cache.get(mbid)
        except Exception:
            identity = None

        if identity is not None:
            url = await self._preview_url(identity)
            if url:
                return Clip(url, identity.title, identity.cover_url, identity.source)
            # The track has left the catalogue. Identity is stable, not
            # permanent, so fall through and find the artist another one.

        found = await self._search(artist_name)
        if found is None:
            return None
        identity, url = found
        # A write failure happens AFTER a successful lookup, so the clip is
        # already in hand. Losing it to a cache error would discard work we
        # have done and silence a card that plays perfectly well (DEP-26).
        try:
            await self._cache.put(mbid, identity)
        except Exception:
            pass
        return Clip(url, identity.title, identity.cover_url, identity.source)

    async def _preview_url(self, identity: TrackIdentity) -> str | None:
        """Re-sign a known track. Returns None if it is no longer available."""
        if identity.source == "deezer":
            body = await self._get(
                f"{self._cfg.deezer_track_url}/{identity.track_id}", {}
            )
            return body.get("preview") or None
        body = await self._get(
            self._cfg.itunes_lookup_url, {"id": identity.track_id}
        )
        for row in body.get("results", []):
            if row.get("previewUrl"):
                return row["previewUrl"]
        return None

    async def _search(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        return await self._from_deezer(artist_name) or await self._from_itunes(artist_name)

    async def _from_deezer(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        body = await self._get(
            self._cfg.deezer_search_url,
            {"q": artist_name, "limit": self._cfg.clip_search_limit},
        )
        for row in body.get("data", []):
            preview, track_id = row.get("preview"), row.get("id")
            artist = row.get("artist") or {}
            if preview and track_id and same_artist(artist.get("name"), artist_name):
                identity = TrackIdentity(
                    source="deezer",
                    track_id=str(track_id),
                    # `or ""` not a .get default: these keys can be present
                    # with a JSON null, and TrackOut's fields are typed str,
                    # so None here becomes a 500 at the endpoint.
                    title=str(row.get("title") or ""),
                    cover_url=str(artist.get("picture_medium") or ""),
                )
                return identity, preview
        return None

    async def _from_itunes(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        body = await self._get(
            self._cfg.itunes_search_url,
            {
                "term": artist_name,
                "entity": "song",
                "limit": self._cfg.clip_search_limit,
            },
        )
        for row in body.get("results", []):
            preview, track_id = row.get("previewUrl"), row.get("trackId")
            if preview and track_id and same_artist(row.get("artistName"), artist_name):
                identity = TrackIdentity(
                    source="itunes",
                    track_id=str(track_id),
                    title=str(row.get("trackName") or ""),
                    cover_url=str(row.get("artworkUrl100") or ""),
                )
                return identity, preview
        return None
