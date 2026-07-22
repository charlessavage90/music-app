"""Objective path-quality evaluation.

Built in response to the stage-2 review: the system was validated only by
eyeballing paths, which hid that the router hub-seeks ~92% of the time and the
popularity-smoothing term is ~10x dominated by similarity. These functions turn
"looks smooth" into numbers: hub fraction, bottleneck/mean similarity along a
path, interior popularity, and length.

Pure over a GraphStore. No I/O. The runner (api/eval/run_baseline.py) drives
these over a frozen panel of artist pairs.
"""

from __future__ import annotations

import heapq
import math
from collections import deque
from dataclasses import dataclass

import numpy as np

from artistpath_api.graph_store import GraphStore


def out_degree(store: GraphStore, node: int) -> int:
    return int(store.offsets[node + 1] - store.offsets[node])


def degree_percentile_threshold(store: GraphStore, top_fraction: float) -> int:
    """Out-degree cutoff for the top `top_fraction` of nodes (e.g. 0.01 = top 1%)."""
    degrees = np.diff(store.offsets)
    return int(np.quantile(degrees, 1.0 - top_fraction))


def edge_score(store: GraphStore, u: int, v: int) -> float:
    """Similarity of the u->v edge, or 0.0 if not adjacent.

    Binary search over the CSR row rather than a linear scan: graph.py sorts
    each row by destination id, and a linear scan over a degree-11,243 hub was
    costing more than everything else in this module combined.
    """
    start, end = int(store.offsets[u]), int(store.offsets[u + 1])
    row = store.neighbours[start:end]
    pos = int(np.searchsorted(row, v))
    if pos < row.size and int(row[pos]) == v:
        return float(store.scores[start + pos])
    return 0.0


# Common-neighbour overlap floors at this value before log-space aggregation,
# so one zero-overlap hop cannot erase an entire path's score. Measured
# zero-rate on the 75k graph is 0.7% (adjudication §4.3).
_GEO_EPSILON = 1e-6


def neighbours_array(store: GraphStore, node: int) -> np.ndarray:
    """This node's neighbour ids as a sorted int32 view over the CSR row.

    graph.py sorts each CSR row by destination id at build time, so this is
    already sorted and needs no copy — which is what lets the set operations
    below run in O(d_u + d_v) with no Python sets.
    """
    start, end = int(store.offsets[node]), int(store.offsets[node + 1])
    return store.neighbours[start:end]


def common_neighbours(store: GraphStore, u: int, v: int) -> np.ndarray:
    """Neighbours shared by u and v, excluding u and v themselves.

    Endpoint convention (spec §B1): for an *adjacent* pair, u is always in
    N(v) and v is always in N(u), while u is never in N(u). Left in, the two
    endpoints would inflate every adjacent pair's overlap by a constant that
    varies with degree. They are excluded here and included in the union for
    `jaccard`, which is the conventional definition.
    """
    shared = np.intersect1d(
        neighbours_array(store, u), neighbours_array(store, v), assume_unique=True
    )
    return shared[(shared != u) & (shared != v)]


def adamic_adar(store: GraphStore, u: int, v: int) -> float:
    """Sum of 1/log(degree) over common neighbours.

    The primary objective. Overlap through a hub counts for little; overlap
    through an obscure artist counts for a lot — which is the property raw
    Jaccard lacks (it correlates -0.639 with max-degree, adjudication §4.1).
    """
    total = 0.0
    for w in common_neighbours(store, u, v):
        degree = out_degree(store, int(w))
        if degree > 1:  # log(1) == 0
            total += 1.0 / math.log(degree)
    return total


def overlap_coefficient(store: GraphStore, u: int, v: int) -> float:
    """|N(u) & N(v)| / min(deg u, deg v) — the degree-neutrality guard.

    Adamic-Adar is flat in max-degree but couples to min-degree at Spearman
    +0.578, a measured channel an optimiser could exploit. This is near-neutral
    on both axes and is the control for that channel (adjudication §4.2-4.3).
    Report both; never adopt on Adamic-Adar alone.
    """
    smaller = min(out_degree(store, u), out_degree(store, v))
    if smaller == 0:
        return 0.0
    return len(common_neighbours(store, u, v)) / smaller


def jaccard(store: GraphStore, u: int, v: int) -> float:
    """|N(u) & N(v)| / |N(u) | N(v)| — DIAGNOSTIC ONLY.

    Retained so its redundancy stays visible in the results table, not as an
    objective. It is structurally bounded by min(d_u,d_v)/max(d_u,d_v), so it
    is a near-deterministic function of max_interior_degree rather than an
    independent check (adjudication §4.1).
    """
    union = np.union1d(neighbours_array(store, u), neighbours_array(store, v))
    if union.size == 0:
        return 0.0
    return len(common_neighbours(store, u, v)) / union.size


def geometric_mean(values: list[float]) -> float:
    """Geometric mean with an epsilon floor.

    Aggregation for per-hop overlap. A bottleneck (min) over 7-9 hops is
    dominated by one noisy node; a plain product collapses to zero on any
    single zero-overlap hop. The floor keeps the ordering meaningful.
    """
    if not values:
        return 0.0
    logs = [math.log(max(v, _GEO_EPSILON)) for v in values]
    return math.exp(sum(logs) / len(logs))


@dataclass(frozen=True, slots=True)
class PathMetrics:
    length: int                  # nodes in the path
    hubfrac: float               # fraction of INTERIOR nodes in the frozen hub set
    max_interior_degree: int
    mean_interior_pop: float
    max_interior_pop: float
    bottleneck_sim: float        # diagnostic — derived from the scores under test
    mean_sim: float              # diagnostic
    ceiling_hops: float          # fraction of hops at score 1.0 — see below
    adamic_adar: float           # PRIMARY objective, geometric mean over hops
    overlap_coefficient: float   # mandatory degree-neutrality guard
    jaccard: float               # diagnostic only
    mean_common_neighbours: float  # DIAGNOSTIC — makes the AA/OC density effect
                                    # visible (revised plan §4, amendment 3b):
                                    # a graph with fewer edges depresses common-
                                    # neighbour metrics mechanically, and a reader
                                    # comparing artifacts with very different edge
                                    # counts cannot tell that from a genuine quality
                                    # regression without this number alongside it.


def path_metrics(
    store: GraphStore, path: list[int], hub_nodes: set[int]
) -> PathMetrics:
    """Measure one path. Interior = nodes excluding the two user-chosen endpoints.

    `hub_nodes` is a FROZEN set of node ids, not a per-graph threshold. The
    top-1% degree cutoff moves between builds, so a threshold would let a
    variant "improve" purely by compressing its degree distribution.

    `ceiling_hops` is the fraction of hops whose similarity is exactly 1.0.
    Those hops cost w_sim*(1 - 1.0) == 0, so the router picks among them on
    w_jump and w_hop alone — effectively on noise. This is the defect that
    made every prior cross-artifact comparison uninterpretable, and it is
    invisible in every other metric here (adjudication §2.5).
    """
    interior = path[1:-1]
    degs = [out_degree(store, n) for n in interior]
    pops = [float(store.popularity[n]) for n in interior]
    hops = list(zip(path, path[1:]))
    sims = [edge_score(store, a, b) for a, b in hops]
    # A fourth call per hop (adamic_adar/overlap_coefficient/jaccard above each
    # already call common_neighbours once): acceptable, find_path dominates the
    # harness's runtime, not this.
    common_counts = [len(common_neighbours(store, a, b)) for a, b in hops]

    return PathMetrics(
        length=len(path),
        hubfrac=(sum(n in hub_nodes for n in interior) / len(interior))
        if interior
        else 0.0,
        max_interior_degree=max(degs) if degs else 0,
        mean_interior_pop=(sum(pops) / len(pops)) if pops else 0.0,
        max_interior_pop=max(pops) if pops else 0.0,
        bottleneck_sim=min(sims) if sims else 1.0,
        mean_sim=(sum(sims) / len(sims)) if sims else 1.0,
        ceiling_hops=(sum(s >= 1.0 for s in sims) / len(sims)) if sims else 0.0,
        adamic_adar=geometric_mean([adamic_adar(store, a, b) for a, b in hops]),
        overlap_coefficient=geometric_mean(
            [overlap_coefficient(store, a, b) for a, b in hops]
        ),
        jaccard=geometric_mean([jaccard(store, a, b) for a, b in hops]),
        mean_common_neighbours=(
            (sum(common_counts) / len(common_counts)) if common_counts else 0.0
        ),
    )


def bfs_shortest_path(store: GraphStore, source: int, target: int) -> list[int] | None:
    """Unweighted shortest path (fewest hops) — the naive baseline the spec's
    popularity-smoothing is meant to beat (spec §9)."""
    if source == target:
        return [source]
    prev: dict[int, int] = {}
    seen = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if u == target:
            break
        for v, _ in store.neighbours_of(u):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                queue.append(v)
    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def similarity_only_path(store: GraphStore, source: int, target: int) -> list[int] | None:
    """Dijkstra minimising (1 - similarity) alone — the full cost function with
    every popularity term zeroed. If this scores like the full router, the
    popularity machinery is inert."""
    if source == target:
        return [source]
    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        for v, sim in store.neighbours_of(u):
            nd = d + (1.0 - float(sim))
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def summarise(metrics: list[PathMetrics]) -> dict[str, float]:
    """Aggregate a set of path metrics into headline numbers."""
    n = len(metrics)
    if n == 0:
        return {}
    return {
        "n": n,
        "mean_hubfrac": sum(m.hubfrac for m in metrics) / n,
        "mean_length": sum(m.length for m in metrics) / n,
        "mean_max_interior_degree": sum(m.max_interior_degree for m in metrics) / n,
        "mean_interior_pop": sum(m.mean_interior_pop for m in metrics) / n,
        "mean_bottleneck_sim": sum(m.bottleneck_sim for m in metrics) / n,
        "mean_sim": sum(m.mean_sim for m in metrics) / n,
        "mean_ceiling_hops": sum(m.ceiling_hops for m in metrics) / n,
        "mean_adamic_adar": sum(m.adamic_adar for m in metrics) / n,
        "mean_overlap_coefficient": sum(m.overlap_coefficient for m in metrics) / n,
        "mean_jaccard": sum(m.jaccard for m in metrics) / n,
        # DIAGNOSTIC — see PathMetrics.mean_common_neighbours. Report alongside
        # mean_adamic_adar / mean_overlap_coefficient so a density-driven fall in
        # those two is visible as a mechanism, not just asserted in prose.
        "mean_common_neighbours": sum(m.mean_common_neighbours for m in metrics) / n,
    }


def hub_node_set(store: GraphStore, top_fraction: float) -> set[int]:
    """Node ids in the top `top_fraction` by out-degree, as a frozen set.

    Computed ONCE on the control build and reused across every variant.
    """
    degrees = np.diff(store.offsets)
    cutoff = np.quantile(degrees, 1.0 - top_fraction)
    return {int(i) for i in np.where(degrees >= cutoff)[0]}
