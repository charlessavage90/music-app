# Tag discrimination — the signal is real, and neither architecture has an adoption case

**Role: ACTIVE findings record. Owns its figures** (tag-discrimination figures only; scoring
and path-quality figures stay in `2026-07-21-scoring-adjudication.md`, the `REL-` probe's stay
in `2026-07-31-release-tag-coverage.md`, and the `WGT-` probe's in
`2026-08-01-label-weighting-probe.md`). Identifier series: `TAS-`. Probes and raw record:
`builder/analysis/2026-07-30-tag-discrimination/`. Governing document, committed before any
measurement ran:
[`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](../specs/2026-07-30-tag-discrimination-probe-preregistration.md).
Reasoning: [`2026-07-30-tag-discrimination-execution-log.md`](../2026-07-30-tag-discrimination-execution-log.md),
§9–§16.

**Scope: descriptive.** Nothing here adopts anything, fixes a criterion, or changes a weight,
default, currency, vocabulary or substrate. `w_coh` does not exist in `ApiConfig` and this
record does not propose it. No rebuild, no API change, no blind listen spent. It settles no
open owner decision in `NEXT.md`.

**⚠ Read §8 of the pre-registration before quoting any criterion.** Five amendments govern:
`TAS-AM1` withdrew `TAS-4`'s original bar **as false** and replaced both its quantity and its
statistic; `TAS-AM2` fixes the substrate per criterion and **forbids comparing a capture-side
figure with an artifact-side one**; `TAS-AM3` withdrew §4's red check **as unachievable** and
replaced it; `TAS-AM4` evaluated a candidate vocabulary; `TAS-AM5` built the routing-side
instrument check. Their disclosure positions differ and the differences are load-bearing —
see [Amendments](#amendments-and-their-disclosure).

**Two substrates, never compared.** Selection-side criteria (`TAS-2`, `TAS-3`, `TAS-4`,
`TAS-6` selection half) run on the pre-cap `ALG-E` capture; map-side criteria (`TAS-1`,
`TAS-5`, `TAS-6` routing half) run on the adopted artifact. They differ by 36 artists and 193
edges (0.05% / 0.04%) — small, but nobody controlled it. Every table below names its side.

---

## §0 The headline

*(Plain: genre labels really do tell an artist's similar artists apart — they are not just the
similarity score wearing a different hat, and switching them on would change a great deal.
But building with them makes the app worse at the one thing you called a defect, and the
journey changes we measured on the router turn out not to be about genre at all: scrambling
which artist owns which labels reproduces 98% of the same change.)*

**Both kill bars were cleared, and neither architecture has an adoption case.** Those are not
in tension; they are decided by different clauses, both pre-registered.

| | build-time selection | router-side pricing |
|---|---|---|
| Kill bar | `TAS-4` — **does not kill**, by 16×–40× | `TAS-5` — **does not kill**; journeys change in every class at every weight |
| Guard | `TAS-6` selection half — **ADVERSE** at λ ≥ 1.0 | `TAS-6` routing half — **VACUOUS**, baseline zero |
| Null control | `TAS-AM3b` — null is 23–25% of real, **below** the 50% line | ⚠ `TAS-AM5c` — null is **98–99%** of real, **FIRES** |
| Outcome | **Barred.** §5: an adverse `TAS-6` bars an adoption recommendation whatever else holds | **Survives its bar on a change that is not attributable to genre structure** |

**The assumption the whole thread rested on is confirmed.** Genre agreement does discriminate
between the candidates an artist already has (`TAS-2`, median within-list spread 0.1726 against
a 0.02 kill), and it is **not** redundant with the similarity score (`TAS-3`, rank correlation
0.1857; the two orderings coincide on 3.07% of candidate lists). The idea was not killed by its
own premise. It was stopped by a guard on one side and by a null control on the other.

---

## `TAS-1` — where do we have labels at both ends? *(gate, narrow — PASS)*

> *Plain, quoted from §2: "on how many of the connections in today's map do both artists carry
> genre labels? Where either is bare, the rule is silent and changes nothing there."*

**Adopted artifact.** 40,437 of the artifact's nodes carry ≥ 1 normalised genre label.

| edge class | edges | both ends labelled |
|---|---|---|
| famous–famous | 5,478 | **99.96%** ← the gate |
| spanning | 398,510 | 55.03% |
| obscure–obscure | 45,015 | 17.12% |
| **all edges** | **448,828** | **51.77%** |

**Gate: ≥ 80% of famous–famous edges. PASS at 99.96%.** The rule acts essentially everywhere
it was designed to act.

**This gate deliberately does not inherit `COH-2`'s coverage bar, and the distinction is the
reason the thread was reopened at all.** That bar governed a *sensor*, where blindness in the
tail returns confident wrong readings about artists it cannot see. This is an *actuator*: where
labels are missing it does nothing, rather than doing something wrong. **Silence is safe in a
way blindness is not.**

**The tail thinness is real and it is not harmless — it is `TAS-6`'s problem, not this gate's.**
17.12% coverage among obscure–obscure connections is the same hole `COH-2` measured, and the
hazard it creates (silence in the tail plus action at the top, tilting the app toward the
famous) is exactly what `TAS-6` was written to catch. It caught it.

## `TAS-2` — does genre overlap vary between an artist's candidates? *(gate — does not kill)*

> *Plain, quoted from §2: "R.E.M. has a hundred similar artists. Do some share far more genre
> labels with R.E.M. than others, or do they all look about the same?"*

**Pre-cap capture**, over 2,622,389 scored candidate pairs.

| | |
|---|---|
| candidate lists considered | 38,782 |
| lists excluded (fewer than two labelled candidates) | 1,654 |
| **median within-list interquartile range** | **0.1726** |
| mean within-list interquartile range | 0.2122 |
| kill bar | < 0.02 |
| weak-signal flag | < 0.10 |

**Does not kill, and is not flagged weak** — 8.6× the kill bar and comfortably past the flag.
Some of an artist's candidates share far more genre labels with it than others.

**This is the gate whose failure would have killed both architectures together**, and it is the
cheapest thing that could have done so. It did not.

## `TAS-3` — is it telling us anything similarity has not? *(diagnostic — carries no bar)*

> *Plain, quoted from §2: "if genre overlap just repeats what the similarity score already
> says, then nudging by it changes nothing — the graph already knows."*

**Pre-cap capture.** Spearman rank correlation between agreement and similarity strength:
**0.1857**. Share of candidate lists on which the agreement ordering and the strength ordering
are identical: **3.07%**.

**Weak correlation and near-zero coincidence, so the signal is genuinely independent of
similarity.** This matters most for interpreting the nulls that follow: §2 names three very
different things a null could mean — no variation, variation redundant with similarity, or a
real independent signal that the cap and the router absorb — and this figure rules out the
first two. **Whatever stopped each architecture, it was not that genre agreement is the
similarity score in disguise.**

`TAS-3` carries no threshold by design, and none is invented here.

## `TAS-4` — would it change which neighbours survive selection? *(gate — does not kill)*

> ⚠ **Governed by `TAS-AM1`**, which replaced this criterion's measured quantity (edge turnover,
> not per-artist swaps), its statistic (mean, not median) and its bar (≤ 1%, not "median ≤ 2
> swaps of 50"). The original bar was **withdrawn as false** before any `TAS-` figure existed.
>
> *Plain, quoted from `TAS-AM1`: "if fewer than one connection in a hundred is different across
> the whole map, no journey will change in a way you could notice. At the original bar, about
> one journey in three would have contained a connection that no longer exists."*

**Pre-cap capture**, reconstructing `ALG-E-mutual_knn-k50` edge for edge. Baseline 448,828
edges. The cap binds for 37,006 artists (49.37%), and 80.3% of edges are incident on at least
one of them. The rule acts on 65.8% of candidate slots.

| λ | deleted | created | edges after | **turnover** | mean swaps (binding artists) |
|---|---|---|---|---|---|
| 0.25 | 24,238 | 49,498 | 474,088 | **16.43%** | 3.10 |
| 0.5 | 37,981 | 76,302 | 487,149 | **25.46%** | 4.98 |
| 1.0 | 52,409 | 100,212 | 496,631 | **34.00%** | 7.03 |
| 2.0 | 64,277 | 116,957 | 501,508 | **40.38%** | 8.79 |

**Kill bar: turnover ≤ 1% at every λ. Does not kill — the gentlest arm exceeds it by 16×.**
The intervention is emphatically not inert.

**The owner set the 1% bar on 2026-07-30**, after being shown `TD-2`'s conversion in journey
terms. It is a materiality line, which is his, not a derivation.

**Creations exceed deletions at every λ, and by a wider margin than even the synthetic
*symmetric* control.** Jaccard is symmetric, so two artists sharing genres promote each other,
and genre agreement is clustered in a way a random symmetric field is not. **Mean degree rises:
the map gets denser, ending 11.7% larger at λ = 2.0.** Nothing in the pre-registration
anticipated this. It is not a `TAS-4` finding — `TAS-4` asks whether selection would change, and
the answer does not depend on it — but it is a standing obligation on any rebuild
pre-registration, and it is in `NEXT.md`'s deferral table for that reason. `w_degree_hub` is
dormant **because of the current graph's top-degree set**, and a rebuild is exactly the
intervention that could wake it.

**Bounded, and the bound is the pre-registration's own.** This measures the **input** to a
rebuild, not its output. Mutual selection means one artist's reordering can delete an edge the
other still ranks, so the built consequence of a given turnover is not derivable from `TAS-4`
alone. Nothing offline here says whether a replaced connection *reads* differently — that
remains the blind listen's.

*(The retired median is emitted under an explicit `_RETIRED_STATISTIC` name in `tas_select.json`
so `TD-3`'s zero-inflation stays visible in this record rather than taken on trust from another.)*

## `TAS-5` — would it change the journeys the app builds? *(gate, per class — does not kill)*

> *Plain, quoted from §2: "if the journeys come back the same, the term is decoration."*
>
> ⚠ **Every figure in this section carries `TAS-AM5c`'s caveat: this change is NOT attributable
> to genre structure.** See the null control below. The caveat is not softened by the change
> rate being large — the largeness is what makes the control decisive rather than a formality.

**Adopted artifact**, production `ApiConfig` weights (`w_sim` = 3.0), 120 pairs from the §3
draw at seed `20260730-tas`: 40 famous–famous, 40 spanning, 40 obscure–obscure, none unreadable.
"Changed" means a different artist sequence, endpoints included; path *cost* is excluded from the
comparison by design, since the added term necessarily moves it.

| `w_coh` (× `w_sim`) | famous–famous | spanning | obscure–obscure |
|---|---|---|---|
| 0 | 0% | 0% | 0% |
| 0.25 | 90.0% | 95.0% | 95.0% |
| 0.5 | 92.5% | 95.0% | 97.5% |
| 1.0 | 92.5% | 97.5% | **100%** |
| 2.0 | 92.5% | 97.5% | **100%** |

**Kill bar: only if journeys are unchanged in EVERY class at EVERY weight. Does not kill.**
A pooled bar was explicitly rejected in advance.

**Two deflations were committed before the null control existed, and both anticipated its
shape.** Recorded here because a caveat written after a result is worth much less:

1. **The gentlest weight is not gentle.** At 0.25 × `w_sim` the added term is comparable in size
   to the similarity term beside it. No cell in this grid is a light touch.
2. **One substitution makes a whole journey "changed".** Journeys run about six hops between
   famous artists and twelve between obscure ones, so near-total path-level change is close to
   arithmetically forced. **The class ordering above matches what path length alone predicts,
   which is the tell** — obscure–obscure, the longest journeys, saturate first.

**Then the null control fired and settled it.** Permuting label sets among labelled artists —
holding fixed exactly which artists carry labels — reproduces **98.2%–99.1%** of the real
change rate at every weight. **`TAS-5`'s change cannot be attributed to genre structure.** What
was measured is what happens when *any* label-shaped cost is added to every edge of a long
journey.

**The standing caution applies and points the same way.** Three consecutive attempts to change
router behaviour by changing prices had already returned nulls — Track 2's repricing family,
Track 3b's thresholded toll, and Track B's `R2`. **This is the fourth, and the first that looked
like a success until the control ran.** Per §2's own instruction, this must not be reported as
"tags do not work": it is consistent with "this router shrugs off new terms", and `TAS-3` is
what distinguishes those — the signal is independent of similarity, so redundancy is not the
explanation.

## `TAS-6` — does any of this cost obscurity? *(guard — reported, never a success signal)*

> *Plain, quoted from §2: "does this make the app worse at reaching unknown artists — the thing
> you called a defect rather than a limitation?"*

Two measurements, one per architecture, **never combined** and each on its own substrate.
Adverse at a ≥ 10% reduction.

### Selection half — **ADVERSE**

**Pre-cap capture.** Famous→obscure connections surviving simulated selection, counted against
the **fixed** adopted fame frame: one end in the top 1%, the other in the lower half.

| λ | famous→obscure edges | change | adverse? |
|---|---|---|---|
| baseline | 93 | — | — |
| 0.25 | 87 | −6.45% | no |
| 0.5 | 85 | −8.60% | no |
| 1.0 | 83 | **−10.75%** | **yes** |
| 2.0 | 79 | **−15.05%** | **yes** |

**Adverse at the top two λ. Per §5 this bars any recommendation to adopt the build-time
architecture, whatever `TAS-4` and `TAS-5` show, and it is not outweighed by `TAS-4` having
survived.** No bar was revisited after a result existed.

**The mechanism is the neutral rule's**, which is why every finding here is reported as "λ **and**
the neutral rule". Unlabelled candidates take a per-artist median; labelled genre-matching
candidates are boosted *above* that median; unlabelled candidates are disproportionately
obscure. The neutral rule stops them being sent to the bottom, which was its job, but it cannot
stop them being squeezed out at the margin.

**⚠ The denominator is 93 edges out of 448,828, and that is information rather than a defence.**
The reader must see it before judging materiality. It cuts both ways: it is also a statement
about how few direct famous→obscure connections this graph has **at all**, which is `DD-F1`
measured from a new angle. The broader count of edges *touching* a sub-decile artist is far
larger and falls far less — 10,017 → 9,658 at λ = 2.0, a 3.6% fall — but that is not the
quantity `TAS-6` fixed, and it is reported here rather than substituted for it.

### Routing half — **⚠ VACUOUS. Must never be quoted as a pass.**

**Adopted artifact.** Sub-decile artists appearing in journey interiors, endpoints excluded.

| `w_coh` | sub-decile interiors | adverse? |
|---|---|---|
| **baseline** | **0** | — |
| 0.25 | 0 | false *(by construction)* |
| 0.5 | 0 | false *(by construction)* |
| 1.0 | 2 | false *(by construction)* |
| 2.0 | 2 | false *(by construction)* |

**The baseline is zero: across all 120 drawn pairs, production routing delivers no
bottom-decile artist mid-journey at all.** A 10% reduction from zero cannot be measured.
`is_adverse` returns `False` outright when the baseline is zero (`tas_guard.py:111`), so every
`false` in that column is a hard-coded early return, **not a safety finding**.

**This is not a defect of the run — it is a property of what production routing delivers, and
the sharpest corroboration of `DD-F1` in the record.** The guard written for this experiment
could not act because the thing it was guarding was already at zero.

**The two sub-decile interiors at the top two weights are an unscored observation, and they are
reported rather than promoted.** No criterion scores them; n = 2 across 120 journeys; and the
`TAS-AM5c` null grid returns zero at every weight, so this is the one place the real frame
differs from a permuted one. **It licenses nothing** — reading two artists as evidence about
genre would need its own pre-registration designed cold, and the null control that fired
governs every other figure in this section.

---

## Instrument checks — both sides, all passed

**No outcome above was read until these were in hand**, per §5. The two sides needed different
checks, and `TAS-AM5` exists because `TAS-AM3`'s could not transfer: `TAS-AM3a` passes on
bit-identity against a **pre-cap capture** reference, while `TAS-AM2` puts `TAS-5` on the
**adopted artifact** and forbids reading one against the other.

### Selection side

- **`TAS-AM3a` — equivalence and liveness. PASSES at every λ.** *Plain: "prove the measuring
  device can register a big change, by giving it a big change we already know the answer to."*
  The selection masks are **bit-identical** to `td_turnover.mask_multiplicative`, and turnover
  reproduces the committed `TD-2` `MULT-SYM` figures **to five decimals** (0.35565 / 0.52423 /
  0.64455 / 0.71029). This is stronger than the withdrawn check's intent: it proves the new code
  path **is** the already-verified one rather than resembling it, against a fixed external
  reference rather than a threshold a session picked.
- **`TAS-AM3b` — the null control. Below the line.** *Plain: "check that the change we measured
  comes from genres sitting where they actually sit, rather than from any label-shaped nudge at
  all."* Null turnover is **23.5% / 24.3% / 24.8% / 24.1%** of real, strikingly flat across the
  grid and below the 0.50 line fixed before it ran. **Attribution is not unsafe. Per its own
  pre-registered read, the ratio is reported and nothing more — no claim about tags is licensed
  by this control.**
- **⚠ The withdrawn naive shuffle had implied a ratio less than half that size**, and the
  correction runs **against** the idea. Holding fixed *which* artists are labelled — the one knob
  the naive version also moved — roughly doubles the null. The naive shuffle halved the number of
  pairs where the device acts, which suppressed the null and **overstated how much of `TAS-4`'s
  turnover came from genre structure.** Its figures stay in `tas_guard.json` under
  `withdrawn_naive_shuffle` with the reason, because `TAS-AM3` cites them as the evidence that
  the direction was known before the amendment was written.

### Routing side

- **`TAS-AM5a` — equivalence. PASSES, 0 mismatches on all 120 pairs.** *Plain: "prove the copy
  of the router used for this experiment is the real router, by checking it returns the app's own
  answer on every journey we test."* At `w_coh` = 0 the fork returns production's own paths
  exactly. This is what **licenses** the fork omitting `excludes`, `avoidance_map`,
  `effective_floor_raw` and `forbidden_edge` — proved equivalent, not argued to be.
- **`TAS-AM5b` — liveness. PASSES, 0 failures.** *Plain: "prove the genre term can move a
  journey, by turning it up until it is the only thing that matters and checking the journey goes
  exactly where it then should."* At a dominating weight (10⁶ × `w_sim`), the total
  `(1 − agreement)` along the returned path equals an **independently computed** Dijkstra optimum
  to within 1e-9 on every pair. Totals rather than node sequences, so ties are not read as
  defects.
- **⚠ `TAS-AM5c` — the null control. FIRES.** Null/real change ratio **0.9822 / 0.9824 / 0.9913 /
  0.9913**, far above the pre-registered 0.50 clause. **`TAS-5`'s change is not attributable to
  genre structure and every `TAS-5` figure carries that caveat.**

**So the `TAS-5` null is a real null, not a broken harness.** That distinction is the entire
reason `TAS-AM5` was written, and it was written **before any routing figure existed**.

---

## The candidate vocabulary — `TAS-AM4`, and the decomposition that corrected it

**§1's vocabulary is UNCHANGED and every committed `TAS-` figure above stands on it.** This
section measures candidate frames *beside* the committed one. Adopting one would be a further
§8 amendment and, per `NEXT.md`, the owner's trigger.

**Pre-cap capture**, all figures on `W0`'s fixed scorable population of 38,782 lists — the
one-knob control, valid because labels only ever accumulate. Spread is the `TAS-2` median IQR;
redundancy is the `TAS-3` rank correlation; reach is the share of candidate slots where the rule
acts.

| frame | contents | spread | vs `W0` | redundancy | reach |
|---|---|---|---|---|---|
| **`W0`** | committed §1 frame | **0.1726** | — | 0.1857 | 65.8% |
| `W1` | + MusicBrainz release groups | 0.1600 | −7.3% | 0.2049 | 84.0% |
| `W4` | `W1` + Discogs **genre** | 0.1565 | −9.3% | **0.1942** | **89.7%** |
| `W5` | `W1` + Discogs **style** | 0.1403 | −18.7% | 0.2340 | 89.2% |
| `W6` | `W1` + both *(the frame `TAS-AM4` measured)* | 0.1418 | −17.8% | 0.2179 | 89.7% |

**`TAS-AM4`'s four pre-registered reads, in the order it fixed them:**

1. **No candidate is killed.** Both enriched frames clear `TAS-2`'s kill bar and its weak-signal
   flag with room, **using `TAS-2`'s existing bars unchanged** — the main thing keeping an
   after-the-fact amendment honest.
2. **The spread fall is the headline, per the read that pre-committed it to being one.** The
   flattening `TAS-AM4` predicted is present, and it more than doubles when Discogs is added on
   top of MusicBrainz.
3. **`TAS-3` rises under both candidates** — the same degradation showing up in a second place.
   The already-ordered share falls, but that must **not** be read as reordering headroom: a
   longer candidate list is less likely to be coincidentally in agreement order, so it is at
   least partly a list-length artifact. The rank correlation is the cleaner reading and it moves
   the other way.
4. **Reach rises substantially** — 65.8% → 84.0% for `W1` (**+18.2 points**) and → 89.7% for
   `W6` (**+23.9 points**). This is the quantity that would drive any `TAS-6` improvement.

   ⚠ **Currency note, because this record holds two reach deltas in different units.** The
   figures above are **percentage points**. `tas_frame_eval.json`'s `acting_slot_change_vs_W0`
   (0.2772, 0.3631) is a **relative** change against `W0` and must not be read as points; the
   isolation table below uses `tas_frame_split.json`'s `reach_change_pts`, which genuinely is
   points. Named rather than silently reconciled — reading one of these as the other is the
   error class `CLAUDE.md` opens with.

**The comparison was confounded and the control did not rescue it.** Enrichment makes far more
artists scorable, so the first pass moved the frame and the population together — and the newly
scorable artists are precisely the obscure ones `REL-` reached. Re-measuring every frame on
`W0`'s scorable set changed almost nothing: **the degradation is real, on the same artists.**
Recorded because a control that is only reported when it helps is not a control, and this one
was run expecting it might overturn the result.

### The decomposition inverts the attribution *(diagnostic only, licenses nothing)*

`TAS-AM4`'s `W6` merged Discogs' closed 15-value **genre** list and its ~600-value **style**
list in one arm — two knobs, and the fall was attributed to neither. `W4` and `W5` isolate each
against a baseline differing by exactly that column, giving **two independent isolations of each
source**, and all four agree.

| isolating | spread | reach | redundancy |
|---|---|---|---|
| **Discogs genre**: `W1`→`W4` | −2.2% | +5.65 pts | −0.0107 |
| **Discogs genre**: `W5`→`W6` | **+1.1%** | +0.52 pts | −0.0161 |
| **Discogs style**: `W1`→`W5` | −12.3% | +5.13 pts | +0.0291 |
| **Discogs style**: `W4`→`W6` | −9.4% | **+0.00 pts** | +0.0237 |

**The closed 15-value genre list is not the problem; the ~600-value style list is.** Adding the
coarse list barely moves the spread — in one isolation it slightly *improves* it — and **lowers**
redundancy in both, meaning it carries information similarity did not already have. Adding styles
costs roughly a tenth of the spread and **raises** redundancy in both isolations.

**The sharpest figure is that styles add no reach whatever on top of the genre list** — every
artist Discogs styles reach, Discogs genres already reach, which follows from `REL-`'s own
measurement that a Discogs release always carries a genre and only sometimes a style.

**`W4` dominates `W6` on every measured axis: identical reach, higher spread, lower redundancy —
and it was never evaluated.** The record's conclusion that adding Discogs is diminishing is
**true as stated and wrongly attributed**, and it pointed at the worse of two available
combinations. **`W6` must not be the frame any future amendment names.**

**The spread statistic is scale-sensitive and its magnitude should not be defended** — adding any
source gives artists more labels, which compresses a Jaccard regardless of quality. What survives
that objection is the **direction and the contrast**, because redundancy is a rank correlation and
therefore scale-free, and it separates the two columns the same way.

*(The `WGT-` probe has since carried this further under rarity and evidence weighting, and closed
the style column with a mechanism. Its figures are its own:
[`2026-08-01-label-weighting-probe.md`](2026-08-01-label-weighting-probe.md).)*

---

## The §5 read that fires

**Two bullets fire together, and neither may be dropped.** They are not in conflict — one reads
the kill bars, the other the guard.

- **"Both survive"** — `TAS-4` and `TAS-5` both clear their kill bars. §5: *"the architecture
  choice becomes a real decision with numbers on both sides, and it is the owner's. Neither is
  adopted on this document's evidence."*
- **"`TAS-6` adverse, anything else positive"** — §5: *"no adoption recommendation, whatever
  else holds. Reported in the summary, not in a footnote."* It is in §0.

**What I infer from the conjunction, labelled as inference and not as a §5 read.** The bullet
anticipating a live choice presupposes numbers on both sides that mean what they appear to mean,
and after the two controls neither side supplies them:

- The **build-time** side is barred by its own guard, and no `TAS-4` figure changes that.
- The **router** side clears its kill bar, but `TAS-AM5c` says the change it clears it on is not
  about genre — so the number is real and the attribution is not.

**So the architecture question is closed rather than open: neither side has an adoption case.**
That is a complete answer, not a partial one. **What would change it:** an adverse-`TAS-6`
mechanism that a richer frame removes (the coverage half of that is measured — `REL-` more than
doubles lower-half coverage — and whether it flips `TAS-6` is unmeasured and needs a rebuild), or
a router-side device whose change survives a label permutation.

**Nothing was left unrun.** The full λ grid, the full `w_coh` grid, both instrument checks on both
sides and all six criteria are in hand. No arm is "not run" and therefore none can be misread as
"returned nothing".

---

## Weakest link

**The load-bearing assumption is that the neutral rule is the right treatment of missing labels,
and `TAS-6`'s adverse verdict is downstream of it.** Where either artist is unlabelled, agreement
takes that artist's own median across its labelled candidates — never zero, deliberately, because
zero is a positive claim of dissimilarity and unlabelled candidates are disproportionately
obscure. It was fixed in §1 before any run and never adjusted. But it is **the one dormant term**:
inert at λ = 0 and active in every arm, so the baseline cannot reveal a bad choice of it. **A
different neutral rule could plausibly move `TAS-6` — and it could move it either way.** Attack
this first.

**What I would defend cheaply:** `TAS-1`, `TAS-2`, `TAS-3` and `TAS-4` — deterministic counts over
a fixed population, no sampling, no network, with the harness proved bit-identical to an
independently verified reference. And `TAS-AM5a`/`TAS-AM5b`, which are proofs rather than
measurements.

**What I would abandon on one contrary measurement:** any reading of `TAS-5`'s 90–100% as evidence
about genre (the null control already removes it); the two sub-decile interiors in the routing
guard; and `TAS-6`'s selection half as a *materiality* claim rather than a *bar-crossing* one —
93 baseline edges is a thin denominator, and while the bar is pre-registered and fires as written,
a rebuild could reasonably find the absolute effect small.

**One prediction class failed twice in one session and is worth carrying forward as a caution.**
Both this project's and the owner's mechanistic predictions about what these label sources *do*
were wrong, in the same direction: the coarse 15-value list was expected to make unrelated artists
look alike and the fine style list to be the valuable half — **the measurement reversed both.**
Separately, a prediction that famous artists' long tails of stray tags would make the device partly
a fame measurement was **retracted**; the effect is real but weak. *(And the first statement of that
retraction, "approximately zero", was itself measured on the wrong substrate and overstated the
case — on pre-cap candidate slots it is roughly six times larger. Both figures are in
`tas_weighting.json`, each labelled with its substrate.)* **Intuitions about these sources are not
reliable here**, which is the argument for decomposing a frame question rather than reasoning
about it.

## What this record cannot conclude

- **Nothing about whether genre tags track the owner's ear.** Discrimination is not validity. The
  `COH-4` retrodiction stays unrun and the **11 blind verdicts stay unconsumed**; `SYN-7` binds any
  future use of them.
- **Nothing that licenses adopting anything** — no weight, default, criterion, currency or
  vocabulary. `w_coh` remains harness-local and does not exist in `ApiConfig`.
- **Nothing about bound 100's hub cost.** That is Track B's `CRS-C4`; no arm here ran at bound 100,
  where the ranking is provably never consulted.
- **Nothing about what a rebuilt graph would route like.** `TAS-4` measures selection inputs only.
- **Nothing about whether a richer frame would flip `TAS-6`.** That needs a rebuild, which this
  probe does not do and does not license.
- **Nothing about the tag-based degree limiter** (`§7`) — owner-raised, ruled **separate and
  explicitly not ruled out**, and needing its own pre-registration designed cold.
- **Nothing durable.** Tag data moves; the frame was collected once, and a re-run months later is a
  new measurement rather than a reproduction.

## Amendments, and their disclosure

**Five, all in the pre-registration's §8, append-only, with their hazards named at their heads.
The disclosure positions differ and the differences must not be tidied away.**

| | written | position |
|---|---|---|
| `TAS-AM1` | **before** any `TAS-` figure existed | Replaced `TAS-4`'s quantity, statistic and bar; withdrew the original bar **as false** on `TD-2`/`TD-3`/`TD-4`'s evidence. |
| `TAS-AM2` | **before** any `TAS-` figure existed | Fixed the substrate per criterion, after writing `TAS-2` revealed the implicit answer was ambiguous. |
| `TAS-AM3` | ⚠ **after** results existed | Withdrew §4's red check **as unachievable** — for a Jaccard device, randomising labels destroys overlap rather than randomising it. Bounded by the naive shuffle's figure being **already committed**, so the direction was on the record before the text. |
| `TAS-AM4` | ⚠ **after** results existed | Evaluated the `REL-` frame as a candidate. Kept honest chiefly by **reusing `TAS-2`'s bars unchanged** rather than inventing new ones. |
| `TAS-AM5` | **before** any routing figure existed | Built the routing-side instrument check that `TAS-AM3`'s scope clause could not supply. |

**The withdrawn text is left standing throughout, struck rather than deleted**, because a
pre-registration whose errors are edited away cannot be checked. The git commit timestamps are the
evidence, and they are the half that cannot be reconstructed afterwards.

**Two defects in this probe's own output, recorded rather than absorbed.** A test passed on a
**tie-break** rather than the behaviour it named —
`test_a_dominating_weight_routes_through_the_agreeing_neighbour` was green with the coherence term
zeroed out, because the expected route was also what a lowest-id tie-break produces; found by
closeout mutation testing, fixed by expecting the higher-id route. And the substrate error in the
retraction noted above. **When a fixture has two symmetric routes, always expect the one a
tie-break would not pick.**
