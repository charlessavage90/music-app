# Handoff — the `JFX-` arms ran and the adoption plan is written, 2026-08-10

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-09-HANDOFF-jfx-amendment.md`](2026-08-09-HANDOFF-jfx-amendment.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The `JFX-` track is complete, its output is committed, and the successor
reads a finished result rather than a live understanding. **The degradation tell did not
fire.**

Reasoning: [`2026-08-10-jfx-run-execution-log.md`](2026-08-10-jfx-run-execution-log.md).
Figures: `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` — cited, never restated.
Branch `crawl-extension-design`, **PR #91**, commits `6cfef67`, `33b430c`, `1873ceb`.

---

## Start here

1. **Read [`plans/2026-08-10-cxa-graph-adoption.md`](plans/2026-08-10-cxa-graph-adoption.md)
   (`CXA-`) — it is the next piece of work** and it records the owner's adoption decision.
2. **Execute it INLINE, not with subagents.** Nine tasks, strictly sequential, zero
   independent — `CXA-G1` is deliberately a joint gate on Tasks 1 and 2 because they only
   prove correct together. Reasoning in the closing message of the previous session and in
   the plan's own doc-map row.
3. **Two OWNER STOPS: `CXA-S1`** (the bound values) and **`CXA-S2`** (go/no-go before
   production). Neither is a formality.

## What is done

The `JFX-` arms, in full: the diagnostic artifact, the routing harness `AM1.3` named but
nobody had written, 300 pairs × 2 arms × 4 depths, and every criterion computed.
`AM1.3`'s `CRE-G1(a)` precondition discharged. Two defects fixed with tests shown red first.
The `CXA-` adoption plan written and doc-mapped.

**Nothing adopted, no default flipped, nothing deployed. The live site is untouched and was
never in scope.** The new artifact is `builder/scratch/graph-cex-117k.bin`, gitignored, and
its manifest records `DO_NOT_DEPLOY: true`.

**⚠ Read [`2026-08-10-jfx-run-execution-log.md`](2026-08-10-jfx-run-execution-log.md) §4
before acting on any `JFX-` number.** It records a defect in this session's **own analysis
code** — `AM1.11` read 9's trigger was implemented from the amendment's *rationale* instead
of its *condition*, and would have silently suppressed a pre-registered read at the one depth
it fires. It was caught by re-reading the amendment against the output, not by any check.
The numbers in the figures README are post-fix; this pointer exists so a reader of the
handoff alone knows the run's execution quality was itself a finding.

## Documents that are now wrong, and in which direction

- **Anything reading the `G1b` ratio as "the new map's gradient is shallower".** It is a
  point estimate; the difference spans zero. Figures in the README. See "must not be
  reverted" below.
- **`TEST-QUEUE.md` on THIS BRANCH is stale**, not lapsed: PR #92's discharge of the
  2026-08-07 bypass-tray entry landed on `main` only, so this branch's topmost heading still
  reads `QUEUED`. **Reconcile at merge; do not discharge it again.** The queue is genuinely
  empty.
- **Local `main` is behind `origin/main`.** Harmless, but a `git log main` misleads.

## Claims that must NOT be reverted by a well-meaning editor

- **The shallower gradient is NOT established.** `G1b` tested against the 0.67 bar, never
  against parity; `D_B − D_A` spans zero. Adoption was taken with **no cost demonstrated**,
  not in spite of a measured one. Both halves travel together: this also does not establish
  that the gradients are equal.
- **The d20 famous-to-famous drift is POST-HOC** — three strata, three intervals, one clears
  zero. It is where to look, not a finding, and needs its own pre-registration to be a claim.
- **`AM1.11` read 9 fires at d20 and the gate still stays on the MEDIAN.** Promoting the mean
  would change what passes and is the owner's call, not a bookkeeping fix.
- **`JFX-B`'s manifest says `DO_NOT_DEPLOY: true` and that is CORRECT** — it was built against
  the old bounds. `CXA-` Task 3 produces a *new* build whose manifest records a pass. Do not
  edit the old manifest; do not deploy the diagnostic artifact.
- **`CRE-G1(a)` as originally run is evidence about the six static cost terms only** — it ran
  at k = 0 with the ramp knob at 0.0, doubly inert on the ramp. Do not cite it as covering the
  ramp; the `JFX-` re-verification is what covers that.
- **`w_known_ramp_fame_pctl` stays at 0.01** through the adoption.
- **The regenerated ALG-E drop payload must not ship** (`CEX-` recensus README).
- **Everything on the previous handoff's "must not be reverted" list still stands in full**,
  including `DD-F1` surviving in popularity currency and the 2026-07-29 defect ruling being
  open and his.

## Already updated — do not redo

The figures README (extended, and it is the figures owner for the run), the `CXA-` plan,
`docs/README.md`'s row for it, this log, `NEXT.md`, and the previous handoff's role line.
`manifest.py` and `jfx_stats.py` are fixed and committed with tests.

**`TEST-QUEUE.md` was deliberately NOT written to** — this session changed nothing the owner
can press. That is C1's correct discharge, not an omission.

## What I know that is not in the durable record

**Nothing of substance.** Everything went into the execution log, including the reversal in
its §3, this session's own analysis defect in §4, and its own misreporting of build progress
in §6.

One thing worth repeating because it will bite the successor: **`CXA-` Task 2 must repoint
`UNLISTENABLE_DROP_LISTS[CANDIDATE_ALGORITHM]`, not the `PRODUCTION_ALGORITHM` entry.** ALG-B
is the adopted lineage and is bound to the constant named *candidate*. Getting it backwards
half-applies another population's list, and `NoUnlistenableListForAlgorithm` will not catch
it — that raises when an algorithm is *absent*, not when it is *wrong*.

## Anything in flight

**Nothing.** No background jobs, no subagents beyond this closeout's `doc-auditor`, **no
listeners: ports 8000, 5173 and 5174 swept and free.** No dev server was started this session
and none was left behind — nothing queued needs one.

## Open, and not this session's

- **`CXA-`'s three deferrals with their conditions** — `SEL-R1`–`R4`, the rank-asymmetry idea,
  and the fourth acceptance artifact. All in the plan's §4.
- **`CEX-F1`**, **`CEXR-6`'s `load_deezer_ids` half**, **`CEX-R3`** (search), **`CLIP-1`**,
  **`FE-SNYK-1`** — unchanged, conditions in the `CEX-` Task 11 log §8. `FE-SNYK-1` is
  untouched: nothing here went near a frontend dependency.
- **The 2026-07-29 famous-to-famous defect ruling** — still open, still the owner's.
- **PR #92 is MERGED**; the landing-dot fix is on `main` but **not deployed**.
