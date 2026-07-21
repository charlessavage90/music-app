# Architecture Review & Path-Quality Baseline

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

1. **Hub-traversal is topological, not caused by the popularity terms.** BFS (86–94%) and similarity-only (100%) also route through hubs — the graph is a hub-dense small world and hubs are its connective tissue. The full router's hub-rate is actually *lower* than similarity-only's. **Therefore quantile-transforming popularity (the ML reviewer's top fix) will NOT reduce hub-traversal.** Only an explicit anti-hub/degree penalty would.

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

### Meta-lesson, sharpened

The harness earns its keep **only when paired with reading actual paths**. Metrics alone endorsed a clearly worse router. Both failure modes have now been seen in this project: eyeballing without metrics (missed hub-seeking) and metrics without eyeballing (endorsed gibberish). Both checks are required.
