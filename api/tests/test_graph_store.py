import json
import struct

import numpy as np
import pytest

from artistpath_api.graph_store import GraphStore


def _write_apg1(path, mbids, names, disambiguations, popularity,
                offsets, neighbours, scores):
    meta = json.dumps(
        {"mbids": mbids, "names": names,
         "disambiguations": disambiguations, "popularity": popularity},
        separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    header = struct.pack("<4sIIIQ", b"APG1", 1, len(mbids), len(neighbours), len(meta))
    edge_types = np.zeros(len(neighbours), dtype=np.uint8)
    path.write_bytes(
        header
        + np.asarray(offsets, dtype="<i4").tobytes()
        + np.asarray(neighbours, dtype="<i4").tobytes()
        + np.asarray(scores, dtype="<f4").tobytes()
        + edge_types.tobytes()
        + meta
    )


def test_load_round_trips_a_small_graph(tmp_path):
    # A<->B<->C chain.
    p = tmp_path / "g.bin"
    _write_apg1(
        p,
        mbids=["a" * 36, "b" * 36, "c" * 36],
        names=["Alpha", "Beta", "Gamma"],
        disambiguations=["UK band", "", ""],
        popularity=[0.9, 0.5, 0.1],
        offsets=[0, 1, 3, 4],
        neighbours=[1, 0, 2, 1],
        scores=[0.8, 0.8, 0.6, 0.6],
    )
    g = GraphStore.load(p)
    assert g.artist_count == 3
    assert g.names[1] == "Beta"
    assert g.disambiguations[0] == "UK band"
    assert g.id_by_mbid["c" * 36] == 2
    assert g.popularity.dtype == np.float32


def test_neighbours_of_yields_id_and_score(tmp_path):
    p = tmp_path / "g.bin"
    _write_apg1(
        p, ["a" * 36, "b" * 36], ["A", "B"], ["", ""], [0.5, 0.5],
        offsets=[0, 1, 2], neighbours=[1, 0], scores=[0.7, 0.7],
    )
    g = GraphStore.load(p)
    assert list(g.neighbours_of(0)) == [(1, np.float32(0.7))]


def test_non_ascii_names_survive(tmp_path):
    p = tmp_path / "g.bin"
    _write_apg1(
        p, ["a" * 36, "b" * 36], ["Sigur Rós", "Beyoncé"], ["", ""], [0.5, 0.5],
        offsets=[0, 1, 2], neighbours=[1, 0], scores=[0.7, 0.7],
    )
    g = GraphStore.load(p)
    assert g.names == ["Sigur Rós", "Beyoncé"]


def test_bad_magic_is_rejected(tmp_path):
    p = tmp_path / "bad.bin"
    p.write_bytes(b"XXXX" + b"\x00" * 40)
    with pytest.raises(ValueError, match="magic"):
        GraphStore.load(p)
