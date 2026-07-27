# Handoff — synthesis and deliverability, 2026-07-26

**Role: COMPLETE.** The last handoff in the low-connection line of work; nothing supersedes it,
and it deliberately names no successor — **path-quality work is PAUSED by owner decision and
this is not a resume signal.** If it ever resumes, the entry point is
[`2026-07-26-RESUME-BRIEF-path-quality.md`](2026-07-26-RESUME-BRIEF-path-quality.md). This is
also the document that records **`F1` as discharged and Gate 1 as complete**; for current
status read [`NEXT.md`](NEXT.md). *(Role line added 2026-07-27.)*

**Written at a clean seam. Nothing is in flight** — no dispatched subagents still
running, no background jobs, no half-written directories, no processes owned. Committed
and pushed; PR #25. Aimed at a session that has never seen this work.

Governing documents, in order: the execution log
[`2026-07-26-deliverability-execution-log.md`](2026-07-26-deliverability-execution-log.md),
then the two findings documents it names. **Where they disagree, the execution log wins.**
Identifiers: **`SYN-`**, **`CWD-`**, **`DLV-`**.

**If you are here to resume path-quality work, read
[`2026-07-26-RESUME-BRIEF-path-quality.md`](2026-07-26-RESUME-BRIEF-path-quality.md)
instead of this file.** It is shorter and written for exactly that. Resuming is the
owner's trigger, not a session's.

## What is now true that was not

- **Gate 1 is complete.** All three queued use-the-app checks came back passed, and **F1
  is discharged** — its condition was an observation and the observation happened.
- **The premise under the low-connection work is tested.** Barely-connected artists almost
  never appear as middle cards, and that survives a pair set built specifically to give
  them their best chance. It is an **association, not a demonstrated cause.**

## Which documents are now wrong, and in which direction

- **Nothing is overturned.** Today is entirely additive.
- `docs/README.md` gained four rows and one amendment. `findings/2026-07-26-committed-walk-deliverability.md`
  gained §7 forward-only, plus an inline marker on §5.

## Claims that must NOT be reverted by a well-meaning editor

1. **`CWD-2` is not superseded by `CWD-6`.** A tidy-minded reader will want to delete the
   "this test could not pass meaningfully" caveat now that a second run agrees with the
   first. **Leave it.** It is a true statement about what that run could support alone, and
   the two runs agreeing is not the same as either one being sufficient.
2. **§5's pricing-versus-arithmetic confound is unresolved.** §7 does not close it and says
   so. Do not read the two agreeing runs as having settled it.
3. **The wrong prediction (`CWD-7`, `DLV-2`) stays.** It is calibration, not clutter.
4. **The threefold overcount (`DLV-9`, `CWD-3`) stays recorded.** The inflated figure was
   self-consistent and plausible; deleting the record of it removes the only evidence for
   why gate 4 exists.
5. **`CNS-1` is still open.** The owner's search check passed, but it carries no record of
   which names were typed, so it is a non-observation and does not close a finding that
   rests on a direct worked example.

## What has already been updated — do not re-edit

`docs/README.md`, `TEST-QUEUE.md`, the two findings documents, the two analysis
directories, the resume brief, and the execution log. **Memory was not touched and the
standing context layer is net zero.**

## What I know that is not in the durable record

Checked deliberately. All folded into the log rather than left here, restated for a cold
reader:

- **The production arm reproduces byte-for-byte across three separate committed runs.**
  That is a stronger determinism guarantee than anything the record states, and it is what
  makes any future re-read of those runs cheap and safe.
- **Routing 24 pairs × 21 depths takes several minutes** and produces no output until it
  finishes. Budget for it; it is not hung.
- **`builder/scratch/` holds eighteen graph artifacts** and only one is adopted. Every
  script here asserts the sha256 for that reason, and so should anything you write.

## What was decided against

- **Chasing the pricing-versus-arithmetic confound today** — it needs an instrument neither
  run used, and choosing it is real design work rather than a follow-on.
- **Proposing the degree floor.** `SYN-`'s §4 records a consulting *position* on it, fenced
  off as a position. Nothing here proposes it, and the resume brief states the decision
  without recommending an answer.
- **Deepening the low-degree lists** — the owner's earlier call, unchanged.
- **Growing the standing context layer.** Nothing needed it.
