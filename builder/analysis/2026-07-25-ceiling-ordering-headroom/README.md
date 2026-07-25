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

**Identity gate, run first:** the in-memory rebuild is serialised **to bytes that are hashed
and discarded — no file is written** — and its sha256 compared to the adopted artifact
`4cb84ef9…b061dc8`. A mismatch means the archive does
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

---

# Result: **WIDE**, by a factor of ten

Both gates passed **before any figure was read**:

- **Identity gate.** The in-memory rebuild serialises to `4cb84ef9…b061dc8` — it reproduces
  the adopted artifact exactly, so this measures the graph the app actually routes on.
- **Formula gate.** The unclipped expression agrees with the real `rescale_scores` on all
  **3,951,579** unsaturated edges. The only difference is the clip.

**Saturated edges: 39,952 of 3,991,531 directed edges = 1.00 %.** That is the p99 clip doing
exactly what it says, and on its own it looks negligible. It is not, because of *where* those
edges are.

## Cost spread the clip erases, in multiples of `w_hop`

Per node, across that node's own ceiling exits. Under the current clip this spread is
**exactly zero** by construction. Renormalisation factor k = 0.7776 (the conservative,
pre-registered rescale; the largest unclipped value is 1.286 in p99 units).

| node set | n | median | mean | p10 | p90 | ≥ 1× | ≥ 7.5× |
|---|---|---|---|---|---|---|---|
| all nodes holding ≥ 2 ceiling edges | 1,201 | **10.01** | 9.82 | 1.98 | 16.83 | 95.5 % | 64.2 % |
| **fully saturated** (every exit at the ceiling) | 303 | **14.50** | 14.72 | 11.59 | 18.67 | 100 % | 98.3 % |
| **the 24 pre-registered endpoints** | 22 | **13.51** | 14.08 | 12.01 | 19.34 | 100 % | **100 %** |

**Decision rule verdict: WIDE.** The pre-registered threshold was a median of 1 × `w_hop`; the
measurement is **10.01 ×**.

## Per-endpoint detail

| endpoint | spread (× `w_hop`) | exits at ceiling |
|---|---|---|
| Aphex Twin | 22.03 | 40/40 — fully saturated |
| Miles Davis | 19.34 | 26/34 |
| Taylor Swift | 16.18 | 46/46 — fully saturated |
| Bob Dylan | 15.89 | 43/43 — fully saturated |
| Pink Floyd | 15.46 | 50/50 — fully saturated |
| Daft Punk | 14.08 | 50/50 — fully saturated |
| Johnny Cash | 14.04 | 19/19 — fully saturated |
| R.E.M. | 13.94 | 47/47 — fully saturated |
| The Rolling Stones | 13.93 | 50/50 — fully saturated |
| Muse | 13.90 | 50/50 — fully saturated |
| Michael Jackson | 13.57 | 39/39 — fully saturated |
| Nirvana | 13.44 | 50/50 — fully saturated |
| Gorillaz | 13.29 | 47/47 — fully saturated |
| Metallica | 13.25 | 48/48 — fully saturated |
| Coldplay | 13.15 | 50/50 — fully saturated |
| System of a Down | 12.90 | 47/47 — fully saturated |
| Arctic Monkeys | 12.62 | 47/47 — fully saturated |
| Madonna | 12.61 | 29/29 — fully saturated |
| Linkin Park | 12.07 | 48/48 — fully saturated |
| The Beatles | 12.01 | 50/50 — fully saturated |
| The Shins | 11.19 | 38/38 — fully saturated |
| Radiohead | 10.95 | 50/50 — fully saturated |

**21 of the 22 resolved endpoints are fully saturated.** This does not contradict the
toll-calibration README's Q4 ("eight are fully saturated"): Q4 counts nodes whose **50**
neighbours are all at the ceiling, and this counts nodes whose **every** exit is, whatever the
degree. Both are correct under their own definition, and the broader one is the
routing-relevant one — Johnny Cash with 19/19 has exactly as little similarity signal to route
on as The Beatles with 50/50.

## What this means, read against Track 2F

The erased ordering is **the same order of magnitude as a toll that demonstrably changed
routing**. Track 2F's ladder moved paths substantially at 7.5 × `w_hop` (`TF1`, −0.139) and
further at 15 × (−0.177); **64.2 % of affected nodes, and 100 % of the pre-registered
endpoints, are having cost differences larger than 7.5 × `w_hop` erased.**

**State the disanalogy honestly:** a toll *adds* the same cost to every ceiling edge, while a
rescale *redistributes* among them — some cheaper, some dearer. They are different operations
of comparable magnitude, so this is a calibration of size, not a prediction of effect.

**The mechanism, and it is the clearest statement of the defect yet reached.** At a fully
saturated node every exit carries `w_sim · (1 − 1.0) = 0`, so the similarity term contributes
**nothing to the choice**. `w_degree_hub` is 0 by default and avoidance is empty on a
`known` walk, so what remains to discriminate 50 candidates is the **popularity** terms —
the jump term and, where live, the floor. **At exactly the famous artists a journey starts and
ends at, the router cannot see which neighbour is most similar, and picks on popularity
instead.** That is a mechanistic account of why paths stay in famous territory, and it is the
half no router-side knob could ever reach: Track 2F's `TF-D1` measured 2.0 structurally forced
ceiling hops per journey, and these are those hops.

## What this still does not license

**Change is not improvement.** This licenses *pre-registering* the builder-side rescale as a
probe with a real expected effect size. It does not predict the probe's result, and it
certainly does not license adoption — that still needs the pre-registered arm, the offline
gates, and a blind listen.

It also says nothing about F2's depth clause. A rescale is static, like every Track 2F arm.
And the rescale would change **every** score in the graph, not only the saturated ones, so it
is an artifact change with a blast radius far beyond the 1.00 % of edges measured here — the
p99-shift measurement already queued at the rebuild seam is what sizes that.
