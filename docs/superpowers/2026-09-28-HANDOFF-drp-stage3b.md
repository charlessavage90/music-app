# Handoff — #200 `DRP-` stage 3b (the `DRP-S0` row) complete at Seam B, 2026-09-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-27-HANDOFF-drp-stage3a.md`](2026-09-27-HANDOFF-drp-stage3a.md) on next actions. It does **not** state project
status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam** (§8's Seam B). Nothing is in flight: every sweep and gate process finished, no server was
started, no subagent is running. Branch `charlessavage90/issue-200-drp-stage3b`, PR #251, tracking
issue #244 (addresses). **The owner chose a separate session for 3c** (2026-09-28).

**Read, in this order:** the pre-registration's body
([`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md),
execute from the body), the stage-3a log's "Seam A" entry, then the stage-3b log
([`2026-09-28-drp-stage3b-execution-log.md`](2026-09-28-drp-stage3b-execution-log.md)) — its task 2 and
"Seam B" entries above all — then
[`builder/analysis/2026-09-28-drp-stage3b/README.md`](../../builder/analysis/2026-09-28-drp-stage3b/README.md).

**Decisions taken here, not to be reverted by a well-meaning editor:**
- **The ceiling's relaxed height is found by certifying a minimax candidate with the shipped
  `find_journey` from both sides, not by bisection** (log, task 2). It departs from `DRP-AM3` item 4's
  wording, not from its definition of `c`. On `DRP-S0` every relaxed press certified and none bisected.
  **3c uses the same harness**, so the two rows are found the same way; do not reintroduce bisection
  for one row only.
- **Both press rules ran on all four pair sets, `DRP-C8` included** (log, task 1).
- **The Seam-B README reads no result.** No criterion is computed and no outcome assigned. That is 3d's,
  at *complete*, from the committed JSON. A 3c session should keep its README the same way.
- **One harness version per row**, enforced by the gate script. A harness edit mid-row means re-running
  the row, as happened twice here.

**Owed, and by whom:**
- **A fresh session:** stage 3c, to Seam C, plus `DRP-C10`'s per-pair frontier count.
- **A session that ran no sweep:** stage 3d.

**Environment facts a 3c session needs:**
- The `DRP-S1` map is `C:\unsung-fast\drp-stage3a\graph-drp-s1.bin` (sha `418fe666…`); `drp_sweep.py`
  loads it only if `DRP-G3` passed on that sha. It is never copied into a worktree.
- The row took about 2.5 h wall at 14 processes (≈ 250 MB each; the machine had ≈ 11 GB free). The
  ceiling cell dominated at 48–75 min per shard; `jobs_all.txt` and `run1.sh` under
  `C:\unsung-fast\drp-stage3b\logs\` are the launch pattern (adjust the cell names and the output root).
- Launch trap met here: a bash tag written `$c__DRP` expands the variable `c__DRP`. Write `${c}__`.
- The gate script's `DRP-G9` step is heavy; run its eight `g9 SET RULE` partials in parallel before
  the combining run.

**What is not in the durable record:** nothing that I know of.
