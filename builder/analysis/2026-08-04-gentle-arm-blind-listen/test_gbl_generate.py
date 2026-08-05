import json
import random

from gbl_generate import (
    assert_page_data_clean,
    frozen_hub_ids,
    hidden_metrics,
    page_row,
    shuffle_tokens,
)


class FakeStore:
    names = ["A", "B", "C", "D"]
    mbids = ["ma", "mb", "mc", "md"]
    pop_raw = [0.9, 0.5, 0.4, 0.2]


class FakeRuler:
    def pctl_of(self, mbid):
        return {"ma": 0.99, "mb": 0.60, "mc": None, "md": 0.10}[mbid]


def test_shuffle_tokens_covers_both_assignments_and_is_per_pair():
    rng = random.Random(7)
    m = shuffle_tokens([f"p{i}" for i in range(64)], rng)
    assert all(set(v.values()) == {"V0", "G"} for v in m.values())
    assert {v["L"] for v in m.values()} == {"V0", "G"}  # both orders occur


def test_page_row_carries_names_and_mbids_only():
    row = page_row(FakeStore(), [0, 1, 3])
    assert row == {"artists": [{"mbid": "ma", "name": "A"},
                               {"mbid": "mb", "name": "B"},
                               {"mbid": "md", "name": "D"}]}


def test_hidden_metrics_payload_and_censoring(monkeypatch):
    import gbl_generate as gg

    class FakePM:
        top1pct_degree_frac = 0.5
        length = 4

    monkeypatch.setattr(gg, "_path_metrics", lambda store, path, top: FakePM())
    m = hidden_metrics(FakeStore(), FakeRuler(), top_set={1}, path=[0, 1, 2, 3])
    assert m["fame_pctl_interior"] == [0.60, None]   # interiors only, None kept
    assert m["payload"] == 1                          # 2 interiors - 1 in top set
    assert m["top1pct_degree_frac"] == 0.5
    assert m["length"] == 4


def test_frozen_hub_ids_maps_by_mbid_and_skips_absent():
    # The hub set is frozen once on V0 and mapped into each arm BY MBID:
    # node ids are not shared between two different artifacts, and a per-graph
    # threshold would let an arm "improve" by compressing its degree
    # distribution (path_metrics' own docstring). Absent MBIDs simply drop.
    class OtherStore:
        mbids = ["mz", "mb", "md"]

    assert frozen_hub_ids(OtherStore(), {"ma", "mb", "md"}) == {1, 2}
    assert frozen_hub_ids(OtherStore(), set()) == set()


CLEAN = {"pairs": [{"key": "ma|mb", "a": "A", "b": "B", "rows": [
    {"depth": 0,
     "L": {"artists": [{"mbid": "m1", "name": "X"}]},
     "R": {"artists": [{"mbid": "m2", "name": "Y"}]}}]}]}


def test_page_data_never_contains_arm_identifiers():
    # The invariant the whole blind rests on, tested at the JSON level.
    assert_page_data_clean(CLEAN)  # no raise
    for poison in ("V0", "B-S1", "ramp", "tiebreakfix", "candidate"):
        dirty = json.loads(json.dumps(CLEAN))
        dirty["pairs"][0]["note"] = poison
        try:
            assert_page_data_clean(dirty)
            assert False, poison
        except SystemExit:
            pass


def test_unexpected_key_is_rejected_even_with_an_innocent_value():
    dirty = json.loads(json.dumps(CLEAN))
    dirty["pairs"][0]["rows"][0]["arm_hint"] = "left one"
    try:
        assert_page_data_clean(dirty)
        assert False, "an unexpected key must fail on its own"
    except SystemExit:
        pass


def test_real_band_names_containing_forbidden_substrings_are_not_flagged():
    # The guard must scan the structure WE write, never the artist names the
    # graph supplies: "The Cramps" contains "ramp", "Armstrong" contains "arm".
    # A substring scan over the whole blob would abort generation on a band name
    # and the runner is told never to work around a gate.
    doc = json.loads(json.dumps(CLEAN))
    doc["pairs"][0]["a"] = "The Cramps"
    doc["pairs"][0]["b"] = "Louis Armstrong"
    doc["pairs"][0]["rows"][0]["L"]["artists"] = [
        {"mbid": "m1", "name": "The Cramps"},
        {"mbid": "m2", "name": "Candidate"},
        {"mbid": "m3", "name": "V0nnegut"},
    ]
    assert_page_data_clean(doc)  # must not raise
