"""`FRO-1` — the publish order that stops a returning visitor meeting a blank page.

Stage 3 fixed the *runbook*: `infra/README.md` §6 became three ordered passes
instead of one `aws s3 sync --delete`. Every other stage 3 fix is held by a test.
§6 was not — it was three commands a person types at the end of a deploy, and the
failure it prevents is invisible to whoever runs it, because you never see the
blank page yourself. Only somebody who visited *before* the change does.

That is the worst shape an operational rule can have: unenforced, and its
violation unobservable from where the violation happens. These tests are what
replaces "the operator read the section carefully".

The invariants below are not stylistic. Each one, inverted, is the live defect:
collapse the passes and a mid-visit browser asks for a hashed asset that
`--delete` has just removed; publish `index.html` first and it names assets that
are not there yet; cache `index.html` and the fix does not stick for the visit
after this one.
"""

from __future__ import annotations

import pytest

from artistpath_infra.sync_frontend import (
    ASSET_CACHE_CONTROL,
    INDEX,
    INDEX_CACHE_CONTROL,
    check_asset_content_type,
    check_build_output,
    pick_probe_asset,
    plan_upload,
    resolve_aws,
)

BUCKET = "artistpath-spa-example"
DISTRIBUTION = "E1EXAMPLE"


def plan(**kwargs):
    return plan_upload(dist="dist", bucket=BUCKET, distribution_id=DISTRIBUTION, **kwargs)


def joined(command):
    return " ".join(command)


def index_step(commands):
    # Matched on the verb, not on the filename: the asset pass names index.html
    # too, in its --exclude, so a substring match finds the wrong command and
    # the ordering assertion below passes for the wrong reason.
    return next(i for i, c in enumerate(commands) if "cp" in c)


def asset_step(commands):
    return next(i for i, c in enumerate(commands) if "sync" in c)


def test_the_assets_go_up_before_the_index_that_names_them():
    # index.html is the only object naming the hashed bundles, so it is the
    # switch that makes a build live. Thrown first, it points at objects that do
    # not exist yet and the site is broken for exactly as long as pass 1 takes.
    commands = plan()
    assert asset_step(commands) < index_step(commands)


def test_the_asset_pass_never_deletes_by_default():
    # The whole of FRO-1. Deleting old assets while the old index.html is still
    # live is what strands a mid-visit browser.
    commands = plan()
    assert "--delete" not in joined(commands[asset_step(commands)])


def test_index_html_is_kept_out_of_the_asset_pass():
    # Without the exclusion, pass 1 uploads index.html with a year-long
    # immutable cache — which is FRO-1 made permanent rather than fixed.
    commands = plan()
    assert "--exclude" in commands[asset_step(commands)]
    assert INDEX in commands[asset_step(commands)]


def test_the_assets_are_cached_for_a_year_and_the_index_is_never_cached():
    # The pairing is the point: the immutable year on hashed assets is what
    # makes an uncached index.html cheap, and an uncached index.html is what
    # stops a browser holding a stale one for a duration nobody chose.
    commands = plan()
    assert ASSET_CACHE_CONTROL in commands[asset_step(commands)]
    assert INDEX_CACHE_CONTROL in commands[index_step(commands)]
    assert "immutable" in ASSET_CACHE_CONTROL
    assert "no-cache" in INDEX_CACHE_CONTROL


def test_the_invalidation_is_the_last_thing_that_happens():
    commands = plan()
    assert "cloudfront" in joined(commands[-1])
    assert DISTRIBUTION in joined(commands[-1])


def test_pruning_is_available_but_must_be_asked_for():
    # The prune is legitimate later, once nobody is still holding the previous
    # index.html. It must never be reachable by accident.
    commands = plan(prune=True)
    assert "--delete" in joined(commands[asset_step(commands)])


def test_the_index_is_never_pruned_even_when_pruning():
    # `--delete` with index.html in scope would delete the live index.html
    # between the two passes, taking the site down rather than merely stranding
    # someone mid-visit.
    commands = plan(prune=True)
    assert "--exclude" in commands[asset_step(commands)]
    assert INDEX in commands[asset_step(commands)]


def test_a_build_with_no_index_is_refused():
    # An empty or half-written dist/ would otherwise upload nothing, invalidate
    # cheerfully, and report success.
    with pytest.raises(SystemExit) as refused:
        check_build_output(["assets/index-abc123.js"])
    assert INDEX in str(refused.value)


def test_a_build_with_no_hashed_assets_is_refused():
    with pytest.raises(SystemExit):
        check_build_output([INDEX])


def test_a_complete_build_is_accepted():
    # The admitting half: a guard that refuses everything passes both tests
    # above and makes the deploy impossible.
    check_build_output([INDEX, "assets/index-abc123.js", "assets/index-def456.css"])


def test_a_script_served_as_the_wrong_type_is_refused():
    # The machine-state caveat in §6, promoted to a check. `aws s3 sync` guesses
    # Content-Type from the extension, and a module script served as text/plain
    # is refused by the browser — giving the SAME blank page as FRO-1 from a
    # completely different cause. It was verified by hand on one machine on one
    # day; nothing re-checks it when the deploy moves.
    with pytest.raises(SystemExit) as refused:
        check_asset_content_type("assets/index-abc123.js", "text/plain")
    assert "text/plain" in str(refused.value)


def test_a_missing_content_type_is_refused_rather_than_assumed():
    with pytest.raises(SystemExit):
        check_asset_content_type("assets/index-abc123.js", None)


def test_the_aws_cli_on_the_path_is_preferred():
    assert resolve_aws("C:/Program Files/Amazon/AWSCLIV2/aws.exe", []) \
        == "C:/Program Files/Amazon/AWSCLIV2/aws.exe"


def test_a_stale_shell_falls_back_to_the_installed_location():
    # The documented trap: the AWS CLI is on the MACHINE path but a shell
    # started before it was installed does not have it, so `aws` is not found
    # while `aws --version` works perfectly in a new window. Observed again on
    # 2026-07-27. Without this the deploy dies on FileNotFoundError partway
    # through, which reads like a broken script rather than a stale environment.
    assert resolve_aws(None, ["C:/Program Files/Amazon/AWSCLIV2/aws.exe"]) \
        == "C:/Program Files/Amazon/AWSCLIV2/aws.exe"


def test_a_genuinely_missing_aws_cli_says_what_to_do():
    with pytest.raises(SystemExit) as refused:
        resolve_aws(None, [])
    # It must distinguish the two causes, because they have different fixes:
    # reopen the shell, or install the thing.
    assert "PATH" in str(refused.value)


def test_the_probed_asset_is_a_script_and_not_the_index():
    # index.html is served with its own Content-Type and is uploaded by a
    # different command, so probing it would check the one object the caveat
    # does not apply to and report the deploy safe.
    probed = pick_probe_asset([INDEX, "assets/style-abc123.css", "assets/main-def456.js"])
    assert probed == "assets/main-def456.js"


def test_the_content_types_a_browser_will_execute_are_accepted():
    for served in [
        "text/javascript",
        "application/javascript",
        "text/javascript; charset=utf-8",
    ]:
        check_asset_content_type("assets/index-abc123.js", served)
