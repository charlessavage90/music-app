# artistpath-api

The path engine and HTTP API for the artist-path app. Loads the graph
artifact into memory at startup and serves artist-path search, two-signal
bypass rerolls, autocomplete, and 30-second clip resolution.

Independent of the `builder/` package: it reads the `APG1` artifact format
directly (the format is the contract, not the builder's code).

## Endpoints

### `GET /api/artists/search?q=<query>`
Autocomplete over artist names, accent-insensitive, ranked by popularity.

```json
[{"mbid": "…", "name": "Radiohead", "disambiguation": "", "popularity": 1.0}]
```

### `POST /api/path`
Build a path between two artists. `exclude` entries carry a `reason` of
`"dislike"` ("not for me") or `"known"` ("know them already") — the two
signals shape the reroll differently (see the spec §4.3).

```json
// request
{"sources": ["<mbid-from>", "<mbid-to>"],
 "exclude": [{"id": "<mbid>", "reason": "dislike"}]}

// response
{"artists": [{"mbid": "…", "name": "Miles Davis", "disambiguation": "",
              "popularity": 0.80}, …]}
```

- `422` if `sources` is not exactly two (alpha supports two; the list shape is
  future-proofed for multi-artist pathing).
- `404` if a source artist is unknown.
- `409` if hard exclusions disconnect the two endpoints.

The response contains artists only; clips are resolved separately per card so
the path renders immediately (spec §5.2).

### `GET /api/artists/{mbid}/track`
Resolve a 30-second clip for one artist: Deezer first, iTunes fallback,
cached. `204` when no clip is available (the card renders unplayable but the
path is unaffected).

```json
{"preview_url": "https://…", "title": "So What", "cover_url": "https://…"}
```

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `ARTISTPATH_GRAPH` | `../builder/scratch/graph-t15-tiebreakfix.bin` | Which artifact to load; the adopted artifact, flipped at each adoption. |
| `ARTISTPATH_CLIP_CACHE` | `memory` | `memory` (local dev — no AWS needed) or `dynamo` (production). |
| `ARTISTPATH_CLIP_TABLE` | `artistpath-clips` | DynamoDB table name when the cache is `dynamo`. |

The graph loads once at startup into numpy typed arrays; path queries touch no
database and no network. With the default `memory` cache the server boots and
serves paths **without any AWS configuration** — only the track endpoint needs
Deezer/iTunes reachability, and clips degrade to unplayable cards if missing.

## Running

```bash
# tests
UV_LINK_MODE=copy uv run --extra dev pytest -q

# dev server — boots the adopted 75k graph by default
uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

Then, e.g.:

```bash
curl "http://localhost:8000/api/artists/search?q=miles%20davis"
curl -X POST http://localhost:8000/api/path -H "content-type: application/json" \
  -d '{"sources":["<from-mbid>","<to-mbid>"],"exclude":[]}'
```

> On Windows with the project under OneDrive, prefix `uv` commands with
> `UV_LINK_MODE=copy` to avoid hardlink errors.

## Cost-function weights

Path quality is governed by weights in `config.py`, starting from the values
validated in stage 1 (`w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`). These are a
tuned starting point, not final — real tuning is a listen-and-adjust activity
against the full 75k graph.
