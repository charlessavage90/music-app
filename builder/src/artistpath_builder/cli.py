"""Builder entry points.

    artistpath-build bootstrap  --out bootstrap.json
    artistpath-build crawl      --bootstrap bootstrap.json --archive-dir ./archive
    artistpath-build fame       --archive-dir ./archive
    artistpath-build build      --archive-dir ./archive --out graph-v1.bin
    artistpath-build fixture    --graph graph-v1.bin --out fixture.bin --size 500

`refrontier` is a REPAIR step, not a pipeline stage: it rebuilds a checkpoint's
`discovered` set from the archive when the frontier was never recorded
(ULC-F3), and is run before a `crawl` that is meant to resume. Offline.

Popularity is score-weighted in-degree, computed from the similarity archive
during `build` (findings 6f). There is no separate popularity input.

FAME is different and is NOT popularity: `fame` fetches ListenBrainz listener
counts into the archive, because `build` may not touch the network (spec §9).
It runs after `crawl` and before `build`. The two quantities are never read as
each other — see fame.py and log §2.11/§2.12.
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
from artistpath_builder.config import PERMITTED_ALGORITHMS, BuilderConfig
from artistpath_builder.crawl import Crawler, http_fetcher
from artistpath_builder.fixture import extract_fixture
from artistpath_builder.frontier import reconstruct_referenced, rewrite_checkpoint
from artistpath_builder.manifest import build_manifest, write_manifest
from artistpath_builder.fame import fetch_fame, lb_fame_fetcher, seed_fame
from artistpath_builder.pipeline import archive_artists, build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.sources.seeds import (
    BOOTSTRAP_CEILING,
    bootstrap_url,
    parse_bootstrap_page,
)

PAGE_SIZE = 1000


def _config(args) -> BuilderConfig:
    """Allow the discovery cap and the source algorithm to be overridden for
    trial runs.

    The DEFAULT stays the production algorithm: flipping the default is the
    re-crawl decision, which is the owner's (NEXT.md).

    Validation lives here at the CLI boundary rather than in
    `BuilderConfig.__post_init__` — analysis harnesses under builder/analysis/
    construct configs directly and own their own validation, and the frozen
    dataclass stays a dumb container.
    """
    overrides: dict = {}
    target = getattr(args, "target", None)
    if target:
        overrides["target_artist_count"] = target
    algorithm = getattr(args, "algorithm", None)
    if algorithm:
        if algorithm not in PERMITTED_ALGORITHMS:
            raise SystemExit(
                f"unknown algorithm {algorithm!r}: the endpoint accepts a "
                "closed enum of six values (CS-P0e) — see "
                "artistpath_builder.config.PERMITTED_ALGORITHMS"
            )
        overrides["algorithm"] = algorithm
    # Both added for MSW- Task 9. cap_strategy needs no validation here:
    # BuilderConfig.__post_init__ rejects anything outside
    # PERMITTED_CAP_STRATEGIES, so a typo raises before a build starts.
    #
    # require_fame is store_true rather than a tri-state flag, so it can only
    # ever turn the guard ON from the CLI. Once config.py's default flips at
    # adoption, omitting the flag inherits True — a CLI that could silently
    # switch the guard OFF is the one thing this must not offer.
    cap_strategy = getattr(args, "cap_strategy", None)
    if cap_strategy:
        overrides["cap_strategy"] = cap_strategy
    if getattr(args, "require_fame", False):
        overrides["require_fame"] = True
    return BuilderConfig(**overrides)


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


def cmd_refrontier(args) -> int:
    """Rebuild the checkpoint's `discovered` set from the archive (ULC-F3).

    Offline: reads archived responses only, never the network.
    """
    config = _config(args)
    source = ListenBrainzSource(config)
    referenced = reconstruct_referenced(_archive(args), config, source)
    stats = rewrite_checkpoint(Path(args.checkpoint), config, referenced)
    print(
        f"done {stats['done']} | discovered {stats['discovered']} | "
        f"frontier {stats['frontier']}"
    )
    return 0


def cmd_fame(args) -> int:
    """Fetch ListenBrainz listener counts into the archive.

    Separate from `build` because `build` may not touch the network (spec §9).
    Resumable: re-running costs only what is not already recorded, so an
    interrupted fetch is picked up rather than restarted.
    """
    config = _config(args)
    archive = _archive(args)
    source = ListenBrainzSource(config)
    mbids = archive_artists(archive, config, source)
    logging.info("fame: %d artists in this archive", len(mbids))

    if args.seed:
        if not args.seed_sha:
            raise SystemExit(
                "--seed requires --seed-sha: the snapshot's sha256 IS the "
                "instrument's identity (FAM-AM1.7), and an unverified file "
                "has unknown provenance. Take it from the manifest sidecar."
            )
        # No log line here: `seed_fame` already emits "fame seed: …" itself.
        # Logging it again at the call site printed the same counts twice per
        # run. Deferred at Task 8 with the condition "whichever task next
        # touches cli.py"; Task 9 is that task.
        seed_fame(
            archive,
            Path(args.seed),
            expected_sha256=args.seed_sha,
            fetched=args.seed_date,
        )

    started = time.monotonic()
    report = fetch_fame(
        archive,
        mbids,
        lb_fame_fetcher(config),
        pause_seconds=config.request_delay_seconds,
    )
    logging.info(
        "fame: %d fetched (%d null), %d already recorded, %d total, %.0fs",
        report.fetched,
        report.nulls,
        report.skipped,
        report.total,
        time.monotonic() - started,
    )
    if report.total != len(mbids):
        raise SystemExit(
            f"fame covered {report.total} artists but the archive has "
            f"{len(mbids)} — refusing to report success on a partial pass"
        )
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
    p_crawl.add_argument(
        "--algorithm",
        default=None,
        help="source algorithm for trial runs; default is production's (ALG-E)",
    )
    add_archive_args(p_crawl)
    p_crawl.set_defaults(func=cmd_crawl)

    p_refrontier = sub.add_parser("refrontier")
    p_refrontier.add_argument("--checkpoint", default="./checkpoint.json")
    p_refrontier.add_argument(
        "--algorithm",
        default=None,
        help="which algorithm's archive tree to scan; default production's",
    )
    add_archive_args(p_refrontier)
    p_refrontier.set_defaults(func=cmd_refrontier)

    p_fame = sub.add_parser("fame")
    p_fame.add_argument(
        "--algorithm",
        default=None,
        help="which algorithm's archive tree to cover; default production's",
    )
    p_fame.add_argument(
        "--seed",
        default=None,
        help="an already-fetched snapshot to import before fetching the rest",
    )
    p_fame.add_argument(
        "--seed-sha",
        default=None,
        help="expected sha256 of --seed, from its manifest sidecar (required "
        "with --seed; never transcribe it by hand)",
    )
    p_fame.add_argument(
        "--seed-date",
        default="unknown",
        help="fetch date recorded for seeded records, from the seed's manifest",
    )
    add_archive_args(p_fame)
    p_fame.set_defaults(func=cmd_fame)

    p_build = sub.add_parser("build")
    p_build.add_argument("--out", required=True)
    p_build.add_argument(
        "--algorithm",
        default=None,
        help="which algorithm's archive tree to build from; default production's",
    )
    p_build.add_argument(
        "--cap-strategy",
        default=None,
        help="connection rule; default config's (mutual_knn until adoption)",
    )
    p_build.add_argument(
        "--require-fame",
        action="store_true",
        help="refuse to build unless every kept artist has a fame record "
        "(MSW-G3); the adopted artifact is built with this explicitly on",
    )
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
