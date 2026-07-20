import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.artifact import serialise
from artistpath_builder.config import BuilderConfig
from artistpath_builder.crawl import Crawler
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C = ("a" * 36, "b" * 36, "c" * 36)

SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5)],
    C: [(B, "Beta", 5)],
}

USERS = {A: 300, B: 200, C: 100}
NAMES = {A: "Alpha", B: "Beta", C: "Gamma"}


def _similar_body(mbid: str) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "score": score}
            for n, name, score in SIMILAR[mbid]
        ]
    ).encode()


def _stats_body(mbid: str) -> bytes:
    return json.dumps(
        {
            "payload": {
                "artist_mbid": mbid,
                "artist_name": NAMES[mbid],
                "total_user_count": USERS[mbid],
                "total_listen_count": USERS[mbid] * 7,
            }
        }
    ).encode()


class RecordedFetcher:
    def __init__(self):
        self.calls = 0

    def __call__(self, url: str) -> bytes:
        self.calls += 1
        for mbid in SIMILAR:
            if mbid in url:
                return _stats_body(mbid) if "/listeners" in url else _similar_body(mbid)
        return b"[]"


class ExplodingFetcher:
    """Stands in for having no network at all."""

    def __call__(self, url: str) -> bytes:
        raise AssertionError(f"network was used during replay: {url}")


@pytest.fixture
def config():
    return BuilderConfig(requests_per_second=1000.0)


def _seed_archive(archive, source, mbids):
    for mbid in mbids:
        archive.put(f"similar/{source.name}/{mbid}.json", _similar_body(mbid))
        archive.put(f"stats/{mbid}.json", _stats_body(mbid))


def test_rebuild_from_archive_is_byte_identical_with_no_network(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)

    # First build: crawls the "network", filling the archive.
    fetcher = RecordedFetcher()
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=fetcher,
        checkpoint_path=tmp_path / "checkpoint.json",
    ).crawl([A])
    # Two calls per artist (similarity + stats), three artists discovered.
    assert fetcher.calls == 6

    first = serialise(build_from_archive(config, archive, source))

    # Second build: same archive, a fetcher that raises if touched.
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=ExplodingFetcher(),
        checkpoint_path=tmp_path / "checkpoint2.json",
    ).crawl([A])

    second = serialise(build_from_archive(config, archive, source))

    assert first == second


def test_replay_produces_a_connected_graph(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    assert graph.mbids == [A, B, C]
    assert graph.edge_count > 0


def test_popularity_comes_from_archived_user_counts(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    # A has the most distinct listeners, C the fewest (spec 4.1).
    assert graph.popularity[graph.mbids.index(A)] == max(graph.popularity)
    assert graph.popularity[graph.mbids.index(C)] == min(graph.popularity)


def test_artists_missing_from_the_archive_are_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    # C is absent — a crawl failure. The build must not raise.
    graph = build_from_archive(config, archive, source)
    assert C not in graph.mbids


def test_artist_without_archived_stats_is_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    archive.put(f"similar/{source.name}/{C}.json", _similar_body(C))
    # C has neighbours but no popularity, so it cannot be routed through.
    graph = build_from_archive(config, archive, source)
    assert C not in graph.mbids
