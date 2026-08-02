# Design critique of the FAM- fame-instrument pre-registration, before its experiment runs

**Scope: design critique and derivation only.** No recommendation on adoption — that is the
owner's, downstream of measurements that do not exist yet. Document under critique:
`docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md`.

## Provenance of everything below

| item | identity |
|---|---|
| adopted artifact | `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` (verified by hashing the file; matches `cb_metrics.ADOPTED_SHA`) |
| candidate artifact | `builder/scratch/graph-algb-full.bin`, 68,467 artists |
| LB snapshot | `builder/analysis/2026-07-30-fame-proxy-coverage/fp_listenbrainz.json`, sha256 `c47fbd2260eaf76473a24348785c42ba87d457ced216b6999e036971cebe6fbf`, 74,193 keys, 42 nulls |
| probes | `<scratchpad>/fam_probe.py`, `<scratchpad>/fam_probe2.py`, run as `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u <file>` |

**A deliberate limit on what I measured.** I read the retained snapshot for tie/atom
structure only, as the brief directed. I did **not** look up any named artist, so no
`FAM-3` or `FAM-4` verdict is computed or leaked here; their critique below is structural
(pair arithmetic, blast radius, power) and uses no ruler value. See `D4` — this line was
worth drawing because the snapshot makes three of the five criteria answerable today.

## Measured facts the critique rests on

**Distribution of `fame_lb_raw` over the adopted frame** (74,151 non-null of 74,193;
99.9434%, which reproduces `FPC-4`):

| quantity | measured |
|---|---|
| zeros | 0 |
| min / median / max | 1 / 1,335 / 455,551 |
| distinct values | 18,402 |
| artists at raw value 1 / 2 / 3 | 11 / 2 / 13 |
| cumulative frame share at raw ≤ 15 | 1.06% |
| largest tie atom anywhere | 109 artists at raw 29 = **0.147% of the frame** |
| largest `fame_lb_pctl` quantisation step anywhere | **0.00138** |

**Distinct `fame_lb_pctl` values and worst atom, by region:**

| region | distinct pctl values | largest atom (frame share) |
|---|---|---|
| bottom decile | 107 | 0.00147 (109 artists) |
| rest of lower half | 1,229 | 0.00104 |
| upper half | 10,229 | 0.00027 |
| top decile | 6,837 | 0.00005 |

**Where the percentile scale sits in listener counts:** pctl 0.01 ↔ 16 listeners;
0.10 ↔ 108; 0.25 ↔ 370; 0.50 ↔ 1,337; 0.90 ↔ 16,379; 0.99 ↔ 117,564; 0.999 ↔ 325,267.

**Percentile points bought by a fame drop, by starting point:**

| start raw | start pctl | after ÷2 | after ÷10 | after ÷100 |
|---|---|---|---|---|
| 100,000 | 0.9870 | +0.019 | +0.139 | +0.548 |
| 10,000 | 0.8479 | +0.101 | +0.409 | +0.754 |
| 3,000 | 0.6570 | +0.134 | +0.440 | +0.629 |
| 1,335 | 0.4998 | +0.143 | +0.381 | +0.492 |
| 100 | 0.0942 | +0.044 | +0.089 | +0.094 |

**Frame arithmetic (the prereg's three population figures all verify):** adopted 74,193;
ALG-B 68,467; union **93,067**; overlap 49,593; **ALG-B-only 18,874 = 20.3% of the union**;
adopted-only 24,600. Median `fame_lb_raw` of adopted artists also in ALG-B: **2,501**; of
adopted artists *not* in ALG-B: **409** — a 6.1× difference between two subsets of the same
graph.

**A correction to my own prior expectation, stated first.** I expected the integer tail to
be dominated by huge ties at 1, 2, 3 listeners, and predicted `FAM-2` would be too weak to
catch it. **That is refuted.** Eleven artists sit at 1 listener and thirteen at 3; the lower
half spans integers 1–1,334 with *every* integer occupied. The crawl seeds from LB sitewide
stats, so the frame is famous-skewed and never reaches the raw tail where ties would bite.
The instrument's resolution on this frame is genuinely good — **better than `FAM-2` tests
for**, which turns out to be the actual problem with `FAM-2`.

---

# Findings, severity-ranked

## A — design defects that could make a verdict unreadable

### `A1` — `FAM-5`'s ρ ≥ 0.99 bar is satisfied by total destruction of the tail's ordering

Measured, by re-running Spearman on the snapshot against controlled perturbations of itself:

| scenario | ρ |
|---|---|
| realistic 3-day drift (Poisson at 0.5% of `u`) | 0.999999 |
| heavy drift (Poisson at 5% of `u`) | 0.999991 |
| ordering **destroyed** among artists with `u ≤ 10` | 1.000000 |
| ordering **destroyed** among artists with `u ≤ 100` (bottom 9.4% of frame) | **0.999154** |
| `u ≤ 100` re-drawn uniform 1–100 (garbage tail) | **0.999144** |
| ordering destroyed among `u ≤ 1000` | 0.915607 |
| ordering destroyed across the whole lower half | 0.875566 |

So the bar has a dead zone: real stability reads 0.999999, and *complete* instability of the
bottom decile still reads 0.9992 and passes. The bottom decile is the region the ruler is
being adopted for. Compounding it, `total_user_count` is cumulative-lifetime and monotone
non-decreasing, so the criterion is near-vacuous against the drift it was written for.

**Fix (one line):** bar ρ **within each of the five existing `cb_metrics.BANDS`**, and add a
bar on the 99th percentile of |Δ`fame_lb_pctl`| across the overlap. Both are computed from
the same two arrays.

### `A2` — no criterion anywhere tests *ordering* in the obscure region

`FAM-1` and `FAM-2` are counting properties. `FAM-3` is the top 1%. `FAM-4`'s pairs all sit
at ≥168,000 Spotify monthly listeners — the famous stratum. So every validity check in the
design lives at the top of the distribution, while the stated reason for the change
(`§0.4`, `FPC-9`) is that the incumbent goes blind on 38.7% of what a successful obscurity
push would deliver.

`§4` says a pass licenses nothing about validity, which is honest but does not close it: the
pass-consequence *does* license writing the cap re-evaluation's primary outcome in this
currency, and that outcome is a gradient read on artists the design never checks the
ordering of. This is the single largest gap.

**Fix:** either add a tail-ordering criterion against an outside population (hand-read
Spotify counts on ~15 artists sampled from `fame_lb_pctl < 0.25`, which is the same
instrument `WHAT-GOOD-LOOKS-LIKE.md` already licenses), or state in `§4` that adoption rests
on coverage + resolution + top-end concordance **only**, that tail ordering is assumed, and
name what would falsify it.

### `A3` — `FAM-4`'s ≥10× filter removes, by construction, every pair that could detect a sub-decade error

Monte Carlo over the 34 qualifying pairs, modelling the ruler as hand-read × 10^N(0,σ) with
the noise drawn **per artist** (so it propagates through every pair that artist is in),
20,000 trials:

| per-artist error σ (decades) | typical factor | P(`FAM-4` passes) |
|---|---|---|
| 0.20 | 1.6× | 1.0000 |
| 0.30 | 2.0× | 0.9999 |
| 0.50 | 3.2× | 0.9195 |
| 0.75 | 5.6× | 0.5774 |
| 1.00 | 10× | 0.3354 |
| 1.50 | 32× | 0.1436 |

A ruler that mis-scores the typical artist by a factor of three passes 92% of the time.
`FAM-4` discriminates only against rulers wrong by roughly an order of magnitude per artist.
That is a valuable sanity gate, but `§2` calls it "the load-bearing criterion" and "the
criterion that can actually fail informatively", and it cannot see the resolution question at
all — which is precisely the property a *gradient* read needs.

**Fix:** keep the ≥10× set as the hard gate, and add a rank-correlation read (Kendall τ or
Spearman) over **all 15** hand-read artists with its own bar fixed now. That uses the pairs
the ≥10× filter throws away, which are the only ones carrying resolution information.

### `A4` — the 90% bar is a per-artist bar wearing a per-pair bar's clothes

34 pairs at ≥10×, drawn from 15 artists. Blast radius per artist (how many pairs flip if that
one artist's ruler value is wrong): Lykke Li 8, Beach House 8, Blood Red Shoes 7, New Order
6, and five artists at 5. The bar tolerates **3 wrong pairs**; 4 fails.

Consequence: **10 of the 15 artists, if mis-read, fail `FAM-4` single-handedly.** Only
Quantic (1), Nightmares on Wax (1), NOFX (2), Boards of Canada (2) and Black Rebel Motorcycle
Club (3) can be wrong without failing it. The effective sample size is ~15 artists with a
tolerance of about one peripheral error — i.e. close to a 100%-agreement bar on 15 items,
not a 90% bar on 34.

**Smallest number of clear pairs at which a 90% bar is readable, as asked:**
- At m ≤ 9, ⌈0.9m⌉ = m, so "90%" is arithmetically a **100% bar with zero tolerance**.
  **m ≥ 10 is the floor** for the stated bar to mean what it says.
- Against a coin-flip null: P(≥90% agreement) = 0.0313 at m=5, **0.0107 at m=10**,
  0.00049 at m=15, 0.0002 at m=20, 4×10⁻⁶ at m=30. So m ≥ 10 for p < 0.05, **m ≥ 15 for
  p < 0.001**.
- With *these* pairs the independence assumption fails, so the honest statement is
  **15 effective units, ~1–2 tolerated errors**, not 34 with 3.

**Fix:** state the bar in artist units as well ("no artist whose ruler value contradicts its
hand read"), and report the count of artists implicated alongside the pair rate.

### `A5` — `FAM-4` admits at least one unflagged name-ambiguous hand read, with enough leverage to fail the criterion alone

The exclusion rule is "whose identity the record does not flag as ambiguous (the
`FERG`/A$AP Ferg class is excluded)". The hand reads were **Spotify name lookups**, and
`BYP-13`'s own guard is *read the MusicBrainz disambiguation before trusting a name lookup*.
The record contains a documented collision for at least one artist on the list that `BYP-`
does not flag: `FPC-10` records that a name search for **"Love"** scored **Sean Combs** at
5.9M pageviews. Love is on the list at 571k, with blast radius 5 → a wrong value drops
agreement to 85.3% → **FAIL**, and `§4` makes any failure block adoption with no fallback.

"Television", "Quantic", "10cc" and "NOFX" are the same shape of risk; `MKS-7` records 1,283
names shared by 2,838 artists (3.83% of the graph), and `BYP-13` was found only because the
owner typed the name into the app's search box.

**Fix:** before running `FAM-4`, resolve all 15 to MBIDs via the app's search (the `BYP-13`
procedure), record the MBIDs in the pre-registration as an amendment, and drop any whose
identity cannot be confirmed. This must happen **before** the ruler values are read, or it
becomes post-hoc exclusion.

## B — bar mis-calibration

### `B1` — `FAM-2`'s "≥ 1,000 distinct values" is arithmetically a test of the frame's *median*, not of resolution

The counts are integers, and the lower half spans 1..(median). So the number of distinct
values in the lower half is bounded above by median + 1, and equals it exactly when the
integers are dense. **Measured: 1,334 distinct values, boundary value 1,334, upper bound
1,336 — every integer from 1 to 1,334 is occupied.**

So passing the bar is arithmetically equivalent to *"the median artist in the frame has
≥ ~1,000 ListenBrainz listeners"* — a property of the population, not of the instrument. It
would fail on a frame whose median artist had 900 listeners even though the instrument's
resolution there is identical (still one distinct value per integer). Its direction is
perverse: a graph that reached obscurer artists — the entire point of the cap re-evaluation
— would score *worse* on this bar with an unchanged ruler.

**Fix:** replace with a direct resolution bar — the largest `fame_lb_pctl` quantisation step
(= largest tie atom ÷ 74,193), reported per band. Measured today: 0.00138 overall, 0.00147 in
the bottom decile.

### `B2` — `FAM-2` has no effect size, and `§0.3`'s sequencing means it structurally cannot get one here

`CLAUDE.md`'s own rule: every gate and branch trigger needs its own effect size. `FAM-2`'s
two bars have none — the gradient they must resolve is fixed in the cap re-evaluation
pre-registration, which `§0.3` deliberately writes **after** this verdict. That is a real
structural bind, not an oversight, and it should be named rather than left implicit. As
written the "< 5%" bar carries ~17× slack against the measured 0.294%, so nobody will notice
it is untethered.

**Fix (cheapest closure, and it preserves `§0.3`):** state here that the cap re-evaluation
pre-registration owes a **back-check** — that any gradient it claims must exceed the ruler's
measured quantisation step by a stated factor — and carry today's measured step forward as
the number that check uses.

### `B3` — `FAM-2` bars only the single largest atom; the natural failure shape is many medium atoms

Measured: top-5 atoms combined = 1.35% of the lower half, so there is no live risk on this
frame. But a ruler that binned artists into, say, forty 2%-blocks would pass the bar as
written while being useless. **Fix:** add the top-5 combined, or bar the *count* of distinct
percentile values per band (measured: 107 / 1,229 / 10,229 / 6,837).

### `B4` — `FAM-3` cannot fail in the direction of the hazard `§2` says is load-bearing

The nine names are all Anglophone rock/alt acts, on a ruler computed from a Western,
tech-forward listening corpus. That is precisely the population LB **over**-represents. So
`FAM-3` cannot detect the shared LB/Wikipedia population blind spot that `§2` says travels
with every figure — it is a smoke test that the scale is not inverted. Correct as far as it
goes, and the exclusion of `acceptance.py`'s top-N-by-popularity set genuinely removes the
circularity `§2.11` would otherwise create.

**Fix:** label it a smoke test in `§3` rather than presenting five criteria of equal weight
whose failure equally blocks adoption.

### `B5` — `FAM-3`'s list is enriched in artists selected *because* their ListenBrainz data is thin

The list is "from names already in the project record". Three of the nine — **R.E.M., Pixies,
PJ Harvey** — entered the record as the `RC-A2`/`GRT-P2` collapse tracers: artists that
reciprocate *nothing at all* under ALG-B at k=50 because they sit at rank 50–97 in their own
candidates' lists (`2026-07-29-graph-rebuild-track-a-execution-log.md` §7b;
`2026-07-29-reciprocity-sampling-preregistration.md` `RC-P2`). That thinness is on the **same
LB corpus** the ruler is computed from.

This is not strict circularity — reciprocation is not listener count — but it enriches the
list toward artists most likely to be under-ranked by an LB-derived ruler, and `§4` makes any
failure block adoption with no partial-adoption escape. Severity in absolute terms: the 0.99
bar admits the top 742 artists and corresponds to **≥ ~117,564 LB listeners** on this frame,
which is a demanding bar for a mid-tier alternative act.

**Fix:** either allow *k* of 9 with *k* fixed now, or drop the bar to a band with a stated
rationale, or replace the three tracers with artists whose only claim on the record is common
knowledge. Any of these must be committed before the values are read.

## C — definition gaps that would bite the future gradient measurement

### `C1` — the percentile denominator is not the population being ranked

Ranks run over the 74,151 non-null artists; the divisor is stated as the 74,193-artist frame.
So max `fame_lb_pctl` = **0.999434**, not 1.0, and the whole scale is compressed by 0.057%.
Numerically trivial, but "top 1%" then contains 700 artists rather than 742, and every future
band criterion inherits the offset silently. **Fix:** one sentence stating ranks are over
non-nulls and the divisor is 74,193 deliberately (or change it to 74,151).

### `C2` — the out-of-frame mapping rule is under-specified

"Artists outside the frame receive the percentile their raw value would occupy in it" is
ambiguous between |{f < v}|/N and the average-rank form, and is undefined for v above the
frame max (455,551). Two implementations will differ, against the document's claim of
byte-reproducibility. **Fix:** write the formula —
`pctl(v) = (|{f < v}| + (|{f = v}| + 1)/2) / 74,193`, with `pctl(v > max) = pctl(max)`.

### `C3` — "lower half" is not a defined artist set

`vals[half-1] = 1,334` and `vals[half] = 1,335`, and 14 artists are tied at the boundary
value, so which of them fall inside the lower half depends on sort stability — against the
same byte-reproducibility claim. Impact on both bars is negligible here; the definition is
still owed. **Fix:** define the lower half as `{fame_lb_pctl < 0.5}`.

### `C4` — 20.3% of the union sits outside every criterion except `FAM-1`

18,874 ALG-B-only MBIDs (verified against both artifacts) are outside the `fame_lb_pctl`
frame, and `FAM-2`'s resolution is measured only on the adopted frame. That the two
populations differ materially in fame is measurable today from the adopted side alone: median
`fame_lb_raw` is **2,501** for adopted artists also in ALG-B versus **409** for adopted
artists not in ALG-B — 6.1×, between two subsets of one graph. The ALG-B-only side is
**unmeasured** (no LB data on disk for it). **Fix:** report `FAM-2`'s statistics on the
ALG-B-only remainder as well, exactly as `FAM-1` already splits coverage.

### `C5` — the frame choice forecloses a downstream confound without naming it

Mapping candidate-only artists into the adopted frame is the right ruler decision and the
Track B precedent supports it. But it means an ALG-B-built arm's interior percentiles will
differ from an adopted-built arm's **partly because the populations differ**, not because the
arm descends. This document settles the frame; the cap re-evaluation inherits an uncontrolled
variable. **Fix:** one sentence naming it as owed to the cap re-evaluation's factor table.

## D — what the validation cannot see, beyond `§4`'s existing list

`§4` already disclaims coherence, validity and absolute obscurity. These are additional.

### `D1` — vintage bias: `total_user_count` is cumulative-lifetime

An artist active since 2010 accumulates distinct listeners a 2023 artist cannot at equal
current popularity. A future gradient finding "deeper bypasses reach less famous artists"
cannot distinguish *less famous* from *newer*. Nothing in `FAM-1`–`FAM-5` touches this.
**Fix:** carry it in `§2` beside the population blind spot.

### `D2` — the adopted object is a snapshot, and `§0.2` bars cross-*currency* comparison but not cross-*snapshot*

Counts only grow. A re-fetch for a later experiment is a different instrument on a different
frame, and comparing a later gradient to this one would be the same error `§0.2` was written
to prevent, one level down. **Fix:** state that the adopted ruler is *this snapshot plus its
sha256*, and that any re-fetch owes its own `FAM-5` and its own re-read decision.

### `D3` — the percentile scale's sensitivity is non-uniform, and is lowest where production currently routes

Measured: a 10× fame drop buys **+0.44** percentile points starting from the frame median
(3,000 → 300 listeners) but only **+0.14** starting near the top (100,000 → 10,000) — a 3.2×
difference in the currency the gradient will be read in. `FPC-9` puts production's routed
interiors at in-graph popularity percentile 0.982–0.986, i.e. at the top.

**This last step is an inference, not a measurement** — `FPC-9`'s percentiles are in-graph
popularity, a different currency, and I did not join `fame_lb` to the routed interiors. The
one-line measurement that would settle it: join this snapshot to the committed Track 3
routed-interior MBIDs in `builder/analysis/2026-07-24-track2-arm-scorer/paths.json` and report
the `fame_lb_pctl` distribution by depth. It needs no fetch and no rebuild. I have not run it
because it is outside the six questions I was asked.

### `D4` — three of the five criteria are answerable today from data already on disk

The retained 2026-07-30 snapshot covers the whole adopted frame, and `FAM-2`, `FAM-3` and
`FAM-4` read only that frame. **I computed `FAM-2`'s two statistics in this critique** (0.294%
and 1,334 distinct — both pass as written) at the caller's direction. `FAM-1` and `FAM-5` are
genuinely open, since both need the union fetch.

This invalidates nothing: the bars are committed and the git timestamp stands. But the
document presents five criteria as equally unknown, and an amendment relaxing one of the three
foreseeable bars after a first look would be indistinguishable from one made in ignorance.
**Fix:** append an amendment recording which criteria were foreseeable from the retained
snapshot and that `FAM-2`'s adopted-frame values were computed in this design critique.

### `D5` — what currently works only because of the property this change removes

The incumbent Wikipedia ruler has a **floor**: unresolvable artists get a value, and the
project learned to read that value (`A11` adopted it, `A12` had to strip `C6` from gating
because of it, `A18` found the blank-name confound in it). The floor's one virtue is that an
out-of-depth reading is *in the data*, in-band, and lands in every aggregate.

Under the new ruler there is no floor: `§1` makes nulls visible and excludes them from paired
reads. So an artist the instrument cannot see becomes a **hole in the denominator** rather
than a low value. Measured: 42 nulls and **zero zeros** on the adopted frame, so the effect is
negligible there. But `FAM-1`'s bar of 99.0% permits up to **931 nulls across the union**, and
the 18,874 ALG-B-only artists are unmeasured. An arm that reaches more null artists then has a
*smaller* denominator, not a worse score — the failure direction that flatters the arm, which
is the direction `BYP-13` warns about for exactly this class of instrument.

**Fix:** fix the null rule for **aggregate** reads here, not in the downstream document —
`§4` already invokes `REQ-Q1`'s all-interiors-and-matched-only reporting; make explicit that
nulls are the axis that split reports on, and that a null count is reported per depth.

---

## Weakest link in this critique

`A3`'s power table and `A4`'s blast radii assume the hand-read Spotify figures are the truth
and the ruler is the thing with error. If instead a hand read is wrong (`A5`), the same
arithmetic runs in reverse and `FAM-4` fails for a reason that has nothing to do with the
ruler — which is why `A5` is ranked as high as it is. I would defend `A1`, `B1`, `C1`–`C4`
and the frame arithmetic cheaply: they are arithmetic over one snapshot and two artifacts. I
would abandon `D3`'s final clause on one contrary measurement, since its last step crosses a
currency boundary I did not measure.

## Stability note

Every figure here comes from **one** snapshot on **one** frame. `FAM-5`'s stress table is a
simulation over that single snapshot, not a comparison of two real readings — it bounds what
the ρ ≥ 0.99 bar *can* detect, not what the instrument *will* do. The `FAM-4` power table is
20,000 Monte Carlo trials at a fixed seed on a 15-artist table; its shape is stable but its
absolute pass probabilities move with the noise model, which is assumed, not measured.
