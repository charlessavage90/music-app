"""Fame: ListenBrainz listener counts, fetched into the archive.

`fame_lb_raw` is an artist's ListenBrainz `total_user_count` — how many
distinct people have listened to them. It is the adopted proxy for the
novelty-likelihood construct (`FAM-`; the construct itself is owned by
`PRODUCT-REQUIREMENTS.md`'s Definitions). It is NOT `pop_raw`, which is
score-weighted in-degree computed from the archive, and the two must never be
read as each other — log §2.11/§2.12 record what that conflation has cost.

WHY THIS IS A SEPARATE STAGE, and it is the load-bearing design decision here.
`build` may not touch the network (spec §9; the replay test injects a fetcher
that raises to prove it), because byte-identical output for identical input is
required and a network call is not an input. So this stage fetches into the
ARCHIVE, exactly as `crawl` does for similarity responses, and `build` reads
records off the archive offline. The pipeline gains a network-sourced quantity
without gaining a network call.

NULLS ARE RESULTS. ListenBrainz returns not-found artists with counts set to
null rather than omitting them, so a null is a measured absence — nobody has
listened — which under the novelty-likelihood construct is genuine maximal
obscurity, never a missing measurement (`FAM-` §1, `FAM-AM1`.8). Two
consequences are load-bearing: a null occupies its archive key like any other
result, so resume does not re-fetch it forever; and no floor value is ever
substituted for one.

Run (from `builder/`):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \\
        -m artistpath_builder.cli fame --archive-dir ./archive
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Iterable

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import TransientFetchError

logger = logging.getLogger(__name__)

# The instrument, exactly as adopted by FAM-. Named here rather than in
# BuilderConfig because changing it changes what the quantity MEANS, which is
# a new instrument and a new pre-registration, not a tunable.
ENDPOINT = "https://api.listenbrainz.org/1/popularity/artist"

# MAX_ITEMS_PER_GET in listenbrainz/webserver/views/api_tools.py: a batch above
# this is silently TRUNCATED, not rejected (read from master 2026-07-30). The
# truncation is why absent-from-response is recorded as null rather than left
# as a hole — a silently short response must not read as "never asked".
MAX_PER_REQUEST = 1000

# mbid -> total_user_count, or None where the server reported no listeners.
FameFetcher = Callable[[list[str]], dict[str, "int | None"]]


class MissingFameError(RuntimeError):
    """A build wanted fame for artists the fetch stage never covered.

    This is the `ULC-F1` failure shape applied to fame: a lookup that quietly
    succeeds over a smaller population than the one being built leaves new
    artists unevaluated, and here it would leave them unpriced in a cost
    function that routes on the price. Refusing to build is the whole point —
    see the `ULF-` filter rule for the same decision taken about drop lists.
    """


@dataclass(frozen=True)
class FameFetchReport:
    fetched: int
    skipped: int
    nulls: int

    @property
    def total(self) -> int:
        return self.fetched + self.skipped


@dataclass(frozen=True)
class FameSeedReport:
    seeded: int
    skipped: int


def fame_key(mbid: str) -> str:
    """Archive key for one artist's fame record.

    Its own prefix, so `keys()` consumers that walk `similar/` are unaffected
    and a fame record can never be mistaken for a similarity response.
    """
    return f"fame/{mbid}.json"


def _write(archive: RawArchive, mbid: str, value: int | None, fetched: str) -> None:
    archive.put(
        fame_key(mbid),
        json.dumps({"fame_lb_raw": value, "fetched": fetched}).encode(),
    )


def fetch_fame(
    archive: RawArchive,
    mbids: Iterable[str],
    fetcher: FameFetcher,
    *,
    batch_size: int = MAX_PER_REQUEST,
    today: str | None = None,
    pause_seconds: float = 0.0,
) -> FameFetchReport:
    """Fetch listener counts for `mbids` into `archive`, resuming past records.

    Resume is by key presence, which is the same mechanism the crawl uses and
    has the same property: interrupting and re-running costs only what was not
    already done. Requests go out in sorted order so a partial run is a
    prefix of a complete one rather than an arbitrary subset.

    `fetcher` is injected so tests never touch the network — the pattern
    `Crawler` uses, and the reason the offline guarantee is testable at all.
    """
    fetched_on = today or date.today().isoformat()
    ordered = sorted(set(mbids))
    pending = [m for m in ordered if not archive.has(fame_key(m))]
    skipped = len(ordered) - len(pending)
    logger.info(
        "fame: %d artists, %d already recorded, %d to fetch",
        len(ordered),
        skipped,
        len(pending),
    )

    fetched = 0
    nulls = 0
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        values = fetcher(batch)
        for mbid in batch:
            # .get() rather than [] deliberately: an mbid absent from the
            # response is recorded as a measured null, so a silently truncated
            # batch cannot leave a hole that the next run reads as unasked.
            value = values.get(mbid)
            _write(archive, mbid, value, fetched_on)
            fetched += 1
            if value is None:
                nulls += 1
        logger.info("fame: %d/%d fetched", fetched, len(pending))
        if pause_seconds and start + batch_size < len(pending):
            time.sleep(pause_seconds)

    return FameFetchReport(fetched=fetched, skipped=skipped, nulls=nulls)


def seed_fame(
    archive: RawArchive,
    snapshot_path: Path,
    *,
    expected_sha256: str,
    fetched: str,
) -> FameSeedReport:
    """Import an already-fetched snapshot as archive records.

    The snapshot IS the instrument's identity — the adopted object is the
    dated file plus its sha256 (`FAM-AM1`.7) — so it is verified BEFORE
    anything is written. Importing an unverified file would put values of
    unknown provenance into an artifact that routes on them.

    Existing records win: a seed is older data by construction, and silently
    overwriting a fresher fetch would make the archive's contents depend on
    the order the operator happened to run things in.
    """
    payload = snapshot_path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256:
        raise ValueError(
            f"{snapshot_path.name} sha256 mismatch: {actual} != {expected_sha256}. "
            "Refusing to seed: the snapshot's sha IS the instrument's identity "
            "(FAM-AM1.7), so an unverified file has unknown provenance."
        )

    snapshot: dict[str, int | None] = json.loads(payload)
    seeded = 0
    skipped = 0
    for mbid in sorted(snapshot):
        if archive.has(fame_key(mbid)):
            skipped += 1
            continue
        _write(archive, mbid, snapshot[mbid], fetched)
        seeded += 1
    logger.info("fame seed: %d imported, %d already present", seeded, skipped)
    return FameSeedReport(seeded=seeded, skipped=skipped)


def load_fame(archive: RawArchive, mbids: Iterable[str]) -> dict[str, int | None]:
    """Read fame records for `mbids`, or refuse if any is uncovered.

    OFFLINE by construction: this is what `build` calls, and it only ever
    reads. Missing records raise rather than defaulting, because a default
    would be a fabricated listener count silently steering real journeys.
    """
    values: dict[str, int | None] = {}
    missing: list[str] = []
    for mbid in mbids:
        raw = archive.get(fame_key(mbid))
        if raw is None:
            missing.append(mbid)
            continue
        values[mbid] = json.loads(raw)["fame_lb_raw"]

    if missing:
        shown = ", ".join(sorted(missing)[:10])
        more = "" if len(missing) <= 10 else f" (and {len(missing) - 10} more)"
        raise MissingFameError(
            f"{len(missing)} artists in this build have no fame record: "
            f"{shown}{more}. The fetch population and the build population "
            "have diverged — run the `fame` stage against this archive. "
            "Refusing to build rather than pricing them by default."
        )
    return values


def lb_fame_fetcher(config: BuilderConfig) -> FameFetcher:
    """The real network fetcher. Kept out of `fetch_fame` so tests inject a fake.

    Retries on the same transient classes the crawler treats as transient
    (429 and 5xx), with the same exponential backoff, because this hits the
    same host under the same rate limit.
    """
    import httpx

    logging.getLogger("httpx").setLevel(logging.WARNING)

    client = httpx.Client(
        headers={
            "User-Agent": config.user_agent,
            "Content-Type": "application/json",
        },
        timeout=config.timeout_seconds,
        follow_redirects=True,
    )

    def _post(batch: list[str]) -> dict[str, int | None]:
        body = json.dumps({"artist_mbids": batch}).encode()
        try:
            response = client.post(ENDPOINT, content=body)
        except httpx.RequestError as exc:
            raise TransientFetchError(str(exc)) from exc
        if response.status_code == 429 or response.status_code >= 500:
            raise TransientFetchError(f"HTTP {response.status_code}")
        response.raise_for_status()
        return {
            row["artist_mbid"]: row.get("total_user_count")
            for row in response.json()
        }

    def fetch(batch: list[str]) -> dict[str, int | None]:
        for attempt in range(config.max_retries):
            try:
                return _post(batch)
            except TransientFetchError as exc:
                backoff = config.request_delay_seconds * (2**attempt)
                logger.warning(
                    "fame batch failed (%s); retrying in %.1fs", exc, backoff
                )
                time.sleep(backoff)
            time.sleep(config.request_delay_seconds)
        raise TransientFetchError(
            f"giving up on a batch of {len(batch)} after {config.max_retries} "
            "attempts"
        )

    return fetch
