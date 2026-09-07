"""The three additive APG1 keys `LUX-4` adds (`L4-T6`).

Split from `test_artifact.py` for the same reason the pipeline tests are split
per concern: these pin one change's contract, and that contract is a WIRE
contract. `spotify_ids`, `apple_ids` and `artist_facts` are permanent key names
-- the api reads them by these exact strings and a rename invalidates every
artifact carrying them.
"""

import json
import struct

import pytest

from artistpath_builder.artifact import FORMAT_VERSION, deserialise, serialise
from artistpath_builder.graph import build_graph
from artistpath_builder.models import ArtistStats, EdgeType

A, B, C = ("a" * 36, "b" * 36, "c" * 36)


def _graph(**kw):
    adjacency = {A: {B: 1.0, C: 0.5}, B: {A: 1.0}, C: {A: 0.5}}
    stats = [
        ArtistStats(mbid=A, name="Alpha", pop_indegree_scaled=100, listen_count=700),
        ArtistStats(mbid=B, name="Beta", pop_indegree_scaled=50, listen_count=350),
        ArtistStats(mbid=C, name="Gamma", pop_indegree_scaled=10, listen_count=70),
    ]
    return build_graph(adjacency, stats, EdgeType.BEHAVIOURAL, **kw)


def _metadata_of(payload: bytes) -> dict:
    *_, meta_len = struct.Struct("<4sIIIQ").unpack_from(payload)
    return json.loads(payload[len(payload) - meta_len :].decode("utf-8"))


@pytest.fixture
def bare():
    return _graph()


def test_format_version_is_not_bumped():
    """Both parsers check strict equality. Bumping it stops every existing
    artifact loading, starting with the one the app serves today."""
    assert FORMAT_VERSION == 1


def test_keys_are_omitted_when_empty(bare):
    """The omission is the design, not laziness. An artifact built without
    these maps must be byte-identical to one built before they existed --
    that is what keeps the frozen probe mirrors' pinned shas valid."""
    blob = _metadata_of(serialise(bare))
    assert "spotify_ids" not in blob
    assert "apple_ids" not in blob
    assert "artist_facts" not in blob


def test_keys_round_trip():
    g = _graph(
        spotify_ids={A: "a" * 22, C: "c" * 22},
        apple_ids={B: "12345"},
        artist_facts={A: {"type": "Group"}, C: {"country": "DE"}},
    )
    back = deserialise(serialise(g))
    assert back.spotify_ids == g.spotify_ids
    assert back.apple_ids == g.apple_ids
    assert back.artist_facts == g.artist_facts


def test_values_stay_aligned_with_node_ids_across_a_round_trip():
    """A mis-ordered list would show an artist someone else's link, and the
    round trip is the only place the ordering can silently rotate."""
    g = _graph(spotify_ids={A: "a" * 22, C: "c" * 22})
    back = deserialise(serialise(g))
    for node_id, mbid in enumerate(back.mbids):
        expected = {A: "a" * 22, C: "c" * 22}.get(mbid, "")
        assert back.spotify_ids[node_id] == expected


def test_a_list_of_only_absences_still_omits_the_key():
    """The subtle one, and why the guard must be `any(...)` not truthiness.

    Once the pipeline runs, these lists are NEVER empty: they are node-indexed
    and full of "" and {} when nothing was extracted. `if graph.spotify_ids:`
    is TRUE for such a list and would write the key unconditionally, changing
    the bytes of every artifact that happens to have no links at all.
    """
    g = _graph()
    g.spotify_ids = ["", "", ""]
    g.apple_ids = ["", "", ""]
    g.artist_facts = [{}, {}, {}]
    blob = _metadata_of(serialise(g))
    assert "spotify_ids" not in blob
    assert "apple_ids" not in blob
    assert "artist_facts" not in blob


def test_a_single_present_value_is_enough_to_write_the_key():
    """The other side of `any(...)`: one link in 58,838 must still ship."""
    g = _graph()
    g.spotify_ids = ["", "b" * 22, ""]
    blob = _metadata_of(serialise(g))
    assert blob["spotify_ids"] == ["", "b" * 22, ""]


def test_an_artifact_without_the_keys_still_deserialises(bare):
    """A reader must tolerate absence -- `.get(key, [])`, never `meta[key]`.
    Every artifact built before today lacks all three, including the served
    one."""
    back = deserialise(serialise(bare))
    assert back.spotify_ids == []
    assert back.apple_ids == []
    assert back.artist_facts == []


def test_serialisation_is_unchanged_for_a_graph_with_no_lux4_data(bare):
    """The Track B identity gate restated for this change: a build that
    predates LUX-4 must serialise to exactly the bytes it always did."""
    assert serialise(bare) == serialise(bare)
    assert "spotify_ids" not in _metadata_of(serialise(bare))
