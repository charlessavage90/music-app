"""Resumable, rate-limited snowball crawler.

Fills the archive and nothing else. Graph assembly reads the archive, never
the network — which is what allows a rebuild to be proven offline (spec
section 9).

No ranked list of 75k artists is obtainable (Task 1 findings section 2), so
the frontier is built breadth-first from the responses themselves.
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from collections.abc import Callable
from pathlib import Path

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import PRODUCTION_ALGORITHM, BuilderConfig
from artistpath_builder.sources.base import SimilaritySource

logger = logging.getLogger(__name__)

Fetcher = Callable[[str], bytes]


class TransientFetchError(RuntimeError):
    """Retryable: rate limiting, timeouts, 5xx."""


def http_fetcher(config: BuilderConfig) -> Fetcher:
    """The real network fetcher. Kept out of Crawler so tests inject a fake.

    Logs per-request latency and any rate-limit headers the server returns.
    An 8-hour crawl that silently degrades is worse than a slow one that says
    why, so this instrumentation is permanent rather than diagnostic.
    """
    import httpx

    # httpx logs every request at INFO, which drowns our own output.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    client = httpx.Client(
        headers={"User-Agent": config.user_agent},
        timeout=config.timeout_seconds,
        follow_redirects=True,
    )

    def fetch(url: str) -> bytes:
        started = time.monotonic()
        try:
            response = client.get(url)
        except httpx.RequestError as exc:
            raise TransientFetchError(str(exc)) from exc
        elapsed = time.monotonic() - started

        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_in = response.headers.get("X-RateLimit-Reset-In")
        logger.info(
            "fetch %6.2fs http=%d remaining=%s reset_in=%s",
            elapsed,
            response.status_code,
            remaining,
            reset_in,
        )

        if response.status_code == 429 or response.status_code >= 500:
            raise TransientFetchError(f"HTTP {response.status_code}")
        response.raise_for_status()
        return response.content

    return fetch


class Crawler:
    def __init__(
        self,
        config: BuilderConfig,
        archive: RawArchive,
        source: SimilaritySource,
        fetcher: Fetcher,
        checkpoint_path: Path,
    ) -> None:
        self.config = config
        self.archive = archive
        self.source = source
        self.fetcher = fetcher
        self.checkpoint_path = Path(checkpoint_path)
        self.failures: list[str] = []
        state = self._load_checkpoint()
        self._done: set[str] = state["done"]
        self.discovered: set[str] = state["discovered"]

    def similar_key(self, mbid: str) -> str:
        # The production archive predates algorithm-scoped keys and keeps its
        # flat layout — 75,000 responses, irreplaceable, and every existing
        # script finds them there. Every OTHER algorithm gets its own
        # sub-tree, so two algorithms' responses can never be mistaken for one
        # another (RC-H3: the key did not encode the algorithm, so a re-crawl
        # aimed at the existing archive would silently return production data).
        if self.config.algorithm == PRODUCTION_ALGORITHM:
            return f"similar/{self.source.name}/{mbid}.json"
        return f"similar/{self.source.name}/{self.config.algorithm}/{mbid}.json"

    def crawl(self, bootstrap_mbids: list[str]) -> None:
        queue: deque[str] = deque()

        # Resume: the checkpoint persists the discovered/done sets but not the
        # in-memory queue, so rebuild the pending frontier from their
        # difference. This also re-queues artists that failed on a previous
        # run (they are discovered but never marked done), so a transient
        # server outage is retried on the next run rather than lost forever.
        for mbid in sorted(self.discovered - self._done):
            queue.append(mbid)

        # Seed a fresh crawl, and pick up any bootstrap artist not yet seen
        # (e.g. added to the bootstrap list between runs).
        for mbid in bootstrap_mbids:
            if mbid not in self.discovered:
                self.discovered.add(mbid)
                queue.append(mbid)

        processed = 0
        # CEX-2: the bound is on artists FETCHED, not artists discovered.
        # Bounding discovery meant the frontier past the target was never
        # recorded (ULC-F3), so a later resume had nothing to resume from.
        while queue and len(self._done) < self.config.target_artist_count:
            mbid = queue.popleft()
            if mbid in self._done:
                continue

            payload = self._archive_or_fetch(
                self.similar_key(mbid), self.source.request_url(mbid), mbid
            )
            # Only a successful fetch counts as done. A failed artist stays
            # out of `done`, so `discovered - done` re-queues it next run.
            if payload is None:
                continue
            self._done.add(mbid)
            processed += 1

            for neighbour in self._neighbours(payload, mbid):
                if neighbour not in self.discovered:
                    self.discovered.add(neighbour)
                    queue.append(neighbour)

            if processed % self.config.checkpoint_every == 0:
                self._save_checkpoint()
                logger.info(
                    "processed %d | discovered %d | queued %d",
                    processed,
                    len(self.discovered),
                    len(queue),
                )

        self._save_checkpoint()
        logger.info(
            "crawl finished: %d processed, %d discovered, %d failures",
            processed,
            len(self.discovered),
            len(self.failures),
        )

    def _neighbours(self, payload: bytes, mbid: str) -> list[str]:
        try:
            return [n.mbid for n in self.source.parse(payload, exclude_mbid=mbid)]
        except ValueError:
            logger.warning("unparseable similarity payload for %s", mbid)
            return []

    def _archive_or_fetch(self, key: str, url: str, mbid: str) -> bytes | None:
        existing = self.archive.get(key)
        if existing is not None:
            return existing
        payload = self._fetch_with_retries(url, mbid)
        if payload is not None:
            self.archive.put(key, payload)
        return payload

    def _fetch_with_retries(self, url: str, mbid: str) -> bytes | None:
        for attempt in range(self.config.max_retries):
            try:
                payload = self.fetcher(url)
            except TransientFetchError as exc:
                backoff = self.config.request_delay_seconds * (2**attempt)
                logger.warning("retry %d for %s: %s", attempt + 1, mbid, exc)
                time.sleep(backoff)
                continue
            time.sleep(self.config.request_delay_seconds)
            return payload

        logger.error("giving up on %s after %d attempts", mbid, self.config.max_retries)
        if mbid not in self.failures:
            self.failures.append(mbid)
        return None

    def _load_checkpoint(self) -> dict[str, set[str]]:
        if not self.checkpoint_path.is_file():
            return {"done": set(), "discovered": set()}
        state = json.loads(self.checkpoint_path.read_text())
        # Every checkpoint written before the algorithm was selectable
        # predates this field, so a missing one means the production
        # algorithm rather than a refusal.
        stored = state.get("algorithm", PRODUCTION_ALGORITHM)
        if stored != self.config.algorithm:
            raise ValueError(
                f"checkpoint {self.checkpoint_path} was written by a crawl "
                f"under {stored!r}; refusing to resume it under "
                f"{self.config.algorithm!r} (RC-H3 — a resumed crawl would "
                "silently skip every artist the other algorithm finished)"
            )
        return {
            "done": set(state.get("done", [])),
            "discovered": set(state.get("discovered", [])),
        }

    def _save_checkpoint(self) -> None:
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(
            json.dumps(
                {
                    "algorithm": self.config.algorithm,
                    "done": sorted(self._done),
                    "discovered": sorted(self.discovered),
                },
                sort_keys=True,
            )
        )
