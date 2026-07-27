# Handoff — Track D complete, 2026-07-26 (night)

**Role: COMPLETE — superseded on next actions** by [`2026-07-26-HANDOFF-track-b-complete.md`](2026-07-26-HANDOFF-track-b-complete.md)
and, through the chain, by [`2026-07-27-HANDOFF-gate2-track-c.md`](2026-07-27-HANDOFF-gate2-track-c.md).
**Still the record of Track D, and its do-not-revert list is live.** For status read
[`NEXT.md`](NEXT.md). *(Role line added 2026-07-27; `docs/README.md` had also called this
"the CURRENT handoff" three handoffs after it stopped being one.)*

**Written at a clean seam. Nothing is in flight** — no subagents running, no background jobs,
no half-written directories, no session-owned processes. **Two detached dev servers are
deliberately left running**; see the bottom. Committed and pushed; **PR #28** on
`gate2-track-d-frontend`. Aimed at a session that has never seen this work.

**Supersedes [`2026-07-26-HANDOFF-track-a-complete.md`](2026-07-26-HANDOFF-track-a-complete.md)
on next actions only.** That handoff remains the record of Track A and **its "must not be
reverted" list is still live** — read it. One of its bullets is now struck in place: the
Playwright `outputDir` claim (see `TKD-3` below).

**Your job, if you are the next session: Track B — the infrastructure track.** Read, in order:

1. [`2026-07-26-gate2-track-d-execution-log.md`](2026-07-26-gate2-track-d-execution-log.md) — `TKD-`, and its §12 is the closeout record.
2. [`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](specs/2026-07-26-gate2-deploy-and-telemetry-design.md) — **§12 amendments first**.
3. [`findings/2026-07-26-gate1-gate2-team-review.md`](findings/2026-07-26-gate1-gate2-team-review.md) — **`DEP-33` is the one that binds Track B**.

## What is now true that was not

- **Track D is DONE.** Eight tasks, seven items. frontend 65 → **78**, e2e 3 → **4**, api 180
  and builder 115 **unchanged** — that last pair is the check that routing was untouched.
- **The app has a phone layout.** It had none. Interior artist name at 390 px: **0 px → 200 px**.
- **`DEP-30` is discharged from Track D, not from Track A** (`TKD-3`).
- **Nothing about routing moved.** `pathfinding.py` was not opened. The path-quality pause
  is intact and Track D is not a resume signal.
- **The standing context layer grew by zero lines.**

## Claims that must NOT be reverted by a well-meaning editor

1. **`Player.play()` captures the handler live at call time** and fires only if it is still
   installed *and* the player is undisposed (`TKD-10`). The two-part condition looks
   redundant — checking `disposed` alone reads as sufficient, and it is not: StrictMode
   revives the instance, which clears the flag. Deleting either half re-opens playback
   restarting after navigation. Both tests around it now go red under mutation; they did not
   before.
2. **A refused `play()` goes through the *existing* `onError` channel**, not a new one. A
   second channel needs its own retry policy and puts all four player invariants back in play.
3. **The timeout wrapper uses its own controller and throws `TimeoutError`** rather than
   aborting the caller's signal. `usePath` returns early on its own abort, so the obvious
   alternative is silently swallowed and the page hangs forever — the defect being fixed. A
   pinning test holds this and it **catches** its mutation.
4. **One copy of the bypass-button markup.** A `hidden sm:flex` / `flex sm:hidden` pair is the
   natural way to build this and breaks `e2e/path.spec.ts`: it resolves those buttons by role
   and Playwright strict mode fails on two matches.
5. **`TEST-QUEUE.md`'s new header constraint stays until cutover.** No queue entry may ask for
   a phone. It is not fussiness — such an entry is *unrunnable* and sits in the file looking
   like an untested item rather than an impossible one.

## What I know that is not in the durable record

- **The cover art is the slowest thing on the page.** A screenshot taken 1.5 s after a path
  renders shows grey squares; the URLs are set correctly and the images simply have not
  arrived. This looked like a Track D defect and is not — it reproduces identically on a warm
  cache in under a second. Do not "fix" it.
- **`npm run test:e2e` needs the API on :8000 and starts only the Vite server itself.**
  Playwright's `webServer` block has `reuseExistingServer: true`.
- **The e2e suite is the only place the responsive work is verified at all**, and it runs
  headless at an emulated viewport. There is no unit coverage of the layout by design —
  jsdom computes none. If someone deletes `e2e/responsive.spec.ts` as slow, the entire
  phone layout becomes unverified and nothing will fail.
- **`vi.waitFor` works in this suite; fake timers are only needed for the client timeout
  tests.** `vi.useFakeTimers()` there must be paired with `advanceTimersByTimeAsync`, not the
  sync variant, or the promise never settles.
- **The `oxlint` run has one standing warning** (`vite.config.ts` triple-slash reference). It
  is pre-existing, unrelated, and deliberately not fixed. Do not read a clean-but-for-one
  lint run as a regression.

## The open decision, and what I would do

> **⚠ SUPERSEDED 2026-07-26, same day — Track B has been planned, built, deployed and
> reviewed.** Record: [`2026-07-26-gate2-track-b-execution-log.md`](2026-07-26-gate2-track-b-execution-log.md);
> current handoff: [`2026-07-26-HANDOFF-track-b-complete.md`](2026-07-26-HANDOFF-track-b-complete.md).
> **`DEP-33` was run and is discharged** — and this section's recommendation to run it inside
> Track B rather than after it was followed. The rest of this handoff stands as the record of
> Track D and of the position at the time it was written.

**Track B has a design and no plan.** Writing that plan is the next unit of work.

**What I would do:** write it, and **run `DEP-33` as part of it rather than after it.** Seven
of the team review's blocking findings are about a design rather than code because `infra/`
did not exist; the review says plainly it must be re-run against the CDK stack before
cutover. Doing that at the *end* of Track B means discovering CDK-shaped defects after the
stack is written. Writing the plan so the review lands mid-track is cheaper and is the same
lesson `TR-1` taught at Track A's expense.

**What is genuinely the owner's:** whether to spend AWS money at all yet, and the two items
Track B inherits that cost real decisions — committing `uv.lock` (`TKA-12`, gitignored today,
with a Track B blast radius) and whether `CLAUDE.md`'s next-action row should name the
executed tracks (an audit HIGH, deliberately not actioned, see the log's §12).

## What was decided against

- **Reordering `TEST-QUEUE.md`** on an audit recommendation — it would break the file's own
  newest-first convention. The defect underneath it was fixed instead.
- **Editing `CLAUDE.md`** to record Track A/D completion. Correct finding; grows the budgeted
  layer; owner's call.
- **Fixing the `vite.config.ts` lint warning.** Pre-existing and outside the fence.
- **Binding the dev server to the LAN** so a phone could reach it before the deploy. Offered
  to the owner, not taken unilaterally — it needs a firewall change on his machine.

## Left running, deliberately

Two **detached** servers, owned by no session — the same two Track A left, still healthy:

| what | address | PID |
|---|---|---|
| frontend | http://localhost:5173 | 211432 |
| api | http://127.0.0.1:8000 | 231092 |

**They started at 18:51, before HEAD**, which normally invalidates a manual test. **Here it
does not, and it was verified rather than assumed:** Vite reloads from disk, and the module
served at `:5173` carries Track D's layout; Track D changed no `api/` or `builder/` file at
all, so the API's boot-time code is current. They are valid for the queued use-the-app entry.
**Nothing will stop them but those PIDs.**
