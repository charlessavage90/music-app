"""`JFX-` routing harness: walk the fixed pair set in both arms, record raw journeys.

**This produces no statistic.** It emits one record per (pair, arm, depth) holding the
journey and the quantities every criterion is computed from. `jfx_report.py` reads that
file and does the arithmetic. The split is deliberate: routing is hours, reporting is
seconds, and a reporting bug must not cost a re-route.

---

## The instrument, per `AM1.3`

- **Routing: production `find_journey` itself**, not the `CRE-` mirror.

  `AM1.3` fixes *`find_journey` semantics* and makes the mirror's use conditional
  (*"if the CRE mirror supplies any routing code, `CRE-G1(a)`'s byte-identity … is
  re-verified first"*). That precondition was discharged by `jfx_g1a_reverify.py`,
  which found the two identical at every rung to k = 20 with the ramp live — so the
  choice between them is **measured-equivalent, not assumed**, and calling the shipped
  function removes a class of instrument risk for free. **This is a methodology
  choice; the equivalence is what makes it free.**

  **No mirror routing code is CALLED.** An earlier draft kept the mirror for
  `term_breakdown` (the `C6` floor decomposition, which production has no hook for),
  but production exports `effective_floor_raw` and the floor term is one expression —
  so `C6` is computed from **production's own definition** rather than from a copy.
  (`cre_mirror` is still *imported*, transitively, because `cre_ladder` imports it at
  module level. Nothing in it is invoked. Stating that rather than claiming the
  stronger "not used at all", which the import makes false.)

- **Press selection: `cre_ladder.victim_key`** — highest-fame interior first, ruler-null
  interiors after every measured one, ties by `pop_raw` desc then lowest MBID. Cited,
  not retyped.

  **⚠ `AM1.3` names this a limitation and so does this file.** A real user presses
  whichever card they happen to know. Under `victim_key` a fame decrease is *partly
  mechanical* — the most famous interior is being deleted twenty times — so **`JFX-G1a`
  is a weak test in the absolute**, and no read may present it passing as evidence the
  product works for a user. Its force is in the between-arm contrast (`G1b`), where the
  mechanical component is present in both arms and cancels.

- **Ruler frame: production.** Each arm's `GraphStore` computes `fame_lb_pctl` against
  **its own** population, which is what the API does and is the §0.1(a) confound the
  design accepts and names. `cre_common.Ruler`'s pinned `FRAME_N = 74_151` would make
  that confound false and uncheckable, and is not used.

- **Outcome currency: `log10(1 + fame_lb)`** (`AM1.2`), from each arm's **own** APG1
  metadata blob — `GraphStore` discards raw fame at load (`AM1.4`). Nulls are excluded
  from the interior statistic and counted for `C7` (§2's null rule; a null is a measured
  absence, never a floor).

## What this file deliberately does not decide

The pair set is **read** from `jfx_pairset.json`, never re-derived — §2 fixes it in
committed order and a second derivation here is a second chance to select on the
outcome. If that file is missing, this refuses rather than falling back.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CRE = ROOT / "builder/analysis/2026-08-03-cap-reevaluation"
sys.path.insert(0, str(CRE))
sys.path.insert(0, str(ROOT / "api/src"))
sys.path.insert(0, str(HERE))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import (  # noqa: E402
    KNOWN,
    Exclusion,
    effective_floor_raw,
    find_journey,
)
from cre_ladder import victim_key  # noqa: E402

from jfx_pairset import ARM_A, ARM_A_SHA, ARM_B, load_arm  # noqa: E402
from jfx_stats import log_fame  # noqa: E402

DEPTHS = (0, 5, 10, 20)   # §2
MAX_K = max(DEPTHS)
OUT = HERE / "jfx_routes.json"
PAIRSET = HERE / "jfx_pairset.json"


def arm_context(store: GraphStore, raw_fame: list):
    """Everything one arm needs: the victim key and the outcome ruler."""
    if store.fame_lb_pctl is None:
        raise SystemExit("artifact carries no fame; the ramp cannot fire")
    fame_pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
    # victim_key wants NaN at unmeasured artists so ruler-nulls sort last.
    # fame_lb_pctl assigns nulls 0.0 (a VALUE), so the raw blob is the only
    # source for the mask.
    measured = np.array(
        [np.nan if v is None else 1.0 for v in raw_fame], dtype=np.float64
    ) * fame_pctl
    # log10(1 + fame_lb), None preserved — the AM1.2 outcome ruler.
    log_raw = [log_fame(v) for v in raw_fame]
    return victim_key(measured, store.pop_raw, store.mbids), log_raw


def floor_fired(store, cfg, excludes, path) -> bool:
    """`JFX-C6`: did the obscurity-floor term contribute anything on THIS path?

    Computed from **production's own** `effective_floor_raw` and production's own
    per-edge expression `w_floor * max(0, floor_raw - pop_raw[v])`, so there is no
    second implementation of the term to drift.

    Per EDGE ON THE RETURNED PATH, which is the question §0.1(b) asks — *"the share
    of paths where the floor term is non-zero"*. The mirror's `stats["floor_active"]`
    counts edges the search EXAMINED, which is a different quantity.
    """
    if path is None or len(path) < 2:
        return False
    base = min(float(store.pop_raw[path[0]]), float(store.pop_raw[path[-1]]))
    floor_raw = effective_floor_raw(base, excludes, cfg)
    return any(max(0.0, floor_raw - float(store.pop_raw[v])) > 0.0
               for v in path[1:])


def route_pair(store, api_cfg, key, log_raw, s, t) -> dict:
    """One all-`known` ladder to k = 20, recording only the pre-registered depths."""
    excludes: list = []
    out: dict[str, dict] = {}
    for k in range(MAX_K + 1):
        result = find_journey(store, s, t, excludes, api_cfg)
        path, kind = (None, "none") if result is None else result
        if k in DEPTHS:
            interior = [] if path is None else path[1:-1]
            values = [log_raw[v] for v in interior]
            out[str(k)] = {
                "kind": kind,
                "path_length": None if path is None else len(path),
                "interior_n": len(interior),
                # §2: interior fame, nulls EXCLUDED from the statistic...
                "interior_log_fame": [v for v in values if v is not None],
                # ...and counted, because C7 is what makes that exclusion readable.
                "interior_null_n": sum(1 for v in values if v is None),
                "floor_fired": floor_fired(store, api_cfg, excludes, path),
            }
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        excludes = excludes + [Exclusion(node=min(interior, key=key), reason=KNOWN)]
    # A ladder that ran short leaves the deeper depths absent rather than
    # fabricating a value; the report treats absence as "not routable at depth".
    return out


def run_arm(name, path, sha, pairs, resume: dict) -> dict:
    store, raw_fame, actual_sha = load_arm(path, sha)
    print(f"\n{name}: {path.name}  {store.artist_count:,} nodes  {actual_sha[:12]}…")
    api_cfg = ApiConfig()
    key, log_raw = arm_context(store, raw_fame)

    done = resume.get(name, {})
    started, t0 = len(done), time.time()
    for i, (stratum, a, b) in enumerate(pairs, 1):
        pk = f"{a}|{b}"
        if pk in done:
            continue
        s, t = store.id_by_mbid[a], store.id_by_mbid[b]
        done[pk] = {
            "stratum": stratum,
            "depths": route_pair(store, api_cfg, key, log_raw, s, t),
        }
        if i % 10 == 0 or i == len(pairs):
            rate = (len(done) - started) / max(time.time() - t0, 1e-9)
            left = (len(pairs) - i) / rate if rate > 0 else float("nan")
            print(f"   {i}/{len(pairs)} pairs  {rate * 60:.1f}/min  "
                  f"~{left / 60:.0f} min left", flush=True)
            resume[name] = done
            OUT.write_text(json.dumps(resume, indent=1), encoding="utf-8")
    resume[name] = done
    return {"artifact": path.name, "sha256": actual_sha,
            "nodes": store.artist_count}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--limit", type=int, default=None,
                   help="route only the first N pairs per stratum (a smoke run; "
                        "NEVER a result — §2 fixes the analysed set at 100)")
    args = p.parse_args(argv)

    if not PAIRSET.is_file():
        raise SystemExit(
            f"REFUSING: {PAIRSET.name} does not exist. §2 fixes the pair set in "
            "committed order; run jfx_pairset.py first rather than re-deriving it "
            "here, which would be a second chance to select on the outcome."
        )
    doc = json.loads(PAIRSET.read_text(encoding="utf-8"))
    if not doc["JFX-C5"]["pass"]:
        raise SystemExit(
            "REFUSING: JFX-C5 FAILED in jfx_pairset.json. §4 read 6 is 'stop, "
            "independent of everything above'; REQ-33 is not tradeable. Routing "
            "past a fired floor is the owner's call, not this script's."
        )

    pairs = []
    for stratum in sorted(doc["pair_set"]["strata"]):
        rows = doc["pair_set"]["strata"][stratum]
        if args.limit:
            rows = rows[: args.limit]
        pairs.extend((stratum, a, b) for a, b in rows)
    print(f"pair set: {len(pairs)} pairs"
          + ("  ⚠ SMOKE RUN, --limit set — not a result" if args.limit else ""))

    resume = {}
    if OUT.is_file():
        resume = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"resuming from {OUT.name}: "
              + ", ".join(f"{k} {len(v)} pairs" for k, v in resume.items()
                          if isinstance(v, dict)))

    meta = {}
    meta["JFX-A"] = run_arm("JFX-A", ARM_A, ARM_A_SHA, pairs, resume)
    meta["JFX-B"] = run_arm("JFX-B", ARM_B, None, pairs, resume)

    resume["_meta"] = {
        "status": "JFX- raw routes. No statistic computed here.",
        "governing": "specs/2026-08-09-journey-fame-exposure-preregistration.md",
        "depths": list(DEPTHS),
        "arms": meta,
        "smoke_run_limit": args.limit,
        "pairset_sha256": hashlib.sha256(
            PAIRSET.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(resume, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
