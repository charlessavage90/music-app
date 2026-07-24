import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from diagnostics import artifact_diagnostics, frozen_hub_diagnostics  # noqa: E402

from tests.conftest import make_store


def _hub_store():
    # Node 0 has degree 5; nodes 1-5 have degree 1. Cap of 2 is exceeded by node 0.
    return make_store(
        names=[f"n{i}" for i in range(6)],
        pop_raw=[0.9] + [0.1] * 5,
        undirected_edges=[(0, i, 1.0) for i in range(1, 6)],
    )


def test_reports_nodes_exceeding_the_configured_cap():
    d = artifact_diagnostics(_hub_store(), cap=2)
    assert d["nodes_over_cap"] == 1
    assert d["max_degree"] == 5
    assert d["cap"] == 2


def test_reports_saturated_edges_and_their_destination_degrees():
    # All edges are 1.0 and all point at or from the hub.
    d = artifact_diagnostics(_hub_store(), cap=2)
    assert d["saturated_edges"] == 10          # 5 undirected edges, both directions
    assert d["saturated_dst_median_degree"] > 0


def test_reports_degree_and_popularity_quantiles():
    d = artifact_diagnostics(_hub_store(), cap=2)
    for key in ("degree_p50", "degree_p99", "pop_p25", "pop_p50", "pop_p75"):
        assert key in d


def test_handles_a_graph_with_no_saturated_edges():
    store = make_store(
        names=list("AB"), pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.4)]
    )
    d = artifact_diagnostics(store, cap=50)
    assert d["saturated_edges"] == 0
    assert d["saturated_dst_median_degree"] == 0.0


def test_frozen_hub_diagnostics_counts_present_nodes_and_means_their_degree():
    # _hub_store: node 0 has degree 5 (edges to 1-5); nodes 1-5 each have
    # degree 1. top1pct_degree_nodes simulates load_or_freeze_hub_set's already-filtered
    # output: node ids known to exist in this artifact.
    d = frozen_hub_diagnostics(_hub_store(), top1pct_degree_nodes={0})
    assert d["frozen_hubs_present"] == 1
    assert d["mean_frozen_hub_degree"] == pytest.approx(5.0)


def test_frozen_hub_diagnostics_averages_degree_over_multiple_present_nodes():
    # Node 0 degree 5, node 1 degree 1 -> mean = (5 + 1) / 2 = 3.0.
    d = frozen_hub_diagnostics(_hub_store(), top1pct_degree_nodes={0, 1})
    assert d["frozen_hubs_present"] == 2
    assert d["mean_frozen_hub_degree"] == pytest.approx(3.0)


def test_frozen_hub_diagnostics_is_zero_when_no_frozen_hubs_are_present():
    # Simulates an artifact from which every frozen hub MBID is absent.
    d = frozen_hub_diagnostics(_hub_store(), top1pct_degree_nodes=set())
    assert d["frozen_hubs_present"] == 0
    assert d["mean_frozen_hub_degree"] == 0.0
