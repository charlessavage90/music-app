# Handoff — the `CRE-` Stage-3 findings note, 2026-08-04

**Role: ⚠ SUPERSEDED 2026-08-04 (evening) on next actions by
[`2026-08-04-HANDOFF-gbl-plan.md`](2026-08-04-HANDOFF-gbl-plan.md)** — the owner took the
decision this handoff said was his (findings §4 **Option A**: a blind listen on the gentle
arm), and the `GBL-` spec and plan now exist. Remains authoritative for the `CRE-`
experiment's internals and its claims-not-to-revert. *(Original role:)* **ACTIVE — this is
the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-04-HANDOFF-cre-t11-seam3.md`](2026-08-04-HANDOFF-cre-t11-seam3.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff, not mid-flight.** Stage 3 was the last stage of the `CRE-`
experiment, and it is complete: the findings note is written, committed and classified.
Branch `cre-stage3-findings`, draft **PR #75**. Tree clean and pushed; **nothing is in
flight** — no background job, no dispatched subagent, no partial directory, no listener on
any of the four ports.

**Which branch to work on — check, do not assume.** If **PR #75 has merged**, branch fresh
off `main`. If it has not, branch off `cre-stage3-findings`. `git log --oneline -1 main`
settles it in one command.

## The `CRE-` experiment is complete. The next action is the OWNER'S.

**Nothing is owed by any session.** All four stages ran, every criterion is computed, every
read is determined, and the results document exists. What remains is a decision, and the
decision is his: which of the two passing arms (if either) is worth a blind listen, and
whether the candidate data set's advantage is worth the re-crawl it implies.

**Entry point for anything `CRE-`:**
[`findings/2026-08-04-cap-reevaluation-results.md`](findings/2026-08-04-cap-reevaluation-results.md)
— **AUTHORITATIVE for the results**, four-part shape, options in §4. Raw record is
`builder/analysis/2026-08-03-cap-reevaluation/cre_scores.json`; cite one of those two for
any `CRE-` number and restate neither. Reasoning:
[`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md) §15–§16.
Governing document remains the prereg,
[`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md).

## Claims that must not be reverted

1. **Every Seam-1, Seam-2 and Seam-3 claim stands unchanged**, and is not restated here.
   In particular `CRE-D1`'s `not_supported` branch still binds (the three `(D1-branch)`
   cells **do not exist** and are `branch_excluded`, not unrun), `CRE-D3` must not be
   re-run, the `CRE-C6` × `CRE-D3` cross-read is still barred, and `cre_scores.json`
   contains no verdict sentence **by design** — that is not an omission to be helpfully
   filled in.
2. **`CRE-R2` fires for two arms and `CRE-R4` finds no clear winner.** These are not in
   tension: `CRE-R4`'s clause (i) fails precisely *because* two arms pass, each being the
   other's counterexample to the "no other non-staged arm meets them anywhere" disjunct.
   A future reader who "fixes" this by promoting one arm has misread clause (i).
3. **§0.4's censoring trigger is a reporting constraint, not a firing condition.** It does
   not bar `CRE-R2`; it forbids either arm's `CRE-C1` being called a clean pass. Both
   readings — treating it as a bar, or dropping it — are wrong, in opposite directions.
4. **`B-S1-P1b`'s matched-only comparison is UNREADABLE, not favourable.** Its matched set
   is below the readable-pair floor. Do not quote its matched-only figure as a second pass;
   the floor exists so that a small favourable subset cannot be read as corroboration.
5. **`E-S1-P1a`'s `CRE-C4` failure does NOT fire `CRE-R3`.** `CRE-R3` requires a `CRE-C1`
   pass alongside the `C4` fail, and that cell fails `CRE-C1`. It is reported as a payload
   cost, not as descent-by-deletion.
6. **`CRE-R4` clause (ii)'s paired lead was computed at Stage 3 and is not in
   `cre_scores.json`.** It is labelled as such in the findings note. Do not go looking for
   it in the raw record and conclude the record is incomplete.
7. **"Arm" in `CRE-R4` means a CELL, one row of §0.2 — and the pre-registration is
   genuinely ambiguous about it.** Its clause (iii) ("explored on no fewer ramp settings
   than any arm it beats") presupposes an arm carrying several ramp settings, which a cell
   cannot; every criterion that produces a number treats an arm as a cell. **Resolved as
   arm = cell** — findings note §1.6, execution log §15 — because every scoring criterion is
   per cell, §0.2 gives each cell the isolating baseline clause (i) compares against, and the
   alternative is incoherent (it would need `B-S1` to pass and fail simultaneously). **Do not
   re-resolve this the other way**: doing so satisfies clause (i)'s second disjunct and
   manufactures a clear-winner call the experiment does not support.
8. **Nothing is adopted; the blind listen (`REQ-38`) is unspent.** No default changed, no
   shipped code touched, no graph artifact built or adopted by this session.

## Owed — one open, one discharged

1. ~~**The affine `pop_raw` map applied.**~~ **DISCHARGED 2026-08-04** by its second
   branch: the findings note makes **no cross-cell `pop_raw` sentence at all**, every
   gradient figure in it being in `fame_lb_pctl`. Struck in place in the Seam-3 handoff.
   Nothing further owed.
2. ~~**A pre-existing Snyk LOW path-traversal in `cre_sweep.py`** (`argparse` value flowing
   into `load_cell`), present since T9 and untouched by Stage 3. *Condition, unchanged:*
   fix if `cre_sweep.py` is ever re-run for new results, or close as accepted when the
   `CRE-` track completes. **That second branch is now arguably due** — the track has
   completed — so the next closeout that touches this should either close it or say why
   not.~~ **CLOSED AS ACCEPTED 2026-08-04 (evening), by the condition's second branch: the
   `CRE-` track is complete.** The first branch is not triggered by the `GBL-` blind-listen
   harness: it imports pure functions from `cre_sweep.py` (`config_for`, `ladder_excludes`)
   and never re-runs its CLI, and every `load_cell` argument in `GBL-` code is the literal
   `"B-S1"`, never user input. Revival condition: any future re-run of `cre_sweep.py
   --cell` for new results re-opens the fix branch.

## Anything the owner said that is not yet in a file

**Nothing.** The only owner input to this session was the instruction to proceed after
`session-start`.

## One thing flagged to the owner that is not a `CRE-` item

**Eight `QUEUED` entries in `TEST-QUEUE.md`, dated 2026-07-22 to 2026-07-27, have never
been marked DONE** (the capfix adoption, the tie-break rename guards, four playback/clip
checks, the search box, and the first-real-run entry). Some are plausibly overtaken by the
2026-08-02 discharge, which covered the live site and the iPhone script — but the queue
records nothing to that effect, and inferring it would be exactly the kind of guess the
queue exists to prevent. Raised, not acted on; whether any is still worth running is the
owner's call.

## Already updated — do not re-edit

The retained log (§15, §16), this handoff, the previous handoff's role line (marked
superseded on next actions, with its discharged deferral struck in place), `NEXT.md`,
`TEST-QUEUE.md` (new N/A entry), `docs/README.md` (row for the findings note; row for this
handoff; the Seam-3 handoff's row marked superseded), and draft PR #75's body.
