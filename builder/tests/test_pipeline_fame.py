"""Fame reaching the artifact, and refusing to build without it (`MSW-`, Task 4).

`MSW-G3`. The refusal is the `ULC-F1` shape applied to a new quantity: a lookup
that quietly succeeds over a smaller population than the one being built leaves
new artists unevaluated. For a drop list that means under-filtering; for fame it
means an artist priced by a default in a cost function that routes on the price.
Neither is acceptable, and the fix is the same — refuse, loudly, naming who is
missing.

`require_fame` was OFF by default until the `MSW-` adoption of 2026-08-06, which
flipped it ON alongside `cap_strategy` and the API's ramp knob. Until the router
read fame, a fame-less build was genuinely valid; now that it routes on fame, an
archive with no `fame` stage run against it refuses to build.

The tests below that exercise the fame-less path therefore pass
`require_fame=False` EXPLICITLY rather than inheriting it. That is deliberate:
the path is still supported and still worth testing, it is simply no longer the
default.
"""

import json

import pytest

from artistpath_builder.archive import LocalArchive
from artistpath_builder.config import BuilderConfig
from artistpath_builder.fame import MissingFameError, fame_key
from artistpath_builder.pipeline import build_from_archive
from artistpath_builder.sources.listenbrainz import ListenBrainzSource


def _body(rows):
    return json.dumps(
        [{"artist_mbid": m, "name": m[:4], "comment": "", "score": s} for m, s in rows]
    ).encode()


def _seed_similarity(archive, source, mbids):
    """A dense mutual mesh, so every seeded artist survives to the artifact."""
    for m in mbids:
        archive.put(
            f"similar/{source.name}/{m}.json",
            _body([(o, 100) for o in mbids if o != m]),
        )


def _seed_fame(archive, values, fetched="2026-08-05"):
    for mbid, value in values.items():
        archive.put(
            fame_key(mbid),
            json.dumps({"fame_lb_raw": value, "fetched": fetched}).encode(),
        )


def _setup(tmp_path, **overrides):
    config = BuilderConfig(
        requests_per_second=1000.0, drop_unlistenable=False, **overrides
    )
    archive = LocalArchive(tmp_path / "archive")
    source = ListenBrainzSource(config)
    mbids = [f"{i:04d}" + "e" * 32 for i in range(6)]
    _seed_similarity(archive, source, mbids)
    return config, archive, source, mbids


def test_build_carries_one_fame_value_per_node(tmp_path):
    config, archive, source, mbids = _setup(tmp_path, require_fame=True)
    _seed_fame(archive, {m: i * 10 for i, m in enumerate(mbids)})
    graph = build_from_archive(config, archive, source)
    assert len(graph.fame_lb_raw) == len(graph.mbids)


def test_fame_values_are_aligned_with_node_ids(tmp_path):
    # The alignment is the whole contract: the api indexes this list by node
    # id. A silently mis-ordered list would price every artist as someone else,
    # and nothing downstream could detect it.
    config, archive, source, mbids = _setup(tmp_path, require_fame=True)
    values = {m: i * 10 for i, m in enumerate(mbids)}
    _seed_fame(archive, values)
    graph = build_from_archive(config, archive, source)
    for node_id, mbid in enumerate(graph.mbids):
        assert graph.fame_lb_raw[node_id] == values[mbid]


def test_nulls_survive_into_the_artifact_as_nulls(tmp_path):
    # A null is a measured absence — maximal obscurity — and must never be
    # rewritten to a floor value on the way in (FAM- §1, FAM-AM1.8).
    config, archive, source, mbids = _setup(tmp_path, require_fame=True)
    values = {m: None for m in mbids}
    values[mbids[0]] = 5
    _seed_fame(archive, values)
    graph = build_from_archive(config, archive, source)
    assert graph.fame_lb_raw.count(None) == len(mbids) - 1


def test_build_refuses_when_a_graph_artist_has_no_fame_record(tmp_path):
    config, archive, source, mbids = _setup(tmp_path, require_fame=True)
    _seed_fame(archive, {m: 1 for m in mbids[:-1]})  # one artist uncovered
    with pytest.raises(MissingFameError) as excinfo:
        build_from_archive(config, archive, source)
    assert mbids[-1] in str(excinfo.value)


def test_the_refusal_names_the_count_and_the_remedy(tmp_path):
    config, archive, source, _ = _setup(tmp_path, require_fame=True)
    with pytest.raises(MissingFameError) as excinfo:
        build_from_archive(config, archive, source)
    message = str(excinfo.value)
    assert "fame" in message
    assert "Refusing to build" in message


def test_fame_is_required_by_default_since_adoption(tmp_path):
    # This assertion read `is False` until the MSW- adoption of 2026-08-06.
    # It is flipped rather than deleted: the default is what routes real
    # traffic, so a silent change to it must be a test failure.
    #
    # The build below is seeded with similarity but NO fame, so the new
    # default alone is enough to make it refuse — which is the point of the
    # flip, exercised rather than asserted.
    config, archive, source, _ = _setup(tmp_path)
    assert config.require_fame is True
    with pytest.raises(MissingFameError):
        build_from_archive(config, archive, source)


def test_a_fameless_build_is_still_supported_when_not_required(tmp_path):
    # The fame-less path did not go away at adoption, it just stopped being
    # the default. Pinned so the flip cannot quietly delete a supported mode.
    config, archive, source, _ = _setup(tmp_path, require_fame=False)
    graph = build_from_archive(config, archive, source)
    assert graph.fame_lb_raw == []


def test_fame_records_are_ignored_when_not_required(tmp_path):
    # Present-but-unrequested fame must not leak into the artifact: that would
    # make the byte output depend on whether an unrelated stage had been run.
    config, archive, source, mbids = _setup(tmp_path, require_fame=False)
    _seed_fame(archive, {m: 7 for m in mbids})
    graph = build_from_archive(config, archive, source)
    assert graph.fame_lb_raw == []


def test_fame_survives_the_whole_chain_to_a_deserialised_artifact(tmp_path):
    """fetch -> archive -> build -> serialise -> deserialise, values intact.

    Each half is unit-tested above and in test_artifact.py; this is the chain.
    The APG1 format is the contract between two packages that share no code,
    so the round trip is where a mismatch would actually surface.
    """
    from artistpath_builder.artifact import deserialise, serialise
    from artistpath_builder.fame import fetch_fame

    config, archive, source, mbids = _setup(tmp_path, require_fame=True)
    wanted = {m: (None if i % 3 == 0 else i * 11) for i, m in enumerate(mbids)}
    fetch_fame(
        archive,
        mbids,
        lambda batch: {m: wanted[m] for m in batch},
        batch_size=2,
        today="2026-08-05",
    )

    graph = build_from_archive(config, archive, source)
    restored = deserialise(serialise(graph))

    assert restored.fame_lb_raw == graph.fame_lb_raw
    for node_id, mbid in enumerate(restored.mbids):
        assert restored.fame_lb_raw[node_id] == wanted[mbid]
    assert None in restored.fame_lb_raw, "nulls must survive the whole chain"
