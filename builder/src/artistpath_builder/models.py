"""Plain data carried between builder stages. No I/O, no behaviour."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EdgeType(IntEnum):
    """Serialised as uint8 per edge.

    Alpha emits only BEHAVIOURAL. The type exists so a second source can be
    added without changing the artifact format (spec section 3.1).
    """

    BEHAVIOURAL = 0
    STRUCTURAL = 1  # reserved: MusicBrainz/Discogs. Not emitted in alpha.
    DESCRIPTIVE = 2  # reserved: shared genre tags. Not emitted in alpha.


@dataclass(frozen=True, slots=True)
class SimilarArtist:
    """One neighbour of some artist, as reported by a similarity source."""

    mbid: str
    name: str
    score: float


@dataclass(frozen=True, slots=True)
class BootstrapArtist:
    """An artist from the sitewide top-1000, used only to start the snowball.

    Carries no popularity: the sitewide endpoint caps at 1000 artists, so
    popularity is fetched per-artist instead (see the Task 1 findings).
    """

    mbid: str
    name: str


@dataclass(frozen=True, slots=True)
class ArtistStats:
    """Per-artist popularity and metadata. One record per graph node."""

    mbid: str
    name: str
    # Score-weighted in-degree, scaled to an integer slot. NOT a listener
    # count: there is no separate popularity source, and this is summed from
    # similarity scores in the archive during `build` (findings 6f). It was
    # called `user_count` and documented as "distinct listeners" until
    # 2026-07-23, which is the same class of currency error as log §2.6/§2.11.
    pop_indegree_scaled: int
    listen_count: int  # plays; archived but NOT used for routing
    disambiguation: str = ""
