# Architecture Review & Path-Quality Baseline

> ## ⚠ SUPERSEDED for scoring and path-quality metrics
>
> **Every number in this document concerning similarity scoring, hub-seeking, or
> path-quality metrics has been superseded by
> [`2026-07-21-scoring-adjudication.md`](2026-07-21-scoring-adjudication.md),
> which is the single quantitative record for those subjects.** That document's §6
> tables 27 prior claims — from this file, from the roadmap, and from the Phase 2 spec —
> as upheld, overturned, or unresolved.
>
> Do not cite a figure from §2, §4 or §5 below without checking §6 there first. Several
> headline numbers in §5 — including the `+0.725` score/degree correlation and the
> conclusion that hub-seeking is scoring-caused — **did not reproduce**. §5 says so
> itself in its provenance note; the adjudication measured it.
>
> **This file is retained as narrative history**: how the reviews unfolded, what was
> believed when, and why. Its non-scoring content (the architect and QA findings in §1 —
> clip 500s, artifact length validation, sync boto3 on the event loop) is **not**
> superseded and remains actionable.

**Date:** 2026-07-21
**Context:** After the full 75k graph was built and the backend proven end-to-end, three independent expert subagents (senior architect, senior QA engineer, ML/graph expert) critically reviewed the architecture, methodology, and plan. Their biggest finding — that path quality was validated only by eyeballing — was then tested with an objective evaluation harness (`api/eval/run_baseline.py`, metrics in `api/src/artistpath_api/evaluation.py`). This records both.

---

## 1. The review (three lenses)

All three affirmed the engineering discipline, documentation, empirical data-sourcing, builder/api decoupling, and 99.997% connectivity. Criticism was concentrated and specific. Points where **reviewers converged independently** (higher confidence):

- **Clip path returns HTTP 500 on any Deezer error** (architect + QA) — the fetch raises *past* the iTunes fallback, so a Deezer rate-limit (which parallel autoplay provokes) breaks every track request instead of degrading to an unplayable card. Spec §5.1 requires graceful degradation. **Not yet fixed.**
- **No objective path-quality evaluation** (QA + ML) — spec §9 mandated a "beats shortest-path on smoothness" test that was never written. Now addressed by the harness (§2).
- **No CI pipeline** (architect + QA) — nothing gates regressions.
- **Artifact corruption at boot is silent** (QA + architect) — the API's graph reader validates magic but not length; a truncated S3 fetch surfaces as request-time crashes.
- **Per-artist score normalisation is incommensurable across artists** (architect + ML), and the design's "scores compress to 0.38–1.0" claim is false — 48% of edges are below 0.38.

Other notable single-reviewer findings:
- **S3 graph-loading is unimplemented** (architect) — the "swap the graph via one env var / roll back" story exists only on paper; code reads a local path. No deploy story yet.
- **The real latency ceiling is GIL-bound pure-Python Dijkstra** (architect), not the choice of algorithm. Bidirectional Dijkstra would only halve node exploration; the fix ladder is (a) cache deterministic results, (b) push the no-exclusion case to a C-level solver (scipy.sparse.csgraph), (c) bidirectional later.
- **The two bypass signals are never distinguished at the path level in tests** (QA) — you could delete the avoidance logic and every test still passes. The signature feature has no behavioural regression protection.

### Real graph statistics (ML reviewer, from `graph-75k.bin`)

| Metric | Value |
|---|---|
| Nodes / directed edges | 74,998 / 4,014,354 (avg degree 53.5) |
| Out-degree median / max | 44 / 11,050 (Radiohead) |
| Nodes with degree ≥ 50 | 44% (the "cap of 50" is illusory post-symmetrisation) |
| Popularity (log in-degree) p25 / p50 / p75 | 0.478 / 0.547 / 0.611 (IQR width **0.13**) |
| Hub concentration: top 1% / top 10% share of weighted in-degree | 15.7% / 40.6% |
| Spearman(popularity, degree) | 0.79–0.81 (popularity ≈ centrality) |
| Mean cost term: `w_sim·(1−sim)` / `w_jump·\|Δpop\|` / `w_hop` | **1.71 / 0.17 / 0.02** (≈10:1) |

---

## 2. Path-quality baseline (the harness result)

50 random pairs + 50 obscure pairs (both endpoints out-degree ≤ 5), seed 42, top-1% degree threshold = 357. Three routers compared. **This is the "before" snapshot for any tuning.**

| Router | Hub-traversal (rand/obsc) | Path length | Bottleneck sim | Interior pop |
|---|---|---|---|---|
| **Full cost function** | 98% / 94% | 12.7 / 13.9 | **0.945 / 0.920** | 0.75 / 0.72 |
| **Similarity-only** | 100% / 100% | 33.2 / 33.7 | 0.985 / 0.961 | 0.68 / 0.67 |
| **Plain BFS (shortest)** | 94% / 86% | 4.3 / 5.6 | **0.213 / 0.202** | 0.77 / 0.69 |

### Conclusions — the harness corrected the review's prescription

1. **[SUPERSEDED BY §5 — the metric behind this conclusion was confounded.]** ~~Hub-traversal is topological, not caused by the popularity terms.~~ BFS (86–94%) and similarity-only (100%) also route through hubs — the graph is a hub-dense small world and hubs are its connective tissue. The full router's hub-rate is actually *lower* than similarity-only's. **Therefore quantile-transforming popularity (the ML reviewer's top fix) will NOT reduce hub-traversal.** Only an explicit anti-hub/degree penalty would.

2. **The popularity terms are a length regulator, not a popularity-smoother.** Their measurable effect is cutting length ~60% (33→13), at a small *cost* to smoothness (0.985→0.945). They do not keep paths among comparably-popular artists (interior pop ~0.72 regardless; obscure pairs still dive through the famous core). "Inert" was too strong; "mis-aimed" is accurate.

3. **Smoothness comes entirely from the similarity term.** Both Dijkstra variants score 0.92–0.99 bottleneck similarity; BFS scores 0.20. Spec §9's "popularity smoothing beats shortest-path" is true but **misattributed** — it is *similarity* that beats shortest-path. The similarity graph is genuinely excellent; do not break it.

4. **Path length is a real, under-weighted problem.** 13 hops (full) is 2–3× the design's imagined 5–8; 33 (similarity-only) is unusable. The card-grid UI will render 13+ cards by default.

### Revised fix priorities (evidence-based)

- **For the discovery goal: add an explicit hub/degree penalty** to the cost (cost rising with destination degree), then re-run the harness targeting hub-traversal well below 90% without wrecking the 0.92 smoothness. This — not popularity re-transformation — is the lever the data supports.
- **Reconsider the jump/floor popularity terms**, don't just re-tune them — they cost smoothness and miss their stated purpose. A simpler cost (similarity + hop-cost + hub-penalty) may beat the current four-term function. Validate with the harness.
- **Give path length an explicit target** (raise `w_hop` or cap).
- **Independently of tuning, before real users:** fix the clip-500 (wrap fetch in try/except → 204), add artifact length-validation at boot, implement real S3 graph-loading + `/health`, stand up CI, and add the missing bypass-differentiation tests.
- **Do not touch** the similarity term or the graph — they work.

### Meta-lesson

The reviewers were right that the system was unvalidated and that hub-seeking was happening — but their specific remedy targeted the wrong cause. That was only discoverable by building the metric instead of acting on the recommendation. The harness is now the standing regression guard for all path-quality work.

---

## 3. Tier-2 weight tuning (Optuna) — metrics improved, product got worse

**Date:** 2026-07-21. A hub-penalty term (`w_hub`, per-node log-degree hub-ness, zeroed below median) was added to the cost function and to `GraphStore`, defaulting to `0.0` so production routing was unchanged. Bayesian optimisation (Optuna TPE, 60 trials, 40 train / 40 test pairs, seed 7) then searched all five weights against a scalar objective:

```
score = bottleneck_similarity - 1.0*max_interior_hub_penalty - 0.3*length_deviation   (target len 7)
```

### Result: every metric improved

| | Baseline (`w_hub=0`) | Tuned |
|---|---|---|
| Hub-traversal (test) | 95% | **50%** |
| Smoothness (bottleneck sim) | 0.923 | 0.716 |
| Path length | 14.2 | 11.8 |
| Max-interior-degree (Miles→Daft) | 1817 | **59** |

Tuned weights: `w_sim=5.918, w_jump=2.131, w_floor=0.058, w_hop=0.079, w_hub=4.123`. The improvement generalised (train 40% / test 50% hub-traversal), so it was not panel overfitting.

### But the paths became incoherent — DO NOT ADOPT

- **Miles Davis → Daft Punk**, tuned: `Miles Davis → Lenny White → Chanson Plus Bifluorée → 山根康広 → 室井憲一 → Ngọc Anh → jesus2099 → Jessica Harper → Paul Williams → Daft Punk`. Unrelated artists across several unconnected scenes — and **`jesus2099` is a MusicBrainz *editor account*, not a musician**.
- **Burzum → Dolly Parton**, tuned: `Burzum → Westwind → Othila → Orchis → Pilori → Johnny Cash → Dolly Parton`. Lurches from obscure French black metal straight to Johnny Cash — the exact jarring transition the product exists to prevent.

The optimiser gamed the objective. `w_hub` remains `0.0` in production; nothing shipped.

### Root cause — promotes the normalisation finding from Medium to blocking

Per-artist max-normalisation (§1, flagged by both the architect and ML reviewer, and originally ranked Medium) makes edge strengths **incommensurable across artists**: an obscure artist's best neighbour scores **1.0** because it is normalised against itself, so a hop between two nobodies looks *maximally similar* while being musically meaningless. The hub penalty pushed routing into exactly that sparse periphery, where the scores lie most. **The smoothness metric is therefore untrustworthy, and any tuning against it optimises a broken yardstick.**

Second cause, independent: **non-artist entities are present in the graph** (editor accounts such as `jesus2099`), i.e. a data-quality gap in the crawl/build.

### Revised order of work

1. **Fix score normalisation** so edge strength is globally comparable — rank/percentile-normalise across the whole graph, or use a symmetric association measure (cosine / PMI / Jaccard over listener sets). Builder change + graph rebuild; **no re-crawl needed**, the archive is complete.
2. **Filter non-artist entities** from the artist set.
3. **Re-run the Tier-2 tuning** (`api/eval/tune_weights.py`) against the corrected metric, then re-check real paths before adopting anything.

### What survives regardless

The optimiser drove `w_floor` from 1.0 to ~0.06 — independently corroborating §2's conclusion that the obscurity-floor term does nothing useful. Two separate lines of evidence agree.

---

## 4. Normalisation fix — three attempts, measured

The blocking issue from §3 was fixed by replacing per-artist normalisation. Three scorings were built and compared **by reading real paths**, not metrics alone.

| Scoring | Result |
|---|---|
| **Per-artist max** (original) | Incommensurable: every artist's top edge = 1.0 whether raw was 11 or 11,147. Routed through junk (`jesus2099`). |
| **Full cosine** `cooc/√(mass·mass)` | **Over-corrected.** Inflates rare co-occurrence: a junk edge scored **0.148 vs 0.022** for Miles Davis→Stan Getz — 6.6× backwards. Produced film-soundtrack nonsense (`Miles Davis → J. K. Simmons → Hank Levy → Justin Hurwitz → Emma Stone → Daft Punk` — two of those are actors). |
| **Global raw + log scale** (adopted) | Coherent paths, well-spread scores, shorter routes. |

**Adopted:** `sim = log1p(cooc) / log1p(p99)`, one formula graph-wide, with a `similarity_damping` knob (default `0.0`; `0.5` = cosine) kept for future tuning. Popularity is deliberately **not** baked into similarity — it is handled in the API cost function (`w_jump`/`w_floor`/`w_hub`), a cleaner separation of concerns.

Log scaling mattered independently: linear scaling left p50=0.022/p75=0.053, so `w_sim·(1−sim)` was nearly constant and the similarity term could not discriminate. Log scaling gives p25=0.405 / p50=0.488 / p75=0.605.

### Measured outcome (75k graph, `graph-75k-v3.bin`)

| | Before | After |
|---|---|---|
| Path length | 13.0 / 14.2 | **7.6 / 9.0** (into the 5–8 design target) |
| Max-interior-degree (spot checks) | up to 11,050 | **428–1,343** |
| Junk/incoherent paths | present | gone |
| Hub-traversal (binary) | 95% | **92–96% (unchanged)** |
| Bottleneck similarity | 0.92 | 0.47 — **not comparable**, see below |

Two honest caveats:

1. **The smoothness numbers are not comparable across the fix.** The old 0.92 was inflated by per-artist normalisation (every artist's top edge was 1.0 by construction). The new 0.47 sits on a globally meaningful scale where median edge strength is 0.488. The metric is now honest, not worse.
2. **Hub-traversal did not improve** on the binary metric. ~~confirming §2's conclusion that it is topological.~~ **[SUPERSEDED BY §5: the binary metric cannot detect improvement — it reads 61–68% by chance at these path lengths. The fix did reduce hub-seeking; this metric was incapable of showing it.]** The `w_hub` term (built, still `0.0`) remains the lever — but it can now be tuned against a trustworthy yardstick, which was the whole point of this fix.

~~**The popularity terms remain nearly inert** even after the fix: FULL vs similarity-only score 0.472/0.474 bottleneck, 7.6/7.7 length, 92%/96% hub — essentially identical. §2's finding survives independently of the normalisation bug.~~ **[SUPERSEDED BY §5 — partially wrong. The three metrics compared here are all insensitive to what `w_jump` actually does: it cuts max interior degree 3.2×. `w_floor` is the genuinely inert term.]**

### Meta-lesson, sharpened

The harness earns its keep **only when paired with reading actual paths**. Metrics alone endorsed a clearly worse router. Both failure modes have now been seen in this project: eyeballing without metrics (missed hub-seeking) and metrics without eyeballing (endorsed gibberish). Both checks are required.

---

## 5. Second ML review — the measurement itself was confounded

**Date:** 2026-07-21, after §4 shipped. A second ML/graph review re-examined not the
router but **the metrics used to judge it**, and overturned three conclusions above.

> **Provenance note.** This section is reconstructed from the session record rather
> than re-derived. The numbers below were measured during that review; the *expected*
> post-fix figures are projections from it, not observed results. Re-measure before
> treating any of them as current. The corresponding plan of record — which carries
> these conclusions in operational form — is
> `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md`.

### 5.1 Hub-seeking is caused by the scoring, not the topology

Similarity scores correlate **+0.725 with endpoint degree**. Raw co-occurrence is a
popularity measure wearing a similarity costume, and log scaling preserves the
correlation rather than removing it. Against a **degree-biased null model** — the
control that §2 never built — length-normalised hub fraction is **0.641 vs 0.172, a
3.7× enrichment**. The router seeks hubs far beyond what the graph's structure forces.

§2 reached the opposite conclusion because it compared routers against *each other* on
a raw rate, with no null. Every router looked hub-heavy, so hub-heaviness looked
inherent. Corroborated experientially in dogfooding: Radiohead kept reappearing across
unrelated journeys.

### 5.2 The binary hub-traversal metric is worthless

"Does any interior node exceed the top-1% degree threshold" returns **61–68% by chance**
at path lengths 7–8. It is a proxy for path length, not for hub-seeking, which is why
§4 saw it sit flat at 92–96% through a fix that genuinely helped. Replace it with:

- **hubfrac** — fraction of interior nodes above the threshold, length-normalised.
- **neighbour-set Jaccard** — score-independent, therefore not circular. This is the
  one to optimise against; bottleneck similarity is derived from the same scores under
  investigation and cannot adjudicate its own correctness.

### 5.3 `w_jump` is not inert; `w_floor` is

`w_jump` cuts max interior degree **3.2×** — invisible to the three metrics §4 compared,
all of which are insensitive to interior degree. `w_floor` is a **provable** no-op: it
reproduces the no-floor result to every digit, because routes never dive below
`min(pop_source, pop_target)`, so the floor never binds. **Delete `w_floor` and
`floor_relax_*`.**

This has a product consequence that had gone unnoticed: "know them already" relaxes a
threshold that never binds, so **the two bypass signals are behaviourally identical at
runtime** — the app's signature feature does not currently do what it claims.

### 5.4 The full-cosine failure in §4 was our own bug

§4 concluded cosine "over-corrects". It does not. **The pipeline applies damping
*before* `log1p`**, which silently degenerates log scaling into linear scaling. The
inflated junk-edge scores were that ordering bug, not a property of cosine.

Correct form — damp **in log space**, then percentile-rescale:

```
log1p(cooc) − d·(log mass_a + log mass_b − 2·log median_mass)
```

**Fix, in order:** entity filter first (`jesus2099`, `[unknown]`, `[anonymous]` are
still nodes), *then* `similarity_damping ≈ 0.25` — filtering must precede damping,
since damping re-inflates low-mass pairs. Expected: hubfrac 0.641 → 0.231, max interior
degree 2118 → 913, bottleneck neighbour-Jaccard 0.0184 → 0.0346. `w_hub` stays dormant
at `0.0`; damping does the job better than an explicit penalty.

### Meta-lesson — the one this section adds

§3 and §4 established that metrics need eyeballs and eyeballs need metrics. §5 adds the
third failure mode: **a metric with no null model measures nothing.** Both prior reviews
read 94–98% hub-traversal as an alarming signal when chance alone accounts for most of
it. The 3.7× enrichment — the actual finding — only became visible once someone
constructed the control. Build the null before believing the rate.
