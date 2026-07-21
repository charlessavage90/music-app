# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**artistpath** — an app that builds a listenable "journey" of artist cards between
two chosen artists. Given artist A and artist B it finds a least-cost path through
a similarity graph and renders each hop as a card with a 30-second clip. Two bypass
signals ("not for me" / "know them already") reroll the whole path.

Three independent packages:

- **`builder/`** — Python. Crawls artist similarity data and compiles it into a single
  immutable binary graph artifact (`APG1` format). Run offline; produces the graph.
- **`api/`** — Python/FastAPI. Loads the artifact into memory at boot and serves
  search, pathfinding, bypass rerolls, and clip resolution. Reads the `APG1` format
  directly and **shares no code with `builder/`**.
- **`frontend/`** — React 19 + Vite + TypeScript SPA. Consumes the API. All path
  state lives in the URL (`/path/:from/:to?dislike=…&known=…`) so paths are shareable
  and Back undoes a bypass.

The **`APG1` binary artifact is the contract** between builder and api — not shared
Python code. Both packages parse the format independently (`builder/…/artifact.py`
writes it, `api/…/graph_store.py` reads it). Keep them in lockstep by hand; there is
no shared module to enforce it.

## Environment note (important)

The project lives under OneDrive on Windows. **Prefix every `uv` command with
`UV_LINK_MODE=copy`** or it fails with hardlink errors:

```bash
UV_LINK_MODE=copy uv run --extra dev pytest -q
```

Each Python package has its own `.venv` and `pyproject.toml`; `cd` into the package
before running `uv`.

## Commands

### builder (from `builder/`)
```bash
UV_LINK_MODE=copy uv run --extra dev pytest -q          # all tests
UV_LINK_MODE=copy uv run --extra dev pytest -q -k crawl # single test / pattern

# data pipeline (each step reads the previous step's output):
uv run artistpath-build bootstrap --out bootstrap.json
uv run artistpath-build crawl  --bootstrap bootstrap.json --archive-dir ./archive
uv run artistpath-build build  --archive-dir ./archive --out graph-v1.bin
uv run artistpath-build fixture --graph graph-v1.bin --out fixture.bin --size 500
# --target N caps discovery for trial runs; --s3-bucket/--s3-prefix use S3 archive
```

### api (from `api/`)
```bash
UV_LINK_MODE=copy uv run --extra dev pytest -q                 # all tests
UV_LINK_MODE=copy uv run --extra dev pytest -q -k pathfinding  # single test / pattern

# dev server against the committed 5k graph:
ARTISTPATH_GRAPH=../builder/scratch/graph-5k.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

### frontend (from `frontend/`)
```bash
npm run dev            # Vite dev server (proxies /api → :8000)
npm test               # Vitest unit + component (single run)
npm test -- usePath    # single test file / pattern
npm run test:watch     # Vitest watch
npm run test:e2e       # Playwright — REQUIRES the API running on :8000
npm run build          # tsc typecheck + production build
npm run lint           # oxlint
```

The frontend needs the API running to be useful. Two-process dev loop: API on :8000
(terminal 1), `npm run dev` (terminal 2). Playwright e2e specs live in `e2e/` and are
excluded from the Vitest run.

## Architecture and key concepts

### Data pipeline (builder)
`bootstrap → crawl → build → fixture`. The crawler is a resumable, rate-limited
snowball: no ranked list of all artists exists, so the frontier is discovered
breadth-first from similarity responses. The crawler **only fills an archive** of raw
JSON responses; `build` reads the archive and never touches the network. This is a
hard rule — the replay test injects a fetcher that raises to prove `build_from_archive`
is offline. It exists because **byte-identical output for identical input is required**
(determinism, spec §9): every ordering decision is explicit (IDs assigned in
sorted-MBID order, ties broken on lowest MBID).

Resume works off a checkpoint holding `done` and `discovered` sets; the pending queue
is rebuilt as `discovered − done`, which also auto-retries artists that failed on a
previous run.

### Popularity = score-weighted in-degree
There is **no separate popularity data source**. Popularity is the sum of similarity
scores on edges pointing at an artist, computed from the archive during `build`. This
was a deliberate choice (see `docs/superpowers/findings/`): every external popularity
source imported a population mismatch with the similarity graph. It's then log-scaled
to 0–1 because raw counts are power-law distributed.

### Graph shape
Similarity is not mutual, so edges are **symmetrised** (keep the stronger score), then
pruned to the **largest connected component**. Keeping only that component guarantees a
path exists between any two artists the UI offers — so a "no path" result can *only*
come from user exclusions, never from missing graph structure.

### APG1 artifact
One little-endian binary file: header (`APG1` magic, version, N, E, metadata length) +
CSR arrays (`offsets`, `neighbours`, `scores`, `edge_types`) + a JSON metadata blob
(mbids, names, disambiguations, popularity). Loaded once into numpy typed arrays at API
boot; path queries touch no database and no network. `edge_types` is written but unused
in alpha (all edges behavioural). Versioned in S3 in production — **never a database**.

### Pathfinding (api, `pathfinding.py`)
Dijkstra over the in-memory `GraphStore`, pure/no I/O. Cost per edge (weights in
`api/…/config.py`, `w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`):
```
w_sim·(1−similarity) + w_jump·|Δpopularity| + w_floor·max(0, floor−pop_v)
  + w_avoid·avoidance + w_hop
```
Every path request is a **full regeneration** — no previous path is reused.

The **two-signal bypass** shapes the reroll differently per signal:
- **`dislike` ("not for me")** applies a soft penalty to the *neighbourhood* of the
  disliked artist (decays over `avoid_radius` hops) — steers around a stylistic region
  rather than offering a near-identical substitute.
- **`known` ("know them already")** relaxes the obscurity *floor* more aggressively than
  dislike — you've exhausted the popular route, so novelty is the goal.

Hard exclusions skip nodes entirely (but never the two endpoints). The API returns
artists only; **clips are resolved separately per card** (`GET /api/artists/{mbid}/track`,
Deezer → iTunes fallback, cached) so the path renders immediately.

### Configuration is env-driven, all tunables centralized
`ApiConfig` / `BuilderConfig` are the *only* place magic numbers live. Key API env vars:
`ARTISTPATH_GRAPH` (swap 5k dev graph for 75k prod without code changes),
`ARTISTPATH_CLIP_CACHE` (`memory` default — boots with **no AWS config** — or `dynamo`),
`ARTISTPATH_CORS_ORIGINS`. The API is testable without a real artifact or network: the
graph, search, and clip resolver are all injected into `create_app`.

## Workflow docs

This project uses the Superpowers workflow. Design docs live under `docs/superpowers/`:
`specs/` (designs), `plans/` (implementation plans), `findings/` (research/probe
results). Source comments reference these (e.g. "spec §4.3", "findings 6f") — consult
them when a decision looks arbitrary; it usually isn't.

## Security

Per global instruction: run the Snyk `snyk_code_scan` tool on new/modified first-party
code in a Snyk-supported language, fix any issues using the Snyk results, and rescan
until clean.
