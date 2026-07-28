# Handoff — the OneDrive migration is planned, not started, 2026-07-27

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-27-HANDOFF-gate2-track-c.md`](2026-07-27-HANDOFF-gate2-track-c.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**Written at a seam.** The plan is committed; no task in it has run. **Nothing is in flight** —
no subagents, no background jobs, no listeners on `:8000` or `:5173` (checked by port at
session start, and nothing was started since).

Branch `queue-corrections-and-migration-plan`, PR #35.

---

## Your job

**Execute [`plans/2026-07-27-onedrive-migration.md`](plans/2026-07-27-onedrive-migration.md).**
Twelve tasks, identifiers `MIG-`, destination `C:\dev\music-app` (owner's decision).

**Read the plan, not this note, for what to do.** This note carries only what the plan cannot:
what happened around it, and what a cold session would otherwise get wrong.

**Its execution recommendation is inline, not subagent-driven**, and the reasoning is in the
PR body: every task gates the next, several need the owner's hands, and Task 11 is an
irreversible deletion. The condition that would reverse it is named there too.

**Stop at the Phase D seam.** Phases A–C leave two complete copies and are fully reversible.
Everything after deletes the rollback.

## What a cold session would get wrong

- **Task 0 is not bookkeeping.** Task 2 clones from origin rather than copying `.git`. That is
  only safe because everything is pushed. If you start with uncommitted work, the clone is
  silently lossy and nothing tells you.
- **`clamp` looks like it does Task 8 and does not.** Evaluated 2026-07-27 and written up in
  Task 8's block: its `encode_path()` handles `/` only, so on Windows it computes
  `-c-dev-music-app` where Claude Code reads `C--dev-music-app`. **Do not re-evaluate it from
  its README**, which says Windows is supported. Read the measurement.
- **`MIG-5` already fired**, on the push that created this branch — `.git/worktrees/lfcheck`
  could not be pruned, `logs/` and `refs/` carrying `ReadOnly` + `ReparsePoint`. It is noise,
  not damage; the commit and push both succeeded. **Do not repair it**; Task 2 erases it.
  Expect it to keep printing until the move.
- **The archive is the asset, not the artifacts.** 75,000 files, 1.1 GB, ~4¼ h to re-crawl and
  **not reproducible**. Verify it by bytes and count, never by eye. A count match with a byte
  mismatch is the placeholder failure and is a stop.
- **`MIG-9`'s count was wrong in the first version of this plan, and the way it was wrong is
  worth more than the number.** It said 16; it is **26**. A regex alternation across two slash
  styles matched **nothing** on the backslash branch and returned a plausible figure. The doc
  audit caught it was wrong and proposed 27, also wrong. **Count each variant separately with
  `grep -F`.** This plan asks you to verify a 75,000-file copy by count and bytes — run that
  check the same way, because this is exactly how it would fail silently.

## What I know that is not in the durable record

- **Backblaze replaced the archive-backup question**, and it is the owner's own arrangement
  rather than something this project set up. `MIG-3` and Task 9 exist because coverage is
  *assumed*: nobody has confirmed `C:\dev` is included, that `.bin` escapes the default
  exclusion list, or that an upload has *completed* rather than queued. **Task 9 gates Task
  11.** Its retention is also weaker than OneDrive's — a deleted file purges after ~30 days on
  the default plan — so `MIG-1` and `MIG-3` are not independent risks.
- **Nothing is dehydrated**, but that rests on a 2,000-file sample of 75,000, attribute
  `0x420`. Task 4's byte-total check does not depend on the sample, which is why the
  assumption is not load-bearing.
- **`du -sh` on this tree exceeded two minutes** and had to be backgrounded. Expect the copy
  in Task 3 to be slower than 1.6 GB suggests; 75,000 small files is the reason.

## Also in this PR, and unrelated to the migration

- **The 2026-07-27 queue entry is DONE, per-step on all six checks** — the first run against
  the live site. Sign-in and the shared journey link were both witnessed by a human for the
  first time; the link was opened by a recipient who had never logged in.
- **The mangled artist descriptions are RETRACTED and were never real.** Retraction in the
  Track C execution log's deferral table; struck from `NEXT.md`. **Do not reinstate it from
  the two Track C records** — both are annotated, but both still contain the original text.
- **`env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert**, because `index.html` never
  sets `viewport-fit=cover`. Recorded in the queue entry, **no fix proposed**, and it is not
  part of the migration. Latent, not live.

## What is owed that this session did not do

> **⚠ This section was written before the closeout ran and then corrected after it.** It said
> a closeout had not happened; one did. `NEXT.md`'s "Closeout state" section owns the full
> account — read that, not this. **Only `B2` and `B3` are genuinely still owed**, and both
> travel with the migration work because they need a finished artifact and this session
> produced no code.

- **`B1` ran and mattered.** `docs-lint` passes, and `doc-auditor` — scoped to the diff —
  found **three HIGH defects**, all fixed before merge. Two were in this session's own output
  and it could not see either: `docs/README.md` briefly had **two rows both claiming to be
  "the CURRENT handoff"**, and this section understated what had been done.
  **The third is the one to carry forward: `MIG-9`'s script count was wrong.**
- **The Gate 2 → 3 team review is now genuinely due to be *recommended*.** Its condition —
  "after a period of real use" — is closer to met than it has ever been, since real use has
  now happened on a real device. **It is the owner's call and was not put to him.**
- **iOS is still unexercised.** The phone pass was an Android Pixel: Safari rendering, the
  iPhone home indicator, and iOS keyboard behaviour on artist names remain unanswered by
  anything.
