"""Assemble a graph from the similarity archive alone.

This function must never touch the network. The replay test enforces that by
injecting a fetcher that raises.

Popularity is **score-weighted in-degree** — the sum of similarity scores on
edges pointing at an artist. It is computed from the archive itself, so there
is no second data source to acquire or keep in sync. In-degree was validated
against 5,255 ground-truth artists at Spearman ~0.50 and, crucially, is the
only popularity measure computed on the same population as the similarity
graph; every external source tested imported a population mismatch (findings
sections 6d-6f).
"""

from __future__ import annotations

import logging
import math
from collections import defaultdict

import numpy as np

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import (
    Adjacency,
    Graph,
    build_graph,
    largest_component,
    symmetrise,
)
from artistpath_builder.models import ArtistStats
from artistpath_builder.sources.base import SimilaritySource
from artistpath_builder.sources.listenbrainz import harvest_identities

logger = logging.getLogger(__name__)


def build_from_archive(
    config: BuilderConfig,
    archive: RawArchive,
    source: SimilaritySource,
) -> Graph:
    """Assemble a graph from archived similarity responses alone.

    A node is any artist that has an archived similarity response (so it has
    out-edges) and appears somewhere as a neighbour (so it has an in-degree
    to serve as popularity). Isolated artists cannot be routed and are dropped
    by the largest-component step regardless.
    """
    prefix = f"similar/{source.name}/"
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[key[len(prefix) : -len(".json")]] = payload

    known = set(payloads)

    # Names and disambiguation live in neighbour rows, not in any per-artist
    # record, so they are harvested across every response.
    identities = harvest_identities(payloads.values())

    # --- Pass 1: raw neighbour lists and per-artist co-occurrence mass -----
    # The mass (sum of an artist's raw scores) is the marginal used to correct
    # for popularity below. Computed over the FULL uncapped list, which is a
    # better marginal estimate than the capped one.
    raw_lists: dict[str, list] = {}
    mass: dict[str, float] = {}
    for mbid in sorted(known):
        neighbours = source.parse(payloads[mbid], exclude_mbid=mbid)
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0

    # --- Pass 2: cosine-corrected, globally comparable edge strength -------
    # sim(a,b) = cooc(a,b) / sqrt(mass(a) * mass(b))
    #
    # Raw co-occurrence conflates similarity with popularity: two famous
    # artists co-occur constantly simply because both are famous. Dividing by
    # each artist's own mass yields "co-occur more than their popularity alone
    # predicts" — the standard cosine measure — and, crucially, the SAME
    # formula everywhere, so an edge score means the same thing graph-wide.
    scored_adjacency: dict[str, list[tuple[str, float]]] = {}
    for mbid in sorted(known):
        mass_a = mass[mbid]
        scored = [
            (n.mbid, n.score / math.sqrt(mass_a * mass[n.mbid]))
            for n in raw_lists[mbid]
            if n.mbid in known
        ]
        # Cap AFTER correction — the corrected ranking differs from the raw one.
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = scored[: config.max_neighbours_per_artist]

    # Rescale globally into 0-1 using a robust maximum, so w_sim in the API's
    # cost function operates on a stable scale.
    all_scores = [s for edges in scored_adjacency.values() for _, s in edges]
    scale = float(np.percentile(all_scores, 99)) if all_scores else 1.0
    if scale <= 0:
        scale = 1.0
    logger.info("cosine scale (p99) = %.6g", scale)

    indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    for mbid, scored in scored_adjacency.items():
        edges = {dst: min(1.0, value / scale) for dst, value in scored}
        adjacency[mbid] = edges
        for dst, score in edges.items():
            indegree[dst] += score

    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    logger.info("largest component: %d of %d artists", len(keep), len(adjacency))

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    # In-degree is a float; ArtistStats.user_count is the integer popularity
    # slot. Scale to preserve ordering — build_graph log-scales it anyway.
    stats = [
        ArtistStats(
            mbid=mbid,
            name=identities.get(mbid, ("", ""))[0],
            user_count=round(indegree[mbid] * 1000),
            listen_count=0,  # not used; popularity is in-degree
            disambiguation=identities.get(mbid, ("", ""))[1],
        )
        for mbid in keep
    ]

    return build_graph(pruned, stats, source.edge_type)
