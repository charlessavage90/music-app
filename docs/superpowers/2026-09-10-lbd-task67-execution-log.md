# `LBD-` Tasks 6–7 — retained execution log

**Role: RETAINED EXECUTION LOG for the `LBD-` build stage (plan Tasks 6 and 7, under
`LBD-AM4`). ACTIVE. Owns no figures** — `builder/analysis/2026-09-10-lbd-supply/README.md`
owns the build-stage figures and `builder/analysis/2026-09-08-lbd-similarity/README.md` §6c
owns the threshold curve. Decisions and reasoning, not narration; appended per task so a
successor can pick up at any seam. Continues
[`2026-09-08-lbd-task34-execution-log.md`](2026-09-08-lbd-task34-execution-log.md), which
closes at the Task 4 owner stop.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
with `LBD-AM4` (its §10 block and §12 row). The plan's Tasks 6–7 are executed as amended;
the plan is not edited. Branch `lbd-build`, worktree `C:\Users\charl\worktrees\music-app-lbd-build`.

## Session opening — what was verified before anything was written

- **Repo state:** `origin/main` at `8aef76a` (PR #113 merged 2026-09-10); no other session's
  changes in the main tree; worktree cut from `origin/main`.
- **Checksums, all matched the handoff's record before any file was read:** `T.parquet`
  `03d47b05…`; `A0.parquet` `f9bd1f83…`; `A2.parquet` `34f92de7…`; `cxr_added_mbids.txt`
  `bfed95ef…`; `cxr_preexisting_mbids.txt` `768054b7…`; `cxr_residual_mbids.txt` `fa8d85cc…`;
  `artist_identity.parquet` `02b4c8dd…`; `graph-cxa-adopted.bin` `bc0431c4…` against its
  sidecar. `A3.parquet` was **not** verified because nothing here reads it (`LBD-AM4-2` bars
  it from building).
- **Grepped before use** (the plan's own claims list, re-resolved in this worktree):
  `FIELD_MBID/NAME/SCORE/COMMENT` and `ListenBrainzSource` (`name`, `edge_type`,
  `request_url`, `parse`, `_rows`) — `sources/listenbrainz.py:19-22, 54-100`;
  `harvest_identities` — same file, reads `name`/`comment` from neighbour rows;
  `similar_prefix` — `pipeline.py:131`; `build_from_archive` — `pipeline.py:169`, the
  nameless drop at 235–246, the `PopulationNotCensused` guard at 303–320, the cap ranking on
  unclipped strengths at ~380; `CANDIDATE_ALGORITHM` — `config.py:26`; `drop_unlistenable`
  (243), `unlistenable_list_path` (259), `require_fame` (132), `union_top_j`/`union_degree_ceiling`
  (107–108); `load_unlistenable_list(algorithm, override_path)` — `unlistenable_drop.py:151`
  and its `UnlistenableList.censused_mbids`; `LocalArchive` — `archive.py:28`; the bridge-arm
  config — `dcf_ceiling_sweep.py:401-407` (`algorithm=CANDIDATE_ALGORITHM`, `require_fame=False`,
  `drop_unlistenable=ulf_path is not None`, `unlistenable_list_path=ulf_path`) and its
  `ReadOnlyArchive` (110–132) and `verify_against_sidecar` (135–155); the `c2a` degree SQL
  — `lbd_reads.py:219-234`, reused verbatim for the curve.
- **One thing the plan says that is no longer how it reads:** Task 6 pins
  `unlistenable_drop_algb_20260805.json`. That is the current default, it censuses 75,000
  artists, and over the fixed population it leaves 29,837 uncovered and would refuse. The
  bridge arms' `20260809` payload is what covers `P`; `LBD-AM4-3` records the measurement.

## Step 1 — `LBD-AM4`, written and committed before anything was emitted

**The decision that shapes everything else: the population is fixed to the `CXA` node set.**
The plan's Task 7 builds over whatever population the arm's pair table names, which the
review measured as a confound in the flattering direction (`LBD-X2`). The ceiling probe had
already shown the alternative: its §4 bridge arms applied the re-censused drop list through
the shipped override and reproduced the `CXA` population to the node, landing on `CXR-P2`'s
ruler. The emitter here does the same thing one step earlier — it never writes an artist or
a neighbour outside `P` — so the drop lists become inert by construction rather than by
luck, and each arm differs from the bridge control in the data alone.

**Measured before writing, not assumed:** the `20260809` payload's censused set covers all
88,685 nodes (0 uncovered), and each of the three drop lists intersects `P` in 0 artists.
So `drop_unlistenable=True` through the override is safe and holds the served map's
filtering constant; this supersedes `LBD-X3`'s `False` for `P` only, and the amendment says
why `LBD-X3` is still right for any other population.

**Why `A3` is barred and `A1` is merely not built.** `A3`'s partner counts (README §6) put its
archive at both directions of every row of `T` held as Python objects in the builder's first
pass — not buildable here — and its pair-level movement on the stratum this track exists for
is within a tenth of a point of `A2`'s. `A1` did not clear `LBD-G2` on the whole set at the
pair level, and a graph-level figure is bounded above by the pair-level one, so building it
cannot change the decision; it stays available.

**Why the population restriction is applied after the rank cut, not by re-ranking inside
`P`.** The arm is defined by §1 as a filter and window over `T` on the full corpus; re-ranking
inside `P` would make "`A0`" a different object from the one `LBD-C2a` was read on. The
emitter filters the sha-pinned derived parquet, so the arm keeps its meaning and the
population becomes the one column that moved between Task 4's read and this one.

**The threshold curve is descriptive and says so three times** in the amendment, because the
obvious misreading — "the curve picked threshold 2" — is a decision the owner has not made.
Its green check is built in: threshold 10 / limit 100 must reproduce README §6's `A0` row and
threshold 0 / limit 100 its `A2` row, or the instrument is wrong.

**Where outputs land:** `C:\unsung-fast\lbd-archives\<arm>\` (NVMe; 88k small files per arm
is the wrong shape for the spinning disk the plan named), consistent with the staging
approval the 2026-09-10 handoff records.

## Step 2 — the threshold curve: one instrument, one crash, one rerun

**Design.** `rank()` inside an `mbid0` partition is unchanged by filtering away lower-scored
rows, so one window pass over `T` serves all eight thresholds; the sixteen cells are filters
on `(score, rank)` and a single `GROUP BY` with sixteen `FILTER` clauses. The instrument's
green check is built in and is a refusal: the (10, 100) cell must reproduce `A0`'s committed
`c2a.json` and (0, 100) `A2`'s on all four sets, or nothing is written. Pairs in `T` were
checked unique and oriented `mbid0 < mbid1` on `A0` (0 rows the other way, 0 duplicates), so
`count(*)` per direction is the distinct-partner count `lbd_reads.py` computes with
`count(DISTINCT …)`.

**The first attempt died, and the cause is recorded as a trap.** Launched 19:12 at a 16 GB
limit and DuckDB's default 24 threads. At 19:22 the second `emit_archive.py` attempt (a
per-artist `list(… ORDER BY …)` aggregation at an 8 GB limit) ran out of its own memory
limit; at 19:24 the curve's Python process died with an access violation
(`0xc0000005`) inside `_duckdb.cp312-win_amd64.pyd` — Application log event 1000 — with
nothing on stderr, leaving `ranked_P.parquet` without a footer. Two DuckDB processes at a
combined nominal 24 GB on a 32 GB machine, one of them at the moment of its own OOM, is the
only thing that changed. **Rerun alone at 12 GB and 8 threads** (19:27); the script's
docstring now says RUN ALONE. Nothing heavy runs beside it until it finishes.

## Step 3 — Task 6, the emitter: what was decided

- **`LbdBulkSource(ListenBrainzSource)` with `name = "lbd"`**, `request_url` raising. The
  algorithm token is `CANDIDATE_ALGORITHM` (the `ALG-B` string, `filter_True` included)
  because the three drop-list loaders key on it — the token names the drop-list lineage,
  never the arm; the arm's tokens live in the archive root's `MANIFEST.json`.
- **Payload rows carry exactly the four `FIELD_*` keys** (`artist_mbid`, `name`, `comment`,
  `score`). The real endpoint also returns `type`, `gender` and `reference_mbid`; the
  builder reads none of them (`sources/listenbrainz.py`), so they are not fabricated.
- **The population filter is applied to the derived parquet, after the rank cut.** Counts
  are recorded in the manifest: of `A0`'s rows, those with both ends in `P`, one end, neither.
- **Identity.** All but 10 of the 88,685 have a row in Task 1's identity frame; all 10 are
  absent from `A0` anyway, so `A0`'s archive has no nameless artist. The 10 MBIDs are listed
  in the manifest for the README.
- **Memory shape, twice corrected.** Version 1 pulled the filtered pairs into Python
  (fine for `A0`, wrong for `A2`); version 2 aggregated per-artist lists inside DuckDB and
  ran out of memory beside the curve; version 3 streams one sorted
  `(artist, -score, partner)` query and groups consecutive rows — a sort spills cleanly.
  `A0` was emitted by version 1 and re-emitted by version 3; the archive digest over every
  payload is compared between the two runs before `A2` is emitted (determinism check, recorded
  in the README).
- **Snyk** (the MCP connected this session): one Medium, CLI path interpolated into DuckDB
  SQL — the class the `builder/analysis/` deferral in `NEXT.md` names. Fixed by binding the
  path as a query parameter (`read_parquet(?)`); rescan clean. The curve script has the same
  finding and gets the same fix **after** its run, so the `script_sha256` its output records
  is the code that ran (commit `57dfb70`).

**Step 2, result.** The rerun finished in 9.6 min, green on both reproduction checks. Recorded as
§6c of the Task 4 figures owner. Two things worth the log: thresholds 0 and 1 are the same arm
because score 1 is nearly nonexistent in `T` (2,135 rows of 689 M — a single co-listen scores
2 under LB's two-order self-join), so "threshold 0" is *one listener, one session*; and the
score-2 mass is 46 % of `T`, yet dropping it moves the added set's dead-end share by only two
tenths of a point at limit 100. Descriptive; the owner reads it. The A0 archive digest is
identical across emitter versions 1 and 3 (`c13c2250…`, 86,854 payloads) — `LBD-D5`'s
determinism, observed.

## Step 4 — Task 7: the builds, the reads, and what was decided in reading them

- **`A2` restricted to `P` is 1.6× `A0`, not 7×.** Of `A2`'s 80.6 M derived rows only 8.8 M have
  both ends in `P`; 49.9 M have one end outside. That is the population confound as a number,
  and it is exactly why `LBD-AM4-1` fixed `P`: a build over the table's own population would
  have been read as "A2 is seven times richer" when, for the artists the app has, it is not.
- **The drop lists were inert in the build, not just in the probe.** Neither build logged a
  drop line (the builder logs only nonzero counts): 0 special-purpose, 0 nameless, 0 from each
  list. The coverage probe predicted it; the build observed it.
- **`A0` was built twice**: once against the archive from emitter version 3, once against the
  re-emission by the final script (identical payload digest, new `MANIFEST.json`). The second
  build's record is the committed one; the first is kept at `C:\unsung-fast\lbd-archives\
  lbd_build_A0.first.json` and the two are compared below.
- **Reads taken in the pre-registration's order** with `lbd_c2b_compare.py`: `LBD-G2` graph
  level with both controls, then `R8`, then `R9`, then the strata descriptively. `A2` clears;
  `R8` and `R9` do not fire. The one reading that needed thought: `LBD-C2b` moves *more* than
  `LBD-C2a` (−8.35 against −3.30). The mechanism is that `A0`'s *map* is far sparser for the
  added set than `A0`'s *table* (9.6 % dead ends against 3.7 %) — the top-*j* union and the
  ceiling delete their weak edges — and `A2` supplies enough candidates that the cap rule keeps
  more. That is `LBD-X1`'s mechanism running the other way; the amendment's held-constant table
  said the ceiling is "not constant in effect", and here is the effect.
- **256 added artists lose connections under `A2`.** Reported, not explained away: the cap
  rule re-selects from a larger candidate set and an edge can be displaced. Small, real.
- **Against the bridge control, differences only.** The control's figures stay in the ceiling
  probe's README; the README here states the deltas as its own figures. The `A0` row's
  difference is "our recomputation on today's data" against "the deployed lists", with every
  lineage term of the Task 4 diagnosis bundled in — the README says so above the table, because
  a reader will otherwise attribute the whole 25 points to the reimplementation.
- **Not done, deliberately:** no path, no routing read, no blind listen, no `NEXT.md` rewrite
  (that is `closeout`'s), no population rule. `top1pct_degree_mass_frac` is in the JSON and not
  read, per the ceiling probe's own forward correction (the ceiling binds in both arms).

## Closeout 2026-09-10 (evening) — the mechanical record

- **Gate outcomes.** `LBD-G2` at graph level: clears for `A2` with both controls (figures owner
  §3). `R8`: does not fire. `R9`: does not fire. `R12`'s shape read descriptively: the residual
  stratum moves most. `LBD-G1` remains fired-and-overridden (`LBD-AM3`); `LBD-G3`/`G4` were Task
  4's and are unchanged. No gate in this stage failed and none was worked around.
- **Defects found in the plan itself.** Task 6's pin of `unlistenable_drop_algb_20260805.json`
  refuses over the fixed population (75,000 censused against 88,685); the `20260809` payload is
  what covers it — recorded in `LBD-AM4-3`, plan unedited. Task 7's "build every arm" is
  superseded by `LBD-AM4-2` (`A3` barred, `A1` not built).
- **Corrections to the prior record.** None overturned. Qualified: `LBD-X3` (for the fixed
  population only, by pointer note); the plan-review's expectation that a graph-level read
  would be swamped by the population confound — it was, until the population was fixed, and
  the size of the swamping is now a number (figures owner §1: `A2` restricted to `P` is 1.6×
  `A0`, not 7×).
- **Operational measurements with no other home.** Curve: 9.6 min at 12 GB / 8 threads; ranked
  intermediate 21.8 GB. Emit: ~2 min per arm. Builds: `A0` 5.9 min, `A2` 7.1 min, each within a
  few GB. The DuckDB access-violation trap is in Step 2 above and in the curve script's
  docstring.
- **Suites** (worktree venvs): builder **286 passed**, api **290 passed**; frontend run from the
  main tree because the worktree has no `node_modules` and the frontend is untouched — result
  in the closeout report. No shipped code changed; only `builder/analysis/` and docs.
- **`docs-lint`:** hard checks passed; every candidate it listed predates this work (restated
  adjudication figures in July/August pre-registrations).
- **D6, the standing context layer**, measured against the memory directory this session's
  context names (`C:/Users/charl/.claude/projects/C--dev-music-app/memory`): unconditional
  **51,694 characters** (delta **zero** against the previous closeout's 51,694); conditional
  **2,567 lines** (2,561 + the previous closeout's own memory append; delta from this session
  **zero** — no memory, skill or agent file was touched).
- **A4:** no config knob was added; the build configuration is an experimental control pinned
  per invocation, not a default. **A5:** no listener on 8000 or 5173, no process of this
  session's left running. **C1:** nothing written to `TEST-QUEUE.md` — nothing here is
  pressable. **D2:** no shipped artifact and no fixture changed. **D3:** every artifact's
  identity is in the figures owner and the handoff.
- **B2 reachability:** `lbd_source.py` is imported by `emit_archive.py` and
  `lbd_build_census.py`; nothing in shipped code imports any of the five scripts, by design
  (frozen research code). **B3:** no tests were added; the two instruments carry their own
  refusal checks — the curve refuses unless it reproduces `A0`/`A2`, the emitter refuses on any
  checksum mismatch — and the curve's check was exercised only green (it never had cause to go
  red); recorded as such rather than claimed as evidence.
- **B1, the audit** (`doc-auditor`, scoped to the diff, lint already run): two findings, both
  fixed from the record. HIGH — `docs/README.md` carried two rows claiming to be the current
  handoff on next actions overall (the `UXR-` T8 row and the `LBD-` row; a pre-existing
  duplication, since the `LBD-` Task 4 row made the same claim beside it); the `UXR-` row now
  claims its track only. MEDIUM — the coverage counts the `LBD-AM4-3` block owns were restated
  in the figures owner's §0; the amendment keeps them (it turns on them and was committed
  first) and the figures owner now cites it. Five other checks clean: identifiers free, links
  resolve, no frozen document edited, no contradiction with `LBD-AM4`, `NEXT.md` states no git
  state. **B4:** the three new docstrings were read against their code (sort order, the
  count-per-direction claim, the `set_stats` semantics) and match. **B5:** nothing in
  `CLAUDE.md`, `.claude/` or memory describes this stage or the drop-list defaults.
