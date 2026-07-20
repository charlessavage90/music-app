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
    stats = archive_dir / "stats"
    similar.mkdir(parents=True)
    stats.mkdir(parents=True)
    for mbid, other, name, users in [(A, B, "Alpha", 100), (B, A, "Beta", 50)]:
        (similar / f"{mbid}.json").write_bytes(
            json.dumps([{"artist_mbid": other, "name": "X", "score": 10}]).encode()
        )
        (stats / f"{mbid}.json").write_bytes(
            json.dumps(
                {
                    "payload": {
                        "artist_mbid": mbid,
                        "artist_name": name,
                        "total_user_count": users,
                        "total_listen_count": users * 7,
                    }
                }
            ).encode()
        )


def test_build_writes_an_artifact(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    exit_code = main(["build", "--archive-dir", str(archive_dir), "--out", str(out)])
    assert exit_code == 0
    assert out.stat().st_size > 0


def test_build_needs_no_seeds_file(tmp_path):
    # Popularity lives in the archive; there is no separate seeds artifact
    # to drift out of sync with it.
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"
    assert main(["build", "--archive-dir", str(archive_dir), "--out", str(out)]) == 0


def test_fixture_command_round_trips(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    graph_path = tmp_path / "graph.bin"
    main(["build", "--archive-dir", str(archive_dir), "--out", str(graph_path)])

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
