# Design inputs for the cap re-evaluation pre-registration

**Role: ACTIVE — the single address for what the 2026-08-02 owner conversation settled
and reasoned about the rebuild, written so the pre-registration can be authored cold.**
Owns no figures (every number cited to its owner) and takes no design decisions the
prereg author owns — it records the owner's rulings, the measured landscape, and the
inferences with their labels. Where this document and a governing spec disagree, the
spec governs. Companion to `2026-08-02-HANDOFF-fame-instrument.md` claim 5 and the
execution log §1, which it expands.

## 1. The goal, as the owner stated it

Journeys that better align with `PRODUCT-REQUIREMENTS.md`: **no matter which two
starting artists you pick, use of the bypass button should overall create a gradient
that trends toward obscure** — `REQ-42`'s shape (movement with depth, never
band-reaching; a famous-famous gradient of zero fails `REQ-13`). Candidate
architectures are evaluated **on both data sets (`ALG-E` and `ALG-B`) until a clear
winner emerges**. Currency: `fame_lb_pctl` (adopted 2026-08-02; the `NOV-` record).
"Obscure" means novelty-likelihood — and note log §8: the famous band is ~73% novel to
the owner, so the famous band is **not** a novelty dead zone and the gradient's floor
starts higher than the retired worldly-fame frame assumed.

## 2. The candidate families, spelled out

Recorded as "(a)–(d)" in the log §1; the definitions are these:

- **(a) Numeric-cap variants of the incumbent** — mutual k-NN at bounds including 50 vs
  100. Measured status: `R0` null on `ALG-E`, decisive on `ALG-B` (Track B results
  note §1).
- **(b) Union without reciprocity, numeric budget** — pool both artists' lists, trim to
  the same budget (`TU`). Measured status: the coverage winner (loses 1 artist where
  `MK50` loses 800), hubs *less* dominant, **no edge explosion — the trim bounds degree
  by construction.** This, not (d), is what "drop the must-be-mutual requirement"
  means at bounded cost.
- **(c) Union with a tag-based degree limiter replacing the numeric cap** — the
  owner-triggered `NEXT.md` deferral row ("ruled SEPARATE and explicitly NOT ruled
  out"). Unmeasured as a family; §5 below carries its design constraints.
- **(d) Router-priced unbounded** — no bound at all, the router does the bounding. In
  the grid **as staged comparison data** behind a structural screen (owner: "more data
  is worth it, if only for comparison"); it owes its own blind listen on adoption
  (`NEXT.md` parked row). §4 below is why its prior condemnation is weaker than it
  reads.

Tag arms may act in **construction, routing, or both** — the owner explicitly left that
as an evaluation axis, not a prior.

## 3. Why router pricing is inside scope — the synthesis a cold session cannot cheaply re-derive

Three measured results triangulate, each owned elsewhere:

1. **Router tuning alone, on today's graph: closed null.** Track 3b — even at zero cost
   for obscure interiors and a toll on famous ones, the router shortens instead of
   descending. The routing-side toll family is closed for descent claims (`NEXT.md`).
2. **Graph supply alone, at production weights: null on `ALG-E`.** Track B's quota
   cells force-connected every famous artist to its ten strongest obscure partners,
   verified the edges exist — and the router took none. The union (`TU`) cells also
   delivered zero sub-decile interiors on `ALG-E`. **Cite this only as "the router
   declines the quota edges *at production weights*"** — `NEXT.md`'s closed ruling; the
   pricing track owns the difference.
3. **On `ALG-B`, famous journeys occasionally reach obscure artists even under the
   incumbent rule** (`CRS-C5`) — the data set moves what is *possible* more than the
   cap rule does.

**The genuinely untested cell is new supply × new pricing.** Neither Track B (barred
from touching weights) nor Track 3b (production graph only) tested the combination, and
the owner's depth-indexed goal lives in it. Consequences: any pricing arm **consumes
`TB-P5H-7`**; and the `known` bypass semantics (`REQ-27`: highly similar AND more
obscure) are the device the gradient acts through.

## 4. The mutual-kNN structural picture, and the blind-listen lineage

- **LB similarity scores are symmetric by construction** (`LBS-1`, from source;
  `CS-P0f` measured it). List asymmetry is purely the per-artist top-N cut — so
  mutual k-NN severs exactly the famous↔obscure pairs where the obscure side ranks the
  famous artist and the famous side's list is full.
- **The owner's cap analysis, corroborated by the record:** artists under ~100
  candidates are fully known (no hidden connections to recover); popular artists have
  thousands of listers hidden by the cap (`CB-P1`: Radiohead has 12,776 sub-decile
  listers; `UC` max degree 15,631) — union rules re-expose them, which is both the
  opportunity (b)/(c) exploit and the mega-hub mechanism (d) must price. **Pairs where
  both sides rank each other below the cut are unrecoverable from any archive — a
  property of the source, identical in every arm, so it bounds recovery but can never
  confound a comparison.**
- **The case against unbounded was never isolated, and predates the goal.** The two
  blind listens capfix won ran 2026-07-21–23, adjudicated on first-path coherence,
  before the requirements layer (2026-07-29) made the bypass gradient a governing goal
  — and `SYN-6` records that **neither listen separated reciprocity from the degree
  bound** (the bound is an *effect* of reciprocity in this codebase; no artifact
  separating them was ever built). What *is* clean and recent: `UC`'s structural
  numbers (hub transit 0.97–1.00 on famous pairs, top-1% degree mass ≈5× any capped
  cell — Track B results note §1). So (d)'s prior condemnation is confounded evidence
  under a superseded definition of good; its structural cost is measured fact. Both
  halves travel together.

## 5. Tags: the constraint, the dissolved hazard, and the design notes

- **Owner constraint, ruled 2026-08-02: LB similarity is the sole source of edge
  existence; tags only re-order, re-weight, or remove** (removal aimed at hubs). Under
  a union source this **dissolves the edge-growth hazard by construction** — the union
  is a hard upper bound and every tag operation moves the count down. The `NEXT.md`
  deferral row "tag-aware selection increases the map's total edge count … before any
  rebuild pre-registration is written" is satisfied by stating this constraint in the
  prereg; the `TAS-4` growth mechanism (symmetric Jaccard creating mutual pairs
  pre-cap) cannot operate when nothing is created.
- **What stays closed:** the λ-Jaccard *reordering* device (`TAS-6` selection half
  ADVERSE — it cut famous→obscure connections because tag-boosting promotes labelled
  partners); router-side genre pricing *as previously designed* (`TAS-AM5c`: its effect
  was indistinguishable from any added cost). A new tag arm is the new device, not a
  revival.
- **The agreement device is the `WGT-` recommendation: rarity-weighted agreement over
  `W4`** (input-only, on the record). `W6` must not be the frame any arm names.
- **The dark tail:** labels are near-total among famous bands (94–100%, `COH-2`) and
  dark in the obscure tail — the limiter's bounding work is needed exactly where labels
  are good, and where labels are dark the default is LB similarity untouched. "The
  coverage hole and this use are close to complementary" is **inference, not
  measurement** (`NEXT.md` parked-strand text); the adverse mechanism must be
  *measured* per arm, not assumed either way — famous→obscure supply is a primary
  metric here anyway.
- **Any router-side tag arm requires a scrambled-labels control** (`TAS-AM5c`'s
  lesson), or the any-cost artifact will reproduce.

## 6. The owner's hypothesis, labelled, and its cheap first read

**Guesswork, flagged as such by the owner:** popular↔popular co-listening
relationships are less likely to be *musically* similar than obscure↔obscure ones
(popular co-listening reflects shared mainstream exposure), with popular↔obscure in
between — the reason tags could refine the top of the graph specifically. **Cheap
design-informing read, proposed and endorsed in conversation:** rarity-weighted tag
agreement per edge against the endpoints' fame band, descriptive, computable from the
committed tag frames with no new collection. If the gradient holds, it is the direct
justification for tags-refine-the-top; if not, family (c)'s premise weakens before
anything is built on it. Belongs early in the prereg as a labelled descriptive read.

## 7. Criteria notes the owner fixed, and what they re-weight

- **Coverage is a guard, not a success metric: ~10,000 artists lost disqualifies an
  arm.** Even `ALG-B` under the incumbent (6,499) survives that bar.
- **Hubness: first-path hub transit is tolerable — hubness *rising with bypass depth*
  marks an arm failed.** This deliberately re-weights Track B's `C4` flag (the
  bound-100 famous-pair hub-transit increase was a *first-path* measurement and no
  longer disqualifies at depth 0). The depth-indexed hub measure is **new** — no track
  has taken it.
- **Every primary outcome is depth-indexed** (gradient form). Instrument obligations
  carried from `FAM-AM1`: gradient claims exceed **10× the ruler's measured
  quantisation step** (0.0015); aggregates reported all-interiors AND matched-only with
  null counts per depth; the **population-vs-descent confound** goes in the factor
  table (an `ALG-B` arm's interior percentiles differ partly because the populations
  differ — median `fame_lb_raw` 6.1× between adopted artists in/not-in `ALG-B`); the
  ruler cannot order candidate-only artists within the 1–5-listener clump
  (`FAM-AM2.2`), so no read may consume within-remainder ordering.
- **Path-level evidence today rests on 22 famous-pair journeys** — the obscure-endpoint
  classes were unreadable at the committed draw (`CRS-G3`). Famous pairs are the hard
  case and the right first target; if a bar leans on obscure-endpoint behaviour, the
  parked redraw (a new §8-class amendment, owner's trigger) becomes part of the price.
- **`w_degree_hub` is decided deliberately and recorded** — it cannot self-activate
  (zero coefficient), but the *reason* it is zero rests on the current graph's
  top-degree set, which a new connection rule changes (`NEXT.md` corrected row).

## 8. Process rulings

**Ordering, ruled by the owner 2026-08-02 (night): the featured-credit filter track runs
BEFORE this pre-registration is written.** Its frozen per-population lists join the
held-constant section of this document's factor table exactly as the no-release drop
lists do — the comparison's cleanup must be identical in every cell, and the class would
otherwise activate only in arms that succeed at pushing obscure (the dormant-term shape)
while the adopted currency scores its delivery as success. `NEXT.md`'s top block owns the
current state of that track.

Staging: **a structural screen cuts arms that provably cannot move the gradient before
any depth sweep runs** — depth sweeps are the cost that scales, and (d) enters only as
staged comparison data. Track B's committed cells are **reused, never re-run**
(byte-deterministic; `NEXT.md` closed list). Handoff seams are named at authoring time
(the >8-task rule). The blind listen (`REQ-38`) remains the primary evaluation for any
adoption, and the deferred isolated listen on the post-drop graph has its condition in
`NEXT.md`'s table — a combined rebuild that sounds worse triggers its decomposition
branch.
