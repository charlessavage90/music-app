# A0-gate review — the floor's arm-invariance, the d1–d5 asymmetry, and the claim-23 wording

**Role: AUTHORITATIVE for its own measurements; ADVISORY on the protocol.** Written
2026-07-23 by the `ml-graph-analyst` subagent, reviewing the step-4 A0-vs-P result and the
argument built on it before the owner chooses between the three options recorded in the
repair+retune execution log ("Track 2 → Steps 2–4 executed"). Remit is **derivation, not
judgement**: nothing here says which option to take, whether the sweep is worth running, or
anything about product direction.

**No sweep arm was scored.** Prerequisite P4 is outstanding and the pre-registration blocks
arm scoring. Paths were routed only to measure mechanical quantities — floor-term firing,
path identity, in-graph popularity exposure. No fame proxy was touched; no ΔF, no C1/C2/C3
outcome exists in this document. Two floor-ON diagnostic twins (`A6r`, `Xr`) were
constructed here; they are **not pre-registered arms and are not candidates for anything.**

**Figures rule.** No measured figure from `2026-07-21-scoring-adjudication.md` or
`../2026-07-22-phase1-execution-log-and-graph-defect.md` is restated; those are cited by
section. New figures are owned by
[`builder/analysis/2026-07-23-track2-a0-review/README.md`](../../../builder/analysis/2026-07-23-track2-a0-review/README.md)
and reproduced here by reference.

**Housekeeping owed by the working session:** register this document in `docs/README.md`'s
map. This engagement may not edit that file.

---

## 0. What was measured, and against what

| Input | Identity |
|---|---|
| Artifact | `builder/scratch/graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`, asserted at the top of every script. N = 74,193, E = 898,006 |
| Router | `builder/analysis/2026-07-23-track2-sweep/mirror.py` — the verified byte-identical mirror, unmodified |
| Scripts | `builder/analysis/2026-07-23-track2-a0-review/` (`floor_asymmetry.py`, `trajectory_carryover.py`, `second_slice.py`); README owns the figures |
| Routed | 6 arms × 12 pairs × 21 depths, twice (two victim policies) = 1,512 walks. Guard G on throughout |
| Not done | any fame fetch, any scoring, any edit to shipped code or to the sweep directory |

**Reproduction check, unasked but free:** my independent P walk reproduces the sweep
directory's step-4 firing counts **exactly** at every depth. The step-4 measurement
replicates.

---

## 1. Q1 — is the unconditional-zero claim unconditional?

### 1.1 The floor's *value* is arm-invariant. CONFIRMED.

**MEASUREMENT (code).** `effective_floor_raw` (`api/src/artistpath_api/pathfinding.py:25-49`)
computes `max(0, base − relax_known·n_known − relax_dislike·n_dislike)`, where
`base = min(pop_raw[source], pop_raw[target])` (`:94`). It takes **counts by reason**, never
node identities. The mirror's `_relaxed_floor` (`mirror.py:123-127`) is the same function.
Nothing else in either cost function reads the exclusion list into the floor. The scripted
walk appends exactly one `KNOWN` exclusion per depth and never repeats a victim (an excluded
node cannot reappear as an interior), so at snapshot depth *d* every arm has exactly
*d* `known` bypasses.

**Therefore:** at a given (pair, depth), the floor **value** is identical across arms
regardless of which artists each arm bypassed. Confirmed, and it is a code property rather
than an empirical one.

One conditional the claim does not state: it holds **only while the walk reaches that
depth**. A guard-infeasible cell would break the correspondence between depth and bypass
count. **MEASUREMENT:** no walk terminated early in 1,512 routed walks — analyst **D7** did
not fire anywhere on this artifact under either victim policy. So the conditional is
satisfied here, not merely assumed.

### 1.2 The d6 threshold is wrong. REFUTED — the correct bound is d7.

**MEASUREMENT (README §1).** `ceil(base_raw / 0.15)` is **7** for seven of the twelve pairs,
6 for one, 5 for two and 4 for two. **Seven of twelve pairs carry a strictly positive raw
floor at d6** — largest 0.0982 (Radiohead → The Beatles), then 0.0403, 0.0396, 0.0307,
0.0285, 0.0280, 0.0313. Only from **d7** is the floor arithmetically zero on all twelve.

**MEASUREMENT (README §2).** At d6, up to **0.914 %** of all directed CSR entries have a head
below that pair's floor, so an arm exploring differently *could* fire the term there. The
zero at d6 is a fact about what P's search examined, not arithmetic.

**MEASUREMENT (README §3).** Empirically it is robust anyway: all three floor-ON arms —
including `Xr`, the floor-ON twin of the most aggressive corner — fire **zero** times at d6
and d7 on every pair. So the recorded number is right; its stated justification covers only
d ≥ 7.

**Effect on the scored window: none.** C1 scores d ≥ 10, C2 d15/d20, C3 d5 and d20, and the
snapshot set is {0,1,2,3,5,7,10,15,20} — d6 is not a snapshot and d7 is arithmetically zero.
The sentence "**it is zero for every raw-floor arm at every scored depth, unconditionally**"
is, as applied to scored depths, **correct**. Only the "from d6" span is over-broad.

### 1.3 The larger problem: value-invariance is not effect-invariance. REFUTES the record.

**MEASUREMENT (README §5, both slices).** The floor term is identically zero at every depth
≥ 7, yet floor-ON and floor-OFF twins of the same arm **still return different paths there**:

| | d5 | d10 | d15 | d20 |
|---|---|---|---|---|
| P vs A0 (slice 1 / slice 2) | 0/12 · 0/12 | **0/12 · 0/12** | 0/12 · 0/12 | 0/12 · 0/12 |
| A6r vs A6 | 1/12 · 0/12 | 1/12 · 0/12 | 1/12 · 0/12 | 1/12 · 0/12 |
| Xr vs X | 5/12 · 7/12 | **5/12 · 4/12** | 2/12 · 2/12 | **2/12 · 2/12** |

The mechanism is not the cost term. The bypass walk is **driven by each arm's own paths**, so
a path the floor changed at d0–d2 changes which artist is bypassed, and the exclusion sets
never re-converge. The floor's influence is *inherited* into the scored window even though
its value there is exactly zero.

**Consequence for the record — this contradicts a statement already put to the owner.** The
execution log's option-1 row says the eight added floor-on cells "can differ from their
floor-off twins **only at d0–d5**, by the arithmetic in finding 2". Measured, they differ at
d20 in 2 of 12 pairs in the X family, on **both** victim policies. Option 1 therefore buys
more information than its own consequence column credits it with — and, symmetrically, a
crossed floor column does **not** yield a clean one-knob attribution at depth, because what
differs there is a trajectory, not a term.

**Stability, stated explicitly.** The P/A0 result (no carry-over past d2) and the Xr/X result
(2 of 12 at d20, and the *same two pairs* both times) reproduce across both victim policies.
The **A6r/A6 carry-over does not reproduce** — 1/12 from d9 on slice 1, 0/12 from d2 on
slice 2. Do not quote the A6 figure without that caveat.

**INFERENCE.** The two persistently-divergent pairs are Radiohead → The Beatles and
Muse → Coldplay — exactly the two direct-edge pairs where guard G forces a masked re-run, so
the walk enumerates single intermediaries and one different first pick permanently reorders
the enumeration. *Falsifier:* a non-direct-edge pair showing the same permanent divergence,
or these two re-converging under a third victim policy.

### 1.4 Two currencies the "zero from d6" statement silently excludes

**MEASUREMENT (arithmetic, README §1).** `floor_relax_dislike = 0.08` is the smaller step, so
on the largest base floor the raw floor survives to **d12** under an all-`dislike` walk and
**d13** is the universal bound for any mix of signals. Stage A is all-`known`, so the sweep is
unaffected — but §1.5's **F4 dislike walk** runs on P and on the winner, and the shipped
router serves users who mix signals (§6.6). "The raw floor is dead after five bypasses" is
true of the scripted protocol and **not** of the product.

---

## 2. Q2 — how large is the d1–d5 asymmetry, and are C3 and C5 confounded?

### 2.1 The asymmetry is real, large, and confined to d0–d2

**MEASUREMENT (README §4).** Path-level floor exposure — what the chosen path would pay in
floor cost — pooled over 12 pairs, `w_hop = 0.02`:

| | d0 | d1 | d2 | d3–d7 |
|---|---|---|---|---|
| P mean path floor cost | 0.0086 (0.43 `w_hop`) | **0** | 0 | 0 |
| X mean path floor cost | **0.2298 (11.5 `w_hop`)** | **0.0905 (4.5 `w_hop`)** | 0.0037 | **0** |
| P interiors below floor | 4 of 35 | 0 | 0 | 0 |
| X interiors below floor | **12 of 27** | 9 of 28 | 1 of 28 | 0 |
| X largest single shortfall | **0.3701 (18.5 `w_hop`)** | 0.2264 | 0.0443 | 0 |

So the brief's suspicion is **confirmed at d0–d2 and refuted from d3**. At d0 a diving arm's
path carries 26.7× P's floor debt, and its worst single hop would be tolled 18.5 `w_hop` —
between the two pre-registered toll magnitudes. From **d3 the exposure is exactly zero for
every arm tested, including the corner X.** The relaxation-level view agrees: `Xr` fires
3.6× more often than P at d3, 12× at d4, and both are in single-digit counts by d5.

The structural ceiling is much higher than what any arm actually did — at d5, up to 10.44 %
of directed edges have heads below the floor on Radiohead → The Beatles, versus 30
relaxations actually fired. So the asymmetry is bounded by routing behaviour, not by the
floor's arithmetic.

### 2.2 A one-knob result that lands on log §2.12's mechanism

**MEASUREMENT.** `X` versus `A6` differ in exactly one *live* term: `w_jump` 0.3 → 0. (Their
jump currencies differ on paper, but at `w_jump = 0` the currency is inert — code read,
`mirror.py:200`.) Turning that one knob raises the d0 path's floor debt from 0.0094 to
0.2298 (**24×**) and the largest single shortfall from 0.0518 to 0.3701 (**7.1×**), and takes
below-floor interiors from 4 of 31 to 12 of 27.

**INFERENCE.** `w_jump` is indeed what holds paths near the floor — log §2.12's mechanism is
directionally right and now has a one-knob demonstration it never had. What is wrong is the
word *prevents*: it **bounds** the dip (every production-strength arm dips by at most 0.0518)
rather than eliminating it. *Falsifier:* an arm at production `w_jump` dipping as deep as X,
or X failing to dip deeper than A6 on a second pair set.

### 2.3 C3's d5 anchor — NOT confounded as the factorial is designed

**MEASUREMENT + code.** Every factorial cell A0–A7 carries floor **off**, so the floor term is
not in the candidate's cost at all, and C3 is a **within-arm** comparison (candidate d20 vs
candidate d5). There is no floor asymmetry to confound it. Corroborating: even with the floor
switched on, path-level exposure at d5 is **zero for all three floor-ON arms**.

Two qualifications, both real:

1. **Under options 1 or 3** (floor crossed), floor-ON and floor-OFF twins differ at d5 in
   5/12 (slice 1) or 7/12 (slice 2) cells. But that difference is **inherited from d0–d2**,
   not generated at d5 — the floor fires ≤ 30 times at d5 in any arm. A d5 anchor is
   therefore not measuring a live floor; it is measuring a trajectory.
2. **For the FL arms this reverses, and it is worth stating before those arms run.**
   **MEASUREMENT (arithmetic):** with A2's relax of 0.05, `pctl_floor(d5) ≈ 0.74–0.75` on ten
   of twelve pairs and `pctl_floor(d20) = 0` on all twelve. **INFERENCE:** an FL arm is
   forbidden from routing below roughly the 74th in-graph popularity percentile at d5 and
   entirely free at d20, so C3's gradient is substantially **manufactured by the device**
   rather than evidence that the cost knobs promote diving. This is not a design error — the
   FL arms exist to be the depth device — but a C3 pass for an FL arm should not be read as
   the same evidence as a C3 pass for a floor-off cell. *Falsifier, and it is cheap:* route
   an FL arm at d5 with the floor forced off and compare interior composition; if unchanged,
   the device was not binding and this inference is wrong. **I did not run it** — it is
   outside the question I was asked.

### 2.4 C5's d0 comparison — CONFOUNDED, and the size is one cell

**MEASUREMENT.** C5 compares candidate d0 against **P** d0, and P's floor is live at d0
(fires on half its relaxations). The candidate's floor is off. So the d0 diff carries the
candidate's knobs **plus** the removal of the floor. The size of that extra component is
exactly the P-vs-A0 d0 difference: **1 of 12 pairs, on both slices** — Miles Davis → Daft
Punk, one interior substituted (Dean Martin 0.6668 → Michael Bublé 0.6563) and payload 6 → 5.

**Direction:** the floor gives the baseline one extra interior and a shallower dip on that
pair, so a floor-off candidate inspected against floor-on P looks marginally worse on payload
and marginally deeper on that one pair, for reasons that are not its knobs.

**Small in count, but note where it lands:** that pair is the canonical listen pair *and* the
F6 trace pair, i.e. the cell most likely to be looked at by hand. C4 is unaffected — it scores
d ≥ 10, where P and A0 are identical on both slices.

---

## 3. Q3 — is the claim-23 falsification correctly stated?

### 3.1 What claim 23 actually says

**Code/document read.** Adjudication §6 row 23 records the prior claim as "`w_floor` is a
provable no-op" (origin: an earlier findings §5.3), adjudicated in §5.4 on a seeded random
pair set on the **v3** graph. §5.4's own text carries two sub-claims — path identity under
`w_floor = 0`, and no path having an interior below `min(pop_source, pop_target)` — plus a
prescription to delete `w_floor` and `floor_relax_*`. **§5.4 does not contain the `w_jump`
mechanism.** That sentence lives in **log §2.12** (and is echoed in log §3.3), and the
pre-registration §0's box cites the two jointly, which is the likely source of the conflation.

### 3.2 What should be recorded — precisely

**Should be recorded as overturned:**

- **The mechanism, cited to log §2.12, not to claim 23.** "`w_jump` prevents paths from
  dipping below the floor in the first place" is false on this artifact and pair set: paths
  dip at d0 in every arm. Record it against **log §2.12** (and §3.3's restatement).
- **Claim 23's second sub-claim — that no routed path has an interior below the floor — does
  not transfer** to `graph-t15-tiebreakfix.bin` under the 12 pre-registered pairs. Both P and
  A0 dip at d0.

**Should be recorded as *nearly* upheld, with its scope named:**

- **Claim 23's headline — `w_floor` is a no-op for path outcomes — holds in 251 of 252 cells**
  and fails in one. "Provable no-op" is refuted as an absolute; "no-op in all but one cell of
  this grid" is what the evidence supports.

**Should NOT be recorded:**

- **Not "claim 23's mechanism is falsified".** Claim 23 has no mechanism; attributing one to
  it puts a wrong sentence into the §6 table that a later reader will cite back.
- **Not "the term firing on half of all d0 relaxations falsifies claim 23".** A relaxation is
  an edge examined during Dijkstra, not a path node. Claim 23 is about **paths**. The firing
  rate is the PR-A diagnostic — it says the term is *reachable*, not that it *binds*. Both
  statements can be true at once and the record should keep them apart.
- **Not a retraction of the original measurement.** Claim 23 was measured on a different
  graph, a different (random) pair population, and without bypasses. This is a **non-transfer
  to a new artifact and a famous-endpoint pair set**, which is exactly the state the prior
  protocol review's item 1d flagged as CANNOT DETERMINE. It is now determined; the earlier
  measurement is not thereby wrong.
- **Not anything about the percentile floor.** Nothing here touches the FL arms' device
  beyond the arithmetic in §2.3.

**And one thing that should be added, because it cuts the other way** (§2.2): a one-knob
contrast now shows `w_jump` increasing the dip 24× in floor-cost terms when it is removed. The
log §2.12 mechanism is **refined, not demolished** — `w_jump` bounds the dip rather than
preventing it. A §6 row saying only "falsified" would lose that, and it is the more useful
half.

---

## 4. Weakest link

The load-bearing assumption in everything above is that **the scripted victim policy is a
fair probe of the trajectory-inheritance effect.** Both slices are deterministic, in-graph,
and drive on popularity; a real user drives on fame and mixes signals (analyst O1, §6.6). If
inheritance is policy-specific, §1.3's carry-over shrinks or grows and I cannot say which. I
would defend §1.1 (code), §1.2 (arithmetic), §2.1 and §2.4 (direct measurement, both slices)
without qualification. I would abandon cheaply: the A6-family carry-over figure (already
unstable), and the §1.3 INFERENCE about *why* the two direct-edge pairs persist.

A second, smaller one: my `Xr`/`A6r` twins are constructions, not pre-registered arms. They
answer "what would a raw floor do inside a diving arm" and nothing else.

---

## 5. Options and their consequences — no recommendation

For the C5 d0 confound (§2.4):

| Option | Consequence | What works today only because of the property it removes |
|---|---|---|
| Report the d0 inspection against **both** P and A0 | **Costs zero extra runs — A0 *is* floor-off P, and its full grid already exists.** P answers "what would the owner notice"; A0 answers "what did the candidate's knobs do" | Nothing. Adding a second reference removes no property |
| Leave C5 referenced to P only, as §1.5 says | One cell of 12 carries an unattributed component — on pair 1 | The inspection stays anchored to shipped behaviour, which is what a no-regression guard is for; switching to A0 alone would silently drop that |

For C3's low anchor (§2.3):

| Option | Consequence |
|---|---|
| Keep d5 | Unconfounded for floor-off cells — measured, §2.3. Only options 1/3 and the FL arms complicate it |
| Move the low anchor to **d6** | d6 is **not** a pre-registered snapshot, so it adds a walk-recording depth, and the floor is still non-zero at d6 on 7 of 12 pairs (§1.2) — it is the one depth that is neither clean nor free |
| Move the low anchor to **d7** | d7 **is** a snapshot and the floor is arithmetically zero there on all 12 pairs. But the −0.5 threshold was pre-registered against a d5→d20 span; shortening the span changes the criterion's strictness by an amount **nobody has measured**, and re-deriving the threshold after seeing d7 data would break the pre-registration |

For the floor column itself:

| Option | What the measurements say about it |
|---|---|
| Cross the floor fully (log option 1) | Its stated consequence is wrong in the owner's favour: added cells differ from their twins at d20 too, not "only at d0–d5" (§1.3). But the extra information is **trajectory inheritance**, not a floor effect at depth, so it does not deliver a clean one-knob floor column at depth either |
| Narrow amendment, floor off across the factorial (log option 2) | Its premise survives, on a **stronger** measurement than the one offered: P vs A0 is identical at every depth ≥ 1 on both slices, so C1's baseline carries no inherited floor effect. Its stated *reasons* need two corrections — the bound is d7 not d6, and the argument must be about *effects*, not the term's value |
| Cross only to d5 (log option 3) | Would not capture the inheritance measured at d10–d20 (§1.3), so it is not "the same information, cheaper" |
| **Any option** | **What works today only because `w_floor` is on:** exactly one production behaviour on this grid — pair 1's d0 path gains a sixth interior and a shallower dip. And `known`'s only non-exclusion behaviour is the floor relax feeding this term (log §3.3), so with `w_floor = 0` the two bypass signals differ **solely** through avoidance. Whether that matters is a product question, not mine |

---

## 6. Categories with nothing in them

Stated rather than padded:

- **No defect found in the mirror.** I re-ran P through it and reproduced the step-4 firing
  counts exactly; the term-order, branch-not-`+0.0`, and `(cost, node)` heap decisions are
  present in the code as documented.
- **No defect found in `run_a0.py`'s protocol.** The walk maintains exactly one bypass per
  depth, victim selection matches the pre-registration, and guard G is on in both arms.
- **No arm-correlated missingness.** D7 did not fire in 1,512 walks.
- **No error found in amendment A2's arithmetic** for the percentile floor's survival span; I
  checked it independently and it holds on all 12 pairs.
