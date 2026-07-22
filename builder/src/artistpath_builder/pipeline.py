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


def damped_strength(
    cooc: float, mass_a: float, mass_b: float, damping: float
) -> float:
    """Popularity-damped edge strength, computed IN LOG SPACE.

        log1p(cooc) - d * (log mass_a + log mass_b)

    d = 0 is raw association, d = 0.5 is cosine, d = 1 is PMI up to a constant.

    No `- 2*log(median_mass)` centring: under the rank rescale it is a global
    additive constant and provably inert. It is mandatory only under the legacy
    clip rescale, where `rescale_scores` raises rather than silently emitting
    nan.

    No clamp at zero. Negative values are meaningful ordering information and
    the rank transform consumes them directly.
    """
    strength = math.log1p(max(0.0, cooc))
    if damping:
        strength -= damping * (math.log(max(mass_a, 1.0)) + math.log(max(mass_b, 1.0)))
    return strength


def rescale_scores(
    values: list[float], strategy: str, damping: float
) -> list[float]:
    """Map raw edge strengths into 0-1.

    `damping` is accepted so the degeneracy guard can be enforced here: under
    the clip rescale with d > 0 the centring term is mandatory, and without it
    the p99 collapses to zero and the whole array becomes nan.
    """
    if not values:
        return []

    if strategy == "p99_log_clip":
        # Legacy path: input is already log1p(cooc) from damped_strength at
        # d = 0, so exponentiate back to raw space to reproduce the original
        # expression exactly. Only valid at d = 0, which is the control arm.
        raw = [math.expm1(max(0.0, v)) for v in values]
        scale = float(np.percentile(raw, 99))
        if scale <= 0:
            raise ValueError(
                f"degenerate p99 ({scale}) under damping={damping}: the clip "
                "rescale requires the centring term when damping > 0. Use "
                "percentile_rank, or restore the centring."
            )
        log_scale = math.log1p(scale)
        return [
            min(1.0, math.log1p(max(0.0, v)) / log_scale) for v in raw
        ]

    if strategy == "percentile_rank":
        # Average rank (midrank / ECDF): every member of a tie group gets the
        # group's mean sequential rank, rather than an arbitrary sequential
        # rank that is a function of array order alone. Raw ListenBrainz
        # scores are session co-occurrence counts, and ~99.99% of them share
        # a value with at least one other edge — sequential ranking would
        # give those provably-identical edges different costs, ordered by
        # nothing but incidental position in the flattened array. Average
        # rank is a function of the *values*, so it is stable under any
        # reordering of equal-valued input (e.g. a different cap strategy),
        # which sequential ranking is not.
        #
        # This is computed explicitly (group by sorted value, average the
        # sequential ranks within each group, scatter back) rather than
        # relying on any incidental tie-breaking behaviour of argsort, so the
        # tie-equal property is guaranteed rather than accidental. It stays
        # deterministic: np.unique sorts on value, and grouping/summation are
        # both order-independent operations, so identical input still
        # produces byte-identical output.
        arr = np.asarray(values, dtype=np.float64)
        n = len(values)
        order = np.argsort(arr, kind="stable")
        sorted_vals = arr[order]
        sequential_ranks = np.arange(n, dtype=np.float64)
        _unique_vals, inverse, counts = np.unique(
            sorted_vals, return_inverse=True, return_counts=True
        )
        group_sums = np.bincount(
            inverse, weights=sequential_ranks, minlength=len(counts)
        )
        group_avg_ranks = group_sums / counts
        sorted_avg_ranks = group_avg_ranks[inverse]
        ranks = np.empty(n, dtype=np.float64)
        ranks[order] = sorted_avg_ranks
        denominator = max(n - 1, 1)
        return [float(r / denominator) for r in ranks]

    raise ValueError(f"unknown rescale strategy: {strategy!r}")


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
    #     score(a,b) = log1p(cooc(a,b)) - damping * (log(mass(a)) + log(mass(b)))
    #
    # Damping is applied in log space, as a subtraction — see damped_strength
    # above, which does the actual computation (no centring, no clamping).
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
            (n.mbid, damped_strength(n.score, mass_a, mass[n.mbid], damping))
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

    # Map raw strength into 0-1 per the configured strategy. See
    # BuilderConfig.similarity_rescale for why the legacy clip is a defect.
    flat: list[float] = []
    layout: list[tuple[str, list[str]]] = []
    for mbid, scored in scored_adjacency.items():
        layout.append((mbid, [dst for dst, _ in scored]))
        flat.extend(value for _dst, value in scored)

    rescaled = rescale_scores(
        flat, strategy=config.similarity_rescale, damping=config.similarity_damping
    )

    indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    cursor = 0
    for mbid, dsts in layout:
        edges = {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            cursor += 1
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
