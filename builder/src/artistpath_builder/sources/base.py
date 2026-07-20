"""The seam that isolates upstream schema changes (spec section 8.1)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from artistpath_builder.models import EdgeType, SimilarArtist


@runtime_checkable
class SimilaritySource(Protocol):
    name: str
    edge_type: EdgeType

    def request_url(self, mbid: str) -> str:
        """The URL to fetch this artist's neighbours from."""
        ...

    def parse(
        self, payload: bytes, exclude_mbid: str | None = None
    ) -> list[SimilarArtist]:
        """Turn a raw response body into neighbours, scores normalised to 0-1."""
        ...
