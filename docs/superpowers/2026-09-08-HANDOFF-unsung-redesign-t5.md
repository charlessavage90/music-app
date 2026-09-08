# Handoff — `UXR-T1`–`UXR-T5` complete, the redesign's first seam, 2026-09-08

**Role: SUPERSEDED ON NEXT ACTIONS by
[`2026-09-08-HANDOFF-unsung-redesign-t8.md`](2026-09-08-HANDOFF-unsung-redesign-t8.md),
2026-09-08 — NOT the current handoff.** `UXR-T6`–`T8` are done and the next task is `T9`, which
that note carries. **Its must-not-revert list still binds in full**, and two of its items were
re-confirmed there rather than restated: the name is Unsung.fm in the UI only, and the step
counts on the landing chips are measured. *(Was:)* the current handoff. Supersedes
[`2026-09-08-HANDOFF-lux-4-wire-and-card.md`](2026-09-08-HANDOFF-lux-4-wire-and-card.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

⚠ **A SECOND track is live and has its own current handoff** —
[`2026-09-07-HANDOFF-lbd-preregistration.md`](2026-09-07-HANDOFF-lbd-preregistration.md) for
`LBD-`, in a worktree at `C:\Users\charl\worktrees\music-app-lbd`. **Neither supersedes the
other**, and this one was written with that worktree live, which is why `NEXT.md` got a
surgical edit rather than the wholesale rewrite `closeout` A2-next prescribes (see below).

**A SEAM handoff — the plan's own first seam, chosen at authoring time.** The degradation
tell did not fire. Branch `unsung-redesign`, **PR #114** — addresses; `git` and `gh` own what
has landed.

---

## Start here

**Read, in this order:** the spec's §2 and §3
([`specs/2026-09-08-unsung-redesign-scope.md`](specs/2026-09-08-unsung-redesign-scope.md) —
the owner's seven decisions and `UXR-D1`–`D18`), then the plan from **`UXR-T6`**
([`plans/2026-09-08-unsung-redesign.md`](plans/2026-09-08-unsung-redesign.md)), then the log
([`2026-09-08-unsung-redesign-execution-log.md`](2026-09-08-unsung-redesign-execution-log.md))
for what the plan got wrong in `T1`–`T5`, because the same shapes recur in `T6`–`T11`.

**Next task is `UXR-T6`** (the card sheds facts, links, try-another and Dig deeper; gains
the detail button). `T6`–`T8` are the layout change and the highest-risk stretch; the plan's
second seam is after `T8`. **`T7` is where the plan is most likely to be wrong about the
repository** — it wires a new component into `JourneyList`, whose `PlayerBar` call `T5`
already changed; read the file, not the plan's excerpt of it.

**Two servers are needed for the screenshots every visual task ends in**, and both were
stopped at this closeout: the API on :8000 (**start it with `ARTISTPATH_GRAPH` pointing at
`builder/scratch/graph-lux4.bin`**, or the facts and links the detail moves will be null) and
Vite on :5173. The helper is `frontend/e2e/screenshot.mjs`; from Git Bash prefix
`MSYS_NO_PATHCONV=1` or the `/` argument becomes a Windows path.

## What this session did

1. Ran **`LUX-E6`** at the owner's instruction — figures owner
   `builder/analysis/2026-09-08-lux-e6-tag-vocabulary/README.md`. Changes nothing: genres
   stay deferred until he lifts it.
2. Wrote the **spec** and the **plan**, exported the mockup to
   `frontend/design/2026-09-08-unsung-redesign/`.
3. Executed **`UXR-T1`–`T5`** inline: tokens and faces; the name; the landing page; `GET
   /api/meta` and the badge; the player bar's progress and "Stop N of M".

## Claims an editor must NOT revert

- **The name is Unsung.fm in the UI only.** `artistpath` stays the package, artifact and
  identifier name (`UXR-D1`). A grep for "Artist Path" under `frontend/src`, `index.html`
  and `e2e/` is empty by design; `artistpath:` localStorage keys are identifiers.
- **`SAMPLE_JOURNEYS` and `TEASER` live in `frontend/src/lib/sampleJourneys.ts`**, not in
  `LandingPage.tsx` as the plan says — oxlint's fast-refresh rule. `T10`'s
  `landing-samples.spec.ts` imports from there.
- **The step counts on the chips are measured, not chosen** (3 / 4 / 6; teaser 5, artists
  *between*), on the served graph 2026-09-08. If `T10`'s spec fails, the served graph moved:
  update the constants, never weaken the test.
- **The `@theme` aliases stay until `UXR-T9` removes them** (`UXR-D17`). Deleting one early
  makes something transparent, and nothing sees transparent.
- **`Brand` is one `role="img"` with `aria-label="Unsung.fm"`**; tests select it by that
  role and name, not by heading. The plan's own test for it was self-contradictory and was
  corrected (log §2).
- **The badge renders nothing on failure** (UI-7) and the landing tests rely on that: the
  real `getMeta` rejects in jsdom and no mock is needed.
- **The bar's "Stop N of M" counts every artist including endpoints** (`UXR-D10`); the
  heading's "steps" (from `T8`) counts artists between. Two currencies, both named in code.

## Two things that are NOT owed, and read as if they might be

- **The mark.** `frontend/public/unsung-mark.png` is the owner's export from the Design
  project (the MCP truncates it at 256 KB). Every test passes without it; the page shows a
  broken image box until it lands. Not a session's item.
- **`UXR-D12`, the landing copy.** Flagged assumption, not a decision to remake: the
  mockup's copy is live, the 2026-08-07 lines are quoted in a comment at the h1. If he
  overrules, it is one edit.

## What I know that is not in the durable record

1. **`NEXT.md` got a surgical edit again, not the wholesale rewrite.** Same reason as the
   LUX-4 closeout: the `LBD-` worktree is live and a one-paragraph strike reconciles in either
   merge order. The outgoing-block demotion to `NEXT-ARCHIVE.md` is now **two closeouts in
   arrears**; the first closeout with no concurrent track does it.
2. **The plan was wrong about the repository three times in five tasks**, all small, all in
   the log: a self-contradictory test (§2), constants exported from a component file (§3), and
   a text query that a new chip hijacked (§3). Expect the same rate in `T6`–`T11`, and expect
   `T7`'s `JourneyList` excerpt to be stale.
3. **The Deezer id gap deferral's condition is now ARMED.** It reads "the first rebuild after
   `LUX-4` merges"; `LUX-4` merged 2026-09-08 (PR #112). No rebuild has happened, so it is not
   discharged — but the next rebuild of the served lineage must carry the Deezer re-extract,
   and nothing in this plan rebuilds.
4. **Snyk ran on `api/` at `T4`** (one pre-existing Low, nothing new). `frontend/` is scanned
   at `T10` per the plan; `T1`–`T5`'s frontend diff has not been scanned yet.
5. **Deezer previews report ~29 s**, so the bar says 0:29 while the card says 0:30. Left
   honest; the owner may prefer the card to say what the clock says. His call, unasked.

## Nothing is in flight

No background jobs, no subagents, no half-written directories. Ports 8000 and 5173 are free
— this session stopped the two servers it started. The working tree is clean and everything
is pushed.
