"""P8b probe 3: at which snapshot depths is each arm's floor term still alive?

Pure arithmetic on the floor device. `floor = min(endpoint value)` and each `known`
bypass subtracts a constant, clamped at 0 (`mirror.py:_relaxed_floor`, identical in
shape to `pathfinding.effective_floor_raw`). So the depth at which the floor dies is
`ceil(base / relax)` and needs no routing to compute.

Three questions, each of which changes how a pre-registered read must be worded:

  L1  P (raw floor, relax 0.15): is the floor alive anywhere in C1's window (d >= 10)?
  L2  FL1/FL2 (pctl floor, relax 0.05 per A2): alive at which snapshots? In particular
      at d20, which C3 and C2 both read.
  L3  the stage-1 factorial cells: w_floor = 0, so the term contributes exactly 0.0 to
      every cost -- asserted numerically here rather than argued.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-p8b-harness-review/probe_floor_lifetimes.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

from artistpath_api.graph_store import GraphStore  # noqa: E402
from mirror import MirrorContext, SweepConfig  # noqa: E402
from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS  # noqa: E402

SNAPSHOTS = (0, 1, 2, 3, 5, 7, 10, 15, 20)


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT
    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    cfg = SweepConfig.production()
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    rows = []
    for label, pairs in (("analysis", ANALYSIS_PAIRS), ("held-out", HELD_OUT_PAIRS)):
        for a, b in pairs:
            s, t = by_name[a], by_name[b]
            base_raw = min(float(pop[s]), float(pop[t]))
            base_pctl = min(float(ctx.pctl[s]), float(ctx.pctl[t]))
            dead_raw = math.ceil(base_raw / cfg.floor_relax_known)
            dead_pctl = math.ceil(base_pctl / cfg.floor_relax_known_pctl)
            rows.append({
                "set": label, "pair": f"{a} -> {b}",
                "base_floor_raw": round(base_raw, 6),
                "base_floor_pctl": round(base_pctl, 6),
                "raw_floor_dies_at_d": dead_raw,
                "pctl_floor_dies_at_d": dead_pctl,
                "raw_alive_at_snapshots": [d for d in SNAPSHOTS if d < dead_raw],
                "pctl_alive_at_snapshots": [d for d in SNAPSHOTS if d < dead_pctl],
            })

    # L3: the factorial cells multiply the floor penalty by w_floor = 0.0. Assert the
    # contribution is exactly 0.0 for every floor penalty the artifact can produce,
    # rather than arguing it.
    worst_pen = float(max(ctx.pctl.max(), pop.max()))  # largest possible floor - value
    l3 = {
        "w_floor_in_factorial_cells": 0.0,
        "largest_representable_floor_penalty": worst_pen,
        "0.0_times_it_is_exactly_zero": (0.0 * worst_pen) == 0.0,
        "adding_it_is_exact": (1.234567890123 + 0.0 * worst_pen) == 1.234567890123,
        "note": ("floor_mode stays RAW in the factorial cells (only w_floor is zeroed), so "
                 "mirror.py still COMPUTES floor_val and still increments the "
                 "stats['floor_active'] counter there -- the cost is inert, the PR-A "
                 "diagnostic is not measuring a live term."),
    }

    out = {
        "artifact": {"file": GRAPH.name, "sha256": digest},
        "constants_read_from_code": {
            "floor_relax_known_raw (ApiConfig, via SweepConfig)": cfg.floor_relax_known,
            "floor_relax_known_pctl (pre-registered, A2)": cfg.floor_relax_known_pctl,
        },
        "L1_L2_per_pair": rows,
        "L1_summary": {
            "raw floor dead by d": max(r["raw_floor_dies_at_d"] for r in rows),
            "pairs with raw floor alive at any d >= 10":
                [r["pair"] for r in rows if r["raw_floor_dies_at_d"] > 10],
            "read": ("P's raw floor is identically zero everywhere in C1's window "
                     "(d in {10,15,20}), so at those depths P's cost function EQUALS "
                     "A0's. Any P-vs-A0 difference at d >= 10 is carried-over exclusion "
                     "history from d0-d6, not a live floor term."),
        },
        "L2_summary": {
            "pairs with pctl floor alive at d15":
                [r["pair"] for r in rows if r["pctl_floor_dies_at_d"] > 15],
            "pairs with pctl floor alive at d20":
                [r["pair"] for r in rows if r["pctl_floor_dies_at_d"] > 20],
            "read": ("base_floor_pctl <= 1.0 by definition and the relax constant is 0.05, "
                     "so the percentile floor is ZERO at d20 for every pair without "
                     "exception. FL1/FL2 and W therefore share an identical cost function "
                     "at d20; any d20 difference is exclusion-history carryover. C3 "
                     "(median d5 - median d20) can only be improved by the FL device "
                     "RAISING d5, and C1 (d >= 10 vs P) can only be made less negative by "
                     "it."),
        },
        "L3_factorial_floor_is_inert": l3,
    }
    (HERE / "probe_floor_lifetimes.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
