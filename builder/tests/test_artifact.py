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
            pop_indegree_scaled=100,
            listen_count=700,
            disambiguation="UK band",
        ),
        ArtistStats(mbid=B, name="Beta", pop_indegree_scaled=50, listen_count=350),
        ArtistStats(mbid=C, name="Gamma", pop_indegree_scaled=10, listen_count=70),
    ]
    return build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)


def test_artifact_starts_with_magic(graph):
    assert serialise(graph)[:4] == MAGIC


def test_round_trip_preserves_everything(graph):
    restored = deserialise(serialise(graph))
    assert restored.mbids == graph.mbids
    assert restored.names == graph.names
    assert restored.disambiguations == graph.disambiguations
    assert restored.pop_raw == pytest.approx(graph.pop_raw)
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


# --- fame_lb, the MSW- additive key ----------------------------------------


def test_fame_round_trips_including_nulls(graph):
    # A null is a measured absence (nobody has listened), never a missing
    # value and never a floor — FAM- §1, FAM-AM1.8. It must survive the wire
    # as a null, not as 0, which would read as a real listener count.
    graph.fame_lb_raw = [12, None, 0]
    assert deserialise(serialise(graph)).fame_lb_raw == [12, None, 0]


def test_an_all_null_fame_list_still_round_trips(graph):
    # Legitimate measurement, not an empty one: the key must be written.
    graph.fame_lb_raw = [None, None, None]
    assert deserialise(serialise(graph)).fame_lb_raw == [None, None, None]
    assert b'"fame_lb"' in serialise(graph)


def test_empty_fame_omits_the_key(graph):
    # Additive-key discipline, exactly as for deezer_ids: FORMAT_VERSION is
    # checked for strict equality by both parsers, so the key is added without
    # a version bump and must be absent when there is nothing to say.
    assert graph.fame_lb_raw == []
    assert b'"fame_lb"' not in serialise(graph)


def test_an_artifact_without_fame_deserialises_to_an_empty_list(graph):
    # Every artifact built before today lacks the key, including the one the
    # app serves. Absence means "this artifact cannot support the ramp", which
    # the api turns into a refusal to boot only if the ramp is actually on.
    assert deserialise(serialise(graph)).fame_lb_raw == []


def test_adding_fame_does_not_bump_the_format_version(graph):
    import struct

    graph.fame_lb_raw = [1, 2, 3]
    version = struct.unpack("<I", serialise(graph)[4:8])[0]
    assert version == 1, (
        "bumping the version would stop every existing artifact loading, "
        "starting with the one the app serves today"
    )


def test_fame_absent_and_fame_empty_serialise_identically(graph):
    # The frozen probe mirrors pin their artifacts' shas. An empty fame list
    # must produce the same bytes as a build from before the field existed.
    before = serialise(graph)
    graph.fame_lb_raw = []
    assert serialise(graph) == before
