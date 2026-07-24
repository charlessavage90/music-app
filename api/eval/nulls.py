"""Null models for path-quality metrics.

A rate with no null model measures nothing. Hub-traversal read 94-98% and
looked alarming; a degree-biased null puts it at 61-68% by chance at typical
path lengths, and the real finding only existed once someone built the null.

Two nulls, answering different questions:

- `degree_biased_walk` — what a router that ignores scores entirely produces.
  Its stationary distribution is proportional to degree, so it is the right
  baseline for "does the router seek hubs beyond what a blind walker hits?"
- `configuration_model_rewire` — preserves the degree sequence exactly but
  randomises who connects to whom, destroying all community structure. Re-run
  the router on it and the question becomes "is hub-seeking a property of the
  SCORING, or of the degree sequence?" That is the one the committed record
  disagrees with itself about (adjudication §5.3).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402


def degree_biased_walk(
    store: GraphStore, source: int, length: int, rng: np.random.Generator
) -> list[int]:
    """A uniform random walk of `length` nodes starting at `source`.

    Uniform over neighbours makes the walk degree-biased in its stationary
    distribution — high-degree nodes are visited more often precisely because
    more edges lead to them. That bias is the point: it is what the observed
    hub fraction must beat to count as a finding.
    """
    walk = [source]
    current = source
    for _ in range(length - 1):
        start, end = int(store.offsets[current]), int(store.offsets[current + 1])
        if end <= start:
            break
        current = int(store.neighbours[rng.integers(start, end)])
        walk.append(current)
    return walk


def configuration_model_rewire(
    store: GraphStore, rng: np.random.Generator
) -> GraphStore:
    """Randomise edge endpoints while preserving every node's degree exactly.

    Double-edge swap on the undirected edge list: pick two edges (a,b) and
    (c,d), replace them with (a,d) and (c,b). Every endpoint keeps its degree
    by construction. Swaps producing a self-loop or a duplicate edge are
    rejected and retried, which is what keeps the result a simple graph.

    The original similarity scores are discarded, not carried along:
    `_store_from_edges` fills every rewired edge with a uniform constant
    placeholder instead. That is intentional — scores are meaningless once
    edge endpoints are randomised. This null is for the score-free question
    of whether the DEGREE SEQUENCE alone explains hub-seeking.
    """
    # Undirected edge list: keep u < v so each edge appears once.
    us, vs = [], []
    for u in range(store.artist_count):
        start, end = int(store.offsets[u]), int(store.offsets[u + 1])
        for k in range(start, end):
            v = int(store.neighbours[k])
            if u < v:
                us.append(u)
                vs.append(v)
    us_arr = np.asarray(us, dtype=np.int64)
    vs_arr = np.asarray(vs, dtype=np.int64)
    m = us_arr.size
    if m < 2:
        return store

    existing = {(int(a), int(b)) for a, b in zip(us_arr, vs_arr)}

    # 10 swap attempts per edge is the standard mixing heuristic for
    # double-edge-swap randomisation.
    for _ in range(10 * m):
        i, j = int(rng.integers(m)), int(rng.integers(m))
        if i == j:
            continue
        a, b = int(us_arr[i]), int(vs_arr[i])
        c, d = int(us_arr[j]), int(vs_arr[j])
        if len({a, b, c, d}) < 4:
            continue
        new_i = (min(a, d), max(a, d))
        new_j = (min(c, b), max(c, b))
        if new_i in existing or new_j in existing:
            continue
        existing.discard((min(a, b), max(a, b)))
        existing.discard((min(c, d), max(c, d)))
        existing.add(new_i)
        existing.add(new_j)
        us_arr[i], vs_arr[i] = new_i
        us_arr[j], vs_arr[j] = new_j

    return _store_from_edges(store, us_arr, vs_arr)


def _store_from_edges(
    template: GraphStore, us: np.ndarray, vs: np.ndarray
) -> GraphStore:
    """Rebuild CSR arrays from an undirected edge list, mirroring each edge."""
    n = template.artist_count
    rows: list[list[int]] = [[] for _ in range(n)]
    for a, b in zip(us, vs):
        rows[int(a)].append(int(b))
        rows[int(b)].append(int(a))

    offsets = np.zeros(n + 1, dtype=np.int32)
    neighbours: list[int] = []
    for i in range(n):
        for v in sorted(rows[i]):  # deterministic within-row order
            neighbours.append(v)
        offsets[i + 1] = len(neighbours)

    return GraphStore(
        mbids=list(template.mbids),
        names=list(template.names),
        disambiguations=list(template.disambiguations),
        pop_raw=template.pop_raw.copy(),
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.full(len(neighbours), 0.5, dtype=np.float32),
    )
