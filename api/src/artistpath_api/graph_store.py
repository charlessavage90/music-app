"""Reads the APG1 graph artifact into memory.

Self-contained: it parses the binary format directly and depends on nothing
in the builder package. The format is the contract (spec section 3).
"""

from __future__ import annotations

import json
import struct
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_MAGIC = b"APG1"
_FORMAT_VERSION = 1
_HEADER = struct.Struct("<4sIIIQ")


@dataclass(slots=True)
class GraphStore:
    mbids: list[str]
    names: list[str]
    disambiguations: list[str]
    # Popularity as stored: log-scaled score-weighted in-degree in 0-1. NOT a
    # percentile — the gap between the two is large at the top of the
    # distribution (Phase 1 log §2.12), which is why the basis is in the name.
    pop_raw: np.ndarray  # float32, 0-1
    offsets: np.ndarray     # int32, length N+1
    neighbours: np.ndarray  # int32, length E
    scores: np.ndarray      # float32, length E
    id_by_mbid: dict[str, int] = field(default_factory=dict)
    # Derived from DEGREE, not from popularity and not from fame (log §2.6).
    degree_hub_penalty: np.ndarray | None = None  # float32 0-1, computed if not given

    def __post_init__(self) -> None:
        if not self.id_by_mbid:
            self.id_by_mbid = {mbid: i for i, mbid in enumerate(self.mbids)}
        if self.degree_hub_penalty is None:
            self.degree_hub_penalty = self._compute_degree_hub_penalty()

    # Read-only aliases under the pre-2026-07-23 names. The frozen probe
    # scripts in builder/analysis/ import this class and read these attributes;
    # they are deliberate records of what was executed and are not updated, so
    # the old names must keep resolving. New code uses the explicit names —
    # these are properties, so nothing can be written through them.
    # Mapping table: builder/analysis/README.md.
    @property
    def popularity(self) -> np.ndarray:
        return self.pop_raw

    @property
    def hub_penalty(self) -> np.ndarray | None:
        return self.degree_hub_penalty

    def _compute_degree_hub_penalty(self) -> np.ndarray:
        """Per-node hub-ness in 0-1, for the cost function's anti-hub term.

        Log-scaled DEGREE, zeroed at or below the median and rising to 1.0 at
        the biggest hub — so typical/obscure artists carry no penalty and only
        the high-degree crossroads are made expensive to route through.

        Degree, not fame: log §2.6 records that the top-1%-by-degree set is
        largely insular micro-genre artists, so a high penalty here means
        "non-insular-cluster-member", NOT "famous".
        """
        degrees = np.diff(self.offsets).astype(np.float64)
        log_deg = np.log1p(degrees)
        median_log = float(np.median(log_deg))
        span = float(log_deg.max()) - median_log
        if span <= 0:
            return np.zeros(len(degrees), dtype=np.float32)
        return np.clip((log_deg - median_log) / span, 0.0, 1.0).astype(np.float32)

    @property
    def artist_count(self) -> int:
        return len(self.mbids)

    def neighbours_of(self, node_id: int) -> Iterator[tuple[int, float]]:
        start, end = int(self.offsets[node_id]), int(self.offsets[node_id + 1])
        for k in range(start, end):
            yield int(self.neighbours[k]), self.scores[k]

    @classmethod
    def load(cls, path: str | Path) -> "GraphStore":
        payload = Path(path).read_bytes()
        if len(payload) < _HEADER.size:
            raise ValueError("artifact truncated: shorter than header")
        magic, version, n, e, meta_len = _HEADER.unpack_from(payload)
        if magic != _MAGIC:
            raise ValueError(f"bad magic: expected {_MAGIC!r}, got {magic!r}")
        if version != _FORMAT_VERSION:
            raise ValueError(f"unsupported artifact version {version}")

        cursor = _HEADER.size

        def take(count: int, dtype: str, size: int) -> np.ndarray:
            nonlocal cursor
            end_ = cursor + count * size
            arr = np.frombuffer(payload[cursor:end_], dtype=dtype)
            cursor = end_
            return arr

        offsets = take(n + 1, "<i4", 4)
        neighbours = take(e, "<i4", 4)
        scores = take(e, "<f4", 4)
        take(e, "<u1", 1)  # edge_types — unused in alpha (all behavioural)
        meta = json.loads(payload[cursor : cursor + meta_len])

        return cls(
            mbids=meta["mbids"],
            names=meta["names"],
            disambiguations=meta["disambiguations"],
            # "popularity" is the APG1 wire key and cannot be renamed without
            # invalidating every existing artifact — the format is the
            # builder/api contract. Only the in-memory name carries the basis.
            pop_raw=np.asarray(meta["popularity"], dtype=np.float32),
            offsets=offsets,
            neighbours=neighbours,
            scores=scores,
        )
