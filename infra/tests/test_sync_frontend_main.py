"""`sync_frontend.main` must EXECUTE the plan it builds, in the plan's order (G3-Q2).

`test_sync_frontend.py` pins the order of the LIST `plan_upload` returns. That is
necessary and not sufficient: `main` unpacks the list into three names and runs
them itself, so swapping two `run(...)` lines there — publishing `index.html`
before the assets it names, which is `FRO-1` exactly — passed the whole infra
suite, including the test named for that bug.

These tests drive `main` end to end with every external effect replaced: the AWS
CLI calls go to a recorder standing in for `run` (the module shells out to
`aws`; there is no boto3 client to mock), the stack outputs and the probed
Content-Type are canned, and `dist/` is a temporary directory. No AWS, no
credentials, no npm.
"""

from __future__ import annotations

import pytest

from artistpath_infra import sync_frontend
from artistpath_infra.sync_frontend import plan_upload

BUCKET = "artistpath-spa-example"
DISTRIBUTION = "E1EXAMPLE"
AWS = "aws-under-test"


@pytest.fixture
def publish(tmp_path, monkeypatch):
    """Run `main` against a fake repo; return (recorded commands, dist path)."""
    dist = tmp_path / "frontend" / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<script src=/assets/app-abc123.js>")
    (dist / "assets" / "app-abc123.js").write_text("export {}")

    commands: list[list[str]] = []
    state = {"content_type": "text/javascript"}

    def fake_run(command, cwd=None):
        commands.append(list(command))
        if "describe-stacks" in command:
            query = command[command.index("--query") + 1]
            return BUCKET if "SpaBucketName" in query else DISTRIBUTION
        if "head-object" in command:
            return state["content_type"]
        return ""

    monkeypatch.setattr(sync_frontend, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sync_frontend, "find_aws", lambda: AWS)
    monkeypatch.setattr(sync_frontend, "run", fake_run)

    def go(argv=("--skip-build",), content_type="text/javascript"):
        state["content_type"] = content_type
        sync_frontend.main(list(argv))
        return commands

    return go, dist, commands


def _uploads(commands):
    """The commands that change the bucket or the CDN, in execution order."""
    return [
        c for c in commands
        if c[1:3] in (["s3", "sync"], ["s3", "cp"])
        or c[1:3] == ["cloudfront", "create-invalidation"]
    ]


def _expected_plan(dist, prune=False):
    return plan_upload(
        dist=str(dist), bucket=BUCKET, distribution_id=DISTRIBUTION,
        prune=prune, aws=AWS,
    )


def test_main_runs_the_plan_in_the_plans_order(publish):
    go, dist, _ = publish
    commands = go()
    # Exactly the plan, command for command, in order: assets, index, invalidate.
    assert _uploads(commands) == _expected_plan(dist)


def test_the_content_type_probe_runs_between_the_assets_and_the_index(publish):
    go, dist, _ = publish
    commands = go()
    assets, index, _ = _expected_plan(dist)
    probe = next(i for i, c in enumerate(commands) if "head-object" in c)
    assert commands.index(assets) < probe < commands.index(index)
    assert commands[probe][commands[probe].index("--key") + 1] == "assets/app-abc123.js"


def test_a_wrong_content_type_stops_before_the_index_goes_live(publish):
    # The probe is only worth anything if a failure keeps index.html off the
    # bucket: the new assets are up but nothing names them yet.
    go, dist, commands = publish
    with pytest.raises(SystemExit, match="would be served as"):
        go(content_type="text/plain")
    assets, index, invalidate = _expected_plan(dist)
    assert assets in commands
    assert index not in commands and invalidate not in commands


def test_prune_reaches_the_asset_pass_and_nothing_else(publish):
    go, dist, _ = publish
    commands = go(argv=("--skip-build", "--prune"))
    assert _uploads(commands) == _expected_plan(dist, prune=True)


def test_the_build_runs_before_anything_is_uploaded(publish):
    go, dist, _ = publish
    commands = go(argv=())
    build = commands.index([sync_frontend.NPM, "run", "build"])
    assert build < commands.index(_expected_plan(dist)[0])


def test_an_incomplete_build_uploads_nothing(publish):
    go, dist, commands = publish
    (dist / "index.html").unlink()
    with pytest.raises(SystemExit, match="no index.html"):
        go()
    assert _uploads(commands) == []
