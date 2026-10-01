# Handoff — #200 `DRP-` stage 5 listen PREPARED (seam 5C): `DSL-G1`, pre-screen, strike, pin, dry-run, 2026-09-30

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-30-HANDOFF-drp-stage5b.md`](2026-09-30-HANDOFF-drp-stage5b.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** Nothing is in flight: no process, server or subagent of this session survives. Branch
`charlessavage90/drp-listen-prep`, PR #266, issue #244 (addresses). Execution log:
[`2026-09-30-drp-stage5-listen-prep-execution-log.md`](2026-09-30-drp-stage5-listen-prep-execution-log.md).
Governing text: `DRP-AM7` (§14 of the #200 pre-registration).

> ⛔ **This note is for the OWNER, not the runner.** `RUNNER-BRIEF.md` forbids the runner every
> handoff and execution log under `docs/superpowers/`, so the runner must never be pointed here. Its
> whole brief is `RUNNER-BRIEF.md`.

**The next session is the RUNNER (seam 5D). It must be fresh.** This session saw side-labelled output
and may run neither the listen nor the write-up (`DRP-AM7-5`). Launch it with exactly this, and nothing
about the experiment:

> *You are the runner for a blind listen. Read `builder/analysis/2026-09-30-drp-stage5-listen/RUNNER-BRIEF.md`
> and follow it exactly; read nothing it forbids. Work only in the worktree it names,
> `C:/Users/charl/worktrees/music-app-dsl-runner`.*

**Merge PR #266 first.** The brief cuts that worktree from `origin/main`, and generation refuses
without the pinned pair sha. If it is not merged, tell the runner to branch from
`charlessavage90/drp-listen-prep` (the brief allows this). **That worktree must outlive the runner**:
the sealed mapping is written there, and the write-up session (5E) works in it.

**Done here, so not to be re-done:** `DSL-G1` PASS; pre-screen run and committed; the owner struck one
pair, filled from its own tier; `DSL_PAIRS_SHA` pinned; dry-run passed every gate with nothing written.
The runner's path and branch (`dsl-listen-run`) were checked free.

**Decisions a well-meaning editor must not revert:**

- **The pre-screen's import-order fix** (`88f45c3`) is committed *before* its outputs; the outputs
  record that script's sha. Do not "restore" the original order.
- **`DSL_PAIRS_SHA` pins the post-strike file.** Re-running `dsl_pairs_final.py` rewrites the file with
  a new timestamp and breaks the pin; the strike is final (`DRP-AM7-2` step 9).
- **`DRP-AM7`'s "each tier needs 6" is not step 8's stop rule** (log, correction 2). The amendment is
  unedited; the log is the address.

**Owed, and by whom:** the owner, merge #266, then launch the runner and listen. Then a fresh write-up
session (`dsl_unblind.py`, the findings note), then his use gate. Carried, and his: the unticked
`TEST-QUEUE.md` boxes, #237, #233, and the #264 exploration review, which comes after the listen.

**What is not in the durable record:** nothing that I know of.
