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

**Plain-language sentence, fixed here:** *among a famous artist's ten strongest connections,
are artists with nothing of their own recorded over-represented compared with the rest of that
same artist's list?*

For each reference artist `R`:

```
p_top   = share of R's ranks 1-10 that are thin
p_rest  = share of R's ranks 11-end that are thin
Δ_R     = p_top − p_rest
```

**`TCE-C1` = the median of `Δ_R` across the reference set**, reported separately for arm A and
arm B. Positive means thin artists crowd the top of lists.

**Pre-registered effect size:**

| `TCE-C1` | Branch |
|---|---|
| **≥ +0.10** | `enriched` |
| **+0.05 to +0.10** | **`indeterminate` — deliberately NEITHER** |
| **−0.05 to +0.05** | `null` |
| **≤ −0.05** | `depleted` (the opposite of the hypothesis) |

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
- **`R3` — `null` in arm A.** The thin-catalogue hypothesis is wrong. **Three mechanisms have
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
- **BOTH arms computed.** Arm A alone licenses nothing — not `R3`, not `R1`. If arm B is not
  run, the probe is incomplete and the correct report is "incomplete", never a partial read.
- **The `Δ_R` distribution recorded**, not only its median (§4.3).

**What is owed before this probe runs at all:** the Laura Lee closure must be written up and
committed, because this document cites it as its premise. **A probe whose stated premise is
uncommitted is not pre-registered.**
