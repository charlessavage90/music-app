# Handoff — the `CRE-` run, Stage 0 and Stage 1 complete (Seam 1), 2026-08-03

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-03-HANDOFF-cap-reeval-exec-plan.md`](2026-08-03-HANDOFF-cap-reeval-exec-plan.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a SEAM handoff**, taken at the execution plan's own **Seam 1** (after
`CRE-T7`) — a boundary chosen at authoring time, not discovered. Nothing is in flight, no
port is listening, no background job survives this session, the tree is clean and pushed,
draft **PR #70** carries the branch `cap-reeval-run`. Reasoning:
[`2026-08-03-cre-run-execution-log.md`](2026-08-03-cre-run-execution-log.md) §1–§7.

## The next session's work: `CRE-T8`

Continue
[`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md)
at **`CRE-T8`**, on the existing `cap-reeval-run` branch, inline on Opus (the owner's
model and execution-mode ruling, 2026-08-03). The prereg governs wherever the plan
disagrees. Six committed JSONs are the entire handoff and can be read cold:
`cre_d3.json`, `cre_d1.json`, `cre_screen.json`, `cre_builds.json`,
`cre_build_gate.json`, `cre_s2_degeneracy_gate.json`.

**The eleven graph cells are gitignored `.bin` files under `builder/scratch/cre-cells/`.**
They survive in this working tree but are in no branch and no backup. Their sha256s are in
`cre_builds.json`; if the tree is lost, `cre_build.py --all-nontag --tag-cells` rebuilds
them and the shas must match (determinism is measured, §5).

## Claims that must not be reverted

1. **`CRE-D1` fired `not_supported`, and its consequence is binding.** The three
   `(D1-branch)` cells — `B-S2-P0`, `E-S2-P1a`, `B-S2-P1a` — **do not exist**, and no
   router-side tag pricing arm does. `E-S2-P0` is branch-proof and runs. `cre_build.py`
   reads this branch from `cre_d1.json` at run time rather than hard-coding it; keep it
   that way.
2. **`CRE-D3` fired `inert_as_expected`, so `CRE-R0`'s wording is already constrained.**
   The `consequence` field carries §4's sentence verbatim. Do not re-word it into an
   undifferentiated joint null, and **do not re-run `CRE-D3` to "check"** — it is a
   committed Stage-0 prior.
3. **Four defects in the plan's own code were corrected, not worked around**, each
   recorded with its reasoning: an import-order trap that made `cre_ladder` unimportable,
   two wrong API calls in the build harness (`ListenBrainzSource` is config-bound; `Graph`
   carries `artist_count`/`edge_count`), and a `SCRATCH` path that wrote outside the
   gitignored tree. Do not "restore" any of them to the plan's literal text.
4. **The plan's motivating case for the `S2` tuple key is not constructible, and the
   replacement is stronger.** A search over 2,000,000 adjacent doubles found no IEEE
   product collapse at the 0.15 constant. The test uses agreement measured at exactly 0 on
   every edge instead — which ties the first key element on *all* edges rather than a rare
   pair — with a red half proving a bare product key gives a different result. Do not
   replace this with the plan's original example; it cannot be made to fire.
5. **`CRE-D1`'s aggregation follows the prereg's words, not `cre_probe3b.py`.** The probe
   pools each band and takes a median with no size-matching; §4 requires size-matched
   per-cell means. Plan pin 5 says the words govern. The probe's form is recomputed
   alongside as `probe_form_pooled_median_difference` and reproduces §9's disclosed +0.08 —
   **that agreement is corroboration of the harness and must not be deleted as redundant.**
6. **The `CRE-C6` × `CRE-D3` cross-read is BARRED** — they were measured on different
   substrates (`D3` on the adopted artifact per §3.3's carve-out; `C6` on the cleaned
   cells). It is written into the log *before* any sweep figure exists precisely so it
   cannot later be assembled as though it had always been the plan.
7. **No `CRE-R` read is licensed by this branch and none has been made.** Nothing is
   adopted, no criterion is evaluated, no blind listen is spent.

## Owed at Stage 2 — four items, each with its address

1. **Liveness check on the unmeasured-class counters.** Plan pins 2 and 3's counters
   (`interiors_null_in_snapshot`, `interiors_absent_from_snapshot`,
   `null_interior_unbypassable`) ran at Stage 0 and counted **zero everywhere**, because
   every `ALG-E` interior was ruler-measured. **Their green is not evidence they work.**
   *Condition:* discharged when a sweep on an `ALG-B` or `UC` cell produces a non-zero
   count, or — if they stay zero there too — when that zero is shown to be the true value
   rather than a dead counter.
2. **The affine `pop_raw` map applied.** Three comparisons are measured **not**
   `pop_raw`-comparable: `E-S1` vs `E-S0`, `B-S0` vs `E-S0`, `B-S1` vs `B-S0`. Their maps
   are two floats each in `cre_screen.json`'s `affine_pop_raw_report`. *Condition:* no
   cross-cell `pop_raw` sentence is written for those three without applying the map, or
   the sentence is not written. Note `B-S0` vs `E-S0` is the data-set-isolated cell that
   already carries §0.4's confound rows.
3. **`S2` share quoting.** Any `CRE-C5` attribution on an `S2` cell must quote both the
   labelled-node share and the ≥ 2-measured-agreements share (analyst M8's licensing
   constraint; both are in each `S2` manifest). *Condition:* discharged at T11 when the
   figures are stored beside the attribution field, or when no `S2` `C5` attribution is
   made.
4. **The barred cross-read** (claim 6). *Condition:* discharged only if it can be made
   within one substrate; otherwise it stays barred permanently and the findings note says
   so.

## Already updated — do not re-edit

`docs/README.md` (new rows for this handoff and the run log; the exec-plan handoff's role
line marked superseded), the retained execution log through §7 and its Seam 1 section,
`TEST-QUEUE.md` (new N/A entry), and draft PR #70's body. **`NEXT.md` is rewritten at this
closeout.**

## What I know that is not in the durable record

- **Nothing load-bearing.** Every measurement is in a committed JSON; every decision,
  divergence and defect is in the run log §1–§7 with its reasoning.
- Two operational notes with no other home. **The instrument gate is much slower than the
  cell builds** (~2 min `ALG-E`, ~3.5 min `ALG-B`, because it runs both the mirror and a
  real `build_from_archive`) while a cell build is ~30 s; and **the `S2` tag cells are the
  expensive ones** at 4–8 minutes each, dominated by `masses()` and the per-node agreement
  lookups in the ceiling loop. Budget Stage 2 accordingly. Both are measured, not
  estimated.
- The `--s2-shares` filler path exists because I added analyst M8's second share **after**
  building the three tag cells. It recomputes from the built artifacts. It is idempotent
  and skips cells that already carry the field; a future run of `--tag-cells` writes the
  field directly and never needs it.
