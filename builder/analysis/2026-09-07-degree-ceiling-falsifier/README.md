# `DCF-` — the degree ceiling, the added artists, and which edges it holds back

**Role: FIGURES OWNER for the `DCF-` probe. ACTIVE.** Every figure below is owned here
and is **cited elsewhere, never restated**. Raw records beside this file:
[`dcf_results.json`](dcf_results.json) (the ceiling sweep),
[`dcf_results_bridge.json`](dcf_results_bridge.json) (the two bridge arms),
[`dcf_edge_fate.json`](dcf_edge_fate.json) and
[`dcf_edge_fate_per_artist.csv.gz`](dcf_edge_fate_per_artist.csv.gz) (the edge-fate read,
aggregates and raw rows), [`dcf_provenance.json`](dcf_provenance.json).

**Scope: DESCRIPTIVE STRUCTURAL PROBES.** Graphs built in memory and two artifacts read.
**No path was built, no routing criterion was evaluated, nothing is adopted and no rule
change is proposed.** The cap-rule decision is parked and the owner's
([`specs/2026-09-06-own-similarity-design.md`](../../docs/superpowers/specs/2026-09-06-own-similarity-design.md)
§9). This is not an `LBD-` arm.

---

## 0. This knob is not new, and the part that is

**Track B swept it.** `TUw-50-100` is this exact rule at ceiling 100, isolated against
`TUw-50-50` by the ceiling alone, scored on both archives against a committed
pre-registration. It **fired `CRS-C4`'s material hub-transit bar on the broad famous
class**, moving it the most of any cell in the bound-100 set. Figures are owned by
[`findings/2026-07-30-track-b-cap-selection-results.md`](../../docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md)
and its raw `cb_scores.json`; they are **cited here and never restated**.

**The gap this probe covers, and the only one:** both Track B sweeps predate the crawl
extension, so neither archive's graphs contained the ~29,900 artists the `CXA` crawl
added, and **no criterion in either pre-registration measures that set's degree or its
dead-end share**. That set is the whole subject of §2–§3.

> ⚠ **`CRS-C4` is not re-measured here and Track B's result on it stands against any
> ceiling raise until someone does.** This probe cannot weaken it: hub transit is a
> property of paths the router chooses, and no path was built.

## 1. Inputs, pinned, and the provenance demonstrated rather than trusted

Artifacts under `builder/scratch/` are gitignored and **not interchangeable**; each was
sha256-verified against its own `.bin.json` manifest sidecar before being read, and parsed
by the **shipped `GraphStore`** (the `cxr_census.py` precedent).

| input | identity |
|---|---|
| the served map | `graph-msw-tu50.bin`, sha `43dd82bb…2be79cc8`, 58,838 artists |
| the extended map | `graph-cxa-adopted.bin`, sha `bc0431c4…8e7ece46`, 88,685 artists |
| extended archive | `grt-archive-algb`, ALG-B sub-tree, **117,302 payloads**, read-only |
| served-lineage archive | `grt-archive-algb.pre-cex-snapshot`, **75,000 payloads**, read-only |

**Provenance is demonstrated, not asserted** ([`dcf_provenance.py`](dcf_provenance.py)).
Manifest sidecars record a build's config but **not its archive directory**, so "this tree
built that artifact" cannot be read off them. Tested by membership instead: all **88,685**
nodes of the extended artifact have a payload in the extended tree, and all but **55** of
the 29,892 added artists have none in the `.pre-cex-snapshot` sibling. The added /
pre-existing split reproduces the `CXR` diagnosis's counts exactly — **29,892 added,
58,793 pre-existing** — which is the read validating itself against figures it did not
compute (`CXR-P2`, cited, never restated).

*(55 is not an error: an artist can be crawled and still be absent from the served map, via
a drop list or the largest-component prune, and would then read as "added" on the next
build without the crawl having discovered it.)*

## 2. Method, and why the two probes' flags differ

Both build through the **shipped** `build_from_archive` / `trimmed_union_cap`. Nothing is
serialised to an artifact and no acceptance check runs. Archives are opened through a
`ReadOnlyArchive` whose `put()` raises (the standing `GRT-A1` condition).

| | §3 ceiling sweep | §5 edge fate | §4 bridge arms |
|---|---|---|---|
| archive | extended (117,302) | pre-CEX (75,000) | extended (117,302) |
| `union_degree_ceiling` | **50 / 100 / 200 / 20000** | 50 | **50 / 20000** |
| `require_fame` | False | False | False |
| `drop_unlistenable` | **False** | **True** | **True**, via override |
| every other knob | default | default | default |

**The `drop_unlistenable` difference is not an inconsistency — it is forced, and the reason
is worth recording.** `graph-cxa-adopted.bin`'s own manifest says `drop_unlistenable: true`
over the extended archive, which **cannot be done at HEAD**: the shipped ALG-B census covers
75,000 artists against that archive's 117,302, so the `ULC-F1` guard refuses on the 42,302
difference. It was possible at the commit that artifact records — `7404a4c`, *"CXA- Task 2:
ship the re-censused payload and repoint the ALG-B default"* — and `4b4a0a6` (`L4-T1`)
repointed the default **back** to the 75,000-artist list. The re-censused payload
(`unlistenable_drop_algb_20260809.json`, 117,302 censused) is still in package data, so §4
applies it through the **shipped per-invocation override** (`unlistenable_list_path`),
which is what that parameter exists for and which changes no default.

**Consequence, stated so it is not read past:** §3's arms sit on a **larger population** than
the `CXA` artifact, so `CXR-P2`'s absolute figures are **not** their reference — the
within-build pre-existing set is. §4 exists to put the same comparison on `CXR-P2`'s own
ruler.

**Instrument gates, both halves, all passed.** A green result from an instrument never shown
to go red is not evidence.

| probe | green | red |
|---|---|---|
| ceiling sweep | control's max degree ≤ 50, the rule's stated bound (`CRS-G2`'s check) | every raised arm exceeds degree 50, so the knob reaches `trimmed_union_cap` |
| edge fate | the reconstruction reproduces the served artifact's edge set **exactly** — 657,842 pairs both sides, **zero** on either side only, agreement 1.0 | the three stages hold strictly decreasing edge counts |

> The edge-fate green half is the load-bearing one. It means the post-drop population and
> the stage order are the **shipped build's**, not an approximation — so `q4`'s stated
> weakest link (its top-*j* step is a reconstruction, not the builder's code path) **does
> not apply to §5**. Instead of reconstructing, §5 calls the shipped `trimmed_union_cap`
> twice: once with a ceiling asserted at run time to be non-binding, isolating the union
> step exactly, and once at the shipped 50.

---

# MEASURED

## 3. The falsifier: raising the ceiling, on the extended archive

Q4 named this falsifier verbatim — *"a build of the extended archive with
`union_degree_ceiling` raised, showing the added set's share-≤2 stays near 34 %"* — and did
not run it. It is run. **Every raised arm's isolating baseline is the ceiling-50 control on
the same archive, differing in exactly one column.**

**The added set (n = 29,892).** *All columns are counts of connections; "share ≤ 2" is the
dead-end share, and "absent" is the share the build drops entirely.*

| ceiling | median | mean | **share ≤ 2** | share = 1 | absent | p90 |
|---:|---:|---:|---:|---:|---:|---:|
| **50 (shipped)** | 5 | 7.96 | **32.10 %** | 19.12 % | 0.31 % | 19 |
| 100 | 6 | 10.00 | 25.48 % | 14.18 % | 0.00 % | 24 |
| 200 | 7 | 11.61 | 22.02 % | 11.97 % | 0.00 % | 29 |
| 20000 *(does not bind)* | 9 | 15.18 | **18.41 %** | 10.04 % | 0.00 % | 45 |

**The pre-existing set (n = 58,793), the within-build reference.**

| ceiling | median | mean | share ≤ 2 | absent |
|---:|---:|---:|---:|---:|
| 50 | 20 | 24.33 | 7.47 % | 0.04 % |
| 100 | 26 | 35.65 | 5.29 % | 0.00 % |
| 200 | 33 | 45.25 | 4.26 % | 0.00 % |
| 20000 | 51 | 64.53 | 3.36 % | 0.00 % |

**The cost side.** `top1pct_degree_mass_frac` is `CRS-C3`'s concentration measure, lifted
unchanged from `cb_metrics.py` — the share of all edge **endpoints** held by the top 1 % of
nodes **by degree**. Degree, never fame and never `pop_raw`.

> ## ⚠ FORWARD CORRECTION, 2026-09-07 — read before using any `top1pct_degree_mass_frac` figure below
>
> **Every number in this document stands exactly as measured. What changes is what one of them
> can be read as evidence of.** A derivation commissioned by the `DFA-` probe established that
> where at least 1 % of nodes sit at the degree ceiling, this statistic reduces algebraically to
> `ceiling ÷ (100 × mean degree)` and **cannot see how edges are arranged at all**. Reasoning and
> its checks are owned by
> [`../2026-09-07-degree-floor-at-admission/README.md`](../2026-09-07-degree-floor-at-admission/README.md)
> §8; this note is a pointer and adds no figure here.
>
> **Which of this document's own arms the measure is valid on**, tested against
> `dcf_results.json` and `dcf_results_bridge.json` themselves:
>
> | arm | at least 1 % of nodes at the boundary? | is its mass figure a concentration measurement? |
> |---|:--|:--|
> | §3 ceiling **50**, **100**, **200** | **yes** (tie pool 9.7×, 5.3× and 1.9× the admitted cut) | **no** — it equals `ceiling ÷ (100 × mean degree)` to within 1 part in 10⁴ |
> | §3 ceiling **20000**, non-binding | **no** (0.01×) | **yes** — the only §3 arm where it is |
> | §4 bridge ceiling **50** | **yes** (10.7×) | **no** |
> | §4 bridge ceiling **20000**, non-binding | **no** (0.01×) | **yes** |
>
> **So the rise across §3's ceiling 50 → 100 → 200 is the ceiling rising against mean degree,
> not evidence that those arms concentrated the graph onto hubs.** The ceiling-200 arm is the
> closest to leaving that regime and is still inside it.
>
> **This does NOT rewrite this section's read, and the read does not depend on the corrected
> quantity.** The conclusion that the non-binding arm is far more concentrated **stands**, and it
> is supported independently by two figures in the tables below that are unaffected: its **max
> degree** (15,347 in §3 and 14,180 in §4, against the ceiling's 50) and its **edge count**. Its
> own mass figure is also unaffected, being the arm where the statistic works.
>
> **Nothing else here is touched.** §5's hub-attachment split is a top-**decile** membership
> read, not this statistic. `CRS-C4` hub transit is a routing measure and was never computed
> here. The cap-rule decision remains parked and the owner's.

| ceiling | nodes | edges | max degree | mean degree | top-1 %-by-degree mass |
|---:|---:|---:|---:|---:|---:|
| 50 | 103,902 | 890,208 | 50 | 17.14 | 0.02918 |
| 100 | 105,145 | 1,269,619 | 100 | 24.15 | 0.04139 |
| 200 | 105,256 | 1,590,329 | 200 | 30.22 | 0.06621 |
| 20000 | 105,351 | 2,254,246 | **15,347** | 42.80 | **0.18569** |

**The 20000 arm's ceiling does not bind** (max degree 15,347 < 20000), asserted rather than
assumed — so it is the **top-*j* union itself**, and therefore the upper bound on what *any*
ceiling change could deliver. Its concentration lands close to Track B's own uncapped
reference row (cited, not restated: Track B results §1), which is the row that was
**barred from candidacy** there.

⚠ **The top-1 % boundary is tie-dominated at the shipped ceiling** — 10,390 nodes sit in
the cut and the boundary degree is 49 — so *which* nodes are in that set is arbitrary among
equal degrees. Track B's own weakest-link note says the same of its `C4` set. The mass
figure is stable; the membership is not.

## 4. The bridge arms — the same comparison on `CXR-P2`'s ruler

Two arms only — the shipped ceiling and the non-binding one — built on the **same extended
archive** but with the re-censused `ULF-` payload applied through the shipped override, so
the population is the `CXA` artifact's own.

**It reproduces that population exactly: 88,685 nodes, the artifact's own count.** The
added-set figures below are *this probe's own measurements*, and they land on `CXR-P2` /
`CXR-M5` to the decimal (cited, not restated) — which is the strongest validation available
that the read is being taken correctly. The control also reproduces Q4's forward arithmetic:
Q4 predicted 4,305 added artists have more than two candidate connections and end with two
or fewer, and **4,305** is exactly the number that leave the dead-end group when the ceiling
is lifted.

| | ceiling 50 (shipped) | ceiling 20000 (does not bind) |
|---|---:|---:|
| nodes | **88,685** | 89,691 |
| edges | 809,082 | 2,050,901 |
| max degree | 50 | 14,180 |
| top-1 %-by-degree mass | 0.02741 | **0.17617** |
| **added — median** | 4 | 8 |
| **added — share ≤ 2** | **34.36 %** | **19.96 %** |
| added — share = 1 | 20.48 % | 10.86 % |
| pre-existing — median | 19 | 51 |
| pre-existing — share ≤ 2 | 8.07 % | 3.64 % |

**Restored edges, ceiling 50 → 20000:** 206,837 in total, **94.6 % to a top-decile-by-degree
hub** and 5.4 % not. **4,305** added artists leave the two-or-fewer group — **3,368 on hub
edges alone**, 135 on non-hub edges alone, 802 on both.

**So the falsifier fails, on `CXR-P2`'s own ruler.** The added set's dead-end share does not
stay near its current level when the ceiling is lifted: it falls from 34.36 % to 19.96 %,
and the residual 19.96 % is what ListenBrainz's lists genuinely do not supply.

**Two documents were corrected as a consequence of this section**, by pointer and without
restating anything above: `findings/2026-09-06-lbd-plan-review.md`'s premise section and
`NEXT.md`'s `LBD-` block both characterised this sparsity as *mostly* ours, and §4 measures
it as the **minority** cause. Each carries a forward-correction note naming this section as
the figures owner. **Only the magnitude moved** — both documents' mechanism, and the three
consequences they draw for the `LBD-` pre-registration, are confirmed by these results.


## 5. Which edges the raised ceiling gives back, and to whom

**The question a dead-end count cannot answer.** Restoring a tail artist's link to a
well-connected artist and restoring a link between two obscure artists are different
products: the first puts an obscure artist one hop from a hub, the second builds routes
through the tail. Every edge a raised arm restores to an added artist is classified by what
sits at the **other end**, by **degree within that arm's own built graph** — not fame, not
`pop_raw`, and not the served map's degrees.

| ceiling | restored edges | → top-decile hub | → another added artist | → pre-existing non-hub | **share to a hub** |
|---:|---:|---:|---:|---:|---:|
| 100 | 58,414 | 53,085 | 672 | 4,657 | **90.9 %** |
| 200 | 106,147 | 99,604 | 981 | 5,562 | **93.8 %** |
| 20000 | 212,832 | 205,185 | 1,276 | 6,371 | **96.4 %** |

**Who leaves the two-or-fewer group, and on which kind of edge.**

| ceiling | left ≤ 2 | on hub edges only | on non-hub edges only | on both | (was absent from the control) |
|---:|---:|---:|---:|---:|---:|
| 100 | 2,028 | 1,599 | 119 | 310 | 14 |
| 200 | 3,045 | 2,507 | 89 | 449 | 29 |
| 20000 | 4,112 | 3,475 | 80 | 557 | 41 |

Added artists gaining at least one hub edge: 15,612 / 18,852 / 21,198. Gaining at least one
non-hub edge: 4,229 / 4,863 / 5,177.

## 6. Which of the two cap steps kills an edge, by fame band

**Attribution — read this before any rate in the table.** Every archive edge is counted **at
both ends**, once in each endpoint's own band, so a row reads *"what happened to the edges of
the artists in this band"* and band totals are double the pair counts. **Bands are FAME
PERCENTILE computed within the served artifact** by the shipped `GraphStore.fame_percentiles`
(0 = nobody on this map has fewer recorded listeners, 1 = nobody has more). **Every other
column is a count of edges or connections.** No degree and no `pop_raw` appears in this read.

Stage totals, undirected pairs: archive **2,421,894** → after the top-*j* cut **1,695,438** →
after the degree trim **657,858** → after the component prune **657,842**. Max degree after
the union and before any trim: **11,806**.

| band | artists | med. own list | med. reverse-only | med. slots | total slots | died top-*j* | died trim | % top-*j* | % trim | **med. kept** | **share ≤ 2 kept** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0–0.1 | 5,982 | 9 | 0 | 9 | 139,420 | 30,324 | 60,417 | 21.75 % | 43.34 % | **5** | **29.96 %** |
| 0.1–0.2 | 5,877 | 14 | 0 | 14 | 152,202 | 22,452 | 62,650 | **14.75 %** | 41.16 % | 7 | 19.12 % |
| 0.2–0.3 | 5,863 | 21 | 0 | 21 | 217,619 | 43,474 | 87,824 | 19.98 % | 40.36 % | 10 | 13.53 % |
| 0.3–0.4 | 5,870 | 28 | 0 | 28 | 264,215 | 60,565 | 101,405 | 22.92 % | 38.38 % | 13 | 9.95 % |
| 0.4–0.5 | 5,876 | 37 | 0 | 37 | 310,755 | 74,262 | 118,471 | 23.90 % | **38.12 %** | 15 | 6.47 % |
| 0.5–0.6 | 5,877 | 50 | 0 | 50 | 367,082 | 89,332 | 144,485 | 24.34 % | 39.36 % | 19 | 4.41 % |
| 0.6–0.7 | 5,869 | 72 | 0 | 74 | 445,874 | 119,858 | 171,478 | 26.88 % | 38.46 % | 24 | 2.21 % |
| 0.7–0.8 | 5,874 | 85 | 2 | 90 | 558,922 | 167,785 | 214,514 | 30.02 % | 38.38 % | 29 | 1.41 % |
| 0.8–0.9 | 5,875 | 90 | 9 | 100 | 718,228 | 233,510 | 285,097 | 32.51 % | 39.69 % | 38 | 0.89 % |
| 0.9–1.0 | 5,875 | 90 | 48 | 137 | 1,667,621 | 611,152 | 827,199 | **36.65 %** | **49.60 %** | **48** | **0.55 %** |

**The two currencies disagree about which band is treated worst, and both are true.** By
**share of slots lost**, the top band is worst — it loses 86.3 % of its slots against the
bottom band's 65.1 %. By **connections retained**, the bottom band is worst by an order of
magnitude — median 5 against 48, and 29.96 % of its artists end as dead ends against 0.55 %.
Neither is the summary; a share lost is not comparable across bands when list length varies
from a median of 9 to a median of 137.

**How a band whose artists hold 9-long lists loses a fifth of its slots at a cut that only
deletes what falls outside a top fifty.** The rate is a property of the band's **edges**, not
its artists: only **13.9 %** of bottom-band artists lose anything at the top-*j* cut, and the
band's 21.75 % is carried by that minority, whose slot counts sit far above the band median
(mean 23.3 against median 9). Splitting those **831** artists by what makes a loss *possible*:
**484** have reverse slots (someone listed them, unreciprocated) and **347** hold own lists
longer than fifty. **Across all ten bands, the number of artists losing at the top-*j* cut
with neither is exactly ZERO** — the invariant the rule implies, and a structural check on
the read rather than a coincidence.

**Which band's artists lose anything at the top-*j* cut, at all:** 13.9 % / 16.2 % / 27.5 % /
34.8 % / 41.6 % / 49.3 % / 64.2 % / 80.8 % / 93.5 % / 98.7 %, bottom band to top.

**What the top-*j* cut selects against, base-rate corrected.** The top fame band holds 24–40 %
of every band's edges to begin with, so raw death shares cannot be read. Enrichment = share of
a band's top-*j* deaths pointing at column *c*, over the share of its archive edges pointing at
*c*. **1.00 means the cut is indifferent to what is at the other end.**

| losing artist's band | → 0.1–0.2 | → 0.2–0.3 | → 0.4–0.5 | → 0.5–0.6 | → 0.8–0.9 | → 0.9–1.0 |
|---|---:|---:|---:|---:|---:|---:|
| 0.0–0.1 | 0.29 | 0.42 | 0.50 | 0.61 | 1.06 | **1.47** |
| 0.1–0.2 | 0.39 | 0.60 | 0.75 | 0.77 | 1.02 | **1.74** |
| 0.2–0.3 | 0.44 | 0.66 | 0.82 | 0.85 | 1.04 | 1.50 |
| 0.3–0.4 | 0.43 | 0.69 | 0.88 | 0.86 | 1.03 | 1.41 |
| 0.4–0.5 | 0.46 | 0.68 | **0.93** | 0.94 | 0.98 | 1.35 |
| 0.5–0.6 | 0.47 | 0.70 | 0.92 | 0.93 | 0.94 | 1.31 |
| 0.6–0.7 | 0.52 | 0.69 | 0.84 | 0.83 | 0.93 | 1.29 |
| 0.7–0.8 | 0.50 | 0.69 | 0.78 | 0.77 | 0.92 | 1.27 |
| 0.8–0.9 | 0.57 | 0.74 | 0.77 | 0.75 | 0.91 | 1.23 |
| 0.9–1.0 | 0.70 | 0.81 | 0.88 | 0.87 | 1.04 | 1.05 |

Full ten-by-ten crosstabs for every fate are in `dcf_edge_fate.json`.

---

# WHAT IS NOT ESTABLISHED HERE

- **No routing, anywhere.** No path was built, no `CRS-C4` hub transit was computed, and no
  criterion of any pre-registration was evaluated. **A candidate-supply gain is not a
  delivered-connection gain, and neither is a journey the router would choose.** §5's hub
  split says what a raised ceiling *offers*; it says nothing about what the router would
  take, and the router is known to decline structure of exactly this kind at production
  weights (`CRS-C5`/`R2`, cited).
- **Track B's `C4` result stands against any ceiling raise until re-measured.** Nothing here
  touches it, weakens it, or is evidence about it.
- **"Hub" in §5 means top-decile BY DEGREE within that arm**, not famous and not popular.
  The three quantities are not interchangeable and §5 does not license a fame claim.
- **§3's absolute levels are on a larger population than the `CXA` artifact's** and are not
  comparable to `CXR-P2`'s figures; §4 is the arm that is. Within §3 the comparison is
  clean, because every arm shares that population.
- **The `.pre-cex-snapshot` and extended archives are different populations**, so §6's bands
  and §3's arms are not on one ruler and no figure is carried between them.
- **§6 is one archive, one cap rule, one build.** It says which step deletes an edge; it does
  not say what a different `union_top_j` would do — no value but 50 was built.
- **The drop lists in §3 under-filter.** `drop_no_release_tail` and `drop_featured_credit`
  are keyed by algorithm, not population, and were censused on the smaller one (9,501 and
  1,940 artists dropped here). They carry no population guard, unlike `drop_unlistenable`.
  Held identical across every arm, so the comparison is unaffected; the absolute levels are
  this probe's own.
- **Nothing about the fame ruler.** §6 bands by the served artifact's own fame percentiles
  and never asks whether that frame is right — `CXR-P1`/`M4` own that question.
- **The top-1 %-by-degree set is tie-dominated at the shipped ceiling** (§3), so its
  membership is selection-order arbitrary; only the mass figure is stable.
- ⚠ **ADDED 2026-09-07 — NO CONCENTRATION COST IS ESTABLISHED BY THE CAPPED ARMS, AND NONE IS
  RULED OUT.** On every arm here whose ceiling binds — §3's 50, 100 and 200, and §4's 50 —
  `top1pct_degree_mass_frac` is algebraically `ceiling ÷ (100 × mean degree)` and is
  **structurally incapable** of distinguishing two graphs with the same node count, edge count
  and ceiling however differently their edges are arranged. Only the **non-binding** arms'
  figures measure concentration. See the forward correction at §3 and, for the derivation and
  its checks,
  [`../2026-09-07-degree-floor-at-admission/README.md`](../2026-09-07-degree-floor-at-admission/README.md)
  §8. **Every figure in this document stands as measured** and §3's conclusion about the
  non-binding arm is unaffected, resting independently on max degree and edge count.
- **No blind listen, and no evidence about how anything sounds.** Every figure here is a
  property of files.

# WHAT THIS DECIDES

**Nothing.** It is measurement. Whether the union width or the degree ceiling should move is
the **owner's parked cap-rule decision** (design §9), it owes a blind listen (`REQ-38`) before
any adoption whatever these numbers say, and Track B's `C4` flag travels with any bound-100
or looser candidate.
