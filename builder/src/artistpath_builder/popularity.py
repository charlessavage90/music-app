"""Artist popularity derived from the ListenBrainz spark dump.

Why a 191GB dump rather than an API call: the per-artist listeners endpoint
costs ~22.8s per artist (findings section 6a), which makes 75,000 artists a
three-week job. Aggregating the dump once is both faster overall and moves
popularity to Tier-1 data we own outright (spec section 1).

Popularity is **distinct listeners**, not plays (spec section 4.1).

The dump is a set of tar archives containing monthly newline-delimited JSON
listens. Each listen names an artist and a user; the aggregate we need is
COUNT(DISTINCT user) per artist MBID.

This module deliberately holds no AWS or download logic. It aggregates a
stream of listen records and nothing else, so it is testable without the
dump present.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable, Iterator
from pathlib import Path

logger = logging.getLogger(__name__)

Popularity = dict[str, int]

# A listen names artists via a mapped MBID list; unmapped listens carry none.
_MAPPING_KEYS = ("artist_mbids", "artist_credit_mbids")


def iter_listen_artists(lines: Iterable[bytes | str]) -> Iterator[tuple[str, str]]:
    """Yield (artist_mbid, user) for every artist named on every listen.

    A listen may credit several artists; each gets the listener. Malformed or
    unmapped lines are skipped rather than raised — a 191GB dump will contain
    some, and aborting the whole aggregation over one bad row is worse than
    losing it.
    """
    for line in lines:
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue

        user = record.get("user_name") or record.get("user_id")
        if not user:
            continue

        metadata = record.get("track_metadata") or {}
        mapping = metadata.get("mbid_mapping") or {}
        additional = metadata.get("additional_info") or {}

        mbids: list[str] = []
        for container in (mapping, additional, record):
            for key in _MAPPING_KEYS:
                value = container.get(key)
                if isinstance(value, list):
                    mbids.extend(m for m in value if isinstance(m, str))

        for mbid in dict.fromkeys(mbids):  # de-duplicate within one listen
            yield mbid, str(user)


def aggregate_listeners(pairs: Iterable[tuple[str, str]]) -> Popularity:
    """Count distinct listeners per artist.

    Holds a set of users per artist. At ListenBrainz's scale this is tens of
    millions of small strings; if that proves too large for one machine, the
    replacement is a disk-backed group-by (DuckDB) over the same pairs, not a
    change to this signature.
    """
    seen: dict[str, set[str]] = {}
    for mbid, user in pairs:
        seen.setdefault(mbid, set()).add(user)
    return {mbid: len(users) for mbid, users in seen.items()}


def write_popularity(popularity: Popularity, path: Path) -> None:
    """Persist the derived table. Deterministic key order for reproducibility."""
    Path(path).write_text(
        json.dumps(popularity, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


def read_popularity(path: Path) -> Popularity:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {mbid: int(count) for mbid, count in data.items()}
