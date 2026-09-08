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
