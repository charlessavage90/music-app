# `LBD-` fidelity and supply — pre-registration

**Role: ACTIVE, and GOVERNING for the `LBD-` track's criteria, arms, gates and reads.**
Committed **before anything runs on real data** beyond Task 1's descriptive input reads.
It is the operational counterpart to
[`2026-09-06-own-similarity-design.md`](2026-09-06-own-similarity-design.md), whose §4 fixed
the *shape* and plain sentence of each criterion; **this document fixes the values**, and
**where the two disagree on a value, this one governs.** Where they disagree on the track's
purpose, stages or closed list, the design governs and this document is wrong.

**It carries the corrections owed to it** by
[`../findings/2026-09-06-lbd-plan-review.md`](../findings/2026-09-06-lbd-plan-review.md) and
by the fourteen-item list in
[`builder/analysis/2026-09-06-lbd-plan-review/measurement-derivation.md`](../../../builder/analysis/2026-09-06-lbd-plan-review/measurement-derivation.md).
The design and the plan are **deliberately unedited** — that was the reviews' ruling, and
§10 below is the register of what this document amends in each, so a reader of either can
find the correction without this document having rewritten history.

**It owns no figures.** Task 1's inputs and reads are owned by
[`builder/analysis/2026-09-07-lbd-inputs/README.md`](../../../builder/analysis/2026-09-07-lbd-inputs/README.md);
the review's by the directory above; Track B's by
[`../findings/2026-07-30-track-b-cap-selection-results.md`](../findings/2026-07-30-track-b-cap-selection-results.md);
the served map's by
[`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md).
**Cited by section, never restated.**

**Identifiers introduced here: `LBD-A0`–`LBD-A4` (arms), `LBD-G1`–`LBD-G4` (gates),
`LBD-X1`–`LBD-X3` (named exposures).** Collision-checked across every ref
(`git grep -lE '\bLBD-A[0-9]' $(git for-each-ref --format='%(refname)' refs/remotes refs/heads) -- '*.md'`,
and the same for `G` and `X`) on 2026-09-07: all three free. **`LBD-A0` is the same object
the design's §6 and the plan call `A0`** — it is namespaced here because a bare `A0` is
already Track 2's control arm, and Track 2's `A1`–`A7` are simultaneously arms and amendment
IDs, which is the collision `CLAUDE.md` records as having cost a session the rule that
governed it.

---

## §0 — Factor table

### The arms, one row per variant, one column per token that varies

Every arm is a set of values for the six tokens ListenBrainz's job takes. **The baseline for
every arm is `LBD-A0`, our own run at `ALG-B`'s parameters — never the archive** (design §6).

| arm | `days` | `session` | `contribution` | `threshold` | `limit` | pairing | isolating baseline |
|---|---|---|---|---|---|---|---|
| **`LBD-A0`** control | 7500 | 300 | 3 | 10 | 100 | listen | — (it *is* the baseline) |
| **`LBD-A1`** cap removed | 7500 | 300 | 3 | 10 | **none** | listen | `LBD-A0` — `limit` only |
| **`LBD-A2`** threshold floored | 7500 | 300 | 3 | **0** | 100 | listen | `LBD-A0` — `threshold` only |
| **`LBD-A3`** corner, both relaxed | 7500 | 300 | 3 | **0** | **none** | listen | `LBD-A1` — `threshold` only; **and** `LBD-A2` — `limit` only |
| **`LBD-A4`** pairing delta | 7500 | 300 | 3 | 10 | 100 | **distinct** | `LBD-A0` — pairing only |

`LBD-A0`'s parameters are `CANDIDATE_ALGORITHM` in `builder/…/config.py`, read from source
2026-09-07, **less its `filter_True` token** — see `LBD-X3`.

**Each arm's plain sentence, fixed here, before any result exists** (design §4; `CLAUDE.md`
requires these beside the parameters so a report whose wording drifts from them is as visible
as a moved number):

- **`LBD-A0`** — *the same rules ListenBrainz used when they gave us the lists we ship today,
  run on their raw listening data by us instead of by them.* Everything else is measured
  against this, never against the lists themselves.
- **`LBD-A1`** — *keep ListenBrainz's bar for how strong a connection has to be, but stop
  cutting each artist's list at a hundred.* Tests whether the cap alone was hiding
  connections.
- **`LBD-A2`** — *keep the hundred-connection cut, but accept every connection the listening
  data produces however weak.* Tests whether the strength bar alone was hiding connections.
- **`LBD-A3`** — *no cut and no strength bar: every connection two artists' shared listeners
  imply.* **This is the one that can say "there is nothing more to find."** If an artist is
  still a dead end here, no choice of these two rules could have helped them.
- **`LBD-A4`** — *count a pair once per session rather than once per pair of plays.* Someone
  playing one artist twice and another once currently counts double; this asks whether that
  choice matters.

**`LBD-A3` is why this table exists.** With only `LBD-A1` and `LBD-A2`, each null is
explicable by the other rule still binding: removing the cap helps only if the new pairs
clear the threshold, and lowering the threshold helps only if the new pairs survive the cap.
**Only the corner can support `LBD-R1`'s reading that the listening is not there.** This is
the same shape as Track 2's stage-2 corner, where the four arms a session recommended
skipping produced the only signal in fifteen. Derivation item 9.

**`threshold` 0 is the floor, not a small number.** `HAVING score > threshold` is strict over
an integer, so 0 keeps every pair whose cross-user score truncates to 1 or more. Nothing
weaker exists inside LB's formulation, which is what makes `LBD-A3` decisive rather than
merely permissive.

### Held constant, and why each is genuinely constant under the intervention

| held constant | why the intervention cannot change it |
|---|---|
| `days`, `session`, `skip`, `contribution` | identical across all five arms by construction; each is fixed at `ALG-B`'s value |
| the listen corpus | one pinned dump, no incrementals applied (design `LBD-D5`; Task 1) |
| the MusicBrainz side-tables | one `mbdump` snapshot, pinned by sha; `recording_length` and `artist_credit` derived from it once |
| cap strategy `trimmed_union`, `top_j = 50` | applied by `build` after the similarity table; identical `BuilderConfig` for every arm |
| similarity rescale `p99_log_clip` | the only strategy `BuilderConfig.__post_init__` permits |
| router weights and cost function (`ApiConfig`) | nothing in `builder/` writes them, and no routing read is made in this pre-registration |
| the fidelity ground truth (`grt-archive-algb.pre-cex-snapshot`) | read-only, pinned by path and identity before Task 4 |
| the `CXR` added set and the pre-existing set | pinned to files with committed sha256s at Task 1, never re-derived per arm |

### Named exposures — terms that are NOT constant in effect, and must not be read as though they were

**This section exists because the design's §0 put two of them in the table above.** A term
inert in the baseline for a reason the intervention removes is an uncontrolled variable that
appears only in the arms that succeed.

- **`LBD-X1` — the degree ceiling (`union_degree_ceiling = 50`).** Nothing here changes it,
  and its *effect* grows in exactly the arms that succeed: an arm that supplies more
  candidates hands more of them to a rule that deletes the weakest edges of over-full
  artists, **bilaterally** — the connection is taken from the obscure artist at the other end
  too. **Consequence, and it is a bar, not a caveat: a graph-level `LBD-C2` null is barred
  from supporting `LBD-R1`.** The pair-table-level read (`LBD-C2a`) is what carries that
  conclusion. Derivation items 4 and 12; moved out of design §0's held-constant list by §10
  below.

  > **Raising the ceiling is not a free downstream fix, and a reader of a strong pair-table
  > result must not infer that it is.** It has already been measured: Track B's `TUw-50-100`
  > isolates the ceiling alone against `TUw-50-50` (its pre-registration's grid names the
  > isolating baseline as "d only"), and **the whole bound-100 set fires the `CRS-C4`
  > material hub-transit bar on the broad famous class on both archives.** Figures are owned
  > by [`../findings/2026-07-30-track-b-cap-selection-results.md`](../findings/2026-07-30-track-b-cap-selection-results.md) §1
  > and the grid in [`2026-07-30-track-b-cap-selection-preregistration.md`](2026-07-30-track-b-cap-selection-preregistration.md) —
  > **cited, never restated here.** In plain terms: letting artists hold more connections
  > measurably pushed journeys through the most-connected artists more often, which is the
  > mechanism a blind listen has already condemned.
  >
  > **And both sweeps predate the crawl extension**, so neither graph contained the added
  > artists and **no criterion in either measured that set's degree**. The ceiling's effect
  > *on them* is genuinely unmeasured.
  >
  > > ### ⚠ AMENDED 2026-09-08 by `LBD-AM2` — the last sentence above is no longer true
  > >
  > > **"The ceiling's effect *on them* is genuinely unmeasured" was true when written and is
  > > not true now.** The `DCF-` probe measured exactly that on the extended archive, and the
  > > `DFA-` probe measured the complementary question. **Nothing above is edited**, per §12's
  > > rule; this note qualifies it in place.
  > >
  > > **Figures are owned by
  > > [`builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md`](../../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md)
  > > and [`builder/analysis/2026-09-07-degree-floor-at-admission/README.md`](../../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md);
  > > this document owns none of them and restates none.** Read the ceiling probe's §3 with
  > > its own ⚠ forward-correction note, which bounds what one of its measures can support.
  > >
  > > **What this does NOT do, and the distinction is the whole point of the amendment.** It
  > > does **not** weaken `LBD-X1`, and it does **not** license reading a graph-level
  > > `LBD-C2` null as a supply null — that bar stands exactly as written, because it rests
  > > on the ceiling *absorbing supply*, not on its effect being unmeasured. Nor does it
  > > propose or support a ceiling change: design §9 keeps the cap-rule decision **parked and
  > > the owner's**, and the measured cost on famous-pair journeys is unchanged.
  > >
  > > It is recorded because a later reader finding this sentence would otherwise conclude
  > > the question is open when two committed probes have answered it — and, per `LBD-AM1`,
  > > the residual set exists precisely *because* that answer came back. So the two facts point in opposite directions and
  > neither is discharged: a ceiling change has a measured cost on famous-pair journeys, and
  > an unmeasured benefit on the added set. **Any later reader proposing one owes a fresh
  > pre-registration** — it is a cap-rule decision, which design §9 places on the closed
  > list for this track and `NEXT.md` places with the owner.

- **`LBD-X2` — the population.** A similarity table computed from the dump names a different
  artist set from the crawl's, and every population-relative quantity recomputes over it:
  `pop_raw`, `fame_lb_pctl`, `degree_hub_penalty`, and the p99 rescale. Measured by the
  review: **same MBIDs, same cap rule, no knob turned, a larger population alone moves the
  supply reading, in the direction that flatters every arm** (magnitude owned by the
  derivation's Q1). This is why `LBD-C2` reports the pre-existing set in every arm as the
  within-arm reference (`LBD-G2`'s second condition).

- **`LBD-X3` — the drop lists are no longer the served map's filtering.**
  `BuilderConfig.drop_unlistenable` defaults `True` and `pipeline.py` raises
  `PopulationNotCensused` for any archive containing artists the `ULF-` census never
  evaluated; every arm's population is larger than that census by construction. So **every
  arm build, `LBD-A0` included, pins `drop_unlistenable=False`** (derivation item 10), and
  the un-listenable filtering is simply absent. `drop_no_release_tail` and
  `drop_featured_credit` have no equivalent guard and will **silently under-filter** over a
  population their lists never covered. All three are constant across arms, so none is a
  confound between arms; **none of them reproduces the served map's filtering**, so no
  cross-comparison with the served map's own figures may treat filtering as matched.
  A re-census is **not** required for this track, and this does not touch `ULC-F4`.

  > ⚠ **Qualified 2026-09-10 by `LBD-AM4-3`** (§10's build-stage block): over the FIXED
  > population `P` the census guard passes and all three lists are measured inert, so the
  > build-stage arms pin `drop_unlistenable=True` through the override. `False` remains the
  > rule for any arm over the table's own population. Nothing above is edited.

  Verified from source 2026-09-07, not from the review's prose: `drop_unlistenable: bool =
  True` at `builder/…/config.py:243`, and `pipeline.py:310` raises with a message that
  itself names `drop_unlistenable=False` as *"an experimental control and never a shipping
  configuration"*. That is the builder's own words for what every arm here is, and it is a
  second, independent statement of `LBD-D7`.

  Separately, `ALG-B`'s token carries `filter_True`, which current ListenBrainz source does
  not emit (`LBS-2`). Our reimplementation cannot reproduce a stage that is not in the
  source, so **`LBD-A0` is `ALG-B`'s parameters minus that token**, and the difference is
  part of the lineage gap `LBD-C1` measures rather than a defect it can detect.

---

## §1 — The structural finding, verified from source, and the run plan it forces

**Verified 2026-09-07 by re-fetching
`https://raw.githubusercontent.com/metabrainz/listenbrainz-server/master/listenbrainz_spark/similarity/artist.py`
(sha256 `7a8516be7fb0c25b99ef63f3210029c348cf69c987a3ce540f325262e4b90de3`, 161 lines) and
reading `build_sessioned_index` stage by stage.** Not transcribed from the plan's prose and
not from `findings/2026-07-30-lb-algorithm-semantics.md` — a review found the plan's prose
contradicts the SQL it quotes, so prose is not admissible evidence about this.

| stage in the SQL | what it does | which token it depends on | relative to the cross-user aggregation |
|---|---|---|---|
| `get_listens_from_dump(from, to)` | selects the window | `days` | **before** |
| `listens` | credit fan-out, duration join, `after_ft_jp` | — | before |
| `ordered` | inter-listen gap; per-row `similarity` 1 or 0.25 | — | before |
| `sessions` | `session_id`; `skipped` | `session`, `skip` | before |
| `sessions_filtered` | `WHERE NOT skipped` | — | before |
| `user_grouped_mbids` | the self-join inside a session | pairing (`LBD-D6`) | before |
| `user_contribtion_mbids` | `LEAST(SUM(similarity), contribution)` per `(user, pair)` | `contribution` | **the per-user aggregation** |
| `thresholded_mbids` | `BIGINT(SUM(part_score))` per pair, `HAVING score > threshold` | `threshold` | **the cross-user aggregation; the HAVING is applied to its output** |
| `ranked_mbids` | `rank() OVER (PARTITION BY mbid0 ORDER BY score DESC)`, `rank <= limit` | `limit` | **after** |

**The claim holds. `threshold` and `limit` are the only two tokens applied strictly after the
cross-user aggregation, and neither enters the `score` expression.** `days`, `session`,
`skip`, `contribution` and the pairing semantics all change `score` itself and are therefore
*not* derivable by filtering.

### Consequence for the run plan — `LBD-S2` and the first four arms are ONE full-history pass

**Materialise the aggregated table once:**

```
T = SELECT mbid0, mbid1, BIGINT(SUM(part_score)) AS score
      FROM user_contribtion_mbids GROUP BY mbid0, mbid1
    HAVING score > 0
```

— i.e. stage `thresholded_mbids` at the **lowest threshold any arm uses (0)** and with **no
rank cut**. Then:

- **`LBD-A0`** = `T` filtered `score > 10`, ranked per `mbid0`, `rank <= 100`
- **`LBD-A1`** = `T` filtered `score > 10`, no rank cut
- **`LBD-A2`** = `T` unfiltered, ranked per `mbid0`, `rank <= 100`
- **`LBD-A3`** = `T` unfiltered, no rank cut — i.e. `T` itself

All four are **pure filters and window functions over one materialised table**, minutes each,
and they are **exactly** what the SQL would have produced at those parameters — not an
approximation. `LBD-A4` varies pairing and therefore needs its **own** pass; it is the
second and last full-history run this pre-registration schedules.

**Two properties of `rank()` that a derivation must preserve, or the arms are not what they
claim.** It is `rank()`, not `row_number()`, so ties at the cut all survive and an arm may
return more than `limit` rows for one `mbid0`. And the cut partitions on `mbid0` only, so an
artist also collects the pairs where it sorts second and the *other* artist's cut kept them —
this is the "up to 2×" the endpoint's own docstring describes and `LBS-3` measured.

### Size, where it lands, and the fallback

**`T` lands at `D:\unsung-large-data\lbd-pairs\aggregate\`**, parquet, sorted `(mbid0, mbid1)`
(`LBD-D5`). Arms land at `D:\unsung-large-data\lbd-pairs\<arm>\`. D: had **1,735 GB free** on
2026-09-07.

**The row count is the one quantity that cannot be pre-registered from anything on disk**, and
saying otherwise would be the failure this project's rules exist to prevent. What is known:
the pinned dump's listen count and the one-day pair figures are owned by Task 1's README and
`builder/analysis/2026-09-06-lb-dump-feasibility/README.md` `LBD-P2` respectively; the
all-history `(user, pair)` aggregation grows **sub-linearly** in listens because a user's
pairs repeat, and **super-linearly** in the artist set because history touches far more
artists than one day does. The two pull opposite ways and no measurement on disk separates
them. At three columns with dictionary-encoded MBIDs, parquet costs roughly 8–16 bytes a row,
so the table fits D: at any row count up to the low hundreds of billions; **disk is not the
binding constraint, and memory during the aggregation is.**

**So the pass is gated, not guessed — `LBD-G4`, §8.** Run the aggregation first on a
`user_id % 16 = 0` slice, record its row count and wall-clock, and extrapolate before
committing to the full pass.

**The fallback is chunking by `user_id % k`, and it is EXACT, not an approximation.** Every
stage up to and including `user_contribtion_mbids` partitions by `user_id` — sessions,
the skip filter, the self-join and the per-user cap all live inside one user — so chunking by
user changes nothing about `part_score`. Only the final `SUM(part_score)` crosses users, so
the chunks' `user_contribtion_mbids` outputs are unioned and re-summed by `(mbid0, mbid1)`
once. **A `GROUP BY` after the union is the whole of the correction.** Read off LB's SQL,
2026-09-07.

---

## §2 — `LBD-C1`, fidelity

> **Plain sentence: when we compute similarity the way ListenBrainz says it does, using their
> own listens, how much of what they told us about each artist do we get back?**

**Our top-N is defined as: the union of both lexical partitions for that artist — every pair
in which the artist appears as either `mbid0` or `mbid1` — ordered by score descending with
the MBID as tie-break, cut at N = the length of the archive's own list for that artist.**
Derivation item 1, and this definition is worth more than any threshold below it. The
alternative reading (the artist's own `mbid0` half, which is what the SQL literally emits per
partition) carries a **construction ceiling far below 1.0 that is *worse* for famous
artists**; the union reading's ceiling is near 1.0. Both ceilings are owned by the
derivation's Q2. Under the own-partition reading a *perfect* reimplementation would fail this
criterion, which makes it the wrong instrument regardless of where a floor is set.

**Sample.** 3,000 artists drawn by MBID from **the pinned snapshot
`C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot`**, by path, its identity
confirmed against the `LUX-E1` README before the draw — **not from the live archive tree**,
which gained tens of thousands of response files after the served map was built. Stratified
into five equal bands by `fame_lb_raw` from the served artifact's metadata, 600 per band,
drawn with `random.Random(20260907)` over the sorted MBID list, **and the resulting list is
committed as a file with its sha256 before Task 4 runs.** Derivation item 3 and `LBDR-F7`.

**Reported two ways, both required.** A per-artist overlap distribution (median, p10, p25,
p75 by band — never one mean), **and** a pooled row-level rate (matched rows ÷ total rows) by
band. The pooled rate exists because served list lengths differ by roughly 5×–7× between the
most- and least-listened bands, so a per-artist share has far coarser resolution at the
obscure end, and thousands of crawled artists have lists of only a few entries. Derivation
item 3; the length figures are owned by the derivation's Q2.

**`LBD-G1` — the "we implemented it wrong" floor: pooled row-level rate below 0.60 in the
top band.** Plain: *for the best-covered, most-listened artists, we get back less than three
in five of what ListenBrainz told us.* The top band is the gate's subject because it is where
the lineage gap has the least room to hide: those artists have full 100-entry lists, the most
listens, and the least mapping loss. The achievable ceiling on a perfect reimplementation is
≈ 0.99 (derivation item 2, figures owned there), and every documented lineage difference —
unknown dataset date, the `filter_True` stage, absent deletions, unknown upstream bot
handling, the two-partition union — is a *subtractive* effect of unknown size. 0.60 sits far
enough below the ceiling that only a defect plausibly reaches it, and far enough above zero
that a genuine lineage gap is not called a bug. **It is a design choice with no prior
calibration and is stated as such.**

---

## §3 — `LBD-C2`, supply

> **Plain sentence: do the ~29,900 artists the crawl extension added — the ones that arrived
> with almost no connections — get more connections when the list cap and the score threshold
> are ours instead of ListenBrainz's?**

**The set is fixed and pinned, never re-derived per arm:** MBIDs present in
`graph-cxa-adopted.bin` and absent from `graph-msw-tu50.bin`, read through the shipped
`GraphStore` with both artifacts sha256-verified against their manifest sidecars, written to
`D:\unsung-large-data\lbd-inputs\cxr_added_mbids.txt`. That file and the pre-existing set
beside it carry committed sha256s in Task 1's README, and **every arm reads those files.**

**Two levels, and the primary one needs no build.**

- **`LBD-C2a` — pair-table level, PRIMARY.** *Plain: how many other artists does ListenBrainz's
  listening data offer as a candidate connection for each of these artists, before any of our
  own rules touch it?* Per added artist, the number of distinct partners in the arm's derived
  pair table. One `GROUP BY` on a parquet the arm already wrote. **This is the statistic
  `LBD-R1` is read off**, because it is upstream of `LBD-X1` entirely. Derivation item 4.
- **`LBD-C2b` — graph level, SECONDARY.** *Plain: how many connections do they actually end up
  with in a map we could ship?* Degree in the arm's built graph. It measures our cap rule at
  least as much as it measures ListenBrainz's, which is the point of calling it secondary.

  > ⚠ **Build stage fixed 2026-09-10 by `LBD-AM4`** (§10's block): the arms are built over
  > the served lineage's own population `P`, so this read lands on `CXR-P2`'s ruler. The
  > read itself is unchanged.

**Denominator and absence.** Both levels score over **all 29,892**, with an artist absent from
the arm's table or graph counted as **degree 0**, so the figures are directly comparable with
the `CXR-P2` reference. Share-absent is reported separately, because *absent* and *present
with degree 1* are different outcomes. Derivation item 5.

**Statistic: the share at or below 2 connections.** *Plain: what fraction of them are still
dead ends?* **Median degree is reported and is NOT gated on** — it bootstraps to a single
value at this resolution, moves by a whole unit under the population confound alone, and flips
between random halves of the same data. Derivation item 6; figures owned there.

**`LBD-G2` — the effect size that counts as movement.**

| read | effect size on share ≤ 2, vs `LBD-A0` | condition |
|---|---|---|
| `LBD-C2a` pair-table | **≥ 1 percentage point**, paired sign test over the fixed 29,892 | always |
| `LBD-C2b` graph | **≥ 1 percentage point** | **only if** both controls are reported: the pre-existing 58,793 as the within-arm reference, and the `LBD-C2a` figure for the same arm |
| `LBD-C2b` graph | **≥ 10 percentage points** | if either control is missing |

The 10-point bar is the population confound's own measured size plus headroom; the 1-point bar
is just above the bootstrap resolution and is only admissible once the controls make a
population artefact distinguishable from a supply gain. Both rest on the derivation's Q1 and
Q3, whose figures are owned there. Derivation items 7 and 8.

**The isolating pair of builds** that would turn the population-drift figure from an order of
magnitude into a constant is **deliberately not commissioned**, and the order of magnitude is
declared sufficient for `LBD-G2` — because `LBD-G2`'s 10-point bar is set at that order of
magnitude rather than inside it, and the 1-point path does not rely on the constant at all.
That discharges the review's open deferral on it with a sentence, as it asked.

> ### ⚠ AMENDED 2026-09-07 by `LBD-AM1` — `LBD-C2a` is additionally reported stratified
>
> **Written before any arm had run**, and it adds a **reporting requirement only**. Nothing
> above this block is edited. **It adds no gate and no effect size**: it changes no threshold,
> triggers no branch, and **does not alter the `LBD-C2a` read or `LBD-G2`**, both of which stand
> exactly as written above and continue to be evaluated over all 29,892.
>
> **In addition to the whole-set figure, `LBD-C2a` is reported over two strata:**
>
> - **the residual set** — the added artists **still at two or fewer connections when our own
>   degree ceiling does not bind**, `n` = 5,967; and
> - **its complement**, `n` = 23,925.
>
> **Why this stratum and not another.** Two probes ran on 2026-09-07 and were read before this
> was written: [`builder/analysis/2026-09-07-degree-ceiling-falsifier/`](../../../builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md)
> and [`builder/analysis/2026-09-07-degree-floor-at-admission/`](../../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md),
> which **own every figure in this paragraph; this document owns none of them.** Measured there:
> with our own degree ceiling made non-binding, a **minority** of the added artists stop being
> dead ends, and **the rest stay dead ends with the degree trim deleting nothing of theirs** —
> the ceiling is not what was holding them back. That residual group is the part of the
> problem **raising the degree ceiling cannot reach**, and it is the part `LBD-` addresses. A
> whole-set figure mixes it with a group a ceiling change alone could rescue, so a whole-set
> movement cannot tell the two apart.
>
> ⚠ **"The ceiling cannot reach them" is NOT "no rule of ours can."** Both probes held the
> union width at `union_top_j = 50` and both kept the drop lists, and the top-*j* cut deletes a
> large share of candidate edges before the trim ever runs — figures owned by the ceiling
> probe's §6. **No arm anywhere has varied the union width**, so whether it would reach this
> stratum is unmeasured, and this amendment must not be read as ruling it out. It is also
> **not a reason to run one**: that is a cap-rule question, parked and the owner's.
>
> **The set is fixed and pinned, never re-derived per arm**, exactly as the added and
> pre-existing sets above:
>
> | | identity |
> |---|---|
> | source | `builder/analysis/2026-09-07-degree-floor-at-admission/dfa_residual_mbids.txt`, sha256 `fa8d85cc12131f3cd39ecebeb5da0d52a1236104acbcbabf20232c72b4f43a08` |
> | pinned for the arms to read | `D:\unsung-large-data\lbd-inputs\cxr_residual_mbids.txt`, same sha256 |
> | the record it was extracted from | `dfa_benefit_identity.json`, sha256 `f10b3329d29b36d896d30f1308bf1394961d4e86ca24a9d6c08f3038e2f26675` |
>
> *That record as first committed held **counts only, no MBIDs**. The list was produced by
> re-running that probe's own committed script with list emission added, and every pre-existing
> value in the record reproduced exactly. Stated because "taken from the committed record"
> would otherwise overstate what the record held.*
>
> **`R12` — the one named failure mode this adds**, extending §9's own `R1`–`R11` branch series.
> It is a read, not a gate, and it fires on no threshold of its own:
>
> > **If `LBD-C2a` clears its bar over the whole set while the residual set does not move, the
> > report must say so in those words**, and the read is that **the loosened settings produce
> > candidate connections but not for the artists this track exists to help.**
>
> **Two limits, both binding on any use of this stratum.**
>
> 1. **The residual set was measured on one population under one cap rule** and inherits that
>    probe's caveats. It is **a pinned MBID list, not a claim about any other build**, and it
>    must not be transferred to a different lineage or re-derived per arm.
> 2. **The candidate fix for the complement sits outside this track.** Design §9 keeps the
>    cap-rule decision **parked and the owner's**, and **nothing here proposes, runs or depends
>    on one.**
>
> **Reachability, checked now rather than discovered at Task 4.** An artist nobody played can
> gain no edge at any threshold or cap, so if a large share of the residual set were absent from
> the dump that would bound the whole track. It was cross-checked against what Task 1 measured,
> and **it is not a bound: 0.13 % of the residual set is absent from the corpus and 99.67 % have
> at least the four distinct listeners a pair arithmetically requires, marginally better than
> the complement.** They are nonetheless **listened to less** — a median of 81 distinct listeners
> against the complement's 140 — which is not a reachability bound but leaves less room for the
> co-occurrence a pair actually needs. **Figures owned by
> [`builder/analysis/2026-09-07-lbd-am1-residual-reachability/README.md`](../../../builder/analysis/2026-09-07-lbd-am1-residual-reachability/README.md)
> §3, carried here because a bound a reader cannot size is not a bound; this document owns
> none of them.** Enough listeners is **necessary, not sufficient** — nothing measures
> co-occurrence, so this must not be read as evidence that any arm will move `LBD-C2`.

---

## §4 — `LBD-C3`, cost

> **Plain sentence: how long does one full run take on this machine?**

Descriptive. Wall-clock, peak memory and spill volume for the full-history pass, recorded per
stage. **`LBD-G3`: if the full pass exceeds 12 hours or spills more than 500 GB, the chunked
form of `LBD-D2` is built and measured before any further pass runs** — including `LBD-A4`.
The bound is a working-session choice, not a measurement: 12 hours is the longest run that
still fits between two sessions on the owner's own machine without occupying it for a working
day. No figure on disk calibrates it, and `LBD-P2`'s per-day estimate is defensible to no
better than 3× by its own owner.

## §5 — `LBD-M1`, population

> **Plain sentence: how many artists does each arm produce, and how does that compare with the
> served map's?**

Descriptive, decides nothing here, and feeds `LBD-S4`. Reported by fame band where fame is
known from the served artifact and "unknown" otherwise. It also **discharges `LBDR-F6`**: the
artist and neighbour counts are the numbers the Task 6/7 scale budget needs and the track has
not had.

## §6 — The synthetic sub-check

Design §6 makes this the only thing separating "we implemented it wrong" from "the inputs
differ", and §7 retires `LBD-R2` on it.

**Its expected values are derived by executing ListenBrainz's quoted SQL by hand — from the
fetched source, never from the plan's prose.** The plan's featured-weight sentence describes
a different computation from the SQL it quotes, and a fixture built from that sentence would
agree with a wrong implementation and disagree with ListenBrainz. That defect **surfaces
never** on its own; this clause is the only thing that catches it. `LBDR-F2`.

**Two specifics the fixture must exercise, both read off the source rather than described:**

- **The window frame.** `any(...) OVER w` with `w` carrying `ORDER BY ac.position` and no
  explicit frame defaults to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, so
  `after_ft_jp` is true when **any join phrase at position ≤ the row's own** matches —
  including the row's own. In MusicBrainz a credit's `join_phrase` is the text that *follows*
  that artist, so in "A feat. B" it is **A**, the main artist, that carries `feat.` and is
  weighted 0.25 — and B is weighted too, through the cumulative frame. The fixture must
  contain a multi-artist credit and assert both.
- **Untrimmed comparison.** LB compares `acn.join_phrase` verbatim, and MusicBrainz stores
  join phrases with their surrounding spaces, so `' feat. '` does not match the literal
  `'feat.'`. The fixture must contain one credit with spacing and one without, and assert
  that only the unspaced one is weighted. **An implementer who trims diverges from
  ListenBrainz on every multi-artist credit in the corpus.**

Task 1's third read measures how often this fires on the real corpus at all; its figure is
owned by Task 1's README. **That figure does not change the fixture** — fidelity to LB's
behaviour is the requirement whether the term is live or dead — but it tells a later reader
how much of `LBD-C1` could possibly turn on it.

## §7 — Task 1's reads, and what they may and may not decide

Task 1 ran **before** this document was committed and is descriptive input verification, not
an arm. Its figures are owned by
[`builder/analysis/2026-09-07-lbd-inputs/README.md`](../../../builder/analysis/2026-09-07-lbd-inputs/README.md).
Two of its reads bear on the reads below and their bearing is fixed here, before they are used:

- **Corpus membership of the added set** (derivation item 11). *Plain: how many of the ~29,900
  added artists does anyone in ListenBrainz's data listen to at all, and how many are listened
  to by enough different people to be able to clear the score threshold?* **This bounds the
  whole track.** An added artist absent from the corpus can gain no edge at any threshold and
  any cap, and that outcome is **neither** of the two explanations `LBD-R1` contrasts — it is
  a third, and the reads in §9 name it explicitly. The user-count half is arithmetic on LB's
  own SQL, not an estimate: each user contributes at most `contribution` and the `HAVING` is
  strict, so a pair needs at least ⌈(threshold+1)/contribution⌉ distinct users before it can
  survive — **four** at `LBD-A0`'s parameters, **one** at `LBD-A2`/`LBD-A3`'s.
- **The heavy-user census** (`LBD-R9`, cheap half). **Decides nothing.** Whether a user filter
  becomes an arm is a decision this pre-registration declines to take, and taking it later
  would require a fresh pre-registration, because by then results exist.

## §8 — Gates, each with its own effect size

**Every gate and branch trigger here carries the size of difference that fires it.** A trigger
without one cannot tell the finding it was written for from noise, and it fires the expensive
response either way.

| gate | fires when | consequence | effect size |
|---|---|---|---|
| **`LBD-G1`** fidelity floor | pooled row-level `LBD-C1` in the top fame band **< 0.60** | **stop.** Find the defect; do not run arms on a reimplementation whose gap is unexplained. The synthetic check having passed means it is an input or join difference — durations, credits, redirects, mapping | 0.60, against an achievable ceiling of ≈ 0.99 |
| **`LBD-G2`** supply movement | see §3's table | an arm is read as having moved supply | ≥ 1 pp with controls, ≥ 10 pp without |
| **`LBD-G3`** cost | full pass **> 12 h** or spill **> 500 GB** | build and measure `LBD-D2`'s chunked form before any further pass | 12 h / 500 GB |
| **`LBD-G4`** aggregation feasibility | the `user_id % 16` slice extrapolates to a full-pass peak memory above 24 GB **or** a `T` above 20 billion rows | **do not run the full pass**; go straight to the chunked form. Extrapolate rows linearly in users and memory linearly in rows — both are conservative here, since pairs repeat across users | 24 GB / 20 bn rows |

> ### ⚠ AMENDED 2026-09-10 by `LBD-AM3` — `LBD-G1` FIRED, the gap is diagnosed, and the arms are read anyway, by owner decision
>
> **Written AFTER a result existed. This amendment spends the commit-before-results property
> of `LBD-G1` and of nothing else**, and it is recorded as an owner decision, not a session's.
>
> **What happened.** `LBD-C1` read **0.5844** in the top band on the pinned corpus — below
> the 0.60 floor — so `LBD-G1` fired and `R1` governed: no arm was read. Figures are owned by
> [`builder/analysis/2026-09-08-lbd-similarity/README.md`](../../../builder/analysis/2026-09-08-lbd-similarity/README.md)
> §5; **nothing above this note is edited and the 0.5844 reading stands.**
>
> **The diagnosis `R1` demanded was taken** (README §5a–5c), and it names the input
> difference the gate's own consequence column asks for: **the deployed dataset was computed
> on a far smaller listening corpus.** Our scores are ~3× ListenBrainz's on the same pairs in
> every band; the dump's `created` column shows about a third of today's mapped listens
> existed by autumn 2024; and a controlled rerun on the corpus as of 2024-10-01 — one knob,
> with its three readings committed before it ran (`C1-DIAG-1`) — lifted the top band to
> **0.6349** and halved the ratio to 1.5×. A second, smaller term is structural: ~4 % of the
> top band's archive entries are uncredited band members, whom no job over the recording
> credit can pair, so the "achievable ceiling of ≈ 0.99" in the row above is **≈ 0.96 at
> most** for a perfect reimplementation of current source. The synthetic sub-check (§6)
> passed with seven mutants red, which is what separates "inputs differ" from "implemented
> wrong" here, exactly as the design's §6 intended.
>
> **The decision.** The owner ruled 2026-09-10 (option 1 of three, tabled with the diagnosis)
> that the gap is explained and **`LBD-A0`–`LBD-A3`, already derived from the pinned corpus,
> may be read** under `LBD-C2a` and `LBD-G2` exactly as written. **The floor is not moved,
> the reading is not re-taken on the dated corpus, and no criterion value changes.** A later
> reader must not cite `LBD-C1` as "passed": it fired, was explained, and was overridden.
>
> **What it must not be read as.** Not a finding that the reimplementation is faithful beyond
> what §6's sub-check shows; not licence to re-read any other gate after its result; and not
> a change to `LBD-C1`'s definition — the two residuals the diagnosis leaves (a ratio of 1.5
> rather than 1, and the band-member class) are recorded there as lineage, unexplained in
> mechanism and measured in size.

**`LBD-G4` is a new gate this document adds to the plan**, and it exists because the size of
`T` is the one quantity nothing on disk bounds. The 1-in-16 slice costs a small fraction of
the full pass and is the cheapest thing that could change the run plan.

## §9 — The read of every possible result, including the null, with the run state each presupposes

**Run state vocabulary.** *Task-1-complete* = inputs pinned, the three reads recorded.
*T-materialised* = the full-history pass has produced `T` and the four derivations
`LBD-A0`–`LBD-A3`. *Fidelity-read* = `LBD-C1` computed against the pinned snapshot.
*Pairing-read* = `LBD-A4` has run. *Built* = the arms have been emitted to archives and built
into graphs.

| # | result | read | run state it presupposes |
|---|---|---|---|
| **R1** | `LBD-C1` top-band pooled rate **< 0.60** | `LBD-G1` fires. The reimplementation is presumed wrong. **Stop and diagnose**; arms already derived from `T` are not read, because they inherit the same defect | fidelity-read; T-materialised is *not* required and the fidelity run should precede the arm reads for exactly this reason |
| **R2** | `LBD-C1` **≥ 0.60**, and materially below the ceiling | proceed. The residual is recorded as lineage gap, per design §6, and its size is reported by band rather than summarised | fidelity-read |
| **R3** | `LBD-C1` at or near the ceiling | proceed, and record that the lineage differences design §6 enumerates are jointly small on this corpus. **This does not retire them** — it bounds them | fidelity-read |
| **R4** | `LBD-C2a` moves ≥ 1 pp on `LBD-A3` (the corner) | **the listening data IS there and our rules were withholding it.** `LBD-R1` is refuted. This is the result that makes the emitter and build work worth doing, and it is the owner's call whether to do it | T-materialised |
| **R5** | `LBD-C2a` moves ≥ 1 pp on `LBD-A1` or `LBD-A2` **but not** on `LBD-A3` | **impossible by construction** — `LBD-A3` is strictly more permissive than either at the pair-table level. **If observed, it is a bug in the derivation, not a finding.** Stop and fix | T-materialised |
| **R6** | `LBD-C2a` **null on `LBD-A3`**, and Task 1 found the added artists **present** in the corpus with enough distinct listeners | **`LBD-R1` is upheld: the listening is not there in the co-occurring form similarity needs.** The people who play these artists do not also play others in a way that survives sessioning. This is a real, publishable-internally null and it closes the supply half of the track | T-materialised **and** Task-1-complete |
| **R7** | `LBD-C2a` **null on `LBD-A3`**, and Task 1 found a large share of the added artists **absent** from the corpus or below the distinct-user minimum | **neither explanation `LBD-R1` contrasts.** The added artists are not in ListenBrainz's listening data at all, so no parameter choice could have helped, and the null says nothing about the rules. The track's premise fails at the input, not the algorithm | T-materialised **and** Task-1-complete |
| **R8** | `LBD-C2a` moves but `LBD-C2b` does not | **our own degree ceiling is absorbing the gain.** Report both; the graph-level null is **barred** from being read as a supply null (`LBD-X1`). Do **not** propose a ceiling change on this evidence — see `LBD-X1`'s block on what that already cost | built |
| **R9** | `LBD-C2b` moves but the pre-existing 58,793 move by as much or more | a **population artefact**, not a supply gain. The within-arm reference is what distinguishes them and this is the reading it exists for | built |
| **R10** | `LBD-A4` changes `LBD-C1` or edge count materially | the pairing semantics are load-bearing; record which every later arm uses and why, per `LBD-D6`. **Material = the `LBD-G2` bar applied to edge count, or 5 pp on the pooled `LBD-C1` rate** | pairing-read |
| **R11** | `LBD-G4` fires on the slice | the full pass is not attempted; the chunked form is built first. **Not a finding about anything** — it is a resource fact | a `user_id % 16` slice only |
| **R12** *(added 2026-09-07, `LBD-AM1`)* | `LBD-C2a` clears its bar **over the whole set** while the **residual set does not move** | **the loosened settings produce candidate connections, but not for the artists this track exists to help.** The report **must say so in those words**. Not a gate and carries no effect size of its own: the bar is `LBD-G2`'s, applied to each stratum and read side by side. Absence is already ruled out as the explanation (§3's block), so this reads as a genuine failure to reach the residual group, not as a gap in the corpus | T-materialised |

**Nothing in this table is reachable before its run state.** In particular, **R4–R9 all
presuppose that all four derivations exist**, and R6 and R7 are distinguishable *only* with
Task 1's membership read in hand — which is why that read is a Task 1 item rather than a
convenience.

## §10 — What this amends in the design and the plan

Neither document is edited; both are governing for everything not listed here.

**In `specs/2026-09-06-own-similarity-design.md`:**

1. **§0's sentence "which is population-independent for a given cap rule" does not hold** and
   is void. Derivation item 14.
2. **§0's drop-list row is void** and is replaced by `LBD-X3` above.
3. **The degree ceiling moves out of §0's held-constant list** into `LBD-X1`, a named
   exposure. It is still not a knob this track turns.
4. **§4's `LBD-C2` "against the `CXR-P2` figures" is corrected**: `LBD-A0` is the baseline,
   `CXR-P2` is context. §6 already said so and §4 disagreed with it. Derivation item 13.
5. **§4's `LBD-C1` is given the definition of "our top-N" it lacked** (§2 above).
6. **§5's owner stop moves earlier**, and this is the material amendment a reader most needs:
   see below.

**In `plans/2026-09-06-lb-dump-exploration.md`:**

7. **Task 5 is restructured**: `LBD-A0`–`LBD-A3` are derivations of one materialised table,
   not four independent runs (§1). The plan's "hours of wall-clock per arm" holds for the
   pass and for `LBD-A4`, not for the four arms.
8. **Task 7's build config gains `drop_unlistenable=False` on every arm** (`LBD-X3`).
9. **`LBD-G4` is added** before the full pass.
10. **Task 2's fidelity sample is drawn from the pinned snapshot by path** (§2), which Task 4
    already did correctly and Task 2 did not specify at all. `LBDR-F7`.

### The owner stop moves to the end of Task 4

**`LBD-C2a`, the primary supply statistic, answers `LBD-R1` with no emitter, no archive and
no build** — it needs only `T`, the four derivations, and the pinned added-set file. So the
owner stop is **at the end of Task 4**, on the pair-table read, and **Tasks 6 and 7 (the bulk
source, the emitter, the builds) become conditional on his read rather than a precondition of
it.**

Plainly: the question "is ListenBrainz's listening data richer for these artists than what we
currently show" can be answered before we build anything, and building is only worth doing if
the answer is yes. Design §5 placed the stop at the end of `LBD-S3`, after the builds; that
ordering spent the build work to reach a decision the pair table already supports.

**This is a material mid-flight amendment to a committed governing document, and is therefore
a handoff seam** (`CLAUDE.md`). The session committing this document stops here; the next
session reads it cold, which is the condition the amendment was written for.

### ⚠ AMENDED 2026-09-10 by `LBD-AM4` — the build stage: population fixed, arms named, drop lists measured, and a descriptive threshold curve

**Written AFTER Task 4's results existed (`LBD-C2a`, README §6) and BEFORE anything was
emitted or built.** It spends nothing: `LBD-C2b`, `R8` and `R9` have not been read, and this
amendment changes no value of theirs — it fixes *what is built* so that those reads, when
taken, are on a controlled comparison. The owner authorised the build stage at the Task 4
stop on 2026-09-10 (`NEXT.md`'s option 1). Nothing above this block is edited.

**`LBD-AM4-1` — the population is FIXED, and it is the served lineage's own.** *Plain: we
build the arms over exactly the artists the current extended map contains, and no others, so
that the only thing that differs between "the map we have" and "the map our own similarity
would give" is the similarity data.* The set `P` is the node set of `graph-cxa-adopted.bin`
(sha256 `bc0431c4…`, verified against its manifest sidecar 2026-09-10 and read through the
shipped `GraphStore`, the `cxr_added_set.py` precedent) — 88,685 artists, of which the added
29,892 and the pre-existing 58,793 are the pinned files of §3. The emitter writes a payload
only for an artist in `P`, and writes a neighbour row only when **both** endpoints are in
`P`. **The arm's own threshold and rank cut are applied as derived over the full corpus**
(the sha-pinned `A0.parquet` / `A2.parquet` of README §6, never re-ranked inside `P`): the
restriction is a filter at emission, after the cut, so the arm keeps the meaning §1 gives it.
**Why:** every graph-level read carries the population confound `LBD-X2` names and the plan
review measured — a larger population alone moves the supply reading, in the direction that
flatters every arm. Fixing `P` makes each arm differ from the served lineage's bridge control
(the ceiling probe's §4, ceiling 50, same population by construction) in **one column, the
data**, and puts `LBD-C2b` on `CXR-P2`'s own ruler exactly as those bridge arms did. **The
population rule for adoption is an `S4` question and is NOT decided here**: `P` is an
experimental control, chosen because it isolates, not because it is what a shipped map would
contain.

| arm (built) | similarity data | `threshold` | `limit` | population | drop lists | ceiling / top-*j* | isolating baseline |
|---|---|---|---|---|---|---|---|
| ceiling probe §4 bridge control *(context, not built here)* | ListenBrainz's deployed lists (`ALG-B` archive) | LB's 10 | LB's 100 | `P` | served (`20260809` via override) | 50 / 50 | — reproduces `CXR-P2` exactly |
| **`LBD-A0`** | ours, today's corpus, LB's parameters | 10 | 100 | `P` | served, same override | 50 / 50 | the bridge control — **data only** (less `filter_True`, `LBD-X3`) |
| **`LBD-A2`** | ours, today's corpus | **0** | 100 | `P` | served, same override | 50 / 50 | `LBD-A0` — **`threshold` only** |

*Held constant, and why each genuinely is:* `P` — fixed by the emitter, no arm can add to
it; the three drop lists — **measured inert on `P`** (`LBD-AM4-3`), so no arm can change what
they remove; `require_fame=False`, `cap_strategy`, `union_top_j`, `union_degree_ceiling`,
`similarity_rescale`, `similarity_damping` — `BuilderConfig` defaults, identical across the
arms. *Named exposures, still not constant in effect:* **`LBD-X1` stands unchanged** — the
ceiling absorbs more of the supply in the arm that supplies more, and that is exactly what
`R8` reads; and the p99 rescale recomputes per arm but **cannot move a degree read**, because
the cap ranks on unclipped strengths (`pipeline.py`, "Rank the cap on UNCLIPPED strengths")
and with `similarity_damping = 0` those strengths are monotone in the raw score.

**`LBD-AM4-2` — the arms built, in order: `LBD-A0`, then `LBD-A2`.** *Plain: first the
control — our own recomputation at ListenBrainz's settings — then the one arm the pair table
said carries the movement.* **`LBD-A1` is not built**: at the pair-table level it did not
clear `LBD-G2` on the whole set (README §6), and a graph-level figure can only be smaller, so
it cannot inform the build decision; it is not barred, and remains buildable under a later
amendment. **`LBD-A3` is BARRED from building.** *Plain: the "everything, no cut" arm cannot
be turned into a map on this machine and would tell us almost nothing `A2` does not.* Reason,
from README §6's partner-count column: the corner's per-artist partner lists are roughly an
order of magnitude longer than `A2`'s on every stratum (and more than that on the
pre-existing set), so its archive is both directions of every row of `T` (row count owned by
README §5) held as Python neighbour objects in `build_from_archive`'s first pass — far beyond
this machine's memory — while its pair-level movement on the residual stratum is within a
tenth of a point of `A2`'s (README §6). **`LBD-A4` is not run** (it stays deferred with the
condition `NEXT.md` records; no read here depends on it).

**`LBD-AM4-3` — the drop lists: `drop_unlistenable=True` through the shipped override, and
this SUPERSEDES `LBD-X3`'s `False` for the fixed population ONLY.** *Plain: because we build
over exactly the artists the extended map already kept, the filters that shaped that map can
be applied unchanged and remove nobody — which is what "held constant" should mean.*
Measured 2026-09-10 before this was written (`builder/analysis/2026-09-10-lbd-supply/lbd_population_coverage.py`, its JSON beside it;
the figures are recorded here because the amendment turns on them and nowhere else owns them):

| list | censused population covers `P`? | members of `P` it would drop |
|---|---|---|
| `unlistenable_drop_algb_20260809.json` (the re-censused payload, applied via `unlistenable_list_path` exactly as the ceiling probe's §4 bridge arms did) | **yes — 0 of 88,685 uncovered** | **0** |
| `no_release_drop_algb_20260802.json` (`config.algorithm` = `CANDIDATE_ALGORITHM`, default on) | n/a — no guard | **0** |
| `featured_credit_drop_algb_20260803_am1.json` (same key, default on) | n/a — no guard | **0** |
| *for the record:* `unlistenable_drop_algb_20260805.json`, the current DEFAULT | no — 29,837 uncovered; would refuse | 30 |

So every arm builds with `algorithm=CANDIDATE_ALGORITHM`, `drop_unlistenable=True`,
`unlistenable_list_path=…/unlistenable_drop_algb_20260809.json`, and the other two drops at
their defaults — the bridge arms' exact configuration, plus `require_fame=False`. **`LBD-X3`
is not wrong and is not edited**: it describes an arm over the *table's own* population,
where the census guard refuses; over `P` the guard passes and the lists are inert, which is a
property of `P`, not of the arms. An arm ever built over a different population returns to
`LBD-X3`'s `False`. `ULC-F4` is untouched.

**`LBD-AM4-4` — the reads.** `LBD-C2b` is read **exactly as §3 and §9 fix it**: share ≤ 2
over all 29,892 with absent counted as degree 0, versus `LBD-A0`, `LBD-G2`'s 1-point bar
**with both controls** (the pre-existing 58,793 as the within-arm reference, and the arm's
own `LBD-C2a` figure from README §6). `R8` and `R9` are read as written. In addition, and
**descriptively only** (the shape `LBD-AM1` gave `LBD-C2a`): `LBD-C2b` is reported over the
residual stratum and its complement, side by side; no gate is attached to either. **`LBD-M1`
is reported descriptively** — node count per arm against `P`, by the served artifact's fame
band where `fame_lb` is known from the `CXA` metadata and "unknown" otherwise; it decides
nothing and feeds `S4`. And, **for each arm, its added-set figures are set beside `CXR-P2`
and beside the ceiling probe's §4 bridge control**, cited from their owners and never
restated — the bridge control is the row that differs from `LBD-A0` in the data alone.

**`LBD-AM4-5` — a descriptive threshold curve from `T`, with no gate and no effect size.**
*Plain: before the second build, look at how the number of dead ends among the added artists
changes as the strength bar is lowered one notch at a time — so the owner can see whether
"accept every connection however weak" is where the gain is, or whether most of it arrives by
a bar of 2 or 3.* From `T` (sha256 `03d47b05…`, verified 2026-09-10), for the added set, the
residual stratum, its complement and the pre-existing set: the dead-end share (≤ 2 distinct
partners, absent counted as 0), the share absent, and the median partner count, at
`threshold` ∈ {0, 1, 2, 3, 4, 5, 7, 10}, each at `limit` 100 and at no limit — sixteen
derivations, each a pure filter and window over `T` exactly as §1 defines an arm (`rank()`
partitioned on `mbid0`; a row's rank does not change when lower-scored rows are filtered
away, so one ranking serves every threshold). Threshold 10 / limit 100 must reproduce README
§6's `LBD-A0` row and threshold 0 / limit 100 its `LBD-A2` row, which is the instrument's own
green check. **It decides nothing.** It is recorded in README §6c of the Task 4 figures
owner and presented to the owner as **context for whether the second build stays at
threshold 0** — that choice is his, is not made here, and a build at any other threshold
would be a further amendment written before that build.

**`LBD-AM4-6` — no criterion value changes.** `LBD-G1`–`LBD-G4`, `LBD-C1`–`LBD-C3`, `LBD-G2`'s
bars, the 29,892 / 58,793 / 5,967 / 23,925 sets and their shas, and every read in §9 stand
exactly as written. This amendment adds a population control, names which arms are built, and
adds descriptive reporting; it moves no threshold and fires no branch.

**Where the outputs land.** Archives at `C:\unsung-fast\lbd-archives\<arm>\` (the plan's
`D:\unsung-large-data\lbd-archives\` is a spinning disk; the owner's earlier approval of
staging on `C:` is recorded in the 2026-09-10 handoff), each with a `MANIFEST.json`; figures
in `builder/analysis/2026-09-10-lbd-supply/README.md`, the emitter and census scripts beside
it, the threshold-curve script beside the Task 4 scripts it reads with.

**Identifier `LBD-AM4`** (and its sub-items `LBD-AM4-1`–`LBD-AM4-6`). Collision-checked
across every ref 2026-09-10 (`git grep -lE '\bLBD-AM4\b'` over `refs/remotes refs/heads`,
`*.md`): free.


## §11 — Claims check

Grepped and fetched 2026-09-07, in the worktree at `lb-dump-exploration`:

- `CANDIDATE_ALGORITHM` — `builder/src/artistpath_builder/config.py:26`, value read from
  source and reproduced in §0 including its `filter_True` token.
- `drop_unlistenable`, `unlistenable_list_path` — `builder/…/config.py`; `PopulationNotCensused`
  raised in `builder/…/pipeline.py`. Mechanism verified by the claims review, `LBDR-F1`.
- `GraphStore`, `fame_percentiles` — `api/src/artistpath_api/graph_store.py`; both artifacts
  loaded through it by `cxr_added_set.py` and sha-verified against their `.bin.json` sidecars.
- `graph-msw-tu50.bin` sha256 `43dd82bb…`, `graph-cxa-adopted.bin` sha256 `bc0431c4…` — matched
  their manifests 2026-09-07; the added set reproduces `CXR-P2`'s population split exactly,
  which is the validation that the read is being taken correctly.
- `grt-archive-algb.pre-cex-snapshot` — a path under gitignored `builder/scratch/` in the
  **main** tree; **its existence and identity are confirmed at Task 4, before the draw**, and
  this document does not assert it.
- ListenBrainz `listenbrainz_spark/similarity/artist.py` — fetched from master by URL
  2026-09-07, sha256 `7a8516be…`. **Deliberately not vendored**: it is third-party material and
  re-fetching is what makes the check reproducible.
- Track B's `TUw-50-100` / `TUw-50-50` cells and the `CRS-C4` hub-transit bar — read from
  `findings/2026-07-30-track-b-cap-selection-results.md` §1 and the grid in
  `specs/2026-07-30-track-b-cap-selection-preregistration.md`. Figures owned there.

**What this document does not decide.** Whether the `LBD-` track is still the right place to
spend, given that most of today's sparsity is attributable to our own ceiling rather than to
missing listening data — that is the owner's, is recorded as open in the review's findings
document, and blocks nothing here. Adoption (`LBD-S4`), the population rule, API sizing, the
fame source, and any cap-rule or ceiling change are all outside this pre-registration and
each needs its own.


## §12 — Amendments to THIS document, made after it was committed

**§10 records what this document amends in the design and the plan. This section records what
later sessions amend in *this* document.** Every entry is **dated and numbered, and is added
beside the text it qualifies — never as a silent edit to it.** The commit timestamp is what
makes the register worth having, exactly as it is for the document itself.

**The rule that governs every entry here:** a criterion's *values* are never edited. If a
later session finds one inconvenient, the answer is an amendment with its own reasoning and
its own date. That property is the whole point of the document.

---

### `LBD-AM4` — the build stage: population fixed, arms named, drop lists measured, threshold curve

**Dated 2026-09-10. Task 4's results existed when this was written; no build-stage read
(`LBD-C2b`, `R8`, `R9`) did**, so it spends no commit-before-results property. The full text is
the block at the end of **§10**, with pointer notes beside `LBD-X3` (§0) and `LBD-C2b` (§3).
This entry is the register row.

| | |
|---|---|
| **what it adds** | a population control: the arms are emitted and built over exactly the node set of `graph-cxa-adopted.bin` (`LBD-AM4-1`), so each differs from the ceiling probe's §4 bridge control in the data alone; the arm list — `LBD-A0` then `LBD-A2`, `A1` not built, `A3` barred, `A4` not run (`-2`); the drop-list configuration, measured rather than assumed — the re-censused payload covers `P` and all three lists remove nobody from it, so `drop_unlistenable=True` via the override supersedes `LBD-X3`'s `False` **for `P` only** (`-3`); descriptive reporting of `LBD-C2b` by stratum and of `LBD-M1` (`-4`); a descriptive threshold curve from `T` (`-5`) |
| **what it does NOT add** | **no change to any value** (`-6`). `LBD-C2b`'s read and `LBD-G2`'s bars stand; `R8`/`R9` are read as written; no gate is attached to the curve or to the strata |
| **what it must not be read as** | a population rule for adoption — `P` is an experimental control and `S4` is untouched; or a weakening of `LBD-X1` — the ceiling still absorbs supply and `R8` is where that shows; or a threshold decision — the curve is context for the owner |
| **why now** | the owner authorised Tasks 6–7 at the Task 4 stop; the plan's Task 7 as written builds over the table's own population, which the review measured as a confound that flatters every arm, and the ceiling probe had already shown the fixed-population bridge form lands on `CXR-P2`'s ruler |
| **figures** | the coverage counts the amendment turns on are recorded in its own block (nowhere else owns them); every build figure is owned by `builder/analysis/2026-09-10-lbd-supply/README.md`, the curve by the Task 4 README §6c |
| **identifier** | **`LBD-AM4`**, sub-items `LBD-AM4-1`–`-6`. Collision-checked across every ref on 2026-09-10: free |

---

### `LBD-AM3` — `LBD-G1` fired and was overridden by owner decision after diagnosis

**Dated 2026-09-10. A RESULT EXISTED WHEN THIS WAS WRITTEN** — `LBD-C1` had been read and
the gate had fired. **This amendment therefore spends the commit-before-results property of
`LBD-G1`**, and only that; every other criterion, gate and read in this document keeps it.
The full text is the block under §8's gate table. This entry is the register row.

| | |
|---|---|
| **what it adds** | an owner decision: the arms derived from the pinned corpus are read under `LBD-C2a` / `LBD-G2` **despite** `LBD-G1` having fired, because the diagnosis `R1` demanded names the input difference (the deployed dataset's far smaller corpus) and a controlled single-knob rerun with a pre-stated read confirms it |
| **what it does NOT add** | **no change to any value.** The 0.60 floor stands; the 0.5844 reading stands; `LBD-C1` is not re-taken on the dated corpus for the record; `LBD-G2`'s effect sizes and `LBD-C2a`'s definition are untouched |
| **what it must not be read as** | "`LBD-C1` passed" — it fired, was explained, and was overridden. Nor as licence to re-read any other gate after its result |
| **why now** | the alternative (stop at a fired gate with an explained gap) was tabled to the owner beside this one and a third; he chose this, and the read is worthless unless the choice is on the record before the read is taken |
| **figures** | owned by `builder/analysis/2026-09-08-lbd-similarity/README.md` §5, §5a–5c; **none is restated here** beyond the two gate readings the decision turns on |
| **identifier** | **`LBD-AM3`**. Collision-checked across every ref on 2026-09-10 (`git grep -lE '\bLBD-AM3\b'` over `refs/remotes refs/heads`): the only hits are this branch's own analysis README naming it prospectively |

---

### `LBD-AM2` — `LBD-X1`'s "genuinely unmeasured" sentence is qualified, not weakened

**Dated 2026-09-08. NO ARM HAD RUN AT THE TIME THIS WAS WRITTEN** — `LBD-` Task 3 completed
the reimplementation and Task 4 was retired mid-flight with no arm read taken, so the
document's commit-before-results property is intact and this amendment does not spend it.
The full text is the block inside **`LBD-X1`** in §0. This entry is the register row.

| | |
|---|---|
| **what it adds** | a note beside `LBD-X1` recording that its closing sentence — *"The ceiling's effect on them is genuinely unmeasured"* — **was true when written and is no longer true.** `DCF-` measured it; `DFA-` measured the complementary question |
| **what it does NOT add** | **no gate, no effect size, no change to any criterion.** `LBD-X1`'s bar — that a graph-level `LBD-C2` null is barred from supporting `LBD-R1` — **stands unchanged**, because it rests on the ceiling absorbing supply, not on its effect being unmeasured |
| **what it must not be read as** | licence for a ceiling change. Design §9 keeps the cap-rule decision **parked and the owner's**, and Track B's measured cost on famous-pair journeys is untouched |
| **why now** | `NEXT.md` recorded this as owed and assigned it to Task 3. A later reader finding the sentence unqualified would conclude the question is open when two committed probes have answered it |
| **figures** | owned by the two `builder/analysis/` probe READMEs named in the block; **none is restated here** |
| **identifier** | **`LBD-AM2`**. Collision-checked across every ref on 2026-09-08 (`git grep -lE '\bLBD-AM2\b'` over `refs/remotes refs/heads`): free |

---

### `LBD-AM1` — `LBD-C2a` is additionally reported stratified by the residual set

**Dated 2026-09-07. NO ARM HAD RUN AT THE TIME THIS WAS WRITTEN**, so the document's
commit-before-results property is intact and this amendment does not spend it. The full text is
the block at the end of **§3**; the result branch it adds is **`R12`** in §9. This entry is
the register row.

| | |
|---|---|
| **what it adds** | a **reporting requirement**: `LBD-C2a` is reported over two strata — the **residual set** (added artists still at ≤ 2 connections when our own degree ceiling does not bind, `n` = 5,967) and its **complement** (`n` = 23,925) — in addition to the whole-set figure |
| **what it does NOT add** | **no gate and no effect size.** It changes no threshold, triggers no branch, and does not alter the `LBD-C2a` read or `LBD-G2`, which continue to be evaluated over all 29,892 exactly as §3 states |
| **the one named failure mode** | **`R12`** — if `LBD-C2a` clears its bar over the whole set while the residual set does not move, the report must say so **in those words**, and the read is that the loosened settings produce candidate connections but not for the artists this track exists to help |
| **why now** | the residual group is the part of the dead-end problem **no candidate outside this track can touch**, so a whole-set figure mixes it with a group our own cap rule could rescue. Motivated by two probes read before writing, which own the figures behind that sentence |
| **the set's identity** | pinned by path and sha256 in §3's block, written beside the added and pre-existing sets, never re-derived per arm |
| **bound checked, not deferred** | absence would have bounded the whole track and is **not** a bound here; measured before the amendment was written, figures owned by `builder/analysis/2026-09-07-lbd-am1-residual-reachability/README.md` |
| **limits carried** | the residual set is one population under one cap rule, so it is a pinned list and not a claim about any other build; and the candidate fix for the complement is **outside this track**, with the cap-rule decision parked and the owner's per design §9 |
| **identifiers introduced** | **`LBD-AM1`** and **`R12`**. Collision-checked across every ref on 2026-09-07 (`git grep -lE 'LBD-AM[0-9]'` and `'LBD-R1[0-9]'` over `refs/remotes refs/heads`): both free. ⚠ **The branch is `R12`, deliberately NOT `LBD-R12`.** §9's series is bare `R1`–`R11` and this extends it; meanwhile **`LBD-R1` already names the track's central risk hypothesis**, a different object entirely, so an `LBD-R12` beside it would read as its sibling. That is the exact collision shape `CLAUDE.md` records as having cost a session the rule that governed it |
