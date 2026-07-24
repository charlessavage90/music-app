"""Stage A walker: routes every arm over every pair and records the snapshot paths.

This produces *paths*, not scores. Fame resolution and the C1-C6 criteria are
separate steps (`fame.py`, `score.py`) so that the expensive, network-bound half is
not entangled with the deterministic, offline half — and so a scoring bug does not
cost a re-route.

Protocol, all from pre-registration §1.2:
  - scripted all-`known` walk, 20 bypasses
  - victim = most-popular interior in in-graph popularity, ties -> lowest node id
  - walked INDEPENDENTLY per arm (each arm bypasses its own paths)
  - guard G on in every arm including P
  - snapshots at d in {0,1,2,3,5,7,10,15,20}

**Guard-infeasible cells (analyst D7).** A cell is infeasible when the walk cannot
continue — no path, or a path with no interior to bypass. D7's success condition is
that such a cell is **dropped from ALL arms uniformly and reported**, so that
missingness cannot correlate with arm. This module records feasibility per cell; the
uniform drop is applied here, in `drop_infeasible_uniformly`, and the dropped set is
written to the output for the scorer to honour and the report to name.

Run from `api/` (the mirror imports `artistpath_api`):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-24-track2-arm-scorer/run_arms.py --smoke
    ... and without --smoke for the full stage-1 grid (~40-50 min).
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "builder" / "analysis" / "2026-07-23-track2-sweep"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

from arms import MAX_DEPTH, SNAPSHOTS, STAGE1, Arm  # noqa: E402
from verify_mirror import ANALYSIS_PAIRS, HELD_OUT_PAIRS  # noqa: E402


def resolve_names(store, pop) -> dict[str, int]:
    """Name -> node id, taking the highest-popularity duplicate.

    Same rule as `run_a0.py` and the probe scripts: the graph carries known
    duplicate names (log §2.2), and every prior script resolves them this way.
    Changing it here would silently re-point a pre-registered endpoint.
    """
    by_name: dict[str, int] = {}
    for i, nm in enumerate(store.names):
        prev = by_name.get(nm)
        if prev is None or pop[i] > pop[prev]:
            by_name[nm] = i
    return by_name


def walk(store, src, dst, cfg, ctx, pop, find_path_mirror, Exclusion, KNOWN, stats):
    """All-`known` walk. Returns paths[d] for d in 0..MAX_DEPTH; None once infeasible.

    The list is always MAX_DEPTH+1 long — an infeasible walk pads with None rather
    than ending short, so every arm's array is the same shape and a cell is either
    a path or explicitly absent.
    """
    excludes: list = []
    out: list[list[int] | None] = []
    for _ in range(MAX_DEPTH + 1):
        path = find_path_mirror(store, src, dst, excludes, cfg, ctx, stats)
        out.append(path)
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break
        victim = min(interior, key=lambda v: (-pop[v], v))
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    out.extend([None] * (MAX_DEPTH + 1 - len(out)))
    return out


def drop_infeasible_uniformly(per_arm: dict[str, dict[str, list]]) -> list[str]:
    """Analyst D7: a cell infeasible in ANY arm is dropped from EVERY arm.

    Without this, an arm that keeps a pair alive one bypass longer than another is
    scored on a cell its rival does not have — arm-correlated missingness, which is
    the selection confound the guard decision (§4) exists to prevent, returning by
    the back door. Returns the dropped cell keys, for reporting.
    """
    dropped: set[str] = set()
    for arm_paths in per_arm.values():
        for pair_key, paths in arm_paths.items():
            for d in SNAPSHOTS:
                if paths[d] is None:
                    dropped.add(f"{pair_key}@d{d}")
    for arm_paths in per_arm.values():
        for pair_key, paths in arm_paths.items():
            for d in SNAPSHOTS:
                if f"{pair_key}@d{d}" in dropped:
                    paths[d] = None
    return sorted(dropped)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="P only, on one pair — validates the walker without "
                         "generating any experimental arm result")
    ap.add_argument("--out", default=str(HERE / "paths.json"))
    args = ap.parse_args()

    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}")

    from artistpath_api.graph_store import GraphStore
    from artistpath_api.pathfinding import KNOWN, Exclusion

    from mirror import MirrorContext, find_path_mirror

    store = GraphStore.load(GRAPH)
    ctx = MirrorContext.build(store)
    pop = np.asarray(store.pop_raw, dtype=np.float64)
    by_name = resolve_names(store, pop)

    arms: list[Arm] = [a for a in STAGE1 if a.name == "P"] if args.smoke else STAGE1
    pairs = ANALYSIS_PAIRS[:1] if args.smoke else ANALYSIS_PAIRS + HELD_OUT_PAIRS
    held_out = set() if args.smoke else {f"{a} -> {b}" for a, b in HELD_OUT_PAIRS}

    missing = [n for a, b in pairs for n in (a, b) if n not in by_name]
    assert not missing, f"endpoints absent from the artifact: {missing}"

    print(f"{len(arms)} arm(s) x {len(pairs)} pair(s) x {MAX_DEPTH + 1} depths"
          f"{'   [SMOKE]' if args.smoke else ''}\n")

    per_arm: dict[str, dict[str, list]] = {}
    arm_stats: dict[str, dict[str, int]] = {}
    t0 = time.time()

    for arm in arms:
        stats = {"examined": 0, "floor_active": 0}
        paths_by_pair: dict[str, list] = {}
        for a, b in pairs:
            paths = walk(store, by_name[a], by_name[b], arm.cfg, ctx, pop,
                         find_path_mirror, Exclusion, KNOWN, stats)
            paths_by_pair[f"{a} -> {b}"] = paths
        per_arm[arm.name] = paths_by_pair
        arm_stats[arm.name] = stats
        # PR-A asks for this alongside identity, so "the term is firing but the
        # outcome is unchanged" is visible rather than inferred.
        frac = 100.0 * stats["floor_active"] / max(1, stats["examined"])
        print(f"  {arm.name:<4} done  ({time.time() - t0:6.1f}s)   "
              f"floor term live on {frac:5.2f} % of {stats['examined']:,} relaxations")

    dropped = drop_infeasible_uniformly(per_arm)

    out = {
        "artifact_sha256": digest,
        "smoke": args.smoke,
        "snapshots": list(SNAPSHOTS),
        "max_depth": MAX_DEPTH,
        "arms": [a.name for a in arms],
        "pairs": [f"{a} -> {b}" for a, b in pairs],
        "held_out_pairs": sorted(held_out),
        "dropped_cells_d7": dropped,
        "arm_stats": arm_stats,
        # Snapshots only — the full 21-depth walk is an implementation detail, and
        # writing every depth would quadruple the file for no scored use.
        "paths": {
            arm: {pair: {str(d): paths[d] for d in SNAPSHOTS}
                  for pair, paths in by_pair.items()}
            for arm, by_pair in per_arm.items()
        },
        "node_names": {},
    }
    seen = {n for by_pair in per_arm.values() for paths in by_pair.values()
            for d in SNAPSHOTS if paths[d] for n in paths[d]}
    out["node_names"] = {str(n): store.names[n] for n in sorted(seen)}
    out["node_mbids"] = {str(n): store.mbids[n] for n in sorted(seen)}

    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False),
                              encoding="utf-8")
    print(f"\nwrote {args.out}  ({len(seen):,} distinct nodes across all snapshots)")

    if dropped:
        print(f"\nD7 — guard-infeasible cells, dropped from ALL arms ({len(dropped)}):")
        for c in dropped:
            print(f"  - {c}")
    else:
        print("\nD7: no guard-infeasible cells.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
