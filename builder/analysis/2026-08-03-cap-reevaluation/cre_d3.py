"""`CRE-D3` -- the pricing prior. Stage 0, runs BEFORE any build.

**Plain (prereg §4, verbatim):** *before building anything, confirm on today's map
that the new pricing knob alone still does nothing for famous-pair journeys -- so
that if nothing moves later, we know the question was always supply.*

**Instrument prior, barred from candidacy and from every `CRE-R` winner clause**
(§3.3's carve-out). It **re-opens neither the Track 3 closed verdict nor the parked
DD-A2 decision**: it is a re-measurement of a known-inert device in the adopted
currency, run so that a later joint null can be worded honestly.

Substrate: the **adopted artifact**, no build (§3.3 carve-out). Pairs: the 22
`cb_pairs` famous pairs. Arms: `P0` (0.0), `P1a` (0.01), `P1b` (0.03), plus the
instrument-only extreme r = 1.0, **never a candidate**.

Pre-registered consequence (§4): |Δ| < 0.015 at both settings -- the expected
outcome -- binds a later `CRE-R0` to the wording stored in the `consequence` field.
Δ ≤ −0.05 at either setting contradicts the committed prior and **stops execution
for the owner's flag before Stage 2 begins**.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time

import numpy as np

from cre_common import (
    BOOTSTRAP_B,
    BOOTSTRAP_SEED,
    C1_BAND,
    EXTREME_RAMP,
    MATERIAL,
    QUANT_FLOOR,
    RAMPS,
    Ruler,
    famous_pairs,
    in_dir,
    load_adopted,
)
from cre_ladder import assert_cost_decomposition, victim_key, walk_journey
from cre_mirror import MirrorContext, SweepConfig

CONSEQUENCE_INERT = (
    "the pricing device is inert on famous pairs at incumbent supply, as Track 3 "
    "found; the open question was and is supply"
)


def excludes_at_depth(paths, key, depth):
    """The exclusion list that produced the journey at `depth`.

    walk_journey does not return its excludes, so they are recomputed from the
    returned paths with the SAME victim_key -- a pure function of the ladder's
    own output, not a second copy of the search.
    """
    from artistpath_api.pathfinding import KNOWN, Exclusion

    out = []
    for j in range(depth):
        path = paths[j][0]
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        out.append(Exclusion(node=min(interior, key=key), reason=KNOWN))
    return out


def interior_stats(paths, depths, measured, status_of, mbids):
    """Pooled interior slots over `depths`: measured values, and the two
    unmeasured classes kept separable (plan pin 2)."""
    vals, n_null, n_absent, n_slots = [], 0, 0, 0
    for d in depths:
        path = paths[d][0]
        if path is None:
            continue
        for v in path[1:-1]:
            n_slots += 1
            f = float(measured[v])
            if not math.isnan(f):
                vals.append(f)
            elif status_of(mbids[v]) == "null":
                n_null += 1
            else:
                n_absent += 1
    return vals, n_null, n_absent, n_slots


def bootstrap_ci(deltas, b=BOOTSTRAP_B, seed=BOOTSTRAP_SEED):
    """Pair-level resampling with replacement, percentile method (plan pin 7)."""
    if not deltas:
        return None, None
    rng = np.random.default_rng(seed)
    arr = np.asarray(deltas, dtype=np.float64)
    meds = np.median(rng.choice(arr, size=(b, arr.size), replace=True), axis=1)
    return float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


def main() -> int:
    t0 = time.time()
    store = load_adopted()
    ruler = Ruler()
    measured, device = ruler.arrays(store)
    ctx = MirrorContext.build(store, device)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    mbids = store.mbids
    key = victim_key(measured, pop, mbids)

    pairs = famous_pairs()
    resolved = []
    for cls, a, b in pairs:
        if a not in store.id_by_mbid or b not in store.id_by_mbid:
            raise SystemExit(
                f"CRE-D3: famous pair endpoint absent from the adopted artifact "
                f"({cls}: {a} / {b}) -- these pairs were drawn from it"
            )
        resolved.append((cls, store.id_by_mbid[a], store.id_by_mbid[b], a, b))

    arms = {"P0": 0.0, **RAMPS, "EXTREME": EXTREME_RAMP}
    ladders: dict[str, list] = {}
    for name, r in arms.items():
        cfg = SweepConfig.production().with_(w_known_ramp_fame_pctl=r)
        ladders[name] = [
            walk_journey(store, s, t, cfg, ctx, measured, pop, mbids)
            for _, s, t, _, _ in resolved
        ]
        print(f"  walked {name} (r={r})  {time.time() - t0:.1f}s", flush=True)

    # --- Gate: d0 identity (CRE-G1(b) shape) -------------------------------
    d0_divergent = []
    for name in arms:
        if name == "P0":
            continue
        for i, (cls, s, t, ma, mb) in enumerate(resolved):
            if ladders[name][i][0][0] != ladders["P0"][i][0][0]:
                d0_divergent.append({"arm": name, "class": cls, "a": ma, "b": mb})
    if d0_divergent:
        raise SystemExit(
            f"CRE-D3 ABORT: the device fires at k = 0 -- {len(d0_divergent)} "
            f"d0 journeys diverge from P0: {d0_divergent[:3]}"
        )

    # --- Gate: device liveness at the instrument extreme (CRE-G2(a) form) ---
    # Run HERE because CRE-D3 is otherwise the one device run with no live check
    # between "inert" and "not connected" (analyst B1).
    changed = sum(
        1 for i in range(len(resolved))
        if ladders["EXTREME"][i][1][0] != ladders["P0"][i][1][0]
    )
    live_share = changed / len(resolved)
    if live_share < 0.5:
        raise SystemExit(
            f"CRE-D3 ABORT: dead wire -- at r = {EXTREME_RAMP} only "
            f"{changed}/{len(resolved)} d1 journeys change (share {live_share:.3f} "
            f"< 0.5). The prior is unreadable."
        )

    # --- Gate: cost decomposition (CRE-G2(b)) at k = 1 and k = 10 -----------
    n_decomp = 0
    for name, r in arms.items():
        if r == 0.0:
            continue
        cfg = SweepConfig.production().with_(w_known_ramp_fame_pctl=r)
        for i, (_, s, t, _, _) in enumerate(resolved):
            for depth in (1, 10):
                path, kind = ladders[name][i][depth]
                if path is None:
                    continue
                ex = excludes_at_depth(ladders[name][i], key, depth)
                masked = (s, t) if kind == "forced" else None
                assert_cost_decomposition(store, ctx, cfg, ex, path, masked)
                n_decomp += 1

    # --- CRE-C1 per ramp arm ------------------------------------------------
    band = list(C1_BAND)
    per_arm = {}
    for name, r in arms.items():
        rows, deltas_all, deltas_matched = [], [], []
        per_depth_nulls = []
        for d in range(len(ladders[name][0])):
            nn = na = ns = 0
            unbypassable = 0
            for i in range(len(resolved)):
                path = ladders[name][i][d][0]
                if path is None:
                    continue
                interior = path[1:-1]
                if not interior:
                    continue
                measured_present = any(
                    not math.isnan(float(measured[v])) for v in interior
                )
                for v in interior:
                    f = float(measured[v])
                    if not math.isnan(f):
                        continue
                    ns += 1
                    if ruler.status_of(mbids[v]) == "null":
                        nn += 1
                    else:
                        na += 1
                    # Pin 3's named mechanical consequence: a ruler-null
                    # interior is never bypassed while any measured interior
                    # exists, so it accumulates with depth independent of any
                    # descent. Counted so the mechanical component is separable.
                    if measured_present:
                        unbypassable += 1
            per_depth_nulls.append({
                "depth": d,
                "interiors_null_in_snapshot": nn,
                "interiors_absent_from_snapshot": na,
                "interiors_unmeasured_total": ns,
                "null_interior_unbypassable": unbypassable,
            })

        for i, (cls, s, t, ma, mb) in enumerate(resolved):
            paths = ladders[name][i]
            d0_vals, d0_nn, d0_na, d0_slots = interior_stats(
                paths, [0], measured, ruler.status_of, mbids)
            bd_vals, bd_nn, bd_na, bd_slots = interior_stats(
                paths, band, measured, ruler.status_of, mbids)
            readable = bool(d0_vals) and bool(bd_vals)
            delta = (statistics.median(bd_vals) - statistics.median(d0_vals)
                     if readable else None)
            matched = readable and (d0_nn + d0_na + bd_nn + bd_na) == 0
            rows.append({
                "class": cls, "a": ma, "b": mb,
                "readable": readable, "delta": delta, "matched": matched,
                "d0_interior_slots": d0_slots, "band_interior_slots": bd_slots,
                "d0_unmeasured": d0_nn + d0_na, "band_unmeasured": bd_nn + bd_na,
            })
            if readable:
                deltas_all.append(delta)
                if matched:
                    deltas_matched.append(delta)

        med_all = statistics.median(deltas_all) if deltas_all else None
        lo, hi = bootstrap_ci(deltas_all)
        loo = sorted(
            statistics.median(deltas_all[:j] + deltas_all[j + 1:])
            for j in range(len(deltas_all))
        ) if len(deltas_all) > 1 else []
        per_arm[name] = {
            "ramp": r,
            "is_candidate": name in RAMPS,
            "c1_median_all_interiors": med_all,
            "c1_median_matched_only": (statistics.median(deltas_matched)
                                       if deltas_matched else None),
            "n_readable_pairs": len(deltas_all),
            "n_matched_pairs": len(deltas_matched),
            "bootstrap_2p5": lo, "bootstrap_97p5": hi,
            "n_pairs_at_or_below_material": sum(1 for d in deltas_all
                                                if d <= -MATERIAL),
            "n_pairs_below_quant_floor": sum(1 for d in deltas_all
                                             if abs(d) < QUANT_FLOOR),
            "leave_one_out_median_range": ([loo[0], loo[-1]] if loo else None),
            "per_depth_unmeasured": per_depth_nulls,
            "per_pair": rows,
        }

    # --- The pre-registered consequence ------------------------------------
    cand = [per_arm[n]["c1_median_all_interiors"] for n in RAMPS]
    if any(d is None for d in cand):
        branch, consequence = "unreadable", (
            "CRE-D3 is unreadable: a candidate ramp arm has no readable pair."
        )
    elif all(abs(d) < QUANT_FLOOR for d in cand):
        branch, consequence = "inert_as_expected", CONSEQUENCE_INERT
    elif any(d <= -MATERIAL for d in cand):
        branch, consequence = "contradicts_prior", (
            "The committed prior is CONTRADICTED: material movement (<= -0.05) at "
            "at least one candidate setting. Prereg §4: this goes to the owner as "
            "a flag and EXECUTION PAUSES before Stage 2 begins."
        )
    else:
        branch, consequence = "between_floor_and_material", (
            "Movement below the material bar at at least one candidate setting, "
            "and not inert at both. Reported as such; CRE-R0's constrained "
            "wording is not licensed by this outcome."
        )

    doc = {
        "read": "CRE-D3",
        "role": ("Stage-0 instrument prior on the adopted artifact. Barred from "
                 "candidacy and from every CRE-R winner clause (§3.3 carve-out). "
                 "Re-opens neither Track 3's closed verdict nor the parked DD-A2 "
                 "decision."),
        "substrate": "adopted artifact, no build",
        "artifact_sha256": __import__("cre_common").ADOPTED_SHA,
        "ruler_frame_n": ruler.frame_n,
        "quantisation_floor": QUANT_FLOOR,
        "material_bar": MATERIAL,
        "n_pairs": len(resolved),
        "gates": {
            "d0_identity": "PASS",
            "device_liveness_at_extreme": {
                "ramp": EXTREME_RAMP,
                "never_a_candidate": True,
                "d1_journeys_changed": changed,
                "share": live_share,
                "bar": 0.5,
                "result": "PASS",
            },
            "cost_decomposition": {"journeys_checked": n_decomp,
                                   "result": "PASS"},
        },
        "arms": per_arm,
        "branch": branch,
        "consequence": consequence,
        "seconds": round(time.time() - t0, 1),
    }
    out = in_dir("cre_d3.json")
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"\nwrote {out.name}  ({doc['seconds']}s)")
    print(f"  liveness at r={EXTREME_RAMP}: {changed}/{len(resolved)} d1 changed")
    print(f"  decomposition checked on {n_decomp} journeys")
    for n in RAMPS:
        a = per_arm[n]
        print(f"  {n} (r={a['ramp']}): C1 all={a['c1_median_all_interiors']}, "
              f"matched={a['c1_median_matched_only']}, "
              f"readable={a['n_readable_pairs']}/{len(resolved)}")
    print(f"  BRANCH: {branch}")
    return 0 if branch != "contradicts_prior" else 2


if __name__ == "__main__":
    sys.exit(main())
