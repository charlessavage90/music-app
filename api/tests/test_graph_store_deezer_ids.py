"""The api reads Deezer artist ids out of the APG1 metadata blob.

The key is ADDITIVE and FORMAT_VERSION is deliberately NOT bumped: both parsers
check the version for strict equality, so bumping it would stop every existing
artifact loading — starting with the one the app serves today. This reader must
therefore tolerate the key's absence, and absence must mean "resolve by name",
which is exactly what the app did before this existed.

Ids are indexed by NODE ID, like every other metadata list. Reading them
against the wrong row would hand one artist's card another artist's clip — the
same defect this feature exists to remove, arriving by a different route.
"""

import json
import struct

import numpy as np

from artistpath_api.graph_store import GraphStore

MBIDS = ["a" * 36, "b" * 36, "c" * 36]


def _write_apg1(path, deezer_ids=None):
    meta = {
        "mbids": MBIDS,
        "names": ["Alpha", "Beta", "Gamma"],
        "disambiguations": ["", "", ""],
        "popularity": [0.9, 0.5, 0.1],
    }
    if deezer_ids is not None:
        meta["deezer_ids"] = deezer_ids
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


def test_ids_are_read_and_indexed_by_node_id(tmp_path):
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin", ["111", "", "333"]))
    assert g.deezer_id_of(0) == "111"
    assert g.deezer_id_of(1) == ""
    assert g.deezer_id_of(2) == "333"


def test_an_artifact_without_the_key_loads_and_reports_no_ids(tmp_path):
    # The adopted artifact the app serves today. Every artist must fall back to
    # name search rather than the load failing.
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin"))
    assert g.artist_count == 3
    assert all(g.deezer_id_of(i) == "" for i in range(3))


def test_a_store_built_in_a_test_reports_no_ids():
    # Most api tests construct GraphStore directly and never mention ids.
    g = GraphStore(
        mbids=MBIDS[:2],
        names=["A", "B"],
        disambiguations=["", ""],
        pop_raw=np.asarray([0.5, 0.5], dtype=np.float32),
        offsets=np.asarray([0, 1, 2], dtype=np.int32),
        neighbours=np.asarray([1, 0], dtype=np.int32),
        scores=np.asarray([0.7, 0.7], dtype=np.float32),
    )
    assert g.deezer_id_of(0) == ""


def test_a_short_id_list_does_not_hand_one_artist_anothers_id(tmp_path):
    # A truncated list would silently shift every id after the gap if it were
    # indexed naively. Out of range must read as "no id", never as a neighbour's.
    g = GraphStore.load(_write_apg1(tmp_path / "g.bin", ["111"]))
    assert g.deezer_id_of(0) == "111"
    assert g.deezer_id_of(1) == ""
    assert g.deezer_id_of(2) == ""
