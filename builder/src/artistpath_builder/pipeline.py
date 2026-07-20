"""Assemble a graph from the archive plus a popularity table.

This function must never touch the network. The replay test enforces that by
injecting a fetcher that raises.

Two independent inputs:
  - the similarity archive, filled by the crawler
  - a popularity table, derived offline from the ListenBrainz spark dump

Neither pipeline blocks the other.
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
from artistpath_builder.sources.listenbrainz import harvest_identities

logger = logging.getLogger(__name__)

Popularity = dict[str, int]


def build_from_archive(
    config: BuilderConfig,
    archive: RawArchive,
    source: SimilaritySource,
    popularity: Popularity,
) -> Graph:
    """Assemble a graph from archived responses and a popularity table.

    An artist needs both an archived similarity response and a popularity
    entry to become a node: without neighbours it cannot be routed through,
    and without popularity the cost function cannot weigh it.
    """
    prefix = f"similar/{source.name}/"
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[key[len(prefix) : -len(".json")]] = payload

    # Names and disambiguation live in neighbour rows, not in any per-artist
    # record, so they are harvested across every response.
    identities = harvest_identities(payloads.values())

    known = {mbid for mbid in payloads if mbid in popularity}
    skipped = len(payloads) - len(known)
    if skipped:
        logger.warning("%d crawled artists had no popularity entry", skipped)

    adjacency: Adjacency = {}
    for mbid in sorted(known):
        neighbours = source.parse(payloads[mbid], exclude_mbid=mbid)
        adjacency[mbid] = {n.mbid: n.score for n in neighbours if n.mbid in known}

    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    logger.info("largest component: %d of %d artists", len(keep), len(adjacency))

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    stats = [
        ArtistStats(
            mbid=mbid,
            name=identities.get(mbid, ("", ""))[0],
            user_count=popularity[mbid],
            listen_count=0,  # not carried; popularity is distinct listeners
            disambiguation=identities.get(mbid, ("", ""))[1],
        )
        for mbid in keep
    ]

    return build_graph(pruned, stats, source.edge_type)
