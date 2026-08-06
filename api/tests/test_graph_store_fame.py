"""Fame arriving in the api, and the percentile frame built at boot (`MSW-`, Task 6).

`fame_lb_raw` is a ListenBrainz listener count. `fame_lb_pctl` is where that
count ranks **within this artifact's own population**, 0 to 1. The cost
function reads only the percentile.

THE FRAME IS THE ARTIFACT'S OWN and this is a deliberate deviation from the
`CRE-` harness, which framed against the previously adopted artifact's values —
a fixed experimental ruler, correct for comparing arms across builds. A shipped
ruler pinned to a retired artifact would go stale at every future adoption, and
would price today's artists against a population that no longer exists. Plain
sentence: the app ranks each artist's obscurity against everyone else on its
own map.

Nulls are measured absences — nobody has listened — which under the
novelty-likelihood construct is genuine maximal obscurity, so they take
percentile 0.0. They are never a missing measurement and never a floor value
(`FAM-` §1, `FAM-AM1`.8).
"""

import json
import struct

import numpy as np
import pytest

from artistpath_api.graph_store import GraphStore

_HEADER = struct.Struct("<4sIIIQ")


def _apg1(mbids, *, fame_lb=None, offsets=None, neighbours=None, scores=None):
    """A minimal ring graph, optionally carrying the additive fame key."""
    n = len(mbids)
    if neighbours is None:
        # ring: each node points at the next, wrapping
        neighbours = [(i + 1) % n for i in range(n)]
        offsets = list(range(n + 1))
        scores = [0.9] * n
    meta = {
        "mbids": mbids,
        "names": [m.upper() for m in mbids],
        "disambiguations": ["" for _ in mbids],
        "popularity": [0.5 for _ in mbids],
    }
    if fame_lb is not None:
        meta["fame_lb"] = fame_lb
    blob = json.dumps(meta).encode()
    e = len(neighbours)
    body = (
        struct.pack(f"<{len(offsets)}i", *offsets)
        + struct.pack(f"<{e}i", *neighbours)
        + struct.pack(f"<{e}f", *scores)
        + bytes(e)
    )
    return _HEADER.pack(b"APG1", 1, n, e, len(blob)) + body + blob


def _names(count):
    return [chr(ord("a") + i) * 36 for i in range(count)]


def test_an_artifact_without_fame_loads_with_none(tmp_path):
    # Every artifact built before 2026-08-05 lacks the key, including the one
    # the app serves today. Absence is not an error — it means this artifact
    # cannot support the ramp, which only matters if the ramp is switched on.
    store = GraphStore.from_bytes(_apg1(_names(3)))
    assert store.fame_lb_pctl is None


def test_fame_ranks_within_the_artifacts_own_population():
    store = GraphStore.from_bytes(_apg1(_names(4), fame_lb=[10, 20, 30, 40]))
    p = store.fame_lb_pctl
    assert p is not None
    assert p[0] == pytest.approx(0.0)
    assert p[3] == pytest.approx(1.0)
    assert p[0] < p[1] < p[2] < p[3]


def test_nulls_take_maximal_obscurity():
    store = GraphStore.from_bytes(_apg1(_names(4), fame_lb=[10, None, 30, 40]))
    p = store.fame_lb_pctl
    # A null is "measured, and nobody listened" — the most obscure reading
    # available, and strictly below the least-listened-to measured artist.
    assert p[1] == pytest.approx(0.0)
    assert p[1] <= p[0]


def test_nulls_are_excluded_from_the_frame():
    # If nulls entered the frame they would drag every real artist's rank up,
    # making a population with many unmeasured artists look uniformly famous.
    with_nulls = GraphStore.from_bytes(
        _apg1(_names(5), fame_lb=[10, 20, 30, None, None])
    )
    without = GraphStore.from_bytes(_apg1(_names(3), fame_lb=[10, 20, 30]))
    assert with_nulls.fame_lb_pctl[:3] == pytest.approx(without.fame_lb_pctl)


def test_equal_counts_take_equal_percentiles():
    store = GraphStore.from_bytes(_apg1(_names(4), fame_lb=[10, 10, 10, 99]))
    p = store.fame_lb_pctl
    assert p[0] == p[1] == p[2]
    assert p[3] > p[0]


def test_a_single_measured_artist_does_not_divide_by_zero():
    store = GraphStore.from_bytes(_apg1(_names(3), fame_lb=[None, 42, None]))
    p = store.fame_lb_pctl
    assert np.all(np.isfinite(p))


def test_an_all_null_population_is_all_maximal_obscurity():
    store = GraphStore.from_bytes(_apg1(_names(3), fame_lb=[None, None, None]))
    p = store.fame_lb_pctl
    assert p is not None
    assert np.all(p == 0.0)


def test_every_percentile_is_within_the_unit_range():
    store = GraphStore.from_bytes(
        _apg1(_names(6), fame_lb=[1, 5, 5, 900, None, 12])
    )
    p = store.fame_lb_pctl
    assert float(p.min()) >= 0.0
    assert float(p.max()) <= 1.0


def test_a_short_fame_list_is_rejected():
    # Indexed by node id in the cost function. A short list would price one
    # artist as another, or read out of bounds mid-request.
    with pytest.raises(ValueError, match="fame"):
        GraphStore.from_bytes(_apg1(_names(4), fame_lb=[1, 2, 3]))


def test_a_long_fame_list_is_rejected():
    with pytest.raises(ValueError, match="fame"):
        GraphStore.from_bytes(_apg1(_names(2), fame_lb=[1, 2, 3]))


def test_an_empty_fame_list_is_treated_as_absent():
    # The builder omits the key when empty, but an artifact carrying an empty
    # list must not become a zero-length array indexed by node id.
    store = GraphStore.from_bytes(_apg1(_names(3), fame_lb=[]))
    assert store.fame_lb_pctl is None
