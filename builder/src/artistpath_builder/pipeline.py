"""Assemble a graph from the archive alone.

This function must never touch the network. The replay test enforces that by
injecting a fetcher that raises.
"""

from __future__ import annotations

import logging

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
from artistpath_builder.sources.seeds import parse_artist_stats

logger = logging.getLogger(__name__)


def _archived_stats(archive: RawArchive) -> dict[str, ArtistStats]:
    """Popularity for every artist whose stats response was archived."""
    stats: dict[str, ArtistStats] = {}
    for key in archive.keys():
        if not key.startswith("stats/"):
            continue
        payload = archive.get(key)
        if payload is None:
            continue
        try:
            record = parse_artist_stats(payload)
        except ValueError:
            logger.warning("unparseable stats payload at %s", key)
            continue
        if record is not None:
            stats[record.mbid] = record
    return stats


def build_from_archive(
    config: BuilderConfig,
    archive: RawArchive,
    source: SimilaritySource,
) -> Graph:
    """Assemble a graph from archived responses alone. Never touches the network."""
    stats = _archived_stats(archive)
    # An artist with no popularity cannot be routed through, so it is not a node.
    known = set(stats)
    adjacency: Adjacency = {}
    missing = 0

    for mbid in sorted(known):
        payload = archive.get(f"similar/{source.name}/{mbid}.json")
        if payload is None:
            missing += 1
            continue
        neighbours = source.parse(payload, exclude_mbid=mbid)
        adjacency[mbid] = {n.mbid: n.score for n in neighbours if n.mbid in known}

    if missing:
        logger.warning("%d artists had no archived similarity response", missing)

    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    logger.info("largest component: %d of %d artists", len(keep), len(adjacency))

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    return build_graph(pruned, list(stats.values()), source.edge_type)
