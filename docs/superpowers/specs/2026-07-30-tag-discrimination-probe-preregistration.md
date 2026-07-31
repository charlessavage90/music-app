# Tag discrimination probe — pre-registration

**Role: ACTIVE pre-registration.** Identifier series: `TAS-` (checked free across the repo
before allocation — note `D1`–`D7` were rejected because the `closeout` skill owns that
series in the always-loaded context layer). Committed **before any measurement runs**; the
git timestamp is the evidence that every bar below predates every number it judges.

**Scope: a descriptive probe.** It adopts nothing, fixes no criterion, changes no weight,
default, currency, or document that defines "better", and requires no rebuild and no API
change. It does **not** settle either open owner decision in `NEXT.md`. It does **not**
constitute the router-side pricing track's pre-registration — that track still owes its own,
consuming `TB-P5H-7`, before anything router-side is adopted.

**Owner decisions already taken, recorded here so they are not re-litigated:** the goal is
**coherence**, not obscurity; the ear is not spent at this stage; the architecture question
(build-time selection vs router-side pricing) is **deliberately left open** for this probe to
inform; and the fresh pair draw including obscure endpoints is his trigger, pulled
2026-07-30.

---

## §0 The question, and why it precedes the architecture choice

Both candidate architectures — a tag-aware **selection** rule at build time, and a tag-aware
**pricing** term in the router — rest on one unexamined assumption: that genre-label
agreement *discriminates* between the candidates an artist actually has. If artists who are
similar already share genres, the signal carries nothing the graph does not already encode,
and both designs are dead without a rebuild, an API change, or a listening test.

This probe tests that assumption alone. It is the cheapest thing that could kill the idea.

**It is also the licensed form of a move the `COH-` handoff barred.** `COH-3` observed that
delivered obscure artists are far better labelled than the obscure population at large, but
it was seen *after* the kill gate fired, so re-gating on it was forbidden; the stated
legitimate route was "a new pre-registration designed cold, with a route-population gate
committed before looking." `TAS-1` is that gate, and it is committed here, unseen.

### The one dormant term

**The neutral value for unlabelled pairs is inert in the baseline and active in every arm.**
At λ = 0 (and at coherence weight 0) the rule multiplies by exactly 1 regardless of what the
neutral rule says, so the baseline cannot reveal a bad choice of neutral value; every arm
can. This is the same shape as `w_floor` in the Track 2 pre-registration's §0 — a term that
switches itself on only in the arms.

It cannot be designed away (the rule must say *something* about missing labels), so it is
**fixed in §1 before any run and never adjusted after seeing a result**. Every finding is
reported as "λ **and** the neutral rule", never as a clean single knob.

### Held constant, and why each is genuinely constant under this intervention

| Held | Why it cannot move here |
|---|---|
| The graph artifact | **No rebuild happens in this probe.** Every measurement runs against the adopted artifact (sha asserted on load, per the `COH-`/`FPC-` import precedent). |
| Popularity / fame currency | Score-weighted in-degree is accumulated over the **uncapped** adjacency (`pipeline.py:253`), before any selection runs — and nothing is rebuilt regardless. The `_log_scaled` renormalisation hazard (`graph.py:148`, retained population sets the 0–1 span) **does not arise here** and returns only if a variant is ever built. |
| Crawl archive | Read-only. Wrapped per `GRT-A1`'s deferral before any harness points at it. |
| Source algorithm, `limit`, `k`, `cap_strategy`, rescale, damping | Untouched. `BuilderConfig` defaults are not moved by this probe. |
| Router weights | Production `ApiConfig()` defaults throughout `TAS-5`, single set, stated in every output. The only addition is the coherence term under test. |
| `w_degree_hub` | **A dormant term, and it stays dormant.** It is `0.0` in production (`api/…/config.py:54`), so the hub penalty never fires today. It is inert here for a reason this intervention does not remove: it is dormant because of the *current graph's* top-degree set, and this probe rebuilds nothing and changes no edge, so that set is untouched. Named rather than assumed, because Track B's own held-constant table flags it as the term a cap change *would* wake — and no arm here is a cap change. |
| Genre normalisation | The **frozen** normalisation from `ct_common.py`, imported not reimplemented, so this record and `COH-` speak one vocabulary. |
| Noise floor | **None — builds and routes are deterministic.** Every bar below is a *materiality* bar, not a significance bar. |

---

## §1 The device

**Agreement** between two artists is the Jaccard overlap of their normalised genre-label
sets: shared labels divided by total distinct labels. 0 = nothing in common, 1 = identical.

**The label set is fixed here as the `COH-2` union genre**: ListenBrainz's genre-whitelisted
tags (a faithful transport for MusicBrainz genres — `COH-5` measured 99.9% identical sets)
**∪** Wikidata P136, both through `ct_common.norm_genre`. This is the same vocabulary the
`COH-` coverage figures were measured in, so `TAS-1` is comparable with them rather than
merely adjacent. **The widest-vocabulary variant is not used**: `COH-6` measured it as
near-identical in the tail, so it would add a second vocabulary for no gain. Pinned before any
run; a change after a result is an §8 amendment.

**Selection form (build time).** The value used to decide which neighbours an artist keeps:

```
rank(u, v) = strength(u, v) × (1 + λ · agreement(u, v))
```

**Routing form (query time).** One additional term in the per-edge cost:

```
… + w_coh · (1 − agreement(u, v))
```

expressed as a multiple of production's `w_sim`, since both price the quality of a single
hop. Grid: `w_coh ∈ {0, ¼, ½, 1, 2} × w_sim`. Selection grid: `λ ∈ {0, 0.25, 0.5, 1.0, 2.0}`.

**Dependency, stated rather than assumed: `w_coh` does not exist.** `ApiConfig` carries no
such field, and this document does not propose adding one. It is a **harness-local** term
applied in simulation over the existing pathfinder. Shipping it would be a config default
change, which is an adoption, which this probe explicitly does not license.

**Three properties, each load-bearing:**

1. **λ = 0 and `w_coh` = 0 reproduce production exactly** — not approximately. The multiplier
   is exactly 1 and the added term is exactly 0. Every arm's isolating baseline differs by
   exactly one column.
2. **Emitted similarity scores are never touched** in the selection form. Only the *choice*
   of surviving neighbour changes. This is enforced by the existing `ranking` parameter of
   `mutual_knn_cap` (`graph.py:67`), which was built for the tie-break fix and already
   separates "what orders the candidates" from "what gets written".
3. **THE NEUTRAL RULE, fixed now:** where either artist carries no labels, `agreement` takes
   the **median agreement across that same artist's own labelled candidates** (global median
   where fewer than two labelled candidates exist). **Never zero.** Zero is a positive claim
   of dissimilarity; applying it to missing data would demote unlabelled candidates, and
   unlabelled candidates are disproportionately the obscure ones — which would push `DD-F1`
   the wrong way. Per-artist rather than a global constant because agreement levels vary by
   artist: a metal act's candidates nearly all share "metal" and score high, an eclectic
   act's share little and score low, so a single constant would reward unlabelled candidates
   for one and punish them for the other.

**The cap binds at 50 and only at 50.** At k = 100 the ranking is provably never consulted:
the source returns at most 100 candidates (`CS-P0e`), so top-100 of a ≤100 list is the whole
list and nothing is cut. Track B measured this without setting out to — `PS100` ≡ `MK100`,
byte-identical on both archives (`LBS-3`), two different ranking rules producing one graph.
**No arm in this document runs at bound 100**, and any future proposal to loosen the bound
must address the *mutual* requirement, not the ranking.

---

## §2 Criteria

Every criterion carries its plain sentence, fixed here, before any result exists. Owner-facing
text quotes identifier **and** sentence.

### `TAS-1` — where do we have labels at both ends? *(gate, narrow)*

*Plain: on how many of the connections in today's map do both artists carry genre labels?
Where either is bare, the rule is silent and changes nothing there.*

Reported **stratified**: famous–famous, famous–obscure, obscure–obscure, over bands from the
adopted fame frame.

**Gate — narrow, and expected to pass:** ≥ 80% of famous–famous edges labelled at both ends.
**It is not a coverage kill gate, and the `COH-2` bar is deliberately not inherited.** That
bar governed a *sensor* — an instrument scoring every path, where blindness in the tail
returns confident wrong readings about artists it cannot see. This is an *actuator*: where
labels are missing it does not act, rather than acting wrongly. **Silence is safe in a way
blindness is not.** This gate's job is to catch our assumption about *where* the rule acts
being wrong, not to kill the idea. The real hazard hidden in sparse tail coverage — silence
in the tail plus action at the top tilting the app toward the famous — is `TAS-6`'s, which is
where it can actually be caught.

### `TAS-2` — does genre overlap vary between an artist's candidates? *(gate)*

*Plain: R.E.M. has a hundred similar artists. Do some share far more genre labels with R.E.M.
than others, or do they all look about the same?*

Measured over artists carrying at least two labelled candidates; the excluded share is
reported.

**Kill only at effectively zero spread: median interquartile range < 0.02.** A signal that is
genuinely flat across a candidate list cannot prefer one candidate over another at any λ or
any weight, and both architectures die together.

**A spread below 0.10 is reported as a weak-signal flag, not a kill** — and this is a
deliberate correction to an earlier draft of this document, which put the kill at 0.10.
That threshold could not be justified: at λ = 2 an agreement spread of 0.10 still moves the
multiplier by ~20%, which is ample to reorder candidates whose strengths differ by less than
that. **`TAS-4` measures reordering directly and exactly, so it decides**; `TAS-2`'s job is
to catch the one case where no reordering is even arithmetically possible, and to flag a weak
signal that would raise the prior on a `TAS-4` null. Setting a bar here that `TAS-4` would
then contradict is precisely the failure this project's gate rule warns about.

### `TAS-3` — is it telling us anything similarity has not? *(diagnostic — NOT a gate)*

*Plain: if genre overlap just repeats what the similarity score already says, then nudging by
it changes nothing — the graph already knows.*

Rank correlation between `agreement(u,v)` and `strength(u,v)` across edges, plus the share of
candidate lists on which the two orderings are identical.

**Deliberately carries no threshold.** `TAS-4` and `TAS-5` measure reordering directly and
decide; `TAS-3` exists to make a null *interpretable*. The failure mode it names is the most
likely one and is invisible to `TAS-2`: **if agreement rises with strength, then
`strength × (1 + λ · agreement)` returns exactly the order strength alone gave** — because
multiplying by something that increases with strength cannot reorder it. Agreement could
range widely, pass `TAS-2`, and λ still be inert at every value. A null from `TAS-4`/`TAS-5`
means three very different things — no variation, variation redundant with similarity, or a
real independent signal the cap and router absorb — and they point at different next moves.

### `TAS-4` — would it change which neighbours survive selection? *(gate)*

> ### ⚠ THIS SECTION IS AMENDED BY [`TAS-AM1`](#tas-am1--tas-4-changes-its-measured-quantity-its-statistic-and-its-bar) — READ IT BEFORE ACTING ON ANYTHING BELOW.
>
> Its **measured quantity, its summary statistic and its bar all changed**, and the plain
> sentence immediately below was **withdrawn as false**. The text is left standing rather
> than rewritten because a pre-registration whose errors are edited away cannot be checked;
> git records what was committed, and this marker records that it no longer governs.
>
> **Current:** edge turnover, deletions and creations reported separately, mean not median,
> **kill at ≤ 1%**.

~~*Plain: swapping two neighbours out of fifty will not change a journey you would notice.*~~
**← WITHDRAWN AS FALSE by `TAS-AM1`.** `TD-2` measured that swap rate as ~8.4% of all
connections differing and `TD-4` as roughly one journey in three containing a deleted
connection. The replacement sentence is in `TAS-AM1`.

Simulated over the archive, no rebuild: the top-50 set under λ = 0 versus each λ > 0, for
artists whose own candidate list exceeds 50 (the only artists for whom selection has a
choice to make; the share of such artists and of edges incident on them is reported).

~~**Kill for the build-time architecture: if at every λ the median artist swaps ≤ 2 of 50.**~~
**← WITHDRAWN by `TAS-AM1`; superseded by turnover ≤ 1% at every λ.**

**Bounded, and stated now:** this measures the *input* to a rebuild, not its output. Mutual
selection means one artist's reordering can delete an edge the other still ranks, so the
built consequence of a given swap rate is not derivable from `TAS-4` alone.

### `TAS-5` — would it change the journeys the app builds? *(gate, per class)*

*Plain: if the journeys come back the same, the term is decoration.*

Today's graph, production weights, plus the coherence term at each `w_coh`, over the §3 pair
set. Reported **per pair class**, with change rates for every class regardless of outcome.

**"Unchanged" means the identical artist sequence, in order, endpoints included.** A path of
the same length through different artists is a change; so is the same artist set in a
different order. Path *cost* is not part of the comparison — it necessarily moves whenever
`w_coh` > 0, since the term is added to every edge, and reading a cost difference as an effect
would be an artefact of the instrument rather than a finding.

**Kill for the router-side architecture: only if journeys are unchanged in EVERY class at
every weight.** A pooled bar is explicitly rejected: a small overall change concentrated
entirely in famous-to-famous journeys is a signal worth chasing, not noise to average away —
and famous-to-famous is both where `DD-F1` lives and where the effect is expected to land.

**Standing caution, from this project's own record:** three consecutive attempts to change
router behaviour by changing prices returned nulls — Track 2's repricing family, Track 3b's
thresholded toll, and Track B's `R2` (quota edges present and declined at production
weights). A `TAS-5` null is therefore **weak evidence about tags specifically** and must not
be reported as "tags do not work"; it is consistent with "this router shrugs off new terms",
which `TAS-3` and `TAS-4` are what distinguish it from.

### `TAS-6` — does any of this cost obscurity? *(guard — reported, never a success signal)*

*Plain: does this make the app worse at reaching unknown artists — the thing you called a
defect rather than a limitation?*

Two measurements, one per architecture. For the `TAS-4` arms: the count of famous→obscure
pairs surviving in the **simulated** top-50 sets (nothing is built, so "retained" means
selected by the simulation, not present in an artifact). For the `TAS-5` arms: sub-decile
presence on delivered journeys. Both against the adopted fame frame as a **fixed reference
population** — never each arm's own, which is the currency error `§0`'s held-constant table
guards.

**Adverse at a ≥ 10% reduction.** An adverse `TAS-6` bars any recommendation to adopt,
whatever `TAS-4`/`TAS-5` show, until a router-side answer exists. This is the guard on the
neutral rule of §1: unlabelled artists are disproportionately obscure, so a careless
treatment of missing labels punishes exactly the artists the product exists to surface.

---

## §3 The pair set

**Fresh draw, this probe's own, seed `20260730-tas`.** Classes carried end to end as labels —
`ff` (both endpoints top 1%), `fo` (one famous, one lower half), `oo` (both lower half) —
because `CRS-A1` records that pooling pairs and discarding their class made three
pre-registered quantities uncomputable in Track B until it was fixed mid-flight.

**Obscure-endpoint classes are included by the owner's explicit trigger, 2026-07-30.**
`NEXT.md` parks the `× lower` redraw as his call and this pulls it, for this probe only;
Track B's committed draw is untouched and its classes stay the record for its own reads.

**No attrition guard is needed and none is applied.** Track B restricted its draw to pairs
routable in every compared cell because its cells were *different graphs*. Nothing here is
rebuilt: `TAS-4` compares sets without routing, and `TAS-5` routes on one graph under
different weights. Since only the largest connected component is retained, a path exists
between any two artists the draw can offer, so no cell can lose a pair. Minimum readable
pairs per class is fixed at draw time and any class falling below it is reported unreadable
rather than pooled.

---

## §4 Instrument checks — both directions, before any arm is scored

**Green:** the harness must reproduce production exactly at λ = 0 and `w_coh` = 0 — the same
fifty neighbours per artist, and identical paths for every pair. A mismatch means the harness
is wrong and nothing it produces counts.

> ### ⚠ THE RED CHECK BELOW IS AMENDED BY [`TAS-AM3`](#tas-am3--the-red-check-cannot-fire-as-written-and-is-replaced-by-two) — READ IT BEFORE ACTING ON IT.
>
> It is **withdrawn as unachievable**, not merely mis-tuned: for an *overlap*-based device,
> randomising labels destroys overlap rather than randomising it, so no randomised frame can
> produce large change. Text left standing per the `TAS-AM1` precedent.

~~**Red:** the same harness, fed a randomised tag frame, must report large swap rates and large
path-change rates.~~ **← WITHDRAWN AS UNACHIEVABLE by `TAS-AM3`.** A measurement that has only
ever come back green is not evidence yet — the standing rule in project memory, and the reason
this is written down before the run rather than offered afterwards as reassurance. **That
principle is unchanged and `TAS-AM3` serves it; only the mechanism is replaced.**

Both checks are run and their outputs recorded whatever the arms show.

---

## §5 Reads — every result, including the null, and the run state each presupposes

**Two classes of read, and the distinction is load-bearing.** A **gate read** fires the moment
its own gate is measured and licenses stopping — `TAS-2`'s kill and `TAS-1`'s failure are the
only two. **Every other read below presupposes the full grid has run**, both instrument checks
have passed, and `TAS-1` through `TAS-6` are all in hand. No outcome read is licensed on a
partial grid; if the probe stops early, what is still owed is named explicitly in the findings
rather than inferred, and any arm left unrun is listed by name so a later session cannot
mistake "not run" for "returned nothing".

- **`TAS-1` fails** (famous-end connections not labelled at both ends) → **not a kill.** Our
  assumption about where the rule acts is wrong, which is what this gate exists to catch. Stop
  the outcome arms, report the stratified coverage, and re-open the design: the device in §1
  is aimed at a population that does not exist as described.
- **`TAS-2` kills** → the idea is dead in both architectures. Report the kill, stop, and do
  not proceed to `TAS-4`/`TAS-5`. The tag frame is retained; it cost 47 minutes and is reusable.
- **`TAS-4` kills, `TAS-5` survives** → the build-time route is dead; the router-side route is
  live and the next step is the router-side pricing track's own pre-registration, consuming
  `TB-P5H-7`.
- **`TAS-5` kills, `TAS-4` survives** → the router-side route is dead *for this device*, read
  against the three-null caution in `TAS-5`; the build-time route is live and the next step is
  a rebuild pre-registration with a factor table and a blind listen (`REQ-38`).
- **Both survive** → the architecture choice becomes a real decision with numbers on both
  sides, and it is the owner's. Neither is adopted on this document's evidence.
- **Both kill** → `TAS-3` says which null this is, and the coherence thread's *instrument*
  line is closed a second time. The **structural** half of §7 (coherence is not additive
  along edges) is untouched by any outcome here and stays parked.
- **`TAS-6` adverse, anything else positive** → no adoption recommendation, whatever else
  holds. Reported in the summary, not in a footnote.

---

## §6 What this probe cannot conclude

- **Nothing about whether genre tags track the owner's ear.** Discrimination is not validity.
  The `COH-4` retrodiction stays unrun and the 11 blind verdicts stay unconsumed; `SYN-7`
  binds any future use of them.
- **Nothing that licenses adopting anything** — no weight, default, criterion, or currency.
- **Nothing about bound 100's hub cost.** That is Track B's `CRS-C4`, and no arm here runs at
  bound 100.
- **Nothing about what a rebuilt graph would route like.** `TAS-4` measures selection inputs
  only (see its bound).
- Tag data moves over time. The frame is collected once, and a re-run months later is a new
  measurement rather than a reproduction.

---

## §7 Out of scope, parked, and explicitly NOT ruled out

**Replacing mutual k-NN with a tag-based degree limiter** — owner-raised 2026-07-30, during
the design of this probe, and parked by his instruction as a separate experiment.

The argument: mutual k-NN may not suit ListenBrainz's data, since reciprocity is partly an
artefact of how that similarity is produced; genre tags could bound degree on a different
principle. **The record corroborates the premise** — Track B's `R1a` isolated reciprocity at
k = 100 and returned **null on both archives**, so the reciprocity requirement is doing very
little for its cost on the criteria measured.

It is **ruled separate, never ruled out.** Replacing mutual k-NN is a structural change of a
different order from reordering within it, and mixing the two would make every attribution in
this document ambiguous. It needs its own pre-registration, designed cold.

**Also out of scope:** the coherence thread's structural half (a sum of per-edge costs cannot
express "the whole path reads as one journey"); bound-100 adoption; and any blind listen.

---

## §8 Amendments — append-only

*(Entries appended after commit, never edited in place; nothing above is renumbered. The
amendment series is `TAS-AM`, deliberately **not** `TAS-A`, so an amendment ID can never be
misread as a criterion ID — the collision that cost Track 2 eleven ambiguous identifiers.)*

### `TAS-AM1` — `TAS-4` changes its measured quantity, its statistic, and its bar

**Appended 2026-07-30, before any `TAS-` criterion was measured.** No tag frame existed and
no `TAS-1`…`TAS-6` number had been produced when this was written. What did exist were four
instrument derivations (`TD-1`…`TD-4`,
`builder/analysis/2026-07-30-tag-discrimination/`), commissioned specifically to check
whether `TAS-4`'s bar meant what it claimed. It did not.

**Three findings, each of which independently breaks the original `TAS-4`:**

1. **`TD-2` — per-artist swaps are not the quantity the gate is about.** Mutual selection was
   suspected of *amplifying* deletions; measured, it is near-neutral (deletions ≈ 1.07× the
   per-artist swap rate). But every swap also *promotes* a neighbour, and promoted neighbours
   become surviving connections at nearly the same rate. Per-artist swap counting sees only
   the drop. The conversion is linear over the observable range and stable across placement
   and endpoint-correlation regimes and across two archives: **turnover ≈ 2.11 × the
   per-artist swap rate.** The original bar of "median ≤ 2 swaps of 50" therefore admitted
   **~8.4% of all connections differing** as a kill.
2. **`TD-3` — the median cannot see the shape this design predicts.** The device is inert
   wherever labels are missing, and `TAS-1` exists because coverage is expected to be uneven.
   Measured: a reranking touching 30% of artists changes 6.3% of the map and reports
   **median = 0** — an unambiguous kill. Zero-inflation is the expected case, not a corner.
3. **`TD-4` — the defence for a permissive bar is refuted, with the sign reversed.** The
   hypothesis (offered by the analyst, then tested by it) was that journeys ride strong
   top-of-list connections and would be insulated from a boundary reranking. Routed
   connections instead sit *deeper* in both endpoints' lists than average (median rank
   position 28 vs 26; 30 for famous-famous), so they are deleted at **1.09–1.26× the
   population rate in all 25 arms, never below 1.0.** Famous-famous is the most exposed class
   per connection (≈1.29×) and the least exposed per journey, because those journeys are
   about half as long — different questions, and a pooled figure hides both.

**What `TAS-4` now measures.** The **symmetric-difference edge turnover of the simulated
mutual k-NN edge set against the λ = 0 baseline, with deletions and creations reported
separately**, not per-artist top-50 swaps. Both are also reported per pair class.

**Statistic.** The median is retired for this criterion. Turnover is a population quantity;
where a per-artist figure is still reported it is the **mean**, which `TD-3` measured as
exactly proportional to turnover.

**New kill bar: turnover ≤ 1% at every λ.** *(≈ 4,500 of ~449,000 connections; ≈ 0.24 swaps
per artist.)* **The owner set this figure on 2026-07-30**, after being shown the conversion
in journey terms — it is a materiality line, which is his, not a derivation. The reasoning
he was given and accepted: a kill gate should fire only when the intervention is provably
inert, and one connection in twelve is not that.

**New plain sentence, replacing the one `TD-2`/`TD-4` contradicted.** The old sentence —
*"swapping two neighbours out of fifty will not change a journey you would notice"* — is
**withdrawn as false**, and is recorded here rather than deleted because a pre-registration's
value is that its errors stay visible. The replacement:

> *Plain: if fewer than one connection in a hundred is different across the whole map, no
> journey will change in a way you could notice. At the original bar, about one journey in
> three would have contained a connection that no longer exists.*

**Substrate, stated because it is an uncontrolled difference between two criteria.** The
adopted artifact predates the nameless-artist drop and cannot be reproduced from the pipeline
capture (36 artists / 193 edges, 0.05% / 0.04%). `TAS-4`'s simulation therefore runs on the
Track B `ALG-E-mutual_knn-k50` cell (sha `73feffa0…a69faa`) while `TAS-5` routes on the
adopted artifact. **Both `TAS-4` arms and its λ = 0 baseline sit on the same substrate**, so
no arm-to-baseline comparison spans graphs; the difference is between criteria, not within
one, and no read may compare a `TAS-4` figure with a `TAS-5` figure without saying so.

**What `TAS-4` does NOT gain from this amendment.** It still measures the input to a rebuild
rather than its output, and `TD-4`'s journey-level figure is a **ceiling on disruption, not
disruption**: a deleted connection may be routed around near-identically, and nothing offline
here can say whether the replacement *reads* differently. That remains the blind listen's.

**Consequential edits, all within this amendment and none above it.** §5's read
"`TAS-4` kills, `TAS-5` survives" now fires on turnover rather than swaps and carries the new
plain sentence. §4's green check is unaffected and if anything strengthened — turnover is
derived from the same per-artist top-50 sets it validates. `TAS-6`'s `TAS-4`-side measurement
is unit-independent and unchanged.

### `TAS-AM2` — the substrate rule, stated for every criterion rather than two

**Appended 2026-07-30, still before any `TAS-` criterion was measured.** `TAS-AM1` named the
substrate for `TAS-4` and `TAS-5` and left the others implicit. Writing `TAS-2` revealed that
the implicit answer was ambiguous, and the ambiguity is not cosmetic: **`TAS-2` asks about an
artist's *candidates* — its own pre-cap similar-artist list of up to 100 — and the built
artifact holds only the ≤ 50 that survived selection.** Measuring spread among survivors
would answer a different question from the one §2 asks, on an already-similarity-selected
population, and would bias toward a kill.

**The rule, and it is one line: selection-side criteria run on the pre-cap capture;
map-side criteria run on the adopted artifact.**

| criterion | substrate | why |
|---|---|---|
| `TAS-1` | adopted artifact | It asks about *connections the map has*. Those exist only post-selection. |
| `TAS-2`, `TAS-3` | pre-cap capture (`ALG-E`) | They ask about the *candidates selection chooses among*, which the artifact has already discarded. |
| `TAS-4` | pre-cap capture (`ALG-E`) | Per `TAS-AM1`; unchanged. |
| `TAS-5` | adopted artifact | It asks what the *app* routes today. |
| `TAS-6` | both, each on its own side's substrate | Its two halves measure the two architectures separately and are never combined. |

**The standing constraint from `TAS-AM1` widens accordingly: no read may compare a figure
from the capture side against one from the artifact side.** They differ by 36 artists and
193 edges (0.05% / 0.04%) — small, but a difference nobody controlled. Within either side,
every arm-to-baseline comparison remains clean, which is what the criteria actually need.

**Capture provenance.** `td_capture.py` regenerates it in ~2 minutes from the archive through
`ReadOnlyArchive`; the `.npz` lives in scratch and is deliberately not committed (~20 MB,
byte-deterministic from committed code). `td_turnover.py --verify` asserts the reconstruction
reproduces `ALG-E-mutual_knn-k50.bin` edge-for-edge, so a lost or stale capture cannot pass
silently.

### `TAS-AM3` — the red check cannot fire as written, and is replaced by two

**⚠ APPENDED AFTER RESULTS EXIST, unlike `TAS-AM1` and `TAS-AM2`.** Both of those were
written before any `TAS-` criterion had a number. This one is not, and the disclosure matters
more than the amendment:

**What existed when this was written:** `TAS-1`, `TAS-2`, `TAS-3` (Task 3), `TAS-4`'s full λ
grid (Task 4), `TAS-6`'s selection half (**adverse**), and the original red check's output
(**did not fire**). **So this amendment is not blind, and a reader must assume it could have
been fitted to those results.** The specific hazard: a null control can be chosen to produce a
small number, which would flatter `TAS-4`. Two things bound that hazard, and neither removes
it — **the naive shuffle's figure already existed and is committed** (`tas_guard.json`, commit
`bc57732`), so the direction was known and is on the record before this text; and every read
below is fixed here, before the replacement runs.

#### Why the original is unachievable rather than mis-tuned

The device is **Jaccard overlap**. Shuffling genre labels between artists does not give artists
*random* genres in common — it gives them **none** in common, because real genre sets are
specific and long-tailed. Measured on a 4,000-node sample (execution log §10.2): agreement is
exactly zero on 92.3% of label-carrying pairs under a shuffled frame against 36.5% under the
real one, mean 0.018 against 0.175, 90th percentile 0.000 against 0.500. A near-constant
multiplier cannot reorder anything.

**This generalises: every correct null control must report a small number here**, because
turnover is driven by overlap and randomisation is what destroys overlap. §4 asked for
something that cannot exist for this class of device. It was conflating two different jobs.

#### `TAS-AM3a` — the liveness-and-equivalence check *(replaces the red check's stated job)*

*Plain: prove the measuring device can register a big change, by giving it a big change we
already know the answer to.*

Feed the **synthetic symmetric field** from `td_turnover.uniform_field` through `tas_select`'s
ranking path.

**Passes only if both hold: (i)** the resulting selection mask is **bit-identical** to
`td_turnover.mask_multiplicative`'s at the same λ and seed, and **(ii)** the turnover
reproduces the committed `TD-2` `MULT-SYM` figures to five decimal places. **Any mismatch
voids every `TAS-4` figure.**

This is stronger than the original intent: it proves the new code path *is* the already-verified
one rather than merely resembling it, and `TD-2`'s committed field is known to produce large
turnover, so a large response is demonstrated against a fixed external reference rather than
against a judgement call. It is deterministic and therefore a unit test, not an experiment.

#### `TAS-AM3b` — the null control *(new, and NOT a gate)*

*Plain: check that the change we measured comes from genres sitting where they actually sit,
rather than from any label-shaped nudge at all.*

Permute label sets **among labelled artists only** — holding fixed exactly *which* artists
carry labels, and therefore the count of pairs where the rule acts. One knob: which labels an
artist holds. (The naive shuffle moved sets among **all** artists and so also halved the
both-ends-labelled pair count, a second knob; that is why it is replaced rather than reused.)

**Reads, fixed here before it runs:**

- **A small null turnover is the CORRECT result and is not a failure.** Stating this in advance
  because the original check's framing makes a small number look like a fault.
- **If the null reaches ≥ 50% of the real turnover at any λ**, then `TAS-4`'s turnover cannot
  be attributed to genre structure, and every `TAS-4` figure must be reported carrying that
  caveat.
- **If the null stays below 50%**, report the ratio and nothing more. **No claim about tags is
  licensed by this control** — it is an instrument reading, and reading it as evidence about
  genres would need its own pre-registration designed cold. This clause exists because the
  control is genuinely informative, which is exactly what makes over-reading it tempting.

#### Scope of this amendment

**`TAS-AM3a`/`b` replace the red check for BOTH architectures.** The routing side inherits the
identical flaw — shuffled labels cannot change paths either, for the same reason — so Task 7's
routing-side red check is replaced by the same pair, with `find_path_coh` in place of the
ranking path and the `w_coh` grid in place of λ.

**Nothing else moves.** No criterion, bar, weight, default, currency or substrate changes.
`TAS-6`'s adverse selection-side verdict is untouched and still bars an adoption recommendation
per §5. `TAS-4`'s figures are unchanged; what changes is whether they are believable.

### `TAS-AM4` — evaluating the `REL-` enriched frame as a CANDIDATE for §1's vocabulary

**⚠ APPENDED AFTER RESULTS EXIST**, like `TAS-AM3` and unlike `TAS-AM1`/`TAS-AM2`. What
existed when this was written: all of `TAS-1`…`TAS-4`, `TAS-6`'s selection half (**adverse**),
`TAS-AM3a`/`b`, and the complete `REL-` record including its headline coverage figures and
`REL-3`'s fidelity median. **Assume it could have been fitted to those.** Every read below is
fixed before the evaluation runs, and — deliberately — **`TAS-2`'s bars are reused unchanged
rather than new ones being invented**, which is the main thing keeping this honest.

#### What this amendment does and does not do

**It does NOT change §1's vocabulary.** §1 stays pinned to the `COH-2` union genre, and every
committed `TAS-` figure stands on it. This amendment authorises **measuring a candidate frame
beside the committed one** and fixes how that comparison is read. Adopting the candidate would
be a further amendment and, per `NEXT.md`, the owner's trigger.

#### Why it is worth measuring at all, and why the answer is not obvious

`TAS-6` went adverse because unlabelled candidates — disproportionately obscure — are squeezed
out at the cap boundary. `REL-` more than doubles lower-half coverage, which attacks that cause
directly. **But `REL-3` measured the recovered labels at a modest median overlap with truth:
they land in the right region rather than recovering an artist's genres.**

**That matters more here than it does for a coverage instrument, and the reason is specific.**
`TAS-`'s agreement is *itself* a Jaccard, computed **between two artists**. If both sides are
derived, the errors compound, and the direction of the bias is unknown in advance: if derived
labels drift toward broad common genres, unrelated artists start to look alike and the signal
**flattens**; if the errors are independent, agreement is **attenuated** toward zero. Both
degrade discrimination, which is this probe's entire premise. **So a frame can raise coverage
and destroy the signal at the same time**, and that is exactly what this evaluation checks
before anything expensive is run.

#### The candidate frames

- **`W0`** — the committed §1 frame. The isolating baseline.
- **`W1`** — `W0` ∪ `REL-`'s `F1` (MusicBrainz release-group genres, strict attributability).
- **`W6`** — `W1` ∪ Discogs genre ∪ Discogs style, i.e. `REL-`'s full `F6` added to `W0`.

One knob between `W0` and `W1` (a source), one between `W1` and `W6` (a second source).
Substrate is the **pre-cap capture**, per `TAS-AM2`, because `TAS-2`/`TAS-3` are selection-side.

#### Reads, fixed here before it runs

1. **`TAS-2`'s existing bars apply unchanged to every candidate frame.** A candidate whose
   median within-list IQR falls below the **0.02** kill is **dead for `TAS-`** and no coverage
   figure rescues it. Below the **0.10** weak-signal flag it carries that flag, exactly as the
   committed frame would have.
2. **A material fall in `TAS-2` spread relative to `W0`, even while clearing the bar, is
   reported as the headline** — not buried under the coverage gain. Stating this now because
   the coverage number is the attractive one and will be the tempting lead.
3. **`TAS-3` stays diagnostic and carries no bar** — unchanged from §2, and no threshold is
   invented for it here. Its rank correlation and already-ordered share are reported for every
   frame. A rise in either means the enriched signal is *more* redundant with similarity, which
   is the flattening failure above showing up in a second place.
4. **The share of candidate slots where the rule ACTS** (both ends labelled) is reported per
   frame. This is descriptive and has no bar. It is the quantity that would drive any `TAS-6`
   improvement, so it is what makes a re-run worth its cost — or not.
5. **Nothing here licenses a `TAS-4` or `TAS-6` re-run, an adoption, or a rebuild.** If every
   read is favourable the outcome is a *recommendation to the owner*, not an enactment.
   **`TAS-6`'s adverse verdict on the committed frame stands regardless of what this shows** —
   it is not retroactively softened by a better frame existing.
