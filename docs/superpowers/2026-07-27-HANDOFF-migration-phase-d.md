# Handoff — OneDrive migration Phases A–C complete, at the Phase D seam, 2026-07-27

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-27-HANDOFF-onedrive-migration.md`](2026-07-27-HANDOFF-onedrive-migration.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns
it.

**Written at a seam** — the plan's own named Phase D seam, not a mid-flight retirement. Phases
A–C are complete and verified; Phase D is not started. Nothing is in flight: no subagents, no
background jobs.

**Work from `C:\dev\music-app`.** Branch `onedrive-migration-phases-abc`, PR #36.
Record: [`2026-07-27-onedrive-migration-execution-log.md`](2026-07-27-onedrive-migration-execution-log.md).

---

## Your job

**Do not start Phase D until two things pass, and both are the owner's.** They are listed in
`NEXT.md`. Task 9 (Backblaze upload *completed*, not queued) **gates Task 11**. Task 10 says use
the new tree for a few days first.

**Then** Tasks 10 → 11 → 12, in that order. Task 11 is an irreversible deletion.

## What a cold session would get wrong

- **`MIG-10` / Task 12 is deliberately NOT done, and that is not an oversight.** `CLAUDE.md`'s
  environment note, `README.md`, `api/README.md`, `builder/README.md`,
  `.claude/agents/ml-graph-analyst.md` and `.claude/skills/session-start/SKILL.md` all still say
  the project lives under OneDrive. **That is still true of the tree that is still the
  rollback.** Correcting them before Task 11 makes the record wrong for the copy we might roll
  back to. **Do not "fix" them early.**
- **One exception was already taken:** `CLAUDE.md`'s *project-memory path* was corrected,
  because it was actively misleading a live session rather than merely describing a stale fact.
  Do not revert it, and do not read it as licence to do the rest.
- **`UV_LINK_MODE=copy` is scoped, not retired.** Measured: unnecessary in `C:\dev`, still
  required in the OneDrive tree. Project memory says so; `CLAUDE.md` still states it
  unconditionally, which is Task 12's business.
- **The Task 4 evidence is not in git and cannot be.** Five files under `C:\dev\`:
  `migration-manifest-SOURCE-2026-07-27.tsv`, `migration-manifest-DEST-2026-07-27.tsv`,
  `migration-verify-2026-07-27.txt`, `bin-SOURCE-fresh.txt`, `bin-DEST-fresh.txt`. **If Phase D
  is ever questioned, these are the proof.** Do not delete them with the old tree.
- **`MIG-5` is dead for the new tree** — its `.git` came from origin and has never been under
  OneDrive. The push from the new tree ran clean, which is the first positive confirmation.
  **The old tree still prints it** until Task 11; that remains noise, not damage.

## What is overturned and must not be reverted

- **`MIG-2` says "ten memory files". There are eleven.** Confirmed twice — by count, and by a
  cold session reading the index. It is stated as a verification criterion, so it matters.
- **The mangled-artist-descriptions defect is RETRACTED** and was never real (carried forward
  from the previous handoff — the two Track C records are annotated but still contain the
  original text). Do not reinstate it.
- **`MIG-9`'s count is 26**, not 16 and not 27. Count each slash variant separately with
  `grep -F`.

## What I know that is not in the durable record

- **⚠ `MIG-11` could not be actioned: killing the two old-tree API servers was BLOCKED by the
  tool-permission classifier, twice.** They are still running on ports **8138** and **8139**,
  from the OLD tree's `.venv`, started 2026-07-20. **They will make Task 11's deletion fail
  partially**, which is the worst state for a rollback copy. The owner has the commands; if you
  are the session doing Task 11, **verify both ports are free before deleting anything.**
- **A third listener, PID 90324 on port 53342, is a Home Assistant MCP sidecar from a different
  project.** Not artistpath. Leave it alone. It is named here only so nobody kills it while
  clearing the other two.
- **Backblaze is mid-rescan.** Acting on `MIG-3` uncovered a **pre-existing** backup failure
  unrelated to this project; a forced full rescan is uploading **over 6 GB** that had never been
  included. `C:\dev` files were seen in the queue. **This is in progress, not done** — it does
  not discharge Task 9.
- **OneDrive sync was paused for 24 h from 2026-07-27** and resumes by itself. Nothing in
  Phases A–C depends on it staying paused.
- **`.vscode/settings.json` carries an uncommitted modification this session did not make** (a
  Snyk organization ID). It was deliberately committed *around*, with a pathspec. This note does
  not speculate about its origin.
- **Measured throughput, for anyone repeating a bulk operation here:** ~2,000 files per 20 s on
  the OneDrive tree, filesystem-bound. A full walk of `builder/scratch` is ~12 minutes; the
  destination walk on `C:\dev` took 7.5. Budget for it rather than assuming a hung job.

## Two tool behaviours that cost time and will do so again

- **`TaskStop` does not kill the process tree here.** It reaps the wrapper and leaves children
  running. This produced the corruption in the execution log's §12, and reproduced itself later
  with six surviving `grep` processes. **Verify with `Get-CimInstance Win32_Process` and stop
  survivors by PID.**
- **`robocopy` exit code 1 means success.** Codes below 8 are all success; the harness reports
  any non-zero as failure.

## What was decided against

- **Renaming the memory directory** rather than copying it. A copy makes a wrong slug prediction
  free. The duplicate under the old slug is retained deliberately until Task 11, because a
  rollback would need it.
- **Setting git identity globally.** It was `--local` in the old tree with nothing global, so
  the clone could not commit. Reproduced `--local` rather than changed machine-wide, which is
  outside a migration's remit.
- **Doing Task 12 early** — see above.
