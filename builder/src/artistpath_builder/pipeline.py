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
from collections import defaultdict

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

    # Score-weighted in-degree over artists we crawled (findings 6f). Only
    # edges between two crawled artists count, so popularity is measured on
    # the same node set the graph is built from.
    indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    for mbid in sorted(known):
        neighbours = source.parse(payloads[mbid], exclude_mbid=mbid)
        edges = {n.mbid: n.score for n in neighbours if n.mbid in known}
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
