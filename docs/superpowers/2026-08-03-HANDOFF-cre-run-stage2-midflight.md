# Handoff — the `CRE-` run, Stage 2 gates and all sixteen sweeps, 2026-08-03

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-03-HANDOFF-cre-run-seam1.md`](2026-08-03-HANDOFF-cre-run-seam1.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a MID-FLIGHT handoff.** `CRE-T10` is complete but Seam 3 is not reached —
`CRE-T11` remains. The retirement was triggered by **context budget**, on the owner's
observation, **not by the degradation tell**: no figure had to be asked for twice, no
tracking item was dropped, and no firm claim was revised under questioning. The successor
should still cold-read this back before acting on it (`session-start`).

Branch `cap-reeval-stage2`, draft **PR #71**. Tree clean and pushed; **nothing is in
flight** — no background job, no dispatched subagent, no partial directory, no listener on
any port.

## The next session's work: `CRE-T11`

Continue
[`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md)
at **`CRE-T11`** — criteria figures, the uniform drop over pin 9's partition, and the
run-state map, then SEAM 3. The prereg governs wherever the plan disagrees. Reasoning:
[`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md) §9–§11.

**Everything T11 needs is committed and readable cold.** Sixteen `cre_sweep_<cell>.json`
files (nine `ALG-E`, seven `ALG-B`) plus `cre_gates.json`. Each sweep JSON carries its
cell's `artifact_sha256`, supply/pricing coordinates, `pop_log_low/high`, per-pair
per-depth journeys with stop kinds, interior MBIDs **with their `fame_lb_pctl` values**,
per-term `CRE-D2` shares, the two unmeasured-class counts and pin 3's counter, and the
cell's infeasible set. **T11 needs no graph artifact** — that was deliberate, so the
figures-only scorer stays figures-only.

## Claims that must not be reverted

1. **All Seam 1 claims 1–7 stand unchanged** and are not restated here. In particular
   `CRE-D1`'s `not_supported` branch still binds, `CRE-D3` must not be re-run, and the
   `CRE-C6` × `CRE-D3` cross-read is still barred.
2. **`CRE-G1`(a) carries a red control that the plan did not specify.** Do not remove it
   as unrequested: an identity gate is the shape that passes vacuously, and this plan has
   produced that defect twice.
3. **`assert_cost_decomposition` runs on `P0` cells too**, and is deliberately **not**
   called `CRE-G2`(b) — that identifier is pre-registered for the `P1` device test. Do not
   merge the two names.
4. **`walk_journey`'s trailing `(None, "none")` entries are PADDING, not measured
   infeasibility.** Each pair carries `walked_depths` and `termination`; the
   `infeasible_cells` set counts only depths the ladder reached. **A uniform drop computed
   off the raw ladder would drop pairs that were never infeasible.**
5. **The exclusion ladder in each sweep is reconstructed, and the reconstruction is
   checked** — every reconstructed exclusion is asserted absent from its own and every
   later interior. Do not replace the check with an assumption of determinism.
6. **`cre_tags.agreement_table` is keyed on `(kind, n_artists)`.** Reverting to a
   `kind`-only key reintroduces a silent wrong-idf defect that no current caller triggers.
7. **No `CRE-R` read is licensed and none has been made.** Nothing is adopted, no
   criterion is evaluated, the blind listen (`REQ-38`) is unspent.

## Owed — three items, plus one now half-discharged

1. ~~**Liveness on the unmeasured-class counters.**~~ **HALF DISCHARGED 2026-08-03.**
   `interiors_null_in_snapshot` is non-zero in all seven `ALG-B` cells and
   `null_interior_unbypassable` tracks it, so that counter is live and the Stage-0 zero was
   a true zero. **`interiors_absent_from_snapshot` is still zero in every cell of both data
   sets — that half remains owed.** *Condition:* discharged when the zero is shown
   structural, or when the findings note states the counter as unexercised. **Do not read
   the null half's discharge as covering it.**
2. **The affine `pop_raw` map applied.** Unchanged, untouched. Three comparisons are not
   `pop_raw`-comparable: `E-S1` vs `E-S0`, `B-S0` vs `E-S0`, `B-S1` vs `B-S0`; maps are in
   `cre_screen.json`'s `affine_pop_raw_report`. *Condition:* no cross-cell `pop_raw`
   sentence for those three without the map, or no sentence.
3. **`S2` share quoting.** Unchanged. Any `CRE-C5` attribution on an `S2` cell quotes both
   the labelled-node share and the ≥ 2-measured-agreements share. *Condition:* discharged
   at T11 when stored beside the attribution, or when no such attribution is made.
4. **The barred cross-read.** Unchanged, still barred.

## Every number computed that is not written down

Only one set, from the scratch probe that checked whether `sim` contributing 0% was a
defect (it is not). The **2.09% of edges at similarity exactly 1.0** is in the log; the
rest of that distribution, measured on the E-S0 cell, is not recorded anywhere:

- similarity over all 802,364 edges: **min 0.339474, p50 0.531679, p99 1.000000,
  max 1.000000**.

Everything else computed this session is in a committed JSON: gate outcomes and the red
control in `cre_gates.json`, every sweep figure and per-cell runtime in the sixteen sweep
files. **Nothing was computed and discarded.**

## Everything decided against, and why

- **Re-running `journey` at every depth to verify the reconstructed exclusions** — sound,
  but it doubles ladder cost (~10 min on the two staged cells alone). Rejected for the
  exclusion-absence assertion, which ties the reconstruction to observable output at zero
  cost.
- **A red half for `CRE-G2`(a)** — rejected deliberately. Its failure direction is "nothing
  changed", so a dead comparison fails; it cannot pass vacuously, and a control there would
  be cost without a hazard.
- **Moving `load_cell`/`surviving_pairs` into `cre_common`** — rejected: it would edit a T1
  module after five tasks depend on it. `cre_sweep` imports them from `cre_gates` instead,
  which is why `cre_gates` has an inbound import and is not an orphan.
- **Naming the `P0` decomposition check `CRE-G2`(b)** — rejected on the identifier rule.
- **Continuing on `cap-reeval-run`** — rejected: PR #70 merged it into `main`. Branched
  fresh. The Seam 1 handoff's "inline on the existing branch" predates that merge.
- **Unit-testing the gates' runs rather than their decision rules** — rejected: the cells
  are gitignored and minutes to rebuild.

## Anything the owner said that is not yet in a file

- **He ruled `CRE-T10` should run before retirement**, overriding the standing "retire at
  the plan's remaining seams" instruction for this one boundary, on the grounds that T10 is
  the run that can discharge the counter-liveness item. **The standing ruling itself is
  unchanged.**
- **Four working notes from the retired Seam 1 session, relayed by him.** Two are
  discharged in code (the `cre_tags` cache; the restated-rule defect in the gate tests) and
  recorded in log §10. **Two are standing guidance with no other home:**
  - **Do not read `cre_screen`'s ladder runs as pre-validating `CRE-G1`(a).** The screen
    called `journey()` over 11 cells × 22 pairs with no failures; that is not byte-identity
    against production. If `G1`(a) ever fails, suspect the pin-8 journey semantics first —
    the masked re-run plus the `adjacent_only` fallback — not the `_dijkstra` copy.
  - **Expect the plan's code snippets to be broken, and find out by running them.** Tasks
    1–7 contained four such defects, all invisible to a name-resolution check that passed
    clean. Grepping that a name resolves checks neither arity, attributes, nor import
    order.

## The open decision, and what I would do

**Whether `interiors_absent_from_snapshot`'s zero is closed by proof or flagged as
unexercised.**

**I would attempt the proof, and I think it succeeds.** Pin 2 states the snapshot's key set
is exactly (adopted node set) ∪ (`ALG-B`-MK50 node set). Every built cell is a cleaned
subgraph of one of those two populations — the supply rules re-select edges, they do not
introduce nodes from outside the crawl. If that holds, **no cell can keep a node the
snapshot lacks**, the counter is correct and structurally unexercisable, and the honest
finding is that the absent class does not arise on any built cell rather than that it was
never checked. The cheap check is a set-difference of each cell's MBIDs against the
snapshot keys — minutes, no rebuild, and it settles the item either way. **If it fails**,
the counter is live-but-unfired and the findings note says so.

Do not read this as settled: it is my position, not a result, and I did not run the check.

## Already updated — do not re-edit

The retained log (§9, §10, §11), `docs/README.md` (row for this handoff; the Seam 1
handoff's role line marked superseded), `NEXT.md`, `TEST-QUEUE.md` (new N/A entry), the
Seam 1 handoff's owed-item 1 struck in place, and draft PR #71's body.
