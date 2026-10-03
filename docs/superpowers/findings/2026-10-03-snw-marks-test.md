# `SNW-` — the `DSL-` listen's weak-step marks against three step measures: result and read (#271)

**Role: AUTHORITATIVE for the `SNW-` test's read, and it OWNS the test's figures**: the three measures'
concordances, p-values, chance rates and readable counts, and every descriptive figure in `SNW-D`. Every
other document cites it by section and does not restate them. It owns **none of the `DSL-` listen's
figures**: the steps shown and the marks per side belong to
[`2026-10-01-dsl-listen-results.md`](2026-10-01-dsl-listen-results.md) §3, which this run's own counts
match exactly (checked after the run, as an identity check).

**Raw data:** [`builder/analysis/2026-10-03-snw-marks-test/snw_result.json`](../../../builder/analysis/2026-10-03-snw-marks-test/snw_result.json),
committed as produced at `7369650`. The rater's fresh ratings and the rating-pass log are
`snw_rater_cache.jsonl` and `snw_rating_passes.jsonl` beside it, committed at `de97224` **before** the
scoring run read any mark.

**Governing document:**
[`specs/2026-10-03-issue-271-shared-neighbours-marks-preregistration.md`](../specs/2026-10-03-issue-271-shared-neighbours-marks-preregistration.md),
designed cold and committed at `24c6494` and `dbdb6a0` (2026-10-03, 01:22 and 01:41), before any run.
**It wins wherever this note disagrees.** The harness that ran is that commit's (`harness_commit` in the
result).

**Written by the fresh session `SNW-RS` requires.** It did not design the test. Before running, it
confirmed the pre-registration and harness equal `origin/main`, that §13's review findings are resolved in
the committed code, that every name in §4 and §9 resolves, that the harness's 31 tests pass, that the
three listen files equal their pinned blobs, that both maps equal their sidecars and §4.2's shas, and
that the rater cache equals §4.3's sha. It opened no listen answer file before the scoring run.

**This is the coherence-instrument line's second attempt** (§8.4). The first is `COH-4`,
`ct_retrodict.py`'s rule, committed 2026-07-30 and never run. The 11 blind verdicts of 2026-07-22 remain
unconsumed. **These marks are now spent**: a further rule scored on them would be the line's next
attempt and these marks' second use, and its chance rate would have to account for this one.

**The identifiers used below, each with its plain sentence (fixed in the pre-registration):**

| id | plain sentence |
|---|---|
| `SNW-M1`, map similarity | *"How similar the map says the two artists are."* |
| `SNW-M2`, shared neighbours | *"Of all the similar artists the two have between them, the share they have in common."* |
| `SNW-M3`, model rater | *"How naturally a language model says the second artist follows the first."* |
| `SNW-C` | *"Take a step he marked and an unmarked step from the same journey, both off an endpoint or both in the middle. `SNW-C` is how often the measure scores the marked one as the worse fit."* |
| `SNW-U` | *"There are enough marked steps on each side to read the measure at all."* (at least 5 per side) |
| `SNW-F1` | *"The measure scores the step he marked as the worse fit at least 65 times in 100, against an unmarked step from the same journey."* |
| `SNW-F2` | *"Random marks would look this good less than once in 60 tries."* |
| `SNW-F3` | *"It points the same way on today's side alone and on the candidate's side alone."* |
| `SNW-V` | *"The rater scored nearly all of his marked steps on both sides, so its result can be set beside the other two."* |

---

## 0. The result, and what cuts against it

| measure | outcome | the pre-registered sentence, verbatim |
|---|---|---|
| **shared neighbours** (`SNW-M2`) | **does not fire** (`SNW-R2`) | *"On his marked steps, shared neighbours did not score worse than on the unmarked steps of the same journey clearly enough to pass the bar."* |
| **map similarity** (`SNW-M1`) | **does not fire** (`SNW-R4`) | *"On his marked steps, map similarity did not score worse than on the unmarked steps of the same journey clearly enough to pass the bar."* (§8.3: the same sentences, naming the measure) |
| **model rater** (`SNW-M3`) | **fires** (`SNW-R5`) | *"the exploration's yardstick agrees with his ear on these steps"* |

`SNW-V` holds (the rater lost none of his marked steps on either side), so the rater's outcome may be set
beside the other two.

**What each outcome licenses, from §8, and nothing more:**

- **`SNW-R2`:** *the exploration's finding is not supported by his ear on this listen.* Because power near
  the bar is limited (pre-registration §6.4), this does not show shared neighbours is useless. It shows
  this falsifier did not back it, **so any edge-price pre-registration would have to rest on other
  evidence.** The descriptive figures may not be read as "nearly passed".
- **`SNW-R4`:** context only. Neither map measure passed.
- **`SNW-R5`:** it bears on **how much weight the exploration's rated screens deserve**, and on nothing
  about the map (§5.1: the rater differs from both map measures in source, so this design is barred from
  concluding why it agrees with him). Under #165 a measure that clears the bar is promoted at most to
  *"worth a real test"*, never to a criterion.

**What cuts against the result:**

1. **The rater's firing rests mostly on the candidate's side.** Its concordance on today's side alone is
   0.550, on the candidate's 0.769 (§1). `SNW-F3` asks only for direction, and today's side clears it on
   7 readable marks, most of them end steps that each have one comparison. With that few, today's
   direction is close to a coin toss decided by a step or two (the pre-registration's own §6.3 rationale).
   The firing is sound under the rule as written; its "on both sides" is thin on one of them.
2. **The rater is not frozen.** 210 of the 295 rated pairs were rated fresh on 2026-10-03 by whatever the
   `sonnet` alias named that day; 85 came from the exploration's cache (§4). A re-run of the rater could
   differ. The firing is about *the kit's rater, as run*.
3. **Repeated connections.** About one step in nine on either side sits on a connection shown more than
   once (§2), so `SNW-F2`'s shuffle is somewhat optimistic. **The deduplicated per-side figures do not
   contradict the rater's firing**: both point the same way (§2). This was the pre-registered check, and
   it holds.
4. **Against the two non-firings: shared neighbours' pooled figure sits between chance and the floor**,
   with a p-value that would clear an unadjusted 1/20 but not the family-wise 1/60. §8.2 bars reading
   that as "nearly passed", and the power table (§6.4) says a measure truly at the floor fires less than
   half the time here. "Does not fire" is **"not backed", never "refuted"**.

---

## 1. The three measures in detail — `SNW-F`

| | map similarity | shared neighbours | model rater |
|---|---|---|---|
| `SNW-C`, pooled | 0.585 | 0.613 | **0.755** |
| `SNW-C`, today's side alone | 0.650 | 0.600 | 0.550 |
| `SNW-C`, the candidate's side alone | 0.581 | 0.614 | 0.769 |
| p-value (`SNW-N`, 20,000 draws, seed 271) | 0.086 | 0.037 | 0.0001 (one of 20,000 shuffles reached it) |
| readable marks, today / candidate (`SNW-U`, ≥ 5 each) | 7 / 39 | 7 / 39 | 7 / 39 |
| `SNW-U` readable | yes | yes | yes |
| `SNW-F1` (≥ 0.65) | **no** | **no** | yes |
| `SNW-F2` (≤ 1/60) | **no** | **no** | yes |
| `SNW-F3` (each side > 0.5) | yes | yes | yes |
| **outcome** | **does not fire** | **does not fire** | **fires** |
| chance-firing rate (`SNW-CH`, same draws) | 0.0043 | 0.0047 | 0.00275 |
| null pooled `SNW-C`: median / 95th / 98.3rd percentile | 0.500 / 0.601 / 0.629 | 0.500 / 0.604 / 0.635 | 0.500 / 0.596 / 0.624 |

**The chance that any of the three fires on noise (`SNW-CH`), on these steps and these values: 0.0115**,
under the family-wise cap of 1/20.

**Readable marks are fewer than marks.** Two of today's marks and four of the candidate's had no unmarked
scorable step in the same journey and position class to be compared against (every step of that class
in that journey was marked), so they enter no comparison. The rater left two steps unscored (`U`); neither was a
marked step.

**What a person using the app would see, as inference.** When the owner said a step did not fit, the
language model, asked cold whether the second artist follows the first, also rated that step as the
weaker one about three times in four, against another step from the same journey and position. The map's
own two numbers, its similarity score and how many similar artists the two share, picked the marked step
as the weaker one only about six times in ten, which is not distinguishable from luck at the bar set in
advance. So on these journeys, **whatever the model hears in a bad step is something the map's own
numbers mostly do not show**, and shared neighbours did not close that gap enough to be backed.

---

## 2. `SNW-D` — descriptive reads, which decide nothing

Each is barred from reversing or softening an outcome in §1.

| | map similarity | shared neighbours | model rater |
|---|---|---|---|
| marks shifted one step **earlier** | 0.569 | 0.621 | 0.540 |
| marks shifted one step **later** | 0.557 | 0.443 | 0.477 |
| end steps only (both sides) | 0.929 | 0.929 | 0.893 |
| middle steps only (both sides) | 0.552 | 0.583 | 0.741 |
| within a journey, ignoring position (the first draft's statistic) | 0.646 | 0.642 | 0.781 |
| the candidate's steps that are also connections in today's map | 0.563 | 0.598 | 0.759 |
| deduplicated, today's side (one row per connection, within the side) | 0.559 | **0.480** | 0.627 |
| deduplicated, the candidate's side | 0.555 | 0.599 | 0.786 |
| head-to-head: pooled `SNW-C` minus similarity's | — | +0.028 | +0.170 |

**Repeat share** (step instances on a connection shown more than once on that side, logged by the rating
step before any mark was read): today's side **0.109**, the candidate's **0.127**.

**Counts:** 316 step instances across 48 journeys; the per-side steps and marks equal the listen note's
§3. The rater left 2 step instances unscored; none was marked on either side.

What these describe, without deciding anything:

- **Shift controls.** The rater's agreement falls to about chance when the marks move one step either way,
  so it is tracking the marked step itself, not a stretch of the journey. Shared neighbours does about as
  well with the marks moved one step *earlier* as on the real ones, and below chance with them moved
  later. That pattern is what a measure tracking a region of the journey would show; with the bar not
  cleared, it bears on nothing.
- **End steps** score high for all three measures, on few comparisons: today's side puts most of its marks
  on end steps and each has one comparison. **Middle steps** carry most of the comparisons, and there only
  the rater stays clearly above chance.
- **Ignoring position**, both map measures move up towards the floor. That is the endpoint effect the
  pre-registration grouped out (SNR-1); §8.5 bars reading this figure as the result.
- **Deduplicated, today's side**, shared neighbours points slightly the wrong way (0.480). It did not fire,
  so this contradicts no firing; it is recorded because it is the per-side check the pre-registration
  named.
- **The head-to-head** is description only. "Shared neighbours beats similarity" is barred (§3).

---

## 3. Barred reads (§8.5), each beside the result it would be drawn from

| result | the read it does NOT support |
|---|---|
| **the rater fires** | that the rater **predicts or explains the `DSL-` verdict** (`DSL-R3`), or that the verdict confirms the rater (K8, `DRP-AM7-11`). This test read step marks, not the verdict. |
| **the rater fires** | that the rater becomes a **criterion**, a threshold, or anything adopted (K4). At most it is *"worth a real test"*. |
| **the rater fires** | anything about **the map**: the rater differs from both map measures in source, so this design cannot say why it agrees with him (§5.1). |
| **the rater fires; shared neighbours does not** | that shared neighbours is therefore validated **through** the rater, because the exploration found it agreed with the rater. The direct test against his ear is this one, and it did not back shared neighbours. |
| **shared neighbours does not fire** | that shared neighbours is **refuted** or useless: power near the bar is limited (§6.4). Also not "nearly passed" from its p-value or any descriptive figure. |
| **shared neighbours +0.028 over similarity** | **"Shared neighbours beats similarity"** (§8.3): this design does not test that difference. |
| **the candidate's side carries most marks; split by connection type in §2** | any attribution to **the ceiling, the extra connections, or any cost term** (K7). |
| **any of it** | a generalisation to **random pairs, either tier alone, or the first path**: the marks cover only the listen's pairs and its depths 5, 10 and 20 (`DRP-AM7-11`, `DRP-X8`). |
| **any of it** | a re-run, a second seed, or a re-read under a changed bar (§9: run-once and final). |
| **the "ignoring position" figures** | the result, where they disagree with `SNW-C` (SNR-1). |

---

## 4. Provenance

| item | value |
|---|---|
| governing pre-registration | `dbdb6a0` (harness and document) |
| listen inputs | blobs at `273ec27`: `dsl_page_data.json` `f923b0bf…`, `dsl_verdicts.json` `e5b474af…`, `dsl_result.json` `019140ec…`; read only as `weak` marks and the side mapping |
| today's map | `C:/dev/music-app/builder/scratch/graph-lba-a6.bin`, sha256 `28311d81…`, equal to its sidecar |
| the candidate's map | `C:/unsung-fast/drp-stage3a/graph-drp-s1.bin`, sha256 `418fe666…`, equal to its sidecar |
| rater cache (pinned) | `exploration/kit/step_cache.jsonl`, LF-sha256 `af527bb9…` |
| rater | `claude` 2.1.288, alias `sonnet`, 2026-10-03 |
| rating step | one pass; nothing left unanswered, so the stopping rule ended it; 295 distinct pairs: **85 from the pinned cache, 210 rated fresh**, 0 unanswered (`snw_rating_passes.jsonl`) |
| scoring run | once, 2026-10-03; never called the model; no refusal |

**⚑ The result file's `rater_provenance` reads `from_pinned_cache: 295, rated_fresh: 0`.** That is a
label, not a fault: the scoring run loads the exploration's cache and this test's own committed cache as
one dictionary and counts both as "cache". The split above, from the pass log written by the rating step,
is the true one. No figure in the read depends on it, and the harness was not changed after the run.

---

## 5. What follows, and whose it is

**The owner's decision (#271 *Done when*): whether a pre-registration for shared neighbours as an edge
price follows.** It is his because what the app should do, and whether to spend a pre-registration on it,
are his. Under `SNW-R2`, any such pre-registration would have to rest on evidence other than these marks.

**Recommended to him, not run (K10):** an `ml-graph-analyst` critique of shared neighbours as a measure,
before any edge-price pre-registration, whatever this outcome.

**Not decided here:** what, if anything, follows from the rater's firing. §8.3 limits it to the weight the
exploration's rated screens deserve; any use of it beyond that is a new question for him.
