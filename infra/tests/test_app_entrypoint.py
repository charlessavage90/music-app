"""`infra/app.py` must refuse a deploy that cannot say what it is deploying.

QUA-10 recorded that this file had no test at all. DEP-34 is what that cost: two
deploy inputs defaulted to the pre-MSW artifact, `.env.deploy` sets neither, and
so an API-only deploy silently reverted the adopted graph. It was caught by a
person reading a `cdk diff`, which is not a gate.

These run `app.py` as a SUBPROCESS rather than importing it. Importing would
execute the CDK app at module scope — and, more to the point, the defect being
pinned here IS module-scope behaviour, so it has to be exercised the way `cdk`
exercises it.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

INFRA = Path(__file__).resolve().parents[1]

# Everything app.py needs BEFORE it reaches the variable under test, so a run
# fails for the reason the test is about and not for the first missing secret.
BASE_ENV = {
    "ARTISTPATH_DEPLOY_SIDECAR": "../builder/scratch/graph-msw-tu50.bin.json",
    "ARTISTPATH_DEPLOY_GRAPH_KEY": "graph-msw-tu50.bin",
    "ARTISTPATH_DEPLOY_ORIGIN_SECRET": "x",
    "ARTISTPATH_FRONT_DOOR_SECRET": "x",
    "ARTISTPATH_DEPLOY_BILLING_USD": "5",
    "ARTISTPATH_DEPLOY_ALARM_EMAIL": "x@example.com",
    "ARTISTPATH_DEPLOY_IMAGE_TAG": "sometag",
    "ARTISTPATH_SITE_HOSTNAME": "example.com",
    "ARTISTPATH_CERTIFICATE_ARN": "arn:aws:acm:us-east-1:1:certificate/x",
}


def run_app(env_overrides: dict[str, str | None]) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, **BASE_ENV, "JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION": "1"}
    for key, value in env_overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return subprocess.run(
        [sys.executable, "app.py"],
        cwd=INFRA, env=env, capture_output=True, text=True, timeout=300,
    )


@pytest.mark.parametrize(
    "missing",
    ["ARTISTPATH_DEPLOY_GRAPH_KEY", "ARTISTPATH_DEPLOY_SIDECAR"],
)
def test_graph_inputs_are_required_not_defaulted(missing: str) -> None:
    """DEP-34-FIX. Both of these DEFAULTED to the pre-MSW artifact.

    The reason both are here rather than only the key: the two defaults agreed
    with each other, so the reverted service booted, matched its own sidecar and
    passed every downstream check. Requiring one and defaulting the other just
    relocates the silent revert into the checksum.
    """
    result = run_app({missing: None})
    assert result.returncode != 0, (
        f"{missing} is unset and app.py still synthesised. A deploy that cannot "
        "say which graph it is deploying must stop (DEP-34)."
    )
    assert missing in result.stderr, (
        f"exited, but never named {missing}; stderr was:\n{result.stderr}"
    )


def test_no_deploy_input_still_names_the_retired_artifact() -> None:
    """The old defaults must not survive anywhere in the entrypoint.

    A grep, deliberately: the failure mode was a DEFAULT, and a default is
    invisible to every test that supplies the variable. This is the check that
    would have caught DEP-34 before it shipped.
    """
    source = (INFRA / "app.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )
    assert "graph-t15-tiebreakfix" not in code, (
        "the retired pre-MSW artifact is still a default in app.py's code"
    )
