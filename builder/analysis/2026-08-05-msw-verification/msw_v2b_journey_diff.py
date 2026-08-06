"""`MSW-V2B` — does the frame deviation change which journeys the router CHOOSES?

**Not in the plan.** Folded in on the owner's authorisation, 2026-08-06, because
`MSW-V4` bounded what the router *adds up* and explicitly did not bound what it
*picks*, and because no journey had ever been run on this artifact. The analyst
named this measurement, said it was not what it had been asked for, and stopped;
this is that measurement, run with the shipped router rather than the mirror.

Plain sentence: **if we ship the new map, do the journeys you actually see differ
from the ones the listening test judged — and how often?**

WHAT IS COMPARED
----------------
One knob: the `fame_lb_pctl` column the ramp reads.

    arm        fame column                                        baseline
    SHIPPED    the new artifact's own population (graph_store       —
               .fame_percentiles, what Task 11 would ship)
    CRE        the CRE- ruler's device column (cre_common.Ruler,   SHIPPED
               framed on the retired adopted artifact) — the
               frame the LISTENED arm ran under

Everything else is byte-identical: same store, same edges, same scores, same
`pop_raw`, same `degree_hub_penalty`, same `ApiConfig`, same exclusions, same
pairs. The two stores differ in exactly one array, injected with
`dataclasses.replace`.

HELD CONSTANT, AND WHY EACH IS GENUINELY CONSTANT UNDER THE INTERVENTION
------------------------------------------------------------------------
- **The press sequence.** The exclusions at each depth are computed ONCE, from
  the SHIPPED column, and the identical `Exclusion` list is handed to both arms.
  Letting each arm choose its own victim would be a second knob — the arms would
  then differ by route *and* by which artist got pressed. Holding it is also the
  more faithful choice: in the real app the **user** picks which card they know,
  so the press sequence is an input to the router, not an output of it.
- **`w_known_ramp_fame_pctl = 0.01`.** The shipped default is `0.0`, at which
  `find_path` does not add the ramp at all, so both arms would be identical **by
  construction** and the measurement would be vacuous. `0.01` is the value Task
  11 would adopt (`P1a`, `cre_common.RAMPS`). **This measurement is therefore
  hypothetical until that default flips** and says so in its output.
- **`degree_hub_penalty`** is already materialised on the store before the
  replace, so `__post_init__` cannot recompute it differently for the two arms.
  Asserted below rather than assumed.

TWO CONTROLS, BECAUSE AN IDENTITY COMPARISON IS THE SHAPE THAT PASSES VACUOUSLY
-------------------------------------------------------------------------------
`CRE-G1(a)`'s lesson, applied: a green run from a comparison that has never gone
red is not evidence.

- **GREEN anchor (`k = 0`)**: with no presses the ramp is not added at all, so
  the two arms MUST agree on every pair. A divergence here means the harness is
  comparing something other than the fame column.
- **RED control**: one arm's column is replaced by its own reversal (`1 − p`),
  which must make journeys diverge. If the reversed run also comes out identical,
  the comparison cannot detect a routing change and **no green result from it is
  evidence** — the script says so and exits non-zero.

Figures are owned by this script's committed JSON output and by the `MSW-`
execution log's Task 10 section. Cited, never restated.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-msw-verification/msw_v2b_journey_diff.py
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
sys.path.insert(0, str(CRE_DIR))

from cre_common import RAMPS, Ruler, famous_pairs, use_frozen  # noqa: E402

use_frozen("api_src")
from artistpath_api.config import ApiConfig                    # noqa: E402
from artistpath_api.graph_store import GraphStore              # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

NEW = ROOT / "builder" / "scratch" / "graph-msw-tu50.bin"
NEW_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"

RAMP = RAMPS["P1a"]        # 0.01 — the value Task 11 would adopt
DEPTHS = (0, 1, 10, 20)    # 0 is the green anchor; 1/10/20 are the analyst's k
MAX_PRESS = max(DEPTHS)


def log(msg: str) -> None:
    print(msg, flush=True)


def load_new() -> GraphStore:
    payload = NEW.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != NEW_SHA:
        raise SystemExit(f"WRONG ARTIFACT: {NEW.name} is {got}, expected {NEW_SHA}")
    return GraphStore.from_bytes(payload)


def with_column(store: GraphStore, column: np.ndarray) -> GraphStore:
    """The same store with one array swapped. `degree_hub_penalty` is already
    materialised, so `__post_init__` recomputes nothing and the two arms cannot
    drift through it."""
    if store.degree_hub_penalty is None:
        raise SystemExit("degree_hub_penalty unmaterialised — the arms could drift")
    return dataclasses.replace(store, fame_lb_pctl=column)


def press_sequence(store: GraphStore, s: int, t: int, cfg: ApiConfig) -> list[list[Exclusion]]:
    """Exclusions in force at each depth, derived ONCE from the shipped arm.

    Highest fame first, ties by `pop_raw` descending then lowest MBID — the
    `CRE-` victim rule (`cre_ladder.victim_key`), restated against the shipped
    column because that is the column being held constant here. Stops early when
    a journey has no interior left to press.
    """
    fame = store.fame_lb_pctl
    def key(v: int):
        return (-float(fame[v]), -float(store.pop_raw[v]), store.mbids[v])

    out: list[list[Exclusion]] = []
    excludes: list[Exclusion] = []
    for _ in range(MAX_PRESS + 1):
        out.append(list(excludes))
        res = find_journey(store, s, t, excludes, cfg)
        if res is None:
            break
        path, _kind = res
        interior = path[1:-1]
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    return out


def compare(a: GraphStore, b: GraphStore, pairs, cfg) -> dict:
    """Paired `find_journey` under both columns with the SAME exclusions."""
    per_depth = {d: {"compared": 0, "differing": 0, "pairs_differing": []}
                 for d in DEPTHS}
    per_pair: dict[str, dict] = {}
    for label, sm, tm in pairs:
        if sm not in a.id_by_mbid or tm not in a.id_by_mbid:
            continue
        s, t = a.id_by_mbid[sm], a.id_by_mbid[tm]
        seq = press_sequence(a, s, t, cfg)
        rows = {}
        for d in DEPTHS:
            if d >= len(seq):
                rows[d] = None          # the ladder never reached this depth
                continue
            ex = seq[d]
            ra, rb = find_journey(a, s, t, ex, cfg), find_journey(b, s, t, ex, cfg)
            pa = (None, "none") if ra is None else ra
            pb = (None, "none") if rb is None else rb
            differs = pa != pb
            per_depth[d]["compared"] += 1
            per_depth[d]["differing"] += bool(differs)
            if differs:
                per_depth[d]["pairs_differing"].append(label)
            rows[d] = {
                "differs": differs,
                "shipped_kind": pa[1],
                "cre_kind": pb[1],
                "shipped_interior": [a.names[v] for v in (pa[0] or [])[1:-1]],
                "cre_interior": [b.names[v] for v in (pb[0] or [])[1:-1]],
            }
        per_pair[label] = rows
    for d in DEPTHS:
        c = per_depth[d]
        c["fraction_differing"] = (c["differing"] / c["compared"]) if c["compared"] else None
    return {"per_depth": per_depth, "per_pair": per_pair}


def main() -> int:
    store = load_new()
    if store.fame_lb_pctl is None:
        raise SystemExit("the new artifact carries no fame data — nothing to compare")

    ruler = Ruler()
    _measured, device = ruler.arrays(store)
    shipped = with_column(store, store.fame_lb_pctl)
    cre = with_column(store, device)
    cfg = ApiConfig(w_known_ramp_fame_pctl=RAMP)

    # --- the pair sets ------------------------------------------------------
    approved = json.loads((GBL_DIR / "gbl_pairs_approved.json").read_text("utf-8"))
    gbl = [(f"{p['a']['name']} -> {p['b']['name']}", p["a"]["mbid"], p["b"]["mbid"])
           for p in approved["pairs"]]
    famous = [(f"{cls}:{a[:8]}|{b[:8]}", a, b) for cls, a, b in famous_pairs()]
    famous_resolved = [p for p in famous
                       if p[1] in store.id_by_mbid and p[2] in store.id_by_mbid]

    log(f"artifact {NEW.name} sha ok, {len(store.mbids):,} nodes")
    log(f"ramp r = {RAMP} (shipped default is 0.0 — this run is HYPOTHETICAL "
        f"until Task 11 flips it)")
    log(f"pairs: {len(gbl)} GBL-AM1, {len(famous_resolved)}/{len(famous)} CRE famous "
        f"resolve in this artifact\n")

    results = {}
    for name, pairs in (("GBL-AM1", gbl), ("CRE-famous", famous_resolved)):
        log(f"--- {name} ---")
        res = compare(shipped, cre, pairs, cfg)
        for d in DEPTHS:
            c = res["per_depth"][d]
            frac = c["fraction_differing"]
            tag = "  (green anchor: MUST be 0)" if d == 0 else ""
            log(f"  k={d:<3} {c['differing']}/{c['compared']} journeys differ"
                f"{'' if frac is None else f'  = {frac:.3f}'}{tag}")
        results[name] = res
        log("")

    # --- the two controls ---------------------------------------------------
    anchor_bad = [n for n, r in results.items()
                  if r["per_depth"][0]["differing"] != 0]
    reversed_col = 1.0 - np.asarray(store.fame_lb_pctl, dtype=np.float64)
    red = compare(shipped, with_column(store, reversed_col), gbl, cfg)
    red_fired = any(red["per_depth"][d]["differing"] > 0 for d in DEPTHS if d != 0)
    log(f"RED control (fame column reversed): "
        f"{ {d: red['per_depth'][d]['differing'] for d in DEPTHS} } differing — "
        f"{'PASS, the comparison can go red' if red_fired else 'FAIL'}")
    log(f"GREEN anchor k=0: {'PASS' if not anchor_bad else 'FAIL in ' + str(anchor_bad)}")

    payload = {
        "check": "MSW-V2B",
        "status": ("diagnostic; NOT in the plan — folded in on the owner's "
                   "authorisation 2026-08-06; adopts nothing, changes no default, "
                   "touches no shipped code"),
        "no_branch_assigned": True,
        "why_no_branch": ("no threshold was pre-registered for this measurement — it "
                          "did not exist when the plan was written. It is a bound for "
                          "the Seam 3 report, not a gate."),
        "plain_question": ("if we ship the new map, do the journeys you actually see "
                           "differ from the ones the listening test judged?"),
        "artifact": {"name": NEW.name, "sha256": NEW_SHA, "nodes": len(store.mbids)},
        "knob": {
            "varied": "the fame_lb_pctl column the known-ramp reads",
            "shipped": "the new artifact's own population (graph_store.fame_percentiles)",
            "cre": "cre_common.Ruler device column, framed on the retired adopted artifact",
            "held": ("same store, edges, scores, pop_raw, degree_hub_penalty, ApiConfig, "
                     "exclusions and pairs; one array swapped via dataclasses.replace"),
        },
        "ramp": {
            "w_known_ramp_fame_pctl": RAMP,
            "shipped_default": 0.0,
            "hypothetical": ("at the shipped default of 0.0 the ramp is not added at "
                             "all and the two arms are identical BY CONSTRUCTION. This "
                             "run presupposes Task 11's flip and is not evidence about "
                             "what the app does today."),
        },
        "press_sequence": {
            "derived_from": "the SHIPPED arm only, then handed identically to both",
            "rule": "highest fame first, ties by pop_raw desc then lowest MBID",
            "why_held": ("letting each arm pick its own victim would be a second knob; "
                         "holding it also matches the app, where the USER picks"),
        },
        "controls": {
            "green_anchor_k0": {
                "expectation": "identical on every pair — the ramp is not added at k=0",
                "result": "PASS" if not anchor_bad else f"FAIL in {anchor_bad}",
            },
            "red_reversed_column": {
                "what": "one arm's fame column replaced by 1 - p",
                "differing_by_depth": {d: red["per_depth"][d]["differing"] for d in DEPTHS},
                "result": "PASS" if red_fired else "FAIL — comparison cannot go red",
            },
        },
        "results": results,
    }
    out = HERE / "msw_v2b_journey_diff.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"\nwrote {out.name}")

    if anchor_bad or not red_fired:
        log("\nINSTRUMENT FAILURE: a control did not behave. No result above is "
            "evidence. Fix the harness; do not read the numbers.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
