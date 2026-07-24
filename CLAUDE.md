# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Orient here first

| Question | Answer |
|---|---|
| **Which documents can I trust?** | [`docs/README.md`](docs/README.md) — the documentation map. It classifies every doc by role and names which are superseded. **Read it before citing anything in `docs/`.** |
| **Where do scoring / path-quality figures live?** | Exactly one file: `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`. Cite it by section; **never restate its numbers anywhere else.** Its §6 marks 27 prior claims upheld/overturned/unresolved. |
| **What is the next action?** | **Track 2 of the repair+retune design** — the cost-function retune. Read `docs/superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §4 and the execution log `docs/superpowers/2026-07-23-repair-and-retune-execution-log.md`. Track 1 (the §2.8 tie-break fix) is DONE and adopted — artifact identity in `docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`. The Phase 1 log's §2 remains the defect record; its §2.12 diagnosis (cost-function problem, not graph problem) is what Track 2 acts on. |
| **Are the hub / payload figures safe to use?** | **No, and neither is "popularity" as a proxy for fame.** Three quantities that get used interchangeably and are not: **degree ≠ fame** (§2.6 — `top1pct_degree_frac`, "payload", `degree_hub_penalty`, `w_degree_hub` are all top-1%-by-*degree*; they were named `hubfrac` / `hub_penalty` / `w_hub` until 2026-07-23, and older documents and every script under `builder/analysis/` still say so — mapping in `builder/analysis/README.md`); **popularity ≠ fame** at the top, where a lo-fi producer and a Beatle score alike (§2.11); and **raw popularity ≠ percentile** — `pop_raw` is a value, never a rank; see §2.12 for the extent of the gap. Each has already caused a wrong conclusion here. **Check which currency a claim is in before acting on it.** |
| **What's the overall plan?** | `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` — three gates: personal use → friends & family → public. |
| **Anything waiting to be tested by hand?** | `docs/superpowers/TEST-QUEUE.md` — the async use-the-app queue. `closeout` appends to it; `session-start` reads it and flags stale entries. It catches the defect class tests structurally cannot. |
| **What does the owner mean by "better"?** | `docs/superpowers/WHAT-GOOD-LOOKS-LIKE.md` — calibration for the blind listening test, this project's strongest evidence class. Read it before running one or interpreting a verdict. It records **preference, not evidence** — never treat it as criteria. |
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

# dev server — boots the ADOPTED 75k graph by default (ApiConfig.graph_path);
# ARTISTPATH_GRAPH overrides:
uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

**No dev or production graph artifact is in git.** `.gitignore` excludes
`builder/scratch/` and `*.bin`, with only `!**/tests/fixtures/*.bin` exempt — so a fresh
clone has the two 500-node test fixtures but none of the dev graphs. (The `**/` matters
and was wrong until 2026-07-22: a gitignore pattern containing a slash is anchored to the
file's own directory, so the previous `!tests/fixtures/*.bin` exempted nothing and the
fixtures were silently uncommitted.) On a fresh clone, copy the adopted 75k artifact (or
the archive, and rebuild in ~30 s) from another machine — identity by the checksum in
`docs/superpowers/findings/2026-07-23-tiebreak-fix-adoption.md`. The 5k dev fixture is
retired; the `fixture` command remains only for the committed 500-node test fixtures.

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

### Quantities carry their currency in their name
**Any popularity- or degree-derived quantity in shipped code names its basis in its
identifier.** `pop_raw` is the stored 0–1 value; `pop_pctl` is reserved for a
percentile and must not be used for anything else. Degree-derived quantities say
*degree* — `degree_hub_penalty`, `w_degree_hub`, `top1pct_degree_frac`,
`top_degree_node_set`. This is not tidiness: reading one of these currencies as another
has produced three separate wrong conclusions here (§2.6, §2.11, §2.12 of the Phase 1
log). **New quantities follow the convention** — in particular the percentile machinery
a Track 2 adoption would add.

Two names are exempt because they are **wire contracts, not identifiers**: the `popularity`
key in the APG1 metadata blob (renaming it invalidates every existing artifact) and the
`popularity` field in the API's JSON response (the frontend consumes it). Both are
commented at their definition.

Shipped code also keeps a few **read-only aliases** under the pre-2026-07-23 names, purely
so the frozen probe scripts in `builder/analysis/` keep executing. Never write new code
against an alias; the mapping table is `builder/analysis/README.md`. They are deferred for
removal, not permanent — condition in the repair+retune execution log.

**A rename's blast radius includes every document that *describes* the quantity, not only
those that *use the name*.** So the check after renaming is **not** "does the old
identifier still appear anywhere" — it is "does every place that should describe this
quantity still describe it correctly, **including by omission**." A grep for stale names
cannot find a name that is not there. This is not hypothetical: the 2026-07-23 rename left
`.claude/agents/ml-graph-analyst.md` describing the cost function with a whole term
missing, and the sweep that searched `.claude/` for stale identifiers passed it clean,
because the defect was the absence. That half cannot be mechanised, which is the argument
**for** the `doc-auditor` step in `closeout`, not against it.

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
Dijkstra over the in-memory `GraphStore`, pure/no I/O. Cost per edge — the weights and
their defaults live in `ApiConfig` (`api/…/config.py`) and are **cited, never restated
here**; two copies of them went stale once already:
```
w_sim·(1−similarity) + w_jump·|Δpop_raw| + w_floor·max(0, floor_raw−pop_raw_v)
  + w_avoid·avoidance + w_degree_hub·degree_hub_penalty + w_hop
```
Both popularity terms are in **raw** currency, and `floor_raw` is the only
depth-graduated device in the function — everything else is static per request.
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
`ARTISTPATH_GRAPH` (overrides the default graph path — the default is the adopted 75k
artifact itself, so this is for pointing at a *different* artifact, not for a dev-vs-prod
swap),
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

**The factor table needs a third section, because it cannot see a dormant term.** The
table asks *which knobs did I turn* — and the confound that nearly broke the Track 2 sweep
was a knob nobody turned.

> **Held constant, and why each is genuinely constant under the intervention.** Enumerate
> every term the comparison holds fixed, and for each, state why the intervention cannot
> change its state. A term that is inert in the baseline *for a reason the intervention
> removes* is not a constant — it is an uncontrolled variable that appears only in the
> arms that succeed.

Worked example: `specs/2026-07-23-track2-preregistration.md` §0. `w_floor` never fires in
production because `w_jump` stops paths dipping below the floor — and diving below the
floor is precisely what the sweep's successful arms do. Left alone it would have switched
itself on in the winners only, making every "one-knob" attribution in the sweep wrong.
Caught before the sweep rather than after, which is the difference between a design
correction and a retraction.

**No experimental arm runs until a pre-registration is committed.** It fixes the primary
outcome, the effect size, the pair or sample set, and the read of every possible result
including the null. The git commit timestamp is the evidence that it preceded the result —
that is the part that cannot be reconstructed afterward. Worked example:
`specs/2026-07-23-track2-preregistration.md`. The discipline is credited in the Phase 1 log
(§2.13 C5) with turning a disappointing null into an actionable one and with saving a blind
listen that would have burned the owner's ear on nothing.

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

### How to present results to the owner

**"Don't draw conclusions, leave the decision to me" does not work as an instruction, and
this repo does not use it.** Every presentation selects and frames, and both are
inferential. A session told to withhold conclusions still makes them — in which table
leads, which figure is bolded, which sentence opens the section — where the owner cannot
challenge them, because they were never stated. Phase 2's "no candidate beats capfix" was
a conclusion delivered as a summary, resting on selection that dropped the data
contradicting it.

**Conclude explicitly, label it, and still decline to decide.** Four parts, in this order:

1. **Measured** — the numbers, no adjectives. Tables belong here and nowhere else.
2. **What I infer from it** — plainly labelled as inference, and **in plain language.**
   Someone who does not know what Adamic–Adar measures must be able to follow this section
   and disagree with it. If a claim cannot survive being restated without its metric name,
   that is worth knowing before it reaches a decision.
3. **Weakest link** — the load-bearing assumption, and what would falsify it. State which
   parts you would defend and which you would abandon cheaply.
4. **Options and their consequences** — not a recommendation wearing a finding's clothes.

**The summary must name whatever cuts against it.** A summary that omits contradicting
data is wrong even when every number in it is right.

**Exception — blind evaluations.** A session running a blind test says nothing beyond the
bare mechanics, and is held ignorant of the expected outcome. There, the whole point is
that no framing reaches the owner at all.

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
