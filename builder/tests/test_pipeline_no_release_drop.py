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
from artistpath_builder.config import (
    CANDIDATE_ALGORITHM,
    PERMITTED_ALGORITHMS,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.no_release_drop import (
    DROP_LIST_SHA256,
    NoDropListForAlgorithm,
    load_drop_mbids,
)
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

# Recorded in NEXT.md and the 2026-08-01 handoff, and reproduced from the
# frozen probe output: sha256 of json.dumps(drop_mbids, sort_keys=True).
RECORDED_SHA256 = "d876c7baec3626094251503f425f3a5a571e8e0d74ac37bf10e6c37bfb7ac1d3"
RECORDED_COUNT = 7035

# The candidate (ALG-B) list, frozen 2026-08-02 by the candidate tail census.
# Same adopted rule, different population — see ctc_droplist.json.
CANDIDATE_SHA256 = "81d7ec99ff6602f21ea25b8b4d41241ec24b36150df76fe214dd82b750149971"
CANDIDATE_COUNT = 9501

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
    # drop_unlistenable pinned off unless a test says otherwise: this file
    # tests the no-release rule in isolation, and the ULF- filter (which
    # supersedes it without reversing it) refuses synthetic populations its
    # census never saw. Its own tests: test_pipeline_unlistenable_drop.py.
    overrides.setdefault("drop_unlistenable", False)
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
    mbids = load_drop_mbids(PRODUCTION_ALGORITHM)
    assert len(mbids) == RECORDED_COUNT
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    assert digest == RECORDED_SHA256
    assert DROP_LIST_SHA256 == RECORDED_SHA256


# --- one list per archive ------------------------------------------------
#
# The builder reads whichever archive it is handed and, until this was wired,
# applied the 2026-08-01 production list to it unconditionally. The two lists
# are not near-copies: of production's 7,035 MBIDs only 2,712 appear in the
# candidate's 9,501. Applying today's list to an ALG-B build would therefore
# drop 4,323 artists the candidate rule keeps and miss 6,789 it drops — the
# exact cross-archive asymmetry the drop rule exists to remove, applied
# silently. The selector is `config.algorithm`, which already decides which
# archive sub-tree a build reads (pipeline.py).

# In the production list, absent from the candidate list: must SURVIVE an
# ALG-B build. This is the half-apply canary — it fails if the production
# list leaks into a candidate build.
PROD_ONLY = "0010692c-b17b-408b-aaf6-4e9e35fb9319"
# In the candidate list, absent from the production list: must be dropped
# from an ALG-B build and must SURVIVE a production build.
CANDIDATE_ONLY = "0003890c-83e6-42e2-9b00-9e7797a6c6eb"

CROSS = {
    A: [(B, "Beta", 10)],
    B: [
        (A, "Alpha", 10),
        (C, "Gamma", 5),
        (PROD_ONLY, "ProdOnly", 4),
        (CANDIDATE_ONLY, "CandOnly", 3),
    ],
    C: [(B, "Beta", 5)],
    PROD_ONLY: [(B, "Beta", 4)],
    CANDIDATE_ONLY: [(B, "Beta", 3)],
}

# Any permitted algorithm that is neither of the two censused populations.
UNCENSUSED = next(
    a
    for a in PERMITTED_ALGORITHMS
    if a not in (PRODUCTION_ALGORITHM, CANDIDATE_ALGORITHM)
)


def _scoped_archive(tmp_path, similar, algorithm, subdir):
    """An archive in the sub-tree layout a non-production algorithm writes."""
    source = ListenBrainzSource(BuilderConfig())
    archive = LocalArchive(tmp_path / subdir)
    for mbid, rows in similar.items():
        archive.put(
            f"similar/{source.name}/{algorithm}/{mbid}.json", _similar_body(rows)
        )
    return archive


def test_candidate_archive_uses_the_candidate_list(tmp_path):
    archive = _scoped_archive(tmp_path, CROSS, CANDIDATE_ALGORITHM, "candidate")
    assert CANDIDATE_ONLY not in _build(archive, algorithm=CANDIDATE_ALGORITHM).mbids


def test_production_list_does_not_leak_into_a_candidate_build(tmp_path):
    # The half-apply hazard itself. PROD_ONLY is dropped by today's list and
    # kept by the candidate rule, so its survival is what distinguishes
    # "selected the right list" from "applied the only list there was".
    archive = _scoped_archive(tmp_path, CROSS, CANDIDATE_ALGORITHM, "candidate")
    assert PROD_ONLY in _build(archive, algorithm=CANDIDATE_ALGORITHM).mbids


def test_candidate_list_does_not_leak_into_a_production_build(tmp_path):
    # The mirror image, so the test cannot pass by applying both lists.
    archive = _archive(tmp_path, CROSS, "production")
    built = _build(archive).mbids
    assert CANDIDATE_ONLY in built
    assert PROD_ONLY not in built


def test_an_uncensused_archive_refuses_to_build(tmp_path):
    # Refuse rather than half-apply: no list has been censused for this
    # population, and silently applying another one is the defect.
    archive = _scoped_archive(tmp_path, CROSS, UNCENSUSED, "uncensused")
    with pytest.raises(NoDropListForAlgorithm):
        _build(archive, algorithm=UNCENSUSED)


def test_an_uncensused_archive_builds_with_the_drop_off(tmp_path):
    # The refusal is conditional on the drop being on. Era-pinned probes
    # (grt_score.py, calibrate.py) build uncensused populations with the flag
    # off deliberately, and must keep working. Since 2026-08-03 that means
    # BOTH drops off — the featured-credit filter refuses on uncensused
    # populations by the same rule, and the era-pinned probes pin both flags.
    # Since 2026-08-05 (ULF-) it means all THREE.
    archive = _scoped_archive(tmp_path, CROSS, UNCENSUSED, "uncensused")
    built = _build(
        archive,
        algorithm=UNCENSUSED,
        drop_no_release_tail=False,
        drop_featured_credit=False,
        drop_unlistenable=False,
    ).mbids
    assert PROD_ONLY in built
    assert CANDIDATE_ONLY in built


def test_shipped_candidate_list_matches_the_frozen_snapshot():
    mbids = load_drop_mbids(CANDIDATE_ALGORITHM)
    assert len(mbids) == CANDIDATE_COUNT
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    assert digest == CANDIDATE_SHA256


def test_the_two_lists_are_not_interchangeable():
    # If these ever coincided, every test above would pass vacuously.
    production = load_drop_mbids(PRODUCTION_ALGORITHM)
    candidate = load_drop_mbids(CANDIDATE_ALGORITHM)
    assert production != candidate
    assert PROD_ONLY in production and PROD_ONLY not in candidate
    assert CANDIDATE_ONLY in candidate and CANDIDATE_ONLY not in production
