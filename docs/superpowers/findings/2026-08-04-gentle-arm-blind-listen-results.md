# `GBL-` — the gentle-arm blind listen: result and read

**Role: AUTHORITATIVE for the `GBL-` read.** This document **owns the `GBL-` figures**;
every other document cites it by section and does not restate its numbers. Raw data:
`builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_verdicts.json` (the owner's saved
picks and notes), `gbl_result.json` (the unblinded mapping and mechanical tally),
`gbl_owner_notes.md` (his impressions, dictated before he read the result).

**Governing document:** `specs/2026-08-04-gentle-arm-blind-listen-design.md` — committed
before any journey existed, and it wins wherever this note disagrees. Its §5 fixes the
read; this note applies it and does not reinterpret it.

**Written by a session that did not run the listen** (`CRE-` Stage-3 rule, harness log §8).
The runner's own record is `docs/superpowers/2026-08-04-gbl-run-execution-log.md` — **its
§5 is required reading before anything is built on this note.**

---

## 0. The result, and what cuts against it

**The pre-registered read is the null.** On the 16 deep rows that constitute the primary
outcome, the margin was **3**, against a bar of **5** fixed before any journey existed.
The branch is `no_detectable_difference`, and its plain sentence — frozen in the spec, not
written now — is:

> **"My ear cannot tell them apart where the numbers could."**

Per §5's own action column: **production stands; Option A closes without adoption.** No
default changes, no shipped code is touched, and the re-crawl decision is untouched.

**Four things cut against reading that as "the two are alike", and they must travel with
the sentence above.**

1. **The novelty question was unanimous for the rebuilt app: 8 pairs out of 8.** `GBL-Q1`
   ("as the presses accumulate, which side, if either, delivers more artists new to you?")
   went to the rebuilt package on **every single pair, with no no-preferences**. That claim
   was frozen in the spec's §4 — but §5 fixed **no threshold and no branch for it**, so it
   is data with no pre-registered read attached, and this note does not invent one.
2. **Five of the seven undecided deep rows were undecided because of clip defects, not
   because the journeys were alike.** His notes name the reason in each case: missing
   clips, clips that are song intros with nothing to judge, and at least one suspected
   wrong-artist clip (`BYP-13`, live and known). Only two of the seven record genuine
   indifference — both on the one pair he flagged himself as badly chosen.
3. **The blind did not hold.** He reports it was "almost always really easy to tell which
   side was the 'new' graph", volunteered *before* he read the result. Runner log §5.
4. **Before any button is pressed, he preferred the rebuilt app 6–0.** The d0 anchor rows
   are **excluded from the tally by pre-registration** (§5) and cannot rescue or veto
   anything — but 6–0 with two no-preferences and zero rows for production is the largest
   single number this listen produced.

**Neither arm collapsed.** `GBL-Q2`'s collapse clause — "did either side collapse into a
random walk into obscurity?" — was answered empty on all eight pairs. That failure mode,
the one the strong arm made plausible and which this listen asked of the gentle arm
deliberately, did not occur.

---

## 1. Measured

Arm tokens: **G** = the rebuilt package (`B-S1-P1a` — candidate data set, pooled-and-trimmed
supply, gentle `known` ramp). **V0** = today's adopted production graph and router. Left/right
was shuffled per pair; the table below is already unblinded.

### 1.1 Per-pair verdicts

| # | Pair | d0 (anchor) | d10 | d20 | `GBL-Q1` novelty | `GBL-Q2` coherence |
|---|---|---|---|---|---|---|
| 1 | Wishbone Ash → Pink Floyd | **G** | — | **G** | **G** | — |
| 2 | Young Gun Silver Fox → Eloy | — | **G** | — | **G** | — |
| 3 | The Killers → The Beatles | **G** | — | — | **G** | — |
| 4 | The War On Drugs → Sigur Rós | **G** | **G** | **G** | **G** | **G** |
| 5 | The Decemberists → Yellowcard | **G** | **G** | — | **G** | **G** |
| 6 | Tame Impala → Fountains Of Wayne | **G** | — | **G** | **G** | **G** |
| 7 | Arcade Fire → America | **G** | V0 | V0 | **G** | V0 |
| 8 | Led Zeppelin → Guster | — | V0 | — | **G** | — |

"—" is *no preference*. Re-derived independently from `gbl_verdicts.json` against the
unsealed mapping; agrees with `gbl_unblind.py`'s tally in every cell.

### 1.2 The primary read (spec §5)

| | G | V0 | no preference |
|---|---|---|---|
| **Deep rows (d10, d20) — the primary outcome** | **6** | **3** | 7 |
| d0 anchor rows — *excluded from the tally* | **6** | 0 | 2 |
| `GBL-Q1` novelty, per pair | **8** | 0 | 0 |
| `GBL-Q2` coherence, per pair | **3** | 1 | 4 |

**Margin = 3, of 16 deep rows. Bar = 5. Branch = `no_detectable_difference`.**

### 1.3 Why the seven deep rows were undecided

Classified from his own notes, by the reason he gives:

| Reason | Rows |
|---|---|
| A clip defect blocked the judgement (missing clip, song-intro clip, or a suspected wrong-artist clip) | **5** — pairs 1 (d10), 2 (d20), 5 (d20), 6 (d10), 8 (d20) |
| Genuine indifference — both sides judged coherent | **2** — pair 3 (d10, d20) |

Worked instance, pair 6 at d10, verbatim: *"tough to score R on coherence, as all of the
interiors are unfamiliar to me, and 2 were missing clips (Max Martin, Brad Delson) … Choosing
no pref, though if I could hear the two missing clips, that would make it easier to choose."*

Clip coverage overall (runner log §1, §4): **145 of 152 artists resolved**; silent card slots
were 4 on one side and 8 on the other, out of 315 — small, and the runner judged it not
conspicuous under the brief's §3 test.

### 1.4 Ear tracking (spec §7) — did any hidden metric predict his pick?

On the 9 deep rows where he made a clear pick, how often the side he picked also won each
metric that was computed at generation and hidden during the listen:

| Metric | Picked side won | of |
|---|---|---|
| Lower mean interior `fame_lb_pctl` (more novelty-likely) | 5 | 9 |
| Higher payload (non-hub interior count) | 1 | 9 |
| Lower `top1pct_degree_frac` (less hub-routed) | 3 | 9 |
| Longer journey | 1 | 9 |

**All nine rows were readable on fame** (`fame_rows` = 9 = `rows`): the censoring blind
spot that qualifies the arm's offline pass did not bite in this sample.

---

## 2. What I infer from it — in plain language

*Labelled inference throughout. Someone who does not know what `fame_lb_pctl` measures must
be able to disagree with this section.*

**2.1 The rebuilt app does the thing it was built to do, and the ear confirms it.** Every
one of the eight pairs delivered him more artists he had never heard of, at every level of
button-pressing, with not one pair going the other way or landing as a tie. The offline
experiment predicted exactly this and the ear agrees with the numbers. His own words, before
he knew which side was which: *"On novelty, the new graph wins without question. I don't
think the old graph ever produced more than one novel artist per pair (not per row), if it
even produced one."*

**2.2 The null is a null about *coherence*, not about the package as a whole — and that is
partly an accident of the instrument.** The per-row pick was presented as a bare
left/right/no-preference under a heading giving only the number of presses; neither the spec
nor the page attached a question to it. Reading his row notes, he answered it almost entirely
on coherence — "I think R is the more coherent journey", "L strongly more coherent", "I have
to choose L on coherence". So the primary read, in practice, tallied coherence judgements,
while novelty was captured only by the once-per-pair question that carries no threshold.
**This is my inference from the notes, not something the design states**, and it is the single
most consequential thing in this write-up: the outcome the experiment was built to detect was
measured by the half of the instrument that has no decision rule attached to it.

> **✅ CONFIRMED BY THE OWNER, 2026-08-05 — this is no longer an inference.** He said so
> directly in conversation during the `CAU-` build: *"whether I meant to or not, that's how I
> ended up scoring the rows."* Recorded at
> [`../2026-08-05-cau-audit-build-and-run-execution-log.md`](../2026-08-05-cau-audit-build-and-run-execution-log.md)
> §3.1, which is where it surfaced — it had reached no file until that log was written.
> **Nothing else in this document moves:** no figure, no branch, no verdict. The null stands
> and `GBL-` §5's run-once rule is untouched. What changes is only the standing of the sentence
> above — the person who made the judgements has confirmed what they were about.

**2.3 The clip defects did not bias the result — they destroyed its resolution.** The spec's
rule was "ignore clip failures unless they differ by arm", which protects against a *biased*
comparison. It does not protect against a *blind* one. The clips were broken roughly equally
on both sides, so no side was favoured; but five of the sixteen deciding rows became
unanswerable, and a 16-row instrument that loses 5 rows to noise cannot clear a 5-row bar.
Plainly: **the test could not fail toward either side, and it could barely succeed toward
either side either.** He says as much himself: *"it's hard to know if it's because of the
wrong clip issue, just a strange track choice for the clip, or if the artist truly doesn't
fit in the path."*

**2.4 What he preferred before pressing anything is the graph swap alone.** At zero presses
the gentle ramp has done nothing by construction — the spec says so in §3 — so the 6–0 d0
result is about the rebuilt map and its connection rule, not about the "dig harder" behaviour.
In plain terms: **the rebuilt map's very first journey, the one you see on opening the app,
was better six times out of eight and worse zero times.** His reason is consistent across
pairs and is not about obscurity at all: today's app is coherent step-to-step but *"seemed to
take weird detours"* when you look at the whole path — Taylor Swift between Tame Impala and
Fountains of Wayne, Kendrick Lamar in the middle of a soul pair, a route through Ozzy Osbourne
and Marilyn Manson to reach Pink Floyd. This is **excluded from the pre-registered read** and
I am not smuggling it back in; I am saying it is the most interesting unspent observation the
listen produced, and it points at a different question from the one that was asked.

**2.5 The blind failing does not appear to have manufactured the result.** If knowing which
side was new had biased him toward it, the primary read would have gone *to* the new side; it
did not. The direction of the leak's likely bias and the direction of the null are opposed,
which is weak evidence the null is real rather than an artifact. It remains a real breach and
it is why every claim here is stated as preference rather than as a measurement.

**2.6 None of the four hidden metrics predicted his ear.** Fame at 5 of 9 is a coin flip;
payload at 1 of 9 and journey length at 1 of 9 run *against* the picks. This repeats the Phase 1
§3.8 pattern that is the standing evidence for `REQ-38` — offline metrics do not override
listener judgement — and it is a live caution for any future scoring work: **nothing we
currently measure tells us which journey he will prefer.**

---

## 3. Weakest link

**The load-bearing assumption is that the seven no-preference rows are honest zeros.** The
whole null rests on them: had the five clip-blocked rows resolved in the same proportion as
the nine that did resolve, the margin would have cleared the bar. I would **defend**: the
tally is arithmetically correct, the run state was complete (32 of 32 slots), and the bar was
fixed and scaled before any journey existed. I would **abandon cheaply**: any claim that the
two packages are *similar in coherence*. That is not what was measured; what was measured is
that a partly-blinded listener could not separate them by 5 rows out of 16.

**What would falsify the null:** a re-run with working clips clearing the margin. **That
re-run is forbidden** — spec §5, "the test runs once; an unwelcome verdict stands", bounded by
the owner on 2026-07-23 to bind *this verdict*. The null stands regardless of the reasoning
above. New candidates on new findings may still be listened to; this one may not be re-listened.

**Second weakest:** pair 3 (The Killers → The Beatles) contributed two of the seven undecided
rows and he flagged it himself as *"probably a bad pair choice — two famous artists sitting
close together."* Short journeys between adjacent famous artists have little interior to judge.

---

## 4. Options, and what each costs

Stated as options with consequences, not as a recommendation. Adoption, the re-crawl, and any
further spend of his ear are the owner's column.

| Option | What it means | Consequence |
|---|---|---|
| **A. Take the null as written** | Option A closes; production stands; the re-crawl question is answered "not on this evidence" | Cheapest and fully pre-registered. Accepts that the 8–0 novelty sweep and the 6–0 first-screen result go unacted on |
| **B. Take the null, and open the clip defect as its own track** | The null stands; `BYP-13` and clip *quality* (song-intro previews, missing previews) become work in their own right | Fixes the thing that blinded this listen before any future listen is spent. Does not require re-crawling anything, and the Deezer-id fix already built is dormant awaiting a rebuild |
| **C. Take the null, and open the d0 observation as a new question** | "Today's app takes weird detours on the whole-path view" becomes a separate, pre-registered investigation | New evidence, new question, so §5's run-once rule does not bar it. Costs a new pre-registration and, if it needs the candidate map, the re-crawl |
| **D. Treat novelty as decided and adopt on it** | Reads the 8–0 as sufficient | **I do not think this is available.** No threshold was pre-registered for `GBL-Q1`, so any bar chosen now is chosen knowing the result. `REQ-38` makes the ear primary, but the ear's *pre-registered* reading here is the null |

---

## 5. Barred reads — what this listen cannot support

- **No attribution to any single factor.** V0 and G differ in data set, supply rule and ramp
  together (spec §2). No sentence may credit the ramp, the connection rule, or the candidate
  data individually. The one exception the spec itself grants: at d0 the ramp is inert by
  construction, so the anchor rows speak to the **graph swap as a whole** — never to data set
  versus supply rule separately.
- **"The two packages are equivalent" is barred.** `REQ-41`: "no difference" in unfamiliar
  territory is uninformative, not evidence of equivalence. Most of the undecided rows sit in
  exactly that territory, several with no audible clip.
- **"The gentle arm passed its listen" is barred.** It did not; the margin was 3 of a
  required 5.
- **"The gentle arm failed its listen" is also barred.** Production did not win either; the
  branch is the null, not a `V0_better`.
- **The arm's offline pass stays qualified.** It remains "descent partly unmeasurable, never a
  clean pass" — the four qualifiers travel, owned by
  `findings/2026-08-04-cap-reevaluation-results.md` §0 and §1.4, cited and not restated here.
- **The re-crawl decision is untouched** by any outcome above.

---

## 6. Instrument defects this run exposed, for the next listen

1. **The per-row pick had no question attached to it** — neither in spec §4 nor on the page.
   The two axis questions were asked once per pair; the sixteen rows that decide the outcome
   asked nothing. **A future protocol must state, per row, which axis the row is scoring** —
   or tally the axis questions, which then need thresholds fixed in advance like every other
   read.
2. **A symmetric defect is unbiased, not harmless.** "Ignore clip failures unless they differ
   by arm" protects the direction of the comparison and not its power. A future protocol should
   fix, in advance, **how many rows may be lost to clip failure before the run is declared
   underpowered** rather than null.
3. **Clip preview URLs live ~15 minutes** (runner log §3, measured across four batches). Budget
   one re-resolve plus a server restart per return from a break. A page refresh alone re-serves
   dead URLs, because clips are embedded at server start.
4. **Preview *quality* is unmeasured and it matters.** Several clips were song intros carrying
   nothing to judge an artist on. This is distinct from `BYP-13` (wrong artist) and from a
   missing clip, and neither existing defect record covers it.
5. **Pair selection should exclude adjacent famous endpoints.** Pair 3 produced almost no
   interior to judge, which the owner identified unprompted during the run.
