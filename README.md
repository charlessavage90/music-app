# artistpath

Give it two artists. It builds you a listenable journey between them — a path of artist
cards, each with a 30-second clip, where every step sounds like a small sensible move
from the last. Miles Davis to Daft Punk in eight hops, without a jolt.

Two bypass signals reshape the route as you listen: **"not for me"** steers away from a
whole stylistic region, and **"know them already"** pushes toward the unfamiliar. All
path state lives in the URL, so any journey is shareable and Back undoes a bypass.

It is a rebuild of the idea behind *Boil the Frog*, which stopped working when the music
APIs it depended on were withdrawn.

**Status: pre-alpha, local only.** Not deployed. See [Documentation](#documentation) for
what is done and what is next.

---

## How it works

Three independent packages. The only thing they share is a binary file format.

| Package | What it does |
|---|---|
| **`builder/`** | Python. Crawls artist-similarity data and compiles it into one immutable binary graph artifact (`APG1`). Runs offline; produces the graph. |
| **`api/`** | Python / FastAPI. Loads the artifact into memory at boot and serves search, pathfinding, bypass rerolls, and clip resolution. |
| **`frontend/`** | React 19 + Vite + TypeScript. Consumes the API. |

The **`APG1` artifact is the contract** between builder and api — not shared Python code.
Both parse the format independently and share no modules.

Pathfinding is Dijkstra over an in-memory graph of ~75,000 artists, pruned by mutual
k-NN to a fraction of its original edge count (exact counts:
`docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`). A path query touches
no database and no network. Clips are resolved separately per card, so the path renders
immediately.

---

## Quick start

The project lives under OneDrive on Windows. **Prefix every `uv` command with
`UV_LINK_MODE=copy`** or it fails with hardlink errors. Each Python package has its own
`.venv`; `cd` into the package first.

You need a graph artifact to run the API. **No graph is committed** — `.gitignore`
excludes `builder/scratch/` and `*.bin`. On a fresh clone, copy the adopted 75k
artifact (or the archive, and rebuild in ~30 s) from another machine — identity by
the checksum in `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`. The
5k dev fixture is retired; the `fixture` command remains only for the committed
500-node test fixtures.

```bash
# terminal 1 — API on :8000 (boots the adopted 75k graph by default)
cd api
UV_LINK_MODE=copy uv run uvicorn artistpath_api.app:build_default_app \
  --factory --port 8000

# terminal 2 — frontend on :5173, proxying /api to :8000
cd frontend
npm run dev
```

### Tests

```bash
cd builder  && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd api      && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd frontend && npm test          # Vitest
cd frontend && npm run test:e2e  # Playwright — needs the API running on :8000
```

### Building a graph

```bash
cd builder
uv run artistpath-build bootstrap --out bootstrap.json
uv run artistpath-build crawl --bootstrap bootstrap.json --archive-dir ./archive
uv run artistpath-build build --archive-dir ./archive --out graph-v1.bin
uv run artistpath-build fixture --graph graph-v1.bin --out fixture.bin --size 500
```

The crawler only fills an archive of raw responses; `build` reads the archive and never
touches the network. Identical input produces byte-identical output.

---

## Documentation

**Start at [`docs/README.md`](docs/README.md)** — the documentation map. It classifies
every document by role (authoritative / active / complete / historical / narrative /
external) and tells you which are safe to cite.

Two things worth knowing before reading anything else:

- **All scoring and path-quality figures live in exactly one file**,
  `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`. Other documents cite it
  and do not restate its numbers.
- **Some documents are deliberately retained but superseded.** The map says which.

`CLAUDE.md` holds the working conventions for AI agents in this repo.
[`docs/how-we-map-similar-artists.md`](docs/how-we-map-similar-artists.md) is a readable
account of the modelling journey and the six ways it went wrong first — it is a journal,
not a source of truth.

---

## Licence and data

Similarity data comes from **ListenBrainz Labs** (CC0), keyed on MusicBrainz IDs. Clips
are resolved at request time from Deezer with an iTunes fallback; none are stored.
