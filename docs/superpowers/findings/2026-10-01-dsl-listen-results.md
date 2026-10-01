# `DSL-` blind listen — today's app against `DRP-S1P3` after several presses: result and read

**Role: AUTHORITATIVE for the `DSL-` listen's read (stage 5 of the #200 depth remedy), and it OWNS that
listen's figures**: the tally, `DSL-P`'s and `DSL-E`'s counts, the identification, strength and
known-everyone counts, the ear-tracking counts and the sealed per-side metrics. Every other document
cites it by section and does not restate its numbers. It owns **no lattice figures** (the results note
[`2026-09-28-drp-lattice-results.md`](2026-09-28-drp-lattice-results.md) owns those) and **no pre-screen
figures** (`dsl_prescreen.md` owns those).

**Raw data**, all in
[`builder/analysis/2026-09-30-drp-stage5-listen/`](../../../builder/analysis/2026-09-30-drp-stage5-listen/):
`dsl_verdicts.json` (his saved answers, marks and notes, exactly as the page wrote them, committed by the
runner at `f6f074b`), `dsl_page_data.json` (the stimulus as presented), `dsl_pairs.json` (the pairs,
sha-pinned `34699ace…`), `dsl_result.json` (the unblinded mapping and the mechanical reads, written by
`dsl_unblind.py` in this session, run once), and `dsl_sealed_summary.json` (§1.6's sealed metrics,
written by `dsl_sealed_summary.py`, added by this session; it reads no answer file). The sealed mapping
and per-journey metrics (`.superpowers/dsl/`) are gitignored and stay in the runner's worktree.

**Governing document:**
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
§14, **`DRP-AM7`** (designed cold and committed 2026-09-30 before any journey existed), including its
seam-5A review. **It wins wherever this note disagrees.** This note applies `DRP-AM7-7`–`-10` and states
`DRP-AM7-11`'s bars. It does not reinterpret them.

**Written by the fresh write-up session `DRP-AM7-5` requires.** It did not design, prepare or run the
listen, and saw no journey or side-labelled output before the unblind. Preconditions checked before the
run: the runner's commit is pushed (`f6f074b` = `origin/dsl-listen-run`); the sealed `pairs_file` sha
equals `DSL_PAIRS_SHA`; all 24 of 24 rows complete by the harness's own `row_complete`.

**The identifiers used below, each with its plain sentence:**

| id | plain sentence |
|---|---|
| **today's app** / incumbent | the app as it runs now: today's map (`graph-lba-a6.bin`, sha `28311d81…`), no per-press device |
| **the candidate** / challenger, `DRP-S1P3` | today's router on the map with the extra connections (`graph-drp-s1.bin`, sha `418fe666…`), plus the ceiling: from press 4, a cap on how famous a middle artist may be, falling as you press |
| `DSL-Q1`, coherence | *"At this point, which side holds together better as a journey — each step a sensible next listen?"* |
| `DSL-Q2`, novelty | *"At this point, which side gives you more artists that are new to you?"* |
| `DSL-Q3` | how strong a pick was: slight or strong |
| `DSL-Q4` | *"On this row, can you tell which side is the new version?"* |
| `DSL-K` | *"Every artist that differed between the two sides was already known to me"* |
| `DSL-M` | his *"I know this artist"* mark on a middle card |
| `DSL-W` | his *"this step doesn't fit"* mark between two adjacent cards |
| d5 / d10 / d20 | the journey after five / ten / twenty presses of Dig deeper |
| `DSL-R3` FAIL | *"After several presses, today's app gives better journeys on [axis]."* |
| `DSL-P` | *of the less-famous artists the candidate put in the middle of journeys after pressing, does he already know most of them?* |
| `DSL-E` | *when a step doesn't fit on the candidate side, is it mostly the step off a famous endpoint?* |
| `DRP-T1` / `DRP-T2` | the top fame tier / the next tier down, as the lattice bounds them |

---

## 0. The result, and what cuts against it

**The pre-registered read is `DSL-R3`, FAIL, on coherence.** The frozen sentence with its axis filled in:

> **"After several presses, today's app gives better journeys on coherence."**

- **Coherence** (which side holds together better as a journey): **15 clear picks for today's app, 2
  for the candidate**, 7 no preference. Margin **13 toward today's app**, past the bar of **8** fixed
  before any journey existed: *today's better*.
- **Novelty** (which side gives more artists new to him): **24 clear picks for the candidate, 0 for
  today's app**, 0 no preference. Margin **24 toward the candidate**: *candidate better*.
- **This is a split, and `DRP-AM7-7` reads a split as FAIL deliberately**: *"A novelty win beside a
  coherence loss is the failure this remedy is most likely to produce, and it reads FAIL, in those
  words."* That is what happened.
- **No row was lost to a clip problem**: the clip box was ticked on none of the 24 rows. The
  underpowered read (`DSL-R4`, *"Too many rows were lost to clip problems to read this listen"*) could
  not fire.

**What `DSL-R3` licenses (`DRP-AM7-7`), and nothing more:** *"`REQ-38` bars any offline figure from
overriding it. What follows is his."* The use gate, adoption, and anything else are the owner's.

**The two side reads, each independent of the verdict and of each other (`DRP-AM7-8`/`-9`):**

- **`DSL-P` does not fire.** *"Most of the less-famous artists the candidate put in the middle were new
  to me."* 24 of 153 marked known (§2).
- **`DSL-E` does not fire.** *"The candidate's weak steps are not mostly at the ends."* 13 of 43 weak-step
  marks on the candidate side were end steps (§3).

**What cuts against the headline. All descriptive; none of it changes the read (`DRP-AM7-10`, `-11`):**

1. **He could tell which side was new on almost every row.** `DSL-Q4`: identified correctly on **21 of 24**
   rows, wrongly on 1, not at all on 2 (§1.3). His own note on Dr. Dog → Matisyahu says *"the new version
   (easy to identify)"*. The blind was effectively open, through the tell `DRP-X9` disclosed in advance
   (longer journeys, no stars). The verdict counts every row in full, as pre-registered. Whether a
   coherence judgement made knowing which side is new carries the same weight is his call.
2. **One pair went the other way, in his own words.** On Dr. Dog → Matisyahu he wrote: *"all the pairs
   prior to this, the new version … really dropped coherence in very noticeable ways. I didn't see that
   in this pair … I would have preferred to get the new version journeys at depth as an app user"*
   (§1.7). His picks there agree: coherence went to the candidate at d5, no preference at d10 and d20.
   This is one pair. It is from `DRP-T2`, and `DRP-X8` bars both a per-tier read and counting `DRP-T2`
   rows as evidence about the extra connections, so it supports no claim beyond itself.
3. **One coherence pick was made with a card he could not hear.** On Grimes → The Police at d20 he
   wrote that the missing clip for T.P.H. Productions on the candidate side *"makes it tough to tell
   whether the left side somehow got coherently connected"*. He picked today's app on coherence there
   and did not tick the clip box. Removing that row would leave the margin at 12, still past 8. This
   is arithmetic for orientation, **not a re-tally**: the read stands as run (`DRP-AM7-11`).
4. **The candidate's journeys are longer**, a median of 8 to 10.5 cards against today's 6 (§1.6). A
   longer journey has more steps that can fail to fit. The listen cannot separate *"the candidate's
   steps fit worse"* from *"the candidate has more steps"*: the question asked about the journey as a
   whole, which is what a user gets.

---

## 1. The verdict in detail

### 1.1 The tally (`DRP-AM7-7`)

| axis | rows | clear picks, candidate | clear picks, today's app | no preference | margin toward candidate | clip-blocked no-preference rows | bar | per-axis read |
|---|---|---|---|---|---|---|---|---|
| coherence | 24 | 2 | 15 | 7 | −13 | 0 | 8 | today's better |
| novelty | 24 | 24 | 0 | 0 | +24 | 0 | 8 | candidate better |

Read: **`DSL-R3`** (either axis *today's better*, including a split). No substitutions were made at
generation; the eight pairs presented are `dsl_pairs.json`'s primaries after his strike, four `DRP-T1`
and four `DRP-T2`.

### 1.2 `DSL-Q3`, pick strength — decides nothing

| axis | strong, candidate | slight, candidate | strong, today's | slight, today's |
|---|---|---|---|---|
| coherence | 0 | 2 | 14 | 1 |
| novelty | 22 | 2 | 0 | 0 |

`DRP-AM7-11` bars re-tallying on strength.

### 1.3 `DSL-Q4`, identification — decides nothing

| depth | could not tell | told, correctly | told, wrongly |
|---|---|---|---|
| d5 | 1 | 7 | 0 |
| d10 | 1 | 6 | 1 |
| d20 | 0 | 8 | 0 |

It never enters the tally, and `DRP-AM7-11` bars re-reading the verdict on it.

### 1.4 `DSL-K` and the trade-off rows — decide nothing

- `DSL-K` (*every differing artist already known to me*): ticked on **0** rows.
- **Trade-off rows** (coherence and novelty picked opposite sides): **15 of 24**. Because every novelty
  pick went to the candidate, these are exactly the rows where coherence went to today's app.

### 1.5 Ear tracking — decides nothing, and barred from being read as what his ear responded to

Defined as `DRP-AM7-10` fixes it: over the rows with a clear pick on an axis, how often the picked side
also had the lower mean interior fame, the longer journey, or more added connections traversed.

| axis | rows with a clear pick | picked side lower fame | picked side longer | picked side more added connections |
|---|---|---|---|---|
| coherence | 17 | 2 | 2 | 0 |
| novelty | 24 | 24 | 19 | 12 |

### 1.6 The sealed per-side metrics (`DRP-AM7-5`) — decide nothing

From `dsl_sealed_summary.json`. Fame is `fame_lb_pctl`, one ruler for both sides (`DRP-G3`); no interior
artist on either side was unmeasured.

| side | depth | median of each journey's mean interior fame | median cards (endpoints included) | journeys using an added connection | added connections used, total | ceiling `c` | journeys with the ceiling relaxed |
|---|---|---|---|---|---|---|---|
| today's app | d5 | 0.9939 | 6 | 0 of 8 | 0 | — | — |
| today's app | d10 | 0.9964 | 6 | 0 of 8 | 0 | — | — |
| today's app | d20 | 0.9961 | 6 | 0 of 8 | 0 | — | — |
| candidate | d5 | 0.8877 | 8 | 4 of 8 | 4 | 0.97 | 0 |
| candidate | d10 | 0.7656 | 9 | 4 of 8 | 5 | 0.895 | 0 |
| candidate | d20 | 0.6348 | 10.5 | 4 of 8 | 7 | 0.745–0.868 | 3 |

**Clips.** Today's app: 143 card slots, none without a clip. Candidate: 221 slots, 3 without a clip.
**Artists with no clip appearing on only one side**, per row (#137's sealed count): 1 on Grimes → The
Police at d20, 1 each on GROUPLOVE → Dire Straits at d10 and d20; 0 on every other row. All three are on
the candidate side.

### 1.7 His row notes, verbatim — decide nothing

Quoted exactly. The side in brackets is resolved from the unsealed mapping by this session.

- **Grimes → The Police, d10:** *"The wording / placement of "This step doesn't fit" is a little
  confusing. I'm checking the box between the two artists that don't fit, so Jean‐Michel Jarre -> The
  Police, just for clarity. That will be how I do it throughout"*. This bears on `DSL-W`'s meaning: §3.
- **Grimes → The Police, d20:** *"No clip for T.P.H. Productions makes it tough to tell whether the left
  side somehow got coherently connected to the police."* [left = the candidate]
- **GROUPLOVE → Dire Straits, d10:** *"No clip for Snowy White and the White Flames"*.
- **Fleet Foxes → Rush, d20:** *"Fleet Foxes to Mt Joy is better than Fleet Foxes to Alt-J, but other
  than that, R makes little sense"*. [R = the candidate]
- **Dr. Dog → Matisyahu, d20:** *"Feedback on this pair overall - all the pairs prior to this, the new
  version (easy to identify) really dropped coherence in very noticeable ways. I didn't see that in this
  pair. There were a few steps that seemed out of place, but overall, the journeys on both sides held
  together, and I would have preferred to get the new version journeys at depth as an app user"*.
- **Badfinger → Future Islands, d5:** *"R took a big detour into movie scores and video game music."*
  [R = the candidate]

---

## 2. `DSL-P`, the fame-proxy read (`DRP-AM7-8`)

**Population:** every distinct middle artist on the candidate side at d5, d10 or d20 that appears on no
today's-app card of the same row. **n = 153.** Known (marked on any card where the artist appears):
**24**. Firing needs ⌊153/2⌋ + 1 = **77**.

**Outcome: does not fire.** *"Most of the less-famous artists the candidate put in the middle were new to
me."*

**What it licenses, per `DRP-AM7-8`:** *"By his rule the proxy fix does not go first. That is **not**
evidence that the fame proxy ranks correctly: it says only that on these journeys the artists it demoted
were mostly new to him."*

⚑ **`dsl_result.json`'s `licenses` field for `DSL-P` reads "a proxy fix goes first, with the lattice
re-run"** regardless of outcome. It is a static string describing what firing would license, and it does
not apply here: the read did not fire. `DRP-AM7-8` governs, as quoted above. The harness is not edited
after its run: the result file is the record of what the instrument wrote.

**Artists marked known on some cards and not others: 3.** They count as known (*"on any card"*).

**"The band that matters", reported beside it, deciding nothing.** Known share within each
`fame_lb_pctl` band; rows sum to n.

| band | candidate-only: n | known | today's-only (reference): n | known |
|---|---|---|---|---|
| below 0.60 | 17 | 0 | 0 | 0 |
| [0.60, 0.70) | 22 | 1 | 0 | 0 |
| [0.70, 0.80) | 31 | 2 | 1 | 1 |
| [0.80, 0.90) | 59 | 15 | 2 | 2 |
| [0.90, 0.99) | 24 | 6 | 11 | 6 |
| 0.99 and above | 0 | 0 | 69 | 59 |
| unmeasured | 0 | 0 | 0 | 0 |
| **total** | **153** | **24** | **83** | **68** |

His observation that prompted this read is recorded in `exploration/HANDOFF.md`; it is not interpreted
here.

---

## 3. `DSL-E`, the weak-step position read (`DRP-AM7-9`)

An **end step** has an endpoint on one side of it (two per journey); every other step is a **middle
step**.

| side | steps shown | end steps | end share of steps | weak-step marks | on end steps | end share of marks |
|---|---|---|---|---|---|---|
| **candidate** | 197 | 48 | 24.4 % | **43** | **13** | **30.2 %** |
| today's app (reference) | 119 | 48 | 40.3 % | 9 | 7 | 77.8 % |

Firing needs at least 8 candidate marks (43: met), **a strict majority on end steps** (13 of 43: **not
met**), **and** an end share of marks at least 1.5 × the end share of steps (30.2 % against 36.5 %:
**not met**).

**Outcome: does not fire.** *"The candidate's weak steps are not mostly at the ends."*

**What firing would have licensed, and so what this outcome does not:** his decision whether to revive
#249. ⚑ `dsl_result.json`'s `licenses` field for `DSL-E` is the same static string whatever the outcome;
`DRP-AM7-9` governs.

**Per depth, marks (end-step marks):** candidate d5 17 (7), d10 13 (4), d20 13 (2); today's app d5 4 (3),
d10 3 (2), d20 2 (2).

**On what a mark means.** His d10 note on Grimes → The Police says he marks *"the box between the two artists
that don't fit"*, and that he would do so throughout. That is the reading `DSL-E` assumes: a mark sits on
a step between two cards. His note calls the toggle's wording *"a little confusing"*, so marks on rows he
answered before writing it may follow a different convention. The page order is not recorded here, so
this note cannot say how many marks that could touch. With 13 of 43 on end steps, the majority condition
is short by 9 marks.

---

## 4. Barred reads (`DRP-AM7-11`), each beside the result it would be drawn from

**Run-once and final under `GBL-` §5.** This verdict stands. It may not be re-listened, re-tallied on
strength, identification, marks or familiarity, or re-read after the use gate. **No verdict carries
across listens**: `LAL-R1` concerned the map now served and says nothing about this candidate.

| result | the read it does NOT support |
|---|---|
| **`DSL-R3` on coherence** | that **the ceiling** made journeys less coherent, or that **the extra connections** did: the two differ together and the verdict is about `DRP-S1P3` as a whole (`DRP-AM7-1`). Nor that any **single cost term** did. |
| **`DSL-R3` on coherence** | that today's app is better for **random famous pairs**, for **either tier alone** (`DRP-X8`), or on the **first path**, which was not in the listen. The verdict holds for famous pairs he knows, on which the two sides differ at every depth in artists he does not know. |
| **the novelty win, 24–0** | that the candidate *"passes on novelty"* in any sense that softens the FAIL: the split is the FAIL. |
| **the 21-of-24 identification** | a re-read of the verdict that discounts identified rows (`DRP-AM7-10`: it never enters the tally). |
| **the strength counts** | a re-tally on strong picks only. |
| **ear tracking (§1.5)** | that his ear was responding to fame, length or added connections. |
| **`DSL-P` does not fire** | that the fame proxy ranks correctly; or that it bears on the verdict, or the verdict on it. |
| **`DSL-E` does not fire** | that the candidate's breaks are evenly spread or caused by the middle; or that it bears on the verdict, or the verdict on it. |
| **any of it** | that any offline figure (`DRP-C1`'s descent, the lattice results) predicted this verdict, or that this verdict confirms or refutes any offline figure: `DRP-C1` measured fame, this listen measured his ear (§10). |
| **any later use-gate outcome** | a re-reading of this verdict. |

**The Dr. Dog → Matisyahu note (§0 item 2)** falls under two of these at once: it is one pair from
`DRP-T2`, and `DRP-X8` bars both a per-tier read and counting `DRP-T2` rows as evidence about the extra
connections.

---

## 5. Provenance

| item | value |
|---|---|
| runner's verdicts commit | `f6f074b` (`dsl-listen-run`, pushed) |
| `DSL_PAIRS_SHA` = sealed `pairs_file` sha | `34699ace50ba5c24538ff12ca2e2ee339140e17dab470ab0392856d154946903` |
| today's map sha (sealed) | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` |
| candidate map sha (sealed) | `418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f` |
| `DSL-G1` (sealed copy) | PASS |
| side assignment | dealt balanced, 4–4 |
| substitutions at generation | none |
| `dsl_unblind.py` | run once, 2026-10-01, from the runner's `api/` |
| Snyk, `dsl_sealed_summary.py` | 0 issues |
