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
