# artistpath-builder

Crawls artist similarity data and compiles it into a single immutable binary
graph artifact (`APG1`). Runs offline, produces the graph, and is then done —
nothing here is part of the running app.

Independent of the `api/` package: the `APG1` **format** is the contract, not
shared code. Both packages parse it separately and are kept in lockstep by hand.

## The one thing not to get wrong

**Never delete the archive.** `crawl` writes raw JSON responses into
`--archive-dir` and nothing else; `build` reads only that archive and never
touches the network. The archive is therefore the entire rebuild guarantee — as
long as it exists, any graph can be rebuilt from scratch without touching the
network, and the crawl (hours, rate-limited, tens of thousands of artists) never
has to run again. Lose it and the only way back is to re-crawl.

The graph artifacts themselves are gitignored and disposable. The archive is
neither.

## The pipeline

Four commands, each reading the previous one's output:

```bash
uv run artistpath-build bootstrap --out bootstrap.json
uv run artistpath-build crawl  --bootstrap bootstrap.json --archive-dir ./archive
uv run artistpath-build build  --archive-dir ./archive --out graph-v1.bin
uv run artistpath-build fixture --graph graph-v1.bin --out fixture.bin --size 500
```

- **`crawl` is resumable and safe to interrupt.** It checkpoints to
  `--checkpoint` (default `./checkpoint.json`) and rebuilds its queue as
  `discovered − done` on restart, which also retries anything that failed last
  time. Ctrl-C is a normal way to stop it. `--target N` caps how many artists are
  **fetched** (`CEX-2`, 2026-08-08 — it capped how many were *discovered* before
  that, which discarded the frontier past the cap and is `ULC-F3`);
  `--s3-bucket` / `--s3-prefix` put the archive in S3 instead of on disk.
- **`refrontier` repairs a checkpoint whose frontier was lost** (`ULC-F3`), by
  rebuilding `discovered` from the archived responses. Offline. Run it before a
  `crawl` that is meant to resume but reports nothing to do.
- **`build` is offline by construction.** `tests/test_replay.py` builds twice
  from one archive, the second time with a fetcher that raises on any request,
  to prove it never reaches the network.
- **`fixture` exists only for the two committed 500-node test fixtures.** The 5k
  dev fixture is retired — the API boots the real adopted artifact.

## Byte-identical output is a requirement

Identical input must produce an identical artifact (design spec §9). Every
ordering decision is explicit: IDs are assigned in sorted-MBID order and ties
break on lowest MBID. If you change anything that affects ordering, that is a
deliberate act with a rebuild and a re-adoption behind it, not a refactor.

## `build` currently rejects a production rebuild, on purpose

`acceptance.py` runs at the emission point and **raises** rather than writing a
bad artifact. One of its checks — that every artist has a name — fails against
the current data, because the adopted artifact contains a number of nameless
artists (the count and its source are in `acceptance.py`'s own header). Whether
to drop them or backfill names from another source is an open decision for the
owner.

So a full rebuild is blocked until that is settled. **Weakening the check to get
a build out is the one wrong response**; it is doing exactly its job.

## Tests

```bash
UV_LINK_MODE=copy uv run --extra dev pytest -q
UV_LINK_MODE=copy uv run --extra dev pytest -q -k crawl
```

The `UV_LINK_MODE=copy` prefix is used on Windows because hardlinking fails at
`C:\dev\music-app`. uv falls back to copying by itself, so it suppresses the
warning rather than being strictly required.

## Where the rest lives

Deliberately not restated here, because a second copy drifts:

- **Tunables and their defaults** — `BuilderConfig`, which is their only
  definition.
- **Graph shape** (mutual k-NN, symmetrisation, largest connected component) and
  how popularity is derived — `CLAUDE.md`, "Architecture and key concepts".
- **Measured figures of any kind** — `docs/superpowers/findings/`, cited by
  section. Never quote a number from here or from a plan.
- **`analysis/`** — frozen one-off probe scripts, each with its own README.
  `analysis/README.md` maps the pre-2026-07-23 identifier names still used there
  onto the current ones.
