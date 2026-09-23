# Execution log — the `LAL-` listen unblinded and read, 2026-09-23

**Role: RETAINED EXECUTION LOG for the `LAL-` read. ACTIVE. Owns no figures** — every listen
figure is owned by [`findings/2026-09-23-lal-listen-results.md`](findings/2026-09-23-lal-listen-results.md)
and cited here by section. The preparation's record is
[`2026-09-23-lal-listen-prep-execution-log.md`](2026-09-23-lal-listen-prep-execution-log.md).

## Who, and what this session had seen

The fresh **write-up** session `LBA-AM6-5` requires, in the runner's worktree
(`C:/Users/charl/worktrees/music-app-lal-runner`, branch `lal-listen-run`). Before the unblind it
had read `LBA-AM6`, `LBA-AM7`, the harness README, `lal_unblind.py` and the preparation handoff. It had
read **no** pre-screen output, page data or verdict. It prepared nothing and ran nothing before the
runner's commit of the complete verdicts (`c62bdf2`).

## What ran, in order

1. The harness tests passed (56). `lal_unblind.py`'s run-state refusal and its invariance tests are
   what make the read mechanical.
2. `lal_unblind.py` → `lal_result.json`: **`LAL-R1`, PASS on coherence** (figures: results §1.1).
3. Two checks against source before writing, because both became claims in the note:
   - **Artifact identity.** Both files hashed in this session. Each matches its manifest sidecar and
     the sealed pin. The shas are in the provenance section below.
   - **Membership.** Every artist the new map presented, checked against today's map's own
     `mbids`: none is absent (results §1.5). This is why the membership tell could not operate and
     why `LBA-X9`'s disclosed lean did not appear.
4. The note was drafted, then **every named artist in it was placed on its side from the sealed
   journeys** rather than from the owner's L/R wording. This caught three defects in my own draft
   before commit: Ed O'Brien's rows were misnumbered (pair 6 for pair 5); the claim that "2 of 3"
   identified rows carried the clipless card was wrong (it is **all 3**, so the two counter-points
   are one exposure); and the count of named out-of-place artists was wrong (8 became 11). It also
   exposed the owner's own slip in the pair-3 d20 note ("R" for the left side), which the note
   records as a slip. His pick stands.

## Decisions, with reasoning

- **The identified rows are reported, not discounted.** `LBA-AM6-8` assigns that weighing to the
  owner by name. The note gives which way the 3 rows went and deliberately does **not** compute a
  margin without them.
- **Per-depth counts are reported. No attribution is made.** `LBA-AM6-1` bars attributing d10/d20
  to the ramp or the fame ranking. The note carries the count and restates the bar beside it.
- **"No worse on the other" is quoted as frozen, with `REQ-41` applied to the tied axis.** This is
  not a reinterpretation of the read. `LBA-AM6-10`'s "no equivalent from a tie" applies to any tied
  axis.
- **`lal_result.json` is committed**, following the listen-2 precedent (`lbl_listen2_result.json`).
  The sealed files stay gitignored in this worktree.

## Gate outcomes

`LBA-AM6-7`'s run state was met in full and the read was reached: **`LAL-R1`**. No substitution
fired, and no row was lost to clips.

## Deferred

- **A clipless artist that appears on one side only acts as a side tell** (results §4.2). The
  condition is in `NEXT.md`'s deferral table.

## Provenance (D3)

- Incumbent `graph-msw-tu50.bin`: sha256 `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`
- Candidate `LBA-A6-candidate.bin`: sha256 `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b`
- Pairs `lal_pairs.json`: sha256 `b28d1d2b3db099f6fa4b25eb1edfbd67fc91ebbd5212fb80ea1241f695433a24`

## Standing-context-layer delta (D6)

**Unconditional layer: zero.** The branch diff touches no `CLAUDE.md`, `.claude/` file or skill/agent `description:`. In `memory/` (outside git), one false status sentence in `roadmap-pointer.md` (*"no blind listen has been spent"*) was replaced by a pointer to `NEXT.md` of the same length. That file is a recall-only body, so the edit falls in the conditional layer and nets roughly zero. The index `MEMORY.md` is untouched.
