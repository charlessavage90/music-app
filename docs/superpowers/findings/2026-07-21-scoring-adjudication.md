# Scoring & Path-Quality Metrics — Adjudicated Record

**Date:** 2026-07-21
**Amended:** 2026-07-21 (§4.3 restated, §4.4 added, §6 rows 28–30 added, §8 note added) —
see §4.4 for what changed and why.
**Status:** This is the single consolidated quantitative record for edge scoring and
path-quality metrics. It **supersedes** the contested sections of both source documents:

- `findings/2026-07-21-architecture-review-and-path-baseline.md` §5 (commit `c041d4a`)
- `specs/2026-07-21-phase2-path-quality-design.md` §1 and §B (commit `817e76c`)

Everything below was re-derived today against the artifacts in `builder/scratch/` and
against the raw crawl archive. Nothing is carried forward on trust from either document.
Where a prior number reproduced, it is marked upheld; where it did not, it is marked
overturned and the correct figure is given. Reproduction snippets are in §8.

---

## 0. The one-paragraph summary

**Both source documents are partly wrong, and they are wrong about the same thing.**
The `p99` clip in `pipeline.py:110-122` makes ~1% of edges cost *exactly zero* under
`w_sim·(1 − sim)`. Dijkstra therefore chains free edges. Which artists those free edges
point at is decided entirely by the damping exponent `d`: at `d = 0` they point at hubs
(median destination out-degree **719**), at `d = 0.5` they point at micro-cliques
(median destination out-degree **9**). So the adopted graph routes `Miles Davis → Ella
Fitzgerald → Dean Martin → Mariah Carey → Justin Timberlake → Daft Punk` — five
consecutive hops at score 1.000 — and the rejected graph routes `Miles Davis →
J. K. Simmons → Hank Levy → Justin Hurwitz → Emma Stone → Daft Punk`. These are the
same bug with the sign of `d` flipped. **No value of `d` fixes it**, which means the
Phase-2 sweep as specified is measuring a variable that cannot resolve the defect, from
a control cell that is itself defective.

---

## 1. Artifact provenance — established first, because it changes everything

The five artifacts in `builder/scratch/` were **not all built by the same code**. This
was not recorded anywhere and both source documents compare them as if they were.

| Artifact | Built | Code | Damping `d` | Rescale |
|---|---|---|---|---|
| `graph-5k.bin` | Jul 20 15:33 | pre-`284366c` | n/a | per-artist max-normalisation |
| `graph-75k.bin` | Jul 21 00:39 | pre-`284366c` | n/a | per-artist max-normalisation |
| `graph-75k-cosine.bin` | Jul 21 08:19 | `284366c` | **0.5** | **linear** (`value / p99`) |
| `graph-75k-v2.bin` | Jul 21 08:30 | `284366c` (working tree, `d=0`) | 0.0 | **linear** (`value / p99`) |
| `graph-75k-v3.bin` | Jul 21 08:33 | `fff422e` = current | 0.0 | **log** (`log1p(v)/log1p(p99)`) |

Evidence:

- `builder/scratch/rebuild.log` and `rebuild2.log` emit `cosine scale (p99) = …`, the
  log string that `fff422e` renamed to `similarity scale`. `rebuild3.log` emits the new
  string. So the first two artifacts predate `fff422e`.
- `v3.scores == min(1, log1p(v2.scores · 1627) / log1p(1627))` holds to **max abs error
  3.61e-08** over all 4,102,014 unsaturated edges, and `v2.neighbours == v3.neighbours`
  exactly. v2 and v3 are the same build differing only in rescale.
- Miles Davis → Stan Getz: archive cooc = 2357, mass(Miles) = 144,013, mass(Getz) =
  77,870 → cosine = **0.022257**. `graph-75k-cosine.bin` stores **0.2224** =
  0.022257 / 0.100074, the *linear* rescale. The log rescale would store 0.2309.
  Confirmed linear.

**Consequence.** The `fff422e` comparison that rejected cosine changed *two* factors at
once — `d` 0.5 → 0.0 **and** rescale linear → log. Findings §4's table presents this as
a one-factor comparison. Spec §1.1's side-by-side of v3 against cosine is likewise a
two-factor comparison. Neither document states this.

---

## 2. Claim 1 — why full cosine appeared to fail

### 2.1 A's mechanism is real code but was not the cause

Position A (§5.4): damping is applied before `log1p`, "silently degenerating log scaling
into linear scaling", and this produced the inflated junk-edge scores.

- **The ordering hazard is real in the current code.** At `d = 0.5` the damped values are
  O(0.01–0.1); `log1p(x) ≈ x` there, so `log1p(v)/log1p(p99)` reproduces `v/p99` to within
  ~2%. Setting `similarity_damping = 0.5` today would produce a near-linear rescale.
  **Upheld as a live hazard.**
- **It cannot have caused the §4 result.** `graph-75k-cosine.bin` was built by `284366c`,
  whose rescale is `min(1.0, value / scale)` — there was no `log1p` in the code to
  degenerate. **Overturned as the explanation.**
- **It cannot invert a ranking either.** Position B is correct: `min(1, log1p(x)/log1p(p99))`
  is monotone non-decreasing, so within a fixed pair-set it preserves order except for
  ties at the ceiling. **B upheld.**

### 2.2 B's diagnosis of the p99 clip is upheld and reproduces exactly

| Artifact | edges at exactly 1.0 | median out-degree of their destinations | graph node-median degree |
|---|---|---|---|
| `graph-75k-v3.bin` (`d=0`) | **34,696** / 4,102,014 (0.846 %) | **719** | 49 |
| `graph-75k-cosine.bin` (`d=0.5`) | **27,808** / 3,582,502 (0.776 %) | **9** | 49 |
| `graph-75k-v2.bin` (`d=0`, linear) | 34,696 | 719 | 49 |
| `graph-75k.bin` (per-artist norm) | 156,290 (3.893 %) | 59 | 44 |

B's figures reproduce to the digit. **B §1.2 upheld.**

### 2.3 But B's *verdict* — that cosine does not over-correct — is overturned

Spec §1.1 says findings §4 "does not reproduce in either built artifact" and that
"`Justin Hurwitz` and `Emma Stone` are neighbours of Miles Davis in neither graph".
The second statement is true and irrelevant: they are *interior hops*, not Miles'
neighbours. Routed with the production cost function on `graph-75k-cosine.bin`:

```
Miles Davis[d337]
 -> J. K. Simmons[d17   rank 327/337  score 0.009]
 -> Hank Levy[d46       rank   3/17   score 1.000]
 -> Justin Hurwitz[d96  rank   4/46   score 1.000]
 -> Emma Stone[d51      rank   4/96   score 0.996]
 -> Daft Punk[d128      rank  37/51   score 0.020]
```

This is findings §4's "film-soundtrack nonsense" path, **verbatim, in the built
artifact.** The qualitative core of §4 is substantiated, not retracted.

The mechanism is the PPMI pathology B's own §B4 names and then dismisses. The router
pays 3·(1 − 0.009) = 2.97 once to enter the *La La Land* cast clique, then crosses it
for free — three consecutive edges at ≥0.996 — for a total of ~3.1 over five hops,
against ~12 for a five-hop jazz route. Cosine's saturated edges have median destination
degree **9**: the free tie-mass points directly into micro-cliques.

Other cosine paths read the same way — `Nina Simone → Radiohead → Deftones`,
`Burzum → Akira Yamaoka → David Bowie → Dolly Parton` — hub-hopping at scores of 0.08.

### 2.4 The §4 junk-edge number is refuted; one half of it is traceable

Findings §4 and commit `fff422e`: *"a junk edge scored 0.148 against 0.022 for Miles
Davis → Stan Getz, 6.6× backwards"* and *"2357 vs 277 on the measured examples"*.

Computed from the raw archive under the pipeline's own definitions:

| Quantity | Value |
|---|---|
| cooc(Miles, Stan Getz) | **2357** ✓ matches the commit message |
| cosine(Miles, Stan Getz) | **0.022257** ✓ matches "0.022" |
| cooc(Miles, J. K. Simmons) | **14** (reverse direction only; Miles' raw list does not contain him) |
| cosine(Miles, J. K. Simmons) | **0.000938** |
| **max cosine over all 566 of Miles' symmetrised edges** | **0.0497** (Miles Davis Quintet) |
| edges with cosine in [0.10, 0.30] | **none** |

Cross-checks confirming cooc = 14: `graph-75k-cosine.bin` stores 0.0094 = 0.000938 /
0.100074, and `graph-75k-v3.bin` stores 0.3662 = log1p(14)/log1p(1627). Both match
Position B's lookups.

**Verdict: "0.148" has no referent.** No Miles edge attains a cosine value within 2× of
it, in either direction, on any artifact or on the archive. Under cosine, Stan Getz
(0.0223) outranks J. K. Simmons (0.00094) by **24×, in the correct direction** — B's
figure, confirmed. The "277" in the commit message is likewise unreproducible (the
actual cooc is 14). The **number** is fabricated or mistranscribed; the **conclusion it
was offered in support of** happens to be right for a different reason (§2.3).

Both documents get this backwards. A published a number that does not exist. B correctly
refuted the number and then wrongly concluded the finding was retracted.

### 2.5 The unifying account both documents miss

The p99 clip creates free edges in *every* build. `d` decides only where they point:

| | free edges | median dst degree of free edges | % of routed hops at score 1.000 | mean path length |
|---|---|---|---|---|
| `graph-75k.bin` (per-artist) | 156,290 | 59 | **81.9 %** | 13.4 |
| `graph-75k-v2.bin` (`d=0`, linear) | 34,696 | 719 | **55.4 %** | 6.9 |
| `graph-75k-v3.bin` (`d=0`, log) | 34,696 | 719 | **44.8 %** | 7.6 |
| `graph-75k-cosine.bin` (`d=0.5`) | 27,808 | 9 | **30.1 %** | 6.3 |

(25 seeded random pairs, production `ApiConfig`.) Between 30 % and 82 % of every routed
hop is a **zero-similarity-cost** hop. On such a hop the router is choosing on
`w_jump·|Δpop| + w_hop` alone — mean 0.104 and 0.02 respectively — i.e. on noise.

This is one defect with two faces:

- `d = 0` → free edges are hub edges → paths cross the famous core
  (`Ella Fitzgerald → Dean Martin → Mariah Carey → Justin Timberlake`, all 1.000).
- `d = 0.5` → free edges are micro-clique edges → paths cross film cast lists.

**Therefore the Phase-2 sweep's control cell (`p99-log-clip`, `d = 0`) is defective, and
sweeping `d` under the clip rescale cannot resolve the defect.** Factor R is not a
co-equal second factor; it is a precondition. Recommendation: fix the rescale first,
re-establish a clean control, and only then sweep `d`. Confidence: high — this follows
directly from the free-edge counts and the decoded paths above. Falsified if a
rank-rescaled `d = 0` build still shows ≥30 % of routed hops at the ceiling.

---

## 3. Claim 2 — the `− 2·log(median_mass)` centring term

Measured over all 3,992,533 in-`known` archive pairs (pre-cap), `median mass = 1229`,
`log median mass = 7.1140`.

### 3.1 Under a rank/percentile rescale: provably inert. B upheld.

`c = 2·d·log(median_mass)` is a global additive constant. Rank vectors of
`log1p(cooc) − d·(log mₐ + log m_b)` and of the centred form are identical: the
residual `|(raw_c − c) − raw_nc|` maxes at **3.55e-15**, and the ≤35,010-of-3,992,533
differing rank positions are float64 rounding among exact ties, not reordering. Since
the neighbour cap at `pipeline.py:100` also sorts on this value, the constant changes
nothing about which edges survive either. **Position B §B4 upheld: under a rank
transform the term does exactly nothing.**

### 3.2 Under the current clip rescale with A's clamp: catastrophically load-bearing

Fraction of edges driven below zero (and therefore destroyed by A's `max(0, ·)` clamp):

| `d` | without centring | with `− 2·log(median_mass)` | constant `c` |
|---|---|---|---|
| 0.25 | **78.67 %** | 0.00 % | 3.557 |
| 0.50 | **99.98 %** | 4.72 % | 7.114 |
| 0.75 | **100.00 %** | 30.62 % | 10.671 |
| 1.00 | **100.00 %** | 50.79 % | 14.228 |

At `d = 0.5` without centring the build is not merely worse, it is *degenerate*: 99.98 %
of edges clamp to 0, `p99(raw) = 0.000`, and the rescale emits `nan`. Both documents are
therefore incomplete:

- **A's formula is only safe because of the centring term, and A does not say why.** A
  presents it as part of the fix without noting that removing it makes the pipeline
  produce a null graph.
- **B's replacement formula is a trap.** Spec §B4 drops the centring term while §B5
  retains `p99-log-clip` as one of two Factor-R levels, giving a grid
  `R ∈ {clip, percentile} × d ∈ {0, 0.5, 0.75, 1.0}`. **Three of those eight cells
  (`clip × d ∈ {0.5, 0.75, 1.0}`) build a degenerate graph**, and `clip × d = 0.25`
  would destroy 79 % of edges. Neither document noticed this.

### 3.3 Is the clamp load-bearing or harmful? Harmful. B upheld.

With centring at `d = 0.75`, **30.62 %** of edges clamp to exactly 0 → identical raw
value → identical rescaled score → a uniform `w_sim·(1 − 0) = 3.0` cost across nearly a
third of the graph. That is the floor mirror-image of the 34,696-edge ceiling defect of
§2.2, an order of magnitude larger. **B's "the clamp creates floor tie-mass mirroring
the ceiling defect" is confirmed and quantified.** A rank transform needs neither the
clamp nor the centring term and removes both tie-masses at once.

**Verdict on Claim 2.** B is right on the substance (inert under rank; only matters
because of the clamp; clamp harmful). A's prescription is not "wrong" so much as
inseparable from a rescale it does not name. The correct action is B's — rank rescale,
no clamp, no centring — with the caveat B missed: *if the clip rescale is retained for
any arm, the centring term is mandatory, not optional.*

---

## 4. Claim 3 — the primary objective

### 4.1 B's Jaccard measurements reproduce. A §5.2 is overturned.

6,000 adjacent pairs sampled from `graph-75k-v3.bin`, seed 7:

| Measurement | B's figure | Re-derived | |
|---|---|---|---|
| `corr(log Jaccard, log max-degree)` (Pearson) | −0.655 | **−0.639** | upheld |
| Spearman(Jaccard, max-degree) | — | **−0.730** | new |
| median Jaccard, lowest → highest degree bucket | 0.4545 → 0.0087 | **0.4000 → 0.0090** | upheld |
| E, v3 → cosine | 4,102,014 → 3,582,502 | **identical** | upheld |
| max degree, v3 → cosine | 11,243 → 3,166 | **identical** | upheld |

Position A §5.2 argued Jaccard is "score-independent, therefore not circular. **This is
the one to optimise against.**" The inference does not follow: independence from *scores*
is not independence from *degree*, and the intervention under test changes degree (the
cap at `pipeline.py:100` is applied **after** damping, so `d` rewires adjacency —
519,512 edges and 8,077 of max-degree disappear between v3 and cosine). Bottleneck
Jaccard is a near-monotone restatement of `max_interior_degree`. **A §5.2's
prescription is overturned.**

### 4.2 But B's replacement is only half-vetted — and I would not adopt it alone

Same 6,000 pairs, all candidate objectives measured side by side (v3):

| Objective | median | Pearson(log ·, log **max**deg) | Spearman vs **max**deg | Spearman vs **min**deg |
|---|---|---|---|---|
| Jaccard | 0.0758 | −0.639 | −0.730 | +0.048 |
| **Adamic–Adar** | 3.9706 | **+0.110** | **+0.131** | **+0.578** |
| Common neighbours | 20.0 | +0.163 | +0.247 | +0.634 |
| Obs/Exp (configuration model) | 17.06 | −0.667 | **−0.880** | −0.291 |
| Salton cosine `CN/√(d_u·d_v)` | 0.1806 | −0.429 | −0.650 | +0.032 |
| **Overlap coefficient `CN/min(d_u,d_v)`** | 0.4000 | **−0.004** | **−0.092** | **−0.062** |

Median by max-degree bucket, v3:

| bucket | n | Jaccard | Adamic–Adar | Obs/Exp | Salton |
|---|---|---|---|---|---|
| 0–10 | 35 | 0.4000 | 1.04 | 849.6 | 0.5714 |
| 10–25 | 84 | 0.3079 | 2.12 | 334.4 | 0.5016 |
| 25–50 | 204 | 0.2070 | 2.91 | 127.2 | 0.3775 |
| 50–100 | 1678 | 0.1815 | 3.76 | 55.1 | 0.3248 |
| 100–300 | 1664 | 0.1079 | 4.35 | 23.1 | 0.2262 |
| 300–1000 | 1065 | 0.0421 | 4.25 | 6.9 | 0.1325 |
| >1000 | 1270 | **0.0090** | **4.15** | 1.4 | 0.0596 |

Three findings, only the first of which is in either document:

1. **Adamic–Adar is genuinely flat in max-degree** across 50 → 11,243 (3.76 → 4.15).
   B's central argument is vindicated.
2. **Adamic–Adar is *not* degree-neutral in min-degree: Spearman +0.578.** It is an
   unbounded sum over the intersection, so it rewards pairs where *both* endpoints have
   large neighbourhoods. That is a pro-hub gradient, in exactly the direction the earlier
   Optuna failure was not guarded against. B never measured this axis.
3. **Observed/expected under a configuration model is the worst candidate of the six**
   (Spearman −0.880 vs max-degree) — more degree-coupled than raw Jaccard. It should be
   removed from consideration as a primary objective.
4. **The overlap coefficient `|N(u) ∩ N(v)| / min(d_u, d_v)` is the only measure that is
   near-neutral on both axes** (−0.004 / −0.092 vs max-degree, −0.062 vs min-degree),
   is bounded in [0,1], and has a low zero rate (0.73 % of adjacent pairs have empty
   intersection). Neither document considered it.

### 4.3 Recommendation

**Optimise against Adamic–Adar, geometric mean over hops** (B's proposal) — it has the
literature grounding and it is the only candidate flat in max-degree — **but report the
overlap coefficient alongside it as a mandatory degree-neutrality cross-check**, and
treat a candidate that improves AA without improving overlap coefficient as unadopted.
AA's +0.578 min-degree coupling is a specific, measured gaming channel; a metric that is
neutral on both axes is the control for it.

- Direct consequence of measurement: A's Jaccard prescription is out; obs/exp is out;
  AA is flat in max-degree; overlap coefficient is flat in both.
- Hypothesis needing a test: that AA's min-degree coupling actually bites under
  optimisation. Falsifiable by a sweep in which AA and overlap coefficient move together;
  if they do, the cross-check can be demoted to a diagnostic.

**Both remain secondary to reading decoded paths.** No overlap metric in this table
would have *rejected* `Miles Davis → J. K. Simmons → Hank Levy → Justin Hurwitz →
Emma Stone → Daft Punk`: aggregated per path and compared against other routed paths in
the same artifact, it sits in the **top quartile on all three** (Jaccard 78th percentile,
overlap coefficient 72nd, Adamic–Adar 71st, of 120 random routed cosine paths; 84th /
79th / 82nd when the null is restricted to length-matched paths). Overlap-based
objectives are blind to the specific failure this project keeps hitting.

> **Amended.** The sentence this paragraph replaced read: *"Every metric in this table
> would have scored `Miles Davis → J. K. Simmons → …` well: that path is a chain of
> dense, mutually-overlapping micro-neighbourhoods."* The **operational conclusion is
> upheld and now quantified** (percentiles above). The **stated mechanism is overturned**:
> the path's hops are *not* densely overlapping — see §4.4. And the claim was true only
> at the *path-aggregate, within-artifact* level; read as a per-hop absolute value it is
> false, which matters because a per-hop threshold is what a rejection screen needs.

### 4.4 What "scores well" means — the level matters, and §4.3 conflated four of them

Added on amendment, after Task 5's bad-path calibration measured per-hop Jaccard on this
same path and reported values that appeared to contradict §4.3. Both readings turn out to
be measuring different quantities. All figures below re-derived from the artifacts.

**Per-hop values on the known-bad path** (`graph-75k-cosine.bin`, routed with production
`ApiConfig`; `CN` excludes the two endpoints, per `evaluation.py`):

| hop | d_u / d_v | CN | Jaccard | degree bound `min/max` | J / bound | overlap coef | Adamic–Adar |
|---|---|---|---|---|---|---|---|
| Miles Davis → J. K. Simmons | 337 / 17 | 3 | **0.0085** | 0.050 | 0.169 | 0.1765 | 0.55 |
| J. K. Simmons → Hank Levy | 17 / 46 | 5 | **0.0862** | 0.370 | 0.233 | 0.2941 | 1.18 |
| Hank Levy → Justin Hurwitz | 46 / 96 | 9 | **0.0677** | 0.479 | 0.141 | 0.1957 | 2.85 |
| Justin Hurwitz → Emma Stone | 96 / 51 | 13 | **0.0970** | 0.531 | 0.183 | 0.2549 | 2.99 |
| Emma Stone → Daft Punk | 51 / 128 | 13 | 0.0783 | 0.398 | 0.197 | 0.2549 | 2.10 |
| **path geometric mean** | | | **0.0520** | | 0.182 | **0.2311** | **1.635** |

Task 5's interior per-hop figures (0.086 / 0.068 / 0.097) **reproduce exactly**.

Four different questions, four different answers:

| Question asked of the bad path | Reference | Answer |
|---|---|---|
| **(a)** Per-hop absolute value, vs a fixed threshold | `_MICRO_CLUSTER_JACCARD = 0.5` | **0.068–0.097 — far below.** No high-Jaccard screen fires. |
| **(b)** Per-hop, vs adjacent pairs in **its own** artifact | cosine adjacent-pair sample, n=6,000, seed 7: median J **0.0948**, OC **0.3333** | **Dead median.** Interior hops at percentiles **47 / 40 / 51** on J, **43 / 27 / 37** on OC. |
| **(c)** Per-hop, vs **degree-matched** adjacent pairs (min- and max-degree both within 2×) | matched medians J 0.157 / 0.143 / 0.143 | **Below median** — percentiles **25 / 23 / 34** on J, **24 / 25 / 35** on OC. |
| **(d)** Path aggregate (geometric mean over hops, as `path_metrics` computes it), vs other routed paths in the same artifact | 120 random routed cosine paths, seed 42: median J **0.0207**, OC **0.1318**, AA **0.789** | **Top quartile: percentiles 78 / 72 / 71** (length-matched, n=57: **84 / 79 / 82**). |

**(d) is the level the evaluation harness operates at**, because `path_metrics` reports
`geometric_mean` over hops. So §4.3's operational claim stands: none of the three overlap
objectives would have flagged this path, and all three rank it above the median routed
path in its own graph. **(a)–(c) are the levels a rejection screen operates at**, and
there §4.3's phrasing is simply wrong.

**Why (d) is high while (b) and (c) are not.** Not because the cast hops are good, but
because the *baseline* is bad: the median random routed cosine path has path-level
Jaccard 0.0207 (0.0120 length-matched), i.e. typical cosine routing is worse than the
cast chain. A metric that ranks a known-bad path above the median only tells you the
median is also bad. This is the same failure mode as reading a raw hub-traversal rate
without a null (§5.3), one level up.

**The "dense micro-neighbourhoods" mechanism is overturned.** The interior hops share
**5, 9 and 13** common neighbours respectively — overlap coefficients 0.196–0.294 against
a cosine adjacent-pair median of **0.3333**. In neighbour-set terms the *La La Land* cast
is not a dense clique at all; it is a **loose** set of nodes. What binds it is the
*similarity scores* (three consecutive edges at ≥0.996, produced by the p99 clip, §2.2 /
§2.5), which no neighbour-set metric can see. The correct statement is not "overlap
metrics score dense junk highly" but **"overlap metrics are blind to a defect that lives
entirely in the score channel."** That is a stronger and more general claim.

**Task 5's proposed mechanism — degree-ratio suppression — is not supported for the
interior hops.** Its argument was that `jaccard ≤ min(d)/max(d)` and the cast members
have very uneven degrees. Measured, their bounds are **0.370 / 0.479 / 0.531**, against a
cosine adjacent-pair **median bound of 0.4237** — entirely typical, not uneven. Dividing
the bound out leaves J/bound = **0.233 / 0.141 / 0.183** against a graph median J/bound
of **0.2544**, still at or below median. Degree-ratio suppression explains only the
*entry* hop `Miles Davis → J. K. Simmons` (bound 0.050, J 0.0085, percentile 8). The
degree-ratio bound is a real property of Jaccard (§4.1 stands) but it is not what defeats
the micro-cluster screen. **What defeats the screen is that the clique is not dense.**

**A defect in the calibration set itself.** Task 5's eight "known-good" paths are routed
on `graph-75k-v3.bin` and include `Miles Davis → Ella Fitzgerald → Dean Martin → Mariah
Carey → Justin Timberlake → Daft Punk` — which **§0 of this document identifies as the
other face of the same defect** (five consecutive hops at score 1.000). Measured, it is
the highest-overlap path in either set: path-level Jaccard **0.1592**, the **98th
percentile** of 120 random v3 paths (**100th** length-matched), and its
`Ella Fitzgerald ~ Dean Martin` interior pair is **0.3723**. The single "false positive"
in Task 5's sweep at `run=2, jaccard ∈ {0.35, 0.30}` is therefore a **true positive on a
path the calibration set mislabelled as good**. This does not rescue the screen — the bad
path still never fires at any threshold above 0.097 — but it means the sweep's
false-positive column is not trustworthy as reported, and the screen should be
re-calibrated against a good set that excludes ceiling-chained paths.

**Consequences.**

1. Task 5's headline — *no Jaccard threshold separates the known-bad path from the
   known-good set* — is **upheld**, for a corrected reason.
2. Swapping the micro-cluster signal from `jaccard` to `overlap_coefficient` (Task 5's
   concern 2) **would not fix it**: the bad path's interior OC is 0.196–0.294, *below*
   the graph median 0.3333. Measured, not hypothesised. Do not make that change expecting
   it to work.
3. A screen that catches this path must read the **score channel**, not the topology —
   e.g. a run of consecutive hops at or near the similarity ceiling. `ceiling_hops`
   already exists in `PathMetrics` and reads 3/5 = 0.60 on this path against a cosine
   mean of 0.301 (§2.5). **Confidence: medium** — proposed from the mechanism above and
   from `ceiling_hops` being the one metric that separates here; it is not yet swept
   against a clean good set, and it is a within-artifact signal that will read ~0 once
   the rescale of §7.1 removes the ceiling tie-mass. It is a diagnostic for the *current*
   defect, not a durable quality screen.
4. Nothing here changes §4.3's objective recommendation (AA primary, OC as
   degree-neutrality guard). Both remain blind to this failure; that was always the
   reason for a separate screen.

---

## 5. Also settled

### 5.1 A's `+0.725` score/degree correlation: unreproducible

`graph-75k-v3.bin`, all 4,102,014 edges:

| Correlation | v3 | v2 | cosine | graph-75k |
|---|---|---|---|---|
| Pearson(score, log dst-degree) | **+0.287** | +0.248 | −0.405 | −0.125 |
| Pearson(score, log max-endpoint-degree) | +0.259 | +0.239 | −0.497 | −0.172 |
| Spearman(score, log dst-degree) | +0.380 | — | −0.261 | −0.077 |
| Node-level Spearman(mean out-score, degree) | +0.706 | +0.711 | — | −0.522 |

**+0.725 does not appear on any artifact.** The closest reproducible analogue is the
node-level Spearman of mean out-score against degree, **+0.706** on v3 — a different
quantity from what §5.1 describes. The edge-level figure §5.1 claims is +0.26 to +0.29,
and its **sign is not stable across artifacts** (−0.41 under cosine). Treat A §5.1's
correlation as retracted.

### 5.2 …and it is substantially tautological

Popularity is defined at `pipeline.py:124-125` as the sum of the very scores under
correlation. Measured on v3: Spearman(sum of a node's out-scores, its degree) =
**+0.987**; Pearson(popularity, log degree) = **+0.838**; Spearman(popularity, degree) =
**+0.861**. A positive score/popularity/degree association is the *null expectation*
here, not evidence of a defect. Spec §A4 is right to demand a non-circular check.

### 5.3 The null model: A's numbers reproduce, A's inference does not

`graph-75k-v3.bin`, 40 seeded random pairs, production weights, top-1 % degree
threshold = 363:

| Router | mean len | hubfrac | degree-biased walk | enrichment | binary hub_traversed | chance at that length | mean max interior degree |
|---|---|---|---|---|---|---|---|
| **FULL cost function** | 7.4 | **0.7054** | 0.1928 | **3.66×** | 0.950 | **0.642** | **2100** |
| similarity-only | 7.2 | 0.5645 | 0.1798 | 3.14× | 0.975 | 0.629 | 4160 |
| plain BFS | 4.3 | 0.5146 | 0.1917 | 2.68× | 0.950 | 0.350 | 4809 |

Analytic degree-biased (stationary) hub probability = **0.1723**; uniform-node = 0.0100.

- **A §5.2 upheld in full.** The binary metric reads **0.642 by chance** at length 7.4
  under the degree-biased null — A said "61–68 % at lengths 7–8". It measures path
  length, not hub-seeking. Replace it with `hubfrac`.
- **A's null baseline upheld:** 0.1723 analytic vs A's 0.172. Enrichment 3.66–4.09×
  vs A's 3.7×. Max interior degree 2100 vs A's 2118. These reproduce.
- **A §5.1's inference — "hub-seeking is caused by the scoring" — is overturned.**
  Plain BFS reads *no scores at all* and is still **2.68×** enriched over the same null;
  similarity-only is 3.14×. Enrichment over a degree-biased random walk is a property of
  *shortest-path routing on a hub-dense small world*, not of the scoring. A random walk
  is the wrong null for a routing question: any shortest-path process concentrates on
  hubs harder than a diffusive one, because hubs are what make paths short.
- **Worse for A's reading:** on the continuous metric the full cost function is the
  *least* hub-seeking of the three — max interior degree 2100 (FULL) < 4160 (sim-only) <
  4809 (BFS). Turning the popularity terms off makes hub-seeking worse.
- **Findings §2's struck-through conclusion is therefore partially reinstated.** §2 was
  right that a scoring-free router hub-seeks comparably, and right that this is the
  relevant control; it was wrong only in reading a raw rate rather than an enrichment.
  A struck it out entirely; that strike-through goes too far.
- Still **unmeasured**: the configuration-model rewire (spec §A3). The degree-biased walk
  and the scoring-free routers are cheap and were run; the rewire was not, and it remains
  the cleanest null for "is it topology or scoring".

### 5.4 `w_floor` is a no-op — A §5.3 upheld

20 seeded random pairs on v3: `find_path` with `w_floor = 1.0` and `w_floor = 0.0`
returns the **identical path 20/20**, and **0/20** paths have any interior node below
`floor = min(pop_source, pop_target)`. The floor never binds. **Delete `w_floor` and
`floor_relax_*`.**

### 5.5 …but A's product corollary is wrong

A §5.3: *"the two bypass signals are behaviourally identical at runtime — the app's
signature feature does not currently do what it claims."* **Overturned.** `dislike`
additionally builds `avoidance_map` (`pathfinding.py:82`, `w_avoid = 1.0`,
`avoid_radius = 2`, `avoid_penalty = 0.5`), which `known` does not. The two signals do
differ; what is dead is only the *floor-relaxation* channel that was supposed to make
`known` push harder into obscurity. The correct statement: **`known` currently degrades
to a plain hard exclusion.** That is a real bug and should be fixed, but the signature
feature is not wholly inert.

---

## 6. Upholds / overturns / unresolved

| # | Prior claim | Where | Verdict |
|---|---|---|---|
| 1 | Damping before `log1p` degenerates log into linear | findings §5.4 | **Upheld as a live hazard in current code** (log ≈ linear at `d=0.5`) |
| 2 | …and that ordering caused the cosine failure | findings §5.4 | **Overturned** — `graph-75k-cosine.bin` was built by `284366c`, which had no `log1p` |
| 3 | Rescaling is monotone, cannot invert a ranking | spec §1.2 | **Upheld** |
| 4 | The real defect is the p99 clip; 34,696 / 719 vs 27,808 / 9 | spec §1.2 | **Upheld**, reproduces exactly |
| 5 | Findings §4's cosine failure "does not reproduce in either artifact" | spec §1.1 | **Overturned** — the film-soundtrack path reproduces verbatim on `graph-75k-cosine.bin` |
| 6 | "A junk edge scored 0.148 against 0.022, 6.6× backwards" | findings §4 | **Overturned** — 0.022 is real (cosine Miles–Getz = 0.022257); 0.148 has no referent; max cosine on any Miles edge is 0.0497 |
| 7 | "2357 vs 277 on the measured examples" | commit `fff422e` | **Overturned** — 2357 correct, actual cooc for the junk edge is **14**, not 277 |
| 8 | Under cosine, Stan Getz outscores the junk edge 24× correctly | spec §1.1 | **Upheld** |
| 9 | `− 2·log(median_mass)` is inert under a rank rescale | spec §B4 | **Upheld** — rank-identical, residual 3.6e-15 |
| 10 | The centring term is part of the fix | findings §5.4 | **Upheld for the wrong reason** — mandatory under the clip+clamp (without it 78.7–100 % of edges clamp to 0); inert otherwise |
| 11 | The clamp at 0 mirrors the ceiling tie-mass defect | spec §B4 | **Upheld** — 30.62 % of edges tie at the floor at `d=0.75` |
| 12 | Sweep grid `R ∈ {clip, percentile} × d ∈ {0,0.5,0.75,1.0}` | spec §B5 | **Overturned as specified** — 3 of 8 cells build a degenerate graph once centring is dropped |
| 13 | Neighbour-set Jaccard is score-independent, "the one to optimise against" | findings §5.2 | **Overturned** — Pearson −0.639 / Spearman −0.730 vs max-degree |
| 14 | `corr(log Jaccard, log maxdeg) = −0.655`; median 0.4545 → 0.0087 | spec §B1 | **Upheld** (−0.639; 0.4000 → 0.0090) |
| 15 | Damping changes the adjacency the metric is computed on (cap after damping) | spec §B1 | **Upheld** — E 4,102,014 → 3,582,502; maxdeg 11,243 → 3,166 |
| 16 | Adamic–Adar is the right primary objective | spec §B1 | **Upheld with a caveat** — flat in max-degree (+0.110) but Spearman +0.578 vs min-degree, an unmeasured pro-hub channel |
| 17 | Observed/expected under a configuration model is a sound alternative | task framing | **Overturned** — Spearman −0.880 vs max-degree, worse than Jaccard |
| 18 | `corr(score, endpoint degree) = +0.725` | findings §5.1 | **Overturned** — +0.259 to +0.287 on v3, sign unstable (−0.497 on cosine); closest analogue +0.706 is a different quantity |
| 19 | Hub-seeking is caused by the scoring | findings §5.1 | **Overturned** — score-free BFS is 2.68× enriched on the same null; FULL has the *lowest* max interior degree of the three routers |
| 20 | Degree-biased null hubfrac = 0.172; enrichment 3.7× | findings §5.1 | **Upheld as measurements** (0.1723; 3.66–4.09×) — but they do not support #19 |
| 21 | The binary hub-traversal metric reads 61–68 % by chance | findings §5.2 | **Upheld** — 0.642 at length 7.4 |
| 22 | Findings §2: hub-traversal is topological (struck through) | findings §2 / §5 | **Partially reinstated** — right about the control, wrong to read a raw rate |
| 23 | `w_floor` is a provable no-op | findings §5.3 | **Upheld** — 20/20 identical paths, 0/20 dip below the floor |
| 24 | The two bypass signals are behaviourally identical | findings §5.3 | **Overturned** — `dislike` still applies `avoidance_map`; only `known` degrades to a hard exclusion |
| 25 | Entity filter is not a quality lever (7 nodes, max degree 218) | spec §1.3 | **Not re-measured — unresolved** |
| 26 | Configuration-model rewire null | spec §A3 | **Unmeasured** — remains the cleanest test for #19/#22 |
| 27 | Projected `hubfrac 0.641 → 0.231`, `max interior degree 2118 → 913`, `Jaccard 0.0184 → 0.0346` under `d≈0.25` | findings §5.4 | **Unresolved** — projections, no `d=0.25` artifact exists; and per §2.5 no `d` fixes the clip defect |
| 28 | §4.3: "every overlap metric would have scored the *La La Land* path well" | this doc §4.3 | **Upheld at the path-aggregate level, overstated as written** — path geomeans rank at percentiles 78 (J) / 72 (OC) / 71 (AA) of 120 random routed cosine paths, so none would reject it; but per hop the values are 0.068–0.097, at the cosine adjacent-pair median (0.0948) and *below* it degree-matched (pct 23–34). §4.3 now states the level (§4.4) |
| 29 | §4.3: "…that path is a chain of dense, mutually-overlapping micro-neighbourhoods" | this doc §4.3 | **Overturned** — interior hops share only 5 / 9 / 13 common neighbours; OC 0.196–0.294 vs a cosine median of 0.3333. It is a *loose* set bound by ceiling-clipped scores, not a dense clique (§4.4) |
| 30 | Task 5: Jaccard's degree-ratio bound suppresses the cast clique's overlap | task-5 report | **Overturned for the interior hops** — their bounds are 0.370 / 0.479 / 0.531 vs a graph median of 0.4237; J/bound 0.141–0.233 vs median 0.2544. True only of the entry hop (bound 0.050). Task 5's *conclusion* (no threshold separates) is **upheld** (§4.4) |
| 31 | Task 5: swapping the micro-cluster signal to the overlap coefficient would fix it | task-5 report, concern 2 | **Overturned** — the bad path's interior OC (0.196–0.294) is below the cosine median (0.3333); the signal would still run the wrong way (§4.4) |
| 32 | Task 5's eight "known-good" calibration paths are good | task-5 report | **Overturned in part** — one of them (`Miles Davis → Ella Fitzgerald → … → Daft Punk`) is the ceiling-chained defect of §0; it is the highest-overlap path measured (path J 0.1592, 98th pct of v3 paths) and is the sweep's sole low-threshold "false positive". Recalibrate against a good set that excludes ceiling-chained paths |
| 33 | A consecutive-ceiling-hop run would catch this path where overlap cannot | §4.4, new | **Unresolved — hypothesis** — `ceiling_hops` reads 0.60 on the bad path vs a cosine mean of 0.301 (§2.5), but it has not been swept against a clean good set and it becomes uninformative once §7.1's rescale removes the ceiling tie-mass |

---

## 7. What follows for Phase 2

Ranked by strength of evidence.

1. **Fix the rescale before anything else, and rebuild the control.** Direct consequence
   of §2.2 and §2.5: 30–82 % of routed hops currently cost zero similarity. A percentile-
   rank rescale removes the ceiling tie-mass; dropping the clamp removes the floor
   tie-mass. Until this is done, no `d` comparison is interpretable, including the one
   that rejected cosine. **Confidence: high.**
2. **Do not run `clip × d > 0` cells without the centring term.** Direct consequence of
   §3.2: they build a null graph. **Confidence: certain** (measured 99.98 % clamped).
3. **Delete `w_floor` and `floor_relax_*`; give `known` a real behaviour.** Direct
   consequence of §5.4/§5.5. **Confidence: high.**
4. **Replace `hub_traversed` with `hubfrac`, reported against the 0.1723 degree-biased
   baseline *and* against a score-free BFS control.** Direct consequence of §5.3: the
   walk null alone licenses the wrong inference. **Confidence: high.**
5. **Primary objective: Adamic–Adar (geometric mean over hops), with the overlap
   coefficient as a mandatory co-reported degree-neutrality check.** §4.3.
   **Confidence: medium** — AA's flatness is measured, its behaviour under optimisation
   is not.
6. **Run the configuration-model rewire** (spec §A3) to close #19/#22 properly.
   **Confidence: n/a — unmeasured, and it is the one cheap experiment still outstanding.**
7. **Hypothesis, not a finding:** once the rescale is fixed, `d` may matter far less than
   either document assumes, because both observed failure modes were clip artefacts. Test
   by sweeping `d` only under the rank rescale. Falsified if rank-rescaled `d = 0` and
   `d = 0.5` still produce qualitatively different path failures.
8. **Do not report `badpath.screen_path`'s count as evidence of path quality, and do not
   fix it by swapping `jaccard` for `overlap_coefficient`.** Direct consequence of §4.4:
   the bad path's interior overlap is *below* the graph median on both metrics, so both
   signals run the wrong way. Rebuild its calibration set first (it currently contains a
   ceiling-chained path labelled good, #32), then calibrate a score-channel signal.
   **Confidence: high on the negative; medium on the replacement (#33).**

---

## 8. Reproduction

Probe scripts were throwaway (run from a scratch directory, not committed). Each figure
above is reproduced by the snippet below; all run as

```bash
cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python <probe>.py
```

with `sys.path.insert(0, "src")` and `from artistpath_api.graph_store import GraphStore`.
`scipy` is not installed in the api venv; Spearman was computed as Pearson over
`np.argsort(np.argsort(x))`.

**§1 provenance.** `v2 = GraphStore.load(...); v3 = GraphStore.load(...)`;
`np.array_equal(v2.neighbours, v3.neighbours)`;
`np.abs(np.minimum(1, np.log1p(v2.scores*1627)/np.log1p(1627)) - v3.scores).max()`.
Rescale of the cosine artifact identified by `0.022257/0.100074 == 0.2224`.

**§2.2 saturation.** `deg = np.diff(s.offsets); dst_deg = deg[s.neighbours];
sat = s.scores >= 1-1e-9; sat.sum(); np.median(dst_deg[sat]); np.median(deg)`.

**§2.3 / §2.5 paths.** `find_path(store, a, b, [], ApiConfig())` with per-hop rank
computed by sorting the source's CSR row by descending score. Artist ids resolved by
first-match on `store.names`.

**§2.4 archive values.** Parse all 75,000 files under
`builder/scratch/graph-archive/similar/listenbrainz/*.json` with the pipeline's own
`_rows`/`parse` logic (377 s); `mass[m] = sum(scores)`;
`cosine(a,b) = max(cooc_fwd, cooc_rev)/sqrt(mass_a*mass_b)`.

**§3 clamp counts.** Over all in-`known` pairs:
`L = np.log1p(cooc); raw = L - d*(log_ma + log_mb - 2*np.log(1229)); (raw < 0).mean()`.
Rank-identity checked with `np.argsort(np.argsort(·, kind='stable'), kind='stable')`.

**§4 overlap metrics.** 6,000 edges sampled with `default_rng(7)`;
`np.intersect1d` over CSR rows; `AA = (1/np.log(np.maximum(deg[inter],2))).sum()`;
`OE = CN / (deg_u*deg_v*kappa/2m)` with `kappa = <k(k-1)>/<k> = 429.2`.

**§4.4 levels.** Per-hop values use `jaccard`, `overlap_coefficient`, `adamic_adar` and
`common_neighbours` from `api/src/artistpath_api/evaluation.py` directly, so the figures
are exactly what the harness and `badpath.py` compute. Adjacent-pair reference: 6,000
edges per artifact with `default_rng(7)`, sampling edge index `k` uniformly and
recovering the source with `np.repeat(np.arange(N), np.diff(offsets))`. Degree-matched
comparison: adjacent pairs whose min- *and* max-endpoint degree are both within a factor
of 2 of the target hop's (n = 554 / 3,323 / 3,325 for the three interior hops). Path-level
null: 120 uniformly random node pairs with `default_rng(42)`, routed by
`find_path(store, a, b, [], ApiConfig())`, paths of length < 3 discarded, aggregated with
`geometric_mean` exactly as `path_metrics` does; the length-matched sub-null keeps paths
within ±1 node of the target's length (n = 57 cosine, 58 v3). `J / bound` uses
`bound = min(d_u, d_v) / max(d_u, d_v)`, the structural ceiling on Jaccard.

**§5.1–5.2 correlations.** Edge-level over all E with
`src = np.repeat(np.arange(N), deg)`; node-level with
`np.add.reduceat(scores, offsets[:-1])`.

**§5.3 nulls.** 40 pairs from `default_rng(42)`; analytic
`p_deg = deg[deg>=thr].sum()/deg.sum()`; empirical null = uniform-random-neighbour walk
of matched interior length from the source; chance binary rate `1-(1-p_deg)**(L-2)`.

**§5.4 `w_floor`.** `dataclasses.replace(cfg, w_floor=0.0)`, compare returned paths.

---

## 9. Meta-lesson this record adds

Findings §3–§4 established that metrics need eyeballs and eyeballs need metrics. §5 added
that a metric without a null model measures nothing. This adjudication adds a fourth:
**a null model can also be the wrong null.** A built the control §2 lacked, got the right
number (0.172), and drew a conclusion the control does not support, because a
degree-biased random walk is not the right comparison for a shortest-path router — the
scoring-free router that §2 already had was closer to the right control all along.

And a fifth, more mundane: **record which commit built each artifact.** Half the
disagreement between these two documents dissolves once you know that `graph-75k-cosine.bin`
and `graph-75k-v3.bin` differ in two factors, not one.

And a sixth, added on the §4.4 amendment: **"scores well" is not a proposition until you
name the reference class.** §4.3 and Task 5 measured the same path with the same function
and reached opposite verdicts, because one aggregated per path against other paths in the
same artifact and the other read a per-hop value against a fixed threshold. Both numbers
were right. When a metric claim is contested, state the level (per-hop / per-path), the
reference (absolute / within-artifact / degree-conditioned), and the null, before
arguing about the value.
