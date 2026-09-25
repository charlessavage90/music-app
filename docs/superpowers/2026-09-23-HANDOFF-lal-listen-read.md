# Handoff — the `LAL-` blind listen run, unblinded and read, 2026-09-23

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-25 by
[`2026-09-25-HANDOFF-lba-a6-adoption.md`](2026-09-25-HANDOFF-lba-a6-adoption.md)**. The use gate
has run and the candidate is adopted. ~~ACTIVE — this is the CURRENT handoff. Nothing supersedes it.~~ Supersedes
[`2026-09-23-HANDOFF-lal-listen-prep.md`](2026-09-23-HANDOFF-lal-listen-prep.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** The listen is complete and read. Everything is committed on `lal-listen-run` (PR #135).
Nothing is in flight: no background job, no server. The retained log is
[`2026-09-23-lal-listen-read-execution-log.md`](2026-09-23-lal-listen-read-execution-log.md).

## What is now true

- **The read is `LAL-R1`, PASS on coherence**, and it is final (`LBA-AM6-9`). Figures, what cuts
  against the read, and the barred reads are in
  [`findings/2026-09-23-lal-listen-results.md`](findings/2026-09-23-lal-listen-results.md) §0, §1
  and §5.
- **The blind is spent.** Journeys on the candidate may now be shown to the owner. `LBA-G5` is
  unblinded by design.

## Easy to get backwards

- **Do not "correct" the owner's pair-3 d20 note.** It says Sevdaliza was on R; the stimulus puts
  her on L. The results note records this as a slip, and his **pick** is what counts.
- **The identified rows and the clipless-card rows are the same three rows.** They are one
  exposure, not two. Do not add them up as separate counter-evidence.
- **PASS is not evidence about `LBA-G5`'s criterion**, and a `LBA-G5` outcome does not re-read the
  listen (`LBA-AM6-10`).
- **The worktree holds the only copy of `.superpowers/lal/`** (the sealed mapping, hidden metrics
  and clip cache). Everything the read needs from it is now in `lal_result.json` and the note.
  Removing the worktree loses the sealed metrics per journey. That is the owner's call.

## What I know that is not in the durable record

Nothing.

## Owed, and by whom

**The owner:** merge #135; decide whether to keep this worktree; then `LBA-G5`. The sequence is in
`NEXT.md`.
