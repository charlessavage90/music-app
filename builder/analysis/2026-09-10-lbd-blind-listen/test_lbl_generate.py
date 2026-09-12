"""Generation's pure parts, and the ladder over the api's committed 500-node test fixture.

`gbl_generate.py` never ran before its runner session (`GBL-` harness log §5). Exercising the
ladder, the press rule and the substitution rule on a real APG1 artifact — never the listen's maps,
which this session must not route — retires most of that residual.
"""
import dataclasses
import random
from collections import deque
from pathlib import Path

import numpy as np
import pytest

from lbl_common import DEPTHS, ROOT, TOKENS
from lbl_generate import (
    assert_page_data_clean,
    choose_pairs,
    ladder,
    press_key,
    routing_identical,
    shuffle_mapping,
)

FIXTURE = ROOT / "api" / "tests" / "fixtures" / "graph-fixture.bin"


def pair(n):
    return {"a": {"mbid": f"a{n}", "name": f"A{n}"}, "b": {"mbid": f"b{n}", "name": f"B{n}"}}


def test_every_primary_that_passes_is_kept_in_order():
    chosen, subs = choose_pairs([pair(1), pair(2)], [pair(9)], lambda p: (None, {"ok": p["a"]["mbid"]}))
    assert [p["a"]["mbid"] for p, _ in chosen] == ["a1", "a2"] and subs == []


def test_a_failing_primary_takes_the_next_reserve_and_records_why():
    bad = {"a2", "r1"}
    check = lambda p: ("(b) adjacent", {}) if p["a"]["mbid"] in bad else (None, {})  # noqa: E731
    reserves = [{"a": {"mbid": "r1", "name": "R1"}, "b": {"mbid": "s1", "name": "S1"}},
                {"a": {"mbid": "r2", "name": "R2"}, "b": {"mbid": "s2", "name": "S2"}}]
    chosen, subs = choose_pairs([pair(1), pair(2), pair(3)], reserves, check)
    assert [p["a"]["mbid"] for p, _ in chosen] == ["a1", "r2", "a3"]
    assert [s["slot"] for s in subs] == [2, 2] and subs[0]["reason"] == "(b) adjacent"


def test_exhausted_reserves_stop_the_run():
    with pytest.raises(SystemExit, match="reserves are exhausted"):
        choose_pairs([pair(1)], [], lambda p: ("(c) short", {}))


def test_the_mapping_is_a_permutation_of_the_two_roles_per_pair():
    m = shuffle_mapping([f"k{i}" for i in range(50)], random.Random(1))
    assert all(sorted(v.values()) == ["challenger", "incumbent"] and set(v) == set(TOKENS) for v in m.values())
    assert len({v["L"] for v in m.values()}) == 2   # both roles appear on the left somewhere


def page(names=("Artist", "Artist 2"), extra=None):
    artist = {"mbid": "0f0f", "name": names[0], "disambiguation": names[1]}
    row = {"depth": 0, "L": {"artists": [artist]}, "R": {"artists": [artist]}}
    doc = {"listen": 1, "pairs": [{"key": "0f0f|1e1e", "a": names[0], "b": names[1], "rows": [row]}]}
    if extra:
        doc["pairs"][0]["rows"][0]["L"]["artists"][0].update(extra)
    return doc


def test_a_clean_page_passes():
    assert_page_data_clean(page())


def test_an_undesigned_field_is_a_leak_whatever_it_holds():
    with pytest.raises(SystemExit, match="LEAK"):
        assert_page_data_clean(page(extra={"fame": 0.3}))


def test_a_missing_designed_field_is_refused_too():
    doc = page()
    del doc["pairs"][0]["rows"][0]["R"]["artists"][0]["disambiguation"]
    with pytest.raises(SystemExit, match="LEAK"):
        assert_page_data_clean(doc)


def test_an_arm_token_in_the_structure_is_caught():
    doc = page()
    doc["pairs"][0]["key"] = "served|x"
    with pytest.raises(SystemExit, match="LEAK"):
        assert_page_data_clean(doc)


def test_artist_names_that_contain_forbidden_text_do_not_abort_generation():
    assert_page_data_clean(page(names=("The Served Production Crew", "LBD challenger band, threshold era")))


# --- over a real APG1 artifact ------------------------------------------------------------------------

@pytest.fixture(scope="module")
def store():
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.graph_store import GraphStore
    s = GraphStore.load(FIXTURE)
    if s.fame_lb_pctl is None:   # the fixture predates fame; a rank by popularity keeps the ramp live
        order = np.argsort(np.argsort(np.asarray(s.pop_raw)))
        s = dataclasses.replace(s, fame_lb_pctl=order / max(1, len(order) - 1))
    return s


def far_pair(store):
    """Two nodes at the largest BFS distance from node 0 — journeys with room for presses."""
    dist = {0: 0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v, _ in store.neighbours_of(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return 0, max(dist, key=dist.get)


def test_the_ladder_presses_and_never_brings_a_pressed_artist_back(store):
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.config import ApiConfig
    s, t = far_pair(store)
    key = press_key(store, [1] * len(store.mbids))
    out = ladder(store, s, t, key, ApiConfig())
    # On this 500-node fixture the farthest pair reaches d10 and runs out of interior before d20
    # (observed 2026-09-10). That is a property of a tiny graph, and it is exactly what G4 (c)
    # exists to catch — the next test proves the gate fires on it.
    assert 0 in out and 10 in out
    for d, (path, _kind, pressed) in out.items():
        assert path[0] == s and path[-1] == t and len(path) >= 3
        assert len(pressed) == d, f"depth {d} should follow exactly {d} presses"
        assert len(set(pressed)) == d, "no artist is pressed twice"
        assert not set(pressed) & set(path[1:-1]), f"a pressed artist came back at depth {d}"
        assert s not in pressed and t not in pressed
    assert out[0][2] == [] and out[0][0] != out[10][0]


def test_run_state_gate_c_fires_on_a_pair_that_cannot_reach_depth_twenty(store):
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.config import ApiConfig
    from lbl_generate import check_pair
    s, t = far_pair(store)
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    key = press_key(store, [1] * len(store.mbids))
    p = {"a": {"mbid": store.mbids[s], "name": "S"}, "b": {"mbid": store.mbids[t], "name": "T"}}
    reason, ladders = check_pair(maps, {"incumbent": key, "challenger": key}, p, ApiConfig())
    assert reason is not None and reason.startswith("(c)") and ladders == {}


def test_gate_b_fires_on_directly_connected_endpoints(store):
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.config import ApiConfig
    from lbl_generate import check_pair
    u = 0
    v = next(iter(store.neighbours_of(u)))[0]
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    key = press_key(store, [1] * len(store.mbids))
    p = {"a": {"mbid": store.mbids[u], "name": "U"}, "b": {"mbid": store.mbids[v], "name": "V"}}
    reason, _ = check_pair(maps, {"incumbent": key, "challenger": key}, p, ApiConfig())
    assert reason.startswith("(b)")


def test_gate_a_fires_on_an_endpoint_one_map_lacks(store):
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.config import ApiConfig
    from lbl_generate import check_pair
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    p = {"a": {"mbid": store.mbids[0], "name": "U"}, "b": {"mbid": "not-in-either-map", "name": "X"}}
    reason, _ = check_pair(maps, {}, p, ApiConfig())
    assert reason.startswith("(a)")


def test_press_key_puts_unmeasured_artists_after_every_measured_one(store):
    raw = [1] * len(store.mbids)
    raw[5] = None
    key = press_key(store, raw)
    assert all(key(5) > key(i) for i in range(len(store.mbids)) if i != 5)


def test_routing_identity_sees_a_single_changed_score(store):
    assert routing_identical(store, store)
    scores = np.array(store.scores, copy=True)
    scores[0] = scores[0] * 0.5 + 0.01
    assert not routing_identical(store, dataclasses.replace(store, scores=scores))


# --- LBD-AM6: the raised generation gate, balanced dealing, and the differential guard -----------

def test_the_default_gate_bar_is_one_which_is_listen_one_exactly_as_it_ran():
    from lbl_common import MIN_INTERIOR_BY_LISTEN
    import inspect
    from lbl_generate import check_pair
    assert MIN_INTERIOR_BY_LISTEN[1] == 1 and MIN_INTERIOR_BY_LISTEN[2] == 3
    assert inspect.signature(check_pair).parameters["min_interior"].default == 1


def test_gate_c_fires_on_short_interiors_even_when_every_depth_is_reached(store, monkeypatch):
    """The findings note §4.1 defect: listen 1's gate asked for a depth, not for a journey."""
    import sys
    sys.path.insert(0, str(ROOT / "api" / "src"))
    from artistpath_api.config import ApiConfig

    import lbl_generate as G
    s, t = far_pair(store)
    two_interiors = {d: ([s, 1, 2, t], "ok", []) for d in DEPTHS}
    monkeypatch.setattr(G, "ladder", lambda *a, **k: two_interiors)
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    p = {"a": {"mbid": store.mbids[s], "name": "S"}, "b": {"mbid": store.mbids[t], "name": "T"}}
    keys = {"incumbent": None, "challenger": None}

    reason, ladders = G.check_pair(maps, keys, p, ApiConfig(), min_interior=3)
    assert reason.startswith("(c)") and "3 interior artists" in reason and ladders == {}
    reason, ladders = G.check_pair(maps, keys, p, ApiConfig(), min_interior=2)
    assert reason is None and set(ladders) == {"incumbent", "challenger"}


def test_the_sides_are_dealt_to_a_balanced_split():
    from lbl_generate import deal_mapping
    keys = [f"k{i}" for i in range(8)]
    m = deal_mapping(keys, random.Random(0))
    lefts = [m[k]["L"] for k in keys]
    assert lefts.count("challenger") == 4 and lefts.count("incumbent") == 4
    assert list(m) == keys


def test_every_dealt_pair_still_carries_both_roles_exactly_once():
    from lbl_generate import deal_mapping
    m = deal_mapping([f"k{i}" for i in range(8)], random.Random(3))
    assert all(sorted(v.values()) == ["challenger", "incumbent"] and set(v) == set(TOKENS)
               for v in m.values())


def test_dealing_still_randomises_which_pairs_get_which_side():
    """Balanced is not fixed: the 4-4 split must land on different pairs from run to run."""
    from lbl_generate import deal_mapping
    keys = [f"k{i}" for i in range(8)]
    seen = {tuple(deal_mapping(keys, random.Random(s))[k]["L"] for k in keys) for s in range(12)}
    assert len(seen) > 1


def test_an_odd_number_of_pairs_splits_as_evenly_as_it_can():
    from lbl_generate import deal_mapping
    keys = [f"k{i}" for i in range(7)]
    counts = {[deal_mapping(keys, random.Random(s))[k]["L"] for k in keys].count("challenger")
              for s in range(12)}
    assert counts <= {3, 4}


class _Store:
    """Only what `assert_differential` reads."""

    def __init__(self, n):
        self.mbids = [f"m{i}" for i in range(n)]


def _ladders(incumbent_paths, challenger_paths):
    return {"incumbent": {d: (p, "ok", []) for d, p in incumbent_paths.items()},
            "challenger": {d: (p, "ok", []) for d, p in challenger_paths.items()}}


def test_a_page_serving_one_map_against_itself_is_refused():
    store = _Store(8)
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    same = {d: [0, 1, 2, 7] for d in DEPTHS}
    from lbl_generate import assert_differential
    with pytest.raises(SystemExit, match="G5 FAILED"):
        assert_differential([({"a": 1, "b": 2}, _ladders(same, dict(same)))], maps)


def test_one_differing_row_anywhere_passes_the_differential():
    store = _Store(8)
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    a = {d: [0, 1, 2, 7] for d in DEPTHS}
    b = dict(a)
    b[20] = [0, 3, 4, 7]
    from lbl_generate import assert_differential
    assert assert_differential([({"a": 1, "b": 2}, _ladders(a, b))], maps) is None


def test_the_differential_looks_across_every_pair_not_only_the_first():
    store = _Store(8)
    maps = {"incumbent": {"store": store}, "challenger": {"store": store}}
    same = {d: [0, 1, 2, 7] for d in DEPTHS}
    other = {d: [0, 4, 5, 7] for d in DEPTHS}
    from lbl_generate import assert_differential
    chosen = [({"a": 1, "b": 2}, _ladders(same, dict(same))),
              ({"a": 3, "b": 4}, _ladders(same, other))]
    assert assert_differential(chosen, maps) is None
