# Execution log — synthesis and deliverability, 2026-07-26

**Role: COMPLETE. The audit trail for the second half of 2026-07-26**, on branch
`low-degree-census` (PR #25). Identifiers namespaced **`DLV-`** — verified unused.

**Touches no shipped code, no graph, no weight, no config default.** Everything here is
read-only measurement and documentation. The path-quality pause is intact throughout.

Figures are owned by the analysis directories cited and are **restated nowhere** in this
log.

---

## 1. What ran, in order

Three units, each committed before the next began where the order was load-bearing.

1. **The queued use-the-app checks were recorded.** The owner exercised all three and
   reported passes with no notes. `TEST-QUEUE.md` marked accordingly. **F1 discharged.**
2. **`findings/2026-07-26-low-degree-synthesis.md`** — identifiers `SYN-1`–`SYN-5`. An
   interpretation assembled across `MKS-`, `CNS-` and `STC-`, none of which read across the
   others. Committed `c13f9a6`.
3. **Two deliverability measurements**, `CWD-1`–`CWD-7`, resolving `SYN-4`.
   - `builder/analysis/2026-07-26-committed-walk-deliverability/` — a re-read of the
     production arm in the committed Track 2 / Track 2F runs (`df34b1c`).
   - `builder/analysis/2026-07-26-obscure-pair-deliverability/` — the missing arm, on
     pairs sampled from the graph's own degree distribution. **Decision rule committed
     first (`8aa6f84`), result second (`9575732`).**
4. **`2026-07-26-RESUME-BRIEF-path-quality.md`** — an ACTIVE cold-session handoff for *if*
   path work resumes (`c675391`). Not a resume signal.

## 2. Decisions, with reasoning

**`DLV-1` — `SYN-4` was written and committed before the measurement that tests it.** The
numeric expectation, both falsifier clauses and the instrument-void condition were fixed in
advance, so the read could not be shaped by the result. Same discipline applied again to
the obscure-pair run, whose decision rule, sampling seed, strata bounds and a **stated
prediction** were committed as a separate commit before the script existed.

**`DLV-2` — the prediction was wrong, and is kept.** Committed at 10–25 %; observed ~3 %,
past the *opposite* threshold. The half of the reasoning that failed is the useful part:
walks starting at a sparse artist leave the sparse neighbourhood almost immediately, rather
than spending early hops among its few neighbours. Recorded as `CWD-7` rather than dropped.

**`DLV-3` — the existing scorer was reused rather than reimplemented.** The instruction
allowed building nothing if reuse was not cheap. `run_arms.py` exposes `walk()` and `arms.py`
the production arm, both importable, so the walk, the depth schedule and the arm are
identical to the committed runs **by construction rather than by transcription**, and
nothing committed was modified.

**`DLV-4` — items already recorded were dropped from the synthesis rather than restated.**
Four of the consulting session's proposed items were already covered by `STC-4`, `STC-6`,
`MKS-5b` and `CNS-2`. The document's value is the assembly; a fifth copy of an existing
finding is the drift the one-document rule exists to prevent.

**`DLV-5` — one figure is quoted in the synthesis under an explicit exception.** The task
instructed both "restate none" and "including that 48 of the top 50…". Resolved by quoting
it once, adjacent to its citation, and flagging in the document that *cap-stranded* and
*rescuable* are different columns. Recorded here because it is a deliberate exception to
`docs/README.md`'s one rule, not an oversight, and the next sweep should re-check it
against the owning table rather than skip it.

**`DLV-6` — the search-entry null was not allowed to close `CNS-1`.** The owner's pass
carries no record of which names were typed, so it is a non-observation. `CNS-1` rests on a
direct worked example, which outranks it. Left open.

## 3. Defects found in the task framing, not in the code

**`DLV-7` — the consulting framing conflated two columns.** "48 of the top 50 fall on the
rule side" merges *cap-stranded* with *rescuable*. They nearly coincide at the top of the
popularity ordering and diverge sharply below it, which is `STC-4`'s entire point.
Corrected in the synthesis rather than propagated.

**`DLV-8` — the degree floor was sized as a small change, and it is not.** A consulting
session put it at a few edges per artist. The obscure-pair run shows nothing was delivered
below four connections and nothing at two, so a floor at two or three lands entirely inside
the range that never gets delivered. Carried into the resume brief as a correction, and it
makes the receiving-side quota a real design problem rather than a formality.

## 4. A correction this session made to its own work

**`DLV-9` — the first deliverability measurement over-counted threefold, self-consistently.**
Track 2 stage 1, Track 2 stage 2 and Track 2F each carry a production arm; the first version
treated them as three samples. They are **byte-identical** — the production arm is
deterministic — so they are one result reproduced three times. Every interior-card instance
figure was inflated 3×.

**What exposed it was not code review**: the three "independent" runs returned *identical*
totals. A gate now enforces the correction (`CWD-3`, and the directory's gate 4). This is
the same shape as the census's `D-4` and `STC-6` — fluent, self-consistent, and wrong.

## 5. Gate outcomes

| gate | where | outcome |
|---|---|---|
| artifact sha256 asserted | both runs | **passed** |
| each run's own recorded sha256 matches | committed-walk | **passed** |
| id-space gate (committed names vs artifact's own) | committed-walk | **passed** |
| byte-identity across the three runs | committed-walk | **passed** — and converted an overcount into a reproducibility result |
| instrument void — a degree-1 interior card | both runs | **not triggered**; runs valid |
| representativeness — ≥ 20 of 24 pairs | obscure-pair | **passed**, 24 of 24 |
| decision rule | obscure-pair | **fired: DO NOT APPEAR** |

**Mutation check (closeout B3):** the artifact gate was deliberately broken with a wrong
expected hash and **aborted** rather than continuing. The gates are not vacuous.

**Test suites (closeout D4), run rather than recalled:** builder **115 passed**, api **153
passed**, frontend **12 files / 64 passed**. No shipped code changed, so this is a
regression check only.

## 6. Corrections to the prior record

**Nothing is overturned.** All of today's work is additive. Two documents gained forward-only
material and nothing was renamed or renumbered:

- `findings/2026-07-26-committed-walk-deliverability.md` gained **§7** (`CWD-6`, `CWD-7`) and
  an inline marker on §5 noting that the measurement it called un-run has now run. Its §5
  confound is **not** resolved by §7.
- `docs/README.md` gained four rows and one amendment.

## 7. Deferred, with success conditions

- **The pricing-versus-arithmetic confound.** Neither deliverability run separates "the
  router prices low-connection artists out" from "they have arithmetically fewer places to
  sit". **Success condition:** discharged by a measurement that separates them, or by an
  owner decision that the degree-floor question is not worth pursuing. **It blocks the
  degree-floor decision** and is the first item in the resume brief.
- **`STC-5` and `STC-6`** carry forward unchanged from the stranding work; **neither is
  due.**
- **`CNS-1`** remains open (see `DLV-6`).

## 8. Standing context layer (closeout D6)

**Net zero.** `git diff --stat` over `CLAUDE.md`, `.claude/skills/` and `.claude/agents/`
for this branch's commits returns empty — nothing was added, nothing compressed. `memory/`
totals **469 lines**, unchanged from the figure `CLM-7` recorded on 2026-07-26.

Four documents were added under `docs/`, which is the routed-around layer and not the
budgeted one. No addition to the standing layer was proposed, so no case for one is made
here — that decision is the owner's and was not needed.
