# Ceiling ordering headroom — measured from the archive, read-only

**Role: ACTIVE analysis record. Owns its figures.** Cites, never restates, the scoring
adjudication, the Phase 1 log, `../2026-07-23-track2-toll-calibration/` and
`../2026-07-25-track2f-toll-ladder/`.

**Not an experimental arm, so not pre-registered as one.** No path is routed, no criterion is
scored, nothing is adoptable. This is a structural measurement of the artifact's *inputs* —
the same class as the toll-calibration directory. **But it feeds a recommendation about
whether to spend a rebuild, so its decision rule is written and committed BEFORE the
measurement runs**, in this file, and the git history is the evidence of that order.

**No artifact is written.** The build runs in memory to recover quantities the artifact
does not retain; the graph object is discarded.

---

## The question

Track 2F established that the ceiling's *cheapness* is exhausted: no router-side toll moves
the primary outcome past −0.198, because 28.86 % of hops are structurally forced onto
maximally-similar edges and no price avoids them (figures owned by
`../2026-07-25-track2f-toll-ladder/`, `TF-D1`).

The untested half is **ordering**. `pipeline.py` stores `min(1.0, log1p(raw)/log1p(p99))`, so
every edge at or above the 99th percentile of raw strength is written as exactly `1.0` and the
artifact **retains no information distinguishing them**. At a node whose exits are all
saturated, the router today picks among them on a cost tie, broken by node id.

**So: how much ordering information does the clip actually destroy, and is it enough to change
a routing decision?** If the tied edges have near-identical true strengths, a rescale re-ranks
nothing and the rebuild is pointless. If they span a wide range, the rescale has real headroom
and the case is made *before* an artifact changes.

## What is measured

The build is reproduced from the archive under the adopted `BuilderConfig`, up to and
including `mutual_knn_cap`, `symmetrise` and `largest_component`, so the edge set is the
**final** one. For every surviving edge two quantities are recovered:

- `stored` — the clipped value the artifact holds (`1.0` for a saturated edge).
- `unclipped` — `log1p(raw)/log1p(p99)`, the same expression **without** the `min`. ≥ 1.0
  exactly on the saturated edges.

**Identity gate, run first:** the in-memory rebuild is serialised to a scratch path and its
sha256 compared to the adopted artifact `4cb84ef9…b061dc8`. A mismatch means the archive does
not reproduce the adopted graph and **every figure below is void** — several graphs exist in
`builder/scratch/` and they are not interchangeable.

### The primary quantity, and why it is in `w_hop`

For each node holding ≥ 2 ceiling edges, the **cost spread** a rescale would induce among
that node's own ceiling exits:

```
spread(node) = w_sim · (s_max − s_min)      over that node's ceiling edges
```

where `s` are the unclipped values renormalised so nothing saturates (the minimal rescale:
same formula, divisor moved from p99 to the max). Today that spread is **exactly zero** —
every ceiling edge contributes `w_sim · (1 − 1.0)`.

It is expressed in multiples of **`w_hop`** because that is the currency the toll-calibration
directory established for reading a similarity cost against an alternative, and the currency
Track 2F's ladder was priced in — so the two measurements are directly comparable. `w_sim`
and `w_hop` are read from `ApiConfig`, cited and not restated.

## Decision rule — fixed now, before the measurement

| Reading | Threshold | What it licenses |
|---|---|---|
| **Wide** | median per-node ceiling cost spread **≥ 1 × `w_hop`** | The clip destroys ordering large enough to flip routing decisions. **Recommend pre-registering the builder-side p99 rescale**, and it goes to the rebuild seam with the p99-shift measurement and the blank-name remediation. |
| **Narrow** | median per-node ceiling cost spread **< 1 × `w_hop`** | The destroyed ordering is smaller than one extra step, so re-ranking cannot change which route wins. **Recommend against the rescale**, and the ceiling question closes on both halves — which would make Track 2F's `TFR0` the end of the ceiling line rather than half of it. |

**Why 1 × `w_hop`.** `w_hop` is what one extra step costs. If reordering two neighbours moves
their relative cost by less than one step, the choice between them is dominated by what
happens downstream and the re-rank is noise. If it moves by more than one step, it can flip a
decision on its own. This is the toll-calibration directory's own logic for reading a
similarity cost against an alternative, applied to a rescale instead of a toll.

**Also reported, against the same yardstick:** the fraction of nodes whose spread exceeds
**7.5 ×** and **30 × `w_hop`** — the two toll magnitudes that respectively did and did not
move the outcome in Track 2F — so the headroom can be read directly against a mechanism whose
effect size is already known.

**Reported separately, because Track 2F says it is where the forced hops live:** the same
spread restricted to the **fully saturated** nodes (every exit at 1.0), and to the 24
pre-registered endpoints. `TF-D1` found exactly 2.0 forced ceiling hops per journey, one
leaving the start artist and one arriving at the destination; those are precisely the hops a
rescale would re-rank and a toll provably cannot.

## What this measurement cannot say

**It can only say whether a rescale would *change* routes, never whether it would *improve*
them.** Change is necessary and not sufficient. A wide reading licenses pre-registering the
probe; it does not predict its result, and it certainly does not license adoption — that
still needs a pre-registered arm, the offline gates, and a blind listen.

It also says nothing about F2's depth clause. A rescale is static, like every Track 2F arm.
