# Handoff — Track B complete and deployed, 2026-07-26 (night)

**Written at a clean seam.** Track B reached its planned boundary: the stack is deployed and
verified, and `DEP-33`'s review has been run. **Nothing is in flight** — no subagents
running, no background jobs, no half-written directories, no session-owned processes. Two
detached dev servers predating this work are still listening; see the bottom.

Committed and pushed. **PR #29** on `gate2-track-b-infra`.

**Supersedes [`2026-07-26-HANDOFF-track-d-complete.md`](2026-07-26-HANDOFF-track-d-complete.md)
on next actions only.** That handoff remains the record of Track D and **its "must not be
reverted" list is still live.**

---

## Your job: the ten blocking findings, then Track C

**Read, in order:**

1. [`findings/2026-07-26-track-b-cdk-review.md`](findings/2026-07-26-track-b-cdk-review.md)
   — **§2 is your work queue, already ordered.** This is the `DEP-33` review output.
2. [`2026-07-26-gate2-track-b-execution-log.md`](2026-07-26-gate2-track-b-execution-log.md)
   — `TKB-`. §1 is what is live, §4 is what must not be reverted, §6 is the environment traps.
3. [`plans/2026-07-26-track-b-infrastructure.md`](plans/2026-07-26-track-b-infrastructure.md)
   — the plan, with `TKB-1`…`TKB-8` stated in full.

**The owner's instruction, 2026-07-26: the ten blockers are the first work of the next
session.** They are not a menu — §2 ranks them by *what breaks and how silently*, and rank 1
(`QUA-2`) is first because it is the only failure that is invisible to the owner while being
open to the internet.

**Write a plan before executing.** Ten findings across four packages is past the point where
task-by-task improvisation holds, and several fixes interact — `ARC-5` closes half of
`ARC-4`; `QUA-1` and `FRO-5` and `ARC-3` are the same missing test.

---

## What is now true that was not

- **The app is deployed.** Identity, URLs and buckets are in the execution log's §1. **Do not
  restate them elsewhere.**
- **`TKA-11` is CLOSED** — the deployed `/health` matches the manifest sidecar on sha256,
  artist count and edge count, checked programmatically.
- **`TKA-12`/`DEP-32` is CLOSED** — both lockfiles are committed; `.gitignore:18` no longer
  ignores them. `infra/uv.lock` is committed too.
- **`TR-7` and `TR-8` are CLOSED**, verified live in both directions.
- **`DEP-33` is DISCHARGED** by the review above. It required the re-run *before cutover*;
  cutover is Track C and has not happened.
- **The site is not usable yet.** The SPA bucket is empty, so the site serves the API and a
  password prompt. That is Track C, not a defect.

## Claims that must NOT be reverted by a well-meaning editor

Additional to the Track A and Track D lists, which remain live.

1. **`ARTISTPATH_CORS_ORIGINS` is set to the empty string, not omitted** (`stack.py`).
   Omitting it yields `config.py`'s dev default `http://localhost:5173`, and same-origin
   means no preflight ever fires to reveal it (`TR-8`). Mutation-verified.
2. **The origin-secret middleware exempts `/health`** (`api/…/app.py`). App Runner's health
   checker reaches the origin directly and cannot be given the header; gating it fails every
   deploy. Mutation-verified.
3. **The distribution has no `errorResponses`** (`TKB-2`). It is distribution-level and would
   rewrite the API's own 404s and the origin-secret 403 into HTML with status 200.
4. **The `/api/*` behaviour pins `CACHING_DISABLED`** or C2 — closed 2026-07-25 and marked
   do-not-re-plan — returns as an apparent regression in closed work.
5. **`Authorization` is not in the origin-request allow-list.** CDK's own synth raises if you
   add it.
6. **The artifact bucket has no CloudFront origin and is `RETAIN`.**
7. **`hmac.compare_digest` is used deliberately** — `QUA-13` records that this is a
   permanent **review-only** invariant with no test behind it. Do not "simplify" it. (Fixing
   `SEC-1` changes it to compare **bytes**; that is the fix, not a simplification.)

## What I know that is not in the durable record

- **The review's four reports are not committed** — only the triage in
  `findings/2026-07-26-track-b-cdk-review.md`. That document is faithful to them, but the
  full reasoning for any individual finding is gone. If a finding looks wrong, re-derive it
  rather than assuming the summary dropped something.
- **`SEC-1` cannot be reproduced through `TestClient`** — httpx rejects the non-ASCII header
  client-side with `UnicodeEncodeError` before it reaches the app. It reproduces at the raw
  ASGI layer, which is what a real request goes through. A test for it must build the ASGI
  scope directly.
- **The `FRO-1` cache measurement was taken by uploading a probe object to the live SPA
  bucket and deleting it afterwards.** The bucket is empty again — verified. If you see a
  `cacheprobe.html` in any listing, something went wrong.
- **`aws s3 sync`'s content-type guessing was checked on this machine and is correct**
  (`.js → text/javascript`). That is machine state, not a repo property — re-check if the
  deploy ever moves machines, because a module script served as `text/plain` is refused and
  gives the same blank page as `FRO-1`.
- **The billing alarm has never fired and its failure mode is silence.** `treat_missing_data`
  is `NOT_BREACHING`. Someone should confirm it reports `OK` rather than `INSUFFICIENT_DATA`
  within ~12 hours of the deploy; the owner enabled billing alerts (P3) but that was not
  re-verified after.
- **The App Runner availability probe left two CloudWatch log groups behind**
  (`/aws/apprunner/apprunner-availability-probe/…`). Harmless, and the only trace of
  `TKB-8`'s measurement. Delete them or leave them; they cost effectively nothing.

## The open decision, and what I would do

**Whether to fix all ten blockers before Track C, or only the three that stand between the
owner and a working URL (`FRO-2`, `FRO-1`, `ARC-1`).** The owner chose **all ten first**.

**What I would do, and why it agrees:** ten green mutations means the suite currently
ratifies a broken stack. That is not a polish problem — it is the condition under which the
*next* change is dangerous, and Track C is the next change. Fixing the tests first means
Track C lands against a suite that can actually reject it.

**What is genuinely the owner's, and is still open:** whether `SEC-9` (no access logs, no
rate limiting) is acceptable for friends-and-family — deferred to Gate 2 → 3, and that
deferral rests on the audience staying small, which nothing enforces or detects.

## What was decided against

- **Fixing anything during the review.** The tree was left untouched so the findings describe
  what is actually deployed.
- **Switching off App Runner** despite the deprecation banner. `TKB-8`: measured that this
  account can still create services, CDK has no ECS Express Mode support, owner's decision to
  proceed and to consider **outside AWS** if it is fully deprecated.
- **Committing a `requirements.txt`** for dependency scanning (`TKB-3`/`TKB-5`) — the image
  scan is strictly better and needs no second manifest.
- **An Alpine base image** to clear `TKB-6`'s two highs. numpy on musl is a worse trade.

## Left running, deliberately — but stale

Two **detached** servers, owned by no session, left by the Track A/D sessions:

| what | address | PID |
|---|---|---|
| frontend | http://localhost:5173 | 211432 |
| api | http://127.0.0.1:8000 | 231092 |

**They started at 18:51 and HEAD is 21:53, so they predate this work** — the API on :8000
does **not** have the origin-secret middleware. That is fine for local use and wrong for any
manual test of Track B. **Nothing will stop them but those PIDs.** No queue entry depends on
them: the queued item for this work needs no local server.
