# Handoff — frontend mockup adoption, Tasks 1–7 of 13, 2026-07-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-28-HANDOFF-password-removal-complete.md`](2026-07-28-HANDOFF-password-removal-complete.md)
**on next actions only.** It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

> **⚠ The two tracks are orthogonal, not sequential.** That document is about **deployed
> infrastructure**; this one is about **half-finished frontend work that is not deployed**. This
> handoff discharges **nothing** in it — and in particular **the iPhone test it says is owed is
> still owed**, on its own axis, unaffected by anything here. If you landed on this document
> from a citation and your question is about the live site, read that one instead.

**Written at a planned seam**, not a mid-flight retirement. The seam was chosen when the plan
was authored, at the point where the landing screen, the API route and the card layer are all
committed artifacts. Nothing below depends on anything held only in a session's head.

**Nothing is in flight.** No subagents, no background jobs, no listeners on 8000, 5173, 8138 or
8139 — all four checked free. Nothing was started by this session.

Record: [`2026-07-28-frontend-mockup-adoption-execution-log.md`](2026-07-28-frontend-mockup-adoption-execution-log.md).
Plan: [`plans/2026-07-28-frontend-mockup-adoption.md`](plans/2026-07-28-frontend-mockup-adoption.md).
Spec: [`specs/2026-07-28-frontend-mockup-adoption-design.md`](specs/2026-07-28-frontend-mockup-adoption-design.md).

---

## The one-line state

**Tasks 1–7 are done, committed and pushed; Tasks 8–13 are not started.** The landing screen is
finished and every journey card carries the mockup's treatment. **The loading screen and the
reroll message are built but not wired**, so the path page still shows the old
`Building your path…` line. Nothing is broken; the redesign is not yet visible end to end.

## Your job

**Tasks 8–13 of the plan, in order.** Task 8 is `JourneyList` and `PlayerBar`; 9–11 are the three
new components; 12 wires them into `PathPage`; 13 is full verification and the PR.

**Everything you need is in the plan.** It carries complete code and complete test code per task.
Read the execution log's §8 first — it is five items long and every one of them is a thing the
plan will let you get wrong.

## Which documents are now wrong, and in which direction

- **The plan's Task 9 code block says `w-13 h-13`.** That is not a Tailwind default size. Use
  `w-[52px] h-[52px]`. The plan flags this at the block; the correction was already applied in
  Task 7.
- **The plan's Task 12 test snippet names a `renderAt` helper** in `PathPage.test.tsx`. **Verify
  its real signature before using it.** Task 5's equivalent snippet was wrong the same way — that
  file's helper is `setup()`, not a bare `render`. Treat the plan's test snippets as intent, not
  as transcription.
- **The plan's Task 13 is the only place Snyk appears. It has already run** — both packages,
  0 issues, at the seam. Do not treat it as outstanding, but do re-run it after Tasks 8–12
  add code.

## What was overturned and must NOT be reverted

- **The `UI-7` test in `useEndpoints.test.tsx` is deliberately MIXED** — one lookup fails, one
  succeeds. The obvious both-fail version is **vacuous**: when `Promise.all` rejects, `.then`
  never runs, so state stays at its initial `null`, which is what the assertion reads. It passed
  with the error handling removed. Do not "simplify" it back. The reasoning is a comment in the
  file and the evidence is execution log §4.
- **`e2e/responsive.spec.ts` locates the artist name by `data-testid`, not `.font-semibold`.**
  Reverting that re-couples a test to a Tailwind class on the element the redesign restyles.
- **`env(safe-area-inset-bottom)` in `PlayerBar.tsx` stays, and `viewport-fit=cover` stays
  absent** (`UI-D3`). The deferral in `NEXT.md` is intact and deliberate.
- **The design export is excluded from oxlint.** It is reference material we do not own.

## What has already been updated — do not re-edit

`docs/README.md` (four new rows), `NEXT.md`, `TEST-QUEUE.md` (new entry at top), the plan's role
header, and the previous handoff's role line.

**The doc audit ran** — `scripts/docs-lint.sh` plus the `doc-auditor` agent. The lint's three
hard failures were all this session's own documents and all are fixed; the lint now reports
**zero**.

⚠ **The agent's report is at [`../2026-07-28-doc-audit-frontend-mockup-adoption.md`](../2026-07-28-doc-audit-frontend-mockup-adoption.md)
and three of its six findings are FALSE.** It was dispatched while this closeout was still
editing the documents it audits, so it read a stale tree: its two HIGH findings and one MEDIUM
are race artifacts, verified false immediately afterwards. **It carries a banner saying so —
read that before acting on any line of it.** Its verification half is real and was kept. Two
findings survived and are already applied.

## What I know that is not in the durable record

**Two items, both small.**

- **`npm run lint` exits 0 when oxlint fails to parse its own config.** I hit this adding a `//`
  comment key to `.oxlintrc.json`, which the schema rejects. A broken lint config is silent here,
  so if lint output ever looks suspiciously short, check it parsed.
- **The `git commit` warnings about LF→CRLF are normal in this tree** and appear on every commit
  touching a text file. `core.autocrlf` is true. Not a defect and not worth investigating.

## What was decided against

- **Continuing inline into Tasks 8–13.** I was not showing the degradation tell, and it would
  have been faster in wall-clock terms. Declined because "the controller is warm" is explicitly
  not a reason to push through a planned seam, and the seam exists precisely so this is cheap.
- **Running the e2e suite at the seam.** It needs a live API on `:8000` and is Task 13's job;
  starting one here would leave a listener nothing is queued to use.
- **Fixing the pre-existing `vite.config.ts` triple-slash lint warning.** Unrelated to this work.
