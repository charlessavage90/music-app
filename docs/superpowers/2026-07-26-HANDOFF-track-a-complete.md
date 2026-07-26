# Handoff — Track A complete, 2026-07-26 (evening)

**Written at a clean seam. Nothing is in flight** — no subagents running, no background
jobs, no half-written directories, no session-owned processes. **Two detached dev servers
are deliberately left running**; see the bottom of this note. Committed and pushed;
PR #27 on `gate2-deploy-and-telemetry`. Aimed at a session that has never seen this work.

**Supersedes [`2026-07-26-HANDOFF-gate2-track-a.md`](2026-07-26-HANDOFF-gate2-track-a.md)
on next actions only.** That handoff remains the record of the design and review work, and
**its "must not be reverted" list is still live** — read it. Its "no code has been written"
line is now false and is marked so in place.

**Your job, if you are the next session: write the Track D plan.** Read, in this order:

1. [`2026-07-26-gate2-track-a-execution-log.md`](2026-07-26-gate2-track-a-execution-log.md) — what was built and what it found (`TKA-`).
2. [`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](specs/2026-07-26-gate2-deploy-and-telemetry-design.md) — **§12 amendments first**; its status banner is now accurate.
3. [`findings/2026-07-26-gate1-gate2-team-review.md`](findings/2026-07-26-gate1-gate2-team-review.md) — `TR-16` is why Track D exists.

## What is now true that was not

- **Track A is DONE.** Ten tasks, six defect fixes plus telemetry. **api 153 → 180**,
  builder 115, frontend 64 → 65, e2e 3. Every per-task expected count hit first time.
- **`DEP-16` is DISCHARGED** — offline routing provably reproduces what the deployed
  router served (`TKA-6`).
- **The app is strictly better even if the deploy never happens** (`DEP-18`), and this is
  now a fact rather than an intention.
- **Nothing about routing moved.** `pathfinding.py` was not edited. The path-quality pause
  is intact.

## Claims that must NOT be reverted by a well-meaning editor

1. **`count=` on `np.frombuffer` stays, and its comment stays honest.** Mutation testing
   proved the guard **unreachable** — the length check above it fires first. The temptation
   is either to delete it as dead or to restore the confident "load-bearing" comment.
   Neither: it is the degradation path if the length check is relaxed, and the comment now
   says exactly that (`TKA-9`).
2. **`TKA-10` is not a bug report against the builder.** `deserialise` genuinely lacks the
   over-long and `TR-3` checks. Do not "fix" it as drive-by work — it has a success
   condition and the risk is confined to offline tooling.
3. **The struck status text in the design and the old handoff stays visible.** Both are
   marked in place, not rewritten. Same reasoning as `DEP-8`.
4. **Telemetry logs facts, not computed metrics.** Unchanged from the previous handoff and
   still the claim most likely to be helpfully undone. `evaluation.py` exists and inlining
   `PathMetrics` looks obvious; it is a scoring decision taken during the scoring pause.
5. **The two pinning tests in Task 5 are supposed to pass without a fix.** An unrecognised
   `reason` must stay coerced to `dislike`; tightening `ExclusionIn.reason` to a `Literal`
   is the natural tidy-up and would silently 422 stale clients (`TR-7`).

## What I know that is not in the durable record

- **`crypto.randomUUID()` works under Vitest's jsdom here.** It was flagged as a risk
  before Task 9 and needed no shim. Do not add a polyfill defensively.
- **The api suite runs in ~1.3 s and all four suites in well under a minute.** There is no
  reason to skip the full-suite gate between tasks.
- **`_client()` in `api/tests/test_app.py` returns `(client, store)`** and builds a
  three-artist graph. Every new API test uses it. `asyncio_mode = "auto"`, so async tests
  need no decorator.
- **The mutation harness used for closeout B3 is disposable and not committed** — it lived
  in the scratchpad. If you want to re-run it, it patched a string, ran one selector,
  and `git checkout --` reverted. Cheap to rewrite; the *result* is in `TKA-9`.
- **`.playwright-results/` is now created at the repo root** on any e2e run and is
  gitignored. That is the `DEP-30` / `TR-17` fix working, not stray output.

## The open decision, and what I would do

**Track D has a scope fence — six items — and no plan.** Writing that plan is the next
unit of work.

**What I would do:** write it, and write it for **subagent-driven execution**. The Track A
plan header names Track D as the specific condition that reverses its own inline
recommendation: six largely independent items, different files, no shared interfaces —
the opposite shape to Track A, where eight of ten tasks edited the same two files. The
responsive-layout item is the one with real design content and the one I would put first,
because it is the only one that could change the others' markup.

**What is genuinely the owner's:** whether Track D happens before Track B at all. The
running order A → D → B → C exists so the deploy ships a phone-usable app rather than
putting a broken one in front of friends — that is a judgement about what friends should
see, not a technical constraint.

## What was decided against

- **Fixing the builder's parser** while in there — `TKA-10`, deferred with a condition.
- **Making `/health` report whether verification was enforced.** It would make `TKA-11`
  checkable over HTTP, but it is a new wire field and a closeout is the wrong moment.
- **Editing `CLAUDE.md` to add `ARTISTPATH_GRAPH_SHA256`.** The audit raised it as HIGH and
  it is a real defect of absence, but the fix grows the budgeted standing layer and that is
  the owner's call. Cost and case: `TKA-13`. **This is the one item awaiting a decision.**
- **Committing `uv.lock`.** `DEP-32` needs it and `.gitignore:18` blocks it, but that is a
  Track B decision with a Track B blast radius (`TKA-12`).

## Left running, deliberately

Two **detached** servers, owned by no session, started after HEAD:

| what | address | PID |
|---|---|---|
| frontend | http://localhost:5173 | 211432 |
| api | http://127.0.0.1:8000 | 231092 |

Both verified answering, not merely bound. They exist for the queued use-the-app entry at
the top of [`TEST-QUEUE.md`](TEST-QUEUE.md). **Nothing will stop them but those PIDs.**
