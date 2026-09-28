# Handoff — #200 `DRP-` stage 3a (the instruments) complete at Seam A, 2026-09-27

**⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-28 (Seam B) by
[`2026-09-28-HANDOFF-drp-stage3b.md`](2026-09-28-HANDOFF-drp-stage3b.md)**; its decisions list and
environment facts still stand. ~~**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it.~~ Supersedes
[`2026-09-27-HANDOFF-drp-amendments.md`](2026-09-27-HANDOFF-drp-amendments.md) on next actions. It does **not** state project
status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam** (§8's Seam A). Nothing is in flight: every background job finished, no server was
started, no subagent is running. Branch `charlessavage90/issue-200-drp-stage3a`, PR #250, tracking
issue #244 (addresses). **No arm has been swept.**

**Read, in this order:** the pre-registration's body
([`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md),
execute from the body), then the stage-3a execution log's **"Seam A"** entry
([`2026-09-27-drp-stage3a-execution-log.md`](2026-09-27-drp-stage3a-execution-log.md)), which names
what 3b inherits and must build, then the figures in
[`builder/analysis/2026-09-27-drp-stage3a/README.md`](../../builder/analysis/2026-09-27-drp-stage3a/README.md).

**Decisions taken here, not to be reverted by a well-meaning editor:**
- **The pair set is committed** (`93aa21e`, before any sweep). Never redraw it.
- **`N_noise` = 0.015 in both famous strata**, and `DRP-G6` did not fire. It is measured once, at 3a.
- **The `DRP-S1` artifact is `418fe666…`**, outside the repo at `C:\unsung-fast\drp-stage3a\`.
  `DRP-G3` passed on exactly that file; a rebuilt one must match the sha or be re-gated.
- **`DRP-C10`'s per-pair frontier count belongs to 3c**, because it needs the band journeys.
- **`N_noise` ran on the two famous strata only.** The A0 seed-1 random ladders on every stratum
  are the A0 cell's `DRP-C7` companion, and 3b produces them.

- **The stage-2 go is on the record as the session's relay on #244, and that is sufficient** (owner,
  2026-09-28). `DRP-AM5-I2`'s "posted by him" was a session's requirement and he has dropped it.
  **Never ask him to re-post it.**

**Owed, and by whom:**
- **A session:** stage 3b, to Seam B.

**Environment facts a 3b session needs:**
- The graph is read from `C:\dev\music-app\builder\scratch\graph-lba-a6.bin`. It is never copied into
  a worktree.
- Per-journey outputs keep node ids only (the §8 sealing rule).
- An A0 ladder costs about 5–10 s per famous pair and about 50 s per middle-of-the-map pair on one
  core. Separate processes per cell parallelise cleanly; this machine has 24 cores and about 12 GB free.

**What is not in the durable record:** nothing that I know of.
