# Handoff — #200 `DRP-` stage 3d (the results note) complete at Seam D, 2026-09-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-28-HANDOFF-drp-stage3c.md`](2026-09-28-HANDOFF-drp-stage3c.md) on next actions. It does **not**
state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** Stage 3 of the pre-registration is finished. Nothing is in flight: no process, server or
subagent of this session survives. Branch `charlessavage90/drp-stage-3d`, tracking issue #244
(addresses; `gh` owns the PR and merge state).

**Read:** the results note, [`findings/2026-09-28-drp-lattice-results.md`](findings/2026-09-28-drp-lattice-results.md).
It owns the reading and names no candidate. The stage-3d execution log
([`2026-09-28-drp-stage3d-execution-log.md`](2026-09-28-drp-stage3d-execution-log.md)) holds the choices
the design left to 3d, committed before any figure existed.

**Decisions taken here, not to be reverted by a well-meaning editor:**
- **The thirteen choices in the log's task 1 were fixed before the reader first ran**, and the commit
  order shows it (`1c1e874` before `0b80dab`). None of them turned out to decide a read (log, task 2).
- **Cell identity is checked on LF-normalised bytes.** The autocrlf working copy hashes differently
  from the committed files. `drp_c10_frontier.json`'s `cell_file_sha256` field holds working-copy
  shas and is not an identity record.
- **Stage 3b's certified relaxation search is accepted** (log, orientation), with what it costs
  `DRP-G9`(d) stated in the note's weakest link.

**Owed, and by whom:**
- **The owner:** stage 4, his go/no-go on at most one cell or none (§8; `DRP-R10`). Then, if a cell,
  the stage-5 blind listen designed cold by a session that has seen no journey, and his use gate.
  **#249's second condition** (where within a journey famous artists sit) is his to name at stage 4
  or not.
- **Nothing is owed by a session before his stage-4 call.** #246 closes with PR's merge (trigger did
  not fire); #247 was closed as not planned (its condition needed `DRP-R0` to fire, and it did not).

**Handoff defect found in the previous one, recorded so the next handoff avoids it:** the stage-3c
handoff said 3d needs "neither graph artifact". It does. The cell files carry node ids and no fame
values, so the reader loads both artifacts read-only.

**What is not in the durable record:** nothing that I know of.
