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
