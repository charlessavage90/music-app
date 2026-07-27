# HANDOFF — F1 built, awaiting the owner's run, 2026-07-25

**Role: ACTIVE, short-lived by design.** Written at a **clean seam**: the work ran to
completion, PR #23 is open, nothing is in flight. **Not a mid-flight handoff — the
degradation tell did not fire, and no cold-read-back is owed.**

Supersedes [`2026-07-25-HANDOFF-clip-playback.md`](2026-07-25-HANDOFF-clip-playback.md)
**on F1 only.** Everything else in that note — the clip closures, the playback fixes —
stands.

> Read the record first; where it and this note disagree, **the record wins**:
> [`2026-07-25-f1-minimum-stop-execution-log.md`](2026-07-25-f1-minimum-stop-execution-log.md).

---

## 1. State in five lines

- **F1 is BUILT.** Every journey now gets at least one stop, or says on screen why it
  cannot. ~~**PR #23 open against `main`, not merged.** Merging is the owner's.~~ **PR #23
  was merged.**
- ~~**F1 is NOT discharged.** Its condition is an observation, and that observation is the
  queued use-the-app entry. A passing suite does not close it.~~ **⚠ STRUCK 2026-07-27:
  `F1` was DISCHARGED on 2026-07-26** — the observation its condition named happened, and
  Gate 1 is closed. Recorded in `2026-07-26-HANDOFF-deliverability.md` and
  [`NEXT.md`](NEXT.md), which owns status. The reasoning above was right; only its
  conclusion has been overtaken.
- **Path-quality work is still paused.** This added no weight, no config knob, no
  cost-function change and no rebuild — a structural constraint over the *result*.
- **Nothing is in flight.** The SDD workspace is deleted; no subagent or job is running.
- Two servers are up for side-by-side testing: **`:5173` old routing, `:5174` new.** They
  are dev processes, not state — kill them freely.

## 2. What is now wrong in the older record, and in which direction

Everything below is **more done** than the older documents said. **Do not revert these.**

| Was recorded as | Is now |
|---|---|
| F1 "requirement settled, implementation deferred" | **Built.** `CLAUDE.md`'s orient table and the clip-playback handoff are both corrected |
| `api/README.md`'s path response | Now documents `stop_rule` — it was owned by no task, which is how absence defects arise |
| The design's §7 asked for a byte-identical comparison | §7 now records what was asked versus what was actually done, and why the claim still holds |

## 3. Four things the successor must not get wrong

- **Do not add a rule for choosing the inserted artist.** The detour is chosen by the
  existing cost function precisely so this stays outside the path-quality pause. A new
  criterion would be scoring, and scoring is paused.
- **Do not cap the detour length or suppress famous stops.** Both were considered and
  deliberately left alone; capping means inventing a threshold to answer a question only
  use can answer. Both are in the queue entry for the owner.
- **Do not restate F1's success condition.** It is owned by
  `2026-07-25-gate1-clips-and-ux-execution-log.md` §16. Two prior conditions on this
  project drifted in exactly that copying and one lapsed silently.
- **The verification script's "no stop possible: 10" is sample-biased and is not a rate.**
  It draws a random artist then one of their connections, over-drawing artists with few.
  The pair-level figure is owned by `findings/2026-07-25-mutual-knn-stranding.md` `MKS-6`.

## 4. What I know that is not in the durable record

**Nothing.** Every decision, plan defect and gate outcome is in the execution log or the
PR body. Two things worth pointing at rather than repeating:

- The three plan defects (§3 of the log) share one shape — a confident premise about the
  graph that the graph contradicts — and all three were caught by *running* against the
  real artifact, none by reading. That is the reusable lesson, not the individual bugs.
- The exposure-estimate correction in §2 of the log: a per-pair rate is not an exposure
  rate when users do not select uniformly. This session got it wrong first.

## 5. The open decision, and what I would do

**The owner's, in order:** merge PR #23; run the queued entry (ten minutes, no waiting);
then Gate 1 → Gate 2.

**What I would do if continuing** (a position, not a menu): nothing new until that run.
F1 was the last named Gate 1 item, so the next thing is the gate itself, and every
remaining candidate sits behind the path-quality pause.

**One item is left explicitly to him** and is not a defect to be fixed by a successor:
`.claude/agents/ml-graph-analyst.md` omits that a two-card result is now re-routed. Its
cost function was checked and is complete. Adding the line would grow the layer that taxes
every session, so it is his call.

## 6. Things decided against, and why

- **Deferring the on-screen message** — was the plan until measurement showed the pairs it
  affects include artists a person would plausibly search.
- **Capping detour length**; **suppressing famous intermediaries.** Both are scoring
  preferences wearing a bug-fix costume.
- **A true historical frontend for the side-by-side.** The routing change lives entirely
  in the API, so a second checkout would have cost a full dependency install for no added
  fidelity. The two dev frontends run identical code; only the APIs differ.

## 7. In flight / git

- **Nothing running** except the two dev servers in §1.
- **Branch `f1-min-stop`, PR #23, open against `main`.**
- **Two consultant branches exist and are not this session's work**:
  `consultant-router-ascent` (merged, PR #22) and `consultant-bypass-use-run` (pushed,
  open, in its own worktree outside this tree). Neither carries any F1 code.
