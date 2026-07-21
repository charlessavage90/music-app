"""ListenBrainz Labs similar-artists source.

CC0 licensed, MusicBrainz-keyed, published by MetaBrainz in response to
Spotify's November 2024 API deprecations (spec section 1).

Field names below are confirmed against a response recorded from the live
endpoint in Task 1. This module is the only place that knows the upstream
schema.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

from artistpath_builder.config import BuilderConfig
from artistpath_builder.models import EdgeType, SimilarArtist

FIELD_MBID = "artist_mbid"
FIELD_NAME = "name"
FIELD_SCORE = "score"
FIELD_COMMENT = "comment"


def harvest_identities(payloads) -> dict[str, tuple[str, str]]:
    """Collect (name, disambiguation) per MBID from neighbour rows.

    There is no per-artist metadata record: an artist's name and
    disambiguation appear only where it is listed as somebody else's
    neighbour. Harvesting across every response is therefore the only way to
    populate the artist table, and it supplies disambiguation
    ("1980s-1990s US grunge band") at no extra cost.
    """
    identities: dict[str, tuple[str, str]] = {}
    for payload in payloads:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            continue
        for row in ListenBrainzSource._rows(data):
            mbid = row.get(FIELD_MBID)
            if not mbid:
                continue
            name = row.get(FIELD_NAME) or ""
            comment = row.get(FIELD_COMMENT) or ""
            existing = identities.get(mbid)
            # Prefer the first non-empty name seen; deterministic because
            # callers pass payloads in sorted order.
            if existing is None or (not existing[0] and name):
                identities[mbid] = (name, comment)
    return identities


class ListenBrainzSource:
    name = "listenbrainz"
    edge_type = EdgeType.BEHAVIOURAL

    def __init__(self, config: BuilderConfig) -> None:
        self._config = config

    def request_url(self, mbid: str) -> str:
        query = urlencode({"artist_mbids": mbid, "algorithm": self._config.algorithm})
        return f"{self._config.similar_artists_url}?{query}"

    def parse(
        self, payload: bytes, exclude_mbid: str | None = None
    ) -> list[SimilarArtist]:
        """Neighbours with RAW co-occurrence scores, uncapped.

        Deliberately does NOT normalise per-artist. Dividing by the artist's own
        strongest neighbour made every artist's top edge score 1.0 regardless of
        whether its raw count was 11 or 11,147 — a 1013x spread — which made
        edge strengths incommensurable across artists and led the router to
        prefer meaningless hops between obscure artists (findings
        2026-07-21 §3). Global, popularity-corrected normalisation and the
        neighbour cap now happen in the pipeline, where the whole graph is
        visible.
        """
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed similarity payload: {exc}") from exc

        neighbours: list[SimilarArtist] = []
        for row in self._rows(data):
            mbid = row.get(FIELD_MBID)
            if not mbid or mbid == exclude_mbid:
                continue
            score = row.get(FIELD_SCORE)
            if score is None:
                continue
            neighbours.append(
                SimilarArtist(
                    mbid=mbid, name=row.get(FIELD_NAME) or "", score=float(score)
                )
            )

        # Deterministic order: strongest first, MBID breaks ties.
        neighbours.sort(key=lambda n: (-n.score, n.mbid))
        return neighbours

    @staticmethod
    def _rows(data: object) -> list[dict]:
        """The endpoint has returned both a bare array and a wrapped object
        across versions. Accept either rather than breaking on a reshuffle."""
        if isinstance(data, list):
            if data and isinstance(data[0], list):  # [[...]] nesting
                return [row for row in data[0] if isinstance(row, dict)]
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            for key in ("similar_artists", "data", "results"):
                value = data.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
        return []
