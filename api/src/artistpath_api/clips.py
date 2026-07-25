"""30-second clip resolution: Deezer primary, iTunes fallback, cached.

The path endpoint never calls this (spec 5.2); clips are resolved per-card on
demand. A missing clip leaves the card unplayable but never alters routing.

Response shapes verified against the live Deezer and iTunes APIs (2026-07).
"""

from __future__ import annotations

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
    def get(self, mbid: str) -> TrackIdentity | None: ...
    def put(self, mbid: str, identity: TrackIdentity) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, TrackIdentity] = {}

    def get(self, mbid: str) -> TrackIdentity | None:
        return self._store.get(mbid)

    def put(self, mbid: str, identity: TrackIdentity) -> None:
        self._store[mbid] = identity


class DynamoClipCache:
    """Production cache: DynamoDB with a 30-day TTL (spec 5.1).

    Stores track *identity* only. A signed preview URL must never be written
    here: the TTL is 30 days and the signature lasts under an hour, which is
    what made every cache hit past the first hour serve dead audio (C2).

    The boto3 resource is created lazily on first use, so constructing the
    cache (and therefore booting the app) never requires AWS to be reachable.
    """

    def __init__(self, cfg: ApiConfig, table=None) -> None:
        self._cfg = cfg
        self._table = table

    def _get_table(self):
        if self._table is None:
            import boto3

            self._table = boto3.resource("dynamodb").Table(self._cfg.clip_table_name)
        return self._table

    def get(self, mbid: str) -> TrackIdentity | None:
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

    def put(self, mbid: str, identity: TrackIdentity) -> None:
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


class ClipResolver:
    def __init__(self, cfg: ApiConfig, cache: ClipCache, fetch_json: FetchJson) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json

    async def resolve(self, mbid: str, artist_name: str) -> Clip | None:
        """Resolve a playable clip, re-signing the URL on every request (C2).

        A cached identity costs one lookup. A cold artist costs one search,
        whose response already carries a signed URL — so the common paths are
        one round trip each.
        """
        identity = self._cache.get(mbid)
        if identity is not None:
            url = await self._preview_url(identity)
            if url:
                return Clip(url, identity.title, identity.cover_url)
            # The track has left the catalogue. Identity is stable, not
            # permanent, so fall through and find the artist another one.

        found = await self._search(artist_name)
        if found is None:
            return None
        identity, url = found
        self._cache.put(mbid, identity)
        return Clip(url, identity.title, identity.cover_url)

    async def _preview_url(self, identity: TrackIdentity) -> str | None:
        """Re-sign a known track. Returns None if it is no longer available."""
        if identity.source == "deezer":
            body = await self._fetch(
                f"{self._cfg.deezer_track_url}/{identity.track_id}", {}
            )
            return body.get("preview") or None
        body = await self._fetch(
            self._cfg.itunes_lookup_url, {"id": identity.track_id}
        )
        for row in body.get("results", []):
            if row.get("previewUrl"):
                return row["previewUrl"]
        return None

    async def _search(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        return await self._from_deezer(artist_name) or await self._from_itunes(artist_name)

    async def _from_deezer(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        body = await self._fetch(
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
                    title=row.get("title", ""),
                    cover_url=artist.get("picture_medium", ""),
                )
                return identity, preview
        return None

    async def _from_itunes(self, artist_name: str) -> tuple[TrackIdentity, str] | None:
        body = await self._fetch(
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
                    title=row.get("trackName", ""),
                    cover_url=row.get("artworkUrl100", ""),
                )
                return identity, preview
        return None
