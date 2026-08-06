"""The trimmed-union supply rule reaching the pipeline (`MSW-`, Task 2).

The rule itself is tested in test_graph.py, including against the frozen
Track B implementation it was ported from. What is tested HERE is the seam:
that `cap_strategy` selects it, that the bound survives the rest of the
pipeline (symmetrise + largest-component run after the cap), and that the
default path is untouched.

`drop_unlistenable` is pinned off throughout: these synthetic archives are
covered by no `ULF-` census, and an uncensused population refuses to build.
"""

import json

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource

import numpy as np
import pytest


def _body(rows):
    return json.dumps(
        [{"artist_mbid": m, "name": m[:4], "comment": "", "score": s} for m, s in rows]
    ).encode()


def _seed(archive, source, *, n=40, per_node=20, seed=7):
    """A dense mesh, so mutual k-NN and the union rule both keep a real graph."""
    import random

    rng = random.Random(seed)
    mbids = [f"{i:04d}" + "c" * 32 for i in range(n)]
    for m in mbids:
        others = rng.sample([x for x in mbids if x != m], per_node)
        archive.put(
            f"similar/{source.name}/{m}.json",
            _body([(o, rng.randint(50, 500)) for o in others]),
        )
    return mbids


def _build(tmp_path, **overrides):
    config = BuilderConfig(
        requests_per_second=1000.0, drop_unlistenable=False, **overrides
    )
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    _seed(archive, source)
    return build_from_archive(config, archive, source)


def test_trimmed_union_build_respects_the_degree_ceiling(tmp_path):
    graph = _build(
        tmp_path,
        cap_strategy="trimmed_union",
        union_top_j=5,
        union_degree_ceiling=5,
    )
    degrees = np.diff(graph.offsets)
    assert int(degrees.max()) <= 5


def test_trimmed_union_supplies_more_edges_than_mutual_knn(tmp_path):
    """The reason the rule was selected: at the same k it is non-reciprocal,
    so it keeps edges mutual k-NN discards. If this ever inverts, the seam is
    wired to the wrong rule."""
    union = _build(
        tmp_path / "u",
        cap_strategy="trimmed_union",
        union_top_j=5,
        union_degree_ceiling=50,
    )
    mutual = _build(tmp_path / "m", max_neighbours_per_artist=5)
    assert union.edge_count > mutual.edge_count


def test_trimmed_union_build_is_deterministic(tmp_path):
    a = _build(tmp_path / "a", cap_strategy="trimmed_union")
    b = _build(tmp_path / "b", cap_strategy="trimmed_union")
    assert a.mbids == b.mbids
    assert list(a.neighbours) == list(b.neighbours)
    assert list(a.scores) == list(b.scores)


def test_default_strategy_is_still_mutual_knn():
    assert BuilderConfig().cap_strategy == "mutual_knn"


def test_trimmed_union_is_a_permitted_strategy():
    cfg = BuilderConfig(cap_strategy="trimmed_union")
    assert cfg.union_top_j == 50
    assert cfg.union_degree_ceiling == 50


def test_the_deleted_legacy_strategy_still_raises():
    # Phase 2 deleted pre_symmetrise on evidence. Adding a second permitted
    # strategy must not quietly re-open the door to the one that lost.
    with pytest.raises(ValueError, match="pre_symmetrise"):
        BuilderConfig(cap_strategy="pre_symmetrise")


def test_an_unknown_strategy_names_both_permitted_ones():
    with pytest.raises(ValueError) as excinfo:
        BuilderConfig(cap_strategy="nonsense")
    message = str(excinfo.value)
    assert "mutual_knn" in message and "trimmed_union" in message
