"""Which resources a deploy builds, and the guard on the destructive answer.

`ARC-1`. `cdk deploy -c stage=storage` builds only the pieces the first image
push and artifact upload need. Against a **deployed** stack it does the opposite
of what its name suggests: it synthesises a template without the App Runner
service or the CloudFront distribution, and CloudFormation deletes every resource
that is no longer in it — **including the distribution**.

The review measured that set at eight. It is **nine** as of 2026-07-27, because
`RMD-10` added an autoscaling configuration to the service half. The count is not
restated anywhere it can rot: `test_deploy_stage.py` derives it from the two
synthesised templates and names the members, so adding a service-side resource
updates the check instead of silently invalidating a comment.

**A deleted CloudFront distribution does not come back with the same domain**,
so every link ever shared dies permanently. `CLAUDE.md` gives shareable URLs as
the reason all path state lives in the URL, so this is not a recoverable
inconvenience.

Until 2026-07-27 the only guard was a sentence in `infra/README.md`
(*"Subsequent deploys skip this section"*) — and §2 is the first deploy command
an operator meets, so the destructive path was also the most reachable one.

This lives in its own module, separate from `app.py`, for one reason: `app.py`
does its work at import time and calls `app.synth()`, so nothing in it can be
tested. `QUA-10` records that `app.py` has no test at all, which meant `TKB-7`'s
protection rode on an unverified context string. This function is pure — two
strings in, one bool out — so the branch that matters is testable without CDK,
without AWS, and without synthesising anything.
"""

from __future__ import annotations

STORAGE_STAGE = "storage"
CONFIRM_FLAG = "confirm-new-stack"

_REFUSAL = f"""\
Refusing to synthesise the storage-only stage.

`-c stage={STORAGE_STAGE}` omits the App Runner service and the CloudFront
distribution. That is correct for the FIRST deploy of a stack that does not
exist yet (TKB-7): App Runner cannot be created before its image is in ECR and
its graph is in S3.

Against an ALREADY DEPLOYED stack it deletes eight resources, including the
CloudFront distribution. A distribution does not come back with the same domain,
so every link anyone has ever been sent would break permanently, and no rollback
restores it.

If ArtistpathStack genuinely does not exist yet, say so explicitly:

    cdk deploy -c stage={STORAGE_STAGE} -c {CONFIRM_FLAG}=true

Check first, and do not guess:

    aws cloudformation describe-stacks --stack-name ArtistpathStack
"""


def resolve_include_service(stage: str | None, confirm_new_stack: str | None) -> bool:
    """Return whether this synth includes the service and the distribution.

    Raises SystemExit for the storage stage unless the operator has explicitly
    confirmed the stack is new. The guard is a second flag rather than an AWS
    lookup on purpose: synth must stay offline — the whole infra suite runs with
    no credentials — and a check that only works when configured is not a guard.
    """
    if stage != STORAGE_STAGE:
        return True
    if (confirm_new_stack or "").lower() != "true":
        raise SystemExit(_REFUSAL)
    return False
