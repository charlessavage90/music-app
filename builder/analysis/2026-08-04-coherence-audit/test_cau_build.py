import json

import pytest

import cau_build
from cau_common import MIN_INJECT_DISTANCE, slot_id


class FakeStore:
    """A path graph 0-1-2-3-4-5, so distances are just index differences."""

    def __init__(self, n=6):
        self.mbids = [f"m{i}" for i in range(n)]
        self.names = [f"n{i}" for i in range(n)]
        adj = {i: [j for j in (i - 1, i + 1) if 0 <= j < n] for i in range(n)}
        self.offsets, self.neighbours = [0], []
        for i in range(n):
            self.neighbours += adj[i]
            self.offsets.append(len(self.neighbours))


def test_within_is_inclusive_and_counts_hops_correctly():
    s = FakeStore()
    assert cau_build._within(s, {0}, 0) == {0}
    assert cau_build._within(s, {0}, 1) == {0, 1}
    assert cau_build._within(s, {0}, 2) == {0, 1, 2}
    assert cau_build._within(s, {2}, 1) == {1, 2, 3}


def test_inject_candidates_exclude_everything_within_the_distance_condition():
    """CAU-AM2: distance >= 3 from BOTH flanking artists means the banned set is
    everything within 2 hops of either."""
    s = FakeStore(12)
    banned = cau_build._within(s, {4, 5}, MIN_INJECT_DISTANCE - 1)
    for v in (2, 3, 4, 5, 6, 7):
        assert v in banned, f"node {v} is within 2 hops of 4 or 5 and must be banned"
    assert 1 not in banned and 8 not in banned


def _journey(n):
    return {"id": "J", "artists": [{"mbid": f"m{i}", "name": f"n{i}"}
                                   for i in range(n)]}


def test_apply_injections_inserts_and_does_not_replace():
    """CAU-CORR1: all real slots survive; the journey grows by one."""
    j = _journey(4)
    inj = {"J": {"journey": "J", "insert_at": 1, "injected_mbid": "X",
                 "injected_name": "XX"}}
    out = cau_build.apply_injections([j], inj)[0]
    assert [a["name"] for a in out["artists"]] == ["n0", "XX", "n1", "n2", "n3"]
    assert inj["J"]["slot"] == slot_id("J", 1)


def test_injected_slot_id_points_at_the_injected_artist_after_the_shift():
    """The scorer keys on final positions; an off-by-one here would silently
    score a REAL artist as the control and vice versa."""
    j = _journey(5)
    inj = {"J": {"journey": "J", "insert_at": 4, "injected_mbid": "X",
                 "injected_name": "XX"}}
    out = cau_build.apply_injections([j], inj)[0]
    pos = int(inj["J"]["slot"].split("#")[1])
    assert out["artists"][pos]["name"] == "XX"


def test_am3_control_at_the_head_excludes_exactly_the_one_real_card_it_touches():
    j = _journey(5)                      # n0 .. n4, endpoints n0 and n4
    inj = {"J": {"journey": "J", "insert_at": 1, "injected_mbid": "X",
                 "injected_name": "XX"}}
    out = cau_build.apply_injections([j], inj)[0]
    # [n0, XX, n1, n2, n3, n4] -- XX at 1, its real neighbour is index 2
    assert inj["J"]["excluded_slot"] == slot_id("J", 2)
    assert out["artists"][2]["name"] == "n1"


def test_am3_control_at_the_tail_excludes_exactly_the_one_real_card_it_touches():
    j = _journey(5)
    inj = {"J": {"journey": "J", "insert_at": 4, "injected_mbid": "X",
                 "injected_name": "XX"}}
    out = cau_build.apply_injections([j], inj)[0]
    # [n0, n1, n2, n3, XX, n4] -- XX at 4, its real neighbour is index 3
    assert inj["J"]["excluded_slot"] == slot_id("J", 3)
    assert out["artists"][3]["name"] == "n3"


def test_am3_rejects_a_control_that_would_touch_two_real_cards():
    """A mid-path insertion contaminates two real slots. That is the defect the
    owner caught, and it must abort the build rather than silently score."""
    j = _journey(6)
    inj = {"J": {"journey": "J", "insert_at": 3, "injected_mbid": "X",
                 "injected_name": "XX"}}
    with pytest.raises(SystemExit, match="touches 2 real cards"):
        cau_build.apply_injections([j], inj)


def test_page_clean_rejects_an_undesigned_key():
    page = {"journeys": [{"id": "J", "extra": 1, "artists": []}]}
    with pytest.raises(SystemExit, match="unexpected journey key"):
        cau_build.assert_page_clean(page, {})


def test_page_clean_rejects_a_leaked_sealed_slot():
    page = {"journeys": [{"id": "J#2", "artists": [
        {"mbid": "a", "name": "a", "role": "endpoint"}]}]}
    with pytest.raises(SystemExit, match="sealed slot"):
        cau_build.assert_page_clean(page, {"k": {"slot": "J#2"}})


def test_page_clean_rejects_an_unknown_role():
    page = {"journeys": [{"id": "J", "artists": [
        {"mbid": "a", "name": "a", "role": "middle"}]}]}
    with pytest.raises(SystemExit, match="unknown role"):
        cau_build.assert_page_clean(page, {})


def test_page_clean_passes_an_artist_named_after_a_forbidden_token():
    """Artist names are deliberately NOT scanned -- the GBL- 'The Cramps' case.
    An artist called 'Control' or 'The Injections' must not abort the build."""
    page = {"journeys": [{"id": "J", "artists": [
        {"mbid": "a", "name": "Control", "role": "endpoint"},
        {"mbid": "b", "name": "The Injections", "role": "interior"},
        {"mbid": "c", "name": "Sealed With A Kiss", "role": "endpoint"}]}]}
    cau_build.assert_page_clean(page, {})


def test_g_deep_journeys_takes_the_g_side_and_drops_d0():
    page = {"pairs": [{"key": "P", "a": "A", "b": "B", "rows": [
        {"depth": 0, "L": {"artists": [{"mbid": "x", "name": "x"}]},
         "R": {"artists": [{"mbid": "y", "name": "y"}]}},
        {"depth": 10, "L": {"artists": [{"mbid": "gl", "name": "gl"}]},
         "R": {"artists": [{"mbid": "vr", "name": "vr"}]}},
    ]}]}
    mapping = {"P": {"L": "G", "R": "V0"}}
    out = cau_build.g_deep_journeys(page, mapping)
    assert len(out) == 1, "d0 must not be audited"
    assert out[0]["id"] == "P@d10"
    assert out[0]["artists"][0]["name"] == "gl", "took the V0 side"


class StubRuler:
    """Every artist reads the same, so the obscurity band never constrains the
    draw and the test isolates PLACEMENT."""

    def pctl_of(self, mbid):
        return 0.5


def test_pick_injections_only_ever_places_endpoint_adjacent():
    """CAU-AM3's placement rule lives in pick_injections, and until this test
    existed nothing drove it -- reverting to a mid-path draw left the whole suite
    green. The downstream guard in apply_injections would only have fired at run
    time, in front of the owner."""
    import random

    store = FakeStore(80)
    journeys = [{"id": f"J{k}",
                 "artists": [{"mbid": f"m{k * 5 + i}", "name": f"n{k * 5 + i}"}
                             for i in range(5)]}
                for k in range(12)]
    inj = cau_build.pick_injections(journeys, store, StubRuler(), random.Random(1))

    assert len(inj) == 12
    for j in journeys:
        v = inj[j["id"]]
        last = len(j["artists"]) - 1
        assert v["insert_at"] in (1, last), (
            f"{v['insert_at']} is a mid-path insertion: it would contaminate two "
            f"real cards, which is the defect CAU-AM3 fixed")


def test_pick_injections_output_survives_the_apply_guard():
    """End-to-end on the two functions together: whatever pick_injections chooses
    must satisfy apply_injections' one-real-card assertion."""
    import random

    store = FakeStore(80)
    journeys = [{"id": f"J{k}",
                 "artists": [{"mbid": f"m{k * 6 + i}", "name": f"n{k * 6 + i}"}
                             for i in range(6)]}
                for k in range(12)]
    inj = cau_build.pick_injections(journeys, store, StubRuler(), random.Random(2))
    cau_build.apply_injections(journeys, inj)          # must not raise
    assert all("excluded_slot" in v for v in inj.values())


def test_to_page_attaches_disambiguation_and_defaults_to_empty():
    """CAU-AM4. A missing disambiguation must render as empty string, not as the
    literal None -- which would reach the page as the word 'None' beside a name."""
    import random

    journeys = [{"id": "J", "artists": [
        {"mbid": "m1", "name": "A"},
        {"mbid": "m2", "name": "B"},
        {"mbid": "m3", "name": "C"}]}]
    page = cau_build.to_page(journeys, random.Random(0),
                             {"m1": "US garage rock band"})
    arts = page["journeys"][0]["artists"]
    assert arts[0]["disambiguation"] == "US garage rock band"
    assert arts[1]["disambiguation"] == ""
    assert arts[2]["disambiguation"] == ""
    assert arts[0]["role"] == "endpoint" and arts[1]["role"] == "interior"


def test_page_clean_still_rejects_an_undesigned_artist_key_after_am4():
    """Widening the artist schema for disambiguation must not have widened it for
    anything else."""
    page = {"journeys": [{"id": "J", "artists": [
        {"mbid": "a", "name": "a", "role": "endpoint", "disambiguation": "",
         "fame": 0.9}]}]}
    with pytest.raises(SystemExit, match="unexpected artist key"):
        cau_build.assert_page_clean(page, {})
