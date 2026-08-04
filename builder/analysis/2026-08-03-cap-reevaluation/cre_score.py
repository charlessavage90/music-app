"""`CRE-T11` -- criteria figures, the uniform drop, and the run-state map.

FIGURES ONLY, NO VERDICTS. This script computes numbers and writes them to
`cre_scores.json`. It evaluates no `CRE-R` read, writes no verdict sentence, and
names no winner. The Stage-3 findings note is written by a session that did not
run the sweeps (plan §"What is NOT in this plan"), from this file plus the prereg.

**One documented divergence from the plan's interface line.** T11's `Interfaces`
block lists only JSON inputs, and the Seam-2 handoff states "T11 needs no graph
artifact". That is true of `C1`, `C4` and `C5`, and **false of `CRE-C2`**: the
prereg's §5 fixes `C2`'s primary reference as *the production artifact's*
top-1%-by-degree set and requires the own-graph share reported beside it, and no
degree set is committed in any Stage-0/1/2 output. The prereg governs where the
plan disagrees (plan §Global Constraints), so this module loads the adopted
artifact and the eleven built cells, each sha-asserted against its own manifest
row by the existing loaders. Recorded in the execution log rather than resolved
silently.

**Uniform drop.** `drop_infeasible_uniformly`'s rule (`run_arms.py`, Track 2's
analyst D7), applied over pin 9's committed partition: one canonical group per
data set, each staged `S3` cell alone with its §0.2 baseline, companions inside
their tag cell's canonical group. **Computed from each sweep's committed
`infeasible_cells` set, never re-derived from the raw ladder** -- `walk_journey`
pads terminated pairs with `(None, "none")` entries and a re-derivation would
drop (pair, depth) cells that were never infeasible (Seam-2 handoff, claim 4).

**Currency.** Every fame figure is `fame_lb_pctl` under the §0.3 ruler. Scoring
reads `interior_fame_pctl`, which is null on both unmeasured classes -- the
device's separate pricing of those classes (plan pin 2) is never a value here
(`FAM-AM1.8`).
"""
from __future__ import annotations

import json
import statistics
import sys
import time

import numpy as np

from cre_common import (
    BOOTSTRAP_B,
    BOOTSTRAP_SEED,
    C1_BAND,
    MATERIAL,
    QUANT_FLOOR,
    SNAPSHOT,
    in_dir,
    load_adopted,
)
from cre_gates import load_cell, surviving_pairs

# --------------------------------------------------------------------------
# The §0.2 rows, as data. Sweep-cell granularity: a cell is (graph cell, pricing).
# `baseline` is §0.2's isolating-baseline column verbatim. `staged` marks the
# cells barred from candidacy (§3.1). Companions are instrument cells for
# `CRE-C5` and never appear in winner logic.
# --------------------------------------------------------------------------
CELLS: dict[str, dict] = {
    "E-S0-P0":   {"ds": "ALG-E", "graph": "E-S0",  "pricing": "P0",  "baseline": None},
    "E-S0b-P0":  {"ds": "ALG-E", "graph": "E-S0b", "pricing": "P0",  "baseline": "E-S0-P0"},
    "E-S1-P0":   {"ds": "ALG-E", "graph": "E-S1",  "pricing": "P0",  "baseline": "E-S0-P0"},
    "E-S1-P1a":  {"ds": "ALG-E", "graph": "E-S1",  "pricing": "P1a", "baseline": "E-S1-P0"},
    "E-S1-P1b":  {"ds": "ALG-E", "graph": "E-S1",  "pricing": "P1b", "baseline": "E-S1-P1a"},
    "E-S2-P0":   {"ds": "ALG-E", "graph": "E-S2",  "pricing": "P0",  "baseline": "E-S1-P0"},
    "E-S3-P0":   {"ds": "ALG-E", "graph": "E-S3",  "pricing": "P0",  "baseline": "E-S1-P0",
                  "staged": True},
    "B-S0-P0":   {"ds": "ALG-B", "graph": "B-S0",  "pricing": "P0",  "baseline": "E-S0-P0"},
    "B-S0b-P0":  {"ds": "ALG-B", "graph": "B-S0b", "pricing": "P0",  "baseline": "B-S0-P0"},
    "B-S1-P0":   {"ds": "ALG-B", "graph": "B-S1",  "pricing": "P0",  "baseline": "B-S0-P0"},
    "B-S0-P1a":  {"ds": "ALG-B", "graph": "B-S0",  "pricing": "P1a", "baseline": "B-S0-P0"},
    "B-S1-P1a":  {"ds": "ALG-B", "graph": "B-S1",  "pricing": "P1a", "baseline": "B-S1-P0"},
    "B-S1-P1b":  {"ds": "ALG-B", "graph": "B-S1",  "pricing": "P1b", "baseline": "B-S1-P1a"},
    "B-S3-P0":   {"ds": "ALG-B", "graph": "B-S3",  "pricing": "P0",  "baseline": "B-S1-P0",
                  "staged": True},
    "E-S2-labelscramble-P0": {
        "ds": "ALG-E", "graph": "E-S2-labelscramble", "pricing": "P0",
        "baseline": "E-S1-P0", "companion_of": "E-S2-P0", "companion_kind": "label"},
    "E-S2-votescramble-P0": {
        "ds": "ALG-E", "graph": "E-S2-votescramble", "pricing": "P0",
        "baseline": "E-S1-P0", "companion_of": "E-S2-P0", "companion_kind": "vote"},
}

# `CRE-AM2`: the two anchors carry no binding `C4` form. E-S0-P0 has no baseline;
# B-S0-P0's is cross-data-set, which §0.4 bars from a binding comparison.
ANCHORS = ("E-S0-P0", "B-S0-P0")

# The §0.2 rows that exist only on a `CRE-D1` "supported" branch. `CRE-D1` fired
# `not_supported`, so these cells do not exist; the run-state map reports them as
# branch-excluded rather than as unrun (which would make no read licensable).
D1_BRANCH_CELLS = ("E-S2-P1a", "B-S2-P0", "B-S2-P1a")

D0_BAND = (0,)
C2_EARLY_BAND = (0, 1, 2)
DESCRIPTIVE_BAND = (3, 4, 5)
READABLE_FLOOR = 8              # `CRE-G3`'s per-comparison device
NULL_TREND_TRIGGER = 0.05       # §0.4's "descent partly unmeasurable"
C2_DELTA_KILL = 0.10
C2_LEVEL_KILL = 0.50
C4_BINDING = 0.70
C4_REFERENCE = 0.75             # reported reference line, never a bar
TOP_DEGREE_FRAC = 0.01


def groups() -> dict[str, list[str]]:
    """Pin 9's committed partition.

    One canonical group per data set = that data set's non-staged cells plus
    their named isolating baselines; companions sit inside their tag cell's
    canonical group. Each staged `S3` cell is compared **only** against its §0.2
    baseline, so a cell barred from candidacy cannot delete (pair, depth) cells
    from the candidates' record.
    """
    out: dict[str, list[str]] = {}
    for ds, tag in (("ALG-E", "E"), ("ALG-B", "B")):
        out[f"canonical-{tag}"] = sorted(
            c for c, m in CELLS.items()
            if m["ds"] == ds and not m.get("staged"))
    for cell, m in CELLS.items():
        if m.get("staged"):
            out[f"staged-{cell}"] = sorted([cell, m["baseline"]])
    return out


# --------------------------------------------------------------------------
# Loading and the uniform drop
# --------------------------------------------------------------------------
def load_sweeps() -> dict[str, dict]:
    out = {}
    for cell in CELLS:
        p = in_dir(f"cre_sweep_{cell}.json")
        if not p.exists():
            continue
        out[cell] = json.loads(p.read_text(encoding="utf-8"))
    return out


def uniform_drop(sweeps: dict[str, dict], members: list[str]) -> list[str]:
    """A (pair, depth) cell infeasible in ANY member is dropped from EVERY member.

    Reads each cell's committed `infeasible_cells`; the raw ladder is never
    re-scanned (handoff claim 4 -- padding is not infeasibility).
    """
    dropped: set[str] = set()
    for cell in members:
        if cell in sweeps:
            dropped.update(sweeps[cell]["infeasible_cells"])
    return sorted(dropped)


def slots(entry: dict, depths, dropped: set[str], pair_key: str,
          measured_only: bool = True) -> list[float]:
    """Interior fame values pooled over `depths`, skipping dropped cells.

    An `interior_len` of 0 (a two-card journey) is feasible and contributes no
    slots -- the `run_arms.py` precedent, pinned in the plan.
    """
    out = []
    for d in depths:
        if f"{pair_key}@d{d}" in dropped:
            continue
        row = entry["depths"][d]
        if not row.get("feasible"):
            continue
        for v in row["interior_fame_pctl"]:
            if v is None and measured_only:
                continue
            out.append(v)
    return out


def counts(entry: dict, depths, dropped: set[str], pair_key: str) -> dict:
    """Interior slot counts by measurability, pooled over `depths`."""
    n_meas = n_null = n_absent = n_slots = 0
    for d in depths:
        if f"{pair_key}@d{d}" in dropped:
            continue
        row = entry["depths"][d]
        if not row.get("feasible"):
            continue
        n_slots += row["interior_len"]
        n_null += row["interiors_null_in_snapshot"]
        n_absent += row["interiors_absent_from_snapshot"]
        n_meas += sum(1 for v in row["interior_fame_pctl"] if v is not None)
    return {"slots": n_slots, "measured": n_meas, "null": n_null, "absent": n_absent}


# --------------------------------------------------------------------------
# Bootstrap (plan pin 7): pair-level resampling, B = 10,000, seed 20260803,
# percentile method. Fixed before any result so no figure can pick a procedure.
# --------------------------------------------------------------------------
def bootstrap_median_ci(values: list[float], b: int = BOOTSTRAP_B,
                        seed: int = BOOTSTRAP_SEED) -> dict | None:
    if not values:
        return None
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(arr), size=(b, len(arr)))
    meds = np.median(arr[idx], axis=1)
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return {"lower": float(lo), "upper": float(hi), "b": b, "seed": seed,
            "method": "percentile", "n_pairs": len(arr)}


def leave_one_out_range(values: list[float]) -> dict | None:
    if len(values) < 2:
        return None
    meds = [statistics.median(values[:i] + values[i + 1:])
            for i in range(len(values))]
    return {"min": float(min(meds)), "max": float(max(meds))}


# --------------------------------------------------------------------------
# `CRE-C1` -- the bypass novelty gradient (primary outcome)
# --------------------------------------------------------------------------
def c1_for_cell(sweep: dict, dropped: set[str], c6: dict) -> dict:
    """*Plain: after ten or more presses of "I know them", is the typical artist
    in the middle of the journey meaningfully less famous than before any press?*

    Per pair: median of pooled measured interior values over d10-20 minus the
    same at d0. Arm statistic: median of per-pair deltas. Reported all-interiors
    and matched-only (plan pin 4), per class and pooled, with the null-share
    trend §0.4 requires.
    """
    band = list(C1_BAND)
    per_pair, matched_keys = {}, []
    for pk, entry in sweep["per_pair"].items():
        d0 = slots(entry, D0_BAND, dropped, pk)
        late = slots(entry, band, dropped, pk)
        c_d0 = counts(entry, D0_BAND, dropped, pk)
        c_late = counts(entry, band, dropped, pk)
        row = {
            "class": entry["class"],
            "d0_median": statistics.median(d0) if d0 else None,
            "late_median": statistics.median(late) if late else None,
            "d0_counts": c_d0,
            "late_counts": c_late,
            "readable": bool(d0 and late),
        }
        row["delta"] = (row["late_median"] - row["d0_median"]
                        if row["readable"] else None)
        # matched-only (plan pin 4): no ruler-null anywhere in d0 or the band.
        row["matched"] = bool(row["readable"]
                              and c_d0["null"] == 0 and c_late["null"] == 0
                              and c_d0["absent"] == 0 and c_late["absent"] == 0)
        if row["matched"]:
            matched_keys.append(pk)
        # descriptive only, never a bar (`REQ-18` is an Expect)
        mid = slots(entry, DESCRIPTIVE_BAND, dropped, pk)
        row["d3_5_median"] = statistics.median(mid) if mid else None
        row["d3_5_delta"] = (row["d3_5_median"] - row["d0_median"]
                             if mid and row["d0_median"] is not None else None)
        per_pair[pk] = row

    def arm(keys: list[str], field: str = "delta") -> dict:
        vals = [per_pair[k][field] for k in keys
                if per_pair[k]["readable"] and per_pair[k][field] is not None]
        if not vals:
            return {"n_pairs": 0, "median": None,
                    "meets_readable_floor": False}
        med = statistics.median(vals)
        ci = bootstrap_median_ci(vals)
        return {
            "n_pairs": len(vals),
            "meets_readable_floor": len(vals) >= READABLE_FLOOR,
            "median": float(med),
            "bootstrap_ci": ci,
            # The conjunction, as three stored booleans (§5, revised at review).
            "clause_i_median_at_or_below_-0.05": bool(med <= -MATERIAL),
            "clause_ii_ci_upper_at_or_below_-0.015": (
                bool(ci["upper"] <= -QUANT_FLOOR) if ci else None),
            # Clause (iii) -- the knife-edge trio, always reported beside them.
            "pairs_at_or_below_-0.05": sum(1 for v in vals if v <= -MATERIAL),
            "pairs_within_instrument_floor": sum(
                1 for v in vals if abs(v) < QUANT_FLOOR),
            "leave_one_out_median_range": leave_one_out_range(vals),
            "per_pair_deltas": {k: per_pair[k][field] for k in keys
                                if per_pair[k]["readable"]
                                and per_pair[k][field] is not None},
        }

    all_keys = list(per_pair)
    by_class = {}
    for cls in sorted({r["class"] for r in per_pair.values()}):
        by_class[cls] = arm([k for k in all_keys if per_pair[k]["class"] == cls])

    # §0.4's differential-censoring obligation, per depth and as the trend.
    per_depth_nulls = {}
    for d in range(len(next(iter(sweep["per_pair"].values()))["depths"])):
        tot = nul = ab = 0
        for pk, entry in sweep["per_pair"].items():
            if f"{pk}@d{d}" in dropped:
                continue
            row = entry["depths"][d]
            if not row.get("feasible"):
                continue
            tot += row["interior_len"]
            nul += row["interiors_null_in_snapshot"]
            ab += row["interiors_absent_from_snapshot"]
        per_depth_nulls[f"d{d}"] = {
            "interior_slots": tot, "null": nul, "absent": ab,
            "null_share": (nul / tot) if tot else None}

    def band_share(depths) -> float | None:
        tot = sum(per_depth_nulls[f"d{d}"]["interior_slots"] for d in depths)
        nul = sum(per_depth_nulls[f"d{d}"]["null"] for d in depths)
        return (nul / tot) if tot else None

    s0, s_late = band_share(D0_BAND), band_share(band)
    rise = (s_late - s0) if (s0 is not None and s_late is not None) else None
    partly = bool(rise is not None and rise > NULL_TREND_TRIGGER)

    out = {
        "plain": ("after ten or more presses of \"I know them\", is the typical "
                  "artist in the middle of the journey meaningfully less famous "
                  "than the ones shown before any press?"),
        "all_interiors": {"all_famous": arm(all_keys), "by_class": by_class},
        "matched_only": {"all_famous": arm(matched_keys),
                         "by_class": {
                             cls: arm([k for k in matched_keys
                                       if per_pair[k]["class"] == cls])
                             for cls in sorted({r["class"]
                                                for r in per_pair.values()})}},
        "matched_pairs": sorted(matched_keys),
        "per_pair": per_pair,
        "null_censoring": {
            "per_depth": per_depth_nulls,
            "d0_null_share": s0,
            "d10_20_null_share": s_late,
            "rise_d0_to_band": rise,
            "trigger": NULL_TREND_TRIGGER,
        },
        # §0.4: never a clean pass while this is true.
        "descent_partly_unmeasurable": partly,
        "d3_5_band": {
            "never_a_bar": True,
            "note": ("`REQ-18`'s handful-of-presses window, descriptive only; "
                     "nothing here optimises toward a press count."),
            "median_delta": (statistics.median(
                [r["d3_5_delta"] for r in per_pair.values()
                 if r["d3_5_delta"] is not None])
                if any(r["d3_5_delta"] is not None for r in per_pair.values())
                else None),
        },
    }

    # §0.4's descent-headroom companion -- descriptive, never a bar, and stored
    # only with its denominator and the cell's mean frontier size beside it
    # (analyst m13: frontier size is set by the supply knob, so this is readable
    # across data sets and never across supply arms).
    heads = [r["headroom"] for r in c6["per_pair"].values()
             if not r.get("c6_undefined") and r.get("headroom") is not None]
    fronts = [r["frontier_nodes"] for r in c6["per_pair"].values()
              if r.get("frontier_nodes") is not None]
    med_head = statistics.median(heads) if heads else None
    arm_med = out["all_interiors"]["all_famous"]["median"]
    out["headroom_companion"] = {
        "never_a_bar": True,
        "median_1hop_headroom": med_head,
        "mean_frontier_nodes": (sum(fronts) / len(fronts)) if fronts else None,
        "c1_as_fraction_of_headroom": (
            (arm_med / med_head) if (med_head not in (None, 0)
                                     and arm_med is not None) else None),
        "note": ("Readable across DATA SETS (its §0.4 purpose) and never across "
                 "supply arms -- frontier size is set by the supply knob. The "
                 "findings note quotes the denominator or does not quote the "
                 "ratio."),
    }
    return out


# --------------------------------------------------------------------------
# `CRE-C2` -- hubness at depth (per-arm kill)
# --------------------------------------------------------------------------
def top_degree_set(store, frac: float = TOP_DEGREE_FRAC) -> set[str]:
    """Plan pin 6, made deterministic: rank `(degree desc, mbid asc)`, take the
    top ceil(N * 0.01), apply membership by MBID."""
    deg = np.diff(store.offsets).astype(np.int64)
    order = sorted(range(len(store.mbids)),
                   key=lambda i: (-int(deg[i]), store.mbids[i]))
    k = -(-len(order) // int(1 / frac))     # ceil(N * frac)
    return {store.mbids[i] for i in order[:k]}


def c2_for_cell(sweep: dict, dropped: set[str], primary: set[str],
                own: set[str]) -> dict:
    """*Plain: as you keep pressing, does the journey lean more and more on the
    map's most-connected artists -- or park on them outright?*

    Primary reference is the production artifact's top-degree set by MBID; the
    own-graph share is reported beside it and never gated on.
    """
    def band(depths, ref: set[str]) -> dict:
        hit = tot = 0
        for pk, entry in sweep["per_pair"].items():
            for d in depths:
                if f"{pk}@d{d}" in dropped:
                    continue
                row = entry["depths"][d]
                if not row.get("feasible"):
                    continue
                for m in row["interior_mbids"]:
                    tot += 1
                    hit += (m in ref)
        return {"slots": tot, "in_set": hit, "share": (hit / tot) if tot else None}

    res = {}
    for label, ref in (("primary_adopted_artifact", primary), ("own_graph", own)):
        early = band(C2_EARLY_BAND, ref)
        late = band(list(C1_BAND), ref)
        delta = ((late["share"] - early["share"])
                 if (early["share"] is not None and late["share"] is not None)
                 else None)
        res[label] = {
            "d0_2": early, "d10_20": late, "delta": delta,
            "reference_set_size": len(ref),
        }
    p = res["primary_adopted_artifact"]
    res["kill_clause_delta_ge_+0.10"] = bool(
        p["delta"] is not None and p["delta"] >= C2_DELTA_KILL)
    res["kill_clause_level_gt_0.50"] = bool(
        p["d10_20"]["share"] is not None and p["d10_20"]["share"] > C2_LEVEL_KILL)
    res["killed"] = bool(res["kill_clause_delta_ge_+0.10"]
                         or res["kill_clause_level_gt_0.50"])
    res["plain"] = ("as you keep pressing, does the journey lean more and more "
                    "on the map's most-connected artists -- or park on them "
                    "outright?")
    res["base_rate_note"] = ("Base rates are the d0-2 shares above; every "
                             "measured descent arm moves the delta negative, so "
                             "a null delta is not reassurance (§5).")
    res["first_path_hub_transit"] = {
        "share": res["primary_adopted_artifact"]["d0_2"]["share"],
        "gated": False,
        "note": "Tolerable by owner ruling; reported, never gated (§5).",
    }
    return res


# --------------------------------------------------------------------------
# `CRE-C4` -- delivered payload floor
# --------------------------------------------------------------------------
def c4_for_cell(sweep: dict, dropped: set[str]) -> dict:
    """*Plain: after ten or more presses, is the journey still delivering a
    comparable number of artists, or has it mostly just got shorter?*

    Per pair: mean interior count over d10-20 divided by the d0 interior count.
    Payload counts delivered artists, so ruler-null interiors count here (they
    are cards the user sees); only the fame value is unmeasurable, not the card.
    """
    per_pair = {}
    for pk, entry in sweep["per_pair"].items():
        d0_row = entry["depths"][0]
        d0_n = d0_row["interior_len"] if d0_row.get("feasible") else None
        late_counts = []
        for d in C1_BAND:
            if f"{pk}@d{d}" in dropped:
                continue
            row = entry["depths"][d]
            if row.get("feasible"):
                late_counts.append(row["interior_len"])
        mean_late = (sum(late_counts) / len(late_counts)) if late_counts else None
        per_pair[pk] = {
            "class": entry["class"],
            "d0_interior_count": d0_n,          # denominators are arm-correlated
            "mean_late_interior_count": mean_late,
            "ratio": ((mean_late / d0_n)
                      if (mean_late is not None and d0_n) else None),
        }
    vals = [r["ratio"] for r in per_pair.values() if r["ratio"] is not None]
    return {
        "plain": ("after ten or more presses, is the journey still delivering a "
                  "comparable number of artists, or has it mostly just got "
                  "shorter?"),
        "absolute_median": float(statistics.median(vals)) if vals else None,
        "absolute_reference_line": C4_REFERENCE,
        "n_pairs": len(vals),
        "per_pair": per_pair,
    }


# --------------------------------------------------------------------------
# `CRE-C5` -- tag attribution
# --------------------------------------------------------------------------
def c5_for_tag_cell(cell: str, c1: dict[str, dict],
                    companions: dict[str, str]) -> dict:
    """*Plain: is the improvement actually coming from what the labels say -- or
    would scrambled labels have done the same?*

    Δgain = cell `C1` − isolating baseline `C1`. Attribution holds iff the 95%
    pair-level bootstrap CI of the paired difference (real − companion, per
    pair) excludes zero. Two companions, two licences (`CRE-AM1`).
    """
    base = CELLS[cell]["baseline"]
    real_arm = c1[cell]["all_interiors"]["all_famous"]["median"]
    base_arm = c1[base]["all_interiors"]["all_famous"]["median"]
    real_gain = ((real_arm - base_arm)
                 if (real_arm is not None and base_arm is not None) else None)
    entered = bool(real_gain is not None and real_gain <= -MATERIAL)

    out = {
        "plain": ("is the improvement actually coming from what the labels say "
                  "-- or would scrambled labels have done the same?"),
        "isolating_baseline": base,
        "real_delta_gain": real_gain,
        "entry_condition_gain_at_or_below_-0.05": entered,
        "companions": {},
    }
    real_pp = c1[cell]["all_interiors"]["all_famous"]["per_pair_deltas"]
    licensed_any = False
    for comp_cell, kind in companions.items():
        comp_arm = c1[comp_cell]["all_interiors"]["all_famous"]["median"]
        comp_gain = ((comp_arm - base_arm)
                     if (comp_arm is not None and base_arm is not None) else None)
        comp_pp = c1[comp_cell]["all_interiors"]["all_famous"]["per_pair_deltas"]
        shared = sorted(set(real_pp) & set(comp_pp))
        paired = [real_pp[k] - comp_pp[k] for k in shared]
        ci = bootstrap_median_ci(paired) if paired else None
        excludes_zero = bool(ci and (ci["lower"] > 0 or ci["upper"] < 0))
        # Attribution is only *asked* past the entry condition; a sub-material
        # effect gets its CI reported and no licence either way.
        holds = bool(entered and excludes_zero)
        licensed_any = licensed_any or holds
        out["companions"][comp_cell] = {
            "kind": kind,
            "licence_if_it_holds": ("tags did this" if kind == "label"
                                    else "votes did this"),
            "companion_delta_gain": comp_gain,
            "paired_difference_median": (float(statistics.median(paired))
                                         if paired else None),
            "paired_bootstrap_ci": ci,
            "ci_excludes_zero": excludes_zero,
            "attribution_holds": holds,
            "n_pairs": len(paired),
        }
    out["attribution_licensed"] = licensed_any
    out["note"] = ("Attribution failing does not delete the cell's measured "
                   "outcome; it bars every sentence of the form \"tags did "
                   "this\" (`TAS-AM5c`'s any-cost artifact, pre-empted).")
    return out


# --------------------------------------------------------------------------
# The `w_floor` attribution guard (§0.3)
# --------------------------------------------------------------------------
def floor_shares(sweep: dict, dropped: set[str]) -> dict:
    """Mean `floor_raw` share of path cost at `CRE-C1`'s two read points."""
    def mean_share(depths) -> float | None:
        vals = []
        for pk, entry in sweep["per_pair"].items():
            for d in depths:
                if f"{pk}@d{d}" in dropped:
                    continue
                row = entry["depths"][d]
                if row.get("feasible") and row.get("term_shares"):
                    vals.append(row["term_shares"]["floor_raw"])
        return (sum(vals) / len(vals)) if vals else None
    return {"d0": mean_share(D0_BAND), "d10_20": mean_share(list(C1_BAND))}


def floor_guard(sweeps: dict[str, dict], drops: dict[str, set[str]]) -> dict:
    """Per supply-knob comparison: both cells' floor-term shares and a boolean.

    §0.3 fixes no threshold, and inventing one here would be a criterion wearing
    bookkeeping's clothes. The boolean is therefore the *conservative* rule --
    any non-zero differential firing sets it -- with both magnitudes stored so
    the findings note reads the size rather than the flag.
    """
    out = {}
    for cell, meta in CELLS.items():
        base = meta.get("baseline")
        if base is None or cell not in sweeps or base not in sweeps:
            continue
        # A supply-knob comparison: the graph differs, the pricing does not.
        if meta["pricing"] != CELLS[base]["pricing"]:
            continue
        if meta["graph"] == CELLS[base]["graph"]:
            continue
        if meta["ds"] != CELLS[base]["ds"]:
            continue                      # data-set comparisons are not this guard
        a = floor_shares(sweeps[cell], drops[cell])
        b = floor_shares(sweeps[base], drops[base])
        diffs = [abs((a[k] or 0.0) - (b[k] or 0.0)) for k in ("d0", "d10_20")]
        out[f"{cell}_vs_{base}"] = {
            "arm_floor_shares": a,
            "baseline_floor_shares": b,
            "max_abs_difference": max(diffs),
            "supply_attribution_carried_by_floor_term": bool(max(diffs) > 0.0),
            "rule": ("conservative: any non-zero differential floor firing sets "
                     "the flag; §0.3 fixes no threshold, so the magnitudes above "
                     "are the figure and the flag is only a pointer."),
            "bars_if_true": ("no findings sentence may attribute this outcome to "
                             "the supply knob ALONE (§0.3). A gradient achieved "
                             "with floor participation is still a real gradient."),
        }
    return out


# --------------------------------------------------------------------------
# The run-state map (§6's precondition, made mechanical)
# --------------------------------------------------------------------------
def run_state(sweeps: dict[str, dict], gates: dict, d1: dict, d3: dict,
              absent_check: dict) -> dict:
    cells = {}
    for cell in CELLS:
        cells[cell] = {
            "sweep_json_present": cell in sweeps,
            "staged_reference_barred_from_candidacy": bool(
                CELLS[cell].get("staged")),
            "companion_of": CELLS[cell].get("companion_of"),
        }
    for cell in D1_BRANCH_CELLS:
        cells[cell] = {
            "sweep_json_present": False,
            "branch_excluded": True,
            "why": ("`CRE-D1` fired `not_supported`, so this (D1-branch) row "
                    "does not exist. Not an unrun cell."),
        }
    unrun = sorted(c for c, r in cells.items()
                   if not r["sweep_json_present"] and not r.get("branch_excluded"))
    gate_outcomes = {
        "CRE_G1a": gates["CRE_G1a"]["result"],
        "CRE_G1a_red_control": gates["CRE_G1a_red_control"]["result"],
        "CRE_G1c": gates["CRE_G1c"]["result"],
        "CRE_G2a": {k: v for k, v in gates["CRE_G2a"].items()},
        "CRE_G1b": {c: s["CRE_G1b"] for c, s in sweeps.items() if "CRE_G1b" in s},
        "CRE_G2b": {c: s["CRE_G2b"] for c, s in sweeps.items() if "CRE_G2b" in s},
    }
    # The Stage-0 records name their result `branch`, not `outcome` -- read the
    # committed key, never a remembered one.
    readable = bool(not unrun and d1.get("branch") and d3.get("branch"))
    return {
        "cells": cells,
        "unrun_specified_cells": unrun,
        "gates": gate_outcomes,
        "CRE_D1_committed": bool(d1.get("branch")),
        "CRE_D1_outcome": d1.get("branch"),
        "CRE_D3_committed": bool(d3.get("branch")),
        "CRE_D3_outcome": d3.get("branch"),
        "cre_r_readable": readable,
        "note": ("`cre_r_readable` is the §6 run-state precondition only. It "
                 "says a read is not barred by an unrun cell; it does not "
                 "evaluate any `CRE-R`, and no verdict appears in this file."),
        "unmeasured_class_counters": absent_check,
    }


def absent_class_check(sweeps: dict[str, dict]) -> dict:
    """Owed item 1's remaining half, settled rather than left open.

    The Seam-2 position was that the snapshot's key set bounds every cell, so
    `interiors_absent_from_snapshot` is structurally unexercisable. It is not:
    the snapshot's key set is (adopted node set) ∪ (`ALG-B`-MK50 node set), i.e.
    two **pruned** populations, while three of the four supply arms prune less
    than MK50 -- so a looser arm keeps artists the snapshot never covered. The
    counter is therefore **live but unfired**: such artists exist in every cell
    and none was ever delivered as a journey interior on the 22 pairs.
    """
    snapshot_keys = set(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    per_cell = {}
    for graph in sorted({m["graph"] for m in CELLS.values()}):
        _, store = load_cell(graph)
        nodes = set(store.mbids)
        per_cell[graph] = {
            "nodes": len(nodes),
            "nodes_absent_from_snapshot": len(nodes - snapshot_keys),
        }
    delivered = sum(row["interiors_absent_from_snapshot"]
                    for s in sweeps.values()
                    for e in s["per_pair"].values()
                    for row in e["depths"] if row.get("feasible"))
    total_absent = sum(r["nodes_absent_from_snapshot"] for r in per_cell.values())
    return {
        "snapshot_keys": len(snapshot_keys),
        "per_graph_cell": per_cell,
        "absent_class_node_slots_across_cells": total_absent,
        "absent_class_interiors_delivered": delivered,
        "counter_status": ("live_but_unfired" if total_absent > 0 and delivered == 0
                           else "fired" if delivered > 0
                           else "structurally_unexercisable"),
        "why": ("The snapshot's key set is two PRUNED populations (adopted ∪ "
                "ALG-B-MK50). S0b, S1 and S3 prune less than MK50, so they keep "
                "artists the snapshot never covered. The Seam-2 handoff's proof "
                "bounded the crawl, not the snapshot, and does not hold."),
        "consequence": ("No artist delivered mid-journey in any cell was scored "
                        "on the absent class's 0.5 neutral prior, so plan pin "
                        "2's class choice never moved a delivered path."),
    }


# --------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    sweeps = load_sweeps()
    screen = json.loads(in_dir("cre_screen.json").read_text(encoding="utf-8"))
    gates = json.loads(in_dir("cre_gates.json").read_text(encoding="utf-8"))
    d1 = json.loads(in_dir("cre_d1.json").read_text(encoding="utf-8"))
    d3 = json.loads(in_dir("cre_d3.json").read_text(encoding="utf-8"))

    grp = groups()
    dropped_by_group = {g: uniform_drop(sweeps, m) for g, m in grp.items()}
    # Every reported figure names its group. A cell in two groups (an S3 cell's
    # baseline) is scored once per group it appears in.
    print("uniform drop, per pin 9 group:")
    for g, d in dropped_by_group.items():
        print(f"  {g:22s} members={len(grp[g]):2d} dropped_cells={len(d)}")

    print("\nloading degree references (prereg §5 -- see module docstring)")
    adopted = load_adopted()
    primary = top_degree_set(adopted)
    own_sets = {}
    for graph in sorted({m["graph"] for m in CELLS.values()}):
        _, store = load_cell(graph)
        own_sets[graph] = top_degree_set(store)
        print(f"  {graph:22s} own top-degree set={len(own_sets[graph])}")

    per_group: dict[str, dict] = {}
    c1_canonical: dict[str, dict] = {}
    for g, members in grp.items():
        dropped = set(dropped_by_group[g])
        rows = {}
        for cell in members:
            if cell not in sweeps:
                continue
            s = sweeps[cell]
            c6 = screen["cells"][CELLS[cell]["graph"]]["CRE_C6"]
            c1 = c1_for_cell(s, dropped, c6)
            rows[cell] = {
                "group": g,
                "data_set": CELLS[cell]["ds"],
                "graph_cell": CELLS[cell]["graph"],
                "pricing": CELLS[cell]["pricing"],
                "isolating_baseline": CELLS[cell]["baseline"],
                "artifact_sha256": s["artifact_sha256"],
                "CRE_C1": c1,
                "CRE_C2": c2_for_cell(s, dropped, primary,
                                      own_sets[CELLS[cell]["graph"]]),
                "CRE_C4": c4_for_cell(s, dropped),
            }
            if g.startswith("canonical"):
                c1_canonical[cell] = c1
        per_group[g] = {
            "members": members,
            "dropped_cells": dropped_by_group[g],
            "cells": rows,
        }

    # `CRE-C4`'s binding form is baseline-relative, so it is filled in after
    # every cell's absolute value exists -- within one group only.
    for g, blk in per_group.items():
        for cell, row in blk["cells"].items():
            base = CELLS[cell]["baseline"]
            c4 = row["CRE_C4"]
            if cell in ANCHORS:
                c4["no_binding_form"] = "anchor"
                c4["why_no_binding_form"] = (
                    "`CRE-AM2`: E-S0-P0 has no baseline; B-S0-P0's is "
                    "cross-data-set, which §0.4 bars. Reported absolute against "
                    "the 0.75 reference line, and it moves no bar.")
                continue
            b_row = blk["cells"].get(base)
            if b_row is None or b_row["CRE_C4"]["absolute_median"] in (None, 0):
                c4["binding_ratio_to_baseline"] = None
                continue
            ratio = c4["absolute_median"] / b_row["CRE_C4"]["absolute_median"]
            c4["binding_ratio_to_baseline"] = ratio
            c4["binding_floor"] = C4_BINDING
            c4["meets_binding_floor"] = bool(ratio >= C4_BINDING)
            # `CRE-R3`'s shape, computed as a FLAG, never as a sentence.
            c1_pass = bool(
                row["CRE_C1"]["all_interiors"]["all_famous"][
                    "clause_i_median_at_or_below_-0.05"]
                and row["CRE_C1"]["all_interiors"]["all_famous"][
                    "clause_ii_ci_upper_at_or_below_-0.015"])
            c4["CRE_R3_shape_flag"] = bool(c1_pass and not c4["meets_binding_floor"])

    companions = {c: CELLS[c]["companion_kind"] for c in CELLS
                  if CELLS[c].get("companion_of") == "E-S2-P0"}
    c5 = {"E-S2-P0": c5_for_tag_cell("E-S2-P0", c1_canonical, companions)}
    c5["E-S2-P0"]["B_S2_share_note"] = (
        "No `B-S2` cell exists (`CRE-D1` fired `not_supported`), so analyst M8's "
        "labelled-node / >=2-measured-agreement share obligation has no cell to "
        "attach to. Stated rather than omitted.")

    drops_per_cell = {}
    for g, blk in per_group.items():
        if g.startswith("canonical"):
            for cell in blk["cells"]:
                drops_per_cell[cell] = set(blk["dropped_cells"])
    for cell in CELLS:
        drops_per_cell.setdefault(cell, set())

    doc = {
        "stage": "3 (criteria figures)",
        "figures_only": ("FIGURES ONLY, NO VERDICTS. No `CRE-R` read is "
                         "evaluated here and none has been made; nothing is "
                         "adopted; the blind listen (`REQ-38`) is unspent."),
        "uniform_drop_partition": {
            "pin": 9,
            "groups": {g: {"members": m, "dropped_cells": dropped_by_group[g]}
                       for g, m in grp.items()},
            "note": ("Every reported figure names its group. Staged S3 cells sit "
                     "in their own two-cell groups so a cell barred from "
                     "candidacy cannot delete (pair, depth) cells from the "
                     "candidates' record."),
        },
        "pairs_surviving_CRE_G3": len(surviving_pairs()),
        "readable_pair_floor_per_comparison": READABLE_FLOOR,
        "by_group": per_group,
        "CRE_C5": c5,
        "w_floor_attribution_guard": floor_guard(sweeps, drops_per_cell),
        "run_state_map": run_state(sweeps, gates, d1, d3,
                                   absent_class_check(sweeps)),
        "seconds": round(time.time() - t0, 1),
    }
    in_dir("cre_scores.json").write_text(json.dumps(doc, indent=2),
                                         encoding="utf-8")
    print(f"\nwrote cre_scores.json ({doc['seconds']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
