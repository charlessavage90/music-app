# ml-graph-analyst critique of the CRE pre-registration — as delivered, 2026-08-03

**Provenance:** produced by the `ml-graph-analyst` subagent, dispatched 2026-08-03 at
the owner's instruction, against the pre-registration as first committed
(`c047d06` + same-day self-review fixes), before any CRE arm was built or run.
Reproduced verbatim below; probe scripts are committed beside this file. **This file
owns the figures it states.** The prereg's §9 records which proposals were adopted,
adjusted, or declined — where they differ, the prereg governs the design and this file
remains the record of what was measured and proposed.

---

**Artifacts, sha256 verified before every read** (`sha256sum`):
- `builder/scratch/graph-t15-tiebreakfix.bin` = `4cb84ef9…b061dc8` (adopted) ✓
- `builder/scratch/graph-algb-full.bin` = `d008a2b5…a0757f` — **this file is the Track B `ALG-B-MK50` cell** (`cb_scores.json` manifest: 68467 artists, 811784 edges, same sha) ✓
- `builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json` = `d9d6d5d3…62ae8` ✓

**Caveat on every ALG-E figure below:** the Track B `ALG-E-MK50` cell is sha `73feff…`, 74157 artists — **not** the adopted artifact (74193). CRE's `E-S0-P0` anchor is a third thing again (a cleaned rebuild with both drop flags). My ALG-E numbers are on the adopted artifact and are a *prior*, not a substitute for `E-S0-P0`.

**Probes** (read-only, no file in the repo touched, no Track B cell re-run): `cre_probe{1,2,3,3b,4,5,6,7,8,9,10}.py`. If any figure here enters the record, they belong in `builder/analysis/2026-08-03-cre-prereg-critique/` with a README, per the 2026-07-23 spec §4.2 convention.

---

## Correction to my own work, stated first

I built the `fame_lb_pctl` frame over the union snapshot's 88,953 non-null values. That is **wrong**. `fi_validation.json`'s `percentile_definition` records the frame as *"over the **adopted frame's** non-null `fame_lb_raw`"*, N = 74,151. Every figure below is recomputed on the correct frame (probe 9/10). **The error was worth 0.026 median in `fame_lb_pctl` per node — 1.7× CRE's own instrument floor** — and it is finding **F5** below, because CRE's own §1 and §0.3 wording is what produced it.

---

# Findings, ranked by how much each changes the design

## F1 — The primary outcome has a committed prior of ≈ 0 on exactly this pair class, at ramp strengths that bracket both proposed settings

**Measured** (probe 9, adopted frame, recomputed from `t3_paths.json` / `tb_paths.json` node sets — a *new* measurement in the adopted currency, not a re-read of any prior fame-scored result):

| arm | ramp `w` | C1 median, all 16 pairs | share of pairs \|Δ\| < 0.015 | share ≤ −0.05 | **the 4 all-famous anchor pairs** |
|---|---|---|---|---|---|
| P | 0.00 | +0.0022 | 0.69 | 0.00 | −0.0003 / +0.0002 / −0.0004 / −0.0006 |
| DD-A1 | 0.01 | +0.0005 | 0.50 | 0.12 | +0.0030 / +0.0013 / −0.0005 / −0.0001 |
| DD-A2 | 0.03 | −0.0272 | 0.31 | 0.31 | +0.0021 / +0.0011 / −0.0002 / −0.0001 |
| DD-A3 | **0.10** | −0.0793 | 0.25 | 0.56 | **+0.0007 / +0.0007 / −0.0002 / −0.0001** |

The anchors are `Miles Davis→Daft Punk`, `Metallica→Taylor Swift`, `Radiohead→The Beatles`, `Muse→Coldplay`. **Their paths do change** — at w = 0.10, depth 20, `Radiohead→Coldplay→The Beatles` becomes `Radiohead→Oasis→The Beatles`; `Muse→The Rolling Stones→Coldplay` becomes `Muse→Franz Ferdinand→Coldplay`; Miles Davis→Daft Punk swaps Ella Fitzgerald/Dean Martin/Alicia Keys/John Legend/Ye for Nat King Cole/Justin Bieber/Imagine Dragons. Twenty re-routes, every substitute another superstar. The device is live and it never leaves the top of the ruler.

Corroborating, on CRE's actual draw (probe 9, 22 `cb_pairs` famous pairs, adopted artifact, production weights): **d0 interior median `fame_lb_pctl` = 0.9971**, and the **lowest `fame_lb_pctl` anywhere within one hop of the d0 path is 0.8398** — headroom of only **+0.16**.

**Inference (plain):** on today's map, the two-superstar journeys CRE measures are surrounded by superstars. Pressing "I know them" twenty times swaps one household name for another. The pricing knob at any strength anyone has run does not change that, because there is nowhere within reach to go. This is `DD-F1`/`REQ-13` and CRE §5 already names it — but the design does not act on it: it spends six `P1` cells on a question whose incumbent-supply answer is already on the record.

**Change I propose:** run **one Stage-0 prior cell** before Stage 2 — the CRE ladder at ramp r₁ on the 22 `cb_pairs` famous pairs on the **adopted artifact** (no build, no new substrate, minutes). Pre-register its read: if C1 ≈ 0 there, `CRE-R0`'s null must be worded as *"the pricing device is inert on famous-famous pairs at incumbent supply, as it was in Track 3; the open question is entirely supply"* rather than as a joint null. And add to `CRE-R0` a branch CRE lacks: **"no viable pricing regime exists"** — a setting weak enough not to dominate (F7) is a setting Track 3 measured at ≈ 0.

**Confidence: high on the measurement, medium on the transfer.** Falsifier: `E-S1-P1a` (union supply × ramp) producing C1 ≤ −0.05 would show the anchors were pinned by *supply*, not by pricing — which is precisely CRE's hypothesis and why the supply arms must still run.

---

## F2 — The design never says whether the ladder uses `find_path` or `find_journey`, and under `find_path` the missingness is arm-correlated *in favour of the union arms*

**Measured.** The committed ladder (`run_arms.py::walk`, imported by `run_arms_t3.py`) calls `find_path_mirror` and **`break`s when `path[1:-1]` is empty**. The app calls `find_journey`. CRE mentions neither (`grep -n "find_path\|find_journey"` on the spec → no hits).

Probe 5, adopted artifact, production weights, 22 famous pairs, CRE's own victim rule:

| | depth 0 | depth 20 |
|---|---|---|
| pairs with a non-empty interior under `find_path` | **21** / 22 | 21 / 22 |
| under `find_journey` | **22** / 22 (one `forced` at every depth) | 22 / 22 |

One `ff-top01pct` pair is directly adjacent; the app forces a stop for it, the harness records nothing. `ff-top01pct` therefore reads **9** pairs against `CRE-G3`'s ≥ 8 floor — one pair of margin.

**Now the arithmetic that matters.** From `cb_scores.json` per-class `path_length` (n = 10 `ff-top01pct` pairs, all lengths ≥ 2):

- **`ALG-E-UC`**: mean 2.50, max 4 → Σ = 25 → `b + 2c = 5`, `a = 5 + c`. **At least 5 and at most 7 of the 10 pairs are directly adjacent at d0.** Under `find_path` the class has ≤ 5 readable pairs — **below `CRE-G3`'s floor of 8**. `CRE-S3` is a *specified-run* cell (§6: "no `CRE-R` is readable while either is unrun").
- **`ALG-E-MK100`** (= candidate cell `E-S0b-P0`): mean 2.80, max 4 → `a = 2 + c` → **at least 2 adjacent**, leaving ≤ 8 — exactly at the floor.
- `ALG-B-UC` (mean 3.20, max 5) admits `a = 0`; no bound.

**Inference (plain):** union rules add connections, which makes two superstars more likely to be *directly* connected. Under the measuring harness, a pair that becomes directly connected simply vanishes from the sums — and those are the pairs with the least room to get obscurer. So the arms that add connections get scored on an easier subset of journeys than the arms that do not. The app, meanwhile, would show those users a forced detour. Two different products are being compared.

**Change I propose, exactly:**
1. **Fix the ladder to `find_journey`** and say so in §0.3's held-constant table. It is what the app ships (F1, 2026-07-25), it makes every pair scorable, and the detour is chosen by the unchanged cost function so it introduces no scoring.
2. **Add the `DD-A13`/analyst-D7 uniform-drop rule to §4 verbatim**: a (pair, depth) cell infeasible in *any* compared cell is dropped from *every* compared cell, with the dropped set committed. Track 3 needed an amendment for this mid-flight (`dropped_cells_d7`, 1 cell); CRE carries no equivalent and its arms shorten paths harder.
3. Restate `CRE-G3`'s floor as **"≥ 8 pairs with a non-empty d0 interior *in every cell being compared*"**, and pre-register the `S3` comparison as expected-unreadable on `ff-top01pct` rather than discovering it.

**Confidence: high** (the length arithmetic is exact and the harness source is unambiguous). Falsifier: none I can see — this is a source reading plus integer arithmetic.

---

## F3 — `CRE-D1`'s gradient runs the *opposite* way to the hypothesis, and its "effect size" is a significance test that fires on any difference

**Measured** (probe 3b, corrected frame; W4 built via the committed `tas_frame_split.five_frames()`; rarity weighting = `tas_weighting`'s `log(N / df)`; adopted artifact's 449,003 undirected edges):

| band | all edges | labelled edges | median rarity-weighted W4 agreement | median label-set size (u, v) | share exactly 0 / exactly 1 |
|---|---|---|---|---|---|
| popular↔popular (both ≥ 0.75) | 114,725 | **113,353** (98.8 %) | **0.2315** | 10, 11 | 0.007 / 0.003 |
| obscure↔obscure (both ≤ 0.50) | 109,779 | **68,940** (62.8 %) | **0.1560** | 4, 4 | 0.081 / 0.039 |

**Observed band median difference (popular − obscure) = +0.0755. The hypothesis predicts negative.**

| null | mean | sd | what it can see |
|---|---|---|---|
| **N1** = CRE-D1 as written (permute the band label among the pooled 182k labelled edges), 1000 draws | +0.00001 | **0.00097** | exchangeability only |
| **N2** = size-preserving label scramble (permute label *sets* among labelled artists **within label-set-size strata**), 100 draws | **+0.01983** | 0.00064 | the label-supply artifact |
| size-matched read (146 shared `(min,max)` label-size cells, ≥ 30 edges each) | weighted mean **+0.0812**; **137 / 146** cells favour popular | — | the semantic effect |

**Inference (plain):** two very popular connected artists share *more* style labels than two obscure connected ones, not fewer — and that survives matching on how many labels each artist has. Separately, CRE's own test would declare almost anything significant: its bar is 2 × 0.00097 = **0.0019**, which is one eighth of the instrument floor the same document calls binding. With 182,000 edges, "exceeds 2 SD of a permutation null" is not an effect size; it is a p-value with a big n behind it. And a fifth of the observed gap (+0.0198 of +0.0755) is manufactured by nothing but label-set size — the artifact CRE's null structurally cannot see, and the one the design already knows how to control, since `CRE-C5` uses the stronger `TAS-AM3b` scramble two sections later.

There is a further hazard neither null touches and the size-matched read only partly does: **62.8 % of obscure-band edges are labelled against 98.8 % of popular-band ones** (`COH-2`'s coverage gradient, here re-measured in the adopted currency on W4). The obscure band's median describes a selected 63 %.

`tas_weighting.py`'s committed diagnostic already warns against exactly this statistic: *"Artists with one label each can only score 0.0 or 1.0, so a band median of 0.5 means 'about half match'… The rank correlation is the honest statistic."* 23.8 % of obscure-band edges have a size-1 endpoint against 2.0 % in the popular band.

**Change I propose, exactly:**
1. **Replace the null.** Effect = observed band difference **minus N2's mean**, tested against **N2's** distribution (200 draws is ample; sd 0.0006). Or drop draws entirely and use the size-matched read, which is deterministic and costs one pass.
2. **Replace the effect size with an absolute one in agreement units**, e.g. *"the size-matched band difference must exceed 0.05 in the hypothesised direction"* — 2 SD of the wrong null is not a threshold.
3. **Add a coverage row to the readability check**: report labelled-edge share per band beside the ≥ 500 floor, and bar any D1 sentence that does not carry it. (The 500 floor itself is fine but non-binding — both bands clear it 130×.)
4. **On this evidence, D1's branch is `not supported`**, so `E-S2-P1a` / `B-S2-P0` / `B-S2-P1a` and the router-side tag arm do not exist, and family (c) reduces to the single probe cell `E-S2-P0`. That is four cells and a whole amendment path saved before anything is built.

**Confidence: high on direction and magnitude; medium on transfer to CRE's substrate.** Falsifier: D1 is specified on "today's map"; I measured the adopted artifact's surviving edges. If CRE intends the *pre-cap candidate* substrate (`TAS-AM2`'s selection side), the number can differ — `tas_weighting`'s reading D records the analogous correlation moving from −0.13 to −0.02 across that same boundary. **§4 should state which substrate D1 runs on.** It currently does not.

---

## F4 — `CRE-C2` is a kill criterion that cannot fire in either regime it is meant to police

**Measured.** Top-1 %-by-degree on the adopted artifact = 742 nodes, degree cutoff 44 (probe 2).

Interior share in that set, pooled per band, from the committed ladders (probe 2/4):

| arm | d0–2 share | d10–20 share | **Δ** | pair-clustered bootstrap sd at n = 22 |
|---|---|---|---|---|
| P | 0.1036 | 0.0943 | −0.0094 | 0.0165 |
| DD-A1 (0.01) | 0.1073 | 0.0793 | −0.0281 | 0.0197 |
| DD-A2 (0.03) | 0.1048 | 0.0852 | −0.0197 | 0.0262 |
| DD-A3 (0.10) | 0.1000 | 0.0480 | −0.0520 | 0.0164 |
| TB-A2 | 0.1040 | 0.0465 | −0.0575 | 0.0130 |
| TB-A3 | 0.0925 | 0.0312 | −0.0613 | 0.0121 |

**Every measured Δ is negative.** The kill needs **+0.10**, i.e. **6 to 11 clustered SD** away from anything ever observed, in the direction opposite to the one the device pushes.

At the other end, from `cb_scores.json`, `top1pct_degree_frac_production` **at d0** on the famous classes: `ALG-E-MK50` = 0.6111 (`ff-top01pct`) / 0.2590 (`ff-top1pct`); `ALG-E-UC` = 0.5000 / 0.1556. A base of 0.61 leaves 0.39 of headroom, and the descent arms move *down* from it.

**Inference (plain):** the criterion asks whether pressing the button makes the journey lean *more* on the map's most-connected artists. Every measurement says pressing the button leans on them *less*, because obscure artists are by definition not the well-connected ones. The criterion is anti-correlated with the intervention by construction. Meanwhile the hub behaviour that Track B actually flagged is at press zero — 61 % of interiors on the top-0.1 % journeys are already top-degree — and the owner has ruled that tolerable, which leaves `CRE-C2` policing nothing.

**One more thing the design should decide, not assume.** `cb_scores.json` shows the two reference sets disagreeing *totally* on the same paths: `ALG-E-TUw-50-50`, `ff-top01pct` — `top1pct_degree_frac_own` = **0.0000**, `top1pct_degree_frac_production` = **0.6111**. The choice of reference set moves the reading by 0.61, six times the kill threshold. §5's argument for the production set (own-graph sets are selection-order arbitrary at ceiling ties) is sound, but a 0.61 divergence should be *stated* in §5, not left in a parenthesis.

**Change I propose, exactly:** keep the production reference set; **replace the kill with a level bar plus a reported delta**. E.g. *"Kill: the d10–20 band share exceeds the same arm's d0–2 share by ≥ +0.10 **or** the d10–20 band share exceeds 0.50 in absolute terms."* The level half is what would actually catch a union arm parking journeys on hubs at depth; the delta half is retained but its measured base rate (−0.06 to −0.01, clustered sd 0.012–0.026) should be recorded in §5 so a null reading is not later mistaken for reassurance.

**Confidence: high** for capped graphs (six arms, two devices, consistent sign). **Medium** for union/UC graphs — I did not build one, so the d10–20 hub share there is **unmeasured**. That is the falsifier: if a UC arm's d10–20 production-set share came in above 0.7 with d0–2 at 0.5, the delta form would fire after all.

---

## F5 — §1 and §0.3 name the wrong frame for the ruler, and the ambiguity is worth 1.7 × the instrument floor

**Measured** (probe 9). §1 says the currency is *"`fame_lb_pctl` … over the frozen union snapshot"*; §0.3's held-constant row says *"the fame ruler: `fame_lb_pctl` over the frozen union snapshot `fi_union_snapshot.json`"*. `fi_validation.json` says the percentile frame is **the adopted artifact's non-null values, N = 74,151** — the union snapshot supplies *raw values*, including for the 18,874 `ALG-B`-only artists, which are then *mapped* into that frame (which is what §0.4's "mapped-percentile grain" means).

| | adopted frame (correct) | union frame (what §1 literally says) |
|---|---|---|
| N_nonnull | 74,151 | 88,953 |
| largest tie atom / N | 109 → **0.001470** ✓ matches CRE's quoted 0.0015 | 242 → **0.002721** |
| ⇒ 10 × step (the binding floor) | **0.015** | **0.027** |
| a node's `fame_lb_pctl` | — | shifts by median **+0.0262**, max 0.0296 |

**Inference (plain):** a session executing this cold builds the ruler the sentence describes, and every artist reads about 2.6 percentile points more famous than intended — bigger than the smallest movement the document says it can see, and bigger than the margin `CRE-R4` uses to pick a winner. I know this because it is what I did, in this critique, until `fi_validation.json` caught it.

**Change I propose, exactly:** replace both sentences with *"`fame_lb_pctl` = `(|{f < v}| + (|{f = v}| + 1)/2) / N_nonnull` over the **adopted artifact's** non-null `fame_lb_raw` (N = 74,151), with `fi_union_snapshot.json` (sha `d9d6d5d3…`) supplying raw values for artists outside it; `pctl(v > frame max) = pctl(max)` (`FAM-AM1.6`)"* — and add a Stage-2 instrument assertion that the harness's frame N equals 74,151. Zero cost, and it is exactly the class of defect `CLAUDE.md`'s rename note describes: correct by citation, wrong by description.

**Confidence: high.** Falsifier: if `FAM-` intended the union frame after all, then CRE's own quoted step (0.0015) is wrong and the floor should be 0.027 — either way one of the two numbers in §1 is inconsistent and must be fixed.

---

## F6 — `CRE-R4`'s 0.015 lead margin sits inside the sampling noise, and `CRE-C1`'s median is a knife-edge statistic

**Measured** (probe 4, pair-level bootstrap, 5,000 draws, resampled to n = 22 from the committed ladders):

| quantity | value |
|---|---|
| bootstrap sd of the **arm C1 median** at n = 22 | P 0.0044 · DD-A1 0.0034 · DD-A2 **0.0121** · DD-A3 **0.0419** · TB-A3 0.0265 |
| DD-A3 95 % CI for its median at n = 22 | **[−0.156, −0.016]** — straddles the −0.05 bar by a factor of 3 either way |
| bootstrap sd of a **paired** arm-vs-arm C1 difference at n = 22 | 0.0032 – **0.0706** (0.012 – 0.033 for arms near the bar) |
| same, **unpaired** difference of medians (what R4 describes) | 0.0053 – 0.0433 |
| leave-one-out swing of the arm median (n = 16) | DD-A3 **0.0190**; TB-A2 0.0034; DD-A2 0.0001 |
| share of pairs with \|Δ\| < 0.015 ("no measured movement") | 0.25 – 0.75 across arms |
| share of pairs with Δ ≤ −0.05 | DD-A3 **0.56** (9/16) — the median clears the bar by one pair |
| aggregation sensitivity: pooled-interiors vs mean-of-per-depth-medians | moves the arm statistic by up to **0.0246** (DD-A3) |

**Inference (plain):** the number that decides which rule wins wobbles by more than the margin that defines "winning". Dropping a single journey from the 22 can move an arm's score by 0.019 — more than the 0.015 lead `CRE-R4` calls decisive. And because the score is a median, an arm passes exactly when more than half the journeys individually beat the bar: DD-A3 passes on 9 of 16, so one journey either way flips it. That is a threshold on a coin-flip, not a measurement.

**Changes I propose, exactly:**
1. **`CRE-C1` becomes a conjunction, all three pre-registered together:** (i) arm median ≤ **−0.05**; (ii) the **95 % pair-level bootstrap upper bound** of that median ≤ **−0.015** (the instrument floor — i.e. the arm is not merely point-estimated past the bar); (iii) **report** the count of pairs at ≤ −0.05, the count at \|Δ\| < 0.015, and the full leave-one-out range of the median. (iii) costs nothing and makes the knife-edge visible; the Track B results note's own leave-one-out concern is thereby discharged mechanically rather than by memory.
2. **A paired sign-flip requirement is *not* worth adding as specified** — with 25–75 % of pairs inside the instrument floor, a sign test is mostly ties and its power is poor. The **count of pairs at ≤ −0.05** carries the same information without a tie convention, and (ii) above is the better second gate. This is a direct answer to the question asked: the leave-one-out half is high-value and free; the sign-flip half is not, for this distribution.
3. **`CRE-R4` (ii): raise the lead margin to ≥ 0.05 and compute it *paired* on the common pair set**, with a bootstrap CI on the paired difference excluding zero. 0.015 is 0.5–1.2 SD of the very quantity it is applied to. If the design would rather keep a small margin, then it must be paired and CI-bounded; unpaired at 0.015 it is noise.
4. **Fix the aggregation explicitly.** §5 says "pooled over depths 10–20"; state that it is the pooled interior slots (not the mean of per-depth medians), and note the 0.0246 sensitivity — pooling weights the depths at which the path is longest, which interacts directly with `CRE-C4`'s shortening.

**Confidence: high on the arithmetic; medium on transfer.** These dispersions come from Track 3 and Track 3b — two devices, but **one pair draw**, and not CRE's draw. That is exactly the one-slice hazard, so I am naming it rather than reporting the point estimates as settled. The cheap fix is that the bootstrap in (ii) is computed on CRE's own 22 pairs at run time, so it needs no transfer at all.

---

## F7 — Both proposed ramp settings are in the *dominating* regime, and r₂ exceeds the strongest ramp any committed track has run

**Measured** (probe 8/10, adopted artifact).

Currency translation first — the ramp moves from `pop_raw`-percentile (Track 3) to `fame_lb_pctl` (CRE):

- mean \|Δ `pop_pctl`\| per directed edge = **0.14357**; mean \|Δ `fame_lb_pctl`\| = **0.14775**; ratio **1.029**. **A CRE ramp `r` behaves like a Track 3 `w` of ≈ `r`.** So r₁ = 0.05 sits between `DD-A2` (0.03) and `DD-A3` (0.10), and **r₂ = 0.15 is 1.5× the strongest ramp Track 3 ran.**

Now the scale. The ramp adds `r · k · fame_lb_pctl(v)` **per interior**, on the relaxation target (`mirror.py` `_dijkstra`, `cost += ramp * pctl_v`):

| `r` \ presses `k` | 1 | 5 | 10 | 20 |
|---|---|---|---|---|
| 0.01 (`DD-A1`) | 0.010 | 0.050 | 0.099 | 0.198 |
| 0.03 (`DD-A2`) | 0.030 | 0.148 | 0.297 | 0.594 |
| **0.05 (r₁)** | 0.050 | 0.247 | **0.495** | 0.990 |
| **0.15 (r₂)** | 0.148 | 0.742 | **1.485** | **2.970** |
| 1.00 (`G2`) | 0.990 | 4.950 | 9.900 | 19.800 |

Against the terms it competes with, **as realised on the edges the router actually chose** (production arm, d0, committed paths): **median `w_sim·(1−sim)` = 0.0038**, mean 0.3565; mean `w_jump·|Δpop_raw|` = 0.0675; `w_hop` = 0.02.

So r₁ at ten presses is **130× the median similarity cost of a production-chosen edge** and 25× `w_hop`; r₂ at twenty presses is **780×**. Measured consequence on the committed ladders: the median realised `w_sim·(1−sim)` on chosen edges at d10–20 goes 0.0014 (P) → 0.2456 (w = 0.01) → 0.6466 (w = 0.03) → **1.1331** (w = 0.10). Track 3's own coherence tripwire (`DD-C4`, figures owned by `2026-07-28-track3-depth-descent/REPORT.md` §2) flagged every arm, monotonically.

**Inference (plain):** "each press makes the builder a little more willing to route through less famous artists" is not what these settings do. From about five presses on, at either setting, the obscurity toll is the *largest* term in the cost function and similarity is a rounding error — the builder will accept an almost unrelated artist to avoid a famous one. That is the mechanism behind the shortening in F8 and behind Track 3's similarity collapse.

**Changes I propose, exactly:**
1. **Move the bracket down**: r₁ = **0.01**, r₂ = **0.03**, reproducing `DD-A1`/`DD-A2`'s realised regime in the new currency (translation factor 1.03, so the reproduction is near-exact), and *state* that both are known to give C1 ≈ 0 on famous-famous pairs at incumbent supply (F1) — the arms exist to test whether **union supply** unlocks them, which is the only genuinely new cell. If the design instead wants strength, keep 0.05 but **drop 0.15**, which is off the end of every measured curve, and say in §3.3 that r₂ is deliberately beyond the coherence data.
2. **`CRE-G2` is sound as a wire test and weak as a scale test.** At r = 1.0, k = 1 the toll is 0.99 against a median chosen-edge similarity cost of 0.0038 — it will pass trivially, so "≥ half change at d1" cannot distinguish "connected" from "connected and correctly scaled in `k`". Its red half is already covered by `CRE-G1` (device off ⇒ byte-identical). **Add one line**: assert that the recorded per-cell toll equals `r · k · Σ fame_lb_pctl` over the returned interiors at two depths (k = 1 and k = 10). Track 3 did this arithmetic check (`REPORT.md` §2, realised toll at k = 10); CRE has no equivalent, and a `k`-indexing bug would pass `G1` and `G2` both.

**Confidence: high on the arithmetic, and the coherence reading is a *flag not a verdict*** — adjacent similarity is not a validated coherence proxy in this project and `REQ-38`'s blind listen decides. I am reporting where the device sits relative to the cost function, not adjudicating whether it sounds bad.

---

## F8 — `CRE-C4`'s floor at 0.5 would have passed every arm Track 3 flagged, including the one it flagged hardest

**Measured** (probe 2, C4 computed exactly as §5 specifies: per pair, mean interior count over d10–20 ÷ interior count at d0; arm statistic = median over pairs):

| arm | ramp `w` | C4 median | C4 mean | C4 min |
|---|---|---|---|---|
| P | 0.00 | **1.278** | 1.393 | 0.958 |
| DD-A1 | 0.01 | 0.963 | 0.956 | 0.500 |
| DD-A2 | 0.03 | 0.778 | 0.792 | 0.487 |
| DD-A3 | **0.10** | **0.722** | 0.763 | 0.438 |

**Every arm clears 0.5 at the median.** Track 3's `DD-C6` flagged all three (its figures are owned by that directory's `REPORT.md` §2 and I do not restate them); CRE's replacement floor would have declared all three fine.

Two structural points the number exposes. First, **the production arm's ratio is 1.278, not 1.0** — the all-known walk *lengthens* paths by ~28 % as exclusions accumulate. So a within-arm ratio of 0.72 is really 0.72/1.28 = **0.56 relative to what the ladder does without the device** — the criterion's baseline is not 1. Second, the ramp is a *per-interior* toll, so **deleting an interior is the cheapest way to pay less**: at r₂ = 0.15, k = 10, dropping one pctl-0.99 interior saves 1.485, while the worst possible similarity penalty for the substituted edge is `w_sim · 1 = 3.0`. Shortening is not a side effect; it is the gradient.

**Change I propose, exactly:** raise the floor to **≥ 0.75** *and* report the baseline-relative form (arm C4 ÷ its isolating baseline's C4) beside it, with `CRE-R3` firing on either. 0.75 is the value that separates `DD-A1` from `DD-A2`/`DD-A3` on the only data that exists; 0.5 separates nothing.

**Confidence: high on the measurement, medium on the threshold.** 0.75 is calibrated on one pair draw and one graph — the falsifier is CRE's own `E-S1-P0` baseline coming in far from 1.278, which would mean the ladder's natural lengthening differs on union supply and the floor needs recalibrating from `E-S0-P0` before Stage 2 reads it. **That recalibration should be pre-registered now**, from the anchor cell, not chosen after the arms have run.

---

## F9 — `CRE-C6` cannot fire as a class total, and the d0 frontier is the wrong frontier — measured, not argued

**Measured** (probe 9, corrected frame, 22 famous pairs, production weights):

| | ALG-E adopted | ALG-B MK50 cell |
|---|---|---|
| pairs with a d0 interior | 21 | 22 |
| d0 interior median `fame_lb_pctl` (median over pairs) | 0.9971 | 0.9963 |
| **C6 class total, d0 path node set** (screen fires only at **0**) | **130** | **600** |
| pairs individually reading zero at the d0 node set | **10 / 21** | 0 / 22 |
| C6 class total, 1-hop frontier | 3,859 | 14,966 |
| pairs individually reading zero at 1 hop | **0 / 21** | 0 / 22 |
| lowest `fame_lb_pctl` within 1 hop of the d0 path (median over pairs) | 0.8398 → headroom **+0.16** | 0.0003 → headroom **+1.00** |

**Inference (plain):** the screen asks "is there anywhere at all, one step off this journey, meaningfully less famous to go?" — and it fires only if the answer is *no for all twenty-two journeys at once*. That never happens: 130 such connections exist on the adopted map and 600 on the candidate one. The screen is inert. Meanwhile, at the per-journey level the frontier choice matters enormously: **10 of 21 journeys have no such connection hanging off the journey itself, but every one of them has plenty one step further out** — and the journey-builder can go one step further out, because pressing "I know them" reroutes the whole path, not just one card.

So, to the question as asked: **as a class total the d0 frontier cannot false-negative, because it cannot negative at all.** The moment `CRE-C6` is made per-pair — which is the only form in which a screen is useful — the d0 frontier false-negatives on **10 of 21** pairs where a 1-hop frontier false-negatives on **0 of 21**.

**Change I propose, exactly:** make the screen per-pair on the **1-hop frontier**, and turn it into supply reporting rather than a disqualifier:

> **`CRE-C6`**: over the famous class, per pair, count edges from the **1-hop neighbourhood of the d0 path node set** to artists with `fame_lb_pctl` ≥ 0.15 below that path's d0 interior median. **Screen: a cell is screened out of Stage 2 only if ≥ 8 pairs (the `CRE-G3` readability floor) individually read zero** — i.e. the cell cannot exhibit the primary outcome on a readable sub-class. Otherwise reported: the per-pair count distribution and the per-pair 1-hop headroom, which are the supply diagnostic `CRE-R0` will need to say *where* movement was not found.

A screen that cannot false-negative *by construction* would be the ∞-hop version, which is the whole component and therefore vacuous. 1-hop is the right compromise, and the measurement says the false-negative rate drops from 10/21 to 0/21 for one extra hop of BFS.

**Confidence: high.** Falsifier: on a union graph the 1-hop neighbourhood is much larger, so the screen gets weaker still — which is an argument for the reporting form, not the disqualifying form.

---

## F10 — The population confound is under-specified: the real cross-population problem is **descent headroom** and **differential ruler-null censoring**, not the median gap §0.4 names

**Measured** (probes 9/10, corrected frame):

| | ALG-E (adopted) | ALG-B (MK50 cell) |
|---|---|---|
| median `fame_lb_pctl` | 0.500 | 0.563 |
| **ruler-null share of nodes** | **0.0006** (42 / 74,193) | **0.0596** (4,080 / 68,467) |
| ruler-null share among `ALG-B`-only artists | — | **0.2157** (4,072 / 18,874) |
| null rate, bottom in-graph-popularity decile → top decile | — | 0.0795 → 0.0453 |
| **1-hop descent headroom from the d0 famous path** (median over pairs) | **+0.16** | **+1.00** |

**Inference (plain), two problems:**

1. **Headroom.** The same absolute bar of −0.05 asks a *six-times harder* question of an `ALG-E` arm than an `ALG-B` one. On the production map the obscurest artist one step off a superstar journey is at the 84th percentile; on the candidate map it is at the 0.03rd. §0.4 promises within-data-set primary reads, but §5's material bar is **absolute and identical on both**, and `CRE-R4` (ii) compares arms' C1 statistics against a common 0.015 margin **without restricting to one data set**. Yes — the answer to question 6 is that **`CRE-R4` (ii) is still cross-population as written**: if the best passing arm on `ALG-E` and the best on `ALG-B` are compared on that margin, the comparison is exactly the one §0.4 bars.

2. **Censoring, which §0.4 does not name at all.** A ruler-null interior is a hole in the denominator. On `ALG-E` that removes 0.06 % of interiors. On `ALG-B` it removes ~6 % of nodes and **21.6 % of the very artists `ALG-B` was crawled to add**, and the null rate is 1.8× higher in the obscure decile than the famous one. So as an `ALG-B` arm descends, the artists it delivers drop *out of its own score* at an increasing rate. **The censoring is depth-correlated and biases `ALG-B`'s C1 toward zero, inside the within-data-set read** — it is not only a cross-population issue.

**Changes I propose, exactly:**
1. **`CRE-R4` (ii)**: add *"…the best other passing arm **on the same data set**; no lead is computed across data sets, per §0.4"*, and state that a cross-data-set choice is presented as options with the headroom figures attached, never as a lead.
2. **Add a §0.4 row for differential ruler-null censoring**, with the obligation: **every C1 figure reports the per-depth null count *and* the null share trend from d0 to d20** (§1 already requires per-depth null counts — this makes the *trend* readable, which is the part that biases). Pre-register the read: an arm whose null share rises by more than 0.05 from d0 to the d10–20 band has its C1 reported as *"descent partly unmeasurable"*, not as a pass.
3. Consider **reporting C1 as a fraction of that arm's own measured 1-hop headroom** as a descriptive companion. Not as a bar — that is a design choice — but it is the statistic that makes the two data sets comparable at all, and without something like it the findings note has no honest way to put `ALG-E` and `ALG-B` arms in the same sentence.

**Confidence: high on the measurements. The 1-hop headroom is a lower bound on what a ladder can reach** (Dijkstra roams further than one hop), so it under-states both data sets — but it under-states them by different amounts, which is the point.

---

## F11 — `CRE-C5`'s tag attribution compounds two noisy quantities and cannot resolve at n = 22

**Measured / derived.** `C5` requires the real Δgain ≥ 0.015 and the scrambled companion's Δgain ≤ 50 % of it. Δgain is a difference of two arm C1 statistics; from F6, the paired bootstrap sd of such a difference at n = 22 is **0.012 – 0.033**. So the entry condition (≥ 0.015) is **0.5 – 1.2 SD** — indistinguishable from zero — and the 50 % test is then a *ratio of two quantities each roughly one SD from zero*, whose sampling distribution is heavy-tailed and effectively unbounded.

**Change I propose, exactly:** require the real Δgain ≥ **0.05** (the material bar — an attribution question about an effect below the material bar is not worth asking), and replace the 50 % ratio with a **difference tested paired**: attribution holds iff the 95 % pair-level bootstrap CI of *(real Δgain − companion Δgain)* excludes zero. Same data, same cost, a statistic that has a distribution.

**Confidence: medium-high.** The sd transfer is from Track 3's draw; the structural point (a ratio of two near-zero noisy quantities) does not depend on the transfer.

---

## F12 — Two smaller items the factor table misses

**(a) The dormant-term disclosure is *right about `w_floor` and wrong about where*.** Measured (probe 6): base `floor_raw` = `min(pop_raw[s], pop_raw[t])` is 0.684–0.763 for the twelve `ff-top1pct` pairs and 0.848–0.889 for the ten `ff-top01pct` pairs; at `floor_relax_known` per press the floor reaches **0.0 after 5 presses (12 pairs) or 6 presses (10 pairs)** — **all 22 pairs, every arm, no exceptions.** And at d0 the ramp term is exactly zero by construction (`mirror.py`: the term is not added at k = 0), so every `P1` arm's d0 path *is* its `P0` baseline's d0 path — Track 3 verified this 16/16.

⇒ **`CRE-C1` reads d0 (floor fires, identically across pricing arms) and d10–20 (floor is identically dead).** The window where the floor both fires *and* differs by pricing arm is d1–d5, which `CRE-C1` does not read. So §0.3's disclosed uncontrolled variable **cannot carry any attribution on the primary outcome across the pricing knob** — which is good news the document should claim rather than hedge. It *does* still apply across the **supply** knob, where d0 routing genuinely differs. §0.3 should say this: it currently over-warns on pricing and under-warns on supply.

**(b) A term genuinely absent from §0.3.** `pop_raw` is `_log_scaled` **min-max over the *kept* (largest-component) node set** (`graph.py::_log_scaled`), while the score-weighted in-degree it scales is accumulated **before** `mutual_knn_cap` (`pipeline.py`). So `pop_raw` values are cap-rule-invariant *up to an affine renormalisation whose endpoints depend on which artists survive* — and `MK50` strands ~800 artists on `ALG-E` where `TUw-50-50` strands 1 (Track B results §1). Any shift in `low` shifts **every** `pop_raw`, hence `floor_raw` and every `w_jump` term, **across supply arms within one data set**. I expect the shift to be tiny (the min is near-zero and the max artist survives everywhere) — **this is inference, not measurement; I did not build a TU cell.** The fix is one line of Stage-1 instrumentation: **record `low` and `high` from `_log_scaled` per built cell and report the affine map between arms**, so a non-trivial shift is visible rather than silent. Cost: two floats per cell.

**(c) Asymmetric ramp axis.** §0.2 gives `E-S1` and `B-S1` both r₁ and r₂, but `E-S2`, `B-S2` and `B-S0` carry only r₁. §6's run-state rule ("both `P1` ramp settings are part of the specified run **in every cell that carries them**") is internally consistent, but it means `CRE-R4` could name a clear winner whose pricing axis was explored at one point while its rival's was explored at two. Either add the missing r₂ cells or add a line to `R4` barring a clear-winner call for an arm explored on fewer ramp settings than the arm it beat.

---

## What I would defend and what I would abandon cheaply

**Defend:** F2's integer arithmetic on adjacency (exact, from committed `cb_scores.json`); F5's frame discrepancy (`fi_validation.json` is explicit); F3's direction and the vacuity of the 2 × SD bar (n ≈ 182,000, sd 0.00097 — arithmetic); F4's sign consistency across six arms and two devices; F12(a)'s floor-death arithmetic.

**Abandon cheaply:** every threshold I proposed calibrated on Track 3's draw (C4 ≥ 0.75, the r₁/r₂ bracket, C5's 0.05) — one pair set, one graph, and the graph is not a CRE substrate. Those should be recalibrated from `E-S0-P0` and `B-S0-P0` **before** Stage 2 reads anything, and that recalibration must itself be pre-registered, or it becomes threshold selection after the fact.

**The load-bearing assumption under F1, F6, F7 and F8:** that dispersion and effect magnitudes measured on Track 3's 12-scored/16-total mixed-class draw on `graph-t15-tiebreakfix` transfer to CRE's 22 famous-famous pairs on two cleaned rebuilds. They reproduce across **two devices** (ramp and thresholded toll) on **one pair set** — that is not a second slice, and I am flagging it rather than reporting the point estimates as settled. The single cheapest thing that would falsify or confirm the whole cluster is the Stage-0 prior cell proposed in F1: **the r₁ ladder on the 22 `cb_pairs` famous pairs, on the adopted artifact, no build required.**

## What I did not do, and would need to

- I built no variant graph, so **every union/UC figure here comes from committed Track B outputs**, never from a cell I ran. The d10–20 hub share on a union graph (F4's falsifier) and the `_log_scaled` affine shift (F12b) are **unmeasured**.
- I did not run any ramp on CRE's own pair set — that is CRE's Stage 2 and outside my brief.
- I did not evaluate whether any of this is *good for the app*. `REQ-38`'s blind listen and the owner's ear decide that; F7's similarity figures are a flag on where the cost function sits, not a coherence verdict.
