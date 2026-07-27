# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
those live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section.

**Last updated: 2026-07-26 (night), after Track B.**

---

## Next

**The ten blocking findings from the `DEP-33` review, in the order given, then Track C.**
The owner's instruction, 2026-07-26: the blockers are the first work of the next session,
not a menu.

1. [`findings/2026-07-26-track-b-cdk-review.md`](findings/2026-07-26-track-b-cdk-review.md)
   — **§2 is the work queue, already ranked** by what breaks and how silently.
2. [`2026-07-26-HANDOFF-track-b-complete.md`](2026-07-26-HANDOFF-track-b-complete.md) — the
   current handoff. Reading order, seven must-not-revert claims, and what the finishing
   session knew that is not otherwise written down.
3. [`2026-07-26-gate2-track-b-execution-log.md`](2026-07-26-gate2-track-b-execution-log.md)
   — §1 owns the deployed identity, §4 what must not be reverted, §6 the Windows traps.

**Write a plan before executing.** Ten findings across four packages, and several interact —
`ARC-5` closes half of `ARC-4`; `QUA-1`, `FRO-5` and `ARC-3` are the same missing test.

**Then Track C** — sync the SPA to the bucket. The site is not usable until it lands: the
bucket is empty, so the site currently serves the API and a password prompt. That is
expected, not a defect.

**Two things are owed before anyone else gets the URL:** the `DEP-33` review outcome acted
on, and `TR-5`'s SPA fallback, which the deploy could not verify.

---

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** `F1`, its last item, closed 2026-07-26. One live exception below (`BYP-13`). |
| **Gate 2 — friends & family** | **In progress.** Tracks A, D and B are DONE; the API is **deployed on AWS** (PR #29, branch `gate2-track-b-infra`). Track C is next, behind the ten blockers. |
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

**Nothing, as of 2026-07-26.** The newest [`TEST-QUEUE.md`](TEST-QUEUE.md) entry is N/A —
the engine is on the internet but there is nothing to press until Track C. `session-start`
reads that file and flags anything sitting untested; it is the authority, not this line.

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
