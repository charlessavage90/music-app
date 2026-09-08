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
    # MusicBrainz-recorded Deezer artist ids, indexed by node id, "" where none
    # is known. Lets a clip be resolved by artist identity rather than by name,
    # so a card cannot play a different artist of the SAME NAME (`BYP-13`).
    # Empty for every artifact built before 2026-08-02 — including the one the
    # app serves — and for stores built in tests. Read it through
    # `deezer_id_of`, never by indexing, since it may be shorter than N.
    deezer_ids: list[str] = field(default_factory=list)
    # LUX-4. Streaming ids and structured MusicBrainz facts, indexed by node
    # id. Additive keys, absent from every artifact built before 2026-09-05 —
    # including the one the app serves — so read them through the accessors
    # below, never by indexing.
    #
    # DISPLAY-ONLY, and that is the whole reason they carry no length check
    # while fame_lb does: nothing here is indexed inside the cost function, so
    # a short list cannot misprice an artist. It can only fail to show a link.
    # Ids are platform id TAILS, not URLs (`L4-D2`) — the frontend composes.
    spotify_ids: list[str] = field(default_factory=list)
    apple_ids: list[str] = field(default_factory=list)
    artist_facts: list[dict] = field(default_factory=list)
    # Where each artist's ListenBrainz listener count ranks within THIS
    # artifact's own population, 0-1. `None` when the artifact carries no fame
    # data — every artifact built before 2026-08-05, including the one the app
    # served until this adoption.
    #
    # Currency, and all three of these are different quantities: this is FAME
    # (an external listener count), `pop_raw` is score-weighted in-degree
    # computed from the similarity archive, and `degree_hub_penalty` is
    # topological degree. Log §2.6/§2.11/§2.12 record a wrong conclusion caused
    # by each conflation. `pctl` in the name because it is a RANK, never a
    # value — the raw counts are not kept, since nothing routes on them.
    fame_lb_pctl: np.ndarray | None = None  # float64 0-1, computed if not given
    # Derived from DEGREE, not from popularity and not from fame (log §2.6).
    degree_hub_penalty: np.ndarray | None = None  # float32 0-1, computed if not given
    # sha256 of the bytes this store was parsed from, when known. Empty for a
    # store built in a test. Reported by /health so "which graph is live" is
    # answerable over HTTP — eighteen artifacts sit in builder/scratch/ and are
    # not interchangeable.
    source_sha256: str = ""

    def deezer_id_of(self, node: int) -> str:
        """The artist's Deezer id, or "" when none is known.

        Bounds-checked rather than indexed: the list is absent on every
        pre-2026-08-02 artifact and could in principle be short. Returning a
        neighbour's id for an out-of-range node would hand one artist's card
        another artist's clip — the very defect this exists to remove.
        """
        if node < len(self.deezer_ids):
            return self.deezer_ids[node]
        return ""

    # LUX-4's three accessors. Bounds-checked for the same reason as
    # `deezer_id_of` — out of range must read as absent, never as the next
    # artist's row — but they return None where that one returns "".
    #
    # The divergence is deliberate and it is the wire's, not a style choice:
    # `deezer_id_of`'s "" is consumed inside the api by the clip resolver,
    # where "" already means "fall back to name search". These three go
    # STRAIGHT ONTO THE WIRE as `spotify_id` / `apple_id` / `facts`, where the
    # contract is null-means-render-a-search-link (`L4-D2`). Normalising the
    # builder's in-band "" here keeps the frontend on one code path instead of
    # having to treat "" and null alike.

    def spotify_id_of(self, node: int) -> str | None:
        if node < len(self.spotify_ids):
            return self.spotify_ids[node] or None
        return None

    def apple_id_of(self, node: int) -> str | None:
        if node < len(self.apple_ids):
            return self.apple_ids[node] or None
        return None

    def facts_of(self, node: int) -> dict:
        """Structured MusicBrainz facts, or {} when there are none.

        {} rather than None so a caller can `.get()` without a null check: an
        artist the extraction pass reached but found nothing for must be
        indistinguishable from one it never covered, since both render as
        nothing at all (`L4-D3`).
        """
        if node < len(self.artist_facts):
            return self.artist_facts[node] or {}
        return {}

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

    @staticmethod
    def fame_percentiles(fame_lb_raw: list[int | None]) -> np.ndarray:
        """Rank listener counts within their own population, 0-1.

        THE FRAME IS THIS ARTIFACT'S OWN non-null values, which is a deliberate
        departure from the `CRE-` harness. That harness framed against the
        previously adopted artifact — a fixed experimental ruler, which is the
        right choice for comparing arms built from different data. A SHIPPED
        ruler pinned to a retired artifact would go stale at the next adoption
        and price today's artists against a population that no longer exists.

        Nulls are measured absences: the instrument asked and ListenBrainz
        reported no listeners. Under the novelty-likelihood construct that is
        genuine maximal obscurity, so they take 0.0 — but they are EXCLUDED
        from the frame, because counting them would drag every measured
        artist's rank upward and make a poorly-covered population look
        uniformly famous.

        Ties take equal ranks: two artists with the same listener count are
        equally obscure, and breaking that tie would invent a distinction the
        instrument did not measure.

        Plain sentence for the whole method: 0 means nobody on this map has
        fewer recorded listeners, 1 means nobody has more.
        """
        values = np.array(
            [np.nan if v is None else float(v) for v in fame_lb_raw],
            dtype=np.float64,
        )
        measured = values[~np.isnan(values)]
        out = np.zeros(len(values), dtype=np.float64)
        if measured.size == 0:
            # Nothing was measured anywhere: every artist is equally, maximally
            # obscure. A real reading, not a failure.
            return out

        frame = np.sort(measured)
        # `side="left"` counts strictly-smaller values, so equal counts share a
        # rank. Divided by size-1 so the least-listened-to measured artist sits
        # at 0.0 and the most-listened-to at 1.0; guarded because a
        # single-measured-artist population would otherwise divide by zero.
        denominator = max(1, frame.size - 1)
        ranks = np.searchsorted(frame, values, side="left") / denominator
        # NaN sorts above everything in searchsorted, so nulls must be written
        # back explicitly rather than left with whatever rank that produced.
        ranks[np.isnan(values)] = 0.0
        return np.clip(ranks, 0.0, 1.0)

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
        return cls.from_bytes(Path(path).read_bytes())

    @classmethod
    def from_bytes(cls, payload: bytes) -> "GraphStore":
        """Parse an APG1 payload.

        The magic, version and truncation checks exist in the builder's parser
        (builder/…/artifact.py `deserialise`) and were missing here: the two
        APG1 parsers had drifted, undetected, in the half that is about to
        start fetching over a network — the team review's TR-4.

        Two of the checks below are in NEITHER parser and are new to this one:
        the over-long case, and the header-N vs metadata-length disagreement
        (TR-3). `deserialise` still lacks both, so a mismatched artifact loads
        clean on the builder side today. That is recorded rather than fixed
        here — this reader is what serves users.
        """
        if len(payload) < _HEADER.size:
            raise ValueError("artifact truncated: shorter than header")
        magic, version, n, e, meta_len = _HEADER.unpack_from(payload)
        if magic != _MAGIC:
            raise ValueError(f"bad magic: expected {_MAGIC!r}, got {magic!r}")
        if version != _FORMAT_VERSION:
            raise ValueError(f"unsupported artifact version {version}")

        # Sections are fixed-width and the metadata blob is last, so the total
        # length is fully determined by the header. A short read is truncation;
        # a long one means the file is not what the header describes.
        expected = _HEADER.size + (n + 1) * 4 + e * 4 + e * 4 + e * 1 + meta_len
        if len(payload) < expected:
            raise ValueError(
                f"artifact truncated: header describes {expected} bytes, got {len(payload)}"
            )
        if len(payload) > expected:
            raise ValueError(
                f"artifact length mismatch: header describes {expected} bytes, "
                f"got {len(payload)}"
            )

        cursor = _HEADER.size

        def take(count: int, dtype: str, size: int) -> np.ndarray:
            nonlocal cursor
            end_ = cursor + count * size
            # count= is defence in depth, NOT the guard that fires: the total
            # length check above already proves every slice is exactly right,
            # so no payload reaching here can be short. Kept because without it
            # a short buffer yields a SHORTER array rather than an error, and
            # that is the failure this would degrade to if the check above were
            # ever relaxed. Verified unreachable by mutation (closeout B3).
            arr = np.frombuffer(payload[cursor:end_], dtype=dtype, count=count)
            cursor = end_
            return arr

        offsets = take(n + 1, "<i4", 4)
        neighbours = take(e, "<i4", 4)
        scores = take(e, "<f4", 4)
        take(e, "<u1", 1)  # edge_types — unused in alpha (all behavioural)
        meta = json.loads(payload[cursor : cursor + meta_len])

        # The header's N and the metadata's length are two independent
        # statements of the same fact. When they disagree the artifact loads
        # clean and leaves pop_raw and degree_hub_penalty at different lengths,
        # both indexed by node id in the cost function (TR-3).
        if len(meta["mbids"]) != n:
            raise ValueError(
                f"artifact inconsistent: header says {n} nodes, "
                f"metadata has {len(meta['mbids'])}"
            )

        # Same class of defect as the check above, for the same reason: this
        # list is indexed by node id inside the Dijkstra loop, so a length
        # disagreement is an out-of-bounds read or a silently mispriced artist
        # rather than a clean failure. Empty is not a disagreement — the
        # builder omits the key when it has nothing to say, and an empty list
        # from an older writer means the same thing.
        fame_lb = meta.get("fame_lb")
        if fame_lb and len(fame_lb) != n:
            raise ValueError(
                f"artifact inconsistent: header says {n} nodes, but fame_lb "
                f"has {len(fame_lb)} entries"
            )

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
            # .get, not [...]: the key is additive and FORMAT_VERSION is not
            # bumped, so every artifact built before 2026-08-02 lacks it —
            # including the one the app serves. Absence means "resolve by
            # name", which is what the app did before this existed.
            deezer_ids=meta.get("deezer_ids", []),
            # LUX-4. Same additive-key reasoning as deezer_ids, and the same
            # exemption from fame_lb's length assertion below: these are
            # display fields read through bounds-checked accessors, never
            # indexed in the cost function.
            spotify_ids=meta.get("spotify_ids", []),
            apple_ids=meta.get("apple_ids", []),
            artist_facts=meta.get("artist_facts", []),
            # Same additive-key reasoning as deezer_ids. Length is checked
            # because this one is INDEXED BY NODE ID in the cost function: a
            # short list would price one artist as another, or read out of
            # bounds mid-request. deezer_ids escapes that check only because it
            # is read through a bounds-checked accessor.
            fame_lb_pctl=cls.fame_percentiles(fame_lb) if fame_lb else None,
        )
