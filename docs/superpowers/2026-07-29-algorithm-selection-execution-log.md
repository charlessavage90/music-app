# Execution log — source algorithm selection (`AS`), 2026-07-29

**Role: COMPLETE** for the measurement it records. Governing document:
[`specs/2026-07-29-algorithm-selection-preregistration.md`](specs/2026-07-29-algorithm-selection-preregistration.md),
committed **before any sampled arm ran**.

**Owns no path-quality figures.** The figures below are source-candidate measurements and
are owned by `builder/analysis/2026-07-29-cap-selection-sim/`. Scoring and path-quality
figures remain in `findings/2026-07-21-scoring-adjudication.md`.

**Nothing here is adopted. No default changed. No re-crawl authorised.**

---

## 1. What ran

Six permitted `algorithm` values × 200 artists stratified by popularity percentile
(40 per stratum, seed `20260729`), interleaved by artist so service drift hit all arms
equally. 1,200 read-only requests, ~18 minutes. Artifact `4cb84ef9…` asserted at run
time. Nothing written to the archive; `build` remains offline.

Harness: `as_run_arms.py` (collect only) and `as_score.py` (all criteria), **both
committed before the run finished**, so neither could be shaped by the result.

## 2. Gates

| Gate | Outcome |
|---|---|
| **`AS-G1`** arm integrity, ≥95% HTTP 200 | **PASS** — all six arms 200/200 (100%). No void arms. |
| **`AS-G2`** design informativeness | **PASS** — `ALG-B` vs `ALG-E` on `AS-C1` clears `3 × AS-N` in both top strata. |

**`AS-N`, the noise floor** (`ALG-A` vs `ALG-F`, 1.4% apart in window), on `AS-C1`:
0.05 / 0.10 / 0.025 / 1.30 / 0.20 across the five strata top-down. It behaved as the
design hoped — near zero at the top, larger in the mid band — which is what makes the
top-stratum bars (0.15 and 0.30) tight enough to be meaningful.

## 3. Primary result

`AS-C1` — *"for a famous artist, how many artists outside the most popular 10% does the
source offer as similar?"* Mean per artist. **Lower bound wherever `AS-C2` > 0.**

| stratum | ALG-E (prod) | **ALG-B** | ALG-A | ALG-F | ALG-D | ALG-C |
|---|---|---|---|---|---|---|
| top 0.1% | 1.175 | **11.25** | 1.225 | 1.175 | 2.5 | 1.45 |
| top 1% – 0.1% | 5.15 | **11.35** | 5.875 | 5.975 | 7.95 | 9.0 |
| top decile – 1% | 27.7 | 28.95 | 25.775 | 25.8 | 3.175 | 36.4 |
| 50th–90th | 33.6 | 28.1 | 18.7 | 17.4 | 0.275 | 22.55 |
| below median | 7.175 | 3.05 | 1.475 | 1.275 | 0.025 | 4.225 |

`AS-C5` — *"does it reach genuinely obscure artists, or just slightly-less-famous ones?"*
At the top, `ALG-E` is effectively zero (0.075) and `ALG-B` is 4.025 — **decisive**, and
it is the more demanding criterion of the two.

All `ALG-B` deltas above are flagged DECISIVE against their stratum's bar, in **both**
directions.

## 4. `AS-H1` — a read-structure gap, recorded rather than resolved in our favour

**Neither `AS-R1` nor `AS-R5` fires as written**, and the pre-registration is at fault,
not the result.

`AS-R1` required `ALG-A` **not** to clear the bar against `ALG-E`. `AS-R5` required that
it **did**. The truth is stratum-dependent and the document assumed the strata would
agree:

- **top 0.1%** — `ALG-A` delta +0.05 against a bar of 0.15: **does not clear.** The long
  window is *required* here.
- **top 1%** — `ALG-A` delta +0.725 against a bar of 0.30: **clears.** Contribution alone
  does something, but `ALG-B` delivers roughly eight times more.

**Substantive reading, stated plainly:** the interaction holds where the ruling that
motivated this work applies (the very top), and weakens one band down. Both reads are
recorded as not-fired; the result is **not** re-labelled to match whichever one flatters
it. Same shape as `TB-P5H-7`, and any successor pre-registration must make its reads
stratum-aware.

## 5. `AS-H2` — what cuts against `ALG-B`, and it is real

**`ALG-B` decisively REDUCES `AS-C1` and `AS-C5` in the two lowest strata** (−5.5 and
−4.125 on `AS-C1`). The summary must not omit this.

A **post-hoc diagnostic, not pre-registered and labelled as such**, explains the
mechanism: expressed as a *rate* of candidates returned, `ALG-B` is never worse —

| stratum | ALG-E rate | ALG-B rate |
|---|---|---|
| top 0.1% | 0.012 | 0.113 |
| below median | 0.438 | 0.445 |

— because `ALG-B` returns **far fewer candidates** for obscure artists: **6.85 vs
16.375** below the median, a 58% reduction in supply.

**That is not a reprieve; it is a different cost.** A sparser candidate list at the bottom
means fewer surviving edges after the mutual-kNN cap, which is exactly the mechanism
behind `MKS-6` / `F1` (zero-intermediary paths) and `MKS-3` (stranding). **`ALG-B` would
plausibly strand more obscure artists than production does.** Unmeasured here — it needs
a built graph, not a candidate list.

## 6. `AS-R3` fires — it is a different graph, not a patch

`AS-C3`, overlap with production, at the top: **Jaccard 0.42** (top 0.1%) and **0.49**
(top 1%) — **less than half the candidate set is shared** — with Spearman 0.67–0.73 on
the candidates that *are* shared, so even those are reordered. `AS-C2` (artists our map
has never seen) is **16.8 per artist** at the top against production's 0.025.

Adopting `ALG-B` would not improve the current graph. It would replace it, and **every
path-quality figure this project holds was measured under `ALG-E`.**

For contrast, `ALG-C` is nearly production (Jaccard 0.80, Spearman 0.994 at the top), and
`ALG-D` (75-day window) collapses — 0.05 candidates per artist below the median. Neither
is a candidate.

## 7. What this does and does not license

**Does:** `ALG-B` (`days_7500 · contribution_3`) is the named re-crawl candidate for the
rebuild plan, on the strength of a decisive, calibrated lift at exactly the pair class
`DD-F1` was ruled about.

**Does not:** authorise the re-crawl, adopt anything, or claim the resulting graph is
*better*. Nothing here measures edge quality — more obscure candidates may mean thinner
co-occurrence evidence. That is an ear question under `REQ-38`.

**Deferred, with conditions:**

| Item | Condition |
|---|---|
| Stranding under `ALG-B` (`AS-H2`) | **Before any adoption decision** — needs a built graph; the candidate-supply drop is measured, its graph-level effect is not. |
| Stratum-aware reads (`AS-H1`) | **If any successor algorithm pre-registration is written.** |
| Edge-quality / blind listen | **If the owner picks up the re-crawl** — `REQ-38`. |

---

## 8. The scope probes that preceded the design (`CS-P0` … `CS-P0f`)

Run before the pre-registration existed, because the simulation the owner had agreed to as
the first task rested on a premise testable in minutes. Scripts and outputs:
`builder/analysis/2026-07-29-cap-selection-sim/`. Artifact `4cb84ef9…` asserted by every one.

- **`CS-P0` / `CS-P0b`** — reproduced `DD-F1` independently (all five named superstars have
  zero neighbours below the top decile) and found the top-decile *population* is 87.8% **not**
  defective. Banded, the collapse is monotone and concentrated at the very top: the
  zero-downward share runs 8.2% → 45.1% → 79.1% → 87.5% from the top decile inward. **So
  "famous artists have no downward edges" was aimed at the wrong population.**
- **`CS-P0c`** — the decisive one. Superstars are offered **zero** sub-decile candidates by
  the crawl itself, so no cap rule can select one. For the top 1% broadly candidates do
  exist (mean 5.57) and the cap discards **72.8%**. This is what re-sequenced the plan.
- **`CS-P0d`** — obscure candidates rank late (mean 64.5 of 100); famous artists' lists
  saturate the limit, most artists' do not (39.1% of a 3,000 sample).
- **`CS-P0e`** — validated the owner's finding that `algorithm` is a **closed enum**. Killed
  two levers: see §9.
- **`CS-P0f`** — the source `score` is symmetric (9,486 of 9,487 reciprocated pairs identical
  both directions; rank correlation between directions **0.12**). So mutual k-NN adds no
  similarity evidence — it re-tests one number against each endpoint's *other* scores, and
  where it rejects an edge the refusing endpoint is the **more popular** one **87.4%** of the
  time (42.7% of reciprocated pairs rejected). This derives Phase 1 log §2.10's depletion
  finding arithmetically from source data rather than observing it in the artifact. **No rule
  change is proposed; `MKS-5b` still requires a simulated degree bound first.**

## 9. `STC-6` is killed, not deferred — and one of this session's own recommendations is retracted

The `algorithm` parameter accepts only six values. `threshold` is 10 or 15 and production is
already on **10**; `limit` is 100 or 50 and `limit_500` is rejected.

- **`STC-6`** — "re-crawl at a lower co-occurrence threshold" — has **nothing lower to ask
  for.** Its condition is *known-unreachable*, which the closeout standing rule makes a kill
  rather than a reschedule. Struck in `NEXT.md`.
- **"Re-crawl asking for longer candidate lists" is retracted.** It was this session's own
  recommendation, made before `CS-P0e` ran, and it is impossible.

## 10. Closeout record

**D4:** builder 115 passed, api 217 passed, frontend 107 passed across 18 files. Run, not
recalled.

**D6 — the standing context layer:** unconditional **44,113 characters (delta 0)**;
conditional **2,121 lines (delta 0)**. Nothing was added to `CLAUDE.md`, `.claude/` or
`memory/` this session. The two `docs/README.md` rows are conditional-corpus, not standing
layer.

**D1/D3:** tree clean at commit. No artifact adopted, created or modified — the only
artifact in play remains `graph-t15-tiebreakfix.bin`, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted by every
script here. **No new archive was written**; `build` remains offline.

**A4 (default-flip):** no config knob was added or changed. `BuilderConfig.algorithm` still
carries `contribution_5`; `ALG-B` is a *candidate*, and flipping it is the re-crawl decision,
which is the owner's. Nothing is sitting at an old default pretending to be shipped.

**B2 (reachability):** the nine new files are standalone analysis probes, imported by nothing
by design — the established pattern for `builder/analysis/`. Not orphans.

**B3 (vacuous tests):** no tests were added, so nothing to spot-check. The suites above are
pre-existing and were run as a regression check only.
