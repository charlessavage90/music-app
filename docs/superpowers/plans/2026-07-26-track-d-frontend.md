# Track D — Frontend Implementation Plan

> **⚠ EXECUTED 2026-07-26 — do not execute again.** Outcomes, including three defects found
> in this plan itself, are in
> [`../2026-07-26-gate2-track-d-execution-log.md`](../2026-07-26-gate2-track-d-execution-log.md).
> Where that log and this plan disagree, **the log wins**. Superseded figures are struck
> inline below as well as listed there.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended
> for this plan — see "Execution recommendation" below, which **reverses** the recommendation
> the Track A completion handoff made before the code had been read) or
> superpowers:subagent-driven-development to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the app usable on a phone and make it tell the truth when something fails —
the seven items the owner fenced into Track D — without touching routing, the graph, or the
cost function.

**Architecture:** All work is inside `frontend/`. Layout goes mobile-first with Tailwind's
`sm:` breakpoint (640 px) restoring today's desktop appearance exactly; no markup is
duplicated across breakpoints, because the existing e2e spec resolves bypass buttons by role
and Playwright's strict mode fails on a locator matching two elements. Failure surfacing
reuses machinery that already exists — a rejected `play()` is routed into the player's
existing `onError` channel rather than given a new one — so the four player invariants
confirmed by the team review keep their existing coverage.

**Tech Stack:** React 19, React Router 7, Tailwind CSS v4, TypeScript ~6.0, Vitest 4 +
Testing Library (jsdom), Playwright 1.61, oxlint.

**Governing documents.** The design
[`specs/2026-07-26-gate2-deploy-and-telemetry-design.md`](../specs/2026-07-26-gate2-deploy-and-telemetry-design.md)
§11 (as amended by `DEP-29`) and the review
[`findings/2026-07-26-gate1-gate2-team-review.md`](../findings/2026-07-26-gate1-gate2-team-review.md)
§5 (`TR-16`), which is where the six-item fence is recorded. The seventh item is new — see
"Scope" below.

**Identifier series: `TKD-`.** Reserved by this plan for the Track D execution log. Checked
against `TKA-`, `TR-`, `DEP-`, `FMS-`, `CLM-`, `STC-`, `CNS-`, `MKS-`, `SYN-`, `CWD-`,
`DRV-`, `BYP-`, `ASC-`, `TF-` — no collision. Do not reuse a `TR-` or `DEP-` number for a
Track D finding.

---

## Scope: seven items, and where the seventh came from

The owner fenced Track D at **six** items (`TR-16`). A **seventh** was added 2026-07-26,
after the owner ran the Track A use-the-app queue entry and reported a wrong-destination
defect. He accepted it into Track D in the same message. The queue entry recording it is
`TEST-QUEUE.md`'s `DONE — 2026-07-26 — six fixes under the bonnet, and one you can see`.

| # | item | task | source |
|---|---|---|---|
| 1 | Responsive layout | 1 | `TR-16` |
| 7 | Search box does not un-choose an artist when you type over them | 2 | owner, in use, 2026-07-26 |
| 2 | Search failure vocabulary | 3 | `TR-16` |
| 6 | iOS input attributes | 4 | `TR-16` |
| 3 | Request timeouts | 5 | `TR-16` |
| 4 | Surfacing a failed `play()` | 6 | `TR-16` |
| 5 | Catch-all route | 7 | `TR-16` |

**Two `TR-16` claims are corrected here, and the corrections are load-bearing.** Both were
verified against source on 2026-07-26 before this plan was written.

- **`TR-16` says `grep` over `frontend/src` returns *zero* hits for any breakpoint or media
  query. It returns six** — `@media (max-width: 1024px)` in `src/App.css`. **`TR-16`'s
  conclusion is nevertheless correct**, because `App.css` is imported by nothing and none of
  its selectors (`#center`, `#next-steps`, `#docs`, `#spacer`) exist in any component: it is
  dead Vite scaffold. **The consequence for this plan is a trap to avoid:** any verification
  of Task 1 that greps for `@media` **passes before the fix**. That is the `FMS-P1` /
  `TR-2` vacuous-check pattern, which this project has now been bitten by twice, and it is
  why Task 1 is verified by measuring rendered geometry in a real browser instead.
- **`TR-16` also lists safe-area insets among the zero hits, and there it is right** —
  but the `<meta name="viewport" content="width=device-width, initial-scale=1.0">` tag
  **is already present** in `frontend/index.html`. Do not add it. Responsive CSS will take
  effect as soon as it is written.

**`App.css` is dead and Task 1 deletes it.** It is not part of the fence; it is removed
because Task 1 is the task that establishes what the app's responsive styling is, and
leaving a dead stylesheet with contradicting breakpoints beside it guarantees a future
reader is misled exactly as `TR-16` was. `closeout`'s orphaned-module sweep would take it
anyway.

**Not in Track D, and do not add them:** accessibility (ARIA, keyboard, focus), link
previews / Open Graph, and path-latency work. All three were considered at the fence and
**deferred to Gate 3 by the owner** — see the review's §6. ~~`DEP-30` (the Playwright `EPERM`
fix) is **already done in Track A**; `playwright.config.ts` already sets
`outputDir: '../.playwright-results'`. Do not redo it.~~ **⚠ WRONG, corrected on execution
(`TKD-3`): it was only PARTLY done.** The repo root is under OneDrive too, so the run still
`EPERM`ed on two consecutive attempts and blocked Task 1. `outputDir` is now `os.tmpdir()`.
**`DEP-30` is discharged from Track D, not from Track A.**

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Every new test must fail against unmodified source first, and for the right reason.**
  Record what the RED run actually said — not that it failed, but the message. This is the
  standing instruction inherited from the Track A plan, written because that plan's own
  predecessor prescribed a test that could not fail (`FMS-P1`), and because `TR-2` found the
  same pattern in the Gate 2 design. `TKA-1` is the worked example of it paying off.
- **Touch no routing weight, no cost-function term, no graph, no `ApiConfig` default.**
  `api/` is not edited by this plan at all. The path-quality pause is intact and this plan
  is not a resume signal.
- **No new runtime or dev dependencies.** `uv.lock`'s absence is a Track B decision
  (`TKA-12`) and the Docker image is the release artifact with no CI (`DEP-32`); a new
  frontend dependency changes what Track C ships. Everything here is achievable with what is
  in `package.json`.
- **Mobile-first.** Unprefixed utilities describe the phone; `sm:` (≥640 px) restores the
  desktop. Never write a `max-width` media query — mixing directions is how the two
  breakpoint systems in this repo came to disagree.
- **No markup duplicated across breakpoints.** `e2e/path.spec.ts:22` resolves a bypass
  button by role inside `ol li`; two copies make that locator match twice and Playwright
  strict mode fails the existing suite.
- **Run all four suites between tasks.** They take well under a minute in total
  (`api` ~1.3 s, frontend ~4 s); there is no reason to skip the gate. From `frontend/`:
  `npm test`, `npm run lint`, `npm run build`.
- **`npm run test:e2e` requires the API on :8000.** Playwright starts the Vite dev server
  itself (`reuseExistingServer: true`) but never the API. As of 2026-07-26 both are already
  running detached — frontend PID 211432, api PID 231092 — and the api answers `/health`
  with `graph_sha256 4cb84ef9…`, the adopted artifact. If they are gone, start the API with
  `uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000` from `api/`.
- **`UV_LINK_MODE=copy` on every `uv` command.** OneDrive breaks hardlinks.
- **Append to the execution log per task, not at closeout** —
  `docs/superpowers/2026-07-26-gate2-track-d-execution-log.md`, identifiers `TKD-`.
  Decisions and reasoning, not narration. This is what makes the seam below cheap.
- **Snyk `snyk_code_scan` on `frontend/` at Task 8**, per the global instruction; fix and
  rescan until clean.
- **Baseline, measured 2026-07-26 at `7fe9b22`:** frontend **65 tests / 12 files**, e2e
  **3**, api 180, builder 115. Each task below states the expected frontend total after it.
  A count that does not match means something else changed — stop and find out what.

## Execution recommendation

**Inline, by a session that has read the frontend — and this reverses what the Track A
completion handoff predicted.** That handoff named Track D as the condition that would flip
Track A's inline recommendation, on the reasoning that Track D is "six largely independent
items, different files, no shared interfaces". **Having now read the code, that premise does
not hold**, and the reversal is recorded here rather than quietly ignored:

- **Three of the seven items land in one file.** Tasks 2, 3 and 4 all edit
  `ArtistSearch.tsx`, each on top of the last — Task 3 rewrites the effect beside the
  `onChange` Task 2 installed, Task 4 adds attributes to the same `<input>`. Task 5 edits
  `PathPage.tsx`, which Task 1 also edits. This is not the independent shape the handoff
  assumed.
- **There is no fan-out to win.** `subagent-driven-development` dispatches one fresh subagent
  per task *sequentially* with review between; independence buys parallelism only where
  tasks actually run in parallel, and none here do. On speed the two options are the same
  minus per-dispatch overhead, which favours inline.
- **The plan is unusually prescriptive.** Every task carries complete code, exact commands,
  exact expected suite totals and the commit message. The per-task review a fresh reviewer
  adds is lowest precisely when there is least judgement left in the task.
- **Where judgement does remain, a cold subagent is the weaker instrument, not the
  stronger.** Task 1's phone layout needs someone to look at it; Task 5's `usePath` test must
  be adapted to a helper this plan did not read in full; Task 5 carries a deliberate typo
  trap in `getTrack`. All three are handled better by someone who has the files in context
  than by someone re-deriving them from the plan text.
- **Token cost compounds the same way.** Eight subagents each re-reading most of
  `frontend/src` to make a correct edit is the expensive path, and it buys none of the
  above.
- **The safety nets already absorb the risk subagent review would.** Red/green per task with
  the RED message recorded, a four-suite gate between tasks that runs in under a minute,
  `npm run build` as typecheck, oxlint, the e2e suite as a desktop regression gate, and a
  per-task commit with a pathspec. Track A is the direct precedent: ten tasks, inline, every
  expected count hit first time.

**What would reverse this back.** If the session executing this has **not** read the
frontend — a cold session picking the plan up tomorrow — the warm-controller argument
evaporates and subagent-driven becomes the better call, because then the context has to be
paid for either way and per-task isolation at least keeps it bounded. The same applies if
the executing session is already long when it arrives.

**Handoff seam after Task 4.** At that point the search box and the phone layout are both
finished and committed — a coherent artifact a fresh session can read cold — and Tasks 5–8
share nothing with them. If the session running this is long by Task 4, retire it there.
**A session resuming at Task 5 is a cold session**, so the paragraph above applies to it:
Tasks 5–8 touch six files across four concerns, and subagent-driven is the better call for
that half.

---

## File Structure

| file | disposition | responsibility after this plan |
|---|---|---|
| `frontend/src/App.css` | **Delete** (Task 1) | — dead Vite scaffold |
| `frontend/src/components/ArtistCard.tsx` | Modify | Card row; wraps its bypass buttons to a second line on phones |
| `frontend/src/components/PlayerBar.tsx` | Modify | Fixed bottom bar; clears the iOS home indicator |
| `frontend/src/routes/LandingPage.tsx` | Modify | Owns the chosen pair; `null` from a search box un-chooses |
| `frontend/src/routes/PathPage.tsx` | Modify | Page chrome; passes retry down |
| `frontend/src/components/ArtistSearch.tsx` | Modify | Text ⇄ selection consistency, search status, iOS attributes |
| `frontend/src/api/client.ts` | Modify | Adds `TimeoutError` and a per-call timeout |
| `frontend/src/hooks/usePath.ts` | Modify | Classifies timeouts; exposes `retry()` |
| `frontend/src/components/PathStatus.tsx` | Modify | Gains the timeout message and a Try again control |
| `frontend/src/player/Player.ts` | Modify | A rejected `play()` reaches the error channel |
| `frontend/src/routes/NotFound.tsx` | **Create** (Task 7) | The catch-all page |
| `frontend/src/App.tsx` | Modify | Adds the `*` route |
| `frontend/e2e/responsive.spec.ts` | **Create** (Task 1) | Phone-viewport geometry regression |

---

## Task 1: Responsive layout

**Files:**
- Modify: `frontend/src/components/ArtistCard.tsx:35-82`
- Modify: `frontend/src/components/PlayerBar.tsx:9`
- Modify: `frontend/src/routes/LandingPage.tsx:32,44-51`
- Modify: `frontend/src/routes/PathPage.tsx:42`
- Delete: `frontend/src/App.css`
- Test: `frontend/e2e/responsive.spec.ts` (create)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: no new exports. Later tasks add markup **inside** the elements this task
  restructures — Task 3 adds a status line under the search input, Task 6 changes nothing
  visual. No later task may reintroduce a fixed width on the card row.

**Why the test is an e2e and not a Vitest test.** jsdom computes no layout and applies no
media queries, so a jsdom test of this change can only assert that certain class strings are
present — which is a test of the implementation, passes for the wrong reason, and is exactly
the vacuous-check pattern named in Global Constraints. The defect `TR-16` describes is
geometric ("the artist name is squeezed toward zero width"), so it is measured
geometrically. **Frontend Vitest total is unchanged by this task: 65.**

**The one design decision in Track D, and the owner may overrule it.** On a phone the two
bypass buttons move to their own full-width row beneath the artist, splitting it evenly;
cover art, name and the play button keep the top row. The alternative considered was
shrinking the buttons to icons and keeping one row, which was rejected because "✕ Not for
me" and "✓ I know them" are two signals the owner has said mean different things, and an
unlabelled icon pair is where that distinction goes to die. Desktop is unchanged.

- [ ] **Step 1: Write the failing e2e test**

Create `frontend/e2e/responsive.spec.ts`:

```ts
import { expect, test } from '@playwright/test';

// TR-16: on a 390px phone the card row's non-shrinkable elements exceed the
// available width and the artist name — the only content that matters — is
// squeezed toward zero. Measured in a real browser because jsdom computes no
// layout: a jsdom test here could only assert class names and would pass before
// the fix (the FMS-P1 / TR-2 vacuous-check pattern).
test.use({ viewport: { width: 390, height: 844 } });

test('a journey is usable at phone width', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('From').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('To').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /find path/i }).click();

  await expect(page.locator('ol li').first()).toBeVisible();

  // 1. The page must not scroll sideways.
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);

  // 2. The artist name must get real width, not a sliver. 160px is well under
  //    what the fixed layout gives it and well over what the broken one does.
  const name = page.locator('ol li .font-semibold').first();
  const box = await name.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.width).toBeGreaterThan(160);

  // 3. Both bypass signals stay reachable and distinguishable — the interior
  //    cards are the only ones that carry them.
  const interior = page.locator('ol li').nth(1);
  await expect(interior.getByRole('button', { name: /not for me/i })).toBeVisible();
  await expect(interior.getByRole('button', { name: /i know them/i })).toBeVisible();
});
```

- [ ] **Step 2: Run it to verify it fails**

Run from `frontend/`: `npm run test:e2e -- responsive`
Expected: FAIL. The likely first failure is assertion 1 (horizontal overflow) or 2 (name
width at or near zero). **Record the actual numbers reported** — they are the before-figures
for the execution log, and they are what proves the test was not vacuous.

- [ ] **Step 3: Make the card row wrap on phones**

In `frontend/src/components/ArtistCard.tsx`, replace the returned JSX (lines 35–82) with:

```tsx
  return (
    <div
      className={`flex flex-wrap items-center gap-x-3 gap-y-0 sm:gap-x-4 rounded-xl px-3 py-3 sm:px-4 border border-[var(--color-border)] ${
        isPlaying ? 'bg-[var(--color-accent)]/15' : 'bg-[var(--color-surface)]'
      }`}
    >
      <div
        className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg flex-none bg-[var(--color-border)] bg-cover"
        style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
        aria-hidden
      />
      <div className="flex-1 min-w-0">
        <div className="font-semibold truncate">{artist.name}</div>
        <div className="text-sm text-[var(--color-muted)] truncate">
          {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
        </div>
        {isPlaying && <div className="text-xs text-[var(--color-accent)] mt-0.5">▮▮▮ now playing</div>}
      </div>
      {!isEndpoint && (
        // On a phone this wrapper is full width and ordered last, so it takes a
        // row of its own beneath the artist and the two signals stay labelled.
        // From sm up it collapses back to an ordinary inline pair and the desktop
        // row is exactly what it was. One copy of the markup, deliberately: the
        // e2e spec resolves these by role and Playwright strict mode fails on two.
        <div className="order-last w-full mt-3 flex gap-2 sm:order-none sm:w-auto sm:mt-0">
          <button
            type="button"
            onClick={() => onBypass(artist.mbid, 'dislike')}
            className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-full border border-[var(--color-away)]/40 text-[var(--color-away)]"
          >
            ✕ Not for me
          </button>
          <button
            type="button"
            onClick={() => onBypass(artist.mbid, 'known')}
            className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-full border border-[var(--color-dig)]/40 text-[var(--color-dig)]"
          >
            ✓ I know them
          </button>
        </div>
      )}
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        disabled={!playable}
        // The card that owns the audio toggles it. Calling onPlay here would
        // re-seek to zero, which is why only the bottom bar could pause.
        onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        className="w-10 h-10 rounded-full flex-none bg-[var(--color-accent)] text-white flex items-center justify-center disabled:opacity-30"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
    </div>
  );
```

- [ ] **Step 4: Clear the iOS home indicator in the player bar**

In `frontend/src/components/PlayerBar.tsx`, replace the wrapper `className` on line 9 with:

```tsx
    <div className="fixed bottom-0 inset-x-0 border-t border-[var(--color-border)] bg-[var(--color-surface)] px-4 pt-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] flex items-center gap-3">
```

- [ ] **Step 5: Give the two pages phone padding**

In `frontend/src/routes/PathPage.tsx` line 42, replace the `<main>` className with:

```tsx
    <main className="max-w-2xl mx-auto px-4 py-6 sm:py-10 pb-32">
```

In `frontend/src/routes/LandingPage.tsx` line 32, replace the `<main>` className with:

```tsx
    <main className="max-w-xl mx-auto px-4 py-10 sm:py-16">
```

and replace the "Find path" button's className (line 48) with:

```tsx
        className="mt-6 w-full sm:w-auto rounded-lg bg-[var(--color-accent)] px-4 py-2 font-medium disabled:opacity-40"
```

- [ ] **Step 6: Delete the dead scaffold**

```bash
git rm frontend/src/App.css
```

Then confirm nothing referenced it — this must return no hits:

```bash
grep -rn "App.css" frontend/src frontend/index.html
```

- [ ] **Step 7: Run the e2e test to verify it passes**

Run: `npm run test:e2e -- responsive`
Expected: PASS. Record the after-figures for the name's width and the overflow.

- [ ] **Step 8: Run every suite**

Run from `frontend/`: `npm test && npm run lint && npm run build && npm run test:e2e`
Expected: frontend **65 passed**, e2e **4 passed**, lint clean, build clean. The three
pre-existing e2e specs must still pass — they are the check that desktop did not move.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/ArtistCard.tsx frontend/src/components/PlayerBar.tsx \
        frontend/src/routes/LandingPage.tsx frontend/src/routes/PathPage.tsx \
        frontend/e2e/responsive.spec.ts
git commit -- frontend/src frontend/e2e -m "Make the app usable at phone width

The card row's non-shrinkable elements exceeded 390px, squeezing the artist
name — the only content that matters — toward zero (TR-16). The two bypass
buttons now take a row of their own below the artist on phones and collapse
back to an inline pair from sm up, so desktop is unchanged. One copy of the
markup: the e2e spec resolves those buttons by role and Playwright strict mode
fails on two.

Verified by rendered geometry in a real browser rather than by class names.
A jsdom test could only assert the classes and would have passed before the
fix, which is the vacuous-check pattern of FMS-P1 and TR-2.

Deletes src/App.css: dead Vite scaffold, imported nowhere, whose six
max-width:1024px blocks are why TR-16 reported zero media queries and was
both wrong in its evidence and right in its conclusion.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 2: Typing over a chosen artist un-chooses them

**Files:**
- Modify: `frontend/src/components/ArtistSearch.tsx:9,45-50,57-63`
- Modify: `frontend/src/routes/LandingPage.tsx:38-39`
- Test: `frontend/src/components/ArtistSearch.test.tsx`, `frontend/src/routes/LandingPage.test.tsx`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `ArtistSearch`'s prop becomes **`onSelect: (artist: Artist | null) => void`**.
  `null` means "there is no longer a chosen artist in this box". Tasks 3 and 4 keep this
  signature unchanged.

**The defect, from source.** `LandingPage` holds `to` as an `Artist`; `ArtistSearch` holds
`query` as text. `onSelect` is called from exactly one place — `choose()` — which runs only
when a dropdown entry is clicked. Typing calls `setQuery` and nothing else, so `to` keeps
the previously chosen artist, `ready` stays true, "Find path" stays enabled, and the app
routes to the artist the user just typed over. **It is not a race with the autocomplete:**
waiting for the dropdown does not help, because only clicking an entry writes the selection.
The "New path" prefill did not introduce this — it removed what was masking it, since both
boxes previously started empty and the button therefore started disabled.

- [ ] **Step 1: Write the failing tests**

Add to `frontend/src/routes/LandingPage.test.tsx`:

```tsx
test('typing over a prefilled artist disables "Find path" until one is chosen again', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  const dest = screen.getByLabelText('To');
  await user.clear(dest);
  await user.type(dest, 'wilco');

  // The box and the page must not disagree about who is chosen. Before this
  // fix the button stayed live and routed to Daft Punk — the artist the user
  // had just typed over — with no way to tell why.
  expect(screen.getByRole('button', { name: /find path/i })).toBeDisabled();
});

test('a single edited character is enough to un-choose', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  await user.type(screen.getByLabelText('To'), 'x');

  expect(screen.getByRole('button', { name: /find path/i })).toBeDisabled();
});
```

Add to `frontend/src/components/ArtistSearch.test.tsx`:

```tsx
test('reports null once the text no longer matches the chosen artist', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  const onSelect = vi.fn();
  render(
    <ArtistSearch
      label="To"
      initial={{ mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 1 }}
      onSelect={onSelect}
    />,
  );

  // Arriving prefilled is not an edit and must not report anything.
  expect(onSelect).not.toHaveBeenCalled();

  await user.type(screen.getByLabelText('To'), '!');

  expect(onSelect).toHaveBeenCalledWith(null);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `npm test -- LandingPage ArtistSearch`
Expected: all three FAIL. The two `LandingPage` tests fail on `expect(button).toBeDisabled()`
— the button is enabled, which **is the defect**. The `ArtistSearch` test fails on
`onSelect` never having been called. Record these messages; a failure for any other reason
means the test is not exercising the defect.

- [ ] **Step 3: Widen the prop and clear on divergence**

In `frontend/src/components/ArtistSearch.tsx`, change the prop type on line 9:

```tsx
  /** An artist, or null when the box no longer holds a chosen one. */
  onSelect: (artist: Artist | null) => void;
```

Replace the `<input>` element (lines 57–63) with:

```tsx
      <input
        id={inputId}
        className="w-full rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] px-3 py-2 outline-none focus:border-[var(--color-accent)]"
        value={query}
        onChange={(e) => {
          const next = e.target.value;
          setQuery(next);
          // Typing away from the chosen artist un-chooses them. The text and the
          // selection are separate state, and nothing else reconciles them: left
          // alone, "Find path" stays live and routes to the artist you just typed
          // over. Not a race with the dropdown — only clicking an entry chooses,
          // so waiting for it never helped.
          if (selectedName.current !== null && next !== selectedName.current) {
            selectedName.current = null;
            onSelect(null);
          }
        }}
        autoComplete="off"
      />
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `npm test -- LandingPage ArtistSearch`
Expected: PASS, including the four pre-existing `LandingPage` tests. In particular
`a prefilled pair can be sent straight back off without retyping` must still pass — it does
no typing, so nothing is un-chosen.

`LandingPage.tsx` needs no edit: `setFrom` and `setTo` are
`Dispatch<SetStateAction<Artist | null>>` and already accept `null`. Confirm with
`npm run build` rather than by assumption.

- [ ] **Step 5: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend **68 passed**.

- [ ] **Step 6: Commit**

```bash
git commit -- frontend/src -m "Un-choose an artist when the user types over them

Found by the owner in use, 2026-07-26. The box held the text and the page held
the previously chosen artist, and nothing reconciled them: typing a new
destination over a prefilled one left \"Find path\" enabled and routed to the
old artist, with nothing on screen to say why.

Not a race with the autocomplete — waiting for the dropdown never helped,
because only clicking an entry writes the selection. Pre-existing since the
landing page was built; the \"New path\" prefill removed what was masking it,
since both boxes previously started empty and the button started disabled.

onSelect now takes Artist | null, and the button going dead is the signal.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 3: A search that failed says so

**Files:**
- Modify: `frontend/src/components/ArtistSearch.tsx:14,21-43,64-81`
- Test: `frontend/src/components/ArtistSearch.test.tsx`

**Interfaces:**
- Consumes: `onSelect: (artist: Artist | null) => void` from Task 2 — unchanged here.
- Produces: no new exports. A status line renders **below** the input, inside the existing
  `relative` wrapper, so it does not disturb the dropdown's absolute positioning.

**The defect (`TR-16`).** `searchArtists`' rejection is swallowed by
`.catch(() => { /* aborted or transient — leave prior results */ })`, and an empty result
sets `results` to `[]`. Both render as nothing at all, so "this artist is not in the graph"
and "the search request failed" are indistinguishable — which matters more after the deploy,
where a cold instance really can fail a search.

- [ ] **Step 1: Write the failing tests**

Add to `frontend/src/components/ArtistSearch.test.tsx`:

```tsx
test('says so when the catalogue has no match', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" onSelect={vi.fn()} />);

  await user.type(screen.getByLabelText('From'), 'zzzz');

  expect(await screen.findByText(/no artists found/i)).toBeInTheDocument();
});

test('distinguishes a failed search from an empty one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockRejectedValue(new Error('network'));
  render(<ArtistSearch label="From" onSelect={vi.fn()} />);

  await user.type(screen.getByLabelText('From'), 'miles');

  expect(await screen.findByText(/search is unavailable/i)).toBeInTheDocument();
  expect(screen.queryByText(/no artists found/i)).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `npm test -- ArtistSearch`
Expected: both FAIL with Testing Library's "Unable to find an element with the text" —
because today both cases render nothing, which is the defect stated exactly.

- [ ] **Step 3: Track and render the status**

In `frontend/src/components/ArtistSearch.tsx`, add a status state beside `results`
(after line 14):

```tsx
  // A search that found nothing and a search that failed used to render
  // identically as nothing. After the deploy the second is a real event.
  const [status, setStatus] = useState<'idle' | 'empty' | 'failed'>('idle');
```

Replace the effect body (lines 21–43) with:

```tsx
  useEffect(() => {
    const q = query.trim();
    if (!q || q === selectedName.current) {
      setResults([]);
      setOpen(false);
      setStatus('idle');
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchArtists(q, controller.signal)
        .then((r) => {
          setResults(r);
          setOpen(true);
          setStatus(r.length === 0 ? 'empty' : 'idle');
        })
        .catch((err) => {
          // An abort is this component superseding its own request, not a
          // failure the user should be told about.
          if (controller.signal.aborted || (err as Error)?.name === 'AbortError') return;
          setResults([]);
          setOpen(false);
          setStatus('failed');
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);
```

Then add the status line immediately after the closing `)}` of the dropdown `<ul>` block
(after line 81, still inside the wrapping `<div className="relative">`):

```tsx
      {status !== 'idle' && (
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          {status === 'empty' ? 'No artists found.' : 'Search is unavailable — try again.'}
        </p>
      )}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `npm test -- ArtistSearch`
Expected: PASS, including the three pre-existing tests in that file and Task 2's.

- [ ] **Step 5: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend **70 passed**.

- [ ] **Step 6: Commit**

```bash
git commit -- frontend/src -m "Tell the user when a search failed rather than found nothing

TR-16. The rejection was swallowed and an empty result rendered as nothing, so
the two were indistinguishable on screen. An abort is still silent: that is the
component superseding its own request, not something the user did.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 4: iOS stops rewriting artist names

**Files:**
- Modify: `frontend/src/components/ArtistSearch.tsx` (the `<input>` element)
- Test: `frontend/src/components/ArtistSearch.test.tsx`

**Interfaces:**
- Consumes: the `<input>` as left by Tasks 2 and 3.
- Produces: nothing. This is the last task that touches `ArtistSearch.tsx`.

**Why it matters (`TR-16`).** Artist names are proper nouns that autocorrect does not know —
"Sigur Rós", "MF DOOM", "!!!", "Godspeed You! Black Emperor". On iOS Safari the software
keyboard rewrites them mid-typing and auto-capitalises the first letter, so the query sent
is not the query typed, and the user sees an empty result for an artist that is present.

- [ ] **Step 1: Write the failing test**

Add to `frontend/src/components/ArtistSearch.test.tsx`:

```tsx
test('opts out of the iOS keyboard rewriting artist names', () => {
  render(<ArtistSearch label="From" onSelect={vi.fn()} />);
  const input = screen.getByLabelText('From');

  // Artist names are proper nouns autocorrect does not know, and iOS rewrites
  // them mid-typing, so the query sent is not the query typed.
  expect(input).toHaveAttribute('autocorrect', 'off');
  expect(input).toHaveAttribute('autocapitalize', 'off');
  expect(input).toHaveAttribute('spellcheck', 'false');
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `npm test -- ArtistSearch`
Expected: FAIL — "expected element to have attribute autocorrect="off"", the element having
no such attribute.

- [ ] **Step 3: Add the attributes**

In `frontend/src/components/ArtistSearch.tsx`, add these three props to the `<input>`,
directly beneath `autoComplete="off"`:

```tsx
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck={false}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npm test -- ArtistSearch`
Expected: PASS.

- [ ] **Step 5: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend **71 passed**.

- [ ] **Step 6: Commit**

```bash
git commit -- frontend/src -m "Stop iOS autocorrect rewriting artist names in the search box

TR-16. Artist names are proper nouns the keyboard does not know, so on iOS
Safari the query sent was not the query typed and a present artist came back
empty.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

> ## ⇥ HANDOFF SEAM — after Task 4
>
> The search box and the phone layout are finished and committed. Tasks 5–8 share no file
> with them. **If the session running this plan is long by here, retire it**: write the
> handoff, push the branch, and let a fresh session read Tasks 5–8 cold. Chosen at authoring
> time, per CLAUDE.md — a boundary discovered at Task 7 is expensive and gets deferred past
> the point it should have happened.

---

## Task 5: Requests time out, and a timed-out path says so

**Files:**
- Modify: `frontend/src/api/client.ts:19-59`
- Modify: `frontend/src/hooks/usePath.ts:11,14-20,22-46`
- Modify: `frontend/src/components/PathStatus.tsx`
- Modify: `frontend/src/routes/PathPage.tsx:65-66`
- Test: `frontend/src/api/client.test.ts`, `frontend/src/hooks/usePath.test.tsx`

**Interfaces:**
- Consumes: nothing from Tasks 1–4.
- Produces:
  - `export class TimeoutError extends Error` in `client.ts`, `name = 'TimeoutError'`.
  - `PathState['error']` gains `'timeout'`.
  - `PathState` gains `retry: () => void`.
  - `PathStatus` gains `onRetry: () => void`.

**The defect (`TR-16`).** No request carries a timeout, so a request that never answers
leaves "Building your path…" on screen forever. Behind CloudFront and App Runner that is a
real state, not a hypothetical.

**The timeout must not be confused with a caller abort.** `usePath` aborts its controller on
navigation and returns early from `.catch` when it sees `signal.aborted` — so a timeout that
worked by aborting the *caller's* signal would be silently swallowed and the screen would
never change. The wrapper below therefore uses its own internal controller and throws a
distinct `TimeoutError`.

**The values are chosen, not measured:** 8 s search, 20 s path, 10 s track. Path gets the
longest because Dijkstra at depth plus a cold instance is the slow case. Revisit them once
the telemetry `duration_ms` field has real data — that is a Gate 3 note, not a Track D one.

- [ ] **Step 1: Write the failing tests**

Add to `frontend/src/api/client.test.ts`:

```ts
test('buildPath times out rather than hanging forever', async () => {
  vi.useFakeTimers();
  // A server that accepts the request and never answers — the App Runner cold
  // start case. Honours abort so the wrapper can actually cut it off.
  vi.stubGlobal('fetch', (_url: string, init: RequestInit) =>
    new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () =>
        reject(new DOMException('Aborted', 'AbortError')),
      );
    }),
  );

  const pending = buildPath(['a', 'b'], []);
  const assertion = expect(pending).rejects.toMatchObject({ name: 'TimeoutError' });
  await vi.advanceTimersByTimeAsync(20_000);
  await assertion;
  vi.useRealTimers();
});

test("a caller's own abort is not reported as a timeout", async () => {
  vi.stubGlobal('fetch', (_url: string, init: RequestInit) =>
    new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () =>
        reject(new DOMException('Aborted', 'AbortError')),
      );
    }),
  );

  const controller = new AbortController();
  const pending = buildPath(['a', 'b'], [], controller.signal);
  controller.abort();

  // usePath returns early on its own abort; a TimeoutError here would be
  // swallowed by that check and the screen would never change.
  await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
});
```

Add to `frontend/src/hooks/usePath.test.tsx` — match the file's existing render helper rather
than inventing one; if it wraps in `MemoryRouter` with a `/path/:from/:to` route, do the same:

```tsx
test('classifies a timeout distinctly from an unknown failure', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.TimeoutError(20_000));
  const { result } = renderPath('/path/a/b');
  await waitFor(() => expect(result.current.status).toBe('error'));
  expect(result.current.error).toBe('timeout');
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `npm test -- client usePath`
Expected: FAIL. The two `client` tests fail at compile/import time on `TimeoutError` not
being exported — that counts, and note it: the first test cannot fail for the *right* reason
until the class exists, so re-run it after Step 3's class is added but before the wrapper is
wired in, and confirm it then fails on the promise never rejecting. The `usePath` test fails
with `error` being `'unknown'`.

- [ ] **Step 3: Add the timeout wrapper**

In `frontend/src/api/client.ts`, insert after the `ApiError` class (line 26):

```ts
/**
 * A request we cut off ourselves, distinct from an abort the caller asked for.
 *
 * The distinction is load-bearing: `usePath` aborts on navigation and returns
 * early when it sees its own signal aborted, so a timeout implemented by
 * aborting the caller's signal would be swallowed and the page would sit on
 * "Building your path…" forever — the exact defect this fixes.
 */
export class TimeoutError extends Error {
  readonly ms: number;
  constructor(ms: number) {
    super(`Request timed out after ${ms}ms`);
    this.name = 'TimeoutError';
    this.ms = ms;
  }
}

/** Chosen, not measured. Path is longest: Dijkstra at depth plus a cold instance. */
const TIMEOUT_MS = { search: 8_000, path: 20_000, track: 10_000 } as const;

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  ms: number,
  caller?: AbortSignal,
): Promise<Response> {
  const internal = new AbortController();
  const relay = () => internal.abort();
  if (caller?.aborted) internal.abort();
  else caller?.addEventListener('abort', relay);

  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    internal.abort();
  }, ms);

  try {
    return await fetch(url, { ...init, signal: internal.signal });
  } catch (err) {
    if (timedOut) throw new TimeoutError(ms);
    throw err;
  } finally {
    clearTimeout(timer);
    caller?.removeEventListener('abort', relay);
  }
}
```

Then route all three calls through it. Replace the three `fetch(` calls:

```ts
export async function searchArtists(q: string, signal?: AbortSignal): Promise<Artist[]> {
  const r = await fetchWithTimeout(
    `${BASE}/artists/search?q=${encodeURIComponent(q)}`, {}, TIMEOUT_MS.search, signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  return (await r.json()) as Artist[];
}

export async function buildPath(
  sources: string[],
  exclude: Exclusion[],
  signal?: AbortSignal,
): Promise<PathResult> {
  const r = await fetchWithTimeout(
    `${BASE}/path`,
    {
      method: 'POST',
      headers: withJourney({ 'content-type': 'application/json' }),
      body: JSON.stringify({ sources, exclude }),
    },
    TIMEOUT_MS.path,
    signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  const data = (await r.json()) as { artists: Artist[]; stop_rule: StopRule };
  return { artists: data.artists, stopRule: data.stop_rule };
}

export async function getTrack(mbid: string, signal?: AbortSignal): Promise<Track | null> {
  const r = await fetchWithTimeout(
    `${BASE}/artists/${encodeURIComponent(mbid)}/track`,
    { headers: withJourney() },
    TIMEOUT_MS.track,
    signal,
  );
  if (r.status === 204) return null;
  if (!r.ok) throw new ApiError(r.status);
  const d = (await r.json()) as { preview_url: string; title: string; cover_url: string };
  return { previewUrl: d.preview_url, title: d.title, coverUrl: d.coverUrl ?? d.cover_url };
}
```

> **Careful:** the last line above is a typo trap — `getTrack` must keep mapping
> `cover_url`, not read `coverUrl`. Write it as
> `return { previewUrl: d.preview_url, title: d.title, coverUrl: d.cover_url };`
> exactly as it is today. The existing test `getTrack maps snake_case to camelCase` catches
> this; do not "fix" that test.

- [ ] **Step 4: Classify it and offer a retry**

In `frontend/src/hooks/usePath.ts`, change the error union on line 11 and `classify`:

```ts
  error?: 'notfound' | 'nopath' | 'timeout' | 'unknown';
```

```ts
function classify(err: unknown): PathState['error'] {
  if (err instanceof TimeoutError) return 'timeout';
  if (err instanceof ApiError) {
    if (err.status === 404) return 'notfound';
    if (err.status === 409) return 'nopath';
  }
  return 'unknown';
}
```

Update the import on line 3 to `import { ApiError, TimeoutError, buildPath } from '@/api/client';`,
add `retry: () => void;` to the `PathState` interface, and give the hook an attempt counter
so a retry actually refetches:

```ts
export function usePath(): PathState {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<PathState, 'retry'>>({
    status: 'loading', artists: [], stopRule: 'natural',
  });

  // The URL is unchanged on a retry, so the attempt counter is what makes the
  // effect run again. Without it "Try again" would do nothing at all.
  const key = `${from}|${to}|${params.toString()}|${attempt}`;
```

and return `{ ...state, retry: () => setAttempt((n) => n + 1) }`.

In `frontend/src/components/PathStatus.tsx`, add `onRetry: () => void;` to `Props` and add a
timeout branch before the final `return`:

```tsx
  if (error === 'timeout') {
    return (
      <div className="rounded-lg border border-[var(--color-border)] p-4">
        <p className="mb-3">That took too long. The server may still be waking up.</p>
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg bg-[var(--color-accent)] px-3 py-1.5 text-sm"
        >
          Try again
        </button>
      </div>
    );
  }
```

In `frontend/src/routes/PathPage.tsx` line 66, pass it through:

```tsx
        <PathStatus
          error={state.error}
          onClearExclusions={() => go(clearExclusions(params))}
          onRetry={state.retry}
        />
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `npm test -- client usePath PathPage`
Expected: PASS, including all six pre-existing `client` tests.

- [ ] **Step 6: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend **74 passed**.

- [ ] **Step 7: Commit**

```bash
git commit -- frontend/src -m "Time requests out and offer a retry instead of hanging

TR-16: no request carried a timeout, so one that never answered left
\"Building your path…\" on screen indefinitely — a real state behind App
Runner, not a hypothetical.

The wrapper uses its own controller and throws TimeoutError rather than
aborting the caller's signal: usePath returns early when it sees its own
abort, so the other design would be silently swallowed and the page would
never change. The retry works off an attempt counter because the URL is
unchanged and the effect key would not otherwise move.

Timeouts are chosen, not measured. Revisit once duration_ms has real data.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 6: A refused `play()` stops the card claiming to play

**Files:**
- Modify: `frontend/src/player/Player.ts:29-35`
- Test: `frontend/src/player/Player.test.ts`, `frontend/src/player/usePlayer.test.tsx`

**Interfaces:**
- Consumes: nothing from Tasks 1–5.
- Produces: no signature change. `Player.play()` stays `(url: string) => void`. The rejection
  is routed into the **existing** `onError` channel.

**Why it reuses `onError` rather than adding a channel.** `usePlayer.onError` already owns
the right response — one silent retry with a freshly signed URL, then clear — and the team
review confirmed all four player invariants hold with unit coverage. A second failure
channel would need its own retry policy and would put those invariants back in play. From
the journey's point of view a refused `play()` and a dead source are the same event: no
audio is coming, so the card must stop saying "▮▮▮ now playing".

**Note for the implementer:** jsdom does not implement `HTMLMediaElement.play()` — the suite
prints "Not implemented" lines today and they are expected, not a new failure. The
established pattern for controlling it is `Player.test.ts:85`,
`vi.spyOn(audioOf(player), 'play')`.

- [ ] **Step 1: Write the failing tests**

Add to `frontend/src/player/Player.test.ts`:

```ts
test('a rejected play() reaches the error handler', async () => {
  // Autoplay policy, a decode failure, or a source the element refuses: the
  // promise rejects and nothing on the page hears about it, so the card sits
  // there claiming to play over silence.
  const player = new HtmlAudioPlayer();
  const onError = vi.fn();
  player.onError(onError);
  vi.spyOn(audioOf(player), 'play').mockRejectedValue(
    new DOMException('play() failed', 'NotAllowedError'),
  );

  player.play('https://example.test/clip.mp3');
  await vi.waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
});

test('a rejected play() on a disposed player reaches nobody', async () => {
  const player = new HtmlAudioPlayer();
  const onError = vi.fn();
  player.onError(onError);
  const el = audioOf(player);
  vi.spyOn(el, 'play').mockRejectedValue(new DOMException('x', 'AbortError'));

  player.play('https://example.test/clip.mp3');
  player.dispose();
  await new Promise((r) => setTimeout(r, 0));

  expect(onError).not.toHaveBeenCalled();
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `npm test -- Player`
Expected: the first FAILS on `vi.waitFor` timing out with `onError` never called — the
defect. The second may pass already; note that, and keep it as a guard against Step 3
regressing the disposed-player invariant rather than claiming it as evidence of a fix.

- [ ] **Step 3: Route the rejection**

In `frontend/src/player/Player.ts`, replace `play()` (lines 29–35):

```ts
  play(url: string): void {
    if (this.disposed) return;
    // Only assigning a *different* src is what lets toggle() resume rather than
    // re-seek to zero, which is why the card's pause button used to restart.
    if (this.audio.src !== url) this.audio.src = url;
    // A rejected play() — autoplay policy, a decode failure — is the same event
    // as a dead source from the journey's side: no audio is coming. Route it to
    // the error channel, which already owns the one silent retry, rather than
    // adding a second channel that would need its own policy and put the four
    // player invariants back in play. jsdom returns undefined here, not a
    // promise, which Promise.resolve normalises.
    void Promise.resolve(this.audio.play()).catch(() => {
      if (!this.disposed) this.errorCb?.();
    });
  }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `npm test -- Player usePlayer`
Expected: PASS, including all five pre-existing `Player` tests and every `usePlayer` test.
The `a disposed player refuses to start playing again` test is the one most at risk from
this change — it must still pass.

- [ ] **Step 5: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend **76 passed**.

- [ ] **Step 6: Commit**

```bash
git commit -- frontend/src -m "Stop a card claiming to play when play() was refused

TR-16: the rejected promise was discarded, leaving a card asserting
\"now playing\" over silence.

Routed into the existing error channel rather than a new one. usePlayer's
onError already owns the right response — one silent retry with a freshly
signed URL, then clear — and the team review confirmed all four player
invariants hold with unit coverage there; a second channel would put them
back in play.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 7: A catch-all route

**Files:**
- Create: `frontend/src/routes/NotFound.tsx`
- Modify: `frontend/src/App.tsx:7-11`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: nothing.
- Produces: `export function NotFound()` — no props.

**Why (`TR-16`).** `App.tsx` declares `/` and `/path/:from/:to` and nothing else, so any
other URL renders an empty page with no way out. After the deploy that includes every
mistyped or truncated shared link — and shared links are how this app is meant to travel.

- [ ] **Step 1: Write the failing test**

Add to `frontend/src/App.test.tsx` — follow that file's existing router-wrapping helper:

```tsx
test('an unknown URL offers a way back rather than a blank page', () => {
  render(
    <MemoryRouter initialEntries={['/path/only-one-id']}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /start a journey/i })).toHaveAttribute('href', '/');
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `npm test -- App`
Expected: FAIL with "Unable to find an element with the text: /nothing here/i" — the page
renders empty, which is the defect.

- [ ] **Step 3: Create the page**

Create `frontend/src/routes/NotFound.tsx`:

```tsx
import { Link } from 'react-router-dom';

/**
 * Any URL that is not the landing page or a path. After the deploy that
 * includes every mistyped or truncated shared link, and shared links are how
 * this app travels — a blank page is the worst possible landing for one.
 */
export function NotFound() {
  return (
    <main className="max-w-xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-semibold mb-3">Nothing here</h1>
      <p className="text-[var(--color-muted)] mb-6">
        That link doesn&rsquo;t point at a journey. It may have been cut short on its way to you.
      </p>
      <Link to="/" className="text-[var(--color-accent)]">
        Start a journey
      </Link>
    </main>
  );
}
```

- [ ] **Step 4: Register it**

In `frontend/src/App.tsx`, add the import and the route:

```tsx
import { Route, Routes } from 'react-router-dom';
import { LandingPage } from '@/routes/LandingPage';
import { NotFound } from '@/routes/NotFound';
import { PathPage } from '@/routes/PathPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/path/:from/:to" element={<PathPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `npm test -- App`
Expected: PASS.

- [ ] **Step 6: Run every suite**

Run: `npm test && npm run lint && npm run build`
Expected: frontend ~~**78 passed**~~ — **CORRECTED ON EXECUTION to 77.** This task's budget
said two tests and its Step 1 specified one; the arithmetic, not the run, was wrong. See
`TKD-7`.

- [ ] **Step 7: Commit**

```bash
git commit -- frontend/src -m "Give unknown URLs a page with a way out

TR-16: only / and /path/:from/:to were declared, so every other URL rendered
blank. After the deploy that includes mistyped and truncated shared links,
which is how this app is meant to travel.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
```

---

## Task 8: Full verification and the record

**Files:**
- Modify: `docs/superpowers/2026-07-26-gate2-track-d-execution-log.md`
- Modify: `docs/superpowers/TEST-QUEUE.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: every task above.
- Produces: nothing executable.

**This task adds no test.** Its job is to prove the seven items land together and to leave
the record a cold session reads. **Expected frontend total: ~~78~~ 77 (corrected on execution,
`TKD-7`). Expected e2e total: 4.**

- [ ] **Step 1: Run everything, from a clean tree**

```bash
cd frontend && npm test && npm run lint && npm run build && npm run test:e2e
cd ../api && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../builder && UV_LINK_MODE=copy uv run --extra dev pytest -q
```

Expected: frontend ~~**78**~~ **77** (`TKD-7`), e2e **4**, api **180**, builder **115**. Any api or builder
movement means this plan touched something it must not have — stop and find out what.

- [ ] **Step 2: Check the desktop view by eye at both widths**

With the dev servers running, open `http://localhost:5173`, build a journey, and look at it
at 390 px and at full width. This is not a substitute for the e2e assertions; it is the
check that the phone layout is *usable*, which no assertion covers. Note anything odd for
the queue entry rather than fixing it silently.

- [ ] **Step 3: Snyk**

Run `snyk_code_scan` on `frontend/`. Fix anything found using the results, and rescan until
clean. Record the outcome either way.

- [ ] **Step 4: Write the execution log**

`docs/superpowers/2026-07-26-gate2-track-d-execution-log.md`, identifiers `TKD-`. It must
carry, at minimum:

- The **RED run messages** for every task — what the failing test actually said. This is the
  half that cannot be reconstructed afterwards (`TKA-1`).
- The **before and after geometry** from Task 1's e2e run: the horizontal overflow and the
  artist name's width at 390 px. Those are the only figures this track owns.
- `TKD-` entries for: the `TR-16` evidence correction and the dead `App.css` (Task 1); the
  stale-selection defect's true provenance — pre-existing, not introduced by "New path", and
  not a race (Task 2); the decision to route a refused `play()` through the existing error
  channel and what that protects (Task 6); and the timeout values being chosen rather than
  measured, with the condition for revisiting them (Task 5).
- Anything decided **against**, which leaves no other artifact.

- [ ] **Step 5: Queue the use-the-app test**

Append a `QUEUED` entry to `docs/superpowers/TEST-QUEUE.md`, newest first. It is owner-facing
prose: **no bare identifiers** — no `TR-16`, no `TKD-3` — per `closeout` C1. It must say that
**nothing about which artists you get has changed**, that the phone layout is the thing to
look at, and that the search box now goes dead when you type over a chosen artist, which is
the fix to the defect he reported. Ask him to open it on his phone; that is the one check
nothing here can do.

- [ ] **Step 6: Add the two rows to the documentation map**

In `docs/README.md`, add rows for this plan (Complete — "**EXECUTED 2026-07-26; do not
execute again**") and for the execution log, stating the role of each in its first ten lines
per that file's own rule.

- [ ] **Step 7: Commit and open the PR**

```bash
git commit -- docs -m "Record Track D: seven frontend items, the phone layout among them

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RboJGSeWS8sGqqBcVwB2ey"
git push -u origin gate2-track-d-frontend
```

Open the PR against `main` with the body carrying: a link to the execution log, the gate
outcomes **including any failure**, the suite counts before and after, the deferred items
with their success conditions, and what is closed and should not be re-litigated. No
artifact checksum applies — this track rebuilds nothing.

---

## Self-review

**Spec coverage.** All six fenced `TR-16` items map to a task (1, 3, 4, 5, 6, 7), and the
seventh owner-reported item maps to Task 2 — the table in "Scope" is that mapping. `DEP-30`
is excluded because Track A already did it, verified in `playwright.config.ts`. The three
Gate 3 deferrals are excluded by name.

**Claims checked against the repo, not assumed.** Every file, line range, symbol and command
in this plan was read from source at `7fe9b22` before it was written: `ArtistSearch.tsx`,
`LandingPage.tsx`, `ArtistCard.tsx`, `PlayerBar.tsx`, `JourneyList.tsx`, `PathPage.tsx`,
`PathStatus.tsx`, `Player.ts`, `usePlayer.ts`, `useClip.ts`, `usePath.ts`, `client.ts`,
`App.tsx`, `main.tsx`, `index.html`, `index.css`, `vite.config.ts`, `playwright.config.ts`,
`package.json`, the four test files whose patterns are reused, and `e2e/path.spec.ts`. The
65-test baseline was **measured**, not quoted. Two `TR-16` claims did not survive that check
and are corrected in "Scope".

**Known soft spots, stated rather than hidden.**
- **The per-task test counts are targets, not measurements.** They assume each new test is
  one `test()` block and nothing else moves. A mismatch is a signal to investigate, not a
  number to make true by adding a test.
- **Task 5's `usePath` test is written against a render helper this plan did not read in
  full.** `usePath.test.tsx` exists and has a working pattern; use it rather than the sketch
  here if they differ.
- **Task 6's second test may pass before the fix.** That is stated in its own step, with the
  instruction to record it as a guard rather than count it as evidence — the `TKA-2` pattern
  of naming a knowingly-passing check instead of letting it look like a RED run.
- **Task 1's e2e depends on the API being up** and on `miles davis` and `daft punk` both
  being present and routable in the adopted artifact. They are — `e2e/path.spec.ts` already
  routes that exact pair against it.
