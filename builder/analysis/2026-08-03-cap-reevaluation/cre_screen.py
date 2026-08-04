"""`CRE-T7` -- Stage 1 structural screens: `CRE-G3`, `CRE-C3`, `CRE-C6`, affine report.

Cheap, per cell, no depth sweeps. Runs **before any sweep** (prereg §4 stage order).

- **`CRE-G3`** -- endpoint survival. A pair that loses an endpoint in any cell is
  removed from **every** cell, so all cells are compared on one pair set.
- **`CRE-C3`** -- coverage guard (owner-fixed). Loss vs the cell's own cleaned
  pre-cap population; **>= 10,000 disqualifies**, below is reported and never
  disqualifying.
- **`CRE-C6`** -- supply screen and headroom, on the **1-hop frontier** of the d0
  path (the d0 node set alone false-negatived 10 of 21 pairs, and the ladder
  reroutes whole paths, so the frontier is the honest floor of what a press can
  reach). Screen out **iff** the zero-supply pair count makes a `CRE-C1` median
  pass arithmetically impossible -- i.e. more than half the readable pairs.

Three pins from analyst m12, implemented literally:

**(a)** "readable pairs" in the screen denominator = the pairs surviving `CRE-G3`'s
**endpoint-survival** device. The per-comparison >= 8 floor is a *different* device
and plays no part in this denominator.
**(b)** The frontier's `absent` and `null` artist counts (plan pin 2's two classes)
are reported beside the measured-only supply count -- the device can route into
them while the count structurally cannot see them.
**(c)** A pair whose d0 journey has no measured interior has **no median**; its
`C6` is recorded `c6_undefined`, excluded from the screen denominator, reported,
and never silently counted as zero supply.

**A screened cell that is a named isolating baseline still sweeps** -- a baseline is
an instrument, not a candidate. §0.2's baseline column is encoded below so that
carve-out is mechanical rather than remembered.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

import numpy as np

from cre_common import Ruler, famous_pairs, in_dir, load_adopted, use_frozen
from cre_ladder import journey
from cre_mirror import MirrorContext, SweepConfig

use_frozen("api_src")
from artistpath_api.graph_store import GraphStore  # noqa: E402

C3_DISQUALIFY_AT = 10_000
C6_SUPPLY_GAP = 0.15          # 10x the 0.015 instrument floor, deliberately
READABLE_FLOOR = 8            # the per-comparison floor (NOT the C6 denominator)


def screens_out(zero_supply: int, denominator: int) -> bool:
    """`CRE-C6`'s screen predicate, in one place.

    A cell is screened out iff a `CRE-C1` MEDIAN pass is arithmetically
    impossible -- strictly more than half the readable pairs have no supply.
    `>` not `>=`: at exactly half, the median can still land on the bar.

    Exported so `test_cre_screen` guards THIS expression rather than a copy of
    it. The copy was found by the closeout B3 tamper check, which it survived.
    """
    return denominator > 0 and zero_supply * 2 > denominator


# §0.2's isolating-baseline column, at graph-cell granularity. A cell named here
# is a baseline for at least one surviving sweep cell, so it sweeps even if
# CRE-C6 screens it out. The (D1-branch) cells are absent because CRE-D1 fired
# not_supported -- they do not exist.
BASELINE_CELLS = {"E-S0", "E-S1", "B-S0", "B-S1"}
STAGED_BARRED = {"E-S3", "B-S3"}


def load_cells() -> list[dict]:
    cells = json.loads(in_dir("cre_builds.json").read_text(encoding="utf-8"))["cells"]
    return [c for c in cells if c["supply"] != "S2" or c["agreement_kind"] == "real"] \
        + [c for c in cells if c["supply"] == "S2" and c["agreement_kind"] != "real"]


def frontier_supply(store, ctx, measured, path, ruler):
    """`CRE-C6` for one pair on one cell."""
    interior = [v for v in path[1:-1]]
    vals = [float(measured[v]) for v in interior
            if not math.isnan(float(measured[v]))]
    if not vals:
        return {"c6_undefined": True, "reason": "no measured d0 interior"}
    median = statistics.median(vals)
    cut = median - C6_SUPPLY_GAP

    frontier = set(path)
    for u in path:
        for v, _s in store.neighbours_of(u):
            frontier.add(v)

    supply = 0
    n_absent = n_null = 0
    lowest = None
    mbids = store.mbids
    for u in frontier:
        for v, _s in store.neighbours_of(u):
            f = float(measured[v])
            if math.isnan(f):
                if ruler.status_of(mbids[v]) == "null":
                    n_null += 1
                else:
                    n_absent += 1
                continue
            if lowest is None or f < lowest:
                lowest = f
            if f <= cut:
                supply += 1
    return {
        "c6_undefined": False,
        "d0_interior_median": median,
        "supply_cut": cut,
        "supply_edges": supply,
        "zero_supply": supply == 0,
        "headroom": (median - lowest) if lowest is not None else None,
        "frontier_nodes": len(frontier),
        # Pin (b): the device can route into these; the count above cannot see them.
        "frontier_edges_to_null": n_null,
        "frontier_edges_to_absent": n_absent,
    }


def main() -> int:
    t0 = time.time()
    ruler = Ruler()
    pairs = famous_pairs()
    cells = load_cells()
    cfg = SweepConfig.production()

    loaded = {}
    for c in cells:
        store = GraphStore.from_bytes(Path(c["path"]).read_bytes())
        measured, device = ruler.arrays(store)
        loaded[c["cell"]] = (c, store, measured, device)
        print(f"  loaded {c['cell']:22s} {store.artist_count} artists "
              f"({time.time() - t0:.0f}s)", flush=True)

    # --- CRE-G3: endpoint survival, applied across every cell ---------------
    lost: dict[str, list[str]] = {}
    for cls, a, b in pairs:
        missing = [name for name, (_c, store, _m, _d) in loaded.items()
                   if a not in store.id_by_mbid or b not in store.id_by_mbid]
        if missing:
            lost[f"{a}|{b}"] = missing
    surviving = [(cls, a, b) for cls, a, b in pairs if f"{a}|{b}" not in lost]
    print(f"\nCRE-G3: {len(surviving)}/{len(pairs)} pairs survive in every cell",
          flush=True)

    # --- CRE-C3 + CRE-C6 per cell ------------------------------------------
    per_cell = {}
    for name, (c, store, measured, device) in loaded.items():
        entering = c["diagnostics"]["nodes_entering_cap"]
        kept = c["diagnostics"]["nodes_after_prune"]
        lost_nodes = entering - kept
        ctx = MirrorContext.build(store, device)

        rows = {}
        for cls, a, b in surviving:
            s, t = store.id_by_mbid[a], store.id_by_mbid[b]
            path, kind = journey(store, s, t, [], cfg, ctx)
            if path is None:
                rows[f"{a}|{b}"] = {"c6_undefined": True,
                                    "reason": "no d0 journey", "class": cls}
                continue
            row = frontier_supply(store, ctx, measured, path, ruler)
            row["class"] = cls
            row["d0_kind"] = kind
            row["d0_interior_len"] = len(path) - 2
            rows[f"{a}|{b}"] = row

        # Pin (c): undefined pairs leave the denominator entirely.
        defined = [r for r in rows.values() if not r["c6_undefined"]]
        undefined = len(rows) - len(defined)
        zero_supply = sum(1 for r in defined if r["zero_supply"])
        denominator = len(defined)
        # Arithmetically impossible for a C1 MEDIAN to pass iff more than half
        # the readable pairs have no supply at all.
        screened_out = screens_out(zero_supply, denominator)
        is_baseline = name.rsplit("-", 1)[0] in BASELINE_CELLS or name in BASELINE_CELLS
        per_cell[name] = {
            "cell": name,
            "data_set": c["data_set"],
            "supply": c["supply"],
            "cap_rule": c["cap_rule"],
            "agreement_kind": c.get("agreement_kind"),
            "sha256": c["sha256"],
            "staged_reference_barred_from_candidacy": c[
                "staged_reference_barred_from_candidacy"],
            "is_isolating_baseline": is_baseline,
            "CRE_C3": {
                "cleaned_pre_cap_population": entering,
                "kept": kept,
                "artists_lost": lost_nodes,
                "disqualify_at": C3_DISQUALIFY_AT,
                "disqualified": lost_nodes >= C3_DISQUALIFY_AT,
            },
            "CRE_C6": {
                "supply_gap": C6_SUPPLY_GAP,
                "readable_pairs_denominator": denominator,
                "undefined_pairs": undefined,
                "zero_supply_pairs": zero_supply,
                "screened_out": screened_out,
                # The baseline carve-out, made mechanical.
                "sweeps_anyway_as_baseline": screened_out and is_baseline,
                "per_pair": rows,
            },
            "pop_log_low": c["diagnostics"]["pop_log_low"],
            "pop_log_high": c["diagnostics"]["pop_log_high"],
        }
        print(f"  {name:22s} C3 lost={lost_nodes:5d} "
              f"{'DISQUALIFIED' if per_cell[name]['CRE_C3']['disqualified'] else 'ok':12s} "
              f"C6 zero-supply={zero_supply}/{denominator} "
              f"{'SCREENED' if screened_out else 'passes'}"
              f"{' (baseline: sweeps anyway)' if screened_out and is_baseline else ''}",
              flush=True)

    # Assert §0.2's held-constant claim: one cleaned pre-cap population per data set.
    for ds in ("ALG-E", "ALG-B"):
        vals = {v["CRE_C3"]["cleaned_pre_cap_population"]
                for v in per_cell.values() if v["data_set"] == ds}
        if len(vals) > 1:
            raise SystemExit(
                f"{ds}: cleaned pre-cap population is not constant across its "
                f"cells ({vals}) -- the cleanup is not being held constant."
            )

    # --- The affine report (§0.3 instrumentation row; reported, never gated) --
    baselines = {"E-S0b": "E-S0", "E-S1": "E-S0", "E-S2": "E-S1",
                 "E-S2-labelscramble": "E-S1", "E-S2-votescramble": "E-S1",
                 "E-S3": "E-S1", "B-S0": "E-S0", "B-S0b": "B-S0",
                 "B-S1": "B-S0", "B-S3": "B-S1"}
    affine = {}
    for name, row in per_cell.items():
        base = baselines.get(name)
        r = {"pop_log_low": row["pop_log_low"], "pop_log_high": row["pop_log_high"],
             "isolating_baseline": base}
        if base and base in per_cell:
            b = per_cell[base]
            span_a = row["pop_log_high"] - row["pop_log_low"]
            span_b = b["pop_log_high"] - b["pop_log_low"]
            # pop_raw_arm = scale * pop_raw_base + shift, if a node's log value
            # were unchanged. Two floats per cell -- the whole instrumentation row.
            r["affine_scale_vs_baseline"] = (span_b / span_a) if span_a else None
            r["affine_shift_vs_baseline"] = (
                (b["pop_log_low"] - row["pop_log_low"]) / span_a if span_a else None)
            r["pop_raw_comparable_with_baseline"] = (
                abs(row["pop_log_low"] - b["pop_log_low"]) < 1e-12
                and abs(row["pop_log_high"] - b["pop_log_high"]) < 1e-12)
        affine[name] = r

    doc = {
        "stage": "1 (structural screens)",
        "ruler_frame_n": ruler.frame_n,
        "CRE_G3": {
            "pairs_drawn": len(pairs),
            "pairs_surviving_everywhere": len(surviving),
            "pairs_lost": lost,
            "readable_pair_floor_per_comparison": READABLE_FLOOR,
            "note": ("The >= 8 floor is a PER-COMPARISON device and is recomputed "
                     "at each comparison in Stage 2; it is deliberately NOT the "
                     "CRE-C6 screen denominator (analyst m12 pin a)."),
        },
        "cells": per_cell,
        "affine_pop_raw_report": affine,
        "seconds": round(time.time() - t0, 1),
    }
    in_dir("cre_screen.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"\nwrote cre_screen.json ({doc['seconds']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
