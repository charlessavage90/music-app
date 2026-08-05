"""ULC-S2 / ULC-C2 / ULC-R1: how often does the class land in a journey's interior?

Governing document: docs/superpowers/specs/2026-08-05-unlistenable-class-preregistration.md
-- section 3, plus ULC-AM5 (the primary read pools d10 and d20; d0 is an
excluded anchor). It governs wherever this script disagrees.

Runs only because ULC-G1 came out `separable` (ulc_census.json).

THE FOUR ARMS (section 3), and the ONLY comparisons they license (section 0.2)
    ULC-A1  E-S0  no ramp        --            baseline of A2
    ULC-A2  B-S0  no ramp        A2 - A1       the archive switch, production supply
    ULC-A3  E-S1  gentle ramp    --            baseline of A4
    ULC-A4  B-S1  gentle ramp    A4 - A3       the archive switch, trimmed union

  A4 - A1 differs by TWO knobs (archive AND supply rule) and licenses nothing
  (ULC-B6), notwithstanding that those are the two cells GBL- put side by side.
  The adopted production artifact (ULC-P5) is NOT an arm here: it carries
  neither drop flag, so it has no isolating baseline (section 0.3).

RUN STATE ULC-R1 PRESUPPOSES (section 4)
  All four arms at all three depths on all eight pairs -- 96 slots. A read taken
  on fewer is NOT ULC-R1 and this script will not label it one: it writes
  `ulc_r1_readable: false` and names the missing slots, rather than dropping
  pairs to make a number appear.

THE INSTRUMENT is the CRE-G1(a)-verified mirror walking the CRE ladder -- the
same object GBL- presented and CAU- audited. Nothing here touches shipped code.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-unlistenable-class/ulc_exposure.py
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
GBL_DIR = ROOT / "builder" / "analysis" / "2026-08-04-gentle-arm-blind-listen"
sys.path.insert(0, str(CRE_DIR))

from cre_common import Ruler                      # noqa: E402
from cre_gates import load_cell                   # noqa: E402
from cre_ladder import victim_key, walk_journey   # noqa: E402
from cre_mirror import MirrorContext              # noqa: E402
from cre_sweep import config_for, ladder_excludes  # noqa: E402

DEPTHS = (0, 10, 20)
DEEP = (10, 20)          # ULC-AM5: the primary read
EFFECT_PP = 2.0          # section 3.1, fixed before any count
BOOTSTRAP = 10_000
SEED = 20260805          # fixed so the CI is reproducible

ARMS = {
    "ULC-A1": {"cell": "E-S0", "pricing": "P0",  "baseline": None},
    "ULC-A2": {"cell": "B-S0", "pricing": "P0",  "baseline": "ULC-A1"},
    "ULC-A3": {"cell": "E-S1", "pricing": "P1a", "baseline": None},
    "ULC-A4": {"cell": "B-S1", "pricing": "P1a", "baseline": "ULC-A3"},
}


def log(msg: str) -> None:
    print(msg, flush=True)


def paired_median_ci(diffs: list[float], rng: random.Random) -> dict:
    """Percentile bootstrap over the paired differences."""
    n = len(diffs)
    point = statistics.median(diffs)
    boots = []
    for _ in range(BOOTSTRAP):
        boots.append(statistics.median([diffs[rng.randrange(n)] for _ in range(n)]))
    boots.sort()
    return {
        "n_pairs": n,
        "median_diff_pp": round(point * 100, 4),
        "ci95_pp": [round(boots[int(0.025 * BOOTSTRAP)] * 100, 4),
                    round(boots[int(0.975 * BOOTSTRAP) - 1] * 100, 4)],
    }


def branch(stat: dict) -> tuple[str, str]:
    """Section 3.1's branch table, applied exactly."""
    lo, hi = stat["ci95_pp"]
    excludes_zero = (lo > 0 and hi > 0) or (lo < 0 and hi < 0)
    d = stat["median_diff_pp"]
    if excludes_zero and d >= EFFECT_PP:
        return "worse_on_candidate", (
            "the new map puts more of these artists in the middle of your journeys")
    if excludes_zero and d <= -EFFECT_PP:
        return "better_on_candidate", (
            "the new map puts fewer of these artists in the middle of your journeys")
    return "no_detectable_difference", (
        "no difference big enough to change what you would see")


def main() -> None:
    flags = json.loads((HERE / "ulc_flags.json").read_text(encoding="utf-8"))
    d2 = set(flags["ULC-D2"])
    d1 = set(flags["ULC-D1"])
    log(f"ULC-D2 set: {len(d2):,} artists; ULC-D1 subset: {len(d1):,}")

    approved = json.loads((GBL_DIR / "gbl_pairs_approved.json").read_text("utf-8"))
    pairs = [(p["a"], p["b"]) for p in approved["pairs"]]
    if len(pairs) != 8:
        raise SystemExit(f"expected the 8 GBL-AM1 pairs, got {len(pairs)}")

    ruler = Ruler()
    per_arm: dict[str, dict] = {}
    missing: list[str] = []

    for arm, spec in ARMS.items():
        manifest, store = load_cell(spec["cell"])
        measured, device = ruler.arrays(store)
        ctx = MirrorContext.build(store, device)
        cfg = config_for(spec["pricing"])
        key = victim_key(measured, store.pop_raw, store.mbids)
        log(f"{arm}  cell={spec['cell']:5} pricing={spec['pricing']:4} "
            f"nodes={len(store.mbids):,} sha ok")

        rows: dict[str, dict] = {}
        for a, b in pairs:
            pk = f"{a['mbid']}|{b['mbid']}"
            s, t = store.id_by_mbid[a["mbid"]], store.id_by_mbid[b["mbid"]]
            ladder = walk_journey(store, s, t, cfg, ctx, measured,
                                  store.pop_raw, store.mbids)
            excl = ladder_excludes(ladder, key)
            depth_rows = {}
            for d in DEPTHS:
                if d >= len(excl) or ladder[d][0] is None:
                    missing.append(f"{arm}@{a['name']}|{b['name']}@d{d}")
                    depth_rows[d] = None
                    continue
                path = ladder[d][0]
                interior = [store.mbids[v] for v in path[1:-1]]
                n = len(interior)
                depth_rows[d] = {
                    "interior": n,
                    "in_d2": sum(1 for m in interior if m in d2),
                    "in_d1": sum(1 for m in interior if m in d1),
                    "share_d2": (sum(1 for m in interior if m in d2) / n) if n else None,
                    "share_d1": (sum(1 for m in interior if m in d1) / n) if n else None,
                }
            rows[pk] = {"a": a["name"], "b": b["name"], "depths": depth_rows}
        per_arm[arm] = rows

    readable = not missing
    log(f"\nrun state: {'MET' if readable else 'NOT MET'} "
        f"({96 - len(missing)}/96 slots)")
    for m in missing[:10]:
        log(f"  missing: {m}")

    reads = {}
    rng = random.Random(SEED)
    for arm, spec in ARMS.items():
        base = spec["baseline"]
        if base is None:
            continue
        entry: dict = {"comparison": f"{arm} - {base}",
                       "plain": ("does switching to the new map put more of these "
                                 "artists in the middle of your journeys?")}
        for label, depths in (("primary_deep_d10_d20", DEEP), ("anchor_d0", (0,))):
            diffs = []
            for pk in per_arm[arm]:
                for d in depths:
                    x = per_arm[arm][pk]["depths"].get(d)
                    y = per_arm[base][pk]["depths"].get(d)
                    if x and y and x["share_d2"] is not None and y["share_d2"] is not None:
                        diffs.append(x["share_d2"] - y["share_d2"])
            if not diffs:
                entry[label] = None
                continue
            stat = paired_median_ci(diffs, rng)
            if label == "primary_deep_d10_d20":
                if readable:
                    b, sentence = branch(stat)
                    stat["branch"], stat["sentence"] = b, sentence
                else:
                    stat["branch"] = None
                    stat["sentence"] = ("run state unmet -- this is NOT ULC-R1 and "
                                        "no branch is assigned")
            else:
                stat["branch"] = None
                stat["sentence"] = "anchor only; ULC-AM5 excludes d0 from the primary read"
            entry[label] = stat
        reads[arm] = entry

    def mean_share(arm: str, depths) -> float | None:
        vals = [r["depths"][d]["share_d2"]
                for r in per_arm[arm].values() for d in depths
                if r["depths"].get(d) and r["depths"][d]["share_d2"] is not None]
        return round(100 * sum(vals) / len(vals), 2) if vals else None

    payload = {
        "status": "diagnostic; adopts nothing, changes no default, no shipped code",
        "governing": "specs/2026-08-05-unlistenable-class-preregistration.md",
        "ulc_r1_readable": readable,
        "missing_slots": missing,
        "arms": {a: {"cell": s["cell"], "pricing": s["pricing"],
                     "baseline": s["baseline"]} for a, s in ARMS.items()},
        "mean_interior_share_pct": {
            a: {"d0": mean_share(a, (0,)), "deep_d10_d20": mean_share(a, DEEP)}
            for a in ARMS
        },
        "ULC_R1": reads,
        "per_arm_per_pair": per_arm,
        "effect_size_pp": EFFECT_PP,
        "bootstrap": {"draws": BOOTSTRAP, "seed": SEED},
    }
    out = HERE / "ulc_exposure.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")

    log("\n--- mean share of interior cards in the class (%) ---")
    for a in ARMS:
        m = payload["mean_interior_share_pct"][a]
        log(f"  {a} ({ARMS[a]['cell']:5} {ARMS[a]['pricing']:4})  "
            f"d0={m['d0']}  deep={m['deep_d10_d20']}")
    log("\n--- ULC-R1 ---")
    for arm, e in reads.items():
        p = e["primary_deep_d10_d20"]
        if p:
            log(f"  {e['comparison']}: median {p['median_diff_pp']:+.2f} pp, "
                f"CI {p['ci95_pp']} -> {p['branch']}")
    log(f"\nwrote {out.name}")


if __name__ == "__main__":
    main()
