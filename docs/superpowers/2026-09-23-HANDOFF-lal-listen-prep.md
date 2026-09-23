# Handoff — the `LAL-` blind listen prepared (`LBA-AM6-2`, `-11`; `LBA-AM7`), 2026-09-23

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-23 by [`2026-09-23-HANDOFF-lal-listen-read.md`](2026-09-23-HANDOFF-lal-listen-read.md)** — the listen it prepared has run and been read. It remains authoritative for what it recorded about the preparation. ~~ACTIVE — this is the CURRENT handoff. Nothing supersedes it.~~ Supersedes
[`2026-09-22-HANDOFF-lba-listen-amendments.md`](2026-09-22-HANDOFF-lba-listen-amendments.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** Everything is committed on `lba-a6-listen-prep` (PR #133). Nothing is in flight: no
background job, no server, no half-written file. The retained log is
[`2026-09-23-lal-listen-prep-execution-log.md`](2026-09-23-lal-listen-prep-execution-log.md).

## ⛔ Who may read this

**The RUNNER must not** — it is under `docs/superpowers/`, which `RUNNER-BRIEF.md` puts off-limits.
The owner hands the runner the brief, not this note.

## What is now true

- The listen's pairs are **final**: `lal_pairs.json`, pinned; the owner struck none. They were drawn
  under **`LBA-AM7`**, which replaced `LBA-AM6-2`'s pool after the owner did not know most of the
  first draw's endpoints.
- A generation **dry-run passed every gate**. The runner's real run deals sides afresh.

## Easy to get backwards

- **Do not "restore" `lal_pairs_drawn.json`.** It is the superseded first draw, kept as the record.
  `lal_pairs_final.py` defaults to `lal_pairs_drawn_am7.json` on purpose.
- **The runner does not unblind.** The write-up session does, **in the runner's worktree**
  (`C:/Users/charl/worktrees/music-app-lal-runner`), because the sealed mapping is gitignored and
  lives there. Nobody removes that worktree before the write-up commits.
- **This session is barred from both the listen and the write-up** — it has read map-labelled
  pre-screen output.
- **`LBA-AM7`'s familiarity list is far larger than `LBA-AM6`'s**, which is why Gate N rejected
  pairs this time and not the first. That is the fix working, not a regression.

## What I know that is not in the durable record

Nothing. The owner's two rulings this session — rebuild the pool (option B) and strike none — are in
`LBA-AM7` and in `lal_am7_known.json`/`lal_pairs.json`.

## Owed, and by whom

**The owner:** merge #133; then open a fresh session with `RUNNER-BRIEF.md` as its only brief. The
rest of the sequence is in `NEXT.md`.
