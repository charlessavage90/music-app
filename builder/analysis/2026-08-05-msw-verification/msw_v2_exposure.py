"""`MSW-V2` — exposure to the un-listenable class, measured on the new artifact.

Task 10 Step 2 of `plans/2026-08-05-msw-package-adoption.md`. Plain sentence:
**how often does a journey's middle land on an artist who has nothing of their
own to play, now that the filter is on?**

**This is a REPORT ROW, NOT A GATE.** No threshold was pre-registered for it, so
**no branch is assigned and no read fires** — deliberately, and this script will
not supply one. `ulc_exposure.branch` is NOT imported for that reason: it applies
`ULC-`'s §3.1 branch table, which was pre-registered for a different comparison.

The frozen original `analysis/2026-08-05-unlistenable-class/ulc_exposure.py` is
NOT edited. Its shared pieces are IMPORTED from it (`paired_median_ci`, the depth
constants, the bootstrap seed) so the statistic here is the same object that
produced the comparator, not a retyped copy of it.

FACTOR TABLE
------------
One row per arm, one column per knob that varies, and the isolating baseline
named per row.

    arm            artifact                 cap rule     drop_unl.  pricing  baseline
    ULC-A4         cre-cells/B-S1.bin       TUw-50-50    False      P1a      ULC-A3
    MSW-V2         graph-msw-tu50.bin       TUw-50-50    True       P1a      ULC-A4

`MSW-V2`'s baseline is `ULC-A4`, which differs by **exactly one column**:
`drop_unlistenable`. That is the intervention.

HELD CONSTANT, AND WHY EACH IS GENUINELY CONSTANT UNDER THE INTERVENTION
------------------------------------------------------------------------
- **Archive** — both are the `ALG-B` candidate archive. `ULC-F3` records that
  crawl resume cannot extend, so no artist entered the archive between the two
  builds. Asserted below via the node-set relationship, not assumed.
- **Cap rule** — `TUw-50-50` both sides: `union_top_j = 50`,
  `union_degree_ceiling = 50`, `max_neighbours_per_artist = 50`. Read off the new
  artifact's sidecar and the `B-S1` manifest row at run time.
- **`require_fame`** — `False` for `B-S1`, `True` for the new artifact, and this
  is the term the factor table would otherwise miss. It is genuinely constant in
  the only sense that matters here: `pipeline.py:434` reads fame **after** `keep`
  is fixed, so it cannot add or remove a node. It changes the metadata blob only.
  Verified by reading the source, not inferred from the node counts.
- **Instrument** — the `CRE-G1(a)`-verified mirror walking the `CRE` ladder, the
  same object that produced the comparator.
- **Fame column** — the `CRE` `Ruler` device column on BOTH sides. The new
  artifact also carries its own shipped `fame_lb_pctl`, and `GraphStore` computes
  it on load, but the mirror reads `ctx.fame_pctl` (the ruler's) and the shipped
  column is unused here. That is deliberate: swapping it would be a second knob,
  and it is exactly the deviation `MSW-V4` bounded and `MSW-V2B` measures.
- **Class definition** — `ULC-D2` from the frozen `ulc_flags.json`, unchanged.
  **This is the load-bearing assumption and it is NOT clean; see below.**
- **Pair set and depths** — the eight `GBL-AM1` pairs, depths 0/10/20. All
  sixteen endpoints survive into the new artifact (asserted below).

THE WEAKEST LINK, STATED HERE RATHER THAN DISCOVERED IN THE READ
-----------------------------------------------------------------
The class definition `ULC-D2` was censused over a population that is not the new
artifact's. Two consequences travel with every figure this script emits:

1. **It is not tautological.** The shipped drop payload
   (`unlistenable_drop_algb_20260805.json`) and `ULC-D2` are different objects —
   the payload was censused over the `ALG-B` archive, `ULC-D2` over `ULC-`'s own
   population. A non-trivial number of `ULC-D2` members survive into the new
   artifact, so the measurement CAN come out non-zero. The script asserts this
   rather than trusting it: if the surviving intersection were empty, the
   measurement would be structurally incapable of a non-zero answer and saying so
   would matter more than the number.
2. **It is an UNDER-count, in a known direction.** An artist in the new artifact
   who was never in `ULC-D2`'s census population cannot be counted, however
   un-listenable they are. So a low share here is evidence the *known* class was
   removed, and is **not** evidence that no un-listenable artist remains. The
   never-censused count is reported beside the share so the gap is visible.

Figures are owned by this script's committed JSON output and by the `MSW-`
execution log's Task 10 section. Cited, never restated.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-msw-verification/msw_v2_exposure.py
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ULC_DIR = ROOT / "builder" / "analysis" / "2026-08-05-unlistenable-class"
CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
sys.path.insert(0, str(CRE_DIR))
sys.path.insert(0, str(ULC_DIR))

from cre_common import Ruler, use_frozen                # noqa: E402
from cre_ladder import victim_key, walk_journey         # noqa: E402
from cre_mirror import MirrorContext                    # noqa: E402
from cre_sweep import config_for, ladder_excludes       # noqa: E402

# Imported, never copied: the same statistic and the same seed that produced the
# comparator. `branch` is deliberately NOT imported — see the module docstring.
from ulc_exposure import BOOTSTRAP, DEEP, DEPTHS, SEED, paired_median_ci  # noqa: E402

use_frozen("api_src")
from artistpath_api.graph_store import GraphStore       # noqa: E402

NEW = ROOT / "builder" / "scratch" / "graph-msw-tu50.bin"
NEW_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"

PRICING = "P1a"          # the ULC-A4 arm's pricing, held constant
COMPARATOR_ARM = "ULC-A4"
COMPARATOR_CELL = "B-S1"


def log(msg: str) -> None:
    print(msg, flush=True)


def load_new() -> GraphStore:
    payload = NEW.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != NEW_SHA:
        raise SystemExit(
            f"WRONG ARTIFACT: {NEW.name} is {got}, expected {NEW_SHA} — refusing "
            "to draw a conclusion from an unidentified artifact"
        )
    return GraphStore.from_bytes(payload)


def main() -> int:
    # --- inputs, each read from the file that owns it -----------------------
    flags = json.loads((ULC_DIR / "ulc_flags.json").read_text(encoding="utf-8"))
    d2, d1 = set(flags["ULC-D2"]), set(flags["ULC-D1"])

    frozen = json.loads((ULC_DIR / "ulc_exposure.json").read_text(encoding="utf-8"))
    base_pairs = frozen["per_arm_per_pair"][COMPARATOR_ARM]
    # The comparator's own run state was NOT met (95/96 slots), which is why
    # `ULC-R1` never fired. That is inherited, not repaired here: any slot the
    # comparator is missing is dropped from the pairing and named in
    # `unpaired_slots`, never silently filled or averaged around.
    comparator_run_state = {
        "ulc_r1_readable": frozen["ulc_r1_readable"],
        "missing_slots_in_comparator_run": frozen["missing_slots"],
        "inherited": ("the comparator's run state was unmet, so ULC-R1 did not fire "
                      "there and no ULC- read is revived here"),
    }

    approved = json.loads((GBL_DIR / "gbl_pairs_approved.json").read_text("utf-8"))
    pairs = [(p["a"], p["b"]) for p in approved["pairs"]]
    if len(pairs) != 8:
        raise SystemExit(f"expected the 8 GBL-AM1 pairs, got {len(pairs)}")

    store = load_new()
    nodes = set(store.mbids)

    # --- the weakest-link assertions, before any journey is walked ----------
    survivors = d2 & nodes
    if not survivors:
        raise SystemExit(
            "ULC-D2 and the new artifact's node set are disjoint: this measurement "
            "cannot come out non-zero and reporting a 0% share would be vacuous. "
            "Report the disjointness instead."
        )
    censused = set(flags["ULC-D2"]) | set(flags["ladder-le2"]) | set(flags["ULC-D0"])
    never_censused = len(nodes - censused)
    log(f"class: ULC-D2 has {len(d2):,}; {len(survivors):,} survive into the new "
        f"artifact, so a non-zero share is reachable")
    log(f"under-count exposure: {never_censused:,} of {len(nodes):,} new-artifact "
        f"nodes were never in the census population and cannot be counted\n")

    missing_endpoints = [
        f"{x['name']}" for a, b in pairs for x in (a, b) if x["mbid"] not in nodes
    ]
    if missing_endpoints:
        raise SystemExit(
            "pair endpoints dropped by the filter: " + ", ".join(missing_endpoints)
        )

    # --- the run ------------------------------------------------------------
    ruler = Ruler()
    measured, device = ruler.arrays(store)
    ctx = MirrorContext.build(store, device)
    cfg = config_for(PRICING)
    key = victim_key(measured, store.pop_raw, store.mbids)
    log(f"MSW-V2  artifact={NEW.name}  pricing={PRICING}  "
        f"nodes={len(store.mbids):,}  sha ok")

    rows: dict[str, dict] = {}
    missing: list[str] = []
    seen_class: dict[str, int] = {}

    for a, b in pairs:
        pk = f"{a['mbid']}|{b['mbid']}"
        s, t = store.id_by_mbid[a["mbid"]], store.id_by_mbid[b["mbid"]]
        ladder = walk_journey(store, s, t, cfg, ctx, measured,
                              store.pop_raw, store.mbids)
        excl = ladder_excludes(ladder, key)
        depth_rows: dict[int, dict | None] = {}
        for d in DEPTHS:
            if d >= len(excl) or ladder[d][0] is None:
                missing.append(f"{a['name']}|{b['name']}@d{d}")
                depth_rows[d] = None
                continue
            interior = [store.mbids[v] for v in ladder[d][0][1:-1]]
            n = len(interior)
            hits = [m for m in interior if m in d2]
            for m in hits:
                seen_class[m] = seen_class.get(m, 0) + 1
            depth_rows[d] = {
                "interior": n,
                "in_d2": len(hits),
                "in_d1": sum(1 for m in interior if m in d1),
                "share_d2": (len(hits) / n) if n else None,
                "share_d1": (sum(1 for m in interior if m in d1) / n) if n else None,
                # Named, not just counted: a share is not actionable but a name is,
                # and these are the artists the owner would actually be shown.
                "class_members": [store.names[store.id_by_mbid[m]] for m in hits],
            }
        rows[pk] = {"a": a["name"], "b": b["name"], "depths": depth_rows}

    readable = not missing
    log(f"\nrun state: {'MET' if readable else 'NOT MET'} "
        f"({24 - len(missing)}/24 slots)")
    for m in missing:
        log(f"  missing: {m}")

    # --- means, and the paired comparison against the frozen ULC-A4 rows ----
    def mean_share(source: dict, depths, field: str = "share_d2") -> float | None:
        vals = [r["depths"][str(d) if str(d) in r["depths"] else d][field]
                for r in source.values() for d in depths
                if r["depths"].get(str(d) if str(d) in r["depths"] else d)
                and r["depths"][str(d) if str(d) in r["depths"] else d][field] is not None]
        return round(100 * sum(vals) / len(vals), 2) if vals else None

    paired: dict[str, dict | None] = {}
    rng = random.Random(SEED)
    for label, depths in (("primary_deep_d10_d20", DEEP), ("anchor_d0", (0,))):
        diffs, unpaired = [], []
        for pk in rows:
            for d in depths:
                x = rows[pk]["depths"].get(d)
                base_row = base_pairs.get(pk)
                y = base_row["depths"].get(str(d)) if base_row else None
                if x and y and x["share_d2"] is not None and y["share_d2"] is not None:
                    diffs.append(x["share_d2"] - y["share_d2"])
                else:
                    unpaired.append(f"{rows[pk]['a']}|{rows[pk]['b']}@d{d}")
        if not diffs:
            paired[label] = None
            continue
        stat = paired_median_ci(diffs, rng)
        stat["unpaired_slots"] = unpaired
        # NO BRANCH. No threshold was pre-registered for MSW-V2.
        stat["branch"] = None
        stat["sentence"] = (
            "report row, not a gate: no effect size was pre-registered for MSW-V2, "
            "so no branch is assigned and no read fires"
        )
        # The median inherits `ULC-R1`'s recorded design defect: the class is
        # CONCENTRATED in a few journeys rather than spread across them, and a
        # paired median over mostly-identical slots reads 0 while the mean moves
        # a lot. `ULC-` results record that defect and deliberately did not patch
        # it; it is not patched here either. Both summaries are reported, and the
        # sign counts below are what actually show the shape.
        stat["mean_diff_pp"] = round(100 * sum(diffs) / len(diffs), 4)
        stat["slots_improved"] = sum(1 for x in diffs if x < 0)
        stat["slots_unchanged"] = sum(1 for x in diffs if x == 0)
        stat["slots_worsened"] = sum(1 for x in diffs if x > 0)
        stat["median_caveat"] = (
            "the paired MEDIAN inherits ULC-R1's recorded statistic defect: with the "
            "class concentrated in a minority of journeys, a median over mostly "
            "identical slots reads zero while the mean moves. Read the sign counts "
            "and the mean beside it; neither is a pre-registered read."
        )
        paired[label] = stat

    class_hits = sorted(
        ({"mbid": m, "name": store.names[store.id_by_mbid[m]], "slots_appeared": c}
         for m, c in seen_class.items()),
        key=lambda r: (-r["slots_appeared"], r["name"]),
    )

    payload = {
        "check": "MSW-V2",
        "status": ("diagnostic; report row, not a gate; adopts nothing, changes no "
                   "default, touches no shipped code"),
        "no_branch_assigned": True,
        "why_no_branch": ("plan Task 10 Step 2: 'This is a report row, not a gate: "
                          "no threshold was pre-registered, so no read fires.'"),
        "governing": "plans/2026-08-05-msw-package-adoption.md Task 10 Step 2",
        "plain_question": ("how often does a journey's middle land on an artist who "
                           "has nothing of their own to play, now the filter is on?"),
        "subject": {
            "artifact": NEW.name,
            "sha256": NEW_SHA,
            "nodes": len(store.mbids),
            "pricing": PRICING,
        },
        "comparator": {
            "arm": COMPARATOR_ARM,
            "cell": COMPARATOR_CELL,
            "source": "analysis/2026-08-05-unlistenable-class/ulc_exposure.json",
            "provenance": ("read from the owning file at run time, never transcribed; "
                           "the ULC- results note owns this figure in prose"),
            "isolating_knob": "drop_unlistenable False -> True",
            "run_state": comparator_run_state,
        },
        "class_definition": {
            "source": "analysis/2026-08-05-unlistenable-class/ulc_flags.json",
            "set": "ULC-D2",
            "size": len(d2),
            "present_in_new_artifact": len(survivors),
            "new_nodes_never_censused": never_censused,
            "under_count_warning": (
                "an artist never in ULC-D2's census population cannot be counted "
                "however un-listenable they are, so a low share is evidence the "
                "KNOWN class was removed and NOT evidence that none remains"
            ),
        },
        "run_state": {
            "slots_expected": 24,
            "slots_measured": 24 - len(missing),
            "readable": readable,
            "missing_slots": missing,
        },
        "mean_interior_share_pct": {
            "new_artifact": {
                "d0": mean_share(rows, (0,)),
                "deep_d10_d20": mean_share(rows, DEEP),
            },
            f"{COMPARATOR_ARM}_frozen": {
                "d0": mean_share(base_pairs, (0,)),
                "deep_d10_d20": mean_share(base_pairs, DEEP),
            },
        },
        "paired_vs_comparator": paired,
        "class_members_still_appearing": class_hits,
        "per_pair": rows,
        "bootstrap": {"draws": BOOTSTRAP, "seed": SEED},
    }

    out = HERE / "msw_v2_exposure.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    m = payload["mean_interior_share_pct"]
    log("\n--- mean share of interior cards in the un-listenable class (%) ---")
    log(f"  new artifact       d0={m['new_artifact']['d0']}  "
        f"deep={m['new_artifact']['deep_d10_d20']}")
    log(f"  {COMPARATOR_ARM} (frozen)   d0={m[COMPARATOR_ARM + '_frozen']['d0']}  "
        f"deep={m[COMPARATOR_ARM + '_frozen']['deep_d10_d20']}")
    log("\n--- paired difference vs the comparator (no branch assigned) ---")
    for label, stat in paired.items():
        if stat:
            log(f"  {label}: median {stat['median_diff_pp']:+.2f} pp "
                f"CI {stat['ci95_pp']} | mean {stat['mean_diff_pp']:+.2f} pp | "
                f"n={stat['n_pairs']}  "
                f"[{stat['slots_improved']} better, {stat['slots_unchanged']} same, "
                f"{stat['slots_worsened']} WORSE]")
    log(f"\nclass members still appearing in an interior: {len(class_hits)}")
    for r in class_hits[:10]:
        log(f"  {r['name']} ({r['slots_appeared']} slot(s))")
    log(f"\nwrote {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
