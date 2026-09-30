"""The lattice's own routing, run through this harness on the 500-node test fixture.

The fixture carries no fame and no sidecar (`S5R-7`), so `drp_common.Map`'s loader would refuse it.
These tests build a `Map` around the fixture's `GraphStore` with a SYNTHETIC fame ranking — raw fame
taken from `pop_raw`, so the ceiling bites on the popular core as it does on the real maps — and then
run the same `side_ladder`, `at_depths`, pre-screen gate and generation check the listen uses. They
prove plumbing, not any property of the real maps; `DSL-G1` is what ties the harness to the lattice.
"""
import random
from pathlib import Path

import numpy as np
import pytest

from dsl_common import DEPTHS, ROLES, ROOT

FIXTURE = ROOT / "api" / "tests" / "fixtures" / "graph-fixture.bin"

dj = pytest.importorskip("dsl_journeys")
dc = dj.dc


def fixture_map():
    """A `drp_common.Map`, built as its __init__ builds one, minus `verify()` and the raw-fame read."""
    store = dc.GraphStore.from_bytes(Path(FIXTURE).read_bytes())
    m = dc.Map.__new__(dc.Map)
    m.sha = "fixture"
    m.store = store
    m.n = store.artist_count
    m.fame = [int(round(float(p) * 1_000_000)) + 1 for p in store.pop_raw]   # synthetic, all measured
    store.fame_lb_pctl = dc.GraphStore.fame_percentiles(m.fame)
    m.pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
    m.measured = np.ones(m.n, dtype=bool)
    m.mbids = list(store.mbids)
    m.key = dc.victim_key(m.pctl.copy(), store.pop_raw, store.mbids)
    m.distinct = np.unique(m.pctl)
    m.off = store.offsets.tolist()
    m.nbr = store.neighbours.tolist()
    m.pl = m.pctl.tolist()
    return m


@pytest.fixture(scope="module")
def fx():
    m = fixture_map()
    rng = random.Random(20260930)
    pairs = []
    while len(pairs) < 12:
        s, t = rng.sample(range(m.n), 2)
        if not dj.adjacent(m, s, t):
            pairs.append((s, t))
    return m, pairs, dj.cfg()


def test_the_incumbent_side_is_the_lattices_own_ladder(fx):
    m, pairs, cfg = fx
    for s, t in pairs:
        mine = [rec["path"] for rec in dj.side_ladder("incumbent", m, s, t, cfg)]
        theirs = [p for p, _stop in dc.ladder(m, cfg, s, t, "primary")]
        assert mine == theirs


def test_the_challenger_side_obeys_its_ceiling_and_is_inert_before_press_four(fx):
    m, pairs, cfg = fx
    diverged = 0
    for s, t in pairs:
        on = dj.side_ladder("challenger", m, s, t, cfg)
        off = dj.side_ladder("challenger", m, s, t, cfg, ceiling=False)
        for k, rec in enumerate(on):
            if rec["path"] is None:
                continue
            if k <= 3:
                assert rec["path"] == off[k]["path"]          # f_max = 1.0: nothing excluded
            if rec.get("c") is not None:
                assert rec["c"] >= dc.f_max(k)
                assert all(m.pctl[v] <= rec["c"] for v in rec["path"][1:-1])
        diverged += any((on[k]["path"] if k < len(on) else None) != (off[k]["path"] if k < len(off) else None)
                        for k in range(4, max(len(on), len(off))))
    assert diverged >= 1          # the ceiling bites somewhere; otherwise these tests prove nothing


def test_the_red_control_comparator_sees_a_difference_and_equality(fx):
    import dsl_g1
    m, pairs, cfg = fx
    s, t = pairs[0]
    on = dsl_g1.paths_of(dj.side_ladder("challenger", m, s, t, cfg))
    assert dsl_g1.compare(on, list(on)) and not dsl_g1.diverges_from(4, on, list(on))
    changed = list(on)
    changed[-1] = None if changed[-1] is not None else [0]
    assert not dsl_g1.compare(on, changed)
    assert dsl_g1.diverges_from(4, changed, on) == (len(on) - 1 >= 4)


def test_at_depths_keeps_only_interior_bearing_presented_depths(fx):
    m, pairs, cfg = fx
    for s, t in pairs:
        lad = dj.side_ladder("challenger", m, s, t, cfg)
        shown = dj.at_depths(lad)
        assert set(shown) <= set(DEPTHS)
        for d, rec in shown.items():
            assert rec is lad[d] and len(rec["path"]) > 2


def test_the_prescreen_and_generation_checks_run_on_real_ladders(fx):
    import dsl_generate
    from dsl_prescreen import screen

    m, pairs, cfg = fx
    maps = {r: m for r in ROLES}
    outcomes = set()
    for s, t in pairs:
        per_side = {r: {d: [m.mbids[v] for v in rec["path"][1:-1]]
                        for d, rec in dj.at_depths(dj.side_ladder(r, m, s, t, cfg)).items()} for r in ROLES}
        reason, _detail = screen(per_side, familiar=set())
        outcomes.add(reason[:1] if reason else None)
        pair = {"a": {"mbid": m.mbids[s], "name": "A"}, "b": {"mbid": m.mbids[t], "name": "B"}, "tier": "DRP-T1"}
        why, ladders = dsl_generate.check_pair(maps, pair, lambda role, mm, x, y: dj.side_ladder(role, mm, x, y, cfg),
                                               dj.adjacent, dj.at_depths)
        assert (why is None) == bool(ladders)
    assert outcomes, "the gates ran"


def test_journey_record_counts_added_connections_against_todays_map(fx):
    import dsl_generate
    m, pairs, cfg = fx
    s, t = pairs[0]
    lad = dj.side_ladder("challenger", m, s, t, cfg)
    d = max(dj.at_depths(lad) or {0: None})
    if lad[d]["path"] is None:
        pytest.skip("no journey at a presented depth on this pair")
    rec = dsl_generate.journey_record({"challenger": m}, "challenger", lad, d, a0=m)
    assert rec["added_connections_traversed"] == 0    # the same map on both sides adds nothing
    assert len(rec["pressed_mbids"]) == d and rec["length"] == len(lad[d]["path"])
