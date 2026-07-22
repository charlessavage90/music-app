# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Orient here first

| Question | Answer |
|---|---|
| **Which documents can I trust?** | [`docs/README.md`](docs/README.md) — the documentation map. It classifies every doc by role and names which are superseded. **Read it before citing anything in `docs/`.** |
| **Where do scoring / path-quality figures live?** | Exactly one file: `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`. Cite it by section; **never restate its numbers anywhere else.** Its §6 marks 27 prior claims upheld/overturned/unresolved. |
| **What is the next action?** | **Gate 1, Phase 1 — and it needs planning first.** Phase 2 is COMPLETE (adopted `capfix`, 2026-07-22; execution log §16). Phase 1 leads with **C3** — `w_floor` is a no-op and `known` degrades to a bare hard exclusion, a pathfinding defect, not a UX item — then clips (C1, C2), then frontend UX. Two items carry in from Phase 2 with success conditions; see the roadmap's Phase 1 section. |
| **What's the overall plan?** | `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` — three gates: personal use → friends & family → public. |
| **Is there project memory?** | Yes, outside the repo: `~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app/memory/`. `MEMORY.md` indexes it. Memory holds pointers and preferences, **not figures**. |
| **Specialist help?** | `.claude/agents/ml-graph-analyst.md` — analysis-only subagent for graph, scoring and metric questions. No `Edit` tool by design. |

**Never use as context:** `docs/how-we-map-similar-artists.md` (a narrative journal) and
anything under `docs/reference/` (third-party material). Neither is maintained as
project documentation.

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

# dev server against the local 5k graph:
ARTISTPATH_GRAPH=../builder/scratch/graph-5k.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

**No dev or production graph artifact is in git.** `.gitignore` excludes
`builder/scratch/` and `*.bin`, with only `!**/tests/fixtures/*.bin` exempt — so a fresh
clone has the two 500-node test fixtures but none of the dev graphs. (The `**/` matters
and was wrong until 2026-07-22: a gitignore pattern containing a slash is anchored to the
file's own directory, so the previous `!tests/fixtures/*.bin` exempted nothing and the
fixtures were silently uncommitted.) Build `graph-5k.bin` locally from an archive with the `build`
and `fixture` commands above, or copy it from another machine. Adopted 75k artifacts
are identified by recorded checksum in `docs/superpowers/findings/`, since they cannot
be committed.

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
Similarity is not mutual, so edges are first filtered by **mutual k-NN** — an edge
survives only if each endpoint ranks the other in its top-k — then **symmetrised** (keep
the stronger score), then pruned to the **largest connected component**. Mutual k-NN is
what actually bounds degree; the legacy alternative capped each artist's own list before
symmetrising, which bounds nothing afterwards. It was deleted in Phase 2 and now raises. Keeping only that component guarantees a
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

### Writing and reviewing plans here

Five review rounds on the Phase 2 plans produced ten findings, and nine were two shapes.
Both have cheap structural fixes; neither is caught by writing more carefully.

**1. Comparisons with an uncontrolled variable.** Most findings were two things compared
that differed in more ways than the author believed — a baseline anchored on the wrong
arm, an artifact built by different code, variants differing by two knobs when the
comparison assumed one.

> **Any plan comparing variants must contain a factor table**: one row per variant, one
> column per knob that varies, and the isolating baseline named per row.
>
> **A variant's baseline is the variant differing by exactly one column.** If none exists,
> either build one or state explicitly that this is a package comparison and what it
> therefore cannot tell you.

The table is what makes this mechanical. You don't have to *notice* a confound — you read
across the row and count the differences. This is not hypothetical rigour: a two-knob
confound survived three rounds of prose review, including one written immediately after
the reviewer had named that exact pattern. The table found it in a single pass.

**2. Documents asserting things about the world that aren't true.** Plans have referenced
functions that did not exist yet, and cross-references have gone stale after renumbering.

> **Before executing a plan, grep every function, file, and config value it names.**
> Anything that doesn't resolve is either not-yet-built — state the dependency — or stale.

**3. Plans over ~8 tasks must name their own handoff points.** Subagent-driven execution
caps how *wide* the controller's context gets — the code stays out — but not how *long*.
The controller still reads one report per task and decides on most of them, so its context
grows with **task count**, not with effort or delegation quality. Past roughly 8–12 tasks
it is in long-context territory however well the work was delegated.

> Choose the handoff seams **at authoring time**, where a track's output is a committed
> artifact rather than a live understanding — then hand off there, retire the session, and
> start the next track fresh. A **material mid-flight amendment is also a seam**: there is a
> new governing document, and the next session reads it cold, which is the condition the
> amendment was written for.

A boundary you planned is cheap. One you discover at task 15 is expensive, and it gets
deferred past the point it should have happened because handing off then feels like an
admission. Phase 2 had a perfect seam at the Track A/Track B split and did not use it.

**What makes handoffs cheap:** append to the retained execution log **per task**, not only
at closeout. Decisions and reasoning, not narration. That is what makes sessions
interchangeable rather than making one of them precious — and "the controller is warm" is
never a reason to keep going, since a plan only its executor can continue is a plan that
was under-recorded.

**The degradation tell is a completeness failure, not a fluency one.** Watch for a session
having to be *asked* for figures it already computed, or an item quietly dropping out of a
tracking document. Both have happened here; both preceded any more obvious symptom.

**How to ask for a plan review.** "Review this plan" finds prose problems. **"Check this
plan's claims against the repo"** finds the confounds. Every high-value finding in Phase 2
came from a reader with the *code* open, because a plan can be perfectly self-consistent
and still wrong relative to `config.py`. Same cost, very different yield.

### Two rituals bracket every chunk of work

Both are mechanical and cheap by design — they ask *did we leave a mess* and *am I
oriented*, never *did we do the right thing*. That second question is a review, and
reviews are rare and targeted here.

- **`session-start`** (`.claude/skills/session-start/`) — run it **before** doing
  substantive work in a fresh session: what governs this work and what supersedes what,
  which decisions are closed, whether another session is live in this tree, and which
  gates would stop you. Also carries the two checks that can only fire at the start —
  the cheapest-experiment scope check, and verifying one claim before building on a
  report.
- **`closeout`** (`.claude/skills/closeout/`) — run it **after** finishing significant
  work: distil the retained execution log, give every deferral a success condition, check
  config defaults were actually flipped, sweep for orphaned modules and vacuous tests,
  queue the use-the-app test, and finalise git.

Closeout writes; session-start reads. Keep them in sync — if you change what one
produces, change what the other consumes.

### When to recommend a review

**Reviews are never automatic.** When a trigger below is reached, *recommend* a partial or
team review to the owner and say what decision it would change — then wait. Running one
unasked is how a project ends up relitigating its direction weekly.

The filter, before recommending anything: **what decision would this review change?** If
you cannot name one, do not recommend it. And **if you can name the specific worry, it is
a targeted single-agent question, not a team** — a team review is for finding what you do
not know to ask about.

- **`ml-graph-analyst`** — derivation, never judgement. Recommend it before adopting a
  normalisation, ranking or rescaling change; when a comparison spans graphs of different
  structure; when a metric moves and you cannot tell property from bug; when a claim about
  the graph is about to enter the record; or to critique an analysis before acting on it.
  Never for interpreting evidence that feeds a human decision.
- **Team review** (architect, security, quality, frontend, plus the graph analyst only if
  a scoring question is open) — **at gate boundaries, after a period of real use.** Gate 1
  → 2 and Gate 2 → 3. Staff the frontend explicitly: three backend-focused reviewers once
  missed an entire defect class that twenty minutes of use found.
- **Not triggers:** phase or plan completion, a merge, a milestone, or feeling uncertain
  about direction. Those get `closeout`. Uncertainty about direction is the one thing a
  team review reliably makes worse.

### How work lands: pull requests, always

Development here is **pull-request driven against `origin`
(`github.com/charlessavage90/music-app`, default branch `main`)**. Nothing is committed
directly to `main`.

- **Branch off `main`** for any piece of work, and **push the branch early** — the first
  commit, not the last. Work that exists only in this working tree is unbacked: the repo
  lives under OneDrive, which syncs files but is not a substitute for a remote, and a
  phase's worth of commits is expensive to lose.
- **Open the PR when the work is coherent, not when it is finished.** A draft PR gives the
  work a durable address that survives any session ending.
- **The PR body is where a reviewer picks up context** — see the `closeout` skill's D5 for
  what it carries: a link to the retained execution log, gate outcomes *including
  failures*, deferred findings with their success conditions, checksums for any adopted
  artifact (they are gitignored and cannot be committed), and what is closed and should
  not be re-litigated.
- **Merge via the PR**, so `main`'s history records how work arrived rather than just what
  arrived.

## Security

Per global instruction: run the Snyk `snyk_code_scan` tool on new/modified first-party
code in a Snyk-supported language, fix any issues using the Snyk results, and rescan
until clean.
