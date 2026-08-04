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

### A path defect of mine, and the determinism check it paid for

The first cell run wrote into **`builder/builder/scratch/`**: my `SCRATCH` took
`parents[2]` from the *file* rather than from its directory, and `parents[2]` of the file
is `builder/`, not the repo root. Caught at `git status` — the stray tree showed as
untracked.

**It matters for one specific reason, and it is the same hazard analyst m11 named arriving
by a different route.** `.gitignore` ignores `builder/scratch/` **wholesale**, but the
stray path only matched the `*.bin` rule — so the `.bin.json` **sidecars there were not
ignored** and were a `git add -A` away from being committed as if they were the record.
The pathspec commit rule is what kept them out; nothing about the rule was aimed at this
case, which is the argument for keeping it.

Fixed at the constant, and the cells were **rebuilt rather than moved** — the manifests
carry absolute paths, and a rebuild regenerates them honestly instead of hand-editing a
record. That cost four minutes and bought a check worth more than it: **all eight cells
came back byte-identical to the first run**, artists, edges and sha256 alike, across two
independent invocations. Determinism (spec §9) is now measured on this harness rather
than inherited from the pipeline's own test.

---

## §6 — `CRE-T6`: the `S2` device, its companions, and the tag cells

**Figures: `cre_s2_degeneracy_gate.json` and the `S2` rows of `cre_builds.json`.**

### The branch was read from the record, not from memory

`--tag-cells` reads `cre_d1.json`'s `branch` field at run time and derives its data-set
list from it. It printed `not_supported → tag cells on ('ALG-E',)`, so **`B-S2` and its
two companions were never built**, exactly as `CRE-D1`'s consequence requires. Wiring it
this way rather than hard-coding `ALG-E` means the branch cannot drift from the committed
outcome.

### The degeneracy gate, which is the whole argument that `S2` is one knob from `S1`

**On the real build: byte-identical to the committed `E-S1` sha.** With an agreement
table that is undefined everywhere, `cap_tag_limited` reproduces
`cap_trimmed_union(trim="weakest_first")` exactly — so §0.2's naming of `S1` as `S2`'s
isolating baseline is now a measured fact rather than a design intention, and the factor
table's row really does differ by one column.

**On the synthetic fixture, the tuple key's middle element was tested where it actually
bites — and the plan's own worked case turned out not to be constructible.** The plan
motivates that element with an IEEE product collapse (two distinct strengths whose
products with the neutral constant are equal). A search over 2,000,000 adjacent doubles
found **no such pair** at the 0.15 constant, which is consistent with the plan's own note
that collapses measure at zero on today's edge scores. Rather than assert a case that
does not exist, the test uses the degeneracy that **does**: agreement measured at exactly
0 on every edge — the block analyst M4 found on ~3.9 % of real edges, here made total. The
first key element then ties on *every* edge, which exercises the middle element harder
than a rare pair would. **And the red half is included**: a bare product key is shown to
produce a genuinely different surviving set on the same fixture, so the degeneracy test
is not passing vacuously.

Liveness is pinned too: an edge ranked at agreement 0 is deleted first at an over-budget
node even though it is the strongest edge there — the device re-orders deletions rather
than merely being wired in.

Both companions are pinned by property: the vote-scramble preserves each artist's
multiset of strengths and its label set exactly while changing the assignment (so it is
`CRE-AM1`'s control and not a different device), and the label-scramble preserves exactly
which artists are labelled (`TAS-AM3b`'s stronger form).

### An omission of mine, caught against the plan and repaired

The first tag-cell run recorded only the labelled-node share. **The plan (analyst M8)
requires each `S2` manifest to record the share of nodes with ≥ 2 *measured* agreements
as well**, because a node with fewer than that has its whole neighbour pool collapse to
one constant and **the device is structurally inert there** — so the labelled share alone
overstates where `S2` can act. Added, and computed from the built artifacts rather than by
rebuilding: the cells are byte-deterministic, so the values are identical to what the
build would have written, and the code path is now in `build_tag_cell` for any later run.

On `ALG-E` the inert share is small, and comfortably better than the pre-drop `ALG-B`
figure the plan warned about — but that warning was aimed at `B-S2`, which does not exist
on this branch. **T11 must still store both shares beside any `CRE-C5` attribution field**;
that obligation is unchanged.

7 unit tests pass; 26 across the suite.

---

## §7 — `CRE-T7`: Stage 1 screens, and SEAM 1

**Figures: `cre_screen.json`.** Eleven graph cells screened: the eight non-tag cells and
the three `ALG-E` `S2` cells.

### Outcomes

- **`CRE-G3`: all 22 famous pairs survive in every cell.** No pair is dropped, so every
  Stage-2 comparison runs on the full draw and the per-comparison ≥ 8 readable floor is
  met with room. The floor is still recomputed per comparison in Stage 2 — it is a
  different device from the endpoint-survival one, and per analyst m12 pin (a) it plays
  no part in the `C6` denominator.
- **`CRE-C3`: no cell is disqualified.** Every cell's loss against its own cleaned
  pre-cap population is well below the owner-fixed 10,000 line. The held-constant claim
  is asserted in-run and re-checked on the committed output: one cleaned pre-cap
  population per data set, identical across all its cells.
- **`CRE-C6`: no cell is screened out** — **zero** zero-supply pairs in every cell. The
  baseline carve-out was therefore never exercised, but it is encoded and tested rather
  than left to be remembered.

**Every cell proceeds to Stage 2.** Nothing was eliminated at Stage 1.

### Two cautions this result needs, and neither is visible from the headline

**1. "Not screened" is a floor, not a quality bar.** The screen asks only whether a
`CRE-C1` median pass is *arithmetically impossible*. Supply is enormous for a typical
pair-cell and as low as a **single qualifying edge** at the thinnest. A cell can pass this
screen and still have almost nowhere to go for particular pairs, and `C6`'s per-pair rows
are committed so that is visible rather than averaged away.

**2. The tempting cross-read is NOT licensed yet, and I am recording that it is
tempting.** It is very natural to put `CRE-C6` beside `CRE-D3` and conclude *"somewhere
obscurer is reachable within one step, and the pricing device still will not go there —
so the blocker is the router, not supply."* **That conclusion is barred here**, because
the two were measured on **different substrates**: `CRE-D3` ran on the adopted artifact
per §3.3's carve-out (no build, no cleanup), while `C6` is measured on the cleaned cells.
The comparison a sweep licenses is `C6` beside the *sweep's own* cells, which is Stage 2's
work. Written down now, before any sweep figure exists, so it cannot be assembled later
as though it had always been the plan.

### The affine `pop_raw` report — the T5 caveat, now measured

§0.3's instrumentation row is computed for every cell against its §0.2 isolating baseline,
and it confirms what T5 flagged: **three comparisons do not share a `pop_raw` scale** —
`E-S1` vs `E-S0`, `B-S0` vs `E-S0`, and `B-S1` vs `B-S0`. Their affine maps are recorded
as two floats each. The remaining seven are exactly comparable.

**Consequence for Stage 2: no cross-cell sentence about `pop_raw` may be written for those
three pairs without applying the recorded map** — and one of them, `B-S0` vs `E-S0`, is
the data-set-isolated cell that already carries §0.4's confound rows. Nothing in the
ladder is affected, since the cost function's jump and floor terms are computed within a
single cell.

38 tests pass across the suite.

---

# SEAM 1 — Stage 0 and Stage 1 are complete and committed

**Everything a successor needs is a committed artifact.** Nothing is in flight, no port is
listening, no background job survives this session.

**Run state.** `CRE-D3` and `CRE-D1` have committed outcomes, both on their pre-registered
expected branches. Eleven graph cells are built, gated and screened. **No `CRE-R` read is
licensed and none has been made.** No criterion has been evaluated, nothing is adopted,
and no blind listen has been spent.

**The next session starts at `CRE-T8`**, reading `cre_d3.json`, `cre_d1.json`,
`cre_screen.json`, `cre_builds.json`, `cre_build_gate.json` and
`cre_s2_degeneracy_gate.json` cold. The branch consequence it must carry: **`CRE-D1` fired
`not_supported`, so the three `(D1-branch)` cells do not exist and no router-side tag arm
does; `E-S2-P0` is branch-proof and runs.**

**Owed at Stage 2, from this session's findings:**

1. **A liveness check on the unmeasured-class counters** (§3). Every interior was
   ruler-measured on `ALG-E` at Stage 0, so pins 2 and 3's machinery has never actually
   counted anything. Its first real exercise is the `ALG-B` and `UC` cells.
2. **The affine map applied** to the three non-comparable `pop_raw` comparisons above,
   or no cross-cell `pop_raw` sentence written for them.
3. **`CRE-C5` attribution on any `S2` cell must quote both `S2` shares** (labelled-node,
   and ≥ 2 measured agreements) as analyst M8's licensing constraint.
4. **The `C6`/`D3` cross-read stays barred** until it can be made within one substrate.

---

## §8 — Closeout outcomes (Seam 1)

- **A1**: this log is the retained record, written **per task** rather than at closeout,
  which is what makes the seam cheap.
- **A2**: handoff [`2026-08-03-HANDOFF-cre-run-seam1.md`](2026-08-03-HANDOFF-cre-run-seam1.md)
  written from the template header; the exec-plan handoff's role line edited to name it as
  successor **and** to record that its claim 3 (`CRE-AM2` not yet appended) is now
  discharged rather than wrong.
- **A3**: the four Stage-2 items each carry a success condition (handoff §"Owed at Stage
  2"). **One prior condition found due and struck in place**: `CRE-AM2`'s "specified but
  not yet appended", discharged at `5656602` — struck in the exec-plan log's §9 with the
  date and what satisfied it, not deleted.
- **A4**: **no config knob added — not applicable**, stated rather than skipped. The
  prereg forbids shipped-code change; `ApiConfig` and `BuilderConfig` defaults are
  untouched and the harness *asserts* the drop flags rather than setting them.
- **A5**: all four ports empty, verified. No server was started at any point in this
  session; every background job (three cell builds, one screen run) has exited. **Nothing
  is left running and nothing is owed a server** — the queued C1 entry is N/A.
- **B1**: `docs-lint.sh` reported **one hard failure — mine**: this log was missing from
  `docs/README.md`. Fixed, along with a new row for the handoff. The `doc-auditor` then
  ran on the semantic half and returned **no findings at any severity**, having
  specifically checked the six things it was asked to disbelieve me about.
- **B2**: every module has inbound imports except `cre_d1.py`, `cre_d3.py` and
  `cre_screen.py`, which are **entry-point runners** invoked by path — the same shape as
  every other probe under `builder/analysis/`. Asked and answered; not orphans.
- **B3**: **this found a real defect in my own tests.** Tampering `cap_tag_limited`'s
  tuple key (dropping the middle element) correctly turned the `S2` degeneracy test red.
  But `test_cre_screen.py` had **re-implemented** `CRE-C6`'s screen predicate locally
  instead of importing it, so it guarded a copy: flipping the module's `>` to `>=` left
  the suite green. The predicate is now exported from `cre_screen.py` and imported by the
  test — re-tampered to confirm, and three tests now fail as they should. **A test that
  restates the logic it is checking is vacuous in exactly the way a test that asserts
  nothing is**, and it is invisible to a passing suite.
- **B4**: `cre_build.py`'s header claimed to be `CRE-T5` alone after `CRE-T6` had added
  four functions to it. Corrected. No other prose-vs-code drift found.
- **B5**: nothing under `.claude/` or `memory/` mentions this work at all, so there is
  nothing there to have gone stale. This log restates no figure — every number is cited
  from a committed JSON by file and key.
- **C1**: N/A entry queued. Nothing changed that the owner can press.
- **D1**: tree clean. **D2**: no committed fixture is affected — the shipped artifact did
  not change and no shipped code did. **D3**: provenance for all eleven gitignored cells
  lives in the committed `cre_builds.json` (sha256, artists, edges, diagnostics), plus the
  two gate JSONs.
- **D4**: builder **164 passed**, api **230 passed**, frontend **107 passed**, and the
  `CRE-` analysis suite **38 passed** (excluded from the builder default run by the
  owner's 2026-08-01 `testpaths` ruling).
- **D6**: standing layer delta **exactly 0 on both units** — unconditional **44,494**
  characters, conditional **2,155** lines, both equal to the figures at the previous
  closeout. This session touched neither `CLAUDE.md`, `.claude/`, nor `memory/`.

---

## §9 — `CRE-T8`: Stage 2 entry gates

**Figures: `cre_gates.json`.** New session, cold from the Seam 1 handoff. Branched
`cap-reeval-stage2` off `main` rather than continuing on `cap-reeval-run`: the handoff's
"inline on the existing branch" instruction predates the merge of PR #70, and that branch
is now in `main`. Nothing else about the instruction changed — execution continues inline
on Opus, retiring at the plan's remaining seams.

### Outcomes — all three gates pass

- **`CRE-G1`(c)**: ruler frame **N = 74,151**, asserted inside the `Ruler` constructor.
- **`CRE-G1`(a)** on **E-S0**: **22/22 pairs identical**, node sequence *and* stop kind,
  mirror against production `find_journey` on the same cleaned substrate. No divergence,
  so no harness fix is owed and the bar was never approached, let alone widened.
- **`CRE-G1`(a)** on **B-S0**, reported QA and **not gated** (the prereg gates E only):
  **22/22 identical**. Worth recording because it is the substrate T10 sweeps.
- **`CRE-G2`(a)**, at the instrument-only extreme r = 1.0, against a bar of ≥ 0.5:
  **E-S1 17/22 (0.773)**, **B-S0 21/22 (0.955)**, **B-S1 22/22 (1.000)**. **No cell is a
  dead wire**, so a `P1` null in any of the three will be readable when T9/T10 produce one.
  All 22 pairs were readable in every cell — no pair lost its d1 to an absent journey or
  an empty d0 interior, so the exclusion path exists but was never taken.

### Three decisions taken here, with their reasoning

**1. `CRE-G1`(a) got a red half the plan did not ask for.** An identity gate is precisely
the shape that passes vacuously: a comparison wired to itself, or a loop body that never
runs, reports a clean 22/22 either way. This plan has already produced that exact defect
twice — `CRE-G2`(b)'s first draft compared the toll formula against itself, and the Seam 1
closeout's B3 check found `test_cre_screen` guarding a *copy* of the predicate it was
meant to check. So the green run is followed by the same comparison with the mirror's
`w_hop` moved off production's value, which **must** diverge. **It does, on 3 of 22
pairs.** That count is small and is reported as measured: `w_hop` is the lowest-magnitude
weight in the cost function, so this is the gentlest available perturbation, and the gate
it discharges is *can this comparison go red at all* — for which three is as decisive as
twenty-two. A red half is not evidence of sensitivity and is not offered as any.

**2. `CRE-G2`(a) deliberately has no red half.** Its failure direction is "nothing
changed", so a dead comparison reports zero changes and **fails**. It cannot pass
vacuously. That asymmetry — not effort or symmetry with `G1` — is what decides where a
control earns its cost.

**3. One d0 per pair is computed and shared by both `G2`(a) arms.** Legitimate because the
fame ramp at k = 0 is not merely zero but *not added at all* in `_dijkstra`, so the arms
share d0 by construction and therefore share the victim the ladder presses. That is
`CRE-G1`(b)'s claim; it is asserted per sweep run in T9 rather than assumed there.

### State

`cre_gates.py` is new first-party code; **Snyk `snyk_code_scan` over the analysis
directory: 0 issues.** No shipped code, no config default and no artifact changed. **No
`CRE-R` read is licensed by this task and none has been made**; nothing is adopted and the
blind listen (`REQ-38`) is unspent. The four items owed at Stage 2 are untouched and all
four remain owed.
