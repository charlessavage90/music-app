"""Baseline path-quality measurement over a frozen panel of artist pairs.

Establishes the numbers the stage-2 review demanded: hub-traversal rate,
smoothness, interior popularity, path length — for the full cost function
versus a similarity-only router and plain BFS. If the full router scores like
similarity-only, the popularity machinery is inert (review finding CRITICAL-1);
the hub-traversal rate quantifies the hub-seeking degeneracy (CRITICAL-2).

Re-run this after any weight change. The panel is frozen (seed) so numbers are
comparable across runs. Success target from the review: hub-traversal well
below 90%, without wrecking smoothness.

Usage:
    cd api && UV_LINK_MODE=copy uv run python eval/run_baseline.py [graph.bin] [n_pairs]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import (
    bfs_shortest_path,
    hub_node_set,
    out_degree,
    path_metrics,
    similarity_only_path,
    summarise,
)
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path

SEED = 42


def build_panel(store: GraphStore, n_each: int, rng: np.random.Generator):
    """Frozen panel: `n_each` random pairs + `n_each` obscure pairs (both
    endpoints out-degree <= 5, where discovery is supposed to happen)."""
    n = store.artist_count
    degrees = np.diff(store.offsets)
    obscure = np.where(degrees <= 5)[0]

    random_pairs = []
    while len(random_pairs) < n_each:
        a, b = int(rng.integers(n)), int(rng.integers(n))
        if a != b:
            random_pairs.append((a, b))

    obscure_pairs = []
    while len(obscure_pairs) < n_each and len(obscure) > 1:
        a, b = (int(x) for x in rng.choice(obscure, size=2, replace=False))
        if a != b:
            obscure_pairs.append((a, b))

    return {"random": random_pairs, "obscure": obscure_pairs}


def run_variant(store, pairs, router, hub_nodes, cfg=None):
    metrics = []
    for a, b in pairs:
        path = router(store, a, b, cfg) if cfg is not None else router(store, a, b)
        if path and len(path) >= 2:
            metrics.append(path_metrics(store, path, hub_nodes))
    return summarise(metrics)


def fmt(s: dict) -> str:
    if not s:
        return "  (no paths)"
    return (
        f"  hubfrac {s['mean_hubfrac']*100:5.1f}%   "
        f"len {s['mean_length']:5.1f}   "
        f"max-interior-deg {s['mean_max_interior_degree']:7.0f}   "
        f"interior-pop {s['mean_interior_pop']:.3f}   "
        f"bottleneck-sim {s['mean_bottleneck_sim']:.3f}   "
        f"mean-sim {s['mean_sim']:.3f}"
    )


def main():
    graph = sys.argv[1] if len(sys.argv) > 1 else "../builder/scratch/graph-75k.bin"
    n_each = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    print(f"loading {graph} ...")
    store = GraphStore.load(graph)
    hub_nodes = hub_node_set(store, 0.01)
    print(f"{store.artist_count:,} artists | top-1% hub set size = {len(hub_nodes)}")

    rng = np.random.default_rng(SEED)
    panel = build_panel(store, n_each, rng)

    cfg = ApiConfig()
    # Router adapters with a uniform (store, a, b[, cfg]) signature.
    def full(store, a, b, cfg):
        return find_path(store, a, b, [], cfg)

    routers = [
        ("FULL cost function", full, cfg),
        ("similarity-only", lambda s, a, b: similarity_only_path(s, a, b), None),
        ("plain BFS (shortest)", lambda s, a, b: bfs_shortest_path(s, a, b), None),
    ]

    for subset, pairs in panel.items():
        print(f"\n=== {subset} pairs (n={len(pairs)}) ===")
        for label, router, c in routers:
            t = time.time()
            s = run_variant(store, pairs, router, hub_nodes, c)
            print(f"{label:22s}{fmt(s)}   [{time.time()-t:.0f}s]")


if __name__ == "__main__":
    main()
