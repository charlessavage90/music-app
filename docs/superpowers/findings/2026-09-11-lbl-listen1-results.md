# `LBL-` listen 1 — the served map against `LBD-A0V`: result and read

**Role: AUTHORITATIVE for the `LBL-` listen-1 read.** This document **owns the listen-1
figures** — the tally, the per-pair breakdown and the ear-tracking counts. Every other
document cites it by section and does not restate its numbers. It owns **no map figures**:
those belong to
[`builder/analysis/2026-09-10-lbd-served-population/README.md`](../../../builder/analysis/2026-09-10-lbd-served-population/README.md)
and are cited by section here, never repeated.

**Raw data**, all in `builder/analysis/2026-09-10-lbd-blind-listen/`:
`lbl_listen1_verdicts.json` (the owner's saved picks and notes, exactly as the page wrote
them), `lbl_listen1_page_data.json` (the stimulus as presented), `lbl_listen1_result.json`
(the unblinded mapping and the mechanical tally).

**Governing document:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
— the **`LBD-AM5`** block at the end of §10, committed before any journey existed on any
map. **It wins wherever this note disagrees with it.** `LBD-AM5-5` fixes the read; this
note applies it and does not reinterpret it.

**Written by a session that did not run the listen and did not prepare it.** The preparing
session's record is
[`2026-09-10-lbd-listen-prep-execution-log.md`](../2026-09-10-lbd-listen-prep-execution-log.md);
the runner worked from `builder/analysis/2026-09-10-lbd-blind-listen/RUNNER-BRIEF.md` and
read nothing else.

---

## 0. The result, and what cuts against it

**The pre-registered read is `LBL-R2` — the tie.** Neither axis reached the margin bar of
8 fixed before any journey existed: coherence came out **+1** toward the challenger,
novelty **+1**. Both axes land on `no_detectable_difference`, and the branch's plain
sentence — frozen in the pre-registration, not written now — is:

> **"My ear cannot tell our recomputed lists from ListenBrainz's own."**

Per `LBD-AM5-5`'s own action column: **listen 2 becomes available, and spending it is the
owner's call.** `LBD-A0V` is now "a baseline no audibly worse than the served map *at this
instrument's resolution*, and nothing more." Nothing is adopted, no default changes, no
shipped code is touched.

**What cuts against reading this as a clean null:**

- **A tie is the outcome a weak instrument produces by default.** 24 rows per axis and a
  bar of 8 is a coarse instrument, and the owner marked **no preference on 11 of 24
  coherence rows and 15 of 24 novelty rows** — most often because both sides held artists
  he already knew, or because the journey was too short to differentiate.
- **Two of the eight pairs contributed almost nothing.** Built to Spill → Spoon produced
  no clear pick at all, on either axis at any depth, and The Naked and Famous → Band of
  Horses produced three. Both ran one or two interior artists per journey; his own pair
  note on the first reads *"Short paths, familiar artists. I think this pair was just too
  close together"*. The generation gate required an interior artist, not a journey long
  enough to hear (§4.1).
- **The one pair that moved decisively moved the challenger's way, and it is the obscure
  one.** The Litter → Night Moves gave the challenger all three coherence rows and drew
  the owner's only unprompted pair-level preference: *"strong preference for L overall in
  this set. L is what I'd want to see as an app user."* L was `LBD-A0V`. One pair of eight
  is not a margin and the read does not move — but a summary that omitted it would be wrong.
- **The tie is not "the two maps are the same map."** They are structurally very different
  — the challenger is markedly denser and strands far fewer of the app's own artists
  (served-population README §3 and §3a, figures owned there). The finding is that a large
  structural difference was **not audible on this instrument**, not that there is no
  difference.
- **And the challenger loses artists the served map keeps.** A body of served artists is
  absent from `LBD-A0V` altogether (§3, "served artists absent from the map"). None of them
  could appear in a journey the owner heard, so this listen says nothing about that cost,
  and it does not disappear because the listen tied.

---

## 1. Measured

### 1.1 The tally (`LBD-AM5-5`)

Challenger = `LBD-A0V`; incumbent = the served map, `graph-msw-tu50.bin`. 8 pairs × 3
depths = 24 rows per axis. A clear pick is left or right; *no preference* counts for
neither.

| axis | challenger | incumbent | margin toward challenger | bar | rows lost to a clip problem | verdict |
|---|---:|---:|---:|---:|---:|---|
| **coherence** (`LBL-Q1`) | 7 | 6 | **+1** | 8 | 0 | `no_detectable_difference` |
| **novelty** (`LBL-Q2`) | 5 | 4 | **+1** | 8 | 0 | `no_detectable_difference` |

**Listen read: `LBL-R2`** — neither axis *incumbent better*, neither *challenger better*,
no axis underpowered.

**The run state `LBD-AM5-5` requires is met**: all 24 rows answered on both axes and all
eight pair entries saved. `lbl_unblind.py` refuses a read otherwise, and the tally above
was reproduced by hand from `lbl_listen1_verdicts.json` and the unsealed mapping.

### 1.2 Per pair

Clear picks per cell, by role. The side labels the owner saw were shuffled per pair; seven
of the eight pairs happened to place the challenger on the left (§3).

| # | pair | coherence | novelty |
|---|---|---|---|
| 1 | The Spinto Band → Hozier | incumbent ×2 | incumbent ×1 |
| 2 | The Naked and Famous → Band of Horses | challenger ×2 | incumbent ×1 |
| 3 | The Litter → Night Moves | **challenger ×3** | incumbent ×2, challenger ×1 |
| 4 | Built to Spill → Spoon | — | — |
| 5 | Dope Lemon → Grizzly Bear | — | — |
| 6 | Sundara Karma → Modest Mouse | incumbent ×2 | challenger ×2 |
| 7 | The Mountain Goats → Manchester Orchestra | challenger ×2 | challenger ×1 |
| 8 | Songs: Ohia → Wye Oak | incumbent ×2 | challenger ×1 |

Slot 1's primary pair (MGMT → The Shins) was replaced mechanically by its first reserve,
The Spinto Band → Hozier, because the endpoints are directly connected in one map — the
pre-committed rule, applied before anything was shown to anyone.

### 1.3 Ear tracking — did any hidden metric predict his pick?

Recorded because `LBD-AM5-5` fixed it in advance; **it decides nothing**, and reading it as
deciding anything is barred (§5). For each row with a clear pick: did the side he picked
also win the hidden metric? Fame is mean interior fame percentile on the served map's fixed
ruler, so "lower" means the picked side's middle artists are less famous.

| axis | rows with a clear pick | fame lower | payload higher | top-1%-by-degree share lower | journey longer |
|---|---:|---:|---:|---:|---:|
| coherence | 13 | 5 | 4 | 5 | 3 |
| novelty | 9 | **7** | 2 | 3 | 3 |

The only count that departs from a coin flip is novelty against fame: on 7 of 9 rows where
he named a side as giving him more new artists, that side's middle artists were also less
famous on the fixed ruler. n = 9.

### 1.4 Clip problems: none

**Not one row of 24 was marked "a clip problem stopped me judging this row."** The
`LBL-R4` underpowered branch never came near firing. This is the direct measure of the
`CAU-` §2.3 correction carried into this protocol — up to three clips per artist, the
served map's recorded Deezer id for both sides — against `GBL-`, where five of seven
undecided deciding rows were undecided *because* of clip defects (`GBL-` results §0).

---

## 2. What I infer from it — in plain language

**Labelled as inference. The measurements are §1; disagree with this section freely.**

1. **If we rebuilt the app's similarity lists ourselves from ListenBrainz's raw listening
   data, using their own settings, the owner could not hear the difference.** He judged 24
   side-by-side rows on two questions without knowing which side was which, and came out
   one row apart on each. That is the whole finding.

2. **That is a genuinely useful answer, because the two maps are not close.** The map we
   built connects the same artists much more densely and leaves far fewer of them as dead
   ends (served-population README §3a). A change of that size passing unheard means the
   density we gained is **not** where the listening experience lives — at least not at the
   depths and pairs this listen covers.

3. **The one place he heard a difference is the place the app finds hardest.** The only
   pair that moved all three coherence rows runs between two artists most people have never
   heard of, and its journeys are long. There he preferred our recomputed map unprompted
   and said it was what he would want as a user. The pairs where he saw nothing were the
   ones running three or four steps between artists he already knows — where there is
   little to get right or wrong. **If the recomputation helps, this is a hint about where:
   long journeys through unfamiliar territory.** It is one pair of eight and carries no read.

4. **He found the novelty question hard to answer honestly, and said so three times.** *"I
   have to say R wins on novelty, but it's not a coherent path"*; *"I feel forced to say R
   wins on novelty… the problem is that the path on the right is not very coherent."* The
   question asks about new artists and he answered it as asked — but on those rows his
   coherence pick went the other way. The design anticipated exactly this (a split is a
   FAIL, because novelty is delivered through coherence, not traded against it), and no
   split occurred. **Worth keeping: on this instrument "more new artists" and "better
   journey" came apart, out loud, on three rows.**

5. **The instrument itself is now clean enough to be believed, and that is new.** No row
   was lost to a clip; the blind held. What limits this listen is its resolution and its
   pair draw, not a defect in the harness.

---

## 3. Weakest link

**The load-bearing assumption is that 24 rows at a bar of 8 can detect a difference the
owner's ear would actually care about.** The tie is consistent with "no difference" and
equally consistent with "a difference this instrument is too coarse to see". Two-thirds of
the novelty rows and nearly half the coherence rows were *no preference*, most of them
because both sides showed him artists he already knew.

**What would falsify it:** a listen on pairs chosen to be far apart and unfamiliar — the
conditions of pair 3 — coming out with a margin. If a re-drawn pair set moved past the bar,
this tie was an instrument limit rather than a fact about the maps.

**What I would defend:** the tally, the run state, and that `LBL-R2` is correctly applied.
`lbl_unblind.py` was checked against `LBD-AM5-5` clause by clause and the tally recomputed
by hand from the raw answers.

**What I would abandon cheaply:** any claim about *where* the recomputation helps. That
rests on one pair.

**One thing worth knowing about the randomisation.** The per-pair shuffle put the challenger
on the left in **seven of the eight pairs**. His raw picks leaned slightly right (13 right,
9 left across both axes), so any side preference he carried worked *against* the challenger
— which the challenger still edged by one on both axes. This changes no read and is not a
defect; it is recorded because a 7–1 split is worth naming before someone else finds it, and
because the next listen's shuffle is worth checking for balance rather than leaving to chance.

---

## 4. Instrument defects this run exposed, for the next listen

1. **The pair gate lets through pairs with nothing to judge.** Generation required an
   interior artist at each depth, not a journey long enough to have a shape. Two pairs
   produced three- and four-step journeys, and the owner said so unprompted on both. **A
   future draw should require a minimum interior length on both maps**, or exclude pairs
   within a few hops rather than only adjacent ones — `GBL-` results §6.5 asked for the
   adjacency exclusion and got it; this is the same defect one hop further out.
2. **Familiarity, not clips, is what now costs rows.** The rows he could not call were
   mostly rows where he knew everyone on both sides. A future draw wanting resolution should
   select for unfamiliar interiors, which is a property of the *pair*, not of the protocol.
3. **The two questions can conflict on the same row, and the protocol has nowhere to record
   it.** He used the free-text notes for it three times. The notes were read; a future
   protocol could ask directly (*"did you have to trade one against the other on this
   row?"*) rather than relying on a listener who happens to explain himself.
4. **Three clips per artist fixed the clip problem.** Carry it forward unchanged.

---

## 5. Barred reads — what this listen cannot support

Taken from `LBD-AM5-5`'s own barred list, plus `LBD-X4` and `LBD-X5`.

- **No attribution to "the data", and none inside it.** The gap between the served map and
  `LBD-A0V` bundles a corpus roughly three times the size, the absent `filter_True` stage,
  today's msid→mbid mapping, the uncredited band-member class and our tie-break (`LBD-X5`).
  **No sentence may credit or blame any one of them.**
- **`LBD-X4` travels with every listen-1 verdict.** 439 artists took part in the served
  build's cap step and could not in `LBD-A0V`'s, because the emitter never writes them. No
  sentence may attribute a listen-1 verdict to "the similarity data" without naming this
  term beside it.
- **"The two maps are equivalent" is barred** (`REQ-41`): no difference in unfamiliar
  territory is uninformative, not evidence of equivalence — and most of the undecided rows
  sit in *familiar* territory, which is worse for the inference, not better.
- **"Our recomputation passed its listen" is barred.** It did not pass; it tied. **"It
  failed" is equally barred** — the served map did not win either.
- **No transitive claim across the two listens**, if listen 2 is ever run: a listen-2 PASS
  would not say `LBD-A5V` beats the served map.
- **No adoption on this outcome.** `S4` owns adoption, the population rule, API sizing, the
  fame source and a refresh procedure. **`V` is an experimental control, not a population
  rule.**
- **No re-listen of this verdict** — `GBL-` §5's run-once rule binds it.
- **The hidden metrics in §1.3 decide nothing**, including the 7-of-9 fame count.

---

## 6. What this leaves open — the owner's, not a session's

- **Listen 2** (`LBD-A0V` against `LBD-A5V`, the two-listener bar) is now *available*. Its
  pairs are already fixed and its map is built; its materials are not prepared, and
  preparing them is his trigger.
- **`LBD-D6` is still unruled.** `LBD-A4` was to run before any further arm was
  pre-registered, and `LBD-A5` was registered without it. Listen 1 does not touch `LBD-A5V`
  and is unaffected; **listen 2 is entirely about it.**
- **Stopping here is a complete outcome**, not an abandonment: the supply question is
  answered at the table level, at the map level, and now at the ear.
