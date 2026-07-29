# DD-P3 — `ml-graph-analyst` protocol review of the Track 3 pre-registration

**Role: REVIEW ARTIFACT for DD-P3 (prereg §4).** Derivation only, per the agent's remit:
arithmetic, instrument correctness, and whether stated conclusions follow from stated
measurements. It contains **no recommendation about adoption, about what the owner will
prefer, or about which option to take** — those are outside the remit and are not
addressed here even where a finding obviously bears on one.

Documents under review:
- `docs/superpowers/specs/2026-07-28-track3-depth-descent-preregistration.md`
- `docs/superpowers/2026-07-28-track3-depth-descent-execution-log.md`
- `dd_p1_headroom.py`, `draw_pairs.py`, `draw_pairs_v2.py` and their outputs, in this
  directory.

Artifact: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 verified
`4cb84ef9…b061dc8`. Measured off it: **N = 74,193**, 898,006 directed CSR entries
(**E = 449,003** undirected), degree min 1 / median 9 / mean 12.10 / p99 44 / max 50;
66,773 nodes (90.00 %) at `pctl < 0.90`.

Every figure below was produced by `dd_p3_review_probes.py` in this directory, or by
the inline probes quoted with each finding. All probes are read-only.

---

## DD-P3-1 — DD-A4 and DD-A5 carry no information at any scored depth. REFUTED (§2)

**Claim checked.** §2's factor table gives DD-A4 (`w=0.03`, floor **off**) the baseline
DD-A2 and the reading "is the floor a material brake on the device", and DD-A5 the same
at `w=0.10` against DD-A3.

**Derivation.** The raw floor is `floor_val = max(0, min(pop_raw[s], pop_raw[t]) − 0.15·k)`
(`mirror.py::_relaxed_floor`, `floor_relax_known = 0.15` from `ApiConfig`). `pop_raw`
is measured on the artifact to lie in **[0.000000, 1.000000]**, so `0.15·7 = 1.05`
exceeds the largest possible base and **the floor term is identically zero for k ≥ 7 on
any pair whatsoever**. On the *actual re-drawn set* it dies far earlier — measured base
and last live depth per pair:

| pair (scored set) | floor base | floor alive for k ≤ |
|---|---|---|
| The Mills Brothers → Tracey Chattaway | 0.4181 | 2 |
| Daniel Avery → Rita Marley | 0.3506 | 2 |
| Patti Smith → Daniel Herskedal | 0.3250 | 2 |
| Jenny Owen Youngs → 洲崎綾 | 0.3656 | 2 |
| Tails → Fingers Inc. | 0.3292 | 2 |
| Mikey Murka → Disiz | 0.3116 | 2 |
| 钟茌 → The Koolaid Electric Company | 0.3081 | 2 |
| Openzone Bar → Gjallarhorn | 0.3447 | 2 |
| Bluetech → L‐Vis 1990 | 0.4570 | 3 |
| Emancipator → Vanbot | 0.3164 | 2 |
| Engine-EarZ Experiment → Dusk + Blackdown | 0.3293 | 2 |
| Shirley Collins → D | 0.3803 | 2 |
| *(unscored anchors)* Miles Davis → Daft Punk / Metallica → Taylor Swift | 0.6726 / 0.7199 | 4 / 4 |
| *(unscored anchors)* Radiohead → The Beatles / Muse → Coldplay | 0.9982 / 0.9313 | 6 / 6 |

Consequently, on the scored set:

- **DD-C1** scores at d ∈ {10, 15, 20}. At those depths `floor_val = 0` for every pair,
  so DD-A4's cost function is **bit-identical to DD-A2's** and DD-A5's to DD-A3's. The
  contrast DD-A4-vs-DD-A2 is *guaranteed* to be exactly zero; it is not a null result,
  it is an identity.
- **DD-C2** reads d5 and d20 — floor already dead at both (k ≥ 3 on 11/12 pairs, k ≥ 4
  on the twelfth).
- **DD-C4 / DD-C5** read d ≥ 10 — same.
- The floor axis can only produce a difference at d ∈ {0, 1, 2} (plus d3 for one
  held-out pair), and **no criterion in §5 reads those depths**.

**Verdict: REFUTED.** Two of six arms — a third of the run — cannot move any scored
criterion, by arithmetic rather than by outcome. §2's reading for DD-A4/DD-A5 ("is the
floor a material brake on the device") is not answerable by the design as written; the
depths where it *is* answerable are unscored. This is the mirror image of Track 2's
inert-FL-arms problem that amendment A2 was written to fix, and the same remedy shape
exists (score a depth where the term is alive, or relax the floor more slowly), but
choosing among remedies is the caller's call, not mine.

**What would falsify this finding:** a `floor_relax_known` other than 0.15, a `pop_raw`
range wider than [0,1], or a criterion added at d ≤ 3. None of those hold today.

---

## DD-P3-2 — DD-G2 as written cannot hold for DD-A4/DD-A5. Measured, not inferred

**Claim checked.** §1: "At k = 0 the term is exactly zero, so the first path is
production's **by construction**." §3: "**DD-G2** — every arm's d0 path byte-identical
to P's on every pair." §5: "**DD-C3 (gate…)** DD-G2 holds."

**Derivation, part 1 — the k = 0 claim itself is sound for the ramp arms.**
`w_known_ramp_pctl · k · pop_pctl(v)` with `k = 0` evaluates to exactly `0.0` in IEEE-754
for any finite `w` and any finite non-negative `pctl`. Every partial sum of the cost
expression is strictly positive (`w_hop = 0.02` is added unconditionally and every other
term is non-negative), so `x + 0.0 == x` bit-exactly regardless of where the new term is
inserted in `mirror.py`'s pre-registered term order. **CONFIRMED for DD-A1, DD-A2,
DD-A3.** (`mirror.py`'s own docstring rule 2 — "optional terms are added only when
active, never as `+ 0.0`" — is still worth honouring in DD-P4 for the same reason it was
written, but it is not load-bearing for this particular term.)

**Derivation, part 2 — the claim does not extend to "every arm".** DD-A4 and DD-A5 turn
off a *second* knob, `w_floor`, which is at its **strongest** at k = 0 (no relaxation
applied). Measured directly, production vs production-with-`w_floor=0`, d0, on all 12
scored pairs plus the 4 unscored anchors:

```
[D] d0 identical in 15/16 pairs; differs in 1
    DIFFERS  Miles Davis -> Daft Punk: P 7 hops, floor-off 6 hops
```

**Verdict: §1's k = 0 claim CONFIRMED for the three ramp arms; DD-G2's scope
("every arm") REFUTED.** DD-A4 and DD-A5 will fail DD-G2 on Miles Davis → Daft Punk, and
§3 says gate failure voids the run. The sharp edge: the all-famous anchors are retained
in `pairs_v2.json` **specifically** to be walked for DD-G2, and the single pair where
DD-G2 breaks is one of them.

Note the correct d0 reference for DD-A4/DD-A5 is a floor-off, zero-ramp arm (Track 2's
`A0` is exactly that configuration). The Track 3 arm list contains no such arm.

---

## DD-P3-3 — the device is 70–96 % a path-length penalty, and on this pair set the obscure route *is* the short route

**Claim checked.** §1: "this device is the first term that **rewards descent itself**."

**Derivation.** The toll on a path is `w · k · Σ_{v ∈ interior} pctl(v)`. That sum is
`(number of interiors) × (mean interior pctl)`, so the term prices **length and
percentile jointly and inseparably**. Decomposing the toll differential between P's
delivered path and the all-obscure BFS route, at k = 10, over the 8 analysis pairs
(`n` = interior count, `S` = Σpctl):

| pair | n_P | S_P | n_obs | S_obs | ΔS | length share | descent share |
|---|---|---|---|---|---|---|---|
| The Mills Brothers → Tracey Chattaway | 12 | 11.91 | 6 | 4.54 | 7.37 | 80.8 % | 19.2 % |
| Daniel Avery → Rita Marley | 13 | 12.44 | 6 | 4.51 | 7.93 | 84.5 % | 15.5 % |
| Patti Smith → Daniel Herskedal | 10 | 9.62 | 7 | 5.65 | 3.97 | 72.7 % | 27.3 % |
| Jenny Owen Youngs → 洲崎綾 | 17 | 16.34 | 8 | 5.43 | 10.91 | 79.3 % | 20.7 % |
| Tails → Fingers Inc. | 16 | 15.08 | 6 | 3.40 | 11.68 | 80.7 % | 19.3 % |
| Mikey Murka → Disiz | 14 | 13.23 | 4 | 3.40 | 9.83 | 96.1 % | 3.9 % |
| 钟茌 → The Koolaid Electric Company | 18 | 17.37 | 6 | 3.50 | 13.87 | 83.5 % | 16.5 % |
| Openzone Bar → Gjallarhorn | 10 | 9.44 | 5 | 2.66 | 6.78 | 69.6 % | 30.4 % |

(length share = `(n_P − n_obs) · mean_pctl_P / ΔS`; descent share =
`n_obs · (mean_pctl_P − mean_pctl_obs) / ΔS`. They sum to 1 by construction.)

**Median length share 80.7 %.** The graph then removes any hope of separating the two
post hoc: the unweighted shortest path and the all-obscure path are nearly the same
route on this pair set.

| pair | P's d0 hops | unweighted min hops | all-obscure hops |
|---|---|---|---|
| The Mills Brothers → Tracey Chattaway | 10 | 6 | 7 |
| Daniel Avery → Rita Marley | 11 | 6 | 7 |
| Patti Smith → Daniel Herskedal | 10 | 6 | 8 |
| Jenny Owen Youngs → 洲崎綾 | 17 | 8 | 9 |
| Tails → Fingers Inc. | 10 | 7 | **7** |
| Mikey Murka → Disiz | 11 | 5 | **5** |
| 钟茌 → The Koolaid Electric Company | 14 | 7 | **7** |
| Openzone Bar → Gjallarhorn | 12 | 6 | **6** |
| Bluetech → L‐Vis 1990 | 7 | 5 | 6 |
| Emancipator → Vanbot | 7 | 4 | 6 |
| Engine-EarZ Experiment → Dusk + Blackdown | 5 | 5 | **5** |
| Shirley Collins → D | 17 | 7 | **7** |

On **6 of 12** pairs the unweighted shortest path is *already* entirely sub-decile.
Production takes a 10–17 hop detour through the top decile where a 5–7 hop sub-decile
route exists — measured production interior `pctl` runs 0.94–0.99 (see DD-P3-8).

**Verdict: the §1 characterisation is INCOMPLETE, not wrong.** The term does reward
descent; it also, and on these pairs predominantly, rewards *fewer stops*. Because the
short route and the obscure route coincide here, **no measurement in §5 can attribute a
DD-C1 or DD-C2 movement to descent rather than to shortening.** Track 2 had an
instrument for exactly this — `score.py`'s **C4 payload guard**, `mean interiors ≥ P's
mean − 1`, written against WGLL value 2 ("fewer-but-obscurer is not a win"). **Track 3's
§5 has no equivalent.** DD-C5 counts *distinct sub-decile interiors*, which rises when
paths get more obscure and does not fall when they get shorter, so it does not cover this.

Falsifiable by: a pair set where the shortest route runs through the top decile (the
all-famous anchors are such pairs — and they are unscored).

---

## DD-P3-4 — DD-P1 certifies headroom in percentile currency; DD-C1/DD-C2 score in fame currency. UNDETERMINED

**Claim checked.** DD-P1 is the prerequisite that makes DD-R2's null "a mechanism-strength
statement rather than an artefact of a pair set with nowhere to go".

**Derivation.** DD-P1's test is `pctl < 0.90` — `MirrorContext.pctl`, a percentile of
`pop_raw`, i.e. score-weighted in-degree. DD-C1 and DD-C2 are scored in **F =
log10(1+pageviews)**, the A11 instrument. CLAUDE.md and §2.11 of the Phase 1 log record
that these are different quantities and that treating one as the other has already
produced wrong conclusions here. So "an all-sub-decile route exists" does **not** entail
"a route exists whose interiors are ≥ 1.0 log10 F below production's" — which is what
DD-C1 requires.

I tried to bound the gap by joining Track 2's committed `fame.json` against the
artifact's `pctl`. Only **239** mbids join, and they are almost all top-decile
(n = 202 at pctl ≥ 0.99), giving median F of 5.977 / 6.071 / 5.984 across
[0.94,0.96) / [0.98,0.99) / [0.99,1.0]. A linear fit over that range is meaningless for
extrapolation below 0.90 and I am not quoting it as a conversion.

**Verdict: UNDETERMINED, and it is the cheapest decisive gap remaining before any arm
runs.** What would settle it: the all-obscure BFS route is already computed for all 12
pairs at all 9 depths (`headroom_v2.json`); resolving F for those routes' interiors with
the committed `fame.py` and comparing their median F against P's delivered interiors
gives **headroom expressed in DD-C1's own currency**. If that difference is materially
below 1.0 log10, DD-C1 is unreachable at *any* `w` — a result available before DD-P4 and
for the cost of one fame fetch. If it is above 1.0, DD-R2's null becomes as interpretable
as §6 claims.

---

## DD-P3-5 — the amendment's selection effect: direction upward, ≤ ~9.5 % relative, with a composition shift. The bound is weak against user journeys

This is the item the caller most wanted checked, so the answer is given in three parts.

**(a) Does conditioning bias the measured effect upward? Yes, and the intensity is
small.** Monte-Carlo over 300 unconditioned draws per group (seed 11071, same pools and
band edges as `draw_pairs_v2.py`), acceptance = "an all-obscure guard-compliant route
exists":

| group | acceptance | accepted src pctl (mean / median) | rejected src pctl | accepted src degree / sub-decile degree (median) | rejected src degree / sub-decile degree |
|---|---|---|---|---|---|
| famous → mid | **250 / 300 = 83.3 %** | 0.9455 / 0.9441 | 0.9675 / 0.9731 | 28 / 8 | 18 / 0 |
| mid → mid | **298 / 300 = 99.3 %** | 0.6987 / 0.7001 | 0.6848 / 0.6848 | 16 / 14 | 7 / 0 |

The scored set is 6 famous→mid + 6 mid→mid, so the pair-weighted acceptance is
`(0.833 + 0.993)/2 = 0.913`. **Bound:** if an excluded pair's true device effect lies
between zero and the included pairs' effect — the natural assumption, since an excluded
pair by definition has no fully-obscure route to descend into — then the conditioned
DD-C1 estimate overstates the unconditioned population mean by at most
`1 / 0.913 = 1.095`, i.e. **≤ 9.5 % relative**. Against DD-C1's −1.0 threshold that is
about 0.09 log10, well inside the criterion's margin. The bound breaks only if excluded
pairs' effect has the *opposite* sign (the device making them *more* famous by
shortening them into hubs) — which DD-P3-3 makes a live possibility, so it is not
free.

**Stability:** one slice, n = 300 per group; binomial se on 83.3 % is 2.2 pp. The
famous→mid figure has not been reproduced on a second slice.

**(b) Composition of the famous→mid group. Yes, it shifts, and in the direction you
suspected.** Over the full famous pool (degree > 1, n = 7,403), **87.9 %** have at least
one sub-decile edge, and usability falls steeply with percentile:

| famous sub-band | usable (≥1 sub-decile edge) | n |
|---|---|---|
| [0.90, 0.93) | 96.8 % | 2,219 |
| [0.93, 0.96) | 93.9 % | 2,219 |
| [0.96, 0.99) | 85.3 % | 2,223 |
| [0.99, 1.00] | **51.3 %** | 742 |

Accepted famous sources average pctl 0.9466 and degree 26.4; rejected average pctl 0.9752
and degree 26.8 — so the shift is **toward lower percentile, not toward lower degree**.
(Degree is essentially unchanged; the discriminating variable is sub-decile degree, median
8 vs 0. This is a case where degree and popularity had to be measured separately and the
answer differs between them.) The six drawn famous endpoints sit at pctl
{0.9102, 0.9404, 0.9735, 0.9743, 0.9880, 0.9966} with sub-decile degrees
{12, 3, 2, 18, 2, 1} of total degrees {32, 12, 7, 27, 34, 42} — so the band is *not*
collapsed to the bottom of the decile, as the log says, but three of the six reach their
obscure route through **1–3 edges**, i.e. a single bottleneck.

**Comparability to Track 2's calibration.** The DD-C1 threshold (−1.0 log10, from the
1.093 band gap) is stated in *absolute fame units*, and a fame unit is pair-set
independent, so reusing the threshold is defensible on its own terms. What is **not**
transferable is the prior probability of reaching it: Track 2's pair set was all-famous,
Track 3's scored set contains no all-famous pair and its famous endpoints are drawn from
a usable subpopulation. The pre-registration's scope guard already says no Track 3 figure
is comparable to Track 2's; DD-P3-8 finds one place where the document does not honour
its own guard.

**(c) The bound in (a) is against a uniform draw from the bands, not against user
journeys.** The scored set additionally excludes, by design and by construction, the
entire all-famous slice and effectively the ≥0.99 band (48.7 % unusable). Users pick
artists they know. Relative to the distribution of journeys the app will actually be
asked for, the exclusion is far larger than 9 % and its magnitude is **unmeasured** —
there is no request log to measure it against.

---

## DD-P3-6 — DD-D3's unsatisfiability arithmetic. CONFIRMED exactly

Independently recomputed from the artifact:

```
both-famous pairs among Track 2 ANALYSIS_PAIRS: 6
  Miles Davis  pctl 0.9936 deg 34 subdeg 0  -> Daft Punk    pctl 0.9895 deg 50 subdeg 3   obscure route: NONE
  Metallica    pctl 0.9992 deg 48 subdeg 0  -> Taylor Swift pctl 0.9943 deg 46 subdeg 0   obscure route: NONE
  Radiohead    pctl 1.0000 deg 50 subdeg 0  -> The Beatles  pctl 1.0000 deg 50 subdeg 0   obscure route: NONE
  Muse         pctl 0.9999 deg 50 subdeg 0  -> Coldplay     pctl 1.0000 deg 50 subdeg 0   obscure route: NONE
  Madonna      pctl 0.9986 deg 29 subdeg 0  -> Bob Dylan    pctl 0.9991 deg 43 subdeg 0   obscure route: NONE
  Pink Floyd   pctl 0.9999 deg 50 subdeg 0  -> Aphex Twin   pctl 0.9999 deg 40 subdeg 0   obscure route: NONE
candidates with NO all-obscure route at all: 6/6
```

Every per-endpoint count in `draw_pairs_v2.py`'s docstring reproduces exactly, including
"Daft Punk at 3 but its partner at 0". Any 4 of the 6 contribute 4 × 3 = **12** lacking
C1-window cells out of 12 pairs × 3 depths = **36**, i.e. **33.33 % against a 30 %
trigger**. The trigger therefore fires for every pair set the pre-registration permits.

Two strengthenings the log does not state, both of which make the conclusion more robust
rather than less:
1. Infeasible cells are excluded from the trigger's denominator (`dd_p1_headroom.py`
   counts only `state == "scored"`), so any infeasibility would *raise* the fraction
   above 33.3 %, never lower it.
2. The 6 candidates fail at **unlimited** hop budget, not merely at +2 — so the slack
   constant is irrelevant to the unsatisfiability, exactly as DD-F2 reports.

**Verdict: CONFIRMED, both the arithmetic and the edge counts.** DD-D3's reading — that
a trigger which cannot be cleared cannot discriminate, and that DD-R3's stated conclusion
is contradicted by the measurement that fires it — follows from the measurements.

---

## DD-P3-7 — `dd_p1_headroom.py` measures what §4 specifies. CONFIRMED on all four sub-questions

A clean derivation, reported as a result.

1. **Induced-subgraph construction.** `below = pctl < 0.90` (strict, matching the
   half-open band edges in DD-P2 and the "below pctl 0.90" wording of DD-P1); endpoints
   exempted by `allowed[src] = allowed[dst] = True`; the cell's exclusions applied
   *after* the endpoint exemption, which cannot conflict because the victim rule draws
   only from `path[1:-1]`. Correct.
2. **Direct-edge mask.** `if u == src and v == dst: continue` forbids only the 1-hop
   path, so every returned path has ≥ 1 interior and is guard-compliant. Masking only the
   `src → dst` direction is sound for the same reason `mirror.py` gives: a shortest path
   to `dst` cannot traverse the reverse direction. Correct. The mask is applied
   unconditionally rather than only when the unconstrained result is 2 nodes, which is
   *stricter* than guard G and therefore safe for an existence test.
3. **BFS hop-count vs P's cost-optimal delivered path.** DD-P1 asks an existence question
   under a hop bound. `min hops ≤ p_hops + 2` ⟺ `∃ a sub-decile path with hops ≤
   p_hops + 2`, so BFS-minimum is exactly the right statistic; no cost comparison is
   owed. `p_hops = len(p) − 1` is P's *delivered* length as specified. Correct.
4. **Exclusion reconstruction vs what `run_arms.walk` actually did.** The reconstruction
   is the same expression as the walker's (`min(interior, key=lambda v: (-pop[v], v))`
   over `paths[d][1:-1]`, with the same `pop` dtype), and `victims[:d]` is by
   construction the walker's `excludes` at iteration `d`. The list-length edge cases are
   safe: `walk` produces a contiguous prefix of usable paths then pads with `None`, so
   whenever `paths[d]` is scoreable, `len(victims) ≥ d`. I verified this at **runtime**
   rather than by reading, by spying on the actual `excludes` list passed into
   `find_path_mirror` on 4 pairs across all 21 depths:

   ```
   victim-reconstruction == walker's actual exclusion sequence on 4 pairs: True
   n_excluded by depth: [(0,0),(1,1),(2,2),(3,3),(5,5),(7,7),(10,10),(15,15),(20,20)]
   ```

   So the exclusions were both correct and non-empty — worth confirming, because
   `obscure_hops` is constant across all nine depths for all twelve v2 pairs, which on its
   own is the signature a silently-unapplied exclusion set would also produce.

**One nuance the log states and that I confirm.** Conditioning the v2 draw at **d0** is
the *conservative* choice, not a convenient one: `p_hops` at d0 is the minimum or
near-minimum across the nine snapshots for every pair (production's paths lengthen with
depth — see DD-P3-8), so d0 is the tightest `p_hops + 2` bound in the walk. Acceptance at
d0 therefore implies acceptance at deeper depths unless the exclusions bite, and they do
not, because the victim is the *most popular* interior and production's interiors are
already almost entirely outside the sub-decile subgraph.

**The log's "weakest link" paragraph is right that headroom is not necessary. It does not
say whether headroom is sufficient — and DD-P3-9 measures that it effectively is, on this
pair set.**

---

## DD-P3-8 — DD-C2's threshold: the hop-count difference biases it, and 0.164 is quoted across pair sets

**Claim checked.** DD-C2: "Median interior F drop d5 → d20 ≥ 0.5 log10 … Production's own
figure is owned by `scores.json` (C3 = 0.164)."

**(a) The statistic is length-weighted.** Track 2's C3, which DD-C2 reuses, is
`score.py::pooled` — *all* interiors from *all* analysis pairs at one depth concatenated
into a single list, then one median. Pairs enter the pool in proportion to their path
length. Any change in the length *distribution* between d5 and d20 reweights the pairs.

**(b) The fame profile along a path is not flat, so length changes the median
mechanically.** Mean interior `pctl` by hops from the *nearest* endpoint, pooled over the
8 analysis pairs on a production walk:

| hops from nearest endpoint | 1 | 2 | 3 | 4 | 5 | 6+ |
|---|---|---|---|---|---|---|
| d5 | 0.898 | 0.935 | 0.960 | 0.967 | 0.981 | 0.984 |
| d20 | 0.895 | 0.932 | 0.959 | 0.965 | 0.978 | 0.984 |

Production climbs into the top decile and back down. A path has ~2 endpoint-adjacent
interiors regardless of its length, so the share of low-percentile interiors is ~2/m and
**falls with length**. Simulating pure shortening — keeping P's own d20 paths and
dropping only the central interiors, i.e. zero genuine descent:

| paths truncated to | pooled interiors | median pctl (d20) |
|---|---|---|
| full (median 15.5 interiors) | 117 | 0.9781 |
| 8 | 64 | 0.9628 |
| 6 | 48 | 0.9516 |
| 4 | 32 | 0.9139 |

**Shortening alone moves the pooled median by 0.026–0.064 percentile points downward
with no descent whatsoever.** Direction: it **inflates** a measured d5 → d20 drop for any
arm that shortens paths with depth — which is precisely what a per-interior toll growing
in `k` does (DD-P3-3).

**(c) Production itself lengthens with depth**, so the baseline runs the other way. Interior
count on a P walk over the 8 analysis pairs: d0 median 10.0 → d5 11.5 → d10 13.5 → **d20
15.5** (means 10.88 → 12.12 → 13.75 → 14.62).

**(d) The 0.164 baseline is a cross-pair-set quotation.** `scores.json` confirms
P's `C3.drop_d5_to_d20 = 0.1637637951265738`, but it was computed on **Track 2's
all-famous pair set**, and §Scope of this very document says "no figure from this track
is comparable to Track 2's — the pair set differs by design, and any cross-track quotation
must say so". DD-C2's plain sentence ("today's app manages about a third of that") is such
a quotation and does not say so. For scale: production's *percentile* gradient on the
Track 3 scored set is 0.9803 (d5) → 0.9781 (d20), a drop of **0.0022** — essentially flat,
consistent with ASC-5's flat bypass ladder. Its gradient in F units on this pair set is
**unmeasured**.

Also worth having on the record while assessing a 0.5 threshold: in Track 2, **no arm
exceeded P's 0.164** — the eleven scored arms ran 0.021 to 0.090, i.e. every arm that
dove had a *flatter* depth gradient than production.

**Verdict: the mechanical bias is CONFIRMED in direction and quantified in percentile
units; its size in log10 F is UNDETERMINED** (same currency gap as DD-P3-4). What would
settle it: report mean interior count per arm alongside DD-C2 (Track 2's C4 does exactly
this and is absent from §5), and recompute DD-C2 on a length-matched interior subsample.
Both are offline and free once the walk exists.

---

## DD-P3-9 — the dose ladder does span the magnitude at which the path provably changes. CONFIRMED

Not asked, but it falls directly out of the DD-P3-3 arithmetic and it is what makes
DD-R2's "magnitude escalation is barred" checkable rather than asserted, so it is
reported here.

For each analysis pair I computed the exact production-cost of P's delivered path and of
the all-obscure BFS route under that cell's exclusions, then solved for `w*`, the smallest
`w_known_ramp_pctl` at which the obscure route's total cost undercuts P's:

| pair | w* at k=10 | w* at k=20 |
|---|---|---|
| The Mills Brothers → Tracey Chattaway | 0.1035 | 0.0596 |
| Daniel Avery → Rita Marley | 0.0607 | 0.0202 |
| Patti Smith → Daniel Herskedal | 0.1416 | 0.0398 |
| Jenny Owen Youngs → 洲崎綾 | 0.0535 | 0.0289 |
| Tails → Fingers Inc. | 0.0296 | 0.0132 |
| Mikey Murka → Disiz | 0.0131 | 0.0089 |
| 钟茌 → The Koolaid Electric Company | 0.0337 | 0.0174 |
| Openzone Bar → Gjallarhorn | 0.0555 | 0.0151 |

`w*` is an **upper bound** on the `w` needed for the delivered path to change: at
`w ≥ w*`, P's path is provably no longer optimal, and since P's path is base-cost-optimal,
the winner must satisfy `Σpctl(winner) ≤ Σpctl(P)` with strict inequality whenever the
winner's base cost is higher. So:

- **DD-A3 (`w = 0.10`)** flips 6/8 pairs at k = 10 and **8/8** at k = 20.
- **DD-A2 (`w = 0.03`)** flips 2/8 at k = 10 and 5/8 at k = 20.
- **DD-A1 (`w = 0.01`)** flips 0/8 at k = 10 and 1/8 at k = 20.

The ladder therefore brackets the crossover rather than sitting entirely below or above
it. A null across it would be a mechanism statement about *what the router does with the
freedom*, not about the toll being too small — which is the claim §6's DD-R2 makes and
which was, before this, unverified. (Sanity check on my cost re-implementation: every
`ΔCost` came out positive, 1.23–7.62, as it must if P's delivered path is base-optimal.)

---

## DD-P3-10 — §0's held-constant enumeration is incomplete, and guard G's *activation* is device-dependent

**Claim checked.** §0 enumerates held-constant terms "per the CLAUDE.md rule, because the
confound that nearly broke Track 2 was a term inert in the baseline *for a reason the
intervention removes*."

**Omissions from the table** (all three are, on inspection, genuinely constant — the
finding is the incompleteness, not a confound):
- `w_avoid = 1.0` / `avoid_penalty` / `avoid_decay` / `avoid_radius`. Inert because the
  walk is all-`known`, so `_avoidance_map` receives an empty list. The device introduces
  no `dislike`, so the reason for inertness survives it.
- `toll_s` / `toll_hops` (Track 2 / 2F's ceiling toll). Inert because both are `None`.
  The device does not set them.
- `floor_relax_known = 0.15` is only implicit in the floor row, and it is the single
  constant that determines DD-P3-1.

**The one term with the Track 2 shape: guard G.** §0 lists guard G as "ON everywhere
incl. P", i.e. constant as a *setting*. Its **activation** is not constant under this
intervention. `mirror.py` runs the masked second Dijkstra only when the unconstrained
optimum is the direct edge. The device tolls interiors and **exempts the target**, so the
2-node direct path is the unique path whose toll is exactly zero at every `k`, while every
alternative's toll grows linearly in `k`. As `w·k` rises, the direct edge becomes optimal
on strictly more pairs than in P, so guard G fires in the arms where it does not fire in
the baseline. That is "inert in the baseline for a reason the intervention removes",
precisely.

It is **not** a scoring confound — guard G is a constraint applied identically to all
arms, and a masked re-run still returns a guard-compliant path. The live risk is
downstream: if an arm's delivered path collapses to a single interior, the next `known`
bypass removes that interior and the walk can go infeasible, at which point A13's uniform
drop removes that cell **from every arm including P**, shrinking the scored set for
everyone. Measured mitigation: no scored pair is adjacent (unweighted min hops 4–8, table
in DD-P3-3), so the direct edge is not available on the scored set; two of the four
unscored anchors (Radiohead → The Beatles, Muse → Coldplay) **are** adjacent, and guard G
is already firing on them in P (their `p_hops` is 2 at nearly every depth in
`headroom.json`). So the hazard is real in mechanism and small in exposure on this
particular pair set — but it is cheap to instrument: count guard-G activations per arm in
DD-P4 and report them beside the arm stats, the way `floor_active` already is.

---

## DD-P3-11 — §2's realised-toll arithmetic. CONFIRMED

`w_hop = 0.02` (`ApiConfig`, cited not restated). Toll at k = 10, pctl = 1 is `10·w`:

| arm | `w` | toll | in `w_hop` | §2 says |
|---|---|---|---|---|
| DD-A1 | 0.01 | 0.10 | 5.0× | 5× ✓ |
| DD-A2 | 0.03 | 0.30 | 15.0× | 15× ✓ |
| DD-A3 | 0.10 | 1.00 | 50.0× | 50× ✓ |

§2's parenthetical for DD-A3 — "at k = 20 the toll (2.0) is commensurate with the whole
sim term (≤ 3.0)" — is also right: `0.10 · 20 · 1 = 2.0`, and `w_sim·(1−sim) ≤ 3.0`.
§1's "at k = 20, pctl ≈ 1, the toll is `20·w`" is right.

Two smaller notes, neither an error:
- DD-R2's −0.3 is described as "a third of the primary effect"; a third of −1.0 is
  −0.333. The document says "≈", so this is a rounding, not a mistake.
- §1 says the toll applies "for every **relaxed** node `v`". In Dijkstra "relaxed" is
  ambiguous between *settled* and *the target of an edge relaxation*. The formula
  `cost(u→v) +=` disambiguates it correctly as an in-edge toll; DD-P4 should implement it
  inside the relaxation loop, and a node-settled implementation would silently price
  nodes that never appear on the returned path.

**Well-posedness of the device as an additive node toll.** Confirmed. The toll is
non-negative (`w > 0`, `k ≥ 0`, `pctl ∈ [0,1]`), so Dijkstra's correctness is preserved.
Folding a node potential into every in-edge is exact for a simple path: each interior pays
exactly once, the source is never a relaxation target on the returned path (its distance
is already 0), and the target's exemption removes a constant that every complete path
would otherwise pay identically. `k` is fixed within a request, so it is a constant
multiplier inside one Dijkstra, not a state variable — this is not a resource-constrained
shortest path and needs no expanded state space. `mirror.py` already carries two
node-keyed terms of the same shape (`floor_pen` and `degree_hub_penalty`, both functions
of `v` alone), so the device is structurally identical to terms already verified
byte-identical against production.

---

## DD-P3-12 — provenance gaps in this directory

Not derivations, but they affect whether these numbers can be re-derived later.

- **DD-F1's band table is correct but its edges are not recorded.** The log's
  "4.5 % → 10.3 % → 20.1 % → 45.1 % → **80.0 %** across pctl bands [0.90,0.95) …
  [0.999,1.0]" reproduces **exactly and uniquely** under edges
  `[0.90, 0.95, 0.98, 0.99, 0.999, 1.0]`. I had to search a grid of six schemes to find
  it; the two neighbouring schemes give 4.5/12.7/36.1/56.4/80.0 and
  4.5/9.5/18.1/45.1/80.0. The ellipsis hides two of the four interior edges.
- **No script in this directory produces that table.** `recon_bands.py` does not compute
  sub-decile degree; `dd_p1_headroom.py` does not either. The figures entered the record
  from an unrecorded probe.
- **This directory has no `README.md`**, which the 2026-07-23 defect-remediation spec §4.2
  requires of an analysis directory whose scripts produce a recorded finding.

---

## Summary of verdicts

| # | item | verdict |
|---|---|---|
| 1 | DD-A4 / DD-A5 answer their §2 reading | **REFUTED** — floor is identically 0 at every scored depth; both arms are identities of DD-A2 / DD-A3 |
| 2 | §1's k = 0 first-path claim | **CONFIRMED** for DD-A1/A2/A3 |
| 2 | DD-G2 "every arm's d0 path byte-identical to P's" | **REFUTED** — fails for DD-A4/A5 on Miles Davis → Daft Punk (measured) |
| 3 | §1's "rewards descent itself" | **INCOMPLETE** — median 80.7 % of the toll differential is path length, and the short route *is* the obscure route on 6/12 pairs; no §5 criterion separates them, and Track 2's C4 payload guard has no Track 3 equivalent |
| 4 | DD-P1's headroom guarantees DD-C1's premise | **UNDETERMINED** — headroom is certified in percentile, DD-C1 scores in fame; settled by one fame fetch over routes already computed |
| 5 | the amendment biases the measured effect upward | **CONFIRMED**, bounded at **≤ 9.5 % relative** against a uniform draw (one slice, n = 300/group); composition shifts toward **lower percentile** famous endpoints, not lower degree; the bound does **not** cover user-requested journeys |
| 6 | DD-D3's 12/36 = 33.3 % and the 6/6 zero-sub-decile claim | **CONFIRMED** exactly, and it holds at unlimited hop budget |
| 7 | `dd_p1_headroom.py` measures §4's DD-P1 | **CONFIRMED** on all four sub-questions, incl. runtime verification of the victim reconstruction |
| 8 | DD-C2's threshold is unaffected by hop-count differences | **REFUTED in direction** (shortening inflates the drop by 0.026–0.064 pctl with zero descent); magnitude in log10 F **UNDETERMINED**; the 0.164 baseline is a cross-pair-set quotation the document's own scope guard forbids unlabelled |
| 9 | the dose ladder brackets the flip magnitude | **CONFIRMED** — w\* ≤ 0.10 on 8/8 pairs at k = 20 |
| 10 | §0's enumeration is complete for this device | **REFUTED** — `w_avoid`, the ceiling-toll knobs and `floor_relax_known` are unlisted (all genuinely constant), and guard G's *activation* has the Track 2 shape |
| 11 | §2's 5× / 15× / 50× and the 2.0-vs-3.0 remark | **CONFIRMED** |
| 12 | DD-F1's band figures | **CONFIRMED** under edges [0.90, 0.95, 0.98, 0.99, 0.999, 1.0]; edges unrecorded, producing script absent, directory has no README |

Nothing in this review is a recommendation about whether to run, amend or stop the track.
