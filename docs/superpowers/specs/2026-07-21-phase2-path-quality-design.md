# Phase 2 — Path Quality: Design

**Date:** 2026-07-21
**Gate:** 1 (personal use)
**Status:** approved design, revised after adjudication, not yet planned
**Supersedes:** the Phase 2 bullet list in `../plans/2026-07-21-alpha-rollout-roadmap.md`.
The roadmap remains the plan of record for gate structure and for Phases 1 and 3–7;
this spec replaces only its Phase 2 content.

**Quantitative record:**
[`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md).
Every measured figure about scoring, hub-seeking, or path-quality metrics lives there and
**is not restated here** — this spec cites section numbers instead. Three documents drifted
apart by each keeping its own copy of the numbers; the rule now is one record, and specs
and plans point at it.

---

## 1. Why this phase is not what the roadmap said

> **All quantitative claims in this section live in
> [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md).**
> This spec cites that record and deliberately does not restate its figures. Three
> documents drifted apart by each restating the same numbers; the rule now is that
> numbers live in exactly one findings document and specs point at it.

The roadmap's Phase 2 rested on a diagnosis that has since been measured and largely
overturned. An earlier draft of this spec proposed its own replacement diagnosis, which
was **also** overturned. Both are recorded in the adjudication; the four facts that
survive and actually shape this phase are:

**1.1 The historical comparisons changed two variables at once.**
`graph-75k-cosine.bin` and `graph-75k-v2.bin` were built by commit `284366c`, whose
rescale is linear; only `graph-75k-v3.bin` has the `log1p` rescale from `fff422e`.
Every conclusion drawn by comparing those artifacts — including this spec's first
draft — is confounded. See adjudication §1.

**1.2 Cosine really does over-correct.** Routing on the cosine artifact reproduces the
film-soundtrack path verbatim. The neighbour *rankings* under cosine are better while
the *routed paths* are worse, which is why ranking evidence alone was insufficient.
Adjudication §2.3. The specific numbers in the original findings §4 are still refuted
(§2.4), but its conclusion was right.

**1.3 The p99 clip is the primary defect, and it is upstream of the damping question.**
It creates zero-cost edges in every build; `d` decides only *where* they point — the
famous core at `d = 0`, micro-cliques at `d = 0.5`. Between **30 % and 82 % of routed
hops currently cost zero similarity**, leaving the router to choose on `w_jump` and
`w_hop` noise. Adjudication §2.5. **Consequence for this design: Factor R is a
precondition, not a co-equal factor — the sweep's control cell is itself defective
until the rescale is fixed.**

**1.4 Hub-seeking is not established as scoring-caused.** The degree-biased null
reproduces (0.1723, 3.66–4.09× enrichment) but does not license that inference:
score-free BFS is 2.68× enriched on the same null, and the full router has the *lowest*
max interior degree of the three routers tested. The `+0.725` correlation behind the
claim is unreproducible and substantially tautological. Adjudication §5.1–5.3. The
configuration-model rewire (§A3) remains the outstanding experiment that would settle it.

**1.5 The entity filter is not a quality lever.** 7 special-purpose nodes, max degree
218 against a top-1 % threshold of 363. Filter on the disambiguation field, never on the
name: 22 nodes have bracketed names and 15 of them are real bands. This measurement is
this spec's own and is listed unresolved in the adjudication's §6 (claim 25) pending
independent re-measurement.

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

**Most of Step A as originally specified has already been executed** by the adjudication
(`../findings/2026-07-21-scoring-adjudication.md`, commit `48f7413`). What follows records
what it settled and what genuinely remains.

**Done — A2, retract or substantiate findings §4.** Settled: findings §4's *conclusion*
was right (cosine over-corrects; the film-soundtrack path reproduces verbatim) while its
*numbers* were wrong. Findings §5.4's ordering explanation is dead — the artifact it
purported to explain was built by a commit that had no `log1p`. `config.py` and the
findings doc have been corrected; the roadmap is corrected as part of this consolidation.

**Done — A4, re-derive the uncommitted numbers.** The `+0.725` correlation is
unreproducible and substantially tautological (Spearman between out-score sum and degree
is +0.987). The degree-biased null reproduces at 0.1723 with 3.66–4.09× enrichment, but
does not support the inference drawn from it. Adjudication §5.1–5.3.

### A1. Path-export tool — still required

**New:** `api/eval/export_paths.py`. Emits one self-contained HTML file.

- Rows: panel artist pairs. Columns: graph artifacts under comparison.
- Each cell: the path, and per hop — the destination's **rank within the source
  artist's neighbour list**, the edge score, and the destination's out-degree. Hubs
  marked.
- Header: the per-artifact diagnostics table from §B7.

**Rank is mandatory, not decorative**, and so is showing the *decoded path* rather than
neighbour lists alone. Both source documents failed here, in opposite directions: one
read scores without rank (twelve consecutive `1.0000`s hid the defect), the other read
neighbour rankings without routing (better rankings hid worse paths). The tool must make
both visible in one view.

### A3. Configuration-model null — the one experiment still outstanding

Rewire the graph preserving the exact degree sequence, randomising edge endpoints;
re-run the router; measure hub fraction against the observed graph.

This is now the **highest-value unmeasured item in the phase**. The degree-biased walk
null alone does not settle whether hub-seeking is topological or scoring-caused: it puts
the full router at 3.66–4.09× enrichment, but score-free BFS is also 2.68× enriched on
the same null, and the full router has the *lowest* max interior degree of the three
routers tested. Turning the scoring off makes hub-seeking worse, which is the opposite
of what findings §5.1 predicted.

- Rewired graph hub-seeks comparably → **topological**; scoring changes will not fix it,
  and findings §2's struck-through conclusion is reinstated.
- It does not → **scoring-caused**, and §5.1's conclusion survives its broken evidence.

Report it alongside the degree-biased walk null; they answer different questions.

### Gate

Step A now answers a narrower question than originally posed. The rescale fix does not
depend on it — that is established independently (§1.3) and proceeds regardless. What
Step A settles is **how much of the remaining hub-seeking any scoring change can reach**,
which sets how hard Step B should push on `d` and whether the dormant `w_hub` term comes
back into scope.

---

## 5. Step B — Narrow sweep

### B1. Metrics (`api/src/artistpath_api/evaluation.py`)

**Primary objective: Adamic–Adar**, `Σ_{w ∈ N(u) ∩ N(v)} 1 / log deg(w)`, over each
adjacent path pair, aggregated as the **geometric mean over hops**.

**Mandatory co-reported guard: the overlap coefficient**, `|N(u) ∩ N(v)| / min(d_u, d_v)`.
A candidate that improves Adamic–Adar *without* improving the overlap coefficient is
**not adopted**. Rationale (adjudication §4.2–4.3): Adamic–Adar is the only candidate
measured flat in max-degree (+0.110), but it carries a Spearman **+0.578 coupling to
min-degree** — a specific, measured channel by which an optimiser could game it. The
overlap coefficient is near-neutral on both axes (−0.004 / −0.062) and is the control
for that channel. Neither source document considered it.

Why not raw Jaccard, which findings §5.2 called "the one to optimise against": it is not
an independent check. `corr(log Jaccard, log max-degree) = −0.639` (Spearman −0.730),
with median Jaccard falling 0.4000 → 0.0090 across degree buckets. It is structurally
bounded by `J ≤ min(d_u, d_v) / max(d_u, d_v)`, so a degree-50 artist adjacent to
Radiohead cannot exceed J = 0.0044 however musically related. Bottleneck Jaccard is
therefore a near-deterministic monotone function of `max_interior_degree`, which
`PathMetrics` already reports — it restates the hub metric rather than corroborating it.
"Score-independent, therefore not circular" is a non-sequitur: independence from the
score *array* is not independence from the *intervention*. Adjudication §4.1.

Observed/expected overlap under a configuration model was also considered and rejected —
at Spearman −0.880 against max-degree it is **worse** than Jaccard (adjudication §4.2).

Adamic–Adar discounts hub-mediated overlap and is the standard link-prediction answer
(Adamic & Adar 2003; Liben-Nowell & Kleinberg 2007).

Also required:

- **Geometric mean, not bottleneck-min.** Over 7–9 hops a min is dominated by one noisy
  node. Measured zero-rate for common-neighbour overlap is 0.7 %, so log-space
  aggregation is safe with a small epsilon.
- **`hubfrac`** replaces the binary `hub_traversed`, which reads **0.642 by chance** at
  length 7.4 and measures path length rather than hub-seeking. Report it against **two**
  baselines, not one: the degree-biased walk null (0.1723) **and a score-free BFS
  control**. The walk null alone licenses the wrong inference — BFS is itself 2.68×
  enriched, so a router can look hub-seeking against the walk null purely because the
  topology is (adjudication §5.3). The hub set is **frozen by MBID** from the control
  build, since the per-graph top-1 % threshold moves (363 in v3, 278 in cosine) and a
  variant could otherwise "improve" by compressing its degree distribution.
- **Raw Jaccard retained as a diagnostic**, reported with its correlation to
  `max_interior_degree` so its redundancy stays visible in the results table.
- Existing `length`, `max_interior_degree`, `mean_interior_pop`, `bottleneck_sim`,
  `mean_sim` retained as diagnostics.

**Every overlap-based objective above is structurally blind to the failure this project
keeps hitting.** All of them would score `Miles Davis → J. K. Simmons → Hank Levy →
Justin Hurwitz → Emma Stone` *well* — it is a chain of dense, mutually-overlapping
micro-neighbourhoods. Decoded paths are not a supplementary check here; they are the only
instrument that detects this class of failure. Adjudication §4.3.

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

Two **separate** changes. **The rescale is a precondition, not a co-equal factor** — an
earlier draft of this spec treated them as a 2 × 5 factorial, which is wrong.

**Factor R (rescale) — fix first, then re-establish the control.** `p99-log-clip`
(current) versus `percentile-rank`. The clip creates zero-cost edges in *every* build,
and damping only relocates them: median destination degree of a free edge is 719 at
`d = 0` and 9 at `d = 0.5`. 30–82 % of routed hops currently cost zero similarity, so
**the `(clip, d = 0)` control cell is itself defective and no `d` comparison run under
the clip is interpretable** — including the historical one that rejected cosine
(adjudication §2.5).

Sequence: adopt the rank rescale, rebuild a clean control, verify that fewer than 30 %
of routed hops sit at the ceiling, and only then sweep `d`. The clip arms are retained
only as the byte-identity control described below, never as candidates for adoption.

**Factor d (damping),** applied in log space:

```
raw   = log1p(cooc) − d · (log mass_a + log mass_b)
score = rescale(raw)          # per factor R
```

Two deliberate departures from roadmap C4's formula:

- **No `2 · log(median_mass)` centring — but only because the rescale is a rank
  transform.** Under a rank transform the term is a global additive constant and
  provably inert (measured residual 3.55e-15, rank-identical). **Under the clip rescale
  with a clamp it is mandatory, not optional:** dropping it clamps 78.67 % of edges at
  `d = 0.25`, 99.98 % at `d = 0.5` — where `p99(raw) = 0.000` and the pipeline emits
  `nan` — and 100 % at `d ≥ 0.75`. Adjudication §3.1–3.2. Any code path that combines
  the clip with `d > 0` **must** keep the centring; the rank path must not bother.
- **No clamp at 0.** Clamping collapses every edge below the threshold into a single tie
  at the floor, then a uniform `w_sim · (1 − 0) = 3.0` cost — the same tie-mass pathology
  as the ceiling defect, mirrored (30.62 % of edges tie at the floor at `d = 0.75`,
  adjudication §3.3). A rank transform handles negative values without help. If a floor
  is later wanted, use NPMI (Bouma 2009), bounded in [−1, 1] and better behaved at small
  counts, rather than raw clamping.

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

**Sequential, not factorial.** An earlier draft proposed R ∈ {clip, percentile} × d ∈
{0, 0.5, 0.75, 1.0} with the centring dropped throughout — **three of those eight cells
build a degenerate graph** (§B4). That grid is withdrawn.

1. **Control:** `(clip, d = 0)`, byte-identical to today's artifact. Built once, to
   anchor the comparison and prove the refactor changed nothing.
2. **Rescale fix:** `(rank, d = 0)`. Adopt if it cuts ceiling hops below 30 % without
   degrading decoded paths. This is the highest-confidence change in the phase.
3. **Damping sweep, under the rank rescale only:** `d ∈ {0, 0.25, 0.5, 0.75}`, exact
   points fixed after Step A and recorded before any build runs.

Note the open hypothesis this ordering is designed to test: **once the rescale is fixed,
`d` may matter far less than either source document assumed**, because both observed
failure modes — the famous core at `d = 0` and the film-cast cliques at `d = 0.5` — were
clip artefacts wearing different clothes. Falsified if rank-rescaled `d = 0` and
`d = 0.5` still produce qualitatively different path failures (adjudication §7.7).

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

Adopt a candidate only if **all six** hold:

1. Adamic–Adar (geometric mean over hops) improves over the control, paired-significant.
2. The **overlap coefficient** improves too. A candidate that improves Adamic–Adar while
   the overlap coefficient is flat or worse has moved along AA's measured +0.578
   min-degree channel rather than genuinely improving, and is **not adopted**.
3. `hubfrac` moves toward the null **without** mean interior degree collapsing *below*
   it. The lower guard is the explicit defence against the earlier failure, where an
   anti-hub objective drove routing into the sparse periphery.
4. **Ceiling hops below 30 %** — the fraction of routed hops at score 1.000. This is the
   defect that made every prior comparison uninterpretable; a candidate that leaves it in
   place has not fixed the thing that matters most.
5. Hand-read decoded paths show no junk hops. **Not a formality and not delegable to the
   metrics:** every overlap objective above scores the *La La Land* path well.
6. The **held-out** panel slice, untouched during analysis, reproduces (1)–(4).

Criteria 2, 4 and 6 are each traceable to a specific failure this project has already
had — an objective gamed along an unmeasured axis, a defect invisible to the summary
output, and an over-fit endorsed by the metrics it was tuned on.

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
- **Degeneracy guard:** a test asserting the pipeline never emits `nan` or an all-zero
  score array for any `(rescale, d)` combination the config permits. Dropping the
  centring under the clip rescale clamps 99.98 % of edges at `d = 0.5` and produces
  `nan`; that must fail loudly at build time rather than silently shipping a null graph.
- **Evaluation unit tests:** `hubfrac`, Adamic–Adar, the overlap coefficient, and Jaccard
  verified against a hand-built toy graph with known values, including the
  endpoint-exclusion convention and the empty-intersection case.
- **Null model tests:** rewiring preserves the degree sequence exactly.
- **Panel test:** loader fails loudly on an unresolvable MBID rather than skipping
  silently.

Snyk `snyk_code_scan` runs on the new and modified Python, per project convention.

---

## 8. Risks and open questions

1. **Build wall-clock is unknown.** One 75k build from the archive has not been timed.
   Six builds could be minutes or hours; this decides serial versus parallel execution
   and is the first thing the plan must measure.
2. **The configuration-model null may reduce the damping sweep to a formality.** If it
   shows hub-seeking is largely topological, no scoring change reaches it and Step B
   narrows to adopting the rescale fix. A feature of the sequencing, not a risk to
   mitigate — but the plan should not assume the sweep will happen.
3. **Disk.** Each 75k artifact is ~43 MB and `builder/scratch/` is gitignored; six builds
   is ~260 MB of untracked local state. Adopted artifacts must be identified by a
   recorded checksum, since they cannot be committed. **Artifacts must also record the
   commit that built them** — the confounded comparison in §1.1 happened because four
   artifacts sat in one directory with no provenance and were compared as though they
   differed in one variable.
4. **`similarity_rescale` is a new public config knob.** Once the sweep concludes, the
   losing option should be deleted rather than left as a permanently supported mode.

---

## 9. Out of scope

All of Phase 1 (clips, bypass differentiation, frontend UX); `w_hub` tuning; API cost
weight retuning beyond the `w_jump = 0` control arm in §6.1; the support/shrinkage axis
(§B6); everything in Gates 2 and 3.

---

## 10. References

- **Quantitative record (cite this, do not restate it):**
  `../findings/2026-07-21-scoring-adjudication.md`
- Roadmap: `../plans/2026-07-21-alpha-rollout-roadmap.md`
- Narrative history only — superseded for scoring and metrics:
  `../findings/2026-07-21-architecture-review-and-path-baseline.md`
- Original design: `2026-07-19-artist-path-alpha-design.md` (determinism, §9)
- Adamic & Adar (2003); Liben-Nowell & Kleinberg (2007) — degree-discounted neighbourhood overlap
- Levy, Goldberg & Dagan (TACL 2015) — context-distribution smoothing, shifted PPMI
- Bouma (2009) — NPMI
- Zhou et al. (PNAS 2010) — tunable degree exponents for popularity debiasing
