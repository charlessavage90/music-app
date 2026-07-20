import json

import pytest

from artistpath_builder.cli import main

A, B = ("a" * 36, "b" * 36)


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def _write_archive(archive_dir):
    similar = archive_dir / "similar" / "listenbrainz"
    similar.mkdir(parents=True)
    for mbid, other, name in [(A, B, "Beta"), (B, A, "Alpha")]:
        (similar / f"{mbid}.json").write_bytes(
            json.dumps(
                [{"artist_mbid": other, "name": name, "comment": "", "score": 10}]
            ).encode()
        )


def _write_popularity(path):
    path.write_text(json.dumps({A: 100, B: 50}), encoding="utf-8")
    return path


def test_build_writes_an_artifact(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    pop = _write_popularity(tmp_path / "popularity.json")
    out = tmp_path / "graph.bin"

    exit_code = main(
        [
            "build",
            "--archive-dir", str(archive_dir),
            "--popularity", str(pop),
            "--out", str(out),
        ]
    )
    assert exit_code == 0
    assert out.stat().st_size > 0


def test_popularity_command_aggregates_listens(tmp_path):
    listens = tmp_path / "listens.jsonl"
    listens.write_text(
        "\n".join(
            json.dumps(
                {
                    "user_name": user,
                    "track_metadata": {"mbid_mapping": {"artist_mbids": [A]}},
                }
            )
            for user in ["alice", "alice", "bob"]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "popularity.json"
    assert main(["popularity", "--out", str(out), "--listens", str(listens)]) == 0
    # Two distinct listeners, three plays.
    assert json.loads(out.read_text(encoding="utf-8")) == {A: 2}


def test_fixture_command_round_trips(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    pop = _write_popularity(tmp_path / "popularity.json")
    graph_path = tmp_path / "graph.bin"
    main(
        [
            "build",
            "--archive-dir", str(archive_dir),
            "--popularity", str(pop),
            "--out", str(graph_path),
        ]
    )

    fixture_path = tmp_path / "fixture.bin"
    exit_code = main(
        [
            "fixture",
            "--graph", str(graph_path),
            "--out", str(fixture_path),
            "--size", "2",
        ]
    )
    assert exit_code == 0
    assert fixture_path.stat().st_size > 0


def test_bootstrap_serialisation_round_trips(tmp_path):
    # Regression: BootstrapArtist is a slots=True dataclass and has no
    # __dict__, so serialisation must use dataclasses.asdict. This path is
    # otherwise only exercised behind a network call.
    from artistpath_builder.cli import write_bootstrap
    from artistpath_builder.models import BootstrapArtist

    out = tmp_path / "bootstrap.json"
    write_bootstrap([BootstrapArtist(mbid=A, name="Alpha")], out)

    rows = json.loads(out.read_text(encoding="utf-8"))
    assert rows == [{"mbid": A, "name": "Alpha"}]
