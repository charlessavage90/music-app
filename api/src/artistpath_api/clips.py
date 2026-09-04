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

from artistpath_api.breaker import CatalogueBreaker
from artistpath_api.config import ApiConfig

FetchJson = Callable[[str, dict], Awaitable[dict]]


class CatalogueUnavailable(Exception):
    """The catalogue refused to answer — throttling or an outage, not a miss.

    Raised by the INJECTED fetcher, never by this module. Naming httpx's
    exception types here would couple the resolver to the transport, which is
    the reason `_get` is broad in the first place; classifying at the fetcher
    keeps that boundary while giving this layer the one distinction it needs.

    That distinction is the whole of G3-A4: a 429 that reads as "no such track"
    makes `resolve` ask the same refusing service twice more, tripling our
    outbound rate at exactly the moment it has to fall.
    """


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


def _album_cover(row: dict) -> str:
    """The card's image, from a Deezer track row's ALBUM rather than its artist.

    Deezer embeds a different artist object per endpoint: `/search` sends a full
    one carrying `picture_medium`, `/artist/{id}/top` sends four keys and no
    picture at all. Reading the photograph therefore worked on the name path and
    silently produced "" on the id path -- a card that played but showed a blank
    square, on roughly half of all artists once the clip cache drained.

    The album block is on BOTH responses, so this needs no extra request, and it
    is what the iTunes path already returns (`artworkUrl100`). One field, one
    meaning, all three paths.

    `or ""` throughout, not `.get` defaults: Deezer sends these keys present-and-
    null, and TrackOut types cover_url as str, so a None here is a 500 at the
    endpoint rather than a missing image.
    """
    album = row.get("album") or {}
    return str(album.get("cover_medium") or "")


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


@dataclass(frozen=True, slots=True)
class Resolution:
    """A clip and how many others the artist has.

    `count` is what lets the UI hide a "try another" control that would do
    nothing. Thin catalogues are a studied population here (TCE-/TCR-) and are
    exactly the artists this app exists to deliver, so the endpoint states the
    count rather than letting the frontend guess it.
    """

    clip: Clip | None
    count: int


class ClipCache(Protocol):
    async def get(self, mbid: str) -> list[TrackIdentity] | None: ...
    async def put(self, mbid: str, identities: list[TrackIdentity]) -> None: ...


class InMemoryClipCache:
    """Dev/test cache. Not shared across processes."""

    def __init__(self) -> None:
        self._store: dict[str, list[TrackIdentity]] = {}

    async def get(self, mbid: str) -> list[TrackIdentity] | None:
        return self._store.get(mbid)

    async def put(self, mbid: str, identities: list[TrackIdentity]) -> None:
        self._store[mbid] = identities


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

    def _get_sync(self, mbid: str) -> list[TrackIdentity] | None:
        item = self._get_table().get_item(Key={"mbid": mbid}).get("Item")
        # Items written before C2 carry a long-expired URL and no track id.
        # Items written before LUX-3 carry a single flat track and cannot say
        # how many candidates there were. Both are a miss and get overwritten;
        # the 30-day TTL (clip_ttl_days) drains the old shapes unaided, which is
        # why there is no migration here and must not be one.
        if not item or "tracks" not in item:
            return None
        return [
            TrackIdentity(
                source=t["source"],
                track_id=t["track_id"],
                title=t["title"],
                cover_url=t["cover_url"],
            )
            for t in item["tracks"]
        ]

    def _put_sync(self, mbid: str, identities: list[TrackIdentity]) -> None:
        ttl = int(time.time()) + self._cfg.clip_ttl_days * 86400
        self._get_table().put_item(
            Item={
                "mbid": mbid,
                "tracks": [
                    {
                        "source": i.source,
                        "track_id": i.track_id,
                        "title": i.title,
                        "cover_url": i.cover_url,
                    }
                    for i in identities
                ],
                "ttl": ttl,
            }
        )

    async def get(self, mbid: str) -> list[TrackIdentity] | None:
        return await asyncio.to_thread(self._get_sync, mbid)

    async def put(self, mbid: str, identities: list[TrackIdentity]) -> None:
        await asyncio.to_thread(self._put_sync, mbid, identities)


class ClipResolver:
    def __init__(
        self,
        cfg: ApiConfig,
        cache: ClipCache,
        fetch_json: FetchJson,
        breaker: CatalogueBreaker | None = None,
    ) -> None:
        self._cfg = cfg
        self._cache = cache
        self._fetch = fetch_json
        # Optional so every existing call site keeps working unchanged, and
        # built from cfg when absent so production gets one without app.py
        # having to know it exists.
        self._breaker = breaker or CatalogueBreaker(
            threshold=cfg.clip_breaker_threshold,
            cooldown_s=cfg.clip_breaker_cooldown_s,
        )

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
        except CatalogueUnavailable:
            # NOT swallowed, and it is the one failure that must not be. The
            # correct response to "you are calling me too much" is to stop
            # calling, not to try harder — and a 429 read as a miss does the
            # opposite (G3-A4).
            raise
        except Exception:
            # Deliberately broad: the fetcher is injected, so this layer
            # cannot name the transport's exception types without coupling
            # to httpx. Observability for this is a Gate 2 item.
            return {}

    async def _get_from(self, source: str, url: str, params: dict) -> dict:
        """`_get`, but skipping a source that is inside its cooldown.

        Raises CatalogueUnavailable WITHOUT calling out when the breaker is
        open, so every caller's existing handling of that exception applies
        unchanged — the breaker adds no new control flow anywhere else.
        """
        if self._breaker.is_open(source):
            raise CatalogueUnavailable(f"{source} breaker open")
        try:
            body = await self._get(url, params)
        except CatalogueUnavailable:
            self._breaker.record_failure(source)
            raise
        self._breaker.record_success(source)
        return body

    async def resolve(
        self,
        mbid: str,
        artist_name: str,
        deezer_artist_id: str = "",
        index: int = 0,
    ) -> Resolution:
        """Resolve a playable clip, re-signing the URL on every request (C2).

        A cached candidate list costs one lookup plus one re-sign. A cold artist
        costs one search, whose response already carries a signed URL for every
        row — so the common paths are one round trip each, as before LUX-3.

        `index` selects among the artist's candidates and WRAPS: the frontend
        holds it and can hold a stale one, and wrapping keeps "next" correct
        rather than handing the user an error they cannot act on.
        """
        # A cache failure must never reach the caller. The endpoint's contract
        # is a clip or silence, never a 500 (see this module's docstring), and
        # in production the cache is DynamoDB, which can throttle (DEP-12).
        try:
            identities = await self._cache.get(mbid)
        except Exception:
            identities = None

        if identities:
            chosen = identities[index % len(identities)]
            try:
                url = await self._preview_url(chosen)
            except CatalogueUnavailable:
                # Throttled, not missing. Falling through to _search would ask
                # the SAME service twice more for the same artist and harden
                # the block (G3-A4). The card is silent for this request; the
                # identities stay cached, so once we are let back in the next
                # request costs one call again.
                return Resolution(None, len(identities))
            if url:
                return Resolution(
                    Clip(url, chosen.title, chosen.cover_url, chosen.source),
                    len(identities),
                )
            # That track has left the catalogue. Identity is stable, not
            # permanent, so fall through and find the artist fresh ones.

        found = await self._search(artist_name, deezer_artist_id)
        if not found:
            return Resolution(None, 0)
        identities = [identity for identity, _ in found]
        # A write failure happens AFTER a successful lookup, so the clip is
        # already in hand. Losing it to a cache error would discard work we
        # have done and silence a card that plays perfectly well (DEP-26).
        try:
            await self._cache.put(mbid, identities)
        except Exception:
            pass
        chosen, url = found[index % len(found)]
        return Resolution(
            Clip(url, chosen.title, chosen.cover_url, chosen.source), len(found)
        )

    async def _preview_url(self, identity: TrackIdentity) -> str | None:
        """Re-sign a known track. Returns None if it is no longer available."""
        if identity.source == "deezer":
            body = await self._get_from(
                "deezer", f"{self._cfg.deezer_track_url}/{identity.track_id}", {}
            )
            return body.get("preview") or None
        body = await self._get_from(
            "itunes", self._cfg.itunes_lookup_url, {"id": identity.track_id}
        )
        for row in body.get("results", []):
            if row.get("previewUrl"):
                return row["previewUrl"]
        return None

    async def _search(
        self, artist_name: str, deezer_artist_id: str = ""
    ) -> list[tuple[TrackIdentity, str]]:
        """Try each catalogue once, skipping any that is refusing us.

        Falling through to a DIFFERENT service is not amplification — it is the
        fallback doing its job. Only repeat calls to the service already saying
        no are the defect (G3-A4).

        Identity before name. When MusicBrainz records a Deezer artist id we ask
        that artist directly, which involves no name matching and so cannot
        return a different artist of the same name (`BYP-13`). Everything after
        it is the pre-existing name path, unchanged — an artist with no id, or
        one whose id yields nothing playable, gets exactly the old behaviour.
        """
        deezer_refused = False
        if deezer_artist_id:
            try:
                found = await self._from_deezer_artist(deezer_artist_id)
                if found:
                    return found
            except CatalogueUnavailable:
                # Deezer is refusing us. Searching it by name now would be the
                # same service, twice, for the same artist — G3-A4's defect
                # rather than its fallback. Skip to iTunes.
                deezer_refused = True

        if not deezer_refused:
            try:
                found = await self._from_deezer(artist_name)
            except CatalogueUnavailable:
                found = []
            if found:
                return found
        try:
            return await self._from_itunes(artist_name)
        except CatalogueUnavailable:
            return []

    async def _from_deezer_artist(
        self, deezer_artist_id: str
    ) -> list[tuple[TrackIdentity, str]]:
        """Top tracks for a SPECIFIC Deezer artist. No name matching anywhere.

        `same_artist` is deliberately not called: the id already names the
        artist, and there is nothing to compare a name against that would not
        re-introduce the defect this exists to remove (BYP-13).

        Every playable row is kept (LUX-3), in the order Deezer returned them,
        which for /top is popularity-ranked — so candidate 2 is genuinely the
        second-best-known track.
        """
        body = await self._get_from(
            "deezer",
            f"{self._cfg.deezer_artist_url}/{deezer_artist_id}/top",
            {"limit": self._cfg.clip_search_limit},
        )
        found: list[tuple[TrackIdentity, str]] = []
        for row in body.get("data", []):
            preview, track_id = row.get("preview"), row.get("id")
            if preview and track_id:
                found.append(
                    (
                        TrackIdentity(
                            source="deezer",
                            track_id=str(track_id),
                            title=str(row.get("title") or ""),
                            cover_url=_album_cover(row),
                        ),
                        preview,
                    )
                )
        return found

    async def _from_deezer(self, artist_name: str) -> list[tuple[TrackIdentity, str]]:
        body = await self._get_from(
            "deezer",
            self._cfg.deezer_search_url,
            {"q": artist_name, "limit": self._cfg.clip_search_limit},
        )
        found: list[tuple[TrackIdentity, str]] = []
        for row in body.get("data", []):
            preview, track_id = row.get("preview"), row.get("id")
            artist = row.get("artist") or {}
            if preview and track_id and same_artist(artist.get("name"), artist_name):
                found.append(
                    (
                        TrackIdentity(
                            source="deezer",
                            track_id=str(track_id),
                            # `or ""` not a .get default: these keys can be
                            # present with a JSON null, and TrackOut's fields
                            # are typed str, so None here becomes a 500 at the
                            # endpoint.
                            title=str(row.get("title") or ""),
                            cover_url=_album_cover(row),
                        ),
                        preview,
                    )
                )
        return found

    async def _from_itunes(self, artist_name: str) -> list[tuple[TrackIdentity, str]]:
        body = await self._get_from(
            "itunes",
            self._cfg.itunes_search_url,
            {
                "term": artist_name,
                "entity": "song",
                "limit": self._cfg.clip_search_limit,
            },
        )
        found: list[tuple[TrackIdentity, str]] = []
        for row in body.get("results", []):
            preview, track_id = row.get("previewUrl"), row.get("trackId")
            if preview and track_id and same_artist(row.get("artistName"), artist_name):
                found.append(
                    (
                        TrackIdentity(
                            source="itunes",
                            track_id=str(track_id),
                            title=str(row.get("trackName") or ""),
                            cover_url=str(row.get("artworkUrl100") or ""),
                        ),
                        preview,
                    )
                )
        return found
