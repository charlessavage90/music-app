import numpy as np

from artistpath_builder.graph import build_graph, largest_component, symmetrise
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
