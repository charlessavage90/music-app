"""GRT collection: run both arms' capped crawls.

Governing document:
docs/superpowers/specs/2026-07-29-algb-trial-build-preregistration.md

Collection only. Scoring lives in grt_score.py so it can be re-run without
re-hitting the service, and so neither script can be shaped by the other's
output. Both are committed before either produces a result.

    AB - ALG-B, capped 3,000, FRESH archive directory (and GR-3 additionally
         routes every key into an ALG-B sub-tree).
    A0 - ALG-E control at the same target, reading the PRODUCTION archive
         through ReadOnlyArchive, whose put() raises. Zero fetches expected.

GRT-G1 (archive safety) is enforced structurally by that wrapper rather than
checked afterwards, and is ALSO counted before and after, because a structural
guarantee that is never verified is a belief.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from artistpath_builder.archive import LocalArchive, RawArchive
from artistpath_builder.config import (
    PERMITTED_ALGORITHMS,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.crawl import Crawler, http_fetcher
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

ALG_B = PERMITTED_ALGORITHMS[1]
TARGET = 3_000

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"
PRODUCTION_ARCHIVE = SCRATCH / "graph-archive"
BOOTSTRAP = SCRATCH / "bootstrap.json"


class ArchiveWriteRefused(RuntimeError):
    """The control arm tried to write into the production archive."""


class OverlayArchive:
    """Reads through to a base archive; writes ONLY to an overlay.

    Added by GRT-A1 (pre-run for AB, mid-collection for A0), after
    ReadOnlyArchive fired on the first A0 attempt and refuted the
    pre-registration's assumption that a 3,000-target BFS stays inside the
    production archive. It does not: the production 75,000 is not closed under
    one-hop neighbours, so a fresh BFS escapes it within ~1,400 artists.

    The base stays strictly read-only — the guarantee ReadOnlyArchive gave is
    kept, because nothing here can write to it — while the handful of genuinely
    new responses land beside it and are counted.
    """

    def __init__(self, base: RawArchive, overlay: RawArchive) -> None:
        self._base = base
        self._overlay = overlay
        self.written: list[str] = []

    def put(self, key: str, payload: bytes) -> None:
        self._overlay.put(key, payload)
        self.written.append(key)

    def get(self, key: str):
        found = self._base.get(key)
        return found if found is not None else self._overlay.get(key)

    def has(self, key: str) -> bool:
        return self._base.has(key) or self._overlay.has(key)

    def keys(self):
        seen = set()
        for k in self._base.keys():
            seen.add(k)
            yield k
        for k in self._overlay.keys():
            if k not in seen:
                yield k


class ReadOnlyArchive:
    """Wraps an archive and refuses every write.

    The production archive is 75,000 responses that took 4.25 hours to gather
    and cannot be gathered again. `Crawler._archive_or_fetch` calls put() on
    any artist it does not find, so pointing a crawl at the archive is safe
    only if put() cannot fire. It raising is a FINDING, not a bug: it means
    ALG-E's frontier left the production crawl's coverage.
    """

    def __init__(self, inner: RawArchive) -> None:
        self._inner = inner
        self.refusals: list[str] = []

    def put(self, key: str, payload: bytes) -> None:
        self.refusals.append(key)
        raise ArchiveWriteRefused(
            f"control arm tried to write {key!r} into the production archive "
            "(GRT-G1). This means ALG-E discovered an artist the production "
            "crawl never fetched — report it; do not relax this guard."
        )

    def get(self, key: str):
        return self._inner.get(key)

    def has(self, key: str) -> bool:
        return self._inner.has(key)

    def keys(self):
        return self._inner.keys()


def _count_files(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.is_file())


def run_arm(arm: str) -> dict:
    if arm == "AB":
        config = BuilderConfig(algorithm=ALG_B, target_artist_count=TARGET)
        archive: RawArchive = LocalArchive(SCRATCH / "grt-archive-algb")
        checkpoint = SCRATCH / "grt-checkpoint-algb.json"
    elif arm == "A0":
        config = BuilderConfig(algorithm=PRODUCTION_ALGORITHM, target_artist_count=TARGET)
        # GRT-A1: read-through to production, writes to an overlay. The
        # production archive remains unwritable by construction.
        archive = OverlayArchive(
            LocalArchive(PRODUCTION_ARCHIVE),
            LocalArchive(SCRATCH / "grt-overlay-alge"),
        )
        checkpoint = SCRATCH / "grt-checkpoint-alge.json"
    else:
        raise SystemExit(f"unknown arm {arm!r}")

    bootstrap = json.loads(BOOTSTRAP.read_text())
    seeds = [row["mbid"] for row in bootstrap]

    before = _count_files(PRODUCTION_ARCHIVE)
    started = time.monotonic()

    crawler = Crawler(
        config=config,
        archive=archive,
        source=ListenBrainzSource(config),
        fetcher=http_fetcher(config),
        checkpoint_path=checkpoint,
    )
    crawler.crawl(seeds)

    elapsed = time.monotonic() - started
    after = _count_files(PRODUCTION_ARCHIVE)

    result = {
        "arm": arm,
        "algorithm": config.algorithm,
        "target": TARGET,
        "discovered": len(crawler.discovered),
        "done": len(crawler._done),
        "failures": len(crawler.failures),
        "failure_mbids": crawler.failures[:20],
        "elapsed_seconds": round(elapsed, 1),
        "production_archive_files_before": before,
        "production_archive_files_after": after,
        "GRT_G1_archive_untouched": before == after,
        "control_write_refusals": getattr(archive, "refusals", []),
        # GRT-A1: responses this arm had to fetch because production never
        # held them. A direct measure of how far a fresh BFS escapes the
        # production archive's coverage.
        "overlay_writes": len(getattr(archive, "written", [])),
    }
    (HERE / f"grt_crawl_{arm}.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=["AB", "A0"])
    args = parser.parse_args()
    out = run_arm(args.arm)
    print(json.dumps(out, indent=2, sort_keys=True))
