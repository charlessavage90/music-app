# Handoff — the `GBL-` blind listen specified and planned, 2026-08-04 (evening)

**Role: SUPERSEDED on next actions** by
[`2026-08-04-HANDOFF-gbl-harness.md`](2026-08-04-HANDOFF-gbl-harness.md), which is the
CURRENT handoff — the plan it hands over has since been executed to its last task. This
document **remains authoritative for the planning chunk's own internals**: why the listen
is shaped as it is, and the six claims-not-to-revert, all of which still stand. It
supersedes
[`2026-08-04-HANDOFF-cre-stage3-findings.md`](2026-08-04-HANDOFF-cre-stage3-findings.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a SEAM handoff.** The planning chunk is complete: spec committed and
owner-reviewed twice, plan committed, branch `gentle-arm-blind-listen` pushed, draft
**PR #77** open. Nothing is in flight — no background job, no subagent, no
listener on any port (8000/5173/8138/8139/8765 all checked empty).

## The next work, and who does it

**A fresh session on Opus executes
[`plans/2026-08-04-gentle-arm-blind-listen.md`](plans/2026-08-04-gentle-arm-blind-listen.md)
inline (executing-plans), on branch `gentle-arm-blind-listen`.** The owner's ruling, same
pattern as the CRE run. Three session boundaries are built into the plan and are not
optional:

1. **Task 3 is an owner gate** — pair approval becomes `GBL-AM1` before any journey exists.
2. **After Task 8, the listen itself** runs in a *separate, mechanics-only runner session*
   per `RUNNER-BRIEF.md` (written at Task 8). The executor session must not run the listen.
3. **The write-up of `gbl_result.json`** belongs to a further fresh session (the CRE
   Stage-3 rule: the reader of results did not run them).

## Which documents govern

[`specs/2026-08-04-gentle-arm-blind-listen-design.md`](specs/2026-08-04-gentle-arm-blind-listen-design.md)
(`GBL-`) governs the listen and **wins wherever the plan disagrees**. The plan is
operational. Reasoning:
[`2026-08-04-gbl-planning-execution-log.md`](2026-08-04-gbl-planning-execution-log.md).

## Claims that must not be reverted

1. **V0 is the adopted production artifact, not the CRE `E-S0` cell.** They differ (the
   drop flags). The plan's V0 mirror check exists *because* `CRE-G1`(a)'s warrant was on
   `E-S0`; do not delete it as redundant.
2. **The margin is ≥ 5 of 16 deep rows, rounded UP from the approved 3-of-10.** Rounding
   down re-weakens a bar the owner already scaled; the worked examples (9–4 fires, 10–6
   does not) are normative.
3. **`GBL-Q1`/`GBL-Q2` wording is frozen** (one axis each, owner-reviewed). A result
   exists only after the listen; until then edits are amendments, after then they are
   barred.
4. **Clips are name-based for both arms by design** — do not "improve" the G side with
   `deezer_ids`; symmetry is the point.
5. **The test runs once**; the spec's §5 scope sentence bounds what that forbids.
6. **Nothing adopts on any verdict**, the four `CRE-R2` qualifiers still travel
   ("descent partly unmeasurable", never a clean pass), and the re-crawl decision is
   untouched by any outcome.

## What this session knew that is now in the durable record

The execution log §2.3 (V0 ≠ `E-S0` and why), §3 (paths considered and dropped), and §6
(sealed-dir convention, approved-pairs sha rule, export shapes) were conversation-only
until written there. Nothing else is held back.

## Already updated — do not re-edit

The previous handoff's role line and its owed item 2 (Snyk LOW — closed as accepted,
struck in place with a revival condition), `NEXT.md` (new top block; CRE block's decision
line discharged), `TEST-QUEUE.md` (new N/A entry; `(latest)` moved), `docs/README.md`
(rows for the spec, plan, this handoff and the execution log; the CRE-stage3 handoff row
marked superseded on next actions).
