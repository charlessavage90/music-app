# Track 2 pre-registration — `ml-graph-analyst` protocol review

**Role: AUTHORITATIVE for its own measurements; ADVISORY on the protocol.** Written
2026-07-23 by the `ml-graph-analyst` subagent, discharging the review gate in
[`../specs/2026-07-23-defect-remediation-and-cost-retune-design.md`](../specs/2026-07-23-defect-remediation-and-cost-retune-design.md)
§4.6 and prerequisite **P8** of
[`../specs/2026-07-23-track2-preregistration.md`](../specs/2026-07-23-track2-preregistration.md) §7.
Scope is the **protocol only** — the harness does not exist and is a separate review
(P8b). Remit is **derivation, not judgement**: nothing here says whether the experiment
is worth running or what the owner should prefer.

**Figures rule.** No measured figure from
`2026-07-21-scoring-adjudication.md` or `../2026-07-22-phase1-execution-log-and-graph-defect.md`
is restated; those are cited by section. This document **owns** the figures in §2 —
they are new measurements taken here for the first time. Code constants are attributed
to file and line.

**Housekeeping owed by the working session:** register this document in
`docs/README.md`'s map (this engagement may not edit that file).

---

## 0. What was read, and against what

| Input | Identity |
|---|---|
| Artifact measured | `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 asserted `4cb84ef9…b061dc8` before every measurement, matching `2026-07-23-tiebreak-fix-adoption.md` |
| Source read | working tree at branch `phase1-pre-track2-guards`, HEAD `78b28bd`, **with uncommitted G2 rename in flight** (see O5) |
| Documents | the pre-registration; governing spec §4; Phase 1 log §2.8–§2.13 and §3.3–§3.10; repair+retune execution log; `plans/2026-07-23-pre-track2-guards.md` |
| Not run | any sweep arm, any `find_path` call, any network fetch, any rebuild |

---

## 1. Task 1 — independent verification of §0's resolution table

Every claim below was checked **in code**, not taken from a document.

| # | §0 claim | Verdict | Evidence |
|---|---|---|---|
| 1a | `w_floor` is live in the cost at weight 1.0 | **CONFIRMED** | `config.py:36` `w_floor: float = 1.0`; the term appears in the summed cost, `pathfinding.py:122` (working tree) / `:104` (HEAD) |
| 1b | `floor = min(pop_source, pop_target)`, raw currency | **CONFIRMED** | `pathfinding.py:94` (HEAD `:80`) — `min(float(store.pop_raw[source]), float(store.pop_raw[target]))`; `pop_raw` is the APG1 `popularity` array loaded verbatim, `graph_store.py:119` |
| 1c | `floor_relax_*` is the only depth-graduated device in the shipped cost | **CONFIRMED for an all-`known` walk; imprecise in general** | Only `hard` (`pathfinding.py:92`), the floor (`:95`) and `avoid` (`:96`) depend on the exclusion list. `avoidance_map` is populated from `DISLIKE` exclusions only, so under Stage A's all-`known` protocol the claim is exactly true. Under a `dislike` walk the avoidance *field itself* grows with depth — relevant to §1.5's F4 dislike walk. |
| 1d | `w_floor` inert in production **transfers to `graph-t15-tiebreakfix.bin`** | **CANNOT DETERMINE** | Claim 23 (adjudication §5.4) and log §2.12 were measured pre-Track-1. Track 1 restored ~50 score-ranked neighbours to exactly the famous artists that are this sweep's endpoints (log §2.8, adoption record), so the neighbourhoods the floor would have to bind in are the ones that changed. Settling it requires routing paths on the current artifact — I did not take that measurement (see PR-A). **The pre-registration's A0 arm is the correct test; it is not currently scheduled as a gate.** |
| 2 | Nothing in `api/src` computes popularity percentiles | **CONFIRMED** | `rg 'percentile\|quantile\|argsort\|rankdata\|pctl' api/src` returns only `evaluation.py:29,32,315` — all `np.quantile` over `np.diff(store.offsets)`, i.e. **degree**. No popularity ranking exists anywhere in the package. |
| 3 | The `known` "gate" does not exist in shipped code | **CONFIRMED** | `_to_exclusions` (`app.py:23-30`) maps a reason string only; `find_path` puts `KNOWN` nodes in `hard` (`:92`) identically to `DISLIKE`, and the sole `KNOWN`-specific behaviour is `floor_relax_known` (`:46`) feeding the floor term. No pop-drop or similarity admission test exists. The ≥0.10 / ≥0.70 gates live only in `builder/analysis/2026-07-23-popularity-stratification/known_viability.py:28`. |
| 4 | Exclusions are node-based and cannot express "forbid this edge" | **CONFIRMED** | `pathfinding.py:92` builds a node set; the neighbour loop skips on `if v in hard` (`:112`) with no edge identity available. Endpoints are subtracted from the set, so they are never excludable. §4's mask-and-re-run guard is therefore the only available construction. |
| 5 | `clips.py` does first-hit track search with no name verification | **CONFIRMED** | `clips.py:98-107` — Deezer **track** search, `limit: 1`, returns the first row carrying a preview; the row's `artist` object is read only for cover art. A fame harness reusing this would silently mis-attribute. |

**No refutation.** §0's code claims stand as written. The one item it could not have known
is 1d, and it flags that honestly.

**On §0's line numbers:** `pathfinding.py:104` and `:78` are **correct against HEAD**
(`78b28bd`) and are already stale against the working tree, where G2's rename is in
flight. That is G2's own named hazard, not a defect of the pre-registration.

---

## 2. Measurements taken

All four are structural properties of the adopted artifact. No path was routed.
Script inlined in §7; it belongs in `builder/analysis/2026-07-23-track2-protocol-review/`
with a README (spec 2026-07-23 §4.2 convention) — the working session should commit it.

**M1 — the similarity ceiling and the score grid** (MEASUREMENT, verified in code)

| quantity | value |
|---|---|
| edges at score exactly `1.0` | 17,574 of 898,006 (1.957 %) |
| largest non-ceiling score | 0.9999056458473206 |
| `1 −` that | 9.435 × 10⁻⁵ |
| distinct score values in the artifact | 1,445 |
| spacing of the top eight distinct scores | ≈ 9.45 × 10⁻⁵, uniform |

**M2 — jump-term magnitude and geometry under the two currencies** (MEASUREMENT).
Percentile = average-rank over N (prerequisite P6's rule, implemented as specified).
Computed over all 898,006 directed CSR entries.

| edge class | n | mean \|Δpop_raw\| | mean \|Δpctl\| | pctl / raw |
|---|---|---|---|---|
| all edges | 898,006 | 0.07702 | 0.14357 | **1.864** |
| incident on top popularity decile | 259,952 | 0.08712 | 0.08872 | 1.018 |
| — of those, **lateral** (both ≥ p90) | 131,724 | 0.06018 | 0.02301 | **0.382** |
| — of those, **exit** (one < p90) | 128,228 | 0.11480 | 0.15623 | **1.361** |
| — deep exits (other endpoint < p50) | 7,150 | 0.30816 | 0.59952 | 1.945 |

Derived price ratios — what an exit costs *relative to staying in the stratum*:

| | raw currency | percentile currency | change |
|---|---|---|---|
| exit / lateral | 1.908 | **6.790** | **3.56× dearer** |
| deep exit / lateral | 5.121 | **26.058** | **5.09× dearer** |

**M3 — popularity tie structure** (MEASUREMENT)

| quantity | value |
|---|---|
| distinct popularity values | 32,503 over N = 74,193 |
| nodes sharing a value with at least one other | 54,923 (74.03 %) |
| largest tie group | 430 nodes (0.58 % of N), at a low popularity value |
| second largest | 414 nodes at popularity exactly 0.0 |
| **top decile: nodes / distinct values / largest tie group** | **7,420 / 7,186 / 3** |

**M4 — floor saturation depth for the pre-registered pair set** (MEASUREMENT).
`floor_relax_known = 0.15` (`config.py:47`); base floor = min of the two endpoints'
values; `n` = number of `known` bypasses at which the relaxed floor reaches 0.

| pair | base floor, percentile | base floor, raw | n to floor = 0 |
|---|---|---|---|
| Miles Davis → Daft Punk | 0.9895 | 0.6726 | 7 |
| The Shins → Wishbone Ash | 0.8756 | 0.4744 | 6 (raw: 4) |
| Metallica → Taylor Swift | 0.9943 | 0.7199 | 7 |
| Radiohead → The Beatles | 1.0000 | 0.9982 | 7 |
| Muse → Coldplay | 0.9999 | 0.9313 | 7 |
| Madonna → Bob Dylan | 0.9986 | 0.8286 | 7 |
| Pink Floyd → Aphex Twin | 0.9999 | 0.9307 | 7 |
| Arctic Monkeys → Johnny Cash | 0.9998 | 0.9285 | 7 |
| Michael Jackson → Gorillaz | 0.9999 | 0.9396 | 7 |
| System of a Down → R.E.M. | 0.9998 | 0.9280 | 7 |
| The Rolling Stones → Linkin Park | 0.9999 | 0.9403 | 7 |
| Nirvana → CROOVE | 0.8505 | 0.4571 | 6 |

All 12 endpoints resolved by name (duplicate-name rule = highest popularity), which
independently corroborates the execution log's statement that G1 discharged P2.

---

## 3. DEFECTS — the protocol does not measure what it claims

Ranked. Each states the measured fact, then the fix, then confidence and falsifier.

### D1 — T1 is inert by construction under its own prerequisite. **Highest.**

**MEASUREMENT (M1).** P3 instructs: "measure the largest non-ceiling edge score in the
artifact; set `s_max` just above it". On the adopted artifact that score is
0.9999056, one grid step below the ceiling. T1's toll on a ceiling hop is therefore
`w_sim · (1 − s_max) ≈ 3.0 × 9.435e-05 ≈ 2.8 × 10⁻⁴` — **about 1.4 % of `w_hop`**
(`w_sim = 3.0`, `w_hop = 0.02`; `config.py:34,37`). It cannot change a routing decision
on any path of any length.

**INFERENCE.** T1 will return a null indistinguishable from W, and that null is
pre-registered (§1.4, and spec §5's recorded trigger) as evidence about whether the p99
ceiling **binds**. Read literally, a guaranteed-inert probe would retire a live builder
question — the deferred p99 rescale — on evidence that was never capable of speaking.
*Falsifier:* if the harness sets `s_max` as a designer-chosen constant (e.g. 0.95) rather
than by P3's rule, D1 does not apply; but that contradicts P3 as written, and it changes
the binding set from "ceiling only" to "everything above 0.95".

**Fix.** Decouple the *binding set* from the *toll magnitude*. Either an additive term —
`cost += w_toll` when `sim >= 1.0`, with `w_toll` pre-registered in units of `w_hop`
(e.g. 1×, 5×) — or keep `min(sim, s_max)` and pre-register `s_max` as a magnitude while
stating plainly that near-ceiling edges are tolled too. P3 as written should be replaced,
not merely executed.

**What currently works only because of the property this removes:** the ceiling edges are
what makes famous↔famous routing cheap and short; a real toll will lengthen exactly the
paths the F1 guard already lengthens on pairs 4–5. That is intended, but it means T1's
d0 no-regression inspection will show the largest diffs of any arm, and should not be
read as a failure signal.

### D2 — the FL arms' depth device is fully relaxed away before the depths the primary outcome scores. **High.**

**MEASUREMENT (M4).** With `floor_relax_known = 0.15` per bypass, the floor reaches 0 at
**6–7 `known` bypasses on every one of the 12 pre-registered pairs** in percentile
currency, and at 4–7 in raw. Snapshots are d ∈ {0, 5, 10, 15, 20}; **C1 is scored at
d ≥ 10 and C2 at d15/d20.**

**Consequence, arithmetic not inference.** `max(0, floor − pop_v) ≡ 0` for every node once
`floor = 0`. So **FL1 and FL2 are numerically identical to W in every cell C1 and C2
score.** They differ from W only at d0, and partially at d5. §2.4 **R3 designates
FL1/FL2 as the pre-registered remedy** for "arms dive but show no depth gradient" — that
remedy is inoperative at the depths in question, so R3's branch cannot be reached as
written.

**Second consequence, about shipped code.** The same arithmetic applies to production P
in raw currency. §0's flip-side claim — that the floor is "the only depth-graduated
device in the shipped cost function", so the family needs it — is true of the code and
**empty at d ≥ 7 for these pairs**. Whatever depth gradient P shows in the C1 window comes
from the exclusion set alone, not from the floor.

**Fix.** Pre-register the relax step *in the currency it operates in*, calibrated against
the snapshot span (e.g. relax such that the floor traverses its range over ~20 bypasses,
or a multiplicative decay), and add snapshots at d ∈ {1, 2, 3, 5, 7} where the device is
alive. *Falsifier:* if the harness re-derives the relax constant instead of reusing
`config.py`'s, D2 does not apply — the pre-registration names the config constant
explicitly (§1.4, FL1 row).

### D3 — the J-cur column's structural expectation is the opposite of its stated mechanism, and §2.4 has no read for that outcome. **High.**

**MEASUREMENT (M2).** Percentile currency compresses the top decile (7,420 nodes into
0.10 of the percentile range) and stretches the bulk. Consequently, on edges incident on
the top decile, **lateral** famous↔famous moves become 2.6× *cheaper* in the jump term
while **exits** become 1.36× *dearer*. The quantity Dijkstra actually responds to is the
price of an exit relative to the alternative: that ratio goes **1.908 → 6.790** (3.56×
worse), and for deep exits **5.121 → 26.058** (5.09× worse).

**INFERENCE.** At matched `w_jump`, the percentile arms (A1, A4, A5, A7) should dive
*less* than their raw counterparts. Within this factorial the knob that promotes diving
is **J-mag** (and X's `w_jump = 0`), not J-cur. *Falsifier, and it is cheap:* A1 beats A0
on C1. If it does, this inference is wrong and should be discarded — the sweep settles it
at zero extra cost. State this prediction in the execution log before the arms run, so
the sweep tests the review as well as the design.

**Why this is a protocol defect and not merely a prediction.** §2.4 asserts it writes
"the read of each possible result". It has R0 (full null), R1 (only X moves), R2 (raw
moves as much as pctl), R3 (dive without gradient), R4/R5 (listen outcomes). **There is
no branch for "the percentile arms move ΔF the wrong way"** — which the graph's own
geometry predicts is the modal outcome. Without a pre-written read, that result arrives as
a surprise and gets interpreted post-hoc, which is the failure mode §2.4 exists to
prevent (log §2.13's own lesson: measurements held, interpretations did not).

**Add R6:** *percentile arms move ΔF positive while raw-magnitude arms move it negative.*
Read: the currency is not the mechanism — top-decile compression makes lateral moves
cheap faster than it makes exits cheap. Licenses: preferring the raw-currency arms and
recording §2.12's currency framing as **specific to the `known` gate** (where it is a
threshold on a drop and the argument is sound) rather than to `w_jump` (where it is a
price relative to alternatives). Does **not** license re-opening anything in log §4/§4.1.

**Also: A1 vs A0 is not one column.** Graph-wide the mean jump term is **1.864×** larger in
percentile currency, so the swap changes the term's overall **scale** as well as its
**geometry**; only the geometry is the intended treatment. Pre-register a scale
normalisation (match the mean jump term over the edge set, or over top-decile-incident
edges) and report normalised and unnormalised side by side. A scalar cannot remove the
geometry change — that is the treatment — but it removes the confound.

### D4 — C6 protects C1 and does not protect C2. **Moderate.**

C1 is a **median** and is robust to losing the extreme tail of an arm's interiors. C2 is
an **extreme-value** criterion ("at least one d15-or-d20 interior below B_unk") and is
maximally sensitive to precisely the artists most likely to fail exact-name proxy
matching — Attack 4's own argument, that match failure correlates with obscurity. C6
bounds the coverage **rate** and the candidate-vs-P coverage **gap**, neither of which
bounds the loss of a single most-obscure artist in a single cell. §2.2 makes manual
resolution discretionary ("where feasible").

**Fix.** Make manual resolution **mandatory** for every unmatched interior in a d15/d20
cell (a bounded set — at most 8 pairs × 2 depths × a few interiors), and pre-register that
a cell with an unresolved interior is scored **C2-indeterminate**, not C2-fail.
*Confidence:* high on the asymmetry (it is a property of medians vs extrema); moderate on
its practical size, which depends on the §5 matching pilot's failure rate.

### D5 — §5's falsifier thresholds are not interpretable on the sample §5 specifies. **Moderate.**

The 33-artist sample is purposively stratified and roughly half extreme-end by
construction (9 anchor "unknowns", 6 likely-reach obscure, plus superstar
endpoint-class). Two consequences in **opposite** directions:

- **Spearman is inflated.** A bimodal sample makes rank agreement easy; the proxy's real
  job is discriminating within the mid-fame regime, which the sample barely populates. The
  0.6 falsifier is easy to pass for the wrong reason. With three buckets over 33 artists
  the ordinal is also heavily tied, and the tie-corrected variant is not specified.
- **The inversion count is inflated.** "More than 2 catastrophic inversions" is an
  absolute count on a sample deliberately enriched 6/33 with off-platform stress cases.
  The falsifier is easy to trip for the wrong reason.

Neither threshold is a population property, so neither pass nor fail is informative as
stated. **Fix:** report per-stratum, compute Spearman additionally **within** the
"heard of" + "know well" subset, express inversions as a rate within the stress stratum,
and pre-register the tie-corrected Spearman. *This does not weaken §5's design* — the
stratification is the right sampling choice; only the scoring rule needs to respect it.

### D6 — the held-out gate's pass rate under the null is ~31 %. **Low-moderate; partly a labelling defect.**

"Direction reproduces if ΔF < 0 in ≥ 3 of 4 held-out pairs" has, under independent 50/50
signs, probability 5/16 = **0.3125** (MEASUREMENT: binomial arithmetic). W is selected as
the maximum over 8 factorial cells, so multiplicity is real and the design correctly
restricts the held-out step to *direction only* (the claim-45 lesson). But a gate that
one candidate in three passes by chance should not be described as confirmation.
Two further points:

- The analysis and held-out sets are **not exchangeable**: analysis pairs were chosen for
  diagnostic value (canonical listen pairs, F1's direct-edge cases, F6's trace), held-out
  are ordinary famous↔famous. A held-out failure confounds instability with pair-population
  difference. Pre-register per-pair reporting on both sets so the two are separable.
- The terminal gate is the blind listen, and §3 already accepts "one burned listen" as the
  cost of a false pass. So the honest fix is mostly **labelling**: state the 0.3125 in the
  document, or tighten to 4 of 4 (P = 1/16).

### D7 — guard G has no defined behaviour when the direct edge is a bridge. **Low.**

§4's mechanic is: if the result is `[source, target]`, mask that edge and re-run. If the
edge is a bridge, `find_path` returns `None` (`pathfinding.py:133-134`) and the cell is
undefined — reintroducing the arm-correlated missingness §4 says the guard removes
(exclusion sets are arm-specific at depth, so infeasibility can arise in one arm and not
another). Unlikely on this graph for famous pairs, and cheap to close: pre-register that a
guard-infeasible cell is dropped from **all** arms uniformly and reported.

---

## 4. OBSERVATIONS — true, not protocol-invalidating

- **O1 — the walk is driven in a currency the design declares invalid for the outcome.**
  Victim selection is "most-popular interior, in-graph popularity" (§1.2); the outcome is
  external fame; log §2.11 establishes these differ at the top. It is held constant across
  arms, so the **contrast** is valid. But C2 and C3 are *absolute trajectory* criteria
  answering F2/F6, which are about what a **user** experiences — and a user bypasses artists
  he *knows*. §6.6 names "real-user bypass behaviour" but not this currency mismatch. Once
  P4 has a validated proxy, one sensitivity arm walked with a fame-driven victim rule
  would bound it cheaply.
- **O2 — pairs 4 and 5 will contribute single-artist medians.** Under guard G, a
  direct-edge pair's walk becomes "enumerate the k-th best single intermediary", so those
  cells carry ~1 interior at every depth. That is 2 of 8 analysis pairs where C1's per-cell
  statistic is one artist, C2 is near-unreachable, and C4 is trivially satisfied. Uniform
  across arms, so not a confound — but pre-register stratified reporting (C1 with and
  without pairs 4–5).
- **O3 — `w_degree_hub` is missing from §1.2's constants table** (`config.py:44`, default
  0.0). It is *genuinely* constant under every intervention here (a zero weight cannot be
  un-zeroed by turning another knob), so this is a completeness gap against the new
  dormant-term rule G3 adds, not a confound.
- **O4 — the avoidance field is depth-graduated too**, under `dislike` (§1 item 1c).
  Matters only for §1.5's F4 dislike walk, where "static per request" is not true.
- **O5 — §0's file:line citations are correct against HEAD and stale against the working
  tree**, where G2 is renaming `popularity → pop_raw`, `w_hub → w_degree_hub`,
  `effective_floor → effective_floor_raw`. G2's plan names this hazard; recording that it
  has materialised.
- **O6 — P2 is already discharged.** The execution log records G1's canonical set covering
  every §2.3 endpoint; my M4 independently resolved all 12 pairs. The pre-registration's §7
  still lists P2 as outstanding.
- **O7 — A0 is scheduled as one of 13 arms, not as a gate.** If A0 ≢ P, §1.4 requires
  re-anchoring with floor as a fully crossed column: 16 cells plus attachments, which is
  not inside the "13 runs, roughly an hour" budget. A0 costs one arm; run it first.
- **O8 — the mirror-and-verify / guard-G contradiction is real.** Independently confirmed:
  §1.2 applies G to all arms including P, while §1.4 requires the mirror to reproduce P
  byte-identically, and log §3.10 says non-identical paths mean *stop*. The pre-Track-2
  guards plan G5(a) already identified this and prescribes the fix (verify with G off, then
  enable G uniformly). One addition it does not make: with G applied to P, **no comparison
  anywhere in the design is against shipped behaviour on pairs 4–5**, so the C5
  no-regression inspection cannot see the d0 change the owner would actually notice there.
- **O9 — C1 weights cells, not artists.** A mean over cells of a within-cell median gives a
  1-interior cell the same weight as a 10-interior cell. Defensible (a cell is one
  user-visible journey) but worth stating, with a pooled-artist variant reported alongside.
- **O10 — a defence, recorded because it looked like a defect and is not.** Walking each arm
  independently means arms accumulate different exclusion sets by depth. That is *not* a
  confound: the bypass trajectory is downstream of the arm's own cost knobs, so it is a
  mediator, and what C1 estimates is the **total effect of the arm under the scripted
  policy**. The design should say so in one sentence, because "paired over cells" reads as
  a within-subject contrast and it is not one.

---

## 5. Task 3 — the outside reader's candidates

**(a) Does the floor-off column remove the state dependence, and is A0-vs-P the right
discriminating test?**

*Partly confirmed, with a relocation the pre-registration does not name.* Holding
`w_floor = 0` does genuinely remove the term as an uncontrolled variable inside the
factorial — a zero weight cannot switch itself on, which is the strongest form of
"constant under the intervention". It relocates **twice**. First into the FL arms, where
the reintroduced floor is a legitimate one-column contrast but is inert at every scored
depth (**D2**). Second into **adoption**: a winning floor-off cell ships a router with no
depth-graduated cost term at all, so F2's "progressively" and F6's "no snap-back" would
rest entirely on the exclusion set. §2.4 R5 does not mention that consequence.

On the test itself: **A0-vs-P path identity is the right discriminating test for the
decision at hand**, though it is weaker than claim 23's literal statement. The floor term
can be non-zero on nodes Dijkstra *examines* without changing the argmin; path identity
tests "the floor changes outcomes", which is exactly what matters for whether it is an
uncontrolled variable. Recommend one addition: report the fraction of examined nodes
carrying a non-zero floor term alongside the identity result, so the state "identity
holds but the term is firing" is visible rather than inferred. And run it **first**, as a
gate (O7).

**(b) Is cell W's selection under R1 a selection-inference problem, and do the attachments
inherit it?**

*Confirmed for W; refuted, with the sign reversed, for the attachments.* W is the maximum
of 8 noisy C1 statistics, so W's own contrast against P is upward-biased — classic
winner's curse. The design's held-out step is the correct structural mitigation and
explicitly restricts to **direction, not magnitude**, citing the claims-45 lesson; the
residual weakness is that gate's 31 % null pass rate (**D6**). The attachments do **not**
inherit the bias in the same direction: T1's and FL1's own effects were not used to select
W, so `T1 − W` is unbiased for the attachment effect, but it is measured against an
upward-biased **baseline**, which biases attachments to look **worse** than they are.
Net: anti-conservative for W-vs-P, conservative for the attachments. Only the first needs
a fix.

**(c) Is the percentile currency well-defined at the top, and is P6's average-rank
sufficient there?**

*Refuted as posed — and a different problem confirmed in the same place.* **MEASUREMENT
(M3):** the top decile holds 7,420 nodes carrying 7,186 distinct popularity values with a
largest tie group of **3**. Percentile is finely resolved at the top and average-rank ties
are a non-issue there. The plateaus are at the **bottom** (largest 430 nodes, 0.58 % of N;
414 at exactly 0.0), where average-rank is both necessary and adequate. P6 is correct and
sufficient as written.

What log §2.12's top-decile span actually implies for the percentile currency is not
ill-definedness but **compression**: the same fact that makes a raw drop meaningless at the
top makes a percentile *distance* tiny at the top — which cheapens lateral famous↔famous
travel far more than it cheapens exits (**D3**). The concern is real; it lives one step
away from where the question put it.

**(d) None of these / what I found instead.**

The three findings I would act on are **D1** (T1 inert by construction), **D2** (the FL
depth device is exhausted before the C1 window), and **D3** (the currency column's expected
sign, and the missing read R6). None of the three was among the candidates offered, and all
three are settled by arithmetic over the artifact rather than by argument. D1 and D2 are
**arithmetic certainties** given the pre-registration's own prerequisites and constants;
D3 is a measurement plus a falsifiable inference that the sweep itself will test.

---

## 6. Prerequisites named rather than taken, and what I did not check

| # | Prerequisite | Why it is not in this document |
|---|---|---|
| PR-A | Run **A0 vs P** on the pair × depth grid as a gate before the factorial | Settles Task 1 item 1d — whether `w_floor`'s inertness transfers to `graph-t15-tiebreakfix.bin`. Requires routing paths, which my brief excludes. It is already an arm; only its ordering needs changing. |
| PR-B | **Cost decomposition on routed dive hops** under both currencies (log §3.7's method) | Settles D3 directly rather than by edge-level marginal analysis. Requires routing paths. |
| PR-C | Re-measure the toll as a fraction of `w_hop` after D1's fix is chosen | Depends on which fix is taken. |

**Not reviewed, by scope:** the harness (P8b), the blind-listen protocol, whether any arm
would produce coherent paths, and anything about clips. **No judgement offered** on whether
the sweep should run, on product direction, or on owner preference.

**Clean-result statements, per the brief.** I found **no refutation** of §0's code claims —
that category is empty and I did not manufacture one. I found **no defect** in the pair
set, in the guard-G decision itself, in the attack analysis of §3, or in P6.

---

## 7. Script

Run from `api/` (`UV_LINK_MODE=copy uv run python …`). Asserts the artifact sha256 first,
per the established convention. Should be committed to
`builder/analysis/2026-07-23-track2-protocol-review/` with a README.

```python
import hashlib, sys
from pathlib import Path
import numpy as np

ROOT = Path(r"C:\Users\charl\OneDrive\Claude Projects\music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
assert hashlib.sha256(GRAPH.read_bytes()).hexdigest() == EXPECT, "WRONG ARTIFACT"

from artistpath_api.graph_store import GraphStore
store = GraphStore.load(GRAPH)
N = store.artist_count
pop = np.asarray(store.pop_raw, dtype=np.float64)
scores = np.asarray(store.scores, dtype=np.float64)

# M1 — ceiling and score grid
ceil = scores >= 1.0
print(int(ceil.sum()), len(scores), float(scores[~ceil].max()),
      1.0 - float(scores[~ceil].max()), np.unique(scores).size)

# P6 percentile: average rank over N
order = np.argsort(pop, kind="stable"); ranks = np.empty(N); sp = pop[order]; i = 0
while i < N:
    j = i
    while j + 1 < N and sp[j + 1] == sp[i]:
        j += 1
    ranks[order[i:j + 1]] = (i + j) / 2.0
    i = j + 1
pctl = ranks / (N - 1)

# M3 — tie structure
u, c = np.unique(pop, return_counts=True)
print(u.size, int(c.max()), float(u[c.argmax()]), int(c[c > 1].sum()))
top = np.where(pctl >= 0.90)[0]
ut, ct = np.unique(pop[top], return_counts=True)
print(top.size, ut.size, int(ct.max()))

# M2 — currency geometry
src = np.repeat(np.arange(N, dtype=np.int64), np.diff(store.offsets))
dst = np.asarray(store.neighbours, dtype=np.int64)
d_raw = np.abs(pop[src] - pop[dst]); d_pct = np.abs(pctl[src] - pctl[dst])
hi = pctl >= 0.90
lateral = hi[src] & hi[dst]; exit_ = (hi[src] | hi[dst]) & ~lateral
deep = (hi[src] | hi[dst]) & ((pctl[src] < 0.5) | (pctl[dst] < 0.5))
for nm, m in (("all", np.ones(len(d_raw), bool)), ("lateral", lateral),
              ("exit", exit_), ("deep", deep)):
    print(nm, int(m.sum()), d_raw[m].mean(), d_pct[m].mean())
print("exit/lateral raw", d_raw[exit_].mean() / d_raw[lateral].mean(),
      "pctl", d_pct[exit_].mean() / d_pct[lateral].mean())

# M4 — floor saturation on the pre-registered pairs
by_name = {}
for i, nm in enumerate(store.names):
    p = by_name.get(nm)
    if p is None or pop[i] > pop[p]:
        by_name[nm] = i
PAIRS = [("Miles Davis", "Daft Punk"), ("The Shins", "Wishbone Ash"),
         ("Metallica", "Taylor Swift"), ("Radiohead", "The Beatles"),
         ("Muse", "Coldplay"), ("Madonna", "Bob Dylan"),
         ("Pink Floyd", "Aphex Twin"), ("Arctic Monkeys", "Johnny Cash"),
         ("Michael Jackson", "Gorillaz"), ("System of a Down", "R.E.M."),
         ("The Rolling Stones", "Linkin Park"), ("Nirvana", "CROOVE")]
for a, b in PAIRS:                      # 0.15 == config.py:47 floor_relax_known
    ia, ib = by_name[a], by_name[b]
    bp, br = min(pctl[ia], pctl[ib]), min(pop[ia], pop[ib])
    print(a, "->", b, round(bp, 4), round(br, 4), int(np.ceil(bp / 0.15)))
```
