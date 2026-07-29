"""Track 3b walker: routes every arm over every pair, records snapshot paths.

Produces *paths*, not scores — the Track 2 split, kept via `run_arms_t3.py`'s pattern.
Nothing is reimplemented: `walk` and `drop_infeasible_uniformly` come from the committed
`../2026-07-24-track2-arm-scorer/run_arms.py`, the cost function is the committed
`mirror.py` with TB-P4's thresholded toll.

**Arms (prereg §2 as amended by TB-P1 F1).** One axis, `w_known_thresh_pctl`:

    P       0.00    production, guard G on — the baseline
    TB-A1   0.10    ~4x  w_hop realised per median above-knee interior at k=10
    TB-A2   0.30    ~13x
    TB-A3   1.00    ~43x

**Pairs.** The 12 scored pairs from Track 3's frozen `pairs_v2.json` (8 analysis / 4
held-out) plus the 4 all-famous anchors, walked for TB-G2 and the descriptive table
only.

**Gates checked here:** TB-G2 (every arm's d0 byte-identical to P's, anchors included)
plus its non-vacuity half (d1 must differ from P somewhere per arm, or the device is
not reaching the walk). **Counters (§0's victim-rule row, TB-P1 F4):** sub-decile
victims per arm per depth, recomputed from each arm's own paths by the walker's victim
rule.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-track3b-thresholded-toll/run_arms_tb.py
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
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-24-track2-arm-scorer"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
T3 = ROOT / "builder" / "analysis" / "2026-07-28-track3-depth-descent"

WS = {"P": 0.0, "TB-A1": 0.10, "TB-A2": 0.30, "TB-A3": 1.00}
KNEE = 0.90


def in_dir(arg: str) -> Path:
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename in {HERE}, got {arg!r}")
    return HERE / arg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="tb_paths.json",
                    help="output filename, in this directory")
    args = ap.parse_args()

    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # TB-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from arms import MAX_DEPTH, SNAPSHOTS
    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import drop_infeasible_uniformly, walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pctl = ctx.pctl
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    doc = json.loads((T3 / "pairs_v2.json").read_text(encoding="utf-8"))
    assert doc["artifact_sha256"] == digest, "pairs_v2.json is from a different artifact"
    scored = [(e["pair"], e["src"], e["dst"], e["split"], e["group"])
              for split, key in (("analysis", "analysis_pairs"),
                                 ("held_out", "held_out_pairs"))
              for e in ({**x, "split": split} for x in doc[key])]
    anchors = [(p, *p.split(" -> "), "anchor", "carry_over")
               for p in doc["unscored_anchor_pairs"]]
    pairs = scored + anchors

    missing = [n for _, a, b, _, _ in pairs for n in (a, b) if n not in by_name]
    assert not missing, f"endpoints absent from the artifact: {missing}"

    base = SweepConfig.production().with_(guard_min_intermediary=True)
    print(f"{len(WS)} arm(s) x {len(pairs)} pair(s) "
          f"({len(scored)} scored + {len(anchors)} unscored anchors) "
          f"x {MAX_DEPTH + 1} depths\n")

    per_arm: dict[str, dict[str, list]] = {}
    arm_stats: dict[str, dict[str, int]] = {}
    victim_stats: dict[str, dict] = {}
    t0 = time.time()
    for arm, w in WS.items():
        cfg = base if w == 0.0 else base.with_(w_known_thresh_pctl=w)
        stats = {"examined": 0, "floor_active": 0, "guard_fired": 0}
        by_pair: dict[str, list] = {}
        for key, a, b, _, _ in pairs:
            by_pair[key] = walk(store, by_name[a], by_name[b], cfg, ctx, pop,
                                find_path_mirror, Exclusion, KNOWN, stats)
        per_arm[arm] = by_pair
        arm_stats[arm] = stats

        # §0's victim-rule counter (TB-P1 F4): victims recomputed from this arm's own
        # paths by the walker's rule; classified against the knee.
        sub_by_depth = [0] * MAX_DEPTH
        total_by_depth = [0] * MAX_DEPTH
        for key, _, _, split, _ in pairs:
            if split == "anchor":
                continue
            for k, p in enumerate(by_pair[key][:MAX_DEPTH]):
                if p is None or not p[1:-1]:
                    break
                victim = min(p[1:-1], key=lambda v: (-pop[v], v))
                total_by_depth[k] += 1
                if float(pctl[victim]) < KNEE:
                    sub_by_depth[k] += 1
        victim_stats[arm] = {"sub_decile_victims": sum(sub_by_depth),
                             "victims_total": sum(total_by_depth),
                             "sub_decile_by_depth": sub_by_depth}
        frac = 100.0 * stats["floor_active"] / max(1, stats["examined"])
        print(f"  {arm:<6} w={w:<5} done ({time.time() - t0:6.1f}s)   "
              f"floor live {frac:5.2f} %   guard G fired {stats['guard_fired']}   "
              f"sub-decile victims {victim_stats[arm]['sub_decile_victims']}"
              f"/{victim_stats[arm]['victims_total']}")

    # ---- TB-G2: first path untouched, on every pair including anchors ----
    g2 = [key for key in per_arm["P"]
          for arm in WS if arm != "P" and per_arm[arm][key][0] != per_arm["P"][key][0]]
    print(f"\nTB-G2 — d0 identical to P on every arm x pair: "
          f"{'PASS' if not g2 else 'FAIL on ' + ', '.join(sorted(set(g2)))}")

    # ---- TB-G2 non-vacuity: d1 must differ from P somewhere, per arm ----
    for arm in WS:
        if arm == "P":
            continue
        n_diff = sum(1 for key in per_arm["P"]
                     if per_arm[arm][key][1] != per_arm["P"][key][1])
        print(f"  non-vacuity: {arm} d1 differs from P on {n_diff}/{len(per_arm['P'])} "
              f"pairs {'(OK)' if n_diff else '(FAIL — device not reaching the walk)'}")

    dropped = drop_infeasible_uniformly(per_arm)
    print(f"A13 uniform drop: {len(dropped)} guard-infeasible cell(s)"
          + (f" — {', '.join(dropped)}" if dropped else ""))

    seen = {n for by_pair in per_arm.values() for paths in by_pair.values()
            for d in SNAPSHOTS if paths[d] for n in paths[d]}
    out = {
        "artifact_sha256": digest,
        "snapshots": list(SNAPSHOTS),
        "max_depth": MAX_DEPTH,
        "arms": list(WS),
        "ws": WS,
        "knee": KNEE,
        "pairs": [k for k, *_ in pairs],
        "splits": {k: s for k, _, _, s, _ in pairs},
        "groups": {k: g for k, _, _, _, g in pairs},
        "unscored_anchor_pairs": [k for k, *_ in anchors],
        "tb_g2_pass": not g2,
        "dropped_cells_d7": dropped,
        "arm_stats": arm_stats,
        "victim_stats": victim_stats,
        "paths": {arm: {pair: {str(d): paths[d] for d in SNAPSHOTS}
                        for pair, paths in by_pair.items()}
                  for arm, by_pair in per_arm.items()},
        "node_names": {str(n): store.names[n] for n in sorted(seen)},
        "node_mbids": {str(n): store.mbids[n] for n in sorted(seen)},
    }
    out_path = in_dir(args.out)
    out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out_path}  ({len(seen):,} distinct nodes across all snapshots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
