"""`CRE-T8`'s properties: the two decision rules the Stage 2 entry gates turn on.

Both rules are **imported**, never restated. The closeout B3 check found
`test_cre_screen` guarding a local copy of `CRE-C6`'s predicate — flipping the
module's `>` to `>=` left the suite green, because the assertion was live and
merely attached to the wrong expression. A test that restates its rule passes
forever while the code drifts, and driving assertions red does not catch it.

The gates' *runs* are not unit-tested: they need the built cells, which are
gitignored and minutes to rebuild. What is tested here is the part that decides
PASS from FAIL, which is where a silent wrong answer would come from.
"""
from __future__ import annotations

from cre_gates import G2A_BAR, g2a_passes, journeys_identical


# --- CRE-G1(a): node sequence AND stop kind ------------------------------


def test_identical_path_and_kind_is_identical():
    assert journeys_identical(([1, 2, 3], "natural"), ([1, 2, 3], "natural"))


def test_a_different_node_sequence_is_not_identical():
    assert not journeys_identical(([1, 2, 3], "natural"), ([1, 4, 3], "natural"))


def test_the_same_path_reached_a_different_way_is_not_identical():
    """The half a path-only comparison would miss.

    `forced` and `natural` can return the same nodes: production inserts a stop by
    re-searching with the direct edge forbidden, and the detour it finds may be the
    path an unforced search would have found anyway. The stop kind is the only
    thing that distinguishes them, and the frontend cannot re-derive it
    (`pathfinding.py`), so it is part of the identity bar rather than metadata.
    """
    assert not journeys_identical(([1, 2, 3], "forced"), ([1, 2, 3], "natural"))


def test_both_spellings_of_no_path_agree():
    """Production returns `None`; the mirror returns `(None, "none")`. Same
    outcome, and a naive comparison would call it a divergence on every
    infeasible pair."""
    assert journeys_identical((None, "none"), None)


def test_no_path_against_a_real_path_is_a_divergence():
    assert not journeys_identical((None, "none"), ([1, 2, 3], "natural"))
    assert not journeys_identical(([1, 2, 3], "natural"), None)


# --- CRE-G2(a): >= half of readable journeys change at d1 ----------------


def test_exactly_half_passes():
    """`>=` is the prereg's effect size ("at least half"), so the knife edge is a
    pass. This is the assertion that fails if the module's `>=` becomes `>`."""
    assert g2a_passes(11, 22)


def test_just_below_half_fails():
    assert not g2a_passes(10, 22)


def test_everything_changing_passes():
    assert g2a_passes(22, 22)


def test_nothing_changing_fails():
    assert not g2a_passes(0, 22)


def test_no_readable_pair_is_a_dead_wire_not_a_pass():
    """The vacuity case, and the one worth having a test for: with no readable
    pair there is no evidence the device fires at all. `0 >= 0.5 * 0` is true, so
    the natural expression returns PASS on an empty run unless the denominator is
    guarded — a gate that passes when it measured nothing."""
    assert not g2a_passes(0, 0)


def test_the_bar_is_the_pre_registered_one():
    assert G2A_BAR == 0.5
