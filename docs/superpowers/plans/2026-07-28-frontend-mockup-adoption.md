# Frontend Mockup Adoption Implementation Plan

**Role: ACTIVE — partially executed.** Tasks 1–7 are complete, committed and pushed on
branch `frontend-mockup-adoption`; **Tasks 8–13 are outstanding.** Governed by
[`../specs/2026-07-28-frontend-mockup-adoption-design.md`](../specs/2026-07-28-frontend-mockup-adoption-design.md),
which wins where the two disagree. Progress is recorded in
[`../2026-07-28-frontend-mockup-adoption-execution-log.md`](../2026-07-28-frontend-mockup-adoption-execution-log.md).
This document does **not** state project status — that is [`../NEXT.md`](../NEXT.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt the committed Claude Design mockup as artistpath's interface across all five screens, adding the building-path loading screen and the bypass explainer the app does not have today.

**Architecture:** Extend the existing `@theme` token set in `frontend/src/index.css` and restyle components in place — the palette already matches, so this is type scale, spacing, states and five new structural pieces, not a re-skin. Four new frontend components (`PlayButton`, `PathSkeleton`, `RerollNotice`, `PathIntro`) and one new API route (`GET /api/artists/{mbid}`), which exists so a cold load from a shared link can name the two endpoint artists.

**Tech Stack:** React 19, TypeScript, Vite 8, Tailwind 4 (CSS-first `@theme`), Vitest + Testing Library, Playwright; FastAPI on the API side.

**Governing spec:** [`../specs/2026-07-28-frontend-mockup-adoption-design.md`](../specs/2026-07-28-frontend-mockup-adoption-design.md). Where this plan and the spec disagree, **the spec governs** — tell the owner rather than working around it.

**Branch:** `frontend-mockup-adoption`, already pushed. Commit per task.

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from the spec.

- **`UI-3` — field label text in markup stays exactly `From` and `To`, uppercased in CSS only.** `getByLabelText('From')` is an exact match. `text-transform` does not change `textContent`. Writing `FROM` breaks four test files.
- **`UI-4` — the journey stays an `<ol>` with one `<li>` per artist.** Three e2e specs index into `ol li`.
- **The bypass markup stays a single copy.** Playwright strict mode fails on two matching elements; mobile and desktop differ by responsive classes on one element.
- **`aria-label` values stay `Play` and `Pause`.** Nine tests resolve them by name.
- **The text `now playing` stays present.** Five unit tests assert it; `playback.spec.ts:54` matches it in `innerText`.
- **The accessible names `not for me`, `i know them`, `find path`, `new path`, `reset path`, `clear exclusions`, `start a journey` are unchanged.**
- **`UI-D3` — do NOT add `viewport-fit=cover` to `frontend/index.html`, and leave `env(safe-area-inset-bottom)` in `PlayerBar.tsx` exactly as it is.**
- **`UI-2` — do not implement the mockup's phone chrome** (52px status bar, `9:41` clock, 36px device radius) or `@keyframes ap-caret`. They are illustration.
- **Existing tests must pass unchanged at every task.** That is the check that the restyle did not move a hook.
- **Every `uv` command is prefixed `UV_LINK_MODE=copy`.**
- **Colours are referenced as tokens** (`var(--color-note)`), never as raw hex, outside `index.css`.

**Copy is fixed by spec §7 and must be used verbatim.** The three reroll strings carry no trailing ellipsis — animated dots supply it.

---

### Task 1: Tokens, font and keyframes

**Files:**
- Modify: `frontend/package.json` (add dependency)
- Modify: `frontend/src/index.css:1-16`

**Interfaces:**
- Consumes: nothing.
- Produces: eight new CSS custom properties (`--color-label`, `--color-note`, `--color-placeholder`, `--color-endpoint`, `--color-border-hover`, `--color-inert`, `--color-inert-fg`, `--color-rail-mid`), `--font-sans`, and three keyframe animations (`ap-shimmer`, `ap-pulse`, `ap-grow`). Every later task uses these.

**This task has no unit test, deliberately.** A jsdom test asserting a CSS custom property exists would pass against unmodified source in every arrangement that matters — it is the vacuous-check pattern `e2e/responsive.spec.ts:4-7` and `test_frozen_script_aliases.py` exist to warn about. The gate is a passing build plus the existing suite still green.

- [ ] **Step 1: Install the font package**

```bash
cd frontend && npm install @fontsource-variable/dm-sans@^5.3.0
```

- [ ] **Step 2: Rewrite `frontend/src/index.css`**

```css
@import "tailwindcss";
@import "@fontsource-variable/dm-sans";

@theme {
  --font-sans: 'DM Sans Variable', system-ui, sans-serif;

  /* Existing eight — the mockup uses these exact values. Do not change. */
  --color-bg: #0f1115;
  --color-surface: #181a1f;
  --color-border: #2a2d34;
  --color-text: #e7e9ee;
  --color-muted: #9aa0ab;
  --color-accent: #4a90d9;
  --color-away: #e8a0a0;
  --color-dig: #a0d9b4;

  /* Added 2026-07-28 for the mockup. Named by role, not by shade. */
  --color-label: #6f7580;          /* uppercase field labels, landing footer */
  --color-note: #7d838e;           /* dropdown disambiguation, card eyebrows */
  --color-placeholder: #5c626d;
  --color-endpoint: #3b4048;       /* endpoint card border */
  --color-border-hover: #343841;
  --color-inert: #20232a;          /* disabled play button, skeleton base */
  --color-inert-fg: #3c414a;       /* disabled play glyph */
  --color-rail-mid: #7bb0cf;       /* the rail gradient's middle stop */
}

:root { color-scheme: dark; }
body {
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
}
input { font-family: inherit; }
input::placeholder { color: var(--color-placeholder); }

/* From the mockup. `ap-caret` is deliberately NOT ported: it fakes a text
   cursor the mockup needs because it has no real <input>. */
@keyframes ap-shimmer {
  0%   { background-position: -260px 0; }
  100% { background-position: 260px 0; }
}
@keyframes ap-pulse {
  0%, 100% { opacity: .5; }
  50%      { opacity: 1; }
}
@keyframes ap-grow {
  0%   { transform: scaleY(.12); }
  100% { transform: scaleY(1); }
}
```

- [ ] **Step 3: Verify the build and the existing suite**

Run: `cd frontend && npm run build && npm test`
Expected: build succeeds; all existing tests pass. If any test fails here, stop — nothing in this task can legitimately break one.

- [ ] **Step 4: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/index.css
git commit -m "UI-1: design tokens, self-hosted DM Sans, and the mockup's keyframes"
```

---

### Task 2: `GET /api/artists/{mbid}`

**Files:**
- Modify: `api/src/artistpath_api/app.py` (insert between `search_artists` at :113 and `build_path` at :117)
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: `artist_out(node)` (`app.py:104`), `ArtistOut` (`models.py:46`), `store.id_by_mbid`.
- Produces: `GET /api/artists/{mbid}` → `ArtistOut` JSON `{mbid, name, disambiguation, popularity}`, or 404. Task 3 consumes this.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests/test_app.py`:

```python
def test_artist_lookup_returns_the_artist():
    client, store = _client()
    r = client.get(f"/api/artists/{store.mbids[0]}")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Radiohead"
    assert body["mbid"] == store.mbids[0]


def test_artist_lookup_404s_on_an_unknown_mbid():
    client, _ = _client()
    assert client.get("/api/artists/not-a-real-mbid").status_code == 404


# REGRESSION GUARD, not a red-first test: this passes before the change too.
# It exists because FastAPI matches routes in declaration order, so registering
# {mbid} ahead of `search` would make it swallow the literal path and this is
# the only thing that would notice.
def test_artist_lookup_does_not_shadow_the_search_route():
    client, _ = _client()
    r = client.get("/api/artists/search", params={"q": "rad"})
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Radiohead"
```

- [ ] **Step 2: Run the tests to verify the first two fail**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q -k artist_lookup`
Expected: `test_artist_lookup_returns_the_artist` FAILS (404 — no such route), `test_artist_lookup_404s_on_an_unknown_mbid` may pass for the wrong reason, `test_artist_lookup_does_not_shadow_the_search_route` PASSES. That mix is expected and is why the third carries the comment above.

- [ ] **Step 3: Add the route**

In `api/src/artistpath_api/app.py`, immediately **after** the `search_artists` route (`:113-115`) and **before** `build_path`:

```python
    # Registered AFTER /api/artists/search deliberately: FastAPI matches in
    # declaration order, so the reverse makes {mbid} swallow the literal path.
    # A pure in-memory lookup — no network, no pathfinding, no clip resolution.
    # Exists so a cold load from a shared link can name the two endpoint
    # artists on the loading screen, where the URL carries only MBIDs.
    @app.get("/api/artists/{mbid}")
    def get_artist(mbid: str) -> ArtistOut:
        node = store.id_by_mbid.get(mbid)
        if node is None:
            raise HTTPException(404, "unknown artist")
        return artist_out(node)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: all pass, including the full pre-existing suite.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "UI-2: GET /api/artists/{mbid} so a cold load can name the endpoints"
```

---

### Task 3: `getArtist` client call and the `useEndpoints` hook

**Files:**
- Modify: `frontend/src/api/client.ts:46` (add a timeout entry) and append the new function
- Create: `frontend/src/hooks/useEndpoints.ts`
- Test: `frontend/src/hooks/useEndpoints.test.tsx`

**Interfaces:**
- Consumes: Task 2's route; `Artist` from `@/api/types`; `fetchWithTimeout`, `ApiError`, `BASE` from `client.ts`.
- Produces: `getArtist(mbid: string, signal?: AbortSignal): Promise<Artist>` and `useEndpoints(fromMbid?: string, toMbid?: string, skip?: boolean): { from: Artist | null; to: Artist | null }`. Task 12 consumes the hook.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/hooks/useEndpoints.test.tsx`:

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { useEndpoints } from './useEndpoints';

const artist = (mbid: string, name: string) => ({ mbid, name, disambiguation: '', popularity: 0 });
afterEach(() => vi.restoreAllMocks());

test('resolves both endpoint artists', async () => {
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) =>
    artist(mbid, mbid === 'a' ? 'Nirvana' : 'Cocteau Twins'),
  );
  const { result } = renderHook(() => useEndpoints('a', 'b'));
  await waitFor(() => expect(result.current.from?.name).toBe('Nirvana'));
  expect(result.current.to?.name).toBe('Cocteau Twins');
});

// UI-7: a decorative lookup must never be able to turn a working page into an
// error page. The path request is the real one.
test('a failed lookup yields nulls and never throws', async () => {
  vi.spyOn(client, 'getArtist').mockRejectedValue(new Error('boom'));
  const { result } = renderHook(() => useEndpoints('a', 'b'));
  await waitFor(() => expect(client.getArtist).toHaveBeenCalled());
  expect(result.current.from).toBeNull();
  expect(result.current.to).toBeNull();
});

test('skip prevents the request entirely', async () => {
  const spy = vi.spyOn(client, 'getArtist').mockResolvedValue(artist('a', 'Nirvana'));
  renderHook(() => useEndpoints('a', 'b', true));
  await new Promise((r) => setTimeout(r, 20));
  expect(spy).not.toHaveBeenCalled();
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- useEndpoints`
Expected: FAIL — `Failed to resolve import "./useEndpoints"`.

- [ ] **Step 3: Add `getArtist` to the client**

In `frontend/src/api/client.ts`, change the timeout constant at `:46`:

```ts
/** Chosen, not measured. Path is longest: Dijkstra at depth plus a cold instance. */
const TIMEOUT_MS = { search: 8_000, path: 20_000, track: 10_000, artist: 8_000 } as const;
```

Then append:

```ts
/**
 * One artist by MBID. In-memory on the server: no network, no pathfinding.
 *
 * Exists for the loading screen — a shared link carries only MBIDs, so without
 * this the two endpoint cards cannot be named until the path itself returns.
 */
export async function getArtist(mbid: string, signal?: AbortSignal): Promise<Artist> {
  const r = await fetchWithTimeout(
    `${BASE}/artists/${encodeURIComponent(mbid)}`, {}, TIMEOUT_MS.artist, signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  return (await r.json()) as Artist;
}
```

- [ ] **Step 4: Create the hook**

Create `frontend/src/hooks/useEndpoints.ts`:

```ts
import { useEffect, useState } from 'react';
import * as client from '@/api/client';
import type { Artist } from '@/api/types';

type Endpoints = { from: Artist | null; to: Artist | null };

/**
 * The two artists the URL names, for the loading screen.
 *
 * UI-7: every failure resolves to null and nothing propagates. `POST /api/path`
 * is the real request; a decorative lookup must not be able to turn a working
 * page into an error page. Pass `skip` once the path itself has supplied names.
 */
export function useEndpoints(fromMbid?: string, toMbid?: string, skip = false): Endpoints {
  const [state, setState] = useState<Endpoints>({ from: null, to: null });

  useEffect(() => {
    if (skip || !fromMbid || !toMbid) return;
    const controller = new AbortController();
    let active = true;
    Promise.all([
      client.getArtist(fromMbid, controller.signal).catch(() => null),
      client.getArtist(toMbid, controller.signal).catch(() => null),
    ]).then(([from, to]) => {
      if (active) setState({ from, to });
    });
    return () => {
      active = false;
      controller.abort();
    };
  }, [fromMbid, toMbid, skip]);

  return state;
}
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd frontend && npm test -- useEndpoints`
Expected: 3 passing.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/hooks/useEndpoints.ts frontend/src/hooks/useEndpoints.test.tsx
git commit -m "UI-3: getArtist client call and the useEndpoints hook"
```

---

### Task 4: `ArtistSearch` — input, focus ring and floating dropdown

**Files:**
- Modify: `frontend/src/components/ArtistSearch.tsx:63-118`
- Test: `frontend/src/components/ArtistSearch.test.tsx` (existing — must pass unchanged)

**Interfaces:**
- Consumes: Task 1's tokens.
- Produces: no new exports. The component's props and behaviour are unchanged.

**Read `UI-3` in Global Constraints before starting.** The label text is the trap in this task.

- [ ] **Step 1: Run the existing tests to establish the baseline**

Run: `cd frontend && npm test -- ArtistSearch`
Expected: all pass. Record the count; it must be identical at Step 4.

- [ ] **Step 2: Replace the `return` block**

In `frontend/src/components/ArtistSearch.tsx`, replace everything from `return (` to the closing `);` with:

```tsx
  return (
    <div className="relative">
      {/* UI-3: the text stays "From"/"To" and is uppercased in CSS.
          getByLabelText is an exact match and four test files depend on it. */}
      <label
        htmlFor={inputId}
        className="block mb-[9px] text-[11px] font-medium uppercase tracking-[.09em] text-[var(--color-label)]"
      >
        {label}
      </label>
      <input
        id={inputId}
        className="w-full h-[52px] sm:h-[54px] rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] px-4 sm:px-[18px] text-[19px] sm:text-[20px] tracking-[-.01em] outline-none transition-shadow hover:border-[var(--color-border-hover)] focus:border-[var(--color-accent)] focus:shadow-[0_0_0_3px_rgba(74,144,217,.14)]"
        placeholder="Search an artist"
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
        // Artist names are proper nouns the keyboard does not know — "Sigur Rós",
        // "MF DOOM", "!!!" — and iOS rewrites and auto-capitalises them mid-typing,
        // so the query sent was not the query typed and a present artist came back
        // empty.
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck={false}
      />
      {open && results.length > 0 && (
        <ul className="absolute z-10 left-0 right-0 top-[calc(100%+8px)] rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] p-1.5 shadow-[0_24px_48px_-12px_rgba(0,0,0,.75),0_2px_6px_rgba(0,0,0,.4)]">
          {results.map((a) => (
            <li key={a.mbid}>
              <button
                type="button"
                className="flex w-full items-baseline gap-[7px] rounded-lg px-3 py-3 text-left hover:bg-[var(--color-accent)]/10"
                onClick={() => choose(a)}
              >
                <span className="text-[15px] tracking-[-.005em] whitespace-nowrap">{a.name}</span>
                {a.disambiguation && (
                  <span className="text-[12.5px] text-[var(--color-note)] truncate">
                    — {a.disambiguation}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
      {status !== 'idle' && (
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          {status === 'empty' ? 'No artists found.' : 'Search is unavailable — try again.'}
        </p>
      )}
    </div>
  );
```

- [ ] **Step 3: Add the placeholder note**

The mockup's empty "To" box reads `Search an artist`. That is now a real `placeholder`, styled by the `input::placeholder` rule added in Task 1 — no extra class needed.

- [ ] **Step 4: Run the tests**

Run: `cd frontend && npm test -- ArtistSearch && npm test -- LandingPage`
Expected: identical pass count to Step 1, zero failures. **If `getByLabelText('From')` fails, the label text was changed — revert that part.**

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ArtistSearch.tsx
git commit -m "UI-4: search input, focus ring and floating dropdown"
```

---

### Task 5: `LandingPage` — heading, pill button and footer

**Files:**
- Modify: `frontend/src/routes/LandingPage.tsx:31-53`
- Test: `frontend/src/routes/LandingPage.test.tsx` (existing — must pass unchanged)

**Interfaces:**
- Consumes: Task 1's tokens, Task 4's `ArtistSearch`.
- Produces: nothing consumed elsewhere.

- [ ] **Step 1: Write the failing test for the footer line**

Append to `frontend/src/routes/LandingPage.test.tsx`:

```tsx
test('the landing page states how long each clip runs', () => {
  render(
    <MemoryRouter>
      <LandingPage />
    </MemoryRouter>,
  );
  expect(screen.getByText(/path length varies — 30 seconds each/i)).toBeInTheDocument();
});
```

If the existing file's imports differ, match them — `MemoryRouter` and `render`/`screen` are already imported there for the other tests.

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- LandingPage`
Expected: the new test FAILS ("unable to find an element with the text"); the rest pass.

- [ ] **Step 3: Replace the `return` block**

```tsx
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[520px] flex-col px-7 pt-11 pb-9 sm:pt-14">
      <h1 className="text-[27px] sm:text-[38px] font-medium tracking-[-.02em] sm:tracking-[-.025em] leading-[1.1] sm:leading-[1.05]">
        Artist Path
      </h1>
      <p className="mt-3 sm:mt-3.5 max-w-[290px] sm:max-w-[400px] text-[14.5px] sm:text-base leading-[1.5] text-[var(--color-muted)] text-pretty">
        Name two artists and hear a smooth path between them.
      </p>

      <div className="mt-11 sm:mt-10 flex flex-col gap-5">
        <ArtistSearch label="From" initial={seedA} onSelect={setFrom} />
        <ArtistSearch label="To" initial={seedB} onSelect={setTo} />
        {sameArtist && (
          <p className="text-sm text-[var(--color-away)]">Pick two different artists.</p>
        )}
        <button
          type="button"
          disabled={!ready}
          onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
          className="mt-1.5 h-[52px] sm:h-[54px] w-full rounded-full bg-[var(--color-accent)] text-[15.5px] sm:text-base font-semibold tracking-[.01em] text-[var(--color-bg)] transition-opacity enabled:hover:bg-[#5b9ce0] disabled:cursor-not-allowed disabled:opacity-30"
        >
          Find path
        </button>
      </div>

      {/* A miniature of the journey the app builds: your artist, someone in
          between, their artist. Decorative — the three dots carry the same
          colours as the two bypass signals and the rail. */}
      <div className="mt-auto flex flex-col items-center gap-3.5 pt-10">
        <div className="flex items-center gap-2" aria-hidden>
          <span className="block size-[5px] rounded-full bg-[var(--color-away)]" />
          <span className="block h-px w-[22px] bg-[var(--color-border)]" />
          <span className="block size-[5px] rounded-full bg-[var(--color-muted)]" />
          <span className="block h-px w-[22px] bg-[var(--color-border)]" />
          <span className="block size-[5px] rounded-full bg-[var(--color-dig)]" />
        </div>
        <p className="text-[11.5px] tracking-[.02em] text-[var(--color-label)]">
          Path length varies — 30 seconds each
        </p>
      </div>
    </main>
  );
```

- [ ] **Step 4: Run the tests**

Run: `cd frontend && npm test -- LandingPage`
Expected: all pass including the new one.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/LandingPage.tsx frontend/src/routes/LandingPage.test.tsx
git commit -m "UI-5: landing screen type scale, pill button and clip-length footer"
```

---

### Task 6: `PlayButton`

**Files:**
- Create: `frontend/src/components/PlayButton.tsx`
- Test: `frontend/src/components/PlayButton.test.tsx`

**Interfaces:**
- Consumes: Task 1's tokens.
- Produces: `<PlayButton state={'play' | 'pause'} size={'card' | 'bar'} disabled?: boolean onClick: () => void />`. Tasks 7 and 8 consume it.

The mockup draws play and pause as CSS shapes, not text glyphs. The current `▶`/`❚❚` characters are replaced.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/PlayButton.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { PlayButton } from './PlayButton';

test('is labelled Play when it will start playback', () => {
  render(<PlayButton state="play" size="card" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Play' })).toBeInTheDocument();
});

test('is labelled Pause when it will stop playback', () => {
  render(<PlayButton state="pause" size="card" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Pause' })).toBeInTheDocument();
});

test('does not fire when disabled', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<PlayButton state="play" size="card" disabled onClick={onClick} />);
  const button = screen.getByRole('button', { name: 'Play' });
  expect(button).toBeDisabled();
  await user.click(button);
  expect(onClick).not.toHaveBeenCalled();
});

test('fires when enabled', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<PlayButton state="play" size="card" onClick={onClick} />);
  await user.click(screen.getByRole('button', { name: 'Play' }));
  expect(onClick).toHaveBeenCalled();
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- PlayButton`
Expected: FAIL — module not found.

- [ ] **Step 3: Create the component**

Create `frontend/src/components/PlayButton.tsx`:

```tsx
interface Props {
  /** What pressing it will do — not what the player is currently doing. */
  state: 'play' | 'pause';
  /** 40px on a card, 36px on the bottom bar. */
  size: 'card' | 'bar';
  disabled?: boolean;
  onClick: () => void;
}

/**
 * The mockup draws both glyphs as CSS shapes rather than text characters, which
 * is what makes them optically centred at every size. Extracted because it
 * appears at two sizes with a disabled variant in four places.
 *
 * The aria-label is `Play`/`Pause` exactly: nine tests resolve this by name.
 */
export function PlayButton({ state, size, disabled, onClick }: Props) {
  const box = size === 'card' ? 'w-10 h-10' : 'w-9 h-9';
  const bar = size === 'card' ? 'w-[3.5px] h-3.5' : 'w-[3px] h-3';
  return (
    <button
      type="button"
      aria-label={state === 'pause' ? 'Pause' : 'Play'}
      disabled={disabled}
      onClick={onClick}
      className={`${box} flex-none rounded-full flex items-center justify-center gap-[3.5px] ${
        disabled
          ? 'bg-[var(--color-inert)] border border-[var(--color-border)] cursor-default'
          : 'bg-[var(--color-accent)] hover:bg-[#5b9ce0]'
      }`}
    >
      {state === 'pause' ? (
        <>
          <span className={`${bar} block rounded-[1px] bg-white`} />
          <span className={`${bar} block rounded-[1px] bg-white`} />
        </>
      ) : (
        <span
          className="block w-0 h-0 ml-[3px] border-y-[6.5px] border-y-transparent border-l-[11px]"
          style={{ borderLeftColor: disabled ? 'var(--color-inert-fg)' : '#fff' }}
        />
      )}
    </button>
  );
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd frontend && npm test -- PlayButton`
Expected: 4 passing.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PlayButton.tsx frontend/src/components/PlayButton.test.tsx
git commit -m "UI-6: PlayButton with the mockup's CSS play and pause glyphs"
```

---

### Task 7: `ArtistCard` — endpoint, now-playing and no-preview variants

**Files:**
- Modify: `frontend/src/components/ArtistCard.tsx`
- Modify: `frontend/e2e/responsive.spec.ts:38`
- Test: `frontend/src/components/ArtistCard.test.tsx` (existing, plus new cases)

**Interfaces:**
- Consumes: Task 6's `PlayButton`; `useClip` from `@/hooks/useClip`.
- Produces: `ArtistCard` gains one optional prop, `endpointLabel?: 'start' | 'destination'`. Task 8 passes it. All existing props are unchanged.

This is the largest task. Read `UI-4`, `UI-5` and the single-copy bypass constraint before starting.

- [ ] **Step 1: Write the failing tests**

Append to `frontend/src/components/ArtistCard.test.tsx`:

```tsx
test('an endpoint card carries its eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(
    <ArtistCard
      artist={artist('start')} isEndpoint endpointLabel="start" isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText('Starting artist')).toBeInTheDocument();
});

test('a destination card carries the other eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(
    <ArtistCard
      artist={artist('dest')} isEndpoint endpointLabel="destination" isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText('Destination artist')).toBeInTheDocument();
});

// UI-5: the e2e responsive spec used to find this by the Tailwind class
// `.font-semibold`, which this task moves. A test hook must not be a style hook.
test('the artist name carries a stable test hook', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<ArtistCard artist={artist('hook')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(screen.getByTestId('artist-name')).toHaveTextContent('Miles Davis');
});
```

- [ ] **Step 2: Run to verify the three fail**

Run: `cd frontend && npm test -- ArtistCard`
Expected: the three new tests FAIL; the six existing tests PASS.

- [ ] **Step 3: Rewrite `ArtistCard.tsx`**

```tsx
import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import { PlayButton } from './PlayButton';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  /** One of the two artists you chose. Neither bypass signal applies to them. */
  isEndpoint?: boolean;
  /** Which end, when this is an endpoint. Drives the eyebrow label. */
  endpointLabel?: 'start' | 'destination';
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  onBypass: (mbid: string, reason: BypassReason) => void;
  /**
   * Reports whether this artist has a clip at all — never its URL. The URL is
   * signed and short-lived, so the player asks for one at the moment of play (C2).
   */
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
}

const BYPASS =
  'flex-1 sm:flex-none h-[34px] sm:h-8 px-3.5 rounded-full border text-[12.5px] flex items-center justify-center whitespace-nowrap transition-colors';

export function ArtistCard({
  artist, isPlaying, isCurrent, isEndpoint, endpointLabel,
  onPlay, onToggle, onBypass, onClipResolved,
}: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';
  const silent = clip.status === 'none';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, playable);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  return (
    <div
      className={`rounded-xl border px-3.5 py-3.5 sm:px-4 ${
        isPlaying
          ? 'bg-[var(--color-accent)]/[.13] border-[var(--color-accent)]/[.34]'
          : isEndpoint
            ? 'bg-[var(--color-surface)] border-[var(--color-endpoint)] shadow-[inset_0_1px_0_rgba(231,233,238,.05)]'
            : 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-border-hover)]'
      }`}
    >
      {endpointLabel && (
        <div className="mb-2.5 text-[9.5px] font-semibold uppercase tracking-[.14em] text-[var(--color-note)]">
          {endpointLabel === 'start' ? 'Starting artist' : 'Destination artist'}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-0 sm:gap-x-3.5">
        <div
          className={`flex-none rounded-[9px] bg-[var(--color-border)] bg-cover ${
            isEndpoint ? 'w-14 h-14' : 'w-13 h-13'
          } ${silent ? 'opacity-75' : ''}`}
          style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
          aria-hidden
        />
        <div className="flex-1 min-w-0">
          {/* UI-5: data-testid, not a style class — e2e/responsive.spec.ts
              measures this element and must not depend on its typography. */}
          <div
            data-testid="artist-name"
            className="font-semibold text-base sm:text-[16.5px] tracking-[-.01em] truncate"
          >
            {artist.name}
          </div>
          <div
            className={`mt-1 text-[12.5px] truncate ${
              silent ? 'text-[var(--color-label)]' : 'text-[var(--color-muted)]'
            }`}
          >
            {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
          </div>
          {isPlaying && (
            <div className="mt-1.5 text-[10.5px] font-medium uppercase tracking-[.1em] text-[var(--color-accent)]">
              ▮▮▮ now playing
            </div>
          )}
        </div>
        {!isEndpoint && (
          // On a phone this wrapper is full width and ordered last, so it takes a
          // row of its own beneath the artist and the two signals stay labelled.
          // From sm up it collapses back to an ordinary inline pair and the desktop
          // row is exactly what it was. One copy of the markup, deliberately: the
          // e2e specs resolve these by role and Playwright strict mode fails on two.
          <div className="order-last w-full mt-3 flex gap-2 sm:order-none sm:w-auto sm:mt-0">
            <button
              type="button"
              onClick={() => onBypass(artist.mbid, 'dislike')}
              className={`${BYPASS} border-[var(--color-away)]/[.38] text-[var(--color-away)] hover:bg-[var(--color-away)]/10 hover:border-[var(--color-away)]/60`}
            >
              ✕ Not for me
            </button>
            <button
              type="button"
              onClick={() => onBypass(artist.mbid, 'known')}
              className={`${BYPASS} border-[var(--color-dig)]/[.38] text-[var(--color-dig)] hover:bg-[var(--color-dig)]/10 hover:border-[var(--color-dig)]/60`}
            >
              ✓ I know them
            </button>
          </div>
        )}
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="card"
          disabled={!playable}
          // The card that owns the audio toggles it. Calling onPlay here would
          // re-seek to zero, which is why only the bottom bar could pause.
          onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        />
      </div>
    </div>
  );
}
```

Note `w-13 h-13` is not a default Tailwind size. Use `w-[52px] h-[52px]` instead — replace both occurrences on that line.

- [ ] **Step 4: Fix the e2e locator**

In `frontend/e2e/responsive.spec.ts`, replace line 38:

```ts
  const box = await interior.getByTestId('artist-name').first().boundingBox();
```

- [ ] **Step 5: Run the tests**

Run: `cd frontend && npm test -- ArtistCard && npm test`
Expected: nine ArtistCard tests pass; the whole unit suite passes.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ArtistCard.tsx frontend/src/components/ArtistCard.test.tsx frontend/e2e/responsive.spec.ts
git commit -m "UI-7: card variants, and a test hook that is not a style class"
```

---

> ## ⏸ HANDOFF SEAM — retire the session here
>
> **Everything above is a committed artifact, not a live understanding.** The
> landing screen is done, the API route is done, and the card layer is done.
> Nothing after this point depends on anything held only in a session's head.
>
> Per `CLAUDE.md`'s handoff rule, this is the planned seam: run `closeout`, write
> the handoff note, and start Tasks 8–13 in a fresh session. A boundary you
> planned is cheap; one discovered at Task 12 is not.
>
> **Retire earlier than this if the degradation tell fires** — being asked for
> figures already computed, an item dropping out of a tracking document, or a firm
> claim revised under mild questioning with no new information. That is a
> mid-flight closeout (`closeout` A2-mid, D1-mid), not a resolution to be careful.

---

### Task 8: `JourneyList` rail and endpoint labels

**Files:**
- Modify: `frontend/src/components/JourneyList.tsx:47-80`
- Modify: `frontend/src/components/PlayerBar.tsx`
- Test: `frontend/src/components/JourneyList.test.tsx` (existing — must pass unchanged)

**Interfaces:**
- Consumes: Task 7's `endpointLabel` prop, Task 6's `PlayButton`.
- Produces: nothing new.

- [ ] **Step 1: Run the existing tests for a baseline**

Run: `cd frontend && npm test -- JourneyList`
Expected: all pass. Record the count.

- [ ] **Step 2: Replace the `<ol>` in `JourneyList.tsx`**

`UI-4`: the `<ol>`/`<li>` structure is unchanged. Only classes and the new prop change.

```tsx
      <ol className="relative flex flex-col gap-3.5 pl-[19px]">
        <span className="absolute left-0 top-1.5 bottom-4 w-[3px] rounded-full bg-gradient-to-b from-[var(--color-accent)] via-[var(--color-rail-mid)] to-[var(--color-dig)]" />
        <span className="absolute left-[-2px] bottom-0 text-[10px] leading-none text-[var(--color-dig)]" aria-hidden>
          ▾
        </span>
        {artists.map((artist, i) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              isCurrent={player.currentMbid === artist.mbid}
              // The two artists you chose are the journey's endpoints; there is
              // nothing to reroute if you reject them.
              isEndpoint={i === 0 || i === artists.length - 1}
              endpointLabel={
                i === 0 ? 'start' : i === artists.length - 1 ? 'destination' : undefined
              }
              onPlay={player.playFrom}
              onToggle={player.toggle}
              onBypass={onBypass}
              onClipResolved={(mbid, available) =>
                setHasClip((prev) => ({ ...prev, [mbid]: available }))
              }
            />
            {/* Some pairs cannot be given a stop: one of the two holds a single
                connection in the graph, and it is to the other. Saying so beats
                a page with two cards and nothing to press. */}
            {stopRule === 'adjacent_only' && i === 0 && (
              <p className="px-1 py-3 text-sm text-[var(--color-muted)]">
                These two are next to each other — there&rsquo;s no artist in between.
              </p>
            )}
          </li>
        ))}
      </ol>
```

The `via-` gradient stop is what the mockup's three-colour rail needs; a two-stop gradient is what exists today.

- [ ] **Step 3: Rewrite `PlayerBar.tsx`**

`UI-D3`: `env(safe-area-inset-bottom)` stays exactly as written. Do not add `viewport-fit=cover`.

```tsx
import { PlayButton } from './PlayButton';

interface Props {
  currentName: string | null;
  isPlaying: boolean;
  onToggle: () => void;
}

export function PlayerBar({ currentName, isPlaying, onToggle }: Props) {
  if (!currentName) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 border-t border-[var(--color-border)] bg-[var(--color-surface)] px-5 pt-3.5 pb-[calc(1.875rem+env(safe-area-inset-bottom))]">
      <div className="mx-auto flex w-full max-w-[620px] items-center gap-3.5">
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="bar"
          onClick={onToggle}
        />
        <span className="min-w-0 truncate text-[13px] sm:text-[13.5px] text-[var(--color-muted)]">
          {currentName}
        </span>
      </div>
    </div>
  );
}
```

The `1.875rem` is the mockup's 30px. `env(safe-area-inset-bottom)` resolves to 0 everywhere today and is left in place unchanged — see `UI-D3`.

- [ ] **Step 4: Run the tests**

Run: `cd frontend && npm test`
Expected: identical pass count to Step 1 across the whole suite, zero failures.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/JourneyList.tsx frontend/src/components/PlayerBar.tsx
git commit -m "UI-8: three-stop rail, endpoint labels and the player bar"
```

---

### Task 9: `PathSkeleton`

**Files:**
- Create: `frontend/src/components/PathSkeleton.tsx`
- Test: `frontend/src/components/PathSkeleton.test.tsx`

**Interfaces:**
- Consumes: Task 1's `ap-shimmer`, `ap-pulse` and `ap-grow` keyframes; `Artist` from `@/api/types`.
- Produces: `<PathSkeleton from={Artist | null} to={Artist | null} />`. Task 12 consumes it.

Display-only: no play buttons and no bypass buttons, matching the mockup.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/PathSkeleton.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { PathSkeleton } from './PathSkeleton';

const artist = (name: string) => ({ mbid: name, name, disambiguation: '', popularity: 0 });

test('names both endpoints when they are known', () => {
  render(<PathSkeleton from={artist('Nirvana')} to={artist('Cocteau Twins')} />);
  expect(screen.getByText('Nirvana')).toBeInTheDocument();
  expect(screen.getByText('Cocteau Twins')).toBeInTheDocument();
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
});

// UI-7: the lookup is decorative and may fail. The screen must still render.
test('degrades without endpoint names', () => {
  render(<PathSkeleton from={null} to={null} />);
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
  expect(screen.getByText(/this usually takes a few seconds/i)).toBeInTheDocument();
});

test('offers nothing to press', () => {
  render(<PathSkeleton from={artist('Nirvana')} to={artist('Cocteau Twins')} />);
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- PathSkeleton`
Expected: FAIL — module not found.

- [ ] **Step 3: Create the component**

```tsx
import type { Artist } from '@/api/types';

interface Props {
  from: Artist | null;
  to: Artist | null;
}

const SHIMMER =
  'bg-[linear-gradient(90deg,var(--color-inert)_0%,#282c34_40%,var(--color-inert)_80%)] bg-[length:260px_100%] [animation:ap-shimmer_1.6s_linear_infinite]';

/** Four rows of decreasing opacity, as the mockup draws them. */
const ROWS = [
  { w1: '62%', w2: '44%', opacity: 1 },
  { w1: '48%', w2: '56%', opacity: 0.82 },
  { w1: '70%', w2: '38%', opacity: 0.62 },
  { w1: '54%', w2: '48%', opacity: 0.42 },
];

function EndpointCard({ artist }: { artist: Artist | null }) {
  return (
    <div className="flex items-center gap-3.5 rounded-xl border border-[var(--color-endpoint)] bg-[var(--color-surface)] px-3.5 py-4">
      <div className="w-14 h-14 flex-none rounded-[9px] bg-[var(--color-border)]" aria-hidden />
      <div className="min-w-0 flex-1">
        {artist ? (
          <div className="truncate text-base font-semibold tracking-[-.01em]">{artist.name}</div>
        ) : (
          <div className={`h-3 w-[58%] rounded-full ${SHIMMER}`} aria-hidden />
        )}
      </div>
    </div>
  );
}

/**
 * The building-path screen. Shown only when there is nothing on screen yet —
 * a first load or a shared link. A bypass press holds the old path instead
 * (UI-D4), which is `RerollNotice`.
 *
 * Both endpoints come from `useEndpoints`, which may legitimately return nulls
 * (UI-7); the cards shimmer in that case rather than the screen failing.
 */
export function PathSkeleton({ from, to }: Props) {
  return (
    <div className="flex min-h-[60vh] flex-col">
      {from && to && (
        <div className="text-[17px] font-medium tracking-[-.01em]">
          {from.name} <span className="font-normal text-[var(--color-label)]">→</span> {to.name}
        </div>
      )}
      <div
        className="mt-2 text-[13px] text-[var(--color-muted)] [animation:ap-pulse_1.8s_ease-in-out_infinite]"
        aria-live="polite"
      >
        Listening for the steps between them…
      </div>

      <div className="relative mt-7 flex flex-col gap-3.5 pl-[19px]">
        <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] origin-top rounded-full bg-gradient-to-b from-[var(--color-accent)] via-[var(--color-rail-mid)] to-[var(--color-dig)] [animation:ap-grow_2.4s_cubic-bezier(.32,.72,.28,1)_infinite]" />

        <EndpointCard artist={from} />

        {ROWS.map((row, i) => (
          <div
            key={i}
            className="flex items-center gap-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-3.5"
            style={{ opacity: row.opacity }}
            aria-hidden
          >
            <div className={`w-13 h-13 flex-none rounded-[9px] ${SHIMMER}`} />
            <div className="flex min-w-0 flex-1 flex-col gap-2">
              <div className={`h-3 rounded-full ${SHIMMER}`} style={{ width: row.w1 }} />
              <div className="h-[9px] rounded-full bg-[#1d2027]" style={{ width: row.w2 }} />
            </div>
            <div className="w-10 h-10 flex-none rounded-full bg-[var(--color-inert)]" />
          </div>
        ))}

        <div className="px-0 py-1 text-base tracking-[.35em] text-[var(--color-inert-fg)]" aria-hidden>
          ···
        </div>

        <EndpointCard artist={to} />
      </div>

      <p className="mt-auto pt-8 text-center text-[11.5px] tracking-[.02em] text-[var(--color-label)]">
        This usually takes a few seconds
      </p>
    </div>
  );
}
```

As in Task 7, `w-13 h-13` is not a default Tailwind size — use `w-[52px] h-[52px]`.

- [ ] **Step 4: Run to verify it passes**

Run: `cd frontend && npm test -- PathSkeleton`
Expected: 3 passing.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PathSkeleton.tsx frontend/src/components/PathSkeleton.test.tsx
git commit -m "UI-9: the building-path skeleton screen"
```

---

### Task 10: `RerollNotice`

**Files:**
- Create: `frontend/src/components/RerollNotice.tsx`
- Test: `frontend/src/components/RerollNotice.test.tsx`

**Interfaces:**
- Consumes: `BypassReason` from `@/api/types`.
- Produces: `type RerollReason = BypassReason | 'reset'` and `<RerollNotice reason={RerollReason} />`. Task 12 consumes both.

Copy is fixed by spec §7 and carries **no** trailing ellipsis — the animated dots supply it.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/RerollNotice.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { RerollNotice } from './RerollNotice';

test('names what the dislike signal does', () => {
  render(<RerollNotice reason="dislike" />);
  expect(screen.getByText(/steering around that sound/i)).toBeInTheDocument();
});

test('names what the known signal does', () => {
  render(<RerollNotice reason="known" />);
  expect(screen.getByText(/digging for someone newer/i)).toBeInTheDocument();
});

test('names what a reset does', () => {
  render(<RerollNotice reason="reset" />);
  expect(screen.getByText(/back to the original path/i)).toBeInTheDocument();
});

// The bypass buttons stay pressable underneath: they work today, and usePath
// aborts a superseded request safely.
test('does not intercept pointer events', () => {
  const { container } = render(<RerollNotice reason="dislike" />);
  expect(container.firstElementChild?.className).toContain('pointer-events-none');
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- RerollNotice`
Expected: FAIL — module not found.

- [ ] **Step 3: Create the component**

```tsx
import type { BypassReason } from '@/api/types';

export type RerollReason = BypassReason | 'reset';

/**
 * Fixed at design time (spec §7) so wording cannot be reshaped to fit an
 * implementation. No trailing ellipsis — the animated dots supply it.
 *
 * These are accurate to the router, not decorative: `dislike` applies a soft
 * penalty to the disliked artist's NEIGHBOURHOOD, decaying over `avoid_radius`
 * hops; `known` relaxes the obscurity floor more aggressively. If either
 * mechanism changes, these strings are wrong.
 */
const MESSAGE: Record<RerollReason, string> = {
  dislike: 'Steering around that sound',
  known: 'Digging for someone newer',
  reset: 'Back to the original path',
};

/**
 * Shown over the previous path while a reroll is in flight (UI-D4). The path
 * underneath stays legible at 60% opacity rather than being replaced, so a run
 * of bypass presses does not strobe.
 */
export function RerollNotice({ reason }: { reason: RerollReason }) {
  return (
    <div className="pointer-events-none absolute inset-0 z-10 flex items-start justify-center pt-24">
      <div
        role="status"
        aria-live="polite"
        className="flex items-center gap-2.5 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-3 text-[13px] text-[var(--color-text)] shadow-[0_24px_48px_-12px_rgba(0,0,0,.75)]"
      >
        {MESSAGE[reason]}
        <span className="flex items-center gap-1" aria-hidden>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="block size-1 rounded-full bg-[var(--color-accent)] [animation:ap-pulse_1.2s_ease-in-out_infinite]"
              style={{ animationDelay: `${i * 0.16}s` }}
            />
          ))}
        </span>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd frontend && npm test -- RerollNotice`
Expected: 4 passing.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/RerollNotice.tsx frontend/src/components/RerollNotice.test.tsx
git commit -m "UI-10: per-signal reroll notice over the held path"
```

---

### Task 11: `PathIntro`

**Files:**
- Create: `frontend/src/components/PathIntro.tsx`
- Test: `frontend/src/components/PathIntro.test.tsx`

**Interfaces:**
- Consumes: `StopRule` from `@/api/types`.
- Produces: `<PathIntro count={number} stopRule={StopRule} />`, where `count` is the number of artists **between** the two chosen ones. Task 12 consumes it.

`UI-D6`: the result line is permanent; the explainer is collapsible, open on a first visit, remembered as closed once dismissed. `UI-D7`: the count is artists in between, not hops.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/PathIntro.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, test } from 'vitest';
import { PathIntro } from './PathIntro';

beforeEach(() => localStorage.clear());

test('states the number of artists in between', () => {
  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.getByText(/in 3 steps/i)).toBeInTheDocument();
});

test('uses the singular for one', () => {
  render(<PathIntro count={1} stopRule="natural" />);
  expect(screen.getByText(/in 1 step\./i)).toBeInTheDocument();
});

// JourneyList already says the useful thing for this case, and there is no
// step count to state and no bypass buttons to explain.
test('stands down entirely when the two artists are adjacent', () => {
  render(<PathIntro count={0} stopRule="adjacent_only" />);
  expect(screen.queryByText(/we found a path/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/what do the two buttons do/i)).not.toBeInTheDocument();
});

test('the explainer is open on a first visit and says a press rebuilds everything', () => {
  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.getByText(/either one rebuilds the whole journey/i)).toBeInTheDocument();
});

test('dismissal persists across a remount', async () => {
  const user = userEvent.setup();
  const { unmount } = render(<PathIntro count={3} stopRule="natural" />);
  await user.click(screen.getByRole('button', { name: /got it/i }));
  expect(screen.queryByText(/either one rebuilds the whole journey/i)).not.toBeInTheDocument();
  unmount();

  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.queryByText(/either one rebuilds the whole journey/i)).not.toBeInTheDocument();
  // Still reachable — dismissed is not deleted.
  expect(screen.getByRole('button', { name: /what do the two buttons do/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd frontend && npm test -- PathIntro`
Expected: FAIL — module not found.

- [ ] **Step 3: Create the component**

```tsx
import { useState } from 'react';
import type { StopRule } from '@/api/types';

const DISMISSED_KEY = 'artistpath:bypass-explainer-dismissed';

function wasDismissed(): boolean {
  try {
    return localStorage.getItem(DISMISSED_KEY) === '1';
  } catch {
    // Private browsing and blocked storage both throw. Showing the explainer
    // is the safe failure — it is help text, not state.
    return false;
  }
}

interface Props {
  /** Artists BETWEEN the two chosen ones — what is visible on screen (UI-D7). */
  count: number;
  stopRule: StopRule;
}

/**
 * The result line and the bypass explainer.
 *
 * The result line is permanent; the explainer is onboarding, so it opens on a
 * first visit and stays closed once dismissed (UI-D6). Both stand down when the
 * two artists are adjacent: there is no count to state, no bypass buttons to
 * explain, and JourneyList already says the useful thing.
 */
export function PathIntro({ count, stopRule }: Props) {
  const [open, setOpen] = useState(() => !wasDismissed());

  if (stopRule === 'adjacent_only') return null;

  function dismiss() {
    setOpen(false);
    try {
      localStorage.setItem(DISMISSED_KEY, '1');
    } catch {
      // Nothing to do — the explainer simply reopens next time.
    }
  }

  return (
    <div className="mb-5">
      <p className="text-[13.5px] text-[var(--color-muted)]">
        We found a path between these artists in{' '}
        <span className="text-[var(--color-text)]">
          {count} step{count === 1 ? '' : 's'}
        </span>
        .
      </p>

      <button
        type="button"
        onClick={() => (open ? setOpen(false) : setOpen(true))}
        aria-expanded={open}
        className="mt-2 text-[12.5px] text-[var(--color-accent)] hover:underline"
      >
        {open ? '▾' : '▸'} What do the two buttons do?
      </button>

      {open && (
        <div className="mt-2.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-[12.5px] leading-[1.55] text-[var(--color-muted)]">
          <p>
            <span className="text-[var(--color-away)]">✕ Not for me</span> — steers away from
            that artist and the ones around them, so you get a different sound rather than a
            near-identical substitute.
          </p>
          <p className="mt-2">
            <span className="text-[var(--color-dig)]">✓ I know them</span> — digs for someone
            less familiar, since you&rsquo;ve already covered the obvious route.
          </p>
          <p className="mt-2 text-[var(--color-text)]">
            Either one rebuilds the whole journey, so every artist between your two can change —
            not just the one you pressed.
          </p>
          <button
            type="button"
            onClick={dismiss}
            className="mt-3.5 rounded-full border border-[var(--color-border)] px-4 py-1.5 text-[12.5px] text-[var(--color-text)] hover:border-[var(--color-border-hover)]"
          >
            Got it
          </button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd frontend && npm test -- PathIntro`
Expected: 5 passing.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PathIntro.tsx frontend/src/components/PathIntro.test.tsx
git commit -m "UI-11: result line and the collapsible bypass explainer"
```

---

### Task 12: Wire `PathPage`

**Files:**
- Modify: `frontend/src/routes/PathPage.tsx`
- Test: `frontend/src/routes/PathPage.test.tsx` (existing, plus new cases)

**Interfaces:**
- Consumes: `useEndpoints` (Task 3), `PathSkeleton` (Task 9), `RerollNotice` + `RerollReason` (Task 10), `PathIntro` (Task 11).
- Produces: the finished path screen.

This is the task that makes the previous four visible. Spec §8 owns the state table.

- [ ] **Step 1: Write the failing tests**

Append to `frontend/src/routes/PathPage.test.tsx`, matching the file's existing render helper and mocking style:

```tsx
test('a first load shows the skeleton, not the old text line', async () => {
  vi.spyOn(client, 'buildPath').mockImplementation(() => new Promise(() => {}));
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) => ({
    mbid, name: mbid === 'a' ? 'Nirvana' : 'Cocteau Twins', disambiguation: '', popularity: 0,
  }));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByText('Nirvana')).toBeInTheDocument());
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
  expect(screen.queryByText(/building your path/i)).not.toBeInTheDocument();
});

test('a bypass press holds the old path and names what it is doing', async () => {
  const user = userEvent.setup();
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getAllByTestId('artist-name').length).toBeGreaterThan(2));
  vi.spyOn(client, 'buildPath').mockImplementation(() => new Promise(() => {}));
  await user.click(screen.getAllByRole('button', { name: /not for me/i })[0]);
  await waitFor(() => expect(screen.getByText(/steering around that sound/i)).toBeInTheDocument());
  // The path is held, not replaced.
  expect(screen.getAllByTestId('artist-name').length).toBeGreaterThan(2);
});

test('the result line counts the artists in between', async () => {
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByText(/we found a path/i)).toBeInTheDocument());
});
```

`renderAt` is the existing helper in that file; reuse it rather than writing a new one. If the mocked path returns five artists, the result line reads `3 steps`.

- [ ] **Step 2: Run to verify they fail**

Run: `cd frontend && npm test -- PathPage`
Expected: the three new tests FAIL; the existing eight PASS.

- [ ] **Step 3: Rewrite `PathPage.tsx`**

```tsx
import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { useEndpoints } from '@/hooks/useEndpoints';
import { JourneyList, type JourneyControls } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { PathSkeleton } from '@/components/PathSkeleton';
import { PathIntro } from '@/components/PathIntro';
import { RerollNotice, type RerollReason } from '@/components/RerollNotice';
import { addExclusion, clearExclusions, decodeExclusions } from '@/lib/exclusions';
import type { BypassReason } from '@/api/types';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();
  const journey = useRef<JourneyControls>(null);

  // Which control started the rebuild currently in flight. Drives the message
  // over the held path; cleared the moment a path lands.
  const [reason, setReason] = useState<RerollReason | null>(null);
  useEffect(() => {
    if (state.status !== 'loading') setReason(null);
  }, [state.status]);

  // Only needed while there is nothing on screen to name the endpoints.
  const endpoints = useEndpoints(from, to, state.artists.length > 0);

  // Every control that leaves or rebuilds the path silences the audio on the press
  // itself. Leaving it to the rebuild meant a clip carried on over a darkened page
  // until the new path arrived, which reads as the button not having worked.
  function go(next: URLSearchParams, why: RerollReason) {
    journey.current?.stop();
    setReason(why);
    const qs = next.toString();
    navigate(`/path/${from}/${to}${qs ? `?${qs}` : ''}`);
  }

  function handleBypass(mbid: string, why: BypassReason) {
    go(addExclusion(params, mbid, why), why);
  }

  const hasBypasses = decodeExclusions(params).length > 0;

  // The names come from the path itself; the ids from the URL, so the link
  // still works while the first path is loading or has failed.
  const newPathParams = new URLSearchParams();
  if (from) newPathParams.set('from', from);
  if (to) newPathParams.set('to', to);
  if (state.artists.length > 1) {
    newPathParams.set('fromName', state.artists[0].name);
    newPathParams.set('toName', state.artists[state.artists.length - 1].name);
  }

  const rebuilding = state.status === 'loading' && state.artists.length > 0;

  return (
    <main className="mx-auto w-full max-w-[620px] px-5 py-6 pb-40 sm:py-9">
      <div className="mb-6 flex items-center gap-5 text-[13px] sm:text-[13.5px]">
        {/* Without this the path page is a dead end: every route back to
            picking two artists was the browser's Back button. The pair
            travels along so the boxes arrive filled in. */}
        <Link
          to={`/?${newPathParams.toString()}`}
          onClick={() => journey.current?.stop()}
          className="text-[var(--color-muted)] hover:text-[var(--color-text)]"
        >
          ← New path
        </Link>
        {/* Only offered once there is something to undo. */}
        {hasBypasses && (
          <button
            type="button"
            onClick={() => go(clearExclusions(params), 'reset')}
            className="text-[var(--color-muted)] hover:text-[var(--color-text)]"
          >
            ↺ Reset path
          </button>
        )}
      </div>

      {state.status === 'error' && state.error ? (
        <PathStatus
          error={state.error}
          onClearExclusions={() => go(clearExclusions(params), 'reset')}
          onRetry={state.retry}
        />
      ) : state.artists.length === 0 ? (
        <PathSkeleton from={endpoints.from} to={endpoints.to} />
      ) : (
        <div className="relative">
          <PathIntro count={state.artists.length - 2} stopRule={state.stopRule} />
          <div className={rebuilding ? 'opacity-60 transition-opacity' : ''}>
            <JourneyList
              ref={journey}
              artists={state.artists}
              stopRule={state.stopRule}
              onBypass={handleBypass}
            />
          </div>
          {rebuilding && reason && <RerollNotice reason={reason} />}
        </div>
      )}
    </main>
  );
}
```

- [ ] **Step 4: Run the whole unit suite**

Run: `cd frontend && npm test`
Expected: everything passes, existing and new.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/PathPage.tsx frontend/src/routes/PathPage.test.tsx
git commit -m "UI-12: wire the skeleton, the reroll notice and the path intro"
```

---

### Task 13: Full verification and the use-the-app queue entry

**Files:**
- Modify: `docs/superpowers/TEST-QUEUE.md` (new entry at the top)

**Interfaces:**
- Consumes: everything.
- Produces: a verified branch ready for a PR.

- [ ] **Step 1: Typecheck, lint and unit tests**

```bash
cd frontend && npm run lint && npm test && npm run build
cd ../api && UV_LINK_MODE=copy uv run --extra dev pytest -q
```
Expected: all green. **`npm run build` runs `tsc -b`, so a type error surfaces here and nowhere earlier.**

- [ ] **Step 2: Run the e2e suite against a live API**

Terminal 1:
```bash
cd api && UV_LINK_MODE=copy uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```
Terminal 2:
```bash
cd frontend && npm run test:e2e
```
Expected: all four specs pass. `responsive.spec.ts` is the one to watch — it exercises the `UI-5` locator change at a real 390px viewport, and jsdom cannot substitute for it.

- [ ] **Step 3: Look at all five screens**

```bash
cd frontend && npm run dev
```
Open `http://localhost:5173`. Check against `frontend/design/2026-07-28-mockup/thumbnail.png`:
landing at desktop width and at 390px; a first load (the skeleton); a bypass press (held path plus notice); the journey at both widths; and a reload of a `/path/…` URL, which is the shared-link case the API route exists for.

- [ ] **Step 4: Snyk scan**

Run the `snyk_code_scan` tool over the modified first-party code. Fix anything it reports using its results, then rescan until clean, per the standing instruction in `CLAUDE.md`.

- [ ] **Step 5: Queue the use-the-app test**

Add an entry at the top of `docs/superpowers/TEST-QUEUE.md`, following that file's conventions: newest first, `(latest)` on the live QUEUED entry only, written in plain language for the owner.

It must ask for: the landing screen on desktop and phone; **two or three familiar journeys, which must be unchanged** — no routing, graph or cost-function code was touched and that is the most valuable check; a bypass press, to see the held path and the new message; a reload of a path URL, which is the shared-link case; and the collapsible explainer, including that dismissing it sticks.

**It must also carry forward the iPhone script from the 2026-07-28 entry, which is still unrun** — whether a clip plays at all on an iPhone is still unanswered, and this work does not answer it.

- [ ] **Step 6: Commit and open the PR**

```bash
git add docs/superpowers/TEST-QUEUE.md
git commit -m "UI-13: queue the use-the-app check for the redesign"
git push
gh pr create --title "Adopt the Claude Design mockup as the app's interface" --body "..."
```

The PR body carries what `closeout` D5 requires: a link to the spec, what is closed and should not be re-litigated, and — importantly — the two deploy-time notes from spec §12. **The `--prune` deferral comes due on this work**, because this is the next frontend publish.

---

## Self-review

**Spec coverage.** §3 tokens → Task 1. §4 `PathSkeleton` → 9, `RerollNotice` → 10, `PlayButton` → 6, `PathIntro` → 11. §5 `ArtistSearch` → 4, `ArtistCard` → 7, `JourneyList`/`PlayerBar` → 8, `LandingPage` → 5, `PathPage` → 12. §6 API → 2 and 3. §7 copy → fixed in 5, 9, 10, 11. §8 state table → 12. §9 `UI-7` → 3 and 9. §10 constraints → Global Constraints plus `UI-5` in 7. §11 testing → every task, and 13. §12 deploy notes → 13 Step 6. **No gaps.**

**Two known imprecisions, flagged rather than hidden.** `w-13 h-13` is not a Tailwind default and is corrected in place in Tasks 7 and 9 — use `w-[52px] h-[52px]`. And Task 12's tests reuse `renderAt` and the mocking style already in `PathPage.test.tsx`; the implementer should read that file before writing them rather than assuming the helper's signature.

**Type consistency.** `Artist`, `StopRule`, `BypassReason` come from `@/api/types` throughout. `RerollReason` is defined once in Task 10 and imported in Task 12. `endpointLabel` is `'start' | 'destination'` in both Task 7 and Task 8. `PathIntro`'s `count` is artists-in-between in both its definition and its one call site (`state.artists.length - 2`).
