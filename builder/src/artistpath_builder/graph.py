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
    popularity: list[float]
    offsets: np.ndarray  # int32, length len(mbids) + 1
    neighbours: np.ndarray  # int32
    scores: np.ndarray  # float32
    edge_types: np.ndarray  # uint8

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
    """Log-scale listener counts to 0-1 (spec section 4.1).

    Raw counts are power-law distributed; a linear scale would make every
    artist outside the top few hundred indistinguishable.
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
    # Distinct listeners, not plays — see spec section 4.1.
    popularity = _log_scaled([stats_by_mbid[m].user_count for m in mbids])

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
        popularity=popularity,
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.full(len(neighbours), int(edge_type), dtype=np.uint8),
    )
