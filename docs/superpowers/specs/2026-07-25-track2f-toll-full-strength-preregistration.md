# Track 2F — the similarity-ceiling toll at full strength: pre-registration

**Role: ACTIVE. This document governs the Track 2F run and nothing else.** It is committed
**before any arm runs**; the git commit timestamp is the evidence that it preceded the
result.

**Why this exists.** Track 2 returned R0, a full null, on 2026-07-24 — but the null had a
direction. `T1b`, the similarity-ceiling toll, was the only coherent signal in fifteen arms,
and per Track 2 amendment **A17(b)** it ran at **half its intended magnitude**: because
R1's fallback selected `W = A7`, which carries `w_sim` 1.5 rather than 3.0, and the toll was
implemented as `w_sim · (1 − toll_s)`, the two magnitudes were 3.75× and 15× `w_hop` rather
than the 7.5× and 30× the Track 2 pre-registration §1.4 names. **The only mechanism that
moved anything has never run at full strength, and its intended top has never been tested.**

**Namespace.** This is a new identifier series and it is namespaced `TF`, per CLAUDE.md's
forward-only rule. It **reuses** Track 2's criteria `C1`–`C4` **by citation, unchanged** —
those are the same objects with the same thresholds, not new ones. Nothing committed is
renamed.

## What this does NOT re-litigate

Per Track 2 pre-registration §2.4's read of R0, and repeated here so it is in the governing
document rather than only in the handoff:

- The **`capfix` adoption**, mutual k-NN, and anything in the repair+retune log §4/§4.1.
- **Any threshold.** `C1`–`C4` stand exactly as written. This document adds a *continuation
  trigger* with its own separate effect size (§2.2); it does not soften a criterion.
- **Shipping an arm that fails the gates.** Passing offline selects a candidate for a blind
  listen; it never adopts one.
- **The floor device.** Track 2 stage 2 established it is never pivotal — `FL1`/`FL2` were
  byte-identical to their base on every scored cell. The floor is off in this design's base
  and stays off.

---

## §0 Factor table

### What varies — exactly one column

| Arm | Toll magnitude (× `w_hop`) | Isolating baseline | Reading a contrast against that baseline licenses |
|---|---|---|---|
| `P` | — (production, toll off) | — | Not an arm. `C1`'s pairing baseline and `C5`'s first reference. |
| `A0` | — (production, floor off) | `P` | Not an arm. `C5`'s second reference, per Track 2 **A8**. |
| `A7` | 0 (off) | — | **The ladder's isolating baseline.** `W`, exactly as stage 2 ran it. |
| `T1a_rpt` | 3.75 | `A7` | **Reproduction of `T1a`.** Must be byte-identical to the committed stage-2 paths. |
| `TF1` | **7.5** | `A7` | §1.4's *intended* `T1a` magnitude — the first never-run cell. |
| `T1b_rpt` | 15 | `TF1` | **Reproduction of `T1b`.** Must be byte-identical to the committed stage-2 paths. |
| `TF2` | **30** | `T1b_rpt` | **§1.4's intended top. The headline arm — the one this experiment exists for.** |
| `TF3` | 60 | `TF2` | One doubling past the intended top. |
| `TF4` | 120 | `TF3` | Two doublings past the intended top. |
| `TFX` | 7,500 (effectively prohibitive) | `TF4` | **The ban corner: a bound, never a candidate.** See the A17(c) check in §3, `TFR4`. |

Every arm is `A7` plus one number. `A7`'s configuration is unchanged from stage 2
(`jump_currency = pctl`, `w_jump = 0.3`, `w_sim = 1.5`, floor off, guard G on), so every
figure here is directly comparable to `scores_stage2.json` without re-deriving anything.

**Magnitudes are pre-registered in multiples of `w_hop`, not as absolute costs and not as
`toll_s` values.** This is the direct fix for what A17(b) caught: `toll_s` is
`w_sim`-dependent, so the same `toll_s` means two different tolls under two different `W`s,
and §1.4's figures were quoted for the wrong one. `w_hop` is the currency §1.4 pre-registered
in. The harness gains a `toll_hops` knob that names its own basis, per CLAUDE.md's
currency-in-the-name convention; `w_hop` itself is read from `ApiConfig` and is cited, never
restated here.

### Held constant, and why each is genuinely constant under the intervention

Per CLAUDE.md: enumerate every term the comparison holds fixed, and for each state why the
intervention cannot change its state. **Two entries below are NOT genuinely constant**, and
both carry a response fixed before the run.

| Held constant | Genuinely constant under a stronger toll? |
|---|---|
| Artifact `4cb84ef9…b061dc8` | **Yes.** Router-side only; no rebuild. Asserted by sha256 in-script before every run. |
| Pair set (8 analysis + 4 held-out), Track 2 §2.3 | **Yes.** Fixed in `verify_mirror.py`; not a knob. |
| Walk protocol (all-`known`, 20 bypasses, victim = most-popular interior, guard G on, snapshots at {0,1,2,3,5,7,10,15,20}) | **Yes.** Arm-independent code path. |
| Fame proxy rule (A11: Wikipedia pageviews, `F = log10(1+views)`, unmatched → 0) | **Yes as a rule** — but see *coverage* below, which is a different thing. |
| Base configuration `A7` | **Yes.** The ladder varies only `toll_hops`. |
| `w_floor = 0.0` | **Yes, unconditionally.** The floor is off by *weight*, not by circumstance, so no toll can switch it on. This is the `w_floor` dormant-term check that restructured Track 2, applied here — and unlike that case it resolves clean. |
| `w_degree_hub = 0.0` | **Yes.** Zero weight, `ApiConfig` default, untouched by every arm. |
| `w_avoid` / the avoidance map | **Yes.** Stage A walks are all-`known`; the map is empty and a toll cannot create a dislike. |
| **Blank-named interiors** | **NO — directional, and this intervention is precisely what could switch it on.** Track 2 **A18**: blank names sit 2.7× concentrated in the bottom popularity decile, resolve to `F = 0` (maximal apparent reach), and are absent from `P` entirely. Stage 1 and 2 saw **zero** blank interiors — but they never tolled harder than 15×, and this ladder drives paths at the obscure tail up to 7,500×. Bias with a known sign, absent from the control, arriving preferentially in the arms that "succeed". **Response fixed in §6.** |
| **Proxy coverage** | **NO — and it moves *with* the intervention's apparent success.** A stronger toll reaches more obscure artists; under A11 an unmatched artist scores at the fame floor, so falling coverage *inflates* reach. Track 2 **A12** already de-gated coverage for this reason; the gating remnant is A11's d15/d20 notability guard. **Response fixed in §6.** |
| Guard-infeasible cells | **Mechanically possible, structurally unlikely.** A toll re-prices edges, it never removes them, so reachability is unchanged and every node stays reachable at finite cost. **A13**'s uniform drop applies regardless, and inherits Track 2 stage 1's drop set. |

---

## §1 What this experiment cannot show — stated before it runs

Three structural bounds, each verified in code or in a committed measurement. They are here
so that neither outcome is over-read.

**1. This tests the ceiling's *cheapness*, never its *ordering* — and the ordering half
cannot be tested router-side at all.** Track 2 §1.4 and the toll-calibration README §2 both
record that at a fully saturated node an additive toll adds the same constant to all 50
exits and therefore **cannot re-rank them**. Verified in the builder:
`pipeline.py:100` stores `min(1.0, …)`, so every above-p99 edge is written as exactly `1.0`
and the artifact retains **no information distinguishing saturated edges from one another**.
The builder-side p99 **rescale** would restore that ordering; no router-side arm can. So a
null here reduces the ceiling hypothesis but **does not close it**, and a hit strengthens it
on both halves.

**2. The first hop out of eight of the twenty-four endpoints is unchangeable by any toll.**
The toll-calibration README's Q4 owns the figure: eight pre-registered endpoints are *fully*
saturated — every one of their 50 neighbours sits at exactly 1.0. All exits are tolled
identically, so no magnitude on this ladder, including `TFX`, can change which neighbour is
preferred there. What a large toll *can* do is make routes that pass **through** saturated
regions dearer overall, pushing paths to avoid entering them. That is the mechanism under
test; the forced first hop is not.

**3. This cannot address F2's "progressively" clause.** Every arm here is
**depth-independent by construction** — a static toll prices the same edges the same way at
bypass 0 and bypass 20. `C3` (the depth gradient) is therefore expected to stay roughly
flat, and a `C3` failure is not evidence about this mechanism. The only depth-graduated
device in the cost function is dead (Track 2 stage 2), so the depth carrier remains an open
problem that this experiment does not touch.

---

## §2 Criteria

### 2.1 Gating criteria — cited from Track 2 §2.2, unchanged

Same thresholds, same pair set, same proxy, same scoring code. Each is given here with the
plain-language sentence fixed **now, before any result exists**, per CLAUDE.md's
presentation rule; owner-facing text must quote the sentence beside the identifier.

| # | Threshold (Track 2 §2.2) | The plain sentence, fixed now |
|---|---|---|
| **C1** | mean `ΔF` over d ≥ 10 cells ≤ **−1.0**, and `ΔF < 0` in ≥ **75 %** of those cells | *After ten or more presses of "know them already", is the typical artist in the middle of the journey meaningfully less famous than the one the app gives you today — about ten times fewer fans — and does that hold on most journeys, not just one or two?* |
| **C2** | in ≥ **4 of 8** analysis pairs, at least one d15-or-d20 interior falls below `B_unk` | *On at least half the test journeys, does deep bypassing eventually put in front of you at least one artist you would genuinely not know?* (`B_unk` = the fame level the owner's own "never heard of them" labels sit at.) |
| **C3** | pooled median `F` at d20 ≤ pooled median `F` at d5 **− 0.5** | *Does the journey keep getting more obscure the more you press, rather than dropping once and then flattening out?* |
| **C4** | mean interior count over d ≥ 10 cells ≥ `P`'s mean **− 1** | *Does the journey still have roughly as many artists in it? You are not allowed to win by handing back a shorter journey.* |

`C2`'s standing under **A17(a)** carries forward: it is a one-sided **regression guard**, not
a discriminator. It did real work in stage 1 — every arm that moved paths went *backwards*
on it — and the Track 2 handoff's warning applies here in full: **if an arm's interior-level
below-band count and its pair-level `C2` disagree, `C2` is the one that counts**, because
reaching deeper in fewer places is Attack 2's signature (the insular-cluster dive), and `C2`
is the criterion encoding what the owner asked for. Both figures are reported per arm.

**A winning configuration** passes `C1`–`C4` on the analysis set, **then** reproduces
direction on the held-out set (mean `ΔF < 0`, negative in ≥ 3 of 4), **then** goes to the
blind listen — gated by **A19**'s zero-blank-named-interiors assertion. Passing offline
**selects a candidate; it never adopts one.**

### 2.2 The continuation trigger — its own effect size, because it is a separate decision

The gating criteria decide *adoption*. This experiment exists to decide something else:
**is the builder-side p99 ceiling-rescale worth pre-registering and a rebuild?** Per
CLAUDE.md, that trigger needs its own effect size rather than borrowing `C1`'s.

Let **`M*`** = the most negative `C1` mean `ΔF` achieved by any arm on the ladder.
*Plain sentence, fixed now: **the best any toll price managed — how much less famous the
middle of a deeply-bypassed journey got, at whichever price worked best.***

| Trigger | Threshold | Why this size |
|---|---|---|
| **Live** | `M*` ≤ **−0.50** | Half of `C1`'s pre-registered −1.0, from **one knob alone**. If tolling the ceiling delivers half the required effect by itself, the remaining half is plausibly reachable by a builder-side fix that *removes* the ceiling rather than taxing it — and which additionally restores the ordering this cannot touch (§1 bound 1). That is the bar at which a rebuild is worth the owner's time. |
| **Partial** | −0.50 < `M*` ≤ **−0.25** | −0.25 is ~2.5× the **entire** spread of the eleven-arm stage-1 grid and ~1.4× `T1b`'s result, so it is the smallest movement that cannot be confused with grid noise. Movement that is real but cannot reach the bar alone. |
| **Null** | `M*` > **−0.25** | The whole ladder, including a near-ban, stays inside `T1b`'s neighbourhood. |

### 2.3 Reported, never gated

- **`TF-D1` — ceiling-edge usage per arm.** Count of score-1.0 edges used per snapshot path.
  *Plain: how many "expressway" hops the journey actually takes.* This is the direct
  mechanism measurement and the empirical check that `TFX` achieves a ban: if `TFX`'s usage
  is ~0, the price is prohibitive as designed; if it is not, those hops were unavoidable,
  which is itself the finding.
- **`TF-D2` — path length.** Mean and max interior count per arm at d ≥ 10. **WHAT-GOOD
  value 3** records that path length has a ceiling set by attention, that it is *unquantified*,
  and that it is discovered by use. **No threshold is read off it.** My own reporting trigger,
  stated as mine: if any arm's mean exceeds ~2× `P`'s, it is flagged and routed to
  `TEST-QUEUE.md` as a use-the-app question, not scored.
- **`TF-D3` — proxy coverage and the A11 d15/d20 notability flags**, per arm, per §0's
  non-constant.
- **`C5` (d0 no-regression inspection, vs both `P` and `A0` per A8) and the A14
  endpoint-fame tracking diagnostic**, unchanged from Track 2 §1.5.

---

## §3 The read of every possible result — written before any arm runs

Every branch below names the run state it presupposes: **all ten arms scored on the eight
analysis pairs.** No read is licensed from a partial ladder — and specifically, a read taken
before `TFX` has run cannot evaluate `TFR4`, which is the bound check every other read
depends on.

- **`TFR0` — the ladder nulls (`M*` > −0.25).**
  Read: **the similarity ceiling's cheapness is not what holds paths in famous territory.**
  `T1b`'s −0.177 was near this mechanism's ceiling, not the start of a curve.
  *Licenses:* recommending **against** spending a rebuild on the p99 ceiling-rescale *on the
  cheapness hypothesis*, and re-pointing the next probe at the other §2.4 branch,
  `cap_strategy`.
  *Does **not** license:* "the p99 ceiling is fine". §1 bound 1 is verified in code — the
  ordering half is untestable router-side, so it survives this null untouched. Anyone
  writing this up as "the ceiling is exonerated" is overstating it by exactly the half this
  design cannot see.

- **`TFR1` — partial (−0.50 < `M*` ≤ −0.25).**
  Read: the ceiling's cheapness is a real lever that cannot reach the bar alone.
  *Licenses:* recording the effect size and naming the builder-side rescale as the follow-up
  that would be decisive, with the number stated. *Does not license* a rebuild on this
  evidence alone — that is the owner's call and this is not enough to make it for him.

- **`TFR2` — live (`M*` ≤ −0.50), no arm passes `C1`–`C4`.**
  Read: the ceiling is a major lever, and the router-side probe has taken it as far as it
  goes.
  *Licenses:* **recommending** the owner pre-register the builder-side p99 rescale at the
  rebuild seam, where it joins the p99-shift measurement and the blank-name remediation.
  *Does not license:* adopting a toll arm, or treating the rescale as pre-registered — it
  needs its own document.

- **`TFR3` — an arm passes `C1`–`C4` outright.**
  Read: a genuine candidate exists, from a mechanism that was already the only signal in
  fifteen arms.
  *Licenses:* held-out confirmation (direction only, ≥ 3 of 4 — the adjudication §6 claim 45
  lesson), then the blind listen, gated by **A19**'s blank-name assertion.
  *Does not license:* adoption. **And it must be read against §1 bound 3:** a static toll
  passing `C1` while `C3` stays flat means the whole fame profile dropped rather than
  deepening with bypass count — which is `R3`'s shape, not a solution to F2.

- **`TFR4` — the bound check, evaluated on every outcome above.** Is `C1` mean `ΔF`
  **monotonically decreasing** in toll magnitude, and is `TFX` the most obscure arm?
  If **not**, `TFX` does not bound the family and every null above must be stated as *"these
  seven magnitudes do not move it"*, never *"the toll mechanism cannot move it"*. This is
  Track 2 **A17(c)** applied in advance rather than discovered afterwards: X was built to
  bound its family, did not, and only a pre-written falsifier caught it. Non-monotonicity is
  a live possibility here — banning ceiling edges may force paths through *other* famous
  non-ceiling artists — so this is a real check, not a formality.

- **`TFR5` — reproduction fails.** If `T1a_rpt` or `T1b_rpt` is not byte-identical to the
  committed stage-2 paths, **stop and report**. The harness has changed under us and no
  figure from this run is comparable to Track 2's. This is the repair+retune log §3.10 rule
  ("a non-identical path means stop, the harness is wrong") applied to the reproduction arms.

---

## §4 Protocol and pre-registered responses

**Run order, fixed:**

1. `verify_mirror.py` — proves the `toll_hops` addition changed no production behaviour.
2. `run_arms.py` for the full ladder, inheriting Track 2 stage 1's `dropped_cells_d7` (A13
   across the stage boundary, P8b F3).
3. **Reproduction gate:** `T1a_rpt` / `T1b_rpt` vs committed `paths_stage2.json`, byte-level.
   Fail → `TFR5`, stop.
4. `fame.py`, then `score.py` with `--blank-cells fail` (the loud default).
5. `TF-D1` ceiling-edge usage, computed offline from the paths and the artifact.

**Response if blank-named interiors appear** (§0's first non-constant), fixed now rather
than after seeing which arm trips it: apply **A13/A18**'s uniform drop — `score.py
--blank-cells drop` removes the affected **cell** from **every** arm including `P` — and name
every dropped cell in the write-up. **A node-level exclusion is rejected**, per A18: it would
silently improve whichever arm produced the blank. A rebuild is rejected as a response, per
A19: it changes the substrate.

**Response on proxy coverage** (§0's second non-constant): coverage is reported per arm, and
**A11's d15/d20 notability guard must be discharged before any figure is read as reach** —
`score.py` already reports which pairs reach below `B_unk` *only* via a flagged
potentially-notable-unmatched interior. If an arm's `C2` pass rests solely on flagged
interiors, that is reported as such and the pass is provisional on the owner's one-glance
check.

**Figures ownership.** `builder/analysis/2026-07-25-track2f-toll-ladder/` owns every figure
this run produces. Nothing in it restates a figure from the scoring adjudication, the Phase 1
log, the Track 2 arm-scorer directory, or the toll-calibration directory — those are cited.

**Determinism.** Offline, no network except `fame.py`'s cache-backed lookups, artifact
asserted by sha256, re-runnable.
