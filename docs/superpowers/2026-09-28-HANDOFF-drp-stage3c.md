# Handoff — #200 `DRP-` stage 3c (the `DRP-S1` row) complete at Seam C, 2026-09-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-28-HANDOFF-drp-stage3b.md`](2026-09-28-HANDOFF-drp-stage3b.md) on next actions. It does **not** state project
status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam** (§8's Seam C). Nothing is in flight: every sweep and gate process finished, no server was
started, no subagent is running. Branch `charlessavage90/DRP-stage-3c`, PR #259, tracking issue #244
(addresses). **All eight cells are now *swept*** (§7).

**Read, in this order (a 3d session):** the pre-registration's body
([`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md),
§5, §7 and §4's drop rule above all), then the stage-3a README, the stage-3b README and log task 2, the
stage-3c README ([`../../builder/analysis/2026-09-28-drp-stage3c/README.md`](../../builder/analysis/2026-09-28-drp-stage3c/README.md)),
and the stage-3c log's "Seam C" entry
([`2026-09-28-drp-stage3c-execution-log.md`](2026-09-28-drp-stage3c-execution-log.md)).

**Decisions taken here, not to be reverted by a well-meaning editor:**
- **The `DRP-S1` row ran stage 3b's harness unchanged, same sha (`6213bb1e…`).** Its cell files and gate
  verdict therefore sit in `builder/analysis/2026-09-28-drp-stage3b/`, beside the `DRP-S0` row's; the
  stage-3c README owns their shas. Do not move them: the scripts write there, and a move breaks the
  reproduce commands.
- **`DRP-G9`'s partials are keyed by row** (`g9__ROW__SET__RULE.json`) and the combining step refuses
  another row's. Before the fix, a `DRP-S1` run could have accepted `DRP-S0`'s partials, since both rows
  share one harness sha. The `DRP-S0` verdict was re-run on the fix and reproduced byte for byte.
- **`DRP-C10`'s frontier count is kept two ways** (endpoints included and excluded) **and summarised
  nowhere.** Which count §2.4's condition reads is 3d's choice, not this stage's.
- **No result was read.** Neither README computes a criterion or assigns an outcome.

**Owed, and by whom:**
- **A session that ran no sweep:** stage 3d, the results note.
- **The owner:** stage 4 onward, after 3d.

**Environment facts a 3d session needs:** none that is not in the READMEs. 3d routes nothing, so it
needs neither graph artifact, only the committed JSON. If it re-runs anything on Windows, the harness
sha trap (the stage-3c README, "Reproduce") applies.

**What is not in the durable record:** nothing that I know of.
