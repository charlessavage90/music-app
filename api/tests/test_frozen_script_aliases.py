"""The 2026-07-23 rename kept aliases so frozen probe scripts keep running.

`builder/analysis/` holds deliberate records of what was executed: hardcoded
paths, never updated, kept so a result can be re-derived. Sixteen of those
scripts import the shipped classes and read these attributes by their
pre-2026-07-23 names, and four import `hub_node_set` by name.

Nothing else covers them — they are not part of any suite and do not run in
CI — so without this test a future rename breaks the project's audit trail
silently, and only at the moment someone tries to reproduce an old result.

Mapping table: builder/analysis/README.md.
"""

from __future__ import annotations

import numpy as np

from artistpath_api import evaluation
from artistpath_api.evaluation import path_metrics, top_degree_node_set

from conftest import make_store


def _store():
    return make_store(
        names=list("ABCD"),
        pop_raw=[0.9, 0.3, 0.5, 0.1],
        undirected_edges=[(0, 1, 0.8), (1, 2, 0.7), (2, 3, 0.6)],
    )


def test_graph_store_exposes_the_old_attribute_names():
    store = _store()
    assert np.array_equal(store.popularity, store.pop_raw)
    assert np.array_equal(store.hub_penalty, store.degree_hub_penalty)


def test_the_old_graph_store_names_are_read_only():
    """Aliases must not become a second way to write the same quantity."""
    store = _store()
    for name in ("popularity", "hub_penalty"):
        try:
            setattr(store, name, np.zeros(4, dtype=np.float32))
        except AttributeError:
            continue
        raise AssertionError(f"{name} is writable; it must be a read-only alias")


def test_path_metrics_exposes_the_old_field_names():
    store = _store()
    m = path_metrics(store, [0, 1, 2, 3], top_degree_node_set(store, 0.01))
    assert m.hubfrac == m.top1pct_degree_frac
    assert m.mean_interior_pop == m.mean_interior_pop_raw
    assert m.max_interior_pop == m.max_interior_pop_raw


def test_hub_node_set_is_still_importable_under_its_old_name():
    assert evaluation.hub_node_set is evaluation.top_degree_node_set


# The builder-side alias (`Graph.popularity`) is covered by the builder's own
# suite. It is not asserted here: this package shares no code with `builder/`
# by design, and importing it would create exactly the coupling the APG1
# format exists to avoid.
