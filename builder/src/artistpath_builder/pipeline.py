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
from artistpath_builder.config import PRODUCTION_ALGORITHM, BuilderConfig
from artistpath_builder.graph import (
    Adjacency,
    Graph,
    build_graph,
    largest_component,
    mutual_knn_cap,
    trimmed_union_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats
from artistpath_builder.artist_facts import load_artist_facts
from artistpath_builder.deezer_ids import load_deezer_ids
from artistpath_builder.dsp_links import load_dsp_links
from artistpath_builder.fame import load_fame
from artistpath_builder.featured_credit_drop import load_featured_credit_drop_mbids
from artistpath_builder.no_release_drop import load_drop_mbids
from artistpath_builder.unlistenable_drop import (
    PopulationNotCensused,
    load_unlistenable_list,
)
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
        # expression exactly. Only valid at d = 0, which is the adopted value.
        raw = [math.expm1(max(0.0, v)) for v in values]
        scale = float(np.percentile(raw, 99))
        if scale <= 0:
            raise ValueError(
                f"degenerate p99 ({scale}) under damping={damping}: the clip "
                "rescale requires the `- 2*log(median_mass)` centring term "
                "when damping > 0, and that term is not implemented. Restore "
                "it before raising similarity_damping above 0."
            )
        log_scale = math.log1p(scale)
        rescaled = [min(1.0, math.log1p(max(0.0, v)) / log_scale) for v in raw]
        # CEX-M1: both figures are population-dependent and price the router's
        # primary term (w_sim). Logged so two builds can be compared rather
        # than assumed.
        saturated = sum(1 for value in rescaled if value >= 1.0)
        logger.info(
            "rescale p99 scale=%.6g | saturated edges %d of %d (%.3f%%)",
            scale,
            saturated,
            len(rescaled),
            100.0 * saturated / len(rescaled),
        )
        return rescaled

    raise ValueError(
        f"unsupported rescale strategy: {strategy!r}. 'percentile_rank' lost "
        "Phase 2 and its implementation was removed (spec §8 risk 4); "
        "'p99_log_clip' is the only supported rescale. See execution log §16."
    )


def similar_prefix(config: BuilderConfig, source: SimilaritySource) -> str:
    """Archive key prefix for this config's similarity responses.

    RC-H3, build side: responses are keyed by algorithm, so a build reads only
    the tree its own algorithm wrote. Production keeps the flat layout (see
    Crawler.similar_key); every other algorithm has a sub-tree.

    Extracted so the `fame` stage enumerates exactly the population `build`
    will read, from one definition rather than two. A second copy of this rule
    is precisely the divergence class test_pipeline_mirrors.py guards.
    """
    if config.algorithm == PRODUCTION_ALGORITHM:
        return f"similar/{source.name}/"
    return f"similar/{source.name}/{config.algorithm}/"


def archive_artists(
    archive: RawArchive, config: BuilderConfig, source: SimilaritySource
) -> set[str]:
    """Every artist with an archived similarity response for this config.

    A superset of the built graph's nodes — a node also needs to appear as
    someone's neighbour, and the largest-component step prunes further — which
    is the property the `fame` stage wants: fetch for everything that could
    end up in the graph, so `load_fame` cannot come up short.
    """
    prefix = similar_prefix(config, source)
    found: set[str] = set()
    for key in archive.keys():
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            continue
        found.add(mbid)
    return found


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
    prefix = similar_prefix(config, source)
    payloads: dict[str, bytes] = {}
    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        mbid = key[len(prefix) : -len(".json")]
        if "/" in mbid:
            # A scoped sub-tree nested under the flat production layout —
            # another algorithm's data, never this build's.
            continue
        payload = archive.get(key)
        if payload is not None:
            payloads[mbid] = payload

    known = set(payloads)
    # The archive's full artist set, captured before any drop: this is the
    # population identity the ULF- census manifest is checked against below.
    # Checked pre-drop deliberately — the censused set was recorded over the
    # raw archive, so a drop-shrunken `known` would mask an extension.
    archive_population = frozenset(known)

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

    # Nameless artists are dropped, unconditionally (owner decision
    # 2026-07-28, recorded in NEXT.md; REQ-2). An artist whose name never
    # appears in any neighbour row is unsearchable, clipless, and renderable
    # only as a blank card. Dropped here, beside the placeholder entities and
    # before the mass computation, so it contributes to no marginal — and a
    # neighbour stranded by the drop falls out at the largest-component
    # prune rather than dangling.
    #
    # Backfilling names by MBID was the declined alternative, and it is also
    # impossible: the three most popular nameless MBIDs in the adopted
    # artifact return "Artist not found" from MusicBrainz (owner, 2026-07-29).
    # They are deleted or merged upstream entities that survive in the
    # similarity data. A future crawl can mint more the same way, so this is a
    # standing build rule rather than a one-off patch.
    nameless = {
        mbid
        for mbid, (name, _disambiguation) in identities.items()
        if not name.strip()
    }
    # An artist with an archived response that never appears as anyone's
    # neighbour has no identity row at all: same defect, same fate.
    nameless |= known - identities.keys()
    if nameless & known:
        logger.info("dropped %d nameless artists", len(nameless & known))
    excluded |= nameless
    known -= nameless

    # The no-release tail is dropped by the same mechanism and in the same
    # place, and for the same reason: before the mass computation, so a dropped
    # artist contributes to no marginal. Owner decision 2026-08-01 (NEXT.md) —
    # keep a release-less artist only where a commercial-DSP link exists and a
    # clip resolves. The rule is ADOPTED; this applies it and never re-derives
    # it, and the list is a frozen snapshot rather than a build-time lookup
    # (no_release_drop.py explains why that is mandatory, not merely tidy).
    #
    # This is not the old graph minus rows: every surviving artist's mass, and
    # so every score and every cap decision, is computed with these artists
    # absent. Removing them additionally strands ~127 artists at the
    # largest-component prune on the adopted graph — a lower bound, since a
    # real build re-selects neighbours.
    #
    # The list is selected by `config.algorithm` — the same value that chose
    # the archive sub-tree above, so a build applies its own population's list
    # or refuses. It never borrows another's; see no_release_drop.py.
    if config.drop_no_release_tail:
        no_release = load_drop_mbids(config.algorithm) & known
        if no_release:
            logger.info("dropped %d no-release-tail artists", len(no_release))
        excluded |= no_release
        known -= no_release

    # The featured-credit filter drops by the same mechanism, in the same
    # place, for the same reason: before the mass computation, so a dropped
    # artist contributes to no marginal. It covers the class the no-release
    # rule structurally cannot see — artists whose credits count as release
    # groups while they have no primary-artist existence (rule document:
    # specs/2026-08-03-featured-credit-filter-rule.md, FCF-). Same per-
    # population list selection, same refusal for an uncensused algorithm,
    # same frozen-snapshot mandate; featured_credit_drop.py carries the why.
    # The two drops are disjoint by construction (this class requires >= 1
    # release-group credit; the no-release tail requires zero), so their
    # application order cannot matter — but both run before Pass 1, which is
    # the invariant the ordering tests pin.
    if config.drop_featured_credit:
        featured = load_featured_credit_drop_mbids(config.algorithm) & known
        if featured:
            logger.info("dropped %d featured-credit artists", len(featured))
        excluded |= featured
        known -= featured

    # The un-listenable filter (ULF-, 2026-08-05) drops by the same
    # mechanism, in the same place, for the same reason: before the mass
    # computation. It supersedes the two drops above without reversing
    # either — both classes are strict subsets of ULC-D2's and their frozen
    # verdicts carry — so applying all three is identical to applying this
    # one; the older flags stay for era-pinned probes (ULF-3).
    #
    # NEW against the siblings, and it is ULC-F1: the list carries the
    # censused population, and an archive containing artists the census
    # never evaluated REFUSES to build. Algorithm-keyed selection alone is
    # identity only while one algorithm means one crawl; a crawl extension
    # breaks that silently, and this is the loud alternative.
    if config.drop_unlistenable:
        ulf = load_unlistenable_list(
            config.algorithm, config.unlistenable_list_path
        )
        unevaluated = archive_population - ulf.censused_mbids
        if unevaluated:
            sample = ", ".join(sorted(unevaluated)[:3])
            raise PopulationNotCensused(
                f"this archive contains {len(unevaluated)} artist(s) the "
                f"ULF- census for {config.algorithm!r} never evaluated "
                f"(e.g. {sample}). The population grew — likely a crawl "
                "extension — so the frozen list would silently under-filter. "
                "Re-census the population (spec 2026-08-05, ULF-5) or build "
                "with drop_unlistenable=False, which is an experimental "
                "control and never a shipping configuration."
            )
        unlistenable = ulf.drop_mbids & known
        if unlistenable:
            logger.info("dropped %d un-listenable artists", len(unlistenable))
        excluded |= unlistenable
        known -= unlistenable

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
        # Uncapped here: mutual_knn_cap below applies the cap symmetrically,
        # once both directions are known. (The legacy pre_symmetrise strategy
        # truncated at this point instead; it was removed in Phase 2 — see
        # BuilderConfig.cap_strategy.)
        scored_adjacency[mbid] = scored

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

    score_weighted_indegree: dict[str, float] = defaultdict(float)
    adjacency: Adjacency = {}
    cursor = 0
    for mbid, dsts in layout:
        edges = {}
        for dst in dsts:
            edges[dst] = rescaled[cursor]
            cursor += 1
        adjacency[mbid] = edges
        for dst, score in edges.items():
            score_weighted_indegree[dst] += score

    # Rank the cap on UNCLIPPED strengths. The clip rescale ties the top ~1%
    # of scores at exactly 1.0; ranking those tied values let the MBID
    # tie-break decide which neighbours a saturated artist kept, collapsing
    # the most famous artists to near-zero degree (Phase 1 log §2.8). The
    # emitted scores are still the rescaled ones.
    ranking: Adjacency = {
        mbid: {dst: strength for dst, strength in scored}
        for mbid, scored in scored_adjacency.items()
    }
    # Both strategies rank on the unclipped strengths above and both bound
    # degree; they differ in reciprocity. mutual_knn keeps an edge only if
    # BOTH endpoints rank the other top-k; trimmed_union keeps it if EITHER
    # does, then trims to a ceiling. See BuilderConfig.cap_strategy.
    if config.cap_strategy == "trimmed_union":
        adjacency = trimmed_union_cap(
            adjacency,
            config.union_top_j,
            config.union_degree_ceiling,
            ranking=ranking,
        )
    else:
        adjacency = mutual_knn_cap(
            adjacency, config.max_neighbours_per_artist, ranking=ranking
        )
    adjacency = symmetrise(adjacency)
    keep = largest_component(adjacency)
    logger.info("largest component: %d of %d artists", len(keep), len(adjacency))

    pruned: Adjacency = {
        node: {dst: score for dst, score in edges.items() if dst in keep}
        for node, edges in adjacency.items()
        if node in keep
    }

    # In-degree is a float; the ArtistStats slot is an integer. Scale to
    # preserve ordering — build_graph log-scales it anyway.
    stats = [
        ArtistStats(
            mbid=mbid,
            name=identities.get(mbid, ("", ""))[0],
            pop_indegree_scaled=round(score_weighted_indegree[mbid] * 1000),
            listen_count=0,  # not used; popularity is score-weighted in-degree
            disambiguation=identities.get(mbid, ("", ""))[1],
        )
        for mbid in keep
    ]

    # Fame is read from the ARCHIVE, never fetched: `build` is offline (spec
    # §9), which is what the replay test's raising fetcher proves. `load_fame`
    # refuses rather than defaulting, so a build whose fetch population has
    # drifted from its similarity population stops here instead of shipping
    # artists priced by a made-up listener count (MSW-G3).
    #
    # Asked for `keep` — the pruned node set — rather than the whole archive:
    # those are exactly the artists that reach the artifact, so an artist the
    # largest-component step discarded cannot block a build by lacking a value
    # nothing would have read.
    fame = load_fame(archive, sorted(keep)) if config.require_fame else None

    # Deezer artist ids ride along in the metadata blob so the api can resolve a
    # clip by artist identity rather than by name (`BYP-13` — a card playing a
    # clip by a different artist of the SAME NAME). Applied unconditionally and
    # with no config knob: it changes no edge, no score and no node, so there is
    # nothing for a factor table to hold constant. A frozen snapshot, never a
    # build-time lookup — deezer_ids.py explains why that is mandatory.
    # LUX-4 rides along the same way and under the same rule: frozen snapshots
    # read from package data, never a build-time network lookup. Like the
    # deezer ids above they change no edge, no score and no node, so there is
    # nothing for a factor table to hold constant.
    #
    # Passed as DICTS, not pre-ordered lists: node ids are assigned inside
    # `build_graph`, and a caller ordering them here would be re-deriving
    # `sorted(...)` and could silently disagree with it.
    spotify_ids, apple_ids = load_dsp_links()
    return build_graph(
        pruned,
        stats,
        source.edge_type,
        deezer_ids=load_deezer_ids(),
        fame_lb_raw=fame,
        spotify_ids=spotify_ids,
        apple_ids=apple_ids,
        artist_facts=load_artist_facts(),
    )
