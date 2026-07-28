"""Behavioural tests for the CloudFront viewer function — QUA-1, FRO-5, ARC-3.

Found independently by three reviewers in the DEP-33 review. The only test of
this function asserted that three substrings appear in its source, so inverting
the gate — right password 401s, no password is served — passed all 18 tests.
That is the whole of DEP-4: this function IS the site's access control, and the
2026-07-27 read of the deployed distribution confirmed it is the *sole* one (no
Lambda@Edge, no signed URLs, no signed cookies on either behaviour).

**PW-7 replaced the shared password with a front-door check.** The gate was not
deleted — it asks a different question. It now refuses anything that did not
arrive through Cloudflare, because the generated CloudFront address answers on
its own name and never touches Cloudflare's rate limit, which would make PW-6
decorative. That is TR-7's defect one layer up (stack.py:147-153), and this
project has already shipped it once.

Two design choices carry most of the value here:

1. **The code is taken from the SYNTHESISED template, not read off disk.** The
   secret is substituted into the function body at synth time
   (stack.py's `.replace("__FRONT_DOOR_SECRET__", ...)`), and "that substitution
   silently no-ops" was one of the review's green mutations. Reading the source
   file would not exercise it; reading the template does.

2. **The expected secret is hardcoded, not recomputed from DeployInputs.**
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

# The Cloudflare-injected value from test_stack.py's DEPLOY fixture. Hardcoded
# rather than recomputed from DeployInputs, for the reason in the module
# docstring: a value derived the way stack.py derives it moves in lockstep with
# a mutation to stack.py and the test stays green.
SECRET = "test-front-door-secret"
HOSTNAME = "artistpath.test.invalid"

# CloudFront Functions hand `handler` one event and use its return value either
# as the response (when it has a statusCode) or as the onward request.
_DRIVER = """
var event = JSON.parse(process.argv[2]);
process.stdout.write(JSON.stringify(handler(event)));
"""


def _request(
    uri: str,
    secret: str | None = None,
    host: str | None = None,
    querystring: dict | None = None,
) -> dict:
    headers = {}
    if secret is not None:
        headers["x-front-door"] = {"value": secret}
    headers["host"] = {"value": host or HOSTNAME}
    return {"uri": uri, "headers": headers, "querystring": querystring or {}}


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
    assert "__FRONT_DOOR_SECRET__" not in code, (
        "the synth-time secret substitution did not happen — the deployed "
        "function would compare against the literal placeholder"
    )
    assert "__SITE_HOSTNAME__" not in code, (
        "the hostname substitution did not happen — the deployed function would "
        "redirect every shared link to the literal placeholder"
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


def test_a_request_that_did_not_come_through_cloudflare_is_refused(run_handler):
    # The bypass this task exists to close: the generated CloudFront address
    # answers on its own and never touches Cloudflare's rate limit, and that
    # address is already in circulation.
    result = run_handler(_request("/", secret=None))
    assert "statusCode" in result and result["statusCode"] in (301, 403)


def test_a_request_with_the_wrong_secret_is_refused(run_handler):
    result = run_handler(_request("/", secret="wrong"))
    assert "statusCode" in result and result["statusCode"] in (301, 403)


def test_a_request_through_cloudflare_is_admitted(run_handler):
    # The half a "does it refuse?" test cannot see. Without this, a function
    # that refuses everyone passes, and so does one that admits everyone.
    result = run_handler(_request("/", secret=SECRET))
    assert "statusCode" not in result, result
    assert result["uri"] == "/index.html"


def test_the_old_cloudfront_address_redirects_rather_than_refusing(run_handler):
    # Every link shared before this change points at the generated address.
    # A 403 would break all of them; a redirect pulls them through Cloudflare
    # instead, which is also what puts them under the rate limit.
    result = run_handler(
        _request("/path/abc/def", secret=None, host="d2n3xqz3pttguf.cloudfront.net")
    )
    assert result["statusCode"] == 301
    assert result["headers"]["location"]["value"] == (
        "https://" + HOSTNAME + "/path/abc/def"
    )


def test_the_redirect_preserves_the_query_string(run_handler):
    # Bypass state lives in the query string (/path/:from/:to?dislike=…&known=…),
    # so dropping it silently changes the journey the recipient sees — G3-F3's
    # shape, arriving by a different route.
    result = run_handler(
        _request(
            "/path/abc/def",
            secret=None,
            host="d2n3xqz3pttguf.cloudfront.net",
            querystring={"dislike": {"value": "xyz"}, "known": {"value": "pqr"}},
        )
    )
    location = result["headers"]["location"]["value"]
    assert "dislike=xyz" in location and "known=pqr" in location


def test_arriving_at_the_right_host_without_the_secret_does_not_loop(run_handler):
    # If the Transform Rule is ever removed, redirecting to the host we are
    # already on is an infinite redirect. Fail closed instead — a broken site
    # is recoverable, a redirect loop looks like a broken site AND hides why.
    result = run_handler(_request("/", secret=None, host=HOSTNAME))
    assert result["statusCode"] == 403


def test_the_refusal_does_not_disclose_the_secret(run_handler):
    # Same class as the password disclosure this replaces: the cheapest way to
    # write a helpful refusal is to name the thing that was missing.
    response = json.dumps(run_handler(_request("/", secret=None, host=HOSTNAME)))
    assert SECRET not in response


def test_the_refusal_body_is_served_as_html(run_handler):
    # Without a content-type the browser renders the markup as plain text and
    # the message arrives as visible tags.
    result = run_handler(_request("/", secret=None, host=HOSTNAME))
    assert result["headers"]["content-type"]["value"].startswith("text/html")


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
            secret=SECRET,
        )
    )
    assert result["uri"] == "/index.html"


def test_an_api_call_is_not_rewritten(run_handler):
    # Rewriting /api/* would send every API call to index.html and the SPA would
    # parse HTML as JSON.
    result = run_handler(_request("/api/artists/search", secret=SECRET))
    assert result["uri"] == "/api/artists/search"


def test_a_hashed_asset_is_not_rewritten(run_handler):
    # Anything with a file extension is a real object. Rewriting it serves
    # index.html as JavaScript, which is FRO-1's blank page by another route.
    result = run_handler(_request("/assets/index-abc123.js", secret=SECRET))
    assert result["uri"] == "/assets/index-abc123.js"
