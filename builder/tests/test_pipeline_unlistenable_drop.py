"""The un-listenable filter (`ULF-`, spec 2026-08-05).

Drop an artist with no sole-credited substantial release group (`ULC-D2`)
unless a commercial-DSP link exists AND a clip resolves. One rule superseding
both earlier drops without reversing either — their classes are strict subsets
and their frozen verdicts carry. Rule document:
docs/superpowers/specs/2026-08-05-unlistenable-filter-rule.md.

Two properties are NEW against the sibling drop tests, and they are the
`ULC-F1` acceptance tests:

- the frozen payload carries the CENSUSED POPULATION (the archive's artist
  set at census time), not just the drops;
- a build whose archive contains artists outside that set REFUSES, exactly as
  an uncensused algorithm already does. Extend the crawl without re-censusing
  and the build fails loudly instead of silently under-filtering — which is
  the defect `no_release_drop.py`'s algorithm-only key could not see.

These tests run against tmp-path payloads because the real lists do not exist
until the `ULF-` census freezes them; the snapshot-pinning tests join this
file when they do.
"""

import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import (
    CANDIDATE_ALGORITHM,
    PERMITTED_ALGORITHMS,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource
from artistpath_builder.unlistenable_drop import (
    NoUnlistenableListForAlgorithm,
    PopulationNotCensused,
    load_unlistenable_list,
)

A, B, C = ("a" * 36, "b" * 36, "c" * 36)
DROPPED = "d" * 36
KEPT = "e" * 36

# A <-> B <-> C is a healthy core; the two class members hang off B.
SIMILAR = {
    A: [(B, "Beta", 10)],
    B: [(A, "Alpha", 10), (C, "Gamma", 5), (DROPPED, "Ghost", 4), (KEPT, "Keeper", 3)],
    C: [(B, "Beta", 5)],
    DROPPED: [(B, "Beta", 4)],
    KEPT: [(B, "Beta", 3)],
}

UNCENSUSED = next(
    a
    for a in PERMITTED_ALGORITHMS
    if a not in (PRODUCTION_ALGORITHM, CANDIDATE_ALGORITHM)
)


def _similar_body(rows) -> bytes:
    return json.dumps(
        [
            {"artist_mbid": n, "name": name, "comment": "", "score": score}
            for n, name, score in rows
        ]
    ).encode()


def _archive(tmp_path, similar, algorithm=PRODUCTION_ALGORITHM, subdir="archive"):
    source = ListenBrainzSource(BuilderConfig())
    archive = LocalArchive(tmp_path / subdir)
    scope = "" if algorithm == PRODUCTION_ALGORITHM else f"{algorithm}/"
    for mbid, rows in similar.items():
        archive.put(f"similar/{source.name}/{scope}{mbid}.json", _similar_body(rows))
    return archive


def _build(archive, **overrides):
    # require_fame pinned off unless a test says otherwise: the MSW- adoption
    # (2026-08-06) turned it on by default, and this file's synthetic archives
    # have no fame stage. The ULF- drop is the subject here; the fame default
    # is exercised in test_pipeline_fame.py (factor-table-control idiom).
    overrides.setdefault("require_fame", False)
    config = BuilderConfig(**overrides)
    return build_from_archive(config, archive, ListenBrainzSource(config))


# The list installer lives in conftest.py (install_ulf_list) because test_cli
# builds through `main` and needs the same machinery; this file aliases it.
@pytest.fixture
def install_list(install_ulf_list):
    return install_ulf_list


FULL_POPULATION = set(SIMILAR)


def test_listed_artist_is_dropped(tmp_path, install_list):
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, keep={KEPT})
    archive = _archive(tmp_path, SIMILAR)
    assert DROPPED not in _build(archive).mbids


def test_class_member_the_keep_check_rescued_survives(tmp_path, install_list):
    # A keep-list artist must be untouched — otherwise the wiring implements
    # "drop the class", not the rule (class minus keep-check rescues).
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, keep={KEPT})
    archive = _archive(tmp_path, SIMILAR)
    assert KEPT in _build(archive).mbids


def test_drop_is_off_when_the_config_flag_is_off(tmp_path, install_list):
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED})
    archive = _archive(tmp_path, SIMILAR)
    assert DROPPED in _build(archive, drop_unlistenable=False).mbids


def test_an_archive_with_uncensused_artists_refuses_to_build(
    tmp_path, install_list
):
    # ULC-F1 itself. The census never saw C — the shape of a crawl extension —
    # so the lookup succeeding by algorithm alone is exactly the silent
    # under-filtering this refusal exists to remove.
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION - {C}, {DROPPED})
    archive = _archive(tmp_path, SIMILAR)
    with pytest.raises(PopulationNotCensused):
        _build(archive)


def test_the_refusal_names_the_uncensused_count(tmp_path, install_list):
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION - {C}, {DROPPED})
    archive = _archive(tmp_path, SIMILAR)
    with pytest.raises(PopulationNotCensused, match="1 artist"):
        _build(archive)


def test_a_shrunken_archive_still_builds(tmp_path, install_list):
    # Subset is fine: every present artist was evaluated. Refusal is owed only
    # to artists the census never saw.
    install_list(
        PRODUCTION_ALGORITHM, FULL_POPULATION | {"f" * 36}, {DROPPED}
    )
    archive = _archive(tmp_path, SIMILAR)
    assert DROPPED not in _build(archive).mbids


def test_population_mismatch_builds_with_the_drop_off(tmp_path, install_list):
    # The probe escape, same as the sibling rules: the refusal is conditional
    # on the drop being on.
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION - {C}, {DROPPED})
    archive = _archive(tmp_path, SIMILAR)
    assert DROPPED in _build(archive, drop_unlistenable=False).mbids


def test_an_uncensused_algorithm_refuses_to_build(tmp_path):
    archive = _archive(tmp_path, SIMILAR, algorithm=UNCENSUSED, subdir="scoped")
    with pytest.raises(NoUnlistenableListForAlgorithm):
        _build(
            archive,
            algorithm=UNCENSUSED,
            drop_no_release_tail=False,
            drop_featured_credit=False,
        )


def test_an_uncensused_algorithm_builds_with_the_drop_off(tmp_path):
    archive = _archive(tmp_path, SIMILAR, algorithm=UNCENSUSED, subdir="scoped")
    built = _build(
        archive,
        algorithm=UNCENSUSED,
        drop_no_release_tail=False,
        drop_featured_credit=False,
        drop_unlistenable=False,
    ).mbids
    assert DROPPED in built


# --- the per-invocation payload override (SEL-, 2026-08-09) ----------------
# The case these exist for is the one the registry cannot name: an algorithm
# whose archive has been EXTENDED, so one algorithm now means two populations.


def test_override_builds_a_population_the_registry_cannot_express(
    tmp_path, install_list
):
    # The registry's list predates a crawl extension and would refuse (it is
    # the ULC-F1 case above). The override censuses the grown archive, so the
    # build proceeds — and actually applies the overriding list's verdicts.
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION - {C}, set())
    extended = install_list(
        PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, register=False
    )
    archive = _archive(tmp_path, SIMILAR)
    built = _build(archive, unlistenable_list_path=extended).mbids
    assert DROPPED not in built, "the override's drop verdict was not applied"
    assert C in built


def test_override_does_not_bypass_the_population_check(tmp_path, install_list):
    # The override selects WHICH payload, never whether ULC-F1 is enforced. A
    # payload that does not cover the archive must still refuse, or the flag
    # would be a way to silently switch the guard off.
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION, set())
    short = install_list(
        PRODUCTION_ALGORITHM, FULL_POPULATION - {C}, set(), register=False
    )
    archive = _archive(tmp_path, SIMILAR)
    with pytest.raises(PopulationNotCensused):
        _build(archive, unlistenable_list_path=short)


def test_override_bypasses_the_lookup_rather_than_substituting_in_it(
    tmp_path, install_list
):
    # UNCENSUSED has no registry entry at all, so a substitution-in-the-dict
    # implementation would still raise NoUnlistenableListForAlgorithm here.
    # Building proves the lookup is bypassed, which is what lets a first-time
    # census be built without editing unlistenable_drop.py.
    payload = install_list(
        UNCENSUSED, FULL_POPULATION, {DROPPED}, register=False
    )
    archive = _archive(tmp_path, SIMILAR, algorithm=UNCENSUSED, subdir="scoped")
    built = _build(
        archive,
        algorithm=UNCENSUSED,
        drop_no_release_tail=False,
        drop_featured_credit=False,
        unlistenable_list_path=payload,
    ).mbids
    assert DROPPED not in built


def test_dropping_equals_never_having_been_archived(tmp_path, install_list):
    # Dropped BEFORE the mass computation, same invariant as the sibling
    # drops: the built graph must equal one from an archive the artist never
    # appeared in, not the old graph minus rows.
    install_list(PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, keep={KEPT})
    without = {
        mbid: [row for row in rows if row[0] != DROPPED]
        for mbid, rows in SIMILAR.items()
        if mbid != DROPPED
    }
    dropped = _build(_archive(tmp_path, SIMILAR, subdir="with"))
    absent = _build(_archive(tmp_path, without, subdir="without"))

    assert dropped.mbids == absent.mbids
    assert dropped.pop_raw == absent.pop_raw
    assert dropped.offsets.tolist() == absent.offsets.tolist()
    assert dropped.neighbours.tolist() == absent.neighbours.tolist()
    assert dropped.scores.tolist() == absent.scores.tolist()


def test_a_payload_whose_population_hash_disagrees_refuses_to_load(
    tmp_path, install_list
):
    # The identity block is what F1 rests on; a payload that disagrees with
    # itself (hand-edited, truncated, wrongly regenerated) must not be trusted
    # for a refusal decision any more than for a drop decision.
    def corrupt(payload):
        payload["population"]["mbids"] = payload["population"]["mbids"][:-1]

    install_list(
        PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, mutate=corrupt
    )
    with pytest.raises(ValueError, match="identity"):
        load_unlistenable_list(PRODUCTION_ALGORITHM)


def test_a_drop_outside_the_censused_population_refuses_to_load(
    tmp_path, install_list
):
    # drop_mbids ⊆ censused population, structurally: a drop the census never
    # evaluated is a contradiction in the payload, not a bigger list.
    def leak(payload):
        payload["drop_mbids"] = sorted(set(payload["drop_mbids"]) | {"z" * 36})

    install_list(
        PRODUCTION_ALGORITHM, FULL_POPULATION, {DROPPED}, mutate=leak
    )
    with pytest.raises(ValueError, match="outside"):
        load_unlistenable_list(PRODUCTION_ALGORITHM)


# --- the frozen shipped snapshots ---------------------------------------
#
# Counts and shas from the census's own payloads (ulf_droplist.py output),
# recorded in the ULF- execution log. Same pinning idiom as the sibling
# rules' snapshot tests.
#
# ⚠ These pin whatever UNLISTENABLE_DROP_LISTS resolves to, so they move with
# a repoint — they are not free-standing history. The CANDIDATE three moved
# together at `CXA-` Task 2 (2026-08-10) when the shipped ALG-B default went
# from the 75,000-artist payload to the re-censused 117,302-artist one; the
# PRODUCTION (ALG-E) three are untouched and must stay so, because the
# regenerated ALG-E payload is a by-product that must not ship
# (analysis/2026-08-09-cex-recensus/README.md).
#
# PREVIOUS (75k-era ALG-B): CANDIDATE_COUNT 15_708, CANDIDATE_POPULATION 75_000

from artistpath_builder.unlistenable_drop import (  # noqa: E402
    CANDIDATE_UNLISTENABLE_DROP_SHA256,
    UNLISTENABLE_DROP_SHA256,
)

RECORDED_COUNT = 13_355
RECORDED_POPULATION = 75_000
# REPOINTED BACK 2026-09-05 (`L4-T1`): the CXA- revert cleanup returned the
# ALG-B default to the 75k-era payload the SERVED map was built with.
# PREVIOUS (117k-era ALG-B): CANDIDATE_COUNT 27_262, CANDIDATE_POPULATION 117_302
CANDIDATE_COUNT = 15_708
CANDIDATE_POPULATION = 75_000


@pytest.fixture
def real_lists():
    # The install_list fixture monkeypatches the registry and clears the
    # cache; these tests want the SHIPPED payloads, so clear both ways.
    load_unlistenable_list.cache_clear()
    yield
    load_unlistenable_list.cache_clear()


def test_shipped_list_matches_the_frozen_snapshot(real_lists):
    from hashlib import sha256

    lst = load_unlistenable_list(PRODUCTION_ALGORITHM)
    assert len(lst.drop_mbids) == RECORDED_COUNT
    assert len(lst.censused_mbids) == RECORDED_POPULATION
    digest = sha256(
        json.dumps(sorted(lst.drop_mbids), sort_keys=True).encode()
    ).hexdigest()
    assert digest == UNLISTENABLE_DROP_SHA256


def test_shipped_candidate_list_matches_the_frozen_snapshot(real_lists):
    from hashlib import sha256

    lst = load_unlistenable_list(CANDIDATE_ALGORITHM)
    assert len(lst.drop_mbids) == CANDIDATE_COUNT
    assert len(lst.censused_mbids) == CANDIDATE_POPULATION
    digest = sha256(
        json.dumps(sorted(lst.drop_mbids), sort_keys=True).encode()
    ).hexdigest()
    assert digest == CANDIDATE_UNLISTENABLE_DROP_SHA256


def test_the_two_lists_are_not_interchangeable(real_lists):
    # If these ever coincided, the per-population selection tests would pass
    # vacuously — same guard as the sibling rules carry.
    production = load_unlistenable_list(PRODUCTION_ALGORITHM)
    candidate = load_unlistenable_list(CANDIDATE_ALGORITHM)
    assert production.drop_mbids != candidate.drop_mbids
    assert production.censused_mbids != candidate.censused_mbids


def test_the_shipped_lists_carry_the_prior_drops_forward(real_lists):
    # ULF-3, supersession without reversal, checked on the shipped data:
    # every artist the two adopted rules drop — where present in the ULF-
    # censused population — is dropped by the merged list too.
    from artistpath_builder.featured_credit_drop import (
        load_featured_credit_drop_mbids,
    )
    from artistpath_builder.no_release_drop import load_drop_mbids

    for algorithm in (PRODUCTION_ALGORITHM, CANDIDATE_ALGORITHM):
        ulf = load_unlistenable_list(algorithm)
        prior = load_drop_mbids(algorithm) | load_featured_credit_drop_mbids(
            algorithm
        )
        assert (prior & ulf.censused_mbids) <= ulf.drop_mbids
