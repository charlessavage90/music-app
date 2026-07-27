"""Behavioural tests for the CloudFront viewer function — QUA-1, FRO-5, ARC-3.

Found independently by three reviewers in the DEP-33 review. The only test of
this function asserted that three substrings appear in its source, so inverting
the gate — right password 401s, no password is served — passed all 18 tests.
That is the whole of DEP-4: this function IS the site's access control, and the
2026-07-27 read of the deployed distribution confirmed it is the *sole* one (no
Lambda@Edge, no signed URLs, no signed cookies on either behaviour).

Two design choices carry most of the value here:

1. **The code is taken from the SYNTHESISED template, not read off disk.** The
   password is substituted into the function body at synth time
   (stack.py's `.replace("__EXPECTED_AUTH__", ...)`), and "that substitution
   silently no-ops" was one of the review's green mutations. Reading the source
   file would not exercise it; reading the template does.

2. **The expected credential is hardcoded, not recomputed from DeployInputs.**
   Deriving it the way stack.py derives it would move in lockstep with a
   mutation to stack.py and the test would stay green — the exact trap that
   makes a test vacuous.

The function is JavaScript and this suite is pytest, so the test runs it under
node. node is already a hard dependency of this package: CDK synthesises through
it, so a machine that cannot run this test cannot run any of the others either.
It therefore FAILS rather than skips when node is missing — a silent skip is the
vacuity this file exists to remove.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from tests.test_stack import template

# base64("artistpath:test-password") — DEPLOY.site_password in test_stack.py,
# with the username literal from stack.py. Hardcoded deliberately: see the
# module docstring.
VALID_AUTH = "Basic YXJ0aXN0cGF0aDp0ZXN0LXBhc3N3b3Jk"

# CloudFront Functions hand `handler` one event and use its return value either
# as the response (when it has a statusCode) or as the onward request.
_DRIVER = """
var event = JSON.parse(process.argv[2]);
process.stdout.write(JSON.stringify(handler(event)));
"""


def _request(uri: str, auth: str | None = None) -> dict:
    headers = {} if auth is None else {"authorization": {"value": auth}}
    return {"uri": uri, "headers": headers}


@pytest.fixture(scope="module")
def run_handler(tmp_path_factory):
    node = shutil.which("node")
    assert node, (
        "node is required to run the viewer function. It is already a hard "
        "dependency of this package — CDK synthesises through it — so this is "
        "a broken environment, not a reason to skip."
    )

    (function,) = template().find_resources("AWS::CloudFront::Function").values()
    code = function["Properties"]["FunctionCode"]
    assert isinstance(code, str), f"FunctionCode is not inline source: {type(code)}"
    assert "__EXPECTED_AUTH__" not in code, (
        "the synth-time credential substitution did not happen — the deployed "
        "function would compare against the literal placeholder"
    )

    script = tmp_path_factory.mktemp("viewer_function") / "driver.js"
    script.write_text(code + _DRIVER, encoding="utf-8")

    def _run(request: dict) -> dict:
        result = subprocess.run(
            [node, str(script), json.dumps({"request": request})],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    return _run


# --- the gate ---------------------------------------------------------------


def test_a_request_with_no_password_is_refused(run_handler):
    result = run_handler(_request("/"))
    assert result["statusCode"] == 401


def test_a_request_with_the_wrong_password_is_refused(run_handler):
    result = run_handler(_request("/", "Basic " + "d3Jvbmc="))
    assert result["statusCode"] == 401


def test_the_right_password_is_admitted(run_handler):
    # The half an inverted gate breaks that a "does it 401?" test cannot see.
    # Without this, a function that refuses everyone passes — and so does one
    # that admits everyone, given only the two tests above.
    result = run_handler(_request("/", VALID_AUTH))
    assert "statusCode" not in result, result
    assert result["uri"] == "/index.html"


def test_the_refusal_asks_the_browser_for_credentials(run_handler):
    # Without www-authenticate the browser shows a bare 401 body and never
    # prompts, so nobody can get in at all (adjacent to FRO-2).
    result = run_handler(_request("/", None))
    assert result["headers"]["www-authenticate"]["value"].startswith("Basic ")


# --- the SPA fallback (TR-5) ------------------------------------------------


def test_a_shared_journey_link_reaches_the_spa_entrypoint(run_handler):
    # TR-5, found independently by two reviewers. The default behaviour serves a
    # private bucket holding no object at /path/<mbid>/<mbid>, so without the
    # rewrite every shared link 403s — and CLAUDE.md gives shareable URLs as the
    # reason all path state lives in the URL.
    result = run_handler(
        _request(
            "/path/a74b1b7f-71a5-4011-9441-d0b5e4122711"
            "/8bfac288-ccc5-448d-9573-c33ea2aa5c30",
            VALID_AUTH,
        )
    )
    assert result["uri"] == "/index.html"


def test_an_api_call_is_not_rewritten(run_handler):
    # Rewriting /api/* would send every API call to index.html and the SPA would
    # parse HTML as JSON.
    result = run_handler(_request("/api/artists/search", VALID_AUTH))
    assert result["uri"] == "/api/artists/search"


def test_a_hashed_asset_is_not_rewritten(run_handler):
    # Anything with a file extension is a real object. Rewriting it serves
    # index.html as JavaScript, which is FRO-1's blank page by another route.
    result = run_handler(_request("/assets/index-abc123.js", VALID_AUTH))
    assert result["uri"] == "/assets/index-abc123.js"
