import json
from pathlib import Path

from artistpath_builder.config import BuilderConfig
from artistpath_builder.manifest import build_manifest, write_manifest


class _FakeGraph:
    artist_count = 3
    edge_count = 4


def test_manifest_records_config_and_shape():
    m = build_manifest(_FakeGraph(), BuilderConfig(), b"abc", elapsed_seconds=12.5)
    assert m["artists"] == 3
    assert m["edges"] == 4
    assert m["elapsed_seconds"] == 12.5
    assert m["sha256"] == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    # Every tunable that changes the artifact must be recorded.
    assert m["config"]["similarity_damping"] == 0.0
    assert m["config"]["max_neighbours_per_artist"] == 50


def test_manifest_records_git_commit():
    m = build_manifest(_FakeGraph(), BuilderConfig(), b"abc", elapsed_seconds=1.0)
    # 40-char sha, or "unknown" when git is unavailable.
    assert len(m["git_commit"]) == 40 or m["git_commit"] == "unknown"


def test_write_manifest_is_sidecar_json(tmp_path: Path):
    out = tmp_path / "graph-test.bin"
    write_manifest(out, {"artists": 3})
    sidecar = tmp_path / "graph-test.bin.json"
    assert json.loads(sidecar.read_text(encoding="utf-8"))["artists"] == 3


def test_manifest_survives_a_path_valued_config_field(tmp_path):
    """A build that sets `--unlistenable-list` must still get a manifest.

    Shown red before being kept: `dataclasses.asdict` preserves
    `BuilderConfig.unlistenable_list_path` as a `Path`, and `json.dumps` refuses
    it — so `write_manifest` raised `TypeError: Object of type WindowsPath is not
    JSON serializable`. It had never fired, because every build that set the flag
    was rejected by acceptance BEFORE serialising and every build that reached a
    manifest used the default of `None`. It fires on the first adoption build off
    a censused payload, after ~28 minutes, with the artifact already written.
    """
    import json
    from pathlib import Path

    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.manifest import build_manifest, write_manifest

    class _Graph:
        artist_count = 3
        edge_count = 4

    payload_list = tmp_path / "droplist.json"
    payload_list.write_text("{}", encoding="utf-8")
    config = BuilderConfig(unlistenable_list_path=payload_list)

    manifest = build_manifest(_Graph(), config, b"abc", 1.0)
    assert manifest["config"]["unlistenable_list_path"] == str(payload_list)

    artifact = tmp_path / "graph.bin"
    artifact.write_bytes(b"abc")
    write_manifest(artifact, manifest)
    written = json.loads(
        (tmp_path / "graph.bin.json").read_text(encoding="utf-8")
    )
    assert Path(written["config"]["unlistenable_list_path"]) == payload_list
