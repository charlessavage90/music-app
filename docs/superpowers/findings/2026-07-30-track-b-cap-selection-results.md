# Track B results — cap-rule selection at production scale

**Role: AUTHORITATIVE for Track B's results.** Raw record:
`builder/analysis/2026-07-30-track-b-cap-selection/cb_scores.json` (commit
`35e63bf`, committed before any read was opened). Criteria, bars and read
order are the pre-registration's
(`specs/2026-07-30-track-b-cap-selection-preregistration.md`, `CRS-`); the
per-read verdicts with run-state sentences are in
`2026-07-30-track-b-runs-execution-log.md` §CB-6. This document is the
four-part presentation. **It licenses a recommendation input to two parked
owner decisions and nothing else** (prereg §5): no adoption, no default
change, no weight retune, and a blind listen (`REQ-38`) is owed before any
adoption regardless of these numbers.

Grid: 24 cells — 12 rules per archive (`ALG-E` = production data,
`ALG-B` = candidate data), identical grids, production router weights stated
in every output. All instrument gates green and red at the scoring commit;
`CRS-G2` (bound holds) passed in all 22 selectable cells; `CRS-G4` never
fired.

> ## ⚠ FORWARD CORRECTION, 2026-09-07 — `CRS-C3`'s silence carried no information
>
> **This document stays exactly as written and every figure in it stands as measured.** The
> correction goes forward, and it concerns only how one criterion's *null* should be weighted.
>
> `CRS-C3` flags a cell whose `top1pct_degree_mass_frac` exceeds its archive's `MK50` by ≥ 50 %
> relative, and §2 reports that **no selectable cell fires the `C3` flag**. That statement is
> arithmetically correct. It is also **the only outcome the criterion could have produced**:
> where at least 1 % of a cell's nodes sit at its degree bound, the statistic reduces
> algebraically to `bound ÷ (100 × mean degree)` and cannot see how edges are arranged. Tested
> against this document's own raw record, `cb_scores.json`: the identity holds on **all ten
> `trimmed_union` cells** to within 1.6 × 10⁻⁴, and pins the `mutual_knn` and `proximity_select`
> cells inside a window 4–12 % wide. **Given only its own bound and mean degree, no selectable cell
> could have exceeded 73.5 % of its own flag threshold.** The two cells that would have fired,
> by a factor of 32–35, are the **uncapped** pair — which the pre-registration barred from
> candidacy.
>
> **Figures owner for that arithmetic:**
> [`../../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md`](../../../builder/analysis/2026-09-07-degree-floor-at-admission/README.md)
> §9, with the derivation behind it in that document's §8, and the raw record beside them.
> **The three numbers in the paragraph above are carried here deliberately** — a warning a reader
> cannot size is not a warning — but they are that document's, not this one's, and this document
> owns none of them. **Every figure this document does own is untouched.**
>
> **Three limits, because each is easy to overrun.** ① This says **nothing about `CRS-C4` hub
> transit**, which is a routing measure over built paths, is not saturation-degenerate, and whose
> bound-100 finding stands exactly as recorded below. ② It **overturns none of this document's
> conclusions**, which rest on the other criteria; `C3` was *a flag, not a gate* by its own
> pre-registration, and a flag that could not fire changed no verdict. ③ It is **not evidence
> about any cap rule** — that decision is parked and the owner's and owes a blind listen before
> any adoption.

## 1. Measured

Anchors (`GRT-P4`, reproduced by the gates): `ALG-E`-`MK50` vs `ALG-B`-`MK50`
= lower-half stranding 0.08 % vs 7.00 %, exclusion 1.07 % vs 8.67 %.

**`CRS-C1` / `C2` — the k-curve (`R0`) and matched-bound families (`R1`):**

| Cell | `ALG-E` C1 | `ALG-E` C2 (abs) | `ALG-B` C1 | `ALG-B` C2 (abs) |
|---|---|---|---|---|
| `MK50` | 0.08 % | 1.07 % (800) | 7.00 % | 8.67 % (6,499) |
| `MK60` | 0.08 % | 0.67 % (500) | 4.33 % | 6.03 % (4,518) |
| `MK75` | 0.07 % | 0.42 % (314) | 2.20 % | 3.20 % (2,402) |
| `MK100` | 0.07 % | 0.30 % (225) | 0.21 % | 0.42 % (312) |
| `TUw-50-50` | 0.07 % | 0.00 % (1) | 0.64 % | 0.72 % (538) |
| `TUq-50-50` | 0.07 % | 0.00 % (1) | 0.63 % | 0.71 % (532) |
| `PS50` | 5.62 % | 3.13 % (2,348) | 8.67 % | 6.91 % (5,179) |
| `TUw-50-100` | 0.07 % | 0.00 % (1) | 0.07 % | 0.04 % (34) |
| `TUq-50-100` | 0.07 % | 0.00 % (1) | 0.07 % | 0.04 % (34) |
| `TUw-100-100` | 0.07 % | 0.00 % (1) | 0.07 % | 0.01 % (6) |
| `PS100` | *byte-identical to `MK100`* | | *byte-identical to `MK100`* | |
| `UC` *(reference, barred)* | 0.07 % | 0.00 % (1) | 0.07 % | 0.01 % (6) |

Verdicts under the pre-registered bars: `R0` **null on `ALG-E`** (no material
k step), **decisive on `ALG-B`** (every step material, cumulative 6.79 / 8.25
points against decisive bars of 3.46 / 3.80). `R1`: **the incumbent loses at
bound 50** — both `TU` trims beat `MK50` decisively on `ALG-B` and materially
on `ALG-E` (`C2` 1.07 % → 0.00 %), with `C3` degree mass *falling* ~40 % (no
flag) and `C4` hub transit falling. `PS50` is materially **worse** on `C1` on
both archives. `R1a` (reciprocity isolation at k = 100, claim confined to the
~89 % of nodes below the ceiling): **null on both archives** — reciprocity
alone costs ≤ 0.41 points on any criterion.

**`CRS-C3` / `C4` — hub structure and transit:** no selectable cell fires the
`C3` flag. The bound-100 set fires `C4`'s ≥ +50 % material bar on the broad
famous class on both archives (`ALG-E` +53…+90 %; `ALG-B` +75…+152 % vs
`MK50`), measured on that graph's own top-degree set. `UC` reference: top-1 %
degree mass ≈ 0.199 (≈ 5× any capped cell), max degree 15,631 / 17,883,
famous-pair hub transit 0.97–1.00.

**`CRS-C5` — famous-pair sub-decile presence (`R2`):** baseline measured
first per `CRS-A2`: **zero in both famous classes on `ALG-E`-`MK50`** (0/12,
0/10), so "any nonzero is decisive" stood. On `ALG-E`: **zero in every cell,
including both quota cells** — verified against the artifacts that the quota
cells hold the reserved obscure edges at famous nodes (Radiohead, The
Beatles, Metallica: 10 each at d = 50; 19/18 at d = 100) and the router takes
none of them at production weights. On `ALG-B`: nonzero nearly everywhere,
**including the production rule itself** (`MK50`: 2/12 broad, 5/10 narrow).

**`CRS-C6` — survival tilt (`R3`):** +1.53 percentile points
(survivors 86.03 vs vanished 84.50, 325,027 common edges) — direction as
pre-committed (`LBS-4`), **below the 5-point material bar**. User-count
companion (descriptive, endpoint re-verified per `CRS-A5`, shared-blind-spot
caveat carried): same direction, 5,839 vs 5,526.

**Flags that travel with all of the above:** every `MK` cell below k = 100 and
every `TU` cell is tie-dominated per `CRS-H1` (cut-tie shares 0.32–0.70; the
MBID tie-break decides those survivors); `PS` cells are tie-free. The
common-routable pair restriction cut the draw 82 → 39: both famous classes
readable, **all five `× lower` classes unreadable per `CRS-G3`** — path
criteria in this document rest on famous pairs only; stranding criteria use
no pairs. `CRS-H2`: ~all quota-reserved partners remain sub-decile under the
adopted frame (share in `cb_ties-*.json`).

## 2. What I infer from it (inference, in the app's terms)

- **Nothing a user sees today has changed, and these results adopt nothing.**
- **The rule that decides which artists get connected is costing us artists
  for no measured benefit.** Today's rule requires two artists to each rank
  the other highly, then keeps at most 50 connections. A rule that pools both
  artists' lists and trims back to the *same* 50-connection budget loses
  **one artist** from the map where today's rule loses **800** — with the
  most-connected artists ending up *less* dominant, not more. I would expect
  a user to notice exactly one thing: artists who today cannot be found or
  reached would appear, and everything else would look the same. Whether it
  *sounds* the same is precisely what no offline number here can say.
- **The candidate data's alarming numbers were mostly our own cut-off, not
  the data.** "R.E.M. drops to 6 connections, 6,499 artists cut off" was
  measured with our must-be-mutual rule at 50. Widen the window to 100, or
  drop the must-be-mutual requirement, and the candidate data keeps nearly
  everyone (0.21 % / 0.07 % of obscure artists cut off, against 7 % as
  first measured). The two ingredients are individually cheap and expensive
  only together.
- **On today's data, no connection rule makes a journey between two famous
  artists pass through anyone genuinely obscure.** We built graphs where
  every famous artist is force-connected to its ten strongest obscure
  partners, confirmed those connections exist, and the journey-builder still
  routed around every one of them — the way it prices fame jumps outranks
  the new connections. Fixing that means changing the router's pricing, which
  this track was explicitly barred from touching; the finding is now
  measured, not guessed.
- **On the candidate data, those journeys do occasionally dig up someone
  obscure — even under today's rule** (between very famous artists, half the
  test journeys under the narrow class). The candidate data changes what is
  *possible*; the rule changes how much of the map survives.
- **The feared hidden cost of the candidate data measured small.** The worry
  was that its surviving connections quietly lean famous. They lean famous by
  1.5 percentile points on the median — a third of the bar we set for
  "matters."
- **The price of removing the connection bound altogether is now a number**:
  nearly every step of a famous journey passes through the most-connected
  artists. That is the mechanism the blind listen condemned, so it stays
  barred from candidacy; the number exists so a future re-evaluation starts
  calibrated.

## 3. Weakest link

**The path-level half of this document rests on 22 famous-pair journeys.**
The pre-registered restriction to pairs routable in every cell collapsed the
obscure-endpoint classes below `CRS-G3`'s readability bar, so hub-transit and
sub-decile claims are famous-pair claims; nothing here measures what a
journey between two obscure artists does under any candidate rule. What would
falsify the headline: a redraw with readable `× lower` classes showing `TU`
cells degrade obscure-endpoint journeys (longer, more no-paths, higher hub
transit) — the structural criteria cannot see that. Second: `C4`'s "own
top-1 %-by-degree" set is ill-defined on cells where thousands of nodes sit
at the ceiling (membership among tied degrees is selection-order arbitrary);
the production-set companion column in `cb_scores.json` is the well-defined
variant and tells the same directional story. Third: every `MK`/`TU` cut is
tie-dominated — which of two equal-scoring artists survives is decided by
MBID; the *shares* are stable, but named-artist claims ("R.E.M. keeps X
connections") are one tie-break away from moving. I would defend the
stranding/exclusion table and the two nulls anywhere; I would abandon
cheaply any named single artist's degree and any reading of `C4` finer than
its ≥ +50 % bar.

## 4. Options and their consequences (decisions are the owner's; both named
decisions are parked)

1. **Do nothing.** The app is unchanged; `DD-F1` (famous journeys never
   obscure) remains a standing defect by `PRODUCT-REQUIREMENTS.md`'s ruling;
   the 800 excluded artists stay excluded.
2. **Rebuild today's data under `trimmed_union` at bound 50** (either trim).
   Consequence: ~799 artists rejoin the map, no measured hub cost at that
   bound, journeys otherwise measure the same; does **not** touch `DD-F1`
   (the router prices the quota edges away); owes the blind listen before
   adoption (`REQ-38`); retires none of the archive questions.
3. **Pick up the parked `ALG-B` adoption with a widened window or union
   rule.** Consequence: the stranding/exclusion objections mostly dissolve
   (`R0`/`R1`), famous journeys gain the possibility `DD-F1` asks for
   (`R2`), the survival-tilt cost measured immaterial (`R3`) — and the
   bound-100 hub-transit flag raises the blind listen's priority; adoption
   retires every existing path-quality figure (`NEXT.md`'s standing note).
4. **The router-side future track** (plan §0 ruling 2, owner's trigger): the
   one place `DD-F1` can be fixed *on today's data* is the router's pricing —
   the structure is now proven present and declined. Needs its own
   pre-registration, which must consume `TB-P5H-7`.

**What cuts against the headline, stated plainly:** the incumbent's loss is
on map-coverage criteria measured on famous-pair-only path evidence; if
listening coherence under a union rule is worse, nothing offline here would
have seen it — the blind listen is load-bearing for any adoption, and the
bound-100 cells carry a measured hub-transit increase in the direction the
ear previously condemned.
