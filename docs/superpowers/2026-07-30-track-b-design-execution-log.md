# Track B design execution log — LBS semantics, plan, harness, pre-registration

**Role: ACTIVE — the retained execution log for Track B's design phase** (source
semantics → plan → `CB-1`–`CB-3` instruments → `CB-4` pre-registration, all
2026-07-30, one session, retired at the plan's named seam). The **runs** (`CB-5`) and
**reads** (`CB-6`) are NOT part of this record; a successor session owns them.
Figures: `builder/analysis/2026-07-30-track-b-cap-selection/` (gate and probe JSONs)
and `builder/analysis/2026-07-30-lb-source-semantics/`; cited here, never restated.
Branch `lb-source-semantics`, PR #51.

## §1 Decisions, with reasoning

- **The track was widened from k-tuning to cap-RULE selection, by the owner** — his
  grounds (requirements post-date the cap; the project is data-driven now) and the
  record's (`SYN-6`, `CS-P0f`, `BTF-4`) are in the plan's §0, with his three scope
  rulings. The degree bound is a scoping constraint of this track, **not** a settled
  product conclusion; re-evaluating bounded-degree is open, his trigger, owes a listen.
- **`LBS` was written before the plan** because `contribution` — the one token
  separating `ALG-B` from production — had no definition anywhere, and the Track B
  design should cite settled semantics rather than re-derive them. Source outranked the
  staff forum comment and corrected it twice (`LBS-5`/`LBS-6`).
- **Own mid-stream retraction, recorded deliberately:** on the `ALG-C` list-length
  check this session first announced "decisive — `limit` is not list length," then the
  upstream docstring's "instructive only, upto 2x" clause reversed it. The lesson is
  the project's standing one: a decisive-looking empirical read was wrong because the
  mechanism had a documented caveat nobody had read yet. Corrected before anything was
  committed; the findings note records only the corrected reading.
- **`banded_quota` exists because both proposed trim keys provably fail.** The
  consultant proposed the trim key as load-bearing (item 2) and offered
  popularity-proximity as an alternative; the `CB-P1` probe plus `CS-P0f` symmetry
  showed weakest-first **provably** deletes every reverse-only famous→obscure edge, and
  the proximity trim deletes the same edges for a different reason (largest fame gap by
  construction). The stratified quota — the consultant's other alternative — is the
  only trim that can retain them; implemented with `q = 0.2` as a **fixed design
  constant, not an axis** (sweeping it is a follow-up only if `CRS-R2` fires).
- **`proximity_select` keeps the both-ways mechanism and swaps only the ordering key**
  — the BTF reference applies its key to a union its ≤20-entry source lists happen to
  bound; a union here is unbounded (`CB-P1`: 12,776 sub-decile listers for Radiohead
  alone). Key pinned from the reconstruction: `|Δpop|` ascending.
- **One weight set** (production `ApiConfig()` defaults) for every path read —
  `w_degree_hub = 0.0` is a dormant term whose inertness a cap change removes, and the
  clean resolution is pre-commitment, not a second weight axis (that is the router-side
  future track).
- **`top1pct_degree_mass_frac`, not `top1pct_degree_frac`,** for graph-level hub mass:
  the shorter name is already a *path* metric (`builder/analysis/README.md`), and
  reusing it would be the §2.6 currency collision. Caught while implementing `CB-2`,
  after the plan had used the wrong name; plan annotated in place.
- **Identifier series:** `LBS-` (findings), `CB-`/`CB-P` (plan tasks/design probes),
  `CRS-` (prereg) — each grepped free before first use.

## §2 The two consultant rounds — all eight items verified before adoption

**Round 1 (pre-`CB-4`), three items:** item 1 confirmed against `CS-P0c`'s own text
(its bar scopes rules choosing from a node's **own** list; the union family widens the
set) and quantified by the new `CB-P1` probe — superstars have thousands of
reverse-only sub-decile listers each, so the bar does not transfer. Item 2 confirmed
and **upgraded from labelled inference to checked premise**: reverse-only edges score
below the target's own-list tail in all 10 rows, both archives (`ALG-B` margins tight —
1497 vs 1532 — exactly what truncation-at-100 predicts). Item 3 adopted as
pre-registered criterion `CRS-C6` rather than left descriptive, because it bears on the
`ALG-B` adoption input and deciding its status after seeing the number is what the
prereg prevents.

**Round 2 (post-commitment, pre-scoring), five items, recorded as `CRS-A1`–`A5`:**
both blocking items were real — the path harness could not express `CRS-C5`, `R2`'s
subset, or `G3`'s per-band readability (`draw_pairs` discarded pair class;
`route_sample` pooled everything), and `C5`'s "structurally zero" baseline claim
over-reached the drawn pool. On the second, the record made the consultant's point
*stronger*: `CS-P0b`'s series has even the top-0.1% band only 87.5% zero-downward, so
no band pool inherits the superstars' zero and the baseline is now measured first,
per class, with any nonzero class's bar fixed blind by a further §8 entry. `CRS-A4`
(the `MK100`-vs-`TUw-100-100` reciprocity isolation — at k = 100 the mutual rank test
is vacuous per `LBS-3`) was verified against `mutual_knn_cap`'s semantics and promoted
to read `R1a`; it is the grid's cleanest expression of the owner's original concern.
`CRS-A5`'s live-endpoint claim was **not** independently verified — treated as report,
gated on one re-verifying request at scoring time, descriptive only.

## §3 Gate outcomes — all passed, none worked around

| Gate | Outcome |
|---|---|
| `CB-1` identity, green | `mutual_knn(k=50)` reproduces **both** reference builds byte-for-byte (sha256, nodes, edges) — `GR-4`'s `ALG-E` and `GRT-P4`'s `ALG-B` |
| `CB-1` red | `k=49` changes the sha |
| `CB-1` bound check | all four selectable configurations hold max degree at exactly 50 on real builds (`cb_bound_check.json` + the `banded_quota` run) |
| `CB-2` | reproduces the published `GRT-P4` figures on both reference builds — every tracer degree, both stranding shares, both exclusion rates |
| `CB-3` green | routing deterministic; every path a valid walk in its own CSR; class labels present end-to-end (added at `CRS-A1`) |
| `CB-3` red | paths move under `w_sim = 0` (16/20 pre-rework, 18/20 post) |

## §4 Defects found in this session's own output

1. **The plan named a metric that collided with an existing currency**
   (`top1pct_degree_frac`) — caught at implementation, §1 above.
2. **The plan's `CB-3` known-journey gate had no offline analogue** (the pattern it
   cited compares two live systems). Substituted stronger checks — per-edge walk
   validation against the CSR plus an unrequested red half — and annotated the plan.
3. **The harness could not produce three pre-registered quantities** (`CRS-A1`,
   blocking) — caught by the consultant's file-level read, not by this session, after
   this session had run the gate green twice. The gate checked determinism and
   validity; nothing checked *expressiveness against the criteria*. Transferable
   lesson: an instrument gate should include "can the output state every
   pre-registered quantity" as a mechanical column.
4. **The prereg asserted a structural zero for a pool it never measured** (`CRS-A2`,
   blocking) — the citation was real but scoped to five superstars, and the drawn pool
   was two bands. Same shape as the project's standing "confident prose about correct
   code" failure, in a pre-registration.

## §5 Corrections to the prior record

- The staff forum comment's parameter definitions are corrected twice by source
  (`LBS-5`/`LBS-6`): `session` is **seconds** (300 s = 5-minute gap, not "300
  minutes"), and the per-pair cap is `contribution` (per **user**), not a per-session
  50. The algorithm-selection handoff's open note that the forum's `contribution`
  mapping "does not cleanly match" is **resolved** by `LBS`.
- `NEXT.md`'s closed-enum item ("do not propose raising the candidate-list length")
  **stands**, with its mechanism now precise: `limit` is the instructive top-N, and
  the observed ceiling is 100 in every arm (`LBS-3`).
- The `rc_raw_records.json` re-scoring deferral is **discharged by supersession** —
  both full archives are on disk, so the 200-artist re-score answers a strictly weaker
  question than the cells answer directly (prereg §0).

## §6 Operational measurements with no other home

- A full-archive scan (75k responses, parse + match) runs ~2–3 minutes per archive;
  the `CB-P1` probe over both archives fits in one background run.
- Variant builds via the harness: ~30 s (`ALG-E` mutual) to ~90 s (`trimmed_union`,
  which symmetrises the union before trimming). The 24-cell grid is well under an hour
  of compute.
- `builder/scratch/cb-cells/` now holds gate/bound-check cell artifacts with manifest
  sidecars (sha256 in each) — gitignored, regenerable, deterministic.

## §7 Decided against, with reasons

- **Proximity-trim cells** — provably blind to the DD-F1 edges (both trim keys delete
  the same reverse-only set); the proximity idea is covered by `proximity_select`.
- **A `q` axis on `banded_quota`** — one fixed value until `CRS-R2` fires.
- **A second path-weight set** — the router-side remedy is a separate future track.
- **Re-verifying the consultant's popularity endpoint now** — one request at scoring
  time is when it matters; descriptive either way.

## §8 Closeout record

- **A4 (default-flip):** no knob added anywhere; analysis-only by design.
  `BuilderConfig` and `ApiConfig` untouched — verified by `git status` over
  `builder/src`, `api/src`, `frontend/src` (empty).
- **A5:** no listeners on 8000/5173/8138/8139; this session started no servers.
- **B2 (reachability):** the five new analysis modules follow the established
  standalone-probe pattern; `cb_metrics`/`cb_paths`/`cb_p1` import from
  `cb_build_variants` and `cb_metrics` deliberately. Not orphans.
- **B3 (vacuous tests):** no pytest tests added. Every instrument gate carries a red
  half, and each red half has been observed to fire (§3) — which is the same check in
  the form this work needed.
- **B5:** `.claude/` grepped for LB parameter semantics, cap-rule claims and the new
  quantity names — nothing there restates them. `CLAUDE.md`'s hub/currency row and
  `ml-graph-analyst` describe the production graph, which this track did not change.
- **D3 (provenance):** the two reference builds' sha256s are recorded in the committed
  gate JSON and their manifest sidecars; every future cell writes a manifest with its
  sha beside the gitignored `.bin`.
- **D4:** suites run at closeout, not recalled — builder **129 passed**, api **217
  passed, 1 warning**, frontend **107 passed** (18 files). One process note for the
  record: this log's first draft wrote these counts (and D6's) from memory before the
  commands ran — the exact failure D4 names. Caught in the same session; the numbers
  here are from the run, and D6's draft figures were wrong.
- **D6:** unconditional layer **44,183 characters**; conditional **2,154 lines**.
  Against the most recent recorded figures (44,113 / 2,121, algorithm-selection
  closeout §10): **+70 characters and +33 lines, none session-authored** — this track
  added nothing to `CLAUDE.md`, `memory/`, or any skill/agent description; the deltas
  match the owner's own `MEMORY.md` deploy-traps edit observed at session start.
