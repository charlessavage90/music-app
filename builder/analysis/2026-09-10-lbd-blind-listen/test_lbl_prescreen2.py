"""The pre-screen's pure parts: the pool exclusions, the draw's two bans, the gates, the ranking.

Every function here is exercised without a map. The gates' behaviour over a real APG1 artifact is
already covered by `test_lbl_generate.py`, which tests the `ladder` and `press_key` this reuses.
"""
import pytest

from lbl_prescreen2 import (
    MAPS,
    MIN_DIFFERING_DEPTHS,
    MIN_INTERIOR,
    draw,
    familiarity,
    familiarity_mbids,
    pool_records,
    rank_key,
    screen,
)

ALL = {"served", "A0V", "A5V"}


def nodes(present=ALL, mbids=("m1", "m2", "m3", "m4", "m5")):
    return {k: (set(mbids) if k in present else set()) for k in ALL}


def usable(*names_mbids):
    return {"usable": [{"name": n, "ms_played": 60_000, "status": "ok",
                        "v0_nodes": [{"mbid": m}], "g_nodes": [{"mbid": m}]}
                       for n, m in names_mbids]}


# --- pool ---------------------------------------------------------------------------------------

def test_an_export_artist_with_no_exclusion_is_eligible():
    recs = pool_records(usable(("A", "m1")), set(), set(), nodes())
    assert recs[0]["name"] == "A" and "excluded" not in recs[0] and recs[0]["rank"] == 1


def test_a_gbl_am1_endpoint_is_excluded_before_anything_else_is_checked():
    recs = pool_records(usable(("A", "m1")), {"m1"}, {"m1"}, nodes(present={"served"}))
    assert recs[0]["excluded"] == "GBL-AM1 endpoint"


def test_a_listen_one_primary_endpoint_is_excluded_at_artist_level():
    recs = pool_records(usable(("A", "m1")), set(), {"m1"}, nodes())
    assert recs[0]["excluded"] == "listen-1 primary endpoint (D1)"


def test_an_artist_missing_from_one_listen_two_map_is_excluded():
    n = nodes()
    n["A5V"] = set()
    recs = pool_records(usable(("A", "m1")), set(), set(), n)
    assert recs[0]["excluded"] == "not a node of both listen-2 maps (D3)"


def test_an_artist_missing_from_the_served_map_is_excluded_because_clips_need_it():
    n = nodes()
    n["served"] = set()
    recs = pool_records(usable(("A", "m1")), set(), set(), n)
    assert recs[0]["excluded"] == "not a node of the served map"


def test_an_artist_that_did_not_resolve_to_one_mbid_in_both_gbl_maps_is_excluded():
    cand = {"usable": [{"name": "A", "ms_played": 1, "status": "ok",
                        "v0_nodes": [{"mbid": "m1"}, {"mbid": "m2"}], "g_nodes": [{"mbid": "m1"}]}]}
    recs = pool_records(cand, set(), set(), nodes())
    assert recs[0]["excluded"] == "not one MBID in both GBL- maps"


# --- draw ---------------------------------------------------------------------------------------

def rec(mbid, name=None, rank=1):
    return {"mbid": mbid, "name": name or mbid.upper(), "rank": rank}


def test_the_draw_pairs_greedily_in_pool_order():
    pairs = draw([rec("m1"), rec("m2"), rec("m3"), rec("m4")], lambda a, b: False, set())
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m2"), ("m3", "m4")]


def test_an_adjacent_candidate_waits_for_the_next_non_adjacent_one():
    adjacent = lambda a, b: {a, b} == {"m1", "m2"}  # noqa: E731
    pairs = draw([rec("m1"), rec("m2"), rec("m3")], adjacent, set())
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m3")]


def test_adjacency_in_either_map_is_enough_to_skip():
    """`adjacent_in_either` is the caller's disjunction; the draw must honour a single True."""
    pairs = draw([rec("m1"), rec("m2")], lambda a, b: True, set())
    assert pairs == []


def test_a_listen_one_reserve_pair_is_banned_but_both_artists_stay_usable():
    banned = {frozenset(("m1", "m2"))}
    pairs = draw([rec("m1"), rec("m2"), rec("m3")], lambda a, b: False, banned)
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m3")]


def test_the_ban_is_recorded_on_the_record_that_was_turned_away():
    banned = {frozenset(("m1", "m2"))}
    eligible = [rec("m1"), rec("m2"), rec("m3")]
    draw(eligible, lambda a, b: False, banned)
    assert eligible[1]["skipped_as_listen1_reserve_with"] == ["M1"]


# --- the gates ----------------------------------------------------------------------------------

def per_map(a_interiors, b_interiors):
    """`{map: {depth: [mbid, ...]}}` from two dicts keyed by depth."""
    return {MAPS[0]: a_interiors, MAPS[1]: b_interiors}


def long_enough(*sets):
    """One interior list per depth, each at the minimum length, from the given first letters."""
    return {d: [f"{letter}{i}" for i in range(MIN_INTERIOR)] for d, letter in zip((0, 10, 20), sets)}


def test_a_pair_differing_at_every_depth_and_long_enough_is_kept():
    reason, detail = screen(per_map(long_enough("a", "b", "c"), long_enough("x", "y", "z")))
    assert reason is None and detail["differing_depths"] == 3


def test_a_pair_that_agrees_everywhere_is_rejected():
    same = long_enough("a", "b", "c")
    reason, detail = screen(per_map(same, dict(same)))
    assert reason is not None and "differ at fewer than" in reason and detail["differing_depths"] == 0


def test_one_differing_depth_is_not_enough():
    a = long_enough("a", "b", "c")
    b = dict(a)
    b[20] = [f"z{i}" for i in range(MIN_INTERIOR)]
    reason, detail = screen(per_map(a, b))
    assert detail["differing_depths"] == 1 < MIN_DIFFERING_DEPTHS and reason is not None


def test_a_short_interior_on_one_map_at_one_depth_is_rejected():
    a = long_enough("a", "b", "c")
    b = long_enough("x", "y", "z")
    b[10] = b[10][: MIN_INTERIOR - 1]
    reason, _ = screen(per_map(a, b))
    assert reason == f"a map has fewer than {MIN_INTERIOR} interior artists at some depth"


def test_a_depth_a_map_cannot_reach_is_rejected_and_named():
    a = long_enough("a", "b", "c")
    b = long_enough("x", "y", "z")
    del b[20]
    reason, detail = screen(per_map(a, b))
    assert reason == "a map does not reach d20 with an interior artist"
    assert detail["depths_reached"][MAPS[1]] == [0, 10]


def test_the_length_gate_is_checked_before_the_difference_gate():
    """A pair that is both short and identical must report the length, the fixable property."""
    short = {d: ["only"] for d in (0, 10, 20)}
    reason, _ = screen(per_map(short, dict(short)))
    assert "interior artists" in reason


# --- familiarity and ranking --------------------------------------------------------------------

def test_familiar_interiors_are_counted_once_across_maps_and_depths():
    a = {0: ["k1", "u1"], 10: ["k1", "u2"], 20: ["u3", "u4"]}
    b = {0: ["k1"], 10: ["k2"], 20: ["u1"]}
    f = familiarity(per_map(a, b), {"k1", "k2", "k9"})
    # union is k1, u1, u2, u3, u4, k2 — six, counted once each however often they recur
    assert f["distinct_interior"] == 6 and f["familiar_interior"] == 2
    assert f["familiar_fraction"] == round(2 / 6, 4)


def test_familiarity_of_an_empty_screen_does_not_divide_by_zero():
    assert familiarity(per_map({}, {}), {"k1"}) == {"distinct_interior": 0, "familiar_interior": 0,
                                                   "familiar_fraction": 0.0}


def test_the_familiarity_set_takes_ambiguous_artists_as_familiar_too():
    cand = {"usable": [{"v0_nodes": [{"mbid": "m1"}], "g_nodes": [{"mbid": "m1"}]}],
            "ambiguous": [{"v0_nodes": [{"mbid": "m2"}, {"mbid": "m3"}], "g_nodes": []}],
            "missing": [{"name": "no mbid at all"}]}
    assert familiarity_mbids(cand) == {"m1", "m2", "m3"}


def test_fewest_familiar_interiors_ranks_first():
    rows = [{"a": rec("m9", rank=1), "b": rec("m8", rank=1), "familiarity": {"familiar_interior": 4, "familiar_fraction": 0.4}},
            {"a": rec("m1", rank=9), "b": rec("m2", rank=9), "familiarity": {"familiar_interior": 1, "familiar_fraction": 0.1}}]
    assert [r["a"]["mbid"] for r in sorted(rows, key=rank_key)] == ["m1", "m9"]


def test_ties_break_on_fraction_then_pool_rank_then_mbid():
    same = {"familiar_interior": 2, "familiar_fraction": 0.2}
    rows = [{"a": rec("mb", rank=5), "b": rec("x", rank=5), "familiarity": same},
            {"a": rec("ma", rank=5), "b": rec("x", rank=5), "familiarity": same},
            {"a": rec("mc", rank=1), "b": rec("x", rank=1), "familiarity": same}]
    assert [r["a"]["mbid"] for r in sorted(rows, key=rank_key)] == ["mc", "ma", "mb"]


def test_the_rank_key_is_total_so_the_order_is_reproducible():
    rows = [{"a": rec("ma", rank=1), "b": rec("x", rank=1),
             "familiarity": {"familiar_interior": 1, "familiar_fraction": 0.1}}]
    assert rank_key(rows[0]) == (1, 0.1, 2, "ma")


def test_maps_tuple_names_exactly_the_two_listen_two_maps():
    """A third map, or the served map, appearing here would mean the screen is not the comparison."""
    assert MAPS == ("A0V", "A5V")


@pytest.mark.parametrize("bad", [{}, {MAPS[0]: {}}])
def test_screen_refuses_rather_than_silently_keeping_an_empty_result(bad):
    reason, _ = screen(bad)
    assert reason is not None


# --- the bars themselves, pinned independently of the constants that set them -------------------
# `long_enough` above builds its fixtures FROM `MIN_INTERIOR`, so every test using it moves with the
# constant and passes at any value — it tests the mechanism, never the bar. Found by the closeout
# mutation check on 2026-09-12: setting MIN_INTERIOR to 1 left the whole file green.

def test_the_two_bars_are_the_values_lbd_am6_fixed():
    assert MIN_INTERIOR == 3, "findings note §4.1: three interior artists at every depth"
    assert MIN_DIFFERING_DEPTHS == 2, "two of the three depths must differ"


def test_two_interior_artists_are_rejected_whatever_the_constant_happens_to_be():
    """A literal fixture, so this goes red if the bar is ever lowered without the amendment."""
    two = {d: ["x", "y"] for d in (0, 10, 20)}
    other = {d: ["p", "q"] for d in (0, 10, 20)}
    reason, _ = screen(per_map(two, other))
    assert reason is not None and "interior artists" in reason


def test_three_interior_artists_are_accepted():
    three = {d: ["x", "y", "z"] for d in (0, 10, 20)}
    other = {d: ["p", "q", "r"] for d in (0, 10, 20)}
    assert screen(per_map(three, other))[0] is None


def test_the_screen_and_the_generation_gate_use_the_SAME_bar():
    """Pairs are SELECTED at the pre-screen's bar and GATED at the harness's. If the two ever
    diverge, a pair chosen as long enough is rejected at generation, or worse, admitted short."""
    from lbl_common import MIN_INTERIOR_BY_LISTEN
    assert MIN_INTERIOR == MIN_INTERIOR_BY_LISTEN[2]
