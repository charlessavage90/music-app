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
`"dislike"` or `"known"` — the two signals shape the reroll differently (see the
spec §4.3). **The reason codes are the wire contract and have never changed**;
the frontend has relabelled the buttons behind them twice, and as of `LUX-1`
(2026-09) ships only one UI control, labelled **"Dig deeper"** (`known`) — the
`dislike` reason, the mechanism behind it, and the `?dislike=` URL parameter all
still exist and still resolve, they are just not reachable from the UI. Do not
rename the codes to follow the labels.

```json
// request
{"sources": ["<mbid-from>", "<mbid-to>"],
 "exclude": [{"id": "<mbid>", "reason": "dislike"}]}

// response
{"artists": [{"mbid": "…", "name": "Miles Davis", "disambiguation": "",
              "popularity": 0.80}, …],
 "stop_rule": "natural",
 "bypassed": [{"mbid": "…", "name": "Coleman Hawkins", "disambiguation": "",
               "popularity": 0.62}],
 "unresolved": ["<mbid-not-in-the-graph>"]}
```

`bypassed` carries the artists a bypass removed, in press order — they are
hard-excluded and so are absent from `artists`, and the route-history panel
reads their names from here (`LUX-2b`). `unresolved` carries any `exclude` id
that did not resolve to a node in the graph (a stale or bogus MBID on a shared
link): the request still succeeds and the path is built as if that press never
happened, but the id is reported rather than silently dropped. Both are
additive — a client that ignores them is unaffected.

`stop_rule` reports how the journey got its middle (F1; design
`docs/superpowers/specs/2026-07-25-f1-minimum-stop-design.md`):
- `"natural"` — the least-cost path already had at least one stop.
- `"forced"` — the two artists were neighbours, so a detour was inserted.
- `"adjacent_only"` — the two are neighbours and nothing connects them both;
  the two-card path is returned as-is.

- `422` if `sources` is not exactly two (alpha supports two; the list shape is
  future-proofed for multi-artist pathing).
- `404` if a source artist is unknown.
- `409` if hard exclusions disconnect the two endpoints.

The response contains artists only; clips are resolved separately per card so
the path renders immediately (spec §5.2).

### `GET /api/artists/{mbid}/track?index=<n>`
Resolve a 30-second clip for one artist: Deezer first, iTunes fallback,
cached. `204` when no clip is available (the card renders unplayable but the
path is unaffected).

**`204` also covers failure, never `5xx`.** A clip is decorative, so a
catalogue that is down, rate-limiting, or missing the track degrades to a
silent card. Only the *identity* of each candidate track is cached; the signed
preview URL is short-lived and is re-resolved on every request, so a repeat
view costs one lookup per card where it previously cost none. The measured
signature lifetime lives in
`docs/superpowers/2026-07-25-gate1-clips-and-ux-execution-log.md` §15 and is
cited, never restated here.

`index` (default `0`) selects among the candidate tracks the resolver found for
this artist (`LUX-3`) — "try another track" on the card increments it. The
response reports `candidate_count`, the total number of playable candidates,
so the frontend knows when there is nothing left to cycle to rather than
guessing.

```json
{"preview_url": "https://…", "title": "So What", "cover_url": "https://…",
 "candidate_count": 3}
```

**The out-of-range behaviour is deliberately asymmetric.** A negative `index`
is rejected with `422`: the frontend never produces one on its own, so a
negative value can only mean a bug on the caller's side, and silently wrapping
it (Python's modulo would turn `-1` into the last candidate) would hide that
bug rather than surface it. A positive `index` past `candidate_count` instead
**wraps** (`index % candidate_count`): the frontend holds the index in
component state and a stale one is normal — after a rebuild, a resolver
returning fewer candidates than before, or a page loaded from a cached URL —
so wrapping keeps "try another" trivially correct instead of handing the user
an error they cannot act on.

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `ARTISTPATH_GRAPH` | `../builder/scratch/graph-t15-tiebreakfix.bin` | Which artifact to load; the adopted artifact, flipped at each adoption. |
| `ARTISTPATH_CLIP_CACHE` | `memory` | `memory` (local dev — no AWS needed) or `dynamo` (production). |
| `ARTISTPATH_CLIP_TABLE` | `artistpath-clips` | DynamoDB table name when the cache is `dynamo`. |
| `ARTISTPATH_GRAPH_SHA256` | unset | Verified at boot, so a wrong artifact refuses to start. Optional locally, **required in production**. Take it from the artifact's manifest sidecar — never transcribe it by hand (`DEP-24`). |
| `ARTISTPATH_CORS_ORIGINS` | empty | Allowed browser origins. Empty means none, deliberately — see `RMD-6`. |
| `ARTISTPATH_ORIGIN_SECRET` | unset | Shared secret proving a request came via CloudFront rather than direct to the origin. |

The last three were missing from this table until 2026-07-27 while being real fields on
`ApiConfig`; read defaults from `config.py`, not from a copy here.

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

> On Windows, prefix `uv` commands with `UV_LINK_MODE=copy`. Hardlinking fails at
> `C:\dev\music-app`; uv falls back to copying by itself, so this suppresses the
> warning rather than being required.

## Cost-function weights

Path quality is governed by the weights in `ApiConfig` (`config.py`), which is
their **only** definition — read the defaults there rather than from a copy
here. They started as the values validated in stage 1: a tuned starting point,
not final. Real tuning is a listen-and-adjust activity against the full 75k
graph.

Every popularity-derived weight is in **raw** popularity currency, not
percentile; the identifiers say so. See CLAUDE.md, "Quantities carry their
currency in their name".
