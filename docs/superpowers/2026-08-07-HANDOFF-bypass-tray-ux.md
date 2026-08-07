# Handoff — the bypass tray UX shipped and deployed, 2026-08-07

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-tcr-rerun.md`](2026-08-06-HANDOFF-tcr-rerun.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The track ran to completion, everything is committed and pushed, PR #89
is merged, the work is **deployed to production and verified**, nothing is in flight, no port
is listening, and the degradation tell did not fire.

Reasoning: [`2026-08-07-bypass-tray-ux-execution-log.md`](2026-08-07-bypass-tray-ux-execution-log.md).
Design export: `frontend/design/2026-08-07-bypass-tray/` (`UI-1`). Branch `bypass-tray-ux`,
**PR #89 MERGED** at `a7a8b9a`; the branch is spent — new work branches from `main`.

---

## Documents that are now wrong, and in which direction

**The staleness runs one way: things this track CLOSED are still recorded as open.**

- **`DEP-34-FIX` is done.** Any document calling it open is stale. `NEXT.md` was rewritten
  at this closeout; the `2026-08-06` handoffs are frozen and correctly describe their own
  moment, so they are **not** edited.
- **`TEST-QUEUE.md` has zero live entries.** Both 2026-08-06 live-site items are discharged.
- **The bypass buttons are no longer "✕ Not for me" / "✓ I know them".** Frozen execution
  logs and discharged queue entries naming them are **correct for their own date and must
  not be edited**. `.claude/skills/closeout/SKILL.md` used the old label in a worked example
  and was corrected, because a skill body is live instruction rather than a record.

## Claims that must NOT be reverted by a well-meaning editor

- **The strip says "Reroute from here", not "Not this step".** This is a deliberate
  departure from the supplied design, argued from that design's own 1b annotation and then
  settled by the owner. Do not "restore fidelity to the mockup".
- **The clip-length line stays OFF the landing page.** The design re-adds it; the owner
  removed it on 2026-07-28 and confirmed on 2026-08-07 that it stays out. A design canvas is
  not authority over a decision the repo records.
- **The landing page carries no mechanism sentence.** The owner's copy replaced
  "someone their listeners share" with a promise; the *how* now lives in the journey page's
  explainer. Do not reinstate it as a fix — there is a comment at the call site saying so.
- **`NOTICE_MIN_MS` is a floor on reading time, not an artificial delay.** The path is
  already rendered underneath. Removing it re-opens the defect the owner reported.
- **The notice's lifetime must not be keyed on the artist list.** That was the stranded-
  notice bug (log §3.1). Two separate effects, deliberately.
- **The owner's `MSW-` map pass does NOT license the `GBL-` null.** That adoption was an
  owner override, knowingly taken and never evidence-backed. Use in production is evidence
  the map works; it is not the pre-registered comparison, which stands as a null.
- **`TEST-QUEUE.md` is for defects and functionality only** — never for long-run judgement
  of how the app feels. Owner ruling, 2026-08-07, written into that file's header.
- **The three sample-journey MBID pairs are a standing liability** (log §2.5, `SMP-1`). The
  comment at the call site is not clutter.

## Already updated — do not redo

`NEXT.md` (rewritten), `docs/README.md` (new rows for this log and this handoff; the previous
handoff's row updated to name this one as successor), the previous handoff's role line,
`TEST-QUEUE.md` (two discharges + the new rule), `.claude/skills/closeout/SKILL.md` (one
stale worked example), `frontend/src/index.css` (a CSS comment asserting an untested Safari
behaviour — closeout B4).

## What I know that is not in the durable record

**Empty, checked rather than asserted.** Every figure reported to the owner was verified into
a committed file before retirement: bundle hashes and `/health` identity in the execution log
§6, drift row detail in §4 and §5, gate outcomes in §4. The three open items all carry
success conditions in §5.

One thing worth stating because it is a *negative* result and leaves no artifact: the
`AlarmTopic` subscription was checked **directly** via `sns list-subscriptions-by-topic`,
not merely inferred from the drift report. It returned zero. That is why `SNS-1` is written
as fact rather than as a suspicion.

## Anything in flight

**Nothing.** No subagents beyond the closeout `doc-auditor`, no background jobs, no
listeners: ports 8000, 5173 and 5174 were swept and are all **free** — both were stopped at
this closeout, including one orphaned Vite child that survived its parent task.

## What I would do if I were continuing

Nothing in this track; it is closed and shipped. The one thing the closure changes elsewhere
is **`SNS-1`** — the billing alarm has no subscriber, which is pre-existing, was surfaced by
this closeout's drift gate, and is the owner's because it needs his inbox. It is not blocking
anything, but `DEP-17` records App Runner billing as unmeasured and this alarm is the only
thing watching cost.
