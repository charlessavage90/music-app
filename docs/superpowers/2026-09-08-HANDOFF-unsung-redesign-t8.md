# Handoff — `UXR-T6`–`UXR-T8` complete, the redesign's second seam, 2026-09-08

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-08-HANDOFF-unsung-redesign-t5.md`](2026-09-08-HANDOFF-unsung-redesign-t5.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

⚠ **A SECOND track is live and has its own current handoff** —
[`2026-09-07-HANDOFF-lbd-preregistration.md`](2026-09-07-HANDOFF-lbd-preregistration.md) for
`LBD-`, in a worktree at `C:\Users\charl\worktrees\music-app-lbd`, which advanced to **Task 4**
while this work ran. **Neither supersedes the other**, and this one was written with that
worktree live — which is again why `NEXT.md` got a surgical edit rather than a wholesale
rewrite (below).

**A SEAM handoff — the plan's own second seam, chosen at authoring time.** The degradation
tell did not fire. Branch `unsung-redesign`, **PR #114** — addresses; `git` and `gh` own what
has landed.

---

## Start here

**Read, in this order:** the spec's §2 and §3
([`specs/2026-09-08-unsung-redesign-scope.md`](specs/2026-09-08-unsung-redesign-scope.md) — the
owner's seven decisions and `UXR-D1`–`D18`), then the plan from **`UXR-T9`**
([`plans/2026-09-08-unsung-redesign.md`](plans/2026-09-08-unsung-redesign.md)), then the log
([`2026-09-08-unsung-redesign-execution-log.md`](2026-09-08-unsung-redesign-execution-log.md))
§§7–9 for what the plan got wrong in `T6`–`T8`, because the same shapes recur.

**Next task is `UXR-T9`** (the remaining surfaces restyled, and the `@theme` aliases removed).
Then `T10` (the real-browser suite) and `T11` (the record). **`T9` is where a token deletion
can make something transparent**, which no test sees — `UXR-D17` is why the aliases survived
this long, and the check is the one `T1` used: every `var(--color-*)` referenced under `src/`
resolves to a definition in `index.css`.

**The plan's section numbers are one behind the log's.** The closeout at the first seam took
`## §6`, so `T6` is logged at §7, `T7` at §8, `T8` at §9. `T9` appends **§10**.

**Two servers are needed for the screenshots every visual task ends in**, and both were
stopped at this closeout: the API on :8000 (**start it with `ARTISTPATH_GRAPH` pointing at
`builder/scratch/graph-lux4.bin`**, or the facts and links in the detail will be null) and Vite
on :5173. The helper is `frontend/e2e/screenshot.mjs`; from Git Bash prefix `MSYS_NO_PATHCONV=1`
or the `/` argument becomes a Windows path.

## What this session did

Executed **`UXR-T6`, `T7` and `T8`** — the card stripped to the listening surface, the artist
detail docked at `lg` and a bottom sheet below it, and the journey page's header with the
brand, Share, the title and its steps tile. Reasoning per task in the log §§7–9.

## Claims an editor must NOT revert

- **The card carries no facts, no links, no cycling and no bypass.** All four are in
  `ArtistDetail` (`UXR-D2`). The card keeps `clipIndex` and `onDeadIndex` deliberately — it
  renders the clip, so it is what can see one die.
- **Every artist has a detail button, endpoints included.** Only "Dig deeper" is
  interior-only, and that is asserted inside the detail, never on the card.
- **`ArtistDetail.test.tsx` uses a distinct MBID per test.** `useClip` caches on `mbid:index`
  at module scope for ten minutes and nothing clears it between tests; a shared id serves one
  test's `candidateCount` to the next. The plan's version shared one and would have failed
  looking like a component bug.
- **The rail runs first dot to last, not the full height** (`top-[41px] bottom-[41px]`). The
  owner's 2026-07-28 request was *full height, and no arrow at the foot*; the no-arrow half is
  untouched, the other half is the approved mockup, and it was flagged to him before `T6`.
- **`max-w-[1200px]` on the journey page was pulled forward from `T8` into `T7`.** `T9`+ must
  not re-apply it. At 620px with the 400px dock the page scrolled sideways at 1280.
- **`PathIntro` has no `count` prop and states no number.** The step count lives once, in
  `JourneyHeading`'s tile (`UXR-D6`). Its copy now names where the control is; reverting it to
  "along the bottom of their card" sends the reader to a card that has nothing there.
- **Queries for an artist's name must go by role or by test hook, never by text.** With a
  detail open the same name renders in the card, the dock and the sheet — three nodes in
  jsdom, which has no breakpoints. This has now broken a test in three separate tasks.
- **`pressBypass` in `PathPage.test.tsx` takes the second detail button.** The first card is an
  endpoint and its detail has no Dig deeper at all.

## Two things that are NOT owed, and read as if they might be

- **`e2e/responsive.spec.ts` is red** and `T10` owns it: its `LUX-4` case looks for the
  streaming links inside an interior *card*, and they are in the detail now. It is Playwright,
  so it is not in `npm test` and gates nothing before `T10`.
- **`UXR-D12`, the landing copy.** Unchanged flagged assumption from the first seam, not a
  decision to remake.

## What I know that is not in the durable record

1. **`NEXT.md` got a surgical edit again, not the wholesale rewrite `closeout` A2-next
   prescribes** — the `LBD-` worktree is live and advanced during this session, and a
   one-paragraph strike reconciles in either merge order. **The outgoing-block demotion is NOT
   in arrears despite what the previous handoff said:** `NEXT.md` holds exactly one status
   block, the superseded ones are already in `NEXT-ARCHIVE.md`, and the file is 427 lines. What
   the previous two closeouts deferred was the *wholesale rewrite*, not a demotion, and there
   is nothing queued to demote.
2. **The owner's mark landed mid-session.** `frontend/public/unsung-mark.png` (1152×1152,
   511 KB) appeared in the working tree at 16:32 and now renders in every screenshot. **It is
   still untracked and this session did not commit it** — it is not this session's file. **The
   deploy needs it in the repo**, so committing it is one line and his call.
3. **Snyk did not run on this frontend diff.** The plan scans `frontend/` at `T10`; `T1`–`T5`'s
   diff was already unscanned and `T6`–`T8`'s now joins it. Credentials are expired and the MCP
   server failed to connect again this session — his hands, and it opens a browser.
4. **Deezer previews still report ~29 s** against the card's nominal 0:30. Unchanged from the
   first seam and still his call, unasked.

## Nothing is in flight

No background jobs, no subagents, no half-written directories. Ports 8000 and 5173 are free —
this session started both and stopped both at closeout. The working tree is clean apart from
the owner's untracked mark, and everything is pushed.
