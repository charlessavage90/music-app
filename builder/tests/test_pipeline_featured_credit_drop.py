"""The featured-credit filter (FCF- rule, 2026-08-03).

Drop an artist credited on release groups but never as the sole artist, with
no Discogs main-artist release, unless a commercial-DSP link exists AND a clip
resolves. The rule document was committed before the keep-check ran; these
tests apply its frozen output and never re-open it.

Structure mirrors test_pipeline_no_release_drop.py deliberately — same
snapshot mandate (spec §9, offline builder), same before-the-mass-computation
ordering pin, same per-population selection with refusal for uncensused
algorithms, same leak canaries. Two additions are specific to being the
SECOND drop: the uncensused refusal is tested with the no-release drop off
(so this module's own refusal is the one that fires rather than being masked
by the earlier stage's), and the coexistence test pins that both drops apply
in one build.
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
from artistpath_builder.featured_credit_drop import (
    FEATURED_DROP_LIST_SHA256,
    NoFeaturedCreditListForAlgorithm,
    load_featured_credit_drop_mbids,
)
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

# Reproduced from the frozen probe output (fcf_droplist.json):
# sha256 of json.dumps(sorted(drop_mbids), sort_keys=True).
RECORDED_SHA256 = "0f337de2b5c1fcfab64b4efd690826e269206a5db3b8142bb5776af4d9b3655c"
RECORDED_COUNT = 2194

# The candidate (ALG-B) list — same committed rule, different population
# (fcf_droplist_algb_am1.json). The lists share 945 MBIDs. Both lists are
# the FCF-AM1 re-freeze, a strict superset of the pre-amendment lists.
CANDIDATE_SHA256 = "b8d230e6ffc7d0f5789b5dbc05fefb0b564bbddfc2590f478aa21e218fbed6f0"
CANDIDATE_COUNT = 1940

A, B, C = ("a" * 36, "b" * 36, "c" * 36)
# Real MBIDs from the frozen lists: one the rule drops, one it keeps.
DROPPED_FCF = "0005eae3-3fe9-4a71-9f1d-8dff89e899f6"
KEPT_FCF = "00432f55-712d-4aba-bf47-2943e6b1e343"

# A <-> B <-> C is a healthy core. Both class artists hang off B.
SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5), (DROPPED_FCF, "Ghost", 4), (KEPT_FCF, "Keeper", 3)],
    C: [(B, "Beta", 5)],
    DROPPED_FCF: [(B, "Beta", 4)],
    KEPT_FCF: [(B, "Beta", 3)],
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
    # tests the FCF- rule in isolation, and the ULF- filter (which supersedes
    # it without reversing it) refuses synthetic populations its census never
    # saw. Its own tests: test_pipeline_unlistenable_drop.py.
    overrides.setdefault("drop_unlistenable", False)
    config = BuilderConfig(**overrides)
    return build_from_archive(config, archive, ListenBrainzSource(config))


@pytest.fixture
def archive(tmp_path):
    return _archive(tmp_path, SIMILAR)


def test_listed_artist_is_dropped(archive):
    assert DROPPED_FCF not in _build(archive).mbids


def test_class_artist_the_rule_keeps_survives(archive):
    # The keep-check keeps part of the class. A keep-list artist must be
    # untouched — otherwise the wiring implements "drop the class", not the
    # committed rule.
    assert KEPT_FCF in _build(archive).mbids


def test_drop_is_off_when_the_config_flag_is_off(archive):
    # Without this the suite cannot tell the drop from an unrelated prune.
    assert DROPPED_FCF in _build(archive, drop_featured_credit=False).mbids


def test_dropping_equals_never_having_been_archived(tmp_path):
    # Dropped BEFORE the mass computation, so the dropped artist perturbs no
    # surviving artist's marginal: the built graph must be identical to one
    # built from an archive the artist never appeared in.
    without = {
        mbid: [row for row in rows if row[0] != DROPPED_FCF]
        for mbid, rows in SIMILAR.items()
        if mbid != DROPPED_FCF
    }
    dropped = _build(_archive(tmp_path, SIMILAR, "with"))
    absent = _build(_archive(tmp_path, without, "without"))

    assert dropped.mbids == absent.mbids
    assert dropped.pop_raw == absent.pop_raw
    assert dropped.offsets.tolist() == absent.offsets.tolist()
    assert dropped.neighbours.tolist() == absent.neighbours.tolist()
    assert dropped.scores.tolist() == absent.scores.tolist()


def test_shipped_list_matches_the_frozen_snapshot():
    mbids = load_featured_credit_drop_mbids(PRODUCTION_ALGORITHM)
    assert len(mbids) == RECORDED_COUNT
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    assert digest == RECORDED_SHA256
    assert FEATURED_DROP_LIST_SHA256 == RECORDED_SHA256


# --- one list per archive ------------------------------------------------
#
# Same defect class as no_release_drop.py's: the lists are the rule evaluated
# against a specific crawl, so borrowing across populations silently drops
# artists the rule keeps there and keeps artists it drops.

# In the production list, absent from the candidate list: must SURVIVE an
# ALG-B build. The half-apply canary.
PROD_ONLY_FCF = "0007d97f-a943-475c-bb2d-f672d44ab24b"
# In the candidate list, absent from the production list.
CANDIDATE_ONLY_FCF = "00f7467f-462e-408c-8d57-ac10f33d8139"

CROSS = {
    A: [(B, "Beta", 10)],
    B: [
        (A, "Alpha", 10),
        (C, "Gamma", 5),
        (PROD_ONLY_FCF, "ProdOnly", 4),
        (CANDIDATE_ONLY_FCF, "CandOnly", 3),
    ],
    C: [(B, "Beta", 5)],
    PROD_ONLY_FCF: [(B, "Beta", 4)],
    CANDIDATE_ONLY_FCF: [(B, "Beta", 3)],
}

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
    assert (
        CANDIDATE_ONLY_FCF
        not in _build(archive, algorithm=CANDIDATE_ALGORITHM).mbids
    )


def test_production_list_does_not_leak_into_a_candidate_build(tmp_path):
    archive = _scoped_archive(tmp_path, CROSS, CANDIDATE_ALGORITHM, "candidate")
    assert PROD_ONLY_FCF in _build(archive, algorithm=CANDIDATE_ALGORITHM).mbids


def test_candidate_list_does_not_leak_into_a_production_build(tmp_path):
    # The mirror image, so the test cannot pass by applying both lists.
    archive = _archive(tmp_path, CROSS, "production")
    built = _build(archive).mbids
    assert CANDIDATE_ONLY_FCF in built
    assert PROD_ONLY_FCF not in built


def test_an_uncensused_archive_refuses_to_build(tmp_path):
    # With the no-release drop off, so the refusal that fires is THIS
    # module's own rather than the earlier stage's — otherwise this test
    # would pass with the featured-credit wiring deleted entirely.
    archive = _scoped_archive(tmp_path, CROSS, UNCENSUSED, "uncensused")
    with pytest.raises(NoFeaturedCreditListForAlgorithm):
        _build(archive, algorithm=UNCENSUSED, drop_no_release_tail=False)


def test_an_uncensused_archive_builds_with_both_drops_off(tmp_path):
    # The refusal is conditional on the flag. Era-pinned probes (grt_score.py,
    # calibrate.py) build uncensused populations with BOTH flags off.
    archive = _scoped_archive(tmp_path, CROSS, UNCENSUSED, "uncensused")
    built = _build(
        archive,
        algorithm=UNCENSUSED,
        drop_no_release_tail=False,
        drop_featured_credit=False,
    ).mbids
    assert PROD_ONLY_FCF in built
    assert CANDIDATE_ONLY_FCF in built


def test_shipped_candidate_list_matches_the_frozen_snapshot():
    mbids = load_featured_credit_drop_mbids(CANDIDATE_ALGORITHM)
    assert len(mbids) == CANDIDATE_COUNT
    digest = sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()
    assert digest == CANDIDATE_SHA256


def test_the_two_lists_are_not_interchangeable():
    # If these ever coincided, every test above would pass vacuously.
    production = load_featured_credit_drop_mbids(PRODUCTION_ALGORITHM)
    candidate = load_featured_credit_drop_mbids(CANDIDATE_ALGORITHM)
    assert production != candidate
    assert PROD_ONLY_FCF in production and PROD_ONLY_FCF not in candidate
    assert CANDIDATE_ONLY_FCF in candidate and CANDIDATE_ONLY_FCF not in production


def test_both_drops_apply_in_one_build(tmp_path):
    # The two rules are disjoint by construction (census-verified), and a
    # production build with defaults applies both lists. NO_RELEASE_DROPPED
    # is from the other rule's frozen list.
    NO_RELEASE_DROPPED = "000cf466-9147-4377-8b8a-84bb576b5813"
    both = {
        A: [(B, "Beta", 10)],
        B: [
            (A, "Alpha", 10),
            (C, "Gamma", 5),
            (NO_RELEASE_DROPPED, "Ghost1", 4),
            (DROPPED_FCF, "Ghost2", 3),
        ],
        C: [(B, "Beta", 5)],
        NO_RELEASE_DROPPED: [(B, "Beta", 4)],
        DROPPED_FCF: [(B, "Beta", 3)],
    }
    built = _build(_archive(tmp_path, both, "both")).mbids
    assert NO_RELEASE_DROPPED not in built
    assert DROPPED_FCF not in built
