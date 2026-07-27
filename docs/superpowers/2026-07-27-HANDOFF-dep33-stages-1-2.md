# Handoff — `DEP-33` remediation, stages 1–2 complete, 2026-07-27

**Written at a planned seam.** The plan named this boundary before any work started
([`plans/2026-07-27-dep33-blocker-remediation.md`](plans/2026-07-27-dep33-blocker-remediation.md)
§3), and stage 2 reached it. **Nothing is in flight** — no subagents running, no background
jobs, no half-written directories, no session-owned processes, **no listeners on `:8000` or
`:5173`** (swept, not assumed — nothing was ever started).

Committed and pushed. **PR #30** on `gate2-dep33-blockers`.

**Supersedes [`2026-07-26-HANDOFF-track-b-complete.md`](2026-07-26-HANDOFF-track-b-complete.md)
on next actions only.** That handoff remains the record of Track B, and **six of its seven
must-not-revert claims still stand** — see below for the one that does not.

---

## Your job: stage 3, then Track C

**Read, in order:**

1. [`plans/2026-07-27-dep33-blocker-remediation.md`](plans/2026-07-27-dep33-blocker-remediation.md)
   — stage 3 is `RMD-11`…`RMD-13`, stated in full. §2's pre-flight table is still accurate.
2. [`2026-07-27-dep33-remediation-execution-log.md`](2026-07-27-dep33-remediation-execution-log.md)
   — §0 for the AWS measurements, the closeout's `A3` table for every open item's condition.
3. [`findings/2026-07-26-track-b-cdk-review.md`](findings/2026-07-26-track-b-cdk-review.md)
   §2 — the original queue, **now annotated** for what is already done.

Stage 3 is the three findings that hit the first real person to open the site: **nobody is
told the username** (`FRO-2`), **a returning visitor gets a blank page after any redeploy**
(`FRO-1`), and **no step anywhere proves the gate admits rather than only rejects**
(`FRO-4`). The last cannot finish before Track C — the SPA bucket is empty, so every path
403s whether the rewrite works or not.

## What is now true that was not

- **Stages 1 and 2 are done**: `RMD-0`…`RMD-10`, plus `ARC-6` which was not on the plan.
- **The suite can reject a broken stack.** 16 mutations, 0 missed — 12 the review recorded as
  green, and 4 it recorded as caught, re-run as controls. Before this, ten went green.
- **`ARC-2` is closed in the world**: 90-day retention is set on both live API log groups.
- **`ARC-1` is a mechanism, not a sentence**: `-c stage=storage` refuses without
  `-c confirm-new-stack=true`.
- **`SEC-1`, `QUA-1`, `QUA-2`, `QUA-3`, `QUA-6`–`QUA-9`, `ARC-5`, `SEC-5` are closed.**
- **The queue was nine blockers, not ten.** `QUA-4` and `ARC-9`/`QUA-5` were already fixed in
  `6f49ab9`. Annotated in the findings document so nobody starts finished work.

## ⚠ The one claim that was REVERSED — do not restore the old mechanism

**Track B's must-not-revert #1** said: *set `ARTISTPATH_CORS_ORIGINS` to the empty string,
never omit it; a test holds it and goes red when the line is deleted.*

**Every sentence of that is true, and production did not match it.** An empty-valued
environment variable does not reach a running App Runner service. Measured two ways — drift
detection reported it `REMOVE`'d, and a live probe of the origin's `/health` returned
`access-control-allow-origin: http://localhost:5173`, with a made-up origin correctly getting
nothing back.

**The guarantee moved to `ApiConfig.cors_origins`, which now defaults to empty**, so *absence*
is the safe state. `stack.py` still sets the empty value and `test_stack.py` still asserts it —
**keep both**; they are now intent rather than the guarantee, and their comments say so.

**The other six must-not-revert claims stand unchanged.**

## ⚠ Fixed in source, STILL LIVE in production

**`RMD-6` is not closed.** Nothing in either stage was deployed. The running service is on the
image tag recorded in Track B's log §1, built before the `config.py` change, so **the deployed
API still serves the dev CORS default** — re-measured at closeout, not assumed. Stack drift
still reports the same three differences for the same reason.

**Exposure is small and should be described as small:** everything except `/health` requires
the origin-secret header that only CloudFront adds. `/health` discloses artifact identity,
already logged as `SEC-6`.

**It closes on the next deploy** — Track C's step, and the owner's call.

## Read this before you deploy

**The deploy will now stop unless `ARTISTPATH_DEPLOY_IMAGE_TAG` is set** (`ARC-6`). It
defaulted to `latest` and `infra/.env.deploy` does not set it, so the next `cdk deploy` would
have silently repointed the live service at a floating tag. Found by the stage-2 `cdk diff`
gate, not by reading. `infra/README.md` §1 documents it.

**`cdk diff` currently shows exactly three intended changes**: the autoscaling configuration,
its ARN on the service, and `ARTISTPATH_CLIP_TABLE`. Anything else is new and worth stopping
for.

## What I know that is not in the durable record

- **`.claude/worktrees/` is untracked in the tree and is not mine.** The owner said mid-session
  that another session is working in a worktree. I left it alone and committed with explicit
  pathspecs throughout. Do not sweep it into a commit.
- **The `cdk diff` and drift commands need `infra/.env.deploy`** (gitignored, `ARC-11`) sourced
  first, plus `ARTISTPATH_DEPLOY_IMAGE_TAG` set explicitly now. `.env.deploy` deliberately does
  **not** carry the tag — it is per-deploy, not per-machine.
- **Drift detection reports `Cpu` and `Memory` as drifted on every run and they are not
  drift** — App Runner normalises `1 vCPU`/`2 GB` to `1024`/`2048`. A third difference is real.
  This is in the runbook, but it will look alarming the first time.
- **The mutation harness lives in the scratchpad, not the repo.** It applies one mutation, runs
  that package's suite, and restores in a `finally`. Re-deriving it took ten minutes; if stage 3
  adds invariants, it is worth rewriting rather than doing them by hand.
- **`test_viewer_function.py` shells out to `node`.** If it ever fails in a strange way, check
  `node` is on `PATH` before reading the test.
- **Review §1's arithmetic does not reconcile** — nineteen mutations claimed, seventeen
  accounted for, and its "ten undetected" is twelve once the `×3` middleware row is expanded.
  **Two mutations are recorded nowhere and cannot be re-run.** I did not invent a number for
  them.

## The open decision, and what I would do

**Whether to deploy now or at Track C.** Deploying closes `RMD-6` and clears the drift; not
deploying leaves a small live exposure and a stack whose template no longer matches it.

**What I would do:** wait for Track C. The exposure is `/health` only, Track C has to deploy
anyway, and deploying twice doubles the chance of meeting `ARC-6`'s new refusal or `FRO-1`'s
cache problem in an unplanned order. **But it is genuinely the owner's**, because it trades a
live exposure against sequencing, and the exposure is his risk to accept.

## What was decided against

- **Fixing `ARC-4` properly.** Dropping the fixed physical names is a migration against a live
  table and repository, not a cleanup. Runbook §10 makes the failure recoverable instead, and
  names the real fix. `RMD-10` added a fourth fixed name (the autoscaling config), which is
  listed there.
- **Deploying anything in stage 2.** The plan's gate was `cdk diff`, not `cdk deploy`.
- **Fixing the two pre-existing Snyk lows.** Neither is in code this work introduced; both have
  closing conditions in the execution log's `A3` table.
- **Measuring `QUA-2`'s last inferential step** — that CloudFront with no viewer-request
  function serves the origin. It would mean detaching the gate on the live distribution. **Do
  not do this.**
