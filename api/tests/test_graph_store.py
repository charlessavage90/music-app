import json
import struct

import numpy as np
import pytest

from artistpath_api.graph_store import GraphStore


def _write_apg1(path, mbids, names, disambiguations, pop_raw,
                offsets, neighbours, scores):
    # "popularity" is the wire key and stays; `pop_raw` is what it holds.
    meta = json.dumps(
        {"mbids": mbids, "names": names,
         "disambiguations": disambiguations, "popularity": pop_raw},
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
        pop_raw=[0.9, 0.5, 0.1],
        offsets=[0, 1, 3, 4],
        neighbours=[1, 0, 2, 1],
        scores=[0.8, 0.8, 0.6, 0.6],
    )
    g = GraphStore.load(p)
    assert g.artist_count == 3
    assert g.names[1] == "Beta"
    assert g.disambiguations[0] == "UK band"
    assert g.id_by_mbid["c" * 36] == 2
    assert g.pop_raw.dtype == np.float32


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


def test_degree_hub_penalty_is_higher_for_higher_degree(tmp_path):
    # Node 0 has degree 3 (hub-ish), leaves have degree 1.
    p = tmp_path / "g.bin"
    _write_apg1(
        p, ["a" * 36, "b" * 36, "c" * 36, "d" * 36], ["A", "B", "C", "D"],
        ["", "", "", ""], [0.5, 0.5, 0.5, 0.5],
        offsets=[0, 3, 4, 5, 6], neighbours=[1, 2, 3, 0, 0, 0],
        scores=[0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
    )
    g = GraphStore.load(p)
    assert g.degree_hub_penalty[0] >= g.degree_hub_penalty[1]
    assert 0.0 <= g.degree_hub_penalty.min() and g.degree_hub_penalty.max() <= 1.0


_HEADER = struct.Struct("<4sIIIQ")


def _build_apg1(n_header: int, mbids: list[str], offsets: list[int],
                neighbours: list[int], scores: list[float]) -> bytes:
    """Assemble an APG1 payload, allowing header/metadata disagreement on purpose."""
    meta = {
        "mbids": mbids,
        "names": [m.upper() for m in mbids],
        "disambiguations": ["" for _ in mbids],
        "popularity": [0.5 for _ in mbids],
    }
    blob = json.dumps(meta).encode()
    e = len(neighbours)
    body = (
        struct.pack(f"<{len(offsets)}i", *offsets)
        + struct.pack(f"<{e}i", *neighbours)
        + struct.pack(f"<{e}f", *scores)
        + bytes(e)
    )
    return _HEADER.pack(b"APG1", 1, n_header, e, len(blob)) + body + blob


def _good() -> bytes:
    return _build_apg1(2, ["a", "b"], [0, 1, 2], [1, 0], [0.9, 0.9])


def test_good_artifact_still_loads():
    store = GraphStore.from_bytes(_good())
    assert store.artist_count == 2


def test_truncated_artifact_raises_a_truncation_error(tmp_path):
    payload = _good()
    p = tmp_path / "t.bin"
    p.write_bytes(payload[: len(payload) - 8])
    with pytest.raises(ValueError, match="truncated"):
        GraphStore.load(p)


def test_over_long_artifact_raises(tmp_path):
    p = tmp_path / "t.bin"
    p.write_bytes(_good() + b"garbage!")
    with pytest.raises(ValueError, match="length"):
        GraphStore.load(p)


def test_header_and_metadata_length_disagreement_raises():
    # Header claims 4 nodes; metadata describes 2. This is the case that
    # currently loads SILENTLY and leaves pop_raw and degree_hub_penalty at
    # different lengths, both indexed by node id (TR-3).
    payload = _build_apg1(4, ["a", "b"], [0, 1, 1, 1, 1], [0], [0.9])
    with pytest.raises(ValueError, match="inconsistent"):
        GraphStore.from_bytes(payload)
