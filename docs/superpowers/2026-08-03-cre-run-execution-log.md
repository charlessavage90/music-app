# Cap re-evaluation (`CRE-`) run — retained execution log

**Role: ACTIVE — the retained execution log for the `CRE-` experiment run.** It records
decisions and reasoning per task, not narration, and is appended to **per task** rather
than only at closeout, so any session can pick the run up from the committed record.

**Governing documents.** The experimental document is
[`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md)
(`CRE-`, frozen `3d7b7d6`, amended by `CRE-AM1` at `eec67a8` and `CRE-AM2` here) — **it
governs wherever anything else disagrees.** The operational document is
[`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md)
(`CRE-T1`–`CRE-T11`, revised pre-run at `da9e49e`). The pre-run review record is
`builder/analysis/2026-08-03-cre-plan-critique/` — frozen as-executed, and **its
cell-level figures were measured on pre-drop Track B builds**; quote them with that
provenance.

**This log owns no figures.** Every measured number lives in a committed JSON under
`builder/analysis/2026-08-03-cap-reevaluation/`, cited by file and key, never restated
here.

**Run branch:** `cap-reeval-run`, off `main` at `2e3b017` (PR #69 merged). Execution is
**inline** on Opus — the owner's model and execution-mode ruling, 2026-08-03
(exec-plan log §6) — retiring at the plan's three seams (after `CRE-T7`, `CRE-T9`,
`CRE-T11`).

---

## §1 — `CRE-T1`: branch, log, `CRE-AM2`, and the fame ruler

**Started 2026-08-03.** Session oriented via `session-start` against the seam handoff
[`2026-08-03-HANDOFF-cap-reeval-exec-plan.md`](2026-08-03-HANDOFF-cap-reeval-exec-plan.md).
No cold-read-back was owed: that handoff is a **seam** handoff, and the committed
artifacts corroborate it.

### Pre-run verification carried out at orientation

The plan's own Verification record (written 2026-08-03, before the plan) states every
file, function, config value and commit the prereg names resolves. Per `session-start`'s
"verify one claim before building on a report", four load-bearing ones were re-checked
independently against the repo before any work began. All four hold:

- `drop_no_release_tail` and `drop_featured_credit` are both `True` by default
  (`builder/src/artistpath_builder/config.py:159`, `:175`), so the Global Constraints'
  "assert, don't set" is the correct instruction.
- `mirror.py::w_known_ramp_pctl` exists, is additive, defaults to `0.0`
  (`builder/analysis/2026-07-23-track2-sweep/mirror.py:107`), and today reads the
  **popularity** percentile — so plan dependency (2), the re-plumb to fame currency, is
  correctly declared rather than assumed.
- The ruler frame count **74,151** resolves, beside the artifact's 74,193 nodes.

**One divergence found and recorded rather than silently fixed.** The plan's
Verification record cites the frame count as `fi_validation.json` → **`frame_n_nonnull`**.
There is no key of that name in that file. The value lives at
`FAM-1.adopted_population.non_null` (with `FAM-1.adopted_population.population` = 74,193
beside it). **Same file, same number, same meaning — only the key path in the citation is
wrong.** Consequence for this run: `cre_common.FRAME_N` is pinned by reading that actual
path, and the prereg's `CRE-G1c` assertion is unaffected. Nothing in the plan or the
prereg is edited for this; the citation defect is recorded here.

### Step 2 — `CRE-AM2`, committed before any stage ran

Appended verbatim from the plan to the prereg's §8, on this branch, **before any stage
has run and before any result exists**. The git timestamp on this branch is the evidence,
which is the point of writing it pre-run rather than as a mid-run stop (a deliberate
divergence from the analyst's exact proposal, reasoned in the plan's Revision record).

It resolves a mechanisation contradiction found in pre-run review (analyst critique M6):
`CRE-C4`'s binding form divides by the isolating baseline's `C4`, which is **undefined**
for `E-S0-P0` (§0.2 baseline "—") and a **cross-data-set ratio §0.4 bars** for
`B-S0-P0`. Resolution: those two anchor cells carry no binding `C4` and are reported
absolute against the 0.75 reference line. **No bar moves and no other cell, criterion or
read changes.**

Committed alone at `5656602`, pathspec-scoped to the prereg, before any other file
existed on this branch.

### Steps 3–6 — `cre_common.py`, and showing the gates go red

Written test-first: the five properties failed on `ModuleNotFoundError`, then passed on
implementation. Two executor-column additions to the plan's test text, both harness
detail rather than substance: a module-scoped `ruler` fixture (the plan specifies one in
prose but does not write it), and a module-level `use_frozen("fame")` so the toy-frame
test's direct `fi_stats` import does not depend on test execution order.

**The suite passed in 0.24 s where the plan expects the `Ruler` to take "several
seconds", so the green was not taken as evidence.** Direct exercise confirms the
instrument is genuinely doing the work and is merely fast, and every quantity
reconciles two ways:

- ruler frame N = 74,151 (`CRE-G1c`), and 74,151 measured + 42 present-but-null = the
  adopted artifact's 74,193 nodes — so **every adopted node is in the snapshot**, and
  the `absent` class is empty *on the adopted artifact*. It exists for the union and
  uncapped cells, which is exactly where pin 2 says it bites.
- 88,953 measured + 4,114 null = the snapshot's 93,067 keys.
- `device_null_pctl` = 6.743e-06, below `min_measured_pctl` = 8.092e-05 — the plan's
  stated ≈ 6.7e-6, and the ordering the null-price test asserts.

**Then the gates were driven red deliberately**, because an assertion never seen to fail
is not yet an assertion: `CRE-G1c` fires on a frame N off by one; the artifact gate
fires on a wrong sha; the snapshot-manifest gate fires on a mismatched digest. All three
fired. No file was left behind by the red-check.

---

## §2 — `CRE-T2`: the mirror copy, the fame-currency ramp, and the ladder

### The copy, and a sixth delta the plan did not anticipate

`cre_mirror.py` is a verbatim copy of the frozen
`builder/analysis/2026-07-23-track2-sweep/mirror.py` with the plan's five deltas plus
`term_breakdown`. The frozen original is untouched. Step 2's diff shows **ten hunks and
exactly five deleted lines** — the docstring's first line, the two `artistpath_api`
imports, the `MirrorContext.build` signature, and its `return cls(...)`. **No line of the
cost function or its term order was touched**, which is the property byte-identity rests
on.

**The sixth delta is plumbing, and it corrects a defect in the plan's own code.** The
frozen mirror relies on its *runner* to put `api/src` on `sys.path` (`run_a0.py:29`,
`verify_mirror.py:29`) — it has no path setup of its own. But the plan's `cre_ladder.py`
text imports `cre_mirror` **before** calling `use_frozen("api_src")`, so as written it
raises `ModuleNotFoundError` on import. Verified: `artistpath_api` does not import in the
builder venv without the insert.

Two fixes were available. Reordering `cre_ladder`'s imports would keep the mirror at
exactly five deltas, but leaves the trap armed for every later module that imports
`cre_mirror` first — nine tasks' worth. **Chosen: `cre_mirror` calls `use_frozen("api_src")`
itself**, one line, no behaviour, and every downstream import becomes order-independent.
Recorded here so Step 2's diff is read against six known deltas rather than five.

### `CRE-G2(b)` shown able to go red on each clause separately

The decomposition check has two clauses against references it does not share, and a red
raised by the wrong clause would not demonstrate what the test claims. Both were driven
red deliberately and each fired on its own clause:

- **dropping the `hop` term** trips clause (1) — the breakdown's total against the
  *search's own* accumulated cost — off by exactly 2 × `w_hop`;
- **moving the ramp's mass into `sim`** leaves the total unchanged, so clause (1) cannot
  see it and only clause (2), the `r · k · Σ fame` form, fires.

The two red tests were then pinned to their clause's own message rather than to a shared
`CRE-G2(b) FAILED` prefix, so neither can pass for the wrong reason later.

Also pinned as tests, because both are `CRE-G1(b)` properties in miniature: the ramp at
`0.0` returns the frozen path even when the fame array would dominate if live (the term
is never *added*, not merely zero), and a **dominating** ramp at k = 0 still returns
production's path — the half a `+ 0.0` implementation would pass and a wrong-`k` one
fails.

14 tests pass across the three modules.

---

## §3 — `CRE-T3`: `CRE-D3`, the pricing prior

**Figures: `builder/analysis/2026-08-03-cap-reevaluation/cre_d3.json`.** Cited by key,
never restated here.

Ran on the adopted artifact with no build, per §3.3's carve-out — 22 famous pairs, arms
`P0` / `P1a` / `P1b` plus the instrument-only extreme at r = 1.0. 53 seconds, consistent
with the critique's measured V1 runtime rather than the first draft's estimates.

**All three gates passed:** d0 identity against `P0` on every arm and every pair; device
liveness at the extreme (19 of 22 d1 journeys change — `gates.device_liveness_at_extreme`,
bar 0.5); and `CRE-G2(b)` cost decomposition on 132 journeys at k = 1 and k = 10.

**Branch: `inert_as_expected`** — the pre-registered expected outcome. Both candidate
settings sit inside the 0.015 instrument floor, so the stored `consequence` field carries
§4's wording verbatim, and that is what a later `CRE-R0` is bound to. **No pause is
triggered**; the contradiction branch (Δ ≤ −0.05) was not reached.

**The extreme arm is the part worth reading, and it is a stronger prior than the
candidate arms alone.** At r = 1.0 — a price no candidate carries — the device
demonstrably *works*: it reroutes 19 of 22 first-press journeys. And it still moves the
`C1` gradient by two orders of magnitude less than the floor. So the null here is not
"the knob is not connected", which is exactly the ambiguity the liveness check was added
(analyst B1) to remove. **The device is live and the gradient does not move**, which is
the supply reading, not a pricing-strength reading.

**One thing this run does NOT establish, and it matters for T9/T10.** Every interior
slot at every depth on every arm was ruler-**measured**: `interiors_null_in_snapshot`,
`interiors_absent_from_snapshot` and `null_interior_unbypassable` are zero throughout,
which is what the plan expected on `ALG-E`. So pins 2 and 3's reporting machinery ran but
had nothing to count — **a green from those counters here is not evidence they work.**
Their first real exercise is the `ALG-B` and union/uncapped cells, where the absent class
exists by construction. A liveness check on those counters is owed at the sweeps rather
than assumed.

---

## §4 — `CRE-T4`: `CRE-D1`, the banding read

**Figures: `builder/analysis/2026-08-03-cap-reevaluation/cre_d1.json`.** Cited by key.

### The pin-5 divergence, resolved as the pin instructs

`cre_probe3b.py` was read before implementing. It and the prereg's §4 words **disagree
on aggregation**: the probe pools every labelled edge in a band and takes a **median**
difference with no size-matching, while §4 requires `(min, max)` label-set-size cells,
**≥ 30 edges in each band** per cell, per-cell **means**, and an edge-weighted mean of
per-cell differences. **The words govern** (plan pin 5), so the size-matched
mean-of-means is the headline and the divergence is recorded in `cre_d1.json`'s
`aggregation` block as well as here.

**One idf divergence was suspected and does not exist.** Pin 5 fixes `n_artists` at the
adopted node count while directing the idf table at `frames["W4"]`, which raised the
possibility of a label whose document frequency exceeds `n_artists` and so earns a
*negative* rarity weight. Checked before implementing: `five_frames()` returns `W4` keyed
on **exactly** the artifact's 74,193 nodes, so the plan's form and the probe's inline
count are the same population and no label goes negative under either. No divergence to
record.

**One genuine ambiguity in §4, pinned and made reversible rather than argued.** "The
cell's contributing edge count" does not say whether that is the popular count, the
obscure count, or their sum. Sum is used, and the **full per-cell table is committed with
both counts**, so any other weighting is recomputable from the output without re-running.

### Branch: `not_supported` — the expected one, and robust to the divergence

Both bands clear the 500-labelled-edge readability floor comfortably. **The measured
difference is positive**, where the hypothesis needed ≤ −0.05: this is not a weak
non-result but a result in the *opposite* direction to the one `CRE-D1` was written to
detect.

**The aggregation divergence does not change the branch, which is the thing that
mattered.** Size-matching moves the figure but not its sign, and the probe's pooled form
— recomputed here as `probe_form_pooled_median_difference` — reproduces §9's disclosed
+0.08 to within rounding. That agreement is worth more than the headline: it is
independent evidence that this run's frame construction, fame join, band masks and edge
extraction match the probe's, since the two were written separately.

**Consequence, applied from here on:** the `(D1-branch)` cells of §0.2 — `B-S2-P0`,
`E-S2-P1a`, `B-S2-P1a` — **do not exist**, and no router-side tag pricing arm does.
**`E-S2-P0` is branch-proof and runs regardless.** No amendment is owed and no pause is
triggered.

**Weakest link, recorded because every `D1` sentence must carry the labelled-edge share.**
The two bands are not equally observed: the popular band's edges are almost entirely
labelled, the obscure band's are around two-thirds. So the obscure-band mean is taken
over the labelled *majority* of a population whose unlabelled remainder is much larger —
the same coverage thinning `COH-2` measured, in the same place. It does not threaten this
branch (the sign is wrong for the hypothesis by a wide margin, and label coverage is
*higher* in the band the hypothesis said should be thinner), but a future reading that
wanted to interpret the *magnitude* would have to deal with it.

---

## §5 — `CRE-T5`: the cleaned-substrate build harness and the eight non-tag cells

**Figures and shas: `cre_build_gate.json` and `cre_builds.json`** (both committed —
`.gitignore` swallows `builder/scratch/` wholesale, so the sidecars beside the `.bin`
files can never reach git and the committed mirror is the only durable identity record;
analyst m11).

### The gate

`assemble_cleaned` is `pipeline.build_from_archive`'s body with exactly one seam at the
cap. **Both greens passed byte-identically** — the mirror at `mutual_knn_cap` k = 50
serialises to the same sha as a direct `build_from_archive` run, on `ALG-E` *and*
`ALG-B` — and **the red at k = 49 fired.** So the copy is the live pipeline, drops
included, and the gate is shown able to detect a changed cap rather than assumed to be.

**Two defects in the plan's own code, found by running it rather than by reading it.**
`ListenBrainzSource` is config-bound (`cli.py:120`), not default-constructed; and `Graph`
carries `artist_count`/`edge_count` accessors, not the `stats`/`adjacency` attributes the
plan's manifest snippet indexes. Both fixed at the call site; neither touches the
assembly body, which is what the gate protects. The source is now constructed from the
**same** config the assembly uses, so it can never carry a different algorithm than the
archive sub-tree it reads.

### Two checks the build produced for free, and both are load-bearing

1. **`E-S0` and `B-S0` reproduce the gate's greens exactly.** They are the same cell
   built twice through different entry points, so the match is independent evidence that
   `build_cell`'s path and `gate()`'s path do not diverge.
2. **`nodes_entering_cap` is identical across all four supply rules within each data
   set** (and the two drop counts are identical too). That is the held-constant claim
   made mechanical: the cleanup and the cap-invariant popularity really are computed
   upstream of the cap, so the four supply cells differ **only** at the seam. A factor
   table can now read across the row and count one difference.

### One diagnostic that is a genuine caveat, not a curiosity

**`pop_log_low` is not constant across cells within a data set.** It sits near 0.29–0.31
for `MK50`/`MK100` and at exactly 0.0 for `TU` and `UC`, because the affine map's anchors
are taken over the **kept** node set and the looser rules keep artists with zero
score-weighted in-degree that `MK50` prunes away. `pop_log_high` is stable.

**Consequence: `pop_raw` is not comparable across supply cells** — the same artist can
carry a different `pop_raw` in two cells purely because the low anchor moved. This is
exactly what §0.3's instrumentation row exists to expose, it is why every manifest
carries both anchors, and it is owed an explicit treatment in the `CRE-T7` affine
`pop_raw` report rather than being noticed later. **Nothing in the ladder is affected**
— the cost function's jump and floor terms are computed within a single cell — but any
cross-cell sentence about `pop_raw` is barred until that report is written.

`ALG-B` drops materially more no-release tail than `ALG-E` (both figures in
`cre_builds.json`), which is the direction the tail-drop census already recorded.

Five unit tests pin the invariants: the cleanup assertion fires when either flag is off,
both flags default on, `UC` is marked staged-and-barred in its manifest, the supply axis
is the four pre-registered rules, and the diagnostics contract holds on the committed
gate output — including that both drop lists actually bit, so a silently inert drop
cannot pass as "held constant".
