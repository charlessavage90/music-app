# `SNW-` pre-registration — the `DSL-` listen's weak-step marks against three step measures (#271)

**Role: GOVERNING for issue #271's test, and nothing else.** Identifiers **`SNW-`**, collision-checked
across every ref on 2026-10-03 (no hit in any `*.md` or `*.py`). **Owns no figures** except this
design's own pre-run estimate (§6.4, whose raw output is
`builder/analysis/2026-10-03-snw-marks-test/snw_chance_estimate.json`). The listen's figures stay with
`findings/2026-10-01-dsl-listen-results.md` and are cited by section, never restated.

**Designed cold.** The designing session did not open `dsl_verdicts.json`, `dsl_result.json` or
`dsl_page_data.json` at any point. It learned the per-step record's shape from the code that writes it
(`dsl_page.py`, `_marks` and `apply_post`; `dsl_unblind.py`, `step_read`). It pinned those three
files by their **git blob ids** at commit `273ec27`, which `git` computes without anyone reading the
content.

**What the design did know about the marks (SNR-2).** Findings §3 is the one place the designing session
read about them. It gives, per side, the steps shown, the end steps, the marks and **the marks on end
steps**, and the marks and end-step marks **per depth**. So the design knew how the marks split between
end steps and middle steps, and fixed every bar knowing that. It did not know which journeys, which
steps, or which artists carry marks. **Every measure, bar and read below was fixed before anyone looked
at which steps carry marks.** The git timestamps of this file's commits are the evidence.

**Amended in place before any run** after `experiment-reviewer`'s check (findings `SNR-1`–`SNR-12`,
dispositioned in §13). Its largest change is `SNW-C`'s grouping by position (SNR-1). No result
existed when any of this was written.

**Run state: nothing has run against the real marks.** The harness is
`builder/analysis/2026-10-03-snw-marks-test/snw_test.py`, with tests in `test_snw.py`. Those tests use
synthetic data and the 500-node fixture only. **A different session runs it, once** (§9).

**Whose:** the owner's. He reopened the coherence-instrument line on 2026-10-03, in his words *"I'm
reopening the instrument line"*, recorded on
[#165](https://github.com/charlessavage90/music-app/issues/165#issuecomment-5965828605). That is
#165's condition and the one #271 waited on. Whether a pre-registration for shared neighbours as an
edge price follows the read is also his (#271, *Done when*).

---

## 1. The question, in plain words

During the `DSL-` listen, the owner could mark any step of a journey as *"this step doesn't fit"*
(`DSL-W`). Each mark sits on one step: the link between two neighbouring cards. **This test asks
whether any of three cheap step measures gives the steps he marked a worse score than the unmarked
steps of the same journey.** The three measures are the map's own similarity score, how many similar
artists the two artists share, and a language model's rating.

The Dig deeper exploration (#264) found that **shared neighbours** judged steps better than the
similarity score. But it measured that against the model rater, on the pairs it tuned on
(`exploration/r2-nsim/NOTES.md`, "The finding that drove everything"), so it is not evidence (#271).
His marks are his ear, collected independently and never seen by the exploration. That makes them a
**falsifier**: they can show a measure does *not* agree with him. Passing promotes a measure only to
*"worth a real test"*, never to a criterion (#165; `ct_retrodict.py`'s docstring, *"THE CORPUS IS A
FALSIFIER, NEVER A TRAINING SET"*).

## 2. The constraints this design must satisfy, each with its source

| # | constraint | source | where it is met |
|---|---|---|---|
| K1 | Designed cold: a pre-registration fixed before the labels are read | #165 *Done when*; #271 first bullet | header; §9 run order |
| K2 | `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt, so this is **reported as a later attempt** | #165 *Done when*; #271 first bullet | §8.4 |
| K3 | **`SYN-7` binds** any use of the 2026-07-22 verdicts | #165 registry row; #271 first bullet; `findings/2026-07-26-low-degree-synthesis.md` `SYN-7` | §3.2 |
| K4 | The label set is a falsifier, not a training set; **beating the bar promotes the measure to "worth a real test", never to a criterion** | #165; #271; `ct_retrodict.py` docstring | §5 (no measure has a free parameter); §8 |
| K5 | **The listen's verdict is not re-tallied** | `DRP-AM7-11` (`specs/2026-09-27-issue-200-depth-remedy-preregistration.md` §14); #271 second bullet | §4.1: the harness reads only `weak` from the answer file, and a test proves it |
| K6 | **Steps pooled across both sides, with a within-side check that must agree**, because most marks fall on one side and a measure that merely separated the sides would look predictive | #271 second bullet (the concern is #271's own; `DRP-AM7-11` supplies the bars around it, not this one) | §6.1 (comparisons only within one journey and position class) and §6.3 `SNW-F3` |
| K7 | **No attribution to the ceiling, the extra connections or any cost term** | `DRP-AM7-11` "Barred, whatever the verdict"; #271 second bullet | §8.5 |
| K8 | **No claim that any measure predicts or explains the verdict** | `DRP-AM7-11`; #271 second bullet | §8.5 |
| K9 | **Each step is scored on the map it was shown from**: today's map for today's side, the extra-connections map for the candidate's, via the unsealed side mapping | #271 third bullet | §4.2 |
| K10 | After the read, and before any pre-registration to adopt shared neighbours as an edge price: an **`ml-graph-analyst` critique, recommended to the owner and not run unasked**, **whatever the outcome** | #271 fourth bullet; `CLAUDE.md` "When to recommend a review" | §9 step 5 |
| K11 | The line reopens **"on a route-population gate (`COH-3`)"**: an instrument must be able to score the steps journeys actually deliver, not just a population at large | #165 *Condition*; `NEXT.md` PARKED, "the coherence thread"; `findings/2026-07-30-coherence-tag-probe.md` `COH-3` | `SNW-M1` and `SNW-M2` score every shown step by construction (a step is a connection of its map). `SNW-M3`'s coverage of the delivered steps is its unscorable count, gated by `SNW-U` and `SNW-V` (§5.2) |

## 3. Where #165 and `DRP-AM7-11` pull against each other, and how this design resolves it

Neither document was written for this test. #165 was written for the **11 blind verdicts of
2026-07-22**. `DRP-AM7-11` was written to protect the **`DSL-` listen's verdict**. #271 applies both to
a third thing: the per-step marks. In four places that needed a ruling. They are this session's, made
from the documents' own wording.

### 3.1 "Re-tallied on … marks" (`DRP-AM7-11`) against scoring measures on the marks (#165, #271)

`DRP-AM7-11` says the verdict *"may not be … re-tallied on strength, identification, marks or
familiarity"*. Read loosely, that bars this test. Read as written, the object is the **verdict**: the
listen's own result, which is a count of row-level picks. **This test never reads a pick**, never
forms a row-level tally, and states nothing about which side was better. It reads the marks as labels
on steps and asks whether three measures agree with them. **Resolution:** the test proceeds, and the
bar is enforced mechanically. `weak_marks_only` is the only projection of the answer file the harness
makes. `test_answer_projection_reads_weak_marks_only` proves the output is unchanged under any value
of every other field.

### 3.2 `SYN-7` binds "any use of the 2026-07-22 verdicts", and this test makes none

`SYN-7` says the owner's 2026-07-22 verdicts predate five of the nine `WHAT-GOOD-LOOKS-LIKE` values,
so agreement with them is agreement with his preferences *as of then*. **This test uses none of those
11 verdicts. They stay unconsumed**, still available to #165 as its corpus. `SYN-7`'s *substance*
applies to any labels: it asks whether the labels predate the calibration record. Checked from git
dates: the marks were committed 2026-10-01 (`f6f074b`). `WHAT-GOOD-LOOKS-LIKE.md` last changed
2026-09-11 and `PRODUCT-REQUIREMENTS.md` 2026-09-27. **So the marks postdate every calibration value
now in the record, and `SYN-7`'s caveat does not bite here.** It is stated rather than dropped, because
#165 says it binds.

### 3.3 "Run once" (`ct_retrodict.py`, #165) against three measures in one attempt

#165's precedent scores **one** rule once, and any second rule is a new, separately reported attempt.
#271 asks for three measures at once. Three rules each judged at the usual chance rate would roughly
triple the chance of a false pass. **Resolution:** the three measures form **one attempt (the line's
second)** with a **family-wise** bar. Each measure must clear a chance threshold of 1/60, so the chance
that *any* of them fires on noise is at most 1/20 (§6.3 `SNW-F2`). The rate is computed, not assumed
(§6.4).

### 3.4 "Pooled, with a within-side check" (`DRP-AM7-11` via #271) against the statistic's own guard

#271's concern is that most marks fall on the candidate's side (findings §3), so a measure that is
merely lower on the candidate's side would look predictive. The statistic here compares a marked step
only with **unmarked steps of the same journey, in the same position class** (§6.1), which removes side
differences by construction. `test_a_measure_that_only_separates_journeys_cannot_score` proves it.
**The within-side check is kept anyway, because #271 requires it**, as `SNW-F3`. It costs power (§6.4),
and that cost is the price of meeting the requirement as written.

**The same concern has a second form, and the review found it (SNR-1).** Findings §3 shows today's side
puts most of its marks on end steps, the steps off an endpoint, while the candidate's mostly fall in
the middle. A measure that is merely lower on steps off an endpoint would then pass today's half of
the side check for a reason that has nothing to do with fit. Shared neighbours is a plausible case: the
endpoints are famous, often heavily connected artists, and the overlap between a heavily connected
artist and a lightly connected one is capped near the ratio of their degrees. **Resolution:** a marked
end step is compared only with unmarked end steps of its journey, and a marked middle step only with
unmarked middle steps (§6.1). `test_a_measure_that_only_tracks_position_cannot_score` proves a
position-only measure scores 0.5. The cost is power, chiefly on today's side, where an end-step mark
has at most one comparison (the journey's other end step).

## 4. Inputs (`SNW-IN`)

### 4.1 The listen's files: pinned by blob, and read only in part

| file | pinned blob at `273ec27` | what is read | what is never read |
|---|---|---|---|
| `builder/analysis/2026-09-30-drp-stage5-listen/dsl_page_data.json` | `f923b0bf734a8c768272a9316d464cc0af5d559f` | each row's two journeys: `pairs[].rows[].{L,R}.artists[].mbid` | — (it holds no answers) |
| `…/dsl_verdicts.json` | `e5b474afeb42fa4c3c7cade64c92c320a440ca00` | **only** `rows[pair][depth]["weak"][L/R]`: step indices, where step *i* joins card *i* and card *i*+1 (`dsl_page._marks`) | picks, strengths, identification, recognition marks, ticks, the clip box, notes |
| `…/dsl_result.json` | `019140ec792753a000955597f89a239eb055a156` | **only** `mapping_unsealed` (which token was which side) and `maps[role].sha256` | the verdict, `DSL-P`, `DSL-E`, every descriptive read |

The harness checks each file with `git hash-object`, which applies the repo's line-ending conversion
and so matches the committed blob. It refuses on any mismatch.

**The sealed per-journey record (`.superpowers/dsl/dsl_sealed.json`) is not needed and not read.** It
lived in the runner's worktree, which no longer exists. The page data holds every journey's artists,
and the result holds the side mapping. Together they are all this test needs.

### 4.2 The two maps, by absolute path and sha256 (#271)

| side | map | absolute path | sha256 |
|---|---|---|---|
| today's app (`incumbent`) | `graph-lba-a6.bin` | `C:/dev/music-app/builder/scratch/graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` |
| the candidate (`challenger`, `DRP-S1P3`) | `graph-drp-s1.bin` (the extra-connections map) | `C:/unsung-fast/drp-stage3a/graph-drp-s1.bin` | `418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f` |

Both were re-hashed by this session on 2026-10-02 and match. The harness re-hashes them, and also
checks them against the sha the listen itself recorded (`dsl_result.json` `maps`), refusing on any
difference. **Each step is scored on its own side's map.** A step the map does not contain stops the
run as an identity fault (`edge_similarity`).

### 4.3 The rater's cache

`exploration/kit/step_cache.jsonl`, LF-sha256
`af527bb9b858b01b88ed8b42762bf8efcc07070fd700c78ebc32f2735daad54a`. It is read as data. Later lines win,
as in `rate.py`'s `load_cache`. Ratings it lacks are written to this test's own
`snw_rater_cache.jsonl`, never to the exploration's.

## 5. The three measures (`SNW-M`) — no free parameters, so nothing is fitted to the marks

| id | measure | definition, restated from source | plain sentence | lower means |
|---|---|---|---|---|
| **`SNW-M1`** | **map similarity** | The stored score on the step's connection, `store.scores` for u→v, in the map that step was shown from. The map is symmetrised, keeping the stronger score (`CLAUDE.md`, "Graph shape"). | *"How similar the map says the two artists are."* | less similar |
| **`SNW-M2`** | **shared neighbours** | inter = the number of artists connected to both u and v. jac = inter / max(1, deg u + deg v − inter), in the map that step was shown from. Restated from `exploration/r2-nsim/r2nsim_core.py` `_shared` (`inter`, `jac`). Because u and v are connected, each counts in the other's degree, so each sits in the denominator and never in `inter`. | *"Of all the similar artists the two have between them, the share they have in common."* | fewer in common |
| **`SNW-M3`** | **model rater** | `exploration/kit/rate.py`: the 0–3 rating of the unordered name pair (key `"A \|\| B"`, names sorted), from the pinned cache, else from the `claude` CLI with `rate.py`'s system prompt, prompt head and metadata line restated verbatim. Model alias `sonnet`, batches of 40, two attempts. **`U` and no answer are unscorable, never 0.** | *"How naturally a language model says the second artist follows the first."* | a worse fit |

**Not imported, and checked equal.** The experiment imports nothing from `exploration/`. Two tests
check the restatements: `test_shared_neighbours_matches_the_exploration_source` compares `SNW-M2` with
`_shared`'s `jac` on every connection of the 500-node fixture, and `test_rater_prompt_is_rate_py_verbatim`
compares `SNW-M3`'s prompt with `rate.py`'s text.

**No parameter is tuned.** The exploration's thresholds (`J0` = 0.15, the 2 % and 5 % cut-offs) are not
used. Each measure enters as a raw value and only its ranking within a journey matters (§6.1).

### 5.1 Factor table — what differs between the measures, and the isolating baseline

| measure | reads | source of the value | scored on | free parameters | isolating baseline |
|---|---|---|---|---|---|
| `SNW-M1` | the connection's own score | the map | the shown map | none | — (the reference) |
| `SNW-M2` | the two artists' neighbour lists | the map | the shown map | none | **`SNW-M1`**: same map, same step; differs in **one** column (which property of the map is read) |
| `SNW-M3` | the two artists' names and metadata | an external model | name pair; names and metadata from **today's map**, the one source the listen page itself used (`dsl_generate.artist_source`), falling back to the shown map only for an artist today's map lacks. (`DSL-` gate G6 checked names, disambiguations and Deezer ids only, not the type, area and start year the rater's line also carries: SNR-10.) | none (fixed prompt) | **none.** It differs from both in source. So this design is **barred from concluding why** the rater agrees or disagrees with him. Its read is about the exploration's *yardstick*, not about the map (§8.3). |

### 5.2 Held constant, and why each is constant under the comparison

- **The step instances and their marks.** All three measures score the same list of (journey, step)
  instances, from one parse of the files.
- **The map a step is scored on.** It is fixed by the side mapping, the same for `SNW-M1` and
  `SNW-M2`.
- **The null draws.** One set of 20,000 shuffles (§6.2) is applied to all three measures, so their
  chance rates are computed jointly.
- **The statistic and every threshold**, identical across measures.
- **Where the step sits.** A step off an endpoint is compared only with steps off an endpoint, and a
  middle step only with middle steps (§6.1). Position is therefore held constant within every
  comparison. It was not in the first draft (SNR-1).
- **⚑ One term is NOT constant: the scorable set.** `SNW-M1` and `SNW-M2` score every step. `SNW-M3`
  drops steps the model answered `U` or not at all. The term is inert for two measures and active for
  the third, and it may not be neutral. A model is likelier to say `U` for obscure artists, and the
  candidate was built to route through less famous ones (`DRP-S1P3`'s ceiling). **Handling:** the rater's statistic is computed on its
  scorable steps only. The harness reports how many steps it could not score
  (`descriptive_only.counts.rater_unscorable`, `inputs.rater_provenance`). If unscorable steps cost a
  side too many marks, the rater is unreadable (`SNW-U`).
- **`SNW-V`, the rater's comparability flag.** *"The rater scored nearly all of his marked steps on both
  sides, so its result can be set beside the other two."* It holds when, on each side, the rater lost
  **at most max(1, 10 %)** of that side's marked steps. With today's side's few marks (findings §3), 10 %
  alone would mean "none lost", so one lost mark is always allowed. The threshold is a judgement, fixed
  here: past it, the rater's agreement is measured on a visibly different set of steps from the map
  measures. When `SNW-V` fails, the rater's outcome is still reported but is not compared with the
  other two (§8.3). The harness writes it as `descriptive_only.SNW-V_rater_comparable_with_map_measures`.

## 6. The statistic, its null, and the bar

### 6.1 `SNW-C` — concordance within a journey and a position class

Each journey's steps fall into two **position classes**: its two **end steps** (each touches an
endpoint; findings §3's definition) and its **middle steps**. For one measure, take every pair of steps
**in the same journey and the same class** where one is marked and the other is not, both scorable.
Score 1 if the marked step has the **lower** value, ½ if they tie, 0 otherwise. **`SNW-C` is the total
score divided by the number of such pairs**, pooled over all journeys of both sides. It is a stratified
AUC: 0.5 is no agreement, 1.0 is perfect agreement.

*Plain sentence:* **"Take a step he marked and an unmarked step from the same journey, both off an
endpoint or both in the middle. `SNW-C` is how often the measure scores the marked one as the worse
fit."**

**Why within a journey and a class.** Every comparison holds the pair, the depth, the side, the map and
whether the step touches an endpoint fixed. A measure that differs only between journeys, sides, maps
or positions cannot raise `SNW-C` above 0.5. That is the guard K6 asks for, extended to position
(§3.4). The journey-only figure is reported under `SNW-D` and decides nothing.

**The unit is the step as shown.** A connection shown in two journeys counts once in each, because he
answered each row separately. The repeat is a known dependence (SNR-3). The shuffle in §6.2 treats each
journey as independent, so if he marked a repeated connection consistently the p-value is somewhat too
small. Two things bound that: `SNW-F1`'s floor does not depend on the shuffle, and `SNW-D` reports the
share of step instances that sit on a repeated connection and a deduplicated figure per side (§7, §11).

### 6.2 `SNW-N` — the null, by shuffling marks within each journey and class

One draw keeps each journey's own number of end-step marks and middle-step marks, and places each set
uniformly at random among that journey's end steps or middle steps, independently across journeys. There are **20,000 draws, with seed 271**. The
p-value is (1 + the number of draws whose pooled `SNW-C` is at least the observed one) / (1 + 20,000).

*Plain sentence:* **"If the marks had landed on random steps of the same journeys, in the same positions,
how often would a measure look this good by luck."**

### 6.3 `SNW-F` — a measure fires only if all three hold, and its side data is readable

| id | condition | threshold | plain sentence |
|---|---|---|---|
| **`SNW-U`** | readable: on **each** side, at least **5** marked steps that the measure can score, each with at least one unmarked scorable step of the same journey and class to compare against | ≥ 5 per side | *"There are enough marked steps on each side to read the measure at all."* |
| **`SNW-F1`** | effect size: pooled `SNW-C` | **≥ 0.65** | *"The measure scores the step he marked as the worse fit at least 65 times in 100, against an unmarked step from the same journey."* |
| **`SNW-F2`** | not luck: the `SNW-N` p-value | **≤ 1/60** (the family-wise 1/20 split over three measures) | *"Random marks would look this good less than once in 60 tries."* |
| **`SNW-F3`** | the within-side check (K6): `SNW-C` on today's side alone **and** on the candidate's side alone | **each > 0.5** | *"It points the same way on today's side alone and on the candidate's side alone."* |

**Outcomes per measure:** **fires** (`SNW-U` and `F1`–`F3` all hold); **does not fire** (`SNW-U`
holds, any of `F1`–`F3` fails); **unreadable** (`SNW-U` fails on either side).

**Why 0.65 (the effect size, which `SNW-F2` alone would not supply).** At 0.65, a marked step loses to
an unmarked neighbour about two times in three. Below that, a measure would put too many of his bad
steps in the middle of the pack to be worth pricing on. Also, with this many marks, a smaller
agreement can clear `SNW-F2` on luck-free data, and a firing that small could not be told from a
measure that barely helps. 0.65 is a judgement, fixed here before the data. It is not derived from
anything measured. The exploration's own figures are about the rater, not his ear, and were not
consulted to set it.

**Why 5 for `SNW-U`.** Below five marks, one mark moves a side's figure by a fifth or more of its range,
and `SNW-F3`'s direction becomes close to a coin toss decided by one step. Five is a judgement, fixed
here. Findings §3's totals put today's side near it, so `SNW-U` can bind there. If it does, the outcome is
"unreadable", never "does not fire".

**Why `SNW-F3` asks only for direction.** Today's side carries few marks (findings §3). A strength
condition there would leave most measures unreadable on any data. Direction is the least the
requirement can mean and still bite: a measure that reverses on either side cannot fire.

### 6.4 `SNW-CH` — the chance-firing rate, computed

**At run time (`SNW-CH`)**, the harness applies `F1`, `F2` and `F3` to every one of the 20,000 null
draws, on the real layout and the real measure values. It reports each measure's chance-firing rate and
the rate that *any* measure fires. `SNW-U` is decided once, on the observed marks: a shuffle keeps each
journey's and class's mark count, so it can change readability only through which steps the rater
scored. A measure that is unreadable reports a chance rate of 0, since it cannot fire (SNR-9). Each
draw's p-value is ranked against a null that includes the draw itself, which is slightly conservative.
Because `SNW-F2` alone caps each measure at 1/60, the any-measure rate cannot exceed 1/20 beyond
Monte-Carlo error. `test_F2_alone_bounds_the_chance_rate` checks that with the floor switched off.
`test_F1_alone_can_block_firing` and `test_F2_alone_can_block_firing` show each condition can stop a
firing on its own (SNR-4).

**Before the run (`SNW-CH0`)**, `snw_chance_estimate.py` computed the same rates on a synthetic layout
built from findings §3's figures only. It uses 24 journeys a side with steps spread evenly, each side's
end-step marks spread at random over its end steps and its middle-step marks over its middle steps, and
synthetic measure values: continuous, and a four-level version standing in for
the rater's ties. The three measures are drawn independent, so the any-measure rate is an upper
estimate. It also gives **power**, the chance of firing when a measure genuinely agrees with him at a
given true concordance. 400 synthetic datasets per setting, 2,000 draws each:

| true concordance | values | similarity fires | shared neighbours fires | rater fires | any of the three fires |
|---|---|---|---|---|---|
| **0.50 (no signal: the chance-firing rate)** | continuous | 0.007 | 0.005 | 0.000 | 0.013 |
| 0.65 | continuous | 0.450 | 0.448 | 0.375 | 0.812 |
| 0.70 | continuous | 0.743 | 0.728 | 0.677 | 0.980 |
| 0.75 | continuous | 0.907 | 0.920 | 0.932 | 1.000 |
| 0.80 | continuous | 0.968 | 0.973 | 0.960 | 1.000 |
| **0.50 (no signal: the chance-firing rate)** | four-level (ties) | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.65 | four-level (ties) | 0.390 | 0.343 | 0.290 | 0.720 |
| 0.70 | four-level (ties) | 0.632 | 0.667 | 0.627 | 0.948 |
| 0.75 | four-level (ties) | 0.863 | 0.882 | 0.892 | 0.995 |
| 0.80 | four-level (ties) | 0.973 | 0.948 | 0.958 | 1.000 |

With 400 datasets a setting, a rate of 0.0025 is one firing in 400. The no-signal rows sit under the 1/60 (≈ 0.017) design cap per measure and the 1/20 cap for any of the three, because `SNW-F1` and `SNW-F3` bind on top of `SNW-F2`. For the four-level rows, "true concordance" names the shift that gives that concordance before rounding into four levels. Ties pull the realised figure toward 0.5, which is why those rows fire less. The table was recomputed after `SNW-C` was grouped by position (SNR-1); grouping costs some power, chiefly through today's side.

**What this means for a reader.** A measure that truly agreed with him about two times in three (0.65) would fire well under half the time here. Mostly that is because the bar sits *at* 0.65 and the luck in his marks spreads around it. **So "does not fire" is weak evidence against a measure near the bar, and the read in §8.2 says so.** A measure that truly agreed seven times in ten fires roughly two times in three. One that agreed three times in four fires most of the time.

## 7. `SNW-D` — descriptive reads, which decide nothing

Reported beside the result, with no threshold. Each is barred from reversing or softening an outcome
in §6.3.

- **Shift controls:** `SNW-C` with every mark moved one step earlier, and one step later. His note says
  the toggle's wording was *"a little confusing"*, so some marks may sit one step off what he meant
  (findings §3, "On what a mark means"). If a measure does as well on shifted marks as on the real
  ones, it is tracking a region of the journey, not the step.
- **End steps and middle steps** separately (an end step touches an endpoint; findings §3's
  definition).
- **Within a journey, ignoring position:** the first draft's statistic. If it differs much from
  `SNW-C`, position was doing work (SNR-1).
- **The candidate's steps that are also connections in today's map**, scored as above. This is a
  description of the measure on ordinary connections. **It is barred from attributing his marks, or
  the verdict, to the extra connections** (K7).
- **Deduplicated, per side:** one row per connection on that side, marked if marked anywhere, compared
  within the side only, so the side confound K6 removes cannot return (SNR-3).
- **Repeat share, per side:** the share of step instances that sit on a connection shown more than once
  on that side. The rating step (§9, step 1) also logs it, before any mark is read.
- **Head-to-head:** `SNW-M2`'s and `SNW-M3`'s pooled `SNW-C` minus `SNW-M1`'s.
- **Counts:** step instances and marks by side, and the rater's provenance (from the pinned cache,
  rated fresh, unanswered).

## 8. Reads, fixed now, for every outcome

Each outcome sentence is quoted in the findings note exactly as written here. **Every read below
presupposes the full run state of §9: all three measures scored on all 48 journeys.** None exists
before that.

### 8.1 `SNW-R1` — shared neighbours fires

*"On steps he marked as not fitting, the two artists shared fewer similar artists than on the unmarked
steps of the same journey, clearly enough to pass the bar, and on both sides."*

**Licenses:** shared neighbours is promoted to **"worth a real test"** (#165, K4). That is all. Next is
the owner's decision whether a pre-registration for shared neighbours as an edge price follows (#271
*Done when*). **Before any such pre-registration, an `ml-graph-analyst` critique of the measure is
recommended to him, not run** (K10). It is not a criterion, not adopted, and changes no default.

### 8.2 `SNW-R2` — shared neighbours does not fire; `SNW-R3` — unreadable

`SNW-R2`: *"On his marked steps, shared neighbours did not score worse than on the unmarked steps of the
same journey clearly enough to pass the bar."* **Licenses:** the exploration's finding is **not
supported by his ear on this listen**. Because power near the bar is limited (§6.4), this does not
show shared neighbours is useless. It shows that this falsifier did not back it, so any edge-price
pre-registration would have to rest on other evidence. The descriptive figures may not be read as
"nearly passed".

`SNW-R3`: *"Too few marked steps on one side to read shared neighbours."* **Licenses:** nothing. No
read exists.

### 8.3 `SNW-R4` — the map's similarity score; `SNW-R5` — the model rater

Read on the same three outcomes, with the same sentences, naming the measure.

- **`SNW-R4`, similarity fires:** *"the map's own similarity score already scores his marked steps as
  the worse fit."* It is context for `SNW-R1`. The exploration's claim was that shared neighbours does
  *better* than similarity. **This design does not test that difference**, which the head-to-head in
  §7 only describes. So "shared neighbours beats similarity" is **barred** as a conclusion from the
  two outcomes. The most the read says is which measures passed.
- **`SNW-R5`, the rater:** fires — *"the exploration's yardstick agrees with his ear on these steps"*.
  Does not fire — *"the exploration's yardstick did not agree with his ear on these steps clearly
  enough"*. Either way, it bears on **how much weight the exploration's rated screens deserve**, and
  on nothing about the map (§5.1). If `SNW-V` fails, its outcome is reported but not compared with the
  other two (§5.2).

### 8.4 How the attempt is reported (K2)

This is the **coherence-instrument line's second attempt**. The first is `COH-4`, `ct_retrodict.py`'s
rule, committed 2026-07-30 and never run, because the coverage kill gate fired
(`findings/2026-07-30-coherence-tag-probe.md`). This attempt scores three measures under one
family-wise bar. **The count is per line, not per corpus** (SNR-12). The 11 blind verdicts of 2026-07-22
remain unconsumed: a rule scored on them would be that corpus's first use and the line's next attempt.
**A further rule scored on these same marks would be the line's next attempt and these marks' second
use**, reported as both, and its chance rate would have to account for this one.

### 8.5 Barred, whatever the outcome

- Any statement that a measure **predicts or explains the `DSL-` verdict** (`DSL-R3`), or that the
  verdict confirms or refutes any measure (K8; `DRP-AM7-11`). This test reads step marks, not the
  verdict.
- **Attribution to the ceiling, the extra connections, or any cost term** (K7), including from
  `SNW-D`'s split by connection type.
- A **criterion**, threshold or adoption claim for any measure (K4).
- **"Shared neighbours beats similarity"** from the two outcomes (§8.3).
- Generalising to **random pairs, either tier alone, or the first path**: the marks cover only the
  listen's pairs and its depths 5, 10 and 20 (`DRP-AM7-11`, `DRP-X8`).
- Re-running, or re-reading under a changed bar, after the result (§9).
- Reading `SNW-D`'s journey-only figure, or any descriptive figure, as the result when it disagrees
  with `SNW-C` (SNR-1).

## 9. `SNW-RS` — run state: who runs it, in what order, and once

**The designing session does not run it.** A fresh session does, after this document and the harness
are committed and `experiment-reviewer`'s findings on them are resolved in place. All commands run from
`api/` with `PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u`.

1. **Rate:** `snw_test.py --rate-only`. It reads the page data, the side mapping and the two maps,
   **and no answer file**; `test_rate_only_reads_no_answer_file` proves it. It asks the model for every
   shown step the pinned cache lacks, and logs each pass to `snw_rating_passes.jsonl`. **Stopping rule
   (SNR-8):** repeat it until a pass leaves nothing unanswered, or a pass adds no new answer, or three
   passes have run, whichever comes first. The harness refuses a further pass after that, and refuses to
   score before it. Nothing it does can be shaped by the marks.
2. **Commit** `snw_rater_cache.jsonl` and `snw_rating_passes.jsonl`. The scoring run refuses either one
   uncommitted or modified.
3. **Score, once:** `snw_test.py`. It refuses if `snw_result.json` exists, if this document or the
   harness differs from its commit, or if any input fails its pin. It never calls the model, so a step
   the rater did not answer in step 1 stays unscorable. It writes `snw_result.json`. **Commit it as
   produced.**
4. **Write the findings note** (`findings/2026-10-??-snw-marks-test.md`). Quote §8's sentences for each
   outcome, put `SNW-D` under "decides nothing", carry §8.5's barred reads beside the results they
   would be drawn from, and name what cuts against the result.
5. **Hand the owner his decision** (#271 *Done when*): whether a pre-registration for shared neighbours
   as an edge price follows. **Whatever the outcome**, the same message recommends the
   `ml-graph-analyst` critique of shared neighbours, to come before any such pre-registration, and does
   not run it (K10; SNR-5).

**All three measures are scored in the same run, whatever happens to any one of them.** If the rater
is unreadable, the shared-neighbours and similarity reads still stand. No measure's outcome is held
back to wait for another's.

**Run-once and final.** An unwelcome result stands. No re-run, no second seed, no changed bar, no
dropped journey. A harness fault found after the run (a crash or a refusal, not an unwelcome number)
is fixed by a dated amendment here **before** any re-run, and that re-run is reported beside the
fault.

## 10. Cost

- **The owner's time and ear:** none. No listen, no new labels.
- **The labels:** his `DSL-W` marks are spent as this line's second-attempt falsifier (§8.4).
- **Model calls:** at most one rating per distinct step the pinned cache lacks, in batches of 40 with up
  to two attempts each. The step count is bounded by findings §3's "steps shown" totals, less whatever
  the cache already holds. So it is at most a few dozen `claude -p` calls of the `sonnet` alias, and
  probably fewer.
- **Compute:** two map loads (about 40 MB each) and 20,000 vectorised shuffles. Seconds, plus however
  long the rating calls take.
- **Sessions:** one fresh session for steps 1–4, then the owner.

## 11. Weakest links

1. **What a mark means.** Most marks are assumed to sit on the step he meant. His own note says the
   toggle confused him (findings §3), so some may be one step off. That would weaken every measure
   equally and bias toward "does not fire". `SNW-D`'s shift controls show its size and change no
   outcome. *Defend:* the design reads the marks as recorded. *Would abandon cheaply:* any reading
   that a shifted-mark figure "should have counted".
2. **Power near the bar** (§6.4). With this many marks, a measure that truly agrees about two times
   in three fires well under half the time. *Defend:* the floor. A weaker measure is not worth an
   edge price. *Would abandon:* nothing. "Does not fire" is worded as "not backed", never "refuted".
3. **The rater is not frozen.** `sonnet` is an alias. Cached ratings came from the exploration's
   runs; fresh ones come from whatever the alias names on run day. The two may differ, and the
   provenance split is reported. *Defend:* it is *the kit's rater*, as #271 names it. *Would abandon:*
   any claim about the rater beyond "the exploration's yardstick, as run".
4. **Repeated connections.** The same connection can appear at several depths, so comparisons are not
   fully independent, and the shuffle treats them as if they were (SNR-3). If he marked repeats
   consistently, `SNW-F2`'s 1/60 is optimistic by an amount that grows with the repeat share. The run
   reports that share and a deduplicated figure per side. *Defend:* `SNW-F1` does not depend on the
   shuffle, and the no-signal estimate in §6.4 sits far below its cap. *Would abandon:* a firing whose
   deduplicated figure, on either side, points the other way. That is not a firing condition, but the
   findings note must name it as cutting against the result. A connection-level shuffle and the
   analyst's sizing of the repeat share (`SNR` D2) were considered and not adopted: both need the
   journeys, and the run computes the share itself.
5. **Position is controlled coarsely.** Two classes (end or middle) remove the endpoint effect, but not
   any gradient within the middle. *Defend:* findings §3's only position figure is end against middle,
   and finer classes would leave most journeys with no comparison.

## 12. Identifiers

`SNW-IN`, `SNW-M1`–`M3`, `SNW-C`, `SNW-N`, `SNW-U`, `SNW-V`, `SNW-F1`–`F3`, `SNW-CH0`, `SNW-CH`,
`SNW-D`, `SNW-R1`–`R5`, `SNW-RS`. The constraint labels `K1`–`K11` are local to this document. The
review's findings are `SNR-1`–`SNR-12` (§13).

## 13. The review, and how each finding was resolved (2026-10-03, before any run)

`experiment-reviewer` checked the first commit (`24c6494`) against the repo and stayed cold: it read
none of the three listen files. Its verdict was *"executable with named corrections"*. Every finding was
resolved in place.

| finding | what it said | resolution |
|---|---|---|
| SNR-1 | Position is not controlled: today's marks sit mostly on end steps, so `SNW-F3` could pass on position | `SNW-C` and `SNW-N` grouped by journey **and** position class (§6.1, §6.2, §3.4); position added to §5.2; journey-only figure moved to `SNW-D`; new test |
| SNR-2 | The header understated what findings §3 disclosed | header now lists it |
| SNR-3 | Repeats make the shuffle anti-conservative, and the deduplicated figure pooled the sides | deduplicated figure now per side; repeat share reported (and logged at rating time); §6.1 and §11 item 4 state the risk |
| SNR-4 | `SNW-F1` and `SNW-F2` had no test that could fail | three tests added, each shown to fail when its condition is switched off |
| SNR-5 | K10 had been narrowed to a firing outcome | step 5 recommends the critique whatever the outcome |
| SNR-6 | #165's route-population gate was missing | K11 |
| SNR-7 | The 10 % rater flag and `SNW-U`'s 5 had no rationale | `SNW-V` named, with its sentence and rationale (max(1, 10 %)); rationale for 5 in §6.3 |
| SNR-8 | The rating step had no stopping rule | at most three passes, stopping early; logged; enforced by the harness |
| SNR-9 | §6.4 described `SNW-U` as applied per draw | wording now matches the code |
| SNR-10 | Gate G6 does not cover the rater's metadata | the rater reads today's map, the page's own source |
| SNR-11 | The rater-restatement test was partial, and refusals were untested | the test compares `SYSTEM`, `PROMPT_HEAD` and `BATCH` exactly, plus the line format, parse pattern and CLI flags; tests added for the blob refusal, the stopping rule, and a scoring run that must never call the model |
| SNR-12 | K6's citation; attempt numbering across corpora; `NEXT.md` and the issue labels lag the reopening | K6 corrected; §8.4 counts per line; #165 and #271 relabelled `deferred` → `task` with comments; `NEXT.md`'s PARKED entry is amended in this PR |

**The analyst derivations the review named** (D1: do end steps score differently from middle steps;
D2: the repeat share and its effect on the shuffle) **were not commissioned.** D1 decided between
grouping by position and only barring a read. Grouping was taken, which needs no D1. D2's share is
computed by the run itself before the read (§9 step 1). Commissioning either would be the owner's call;
neither changes a bar now.
