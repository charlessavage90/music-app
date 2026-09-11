"""The draw rule's two mechanical halves. The committed `lbl_pairs.json` is the output of record;
these pin the rule so a later reader can see it would re-derive the same shape."""
import pytest

from lbl_pairs import NEEDED, deal, draw, pool_records


def rec(n):
    return {"rank": n, "name": f"N{n}", "mbid": f"m{n}", "minutes": 100 - n}


def test_neighbours_in_the_ranking_pair_when_not_adjacent():
    pairs = draw([rec(i) for i in range(4)], lambda a, b: False)
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m0", "m1"), ("m2", "m3")]


def test_an_adjacent_candidate_is_skipped_and_waits_for_the_next_artist():
    adjacent = lambda a, b: {a, b} == {"m0", "m1"}  # noqa: E731
    pairs = draw([rec(i) for i in range(4)], adjacent)
    assert [(p["a"]["mbid"], p["b"]["mbid"]) for p in pairs] == [("m0", "m2"), ("m1", "m3")]


def test_the_draw_stops_at_the_number_the_rule_needs():
    assert len(draw([rec(i) for i in range(200)], lambda a, b: False)) == NEEDED == 24


def test_dealing_alternates_and_gives_each_listen_eight_plus_four():
    pairs = [{"a": rec(2 * i), "b": rec(2 * i + 1)} for i in range(24)]
    dealt = deal(pairs)
    assert [p["a"]["rank"] for p in dealt["listen1"]["primary"]] == [0, 4, 8, 12, 16, 20, 24, 28]
    assert [p["a"]["rank"] for p in dealt["listen2"]["primary"]] == [2, 6, 10, 14, 18, 22, 26, 30]
    assert len(dealt["listen1"]["reserve"]) == len(dealt["listen2"]["reserve"]) == 4
    firsts = [p["a"]["mbid"] for part in dealt.values() for group in part.values() for p in group]
    assert len(firsts) == len(set(firsts)) == 24, "the two listens share no pair"


def test_dealing_refuses_a_short_draw():
    with pytest.raises(SystemExit):
        deal([{"a": rec(0), "b": rec(1)}])


def test_pool_exclusions_in_order_of_precedence():
    usable = [
        {"name": "ok", "ms_played": 60_000, "status": "ok", "v0_nodes": [{"mbid": "x"}], "g_nodes": [{"mbid": "x"}]},
        {"name": "gbl", "ms_played": 60_000, "status": "ok", "v0_nodes": [{"mbid": "g"}], "g_nodes": [{"mbid": "g"}]},
        {"name": "gone", "ms_played": 60_000, "status": "ok", "v0_nodes": [{"mbid": "z"}], "g_nodes": [{"mbid": "z"}]},
        {"name": "split", "ms_played": 60_000, "status": "ok", "v0_nodes": [{"mbid": "p"}], "g_nodes": [{"mbid": "q"}]},
    ]
    out = pool_records({"usable": usable}, excluded_endpoints={"g"}, served_nodes={"x", "g", "p", "q"})
    assert [r.get("excluded") for r in out] == [
        None, "GBL-AM1 endpoint", "not a node of the served map", "not one MBID in both GBL- maps"]
