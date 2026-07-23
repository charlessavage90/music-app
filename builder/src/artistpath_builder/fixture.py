"""Extract a small connected sub-graph for local development and tests.

Spec section 6.1: a fresh clone must run without the 80MB artifact, and the
same fixture backs the pathfinding tests.
"""

from __future__ import annotations

from collections import deque

import numpy as np

from artistpath_builder.graph import Graph


def most_popular_index(graph: Graph) -> int:
    """Index of the most popular artist. Ties break on lowest MBID.

    This is the default fixture seed. It used to be `mbids[0]` — an arbitrary
    artist, whichever sorted first — and that was harmless only by accident.
    The pre-Phase-2 graph left hubs unbounded (a configured cap of 50 produced
    an observed degree of 11,243), so a breadth-first walk from *anywhere*
    reached the famous core within a hop or two and swept it in. Mutual k-NN
    bounds degree at k, so the same walk now stays inside a local cluster: the
    first fixture built after adoption contained neither Miles Davis nor
    Radiohead. Seeding from the most popular artist makes the sample
    representative by construction rather than by a property of the graph that
    no longer holds.
    """
    return min(
        range(len(graph.mbids)),
        key=lambda i: (-graph.pop_raw[i], graph.mbids[i]),
    )


def extract_fixture(graph: Graph, size: int, seed_mbid: str | None = None) -> Graph:
    """Breadth-first expansion from a seed, so the result is always connected.

    `seed_mbid=None` seeds from the most popular artist — see
    `most_popular_index` for why that default matters.
    """
    if seed_mbid is None:
        start = most_popular_index(graph)
    else:
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
        pop_raw=[graph.pop_raw[i] for i in keep],
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.asarray(edge_types, dtype=np.uint8),
    )
