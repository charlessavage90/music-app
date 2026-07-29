# Cap selection and source algorithm selection — analysis directory

Governing document for the `AS` arms:
`docs/superpowers/specs/2026-07-29-algorithm-selection-preregistration.md`.
Read alongside `docs/superpowers/2026-07-29-algorithm-selection-execution-log.md`, which
owns the reads.

**The directory name is now partly misleading and is kept anyway.** It was created for the
cap-selection simulation, which was the agreed first task. `cs_p0c_candidates.py` then showed
that task cannot fix `DD-F1`, and the work re-sequenced into source *algorithm* selection.
The name is not corrected because renaming a committed path breaks every citation — the
`CS-` scripts are the scope probes, the `as_` scripts are the algorithm-selection arms, and
**the cap-selection simulation itself has not been run and is not in here.**

Artifact for everything: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256
`4cb84ef9…b061dc8` — **asserted by every script**, which refuses to run on a mismatch.
N = 74,193, E = 898,006 directed CSR entries.

**Currency notice.** Every percentile here (`pop_pctl`, "sub-decile", "below median") is
computed **in the script** by ranking the artifact's `pop_raw`. `pop_raw` is never read as a
rank (Phase 1 log §2.12). None of these figures is a fame claim (§2.11). Raw source
`score` values are **not comparable across `algorithm` values** — see the pre-registration
§1.5; cross-arm comparison here uses ranks and set overlap only.

## Scope probes (`CS-P0…`) — run BEFORE the pre-registration existed

They tested the premise of the task that had been agreed, which is why they precede the
design rather than following it. Read-only; nothing built, adopted or written to the archive.

| script | what it computes | reads | writes |
|---|---|---|---|
| `cs_p0_control.py` | The control's degree distribution and downward-edge profile under production's rule; `DD-F1` reproduced independently on five named superstars; stranding share | artifact | `cs_p0_control.json` |
| `cs_p0b_gradient.py` | The same downward-edge question banded by popularity percentile, finer at the top — locates the defect as a superstar phenomenon rather than a top-decile one | artifact | `cs_p0b_gradient.json` |
| `cs_p0c_candidates.py` | **The decisive one.** Whether the crawl offers superstars any sub-decile candidate at all, before any cap; and the discard rate for the top 1% | artifact, crawl archive | `cs_p0c_candidates.json` |
| `cs_p0d_ranks.py` | Where sub-decile candidates sit in the returned list, and what share of lists saturate the source limit — separates "raise the limit" from "change the threshold" as remedies | artifact, crawl archive | `cs_p0d_ranks.json` |
| `cs_p0e_algorithms.py` | **Network probe.** Validates that `algorithm` is a closed enum by reading the rejection body, and measures each permitted value on the five superstars | artifact, live endpoint | `cs_p0e_algorithms.json` |
| `cs_p0f_symmetry.py` | Whether the source `score` is symmetric, the rank correlation between directions, and which endpoint refuses when mutual k-NN rejects an edge | artifact, crawl archive | `cs_p0f_symmetry.json` |

## `AS` arms — runner and scorer, split deliberately

**Both were committed before the run finished**, so the scorer could not be shaped by the
numbers it produces.

| script | what it computes | reads | writes |
|---|---|---|---|
| `as_run_arms.py` | **Collects only** — six permitted `algorithm` values × 200 stratified artists (40 per stratum, seed `20260729`), interleaved by artist so service drift hits all arms equally. Computes no criterion and makes no comparison | artifact, live endpoint | `as_raw_records.json` |
| `as_score.py` | Every criterion (`AS-C1`…`AS-C5`), both gates, the `AS-N` noise floor and the `3 × AS-N` decision rule. **No network** — re-runnable and independently reviewable | `as_raw_records.json`, artifact | `as_scores.json` |

`as_raw_records.json` (5.6 MB) is committed **on purpose**: re-scoring, or scoring
differently, needs no further requests against someone else's free service.

## What this directory cannot conclude

- **Nothing about whether `ALG-B`'s edges are any good.** It measures candidate *supply*,
  never edge quality. That is a listening question (`REQ-38`).
- **Nothing about stranding under `ALG-B`.** `AS-H2` measures a 58% drop in candidate
  supply for obscure artists and infers a stranding risk; confirming it needs a **built
  graph**, which does not exist. Deferred on "before any adoption decision".
- **Nothing about `threshold_15` or `limit_50` specifically.** `ALG-C` differs from
  production in four columns and the closed enum makes an isolating baseline impossible, so
  it is barred from one-knob attribution (pre-registration §1).
- **Nothing about artists the crawl has never seen.** The sampling frame is the adopted
  artifact, so `AS-C2` can count absent candidates but cannot rank them.
- **No adoption, no re-crawl, and no rule change.** `MKS-5b` still requires any cap-rule
  alternative to demonstrate its degree bound by simulation first, and that simulation is
  **not** in this directory.
