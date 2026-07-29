# Pre-registration — source algorithm selection (`AS`)

**Role: ACTIVE.** Governing document for the algorithm-selection measurement. Committed
**before any sampled arm runs**; the git commit timestamp is the evidence that it
preceded the result, which is the part that cannot be reconstructed afterwards.

**Owns no figures.** Scoring and path-quality figures live in
`findings/2026-07-21-scoring-adjudication.md` and are cited, never restated. The figures
this design produces are owned by `builder/analysis/2026-07-29-cap-selection-sim/`.

**Identifier namespaces, disjoint by construction** (CLAUDE.md: no two load-bearing
objects share an identifier). Arms are `ALG-A` … `ALG-F`. Criteria are `AS-C1` …,
gates `AS-G1` …, reads `AS-R1` …, the noise floor `AS-N`. `ALG-` and `AS-` are unused
elsewhere in this repo, checked 2026-07-29. **Forward-only: nothing here is renamed
after commit.**

---

## 0. What this measures, and what it explicitly does not

The crawl asks ListenBrainz Labs for each artist's similar artists. The `algorithm`
parameter is a **closed enum of six values** — validated against the live endpoint on
2026-07-29 (`CS-P0e`), which rejects anything else with a 400 naming the permitted set.
`limit` cannot exceed 100 and `threshold` cannot go below 10 at any permitted setting.

A scope probe (`CS-P0c`, `CS-P0e`) found that production's setting returns **zero**
candidates below the 90th popularity percentile for five named superstars, while one
other permitted setting returns roughly fourteen each. This design measures whether
that holds beyond five artists, and which parameter is responsible.

**It does not license adoption.** No result here adopts anything, changes any default,
or authorises a re-crawl. A re-crawl costs about 4¼ hours and produces a *new graph*
rather than a patched one — that is the owner's decision, and on this project's terms it
would additionally owe a blind listen before adoption (`REQ-38`). Every read in §5 is
written to stop at a recommendation.

**It is not the cap-selection simulation.** That work is separate, still owed under
`MKS-5b`, and is unaffected by any result here.

---

## 1. Arms — the factor table

Every arm is one of the six permitted `algorithm` values. All share the constant prefix
`session_based_days_…_session_300_…_skip_30`; only the varying columns are shown.

| Arm | days | contribution | threshold | limit | filter | Isolating baseline — differs by exactly one column |
|---|---|---|---|---|---|---|
| **ALG-E** | 7500 | 5 | 10 | 100 | True | *(production — the baseline others are read against)* |
| **ALG-B** | 7500 | **3** | 10 | 100 | True | **ALG-E** — contribution only |
| **ALG-A** | **1825** | 3 | 10 | 100 | True | **ALG-B** — days only |
| **ALG-F** | **1800** | 3 | 10 | 100 | True | **ALG-A** — days only, and only by 1.4% |
| **ALG-D** | **75** | 5 | 10 | 100 | True | **ALG-E** — days only |
| **ALG-C** | 9000 | 5 | **15** | **50** | **absent** | **none — four columns differ** |

**`ALG-C` is barred from every one-knob attribution in this document.** It may be
described; no observed difference involving it may be attributed to threshold, to limit,
or to the missing filter. There is no arm differing from it by one column and none can be
constructed, because the enum is closed. This clause is load-bearing: §5 must not read a
`ALG-C` difference as evidence about `threshold_15`.

**`ALG-A` vs `ALG-F` is the noise floor, `AS-N`.** A 25-day difference in a ~5-year
window is 1.4%; the two are the same measurement taken twice. Whatever separates them is
the source's own variability, not an effect. This is what every other comparison is
measured against, and it is the reason this design has calibrated effect sizes rather
than invented ones.

### Held constant, and why each is genuinely constant under the intervention

Per CLAUDE.md, this section exists because the factor table cannot see a term that is
inert in the baseline *for a reason the intervention removes*.

1. **The artist set queried.** The same 200 MBIDs go to all six arms. Genuinely
   constant — the request differs only in the `algorithm` string.
2. **Request ordering and timing.** Requests are **interleaved by artist across arms**
   (artist 1 through all six, then artist 2, …), never arm-by-arm. Any drift in the
   service over the run therefore hits all six arms equally instead of loading onto
   whichever arm ran last. Constant by construction of the harness.
3. **⚠ The popularity yardstick is NOT genuinely constant, and this is the dormant term.**
   "Below the 90th percentile" is measured against the **current adopted artifact's**
   popularity percentiles, because that is the only ranking that exists. A returned
   candidate absent from that artifact has no percentile and is excluded from the
   sub-decile count.

   In `ALG-E` that exclusion is inert: production returned **zero** absent candidates for
   all five superstars. Under `ALG-B` it is not: **104** of its returned candidates were
   absent. So the yardstick silently drops exactly the artists the intervention adds —
   a term inert in the baseline for a reason the intervention removes, which is the
   confound this section exists to catch.

   **Handling, fixed now:** absence is promoted to its own criterion (`AS-C2`) and
   reported per arm alongside `AS-C1`. **`AS-C1` systematically UNDERCOUNTS any arm with
   high absence**, so it is a lower bound for such arms and must be reported as one. No
   read may treat `AS-C1` as a complete measure of an arm's obscure-candidate yield
   without `AS-C2` beside it.
4. **The sampling frame.** Strata are drawn from the adopted artifact, so the sample
   **cannot contain artists we have never crawled.** Every arm is equally blind to them;
   constant across arms, but a real limit on what any read can claim (§6).
5. **Score currency.** Raw `score` values are **not comparable across arms** — a count
   under `contribution_3` and one under `contribution_5` do not mean the same thing, and
   a 1,800-day window accumulates differently from a 7,500-day one. Constant *within* an
   arm only. Enforced in §3: cross-arm comparisons use ranks and set overlap, never score
   magnitudes.

---

## 2. Sample

**200 artists, stratified by popularity percentile of the adopted artifact**
(sha256 `4cb84ef9…`, asserted at run time), drawn with a **fixed seed recorded in the
harness** so the draw is reproducible (design §9 determinism):

| Stratum | Population | Drawn |
|---|---|---|
| top 0.1% | 75 | 40 |
| top 1%, below top 0.1% | 667 | 40 |
| top decile, below top 1% | 6,678 | 40 |
| 50th–90th percentile | ~29,700 | 40 |
| below 50th percentile | ~37,000 | 40 |

Deliberately over-weighted at the top: the defect under investigation (`DD-F1`) lives
there, the bands are tiny, and an unstratified sample of 200 would draw about **one**
artist from the top 0.1%.

**Cost:** 200 × 6 = 1,200 read requests, rate limited. Roughly ten minutes. Nothing is
written to the archive; `build` remains offline and the replay test still proves it.

---

## 3. Criteria — each with its plain-language sentence, fixed before any result exists

Per CLAUDE.md the sentence is written **now**, beside the threshold, so it cannot be
reshaped to fit a result. Owner-facing text quotes identifier **and** sentence.

- **`AS-C1` — sub-decile yield.** *"For a famous artist, how many artists outside the
  most popular 10% does the data source offer as similar?"* Mean count per artist, per
  stratum. **Lower bound only** where `AS-C2` is non-zero (§1.3).
- **`AS-C2` — novelty / absence.** *"How many of the artists it suggests are ones our
  map has never seen?"* Mean count per artist, per stratum. Read **with** `AS-C1`, never
  instead of it.
- **`AS-C3` — overlap with production.** *"If we switched, how much of the current map
  would survive?"* Shared-candidate fraction and Spearman rank correlation against
  `ALG-E` on the same artist. **Descriptive — no threshold, no gate.** It sizes the cost
  of a switch; it does not decide one.
- **`AS-C4` — the tail.** *"Does it run out of suggestions, and how weak are the last
  ones?"* Share of artists returning fewer than `limit`, and the within-arm score at
  ranks 1 / 50 / last. Within-arm only (§1.5).
- **`AS-C5` — sub-median yield.** *"Does it reach genuinely obscure artists, or just
  slightly-less-famous ones?"* Mean candidates below the 50th percentile. Separates a
  real reach into the tail from a shuffle inside the popular band.

---

## 4. The decision rule and its effect sizes

**Fixed now; the noise floor's value arrives with the run, the rule does not.**

> **`AS-N` (the noise floor).** For each criterion and each stratum, `AS-N` is the
> absolute difference between `ALG-A` and `ALG-F` on that criterion in that stratum.
>
> **A difference between any two arms counts as REAL only if it exceeds `3 × AS-N` on
> the same criterion in the same stratum.** Three, not two, because `AS-N` is a single
> realisation rather than a variance estimate, so the bar is deliberately conservative.
>
> **If `AS-N` is exactly zero** for a criterion and stratum, the rule would admit any
> difference at all. It does not: an absolute floor of **≥ 1.0 candidate per artist**
> applies in that case, so a difference of 0.02 candidates cannot be decisive merely
> because the noise floor happened to round to nothing.

**Gates, each with its own effect size** (CLAUDE.md: a trigger without one fires the
expensive response on noise):

- **`AS-G1` — arm integrity.** An arm is **void** unless it returns HTTP 200 for
  **≥ 95%** of the 200 sampled artists. A void arm is reported and excluded; it is not
  retried into validity.
- **`AS-G2` — design informativeness.** If the `ALG-E` vs `ALG-B` difference on `AS-C1`
  in the top-1% strata does **not** exceed `3 × AS-N`, the design is uninformative and
  **`AS-R2` (the null) fires** — not a request for a larger sample. A bigger sample is a
  separate decision with its own cost, and this gate must not be dischargeable by simply
  running more.

---

## 5. Reads — every possible result, including the null

**Each read names the run state it presupposes.** Any instruction keeping a specified
run alive gets its own sentence, never a subordinate clause.

- **`AS-R1` — the interaction confirms.** *Presupposes all six arms complete and
  non-void across all five strata.* If `ALG-B` exceeds `ALG-E` on `AS-C1` by more than
  `3 × AS-N` in the top-1% and top-0.1% strata, **and** `ALG-A` does not exceed `ALG-E`
  by that margin, then the effect requires **both** the long window and the low
  contribution — an interaction, not a single lever. Recommendation: `ALG-B` becomes the
  named re-crawl candidate in the rebuild plan. **Does not authorise the re-crawl.**
- **`AS-R2` — the null.** *Presupposes all six arms complete and non-void.* If no arm
  exceeds `ALG-E` on `AS-C1` by more than `3 × AS-N` in any stratum, algorithm selection
  is **not** a lever for `DD-F1`. The rebuild plan drops this strand, and `DD-F1` returns
  to being unfixable on this source — which makes it a product question under `REQ-37`,
  the owner's, not an engineering one. **The five-superstar result would then stand as a
  small-sample artefact and must be reported as retracted.**
- **`AS-R3` — it works but it is a different graph.** *Presupposes `AS-R1` has fired.*
  If `AS-C2` is large or `AS-C3` shows low overlap, `ALG-B` is not an improvement to the
  current graph but a replacement for it. Every path-quality figure this project holds
  was measured under `ALG-E` and would become historical. Recommendation must say so
  explicitly and must **not** present the switch as an incremental fix.
- **`AS-R4` — partial.** *Presupposes all six arms complete.* If the effect clears
  `3 × AS-N` in the top-1% stratum but not the top-0.1%, then the remedy reaches the
  tier below the superstars and **not the superstars themselves** — which is where
  `DD-F1` was ruled. Report as a partial remedy; do not let the top-1% result stand in
  for the pair class the ruling was about.
- **`AS-R5` — contribution alone.** *Presupposes all six arms complete.* If `ALG-A`
  *also* clears the bar against `ALG-E`, the days column is not required and the lever is
  contribution alone. This contradicts the five-artist probe, which found `ALG-A` at
  zero; the probe would be the thing overturned, and this document says so in advance.

**No read licenses adoption, and none is a recommendation to re-crawl.** The output of
this design is a named candidate and its costs.

---

## 6. Weakest link, stated in advance

1. **The sampling frame cannot see artists we never crawled** (§1.4). If `ALG-B`'s value
   is largely that it reaches an unseen population, this design measures only the shadow
   of that — `AS-C2` counts them but cannot rank them.
2. **`AS-C1` undercounts high-absence arms** (§1.3). It is a lower bound for `ALG-B`,
   reported as one.
3. **Nothing here measures whether the new edges are any good.** More obscure candidates
   may mean thinner co-occurrence evidence and noisier similarity. That is an ear
   question under `REQ-38`, not a metric one, and no result here can settle it.
4. **`ALG-C` contributes no attributable evidence** and is run only because it is free.

---

## 7. Amendments

Amendments are appended here with a date and a reason, **never by editing a committed
clause**. A material mid-flight amendment is also a handoff seam (CLAUDE.md).

*None yet.*

**2026-07-29, post-run — `AS-H1`, a read-structure gap.** `AS-R1` and `AS-R5` were
written as if the strata would agree about `ALG-A`; they do not (it clears the bar at
top 1%, not at top 0.1%), so **neither read fires as written**. Recorded in the execution
log §4 rather than resolved toward whichever read flatters the result. Any successor
pre-registration must make its reads stratum-aware. Same shape as `TB-P5H-7`.

**2026-07-29, post-run — `AS-H2`, a criterion confound found after the fact.** `AS-C1`
and `AS-C5` are absolute counts, so they conflate "fewer sub-decile candidates" with
"fewer candidates at all". `ALG-B` returns 58% fewer candidates below the median, which
is the whole of its apparent decrease there. Execution log §5 reports the rate as an
explicitly post-hoc diagnostic. **A successor design should pre-register the rate
alongside the count.** No clause above is edited.
