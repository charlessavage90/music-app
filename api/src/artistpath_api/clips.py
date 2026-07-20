"""30-second clip resolution: Deezer primary, iTunes fallback, cached.

The path endpoint never calls this (spec 5.2); clips are resolved per-card on
demand. A missing clip leaves the card unplayable but never alters routing.

Response shapes verified against the live Deezer and iTunes APIs (2026-07).
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from artistpath_api.config import ApiConfig

FetchJson = Callable[[str, dict], Awaitable[dict]]


@dataclass(frozen=True, slots=True)
class Clip:
    preview_url: str
    title: str
    cover_url: str


class ClipCache(Protocol):
    def get(self, mbid: str) -> Clip | None: ...
    def put(self, mbid: str, clip: Clip) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, Clip] = {}

    def get(self, mbid: str) -> Clip | None:
        return self._store.get(mbid)

    def put(self, mbid: str, clip: Clip) -> None:
        self._store[mbid] = clip


class DynamoClipCache:
    """Production cache: DynamoDB with a 30-day TTL (spec 5.1)."""

    def __init__(self, cfg: ApiConfig, table=None) -> None:
        self._cfg = cfg
        if table is None:
            import boto3

            table = boto3.resource("dynamodb").Table(cfg.clip_table_name)
        self._table = table

    def get(self, mbid: str) -> Clip | None:
        item = self._table.get_item(Key={"mbid": mbid}).get("Item")
        if not item:
            return None
        return Clip(item["preview_url"], item["title"], item["cover_url"])

    def put(self, mbid: str, clip: Clip) -> None:
        ttl = int(time.time()) + self._cfg.clip_ttl_days * 86400
        self._table.put_item(
            Item={
                "mbid": mbid,
                "preview_url": clip.preview_url,
                "title": clip.title,
                "cover_url": clip.cover_url,
                "ttl": ttl,
            }
        )


class ClipResolver:
    def __init__(self, cfg: ApiConfig, cache: ClipCache, fetch_json: FetchJson) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json

    async def resolve(self, mbid: str, artist_name: str) -> Clip | None:
        cached = self._cache.get(mbid)
        if cached is not None:
            return cached
        clip = await self._from_deezer(artist_name) or await self._from_itunes(artist_name)
        if clip is not None:
            self._cache.put(mbid, clip)
        return clip

    async def _from_deezer(self, artist_name: str) -> Clip | None:
        body = await self._fetch(
            self._cfg.deezer_search_url, {"q": artist_name, "limit": 1}
        )
        for row in body.get("data", []):
            preview = row.get("preview")
            if preview:
                artist = row.get("artist") or {}
                return Clip(preview, row.get("title", ""), artist.get("picture_medium", ""))
        return None

    async def _from_itunes(self, artist_name: str) -> Clip | None:
        body = await self._fetch(
            self._cfg.itunes_search_url,
            {"term": artist_name, "entity": "song", "limit": 1},
        )
        for row in body.get("results", []):
            preview = row.get("previewUrl")
            if preview:
                return Clip(preview, row.get("trackName", ""), row.get("artworkUrl100", ""))
        return None
