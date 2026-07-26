# HANDOFF — clips closed, two playback defects fixed, 2026-07-25

> **⚠ PARTLY SUPERSEDED 2026-07-25 — on F1 only.** This note says F1 is "decided but not
> built" (§2, §3, §5). **It is now built** — PR #23, record
> [`2026-07-25-f1-minimum-stop-execution-log.md`](2026-07-25-f1-minimum-stop-execution-log.md).
> Everything else here — the clip closures, the playback fixes, and what must not be
> reverted — stands unchanged.

**Role: ACTIVE, short-lived by design.** Written at a **clean seam**: the work ran to
completion, PR #20 is open and ready, and nothing is in flight. **This is not a mid-flight
handoff — the degradation tell did not fire, and no cold-read-back is owed.**

Supersedes [`2026-07-25-HANDOFF-track2f-and-headroom.md`](2026-07-25-HANDOFF-track2f-and-headroom.md)
**on what happens next only.** That note remains the record of Track 2F's result and of the
path-quality pause, both of which still stand.

> Read the record first; where it and this note disagree, **the record wins**:
> [`2026-07-25-gate1-clips-and-ux-execution-log.md`](2026-07-25-gate1-clips-and-ux-execution-log.md),
> **§15 to §19**.

---

## 1. State in five lines

- **C1 and C2 are both CLOSED.** Fixed *and* confirmed in use. **The roadmap's clip work is
  finished.**
- **Two playback defects found by that same use-the-app run, fixed and verified in real
  Chrome.** One of them was a regression introduced earlier the same day.
- **PR #20 (`clip-freshness-on-play`) is open against `main`, ready for review, not merged.**
  Merging is the owner's.
- **Path-quality work is still paused.** Nothing here touches routing, the cost function, or
  the graph. No rebuild happened and none is due.
- **Nothing is in flight.** One subagent (the closeout documentation audit) was dispatched
  and completed; its findings are actioned in §20.

## 2. What is now wrong in the older record, and in which direction

Everything below is **more done** than the older documents say. A well-meaning editor must
not revert these.

| Was recorded as | Is now |
|---|---|
| C1/C2 "fixed, not closed", awaiting confirmation | **Closed.** Confirmed in use, twice, plus a live retest of the documented failing case |
| Clip URLs die "somewhat under an hour" | **15 minutes**, measured twice against wall clock. §15 owns the figure |
| The queue's question 2 is BLOCKED | **DONE and passed** |
| F1 — "does a journey need at least one stop" is an open question | **Decided by the owner: yes.** Requirement settled. ~~Implementation deferred.~~ **⚠ SUPERSEDED — built 2026-07-25, PR #23.** §16 |
| F1 is blocked on path work resuming | **It is not.** It is a structural invariant over the result, not cost-function tuning. Blocked only on the owner scheduling it |

## 3. Four things the successor must not get wrong

- **⚠ SUPERSEDED — F1 is now BUILT (2026-07-25, PR #23).** *Original text:* **F1 is decided but not built.** A zero-intermediary path is now a **defect against a
  stated requirement**, not a candidate improvement. Its success condition is anchored to an
  observable in §16 and **must not be restated in other words** — two deferral conditions
  have already drifted in the copying, and one lapsed silently.
- **Do not "simplify" `toggle()` into re-resolving on resume.** It must replay the loaded
  URL, or the element re-seeks to zero and the card-pause bug returns.
- **Do not make `dispose()` permanent.** Subscribing revives a disposed player, because
  StrictMode cleans up and remounts on the same memoised instance. A sticky flag silences the
  app outright — found by breaking it, not by reasoning.
- **Playback defects need `e2e/playback.spec.ts`, and it needs real Chrome.** A
  JS-dispatched event has no microtask checkpoint between listeners, so a unit test proves
  the advance correct under a condition browsers never produce; bundled Chromium has no MP3
  codec, so nothing ever ends naturally. **A green unit suite is not evidence here.**

## 4. What I know that is not in the durable record

**Nothing.** Every judgement is in §15–§19, in the PR body, or in a comment at the point of
use. Two things worth pointing at rather than repeating:

- The three-line reasoning for choosing resolve-on-play **and** retry-on-error rather than
  either alone is in §17, and it turns on `toggle()`. It reads as belt-and-braces otherwise.
- The reason the roadmap's C2 inference is loose but its measurement is fine is in §18.

## 5. The open decision, and what I would do

**The owner's, in order:**

1. **Merge PR #20.** Nothing depends on it, but the queue entry for the three playback fixes
   is easier to run against `main`.
2. **Run the queued check** — ten minutes, no waiting. It is the only thing standing between
   the playback fixes and "confirmed".
3. **Then Gate 1 → Gate 2.** With clips closed, the remaining named Gate 1 item is F1.

**What I would do if continuing** (a position, not a menu): build F1 next. It is decided, it
is small, it is outside the pause, and it is the last thing between here and a friends-and-
family gate. The design question worth settling first is what the app should do when two
artists genuinely are neighbours — force a detour, or say so on screen. That is a product
question, so it is the owner's, but it is the only part that needs him.

**Do not start the p99 rescale.** Still not pre-registered, still behind the pause, still the
owner's trigger.

## 6. Things decided against, and why

- **Periodic clip refresh** — fires for cards nobody plays against a rate-limited service.
- **Fixing the skip at the two call sites** rather than at the `Player` seam. The call sites
  were correct; only the seam was wrong.
- **Verifying the skip against the old build** — the fix is identical either way, so it buys
  a label on a historical claim and nothing else. Recorded as inference.
- **Editing the roadmap's C2 inference blind** while the documentation audit was reading the
  same files. Deferred to §20 rather than risking two writers.

## 7. In flight / git

- **Nothing running.**
- **Branch `clip-freshness-on-play`, PR #20, open against `main`, ready for review.**
- **Two commits landed on `main` directly**, both documentation-only, matching the precedent
  set by the two commits before them. One of them (the F1 decision) also carried §17, whose
  code is on the branch — §17 names its own branch in its first line, and merging resolves it.
- This session owned every commit in the tree; no other session was live in it.
