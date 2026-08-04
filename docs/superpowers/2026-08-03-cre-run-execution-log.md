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
