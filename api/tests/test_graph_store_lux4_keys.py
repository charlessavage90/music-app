"""The api reads LUX-4's three additive keys: spotify_ids, apple_ids, artist_facts.

Same additive-key contract as deezer_ids, for the same reason: FORMAT_VERSION
is deliberately NOT bumped, both parsers check it for strict equality, and so
every artifact built before 2026-09-06 lacks these keys — including the one the
app serves today. Absence must load clean and read as "nothing to show", which
degrades to a search link on the card rather than to a missing button.

Unlike deezer_ids these are DISPLAY-ONLY and never indexed in the cost
function, which is why they carry no length assertion: the accessors are the
bounds check. `graph_store.py`'s loader comment states that discipline and why
it differs by field.
"""

import json
import struct

import numpy as np

from artistpath_api.graph_store import GraphStore

MBIDS = ["a" * 36, "b" * 36, "c" * 36]


def _write_apg1(path, **keys):
    """An APG1 artifact carrying only the LUX-4 keys explicitly passed.

    Omitting a key is the pre-LUX-4 artifact; passing one is a post-LUX-4 one.
    """
    meta = {
        "mbids": MBIDS,
        "names": ["Alpha", "Beta", "Gamma"],
        "disambiguations": ["", "", ""],
        "popularity": [0.9, 0.5, 0.1],
    }
    meta.update({k: v for k, v in keys.items() if v is not None})
    blob = json.dumps(meta, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    offsets, neighbours, scores = [0, 1, 3, 4], [1, 0, 2, 1], [0.8, 0.8, 0.6, 0.6]
    header = struct.pack("<4sIIIQ", b"APG1", 1, len(MBIDS), len(neighbours), len(blob))
    path.write_bytes(
        header
        + np.asarray(offsets, dtype="<i4").tobytes()
        + np.asarray(neighbours, dtype="<i4").tobytes()
        + np.asarray(scores, dtype="<f4").tobytes()
        + np.zeros(len(neighbours), dtype=np.uint8).tobytes()
        + blob
    )
    return path


def test_missing_keys_mean_no_links_not_a_crash(tmp_path):
    # Every artifact built before LUX-4 lacks these keys, including the one the
    # app serves. Absence must degrade to a search link, not to a load failure.
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin"))
    assert g.artist_count == 3
    assert g.spotify_id_of(0) is None
    assert g.apple_id_of(0) is None
    assert g.facts_of(0) == {}


def test_ids_and_facts_are_read_and_indexed_by_node_id(tmp_path):
    g = GraphStore.load(
        _write_apg1(
            tmp_path / "g.bin",
            spotify_ids=["s0", "", "s2"],
            apple_ids=["", "a1", "a2"],
            artist_facts=[{"type": "Group"}, {}, {"country": "IS"}],
        )
    )
    assert g.spotify_id_of(0) == "s0"
    assert g.spotify_id_of(2) == "s2"
    assert g.apple_id_of(1) == "a1"
    assert g.facts_of(0) == {"type": "Group"}
    assert g.facts_of(2) == {"country": "IS"}


def test_a_short_list_does_not_read_out_of_bounds(tmp_path):
    # The accessor is the bounds check — the same reason deezer_ids is exempt
    # from the length assertion fame_lb carries. Out of range reads as absent,
    # never as a neighbour's id.
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin", spotify_ids=["s0"]))
    assert g.spotify_id_of(0) == "s0"
    assert g.spotify_id_of(1) is None
    assert g.spotify_id_of(2) is None


def test_an_empty_slot_reads_as_absent(tmp_path):
    # "" is how the builder records "no id known" — the same in-band sentinel
    # deezer_ids uses. On this wire absent must be null, so the accessor
    # normalises it rather than leaking an empty string to the frontend.
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin", spotify_ids=["s0", "", "s2"]))
    assert g.spotify_id_of(1) is None
    g2 = GraphStore.load(_write_apg1(tmp_path / "h.bin", apple_ids=["", "a1", ""]))
    assert g2.apple_id_of(0) is None
    assert g2.apple_id_of(2) is None


def test_an_empty_facts_dict_reads_as_no_facts(tmp_path):
    # An artist the extraction pass reached but found nothing structured for.
    # Renders as nothing at all (L4-D3), so it must be indistinguishable from
    # an artist the pass never covered.
    g = GraphStore.load(
        _write_apg1(tmp_path / "g.bin", artist_facts=[{}, {"type": "Person"}, {}])
    )
    assert g.facts_of(0) == {}
    assert g.facts_of(2) == {}
    assert g.facts_of(99) == {}


def test_a_store_built_in_a_test_reports_nothing():
    # Most api tests construct GraphStore directly and never mention these.
    g = GraphStore(
        mbids=MBIDS[:2],
        names=["A", "B"],
        disambiguations=["", ""],
        pop_raw=np.asarray([0.5, 0.5], dtype=np.float32),
        offsets=np.asarray([0, 1, 2], dtype=np.int32),
        neighbours=np.asarray([1, 0], dtype=np.int32),
        scores=np.asarray([0.7, 0.7], dtype=np.float32),
    )
    assert g.spotify_id_of(0) is None
    assert g.apple_id_of(0) is None
    assert g.facts_of(0) == {}
