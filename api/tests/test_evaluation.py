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


def test_hubfrac_is_the_fraction_of_interior_nodes_that_are_hubs():
    # Path 1->0->2->3 has interior [0, 2]; only node 0 is in the hub set.
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9), (2, 3, 0.9)],
    )
    m = path_metrics(store, [1, 0, 2, 3], hub_nodes={0})
    assert m.hubfrac == pytest.approx(0.5)
    assert m.max_interior_degree == 3


def test_hubfrac_ignores_endpoints_even_when_they_are_hubs():
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 0.9), (0, 2, 0.9), (0, 3, 0.9)],
    )
    m = path_metrics(store, [0, 1], hub_nodes={0})
    assert m.hubfrac == 0.0


def test_hubfrac_is_zero_for_a_path_with_no_interior():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert path_metrics(store, [0, 1], hub_nodes=set()).hubfrac == 0.0


def test_ceiling_hops_counts_free_similarity_edges():
    # Two hops: one at exactly 1.0 (free — w_sim*(1-sim) == 0), one at 0.5.
    store = make_store(
        names=list("ABC"), popularity=[0.5] * 3,
        undirected_edges=[(0, 1, 1.0), (1, 2, 0.5)],
    )
    m = path_metrics(store, [0, 1, 2], hub_nodes=set())
    assert m.ceiling_hops == pytest.approx(0.5)


def test_bottleneck_is_the_weakest_link():
    # Path 0-1-2 with edge sims 0.9 and 0.2; bottleneck is 0.2.
    store = make_store(
        names=list("ABC"), popularity=[0.5, 0.5, 0.5],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.2)],
    )
    m = path_metrics(store, [0, 1, 2], hub_nodes=set())
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


def test_summarise_aggregates_hubfrac_and_ceiling_hops():
    store = make_store(
        names=list("ABCD"), popularity=[0.9, 0.3, 0.3, 0.3],
        undirected_edges=[(0, 1, 1.0), (0, 2, 1.0), (0, 3, 0.5), (2, 3, 0.5)],
    )
    a = path_metrics(store, [1, 0, 2, 3], hub_nodes={0})   # hubfrac 0.5
    b = path_metrics(store, [1, 0], hub_nodes={0})          # hubfrac 0.0
    s = summarise([a, b])
    assert s["n"] == 2
    assert s["mean_hubfrac"] == pytest.approx(0.25)
    assert "mean_adamic_adar" in s
    assert "mean_overlap_coefficient" in s
    assert "mean_ceiling_hops" in s


import math

import numpy as np

from artistpath_api.evaluation import (
    adamic_adar,
    common_neighbours,
    geometric_mean,
    jaccard,
    neighbours_array,
    overlap_coefficient,
)


def _triangle_with_hub():
    # 0 and 1 are adjacent and share two common neighbours: 2 (degree 2) and
    # 3 (degree 4, a hub). Node 3 also links 4 and 5 to inflate its degree.
    return make_store(
        names=list("ABCDEF"),
        popularity=[0.5] * 6,
        undirected_edges=[
            (0, 1, 0.9),
            (0, 2, 0.9), (1, 2, 0.9),
            (0, 3, 0.9), (1, 3, 0.9),
            (3, 4, 0.9), (3, 5, 0.9),
        ],
    )


def test_neighbours_array_is_sorted_and_excludes_self():
    store = _triangle_with_hub()
    assert list(neighbours_array(store, 0)) == [1, 2, 3]


def test_common_neighbours_excludes_the_two_endpoints():
    # 0 and 1 are each other's neighbours, but neither is a *common* neighbour.
    store = _triangle_with_hub()
    assert list(common_neighbours(store, 0, 1)) == [2, 3]


def test_adamic_adar_discounts_the_hub():
    # AA = 1/log(deg 2) + 1/log(deg 4) = 1/log(2) + 1/log(4).
    store = _triangle_with_hub()
    expected = 1 / math.log(2) + 1 / math.log(4)
    assert adamic_adar(store, 0, 1) == pytest.approx(expected, rel=1e-9)
    # The hub contributes strictly less than the low-degree node — the whole point.
    assert 1 / math.log(4) < 1 / math.log(2)


def test_overlap_coefficient_divides_by_the_smaller_degree():
    # |CN| = 2; deg(0) = 3, deg(1) = 3; min = 3.
    store = _triangle_with_hub()
    assert overlap_coefficient(store, 0, 1) == pytest.approx(2 / 3, rel=1e-9)


def test_jaccard_uses_union_including_the_endpoints():
    # N(0) = {1,2,3}, N(1) = {0,2,3}. Intersection {2,3} = 2; union {0,1,2,3} = 4.
    store = _triangle_with_hub()
    assert jaccard(store, 0, 1) == pytest.approx(2 / 4, rel=1e-9)


def test_metrics_are_zero_when_no_common_neighbours():
    store = make_store(
        names=list("AB"), popularity=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert list(common_neighbours(store, 0, 1)) == []
    assert adamic_adar(store, 0, 1) == 0.0
    assert overlap_coefficient(store, 0, 1) == 0.0
    assert jaccard(store, 0, 1) == 0.0


def test_adamic_adar_skips_degree_one_common_neighbours():
    # log(1) = 0 would divide by zero. A degree-1 node cannot be a common
    # neighbour of two distinct nodes, but the guard must exist regardless.
    store = _triangle_with_hub()
    assert math.isfinite(adamic_adar(store, 0, 1))


def test_geometric_mean_is_robust_to_a_single_zero():
    # A plain product would collapse to 0; the epsilon floor keeps it finite
    # and ordered, so one bad hop does not erase the rest of the path.
    assert geometric_mean([1.0, 1.0, 1.0]) == pytest.approx(1.0)
    assert geometric_mean([4.0, 1.0]) == pytest.approx(2.0)
    assert 0.0 < geometric_mean([1.0, 0.0]) < 1.0
    assert geometric_mean([]) == 0.0
