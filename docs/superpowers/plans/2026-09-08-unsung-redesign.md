# Unsung.fm Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Role: ACTIVE implementation plan for the `UXR-` set. IN PROGRESS: `T1`–`T5` executed 2026-09-08 (branch `unsung-redesign`, PR #114), `T6`–`T11` unstarted.** *(Role line updated at the first-seam closeout; the tasks below are as written, with two in-place corrections marked `⚠ CORRECTED`.)*
Tasks are `UXR-T1`–`UXR-T11`. Retained execution log: `docs/superpowers/2026-09-08-unsung-redesign-execution-log.md`, created by `UXR-T1` and appended **per task**.

**Goal:** Rename the app to Unsung.fm and rebuild the landing and journey pages to the owner's approved mockup, with the artist detail docked beside the rail (a bottom sheet on phones), a share button, a player progress line and a live artist count — and nothing the spec drops or defers.

**Architecture:** Frontend-only except one new read route (`GET /api/meta`). The palette and type move to role-named tokens in one commit with aliases, then each surface is migrated task by task. The card sheds the `LUX-4` facts and links into a new `ArtistDetail` component rendered by one of two containers chosen by breakpoint. All path state stays in the URL; detail selection is component state.

**Tech Stack:** React 19, Vite, TypeScript, Tailwind 4 (`@theme` tokens), Vitest + Testing Library, Playwright; FastAPI + Pydantic for the one route.

**Spec:** `docs/superpowers/specs/2026-09-08-unsung-redesign-scope.md` — read §2 (the owner's decisions) and §3 (`UXR-D1`–`UXR-D18`) before any task. Visual source: `frontend/design/2026-09-08-unsung-redesign/Unsung.fm.dc.html`.

## Global Constraints

- **Another session is live** in a worktree on the `LBD-` track. Commit with a pathspec — `git commit -- <paths>` — never `-A`, `-a`, `--amend`, `rebase` or `stash`. Branch: `unsung-redesign`, already pushed.
- **Every `uv` command is prefixed `UV_LINK_MODE=copy`** and run from the package directory (`api/`). Frontend commands run from `frontend/`.
- **Behaviour tests go red before green.** A test that passes against unmodified source is the vacuous-check pattern (`FMS-P1` / `TR-2`); the plan says where a red run is expected and what it fails with.
- **Visual tasks end in a screenshot at 390 px and 1280 px** (spec §6), not only in a green suite. Use the Playwright script in `UXR-T1` step 7.
- **Count currencies are named** (spec `UXR-D6`, `UXR-D10`): "steps" = artists between the two chosen; "Stop N of M" = 1-based position among all artists including endpoints. Never mix them.
- **Copy is the mockup's verbatim** where a task quotes it; do not paraphrase. The one assumption is `UXR-D12` (landing copy) — if the owner overrules it, `UXR-T3` step 4 keeps the 2026-08-07 lines.
- **The streaming links stay neutral** (`UXR-D4`): no brand colours, no logos, text labels.
- **Both faces are self-hosted** (`UXR-D11`): `@fontsource-variable/dm-sans` (present) and `@fontsource-variable/space-grotesk` (installed in `UXR-T1`). No Google Fonts request.
- **Snyk:** run `snyk_code_scan` on the `api/` diff after `UXR-T4` and on the `frontend/` diff after `UXR-T10`; fix and rescan until clean. Pre-existing findings in `api/tests/test_origin_secret.py` and `frontend/design/*/support.js` are known and left alone.
- **The owner's one hands-on item:** export `assets/unsung-mark.png` from the Design project (1152×1152) and save it as `frontend/public/unsung-mark.png` (resized to 512×512 is fine). `UXR-T2` references the path; every test passes without the file; the app shows a broken image until it exists.
- **Handoff seams:** after `UXR-T5` and after `UXR-T8`. Retire the session there if it has been long; the next one reads the execution log cold.

---

## File structure

| File | Responsibility | Task |
|---|---|---|
| `frontend/src/index.css` | tokens, faces, keyframes — the only place colours live | T1, T9 |
| `frontend/src/components/Brand.tsx` (new) | the mark + wordmark, two sizes | T2 |
| `frontend/index.html`, `frontend/public/favicon.*` | title, no-JS fallback, favicon | T2 |
| `frontend/src/routes/LandingPage.tsx` | layout, hero copy, chips with steps, How it works, teaser | T3 |
| `frontend/src/components/ArtistCountBadge.tsx` (new) | the live count, or nothing | T4 |
| `api/src/artistpath_api/models.py`, `app.py`, `api/tests/test_app.py` | `MetaOut`, `GET /api/meta` | T4 |
| `frontend/src/api/client.ts` | `getMeta` | T4 |
| `frontend/src/player/Player.ts`, `usePlayer.ts`, `components/PlayerBar.tsx` | `timeupdate` → position/duration → progress line, "Stop N of M" | T5 |
| `frontend/src/components/ArtistCard.tsx` | the listening surface only; gains the detail button | T6 |
| `frontend/src/components/ArtistDetail.tsx` (new) | facts, links, play/try-another, Dig deeper | T7 |
| `frontend/src/components/DetailDock.tsx`, `DetailSheet.tsx` (new) | the two containers | T7 |
| `frontend/src/components/JourneyList.tsx` | owns selection; the grid | T7 |
| `frontend/src/components/JourneyHeading.tsx` (new), `ShareButton.tsx` (new), `PathIntro.tsx`, `routes/PathPage.tsx` | header row, title, steps tile, share, explainer copy | T8 |
| `PathSkeleton.tsx`, `RerollNotice.tsx`, `PathStatus.tsx`, `RouteHistory.tsx`, `ArtistSearch.tsx`, `routes/NotFound.tsx` | restyle only; alias tokens removed | T9 |
| `frontend/e2e/*.spec.ts`, `frontend/e2e/landing-samples.spec.ts` (new) | the real-browser suite | T10 |
| `docs/README.md`, `docs/superpowers/NEXT.md`, `infra/README.md` §6 | the record | T11 |

---

### UXR-T1: Tokens, faces, and the execution log

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/package.json` (via `npm install`)
- Create: `docs/superpowers/2026-09-08-unsung-redesign-execution-log.md`
- Create: `frontend/e2e/screenshot.mjs` (a helper, not a spec)

**Interfaces:**
- Produces: CSS tokens by role — `--color-bg`, `--color-bg-raised`, `--color-surface`, `--color-surface-raised`, `--color-field`, `--color-border`, `--color-border-strong`, `--color-border-hover`, `--color-text`, `--color-muted`, `--color-label`, `--color-chip`, `--color-start`, `--color-playing`, `--color-end`, `--color-detail`, `--color-detail-fg`, `--color-detail-border`, `--color-detail-hairline`, `--color-inert`, `--color-inert-fg`, `--color-bar`, `--color-bar-border`, `--color-away`; and `--font-sans`, `--font-display`. Every later task uses only these names.

- [ ] **Step 1: Install the display face**

Run from `frontend/`: `npm install @fontsource-variable/space-grotesk@5.3.0`
Expected: `package.json` gains the dependency; `package-lock.json` changes.

- [ ] **Step 2: Replace the `@theme` block**

In `frontend/src/index.css`, replace everything from `@import "@fontsource-variable/dm-sans";` through the closing `}` of `@theme` with:

```css
@import "@fontsource-variable/dm-sans";
@import "@fontsource-variable/space-grotesk";

@theme {
  --font-sans: 'DM Sans Variable', system-ui, sans-serif;
  /* Display face: the h1, the wordmark, artist names, numbers in tiles. UXR-D11. */
  --font-display: 'Space Grotesk Variable', 'DM Sans Variable', system-ui, sans-serif;

  /* The Unsung.fm palette (frontend/design/2026-09-08-unsung-redesign), named by
     ROLE, never by shade. UXR-D17: changed in one commit; the aliases at the foot
     of this block keep every pre-redesign token name resolving until UXR-T9
     removes the unused ones — a token that resolves to nothing is transparent,
     and no test sees transparent. */
  --color-bg: #08080b;              /* the page */
  --color-bg-raised: #0a0a0f;       /* a framed region on the page (the phone/desktop frames) */
  --color-surface: #0e0e14;         /* an interior card, a chip, the skeleton rows */
  --color-surface-raised: #111119;  /* an endpoint card; a hover-able chip */
  --color-field: #14141c;           /* the two search inputs */
  --color-border: #1e1e29;
  --color-border-strong: #262633;   /* buttons, pills, the field's resting border */
  --color-border-hover: #2a2a38;
  --color-text: #f2f0f7;
  --color-muted: #9b98ab;           /* body copy on dark */
  --color-label: #6d6a7d;           /* uppercase eyebrows, captions, placeholders */
  --color-chip: #c8c4d8;            /* text inside a bordered pill */

  /* The three lights of the rail. The mockup runs cyan → violet → pink top to
     bottom; each also has a job: start / now playing / destination. */
  --color-start: #2ec5ee;
  --color-playing: #8f6cf5;
  --color-end: #f5479b;

  /* The selected card and the docked detail. A fourth hue, so "showing detail"
     never reads as "playing". */
  --color-detail: #4f7fe0;
  --color-detail-fg: #7fa4ec;
  --color-detail-border: #2a3450;
  --color-detail-hairline: #1c2233;

  --color-inert: #191922;           /* a play button with nothing to play */
  --color-inert-fg: #3c414a;
  --color-bar: #0c0c12;             /* the player bar */
  --color-bar-border: #1c1c26;
  --color-away: #e8a0a0;            /* the one error tint; unchanged */

  /* ---- ALIASES, pre-redesign names. Removed in UXR-T9 once nothing uses them. ---- */
  --color-accent: #2ec5ee;
  --color-dig: #f5479b;
  --color-note: #6d6a7d;
  --color-placeholder: #6d6a7d;
  --color-endpoint: #2a2a38;
  --color-rail-mid: #8f6cf5;
  --color-strip: #0e0e14;
  --color-strip-border: #1e1e29;
  --color-field-hover: #14141c;
  --color-field-border: #262633;
}
```

Leave `:root`, `body`, `input`, and every `@keyframes` block as they are, but add these two keyframes after `ap-grow`:

```css
/* The mockup's equaliser on the playing card and the CTA's slow sheen. */
@keyframes un-eq {
  0%, 100% { transform: scaleY(.35); }
  50%      { transform: scaleY(1); }
}
@keyframes un-sheen {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
```

and inside the existing `@media (prefers-reduced-motion: reduce)` block add:

```css
  .motion-safe-only { animation: none !important; }
```

- [ ] **Step 3: Check nothing referenced a token the aliases do not cover**

Run from `frontend/`: `grep -rhoE 'var\(--color-[a-z-]+\)' src | sort -u`
Expected: every name printed is defined in the block above. If one is not, add it to the alias section with the closest new value — do not leave it undefined.

- [ ] **Step 4: Build, lint, test**

Run from `frontend/`: `npm run build && npm run lint && npm test`
Expected: all green. Nothing has changed behaviour yet; the palette is different.

- [ ] **Step 5: Write the screenshot helper**

Create `frontend/e2e/screenshot.mjs`:

```js
// Two screenshots per page at the two widths the spec names (UXR spec §6).
// Not a test: run by hand after any visual task. Requires the dev server on
// :5173 and the API on :8000, exactly as `npm run test:e2e` does.
//   node e2e/screenshot.mjs /                      -> landing
//   node e2e/screenshot.mjs /path/<from>/<to>      -> journey
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const route = process.argv[2] ?? '/';
const name = route === '/' ? 'landing' : 'journey';
mkdirSync('e2e/screenshots', { recursive: true });
const browser = await chromium.launch();
for (const width of [390, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: width === 390 ? 844 : 900 } });
  await page.goto(`http://localhost:5173${route}`);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `e2e/screenshots/${name}-${width}.png`, fullPage: true });
  await page.close();
}
await browser.close();
```

Add `e2e/screenshots/` to `frontend/.gitignore`.

- [ ] **Step 6: Create the execution log**

Create `docs/superpowers/2026-09-08-unsung-redesign-execution-log.md` with this header, then a `## §1 UXR-T1` section recording what step 3 printed and the commit hash:

```markdown
# `UXR-` execution log — the Unsung.fm redesign

**Role: RETAINED EXECUTION LOG for `UXR-T1`–`UXR-T11`. ACTIVE. Owns no figures and no status**
(`NEXT.md` owns status). Appended per task: decisions and reasoning, never narration.
Plan: `plans/2026-09-08-unsung-redesign.md`. Spec: `specs/2026-09-08-unsung-redesign-scope.md`.
```

- [ ] **Step 7: Screenshots, then commit**

Run from `frontend/` with both servers up: `node e2e/screenshot.mjs /` and `node e2e/screenshot.mjs /path/561d854a-6a28-4aa7-8c99-323e6ce46c2a/056e4f3e-d505-4dad-8ec1-d04f521cbb56`. Look at all four. Expected: the old layout in the new palette; nothing unreadable.

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/index.css frontend/e2e/screenshot.mjs frontend/.gitignore docs/superpowers/2026-09-08-unsung-redesign-execution-log.md
git commit -m "UXR-T1: the Unsung.fm palette and faces as role tokens, with aliases" -- frontend/package.json frontend/package-lock.json frontend/src/index.css frontend/e2e/screenshot.mjs frontend/.gitignore docs/superpowers/2026-09-08-unsung-redesign-execution-log.md
```

---

### UXR-T2: The name

**Files:**
- Create: `frontend/src/components/Brand.tsx`, `frontend/src/components/Brand.test.tsx`
- Modify: `frontend/index.html`, `frontend/src/App.test.tsx`, `frontend/src/routes/NotFound.tsx`, `frontend/src/routes/LandingPage.tsx:60-64` (the h1 only), `frontend/e2e/fallback.spec.ts`
- Delete: `frontend/public/favicon.svg`

**Interfaces:**
- Produces: `Brand({ size }: { size: 'nav' | 'hero' })` — renders `<img src="/unsung-mark.png" alt="">` plus the wordmark; the accessible name of the whole thing is "Unsung.fm".

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/Brand.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { Brand } from './Brand';

test('the brand reads as one name to assistive tech, not as "unsung" and ".fm"', () => {
  render(<Brand size="nav" />);
  // One accessible name. The mark is decorative (alt=""), the split wordmark is
  // aria-hidden, and a single label carries the product name.
  expect(screen.getByLabelText('Unsung.fm')).toBeInTheDocument();
  expect(screen.queryByRole('img', { name: /unsung/i })).not.toBeInTheDocument();
});

test('the hero size is larger than the nav size', () => {
  const { container: nav } = render(<Brand size="nav" />);
  const { container: hero } = render(<Brand size="hero" />);
  expect(nav.querySelector('img')?.getAttribute('width')).toBe('30');
  expect(hero.querySelector('img')?.getAttribute('width')).toBe('38');
});
```

- [ ] **Step 2: Run it to see it fail**

Run from `frontend/`: `npx vitest run src/components/Brand.test.tsx`
Expected: FAIL — cannot resolve `./Brand`.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/Brand.tsx`:

```tsx
interface Props {
  /** 30 px mark in a page header, 38 px on the landing hero. */
  size: 'nav' | 'hero';
}

/**
 * The mark and the wordmark, as one accessible name (UXR-D1).
 *
 * The mark is the owner's PNG at /unsung-mark.png — his to export from the
 * Design project; nothing here depends on it existing. The wordmark is split
 * only visually: "unsung" bright, ".fm" dim, exactly as drawn.
 */
export function Brand({ size }: Props) {
  const px = size === 'hero' ? 38 : 30;
  const text = size === 'hero' ? 'text-[19px]' : 'text-[16px]';
  return (
    <span className="inline-flex items-center gap-2.5" aria-label="Unsung.fm" role="img">
      <img src="/unsung-mark.png" alt="" width={px} height={px} className="block" />
      <span aria-hidden className={`font-display font-semibold tracking-[-.02em] ${text}`}>
        unsung<span className="font-normal text-[var(--color-label)]">.fm</span>
      </span>
    </span>
  );
}
```

- [ ] **Step 4: Run the test to see it pass**

Run: `npx vitest run src/components/Brand.test.tsx` — Expected: PASS.

- [ ] **Step 5: Rename every surface that says "Artist Path"**

`frontend/index.html`: `<title>Unsung.fm</title>`; in the fallback block `<h1>Unsung.fm</h1>`; replace the favicon line with `<link rel="icon" type="image/png" href="/unsung-mark.png" />`. Delete `frontend/public/favicon.svg` (`git rm`).

`frontend/src/routes/LandingPage.tsx`: replace the `<h1 …>Artist Path</h1>` with `<Brand size="hero" />` inside a `<div className="flex">` (the full hero is `UXR-T3`; this task only removes the old name). Add the import.

`frontend/src/App.test.tsx` line 11: `expect(screen.getByLabelText('Unsung.fm')).toBeInTheDocument();`

`frontend/e2e/fallback.spec.ts` line 21: `await expect(page.getByLabel('Unsung.fm')).toBeVisible();`

`frontend/src/routes/NotFound.tsx`: no product name appears; leave the copy, change nothing.

- [ ] **Step 6: Grep for the old name**

Run from `frontend/`: `grep -rn "Artist Path" src index.html e2e`
Expected: no output. (`artistpath:` localStorage keys and package identifiers are not the product name and stay.)

- [ ] **Step 7: Test and commit**

Run: `npm test && npm run build` — Expected: green.

```bash
git add frontend/src/components/Brand.tsx frontend/src/components/Brand.test.tsx frontend/index.html frontend/src/App.test.tsx frontend/src/routes/LandingPage.tsx frontend/e2e/fallback.spec.ts
git rm --quiet frontend/public/favicon.svg
git commit -m "UXR-T2: the app is called Unsung.fm" -- frontend/src/components/Brand.tsx frontend/src/components/Brand.test.tsx frontend/index.html frontend/src/App.test.tsx frontend/src/routes/LandingPage.tsx frontend/e2e/fallback.spec.ts frontend/public/favicon.svg
```

Append `## §2 UXR-T2` to the execution log: note that the mark file is the owner's and whether it existed at commit time.

---

### UXR-T3: The landing page

**Files:**
- Modify: `frontend/src/routes/LandingPage.tsx`, `frontend/src/routes/LandingPage.test.tsx`
- Modify: `frontend/e2e/path.spec.ts:12`, `frontend/e2e/responsive.spec.ts:17,67,101` (the CTA's name)

**Interfaces:**
- Consumes: `Brand`, `ArtistSearch` (unchanged), the tokens.
- Produces: exported `SAMPLE_JOURNEYS` with a `steps: number` field and exported `TEASER` — `UXR-T10`'s e2e reads both. **⚠ CORRECTED 2026-09-08:** they were placed in `frontend/src/lib/sampleJourneys.ts`, not in `LandingPage.tsx` (log §3).

- [ ] **Step 1: Write the failing tests**

In `frontend/src/routes/LandingPage.test.tsx` add, and change the CTA matcher in the three existing tests from `/discover a path/i` to `/build the path/i`:

```tsx
test('each sample journey says how many steps it takes, in the "between" currency', () => {
  setup();
  // UXR-D6/D7: "steps" = artists BETWEEN the two chosen. Measured on the served
  // graph 2026-09-08; e2e/landing-samples.spec.ts pins these against the live
  // router so a rebuild that moves them fails a test instead of lying on a chip.
  expect(screen.getByRole('link', { name: /miles davis.*radiohead/i })).toHaveTextContent('3 steps');
  expect(screen.getByRole('link', { name: /dolly parton.*daft punk/i })).toHaveTextContent('4 steps');
  expect(screen.getByRole('link', { name: /bad bunny.*chappell roan/i })).toHaveTextContent('6 steps');
});

test('the hero carries the approved copy and a three-step "How it works"', () => {
  setup();
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
    'Hear what lives between two artists you love.',
  );
  expect(screen.getByText(/name two artists/i)).toBeInTheDocument();
  expect(screen.getByText(/listen to the path/i)).toBeInTheDocument();
  expect(screen.getAllByText(/dig deeper/i).length).toBeGreaterThan(0);
});

test('the teaser names the measured Miles Davis to Daft Punk journey, without tags', () => {
  setup();
  for (const name of ['Nina Simone', 'Marvin Gaye', 'Daryl Hall & John Oates', 'Genesis', 'David Gilmour']) {
    expect(screen.getByText(name)).toBeInTheDocument();
  }
  expect(screen.queryByText(/low reach/i)).not.toBeInTheDocument();
});
```

Also update the first test's expected accessible names: the chips now read `Miles Davis → Radiohead · 3 steps` etc., so change the `toEqual([...])` list to match `['Miles Davis→Radiohead3 steps', 'Dolly Parton→Daft Punk4 steps', 'Bad Bunny→Chappell Roan6 steps']` — or, better, give each `<Link>` an explicit `aria-label={`${j.fromName} to ${j.toName}, ${j.steps} steps`}` and assert those three strings. Use the aria-label form.

- [ ] **Step 2: Run to see them fail**

Run: `npx vitest run src/routes/LandingPage.test.tsx`
Expected: FAIL — no "3 steps", no h1 with that copy, no teaser names.

- [ ] **Step 3: Rewrite the landing page**

Replace `frontend/src/routes/LandingPage.tsx` wholesale (keep `seedFrom` and the `useState`/`navigate` logic exactly as they are; only the data and the JSX change):

```tsx
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArtistCountBadge } from '@/components/ArtistCountBadge';
import { ArtistSearch } from '@/components/ArtistSearch';
import { Brand } from '@/components/Brand';
import type { Artist } from '@/api/types';

/**
 * Ready-made pairs, so a first visit does not begin with a blank box. Owner-chosen
 * 2026-08-07. `steps` = artists BETWEEN the two (UXR-D6), measured on the served
 * graph 2026-09-08 by the router itself.
 *
 * ⚠ MBIDs and step counts both depend on the SERVED ARTIFACT. A future artifact can
 * drop an artist or move a count. e2e/landing-samples.spec.ts asks the live router
 * for each pair and fails if a chip disagrees — that test IS the re-check rule.
 */
export const SAMPLE_JOURNEYS = [
  { from: '561d854a-6a28-4aa7-8c99-323e6ce46c2a', fromName: 'Miles Davis',
    to: 'a74b1b7f-71a5-4011-9441-d0b5e4122711', toName: 'Radiohead', steps: 3 },
  { from: '1d543e07-d0d2-4834-a8db-d65c50c2a856', fromName: 'Dolly Parton',
    to: '056e4f3e-d505-4dad-8ec1-d04f521cbb56', toName: 'Daft Punk', steps: 4 },
  { from: '89aa5ecb-59ad-46f5-b3eb-2d424e941f19', fromName: 'Bad Bunny',
    to: '56a55378-f155-48de-80a5-d80104221267', toName: 'Chappell Roan', steps: 6 },
] as const;

/** The desktop hero's illustrative journey (UXR-D14). Same drift rule, same test. */
export const TEASER = {
  from: '561d854a-6a28-4aa7-8c99-323e6ce46c2a',
  to: '056e4f3e-d505-4dad-8ec1-d04f521cbb56',
  names: ['Miles Davis', 'Nina Simone', 'Marvin Gaye', 'Daryl Hall & John Oates', 'Genesis', 'David Gilmour', 'Daft Punk'],
} as const;

const HOW = [
  { n: '01', tone: 'var(--color-start)', title: 'Name two artists',
    body: 'One you are in the mood for, one you are curious about.' },
  { n: '02', tone: 'var(--color-playing)', title: 'Listen to the path',
    body: 'Every stop gets a 30-second clip, and every step sounds like a sensible move from the last. No jolts.' },
  { n: '03', tone: 'var(--color-end)', title: 'Dig deeper',
    body: 'Know a stop already? Press Dig deeper and the route rebuilds through artists you are far less likely to know.' },
] as const;

function seedFrom(params: URLSearchParams, idKey: string, nameKey: string): Artist | null {
  const mbid = params.get(idKey);
  const name = params.get(nameKey);
  if (!mbid || !name) return null;
  return { mbid, name, disambiguation: '', popularity: 0, spotifyId: null, appleId: null, facts: null };
}

export function LandingPage() {
  const [params] = useSearchParams();
  const [seedA] = useState(() => seedFrom(params, 'from', 'fromName'));
  const [seedB] = useState(() => seedFrom(params, 'to', 'toName'));
  const [from, setFrom] = useState<Artist | null>(seedA);
  const [to, setTo] = useState<Artist | null>(seedB);
  const navigate = useNavigate();

  const sameArtist = !!from && !!to && from.mbid === to.mbid;
  const ready = !!from && !!to && !sameArtist;

  return (
    <main className="mx-auto w-full max-w-[1280px] px-6 pb-14 pt-6 sm:px-10">
      <header className="flex items-center justify-between py-2">
        <Brand size="hero" />
        {/* UXR-D13: no nav until the pages behind it exist. */}
      </header>

      <div className="mt-10 grid items-center gap-12 lg:mt-16 lg:grid-cols-[1.08fr_.92fr] lg:gap-16">
        <div>
          <ArtistCountBadge />
          {/* UXR-D12: the mockup's copy, verbatim. If the owner overrules that
              decision, the 2026-08-07 lines return here under the new type:
              "Find a smooth path between any two artists" / "Discover what lives in between". */}
          <h1 className="mt-5 font-display text-[31px] font-medium leading-[1.06] tracking-[-.03em] text-balance sm:text-[44px] lg:text-[60px] lg:leading-[1.02] lg:tracking-[-.035em]">
            Hear what lives between two artists you love.
          </h1>
          <p className="mt-4 max-w-[520px] text-[15px] leading-[1.5] text-[var(--color-muted)] text-pretty sm:text-[18px]">
            Name two. Unsung.fm builds a listenable path between them — every step a small,
            sensible move from the last, with a 30-second clip. Then{' '}
            <span className="text-[var(--color-text)]">dig deeper</span> to swap the obvious
            names for the ones you have never heard.
          </p>

          <div className="mt-8 flex max-w-[600px] flex-col gap-3.5">
            <div className="grid gap-3.5 sm:grid-cols-2">
              <ArtistSearch label="Start with" end="start" initial={seedA} onSelect={setFrom} />
              <ArtistSearch label="End with" end="destination" initial={seedB} onSelect={setTo} />
            </div>
            {sameArtist && (
              <p className="text-sm text-[var(--color-away)]">Pick two different artists.</p>
            )}
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
              <button
                type="button"
                disabled={!ready}
                onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
                className="h-14 rounded-full bg-[linear-gradient(90deg,var(--color-start),var(--color-playing)_55%,var(--color-end))] bg-[length:200%_100%] px-9 text-[16.5px] font-bold tracking-[-.01em] text-[var(--color-bg)] [animation:un-sheen_9s_linear_infinite] motion-safe-only disabled:cursor-not-allowed disabled:opacity-30"
              >
                Build the path
              </button>
              <span className="text-[13.5px] text-[var(--color-label)]">
                Takes about three seconds · no account needed
              </span>
            </div>
          </div>

          <section className="mt-8">
            <h2 className="text-[12.5px] text-[var(--color-label)]">Or start from one of these</h2>
            <ul className="mt-3 flex flex-wrap gap-2.5">
              {SAMPLE_JOURNEYS.map((j) => (
                <li key={j.from}>
                  <Link
                    to={`/path/${j.from}/${j.to}`}
                    aria-label={`${j.fromName} to ${j.toName}, ${j.steps} steps`}
                    className="flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-4 py-2.5 text-[14px] transition-colors hover:border-[var(--color-start)]"
                  >
                    <span>{j.fromName}</span>
                    <span aria-hidden className="text-[var(--color-label)]">→</span>
                    <span>{j.toName}</span>
                    <span className="text-[12px] text-[var(--color-label)]">{j.steps} steps</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* The desktop hero's right column: the mark, breathing, and the teaser (UXR-D14).
            Hidden below lg — the mobile artboard shows the mark alone, above the h1. */}
        <div className="hidden flex-col items-center gap-7 lg:flex">
          <div className="relative flex size-[300px] items-center justify-center">
            <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle,rgba(143,108,245,.28),rgba(46,197,238,.12)_45%,transparent_70%)]" aria-hidden />
            <img src="/unsung-mark.png" alt="" width={246} height={246} className="relative" />
          </div>
          <div className="w-full max-w-[420px] rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-5">
            <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">
              A path, {TEASER.names.length - 2 === 5 ? 'five' : `${TEASER.names.length - 2}`} steps
            </div>
            <ol className="relative mt-4 flex flex-col gap-3 pl-5">
              <span aria-hidden className="absolute bottom-1.5 left-[3px] top-1.5 w-0.5 rounded-full bg-gradient-to-b from-[var(--color-start)] via-[var(--color-playing)] to-[var(--color-end)]" />
              {TEASER.names.map((name) => (
                <li key={name} className="relative flex items-center gap-2.5 text-[14.5px]">
                  <span aria-hidden className="absolute -left-[22px] size-2 rounded-full border-2 border-[var(--color-playing)] bg-[var(--color-surface)]" />
                  {name}
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      <section className="mt-14 grid gap-5 border-t border-[var(--color-border)] pt-10 md:grid-cols-3">
        {HOW.map((h) => (
          <div key={h.n} className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-6">
            <div className="flex items-center gap-3">
              <span className="font-display text-[13px] font-bold tracking-[.06em]" style={{ color: h.tone }}>{h.n}</span>
              <span aria-hidden className="h-px flex-1" style={{ background: `linear-gradient(90deg, ${h.tone}, transparent)` }} />
            </div>
            <h3 className="mt-4 font-display text-[21px] font-medium tracking-[-.02em]">{h.title}</h3>
            <p className="mt-2 text-[14.5px] leading-[1.55] text-[var(--color-muted)] text-pretty">{h.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
```

`ArtistCountBadge` does not exist until `UXR-T4`. For this task create a stub `frontend/src/components/ArtistCountBadge.tsx` that returns `null` with a comment `// Filled in by UXR-T4.`; `UXR-T4` replaces it.

In `ArtistSearch.tsx` the label text changes from "From"/"To" to "Start with"/"End with" **at the call site only** — the component takes `label` as a prop. Tests that call `getByLabelText('From')` and `getByLabelText('To')` — `LandingPage.test.tsx` (three places), `e2e/path.spec.ts`, `e2e/responsive.spec.ts` (three tests), `e2e/playback.spec.ts` if it fills the boxes — change to `'Start with'` / `'End with'`. Grep: `grep -rn "getByLabel(\?'\(From\|To\)'" src e2e`.

- [ ] **Step 4: Run the tests to see them pass**

Run: `npx vitest run src/routes/LandingPage.test.tsx && npm test` — Expected: PASS.

- [ ] **Step 5: Screenshots, then commit**

`node e2e/screenshot.mjs /` — look at both. At 390 px: mark absent (that column is hidden), fields stacked, chips wrapping, How-it-works stacked. At 1280 px: two columns, teaser visible.

```bash
git add frontend/src/routes/LandingPage.tsx frontend/src/routes/LandingPage.test.tsx frontend/src/components/ArtistCountBadge.tsx frontend/e2e/path.spec.ts frontend/e2e/responsive.spec.ts frontend/e2e/playback.spec.ts
git commit -m "UXR-T3: the landing page — hero, chips with steps, how it works, the teaser" -- frontend/src/routes/LandingPage.tsx frontend/src/routes/LandingPage.test.tsx frontend/src/components/ArtistCountBadge.tsx frontend/e2e/path.spec.ts frontend/e2e/responsive.spec.ts frontend/e2e/playback.spec.ts
```

Append `## §3 UXR-T3` to the log.

---

### UXR-T4: The live artist count — `GET /api/meta` and the badge

**Files:**
- Modify: `api/src/artistpath_api/models.py` (after `HealthOut`), `api/src/artistpath_api/app.py` (after the `/health` route), `api/tests/test_app.py`
- Modify: `frontend/src/api/client.ts`, `frontend/src/api/client.test.ts`
- Replace: `frontend/src/components/ArtistCountBadge.tsx`; create `ArtistCountBadge.test.tsx`

**Interfaces:**
- Produces: `GET /api/meta` → `{"artists": int, "graph_sha256": str}`; `client.getMeta(signal?) → Promise<{ artists: number; graphSha256: string }>`; `ArtistCountBadge()` renders `"{floor-to-thousand} artists mapped by who listens to whom"` or nothing.

- [ ] **Step 1: The API test, red**

In `api/tests/test_app.py`, next to `test_health_reports_artifact_identity`, add:

```python
def test_meta_is_reachable_under_api_and_carries_the_count():
    # UXR-D8: /health is deliberately off /api (App Runner reaches it directly)
    # and CloudFront routes only /api/*, so the landing badge needs THIS route.
    client = make_client()
    r = client.get("/api/meta")
    assert r.status_code == 200
    body = r.json()
    assert body["artists"] == client.app.state.store.artist_count
    assert body["graph_sha256"] == client.app.state.store.source_sha256


def test_meta_is_a_coroutine_so_it_never_queues_for_a_thread():
    # Same discipline as /health (G3-A1): three in-memory reads, no I/O.
    import inspect
    from artistpath_api.app import create_app
    app = make_client().app
    route = next(r for r in app.routes if getattr(r, "path", "") == "/api/meta")
    assert inspect.iscoroutinefunction(route.endpoint)
```

Use whatever helper `test_health_reports_artifact_identity` uses to build its client (read that test first; if it uses a module-level `client`, use the same and drop `make_client()`), and adapt the two `store` reads to however that test reaches the store.

Run from `api/`: `UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k meta`
Expected: FAIL — 404.

- [ ] **Step 2: The route**

`api/src/artistpath_api/models.py`, after `HealthOut`:

```python
class MetaOut(BaseModel):
    """What the landing page may say about the map. UXR-D8.

    A subset of HealthOut, served under /api because /health is not reachable
    through CloudFront by design. Additive; nothing consumes it but the badge.
    """

    artists: int
    graph_sha256: str
```

`api/src/artistpath_api/app.py`: import `MetaOut` alongside `HealthOut`, and after the `/health` route add:

```python
    @app.get("/api/meta")
    async def meta() -> MetaOut:
        # `async def` for the same reason /health is (G3-A1): in-memory reads
        # only, so it must never queue behind build_path in the thread pool.
        return MetaOut(artists=store.artist_count, graph_sha256=store.source_sha256)
```

Run the two tests — Expected: PASS. Then the whole api suite: `UV_LINK_MODE=copy uv run --extra dev pytest -q` — Expected: green.

- [ ] **Step 3: Snyk the api diff**

Run `snyk_code_scan` on `api/`. Expected: no new findings. Fix and rescan if any.

- [ ] **Step 4: The client, red then green**

In `frontend/src/api/client.test.ts` add (mirror the file's existing `fetch` mocking pattern):

```ts
test('getMeta reads the count and the artifact identity', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify({ artists: 58838, graph_sha256: 'abc' }), { status: 200 }),
  );
  await expect(getMeta()).resolves.toEqual({ artists: 58838, graphSha256: 'abc' });
});
```

Run: `npx vitest run src/api/client.test.ts` — Expected: FAIL, `getMeta` not exported.

Add to `frontend/src/api/client.ts` (and `meta: 5_000` to `TIMEOUT_MS`):

```ts
/** What the landing page may say about the map (UXR-D8). Decorative: callers must tolerate failure. */
export async function getMeta(signal?: AbortSignal): Promise<{ artists: number; graphSha256: string }> {
  const r = await fetchWithTimeout(`${BASE}/meta`, {}, TIMEOUT_MS.meta, signal);
  if (!r.ok) throw new ApiError(r.status);
  const d = (await r.json()) as { artists: number; graph_sha256: string };
  return { artists: d.artists, graphSha256: d.graph_sha256 };
}
```

Run — Expected: PASS.

- [ ] **Step 5: The badge, red then green**

Create `frontend/src/components/ArtistCountBadge.test.tsx`:

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCountBadge } from './ArtistCountBadge';

afterEach(() => vi.restoreAllMocks());

test('floors the count to the nearest thousand and says what the map is', async () => {
  vi.spyOn(client, 'getMeta').mockResolvedValue({ artists: 58838, graphSha256: 'x' });
  render(<ArtistCountBadge />);
  expect(await screen.findByText('58,000 artists mapped by who listens to whom')).toBeInTheDocument();
});

test('renders nothing at all when the request fails — a decoration cannot break the page (UI-7)', async () => {
  vi.spyOn(client, 'getMeta').mockRejectedValue(new Error('down'));
  const { container } = render(<ArtistCountBadge />);
  await waitFor(() => expect(client.getMeta).toHaveBeenCalled());
  expect(container).toBeEmptyDOMElement();
});
```

Run — Expected: FAIL (the stub renders nothing in both cases; the first test fails).

Replace `frontend/src/components/ArtistCountBadge.tsx`:

```tsx
import { useEffect, useState } from 'react';
import * as client from '@/api/client';

/**
 * "58,000 artists mapped by who listens to whom" — live, from /api/meta (UXR-D8).
 *
 * Floored to the nearest thousand: the exact count changes with every rebuild and
 * is a fact about the artifact, not a promise to the visitor. Renders NOTHING on
 * any failure (UI-7): this is decoration, and a decoration must not be able to
 * turn a working landing page into an error.
 */
export function ArtistCountBadge() {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    client.getMeta(controller.signal)
      .then((m) => setCount(m.artists))
      .catch(() => setCount(null));
    return () => controller.abort();
  }, []);

  if (count === null || count < 1000) return null;
  const floored = Math.floor(count / 1000) * 1000;
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-3.5 py-1.5 text-[12.5px] text-[var(--color-muted)]">
      <span aria-hidden className="size-1.5 rounded-full bg-[var(--color-start)] [animation:ap-pulse_1.8s_ease-in-out_infinite]" />
      {floored.toLocaleString('en-US')} artists mapped by who listens to whom
    </div>
  );
}
```

Run: `npx vitest run src/components/ArtistCountBadge.test.tsx` — Expected: PASS. `LandingPage.test.tsx` now calls the real `getMeta` — it will reject in jsdom (no server) and render nothing, which is the designed behaviour; if a test there becomes noisy, add `vi.spyOn(client, 'getMeta').mockRejectedValue(new Error('offline'))` to its `setup()`.

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/models.py api/src/artistpath_api/app.py api/tests/test_app.py frontend/src/api/client.ts frontend/src/api/client.test.ts frontend/src/components/ArtistCountBadge.tsx frontend/src/components/ArtistCountBadge.test.tsx frontend/src/routes/LandingPage.test.tsx
git commit -m "UXR-T4: GET /api/meta, and the landing badge that reads it or says nothing" -- api/src/artistpath_api/models.py api/src/artistpath_api/app.py api/tests/test_app.py frontend/src/api/client.ts frontend/src/api/client.test.ts frontend/src/components/ArtistCountBadge.tsx frontend/src/components/ArtistCountBadge.test.tsx frontend/src/routes/LandingPage.test.tsx
```

Append `## §4 UXR-T4` to the log, including the Snyk result.

---

### UXR-T5: Player progress and "Stop N of M"

**Files:**
- Modify: `frontend/src/player/Player.ts`, `Player.test.ts`, `usePlayer.ts`, `usePlayer.test.tsx`
- Modify: `frontend/src/components/PlayerBar.tsx`, create `PlayerBar.test.tsx`
- Modify: `frontend/src/components/JourneyList.tsx` (only the `<PlayerBar>` call)

**Interfaces:**
- Produces: `Player.onTimeUpdate(cb: (position: number, duration: number) => void)`; `usePlayer(...)` additionally returns `{ position: number; duration: number }` in seconds; `PlayerBar({ currentName, trackTitle, isPlaying, position, duration, stopIndex, stopCount, onToggle })` where `stopIndex` is 0-based and rendered 1-based.

- [ ] **Step 1: Player, red**

Append to `frontend/src/player/Player.test.ts`:

```ts
test('timeupdate reports position and duration in seconds', () => {
  const player = new HtmlAudioPlayer();
  const audio = audioOf(player);
  Object.defineProperty(audio, 'currentTime', { value: 11.2, configurable: true });
  Object.defineProperty(audio, 'duration', { value: 30, configurable: true });
  const cb = vi.fn();
  player.onTimeUpdate(cb);
  audio.dispatchEvent(new Event('timeupdate'));
  expect(cb).toHaveBeenCalledWith(11.2, 30);
});

test('a second timeupdate handler replaces the first, like the other two', () => {
  const player = new HtmlAudioPlayer();
  const first = vi.fn();
  const second = vi.fn();
  player.onTimeUpdate(first);
  player.onTimeUpdate(second);
  audioOf(player).dispatchEvent(new Event('timeupdate'));
  expect(first).not.toHaveBeenCalled();
  expect(second).toHaveBeenCalledTimes(1);
});
```

Run: `npx vitest run src/player/Player.test.ts` — Expected: FAIL, `onTimeUpdate` is not a function.

- [ ] **Step 2: Player, green**

In `Player.ts`: add to the interface `onTimeUpdate(cb: (position: number, duration: number) => void): void;`. In `HtmlAudioPlayer` add a field `private timeCb?: () => void;` and:

```ts
  // Same replace-never-accumulate rule as onEnded/onError, for the same
  // StrictMode reason. Duration is NaN before metadata loads; report 0 then, so
  // a consumer never divides by NaN.
  onTimeUpdate(cb: (position: number, duration: number) => void): void {
    if (this.timeCb) this.audio.removeEventListener('timeupdate', this.timeCb);
    this.disposed = false;
    this.timeCb = () => {
      const d = this.audio.duration;
      cb(this.audio.currentTime, Number.isFinite(d) ? d : 0);
    };
    this.audio.addEventListener('timeupdate', this.timeCb);
  }
```

and in `dispose()` detach it too (`if (this.timeCb) this.audio.removeEventListener('timeupdate', this.timeCb); this.timeCb = undefined;`).

Run — Expected: PASS.

- [ ] **Step 3: usePlayer, red then green**

In `usePlayer.test.tsx`, the mocked `HtmlAudioPlayer` class gains `onTimeUpdate(cb) { timed.push(cb); }` with a module-level `const timed: Array<(p: number, d: number) => void> = [];` reset in `beforeEach`. Add to `Harness` a `<span data-testid="pos">{p.position}/{p.duration}</span>` and this test:

```tsx
test('position and duration follow the audio element and reset when playback stops', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));
  act(() => timed.at(-1)?.(11.2, 30));
  expect(screen.getByTestId('pos')).toHaveTextContent('11.2/30');
  act(() => ended.at(-1)?.()); // miles ends, kraftwerk starts
  act(() => ended.at(-1)?.()); // kraftwerk ends, nothing next
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('none'));
  expect(screen.getByTestId('pos')).toHaveTextContent('0/0');
});
```

Run — Expected: FAIL (`position` undefined).

In `usePlayer.ts`: add `const [position, setPosition] = useState(0); const [duration, setDuration] = useState(0);`; in `clear()` also `setPosition(0); setDuration(0);`; in the effect, before `return () => player.dispose();`, add `player.onTimeUpdate((p, d) => { setPosition(p); setDuration(d); });`; in `start()` after `setIsPlaying(true)` add `setPosition(0);`. Return `{ currentMbid, isPlaying, position, duration, playFrom, toggle, stop }`.

Run — Expected: PASS.

- [ ] **Step 4: PlayerBar, red then green**

Create `frontend/src/components/PlayerBar.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { PlayerBar } from './PlayerBar';

const base = { currentName: 'Herbie Hancock', trackTitle: 'Watermelon Man', isPlaying: true, onToggle: vi.fn() };

test('shows elapsed and total time and the stop position in the whole-journey currency', () => {
  // UXR-D10: N of M counts EVERY artist including both endpoints; index is 0-based in.
  render(<PlayerBar {...base} position={11.2} duration={30} stopIndex={1} stopCount={6} />);
  expect(screen.getByText('0:11')).toBeInTheDocument();
  expect(screen.getByText('0:30')).toBeInTheDocument();
  expect(screen.getByText('Stop 2 of 6')).toBeInTheDocument();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '37');
});

test('renders nothing with no current artist', () => {
  const { container } = render(<PlayerBar {...base} currentName={null} position={0} duration={0} stopIndex={-1} stopCount={0} />);
  expect(container).toBeEmptyDOMElement();
});
```

Run — Expected: FAIL (props unknown; no progressbar).

Replace `PlayerBar.tsx`:

```tsx
import { PlayButton } from './PlayButton';

interface Props {
  currentName: string | null;
  trackTitle: string | null;
  isPlaying: boolean;
  /** Seconds, from the audio element's own clock — never estimated. */
  position: number;
  duration: number;
  /** 0-based position among ALL artists including endpoints (UXR-D10). -1 when none. */
  stopIndex: number;
  stopCount: number;
  onToggle: () => void;
}

function mmss(s: number): string {
  const whole = Math.max(0, Math.floor(s));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`;
}

export function PlayerBar({ currentName, trackTitle, isPlaying, position, duration, stopIndex, stopCount, onToggle }: Props) {
  if (!currentName) return null;
  const pct = duration > 0 ? Math.min(100, Math.round((position / duration) * 100)) : 0;
  return (
    <div className="fixed inset-x-0 bottom-0 border-t border-[var(--color-bar-border)] bg-[var(--color-bar)] px-5 pt-3.5 pb-[calc(1.25rem+env(safe-area-inset-bottom))]">
      <div className="mx-auto flex w-full max-w-[1200px] items-center gap-4">
        <PlayButton state={isPlaying ? 'pause' : 'play'} size="bar" onClick={onToggle} />
        <div className="min-w-0 flex-1">
          <div className="truncate text-[14px] font-semibold">
            {currentName}
            {trackTitle && <span className="font-normal text-[var(--color-label)]"> — {trackTitle}</span>}
          </div>
          <div className="mt-2 flex items-center gap-2.5">
            <span className="text-[11.5px] text-[var(--color-label)]">{mmss(position)}</span>
            <div
              role="progressbar"
              aria-label="Clip progress"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={pct}
              className="relative h-[3px] flex-1 rounded-full bg-[var(--color-border)]"
            >
              <span
                className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-[var(--color-start)] to-[var(--color-playing)]"
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-[11.5px] text-[var(--color-label)]">{mmss(duration)}</span>
          </div>
        </div>
        {stopIndex >= 0 && (
          <span className="hidden flex-none rounded-full border border-[var(--color-border-strong)] px-3.5 py-2 text-[12.5px] text-[var(--color-muted)] sm:inline">
            Stop {stopIndex + 1} of {stopCount}
          </span>
        )}
      </div>
    </div>
  );
}
```

Run — Expected: PASS.

- [ ] **Step 5: Wire it in `JourneyList.tsx`**

Replace the `<PlayerBar …/>` call with:

```tsx
      <PlayerBar
        currentName={currentName}
        trackTitle={currentTrackTitle}
        isPlaying={player.isPlaying}
        position={player.position}
        duration={player.duration}
        stopIndex={artists.findIndex((a) => a.mbid === player.currentMbid)}
        stopCount={artists.length}
        onToggle={player.toggle}
      />
```

`currentTrackTitle` needs the playing card's resolved title, which lives in the clip cache. Import `useClip`'s cache read: add to `useClip.ts` an exported `export function cachedTrack(mbid: string, index = 0): Track | null { return fresh(mbid, index)?.track ?? null; }` and in `JourneyList` compute `const currentTrackTitle = player.currentMbid ? cachedTrack(player.currentMbid, clipIndex[player.currentMbid] ?? 0)?.title ?? null : null;`.

Run: `npm test && npm run build` — Expected: green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/player/Player.ts frontend/src/player/Player.test.ts frontend/src/player/usePlayer.ts frontend/src/player/usePlayer.test.tsx frontend/src/components/PlayerBar.tsx frontend/src/components/PlayerBar.test.tsx frontend/src/components/JourneyList.tsx frontend/src/hooks/useClip.ts
git commit -m "UXR-T5: the player bar reports where it is — progress, times, stop N of M" -- frontend/src/player/Player.ts frontend/src/player/Player.test.ts frontend/src/player/usePlayer.ts frontend/src/player/usePlayer.test.tsx frontend/src/components/PlayerBar.tsx frontend/src/components/PlayerBar.test.tsx frontend/src/components/JourneyList.tsx frontend/src/hooks/useClip.ts
```

Append `## §5 UXR-T5` to the log. **HANDOFF SEAM.** Everything so far is independent of the layout change; a fresh session can take T6 onward from the log.

---

### UXR-T6: The card sheds what it does not need to listen

**Files:**
- Modify: `frontend/src/components/ArtistCard.tsx`, `ArtistCard.test.tsx`
- Modify: `frontend/src/components/JourneyList.tsx`, `JourneyList.test.tsx`, `frontend/src/routes/PathPage.test.tsx` (the `pressBypass` helper — temporarily; `UXR-T7` finishes it)

**Interfaces:**
- Produces: `ArtistCard` props become `{ artist, index, total, isPlaying, isCurrent, isEndpoint, endpointLabel, isNew, isSelected, onPlay, onToggle, onDetail, onClipResolved, clipIndex, onDeadIndex }`. **Removed:** `onBypass`, `onCycleClip`. The detail button's accessible name is `About {artist.name}`.

- [ ] **Step 1: Tests, red**

In `ArtistCard.test.tsx`:
- Delete the two Dig-deeper tests (`one bypass control…` and `the bypass control does not read as rejecting…`) — they move to `ArtistDetail.test.tsx` in `UXR-T7`. Note in the log that `REQ-45`'s guard moves with them.
- Change `getByText('Starting artist')` → `getByText('You started here')` and `getByText('Destination artist')` → `getByText('You were heading here')` (`UXR-D15`).
- Replace every `onBypass={vi.fn()}` with `onDetail={vi.fn()} index={1} total={3}`.
- Add:

```tsx
test('the detail button carries the artist name, and the card carries no links or facts itself', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 3 });
  const onDetail = vi.fn();
  render(
    <ArtistCard
      artist={{ ...artist('detail'), facts: { type: 'Group', country: 'FR', area: 'France', begin: '1995', end: null, ended: false } }}
      index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={onDetail}
    />,
  );
  await user.click(screen.getByRole('button', { name: 'About Miles Davis' }));
  expect(onDetail).toHaveBeenCalledTimes(1);
  // UXR-D2: what a listener needs AFTER listening lives in the detail, not here.
  expect(screen.queryByRole('link', { name: /spotify/i })).not.toBeInTheDocument();
  expect(screen.queryByText(/try another track/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/dig deeper/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/France/)).not.toBeInTheDocument();
});
```

In `JourneyList.test.tsx`, the test `bypass is offered on the artists in the middle…` changes its assertion to count detail buttons: `expect(screen.getAllByRole('button', { name: /^About / })).toHaveLength(3);` and its title to `every artist, endpoints included, has a detail button`. (`UXR-T7` adds the interior-only Dig deeper assertion back, in the detail.)

In `PathPage.test.tsx`, `pressBypass` will break; leave it — `UXR-T7` rewrites it. Run only the two files here.

Run: `npx vitest run src/components/ArtistCard.test.tsx src/components/JourneyList.test.tsx` — Expected: FAIL (no "About …" button; old eyebrows).

- [ ] **Step 2: Rewrite the card**

Replace `ArtistCard.tsx`:

```tsx
import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import { PlayButton } from './PlayButton';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
  /** 0-based position among ALL artists including endpoints; drives the rail dot's colour. */
  index: number;
  total: number;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  isEndpoint?: boolean;
  endpointLabel?: 'start' | 'destination';
  /** Not on the previous path; marked briefly on arrival. */
  isNew?: boolean;
  /** Its detail is open (UXR-D3). */
  isSelected?: boolean;
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  onDetail: () => void;
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
  clipIndex?: number;
  onDeadIndex?: (mbid: string) => void;
}

/** Cyan at the start, pink at the end, violet-ish between — the rail's own gradient, per stop. */
function dotColour(index: number, total: number): string {
  if (index === 0) return 'var(--color-start)';
  if (index === total - 1) return 'var(--color-end)';
  return 'var(--color-playing)';
}

/**
 * One stop on the journey — the LISTENING surface only (UXR-D2).
 *
 * Cover, name, track, play, and a button to the detail. The facts line, the
 * streaming links, "Try another track" and "Dig deeper" all moved to
 * ArtistDetail on 2026-09-08; the card is what you press to hear, the detail is
 * where you go once you have.
 */
export function ArtistCard({
  artist, index, total, isPlaying, isCurrent, isEndpoint, endpointLabel, isNew, isSelected,
  onPlay, onToggle, onDetail, onClipResolved, clipIndex, onDeadIndex,
}: Props) {
  const clip = useClip(artist.mbid, clipIndex ?? 0);
  const playable = clip.status === 'ready';
  const silent = clip.status === 'none';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, playable);
    if (!playable && (clipIndex ?? 0) > 0) onDeadIndex?.(artist.mbid);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  const frame = isSelected
    ? 'border-[1.5px] border-[var(--color-detail)] bg-[#12141d] shadow-[0_0_0_4px_rgba(79,127,224,.1)]'
    : isPlaying
      ? 'border border-[rgba(143,108,245,.45)] bg-[linear-gradient(120deg,rgba(143,108,245,.16),rgba(46,197,238,.07))]'
      : isEndpoint
        ? 'border border-[var(--color-border-hover)] bg-[var(--color-surface-raised)]'
        : 'border border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-border-hover)]';

  return (
    <div className="relative">
      {/* The rail dot for this stop. Sits on the rail JourneyList draws. */}
      <span
        aria-hidden
        className="absolute -left-[29px] top-1/2 size-[13px] -translate-y-1/2 rounded-full border-[3px] bg-[var(--color-bg)]"
        style={{ borderColor: isSelected ? 'var(--color-detail)' : dotColour(index, total) }}
      />
      <div className={`flex items-center gap-3 rounded-2xl px-3.5 py-3 sm:gap-4 sm:px-[18px] sm:py-3.5 ${frame} ${isNew ? '[animation:ap-glow_800ms_ease-out]' : ''}`}>
        <div
          className={`size-12 flex-none rounded-[10px] bg-[var(--color-border)] bg-cover sm:size-[54px] ${silent ? 'opacity-75' : ''}`}
          style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
          aria-hidden
        />
        <div className="min-w-0 flex-1">
          {endpointLabel && (
            <div
              className="text-[10px] font-bold uppercase tracking-[.16em]"
              style={{ color: endpointLabel === 'start' ? 'var(--color-start)' : 'var(--color-end)' }}
            >
              {endpointLabel === 'start' ? 'You started here' : 'You were heading here'}
            </div>
          )}
          <div className="flex items-center gap-2.5">
            {/* UI-5: data-testid, not a style class — e2e/responsive.spec.ts measures it. */}
            <div data-testid="artist-name" className="truncate font-display text-[16.5px] font-semibold tracking-[-.02em] sm:text-[19px]">
              {artist.name}
            </div>
            {isPlaying && (
              <span className="flex h-[13px] flex-none items-end gap-0.5" aria-label="now playing" role="img">
                {[0, 0.15, 0.3].map((delay) => (
                  <span key={delay} className="block h-full w-[3px] origin-bottom rounded-[1px] bg-[var(--color-playing)] [animation:un-eq_.9s_ease-in-out_infinite] motion-safe-only" style={{ animationDelay: `${delay}s` }} />
                ))}
              </span>
            )}
          </div>
          <div className="mt-1 flex items-baseline gap-1.5 text-[12.5px] sm:text-[13px]">
            <span className={`truncate ${silent ? 'text-[var(--color-label)]' : 'text-[var(--color-muted)]'}`}>
              {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
            </span>
            {playable && <span className="flex-none text-[var(--color-label)]">· 0:30</span>}
          </div>
        </div>
        <button
          type="button"
          onClick={onDetail}
          aria-label={`About ${artist.name}`}
          aria-expanded={isSelected ?? false}
          className={`flex size-11 flex-none items-center justify-center rounded-full border text-[15px] sm:size-[46px] ${
            isSelected
              ? 'border-[var(--color-detail)] bg-[rgba(79,127,224,.16)] text-[var(--color-text)]'
              : 'border-[var(--color-border-strong)] text-[var(--color-muted)] hover:text-[var(--color-text)]'
          }`}
        >
          <span aria-hidden>›</span>
        </button>
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="card"
          disabled={!playable}
          onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        />
      </div>
    </div>
  );
}
```

The old `▮▮▮ now playing` text is gone; tests that used `getByText(/now playing/i)` (`JourneyList.test.tsx` ×3, `PathPage.test.tsx` ×3, `e2e/playback.spec.ts`'s `playingCardIndex`) now match the `aria-label="now playing"` — change `getByText(/now playing/i)` to `getByRole('img', { name: /now playing/i })` in the unit tests, and in `playback.spec.ts` change `innerText().match(/now playing/i)` to `page.locator('ol li').nth(i).getByRole('img', { name: /now playing/i }).count() > 0`.

- [ ] **Step 3: Wire `JourneyList.tsx` minimally**

In the `<ArtistCard>` call: add `index={i} total={artists.length} onDetail={() => setSelected(artist.mbid)} isSelected={selected === artist.mbid}` and remove `onBypass` and `onCycleClip`. Add `const [selected, setSelected] = useState<string | null>(null);`. Keep `onBypass` in `JourneyList`'s own props (the detail uses it in `UXR-T7`); the compiler will complain that `onBypass` and `cycleClip` are unused — that is fine for this commit only if `npm run lint` tolerates it; if not, prefix with `void onBypass;` temporarily and remove in `UXR-T7`. Change the `<ol>` to `pl-[26px]` with the rail at `left-[5px] top-[41px] bottom-[41px]`.

- [ ] **Step 4: Run the two files, then commit**

Run: `npx vitest run src/components/ArtistCard.test.tsx src/components/JourneyList.test.tsx src/player` — Expected: PASS. (`PathPage.test.tsx` is red until `UXR-T7`; say so in the commit message.)

```bash
git add frontend/src/components/ArtistCard.tsx frontend/src/components/ArtistCard.test.tsx frontend/src/components/JourneyList.tsx frontend/src/components/JourneyList.test.tsx frontend/e2e/playback.spec.ts
git commit -m "UXR-T6: the card is the listening surface — detail button in, facts/links/bypass out (PathPage tests red until T7)" -- frontend/src/components/ArtistCard.tsx frontend/src/components/ArtistCard.test.tsx frontend/src/components/JourneyList.tsx frontend/src/components/JourneyList.test.tsx frontend/e2e/playback.spec.ts
```

Append `## §6 UXR-T6` to the log.

---

### UXR-T7: The artist detail, docked and as a sheet

**Files:**
- Create: `frontend/src/components/ArtistDetail.tsx`, `ArtistDetail.test.tsx`, `DetailDock.tsx`, `DetailSheet.tsx`, `DetailSheet.test.tsx`
- Modify: `frontend/src/components/JourneyList.tsx`, `JourneyList.test.tsx`, `frontend/src/routes/PathPage.test.tsx`
- Consumes: `ArtistInfo`, `StreamingLinks` (both unchanged), `useClip`, `PlayButton`.

**Interfaces:**
- `ArtistDetail({ artist, index, total, isEndpoint, clipIndex, isPlaying, isCurrent, onPlay, onToggle, onCycleClip, onBypass, onClose })`. Dig deeper renders only when `!isEndpoint`; "Try another track" only when the clip has `candidateCount > 1`.
- `DetailDock({ children })` — `hidden lg:block`, sticky; `DetailSheet({ open, onClose, children })` — `lg:hidden`, `role="dialog"`, closes on Escape and scrim.

- [ ] **Step 1: ArtistDetail tests, red**

Create `frontend/src/components/ArtistDetail.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistDetail } from './ArtistDetail';

afterEach(() => vi.restoreAllMocks());

const air = {
  mbid: 'air', name: 'Air', disambiguation: 'French duo', popularity: 0.5,
  spotifyId: '1', appleId: null,
  facts: { type: 'Group', country: 'FR', area: 'Versailles', begin: '1995', end: null, ended: false },
};
const base = {
  artist: air, index: 2, total: 6, isEndpoint: false, clipIndex: 0, isPlaying: false, isCurrent: false,
  onPlay: vi.fn(), onToggle: vi.fn(), onCycleClip: vi.fn(), onBypass: vi.fn(), onClose: vi.fn(),
};

test('says which stop this is, shows the facts, and offers both services', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'La Femme', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistDetail {...base} />);
  expect(screen.getByText('Stop 3 of 6')).toBeInTheDocument();
  expect(screen.getByText(/French duo · Group · Versailles · 1995–/)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Air on Spotify' })).toHaveAttribute('href', 'https://open.spotify.com/artist/1');
  expect(screen.getByRole('link', { name: 'Air on Apple Music' })).toHaveAttribute('href', /music\.apple\.com\/search/);
});

test('one bypass control, on interior artists only, and it fires the known signal', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onBypass = vi.fn();
  render(<ArtistDetail {...base} onBypass={onBypass} />);
  await user.click(screen.getByRole('button', { name: /dig deeper/i }));
  expect(onBypass).toHaveBeenCalledWith('air');
});

test('an endpoint gets no bypass control', () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base} isEndpoint />);
  expect(screen.queryByRole('button', { name: /dig deeper/i })).not.toBeInTheDocument();
});

// REQ-45, moved here from the card with the control.
test('the bypass control does not read as rejecting the artist', () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base} />);
  expect(screen.queryByText(/not for me|dislike|reject|no thanks|steer away/i)).not.toBeInTheDocument();
  expect(screen.getByText(/rebuilds the whole journey/i)).toBeInTheDocument();
  expect(screen.queryByText(/recommended/i)).not.toBeInTheDocument(); // UXR-D16
});

test('"Try another track" appears only when there is another track', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 3 });
  const onCycleClip = vi.fn();
  render(<ArtistDetail {...base} onCycleClip={onCycleClip} />);
  await user.click(await screen.findByRole('button', { name: /try another track/i }));
  expect(onCycleClip).toHaveBeenCalledWith(3);
});
```

Run: `npx vitest run src/components/ArtistDetail.test.tsx` — Expected: FAIL, module missing.

- [ ] **Step 2: ArtistDetail**

```tsx
import { useClip } from '@/hooks/useClip';
import { ArtistInfo } from './ArtistInfo';
import { PlayButton } from './PlayButton';
import { StreamingLinks } from './StreamingLinks';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
  /** 0-based among ALL artists including endpoints; shown 1-based (UXR-D10 currency). */
  index: number;
  total: number;
  isEndpoint: boolean;
  clipIndex: number;
  isPlaying: boolean;
  isCurrent: boolean;
  onPlay: (mbid: string) => void;
  onToggle: () => void;
  onCycleClip: (candidateCount: number) => void;
  onBypass: (mbid: string) => void;
  onClose: () => void;
}

/**
 * Everything about a stop that is not the clip (UXR-D2). Rendered by DetailDock
 * at lg and by DetailSheet below it — one component, two containers (UXR-D3).
 *
 * The facts line (ArtistInfo) and the two links (StreamingLinks) are the LUX-4
 * components unchanged; only their home moved. "Dig deeper" lives here so it
 * cannot be hit by accident on the card (owner decision 2, 2026-09-08).
 */
export function ArtistDetail({
  artist, index, total, isEndpoint, clipIndex, isPlaying, isCurrent,
  onPlay, onToggle, onCycleClip, onBypass, onClose,
}: Props) {
  const clip = useClip(artist.mbid, clipIndex);
  const playable = clip.status === 'ready';
  const candidates = clip.track?.candidateCount ?? 0;

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between border-b border-[var(--color-detail-hairline)] px-[18px] py-3.5">
        <span className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-detail-fg)]">
          Stop {index + 1} of {total}
        </span>
        <button type="button" onClick={onClose} aria-label="Close" className="flex size-9 items-center justify-center rounded-full border border-[var(--color-detail-border)] text-[14px] text-[var(--color-muted)]">
          <span aria-hidden>✕</span>
        </button>
      </div>

      <div className="flex flex-col gap-[18px] px-[18px] pb-[22px] pt-5">
        <div className="flex items-center gap-3.5">
          <div className="size-[86px] flex-none rounded-[14px] bg-[var(--color-border)] bg-cover" style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined} aria-hidden />
          <div className="min-w-0">
            <div className="font-display text-[26px] font-semibold tracking-[-.03em]">{artist.name}</div>
            <ArtistInfo artist={artist} />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <PlayButton state={isPlaying ? 'pause' : 'play'} size="card" disabled={!playable} onClick={() => (isCurrent ? onToggle() : onPlay(artist.mbid))} />
            <span className="min-w-0 truncate text-[13.5px] text-[var(--color-muted)]">
              {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
              {playable && <span className="text-[var(--color-label)]"> · 0:30</span>}
            </span>
          </div>
          {playable && candidates > 1 && (
            <button type="button" onClick={() => onCycleClip(candidates)} className="self-start text-[12.5px] text-[var(--color-label)] underline-offset-2 hover:text-[var(--color-text)] hover:underline">
              Try another track
            </button>
          )}
        </div>

        <StreamingLinks artist={artist} />

        {!isEndpoint && (
          <>
            <div className="h-px bg-[var(--color-detail-hairline)]" />
            <div className="flex flex-col gap-2">
              <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">Reroute from here</div>
              <button
                type="button"
                onClick={() => onBypass(artist.mbid)}
                className="rounded-xl border border-[rgba(245,71,155,.45)] bg-[linear-gradient(130deg,rgba(245,71,155,.14),rgba(143,108,245,.06))] px-4 py-3.5 text-left"
              >
                <span className="block text-[15.5px] font-semibold">Dig deeper</span>
                <span className="mt-1 block text-[13px] leading-[1.45] text-[var(--color-muted)]">
                  Same vibe, less familiar. Rebuilds the whole journey from this point on.
                </span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

`StreamingLinks` becomes two full-width neutral buttons (`UXR-D4`): change its wrapper to `flex flex-col gap-2` and each `<a>` to `flex h-12 items-center justify-center rounded-full border border-[var(--color-border-strong)] bg-[var(--color-surface-raised)] text-[13.5px] text-[var(--color-text)]` with labels `Open on Spotify` / `Open on Apple Music`. The `aria-label` (`{name} on {service}`) and `rel` are unchanged; `StreamingLinks.test.tsx` and the responsive e2e match on those, so they keep passing.

Run — Expected: PASS.

- [ ] **Step 3: DetailSheet test, red, then both containers**

`DetailSheet.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { DetailSheet } from './DetailSheet';

test('is a dialog that closes on Escape and on the scrim, and renders nothing when closed', async () => {
  const user = userEvent.setup();
  const onClose = vi.fn();
  const { rerender } = render(<DetailSheet open onClose={onClose}><p>content</p></DetailSheet>);
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  await user.keyboard('{Escape}');
  expect(onClose).toHaveBeenCalledTimes(1);
  await user.click(screen.getByTestId('scrim'));
  expect(onClose).toHaveBeenCalledTimes(2);
  rerender(<DetailSheet open={false} onClose={onClose}><p>content</p></DetailSheet>);
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
```

Run — Expected: FAIL, module missing.

`DetailSheet.tsx`:

```tsx
import { useEffect, type ReactNode } from 'react';

interface Props { open: boolean; onClose: () => void; children: ReactNode }

/**
 * The phone container for ArtistDetail (UXR-D3): a bottom sheet over a scrim.
 * lg:hidden — at lg the same children render in DetailDock instead.
 */
export function DetailSheet({ open, onClose, children }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-30 lg:hidden">
      <div data-testid="scrim" onClick={onClose} className="absolute inset-0 bg-black/60" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Artist detail"
        className="absolute inset-x-0 bottom-0 max-h-[88vh] overflow-y-auto rounded-t-[22px] border-t border-[var(--color-detail-border)] bg-[linear-gradient(180deg,#101420,#0b0b11_55%)] shadow-[0_-30px_60px_-20px_rgba(0,0,0,.9)]"
      >
        <div className="flex justify-center pb-1 pt-2.5"><span className="h-1 w-11 rounded-full bg-[var(--color-detail-border)]" /></div>
        {children}
      </div>
    </div>
  );
}
```

`DetailDock.tsx`:

```tsx
import type { ReactNode } from 'react';

/** The desktop container for ArtistDetail (UXR-D3): docked, sticky, beside the rail. */
export function DetailDock({ children }: { children: ReactNode }) {
  return (
    <aside className="hidden lg:block">
      <div className="sticky top-6 overflow-hidden rounded-[18px] border border-[var(--color-detail-border)] bg-[linear-gradient(180deg,#101420,#0c0c12_55%)]">
        {children}
      </div>
    </aside>
  );
}
```

Run — Expected: PASS.

- [ ] **Step 4: JourneyList owns the selection**

Tests first, in `JourneyList.test.tsx`:

```tsx
test('opening an artist shows its detail; Dig deeper there fires the bypass; a new path closes it', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  const onBypass = vi.fn();
  const threeStop = [artists[0], { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9, spotifyId: null, appleId: null, facts: null }, artists[1]];
  const { rerender } = render(<JourneyList artists={threeStop} stopRule="natural" onBypass={onBypass} />);

  expect(screen.queryByText(/stop 2 of 3/i)).not.toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'About Herbie Hancock' }));
  // Two containers, one open at a time by CSS — jsdom has no breakpoints, so
  // both render; assert on the first.
  expect(screen.getAllByText('Stop 2 of 3').length).toBeGreaterThan(0);
  await user.click(screen.getAllByRole('button', { name: /dig deeper/i })[0]);
  expect(onBypass).toHaveBeenCalledWith('h');

  rerender(<JourneyList artists={[artists[0], artists[1]]} stopRule="natural" onBypass={onBypass} />);
  expect(screen.queryByText(/stop 2 of 3/i)).not.toBeInTheDocument();
});

test('an endpoint opens a detail with no bypass control', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  await user.click(screen.getByRole('button', { name: 'About Miles Davis' }));
  expect(screen.getAllByText('Stop 1 of 2').length).toBeGreaterThan(0);
  expect(screen.queryByRole('button', { name: /dig deeper/i })).not.toBeInTheDocument();
});
```

Run — Expected: FAIL.

In `JourneyList.tsx`: reset the selection in the existing `pathKey` effect (`setSelected(null)` next to `stopRef.current()`); build the detail element once:

```tsx
  const selectedIndex = artists.findIndex((a) => a.mbid === selected);
  const detail = selectedIndex >= 0 && (
    <ArtistDetail
      artist={artists[selectedIndex]}
      index={selectedIndex}
      total={artists.length}
      isEndpoint={selectedIndex === 0 || selectedIndex === artists.length - 1}
      clipIndex={clipIndex[artists[selectedIndex].mbid] ?? 0}
      isPlaying={player.currentMbid === selected && player.isPlaying}
      isCurrent={player.currentMbid === selected}
      onPlay={player.playFrom}
      onToggle={player.toggle}
      onCycleClip={(count) => cycleClip(artists[selectedIndex].mbid, count)}
      onBypass={onBypass}
      onClose={() => setSelected(null)}
    />
  );
```

and return:

```tsx
  return (
    <>
      <div className="lg:grid lg:grid-cols-[1fr_400px] lg:items-start lg:gap-10">
        <ol className="relative flex flex-col gap-3 pl-[26px]">
          <span aria-hidden className="absolute bottom-[41px] left-[5px] top-[41px] w-[3px] rounded-full bg-gradient-to-b from-[var(--color-start)] via-[var(--color-playing)] to-[var(--color-end)]" />
          {/* …the existing artists.map(...) with the UXR-T6 card props… */}
        </ol>
        <DetailDock>
          {detail || (
            <p className="px-[18px] py-5 text-[13.5px] text-[var(--color-muted)]">
              Open any artist with › for where to hear more, and to dig deeper from there.
            </p>
          )}
        </DetailDock>
      </div>
      <DetailSheet open={!!detail} onClose={() => setSelected(null)}>{detail}</DetailSheet>
      <PlayerBar … />
    </>
  );
```

Delete any `void onBypass;` left by `UXR-T6`. Update `PathPage.test.tsx`'s helper:

```tsx
async function pressBypass(user: ReturnType<typeof userEvent.setup>) {
  // Two presses since 2026-09-08 (owner decision 2): open the detail, then dig.
  await user.click(screen.getByRole('button', { name: /^About / }));
  await user.click(screen.getAllByRole('button', { name: /dig deeper/i })[0]);
}
```

If a PathPage test opens the *first* card's detail (an endpoint, no Dig deeper), change its `getByRole('button', { name: /^About / })` to `getAllByRole(...)[1]`.

Run: `npm test` — Expected: green across the suite.

- [ ] **Step 5: Screenshots at both widths, commit**

`node e2e/screenshot.mjs /path/561d854a-6a28-4aa7-8c99-323e6ce46c2a/056e4f3e-d505-4dad-8ec1-d04f521cbb56` — at 1280 the dock shows the placeholder; open a detail by hand in a browser and confirm the sheet at 390 and the dock at 1280.

```bash
git add frontend/src/components/ArtistDetail.tsx frontend/src/components/ArtistDetail.test.tsx frontend/src/components/DetailDock.tsx frontend/src/components/DetailSheet.tsx frontend/src/components/DetailSheet.test.tsx frontend/src/components/StreamingLinks.tsx frontend/src/components/JourneyList.tsx frontend/src/components/JourneyList.test.tsx frontend/src/routes/PathPage.test.tsx
git commit -m "UXR-T7: the artist detail — docked at lg, a bottom sheet below, one component" -- frontend/src/components/ArtistDetail.tsx frontend/src/components/ArtistDetail.test.tsx frontend/src/components/DetailDock.tsx frontend/src/components/DetailSheet.tsx frontend/src/components/DetailSheet.test.tsx frontend/src/components/StreamingLinks.tsx frontend/src/components/JourneyList.tsx frontend/src/components/JourneyList.test.tsx frontend/src/routes/PathPage.test.tsx
```

Append `## §7 UXR-T7` to the log: record that `REQ-45`'s guard test moved to `ArtistDetail.test.tsx`.

---

### UXR-T8: The journey page's header, title, share, and the explainer's new words

**Files:**
- Create: `frontend/src/components/JourneyHeading.tsx`, `ShareButton.tsx`, `ShareButton.test.tsx`
- Modify: `frontend/src/routes/PathPage.tsx`, `PathPage.test.tsx`, `frontend/src/components/PathIntro.tsx`, `PathIntro.test.tsx`

**Interfaces:**
- `JourneyHeading({ from, to, steps })` — names in display type and a tile "{steps} steps" (`UXR-D6`).
- `ShareButton()` — shares `location.href`; `UXR-D9`.
- `PathIntro({ stopRule })` — the result line leaves (the tile has it); the explainer stays with new copy.

- [ ] **Step 1: ShareButton test, red**

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import { ShareButton } from './ShareButton';

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

test('uses the Web Share API when the browser has one', async () => {
  const user = userEvent.setup();
  const share = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('navigator', { ...navigator, share });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(share).toHaveBeenCalledWith({ title: 'Unsung.fm', url: window.location.href });
});

test('falls back to the clipboard and says so for a moment', async () => {
  const user = userEvent.setup();
  const writeText = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('navigator', { ...navigator, share: undefined, clipboard: { writeText } });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(writeText).toHaveBeenCalledWith(window.location.href);
  expect(await screen.findByText(/link copied/i)).toBeInTheDocument();
});
```

Run — Expected: FAIL, module missing.

- [ ] **Step 2: ShareButton**

```tsx
import { useEffect, useState } from 'react';

/**
 * Share the journey (UXR-D9). The URL already IS the journey — endpoints and
 * every bypass — so there is nothing to build; the button hands the address
 * bar to the OS share sheet where one exists and to the clipboard elsewhere.
 */
export function ShareButton() {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const t = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(t);
  }, [copied]);

  async function share() {
    const url = window.location.href;
    if (typeof navigator.share === 'function') {
      try { await navigator.share({ title: 'Unsung.fm', url }); } catch { /* user dismissed */ }
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
    } catch { /* nothing to say: the address bar still has it */ }
  }

  return (
    <button type="button" onClick={share} className="rounded-full border border-[var(--color-border-strong)] px-[15px] py-2 text-[13.5px] text-[var(--color-muted)] hover:text-[var(--color-text)]" aria-live="polite">
      {copied ? 'Link copied' : 'Share'}
    </button>
  );
}
```

Run — Expected: PASS.

- [ ] **Step 3: JourneyHeading and the explainer copy, tests red then green**

In `PathPage.test.tsx` add:

```tsx
test('the heading names both artists and counts the steps between them', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
      { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
      { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
    ],
    stopRule: 'natural', bypassed: [], unresolved: [],
  });
  renderAt('/path/m/d');
  expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Miles DavisDaft Punk');
  expect(screen.getByText('1')).toBeInTheDocument();
  expect(screen.getByText(/^steps?$/)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /share/i })).toBeInTheDocument();
});
```

In `PathIntro.test.tsx` change the copy assertion to `expect(screen.getByText(/open any artist in the middle/i)).toBeInTheDocument();` and remove any assertion on "We found a path".

Run — Expected: FAIL.

`JourneyHeading.tsx`:

```tsx
interface Props { from: string; to: string; steps: number }

/** "Your journey" — both names in display type and the steps tile (UXR-D6: artists between). */
export function JourneyHeading({ from, to, steps }: Props) {
  return (
    <div className="flex items-end justify-between gap-6">
      <div className="min-w-0">
        <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">Your journey</div>
        <h1 className="mt-2 flex flex-wrap items-center gap-x-3.5 gap-y-1 font-display text-[23px] font-medium leading-[1.2] tracking-[-.025em] sm:text-[34px] sm:tracking-[-.03em]">
          <span>{from}</span>
          <span aria-hidden className="h-0.5 w-[46px] rounded-full bg-gradient-to-r from-[var(--color-start)] to-[var(--color-end)]" />
          <span>{to}</span>
        </h1>
      </div>
      <div className="flex-none rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-center">
        <div className="font-display text-[20px] font-semibold">{steps}</div>
        <div className="text-[11px] uppercase tracking-[.08em] text-[var(--color-label)]">{steps === 1 ? 'step' : 'steps'}</div>
      </div>
    </div>
  );
}
```

`PathIntro.tsx`: drop the `count` prop and the `<p>We found a path…</p>`; the explainer's three paragraphs become:

```
Open any artist in the middle with › and you will find Dig deeper.
Press it and that artist is replaced by someone with a similar sound who is less well known — you have already covered the obvious route.
It rebuilds the whole journey, so every artist between your two can change — not just the one you pressed.
```

`PathPage.tsx`: the header row becomes `<Brand size="nav" />` left, and right: `Reset path` (only when `hasBypasses`), `<ShareButton />`, `New path` — all as `rounded-full border` pills; `New path`'s border uses `--color-start`. Replace `<PathIntro count=… stopRule=…/>` with `<JourneyHeading from={state.artists[0].name} to={state.artists.at(-1)!.name} steps={state.artists.length - 2} />` followed by `<PathIntro stopRule={state.stopRule} />`. Widen `<main>` to `max-w-[1200px]`.

Run: `npm test` — Expected: green.

- [ ] **Step 4: Screenshots, commit**

```bash
git add frontend/src/components/JourneyHeading.tsx frontend/src/components/ShareButton.tsx frontend/src/components/ShareButton.test.tsx frontend/src/routes/PathPage.tsx frontend/src/routes/PathPage.test.tsx frontend/src/components/PathIntro.tsx frontend/src/components/PathIntro.test.tsx
git commit -m "UXR-T8: the journey header — brand, share, the title and its steps tile" -- frontend/src/components/JourneyHeading.tsx frontend/src/components/ShareButton.tsx frontend/src/components/ShareButton.test.tsx frontend/src/routes/PathPage.tsx frontend/src/routes/PathPage.test.tsx frontend/src/components/PathIntro.tsx frontend/src/components/PathIntro.test.tsx
```

Append `## §8 UXR-T8`. **HANDOFF SEAM.**

---

### UXR-T9: The remaining surfaces, and the aliases go

**Files:**
- Modify: `PathSkeleton.tsx`, `RerollNotice.tsx`, `PathStatus.tsx`, `RouteHistory.tsx`, `ArtistSearch.tsx`, `routes/NotFound.tsx`, `index.css`

No behaviour changes; no new tests. The existing tests for each file must stay green untouched — that is the check that nothing but style moved.

- [ ] **Step 1: Restyle each file to the new tokens**

For each file, replace token references by role: `--color-accent` → `--color-start` (CTA/hover) ; `--color-dig` → `--color-end`; `--color-note`/`--color-placeholder` → `--color-label`; `--color-endpoint` → `--color-border-hover`; `--color-rail-mid` → `--color-playing`; `--color-field-border` → `--color-border-strong`; `--color-field-hover` → `--color-field`; `--color-strip*` → delete the element that used it if any remains. Artist names and headings take `font-display`. `ArtistSearch`'s input: `rounded-xl bg-[var(--color-field)] border-[1.5px] border-[var(--color-border-strong)] focus:border-[var(--color-start)]`, dot colours `--color-start` / `--color-end`. `PathSkeleton`'s rail gradient and endpoint cards follow the journey list's. `RerollNotice`'s dots `--color-start`. `RouteHistory` keeps its structure with `--color-surface` / `--color-border`.

- [ ] **Step 2: Remove the aliases**

In `index.css` delete the `ALIASES` section, then run from `frontend/`: `grep -rhoE 'var\(--color-[a-z-]+\)' src | sort -u` and confirm every name is still defined. `npm run build` — Tailwind does not error on an unknown custom property, which is why the grep is the check.

- [ ] **Step 3: Tests, screenshots, commit**

`npm test && npm run lint && npm run build`; both screenshot commands; look at all four.

```bash
git add frontend/src/components/PathSkeleton.tsx frontend/src/components/RerollNotice.tsx frontend/src/components/PathStatus.tsx frontend/src/components/RouteHistory.tsx frontend/src/components/ArtistSearch.tsx frontend/src/routes/NotFound.tsx frontend/src/index.css
git commit -m "UXR-T9: every remaining surface on the new tokens; the aliases removed" -- frontend/src/components/PathSkeleton.tsx frontend/src/components/RerollNotice.tsx frontend/src/components/PathStatus.tsx frontend/src/components/RouteHistory.tsx frontend/src/components/ArtistSearch.tsx frontend/src/routes/NotFound.tsx frontend/src/index.css
```

Append `## §9 UXR-T9`.

---

### UXR-T10: The real-browser suite

**Files:**
- Modify: `frontend/e2e/path.spec.ts`, `responsive.spec.ts`, `playback.spec.ts` (only what T3/T6 already touched, verified here)
- Create: `frontend/e2e/landing-samples.spec.ts`

Requires the API on :8000 (`cd api && UV_LINK_MODE=copy uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000`).

- [ ] **Step 1: `path.spec.ts` — the bypass is two presses**

Replace `await second.getByRole('button', { name: /dig deeper/i }).click();` with:

```ts
  // Two presses since UXR (owner decision 2): open the detail, then dig.
  await second.getByRole('button', { name: /^About / }).click();
  await page.getByRole('dialog').getByRole('button', { name: /dig deeper/i }).click();
```

(`getByRole('dialog')` is the sheet — this spec runs at Playwright's default 1280 width, where the DOCK shows instead. Use `page.locator('aside, [role=dialog]').getByRole('button', { name: /dig deeper/i }).first()` so the same line works at either width.)

- [ ] **Step 2: `responsive.spec.ts` — the sheet at 390 px**

In the first test, replace assertion 3 with:

```ts
  // 3. The bypass control is reachable at phone width: open the detail (a
  //    bottom sheet here), and Dig deeper is visible inside it. Two presses,
  //    by decision; the second must not need a scroll on an 844px-tall phone.
  await interior.getByRole('button', { name: /^About / }).click();
  const sheet = page.getByRole('dialog');
  await expect(sheet).toBeVisible();
  await expect(sheet.getByRole('button', { name: /dig deeper/i })).toBeInViewport();
  // The sheet must not push the page sideways either.
  const overflowOpen = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflowOpen).toBeLessThanOrEqual(1);
```

In the second test (links), open the detail the same way before asserting on the links, and scope `spotify`/`apple` to `page.getByRole('dialog')`. In the third test (facts line never cut off), open the detail first and run the clipped-element scan over `[role=dialog]` instead of `ol li`.

- [ ] **Step 3: The new spec — chips agree with the router**

Create `frontend/e2e/landing-samples.spec.ts`:

```ts
import { expect, test } from '@playwright/test';
// ⚠ CORRECTED 2026-09-08 (log §3): the constants live in src/lib/sampleJourneys.ts, not
// in LandingPage.tsx as this plan first said — oxlint's fast-refresh rule moved them.
import { SAMPLE_JOURNEYS, TEASER } from '../src/lib/sampleJourneys';

// UXR-D7 / UXR-D14: the chips and the teaser carry counts and names measured on
// the served graph. This is the re-check rule as a test: after any artifact
// adoption it fails if a chip lies, instead of a comment asking someone to look.
test('every sample chip states the step count the live router gives', async ({ request }) => {
  for (const j of SAMPLE_JOURNEYS) {
    const r = await request.post('http://localhost:8000/api/path', {
      data: { sources: [j.from, j.to], exclude: [] },
    });
    expect(r.ok(), `${j.fromName} -> ${j.toName}`).toBeTruthy();
    const body = (await r.json()) as { artists: { name: string }[] };
    expect(body.artists.length - 2, `${j.fromName} -> ${j.toName}`).toBe(j.steps);
  }
});

test('the teaser lists exactly the journey the live router builds', async ({ request }) => {
  const r = await request.post('http://localhost:8000/api/path', {
    data: { sources: [TEASER.from, TEASER.to], exclude: [] },
  });
  const body = (await r.json()) as { artists: { name: string }[] };
  expect(body.artists.map((a) => a.name)).toEqual([...TEASER.names]);
});
```

- [ ] **Step 4: Run the whole suite**

Run from `frontend/`: `npm test && npm run build && npm run test:e2e`
Expected: all green, including `playback.spec.ts` in real Chrome. If `landing-samples` fails, the served graph moved since 2026-09-08 — update the constants in `LandingPage.tsx` to what the router returned and record the new figures in the log; do not weaken the test.

- [ ] **Step 5: Snyk the frontend diff, then commit**

Run `snyk_code_scan` on `frontend/`. Expected: no new findings beyond the known `design/*/support.js` ones.

```bash
git add frontend/e2e/path.spec.ts frontend/e2e/responsive.spec.ts frontend/e2e/playback.spec.ts frontend/e2e/landing-samples.spec.ts
git commit -m "UXR-T10: the e2e suite follows the two-press reroute, and pins the chips to the router" -- frontend/e2e/path.spec.ts frontend/e2e/responsive.spec.ts frontend/e2e/playback.spec.ts frontend/e2e/landing-samples.spec.ts
```

Append `## §10 UXR-T10` with the Snyk result and the e2e run's summary line.

---

### UXR-T11: The record

**Files:**
- Modify: `docs/README.md`, `docs/superpowers/NEXT.md`, `infra/README.md` §6

- [ ] **Step 1: `docs/README.md` rows** — under *Active*, add rows for `superpowers/specs/2026-09-08-unsung-redesign-scope.md` (ACTIVE, governing scope for `UXR-`), `superpowers/plans/2026-09-08-unsung-redesign.md` (executed — state which tasks ran), `superpowers/2026-09-08-unsung-redesign-execution-log.md` (RETAINED EXECUTION LOG), `../frontend/design/2026-09-08-unsung-redesign/README.md` (the visual source; spec governs), and `../builder/analysis/2026-09-08-lux-e6-tag-vocabulary/README.md` (FIGURES OWNER for `LUX-E6`; never restate its numbers). Mark `2026-09-03-launch-ux-scope.md`'s row: `LUX-E6` ran 2026-09-08, deferral of genres stands.

- [ ] **Step 2: `NEXT.md`** — one surgical paragraph in the top block (the `LBD-` worktree is live; no wholesale rewrite): `UXR-` is built on branch `unsung-redesign`, PR #N; the deploy is two images (frontend + API for `/api/meta`) and follows the owed `LUX-4` deploy; the mark PNG is his; the reach marker is dropped by his decision and recorded in the spec §4; `LUX-E6` is run and his to read.

- [ ] **Step 3: `infra/README.md` §6** — one sentence: the landing badge reads `GET /api/meta`, which exists only in API images built from commit ≥ `UXR-T4`; a frontend deployed ahead of it shows no badge, by design.

- [ ] **Step 4: Commit and open the draft PR**

```bash
git add docs/README.md docs/superpowers/NEXT.md infra/README.md
git commit -m "UXR-T11: the record — docs map, status, the deploy note" -- docs/README.md docs/superpowers/NEXT.md infra/README.md
git push
gh pr create --draft --title "UXR-: the Unsung.fm redesign" --body-file docs/superpowers/2026-09-08-unsung-redesign-execution-log.md
```

Then run `closeout`.

---

## Self-review

**Spec coverage.** `UXR-D1` → T2; D2 → T6/T7; D3 → T7; D4 → T7 step 2; D5 → T8 (explainer), T9 (RouteHistory); D6 → T3, T8; D7 → T3, T10; D8 → T4; D9 → T8; D10 → T5; D11 → T1; D12 → T3; D13 → T3; D14 → T3, T10; D15 → T6; D16 → T7; D17 → T1, T9; D18 → T2. Spec §6 (screenshots) → T1, T3, T7, T8, T9. Spec §7 (deploy shape) → T11. The dropped/deferred items in spec §4 have no task, by design.

**Placeholder scan.** Every code step carries code. Two steps say "adapt to the file's own helper" (T4 step 1 reads `test_health_reports_artifact_identity` first; T4 step 4 mirrors `client.test.ts`'s fetch mock) — both name the exact file and function to copy from.

**Type consistency.** `ArtistCard`'s props in T6 match the call in T7; `ArtistDetail`'s props in T7 match `JourneyList`'s call; `PlayerBar`'s props in T5 match `JourneyList`'s call in T5 step 5; `getMeta`'s return shape in T4 matches `ArtistCountBadge`'s use; `SAMPLE_JOURNEYS`/`TEASER` exports in T3 match `landing-samples.spec.ts` imports in T10.
