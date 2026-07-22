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
import re

from collections import defaultdict

import numpy as np

from artistpath_builder.archive import RawArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.graph import (
    Adjacency,
    Graph,
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats
from artistpath_builder.sources.base import SimilaritySource
from artistpath_builder.sources.listenbrainz import harvest_identities

logger = logging.getLogger(__name__)

# MusicBrainz marks placeholder entities in the disambiguation field.
_SPECIAL_PURPOSE = re.compile(r"special purpose", re.IGNORECASE)


def is_special_purpose(disambiguation: str | None) -> bool:
    """True for MusicBrainz placeholder entities, matched on disambiguation."""
    return bool(_SPECIAL_PURPOSE.search(disambiguation or ""))


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

    # Drop placeholder entities BEFORE the mass computation, so they
    # contribute to no marginal. Mass is computed over the full uncapped
    # neighbour list, so leaving them in would perturb every score slightly.
    if config.filter_special_purpose:
        excluded = {
            mbid
            for mbid, (_name, disambiguation) in identities.items()
            if is_special_purpose(disambiguation)
        }
        if excluded:
            logger.info("filtered %d special-purpose entities", len(excluded))
        known -= excluded
    else:
        excluded = set()

    # --- Pass 1: raw neighbour lists and per-artist co-occurrence mass -----
    # The mass (sum of an artist's raw scores) is the marginal used to correct
    # for popularity below. Computed over the FULL uncapped list, which is a
    # better marginal estimate than the capped one.
    raw_lists: dict[str, list] = {}
    mass: dict[str, float] = {}
    for mbid in sorted(known):
        neighbours = [
            n
            for n in source.parse(payloads[mbid], exclude_mbid=mbid)
            if n.mbid not in excluded
        ]
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0

    # --- Pass 2: globally comparable edge strength -------------------------
    #     sim(a,b) = cooc(a,b) / (mass(a) * mass(b)) ** damping
    #
    # The SAME formula everywhere, so a score means the same thing graph-wide —
    # unlike the per-artist normalisation this replaced. `damping` controls how
    # much popularity is discounted; see BuilderConfig.similarity_damping for
    # why the default is 0.0 (full cosine over-corrects and inflates rare
    # co-occurrences). Popularity is handled in the API's cost function.
    damping = config.similarity_damping
    scored_adjacency: dict[str, list[tuple[str, float]]] = {}
    for mbid in sorted(known):
        mass_a = mass[mbid]
        scored = [
            (
                n.mbid,
                n.score / ((mass_a * mass[n.mbid]) ** damping) if damping else n.score,
            )
            for n in raw_lists[mbid]
            if n.mbid in known
        ]
        # Cap AFTER correction — the corrected ranking differs from the raw one.
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        scored_adjacency[mbid] = (
            scored
            if config.cap_strategy == "mutual_knn"
            else scored[: config.max_neighbours_per_artist]
        )

    # Rescale globally into 0-1, LOG-scaled against a robust maximum.
    #
    # Co-occurrence is power-law distributed, so linear scaling crushes the
    # bulk of edges to near-zero (measured: p50 0.022, p75 0.053), leaving
    # w_sim*(1-sim) almost constant and the similarity term unable to
    # discriminate. Log scaling spreads the mass across 0-1, the same reason
    # popularity is log-scaled in graph.py.
    all_scores = [s for edges in scored_adjacency.values() for _, s in edges]
    scale = float(np.percentile(all_scores, 99)) if all_scores else 1.0
    if scale <= 0:
        scale = 1.0
    log_scale = math.log1p(scale)
    logger.info("similarity scale (p99) = %.6g", scale)

    indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    for mbid, scored in scored_adjacency.items():
        edges = {
            dst: min(1.0, math.log1p(max(0.0, value)) / log_scale)
            for dst, value in scored
        }
        adjacency[mbid] = edges
        for dst, score in edges.items():
            indegree[dst] += score

    if config.cap_strategy == "mutual_knn":
        adjacency = mutual_knn_cap(adjacency, config.max_neighbours_per_artist)
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
