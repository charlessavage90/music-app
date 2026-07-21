import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from panel import generate_panel, load_panel, resolve_pairs  # noqa: E402

from tests.conftest import make_store


def _store(n=40):
    edges = [(i, (i + 1) % n, 0.9) for i in range(n)]
    edges += [(0, i, 0.9) for i in range(2, 12)]  # give node 0 a high degree
    return make_store(
        names=[f"artist{i}" for i in range(n)],
        popularity=[i / n for i in range(n)],
        undirected_edges=edges,
    )


def test_generate_panel_has_all_four_strata():
    panel = generate_panel(_store(), np.random.default_rng(42))
    assert set(panel["strata"]) == {
        "random", "obscure", "popularity_weighted", "hand_picked"
    }


def test_panel_pairs_are_mbid_keyed_not_index_keyed():
    panel = generate_panel(_store(), np.random.default_rng(42))
    first = panel["strata"]["random"][0]
    assert isinstance(first["from"], str) and len(first["from"]) == 36
    assert isinstance(first["to"], str)


def test_panel_pairs_are_deduped():
    panel = generate_panel(_store(), np.random.default_rng(42))
    for pairs in panel["strata"].values():
        keys = [(p["from"], p["to"]) for p in pairs]
        assert len(keys) == len(set(keys))


def test_no_pair_has_identical_endpoints():
    panel = generate_panel(_store(), np.random.default_rng(42))
    for pairs in panel["strata"].values():
        for p in pairs:
            assert p["from"] != p["to"]


def test_held_out_slice_is_flagged_and_disjoint():
    panel = generate_panel(_store(), np.random.default_rng(42))
    aggregated = [
        p
        for name in ("random", "obscure", "popularity_weighted")
        for p in panel["strata"][name]
    ]
    held = [p for p in aggregated if p.get("held_out")]
    analysis = [p for p in aggregated if not p.get("held_out")]
    assert held and analysis
    assert not ({(p["from"], p["to"]) for p in held}
                & {(p["from"], p["to"]) for p in analysis})


def test_hand_picked_pairs_are_never_held_out():
    # They are qualitative-only and never enter aggregates or the held-out check.
    panel = generate_panel(_store(), np.random.default_rng(42))
    assert all(not p.get("held_out") for p in panel["strata"]["hand_picked"])


def test_resolve_pairs_reports_dropped_mbids_rather_than_substituting():
    store = _store()
    panel = {
        "strata": {
            "random": [
                {"from": store.mbids[0], "to": store.mbids[1]},
                {"from": "missing-mbid-aaaaaaaaaaaaaaaaaaaaaaaa", "to": store.mbids[2]},
            ]
        }
    }
    pairs, dropped = resolve_pairs(store, panel, "random")
    assert pairs == [(0, 1)]
    assert dropped == ["missing-mbid-aaaaaaaaaaaaaaaaaaaaaaaa"]


def test_load_panel_rejects_a_malformed_file(tmp_path: Path):
    bad = tmp_path / "panel.json"
    bad.write_text(json.dumps({"nope": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="strata"):
        load_panel(bad)
