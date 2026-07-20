import numpy as np
import pytest

from artistpath_builder.artifact import MAGIC, deserialise, serialise
from artistpath_builder.graph import build_graph
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C = ("a" * 36, "b" * 36, "c" * 36)


@pytest.fixture
def graph():
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    stats = [
        ArtistStats(
            mbid=A,
            name="Alpha",
            user_count=100,
            listen_count=700,
            disambiguation="UK band",
        ),
        ArtistStats(mbid=B, name="Beta", user_count=50, listen_count=350),
        ArtistStats(mbid=C, name="Gamma", user_count=10, listen_count=70),
    ]
    return build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)


def test_artifact_starts_with_magic(graph):
    assert serialise(graph)[:4] == MAGIC


def test_round_trip_preserves_everything(graph):
    restored = deserialise(serialise(graph))
    assert restored.mbids == graph.mbids
    assert restored.names == graph.names
    assert restored.disambiguations == graph.disambiguations
    assert restored.popularity == pytest.approx(graph.popularity)
    assert np.array_equal(restored.offsets, graph.offsets)
    assert np.array_equal(restored.neighbours, graph.neighbours)
    assert np.array_equal(restored.scores, graph.scores)
    assert np.array_equal(restored.edge_types, graph.edge_types)


def test_serialisation_is_byte_identical_across_runs(graph):
    # The whole replay guarantee (spec section 9) rests on this.
    assert serialise(graph) == serialise(graph)


def test_non_ascii_names_survive(graph):
    # Artist names are full Unicode; a mojibake round trip would corrupt
    # search and display without failing any other test.
    graph.names[0] = "Sigur Rós"
    graph.names[1] = "少女時代"
    restored = deserialise(serialise(graph))
    assert restored.names[0] == "Sigur Rós"
    assert restored.names[1] == "少女時代"


def test_dtypes_survive_the_round_trip(graph):
    restored = deserialise(serialise(graph))
    assert restored.offsets.dtype == np.int32
    assert restored.neighbours.dtype == np.int32
    assert restored.scores.dtype == np.float32
    assert restored.edge_types.dtype == np.uint8


def test_bad_magic_is_rejected(graph):
    corrupted = b"XXXX" + serialise(graph)[4:]
    with pytest.raises(ValueError, match="magic"):
        deserialise(corrupted)


def test_truncated_payload_is_rejected(graph):
    with pytest.raises(ValueError):
        deserialise(serialise(graph)[:20])
