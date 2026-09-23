"""The pre-screen's pure parts: the pool exclusions, the draw's two bans, gates L/D/N, the ranking,
the selection. Every function here is exercised without a map."""
import pytest

from lal_common import DEPTHS, MIN_INTERIOR, ROLES
from lal_prescreen import (
    WANTED,
    _endpoint,
    draw,
    familiarity,
    familiarity_mbids,
    pool_records,
    rank_key,
    screen,
    select,
)

INC, CHA = ROLES


def nodes(missing_from=()):
    full = {"m1", "m2", "m3", "m4", "m5"}
    return {r: (set() if r in missing_from else set(full)) for r in ROLES}


def usable(*names_mbids):
    return {"usable": [{"name": n, "ms_played": 60_000, "status": "ok",
                        "v0_nodes": [{"mbid": m}], "g_nodes": [{"mbid": m}]}
                       for n, m in names_mbids]}


# --- pool ---------------------------------------------------------------------------------------

def test_an_artist_with_no_exclusion_is_eligible_and_keeps_committed_order():
    recs = pool_records(usable(("A", "m1"), ("B", "m2")), {}, nodes())
    assert [(r["rank"], r["name"]) for r in recs] == [(1, "A"), (2, "B")]
    assert all("excluded" not in r for r in recs)


@pytest.mark.parametrize("label", ["GBL-AM1", "LBL listen 1", "LBL listen 2"])
def test_every_presented_endpoint_is_excluded_at_artist_level_and_named(label):
    recs = pool_records(usable(("A", "m1")), {"m1": label}, nodes())
    assert recs[0]["excluded"] == f"endpoint of a presented pair ({label})"


@pytest.mark.parametrize("role", ROLES)
def test_an_artist_missing_from_either_map_is_excluded(role):
    recs = pool_records(usable(("A", "m1")), {}, nodes(missing_from=(role,)))
    assert recs[0]["excluded"] == "not a node of both maps"


def test_an_artist_without_one_consistent_mbid_is_excluded():
    cand = {"usable": [{"name": "A", "ms_played": 1, "status": "ok",
                        "v0_nodes": [{"mbid": "m1"}], "g_nodes": [{"mbid": "m2"}]}]}
    assert pool_records(cand, {}, nodes())[0]["excluded"] == "not one MBID in both GBL- maps"


# --- draw ---------------------------------------------------------------------------------------

def rec(mbid, rank=1):
    return {"mbid": mbid, "name": mbid.upper(), "rank": rank}


def test_the_draw_pairs_greedily_in_pool_order():
    pairs = draw([rec("m1"), rec("m2"), rec("m3"), rec("m4")], lambda a, b: False, set())
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m2"), ("m3", "m4")]


def test_an_adjacent_candidate_waits_for_the_next_non_adjacent_one():
    adj = lambda a, b: {a, b} == {"m1", "m2"}  # noqa: E731
    pairs = draw([rec("m1"), rec("m2"), rec("m3")], adj, set())
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m3")]


def test_a_reserve_pair_is_banned_but_both_artists_stay_usable():
    pairs = draw([rec("m1"), rec("m2"), rec("m3"), rec("m4")], lambda a, b: False,
                 {frozenset(("m1", "m2"))})
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m1", "m3"), ("m2", "m4")]


# --- gates --------------------------------------------------------------------------------------

def per_map(inc, cha):
    """`inc`/`cha`: depth -> interior list, applied to all depths if a list is given."""
    as_depths = lambda x: x if isinstance(x, dict) else {d: list(x) for d in DEPTHS}  # noqa: E731
    return {INC: as_depths(inc), CHA: as_depths(cha)}


def test_a_long_enough_pair_differing_in_unfamiliar_artists_at_every_depth_is_kept():
    reason, detail = screen(per_map(["x1", "x2", "x3"], ["x1", "x2", "y1"]), familiar=set())
    assert reason is None
    assert detail["novel_symdiff"] == {"0": 2, "10": 2, "20": 2}


def test_gate_l_rejects_two_interior_artists_at_one_depth_on_one_map():
    cha = {0: ["a", "b", "c"], 10: ["a", "b"], 20: ["a", "b", "c"]}
    reason, _ = screen(per_map(["x", "y", "z"], cha), set())
    assert reason.startswith("L:")


def test_gate_l_rejects_a_depth_a_map_cannot_reach():
    cha = {0: ["a", "b", "c"], 10: ["a", "b", "c"]}
    reason, _ = screen(per_map(["x", "y", "z"], cha), set())
    assert reason == "L: a map does not reach d20 with an interior artist"


def test_gate_d_needs_all_three_depths_not_two():
    inc = {0: ["a", "b", "c"], 10: ["a", "b", "c"], 20: ["a", "b", "c"]}
    cha = {0: ["a", "b", "c"], 10: ["x", "b", "c"], 20: ["x", "b", "c"]}
    reason, _ = screen(per_map(inc, cha), set())
    assert reason.startswith("D:")


def test_gate_d_compares_sets_so_a_reordering_is_not_a_difference():
    reason, _ = screen(per_map(["a", "b", "c"], ["c", "b", "a"]), set())
    assert reason.startswith("D:")


def test_gate_n_rejects_a_depth_where_every_differing_artist_is_familiar():
    inc = {d: ["a", "b", "c"] for d in DEPTHS}
    cha = {0: ["a", "b", "u"], 10: ["a", "b", "u"], 20: ["a", "b", "k"]}
    reason, detail = screen(per_map(inc, cha), familiar={"c", "k"})
    assert reason.startswith("N:")
    assert detail["novel_symdiff"]["20"] == 0


def test_gate_n_counts_either_side_of_the_difference():
    inc = {d: ["a", "b", "new"] for d in DEPTHS}
    cha = {d: ["a", "b", "known"] for d in DEPTHS}
    reason, _ = screen(per_map(inc, cha), familiar={"known"})
    assert reason is None


def test_gates_are_symmetric_in_the_two_maps():
    inc = {0: ["a", "b", "c"], 10: ["a", "b", "q"], 20: ["a", "b", "c", "d"]}
    cha = {0: ["a", "b", "z"], 10: ["a", "b", "c"], 20: ["a", "e", "c"]}
    fam = {"c", "d"}
    r1, d1 = screen({INC: inc, CHA: cha}, fam)
    r2, d2 = screen({INC: cha, CHA: inc}, fam)
    assert r1 == r2 and d1["novel_symdiff"] == d2["novel_symdiff"]


def test_the_bar_is_the_value_lba_am6_fixed():
    assert MIN_INTERIOR == 3 and DEPTHS == (0, 10, 20) and WANTED == 12


# --- ranking and selection ----------------------------------------------------------------------

def row(novel, familiar_n, ra=1, rb=2, ma="m1", mb="m2"):
    return {"a": {"rank": ra, "mbid": ma, "name": ma}, "b": {"rank": rb, "mbid": mb, "name": mb},
            "detail": {"novel_symdiff": {"0": novel, "10": 0, "20": 0}},
            "familiarity": {"familiar_interior": familiar_n, "distinct_interior": 9}}


def test_most_novel_differing_artists_ranks_first():
    assert sorted([row(2, 0), row(5, 9)], key=rank_key)[0]["detail"]["novel_symdiff"]["0"] == 5


def test_ties_break_on_fewest_familiar_then_pool_rank_then_mbid():
    rows = [row(3, 2), row(3, 1, ra=50), row(3, 1, ra=2, ma="mz"), row(3, 1, ra=2, ma="ma")]
    order = sorted(rows, key=rank_key)
    assert [(r["familiarity"]["familiar_interior"], r["a"]["rank"], r["a"]["mbid"]) for r in order] == [
        (1, 2, "ma"), (1, 2, "mz"), (1, 50, "m1"), (2, 1, "m1")]


def test_familiar_interiors_are_counted_once_across_maps_and_depths():
    f = familiarity(per_map(["k", "x", "y"], ["k", "z", "w"]), {"k", "z"})
    assert f == {"distinct_interior": 5, "familiar_interior": 2}


def test_familiarity_set_takes_ambiguous_artists_too():
    cand = {"usable": [{"v0_nodes": [{"mbid": "u"}]}], "ambiguous": [{"g_nodes": [{"mbid": "a"}]}]}
    assert familiarity_mbids(cand) == {"u", "a"}


def test_fewer_than_twelve_survivors_selects_nothing():
    assert select([row(1, 0)] * 11) is None


def test_selection_is_first_eight_primary_next_four_reserve_and_carries_no_side_data():
    survivors = [row(20 - i, 0, ra=i, ma=f"a{i}", mb=f"b{i}") for i in range(14)]
    sel = select(survivors)
    assert [p["a"]["mbid"] for p in sel["primary"]] == [f"a{i}" for i in range(8)]
    assert [p["a"]["mbid"] for p in sel["reserve"]] == [f"a{i}" for i in range(8, 12)]
    for p in sel["primary"] + sel["reserve"]:
        assert set(p) == {"a", "b"} and set(p["a"]) == {"name", "mbid", "rank"}


def test_an_endpoint_leaves_with_only_name_mbid_rank():
    assert _endpoint({"name": "A", "mbid": "m", "rank": 1, "minutes": 9, "excluded": "x"}) == {
        "name": "A", "mbid": "m", "rank": 1}
