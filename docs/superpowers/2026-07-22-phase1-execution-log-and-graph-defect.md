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

- `graph-t15-capfix.bin` (adopted, and the subject of §2) — sha256
  `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237`
- Comparison artifacts used in §2.2: `graph-t15-control.bin`, `graph-t15-d025.bin`,
  `graph-75k.bin`, all present in `builder/scratch/`.

---

## 6. State of play

- **Phase 1 C3 is not implemented.** No mechanism is chosen; the A-vs-C question is
  **unresolved** (no clear winner, pair-dependent).
- **Phase 1 is paused pending the owner's decision on §2.**
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
