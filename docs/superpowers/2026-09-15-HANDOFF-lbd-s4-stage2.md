# Handoff — `LBD-S4` stage 2 measurement complete, retired mid-flight, 2026-09-15

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-16 by
[`2026-09-16-HANDOFF-lbd-s4-stage3.md`](2026-09-16-HANDOFF-lbd-s4-stage3.md) — `LBA-D8` stage 3
has since RUN and the owner stop is reached. ACTIVE for everything else it records**, and its
claims-not-to-revert list still binds. ⚠ **Its "Owed, by a fresh session" item 2 was wrong when
written**: it names "the `doc-auditor` findings this session could not adjudicate" as handed
forward, and the stage-2 execution log's B1 records that all four were resolved and **none** was
handed forward. What genuinely carried was `closeout` B2/B3/B4, now discharged. *(Original role:)*
**ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-14-HANDOFF-lbd-s4-stage1.md`](2026-09-14-HANDOFF-lbd-s4-stage1.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

⚠ **MID-FLIGHT, and the trigger was the context-size tell, not a failure.** Stage 2's *measurement*
is complete and reported; the session was retired on the owner's instruction before the remaining
bookkeeping, at ~409k tokens. **`CLAUDE.md`'s degradation tell is a COMPLETENESS failure**, so this
note does not certify its own completeness — the sections below are **enumerations, not
assessments**, per `closeout` A2-mid. Cold-read it back before acting on it.

**It owns no figures.** They are owned by
[`../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md).
Reasoning is [`2026-09-14-lbd-s4-stage2-execution-log.md`](2026-09-14-lbd-s4-stage2-execution-log.md).

---

## What happened

**Governing document unchanged:** `specs/2026-09-14-lbd-s4-adoption-preregistration.md` (`LBA-`),
§11's `LBA-AM1` and `LBA-AM2` before §3 or §5. **No amendment was added by this session.**

1. **All 14 pins re-verified** (`LBA-D9`). `T_A4.parquet` absent from every searched path.
2. **Seven archives emitted.** All 21 counts reproduce stage 1 exactly.
3. **Six cells built, one stopped.** **`LBA-G2` FIRES on `LBA-A9`** — the corner's projection
   exceeded the 24 GiB bar (the figure is the stage-2 README's §2a). **Unbuilt for a resource
   reason.**
4. **`LBA-M1` taken on eight arms. `LBA-G1` fires on NOTHING — on those eight.** `LBA-A9` was
   never built and never sized, so the corner is outside that claim; see point 2 below.
5. **Reads taken: `LBA-R0` and `LBA-R1`.** Nothing else in §7 is reachable.

## ⚠ The five things a reader is most likely to get backwards

**1. `LBA-G2` firing on `LBA-A9` is a resource fact about this machine, not a finding about the
corner.** §2.6's three barred conclusions are attached to that cell's own record. The one that
matters most: **"we could not build it here" and "it is too big to serve" are different claims**,
and the second needs `LBA-M1`, which that cell does not have. `build_from_archive` holds neighbour
objects in a Python dict during its first pass — a property of the **builder**, not `GraphStore`.

**2. "No arm fires `LBA-G1`" is a statement about the EIGHT SIZED arms.** `LBA-A9` was never built
and never sized. The `LBA-G1`(b) ratio is monotone in population across all eight and the largest
built arm reaches **93 % of that bar** (figures: stage-2 README §3b and §4). Do not read `LBA-R1`
as covering the corner.

**3. `LBA-R1`'s own text contains a clause this stage cannot support.** It reads *"the decision then
rests on `LBA-M2`, `LBA-M3` and `LBA-M4` alone"* — true about where the decision sits, but **all
three are unmeasured here**. No sentence anywhere presents that clause as evidence about them.

**4. The gate reads the MEDIAN; the `U` row's cost is in the TAIL.** On the two `U` arms p95 is
roughly double what it is on every `V` and `P` arm (figures: stage-2 README §3b). §5 requires both
reported and the gate to fire on the median alone. **It did not fire. That is the specified
reading, and the tail is still the number worth looking at.**

**5. Every `U` arm is built in a configuration the shipped code names.** `pipeline.py:303-318`'s
refusal text calls `drop_unlistenable=False` *"an experimental control and never a shipping
configuration."* All three `U` cells are built that way because no census covers that population
and the guard refuses. **`drop_no_release_tail` and `drop_featured_credit` have no guard at all and
silently under-filter over `U`.**

## Claims not to revert

- **`LBA-D8`'s prohibition held and must keep holding:** a cell is stopped **only** on `LBA-G2`'s
  stated bar. `LBA-A9` was stopped that way and on no other ground.
- **`s4_instrument.py` supersedes stage 1's `stage2_build_instrument.py`** for any future use —
  that module raises on **every real build**. Do not "simplify" stage 2 back onto it. It imports
  the fit rule and the 24 GiB bar from stage 1 unchanged, so **no bar moved**.
- **Boot memory is measured on BARE re-serialisations for all eight arms.** Measuring a census
  build as-built would double-count the `LUX-4` metadata that `metadata_ratio` models. Do not
  "fix" this back.
- **`LBA-A1`/`LBA-A3` reused and sha-verified, never rebuilt** (`LBA-D9`).
- **The `U`-row acceptance floors are UNCALIBRATED gross-loss tripwires and are labelled so.** Two
  cells is not a calibration. On that row the edge floor **cannot see a silent cap-rule revert**.
- **`LBA-G3` fired at stage 1**; no census was run and none is owed by this stage.
- Nothing re-reads any `LBD-` criterion; `LBD-C1` is not cited as passed; `LBD-X6` stands; both
  `LBL-` verdicts remain run-once.

---

## Every number computed that is NOT written down elsewhere

*(Enumerated, not filtered for relevance — `closeout` A2-mid.)*

1. **The final six-point `LBA-G2` fit's coefficients: slope 0.6164 GiB per million archive
   neighbour rows, intercept −0.165 GiB.** Reproduces `LBA-A9`'s projection (README §2a) exactly.
   Only the *projections* were recorded, never the fitted coefficients. **These two numbers are
   owned here** — they exist in no other document. ⚠ **The intercept is slightly
   NEGATIVE**, which is a fit artefact rather than a physical claim, and any future extrapolation
   far below the measured range should not use it naively.
2. **Bare-versus-carrying ratio for the two reused artifacts:** 25.7 → 19.3 MB and 26.9 → 20.3 MB,
   i.e. **1.33× and 1.32×**. In `s4_bare_copy_LBA-A*.json`, not in the README.
3. **Pool adjacency for the pair draw:** exactly **1 candidate of 2000** was adjacent in any arm
   map, and **0** in the served map. In `s4_pairset.json`, not in the README.
4. **`_logs/machine_state.tsv` holds 2,760 rows** of free-memory samples across the build chain
   **and was never analysed.** It was collected so "was the machine quiet for this build" is
   answerable; **nobody has answered it.** The build records carry the timestamps to align it.
5. **Total emit wall clock ≈ 37 min; total build wall clock ≈ 83 min** across the six builds.
   Per-cell figures are in the README; the totals are not.
6. **`LBA-A8`'s build was 32.9 min** and is the longest; `LBA-A7`'s 25.9 min. Both in the README.
   **`LBA-A7`'s CPU time was ~12 % of wall clock** — the `U` builds are I/O-bound reading hundreds
   of thousands of archive files, not CPU-bound. Observed once, in a process listing, nowhere else.

## Everything decided against, and why

1. **Editing stage 1's instrument in place** — rejected; that README states its self-test passed
   and quotes the output, and overwriting the module would silently invalidate a committed
   statement. Forward copy instead. ⚠ **Partly revised at closeout**: the `doc-auditor` pointed out
   that stage 1's README is classified **ACTIVE**, not frozen, so it *should* carry a correction —
   a forward-pointer block was added there. The instrument module itself is still not edited, and
   that half of the decision stands.
2. **Reusing the existing `A0` archive for `LBA-A4`** — rejected; re-emitting it reproduced three
   committed counts and proved the wrapper against a **frozen record** before any novel cell.
3. **An 80 % node floor on the `U` row** — rejected before any `U` build, because §2.4 records the
   prune's effect there as unmeasured. *(It would in fact have passed — the measured retentions are
   README §2e. The decision was still right on the information available, and two cells is still
   not a calibration.)*
4. **Adding per-build memory logging to `s4_build.py` mid-chain** — rejected; it would have raced
   the chain and split `script_sha256` across the lattice. Separate sampler instead.
5. **Hand-writing `LBA-A2`'s record after the assertion failure** — rejected; rebuilt instead, even
   though the measurement was valid. Never hand-write a measurement record.
6. **A stored served-map d0 baseline** — rejected; the served median moved **13.8 %** across eight
   runs, so every comparison is back-to-back in one process.
7. **Silently deleting `_projections.json`'s failed-attempt entries** — intended to keep them,
   then deleted them during a restart; the contradiction is **corrected in place and left visible**
   in the execution log rather than back-edited.

## Anything the owner said in conversation that is not yet in a file

- He closed a browser and left the machine ~20:00 for at least an hour, and expected an unrelated
  Claude session on another project to finish within it. **Recorded** in the execution log's
  machine-state section.
- He instructed this closeout to run as a **mid-flight handoff**. Recorded here.
- **Nothing else.** No decision, threshold, preference or ruling was given verbally.

---

## The open decision, and what I would do if I were continuing

**The decision: does stage 3 run, and over which arms?**

**What I would do: run stage 3 over all eight sized arms, including the `U` row.** Reasoning, so it
can be argued with rather than re-derived:

- `LBA-R1` says hosting does not decide this. So the decision genuinely rests on `LBA-M2` /
  `LBA-M3` / `LBA-M4`, none of which exist yet.
- The instinct to drop the `U` row is available and I think it is wrong **at this stage**. Its
  filter is off and its playability can only be estimated — but **`LBA-M2` is fully measurable on
  it**, and `LBA-M2` is what says whether a bigger population wrecks the journeys between artists
  the app already serves. That is the question that would rule the `U` row in or out on product
  grounds rather than on a filter technicality, and it costs one pass.
- **Dropping it now would also make `LBA-R6` and `LBA-R7` unreadable**, since both turn on the
  `P`-versus-`U` contrast.

**What I would NOT do:** treat the query-cost result as settling speed. The largest built arm sits
just under the (b) bar and its p95 is a multiple of the served map's (README §3b, §4). **I would measure d0 on the actual container before
anyone concludes the bigger maps are fast enough** — cheap, and it replaces a multiplier taken on a
retired artifact with a direct reading.

⚠ **Two things about this that are the owner's and not a session's:** whether stage 3 runs at all,
and whether the `U` row is worth carrying given its filter state. **`LBA-D2` reserves the threshold
to him** and nothing here selects one.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories. **No listeners on 8000 or
5173 — this session never booted the app.** The machine-state sampler (PID 194136) ran from 20:01
until **stopped during this closeout**; it was an infinite loop and would otherwise still be
running. Two `powershell` processes started 2026-09-15 11:42 and 11:44 are **not this session's**
and were left alone.

**The working tree is clean** — every task was committed as it landed, so `D1-mid`'s usual "name
the untracked paths" is empty. **Nothing is half-written.**

## Artifacts (gitignored — checksum is the only identity they will have)

| arm | artifact | sha256 |
|---|---|---|
| `LBA-A2` | `LBA-A2.bin` | `af49db6320465a158f0a1d9b12fef36d66a020dee0d33179bd7e304925cfc38f` |
| `LBA-A4` | `LBA-A4.bin` | `facace5a038d46dbb51ecaa9b58939ee28bc15f830d2854f4b69b190d52920fa` |
| `LBA-A5` | `LBA-A5.bin` | `30bb396101d2bc6eddd99dc6ce733cb405d4e8d7047ca5dc2efd822a06232ee4` |
| `LBA-A6` | `LBA-A6.bin` | `199b9e20a2fea4d998043bca83ed2f10a3696f84f3e5399f960834770f8f290e` |
| `LBA-A7` | `LBA-A7.bin` | `45579077c7adb212bddf87421d35135eb98b71cacb1b9f0d9a741b8dc2d76dc4` |
| `LBA-A8` | `LBA-A8.bin` | `aa0a96757237f2f97196f69efab7dff0e5a91ad2a83923386f46789c2edd78b8` |
| `LBA-A9` | — | **unbuilt (`LBA-G2`)** |

All at `C:\unsung-fast\lbd-artifacts\`, each with a `-bare.bin` sibling used for sizing, plus the
seven `S4-<arm>` archives at `C:\unsung-fast\lbd-archives\`. A fresh clone has none of them.
**Pair set:** `s4_pairset.tsv`, sha256
`2713e5369719dd39091363d8d0977b8ae2339b4df6a56ad707ca67a967528cc9`.

## Owed, and by whom

**The owner's**, in this order — per `NEXT.md`'s rule this note does not record how far he has got:

1. **Run the queued use-the-app tests** — `TEST-QUEUE.md`, untouched by this work.
2. **Merge the stage-2 PR (#128).**
3. **Decide whether `LBD-AM3`'s override extends to `LBD-A4`** — carried forward, nothing blocked.
4. **Decide whether stage 3 runs, and over which arms.** My position is above.

**A fresh session's, if he says run stage 3:**

1. **Read `LBA-AM1` and `LBA-AM2` before §3 or §5.** Neither was amended by stage 2.
2. **Finish this closeout's deferred items** — the named list in `NEXT.md`'s deferral registry:
   the `doc-auditor` findings this session could not adjudicate, and `closeout` B2/B3/B4, which the
   mid-flight tier hands forward deliberately.
3. **`LBA-M2` needs the served map's neighbour lists per artist** and the four raw quantities
   §4 fixes (`R`, `R_avail`, `b_out` share, forced share, denominator both ways) — none exist yet.
4. **`LBA-M4` will be ESTIMATED, not measured, on every arm** — `LBA-G3` fired, so there is no
   fresh census verdict anywhere, and the split by verdict source §4 requires will show **zero**
   freshly evaluated artists.

Branch `lbd-s4-stage2`, PR **#128** (`gh` says where it is).
