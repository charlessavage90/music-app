# Handoff — the frontend redesign, built and deployed, 2026-07-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-28-HANDOFF-frontend-mockup-adoption.md`](2026-07-28-HANDOFF-frontend-mockup-adoption.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**Written at a seam**, not a mid-flight retirement. The work is finished, merged, deployed and
verified; nothing below depends on anything held only in a session's head.

**Nothing is in flight.** No subagents at retirement, no background jobs, no listeners on 8000
or 5173 — both stopped by this session and confirmed free.

Record: [`2026-07-28-frontend-mockup-adoption-execution-log.md`](2026-07-28-frontend-mockup-adoption-execution-log.md)
— §9–§13 are Tasks 8–13, §14–§17 the owner's changes and the deploy.
Plan: [`plans/2026-07-28-frontend-mockup-adoption.md`](plans/2026-07-28-frontend-mockup-adoption.md).
Spec: [`specs/2026-07-28-frontend-mockup-adoption-design.md`](specs/2026-07-28-frontend-mockup-adoption-design.md).

---

## The one-line state

**All 13 tasks are done, plus three owner copy/rail changes and `path_length` telemetry. It is
merged (`d68ef7a`) and LIVE at `https://musicapp.cmiller.io`.** PR #43 merged; PR #44 (docs
only) is open and unmerged. **The one thing owed is the owner's: the queued use-the-app test,
including the iPhone script.**

## Your job

**Probably nothing on this axis.** The redesign is closed. The next action is the owner's use
of the app, and after that whatever he decides. Two mechanical items are owed and named below.

## What is owed, and neither is urgent

1. **The `--prune` publish pass — TRIGGERED, owed as a SEPARATE LATER RUN.** Not during a
   publish: `infra/README.md` §6 is explicit that pruning while the old `index.html` may still
   be cached re-opens the `FRO-1` blank-page window. Run
   `sync_frontend.py --prune --skip-build` once the new `index.html` has been live long enough
   — a day is ample. Cost of waiting: a few kB of orphaned assets. Cost of rushing: a white
   screen for a returning visitor.
2. **PR #44 is open** and carries only the post-deploy documentation sync.

## Which documents are now wrong, and in which direction

- **The plan and the spec are COMPLETE, not active.** The spec's §7 copy table is annotated
  where the owner changed two landing strings; the annotation is authoritative over the rows.
- **`docs/README.md` should gain a row for this handoff** if it does not have one — the
  doc-audit at closeout is the check for that.
- **Nothing in `CLAUDE.md`, `.claude/` or `memory/` was touched**, so nothing there went stale
  from this work. D6 deltas are exactly 0 in both layers.

## What was overturned and must NOT be reverted

- **The `UI-7` test in `useEndpoints.test.tsx` is deliberately MIXED** — one lookup fails, one
  succeeds. The both-fail version is vacuous; it passed with the error handling removed.
- **`PathIntro`'s two count assertions read the line's `textContent`, not `getByText`.** The
  plan's version could never pass: the design splits that sentence across three text nodes and
  `getByText` matches a node's own text children only.
- **`e2e/path.spec.ts` locates the artist name by `data-testid`, not `.font-semibold`.** The
  endpoint eyebrow is also `font-semibold`, so the old locator silently resolved to the *first*
  card. This is the same fix `UI-5` made in `responsive.spec.ts`.
- **The landing clip-length test asserts the line is ABSENT.** That is the owner's removal
  pinned, not a leftover.
- **`viewport-fit=cover` stays absent and `env(safe-area-inset-bottom)` stays inert** (`UI-D3`).
- **The loading screen's rail was deliberately not changed** when the journey rail became full
  height. Different element, animated, never had the arrow.
- **The design export stays excluded from oxlint.**

## What has already been updated — do not re-edit

`NEXT.md`, `TEST-QUEUE.md` (the QUEUED entry now names the live address and its phone half is
un-deferred), the execution log §9–§17, the spec's §7 annotation, and the previous handoff's
role line.

## What I know that is not in the durable record

**Two items, both small, both now written down here rather than left in a scratch file.**

- **The `cdk deploy` output is not safe to paste anywhere public.** The runbook says so, and it
  is easy to forget while pasting logs into a message. Filter `Basic `, `x-front-door` and
  `SECRET` out of any captured deploy log before showing it.
- **`npm run lint` still exits 0 if oxlint fails to parse its own config** (carried forward
  from the previous handoff — it remains true). A positive control was run this session:
  linting a file containing `debugger` does report, so the config parses today.

## What was decided against

- **Running `--prune` during the publish.** `NEXT.md` said the deferral "comes due on the next
  publish", which read as *do it now*; the runbook says the opposite. Deferred correctly and
  the wording in `NEXT.md` was fixed so the next reader is not misled the same way.
- **Recording The Soft Boys find** (a 23k-monthly-listener artist reached naturally after eight
  bypass presses). Offered; the owner declined. It is *not* in the record and should not be
  cited as evidence — it is mentioned here only so a successor does not rediscover it and
  assume it was lost.
- **Changing the reroll notice's position.** On a first visit it lands over the open explainer
  rather than the journey. Raised to the owner as a one-line change; he did not ask for it, so
  it stands as designed.
