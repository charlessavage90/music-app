import numpy as np
import pytest

from artistpath_builder.graph import (
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
    trimmed_union_cap,
)
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C, D, E = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)


def _stats(*mbids_and_users):
    """Popularity is score-weighted in-degree, not listeners and not plays.

    `listen_count` is set here only to prove it is ignored.
    """
    return [
        ArtistStats(mbid=m, name=m[0].upper(), pop_indegree_scaled=u, listen_count=u * 7)
        for m, u in mbids_and_users
    ]


def test_symmetrise_mirrors_one_way_edges():
    # A one-way edge is a dead end: you can reach B from A but never return.
    adjacency = {A: {B: 0.8}, B: {}}
    result = symmetrise(adjacency)
    assert result[B][A] == 0.8


def test_symmetrise_keeps_the_stronger_score():
    adjacency = {A: {B: 0.3}, B: {A: 0.9}}
    result = symmetrise(adjacency)
    assert result[A][B] == 0.9
    assert result[B][A] == 0.9


def test_largest_component_discards_islands():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {D: 1.0}, D: {C: 1.0}, E: {}}
    assert largest_component(adjacency) == {A, B}


def test_largest_component_is_deterministic_when_sizes_tie():
    # Two components of equal size: the one containing the lowest MBID wins,
    # so the artifact is reproducible.
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {D: 1.0}, D: {C: 1.0}}
    assert largest_component(adjacency) == {A, B}


def test_build_graph_assigns_ids_in_mbid_order():
    adjacency = {B: {A: 1.0}, A: {B: 1.0}}
    graph = build_graph(adjacency, _stats((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
    assert graph.mbids == [A, B]


def test_csr_offsets_are_valid():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    graph = build_graph(
        adjacency, _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    assert graph.offsets[0] == 0
    assert graph.offsets[-1] == len(graph.neighbours)
    assert len(graph.offsets) == len(graph.mbids) + 1
    assert np.all(np.diff(graph.offsets) >= 0)


def test_every_edge_is_reciprocated_in_csr():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}, C: {A: 0.4}}
    graph = build_graph(
        symmetrise(adjacency), _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    for src in range(len(graph.mbids)):
        for i in range(graph.offsets[src], graph.offsets[src + 1]):
            dst = int(graph.neighbours[i])
            back = graph.neighbours[graph.offsets[dst] : graph.offsets[dst + 1]]
            assert src in back


def test_neighbours_are_sorted_within_each_row():
    adjacency = {A: {B: 0.1, C: 0.9}, B: {A: 0.1}, C: {A: 0.9}}
    graph = build_graph(
        adjacency, _stats((A, 10), (B, 20), (C, 30)), EdgeType.BEHAVIOURAL
    )
    row = graph.neighbours[graph.offsets[0] : graph.offsets[1]]
    assert list(row) == sorted(row)


def test_popularity_is_log_scaled_to_unit_range():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _stats((A, 1), (B, 1_000_000)), EdgeType.BEHAVIOURAL)
    assert min(graph.pop_raw) == 0.0
    assert max(graph.pop_raw) == 1.0


def test_popularity_uses_the_indegree_slot_not_listen_count():
    # A has a far larger in-degree slot but fewer plays, so it must rank
    # higher: listen_count is archived and never routed on.
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    stats = [
        ArtistStats(mbid=A, name="A", pop_indegree_scaled=1000, listen_count=1000),
        ArtistStats(mbid=B, name="B", pop_indegree_scaled=10, listen_count=999_999),
    ]
    graph = build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)
    assert graph.pop_raw[graph.mbids.index(A)] > graph.pop_raw[
        graph.mbids.index(B)
    ]


def test_edges_carry_the_source_edge_type():
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    graph = build_graph(adjacency, _stats((A, 10), (B, 20)), EdgeType.BEHAVIOURAL)
    assert np.all(graph.edge_types == EdgeType.BEHAVIOURAL)


def test_mutual_knn_bounds_every_node_degree():
    # A star: the centre "hub" is in everyone's list, so pre-symmetrisation
    # capping leaves it unbounded. Mutual k-NN must bound it at k.
    adjacency = {"hub": {}}
    for i in range(10):
        leaf = f"leaf{i}"
        adjacency["hub"][leaf] = 1.0 - i * 0.01
        adjacency[leaf] = {"hub": 1.0}
    capped = mutual_knn_cap(adjacency, k=3)
    assert all(len(edges) <= 3 for edges in capped.values())


def test_mutual_knn_keeps_only_edges_in_both_top_k():
    # a's top-1 is b; b's top-1 is c. So a-b survives only if b also ranks a
    # first, which it does not.
    adjacency = {
        "a": {"b": 0.9, "c": 0.1},
        "b": {"c": 0.9, "a": 0.5},
        "c": {"b": 0.9, "a": 0.1},
    }
    capped = mutual_knn_cap(adjacency, k=1)
    assert "b" in capped["c"] and "c" in capped["b"]
    assert "b" not in capped.get("a", {})


def test_mutual_knn_output_is_symmetric():
    adjacency = {
        "a": {"b": 0.9, "c": 0.8},
        "b": {"a": 0.9, "c": 0.7},
        "c": {"a": 0.8, "b": 0.7},
    }
    capped = mutual_knn_cap(adjacency, k=2)
    for src, edges in capped.items():
        for dst, score in edges.items():
            assert capped[dst][src] == score


def test_mutual_knn_breaks_score_ties_on_lowest_mbid():
    # Determinism (design §9): equal scores must resolve the same way every run.
    adjacency = {
        "a": {"b": 0.5, "c": 0.5},
        "b": {"a": 0.5},
        "c": {"a": 0.5},
    }
    first = mutual_knn_cap(adjacency, k=1)
    second = mutual_knn_cap(adjacency, k=1)
    assert first == second
    assert "b" in first["a"]  # lowest mbid wins the tie


def test_mutual_knn_is_a_noop_below_the_cap():
    adjacency = {"a": {"b": 0.9}, "b": {"a": 0.9}}
    assert mutual_knn_cap(adjacency, k=50) == adjacency


def test_symmetrise_preserves_the_mutual_knn_degree_bound():
    # The invariant the old scheme never satisfied: after symmetrisation, no
    # node exceeds the cap. Nothing in the codebase asserted this, which is how
    # a cap of 50 and a max degree of 11,243 coexisted unnoticed.
    adjacency = {"hub": {}}
    for i in range(20):
        leaf = f"leaf{i:02d}"
        adjacency["hub"][leaf] = 1.0 - i * 0.01
        adjacency[leaf] = {"hub": 1.0}
    capped = symmetrise(mutual_knn_cap(adjacency, k=4))
    assert max(len(edges) for edges in capped.values()) <= 4


def test_mutual_knn_ranks_on_the_ranking_argument_when_given():
    # The Phase 1 log §2.8 defect scenario: emitted scores tied at the p99
    # ceiling, unclipped strengths distinct. Selection must follow the
    # ranking, not fall through to the MBID tie-break over the tied scores.
    adjacency = {
        "a": {"e": 1.0, "c": 1.0},  # both clipped to the ceiling
        "e": {"a": 1.0},
        "c": {"a": 1.0},
    }
    ranking = {
        "a": {"e": 5.3, "c": 5.0},  # unclipped: e is genuinely stronger
        "e": {"a": 5.3},
        "c": {"a": 5.0},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert "e" in capped["a"]
    assert "c" not in capped["a"]


def test_mutual_knn_without_ranking_keeps_the_old_tie_break():
    # Same inputs, no ranking: the lowest MBID wins the tie, as before.
    adjacency = {
        "a": {"e": 1.0, "c": 1.0},
        "e": {"a": 1.0},
        "c": {"a": 1.0},
    }
    capped = mutual_knn_cap(adjacency, k=1)
    assert "c" in capped["a"]
    assert "e" not in capped["a"]


def test_mutual_knn_emits_adjacency_scores_not_ranking_values():
    # The ranking decides membership only; the artifact still carries the
    # rescaled scores.
    adjacency = {
        "a": {"e": 1.0},
        "e": {"a": 1.0},
    }
    ranking = {
        "a": {"e": 5.3},
        "e": {"a": 5.3},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert capped["a"]["e"] == 1.0


def test_mutual_knn_ranking_ties_still_break_on_lowest_mbid():
    # Determinism (design §9) must survive the new argument: genuinely tied
    # unclipped strengths resolve the same way every run.
    adjacency = {
        "a": {"e": 0.9, "c": 0.8},
        "e": {"a": 0.9},
        "c": {"a": 0.8},
    }
    ranking = {
        "a": {"e": 2.0, "c": 2.0},
        "e": {"a": 2.0},
        "c": {"a": 2.0},
    }
    capped = mutual_knn_cap(adjacency, k=1, ranking=ranking)
    assert "c" in capped["a"]


def test_mutual_knn_rejects_ranking_with_a_different_node_set():
    with pytest.raises(ValueError, match="ranking"):
        mutual_knn_cap({"a": {}}, k=1, ranking={"b": {}})


def test_graph_exposes_popularity_as_a_read_only_alias_for_pop_raw():
    """The frozen probe scripts in builder/analysis/ read `.popularity`.

    They are deliberate records of what was executed, never updated, and not
    part of any suite — so a future rename would break the project's audit
    trail silently. Mapping table: builder/analysis/README.md.
    """
    graph = build_graph(
        {A: {B: 0.5}, B: {A: 0.5}},
        [
            ArtistStats(mbid=A, name="A", pop_indegree_scaled=10, listen_count=0),
            ArtistStats(mbid=B, name="B", pop_indegree_scaled=1, listen_count=0),
        ],
        EdgeType.BEHAVIOURAL,
    )
    assert graph.popularity == graph.pop_raw
    with pytest.raises(AttributeError):
        graph.popularity = [0.0, 0.0]


# --- trimmed_union_cap (MSW-, the adopted TUw-50-50 supply rule) -----------


def _random_adjacency(seed: int, n: int = 60, per_node: int = 12) -> dict:
    """Synthetic scored adjacency shaped like pipeline output.

    Deliberately asymmetric: each node samples its own neighbour list, so
    reverse-only edges arise, which is the case the union rule exists for.
    """
    import random

    rng = random.Random(seed)
    mbids = [f"{i:04d}" + "x" * 32 for i in range(n)]
    adjacency: dict[str, dict[str, float]] = {}
    for m in mbids:
        dsts = rng.sample([x for x in mbids if x != m], per_node)
        adjacency[m] = {d: rng.random() for d in dsts}
    return adjacency


def test_trimmed_union_cap_bounds_degree_and_is_symmetric():
    adjacency = _random_adjacency(1)
    result = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
    for node, edges in result.items():
        assert len(edges) <= 5
        for dst in edges:
            assert node in result[dst], "must stay symmetric after trimming"


def test_trimmed_union_cap_is_deterministic():
    adjacency = _random_adjacency(2)
    a = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
    b = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
    assert a == b


def test_trimmed_union_cap_keeps_reverse_only_edges_under_the_ceiling():
    # C ranks B but B's own top-1 is A. Mutual k-NN would delete C-B; the
    # union admits it, and the ceiling is high enough to keep it. That
    # difference is the whole point of this rule.
    adjacency = {
        A: {B: 0.9},
        B: {A: 0.9, C: 0.5},
        C: {B: 0.5},
    }
    result = trimmed_union_cap(adjacency, 1, 5, ranking=adjacency)
    assert C in result[B]
    assert B in result[C]
    # and the mutual rule, on the same input, does delete it
    assert C not in mutual_knn_cap(adjacency, 1)[B]


def test_trimmed_union_cap_matches_the_frozen_track_b_implementation():
    """The port is equivalent to the frozen Track B cap on random input.

    Imports the frozen module read-only, which is the sanctioned direction
    (builder/analysis/README.md): never write shipped code against a frozen
    probe, but pinning a port to one with a test is what keeps the adopted
    rule the rule that was actually selected.
    """
    import sys
    from pathlib import Path

    frozen_dir = (
        Path(__file__).resolve().parents[1]
        / "analysis"
        / "2026-07-30-track-b-cap-selection"
    )
    sys.path.insert(0, str(frozen_dir))
    try:
        from cb_build_variants import cap_trimmed_union
    finally:
        sys.path.remove(str(frozen_dir))

    for seed in (3, 4, 5):
        adjacency = _random_adjacency(seed)
        frozen = cap_trimmed_union(
            adjacency, adjacency, {}, j=5, d=5, trim="weakest_first"
        )
        ported = trimmed_union_cap(adjacency, 5, 5, ranking=adjacency)
        assert ported == frozen, f"seed {seed}: port diverges from the frozen cap"


def test_trimmed_union_cap_deletion_ties_drop_the_highest_mbid():
    """Deletion order is the OPPOSITE tie-break to selection, and it is load-bearing.

    Four neighbours of the hub at IDENTICAL strength, ceiling 3, so exactly
    one must be deleted. Dropping the highest MBID leaves the same artist a
    lowest-MBID *selection* rule would have kept.

    This case is not reachable from random float strengths — every pair is
    distinct there — so the frozen-equivalence test above passes whatever this
    tie-break does. Verified by perturbation: flipping `_desc(v)` to `v` leaves
    that test green and turns this one red.
    """
    hub = "h" * 36
    n1, n2, n3, n4 = ("1" * 36, "2" * 36, "3" * 36, "4" * 36)
    adjacency = {
        hub: {n1: 0.5, n2: 0.5, n3: 0.5, n4: 0.5},
        n1: {hub: 0.5},
        n2: {hub: 0.5},
        n3: {hub: 0.5},
        n4: {hub: 0.5},
    }
    result = trimmed_union_cap(adjacency, 50, 3, ranking=adjacency)
    assert len(result[hub]) == 3
    assert n4 not in result[hub], "the highest MBID is the one deleted"
    assert hub not in result[n4], "and the deletion is symmetric"
    assert {n1, n2, n3} == set(result[hub])


def test_trimmed_union_cap_deletion_ties_match_the_frozen_rule():
    """The tie case above, checked against the frozen Track B implementation."""
    import sys
    from pathlib import Path

    frozen_dir = (
        Path(__file__).resolve().parents[1]
        / "analysis"
        / "2026-07-30-track-b-cap-selection"
    )
    sys.path.insert(0, str(frozen_dir))
    try:
        from cb_build_variants import cap_trimmed_union
    finally:
        sys.path.remove(str(frozen_dir))

    hub = "h" * 36
    neighbours = [str(i) * 36 for i in range(1, 6)]
    adjacency = {hub: {n: 0.5 for n in neighbours}}
    for n in neighbours:
        adjacency[n] = {hub: 0.5}

    frozen = cap_trimmed_union(adjacency, adjacency, {}, j=50, d=3,
                               trim="weakest_first")
    ported = trimmed_union_cap(adjacency, 50, 3, ranking=adjacency)
    assert ported == frozen
