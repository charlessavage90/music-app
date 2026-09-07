# `LBD-` measurement derivation — four questions, measured

Derivation for the `LBD-` pre-registration (plan Task 2). **New figures below are mine and
are labelled as such**; `CXR-`, `LBS-` and `LBD-P1/P2` figures are cited to their owners and
never restated except where I independently reproduced them as a validation check (marked).

## Artifacts and inputs used, all verified by sha256 before reading

| file | sha256 (verified `sha256sum`) | matches sidecar? | N | CSR entries |
|---|---|---|---|---|
| `builder/scratch/graph-msw-tu50.bin` | `43dd82bb…2be79cc8` | yes | 58,838 | 1,315,684 |
| `builder/scratch/graph-cex-baseline-75k.bin` | `43dd82bb…2be79cc8` | yes | — | — |
| `builder/scratch/graph-cxa-adopted.bin` | `bc0431c4…8e7ece46` | yes | 88,685 | 1,618,164 |
| `builder/scratch/graph-cex-117k.bin` | `bc0431c4…8e7ece46` | yes | — | — |
| `builder/scratch/graph-lux4.bin` | `fd92a735…5740369` | yes | 58,838 | 1,315,684 |

`graph-msw-tu50.bin` and `graph-cex-baseline-75k.bin` are **byte-identical**; so are
`graph-cxa-adopted.bin` and `graph-cex-117k.bin`. Both pairs were built at different commits
on different days (manifest sidecars). Archives read: `grt-archive-algb.pre-cex-snapshot`
(75,000 payloads) and `grt-archive-algb` (117,302 payloads), both the ALG-B sub-tree.

Scripts (committed beside this file): `q1_degree_drift.py`, `q2_archive_shape.py`,
`q3_truncation_and_cap.py`, `q4_added_set_supply.py`, `q5_tie_ceiling.py`,
`q6_partition_and_stability.py`. Artifacts parsed through the shipped `GraphStore`
(`cxr_census.py` precedent) except where noted.

---

# Q1 — Is `LBD-C2` population-independent?

## Measured

**Mechanism, read off source first.** At `similarity_damping = 0.0` (the adopted default),
`damped_strength` reduces to `log1p(score)` — no population term. `pipeline.py` builds
`ranking` from those *unclipped* strengths and hands it to `trimmed_union_cap`, so
**the p99 log clip cannot affect which edges survive.** The prompt's second suspected
mechanism is provably inert for degree. It moves emitted `scores` and therefore `pop_raw`,
not degree.

The population-dependent mechanisms that remain, all in `graph.py` / `pipeline.py`:

1. `scored_adjacency` filters `if n.mbid in known` — a fixed artist's top-*j* is selected
   from a candidate set that grows with the population.
2. `trimmed_union_cap`'s union direction: more artists in the table ⇒ more artists that
   rank a fixed artist in *their* top-*j* ⇒ more in-edges.
3. The degree-ceiling trim deletes **whole edges**, ordered globally by `(-degree, mbid)`.
   Trimming a hub removes an edge from its partner too. Which nodes are over the ceiling,
   and by how much, is a function of the population.
4. `largest_component` membership.

**Magnitude, newly computed** (`q1_degree_drift.py`). Fixed MBID set = the 58,793 artists
present in both artifacts; same cap rule (`trimmed_union`, `top_j` 50, ceiling 50), same
algorithm, same rescale, same drop flags; population 58,838 → 88,685 (+50.7 %).

| fixed set, degree in | median | mean | share ≤ 2 | share = 1 |
|---|---:|---:|---:|---:|
| `graph-msw-tu50.bin` | 17 | 22.37 | 8.86 % | 4.69 % |
| `graph-cxa-adopted.bin` | 19 | 23.77 | 8.07 % | 4.27 % |

42.73 % of the fixed set changed degree at all; 37.01 % gained, 5.72 % lost, 45 left the
graph. (Paired median +0.0 / mean +1.40 and the 5.72 % reproduce `CXR-P2`'s pre-existing-set
figures exactly — an intentional validation of my read, not a new figure.)

**Stratified — the statistic `LBD-C2` actually uses, on a fixed set of sparse artists:**

| stratum (degree in the 58,838-node artifact) | n | median → | share ≤ 2 → | Δ share ≤ 2 |
|---|---:|---|---|---:|
| degree = 1 | 2,758 | 1 → 1 | 100.00 % → 96.77 % | −3.23 pp |
| degree = 2 | 2,450 | 2 → 2 | 100.00 % → 81.67 % | −18.33 pp |
| degree ≤ 2 | 5,208 | 1 → 2 | 100.00 % → 89.67 % | **−10.33 pp** |
| degree ≤ 4 | 9,762 | 2 → 3 | 53.35 % → 48.60 % | **−4.75 pp** |
| all 58,793 | 58,793 | 17 → 19 | 8.86 % → 8.07 % | −0.79 pp |

**Split-half stability** (`q6`, MBID sha1 parity): deg ≤ 2 stratum −10.78 pp / −9.90 pp;
deg ≤ 4 stratum −4.94 pp / −4.57 pp. The share-≤2 drift reproduces to ≈ 0.9 pp across halves.
The **median flips between halves** in the deg ≤ 2 stratum (half A 1 → 2, half B 1 → 1) —
i.e. the median statistic is not stable at its own resolution on the same data.

**Uncontrolled second column in this pair, named.** `graph-msw-tu50.bin` was built with the
`unlistenable_drop_algb_20260805` list; `graph-cxa-adopted.bin` with the `CEX-` re-census
list (its manifest says `unlistenable_list_path: null`, and it is byte-identical to
`graph-cex-117k.bin`, which pinned the re-census file explicitly). So this pair differs in
**two** columns: population and drop list. Bound on the second: only 45 of the fixed set left
the graph, so the drop list's direct membership effect is ≤ 0.08 % of the set; its indirect
effect on top-*j* competition is not bounded here.

## What it implies (inference)

`LBD-C2` is **not** population-independent, and the error is not small where it matters. In
plain terms: if you take the same 5,208 artists and rebuild the map with half again as many
artists in it — changing nothing about how similarity is computed, nothing about the cap, no
knob at all — the share of them that are still near-dead-ends falls by about ten points. An
arm of the `LBD-` sweep that produces a bigger population will look like it has helped the
sparse artists even if its similarity table is no better at all. Since the `LBD-` arms will
produce populations far larger than 88,685 (`LBD-P1` counted 142,683 artists in a *single
day* of listens), this is the dominant source of apparent movement, not a rounding error.

The comparison is also directional: bigger population ⇒ higher degree for a fixed set. So the
confound pushes every arm toward "success".

## Weakest link

One pair, one population ratio (+50.7 %), and that pair carries a second changed column (the
drop list). I would defend "the sign is positive and the magnitude on share-≤2 is of order
5–10 pp for a +50 % population change" — it reproduced on both halves. I would **not** defend
any extrapolation to a 5× or 50× population change; the mechanism (ceiling-trim cascade) is
not linear and could reverse at large populations, because a much bigger table also means
many more nodes over the ceiling.

Falsified by: a build of the extended archive with `drop_unlistenable=False` alongside a
build of the pre-CEX archive with the same flag, isolating population as the single column.

## Does `LBD-C2` need a control, and the cheapest one that works

**Yes.** Three options, cheapest first:

1. **Free, and I would make it primary: read `LBD-C2` at the pair-table level as well as
   the graph level.** For each MBID in the `CXR` added set, count its above-threshold pairs
   in the arm's own pair table, before any of our graph rules. That statistic has no cap, no
   ceiling, no component prune and no population-relative term in it — it is the one form of
   the question that genuinely *is* population-independent. Cost: one DuckDB `GROUP BY` over
   a parquet the arm already produces (seconds to minutes, given `LBD-P2`'s timings).
2. **Free: report the pre-existing 58,793 as a within-arm reference in every arm**, exactly
   as `CXR-P2` did. If the added set's share-≤2 falls by 12 pp and the pre-existing set's
   falls by 10 pp, the arm did nearly nothing.
3. **Not free, and I do not think it is needed:** a population-matched control build. It
   would require sub-sampling each arm's artist set down to a common size before `build`,
   which is a population rule — `LBD-S4` territory and out of scope per §10.

The control that would isolate the Q1 magnitude itself (two builds of the two existing
archives with `drop_unlistenable=False`) is a **diagnostic**, not a `LBD-C2` control. Cost
estimate from the manifest sidecars: `graph-lux4` 616 s and `graph-cxa-adopted` 1,372 s
elapsed, so ~35 minutes of wall clock plus the harness. I did not run it.

---

# Q2 — Is list-overlap the right fidelity metric for `LBD-C1`?

## Measured

All newly computed over `grt-archive-algb.pre-cex-snapshot`'s ALG-B sub-tree, 75,000
payloads, 4,164,212 neighbour rows (`q2`, `q3`, `q5`, `q6`).

**Served list lengths.** median 52, mean 55.52, max **100**, min 0. 37.68 % of crawled
artists sit exactly at 100; 0.31 % have an empty list.

**Reciprocity.** Of the 4,017,540 rows whose neighbour is also crawled, only **42.30 %** are
reciprocal (owner appears in the neighbour's list). Per-artist reciprocity: median 0.5000,
p10 0.1100, p90 0.9500. It falls monotonically with list length: mean 0.8145 at list length
1–4, 0.4071 at exactly 100.

**Why: the served list is a score-ordered truncation of the union at 100.** Of the 2,317,880
non-reciprocal rows, **99.72 %** have a partner whose list is full (≥ 100), and among those
**99.99 %** have the omitted score at or below the partner's served minimum. Scores agree in
both directions on 99.9610 % of doubly-served rows (1,698,444 equal, 662 unequal). The
residue — 6,522 rows (0.16 %) where the partner's list is *not* full and the row is still
absent, plus the 662 score disagreements — is lineage drift (the archive was fetched over
time against a dataset that moved), not construction.

**So the `LBS-3` union model is confirmed and extended:** X's served list = the union of both
lexical partitions, ordered by score, truncated at 100. That is reproducible.

**The tie boundary at the truncation is a real but tiny ceiling.** For the 28,259 artists at
100: median 3 (mean 4.45) served rows tie at the list's minimum score, and 42.95 % have at
least one *observed* omitted candidate at that same score. Expected overlap under a random
tie-break (upper bound, since omitted candidates are only visible via the other direction):

| fame band (`fame_lb` quintiles of the served map) | n | share at the 100 ceiling | median ceiling | mean ceiling | p10 ceiling |
|---|---:|---:|---:|---:|---:|
| Q1 (least-listened) | 11,767 | 8.44 % | 1.0000 | 0.9997 | 1.0000 |
| Q2 | 11,733 | 18.70 % | 1.0000 | 0.9987 | 0.9950 |
| Q3 | 11,753 | 31.93 % | 1.0000 | 0.9981 | 0.9917 |
| Q4 | 11,746 | 56.24 % | 1.0000 | 0.9967 | 0.9880 |
| Q5 (most-listened) | 11,747 | 92.18 % | 1.0000 | 0.9969 | 0.9909 |

**The definition of "our top-N" is where the real ceiling lives.** If our list for X were X's
own lexical partition only (`rank() OVER (PARTITION BY mbid0)`, which is what LB's SQL
literally emits) rather than the unioned-and-truncated list, then even a perfect
reimplementation scores: pooled 73.90 % of rows, per-artist median 0.8000, mean 0.6884,
**p10 0.1800**; for artists at the 100 ceiling, median 0.8800 / mean 0.7632.

**Resolution varies enormously by fame band**, because N does. Median served list length by
fame quintile: Q1 14, Q2 29, Q3 52, Q4 100, Q5 100. 6,575 crawled artists have lists of
length 1–4, where a per-artist overlap can only take 2–5 distinct values.

## What it implies (inference)

Overlap is the right shape, but **only under one of two possible readings of "our top-N", and
the pre-registration must say which.** Read one way — our unioned list for the artist, ranked
by score, cut at the archive list's length — a perfect reimplementation scores about 99.8 %,
and the small shortfall is a tie at the bottom of long lists plus a handful of rows where the
archive contradicts itself. Read the other way — the artist's own half of the pair table,
which is what ListenBrainz's code literally produces — a perfect reimplementation scores
about 80 % for the typical artist and as low as 18 % for one artist in ten, and the shortfall
is worst for the best-known artists. Those two readings differ by more than any plausible
lineage gap, so writing down which one is meant is worth more than any threshold in the
document.

The other thing to fix is that "overlap" for an obscure artist with three neighbours is a
number that can only be 0, ⅓, ⅔ or 1. Averaging that across a fame-banded sample mixes
statistics of wildly different precision. Report the pooled row-level figure per band
(matched rows ÷ total rows) alongside the per-artist distribution.

## Weakest link

The tie-ceiling figure is an **upper** bound: I can only see omitted candidates when the
other endpoint served the row, so artists whose omitted rivals are themselves saturated look
cleaner than they are. If a large share of boundary ties are mutually invisible, the true
ceiling is lower than 0.9955 mean. I would defend the 99.99 %-score-ordered-truncation result
and the 73.90 % own-partition share firmly (both are direct counts over 4.16 M rows); I would
abandon the exact ceiling number cheaply.

Also: the fidelity ground truth is *this* archive, and §6's lineage gap is by construction
unmeasurable from inside it. Nothing here bounds that gap.

---

# Q3 — What effect size is distinguishable from the noise of a rebuild?

## Measured

**Build noise is exactly zero.** `graph-lux4.bin` (built 2026-09-06, commit `7d2d800`,
616.1 s) against `graph-msw-tu50.bin` (built 2026-08-06, commit `3aa61f0`): `mbids` identical,
`offsets` identical, `neighbours` identical, `scores` identical — element for element. The
files differ in sha256 only because `LUX-4` added metadata keys. Independently,
`graph-msw-tu50.bin` ≡ `graph-cex-baseline-75k.bin` and `graph-cxa-adopted.bin` ≡
`graph-cex-117k.bin` byte-for-byte, across different commits and days.

**Statistical resolution of the two `LBD-C2` statistics** on the fixed 29,892-MBID set
(non-parametric bootstrap, 2,000 resamples, seed 20260906, over the added set's degrees in
`graph-cxa-adopted.bin`): median degree — every one of 2,000 resamples returned exactly 4.0
(the statistic is integer-quantised and cannot resolve below 1). Share ≤ 2 — 95 % interval
33.832 %–34.902 %, half-width **0.535 pp**.

**The genuine floor is the population confound from Q1, not noise:** ±5–10 pp on share-≤2 for
a fixed sparse set under a +50 % population change, and +1 on the median.

**Median instability at its own resolution** (Q1's split-half, restated here because it bears
on the choice of statistic): the same deg ≤ 2 stratum gives median 1 → 2 on one half and
1 → 1 on the other.

## What it implies (inference)

There is no rebuild noise to speak of. Run the same inputs through the same code and you get
the same bytes, a month and several commits apart. So a pre-registered effect size cannot be
derived from run-to-run variation — there isn't any.

What actually moves the number for reasons that have nothing to do with the knob being turned
is the size of the map. That is the floor a threshold has to clear. On the evidence available:

- **Graph-level `share with ≤ 2 connections`: a movement below about 10 percentage points
  cannot be attributed to the knob** on a single arm-vs-baseline comparison, because a
  population change alone produced that much. With the pair-table-level control from Q1 in
  place, and the pre-existing-population reference reported alongside, that floor drops to
  roughly the bootstrap resolution — call it 1 percentage point.
- **Graph-level `median degree`: not usable as a primary criterion.** It cannot resolve
  below 1, one unit is roughly what the population confound alone delivers, and it flips
  between halves of the same data. Keep it as a reported descriptive, demote it as a gate.
- **Pair-table-level candidate count** (the Q1 control): no cap, no ceiling, no population
  term. Here the paired per-artist comparison against `A0` over 29,892 fixed MBIDs is the
  sensitive instrument, and a pre-registration can responsibly set a threshold at the
  1-percentage-point level on share-≤2 and use the sign test / share-improved on the paired
  differences.

## Weakest link

The 10-point floor rests on the single artifact pair of Q1, at one population ratio, with a
second changed column (drop list). It is a measured order of magnitude, not a calibrated
constant. If the pre-registration wants a defensible number rather than an order of
magnitude, the isolating pair of builds named in Q1 (~35 min wall clock) supplies it.

---

# Q4 — Do Task 5's arms separate `LBD-R1` from the rules?

## Measured

The decisive figure first. Newly computed (`q4_added_set_supply.py`) over the **extended**
archive `grt-archive-algb` (117,302 payloads), the archive `graph-cxa-adopted.bin` was built
from. Union candidates are counted **among the artifact's own 88,685 nodes**, so every drop
list is already applied; the final-degree column reproduces `CXR-P2` and `CXR-M5` exactly,
which is what validates the read.

| the `CXR` added set, n = 29,892 | median | mean | share ≤ 2 | share = 1 |
|---|---:|---:|---:|---:|
| candidates the ALG-B archive supplies (no cap of ours) | **8** | 16.27 | **19.94 %** | **10.83 %** |
| after our `top_j` = 50 union step | 8 | 14.14 | 19.98 % | 10.85 % |
| **final degree in `graph-cxa-adopted.bin`** | **4** | 7.38 | **34.36 %** | **20.48 %** |

| the pre-existing set, n = 58,793 | median | mean | share ≤ 2 | share = 1 |
|---|---:|---:|---:|---:|
| candidates the archive supplies | 60 | 88.63 | 3.61 % | 1.81 % |
| after our `top_j` = 50 union step | 47 | 59.09 | 3.64 % | 1.82 % |
| final degree | 19 | 23.77 | 8.07 % | 4.27 % |

The degree-ceiling trim discards **47.82 %** of the added set's endpoint slots and 59.77 % of
the pre-existing set's. 4,305 of the added artists (**14.40 %**) have more than two candidate
connections and end with two or fewer. 5,972 (19.98 %) have two or fewer candidates in the
first place.

*(`largest_component` removes no edges from surviving nodes — every neighbour of a node in
the largest component is in that component — so the whole gap between the second and third
rows is the ceiling trim.)*

Same decomposition over the pre-CEX archive and `graph-msw-tu50.bin` (`q3`): union median 55
→ after `top_j` 45–50 → final 17; share ≤ 2 3.93 % → 3.96 % → **8.89 %**. 51.90 % of the
served map's nodes have more union candidates than the ceiling permits, and the maximum union
degree is 14,797.

**The factor table for the suggested arm pair.** Knobs are LB's own tokens; `A0` is the
`ALG-B`-parameter run (design §6).

| arm | `limit` | `threshold` | `contribution` | pairing | isolating baseline (differs by exactly one column) |
|---|---|---|---|---|---|
| `A0` | 100 | 10 | 3 | listen | — (the baseline) |
| cap removed | **none** | 10 | 3 | listen | `A0` ✓ |
| threshold lowered | 100 | **< 10** | 3 | listen | `A0` ✓ |
| *(missing)* both | **none** | **< 10** | 3 | listen | either single-knob arm ✓ |

**Held constant, and whether each is genuinely constant under the intervention:**

| held constant | genuinely constant? |
|---|---|
| `similarity_rescale = p99_log_clip` | **Yes, for degree** — `ranking` is built from unclipped strengths (`pipeline.py`), and at `similarity_damping = 0.0` those are `log1p(raw score)` with no population term. Provably cannot move an edge's survival. Does move emitted scores and `pop_raw`, so any routing read is exposed. |
| `union_top_j = 50` | **State moves, effect small.** Measured: the top-*j* step changes the added set's share ≤ 2 by 0.04 pp (19.94 → 19.98 %). Safe to treat as constant for `LBD-C2`. |
| `union_degree_ceiling = 50` | **NO.** It already discards 47.8 % of the added set's endpoint slots and is what turns 19.94 % ≤ 2 into 34.36 % ≤ 2. Every arm that raises supply raises the number of nodes over the ceiling, so the ceiling absorbs *more* in the successful arms than in `A0`. This is the §0 dormant-term shape exactly. |
| drop lists pinned by MBID | **NO, and it will raise.** `pipeline.py`'s `drop_unlistenable` branch computes `archive_population − ulf.censused_mbids` and raises `PopulationNotCensused` on any artist the census never evaluated. Every `LBD-` arm's population is far larger than 75 k, so **Task 7's sketch as written will refuse to build** (`BuilderConfig.drop_unlistenable` defaults `True`). `drop_no_release_tail` and `drop_featured_credit` have no such guard — they silently under-filter a larger population. |
| the `CXR` added set's presence in the corpus | **Unmeasured and not constant.** `LBD-R8` records the mapping bias at the obscure end; if 20 % of the added set never appears in the dump, `LBD-C2` reads worse for a reason that is neither LB's rules nor the listening. |
| router weights, fame source, endpoint archive | Yes (§0, unchallenged). |

## What it implies (inference)

**The two suggested arms do not separate the two explanations, for three independent
reasons.**

First and largest: the sparsity `LBD-R1` is about is, on the current map, mostly ours. For
the ~29,900 artists the crawl extension added, ListenBrainz already offers a typical eight
connections and only one artist in five has two or fewer. The map the app serves gives them
four, and one in three has two or fewer. Our own rule that no artist may hold more than fifty
connections — enforced by deleting the weakest connections of the over-full artists, which
takes the connection away from the artist at the other end too — is what makes 4,305 of those
artists dead ends. So an arm can succeed handsomely at the ListenBrainz end and still show
nothing at the graph end, and a null would be read as "the listening isn't there" when the
measurement never let it show.

Second: neither single-knob arm can be told from the other's shadow. Removing the
hundred-neighbour cap only helps an obscure artist by letting them survive in a *famous*
artist's list — and if the score threshold still deletes those pairs, nothing arrives.
Lowering the threshold only helps if the newly admitted pairs then survive the cap — and in a
famous artist's crowded list they will not. Each arm's null is explicable by the other rule
still binding. **Only the corner where both are relaxed can support the conclusion "the
listening data is not there."** With the two arms alone, that conclusion is barred, and it is
the conclusion `LBD-R1` exists to test. This is the same shape as the Track 2 stage-2 corner
that produced the only signal in fifteen.

Third, a mechanical point rather than a design one: the score threshold and the per-user
contribution cap are not independent knobs. A pair needs `ceil((threshold+1)/contribution)`
distinct listeners to survive — four at threshold 10 / contribution 3, one at threshold 0.
Lowering the threshold to 0 makes the contribution cap irrelevant, so a contribution arm is
**not** needed to test `LBD-R1`; it would only be needed if a shippable intermediate is
wanted. That is the owner's question, not mine.

## Weakest link

The candidate-count rows are exact arithmetic over the archive and the artifact; the
`top_j`-step row is my reconstruction of `trimmed_union_cap`'s first half, not the builder's
own code path (the real one is pinned by
`test_graph.py::test_trimmed_union_cap_matches_the_frozen_track_b_implementation`). If my
reconstruction is wrong, the split between "top-*j* step" and "ceiling trim" moves — but the
headline comparison, **8 candidates → 4 edges and 19.94 % → 34.36 % ≤ 2**, uses neither, only
the archive and the artifact. I would defend that firmly.

What would falsify the "our ceiling dominates" reading: a build of the extended archive with
`union_degree_ceiling` raised, showing the added set's share-≤2 stays near 34 %. That build
is not this track's to run (§9 parks the cap-rule decision) and I did not run it.

**What currently works only because of the property a ceiling change would remove.** Naming
it because the rule requires it, and because the answer is not nothing: the ceiling of 50 is
what bounds degree at all under `trimmed_union` — the union alone bounds nothing, and the
observed pre-cap maximum here is **14,797**. Raising or removing it restores unbounded hubs,
which is the defect that produced the observed max degree of 11,243 under the deleted legacy
cap. It would also change artifact size, API memory, Dijkstra frontier width, and
`degree_hub_penalty`'s top-1 %-by-degree set. Nothing in `LBD-` should touch it; the point
here is only that `LBD-C2` cannot be read as if it were constant.

---

# What the pre-registration should fix

Ranked: **direct consequences of a measurement** first, then **hypotheses needing a test**.

## Direct consequences of a measurement

1. **Define "our top-N" for `LBD-C1` explicitly as the union of both lexical partitions,
   ordered by score descending, cut at the archive list's own length.** Arithmetic: the
   alternative (own-partition only) has a construction ceiling of median 0.80 / mean 0.6884 /
   p10 0.1800, rising to a *worse* ceiling for famous artists (median 0.88 at the 100 cut) —
   larger than any threshold the document would set. Under the union definition the ceiling is
   ≈ 0.995 mean / 1.0000 median.
2. **Name the achievable ceiling, and set the `LBD-R2` floor beneath it, not at 1.0.**
   Arithmetic: tie-break loss at the truncation boundary ≈ 0.5 % mean, p10 1.3 %; archive
   self-inconsistency 0.16 % of rows non-reciprocal against a non-full partner plus 0.04 %
   score disagreements. So ≈ 99.3 % is the best a perfect reimplementation could reach on
   *this* archive, before any lineage gap. I would put the "we implemented it wrong" floor
   well below that — but where is a judgement about how much lineage drift is plausible, and
   that is not mine to set.
3. **Report `LBD-C1` per fame band as a pooled row-level rate (matched rows ÷ total rows) as
   well as a per-artist distribution.** Arithmetic: median served list length is 14 in the
   least-listened quintile and 100 in the top two, so per-artist overlap has 5× to 7× coarser
   resolution at the obscure end, and 6,575 crawled artists have lists of length 1–4.
4. **Make the pair-table-level candidate count the primary `LBD-C2` statistic**, with the
   built-graph degree as the shipped-consequence secondary. Arithmetic: our own ceiling turns
   the added set's 19.94 % ≤ 2 into 34.36 % ≤ 2 and discards 47.82 % of their endpoint slots,
   so the graph-level statistic measures our cap at least as much as it measures LB's rules.
   Cost of the control: one `GROUP BY` on a parquet the arm already writes.
5. **State the denominator, and score an artist absent from an arm's graph as degree 0.**
   Arithmetic: `CXR-P2`'s median of 4 is over all 29,892 with none absent, so absent-as-0
   makes the cited reference exactly comparable; restricting to the present subset does not.
   Report share-absent separately, as the plan already says.
6. **Demote median degree from a gate to a reported descriptive; gate on share ≤ 2.**
   Arithmetic: 2,000 bootstrap resamples of the added set returned median 4.0 every time
   (resolution 1), the population confound alone moves it by 1, and it flips between random
   halves of the same data (1 → 2 vs 1 → 1). Share ≤ 2 has bootstrap half-width 0.535 pp.
7. **Effect size for graph-level `LBD-C2`: ≥ 10 pp on share ≤ 2, unless the controls in (4)
   and (8) are both reported, in which case ≥ 1 pp.** Arithmetic: a +50.7 % population change
   with no knob turned moved a fixed sparse set's share ≤ 2 by 10.33 pp (deg ≤ 2 stratum) /
   4.75 pp (deg ≤ 4 stratum), reproducing on both halves; bootstrap resolution is 0.535 pp.
   For the pair-table-level statistic, ≥ 1 pp with a paired sign test over the fixed 29,892.
8. **Report the pre-existing 58,793 in every arm as the within-arm reference**, the shape
   `CXR-P2` used. Free, and it is what tells a real supply gain from a population artefact.
9. **Add the fourth arm: cap removed AND threshold lowered together.** Arithmetic: none
   needed — with only the two single-knob arms, each null is explicable by the other rule
   still binding, so the pre-registration must otherwise state that **no combination of the
   two arms can support `LBD-R1`'s "the listening is not there" reading**. Cost: one more
   pair-table run (hours of wall clock, little session time, per plan Task 5).
10. **Pin `drop_unlistenable=False` on every arm build, including `A0`, and say so.**
    Arithmetic: `pipeline.py` raises `PopulationNotCensused` for any archive containing
    artists the census never evaluated; `LBD-P1` counted 142,683 artists in one day against a
    75,000-artist census. Task 7's sketch omits the flag and `BuilderConfig` defaults it
    `True`, so as written every arm build fails. Note in the held-constant section that
    `drop_no_release_tail` and `drop_featured_credit` have no equivalent guard and will
    silently under-filter — constant across arms, so not a confound, but not the served map's
    filtering either.
11. **Add a pre-arm control at Task 1: the share of the 29,892 `CXR` added MBIDs that appear
    in the dump at all.** Arithmetic: `LBD-R8` names the mapping bias as concentrated at the
    obscure end; without this number a null on `LBD-C2` cannot be told from absence-from-the-
    corpus, which is neither of the two explanations `LBD-R1` contrasts. Cost: one `GROUP BY`
    over the parquet Task 1 already extracts, minutes.
12. **Move `union_degree_ceiling = 50` out of §0's held-constant list and into a named
    exposure.** It is not constant in effect under the intervention, per the table above. The
    pre-registration should state that a graph-level `LBD-C2` null is barred from supporting
    `LBD-R1`, and that the pair-table read is what carries that conclusion.
13. **Reconcile §4's `LBD-C2` wording with §6.** §4 says the measurement is "against the
    `CXR-P2` figures"; §6 says every arm's baseline is `A0`. `CXR-P2` was measured in an
    88,685-node graph built from the endpoint archive; an arm's graph will have a different
    population and, per Q1, a systematically different degree distribution for the same
    MBIDs. `CXR-P2` should be named as **context**, `A0` as the **baseline**.
14. **Drop the §0 sentence "which is population-independent for a given cap rule."** It is
    the claim Q1 measured and it does not hold: same MBIDs, same cap rule, no knob turned,
    share ≤ 2 moved 10.33 pp.

## Hypotheses needing a test

15. `LBD-C3`'s revisit threshold — I have no measurement. `LBD-P2`'s per-day estimate is
    "defensible to no better than 3×" by its own owner, and the all-history `(user, pair)`
    aggregation is the unmeasured step. The number arrives at Task 4 and cannot be
    pre-registered from anything on disk.
16. Whether the two-arm null would in fact have been a false null — testable only by running
    the corner arm (item 9).
17. Whether the population confound scales, reverses, or saturates at 5×–50× population.
    Supplied by the isolating build pair named in Q1 (~35 min) plus, at a large population,
    only by an arm itself.

## What I could not derive from what is on disk

- Anything about the full dump, including whether the `CXR` added artists appear in it.
- The lineage gap of §6 — unmeasurable from inside the archive by construction.
- The true (rather than upper-bound) tie ceiling, which needs the full pair table.
- A calibrated population-drift constant: one artifact pair, one ratio, two changed columns.
