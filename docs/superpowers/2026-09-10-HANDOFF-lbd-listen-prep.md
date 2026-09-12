# Handoff — `LBD-AM5`: the served-population maps built, the `LBL-` listen 1 ready, 2026-09-10 (night)

**Role: SUPERSEDED on next actions by
[`2026-09-11-HANDOFF-lbl-listen1-read.md`](2026-09-11-HANDOFF-lbl-listen1-read.md)** — the
listen it prepared has since been run, unblinded and read. **Next actions only:** this
document remains the record of what was built and why, and its "Claims that must NOT be
reverted" all still bind. ⚠ **Its "the listen has NOT been run" statement is now false** and
is left as written, because it was true when written. *(Original role:)* **ACTIVE — the
CURRENT handoff for the `LBD-` track.** Supersedes
[`2026-09-10-HANDOFF-lbd-task67-build-stage.md`](2026-09-10-HANDOFF-lbd-task67-build-stage.md) on
`LBD-` next actions. It does **not** state project status — [`NEXT.md`](NEXT.md) owns that, and is
**deliberately not updated by this session** (see "Owed").

**A SEAM handoff, at the owner's stop.** Steps 1–3 of the owner's instruction are done: the
amendment is committed, both maps are built and serialised, and listen 1's materials are prepared.
**The listen has NOT been run and no journey exists on any map.** Nothing further starts on a
session's initiative: running the listen spends the owner's ear, and listen 2 is not prepared until
he has heard listen 1.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
— the **`LBD-AM5`** block at the end of §10 and its §12 row, beside `LBD-AM1`–`AM4`.
**Retained log:** [`2026-09-10-lbd-listen-prep-execution-log.md`](2026-09-10-lbd-listen-prep-execution-log.md).
**Figures:** [`builder/analysis/2026-09-10-lbd-served-population/README.md`](../../builder/analysis/2026-09-10-lbd-served-population/README.md),
nowhere else. **Harness and runner brief:** `builder/analysis/2026-09-10-lbd-blind-listen/`.
Branch `lbd-listen`, draft PR #116, worktree `C:\Users\charl\worktrees\music-app-lbd-listen`.

---

## What a cold reader most needs

1. **Listen 1 compares the map the app serves with `LBD-A0V`** — *ListenBrainz's rules, run by us on
   today's listening data, over exactly the artists the app serves.* Listen 2 (`LBD-A0V` against the
   two-listener bar, `LBD-A5V`) is registered, its map is built, and **its materials are not prepared**.
2. **The pairs are new** — drawn by a rule committed before it ran, from the owner's familiarity
   ranking **minus every `GBL-AM1` endpoint**, because a journey he remembers from `GBL-`/`CAU-` would
   identify a side. The two listens share no pair. **He may amend the pairs before any journey exists.**
3. **Both answers are asked on every row and d0 counts** (`LBL-Q1` coherence, `LBL-Q2` novelty, bar 8
   of 24 each), a clip-problem box feeds an *underpowered* read, and **a split is FAIL**. Each is a
   correction `GBL-` results §6 asked for, or a departure the amendment states a reason for.
4. **Fame is the served map's own records, artist by artist** — all three `LBD-AM5-4` checks passed
   on both maps (figures owner §4). No fame stage was re-run.

## Claims that must NOT be reverted

- **The drop list for `V` is `unlistenable_drop_algb_20260805.json`, not `LBD-AM4`'s `20260809`** —
  the latter would drop 31 artists the app serves (`LBD-AM5-3`). `LBD-AM4-3` stays right for `P`.
- **Every name, disambiguation and clip lookup on the listen page comes from the served map, by
  MBID, for both sides.** The two maps harvest names from different sources; a spelling difference
  would be a tell.
- **Two edge-count units, a factor of two apart** — connections (degree sum ÷ 2) vs CSR entries (every
  sidecar's `"edges"`). The first build run was refused because a bound mixed them; it was corrected
  from the unit, not the build's value (log, Step 2). Never compare a figure across the two.
- **This session must not run generation, and neither may any session that has read the figures
  owner** (`GBL-` harness log §3.4). The runner reads `RUNNER-BRIEF.md` and nothing else; the write-up
  is a further fresh session.
- **`LBD-X4` travels with any listen-1 verdict**: 439 artists took part in the served build's cap step
  and cannot in `LBD-A0V`'s. No sentence attributes a listen-1 verdict to "the data" without it.

## What is on disk and must not be rebuilt

Identities are owned by the figures owner (§0–§5); paths only here.

| | |
|---|---|
| `LBD-A5` derived table | `C:\unsung-fast\lbd-pairs\A5\A5.parquet` (+ manifest with its curve reproduction) |
| archives | `C:\unsung-fast\lbd-archives\A0V\`, `…\A5V\`, `…\population_msw_mbids.txt` |
| **the two listenable maps** | `C:\unsung-fast\lbd-artifacts\LBD-A0V.bin`, `LBD-A5V.bin`, each with its `.bin.json` sidecar |
| the pins the harness reads | `builder/analysis/2026-09-10-lbd-blind-listen/lbl_maps.json` (listen 1 only), `lbl_pairs.json` |
| everything from `LBD-AM4` and Task 4 | unchanged; see the previous handoff |

## What I know that is not in the durable record

- **The listen will be longer than `GBL-`'s.** Two questions per row and up to three tracks per
  artist; `GBL-` budgeted about five hours for the same eight pairs and three depths. Splittable.
- **Two gates were pre-checked because a failure would waste a sitting:** G2 (the served map routes
  identically to production's `graph-lux4.bin`) and G1's loader on `LBD-A0V`. Both compare artifacts
  only; no journey was computed. The run-state gate (c) has only fired on the api's test fixture.
- **Decided against:** reusing `GBL-AM1`'s pairs (memory tell); `GBL-`'s name-only clips (not needed
  when one id source serves both sides); an owner swap at the run-state gate (ordered reserves keep the
  runner mechanics-only).
- **Another session is working on documentation conventions concurrently** (owner, 2026-09-10). This
  session's shared-document edits are small: one sentence on the pre-registration's `docs/README.md`
  row and new rows for its own new files.

## In flight

Nothing, once `LBD-A5V`'s build record is committed. No server, no listener; ports 8000/5173/8765 clear.

## Owed, and by whom

| | |
|---|---|
| **Owner — first** | **rule on `LBD-D6`**: `LBD-A4` was to run before any further arm was pre-registered, and `LBD-A5` was registered on your instruction without it (`LBD-AM5-7`). Optionally, **amend the pairs** — only before any journey exists |
| **Owner — then** | **start a fresh runner session** in the worktree with the instruction to follow `builder/analysis/2026-09-10-lbd-blind-listen/RUNNER-BRIEF.md` and read nothing else; do the listen; **keep PR #116 open** until the runner has committed the answers and result to `lbd-listen` |
| **A further fresh session** | the write-up of `lbl_listen1_result.json`, reading the answers and notes before the result (`GBL-` write-up order); then `closeout`, which also rewrites `NEXT.md` |
| **Only if listen 1 reads PASS or TIE, and you choose to spend it** | a session adds listen 2 to `LISTENS` and `lbl_maps.json` and prepares its materials — listen 2's own pairs are already fixed |
