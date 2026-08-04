# Cap re-evaluation results (`CRE-`) — the four-part read

**Role: AUTHORITATIVE for the `CRE-` experiment's results.** Raw record:
`builder/analysis/2026-08-03-cap-reevaluation/cre_scores.json` (plus `cre_screen.json`,
`cre_d1.json`, `cre_d3.json`, `cre_gates.json` and the sixteen `cre_sweep_*.json`), all
committed before this document was opened. Criteria, bars, effect sizes and read order are
the pre-registration's
([`specs/2026-08-03-cap-reevaluation-preregistration.md`](../specs/2026-08-03-cap-reevaluation-preregistration.md),
`CRE-`, frozen `3d7b7d6`, amended `CRE-AM1` and `CRE-AM2`, both before any stage ran).
Execution reasoning: [`2026-08-03-cre-run-execution-log.md`](../2026-08-03-cre-run-execution-log.md).

**Written by a session that did not run the sweeps** — the prereg's §4 Stage 3 requirement
and the reason Seam 3 exists. Every figure below was read from the committed JSON, not from
any session's prose summary.

**What this licenses, and nothing more** (prereg §preamble): a recommendation input to the
owner's parked decisions. **No adoption, no default change, no shipped-code change, and the
blind listen (`REQ-38`) is owed before any adoption regardless of every number here.**

---

## §0 — Summary, including what cuts against it

**Two arms cleared the primary bar, both on the candidate data set, and both did it with a
measurement hole that opened as they descended.**

`B-S1-P1a` and `B-S1-P1b` — the candidate archive (`ALG-B`), pooled-then-trimmed
connections (`CRE-S1`), plus the depth-graduated `known` ramp at 0.01 and 0.03 per press
(`CRE-P1`) — pass `CRE-C1` on both of its binding clauses, are not killed by `CRE-C2`, are
not disqualified by `CRE-C3`, and clear `CRE-C4`'s binding payload floor. **`CRE-R2` fires
for both.** No `ALG-E` arm moved the gradient at all: all six production-data candidate cells
— and both scramble companions — sit inside the instrument's own no-movement band.

**What cuts against it, and none of it is optional reading:**

1. **Both passing arms trip §0.4's censoring trigger.** The share of delivered artists the
   fame ruler cannot score rises from 0 % at depth 0 to 10.8 % (`B-S1-P1a`) and 16.4 %
   (`B-S1-P1b`) in the depth-10–20 band, against a 0.05 trigger. Per §0.4 their `CRE-C1`
   **must be reported as "descent partly unmeasurable", never as a clean pass.** It is so
   reported throughout this document.
2. **On the pairs where nothing drops out of measurement, `B-S1-P1a` does not clear the
   bar.** Its matched-only median is −0.0405 against a −0.05 material bar, on 8 pairs — at
   the readability floor exactly. `B-S1-P1b`'s matched-only set is 5 pairs, **below the
   floor of 8, so that comparison is unreadable rather than favourable.**
3. **No clear winner exists.** `CRE-R4` — *the rule that decides whether one arm is far
   enough ahead of the others to be called the winner rather than one of several options* —
   has its clause (i) fail for both arms: neither meets the bars on both data sets, and each
   has another non-staged arm meeting them. Per `CRE-R4`
   this document presents options, not a recommendation.
4. **The supply rule cannot be credited on its own.** The `w_floor` guard flags all nine
   supply comparisons, so no sentence here attributes an outcome to the connection rule
   alone (§0.3).
5. **Tags and votes are credited with nothing.** `CRE-C5`'s entry condition was not met —
   the tag-limited build's gain over its baseline was −0.0012 where entry needs −0.05 — and
   both scramble companions' paired confidence intervals include zero.

**And the standing bar, quoted rather than paraphrased: "the family space is exhausted" is
barred.** This design ran two bounds of family (a), one member each of families (b) and (c),
two ramp settings of one pricing device, and family (d) as reference only. The unrun
remainder is named in §5.3.

---

## §1 — Measured

### 1.1 Run state

Every read below presupposes the full run state, and it is met. Sixteen sweep cells have a
committed JSON; three cells (`E-S2-P1a`, `B-S2-P0`, `B-S2-P1a`) are **branch-excluded, not
unrun** — `CRE-D1` fired `not_supported`, so those rows do not exist. Both `P1` ramp settings
ran in every cell carrying them; the branch-proof probe cell `E-S2-P0` ran; both staged `S3`
comparison cells ran. `cre_r_readable` is `true`.

**`CRE-G3`** — *"we only compare journeys that exist in every variant being compared, and
only when enough survive to say anything."* All 22 drawn pairs survive on both cleaned
substrates; none lost an endpoint. Per-comparison readable floor: 8 pairs. The uniform-drop
partition (pin 9, four groups) dropped **zero (pair, depth) cells** in any group.

**Instrument gates, all green:**

| Gate | Result |
|---|---|
| `CRE-G1`(a) mirror ≡ production router, `E-S0`, all pairs | PASS — 22/22 identical, 0 diverged |
| `CRE-G1`(a) **red control** — same comparison with the mirror's `w_hop` moved off production's (0.05) | PASS — 3 pairs diverge, so the comparison *can* fail |
| `CRE-G1`(a) QA run on `B-S0` (reported, not a bar — the prereg gates `E` only) | 22/22 identical |
| `CRE-G1`(b) every `P1` cell's d0 ≡ its `P0` baseline's d0 | PASS in all five `P1` cells |
| `CRE-G1`(c) ruler frame N = 74,151 | PASS |
| `CRE-G2`(a) liveness at instrument-only extreme (r = 1.0), bar 0.5 | PASS in all three `P1`-carrying graph cells — `E-S1` 17/22 (0.773), `B-S0` 21/22 (0.955), `B-S1` 22/22 (1.000) |
| `CRE-G2`(b) recorded toll ≡ formula at k = 1 and k = 10 | PASS in all five `P1` cells (44 assertions each) |

The red control is the part worth pausing on: `CRE-G1`(a) is an exact-identity test, and an
identity test that has never been shown to fail is not evidence. It was shown to fail.

### 1.2 Stage 0 — the two cheap reads

**`CRE-D1`** — *"on today's map, do two very popular connected artists share fewer meaningful
style labels than two obscure connected artists do?"* Size-matched difference **+0.052**;
supported iff ≤ −0.05. **Branch: `not_supported`**, measured in the opposite direction to the
hypothesis. Consequence, binding: the three `(D1-branch)` cells do not exist and no
router-side tag arm does.

**`CRE-D3`** — *"before building anything, confirm on today's map that the new pricing knob
alone still does nothing for famous-pair journeys — so that if nothing moves later, we know
the question was always supply."* **Branch: `inert_as_expected`.** Its `P0` reference median
is −0.00046 with 21 of 22 pairs inside the quantisation floor.

### 1.3 Stage 1 — the structural screens

**`CRE-C3`** — *"does this rule cut around ten thousand artists or more off the map
entirely?"* Disqualification at 10,000. **Nothing came close and nothing is disqualified:**

| Cell | Cleaned pre-cap population | Kept | Artists lost |
|---|---|---|---|
| `E-S0` | 65,761 | 64,724 | 1,037 |
| `E-S0b` | 65,761 | 65,416 | 345 |
| `E-S1` | 65,761 | 65,679 | 82 |
| `E-S2` | 65,761 | 65,596 | 165 |
| `E-S3` | 65,761 | 65,719 | 42 |
| `B-S0` | 63,525 | 58,851 | **4,674** |
| `B-S0b` | 63,525 | 63,041 | 484 |
| `B-S1` | 63,525 | 63,056 | 469 |
| `B-S3` | 63,525 | 63,472 | 53 |

**`CRE-C6`** — *"for each journey, does this map offer anywhere meaningfully less famous to
go, within one step of the journey?"* **Zero zero-supply pairs in every cell; nothing
screened out.** Median 1-hop headroom, which §0.4 makes the only honest denominator for
putting the two data sets in one sentence: **0.7395 on `ALG-E`, 0.9966 on `ALG-B`.**

### 1.4 Stage 2 — the criteria

The `C1`/`C2`/`C4` tables below cover the twelve **candidate** cells. The two scramble
companions are instrument cells and appear under `CRE-C5`; the two staged `S3` cells are
barred from candidacy and appear at the end of this section.

`CRE-C1` — *"after ten or more presses of 'I know them', is the typical artist in the middle
of the journey meaningfully less famous than the ones shown before any press?"* Pass is the
conjunction of **(i)** arm median ≤ −0.05 and **(ii)** the 95 % pair-level bootstrap upper
bound ≤ −0.015. Instrument floor for "no measured movement": |Δ| < 0.015.

| Cell | Baseline | `C1` median | CI upper | (i) | (ii) | pairs ≤ −0.05 | pairs in floor | LOO range |
|---|---|---|---|---|---|---|---|---|
| `E-S0-P0` | — (anchor) | −0.0003 | +0.0009 | ✗ | ✗ | 0 | 20 | −0.00034 … −0.00030 |
| `E-S0b-P0` | `E-S0-P0` | −0.0006 | −0.0003 | ✗ | ✗ | 1 | 21 | — |
| `E-S1-P0` | `E-S0-P0` | −0.0002 | +0.0006 | ✗ | ✗ | 0 | 21 | — |
| `E-S1-P1a` | `E-S1-P0` | −0.0003 | +0.0001 | ✗ | ✗ | 1 | 20 | — |
| `E-S1-P1b` | `E-S1-P1a` | −0.0005 | −0.0002 | ✗ | ✗ | 1 | 20 | — |
| `E-S2-P0` | `E-S1-P0` | −0.0014 | −0.0003 | ✗ | ✗ | 1 | 19 | — |
| `B-S0-P0` | `E-S0-P0` | −0.0028 | −0.0007 | ✗ | ✗ | 2 | 16 | — |
| `B-S0b-P0` | `B-S0-P0` | −0.0031 | +0.0009 | ✗ | ✗ | 1 | 15 | — |
| `B-S1-P0` | `B-S0-P0` | −0.0029 | −0.0013 | ✗ | ✗ | 3 | 14 | — |
| `B-S0-P1a` | `B-S0-P0` | **−0.0413** | −0.0099 | ✗ | ✗ | 11 | 9 | −0.0502 … −0.0324 |
| **`B-S1-P1a`** | `B-S1-P0` | **−0.0622** | **−0.0337** | **✓** | **✓** | **12** | 4 | −0.0647 … −0.0597 |
| **`B-S1-P1b`** | `B-S1-P1a` | **−0.6163** | **−0.1524** | **✓** | **✓** | **18** | 2 | −0.6352 … −0.5973 |

`B-S0-P1a` sits above the instrument floor and below the material bar; per §5 it is reported
as **"movement below the material bar"** and as nothing else.

**Per-class, for the two passing arms** (both classes clear the ≥ 8 readability floor):

| Cell | `ff-top01pct` (n = 10) | `ff-top1pct` (n = 12) |
|---|---|---|
| `B-S1-P1a` | −0.098 (both clauses ✓) | −0.0622 (both clauses ✓) |
| `B-S1-P1b` | −0.7105 (both clauses ✓) | −0.5959 (both clauses ✓) |

**The censoring companions §0.4 requires beside every `C1` figure:**

| Cell | null share d0 | null share d10–20 | rise (trigger 0.05) | matched-only median / n | d3–5 band (never a bar) |
|---|---|---|---|---|---|
| every `ALG-E` cell | 0.000 | 0.000 | 0.0000 | −0.0002 … −0.0017 / 22 | ≈ 0 |
| `B-S0-P0` | 0.000 | 0.001 | 0.0013 | −0.0034 / 16 | −0.0027 |
| `B-S1-P0` | 0.000 | 0.011 | 0.0106 | −0.0030 / 17 | −0.0010 |
| `B-S0-P1a` | 0.012 | 0.059 | 0.0471 | −0.0112 / 11 | −0.0149 |
| **`B-S1-P1a`** | 0.000 | 0.108 | **0.1077 — trips** | **−0.0405 / 8** | −0.0125 |
| **`B-S1-P1b`** | 0.000 | 0.164 | **0.1641 — trips** | **−0.0933 / 5 — below floor, unreadable** | −0.2930 |

The **absent-from-snapshot** counter reads **zero in all sixteen swept cells** — 0 of 30,516
interior slots. It is live but unfired (the liveness question closed at Seam 3), so no
delivered artist was ever scored on a missing measurement. The null-in-snapshot counter, by
contrast, fires exactly where §0.4 predicted: 0 on every `ALG-E` cell, and 17 to 245 slots on
the `ALG-B` cells, rising with descent.

**`CRE-C2`** — *"as you keep pressing, does the journey lean more and more on the map's
most-connected artists — or park on them outright?"* Kill at delta ≥ +0.10 **or** d10–20
level > 0.50. **Nothing is killed anywhere.** Base rates are quoted because §5 requires it: a
null delta is not reassurance, since every measured descent arm moves the delta negative.

| Cell | d0–2 share (base rate) | d10–20 share | delta |
|---|---|---|---|
| `E-S0-P0` | 0.249 | 0.159 | −0.0896 |
| `E-S1-P0` | 0.225 | 0.138 | −0.0873 |
| `E-S2-P0` | 0.217 | 0.100 | −0.1174 |
| `B-S0-P0` | 0.099 | 0.071 | −0.0283 |
| `B-S1-P0` | 0.119 | 0.071 | −0.0481 |
| `B-S0-P1a` | 0.092 | 0.077 | −0.0150 |
| **`B-S1-P1a`** | 0.107 | 0.073 | −0.0347 |
| **`B-S1-P1b`** | 0.081 | 0.058 | −0.0236 |

Reference set is the production artifact's top-degree set, as §5 fixes; own-graph shares are
in the JSON. First-path hub transit is reported, never gated (owner ruling).

**`CRE-C4`** — *"after ten or more presses, is the journey still delivering a comparable
number of artists, or has it mostly just got shorter?"* Binding form is arm ÷ isolating
baseline ≥ 0.70; the two anchors carry no binding form (`CRE-AM2`).

| Cell | absolute median (ref. line 0.75) | binding ratio | ≥ 0.70 |
|---|---|---|---|
| `E-S0-P0` | 1.795 | — no binding form (anchor, `CRE-AM2`) | — |
| `E-S0b-P0` | 1.455 | 0.810 | ✓ |
| `E-S1-P0` | 1.788 | 0.996 | ✓ |
| `E-S1-P1a` | 1.155 | **0.646** | **✗ — fails the binding floor** |
| `E-S1-P1b` | 1.045 | 0.905 | ✓ |
| `E-S2-P0` | 1.469 | 0.822 | ✓ |
| `B-S0-P0` | 1.640 | — no binding form (anchor, `CRE-AM2`) | — |
| `B-S0b-P0` | 1.515 | 0.924 | ✓ |
| `B-S1-P0` | 1.576 | 0.961 | ✓ |
| `B-S0-P1a` | 1.386 | 0.845 | ✓ |
| **`B-S1-P1a`** | 1.390 | 0.882 | ✓ |
| **`B-S1-P1b`** | 1.477 | 1.063 | ✓ |

**One cell fails `C4`: `E-S1-P1a`**, at 0.646 against the 0.70 floor. It delivers about a
third fewer artists than its own baseline while moving the gradient by −0.0003 — payload
spent for nothing. **It does not fire `CRE-R3`**, which requires a `C1` *pass* alongside the
`C4` fail, and `E-S1-P1a` fails `C1`. **No cell fires `CRE-R3`.** Everywhere else paths
lengthen rather than shorten under the ladder; lengthening is reported and never rewarded
(`REQ-14`).

**`CRE-C5`** — *"is the improvement actually coming from what the labels say — or would
scrambled labels have done the same?"* Entry condition: real Δgain ≤ −0.05.

| Quantity | Value |
|---|---|
| `E-S2-P0` real Δgain vs `E-S1-P0` | **−0.0012** — entry condition **not met** |
| label-scramble companion Δgain | −0.0016; paired difference CI [−0.0007, +0.0016], includes zero |
| vote-scramble companion Δgain | −0.0006; paired difference CI [−0.0011, +0.0005], includes zero |

**Attribution does not hold on either companion.** No sentence of the form "tags did this" or
"votes did this" is licensed anywhere in this document. There is no `B-S2` cell for the
`CRE-AM1` share obligation to attach to, and that is recorded explicitly rather than by
omission.

**`CRE-D2` / the `w_floor` guard.** The floor term's share of chosen-path cost at d10–20 is
**0.000 in every cell**; all differential firing is at d0, ranging from 0.0020 to 0.106
absolute. The guard's rule is deliberately conservative — any non-zero differential sets the
flag — so **all nine supply comparisons are flagged**, and §0.3's bar applies: no sentence
here attributes an outcome to the supply knob alone. The pricing knob is exempt by
construction (§0.3: the ramp is identically zero at d0, and the floor is identically dead at
d10–20).

**Staged reference cells, `CRE-S3`** — *"no cap at all; the journey-builder does all the
bounding."* `E-S3-P0` `C1` = −0.0004, `B-S3-P0` `C1` = −0.0016; neither moves, and both are
**barred from candidacy and from every `CRE-R` winner clause**. §3.1's two halves, quoted
together as that section requires: its prior condemnation is confounded evidence under a
superseded definition of good, *and* its structural cost is measured fact.

### 1.5 The read determinations

These are mechanical — every bar was fixed before any result existed.

| Read | Fires? | Basis |
|---|---|---|
| **`CRE-R0`** — *"nothing we tried makes the bypass button dig, on either data set."* | **No** | Two non-staged arms pass `C1` on readable classes |
| **`CRE-R1`** — a passing arm on the production data set | **No** | No `ALG-E` arm clears either `C1` clause |
| **`CRE-R2`** — a passing arm on the candidate data set only | **Yes, twice** | `B-S1-P1a` and `B-S1-P1b`: `C1` (i)+(ii) ✓, `C2` not killed, `C3` not disqualified, `C4` ≥ binding floor |
| **`CRE-R3`** — *"the journey got 'less famous' mainly by getting shorter — fewer artists delivered, not more discoveries."* | **No** | `C4` passes in both; shape flag false |
| **`CRE-R4`** — *is one arm far enough ahead of the others to be called the winner?* | **No clear winner** | Clause (i) fails for both: neither meets the bars on both data sets, and each has another non-staged arm meeting them |

`CRE-R4`'s clause (ii) is reported for completeness even though clause (i) already bars the
call. **Computed at Stage 3 from the committed per-pair deltas using clause (ii)'s
pre-registered form — this statistic is not in `cre_scores.json`:** on the 22-pair common
set, median(`B-S1-P1a` − `B-S1-P1b`) = **+0.0649**, 95 % percentile bootstrap CI
[+0.0026, +0.3329], excluding zero. So `B-S1-P1b` would lead `B-S1-P1a` on clause (ii)'s
terms. **This changes nothing** — clause (i) is not satisfiable by either arm, and per
`CRE-R4` the note presents options.

**`CRE-R2`'s standing citations, per §6**, attach to both arms: the §0.4 rows (composition,
censoring, headroom); adoption retires every existing path-quality figure and owes a blind
listen; switching data set is the `BuilderConfig.algorithm` re-crawl decision.

### 1.6 One ambiguity in `CRE-R4`, resolved here and recorded rather than resolved silently

**`CRE-R4`'s clause (i) turns on what counts as "an arm", and the pre-registration uses that
word two ways.** Everywhere it is *measured* — `CRE-C1`'s "arm statistic", `CRE-C2`'s
"per-arm kill", `CRE-C4`'s "arm `C4` ÷ its isolating baseline's `C4`" — an arm is a **cell**,
one row of §0.2. But `CRE-R4`'s own clause (iii), "explored on no fewer ramp settings than
any arm it beats", presupposes that an arm can *carry* several ramp settings, which a cell
cannot.

**Resolved as arm = cell**, on three grounds: every criterion that produces a number is
computed per cell; §0.2 gives each cell its own isolating baseline, which is what clause (i)
compares against; and the alternative reading is not merely different but incoherent — under
"arm = supply configuration", `B-S1` would have to both pass and fail, since `B-S1-P1a` and
`B-S1-P1b` clear the bars while `B-S1-P0` does not. Clause (iii) is then read as comparing
the ramp exploration of the *supply configurations behind* two competing cells, which is what
its stated purpose ("no clear-winner call from an asymmetrically explored pricing axis")
requires.

**It is recorded because the stakes are not zero and the resolution is not self-evident.**
Under arm = cell, clause (i)'s second disjunct fails for each passing arm because the other
one is its counterexample — which is the whole reason there is no clear winner. A reader who
took the other reading would find that disjunct satisfied and could arrive at a clear-winner
call. That reading does not survive contact with the rest of the document, but nothing stops
someone reaching for it, so the argument is written down here rather than left to be
re-derived. **No bar was moved and no criterion was reinterpreted to reach a result** — this
was settled from §0.2 and §5's own wording, and it is the reading under which the experiment
was already scored.

---

## §2 — What I infer from it, in plain language

*This section is inference, labelled as such. It is written so that someone who has never
heard of a bootstrap confidence interval can disagree with it.*

**The "I know them" button now digs — but only on the map built from the other data source,
and only when a second change is made too.**

Today, pressing "I know them" twenty times leaves you among artists just as famous as the
ones you started with. That is the defect you named. On the production data, **nothing this
experiment tried changed that** — not pooling artists' suggestion lists instead of requiring
both to rank each other, not raising the connection budget from 50 to 100, not using style
labels to choose which connections a crowded artist keeps, and not the new "each press digs a
little harder" rule. Every one of those left the typical mid-journey artist as famous after
twenty presses as before the first. Not "barely moved" — inside the range where our
measurement cannot tell movement from noise at all.

**And on the production data the gentle "dig harder" rule is not merely useless, it is
slightly costly.** Combined with pooled connections it delivers about a third fewer artists
per journey than the same map without it — the only cell in the whole experiment that fails
the payload criterion — while moving fame by three ten-thousandths. If anyone were tempted to
ship the ramp on today's data on the grounds that it cannot hurt, that is the figure that
says it can.

**On the candidate data, the same "dig harder" rule works.** With connections chosen by
pooling both artists' lists and trimming back to the same budget, twenty presses now leave
you with mid-journey artists about **six percentile points less famous** at the gentle
setting. At the stronger setting the drop is enormous — over sixty percentile points — which
is less "a nudge" than a different app.

**Three things about that which you should not let past you.**

**First, and this is the important one: the descent is partly invisible to our own ruler.**
As these journeys reach further into unknown artists, a growing share of the artists they
deliver are people our fame yardstick has no reading for at all — none at the start, but
about one in nine by press ten on the gentle setting, and one in six on the strong one. Those
artists drop out of the score. So the number that says "six percentile points less famous" is
computed on the artists we *could* measure, and the ones we could not are exactly the ones
most likely to be obscure. **The direction of that bias favours the result being smaller than
it looks, not larger** — but "smaller" is doing real work here, because on the subset of
journeys where nothing dropped out, the gentle setting's descent is **−0.0405, which does not
clear the bar it just passed.** Only eight journeys qualify for that stricter reading, which
is the bare minimum we agreed counts. On the strong setting only five qualify, and five is
below the minimum — so for that arm the stricter reading is not "worse", it is *absent*.

**Second, nothing was lost in exchange, as far as offline numbers can tell.** The journeys do
not get shorter — they get slightly longer, delivering more artists rather than fewer, which
was the failure mode we wrote a criterion against in advance. And they do not start leaning
on the map's celebrity hubs; if anything they lean on them less as you press.

**Third, the labels contributed nothing.** The idea that style labels should decide which
connections a crowded artist keeps was built, run, and measured against two different
scrambled-label controls. It moved the gradient by about a thousandth — so far below the
level worth investigating that we did not even open the attribution question. Your hunch
about popular artists being connected on thinner label evidence was also measured, and it
came out in the opposite direction, decisively. Both of those close doors rather than opening
them.

**What I cannot tell you, and it is the thing that matters most:** whether any of these
journeys sound good. Every number here says *how famous* the artists in the middle are. None
says whether they belong next to each other. The strong setting in particular produces a
change so large that the question "does this still feel like a journey rather than a random
walk into obscurity" is wide open, and no offline measurement in this project can answer it.

---

## §3 — Weakest link

**The load-bearing assumption is that the fame ruler's blind spots are randomly scattered
across the artists these arms deliver.** They are not, and we knew that before the run — §0.4
recorded it as a measured confound. What the run adds is that the blind spot **grows with
exactly the thing being measured**: the more successfully an arm digs, the more of its
delivered artists the ruler cannot score. The two passing arms are the two arms where this is
worst.

**What would falsify it:** re-scoring the two passing arms' depth-10–20 interiors against an
instrument with coverage in the candidate-only population. If the unmeasured artists turn out
to be *less* obscure than the measured ones, the descent is real and possibly understated. If
they are more obscure, the pass is partly an artifact of who fell out of the score. Nothing
in this project's record settles which, and `FAM-AM2.2` says the current ruler cannot order
within that clump at all.

**What I would defend:** the `ALG-E` null. Eight cells, four distinct interventions, every
median inside the instrument floor, with a confirmed pre-run prior (`CRE-D3`) saying the
pricing device was inert there before anything was built, and a liveness gate proving the
device is not a dead wire. That is as clean a null as this project has produced.

**What I would abandon cheaply:** the strong-setting arm `B-S1-P1b`. Its headline number is
the largest in the record, its matched-only companion is unreadable for want of pairs, its
censoring rise is the worst measured, and its depth-3–5 movement (−0.293) suggests the change
lands within a handful of presses rather than accumulating — which is not the `REQ-42` shape
(*obscurity should build steadily the more you press, not arrive all at once*) that the
primary outcome was chosen to detect. I would not defend a sentence that treats its magnitude
as six times better than the gentle arm's.

**One structural weakness worth naming:** the conservative `w_floor` guard fires on every
supply comparison, so this experiment **cannot** tell you how much of the candidate data's
advantage comes from the connection rule versus from the router's floor term behaving
differently at depth 0. It was designed to detect that rather than to resolve it, and it
detected it.

---

## §4 — Options and their consequences

**Why this decision is yours and not mine: it is adoption, it spends your ear, and it accepts
or refuses a residual risk on a data-set switch that retires every path-quality figure this
project has.** All four of those are in your column by the standing split. My column —
methodology, which cells to run, what to measure — is spent; the experiment is complete and
its bars were fixed in advance.

**Option A — spend a blind listen on `B-S1-P1a` (candidate data, pooled-and-trimmed
connections, gentle ramp).** The arm with a real pass and the smaller measurement hole.
Consequence: if it sounds good, you have a candidate for the cap decision *and* the data-set
decision together, and both still need the re-crawl. If it sounds bad, you have spent one
listen and closed the strongest thing the experiment found. Note the honest weakness going
in: on fully-measured journeys it scores −0.0405, below the bar it passed on the full set.

**Option B — spend the listen on both `B-S1-P1a` and `B-S1-P1b`.** Buys the answer to
"is the strong setting a better journey or a worse one" directly, which no number here can
give you. Costs more of the scarcest resource in this project.

**Option C — close the ruler's blind spot first, then re-read.** The single measurement that
would most change how much to trust the pass. Consequence: delays any listen, and the
fame-instrument track already failed to find a candidate that orders the obscure tail — so
this may be an expensive way to arrive back here.

**Option D — accept the `ALG-E` null and stop pursuing supply-side unlocking on the
production data.** Consistent with everything measured. Consequence: the defect `DD-F1` /
`REQ-13` — *pressing "I know them" on a journey between two famous artists never digs up
anyone obscure* — stands on the production data unless the data set changes. This is compatible with
A, B or C rather than an alternative to them.

**What no option here includes:** adopting anything. Nothing in this document changes a
default, a weight, or a shipped line of code.

---

## §5 — Bookkeeping this read is required to discharge

### 5.1 The affine `pop_raw` deferral

Three comparisons are not `pop_raw`-comparable — `E-S1` vs `E-S0` (scale 0.96772, shift
+0.03228), `B-S0` vs `E-S0` (0.99495, −0.00236), `B-S1` vs `B-S0` (0.96567, +0.03433). The
inherited condition was: no cross-cell `pop_raw` sentence for those three without applying
the map, **or no sentence**. **This document makes no cross-cell `pop_raw` sentence at all** —
every gradient figure here is in `fame_lb_pctl`. Discharged by the second branch.

### 5.2 Standing bars honoured

No worldly-fame sentence appears; "fame" throughout means the adopted novelty-likelihood
construct and its proxy. No within-remainder ordering is consumed. `CRE-S3` sentences carry
both §3.1 halves. Famous-pair first-path fame is reported, never scored (`PLA-R1`). The
barred `CRE-C6` × `CRE-D3` cross-read is not made. Track B's `R0` is cited only for what it
measured.

### 5.3 The unrun remainder, named rather than waved at

Family (a): bounds other than 50 and 100. Family (b): trim budgets and union widths other
than `TUw-50-50`. Family (c): tag devices other than the `evidence_rel`-ranked ceiling — one
member was run, and §3.2 says explicitly that this is not family (c) exhausted. Pricing:
one device at two ramp settings; router-side tag pricing is branch-excluded by `CRE-D1` and
was never eligible. Family (d): reference only, never a candidate. **No read in this document
claims family exhaustion.**
