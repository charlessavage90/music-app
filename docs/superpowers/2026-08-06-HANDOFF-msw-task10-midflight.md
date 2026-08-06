# Handoff — the `MSW-` map switch, Task 10 half done (mid-flight), 2026-08-06

**Role: SUPERSEDED on next actions** by
[`2026-08-06-HANDOFF-msw-seam3.md`](2026-08-06-HANDOFF-msw-seam3.md), which is the CURRENT
handoff. **This note remains authoritative for Task 9's internals** — the three plan defects,
the `MSW-G3` firing, the acceptance rejection and the owner's Option A recalibration — **and
its "Claims that must NOT be reverted" list still stands in full.** Supersedes
[`2026-08-06-HANDOFF-msw-task8-midflight.md`](2026-08-06-HANDOFF-msw-task8-midflight.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**⚠ A MID-FLIGHT handoff, not a seam.** The plan's seams are 5/7/10/12. Task 9 is complete and
**Task 10 is 2 of 4** — `MSW-V1` and `MSW-V4` done, `MSW-V2` and `MSW-V3` not started. Seam 3
is therefore **not reached**. `session-start`'s cold-read check applies: **state back what you
believe the situation is before acting on this note.**

**Branch** `msw-package-adoption-plan`, draft PR **#81**. HEAD `1c40c9f`. Tree clean, no
listener on 8000 or 5173, nothing in flight.

---

## Why this stopped here

**Not the degradation tell.** No figure was re-requested, no tracked item dropped, no firm
claim revised under questioning.

The reason is a **role conflict the plan names itself**: *"The Seam-3 session must not be the
session that reads the verification results and decides."* This session **built the artifact
and recalibrated the acceptance bound that let it through**. It is therefore the wrong session
to run the remaining verification and report it — not because it is tired, but because it
would be checking its own work and reporting on its own judgement call. The session raised
this and recommended handing over; the owner ran `closeout`.

## What is done

**Task 9 complete** (`3aa61f0`, `4b55144`, `1aacc38`). **Task 10 Steps 1 and 4 complete**
(`53ca147`, `1c40c9f`). Reasoning and figures are in the execution log's **Task 9** and
**Task 10** sections — cited, not restated here.

**The artifact exists** and its identity is committed:
`builder/scratch/graph-msw-tu50.bin`, sha256
`43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`, 58,838 artists,
1,315,684 edges. Built twice, byte-identical.

## Every number computed that is not in the retained log

Enumerated rather than filtered — the mid-flight rule.

- **D6 standing layer, absolute:** **45,569 characters unconditional / 2,459 lines
  conditional.** **This session's delta is exactly zero in both** — it touched no
  standing-layer file, and the figures are byte-identical to the Task 8 session's, which is a
  third independent reproduction of them.
- **Suite counts at this HEAD:** **224 builder** (up from 220 — four new CLI-flag tests),
  **254 api** (unchanged; no api file was touched). Frontend not run, no frontend file
  touched.
- **`docs-lint`: hard checks PASSED.** 27 `CAND` figure-restatement candidates, **all
  pre-existing thresholds in preregistration specs, none introduced by this diff** — checked
  file by file against the diff, not assumed. Same adjudication the Task 8 session made.
- **Port sweep: zero listeners** on 8000 and 5173. This session started no server.
- **Snyk `snyk_code_scan` over `builder/src`: 0 issues.**

## Decided against, with reasons — these leave no artifact and evaporate first

- **Starting `MSW-V2`.** Three reasons, in order of weight: it is built around `load_cell` for
  `CRE-` cells so pointing it at a plain artifact needs real adaptation; it touches the same
  harness files the `MSW-V4` agent was reading while that agent ran; and the plan calls it
  *"a report row, not a gate"* with no pre-registered threshold, so nothing fires on it.
  **Deferred, not dropped — Task 10 is not complete without it.**
- **Starting `MSW-V3`.** Needs a live API, a dev server and Playwright, and it is verification
  of this session's own artifact. It belongs with the successor.
- **Dispatching `ml-graph-analyst` on the Task 9 acceptance failure** (the plan's conditional
  property-or-bug trigger). The structural metrics did not drift from what `B-S1` predicts —
  they landed on it to within 30 nodes, from the committed record, with a one-knob explanation
  per breach. Dispatching would have been escalating settled reasoning.
- **Flipping the `require_fame` default** to make the Task 9 build work. Forbidden by Task 11
  Step 0's ordering; a `--require-fame` `store_true` flag was added instead.
- **Widening the acceptance bounds into a union covering both the old and new maps.** It would
  have kept the frozen probe passing with no code change, and gutted the tripwire — a band
  spanning two structurally different maps cannot detect a build that lost a large share of
  either.
- **Fixing `check.py`'s `ROOT`**, which still points at the pre-2026-07-27 OneDrive path and
  has been unrunnable since the move. Out of Task 9's remit; recorded in the log.
- **Keeping the determinism twin artifact.** Deleted: byte-identical, so nothing was lost, and
  an 18 MB near-namesake feeds the "several graphs exist and are not interchangeable" problem.

## What the owner said in conversation that is in no other file

**Pre-authorisations given for this session's run, 2026-08-06 — they were scoped to it and the
successor should NOT assume they carry forward without asking:**

> add `--cap-strategy` to `cmd_build` if missing; if `MSW-V1`'s stop-branch fires, write the
> report and STOP — don't wait; if a clip can't be confirmed audible, say so plainly, don't
> claim it; run the `ml-graph-analyst` dispatch for `MSW-V4`.

**Hard stops he set, which DO carry forward:**

> do NOT start Task 11 or flip any default — Seam 3 is mine. Commit the artifact's sha256 in
> the SAME session as the build, first thing after building. Keep verifying inherited work as
> you go.

**And his notes on the `require_fame` defect**, which correctly predicted that Task 9 would
need **two** flags rather than the one the plan anticipated, and that the obvious fix
(flipping the default) is the forbidden one.

**Still standing from 2026-08-05, and NOT discharged:**

> *"The last session was not long-lived, but seemed to make a few errors along the way. Verify
> its work as you go."*

## Claims that must NOT be reverted by a well-meaning editor

Everything in the two previous handoffs' lists still stands. Additionally:

1. **`--require-fame` is a `store_true` flag and must stay one.** It can only turn the guard
   ON. Once `config.py`'s default flips at Task 11, omitting it inherits `True`. A tri-state
   flag able to switch the guard *off* from the command line is the one thing this must not
   offer.
2. **`--algorithm` and `--require-fame` are both non-optional on the Task 9 build.** Without
   the first it builds an empty graph; without the second, a **fameless** one, exiting 0 either
   way. Both are now in the plan's command with warnings. Do not simplify them back.
3. **The acceptance recalibration moved the CENTRE, not the tolerance** (±20 % in both cases).
   Do not "tidy" it to rounder numbers without re-checking the four-artifact table in the log
   — the band must admit this build **and** `B-S1`, and exclude the retired map **and** a
   mutual-kNN build of the candidate archive.
4. **`PRE_MSW_ACCEPTANCE` in the frozen probe is era-pinning, not duplication.** Deleting it
   and pointing the probe back at `PRODUCTION_ACCEPTANCE` makes it fail.
5. **`MSW-V4`'s deviation is TWO knobs, not one** — frame population *and* estimator. The
   estimator half is negligible but the decomposition is what makes the attribution valid.
6. **The 21-node null-pricing gap is deviation 3, not deviation 2.** It is correct shipped
   behaviour and must not be filed inside `MSW-V4`'s frame bound.

## What has already been updated — do not re-edit

The execution log (Task 9 and Task 10 sections), the plan (Task 9's command corrected, all
five steps ticked), `NEXT.md`, `docs/README.md`, this note, and the previous handoff's role
line.

**`CLAUDE.md` was NOT touched and still needs no correction.** Its "Graph shape" section
remains accurate about what *ships* today and becomes false at **Task 11**, where its
correction is already listed.

## The open decision, and what I would do

**Not "the owner's call" — here is a position to argue with.**

The decision is how to finish Task 10. **I would run `MSW-V2` and `MSW-V3` in a fresh session
and report Seam 3 from there**, for the role-conflict reason at the top of this note rather
than for budget.

**And I would seriously consider adding one measurement before Task 11**, though it is the
owner's to authorise because it costs time: `MSW-V4` bounds what the router *adds up* and
explicitly does **not** bound what it *chooses*. Nobody has run a single journey on this
artifact. The analyst named the measurement that would settle it — paired `find_journey` runs
over a fixed pair set at k ∈ {1, 10, 20} under both percentile columns, with paths decoded —
and stopped rather than widening its own scope, which was right. **The question "do the
journeys actually change?" is currently open and is the most decision-relevant thing not
measured.** `MSW-V3` partly touches it by hand but is not designed to answer it.

## Anything in flight

**Nothing.** The `ml-graph-analyst` dispatch completed and its output is committed. No
background jobs, no half-written directories, no servers, no uncommitted files.

## Owed, and by whom

- **Owner:** nothing until Seam 3, which is **after Task 10** and remains an OWNER STOP before
  any default flips. The Option A recalibration decision is taken and recorded.
- **Next session:** `MSW-V2`, then `MSW-V3`, then the Seam 3 report. **B2 (reachability), B3
  (vacuous-test spot check) and B4 (prose-versus-code) travel with the work** — they were
  deliberately not run here because they want a finished artifact and Task 10 is half done.
- **Task 11 Step 0, non-negotiable and unchanged:** era-pin `cap_strategy="mutual_knn"` **and**
  `require_fame=False` in `grt_score.py`, `calibrate.py`, `cre_build.py`, and correct
  `CLAUDE.md`'s Graph shape section in the same commit. **Note this now has a fourth sibling**
  — `builder/analysis/2026-07-23-acceptance-bounds/check.py` is already era-pinned, done here,
  and needs nothing further.
- **Unchanged and not `MSW-`:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl
  extension; `ULC-F4` (keep-check name resolution) is its own track; `ULF-3`'s first half is
  satisfied by Task 12, so the next closeout must **re-test** it rather than copy it forward.
