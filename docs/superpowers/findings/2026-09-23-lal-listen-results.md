# `LAL-` blind listen — today's served map against the `LBA-A6` candidate: result and read

**Role: AUTHORITATIVE for the `LAL-` listen's read, and it OWNS that listen's figures**: the tally,
the per-pair and per-depth breakdowns, the identification, strength and known-everyone counts,
the ear-tracking counts, and the sealed per-map metrics. Every other document cites it by section
and does not restate its numbers. It owns **no map figures** (the candidate's README owns those)
and **no pre-screen figures** (`lal_am7_prescreen.md` owns those).

**Raw data**, all in [`builder/analysis/2026-09-22-lba-a6-blind-listen/`](../../../builder/analysis/2026-09-22-lba-a6-blind-listen/):
`lal_verdicts.json` (his saved answers and notes, exactly as the page wrote them, committed by the
runner at `c62bdf2`), `lal_page_data.json` (the stimulus as presented), `lal_pairs.json` (the pairs,
sha-pinned), and `lal_result.json` (the unblinded mapping and the mechanical tally, written by
`lal_unblind.py` in this session). The sealed mapping and hidden metrics (`.superpowers/lal/`) are
gitignored and stay in the runner's worktree; §1.5 reports what they held.

**Governing document:**
[`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../specs/2026-09-14-lbd-s4-adoption-preregistration.md)
§11, **`LBA-AM6`** (the listen's design, committed 2026-09-22 before any journey existed) **as amended
by `LBA-AM7`** (2026-09-23: the pair pool only). **They win wherever this note disagrees.** This note
applies `LBA-AM6-7`'s read and `LBA-AM6-8`'s descriptive reads. It does not reinterpret them.

**Written by the fresh write-up session `LBA-AM6-5` requires.** It did not prepare the listen or run it.
It read the governing amendments, the harness source and the preparation handoff, then ran
`lal_unblind.py` after the runner's commit of the complete verdicts.

**The identifiers used below, each with the plain sentence the pre-registration fixed for it:**

| id | plain sentence |
|---|---|
| **served map** / incumbent | today's map, `graph-msw-tu50.bin`: the map the site routes on |
| **candidate** / challenger | the new map, `LBA-A6-candidate.bin`: the one adoption would ship |
| `LAL-Q1`, coherence | *"At this point, which side holds together better as a journey — each step a sensible next listen?"* |
| `LAL-Q2`, novelty | *"At this point, which side gives you more artists that are new to you?"* |
| `LAL-Q3` | how strong a pick was: slight or strong |
| `LAL-Q4` | *"On this row, can you tell which side is the new map?"* |
| `LAL-K` | *"Every artist that differed between the two sides was already known to me"* |
| d0 / d10 / d20 | the first path you see / after ten presses of "Dig deeper" / after twenty |
| `LAL-R1` PASS | *"Journeys on the new map are better on [axis], and no worse on the other."* |

---

## 0. The result, and what cuts against it

**The pre-registered read is `LAL-R1`, PASS, on coherence.** The frozen sentence with its axis
filled in reads:

> **"Journeys on the new map are better on coherence, and no worse on the other."**

- **Coherence** (which side holds together better as a journey): **13 clear picks for the new map,
  2 for today's map**, 9 no preference. The margin of **11** clears the bar of **8** fixed before any
  journey existed, so this axis reads *candidate better*.
- **Novelty** (which side gives more artists new to him): **8 and 8**, 8 no preference. Margin **0**,
  so *no detectable difference*.
- **No row was lost to a clip problem**: the clip box was ticked on none of the 24 rows. The
  underpowered branch (`LAL-R4`, too many rows lost to clip problems to read) could not fire.

**"No worse on the other" is the frozen sentence, and `REQ-41` limits it.** On novelty the instrument
could not separate the maps at this margin on these pairs. That is **not** evidence that the new map
gives as many new artists as today's map (`LBA-AM6-10`: no "equivalent" from a tie, applied here to
the tied axis).

**What cuts against it. All of this is descriptive, and none of it changes the read (`LBA-AM6-8`):**

1. **Every row that traded one axis against the other traded in the same direction.** On 5 of 24
   rows he picked opposite sides on the two questions. On all 5, **the new map was the more coherent
   side and today's map the more novel one** (§1.3). In those rows, where he felt a choice between
   the two, the new map held together and today's map gave him more new names. The pre-registration
   counts a split as FAIL only at the level of a whole axis (`LBA-AM6-7`), which did not happen here.
   Row-level trades are reported and do not decide anything.
2. **The new map's journeys stayed among better-known artists, and it put fewer unfamiliar artists
   in front of him.** This held at every depth, and the fame gap was widest after twenty presses
   (§1.5). The same data can be read two ways: the coherence win could be partly the familiar route
   holding together, or the new map could be genuinely better at coherence. This listen cannot
   separate them (§3).
3. **He identified the new map on 3 rows, correctly each time, and all three were coherence picks
   for it** (§1.4). By `LBA-AM6-8`, identified rows count in full; this note does not discount them.
   How much weight that leaves the verdict is his call.
4. **One artist with no clip, Ed O'Brien, appeared only on today's map, in 3 rows. Those are exactly
   the 3 rows he identified, and all 3 were coherence picks for the new map** (§1.6). He did not tick
   the clip box on any of them, and his notes cite Ed O'Brien as his clue to which side was today's map.
   The clip rule was the same for both maps (`LBA-AM6-6`). Ed O'Brien had no clip because of who he is,
   not because of which map showed him. Whether a card with no clip weighed on his coherence pick on
   those rows cannot be recovered from the record.
5. **Most coherence picks were slight: 10 of 13** (§1.4).

**Where the evidence points the other way (toward a genuine coherence difference):** the new map's
coherence picks came from **all eight pairs**, so they are not concentrated in one or two (§1.2).
Of the 3 rows where he identified a side, 2 are among the 5 trade-off rows above, where the side he
identified won coherence and lost novelty. That is not the pattern of a listener favouring the side
he believed to be new. **And of the 11 places where his notes name a specific artist or step as out of place, 9 are on
today's map** (§2).

---

## 1. Measured

### 1.1 The tally (`LBA-AM6-7`)

| axis | rows | new map | today's map | no preference | margin toward new map | bar | clip-blocked no-preference rows | axis verdict |
|---|---|---|---|---|---|---|---|---|
| coherence | 24 | 13 | 2 | 9 | **+11** | 8 | 0 | **candidate better** |
| novelty | 24 | 8 | 8 | 8 | **0** | 8 | 0 | no detectable difference |

**Read: `LAL-R1`.** No axis went to today's map, and one went to the new map. Every row was complete on
both axes, `LAL-Q3` was given wherever owed, `LAL-Q4` was answered on every row, and all eight
pair-end entries were saved. `lal_unblind.py` refuses to read anything less (`LBA-AM6-7`'s run state).
Its verdict is tested invariant to every assignment of `LAL-Q3`, `LAL-Q4` and `LAL-K`, and the
56 harness tests passed in this session before it ran. **No substitution fired**: the eight primaries
are the eight pairs he heard. The sides were dealt 4–4.

**Map identity, checked in this session:** both artifacts' sha256 match the shas recorded in their
manifest sidecars and in the sealed pin.

### 1.2 Per pair (descriptive)

`new` = the new map, `today` = today's map, `—` = no preference. Each cell gives coherence / novelty.

| # | pair | d0 | d10 | d20 | pair-end: *"did either side collapse into a random walk into obscurity?"* |
|---|---|---|---|---|---|
| 1 | St. Paul & The Broken Bones – Journey | — / today | new / new | new / today | *"Possibly R at hop 20"*, where **R was today's map** |
| 2 | Lake Street Dive – Unwritten Law | new / today | — / — | — / new | — |
| 3 | Orville Peck – Best Coast | — / new | new / new | new / — | — |
| 4 | U2 – Day Wave | new / new | new / new | new / — | — |
| 5 | Daryl Hall & John Oates – Cold War Kids | — / — | — / today | new / today | — |
| 6 | Bruce Springsteen – DISPATCH | — / today | new / today | — / — | — |
| 7 | Beck – J. Cole | today / — | today / — | new / today | — |
| 8 | The Gaslight Anthem – Alabama Shakes | — / — | new / new | new / new | — |

He left every pair-end notes box empty. **The only collapse he flagged was a possible one, on today's
map, after twenty presses.** The new map's coherence picks cover all eight pairs. Both of today's map's
coherence picks came from pair 7.

### 1.3 Per depth, and the trade-off rows (descriptive)

| depth | coherence: new / today / — | novelty: new / today / — |
|---|---|---|
| d0 | 2 / 1 / 5 | 2 / 3 / 3 |
| d10 | 5 / 1 / 2 | 4 / 2 / 2 |
| d20 | 6 / 0 / 2 | 2 / 3 / 3 |

**The per-depth split is a count and supports no attribution.** `LBA-AM6-1` bars any sentence
attributing a d10 or d20 difference to the press ramp, the fame ranking or any single recomputed
quantity. The listen hears their joint effect and cannot separate them.

**Trade-off rows:** 5 of 24 (pair 1 d20, pair 2 d0, pair 5 d20, pair 6 d10, pair 7 d20). **On all five,
coherence went to the new map and novelty to today's map.**

### 1.4 Identification, strength and known-everyone (`LBA-AM6-8`, which decides nothing)

**`LAL-Q4`: could he tell which side was the new map?**

| depth | no | yes, and right | yes, and wrong |
|---|---|---|---|
| d0 | 8 | 0 | 0 |
| d10 | 7 | 1 | 0 |
| d20 | 6 | 2 | 0 |

He identified 3 rows: pair 4 d10, pair 5 d20 and pair 7 d20. His picks on them were new/new,
new/today and new/today (coherence / novelty). In his notes, the clue each time was an artist on today's
map. On pair 4 d10, he suspected today's map *"due to the appearance of Ed O'Brien and Albert Hammond,
Jr. as mid-path artists"*. On pair 5 d20, *"Ed O'Brien and Andrew VanWyngarden showing up is a sign to
me that R is the current map"*. **The membership tell (`LBA-X10`: a row identifiable because it shows an
artist today's map cannot contain) could not operate.** None of the 162 cards the new map presented was
an artist absent from today's map (§1.5, checked directly against the artifact in this session).

**`LAL-Q3`: strength of clear picks.**

| axis | slight: new / today | strong: new / today |
|---|---|---|
| coherence | 10 / 2 | 3 / 0 |
| novelty | 8 / 7 | 0 / 1 |

**`LAL-K`: every differing artist already known to him.** Ticked on 4 rows (d0: 1, d10: 2, d20: 1).
Of those, 3 were no-preference rows on coherence and 4 on novelty.

### 1.5 The sealed per-map metrics (`LBA-AM6-5`), and whether any tracked his picks

Summed or summarised over the eight pairs. Fame is on **the new map's own fame percentile**, the only
ruler covering every artist either side can present (`LBA-AM6-5`). The median is over the eight
journeys' mean interior fame.

| depth | map | mean length | median interior fame | differing artists absent from his familiarity list, summed | presented artists outside today's map | mean top-1%-by-degree interior fraction |
|---|---|---|---|---|---|---|
| d0 | today | 7.1 | 0.961 | 37 | 0 | 0.425 |
| d0 | new | 7.3 | 0.975 | 31 | 0 | 0.451 |
| d10 | today | 7.1 | 0.919 | 39 | 0 | 0.407 |
| d10 | new | 6.6 | 0.966 | 31 | 0 | 0.435 |
| d20 | today | 6.8 | 0.871 | 35 | 0 | 0.400 |
| d20 | new | 6.4 | 0.982 | 28 | 0 | 0.356 |

**`LBA-X9` disclosed a lean it expected the selection to have, and the lean did not appear.** It
expected the pairs to lean toward ones where the new map routes through artists it adds. On these
pairs the new map presented **none**. So the unfamiliar artists that made the pairs pass the
pre-screen came from the two maps choosing different routes through shared artists, not from the
new map's additions. **The bar `LBA-X9` set still stands in full** (§5).

**Ear tracking.** For each clear pick, did the picked side also win each hidden metric?

| axis | clear picks | picked side lower fame | picked side more non-hub interior | picked side lower top-1%-degree fraction | picked side longer | picked side more artists outside today's map |
|---|---|---|---|---|---|---|
| coherence | 15 | 4 of 15 | 8 | 10 | 2 | 0 |
| novelty | 16 | 10 of 16 | 7 | 6 | 9 | 0 |

**Descriptive only.** No threshold and no branch reads any of this (`LBA-AM6-10`).

### 1.6 Clips

**Clip coverage by map: today's map 4 of 168 card slots with no clip; the new map 1 of 162.** The five were
Ed O'Brien, 3 times, all on today's map (pair 4 d10, pair 5 d20, pair 7 d20, which are the three rows
he identified), and Edward Sharpe and the Magnetic Zeros, twice, once per map (pair 8 d10 on today's
map, pair 5 d0 on the new map). Every "no clip found" card said so, as `LBA-AM6-4` requires. He ticked the clip-problem box on no
row. On one row (pair 5 d10) his note says a single-clip artist was *"tough to judge ... but not enough
to say 'a clip problem stopped me judging this row'"*.

---

## 2. What I infer from it, in plain language

*Inference, labelled as such. You can disagree with any sentence here.*

**Here is what you would see on the eight pairs, both of whose endpoints you know.** You were shown the
two maps' journeys side by side with no labels. Asked which side holds together better as a sequence of
listens, you picked the new map's side 13 times and today's map's side twice. Mostly the difference was
slight, and it came from every pair. At the first path, you mostly had no preference (5 of 8). It was
after pressing "Dig deeper" ten or twenty times that you usually preferred the new map's journey.
Asked which side gave you more new artists, the two maps came out even.

**Your own notes say what the difference sounded like.** Your notes name a specific artist or step
as out of place in 11 places, and **9 of those 11 are on today's map** (each checked against the
stimulus):

- Roy Bittan (pair 1, d10)
- the Macklemore → Nathan East → Bill Wolfer chain (pair 1, d20)
- Of Monsters and Men → The Neighbourhood (pair 2, d0)
- Luke Wood (pair 2, d20)
- Weyes Blood next to Orville Peck (pair 3, d0)
- Sevdaliza next to Orville Peck (pair 3, d10 and d20)
- Kendrick Lamar and SZA (pair 4, d20)
- Geezer Butler (pair 6, d10)

The two on the new map were AURORA → Bring Me the Horizon (pair 2, d20) and Noah Cyrus next to Orville
Peck (pair 3, d0), which you say a third clip resolved. *(Your pair-3 d20 note says Sevdaliza was
"still present on the R". The stimulus puts her on the left, today's map, at both d10 and d20, and
your pick that row was the right side, the new map. The pick is what counts. The note is recorded as
a slip.)* Several of today's map's out-of-place entries were **session players, or band members with
solo credits**: Roy Bittan, Nathan East, Bill Wolfer, Geezer Butler, and the three you used as your
clue to which side was today's map, Ed O'Brien, Albert Hammond Jr. and Andrew VanWyngarden.
Your one "collapse" flag was on today's map after twenty presses.

**What cuts against this, in the same terms:** after many presses, the new map's journeys kept to
better-known artists than today's map. On the five rows where you felt one side was more coherent and
the other gave you more new names, the new map was the coherent one every time. So one reading is that
the new map holds together better **partly by staying closer to familiar ground**. It did not cost
novelty overall, since novelty tied, but it did on the rows where you traded.

**My read, which is inference, not a verdict:** the coherence result looks like a real difference in
how the two maps behave after presses. Today's map more often drops in an artist from outside the
style, frequently a player credited on someone else's record, and the new map does that less. Whether
the new map buys some of that by going less deep into unknown territory is exactly what this listen
cannot tell.

---

## 3. Weakest link

**The load-bearing assumption is that the coherence picks reflect the maps and not what came with
them.** Three things came with them, and none can be separated in this record:

- **Fame.** The new map stayed with more famous artists after presses (§1.5). Journeys between
  better-known artists may hold together better simply because they are better-known. **What would
  falsify the "real difference" reading:** a listen whose pairs are matched on fame across the two
  sides, where the coherence gap disappears. That would be a new amendment on new pairs
  (`LBA-AM6-9`), not a re-read of this one.
- **Identification.** 3 rows were identified, all correctly, all pro-new-map on coherence. The margin
  is 11 against a bar of 8.
- **The clipless card.** Ed O'Brien had no clip, appeared only on today's map, and was on 3 rows that
  went to the new map on coherence. They are the same three rows as the identified ones, so these two
  points are one exposure, not two.

**What I would defend:** that the read is `LAL-R1`, correctly computed from a complete run under the
pre-registered rule; that the coherence picks are spread across all eight pairs; that the membership
tell could not operate; that no row was lost to clips. **What I would abandon cheaply:** any story
about *why* the new map is more coherent. The fame and session-player readings in §2 are
interpretations of descriptive data, and the pre-registration bars attributing the result to any one
cause.

---

## 4. Instrument defects this run exposed, for any future listen

1. **The extended-history familiarity list still under-reads what he knows.** Gate N required at least
   one differing artist absent from his whole Spotify history at every depth, yet he ticked
   known-everyone on 4 rows. An artist he never streamed on Spotify can still be one he knows. Any
   future listen should expect `LAL-K`-style residue even from a complete streaming history.
2. **A card with no clip can be a side-specific tell, even under an artist-keyed clip rule.** If an
   artist with no clip appears on only one side, the gap marks that side. That is what happened with
   Ed O'Brien here. A future pre-screen could count single-side, clipless artists per row. Deferred with
   a success condition: this is done when the next listen's pre-registration either adds that count or
   states why not.
3. **Pair-end notes went unused.** He wrote row notes on 22 of 24 rows and left all eight pair-end notes
   boxes empty. The row notes carried §2's evidence. The pair-end box adds little and could be dropped.

---

## 5. Barred reads: what this listen cannot support (`LBA-AM6-9`, `LBA-AM6-10`)

- **No attribution to any one column or subset** of what distinguishes the maps: threshold, population,
  payload, fame date, data source, or any one component of the data bundle. The verdict is about the
  new map **as a whole** against today's.
- **No attribution of the d10/d20 pattern** to the press ramp, the fame ranking or any single recomputed
  quantity.
- **No generalisation to the typical journey.** The verdict holds for **pairs on which the two maps
  differ at every depth in artists he does not know** (`LBA-X9`), drawn from artists he vetted as known
  (`LBA-AM7`). It also does not generalise to the cheaper pairing form.
- **No "the new map is as novel as today's"** from the novelty tie (`REQ-41`).
- **No descriptive or sealed quantity decides anything**: identification, strength, known-everyone,
  trade-off rows, fame, clips.
- **Run-once and final.** No re-listen, and no re-tally on strength, identification or familiarity.
  The verdict is not re-read after `LBA-G5`, the owner's two days of use against his own criterion.
- **Nothing carries across listens.** Listens 1 and 2 (both ties) say nothing about the candidate, this
  says nothing about their comparisons, and no transitive claim may be built across the three. It says
  nothing about `LBA-A3`, other thresholds, maps not built, or `LBA-R9`.
- **This verdict is not evidence about `LBA-G5`'s criterion, and a `LBA-G5` outcome does not re-read it.**

---

## 6. What this leaves open. These are the owner's calls, not a session's

**What PASS licenses, quoted from `LBA-AM6-7`:** *"the ear evidence `REQ-38` asks for, on these pairs,
favours the candidate. `LBA-G5` runs next (`LBA-AM5`)."* It recommends nothing and adopts nothing.

- **How much weight the verdict carries**, with §0's five counter-points in front of him: the one-way
  trade-off rows, the fame gap, the 3 identified rows and the clipless card (the same three rows),
  and the mostly slight picks.
  This is his because `LBA-AM6-8` assigns that weighing to him by name.
- **Running `LBA-G5`**: the owner's two days of use against his own criterion, logging every artist
  pair he uses. This is next in `NEXT.md`'s sequence and needs his time and his use of the app.
- **Adoption**: his, after `LBA-G5`. If the candidate is not adopted, `NEXT.md`'s warning about
  restoring `acceptance.py`'s previous line before rebuilding either map applies.
