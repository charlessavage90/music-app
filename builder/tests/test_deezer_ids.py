"""Deezer artist ids carried in the APG1 metadata blob.

WHY: `BYP-13` -- a card playing a clip by a DIFFERENT ARTIST OF THE SAME NAME,
because clips are resolved by searching the artist's NAME. A
MusicBrainz-recorded Deezer artist id names the exact artist, so a clip found
through it cannot be the wrong same-named one.

The two constraints these tests exist to hold, both of which are easy to break
and invisible when broken:

1. **`serialise` omits the key when there are no ids.** Two frozen probe
   mirrors build artifacts through `build_graph` and their committed shas are
   pinned by Track B's identity gate. Writing the key unconditionally changes
   every mirror-built artifact's bytes and fails that gate -- the exact
   divergence class PR #63 closed. Omission keeps them byte-identical.

2. **`build_graph`'s signature stays positional-compatible.**
   `cb_build_variants.py:479` and `measure_headroom.py:151` call it with three
   positional arguments and are FROZEN. The ids parameter must be optional.

The map is a dated snapshot and is never re-resolved at build time: the builder
is offline by a hard rule and spec section 9 requires byte-identical builds.
"""

import json
from hashlib import sha256

import numpy as np

from artistpath_builder.artifact import deserialise, serialise
from artistpath_builder.deezer_ids import DEEZER_IDS_SHA256, load_deezer_ids
from artistpath_builder.graph import Graph, build_graph
from artistpath_builder.models import ArtistStats, EdgeType

# Recorded in NEXT.md and reproduced from the frozen probe output:
# sha256 of json.dumps(sorted(deezer_ids.items()), sort_keys=True).
RECORDED_SHA256 = "7d204111284c7e50450d20af704168d26846a2607f761ef5103eef0514b52fb6"
RECORDED_COUNT = 39465

A, B = ("a" * 36, "b" * 36)


def _stats(mbid, name):
    return ArtistStats(
        mbid=mbid, name=name, pop_indegree_scaled=10, listen_count=0,
        disambiguation="",
    )


def _graph(deezer_ids=None):
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    stats = [_stats(A, "Alpha"), _stats(B, "Beta")]
    return build_graph(adjacency, stats, EdgeType.BEHAVIOURAL,
                       deezer_ids=deezer_ids)


def test_build_graph_still_takes_three_positional_arguments():
    # cb_build_variants.py:479 and measure_headroom.py:151 are FROZEN and call
    # it exactly this way. If this fails, those probes stop executing.
    adjacency = {A: {B: 1.0}, B: {A: 1.0}}
    stats = [_stats(A, "Alpha"), _stats(B, "Beta")]
    graph = build_graph(adjacency, stats, EdgeType.BEHAVIOURAL)
    assert graph.deezer_ids == []


def test_ids_are_ordered_by_node_id_not_by_mbid_insertion():
    # Every other metadata list is indexed by node id; this one must be too, or
    # the api reads one artist's id against another artist's row.
    graph = _graph({B: "222", A: "111"})
    assert graph.mbids == [A, B]
    assert graph.deezer_ids == ["111", "222"]


def test_an_artist_with_no_id_gets_an_empty_string():
    graph = _graph({A: "111"})
    assert graph.deezer_ids == ["111", ""]


def test_ids_survive_a_serialise_deserialise_round_trip():
    graph = _graph({A: "111", B: "222"})
    assert deserialise(serialise(graph)).deezer_ids == ["111", "222"]


def test_the_key_is_omitted_when_there_are_no_ids():
    # Constraint 1. A mirror-built artifact must stay byte-identical to the one
    # it built before this feature existed.
    payload = serialise(_graph())
    meta = json.loads(payload[payload.index(b'{"disambiguations"'):])
    assert "deezer_ids" not in meta


def test_an_artifact_without_the_key_still_deserialises():
    # The adopted artifact the app serves today has no such key.
    graph = deserialise(serialise(_graph()))
    assert graph.deezer_ids == []


def test_omitting_the_key_leaves_the_bytes_unchanged():
    # The sharpest form of constraint 1: identical to a graph whose field does
    # not exist at all, which is what the frozen mirrors produce.
    with_field = _graph()
    without = Graph(
        mbids=with_field.mbids,
        names=with_field.names,
        disambiguations=with_field.disambiguations,
        pop_raw=with_field.pop_raw,
        offsets=with_field.offsets,
        neighbours=with_field.neighbours,
        scores=with_field.scores,
        edge_types=with_field.edge_types,
    )
    assert serialise(with_field) == serialise(without)


def test_shipped_map_matches_the_frozen_snapshot():
    ids = load_deezer_ids()
    assert len(ids) == RECORDED_COUNT
    digest = sha256(json.dumps(sorted(ids.items()), sort_keys=True).encode()).hexdigest()
    assert digest == RECORDED_SHA256
    assert DEEZER_IDS_SHA256 == RECORDED_SHA256


def test_every_shipped_id_is_a_bare_deezer_artist_id():
    # A URL fragment or a locale query string reaching the api would be
    # requested verbatim against the Deezer artist endpoint and 404 silently.
    ids = load_deezer_ids()
    bad = [v for v in ids.values() if not v.isdigit()]
    assert bad[:5] == []
