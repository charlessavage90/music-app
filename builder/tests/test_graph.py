import numpy as np
import pytest

from artistpath_builder.graph import (
    build_graph,
    largest_component,
    mutual_knn_cap,
    symmetrise,
)
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C, D, E = ("a" * 36, "b" * 36, "c" * 36, "d" * 36, "e" * 36)


def _stats(*mbids_and_users):
    """Popularity is distinct listeners, not plays (spec 4.1)."""
    return [
        ArtistStats(mbid=m, name=m[0].upper(), user_count=u, listen_count=u * 7)
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
    assert min(graph.popularity) == 0.0
    assert max(graph.popularity) == 1.0


def test_popularity_uses_user_count_not_listen_count():
    # A has fewer plays but more distinct listeners, so it must rank higher.
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    stats = [
        ArtistStats(mbid=A, name="A", user_count=1000, listen_count=1000),
        ArtistStats(mbid=B, name="B", user_count=10, listen_count=999_999),
    ]
    graph = build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)
    assert graph.popularity[graph.mbids.index(A)] > graph.popularity[
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
