"""The no-release-tail drop rule (owner decision 2026-08-01, NEXT.md).

Keep a release-less artist only where a commercial-DSP link exists AND a clip
resolves; 7,035 of the 7,686 no-release tail are dropped. The rule is ADOPTED,
not proposed — these tests apply it and never re-open it.

The list is a 2026-08-01 SNAPSHOT and is applied verbatim. It must never be
re-resolved at build time: `build_from_archive` is offline by a hard rule and
spec §9 requires byte-identical builds, so a build that asked Deezer whether a
clip still resolves would make two builds of one archive disagree.

Dropped beside the nameless and special-purpose drops and BEFORE the mass
computation, so a dropped artist contributes to no marginal. That is what
`test_dropping_equals_never_having_been_archived` pins: the drop must produce
the same graph the archive would have produced had the artist never appeared,
rather than the old graph minus rows.
"""

import json
from hashlib import sha256

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.no_release_drop import DROP_LIST_SHA256, load_drop_mbids
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

# Recorded in NEXT.md and the 2026-08-01 handoff, and reproduced from the
# frozen probe output: sha256 of json.dumps(drop_mbids, sort_keys=True).
RECORDED_SHA256 = "d876c7baec3626094251503f425f3a5a571e8e0d74ac37bf10e6c37bfb7ac1d3"
RECORDED_COUNT = 7035

A, B, C = ("a" * 36, "b" * 36, "c" * 36)
# Real MBIDs from the frozen list: one the rule drops, one it keeps.
DROPPED = "000cf466-9147-4377-8b8a-84bb576b5813"
KEPT_TAIL = "00471495-e27f-480c-9d32-4c015b4c9c94"

# A <-> B <-> C is a healthy core. Both tail artists hang off B.
SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5), (DROPPED, "Ghost", 4), (KEPT_TAIL, "Keeper", 3)],
    C: [(B, "Beta", 5)],
    DROPPED: [(B, "Beta", 4)],
    KEPT_TAIL: [(B, "Beta", 3)],
}


def _similar_body(rows) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "comment": "", "score": score}
            for n, name, score in rows
        ]
    ).encode()


def _archive(tmp_path, similar, subdir="archive"):
    source = ListenBrainzSource(BuilderConfig())
    archive = LocalArchive(tmp_path / subdir)
    for mbid, rows in similar.items():
        archive.put(f"similar/{source.name}/{mbid}.json", _similar_body(rows))
    return archive


def _build(archive, **overrides):
    config = BuilderConfig(**overrides)
    return build_from_archive(config, archive, ListenBrainzSource(config))


@pytest.fixture
def archive(tmp_path):
    return _archive(tmp_path, SIMILAR)


def test_listed_artist_is_dropped(archive):
    assert DROPPED not in _build(archive).mbids


def test_tail_artist_the_rule_keeps_survives(archive):
    # The rule keeps 651 of the tail. A keep-list artist must be untouched —
    # otherwise the wiring implements "drop the tail", not the adopted rule.
    assert KEPT_TAIL in _build(archive).mbids


def test_drop_is_off_when_the_config_flag_is_off(archive):
    # Without this the suite cannot tell the drop from an unrelated prune.
    assert DROPPED in _build(archive, drop_no_release_tail=False).mbids


def test_dropping_equals_never_having_been_archived(tmp_path):
    # Dropped BEFORE the mass computation, so the dropped artist perturbs no
    # surviving artist's marginal: the built graph must be identical to one
    # built from an archive the artist never appeared in.
    without = {
        mbid: [row for row in rows if row[0] != DROPPED]
        for mbid, rows in SIMILAR.items()
        if mbid != DROPPED
    }
    dropped = _build(_archive(tmp_path, SIMILAR, "with"))
    absent = _build(_archive(tmp_path, without, "without"))

    assert dropped.mbids == absent.mbids
    assert dropped.pop_raw == absent.pop_raw
    assert dropped.offsets.tolist() == absent.offsets.tolist()
    assert dropped.neighbours.tolist() == absent.neighbours.tolist()
    assert dropped.scores.tolist() == absent.scores.tolist()


def test_shipped_list_matches_the_frozen_snapshot():
    mbids = load_drop_mbids()
    assert len(mbids) == RECORDED_COUNT
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    assert digest == RECORDED_SHA256
    assert DROP_LIST_SHA256 == RECORDED_SHA256
