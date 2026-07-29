"""Track 3 Stage A walker: routes every arm over every pair, records snapshot paths.

Produces *paths*, not scores — fame resolution and the criteria are separate steps, so
a scoring bug does not cost a re-route (the Track 2 split, kept).

**Nothing here is reimplemented.** `walk` and `drop_infeasible_uniformly` are imported
from the committed `../2026-07-24-track2-arm-scorer/run_arms.py`, and the cost function
is the committed `mirror.py` with DD-P4's ramp. This module exists rather than a
`--pairs-file` flag on the Track 2 walker so that **no committed Track 2 file changes**
and every Track 2 figure stays reproducible from its own script unchanged.

**Arms (prereg §2 as amended by DD-D4).** DD-A4 and DD-A5 are struck: with the re-drawn
pair set the floor dies at k = 3 while the shallowest scored depth is d5, so their cost
functions are bit-identical to DD-A2's and DD-A3's at every scored depth, and they would
additionally fail DD-G2. See the execution log §3.

    P       w_known_ramp_pctl = 0.00    production, guard G on — the baseline
    DD-A1                       0.01    5x  w_hop at k=10, pctl=1
    DD-A2                       0.03    15x
    DD-A3                       0.10    50x

**Pairs.** The 12 scored pairs from `pairs_v2.json` (8 analysis / 4 held-out), plus the
4 all-famous anchors walked for **DD-G2 only** and excluded from every criterion — they
cannot pass DD-P1 by any choice of pairs (execution log §2).

**DD-G2** — every arm's d0 path must be byte-identical to P's on every pair, anchors
included. Checked here and reported; §3 says a gate failure voids the run.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-track3-depth-descent/run_arms_t3.py
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

RAMPS = {"P": 0.0, "DD-A1": 0.01, "DD-A2": 0.03, "DD-A3": 0.10}


def in_dir(arg: str) -> Path:
    """Resolve `arg` as a bare filename inside this directory.

    `--out` names an output file *in this directory*; a separator or parent reference
    is a mistake rather than a use case. Also closes the path-traversal finding Snyk
    raises on the argparse -> path flow.
    """
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename in {HERE}, got {arg!r}")
    return HERE / arg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="t3_paths.json",
                    help="output filename, in this directory")
    args = ap.parse_args()

    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"          # DD-G3
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from arms import MAX_DEPTH, SNAPSHOTS
    from mirror import MirrorContext, SweepConfig, find_path_mirror
    from run_arms import drop_infeasible_uniformly, walk

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)

    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i

    doc = json.loads((HERE / "pairs_v2.json").read_text(encoding="utf-8"))
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
    print(f"{len(RAMPS)} arm(s) x {len(pairs)} pair(s) "
          f"({len(scored)} scored + {len(anchors)} unscored anchors) "
          f"x {MAX_DEPTH + 1} depths\n")

    per_arm: dict[str, dict[str, list]] = {}
    arm_stats: dict[str, dict[str, int]] = {}
    t0 = time.time()
    for arm, w in RAMPS.items():
        cfg = base if w == 0.0 else base.with_(w_known_ramp_pctl=w)
        stats = {"examined": 0, "floor_active": 0, "guard_fired": 0}
        by_pair: dict[str, list] = {}
        for key, a, b, _, _ in pairs:
            by_pair[key] = walk(store, by_name[a], by_name[b], cfg, ctx, pop,
                                find_path_mirror, Exclusion, KNOWN, stats)
        per_arm[arm] = by_pair
        arm_stats[arm] = stats
        frac = 100.0 * stats["floor_active"] / max(1, stats["examined"])
        print(f"  {arm:<6} w={w:<5} done ({time.time() - t0:6.1f}s)   "
              f"floor live on {frac:5.2f} % of {stats['examined']:,} relaxations   "
              f"guard G fired {stats['guard_fired']}")

    # ---- DD-G2: first path untouched, on every pair including anchors ----
    g2 = [key for key in per_arm["P"]
          for arm in RAMPS if arm != "P" and per_arm[arm][key][0] != per_arm["P"][key][0]]
    print(f"\nDD-G2 — d0 identical to P on every arm x pair: "
          f"{'PASS' if not g2 else 'FAIL on ' + ', '.join(sorted(set(g2)))}")

    dropped = drop_infeasible_uniformly(per_arm)
    print(f"A13 uniform drop: {len(dropped)} guard-infeasible cell(s)"
          + (f" — {', '.join(dropped)}" if dropped else ""))

    seen = {n for by_pair in per_arm.values() for paths in by_pair.values()
            for d in SNAPSHOTS if paths[d] for n in paths[d]}
    out = {
        "artifact_sha256": digest,
        "snapshots": list(SNAPSHOTS),
        "max_depth": MAX_DEPTH,
        "arms": list(RAMPS),
        "ramps": RAMPS,
        "struck_arms": {"DD-A4": "identical to DD-A2 at every scored depth (DD-D4)",
                        "DD-A5": "identical to DD-A3 at every scored depth (DD-D4)"},
        "pairs": [k for k, *_ in pairs],
        "splits": {k: s for k, _, _, s, _ in pairs},
        "groups": {k: g for k, _, _, _, g in pairs},
        "unscored_anchor_pairs": [k for k, *_ in anchors],
        "dd_g2_pass": not g2,
        "dropped_cells_d7": dropped,
        "arm_stats": arm_stats,
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
