# Phase 2 — Path Quality: Design

**Date:** 2026-07-21
**Gate:** 1 (personal use)
**Status:** approved design, not yet planned
**Supersedes:** the Phase 2 bullet list in `../plans/2026-07-21-alpha-rollout-roadmap.md`.
The roadmap remains the plan of record for gate structure and for Phases 1 and 3–7;
this spec replaces only its Phase 2 content.

---

## 1. Why this phase is not what the roadmap said

The roadmap's Phase 2 assumed three things. Two are now measured to be wrong, and the
third is not the defect it was believed to be.

### 1.1 The rejected graph is better than the adopted one

Commit `fff422e` set `BuilderConfig.similarity_damping = 0.0` and recorded that full
cosine (`d = 0.5`) "over-corrects". Both artifacts still exist in `builder/scratch/`.
Miles Davis' top-12 neighbours, read directly from them:

| `graph-75k-v3.bin` — d = 0.0, **current default** | `graph-75k-cosine.bin` — d = 0.5, **rejected** |
|---|---|
| Frank Sinatra, Chet Baker, Herbie Hancock, Nina Simone, Duke Ellington, Sonny Rollins, Ella Fitzgerald, **Led Zeppelin**, **Bob Dylan**, The Dave Brubeck Quartet, Bill Evans, **Pink Floyd** — all tied at exactly 1.0000 | Miles Davis Quintet .496, John Coltrane .403, Charles Mingus .295, Herbie Hancock .284, Charlie Parker .275, The Dave Brubeck Quartet .269, Thelonious Monk .267, Chet Baker .255, Duke Ellington .248, Bill Evans .242, Sonny Rollins .237, Gil Evans .236 |

The rejected ranking is clean jazz. The adopted one ties Led Zeppelin and Pink Floyd
with John Coltrane at maximum similarity to Miles Davis.

The specific evidence in findings §4 — *"a junk edge scored 0.148 against 0.022 for
Miles Davis → Stan Getz, 6.6× backwards"* — **does not reproduce in either built
artifact**:

| | J. K. Simmons | Stan Getz |
|---|---|---|
| v3 (d = 0.0) | rank 509 / 566, score 0.366 | rank 14 / 566, score 1.000 |
| cosine (d = 0.5) | rank 327 / 337, score 0.0094 | rank 15 / 337, score 0.222 |

Under cosine, Stan Getz outscores the junk edge **24× in the correct direction**.
`Justin Hurwitz` and `Emma Stone` are neighbours of Miles Davis in neither graph.
Findings §4 was measured on intermediates, not on the built graph.

### 1.2 The real defect is the p99 clip, not the linear/log ordering

`builder/src/artistpath_builder/pipeline.py:110-122` rescales scores as
`min(1.0, log1p(value) / log1p(p99))`. By construction ~1% of edges saturate at
exactly 1.0. Measured:

| | edges at exactly 1.0 | median out-degree of those edges' **destinations** |
|---|---|---|
| v3 (d = 0.0) | 34,696 / 4,102,014 (0.85 %) | **719** |
| cosine (d = 0.5) | 27,808 / 3,582,502 (0.78 %) | **9** |

Graph median degree is 49 in both. So in the production graph, ~35k edges have
`w_sim·(1 − similarity) = 0` — similarity is *free* — and that free tie-mass points at
destinations with a median degree 14.7× the graph median. Dijkstra breaks the resulting
tie on `w_jump·|Δpop| + w_hop` alone. **This is a direct mechanical route into the hub
core, and it is an artefact of percentile clipping, not of damping.**

Roadmap C4 attributed the cosine failure to damping being applied before `log1p`
("degenerating log scaling into linear"). The compression is real — cosine's score
p50 is 0.075 against v3's 0.488 — but rescaling is **monotone**, so it cannot invert a
ranking, and cosine's ranking was never inverted. The ordering story identified a real
defect and drew the wrong conclusion from it.

### 1.3 The entity filter is not a quality lever

Exactly **7** special-purpose entities exist in the graph, all identified by
`"Special Purpose Artist"` in the disambiguation field: `[unknown]`, `[traditional]`,
`[no artist]`, `[anonymous]`, `[theatre]`, `[dialogue]`, `[Disney]`. Maximum out-degree
among them is **218**, against a top-1% threshold of 363. They are not hubs and removing
them will not move path quality.

It is still worth doing for correctness, and it must be done by **disambiguation match,
never by name**. There are 22 bracket-named nodes in the graph; 7 are special-purpose
and **15 are real bands** that a name-based `[...]` filter would delete, including
`[Alexandros]`, `[dunkelbunt]`, `[:SITD:]`, `[re:jazz]`, `[ingenting]`, `[spunge]`,
`[die!]`, `[bsd.u]`, `[ocean jams]` and `[The] Slowest Runner [In All the World]`.
The full 22 are enumerated in the unit-test fixture (§7).

### 1.4 There is an unresolved contradiction in the committed record

- Findings §2 concluded hub-traversal is **topological** — BFS and similarity-only
  routers do it too, so no scoring change will fix it.
- Roadmap C4 concluded hub-seeking is **caused by the scoring** — score correlates
  +0.725 with endpoint degree.

Both are committed as conclusions. They disagree. No amount of sweeping damping values
resolves this; a null model does. Settling it is a precondition for interpreting any
sweep result, so it belongs in Step A.

### 1.5 The numbers driving the plan are not in version control

The +0.725 correlation, the 0.641-vs-0.172 hub enrichment (3.7×), and the projected
0.641 → 0.231 improvement exist only in prose. The roadmap says, verbatim, *"Fix
(measured in memory)"*. These figures currently pre-authorise an adoption criterion.
Given §1.1 showed a recorded measurement that the artifacts contradict, none of them
can be trusted until re-derived in committed code.

---

## 2. Goal

Make path quality **judgeable**, then use that to fix hub-seeking.

The deliverable is an adopted 75k graph with recorded, reproducible evidence, plus the
permanent tooling to make the next such decision cheaply. **"No candidate beats the
control, keep the current scoring"** is an acceptable and pre-authorised outcome.

Non-goal: tuning the API cost weights. They stay fixed so the scoring is the only
deliberate variable (see §6.1 for the one place that is not automatically true).

---

## 3. Structure: two steps with a gate

Step A is analysis over artifacts that already exist and involves **no graph builds**.
It is cheap and it can collapse Step B, so it runs first and its result sets Step B's
parameters.

```
Step A  adjudicate ──gate──▶  Step B  sweep ──▶ adopt (or keep control)
```

---

## 4. Step A — Adjudication

### A1. Path-export tool

**New:** `api/eval/export_paths.py`. Emits one self-contained HTML file.

- Rows: panel artist pairs. Columns: graph artifacts under comparison.
- Each cell: the path, and per hop — the destination's **rank within the source
  artist's neighbour list**, the edge score, and the destination's out-degree. Hubs
  marked.
- Header: the per-artifact diagnostics table from §B7.

**Rank is mandatory, not decorative.** The v3 defect in §1.1 is invisible in scores
(twelve consecutive `1.0000`s) and obvious in rank. Any comparison tool that shows only
scores would have missed it, exactly as the original review did.

This tool is built in Step A because A2 needs it, and it is a permanent debugging
asset — it is the roadmap's "path export" item, delivered early.

### A2. Retract or substantiate findings §4

Read ~15 paths across `graph-75k-v3.bin` and `graph-75k-cosine.bin` using A1. Then
correct the record in all three places the §4 conclusion is load-bearing:

1. `builder/src/artistpath_builder/config.py:38-46` — the comment justifying
   `similarity_damping = 0.0` in production cites §4 directly.
2. `docs/superpowers/findings/2026-07-21-architecture-review-and-path-baseline.md` §4.
3. `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` C4.

Correcting the record is a deliverable of this step, not a side effect. A wrong finding
that stays committed will be re-used.

### A3. Configuration-model null

Rewire the graph preserving the exact degree sequence, randomising edge endpoints;
re-run the router; measure hub fraction. Compare against the observed graph.

- If the rewired graph hub-seeks comparably → hub-seeking is **topological** (findings
  §2 is right) and scoring changes will not fix it.
- If it does not → hub-seeking is **scoring-caused** (roadmap C4 is right).

This adjudicates §1.4. Report both this null and a degree-biased random walk of matched
length; they answer different questions and both are cheap.

### A4. Re-derive the uncommitted numbers

In committed, tested code: the score/degree correlation, hub fraction, and the null
baselines. Plus one **non-circular** check, because correlating similarity with degree
is close to tautological — popularity is defined at `pipeline.py:124-125` as a sum of
the very scores being correlated, and `E[cooc(a,b)] ∝ mass(a)·mass(b)` holds under
independence for any co-occurrence process, so a positive correlation is the *null*
expectation rather than evidence.

The non-circular check: correlate raw co-occurrence against ListenBrainz sitewide
listener counts. `BuilderConfig.sitewide_artists_url` already exists.

### Gate

Step A answers: **is damping the lever, and in which direction?** Its output sets
Step B's grid. If A shows the answer is already determined by the existing artifacts,
Step B narrows to a confirmation build rather than a sweep.

---

## 5. Step B — Narrow sweep

### B1. Metrics (`api/src/artistpath_api/evaluation.py`)

**Primary objective: Adamic–Adar**, `Σ_{w ∈ N(u) ∩ N(v)} 1 / log deg(w)`, over each
adjacent path pair, aggregated as the **geometric mean over hops**.

Why not raw Jaccard, which the earlier design proposed as primary: it is not an
independent check. Measured over 6,000 sampled adjacent pairs in `graph-75k-v3.bin`,
`corr(log Jaccard, log max-degree) = −0.655`, with median Jaccard falling 0.4545 →
0.0087 across degree buckets — a 52× swing driven by degree alone. It is also
structurally bounded: `J ≤ min(d_u, d_v) / max(d_u, d_v)`, so a degree-50 artist
adjacent to Radiohead (degree 11,243) cannot exceed J = 0.0044 no matter how musically
related. Bottleneck Jaccard is therefore a near-deterministic monotone function of
`max_interior_degree`, which `PathMetrics` already reports. It restates the hub metric
rather than corroborating it.

Worse, it is gameable in the previously-observed direction: bottleneck Jaccard is
*maximised* by routing through small, tight, mutually-overlapping neighbourhoods —
a film cast list, a label roster — which is precisely the failure mode of the earlier
tuning run.

Adamic–Adar discounts hub-mediated overlap and is the standard link-prediction answer
(Adamic & Adar 2003; Liben-Nowell & Kleinberg 2007).

Also required:

- **Geometric mean, not bottleneck-min.** Over 7–9 hops a min is dominated by one noisy
  node. Measured zero-rate for common-neighbour overlap is 0.7 %, so log-space
  aggregation is safe with a small epsilon.
- **`hubfrac`** replaces the binary `hub_traversed`, which is 61–68 % by chance at
  length 7–8 and measures path length rather than hub-seeking. The hub set is **frozen
  by MBID** from the control build — the per-graph top-1 % threshold itself moves (363
  in v3, 278 in cosine), so a variant could otherwise "improve" purely by compressing
  its degree distribution. Each variant's own threshold is reported as a diagnostic.
- **Raw Jaccard retained as a diagnostic**, reported together with its correlation to
  `max_interior_degree` so its redundancy stays visible in the results table.
- Existing `length`, `max_interior_degree`, `mean_interior_pop`, `bottleneck_sim`,
  `mean_sim` retained as diagnostics.

**Implementation note:** compute set intersection/union with `np.intersect1d` over the
CSR rows, which `graph.py` already sorts by destination id — O(d_u + d_v) with no Python
sets. `evaluation.py:34-39`'s `edge_score` currently linear-scans a neighbour list per
hop, which for a degree-11,243 hub is slow; fix it in the same pass.

Define explicitly in code and docstring whether the two endpoints are excluded from both
neighbour sets. For an adjacent pair, `u ∈ N(v)` and `v ∈ N(u)` always hold while
`u ∉ N(u)`, so endpoints land in the union but never the intersection — a small
downward bias that itself varies with degree.

### B2. Panel (`api/eval/panel.json`)

Frozen, committed, **MBID-keyed**. The existing panel is generated from random *node
indices* under a fixed seed; node indices shift when the node set changes, so it can
silently compare different artists across variants.

Strata:

| Stratum | n | Purpose |
|---|---|---|
| Random | 50 | Broad coverage |
| Obscure–obscure (both endpoints degree ≤ 5) | 50 | The discovery case |
| **Popularity-weighted** | 30 | The real query distribution |
| Hand-picked known-bad pairs | 8 | Qualitative only, never aggregated |

The three aggregated strata total **130 pairs**. The popularity-weighted stratum is new
and necessary: uniform sampling over 75k nodes is dominated by the obscure tail, so both
existing strata are effectively obscure and the panel never tests the
mainstream→mainstream case users actually query.

The hand-picked stratum is **never pooled into aggregates**. It was adversarially
selected on the d = 0 graph, so regression to the mean guarantees it improves under any
variant.

**Held-out slice:** 30 of the 130 aggregated pairs — 12 random, 12 obscure, 6
popularity-weighted, chosen once by seeded draw and flagged `"held_out": true` in
`panel.json`. The analysis arm uses the remaining 100. Held-out results are computed
only after a candidate has been selected on the 100, and are used solely to check
criterion B9.4.

Pairs are deduped. The runner resolves MBIDs per variant, asserts the node set is
identical across builds, and if not, restricts to the intersection and **reports the
drop-outs** rather than silently substituting.

Panel size grows rather than shrinks: prior runs used 50+50, then 25+25. Runtime is
~4 s/path, so 8 arms × 130 pairs is roughly 70 minutes of evaluation — affordable, and
separate from build time (§8, risk 1). Detecting a subtler effect with a smaller sample would
be backwards.

### B3. Entity filter (builder)

Drop nodes whose disambiguation matches `special purpose`, case-insensitively, in
`build_from_archive` before the mass computation at `pipeline.py:76`.

Enabled in **every** arm, so it is not confounded with damping. Credited with nothing
(§1.3). Unit test asserts both directions: the 7 are removed, and the 15 bracket-named
real bands survive.

Note that mass is computed over the full uncapped neighbour list, so removing these
nodes perturbs every mass slightly and therefore every score. The effect is negligible
at these degrees, but it is a second variable and is why the filter is held constant
across arms rather than swept.

### B4. Scoring changes

Two **separate** changes, varied as two factors — not bundled.

**Factor R (rescale).** `p99-log-clip` (current) versus `percentile-rank`. The clip is
the confirmed 34,696-edge hub funnel of §1.2, and a rank transform has no tie mass at
the ceiling. Bundling this with damping and sweeping only damping would attribute the
clip fix to damping.

**Factor d (damping),** applied in log space:

```
raw   = log1p(cooc) − d · (log mass_a + log mass_b)
score = rescale(raw)          # per factor R
```

Two deliberate departures from roadmap C4's formula:

- **No `2 · log(median_mass)` centring.** Under a rank transform it is a global additive
  constant and therefore provably inert. It appears to matter only because of the clamp.
- **No clamp at 0.** Clamping collapses every edge below the threshold into a single tie
  at the floor, then a single tie at the bottom of the rescale, then a uniform
  `w_sim · (1 − 0) = 3.0` cost — the same tie-mass pathology as the ceiling defect,
  mirrored. A rank transform handles negative values without help. If a floor is later
  wanted, use NPMI (Bouma 2009), bounded in [−1, 1] and better behaved at small counts,
  rather than raw clamping.

Naming what this is: `cooc / (mass_a^d · mass_b^d)` is the standard family — d = 0 raw,
d = 0.5 cosine, d = 1 lift/PMI; in log space with a clamp it is PPMI, whose textbook
pathology is over-weighting rare pairs, which is exactly the failure findings §4
*believed* it had observed. Relevant prior art: Levy, Goldberg & Dagan (TACL 2015) on
context-distribution smoothing and shifted PPMI; Zhou et al. (PNAS 2010) on tunable
degree exponents for popularity debiasing.

**Byte-for-byte equivalence** is required for the `(p99-log-clip, d = 0)` control cell
only, where the expression collapses exactly to today's. To preserve it, the p99 must
continue to be computed in **raw** space as `pipeline.py:110-113` does — `np.percentile`
with linear interpolation does not commute with `log1p`. Byte-identity is explicitly
**not** required of the percentile-rescale arms; they are new experimental conditions,
and asserting both identity and a rank transform at d = 0 is self-contradictory (a rank
transform is uniform on [0,1]; the current artifact measures p25/p50/p75 =
0.405/0.488/0.605).

Determinism (spec §9) still holds within every arm: identical input, identical bytes.

### B5. Grid

Set by Step A's gate. The prior now points **upward** from roadmap C4's d ≈ 0.25 —
cosine at 0.5 already reads well (§1.1), and the literature prior for context-distribution
smoothing is ≈ 0.75. Expected shape is R ∈ {clip, percentile} × d ∈ {0, 0.5, 0.75, 1.0},
with the exact grid fixed after A and recorded before any build runs.

### B6. Deferred: the support axis

Damping and support are different axes. No value of d distinguishes "a genuinely tight
niche pair" from "two artists with cooc = 3 and tiny masses" — and the second is what
every reported junk-path incident looks like. If Step B concludes "no candidate wins",
that conclusion is only valid for the damping axis.

Deferred to a follow-up, conditional on the sweep result: shrinkage
`score × cooc/(cooc + k)`, or context-distribution smoothing damping the marginal as
`mass^0.75` rather than the product. Recorded here so a null result is not mistaken for
"scoring cannot be improved".

### B7. Diagnostics

Per build, in the results table and the HTML export: N, E, degree p50/p99/max,
popularity p25/p50/p75, **count of saturated (score = 1.0) edges and the median degree
of their destinations**, `corr(score, log degree)`, node-set diff versus the control.

Both defects in §1.1 and §1.2 were invisible in the existing summary output and fall
straight out of these.

### B8. Statistics

The same endpoint pairs appear in every arm, so measurements are strongly paired.
Compare **per-pair deltas against the control arm** with a Wilcoxon signed-rank test
(or a paired bootstrap CI on the mean delta), which recovers substantial power over
comparing aggregate means.

One primary metric and one decision rule are pre-specified and committed **before** any
build runs. Holm correction across arms.

### B9. Adoption criterion

Adopt a candidate only if **all four** hold:

1. Degree-controlled neighbour overlap (Adamic–Adar, geometric mean) improves over the
   control, paired-significant.
2. `hubfrac` moves toward the null **without** mean interior degree collapsing *below*
   it. The lower guard is the explicit defence against the earlier failure, where an
   anti-hub objective drove routing into the sparse periphery and produced incoherent
   paths through unrelated artists.
3. Hand-read paths show no junk hops.
4. The **held-out** panel slice, untouched during analysis, reproduces (1) and (2).

Criterion 4 is what would have caught the earlier over-fit.

### B10. Adoption

Regenerate the 5k fixture from the adopted graph, record the result in
`docs/superpowers/findings/`, update the roadmap and `config.py`'s justification comment.

---

## 6. Interfaces and boundaries

| Unit | Responsibility | Depends on |
|---|---|---|
| `builder/…/pipeline.py` | Scoring: damping factor, rescale factor, entity filter | archive, `BuilderConfig` |
| `builder/…/config.py` | `similarity_damping`, new `similarity_rescale`, entity-filter toggle | — |
| `api/…/evaluation.py` | Pure metrics over a `GraphStore`; no I/O | `GraphStore` |
| `api/eval/nulls.py` *(new)* | Configuration-model rewiring, degree-biased walk | `GraphStore` |
| `api/eval/panel.json` *(new)* | Frozen MBID panel + held-out flag | — |
| `api/eval/run_baseline.py` | Drives metrics over the panel; emits the diagnostics table | evaluation, panel |
| `api/eval/export_paths.py` *(new)* | Side-by-side HTML with rank/score/degree per hop | evaluation, panel |

The `APG1` artifact remains the builder↔api contract. Nothing in this phase changes the
format; only the values written into `scores` and the node set change.

### 6.1 The one place "weights are frozen" is not automatically true

Popularity is **derived from the scores** (`pipeline.py:124-125`, log-scaled in
`graph.py`). Measured popularity p25/p50/p75 is 0.481/0.543/0.606 in v3 against
0.661/0.716/0.762 in cosine — a 0.17 shift in median. So `w_jump·|Δpop|` and
`w_floor·max(0, floor − pop_v)` behave differently across arms even with numerically
identical weights. The cost function is not frozen just because the config is.

Resolution, to be settled in the plan: either add an arm with `w_jump = 0` (which,
given `w_floor` is a proven no-op per roadmap C3 and `w_hub` is dormant at 0.0, reduces
cost to `w_sim·(1 − sim) + w_hop` and removes the popularity channel entirely), or hold
popularity fixed at control values while varying only edge scores. The `w_jump = 0` arm
is the cleaner experiment for attributing a *scoring* change and is the recommended
default.

---

## 7. Testing

- **Builder unit tests:** entity filter removes the 7 and retains the 15 named real
  bands; log-space damping at d = 0 with the clip rescale reproduces the current
  expression exactly; percentile rescale produces a uniform score distribution.
- **Determinism:** the existing offline replay test (which injects a raising fetcher to
  prove `build_from_archive` never touches the network) must still pass unchanged.
- **Evaluation unit tests:** `hubfrac`, Adamic–Adar, and Jaccard verified against a
  hand-built toy graph with known values, including the endpoint-exclusion convention
  and the empty-intersection case.
- **Null model tests:** rewiring preserves the degree sequence exactly.
- **Panel test:** loader fails loudly on an unresolvable MBID rather than skipping
  silently.

Snyk `snyk_code_scan` runs on the new and modified Python, per project convention.

---

## 8. Risks and open questions

1. **Build wall-clock is unknown.** One 75k build from the archive has not been timed.
   Eight arms could be minutes or hours; this decides serial versus parallel execution
   and is the first thing the plan must measure.
2. **Step A may collapse Step B.** If the null model shows hub-seeking is topological,
   damping is not the lever and Step B changes shape entirely. This is a feature of the
   sequencing, not a risk to mitigate.
3. **Disk.** Each 75k artifact is ~43 MB and `builder/scratch/` is gitignored; eight
   arms is ~350 MB of untracked local state. Adopted artifacts must be identified by a
   recorded checksum, since they cannot be committed.
4. **`similarity_rescale` is a new public config knob.** Once the sweep concludes, the
   losing option should be deleted rather than left as a permanently supported mode.

---

## 9. Out of scope

All of Phase 1 (clips, bypass differentiation, frontend UX); `w_hub` tuning; API cost
weight retuning beyond the `w_jump = 0` control arm in §6.1; the support/shrinkage axis
(§B6); everything in Gates 2 and 3.

---

## 10. References

- Roadmap: `../plans/2026-07-21-alpha-rollout-roadmap.md`
- Prior review and baseline: `../findings/2026-07-21-architecture-review-and-path-baseline.md`
  (§4 to be corrected per A2)
- Original design: `2026-07-19-artist-path-alpha-design.md` (determinism, §9)
- Adamic & Adar (2003); Liben-Nowell & Kleinberg (2007) — degree-discounted neighbourhood overlap
- Levy, Goldberg & Dagan (TACL 2015) — context-distribution smoothing, shifted PPMI
- Bouma (2009) — NPMI
- Zhou et al. (PNAS 2010) — tunable degree exponents for popularity debiasing
