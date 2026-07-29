# DD-P3 second half — `ml-graph-analyst` harness review

**Role: REVIEW ARTIFACT for DD-P3 (prereg §4), second half.** Discharges "then **harness
review** once the toll lands in the mirror (P8b's precedent)". Derivation and correctness
only, per the agent's remit: **no recommendation about adoption, about whether DD-A2 should
be blind-listened, or about which option the owner should take**, and none is implied by
the ordering below.

Companion: `DD-P3-analyst-review.md` (the protocol half, pre-toll). Findings there are
cited as **DD-P3-n**; findings here as **DD-P3H-n**.

Under review: the DD-P4 diff to `../2026-07-23-track2-sweep/mirror.py` (commit `d22641b`),
`run_arms_t3.py`, `score_t3.py`, and the committed outputs `t3_paths.json`,
`t3_scores.json`, `REPORT.md`.

Artifact `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 verified
`4cb84ef9…b061dc8`, N = 74,193.

Probes, both read-only and both in this directory:
`dd_p3_harness_probes.py`, `dd_p3_harness_probes2.py`. Everything below was recomputed
**without importing `score_t3.py`**, including a second independent implementation of the
average-rank percentile (unique-value grouping instead of the sorted run-scan); the two
agree to `max|diff| = 0.000e+00` over all 74,193 nodes.

```bash
cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-28-track3-depth-descent/dd_p3_harness_probes.py
cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-28-track3-depth-descent/dd_p3_harness_probes2.py
cd api && UV_LINK_MODE=copy uv run python -u \
  ../builder/analysis/2026-07-23-track2-sweep/verify_mirror.py     # DD-G1, re-run
```

---

## DD-P3H-1 — DD-A2's DD-C1 pass rests substantially on the A11 unmatched→0 floor, and `score_t3.py` drops the A11 audit hook that Track 2's scorer reads. CONFIRMED

**Claim checked (task item F).** Whether any criterion could report PASS for a reason
other than the effect it names.

**Derivation.** Under A11, an artist with no English Wikipedia article scores `F = 0` — the
fame floor, an adopted decision resting on absence predicting "never heard of" 9/9. That
encoding is not in question here. What *is* measurable is how much of DD-C1 it carries, and
it rises steeply with the knob:

| arm | scored interiors, C1 window | unmatched (`F = 0`) | share | of those, A11-flagged *potentially notable* |
|---|---|---|---|---|
| P | 307 | 21 | 6.8 % | 4 |
| DD-A1 | 207 | 25 | 12.1 % | 2 |
| DD-A2 | 175 | 35 | **20.0 %** | 6 |
| DD-A3 | 157 | 52 | **33.1 %** | 10 |

DD-C1 recomputed over **matched interiors only** (the floor removed entirely):

| arm | DD-C1 as scored | matched-only | share of the effect carried by `F = 0` |
|---|---|---|---|
| DD-A1 | −0.658 | −0.400 (n = 23) | 39 % |
| **DD-A2** | **−1.287 (PASS)** | **−0.709 (n = 22, would not meet −1.0)** | **45 %** |
| DD-A3 | −1.923 (PASS) | −0.985 (n = 22, would not meet −1.0) | 49 % |

**This is not a bug** — A11 pre-registered exactly this encoding, and "the arm routed into
artists with no English article" is *intended* to read as reach. But A11 attached a guard
to it: an unmatched interior flagged `potentially_notable` gets a **one-glance owner check
before it counts as maximal reach**, and Track 2's `score.py` implements that hook
(`rests_on_notable`, "P8b F2 — COUNTED, and REPORTED"). **`score_t3.py` never reads
`potentially_notable_unmatched`.** It is present in `t3_fame.json` (19 mbids) and unused.
Six of them sit in DD-A2's scored C1 interiors and ten in DD-A3's:

```
DD-A2  藤澤慶昌, L'Entourloop, Paul St. Hilaire, Raj Ramayya, ellis, 黒沢ともよ
DD-A3  A Lull, 藤澤慶昌, Omar Perry, Degiheugi, Two Fingers, Lyricson,
       2econd Class Citizen, 黒沢ともよ
```

**Bounded, and the bound is reassuring.** I ran the strongest counterfactual the guard
could produce — every flagged artist reclassified as **as famous as a typical production
interior** (`F = 5.24`, the median matched interior F on P's C1 cells):

| arm | DD-C1 as scored | flagged dropped | flagged set to F = 5.24 | DD-C2 as scored → set to 5.24 |
|---|---|---|---|---|
| DD-A2 | −1.287 | −1.202 | **−1.160 (still ≤ −1.0)** | +0.644 → **+0.562 (still ≥ 0.5)** |
| DD-A3 | −1.923 | −1.796 | −1.657 | +0.364 → +0.342 |

**Verdict: CONFIRMED as a live false-pass channel, and CONFIRMED as non-decisive for
DD-A2.** The A11 guard is unimplemented in this scorer — a real omission against the
committed instrument — but discharging it cannot overturn DD-A2's DD-C1 or DD-C2 pass at
any owner verdict on those six names. What it *cannot* bound is the 29 unflagged unmatched
interiors in DD-A2's cells: A11's two flags (non-Latin script, foreign-language sitelink)
are the pre-registered detector, and this review does not re-open whether they are
sufficient.

**What would settle the remainder:** nothing offline. It is the owner's glance, and it is
already the pre-registered mechanism.

---

## DD-P3H-2 — DD-C2's d5 and d20 pools are drawn from different pair sets, and production's headline negative gradient flips sign under an equally defensible pooling. CONFIRMED, and it is an instability

**Claim checked (task items C and D).** DD-C2's pooled median, and whether the A13 uniform
drop is honoured.

**Derivation.** A13's drop is uniform **across arms** (verified clean — DD-P3H-7) but it is
not uniform **across depths**: the single dropped cell is `Openzone Bar -> Gjallarhorn@d20`,
so that pair contributes interiors to DD-C2's d5 pool and none to its d20 pool. DD-C2 is a
*difference of two pooled medians*, so a pair present on one side only shifts it directly.

DD-C2 under four pooling choices, all on the analysis set:

| arm | as scored | Openzone pair dropped at **both** depths | per-pair median, then median across pairs | both changes |
|---|---|---|---|---|
| **P** | **−0.158** | **+0.076** | −0.200 | −0.197 |
| DD-A1 | +0.275 | +0.353 | +0.278 | +0.326 |
| **DD-A2** | **+0.644 PASS** | +0.801 | +0.540 | +0.613 |
| DD-A3 | +0.364 | +0.411 | **+0.028** | +0.040 |

Three consequences, and they differ per arm:

1. **`REPORT.md`'s headline "Production fails DD-C2 in the negative direction: −0.158 — its
   middles get *more* famous as bypasses accumulate" is sign-unstable.** It is negative
   under three of four poolings and **positive under the fourth**, which differs from the
   scored one only by removing a pair that DD-C2 was already scoring asymmetrically. The
   direction is *supported*, at |0.076|–|0.200|; the specific claim "measured in fame
   currency on this pair set for the first time" is a real first, but the figure is well
   inside the choice-of-pooling spread.
2. **DD-A2's DD-C2 pass is robust** — 0.540 to 0.801 across all four, every one ≥ 0.5.
3. **DD-A3's DD-C2 figure is not stable at all** — 0.028 to 0.411, a 15× range. The
   execution log's mechanism story for the non-monotonicity ("at the strong dose the path
   is near-maximally obscure by d5") is consistent with all four, but the *size* of DD-A3's
   gradient is a property of the pooling as much as of the arm.

**Verdict: CONFIRMED.** The scorer honours the drop set exactly as written (a `None` cell is
skipped in both pools), so this is a design consequence of pooling a difference across
depths, not an implementation defect. **Fixable offline for free** by scoring DD-C2 on
pairs present at *both* d5 and d20 — but that is a change to a pre-registered statistic
after seeing the result, so it belongs in the record as a sensitivity, not as a
substitution. Reported as the sensitivity above.

---

## DD-P3H-3 — DD-C4 is computed over **all** hops; §5 says "interior hops". DD-A1's flag does not survive the literal reading. CONFIRMED, materially

**Claim checked (task item C).** §5: "Median per-hop similarity of **interior hops** at
d ≥ 10". `score_t3.py` uses `for i in range(len(p) - 1)` — every hop including the two
endpoint-adjacent ones — and its own comment says so ("every hop on the path"), as does
`REPORT.md`'s exposure map ("all hops, d ≥ 10"). So the deviation is disclosed, not hidden.

Measured both ways (interior-only = hops between two interior nodes, `i` in `1 … len-3`):

| arm | all hops | drop vs P | flag? | interior-only | drop vs P | flag? |
|---|---|---|---|---|---|---|
| P | 0.980 | — | — | **1.000** | — | — |
| DD-A1 | 0.837 | 0.143 | **FLAG** | 0.944 | **0.056** | **not flagged** |
| DD-A2 | 0.736 | 0.244 | FLAG | 0.802 | 0.198 | FLAG |
| DD-A3 | 0.583 | 0.397 | FLAG | 0.592 | 0.408 | FLAG |

**Verdict: CONFIRMED and material for exactly one arm.** `REPORT.md`'s "**all arms
flagged**" holds under the implemented reading and **fails under the literal §5 reading for
DD-A1** (0.056 against a 0.10 threshold). DD-A2 and DD-A3 flag either way, and DD-C4 gates
nothing by design, so no gate or read changes. Two further facts worth having:

- P's interior-only median is **exactly 1.000** — production's interior hops are
  ceiling-saturated, which is the same score-ceiling structure Track 2/2F's toll was aimed
  at. The endpoint-adjacent hops are what pull P's all-hop median to 0.980.
- Because P sits on the ceiling, the interior-only reading is the *stricter* statement of
  what the device costs in similarity for DD-A2 and DD-A3 (0.198 / 0.408, against 0.244 /
  0.397 measured), not a softer one.

---

## DD-P3H-4 — DD-C1's within-cell aggregator is the **mean**; Track 2's committed C1, whose threshold DD-C1 explicitly reuses, is the **median**. CONFIRMED; no verdict changes

**Claim checked (task item C).** §5: "Thresholds reuse Track 2's committed calibration
(band gap 1.093) — reused, not re-derived."

**Derivation.** `../2026-07-24-track2-arm-scorer/score.py` computes C1 from `cell_median`
(median of interior F within a cell), differences those against P, then takes the mean over
cells and tests `<= C1_MEAN_MAX = -1.0`. `score_t3.py` uses `statistics.mean` of interior F
within the cell, then the same outer mean and the same −1.0. The *outer* statistic and the
threshold constant are identical; the *inner* one is not. The mean is materially more
exposed to the `F = 0` floor than the median is (DD-P3H-1), which is why this is worth
stating rather than filing as style.

Recomputed with Track 2's inner statistic:

| arm | DD-C1 as scored (cell mean) | with Track 2's cell median | pass under either? |
|---|---|---|---|
| DD-A1 | −0.658 | −0.592 | no / no |
| DD-A2 | −1.287 | −1.317 | **yes / yes** |
| DD-A3 | −1.923 | −2.252 | yes / yes |

**Verdict: CONFIRMED as a deviation, with no consequence for any Track 3 verdict.** §5's
wording ("Paired **mean** ΔF") fixes the outer statistic and is silent on the inner one, so
the implementation is not contrary to the pre-registration; it is contrary to the script the
calibration was carried in. The negative-fraction test is unaffected (83 / 87 / 83 % under
the mean, and every arm's pass/fail is the same under the median).

---

## DD-P3H-5 — the device implementation matches §1 exactly, including DD-D7. CONFIRMED on all four sub-questions

**Claim checked (task item A).** A clean derivation, reported as a result.

1. **`k` is the right quantity.** `n_known = sum(1 for e in excludes if e.reason == KNOWN)`
   — the count of `known` exclusions carried into this request, computed once outside the
   search loop, identically to how `_relaxed_floor` counts them two lines above. On the
   all-`known` walk this equals the snapshot depth `d`, so "number of `known` bypasses so
   far" is exact. `k` is a request constant, not search state, so the folding is legitimate
   (already derived in DD-P3-11: this is a node potential, not a resource-constrained
   shortest path, and Dijkstra's correctness is preserved because the toll is non-negative).
2. **DD-D7 is honoured.** The term is inside the `for v, sim in store.neighbours_of(u)`
   loop, added to `cost` for the **relaxation target `v`**, before `nd = d + cost`. There is
   no node-settle branch anywhere in `_dijkstra` that could price a node absent from the
   returned path. Each interior on a simple path pays exactly once; the source is never a
   relaxation target on the returned path (`dist[source] = 0` and every cost is strictly
   positive, `w_hop = 0.02` unconditional).
3. **The target exemption is correctly placed.** `if ramp_on and v != target` guards the
   term itself, not the whole cost, so the exemption removes precisely the final in-hop and
   nothing else. It applies identically inside the guard-G masked re-run, which is the only
   other call site.
4. **Term order and the "live only" rule.** The ramp is appended **after** the six
   production terms and after the Track 2 `toll`, in its own `if`. Production's parenthesised
   six-term sum is textually and dynamically unchanged, so §1's byte-identity rule 1
   (float addition is not associative) is not disturbed.

**Verdict: CONFIRMED.** The diff (`git log -p -1 -- builder/analysis/2026-07-23-track2-sweep/mirror.py`)
adds 16 comment lines + 1 field, 5 lines in `_dijkstra`, 2 lines in the guard-G branch, and
touches nothing else. No committed Track 2 or 2F figure can move.

---

## DD-P3H-6 — the byte-identity argument is sound, and there is no path through `_dijkstra` where the ramp acts at k = 0. CONFIRMED, by derivation and by re-run

**Claim checked (task item B).**

**Derivation.** `ramp = cfg.w_known_ramp_pctl * n_known`; `ramp_on = ramp != 0.0`. At
`k = 0`, `ramp == 0.0` for every finite `w`, so `ramp_on` is `False` and Python's `and`
short-circuits before `ramp * pctl_v` is ever evaluated. The `cost` expression executed is
**the same expression object** production executes. This is strictly stronger than the
`x + 0.0 == x` argument I gave in DD-P3-2: that argument is also true here (every partial
sum is strictly positive), so the claim is over-determined. The only other added work at
k = 0 is the `n_known` sum, which has no side effect and does not touch `cost`, `dist`,
`prev` or the heap.

**Guard-G interaction, checked specifically.** `find_path_mirror` passes the same `cfg`,
`ctx` and `excludes` into the masked re-run, so `ramp_on` has the same value in both
Dijkstras of a single call. At d0 `excludes` is empty in both, so a guard-G re-run at d0 is
also byte-identical to P's. There is no ordering or state carried between the two runs. The
`stats["guard_fired"]` increment added in the same diff writes only to the stats dict.

**Measured, three ways:**

- **DD-G1 re-run** (`verify_mirror.py`, with the device field present and at its 0.0
  default): `cells compared: 212` … `BYTE-IDENTICAL on every cell. Gate passed.` The
  REPORT's 212/212 reproduces.
- **DD-G2 recheck** direct from `t3_paths.json`: **0** d0 differences over 16 pairs × 3
  ramp arms (48 comparisons), anchors included.
- **The device is demonstrably live from k = 1**, so DD-G2 is not passing because the knob
  is inert: d1 paths differ from P's on **11 / 16** pairs for DD-A1 and **12 / 16** for
  DD-A2 and DD-A3.

**Verdict: CONFIRMED.** DD-G2 holds by construction, the construction is the short-circuit
rather than floating-point luck, and the gate is not vacuous.

---

## DD-P3H-7 — the A13 uniform drop is applied and honoured; no arm-correlated missingness survives anywhere. CONFIRMED

**Claim checked (task item D).**

**Derivation.** `run_arms_t3.py` calls the committed `drop_infeasible_uniformly(per_arm)`
after all four arms are walked and before writing, in a **single invocation**, so the
`inherited` mechanism P8b F3 requires across a stage boundary is not needed and its absence
is correct. The function unions every `None` snapshot cell across all arms and then writes
`None` back into every arm. `score_t3.py` skips on `if not pa or not pp` and on
`if cell(...)`, which after the drop is arm-independent by construction.

**Measured, independently over the committed `t3_paths.json`:**

```
cells whose presence differs between arms: 0
missing cells (all arms): ['Openzone Bar -> Gjallarhorn@d20']
declared dropped_cells_d7: ['Openzone Bar -> Gjallarhorn@d20']
cells with a path but no interior (guard-G violation): 0
```

The last line closes the one residual channel: `walk` records a 2-node path *then* breaks,
so an empty-interior path at a snapshot depth would survive the drop and raise inside
`statistics.mean([])`. With guard G on this cannot arise (the masked re-run returns either
`None` or a path with ≥ 1 interior), and empirically it does not. `c1_n = 23 = 8 × 3 − 1`
in every arm, confirming the drop landed on exactly one cell in all four.

One derived note the REPORT does not make: the dropped cell's pair is an **analysis** pair,
which is what gives DD-P3H-2 its handle. It costs DD-C1 one of 24 cells (uniformly) and
costs DD-C2 one pair at d20 only (asymmetrically).

**Verdict: CONFIRMED for arm-correlation. The depth-correlation is real and is DD-P3H-2.**

---

## DD-P3H-8 — every headline figure reproduces exactly. CONFIRMED, no disagreement

**Claim checked (task item E).** Recomputed from `t3_paths.json` + `t3_fame.json` by an
independent route, no import of `score_t3.py`, independent percentile implementation.

| quantity | `REPORT.md` / `t3_scores.json` | recomputed here | agreement |
|---|---|---|---|
| DD-A2 DD-C1 | −1.2874208252745591 | −1.287 | exact to printed precision |
| DD-A2 DD-C1 negative fraction | 0.8695652173913043 (87 %) | 20/23 = 86.96 % | exact |
| DD-A2 DD-C2 | +0.644298662145828 | +0.644 | exact |
| DD-A2 DD-C5 per cell | 3.0869565217391304 | 3.09 (71/23) | exact |
| DD-A2 DD-C5 distinct | 59 | 59 | exact |
| DD-A2 DD-C6 | −5.739130434782608 | −5.74 | exact |
| DD-A2 DD-C4 (all hops) | 0.7360683679580688 | 0.736 | exact |
| DD-A3 DD-C1 / DD-C2 / DD-C6 | −1.923 / +0.364 / −6.52 | −1.923 / +0.364 / −6.52 | exact |
| DD-A1 DD-C1 / DD-C2 / DD-C6 | −0.658 / +0.275 / −4.35 | −0.658 / +0.275 / −4.35 | exact |
| P DD-C2 | −0.158 | −0.158 | exact |
| fame coverage | 710/832 = 85.3 % | 832 nodes, 0 missing from the fame table | exact |

**Verdict: CONFIRMED, zero disagreements.** Stating it plainly because a clean
reproduction is a result: the numbers in `t3_scores.json` are the numbers the definitions
in `score_t3.py` produce, and the numbers in `REPORT.md` are the numbers in
`t3_scores.json`.

---

## DD-P3H-9 — DD-C6 matches the definition adopted in the execution log, exactly. CONFIRMED

**Claim checked (task item C).** DD-D5's adopted text: "Mean interior count per arm vs P at
the same cell … An arm whose mean interior count falls more than **1.0** below P's is
flagged … and **DD-C1 may not be read as descent for a flagged arm**."

**Derivation.** The implementation accumulates `(len(pa) - 2) - (len(pp) - 2)` per cell and
means it. Because the cell set is identical for arm and P after the uniform drop, the mean
of paired differences **equals** (arm's mean interior count − P's mean interior count) — the
log's wording — identically, not approximately. The flag is `< -1.0`, strict, matching
"falls more than 1.0 below". The window is the C1 window, which is the window the qualifier
governs. `c6_mean_len_delta` for P is exactly 0, as it must be.

Track 2's C4 (`score.py::mean_count`) computes the two means over each source's *own*
feasible cells; Track 3's paired form is equivalent here and strictly safer if a drop were
ever missed. **Verdict: CONFIRMED.**

**One gap, stated as a fact and not a prescription:** DD-C6 covers DD-C1's window only.
DD-C2 reads d5 and d20 and has no length control, while the interior counts it pools move
sharply with the knob — P: d5 mean 12.12 → d20 14.57; DD-A2: 8.62 → 7.29; DD-A3: 6.12 →
7.14. That is DD-P3-8 (my protocol finding 8) **inherited in full by the implementation**,
which the next finding quantifies.

---

## DD-P3H-10 — DD-C2 inherits protocol finding 8's length bias; measured in fame units it is worth roughly a third of DD-A2's figure. CONFIRMED

**Claim checked (task item C).** "Does pooling across pairs of differing path length do what
§5 intends — state whether the implementation inherits the bias."

**Derivation.** `pooled_F(d)` concatenates every interior from every analysis pair at one
depth into a single list and takes one median, so pairs enter in proportion to their path
length — Track 2's `score.py::pooled`, reproduced. DD-P3-8 established (in percentile units)
that production's fame profile rises from the endpoints inward, so shortening alone moves a
pooled median downward with zero genuine descent.

The implementation inherits it in full. The length-unweighted control — per-pair median
first, then median across pairs — is in the DD-P3H-2 table: DD-A2 +0.644 → **+0.540**, a
0.104 reduction, ≈ 16 % of the figure; DD-A3 +0.364 → **+0.028**, ≈ 92 %. So for DD-A2 the
pass survives the control comfortably, and for DD-A3 essentially the whole gradient is a
pooling artefact.

**Verdict: CONFIRMED as inherited, quantified, and non-decisive for DD-A2's pass.** This is
the one place a Track 3 read (the non-monotonicity story) rests on a statistic that the
control substantially changes.

---

## DD-P3H-11 — "DD-P3 finding 10 did not materialise" is true, but for a reason of exposure rather than mechanism. CONFIRMED with a correction to the reading

**Claim checked.** `REPORT.md` and execution log §5: "Guard G fired 42 times in *every* arm
including P … Neither varies with the knob — so the one term §0 could not certify as
constant is constant in fact."

**Derivation.** I instrumented the walk directly rather than reading the totals. Guard G
fires on **exactly two pairs, at all 21 depths each** (2 × 21 = 42), in both P and DD-A3:

```
P      Radiohead -> The Beatles   guard fired 21/21 depths
P      Muse -> Coldplay           guard fired 21/21 depths      TOTAL 42
DD-A3  Radiohead -> The Beatles   guard fired 21/21 depths
DD-A3  Muse -> Coldplay           guard fired 21/21 depths      TOTAL 42
```

Both are **unscored all-famous anchors**, and both have adjacent endpoints (verified in the
CSR: `The Beatles` is in `Radiohead`'s neighbour row, `Coldplay` in `Muse`'s). No scored
pair is adjacent (DD-P3-3: unweighted min hops 4–8), so guard G has no scored pair it could
fire on at any `w`.

**Verdict: the invariance is CONFIRMED; the inference "so its activation is constant" is
CONFIRMED for this pair set and does not generalise.** Finding 10's mechanism — the device
makes the 2-node direct path uniquely toll-free, so guard G fires in arms where it does not
fire in P — is untested by this run, because the only pairs where it *could* be tested
already fire at every depth in every arm including P, and it is untestable on the scored
set, which contains no adjacent pair. The counting was still the right call: it converts an
assumption into a measurement, and it names its own scope.

---

## DD-P3H-12 — DD-C1's stability on the second slice. CONFIRMED, and reported because the instrument has reversed sign before

**Not asked**, but the standing instruction to check a difference reproduces on a second
slice before reporting it applies to the primary criterion, and the held-out half exists for
exactly this. Recomputed by the same route:

| arm | DD-C1, 8 analysis pairs (n = 23) | DD-C1, 4 held-out pairs (n = 12) |
|---|---|---|
| DD-A1 | −0.658, 83 % negative | −0.828, 100 % negative |
| **DD-A2** | **−1.287, 87 %** | **−1.258, 92 %** |
| DD-A3 | −1.923, 83 % | −1.703, 100 % |

**Verdict: CONFIRMED stable.** Same sign, same ordering in `w`, and DD-A2 within 0.03 log10
across the split. This is the opposite of the instrument behaviour the project has been
burned by before, and it is worth having on the record as such. It **gates nothing** — the
pre-registration reads no criterion off the held-out set (DD-D2), and turning a confirmation
set into a gate after seeing the analysis result is precisely what pre-registration
prevents. `score_t3_supplementary.py` computes the same table and states this itself; note
that its output file `t3_supplementary.json` is **not present in this directory**, so as of
this review the held-out figures exist only in that script's stdout and here.

---

## DD-P3H-13 — smaller confirmations and provenance notes

Each is clean unless stated; grouped because none is load-bearing on its own.

- **DD-C1's pairing is cell-wise against P, as specified, and the ≥ 75 % test is on the
  right quantity.** The negative fraction is computed over the *per-cell paired deltas*
  (`sum(1 for x in deltas if x < 0) / len(deltas)`), not over interiors and not over pairs
  — which is the only reading under which "% of cells negative" is well defined. **CONFIRMED.**
  Note that the pairing is by `(pair, depth)`, not by exclusion set: each arm is walked
  independently and bypasses its own victims, so at d ≥ 1 an arm and P hold *different*
  exclusion sets. That is the pre-registered Track 2 protocol (§0, "the walk is imported
  from the committed `run_arms.py`"), not a defect, but it means DD-C1 compares two
  journeys, not two routings of one journey.
- **DD-C5's pre-registered quantity is the *distinct* count; the REPORT's lead column is
  the per-cell mean.** §5: "**Distinct** interior artists below pctl 0.90 at d ≥ 10, per
  arm." `score_t3.py` computes both (`c5_distinct`, `c5_mean_per_cell`) and `REPORT.md`
  tabulates both, so nothing is hidden — but the column headed `DD-C5 /cell` (3.09 at
  DD-A2) is not the pre-registered statistic, and `c5_distinct` (59) is. Both reproduce
  exactly. The `pctl < 0.90` test is strict and in the same currency as DD-P1's, correctly.
  **CONFIRMED with a labelling note.**
- **DD-G4's second half is enforced and passes.** The scorer asserts no blank-named interior
  over all arms × scored pairs × all snapshots, and `t3_fame.json` reports
  `nameless_nodes: []`. Fame is keyed by mbid throughout (`F[mbids[str(n)]]`), with **832
  fame entries against 832 mbids in the paths file, 0 missing** — so no `KeyError` path and
  no silent default. **CONFIRMED.**
- **Endpoint resolution cannot have silently re-pointed a pair.** `run_arms_t3.py` resolves
  the pair-file's *names* by the highest-popularity-duplicate rule. One scored endpoint's
  name is shared by two nodes (`D`, in the held-out pair `Shirley Collins -> D`). I checked
  the resolved node's mbid against `pairs_v2.json`'s stored `src_mbid`/`dst_mbid` for all 24
  endpoints: **0 mismatches**. **CONFIRMED.**
- **DD-G3 is asserted in every script under review** (`run_arms_t3.py`, `score_t3.py`,
  `score_t3_supplementary.py`, and both probes here), and `run_arms_t3.py` additionally
  asserts `pairs_v2.json`'s artifact matches. `t3_paths.json` and `t3_scores.json` both
  record the sha256. **CONFIRMED.**
- **`score_t3.py` re-asserts DD-C3** (`assert paths["dd_g2_pass"]`), so a scoring run cannot
  proceed on a void walk. The DD-G2 check in `run_arms_t3.py` runs **before** the uniform
  drop, which is correct — d0 is never dropped, and checking after would be equally correct
  but for a weaker reason. **CONFIRMED.**
- **Provenance.** This directory's `README.md` does not yet list the two probe scripts added
  by this review (`dd_p3_harness_probes.py`, `dd_p3_harness_probes2.py`), nor
  `score_t3_supplementary.py`, which post-dates it. The 2026-07-23 defect-remediation spec
  §4.2 asks for that; I do not edit files under review, so this is left to the caller.

---

## Summary of verdicts

| # | item | verdict |
|---|---|---|
| 1 | DD-C1 could pass for a reason other than descent — the A11 `F = 0` floor | **CONFIRMED as a channel** (45 % of DD-A2's effect), **and bounded**: DD-A2 still passes under the strongest A11-guard counterfactual. `score_t3.py` does **not** read `potentially_notable_unmatched`, which Track 2's scorer does — 6 flagged artists sit in DD-A2's scored cells |
| 2 | DD-C2's pools are drawn from the same pair set at d5 and d20 | **REFUTED** — the A13 drop is at d20 only; P's headline −0.158 becomes **+0.076** if the pair is removed from both. DD-A2's pass robust (0.540–0.801); DD-A3's figure ranges 0.028–0.411 |
| 3 | DD-C4 computes §5's "interior hops" | **REFUTED** — it uses all hops (disclosed in code and REPORT). DD-A1's flag disappears under the literal reading (0.056 vs 0.10); DD-A2/A3 flag either way |
| 4 | DD-C1 reuses Track 2's committed C1 statistic | **REFUTED** — Track 2 uses the cell **median**, Track 3 the cell **mean**; same outer statistic and threshold. **No verdict changes** (DD-A2 −1.317 under the median) |
| 5 | `mirror.py` implements §1 exactly, `k` right, target exempt, live-only, DD-D7 | **CONFIRMED** on all four |
| 6 | byte-identity at k = 0 / DD-G2 by construction; guard-G re-run interaction | **CONFIRMED** by short-circuit derivation, by a DD-G1 re-run (212/212 byte-identical) and by 0/48 d0 differences — and the knob is demonstrably live at d1 (11–12 of 16 pairs) |
| 7 | A13's drop uniform across arms; no arm-correlated missingness | **CONFIRMED** — 0 cells differ in presence between arms; 0 empty-interior cells |
| 8 | the headline figures reproduce independently | **CONFIRMED** — DD-C1 −1.287, DD-C2 +0.644, DD-C5 3.09, DD-C6 −5.74 and every other cell, **zero disagreements** |
| 9 | DD-C6 matches the execution-log definition | **CONFIRMED** exactly; it covers DD-C1's window only, and DD-C2 has no length control |
| 10 | DD-C2 inherits protocol finding 8's length bias | **CONFIRMED**, worth 0.104 (16 %) of DD-A2's figure and 0.336 (92 %) of DD-A3's |
| 11 | guard-G invariance means finding 10 did not materialise | **CONFIRMED for this pair set**; the mechanism is untested — the only firing pairs are the 2 adjacent unscored anchors, and no scored pair is adjacent |
| 12 | DD-C1 reproduces on a second slice | **CONFIRMED** — held-out DD-A2 −1.258 against analysis −1.287 |
| 13 | DD-G4, DD-G3, endpoint resolution, DD-C5's statistic, DD-C1's pairing | **CONFIRMED**; DD-C5's lead column is the per-cell mean, not §5's distinct count (both reported) |

Nothing in this review is a recommendation about whether to adopt DD-A2, whether to spend a
blind listen, or how the owner should weigh WGLL values 1 and 2 against each other.
