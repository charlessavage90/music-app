"""Pins what the api's APG1 reader decodes from the committed fixture.

`builder/` writes APG1 and this package reads it; they share no code and are
kept in lockstep by hand. `conftest.fixture_store` loads `graph-fixture.bin`
for the smoke and pathfinding tests, but those only need a plausible graph —
a reader that misread a section consistently could still route through it.

This test fixes the reader to the file's actual contents: the header fields,
the section layout the header implies, and literal values decoded from every
section (metadata strings including non-ASCII, raw popularity, offsets,
neighbours, scores). Its counterpart, `builder/tests/test_apg1_fixture_lockstep.py`,
proves builder's writer still re-emits this exact file byte for byte. Together
they pin writer and reader to the same bytes without either importing the other.

The literals were read from the fixture on 2026-09-10. If the fixture is
regenerated on purpose, the sha check fails first: re-derive every literal
below from the new file, and keep the builder copy byte-identical.
"""

from __future__ import annotations

import hashlib
import struct

from artistpath_api.graph_store import GraphStore

from conftest import FIXTURES

FIXTURE = FIXTURES / "graph-fixture.bin"
FIXTURE_SHA256 = "f30676533aa95f7b5fbbae33e1fe581fef6343e121d8f71e93fb5c8a4f6de9ba"

N = 500
E = 8724
METADATA_LENGTH = 43744

# node id -> (mbid, name, pop_raw, offsets[node], offsets[node + 1])
NODES = {
    0: ("000fc734-b7e1-4a01-92d1-f544261b43f5", "Cocteau Twins", 0.5003594756126404, 0, 12),
    1: ("0039c7ae-e1a7-4a7d-9b49-0cbc716821a6", "Death Cab for Cutie", 0.5437254309654236, 12, 32),
    # Non-ASCII: the metadata blob is UTF-8, and a mis-decode is silent.
    88: ("26f07661-e115-471d-a930-206f5c89d17c", "Mötley Crüe", 0.5423397421836853, 1775, 1794),
    499: ("ff81d878-cc98-44d4-a823-1d7c590cf1d8", "Bob B. Soxx and the Blue Jeans", 0.4335223138332367, 8721, 8724),
}
NEIGHBOURS_HEAD = [18, 133, 138, 164]
NEIGHBOURS_TAIL = [119, 366, 411]
# The head scores are all 1.0 and would not catch a misread section; the tail's are distinct.
SCORES_TAIL = [0.9514060616493225, 0.9429564476013184, 0.9378626942634583]


def test_fixture_is_the_file_these_literals_were_read_from():
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert digest == FIXTURE_SHA256, (
        "graph-fixture.bin changed; re-derive every literal in this file from "
        "the new fixture and keep builder/tests/fixtures/graph-fixture.bin identical"
    )


def test_header_and_section_layout_match_the_spec():
    payload = FIXTURE.read_bytes()
    assert struct.unpack_from("<4sIIIQ", payload) == (b"APG1", 1, N, E, METADATA_LENGTH)
    # header, int32[N+1] offsets, int32[E] neighbours, float32[E] scores,
    # uint8[E] edge types, metadata JSON.
    assert len(payload) == 24 + (N + 1) * 4 + E * 4 + E * 4 + E + METADATA_LENGTH


def test_graph_store_decodes_the_fixture_to_these_values():
    store = GraphStore.load(FIXTURE)

    assert store.artist_count == N
    assert len(store.names) == len(store.disambiguations) == len(store.pop_raw) == N
    assert store.offsets.shape == (N + 1,)
    assert store.neighbours.shape == store.scores.shape == (E,)
    assert int(store.offsets[-1]) == E

    for node, (mbid, name, pop_raw, start, end) in NODES.items():
        assert store.mbids[node] == mbid
        assert store.names[node] == name
        assert store.id_by_mbid[mbid] == node
        assert float(store.pop_raw[node]) == pop_raw
        assert (int(store.offsets[node]), int(store.offsets[node + 1])) == (start, end)

    assert store.neighbours[: len(NEIGHBOURS_HEAD)].tolist() == NEIGHBOURS_HEAD
    assert store.neighbours[-len(NEIGHBOURS_TAIL) :].tolist() == NEIGHBOURS_TAIL
    assert [float(s) for s in store.scores[-len(SCORES_TAIL) :]] == SCORES_TAIL
