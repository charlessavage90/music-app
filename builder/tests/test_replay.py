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

NAMES = {A: "Alpha", B: "Beta", C: "Gamma"}
COMMENTS = {A: "UK band", B: "US duo", C: ""}

# Derived offline from the spark dump; distinct listeners per artist.
POPULARITY = {A: 300, B: 200, C: 100}


def _similar_body(mbid: str) -> bytes:
    return json.dumps(
        [
            {
                "artist_mbid": n,
                "name": NAMES[n],
                "comment": COMMENTS[n],
                "score": score,
            }
            for n, _, score in SIMILAR[mbid]
        ]
    ).encode()


class RecordedFetcher:
    def __init__(self):
        self.calls = 0

    def __call__(self, url: str) -> bytes:
        self.calls += 1
        for mbid in SIMILAR:
            if mbid in url:
                return _similar_body(mbid)
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
    # One call per artist now that stats come from the dump.
    assert fetcher.calls == 3

    first = serialise(build_from_archive(config, archive, source, POPULARITY))

    # Second build: same archive, a fetcher that raises if touched.
    Crawler(
        config=config,
        archive=archive,
        source=source,
        fetcher=ExplodingFetcher(),
        checkpoint_path=tmp_path / "checkpoint2.json",
    ).crawl([A])

    second = serialise(build_from_archive(config, archive, source, POPULARITY))

    assert first == second


def test_replay_produces_a_connected_graph(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source, POPULARITY)
    assert graph.mbids == [A, B, C]
    assert graph.edge_count > 0


def test_popularity_comes_from_the_supplied_table(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source, POPULARITY)
    # A has the most distinct listeners, C the fewest (spec 4.1).
    assert graph.popularity[graph.mbids.index(A)] == max(graph.popularity)
    assert graph.popularity[graph.mbids.index(C)] == min(graph.popularity)


def test_names_and_disambiguation_are_harvested_from_neighbour_rows(tmp_path, config):
    # There is no per-artist metadata record; an artist's name and
    # disambiguation appear only where it is listed as someone else's
    # neighbour.
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source, POPULARITY)
    assert graph.names[graph.mbids.index(A)] == "Alpha"
    assert graph.disambiguations[graph.mbids.index(A)] == "UK band"


def test_artists_missing_from_the_archive_are_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    # C was never crawled. The build must not raise.
    graph = build_from_archive(config, archive, source, POPULARITY)
    assert C not in graph.mbids


def test_artist_without_popularity_is_skipped(tmp_path, config):
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])
    # C has neighbours but no popularity, so it cannot be weighed and is
    # not a node.
    graph = build_from_archive(config, archive, source, {A: 300, B: 200})
    assert C not in graph.mbids
