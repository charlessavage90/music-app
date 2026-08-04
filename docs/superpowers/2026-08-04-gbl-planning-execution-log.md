# Execution log — the `GBL-` blind-listen design and plan, 2026-08-04 (evening)

**Role: RETAINED EXECUTION LOG** for the session that took the owner's §4 Option A
decision through brainstorm → spec (`GBL-`) → implementation plan. **Owns no figures** —
`CRE-` numbers live in `findings/2026-08-04-cap-reevaluation-results.md`; the one figure
quoted in the spec's §1 carries its citation there. No code was written; the plan's code
blocks are instructions to an executor, not shipped work.

## §1 The owner's decision, and what it fixed

The owner chose **findings §4 Option A**: a blind listen on the gentle arm `B-S1-P1a`
only. During design review he made three further calls, all his column: **eight pairs**
(raised from five, accepting ~5 hours of listening), the **two frozen claims split one
per axis** (novelty `GBL-Q1`, coherence `GBL-Q2` — his catch that the drafted Q1 asked
both at once), and pairs derived from **his Spotify export** with manual supplements.
Execution ruling: **a fresh session on Opus runs the plan inline** (executing-plans);
this Fable session retires at the seam. Same pattern as the CRE execution ruling.

## §2 Decisions taken, with reasoning

1. **Side-by-side page, not two live app instances.** This session first recommended two
   live stacks (the §15/§16 Phase-2 precedent it found first) and argued pre-generated
   journeys "change the object being judged." The owner pushed back; the record agreed
   with him twice over — the C3 listen (`specs/2026-07-22-c3-known-mechanism-blind-listen.md`)
   is the calibrated precedent, and Phase 1 log §3.9 records his verdict that the
   side-by-side format was *materially better* than two instances. Both of this session's
   objections dissolved on the record: bypass is exercised **by construction** (depth
   rows), and `CRE-G1`(a) proves mirror journeys are the app's journeys. Recommendation
   withdrawn, not overruled-and-resented; the log notes it because the two-instances
   precedent is the one a future search finds first, exactly as happened here.
2. **No shipped-code ramp wiring before the listen.** The side-by-side format removes the
   only reason to wire the ramp into `ApiConfig` pre-listen. The ramp enters shipped code
   only on adoption, as its own work.
3. **V0 is the adopted production artifact, NOT the `CRE-` `E-S0` cell.** They are not
   the same graph: `E-S0` was rebuilt with both drop flags applied (cleanup held constant
   across CRE cells), while the artifact the app serves (`graph-t15-tiebreakfix.bin`)
   predates the drop wiring and no rebuild has happened. The spec's comparator is
   "production app as-is," so V0 must be the adopted artifact. Consequence: `CRE-G1`(a)'s
   mirror warrant was earned on `E-S0`, so the plan adds its own **V0 mirror check** —
   real `find_journey` must equal the mirror ladder at every presented depth on the
   adopted substrate (plan Task 4, gate 2).
4. **Clips are name-based for both arms** (`deezer_artist_id=""` forced). Arm symmetry:
   V0's artifact predates `deezer_ids`, and whatever `B-S1` carries must not become an
   arm tell through clip quality. `BYP-13` stays live and shared; the page says to ignore
   clip failures unless they differ by side.
5. **Margin scaling rounded up, not down**: 3-of-10 → 16 × 0.3 = 4.8 → **5**, so the
   enlarged listen cannot fire on a proportionally weaker signal. Owner approved the
   direction implicitly by approving "proportionally"; the round-up is recorded in the
   spec beside the number.
6. **`GBL-` namespace** collision-checked against the corpus before use (no hits).
7. **Depths d0/d10/d20**, not C3's four rows: the measured effect lives at depth ≥ 10,
   and three rows keep eight pairs inside the accepted budget. d0 is an anchor row,
   excluded from the primary read by the spec.

## §3 Decided against, and why

- **Two live app instances** (§2.1) and **a blind-switching proxy** (slicker blinding,
  new plumbing that could void pairs mid-listen). Both declined in favour of the C3 format.
- **Comparing G against `B-S1-P0`** (one-knob ramp isolation): answers attribution, not
  the adoption question the owner is holding. The spec bars attribution sentences instead.
- **A strong-arm (`B-S1-P1b`) row in this listen**: out of scope by the owner's Option A
  choice; the spec's §9 names it as a new-amendment matter, not a re-run.
- **An end-to-end dry run by a planning session**: it would put G journeys in front of
  eyes that know the expected outcome. The smoke test is the runner's, on a throwaway
  pair (RUNNER-BRIEF step 4).
- **`Follow.json` as a familiarity source**: it holds followed *users*, not artists, in
  this export. Corrected in the spec at plan time.

## §4 Defects found in the record or in this session's own output

1. This session's first approach recommendation contradicted the calibrated precedent
   (§2.1) — caught by the owner, then verified against Phase 1 log §3.9.
2. The drafted `GBL-Q1` conflated novelty and coherence — caught by the owner at spec
   review; both questions re-frozen pre-run.
3. The spec's original §3 named `Follow.json` as a source — wrong for this export;
   corrected in place with the date.

## §5 Gate outcomes

No experimental gates ran (no code, no journeys, no results). The plan's own self-review
ran: spec coverage mapped task-by-task, placeholder scan clean, type consistency checked
across tasks (recorded at the plan's foot). Deferral check: the previous handoff's open
Snyk-LOW item came due and is **closed as accepted**, struck in place there with the
revival condition.

## §6 Operational notes with no other home

- The blind-listen tooling precedent lives in gitignored `.superpowers/` —
  `BLIND-MAPPING.json` is the historical key file; `GBL-` seals to `.superpowers/gbl/`
  to stay inside that convention.
- The approved-pair file (`gbl_pairs_approved.json`) is the machine source of truth;
  `GBL-AM1` cites it by sha256 rather than restating it.
- Spotify export observed shapes (2026-08-04): history rows carry
  `artistName`/`msPlayed`/`endTime`/`trackName`; `YourLibrary.json` carries
  `tracks[].artist`. The export lives outside the repo and its path is always a CLI
  argument.
- **D6 standing-layer measurement, 2026-08-04 (evening):** unconditional 44,494
  characters; conditional 2,155 lines. This session's diff touches neither `CLAUDE.md`,
  `memory/`, nor `.claude/`, so both deltas are zero by construction; the totals are
  recorded as the next closeout's baseline.
- **Closeout check outcomes:** lint 1 hard failure (plan role marker), fixed; doc-audit
  3 findings (2 MEDIUM, 1 LOW — two citation gaps, one unnamed handoff reference), all
  fixed in place; suites all green (builder 164, api 230, frontend 107); A4 N/A (no
  config knob added — no code exists yet); B2/B3/B4 N/A for the same reason, and they
  travel to the executor session with the work; ports 8000/5173/8138/8139/8765 all empty,
  nothing started, nothing owned.
