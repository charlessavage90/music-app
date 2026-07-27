# Stage 3a Web Frontend Implementation Plan

> **⚠ Role: HISTORICAL. EXECUTED and SHIPPED — do not execute again.** The frontend described
> here is live in `frontend/` and has since been reworked by Gate 2 Track D
> ([`../2026-07-26-gate2-track-d-execution-log.md`](../2026-07-26-gate2-track-d-execution-log.md)).
> Two details below have moved on: it targets React 18 (the code is on React 19) and the
> **5k dev graph, which is retired**. Where this plan and the code disagree, **the code wins**.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the React web frontend for the artist-path app — two autocomplete inputs, a vertical-journey of artist cards with clips and two bypass controls, sequential autoplay, reroll-as-new-path, and shareable URLs — running locally against the existing Python API on the 5k graph.

**Architecture:** A Vite + React + TypeScript SPA. The URL is the single source of truth (`/path/:from/:to?dislike=…&known=…`). A thin typed client wraps the three API endpoints. Path load is two-phase: `POST /api/path` renders artists instantly, then each card lazy-loads its clip. Playback sits behind a `Player` interface. Every bypass navigates to a new URL, producing a wholly new path (no in-place edit).

**Tech Stack:** React 18, Vite 6, TypeScript, Tailwind CSS v4 (Vite plugin), React Router v7, Vitest + React Testing Library + jsdom, Playwright.

**Reference docs the engineer should read first:**
- Spec: `docs/superpowers/specs/2026-07-20-stage3-web-frontend-design.md` (this plan implements it)
- Parent design: `docs/superpowers/specs/2026-07-19-artist-path-alpha-design.md` §3.3, §4.3, §5
- API contract: `api/README.md` (endpoint shapes, error codes)

## Global Constraints

- **Node** ≥ 20.17, **npm** ≥ 10.8 (verified locally).
- **API base URL** comes from `import.meta.env.VITE_API_BASE`, defaulting to `/api`. Never hard-code `http://localhost:8000` in app code — the Vite dev proxy maps `/api` → `:8000`.
- **The URL is the single source of truth.** The path and its two bypass lists live only in the route + query string. Playback state and resolved clips are the only non-URL client state.
- **Two bypass signals stay distinct**: `dislike` and `known` are separate query params, mapped to `reason: "dislike"` / `"known"` in the API request. Never merge them.
- **Reroll is a new path, never an edit**: no swap/slide/cross-fade animation, no diffing against the previous path, no preserving per-card scroll. Re-render from the new array keyed by MBID.
- **A missing clip (`204`) never blocks or reorders a card.** The card renders unplayable but present.
- **TDD**: write the failing test first, watch it fail, implement minimally, watch it pass, commit. Small commits.
- **API response fields are snake_case** (`preview_url`, `cover_url`); the client maps them to camelCase at the boundary so the rest of the app is camelCase.

---

### Task 1: Scaffold the frontend package and tooling

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/tsconfig.node.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`, `frontend/src/vite-env.d.ts`, `frontend/src/test/setup.ts`
- Create: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: a working dev server (`npm run dev`), test runner (`npm test`), Tailwind v4 pipeline, and a `<BrowserRouter>`-wrapped `<App/>`. Path alias `@/` → `frontend/src/`.

- [ ] **Step 1: Scaffold with Vite**

Run from repo root:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

- [ ] **Step 2: Add dependencies**

Run in `frontend/`:
```bash
npm install react-router-dom
npm install -D tailwindcss @tailwindcss/vite vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitest/coverage-v8
```

- [ ] **Step 3: Configure Vite (proxy, Tailwind, Vitest, alias)**

Overwrite `frontend/vite.config.ts`:
```typescript
/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
});
```

- [ ] **Step 4: Wire Tailwind v4 and design tokens**

Overwrite `frontend/src/index.css`:
```css
@import "tailwindcss";

@theme {
  --color-bg: #0f1115;
  --color-surface: #181a1f;
  --color-border: #2a2d34;
  --color-text: #e7e9ee;
  --color-muted: #9aa0ab;
  --color-accent: #4a90d9;
  --color-away: #e8a0a0;
  --color-dig: #a0d9b4;
}

:root { color-scheme: dark; }
body { background: var(--color-bg); color: var(--color-text); }
```

- [ ] **Step 5: Set up the test setup file and path alias in tsconfig**

Create `frontend/src/test/setup.ts`:
```typescript
import '@testing-library/jest-dom/vitest';
```

In `frontend/tsconfig.json`, add to `compilerOptions`:
```json
"baseUrl": ".",
"paths": { "@/*": ["./src/*"] }
```

- [ ] **Step 6: Minimal router-wrapped App**

Overwrite `frontend/src/App.tsx`:
```tsx
export default function App() {
  return <div data-testid="app-root">Artist Path</div>;
}
```

Overwrite `frontend/src/main.tsx`:
```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
```

- [ ] **Step 7: Add test/lint scripts to package.json**

In `frontend/package.json` `"scripts"`, ensure:
```json
"dev": "vite",
"build": "tsc -b && vite build",
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 8: Write the smoke test**

Create `frontend/src/App.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the app root', () => {
  render(<App />);
  expect(screen.getByTestId('app-root')).toBeInTheDocument();
});
```

- [ ] **Step 9: Run the smoke test — expect PASS**

Run: `npm test`
Expected: 1 passed. If jsdom/matcher errors appear, confirm Step 5 setup file is referenced in `vite.config.ts`.

- [ ] **Step 10: Verify dev server boots**

Run: `npm run dev` then Ctrl-C. Expected: Vite prints a local URL with no errors.

- [ ] **Step 11: Commit**

```bash
git add frontend
git commit -m "feat(web): scaffold React+Vite+TS frontend with Tailwind and Vitest"
```

---

### Task 2: API types and typed client

**Files:**
- Create: `frontend/src/api/types.ts`, `frontend/src/api/client.ts`
- Test: `frontend/src/api/client.test.ts`

**Interfaces:**
- Consumes: `VITE_API_BASE` env (default `/api`).
- Produces:
  - Types: `Artist { mbid, name, disambiguation, popularity }`, `Track { previewUrl, title, coverUrl }`, `BypassReason = 'dislike' | 'known'`, `Exclusion { id: string; reason: BypassReason }`.
  - `class ApiError extends Error { status: number }`.
  - `searchArtists(q: string, signal?: AbortSignal): Promise<Artist[]>`
  - `buildPath(sources: string[], exclude: Exclusion[], signal?: AbortSignal): Promise<Artist[]>`
  - `getTrack(mbid: string, signal?: AbortSignal): Promise<Track | null>` (`null` on 204).

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/api/client.test.ts`:
```typescript
import { afterEach, expect, test, vi } from 'vitest';
import { ApiError, buildPath, getTrack, searchArtists } from './client';

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response);
}

afterEach(() => vi.unstubAllGlobals());

test('searchArtists returns artists', async () => {
  vi.stubGlobal('fetch', mockFetch(200, [
    { mbid: 'a', name: 'Radiohead', disambiguation: '', popularity: 1.0 },
  ]));
  const out = await searchArtists('radio');
  expect(out[0].name).toBe('Radiohead');
});

test('buildPath unwraps the artists array and sends sources+exclude', async () => {
  const fetch = mockFetch(200, { artists: [{ mbid: 'x', name: 'A', disambiguation: '', popularity: 0.5 }] });
  vi.stubGlobal('fetch', fetch);
  const out = await buildPath(['a', 'b'], [{ id: 'z', reason: 'dislike' }]);
  expect(out).toHaveLength(1);
  const body = JSON.parse((fetch.mock.calls[0][1] as RequestInit).body as string);
  expect(body).toEqual({ sources: ['a', 'b'], exclude: [{ id: 'z', reason: 'dislike' }] });
});

test('getTrack maps snake_case to camelCase', async () => {
  vi.stubGlobal('fetch', mockFetch(200, { preview_url: 'u', title: 't', cover_url: 'c' }));
  const track = await getTrack('a');
  expect(track).toEqual({ previewUrl: 'u', title: 't', coverUrl: 'c' });
});

test('getTrack returns null on 204', async () => {
  vi.stubGlobal('fetch', mockFetch(204, null));
  expect(await getTrack('a')).toBeNull();
});

test('buildPath throws ApiError with status on 409', async () => {
  vi.stubGlobal('fetch', mockFetch(409, {}));
  await expect(buildPath(['a', 'b'], [])).rejects.toMatchObject({ status: 409 } as Partial<ApiError>);
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- client`
Expected: FAIL, `./client` has no exports.

- [ ] **Step 3: Write the types**

Create `frontend/src/api/types.ts`:
```typescript
export type BypassReason = 'dislike' | 'known';

export interface Artist {
  mbid: string;
  name: string;
  disambiguation: string;
  popularity: number;
}

export interface Track {
  previewUrl: string;
  title: string;
  coverUrl: string;
}

export interface Exclusion {
  id: string;
  reason: BypassReason;
}
```

- [ ] **Step 4: Write the client**

Create `frontend/src/api/client.ts`:
```typescript
import type { Artist, Exclusion, Track } from './types';

const BASE = import.meta.env.VITE_API_BASE ?? '/api';

export class ApiError extends Error {
  constructor(public status: number) {
    super(`API error ${status}`);
    this.name = 'ApiError';
  }
}

export async function searchArtists(q: string, signal?: AbortSignal): Promise<Artist[]> {
  const r = await fetch(`${BASE}/artists/search?q=${encodeURIComponent(q)}`, { signal });
  if (!r.ok) throw new ApiError(r.status);
  return (await r.json()) as Artist[];
}

export async function buildPath(
  sources: string[],
  exclude: Exclusion[],
  signal?: AbortSignal,
): Promise<Artist[]> {
  const r = await fetch(`${BASE}/path`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ sources, exclude }),
    signal,
  });
  if (!r.ok) throw new ApiError(r.status);
  const data = (await r.json()) as { artists: Artist[] };
  return data.artists;
}

export async function getTrack(mbid: string, signal?: AbortSignal): Promise<Track | null> {
  const r = await fetch(`${BASE}/artists/${encodeURIComponent(mbid)}/track`, { signal });
  if (r.status === 204) return null;
  if (!r.ok) throw new ApiError(r.status);
  const d = (await r.json()) as { preview_url: string; title: string; cover_url: string };
  return { previewUrl: d.preview_url, title: d.title, coverUrl: d.cover_url };
}
```

- [ ] **Step 5: Run tests — expect PASS**

Run: `npm test -- client`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api
git commit -m "feat(web): typed API client for search, path, track"
```

---

### Task 3: URL exclusion codec

**Files:**
- Create: `frontend/src/lib/exclusions.ts`
- Test: `frontend/src/lib/exclusions.test.ts`

**Interfaces:**
- Consumes: `Exclusion`, `BypassReason` from `@/api/types`.
- Produces:
  - `decodeExclusions(params: URLSearchParams): Exclusion[]` — reads `dislike` and `known` comma-lists into a flat exclusion array (dislikes first, then knowns).
  - `addExclusion(params: URLSearchParams, mbid: string, reason: BypassReason): URLSearchParams` — returns a NEW params object with `mbid` appended to the right list (deduped).
  - `clearExclusions(params: URLSearchParams): URLSearchParams` — returns a NEW params object with both lists removed.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/lib/exclusions.test.ts`:
```typescript
import { expect, test } from 'vitest';
import { addExclusion, clearExclusions, decodeExclusions } from './exclusions';

test('decodeExclusions reads both lists, dislikes first', () => {
  const params = new URLSearchParams('dislike=a,b&known=c');
  expect(decodeExclusions(params)).toEqual([
    { id: 'a', reason: 'dislike' },
    { id: 'b', reason: 'dislike' },
    { id: 'c', reason: 'known' },
  ]);
});

test('decodeExclusions returns [] when absent', () => {
  expect(decodeExclusions(new URLSearchParams())).toEqual([]);
});

test('addExclusion appends to the correct list and does not mutate input', () => {
  const input = new URLSearchParams('dislike=a');
  const out = addExclusion(input, 'b', 'dislike');
  expect(out.get('dislike')).toBe('a,b');
  expect(input.get('dislike')).toBe('a'); // unchanged
});

test('addExclusion is idempotent (no duplicates)', () => {
  const out = addExclusion(new URLSearchParams('known=c'), 'c', 'known');
  expect(out.get('known')).toBe('c');
});

test('addExclusion writes known separately from dislike', () => {
  const out = addExclusion(new URLSearchParams('dislike=a'), 'c', 'known');
  expect(out.get('dislike')).toBe('a');
  expect(out.get('known')).toBe('c');
});

test('clearExclusions strips both lists', () => {
  const out = clearExclusions(new URLSearchParams('dislike=a&known=c'));
  expect(out.has('dislike')).toBe(false);
  expect(out.has('known')).toBe(false);
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- exclusions`
Expected: FAIL, module not found.

- [ ] **Step 3: Implement**

Create `frontend/src/lib/exclusions.ts`:
```typescript
import type { BypassReason, Exclusion } from '@/api/types';

const KEY: Record<BypassReason, string> = { dislike: 'dislike', known: 'known' };

function list(params: URLSearchParams, reason: BypassReason): string[] {
  const raw = params.get(KEY[reason]);
  return raw ? raw.split(',').filter(Boolean) : [];
}

export function decodeExclusions(params: URLSearchParams): Exclusion[] {
  const out: Exclusion[] = [];
  for (const id of list(params, 'dislike')) out.push({ id, reason: 'dislike' });
  for (const id of list(params, 'known')) out.push({ id, reason: 'known' });
  return out;
}

export function addExclusion(
  params: URLSearchParams,
  mbid: string,
  reason: BypassReason,
): URLSearchParams {
  const next = new URLSearchParams(params);
  const ids = list(params, reason);
  if (!ids.includes(mbid)) ids.push(mbid);
  next.set(KEY[reason], ids.join(','));
  return next;
}

export function clearExclusions(params: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(params);
  next.delete('dislike');
  next.delete('known');
  return next;
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- exclusions`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib
git commit -m "feat(web): URL codec for the two bypass exclusion lists"
```

---

### Task 4: usePath hook

**Files:**
- Create: `frontend/src/hooks/usePath.ts`
- Test: `frontend/src/hooks/usePath.test.tsx`

**Interfaces:**
- Consumes: `buildPath`, `ApiError` from `@/api/client`; `decodeExclusions` from `@/lib/exclusions`; React Router `useParams`, `useSearchParams`.
- Produces: `usePath(): PathState` where
  `type PathState = { status: 'loading' | 'ready' | 'error'; artists: Artist[]; error?: 'notfound' | 'nopath' | 'unknown' }`.
  Maps API `404 → 'notfound'`, `409 → 'nopath'`, anything else → `'unknown'`. Reads `from`/`to` from route params and exclusions from the query string; refetches whenever any of them change; aborts the in-flight request on change.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/hooks/usePath.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { usePath } from './usePath';

function Harness() {
  const state = usePath();
  return <div data-testid="state">{state.status}:{state.error ?? ''}:{state.artists.map(a => a.name).join(',')}</div>;
}

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes><Route path="/path/:from/:to" element={<Harness />} /></Routes>
    </MemoryRouter>,
  );
}

afterEach(() => vi.restoreAllMocks());

test('resolves and exposes artists', async () => {
  vi.spyOn(client, 'buildPath').mockResolvedValue([
    { mbid: 'a', name: 'Miles', disambiguation: '', popularity: 1 },
  ]);
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('ready::Miles'));
});

test('passes decoded exclusions to buildPath', async () => {
  const spy = vi.spyOn(client, 'buildPath').mockResolvedValue([]);
  renderAt('/path/a/b?dislike=z&known=y');
  await waitFor(() => expect(spy).toHaveBeenCalledWith(
    ['a', 'b'],
    [{ id: 'z', reason: 'dislike' }, { id: 'y', reason: 'known' }],
    expect.any(AbortSignal),
  ));
});

test('maps 409 to nopath', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:nopath:'));
});

test('maps 404 to notfound', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(404));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:notfound:'));
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- usePath`
Expected: FAIL, `usePath` not found.

- [ ] **Step 3: Implement**

Create `frontend/src/hooks/usePath.ts`:
```typescript
import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { ApiError, buildPath } from '@/api/client';
import type { Artist } from '@/api/types';
import { decodeExclusions } from '@/lib/exclusions';

export interface PathState {
  status: 'loading' | 'ready' | 'error';
  artists: Artist[];
  error?: 'notfound' | 'nopath' | 'unknown';
}

function classify(err: unknown): PathState['error'] {
  if (err instanceof ApiError) {
    if (err.status === 404) return 'notfound';
    if (err.status === 409) return 'nopath';
  }
  return 'unknown';
}

export function usePath(): PathState {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const [state, setState] = useState<PathState>({ status: 'loading', artists: [] });

  const key = `${from}|${to}|${params.toString()}`;

  useEffect(() => {
    if (!from || !to) return;
    const controller = new AbortController();
    setState((prev) => ({ status: 'loading', artists: prev.artists }));
    buildPath([from, to], decodeExclusions(params), controller.signal)
      .then((artists) => setState({ status: 'ready', artists }))
      .catch((err) => {
        if (controller.signal.aborted) return;
        setState({ status: 'error', artists: [], error: classify(err) });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return state;
}
```

Note: during a reroll the previous `artists` are retained while `status` is `'loading'` (spec §7 — existing path stays visible under a subtle loading state).

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- usePath`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/hooks/usePath.ts frontend/src/hooks/usePath.test.tsx
git commit -m "feat(web): usePath hook mapping URL to path requests"
```

---

### Task 5: ArtistSearch component

**Files:**
- Create: `frontend/src/components/ArtistSearch.tsx`
- Test: `frontend/src/components/ArtistSearch.test.tsx`

**Interfaces:**
- Consumes: `searchArtists` from `@/api/client`; `Artist` type.
- Produces: `<ArtistSearch label: string; onSelect: (artist: Artist) => void />`. Debounces input by 250ms, queries `searchArtists`, renders a result dropdown, calls `onSelect` on click. Aborts stale requests.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/components/ArtistSearch.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistSearch } from './ArtistSearch';

afterEach(() => vi.restoreAllMocks());

test('debounces, shows results, and selects one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 0.8 },
  ]);
  const onSelect = vi.fn();
  render(<ArtistSearch label="From" onSelect={onSelect} />);

  await user.type(screen.getByLabelText('From'), 'miles');
  const option = await screen.findByText('Miles Davis');
  await user.click(option);

  expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ mbid: 'm' }));
});

test('does not query for empty input', async () => {
  const spy = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" onSelect={vi.fn()} />);
  await new Promise((r) => setTimeout(r, 300));
  expect(spy).not.toHaveBeenCalled();
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- ArtistSearch`
Expected: FAIL, component not found.

- [ ] **Step 3: Implement**

Create `frontend/src/components/ArtistSearch.tsx`:
```tsx
import { useEffect, useRef, useState } from 'react';
import { searchArtists } from '@/api/client';
import type { Artist } from '@/api/types';

interface Props {
  label: string;
  onSelect: (artist: Artist) => void;
}

export function ArtistSearch({ label, onSelect }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Artist[]>([]);
  const [open, setOpen] = useState(false);
  const inputId = useRef(`search-${Math.random().toString(36).slice(2)}`).current;

  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchArtists(q, controller.signal)
        .then((r) => {
          setResults(r);
          setOpen(true);
        })
        .catch(() => {
          /* aborted or transient — leave prior results */
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  function choose(artist: Artist) {
    onSelect(artist);
    setQuery(artist.name);
    setOpen(false);
  }

  return (
    <div className="relative">
      <label htmlFor={inputId} className="block text-sm text-[var(--color-muted)] mb-1">
        {label}
      </label>
      <input
        id={inputId}
        className="w-full rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] px-3 py-2 outline-none focus:border-[var(--color-accent)]"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        autoComplete="off"
      />
      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] overflow-hidden">
          {results.map((a) => (
            <li key={a.mbid}>
              <button
                type="button"
                className="w-full text-left px-3 py-2 hover:bg-[var(--color-accent)]/20"
                onClick={() => choose(a)}
              >
                {a.name}
                {a.disambiguation && (
                  <span className="text-[var(--color-muted)] text-sm"> — {a.disambiguation}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- ArtistSearch`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ArtistSearch.tsx frontend/src/components/ArtistSearch.test.tsx
git commit -m "feat(web): debounced artist autocomplete input"
```

---

### Task 6: LandingPage

**Files:**
- Create: `frontend/src/routes/LandingPage.tsx`
- Test: `frontend/src/routes/LandingPage.test.tsx`

**Interfaces:**
- Consumes: `ArtistSearch`; React Router `useNavigate`.
- Produces: `<LandingPage />` at `/`. Two `ArtistSearch` inputs; a "Find path" button enabled only when both are chosen and different; navigates to `/path/:fromMbid/:toMbid`. Selecting the same artist for both shows a nudge and blocks.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/routes/LandingPage.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { LandingPage } from './LandingPage';

afterEach(() => vi.restoreAllMocks());

function setup() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/path/:from/:to" element={<div data-testid="dest">dest</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

test('navigates to the path route once both artists are chosen', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockImplementation(async (q) => [
    { mbid: q.includes('miles') ? 'm' : 'd', name: q, disambiguation: '', popularity: 1 },
  ]);
  setup();
  await user.type(screen.getByLabelText('From'), 'miles');
  await user.click(await screen.findByText('miles'));
  await user.type(screen.getByLabelText('To'), 'daft');
  await user.click(await screen.findByText('daft'));
  await user.click(screen.getByRole('button', { name: /find path/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('blocks identical endpoints with a nudge', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'same', name: 'Radiohead', disambiguation: '', popularity: 1 },
  ]);
  setup();
  await user.type(screen.getByLabelText('From'), 'radio');
  await user.click(await screen.findByText('Radiohead'));
  await user.type(screen.getByLabelText('To'), 'radio');
  await user.click((await screen.findAllByText('Radiohead'))[0]);
  expect(screen.getByText(/pick two different artists/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- LandingPage`
Expected: FAIL.

- [ ] **Step 3: Implement**

Create `frontend/src/routes/LandingPage.tsx`:
```tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArtistSearch } from '@/components/ArtistSearch';
import type { Artist } from '@/api/types';

export function LandingPage() {
  const [from, setFrom] = useState<Artist | null>(null);
  const [to, setTo] = useState<Artist | null>(null);
  const navigate = useNavigate();

  const sameArtist = !!from && !!to && from.mbid === to.mbid;
  const ready = !!from && !!to && !sameArtist;

  return (
    <main className="max-w-xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-semibold mb-6">Artist Path</h1>
      <p className="text-[var(--color-muted)] mb-8">
        Name two artists and hear a smooth path between them.
      </p>
      <div className="space-y-4">
        <ArtistSearch label="From" onSelect={setFrom} />
        <ArtistSearch label="To" onSelect={setTo} />
      </div>
      {sameArtist && (
        <p className="mt-3 text-sm text-[var(--color-away)]">Pick two different artists.</p>
      )}
      <button
        type="button"
        disabled={!ready}
        onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
        className="mt-6 rounded-lg bg-[var(--color-accent)] px-4 py-2 font-medium disabled:opacity-40"
      >
        Find path
      </button>
    </main>
  );
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- LandingPage`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/LandingPage.tsx frontend/src/routes/LandingPage.test.tsx
git commit -m "feat(web): landing page with dual artist inputs"
```

---

### Task 7: Player interface, HTML audio implementation, and usePlayer hook

**Files:**
- Create: `frontend/src/player/Player.ts`, `frontend/src/player/usePlayer.ts`
- Test: `frontend/src/player/usePlayer.test.tsx`

**Interfaces:**
- Consumes: `Artist`, `Track` types.
- Produces:
  - `interface Player { play(url: string): void; pause(): void; onEnded(cb: () => void): void; dispose(): void }`.
  - `class HtmlAudioPlayer implements Player` wrapping one `HTMLAudioElement`.
  - `usePlayer(playables: { mbid: string; url: string }[]): { currentMbid: string | null; isPlaying: boolean; playFrom(mbid: string): void; toggle(): void }`. On track-end, auto-advances to the next entry in `playables`; entries that are absent (unplayable) are simply not in the list, so advancing skips them.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/player/usePlayer.test.tsx`:
```tsx
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { usePlayer } from './usePlayer';

const ended: Array<() => void> = [];
vi.mock('./Player', () => ({
  HtmlAudioPlayer: class {
    play = vi.fn();
    pause = vi.fn();
    dispose = vi.fn();
    onEnded(cb: () => void) { ended.push(cb); }
  },
}));

function Harness() {
  // Miles and Kraftwerk are playable; a middle artist with no clip is absent from the list.
  const p = usePlayer([{ mbid: 'miles', url: 'u1' }, { mbid: 'kraftwerk', url: 'u2' }]);
  return (
    <div>
      <span data-testid="current">{p.currentMbid ?? 'none'}</span>
      <button onClick={() => p.playFrom('miles')}>play</button>
    </div>
  );
}

test('auto-advances to the next playable on track end', async () => {
  const user = userEvent.setup();
  render(<Harness />);
  await user.click(screen.getByText('play'));
  expect(screen.getByTestId('current')).toHaveTextContent('miles');
  act(() => ended.forEach((cb) => cb()));
  expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk');
});
```

- [ ] **Step 2: Run test — expect FAIL**

Run: `npm test -- usePlayer`
Expected: FAIL, module not found.

- [ ] **Step 3: Implement the Player**

Create `frontend/src/player/Player.ts`:
```typescript
export interface Player {
  play(url: string): void;
  pause(): void;
  onEnded(cb: () => void): void;
  dispose(): void;
}

export class HtmlAudioPlayer implements Player {
  private audio = new Audio();

  play(url: string): void {
    if (this.audio.src !== url) this.audio.src = url;
    void this.audio.play();
  }

  pause(): void {
    this.audio.pause();
  }

  onEnded(cb: () => void): void {
    this.audio.addEventListener('ended', cb);
  }

  dispose(): void {
    this.audio.pause();
    this.audio.src = '';
  }
}
```

- [ ] **Step 4: Implement usePlayer**

Create `frontend/src/player/usePlayer.ts`:
```typescript
import { useEffect, useMemo, useRef, useState } from 'react';
import { HtmlAudioPlayer } from './Player';

interface Playable {
  mbid: string;
  url: string;
}

export function usePlayer(playables: Playable[]) {
  const player = useMemo(() => new HtmlAudioPlayer(), []);
  const [currentMbid, setCurrentMbid] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const listRef = useRef(playables);
  listRef.current = playables;

  useEffect(() => {
    player.onEnded(() => {
      const list = listRef.current;
      setCurrentMbid((cur) => {
        const idx = list.findIndex((p) => p.mbid === cur);
        const next = idx >= 0 ? list[idx + 1] : undefined;
        if (next) {
          player.play(next.url);
          setIsPlaying(true);
          return next.mbid;
        }
        setIsPlaying(false);
        return null;
      });
    });
    return () => player.dispose();
  }, [player]);

  function playFrom(mbid: string) {
    const entry = listRef.current.find((p) => p.mbid === mbid);
    if (!entry) return;
    player.play(entry.url);
    setCurrentMbid(mbid);
    setIsPlaying(true);
  }

  function toggle() {
    if (isPlaying) {
      player.pause();
      setIsPlaying(false);
    } else if (currentMbid) {
      playFrom(currentMbid);
    }
  }

  return { currentMbid, isPlaying, playFrom, toggle };
}
```

- [ ] **Step 5: Run test — expect PASS**

Run: `npm test -- usePlayer`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/player
git commit -m "feat(web): Player interface and sequential-autoplay hook"
```

---

### Task 8: useClip hook (lazy clip load + in-memory cache)

**Files:**
- Create: `frontend/src/hooks/useClip.ts`
- Test: `frontend/src/hooks/useClip.test.tsx`

**Interfaces:**
- Consumes: `getTrack` from `@/api/client`; `Track` type.
- Produces: `useClip(mbid: string): { status: 'loading' | 'ready' | 'none'; track: Track | null }`. `'none'` means the API returned 204 (unplayable). A module-level `Map` caches resolved results by MBID for the session so re-renders and re-mounts don't refetch.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/hooks/useClip.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { useClip } from './useClip';

afterEach(() => vi.restoreAllMocks());

function Harness({ mbid }: { mbid: string }) {
  const c = useClip(mbid);
  return <div data-testid="c">{c.status}:{c.track?.title ?? ''}</div>;
}

test('loads a clip and exposes the track', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<Harness mbid="miles" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:So What'));
});

test('204 becomes status none', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<Harness mbid="silent" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('none:'));
});

test('caches by mbid — second mount does not refetch', async () => {
  const spy = vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  const { unmount } = render(<Harness mbid="cached" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  unmount();
  render(<Harness mbid="cached" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  expect(spy).toHaveBeenCalledTimes(1);
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- useClip`
Expected: FAIL.

- [ ] **Step 3: Implement**

Create `frontend/src/hooks/useClip.ts`:
```typescript
import { useEffect, useState } from 'react';
import { getTrack } from '@/api/client';
import type { Track } from '@/api/types';

type ClipState = { status: 'loading' | 'ready' | 'none'; track: Track | null };

const cache = new Map<string, Track | null>();

export function useClip(mbid: string): ClipState {
  const [state, setState] = useState<ClipState>(() =>
    cache.has(mbid)
      ? { status: cache.get(mbid) ? 'ready' : 'none', track: cache.get(mbid) ?? null }
      : { status: 'loading', track: null },
  );

  useEffect(() => {
    if (cache.has(mbid)) {
      const cached = cache.get(mbid) ?? null;
      setState({ status: cached ? 'ready' : 'none', track: cached });
      return;
    }
    let active = true;
    setState({ status: 'loading', track: null });
    getTrack(mbid)
      .then((track) => {
        cache.set(mbid, track);
        if (active) setState({ status: track ? 'ready' : 'none', track });
      })
      .catch(() => {
        if (active) setState({ status: 'none', track: null });
      });
    return () => {
      active = false;
    };
  }, [mbid]);

  return state;
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- useClip`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/hooks/useClip.ts frontend/src/hooks/useClip.test.tsx
git commit -m "feat(web): lazy per-card clip resolution with session cache"
```

---

### Task 9: ArtistCard

**Files:**
- Create: `frontend/src/components/ArtistCard.tsx`
- Test: `frontend/src/components/ArtistCard.test.tsx`

**Interfaces:**
- Consumes: `useClip`; `Artist`, `BypassReason` types.
- Produces: `<ArtistCard artist, isPlaying, onPlay, onBypass />` where
  `onPlay: (mbid: string) => void` and `onBypass: (mbid: string, reason: BypassReason) => void`.
  Renders artwork (from clip cover, placeholder while loading), name, track title, a play control, and the two labeled bypass buttons `✕ Not for me` / `✓ I know them`. When the clip is `none`, the play control is disabled and de-emphasized but the card still renders. When `isPlaying`, shows the now-playing treatment.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/components/ArtistCard.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCard } from './ArtistCard';

const miles = { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 };
afterEach(() => vi.restoreAllMocks());

test('fires the two bypass signals with the right reason', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onBypass = vi.fn();
  render(<ArtistCard artist={miles} isPlaying={false} onPlay={vi.fn()} onBypass={onBypass} />);
  await user.click(screen.getByRole('button', { name: /not for me/i }));
  await user.click(screen.getByRole('button', { name: /know them/i }));
  expect(onBypass).toHaveBeenNthCalledWith(1, 'm', 'dislike');
  expect(onBypass).toHaveBeenNthCalledWith(2, 'm', 'known');
});

test('play disabled and card still present when clip is 204', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={miles} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeDisabled());
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('play fires onPlay when a clip exists', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onPlay = vi.fn();
  render(<ArtistCard artist={miles} isPlaying={false} onPlay={onPlay} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeEnabled());
  await user.click(screen.getByRole('button', { name: /play/i }));
  expect(onPlay).toHaveBeenCalledWith('m');
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- ArtistCard`
Expected: FAIL.

- [ ] **Step 3: Implement**

Create `frontend/src/components/ArtistCard.tsx`:
```tsx
import { useClip } from '@/hooks/useClip';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  onPlay: (mbid: string) => void;
  onBypass: (mbid: string, reason: BypassReason) => void;
}

export function ArtistCard({ artist, isPlaying, onPlay, onBypass }: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';

  return (
    <div
      className={`flex items-center gap-4 rounded-xl px-4 py-3 border border-[var(--color-border)] ${
        isPlaying ? 'bg-[var(--color-accent)]/15' : 'bg-[var(--color-surface)]'
      }`}
    >
      <div
        className="w-14 h-14 rounded-lg flex-none bg-[var(--color-border)] bg-cover"
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
      <button
        type="button"
        onClick={() => onBypass(artist.mbid, 'dislike')}
        className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-away)]/40 text-[var(--color-away)]"
      >
        ✕ Not for me
      </button>
      <button
        type="button"
        onClick={() => onBypass(artist.mbid, 'known')}
        className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-dig)]/40 text-[var(--color-dig)]"
      >
        ✓ I know them
      </button>
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        disabled={!playable}
        onClick={() => onPlay(artist.mbid)}
        className="w-10 h-10 rounded-full flex-none bg-[var(--color-accent)] text-white flex items-center justify-center disabled:opacity-30"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
    </div>
  );
}
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `npm test -- ArtistCard`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ArtistCard.tsx frontend/src/components/ArtistCard.test.tsx
git commit -m "feat(web): artist card with clip, play, and two bypass controls"
```

---

### Task 10: JourneyList and PlayerBar

**Files:**
- Create: `frontend/src/components/JourneyList.tsx`, `frontend/src/components/PlayerBar.tsx`
- Test: `frontend/src/components/JourneyList.test.tsx`

**Interfaces:**
- Consumes: `ArtistCard`, `usePlayer`, `useClip` (indirectly), `Artist`, `BypassReason`.
- Produces:
  - `<JourneyList artists: Artist[]; onBypass: (mbid, reason) => void />` — renders the vertical spine of `ArtistCard`s, owns the `usePlayer` wiring, and passes `isPlaying`/`onPlay` down. It builds the `playables` list from resolved clips (via a shared clip lookup — see note) so autoplay skips unplayable artists.
  - `<PlayerBar currentName: string | null; isPlaying: boolean; onToggle: () => void />` — fixed bar reflecting the current track.
- **Note on playables:** `JourneyList` cannot read `useClip` state for children directly. Resolve the playable list by calling `getTrack` availability through a small shared map is over-engineering for alpha; instead, treat **every artist as a candidate** and let `usePlayer.playFrom` no-op when a card has no URL. To keep the single source of clip truth, `JourneyList` maintains a `Record<mbid, string | null>` of resolved URLs updated via an `onClipResolved` callback threaded through `ArtistCard`. Add that callback now.

- [ ] **Step 1: Extend ArtistCard with an onClipResolved callback**

Modify `frontend/src/components/ArtistCard.tsx`: add optional prop `onClipResolved?: (mbid: string, url: string | null) => void` and call it in an effect when `clip.status` settles:
```tsx
import { useEffect } from 'react';
// ...add to Props:
//   onClipResolved?: (mbid: string, url: string | null) => void;
// ...inside component, after `const playable = ...`:
useEffect(() => {
  if (clip.status === 'loading') return;
  onClipResolved?.(artist.mbid, clip.track?.previewUrl ?? null);
}, [clip.status]); // eslint-disable-line react-hooks/exhaustive-deps
```

- [ ] **Step 2: Write the failing test**

Create `frontend/src/components/JourneyList.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { JourneyList } from './JourneyList';

const artists = [
  { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
  { mbid: 'k', name: 'Kraftwerk', disambiguation: '', popularity: 0.8 },
];
afterEach(() => vi.restoreAllMocks());

test('renders every artist as a card', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} onBypass={vi.fn()} />);
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Kraftwerk')).toBeInTheDocument();
});

test('clicking play marks that card now-playing', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  await user.click(firstPlay);
  expect(screen.getByText(/now playing/i)).toBeInTheDocument();
});
```

- [ ] **Step 3: Run test — expect FAIL**

Run: `npm test -- JourneyList`
Expected: FAIL.

- [ ] **Step 4: Implement PlayerBar**

Create `frontend/src/components/PlayerBar.tsx`:
```tsx
interface Props {
  currentName: string | null;
  isPlaying: boolean;
  onToggle: () => void;
}

export function PlayerBar({ currentName, isPlaying, onToggle }: Props) {
  if (!currentName) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 border-t border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 flex items-center gap-3">
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        onClick={onToggle}
        className="w-9 h-9 rounded-full bg-[var(--color-accent)] text-white flex items-center justify-center"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
      <span className="text-sm text-[var(--color-muted)]">{currentName}</span>
    </div>
  );
}
```

- [ ] **Step 5: Implement JourneyList**

Create `frontend/src/components/JourneyList.tsx`:
```tsx
import { useMemo, useRef, useState } from 'react';
import { ArtistCard } from './ArtistCard';
import { PlayerBar } from './PlayerBar';
import { usePlayer } from '@/player/usePlayer';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artists: Artist[];
  onBypass: (mbid: string, reason: BypassReason) => void;
}

export function JourneyList({ artists, onBypass }: Props) {
  const [urls, setUrls] = useState<Record<string, string | null>>({});
  const urlsRef = useRef(urls);
  urlsRef.current = urls;

  const playables = useMemo(
    () =>
      artists
        .map((a) => ({ mbid: a.mbid, url: urls[a.mbid] }))
        .filter((p): p is { mbid: string; url: string } => !!p.url),
    [artists, urls],
  );

  const player = usePlayer(playables);
  const currentName = artists.find((a) => a.mbid === player.currentMbid)?.name ?? null;

  return (
    <>
      <ol className="relative flex flex-col gap-2 pl-5">
        <span className="absolute left-1.5 top-3 bottom-3 w-[3px] rounded bg-gradient-to-b from-[var(--color-accent)] to-[var(--color-dig)]" />
        {artists.map((artist) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              onPlay={player.playFrom}
              onBypass={onBypass}
              onClipResolved={(mbid, url) => setUrls((prev) => ({ ...prev, [mbid]: url }))}
            />
          </li>
        ))}
      </ol>
      <PlayerBar currentName={currentName} isPlaying={player.isPlaying} onToggle={player.toggle} />
    </>
  );
}
```

- [ ] **Step 6: Run test — expect PASS**

Run: `npm test -- JourneyList`
Expected: 2 passed. Re-run `npm test -- ArtistCard` to confirm the Step-1 change didn't regress it.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/JourneyList.tsx frontend/src/components/PlayerBar.tsx frontend/src/components/ArtistCard.tsx
git commit -m "feat(web): vertical journey list with autoplay and player bar"
```

---

### Task 11: PathStatus and PathPage integration

**Files:**
- Create: `frontend/src/components/PathStatus.tsx`, `frontend/src/routes/PathPage.tsx`
- Modify: `frontend/src/App.tsx` (add routes)
- Test: `frontend/src/routes/PathPage.test.tsx`

**Interfaces:**
- Consumes: `usePath`, `JourneyList`, `PathStatus`, `addExclusion`, `clearExclusions`, React Router `useSearchParams`, `useNavigate`, `useParams`.
- Produces: `<PathPage />` at `/path/:from/:to`. Renders `JourneyList` when ready; a loading skeleton while loading (retaining the previous list beneath it); `PathStatus` for `nopath` (with Clear exclusions) and `notfound`/`unknown`. Bypass handler appends to the URL via `addExclusion` and navigates — producing a fresh path. `App.tsx` maps `/` → `LandingPage`, `/path/:from/:to` → `PathPage`.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/routes/PathPage.test.tsx`:
```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { PathPage } from './PathPage';

afterEach(() => vi.restoreAllMocks());

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes><Route path="/path/:from/:to" element={<PathPage />} /></Routes>
    </MemoryRouter>,
  );
}

test('renders the path, then a bypass triggers a new request carrying the exclusion', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const buildPath = vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9 },
    ])
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7 },
    ]);

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  const dislikeButtons = screen.getAllByRole('button', { name: /not for me/i });
  await user.click(dislikeButtons[1]); // bypass Herbie

  await waitFor(() =>
    expect(buildPath).toHaveBeenLastCalledWith(
      ['m', 'd'],
      [{ id: 'h', reason: 'dislike' }],
      expect.any(AbortSignal),
    ),
  );
  await screen.findByText('Sun Ra');
});

test('shows the no-path banner with a clear-exclusions action on 409', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/m/d?dislike=z');
  expect(await screen.findByText(/no path avoiding those artists/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /clear exclusions/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `npm test -- PathPage`
Expected: FAIL.

- [ ] **Step 3: Implement PathStatus**

Create `frontend/src/components/PathStatus.tsx`:
```tsx
import { Link } from 'react-router-dom';

interface Props {
  error: 'notfound' | 'nopath' | 'unknown';
  onClearExclusions: () => void;
}

export function PathStatus({ error, onClearExclusions }: Props) {
  if (error === 'nopath') {
    return (
      <div className="rounded-lg border border-[var(--color-away)]/40 p-4">
        <p className="mb-3">No path avoiding those artists.</p>
        <button
          type="button"
          onClick={onClearExclusions}
          className="rounded-lg bg-[var(--color-accent)] px-3 py-1.5 text-sm"
        >
          Clear exclusions
        </button>
      </div>
    );
  }
  const message =
    error === 'notfound' ? "Couldn't find that artist." : 'Something went wrong building the path.';
  return (
    <div className="rounded-lg border border-[var(--color-border)] p-4">
      <p className="mb-3">{message}</p>
      <Link to="/" className="text-[var(--color-accent)]">
        Start over
      </Link>
    </div>
  );
}
```

- [ ] **Step 4: Implement PathPage**

Create `frontend/src/routes/PathPage.tsx`:
```tsx
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { JourneyList } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { addExclusion, clearExclusions } from '@/lib/exclusions';
import type { BypassReason } from '@/api/types';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();

  function go(next: URLSearchParams) {
    const qs = next.toString();
    navigate(`/path/${from}/${to}${qs ? `?${qs}` : ''}`);
  }

  function handleBypass(mbid: string, reason: BypassReason) {
    go(addExclusion(params, mbid, reason));
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-10 pb-24">
      {state.status === 'error' && state.error ? (
        <PathStatus error={state.error} onClearExclusions={() => go(clearExclusions(params))} />
      ) : (
        <div className={state.status === 'loading' ? 'opacity-60 transition-opacity' : ''}>
          {state.artists.length > 0 ? (
            <JourneyList artists={state.artists} onBypass={handleBypass} />
          ) : (
            <p className="text-[var(--color-muted)]">Building your path…</p>
          )}
        </div>
      )}
    </main>
  );
}
```

- [ ] **Step 5: Wire routes in App.tsx**

Overwrite `frontend/src/App.tsx`:
```tsx
import { Route, Routes } from 'react-router-dom';
import { LandingPage } from '@/routes/LandingPage';
import { PathPage } from '@/routes/PathPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/path/:from/:to" element={<PathPage />} />
    </Routes>
  );
}
```

Then update `frontend/src/App.test.tsx` to render within a router and assert the landing heading:
```tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

test('landing page renders at root', () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByRole('heading', { name: /artist path/i })).toBeInTheDocument();
});
```

- [ ] **Step 6: Run the full suite — expect PASS**

Run: `npm test`
Expected: all tests pass (App, client, exclusions, usePath, ArtistSearch, LandingPage, usePlayer, useClip, ArtistCard, JourneyList, PathPage).

- [ ] **Step 7: Commit**

```bash
git add frontend/src
git commit -m "feat(web): path page wiring reroll-as-new-path and status states"
```

---

### Task 12: API CORS middleware (backend, additive)

**Files:**
- Modify: `api/src/artistpath_api/config.py` (add `cors_origins` setting)
- Modify: `api/src/artistpath_api/app.py` (add CORS middleware)
- Test: `api/tests/test_cors.py`

**Interfaces:**
- Consumes: existing `ApiConfig`, `create_app` (from Task-0 codebase).
- Produces: CORS headers on responses when an `Origin` from the configured allow-list is present. Default allow-list: localhost dev origins. This is the only backend change in Stage 3a and is not needed for local proxied dev — it unblocks the future 3b cross-origin deploy.

- [ ] **Step 1: Read the current config and app wiring**

Read `api/src/artistpath_api/config.py` and `api/src/artistpath_api/app.py`. Confirm `ApiConfig` fields and how `create_app` builds the `FastAPI` instance (see `app.py:32` `create_app`).

- [ ] **Step 2: Write the failing test**

Create `api/tests/test_cors.py`:
```python
def test_cors_allows_configured_dev_origin(client):
    r = client.get(
        "/api/artists/search?q=mi",
        headers={"Origin": "http://localhost:5173"},
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
```

Note: reuse the existing `client` fixture from `api/tests/conftest.py`. If that fixture builds the app without CORS, extend it or build a CORS-enabled app in this test per the conftest pattern.

- [ ] **Step 3: Run test — expect FAIL**

Run (from `api/`): `UV_LINK_MODE=copy uv run --extra dev pytest tests/test_cors.py -q`
Expected: FAIL — no `access-control-allow-origin` header.

- [ ] **Step 4: Add the config field**

In `api/src/artistpath_api/config.py`, add to `ApiConfig` a `cors_origins` field defaulting to `["http://localhost:5173"]`, read from `ARTISTPATH_CORS_ORIGINS` (comma-separated) if present. Match the file's existing config style (env var reading pattern already in the class).

- [ ] **Step 5: Add the middleware**

In `api/src/artistpath_api/app.py`, inside `create_app`, after `app = FastAPI(...)`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)
```
Place the `import` at the top of the file with the other imports.

- [ ] **Step 6: Run test — expect PASS**

Run (from `api/`): `UV_LINK_MODE=copy uv run --extra dev pytest tests/test_cors.py -q`
Expected: PASS.

- [ ] **Step 7: Run the full API suite — expect no regressions**

Run (from `api/`): `UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: all existing tests + the new one pass.

- [ ] **Step 8: Commit**

```bash
git add api/src/artistpath_api/config.py api/src/artistpath_api/app.py api/tests/test_cors.py
git commit -m "feat(api): configurable CORS for cross-origin frontend"
```

---

### Task 13: Playwright end-to-end test

**Files:**
- Create: `frontend/playwright.config.ts`, `frontend/e2e/path.spec.ts`
- Modify: `frontend/package.json` (add `test:e2e` script)

**Interfaces:**
- Consumes: the running frontend + a running API (documented as a prerequisite).
- Produces: one Playwright run covering search → path renders → bypass → new path excludes the artist and is reconfigured (spec §9 E2E row).

- [ ] **Step 1: Install Playwright**

Run in `frontend/`:
```bash
npm install -D @playwright/test
npx playwright install chromium
```

- [ ] **Step 2: Configure Playwright**

Create `frontend/playwright.config.ts`:
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://localhost:5173' },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
```

- [ ] **Step 3: Add the script**

In `frontend/package.json` `"scripts"`: `"test:e2e": "playwright test"`.

- [ ] **Step 4: Write the E2E spec**

Create `frontend/e2e/path.spec.ts`:
```typescript
import { expect, test } from '@playwright/test';

// Requires the API running on :8000 against the 5k graph, and the dev server (started by webServer).
test('search, path, bypass produces a new path without the bypassed artist', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('From').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('To').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /find path/i }).click();

  // The path renders as a list of cards.
  await expect(page.getByText('Miles Davis')).toBeVisible();
  const before = await page.locator('ol li').allInnerTexts();
  expect(before.length).toBeGreaterThan(1);

  // Bypass the second artist with "not for me".
  const secondName = (await page.locator('ol li .font-semibold').nth(1).innerText());
  await page.locator('ol li').nth(1).getByRole('button', { name: /not for me/i }).click();

  // URL now carries the exclusion, and the bypassed artist is gone from the new path.
  await expect(page).toHaveURL(/dislike=/);
  await expect(page.getByText(secondName, { exact: true })).toHaveCount(0);
});
```

- [ ] **Step 5: Run the E2E (manual prerequisite: API on :8000)**

Start the API in a separate terminal (from `api/`):
```bash
ARTISTPATH_GRAPH=../builder/scratch/graph-5k.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```
Then run (from `frontend/`): `npm run test:e2e`
Expected: 1 passed. If artist names differ in the 5k graph, adjust the two search terms to artists known to be present.

- [ ] **Step 6: Commit**

```bash
git add frontend/playwright.config.ts frontend/e2e frontend/package.json
git commit -m "test(web): Playwright e2e for search, path, and reroll"
```

---

### Task 14: Frontend README and dev-loop note

**Files:**
- Create: `frontend/README.md`
- Modify: `README.md` at repo root if one exists (add a pointer); otherwise skip.

**Interfaces:**
- Consumes: nothing.
- Produces: documentation of the two-process dev loop and the env vars.

- [ ] **Step 1: Write the frontend README**

Create `frontend/README.md`:
```markdown
# artistpath web frontend

React + Vite + TypeScript SPA for the artist-path app. Implements the
Stage 3a spec (`docs/superpowers/specs/2026-07-20-stage3-web-frontend-design.md`).

## Two-process dev loop

The frontend proxies `/api` to the Python API. Run both:

**Terminal 1 — API** (from `api/`, against the 5k graph):
```bash
ARTISTPATH_GRAPH=../builder/scratch/graph-5k.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

**Terminal 2 — web** (from `frontend/`):
```bash
npm run dev
```

Open the URL Vite prints (default http://localhost:5173).

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `VITE_API_BASE` | `/api` | API base path used by the client. Leave as `/api` for the proxied dev setup. |
| `VITE_API_PROXY` | `http://localhost:8000` | Where the dev server proxies `/api` (dev only). |

## Testing

```bash
npm test          # unit + component (Vitest)
npm run test:e2e  # Playwright (needs the API running on :8000)
```
```

- [ ] **Step 2: Commit**

```bash
git add frontend/README.md
git commit -m "docs(web): frontend README and two-process dev loop"
```

---

## Self-Review (completed while writing)

**Spec coverage:**
- §1.3 CORS change → Task 12. Vite proxy → Task 1. `VITE_API_BASE` → Tasks 2, 14. ✓
- §2 vertical journey + labeled cards + now-playing → Tasks 9, 10. ✓
- §4 URL as source of truth, distinct dislike/known → Tasks 3, 4, 11. ✓
- §5.1 component tree → Tasks 5–11 (one component per task or grouped). ✓
- §5.2 two-phase load → Task 4 (artists-first) + Task 8 (lazy clip). ✓
- §5.3 typed client → Task 2. ✓
- §6 Player seam + autoplay + skip unplayable → Task 7, 10. ✓
- §7 reroll-as-new-path (no diff/animation), 409 clear-exclusions → Task 11 (+ usePath retains prior artists during loading). ✓
- §8 edge states: no matches (Task 5 dropdown empties), same artist (Task 6), 404/unknown/nopath (Task 11), 204 unplayable (Tasks 8, 9). ✓
- §9 testing incl. one Playwright E2E → each task's tests + Task 13. ✓
- §10 dev loop → Task 14. ✓
- §11 seams: `sources: id[]` (Task 2), Player interface (Task 7), opaque MBIDs (throughout), distinct signals (Task 3). ✓

**Placeholder scan:** No TBD/TODO; every code step carries complete code. The one prose-instruction step (Task 10 Step 1, Task 12 Steps 4–5) references exact files/lines and shows the code to add. ✓

**Type consistency:** `Artist`, `Track`, `Exclusion`, `BypassReason` defined in Task 2 and used verbatim after. `PathState` defined in Task 4. `usePlayer` returns `{ currentMbid, isPlaying, playFrom, toggle }` — consumed exactly in Task 10. `onBypass(mbid, reason)` signature consistent across Tasks 9, 10, 11. `onClipResolved(mbid, url|null)` introduced in Task 10 Step 1 and consumed in the same task. ✓

**Known adjustment point:** Task 12 Steps 4–5 depend on the exact shape of `ApiConfig`; the implementer reads the file first (Step 1) and matches its env-reading style. Task 13 search terms may need swapping for artists present in the 5k graph.
