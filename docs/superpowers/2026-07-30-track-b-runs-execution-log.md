# Track B runs — execution log (CB-5, CB-6)

**Role: ACTIVE while the track runs; retained afterward.** Governing plan:
[`plans/2026-07-30-graph-rebuild-track-b.md`](plans/2026-07-30-graph-rebuild-track-b.md)
(tasks `CB-5`, `CB-6`). Pre-registration:
[`specs/2026-07-30-track-b-cap-selection-preregistration.md`](specs/2026-07-30-track-b-cap-selection-preregistration.md)
(`CRS-`, amendments `A1`–`A5` in §8). Session: `track-b-runs-builder`, branch
`track-b-runs`, picked up at the `CB-4` seam from
[`2026-07-30-HANDOFF-track-b-design.md`](2026-07-30-HANDOFF-track-b-design.md).

Decisions and reasoning per task, appended as work lands. Figures cited from
`cb_scores.json` and the prereg — never restated in prose where a number could
drift.

## Orientation (session start)

- Seam handoff read; not mid-flight, so no cold-read-back owed. All artifacts the
  handoff names resolve on disk (prereg, plan, three gated modules, 4 pre-built
  cells with manifest sidecars, both archives, both reference builds, adopted
  artifact).
- The three order-sensitive obligations are tracked as explicit tasks: scorer
  dry-run first; `ALG-E`-`MK50`'s `C5` per class before any other cell's `C5`
  (`CRS-A2`); reads in `R0 → R1 → R1a → R2 → R3 → R4` order.
- Flagged to the owner at orientation: the 2026-07-28 QUEUED redesign test (with
  the iPhone script) is still undischarged. Not this track's work.

## CB-5a — the runner (`cb_run_cells.py`), committed before any cell ran

**What was built and why it is new code at all:** the three gated modules are
per-cell instruments; nothing scripted the grid, the pair draw, or four
prereg quantities that live above single cells — `CRS-C6` (survival split),
`CRS-H1` (tie prevalence), `CRS-H2` (quota-frame disagreement), `CRS-G2`
(bound verification), plus the `CRS-A5` re-verification. The runner
orchestrates and computes only those; every per-cell number comes from the
gated modules unchanged.

**Decisions worth recording:**

- **Phased CLI (`dryrun / build / ties / baseline / score`) so the `CRS-A2`
  ordering is structural, not remembered.** `--phase score` refuses to run
  before `cb_c5_baseline.json` exists. Other cells' `C5` values land in
  `cb_scores.json` unprinted and are first opened in the CB-6 reads.
- **`CRS-H1`'s operationalisation fixed in the docstring before any cell's
  ties were computed:** a binding cut is tied when the primary key of the
  last-kept and first-dropped candidates is equal — the MBID tie-break, not
  the key, decided the survivor. Prevalence = tied cuts / binding cuts.
- **The `trimmed_union` tie/quota instrumentation is a copy of the gated trim
  loop, not an edit** — editing `cb_build_variants.py` would re-trigger
  `CRS-G1`'s full gate battery for a descriptive column. The copy is not
  trusted: per cell, its surviving edge set must equal the built artifact's
  exactly, or the cell's H1/H2 numbers are marked unusable.
- **Builds run as subprocesses** so a `CRS-G4` exhaustion on an uncapped cell
  degrades to a diagnostic row instead of killing the sweep. 30-minute cap.
- **Kept the four gate-built cells** rather than rebuilding — the handoff
  allows either; byte-determinism is gate-proven.

## CB-5b — scorer dry-run on `ALG-E`-`MK50` (obligation 1) — PASSED

82 pairs at 0.37 s/pair, `no_path=0`, `invalid_walks=0`; structural output
reproduces the published anchors (exclusion 1.07 %, lower-half stranding
0.08 %); class labels, `C5` fields, `CRS-G3` readability flags, and the weight
set all present in the output. Shape checks all green. (This dry-run used a
provisional pair set restricted to the one cell; nothing from it is the scored
record.)

## CB-5c — instrument gates re-run at the scoring commit (`CRS-G1`)

`CRS-G1` says the gates pass *at the harness commit that scores cells*. The
runner is a new file, not an edit to any gated module, so the committed gate
outputs arguably still stand — re-run anyway, conservatively, and logged to
`cb5_gates.log`.

**All three PASSED, green and red halves**, at commit `997d7c4`: CB-1
byte-identical on both archives with the k=49 red half differing; CB-2 on the
published anchors for both reference builds; CB-3 deterministic, all walks
valid, class labels present, and 18/20 paths moved under `w_sim = 0`.

## CB-5d — all 24 cells built

20 built + 4 kept from the gate runs, all 27–37 s each (`cb5_build.log`).
**`CRS-G4` never fired**: both uncapped reference rows built in ~30 s — the
"unbuildable" branch and its degraded-diagnostics fallback were never needed.
Manifest sidecars with sha256s sit beside every cell in
`builder/scratch/cb-cells/` (gitignored; the manifests are embedded in
`cb_scores.json` at scoring).

## CB-5e — ties (`CRS-H1`/`H2`), both archives

Figures in `cb_ties-ALG-E.json` / `cb_ties-ALG-B.json`. Three observations that
belong to the record, not to any read:

- **`MK100` and `PS100` have zero binding cuts on both archives** — no source
  list exceeds 100 entries, which is `LBS-3` measured rather than assumed, and
  it is the exact vacuousness `CRS-A4` built the `R1a` read on: `MK100` is the
  maximal mutual graph.
- **The tie-dominated flag (>20 %) fires for every `MK` and `TU` cell on both
  archives** (cut-tie shares 0.32–0.70); `PS` cells are essentially tie-free
  (float |Δpop| keys). So the flag travels with the whole `R0` k-curve and the
  weakest-first trims — the MBID tie-break, not the similarity key, decides a
  large minority of survivors at every cut. Consistent with the tiebreak-fix
  history rather than surprising, but now measured.
- **The `trimmed_union` instrumentation validated against the built artifact
  on every TU cell** (exact edge-set equality, checked in both archives'
  `cb_ties-*.json`), so the H1/H2 numbers are usable everywhere they are
  reported.

## CB-5f — pair set and the `CRS-A2` baseline

**Baseline verdict: both famous classes measure ZERO `C5` on `ALG-E`-`MK50`**
(0/12 `ff-top1pct`, 0/10 `ff-top01pct`, both readable per `CRS-G3`, no
unroutable pairs). Per the `CRS-A2` protocol, §2's "any nonzero count is
decisive" stands as written for both classes; no further §8 entry is needed and
no bar was fixed against a nonzero baseline. `cb_c5_baseline.json` is the
record, written before any other cell's `C5` was opened.

**The common-routable restriction cut the draw 82 → 39** (`cb_pairs.json`
carries both per-class tables). The two famous classes survive readable; all
five `× lower` classes fall below `CRS-G3`'s 8-pair bar and are flagged
unreadable for path criteria in every cell.

**Decision, recorded here rather than papered over:** proceed under the
committed design, no redraw. The pair set was fixed in the prereg's §0 —
seed, stratification, drawn once, restricted to pairs routable in every
compared cell — and `CRS-G3` is the pre-registered answer to a thin band:
refuse to pool, refuse to squint, say so. Enlarging the draw after seeing
which classes died would be a post-hoc design change shaped by the attrition
it responds to. Consequences for the reads, stated now: path criteria
(`C4`, `C5`, lengths) are readable on famous classes only; the obscure-end
story is carried by the structural criteria (`C1`/`C2`), which use no pairs.
The handoff anticipated exactly this ("`CRS-G3`'s readability flags are the
thing to watch on `ALG-B` cells"). If the owner later wants path reads on
`× lower` classes, that is a new draw under a new §8 amendment, designed
cold.

## CB-6 — the reads, in the prereg's order, each written before the next is opened

Figures cited from `cb_scores.json` (commit `35e63bf`); this log states verdicts
against the pre-registered bars and does not restate tables.

### `CRS-R0` — the k-curve at production scale

*Run state presupposed: all four `MK` cells per archive — satisfied, all eight
built and scored.*

- **`ALG-E`: NULL, and it is the pre-committed null.** `C1` (lower-half
  stranding) moves 0.08 % → 0.07 % across k 50→100; `C2`'s largest step is
  0.40 points — nothing reaches the 1.0-point material bar. Per `CRS-A3`'s
  amended wording: **k within mutual k-NN is not the operative lever for
  stranding at production scale on `ALG-E`; `R0` cannot speak to reciprocity —
  `R1`/`R1a` do.** No escalation to k > 100, which does not exist (`LBS-3`).
- **`ALG-B`: every k step is material on both criteria, and the curve is
  decisive on both.** `C1` falls 7.00 → 4.33 → 2.20 → 0.21 % (every step
  ≥ 1.0 points; cumulative 6.79 against a 3.46 decisive bar). `C2` falls
  8.67 → 0.42 % (every step material; cumulative 8.25 against a 3.80 decisive
  bar). **`GRT-P3`'s trial-scale k-sensitivity transferred to production
  scale: `ALG-B`'s headline stranding and exclusion costs are largely
  k = 50 artifacts.** At k = 100, `ALG-B`'s lower-half stranding (0.21 %)
  sits near `ALG-E`-`MK50`'s 0.08 %, and its exclusion (0.42 %) is below
  production's 1.07 %.
- **Flag carried per `CRS-H1`:** every `MK` cell below k = 100 is
  tie-dominated on both archives (cut-tie shares 0.58–0.70) — the MBID
  tie-break, not the similarity key, decides a majority of survivors at those
  cuts. `MK100` has no binding cut at all (`LBS-3` measured).

### `CRS-R1` — the rule effect at matched bound

*Run state presupposed: the four bound-50 cells and the five bound-100 cells of
each archive, all scored — satisfied.*

**The pre-committed null does NOT hold: the incumbent mechanism loses its first
real competition at bound 50, on both archives.**

- **Bound 50, `ALG-B`:** both `trimmed_union` cells beat `MK50` **decisively**
  on both criteria — `C1` 7.00 % → 0.64 / 0.63 % (6.4 points against a 3.46
  decisive bar), `C2` 8.67 % → 0.72 / 0.71 % (8.0 points against 3.80) — with
  **no `C3` flag** (degree mass *falls* 40 %) and `C4` hub transit *falling*
  on both readable famous classes.
- **Bound 50, `ALG-E`:** the same two cells beat `MK50` **materially** on `C2`
  (1.07 % → 0.00 %; the absolute column: **1 artist excluded against 800**)
  with `C1` flat at floor (0.08 → 0.07 %), no `C3` flag, `C4` falling.
  (`C2` decisiveness is unreachable on `ALG-E` by construction — the whole
  baseline is 1.07 points.)
- **`proximity_select` is the family that loses:** at bound 50 it is
  **materially worse** on `C1` on both archives (`ALG-E` 0.08 → 5.62 %;
  `ALG-B` 7.00 → 8.67 %) — the anti-obscure direction §0's bearing table
  predicted from its construction (the reference's author built the key to
  suppress "back alleys").
- **Bound 100:** every family converges to near-floor stranding and exclusion.
  **`PS100` is byte-identical to `MK100` on both archives** (sha-equal;
  at k = 100 no list has a binding cut, so the selection key never fires —
  `LBS-3`'s ceiling, now measured as graph identity). The bound-100 set's
  `C4` moves ≥ +50 % on `ff-top1pct` for most cells vs `MK50`
  (`ALG-E`: `MK100`/`PS100` +53 %, `TUw-50-100` +90 %; `ALG-B`: +83/89 %,
  `TUw-50-100` +152 %, `TUq-50-100` +75 %) — **the material hub-transit flag
  travels with the whole bound-100 set** in any recommendation.
- **Caveat, carried to the weakest-link section of the report:** `C4`'s "own
  top-1 %-by-degree set" is ill-defined on cells where thousands of nodes sit
  at the ceiling degree — membership among tied-degree nodes is
  selection-order arbitrary. The production-set companion column
  (`top1pct_degree_frac_production`) is in `cb_scores.json` for anyone who
  wants the well-defined variant; the criterion reads as committed.

### `CRS-R1a` — the reciprocity isolation (`CRS-A4`)

*Run state presupposed: `MK100` and `TUw-100-100` built and scored per
archive — satisfied. Share of nodes at the ceiling, where the trim
contaminates the isolation: 10.4 % (`ALG-E`), 10.9 % (`ALG-B`); the claim
below is confined to below-ceiling nodes.*

**NULL on both archives, per `R1`'s pre-commitment bars.** At the maximal
mutual graph, removing the reciprocity requirement moves `C1` by 0.00 points
(`ALG-E`, 0.07 → 0.07 %) and 0.14 points (`ALG-B`, 0.21 → 0.07 %), and `C2`
by 0.30 / 0.41 points — all below the 1.0-point material bar.

**Read together with `R0` and `R1`, this settles the owner's question with an
interaction, not a monocause:** reciprocity *alone* (at k = 100) is nearly
free; the rank window *alone* (on `ALG-E`) is nearly free; **reciprocity × a
narrow rank window is what strands** — `ALG-B`-`MK50`'s 7.00 % stranding
collapses to 0.64 % by dropping reciprocity at the same bound (`R1`) or to
0.21 % by widening the window under reciprocity (`R0`). Both levers work; the
union family additionally zeroes component exclusion at every bound.

### `CRS-R2` — DD-F1 bearing

*Run state presupposed: both `TUq` cells and their `TUw` isolating baselines
built, path module run on the famous-pair subset — satisfied; both famous
classes readable per `CRS-G3` (12 and 10 pairs).*

**On `ALG-E`: the NULL, and it is `R2`'s pre-committed router finding.**
`C5` = 0 on every cell, both famous classes — including both quota cells. The
mechanism premise was verified directly against the artifacts rather than
assumed: in `ALG-E`-`TUq-50-50`, Radiohead, The Beatles and Metallica each
hold exactly their 10 reserved sub-decile neighbours (19/18 at d = 100),
where `MK50` holds zero — **the reserved edges exist in the graph and the
router does not take one of them at production weights.** Per the
pre-commitment: this is a *router* finding — the `w_floor`/`w_jump` pricing
outranks the new structure — it feeds the plan §0 ruling-2 future track, and
it is **not** a licence to retune weights inside this track. Zeros on
`weakest_first` and `mutual` cells confirm §0's bearing table and are not
findings.

**On `ALG-B`: decisive nonzeros, including under the incumbent rule.** The
`CRS-A2` protocol left §2's "any nonzero count is decisive" standing for both
classes, and `ALG-B`-`MK50` itself scores 2/12 (`ff-top1pct`) and 5/10
(`ff-top01pct`); every `ALG-B` cell except `MK100`'s broad class is nonzero
somewhere, with sub-decile interior shares up to 0.30. **The archive change,
not the cap rule, is what moves DD-F1's territory** — famous-pair journeys
through genuinely obscure interiors exist under `ALG-B` even at the
production rule, while no rule cell achieves them on `ALG-E` at production
weights.

### `CRS-R3` — the archive tilt

*Run state presupposed: both `MK50` cells scored and the survival split
computed — satisfied (325,027 common edges; 242,805 survive, 82,222 vanish).*

**Direction as pre-committed, magnitude immaterial.** Survivors' median
max-endpoint percentile is 86.03 against the vanished edges' 84.50 —
**+1.53 points, below the 5-point material bar.** `LBS-4`'s directional
prediction (survivors tilt famous) is confirmed, but `ALG-B` does **not**
materially re-price "similar" toward popularity among surviving edges — the
cost that would have had to appear in every summary of `ALG-B`'s candidacy is
measured and small. The `CRS-A5` companion (endpoint re-verified 200, zero
nulls in the probe; 49,399 artists fetched, 47 null-count edges) agrees in
direction in `total_user_count` currency (5,839 vs 5,526), with the
carried caveat that this table shares the Wikipedia proxy's blind spot and
corroborates nothing. Per the prereg, this figure now travels beside
`RC-R1`'s stranding figures in any future `ALG-B` discussion.

### `CRS-R4` — the reference row

*Run state presupposed: `UC` built or `CRS-G4` excused it — both built, in
~30 s each; `G4` never fired and the full row exists, not the degraded form.*

Measured, never an option (plan §0 ruling 3): the uncapped graphs put
stranding and exclusion at floor (`C1` 0.07 %, `C2` ≤ 6 artists) at the price
of max degree **15,631** (`ALG-E`) / **17,883** (`ALG-B`), top-1 % degree
mass ≈ **0.199** (five times any capped cell), and famous-pair hub transit of
**0.97–1.00** — nearly every interior hop of a famous-pair journey passes
through the top-degree set. This is the measured baseline plan §0 ruling 2's
future track starts from; no sentence here recommends unbounded operation.

### Exposure map (criterion × changed knob), before anything is escalated

| Criterion | archive | k (rank window) | family/mechanism | d (ceiling) | trim | reciprocity (R1a) |
|---|---|---|---|---|---|---|
| `C1` stranding | crossed: 7.00 vs 0.08 at `MK50` | crossed on `ALG-B` (decisive), null on `ALG-E` | crossed at bound 50 (`TU` decisive on `ALG-B`; `PS` materially worse both) | crossed (`TU` d 50→100 immaterial, already at floor) | not crossed (`TUq`≈`TUw` on `C1`) | null both archives |
| `C2` exclusion | crossed (8.67 vs 1.07) | crossed on `ALG-B` (decisive), immaterial on `ALG-E` | crossed (`TU` zeroes it, both archives, decisive on `ALG-B`/material on `ALG-E`) | immaterial | not crossed | null both |
| `C3` hub-mass flag | no flag fired in any selectable cell (all `TU` fall ~40 %; `MK100`/`PS100` +3–5 %) | — | — | — | — | — |
| `C4` hub transit | crossed (anchors differ) | fires ≥+50 % on the bound-100 set | falls at bound 50, rises at bound 100 | crossed | `TUq` < `TUw` at bound 100 | — |
| `C5` famous-pair presence | **crossed decisively** (`ALG-E` all-zero, `ALG-B` nonzero incl. `MK50`) | not crossed on `ALG-E` (zero at every k) | not crossed on `ALG-E` (zero in every family) | not crossed on `ALG-E` | **not crossed on `ALG-E` — the R2 router null** | — |
| `C6` survival tilt | crossed (the only knob it reads) — direction confirmed, immaterial | — | — | — | — | — |

Nothing requires escalation: every read resolved under its pre-registered bar,
including both nulls, and no criterion was endangered by a knob it does not
cross.

### The report

Four-part presentation (measured / inferred in plain language / weakest link /
options): [`findings/2026-07-30-track-b-cap-selection-results.md`](findings/2026-07-30-track-b-cap-selection-results.md)
— **the authoritative document for Track B's results.** Raw record stays
`cb_scores.json`. Weakest link named there: the path half rests on 22
famous-pair journeys after the `CRS-G3` attrition; the stranding half uses no
pairs and is defended everywhere.
