# `CAU-` — coherence audit of the gentle arm's novel artists

**Role: ACTIVE (pre-registration, not yet run).** Fixes the workload, the instrument, the
red control, and the read of every possible outcome **before any judgement is recorded**.
The git commit timestamp of this file is the evidence the readings were not fitted to a
result. **This document is frozen on commit**; changes come as `CAU-AM` amendments, and
corrections that move no bar come as `CAU-CORR`, a separate series (the `GBL-CORR1`
precedent).

**Identifiers.** This document owns the `CAU-` series. Collision-checked against `docs/`,
`builder/analysis/` and `.claude/` on 2026-08-04: unused.

**Why the freeze is stricter here than usual.** The result this audit follows is already
known to everyone involved, including the listener. That is exactly when a read is easiest
to reshape without noticing, so every bar, every denominator and every branch below is
fixed now.

---

## 0. What happened before this, in one paragraph

The `GBL-` blind listen ran and returned the pre-registered null — margin 3 of 16 deep
rows against a bar of 5 (`findings/2026-08-04-gentle-arm-blind-listen-results.md`, which
owns those figures). **That null stands and this document does not touch it.** The owner
then identified a confound in the instrument, and it is the reason this audit exists: a
30-second slice of one arbitrary track cannot support a coherence judgement about an artist
the listener has never heard of. That was harmless while every interior artist was familiar,
and it stopped being harmless at exactly the point an arm began delivering unfamiliar
artists — so **the measurement degrades only in the arm that succeeds.** The owner also
recorded, unprompted, that had he read the row pick as "which do you prefer" rather than as
a coherence question he would likely have chosen the new graph more often, and that this
must not be edited in after the fact. It has not been.

## 1. The question, and the three this does not ask

**Plain sentence, fixed now:** *"When the rebuilt app hands me an artist I have never heard
of, does that artist actually belong where it was put?"*

Not asked, and **barred from every sentence of the result** (§6):

- **Which graph is better.** This is a one-arm audit. There is no comparison and no margin.
- **Whether the journeys hang together end to end.** The unit here is one artist against its
  immediate neighbours. The owner's "today's app takes weird detours when you look at the
  whole path" observation is a *global* property this instrument cannot see, and a good
  local score says nothing about it in either direction.
- **Anything about novelty.** Settled at 8–0 by `GBL-Q1` and not re-opened. Because this
  audit sends the listener to Spotify, where monthly listeners are displayed, the spec §6
  WGLL bound is live: **any novelty observation arising during this run is void by
  construction** and may not be recorded as a finding.

## 2. Material

**Source:** the **G arm only** (`B-S1-P1a`) journeys already generated and committed for
`GBL-`, at depths **d10 and d20** across all eight approved pairs. No new journeys are
generated; no graph is rebuilt; no shipped code is touched. Raw source:
`builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_page_data.json` with the arm
identity in `gbl_result.json`.

**Population, measured before this document was committed: 54 distinct interior artists**
(endpoints excluded, deduplicated across the 16 deep journeys). Journey lengths d10/d20 run
3 to 11 cards, median 6.

**Unit of judgement: a step.** One interior artist shown with its immediate predecessor and
successor from the journey it came from. Steps are presented in **shuffled order**, not
grouped by journey, so that no judgement is anchored by the one before it.

## 3. The instrument

For each step the owner records one of:

| Verdict | Meaning |
|---|---|
| **FITS** | This artist belongs between these two |
| **DOESN'T FIT** | This artist does not belong between these two |
| **CAN'T TELL** | Still unable to judge after listening |

**The listening rule, and it is the point of the whole exercise.** For any artist he cannot
confidently place, he goes to Spotify (or any source he likes) and listens to **several
tracks** — as much as it takes to form a view. There is no 30-second limit and no single-track
limit. An artist he already knows is judged on sight; that is not a lesser judgement and it
is counted in the same denominator.

Free-text reason per step, optional but encouraged — the `GBL-` notes corpus was the most
operationally useful thing that listen produced.

**`CAN'T TELL` should now be rare, and its rate is itself a reading** (`CAU-C3`).

## 4. The red control — and the audit is void without it

Standing project rule: *a green result from a new instrument is not evidence until the
instrument has been shown to go red.*

**Injected steps.** A pre-registered number of steps have their middle artist **replaced by
a random artist drawn from the same graph**, sampled from the same obscurity band
(`fame_lb_pctl`) as the artist it replaces, so it cannot be spotted by fame alone. These
steps are indistinguishable in presentation from real ones.

- **Count: 12 injected steps**, fixed now, sealed before the run.
- The injection map is written to a **gitignored file under `.superpowers/`** before serving
  and read by nobody until every real step is judged (the `BLIND-MAPPING.json` convention).
- **`CAU-G1` (gate, and the audit's validity condition): at least 10 of the 12 injected
  steps must be judged DOESN'T FIT.** Plain sentence: *"the audit can tell a bad
  recommendation from a good one."* Below 10, **the instrument is blunt and every reading
  below is void** — reported as void, not as a weak pass, and no result sentence survives.

**The injected steps are excluded from every denominator in §5.** They test the instrument,
not the graph.

**Why this protocol is lighter than `GBL-`'s.** The only thing needing concealment is which
steps are injected. There is no arm to blind, no expectation to protect on either side, and
therefore no mechanics-only runner session is required. A sealed file is sufficient, and the
session that builds the audit may also serve it, provided it discloses nothing about the
injections.

## 5. Reads — fixed in advance, with effect sizes

**Denominators are declared here so neither can be chosen after the fact.** Both are
reported, always, side by side:

- **`D_all`** — all 54 real interior artists.
- **`D_lookup`** — only those the owner had to look up (could not place on sight).

`D_lookup` is the harder population by construction and will score worse; **reporting it
alone would be pessimistic and reporting `D_all` alone would be flattering.** Neither is
"the" number.

### `CAU-C1` — the primary outcome

**The fraction of real interior artists judged FITS, over `D_all`.**

Plain sentence: *"how often the rebuilt app's artists actually belong where it put them."*

| Outcome | Plain sentence | Action |
|---|---|---|
| **≥ 75% FITS** | "The new artists it digs up genuinely belong in the journey." | The coherence worry is answered on this evidence. The `GBL-` null is **explained** — not overturned — and adoption becomes a live decision for the owner, taken outside this document |
| **≤ 50% FITS** | "The new artists it digs up are substantially noise." | Decisive against the arm on coherence. No further listen is owed and Option A stays closed |
| **50% < FITS < 75%** | "It is a real improvement in what it finds and a real cost in what it gets wrong." | **Genuinely ambiguous, and the audit says so rather than picking a side.** The next move is the owner's and this document names no default |

**The bar is the owner's to ratify before the run**, because "how many wrong cards is too
many" is a judgement about what the app should be, not a methodological choice. Proposed
above with reasoning; **it is not fixed until he has signed off, and nothing runs before he
does.**

### `CAU-C2` — concentration

**The largest number of DOESN'T FIT artists falling in any single journey.**

Plain sentence: *"whether the bad ones are sprinkled about or whether some whole journeys
are wrecked."*

**Trigger: any single journey carrying ≥ 3 DOESN'T FIT artists.** This fires independently
of `CAU-C1` and is reported even when `CAU-C1` passes — a good average with one ruined
journey per eight is a different product than a good average spread thin, and a rate alone
cannot tell them apart.

### `CAU-C3` — residual unjudgeability

**The fraction of real steps still CAN'T TELL after listening properly.**

Plain sentence: *"how often even proper listening left me unable to say."*

**Expected to be near zero.** Above **15%** it is a finding in its own right: it would mean
unfamiliarity, not clip length, was the barrier, and that the whole diagnosis in §0 is
wrong. Reported prominently if it fires, because it falsifies this document's own premise.

### Run state every read presupposes

**All 54 real steps and all 12 injected steps judged.** A partial run licenses **no read**;
what is owed is named and the run resumes or is abandoned by the owner, never summarised.
`CAU-G1` is evaluated **first**; if it fails, nothing else is computed.

**Sample-size knob, fixed now because it must not be chosen later:** if the owner wants the
run smaller, he may set a target count **before generation**, and the steps are then drawn by
seeded random sample from the 54 with the seed committed. **Post-hoc exclusion of any step is
forbidden.**

## 6. Barred reads

- **No comparison with today's app**, in any sentence, at any strength. `GBL-` §5's run-once
  rule binds its verdict; this audit does not re-run it, because it measures a different
  thing (one artist's local fit, not a journey-level preference between two arms) — and it
  must not be used to smuggle a comparison back in. **The `GBL-` null stands whatever this
  finds.**
- **No whole-path or "detour" claim**, in either direction — §1.
- **No novelty claim** — §1, and the WGLL monthly-listeners bound.
- **No adoption on any outcome.** Adoption and the re-crawl remain the owner's, taken
  outside this document. A `CAU-C1` pass makes adoption *decidable*; it does not decide it.
- **No attribution** to the data set, the connection rule or the ramp individually — the
  `GBL-` §2 package-comparison constraint travels, and one arm cannot isolate anything.
- **"The coherence question is now settled" is barred even on a pass**, because the global
  defect in §1 remains unmeasured by anything.

## 7. Amendments

*(none yet)*
