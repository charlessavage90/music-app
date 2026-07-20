from pathlib import Path

import numpy as np
import pytest

from artistpath_api.graph_store import GraphStore

FIXTURES = Path(__file__).parent / "fixtures"


def make_store(names, popularity, undirected_edges):
    """Build a GraphStore from a human-readable spec, for pathfinding tests.

    names: list of artist names (index = node id)
    popularity: list of floats 0-1 (index = node id)
    undirected_edges: list of (u, v, score) — each added in both directions
    """
    n = len(names)
    adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for u, v, s in undirected_edges:
        adj[u].append((v, s))
        adj[v].append((u, s))

    offsets = np.zeros(n + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []
    for i in range(n):
        for v, s in sorted(adj[i]):
            neighbours.append(v)
            scores.append(s)
        offsets[i + 1] = len(neighbours)

    return GraphStore(
        mbids=[f"{i:036d}" for i in range(n)],
        names=list(names),
        disambiguations=[""] * n,
        popularity=np.asarray(popularity, dtype=np.float32),
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
    )


@pytest.fixture
def fixture_store():
    return GraphStore.load(FIXTURES / "graph-fixture.bin")
