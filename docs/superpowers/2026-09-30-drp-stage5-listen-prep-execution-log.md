# Execution log — `DSL-` blind listen PREPARATION (seam 5C, `DRP-AM7`), 2026-09-30

**Role: RETAINED EXECUTION LOG. ACTIVE. Owns no figures** — `dsl_g1.json`, `dsl_prescreen.json` and
`dsl_pairs_drawn.json` / `dsl_pairs.json` own their counts. **`dsl_prescreen.json` and `dsl_prescreen.md`
are SIDE-LABELLED: a runner or write-up session must not read them.** Governing text: `DRP-AM7` in
`specs/2026-09-27-issue-200-depth-remedy-preregistration.md` §14, including its seam-5A review. Harness:
`builder/analysis/2026-09-30-drp-stage5-listen/`. Branch `charlessavage90/drp-listen-prep`, issue #244.

**This session is barred from running the listen and from the write-up** (`DRP-AM7-5`): it runs
`DSL-G1`, the pre-screen, the strike and pin, and a generation dry-run. It shows the owner endpoint
names only — never an interior, length or side.

## Preconditions, checked before any step ran

- PR #265 merged (`7e7bfa3`); harness present; `dsl_prescreen.py` committed at `f56eaa2`, never run.
- Both artifacts hashed and matched their sidecars and the lattice's pins (`drp_common.A0_SHA`;
  `drp_s1_build.json`, with `drp_g3.json` PASS on the same sha). Every input pin in `dsl_common.py`
  matched on LF-normalised bytes, and both cell shas appear in the stage-3b and stage-3c READMEs.

## Corrections reported to the owner before execution (he said go)

1. `DSL-G1` runs ~240 ladders (80 lattice pairs × incumbent, challenger, red control) against the
   pre-screen's ~100, so it is the longer step; run in the background with `python -u`.
2. **"Each tier needs 6 survivors"** (the handoff, and `DRP-AM7`'s closing count) is not step 8's rule.
   Step 8 stops only below 12 survivors across both tiers; a tier's gap is filled from the other
   tier's next in rank order, recorded. The script implements step 8.
3. `dsl_prescreen.select` fills tier by tier, so if `DRP-T1` had < 4 survivors its gap would take
   `DRP-T2`'s top survivor before `DRP-T2`'s own primaries. Step 8 reads as own-tier first. Inert
   unless `DRP-T1` is short; if it is, stop and bring it to the owner rather than run the code's reading.
4. `RUNNER-BRIEF.md` cuts the runner's worktree from `origin/main`, so this branch — with the pinned
   `DSL_PAIRS_SHA` — must be merged before the runner starts.

Checked and not a correction: generation's G1 check hashes only `dsl_journeys.py`, so pinning
`dsl_common.py` afterwards leaves `dsl_g1.json`'s recorded `dsl_common.py` sha stale but breaks
nothing; Gate N's familiarity list (file plus known pool) is `LBA-AM7-3`'s definition; `--dry-run`
returns before any write, including the sealed directory.

## Steps

### Step 1 — `DSL-G1`: PASS

Reproduction exact on both sides for every `DRP-T1` and `DRP-T2` lattice pair; the red control
(ceiling off on `DRP-S1`) diverged from `DRP-S1P3` at press ≥ 4 on every pair. Counts and timing:
`dsl_g1.json`. Committed before the pre-screen ran.

### Step 2 — pre-screen: an import-order fault, fixed before its first successful run

The first launch died at import (`ModuleNotFoundError: drp_common`) before it read any input or wrote
anything: `main()` imported `drp_common` before `dsl_journeys`, which is what puts the lattice's
directories on `sys.path`. The tests import only the pure functions and never run `main()`, so they
could not see it. **Fix: the two import lines swapped, nothing else** — no rule, gate, key or
selection line touched. Committed on its own before the pre-screen ran again, so the commit order
still shows the script preceding its output (the `855b090` precedent). `dsl_generate.py` imports
`dsl_journeys` alone and is not affected.

Second launch, on `88f45c3`, ran to completion: enough survivors in both tiers, 12 selected, no
cross-tier fill (so correction 3 above stayed inert). The outputs record the script's LF sha, which
equals the committed `88f45c3` script. Counts: `dsl_prescreen.json` (**side-labelled**). Draw:
`dsl_pairs_drawn.json` (names, MBIDs, tiers, pool ranks only).

### Step 3 — the owner's strike and the pin

Shown the 12 drawn pairs by endpoint name only (positions 1–8 primary, 9–12 reserve; no interior,
length, side or tier), **he struck position 8**. `dsl_pairs_final.py --strike 8` filled it with the
next unstruck reserve of the same tier (position 11), as `DRP-AM7-2` step 9 requires; no cross-tier
fill. `dsl_pairs.json` committed first, then `DSL_PAIRS_SHA` pinned in `dsl_common.py` in its own
commit; the committed blob's sha equals the pin.

### Step 4 — generation `--dry-run`: every gate passed, nothing written

G1 (PASS on this `dsl_journeys.py`), G2 (both maps against sidecar and pin; `DRP-G3` on `DRP-S1`), G3
(pairs pinned, 8 primaries), G6 (name, disambiguation and Deezer id identical for every MBID —
`DRP-AM7-6`'s refusal did not fire), G4 (0 substitutions), G4' (Gates D and N re-asserted), G5
(differential) and G7 (page leak guard) all ran before the dry-run's early return. A sha256 listing of
the harness directory and of `.superpowers/` taken before and after is identical, and `.superpowers/`
does not exist.

## Defects found in the plan and the harness

- **Import order in `dsl_prescreen.main()`** (above): untested because the suite exercises only the
  pure functions. Fixed before the first successful run.
- **The runner cannot read the handoff.** `RUNNER-BRIEF.md`'s do-not-read list covers every handoff
  and execution log under `docs/superpowers/`, so a "handoff for the runner" there would unblind it if
  read. The seam-5C handoff is therefore addressed to the **owner**, and carries a launch prompt that
  points the runner at `RUNNER-BRIEF.md` only.
- **Merge before the runner is the clean order, not the only one.** The brief cuts the runner's
  worktree from `origin/main`, and also allows branching from a branch the owner names if this PR is
  not merged. Correction 4 above overstated it as a hard dependency.
- **"Each tier needs 6"** (`DRP-AM7`'s closing count) is not step 8's stop rule (correction 2). Inert
  this time — both tiers had more than 6 survivors. The amendment is left unedited; this log is the
  correction's address.

## Operational

`DSL-G1`: about an hour (80 pairs × 3 ladders, ~45 s a pair). Pre-screen: under an hour (50 pairs ×
2 ladders). Dry-run: a few minutes. All run from `api/` with `python -u` in the background.

## Provenance (D3)

Maps read by absolute path and verified by the lattice's loader at every step: today's
`graph-lba-a6.bin` sha `28311d81…`, `graph-drp-s1.bin` sha `418fe666…` (full values: `dsl_g1.json`'s
`map_sha256`). Post-strike pairs: `dsl_common.DSL_PAIRS_SHA`.

## Deferred

- **#267** — `select()`'s fill order for a short *first* tier, and `main()` having no test. Condition:
  before any future listen adapts `dsl_prescreen.py`. This listen's copy stays as run.

## Closeout measurements

- **D6:** no edit to `CLAUDE.md`, `.claude/` or memory, so delta 0 in both layers. Totals measured
  against `C:/Users/charl/.claude/projects/C--dev-music-app/memory`: unconditional 46,650 characters,
  conditional 3,538 lines.
- **D4:** harness 52 passed, api 347 passed, builder 292 passed; frontend untouched, not run.
- **Snyk:** the harness directory scanned after the import-order edit: 0 issues.
- **B2:** no module added. **B3:** the only code change is an import swap, and its proof is the
  pre-screen's successful run; the missing `main()` test is #267. **C1:** nothing the owner can
  press changed, so nothing is queued. **A4:** no config knob added. **A5:** no server or listener
  started; every background job finished.
- **B6:** `NEXT.md` 360 lines (budget 250) and `docs/README.md` (budget 400) were over before this
  session; its net additions are the new top block, which replaced the old one, and three map rows.
