# Release-tag aggregation coverage — pre-registration

**Role: ACTIVE pre-registration.** Identifier series: `REL-` (checked free across the repo
before allocation). Committed **before any coverage measurement runs**; the git timestamp is
the evidence that every bar below predates every number it judges.

**Scope: a descriptive coverage probe.** It adopts nothing, fixes no criterion, changes no
weight, default, currency, vocabulary, or document that defines "better", and requires no
rebuild, no API change and no listening test. It does **not** settle any open owner decision
in `NEXT.md`. It does **not** amend the `TAS-` pre-registration: §1 of that document pins the
label vocabulary, and **nothing here changes it** — a frame that passes every bar below is a
*candidate* for a future `TAS-` §8 amendment, never an enactment of one.

**Commissioned by the owner 2026-07-31**, recorded in the `TAS-` execution log §12.2, which
also carries four constraints from the retiring session. All four are honoured below and
cited where they land.

---

## §0 Prior knowledge, declared

**Some numbers already existed when this document was written. Concealing that would make
every bar below look stronger than it is.**

| Known before this document | Value | Where from |
|---|---|---|
| Artists carrying no genre label today | **33,756 / 74,193 (45.5%)** | census over the committed `tas_tags` frame, this session |
| Same, lower-half band | **23,959 / 37,096 (64.6%)** — so 35.4% labelled | as above; independently reproduces `COH-2`'s sampled 35.3% |
| Unlabelled artists with ≥ 1 release group | **lower half 66.4%** | ListenBrainz batched census, this session |
| Unlabelled artists with ≥ 1 *attributable* release group | **lower half 55.0%** | as above, under the §1 filter |
| Absolute ceiling on lower-half coverage | **71.0% strict / 78.3% permissive** | derived from the two rows above |
| Fill rates in the three dumps | release-group tags 42.4%, release tags 13.5%, Discogs genre 100% | 2,000–3,000-record samples per dump, this session |

**`REL-1`'s 50% bar was fixed and stated in writing *before* the ceiling above was
measured.** That ordering is the only reason the bar is credible, and it is the one claim in
this section that matters. The ceiling figures are *upper bounds* — they can say "no more
than this" and can never say whether a bar is cleared — so seeing them cannot have tuned a
bar that judges a realised value.

**The dump fill rates are over whole databases, not over our population.** They are recorded
as provenance for the design (they are why the release dump is out of scope) and are **not
predictions** of any figure below.

---

## §1 The device

**Aggregated label set.** For an artist `a`, the union of normalised genre labels over `a`'s
**attributable** releases:

```
agg(a) = ⋃ { norm_genre(t) : t ∈ labels(r), r ∈ attributable(a) }
```

Empty normalised labels are dropped — `norm_genre` can return `""` for punctuation-only
input, and an empty string would otherwise read as a genre shared by every artist carrying
one.

**Normalisation is the frozen `ct_common.norm_genre`, imported and never reimplemented**, so
this record and `COH-`/`TAS-` speak one vocabulary.

### `attributable` — the validity filter, fixed here, before any run

This is the **dormant term** of this design, and it has the same shape as `w_floor` in the
Track 2 pre-registration's §0 and the neutral rule in `TAS-` §1: **it is inert in the
baseline and active in every arm.** `F0` performs no aggregation, so no filter applies to it
and the baseline cannot reveal a bad filter; every arm can. It is therefore fixed now and
must not move after a result exists.

| Source | A release counts when |
|---|---|
| MusicBrainz release group | `artist-credit` has **exactly one** entry, and that entry's `artist.id` is the artist; `primary-type` ∉ {Broadcast}; `secondary-types` ∩ {Compilation, Live, DJ-mix, Mixtape/Street, Remix, Interview, Spokenword, Audiobook, Audio drama} = ∅ |
| Discogs release | `<artists>` has **exactly one** entry and its `<id>` is the mapped Discogs artist id; that id ≠ `194` (Various Artists); the artist appears in `<artists>`, **never** via `<extraartists>` |

**Why sole-credit rather than membership:** a split release or a collaboration attributes the
other party's genres to this artist, and a Various-Artists compilation attributes a curator's.
Both raise coverage while making labels worse — the failure `TAS-` §12.2 item (b) named, and
the one a coverage number structurally cannot show. `REL-3` is what actually tests whether the
filter worked; this row only makes the attempt.

**Why `extraartists` is excluded on the Discogs side:** its `<role>` vocabulary is dominated
by *Producer*, *Written-By*, *Mastered By*, *Lacquer Cut By*. A mastering engineer is not the
genre of the record.

### Minimum support: **one release**, and why

A label counts if it appears on **≥ 1** attributable release. **The median unlabelled
lower-half artist has 2 release groups** (§0), so a ≥ 2 threshold would discard most of the
target population by construction — it would measure prolificacy, not tagging.

The cost is that a single mis-tagged EP can define an artist's genre. That is not waved away:
**every aggregated label is emitted with its support count**, so the fragility is visible in
the raw output, and `REL-3` measures its consequence directly rather than assuming it away.

### The frames

Every arm differs from its named baseline by **exactly one column**.

| Frame | Source | Unit | Vocabulary | Filter | Isolating baseline | Differs by |
|---|---|---|---|---|---|---|
| `F0` | LB genre-tags ∪ Wikidata P136 | **artist** | genre-whitelist | n/a | — | *(this is today)* |
| `F1` | MB release-group dump | release group | `genres` (whitelist) | strict | `F0` | unit of attachment |
| `F2` | MB release-group dump | release group | `tags` (wide) | strict | `F1` | vocabulary width |
| `F3` | MB release-group dump | release group | `genres` | **permissive** | `F1` | validity filter |
| `F4` | Discogs releases | release | `<genre>` (15 values) | strict | `F1` | source |
| `F5` | Discogs releases | release | `<style>` (~600 values) | strict | `F4` | vocabulary granularity |
| `F6` | `F1` ∪ `F4` ∪ `F5` | both | both | strict | `F1` | a second source added |

Every frame is reported as `F0 ∪ frame` — aggregation **adds** labels, never replaces them.
"Permissive" in `F3` means the filter is dropped entirely: every release group the artist is
credited on counts.

### Held constant, and why each is genuinely constant under this intervention

| Held | Why it cannot move here |
|---|---|
| The graph artifact and the fame frame | **Nothing is rebuilt.** Band membership comes from `cb_metrics.band_of` over the adopted artifact, sha256 asserted on load, imported not reimplemented — so this record is comparable with `COH-`, `FPC-` and `TAS-` rather than merely adjacent. |
| `F0`, the baseline frame | **This is the trap of this design and it is named rather than assumed.** The MusicBrainz *artist* dump carries artist-level `tags`/`genres` for every artist. Using it to define `F0` would silently redefine "unlabelled", moving every coverage figure below for a reason that has nothing to do with aggregation. **`F0` stays the committed `tas_tags` LB ∪ P136 frame.** The artist dump's tags are used in exactly one place — `REL-7`, a cross-check that is not a gate and feeds no other criterion. |
| Genre normalisation | Frozen `ct_common.norm_genre`. A change is an amendment, not an improvement. |
| The `TAS-` vocabulary | Untouched. No frame here enters `tas_common`; `TAS-` §1 still pins LB ∪ P136. |
| Router weights, `BuilderConfig`, `cap_strategy`, `k`, rescale, damping | Not read and not written. No pathfinding runs in this document. |
| Noise floor | **None — every pass is deterministic over frozen local files.** Every bar below is a *materiality* bar, never a significance bar. No sampling: every figure is a census over all 74,193 nodes. |

---

## §2 Criteria

Every criterion carries its plain sentence, fixed here, before any result exists. Owner-facing
text quotes identifier **and** sentence.

### `REL-1` — the headline *(gate)*

> *Plain: after looking at what they released, for how many of the obscure artists we
> currently know nothing about do we now know a genre?*

**Measured:** share of **all** lower-half-band artists carrying ≥ 1 label under `F0 ∪ F1`.
Same band, same denominator and same vocabulary family as `COH-2`, so the two are directly
comparable.

**Bar: ≥ 50%.** Inherited from `COH-2`'s committed kill gate — same bar, same band, same
denominator. Not renegotiated, and stated in writing before the ceiling was measured.
Baseline to beat: **35.4%**.

Reported for every frame `F1`–`F6`; **the gate is judged on `F1` alone**, the conservative
frame. A frame that clears only under `F3` (permissive) has cleared a different bar.

### `REL-2` — the Discogs mapping ceiling *(descriptive; `REL-4` is uninterpretable without it)*

> *Plain: for how many of these artists can we even find a Discogs page — and of those, how
> many actually have records listed?*

**Measured, per band, over unlabelled artists:** (a) share with a `discogs` url-rel in the MB
artist dump; (b) of those, share whose Discogs artist id appears on ≥ 1 attributable release;
(c) the product, which is the Discogs route's true ceiling.

**Not a gate.** This is `TAS-` §12.2 item (c) made mechanical: a high tag rate among artists
that resolve is not a gain of that size if resolution is partial. **Any `F4`/`F5`/`F6` figure
quoted without `REL-2` beside it is misreported.**

### `REL-3` — validity, the held-out check *(gate)*

> *Plain: when we guess an artist's genre from their records, and we already happen to know
> the real answer, how often do we get it right?*

**Population:** artists **labelled today** (`F0` non-empty) with ≥ 1 attributable release —
about 40,437 before the release filter. Their known `F0` set is held out; the aggregation is
run as if they were unlabelled and scored against it.

**Measured:** Jaccard between `agg(a)` and `F0(a)`. Report the median, the share at ≥ 0.5, and
the **zero-overlap rate** — the share where the aggregation and the truth share nothing at
all, which is the outright-wrong rate.

**Bar, expressed against a null rather than an invented threshold:** the matched median
Jaccard must be **≥ 3×** the median of the same statistic under `REL-C2`'s shuffled ownership,
**and** the zero-overlap rate must be **below** the shuffled rate by at least 20 percentage
points.

**Why a null and not a fixed number:** genres are unevenly distributed, so a large share of
artists agree on "rock" by chance. A fixed Jaccard bar would be satisfied by that base rate.
The shuffle measures the base rate directly and the bar is stated as a multiple of it.

**This gate is the whole answer to `TAS-` §12.2 item (b).** Coverage rising while labels get
worse is a *pass* on `REL-1` and a *fail* here, and the design must be able to say so.

### `REL-4` — does the second source add anything? *(descriptive)*

> *Plain: does Discogs reach artists MusicBrainz misses, or the same ones twice?*

**Measured:** lower-half coverage of `F6` minus `F1` — the **incremental** gain, never the
total. Also the label-level agreement between the two sources where both fire, since two
sources agreeing is worth more than either alone and two sources disagreeing is a finding.

### `REL-5` — what the validity filter costs *(descriptive)*

> *Plain: how many artists do we give up on by refusing to guess from compilations and
> collaborations?*

**Measured:** `F3` minus `F1`, lower half, in artists and in percentage points. Priced in
advance at **2,730 artists (11.4% of the unlabelled lower half)** by the §0 ceiling census;
this is the realised figure.

### `REL-6` — does the gain land in the tail, or in the middle? *(guard — reported, never a success signal)*

> *Plain: does this fix the obscure artists we built the app to surface, or mostly the
> nearly-famous ones that were almost covered already?*

**Measured:** coverage gain in percentage points, per band, `F1` − `F0`.

**Adverse if the lower-half gain is less than half the upper-half gain.** That would mean the
new frame reproduces the existing skew rather than correcting it — richer labels where labels
were already good, which is `TAS-` §12.2 item 2's explicit statement that such a frame
"changes nothing here".

**A guard, never a success signal.** A favourable `REL-6` licenses nothing on its own.

### `REL-7` — census-scale fidelity cross-check *(descriptive, not a gate, feeds nothing)*

> *Plain: does the offline copy of MusicBrainz agree with the live data we collected last
> week?*

**Measured:** artist-level `tags`/`genres` from the MB artist dump against the committed
`tas_tags` LB frame, over all 74,193 nodes. Extends `COH-5` from n = 872 to a census.

**Why it exists:** the dumps are dated 2026-07-28/29 and the `tas_tags` frame was collected
live on 2026-07-30. Without this, snapshot drift would be indistinguishable from a finding.
**It is walled off from `F0` by the §1 held-constant row** and must not be used to redefine
the population.

---

## §3 Population and sources

**Population:** all 74,193 nodes of the adopted artifact (`graph-t15-tiebreakfix.bin`,
sha256 asserted on load). **Census, not sample** — no seed, no CI, no noise band, because the
dumps are local and every pass is deterministic.

The **unlabelled** population (33,756) is where `REL-1`, `REL-2`, `REL-5` and `REL-6` are
measured. The **labelled** population (40,437) is where `REL-3` is measured. `TAS-` §12.2 item
(a) required exactly this split, banded as `COH-2` banded it.

**Note the top two bands are empty by construction** — 0 unlabelled artists in the top 0.1%
and 1 in the top 1%. Only three bands carry a population, and the headline is a lower-half
figure. This is a property of the question, not a defect of the draw.

| Source | Path under `builder/scratch/` | Verified |
|---|---|---|
| Adopted artifact | `graph-t15-tiebreakfix.bin` | sha256 in `cb_metrics.ADOPTED_SHA` |
| MB artist dump | `mb-json-dumps/artist/mbdump/artist` | JSONL, 17.2 GB, `relations` carries `discogs` |
| MB release-group dump | `mb-json-dumps/release-group/mbdump/release-group` | JSONL, 18.0 GB, `tags`/`genres`/types/credits |
| Discogs releases | `discogs-data-dump/discogs_20260601_releases.xml` | XML, 61.6 GB, closes `</releases>`, artist ids 100% |
| `F0` label frame | `analysis/2026-07-30-tag-discrimination/tas_tags_raw.json` + `tas_wikidata_raw.json` | untracked working-tree files; `label_sets()` |

**All four large files are gitignored and live only in the main working tree** — they are not
in git and would not appear in a worktree (`TAS-` §12.2's practical note). Any re-run points at
`builder/scratch/` explicitly.

**The MB `release` dump (345 GB) is out of scope and has been deleted.** Release-level tags
measured at 13.5% against release-group's 42.4% — the aggregation unit is the album concept,
not the pressing. A union pass over it is named in §7 as a follow-up lever, not a step here.

---

## §4 Instrument checks — both must pass before any criterion is read

A green result from a new instrument is not evidence until the instrument has been shown to
go red.

### `REL-C1` — liveness and equivalence

Point the aggregation pipeline at **artist-level** tags from the MB artist dump instead of
release-level tags, and require it to reproduce a known answer: the labelled count of the
committed `tas_tags` frame, to within the drift `REL-7` measures independently.

**Fails if** the reproduction is outside `REL-7`'s measured drift. An instrument that cannot
recover an answer we already have is not believable on answers we do not.

**Ordering, stated because it is not obvious: `REL-7` runs FIRST.** `REL-C1`'s tolerance *is*
`REL-7`'s drift figure, so the cross-check must exist before the liveness check can be judged.
This is the one place a descriptive criterion gates an instrument check, and it is the reason
`REL-7` is walled off from `F0` in §1 — it supplies a tolerance, never a population.

### `REL-C2` — null control, on the axis that can actually move

Shuffle the **artist → release ownership** mapping, preserving each artist's release count,
and re-run. This is also the null `REL-3`'s bar is expressed against.

**Two things this null does and does not do, stated now because `TAS-AM3` is the worked
example of a red check that could not fire as written:**

- **It is informative for `REL-3`.** Under shuffled ownership the aggregated set is a random
  artist's genres, so matched Jaccard must collapse toward chance. If it does not, `REL-3`'s
  agreement is a base-rate artifact and not evidence of anything.
- **It is NOT informative for `REL-1`, and must never be quoted as if it were.** Coverage is
  near-invariant under this shuffle by construction — a randomly assigned album still carries
  tags, so a randomly assigned artist still ends up labelled. Randomising ownership relocates
  coverage rather than destroying it. **Any coverage figure from `REL-C2` is meaningless and
  is reported only to make that visible.**

---

## §5 Reads — every result, including the null, and the run state each presupposes

**Run state, stated per read.** `REL-1` and `REL-3` presuppose `REL-C1` and `REL-C2` have both
passed. `REL-4` presupposes `F1`, `F4` and `F5` have all run — a Discogs figure read without
its MusicBrainz counterpart, or vice versa, is uninterpretable. `REL-2` must be run and quoted
beside **every** `F4`/`F5`/`F6` figure. **No read below is reachable before `REL-C1` and
`REL-C2` have run, and none may be taken early on the grounds that the pattern looks clear.**

| Outcome | Read |
|---|---|
| `REL-1` ≥ 50%, `REL-3` passes, `REL-6` not adverse | The strongest available result. The frame is a **candidate**, and the next step is an owner decision on whether a `TAS-` §8 vocabulary amendment and a rebuild are worth their cost. **This document adopts nothing and licenses no rebuild.** |
| `REL-1` ≥ 50%, `REL-3` **fails** | **A kill, not a trade-off.** Coverage rose and the labels got worse — exactly what §12.2 item (b) predicted. A `TAS-` device consuming confidently wrong labels is worse than one that stays silent where labels are missing, because silence is safe in a way error is not (`TAS-1`'s own reasoning, applied here). Report the coverage figure with the failure attached to it, never alone. |
| `REL-1` in **45.0–49.9%** | A near miss. The frame does not clear `COH-2`'s bar, and re-gating on a different population after seeing this number is forbidden — the same trap `COH-3` was caught by. **This band, and only this band, fires §7's release-dump union pass**, because that is the one lever whose plausible increment could close a gap this size. |
| `REL-1` in **38.5–44.9%** | A real gain that does not clear the bar. **No instrument is built on it.** The increment is recorded for a future pre-registration designed cold; nothing here licenses one. |
| `REL-1` **< 38.5%** (gain under 3 points — the null) | Obscure artists' releases are as untagged as the artists themselves. This **falsifies the mechanism §12.2 recorded as the argument *for*** — that MusicBrainz effort attaches to the release a person just added — and confirms the argument *against*: the indifference that left the artist bare left the records bare. **Closes the MusicBrainz release-aggregation line.** Discogs is read separately; a MusicBrainz null does not transfer to it. |
| `REL-6` adverse, whatever `REL-1` says | The gain is in the wrong place. **Says nothing about whether `TAS-6` could flip** — `TAS-6`'s adverse result is driven by unlabelled *obscure* candidates being squeezed out, and a frame that thickens the upper half does not touch that. Recommendation to adopt is barred regardless of `REL-1`. |
| `REL-2` product **< 50%** in the lower half | The Discogs route is mapping-bound, not tag-bound. Its 100% genre fill is then a fact about Discogs' schema and **not** a coverage gain of that size. `F4`/`F5`/`F6` are reported as bounded by `REL-2` and no Discogs claim survives without it. |
| `REL-4` **< 2 percentage points** | The two sources reach the same artists. Discogs' independence buys a cross-check on *validity* but no coverage, and the case for carrying a second vocabulary weakens sharply. |
| `REL-C1` or `REL-C2` fails | **Nothing above is read at all.** The instrument is repaired or withdrawn first, and any repair after a result exists is an §8 amendment carrying `TAS-AM3`'s disclosure. |

---

## §6 What this probe cannot conclude

- **Nothing about whether tags track the owner's ear.** No retrodiction, no listening test.
  Coherence still has no validated offline metric in any currency.
- **Nothing that licenses a criterion, weight, default, currency or vocabulary change.**
  A pass makes the frame a candidate for a `TAS-` §8 amendment; it does not make one.
- **Nothing about whether `TAS-6` would flip.** That requires a rebuild under a richer frame,
  which this document does not do and does not license.
- **Nothing about release-*level* tagging.** The 345 GB release dump is out of scope (§7).
- **Nothing durable about MusicBrainz or Discogs content.** Both move; these dumps are
  2026-06-01 and 2026-07-28/29 snapshots and a re-run later is a new measurement.
- **Nothing about the 8,043 lower-half artists with no release at all.** They are outside
  every frame here by construction, and no release-aggregation method of any kind reaches them.

---

## §7 Out of scope, parked, and explicitly NOT ruled out

- **The MB release dump union pass** — release groups with no tags whose individual releases
  carry some. Measured at ~1.2 h of compute; the file has been deleted and would need
  re-downloading. **Condition: if and only if `REL-1` lands in 45.0–49.9%** (§5's near-miss
  band). Not otherwise — below 45% the gap is too wide for a 13.5%-fill source to close, and
  at or above 50% the bar is already cleared.
- **Wikidata P136 expansion via release links** — untouched, unproposed.
- **Merging any Discogs vocabulary into the `TAS-` frame** — a §8 amendment there, the owner's
  trigger, and `F4`'s 15-value genre list would badly inflate any agreement statistic
  (nearly every guitar band agrees on "Rock"). `F5`'s styles are the comparable-granularity
  layer if that decision is ever taken.
- **Any rebuild, any selection-rule change, any router change.** `TAS-`'s architecture
  question is untouched by this document.
- **Name-based Discogs matching** — explicitly rejected, not deferred. It is the
  population-mismatch trap that killed every external popularity source, and the MB `url-rels`
  route makes it unnecessary.

---

## §8 Amendments — append-only

*(Any amendment appended after a result exists says so at its head and names the hazard, per
`TAS-AM3`.)*

### `REL-AM1` — `REL-7` compared two different things, and `REL-C1`'s tolerance inherited the error

**⚠ APPENDED AFTER A RESULT EXISTED.** `REL-7`'s first figure (11.73%) had been produced when
this was written. The hazard is the one `TAS-AM3` names: an amendment written with a number in
view can be shaped by that number, and the reader cannot tell from the text alone. Read it
knowing that. What limits the damage here is that the defect is a **conflation of two sources**,
visible from the code without reference to any outcome, and that **no criterion bar moves**.

**What was wrong.** §2 specifies `REL-7` as the dump's artist-level tags/genres *against the
committed `tas_tags` LB frame*, to separate snapshot drift from findings. The implementation
compared the dump's `genres` against **`F0`** — which is LB genres **∪ Wikidata P136**. Those
two differ by an entire source, so the measured 11.73% is dominated by P136's contribution and
is close to silent about drift. The per-band pattern shows it: the dump's genres were a subset
of `F0` in **100.0%** of artists labelled by both, in every band, which is what you would see
if the difference were *additive source coverage* rather than disagreement.

**Why it is not cosmetic.** `REL-C1`'s pass tolerance **is** this figure. At 11.73% the
liveness check would admit a pipeline that mislabelled one artist in nine — it could not go
red, which is the entire property an instrument check exists to have.

**The correction.** `REL-7` compares the dump's `genres` against the **LB genre half of the
frame alone** — like with like, the same quantity `COH-5` measured at n = 872. The Wikidata
P136 contribution is reported beside it as its own descriptive column, because it is worth
knowing and is **not** drift.

**Scope: `REL-7`'s statistic and `REL-C1`'s tolerance, and nothing else.** `REL-1`'s 50% bar,
`REL-3`'s null-relative bars, `REL-6`'s adverse condition, the §1 validity filter and the §5
read table are all untouched, and none of them had produced a figure when this was written.
