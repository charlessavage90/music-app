# Handoff — `TAS-R1`–`TAS-R4`, the routing side of the tag probe, 2026-08-01

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-31-HANDOFF-tas-am3-am4.md`](2026-07-31-HANDOFF-tas-am3-am4.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**This is a SEAM handoff, not mid-flight.** Everything is committed and pushed, nothing is in
flight, no subagent is running, no background job survives, no port is listening, and the tree
is clean. `TAS-` Tasks 1–7 are complete; **Task 8, the findings document, is the one thing
left**, and it was left deliberately — §5 licenses an outcome read only once the full grid and
both instrument checks are in hand, which they now are.

## What this work is

Continuation of the `TAS-` probe. Governing experimental document:
[`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md).
Governing plan for the routing side:
[`plans/2026-07-31-tas5-routing-execution-plan.md`](plans/2026-07-31-tas5-routing-execution-plan.md).
Record: [`2026-07-30-tag-discrimination-execution-log.md`](2026-07-30-tag-discrimination-execution-log.md),
**§15–§16** (this session). Probes: `builder/analysis/2026-07-30-tag-discrimination/`.
PR: **#58**.

## The five things that must not be reverted

1. **`TAS-AM5c` FIRED, so `TAS-5`'s change is NOT attributable to genre structure.** Every
   `TAS-5` figure carries that caveat. It is not softened by the change rate being large, and
   the largeness is exactly what makes the control decisive rather than a formality.
2. **`TAS-6`'s ROUTING half is VACUOUS — never quote it as a pass.** Baseline zero, so the
   bar cannot fire and "not adverse" is a division-by-zero artifact. The zero is a
   corroboration of `DD-F1`, not a defect of the run.
3. **`TAS-6`'s SELECTION half is still ADVERSE** and still bars an adoption recommendation
   for the build-time architecture, whatever else shows.
4. **The old probe plan's Tasks 5–7 contain a trap and are superseded.** Task 7 Step 5 tells
   the executor to make the withdrawn randomised-label red check fire and stop if it does
   not. **Execute the routing side only from the 2026-07-31 plan.**
5. **`TAS-AM5` was written BEFORE any routing figure existed** and says so at its head. Do
   not remove that disclosure to make §8 read uniformly — `TAS-AM3` and `TAS-AM4` carry the
   opposite disclosure, and the difference between them is the point.

## Status of the instrument question

**Discharged on both sides.** Selection by `TAS-AM3a`; routing by `TAS-AM5a` (equivalence,
0 mismatches on the full draw against production's own pathfinder) and `TAS-AM5b` (liveness,
0 failures against an independently computed reference). **So the `TAS-5` null is a real null,
not a broken harness** — that distinction is the whole reason `TAS-AM5` exists.

## The open decision, and what I would do

**Whether to write Task 8's findings now, and what to do with the probe afterwards.**

**If I were continuing: write Task 8, then stop and take the architecture question to the
owner as closed rather than open.** The probe was commissioned to inform a choice between two
architectures. It has now returned no adoption case for either — one barred by its own guard,
one surviving on a change the control says is not about genre. That is a complete answer, not
a partial one, and it is worth stating as such rather than leaving the question looking live.

**What I would not do:** re-run anything hoping for a better number. No bar may move now that
results exist, and both instrument checks passed, so there is no harness defect to chase. In
particular, do not read the 90–95% journey-change rate as encouraging — the null control is
what that figure has to be read through.

**The one thing I would flag as genuinely unresolved** is the owner's clustering idea (a real
label's carriers cluster, a junk label's scatter). It is unmeasured, it is cheap, and it is
the only live idea in this area that the probe did not touch. It is in `NEXT.md`'s deferral
table.

## Already updated — do not re-edit

`NEXT.md` (status block, four stale claims, six deferral rows, Snyk count), the execution log
(§15, §16, and its header's scope line), the pre-registration's §8 (`TAS-AM5`), `docs/README.md`
(two plan rows), the probe directory `README.md` (five script rows, a stale test count removed),
and this handoff's predecessor's role line.

## What I know that is not otherwise in the durable record

- **The capture regenerates byte-identically.** Its sha256 matches the value recorded in
  execution log §14.1, which was recorded precisely so a divergent regeneration would be
  detectable. That check has now run and passed — the pipeline is deterministic across
  sessions from committed code, which is stronger than the green edge-for-edge check.
- **A test can pass on a tie-break rather than on the behaviour it names.** Closeout B3 found
  that `test_a_dominating_weight_routes_through_the_agreeing_neighbour` was green with the
  coherence term **zeroed out**, because the expected route was also what a lowest-id
  tie-break produces. Fixed by expecting the higher-id route. **When a fixture has two
  symmetric routes, always expect the one a tie-break would not pick.**
- **The doc-auditor's report can be stale on arrival.** It audited a snapshot taken before
  §16 was appended and reported the section missing. Its other findings were all real. **Check
  each finding against current state rather than accepting or dismissing the report wholesale.**
- **`docs-lint.sh`'s check 2 catches an unclassified new document**, and it caught this
  session's plan. Worth running immediately after creating any document under `docs/`, not
  only at closeout.
- **Nothing about tags has been measured against the owner's ear, and cannot be offline.** The
  11 blind verdicts remain unconsumed; `ct_retrodict.py` remains committed and unrun.
