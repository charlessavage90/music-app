# `TCE-` — do artists with almost nothing of their own recorded get ARTIFICIALLY STRONG links?

**Role: ACTIVE — governing document for the `TCE-` probe.** Committed **before any outcome
value is observed**; the git commit timestamp is the evidence, not this sentence.

**Plain-language question, fixed here so it cannot be reshaped by a result:** *when the app
looks at a famous artist's strongest connections, are artists with nothing of their own
recorded over-represented among them — and if so, does that survive into the map the website
actually serves?*

**Prompted by:** the Laura Lee closure, `builder/analysis/2026-08-06-laura-lee-closure/README.md`,
which **owns the figures** and against which this premise must be read.

> **⚠ The premise is PARTIAL, and this probe does not inherit a closed question.** The closure
> kills the same-name MBID collision hypothesis **for Laura Lee** and explicitly **does not
> settle it as a class** (its §4a). So
> `docs/superpowers/2026-08-06-cocredit-investigation-execution-log.md` §6 item 1 is
> **discharged for its worked case and OPEN as a population question** — it must not be
> recorded as closed, and **`TCE-` neither tests nor closes it.** They are different
> mechanisms.
>
> **And the case that motivated this probe does not support it** (closure §4c). A single artist
> cannot evidence a population pattern, and the cross-artist score comparison that makes her
> look striking is barred by §0 below. Two probes have already declined to attribute the
owner's observed class to band membership (`CCR-`, null and instrument-limited) or to shared
recording credits (`RCC-`, null and instrument-validated). **This is a third and different
mechanism, and it is not a variant of either.**

**⚠ This is NOT a route to widening the drop rule.** The owner ruled that out on 2026-08-06 —
he does not think Andrew VanWyngarden or Zach Condon should have been dropped — and that
ruling is untouched by any result here. This probe measures whether a link's *strength* tracks
how much of an artist exists. It proposes nothing about whether an artist appears at all.

---

## 0. The confound that would kill the naive design, and how this avoids it

**The naive design compares scores across artists** — "thin-catalogue artists have higher top
scores than thick-catalogue ones". The motivating observation is exactly that shape: Laura Lee
(Khruangbin) has 2 recordings and a top score of 214; Laura Lee (soul, b.1945) has 288
recordings and a top score of 65.

**That comparison is barred here, and `RCC-AM1` is why.** Nothing establishes that a score of
214 on one artist's list means the same thing as 214 on another's. `RCC-` hit the same class of
problem and fixed it by making the comparison *within one artist's own list*. This design does
the same, and it is the single most important thing about it:

> **Every comparison in this probe is WITHIN one reference artist's similar-list, using RANK,
> never raw score.** Rank within a list is unambiguously comparable regardless of how the
> underlying scores are scaled. Cross-artist score comparison appears nowhere and licenses
> nothing.

**The confound that remains, and it points against the hypothesis.** A famous artist's
strongest neighbours are plausibly *also* famous, and famous artists have large catalogues. So
the ambient expectation is that thin-catalogue artists sit LOW in a list. Finding them high is
therefore harder than chance, not easier — which is what makes a positive result readable. **A
negative or null result is correspondingly weak evidence** and §5 says so.

## 0.1 The dormant term — a knob nobody turns, which this intervention switches on

Per `CLAUDE.md`'s factor-table rule, the term inert in the baseline *for a reason the
intervention removes*:

**`similarity_rescale = p99_log_clip`.** Rank is invariant under any *monotone* transform, so a
rescale would normally be irrelevant to a rank-based design. **`p99_log_clip` is not monotone at
the top** — it clips, and clipped edges become **ties**. Ties are concentrated exactly where
this probe looks (the top of the list), so the rescale is dormant everywhere except in the arm
that matters. B1 measured the clipping as minor and found ordering survives
(`builder/analysis/2026-08-06-rescale-fidelity/README.md` owns those figures) — **but "minor"
is not "absent", and this design must not inherit it as an assumption.**

**Handled, not assumed away:**

- **Arm A reads RAW archived scores**, which are never rescaled. The rescale cannot reach it.
- **Arm B reads the shipped graph's stored scores**, which are. Ties are resolved by
  **average rank**, and the count of tied top-10 slots is **reported as run state**, not
  buried.

## `TCE-AM1` — the `±0.10` absolute band was unreachable and blind. Committed before any outcome value was observed.

**Status: this amendment GOVERNS where it and the original text disagree.** It was written after
a bounded derivation of the statistic's behaviour — **no part of `TCE-` was run, no base rate was
computed, and no `Δ_R` exists.** Derivation and figures:
`builder/analysis/2026-08-06-tce-c1-statistic-behaviour/`, which **owns them**.

### What was wrong

`TCE-C1` as originally written is a census **median** of `Δ_R`, and it fails twice at small base
rates. **Both were re-derived independently before this amendment was written**, not taken from
the derivation on trust:

1. **A ceiling failure — the statistic can be a CONSTANT.** If more than half the reference
   artists have **no thin neighbour anywhere in their list**, more than half have `Δ_R = 0`
   identically and the median is **exactly 0 whatever the placement does, in both directions**.
   That happens whenever `b < 1 − 2^(−1/L)` — about **0.007** for 100-entry lists, **0.023** for
   30-entry ones. Verified: at `b = 0.01`, `L = 60`, the median reads `+0.0000` at **every**
   effect size including a total one.
2. **A breakdown failure, and it is `ULC-R1` reproducing.** A median has a 50 % breakdown point,
   so an effect confined to a **minority** of reference artists moves it **not at all, however
   large**. Verified: at `b = 0.03`, an effect in **20 % of the census at maximum strength**
   reads `+0.0000` — squarely `null`. **`§4.3`'s claim that `ULC-R1`'s defect "is deliberately
   not repeated here" was false as written**, because recording the distribution does not help
   when **no branch reads it** and the decision rests on the median alone.

**The consequence that made this urgent:** `R3` fires on a null `TCE-C1` and closes the entire
co-credit investigation. A real effect in a fifth of the census produces exactly that reading.

### What changes

- **`§4.1`'s bands become a function of run state** (below), replacing the fixed `±0.05 / ±0.10`.
- **`§4.1`'s plain sentence is rewritten** to match `§1`'s population (below).
- **`TCE-G3` is added** — a pinning gate that can bar any read of `TCE-C1`.
- **`TCE-C3`, `TCE-C4`, `TCE-C5` are added**, because re-banding fixes *reachability* and does
  nothing for *blindness*. Their nulls are exact and base-rate-free, which is the whole point.
- **`R3` is conditioned on `TCE-C1` and `TCE-C3` both landing null.**

**`TCE-C1` is NOT removed or weakened.** It is kept, re-banded, and reported. Removing it after
seeing an inconvenient derivation — even a pre-outcome one — is the move this project's
pre-registration discipline exists to prevent.

### `TCE-G3` — the pinning gate. Computed from run state, before any `Δ_R` is read.

**Record the share of reference artists with `T_R = 0`** (no thin neighbour anywhere in their
list). **If that share exceeds 0.5, `TCE-C1` is a mathematical constant and NO read of it is
licensed** — not `enriched`, not `null`, not `R3`. `TCE-C3`–`C5` are unaffected and still read.

### `TCE-C1`'s bands, as a function of measured run state

Fixed here as a **functional form**; the value is filled in as run state (§6) **before any
`Δ_R` is read**, per the same discipline that fixes the base rate.

Let `C` = the **attainable ceiling**, the median over reference artists of

```
min(10, T_R)/10 − (T_R − min(10, T_R))/(L_R − 10)
```

— what `Δ_R` would be if every thin neighbour that artist has were crowded into its top ten.
**`C` depends only on `(L_R, T_R)`, so it is computable before any `x_R` is looked at.**

| `TCE-C1` | Branch |
|---|---|
| **≥ 0.50 · C** | `enriched` |
| **0.25 · C to 0.50 · C** | `indeterminate` — deliberately NEITHER |
| **−0.25 · C to +0.25 · C** | `null` |
| **≤ −0.25 · C** | `depleted` |

**If `C < 0.10` the scale is finer than the statistic's own lattice** (`Δ_R` moves in steps of
about 0.1 at the top) and **`TCE-C1` is reported as `no_resolution`, which fires no branch.**

*Why a fraction of the ceiling rather than an absolute number: the ceiling is what a total
effect would produce, so half of it is "the effect is at least half as big as it could possibly
be" — a statement that means the same thing at every base rate, which `+0.10` did not.*

### `§4.1`'s plain sentence — reconciled with the population, by rewriting the sentence

**Original:** *"among a **famous** artist's ten strongest connections…"*. **`§1` carries no fame
criterion**, so the sentence overclaimed.

**Replacement, and this is the fixed sentence for `TCE-C1`:** *when the app looks at any
artist's ten strongest connections, are artists with nothing of their own recorded
over-represented there compared with the rest of that same artist's list?*

**Rewritten rather than restricting the reference set by fame, for three reasons, recorded so
the choice can be argued with:**

1. **Arm A cannot compute it.** Arm A's reference set is the archive, and the archived
   similar-artist responses carry `name`, `comment`, `type`, `gender` and `score` — **no fame
   figure**. `fame_lb` enters only at build time. A fame criterion is therefore not computable
   in the arm that is the *isolating baseline*, which would make the two arms differ by a third
   column.
2. **It would bake in a guess about the concentrating variable.** "Famous artists" is one
   hypothesis about *where* an effect concentrates. `TCE-C5` locates concentration **without
   naming its cause**, which is the better instrument for something nobody has measured.
3. **It reintroduces a selection the census design exists to avoid.**

**Descriptive companion, with NO pre-registered read:** `TCE-C3` broken down by fame band, for
graph-present reference artists only. It keeps the owner's original intuition inspectable
without committing a branch to it. **No branch reads it and it may not rescue or overturn
anything.**

### The three added criteria, with exact nulls

| Criterion | Definition | **Exact null** | Bands |
|---|---|---|---|
| **`TCE-C3`** *(primary supplement)* | census **mean** of `M_R = P(X < x_R) + ½·P(X = x_R)` under that artist's own central hypergeometric on `(L_R, T_R)` | **exactly 0.500**, for every base rate and every list-length distribution | `≥0.55` enriched · `0.52–0.55` indeterminate · `0.48–0.52` null · `≤0.48` depleted |
| **`TCE-C4`** *(interpretation)* | `Σ x_R / Σ E[x_R]` | **exactly 1.000**, for every base rate | `≥1.5` enriched · `1.2–1.5` indeterminate · `0.8–1.2` null |
| **`TCE-C5`** *(locates concentration)* | share of reference artists with one-sided mid-p `≤ 0.05` | **base-rate dependent — computed exactly from the census's own `(L_R, T_R)` before any `x_R` is read**, and recorded in §6 | ratio to that computed null `≥ 2.0` = concentrated |

**Plain sentences, fixed here before any result exists:**

- **`TCE-C3`** — *pick an artist at random: how often does their real top ten hold more
  artists-with-nothing-of-their-own than a reshuffle of that same artist's own list would give?
  0.5 is a coin flip.*
- **`TCE-C4`** — *across everyone, how many times more artists-with-nothing-recorded sit in
  top-ten slots than chance puts there? 1.0 is exactly chance.*
- **`TCE-C5`** — *what share of artists have a top ten too crowded with them to be luck, and how
  does that compare with the share you would get by luck alone?*

### ⚠ What this amendment COSTS, stated because it is a real trade and not a free upgrade

**`TCE-C1`'s blindness to a minority was also robustness, and `TCE-C3`/`C4` give it up.**
Counting release-groups will classify MusicBrainz editor accounts, placeholder entries and
mis-merged MBIDs as `thin`. Under a median, a few dozen such entries change nothing; under a
mean they contribute linearly and could produce the entire headline. **Three mitigations, all
owed when this runs:**

1. **Report `TCE-C5` alongside `TCE-C3`**, so "a small effect everywhere" is distinguishable
   from "a large effect in 2 % of cases".
2. **Read the actual top tens of the twenty reference artists contributing most to `TCE-C3`.**
   Metrics and eyeballs, not metrics alone.
3. **Feed the hypergeometric each artist's post-`TCE-G2` list length**, not its raw one, or the
   null is computed for a list that was not scored. *(Implementation trap, not a judgement.)*

**A statistic the derivation explicitly warns against, recorded so nobody reinvents it:** the
naive "share of artists whose top-10 thin count **exceeds** its expectation" has a null of
**0.33–0.48, not 0.5**, and moves non-monotonically with the base rate — because most artists
have `x_R = 0` while `E[x_R] > 0`. Pre-registering it against a nominal 0.5 would read
**depletion under a perfect null.** `TCE-C3`'s mid-p form is what fixes it.

---

## `TCE-AM2` — every run-state quantity is PER ARM. Committed before any outcome value was computed.

**Clarifying, not redirecting.** `TCE-AM1` introduced quantities that depend on the census they
are computed over, and did not say which census. **They are per arm, and reading arm B against
arm A's numbers would be a category error**, because the two censuses are structurally
different: arm A's lists run to 100 entries, **arm B's are capped at 50**
(`union_degree_ceiling` / `max_neighbours_per_artist` in the adopted artifact's manifest), and
**arm B has thin artists largely removed by the very filters that define the arm.**

**Binding:**

1. **`C` (the attainable ceiling), `TCE-G3`'s `T_R = 0` share, and `TCE-C5`'s exact null each
   take an arm A value and an arm B value**, computed from **that arm's own** `(L_R, T_R)`.
   Written `C_A` / `C_B`, and so on. The thin base rate is likewise per arm.
2. **`§4.2`'s "read against the same four bands" means the same FUNCTIONAL FORM** — fractions of
   **that arm's own** `C` — **never arm A's numeric bands.** `TCE-C2` is read against
   `0.50·C_B`, `0.25·C_B` and so on.
3. **`TCE-C3`, `TCE-C4` and `TCE-C5` are computed for BOTH arms.** `R1` and `R2` both read both
   arms, so a single-arm value cannot serve either. Their nulls (0.500 and 1.000) are
   base-rate-free and so are identical across arms; **`TCE-C5`'s null is not**, and is computed
   per arm.
4. **`TCE-G3` is evaluated per arm and can bar one arm's `TCE-C1` read while leaving the
   other's standing.** If it bars arm B, `TCE-C2` is reported as `no_read_licensed` and `R1`
   and `R2` rest on `TCE-C3`/`C4`/`C5` for that arm.

> **⚠ Expect arm B to be the one at risk, and that is not a failure of the run.** The drop
> filters remove artists with nothing of their own to play, which is close to this probe's
> `thin`. Arm B's base rate may therefore be low enough to pin its median. **A pinned arm B is
> a finding about the filters, not a broken probe** — but it must be reported as
> `no_read_licensed`, never as `null`.

**`TCE-G1`'s MBIDs are display-truncated in its table** (`50ef58c4…` and the rest). **The
authoritative full MBIDs are `builder/analysis/2026-08-06-laura-lee-closure/ll_closure.json`**,
a committed source. The run **must read them from there and record that it did so** in its
output, rather than re-deriving them from a truncated string.

---

## 1. Population — a CENSUS, not a sample

**Compute is free once the instrument exists, so there is no sampling and no seed.** Every
reference artist meeting the criteria is used, which removes sampling error and any argument
about a seed.

- **Arm A reference set:** every artist in the 75,000-artist `ALG-B` archive
  (`builder/scratch/grt-archive-algb/similar/…`, population sha
  `381305a73f7c6a9cba338e207d1a9ae7890709169afa3c4d953944b5fc6477be`) whose archived
  similar-list has **≥ 30 entries**. The floor exists so "top 10 vs the rest" has a rest.
- **Arm B reference set:** every artist **present in the adopted artifact**
  `graph-msw-tu50.bin`, sha `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`
  (verified against its manifest sidecar 2026-08-06), with **degree ≥ 30**.

**The two reference sets are deliberately different sizes and that is not a defect** — the
difference between them *is* arm B's intervention. See §2.

## 2. Factor table

| Arm | Edge source | Drop filters applied | Scores rescaled | Isolating baseline |
|---|---|---|---|---|
| **A** | raw ListenBrainz archive | **no** | no | — (this is the baseline) |
| **B** | adopted graph `43dd82bb…` | **yes** (`drop_unlistenable`, `drop_no_release_tail`, `drop_featured_credit`) | yes | **A** |

**A and B differ by two columns, not one, and the design says so rather than claiming
otherwise.** The rescale rides along with the filters because the shipped artifact carries
both; no artifact exists with one and not the other, and building one is not worth it. **The
consequence is named and binding:** a difference between A and B **may not be attributed to
the drop filters alone**. §5's `R2` is written to respect this — it reads the A→B difference as
"something between the raw feed and the shipped map removes it", never as "the filters remove
it".

**Held constant, and why each is genuinely constant under the intervention:**

- **The connection rule (`trimmed_union`).** Classification is by MusicBrainz release-group
  count, computed from a dump the builder never reads. No connection rule can change an
  artist's catalogue.
- **Fame and the `known` ramp.** Both are router-side, applied at query time. This probe reads
  stored edges and runs no journeys, so neither term is reachable.
- **`pop_raw`.** Not used anywhere in this design — deliberately, because popularity here is
  score-weighted in-degree computed *from these very edges*, so using it would be circular.

## 3. The instrument, and the gate that must pass before any outcome is computed

**Catalogue size** = the number of MusicBrainz **release-groups** on which the artist appears
in `artist-credit`, counted by one streaming pass over
`builder/scratch/mb-json-dumps/release-group/mbdump/release-group` (dump dated 2026-07-29).
**This is a superset of "sole-credited"** and is deliberately looser than the adopted drop
rule's criterion; §5's barred reads carry the consequence.

**An artist is `thin` iff that count is 0.** The gradient (counts 1, 2, 5, 10) is reported as
descriptive secondary output with **no pre-registered read** — see §4.3.

### `TCE-G1` — instrument validation. Evaluated FIRST and ALONE.

`CCR-` returned a null its instrument could not have distinguished from a positive. That must
not recur, so the counter is validated against known answers **before any outcome value is
computed**:

| Artist | MBID | Required |
|---|---|---|
| Laura Lee (Khruangbin member) | `50ef58c4…` | **0** |
| Laura Lee (soul/gospel, b.1945) | `70a65cf5…` | **≥ 20** |
| Leon Bridges | `69d9dfd7…` | **≥ 5** |
| Khruangbin | `aea4c9b9…` | **≥ 5** |

**Any cell failing → the probe is VOID.** Not a weak pass, not a caveat, not "the instrument
is approximate". Void means no outcome is computed and no result is reported beyond the gate
failure itself.

### `TCE-G2` — coverage floor.

**≥ 95 % of neighbours across the arm A reference set must resolve to a count** (present in
the dump, whether the count is 0 or 500). Below that the dump and the archive describe
different populations and the probe is **VOID**. Between 95 % and 100 %, the exact figure is
reported as run state and unresolved neighbours are **excluded from both numerator and
denominator**, never silently counted as thin.

## 4. Outcomes

### 4.1 `TCE-C1` — the primary outcome

> **⚠ SUPERSEDED IN PART BY `TCE-AM1`** — the plain sentence below and the band table further
> down are **replaced** there. The definition of `Δ_R` is unchanged. Read `TCE-AM1` first.

**Plain-language sentence — ~~*among a famous artist's ten strongest connections, are artists
with nothing of their own recorded over-represented compared with the rest of that same
artist's list?*~~** *(struck by `TCE-AM1`: `§1` carries no fame criterion and arm A cannot
compute one. The governing sentence is `TCE-AM1`'s. Struck rather than deleted — it is what was
committed first.)*

For each reference artist `R`:

```
p_top   = share of R's ranks 1-10 that are thin
p_rest  = share of R's ranks 11-end that are thin
Δ_R     = p_top − p_rest
```

**`TCE-C1` = the median of `Δ_R` across the reference set**, reported separately for arm A and
arm B. Positive means thin artists crowd the top of lists.

**Pre-registered effect size — ⚠ THIS TABLE IS SUPERSEDED BY `TCE-AM1`.** It is retained
because it is what was committed first and the record of what changed is the point. **Do not
read a branch off it.**

| ~~`TCE-C1`~~ | ~~Branch~~ |
|---|---|
| ~~**≥ +0.10**~~ | ~~`enriched`~~ |
| ~~**+0.05 to +0.10**~~ | ~~`indeterminate`~~ |
| ~~**−0.05 to +0.05**~~ | ~~`null`~~ |
| ~~**≤ −0.05**~~ | ~~`depleted`~~ |

*Struck by `TCE-AM1`: at small base rates this band is unreachable — the statistic can be a
constant 0 at every effect size — and it is blind to an effect concentrated in a minority. The
governing bands are `TCE-AM1`'s, expressed as a fraction of the attainable ceiling `C`.*

**The middle band names no default and none may be supplied afterwards.** It follows
`CAU-C1`'s precedent. A result landing there is reported as landing there.

**Why +0.10.** Ten points of enrichment means a person building journeys meets a visibly
different top-of-list than the rest of the list would predict, and it sits comfortably above
the ±0.05 band where list-length and tie artefacts live.

**⚠ The thin base rate is RUN STATE, not a known quantity, and this document must not pretend
otherwise.** `unlistenable_drop_algb_20260805.json`'s `counts.class` covers artists with no
*sole-credited substantial* release group. **This probe's `thin` is STRICTER** — zero credited
release-groups of any kind — so `TCE-`'s thin set is a **subset** of that class and its share
is bounded above by it, not equal to it. **The exact base rate is computed and reported as run
state (§6) before `TCE-C1` is read**, and `Δ_R` is a within-list contrast that does not depend
on it. *(This paragraph replaced an earlier draft that took the cited 24.7 % as this probe's
base rate. It is not; the subset relation makes it an upper bound.)*

### 4.2 `TCE-C2` — does it survive to what users see?

**Plain-language sentence:** *whatever the raw feed does, is it still there in the map the
website serves today?*

**`TCE-C2` = `TCE-C1`(arm B)**, read against the same four bands. It is stated separately from
`TCE-C1` because it is the decision-relevant half and must not be reported as a footnote to
arm A.

### 4.3 Descriptive, with NO pre-registered read

- The gradient: `TCE-C1` recomputed at thin-thresholds 1, 2, 5, 10.
- The distribution of `Δ_R`, not only its median — `ULC-R1`'s recorded defect was a statistic
  that could not see an effect concentrated in a minority, and that defect is deliberately not
  repeated here.
- Tied-rank counts in arm B (per §0.1).

**No branch reads these. They may not be used to rescue or overturn `TCE-C1` or `TCE-C2`.**

## 5. The read of every result, including the null

**Every read below presupposes the run state in §6. No read is licensed before it.**

- **`R1` — `enriched` in BOTH arms.** The mechanism is real and it reaches users. **Report to
  the owner with options; adopt nothing.** This is the only branch that would justify further
  work, and even then the work is *measurement of user-visible impact*, not a scoring change —
  B1 established that the similarity signal is load-bearing and that changing it is a risk to a
  working mechanism, not a cheap win.
- **`R2` — `enriched` in arm A, `null` in arm B.** The raw feed has it; **something between the
  raw feed and the shipped map removes it.** Per §2 that may **not** be attributed to the drop
  filters alone — two columns differ. **The investigation closes anyway**, because the
  decision-relevant arm is negative and no user is affected. Attribution would be a separate
  probe and is not owed.
- **`R3` — `null` in arm A. ⚠ AMENDED BY `TCE-AM1`: `R3` fires only when `TCE-C1` AND `TCE-C3`
  BOTH land null.** A null `TCE-C1` alone is consistent with a real effect in a fifth of the
  census at maximum strength, and `R3` closes an entire investigation — the two facts must not
  meet. **If `TCE-G3` bars a `TCE-C1` read, `R3` rests on `TCE-C3` alone and says so.**
  The thin-catalogue hypothesis is wrong. **Three mechanisms have
  now been ruled out** and the owner's original observation remains unexplained. **The
  co-credit investigation closes entirely**, and the honest statement is that we do not know
  what produces the class he saw. Arm B is still computed and reported; it cannot rescue a null
  arm A, and no read may treat it as doing so.
- **`R4` — `depleted` in arm A.** Thin artists sit *lower* than the rest of the list. Reported
  as the opposite finding, with the §0 confound named as the likely cause. **Closes.**
- **`indeterminate` in either arm.** Reported as indeterminate to the owner as data. **No
  branch fires and no default is supplied.** If he wants a bar set afterwards, that is a new
  pre-registration, not an amendment to this one.

### Barred reads — these travel with every citation of this document

1. **No adoption follows from any branch.** No default, weight, filter or threshold changes on
   this result.
2. **This does not reopen widening the drop rule.** Closed by the owner 2026-08-06.
3. **Release-group count is a proxy** for "how much of their own work exists". It is not listen
   volume, not catalogue quality, and it is looser than the adopted drop rule's
   sole-credited-and-substantial criterion.
4. **Enrichment at the top of a similar-list is NOT "appears in journeys".** The router's cost
   function has several other terms and this probe runs no journeys. Any claim about what a
   user meets requires a different measurement.
5. **A→B differences are not attributable to the drop filters alone** (§2, two columns).

## 6. Run state a read presupposes

**Every read in §5 presupposes ALL of the following. A read taken before them is void, and this
sentence exists because a previous track's read was reachable four arms early and nearly cost
the only signal in fifteen.**

- **`TCE-G1` passed on all four cells.**
- **`TCE-G2` passed**, with the coverage figure recorded.
- **The thin base rate computed and recorded** for both reference sets (§4.1), before
  `TCE-C1` is read.
- **`TCE-AM1`'s run-state quantities, ALL computed before any `Δ_R` or `x_R` is read:** the
  share of reference artists with `T_R = 0` (`TCE-G3`); the attainable ceiling `C`, which fixes
  `TCE-C1`'s bands; and `TCE-C5`'s exact null, computed from the census's own `(L_R, T_R)`.
  **These are functions of list membership only. Computing them after looking at where the thin
  artists sit would forfeit the pre-registration**, and the run must record that it did not.
- **BOTH arms computed.** Arm A alone licenses nothing — not `R3`, not `R1`. If arm B is not
  run, the probe is incomplete and the correct report is "incomplete", never a partial read.
- **The `Δ_R` distribution recorded**, not only its median (§4.3).

**What is owed before this probe runs at all:** the Laura Lee closure must be written up and
committed, because this document cites it as its premise. **A probe whose stated premise is
uncommitted is not pre-registered.**
