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

---

## §10 — `CRE-T9`: the `ALG-E` sweeps, and SEAM 2

**Figures: `cre_sweep_E-*.json`, nine committed files, one per cell.** All nine `ALG-E`
cells swept: E-S0-P0, E-S0b-P0, E-S1-P0, E-S1-P1a, E-S1-P1b, E-S2-P0, its two companions,
and the staged E-S3-P0.

### Outcomes

- **`CRE-G1`(b): PASS on both `P1` cells.** E-S1-P1a and E-S1-P1b are bit-identical to
  E-S1-P0 at d0 on all 22 pairs, so the device fires at depth and not before.
- **`CRE-G2`(b): 44 assertions per `P1` cell, all passing** (22 pairs × k ∈ {1, 10}).
- **Every pair completes the full ladder in every cell**: 22/22 walked all 21 depths, no
  infeasible `(pair, depth)` cell anywhere, and no `adjacent_only` termination. The
  padding-vs-infeasibility machinery is therefore built, tested and **unexercised** on
  `ALG-E` — which is a fact about this data set, not evidence the distinction is idle.
- **Cost, measured:** ~7–26 s per capped cell, **292 s for the staged E-S3** — squarely
  inside analyst V1's "~4–5 minutes on UC" and two orders off the plan's superseded
  "~8–15 min per capped cell", exactly as V1 predicted.

### The counter-liveness item is NOT discharged, and `ALG-E` cannot discharge it

Owed item 1 from the Seam 1 handoff asked for a non-zero reading on the two unmeasured
classes. **Across all nine cells the totals are zero: no ruler-null interior, no
absent-from-snapshot interior, and therefore a zero mechanical `null_interior_unbypassable`
count.** That is the *same* green the Stage-0 run produced and it carries the *same* weight
— none — because every `ALG-E` interior is ruler-measured, so a dead counter and a true
zero are indistinguishable here. **The condition passes to T10**, where the plan expects
~6% of `ALG-B` nodes to be ruler-null and the counters can go non-zero. Recorded here so
the item cannot be quietly marked green by a second zero.

### One thing checked rather than assumed, because it looked wrong

The `CRE-D2` term shares came back with **`sim` contributing exactly 0.0%** of path cost on
the first cell — the largest weight in the cost function contributing nothing. Probed
before running the remaining eight: the d0 paths ride entirely on edges at similarity
**exactly 1.0**, of which the artifact carries 2.09%, so `w_sim · (1 − sim)` is genuinely
zero along them and path cost is `jump_raw` + `hop` alone. Not an instrument fault, and
consistent with the ceiling-saturation this project already prices elsewhere
(`toll_s`'s "ceiling-saturated edges").

**It did expose a real gap, and it is now closed.** `assert_cost_decomposition` was pinned
to `P1` cells only, so the term shares on every `P0` **baseline** — the cells each candidate
is measured *against* — would have gone into T11 unverified. The same assertion now runs on
`P0` cells too, 44 per cell, recorded under its own key as a plain instrument check and
**deliberately not called `CRE-G2`(b)**: that identifier is pre-registered for the device
test, and two load-bearing objects do not share an identifier here.

### Two defects fixed before the sweeps, both from the retired session's notes

1. **`cre_tags.agreement_table` cached on `kind` alone**, and the cache hit returned before
   `n_artists` was consulted. Every caller passes the same value today, so it could not
   misfire — it would have surfaced as a **wrong figure, not an error**. Keyed on
   `(kind, n_artists)` now, with a regression test **tamper-checked red** against the old
   key.
2. **`cre_gates` carried both its decision rules inline**, which is the shape closeout B3
   found in `test_cre_screen`. `journeys_identical` and `g2a_passes` are extracted and the
   new `test_cre_gates` imports them. `g2a_passes` guards its denominator: **an empty
   readable set is a dead wire, not a pass** — `0 >= 0.5 × 0` is true, and that is how a
   vacuous gate gets built.

### What is measured, and what is not licensed

Per-pair per-depth journeys, interior fame values, term shares and the unmeasured-class
counts are in the nine committed `cre_sweep_E-*.json` files — **cited here, never restated,
including in aggregate**: a median quoted in this log would be a second home for a figure
`cre_score.json` is about to own, which is how the drift this project has already paid for
begins. **No `CRE-R` read is licensed by any of it and none is made here** — no criterion is
evaluated, no cell is compared to another, the three non-`pop_raw`-comparable comparisons
have had no map applied, and `CRE-C1`'s two reporting populations are T11's work. The
figures are recorded so T11 can compute; they are not a result.

**SEAM 2.** All `ALG-E` sweep JSONs committed. `T10` starts cold from here.

---

## §11 — `CRE-T10`: the `ALG-B` sweeps

**Figures: `cre_sweep_B-*.json`, seven committed files, one per cell.** B-S0-P0, B-S0b-P0,
B-S1-P0, B-S0-P1a, B-S1-P1a, B-S1-P1b, and the staged B-S3-P0. Same harness, unchanged —
no code was touched between the two data sets, which is what makes them comparable at T11.

### Outcomes

- **`CRE-G1`(b): PASS on all three `P1` cells** (B-S0-P1a, B-S1-P1a, B-S1-P1b), each
  bit-identical at d0 to its supply-matched `P0`.
- **`CRE-G2`(b): 44 assertions per cell, all passing.**
- **Every pair completes the full ladder in every cell**; no infeasible `(pair, depth)`
  cell and no `adjacent_only` termination on `ALG-B` either. The §0.4 censoring row's
  expectation of material per-depth null counts is met (below), but not by way of
  infeasibility.
- **Cost:** 12–22 s per capped cell, **307 s for the staged B-S3**.

### Owed item 1 is DISCHARGED — for one of its two classes, not both

The Seam 1 condition was a non-zero reading, or a demonstration that zero is the true
value. **`interiors_null_in_snapshot` is non-zero in all seven cells** and
`null_interior_unbypassable` tracks it almost exactly, which is pin 3's mechanical
prediction behaving as specified: a ruler-null interior is not pressed while any measured
interior remains. **The counter is live and the Stage-0 zero was a true zero, not a dead
wire.**

**`interiors_absent_from_snapshot` is still zero in every cell of both data sets, and that
half of the item stays owed.** It counts nodes a cell keeps that were never in the fetch
population, so it can only fire where a supply rule admits nodes outside
(adopted ∪ `ALG-B`-MK50) — and the staged B-S3 union cell, the likeliest place, reports
zero too. **Do not read the discharge of the null counter as covering the absent counter:
they are two counters, and only one has been shown to move.** The remaining honest routes
are to show the zero is structurally true (the snapshot's key set may simply cover every
node any built cell can keep, which would close it by proof rather than by observation) or
to leave it flagged as unexercised in the findings note.

### What is measured and not read

The null counts rise steeply with the device (`P1b` > `P1a` > `P0` in both supply
families), and rise with depth. **That pattern is exactly what §0.4's "descent partly
unmeasurable" trigger was written to detect, and reading it is `CRE-T11`'s work under
`CRE-C1`'s two reporting populations — not this task's.** It is recorded here as a
measurement and cited to the committed JSONs, never restated. **No `CRE-R` read is
licensed, none is made, nothing is adopted, `REQ-38` is unspent.**

---

## §12 — Closeout outcomes (mid-flight, between `CRE-T10` and Seam 3)

- **A1**: this log is the retained record, appended per task (§9–§11), not at the end.
- **A2-mid**: handoff `2026-08-03-HANDOFF-cre-run-stage2-midflight.md` written from the
  template header, with the **enumerations rather than a self-assessment** — the one set of
  numbers computed and not written down, six decisions taken against, the owner
  conversation not yet in a file, and the open decision **with a position taken**. The Seam
  1 handoff's role line now names it as successor on next actions.
- **A3**: owed item 1 **struck in place** in the Seam 1 handoff as HALF discharged, with
  the date and what satisfied it. The other three conditions were re-tested against reality
  and none has come due.
- **A4**: **not applicable, stated rather than skipped** — no config knob was added, and
  the prereg forbids shipped-code change.
- **A5**: all four ports empty, verified by listener sweep rather than task list. No server
  was started at any point this session and none was left behind; C1 is N/A, so none was
  relaunched.
- **B1**: `docs-lint.sh` **hard checks passed** (its `CAND` lines are cost-function weight
  values, not adjudication figures). The `doc-auditor` then ran on the semantic half and
  returned **no findings at any severity**, having checked the six claims it was asked to
  disbelieve — including that owed item 1 reads as *half* discharged in all four places it
  appears, and that `CRE-G2`(b) never names the `P0` check.
- **B5**: `.claude/` carries **no `CRE-` description at all**, so there is nothing there to
  have gone stale. The plan's task checkboxes are unticked by convention (T1–T7 likewise);
  this log owns completion state. No figure is restated anywhere in the diff.
- **B2, B3, B4**: **deliberately travel to the successor** per mid-flight scaling — they
  want a finished artifact, and `CRE-T11` is unbuilt.
- **C1**: N/A entry queued. Nothing changed that the owner can press.
- **D1-mid**: tree clean and pushed; **nothing untracked**. One real catch: `cre_gates.json`
  had never been committed at T8, because that commit used a pathspec and pathspecs do not
  pick up untracked files. Fixed at `7f458e3`.
- **D3**: all sixteen sweep JSONs carry their cell's `artifact_sha256`; the eleven cell
  checksums were verified against `cre_builds.json` at session start.
- **D4**: builder **164 passed**, `CRE-` analysis **66 passed** (38 at Seam 1, plus the 28
  added here), api **230 passed**, frontend **107 passed**.
- **D5**: draft PR #71, its body carrying gate outcomes, the four deferrals with their
  conditions, provenance, and what must not be re-litigated.
- **D6**: standing layer delta **exactly 0 on both units** — unconditional **44,494**
  characters, conditional **2,155** lines, both equal to the Seam 1 figures. This session
  touched neither `CLAUDE.md`, `.claude/`, nor `memory/`.

---

## §13 — `CRE-T11`: criteria figures, the run-state map, and SEAM 3

`cre_score.py` + `test_cre_score.py` (33 tests) → `cre_scores.json`. **FIGURES ONLY, NO
VERDICTS**, the `fi_stats` precedent: no `CRE-R` read is evaluated, none is made, nothing
is adopted, `REQ-38` is unspent. Figures live in the committed JSON and are **cited, never
restated** — including in this section.

**Two corrections to the mid-flight handoff, both found by reading source rather than by
trusting its summary.** They are recorded here because a successor otherwise inherits both
as settled.

1. **"`CRE-T11` needs no graph artifact" is false for `CRE-C2`.** It holds for `CRE-C1`, `CRE-C4`
   and `CRE-C5`. It fails for `CRE-C2`, whose primary reference the prereg §5 fixes as *the
   production artifact's* top-1%-by-degree set, with the own-graph share reported beside
   it — and **no degree set is committed in any Stage-0/1/2 output** (checked: the string
   `top1pct` in `cre_screen.json` and `cre_gates.json` is the pair-*class* name, not a
   degree set). The plan is internally inconsistent here: its T11 `Interfaces` block lists
   JSON inputs only, while its own `C2` bullet demands both degree references. **The prereg
   governs** (plan §Global Constraints), so `cre_score.py` loads the adopted artifact and
   the eleven cells through the existing sha-asserting loaders (`load_adopted`,
   `load_cell`). Cost: about two seconds. The figures-only *output* discipline is untouched
   — what the handoff was protecting was the seam, and the seam is intact.
2. **Owed item 1's remaining half is discharged, and against the handoff's position.**
   Its proof premise — the snapshot's key set bounds every cell, so
   `interiors_absent_from_snapshot` is structurally unexercisable — **does not hold.** The
   snapshot's key set is (adopted node set) ∪ (`ALG-B`-MK50 node set): two **pruned**
   populations. `S0b`, `S1` and `S3` all prune *less* than MK50, so a looser arm keeps
   artists MK50 stranded and the snapshot therefore never covered. The premise bounded the
   *crawl*, which is true and not the relevant bound. Measured by set-difference over all
   eleven cells (figures in `cre_scores.json` → `run_state_map.unmeasured_class_counters`):
   **every cell carries such nodes**, rising monotonically with how loosely the arm prunes,
   and far higher on `ALG-B` than `ALG-E` — which is what the two-population key set
   predicts. **Verdict: the counter is `live_but_unfired`, not unexercisable.** Its zero is
   a true zero about *delivery*, not about existence: the counter only ever inspects
   journey interiors, so it is silent on nodes that exist and are never routed through.
   **Consequence worth carrying forward:** no artist delivered mid-journey in any cell was
   scored on the absent class's 0.5 neutral prior, so plan pin 2's class choice — measured
   by the analyst as worth 1–2.5 whole hops — never moved a delivered path. **A residual
   remains and is named rather than closed:** *why* none was delivered is not measured. The
   plausible mechanism is that these nodes are exactly the weakly-connected ones a tighter
   prune stranded, and weakly-connected nodes are unlikely to sit on a least-cost path;
   that is inference, not a result.

**One defect in this session's own output, caught after the first run.** The run-state map
read a `cre_d1.json` / `cre_d3.json` key named `outcome`. **That key does not exist** — the
committed records name their result `branch`. `dict.get` returned `None` silently, and the
map reported `cre_r_readable: false` on a **complete** run, which is not a safe failure but
a wrong answer: it would have told the Stage-3 session that no read was licensed. Fixed,
and `test_run_state_reads_the_committed_stage0_key_not_a_remembered_one` now asserts the
committed key exists and that `outcome` does not. **This is the plan's own warning
discharging as written** ("expect the plan's code snippets to be broken, and find out by
running them"; a name-resolution check tests neither arity nor attributes) — here the name
was mine rather than the plan's, and only running it surfaced the defect.

**What was implemented, against which pin.** The uniform drop over **pin 9's** partition —
four groups (`canonical-E` 8 members, `canonical-B` 6, and the two staged `S3` cells each
alone with their §0.2 baseline), computed from each sweep's committed `infeasible_cells`
and **never re-derived from the padded ladder** (handoff claim 4). **All four dropped sets
are committed** at `cre_scores.json` → `uniform_drop_partition`, one per group, and are to
be read there — recorded as computed because a drop set that was never computed and one
that was computed and came back empty are indistinguishable in the output otherwise.
`C1` with plan pin 4's two reporting populations, the §0.4 null-share trend and its
`descent_partly_unmeasurable` trigger, the d3–5 descriptive band marked `never_a_bar`, and
the `C6` headroom companion stored only with its denominator and mean frontier size
(analyst m13). `C2` on plan pin 6's deterministic `(degree desc, mbid asc)` ranking, gated
on the primary reference only. `C4` baseline-relative per `CRE-AM2`, with the two anchors
marked `no_binding_form` and the `CRE-R3` shape stored **as a flag, never a sentence**.
`C5` on the two companions with their two separate licences (`CRE-AM1`).

**Two things stated rather than omitted.** `CRE-C5`'s analyst-M8 obligation (the
labelled-node and ≥ 2-measured-agreement shares beside any `B-S2` attribution) **has no
cell to attach to**: `CRE-D1` fired `not_supported`, so no `B-S2` cell exists. And the §0.3
`w_floor` guard fixes **no threshold**, so its boolean is deliberately the *conservative*
rule — any non-zero differential firing sets it — with both magnitudes stored beside it, so
the findings note reads the size and not the flag. Inventing a threshold there would have
been a criterion wearing bookkeeping's clothes, which is not the executor's column.

**Tests: 33, and the green was shown to go red** before it was believed (`working-style`
memory: a new instrument is not evidence until it has been). Two tampers, both caught:
re-deriving the uniform drop from the padded ladder (2 tests red), and pricing a ruler-null
interior at 0.0 instead of skipping it (1 test red — the `FAM-AM1.8` violation). One test
of mine was wrong on first run and the code was right: an all-tie ceiling fixture at N=101
takes two slots, not one.

**`cre_r_readable` is `true`**, with no unrun specified cell and both Stage-0 branches
committed. That is the §6 *run-state precondition* only — it says a read is not barred by
an unrun cell. **It evaluates no `CRE-R` and this session has read none.**

---

# SEAM 3 — the criteria figures are computed and committed

**The Stage-3 findings note is the next session's work, and it must be a session that did
not run the sweeps** (plan §"What is NOT in this plan"). It is written from
`cre_scores.json` + the prereg, never from any session's memory — the four-part shape,
every identifier carrying the plain sentence fixed for it in §5 before any result existed,
the summary naming whatever cuts against it, and `CRE-R` reads under §6's wording
constraints.

## §14 — Closeout outcomes (Seam 3)

- **A1**: this log, appended per task; §13 is `CRE-T11`.
- **A2**: handoff `2026-08-04-HANDOFF-cre-t11-seam3.md`, from the template header. The
  mid-flight handoff's role line now names it as successor **on next actions**.
- **A3**: owed item 1 **struck in place, discharged** with what settled it. Items 2–4
  re-tested against reality rather than re-listed: item 2 (the affine `pop_raw` map) is
  **not yet due** — no cross-cell `pop_raw` sentence exists to carry it, and
  `cre_scores.json` contains none; item 3 (`S2` share quoting) is **discharged by the
  no-cell branch** above and recorded as such; item 4 (the barred cross-read) stands. Two
  new deferrals, each with a condition: the `--out`-argument row the plan named, and the
  pre-existing Snyk LOW.
- **A4**: **inapplicable, said rather than skipped.** Analysis-only track; it adds no config
  knob and moves no default. `BuilderConfig` and `ApiConfig` are untouched.
- **A5**: all four ports (8000, 5173, 8138, 8139) swept and **empty**. No server was started
  at any point this session and none was left behind; C1 is N/A, so none was relaunched.
- **B1**: `docs-lint.sh` **hard checks passed**. Its check-4 candidate was a **real finding
  and is fixed**: the execution plan still declared itself `ACTIVE` after its last task
  completed. Check-5's bare-identifier candidates are the known committed `A`-series
  collisions — **never renamed**, per the forward-only rule. The `doc-auditor` then ran the
  semantic half and returned **four findings, all real and all fixed**, having checked the
  six claims it was asked to disbelieve. **The HIGH is the one worth carrying:** the doc
  map's row for the *Seam-1* handoff still asserted owed item 1 was **half** discharged —
  true when written, false since §13, and invisible to every check that looks at the
  documents this work *changed*, because that row was not one of them. The propagating half
  of a struck deferral is the defect class, and it is why B1 is not made conditional on a
  document having changed. Also fixed: a stale section header over the two struck items in
  the mid-flight handoff (the same failure one level up); "all four groups dropped zero
  cells" **restated in three documents** in violation of the one-document rule, now cited to
  `cre_scores.json` in all three; and bare `C`-series tokens qualified to `CRE-`. **Its one
  escalation was upheld against this session's own output**: the handoff's §6 paraphrase
  enumerated **four of the five** standing bars, silently narrowing a constraint the
  Stage-3 author is told to rely on. Replaced with a citation to §6 and a note saying why —
  the fix for a lossy enumeration is never a better enumeration.
- **B2**: `cre_score.py` is imported by `test_cre_score.py` and is an entry-point script
  like `cre_screen.py` / `cre_sweep.py`. No orphan; `cre_gates` keeps its inbound import.
- **B3**: the two tampers above, on the invariants whose failure would matter.
- **B4**: the module docstring's central claim — that the prereg forces the artifact load —
  was checked against `cre_common.py`, `cre_screen.json` and `cre_gates.json` before it was
  written, which is how correction 1 was found.
- **B5**: `.claude/` carries **no `CRE-` description**, so nothing there can have gone
  stale. No figure is restated in the diff; §13 cites `cre_scores.json` and quotes no
  number from it.
- **C1**: N/A entry queued. Nothing changed that the owner can press.
- **D1**: tree clean, nothing untracked.
- **D3**: the sixteen sweep JSONs carry their cells' `artifact_sha256`; the eleven cell
  checksums and the adopted artifact's were re-verified by the loaders on this run.
- **D4**: builder **164 passed**, api **230 passed**, frontend **107 passed** (18 files),
  `CRE-` analysis **33 passed** for this task.
- **D6**: standing layer delta **exactly 0 on both units** — unconditional **44,494**
  characters, conditional **2,155** lines, both equal to the mid-flight figures. This
  session touched neither `CLAUDE.md`, `.claude/`, nor `memory/`.
