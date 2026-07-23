"""Graph assembly: symmetrise, prune to one component, emit CSR.

Pure functions over in-memory data. Determinism is a hard requirement here
(spec section 9) — every ordering decision is explicit.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

import numpy as np

from artistpath_builder.models import ArtistStats, EdgeType

Adjacency = dict[str, dict[str, float]]


@dataclass(slots=True)
class Graph:
    mbids: list[str]
    names: list[str]
    disambiguations: list[str]
    # Log-scaled score-weighted in-degree in 0-1. NOT a percentile, and NOT
    # fame — log §2.11/§2.12 record both conflations and what each cost.
    pop_raw: list[float]
    offsets: np.ndarray  # int32, length len(mbids) + 1
    neighbours: np.ndarray  # int32
    scores: np.ndarray  # float32
    edge_types: np.ndarray  # uint8

    @property
    def popularity(self) -> list[float]:
        """Read-only alias for the frozen probe scripts in builder/analysis/.

        Mapping table: builder/analysis/README.md.
        """
        return self.pop_raw

    @property
    def artist_count(self) -> int:
        return len(self.mbids)

    @property
    def edge_count(self) -> int:
        return int(self.neighbours.size)


def symmetrise(adjacency: Adjacency) -> Adjacency:
    """Mirror one-way edges, keeping the stronger score.

    Similarity is not mutual: A may list B without B listing A. Left alone,
    those become dead ends during pathfinding (spec section 3.1 step 4).
    """
    result: Adjacency = {node: dict(edges) for node, edges in adjacency.items()}
    for src, edges in adjacency.items():
        for dst, score in edges.items():
            result.setdefault(dst, {})
            result.setdefault(src, {})
            best = max(score, result[dst].get(src, 0.0), result[src].get(dst, 0.0))
            result[src][dst] = best
            result[dst][src] = best
    return result


def mutual_knn_cap(
    adjacency: Adjacency, k: int, ranking: Adjacency | None = None
) -> Adjacency:
    """Keep edge (u,v) only if v is in u's top-k AND u is in v's top-k.

    The cap this replaces was applied BEFORE symmetrisation. Symmetrisation
    adds a reverse edge for every incoming one and nothing bounds how many
    neighbour lists an artist appears in, so the cap truncated the obscure
    tail — where alternative routes are scarcest — while leaving hubs
    completely unbounded. A configured cap of 50 produced an observed maximum
    degree of 11,243.

    Mutual k-NN is the only formulation that both bounds degree at k and stays
    symmetric by construction: union-kNN does not bound degree, and capping
    after symmetrisation breaks symmetry again. It prunes harder than the old
    scheme, so callers must check largest-component retention.

    `ranking`, when given, supplies the values used to order each node's
    top-k; emitted scores still come from `adjacency`. It exists because the
    p99 clip collapses the top ~1% of scores to exactly 1.0, and ranking those
    tied values let the MBID tie-break decide which neighbours a saturated
    artist kept — which is how the most famous artists lost nearly all their
    edges (Phase 1 log §2.8). Callers that rescale destructively must pass the
    pre-rescale strengths here. `ranking` must cover exactly the nodes of
    `adjacency` (ValueError otherwise) and every edge of `adjacency`
    (KeyError otherwise — loud by design).

    Ties break on lowest MBID, matching every other ordering decision in this
    module (design §9).
    """
    if ranking is not None and set(ranking) != set(adjacency):
        raise ValueError(
            "ranking must cover exactly the nodes of adjacency; top-k "
            "selection over a different node set is undefined"
        )
    rank_of = ranking if ranking is not None else adjacency

    top_k: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(
            ((dst, rank_of[node][dst]) for dst in edges),
            key=lambda pair: (-pair[1], pair[0]),
        )
        top_k[node] = {dst for dst, _score in ranked[:k]}

    result: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in top_k[node] and node in top_k.get(dst, set()):
                result[node][dst] = score
    return result


def largest_component(adjacency: Adjacency) -> set[str]:
    """Return the biggest connected component.

    Keeping only this guarantees a path exists between any two artists the UI
    offers, so a "no path" result can only ever come from user exclusions
    (spec section 3.1 step 5). Ties break on lowest MBID for determinism.
    """
    unvisited = set(adjacency)
    best: set[str] = set()

    for start in sorted(adjacency):
        if start not in unvisited:
            continue
        component: set[str] = set()
        queue = deque([start])
        unvisited.discard(start)
        while queue:
            node = queue.popleft()
            component.add(node)
            for neighbour in adjacency.get(node, {}):
                if neighbour in unvisited:
                    unvisited.discard(neighbour)
                    queue.append(neighbour)
        if len(component) > len(best):
            best = component
    return best


def _log_scaled(counts: list[int]) -> list[float]:
    """Log-scale the popularity counts to 0-1 (spec section 4.1).

    Raw counts are power-law distributed; a linear scale would make every
    artist outside the top few hundred indistinguishable.

    The output is a rescaled VALUE, not a percentile: the log scale compresses
    the head, so equal steps here are wildly unequal steps in rank. That gap is
    what log §2.12 records as the currency error.
    """
    logs = [math.log1p(max(0, n)) for n in counts]
    low, high = min(logs), max(logs)
    span = high - low
    if span == 0:
        return [0.0] * len(logs)
    return [(value - low) / span for value in logs]


def build_graph(
    adjacency: Adjacency,
    stats: list[ArtistStats],
    edge_type: EdgeType,
) -> Graph:
    """Assemble CSR arrays. IDs are assigned in sorted-MBID order."""
    stats_by_mbid = {record.mbid: record for record in stats}
    mbids = sorted(set(adjacency) & set(stats_by_mbid))
    index = {mbid: i for i, mbid in enumerate(mbids)}

    names = [stats_by_mbid[m].name for m in mbids]
    disambiguations = [stats_by_mbid[m].disambiguation for m in mbids]
    # Score-weighted in-degree, computed from the archive during `build`.
    # There is no separate popularity source (findings 6f) — the field's old
    # name and the "distinct listeners" comment that used to sit here were both
    # inherited from a design that was never built.
    pop_raw = _log_scaled([stats_by_mbid[m].pop_indegree_scaled for m in mbids])

    offsets = np.zeros(len(mbids) + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []

    for i, mbid in enumerate(mbids):
        row = [
            (index[dst], score)
            for dst, score in adjacency[mbid].items()
            if dst in index
        ]
        row.sort(key=lambda pair: pair[0])  # deterministic within-row order
        for dst_id, score in row:
            neighbours.append(dst_id)
            scores.append(score)
        offsets[i + 1] = len(neighbours)

    return Graph(
        mbids=mbids,
        names=names,
        disambiguations=disambiguations,
        pop_raw=pop_raw,
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.full(len(neighbours), int(edge_type), dtype=np.uint8),
    )
