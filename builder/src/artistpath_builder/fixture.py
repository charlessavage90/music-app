"""Extract a small connected sub-graph for local development and tests.

Spec section 6.1: a fresh clone must run without the 80MB artifact, and the
same fixture backs the pathfinding tests.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from artistpath_builder.graph import Graph


def extract_fixture(graph: Graph, size: int, seed_mbid: str) -> Graph:
    """Breadth-first expansion from a seed, so the result is always connected."""
    try:
        start = graph.mbids.index(seed_mbid)
    except ValueError as exc:
        raise KeyError(f"seed artist not in graph: {seed_mbid}") from exc

    chosen: list[int] = []
    seen = {start}
    queue = deque([start])
    while queue and len(chosen) < size:
        node = queue.popleft()
        chosen.append(node)
        row = graph.neighbours[graph.offsets[node] : graph.offsets[node + 1]]
        for neighbour in sorted(int(n) for n in row):  # deterministic
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)

    keep = sorted(chosen)
    remap = {old: new for new, old in enumerate(keep)}

    offsets = np.zeros(len(keep) + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []
    edge_types: list[int] = []

    for new_id, old_id in enumerate(keep):
        for i in range(graph.offsets[old_id], graph.offsets[old_id + 1]):
            old_neighbour = int(graph.neighbours[i])
            if old_neighbour in remap:
                neighbours.append(remap[old_neighbour])
                scores.append(float(graph.scores[i]))
                edge_types.append(int(graph.edge_types[i]))
        offsets[new_id + 1] = len(neighbours)

    return Graph(
        mbids=[graph.mbids[i] for i in keep],
        names=[graph.names[i] for i in keep],
        disambiguations=[graph.disambiguations[i] for i in keep],
        popularity=[graph.popularity[i] for i in keep],
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.asarray(edge_types, dtype=np.uint8),
    )
