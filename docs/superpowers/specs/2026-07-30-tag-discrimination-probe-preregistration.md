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

*Plain: swapping two neighbours out of fifty will not change a journey you would notice.*

Simulated over the archive, no rebuild: the top-50 set under λ = 0 versus each λ > 0, for
artists whose own candidate list exceeds 50 (the only artists for whom selection has a
choice to make; the share of such artists and of edges incident on them is reported).

**Kill for the build-time architecture: if at every λ the median artist swaps ≤ 2 of 50.**

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

**Red:** the same harness, fed a randomised tag frame, must report large swap rates and large
path-change rates. A measurement that has only ever come back green is not evidence yet — the
standing rule in project memory, and the reason this is written down before the run rather
than offered afterwards as reassurance.

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

*(None yet. Entries appended here after commit, never edited in place; nothing above is
renumbered once committed.)*
