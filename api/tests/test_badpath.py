from artistpath_api.badpath import screen_path
from artistpath_api.graph_store import GraphStore
from tests.conftest import make_store


def _store_with_disambiguations(names, disambiguations, undirected_edges):
    base = make_store(
        names=names, pop_raw=[0.5] * len(names), undirected_edges=undirected_edges
    )
    return GraphStore(
        mbids=base.mbids,
        names=base.names,
        disambiguations=list(disambiguations),
        pop_raw=base.pop_raw,
        offsets=base.offsets,
        neighbours=base.neighbours,
        scores=base.scores,
    )


def test_flags_a_special_purpose_interior_node():
    store = _store_with_disambiguations(
        names=["A", "[unknown]", "C"],
        disambiguations=["", "Special Purpose Artist - do not add releases", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    report = screen_path(store, [0, 1, 2])
    assert report.flagged is True
    assert any("non-musical" in r for r in report.reasons)


def test_flags_an_interior_node_with_no_name():
    store = _store_with_disambiguations(
        names=["A", "", "C"],
        disambiguations=["", "", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9)],
    )
    assert screen_path(store, [0, 1, 2]).flagged is True


def test_does_not_flag_a_special_purpose_ENDPOINT():
    # Endpoints are user-chosen. Only interior nodes are the router's fault.
    # The 0-2 edge is load-bearing: without it this is a bare chain, every hop
    # trivially has no common neighbour, and signal 2 would flag the path for
    # reasons that have nothing to do with the endpoint rule under test.
    store = _store_with_disambiguations(
        names=["[unknown]", "B", "C"],
        disambiguations=["Special Purpose Artist", "", ""],
        undirected_edges=[(0, 1, 0.9), (1, 2, 0.9), (0, 2, 0.9)],
    )
    assert screen_path(store, [0, 1, 2]).flagged is False


def test_flags_a_hop_with_no_common_neighbours():
    # 0-1 and 1-2 are adjacent but 1-2 share nothing: a leap with no context.
    store = make_store(
        names=list("ABCD"), pop_raw=[0.5] * 4,
        undirected_edges=[(0, 1, 0.9), (0, 3, 0.9), (1, 3, 0.9), (1, 2, 0.9)],
    )
    report = screen_path(store, [0, 1, 2])
    assert report.flagged is True
    assert any("no common neighbour" in r for r in report.reasons)


def test_flags_three_consecutive_nodes_from_one_micro_cluster():
    # Interior nodes 1,2,3 sit in a tight clique with 6 and 7 and nothing else
    # — the signature of a film cast list or a label roster.
    # A bare 3-clique is NOT enough to reach _MICRO_CLUSTER_JACCARD: `jaccard`
    # excludes the pair itself from the intersection but keeps it in the union,
    # so adjacent nodes in a 3-clique only reach 0.25. Five mutually connected
    # nodes put consecutive interior pairs at exactly the 0.5 threshold.
    clique = [
        (a, b, 0.9)
        for i, a in enumerate([1, 2, 3, 6, 7])
        for b in [1, 2, 3, 6, 7][i + 1 :]
    ]
    store = make_store(
        names=list("ABCDEFGH"), pop_raw=[0.5] * 8,
        undirected_edges=[
            (0, 1, 0.9), *clique,
            (3, 4, 0.9), (4, 5, 0.9), (0, 5, 0.9), (0, 4, 0.9),
        ],
    )
    report = screen_path(store, [0, 1, 2, 3, 4])
    assert any("micro-cluster" in r for r in report.reasons)


def test_does_not_flag_a_clean_path():
    store = make_store(
        names=list("ABCD"), pop_raw=[0.5] * 4,
        undirected_edges=[
            (0, 1, 0.9), (1, 2, 0.9), (2, 3, 0.9), (0, 2, 0.5), (1, 3, 0.5),
        ],
    )
    report = screen_path(store, [0, 1, 2, 3])
    assert report.flagged is False
    assert report.reasons == []


def test_short_paths_are_never_flagged():
    store = make_store(
        names=list("AB"), pop_raw=[0.5, 0.5], undirected_edges=[(0, 1, 0.9)]
    )
    assert screen_path(store, [0, 1]).flagged is False


def test_calibrated_thresholds_are_pinned():
    # Changing these silently would change what the screen rejects, and the
    # screen is criterion 5 of the adoption decision. Task 5's calibration
    # against the cosine La La Land path (must flag) and the v3 Miles Davis ->
    # Daft Punk and Burzum -> Dolly Parton paths (must not) did NOT separate at
    # any setting, so these remain the brief's defaults rather than fitted
    # values. See .superpowers/sdd/task-5-report.md.
    from artistpath_api import badpath

    assert badpath._MICRO_CLUSTER_JACCARD == 0.5
    assert badpath._MICRO_CLUSTER_RUN == 3
