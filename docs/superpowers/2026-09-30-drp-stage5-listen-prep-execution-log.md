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
