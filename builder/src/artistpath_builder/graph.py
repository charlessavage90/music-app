"""Graph assembly: symmetrise, prune to one component, emit CSR.

Pure functions over in-memory data. Determinism is a hard requirement here
(spec section 9) — every ordering decision is explicit.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from artistpath_builder.models import ArtistStats, EdgeType

Adjacency = dict[str, dict[str, float]]


@dataclass(slots=True)
class Graph:
    mbids: list[str]
    names: list[str]
    disambiguations: list[str]
    # Log-scaled score-weighted in-degree in 0-1. NOT a percentile, and NOT
    # fame — log §2.11/§2.12 record both conflations and what each cost.
    pop_raw: list[float]
    offsets: np.ndarray  # int32, length len(mbids) + 1
    neighbours: np.ndarray  # int32
    scores: np.ndarray  # float32
    edge_types: np.ndarray  # uint8
    # MusicBrainz-recorded Deezer artist ids, indexed by node id like every
    # other metadata list, "" where none is known. Lets the api resolve a clip
    # by artist identity rather than by name (`BYP-13`); see deezer_ids.py.
    #
    # DEFAULTED, and that is load-bearing twice over: `build_graph` is called
    # with three positional arguments by two FROZEN probes, and an empty list
    # makes `serialise` omit the key so their artifacts stay byte-identical.
    deezer_ids: list[str] = field(default_factory=list)
    # ListenBrainz total_user_count per node, or None where the instrument
    # measured no listeners. NOT popularity: `pop_raw` above is score-weighted
    # in-degree computed from this archive, while this is an external listener
    # count — log §2.11/§2.12 record what reading one as the other has cost.
    # A null is a measured absence and is never a floor value (FAM-AM1.8).
    #
    # DEFAULTED for the same two reasons as `deezer_ids`: frozen probes call
    # `build_graph` positionally, and an empty list makes `serialise` omit the
    # key so their artifacts stay byte-identical.
    fame_lb_raw: list[int | None] = field(default_factory=list)
    # LUX-4. Streaming deep links and structured MusicBrainz facts, all three
    # node-indexed and parallel to `mbids` exactly as `deezer_ids` is. The api
    # indexes them BY NODE ID, so alignment is the whole contract: a rotated
    # list would show every artist someone else's link and nothing downstream
    # could detect it.
    #
    # Ids are platform id TAILS, never URLs (`L4-D2`) -- a hostname baked into
    # tens of thousands of entries cannot be changed without a rebuild. Sources
    # are the frozen snapshots in dsp_links.py and artist_facts.py.
    #
    # DEFAULTED for the same two reasons as `deezer_ids` and `fame_lb_raw`
    # above: frozen probes call `build_graph` positionally, and an empty list
    # makes `serialise` omit the key so their artifacts stay byte-identical.
    spotify_ids: list[str] = field(default_factory=list)
    apple_ids: list[str] = field(default_factory=list)
    artist_facts: list[dict] = field(default_factory=list)

    @property
    def popularity(self) -> list[float]:
        """Read-only alias for the frozen probe scripts in builder/analysis/.

        Mapping table: builder/analysis/README.md.
        """
        return self.pop_raw

    @property
    def artist_count(self) -> int:
        return len(self.mbids)

    @property
    def edge_count(self) -> int:
        return int(self.neighbours.size)


def symmetrise(adjacency: Adjacency) -> Adjacency:
    """Mirror one-way edges, keeping the stronger score.

    Similarity is not mutual: A may list B without B listing A. Left alone,
    those become dead ends during pathfinding (spec section 3.1 step 4).
    """
    result: Adjacency = {node: dict(edges) for node, edges in adjacency.items()}
    for src, edges in adjacency.items():
        for dst, score in edges.items():
            result.setdefault(dst, {})
            result.setdefault(src, {})
            best = max(score, result[dst].get(src, 0.0), result[src].get(dst, 0.0))
            result[src][dst] = best
            result[dst][src] = best
    return result


def mutual_knn_cap(
    adjacency: Adjacency, k: int, ranking: Adjacency | None = None
) -> Adjacency:
    """Keep edge (u,v) only if v is in u's top-k AND u is in v's top-k.

    The cap this replaces was applied BEFORE symmetrisation. Symmetrisation
    adds a reverse edge for every incoming one and nothing bounds how many
    neighbour lists an artist appears in, so the cap truncated the obscure
    tail — where alternative routes are scarcest — while leaving hubs
    completely unbounded. A configured cap of 50 produced an observed maximum
    degree of 11,243.

    Mutual k-NN is the only formulation that both bounds degree at k and stays
    symmetric by construction: union-kNN does not bound degree, and capping
    after symmetrisation breaks symmetry again. It prunes harder than the old
    scheme, so callers must check largest-component retention.

    `ranking`, when given, supplies the values used to order each node's
    top-k; emitted scores still come from `adjacency`. It exists because the
    p99 clip collapses the top ~1% of scores to exactly 1.0, and ranking those
    tied values let the MBID tie-break decide which neighbours a saturated
    artist kept — which is how the most famous artists lost nearly all their
    edges (Phase 1 log §2.8). Callers that rescale destructively must pass the
    pre-rescale strengths here. `ranking` must cover exactly the nodes of
    `adjacency` (ValueError otherwise) and every edge of `adjacency`
    (KeyError otherwise — loud by design).

    Ties break on lowest MBID, matching every other ordering decision in this
    module (design §9).
    """
    if ranking is not None and set(ranking) != set(adjacency):
        raise ValueError(
            "ranking must cover exactly the nodes of adjacency; top-k "
            "selection over a different node set is undefined"
        )
    rank_of = ranking if ranking is not None else adjacency

    top_k: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(
            ((dst, rank_of[node][dst]) for dst in edges),
            key=lambda pair: (-pair[1], pair[0]),
        )
        top_k[node] = {dst for dst, _score in ranked[:k]}

    result: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in top_k[node] and node in top_k.get(dst, set()):
                result[node][dst] = score
    return result


class _desc:
    """Sort helper: reverses string order so ties drop the HIGHEST MBID first.

    Deliberately the opposite of every other tie-break in this module. It
    orders *deletions*, not selections, so dropping the highest MBID first
    leaves the lowest standing — which is the same artist mutual k-NN's
    lowest-MBID selection would have kept.
    """

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value

    def __lt__(self, other: "_desc") -> bool:
        return self.value > other.value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _desc) and self.value == other.value


def trimmed_union_cap(
    adjacency: Adjacency,
    top_j: int,
    degree_ceiling: int,
    *,
    ranking: Adjacency,
) -> Adjacency:
    """Keep edge (u,v) if EITHER endpoint ranks the other top-j, then trim to a
    hard degree ceiling by deleting the weakest edges.

    ADOPTED 2026-08-05 with the map switch, as Track B's `TUw-50-50` (cell
    `B-S1`). It is deliberately non-reciprocal where `mutual_knn_cap` is
    reciprocal: an artist whose own list is crowded with famous neighbours
    keeps the obscure neighbour that ranks *them* highly, which mutual k-NN
    discards. That is the supply difference the whole cap re-evaluation was
    about — see docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md.

    The union alone bounds NOTHING — a famous artist appears in unboundedly
    many neighbour lists, which is exactly the defect that killed the legacy
    pre-symmetrise cap (configured 50, observed max degree 11,243). The
    ceiling is what bounds it, and it deletes WHOLE EDGES rather than
    truncating one endpoint's row, because per-node truncation breaks symmetry
    again.

    BOUND: degree <= degree_ceiling by construction. A single pass suffices —
    nodes are processed in a fixed order and deletion only ever lowers a
    degree, so a node brought to the ceiling cannot later rise above it.

    Determinism (design §9): top-j ties break on lowest MBID; nodes are
    processed by (-degree, mbid); deletions are ordered by symmetric pair
    strength with ties dropping the highest MBID first. The surviving set is a
    function of the input alone.

    `ranking` supplies the values used to order both the top-j selection and
    the trim, for the same reason `mutual_knn_cap` takes one: the p99 clip
    ties the top ~1% of emitted scores at exactly 1.0, so selecting on them
    would let the MBID tie-break decide which neighbours a saturated artist
    kept (Phase 1 log §2.8). Emitted scores still come from `adjacency`.

    Equivalence to the frozen rule that was actually selected is pinned by
    test_graph.py::test_trimmed_union_cap_matches_the_frozen_track_b_implementation.
    """
    if set(ranking) != set(adjacency):
        raise ValueError(
            "ranking must cover exactly the nodes of adjacency; top-j "
            "selection over a different node set is undefined"
        )

    keep: dict[str, set[str]] = {}
    for node, edges in adjacency.items():
        ranked = sorted(edges, key=lambda dst: (-ranking[node][dst], dst))
        keep[node] = set(ranked[:top_j])

    # Union, then symmetrise on the stronger score, giving an undirected graph.
    unioned: Adjacency = {node: {} for node in adjacency}
    for node, edges in adjacency.items():
        for dst, score in edges.items():
            if dst in keep[node] or node in keep.get(dst, set()):
                unioned[node][dst] = score
    result = symmetrise(unioned)

    # Symmetric strength for the trim order: the pair's stronger unclipped
    # ranking value, so both endpoints agree on which edge is weakest.
    def strength(u: str, v: str) -> float:
        return max(
            ranking.get(u, {}).get(v, float("-inf")),
            ranking.get(v, {}).get(u, float("-inf")),
        )

    for node in sorted(result, key=lambda n: (-len(result[n]), n)):
        excess = len(result[node]) - degree_ceiling
        if excess <= 0:
            continue
        doomed = sorted(result[node], key=lambda v: (strength(node, v), _desc(v)))[
            :excess
        ]
        for victim in doomed:
            result[node].pop(victim, None)
            result[victim].pop(node, None)
    return result


def largest_component(adjacency: Adjacency) -> set[str]:
    """Return the biggest connected component.

    Keeping only this guarantees a path exists between any two artists the UI
    offers, so a "no path" result can only ever come from user exclusions
    (spec section 3.1 step 5). Ties break on lowest MBID for determinism.
    """
    unvisited = set(adjacency)
    best: set[str] = set()

    for start in sorted(adjacency):
        if start not in unvisited:
            continue
        component: set[str] = set()
        queue = deque([start])
        unvisited.discard(start)
        while queue:
            node = queue.popleft()
            component.add(node)
            for neighbour in adjacency.get(node, {}):
                if neighbour in unvisited:
                    unvisited.discard(neighbour)
                    queue.append(neighbour)
        if len(component) > len(best):
            best = component
    return best


def _log_scaled(counts: list[int]) -> list[float]:
    """Log-scale the popularity counts to 0-1 (spec section 4.1).

    Raw counts are power-law distributed; a linear scale would make every
    artist outside the top few hundred indistinguishable.

    The output is a rescaled VALUE, not a percentile: the log scale compresses
    the head, so equal steps here are wildly unequal steps in rank. That gap is
    what log §2.12 records as the currency error.
    """
    logs = [math.log1p(max(0, n)) for n in counts]
    low, high = min(logs), max(logs)
    span = high - low
    if span == 0:
        return [0.0] * len(logs)
    return [(value - low) / span for value in logs]


def build_graph(
    adjacency: Adjacency,
    stats: list[ArtistStats],
    edge_type: EdgeType,
    deezer_ids: dict[str, str] | None = None,
    fame_lb_raw: dict[str, int | None] | None = None,
    spotify_ids: dict[str, str] | None = None,
    apple_ids: dict[str, str] | None = None,
    artist_facts: dict[str, dict] | None = None,
) -> Graph:
    """Assemble CSR arrays. IDs are assigned in sorted-MBID order.

    `deezer_ids` is KEYWORD-OPTIONAL on purpose: `cb_build_variants.py:479` and
    `measure_headroom.py:151` are frozen and call this with three positional
    arguments. Omitting it yields an empty list, which `serialise` then omits
    from the metadata blob, so those probes' artifacts stay byte-identical.
    `fame_lb_raw` is keyword-optional for exactly the same reasons, as are
    LUX-4's `spotify_ids`, `apple_ids` and `artist_facts`.

    `fame_lb_raw` maps mbid -> listener count or None. It is passed as a dict
    and indexed here rather than pre-ordered by the caller, because node ids
    are assigned in this function: a caller building the list itself would be
    re-deriving `sorted(...)` and could silently disagree with it.
    """
    stats_by_mbid = {record.mbid: record for record in stats}
    mbids = sorted(set(adjacency) & set(stats_by_mbid))
    index = {mbid: i for i, mbid in enumerate(mbids)}

    names = [stats_by_mbid[m].name for m in mbids]
    disambiguations = [stats_by_mbid[m].disambiguation for m in mbids]
    # Score-weighted in-degree, computed from the archive during `build`.
    # There is no separate popularity source (findings 6f) — the field's old
    # name and the "distinct listeners" comment that used to sit here were both
    # inherited from a design that was never built.
    pop_raw = _log_scaled([stats_by_mbid[m].pop_indegree_scaled for m in mbids])

    offsets = np.zeros(len(mbids) + 1, dtype=np.int32)
    neighbours: list[int] = []
    scores: list[float] = []

    for i, mbid in enumerate(mbids):
        row = [
            (index[dst], score)
            for dst, score in adjacency[mbid].items()
            if dst in index
        ]
        row.sort(key=lambda pair: pair[0])  # deterministic within-row order
        for dst_id, score in row:
            neighbours.append(dst_id)
            scores.append(score)
        offsets[i + 1] = len(neighbours)

    return Graph(
        mbids=mbids,
        names=names,
        disambiguations=disambiguations,
        pop_raw=pop_raw,
        offsets=offsets,
        neighbours=np.asarray(neighbours, dtype=np.int32),
        scores=np.asarray(scores, dtype=np.float32),
        edge_types=np.full(len(neighbours), int(edge_type), dtype=np.uint8),
        # Indexed by node id, like every other metadata list above.
        deezer_ids=[deezer_ids.get(m, "") for m in mbids] if deezer_ids else [],
        # `is not None` rather than truthiness: a fame dict whose values are
        # all None is a legitimate measurement (nobody listened to anyone in
        # this population) and must not be silently discarded as "empty".
        fame_lb_raw=(
            [fame_lb_raw.get(m) for m in mbids] if fame_lb_raw is not None else []
        ),
        # LUX-4, projected here rather than by the caller for the reason this
        # function's docstring gives for `fame_lb_raw`: node ids are assigned
        # in THIS function, so a caller pre-ordering the list would be
        # re-deriving `sorted(...)` and could silently disagree with it.
        spotify_ids=[spotify_ids.get(m, "") for m in mbids] if spotify_ids else [],
        apple_ids=[apple_ids.get(m, "") for m in mbids] if apple_ids else [],
        artist_facts=(
            [artist_facts.get(m, {}) for m in mbids] if artist_facts else []
        ),
    )
