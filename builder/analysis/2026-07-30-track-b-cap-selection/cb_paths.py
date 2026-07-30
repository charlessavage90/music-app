"""CB-3: path-level metrics -- what the real router does on a candidate graph.

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md

Structural metrics (CB-2) say what a cap rule does to the GRAPH. They cannot
say what it does to a JOURNEY, and the journey is the product. This module
loads each cell through the API's own GraphStore and routes with the API's own
find_path -- no server, no network, no reimplementation of the cost function.

WHY THIS EXISTS AT ALL -- the unpriced half of MKS-5b
    Removing unbounded hubs is what capfix won its blind listen for, and no
    probe in this project has ever measured hub TRANSIT. GRT-P3 measured the
    benefit side of a looser cap (stranding falls) and explicitly priced no
    hub cost. This is that column. It is a proxy and not a substitute: there
    is NO validated offline proxy for listening coherence here, which CB-4
    must state plainly rather than let a hub-transit number stand in for.

⚠ w_degree_hub IS A LIVE INTERACTING TERM HERE, NOT A CONSTANT
    ApiConfig.w_degree_hub defaults to 0.0, and its comment records why: the
    2026-07-21 baseline found hub traversal topological, and the top-1%-by-
    degree set on the CURRENT CAPPED graph is largely insular micro-genre
    artists, so the term was tuned to no-op against that structure. A looser
    cap moves famous artists into the top-degree set. So the default is inert
    "for a reason the intervention removes" -- exactly the dormant-term shape
    CLAUDE.md's factor-table rule exists to catch. Every read here therefore
    NAMES the weight set it ran under, and CB-4 decides whether a second set
    runs and pre-commits its read.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_paths.py --gate
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path  # noqa: E402

from cb_metrics import ADOPTED, BANDS, fame_frame, top_degree_node_set  # noqa: E402

SCRATCH = ROOT / "builder" / "scratch"
SEED = 20260730
PAIRS_PER_BAND = 12


def draw_pairs(frame: dict[str, float], present: set[str],
               seed: int = SEED, per_band: int = PAIRS_PER_BAND) -> list[tuple[str, str]]:
    """Stratified pair draw over the adopted fame frame, fixed seed.

    One endpoint from each band paired with one from the lower half, plus
    within-band pairs at the top -- so the sample covers both the famous-pair
    class (DD-F1's territory) and the mixed-fame class where Track 3 found the
    only movement. Deterministic: same seed, same frame, same pairs.
    """
    rng = random.Random(seed)
    by_band: dict[str, list[str]] = {name: [] for name, _lo, _hi in BANDS}
    for mbid, pctl in sorted(frame.items()):
        if mbid not in present:
            continue
        for name, lo, hi in BANDS:
            if lo <= pctl < hi:
                by_band[name].append(mbid)
                break

    pairs: list[tuple[str, str]] = []
    lower = by_band["lower half"]
    for name, _lo, _hi in BANDS:
        pool = by_band[name]
        if len(pool) < 2 or not lower:
            continue
        for _ in range(per_band):
            a = rng.choice(pool)
            b = rng.choice(lower if name != "lower half" else pool)
            if a != b:
                pairs.append((a, b))
    # Famous-famous pairs: the class DD-F1 is about.
    top = by_band["top 0.1%"] + by_band["top 1%"]
    for _ in range(per_band):
        a, b = rng.choice(top), rng.choice(top)
        if a != b:
            pairs.append((a, b))
    return sorted(set(pairs))


def routable_everywhere(pairs, stores: dict[str, GraphStore]) -> list[tuple[str, str]]:
    """Keep only pairs whose BOTH endpoints exist in EVERY compared cell.

    Load-bearing: the two archives' crawl frontiers diverge by 31% (GRT-P4),
    so an unfiltered sample would compare routing against coverage and read
    a missing artist as a routing failure.
    """
    return [
        (a, b) for a, b in pairs
        if all(a in s.id_by_mbid and b in s.id_by_mbid for s in stores.values())
    ]


def _valid_walk(store: GraphStore, path: list[int]) -> bool:
    """Every consecutive pair is a real edge in this graph's CSR."""
    for u, v in zip(path, path[1:]):
        lo, hi = int(store.offsets[u]), int(store.offsets[u + 1])
        if v not in store.neighbours[lo:hi].tolist():
            return False
    return True


def route_sample(store: GraphStore, pairs: list[tuple[str, str]], cfg: ApiConfig,
                 frame: dict[str, float],
                 production_top_degree: set[str] | None = None) -> dict:
    """Route every pair and summarise. Returns paths too, for determinism checks."""
    own_top = top_degree_node_set(store)
    lengths: list[int] = []
    no_path = 0
    hub_own: list[float] = []
    hub_prod: list[float] = []
    sub_decile: list[float] = []
    invalid = 0
    routed: list[list[str]] = []

    for a, b in pairs:
        src, tgt = store.id_by_mbid[a], store.id_by_mbid[b]
        path = find_path(store, src, tgt, [], cfg)
        if path is None:
            no_path += 1
            routed.append([])
            continue
        if not _valid_walk(store, path):
            invalid += 1
        routed.append([store.mbids[i] for i in path])
        lengths.append(len(path))
        interior = [store.mbids[i] for i in path[1:-1]]
        if not interior:
            continue
        hub_own.append(sum(1 for m in interior if m in own_top) / len(interior))
        if production_top_degree is not None:
            hub_prod.append(
                sum(1 for m in interior if m in production_top_degree) / len(interior)
            )
        sub_decile.append(
            sum(1 for m in interior if frame.get(m, 1.0) < 0.90) / len(interior)
        )

    def mean(xs):
        return round(float(statistics.mean(xs)), 5) if xs else None

    return {
        # The weight set is IN THE OUTPUT, never assumed (see module docstring).
        "weights": {k: v for k, v in asdict(cfg).items()
                    if k.startswith("w_") or k.startswith("floor_")
                    or k.startswith("avoid_")},
        "pairs_attempted": len(pairs),
        "no_path": no_path,
        "invalid_walks": invalid,
        "path_length": {
            "median": float(statistics.median(lengths)) if lengths else None,
            "mean": mean(lengths),
            "max": max(lengths) if lengths else None,
        },
        # Fraction of interior nodes in a top-1%-by-DEGREE set -- the
        # established PathMetrics.top1pct_degree_frac quantity, reported
        # against two different sets and named for each.
        "top1pct_degree_frac_own": mean(hub_own),
        "top1pct_degree_frac_production": mean(hub_prod),
        "sub_decile_interior_share": mean(sub_decile),
        "_paths": routed,
    }


def gate() -> dict:
    """CB-3's instrument gate: determinism + walk validity (green), and a
    weight perturbation that must MOVE the paths (red).

    A router harness that returns the same answer under any weights is wired
    to nothing; the red half is what proves the cost function is reached.
    """
    frame = fame_frame()
    store = GraphStore.load(ADOPTED)
    present = set(store.id_by_mbid)
    pairs = draw_pairs(frame, present)[:20]
    prod_top = top_degree_node_set(store)

    first = route_sample(store, pairs, ApiConfig(), frame, prod_top)
    second = route_sample(store, pairs, ApiConfig(), frame, prod_top)
    deterministic = first["_paths"] == second["_paths"]
    valid = first["invalid_walks"] == 0

    # Red half: w_sim = 0 removes the similarity reward entirely, so the router
    # optimises a different function and must reach different artists.
    perturbed = route_sample(store, pairs, ApiConfig(w_sim=0.0), frame, prod_top)
    moved = sum(1 for a, b in zip(first["_paths"], perturbed["_paths"]) if a != b)

    passed = deterministic and valid and moved > 0
    print(f"GREEN determinism: {'PASS' if deterministic else 'FAIL'} "
          f"({len(pairs)} pairs, {first['no_path']} unroutable)")
    print(f"GREEN walk validity: {'PASS' if valid else 'FAIL'} "
          f"({first['invalid_walks']} invalid)")
    print(f"RED   w_sim=0 moves paths: {'PASS' if moved else 'FAIL'} "
          f"({moved}/{len(pairs)} changed)")
    print(f"      median length {first['path_length']['median']}, "
          f"hub-transit(own) {first['top1pct_degree_frac_own']}, "
          f"sub-decile interiors {first['sub_decile_interior_share']}")

    results = {
        "deterministic": deterministic,
        "walks_valid": valid,
        "paths_moved_under_perturbation": moved,
        "gate_passed": passed,
        "production_weights_summary": {
            k: v for k, v in first.items() if not k.startswith("_")
        },
    }
    (HERE / "cb_paths_gate.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    if not args.gate:
        raise SystemExit("cb_paths is a library; --gate runs its instrument check")
    out = gate()
    raise SystemExit(0 if out["gate_passed"] else 1)
