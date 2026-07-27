# Stage 3a — Web Frontend Design

**Date:** 2026-07-20
**Role: COMPLETE — shipped.** The frontend is live in `frontend/` and has since been reworked
by Gate 2 Track D. Two details here have moved on: the **5k dev graph is retired**, and the
code is on React 19. Where this and the code disagree, **the code wins**; for current status
see [`../NEXT.md`](../NEXT.md). *(Read "Approved, ready for implementation planning" until
2026-07-27.)*
**Scope:** The web frontend only, built and validated locally against the existing Python/FastAPI API on the 5k graph. AWS packaging, deploy, and CI/CD are deferred to a separate Stage-3b infra spec.

Parent design: [`2026-07-19-artist-path-alpha-design.md`](./2026-07-19-artist-path-alpha-design.md). Where this spec and the parent disagree, the reason is recorded inline (§1) — the parent predates the Stage-2 decision to build the API in Python.

---

## 1. Scope and the API boundary

### 1.1 What this spec covers

The React web app described in the parent §3.3: two autocomplete artist inputs, an ordered vertical run of artist cards with clips and two bypass controls each, sequential autoplay, reroll, and shareable URLs. Nothing server-side except one additive change (§1.3).

### 1.2 What it does not cover

AWS infrastructure, CDK, App Runner, S3/CloudFront, DynamoDB wiring, GitHub Actions CI/CD, and the production frontend/API topology. These are a separate Stage-3b spec, to be written once the 75k graph is built (the crawl was still running on 2026-07-20). Deploying anything real wants the finished graph, so there is no value in designing infra against the 5k placeholder now.

### 1.3 Reconciling with the parent: the API is Python, not Node

The parent §3.2–3.3 assumed a Node/TS Fastify API with the frontend "served by the same container." Stage 2 built the API in **Python/FastAPI** instead. This changes only how the two talk; it does not change any behaviour in the parent design.

- **Development:** the Vite dev server proxies `/api/*` to `http://localhost:8000`. The browser sees a single origin, so **no CORS is required for local work** and there is no build-time coupling between the packages.
- **The one backend change in this stage:** add FastAPI **CORS middleware** to `api/src/artistpath_api/app.py`, with allowed origins read from config (default: localhost dev origins only). This is additive and unblocks 3b, where the SPA may be served from a different origin (e.g. S3+CloudFront). It is the *only* change to the API package here.
- **Deferred to 3b:** the deploy-time topology — static SPA on S3+CloudFront calling the API cross-origin, versus mounting the built SPA as static files inside the FastAPI container. Not decided here. The frontend reads its API base from `VITE_API_BASE` (default `/api` for the proxied dev case) so either choice is a configuration change, not a rewrite.

### 1.4 Repository shape

A new `frontend/` package sits alongside `api/` and `builder/`. It is independent: it depends on the API only through HTTP, described by a typed client (§3.1).

---

## 2. Visual and interaction direction

Settled during brainstorming (visual companion, 2026-07-20):

- **Aesthetic:** modern and polished — real artist artwork as the visual anchor, smooth transitions, a contemporary music-product feel. Not a faithful reproduction of the original's utilitarian coloured bars.
- **Path layout:** **vertical journey** — full-width artist cards stacked top-to-bottom along a gradient "spine," scrolled downward. Chosen over a horizontal filmstrip (scrolls off-screen on long paths, cramped controls, weak on mobile) and a wrapping grid (loses the linear step-by-step reading). The vertical journey has room for the two bypass controls, reads well on mobile, and simply grows taller when a reroll lengthens the path.
- **Card treatment:** **labeled actions** — both bypass controls visible and named, colour-coded to their opposite meanings (warm = "not for me" / route away; cool-green = "know them already" / dig deeper). Chosen over icon-minimal (meaning not obvious at a glance) and an overflow menu (buries the reroll, which is the core mechanic). In a personal alpha where these behaviours are being tuned, the signals must be visible and legible.

Card anatomy: artwork · artist name · track title · play control · `[✕ Not for me]` `[✓ I know them]`. The currently-playing card gets a distinct now-playing treatment (accent spine + label).

---

## 3. Architecture and stack

- **React + Vite + TypeScript** — SPA, no SSR (nothing here needs it; the API is a separate Python runtime).
- **Tailwind CSS** + a small design-token layer — utility-first styling keeps the card and spine styling co-located; the one opinionated dependency.
- **React Router** — the URL is application state (§4).
- **Typed `fetch` client** — a thin `apiClient` module wrapping the three endpoints; no data-fetching library needed at alpha size.
- **Vitest + React Testing Library** for unit/component tests; **one Playwright E2E** (§8).

Rejected: Next.js (SSR/routing/image machinery unused; adds a second server runtime and muddies the deferred deploy decision). Vanilla CSS Modules (viable, but slower to reach the chosen polish by hand).

---

## 4. State model

**The URL is the single source of truth** (parent §3.3).

- Landing: `/`
- Path: `/path/:from/:to?dislike=<mbid,mbid,…>&known=<mbid,mbid,…>`

`:from` and `:to` are artist MBIDs. `dislike` and `known` are comma-separated MBID lists — the two bypass signals, kept distinct so the "know them already" signal stays a durable statement of taste (parent §4.3 "Future value"), not collapsed into a generic exclusion.

Two consequences fall out for free and are required behaviours, not incidental:

1. **Paths are shareable** — the whole state travels in the URL.
2. **Browser Back undoes a bypass** — each reroll is a new URL, so history navigation is bypass undo/redo with no extra code.

Two kinds of client state are deliberately **not** in the URL, because they do not define the path:

- **Transient playback state** — which card is playing, audio position, play/pause.
- **Per-card clip resolution** — resolved lazily (§5), cached in memory by MBID for the session.

---

## 5. Components and data flow

### 5.1 Component tree

```
App (router)
├─ LandingPage            /            two ArtistSearch inputs → navigate to /path/:from/:to
│   └─ ArtistSearch       debounced GET /api/artists/search; accent-insensitive dropdown
├─ PathPage               /path/:from/:to
│   ├─ PathHeader         the two endpoint artists; "start over"
│   ├─ JourneyList        the vertical spine; maps the path array → ArtistCard[]
│   │   └─ ArtistCard     art · name · track · play · [✕ Not for me] [✓ I know them]
│   ├─ PlayerBar          sequential autoplay controls; reflects the current track
│   └─ PathStatus         loading / no-path / error banner
└─ (shared) apiClient · usePath hook · Player
```

Each unit has one purpose and a clear interface: `ArtistSearch` turns a query into a chosen MBID; `usePath` turns the URL into a path; `ArtistCard` renders one artist and emits play/bypass intents; `Player` owns audio. Any of them can be tested without the others.

### 5.2 Two-phase load (parent §5.2) — the path renders instantly

1. `usePath` reads the URL, builds `{ sources:[from,to], exclude:[{id,reason}…] }` from the two bypass lists, and calls `POST /api/path`. The response is **artists only**; `JourneyList` renders the entire journey immediately.
2. Each `ArtistCard` independently calls `GET /api/artists/:mbid/track`, in parallel, and caches the result in memory by MBID. A card gains its artwork and a working play control the moment its clip resolves. A `204` (no clip available) renders the card **unplayable but present and correctly positioned** — a missing clip must never block rendering or alter the path (parent §5.1).

### 5.3 Typed API client

`apiClient` exposes exactly three calls, mirroring the API (`api/README.md`): `searchArtists(q)`, `buildPath(sources, exclude)`, `getTrack(mbid)`. Response types mirror the Pydantic models (`ArtistOut`, `PathResponse`, `TrackOut`). Base URL from `VITE_API_BASE` (default `/api`).

---

## 6. Playback

Behind a **`Player` interface** (parent §7.2) so a Spotify Web Playback SDK implementation can drop in later without touching UI or routing.

- Interface: `play(url)`, `pause()`, `onEnded`.
- Alpha implementation wraps a single HTML `<audio>` element, 30-second clips, no authentication (parent §5.4).
- Clicking play on any card starts playback there and **auto-advances down the journey on track-end**, skipping unplayable (`204`) cards. `PlayerBar` reflects the current artist and play/pause state; the playing card shows the now-playing treatment.

Energy-smoothing between adjacent tracks is out (parent §5.3 — the Echo Nest features are gone and have no free replacement). Clip selection is whatever the API returns for the artist.

---

## 7. Reroll behaviour

The mechanic the parent is most emphatic about (parent §3.3, §4.3). The frontend's job is to carry the two signals faithfully and to present every reroll honestly.

- **Triggering:** clicking **✕ Not for me** or **✓ I know them** on a card appends that artist's MBID to the corresponding URL query param (`dislike=` / `known=`) and navigates. The URL change re-runs `usePath`, producing a fresh `POST /api/path`. The backend already shapes the two signals differently (avoidance vs. floor-relaxation); the frontend does not encode any of that — it only routes the MBID into the right list.

- **The result is a wholly new path, never an edit.** This is a hard requirement, and it is a set of prohibitions on things a React developer would otherwise do by reflex:
  - No animating one card out and another in; no cross-fade or slide that implies a 1-for-1 substitution.
  - No diffing the new path against the old to "keep" shared cards in place.
  - No preserving per-card scroll position to make the change feel small.

  `JourneyList` re-renders from the new artist array, keyed by MBID; React reconciles naturally. We deliberately add **no** transition choreography that would misrepresent an unchanged-length assumption. A reroll may return a **longer or shorter** path, and the expansion is the discovery mechanism (parent §4.3) — the UI must not fight it.

- **During a reroll:** the existing path stays visible under a subtle loading state (no jarring blank), then is replaced atomically when the new path arrives.

- **No path found** (hard exclusions disconnected the endpoints → API `409`): `PathStatus` shows an explicit "no path avoiding those artists" message with a **Clear exclusions** action (parent §4.3 failure handling). Never a silent failure, never a partial path.

---

## 8. Edge, empty, and loading states

Every screen handles its off-happy-path cases so nothing renders half-broken:

| Situation | Trigger | Behaviour |
|---|---|---|
| Empty landing | `/` | Two empty inputs, brief explanation. |
| No search matches | search returns `[]` | "No artists found — autocomplete only offers artists in the graph" (parent §8.3). |
| Same artist both sides | from == to before navigating | Blocked with a nudge; no request made. |
| Path loading | phase-1 in flight | Skeleton journey; per-card art/clip skeletons in phase-2. |
| Unknown artist in URL | shared/edited link, bad MBID → `404` | Explicit "couldn't find that artist," link back to landing. |
| No path | hard exclusions → `409` | Clear-exclusions banner (§7). |
| Clip missing | `204` | Unplayable card, de-emphasised play control, path intact. |

---

## 9. Testing

Matches the parent §9 frontend obligations.

| Layer | Coverage |
|---|---|
| `ArtistSearch` (Vitest + RTL) | Debounce; accent-insensitive matching; keyboard navigation; selecting a result. |
| `usePath` (Vitest) | URL query params ↔ request body mapping; the two bypass signals land in the correct `reason`; a shared URL reconstructs the exact path and exclusions. |
| `ArtistCard` (RTL) | Playable vs `204` rendering; play and both bypass intents fire with the right MBID/reason. |
| `Player` (Vitest) | Auto-advance on `onEnded`; skips unplayable cards. |
| E2E (Playwright, one run) | search → path renders → bypass → the new path excludes the artist and is **fully reconfigured, not a 1-for-1 substitution**. Runs against the real local API on the committed fixture graph. |

---

## 10. Local development

- `frontend/` package. `npm run dev` starts Vite with the `/api` → `:8000` proxy.
- The API runs separately per `api/README.md` (`uv run uvicorn … --factory --port 8000`) against the 5k graph.
- A root note documents the two-process dev loop. No AWS, no Docker, no dependency on the crawl finishing — this stage is fully exercisable today against the 5k graph.

---

## 11. Seams honoured from the parent

- **`sources: id[]`** — `buildPath` takes an array; alpha passes two (parent §7.1). Multi-artist pathing is a caller change.
- **`Player` interface** (§6) — parent §7.2.
- **Opaque MBIDs at the edges** — the frontend treats artist identifiers as opaque strings; it makes no assumption that a node is an artist (parent §7.3).
- **Two bypass signals kept distinct** in the URL (§4) — preserves "know them already" as a future taste signal (parent §4.3).

---

## 12. Open decisions

None blocking. The production frontend/API topology is deliberately deferred to the Stage-3b infra spec (§1.2); the `VITE_API_BASE` seam keeps that choice cheap.
