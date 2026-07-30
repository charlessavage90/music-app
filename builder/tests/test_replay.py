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
    # One call per artist: similarity only.
    assert fetcher.calls == 3

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


def test_popularity_is_score_weighted_indegree(tmp_path, config):
    # Graph A<->B<->C: B is the hub, receiving in-links from both A and C, so
    # it is most popular; C is a leaf and least popular (findings 6f).
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    assert graph.pop_raw[graph.mbids.index(B)] == max(graph.pop_raw)
    assert graph.pop_raw[graph.mbids.index(C)] == min(graph.pop_raw)


def test_popularity_needs_no_external_input(tmp_path, config):
    # The whole point of in-degree: build takes only the archive.
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])
    # Signature has no popularity parameter; this call proves it.
    graph = build_from_archive(config, archive, source)
    assert graph.artist_count == 3


def test_names_and_disambiguation_are_harvested_from_neighbour_rows(tmp_path, config):
    # There is no per-artist metadata record; an artist's name and
    # disambiguation appear only where it is listed as someone else's
    # neighbour.
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B, C])

    graph = build_from_archive(config, archive, source)
    assert graph.names[graph.mbids.index(A)] == "Alpha"
    assert graph.disambiguations[graph.mbids.index(A)] == "UK band"


ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)


def test_build_reads_only_its_own_algorithms_subtree(tmp_path, config):
    # RC-H3, build side. The flat tree (production) and the ALG-B sub-tree
    # sit in one archive; each build must see only its own.
    algb_config = BuilderConfig(requests_per_second=1000.0, algorithm=ALG_B)
    source = ListenBrainzSource(config)
    archive = LocalArchive(tmp_path / "archive")
    _seed_archive(archive, source, [A, B, C])  # flat: A<->B<->C
    # ALG-B tree: A and B only, so C was never crawled under ALG-B.
    for mbid in (A, B):
        archive.put(f"similar/{source.name}/{ALG_B}/{mbid}.json", _similar_body(mbid))

    algb_graph = build_from_archive(
        algb_config, archive, ListenBrainzSource(algb_config)
    )
    assert C not in algb_graph.mbids


def test_a_foreign_algorithm_subtree_cannot_perturb_the_flat_build(tmp_path, config):
    """The flat (production) build must be byte-identical whether or not
    another algorithm's sub-tree is sitting beside it (RC-H3).

    Two earlier versions of this test were VACUOUS and both were caught by
    closeout B3 break-the-code spot checks on 2026-07-29. They are recorded
    because each failed for a different reason and the second is subtle:

      1. Asserting on `mbids` proved nothing — a nested key parses into a
         bogus mbid that no real artist lists as a neighbour, so mutual k-NN
         drops its edges and `largest_component` drops the node. The node
         list is identical either way.
      2. Asserting byte-identity while contaminating with COPIES of the same
         responses also proved nothing — that raises every artist's in-degree
         by roughly the same factor, and `pop_raw` is normalised, so the
         perturbation cancels exactly.

    So the contaminant here is deliberately ASYMMETRIC: a sub-tree node
    pointing hard at the graph's LEAST popular artist. Its edge is still
    dropped by mutual k-NN, but in-degree is accumulated BEFORE the cap, so
    it moves that artist's popularity relative to everyone else's — which is
    precisely the silent corruption RC-H3 warns about.

    ⚠ **This invariant is defended TWICE, so breaking ONE guard will not turn
    this test red.** A future break-the-code spot check needs to know that,
    because it looks exactly like vacuity and is not:

      - the RC-H3 nested-key skip in `build_from_archive`, and
      - the GR-1 drop rule's orphan clause (`known - identities.keys()`) —
        a nested-key pseudo-mbid never appears as anyone's neighbour, so it
        has no identity row and is dropped as nameless.

    Verified 2026-07-29 by disabling each alone (output unchanged) and both
    together: the contaminated build then inverts the popularity ordering
    outright, carrying C from least popular (0.0) to most popular (1.0). The
    corruption is real and severe; the redundancy is deliberate defence in
    depth, and the RC-H3 skip is kept so the isolation does not silently
    depend on the drop rule staying where it is.
    """
    source = ListenBrainzSource(config)
    # C is the leaf: lowest in-degree in the A<->B<->C fixture.
    contaminant = json.dumps(
        [{"artist_mbid": C, "name": "Gamma", "comment": "", "score": 5000}]
    ).encode()

    clean = LocalArchive(tmp_path / "clean")
    _seed_archive(clean, source, [A, B, C])
    expected = serialise(build_from_archive(config, clean, source))

    contaminated = LocalArchive(tmp_path / "contaminated")
    _seed_archive(contaminated, source, [A, B, C])
    contaminated.put(f"similar/{source.name}/{ALG_B}/{'d' * 36}.json", contaminant)

    assert serialise(build_from_archive(config, contaminated, source)) == expected


def test_uncrawled_neighbours_are_not_nodes(tmp_path, config):
    # C is listed as B's neighbour but was never crawled, so it has no
    # out-edges and cannot be routed through. It must not become a node, and
    # must not contribute to anyone's in-degree.
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed_archive(archive, source, [A, B])
    graph = build_from_archive(config, archive, source)
    assert C not in graph.mbids
