# Handoff — `LBD-S4` stage 3 complete, the owner stop is reached, 2026-09-16

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-15-HANDOFF-lbd-s4-stage2.md`](2026-09-15-HANDOFF-lbd-s4-stage2.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam, not a mid-flight retirement.** `LBA-D8` stage 3 ran to its end: all four remaining
measurements taken, every §7 read the run state licenses read, and the go/no-go report written.
Nothing is in flight. ⚠ The context-size proxy did fire, **after** step 7 completed — noted in the
closing message as a fact about the session, not as a caveat on the work.

**It owns no figures.** They are owned by
[`../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md).
Reasoning is [`2026-09-15-lbd-s4-stage3-execution-log.md`](2026-09-15-lbd-s4-stage3-execution-log.md),
appended per task. The owner-facing note is
[`findings/2026-09-16-lbd-s4-stage3-go-no-go.md`](findings/2026-09-16-lbd-s4-stage3-go-no-go.md).

---

## What happened

**Governing document unchanged:** `specs/2026-09-14-lbd-s4-adoption-preregistration.md` (`LBA-`),
§11's `LBA-AM1`, `LBA-AM2` and `LBA-AM3` before §3, §4 or §5. **No amendment was added by this
session** — `LBA-AM3` was committed by the previous one, before `LBA-M4` ran.

1. **Pins re-verified by this session**, not inherited: 27 checks across two instruments, all
   match. `T_A4.parquet` absent from every searched path; `LBA-A9`'s stop record clean.
2. **`LBA-M2`, `M3`, `M4` and `M5` taken on all eight sized arms.**
3. **Reads taken: `LBA-R5`** (on the `P` and `U` rows). `LBA-R4` **does not read** on either row;
   `LBA-R4-V` is restated, never reported as a finding; **`LBA-R6`/`LBA-R7` are not adjudicable by
   this design**; `LBA-R8`/`LBA-R9` remain formally unreachable.
4. **The go/no-go report written** in `CLAUDE.md`'s four parts, plus the owner-facing findings note.

## ⚠ The six things a reader is most likely to get backwards

**1. `LBA-AM3-2`'s disqualifier FIRED on every arm where `LBA-G4` could be read**, at a measured
provenance skew many times its bar. **That means the comparison is disqualified, not that its
figure is wrong — and not that it is right.** Neither *"the artists a `U` rule adds are much less
playable"* nor *"they are fine"* is licensed by this stage. The raw delta on the `U` row is large
and would have fired the gate; **it is recorded as disqualified, and a session that reports it as a
finding has inverted the amendment.**

**2. The skew is STRUCTURAL, not an accident of these arms.** Every kept-from-`V` subset draws
**exactly 0.0 %** of its verdicts from the 2026-08-09 recensus, because the 2026-08-05 census
covered the population containing `V` entirely. So under the censuses that exist, an
added-beyond-`V` subset and a kept-from-`V` subset **can never have matching provenance**, and
`LBA-G4` as `LBA-AM1-A5` redefined it is not readable at all without a fresh pass. Do not "fix"
this by loosening the disqualifier — it is `LBA-G4`'s own bar in `LBA-G4`'s own units, and it can
only ever withhold a gate result.

**3. `LBA-R6`/`LBA-R7` being unadjudicable is a DESIGN defect, not a result.** They differ only in
whether the population rules separate on `LBA-M2`'s materially-changed share, and **`LBA-M2`
carries no effect size by design** — §4 fixes it as descriptive and bars attaching one. A session
that picks one of the two reads is fixing a threshold with results in hand. **Both halves are
reported side by side; the branch is the owner's.**

**4. `LBA-R9` — *the numbers say no*, and the row that records stopping as a COMPLETE OUTCOME
rather than an abandonment — is unreachable.** Stopping remains a perfectly good decision; what is
missing is the design's own certificate for it. Do not read the unreachability as an argument
against stopping.

**5. The arm-to-arm `LBA-M2` result is near-pure ADDITION, and it was not known.** Within a fixed
population the looser threshold retains essentially all of the tighter one's neighbour lists.
Nesting had been proved at the **pair-table** level; whether the degree ceiling would undo it at
the **map** level was open, and nothing on the record said it would not.

**6. `LBA-A9` is still a hole, and §2.6's three barred conclusions still attach to it.** In
particular *"we could not build it here"* and *"it is too big to serve"* are different claims.

## Claims not to revert

- **The gated `LBA-M2` statistic is RETENTION, not Jaccard** (`LBA-AM1-A1`, `LBA-AM1-A6`). The
  forced-share null model is reported precisely so a later reader cannot re-adopt Jaccard
  unknowingly — at these length ratios it would flag a quarter to nearly half of artists with
  **zero contribution from neighbour identity**.
- **Every arm is decoded from its BARE artifact**, not its built one. Stage 2 §3a's reasoning
  applied to the structural half. Do not "fix" this back.
- **`LBA-M3`'s table-level control is a property of the THRESHOLD ALONE** — all three arms at a
  threshold share one pair table, so it cannot distinguish the population rules.
- **`LBD-G2`'s bar is admissible as a one-column threshold read on exactly two cells**, `LBA-A5`
  and `LBA-A6` against `LBA-A4` (`LBA-AM1-A9`). Not nine.
- **`LBA-M3` on the `V` row is 1.0 by construction and is `n/a` as a bar, never a finding.**
- **`LBA-G4` is `n/a` on the `V` row, not zero** (`LBA-AM1-A5`).
- **The coverage store was read and never written**, evidenced by sha256 before and after.
- `LBA-D8`'s prohibition held; `LBD-X6` stands; both `LBL-` verdicts remain run-once and final;
  `LBD-C1` is never cited as passed.

## One defect found, with no effect on any result — **`LBA-G2`'s bar is written GB and implemented GiB**

**Found by `closeout` B4.** The pre-registration writes the build-feasibility bar as **24 GB**, in
five places. The implementation is `LBA_G2_BAR_BYTES = 24 * 1024**3` — **24 GiB**, which is 25.77 GB.
Stage 1's instrument introduced it, stage 2's forward copy imports it unchanged, and stage 2's
README and handoff both adopted *"24 GiB"* in prose, which made the implementation self-consistent
and diverged from the governing document silently.

**No cell's disposition changes under either reading, and the margins are comfortable on both
sides.** Recomputed from `_points.json` and `_projections.json` in bytes: the largest projection for
a cell that was built is `LBA-A8`'s **19.30 GB** — under the tighter 24 GB reading with 4.7 GB to
spare — and `LBA-A9`'s is **34.41 GB**, over the looser 24 GiB reading by 8.6 GB. Every measured
build peak is below both.

⚠ **It is NOT fixed here, deliberately.** §11's rule is that a bar's value is never edited, and
deciding which unit governs *after* the results exist is changing a bar with results in hand — even
when the arithmetic shows it changes nothing. **It is filed in `NEXT.md`'s deferral registry with a
condition**, and it is the owner's to settle if any future `LBD-` build gate is read.

## Owed, and by whom

**The owner's**, in this order — per `NEXT.md`'s rule this note does not record how far he has got:

1. **Run the queued use-the-app tests** — `TEST-QUEUE.md`, untouched by this work.
2. **Merge the stage-3 PR (#129).**
3. **Decide whether `LBD-AM3`'s override extends to `LBD-A4`** — carried forward, nothing blocked.
4. **THE GO/NO-GO STOP.** The numbers are in the stage-3 README §1–§6, the inference in §7, the
   weakest links in §8, the options in §9. **No arm is preferred and no threshold named**, and the
   `LBA-R6`/`LBA-R7` branch above is his to settle as part of it.
5. **Settle the `24 GB` / `24 GiB` unit question**, if and when any future build gate is read.

**A fresh session's, if he rules:**

1. **If GO** — §8 of the pre-registration is what it commits to, and **the `REQ-38` blind listen is
   designed COLD, as a separate amendment, written when no journey exists on either map**
   (`LBA-D3`). Its pair draw, generation gate and reads are all fixed before it runs, and `GBL-` §5's
   run-once rule binds it.
2. **If STOP** — nothing is owed but the record, and `LBA-R9`'s unreachability is stated rather than
   worked around.
3. **Either way**, the two cheap measurements in stage-3 README §9 option E remain deferral rows.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories. **No listeners on 8000 or
5173** — this session never booted the app and none was running when it swept the ports. The working
tree is clean; every task was committed as it landed.

## Artifacts (gitignored — checksum is the only identity they will have)

**No new graph artifacts.** This stage built nothing. The eight bare artifacts and six built ones it
decoded are stage 2's, re-verified here; their digests are in
`builder/analysis/2026-09-14-lbd-s4-stage3/_pins/stage3_verify_artifacts.json`.

**New gitignored outputs:** the per-arm `nodes(arm) − V` membership files at
`C:\unsung-fast\lbd-artifacts\s3_stratum4\`, pinned by sha256 in `s3_m3.json`. A fresh clone has
none of them.

**Three table-level control reads** were written beside their parquet tables at
`C:\unsung-fast\lbd-pairs\{A0,T7,A5}\c2a.json` by the frozen `lbd_reads.py`, run unedited. The `A0`
one reproduces the similarity README §6's committed shares exactly.

Branch `lbd-s4-stage3`, PR **#129** (`gh` says where it is).
