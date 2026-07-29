# TB-P1 — protocol review of the Track 3b pre-registration

Artifact: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 verified
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`. N = 74,193, 898,006
directed CSR entries. Asserted by all three probes.

Derivation only, per the agent's remit. Nothing here says whether the track is worth
running, and no finding below is a recommendation about adoption, a listen, or a knob
value.

---

## F1 (HIGH) — §2's dose premise is a cross-pair-set quotation, and it is wrong on the pair set this track uses

**Claim checked.** §2: "production's d ≥ 10 interiors sit at median pctl ≈ 0.998 (PLA-R2),
so per interior the toll is `w · k · 0.098 ≈ w·k/10`, and at k = 10 the realised toll per
such interior is ≈ `w`. Setting `w ∈ {0.10, 0.30, 1.00}` therefore reproduces Track 3's
realised ladder of 5× / 15× / 50× `w_hop`."

**What I did.** `tb_p1_probe_dose.py` §2 — the pctl of production's own scored C1-window
interiors, taken from the committed `t3_paths.json` P walks on `pairs_v2.json`, and the
same statistic on Track 2's committed `paths.json` (the set PLA-R2 was measured on).

**Result.**

| set | interiors pooled (d ∈ {10,15,20}, analysis) | median pctl | share above the knee | above-knee median pctl |
|---|---|---|---|---|
| Track 2's set (PLA-R2's own) | 157 | 0.9976 | 100.0 % | 0.9976 |
| **`pairs_v2.json` (this track's)** | **307** | **0.9810** | **88.6 %** | **0.9864** |

PLA-R2's ≈0.998 reproduces exactly — **on Track 2's pair set**. On `pairs_v2.json` the
figure is 0.9810 (all interiors) / 0.9864 (above-knee only), mean 0.9585. The realised
ladder at k = 10, in `w_hop` units per interior:

| premise | w = 0.10 | w = 0.30 | w = 1.00 |
|---|---|---|---|
| §2's (pctl 0.998, other pair set) | 4.9× | 14.7× | 49.0× |
| measured, above-knee median (0.9864) | 4.3× | 13.0× | 43.2× |
| measured, all-interior median (0.9810) | 4.1× | 12.2× | 40.5× |

**Second, larger half of the finding — dispersion.** Track 3's toll is `w·k·pctl`, and
production's interiors span pctl 0.90–1.00, so its per-interior price is nearly uniform.
This device's toll is `w·k·(pctl−0.90)`, so its price spans the whole range 0→0.10. Per
above-knee interior at k = 10 (percentiles across the 272 above-knee interiors):

| arm | p5 | p25 | median | p75 | p95 | max |
|---|---|---|---|---|---|---|
| TB-A2 (w = 0.30) | 1.9× | 9.6× | 13.0× | 14.2× | 14.8× | 14.9× |
| DD-A2 (w = 0.03) | 12.5× | 14.3× | 14.7× | 14.9× | 15.0× | 15.0× |

An **8× spread** where Track 3's was **1.2×**. At the whole-path level the ladders are
also not equivalent: median path toll at k = 10 is 46 / 138 / 461 `w_hop` for
TB-A1/A2/A3 against 62 / 187 / 625 for DD-A1/A2/A3 — this ladder prices a whole
production path at ~74 % of Track 3's at the same nominal rung.

**Verdict.** The arithmetic in §2 is internally correct and the *median* correspondence is
good to ~12–18 %. The **premise** is a figure measured on a different pair set, quoted
without saying so — the exact defect DD-P3-8 recorded against Track 3's DD-C2 baseline —
and this document's own scope guard ("No figure here is comparable to Track 3's except
where the pair set and statistic are identical and the comparison says so") forbids it.
The "comparable in the currency that matters" claim survives **at the median only**; it
does not survive as a statement about what a typical famous interior pays, because there
is no typical payment under this device.

**Amendable as:** replace the PLA-R2 citation with the measured `pairs_v2` figures above
(this review owns them), state the ladder correspondence as "≈4 / 13 / 43× at the median
above-knee interior", and add one sentence recording the dispersion so a null at TB-A1
cannot later be read as "the price was uniform and still ignored".

---

## F2 (HIGH) — TB-P3(b)'s forecast is already determinable, and it says the ceiling shortens: mean −6.83 interiors

**Claim checked.** §5 TB-P3(b): "Track 3's (unthresholded) ceiling shortened 13 → 5; if
**this** ceiling preserves length, the mechanism has structural room… Recorded before arms
so the forecast cannot be reshaped to fit them."

**What I did.** `tb_p1_probe_ceiling.py` computes TB-P3's ceiling exactly as §5 specifies —
base-cost-minimal Dijkstra on the induced sub-decile subgraph, endpoints exempt, the
cell's exclusion set applied (reconstructed by `dd_p1_headroom.py`'s rule from a fresh
production walk), direct edge masked — on all 23 surviving analysis C1-window cells. The
probe first asserts that its own production cost reproduces P's delivered path: **35/35
cells byte-identical**, which is also an independent confirmation that the floor
contributes nothing at these depths (the probe omits the floor term entirely).

**Result.**

| C1 window, analysis, n = 23 | P | TB-P3 ceiling |
|---|---|---|
| mean interior count | 13.35 | **6.52** |
| median interior count | 13.0 | 6.0 |
| mean paired delta (ceiling − P) | — | **−6.83** |
| mean of cell-median pctl | 0.9815 | 0.7879 |
| mean above-knee interiors | 11.83 | 0.00 |
| ceiling exists | — | 23/23 |

TB-C6 flags a drop > 1.0. The ceiling is flagged by **6.8×** the threshold.

**The DD-D5 decomposition, restated for this device.** With the ceiling's toll identically
zero, `ΔT = n_P·ē_P`, so length share = `(n_P − n_C)/n_P` and descent share = `n_C/n_P`
exactly. Measured per cell: min 0.000, **median 0.500**, max 0.714. Track 3's median
length share was 80.7 % (owned by `DD-P3-analyst-review.md` DD-P3-3). So the thresholded
form genuinely halves the confound and does not remove it.

**Verdict.** §5 says TB-P3(b) "gates nothing" and is recorded "before arms so the forecast
cannot be reshaped". Both are satisfied — but the forecast's *answer* is derivable now,
with no arm, no fame fetch and no harness: **this ceiling also shortens**, by a mean 6.83
interiors, and §5's own text says that makes "TB-R2 the likely outcome". This is the same
class of item as DD-D4 and DD-D5 — available from the document plus the artifact before
anything is built, which is what running TB-P1 first was for.

**Amendable as:** record this figure in TB-P3(b) now, as the pre-run forecast, with its
provenance. Note that it does *not* pre-judge the arms: the finite doses are not at the
limit (F3), and the arms walk their own victim sequences (F4).

---

## F3 (HIGH) — TB-R3's inference does not follow. The ceiling bounds the toll; TB-C1 is scored in fame, and the two are not monotonically related

**Claim checked.** §5 TB-P3(a) / §7 TB-R3: "If it fails to clear −1.0 log10, the arms are
not run: **no dose can beat the `w → ∞` limit**, so TB-C1 would be unreachable."

**Part 1 — the limit argument itself is sound, and I verify it.** Write
`cost_w(p) = base(p) + w·k·T(p)` with `T(p) = Σ_interiors max(0, pctl − 0.90) ≥ 0`. The
feasible path set is finite. Since a zero-toll path exists on every scored cell (DD-P1 at
100 %, and confirmed here: the ceiling exists on 23/23), `min T = 0`, and for large enough
`w` the argmin is the **lexicographic** minimum of `(T, base)` — i.e. base-cost-minimal
among zero-toll paths. That is precisely TB-P3's construction. Two degenerate cases
checked:

- **Set identity at the knee.** The device is zero at `pctl ≤ 0.90`; the construction
  removes `pctl < 0.90`'s complement. Measured: **no node has pctl exactly 0.90**
  (`pctl` is average-rank over N = 74,193; nearest values 0.8999824779 and 0.9000026957).
  So the two sets coincide at 66,773 nodes and the construction is exact **on this
  artifact**. It is not exact by definition — it is exact because of an arithmetic
  accident, and it would need re-checking on any rebuilt artifact.
- **"Toll → 0 without being zero."** Impossible: the smallest positive per-node toll
  factor is `2.696e-06`, so positive path tolls are bounded away from zero. But the same
  number bounds *convergence*: reaching the limit requires `w·k · 2.696e-06 >` the base-cost
  gap, which runs to 7.4 here — i.e. `w·k ≳ 2.7e6`, against a ladder maximum of `w·k = 20`.
- **Ties.** Base-cost ties among zero-toll paths break on the heap's `(cost, node)` order,
  the same tie-break production uses. Correct, and strictly better than DD-D6's `BIG = 1e6`
  scaling, which could in principle be defeated by a small enough pctl gap.

**Part 2 — the inference from the limit to "no dose can reach TB-C1" is not valid.**
Three measured reasons:

1. **TB-P3's ceiling is not the fame-extreme of the zero-toll family.** Once `T = 0` the
   device is indifferent among *all* all-sub-decile paths and picks the base-cost-cheapest.
   DD-D6's committed LIMIT (min Σpctl) is a different member: **0/23 cells identical**;
   mean cell-median pctl 0.6445 (LIMIT) vs **0.7879** (TB ceiling), with the TB ceiling less
   obscure on **17/23** cells. Recomputed from `gap_paths.json` + `gap_fame.json`, DD-D6's
   LIMIT sits at a mean-interior-F gap of **−2.732** against P (this agrees with the figure
   the Track 3 execution log §4 owns). The TB ceiling's fame is **unmeasured** — it needs
   TB-P2 (F8). Picking the base-cost tie-break is *correct for this device*; the point is
   that the resulting number is materially weaker in obscurity than the Track 3 ceiling
   everyone will anchor on, and TB-P3(a)'s −1.0 gate is read against it.
2. **The step "ceiling fails in pctl ⟹ no dose reaches −1.0 in fame" requires the
   pctl→fame map to be monotone**, which is exactly the map DD-D6 named as the trap
   (percentile headroom does not entail fame delivery). Measured monotonicity holds here in
   **pctl**: mean cell-median pctl runs P 0.9815 → w=0.10 0.9349 → w=0.30 0.9049 → w=1.00
   0.8570 → ceiling 0.7879. It is **not** measured in fame, and the gate is stated in fame.
3. **The ladder mostly does not reach the limit.** Static per-cell optima under P's own
   exclusion sets (one Dijkstra per cell at fixed k — not an arm, not a criterion):

   | quantity | P | w=0.10 | w=0.30 | w=1.00 | ceiling |
   |---|---|---|---|---|---|
   | mean interior count | 13.35 | 8.13 | 6.48 | **5.91** | 6.52 |
   | mean above-knee interiors | 11.83 | 6.22 | 3.39 | 1.83 | 0.00 |
   | mean path toll (pctl units) | 0.8830 | 0.3748 | 0.1524 | 0.0615 | 0.0000 |
   | cells identical to P | 23 | 1 | 0 | 0 | 0 |
   | cells identical to the ceiling | 0 | 0 | 0 | **5** | 23 |
   | cells strictly between | 0 | 22 | 23 | **18** | 0 |

   At the ladder's top rung the device reaches the limit on **5/23 cells**. Note also that
   **interior count is not monotone**: w=1.00's optimum is *shorter* (5.91) than the
   ceiling (6.52). So the ceiling is not extremal in TB-C6's currency either.

   Corroborating: `w*`, the smallest dose at which the ceiling undercuts P's delivered path
   at that cell, runs min 0.0580 / median 0.2808 / max 0.6652. `w = 0.10` clears it on
   3/23 cells, `w = 0.30` on 14/23, `w = 1.00` on 23/23 — so the ladder does bracket the
   crossover, which is the DD-P3-9 property and it holds here. That is a separate,
   clean confirmation and it is F-clean below.

4. **The ceiling is computed under P's exclusion sets; the arms do not share them.**
   DD-P3H-13 recorded that TB-C1's pairing is by `(pair, depth)` and *not* by exclusion set
   — each arm bypasses its own victims. So the ceiling is the limit "at the exclusion state
   production would have been in", not the limit of the arm's own walk. See F4 for why the
   difference is not small.

**Verdict.** TB-P3 is a **sound and useful upper bound on the device's toll-minimising
behaviour at P's exclusion state**, and a sound NO-GO screen in the weak sense (if even
this is nowhere near −1.0, the ladder is unlikely to be). It is **not** the theorem TB-R3
states. As written, TB-R3 licenses stopping the track on a bound that does not bound the
quantity TB-C1 measures.

**Amendable as:** restate TB-R3's reasoning without the word "no dose can beat", e.g.
*"TB-P3 computes the device's limit path at P's exclusion state. It bounds the toll, not
fame; the pctl→fame map is the one DD-D6 named as non-monotone. A failure is therefore
strong evidence that the ladder cannot reach TB-C1, not a proof of it — the stop is a
judgement about cost, and it is stated as one."* Keep the −1.0 effect size; it is a
legitimate pre-committed trigger either way.

---

## F4 (HIGH) — §0 omits the one term this device genuinely wakes: the victim rule feeding on the sub-decile subgraph

**Claim checked.** §0's stated purpose — "the confound that nearly broke Track 2 was a term
inert in the baseline *for a reason the intervention removes*" — applied to the
`victim rule` row, which §0 holds constant as "Track 2's exactly".

**What I did.** `tb_p1_probe_dormant.py` §1: walked production on all 12 scored pairs for
the full 21 depths and classified every victim the walker produced.

**Result.**

```
TOTAL: 0/252 of production's victims are sub-decile (0.0 %)
```

Every one of production's 252 victims is top-decile. So in P, the exclusion set is drawn
**entirely from nodes the sub-decile subgraph does not contain** — the walk never removes
a node the device would want to route through. Under an arm that routes sub-decile, the
victim (the most popular interior) is drawn **from that subgraph**, so the arm progressively
excludes its own supply. Sizing: the all-sub-decile routes available at these cells carry
**4–9 interiors (median 6)** against a walk of **20 presses**.

This is precisely the Track 2 §0 shape in mirror image: a mechanism that is inert in the
baseline *for a reason the intervention removes*, and it appears only in the arms that
succeed at descending.

**Consequences, none of which is fatal but all of which are unstated:**
- TB-P3's ceiling, computed under P's victims, is **optimistic** as a description of what an
  arm can deliver at depth — its exclusion set is disjoint from the subgraph, an arm's is not.
- TB-C2 (d5 → d20) compares an arm at d20 routing under 20 sub-decile exclusions against P
  at d20 routing under 20 top-decile exclusions. That is a real asymmetry in the statistic
  TB-R1 requires to pass, and it is not the pooling asymmetry TB-C2 already pre-commits
  against.
- It is a candidate mechanism for a **non-monotone TB-C2**, which is what Track 3 observed
  and attributed to saturation.

**Amendable as:** add a §0 row — *"victim rule × the sub-decile subgraph: NOT constant in
its effect. Measured: 0/252 of production's victims are sub-decile, so P's exclusions never
touch the subgraph the device routes into; an arm's do. Instrumented rather than assumed:
count sub-decile victims per arm per depth beside `floor_active` and `guard_fired`."* That
is the same remedy shape Track 3 adopted for guard G, it costs one counter, and it converts
an assumption into a measurement.

---

## F5 (MED) — §0's floor argument is unsound as written; the conclusion survives, and the argument is false exactly where TB-G2's non-vacuity check reads

**Claim checked.** §0: "the floor term depends only on the endpoints' min `pop_raw` and on
k (relaxing 0.15 per `known`), never on path content — so no device can wake it."

**Derivation.** `mirror.py::_dijkstra` computes `floor_pen = max(0.0, floor_val −
pop_raw_v)`. The floor **base** depends only on endpoints and k; the floor **penalty**
depends on the relaxation target `v`. As written the sentence is false, and it is false in
the specific way Track 2's §0 worked example warns about — if it were true, `w_floor` could
not have been woken by diving arms there.

The conclusion nevertheless holds, for the reason the *next* clause gives and which I
reproduce: floor bases on this pair set are 0.3081–0.4570 (DD-D4's table, reproduced
exactly by `tb_p1_probe_dose.py` §4 — alive for k ≤ 2 on 11 pairs, k ≤ 3 on
`Bluetech → L‐Vis 1990`), so `floor_val ≡ 0` from k = 3 (k = 4 on that one pair) and the
penalty is identically zero regardless of path content. The shallowest scored depth is d5.
Independent corroboration: `tb_p1_probe_ceiling.py`'s self-check omits the floor term
entirely and still reproduces P's delivered path on **35/35** C1-window cells.

**Where it is actually false.** At **d1 and d2** the floor is alive on every pair
(base − 0.15 ∈ [0.158, 0.307]; base − 0.30 ∈ [0.008, 0.157]), and the device pushes toward
sub-decile nodes — which have lower `pop_raw`, which is exactly what the floor penalises.
**TB-G2's non-vacuity check reads d1.** No criterion is affected; one gate is.

**Amendable as:** replace "never on path content — so no device can wake it" with "the
floor *base* depends only on the endpoints and k; the *penalty* depends on the relaxation
target, so the device does interact with it wherever the base is positive. On this pair set
the base is zero from k = 3 (k = 4 on one pair, DD-D4) while the shallowest scored depth is
d5, so the term is identically zero at every scored cell. It is live at d1–d2, which only
TB-G2's non-vacuity check reads."

---

## F6 (MED) — §0's enumeration is incomplete, and one omission is new: Track 3's own live knob

**Claim checked.** §0 "Enumerated per the CLAUDE.md rule."

**Result.** Reading `mirror.py`'s `SweepConfig`, the following are knobs that exist in the
harness this track will extend and are absent from §0's table:

| omitted term | inert because | does this device remove that reason? |
|---|---|---|
| `w_known_ramp_pctl = 0.0` — **Track 3's device, now living in the same `mirror.py`** | not set | no, but §0 must say it stays 0.0; a sibling device sharing a file is the single most confusable constant here |
| `w_avoid`, `avoid_penalty`, `avoid_decay`, `avoid_radius` | walk is all-`known`, so `_avoidance_map` gets an empty list | no |
| `toll_s`, `toll_hops` (Track 2 / 2F ceiling toll) | both `None` | no |
| `jump_mean_match` | only reachable under `jump_currency = pctl` | no |

All four are genuinely constant; the finding is the incompleteness, and it is a **carried
item from `DD-P3-analyst-review.md` DD-P3-10 that the new document does not honour** — the
same three omissions recur, plus a fourth that did not exist when DD-P3-10 was written.

**Amendable as:** four rows, one line each.

---

## F7 (MED) — TB-C2 gates TB-R1 and has no length control; DD-P3H-9's gap is now load-bearing

**Claim checked.** §6 TB-C6: "Mean interior count per arm vs P over **C1-window cells**".
§7 TB-R1: passes require TB-C1 **and** TB-C2, with **TB-C6 unflagged**.

**Derivation.** `DD-P3-harness-review.md` DD-P3H-9 recorded, as a stated gap, that DD-C6
covered DD-C1's window only while DD-C2 reads d5 and d20 with no length control, and
DD-P3H-10 quantified the inherited length bias at 16 % of DD-A2's DD-C2 figure and 92 % of
DD-A3's. Track 3b **promotes** TB-C6 to a criterion that gates TB-R1 — and keeps it on the
C1 window. So under TB-R1 an arm can be certified "length-preserving" on d ∈ {10,15,20}
while its TB-C2 pass at d5 → d20 is carried by a length change at d5 that nothing measures.
TB-C2's pre-committed pooling (per-pair medians, then a median across pairs) removes the
*pair-weighting* half of DD-P3H-10's bias but not the *within-cell* half: shortening still
moves a per-cell median downward with zero descent, because production's fame profile rises
from the endpoints inward (DD-P3-8 owns that measurement).

**Amendable as:** either extend TB-C6's window to every depth TB-C2 reads, or state
explicitly in TB-C6 that it does not cover TB-C2 and that a TB-R1 pass therefore certifies
length-preservation only in the C1 window. The first is free (the walk already produces
d5), and it must be chosen **now**, because choosing it after seeing the table is the move
pre-registration prevents.

---

## F8 (MED) — TB-P2 cannot be discharged in the order §5 fixes

**Claim checked.** §5: "Order: TB-P1 → TB-P2 → TB-P3 → TB-P4 → arms → TB-P5 → read", with
TB-P2 = "Fetch fame for interiors newly delivered by **the ceiling probe and the arms**".

**Derivation.** The ceiling probe is TB-P3 and the arms come after TB-P4. TB-P2 as worded
depends on outputs that do not exist at its position. Track 3 solved exactly this with
`dd_d6_gap.py`'s `--emit` / `--score` split (emit paths → run committed `fame.py` → score),
and the same split is what TB-P3 needs.

**Sizing, measured** (`tb_p1_probe_dormant.py` §3, over all 12 scored pairs' C1-window
cells): the ceiling delivers **78 distinct interiors**, of which **48** are already in a
committed mbid-keyed fame table (`t3_fame.json` ∪ `gap_fame.json`) and **30 are new
fetches**. **0 are blank-named**, so TB-G4's blank-name assertion is expected to pass on the
ceiling. Separately, `tb_p1_probe_ceiling.py` §F finds **0/23** ceiling cells fully covered
by `gap_fame.json` — i.e. the TB ceiling is a genuinely different path family from DD-D6's
LIMIT and cannot be scored from Track 3's committed fame table.

**Amendable as:** restate TB-P2 as two discharges — *"TB-P2a: the ceiling probe emits its
paths; fame is fetched for its new interiors before TB-P3(a) is read. TB-P2b: the same for
the arms' new interiors, before any criterion is evaluated (DD-G4 discipline)."* — and keep
the order otherwise.

---

## F9 (MED–LOW) — §3 mislabels the headroom denominator

**Claim checked.** §3: "**100 % certified headroom** (108/108 C1-window cells)".

**Result**, read off the committed `headroom_v2.json`:

```
all_scored          n=108  lacking 0
c1_window           n=36   lacking 0
c1_window_analysis  n=24   lacking 0
```

108 is **all nine snapshot depths** × 12 pairs. The C1 window is 36 cells (24 analysis).
The substance — 100 % everywhere, including every cell TB-P3 needs — is correct; the label
is not, and TB-P3 leans on it ("DD-P1 certifies a toll-free route exists for every scored
cell", which is true at 108/108 and would be a weaker claim if read as 36).

**Amendable as:** "100 % certified headroom — 108/108 scored cells across all nine snapshot
depths, of which 36/36 are C1-window (24/24 analysis)."

---

## F10 (LOW) — REQ-14 does not say what §Commissioned claims it says

**Claim checked.** Preamble: "REQ-14 *(no bypass mechanism may treat length as its
objective — which this device satisfies by construction, unlike Track 3's)*".

**Derivation.** REQ-14's text: *"Lengthening is **not a goal** of bypass, and no bypass
mechanism may treat **added length** as its objective."* Track 3's device did not treat
added length as an objective; it rewarded *shortening* as a side effect. REQ-14 as written
does not prohibit that, and PRODUCT-REQUIREMENTS §10 explicitly supersedes value 2's
lengthening clause precisely so failure-to-lengthen is not automatically a defect. The
parenthetical therefore (a) restates REQ-14 with "length" where the requirement says
"added length", and (b) draws a contrast with Track 3 that REQ-14 does not support.

Note that the substantive claim the document wants — this device does not price length as
its objective — is true by construction and is correctly argued in §1. It just is not
REQ-14's content, and REQ-14 is one of the three requirements the track names as its
warrant.

**Amendable as:** cite REQ-13 (bypass must increase delivered novelty) as the warrant and
REQ-14 as the constraint the device satisfies, and drop "unlike Track 3's" — or replace it
with a pointer to DD-C6's flag, which is the measured statement.

---

## F11 (LOW) — TB-C5 cites REQ-Q1 for a diagnostic in the wrong currency

**Claim checked.** TB-C5: "Distinct interior artists below pctl 0.90 at d ≥ 10 …
*(REQ-Q1: fame is the requirement currency; the pctl count is the artifact-currency
diagnostic)*".

**Derivation.** REQ-Q1's ruling retains, as the secondary diagnostic, "**Value 1's
degree-based count (non-hub interiors)** … because it catches the one failure fame cannot
see: an obscure structural connector the router over-uses." That is `top1pct_degree_frac`
territory — **degree**, not popularity percentile. A sub-decile-popularity count cannot
catch an over-used obscure connector, because such a connector is by construction
sub-decile *and* high-degree, so it counts as a win under TB-C5.

Both quantities are worth reporting; the citation attributes a degree ruling to a
percentile statistic, which is the currency-conflation class CLAUDE.md's orient table
names.

**Amendable as:** keep TB-C5 as written but re-label it "artifact-currency diagnostic
(popularity percentile)" without the REQ-Q1 attribution, and either add REQ-Q1's actual
degree diagnostic as TB-C5(b) or state that it is deliberately not reported here and why.

---

## F12 (LOW) — two well-definedness items in TB-C1

**(a) "24 C1-window cells" pre-commits a count the A13 drop changes.** 8 analysis pairs × 3
depths = 24 before any drop; **23** after Track 3's own drop set. TB's arms will produce
their own drop set, which may differ. Measured: `tb_p1_probe_dormant.py` §4 → 24 before,
23 after.

**(b) "cell statistic = median interior F difference" parses two ways.** Literally it reads
as the median of a set of differences, which is undefined — interiors do not pair up
between arm and P. The intended reading is Track 2's committed form, confirmed in
`score.py`: `cell_median(arm) − cell_median(P)`, then the mean over cells, tested against
`C1_MEAN_MAX = -1.0`.

**Amendable as:** "cell statistic = (median interior F of the arm) − (median interior F of
P) at the same cell — Track 2's `score.py::cell_median` form; mean over the C1-window cells
surviving the uniform A13 drop (24 before any drop)".

---

## F13 (LOW) — TB-C1(i)'s counterfactual constant is under-specified

"Reclassifying every `potentially_notable_unmatched` interior as a production-typical
famous artist (**F = P's C1-window median**)" does not say whether that median is over all
interiors (which includes the `F = 0` floor mass) or over matched interiors only. The two
differ materially and the choice moves the counterfactual in the direction that decides it.
`DD-P3-harness-review.md` DD-P3H-1 used the **matched** median. Fix the wording to
"matched-interior median on P's C1-window cells" so the constant is reproducible.

---

## F14 (LOW) — four citation-precision items

1. **TB-C1 cites DD-D8** for "the median is the less floor-exposed of the two". DD-D8
   (execution log §8) is the finding that DD-A2's pass rests substantially on the fame
   floor; it does not compare the cell mean against the cell median. The finding that does
   is **DD-P3H-4** ("the mean is materially more exposed to the `F = 0` floor than the
   median is"). Cite both.
2. **TB-C4 cites "DD-P3H's disclosed variant"** without a number; it is **DD-P3H-3**.
3. **§1 cites DD-D5 for "~80 % of its price was a hop-count penalty"**. DD-D5's 80.7 % is
   the median **length share of the toll differential between P's delivered path and the
   all-obscure route** — not a decomposition of the device's price in general. The
   distinction matters here because this document computes the analogous quantity for its
   own device implicitly (F2: median 0.500) and the two must be stated in the same form to
   be compared.
4. **§2 cites PLA-R2** without naming its pair set — see F1.

---

## F15 (LOW) — TB-P4 does not require a README for the new analysis directory

The 2026-07-23 defect-remediation spec §4.2 requires one of any analysis directory whose
scripts produce a recorded finding; `DD-P3-analyst-review.md` DD-P3-12 logged its absence as
a Track 3 provenance gap. TB-P4's bullet lists the mirror change, the new runner and scorer,
the Snyk scan and the guard-G counter, and does not list the README. (This review has
created `builder/analysis/2026-07-29-track3b-thresholded-toll/README.md` as a script index
for its own probes; the track's own directory still needs one.)

---

## Verified clean — checked and found correct, so the absence of a finding is a result

These were checked and are **not** findings. Listed so that silence is distinguishable from
an unexamined claim.

| # | claim | how checked | verdict |
|---|---|---|---|
| 1 | The `w → ∞` limit is base-cost-minimal among zero-toll paths | derivation over a finite path set; lexicographic argmin | **CONFIRMED** |
| 2 | The knee's removal set equals the device's zero-toll set | measured: 0 nodes at pctl exactly 0.90; 66,773 at pctl < 0.90 = pctl ≤ 0.90 | **CONFIRMED on this artifact**, by arithmetic accident not by definition |
| 3 | No path's toll tends to zero without being zero | smallest positive per-node toll factor 2.696e-06 | **CONFIRMED** (and it is what makes the ladder 5 orders of magnitude from the limit — F3) |
| 4 | A zero-toll guard-compliant path exists at every scored C1-window cell | ceiling computed directly: **23/23** analysis cells, all interiors verified sub-decile by assertion | **CONFIRMED** |
| 5 | TB-P3's per-cell exclusion handling matches `dd_p1_headroom.py` | probe reconstructs victims by the walker's own rule from a fresh production walk, endpoints exempt, direct edge masked; asserted no victim is an endpoint | **CONFIRMED** — and the probe's own production cost reproduces P's delivered path on 35/35 cells |
| 6 | DD-D4's floor bases and death depth | recomputed from the artifact: 0.3081–0.4570, alive k ≤ 2 on 11 pairs, k ≤ 3 on one | **REPRODUCES EXACTLY**; the whole absence of a floor axis is safe at every scored depth |
| 7 | §0's guard-G row: zero expected exposure on scored pairs | adjacency measured in the CSR: **0/12** scored pairs adjacent; **2/4** anchors adjacent (`Radiohead → The Beatles`, `Muse → Coldplay`) | **CONFIRMED** |
| 8 | §1's "at k = 0 the term is exactly zero, first path is production's by construction" | same short-circuit / `x + 0.0` argument as DD-P3H-6, which is over-determined; `mirror.py`'s live-only rule is already in place for the Track 3 term | **CONFIRMED**, subject to TB-P4 implementing the new term the same way |
| 9 | Dijkstra validity | toll non-negative, node potential folded onto the in-edge, `k` a request constant | **CONFIRMED** (DD-P3-11's derivation carries unchanged) |
| 10 | The factor table's one-column rule | P → TB-A1 → TB-A2 → TB-A3, each differing only in `w_known_thresh_pctl` | **CONFIRMED** — one axis, no package comparisons |
| 11 | The ladder brackets the crossover (DD-P3-9's property) | `w*` per cell: min 0.0580 / median 0.2808 / max 0.6652; w=0.10 clears 3/23, w=0.30 14/23, w=1.00 23/23 | **CONFIRMED** — a null across this ladder is a mechanism statement, not "too small" |
| 12 | §2's TB-A3 remark: k=20 toll ≈ 2.0 vs sim term ≤ 3.0 | `1.0 × 20 × 0.098 = 1.96`; `w_sim(1−sim) ≤ 3.0` | **CONFIRMED** at §2's premise; at the measured above-knee median it is 1.73 |
| 13 | TB-C2 is well-defined on this pair set | 7/8 analysis pairs present at both d5 and d20 under Track 3's drop; **0 cells with 0 interiors, 0 cells with 1 interior**; median of 7 is a single value | **CONFIRMED** — see the note below |
| 14 | The A13 asymmetry DD-P3H-2 documented is removed | removing the pair from **both** depths is exactly the "pair dropped at both depths" column of DD-P3H-2's table, and A13 is uniform across arms (DD-P3H-7), so the pair sets match across arms and depths | **CONFIRMED** |
| 15 | TB-C4 is computable as written | interior hops require ≥ 2 interiors; **0/23** P cells and **0/23** ceiling cells fall below that | **CONFIRMED** |
| 16 | TB-C6 is computable as written | paired per-cell interior-count delta over a common cell set; identical to DD-C6, which DD-P3H-9 confirmed matches its definition | **CONFIRMED** |
| 17 | TB-G4's premise: `score_t3.py` never reads the A11 flag | `grep -c potentially_notable score_t3.py` → **0**; `fame.py:317` emits `potentially_notable_unmatched` | **CONFIRMED** — the `NEXT.md` deferral is genuinely due and TB-G4 discharges it |
| 18 | The `TB-` namespace is collision-free | repo-wide search for `\bTB-[A-Z]?[0-9]`: matches only in the pre-registration, `docs/README.md` and `NEXT.md` | **CONFIRMED**; and no collisions *within* the TB- series (A/C/G/P/R sub-series are disjoint) |
| 19 | Pair-set description in §3 | `pairs_v2.json`: seed 20260728, 8 analysis (4 famous_mid / 4 mid_mid), 4 held-out (2/2), 4 unscored anchors | **CONFIRMED** exactly as §3 describes, apart from F9's label |
| 20 | §0's walk row | `arms.py`: `SNAPSHOTS = (0,1,2,3,5,7,10,15,20)`, `MAX_DEPTH = 20`; victim rule `min(interior, key=(-pop, v))` in `run_arms.walk` | **CONFIRMED** |
| 21 | The 1.093 band-gap calibration | `band_gap.json` → `matched_only.band_gap = 1.092903405699702` | **CONFIRMED** |
| 22 | `acceptance.py`'s nameless-artist gate exists and is not in play (no rebuild) | `acceptance.py:162` blank-name check present | **CONFIRMED** |
| 23 | Every other cited identifier resolves | PLA-R1, PLA-R2, PLA-R4, MKS-6, DD-D4/5/6/7/8, DD-F1/F2, DD-P3H-2, DD-R2, DD-G1/G3/G4, REQ-9/13/14/30/31/34, REQ-Q1, `NEXT.md`'s closed list and its `score_t3.py` deferral | **ALL RESOLVE** — content mismatches only at F10, F11, F14 |

**One qualifier on row 13.** The 7/8 survival figure is under **Track 3's** drop set. TB's
arms will produce their own, and TB-C2's rule is well-defined for any drop set: if it leaves
an even number of pairs the median averages two values, and it only becomes undefined if
every analysis pair drops. The statistic is robust; the *specific* n is not pre-determinable.

**Carried items from the two prior reviews.** Honoured: DD-P3-3/DD-D5 (TB-C6 promoted),
DD-P3-4/DD-D6 (TB-P3 + TB-R3), DD-P3-10's guard-G counter, DD-P3H-1 (TB-G4 reads the A11
flag), DD-P3H-2 (TB-C2's pooling pre-committed), DD-P3H-3 (TB-C4 interior hops made
explicit), DD-P3H-4 (TB-C1 uses the cell median), DD-P3H-12 (held-out reported, gates
nothing). **Not honoured:** DD-P3-8's cross-pair-set-quotation lesson (F1), DD-P3-10's §0
completeness (F6), DD-P3H-9's TB-C2 length-control gap (F7), DD-P3-12's directory README
(F15).
