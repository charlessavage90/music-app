import pytest

from artistpath_api.evaluation import (
    bfs_shortest_path,
    degree_percentile_threshold,
    edge_score,
    out_degree,
    path_metrics,
    similarity_only_path,
    summarise,
)
from tests.conftest import make_store


def test_out_degree_counts_neighbours():
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9)],
    )
    assert out_degree(store, 0) == 2
    assert out_degree(store, 1) == 1


def test_edge_score_returns_similarity_or_zero():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.73)]
    )
    assert edge_score(store, 0, 1) == pytest.approx(0.73, abs=1e-6)  # float32
    assert edge_score(store, 0, 0) == 0.0  # no self-edge


def test_hub_detection_flags_high_degree_interior_node():
    # Star centre (node 0, degree 3) sits interior on 1->0->2.
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    m = path_metrics(store, [1, 0, 2], hub_threshold=3)
    assert m.hub_traversed is True
    assert m.max_interior_degree == 3


def test_endpoints_are_not_counted_as_hubs():
    # The high-degree node is an endpoint, so it must not count as hub-traversal.
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    m = path_metrics(store, [0, 1], hub_threshold=3)
    assert m.hub_traversed is False


def test_bottleneck_is_the_weakest_link():
    # Path 0-1-2 with edge sims 0.9 and 0.2; bottleneck is 0.2.
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.2)],
    )
    m = path_metrics(store, [0, 1, 2], hub_threshold=99)
    assert m.bottleneck_sim == pytest.approx(0.2, abs=1e-6)  # float32
    assert m.mean_sim == pytest.approx(0.55, abs=1e-6)


def test_degree_percentile_threshold_is_monotonic_and_bounded():
    # A hub (node 0, degree 20) among 20 leaves (degree 1). The top-fraction
    # cutoff must lie within [min, max] degree, and a stricter percentile must
    # not give a lower cutoff. (On the real 75k graph top-1% = degree 357.)
    hub_edges = [(0, i, 0.9) for i in range(1, 21)]
    store = make_store(
        names=[str(i) for i in range(21)], popularity=[0.5] * 21,
        undirected_edges=hub_edges,
    )
    top1 = degree_percentile_threshold(store, 0.01)
    half = degree_percentile_threshold(store, 0.5)
    assert 1 <= half <= top1 <= 20


def test_bfs_finds_fewest_hops_route():
    # 0-1-2-3 and a direct 0-3; BFS must take the 1-hop direct edge.
    store = make_store(
        names=list("ABCD"), popularity=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (0, 3, 0.1)],
    )
    assert bfs_shortest_path(store, 0, 3) == [0, 3]


def test_similarity_only_prefers_strong_edges():
    # 0-2 weak direct; 0-1-2 strong. Similarity-only routing takes the strong pair.
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 2, 0.1), (0, 1, 0.95), (1, 2, 0.95)],
    )
    assert similarity_only_path(store, 0, 2) == [0, 1, 2]


def test_summarise_aggregates_hub_rate():
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    hub = path_metrics(store, [1, 0, 2], hub_threshold=3)      # hub-traversed
    no_hub = path_metrics(store, [1, 0], hub_threshold=99)     # not
    s = summarise([hub, no_hub])
    assert s["n"] == 2
    assert s["hub_traversal_rate"] == 0.5
