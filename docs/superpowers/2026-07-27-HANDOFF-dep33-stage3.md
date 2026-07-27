# Handoff — `DEP-33` remediation stage 3 complete, 2026-07-27

**Written at a planned seam.** The plan named this boundary before any work started
([`plans/2026-07-27-dep33-blocker-remediation.md`](plans/2026-07-27-dep33-blocker-remediation.md)
§3), and stage 3 reached it. **Nothing is in flight** — no subagents running, no background
jobs, no half-written directories, **no listeners on `:8000` or `:5173`** (swept by port, not
assumed; an API was started for the e2e run and stopped).

Committed and pushed. **PR #32** on `gate2-dep33-stage3`.

**Supersedes [`2026-07-27-HANDOFF-dep33-stages-1-2.md`](2026-07-27-HANDOFF-dep33-stages-1-2.md)
on next actions only.** Everything else in that note still stands, including its reversed
must-not-revert claim and the six that survived it.

---

## Your job: Track C

Sync the SPA to the bucket. **Read `infra/README.md` §6 first, and read it rather than
remembering it** — it changed under stage 3 and the old one-line form is now a defect.

Track C is also what closes three things at once: `RMD-6` (below), the stack drift it causes,
and `RMD-13`'s browser half.

## What is now true that was not

- **Stage 3 is done**: `RMD-11`, `RMD-12` closed; `RMD-13`'s runbook step landed and executes
  at cutover, exactly as the plan anticipated.
- **The 401 names the username.** `stack.py`'s new `SITE_USERNAME` is substituted into both the
  admitted credential and the refusal page, so the page cannot name a username the gate rejects.
- **`infra/README.md` §6 is three ordered passes, not one `aws s3 sync --delete`.**
- **`infra/README.md` §8a exists** and is the first step of the cutover.
- **`frontend/index.html` carries static fallback markup** inside `#root`.
- Suites: builder **115**, api **195**, infra **41**, frontend unit **80**, e2e **5**. All green.

## ⚠ Do not revert these

1. **The `--delete` is out of §6's first pass deliberately.** Putting it back re-opens
   `FRO-1` for anyone mid-visit. The prune is a separate, later step and §6 says why.
2. **`index.html`'s fallback must stay inside `<div id="root">`.** Moved beside it, React never
   clears it and it sits under the app forever. Three tests catch this; it is not a style choice.
3. **The 401 body must never carry the password.** It is base64 in the credential, so "no
   plaintext password" is not the check — `test_the_refusal_does_not_disclose_the_password`
   checks the encoded form too, and that is why.
4. **`ARTISTPATH_DEPLOY_IMAGE_TAG` is still required** (`ARC-6`, from stage 2).

## ⚠ Unchanged from the last handoff and STILL LIVE in production

**`RMD-6` is not closed.** Nothing was deployed in stage 3 either. The running service still
serves `config.py`'s old dev CORS default. **The owner accepted this exposure on 2026-07-27**
rather than deploy twice — that was the open decision the previous handoff put to him, and it
is now settled. Exposure is `/health` only; everything else needs the origin secret. It closes
on Track C's deploy.

## What I know that is not in the durable record

- **The mutation harness is still in the scratchpad, not the repo**, and I rewrote it rather
  than recovering the previous session's. Cost about ten minutes. It applies one substitution,
  runs one package's suite, restores in a `finally`. If Track C adds invariants it is worth
  writing again.
- **Mutating a frontend file needs `PYTHONIOENCODING=utf-8`** if you drive it from Python and
  print the runner's output — Playwright's output is not cp1252 and the harness dies *after*
  the run, which reads like a failed mutation and is not one.
- **`aws s3 sync`'s content-type guessing was re-confirmed only for the previous session's
  check, not re-measured by me.** It is now written into §6 as a machine-state caveat, which is
  where it belongs, but nobody has re-run it since 2026-07-27 morning.
- **I did not annotate `plans/2026-07-26-track-b-infrastructure.md:1419`**, which still shows
  the old single-line sync. Judgement, not oversight: it is a completed plan, `docs/README.md`
  already labels it "EXECUTED; do not execute again", and annotating frozen plans for every
  later change is unbounded. If you disagree, the fix is one line.
- **The doc audit did not open `.claude/`.** I swept it myself for anything describing the
  deploy, CORS, CloudFront, the sync or the viewer function: **no matches**, so nothing in the
  auto-loaded layer went stale. Recorded because B5 requires that sweep and the audit report
  will not show it.

## The open decision, and what I would do

**Whether to turn `infra/README.md` §6 into a script before running Track C.**

Every other fix in stage 3 is held by a test. §6 is not — it is three ordered commands a person
types, at the end of a deploy, and the failure it prevents is invisible to whoever runs it
(you never see the blank page yourself; only a returning visitor does).

**What I would do:** write the script as Track C's first task, then use it for the cutover.
It is small, it is used immediately, and it removes the one thing in this stage that nothing
enforces. **But it is genuinely the owner's**, because it trades a little time now against how
much he trusts a runbook step, and he is the one who will be running it.

## What was decided against

- **Deploying anything in stage 3.** Same reasoning as stage 2, and now the owner's explicit
  decision.
- **Annotating the completed Track B plan's stale sync command** — see above.
- **Adding node types to `tsconfig.app.json`** so a test could use `node:fs`. It would let any
  app module import node builtins and still typecheck. Used Vite's `?raw` instead.
