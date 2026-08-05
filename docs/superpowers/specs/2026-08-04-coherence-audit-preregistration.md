# `CAU-` — coherence audit of the gentle arm's novel artists

**Role: ACTIVE (pre-registration, not yet run).** Fixes the workload, the instrument, the
red control, and the read of every possible outcome **before any judgement is recorded**.
The git commit timestamp of this file is the evidence the readings were not fitted to a
result. **This document is frozen on commit**; changes come as `CAU-AM` amendments, and
corrections that move no bar come as `CAU-CORR`, a separate series (the `GBL-CORR1`
precedent).

**Identifiers.** This document owns the `CAU-` series. Collision-checked against `docs/`,
`builder/analysis/` and `.claude/` on 2026-08-04: unused.

**Why the freeze is stricter here than usual.** The result this audit follows is already
known to everyone involved, including the listener. That is exactly when a read is easiest
to reshape without noticing, so every bar, every denominator and every branch below is
fixed now.

---

## 0. What happened before this, in one paragraph

The `GBL-` blind listen ran and returned the pre-registered null — margin 3 of 16 deep
rows against a bar of 5 (`findings/2026-08-04-gentle-arm-blind-listen-results.md`, which
owns those figures). **That null stands and this document does not touch it.** The owner
then identified a confound in the instrument, and it is the reason this audit exists: a
30-second slice of one arbitrary track cannot support a coherence judgement about an artist
the listener has never heard of. That was harmless while every interior artist was familiar,
and it stopped being harmless at exactly the point an arm began delivering unfamiliar
artists — so **the measurement degrades only in the arm that succeeds.** The owner also
recorded, unprompted, that had he read the row pick as "which do you prefer" rather than as
a coherence question he would likely have chosen the new graph more often, and that this
must not be edited in after the fact. It has not been.

## 1. The question, and the three this does not ask

**Plain sentence, fixed now:** *"When the rebuilt app hands me an artist I have never heard
of, does that artist actually belong where it was put?"*

Not asked, and **barred from every sentence of the result** (§6):

- **Which graph is better.** This is a one-arm audit. There is no comparison and no margin.
- **Whether the journeys hang together end to end.** ⚠ **The reason changed under `CAU-AM1`
  and the bar did not.** Before the amendment the whole path was genuinely invisible to the
  instrument; now the owner sees each journey complete, so he *can* form a whole-path
  impression and §7 captures it as a free-text note. **It remains unscored and unbarred: no
  criterion measures it, no threshold exists for it, and none may be invented after the
  run.** The owner's "today's app takes weird detours when you look at the whole path"
  observation is about the *other* arm and stays out of scope entirely — this audit sees only
  the rebuilt graph and can compare nothing.
- **Anything about novelty.** Settled at 8–0 by `GBL-Q1` and not re-opened. Because this
  audit sends the listener to Spotify, where monthly listeners are displayed, the spec §6
  WGLL bound is live: **any novelty observation arising during this run is void by
  construction** and may not be recorded as a finding.

## 2. Material

**Source:** the **G arm only** (`B-S1-P1a`) journeys already generated and committed for
`GBL-`, at depths **d10 and d20** across all eight approved pairs. No new journeys are
generated; no graph is rebuilt; no shipped code is touched. Raw source:
`builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_page_data.json` with the arm
identity in `gbl_result.json`.

**Population, measured before this document was committed: 54 distinct interior artists**
(endpoints excluded, deduplicated across the 16 deep journeys). Journey lengths d10/d20 run
3 to 11 cards, median 6.

**Unit of judgement: an interior slot.** ⚠ **Superseded by `CAU-AM1` (§7) before any
judgement existed** — the isolated-triple presentation fixed here could not pose the question
where several consecutive artists are novel to the listener. **Read §7 for the governing
form: whole journeys presented, every interior slot judged, 65 slots rather than 54.**
*(Original text:)* One interior artist shown with its immediate predecessor and successor
from the journey it came from, presented in shuffled order, not grouped by journey.

## 3. The instrument

⚠ **`CAU-AM3` (§7) replaced the question below with a journey-level one — "does this artist
belong on this journey?" — because an inserted control was contaminating its two real
neighbours. Read it before implementing this section.** For each interior slot the owner
records one of:

| Verdict | Meaning *(wording superseded by `CAU-AM3`)* |
|---|---|
| **FITS** | This artist belongs ~~between these two~~ **on this journey** |
| **DOESN'T FIT** | This artist does not belong ~~between these two~~ **on this journey** |
| **CAN'T TELL** | Still unable to judge after listening |

**The listening rule, and it is the point of the whole exercise.** For any artist he cannot
confidently place, he goes to Spotify (or any source he likes) and listens to **several
tracks** — as much as it takes to form a view. There is no 30-second limit and no single-track
limit. An artist he already knows is judged on sight; that is not a lesser judgement and it
is counted in the same denominator.

Free-text reason per step, optional but encouraged — the `GBL-` notes corpus was the most
operationally useful thing that listen produced.

**`CAN'T TELL` should now be rare, and its rate is itself a reading** (`CAU-C3`).

## 4. The red control — and the audit is void without it

Standing project rule: *a green result from a new instrument is not evidence until the
instrument has been shown to go red.*

**Injected steps.** ⚠ **`CAU-CORR1` (§7): "replaced by" below is wrong — an injected artist
is INSERTED between two existing cards, so all 65 real slots survive. Read it before
implementing this section.** A pre-registered number of steps carry a random artist **drawn
from the same graph**, sampled from the same obscurity band
(`fame_lb_pctl`) as the artist it replaces, so it cannot be spotted by fame alone. These
steps are indistinguishable in presentation from real ones. **`CAU-AM2` adds a hardness
condition — distance >= 3 from both displayed neighbours — without which `CAU-G1` is not a
red control; read it before implementing this section.**

- **Count: 12 injected steps**, fixed now, sealed before the run. *(`CAU-AM1`: placed into
  journeys, at most one per journey. Count and bar unchanged.)*
- The injection map is written to a **gitignored file under `.superpowers/`** before serving
  and read by nobody until every real step is judged (the `BLIND-MAPPING.json` convention).
- **`CAU-G1` (gate, and the audit's validity condition): at least 10 of the 12 injected
  steps must be judged DOESN'T FIT.** Plain sentence: *"the audit can tell a bad
  recommendation from a good one."* Below 10, **the instrument is blunt and every reading
  below is void** — reported as void, not as a weak pass, and no result sentence survives.

**The injected steps are excluded from every denominator in §5.** They test the instrument,
not the graph.

**Why this protocol is lighter than `GBL-`'s.** The only thing needing concealment is which
steps are injected. There is no arm to blind, no expectation to protect on either side, and
therefore no mechanics-only runner session is required. A sealed file is sufficient, and the
session that builds the audit may also serve it, provided it discloses nothing about the
injections.

## 5. Reads — fixed in advance, with effect sizes

**Denominators are declared here so neither can be chosen after the fact.** Both are
reported, always, side by side:

- **`D_all`** — ⚠ **`CAU-AM3` (§7) is the governing count: 53 SCORED slots.** 65 real slots
  are presented and judged; the 12 sitting next to a control are excluded. *(`CAU-AM1` said
  65; the original said all 54 real interior artists.)*
- **`D_lookup`** — only those the owner had to look up (could not place on sight).

`D_lookup` is the harder population by construction and will score worse; **reporting it
alone would be pessimistic and reporting `D_all` alone would be flattering.** Neither is
"the" number.

### `CAU-C1` — the primary outcome

**The fraction of real interior artists judged FITS, over `D_all`.**

Plain sentence: *"how often the rebuilt app's artists actually belong where it put them."*

| Outcome | Plain sentence | Action |
|---|---|---|
| **≥ 75% FITS** | "The new artists it digs up genuinely belong in the journey." | The coherence worry is answered on this evidence. The `GBL-` null is **explained** — not overturned — and adoption becomes a live decision for the owner, taken outside this document |
| **≤ 50% FITS** | "The new artists it digs up are substantially noise." | Decisive against the arm on coherence. No further listen is owed and Option A stays closed |
| **50% < FITS < 75%** | "It is a real improvement in what it finds and a real cost in what it gets wrong." | **Genuinely ambiguous, and the audit says so rather than picking a side.** The next move is the owner's and this document names no default |

**✅ RATIFIED BY THE OWNER at ≥ 75%, 2026-08-04 (night), before generation — `CAU-AM2`.**
The bar was his to set, because "how many wrong cards is too many" is a judgement about what
the app should be, not a methodological choice. *(Original text:)* it is not fixed until he
has signed off, and nothing runs before he does.

### `CAU-C2` — concentration

**The largest number of DOESN'T FIT artists falling in any single journey.**

Plain sentence: *"whether the bad ones are sprinkled about or whether some whole journeys
are wrecked."*

**Trigger: any single journey carrying ≥ 3 DOESN'T FIT artists.** This fires independently
of `CAU-C1` and is reported even when `CAU-C1` passes — a good average with one ruined
journey per eight is a different product than a good average spread thin, and a rate alone
cannot tell them apart.

### `CAU-C3` — residual unjudgeability

**The fraction of real steps still CAN'T TELL after listening properly.**

Plain sentence: *"how often even proper listening left me unable to say."*

**Expected to be near zero.** Above **15%** it is a finding in its own right: it would mean
unfamiliarity, not clip length, was the barrier, and that the whole diagnosis in §0 is
wrong. Reported prominently if it fires, because it falsifies this document's own premise.

### Run state every read presupposes

**All 65 real interior slots and all 12 injected slots judged** (`CAU-AM1`; this read
"54 real steps" before that amendment). A partial run licenses **no read**;
what is owed is named and the run resumes or is abandoned by the owner, never summarised.
`CAU-G1` is evaluated **first**; if it fails, nothing else is computed.

**Sample-size knob, fixed now because it must not be chosen later:** if the owner wants the
run smaller, he may set a target count **before generation**, and the steps are then drawn by
seeded random sample from the 54 with the seed committed. **Post-hoc exclusion of any step is
forbidden.**

## 6. Barred reads

- **No comparison with today's app**, in any sentence, at any strength. `GBL-` §5's run-once
  rule binds its verdict; this audit does not re-run it, because it measures a different
  thing (one artist's local fit, not a journey-level preference between two arms) — and it
  must not be used to smuggle a comparison back in. **The `GBL-` null stands whatever this
  finds.**
- **No whole-path or "detour" claim**, in either direction — §1.
- **No novelty claim** — §1, and the WGLL monthly-listeners bound.
- **No adoption on any outcome.** Adoption and the re-crawl remain the owner's, taken
  outside this document. A `CAU-C1` pass makes adoption *decidable*; it does not decide it.
- **No attribution** to the data set, the connection rule or the ramp individually — the
  `GBL-` §2 package-comparison constraint travels, and one arm cannot isolate anything.
- **"The coherence question is now settled" is barred even on a pass**, because the global
  defect in §1 remains unmeasured by anything.

## 7. Amendments

### `CAU-AM1` — the unit becomes the journey, not the isolated triple, 2026-08-04 (night)

**Raised by the owner before any judgement existed, before generation, and before `CAU-C1`'s
bar was ratified.** No result of any kind exists at the time of this amendment.

**The defect.** §2 fixed the unit as an isolated triple — one interior artist with its
immediate predecessor and successor, shuffled. The owner pointed out that his journeys
contain **runs of consecutive artists all novel to him**. Under the committed design such a
run produces overlapping triples sharing members, and each asks him to judge an unknown
artist against two unknown neighbours. Three consequences, none of them acceptable:

1. **The judgement asked is not the judgement needed.** With A→B→C→D→E and B, C, D all
   novel, "does C belong between B and D" cannot be answered independently — the real
   question is whether the run B,C,D is a sensible passage, and no triple asks it.
2. **The lookup cost was understated.** Context artists need looking up too, so the §5
   estimate counted targets and ignored neighbours.
3. **The steps were never independent.** 65 interior slots over 54 distinct artists, 11 of
   which recur across journeys — presenting them shuffled hid a dependence structure rather
   than removing it.

**The change.** The unit of *presentation* becomes the **whole journey**; the unit of
*judgement* stays the **interior slot**.

- Each of the 16 deep journeys is shown complete, endpoints included and marked, with every
  interior artist carrying its own FITS / DOESN'T FIT / CAN'T TELL control.
- The owner judges every interior slot of a journey in one pass, with the full path visible.
  An artist is looked up once, in the context it actually occupies.
- **Journeys are presented in shuffled order with no pair or depth label.**
- **A free-text note per journey** is captured. It is **not scored and carries no bar** —
  added so the whole-path impression has somewhere to go without inviting a post-hoc
  criterion.

**Denominators change accordingly, and this supersedes §5's:** the same artist in two
journeys is **two judgements**, because fit is contextual and it may genuinely fit in one
and not the other.

- **`D_all` = 65 interior slots** (was: 54 distinct artists).
- **`D_lookup`** = those slots whose artist the owner could not place on sight.

**The red control changes shape, not size.** The 12 injected artists are placed **into
journeys, at most one per journey** (12 of the 16 journeys carry one). They occupy an
interior slot and are judged like any other. `CAU-G1`'s bar is unchanged: **at least 10 of
12 judged DOESN'T FIT, or the audit is void.** Injected slots remain excluded from both
denominators.

**What this costs, stated plainly.** Shuffling isolated triples was the defence against the
owner recognising journeys he judged hours earlier and importing his impressions. Whole
journeys give that defence up. **This is a real loss and it is accepted deliberately:** an
instrument that cannot pose the question properly is worse than one that poses it properly
to a listener with a known prior — and that prior is exactly what `CAU-G1` exists to catch,
since a listener approving indiscriminately will wave the injected artists through.

**Workload after this amendment: 65 real slots + 12 injected = 77 judgements across 16
journeys** (the owner approved "all, no sampling" against a quoted 66; the true figure is
77, disclosed here before generation). No sampling, no seed, `CAU-C2` fully measurable.

**Unchanged by this amendment:** every read in §5, every bar, `CAU-G1`'s threshold, and the
whole of §6. `CAU-C2` (concentration) becomes *easier* to measure, since journeys arrive
intact by construction.

### `CAU-AM2` — the bar is ratified, and the control gets a hardness condition, 2026-08-04 (night)

**Committed before generation. No journey has been rendered, no artist sampled, and no
judgement exists.**

**1. `CAU-C1`'s bar is ratified by the owner at ≥ 75% FITS**, with the ≤ 50% and 50–75%
branches as written in §5. **This is his decision, not a session's** — he was offered the
choice, initially expressed no preference, and ratified 75% after being shown the argument
from `REQ-9` ("novelty is delivered **through** coherence, never at its expense. An
incoherent path is always worse, however novel"). Recorded this way because a later reader
must be able to tell an owner-set bar from a session-set one, and §5 previously said the bar
was unfixed.

**2. The injected artists get a hardness condition, and `CAU-G1` is meaningless without
it.** §4 required only that an injected artist be drawn from the same obscurity band. That
is not enough: a random artist in the same band could coincidentally *belong* between its
displayed neighbours, and rejecting the control would then be a harder task than the audit
itself — a listener could fail `CAU-G1` while judging perfectly well.

> **An injected artist must sit at graph distance ≥ 3 from both of its displayed
> neighbours** in the artifact the journey came from — no edge, and no shared neighbour.

Plain sentence: *"the fake artists really are unrelated to what sits either side of them, so
failing to reject one means the audit is not working."* Sampling retries until the condition
holds; if no candidate in an obscurity band satisfies it, the band is widened and **the
widening is recorded per injection** in the sealed file, so a later reader can see how hard
each control actually was.

**This makes `CAU-G1` a genuine red control** rather than a test of the listener's tolerance
for unusual-but-plausible neighbours. It moves no bar: 10 of 12 stands.

### `CAU-AM3` — the control contaminated its neighbours; question, placement and denominator all move, 2026-08-04 (night)

**Raised by the owner before any judgement existed.** A build had been generated under the
defective placement; **it was discarded, along with its sealed map, and nothing generated
under it survives into the run.** No result of any kind exists at the time of this
amendment.

**The defect.** `CAU-CORR1` fixed injections to be inserted between two existing cards. But
an inserted artist then becomes *a neighbour of two real cards*, and §3 asked the owner to
judge each artist against its neighbours. So up to two real slots per control were being
judged against a fake — **measured on the discarded build: 20 of the 65 real slots, 31% of
the audit.** The bias runs **against the graph**: a real artist looks wrong when the thing
beside it is nonsense. Large enough on its own to move `CAU-C1` across a branch boundary,
which would have been indistinguishable from a genuine result.

**Three changes, and the first two are methodology.**

**1. The question becomes journey-level.** §3's unit of judgement is no longer "does this
artist belong *between these two*" but:

> **"Does this artist belong on this journey?"**

The owner already sees the whole path under `CAU-AM1`, and journey-membership is the product
question — *is this a good card to be shown here*. It is also far less sensitive to one
perturbed neighbour than a strict local-transition test. The three verdicts (FITS / DOESN'T
FIT / CAN'T TELL) and the listening rule are unchanged.

**2. Controls are placed endpoint-adjacent only.** An injected artist is inserted either
between the first endpoint and the first interior, or between the last interior and the
second endpoint. **Endpoints are never judged**, so each control now touches exactly **one**
real card rather than two.

**3. The one real card flanking each control is excluded from scoring, and the owner is
never told which.** He judges it like any other; the scorer discards it. Declared here, in
advance, so the exclusion cannot be chosen after the fact.

**The denominator moves and this supersedes `CAU-AM1`'s:**

| | |
|---|---|
| Real interior slots **presented and judged** | **65** (unchanged) |
| Real slots **excluded** as control-adjacent | **12** |
| **`D_all` — real slots SCORED** | **53** |
| Control slots | 12 |
| **Total judgements — the owner's workload** | **77** (unchanged) |

`D_lookup` remains the looked-up subset **of the 53**. `CAU-C2`'s concentration count runs
over scored slots only. A journey whose sole interior is the excluded one contributes
nothing to `D_all`; that is accepted rather than patched, because moving the control
elsewhere in such a journey would put it back beside a scored card.

**The owner chose this over the alternative**, which was to move the controls into the eight
unaudited d0 journeys, keep all 65 slots scored, and pay 28 extra judgements of pure
camouflage (workload 77 → 105). His call, because it spends his time. Recorded so a later
reader does not read 53 as a session quietly shrinking the audit.

**Unchanged:** `CAU-G1` (10 of 12), `CAU-C1`'s ratified bars (75% / 50%), `CAU-C2`'s
trigger, `CAU-C3`'s trigger, `CAU-AM2`'s distance condition, and the whole of §6.

### `CAU-AM4` — each card carries its MBID, disambiguation and a MusicBrainz link, 2026-08-04 (night)

**Raised by the owner before any judgement existed and before the rebuild.** No result
exists at the time of this amendment.

**The problem.** The listening rule sends the owner to Spotify for any artist he cannot
place. Artist names are not unique, and this project has *measured* how often that bites:
the app's own name-based clip resolver plays the wrong same-named artist at roughly one card
in eleven (`BYP-13`, and it is one of the defects that motivated this audit). A listener who
looks up the wrong "Orbital" and judges *that* has not made a weak judgement — he has made
an unrelated one, and nothing downstream can detect it.

**The change.** Every interior and endpoint card now shows, alongside the name:

- the artist's **MBID**;
- its **MusicBrainz disambiguation** where one exists (38.6% of the artifact's nodes carry
  one — e.g. "US garage rock band", "Dutch techno producer Ralph Barendse");
- a **link to its MusicBrainz page**, from which the commercial-service links can be
  followed.

**Why this leaks nothing.** This is a one-arm audit, so there is no arm identity to protect.
Injected artists are drawn from the same artifact and carry the same three fields, so the
metadata cannot distinguish a control from a real card. MBIDs are opaque and carry no fame
signal, so the WGLL monthly-listeners bound is untouched.

**What it does cost, stated rather than discovered later.** A disambiguation is a genre/era
label, so the owner may sometimes judge partly on the label rather than on the music. That
cuts both ways and it makes the **red control somewhat easier to reject** — a random artist
whose disambiguation reads "Finnish black metal" stands out on a soft-rock journey without
being played. **So a `CAU-G1` pass is a weaker demonstration of discrimination than it would
have been without the metadata.** It remains a valid floor — `CAU-G1` exists to prove the
instrument *can* go red, not to measure how hard that is — and the trade is taken because a
misidentified artist corrupts a judgement outright while a label merely informs one.

**Unchanged:** every bar, every denominator, `CAU-G1`'s threshold, `CAU-AM3`'s placement and
exclusion, and the whole of §6.

### Corrections (`CAU-CORR`) — a separate series; these move no bar

> **`CAU-CORR1`, 2026-08-04 (night) — injected artists are INSERTED, not substituted.**
> §4 said an injected step has "their middle artist **replaced by** a random artist". That
> contradicts `CAU-AM1`'s own arithmetic in the same document: **"65 real slots + 12 injected
> = 77 judgements"**, and the denominator `D_all = 65 interior slots`. Replacement would
> destroy 12 real slots and leave 53, making `D_all` 53 and the workload 65 — neither of
> which any part of this document states.
>
> **The arithmetic is the original and governs: 77 = 65 + 12.** An injected artist is
> **inserted between two existing cards**, lengthening that journey by one; every real
> interior slot survives and is judged. `D_all` remains **65**, injected slots remain
> excluded from it, and the owner's approval of "all, no sampling" was given against 77.
>
> Only §4's verb lagged. Corrected before generation, before any artist was sampled and
> before any judgement existed, so no result could have shaped it. **This is a correction,
> not an amendment** — it changes no bar, no branch and no denominator, and `CAU-CORR` is a
> separate series from `CAU-AM` deliberately.
>
> Found by the build script's own self-check 5, which asserts the post-injection slot count
> against the declared denominator. The check existed because the `GBL-` harness log records
> four tests that passed while testing nothing; this one earned its place immediately.
