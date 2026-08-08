import json

import pytest

from artistpath_builder.acceptance import AcceptanceCriteria, ArtifactRejected
from artistpath_builder.cli import main
from artistpath_builder.config import CANDIDATE_ALGORITHM, PRODUCTION_ALGORITHM

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
    # A fame stage, because since the MSW- adoption (2026-08-06) `require_fame`
    # defaults ON and a build over an archive without one REFUSES. These tests
    # go through `main`, and the CLI has no flag that turns the requirement off
    # (--require-fame is store_true by design) — so the archive is made to meet
    # the shipping requirement rather than the requirement being weakened for
    # the test. Same idiom as the ULF- fixture list noted below.
    fame = archive_dir / "fame"
    fame.mkdir(parents=True)
    for mbid in (A, B):
        (fame / f"{mbid}.json").write_bytes(
            json.dumps({"fame_lb_raw": 1000, "fetched": "2026-08-06"}).encode()
        )


# The CLI has no flag for the drop rules (deliberately — turning one off is an
# experimental control, never a shipping configuration), so the build tests
# install a ULF- fixture list censusing their two-artist population instead.
def test_build_writes_an_artifact(tmp_path, install_ulf_list):
    install_ulf_list(PRODUCTION_ALGORITHM, {A, B})
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    exit_code = main(
        ["build", "--archive-dir", str(archive_dir), "--out", str(out)],
        criteria=PERMISSIVE,
    )
    assert exit_code == 0
    assert out.stat().st_size > 0


def test_build_refuses_to_write_an_artifact_that_fails_acceptance(
    tmp_path, install_ulf_list
):
    """The guard is wired into the emission point, not merely importable.

    The default criteria are the production ones, and a two-artist graph
    cannot satisfy them — so this asserts both that the check runs and that
    nothing is written when it fails.
    """
    install_ulf_list(PRODUCTION_ALGORITHM, {A, B})
    archive_dir = tmp_path / "archive"
    _write_archive(archive_dir)
    out = tmp_path / "graph.bin"

    with pytest.raises(ArtifactRejected):
        main(["build", "--archive-dir", str(archive_dir), "--out", str(out)])
    assert not out.exists()


def test_fixture_command_round_trips(tmp_path, install_ulf_list):
    install_ulf_list(PRODUCTION_ALGORITHM, {A, B})
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


def _build_config_from_argv(monkeypatch, extra_argv):
    """Parse a real `build` argv and return the BuilderConfig it produces.

    Goes through argparse rather than a hand-built Namespace deliberately: a
    Namespace test cannot see a missing `add_argument`, nor a flag whose dest
    does not match what `_config` reads. Both are the actual failure this
    helper exists to catch — MSW- Task 9 found `--cap-strategy` absent and
    `require_fame` unreachable, and neither would have shown up here.
    """
    from artistpath_builder import cli

    captured = {}

    def fake_cmd_build(args):
        captured["config"] = cli._config(args)
        return 0

    monkeypatch.setattr(cli, "cmd_build", fake_cmd_build)
    assert cli.main(["build", "--out", "unused.bin", *extra_argv]) == 0
    return captured["config"]


def test_build_cap_strategy_flag_reaches_config(monkeypatch):
    config = _build_config_from_argv(monkeypatch, ["--cap-strategy", "trimmed_union"])
    assert config.cap_strategy == "trimmed_union"


def test_build_require_fame_flag_reaches_config(monkeypatch):
    # MSW-G3's guard is only reachable from the CLI through this flag:
    # BuilderConfig has no env-driven loading, so without it a Task 9 build
    # would silently produce a FAMELESS artifact — load_fame is called only
    # `if config.require_fame` (pipeline.py) and artifact.py omits the
    # `fame_lb` key when the value is falsy.
    config = _build_config_from_argv(monkeypatch, ["--require-fame"])
    assert config.require_fame is True


def test_build_flags_absent_leaves_both_defaults_untouched(monkeypatch):
    # The red half: proves the two tests above are reading the flags rather
    # than the defaults. Flipping either default is the adoption commit
    # (Task 11), never a side effect of adding a flag.
    from artistpath_builder.config import BuilderConfig

    config = _build_config_from_argv(monkeypatch, [])
    assert config.cap_strategy == BuilderConfig().cap_strategy
    assert config.require_fame == BuilderConfig().require_fame


def test_build_rejects_an_unknown_cap_strategy(monkeypatch):
    # __post_init__ owns this validation, not the CLI. Pinned so a future
    # CLI-side shortcut cannot quietly drop it.
    with pytest.raises(ValueError, match="cap_strategy"):
        _build_config_from_argv(monkeypatch, ["--cap-strategy", "pre_symmetrise"])


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


def test_fame_command_covers_the_archive_population(tmp_path, monkeypatch):
    """The `fame` subcommand reaches the archive's artists and records each.

    The network fetcher is replaced, which is the point: the stage is testable
    without touching ListenBrainz, exactly as the crawl is.
    """
    import json as _json

    from artistpath_builder import cli as cli_module
    from artistpath_builder.archive import LocalArchive
    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.fame import fame_key
    from artistpath_builder.sources.listenbrainz import ListenBrainzSource

    config = BuilderConfig()
    source = ListenBrainzSource(config)
    archive_dir = tmp_path / "archive"
    archive = LocalArchive(archive_dir)
    mbids = ["a" * 36, "b" * 36]
    for m in mbids:
        archive.put(
            f"similar/{source.name}/{m}.json",
            _json.dumps(
                [{"artist_mbid": "c" * 36, "name": "N", "comment": "", "score": 10}]
            ).encode(),
        )

    asked = []

    def fake_fetcher(_config):
        def fetch(batch):
            asked.extend(batch)
            return {m: 42 for m in batch}

        return fetch

    monkeypatch.setattr(cli_module, "lb_fame_fetcher", fake_fetcher)
    assert cli_module.main(["fame", "--archive-dir", str(archive_dir)]) == 0
    assert sorted(asked) == sorted(mbids)
    assert _json.loads(archive.get(fame_key(mbids[0])))["fame_lb_raw"] == 42


def test_fame_seed_without_a_sha_is_refused(tmp_path):
    from artistpath_builder import cli as cli_module

    snapshot = tmp_path / "snap.json"
    snapshot.write_text("{}")
    with pytest.raises(SystemExit, match="seed-sha"):
        cli_module.main(
            [
                "fame",
                "--archive-dir",
                str(tmp_path / "archive"),
                "--seed",
                str(snapshot),
            ]
        )


def test_refrontier_recovers_the_frontier_from_the_archive(tmp_path, capsys):
    # CEX-1: the frontier past the old discovery bound was never recorded
    # (ULC-F3), so a resume rebuilt an empty queue. `refrontier` reconstructs
    # it offline from the archived responses.
    prefix = f"similar/listenbrainz/{CANDIDATE_ALGORITHM}/"
    archive_dir = tmp_path / "archive"
    (archive_dir / prefix).mkdir(parents=True)
    (archive_dir / prefix / f"{A}.json").write_text(
        json.dumps([{"artist_mbid": B, "name": "B", "score": 90}])
    )
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(
        json.dumps({"algorithm": CANDIDATE_ALGORITHM, "done": [A], "discovered": [A]})
    )

    exit_code = main(
        [
            "refrontier",
            "--checkpoint",
            str(checkpoint),
            "--archive-dir",
            str(archive_dir),
            "--algorithm",
            CANDIDATE_ALGORITHM,
        ]
    )

    assert exit_code == 0
    state = json.loads(checkpoint.read_text())
    assert set(state["discovered"]) == {A, B}
    assert "frontier" in capsys.readouterr().out
