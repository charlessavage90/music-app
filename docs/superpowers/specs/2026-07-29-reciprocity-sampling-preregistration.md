# Pre-registration — does `ALG-B` strand obscure artists? (sampled reciprocity)

**Role: ACTIVE.** Committed **before any arm runs**. The git commit timestamp is the
evidence that it preceded the result; that is the part which cannot be reconstructed
afterwards.

**Owns no figures from elsewhere.** Path-quality and scoring figures live in
`findings/2026-07-21-scoring-adjudication.md` and are cited, never restated. The figures
this document *creates* are its own measurements and belong to
`builder/analysis/2026-07-29-reciprocity-sampling/`.

**Identifier namespace: `RC-`.** Unused before this document (checked against `docs/`).
Roles are disjoint by letter and never shared: arms are `RC-ARM-*`, criteria `RC-C*`, gates
`RC-G*`, reads `RC-R*`, hazards `RC-H*`. **Forward-only — nothing here is renamed once
committed.**

---

## §0 Factor table

The comparison is paired: the **same artists** measured under two source settings.

| Arm | source `contribution_` | Every other request parameter | Estimator, `k`, sample size, seed list | Isolating baseline |
|---|---|---|---|---|
| **`RC-ARM-P`** | `5` (production, `BuilderConfig.algorithm`) | identical | identical | — it *is* the baseline |
| **`RC-ARM-B`** | `3` (`ALG-B`) | identical | identical | **`RC-ARM-P`**, differing in exactly one column |

`ALG-B` is `days_7500 · contribution_3`; production is `days_7500 · contribution_5`. One
parameter differs, which is why this pair is readable at all.

### Held constant, and why each is genuinely constant under the intervention

The intervention is **a change to a source request parameter**. It changes which candidates
come back and with what raw scores. What it must not be allowed to change silently:

- **`max_neighbours_per_artist = 50`.** The estimator computes top-50 explicitly from the
  response, so `k` cannot drift with the arm.
- **`similarity_damping = 0.0`.** Genuinely constant: it is a builder config value, and the
  intervention is a request parameter. Load-bearing consequence, **verified in source rather
  than assumed** (`pipeline.py:218-226`): `mutual_knn_cap` ranks on *unclipped* strengths
  (`damped_strength`), which at damping 0.0 is `log1p(cooc)` — strictly monotone in the raw
  response score. So ranking candidates by raw score is order-equivalent to what the real
  build does, in both arms.
- **`similarity_rescale = "p99_log_clip"` — a dormant term, and it stays dormant for a
  reason the intervention does not remove.** The p99 clip changes *emitted* scores, never the
  cap's ranking (same source lines). The intervention changes raw scores and therefore
  changes each arm's p99 — but since ranking never consults the rescale, the clip cannot
  enter this measurement in one arm only. **This is the term that would otherwise have
  switched itself on in whichever arm succeeded**, and it is the check `CLAUDE.md` requires.
- **`filter_special_purpose = True`. NOT automatically constant.** `ALG-B` returns different
  candidates, so the *set* of placeholder entities differs by arm. The estimator therefore
  applies `is_special_purpose` to both arms identically, from harvested disambiguation, and
  reports how many candidates each arm dropped. Left unhandled this is an uncontrolled
  variable present only in the arm with new candidates.
- **The seed artist list.** Fixed in §2 before any arm runs, identical across arms, so no
  arm can be read on a more or less favourable population than the other.

**Not held constant, and deliberately not measured:** largest-component membership. See
`RC-H1`.

## §1 The question, and what this is not

**`AS-H2`** (deferred, condition "before any adoption decision") records that `ALG-B` returns
**58% fewer candidates below the median**, so it may strand obscure artists while fixing the
famous-pair defect. It closes with an instruction to any successor: *"pre-register the rate
alongside the count."* **This document does that** — it fixes the count, the rate, and their
product, so "fewer obscure candidates" can never again be conflated with "fewer candidates at
all".

**What this is not.** Not an adoption decision, not a quality measurement, and not a listen.
Whether `ALG-B`'s new edges are any *good* is `REQ-38` and is untouched here. The re-crawl
itself remains the owner's call.

**Why not the capped trial crawl the previous handoff named.** Measured, offline, before this
document existed: a `--target`-capped crawl's readable core is structurally famous — 3 artists
below the median at target 3,000, 19 at target 5,000 — because BFS closes the famous core
first and obscure artists are always on the frontier. Reaching a few hundred obscure artists
needs tens of thousands of fetches, i.e. the full re-crawl. Record and figures:
`builder/analysis/2026-07-29-trial-crawl-calibration/`. That instrument is **retired for this
question**, not for all questions.

## §2 The sample set — fixed here, before any arm runs

150 artists drawn from the **adopted artifact** (`graph-t15-tiebreakfix.bin`, sha256
`4cb84ef9…`, verified against its sidecar), stratified on `pop_pctl_full` — a percentile
rank over that artifact, never `pop_raw`, which is a value (log §2.12).

| Band | Seeds |
|---|---|
| top 0.1% | 25 |
| top 1% (99.0–99.9) | 25 |
| top 10% (90.0–99.0) | 25 |
| upper half (50.0–90.0) | 25 |
| **lower half (0–50.0)** | **50** |

The lower half carries double weight because that is where the question lives. **Bands are
never pooled** — `AS-H1` records two reads that failed to fire because they assumed the bands
would agree; they do not.

Sampling is uniform within band under a **fixed seed (`RC_SEED = 20260729`)**, written into
the harness before it runs, so the seed list is reproducible and cannot be reselected after
seeing a result.

## §3 The instrument

For a seed artist `u`, the built graph gives `u` an edge to `v` only if each ranks the other
in its top-50 (mutual k-NN). So:

    degree(u) = #{ v in top50(u) : u in top50(v) }

**Estimator.** Fetch `u`'s candidate list (1 request). Take `top50(u)`. Sample `m = 10` of
those candidates uniformly (all of them if `|top50(u)| <= 10`, in which case there is no
sampling error), fetch each, and record whether `u` appears in that candidate's own top-50.
Then:

- **count:** `n_cand(u) = |top50(u)|`
- **rate:** `recip(u)` = reciprocating share of the sampled candidates
- **degree:** `d_hat(u) = n_cand(u) * recip(u)`

All three are reported per band, per arm. Reporting the rate beside the count is `AS-H2`'s
instruction discharged.

**Cost.** ~1,650 requests for `RC-ARM-B` at ~1.05 s each (measured: 0.141 s mean fetch during
the production crawl, ~0.85 s on the same endpoint today, plus the fixed 0.2 s delay) ≈ 30
minutes. `RC-ARM-P` is served from the existing 75,000-response archive wherever possible and
fetches only misses.

**`RC-ARM-B` writes to its own archive directory.** The archive key is
`similar/listenbrainz/{mbid}.json` and **does not encode the algorithm**, so an `ALG-B` crawl
pointed at the production archive would silently return production responses and never fetch.
Recorded as a hazard for the rebuild plan.

## §4 Criteria — threshold and plain sentence, both fixed now

Each criterion carries the sentence it must be reported with. A report whose wording drifts
from these is as visible as a moved number.

- **`RC-C1` — stranding share, lower half.** Share of lower-half seeds with `d_hat < 2`
  (an artist with fewer than two connections cannot sit *between* two others).
  **Material: a rise of ≥ 10 percentage points** under `RC-ARM-B`. **No material effect:
  < 3 points.** 3–10 points is **indeterminate and must be reported as such**.
  *Plain sentence:* "how many obscure artists end up with too few connections to appear in
  the middle of a journey at all."
- **`RC-C2` — median connections, lower half.** Ratio of median `d_hat` (`RC-ARM-B` /
  `RC-ARM-P`). **Material: ≤ 0.5** (halved). **No material effect: ≥ 0.85.** Between is
  **indeterminate**.
  *Plain sentence:* "whether the typical obscure artist ends up with far fewer connections
  under the new setting."
- **`RC-C3` — the famous side must not collapse.** Median `d_hat` across the top 0.1% and
  top 1% bands under `RC-ARM-B`. **Fails if < 25**, which is the floor
  `PRODUCTION_ACCEPTANCE.famous_median_degree_floor` already enforces at build time — so a
  failure here predicts that an `ALG-B` artifact would be **refused by the build**.
  *Plain sentence:* "whether famous artists keep enough connections for the build to accept
  the result at all."
- **`RC-C4` — the count/rate split, reported always.** `n_cand` and `recip` per band, both
  arms, whatever `RC-C1`–`RC-C3` do. No threshold: this is the diagnostic that says *which*
  of the two moved, and it exists because `AS-H2` was caused by its absence.
  *Plain sentence:* "whether the new setting offers fewer candidates, or the same number but
  fewer that point back."

## §5 Gates — each with its own effect size

- **`RC-G1` — archive drift.** `RC-ARM-P` reads responses fetched on 2026-07-20; `RC-ARM-B`
  fetches today. Re-fetch **40** seed lists live under the production setting and compare
  with the archived copy. **Fires if > 10% of the 40 differ from their archived top-50 by
  more than 5 members.** On firing, `RC-ARM-P` must be re-fetched live in full (+~30 min) and
  no cross-arm read is valid until it is; the archived arm is then reported only as a
  drift measurement. **If it does not fire, the archive is used and this gate is reported as
  not-fired with its figure**, never silently omitted.
  *Plain sentence:* "checking the nine-day-old saved answers still match what the service
  says today, before comparing them against anything."
- **`RC-G2` — band sufficiency.** A band is readable only with **≥ 15 usable seeds in both
  arms**, and the lower half requires **≥ 30**. A band below its threshold is **reported as
  unread** and is never pooled into another band to reach a number.
  *Plain sentence:* "a fame group with too few usable artists gets reported as unmeasured
  rather than quietly merged into its neighbour."

## §6 The read of every possible result

**Every read below presupposes that both arms have completed for every band passing
`RC-G2`, and that `RC-G1` has been evaluated and reported.** A read taken before that state
says so and names what is still owed.

- **`RC-R1` — material stranding.** `RC-C1` ≥ 10 points **or** `RC-C2` ≤ 0.5. Then `ALG-B`
  buys the famous-pair fix at the price of obscure artists, and that price is now measured.
  Feeds the owner's re-crawl decision; **does not decide it.** `AS-H2` is discharged for the
  connection-count half.
- **`RC-R2` — the null, and it is actionable.** `RC-C1` < 3 points **and** `RC-C2` ≥ 0.85.
  Then the 58% candidate-supply drop does **not** translate into lost connections — obscure
  artists keep their links because the candidates they lose were ones that never pointed
  back. `AS-H2` is discharged for the connection-count half, and `ALG-B`'s remaining costs
  are the ones already known (`AS-R3`: it is a replacement graph, and `REQ-38`: nothing
  measures whether its edges are good).
- **`RC-R3` — indeterminate.** Either criterion lands in its middle band. Reported as
  indeterminate with both figures. What would resolve it is a **real build** of an `ALG-B`
  trial archive — which is blocked until the nameless-artist drop rule lands (§7). No
  further sampling is proposed: more seeds narrow the interval but cannot answer the
  main-component half.
- **`RC-R4` — build blocker.** `RC-C3` fails. Then `ALG-B` as configured would be **refused
  by `check_acceptance`**, and that is a fact about the rebuild plan regardless of every
  other result here. Reported even if `RC-R2` holds.

**No result here licenses "`ALG-B` is better" or "`ALG-B` is worse" overall.** This measures
one named risk.

## §7 Out of scope, and the hazards this run does not clear

- **`RC-H1` — largest-component membership is not measured.** The estimator sees the
  connection count that *precedes* falling out of the main graph, not the outcome. Only a
  real build shows it.
- **`RC-H2` — the nameless-artist drop rule blocks every build, not just production.**
  `check_acceptance`'s blank-name check refuses any rebuild by design until the decided drop
  rule is implemented (`acceptance.py:14-26`). So the rebuild plan cannot build *anything*,
  trial or production, until that lands. It is listed in `NEXT.md` as due inside the plan;
  this run establishes it also **gates the plan's own first build**.
- **`RC-H3` — the archive is not algorithm-tagged.** §3 records the mechanism. A future
  re-crawl pointed at an existing archive silently returns the old setting's data.
- **`RC-H4` — `top50(v)` is computed over `v`'s full candidate list**, whereas a real build
  restricts to artists that are graph nodes (`pipeline.py:184`). In a full 75k re-crawl
  nearly every candidate is a node, so this is closer to the real re-crawl than a capped
  crawl would be — but it is an approximation, it is identical in both arms, and it is
  named here rather than discovered later.

## §8 Amendments

Append-only. Nothing above is edited once committed; a correction is a new dated entry here.

### `RC-A1` — 2026-07-29, before any arm ran: adopt the AS sample as the seed set

**Nothing above is edited. §2 is superseded by this entry on the seed set only; every
criterion, gate and read stands as written.**

`analysis/2026-07-29-cap-selection-sim/as_raw_records.json` already holds, for **200
artists — 40 per stratum, the same five bands, drawn with the same fixed seed 20260729 from
the same verified artifact** — the full candidate list under **both** `ALG-B` and `ALG-E`
(`ALG-E` is the AS label for the production setting; its algorithm string is
`BuilderConfig.algorithm` verbatim). Those were fetched **today**.

**The seed set for this run is therefore that 200, not the 150 of §2.** Three reasons, all
of which make the design stronger rather than cheaper-and-worse:

1. **The seed side costs nothing and needs no drift control at all** — both arms' seed lists
   were fetched today, in one interleaved pass, so no seed comparison spans the archive's age.
2. **More seeds per band than §2 asked for** (40 everywhere, against 25/25/25/25/50). The
   lower half loses its double weight and gains nothing; `RC-G2`'s thresholds (≥ 15, and ≥ 30
   for the lower half) are still met with margin, so no band changes readability.
3. **Directly comparable with `AS-C1`**, which was scored on this exact sample. A rate
   measured on the same artists as the count is what `AS-H2` asked for.

**`RC-G1` is retargeted and becomes free.** Its purpose was to check the nine-day-old archive
against today's service before any cross-arm read leans on it. With this amendment the archive
is used only for **`RC-ARM-P`'s sampled-candidate lists**, so the gate compares AS's live
production seed lists (2026-07-29) against the archived responses for those same artists
(2026-07-20) — **all 200 of them, no fetches**, instead of 40 fetched ones. **Threshold is
unchanged:** it fires if more than 10% of comparable artists differ from their archived top-50
by more than 5 members, and on firing `RC-ARM-P`'s candidate lists must be re-fetched live
before any cross-arm read.

**Cost after this amendment:** `RC-ARM-B` needs its sampled candidates fetched live —
200 seeds × up to 10 sampled candidates ≈ 2,000 requests at ~1.25 s ≈ **40 minutes**, up from
the ~30 minutes §3 estimated, because the sample grew from 150 seeds to 200.
`RC-ARM-P`'s candidates come from the archive wherever present.

**`m = 10` is unchanged**, as is every threshold in §4 and §5.
