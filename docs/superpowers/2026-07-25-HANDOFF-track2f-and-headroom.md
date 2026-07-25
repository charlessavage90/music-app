# HANDOFF — Track 2F null, ordering headroom WIDE, 2026-07-25

**Role: ACTIVE, short-lived by design.** Written at a **clean seam**: both units ran to
completion, nothing was adopted, and no work is in flight. Supersedes
[`2026-07-24-HANDOFF-track2-complete.md`](2026-07-24-HANDOFF-track2-complete.md) **on what
happens next only** — that note remains the record of Track 2's own result, and its §2 and §4
carry inline supersession marks.

**This is a seam handoff, not mid-flight.** The degradation tell did not fire. The successor
does the ordinary orientation; no cold-read-back is owed.

> Read the record first; where it and this note disagree, **the record wins**:
> [`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md),
> the last two entries (**TRACK 2F** and **ORDERING HEADROOM**). Figures are owned by
> `builder/analysis/2026-07-25-track2f-toll-ladder/` and
> `builder/analysis/2026-07-25-ceiling-ordering-headroom/`. **Do not restate them elsewhere.**

---

## 0. PAUSED — path-quality work is stopped by owner decision, 2026-07-25

**Decided by the owner after this session's closeout had already run.** The app goes to
**Gate 2 (friends & family)** instead; the next work is Gate 1 leftovers, not path quality.

**The builder-side p99 rescale is NOT pre-registered, and must not be started.** The
headroom measurement licenses *pre-registering* it — that is all it ever licensed, and no
pre-registration exists. A session that begins designing, building or running it is acting
without a governing document.

**Resuming path work is the owner's trigger, not a session's.** Nothing in this file, in the
execution log, or in the analysis directories constitutes a resume signal, however live the
reasoning looks. The measurements are deliberately left mid-argument; that is what a pause
looks like, not an invitation.

### What is parked, with success conditions

| Parked | Success condition |
|---|---|
| **The builder-side p99 rescale probe** | The owner resumes path work **and** it is pre-registered with its own document. Both, in that order. |
| **Open question 1 — the *direction* of the restored ordering** | Unanswered and load-bearing. WIDE established the clip erases ordering large enough to change routes; it says **nothing about which way** those routes move. Restoring the ranking could route toward more obscure neighbours, or merely toward *different* famous ones. Condition: answered before any rescale is adopted — by the probe, or by a cheaper measurement if one exists. |
| **Open question 2 — the nameless-artist decision (drop vs backfill)** | The owner decides, and `builder/src/artistpath_builder/acceptance.py` stops rejecting a production rebuild. It is the hard blocker: **no rebuild, therefore no rescale, until this is settled.** Weakening the check to unblock a build remains the one wrong response. |
| **`TF2`, the full-strength toll arm** | Not adopted, not listened to. It failed the offline gates, so the pre-registration bars a blind listen. Condition: adoption would need a fresh pre-registration; a listen would need the owner's explicit deliberate deviation. |
| **The depth carrier (F2's "progressively")** | Still unsolved and untouched by either unit here. No condition set — it needs a design, not a probe. |

**§4 below is superseded by this section** on what to do next; it is retained as the record
of the position this session held at the seam. Its step 1 (settle the nameless artists) is
still owed *whenever* a rebuild is next wanted, for any reason.

## 1. State in five lines

- **Track 2F is DONE.** The ceiling toll ran at full strength and past it — 8 magnitudes from
  0 to 7,500 × `w_hop` — on artifact `4cb84ef9…b061dc8`, **unchanged**.
- **Result `TFR0`, a null on the primary criterion.** `M*` = −0.198 against a −0.25
  continuation trigger and `C1`'s −1.0 bar. **Nothing adopted, no shipped code changed, no
  blind listen run, no threshold touched.**
- **The ordering-headroom measurement is DONE and came back WIDE** — median 10.01 × `w_hop`
  of cost ordering erased by the p99 clip, against a 1 × threshold committed beforehand.
- **No rebuild happened and none is due.** Both units were router-side or read-only.
- **Nothing is in flight.** One subagent (the closeout doc audit) was dispatched and completed.

## 2. What was learned, in order of how firmly it is established

1. **The toll mechanism is exhausted, and this time the bound holds.** `TF2` (30×), `TF3`
   (60×), `TF4` (120×) and `TFX` (7,500×) are identical on every criterion, and `TFX` ties the
   best arm. Track 2's corner arm `X` failed exactly this check (A17(c)); this one passes, so
   the null may be stated at **mechanism** strength: no router-side toll moves the primary
   outcome past −0.198 at any price. Established from paths alone.
2. **Production takes 85.42 % of its hops on ceiling edges**, and no price drives that below
   **28.86 %** — 144 of 499, exactly **2.0 per journey**, one leaving the start artist and one
   arriving at the destination. The limit is graph structure, not price. §1.4's intended top of
   30× is exactly where the ladder lands, so the magnitude was chosen correctly.
3. **The clip erases a median 10.01 × `w_hop` of ordering**, rising to 14.50 × on fully
   saturated nodes and 13.51 × on the pre-registered endpoints — of which **100 % exceed
   7.5 ×**, a magnitude Track 2F proved changes routing. Both self-checks passed: the
   in-memory rebuild reproduces the adopted artifact's sha256, and the unclipped formula
   agrees with the real `rescale_scores` on all 3,951,579 unsaturated edges.
4. **The mechanism, which is the clearest statement of the defect this project has reached.**
   At a fully saturated node every exit carries `w_sim · (1 − 1.0) = 0`, so similarity
   contributes **nothing** to the choice; `w_degree_hub` is 0 and avoidance is empty on a
   `known` walk, leaving the **popularity** terms to discriminate up to 50 candidates. At
   exactly the famous artists a journey starts and ends at, the router cannot see who is most
   similar and routes on fame instead. §2.12's "cost-function problem" and the graph-structure
   reading were never competing — the cost function is starved of signal where it matters.

## 3. Four things the successor must not get wrong

- **`TFR0` does NOT mean "the p99 ceiling is fine".** Verified in the builder: `pipeline.py`
  stores `min(1.0, …)`, so the artifact retains no information distinguishing saturated edges.
  A toll can only test the ceiling's **cheapness**; its **ordering** is untestable
  router-side. The null closes one half and the headroom measurement opens the other.
- **WIDE means a rescale would *change* routes, never that it would *improve* them.** Change
  is necessary and not sufficient. Every offline measure here has been a poor predictor of the
  owner's ear.
- **Neither unit touches F2's "progressively" clause.** Every Track 2F arm is
  depth-independent by construction and `C3` fails on all of them. The only depth-graduated
  device in the cost function is still dead (Track 2 stage 2). The depth carrier is unsolved.
- **The Attack 2 worry the previous handoff carried forward is dead.** `T1b` reached deeper in
  *fewer* pairs than production (3/8); at full strength `TF2` reaches **wider** (5/8) — the
  first arm in either track to beat production on absolute reach.

## 4. The open decision, and what I would do

> **⚠ SUPERSEDED by §0, 2026-07-25 — the owner paused path work after this was written.**
> Nothing below is a live instruction. Step 1 survives only in the weaker form stated in §0:
> the nameless-artist decision is owed before any rebuild, whatever the rebuild is for.
> **Do not act on step 2.** *Original text follows.*

**The rescale probe is now well-motivated and still un-pre-registered.** Nothing licenses
running it yet: it needs its own pre-registration, and it changes the artifact, so it sits
behind the rebuild seam.

**What I would do if continuing** (a position, not a menu — argue with it):

1. **Settle the nameless-artist question first.** `acceptance.py` deliberately rejects a
   production rebuild until drop-vs-backfill is decided, so it blocks everything below and is
   owed regardless of what comes next. Owner's decision.
2. **Then pre-register the builder-side p99 rescale**, with the headroom figures as its
   expected effect size — the first probe in this family to have one before it runs.
3. **Do not spend the blind listen on `TF2` unless the owner chooses to.** It failed the
   offline gates, so the pre-registration bars a listen; overriding that after seeing results
   is exactly what pre-registration exists to prevent. If he wants it anyway it is his
   one-shot resource, and it must be recorded as a deliberate deviation, with the pairs picked
   blind and the arms unlabelled.

The owner has been given this and has not yet chosen.

## 5. Numbers computed and not written down

**None.** Every figure is in a committed file. Two worth knowing that are not criteria: the
ladder is ~461 s of compute for 10 arms, and the in-memory rebuild from the 75,000 archived
responses takes about the same. Both are far cheaper than the "order of an hour" the Track 2
pre-registration budgeted.

## 6. Things decided against, and why

- **Adding a `w_sim = 3.0` arm to the ladder** — it would have restored §1.4's nominal
  `toll_s` figures but changed two knobs at once, which is the confound A17(b) was written
  about. Magnitudes were re-expressed in `w_hop` instead.
- **Extending the ladder below 3.75×** — Track 2 already recorded that magnitude as inert, and
  the reproduction arm confirmed it (+0.001 against its baseline).
- **Reading the held-out set.** It confirms a winner's direction and there is no winner.
  Deliberately untouched, as in Track 2.
- **Scoring the ladder two ways when `TFX` looked like it might strip cells.** It did not —
  zero guard-infeasible cells — but the fallback would have invited selection, so A13's
  uniform drop was kept as written.
- **Treating the headroom measurement as an experimental arm.** It routes no path and scores
  no criterion, so it got a committed decision rule rather than a full pre-registration.

## 7. Things the owner said, now in a file

- **He accepted that the consulting session's commits bundle into this PR** rather than being
  split out. Recorded because the alternative was considered and declined for a reason
  (branch surgery would disturb a live session), not overlooked.
- **`-builder` is the session-naming suffix for builder sessions**, distinct from the
  parenthetical `(handoff)` markers. Now written into `session-start` §E; it had been in use
  and undocumented.
- His reaction to a labelled `d20` path comparison **cannot be used as evidence** — the paths
  were shown labelled, so the blind protocol was broken. Recorded so nobody later mines it as
  a listening result. It is suggestive only, and it happened to track `C2` exactly.

## 8. In flight / git

- **Nothing running.**
- **Branch `track2f-toll-full-strength`, PR #18, open against `main`.** Not merged.
- **The PR bundles a second session's work**, at the owner's explicit direction: four commits
  from a concurrent consulting session scoped to skills, agents and hooks. They are attributed
  in their commit messages and are unrelated to Track 2F.
- **This session owned all commits in the tree**, including landing the other session's work.

## 9. Deferred findings — one new, none came due

**New:** *(none from Track 2F itself — it adopted nothing and added no config knob.)*

**Carried, unchanged and not yet due:**

- **Drop-vs-backfill for the 33 nameless artists** (owner) — due at the rebuild seam, and now
  the blocker in front of the rescale probe. `acceptance.py` is the forcing function;
  weakening it to unblock a build is the one wrong response.
- **Gate 2 → 3 content curation** (owner) — condition in the roadmap's Gate 3 section.
- **`jesus2099` / entity-filter coverage** — belongs inside the existing filter as a third
  predicate; due at the rebuild seam.
- **The discovery report** for non-artist entities — due before Gate 2 → 3.
- **`builder/README.md` is missing** — success condition: written, or explicitly declined,
  before Gate 1 closes. Still open, still pre-existing.
