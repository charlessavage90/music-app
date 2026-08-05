"""The nameless-artist drop rule (owner decision 2026-07-28, NEXT.md; REQ-2).

A nameless artist is unsearchable, clipless, and renderable only as a blank
card, so `build_from_archive` drops it before the largest-component prune —
and a neighbour stranded by the drop is pruned rather than kept dangling.

Confirmed 2026-07-29 by the owner against MusicBrainz: the three most popular
nameless MBIDs in the adopted artifact all return "Artist not found". They are
deleted or merged upstream entities that survive in the similarity data, so
backfilling names by MBID — the alternative the owner declined — is not merely
unattractive but impossible.
"""

import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

A, B, C, N, S = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)

# A <-> B <-> C is a healthy named core. N is nameless: every row that
# mentions it carries an empty name. S is a satellite whose only tie is to N.
SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5), (N, "", 4)],
    C: [(B, "Beta", 5)],
    N: [(B, "Beta", 4), (S, "Sigma", 6)],
    S: [(N, "", 6)],
}


def _similar_body(mbid: str) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "comment": "", "score": score}
            for n, name, score in SIMILAR[mbid]
        ]
    ).encode()


@pytest.fixture
def archive(tmp_path):
    source = ListenBrainzSource(BuilderConfig())
    archive = LocalArchive(tmp_path / "archive")
    for mbid in SIMILAR:
        archive.put(f"similar/{source.name}/{mbid}.json", _similar_body(mbid))
    return archive


def _build(archive):
    # drop_unlistenable pinned off: the nameless drop is the subject; the
    # synthetic archive is covered by no ULF- census (factor-table idiom).
    config = BuilderConfig(drop_unlistenable=False)
    return build_from_archive(config, archive, ListenBrainzSource(config))


def test_nameless_artist_is_dropped(archive):
    assert N not in _build(archive).mbids


def test_stranded_neighbour_of_dropped_node_is_pruned_not_dangling(archive):
    # S's only edge is to N. With N dropped, S must fall out at the
    # largest-component prune — never survive as an edgeless node.
    graph = _build(archive)
    assert S not in graph.mbids
    assert sorted(graph.mbids) == sorted([A, B, C])


def test_every_emitted_artist_has_a_name(archive):
    assert all(name.strip() for name in _build(archive).names)
