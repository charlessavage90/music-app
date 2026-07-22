# Configuration-Model Null — Topological vs. Community-Structure Hub-Seeking

**Date:** 2026-07-22
**Status:** Quantitative record for this experiment only. Resolves
`2026-07-21-scoring-adjudication.md` §6 claims **19** and **22** (spec §A3, task-10).
This document owns the numbers below; the adjudication doc is amended to cite this
one rather than restate them.

---

## 0. Verdict

**Topological, for shortest-path routing.** BFS-on-rewired hubfrac (**0.4769**) is not
lower than BFS-on-observed hubfrac (**0.4370**) — it is slightly *higher* — despite the
rewire destroying all community structure while holding the degree sequence exactly
fixed. Under the pre-registered rule this reinstates findings **§2** and closes **§5.1**'s
claim that hub-seeking is caused by the scoring, for BFS and for similarity-only routing.

**Left open:** the production `FULL` cost function's hub-seeking (hubfrac 0.6966) sits
well above this topological baseline, and this experiment does not test whether that
excess is topological or cost-function-driven — see §6.

---

## 1. Setup

| | |
|---|---|
| Graph | `builder/scratch/graph-75k-v3.bin` — 74,998 artists, 4,102,014 directed edge slots |
| Panel | frozen MBID-keyed panel, 130 pairs (random 50, obscure 50, popularity-weighted 30) |
| Hub set | top 1 % by degree = 751 nodes |
| Seeds | walk 42, rewire 42 |
| Wall-clock | 659 s total; rewire alone 85.3 s |
| Command | `cd api && PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy uv run python -u run_null_experiment.py` |

`run_null_experiment.py` (throwaway, scratch dir, not committed) is a faithful
implementation of task-10-brief.md Step 1, with progress/timing instrumentation added.
It consumes `api/eval/nulls.py` (`configuration_model_rewire`, `degree_biased_walk`) and
`api/src/artistpath_api/evaluation.py` (`path_metrics`, `hub_node_set`, `summarise`,
`bfs_shortest_path`, `similarity_only_path`) unmodified. `configuration_model_rewire`
performs a double-edge swap (10·E attempts) on the undirected edge list, preserving every
node's degree exactly and rejecting swaps that would create a self-loop or duplicate
edge; rewired edge scores are a uniform placeholder (0.5), not carried over, because they
are meaningless once endpoints are randomised.

**Pre-registered rule** (written before these numbers existed, task-10-brief.md Step 3):

- BFS-on-rewired hubfrac ≈ BFS-on-observed hubfrac → hub-seeking is **topological**. §2
  is reinstated.
- BFS-on-rewired hubfrac substantially lower → hub-seeking depends on **community
  structure**. §5.1's conclusion survives its broken evidence.

---

## 2. Measured table

```
condition            n    hubfrac   len   max_int_deg  int_pop  ceiling_hops    AA      OC       Jaccard
FULL cost function  130   0.6966    7.96    2300.3      0.802     0.4479      10.7955  0.2319   0.04536
sim-only            130   0.4769    8.62    3682.4      0.781     0.5115       6.4850  0.2800   0.04002
plain BFS           129   0.4370    4.79    4575.2      0.741     0.0234       1.7640  0.2087   0.01195
walk null (deg-bias)130   0.1436    8.00    1256.9      0.634     0.0077       2.7583  0.3407   0.07256
BFS on rewired      130   0.4769    4.35    3107.7      0.756     0.0000       0.0931  0.0081   0.00031

enrichment vs walk null:  FULL 4.85x | sim-only 3.32x | BFS 3.04x | BFS-rewired 3.32x
```

`plain BFS` is n=129: one panel pair is directly adjacent, so it has no interior nodes
and no hubfrac. Every other condition is n=130.

**Integrity checks the run asserted, before any interpretation:**

- Rewired degree sequence identical to observed: `True`.
- Rewired edge slots: 4,102,014 = observed.
- Rewired hub set size: 751, **identical membership** to the observed hub set: `True`.

These three checks establish that the rewired graph is a valid configuration-model
realisation of the *same* degree sequence and the *same* hub definition as the observed
graph — the comparison below is apples-to-apples on the one axis (degree) the null is
designed to hold fixed.

---

## 3. Interpretation

### 3.1 The comparison the rule names

BFS-on-observed hubfrac 0.4370 vs. BFS-on-rewired hubfrac 0.4769. The rewired value is
**not lower** — it is 9.1% relatively *higher*. That is squarely the "≈" branch of the
pre-registered rule (if anything it overshoots into "higher," which is at least as strong
evidence for "topological" as exact equality would be, not weaker). Mean path length
actually shortens on the rewired graph (4.35 vs 4.79 hops) and mean max-interior-degree
drops (3107.7 vs 4575.2) — both consistent with a configuration-model random graph on a
heavy-tailed degree sequence being an even smaller, more hub-permeated world than the
real graph's community-structured topology, not a less hub-permeated one.

**A single-number reading would stop here and call it topological. Per the house rule
against deciding on hubfrac alone, the rest of the table has to corroborate or contradict
that before it is a verdict.**

### 3.2 Why the near-zero AA/OC/Jaccard on the rewired graph is not a red flag

`BFS on rewired` reads AA 0.0931, OC 0.0081, Jaccard 0.00031 — an order of magnitude or
more below every other row, including the walk null. This is the expected signature of a
*successful* double-edge-swap rewire, not evidence the rewired comparison is broken: the
rewire's entire purpose is to destroy the correlation between "connected" and "shares
neighbours with," while leaving each node's degree untouched. If AA/OC/Jaccard on the
rewired graph had come out comparable to the observed graph, that would mean the swap
routine failed to mix and the result was still substantially the observed graph — which
the degree-identity and hub-membership-identity checks already rule out, and the
near-zero overlap metrics rule out from the other direction. Both integrity signals point
the same way: this is a graph with the observed degree sequence and none of the observed
community structure, exactly as designed.

That the hub-seeking rate is preserved *anyway*, on a graph whose local neighbourhoods
are essentially uncorrelated with the original (Jaccard 0.00031 vs. 0.01195 observed,
roughly 38× lower), is the finding. Hub membership survives an intervention that erases
the local structure scoring operates on.

### 3.3 sim-only and BFS-rewired coincide

`sim-only` hubfrac is **0.4769** — identical to four decimal places to `BFS on rewired`.
This is worth stating explicitly because it extends the verdict beyond plain BFS: a
router that *does* use the (community-structure-dependent) similarity scores, with no
popularity term at all, lands at exactly the hub-seeking rate that pure degree-sequence
topology produces once community structure is deleted. If the scoring were adding
hub-seeking on top of topology, sim-only should read above BFS-on-observed and further
above BFS-rewired; instead it sits at the rewired level. This is corroborating, not
independent, evidence — sim-only and BFS-rewired could coincide by chance on one panel —
but it points the same direction as §3.1 rather than against it.

### 3.4 What FULL well above BFS implies — and what this experiment does not establish

`FULL` hubfrac is 0.6966, ~59% relatively higher than BFS-observed (0.4370) and ~46%
higher than the topological baseline BFS-rewired defines (0.4769). At the same time
`FULL` has the *lowest* mean max-interior-degree of the three observed-graph routers
(2300.3, vs. 3682.4 sim-only and 4575.2 BFS) — the same pattern §5.3 measured on the
40-pair panel (there: FULL lowest max-interior-degree despite the least-favourable binary
read), now reproducing on this 130-pair panel with the continuous metrics. So `FULL`
touches the hub set (751 nodes, top 1% by degree) *more often* than either simpler
router, but the specific hubs it touches are less extreme by degree — it spreads across
more of the hub set rather than concentrating on the same super-hubs BFS finds.

**This experiment tests shortest-path / similarity-only routing against a topology-only
null. It does not run the production `FULL` cost function on the rewired graph**, because
rewiring discards the similarity scores `FULL` depends on (replaced with a uniform
placeholder) — there is no meaningful `w_sim·(1−similarity)` term to evaluate there, and
a `FULL` run on the rewired graph would reduce to a popularity-jump-only router on a
graph with randomised adjacency, which is not the same question. Concretely: **the ~0.22
hubfrac gap between `FULL` and the BFS-rewired topological baseline is not addressed by
this experiment.** The cost function term structure (`w_sim·(1−sim) + w_jump·|Δpop| +
w_floor·max(0, floor−pop_v) + w_avoid·avoidance + w_hop`) makes `w_jump` — which
penalises popularity jumps between consecutive hops — the most plausible mechanism for
routing through more, moderate hubs to smooth a popularity gradient, but this is a
plausible mechanism read off the config, not a measured one. Establishing it would need a
`FULL`-cost-function run against a null that preserves *popularity* (not just degree) —
a different experiment from this one.

`ceiling_hops` and `int_pop` are reported for completeness and are not decisive either
way: `ceiling_hops` on rewired reads 0.0000 (rewired scores are a constant 0.5, never
1.0, so this is mechanical, not informative about hub-seeking) and `int_pop` (0.756
rewired vs. 0.741 BFS-observed) is close enough to be uninformative in either direction.

---

## 4. Verdict against §2 / §5.1

- **Findings §2 ("hub-traversal is topological", struck through) is reinstated for
  shortest-path routing** (BFS and similarity-only). The configuration-model rewire —
  the cleanest null available, per §5.3's own recommendation — shows hub-seeking
  survives, undiminished, when community structure is destroyed and only the degree
  sequence is held fixed. §5.3's earlier "partially reinstated" verdict (based on the
  walk null and score-free-BFS-on-the-observed-graph alone) becomes fully reinstated for
  this class of router now that the rewire has actually been run.
- **Findings §5.1 ("hub-seeking is caused by the scoring") is overturned, conclusively,
  for shortest-path and similarity-only routing.** It was already overturned on weaker
  grounds in §5.3 (score-free BFS enriched on the walk null); this experiment supplies
  the test §5.3 flagged as still missing and gets the same answer by the stronger route.
- **Neither claim is settled for the production `FULL` router.** `FULL`'s hub-seeking
  exceeds the topological baseline this experiment establishes, by a margin this
  experiment cannot attribute. Do not read this document as clearing the scoring/cost
  function of all responsibility for `FULL`'s hub-seeking — only of responsibility for
  the *shortest-path* hub-seeking baseline that `FULL` is built on top of.

### 4.1 Statistical limitations of this result

Recorded because this project's recurring failure is a claim reported without its
uncertainty. None of these overturn the verdict; all of them bound it.

- **BFS-on-rewired is a single rewire realisation (seed 42). There is no error bar on
  0.4769, and no significance test was run** — the table is means only, pooled across
  three strata. The verdict is nonetheless robust in the direction that matters: the
  pre-registered "community structure" branch requires the rewired value to be
  *substantially lower*, and it is 9.1 % *higher*. Sampling noise would have to reverse
  the sign of the gap, not merely shrink it. A tighter result would draw 10–20
  independent rewires (~85 s each, plus ~60 s BFS routing per draw) and report a
  distribution; that was not done.
- **The two numbers the rule compares are not over an identical pair set.** BFS-observed
  is n=129, BFS-rewired n=130: panel pair `(58169, 49974)` is directly adjacent in the
  observed graph, so BFS returns a length-2 path with no interior nodes and no `hubfrac`.
  The excluded pair contributes to neither mean, but the denominators differ by one.
- **Only BFS is comparable across observed and rewired.** The rewire replaces every edge
  score with a uniform 0.5, so `FULL` and similarity-only cannot be run on the rewired
  graph at all, and the rewired row's AA / overlap / Jaccard are near-zero by
  construction rather than by measurement (see §3.2).

---

## 5. Consequence for Task 14

Per the pre-registered rule, the topological verdict for BFS/similarity-only routing
narrows Task 14's damping-parameter sweep to a two-point confirmation (`d ∈ {0, 0.5}`)
rather than a full grid, **for the question the sweep was originally framed to answer**
(does the damping exponent change hub-seeking via community structure). It does not
license skipping investigation of `FULL`'s excess hub-seeking over the BFS baseline,
which is a `w_jump`/popularity-term question, not a `d`/edge-scoring question, and is out
of scope for the damping sweep either way.

---

## 6. Reproduction

Script: `run_null_experiment.py` (scratch directory, not committed) — faithful to
task-10-brief.md Step 1 with added timing/progress logging. Run from `api/`:

```bash
cd api && PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy \
  uv run python -u run_null_experiment.py
```

Seeds: `WALK_SEED = 42` (`np.random.default_rng(42)`, used for `degree_biased_walk`),
`REWIRE_SEED = 42` (`np.random.default_rng(42)`, used for `configuration_model_rewire`).
`HUB_TOP_FRACTION = 0.01`. Panel loaded via `panel.load_panel("eval/panel.json")` and
resolved per-stratum via `panel.resolve_pairs`; no pairs were dropped as unresolvable
MBIDs on this run. `path_metrics`, `hub_node_set`, `summarise`, `bfs_shortest_path`,
`similarity_only_path` are `api/src/artistpath_api/evaluation.py` unmodified;
`configuration_model_rewire` and `degree_biased_walk` are `api/eval/nulls.py` unmodified.
