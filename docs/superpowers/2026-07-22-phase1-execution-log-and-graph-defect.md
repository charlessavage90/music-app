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

---

## 1. How to read this document

- **§2 is the blocker.** Facts, discovery mechanism, suspected cause. No solutions — by
  explicit instruction, this document does **not** propose fixes or diagnose deeply.
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

**`d025` — the same mutual-kNN capping but with `similarity_damping=0.25` — does not show
this:** Radiohead 50, The Beatles 50, Coldplay 50, all present and at the cap.

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

### 2.4 Suspected root cause (stated as suspicion; not investigated further, by instruction)

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

**No solution is proposed in this document, by instruction.**

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

**Throwaway scripts (NOT in git; scratchpad only, will be lost when the session's temp
directory is cleaned):** `reconstruct.py`, `stage0.py`, `stage0b.py`, `stage0c.py`,
`listen_gen.py`, `listen_serve/listen.html`, `unblind.py`, `hubcheck.py`, `beatles.py`,
`compare_graphs.py`, `dropped.py`, plus `listen_public.json` (blinded) and
`listen_secret.json` (sealed mapping + hidden metrics). **If any of this needs to survive,
it must be committed deliberately.**

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
