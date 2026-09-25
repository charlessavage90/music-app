# Handoff — `LBA-A6` deployed to production, 2026-09-25

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-25-HANDOFF-lba-a6-adoption.md`](2026-09-25-HANDOFF-lba-a6-adoption.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** The deploy is done and verified; everything is committed on
`charlessavage90/deploy-lba-a6-production` (PR #236). No background job, no server, no dev port
held. The retained log is [`2026-09-25-lba-a6-deploy-execution-log.md`](2026-09-25-lba-a6-deploy-execution-log.md);
this note is a delta against it.

**Which documents are now wrong, and in which direction**
- None found. `infra/README.md` §4 now names `graph-lba-a6.bin` as served, and `NEXT.md`'s standing
  fact about the UI name was corrected (it had been false since 2026-09-08).
- Frozen plans and specs naming `graph-lux4.bin` were correct when written. Leave them.

**Overturned — must not be reverted by a well-meaning editor**
- **A graph-swap `cdk diff` has FOUR rows**, the IAM read statement among them, and
  `--require-approval never` is passed **only after the owner has seen that IAM delta**
  (runbook §5). "Three rows, anything else is a stop" is wrong for a map change.
- **The "omitted 1 change" line is the viewer function, and is inert only when checked**: the live
  code equals the synthesised code (runbook §5 has the comparison). Earlier logs' "exactly four"
  never ran `--strict`.
- **A graph rollback includes the frontend** (runbook §9, from `e5d8850`). The landing's stop counts
  are measured on the map.
- **No pre-set revert trigger exists for `LBA-A6`** — owner ruling, verbatim in the log §6.

**Already updated, so do not re-edit:** runbook §4/§5/§9; #142 (closed with its reading); #237
(the prune deferral); `TEST-QUEUE.md`'s two "Where" lines; the `docs/README.md` rows.

**What is not in the durable record:** nothing. Two operational facts that are, and would
otherwise cost a successor time: Cloudflare **1010-blocks Python-urllib's default user agent**, so
any scripted probe of unsung.fm must set its own (log §5); and **CloudWatch delivers path events
minutes late**, so count them only after they stop arriving (log §5).
