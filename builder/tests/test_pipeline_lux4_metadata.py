"""`LUX-4` links and facts reaching the artifact, node-indexed (`L4-T5`).

Same contract and same failure mode as the fame wiring next door: the api
indexes these lists BY NODE ID, so a silently mis-ordered list would show every
artist someone else's streaming link, and nothing downstream could detect it.

Node ids are assigned inside `build_graph` (sorted-MBID order), which is why
the maps are passed to it as DICTS and projected there. A caller pre-ordering
them would be re-deriving `sorted(...)` and could silently disagree with it --
`build_graph`'s own docstring makes that point about `fame_lb_raw`, and it
applies unchanged here.
"""

import json

from artistpath_builder import pipeline as pipeline_mod
from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource


def _body(rows):
    return json.dumps(
        [{"artist_mbid": m, "name": m[:4], "comment": "", "score": s} for m, s in rows]
    ).encode()


def _setup(tmp_path):
    # require_fame=False EXPLICITLY: it has been on by default since the MSW-
    # adoption, and this module tests metadata that is orthogonal to fame. Same
    # discipline test_pipeline_fame.py documents -- the fame-less path is still
    # supported, it is simply no longer the default.
    config = BuilderConfig(
        requests_per_second=1000.0, drop_unlistenable=False, require_fame=False
    )
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    mbids = [f"{i:04d}" + "e" * 32 for i in range(6)]
    for m in mbids:
        archive.put(
            f"similar/{source.name}/{m}.json",
            _body([(o, 100) for o in mbids if o != m]),
        )
    return config, archive, source, mbids


def _install(monkeypatch, spotify=None, apple=None, facts=None):
    monkeypatch.setattr(
        pipeline_mod, "load_dsp_links", lambda: (spotify or {}, apple or {})
    )
    monkeypatch.setattr(pipeline_mod, "load_artist_facts", lambda: facts or {})


def test_build_carries_one_slot_per_node(tmp_path, monkeypatch):
    config, archive, source, mbids = _setup(tmp_path)
    _install(
        monkeypatch,
        spotify={mbids[0]: "x" * 22},
        apple={mbids[1]: "12345"},
        facts={mbids[2]: {"type": "Group"}},
    )
    graph = build_from_archive(config, archive, source)
    assert len(graph.spotify_ids) == len(graph.mbids)
    assert len(graph.apple_ids) == len(graph.mbids)
    assert len(graph.artist_facts) == len(graph.mbids)


def test_a_populated_map_is_node_indexed_but_an_empty_one_stays_empty(
    tmp_path, monkeypatch
):
    """The two states are different on purpose, and the difference is load-bearing.

    A map with even ONE entry becomes a full node-indexed list, mostly of
    absences. A map with NO entries stays [] so that `serialise` omits the key
    entirely and a pre-LUX-4 artifact keeps its bytes. Each of the three is
    decided independently, so a build with links but no facts writes two keys
    and not three.
    """
    config, archive, source, mbids = _setup(tmp_path)
    _install(monkeypatch, spotify={mbids[0]: "x" * 22})
    graph = build_from_archive(config, archive, source)
    assert len(graph.spotify_ids) == len(graph.mbids)
    assert graph.apple_ids == []
    assert graph.artist_facts == []


def test_values_are_aligned_with_node_ids(tmp_path, monkeypatch):
    """The alignment IS the contract -- see this module's docstring."""
    config, archive, source, mbids = _setup(tmp_path)
    spotify = {m: f"s{i:021d}" for i, m in enumerate(mbids)}
    apple = {m: str(1000 + i) for i, m in enumerate(mbids)}
    facts = {m: {"type": "Group", "country": f"C{i}"} for i, m in enumerate(mbids)}
    _install(monkeypatch, spotify=spotify, apple=apple, facts=facts)
    graph = build_from_archive(config, archive, source)
    for node_id, mbid in enumerate(graph.mbids):
        assert graph.spotify_ids[node_id] == spotify[mbid]
        assert graph.apple_ids[node_id] == apple[mbid]
        assert graph.artist_facts[node_id] == facts[mbid]


def test_an_artist_with_no_link_gets_an_empty_slot_not_a_gap(tmp_path, monkeypatch):
    """Parallel-to-mbids means every node has a slot. An absent id is the empty
    string, which the api reads as "fall back to a search link"."""
    config, archive, source, mbids = _setup(tmp_path)
    _install(monkeypatch, spotify={mbids[2]: "y" * 22})
    graph = build_from_archive(config, archive, source)
    assert all(isinstance(v, str) for v in graph.spotify_ids)
    assert graph.spotify_ids.count("") == len(graph.mbids) - 1
    assert all(v == "" for v in graph.apple_ids)


def test_an_artist_with_no_facts_gets_an_empty_dict(tmp_path, monkeypatch):
    config, archive, source, mbids = _setup(tmp_path)
    _install(monkeypatch, facts={mbids[1]: {"type": "Person"}})
    graph = build_from_archive(config, archive, source)
    assert all(isinstance(v, dict) for v in graph.artist_facts)
    assert graph.artist_facts.count({}) == len(graph.mbids) - 1


def test_an_mbid_outside_the_graph_does_not_leak_in(tmp_path, monkeypatch):
    """The maps are extracted over a SUPERSET population deliberately, so most
    of their entries belong to no node in any given build."""
    config, archive, source, mbids = _setup(tmp_path)
    _install(monkeypatch, spotify={"f" * 36: "z" * 22, mbids[0]: "w" * 22})
    graph = build_from_archive(config, archive, source)
    assert "z" * 22 not in graph.spotify_ids
    assert graph.spotify_ids.count("w" * 22) == 1


def test_empty_maps_leave_the_lists_empty_so_the_keys_are_omitted(
    tmp_path, monkeypatch
):
    """The link to `L4-T6`'s omit-when-empty rule. An empty list is what makes
    `serialise` leave the key out, which is what keeps every pre-LUX-4
    artifact -- including the frozen probe mirrors -- byte-identical."""
    config, archive, source, _ = _setup(tmp_path)
    _install(monkeypatch)
    graph = build_from_archive(config, archive, source)
    assert graph.spotify_ids == []
    assert graph.apple_ids == []
    assert graph.artist_facts == []
