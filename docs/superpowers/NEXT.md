# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-27, after `DEP-33` blocker remediation stage 3.**

---

## Next

**Track C — sync the SPA to the bucket.** PR #32 on `gate2-dep33-stage3` is open and carries
stage 3.

**The `DEP-33` blockers are discharged.** All three stages are done (`RMD-0`…`RMD-13`), each
retired at a planned seam. Read in this order:

1. [`2026-07-27-HANDOFF-dep33-stage3.md`](2026-07-27-HANDOFF-dep33-stage3.md) — the current
   handoff. What changed about the deploy procedure, what must not be reverted, what is still
   live, and the one open decision.
2. [`2026-07-27-dep33-remediation-execution-log.md`](2026-07-27-dep33-remediation-execution-log.md)
   — per-task reasoning and the mutation results. Stages 1–2 are PR #30, stage 3 is PR #32.
3. **`infra/README.md` §6 and §8a — read, do not remember.** §6 changed under stage 3: the
   frontend sync is now **three ordered passes**, and the old single `aws s3 sync --delete` is
   itself the defect (`FRO-1`). §8a is the cutover's first step.

**Track C makes the site usable.** The bucket is empty, so the site today serves a password
prompt and then an error. That is expected, not a defect. Track C also closes `RMD-6`, the
stack drift it causes, and `RMD-13`'s browser half — the three things that all point at the
same deploy.

> **⚠ One defect is fixed in source and STILL LIVE in production.** `RMD-6`: the deployed API
> serves `config.py`'s old dev CORS default, because an empty-valued environment variable
> never reaches App Runner. **The owner accepted this exposure on 2026-07-27** rather than
> deploy twice — that decision is settled, do not re-table it. Exposure is `/health` only.
>
> **The deploy will refuse unless `ARTISTPATH_DEPLOY_IMAGE_TAG` is set** (`ARC-6`). Deliberate,
> and a change to the deploy procedure; `infra/README.md` §1 has it.

**One open decision, and it is the owner's:** whether to turn `infra/README.md` §6 into a
script before running Track C. Every other stage 3 fix is held by a test; §6 is three ordered
commands a person types, and the failure it prevents is invisible to whoever runs it. The
retiring session's position and reasoning are in the handoff.

---

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** `F1`, its last item, closed 2026-07-26. One live exception below (`BYP-13`). |
| **Gate 2 — friends & family** | **In progress.** Tracks A, D and B are DONE; the API is **deployed on AWS** (PR #29). `DEP-33` blocker remediation is **fully discharged** — stages 1–2 (PR #30), stage 3 (PR #32). **Track C is all that remains.** |
| **Gate 3 — public** | Not started. |

A team review is scheduled at each gate boundary after a period of real use — staff the
frontend explicitly. See `CLAUDE.md`, "When to recommend a review".

## Closed — do not re-plan or re-investigate

- **The Gate 1 clip work**, 2026-07-25 (PR #19, then PR #20). Both defects — *plays the
  wrong artist* and *clips die after a while*, filed as `C1`/`C2` in the roadmap and **not**
  the Track 2 success criteria of the same names — plus all four frontend UX items, all
  **confirmed in use**. Record:
  [`2026-07-25-gate1-clips-and-ux-execution-log.md`](2026-07-25-gate1-clips-and-ux-execution-log.md)
  §15–§19.
  - ⚠ **One exception, and it is live.** `BYP-13` in
    [`findings/2026-07-25-bypass-depth-use-run.md`](findings/2026-07-25-bypass-depth-use-run.md)
    records a card that played a clip by a *different artist of the same name*. That is
    `C1`'s failure reached by a different route — an artist-name collision aggravated by a
    rename, where `C1` was closed on a band name colliding with a song title. **It is not
    path-quality work and is not inside the pause.**
- **Track 1** (the §2.8 tie-break fix) — done and **adopted**; the app routes on
  `graph-t15-tiebreakfix.bin`.
- **Track 2, Track 2F, and the ceiling toll.** See the pause below.

## Waiting on hand-testing

**Nothing, as of 2026-07-27.** The newest [`TEST-QUEUE.md`](TEST-QUEUE.md) entry is N/A —
the engine is on the internet but there is nothing to press until Track C. **The deferred
phone section in that file is still deferred**: its trigger is the cutover, which has not
happened. `session-start` reads that file and flags anything sitting untested; it is the
authority, not this line.

**`F1` is DISCHARGED, 2026-07-26** — every journey now gets at least one stop, or says why
it cannot (PR #23). The owner ran the queued entry and it passed with no notes; its closing
condition was an observation and that observation happened. **Do not re-plan or re-open it.**
Record: [`2026-07-25-f1-minimum-stop-execution-log.md`](2026-07-25-f1-minimum-stop-execution-log.md),
design [`specs/2026-07-25-f1-minimum-stop-design.md`](specs/2026-07-25-f1-minimum-stop-design.md).

Two questions that entry raised are **still open and are the owner's alone** — no
measurement settles either: how long a forced detour may get before a journey stops feeling
like a journey (uncapped, deliberately), and whether routing two famous artists through a
third famous one reads as reasonable or as lazy.

---

## Path quality is PAUSED — owner decision, 2026-07-25

**This is a separate track from the gates, and it is stopped. Resuming it is the owner's
trigger, never a session's.**

- Track 2 and Track 2F **both returned nulls**. The ceiling *ordering* measurement came back
  **WIDE**. **Nothing adopted, no shipped code changed, no blind listen run, no threshold
  touched, no rebuild.**
- **Track 2F's full-strength toll re-run is already EXECUTED. Do not run it again** — it was
  the previous handoff's own recommendation and it has been carried out. The toll mechanism
  is exhausted with its bound holding.
- **The live candidate is a builder-side p99 rescale, and it is NOT pre-registered. Do not
  start it.** No experimental arm runs before a committed pre-registration.

**If it is ever resumed, the entry point is
[`2026-07-26-RESUME-BRIEF-path-quality.md`](2026-07-26-RESUME-BRIEF-path-quality.md)** —
read it in full first. It is not itself a resume signal. Parked candidates and what each
needs before it can move: §0 of
[`2026-07-25-HANDOFF-track2f-and-headroom.md`](2026-07-25-HANDOFF-track2f-and-headroom.md).

**Before acting on any path-quality claim**, read
[`2026-07-22-phase1-execution-log-and-graph-defect.md`](2026-07-22-phase1-execution-log-and-graph-defect.md)
§2 — and §2.12 first, because it retracts a central claim of §2.9. The three quantities that
are not interchangeable (**degree ≠ popularity ≠ fame**) are live hazards; `CLAUDE.md`'s
orient table has the short form.
