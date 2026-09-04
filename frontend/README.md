# artistpath web frontend

React + Vite + TypeScript SPA for the artist-path app. Implements the
Stage 3a spec (`docs/superpowers/specs/2026-07-20-stage3-web-frontend-design.md`).

A vertical "journey" of artist cards between two chosen artists: each card has
artwork and a 30-second clip with sequential autoplay.

**Each interior card carries a recessed footer strip that is itself the bypass
control** — press **"Dig deeper"** (`known`) and the **whole** path rerolls, not
just that card. There is no tray: since `LUX-1` removed the second signal
("Steer away" / `dislike`), a disclosure revealing one button would be a wasted
press, so the strip IS the control rather than something that opens one. The two
endpoint cards have no strip: there is nothing to reroute about an artist you
chose. Restyled 2026-08-07; before that both controls sat on the card face and
read "✕ Not for me" / "✓ I know them". The `dislike` mechanism and its URL
parameter still exist — see below — only the UI control is gone.

Each card also carries a **"Try another track"** control when the resolved
artist has more than one playable candidate (`LUX-3`) — it cycles the clip
shown for that card, in place, without touching the path or the URL. It is
absent for thin catalogues (an artist with exactly one playable track) and for
silent cards, since the endpoint reports the candidate count and the UI never
guesses it.

All path state lives in the URL (`/path/:from/:to?dislike=…&known=…`), so paths
are shareable and Back undoes a bypass. **The URL keys are the wire contract and
did not change with the labels** — see `api/README.md`. The clip index is
deliberately not part of that state (spec §3): it lives in component state only,
so Back does not restore a clip choice.

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
