# Handoff — the `CRE-` run, Seam 3: criteria figures computed, 2026-08-04

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-03-HANDOFF-cre-run-stage2-midflight.md`](2026-08-03-HANDOFF-cre-run-stage2-midflight.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a SEAM handoff, not mid-flight.** `CRE-T11` was the execution plan's last task
and Seam 3 is reached. The plan is fully executed and now declares itself so. Branch
`cre-t11-scoring`, draft **PR #72**. Tree clean and pushed; **nothing is in flight** — no
background job, no dispatched subagent, no partial directory, no listener on any of the
four ports.

**Which branch to work on — check, do not assume.** If **PR #72 has merged**, branch fresh
off `main`. If it has not, branch off `cre-t11-scoring`. `git log --oneline -1 main`
settles it in one command. Written conditionally on purpose: a handoff cannot know when
the owner presses merge, and the Seam 1 handoff named a branch its own PR merged out from
under it.

## The next session's work: the Stage-3 findings note

**It must be written by a session that did not run the sweeps** — the plan's own
§"What is NOT in this plan", and the reason this seam exists. Source is
[`cre_scores.json`](../../builder/analysis/2026-08-03-cap-reevaluation/cre_scores.json)
plus the pre-registration, **never any session's memory or any prose summary of the
result**, including this handoff's. Reasoning:
[`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md) §13–§14.
Governing document is the prereg,
[`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md);
the operational plan is
[`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md),
**the prereg governing wherever they disagree**.

**What the note owes, all fixed in advance:** the four-part shape (`CLAUDE.md`, "How to
present results"); every identifier carrying the plain sentence §5 fixed for it **before
any result existed**, quoted rather than re-worded; the summary naming whatever cuts
against it; and `CRE-R` reads under §6's wording constraints. **Read §6 itself rather than any
summary of it, this one included** — it fixes `CRE-R0`'s constrained wording, `CRE-R4`'s
three-part clear-winner rule, and a closing list of standing bars on *every* read. An
earlier draft of this handoff enumerated four of those five bars, which is how a
restatement silently narrows a constraint.

**This handoff deliberately does not characterise the figures, and neither should any
summary the successor reads before opening the JSON.** That is the whole point of the seam.

## Claims that must not be reverted

1. **All Seam 1 and Seam 2 claims stand unchanged**, and are not restated here. In
   particular `CRE-D1`'s `not_supported` branch still binds (the three `(D1-branch)` cells
   **do not exist**, and are marked `branch_excluded` rather than unrun in the run-state
   map — reverting that would bar every read for cells the design deleted), `CRE-D3` must
   not be re-run, and the `CRE-C6` × `CRE-D3` cross-read is still barred.
2. **The scorer loads graph artifacts, and that is correct.** The Seam-2 handoff said T11
   needs none; that holds for `CRE-C1`/`CRE-C4`/`CRE-C5` and is **false for `CRE-C2`**, whose primary
   reference the prereg fixes as the production artifact's top-degree set and whose
   own-graph share needs each cell. No degree set is committed anywhere. Do not "restore"
   a figures-only input list — the plan contradicts itself here and the prereg governs.
   Log §13, correction 1.
3. **`interiors_absent_from_snapshot` is `live_but_unfired`, not structurally
   unexercisable.** The Seam-2 position was the opposite and its premise does not hold.
   Do not revert to it. Log §13, correction 2.
4. **The run-state map reads the `branch` key, not `outcome`.** `cre_d1.json` and
   `cre_d3.json` have no `outcome` key; reading one returns `None` silently and reports
   `cre_r_readable: false` on a complete run. A test asserts both directions.
5. **The uniform drop is computed from committed `infeasible_cells`, never re-derived**
   from the ladder (padding is not infeasibility). A test asserts it, and it goes red when
   broken.
6. **`cre_scores.json` contains no verdict sentence, and that is deliberate**, not an
   omission to be helpfully filled in. `CRE-R3`'s shape is stored as a boolean flag; the
   `w_floor` guard stores magnitudes plus a conservative flag and fixes no threshold.
7. **No `CRE-R` read is licensed by anything in this session, and none has been made.**
   `cre_r_readable: true` is the §6 *run-state precondition* — it says no unrun cell bars a
   read. Nothing is adopted; the blind listen (`REQ-38`) is unspent.

## Owed — one open, two discharged, one standing

1. ~~**Liveness on the unmeasured-class counters.**~~ **FULLY DISCHARGED 2026-08-04.** The
   null half was discharged at Seam 2; the absent half is settled here by set-difference
   over all eleven cells. Figures in `cre_scores.json`. Nothing further owed.
2. **The affine `pop_raw` map applied.** **Not yet due, re-tested rather than re-listed.**
   Three comparisons are not `pop_raw`-comparable (`E-S1` vs `E-S0`, `B-S0` vs `E-S0`,
   `B-S1` vs `B-S0`); maps are in `cre_screen.json`'s `affine_pop_raw_report`.
   `cre_scores.json` makes **no cross-cell `pop_raw` sentence**, so nothing has yet needed
   the map. *Condition, unchanged and now inherited by the findings note:* no cross-cell
   `pop_raw` sentence for those three without the map, or no sentence.
3. ~~**`S2` share quoting.**~~ **DISCHARGED by branch, 2026-08-04.** The obligation attached
   to a `B-S2` cell; `CRE-D1` fired `not_supported`, so no such cell exists. Recorded in
   `cre_scores.json` as an explicit note rather than by omission.
4. **The barred cross-read** (`CRE-C6` × `CRE-D3`). Unchanged, still barred.

**Two new deferrals, each with a condition.**

- **The `--out` argument row** the plan named for this table. `cre_score.py` takes **no**
  command-line arguments and routes every path through `in_dir()`'s bare-filename rule, so
  the traversal class is closed by construction for this module. *Condition:* discharged —
  accepted, won't fix, because there is nothing to fix here.
- **A pre-existing Snyk LOW path-traversal in `cre_sweep.py`** (`argparse` value flowing
  into `load_cell`), unrelated to this task and present since T9. Not fixed here: editing a
  frozen harness after its sixteen result JSONs are committed buys a LOW severity finding
  at the cost of the provenance those results rest on. *Condition:* fix if `cre_sweep.py`
  is ever re-run for new results, or close as accepted when the `CRE-` track completes.

## Anything the owner said that is not yet in a file

**Nothing.** The only owner input this session was the instruction to start, and one
question about task ordering — answered in-conversation and folded into §13's structure
(the counter check belongs inside T11's run-state map, not sequenced beside it, because
the Stage-3 session is figures-only by design and structurally cannot run it).

## Already updated — do not re-edit

The retained log (§13, §14), this handoff, the previous handoff's role line (marked
superseded on next actions), `NEXT.md`, `TEST-QUEUE.md` (new N/A entry), `docs/README.md`
(row for this handoff; the plan's role changed to COMPLETE; the Seam-2 handoff's row
marked superseded), the execution plan's own role line, and draft PR #72's body.
