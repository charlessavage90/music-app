# Coherence tag probe — the kill gate fired, and what survived it

**Role: ACTIVE findings record. Owns its figures** (instrument-coverage figures only;
scoring and path-quality figures stay in `2026-07-21-scoring-adjudication.md`).
Identifier series: `COH-`. Probes and raw data:
`builder/analysis/2026-07-30-coherence-tag-probe/`; execution log:
`../2026-07-30-coherence-tag-probe-execution-log.md`.

**Scope: a one-day falsification probe, descriptive in the `CS-P0` sense.** Nothing here
fixes a criterion, adopts anything, or changes any weight, default, or document that
defines "better". It does **not** settle either open owner decision in `NEXT.md`
(fame-instrument sequencing; currency re-read policy). Every expectation, threshold and
the kill gate were committed before the runs — the argument under test and the two-step
design are in the directory README.

## §0 The headline: the gate killed step 2, exactly as §7 warned it might

*(Plain: we asked whether genre labels exist for enough of the graph to build a
"does this journey hang together" measure on them. In the obscure half of the graph —
the part the product exists to explore — two thirds of artists have no genre label
anywhere we looked. That is the same hole the fame ruler has, in the same place, so we
stopped before building anything on it.)*

The pre-committed gate: proceed to retrodiction only if union-genre coverage
(MusicBrainz genres ∪ Wikidata P136) in the **lower half** band is **≥ 50%** of all
sampled artists. Measured: **35.3%** — 14.7 points under the bar, outside the ±6-point
sampling noise band, so the kill is decisive, not fragile.

**The pre-registered retrodiction (`COH-4`, `ct_retrodict.py`) was therefore never
run.** The scoring rule it froze is committed and unexecuted; running it later against
these verdicts would be a second attempt and must be reported as one.

**What cuts against the kill, named rather than buried: `COH-3`.** The 62 interiors of
the most obscure route this artifact admits are **74.2%** genre-covered — twice the
band average. The gate was fixed on band population; the artists a successful obscurity
push would *actually deliver* are markedly better covered than the band they sit in.
That does not un-fire the gate — re-gating on delivered population after seeing this
number is precisely what pre-commitment forbids — but it is the first thing a future
pre-registration should weigh, and it is the reason this kill closes the *probe*, not
the *idea*.

## `COH-1` — Wikidata P136 genre coverage, full artifact

*(Plain: Wikidata's "genre" field covers the famous end of the graph almost completely
and barely a fifth of the obscure half.)*

Full-graph join by P434 = MBID, so no name-resolution failure class. By band, share of
**all** artists with ≥ 1 genre statement: **100 / 99.0 / 78.9 / 52.5 / 22.9%** (top
0.1% → lower half). Among artists that have a Wikidata item at all (`FPC-3`'s
denominators), genre-given-item falls **100 → 62.5%** top to bottom — the committed
prediction (high at top, falling; refuted if flat) was **confirmed**: genre statements
are editor effort, not a free property of having an item.

Route A alone was barred from passing the tail gate by construction (item coverage
there is 36.7%, `FPC-3`), and its docstring said so before the run.

## `COH-2` — MusicBrainz genre/tag coverage, banded sample, and the gate

*(Plain: MusicBrainz could in principle tag every artist we have; in practice its
volunteers have tagged the same artists Wikipedia writes about.)*

Stratified sample, min(300, band size) per band, seeded (n = 1,275; 95% CI half-width
≤ 5.7 points at p = 0.5). Every sampled MBID resolved (no deleted-MBID hits). Share
with ≥ 1:

| band | MB genre | MB tag | P136 (sample) | **union genre** |
|---|---|---|---|---|
| top 0.1% | 100% | 100% | 100% | **100%** |
| top 1% | 99.7% | 100% | 99.3% | **100%** |
| top 10% | 87.7% | 90.7% | 81.0% | **94.3%** |
| upper half | 54.3% | 58.0% | 54.3% | **69.3%** |
| lower half | 24.0% | 28.0% | 23.0% | **35.3%** |

**Gate: 35.3% vs 50% → KILL.** The committed weaker prediction — union lands above
Wikipedia's 27.4% EN-article tail figure — was **confirmed**: the two sources overlap
imperfectly enough that their union beats either alone (22.9% and 24.0% separately).
Both facts stand together: tags are *somewhat* better than articles in the tail, and
still dark on two artists in three.

## `COH-3` — coverage exactly where a successful obscurity push would deliver

*(Plain: the specific obscure artists a journey would actually surface are much better
labelled than the obscure population at large — obscure artists that are connected
enough to be routed through are also connected enough to have been tagged.)*

The `FPC-9` set: 62 distinct interiors of Track 3's `LIMIT` arm (median percentile
0.6072). Union-genre coverage **74.2%** (MB 61.3%, P136 54.8%). Committed prediction
(at or above the lower-half figure) **confirmed**, by 39 points rather than narrowly.

Bounded the same way `FPC-9` is: one arm, twelve pairs, this artifact — and the
interiors sit mostly in the *upper half* band, where coverage is 69.3% anyway. It is a
spot check, not a coverage claim for any future route.

## `COH-4` — the pre-registered retrodiction: NOT RUN

The scoring rule (min-then-mean genre Jaccard over adjacent steps, lexicographic,
strict agreement counting, the recomputed AA/OC bar) is frozen in `ct_retrodict.py`,
committed before any coverage number existed. The 11 verdicts remain an unconsumed
falsifier — nothing was scored against them, so nothing was burned. `SYN-7` would bind
any future use: the verdicts date to 2026-07-22 and encode the owner's preferences as
of then.

## `COH-5` — ListenBrainz as a batched transport for MusicBrainz tags (owner's question)

*(Plain: ListenBrainz will hand us MusicBrainz's own tag data fifty artists at a time
instead of one per second, and the answers match almost exactly — so if tags are ever
worth collecting for the whole graph, it costs under an hour, not a day.)*

All three committed predictions **confirmed**: fidelity **871/872 (99.9%)** identical
normalised genre sets where both sources answer; coverage within 0.7 points of MB
direct in every band (LB marginally *higher* — 24.3% vs 24.0% in the tail); throughput
**26.1 artists/s ≈ 29×** MB direct. Full artifact ≈ **47 minutes** via LB against
~21 hours via the MB web service. LB here is a transport for MB's data, not an
independent source — the shared-blind-spot hazard (`FPC` standing note) is about fame
signal and does not transfer to this fidelity question.

## `COH-6` — the widest vocabulary changes nothing (post-hoc, owner-requested)

*(Plain: we re-asked the coverage question counting every tag anyone ever applied,
not just proper genre labels — and the dark part of the graph stays dark, so the
problem is missing labels, not our choice of which labels count.)*

Requested by the owner after the gate fired, and labelled post-hoc: the tag columns had
already been glimpsed, so no prediction could honestly be pre-committed, and this read
cannot move the gate. Under the widest union (any MB tag ∪ any LB tag ∪ any MB genre ∪
any P136 statement): lower half **38.7%** against the genre union's 35.3% — +3.4
points, still 11 under the bar. The LIMIT interiors are unchanged at **74.2%** either
way. The kill is robust to vocabulary: artists the instrument cannot see carry no tags
of any kind in any source measured here.

## Weakest link

**The gate's population choice.** The gate measured the lower-half *band*; `COH-3`
measured a *delivered route* and got twice the coverage. If the decision-relevant
population is "artists a router would deliver" rather than "artists in the band", the
kill is too harsh — and that is exactly the argument a future pre-registration would
have to make *in advance*, with a route-population gate it commits to before looking.
What would falsify the kill as it stands: a committed route-population coverage
measurement, over realistic candidate devices rather than one ceiling arm, clearing a
pre-registered bar.

**What I would defend cheaply:** `COH-1`, `COH-2`, `COH-5` — counts over fixed
populations against two APIs, no fame claim, no router. **What I would abandon on one
contrary measurement:** any generalisation from `COH-3` beyond its 62 artists.

## What this record cannot conclude

- **Nothing about whether tags track the owner's ear.** The retrodiction never ran;
  coherence remains without any validated offline metric, in any currency.
- **Nothing that licenses a criterion, weight or currency change.**
- MB tag data moves over time; the seeded sample is deterministic but a re-run months
  from now is a new measurement. The raws needed to reproduce the scored summaries are
  committed or regenerable (directory README).
