"""The pre-registered TAS-5 draw -- the properties that must not drift."""

from __future__ import annotations

from tas_pairs import MIN_READABLE_PER_CLASS, SEED, draw_pairs


def test_pairs_carry_their_class_label():
    # CRS-A1: Track B's draw discarded class labels and three pre-registered
    # quantities became uncomputable until it was fixed mid-flight.
    pairs = draw_pairs()
    assert all(len(p) == 3 for p in pairs)
    assert {p[2] for p in pairs} <= {"ff", "fo", "oo"}


def test_draw_is_deterministic_under_the_committed_seed():
    assert draw_pairs() == draw_pairs()


def test_the_seed_is_the_pre_registered_one():
    # td_pathedges.py deliberately used a DIFFERENT seed so it would not consume
    # this draw. Any other value here means TAS-5 did not run on the
    # pre-registered pair set.
    assert SEED == "20260730-tas"


def test_every_class_meets_the_readability_floor_or_is_reported_unreadable():
    pairs = draw_pairs()
    for cls in ("ff", "fo", "oo"):
        n = sum(1 for p in pairs if p[2] == cls)
        assert n >= MIN_READABLE_PER_CLASS or n == 0


def test_no_pair_joins_an_artist_to_itself():
    assert all(a != b for a, b, _ in draw_pairs())


def test_endpoints_are_stored_in_sorted_order():
    # The pair is undirected; storing it lo-hi makes the draw comparable
    # across runs and lets the set deduplicate reversed duplicates.
    assert all(a < b for a, b, _ in draw_pairs())
