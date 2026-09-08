# `DFA-` — a degree floor at admission, instead of raising the ceiling

**Role: FIGURES OWNER for the `DFA-` probe. ACTIVE.** Every figure below is owned here and is
**cited elsewhere, never restated** — with one deliberate exception, marked in place: the
ceiling-lift column of §3's tables is **cited from
[`2026-09-07-degree-ceiling-falsifier/README.md`](../2026-09-07-degree-ceiling-falsifier/README.md)
§4 and owned there, not here.** It is carried into these tables because a benefit-versus-cost
comparison is unreadable with the comparator in another document.

Raw records beside this file: [`dfa_results.json`](dfa_results.json) (the seven arms),
[`dfa_gate_addendum.json`](dfa_gate_addendum.json) (a dated correction to this probe's own
instrument gate), [`dfa_benefit_identity.json`](dfa_benefit_identity.json) (the set-identity
check), [`dfa_cap_diff.txt`](dfa_cap_diff.txt) (the variant cap against the shipped one),
and the two run logs.

**Scope: A DESCRIPTIVE STRUCTURAL PROBE, and one arm of an existing instrument.** Graphs built
in memory, two artifacts read and sha-verified, archives opened read-only, nothing serialised.
**No path was built, no routing criterion was evaluated, nothing is adopted and no rule change
is proposed.** The cap-rule decision is parked and the owner's
([`specs/2026-09-06-own-similarity-design.md`](../../docs/superpowers/specs/2026-09-06-own-similarity-design.md)
§9) and it owes a blind listen (`REQ-38`) before any adoption whatever these numbers say.

---

## 0. What this extends, and the arm it adds

**This is not a new instrument.** It extends the `DCF-` probe beside it, and the extension is
literal rather than rhetorical: the pinned archive, the artifact identity check, the
added/pre-existing split, `set_stats`, `hub_stats`, `top_decile_by_degree`,
`neighbour_sets` and `restored_edge_composition` are **imported from
`dcf_ceiling_sweep.py`**, not copied. Every read convention is therefore that probe's own
code, and this probe cannot drift from it by transcription.

**What `DCF-` established, cited and not restated.** Lifting `union_degree_ceiling` to a
non-binding value moves the `CXA`-added artists' dead-end share substantially, and it does so
by restoring a very large number of edges of which the overwhelming majority attach to a
top-decile-by-degree artist, driving `top1pct_degree_mass_frac` close to Track B's uncapped
reference row — the row Track B **barred from candidacy**. Figures: that README's §4 and §5.

**The shape of that result is what motivates this arm.** The benefit is carried by a few
thousand edges; the cost is carried by all of them. So:

> **The arm.** Instead of raising the ceiling, **exempt an edge from the degree trim when
> deleting it would leave the artist at the FAR end with at or below `F` connections.** The
> ceiling is held at the shipped 50 and every other knob at its default. `F` is swept over
> 1, 2 and 3.

This is the **"degree floor at admission"** candidate named in design §9.

## 1. Method — how the implementation relates to the shipped one, and what that costs

**`trimmed_union_cap` is not modified and no shipped builder path is touched.**
`floored_trimmed_union_cap` in [`dfa_degree_floor.py`](dfa_degree_floor.py) is a **copy of that
function's body with one added condition** inside the deletion loop. It is substituted into
the shipped pipeline by **rebinding `artistpath_builder.pipeline.trimmed_union_cap` for the
duration of one arm**, so every other stage of `build_from_archive` — payload parse, drop
lists, rescale, symmetrise, largest-component prune — is shipped code at shipped defaults.
Nothing on disk is edited.

**The relation is demonstrated, not asserted.** [`dfa_cap_diff.txt`](dfa_cap_diff.txt) is a
code-only diff of the two functions with comments and docstrings stripped. **The top-*j*
selection with its lowest-MBID tie-break, the union, the `symmetrise` call, the `strength`
helper and the highest-MBID-first deletion tie-break do not appear in that diff at all**,
because they are character-identical. What differs is the signature, two argument guards, the
node-order switch, the exemption condition, and telemetry.

**What the copy costs in fidelity, stated plainly.** A copy can drift: if the shipped rule
changes, this one silently does not, and every figure below would then describe a rule the
builder no longer runs. That is why **`F=0` is run as a full arm** — a floor of zero exempts
nothing, so it must reproduce the shipped control build exactly. It does (§2). That identity
is the drift detector, and it is the reason the copy is an acceptable cost rather than an
unbounded one. It is **not** free: it detects drift only when the probe is re-run.

**Two order conventions, chosen and justified — because the result depends on both.**

| choice | primary, and why | the alternative, run at `F=2` |
|---|---|---|
| **When the far end's degree is read** | **live**, at the moment of deletion. It is the only reading that *delivers* a floor: under it, no artist whose pre-trim degree exceeds `F` can be carried to or below `F` by the trim. Under a frozen pre-trim reading an artist at `F+5` is never protected, and five over-full neighbours can still strip it to zero | **fixed**, from a degree frozen before any deletion |
| **The order over-full nodes are processed** | **shipped** — `trimmed_union_cap`'s own `(-pre-trim degree, mbid)`. Holding every other knob at default includes holding the processing order at default | **ascending**, the degree key reversed |

**Both alternatives were run, so the sensitivity is measured rather than asserted (§7).**

**Inputs, pinned — `DCF-`'s own, unchanged.** Both artifacts were sha256-verified against
their manifest sidecars before being read and parsed by the **shipped `GraphStore`**; the
archive was opened through the `ReadOnlyArchive` whose `put()` raises (`GRT-A1`). The
added/pre-existing split reproduces `CXR-P2`'s counts exactly — **29,892 added, 58,793
pre-existing** — which is the read validating itself against figures it did not compute.

**Configuration.** Every arm: extended ALG-B archive (117,302 payloads), ALG-B algorithm,
`union_degree_ceiling=50`, `require_fame=False`, `drop_unlistenable=True` through the
**shipped per-invocation override** with the re-censused payload, every other knob default.
This is `DCF-`'s **bridge** configuration, and it is deliberate: it reproduces
`graph-cxa-adopted.bin`'s population exactly, which is what puts every figure here on
`CXR-P2`'s ruler and makes the ceiling-lift comparator legitimate. **`DCF-`'s
larger-population primary arms are not reproduced and no figure here is comparable to them.**

## 2. Instrument gates — and the run reported FAIL

**A green result from an instrument never shown to go red is not evidence.** Both halves were
run. **The red half as written FAILED, the failure was mine, and the original gate block in
[`dfa_results.json`](dfa_results.json) is left exactly as the run wrote it.** The correction
is a dated addendum beside it ([`dfa_gate_addendum.json`](dfa_gate_addendum.json)), never an
edit to a value.

| half | check | outcome |
|---|---|---|
| **green** | `F=0` reproduces the shipped control build exactly — same whole-graph, added, pre-existing and degree-histogram figures, and **zero** restored edges | **PASS** |
| **green** | the control's max degree ≤ 50, the shipped rule's stated bound (`CRS-G2`'s check) | **PASS** |
| **red, as written** | every floored arm exceeds degree 50, so the floor reached the trim | **FAIL** |
| **red, corrected** | every floored arm holds strictly more edges than the control **and** restores a non-zero count of edges to the added set | **PASS** |

**Why the written clause was wrong, and why this is not a failure being explained away.** The
clause encoded a **prediction about the rule** rather than a property of the instrument, and
the prediction was wrong: an over-full artist that meets an exempt edge does not stay
over-full, it deletes its **next-weakest non-exempt edge** instead. So the ceiling still binds
at `F=1` and `F=2`, and stops binding only at `F=3`, where two nodes run out of non-exempt
candidates. The red half's **purpose** is to show the knob is not silently inert, and the two
corrected clauses already demonstrated that on every arm — the max-degree clause was a third,
redundant, wrongly-generalised way of asking the same question. **The ceiling holding at 50 is
a measured result, reported as one in §3's cost table, and it is not a gate outcome.**

---

# MEASURED

## 3. The added set — what each floor buys

**n = 29,892, and every artist in it is present in every primary arm** (zero absent), so these
shares share one denominator. The **ceiling-lift row is cited from
[`2026-09-07-degree-ceiling-falsifier/README.md`](../2026-09-07-degree-ceiling-falsifier/README.md)
§4 and owned there** — it is carried here as the comparator and is not this probe's figure.

| arm | median | mean | share = 1 | **share ≤ 2** | count ≤ 2 | absent |
|---|---:|---:|---:|---:|---:|---:|
| **control — shipped ceiling 50** | 4 | 7.376 | 20.48 % | **34.36 %** | 10,272 | 0 |
| `F` = 1 | 4 | 7.453 | **10.86 %** | 34.49 % | 10,310 | 0 |
| `F` = 2 | 4 | 7.583 | 10.86 % | **19.96 %** | 5,967 | 0 |
| `F` = 3 | 4 | 7.743 | 10.86 % | **19.96 %** | 5,967 | 0 |
| *ceiling 20000, cited from `DCF-` §4 — owned there* | *8* | — | *10.86 %* | *19.96 %* | — | — |

**The pre-existing set, the within-build reference (n = 58,793).**

| arm | median | mean | share ≤ 2 |
|---|---:|---:|---:|
| control | 19 | 23.773 | 8.07 % |
| `F` = 1 | 19 | 23.753 | 8.14 % |
| `F` = 2 | 19 | 23.747 | **3.64 %** |
| `F` = 3 | 19 | 23.751 | 3.64 % |
| *ceiling 20000, cited from `DCF-` §4* | *51* | — | *3.64 %* |

**The cost side.** `top1pct_degree_mass_frac` is `CRS-C3`'s concentration measure, imported
unchanged — the share of all edge **endpoints** held by the top 1 % of nodes **by degree**.
Degree, never fame and never `pop_raw`. It is given **two ways** because §8 finds the two
disagree in sign: **own** scores each arm against its own top 1 %; **fixed** scores every arm
against one held-constant reference set, the control's own top 1 %.

| arm | nodes | edges | **edges vs control** | max degree | mean degree | top-1 % **own** | top-1 % **fixed** |
|---|---:|---:|---:|---:|---:|---:|---:|
| control | 88,685 | 809,082 | — | **50** | 18.246 | 0.02741 | 0.02741 |
| `F` = 1 | 89,678 | 810,439 | **+1,357** | **50** | 18.074 | 0.02767 | 0.02736 |
| `F` = 2 | 89,684 | 812,425 | **+3,343** | **50** | 18.118 | 0.02760 | 0.02729 |
| `F` = 3 | 89,684 | 815,073 | **+5,991** | **84** | 18.177 | 0.02754 | 0.02719 |
| *ceiling 20000, cited from `DCF-` §4* | *89,691* | *2,050,901* | — | *14,180* | — | *0.17617* | — |

*The earlier README reports no mean degree and no fixed-reference score for its bridge arms, so
those cells are blank rather than filled by a figure computed here under another probe's name.
Its edges-vs-control cell is left blank for the same reason: the subtraction is arithmetic on
two figures owned there.*

⚠ **The node count rising is NOT the measured sets gaining members.** Added plus pre-existing
is 88,685 — the artifact's own population — and both are fully present in every primary arm.
The extra ~1,000 nodes are artists **outside both measured sets** that the floor keeps inside
the largest component. No share in the tables above is affected.

## 4. Benefit retained against concentration cost paid — one sentence per `F`

- **`F` = 1 pays +1,357 edges and no concentration cost worth the name (own 0.02741 → 0.02767,
  fixed 0.02741 → 0.02736), and buys none of the dead-end benefit** — it halves the share of
  added artists left on a single connection, 20.48 % → 10.86 %, but moves them to two rather
  than past two, so the dead-end share does not fall and in fact rises to 34.49 %.
- **`F` = 2 pays +3,343 edges, keeps the ceiling binding at 50, and moves concentration by
  +0.7 % relative on own scoring and −0.4 % on fixed — and buys the ENTIRE dead-end benefit the
  ceiling lift buys**, 34.36 % → 19.96 %, on the same 4,305 artists (§5).
- **`F` = 3 pays +5,991 edges and stops the ceiling binding (max degree 84), and buys nothing
  further** — the same 4,305 artists, the same 19.96 %.

**The comparator, cited not restated:** the ceiling lift buys that same dead-end movement while
taking total edges to 2,050,901, max degree to 14,180 and own-scored concentration to 0.17617
(`DCF-` §4).

> ⚠ **Every concentration figure in the three sentences above must be read through §8, and none
> of them is evidence of a concentration cost.** On these arms that measure is algebraically
> `ceiling ÷ (100 × mean degree)` and cannot see edge arrangement at all; the differences are
> node counts. The statistic that *can* detect a moved top set is §8.4's, and it says the
> top-degree set is 98–99 % the same artists as the control's. **The defensible cost-side
> statement is "no available measure detects a concentration cost, and one of them provably
> cannot" — not "there is none."**

**`F` = 2 is not an empirical knee — it is definitional, and that is the weakest link.** A
floor at `F` guarantees no artist is *cut* to `F` or below. The dead-end criterion is degree
≤ 2. So `F` = 2 is exactly the value whose guarantee coincides with the criterion, and it
scores perfectly on that criterion **by construction**. The measured confirmation is the
redistribution column below: at `F` = 2 the number of added artists pushed INTO the two-or-fewer
group is **zero**, necessarily. Had the criterion been ≤ 3, `F` = 3 would be the matching value
and this table would read differently.

**Redistribution is a real cost, and it is why `F` = 1 goes backwards.** Exempting a fragile
artist does not stop an over-full artist deleting — it redirects the deletion onto the
next-weakest non-exempt neighbour, which can make *that* artist fragile.

| arm | rescued from ≤ 2 | **pushed into ≤ 2** | net |
|---|---:|---:|---:|
| `F` = 1 | 9 | **47** | **+38 worse** |
| `F` = 2 | 4,305 | **0** | −4,305 |
| `F` = 3 | 4,305 | **0** | −4,305 |
| `F` = 2, fixed pre-trim | 1,314 | 31 | −1,283 |

*Pushed-in counts are derived as (rescued + net change in the ≤ 2 count) on a constant
denominator. That derivation is not valid for the ascending-order arm, where 12 added artists
leave the graph entirely, so it is not given for it.*

## 5. Are they the same artists, or only the same number?

**The same artists. Jaccard 1.0, and the residual sets match too.**
[`dfa_benefit_identity.json`](dfa_benefit_identity.json) rebuilds the control, `F` = 2 and the
non-binding ceiling on one archive and compares MBID sets rather than counts, because
`restored_edge_composition` returns counts and equinumerous is not identical.

| | floor `F` = 2 | ceiling 20000 | both | floor only | ceiling only |
|---|---:|---:|---:|---:|---:|
| rescued from the two-or-fewer group | 4,305 | 4,305 | **4,305** | **0** | **0** |
| still at two or fewer | 5,967 | 5,967 | identical | — | — |

**So the two rules disagree about nobody** on this criterion. That is the strongest single
result here, and it is what licenses reading the floor as buying the ceiling lift's dead-end
benefit rather than a different benefit of similar size.

**But it buys strictly less of it, and this is the half a rescue count cannot show.** The same
4,305 artists, measured in each arm:

| the 4,305 rescued artists | median | mean | p90 | max |
|---|---:|---:|---:|---:|
| under the floor `F` = 2 | **3** | **3.000** | **3** | **3** |
| under the ceiling lift | 5 | 7.391 | 14 | 52 |

**Every rescued artist lands on exactly three connections under the floor** — it holds them at
the threshold and gives them nothing beyond it. Across the whole added set the same gap shows
as enrichment the floor does not deliver: mean degree 7.376 → 7.583 under the floor against
14.41 under the ceiling lift, and median 4 → 4 against 4 → 8.

## 6. Where the restored edges attach

Every edge an arm restores to an added artist, classified by what sits at the **other end**, by
**degree within that arm's own built graph** — never fame, never `pop_raw`.

| arm | restored edges | **share to a top-decile hub** | left ≤ 2 | via hub edges only | **via non-hub edges only** | via both |
|---|---:|---:|---:|---:|---:|---:|
| `F` = 1 | 3,031 | 61.2 % | 9 | 8 | 1 | 0 |
| `F` = 2 | 7,441 | **60.2 %** | 4,305 | 2,275 | **1,310** | 720 |
| `F` = 3 | 12,768 | 60.5 % | 4,305 | 1,673 | 965 | 1,667 |
| *ceiling 20000, cited from `DCF-` §4/§5* | *206,837* | *94.6 %* | *4,305* | *3,368* | *135* | *802* |

**The same artists are rescued, but not through the same kind of edge.** Under the floor, 1,310
of them clear the threshold on connections to non-hub artists alone; under the ceiling lift,
135 do. Restored edges run about 60 % to a top-decile-by-degree artist rather than 94.6 %.

⚠ **This is a statement about candidate structure and nothing else.** It does not say the
router would take those edges, and `CRS-C5`/`R2` record that it declines structure of this kind
at production weights.

## 7. Is the result sensitive to the two order choices? Yes to one, catastrophically to the other

Both alternatives were run at `F` = 2, against the same control. **Neither is a rule anyone has
proposed** — they exist to measure how load-bearing the conventions in §1 are.

| `F` = 2 arm | nodes | edges | max degree | added median | **added ≤ 2** | rescued | top-1 % own | top-1 % fixed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **primary — live, shipped order** | 89,684 | 812,425 | **50** | 4 | **19.96 %** | **4,305** | 0.02760 | 0.02729 |
| **fixed pre-trim** degree | 89,393 | 810,727 | 50 | 4 | **30.07 %** | **1,314** | 0.02757 | 0.02735 |
| **ascending** node order | 89,665 | **513,485** | **3,055** | **3** | 19.95 % | 4,305 | **0.05214** | 0.02759 |

**When the far end's degree is read decides most of the benefit.** Reading it from a frozen
pre-trim value rescues 1,314 artists instead of 4,305 — under a third — and leaves the dead-end
share at 30.07 % instead of 19.96 %. This is the mechanism §1 predicted before the run: a frozen
reading protects only artists who were *already* fragile when the trim began, while a live
reading also protects artists the trim itself is about to make fragile, and the second group is
much the larger. **The primary choice is vindicated, and it is vindicated as a design argument
rather than by preferring the better number** — live is the only reading that delivers the
guarantee the candidate is named for, and §4's zero pushed-into-the-group column is that
guarantee showing up as a measurement.

**The node processing order leaves the benefit alone and destroys everything else.** The
ascending arm rescues **the same 4,305 artists** and lands on the same dead-end share to within
0.01 pp. It gets there in a graph with **295,597 fewer edges than the control** — a 37 % cut —
a max degree of **3,055**, 58 nodes left above the ceiling, the pre-existing set's median degree
halved from 19 to 10, and own-scored concentration nearly doubled.

**Why, and the telemetry supports it.** Under the shipped descending order the largest artists
trim first, and their deletions drop many mid-degree artists below the ceiling so those never
trim at all. Under ascending order the barely-over-full trim first, their cuts leave the largest
artists untouched, and the largest then trim anyway — so far more edges are cut in total. By the
time those artists are processed, many of their neighbours have already fallen to three
connections and are exempt, so they cannot reach the ceiling: refusals rise from 13,466 to
**36,469** and nodes left above the ceiling from **0 to 58**.

> ⚠ **This is the candidate's sharpest weakness and it is a property of the rule, not of this
> harness.** The shipped `trimmed_union_cap` bounds degree at the ceiling **whatever order nodes
> are processed in** — the bound is a guarantee. The floored variant's bound is not: it holds
> under the shipped order and fails badly under another. A rule whose degree bound depends on an
> incidental convention is a different kind of object from one whose bound is structural, and
> **any adoption discussion owes that difference an answer.** Nothing here proposes one.

## 8. Commissioned derivation — is the cost side's measure comparable across these arms?

**This was commissioned from `ml-graph-analyst` after the arms were built and before any
comparison in §4 was written**, precisely so the cost side could not be framed first and
checked afterwards. It was asked for arithmetic, explicitly not for a recommendation about
which arm to prefer, which is outside its remit and is the owner's parked decision.

> **The question, verbatim as it was put:**
>
> "Does the concentration measure used as the cost side here — the share of edge endpoints held
> by the top 1% of nodes by degree — behave comparably across arms whose degree distributions
> differ in shape, given that the shipped-ceiling control is tie-dominated at its top-1%
> boundary while the raised and floored arms are not? Specifically: does scoring every arm
> against a FIXED reference set of top-degree nodes taken from one artifact, as Track B's
> companion column did, change the ranking of the arms compared with scoring each against its
> own set, and if so by how much and in which direction?"

**The question's premise was wrong and I supplied the correction with the dispatch.** It
assumes the floored arms are not tie-dominated. They are, to the same degree as the control:
the tie pool is 10.4 to 10.7 times the admitted cut in every shipped-ceiling arm. The
derivation was asked to work from the measured facts and to say whether the premise as put
would have led somewhere different.

### 8.1 The answer, and it is larger than the question asked

**On every shipped-ceiling arm here, this measure is not a concentration measure at all.**
Where at least 1 % of nodes sit at the ceiling `C` — true of six of the seven arms by a factor
of about ten — every node in the top 1 % by degree has degree exactly `C`, so the statistic
reduces algebraically to

```
top1pct_degree_mass_frac  =  round(N/100) · C / 2E  =  C / (100 · mean_degree)
```

The derivation checked this against the measured values on all six saturated arms and they
agree to about one part in a thousand. **Two graphs with the same node count, edge count and
ceiling score identically however differently their edges are arranged.** So a difference
between two saturated arms is a difference in node count and edge count wearing a
concentration measure's name.

**That reaches beyond this probe.** The derivation notes the same identity holds on `DCF-`'s
ceiling 50, 100 and 200 arms, so the rise across those three is the ceiling rising against mean
degree rather than evidence that lifting the ceiling concentrated the graph onto hubs. Its
uncapped arm is the only one of the four where that figure measures concentration — and
therefore the only one not on the same footing as the other three. **I have not edited that
probe's README and will not: its figures are its own to annotate, and this is reported here as
a pointer, not a correction made on its behalf.**

### 8.2 Does the fixed-reference scoring change the ranking? Yes, and both directions are forced

The sign flip in §3's two columns is real and **both signs are theorems rather than
observations**:

- **Own-set reads every floored arm as more concentrated.** The floored arms pull about a
  thousand extra artists into the largest component, so the 1 % cut rises from 887 to 897, a
  1.13 % numerator increase, while edges rise only 0.17 % to 0.74 %. The numerator must beat
  the denominator. Equivalently, mean degree falls because the newly admitted artists are
  low-degree, and the measure is inversely proportional to mean degree.
- **Fixed-reference reads every floored arm as less concentrated.** All 887 reference nodes had
  degree 50 in the control, and no node exceeds 50 in `F` = 1, `F` = 2 or the fixed-pre-trim
  arm, so the numerator is capped at 887 × 50 while the denominator grows. `F` = 3 breaches the
  ceiling by exactly two nodes and its bound still sits strictly below the control's.

The entire gap between the two columns on these arms is the cut-size ratio 897/887, predicted
at 1.01127 against 1.01133 and 1.01136 measured. **Neither column is reporting anything about
hubs.** In plain terms: the two scorings disagree about the floored arms because one counts how
many artists are in the graph and the other does not, and neither is looking at whether the
graph routes through a small set of well-connected artists.

### 8.3 Is a difference of that size meaningful? No, and not for the reason the question assumed

**The own-set figure is exactly invariant under tie-breaks** — every boundary node has the same
degree, so which of the tied nodes are admitted cannot change the sum. Its ambiguity width is
zero. **Tie-domination is therefore not what makes the own-set differences uninformative; the
saturation identity is.** For scale, the cut-size quantisation step is 3.09 × 10⁻⁵ and the
measured own-set differences are four to eight such steps, all of it node count.

**The fixed-reference figure does carry a genuine ambiguity**, because it inherits the
control's arbitrary choice of 887 nodes from among equals.
Because that choice is arbitrary among equals, the derivation bounded the resulting ambiguity
distributionally and flagged the assumption behind it as **the one place it extrapolated**.
That bound is now unnecessary: [`dfa_overlap_and_ambiguity.py`](dfa_overlap_and_ambiguity.py)
records every tie-pool node's degree in every arm, so the extremes over admissible reference
sets are **exact** — the 887 smallest and the 887 largest.

| arm | fixed-reference, measured | exact range over admissible reference sets | **exact width** | difference from control | **inside its own ambiguity?** |
|---|---:|---:|---:|---:|:--|
| control | 0.027408 | [0.027408, 0.027408] | **0.000000** | — | — |
| `F` = 1 | 0.027356 | [0.027311, 0.027362] | 0.000051 | 0.000052 | **essentially at it** |
| `F` = 2 | 0.027286 | [0.027178, 0.027295] | 0.000117 | 0.000122 | just outside |
| `F` = 3 | 0.027191 | [0.026982, 0.027227] | 0.000245 | 0.000217 | **yes — inside** |
| `F` = 2 fixed pre-trim | 0.027348 | [0.027313, 0.027352] | 0.000039 | 0.000060 | just outside |
| `F` = 2 ascending | 0.027588 | **[0.010689, 0.045994]** | **0.035305** | 0.000180 | **yes — by a factor of 196** |

The control's width is zero, as it must be: every tie-pool node has the same degree there, so
which 887 are chosen cannot matter. **The exact widths come out slightly narrower than the
derivation's distributional bound and change none of its conclusions.** Two of the five
differences sit inside or at their own ambiguity, and the ascending arm's fixed-reference
reading is meaningless — the number moves by 0.00018 inside a window 196 times that wide.

### 8.4 The statistic that does work, and what it says

Track B's companion column is **not** a mass against a fixed set. It is
`top_degree_node_set_overlap_with_production`, a **set overlap fraction**
(`cb_metrics.py:171-174`, verified in source). My `fixed_reference_mass` is therefore a **new
quantity and not a reproduction of Track B's**; its docstring said otherwise and is corrected.
The distinction is not pedantic — the derivation predicted the overlap column would catch what
the mass column misses, because it responds when the top set **moves** rather than when it
grows. Computed here against this probe's control rather than a production cell, so it is
**that statistic's shape on this baseline and is not comparable to `cb_scores.json`**:

| arm | **top-1 % set overlap with the control** | top-decile overlap | own-set mass | saturation identity `50/(100·mean)` | ties ÷ cut |
|---|---:|---:|---:|---:|---:|
| control | 1.00000 | 1.00000 | 0.02741 | 0.02740 | 10.74 |
| `F` = 1 | **0.99098** | 0.99188 | 0.02767 | 0.02766 | 10.57 |
| `F` = 2 | **0.98873** | 0.98275 | 0.02760 | 0.02760 | 10.50 |
| `F` = 3 | **0.98083** | 0.96910 | 0.02754 | 0.02751 | 10.40 |
| `F` = 2 fixed pre-trim | 0.99436 | 0.99335 | 0.02757 | 0.02757 | 10.65 |
| `F` = 2 ascending | **0.05524** | 0.53033 | 0.05214 | 0.04366 | **0.24** |

**Read across the last two columns first: the saturation identity holds to the fifth decimal on
every arm whose tie ratio exceeds 1, and breaks on the one arm where it does not.** That is the
derivation's central claim, checked here rather than taken on trust.

**Then the answer the cost side actually needed.** Under the floored arms at the shipped
ceiling, **98 to 99 % of the top-degree set is the same artists as the control's**. The floor
does not relocate the well-connected artists; it adds a small number of edges around the
existing structure. Under the alternative node order, **94.5 % of the top-degree set is
different** — the overlap collapses to 0.055 while the fixed-reference mass reported that same
arm as 0.7 % above the control. **The mass column called that arm unchanged; the overlap column
calls it a different graph, and the overlap column is right** — its max degree is 3,055.

> **So the cost side of §3 and §4 should be read through this section, not on its own.** For
> the shipped-ceiling arms the honest statement is: **no measure available here detects a
> concentration cost, and one of them is provably incapable of detecting one** — while the
> statistic that can detect a moved top set says it did not move. That is weaker than "the
> floor costs nothing in concentration" and it is what the evidence supports.

---

# WHAT IS NOT ESTABLISHED HERE

- **No routing, anywhere.** No path was built, no `CRS-C4` hub transit was computed, and no
  criterion of any pre-registration was evaluated. **A candidate-supply gain is not a
  delivered-connection gain, and neither is a journey the router would choose.** §6 says what
  each floor *offers*; it says nothing about what the router would take, and the router is
  known to decline structure of exactly this kind at production weights (`CRS-C5`/`R2`, cited).
- **Track B's `C4` result stands against any looser bound until re-measured.** Nothing here
  touches it, weakens it or is evidence about it. That matters more for `F` = 3 and for the
  ascending-order arm than for `F` = 1 or `F` = 2, since those two leave the degree bound
  intact — but "leaves the bound intact" is a statement about max degree, **not** a statement
  about hub transit, which was not measured.
- **"Hub" means TOP DECILE BY DEGREE within the arm's own built graph**, never famous and never
  popular. §6 licenses no fame claim. The boundary is tie-dominated in every shipped-ceiling
  arm (boundary degree 50, ~9,400 nodes tied, ~890 admitted), so *which* artists are in that
  set is arbitrary among equals. **The own-set mass is nevertheless exactly invariant to that
  choice** (§8.3) — the arbitrariness reaches the fixed-reference column and §6's membership,
  not the mass.
- **NO CONCENTRATION COST IS ESTABLISHED, AND NONE IS RULED OUT** (§8). On every
  shipped-ceiling arm `top1pct_degree_mass_frac` reduces to `ceiling ÷ (100 × mean degree)`
  and is structurally incapable of seeing how edges are arranged; the fixed-reference column is
  blind to concentration forming outside its reference set, and two of its five differences sit
  inside their own exact ambiguity. What *is* established is narrower: the **identity** of the
  top-degree set is 98–99 % unchanged under the floored arms. An artist can gain endpoints
  without the set moving, and nothing here would detect that.
- **`F` = 2's perfect score on the dead-end criterion is partly definitional** (§4). It is the
  floor value whose guarantee coincides with the criterion's threshold. Read as "the floor
  achieves the criterion", it is close to a tautology; the non-trivial findings are the
  *identity* of the rescued set (§5), the *cost* of achieving it (§3), and the fact that
  `F` = 3 buys nothing further.
- **Nothing here says three connections is enough.** §5 measures that every rescued artist
  lands on exactly three. Whether an interior card with three connections is a *good* card is a
  question about journeys and about the owner's taste, and neither is measured anywhere in this
  probe.
- **The two order conventions are not neutral** (§7), and the ascending-order arm shows the
  floored rule's degree bound is not a guarantee. **No claim here holds under a different node
  processing order** except the added set's dead-end share and the identity of the rescued set,
  which are the two quantities measured to be robust to it.
- **Only the `CXA`-lineage bridge population was built.** `DCF-`'s larger-population primary
  arms were not reproduced, so no figure here is comparable to them — only to that probe's
  §4 bridge arms.
- **The drop lists under-filter in the same way `DCF-` records**, and for the same reason:
  `drop_no_release_tail` and `drop_featured_credit` are keyed by algorithm rather than
  population. Held identical across every arm, so the comparison is unaffected; the absolute
  levels carry the caveat.
- **The variant cap is a copy and copies drift** (§1). The `F` = 0 identity arm detects drift,
  but only when the probe is re-run. Nothing detects it in between.
- **No blind listen, and no evidence about how anything sounds.** Every figure here is a
  property of files.
- **The Snyk scan did not run on these scripts.** Credentials are expired, and the owner's
  ruling of 2026-09-07 accepts that deferral for `builder/analysis/` code on the grounds that
  none of it is live, with the revisit condition being promotion into shipped code — which
  nothing here proposes. Reviewed by hand instead and reported as such, not as clean: read-only
  analysis scripts, no network calls, no `eval`, no subprocess use, and no externally-sourced
  value reaching a query or a path.

# WHAT THIS DECIDES

**Nothing.** It is measurement, and one arm of it.

Whether the cap rule should change at all is the **owner's parked decision** (design §9). It
owes a **blind listen** (`REQ-38`) before any adoption whatever these numbers say. Track B's
`C4` flag travels with any candidate that loosens the bound, and `F` = 3 and the ascending-order
arm loosen it.

**The probe was asked for one arm and ran one arm.** It proposes no floor value, recommends no
adoption, and changes no default.
