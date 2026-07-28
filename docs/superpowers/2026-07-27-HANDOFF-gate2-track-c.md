# Handoff — Gate 2 Track C complete, 2026-07-27

> **⚠ SUPERSEDED 2026-07-27 on next actions** by
> [`2026-07-27-HANDOFF-onedrive-migration.md`](2026-07-27-HANDOFF-onedrive-migration.md).
> Its "your job: probably nothing yet" is **spent, not wrong** — the phone run it was waiting
> on has happened and passed. Its "do not revert these" list is untouched and still governs.
> Retained for audit.

**Role: SUPERSEDED on next actions; ACTIVE for its four must-not-revert items.** Supersedes
[`2026-07-27-HANDOFF-dep33-stage3.md`](2026-07-27-HANDOFF-dep33-stage3.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.
*(Role line added 2026-07-27.)*

**Written at a seam.** Track C was the last build track in Gate 2 and it is finished.
**Nothing is in flight** — no subagents, no background jobs, no half-written directories,
**no listeners on `:8000` or `:5173`** (swept by port, not assumed; an API was started for
the e2e run and stopped).

Committed and pushed. **PR #33** on `gate2-track-c`.

**Supersedes [`2026-07-27-HANDOFF-dep33-stage3.md`](2026-07-27-HANDOFF-dep33-stage3.md) on
next actions.** Two of that note's statements are now spent rather than wrong — see below.

---

## Your job: probably nothing yet

> **⚠ SPENT — this section is no longer the next action.** The phone run happened on
> 2026-07-27 and passed on all six checks. Current next action:
> [`2026-07-27-HANDOFF-onedrive-migration.md`](2026-07-27-HANDOFF-onedrive-migration.md).
> *(Inline marker added because this document is over 100 lines and a reader arriving from a
> citation would not see the banner at the top.)*

**The next action is the owner's, and it is to use the app on a phone.** The queued entry at
the top of [`TEST-QUEUE.md`](TEST-QUEUE.md) is the first in this file's history with a URL in
it, and it folds in the mobile section deferred since 2026-07-26 whose trigger has now fired.

**Do not start new build work on the assumption that Gate 2 needs it.** Gate 2's build tracks
are all done. What is owed is *use*, then the Gate 2 → 3 team review, which is scheduled
after a period of real use and is his call.

## What is now true that was not

- **The app is on the internet and reachable.** `https://d2n3xqz3pttguf.cloudfront.net`,
  username `artistpath`. It serves the same graph as the desktop copy, verified mechanically
  against the sidecar.
- **`RMD-6` is CLOSED** — measured on both sides of the deploy, not assumed. The live API
  echoed `http://localhost:5173` before and returns no CORS header after.
- **`RMD-11` is live in production**: the refusal page names the username, and carries no
  credential in plaintext or base64.
- **`FRO-1` verified on the live distribution**: `index.html` is `no-cache`, hashed assets
  are `immutable` and `text/javascript`.
- **§8a ran for the first time in the project's history.** Everything before it proved only
  that the site *refuses*.
- **`infra/README.md` §6 is one command**, not three passes. Image `37d559e` replaced
  `9f5343d`. Suites: builder **115**, api **195**, infra **58**, frontend **80** + **5** e2e.

## ⚠ Do not revert these

1. **`--prune` stays off by default** in `sync_frontend.py`. Turning it on deletes the
   previous build's assets while the previous `index.html` is still live, which is `FRO-1`
   for anyone mid-visit.
2. **The content-type probe stays *between* the two passes.** Moved after `index.html`, it
   reports a fault that is already live; moved before the upload it has nothing to read.
3. **`infra/README.md` §7 now expects THREE drift rows, not two.** The third —
   `ARTISTPATH_CORS_ORIGINS`, `REMOVE` — is permanent by design and is **not** a defect;
   `stack.py` keeps the empty variable deliberately and the guarantee lives in `ApiConfig`.
   Restoring "expect exactly two" makes the gate fire on every future deploy.
4. **§6 must not regain a copy of the commands.** They live in `plan_upload`. Two copies
   drift, which is the whole reason the script exists.

## Overtaken in the previous handoff — spent, not wrong

- Its **`RMD-6` section** described an accepted live exposure. That exposure is closed.
- Its **"§6 is three ordered passes"** was true when written. The open decision it put to the
  owner — script them — was answered yes, and §6 is now one command.

## What I know that is not in the durable record

- **The mutation harness is in the scratchpad again, not the repo.** I rewrote it rather than
  recovering stage 3's. Ten mutations, all caught. If Track C's invariants are ever extended
  it is worth writing a fourth time — or promoting it, which nobody has yet argued for.
- **`cdk diff` and `cdk deploy` print the site credential base64-encoded.** Now in
  `infra/README.md` §5, but worth knowing before you run either.
- **`.env.deploy` is `export NAME=value`.** Bash sources it; PowerShell cannot, and a
  name-anchored regex there fails *silently* — it sets nothing and `app.py` then names
  whichever secret it checks first, which reads like one missing variable rather than none
  loaded. Cost one failed deploy attempt. A working PowerShell loader is in
  `infra/README.md` §5's note.
- **The doc audit (`closeout` B1) was NOT run.** I have a standing instruction not to launch
  subagents unasked, so I did a manual `.claude/` and `memory/` sweep instead: no matches for
  anything describing the deploy, CORS, CloudFront or the sync. **That sweep cannot find a
  defect of omission**, which is precisely what B1 exists for and what it has caught twice
  before. Treat this as an open item, not a clean result.
- **I did not annotate `plans/2026-07-26-track-b-infrastructure.md:1419`**, which still shows
  the old single-line sync — same judgement the last session made, for the same reason: it is
  a completed plan that `docs/README.md` labels "EXECUTED; do not execute again".

## What was decided against

- **Upgrading `react-router` to 8.3.0** for a Medium CSRF advisory. It is exploitable only
  with the unstable RSC APIs enabled; this is a Vite SPA on `BrowserRouter` with no loaders,
  actions, fetchers or `Form`. Major bump, cutover day, non-applicable advisory. Condition
  for revisiting is in the execution log §6.
- ⚠ **RETRACTED 2026-07-27 — there was nothing to fix.** The artifact holds correct UTF-8;
  the mangling was in the tool that read the live response. Full retraction in the execution
  log's deferral table. The struck item follows.
- ~~**Fixing the double-encoded artist descriptions** (`â€œThe Fab Fourâ€`). It is in the
  adopted artifact, so it needs a rebuild, which is the owner's call and not a Track C
  decision. It *is* user-visible — `ArtistSearch.tsx:105` renders it.~~
- **Running the `--prune` pass at cutover.** The bucket was empty; nothing to prune.
