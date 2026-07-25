# HANDOFF — Track 2 complete, result R0 (null), 2026-07-24

**Role: ACTIVE, short-lived by design.** Written at a **clean seam**: the Track 2 sweep ran to
completion, returned a null, and nothing was adopted. Supersedes
[`2026-07-24-HANDOFF-track2-scorer.md`](2026-07-24-HANDOFF-track2-scorer.md), whose open unit
(P8b, then the arms) is now closed.

**This is a seam handoff, not mid-flight.** The degradation tell did not fire. The successor does
the ordinary `session-start`; no cold-read-back is owed.

> Read the record first; where it and this note disagree, **the record wins**:
> [`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md),
> the Track 2 section — in particular the last four entries (**P8b discharged**, **nameless
> artists**, **STAGE 1 RUN**, **STAGE 2 RUN**). Then pre-registration §9, now **A1–A19**.
> `docs/README.md` classifies every document.

---

## 1. State in four lines

- **The sweep is DONE.** 15 arms across two stages, on artifact `4cb84ef9…b061dc8`, **unchanged**.
- **Result: R0, a full null.** C1's threshold is mean ΔF ≤ −1.0; the best arm reached **−0.177**.
- **Nothing was adopted. No shipped code changed. No blind listen was run** — nothing cleared the
  offline gates, so the one-shot resource was saved rather than spent.
- **Figures are owned by** `builder/analysis/2026-07-24-track2-arm-scorer/scores.json` and
  `scores_stage2.json`, narrated in the execution log. **Do not restate them elsewhere.**

## 2. What was learned, in order of how firmly it is established

1. **The floor device is never pivotal.** FL1 and FL2 are byte-identical to each other and to
   their base across all 72 analysis cells, while the floor term fires on 3× as many relaxations
   as production. Tripling `w_floor` changes nothing. **The only depth-graduated device in the
   cost function cannot do its job.** Established without any fame measurement, which is why it
   is first. A16's "floor is load-bearing only if FL1 beats W" resolves to **no**, and §4.4's
   conditional deletion of `w_floor`/`floor_relax_*` now rests on direct evidence.
2. **Re-pricing does not move fame.** Every arm's pooled median interior fame sits in a ~0.1
   band around production's, against a B_unk five times further away. The arms that move paths
   most also make them **shorter and less obscure**.
3. **The similarity ceiling is the one thing that moved anything.** T1b (the ceiling toll) is the
   only coherent signal in fifteen arms — most obscure arm, only one to pass C4, paths *longer*
   than production. It still fails every gate.

## 3. Three things the successor must not get wrong

- **R0 does NOT license "the repricing family is exhausted".** A17(c)'s falsifier **fired**: the
  corner arm X was supposed to bound the family, and both production and T1b are more obscure
  than it. R0 licenses only *"these fifteen configurations do not move it."* Anyone writing up
  this null more strongly than that is overstating it.
- **T1b's two best numbers disagree, and the pessimistic one is the one that counts.** It has
  more below-band interiors than production (31.2 % vs 19.3 %) yet **fails C2 relative to
  production** (3/8 vs 4/8), because it concentrates them in fewer pairs. That is **Attack 2's
  signature** (the insular-cluster dive), and C2 is the criterion encoding what the owner asked
  for. Carry this into any follow-up.
- **The toll ran at HALF its intended strength and its top is untested.** Per A17(b), because W
  = A7 carries `w_sim` 1.5 rather than 3.0, the magnitudes were 3.75× and 15× `w_hop`, not
  §1.4's 7.5× and 30×. The mechanism that produced the only signal has never run at full
  strength.

## 4. The open decision, and what I would do

**Per §2.4, R0 licenses two follow-ups, each needing its own pre-registration:** the **p99
ceiling-rescale arm** (builder side) and/or revisiting the deferred **`cap_strategy`**. It
explicitly does **not** license re-litigating the `capfix` adoption, mutual k-NN, anything in log
§4/§4.1, shipping an arm anyway, or weakening a threshold.

**What I would do if continuing** (not "the owner's call" — he can argue with a position):

1. **Re-test the toll at its intended magnitude first**, in the router. Cheap, needs no rebuild,
   and it tells you whether the ceiling hypothesis has more in it than 15× showed. If a full-
   strength toll still nulls, the builder-side rescale is much less attractive and you have saved
   an artifact change.
2. **Then, if it looks live, pre-register the p99 ceiling-rescale in the builder.** This changes
   the artifact, so it belongs at the rebuild seam — see §6.

The owner has been given this recommendation and has not yet chosen.

## 5. Numbers computed and not written down

**None.** Every figure is in a committed file. The one figure worth knowing that is *not* a
criterion: the stage-1 grid is ~158 s of compute for 11 arms, stage 2 ~113 s for 7 — both far
under §1.4's "order of an hour" estimate.

## 6. The rebuild seam now has THREE items wanting one rebuild

Nothing here is due before the owner decides to rebuild, and they should be done together:

1. **Compute the p99 shift FIRST** — drop the affected edges from the raw score array and
   re-take `np.percentile(raw, 99)`. It is the only channel that can come out **exactly zero**;
   if it does, re-verification is largely reusable, and if it does not, everything downstream is
   redone. It sizes all the other work, so it precedes it.
2. **Scan the archive for the 33 nameless MBIDs**, then the owner's **drop-vs-backfill** decision
   (open). Code reading already excludes the reading under which backfill would be free, so the
   scan is **confirmatory, not decisive**.
3. **The p99 ceiling-rescale arm**, if the owner takes that follow-up.

**`builder/src/artistpath_builder/acceptance.py` deliberately REJECTS a production rebuild** until
item 2 lands. That is the forcing function, it is documented at the check, and **weakening it to
unblock a build is the one wrong response.**

## 7. Things the owner said, now in a file

Nothing new this session beyond what is already recorded: the drop-vs-backfill deferral (with his
confirmation that it does not block progress) is in the pre-registration's deferral entry, and the
Gate 2 → 3 content-curation condition is in the roadmap.

## 8. In flight / git

- **Nothing running.** Two subagents were dispatched (the P8b review, the closeout doc audit) and
  both completed; their findings are folded in.
- **MERGED to `main`: PR #12 → `793587d`, 2026-07-25.** No Track 2 branch remains — the next
  piece of work branches fresh off `main`. The PR body carries the gate outcomes, the deferred
  findings, and the do-not-re-litigate list.
- **The stale `track2-prereg-amendments` branch was deleted** (local and `origin`) after checking
  it line by line. Its one unmerged commit's substance had landed via PR #10; the only content
  `main` lacked was **9 lines of pre-amendment text that A12, A13 and A16 deliberately
  superseded**, so restoring any of it would have reverted an amendment. Recorded because the
  memory note asserting the branch was "contained in main by content" was **wrong on the
  detail** — the diff was not empty — and only the hand check established the conclusion was
  nonetheless right. Its SHA was `efa4a79` if it is ever wanted.
- **This session owned all commits.** No other session was live in the tree.
- **Three merges landed after this note was written, none of them Track 2 work** — PR #13
  (post-merge git state), **PR #14** (the stage-2 near-miss process finding, appended to the
  execution log) and **PR #15** (identifier and read-of-result conventions; mandatory
  displacement retired). Track 2's result is untouched by all three. **PR #15 changed rules a
  successor is governed by**, so read `CLAUDE.md`'s plan-writing and presentation sections as
  current rather than assuming they match what this note's author worked under.

## 9. Deferred findings — none came due at this seam

- **Drop-vs-backfill** (owner) — first step and success condition in pre-registration §9's
  deferral entry. Due at the rebuild seam.
- **Gate 2 → 3 content curation** (owner) — condition recorded in the roadmap's Gate 3 section.
- **`jesus2099` / entity-filter coverage** — Task 11 is complete for placeholders only. Belongs
  inside the existing filter as a third predicate; due at the rebuild seam.
- **The discovery report** for non-artist entities — signals must be external to the graph, and
  the clip test must be name-matching (the naive form fails on `jesus2099`). Due before Gate 2 → 3.
- **D6, PR-B, O-series** — the sweep's reporting items, now largely moot: there is no winner to
  report. **D4 and D7 are discharged.**
- **`builder/README.md` is missing** (doc-audit finding, pre-existing and not caused by this
  work). Success condition: written, or explicitly declined, before Gate 1 closes.
