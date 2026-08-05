# `CAU-` — coherence audit results

**Role: ACTIVE — the results of record for `CAU-`, and it owns the `CAU-` figures.** Nothing
else restates them. Raw data, cited and never restated:
`builder/analysis/2026-08-04-coherence-audit/cau_judgements.json` (committed `cb11b38`,
before anything was scored), `cau_result.json`, and `cau_page_data.json` (the stimulus as
presented). Governing document:
[`specs/2026-08-04-coherence-audit-preregistration.md`](../specs/2026-08-04-coherence-audit-preregistration.md)
— four amendments and one correction, all committed before any judgement existed.

**Written by a session that did not design, build or run the audit**, and committed **before
`cau_owner_notes_SEALED.md` was opened.** That commit boundary is the evidence this read was
not shaped by the owner's direction. §5 is the response to his note, added afterwards in a
separate commit; **nothing above §5 was revised after reading it.**

---

## 0. What this can and cannot say

One arm, one listener, 53 scored judgements. The audit asks one question, fixed before any
journey was rendered: *"When the rebuilt app hands me an artist I have never heard of, does
that artist actually belong where it was put?"*

**§6's barred reads travel with every sentence below, and they are not softened by the
outcome:** no comparison with today's app at any strength; no whole-path or "detour" claim in
either direction; **no novelty claim** — the run sent the owner to Spotify, where monthly
listeners are displayed, so any novelty observation arising here is void by construction
(there are several in his notes, and they are deliberately not reported as findings below);
no adoption on any outcome; no attribution to the data set, the connection rule or the ramp
individually, because one arm can isolate nothing; and **"the coherence question is now
settled" is barred even on a pass.**

**The `GBL-` null is untouched.** Its margin of 3 against a bar of 5 stands, and
`findings/2026-08-04-gentle-arm-blind-listen-results.md` remains the owner of that verdict.
This audit measures a different thing — per-artist fit on one arm, not a journey-level
preference between two — and may not be used to smuggle that comparison back in.

---

## 1. Measured

Run state met: all 77 judgements present (65 real slots + 12 controls). The scorer refuses to
read a partial run.

### `CAU-G1` — the validity gate, evaluated first and alone

*Plain sentence: "the audit can tell a bad recommendation from a good one."*

| | |
|---|---|
| Planted artists | 12 |
| Judged DOESN'T FIT | **12** |
| Bar | ≥ 10 |
| Outcome | **PASS** — the audit is not void |

Of the 12, **10 were looked up before being rejected** and 2 were rejected on sight.

### `CAU-C1` — the primary outcome

*Plain sentence: "how often the rebuilt app's artists actually belong where it put them."*

| Denominator | Slots | FITS | DOESN'T FIT | CAN'T TELL | FITS fraction |
|---|---|---|---|---|---|
| **`D_all`** — every scored slot | 53 | 40 | 4 | 9 | **75.5%** |
| **`D_lookup`** — only artists he could not place on sight | 37 | 26 | 3 | 8 | **70.3%** |

**Branch: `meets_bar`** (bar ≥ 75%; the ≤ 50% fail branch is nowhere near). The bar is the
owner's, ratified at `CAU-AM2` before generation.

**The margin is one card.** 40 of 53 is 75.47%. Thirty-nine of 53 is 73.6%, which is the
`ambiguous` band. One slot moving from FITS to anything else changes the branch.

Neither denominator is "the" number — the pre-registration says so, and says `D_lookup` will
score worse by construction. Reported for completeness and carrying **no bar of its own**:
the 16 slots he placed on sight went 14 FITS / 1 DOESN'T FIT / 1 CAN'T TELL.

The 53 scored slots cover **43 distinct artists**; ten artists appear in two journeys each
and are two judgements by design, because fit is contextual.

### `CAU-C2` — concentration

*Plain sentence: "whether the bad ones are sprinkled about or whether some whole journeys are
wrecked."*

| | |
|---|---|
| Most DOESN'T FIT in any one journey | **1** |
| Trigger | ≥ 3 |
| Outcome | **does not fire** |

The four DOESN'T FIT verdicts fall in four different journeys. Twelve of the sixteen journeys
carry none.

### `CAU-C3` — residual unjudgeability — **FIRES**

*Plain sentence: "how often even proper listening left me unable to say."*

| | |
|---|---|
| CAN'T TELL, over `D_all` | 9 of 53 = **17.0%** |
| Trigger | > 15% |
| Outcome | **FIRES** |

The pre-registration attaches a specific reading to this: above 15% "it would mean
unfamiliarity, not clip length, was the barrier, and that the whole diagnosis in §0 is wrong",
to be reported prominently. **It is reported prominently, and §2.2 gives the reason I do not
think that particular inference survives contact with the notes** — which is a claim about the
pre-registered read, not a licence to discard it.

**Every CAN'T TELL slot, with the reason he gave.** This is raw data, not interpretation:

| Artist | His stated reason |
|---|---|
| Rick Davies | could not find his solo work anywhere he could listen; no solo release on MB |
| Max Martin | only findable "solo work" is a musical; otherwise a writer/producer for others |
| Brad Delson (×2 slots) | one release with one song on MB, and it cannot be found anywhere |
| Joey Kramer | Aerosmith drummer; no solo work findable |
| Dallas Taylor (×2 slots) | no releases visible at all; "surprised they weren't dropped by one of our filters" |
| John McVie | no solo releases |
| Four Tet | listened and read the MB bio; understood why it appears, but felt the bio had compromised his blind judgement and declined to pick a side |

**Eight of the nine are the same cause: there was nothing to listen to.** The ninth is Four
Tet, and it is a listener declining to score after his judgement had been informed by prose —
a protocol scruple, not an inability.

The same cause appears once more outside the CAN'T TELL column: **Rick Davies is DOESN'T FIT
in the other journey he appears in, with the identical reason recorded.** So the "nothing to
listen to" class accounts for **9 of the 53 scored slots (17%)** across both non-FITS columns.

### Free-text notes

Twenty-two of the 53 scored slots carry a note; **one** of the sixteen optional per-journey
notes was filled in. Per `CAU-AM1` the journey notes are unscored and no criterion may be
invented for them, so the single note is quoted in §2.4 as his statement and nothing is built
on it.

---

## 2. What I infer from this, in plain language

Labelled as inference throughout. Someone who has never read the pre-registration should be
able to disagree with all of it.

### 2.1 The audit works, and it is the first thing worth saying

Twelve fake artists were dropped into these journeys, chosen to be genuinely unrelated to what
sat either side of them. **The owner rejected all twelve**, and looked ten of them up before
doing so rather than rejecting them on the label. An instrument that waves fakes through
cannot tell you anything about real cards; this one does not. That is the condition the whole
audit rests on and it is met with room to spare.

One caveat, recorded before the run rather than discovered after (`CAU-AM4`): cards carry a
MusicBrainz disambiguation, so a fake whose label reads wildly wrong is easier to reject
without playing it. **A perfect score here is therefore a weaker demonstration than it looks.**
It is still a floor, and the floor is what the gate is for.

### 2.2 The headline result, and the thing that sits underneath it

**Of the 53 cards judged, 40 belonged where the app put them, 4 did not, and 9 he could not
say.** That is 75.5% against a bar of 75% — a pass by one card. Say it that way, because it is
one card.

Now the part that changes how I read it. **Nine of those thirteen non-fits are not the app
recommending badly — they are the app recommending someone with no music to play.** Rick
Davies, John McVie, Joey Kramer, Dallas Taylor, Brad Delson, Max Martin: a Supertramp
keyboardist, a Fleetwood Mac bassist, the Aerosmith drummer, a session drummer, Linkin Park's
guitarist, a pop songwriter-producer. These are real people who are on real records. They are
not artists you can put on. The owner went looking, and in most cases found nothing he could
listen to at all.

So the pre-registered reading of the can't-tell rate — "unfamiliarity, not clip length, was the
barrier" — **does not fit what he actually wrote.** Unfamiliarity was not the barrier; he
resolved plenty of unfamiliar artists by listening, including several he ended up adding to his
library. The barrier was that **for these cards there was nothing to resolve.** That is a third
possibility the pre-registration's binary did not anticipate, and I am naming it as a defect in
that read rather than treating the read as satisfied or discarding it. The recorded reading
stands on the record; I do not think it is what happened.

**This cuts both ways and I would not want only one half quoted.** Read one way, the coherence
of the real recommendations is better than 75.5% suggests, because most of the shortfall is a
data problem wearing a coherence problem's clothes: where he could hear anything at all, he
said it belonged 40 times out of 44. Read the other way, **a card you cannot listen to is a
failed card in the actual product**, whatever the reason — the app's whole unit is an artist
with a 30-second clip, and it has no way to play a man with no solo releases. On that reading
the 75.5% is not conservative at all; it is the honest number and roughly one card in six is
dead on arrival.

I do not think the audit can choose between those two readings, because it never asked. It
measured fit, and the "nothing to play" class showed up as a side effect.

### 2.3 The confound this audit was built to test did show up, independently of the criteria

The reason `CAU-` exists is that thirty seconds of one arbitrary track cannot support a
judgement about an unfamiliar artist. Three notes record his verdict changing as he listened
further:

- a **planted** artist whose first song he "could almost convince myself fit" — two more songs
  told him it did not;
- a real card where the first two songs "made no sense to me, but after listening to a few
  more, the connection is clear. It's actually a good fit";
- Four Tet, where more information changed his understanding enough that he declined to score
  it.

**In two of the three, the extra listening reversed the direction of the judgement.** That is
direct support for the diagnosis that motivated this audit — one clip is not enough — and it
arrives from the notes rather than from any criterion, so no bar attaches to it.

Two further notes record him nearly judging **the wrong artist** — a different Andy Ward and a
different Charlie Hall, both caught because the card carried an MBID and a MusicBrainz link.
`CAU-AM4` was added for exactly this and it paid for itself twice in 53 cards.

### 2.4 The bad cards, and his one journey note

The four DOESN'T FIT verdicts are spread one per journey, and where he explained them the
reason is sonic rather than structural: an instrumental cellist and a session bassist whose own
records sound nothing like the journey around them, even though the collaboration graph makes
the connection obvious. **This is the same class as §2.2 seen from the other side** — where a
collaborator does have solo records, they often sound like a different act.

His single journey note is his statement, unscored and carrying no criterion by construction:
*"Nathan East, Max Martin, and Brad Delson are all artists that seem to be mostly collaborators
on other works."* Every artist he names is in the class above. It is the only journey he
commented on, and the two of those three that were scored are both CAN'T TELL.

### 2.5 What I would say to the question the audit asked

On the evidence: **when this arm hands the owner an artist he has never heard of, and that
artist is someone he can actually listen to, it belongs there far more often than not.** When
it hands him a name with no records behind it, the question does not have an answer, and that
happened about one card in six.

The coherence worry that survived the `GBL-` null is answered on this evidence at the bar he
set — by one card. Nothing here is settled, nothing is adopted, and the audit compares this
arm to nothing.

---

## 3. Weakest link

In order of how much of the above they would take with them.

**1. The primary result rests on a single judgement.** 75.5% against 75%. One card moving out
of FITS puts it in the band the pre-registration deliberately refuses to call either way. **What
would falsify it:** nothing available — the run is complete and post-hoc exclusion is forbidden.
So this cannot be firmed up; it can only be stated. I would defend the direction of the result
and I would abandon the branch label cheaply, because a bar passed by 0.47 percentage points is
a coin landing on its edge.

**2. My re-diagnosis of the can't-tell rate is inference from free text, not measurement.** It
rests on eight notes from one listener, and no criterion measures "has listenable output". **What
would falsify it:** checking those artists against the artifact and the resolver — if the cards
in question do resolve to a playable clip, my reading is wrong and the pre-registered one gets
stronger. That check is cheap, it is not part of this audit, and I have not run it. I would
defend the observation that the notes say this; I would abandon any quantitative claim built on
it.

**3. The listener had seen these journeys before.** `CAU-AM1` gave up the shuffled-triple
defence on purpose so the question could be posed properly, and accepted that he might import
impressions from the `GBL-` run a day earlier. `CAU-G1` is the designed mitigation and it held
12 of 12 — but `CAU-AM4` weakened that same gate. The two amendments interact, and the
pre-registration notes each of them separately without noting that together they trade away
some of the protection twice.

**4. Fifty-three slots, 43 distinct artists, one listener, one arm.** The slots are not 53
independent observations; `CAU-AM1` said so in advance rather than being caught at it. There is
no confidence interval anywhere in this document because the design does not support one.

**5. `CAU-C3` firing means this audit's own premise is under challenge on the record.** Whatever
I make of the mechanism, the pre-registered sentence for that branch says the §0 diagnosis is
wrong, and a later reader is entitled to weigh that sentence over my reading of the notes.

---

## 4. Options, and what each costs

Adoption is not among them — §6 bars it on any outcome, and a pass makes adoption *decidable*
rather than decided. **These are the owner's, because each spends his time, his ear, or accepts
a residual risk.**

**A. Take the pass as it stands and move to the re-crawl decision.** The coherence worry that
survived the `GBL-` null is answered at his own bar; the standing untaken decision is whether
the candidate data set's advantage justifies the re-crawl it implies, and that has been waiting
since 2026-08-04. **Cost:** the branch was won by one card, and the "nothing to play" class stays
unaddressed underneath whichever data set wins.

**B. Open the un-listenable-artist class as its own question, before anything else.** It is
measurable entirely offline and against the whole artifact rather than 53 cards: how many nodes
have no solo release, how many fail to resolve to a clip, and how often they land in a journey's
interior. Two existing drop flags already target adjacent classes, and his own note asks why
these were not caught by them. **Cost:** it is a new track, and it delays the re-crawl decision
again. **This is the option I would take**, and the reason is that it is the only one here that
is cheap, decisive, and answers a question the audit raised rather than one it was asked —
and because a fix there moves both the coherence number and the clip-defect problem that cost
the `GBL-` listen five of its seven undecided rows.

**C. Re-run nothing and treat coherence as closed.** Not available as stated: §6 bars "the
coherence question is now settled" even on a pass. It is available as *"coherence is answered
well enough to stop measuring it for now"*, which is a different and defensible sentence.
**Cost:** the global question — whether journeys hang together end to end — remains measured by
nothing at all, and this audit deliberately did not ask it.

**D. Extend the audit.** More journeys, more listeners, or the d0 journeys left unaudited.
**Cost:** his time, at roughly 77 judgements per pass, to tighten a number whose direction is
already clear. I would not recommend it — the uncertainty that matters is not sampling error, it
is the class in §2.2, and option B addresses that far more cheaply.

---

## 5. The owner's sealed note — response

**Added after §§0–4 were written and committed (`184b3ac`). Nothing above this line was
revised.** `cau_owner_notes_SEALED.md` was written after he finished all 77 judgements and
before anything was scored, and committed unread at `4009707`. It carries his views on where
the project should go, which is why it was sealed until this point.

### 5.1 Where it converges, and that convergence is worth something

He identified the same mechanism I did, independently and first: that the deep cards are
**"solo acts of related musicians who are likely featured or credited on coherent songs/albums,
but they haven't released much solo work"**, that **"pretty much all of the 'can't tell' were
along these lines"**, and he names **Rick Davies** as the worked case.

My §2.2 was written without access to that sentence and reached the same class, with the same
artist as its first example. Measured against his claim: **8 of the 9 CAN'T TELL slots** are
this class, and the ninth (Four Tet) is a listener declining to score rather than being unable
to. So "pretty much all" is right, and it is the strongest thing this audit found.

**Two independent routes to the same conclusion is why the commit boundary was worth the
trouble.** Had the note been read first, this would be his hypothesis with my agreement
attached, which is worth much less.

### 5.2 His claims that no criterion here measures — reported as his statements

Per the handoff, these are recorded as what he said. **None is converted into a finding, and no
criterion is invented to accommodate any of them.**

- **"Overall I strongly prefer the new graph to the old."** A comparison between arms. §6 bars
  every such sentence in this document and `GBL-` §5's run-once rule binds that verdict; **the
  null stands.** It is also not new information: the `GBL-` results note already records that
  the blind did not hold and that he preferred the rebuilt package 6–0 at zero presses, which
  §5 excluded from the tally by design. An unblinded preference formed after judging everything
  cannot reopen a blind, pre-registered, run-once comparison — and I do not read him as asking
  it to.
- **"20 presses is too deep on this graph… on the old graph we went to at least 100 and barely
  moved the needle."** A depth claim and a comparative one. **This audit fixed no depth
  criterion.** The material is 16 journeys at two depths, and splitting the 53 slots by depth
  after seeing his note would be exactly the post-hoc denominator the pre-registration forbids.
  **So I have deliberately not computed it**, and I am not reporting a number I could easily
  have produced. It is a clean, cheap question for its own pre-registration.
- **"There were a lot of wrong artists' clips played."** Already in the record as `BYP-13` and
  as the reason five of the seven undecided deep rows in the `GBL-` listen were undecided. This
  audit routed around it by sending him to MusicBrainz and Spotify instead, so it measures
  nothing about clips.

### 5.3 Where my independent read disagrees with his

**He reads the un-listenable class as a benign side effect of reaching novelty faster. I read
it as a product defect.** He frames it as what you get when the graph is working — deep,
genuinely obscure, credited musicians on coherent records. That is a fair description of the
*cause*. But the app's unit is an artist with a clip you press play on, and **a card with
nothing to play has failed regardless of why it is there.** He half-concedes this himself in
the next sentence — "clips could be an issue though, especially at depths approaching 20" —
which is the same class arriving from the product side rather than the data side.

My §2.2 stated both readings before I saw his; his note picks the benign one. **I would defend
the stricter reading**, and it is the reason my §4 recommends counting this class offline before
anything else.

### 5.4 On "if I had my choice on my own, I'd adopt this graph to production and test it out"

**That is his decision and this document does not make it.** §6 bars adoption *on this audit's
outcome*, not adoption as such — he can take it on his own authority, and the only thing that
matters is that it is not recorded afterwards as something the audit licensed.

**Having said that, I think his instinct is more defensible than my §4 implies, and I want to
be honest about that rather than defend my own recommendation.** The roadmap's Gate 1 is
personal use, so the blast radius of adopting and living with it is himself — which makes
"adopt and try it" a genuinely cheap experiment, not a reckless one. My §4 option B does not
actually conflict with it: the un-listenable census is offline, runs against the artifact, and
does not need production to be left alone while it runs.

Two costs to name, and then it is his call:

1. **The blind listen is spent.** After adoption there is no clean instrument left to compare
   the two packages, and `GBL-` §5's run-once rule means it cannot be re-listened. Adoption
   makes the rebuilt graph the thing everything is measured *against* from then on.
2. **Adopting first means meeting the un-listenable cards in use rather than in a count.** He
   will find them — he already has, nine times in 53 — and the offline census that would size
   the problem takes one session either way.

**So the version I would put to him: adopt if he wants to, and run the census regardless.**
They are not alternatives, and I framed them as sequential in §4 when they are not.

---

## 6. Addendum — why the existing filters did not catch this class

**Added 2026-08-05 after the owner asked, in conversation, why an artist with no releases was
not already dropped. It measures nothing about `CAU-C1`, `CAU-C2` or `CAU-C3`, computes nothing
over the 53 slots, and is not a criterion.** It is a check of the builder's filter coverage,
prompted by the audit rather than performed by it. Figures are read off the census JSONs named
below, which own them.

**First, a correction to my own framing in §2.2, recorded here rather than edited in above.** I
wrote as though the app's unit is "an artist with a clip you press play on". The owner's
position, and it is his to define, is that the point is finding novel artists that cohere with
what you already like. That narrows the failing class usefully: the failure is not *"no clip
resolves"* but *"there is nothing to go and listen to"*. **Keith Scott is the worked
counterexample from this audit's own data** — the owner found him only on YouTube and judged
him FITS twice. A test that requires a commercial clip would drop a card he liked.

### What the two rules actually require

- **`drop_no_release_tail`** fires only at **zero** release-group credits (`pipeline.py:226`:
  *"the no-release tail requires zero"*).
- **`drop_featured_credit`** fires, per the rule string committed in the drop list itself, only
  when there is *"≥ 1 MB release-group credit **AND none sole** AND no sole-credit Discogs
  main-artist release AND NOT (commercial-DSP link AND a clip resolves)"*.

**A single sole credit is therefore enough to exempt an artist from both rules.** Zero credits
is covered; credits-but-never-sole is covered; **"has one sole credit that is not a body of
listenable work" is covered by neither.**

### The check

Every artist behind a CAN'T TELL or DOESN'T FIT verdict in this audit, tested against both
committed `ALG-B` lists (`fcf_droplist_algb_am1.json`, `ctc_droplist.json`):

| Result | Count |
|---|---|
| Never in the featured-credit class at all — not dropped, not kept, **never evaluated** | 22 of 23 |
| In the class and **kept** by the keep-check | 1 (Pino Palladino) |
| In the no-release drop list | 0 |

**So the class the audit found was not admitted by a filter making a bad call — it was never
looked at.** Brad Delson is the worked case: one release with one song in MusicBrainz. That one
sole credit puts him outside the featured-credit class and his non-zero credit count puts him
outside the no-release tail, so both rules pass him through in silence.

The single exception cuts the other way and is worth keeping: **Pino Palladino was in the class
and the keep-check kept him**, and the owner judged him DOESN'T FIT — "he's only released a few
solo albums… going off the sound, it doesn't fit". That is one instance of the keep-check being
too weak, against 22 of the class never being reached.

### A separate, real defect in the keep-check — which is *not* what admitted these artists

The owner raised the possibility that the wrong-artist clip defect (`BYP-13`) feeds the keep
decision. **It does, it is measured, and it does not explain this class** — because these
artists never reached the keep-check.

The keep-check resolves a clip **by name** and can only be verified where MusicBrainz recorded
a Deezer id. Read off `fcf_clips.json` and `fcf_clips_am1.json`, which own these figures and
which report the read as *"not part of the criterion"*:

| | pre-`FCF-AM1` | `FCF-AM1` |
|---|---|---|
| Name match landed on a **different** artist than MB recorded | 17 of 152 checkable (11.2%) | 8 of 165 (4.9%) |
| Keeps resting on a name match with **no recorded id to check against** | 211 of 394 | 179 of 367 |

**About half of all keeps could not be verified at all**, and the unverifiable half is the half
where a collision is most likely — an artist with no recorded DSP identity is exactly the one
whose name is most likely to resolve to a better-known namesake. The measured rate is therefore
a floor, on the checkable half. The census disclosed this honestly and did not act on it; the
keep list is name-path resolutions unfiltered by the wrong-artist check.

### What this makes the census in §4 option B

Sharper and cheaper than I described it. The question is not "does a clip resolve" — that is a
network snapshot, and it is the test that is already unsound. It is **"how many artists in this
graph have only a token sole credit, and how often do they land in a journey's interior"**,
which is countable offline against the archive with no clip resolution, no network and no
snapshot to freeze. The `BYP-13` exposure in the existing keep list is a second, separable
question.

---

## 7. Addendum — `CAU-G1` carries a third weakening, and all three point the same way

**Added 2026-08-05 (later), from
[`../2026-08-05-cau-audit-build-and-run-execution-log.md`](../2026-08-05-cau-audit-build-and-run-execution-log.md)
§5 — the build session's own log, written after this note was committed and read under a bar
that kept it from seeing any result.** Recorded here rather than edited into §3, so that
document's revision boundary holds. **It moves no figure and no branch.**

§3 named two things softening the red control: `CAU-AM1` gave up the shuffled-triple defence,
and `CAU-AM4`'s disambiguation labels make a wrong-sounding fake easier to reject unheard.
There is a third, and it was never written down until now:

> **Controls sit endpoint-adjacent, and the endpoints are the owner's own picks** — so every
> planted artist was judged next to an artist he chose and therefore always knows. A control in
> fully familiar context can be rejected without a lookup.

`CAU-AM3` gives the contamination argument for that placement, which is sound and was the
reason it was chosen. This is its unstated cost. **All three weakenings push in the same
direction: `CAU-G1` was easier to pass than the version of it a reader would imagine.**

**What this does and does not change.** It does not touch the gate's outcome or any reading
below it — 12 of 12 still means the audit is not void, and **10 of the 12 were looked up
before being rejected**, which is the measured fact that most limits how far this caveat
travels. What it changes is how much a *perfect* score is worth as evidence of discrimination:
less than it looks, for three compounding reasons rather than two. The gate exists to prove the
instrument **can** go red, not to measure how hard that is — and on that job it still holds.

**Recorded because the pattern matters more than the item.** Each weakening was disclosed in
advance, in the amendment that introduced it, exactly as the pre-registration discipline
requires. **None of the three documents noticed that the others existed.** A cost declared
three times in three places, and never once summed, is the failure mode that survives
per-amendment honesty.

---

## 8. Owed after this note

- `cau_page_data.json` is committed and out of `.gitignore` — the stimulus as presented, without
  which the judgements cannot be interpreted.
- No closeout has been run for the `CAU-` build-and-run chunk, nor for this one.
- **Not `CAU-`, and still open:** the owner's 2026-08-04 no-commercialization ruling is in memory
  but not yet in the repo record, and the eight 2026-07-22→27 `TEST-QUEUE.md` entries remain
  `QUEUED` and unruled-on.
