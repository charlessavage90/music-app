"""Builder entry points.

    artistpath-build bootstrap  --out bootstrap.json
    artistpath-build crawl      --bootstrap bootstrap.json --archive-dir ./archive
    artistpath-build build      --archive-dir ./archive --out graph-v1.bin
    artistpath-build fixture    --graph graph-v1.bin --out fixture.bin --size 500

Popularity is score-weighted in-degree, computed from the similarity archive
during `build` (findings 6f). There is no separate popularity input.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
import time
from pathlib import Path

from artistpath_builder.acceptance import (
    PRODUCTION_ACCEPTANCE,
    AcceptanceCriteria,
    check_acceptance,
)
from artistpath_builder.archive import LocalArchive, S3Archive
from artistpath_builder.artifact import deserialise, serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler, http_fetcher
from artistpath_builder.fixture import extract_fixture
from artistpath_builder.manifest import build_manifest, write_manifest
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.sources.seeds import (
    BOOTSTRAP_CEILING,
    bootstrap_url,
    parse_bootstrap_page,
)

PAGE_SIZE = 1000


def _config(args) -> BuilderConfig:
    """Allow the discovery cap to be overridden for trial runs."""
    target = getattr(args, "target", None)
    if target:
        return BuilderConfig(target_artist_count=target)
    return BuilderConfig()


def _archive(args):
    if args.s3_bucket:
        return S3Archive(args.s3_bucket, args.s3_prefix)
    return LocalArchive(Path(args.archive_dir))


def write_bootstrap(artists, path: Path) -> None:
    """Serialise bootstrap artists to disk.

    Uses dataclasses.asdict, not __dict__ — these are slots=True dataclasses
    and have no instance dict.
    """
    path.write_text(
        json.dumps([dataclasses.asdict(a) for a in artists], sort_keys=True),
        encoding="utf-8",
    )


def cmd_bootstrap(args) -> int:
    """Fetch the top artists that seed the snowball.

    The sitewide endpoint serves at most BOOTSTRAP_CEILING artists whatever
    is requested (Task 1 findings section 2), so this is deliberately small.
    """
    config = _config(args)
    fetch = http_fetcher(config)
    artists = []
    offset = 0
    while offset < BOOTSTRAP_CEILING:
        page = parse_bootstrap_page(
            fetch(bootstrap_url(config, offset=offset, count=PAGE_SIZE))
        )
        if not page:
            break
        artists.extend(page)
        offset += PAGE_SIZE

    write_bootstrap(artists, Path(args.out))
    logging.info("wrote %d bootstrap artists to %s", len(artists), args.out)
    return 0


def cmd_crawl(args) -> int:
    config = _config(args)
    bootstrap = json.loads(Path(args.bootstrap).read_text())
    crawler = Crawler(
        config=config,
        archive=_archive(args),
        source=ListenBrainzSource(config),
        fetcher=http_fetcher(config),
        checkpoint_path=Path(args.checkpoint),
    )
    crawler.crawl([row["mbid"] for row in bootstrap])
    if crawler.failures:
        logging.warning("%d artists failed permanently", len(crawler.failures))
    return 0


def cmd_build(args) -> int:
    config = _config(args)
    started = time.monotonic()
    graph = build_from_archive(config, _archive(args), ListenBrainzSource(config))
    # Refuse to write an artifact with the log §2.8 failure signature. This is
    # the emission point, and nothing downstream re-checks: the artifact is
    # gitignored, so a bad one is only ever caught by a human noticing a
    # missing artist. Raises rather than warns, by design.
    check_acceptance(graph, getattr(args, "criteria", PRODUCTION_ACCEPTANCE))
    payload = serialise(graph)
    elapsed = time.monotonic() - started
    out = Path(args.out)
    out.write_bytes(payload)
    write_manifest(out, build_manifest(graph, config, payload, elapsed))
    mean_edges = graph.edge_count / graph.artist_count if graph.artist_count else 0
    logging.info(
        "wrote %s: %d artists, %d edges (%.1f per artist), %.1f MB, %.0fs",
        args.out,
        graph.artist_count,
        graph.edge_count,
        mean_edges,
        len(payload) / 1e6,
        elapsed,
    )
    return 0


def cmd_fixture(args) -> int:
    graph = deserialise(Path(args.graph).read_bytes())
    # seed_mbid=None means "most popular artist" — see fixture.most_popular_index.
    fixture = extract_fixture(graph, size=args.size, seed_mbid=args.seed_mbid)
    Path(args.out).write_bytes(serialise(fixture))
    logging.info("wrote fixture: %d artists", fixture.artist_count)
    return 0


def main(
    argv: list[str] | None = None,
    *,
    criteria: AcceptanceCriteria = PRODUCTION_ACCEPTANCE,
) -> int:
    """`criteria` is deliberately NOT an argparse flag.

    There is no way for a user to relax or skip the acceptance check from the
    command line — an escape hatch on this guard would be the first thing
    reached for when a build fails, which is exactly when it must hold. Tests
    substitute scaled-down criteria by calling `main` in-process.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="artistpath-build")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_archive_args(p):
        p.add_argument("--archive-dir", default="./archive")
        p.add_argument("--s3-bucket", default=None)
        p.add_argument("--s3-prefix", default="raw")

    p_bootstrap = sub.add_parser("bootstrap")
    p_bootstrap.add_argument("--out", required=True)
    p_bootstrap.set_defaults(func=cmd_bootstrap)

    p_crawl = sub.add_parser("crawl")
    p_crawl.add_argument("--bootstrap", required=True)
    p_crawl.add_argument("--checkpoint", default="./checkpoint.json")
    p_crawl.add_argument(
        "--target", type=int, default=None, help="discovery cap; for trial runs"
    )
    add_archive_args(p_crawl)
    p_crawl.set_defaults(func=cmd_crawl)

    p_build = sub.add_parser("build")
    p_build.add_argument("--out", required=True)
    add_archive_args(p_build)
    p_build.set_defaults(func=cmd_build)

    p_fixture = sub.add_parser("fixture")
    p_fixture.add_argument("--graph", required=True)
    p_fixture.add_argument("--out", required=True)
    p_fixture.add_argument("--size", type=int, default=500)
    p_fixture.add_argument("--seed-mbid", default=None)
    p_fixture.set_defaults(func=cmd_fixture)

    args = parser.parse_args(argv)
    args.criteria = criteria
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
