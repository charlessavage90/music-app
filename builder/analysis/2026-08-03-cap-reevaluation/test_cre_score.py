"""`CRE-T11`'s scoring arithmetic, on synthetic ladders.

The properties that must not drift, each written so an edit that breaks it fails
here rather than silently changing a criterion figure:

- the uniform drop is computed from committed `infeasible_cells`, never from the
  padded ladder (Seam-2 handoff, claim 4);
- pin 9's partition keeps staged `S3` cells out of the candidates' group;
- `CRE-C1` pools interior *slots* (so path length weights the median), skips
  ruler-null holes, and fires §0.4's "descent partly unmeasurable" at the right
  side of the boundary;
- `CRE-C4` counts delivered cards, including ruler-null ones;
- the two anchors carry no binding `C4` form (`CRE-AM2`);
- `CRE-C2` ranks its reference set deterministically (plan pin 6).

Imported, never re-implemented: a local copy passes while the module diverges,
which is what the closeout B3 tamper check caught in this directory before.
"""
from __future__ import annotations

import statistics

import pytest

from cre_score import (
    ANCHORS,
    C4_BINDING,
    CELLS,
    NULL_TREND_TRIGGER,
    bootstrap_median_ci,
    c1_for_cell,
    c2_for_cell,
    c4_for_cell,
    counts,
    groups,
    leave_one_out_range,
    slots,
    top_degree_set,
    uniform_drop,
)

MAX_D = 21


def depth_row(fames: list[float | None], feasible: bool = True) -> dict:
    """One depth of one pair. `None` entries are ruler-null interiors."""
    if not feasible:
        return {"kind": "none", "feasible": False}
    return {
        "kind": "natural",
        "feasible": True,
        "interior_len": len(fames),
        "interior_mbids": [f"mb-{i}" for i in range(len(fames))],
        "interior_fame_pctl": list(fames),
        "interiors_null_in_snapshot": sum(1 for f in fames if f is None),
        "interiors_absent_from_snapshot": 0,
        "null_interior_unbypassable": 0,
        "path_cost_total": 1.0,
        "term_shares": {"sim": 0.5, "jump_raw": 0.3, "floor_raw": 0.0,
                        "hop": 0.2, "ramp_fame": 0.0},
    }


def pair(d0: list, late: list, cls: str = "ff-top1pct",
         mid: list | None = None) -> dict:
    """A 21-depth ladder: d0 as given, d1-9 as `mid` (defaults to d0), d10-20 late."""
    depths = [depth_row(d0)]
    depths += [depth_row(mid if mid is not None else d0) for _ in range(1, 10)]
    depths += [depth_row(late) for _ in range(10, MAX_D)]
    return {"class": cls, "endpoints": ["a", "b"], "walked_depths": MAX_D,
            "termination": "completed", "depths": depths}


def sweep(per_pair: dict, cell: str = "E-S0-P0", infeasible=None) -> dict:
    return {"cell": cell, "artifact_sha256": "deadbeef",
            "per_pair": per_pair, "infeasible_cells": infeasible or []}


C6_STUB = {"per_pair": {"p1": {"headroom": 0.5, "frontier_nodes": 100,
                              "c6_undefined": False}}}


# --------------------------------------------------------------------------
# The uniform drop
# --------------------------------------------------------------------------
def test_uniform_drop_reads_committed_set_not_the_padded_ladder():
    """Handoff claim 4. A pair padded past its termination must NOT be dropped;
    only depths the ladder actually reached count as infeasible."""
    padded = pair([0.9], [0.9])
    for d in range(15, MAX_D):                 # padding, not measured infeasibility
        padded["depths"][d] = depth_row([], feasible=False)
    padded["walked_depths"] = 15
    s = sweep({"p1": padded}, infeasible=[])   # committed set is EMPTY
    assert uniform_drop({"E-S0-P0": s}, ["E-S0-P0"]) == []


def test_uniform_drop_unions_across_members():
    a = sweep({"p1": pair([0.9], [0.8])}, "E-S1-P0", infeasible=["p1@d3"])
    b = sweep({"p1": pair([0.9], [0.8])}, "E-S0-P0", infeasible=["p1@d7"])
    got = uniform_drop({"E-S1-P0": a, "E-S0-P0": b}, ["E-S1-P0", "E-S0-P0"])
    assert got == ["p1@d3", "p1@d7"]


def test_staged_cells_are_quarantined_from_the_canonical_group():
    """Pin 9 / analyst M3: a cell barred from candidacy must not delete
    (pair, depth) cells from the candidates' record."""
    g = groups()
    assert "E-S3-P0" not in g["canonical-E"]
    assert "B-S3-P0" not in g["canonical-B"]
    assert set(g["staged-E-S3-P0"]) == {"E-S3-P0", "E-S1-P0"}
    assert set(g["staged-B-S3-P0"]) == {"B-S3-P0", "B-S1-P0"}


def test_companions_sit_inside_their_tag_cells_canonical_group():
    g = groups()
    assert "E-S2-labelscramble-P0" in g["canonical-E"]
    assert "E-S2-votescramble-P0" in g["canonical-E"]


def test_every_cell_belongs_to_at_least_one_group():
    members = {c for m in groups().values() for c in m}
    assert members == set(CELLS)


# --------------------------------------------------------------------------
# Slot pooling
# --------------------------------------------------------------------------
def test_slots_pool_by_interior_not_by_depth():
    """Pooling weights depths by path length -- stated deliberately in §5,
    because it interacts with `CRE-C4`'s shortening."""
    e = pair([0.9, 0.8, 0.7], [0.5])
    assert slots(e, [0], set(), "p1") == [0.9, 0.8, 0.7]
    assert len(slots(e, range(10, MAX_D), set(), "p1")) == 11


def test_slots_skip_ruler_nulls_but_counts_see_them():
    e = pair([0.9, None, 0.7], [0.5])
    assert slots(e, [0], set(), "p1") == [0.9, 0.7]
    c = counts(e, [0], set(), "p1")
    assert c == {"slots": 3, "measured": 2, "null": 1, "absent": 0}


def test_slots_honour_the_dropped_set():
    e = pair([0.9], [0.5])
    got = slots(e, range(10, MAX_D), {"p1@d10", "p1@d11"}, "p1")
    assert len(got) == 9


def test_empty_interior_is_feasible_and_contributes_no_slots():
    """An `adjacent_only`/two-card depth: feasible, 0 slots to `C1`, 0 to `C4`."""
    e = pair([0.9], [])
    assert slots(e, range(10, MAX_D), set(), "p1") == []
    assert counts(e, range(10, MAX_D), set(), "p1")["slots"] == 0


# --------------------------------------------------------------------------
# `CRE-C1`
# --------------------------------------------------------------------------
def test_c1_delta_is_late_minus_d0():
    s = sweep({"p1": pair([0.9], [0.4])})
    c1 = c1_for_cell(s, set(), C6_STUB)
    assert c1["per_pair"]["p1"]["delta"] == pytest.approx(-0.5)


def test_c1_conjunction_clauses_are_separate_booleans():
    """A cell may clear the median bar and fail the bootstrap bound; §5 revised
    the pass to a conjunction precisely so one cannot stand in for the other."""
    s = sweep({f"p{i}": pair([0.9], [0.2]) for i in range(22)})
    arm = c1_for_cell(s, set(), C6_STUB)["all_interiors"]["all_famous"]
    assert arm["clause_i_median_at_or_below_-0.05"] is True
    assert arm["clause_ii_ci_upper_at_or_below_-0.015"] is True
    assert arm["median"] == pytest.approx(-0.7)


def test_c1_no_movement_is_not_a_pass():
    s = sweep({f"p{i}": pair([0.9], [0.9]) for i in range(22)})
    arm = c1_for_cell(s, set(), C6_STUB)["all_interiors"]["all_famous"]
    assert arm["clause_i_median_at_or_below_-0.05"] is False
    assert arm["pairs_within_instrument_floor"] == 22


def test_c1_knife_edge_trio_is_always_reported():
    s = sweep({f"p{i}": pair([0.9], [0.8]) for i in range(9)})
    arm = c1_for_cell(s, set(), C6_STUB)["all_interiors"]["all_famous"]
    for k in ("pairs_at_or_below_-0.05", "pairs_within_instrument_floor",
              "leave_one_out_median_range"):
        assert k in arm, f"{k} missing -- a median at n=22 can clear a bar by one pair"


def test_c1_readable_floor_is_reported_not_enforced():
    s = sweep({f"p{i}": pair([0.9], [0.4]) for i in range(3)})
    arm = c1_for_cell(s, set(), C6_STUB)["all_interiors"]["all_famous"]
    assert arm["meets_readable_floor"] is False
    assert arm["median"] is not None       # reported, with the floor flag beside it


def test_c1_matched_only_excludes_pairs_carrying_nulls():
    s = sweep({"clean": pair([0.9], [0.4]),
               "nulled": pair([0.9, None], [0.4])})
    c1 = c1_for_cell(s, set(), C6_STUB)
    assert c1["matched_pairs"] == ["clean"]
    assert c1["all_interiors"]["all_famous"]["n_pairs"] == 2
    assert c1["matched_only"]["all_famous"]["n_pairs"] == 1


def test_null_share_rise_above_005_flags_descent_partly_unmeasurable():
    """§0.4's obligation, at the boundary. d0 has no nulls; the band is 1 of 5."""
    s = sweep({"p1": pair([0.9, 0.8, 0.7, 0.6, 0.5], [0.4, 0.3, 0.2, 0.1, None])})
    c1 = c1_for_cell(s, set(), C6_STUB)
    assert c1["null_censoring"]["rise_d0_to_band"] == pytest.approx(0.2)
    assert c1["descent_partly_unmeasurable"] is True


def test_no_null_rise_does_not_flag():
    s = sweep({"p1": pair([0.9], [0.4])})
    c1 = c1_for_cell(s, set(), C6_STUB)
    assert c1["null_censoring"]["rise_d0_to_band"] == pytest.approx(0.0)
    assert c1["descent_partly_unmeasurable"] is False
    assert NULL_TREND_TRIGGER == 0.05


def test_d3_5_band_is_marked_never_a_bar():
    s = sweep({"p1": pair([0.9], [0.4], mid=[0.6])})
    c1 = c1_for_cell(s, set(), C6_STUB)
    assert c1["d3_5_band"]["never_a_bar"] is True
    assert c1["d3_5_band"]["median_delta"] == pytest.approx(-0.3)


def test_headroom_companion_carries_its_denominator():
    """Analyst m13: the ratio is unreadable across supply arms without the
    frontier size, so it is never stored alone."""
    s = sweep({"p1": pair([0.9], [0.4])})
    comp = c1_for_cell(s, set(), C6_STUB)["headroom_companion"]
    assert comp["median_1hop_headroom"] == 0.5
    assert comp["mean_frontier_nodes"] == 100
    assert comp["never_a_bar"] is True


# --------------------------------------------------------------------------
# `CRE-C2`
# --------------------------------------------------------------------------
class FakeStore:
    def __init__(self, mbids, degrees):
        self.mbids = mbids
        import numpy as np
        self.offsets = np.concatenate([[0], np.cumsum(degrees)])


def test_top_degree_set_is_deterministic_at_ties():
    """Plan pin 6: rank (degree desc, mbid asc). Ties must not depend on the
    graph's storage order -- the two references were measured disagreeing by
    0.61 on the same paths, six times `C2`'s kill margin."""
    store = FakeStore([f"z{i}" for i in range(99)] + ["aaa"], [5] * 100)
    got = top_degree_set(store)          # N = 100, so exactly one slot
    assert got == {"aaa"}, "an all-tie set must break on lowest MBID"


def test_top_degree_set_takes_ceiling_not_floor():
    store = FakeStore([f"m{i:03d}" for i in range(150)], list(range(150, 0, -1)))
    assert len(top_degree_set(store)) == 2      # ceil(150 * 0.01)


def test_c2_reports_own_graph_beside_primary_and_gates_on_primary():
    s = sweep({"p1": pair([0.9], [0.4])})
    primary, own = {"mb-0"}, set()
    c2 = c2_for_cell(s, set(), primary, own)
    assert c2["primary_adopted_artifact"]["d10_20"]["share"] == 1.0
    assert c2["own_graph"]["d10_20"]["share"] == 0.0
    assert c2["kill_clause_level_gt_0.50"] is True      # gated on primary only


def test_c2_level_clause_catches_what_the_delta_clause_cannot():
    """Every measured descent arm moves the delta negative, so a delta-only kill
    polices a direction the device does not travel (§5)."""
    s = sweep({"p1": pair([0.9, 0.8], [0.4])})   # d0-2 share 1.0, d10-20 share 1.0
    c2 = c2_for_cell(s, set(), {"mb-0", "mb-1"}, set())
    assert c2["kill_clause_delta_ge_+0.10"] is False
    assert c2["kill_clause_level_gt_0.50"] is True
    assert c2["killed"] is True


# --------------------------------------------------------------------------
# `CRE-C4`
# --------------------------------------------------------------------------
def test_c4_counts_delivered_cards_including_ruler_nulls():
    """Payload is cards the user sees. A null interior is a delivered artist
    whose fame we cannot measure -- not a missing card."""
    s = sweep({"p1": pair([0.9, None], [0.5, None])})
    c4 = c4_for_cell(s, set())
    assert c4["per_pair"]["p1"]["d0_interior_count"] == 2
    assert c4["per_pair"]["p1"]["ratio"] == pytest.approx(1.0)


def test_c4_ratio_falls_when_the_journey_shortens():
    s = sweep({"p1": pair([0.9] * 10, [0.5] * 5)})
    assert c4_for_cell(s, set())["per_pair"]["p1"]["ratio"] == pytest.approx(0.5)


def test_c4_stores_per_pair_d0_denominators():
    """d0 adjacency is arm-correlated, so the smallest denominators sit on the
    arms that add connections; the findings note needs that visible."""
    s = sweep({"p1": pair([0.9], [0.5])})
    assert c4_for_cell(s, set())["per_pair"]["p1"]["d0_interior_count"] == 1


def test_anchors_are_exactly_the_two_cre_am2_names():
    assert set(ANCHORS) == {"E-S0-P0", "B-S0-P0"}
    assert CELLS["E-S0-P0"]["baseline"] is None
    assert CELLS["B-S0-P0"]["baseline"] == "E-S0-P0"   # cross-data-set: §0.4 bars
    assert C4_BINDING == 0.70


# --------------------------------------------------------------------------
# Bootstrap (plan pin 7)
# --------------------------------------------------------------------------
def test_bootstrap_is_seeded_and_reproducible():
    vals = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1]
    assert bootstrap_median_ci(vals) == bootstrap_median_ci(vals)


def test_bootstrap_ci_brackets_the_point_estimate():
    vals = [-0.5, -0.4, -0.45, -0.35, -0.42, -0.38, -0.41, -0.39]
    ci = bootstrap_median_ci(vals)
    assert ci["lower"] <= statistics.median(vals) <= ci["upper"]
    assert ci["b"] == 10_000 and ci["seed"] == 20260803


# --------------------------------------------------------------------------
# The run-state map (§6's precondition)
# --------------------------------------------------------------------------
def test_run_state_reads_the_committed_stage0_key_not_a_remembered_one():
    """`cre_d1.json` / `cre_d3.json` name their result `branch`. Reading a key
    that is not there returns None silently and reports `cre_r_readable: false`
    on a complete run -- which is the wrong answer, not a safe one."""
    import json as _json

    from cre_common import in_dir
    for name in ("cre_d1.json", "cre_d3.json"):
        doc = _json.loads(in_dir(name).read_text(encoding="utf-8"))
        assert "branch" in doc, f"{name} lost its `branch` key"
        assert "outcome" not in doc


def test_run_state_marks_d1_branch_cells_excluded_not_unrun():
    """`CRE-D1` fired `not_supported`, so those rows DO NOT EXIST. Counting them
    as unrun would bar every read for a cell the design deleted."""
    from cre_score import D1_BRANCH_CELLS, run_state
    gates = {"CRE_G1a": {"result": "pass"},
             "CRE_G1a_red_control": {"result": "pass"},
             "CRE_G1c": {"result": "pass"}, "CRE_G2a": {}}
    rs = run_state({c: {"per_pair": {}} for c in CELLS}, gates,
                   {"branch": "not_supported"}, {"branch": "inert_as_expected"},
                   {})
    assert rs["unrun_specified_cells"] == []
    for c in D1_BRANCH_CELLS:
        assert rs["cells"][c]["branch_excluded"] is True
    assert rs["cre_r_readable"] is True


def test_run_state_bars_readability_when_a_specified_cell_is_unrun():
    from cre_score import run_state
    gates = {"CRE_G1a": {"result": "pass"},
             "CRE_G1a_red_control": {"result": "pass"},
             "CRE_G1c": {"result": "pass"}, "CRE_G2a": {}}
    partial = {c: {"per_pair": {}} for c in CELLS if c != "E-S3-P0"}
    rs = run_state(partial, gates, {"branch": "not_supported"},
                   {"branch": "inert_as_expected"}, {})
    assert rs["unrun_specified_cells"] == ["E-S3-P0"]
    assert rs["cre_r_readable"] is False


def test_leave_one_out_range_exposes_a_one_pair_knife_edge():
    vals = [-0.06] * 11 + [-0.04] * 11        # median sits between the two
    rng = leave_one_out_range(vals)
    assert rng["min"] == pytest.approx(-0.06)
    assert rng["max"] == pytest.approx(-0.04)
