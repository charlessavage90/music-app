# 200 bypasses on one pair — what the app actually delivered, 2026-07-25

**Role: AUTHORITATIVE for its own measurements.** The owner's own use of the shipped app,
recorded. Owns every figure below; cite by section rather than restating.

**Two runs on the same pair**, Bob Dylan → Metallica, 100 presses each:

- **Run 1** — buttons mixed as they felt natural (74 `known`, 26 `dislike`).
- **Run 2** — **`dislike` only**, 100 presses, no `known` parameter at all. Run on the newer
  build, after confirming both builds return an identical path for run 1's final URL.

**This is dogfooding, not an experiment.** One pair, one listener, no arms, no control,
nothing scored, nothing pre-registered. It is recorded because use has twice surfaced defect
classes that code review and offline metrics missed
(`../plans/2026-07-21-alpha-rollout-roadmap.md`, meta-lesson), and because these runs are
currently the only evidence anywhere on how deep repeated bypassing actually goes.

**The path-quality pause is intact.** Using the shipped app and writing down what appeared
is not path-quality work and resumes nothing. No arm ran, no weight moved, no rebuild.

Identifiers are namespaced `BYP-n` — disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`, `MKS-`
and `ASC-`. **`BYP-1`–`BYP-9` were committed after run 1; `BYP-3`, `BYP-4`, `BYP-5`, `BYP-8`
and `BYP-9` are revised below by run 2, each marked inline with its original claim left
visible.** Numbers are never reused or renamed.

---

## 1. Protocol as actually run, including its defects

Outcome measure, both runs: **did a card appear whose artist the owner did not recognise** —
then, for each, **Spotify monthly listeners read by hand** to separate genuinely obscure from
famous-but-not-to-him.

**Run 1 defects, all three load-bearing:**

1. **The buttons are mixed**, so run 1 attributes nothing to `known` versus `dislike`. That was
   a deliberate instruction — a use test that makes the user behave unnaturally stops being a
   use test. Run 2 pays it back.
2. **A first attempt was abandoned on Radiohead → Bad Bunny**, because the interior fell
   entirely outside the owner's listening knowledge and "unfamiliar" therefore measured
   nothing — the limit `../WHAT-GOOD-LOOKS-LIKE.md` already records. The pair was suggested by
   a session optimising for path length and was a design error.
3. **Path length was logged only where it changed sharply.** *(This defect turned out to be the
   most consequential of the three: it produced a biased sample that a session then read as a
   behavioural signature. See `BYP-4`.)*

**Run 2 protocol, corrected:** single mechanism, and **path length recorded on every press for
the first 40**. The owner supplied the series as a CSV outside the repository; it is
transcribed verbatim into §10 so it survives independently of that file, and summarised in
`BYP-4`.

**Run 2's own residual defects:** still one pair and one listener; genre-deviation onset
(`BYP-11`) is an impression of a boundary, not a measured one; and the identity of the
single deepest artist is unverified (`BYP-10`).

## 2. What appeared — run 1

**`BYP-1` — seven artists the owner did not recognise, in 100 mixed presses.** *(Plain: across
a hundred presses, seven cards showed an artist he had never heard of.)*

| press | artist | Spotify monthly listeners |
|---|---|---|
| 29 | Lykke Li | 15M |
| 35 | The Human League | 6M |
| 37 | NOFX | 1M |
| 59 | Porcupine Tree | 500k |
| 83 | Television | **372k** |
| 84 | Boards of Canada | 1M |
| 98 | Beach House | 14.8M |

Listener figures throughout are **point-in-time, read by hand on 2026-07-25**, and will drift.

**`BYP-2` — the first one took 29 presses.**

**`BYP-3` — REVISED, THEN SUBSTANTIALLY RESTORED. Original claim:** *"nothing genuinely obscure
ever appeared. The floor across all 100 presses is 372k monthly listeners."*

**The floor figure is run-1-specific; the claim it supports survives both runs.** Run 2 reached
**168k** (Blood Red Shoes) — about twice as deep, and still a working band with six figures of
monthly listeners, not an obscurity. A draft of this document briefly recorded run 2 as
reaching **23** monthly listeners; that rested on FERG, which `BYP-13` shows is A$AP Ferg.

> **Across 200 presses on this pair, using both mechanisms, the app never presented an artist
> who is obscure by any ordinary reading.** *(Plain: it showed him artists he personally didn't
> know, but never one that is actually little-known.)*

**Method note worth keeping:** this document stated the run-2 floor conservatively as 168k
*before* FERG was checked, precisely because its identity was unverified. Had it led with 23,
the correction would have been a retraction of the headline rather than a footnote.

## 3. What appeared — run 2, `dislike` only

**`BYP-10` — ten unrecognised artists, and a floor roughly twice as deep as run 1's — but
still not obscure.** *(Plain: pressing only "not for me" found more artists he didn't know, and
went somewhat further down, but never reached anyone genuinely unknown.)*

| press | artist | Spotify monthly listeners |
|---|---|---|
| 41 | New Order | 8.8M |
| 60 | NOFX | 1M *(also unfamiliar in run 1)* |
| 65 | Love | 571k *(no clip — see `BYP-12`)* |
| 65 | Captain Beefheart & His Magic Band | 235k |
| **89** | **FERG** | **NOT a discovery — this is A$AP Ferg. See `BYP-13`.** |
| 91 | 10cc | 6.7M |
| 93 | Blood Red Shoes | **168k** |
| 93 | Black Rebel Motorcycle Club | 716k |
| 100 | Quantic | 2.3M |
| 100 | Nightmares on Wax | 1.7M |

**Head-to-head:**

| | run 1 (mixed) | run 2 (`dislike` only) |
|---|---|---|
| unrecognised artists | 7 | **10** |
| first at press | **29** | 41 |
| floor, monthly listeners | 372k | **168k** |

**`dislike` is slower to first novelty, finds more of it, and reaches somewhat deeper — about
2× on the floor, not the three orders of magnitude an earlier draft of this section claimed on
the strength of FERG.** It still **confirms** the prediction recorded in §11 before run 2 ran —
that the button *designed* to carry obscurity (`known`) is the weaker of the two — and
**falsifies the mechanism `BYP-9` was read to imply**, that `dislike`'s length suppression
would make it deliver less. But the margin is modest, and **neither run reached an artist who
is obscure by any ordinary reading**; see `BYP-3`.

## 4. Path length — and a correction to the run-1 reading

**`BYP-4` — ⚠ CORRECTED BY RUN 2, THEN PARTLY RESTORED BY THE OWNER. Original claim, left
visible:** *"length oscillates; it does not progress."*

**Two corrections, in opposite directions. The accurate statement is that both things happen at
once, and a session got each half wrong in turn.**

**First half — "does not progress" is false.** Run 1 logged length *only where it changed
sharply* (§1 defect 3), so its record contained spikes and collapses **by construction**, and a
session read that selection artifact as a behavioural signature. The run-2 series, recorded on
every press, shows a clear stepwise climb:

| presses | cards | note |
|---|---|---|
| **1–9** | **3** | nine consecutive — see `BYP-9` |
| 10–25 | 4 *(one dip to 3 at press 11)* | fourteen consecutive 4s from press 12 |
| 26–32 | 5 *(one 6 at press 27)* | |
| **33** | **10** | spike |
| 34 | 5 | immediate collapse |
| 35–40 | 6–8 | trending up |

**Second half — "oscillates" survives, and the session that discarded it over-corrected.**
Raised by the owner against that correction, with the decisive evidence:

> **In neither run is the final path length the largest.** Run 1 peaked at **13 cards** and
> ended at **6**. Run 2 reached **10** by press 33 and was back to **5** the next press. If
> length were monotone in bypass depth, the last state would be the longest. It is not, in
> either run.

The excursions are large — a fall from 10 cards to 5 in a single press — and they are not an
artifact of what was logged, because run 2's series recorded every press.

**Accurate statement, replacing both the original and the first correction: an upward trend
with large non-monotone excursions.** The owner's characterisation, recorded as his impression
rather than as measurement, is that both runs share this shape — climbing steadily, then
dropping abruptly at several points, with jumping in between.

**What still cannot be separated:** whether run 1's excursions were *larger* than run 2's, or
differ by mechanism. Run 1 has no series, and only run 2's first 40 presses were logged.

**`BYP-5` — ⚠ CORRECTED BY RUN 2. Original claim, left visible:** *"after 100 accumulated
exclusions the output is qualitatively where it started."*

**Wrong on length, and wrong as a statement about the app.** Run 1 went from 3 cards to 6 —
growth, not return; the claim read a *drawdown from the peak* as a *return to the start*, which
`BYP-4`'s restored second half now accounts for properly. And run 2's final state carries **two
unfamiliar artists** (Quantic, Nightmares on Wax at press 100), so it did not end where it
began in the other quantity either.

**What survives is run-1-specific:** run 1's own final state was 6 cards and, by the owner's
report, all famous.

**What survives, and it is narrower:** *(Plain: for the first quarter of a long session the
journey has only one or two artists in the middle.)* **25 of run 2's first 40 presses sit at
length 3 or 4** — one or two interior cards. At length 3 there is exactly one interior card and
bypass is hidden on the endpoints, so the app can only substitute that single artist.

**`BYP-9` — CONFIRMED AND REPRODUCED.** *(Plain: pressing only "not for me" kept the journey at
three cards — start, one artist in the middle, end — for nine presses running.)* Nine
consecutive 3-card paths at presses 1–9, and a tenth at press 11, **reproduced on the newer
build**. At 3 cards this is **forced 1:1 swapping**. Against `../WHAT-GOOD-LOOKS-LIKE.md`:
**value 6** says `dislike` should 1:1-swap *much less often* than `known` — here it swapped on
every press; **value 7** names sustained confinement as the defect form, explicitly
distinguishing it from single local deviations, which are expected and fine.

*(Recorded for method: a session challenged the original observation as a possible artifact of
finer logging, since run 1's early phase was a range not a series. The owner held the claim on
recall, noting a run of that many 3-card paths would have been salient. Run 1's own notation —
"3–5" for presses 1–27, a statement of variation — corroborated him, and the run-2 series then
confirmed it outright. **Twice in this investigation finer logging overturned a reading built
on coarser notes, both times against the session.**)*

## 5. Novelty arrives by leaving the genre, not by descending within it

**`BYP-11` — genre deviation precedes obscurity by roughly fifty presses, and the deepest
artist arrived inside a path the owner called incoherent.** *(Plain: before the app showed him
anything genuinely unknown, it first wandered into kinds of music that have nothing to do with
either artist he picked — and the one truly obscure artist turned up in the middle of a jump
that made no musical sense.)*

Owner's observations across run 2, verbatim in substance:

| press | observation |
|---|---|
| ~37 | "where I start to see real genre deviation. Nothing earlier stood out" |
| 38 | Usher, 50 Cent, Xzibit — "did very much stand out to me" |
| 61 | Norah Jones → Dido → **Eminem** — "the transition to Eminem is the jarring part" |
| 77 | "another interesting genre jump", Wu-Tang Clan |
| **89** | **"wildly incoherent step between BROCKHAMPTON and Skrillex"** *(the FERG card sits here; see `BYP-13` — the judgement was made on the card names, which were correct, so it stands)* |

**Onset of genre deviation ≈ press 37. First genuinely obscure artist: press 89.**

**INFERENCE, and it is the most consequential reading in this document:** the router does not
descend *within* a genre — it crosses genres at comparable fame, and only then descends. That
is consistent with `2026-07-25-mutual-knn-stranding.md`: the artists one rung below Dylan and
Metallica *in their own genres* are precisely the stranded class, so those routes are cut,
leaving cross-genre movement as the affordable way out of the famous stratum.

**Measured against a stated preference, this is a defect.** `../WHAT-GOOD-LOOKS-LIKE.md`
value 8 states novelty is delivered *through* coherence, not traded against it; value 1's bound
says it is "not a licence to buy novelty with incoherence." **The single deepest discovery in
either run arrived inside a path the owner independently called wildly incoherent.**

**Falsified if:** a run on a different pair reaches comparable obscurity without genre
departure, or if the deviation onset does not precede the obscurity onset.

## 6. Mechanism inferences

**`BYP-6` — novelty co-occurs with the length spikes. INFERENCE, run 1 only, and weakened.**
Three of run 1's seven landed on or within two presses of a spike. With `BYP-4` corrected, run
1's "spikes" are a selected sample, so the co-occurrence may be an artifact of what was logged.
**Run 2 does not obviously support it**: the press-33 spike to 10 cards produced no unfamiliar
artist, and the first came at 41.

**`BYP-7` — why a path can get *shorter* as exclusions accumulate. INFERENCE, and it survives**
— presses 33 → 34 fall from 10 cards to 5. Exclusions only accumulate, so the option set only
shrinks, yet hop count falls. Hop count is not monotone under exclusion: removing one artist
can break a long chain of cheap small steps, forcing a shorter route that pays larger
popularity jumps instead. Total cost rises, as it must; cards fall.

**`BYP-8` — ⚠ SUBSTANTIALLY WEAKENED BY `BYP-4`'s CORRECTION. Original claim, left visible:**
that Track 2 and Track 2F, scoring at depths 10/15/20, may have sampled an oscillating signal
at arbitrary phase.

**Its premise was oscillation. The premise is gone.** A signal that progresses stepwise is not
sampled at arbitrary phase by three increasing depths — it is sampled sensibly. **This is no
longer a reason to doubt those results**, and it never was offered as an explanation of `R0`.
The read-only check it proposed (plot path length against depth in the committed walks) is
still cheap and would close it either way, but its expected value has dropped sharply.

## 7. New observation — clip coverage, distinct from the closed clip defects

**`BYP-12` — two artists returned no clip: Wu-Tang Clan (press 77) and Love (press 65).**
*(Plain: two cards had nothing to play, one of them a very well-known group.)*

**This is a coverage gap, not a regression.** C2 (clips die after a while) is unrelated. Here
the resolver returned nothing at all. Wu-Tang Clan is large enough that its absence is
surprising and worth a look before Gate 2, when other people will meet it.

**`BYP-13` — a card played a clip by a different artist, and the mechanism is not the one C1
fixed.** *(Plain: one card said FERG and played music by a completely different, tiny artist of
the same name.)*

At press 89 the card read **"FERG — fka A$AP Ferg"**. That is **A$AP Ferg**, who renamed
himself; the graph node is a famous rapper. The clip that played was by an unrelated Spotify
artist also called FERG, with 23 monthly listeners.

**Sequence of how this was established, because it is the useful part:**

1. The owner did not recognise the name and read Spotify monthly listeners for "FERG" — 23.
   Logged as the deepest artist in either run.
2. A session flagged the identity as unverified and stated the run-2 floor conservatively at
   168k rather than 23.
3. The owner typed FERG into **the app's search box**: one result, `FERG — fka A$AP Ferg`, no
   second entity. That settled it.

**Nothing in the normal viewing flow would have caught this.** The disambiguation that names the
artist appears in search and **not on the card** (`BYP-15`), so the correction required leaving
the journey and going to a different screen — prompted by a session, not by anything the page
showed.

**Three things follow.**

- **The graph is fine.** The app's search returns one FERG and its MusicBrainz disambiguation
  says exactly who it is. This is **not** an instance of
  `2026-07-25-mutual-knn-stranding.md` `MKS-7`, and not a junk node.
- **The clip resolver is not.** It matched an external catalogue by *name string* and picked
  the wrong entity. That is **C1's defect class — a card playing the wrong artist — reached by
  a different route.** C1 was closed on a worked example where a band name collided with a
  *song title*; this is an **artist-name collision, aggravated by a recent rename**, and it is
  live in the shipped app. **C1 should not be treated as fully closed on the strength of this.**
- **The second-opinion instrument has a failure mode, and it is exactly here.**
  `../WHAT-GOOD-LOOKS-LIKE.md` licenses hand-reading Spotify monthly listeners to separate
  obscure from famous-but-not-to-him. That lookup is **by name**, so for a renamed or colliding
  artist it silently returns a different entity — and it fails *toward* reporting a spurious
  discovery, which is the direction that flatters a result. **Guard: read the MusicBrainz
  disambiguation before trusting a name lookup.** Note `BYP-15` — in the shipped app that
  disambiguation is **not on the card**, so nothing in the normal viewing flow offers it.

**`BYP-15` — the card does not show the MusicBrainz disambiguation; search does.** *(Plain: the
app knows this artist is "fka A$AP Ferg" and shows you that when you search, but the card in a
journey just says FERG.)*

Reported by the owner, 2026-07-25, correcting a draft of this section that assumed the card
carried it.

**This is a separate defect from `BYP-13` and survives a fix to it.** Had the disambiguation
been on the card, the wrong clip would still have played — that is a resolver bug — **but the
owner would not have been misled about who he was looking at**, which is what turned a clip
defect into a false entry in this document.

**Why it matters beyond this one card:** `2026-07-25-mutual-knn-stranding.md` `MKS-7` records
**1,283 artist names shared by 2,838 artists — 3.83 % of the graph.** For any of them, a card
gives the user no way to tell which entity they are being shown, while the data to disambiguate
is already loaded and already rendered elsewhere in the same app.

**What it would cost:** MusicBrainz disambiguations are optional, so most cards would be
unchanged and the addition is conditional. **Whether the card should carry it is the owner's
call** — it is a question about what the product shows, and the card has just been through a
round of design. Recorded here, not proposed.

## 8. What this does and does not license

**Does:** establishes from use that repeated bypassing surfaces unfamiliar artists, how long
that takes on each mechanism, how deep each reaches, that `dislike` reaches far deeper than a
mixed run, that length progresses stepwise under `dislike`, and that genre departure precedes
obscurity.

**Does not — five ways:**

1. **It does not refute §2.9 of the Phase 1 log.** That is in **graph-popularity percentile**;
   this is in **Spotify monthly listeners**. Conflating them is the error §2.6, §2.11 and §2.12
   warn about. Nothing here measures the graph's own popularity for any artist named.
2. **Two runs, one pair, one listener.** Bob Dylan → Metallica is a famous-to-famous cross-genre
   pair, the hard case by design — it is not a sample.
3. **Run 1's mechanisms are confounded** (§1) and its length record is a selected sample (§4).
4. **The deepest artist is unverified** (`BYP-10`).
5. **It proposes no change.** No arm, no weight, no rebuild, no threshold.

## 9. Method note — the second-opinion instrument, and that it changed the read

`../WHAT-GOOD-LOOKS-LIKE.md` licenses hand-read Spotify monthly listeners for exactly this
question, under three bounds, all met: **not a blind listen** (no arms, no selection), **no
scored criterion used it**, and the third — *write down any check that changed your mind* — is
discharged here:

> **Run 1: two of seven would have been logged as discoveries without it.** Lykke Li (15M) and
> Beach House (14.8M) are famous artists outside this listener's geography, not obscure ones.
> **Run 2: it separated a genuine result from an unverifiable one** — Blood Red Shoes at 168k
> and Captain Beefheart at 235k stand; FERG at 23 is flagged rather than claimed.

The instrument is why `BYP-3` could be stated and why `BYP-10` is stated conservatively. **Its
failure mode is recorded in `BYP-13`** and is not hypothetical: it produced the one wrong figure
in this document.

**`BYP-14` — manual logging at this scale is not sustainable, and most of it was unnecessary.**
*(Plain: counting presses and writing down path lengths by hand took a long time, was hard, and
nearly went wrong — and the app was already recording most of it.)*

The owner's report after run 2: it took a long time, was difficult, he thought he had lost
count, and was surprised to have hit exactly 100 twice. **The press accounting did in fact come
out exact both times** (§10) — but a method whose accuracy depends on that is not one to build
on.

**Most of the burden was avoidable, and this is worth knowing before any further run:**

- **The URL is already a complete log of the presses.** Exclusions accumulate in press order.
  For a **single-mechanism** run like run 2, press *N*'s state is the first *N* entries of the
  final list, so **the entire length series and every card list is recoverable by replaying
  truncations of one URL** — including the 60 presses past where manual logging stopped. Nothing
  needed to be written down for that.
- **Run 1 is only partly recoverable**, because two lists interleave and the final URL does not
  record the order the mechanisms were pressed in. **A single-mechanism run is fully
  reconstructible; a mixed one is not.** That is an argument for running one mechanism at a
  time, independent of the confound argument in §1.
- **What genuinely needs a person is recognition** — and it does not need to happen between
  presses. A list of the artists seen can be read afterwards, away from the app.

**Instrument rather than simulate.** A scripted walk would be cheaper still, but it must choose
its own victim each press, and a mechanical victim policy is not what a real user does — the
choice of *which* card to bypass is the taste-driven part. Recording what the app already
returns preserves that; simulating it does not.

## 10. Reproducible states

These URLs encode the **full exclusion set** and therefore reproduce the exact path on the
adopted artifact. The host is a local dev server; the path and query are the durable part. The
endpoint MBIDs are `72c536dc-…` (Bob Dylan) and `65f4f0c5-…` (Metallica).

**Exclusion counts corroborate every press label exactly** — run 1: 25+2 = 27, 30+3 = 33,
44+6 = 50, 74+26 = 100. Run 2: 100 `dislike` entries, no duplicates, no `known` parameter.
That is why the press numbers here can be trusted rather than treated as recollection.

### Run 2 — path length by press, 1–40

Transcribed verbatim from the owner's CSV, which lives outside the repository. **This is the
series `BYP-4` summarises**, and the only complete length record either run produced.

```
press,cards
1,3    2,3    3,3    4,3    5,3    6,3    7,3    8,3    9,3    10,4
11,3   12,4   13,4   14,4   15,4   16,4   17,4   18,4   19,4   20,4
21,4   22,4   23,4   24,4   25,4   26,5   27,6   28,5   29,5   30,5
31,5   32,5   33,10  34,5   35,7   36,6   37,7   38,8   39,7   40,6
```

Presses 41–100 were not logged by hand, and per `BYP-14` **do not need to be** — they are
recoverable by replaying truncations of the run-2 URL below.

### Run 2 — one URL suffices, and here is why

**Exclusions accumulate in press order**, and run 2 used a single mechanism, so **press *N*'s
state is the first *N* entries of the final list.** Verified: press 89's list ends at
`985c709c-…`, which is exactly the 89th entry of the final list. Every intermediate state of
run 2 is therefore recoverable from the URL below — including press 89, the FERG path.

**Run 1 needs its four URLs** because two lists interleave and the final URLs do not record the
order in which the two mechanisms were pressed.

**Run 2, press 100 — 100 `dislike` exclusions.**

```
http://localhost:5174/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?dislike=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2C83d91898-7763-47d7-b03b-b92132375c47%2C5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C70248960-cb53-4ea4-943a-edb18f7d336f%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C618b6900-0618-4f1e-b835-bccb17f84294%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2C109958eb-a335-4c5e-907e-597ff4c6af46%2C06fb1c8b-566e-4cb2-985b-b467c90781d4%2C04cd0cfd-bfd1-4c36-bc38-95c35e2c045f%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2C8f6bd1e4-fbe1-4f50-aa9b-94c450ec0f11%2C40f5d9e4-2de7-4f2d-ad41-e31a9a9fea27%2Cb6b2bb8d-54a9-491f-9607-7b546023b433%2C64b94289-9474-4d43-8c93-918ccc1920d1%2C5cbef01b-cc35-4f52-af7b-d0df0c4f61b9%2C9a58fda3-f4ed-4080-a3a5-f457aac9fcdd%2C82eb8936-7bf6-4577-8320-a2639465206d%2C39c2a93d-9afa-4a22-9bba-c087ab056e1c%2C9e53f84d-ef44-4c16-9677-5fd4d78cbd7d%2Cafdb7919-059d-43c1-b668-ba1d265e7e42%2C494e8d09-f85b-4543-892f-a5096aed1cd4%2Cf9ef7a22-4262-4596-a2a8-1d19345b8e50%2Ca94a7155-c79d-4409-9fcf-220cb0e4dc3a%2Cf1106b17-dcbb-45f6-b938-199ccfab50cc%2Ce795e03d-b5d5-4a5f-834d-162cfb308a2c%2C794c6bf2-3241-416f-9b8f-24e2d84a1c4b%2C72359492-22be-4ed9-aaa0-efa434fb2b01%2C8ac6cc32-8ddf-43b1-9ac4-4b04f9053176%2Ce01c3376-15fa-40d7-b747-5f219bdefdd7%2C774666d2-2064-4d6c-856c-f8cda0aaf9f0%2C12ff8858-bfcb-4812-a8dd-7e9debf0cbee%2Cf27ec8db-af05-4f36-916e-3d57f91ecf5e%2Cd6ed7887-a401-47a8-893c-34b967444d26%2C0c502791-4ee9-4c5f-9696-0602b721ff3b%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2Cd2ff6b6b-fc30-48dc-8952-06f9d8fc64f8%2Caab5c954-cabe-432e-899e-1c4f99757327%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2Ca96ac800-bfcb-412a-8a63-0a98df600700%2C52074ba6-e495-4ef3-9bb4-0703888a9f68%2Cdebabff3-2559-46e5-862d-ef2a906d7010%2Ce57f0cac-4f56-473c-8d7e-d93f753fd586%2Cf37b3f31-b1f8-4b88-8cb5-b34f709b17d7%2C561d854a-6a28-4aa7-8c99-323e6ce46c2a%2C611700cf-27f0-4dc9-ae80-c513a767853e%2C36bfa85f-737b-41db-a8fc-b8825850ffc3%2C99ea432a-e3d8-42cb-9d5e-db316a6a8458%2C84dc4f23-c0b8-4fe1-bbca-a3993ddc8fc2%2C03ad1736-b7c9-412a-b442-82536d63a5c4%2C588dea29-eea3-456b-a815-3ee04f75c8e7%2Cd1353a0c-26fb-4318-a116-defde9c7c9ad%2Cdcaa4f81-bfb7-44eb-8594-4e74f004b6e4%2C331ce348-1b08-40b9-8ed7-0763b92bd003%2C1ee18fb3-18a6-4c7f-8ba0-bc41cdd0462e%2C2f9ecbed-27be-40e6-abca-6de49d50299e%2C34cf95c7-4be9-4efd-a48a-c2ea4a0bb114%2C0d8b0d50-e4cf-4da4-965d-f24c58ec3268%2C160629ab-ec18-4931-8c95-02cb92d06186%2Cbdbd48f5-abf3-4a4f-9a21-4551dbc3fde9%2Cc2e36518-9c3b-4dcb-82ad-a3fc7fe99c67%2C4b585938-f271-45e2-b19a-91c634b5e396%2Cf93dbc64-6f08-4033-bcc7-8a0bb4689849%2Cfbe054ec-a143-4101-9e9e-64abc5ff5ac9%2C2fddb92d-24b2-46a5-bf28-3aed46f4684c%2Ce6e879c0-3d56-4f12-b3c5-3ce459661a8e%2Ce20747e7-55a4-452e-8766-7b985585082d%2Ca6de8ef9-b1a1-4756-97aa-481bbb8a4069%2Cd87e52c5-bb8d-4da8-b941-9f4928627dc8%2C2944824d-4c26-476f-a981-be849081942f%2Ce5db18cb-4b1f-496d-a308-548b611090d3%2C985c709c-7771-4de3-9024-7bda29ebe3f9%2Cae002c5d-aac6-490b-a39a-30aa9e2edf2b%2Cf23ef341-33bd-47c1-b83c-846a78581f05%2Cece57992-dc2e-4f67-a269-fa43626c1a3d%2Ce21857d5-3256-4547-afb3-4b6ded592596%2Cba550d0e-adac-4864-b88b-407cab5e76af%2C487bfd74-71bf-46dd-b89c-80b7a0f06f2f%2C0aad6b52-fd93-4ea4-9c5d-1f66e1bc9f0a%2C34ec9a8d-c65b-48fd-bcdd-aad2f72fdb47%2C9e0e2b01-41db-4008-bd8b-988977d6019a%2Cc7423e0c-ab3e-4ab4-be10-cdff5a9d3062%2C169c4c28-858e-497b-81a4-8bc15e0026ea%2C534ee493-bfac-4575-a44a-0ae41e2c3fe4
```

### Run 1 — four states

**Press 27 — 12 cards** (25 `known`, 2 `dislike`). The first large length spike.

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58
```

**Press 33 — 5 cards** (30 `known`, 3 `dislike`). Six presses after the spike, collapsed.

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8
```

**Press 50 — 4 cards** (44 `known`, 6 `dislike`).

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8%2C94b0fb9d-a066-4823-b2ec-af1d324bcfcf%2C9e53f84d-ef44-4c16-9677-5fd4d78cbd7d%2C4b585938-f271-45e2-b19a-91c634b5e396%2C331ce348-1b08-40b9-8ed7-0763b92bd003%2C52074ba6-e495-4ef3-9bb4-0703888a9f68%2C84eac621-1c5a-49a1-9500-555099c6e184%2C34cf95c7-4be9-4efd-a48a-c2ea4a0bb114%2C05517043-ff78-4988-9c22-88c68588ebb9%2C109958eb-a335-4c5e-907e-597ff4c6af46%2C5cbef01b-cc35-4f52-af7b-d0df0c4f61b9%2C39c2a93d-9afa-4a22-9bba-c087ab056e1c%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C64b94289-9474-4d43-8c93-918ccc1920d1%2Caab5c954-cabe-432e-899e-1c4f99757327&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8%2C611700cf-27f0-4dc9-ae80-c513a767853e%2Cdcaa4f81-bfb7-44eb-8594-4e74f004b6e4%2C2eada8f8-056a-4093-bbc2-004909ce743b
```

**Press 100 — 6 cards** (74 `known`, 26 `dislike`).

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8%2C94b0fb9d-a066-4823-b2ec-af1d324bcfcf%2C9e53f84d-ef44-4c16-9677-5fd4d78cbd7d%2C4b585938-f271-45e2-b19a-91c634b5e396%2C331ce348-1b08-40b9-8ed7-0763b92bd003%2C52074ba6-e495-4ef3-9bb4-0703888a9f68%2C84eac621-1c5a-49a1-9500-555099c6e184%2C34cf95c7-4be9-4efd-a48a-c2ea4a0bb114%2C05517043-ff78-4988-9c22-88c68588ebb9%2C109958eb-a335-4c5e-907e-597ff4c6af46%2C5cbef01b-cc35-4f52-af7b-d0df0c4f61b9%2C39c2a93d-9afa-4a22-9bba-c087ab056e1c%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C64b94289-9474-4d43-8c93-918ccc1920d1%2Caab5c954-cabe-432e-899e-1c4f99757327%2C06fb1c8b-566e-4cb2-985b-b467c90781d4%2C04cd0cfd-bfd1-4c36-bc38-95c35e2c045f%2C160629ab-ec18-4931-8c95-02cb92d06186%2C2819834e-4e08-47b0-a2c4-b7672318e8f0%2C092b603f-eb4c-4958-b10e-02420de5885b%2Cf37b3f31-b1f8-4b88-8cb5-b34f709b17d7%2Ca94a7155-c79d-4409-9fcf-220cb0e4dc3a%2C72359492-22be-4ed9-aaa0-efa434fb2b01%2C0c502791-4ee9-4c5f-9696-0602b721ff3b%2Cf93dbc64-6f08-4033-bcc7-8a0bb4689849%2C9a58fda3-f4ed-4080-a3a5-f457aac9fcdd%2Cfa97dd36-1b82-43d7-a6e4-2adeafd59cef%2C9e0e2b01-41db-4008-bd8b-988977d6019a%2Cdebabff3-2559-46e5-862d-ef2a906d7010%2C78f797e3-4913-4026-aad0-1cd858bd735b%2Cf27ec8db-af05-4f36-916e-3d57f91ecf5e%2C03ad1736-b7c9-412a-b442-82536d63a5c4%2Cd8e41375-bd8d-4e39-9da7-f0c171e97086%2Cc3f28da8-662d-4f09-bdc7-3084bf685930%2C33b3c323-77c2-417c-a5b4-af7e6a111cc9%2C1f43d76f-8edf-44f6-aaf1-b65f05ad9402%2C01d3c51b-9b98-418a-8d8e-37f6fab59d8c%2Cb6b2bb8d-54a9-491f-9607-7b546023b433%2Ce01c3376-15fa-40d7-b747-5f219bdefdd7%2C59a7fbcb-ff74-494d-abd0-9c82359040c9%2C7808accb-6395-4b25-858c-678bbb73896b%2C6a726ac6-019e-455c-8bbb-571a77bed52e%2C17b53d9f-5c63-4a09-a593-dde4608e0db9%2C664c3e0e-42d8-48c1-b209-1efca19c0325%2C0af78501-5647-4c18-9a0d-66ac8789e13b&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8%2C611700cf-27f0-4dc9-ae80-c513a767853e%2Cdcaa4f81-bfb7-44eb-8594-4e74f004b6e4%2C2eada8f8-056a-4093-bbc2-004909ce743b%2Cc0b2500e-0cef-4130-869d-732b23ed9df5%2Cbdc70372-7e8a-4cb9-8d33-f036b3b7cdc1%2C169c4c28-858e-497b-81a4-8bc15e0026ea%2Cece57992-dc2e-4f67-a269-fa43626c1a3d%2C22dc19af-d085-4c9b-adfb-22ec256251f1%2C2f9ecbed-27be-40e6-abca-6de49d50299e%2C2fddb92d-24b2-46a5-bf28-3aed46f4684c%2C3414d446-735a-443c-931f-10634f57e5b9%2Cd2ff6b6b-fc30-48dc-8952-06f9d8fc64f8%2C149e6720-4e4a-41a4-afca-6d29083fc091%2C01809552-4f87-45b0-afff-2c6f0730a3be%2Cd8661c02-f423-4d72-8044-40ff05daf7a1%2C69158f97-4c07-4c4e-baf8-4e4ab1ed666e%2C5dfdca28-9ddc-4853-933c-8bc97d87beec%2C985c709c-7771-4de3-9024-7bda29ebe3f9%2C494e8d09-f85b-4543-892f-a5096aed1cd4%2Ccc2c9c3c-b7bc-4b8b-84d8-4fbd8779e493%2C7bd9e20e-74b9-446a-a2ed-a223f82a36e7%2Cd5cc67b8-1cc4-453b-96e8-44487acdebea%2C77c167d2-4965-4421-830a-9815e4956475
```

## 11. What these runs make worth doing next

Named, **not scheduled** — the trigger is the owner's:

- **The wrong-artist clip in `BYP-13`.** Not path-quality work, not paused, and it means C1 is
  not fully closed. Highest priority here because it is a **live defect in the shipped app**
  that a Gate 2 user would meet, and the graph is not implicated.
- **Replay run 2's URL** to recover presses 41–100's lengths and card lists (`BYP-14`). No
  pressing, no ear, no rebuild — the data already exists.
- **A `known`-only run on the same pair**, to complete the factor: run 1 was mixed and run 2
  was pure `dislike`, so `known` alone has never been observed. **Prediction, fixed here before
  it runs:** `known` alone will reach a *shallower* floor than run 2's, because `dislike`'s
  advantage appears to be its live neighbourhood penalty against `known`'s inert floor device.
- **A second pair**, to test whether `BYP-11`'s genre-departure route is a property of the app
  or of this pair.
- **The clip-coverage look** (`BYP-12`), before Gate 2.
- **`BYP-8`'s length-vs-depth plot** against Track 2's committed walk data — now low value, but
  cheap and closes it.
