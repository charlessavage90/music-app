# `CXR-` — why the extended map was worse at finding unknown artists

**Role: FIGURES OWNER for the `CXR-` diagnosis.** Every number below is owned here and
cited elsewhere, never restated — including in `NEXT.md`, the execution log and the PR
body. Predictions were committed **before** any figure existed:
[`PREDICTIONS.md`](PREDICTIONS.md), commit `09a5656`.

**Scope: DESCRIPTIVE PROBES over two artifact files.** No routing was measured, no arm
ran, no criterion is fixed and nothing is adopted. **Resuming path-quality work is the
owner's trigger, never a session's** — this diagnosis exists because he reported a
regression and asked for it.

Scripts: `cxr_census.py` (`CXR-P1`/`P2`/`P3`, `M3`), `cxr_compression.py` (`M4`, `M5`).
Both parse the artifacts through the **shipped** `GraphStore`, not a second parser.

## Artifact identity

| | file | sha256 | artists | edges |
|---|---|---|---|---|
| **old** — live again since 2026-09-01 | `graph-msw-tu50.bin` | `43dd82bb…2be79cc8` | 58,838 | 1,315,684 |
| **extended** — live 2026-08-10 → 2026-09-01 | `graph-cxa-adopted.bin` | `bc0431c4…8e7ece46` | 88,685 | 1,618,164 |

29,892 artists added, 45 lost, 58,793 in both. Mean connections per artist **fell**, 22.36
→ 18.25 — **measured here, from the two artifacts' own CSR offsets.**

> ⚠ **Not the same number as the `CEX-` re-census's mean-degree figure**, which is coarser and
> is owned by `builder/analysis/2026-08-09-cex-recensus/README.md`. Two independently sourced
> figures for closely related quantities is exactly the shape that drifts, so: **this document
> owns only what it measured itself, and cites that one.** Flagged by the `CXR-` closeout audit
> after `PREDICTIONS.md` restated the re-census figure without citing it — that document is
> frozen and was deliberately left alone (see below).

---

## The finding, in one sentence

**The extension added ~29,900 artists that are exactly the ones the router wants — much
less listened-to than the existing population — in a shape the router cannot travel
through, and the act of adding them squeezed 21 % out of the only device that steers a
journey toward unfamiliar artists once you have pressed *Dig deeper* about five times.**

## `CXR-P2` — CONFIRMED, and by a wide margin. The new artists are cul-de-sacs.

Degree is the number of similarity connections an artist has in the map. Measured in the
extended artifact, so the two sets are on one ruler:

| set | n | median | mean | p10 | p90 | share with ≤ 2 |
|---|---:|---:|---:|---:|---:|---:|
| **added** | 29,892 | **4** | 7.38 | 1 | 18 | **34.36 %** |
| pre-existing | 58,793 | **19** | 23.77 | 3 | 50 | 8.07 % |

Median ratio **0.211**; `CXR-P2` was pre-set to fire below 0.50.

**`CXR-M5`: 6,123 of the added artists — 20.48 % — have EXACTLY ONE connection.** They
**cannot be a card in the middle of a journey at any price**, because a journey enters and
leaves every artist it passes through. The same figure for the pre-existing population is
4.27 %.

*(Exactly one, not "one or none": the artifact is pruned to the largest connected component,
so its minimum degree is 1 and an isolated artist cannot be in it. Verified against the
artifact — `deg.min() == 1`, zero occurrences of 0 — because the looser phrasing was written
here first and is the kind of claim that gets quoted onward. `findings/2026-07-25-mutual-knn-stranding.md`
uses "one connection or none" correctly: it measures BEFORE the component prune, where
degree 0 does occur.)*

The pre-existing artists were not harmed: their own paired degree change is **median +0.0,
mean +1.40**, and only 5.72 % lost any connection. **This is not a case of the old map
being damaged. The new material simply sits at the edges.**

## `CXR-P1` — CONFIRMED, and I predicted the opposite. The fame ruler moved under the router.

I predicted ≥ 70 % of the added artists would have no measured listener count, which would
have made this mechanism impossible. **The real figure is 0.11 %.**

| | measured | of | coverage |
|---|---:|---:|---|
| old artifact | 58,746 | 58,838 | 99.84 % |
| extended artifact | 88,559 | 88,685 | 99.86 % |
| **added artists** | **29,858** | 29,892 | **99.89 %** |

The ramp prices each artist by their **rank within the artifact's own measured
population**, rebuilt per artifact by design (`graph_store.fame_percentiles`). ~29,900
measured artists arriving below the existing population therefore moved everyone:

**`CXR-M3`, paired over the 58,793 artists in both maps: median shift **+0.0791**, mean
+0.0712, **99.30 % rose**, p10 +0.0199, p90 +0.1073.**

## `CXR-M4` — the shift is a SQUEEZE, not a level change, and that is what costs

A uniform rise would cost nothing: the router compares differences, so a constant added to
every artist is a per-hop toll, not a change of preference. It is not uniform. An artist
already at the top of the scale has nowhere to go, so the middle rises into them:

| position in the old frame | n | old mean | new mean | shift |
|---|---:|---:|---:|---:|
| 0.00–0.20 | 11,839 | 0.0992 | 0.1411 | +0.0419 |
| 0.20–0.40 | 11,721 | 0.3000 | 0.3896 | +0.0896 |
| **0.40–0.60** | 11,745 | 0.5000 | 0.6070 | **+0.1069** |
| 0.60–0.80 | 11,740 | 0.7000 | 0.7856 | +0.0856 |
| 0.80–0.90 | 5,873 | 0.8500 | 0.8979 | +0.0479 |
| 0.90–0.95 | 2,937 | 0.9250 | 0.9497 | +0.0247 |
| 0.95–0.99 | 2,350 | 0.9700 | 0.9800 | +0.0100 |
| **0.99–1.00** | 588 | 0.9950 | 0.9967 | **+0.0017** |

*(59 artists sit at the very top of the old frame and moved +0.0002 — the ceiling.)*

**Priced in the ramp's own units.** The gap between a top-1 % artist and a mid-scale one
— which is what the ramp converts into a preference — falls from **0.4950 to 0.3897, a
21.3 % loss**:

| presses of *Dig deeper* | preference for the mid-scale artist, old | extended |
|---:|---:|---:|
| 5 | 0.02475 | 0.01949 |
| 10 | 0.04950 | 0.03897 |
| 20 | 0.09900 | 0.07794 |

**Materiality, stated so it can be argued with.** `w_hop` is 0.02, so at twenty presses the
ramp is worth about five hops of cost and the loss is worth about one. Against `w_sim` at
3.0 the same loss is worth a similarity difference of only ~0.007. **So this is a real
force that got measurably weaker, not a dominant one** — and it matters because
`AM1.9` established the obscurity floor is fully spent by press five, leaving the ramp as
**the only remaining device** pushing a journey toward the unfamiliar.

## `CXR-P3` — DID NOT FIRE. The popularity currency held still.

Popularity (`pop_raw`, score-weighted in-degree, the currency of the floor and the
popularity-cliff term — **not** the fame ruler above) barely moved: paired **median
−0.0026, median |Δ| 0.0039**, against a 0.01 threshold; the top 1 % moved −0.0020.

**This matters for what it rules out.** The owner reports the first journey — before any
press — is also worse. **Nothing here explains that**, and neither does `JFX-C1`, which
measured no change at depth 0 across 297 pairs. That half of his report is unexplained, and
saying so is more useful than stretching these figures to cover it.

## How the two halves interlock

The added artists' median fame percentile is **0.3361** against **0.6081** for the
pre-existing population — they are precisely the unfamiliar artists the app exists to find,
and the ramp would prefer them strongly. Their median degree is **4** against **19**.

**So the map gained 29,892 artists the router wants and mostly cannot reach, and paid for
them by flattening the scale it uses to want them.** That is consistent with what the
pre-adoption run measured — journeys needing ~24 presses to reach where 20 used to get,
`JFX-` figures cited not restated — and with what the owner reported after three weeks of
use.

## What is NOT established here

- **No figure here says which artists a journey actually delivers.** These are properties
  of two files. Demonstrating that the extended map routes to its own new artists less
  often needs the `JFX-` routing harness (~2.6 h).
- **Nothing here says a fix works.** Three candidates are visible from these numbers — a
  degree floor on what the crawl admits, a fame ruler framed on something other than the
  shipped population, and a deeper crawl of the new artists rather than a wider one — and
  **each would need its own pre-registration and is the owner's call to start.**
- **The depth-0 half of the report is unexplained**, per `CXR-P3`.
