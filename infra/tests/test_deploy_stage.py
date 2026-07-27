"""ARC-1 / QUA-10 — the guard on the destructive deploy stage.

`cdk deploy -c stage=storage` against a deployed stack deletes eight resources
including the CloudFront distribution, and a distribution does not return with
the same domain. Until 2026-07-27 the only guard was a sentence in the runbook,
and QUA-10 records that `infra/app.py` had no test at all — so TKB-7's
protection rode on an unverified context string.

These tests exist because the storage stage is *correct exactly once* (the first
deploy) and destructive every other time, which is the worst shape a flag can
have.
"""

from __future__ import annotations

import pytest

from artistpath_infra.deploy_stage import (
    CONFIRM_FLAG,
    STORAGE_STAGE,
    resolve_include_service,
)


def test_an_ordinary_deploy_builds_everything():
    assert resolve_include_service(None, None) is True


def test_an_unrecognised_stage_builds_everything_rather_than_less():
    # Fail toward the SAFE answer: a typo'd stage must not silently drop the
    # distribution. Only the exact storage token is destructive.
    assert resolve_include_service("storag", None) is True
    assert resolve_include_service("Storage", None) is True


def test_the_storage_stage_is_refused_without_explicit_confirmation():
    # The whole of ARC-1. This is the command an operator meets first in the
    # runbook, so the unconfirmed path must not be the working one.
    with pytest.raises(SystemExit) as refused:
        resolve_include_service(STORAGE_STAGE, None)
    message = str(refused.value)
    # The refusal has to say what would break, or it is just an obstacle to
    # route around with whatever flag makes it stop complaining.
    assert "CloudFront distribution" in message
    assert CONFIRM_FLAG in message


def test_the_storage_stage_is_allowed_when_the_stack_is_confirmed_new():
    # The admitting half: without it, a guard that refuses unconditionally
    # passes the test above and the first deploy becomes impossible.
    assert resolve_include_service(STORAGE_STAGE, "true") is False


def test_confirmation_must_be_the_word_true_not_merely_present():
    # `-c confirm-new-stack` with no value yields the string "True" from CDK in
    # some paths and an empty string in others; anything that is not an explicit
    # affirmative must refuse.
    assert resolve_include_service(STORAGE_STAGE, "TRUE") is False
    for not_confirmed in ["", "false", "yes", "1", None]:
        with pytest.raises(SystemExit):
            resolve_include_service(STORAGE_STAGE, not_confirmed)
