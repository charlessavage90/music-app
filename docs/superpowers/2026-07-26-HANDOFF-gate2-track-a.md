# Handoff — Gate 2 design, team review, and the Track A plan, 2026-07-26

**Written at a clean seam. Nothing is in flight** — no subagents running, no background
jobs, no half-written directories, no processes owned, no servers left listening. Committed
and pushed; PR #27 on branch `gate2-deploy-and-telemetry`. Aimed at a session that has never
seen this work.

**Your job, if you are the next session: coordinate Track A implementation.** Read, in this
order:

1. [`plans/2026-07-26-track-a-api-hardening-and-telemetry.md`](plans/2026-07-26-track-a-api-hardening-and-telemetry.md) — **the plan you execute.** Ten tasks, complete code, exact expected test counts.
2. [`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](specs/2026-07-26-gate2-deploy-and-telemetry-design.md) — the design. **Read §12 (amendments) FIRST**; several original claims are struck and corrected in place.
3. [`findings/2026-07-26-gate1-gate2-team-review.md`](findings/2026-07-26-gate1-gate2-team-review.md) — the review that produced those corrections.

**Where they disagree, the design governs the plan, and §12 governs the rest of the design.**

> **⚠ SUPERSEDED ON STATUS, 2026-07-26 (later the same day) — ~~"No code has been
> written. Today produced documents only."~~** That was true when written and is now
> false: **Track A was executed in full** — ten tasks, api 153 → 180, PR #27. This
> handoff remains the record of the design and review work, and its "must not be
> reverted" list below is **still live**. For Track A's outcome read
> [`2026-07-26-gate2-track-a-execution-log.md`](2026-07-26-gate2-track-a-execution-log.md);
> the next unbuilt unit is **Track D**, which has a scope fence but **no plan yet**.

## What is now true that was not

- **Gate 2 has a governing design**, owner-approved: App Runner + S3 + CloudFront +
  DynamoDB in `us-east-1`, telemetry as structured JSON to CloudWatch, a shared-password
  CloudFront Function, CloudFront's default domain, **no CI** (the roadmap's own open
  judgment call 2, taken deliberately).
- **The Gate 1 → 2 team review has been run** — four reviewers, before any implementation
  plan existed. It found seven blocking gaps in the design and corrected the design's own
  flagship defect claim.
- **There are four tracks, not three**, and the order is **A → D → B → C**. Both AWS-free
  code tracks land before infrastructure, so the deploy ships an already-fixed app.

## The single most important thing to carry forward

**`TR-1`/`TR-2`: the design's flagship defect was misdiagnosed, and its prescribed test could
not fail.** `DEP-10` claimed a truncated artifact loads silently. It does not — the metadata
JSON blob is the **last** section of the APG1 layout, so tail truncation destroys the JSON
and `json.loads` raises first. The §9 verification instruction then said "assert that a short
artifact raises" — **which passes today, against unmodified source**, because
`JSONDecodeError` subclasses `ValueError`.

**This is the `FMS-P1` pattern recurring: a verification step that cannot fail.** Both are
corrected, and the plan's Task 1 carries an explicit warning about matching on the *message*
rather than the exception type. **Do not let a task report "test fails" without checking it
fails for the right reason** — that is now a standing instruction in the plan's Global
Constraints, and it is there because this session got it wrong.

The genuinely silent case is `TR-3`: a header whose `N` disagrees with the metadata length
loads clean, leaving `pop_raw` and `degree_hub_penalty` at different lengths, both indexed by
node id. Task 1 guards it.

## Claims that must NOT be reverted by a well-meaning editor

1. **`DEP-8`'s struck text stays struck, and visible.** Two false claims — that App Runner is
   unreachable except through CloudFront, and that `cors_origins` "goes unset" — are marked
   in place rather than deleted. A tidy-minded reader will want to clean that up. **Leave
   it:** two other decisions were justified by the first claim, and the record of what was
   believed is what stops it being re-believed.
2. **`DEP-10`'s corrected version is the corrected one.** The struck original reads more
   confidently and is wrong. Verified by experiment three times.
3. **Telemetry logs facts, not computed metrics (`DEP-7`).** Someone will suggest computing
   `PathMetrics` inline since `evaluation.py` already exists. Three reasons not to, in §5 —
   the strongest being that choosing production's metric is a **scoring decision taken during
   the scoring pause.**
4. **`exclude` bounding belongs in §4's defect table, not under "abuse handling."** This
   session filed it wrongly first; the re-filing is deliberate and the reasoning is `TR-12`.
5. **Track A is AWS-free and that is a property, not a convenience (`DEP-18`).** If anything
   in Task 1–9 starts needing AWS credentials, the injectable seam has been bypassed and the
   task is wrong.

## What I know that is not in the durable record

- **`.gitignore` already carries `cdk.out/`** at line 8, from before this work. Track B does
  not need to add it.
- **The API test suite's `_client()` helper** (`api/tests/test_app.py:13`) builds a
  three-artist graph — Radiohead, Muse, Coldplay — and returns `(client, store)`. Every new
  API test in the plan uses it. `make_store` is in `tests/conftest.py:11`.
- **`asyncio_mode = "auto"`** is set in `api/pyproject.toml:28`, so async tests need no
  decorator. This matters for Tasks 3, 4 and 7.
- **Running the four suites takes about 20 seconds total.** There is no reason to skip the
  full-suite gate between tasks.
- **The adopted artifact's identity is owned by**
  `findings/2026-07-23-tiebreak-fix-adoption.md`, and the manifest sidecar
  `builder/scratch/graph-t15-tiebreakfix.bin.json` carries the same values machine-written.
  **Read from one of those; do not transcribe a sha256 by hand** — that is `DEP-24`, and its
  failure signature is a service that refuses to boot during a cutover.
- **Snyk Code returned 0 issues on `api/`** during the review. The SCA scan did **not** run —
  it needs a folder-trust write the reviewer declined to make under a read-only brief. Worth
  running once Track A modifies code, per the global instruction.

## What was decided against

- **Subagent-driven execution for Track A.** The tasks are strictly sequential and eight of
  ten edit the same two files, so fan-out serialises anyway while paying cold context
  re-derivation ten times. The plan header carries the full reasoning and names the
  condition under which the other choice is right — **Track D is that condition.**
- **Computing metrics in the telemetry event** — see claim 3 above.
- **aioboto3.** `asyncio.to_thread` fixes the blocking cache with no new dependency.
- **Accessibility work in Gate 2** — owner's call, on his knowledge that no one in the group
  uses a screen reader. Recorded with its findings, not dropped.
- **Link previews (Open Graph) in Track D** — considered and excluded when the fence was
  drawn. Recorded as Gate-3.
- **Growing the standing context layer.** Nothing was added to `CLAUDE.md` or `memory/`;
  `closeout` **D6** delta is **net zero**.

## Owed but not done

**A full `closeout` was not run** — the owner ended the session at the plan. What a closeout
would still add: the deferral sweep with success conditions (most already carry them, in the
design's §10 and the review's §6), the orphaned-module check, and the git finalisation
(already done — branch pushed, PR #27 updated). **The test-queue entry and the doc-map rows
were written**, since a cold session consumes both.
