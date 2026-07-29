# TB-P5 — harness review of the Track 3b run

Artifact: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 verified
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted by all three
probes. Measured off that artifact: **N = 74,193 nodes, 898,006 directed CSR entries
(449,003 undirected edges), degree mean 12.10 / median 9 / p99 44 / max 50.**

Derivation only, per the agent's remit. Nothing here says whether any arm should be
adopted, whether a listen should be spent, or which candidate is better. §7's reads are
stated **mechanically** from the amended definitions and the verified figures; the verdict
is not mine to take.

Probes (all in this directory, all assert the sha256):

| script | what it does | writes |
|---|---|---|
| `tb_p5_probe_rewalk.py` | re-implements production's cost from `ApiConfig` + `pathfinding.py` **plus the pre-registration §1 text for the device**, its own average-rank percentile, its own Dijkstra, and its own all-`known` walk and victim rule; re-walks all 4 arms × 12 scored pairs × 21 depths and compares against `tb_paths.json` | `tb_p5_rewalk.json` |
| `tb_p5_probe_rescore.py` | recomputes every headline figure in `tb_scores.json` from `tb_paths.json` + `tb_fame.json` **without importing `score_tb.py`** (numpy medians, different loop structure), plus per-pair spread, leave-one-pair-out, thin-pair cells, TB-C6 cell-median variant, A11 shares | `tb_p5_rescore.json` |
| `tb_p5_probe_aux.py` | A11 flag list vs each row's own guard; degree top-1 % sizing; the counterfactual family; the TB-C2 pooling family; ceiling cell set vs arms' cell set; TB-C4 saturation | `tb_p5_aux.json` |

**Headline reproduction result, stated first because a clean reproduction is a result:
86 figures compared, maximum absolute discrepancy 2.220 × 10⁻¹⁶** (`TB-A3.c1_all.mean`;
next 1.11 × 10⁻¹⁶, then 5.55 × 10⁻¹⁷, then exact zeros). Every discrepancy is
floating-point summation order. **And 0 path mismatches out of 432 snapshot cells** in the
independent re-walk, with the victim counters matching exactly including the by-depth
vectors. The numbers in `tb_scores.json` are the numbers the amended definitions produce,
and the paths they were computed from are the paths the device as specified produces.

---

## TB-P5H-1 (HIGH) — TB-A2's TB-C1 pass is carried by two of eight pairs; removing either one on its own sinks it

**Claim checked.** §3's table: `TB-A2 … −1.080 … PASS`, and TB-C1's own second clause
("this holds across most journeys rather than being bought by a few"), which the ≥ 75 %
negative-cell condition is supposed to enforce.

**What I did.** `tb_p5_probe_rescore.py` — per-pair mean of the three C1-window cell
deltas, and leave-one-pair-out on the primary statistic.

| pair | TB-A2 per-pair mean | TB-A2 primary with this pair removed | still passes? |
|---|---|---|---|
| `Tails -> Fingers Inc.` | **−2.174** | **−0.924** | **NO** |
| `钟茌 -> The Koolaid Electric Company` | **−2.308** | **−0.905** | **NO** |
| `Mikey Murka -> Disiz` | −1.311 | −1.047 | yes |
| `The Mills Brothers -> Tracey Chattaway` | −1.118 | −1.075 | yes |
| `Jenny Owen Youngs -> 洲崎綾` | −1.010 | −1.090 | yes |
| `Daniel Avery -> Rita Marley` | −0.686 | −1.136 | yes |
| `Patti Smith -> Daniel Herskedal` | −0.041 | −1.228 | yes |
| `Openzone Bar -> Gjallarhorn` | +0.007 | −1.235 | yes |

TB-A2's pass margin is **0.080** on the primary and **0.040** on the counterfactual. Two of
eight pairs each individually account for more than that margin.

**The contrast, and it is the point.** TB-A3's pass is robust: its worst leave-one-out is
**−1.334** (removing `Tails -> Fingers Inc.`), every one of the eight clears −1.0, and its
counterfactual margin is 0.375. So the fragility is specific to TB-A2, not to the
instrument.

**Why the pre-registered guard did not catch it.** TB-C1's ≥ 75 % condition constrains the
*sign* of cells, not the *concentration of magnitude*. TB-A2 is negative on 87.5 % of
cells and still fails to survive the removal of either of two pairs, because two pairs
carry roughly twice the mean effect. That is not a defect in the harness — the harness
implements the criterion exactly — it is a property of the criterion that the record must
carry beside the figure.

**Not a finding about which read fires.** TB-A3 passes TB-C1 robustly, so the TB-C1 pass
set is non-empty under any leave-one-pair-out. §7's mechanics are unaffected (see
TB-P5H-8).

---

## TB-P5H-2 (HIGH) — TB-C2 is pooling-unstable across the threshold, and the primary and the secondary variant order the ladder in opposite directions

**Claim checked.** §6 TB-C2's pre-committed pooling and its "pooled variant reported beside
it, labelled secondary"; TB-P1 clean rows 13–14, which certified the *A13-drop* asymmetry
removed. With zero drops this run, that certification holds — **and it was not the only
source of instability.**

**What I did.** `tb_p5_probe_aux.py` — TB-C2 under the four poolings DD-P3H-2 used, adapted
to this run (with zero A13 drops, "drop the asymmetric pair at both depths" collapses onto
"as scored", so the family is {per-pair, pooled} × {median, mean}).

| arm | per-pair median (**PRIMARY**) | per-pair mean | pooled median (**secondary, printed**) | pooled mean | range | passes ≥ 0.5 under |
|---|---|---|---|---|---|---|
| P | +0.015 | −0.076 | −0.048 | −0.026 | 0.09 | — |
| TB-A1 | **+0.626 PASS** | +0.541 | +0.352 | +0.593 | **0.352–0.626** | primary, per-pair mean, pooled mean |
| TB-A2 | +0.475 | +0.466 | +0.457 | +0.446 | 0.446–0.475 | **none — stable fail** |
| TB-A3 | +0.213 | +0.332 | +0.485 | **+0.549** | **0.213–0.549** | pooled mean only |

Three things follow, and they differ from Track 3's version of this finding.

1. **The ladder ordering reverses between the primary and the variant printed next to
   it.** Primary: 0.626 → 0.475 → 0.213, strictly decreasing in `w`. Pooled median:
   0.352 → 0.457 → 0.485, strictly *increasing* in `w`. Under the primary the weakest
   gradient is at the top rung; under the secondary the strongest is. Both are in the
   table in `tb_scores.json` and in execution-log §3, side by side, with no note that they
   disagree about which way the ladder runs.
2. **The pass set is pooling-dependent for two of three arms.** {TB-A1} under the primary,
   {} under the pooled median, {TB-A1, TB-A3} under the pooled mean. TB-A3's figure spans
   the threshold by a factor of 2.6.
3. **TB-A2's TB-C2 failure is the one stable result here** — 0.446 to 0.475 across all
   four, every one below 0.5, margin 0.025 on the primary. Its failure is robust; its
   *nearness* to the threshold is real and should be stated as 0.475 against 0.500, not as
   "misses".

**Structural cause, since it is not the DD-P3H-2 cause.** The primary weights each pair
once regardless of how many interiors it contributes; the pooled variants weight by
interior count, and interior counts differ by a factor of several between arms at d5 and
d20 (TB-C6: TB-A3 runs 4.4 interiors shorter than P at d5 and 5.6 shorter in the C1
window). So a length change re-weights the pooled statistic and not the per-pair one. This
is DD-P3H-9's within-cell half, which TB-P1 F7 flagged and the §6 amendment addressed for
TB-C6's *window* — it is not addressed for TB-C2's *pooling*, and it does not need to be:
the primary is pre-committed and the primary is the length-insensitive one. The finding is
that the secondary should not be read as corroboration when it inverts the ordering.

**Does it change §7?** No — see TB-P5H-8. Even under the pooling most favourable to a
mechanism claim (pooled mean, where TB-A3 passes TB-C1 *and* TB-C2), TB-A3 is TB-C6-flagged
in both windows, and TB-R1 requires TB-C6 unflagged. **The read is insensitive to the
entire TB-C2 pooling family.** That is worth stating explicitly, because it is the strongest
thing that can be said about the stability of this run's outcome.

---

## TB-P5H-3 (MED) — execution-log §3's "the gradient is non-monotone in `w` again" does not describe the primary statistic, and "again" mis-states the continuity with Track 3

**Claim checked.** Execution log §3: "The gradient is **non-monotone in `w`** again — at
strength the path is near-maximally obscure by d5".

**Measured.** TB-C2's primary across the three arms is **0.626 → 0.475 → 0.213: strictly
monotone decreasing.** Including P (0.015) the four-point sequence is single-peaked at the
*lowest* rung. Track 3's DD-C2 was 0.275 → 0.644 → 0.364, peaked at the *middle* rung —
genuinely non-monotone among its arms. The two shapes are different, so "again" asserts a
continuity the figures do not have.

The mechanism sentence attached to it ("at strength the path is near-maximally obscure by
d5") is *better* supported by the correct shape than by the stated one: monotone decay in
`w` is exactly what running out of headroom at d5 predicts, and it is corroborated
independently by TB-C6's d5 window (0 → −1.00 → −2.88 → −4.38) and by the sub-decile
victim counter (0 → 3 → 14 → 56). The defect is the word, not the story.

**Amendable as:** "The gradient falls monotonically with `w` across the three arms
(0.626 / 0.475 / 0.213) — the opposite of Track 3's mid-rung peak — consistent with the
path being near-maximally obscure by d5 at strength."

---

## TB-P5H-4 (MED) — the TB-P3 ceiling gate and the arms are scored on different cell sets: 23 against 24

**Claim checked.** Execution log §2: "mean over 23 analysis C1-window cells"; "18/23 cells
clear individually"; "5 of the 23 cells cannot individually clear −1.0 even at the limit".
And §3: "**Zero A13 drops** — … all 24 C1-window analysis cells score."

**Derivation.** `tb_p3_ceiling.py` reads `dropped_cells_d7` from **Track 3's**
`t3_paths.json` (line 86) and skips those cells. TB's own run dropped nothing. Confirmed by
set difference in `tb_p5_probe_aux.py`:

```
ceiling cells 23 · arms scored cells 24
in arms, not in ceiling: ["Openzone Bar -> Gjallarhorn@d20"]
in ceiling, not in arms: []
arms' own dropped set: []
```

**Materiality.** Immaterial to the gate itself: the gate passes at −2.554 against −1.0, and
no plausible value for the 24th cell moves a 23-cell mean by 1.5 log10. It *is* material to
every "of the 23" statement in the record, because those denominators are now one cell away
from the set the criteria score, and the missing cell belongs to one of the two
thin-headroom pairs the same section singles out — i.e. the omission is in the direction
that flatters the ceiling, however slightly.

**Amendable as:** state the ceiling's denominator as "23 of the 24 scored cells — the
ceiling probe inherited Track 3's drop set, which TB's own run does not have".

---

## TB-P5H-5 (MED) — the ceiling is not a per-cell upper bound on an arm, and the arms cross it on up to 7 of 23 cells

**Claim checked.** Execution log §2: "5 of the 23 cells cannot individually clear −1.0 even
at the limit, so a per-cell read of any arm must not treat those cells as failures of the
device."

**Derivation.** TB-P1 F3 item 4 recorded, in advance, that the ceiling is computed under
**P's** exclusion sets while each arm bypasses its own victims, so it is "the limit at the
exclusion state production would have been in", not the limit of the arm's own walk. That
is now measurable. Comparing each arm's TB-C1 cell delta against the ceiling's own
cell-median gap at the same cell:

| arm | cells where the arm is **more obscure than the ceiling** |
|---|---|
| TB-A1 | 1 / 23 |
| TB-A2 | 2 / 23 |
| **TB-A3** | **7 / 23** |

Worked example: `Openzone Bar -> Gjallarhorn@d10` — ceiling −1.177, TB-A3 −1.801.

**Consequence, symmetrical to the one the log states.** The log's caution is correct in the
direction it is written (a cell the ceiling cannot clear is not an arm's failure). The
converse is now also on record and is *not* stated: the ceiling is not a per-cell ceiling,
so an arm exceeding it is not an anomaly and the ceiling may not be used as a per-cell
upper bound on what the device can deliver. Both halves come from the same fact — the
exclusion sets differ — and only one is written down.

---

## TB-P5H-6 (MED) — TB-C1(i)'s counterfactual bounds 18.5 % of the unmatched mass; the exposure it does not bound is where the pass lives

**Claim checked.** §6 TB-C1(i): "reclassifying every `potentially_notable_unmatched`
interior as a production-typical famous artist … the arm still passes", and TB-G4's
requirement that the scorer *read* the A11 flag.

**Verified first:** the flag list in `tb_fame.json` is exactly the set derivable from each
row's own `guard.potentially_notable` (**20 = 20, identical, 0 unmatched rows lacking a
guard block**), and `score_tb.py` reads it (line 81) and reports it per arm. TB-G4's
deferral is genuinely discharged. The counterfactual constant reproduces exactly:
**5.229561543744921**, from a pool of **299 matched P interior occurrences** across the 24
C1-window analysis cells — which is TB-P1 F13's specification (analysis pairs, C1-window,
matched rows only) exactly. The all-interior median, which F13 ruled out, is 5.120.

**But the flag covers 20 of 108 unmatched artists — 18.5 %.** The A11 encoding floors the
other 81.5 % at F = 0 with no guard. Measured exposure, occurrence-weighted over each arm's
scored interiors:

| arm | scored interior occurrences | unmatched | unmatched % | of which A11-flagged |
|---|---|---|---|---|
| P | 322 | 23 | 7.1 % | 4 |
| TB-A1 | 234 | 26 | 11.1 % | 4 |
| TB-A2 | 203 | 31 | 15.3 % | 6 |
| **TB-A3** | 187 | **45** | **24.1 %** | 10 |

The DD-D8 pattern the execution log names is confirmed and quantified: the unmatched share
**rises monotonically with dose**, and at TB-A3 nearly a quarter of what is scored sits on
the fame floor.

**The counterfactual family, so the guard's reach is visible:**

| arm | primary | (i) as pre-registered (flagged only) | shift | **all unmatched reclassified** (NOT a criterion) | shift | matched-only |
|---|---|---|---|---|---|---|
| TB-A1 | −0.554 | −0.471 | 0.083 | −0.229 | 0.325 | −0.372 |
| TB-A2 | **−1.080** | **−1.040** | **0.040** | −0.577 | 0.503 | −0.769 |
| TB-A3 | **−1.709** | **−1.375** | 0.334 | −0.734 | 0.975 | −1.068 |

**Reading it correctly, and the limits on it.** Condition (i) moves TB-A2 by 0.040 — it is
close to inert on the arm whose margin is smallest. The right-hand columns are a
**sensitivity, not a criterion**: the unmatched → floor encoding is the owner's adopted
decision, §0 says so, and TB-C1's primary is all-interiors deliberately because "an
unmatched artist genuinely is reach". The pre-registered instruments for this exposure are
(i) — which both passing arms clear — and the matched-only report, which is why TB-C1(ii)
exists and why it correctly fires on TB-A2 and correctly does not fire on TB-A3
(−1.068). Nothing here overturns a criterion. What it adds is the size of the thing (ii)'s
fixed wording is pointing at.

---

## TB-P5H-7 (MED) — no §7 read consumes TB-C2's failure by the TB-C1-passing arms

**Claim checked.** §7 TB-R2's letter: "If arms pass TB-C1 but **every** passing arm is
TB-C6-flagged".

TB-R2 conditions on TB-C1 and TB-C6 only. Both TB-C1-passing arms *also* miss TB-C2
(0.475 and 0.213 against 0.500). TB-R2's condition is satisfied on the letter and its fixed
reading ("even with obscure interiors toll-free, the router prefers dropping famous
interiors to replacing them") is not contradicted by the TB-C2 miss — but TB-C2 gates
nothing except TB-R1, so a run in which the passing arms fail it reads identically to one in
which they pass it. That is a real gap in the read structure, and it is the same shape as
the gate-without-an-effect-size problem CLAUDE.md records against Track 2.

**Not amendable now** — amending a read after seeing the table is exactly what
pre-registration prevents. The remedy is to **state the TB-C2 miss explicitly in the record
alongside TB-R2**, and to carry it as a design item for any successor pre-registration.

---

## TB-P5H-8 (LOW) — two letter-level ambiguities in §7, neither of which changes which read fires

**(a) TB-R1's "passes TB-C1 (with both robustness conditions)".** Condition (i) is a
pass/fail test; condition (ii) is an *obligation triggered by a state* ("every statement of
the pass carries this fixed wording"), not a test that can hold or fail. `score_tb.py`
implements `c1_pass = c1_all.pass and c1_counterfactual.pass` and reports (ii) separately,
which is the reading the amended §6 supports. Under the alternative reading — "(ii) must
not fire" — TB-A2 leaves the TB-C1 pass set, and **the outcome is unchanged**: TB-A3 still
passes TB-C1, is still TB-C6-flagged, TB-R1 still fails, TB-R2 still fires.

**(b) TB-R2 vs TB-R0 exclusivity.** Not an issue on these figures: TB-R0 requires no arm
past −0.3 and all three arms are past it (−0.554 / −1.080 / −1.709), so only one read's
condition is satisfiable.

---

## TB-P5H-9 (LOW) — P's TB-C4 baseline of exactly 1.000 sits on a 50.34 % / 49.66 % split

`tb_p5_probe_rescore.py`: P's interior hops number **298, of which 150 (50.34 %) are at
similarity exactly 1.0**; median 1.000, mean 0.926. The log calls this "ceiling-saturated"
and reproduces DD-P3H's side fact, which is correct — but the median is at a step
discontinuity, and a pair set giving 148 rather than 150 would report a visibly lower P
baseline against which every arm's drop is measured. Saturation by arm: P 50.3 % →
TB-A1 28.1 % → TB-A2 4.5 % → TB-A3 0.6 %. TB-C4 gates nothing by design (§6), so this
constrains wording only.

---

## TB-P5H-10 (LOW) — TB-C5(b)'s degree cut selects 1.27 % of nodes, not 1 %

`top_degree_cut = np.percentile(degree, 99.0) = 44.0` reproduces exactly, but degree is
integer and 44 is a tied value: **940 nodes have degree ≥ 44 = 1.27 % of N = 74,193**
(median degree 9, max 50). The set is therefore slightly *larger* than top-1 %-by-degree, so
the diagnostic is generous — TB-A3's count of **0** distinct top-degree interiors is if
anything a stronger statement than a strict 1 % cut would give, and P's 24 is marginally
inflated. Direction is safe; the label "top-1 %-by-degree" is approximate.

---

## TB-P5H-11 (LOW) — TB-A1's d5 TB-C6 is exactly −1.0, on both statistics, and correctly unflagged

Asked specifically. The eight per-cell interior-count deltas at d5 are
`[1, −3, −2, 1, −3, 0, −2, 0]`, summing to −8: **the mean is exactly −1.0**
(`repr` = `'-1.0'`, integer arithmetic, no rounding). §6's flag is "falling **more than**
1.0 below P", implemented as `< -1.0` — strict — so TB-A1 is **not** flagged by the d5
window. **The cell-median variant is also exactly −1.0** (sorted deltas
`[−3,−3,−2,−2,0,0,1,1]`, median = (−2 + 0)/2), so the flag state does not change under it
either. TB-A1 is flagged regardless via the C1 window: mean −3.667, cell-median −4.000.
Execution-log §3's parenthetical is accurate as written.

---

## TB-P5H-12 (LOW) — the victim counter's denominator is 240, TB-P1's baseline figure was /252

`run_arms_tb.py` counts victims over depths 0–19 (`[:MAX_DEPTH]`) — the victims that
actually took effect — giving **240 = 12 pairs × 20**. TB-P1 F4's headline "0/252 of
production's victims are sub-decile" counted all 21 walk iterations, including the final
victim the walk computes and never uses. Both give 0 for P, so nothing is wrong; the
denominators simply differ, and `0/252` should not be set beside `56/240` as though they
shared one. My re-walk reproduces `run_arms_tb.py`'s convention exactly, by-depth.

---

## The two thin-headroom pairs, cell by cell

Asked for. TB-C1 cell deltas (cell-median form, arm − P):

| cell | ceiling (median form) | TB-A1 | TB-A2 | TB-A3 |
|---|---|---|---|---|
| `Patti Smith -> Daniel Herskedal@d10` | −0.639 | −0.421 | −0.280 | −0.415 |
| `Patti Smith -> Daniel Herskedal@d15` | −0.043 | **+0.784** | **+0.784** | **+0.288** |
| `Patti Smith -> Daniel Herskedal@d20` | −0.845 | −0.114 | −0.627 | −0.912 |
| `Openzone Bar -> Gjallarhorn@d10` | −1.177 | **+0.230** | **+0.014** | −1.801 |
| `Openzone Bar -> Gjallarhorn@d15` | −1.410 | −3.078 | **+0.021** | −0.860 |
| `Openzone Bar -> Gjallarhorn@d20` | *(not in ceiling set — TB-P5H-4)* | **+0.013** | −0.014 | −1.473 |

Per-pair means: `Patti Smith` +0.083 / −0.041 / −0.347 across TB-A1/A2/A3;
`Openzone Bar` −0.945 / +0.007 / −1.378. Both pairs are near-inert for TB-A2 and both are
among the pairs whose *removal* strengthens TB-A2's primary (TB-P5H-1's right-hand column),
so they are not what carries any pass. `Openzone Bar@d15` under TB-A1 (−3.078) is the single
largest negative cell in the TB-A1 table and is 3.3× TB-A1's own mean — worth knowing before
anyone reads TB-A1's −0.554 as an evenly-spread small effect.

---

## Question 7 — which pre-registered read fires, mechanically

Stated from the amended §7's definitions and the figures verified above. **No
interpretation; the verdict is the owner's.**

| read | condition, as written | evaluated | holds? |
|---|---|---|---|
| **TB-R3** | TB-P3(a) fails to clear −1.0; arms not run | gate passed at −2.554 (median form −2.889); arms ran | **no** |
| **TB-R1** | ≥ 1 arm passes TB-C1 (both robustness conditions) **and** TB-C2, TB-C3 holding, **TB-C6 unflagged** | TB-C1 pass set {TB-A2, TB-A3}; TB-C2 pass set {TB-A1}; **intersection empty**; and TB-C6 flags all three arms in both windows | **no** (fails twice over) |
| **TB-R2** | arms pass TB-C1 but **every** passing arm is TB-C6-flagged | TB-A2 and TB-A3 pass TB-C1 (all-interiors −1.080 / −1.709 at 87.5 % / 95.8 % negative, counterfactual −1.040 / −1.375); both TB-C6-flagged (C1 window −4.96 / −5.63; d5 −2.88 / −4.38) | **YES** |
| **TB-R0** | no arm moves TB-C1 past −0.3 | −0.554 / −1.080 / −1.709 — all past −0.3 | **no** |

**Exactly one read's condition is satisfied: TB-R2.** TB-C3 holds independently verified
(TB-G2: d0 byte-identical to P on all 16 pairs for all three arms; non-vacuity: d1 differs
from P on 11 / 11 / 12 of 16 pairs, 9 / 9 / 10 of the 12 scored pairs).

**Ambiguity in the letter:** two, both in TB-P5H-8, **neither changes the answer**. And the
answer is insensitive to the whole TB-C2 pooling family (TB-P5H-2): even under the pooling
where TB-A3 passes both TB-C1 and TB-C2, TB-C6 flags it and TB-R1 remains unavailable.
**One thing the reads do not consume:** both TB-C1-passing arms also fail TB-C2, and no §7
read reads that (TB-P5H-7) — it should be stated explicitly rather than left in the table.

---

## Verified clean — checked and found correct, so silence is distinguishable from an unchecked claim

| # | claim | how checked | verdict |
|---|---|---|---|
| 1 | The device is `w · k · max(0, pctl(v) − 0.90)` on the relaxation target | `mirror.py:294-296`, inside the `for v, sim in store.neighbours_of(u)` loop | **CONFIRMED** |
| 2 | Destination exempt | `if thresh_on and v != target` | **CONFIRMED**. Source is not exempt and does not need to be: `dist[source] = 0` is never improved |
| 3 | Added only when live, never as `+ 0.0` | `thresh = cfg.w_known_thresh_pctl * n_known; thresh_on = thresh != 0.0` — at k = 0 or w = 0 the term is not executed | **CONFIRMED**; TB-G2 holds by construction, not by float luck |
| 4 | `k` = the `known` count | `n_known = sum(1 for e in excludes if e.reason == KNOWN)`, hoisted out of the loop as a request constant | **CONFIRMED** |
| 5 | Knee constant is 0.90 | `KNOWN_THRESH_PCTL_KNEE = 0.90` (`mirror.py:43`), used only at line 296 | **CONFIRMED** |
| 6 | **No node-settle branch exists** | grep for `thresh` in `mirror.py` returns lines 43, 113–119 (config + comment), 232–234 (hoist), 294–296 (relaxation). Nothing at heap-pop | **CONFIRMED** — DD-D7 honoured |
| 7 | Track 3's sibling knob stays off | `w_known_ramp_pctl` default 0.0, set by no TB config; `ramp_on` False in all four arms | **CONFIRMED** (§0 row per TB-P1 F6) |
| 8 | `SweepConfig.production()` unchanged | returns `cls()`, both device fields default 0.0 — every committed Track 2/2F/3 figure still reproduces from this file | **CONFIRMED** |
| 9 | **The whole run reproduces from an independent implementation** | `tb_p5_probe_rewalk.py`: own percentile (unique-value grouping, not the sort-scan), own Dijkstra, own cost from `ApiConfig` + `pathfinding.py`, own walk and victim rule — **0/432 snapshot-path mismatches** across 4 arms × 12 scored pairs × 9 depths | **CONFIRMED, zero disagreements** |
| 10 | pctl definition | my route equals `MirrorContext.build`'s array-for-array on all 74,193 nodes | **CONFIRMED** |
| 11 | Victim rule and its counter | `min(interior, key=(-pop_raw, node_id))` in `run_arms.walk`, reproduced in `run_arms_tb.py`'s counter; my re-walk matches **totals and by-depth vectors exactly**: 0 / 3 / 14 / 56 of 240 | **CONFIRMED** |
| 12 | Guard G never fires on a scored pair | my re-walk counts len-2 paths on all 12 scored pairs × 21 depths × 4 arms: **0**. The runner's 42 firings per arm = 2 adjacent anchors × 21 depths, exactly | **CONFIRMED** — §0's "an activation on a scored pair is an anomaly" had nothing to report |
| 13 | TB-G2 and its non-vacuity | recomputed from `tb_paths.json` independently of the runner's own print: d0 differing pairs **[] for all three arms**; d1 differing 11 / 11 / 12 of 16 | **CONFIRMED**, matches §3's "11–12" |
| 14 | TB-C1's cell statistic is Track 2's `cell_median` form | `statistics.median(fa) - statistics.median(fp)` per cell, `mean` over cells, tested `<= -1.0` and `neg >= 0.75` | **CONFIRMED** — TB-P1 F12(b) honoured |
| 15 | TB-C1 all / matched / counterfactual reproduce | all 12 arm × variant figures, max discrepancy 2.2e-16 | **REPRODUCES EXACTLY** |
| 16 | The counterfactual constant's pool | analysis pairs, C1-window cells, **matched rows only**, P's paths — n = 299 occurrences, median **5.229561543744921** = committed | **REPRODUCES EXACTLY**; TB-P1 F13 honoured (all-interior median would have been 5.120) |
| 17 | TB-C1(ii)'s trigger | fires iff primary passes and matched-only does not: TB-A2 only. Verbatim wording present in `score_tb.py` and in the log | **CONFIRMED** |
| 18 | TB-C2's primary form | per pair present at **both** d5 and d20, `median F(d5) − median F(d20)`, statistic = median over pairs, `>= 0.5` | **CONFIRMED** — matches the amended §6 exactly |
| 19 | `pooled()` conditions on the same pair set at both depths | `if cell(arm,pair,d) and cell(arm,pair,5) and cell(arm,pair,20)` — the DD-P3H-2 remedy, applied. **Differs from Track 3's pooling**, which did not condition | **CONFIRMED**, and it is the fix DD-P3H-2 asked for |
| 20 | **n = 8 pairs everywhere** with zero A13 drops | `c2_n_pairs = 8` in all four arms; TB-C1 `n = 24` in all four arms and all three variants; `dropped_cells_d7 = []` | **CONFIRMED** |
| 21 | TB-C4 is over **interior hops only** | `for i in range(1, len(p) - 2)` on paths with `len >= 4` — both ends interiors. DD-P3H-3's disclosed variant resolved in favour of the stated design | **CONFIRMED**; medians 1.000 / 0.947 / 0.807 / 0.670 reproduce exactly |
| 22 | TB-C5(a) and (b) reproduce | per-cell means 1.54 / 2.00 / 4.00 / 6.08; distinct sub-decile 16 / 25 / 69 / 129; degree counts 24 / 12 / 6 / 0 | **REPRODUCE EXACTLY** |
| 23 | TB-C6 covers **both** windows | `len_deltas(C1_DEPTHS)` and `len_deltas((5,))`, flag if either `< -1.0` | **CONFIRMED** — TB-P1 F7 honoured |
| 24 | The fame join is mbid-keyed end to end | `node_mbids` → `fame` / `rows`; **802 distinct scored interior nodes, 0 mbids missing from the fame table**; 0 duplicate mbids across node ids | **CONFIRMED** |
| 25 | TB-G4's blank-name assertion | **0 blank-named nodes anywhere** in `tb_paths.json`'s 893 nodes, and `nameless_nodes = []` in `tb_fame.json`. The assertion is correctly written and had nothing to catch | **CONFIRMED, and non-vacuous in form** — it would fire; the population is clean |
| 26 | The A11 flag is read, and the list is the table's own | `score_tb.py:81` reads it; the 20 mbids are **exactly** the rows whose `guard.potentially_notable` is true; 0 unmatched rows lack a guard block | **CONFIRMED** |
| 27 | TB-C3 / TB-G2 re-asserted at score time | `assert paths["tb_g2_pass"]` before any figure | **CONFIRMED** |
| 28 | The floor is inert at every scored depth | my re-walk implements the floor and reproduces every path; `floor_active` is nonzero only via d1–d2, as TB-P1 F5 predicted | **CONFIRMED** |
| 29 | Runner and scorer are new modules importing committed code | `run_arms_tb.py` imports `walk`, `drop_infeasible_uniformly`, `MAX_DEPTH`, `SNAPSHOTS`, `find_path_mirror`; no committed Track 2/3 file edited except `mirror.py`'s additive term | **CONFIRMED** |
| 30 | TB-P1 F15's README exists and is accurate | `README.md` present, script table matches the files on disk, currency notice present | **CONFIRMED** (its "How to run" block lists the TB-P1 probes only — cosmetic) |
| 31 | The output filename guard | `in_dir()` rejects anything but a bare filename in the analysis directory | **CONFIRMED** |
| 32 | TB-A2's TB-C2 near-miss is real, not a rounding artefact | 0.4752957695996227 against 0.5; median of 8 = mean of the 4th and 5th sorted per-pair deltas (0.2941, 0.6565); stable 0.446–0.475 across all four poolings | **CONFIRMED** — margin 0.0247, and the *failure* is robust |

---

## What TB-P5 does **not** cover

- **TB-G1** (mirror vs shipped `find_path` with the device off) was re-earned by the
  session at 212/212 and I did not re-run it as such. My re-walk is a partial independent
  substitute: it implements production's cost from `pathfinding.py` + `ApiConfig` and
  reproduces the P arm on 108/108 scored-pair snapshot cells.
- **The four anchor pairs** were not re-walked (they are descriptive, gate nothing, and
  carry 4/16 of the runtime). Their d0 identity *is* verified from `tb_paths.json`.
- **The A11 fetch itself** — I verified the join, the keying, the flag derivation and the
  coverage, not the pageview values, which come from the committed instrument.
- **Anything about whether a candidate should be adopted, listened to, or shipped.** Out of
  remit by design.
