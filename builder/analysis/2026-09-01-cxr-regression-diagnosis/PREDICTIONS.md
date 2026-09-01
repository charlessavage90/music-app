# `CXR-` — predictions, committed BEFORE the measurement

**Role: PREDICTION RECORD for the `CXR-` diagnosis.** Written and committed before any
figure was computed; the git timestamp is the evidence. Figures land in `README.md` beside
this file and are cited from there, never restated.

**Identifiers `CXR-`, collision-checked against the whole repository 2026-09-01.**

**Scope: DESCRIPTIVE PROBES over two artifacts already on disk. No arm runs, no criterion
is fixed, nothing is adopted, no routing is measured.** A pre-registration is owed before
anything here becomes a change to the shipped cost function.

---

## What happened, in one paragraph

The extended 117k-response map (`graph-cxa-adopted.bin`, 88,685 artists / 1,618,164 edges)
was adopted and deployed 2026-08-10. On **2026-09-01 the owner reported it noticeably
worse than the previous map at the thing the whole app is for — finding artists he does not
know — worse both on the first journey and, mostly, as he presses *Dig deeper*.** That is
his revert criterion from `TEST-QUEUE.md`, in his own words. **He instructed the revert; it
was executed and verified live the same day.** This diagnosis asks *why*, against the two
artifact files, with production already back on the old map.

## What the pre-adoption run already said

Cited from `builder/analysis/2026-08-09-jfx-prereg-critique/README.md`, not restated:
the acceptance gate `JFX-G1b` was a **"the map is broken" stop-gate, deliberately lenient**
— it permitted up to ~30 presses of *Dig deeper* to reach where the old map got in 20, and
the new map realised ~24. **Passing it was never a claim that the map was no worse.** The
one signal pointing the other way (the d20 fame drift concentrated in famous-to-famous
pairs) was explicitly post-hoc.

**So the owner's report is consistent with the measurements rather than contradicting
them.** What is missing is the mechanism, which no `JFX-` figure identifies.

## The predictions

Each states what I expect, the threshold that decides it, and — the part that matters —
**what a result would rule OUT**, so a null here is as informative as a hit.

### `CXR-P1` — the fame ruler is diluted by the new population. **I expect this REFUTED.**

The only device still steering the journey away from familiar artists after about five
presses is the fame ramp (`w_known_ramp_fame_pctl`), which prices each artist by their
**percentile within the artifact's own measured listener counts**
(`graph_store.fame_percentiles`). That frame is rebuilt per artifact by design. Adding
~30,000 artists could therefore move every pre-existing artist's price.

**Prediction: it does not, because most of the newly added artists have no measured
listener count at all.** Nulls are excluded from the frame (and take 0.0 themselves), so
they cannot move it.

- **Decides it:** if **≥ 70 %** of the newly added artists are null on `fame_lb`, `CXR-P1`
  is refuted as a mechanism and I stop pursuing it.
- **If it is instead confirmed** (a large measured share sitting low in the distribution,
  and `CXR-M3` showing pre-existing artists' percentiles moved by a median > 0.02), the
  ramp is mispriced by the population change and that is the mechanism.

### `CXR-P2` — the new artists are cul-de-sacs. **This is my leading hypothesis.**

Average edges per artist fell from **22.4 to 18.2** (−18 %) across the adoption — the map
grew 51 % in artists but only 23 % in connections. Mutual k-NN keeps an edge only where
each artist ranks the other in its top k, and a thinly-crawled newcomer has few responses
to rank anyone in.

**Prediction: the newly added artists have markedly lower degree than the pre-existing
ones — median new degree below half the median pre-existing degree.** If so they are
*present but expensive*: reaching one costs similarity the router can avoid by staying in
the dense, older, more famous core. The map would then be bigger and less traversable at
once, which is exactly the shape of "more artists in it, fewer of them shown to me."

- **Decides it:** median degree of the ~29,850 new artists **< 50 %** of the median degree
  of the 58,838 pre-existing ones, measured in the same artifact.
- **What would rule it out:** comparable medians. Then thinness is not the story and the
  cost has to be in how the terms are priced, not in the graph's shape.

### `CXR-P3` — the popularity currency was re-censused under the router's feet.

Popularity here is score-weighted in-degree over the archive, log-scaled — so **it is not
a property of an artist, it is a property of an artist within a population**. The obscurity
floor is anchored on `min(pop_raw[source], pop_raw[target])`, both endpoints' own values.
If every pre-existing artist's `pop_raw` moved, the floor moved with it, and it moved on
the **first journey**, before any press.

**Prediction: pre-existing artists' `pop_raw` shifted measurably** (paired median |Δ| >
0.01 on the 0–1 scale). This is the only candidate here that could touch the pre-press
journey, which is the half of the owner's report that `JFX-C1` did **not** corroborate
(median change 0.0000 at depth 0).

- **Decides it:** the paired median shift, plus whether the shift is one-directional.
- **⚠ It being real does not make it the cause.** `JFX-` measured no depth-0 change across
  297 pairs. If `CXR-P3` is confirmed *and* depth-0 journeys did not move, both are true and
  the honest read is that the currency moved without changing what the router picked.

## What this diagnosis cannot answer

**No figure here says which artists a journey actually delivers.** All three probes are
properties of the two files. Establishing that the new map routes *to* its new artists less
often needs the `JFX-` routing harness (~2.6 hours), and establishing that a change fixes it
needs its own pre-registration and the owner's ear. **Neither is started here, and resuming
path-quality work is the owner's trigger, never a session's.**
