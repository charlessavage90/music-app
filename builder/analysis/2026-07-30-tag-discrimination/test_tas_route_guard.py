"""`TAS-AM5b`/`c` and `TAS-6`'s routing half -- the properties that must not drift."""

from __future__ import annotations

import numpy as np
import pytest

from tas_route_guard import agreement_only_path, sub_decile_interior_count


class FakeStore:
    """Four nodes, two routes from 0 to 2. Similarity and genre DISAGREE.

    Route 0->1->2 has strong similarity and a genre mismatch in the middle.
    Route 0->3->2 has weak similarity and perfect genre agreement.
    An agreement-only search must take the second; production would take the first.
    """

    def __init__(self):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.9, 0.5, 0.9, 0.05], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        self._adj = {
            0: [(1, 0.9), (3, 0.1)],
            1: [(0, 0.9), (2, 0.9)],
            2: [(1, 0.9), (3, 0.1)],
            3: [(0, 0.1), (2, 0.1)],
        }

    def neighbours_of(self, node_id):
        return iter(self._adj[node_id])


def test_agreement_only_path_ignores_similarity_entirely():
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}, "d": {"rock"}}
    path, cost = agreement_only_path(store, 0, 2, labels)
    assert path == [0, 3, 2], "the reference search was influenced by similarity"
    assert cost == pytest.approx(0.0)


def test_agreement_only_path_cost_is_not_trivially_zero():
    # Guards the assertion above from passing because the function always
    # returns 0.0 -- the vacuous-green shape.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}, "d": {"jazz"}}
    _path, cost = agreement_only_path(store, 0, 2, labels)
    assert cost > 0.0


def test_sub_decile_interior_count_excludes_endpoints():
    # TAS-6's routing half counts INTERIOR artists below the tenth fame
    # percentile. An obscure ENDPOINT is the user's own choice, not something
    # the router supplied.
    mbids = ["a", "b", "c", "d"]
    frame = {"a": 0.99, "b": 0.40, "c": 0.99, "d": 0.05}
    assert sub_decile_interior_count([[0, 3, 2]], mbids, frame) == 1
    assert sub_decile_interior_count([[3, 1, 0]], mbids, frame) == 0


def test_sub_decile_interior_count_sums_across_paths_and_interiors():
    mbids = ["a", "b", "c", "d"]
    frame = {"a": 0.99, "b": 0.05, "c": 0.99, "d": 0.05}
    assert sub_decile_interior_count([[0, 3, 1, 2], [0, 3, 2]], mbids, frame) == 3


def test_an_artist_absent_from_the_fame_frame_is_not_counted_as_obscure():
    # Unframed nodes must not be silently classed obscure -- the defect
    # tas_select.py:155 records against the capture/artifact node-set delta.
    mbids = ["a", "b", "c"]
    frame = {"a": 0.99, "c": 0.99}  # b is unframed
    assert sub_decile_interior_count([[0, 1, 2]], mbids, frame) == 0
