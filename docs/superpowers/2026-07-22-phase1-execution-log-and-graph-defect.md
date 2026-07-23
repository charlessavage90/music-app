# Phase 1 execution log — and the graph-structure defect that stopped it

**Role: ACTIVE. Written 2026-07-22 at the point work was halted.** This is both the
audit trail for the Phase 1 work done so far **and** the record of a defect discovered in
the **adopted** graph artifact. It is deliberately **one document**: the progress record
must not be picked up without the defect context, or a session will build on facts that
are now known to be unreliable.

**This document owns its figures.** Every number here was measured in this session against
named artifacts. Cite them from here; do not restate them elsewhere (docs/README.md, the
one rule). Nothing here supersedes
`findings/2026-07-21-scoring-adjudication.md` — these are new measurements, not restatements.

---

> ## ⛔ STOP — read §2 before doing any Phase 1 implementation
>
> **Phase 1 (C3 bypass work) is PAUSED, not abandoned.** No shipped code was changed. A
> defect was found in the connectivity structure of the **adopted** graph
> (`graph-t15-capfix.bin`) that calls into question the meaning of the hub/payload metrics
> used throughout this session — and possibly the interpretation of earlier work.
>
> **Do not resume mechanism tuning, and do not treat any "hubfrac"/"payload" figure as
> meaning "famous artists," until the owner has decided how to handle §2.** The decision is
> the owner's and had not been made when this was written.
>
> **Update 2026-07-22 — the mechanism is now determined; the decision still is not.**
> **§2.8** identifies the cause by one-knob intervention, and it is **not** what §2.4
> suspected. Read **§2.8 first**, then §2.2's two correction notices. **§2.4 is overturned
> with its sign inverted — do not act on it.** All four of §2.7's questions remain open.
>
> **Update 2026-07-23 — the decision has been made: repair + retune.** The owner chose the
> repair-then-retune route; the governing design is
> `specs/2026-07-23-defect-remediation-and-cost-retune-design.md`. **Track 1 (the §2.8
> tie-break fix) is complete and the rebuilt artifact is adopted** — identity and
> verification in `findings/2026-07-23-tiebreak-fix-adoption.md`. **Track 2 (the
> cost-function retune) is next.** This document's §2 remains the authoritative record of
> the defect and of the three conflated quantities (degree ≠ fame, popularity ≠ fame,
> raw popularity ≠ percentile) — those warnings are still live.

---

## 1. How to read this document

- **§2 is the blocker.** Facts, discovery mechanism, and — as of 2026-07-22 — the
  determined cause in **§2.8**. Still **no solutions**: §2.8 says what the mechanism is,
  not what to do about it. Read §2.8 before §2.4, which it overturns.
- **§3 is the work record**, start to finish, including two independent ML-analyst reviews
  and what each overturned.
- **§4 is what is closed** and must not be re-argued.
- **§5–§7** are artifacts, current state, and deferred items.

---

## 2. The blocking discovery — the adopted graph's connectivity is inverted

### 2.1 What was found

In `graph-t15-capfix.bin` — the artifact adopted at the end of Phase 2 and the one the app
currently routes on — **the most popular artists are among the *least* connected nodes,
and the highest-degree nodes are insular micro-genre artists.**

### 2.2 The measurements

All from `graph-t15-capfix.bin` (sha256 `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237`)
compared against `graph-t15-control.bin` (same crawl, legacy capping).

> **⚠ CORRECTED 2026-07-22 — neither comparison below isolates one variable.** The
> degree measurements themselves are sound and are unchanged. What is corrected is what
> they can be attributed to. **capfix vs control differs in two knobs**, not one:
> whether reciprocity is required, *and* whether the top-k selection ranks clipped or
> unclipped scores (the deleted `pre_symmetrise` arm truncated before `rescale_scores`
> ran). **capfix vs d025 differs in three.** The isolating one-knob experiment has since
> been run — see **§2.8**, which supersedes §2.4 and identifies the operative knob.

**Degree of the most popular artists, control → capfix:**

| artist | popularity | control degree | **capfix degree** |
|---|---|---|---|
| Radiohead | 1.00 | 11,241 | **ABSENT from graph** |
| The Beatles | 1.00 | 11,113 | **7** |
| Coldplay | 0.98 | 8,427 | **4** |
| Linkin Park | 0.98 | 8,221 | **6** |
| Gorillaz | 0.97 | 7,296 | 11 |
| R.E.M. | 0.96 | 5,529 | **3** |
| Aphex Twin | 0.95 | 5,957 | 30 |
| The Rolling Stones | 0.95 | 4,918 | 10 |
| Michael Jackson | 0.94 | 4,816 | 9 |
| Nine Inch Nails | 0.94 | 4,747 | **5** |
| Pink Floyd | 0.94 | 4,582 | 39 |
| Muse | 0.94 | 4,258 | **4** |
| Red Hot Chili Peppers | 0.94 | 4,210 | 28 |
| System of a Down | 0.94 | 4,101 | 8 |
| Arctic Monkeys | 0.94 | 3,959 | 9 |
| Johnny Cash | 0.94 | 4,237 | 11 |

**Graph shape:**

| graph | N | E (directed) | median degree | p99 degree | max degree |
|---|---|---|---|---|---|
| original `graph-75k.bin` | 74,998 | 4,014,354 | 44 | 357 | 11,050 |
| `graph-t15-control.bin` | 74,991 | 4,101,222 | 49 | 363 | 11,241 |
| `graph-t15-d025.bin` (damping 0.25) | 74,750 | 1,294,810 | 14 | 49 | 50 |
| **`graph-t15-capfix.bin` (ADOPTED)** | **74,191** | **898,314** | **9** | **44** | **50** |

- capfix median degree is **9**; the cap is **50**. So The Beatles (7), Coldplay (4),
  R.E.M. (3), Muse (4) sit **below the median connectivity of the graph**.
- **44%** of capfix nodes have degree < 8.
- The **top-1% degree cutoff is 44 neighbours** (hub set = 952 nodes).

**The top-25 highest-degree nodes in capfix** (all at the cap of 50) are dominated by
lo-fi / synthwave / chiptune micro-genre artists, mixed with a few broad names:

> Leavv, saib., Lazerhawk, David Bowie, Dierks Bentley, Queen, CROOVE, Rogue, Toonorth,
> AC/DC, idealism, 林俊傑, sleepy fish, Stonebank, EGOIST, Miami Nights 1984, Nirvana,
> Metallica, Daft Punk, HM Surf, Kobaryo, Astronaut, Boney James, Purrple Cat, USAO

**`d025` does not show this:** Radiohead 50, The Beatles 50, Coldplay 50, all present and
at the cap.

> **⚠ CORRECTED 2026-07-22 — the original wording of this line said `d025` was "the same
> mutual-kNN capping but with `similarity_damping=0.25`". That is wrong, and it was the
> load-bearing evidence that the effect is capfix-specific.** `d025` differs in **three**
> knobs, not one. It is **not** `p99_log_clip` at all: it carries 642,643 distinct score
> values and **zero** edges at exactly 1.0, which is impossible under the clip, where
> ~1% of edges land at the ceiling by construction. It also **cannot be rebuilt with
> current code** — `rescale_scores` now raises on that combination, since
> `percentile_rank` was deleted at Task 16. **Do not cite `d025` as a witness for
> anything.** §2.8's Arm 2 supersedes it as a genuine one-knob comparison.

**What capfix dropped**, comparing MBID sets against control:

- **800 nodes dropped** (74,991 → 74,191).
- Dropped-node popularity: median **0.465**, mean 0.470 — *below* the graph median of
  0.543. The drops are **not** famous-biased in aggregate.
- Of the **750** top-1%-popularity artists in control, capfix dropped exactly **one**:
  **Radiohead**.

**The Beatles' 7 surviving neighbours**, every one at similarity score exactly **1.000**
(the p99 ceiling): Paul Simon, The Byrds, The Jimi Hendrix Experience, Jefferson Airplane,
George Harrison, The Animals, Chuck Berry.

**Degree and popularity diverge at the top.** Across all 74,191 nodes
Spearman(degree, popularity) = **0.833**, but of the top-1% *most popular* artists in
capfix (742), only **12%** are also top-1% by *degree*. Concretely, against the 44-degree
hub cutoff:

| artist | degree (percentile) | popularity (percentile) | counted as a "hub"? |
|---|---|---|---|
| Kylie Minogue | 31 (92.1%) | 0.68 (99.0%) | no |
| Whitney Houston | 30 (91.2%) | 0.51 (91.9%) | no |
| Prince | 31 (92.1%) | 0.56 (95.4%) | no |
| Paul Simon | 34 (94.3%) | 0.52 (92.9%) | no |
| The Beatles | 7 (40.3%) | 1.00 (100%) | no |
| The Shins | 46 (99.2%) | 0.78 (99.7%) | **yes** |
| Aerosmith | 50 (99.9%) | 0.72 | **yes** |

**Incidental data-quality note:** duplicate artist names with distinct MBIDs exist —
"Nirvana" appears twice in capfix (degree 50 / popularity 0.88, and degree 4 / popularity
0.26). This was noticed while checking the above and has not been investigated.

### 2.3 Discovery mechanism — how this surfaced

This matters, because **nothing in the automated apparatus caught it.** All 209 tests pass.
It was not found by code review, by the Phase 2 six-arm sweep, or by either ML-analyst
review. The chain was:

1. A **blind listening test** (§3.8) produced a verdict, alongside hidden per-path metrics.
2. The owner **questioned a metric against his own perception**: a path reported as
   `hubfrac = 0.0` ("no hubs") contained Kylie Minogue, Whitney Houston, Prince and Paul
   Simon, which he would have called hubs.
3. Checking those four artists showed they sit **below the degree-based hub cutoff but in
   the 92nd–99th popularity percentile** — degree and fame diverge.
4. The same check incidentally showed **The Beatles at degree 7**, and **"Radiohead" not
   found in the graph at all**. The owner recognised the significance — "everything is
   Radiohead" was the founding name for the hub problem this project set out to fix.
5. A **cross-artifact comparison** (capfix vs control vs d025 vs original) established the
   effect is specific to capfix and absent from d025.

**The generalisable point:** the defect was found by a human comparing a metric's output to
his own perception of the artists in the result. No structural test asserts that famous
artists remain well-connected, and none of the offline metrics would have revealed it.

### 2.4 Suspected root cause — ⛔ OVERTURNED 2026-07-22, WITH THE SIGN INVERTED

> **This section was wrong. It is retained so the reasoning can be audited; do not act on
> it and do not restate it. §2.8 replaces it with a measured mechanism.**
>
> The suspicion below claims famous artists' lists go **unreciprocated**. Measured, they
> are **the most reciprocated in the graph** — 0.959 for the top 25 by popularity against
> a graph-wide per-node median of 0.511, declining monotonically as artists get more
> obscure. The mechanism is real and it is not the cause of the inversion: it explains the
> graph's *overall* degree level, and it is identical in both arms of §2.8's experiment.
>
> It survived because it is consistent with every measurement in §2.2, and consistency
> was all that was ever checked. **That is the lesson worth carrying: "consistent with
> every observation" is not a cause.** Two mechanisms were consistent with the same
> evidence and only intervention separated them.

*Original text, retained for audit:*

Mutual k-NN keeps an edge only if **each endpoint ranks the other in its top-k**. A broad,
famous artist is listed by thousands of others, but its own top-k list is short and
specific, so most of those inbound edges are **not reciprocated** and are pruned. A tight,
mutually-referential micro-genre cluster (lo-fi, synthwave) has near-total reciprocity, so
it keeps essentially all of its edges and lands at the cap.

The result is that the reciprocity rule prunes **broad famous artists hardest and insular
clusters not at all**. This is consistent with every measurement in §2.2 and with `d025`
behaving differently (damping changes the scores, hence the top-k rankings, hence which
edges are mutual). **It has not been verified beyond that consistency, and no deeper
investigation was performed.**

*(Two further errors in the passage above, for completeness: inbound edges do not exist
when the cap runs — `symmetrise` runs one line later, at `pipeline.py:219` — so nothing
inbound is pruned. And the `d025` clause rests on the mischaracterisation corrected in
§2.2.)*

### 2.5 What cuts against alarm — required context

A session reading only §2.1–2.4 would over-correct. All of the following are also true:

- **`capfix` won a blind listening test** in Phase 2 and was adopted by the owner on that
  basis. It won a second, informal comparison earlier in Phase 2.
- **The drops are not famous-biased.** 799 of the 800 dropped artists are middling
  popularity. Radiohead is a single dramatic exception, not a pattern.
- **No path has been shown to be worse *because* of this structure.** The link between the
  degree collapse and the path-quality problems observed in §3 is **unproven inference**.
- This is **information that was not available when the adoption decision was made** — it
  is not evidence that the decision was wrong.

### 2.6 What this calls into question (facts only)

- **The degree-based hub metric does not mean "famous."** `hubfrac`, the "payload" count
  (non-hub interior artists), `hub_penalty`, and the dormant `w_hub` weight are all built
  on top-1%-by-degree. Post-capfix that set is largely insular micro-genre artists. Every
  hub/payload figure in this document and in this session's analysis therefore means
  "non-insular-cluster-member," **not** "not famous."
- The founding complaint is phrased in terms of **popularity** ("rerolls return artists at
  the same popularity band"), and the owner's perception tracks **fame**. The measurement
  apparatus tracks **degree**. These were assumed equivalent and are not.
- Whether any earlier conclusion rests on that conflation has **not** been audited.

### 2.7 Open questions (deliberately not answered here)

- Does the degree collapse of famous artists cause the coherence problems observed in §3.8?
- Should hub/novelty measurement be popularity-based rather than degree-based?
- Is Radiohead's absence a defect to correct, and are there other absences like it?
- Does any of this change the Phase 2 adoption decision?

**No solution is proposed in this document, by instruction.** §2.8 determines the
*mechanism*; it does not answer any of the four questions above, all of which remain the
owner's.

### 2.8 The mechanism, determined by intervention (2026-07-22)

Run by `ml-graph-analyst` in two checkpointed parts, briefed with two candidate mechanisms
given unranked and a mandatory third "neither" slot, and required to pre-register the
discriminating measurement before running it.

**The experiment.** A replay of the build from the archive up to `pipeline.py:218`,
branching on **exactly one knob**: whether the top-k selection inside `mutual_knn_cap`
ranks **clipped** or **unclipped** scores. Same archive, same damping, same p99 (computed
once over the full uncapped array, so emitted scores are identical between arms), same k,
same tie-break code, same `symmetrise`, same `largest_component`.

**Arm 1 reproduced `capfix` exactly** — N, E, MBID set, and every per-artist degree. That
is what makes Arm 2 interpretable.

| | Arm 1 (= capfix, clipped ranking) | Arm 2 (unclipped ranking) |
|---|---|---|
| Radiohead | **isolated singleton, 0 edges** | **degree 50, in the LCC** |
| The Beatles | 7 | 50 |
| Coldplay | 4 | 50 |
| R.E.M. | 3 | 47 |
| median degree, popularity rank 1–10 | 6.5 | 47.5 |
| median degree, rank 11–25 | 10 | 44 |
| median degree, rank 101–250 | 27 | 31 |
| **median degree, whole graph** | **9** | **9** |
| **frac of nodes with degree < 8** | **0.449** | **0.449** |
| N / E | 74,191 / 898,314 | 74,193 / 898,006 |

**The global shape does not move.** Two nodes and 308 edges differ, out of 74k and 898k.
The inversion is entirely a top-of-distribution artefact.

**Why it binds only at the top.** `p99_log_clip` collapses the top 1% of raw scores into a
single value, so a node whose ceiling pool exceeds k has a top-k that is decided entirely
by the tie-break — `sorted(..., key=lambda pair: (-pair[1], pair[0]))` at `graph.py:76-78`,
i.e. **the k lowest destination MBIDs**. Source out-lists are hard-capped at 100 upstream.
Only **285 nodes of 74,993 (0.4%)** have a ceiling pool above 50 — but 25 of the top 26 by
popularity are **fully saturated**, all 100 entries tied. Among those 285, degree
correlates with MBID rank at Spearman **−0.722**; among everyone else, **+0.105**, which is
the graph-wide baseline, i.e. nothing.

**Radiohead's terminal state:** zero surviving mutual edges, component size 1, removed by
`largest_component`. Every one of its 50 selected partners is itself ceiling-saturated, so
it had no exempt channel at all.

**The reciprocity measurement that falsified §2.4:** fraction of pre-cap directed edges
reciprocated is **0.4366** graph-wide, per-node median **0.511**; by popularity band,
rank 1–25 → **0.959**, 26–100 → 0.852, 101–1,000 → 0.731, 1,001–10,000 → 0.634.

**In plain language.** The similarity scores are counts, and the scoring step squashes the
top 1% of them down to one identical value. Each artist then keeps its 50 best neighbours
out of the 100 the data source gave it. For an ordinary artist that is a real choice. For a
very famous artist *every* neighbour is in that squashed top 1%, so they are all tied, and
the code falls back on keeping whichever 50 have the earliest-sorting random identifier.
The neighbour has to make the same arbitrary choice back, and both have to agree — usually
they do not. Radiohead's never agreed, so it connected to nothing and was deleted.

**One finding recorded as measured-but-unverified.** In the archived source data, edge
destinations skew monotonically toward high-hex MBIDs (first-hex share 0.0248 at `0` rising
to 0.1125 at `f`, against a uniform crawled population), and famous artists average MBID
percentile 0.772. If real, a tie-break keeping the *lowest* MBIDs is systematically
anti-famous rather than merely arbitrary, and amplifies the effect roughly 3×. **This has
no proposed mechanism and has not been independently checked. Verify before citing it.**
Nothing above depends on it: Arm 2 recovers the graph regardless of *why* famous artists
lose the coin toss.

**What this does not fix.** Arm 2 still emits clipped scores. The p99 ceiling defect
survives untouched — including §3.7's near-zero-cost hub expressway and the flattened
transition signal. This accounts for **one of that defect's consequences**, not the defect.

**What remains the owner's call, and is not decided here.** `capfix` was adopted on two
blind listening tests, and §12 of the Phase 2 log attributes the win to removing hubs'
ability to act as universal shortcuts — which is the same mechanism, in its extreme form.
Whether Arm 2 is *better to listen to* is unmeasured and is a product question, not a graph
question. Note also that §15–17 forbid a third listening test; whether that bars a listen of
a **new** candidate on a **new** finding is a reading the owner should make deliberately.

### 2.9 The larger finding — mutual k-NN depletes famous→obscure edges (2026-07-23)

> **⚠ VALIDATED AND PARTLY CORRECTED — read §2.10 first.** This section was written by an
> outside consulting session and put to `ml-graph-analyst` for validation. The result:
> **the core finding is upheld and strengthened; the framing below is wrong, and two of its
> figures were measuring the wrong thing.** Specifically — the "before" graphs were **never**
> disassortative in any useful sense (control sits at *exactly chance* against its own
> degree-sequence null), so "mutual k-NN destroyed a property discovery needs" is not
> supported. What is supported is one-sided and stronger: capfix **actively depletes** those
> edges, 15.6× below a structure-preserving null. §2.10 owns the corrected figures.
>
> The original heading read "…inverted the graph's popularity assortativity". Retained
> below for audit; **do not cite this section's numbers — cite §2.10.**
>
> **⚠ SECOND CORRECTION — §2.12.** This section measures in **percentile** units while the
> `known` gate and `w_jump` operate in **raw popularity**, and the two diverge sharply at
> the top of the distribution. Its claim that *"no cost function can route to an obscure
> artist along edges that do not exist"* is **fully retracted** — obscure artists are 2–3
> hops from every famous artist tested, and even The Beatles have 7 admissible `known`
> substitutes. **This is a cost-function problem, not a graph-structure problem.**

**This supersedes §2.8 in importance.** §2.8's tie-break defect is real and explains
Radiohead and The Beatles. It is **not** the reason the product does not surface obscure
artists. This is.

#### What was measured

Prompted by the owner's repeated note that *every* artist in the blind listen felt
well-known, the interior artists of all 36 judged paths were scored against the graph's own
popularity distribution.

**Every interior artist in all 36 paths sits above the 90th popularity percentile.** 100%,
in every arm, at every bypass depth. The least popular artist offered anywhere in the test
was **Whitney Houston, 91.9th percentile**; 57% of the 102 distinct interior artists are
above the **99th**. Pooled mean percentile by depth: d5 **0.982** → d20 **0.978**. On the
shipped mechanism it moves the wrong way (0.992 → 0.994). Not an endpoint artifact — the
deliberate "pop-obscure" pair ends at Wishbone Ash (87.6th percentile) and its interiors run
0.992–0.994, i.e. the path routes **above its own destination** and never dips.

#### The pre-registered follow-up, and its null

Predicted before running: if removing the p99 ceiling opened the obscure tail, `rankfix`
would reach lower. **It does not.** Same 3 pairs, shipped router, 20 bypasses, two victim
policies (highest `hub_penalty`, and most-popular-interior):

| graph | policy | d0 | d5 | d10 | d15 | d20 |
|---|---|---|---|---|---|---|
| capfix | hub_penalty | 0.995/0.981 | 0.993/0.981 | 0.994/0.981 | 0.994/0.981 | 0.995/0.981 |
| capfix | most-popular | 0.995/0.981 | 0.995/0.981 | 0.992/0.982 | 0.994/0.981 | 0.991/0.965 |
| rankfix | hub_penalty | 0.995/0.990 | 0.997/0.982 | 0.991/0.957 | 0.997/0.991 | 0.996/0.988 |
| rankfix | most-popular | 0.995/0.990 | 0.988/0.950 | 0.997/0.982 | 0.990/0.950 | 0.991/0.957 |

*(mean / lowest single interior percentile.)* **Flat everywhere.** Twenty bypasses, either
graph, either policy, never below the 95th percentile.

#### The cause — and it is the adopted cap strategy

| artifact | popularity assortativity | neighbours of top-500 below p90 | below p50 |
|---|---|---|---|
| `graph-75k.bin` (original) | **−0.290** | **83.0 %** | 39.5 % |
| `graph-t15-control.bin` | **−0.262** | **82.3 %** | 35.3 % |
| `graph-t15-d050.bin` | ~~+0.380~~ → **+0.468** | ~~18.4 %~~ → **7.8 %** | ~~1.7 %~~ |
| **`graph-t15-capfix.bin` (ADOPTED)** | **+0.597** | **5.2 %** | 0.5 % |
| `graph-t15-rankfix.bin` | ~~+0.658~~ → **+0.596** | ~~3.5 %~~ → **3.9 %** | ~~0.3 %~~ |

> **⚠ Two rows above were wrong and are struck.** Under a fixed popularity reference,
> **capfix and rankfix are identical (+0.596 vs +0.596), not 0.06 apart** — the difference
> was the rescale changing the *popularity vector*, not the graph. `d050` is +0.468 / 7.8 %.
> Corrected values in §2.10.

**Mutual k-NN inverted the sign.** Before it, the graph was *disassortative* — famous
artists were connected mostly to obscure ones, which is exactly the structure a "journey to
somewhere you haven't heard" needs. After it, famous artists are connected almost only to
each other. **No cost function can route to an obscure artist along edges that do not
exist.**

> **⚠ THE PARAGRAPH ABOVE IS OVERTURNED. Both sentences.**
>
> *"Before it, the graph was disassortative"* — **no.** That figure is edge-weighted, so a
> handful of nodes carrying 11,000–15,000 edges each supplied most of the endpoint pairs.
> Node-weighted, the "before" graphs are **positive**: +0.250 uncapped, +0.185 control,
> +0.186 original. And against its own degree-sequence null, control sends 81.3 % of
> top-500 edges below p90 versus a null of 80.4 % — **ratio 1.01, exactly chance.** The old
> graph was not steering famous artists toward obscure ones; it was connected to everything,
> and most artists are obscure.
>
> *"No cost function can route along edges that do not exist"* — **too strong.** A p95–p99
> artist has a **median of 4** sub-p90 neighbours out of 28, and only 12.6 % have none. It
> is an *existence* problem only at the extreme top (63.5 % of the top 0.1 % have zero
> exits) and a **competition** problem across the band the judged paths actually occupied.
> See §2.10.

The mechanism is the reciprocity rule, and it is **§2.4's candidate A, vindicated for a
different quantity than it was tested on.** Obscure artists list famous ones; famous ones do
not list back. Those edges are unreciprocated and pruned. §2.4 was correctly *falsified* as
the cause of the **degree collapse** (§2.8 proved that is the tie-break) — but the asymmetry
it described is real and produces the stratification. Two mechanisms, two different symptoms;
overturning A for the first does not clear it for the second.

#### What this does and does not establish

- **Does not overturn the `capfix` adoption.** `control` is disassortative but carries
  degree-11,241 hubs, and the owner preferred `capfix` blind, twice. Both things are true:
  `capfix` removed the hub expressway *and* severed the route to obscurity. That is
  precisely the owner's own summary of the Task 0 test — **improvement, not goodness.**
- **Does not test a fix.** Whether a cap strategy exists that bounds degree *without*
  inverting assortativity is **unmeasured**. `d050` sitting at +0.380 with 18.4 % is a
  datapoint, not a recommendation; the damping arms were rejected on other grounds and
  `d050` was never listened to.
- **The link from assortativity to path behaviour is inference**, though the tail probe
  measured the path behaviour directly on both graphs and found it flat on each.
- **Thin evidence base for the path measurements:** 3 pairs, 102 distinct artists. The
  assortativity figures are whole-artifact and not thin.

#### Consequences for the paused work

- **The A-vs-C mechanism question (§3.8) was decided on a substrate where no mechanism
  reached below the 92nd percentile.** On the axis the owner cares about, the three arms are
  indistinguishable. The bypass mechanism was never the binding constraint.
- **§2.7's first open question is answered in one direction:** the *degree collapse* is not
  what causes the coherence problems. Whether the *stratification* does is now the live
  question.
- **§17's carried success condition — "a hub-incidence-versus-bypass-count measurement
  exists" — is now satisfied.** The channel is flat, on both graphs.
- A `capfix` vs `rankfix` blind listen is **not** the next step. ~~They differ by 0.06 in
  assortativity~~ — **corrected: they are identical, +0.596 vs +0.596** — and behave
  identically on the tail. *(The conclusion is strengthened, not weakened, by the
  correction.)*

**Scripts:** `builder/analysis/2026-07-23-popularity-stratification/`.

---

### 2.10 Validation of §2.9 — what survived, what was overturned (2026-07-23)

`ml-graph-analyst`, briefed that §2.9 was an unverified outside claim and that overturning it
was the useful outcome. Checkpointed; Part 2 not run. **This section owns the corrected
figures — cite from here, not from §2.9.**

#### The circularity confound was real, and asymmetric in the opposite direction to the worry

Popularity is score-weighted in-degree, so §2.9 compared arms using each arm's own
definition of "popular." Corrected by fixing a single reference — **pre-cap in-degree**,
which `pipeline.py:206-217` computes one line *before* `mutual_knn_cap` at `:218`, i.e. the
last point before any arm diverges.

The contamination turned out to sit entirely on the **baseline** side. capfix's shipped
popularity is Spearman **1.000000** against the fixed reference — never contaminated,
because the pipeline computes in-degree pre-cap. Control's is **0.9737**, because the legacy
`pre_symmetrise` strategy truncated out-lists *before* the in-degree sum.

**93–95 % of the claimed movement survives**, and the sign change survives under three
independent references (clipped in-degree, raw edge count, raw co-occurrence): Δ control→capfix
of **0.815 / 0.803 / 0.800** against 0.859 claimed. Split-halves reproduce within 0.008;
bootstrap SD ≤ 0.0009.

#### The real finding, with the null §2.9 omitted

| | observed | own-degree-sequence null | ratio |
|---|---|---|---|
| control | 81.3 % | 80.4 % | **1.01 — chance** |
| **capfix** | **5.1 %** | 79.9 % | **0.064 — 15.6× depleted** |

**capfix does not merely lack famous→obscure edges; it actively avoids them.** Density alone
explains none of it — uniform pruning to capfix's edge count leaves 80.3 % (two seeds), and
score-greedy pruning to the same density leaves 36.6 % while shattering the graph.

#### Attribution — 2×2 factorial, one knob per axis

| | score-ranked top-k | random-k (3 seeds) |
|---|---|---|
| **AND (mutual)** | **+0.596** | +0.499 / +0.500 / +0.499 |
| **OR (union)** | −0.219 | −0.212 |

Reciprocity knob **+0.815**; ranking knob +0.097; density −0.007. The `MUTUAL_TOPK` arm
reproduces capfix exactly (74,191 / 898,314), which is what makes the rest interpretable.

**§2.4's candidate A is legitimately revived for this quantity** — it now has the one-knob
intervention it never had. It remains falsified for the degree collapse (§2.8).

#### §2.8's tie-break is not this

| arm | assortativity | top-500 exits below p90 |
|---|---|---|
| ranking on clipped scores (= capfix) | +0.596 | 5.1 % |
| ranking on unclipped scores (= §2.8 Arm 2, restores Radiohead) | **+0.596** | **3.9 %** |

Fixing §2.8 changes stratification by nothing, and makes the exit rate marginally worse.

#### Existence vs competition — where the constraint actually binds

| popularity band | n | median degree | median exits below p90 | % with **zero** exits |
|---|---|---|---|---|
| top 0.1 % | 74 | 17 | 0 | **63.5 %** |
| p99–p99.9 | 675 | 28 | 1 | 38.8 % |
| p95–p99 | 2,999 | 28 | **4** | 12.6 % |
| p90–p95 | 3,749 | 25 | 10 | 4.5 % |

Control, for contrast: **0.0 %** of nodes above p50 have zero sub-p90 exits, and its top
0.1 % has a median of **2,170**.

**So it is an existence problem only at the extreme top, and a competition problem across
the band the judged paths occupied** — roughly 4 exits against ~24 same-band alternatives,
under a cost function charging `w_jump·|Δpop|` to use them. This materially reopens the
cost-function route, which §2.9 dismissed.

#### The coupling — raised unprompted, and it is the trade everything turns on

**Anything that restores disassortativity restores unbounded degree.** `UNION_TOPK` is the
proof: identical k=50 cap, no reciprocity test, **max degree 11,153**. In this codebase the
degree bound is an *effect* of the reciprocity requirement (`graph.py:57-74`), not a separate
knob.

Separating them requires a `cap_strategy` **that does not exist**: symmetric degree-quota
selection, score-ranked, no reciprocity test — one branch in `mutual_knn_cap`. `d050` cannot
substitute (two knobs: damping 0.5 *and* `percentile_rank`).

Unbounded hubs are what `capfix` won its blind listen for removing, and the top-1 %-by-degree
hub set behind `hubfrac`, `hub_penalty` and `payload` would move again.

#### Weakest link, as stated by the analyst

The degree-sequence null is a randomised greedy b-matching, not an exact configuration-model
sample — 3.9 % of control's quota and 7.7 % of capfix's went unmet. Two seeds agree to three
decimals and achieved max degree is exactly 50. **An exact rewiring is the stronger
instrument if anyone leans hard on the 15.6×.**

**Not measured by any of this:** whether stratification changes what the owner prefers.
`capfix` won two blind listens carrying this structure.

**Scripts:** `builder/analysis/2026-07-23-popularity-stratification/validation/`.

> **Before using the exits table above, read §2.11.** It establishes who the zero-exit
> nodes actually are, and why the p90 threshold that defines an "exit" is a **gameable**
> success criterion for any experiment that tries to fix this.

---

### 2.11 Who has zero exits — and a third conflation (2026-07-23)

Prompted by the owner asking whether §2.10's zero-exit nodes are the lo-fi/chiptune
cap-set artists or the Beatles-like ones. **The question has a false premise, and that is
the finding: they are the same population.**

#### The "micro-genre" artists are popular artists

| artist | degree | **popularity percentile** | sub-p90 exits |
|---|---|---|---|
| Stonebank | 50 | **0.991** | 1 |
| USAO | 50 | **0.988** | 5 |
| saib. | 50 | **0.986** | **0** |
| Lazerhawk | 50 | **0.986** | 1 |
| Miami Nights 1984 | 50 | **0.982** | 1 |
| idealism | 50 | **0.977** | 1 |
| Purrple Cat | 50 | **0.966** | **0** |
| CROOVE | 50 | 0.850 | **47** |

§2.2 describes the top-25 by degree as "insular micro-genre artists," set against the
famous ones. **Right about insularity, wrong about obscurity.** Popularity here is
score-weighted co-listening, and lo-fi/synthwave artists are playlist staples, so they
accumulate very high in-degree. They sit in the top 1–3 % by popularity, alongside The
Beatles. CROOVE is the sole genuine outlier — below p90 itself, and the only one with a
large exit count.

#### Zero exits is a popularity property, not a degree property

| popularity band | deg ≥45 | deg 20–44 | deg <20 |
|---|---|---|---|
| top 0.1 % | **75.0 %** (n=8) | 44.0 % (n=25) | **73.8 %** (n=42) |
| p99–99.9 | 49.3 % (n=71) | 33.5 % (n=409) | 44.4 % (n=187) |
| p95–99 | 25.3 % (n=293) | 9.7 % (n=1,914) | 14.5 % (n=761) |
| p90–95 | 6.6 % (n=167) | 2.3 % (n=2,281) | 8.1 % (n=1,262) |
| p50–90 | 0.0 % (n=195) | 0.0 % (n=10,570) | 1.5 % (n=18,911) |
| below p50 | — | — | 0.8 % (n=37,095) |

It rises monotonically with popularity inside **every** degree band and effectively
vanishes below p90. **The graph is structurally normal everywhere except its top decile**,
which is a single sealed stratum containing both Metallica and saib.

**Two routes into it**, which is why the top row is U-shaped in degree — and this explains
a number §2.10 left unexplained:

- **Too few edges to have any obscure ones** — the §2.8 tie-break victims. The Beatles
  (deg 7, 0 exits), Coldplay (deg 4, 0 exits).
- **All 50 slots consumed by same-band peers** — the saturated ones. Metallica (deg 50,
  0 exits), The Shins (deg 46, 0 exits).

Different mechanisms, identical outcome. **This is why fixing §2.8 moves the exit rate only
5.1 % → 3.9 %:** it repairs the first route and does nothing about the second.

#### The third conflation — and it threatens the success criterion, not just the vocabulary

The record has established **degree ≠ fame** (§2.6). This establishes **popularity ≠ fame**
as well, at the top of the distribution, where a lo-fi producer and a Beatle score alike.

For the judged paths it did not matter — Nina Simone, Aretha Franklin, Madonna and Bob Dylan
are genuinely famous, so metric and ear agreed, and §2.9's tail finding is **not** weakened.

**What it does threaten is any future experiment scored on "reaches below p90."** That
criterion is gameable: a cost-function change could satisfy it by routing from Metallica into
synthwave — a large popularity drop by the metric, and plausibly indistinguishable from the
current behaviour to the listener. **Any attempt to fix the stratification needs a success
criterion sharper than a popularity percentile** — decided artists, or a fame proxy that is
not in-degree.

**Labelled as inference, not measurement:** that saib. and Purrple Cat would not *feel*
well-known to the owner is inferred from genre, not from any recorded verdict. He has never
been shown one. If that inference is wrong, the gameability concern weakens — but the
structural finding above does not depend on it.

**Scripts:** `builder/analysis/2026-07-23-popularity-stratification/exits_by_band.py`.

> **⚠ The "exits" measure above is in PERCENTILE units. §2.12 shows that is the wrong
> currency for the mechanism, and corrects the conclusions drawn from it.**

---

### 2.12 The currency error — and why this is a cost-function problem, not a graph problem (2026-07-23)

Prompted by the owner pushing on whether zero-exit artists are underserved, given that
famous artists are the most likely path endpoints and the most likely `known` targets.
**The answer reverses the direction of §2.9–§2.11.**

#### `known` is satisfiable — and most satisfiable for exactly the famous artists

Per §3.4's specification (route to an artist *highly similar to K but more obscure*) and
§3.10's gates (pop drop ≥ 0.10; similarity ≥ 0.70 for the waypoint form):

| popularity band | n | % with **zero** admissible substitutes | median # | % zero **with** sim gate |
|---|---|---|---|---|
| **top 0.1 %** | 75 | **0.0 %** | **17** | 0.0 % |
| p99–99.9 | 667 | 0.3 % | 12 | 0.3 % |
| p95–99 | 2,968 | 11.6 % | 5 | 23.0 % |
| p90–95 | 3,710 | 23.9 % | 3 | 70.2 % |
| p75–90 | 11,128 | 29.6 % | 2 | 92.9 % |
| p50–75 | 18,548 | 42.8 % | 1 | 98.8 % |
| **below p50** | 37,095 | **88.7 %** | **0** | 100.0 % |

The Beatles have **7 of 7** neighbours admissible; Metallica 32, Bob Dylan 34, Pink Floyd 30.
**The mechanism is unsatisfiable for obscure artists, not famous ones.** The similarity gate
is what bites in the middle bands, not availability.

#### But it satisfies its gate and returns a famous artist

The Beatles' best substitute is **Paul Simon** — raw popularity **1.00 → 0.52**, clearing the
0.10 gate by nearly 5×, and still at the **92.9th percentile**.

**The cause is that the two currencies diverge at the top.** Raw popularity: median 0.302,
p90 **0.495**, p99 0.677, max 1.00. So the top decile spans *half the entire raw range*, and
a 0.10 raw drop from a superstar lands comfortably inside the famous stratum.

> **This corrects §2.9, §2.10 and §2.11.** All three measure "exits" and stratification in
> **percentile** units. The `known` gate and the `w_jump` cost term operate in **raw
> popularity**. The two were never reconciled, and they disagree precisely where the product
> operates. The structural measurements in those sections are arithmetically correct; the
> **conclusions drawn from them about mechanism viability are not.**

#### The obscure region is 2–3 hops away, not absent

| from | → p90 | → p75 | → p50 |
|---|---|---|---|
| The Beatles | 2 | 2 | **3** |
| Metallica | 2 | 2 | **2** |
| The Shins | 2 | 2 | **2** |
| Pink Floyd | 2 | 2 | **2** |
| Taylor Swift | 1 | 2 | **2** |

**§2.9's "no cost function can route to an obscure artist along edges that do not exist" is
fully retracted**, and §2.10's softened "competition problem" still understates the
proximity.

#### What this makes the problem

**A cost-function problem.** Beatles → Paul Simon costs `w_jump·|Δpop| = 1 × 0.48 ≈ 0.48`;
remaining in the stratum costs ≈ `w_hop` = 0.02 per hop. **One dive costs twenty-four hops'
worth of `w_hop`.** The router is not failing to find exits — it is correctly pricing them as
expensive and declining.

**`w_floor` being inert (§3.3) is a symptom of this, not a separate defect.** It was the term
designed to counteract exactly this pressure. It never fires because `floor =
min(pop_source, pop_target)` and `w_jump` prevents paths from dipping below the floor in the
first place. One defect, two faces.

#### Consequences

- **The stratification work does not motivate a builder redesign on its own.** The new
  `cap_strategy` of §2.10 remains an open design question, but it is **no longer the
  cheapest or most likely fix** and should not be built on the strength of §2.9–§2.11.
- **A cost-function experiment needs three knobs, not two:** `w_jump`, `w_sim`, **and the
  currency of the `known` gate**. A gate expressed as a raw drop cannot express "less
  famous" at the top of this distribution; a percentile-based or rank-based gate can.
- **§2.11's gameability warning survives and sharpens.** Any success criterion must be
  robust to *both* currency errors — raw drops that stay famous, and percentile drops that
  land in insular high-popularity genres.

#### Calibration note for a future reader

§2.9 through §2.12 were produced by an **outside consulting session** over a single day, and
§2.9's central framing has now been corrected **twice** — once by `ml-graph-analyst` (§2.10)
and once by the owner's own question (this section). The underlying measurements have held
each time; the **interpretations** have not. Treat any conclusion in this range as load-tested
only where a later section explicitly re-affirms it.

**Scripts:** `builder/analysis/2026-07-23-popularity-stratification/known_viability.py`.

---

### 2.13 Decisions, reversals, and what a fresh session needs (closeout A1/A2, 2026-07-23)

#### Decisions taken, with reasoning

| # | Decision | Reasoning |
|---|---|---|
| C1 | §2.8–§2.12 were produced by a **consulting session held deliberately away from the code**, so its inputs differed from the working session's | Disagreement between two readers is only informative if their inputs differ; a second reader who has acquired the first's information produces correlated errors that look like confirmation. The constraint was relaxed only when the owner asked for measurements. |
| C2 | Used the existing **`rankfix` artifact** as the ceiling-removal comparison rather than building §2.8's Arm 2 | Their topology is identical (74,193 / 898,006). Building a second copy of an artifact already on disk would have cost a rebuild and proved nothing. |
| C3 | Put §2.9 to `ml-graph-analyst` **after** committing it, rather than trusting it | A claim about the graph was entering the record, and the decision it pointed at — redesigning `cap_strategy` — is expensive builder work. It came back partly overturned. |
| C4 | **Correction notices** over rewriting, but wrong *figures* struck inline | The doc-map rule is to mark superseded claims inline so a mid-document reader sees them. But this document declares it owns its figures, so a wrong number is worse than a wrong sentence — those are struck at the point of use. |
| C5 | **Measured before listening**, with the reading pre-registered | A `capfix`-vs-`rankfix` listen was the obvious next step and would have burned the owner's ear on a null. The pre-registration is what made the null actionable rather than disappointing. |
| C6 | Did **not** recommend building the new `cap_strategy` | §2.12 removed its motivation before anyone started. Deferred, not killed (§7.1). |

#### Reversals — three, all of this session's own conclusions

Recorded because the pattern matters more than any one of them: **the measurements held every
time; the interpretations did not.**

1. *"Blind-listen `capfix` vs `rankfix` next"* → withdrawn. They are identical at +0.596.
2. *"The p99 ceiling defect is primary, the degree inversion is its symptom"* → reversed. The
   stratification is caused by reciprocity; fixing the ceiling changes it by nothing.
3. *"The graph is the binding constraint, not the cost function"* → **reversed** (§2.12).
   Obscure artists are 2–3 hops away and the router declines them on price.

#### What a fresh session needs that is not obvious from the sections above

- **The analyst's Part 2 was never run.** It is gated on a `cap_strategy` branch that does
  not exist (symmetric degree-quota selection, score-ranked, no reciprocity test). Do not
  dispatch it expecting an answer; it needs a code change first.
- **The C3 A-vs-C mechanism question is moot until the cost function is settled** (§2.9
  consequences). Both prototypes were tuned on a substrate where no mechanism reached below
  the 92nd percentile.
- **The next experiment is a three-knob cost-function sweep** — `w_jump`, `w_sim`, and the
  **currency of the `known` gate** — and its success criterion is an open design question
  (§7.1 item 5), not a detail to settle while running it.
- **`w_floor`'s inertness is not an independent defect** (§2.12). Fixing it in isolation
  would achieve nothing.

---

**Scripts — committed, not lost.** `builder/analysis/2026-07-22-cap-ranking-replay/`
holds `part1_probe.py`, `precheck_mbid.py`, `replay.py`, `decompose.py` and `replay.log`,
with a README covering the hardcoded paths and what they need to run. The ~75 MB
`precap.npz` cache is **not** committed; `decompose.py` regenerates it from the archive.
They were rescued from a scratchpad directory that was about to be cleaned — a checksum
and a prose description are not enough to re-run an experiment.

---

## 3. Phase 1 work record

### 3.1 Orientation and the app test

Session-start ritual run. Test-queue entry (post-`capfix` adoption sanity check) was
outstanding; the owner completed it during this session — **no regressions found**, and the
only missing artists were ones already known to be absent.

The dev API was switched from the 5,000-node fixture to the **full 74,191-node adopted
graph** for all testing, on the reasoning that the 5k fixture represents the obscure tail
worst, and the tail is what bypass exercises. Artifact identity was asserted by sha256
before any conclusion was drawn.

### 3.2 The owner's dogfooding trace (motivating evidence)

The owner bypassed ~15 times on The Shins → Wishbone Ash. Reconstructed against the full
graph:

- **Novel-artist payload collapsed** from ~6 to ~2 as bypasses accumulated, while path
  length **shortened 11 → 7**. The inverse of the stated target (successive bypasses,
  especially of hubs, should yield progressively fewer hubs).
- **Hub-for-hub swapping**: bypassing Aerosmith (via `dislike`) returned Pearl Jam.
- **The Smiths ↔ The Shins is a mutual edge scoring exactly 1.000** — a p99-ceiling edge,
  i.e. zero similarity cost.

*(Note in light of §2: "payload" here is the degree-based count. Its meaning is now
uncertain.)*

### 3.3 C3 confirmed as diagnosed

Verified against the code, not assumed: `w_floor` is wired into the cost
(`pathfinding.py:104`) but empirically inert because `floor = min(pop_source, pop_target)`
and routed paths do not dip below it (adjudication §5.4, claim 23). `known` differs from
`dislike` **only** through `floor_relax_known`, which feeds that inert term — so `known`
degrades to a bare hard exclusion. `w_hub` exists and defaults to `0.0`. The owner's 19
`known` bypasses therefore steered nothing.

### 3.4 The owner's `known` semantic (his specification)

> Clicking `known` on artist K should route to an artist **highly similar to K but more
> obscure** — "I know The Beatles, give me a Beatles-like act I haven't heard."

Explicitly **not** global anti-fame pressure, and **not** neighbourhood avoidance. `dislike`
keeps its existing neighbourhood-avoidance behaviour.

### 3.5 Experiment protocol, and ML-analyst review #1

A diagnostic experiment was specced
(`specs/2026-07-22-c3-bypass-diagnostic-experiment.md`) and reviewed by `ml-graph-analyst`
before execution. The review found a **false claim** and several confounds. Revision 2
folded in:

- **M3 corrected from arithmetic to geometric-mean Adamic–Adar**, matching `evaluation.py`
  and the aggregator claim 40 used. Arithmetic mean is dominated by the *best* hop and would
  have masked the incoherent-hop failure the guardrail exists to catch.
- **Overlap coefficient added as a mandatory degree-neutral co-guardrail** (adjudication
  §4.3): AA carries a pro-hub min-degree coupling, and the `known` mechanism lowers degree
  by design, so AA alone would falsely reject a coherent obscure reroute.
- **Split into a cheap Stage 0 binding pre-check and a Stage 1 panel**, because the proposed
  mechanism might not bind at all.
- **Held-out design** (200 pairs, 100/100 split, sign-reproduction, bootstrap CIs, a
  predefined ≥1-artist payload delta) per the claims 41–42 sign-flip discipline.
- M5 pooled over traversed hub-hops; M6 replaced with a hub-replacement rate.

### 3.6 Stage 0 — the binding gate

Implemented by mirroring production `find_path` and verifying the copy reproduced it
exactly with the mechanism disabled, so any difference is provably the mechanism.

**Result: the proposed multiplicative throughput discount is INERT** at the proposed default
strength (`w_known = 0.5`) on all three trace states — identical paths to production. It
bound only at `w_known = 0.9`, and only on the deepest-bypass state. Interior nodes below
the obscurity floor: **0** in every arm and state.

### 3.7 ML-analyst review #2 (fresh reviewer) — what it overturned

A second, independent analyst reviewed the revised protocol, the Stage 0 code and its
result. It **overturned the controlling session's own diagnosis**:

- **"The blocker is `w_jump`" was wrong.** A cost decomposition of the actual hops showed
  (a) the multiplicative discount scales the *whole* base cost, so it never specifically
  fights `w_jump`; and (b) on the hops that actually reach obscurity, **`w_sim` is the
  barrier** (74% of cost on the genuine dive hop vs 26% for `w_jump`).
- **The real blocker is the free hub expressway.** Ceiling-saturated hub-to-hub hops cost
  as little as **0.001** because sim = 1.0 zeroes the `w_sim` term. A *multiplicative*
  discount is proportional to base cost and cannot undercut a near-zero competitor at any
  strength. **It is a wrong-shape problem, not a wrong-strength problem.**
- **The redesign ranking was inverted**: waiving `w_jump` is the weaker option; a **bounded
  additive node reward** is the right shape, but only if its cap permits edge cost to reach
  **0** (Dijkstra requires ≥ 0, not > 0). A **hard waypoint** (two-leg route through the
  cousin) was identified as a missing third form that binds by construction.
- **The Stage 0 floor-confound clearance evaporates under the redesign** — 0-below-floor was
  measured on an *inert* mechanism, so it does not transfer; Stage 0 must be re-run on
  whatever mechanism is eventually chosen.
- **The obscurity cap observed was formula-induced, not structural**: `d = sim·Δpop` rewards
  both high similarity and a large popularity drop, which fight each other, clustering
  selection at intermediate popularity.
- **The overlap coefficient has its own regime failure** (its min-degree denominator shrinks
  exactly when routing to low-degree nodes); raw `mean_common_neighbours` was added as the
  degree-independent backstop.

Review #1's fixes were independently re-checked by review #2 and **held**.

### 3.8 Stage 0 v2, the rejected refinement, and the blind listen

**Both redesigned shapes bind.** The additive-reward form reached obscurity but retained
ceiling hub hops; the waypoint form was hub-free and coherent at deep bypass but forced an
incoherent detour at shallow bypass.

**A route-aware waypoint selection was tried and REJECTED.** Choosing the cousin that
minimises detour cost selects **hub-adjacent** cousins, because the free ceiling hops are
the cheapest routes — it routed through Beyoncé and Madonna and raised mean interior
popularity above baseline. Cost-based selection is captured by the expressway it should
escape.

**Offline metrics could not separate the two shapes** (AA/OC collapsed while
`mean_common_neighbours` rose — the degree-coupling regime, confirmed live), so the decision
went to a **blind listening test**
(`specs/2026-07-22-c3-known-mechanism-blind-listen.md`).

**Blind listen result** — 3 pairs × 4 bypass depths, three arms (V0 = current production,
A = additive reward, C = waypoint), tokens shuffled per pair, mapping sealed until verdicts
were recorded:

| pair | d5 | d10 | d15 | d20 |
|---|---|---|---|---|
| Miles Davis → Daft Punk | V0 | A | A | A |
| The Shins → Wishbone Ash | A | A | V0 | V0 |
| Metallica → Taylor Swift | tie | C | C | C |

**Tally: A additive 5, V0 (current) 3, C waypoint 3** — 11 clear picks and 1 no-preference.
**No mechanism dominates**, the winner is pair-dependent, and **the current shipped
mechanism beat both redesigns at deep bypass on one pair.**

**Which hidden metric tracked the owner's ear** (how often his pick optimised it, 11 rows):

| metric | agreement |
|---|---|
| payload (non-hub interior count) | 8/11 (72%) |
| ceiling_hops | 8/11 (72%) |
| hubfrac | 7/11 (63%) |
| mean_common_neighbours | 5/11 (45%) |
| adamic_adar | 3/11 (27%) |
| overlap_coefficient | 3/11 (27%) |

**The owner's stated decision criterion was coherence, not hub incidence.** In his own
summary: hub incidence felt **high across all arms**, he could not have chosen on hubs
alone, and **coherence decided nearly every selection**. The two metrics built to guard
coherence (AA, OC) are the **worst** predictors of his verdict.

He also reported that **bad clips were noticeably intrusive** (Metallica's clip wrong, CCR's
a remix), and that judging an unfamiliar artist from a single clip was occasionally hard —
he judged neither materially affected the verdicts.

Immediately after this, the questioning of `hubfrac` against his perception led to §2.

### 3.9 The owner's verdict notes, verbatim

**Why these are preserved rather than summarised.** Coherence decided the listen, and **no
metric we have captures it** (§3.8). These notes are therefore the only operational
description in the record of what the owner means by a coherent journey — a small labelled
corpus of what reads as smooth versus jarring, in his own words. Anyone trying to define,
learn, or test a coherence objective should start here rather than from a metric.

Arms are named (the test was blind at the time; the mapping is in §3.8's table).

**Miles Davis → Daft Punk**

- *d5 (picked V0):* "Tough decision. [C] was discarded first as the Avril Lavigne and
  Blink-182 hops felt wrong for the path (coherence). [V0] felt more coherent than [A]."
- *d10 (picked A):* "[A] felt distinctively more coherent in this set and feels like fewer
  hubs to me (or at least, a smaller ratio of hubs). [C]'s Taylor Swift → Daft Punk feels
  like a big jump, and [V0] seems least coherent after Aretha Franklin."
- *d15 (picked A):* "[A] feels overall most coherent, though the Kylie Minogue to Justin
  Timberlake step feels off. I don't know those two artists' discography deeply, but I
  suspect they both have a range of styles in their catalog which might explain why they are
  neighbors. [C]'s Avril → Britney → Daft Punk hops don't make sense to me."
- *d20 (picked A):* "The hardest of the three to differentiate. Surprising because based on
  previous tests, more bypasses made issues more pronounced. From a hub perspective, this
  pop-pop pairing may be a really challenging one… My feedback on all rows is driven more by
  coherence than hub-elimination. **[A] ultimately chosen because the longer path genuinely
  does feel like it transitions well to me, but nearly every step looks like a hub.**"

**The Shins → Wishbone Ash**

- *d5 (picked A):* "[C] discarded pretty quickly. The Shins to the White Stripes feels like a
  leap that should have at least a step in between. **[A] inserts the Flaming Lips between
  the Shins and the White Stripes, fixing the issue [C] has.** All 3 have many well-known
  artists, but [A] wins on coherence."
- *d10 (picked A):* "The Shins to Kings of Leon feels like a bit of a jump, but the
  connection is real and all 3 have it. [V0]'s inclusion of Marilyn Manson doesn't land with
  my ears… Kings of Leon → Green Day → CCR doesn't feel right."
- *d15 (picked V0):* "[A] seems to go all over the place. Low coherence from my ears. [V0]
  wins — this one feels like a path that's gone through bypasses but remains coherent. [C]
  doesn't look that different from paths in the lesser-bypassed rows above."
- *d20 (picked V0):* "A lot of hubs. What's interesting about this set is it feels like the
  first few hops in each are less well-known, but then each lands on hubs. **[A] — feels like
  it got gravitationally pulled towards a hub around step 3-4, then had to fight its way back
  to Wishbone Ash.** [C] — I get the Florence → Sia transition, but then going to Justin
  Timberlake and Mariah Carey feels like it headed in the wrong direction. [V0] — tempted to
  eliminate because of the Bastille → Fall Out Boy → Marilyn Manson jump, but coherent enough
  to rise above the other two."

**Metallica → Taylor Swift**

- *d5 (no preference):* "[A] and [V0] are the same path. [C] is interesting… a more
  interesting path, with lesser known artists involved. The Daft Punk to Taylor Swift jump
  feels like a leap, but could be explained by the pop genre and popularity of those artists.
  I'm tempted to pick [C], but I will pick 'no pref'… [A] and [V0] being identical and [C]
  including multiple artists that I like may be confounding." *(Recorded as a true
  no-preference and excluded from the tally; the lean toward C is noted, not counted.)*
- *d10 (picked C):* "[A] — to me, incoherent: Metallica to Oasis? Bon Iver to Ye to Taylor
  Swift? Not registering with me. [V0] — similar; the Metallica jump to Bob Dylan doesn't
  land as right. [C] — much more coherent, and feels like fewer hubs. Clearest winner I've
  reviewed so far."
- *d15 (picked C, radio left blank — verdict taken from the note):* "**A 4-clip, highly
  popular artist path in the 15 category row is a red flag to me.** Discarding [V0]… [C] wins
  out — fewer hubs while keeping coherent to my ears."
- *d20 (picked C):* "[C] wins — I think it retains coherence while including fewer hubs."

**His general observations on the exercise:**

- The blind side-by-side format was **materially better than running two app instances
  manually**; the improvement he asked for is verdicts written to disk rather than
  copy-pasted (§7).
- **Hub incidence felt high across every arm**, and he could not have chosen on hub incidence
  alone — except on Metallica → Taylor Swift, which felt like it had fewer hubs overall,
  especially at the deeper bypass counts.
- Judging an unfamiliar artist from a **single clip** is a real limitation; he flagged the
  rows where he suspected the clip was unrepresentative of a catalog.

### 3.10 Reproducibility — parameters and the verification method

**Parameters actually used.** The Stage 0 and listen figures cannot be reproduced without
these; only `w_known` appears elsewhere in this log.

| parameter | value | what it controls |
|---|---|---|
| substitute pop-drop gate | **≥ 0.10** | how much more obscure than K a node must be to qualify |
| quality-cousin similarity gate | **≥ 0.70** | waypoint candidate admission (form C) |
| `w_known` (multiplicative form) | swept **0.5**, **0.9** | the inert form of §3.6 |
| `w_known` (additive form) | **1.0** | the binding form of §3.8 |
| bypass policy | **all-`known`, bypass the highest `hub_penalty` interior artist each step, walked independently per arm** | each arm is driven by bypassing what *that arm* shows, which is how it would really be used |
| snapshots | **5, 10, 15, 20** bypasses | the depth axis |
| pair/token shuffle seed | **20260722** | blind token assignment, per pair |
| hub set | **frozen top-1% by degree** (`hub_node_set(store, 0.01)`) | see §2.6 — this is the definition now in question |

**The verification method — reuse this for any future mechanism test.** Stage 0's central
claim ("the mechanism is inert") is only trustworthy because the comparison was built this
way, and review #2 specifically checked that it isolated the mechanism:

1. **Mirror** production `find_path` in the experiment harness rather than editing it.
2. **Assert the mirror reproduces production exactly** on the real workload with the
   mechanism switched off. If the paths are not identical, stop — the harness is wrong.
3. **Only then** layer the mechanism on top. Any difference is now provably the mechanism
   and not a reimplementation artifact.

Its one known limitation, named by review #2: the self-check exercises the mechanism-**off**
path only, so a bug in how the mechanism is *applied* would not be caught by it and still
needs reading.

**Blind-test integrity, if a listen is run again.** What made the listen genuinely blind:
the generator emitted a **public** file (tokens + artist names only) and a **secret** file
(token→arm mapping + hidden metrics); only a dedicated directory containing the page and the
public file was served, so the secret file returned 404; tokens were **shuffled per pair**, so
a token means a different arm in each pair and the listener cannot learn the pattern; and the
API's CORS origin was widened by **environment variable**, so no shipped code was touched.

---

## 4. Closed — do not re-argue

- **The `known` semantic** is the owner's specification in §3.4. Not global anti-fame, not
  neighbourhood avoidance.
- **The multiplicative throughput discount is dead** — wrong shape, cannot beat a
  near-zero-cost ceiling hop at any strength (§3.7).
- **Cost-based ("route-aware") waypoint selection is rejected** — it selects hub-adjacency
  (§3.8).
- **Offline coherence metrics (AA, overlap coefficient) do not track the owner's ear** at
  these effect sizes (§3.8). Do not settle a coherence question on them alone.
- **Stage 0's thin data was adequate for the binding question** (a floor/existence property)
  and **not** for quality questions — which is why quality went to the ear. This was
  explicitly examined and agreed.
- **M3 is geometric-mean AA**, and the overlap coefficient is a mandatory co-guardrail.
  Both were independently confirmed by two analysts.

### 4.1 Closed by the §2.8–§2.13 defect work (2026-07-23)

- **The `capfix` adoption is not overturned.** `control` is disassortative *and* carries
  degree-11,241 hubs, and the owner preferred `capfix` blind, twice. Both are true at once:
  `capfix` removed the hub expressway **and** severed the route to obscurity. That is the
  owner's own "improvement, not goodness" (Phase 2 log §12), now with a mechanism.
- **`capfix` vs `rankfix` is not worth a listening test.** Identical assortativity (+0.596
  under a fixed reference) and identical behaviour on the tail. A listen would burn the
  owner's ear on a null.
- **No graph change is indicated by §2.8–§2.12.** §2.10's alternative `cap_strategy` is
  **deferred, not killed** — §2.12 removed its motivation before anyone built it, which is
  discouragement rather than unreachability.
- **The C3 A-vs-C mechanism question is moot** until the cost function is settled. Both
  prototypes were tuned on a substrate where no mechanism reached below the 92nd popularity
  percentile.
- **`w_floor`'s inertness is not an independent defect** (§2.12). Fixing it alone achieves
  nothing; it is a symptom of `w_jump`.
- **§2.4's candidate A being falsified for the degree collapse and revived for the
  stratification is not a re-reversal.** Two mechanisms, two symptoms; §2.10's 2×2 factorial
  gave the revival the one-knob intervention §2.4 never had.
- **`d025` is not a witness for anything.** Three knobs from `capfix`, not
  `p99_log_clip` at all, and unbuildable with current code (§2.2's correction notice).

---

## 5. Artifacts

**Branch `phase1-c3-bypass`, draft PR #5.** Committed:

- `specs/2026-07-22-c3-bypass-diagnostic-experiment.md` (revision 2)
- `specs/2026-07-22-c3-known-mechanism-blind-listen.md`
- this document

**No shipped code was modified.** Nothing landed in `ApiConfig`, `pathfinding.py`, or any
package. Both mechanisms exist only as throwaway scripts.

**Research scripts — COMMITTED 2026-07-22** (they were scratchpad-only and about to be
lost; each directory has a README):

| Directory | Contents |
|---|---|
| `builder/analysis/2026-07-22-c3-bypass-mechanisms/` | §3's work: `reconstruct.py` (the owner's trace), `stage0.py` (the binding gate and the mirror-and-verify method of §3.10), `stage0b.py` (both redesigned shapes), `stage0c.py` (the **rejected** route-aware waypoint, kept as a negative result), `listen_gen.py`, `listen.html`, `unblind.py`, plus `listen_public.json` and `listen_secret.json` — the exact 36 paths judged, the sealed mapping, and the hidden per-path metrics. The blind test is un-blinded, so the secret file is no longer sensitive. |
| `builder/analysis/2026-07-22-graph-defect-discovery/` | §2.2's discovery: `hubcheck.py`, `beatles.py`, `compare_graphs.py` (**has a known duplicate-name bug** — superseded by the next), `dropped.py`. |
| `builder/analysis/2026-07-22-cap-ranking-replay/` | §2.8's one-knob intervention. |

These are **research tooling invoked manually** — nothing imports them, which is correct
(Phase 2 execution log §18, B2). Paths are hardcoded deliberately: they are a record of what
was executed, not a maintained tool.

**Artifact checksums** (gitignored; checksum is their only identity):

**All six artifacts compared in §2, with checksums.** These are gitignored, several exist,
and they are **not interchangeable** — a conclusion drawn from the wrong one looks exactly
like a correct one. Every probe script in `builder/analysis/` asserts the sha256 before
measuring; keep that. *(Completed at closeout D3 — only `capfix` was recorded before, while
§2.9–§2.12 compare five.)*

| artifact | sha256 | used in |
|---|---|---|
| `graph-t15-capfix.bin` **(ADOPTED)** | `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` | everything |
| `graph-t15-rankfix.bin` | `87d9bf7edfc51fb13ee0fdf6a4216d01df7d3aa7f38b66ea9b7b8c2e7addae05` | §2.9 tail probe, §2.10 |
| `graph-t15-control.bin` | `d3016bc06dd9e62de9e6edff3206ca9a3d8366243ca18b2588c0a7063042f57a` | §2.2, §2.9, §2.10 nulls |
| `graph-75k.bin` (original) | `478426753de39282f99c0b8955a846d159deb656576026b265bec9060977d5ff` | §2.2, §2.9 |
| `graph-t15-d050.bin` | `6fb52ff8e918cf14da6e4fc6fa52052a66d7bfdb35a7f910460c2c8868c80a20` | §2.9, §2.10 |
| `graph-t15-d025.bin` | `2811e87d1c900e4ec233317c05143ccaec5a3f0e1fb3c531c04455594bb27e65` | §2.2 only — **do not cite, see §2.2's correction notice** |

---

## 6. State of play

- **Phase 1 C3 is not implemented.** No mechanism is chosen; the A-vs-C question is
  **unresolved** (no clear winner, pair-dependent) — and **moot until the cost function is
  settled** (§2.9, §2.13): both prototypes were tuned on a substrate where no mechanism
  reached below the 92nd popularity percentile.
- **Phase 1 is paused pending the owner's decision on §2.**
- **Updated 2026-07-23:** the diagnosis changed. §2.12 concludes this is a **cost-function**
  problem rather than a graph one. **No graph change is indicated by any of §2.8–§2.12** —
  the §2.8 tie-break fix (Radiohead, The Beatles) remains real, cheap, and a standalone
  owner decision about whether it earns its own rebuild-and-re-adopt cycle. The next
  experiment is a three-knob cost-function sweep whose success criterion is still open
  (§7.1 item 5).
- Two mechanism shapes are specified and prototyped but exist only in scratch.
- Stage 1 of the diagnostic experiment was **never run** — Stage 0 gated it, then the
  listen superseded it, then §2 halted the work.

---

## 7. Deferred, with what would make them due

- **Clips C1 (wrong-artist matching) / C2 (signed-URL expiry vs 30-day cache).** Already in
  the roadmap as Phase 1 items. This session added evidence that they are **evaluation
  infrastructure, not only UX** — a wrong clip is a confound in any listening test.
- **The p99 ceiling defect.** Carried from Phase 2 with its own success condition. This
  session found it implicated in *two* further ways: it manufactures near-zero-cost hub
  expressways (§3.7), and it flattens the transition-quality signal the owner actually
  judges on (every hop in one listen pair scored exactly 1.0).
- **Blind-listen harness improvement:** verdicts should be written to disk rather than
  copy-pasted. Raised by the owner after using it.
- **Duplicate artist names** with distinct MBIDs (§2.2) — noticed, not investigated.
- **Stage 1 of the diagnostic experiment**, if and when a mechanism is chosen — and note
  Stage 0 must be re-run first on the chosen mechanism (§3.7).

### 7.1 Opened by the §2.8–§2.12 defect work (closeout A3, 2026-07-23)

**Three of the five items below had no success condition when raised.** They do now.

| # | Item | Success condition |
|---|---|---|
| 1 | **Exact configuration-model null.** §2.10's 15.6× depletion rests on a randomised greedy b-matching leaving 3.9–7.7 % of degree quota unmet, not an exact rewiring. | **Rebuild exactly if anyone challenges the 15.6×, or before it becomes load-bearing for adopting a new `cap_strategy`.** If neither happens it expires unactioned — a legitimate terminal state. |
| 2 | **The MBID/in-degree coupling** in the archived source data (§2.8) — monotone, no proposed mechanism, never independently checked. | **Verify before citing it anywhere.** §2.8 already carries this warning inline. Nothing else depends on it; the intervention result holds without it. |
| 3 | **Snyk: 3 Medium DOM XSS in `listen.html`** (`builder/analysis/2026-07-22-c3-bypass-mechanisms/`, lines 90/98/109). Artist names from a remote resource flow into the DOM unsanitised. MusicBrainz names are user-contributed. | **ACCEPTED by the owner, 2026-07-23, on merge of PR #5.** The fix was offered and declined. Rationale: the page is a local, single-user, throwaway analysis harness; it is not shipped, not served publicly, and reaches only a localhost API. The cost is that **`main` is no longer Snyk-clean** — anything scanning the default branch will report these three. **Reopens if the harness is ever served beyond localhost or reused by someone other than the owner.** Fix is `textContent` over `innerHTML` and changes no output. |
| 4 | **`listen_secret.json` is committed** at a predictable path. Harmless for the completed test — it is un-blinded. But §15's session-hygiene rule requires the session *running* a blind test not to know the mapping, and the harness is preserved for reuse. **Raised 2026-07-23, had no address.** | **Before the next blind listen:** gitignore future `listen_secret*.json`, or have `listen_gen.py` write secrets outside the repo. Recorded in the harness README either way. |
| 5 | **A cost-function experiment's success criterion** (§2.11, §2.12). "Reaches below p90" is gameable in *two* currencies — raw drops that stay famous, percentile drops that land in insular high-popularity genres. **Raised 2026-07-23, had no address.** | **Settled before the `w_jump`/`w_sim`/gate-currency sweep is specified, not after it reports success.** |

**Conditions that came due this session:** §17's carried "a hub-incidence-versus-bypass-count
measurement exists" — satisfied by §2.9's tail probe, and the channel is flat on both graphs.

**Nothing was killed this session.** The new `cap_strategy` of §2.10 is **deferred, not
killed** — §2.12 makes it unlikely to be the fix, which is not the same as its path being
closed, and the standing rule is to kill on unreachability rather than on discouragement.
