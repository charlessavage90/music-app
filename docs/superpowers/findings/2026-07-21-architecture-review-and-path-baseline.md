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
