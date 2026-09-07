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


# --- Which files actually built this graph (the fired ULF-/CXA- deferral) ----
#
# A manifest could say `drop_unlistenable: true` but never WHICH list, and the
# override pointer read `null` — meaning "whatever the default was that day",
# where the default is mutable. `CXA-` Task 2 moved the ALG-B unlistenable
# default and the `CXR-` revert did not move it back, so a rebuild silently
# differed from the live map by 31 artists and establishing that took a hand
# analysis. Recording only: a mismatch is not a refusal (owner, 2026-09-05).


def _algb_config(**kw) -> BuilderConfig:
    from artistpath_builder.config import CANDIDATE_ALGORITHM

    return BuilderConfig(algorithm=CANDIDATE_ALGORITHM, **kw)


def test_build_inputs_name_the_resolved_file_not_just_the_flag():
    from hashlib import sha256

    from artistpath_builder.manifest import resolve_build_inputs

    inputs = resolve_build_inputs(_algb_config(), archive_dir=Path("a/b"))
    ulf = inputs["drop_lists"]["unlistenable"]
    assert ulf["file"] == "unlistenable_drop_algb_20260805.json"

    # The sha is over the FILE'S BYTES, deliberately: the payloads' own hash
    # keys are inconsistent between families and featured_credit carries none.
    from artistpath_builder.unlistenable_drop import (
        CANDIDATE_UNLISTENABLE_DROP_LIST_PATH,
    )

    expected = sha256(CANDIDATE_UNLISTENABLE_DROP_LIST_PATH.read_bytes()).hexdigest()
    assert ulf["sha256"] == expected


def test_build_inputs_record_all_three_families_and_the_archive():
    from artistpath_builder.manifest import resolve_build_inputs

    inputs = resolve_build_inputs(_algb_config(), archive_dir=Path("scratch/arc"))
    assert set(inputs["drop_lists"]) == {
        "no_release",
        "featured_credit",
        "unlistenable",
    }
    # The archive is the other input that drifted; a path is weak identity but
    # it is exactly what separates the pre-CEX snapshot from the live archive.
    assert inputs["archive_dir"].endswith("arc")


def test_a_family_whose_flag_is_off_is_absent_not_null():
    """Absence means "not applied". A null would read as "applied, unknown"."""
    from artistpath_builder.manifest import resolve_build_inputs

    inputs = resolve_build_inputs(
        _algb_config(drop_unlistenable=False), archive_dir=Path("a")
    )
    assert "unlistenable" not in inputs["drop_lists"]


def test_a_per_invocation_override_is_what_gets_recorded(tmp_path):
    """The override is the case the algorithm-keyed default cannot express."""
    from artistpath_builder.manifest import resolve_build_inputs
    from artistpath_builder.unlistenable_drop import UNLISTENABLE_DROP_LISTS

    override = UNLISTENABLE_DROP_LISTS[BuilderConfig().algorithm]
    inputs = resolve_build_inputs(
        _algb_config(unlistenable_list_path=override), archive_dir=Path("a")
    )
    assert inputs["drop_lists"]["unlistenable"]["file"] == override.name


def test_build_manifest_carries_build_inputs_when_given():
    from artistpath_builder.manifest import build_manifest, resolve_build_inputs

    inputs = resolve_build_inputs(_algb_config(), archive_dir=Path("a"))
    m = build_manifest(_FakeGraph(), _algb_config(), b"abc", 1.0, build_inputs=inputs)
    assert m["build_inputs"]["drop_lists"]["unlistenable"]["file"]


def test_build_manifest_stays_positional_for_the_frozen_probes():
    """`analysis/2026-08-09-jfx-prereg-critique/` calls this with four args.

    Same discipline as `Graph.deezer_ids`: the new field is defaulted, and a
    caller that omits it gets a manifest with no `build_inputs` key at all.
    """
    m = build_manifest(_FakeGraph(), BuilderConfig(), b"abc", 1.0)
    assert "build_inputs" not in m
