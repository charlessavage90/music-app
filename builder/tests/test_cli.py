import json

import pytest

from artistpath_builder.acceptance import AcceptanceCriteria, ArtifactRejected
from artistpath_builder.cli import main

A, B = ("a" * 36, "b" * 36)

# ALG-B: the named re-crawl candidate (AS log §7). Differs from production by
# contribution_3.
ALG_B = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)

# These tests exercise the CLI plumbing on a two-artist archive, which cannot
# satisfy the production structural invariants. The invariants themselves are
# tested in test_acceptance.py; here they are relaxed so the commands under
# test are the subject. `main` takes this keyword in-process only — there is
# no command-line flag that relaxes acceptance.
PERMISSIVE = AcceptanceCriteria(
    canonical_names=(),
    famous_sample=1,
    famous_median_degree_floor=0.0,
    famous_min_degree_floor=0,
    node_count=(1, 100),
    edge_count=(1, 100),
    median_degree=(0.0, 100.0),
)


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


def test_build_writes_an_artifact(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    exit_code = main(
        ["build", "--archive-dir", str(archive_dir), "--out", str(out)],
        criteria=PERMISSIVE,
    )
    assert exit_code == 0
    assert out.stat().st_size > 0


def test_build_refuses_to_write_an_artifact_that_fails_acceptance(tmp_path):
    """The guard is wired into the emission point, not merely importable.

    The default criteria are the production ones, and a two-artist graph
    cannot satisfy them — so this asserts both that the check runs and that
    nothing is written when it fails.
    """
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    with pytest.raises(ArtifactRejected):
        main(["build", "--archive-dir", str(archive_dir), "--out", str(out)])
    assert not out.exists()


def test_fixture_command_round_trips(tmp_path):
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    graph_path = tmp_path / "graph.bin"
    main(
        ["build", "--archive-dir", str(archive_dir), "--out", str(graph_path)],
        criteria=PERMISSIVE,
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


def test_config_threads_algorithm_override():
    import argparse

    from artistpath_builder.cli import _config
    from artistpath_builder.config import PERMITTED_ALGORITHMS

    args = argparse.Namespace(target=None, algorithm=ALG_B)
    assert _config(args).algorithm == ALG_B
    assert ALG_B in PERMITTED_ALGORITHMS


def test_config_rejects_a_value_outside_the_closed_enum():
    import argparse

    from artistpath_builder.cli import _config

    args = argparse.Namespace(target=None, algorithm="definitely_not_a_real_algorithm")
    with pytest.raises(SystemExit):
        _config(args)


def test_config_default_algorithm_is_production():
    # Flipping this default IS the re-crawl decision, which is the owner's
    # (NEXT.md). A trial run overrides it per-invocation; nothing else may.
    import argparse

    from artistpath_builder.cli import _config
    from artistpath_builder.config import PRODUCTION_ALGORITHM

    assert _config(argparse.Namespace()).algorithm == PRODUCTION_ALGORITHM


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
