# The un-listenable class (`ULC-`) — pre-registration

**Role: GOVERNING for this track.** Written and committed **before any count exists**. Where a
later plan, script or note disagrees with this document, **this governs**. Status and sequencing
live in [`NEXT.md`](../NEXT.md); this document owns no status.

**Origin.** The owner chose §4 **option B** of
[`findings/2026-08-05-coherence-audit-results.md`](../findings/2026-08-05-coherence-audit-results.md)
on 2026-08-05, scoped **across both archives**, with the `BYP-13` keep-check half deferred to a
follow-on track. That findings note's §6 already sharpened the question, and this document adopts
its framing rather than restating it.

**It owns no figures.** `CAU-` figures stay in the findings note; `CRE-` figures in
`findings/2026-08-04-cap-reevaluation-results.md`; drop-list sizes in the census JSONs under
`builder/analysis/`. Cited, never restated.

---

## §0 Factor table, and what is held constant

### 0.1 The populations

Five node sets. The first four form the factor table; the fifth is a reference row that is
**not** part of any one-knob comparison and is explained in §0.3.

| id | artifact | archive | supply rule | drop flags | isolating baseline |
|---|---|---|---|---|---|
| **`ULC-P1`** | `builder/scratch/cre-cells/E-S0.bin` | `ALG-E` | S0 (production: mutual k-NN, k = 50) | both on | — (baseline of `P2`) |
| **`ULC-P2`** | `builder/scratch/cre-cells/B-S0.bin` | `ALG-B` | S0 | both on | **`P1`** — differs by archive alone |
| **`ULC-P3`** | `builder/scratch/cre-cells/E-S1.bin` | `ALG-E` | S1 (trimmed union) | both on | — (baseline of `P4`) |
| **`ULC-P4`** | `builder/scratch/cre-cells/B-S1.bin` | `ALG-B` | S1 | both on | **`P3`** — differs by archive alone |
| **`ULC-P5`** | `builder/scratch/graph-t15-tiebreakfix.bin` | `ALG-E` | S0 | **NEITHER** | **none — see §0.3** |

Every artifact is verified against its manifest sidecar (`*.bin.json`) before it is read; `P5`
against the sha256 in `findings/2026-07-23-tiebreak-fix-adoption.md`. A population whose
checksum does not match is a hard stop, not a warning.

**Why `P4` and not the production artifact is the `ALG-B` comparator.** `P4` is the graph the
`GBL-` listen ran on (its **G** arm) and the graph `CAU-` audited. The evidence that raised this
question is about that node set.

### 0.2 The one-knob comparisons this table licenses

- **`P2` − `P1`** — the archive switch under the production supply rule.
- **`P4` − `P3`** — the archive switch under the trimmed-union supply rule.

**Nothing else.** In particular `P4` − `P1` differs by two knobs (archive **and** supply rule)
and no read in this track may use it, notwithstanding that those two cells are the ones the
listen compared.

### 0.3 `ULC-P5` has no baseline, and that is the point

**The artifact the app serves today has neither drop filter applied.** `graph-t15-tiebreakfix.bin`
predates the drop wiring and no production rebuild has happened
(`2026-08-04-gbl-planning-execution-log.md` §3). So it differs from `P1` by archive-identical data
but *no cleanup at all*, and it is not comparable to any cell in the table.

It is measured anyway, and reported alone, because **it is the only population any user has ever
seen.** A number about `P1` describes a graph that has never shipped. Any sentence about "the app
today" must cite `P5`; any sentence about the archive switch must cite `P2` − `P1` or `P4` − `P3`.
**Mixing those two jobs in one sentence is barred (`ULC-B4`).**

### 0.4 Held constant, and why each is genuinely constant under the archive switch

| Held constant | Why the intervention cannot change it |
|---|---|
| The MusicBrainz dump snapshot | One local dump pass covers the **union** of all five node sets in a single read. Every population is scored against literally the same bytes. |
| The class predicate | Fixed in §1 before any count exists, and applied identically to all five. It is a property of an *artist*, not of a graph. |
| The credit extraction code | Imported from `fcf_census`, never reimplemented (§1.4). Two readers would be two chances to disagree — the rule `ctc_census` already states for itself. |
| Journey generation (`ULC-S2` only) | The `CRE-G1`(a)-verified mirror, the same instrument `GBL-` and `CAU-` used, on all arms. |

**One thing that is NOT constant, and must never be described as constant.** The two drop
**rules** are held constant; their **outputs are not, and cannot be.** A drop list is the rule
evaluated against a specific crawl, so each population has its own
(`no_release_drop.py:9-21`). The two censused lists share only a minority of their MBIDs. So a
difference in residual class size between `P1` and `P2` is **partly a difference in what the
cleanup already removed**, and this document may not attribute it to the archive alone.

**This is the dormant-term check, and it fires.** The class is *defined* as what both filters
leave behind, so the filters are not a background condition here — they are inside the
measurement. `ULC-C1` therefore reports the residual class **and** the two dropped sets, per
population, so a reader can see all three and this document cannot quietly bank the difference.

---

## §1 The class, fixed before any count exists

### 1.1 The owner's definition governs, and it is not "a clip resolves"

Recorded in the findings note §6, in his words and his column:

> the point is finding novel artists that cohere with what you already like … the failure is not
> *"no clip resolves"* but *"there is nothing to go and listen to"*.

**Keith Scott is the worked counterexample and travels with every use of this definition:** the
owner found him on YouTube only, and judged him FITS twice. **A predicate requiring a commercial
clip would drop a card he liked.** No stage of this track resolves a clip, touches the network,
or takes a snapshot.

### 1.2 The gap both filters leave

- `drop_no_release_tail` fires only at **zero** release-group credits.
- `drop_featured_credit` fires only when **none** of an artist's credits are sole.

**One sole credit exempts an artist from both.** The class is what sits in that gap.

### 1.3 `ULC-C1` — the measured quantity, and it is a distribution, not a threshold

> **Plain-language sentence, fixed here:** *`ULC-C1` — of all the artists on the map, how many
> have put out almost nothing of their own, even though our two cleanup rules both let them
> through?*

For every artist in the union of the five node sets, record:

| field | source | verified present |
|---|---|---|
| `rg_total` | MB release-group dump — credits of any shape | yes (`fcf_census` records it today) |
| `rg_sole` | credits where the artist is the **only** credited artist | yes |
| `rg_sole_primary` | of those, `primary-type` ∈ {Album, EP, Single} **and** `secondary-types` empty | yes — both fields confirmed present in the dump |
| `rg_sole_secondary_kinds` | the secondary types seen on sole credits (Compilation, Live, Soundtrack, DJ-mix, Remix…) | yes |
| `has_dsp_link` | MB artist dump, commercial-DSP relation | yes (`ctc_census` extracts it) |
| `has_discogs` | MB artist dump, Discogs relation | yes |

**`ULC-C1` is the joint distribution of `rg_sole_primary` × `rg_sole` per population, reported as
rates over that population's node count — never as raw counts** (`ULC-B1`). **No threshold is set
and none may be inferred from this document.** The output is a table a reader can cut anywhere.

**This is deliberate and it is the owner's instinct, adopted.** A census here sets no bar — the
established precedent is `ctc_census.py` and `fcf_census.py`, both of which open *"DIAGNOSTIC
ONLY. Adopts nothing, fixes no criterion, sets no bar."* This one says the same.

### 1.4 What is reused rather than rewritten

Credit-shape extraction and the artist-dump pass come from
`builder/analysis/2026-08-03-featured-credit-filter/fcf_census.py`; population loading and
manifest verification from `cb_metrics`. Both are frozen probe code and are imported, not copied.

**Not verified and therefore not promised:** recording- or track-level counts ("how many songs").
The local `release-group` dump does not carry them. If a later stage wants that depth it must
first confirm the `release` dump carries track counts; **no read in this document depends on it.**

### 1.5 The validation set — 11 artists, not 23, and why

**The findings note's §6 reports "22 of 23 never evaluated by either rule". That denominator
includes the audit's own 12 planted controls, and it should not.** Recomputed from
`cau_judgements.json` × `cau_page_data.json` × the sealed injection file, against the same two
committed lists §6 used:

| Set | Artists | Never evaluated | In class, kept |
|---|---|---|---|
| All bad-or-unjudgeable verdicts (as §6 counted) | 23 | 22 | 1 |
| — of which **planted controls** | 12 | 12 | 0 |
| — of which **real artists** | **11** | **10** | **1** (Pino Palladino) |

The 12 controls were **injected by the harness**, not delivered by routing, so asking whether a
build-time filter evaluated them is meaningless — all 12 are trivially "never evaluated" and they
more than double the denominator. **§6's direction survives intact (10 of 11 is the same finding
at essentially the same rate); its evidence base is half the size it appears.** Correction owed
to the findings note — see `ULC-AM0` in §7.

**The 11 are a validation set, not a training set** (§2), and they are heterogeneous: some are
un-listenable (session players, a producer), others are perfectly listenable artists that simply
did not fit (Billie Joe Armstrong, Four Tet). The findings note reports that **eight of the nine
CAN'T TELL judgements** record the "nothing to listen to" cause — **7 distinct artists**. So:

| `ULC-V1` | the 7 distinct artists behind a CAN'T TELL verdict — **the target class** |
|---|---|
| **`ULC-V2`** | all 11 real artists behind any bad-or-unjudgeable verdict — the wider set |

**Seven artists is a thin validation set and this document does not pretend otherwise.** It is
enough to falsify a predicate, not enough to fit one — which is exactly why §2 fixes the
predicate from the definition instead.

> **Post-result disclosure, in the style this project already uses (`FCF-AM1`, `NOV-AM1`).**
> Before writing §2's predicate I had read one fact about one validation artist: findings §6
> states Brad Delson has *"one release with one song in MusicBrainz."* No other credit-shape fact
> about any of the 11 was known, and no distribution had been computed. Recorded so a reader can
> discount §2's predicate by exactly that much.

---

## §2 `ULC-G1` — is the class separable offline at all?

> **Plain-language sentence, fixed here:** *`ULC-G1` — using only what we can look up offline,
> can we actually pick out the artists you couldn't listen to, without also flagging huge numbers
> of ordinary artists?*

**Evaluated first and alone, before any cross-archive read.**

### 2.1 The predicate comes from the definition, not from the cases

**`ULC-D0`, fixed here and committed before any count exists:**

> An artist is in the candidate class when **`rg_sole_primary == 0`** — they are the sole credited
> artist on **no** release group whose `primary-type` is Album, EP or Single with no secondary
> type. Everything they appear on is either shared, or a compilation / live / soundtrack /
> DJ-mix / remix.

**This is derived from §1.1's definition — "there is nothing to go and listen to" — and from
§1.2's gap, not from looking at the 11.** No cut was searched, no distribution consulted. The
only leakage is the single Brad Delson fact disclosed in §1.5.

**Why this matters more than the tidiness of it.** A predicate fitted to seven artists would
capture them by construction and teach us nothing; a predicate fixed in advance can **fail**, and
`ULC-V1` is then a genuine test of it. That converts the thin validation set from a weakness into
the strongest thing available. Two further cuts, `rg_sole_primary ≤ 1` and `≤ 2`, are reported as
a **sensitivity ladder** — reported, never selected from after the fact (`ULC-B8`).

### 2.2 The branches

| Branch | Trigger | Consequence |
|---|---|---|
| **`separable`** | `ULC-D0` captures **≥ 5 of the 7** `ULC-V1` artists **and** selects **≤ 20 %** of `P4`'s nodes | Proceed to `ULC-S2`. |
| **`predicate_wrong`** | Captures **≤ 4 of 7**, at any selectivity | **STOP.** Credit shape does not identify what the owner could not listen to. The track closes with `ULC-R0`. **No second predicate is fitted and tried** — that is the fishing this design exists to prevent; a new predicate is a new pre-registration. |
| **`too_broad`** | Captures ≥ 5 of 7 but selects **> 20 %** of nodes | **STOP.** The signal is real but unusably coarse: acting on it would be a purge, not a filter. Reported as such, not as a pass. |

**Why 5 of 7 and why 20 %, both fixed before any count.** Five of seven is a clear majority of the
target set — with seven cases there is no threshold that is both meaningful and finely graded, and
this document says so rather than implying a precision it does not have. Twenty percent is roughly
twice the share the existing no-release cleanup already removes, so above it the predicate is
describing the general population rather than a tail. **Both are gate triggers carrying their own
effect size, per `CLAUDE.md`'s rule that a gate without one fires the expensive response on
noise — the rule written after a `Track 2` gate fired on a single cell.**

**Two of the three branches stop the track, and that is deliberate.** `predicate_wrong` and
`too_broad` are real, valuable outcomes: they say the coherence problem `CAU-` found cannot be
fixed by a build-time filter of this shape, which redirects effort rather than wasting it.

### 2.2a `predicate_wrong` is anticipated, and this is recorded before the run

**Stated here so that, if it fires, it is visibly not a post-hoc excuse.** Two facts already in
the record point at it: findings §6 says Brad Delson — a target-class member — has *"one release
with one song in MusicBrainz"*, and `ULC-AM1` records that Keith Scott — a member of the class we
must **not** flag — has one sole primary release, a 1993 single.

**If Delson's single release is sole-credited and of primary type, `ULC-D0` misses him and Keith
Scott is spared by the same rule for the same reason.** The two would then be indistinguishable
by credit count, and the broader rungs of the sensitivity ladder (`≤ 1`, `≤ 2`) catch both or
neither. **That is the shape of a `predicate_wrong` result**, and its meaning would be specific
and useful: what separates these two artists is whether the owner could actually find something
to play, which is availability rather than credit shape — and no offline credit signal encodes
it. `ULC-D1` is the one lever that could still separate them, since Delson and Scott differ
sharply in supporting-credit footprint; **it is secondary and cannot rescue the gate**
(`ULC-AM1`(b)).

### 2.3 `ULC-V2` is reported, never used as a trigger

Capture over all 11 is reported alongside. **It fires nothing** — the wider set mixes the target
class with ordinary stylistic misfits (Billie Joe Armstrong, Four Tet), and a predicate that
captured *those* would be a worse predicate, not a better one. Recorded here so that a reader
cannot later read a high `ULC-V2` capture as success.

---

## §3 `ULC-S2` — interior exposure

> **Plain-language sentence, fixed here:** *`ULC-S2` — when you actually build a journey, how
> often does one of these artists turn up in the middle of it?*

Runs only on `ULC-G1` = `separable`. A node set can contain a class that routing never surfaces;
exposure is the quantity that makes the census actionable, and `ULC-C1` alone cannot produce it.

**Arms**, generated by the `CRE-G1`(a)-verified mirror on the eight `GBL-AM1` pairs at d0 / d10 /
d20:

| arm | population | ramp | isolating baseline |
|---|---|---|---|
| **`ULC-A1`** | `P1` | none | — |
| **`ULC-A2`** | `P2` | none | `A1` — archive alone |
| **`ULC-A3`** | `P3` | gentle — `RAMPS["P1a"]`, cited never restated | — |
| **`ULC-A4`** | `P4` | gentle — `RAMPS["P1a"]`, cited never restated | `A3` — archive alone |

`ULC-C2` is the **share of interior cards falling in `ULC-D0`**, per arm per depth,
paired by pair. Endpoints are excluded — the owner picks those.

### 3.1 `ULC-R1` — the archive read, and its effect size

> **Plain-language sentence:** *`ULC-R1` — does switching to the new map put more of these
> artists in the middle of your journeys, fewer, or about the same?*

Fires on **`A2` − `A1`** and **`A4` − `A3`** independently:

| Branch | Trigger |
|---|---|
| **`worse_on_candidate`** | Paired median difference **≥ +2 percentage points** and its 95 % percentile-bootstrap CI excludes zero |
| **`better_on_candidate`** | **≤ −2 pp** and CI excludes zero |
| **`no_detectable_difference`** | Anything else — **including a CI excluding zero on a difference smaller than 2 pp** |

**Why 2 pp, fixed before any count.** A journey presents roughly a dozen interior cards, so 2 pp
is about one extra un-listenable card every four journeys — the smallest difference that would
change what the owner experiences. Below it, the difference is real-but-irrelevant, and this
document says so in advance rather than discovering it convenient later.

**If the two comparisons disagree, both are reported and neither is averaged** — they are
different supply rules, and an averaged number describes no graph that exists.

### 3.2 The depth confound, named because it is now known

**A fixed press count is not a matched comparison between two graphs.** The owner parked this on
2026-08-05 (`NEXT.md`): if one graph reaches novelty faster, the same number of presses sits at a
different position on each graph's own curve. `d10` on `P4` may be further along its journey than
`d10` on `P3`.

**This is an uncontrolled variable in `ULC-R1` and it cannot be controlled away here** — no curve
has been measured for either graph, and measuring one is a different track. It is declared rather
than fixed: **every `ULC-R1` sentence carries it**, and a `worse_on_candidate` result is
consistent with "the candidate graph surfaces this class more" *and* with "the candidate graph is
simply deeper at the same press count."

---

## §4 Reads, and the run state each presupposes

| Read | Fires when | Run state it presupposes |
|---|---|---|
| **`ULC-R0`** — *the class is not offline-detectable by credit shape; a build-time filter of this shape cannot fix it* | `ULC-G1` = `predicate_wrong` **or** `too_broad` — and the two are reported as different results, never merged | All 11 `ULC-V2` artists recovered and all 7 `ULC-V1` scored against `ULC-D0` on `P4`. **`P1`, `P2`, `P3`, `P5` need not be counted.** |
| **`ULC-R1`** — the archive read (§3.1) | `ULC-G1` = `separable` and **all four arms generated at all three depths on all eight pairs** | 96 arm-pair-depth slots present. **A read taken on three arms is not `ULC-R1`** and may not be reported as one. |
| **`ULC-R2`** — *the shipped app carries the class at a rate no cell in the table describes* | Always computed | `P5` counted. **Requires no other population** and is reported alone (§0.3). |
| **`ULC-R3`** — *the cleanup already removes most of this class; the gap is narrow* | `ULC-C1`'s residual is smaller than either dropped set on the same population | Both dropped sets loaded per population from their committed lists. |

**`ULC-R2` is expected to be the most actionable read and is available earliest.** It is the only
one about software anybody is running.

---

## §5 Barred reads

Each travels with every sentence this track produces.

- **`ULC-B1`** — **No raw-count comparison across populations.** The node sets differ in size.
  Rates only.
- **`ULC-B2`** — **Nothing here reopens the `GBL-` null.** Its run-once rule binds. This track
  measures population and exposure; it takes no position on which package sounds better, and a
  `worse_on_candidate` result is **not** evidence against the rebuilt graph's listen.
- **`ULC-B3`** — **`ULC-D0` is not a proposed drop rule.** It is a detection predicate fixed to
  test a hypothesis. Its false-positive rate against *listenable* artists is **not measured by
  this track**: `ULC-V1` can show the predicate catches what it should, never that it spares what
  it should. A drop rule needs its own pre-registration, its own census, and `ULC-OG2`.
- **`ULC-B8`** — **The sensitivity ladder (§2.1) is reported, never selected from.** If
  `rg_sole_primary ≤ 1` or `≤ 2` captures more of `ULC-V1` than `ULC-D0` does, that is **recorded
  as a fact and changes no branch.** Choosing the best-performing cut after seeing the results is
  the fit this design exists to avoid, and it would silently convert `ULC-V1` from a test set into
  a training set.
- **`ULC-B9`** — **No sentence uses "22 of 23"** (§1.5). The corrected figures are 10 of 11 for
  never-evaluated and 7 for the target class.
- **`ULC-B4`** — **No sentence mixes `P5` with a cross-archive comparison** (§0.3).
- **`ULC-B5`** — **No causal claim that this class caused `CAU-`'s verdicts.** `CAU-` judged 53
  cards; this counts artists. The overlap is the calibration set and it is 23 people.
- **`ULC-B6`** — **`P4` − `P1` is a two-knob comparison and licenses nothing** (§0.2).
- **`ULC-B7`** — **Nothing here adopts anything, changes any default, or touches shipped code.**
  Any rule that follows is a separate track with the owner's ruling.

---

## §6 Owner gates

- **`ULC-OG1` — the definition in §1.1 is his.** It is quoted from his own correction and pinned
  with the Keith Scott counterexample. **If he wants "there is nothing to go and listen to" drawn
  differently, it must move before `ULC-G1` runs**, because `ULC-D0` is derived from it and the
  gate tests that derivation. After that the document is frozen and a change is an amendment.
- **`ULC-OG2` — where to cut, if a rule is ever written, is his** and is out of scope here
  (`ULC-B3`).

No other gate. Everything else in this document — populations, arms, effect sizes, run counts,
what to measure and in what order — is methodology, and is mine.

---

## §7 Amendment record

Amendments are `ULC-AM1`, `ULC-AM2`, … appended here, each committed **before** the stage it
affects runs, with the reason and what it does not change. **Forward-only: nothing above is
renamed or renumbered.**

> **Read `ULC-AM1` and `ULC-A1` carefully — they are different objects.** `ULC-AM<n>` is an
> amendment (this section); `ULC-A<n>` is a Stage-2 arm (§3). They are distinct tokens and so
> not a collision under `CLAUDE.md`'s rule, but they are visually adjacent, and Track 2's
> eleven-collision mess was this shape. Flagged rather than renamed: renaming a committed
> identifier is barred, and the whole value of a frozen document is that it is frozen.

### `ULC-AM5` — `ULC-R1` pools the two deep rows; `d0` is an anchor, excluded

**Committed before `ULC-S2` runs.** §3.1 fixes `ULC-R1`'s trigger as a "paired median
difference" but never says **over which depths** — an underspecification found while building the
harness, and resolvable only before results exist.

> **`ULC-R1`'s primary read is the pooled deep rows — `d10` and `d20`, 8 pairs × 2 depths = 16
> paired observations per comparison.** `d0` is reported as an anchor and is **excluded from the
> primary read.**

**Why this and not the alternatives.** Evaluating all three depths separately would be three
reads where the design fixed one, and multiplying comparisons after the fact is the thing
pre-registration exists to stop. Pooling all three would let `d0` — the journey before any button
is pressed — dominate a question that is about what **bypassing** surfaces. **This is exactly
`GBL-`'s shape**, whose primary read was its 16 deep rows with `d0` as an excluded anchor, and
reusing it means the two tracks' numbers sit in the same frame.

**`d0` is still worth reporting and may still be quoted**, with its own figure and no branch
attached: it is what a user sees on first load, and `ULC-R2`-style sentences about the shipped app
live there.

**Effect size and branches are unchanged** — ±2 percentage points, CI excluding zero, per §3.1.

**A limitation this makes visible: 16 paired observations is a small sample and the confidence
interval will be wide.** That is a property of the eight-pair set inherited from `GBL-AM1`, not a
choice made here, and it is a reason a `no_detectable_difference` result would be weak evidence of
equivalence rather than strong evidence of sameness. §3.2's depth confound applies on top.

### `ULC-AM4` — `ULC-V1` is 6, not 7; the trigger's absolute count is held at 5

**Committed before any stage runs**, from the owner's own committed notes.

§1.5 built `ULC-V1` as "the 7 distinct artists behind a CAN'T TELL verdict", inferring the target
class from the findings note's statement that **eight of the nine** can't-tells record the
"nothing to listen to" cause. Reading the notes themselves resolves which one is the ninth:

| artist | the owner's note, verbatim-in-substance | target class? |
|---|---|---|
| Rick Davies | *"could not find his solo work anywhere I could listen"* | yes |
| John McVie | *"No solo releases"* | yes |
| Joey Kramer | *"Aerosmith drummer, but I can't find any solo work"* | yes |
| Dallas Taylor ×2 | *"I don't see any releases for this artist. I'm surprised they weren't dropped by one of our filters."* | yes |
| Brad Delson ×2 | *"one release with one song on MB, and I can't find it anywhere"* | yes |
| Max Martin | *"the only solo work I could find is the musical & Juliet"* | yes |
| **Four Tet** | *"I did look up the artist on MB and read the bio. I wasn't sure I had the right one"* | **NO — an identity doubt, not an availability one** |

**`ULC-V1` is therefore the 6 artists above and excludes Four Tet.** He is a working electronic
producer with a large catalogue; a predicate that flagged him would be wrong. He remains in
`ULC-V2`, which is reported and triggers nothing (§2.3).

**The trigger stays at ≥ 5 — the absolute count is held, not rescaled.** This amendment removes an
artist the predicate could never have caught, which strictly helps it, so rescaling the bar to
keep the *rate* at 5-of-7 (≈ 71 %) would be loosening it under cover of a correction. Holding the
count makes the bar **5 of 6 ≈ 83 %, stricter than it was**, and that is the intended direction:
it cannot be read as goalpost-moving in the predicate's favour. §2.2's `too_broad` and
`predicate_wrong` branches are otherwise unchanged.

**One thing the owner noticed during the audit that the census will now answer.** His Dallas
Taylor note — *"I don't see any releases for this artist. I'm surprised they weren't dropped by
one of our filters"* — is the filter gap being spotted live, at the card. If Taylor truly has no
releases, `drop_no_release_tail` should have caught him; that it did not suggests he carries
release-**group** credits without releases, which is exactly the distinction `ULC-D2`'s track-count
join makes visible. **Reported when the census runs; no bar attaches to it.**

### `ULC-AM3` — `ULC-OG3` is ruled: substance is counted in tracks, and `ULC-D2` supersedes `ULC-D0` as primary

**Committed before any stage runs.** The owner ruled on `ULC-OG3`, 2026-08-05: **count songs, not
releases.**

> **`ULC-D2`** — an artist is in the candidate class when they are the sole credited artist on
> **no** release group that is **both** (a) `primary-type` ∈ {Album, EP, Single} with no secondary
> types, **and** (b) carries at least one release whose total track count across all media is
> **≥ 2**.
>
> **Plain-language sentence, fixed here:** *`ULC-D2` — this artist has never put out anything of
> their own that is more than a single track.*

**`ULC-G1` now evaluates `ULC-D2`.** `ULC-D0` is **not renamed and not deleted** — it is retained
as a reported rung of the sensitivity ladder (§2.1), which now reads: `ULC-D2` (primary),
`ULC-D0`, `rg_sole_primary ≤ 1`, `≤ 2`. **`ULC-B8` applies to all four**: reported, never selected
from after the fact. Everything else in §2.2 — the 5-of-7 and 20 % triggers, the three branches —
is **unchanged and still binding.**

**Why this and not the other two options**, in his own reasoning: what changed his assessment of
Keith Scott was learning the release was a single track, not learning it was a single release.
Counting releases would either spare both worked artists or sweep in every one-album act;
counting tracks separates a one-episode TV theme from a real record, which is the distinction the
definition is about.

**Verified buildable before the question was put:** the release dump carries
`media[].track-count` and a `release-group` reference, so the join is available offline. Cost is
one extra dump pass.

#### Two executor-column decisions this forces, fixed here rather than at run time

1. **A release group's track count is the MAXIMUM total across its releases.** A one-track promo
   sitting in the same release group as a twelve-track album does not make the album
   insubstantial. This is a data-completeness reading, not a leniency judgement.
2. **A release group with no release in the dump has an UNKNOWN track count, and unknown is
   treated as NOT substantial** — i.e. it does not rescue an artist from `ULC-D2`.

   > **This is where two of the owner's own statements pull in opposite directions, and it is
   > named rather than silently resolved.** His asymmetry ruling (`ULC-AM2`(d)) says a false
   > negative costs more than a false positive, which argues for treating unknown as
   > insubstantial. His first correction (`ULC-AM2`(b1)) says MusicBrainz incompleteness is common
   > and must not be read as absence, which argues the opposite.
   >
   > **Resolved by measuring the ambiguity rather than by adjudicating it:** the primary reading
   > follows the explicit asymmetry ruling, the opposite reading is reported alongside, and
   > **the count of affected artists is reported in both.** If that count is small the question is
   > moot and no adjudication was ever needed; if it is large, the owner has the figure and the
   > decision is his, with `ULC-B8` barring me from picking the flattering one.

### `ULC-AM2` — `ULC-OG1` is ruled, and the worked example is no longer a clean counterexample

**Committed before any stage runs.** The owner ruled on `ULC-OG1` on 2026-08-05 and supplied four
corrections, two of them to his own earlier account.

#### (a) The ruling

**The definition in §1.1 STANDS: *"there is nothing to go and listen to."*** Unchanged, and now
frozen — a further change is an amendment, not an edit.

#### (b) What he corrected, and what each one does

1. **Missing streaming links in MusicBrainz are common and do not mean the artist is absent from
   the platform.** His earlier manual exercises were spot checks of *Spotify monthly listeners*,
   so non-Spotify links were not being attended to. **Consequence: this strengthens §1.1's move
   away from DSP-link tests** — the signal is not merely wrong for Keith Scott, it is
   systematically unreliable. No change to `ULC-D0`, which never used it.
2. **Keith Scott's sole release is one track, and it is a theme from a single episode of a TV
   show.** He had read it as an album while working quickly. **His revised assessment: Scott is
   "much closer to *there is nothing to go and listen to*" than he first thought** — and he
   explicitly declines to rush a rule change on it.
3. **MusicBrainz carries data at RELEASE level that the release-group level does not.** Scott's
   release page holds a YouTube link to the track. Precedent from this project's own tag work:
   releases often carried genre tags where the artist carried none. **Recorded as a candidate
   instrument (§8), not adopted** — he notes it may be expensive.
4. **Brad Delson's single MusicBrainz entry is a live cover of a Britney Spears song, performed
   during a speech at a UCLA graduation**; the owner had previously failed to find it only because
   he searched the wrong title. ListenBrainz records **one play by one listener**.

#### (c) The consequence, and it supersedes §2.2a's *reasoning* while leaving its branch intact

**§2.2a predicted that `ULC-D0` would miss Delson and spare Scott, and read that as evidence that
availability rather than credit shape is the discriminator. That reading is now wrong**, and is
superseded here rather than edited above.

Both artists have `rg_sole_primary` = 1. If the owner's revised view of Scott holds, **both belong
in the class and `ULC-D0` at `== 0` misses both** — so the failure is not that the two are
inseparable, it is that **the threshold is one rung out.** `rg_sole_primary ≤ 1` catches both.

**Availability is also refuted as the discriminator, by his own two examples.** Both men have
something playable on YouTube; neither has a body of work. **The distinction is substance, not
availability** — one TV-episode theme, one live cover at a graduation ceremony. A YouTube-presence
test would have separated neither.

**§2.2a's `predicate_wrong` branch is unchanged and still fires on its stated trigger.** Only the
interpretation attached to it is replaced.

#### (d) The owner's asymmetry ruling, recorded because it governs any future rule

> *"I think keeping Brad is a bigger 'miss' than dropping Keith."*

**Recall over precision, in his own column** — false negatives (leaving an un-listenable artist in
the graph) cost more than false positives (dropping a marginal one). **Fixed here, before any
capture rate exists**, so no later result can be read as having discovered it. It governs
`ULC-OG2` if a rule is ever written, and it is the reason the sensitivity ladder is reported at
all.

#### (e) What this leaves open — `ULC-OG3`, and it blocks `ULC-G1`

**Does one single, one-off or one-track release count as "something to go and listen to"?** It is
his because it is the definition's own boundary, it decides Scott and Delson together, and it
selects which rung of the ladder is `ULC-D0`. **Nothing is run until it is answered**, because
answering it after the distribution is visible would let selectivity masquerade as definition.

### `ULC-AM1` — the Keith Scott pre-run check, and a precision companion `ULC-D1`

**Committed before any stage runs.** Prompted by the owner on 2026-08-05: he clarified that he
cited YouTube for Keith Scott because the music is not on Spotify or other major streaming
services, **not** because there is no release — and asked for the filter criteria to be checked
against that case.

#### (a) Pre-run disclosure — `ULC-D0` was tested against one artist before the run

Looked up in the local MusicBrainz dumps (offline, read-only), artist
`bc4db91e-3fbf-460d-99dc-4eaca2872b44`:

| field | value |
|---|---|
| `rg_total` | 1 |
| `rg_sole` | 1 |
| `rg_sole_primary` | **1** — *Gallery of Dreams*, Single, 1993-10-04 |

**`ULC-D0` does not flag him.** The owner's understanding of the criteria is correct, and the
worked counterexample behaves as §1.1 requires: a predicate built on *streaming presence* would
have gone against him (his only DSP-ish link is Discogs), and one built on *credit shape* clears
him.

> **This is a disclosure, not a result.** `ULC-B3` says this track does not measure the
> false-positive side. It now has **exactly one** pre-run data point on it, and one artist is not
> a rate. **It may not be reported as evidence that `ULC-D0` is precise.** Recorded because it was
> seen before the run and would otherwise be invisible leakage.

**Noted and deliberately not acted on:** his one sole primary release is a single from 1993, which
is a thin body of work. `ULC-D0` spares him anyway, and the owner judged him FITS twice — so the
predicate agrees with the person it exists to serve. **No threshold is added to chase this.**

#### (b) `ULC-D1` — a precision companion, secondary and declared

> **Plain-language sentence, fixed here:** *`ULC-D1` — of the artists we flagged as having
> nothing of their own, which ones also show a heavy footprint as somebody else's sideman?*

The artist dump carries relationship data at usable scale — Keith Scott's record shows
`instrument` × 234, `vocal` × 21, `performer` × 9, `member of band` × 3.

> **`ULC-D1`** = `ULC-D0` **AND** at least one relation of type `member of band`,
> `instrumental supporting musician`, `instrument`, `vocal` or `performer`.

**`ULC-D1` is a strict subset of `ULC-D0` by construction**, so it competes with nothing: it
cannot change `ULC-G1`'s branch, and the gate is evaluated on `ULC-D0` alone exactly as §2.2
already fixes. It is reported as *"of those `ULC-D0` flags, how many also look like a sideman."*

**Why it is worth carrying.** It addresses the owner's stated residual risk — poor MusicBrainz
coverage flagging artists who should stay — by identifying the class **positively** instead of
inferring it from absence. An under-documented solo artist has few sole releases *and* few
supporting credits, so `ULC-D1` spares them; a session player has few sole releases *and* a heavy
supporting footprint, so `ULC-D1` keeps them flagged. That is precisely the distinction absence
alone cannot draw.

> **Leakage disclosed, and it is the reason `ULC-D1` is secondary rather than primary.** This
> predicate was designed **after** seeing the validation-set names, most of whom are visibly band
> members or session players, and after seeing Keith Scott's relation counts. `ULC-D0` was fixed
> with materially less knowledge. **`ULC-D0` therefore remains primary and owns the gate**, and
> `ULC-B8`'s bar on choosing the better-performing cut after the fact **applies to `ULC-D1` in
> full.**

**A known weakness, named now rather than discovered later:** MusicBrainz relationship coverage is
itself patchy, so `ULC-D1` may simply inherit the coverage problem it was designed to mitigate.
Its own miss rate is unmeasured, and this track will not measure it.

### `ULC-AM0` — a correction owed to `findings/2026-08-05-coherence-audit-results.md` §6

**Not an amendment to this document** — it is numbered `AM0` because it predates this track's
first stage and is recorded here so the finding is not lost if this track closes early. **It is
the findings note's to carry, not this one's**; that note owns the `CAU-` figures and a correction
belongs in it, appended, so its revision boundary holds exactly as §6 and §7 were appended.

**What is wrong.** §6's *"22 of 23 never evaluated by either rule"* includes the audit's own 12
planted controls in the denominator. They were injected by the harness rather than delivered by
routing, so filter coverage over them is not a meaningful question, and all 12 are trivially
"never evaluated".

**What is right.** **10 of 11** real artists behind a bad-or-unjudgeable verdict were never
evaluated; 1 (Pino Palladino) was in the featured-credit class and kept; 0 were in either drop
list. Reproducible from `cau_judgements.json` × `cau_page_data.json` × `.superpowers/cau/
cau_sealed.json` against `fcf_droplist_algb_am1.json` and `ctc_droplist.json`.

**What does not change.** §6's conclusion — *"the class the audit found was not admitted by a
filter making a bad call — it was never looked at"* — **stands**, at 90.9 % rather than 95.7 %.
No `CAU-` criterion, gate or branch is touched: `CAU-C1`, `CAU-C2`, `CAU-C3` and `CAU-G1` are all
computed by `cau_score.py` over `D_all`, which excludes controls and control-adjacent slots
correctly (`cau_score.py:62-68`). **The defect is confined to §6's ad-hoc check**, which applied
neither exclusion.

**Why it is worth recording rather than quietly fixing.** It is the third instance of the pattern
that same note names in its §7 — *"a cost declared three times in three places, and never once
summed"*. `CAU-AM3`'s control exclusion was declared, implemented in the scorer, and then not
applied by a check written in the same document.

---

## §8 Out of scope, named rather than waved at

- **The `BYP-13` keep-check defect** — that the featured-credit keep-check resolves clips by
  name, with about half its keeps unverifiable (findings §6). **Deferred to its own track by the
  owner, 2026-08-05.** It is a fix, not a measurement, and running it inside this track would move
  the population mid-count. Its effect here is a **named limitation**: both committed keep lists
  contain unverified name-path resolutions, identically on both archives — so it bounds absolute
  claims and does **not** confound `ULC-R1`.
- **Recording- or track-level depth** (§1.4) — unverified data source, no read depends on it.
  **`ULC-AM2` raises its value considerably**: both worked artists are distinguished from a real
  act by *substance* (one TV theme; one live cover), which is a track-count question. If
  `ULC-OG3` rules that a one-track release does not count, this stops being optional.
- **Descending to RELEASE level for links and data absent at release-group level** — the owner's
  observation (`ULC-AM2`(b3)), with the tag work as precedent. **A candidate instrument, not
  adopted here.** Note that it would not have separated his two worked cases: both have a
  YouTube-reachable track. Its value is elsewhere, and it needs its own scoping.
- **ListenBrainz play counts as a floor test** — *"has anyone ever listened to this at all"*,
  prompted by Delson's one play by one listener. **Not adopted, and it carries a live
  constraint:** `FAM-` measured ListenBrainz listener counts against worldly fame and they
  **failed**, and there is a standing bar on worldly-fame claims entering new criteria. A floor
  test is a materially weaker claim than the ordering claim that failed, so it is not obviously
  barred — but establishing that is its own pre-registration, not a footnote here.
- **Any drop rule, any adoption, any default change** (`ULC-B7`).
- **The crawl-expansion defects found 2026-08-05** — that resuming with a raised
  `target_artist_count` does nothing (`crawl.py:115`, the frontier is `discovered − done` and both
  are 75,000), and that both drop lists key on algorithm alone so an extended population would be
  silently un-filtered (`no_release_drop.py:30-33`). **Recorded here because this track discovered
  them and they would otherwise be lost; they are a separate track and nothing here depends on
  them.**
