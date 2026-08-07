# artistpath web frontend

React + Vite + TypeScript SPA for the artist-path app. Implements the
Stage 3a spec (`docs/superpowers/specs/2026-07-20-stage3-web-frontend-design.md`).

A vertical "journey" of artist cards between two chosen artists: each card has
artwork and a 30-second clip with sequential autoplay.

**Each interior card carries a recessed "Reroute from here" footer strip** that
opens a tray offering the two bypass signals — **"Steer away"** (`dislike`) and
**"Dig deeper"** (`known`) — either of which rerolls the **whole** path, not just
that card. The two endpoint cards have no strip: there is nothing to reroute
about an artist you chose. Restyled 2026-08-07; before that both controls sat on
the card face and read "✕ Not for me" / "✓ I know them".

All path state lives in the URL (`/path/:from/:to?dislike=…&known=…`), so paths
are shareable and Back undoes a bypass. **The URL keys are the wire contract and
did not change with the labels** — see `api/README.md`.

## Two-process dev loop

The frontend proxies `/api` to the Python API. Run both:

**Terminal 1 — API** (from `api/`, boots the adopted 75k graph by default):

```bash
uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

> On Windows, prefix `uv` commands with `UV_LINK_MODE=copy` — hardlinking fails at
> `C:\dev\music-app`, though uv falls back to copying by itself.

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
npm run build     # typecheck (tsc) + production build
npm run test:e2e  # Playwright (needs the API running on :8000)
```
