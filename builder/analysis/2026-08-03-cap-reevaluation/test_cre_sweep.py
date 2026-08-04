"""`CRE-T9`/`T10`'s properties: the rules the sweep applies between the ladder and
the committed JSON.

Every rule is **imported**, never restated (the closeout B3 defect). The sweep's
*runs* need the gitignored cells and are not unit-tested; what is tested here is
the reconstruction of the exclusion ladder, the padding/infeasibility
distinction, and pin 3's counter — the three places a wrong number would be
produced silently rather than loudly.
"""
from __future__ import annotations

import pytest

from cre_common import RAMPS
from cre_ladder import victim_key
from cre_sweep import (config_for, ladder_excludes, check_reconstruction,
                       null_interior_unbypassable, split_cell)


# --- cell ids ------------------------------------------------------------


def test_split_cell_handles_a_plain_cell():
    assert split_cell("E-S1-P1a") == ("E-S1", "P1a")


def test_split_cell_handles_a_hyphenated_companion():
    """The companions carry hyphens of their own, so a naive rsplit on '-' takes
    the wrong half and would sweep the real S2 cell under the companion's name."""
    assert split_cell("E-S2-labelscramble-P0") == ("E-S2-labelscramble", "P0")
    assert split_cell("E-S2-votescramble-P0") == ("E-S2-votescramble", "P0")


def test_an_unknown_pricing_is_refused():
    with pytest.raises(SystemExit):
        split_cell("E-S1-P2")


def test_pricing_maps_to_the_pre_registered_ramps():
    assert config_for("P0").w_known_ramp_fame_pctl == 0.0
    assert config_for("P1a").w_known_ramp_fame_pctl == RAMPS["P1a"]
    assert config_for("P1b").w_known_ramp_fame_pctl == RAMPS["P1b"]


def test_pricing_changes_nothing_but_the_device():
    """The one-knob claim §0.2 rests on, asserted rather than trusted."""
    p0, p1 = config_for("P0"), config_for("P1b")
    for f in ("w_sim", "w_jump", "w_floor", "w_hop", "w_avoid", "w_degree_hub",
              "floor_relax_known", "floor_mode", "jump_currency"):
        assert getattr(p0, f) == getattr(p1, f), f"{f} moved with the pricing"


# --- the exclusion ladder ------------------------------------------------


def _key():
    # Highest fame first; here node id doubles as fame so victims are predictable.
    fame = {0: 0.0, 1: 0.1, 2: 0.9, 3: 0.5, 4: 0.2, 5: 0.7}
    pop = {n: 0.5 for n in fame}
    mbids = {n: f"m{n}" for n in fame}
    return victim_key([fame[n] for n in sorted(fame)],
                      [pop[n] for n in sorted(pop)],
                      [mbids[n] for n in sorted(mbids)])


def test_excludes_accumulate_one_victim_per_depth():
    ladder = [([0, 2, 3, 1], "natural"),
              ([0, 5, 3, 1], "natural"),
              ([0, 4, 1], "natural")]
    out = ladder_excludes(ladder, _key())
    assert [len(e) for e in out] == [0, 1, 2]
    # The highest-fame interior is pressed first: node 2 (0.9), then node 5 (0.7).
    assert [e.node for e in out[2]] == [2, 5]


def test_the_ladder_stops_pressing_at_an_infeasible_depth():
    ladder = [([0, 2, 1], "natural"), (None, "none"), (None, "none")]
    out = ladder_excludes(ladder, _key())
    assert len(out) == 2, "walked depths must stop at the infeasible one"


def test_the_ladder_stops_pressing_at_an_interior_less_depth():
    """An `adjacent_only` depth is FEASIBLE but has no victim to press, so the
    walk ends there and everything after it is padding. A scorer that read that
    padding as infeasibility would drop the pair from every compared cell under
    the uniform-drop rule -- the failure §0.3's journey-semantics row exists to
    prevent, arriving by a different route."""
    ladder = [([0, 2, 1], "natural"), ([0, 1], "adjacent_only"), (None, "none")]
    out = ladder_excludes(ladder, _key())
    assert len(out) == 2
    assert [e.node for e in out[1]] == [2]


def test_reconstruction_check_accepts_a_consistent_ladder():
    ladder = [([0, 2, 3, 1], "natural"), ([0, 5, 3, 1], "natural")]
    check_reconstruction(ladder, ladder_excludes(ladder, _key()))


def test_reconstruction_check_fires_when_an_excluded_node_reappears():
    """The tie between the reconstruction and observable output. A hard exclusion
    cannot appear in a later interior, so if it does, the wrong victim was
    reconstructed and every term share attributed after it is wrong."""
    ladder = [([0, 2, 3, 1], "natural"), ([0, 2, 4, 1], "natural")]
    with pytest.raises(SystemExit):
        check_reconstruction(ladder, ladder_excludes(ladder, _key()))


# --- pin 3's mechanical counter ------------------------------------------


def test_nulls_are_unbypassable_while_any_measured_interior_exists():
    assert null_interior_unbypassable([0.9, None, None]) == 2


def test_with_no_measured_interior_exactly_one_null_becomes_the_victim():
    assert null_interior_unbypassable([None, None, None]) == 2


def test_a_single_null_alone_is_bypassable():
    assert null_interior_unbypassable([None]) == 0


def test_all_measured_counts_nothing():
    assert null_interior_unbypassable([0.9, 0.4]) == 0


def test_an_empty_interior_counts_nothing():
    """`adjacent_only` depths reach here; `max(0, -1)` is the guard."""
    assert null_interior_unbypassable([]) == 0
