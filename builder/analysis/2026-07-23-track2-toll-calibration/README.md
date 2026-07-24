# Track 2 — T1 expressway-toll calibration

**Taken 2026-07-23, to amend the Track 2 pre-registration for defect D1.** Discharges
prerequisite **PR-C** of
[`../../../docs/superpowers/findings/2026-07-23-track2-protocol-analyst-review.md`](../../../docs/superpowers/findings/2026-07-23-track2-protocol-analyst-review.md)
("re-measure the toll as a fraction of `w_hop` after D1's fix is chosen").

Artifact: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`,
asserted in-script before every measurement. No path was routed; every quantity here is
a structural property of the artifact. Constants `w_sim = 3.0`, `w_hop = 0.02` are read
from `api/src/artistpath_api/config.py`.

**Figures ownership.** This README owns Q1–Q4 below — they are new measurements. The
ceiling-edge count, the largest non-ceiling score and the score grid are owned by the
analyst review's **M1** and are cited, never recomputed. Nothing here restates a figure
from the scoring adjudication or the Phase 1 log.

Run: `cd api && UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-track2-toll-calibration/calibrate_toll.py`

---

## What was asked

D1 showed that P3's rule — `s_max` just above the largest non-ceiling score — yields a
toll of **1.42 % of `w_hop`**, confirmed here independently. The replacement prices a
ceiling edge as though its similarity were a pre-registered `s_toll < 1`. Two questions
had to be settled before levels could be chosen: what a toll is competing against, and
whether the ceiling sits anywhere a routed path would meet it.

## Q1 — edge-similarity quantiles

What an *alternative* hop costs, so a toll can be read against it.

| set | n | p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|---|---|
| all edges | 898,006 | 0.3718 | 0.4305 | 0.5226 | 0.6466 | 0.7863 | 1.0000 |
| top-decile-popularity incident | 259,952 | 0.5731 | 0.6323 | 0.7190 | 0.8230 | 0.9506 | 1.0000 |
| lateral (both ≥ p90) | 131,724 | 0.6441 | 0.7137 | 0.7966 | 0.9039 | 1.0000 | 1.0000 |

## Q2 — ceiling edges per node

| set | mean | median | max |
|---|---|---|---|
| all nodes | 0.237 | 0 | 50 |
| top-decile-popularity nodes | 2.313 | 0 | 50 |

Only **1,428 of 7,420** top-decile nodes (19.25 %) carry any ceiling edge; their mean
degree is 26.39. Saturation is concentrated, not diffuse.

## Q3 — what each candidate toll buys

`toll = w_sim · (1 − s_toll)`. The last column is where a tolled ceiling edge would rank
within the top-decile-incident similarity distribution.

| `s_toll` | toll | × `w_hop` | tolled ceiling edge ranks at |
|---|---|---|---|
| 0.99 | 0.0300 | 1.50 | 92.69th pctile |
| 0.95 | 0.1500 | 7.50 | 89.97th pctile |
| 0.90 | 0.3000 | 15.00 | 85.66th pctile |
| 0.80 | 0.6000 | 30.00 | 70.35th pctile |
| *P3 as written* | 2.831 × 10⁻⁴ | **0.0142** | — (inert; D1) |

## Q4 — the ceiling sits precisely on the sweep's endpoints

This is the result that changed the amendment, and it was not anticipated by D1.

| set | n | mean ceiling edges | with ≥ 1 |
|---|---|---|---|
| p90–p99 by degree | 6,981 | 1.23 | 7.5 % |
| top 1 % by degree | 940 | 3.54 | 13.6 % |
| **the 24 pre-registered endpoints** | 24 | **40.17** | **22 of 24** |

All 24 endpoints resolved by name (highest-popularity duplicate rule), independently
re-confirming that P2 is discharged. Their mean degree is 43.1, and eight are **fully
saturated** — every one of their 50 neighbours sits at score exactly 1.0: The Rolling
Stones, The Beatles, Radiohead, Pink Floyd, Nirvana, Muse, Daft Punk, Coldplay.

## What follows, and what does not

1. **T1 is not the narrow probe Q2 alone suggests.** Ceiling saturation is rare in the
   population and near-universal among the artists this sweep starts and ends at, so the
   toll binds where the sweep actually routes. A T1 null is correspondingly stronger
   evidence about the p99 ceiling than Q2 would imply on its own.
2. **A toll cannot re-rank the exits from a saturated node — it can only make the
   expressway longer-dearer.** At a node whose 50 edges are all at 1.0, an additive toll
   adds the same constant to every exit. It changes the trade-off between a multi-hop
   ceiling route and a shorter or dearer alternative; it does not change *which*
   neighbour is preferred. T1's question is therefore precisely "is the expressway's
   **cheapness** load-bearing?", not "is its **ordering** wrong?"
3. **The same degeneracy affects the S-mag column,** and this is a factor-table
   completeness point rather than a toll one: at a fully saturated endpoint the
   `w_sim · (1 − sim)` term contributes an identical constant across all 50 exits, so
   S-mag (3.0 vs 1.5) has no discriminating power on the *first hop* out of those eight
   endpoints. Its treatment effect there operates only through downstream hops and
   through the term's weight relative to the jump term. Recorded in the pre-registration's
   held-constant section.
4. **What this does not say.** Nothing here is a claim about path quality, about whether
   the ceiling *should* be rescaled (that is the deferred builder route, and T1 probes
   binding, not rescaling), or about the `cap_strategy` question closed in Phase 1 log
   §4. No path was routed, so nothing here measures what any arm will do.
