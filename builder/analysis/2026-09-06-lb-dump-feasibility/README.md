# `LBD-` feasibility probes — can artist similarity be computed from ListenBrainz's own listens?

**Role: FIGURES OWNER for the `LBD-` route assessment. ACTIVE.** Every number below is
owned here and cited elsewhere — `findings/2026-09-06-lb-dump-route-assessment.md`, the
`LBD-` design, `NEXT.md` — **never restated.** Two descriptive probes, no criterion, no
threshold, nothing adopted. Written 2026-09-06 in an exploratory session at the owner's
request; the assessment they feed is the findings document above.

Both scripts are **frozen**: no project imports, stdlib + `pyarrow` / `duckdb` only, run
with `uv run --with …` and need no `.venv`. Reproduce with the commands in each docstring.

## Inputs, pinned

| input | identity |
|---|---|
| one day of listens, Spark/parquet incremental | `listenbrainz-spark-dump-2653-20260906-000002-incremental.tar`, **sha256 `ce604db4605f712bab68fdee3aa84848f03c98b972c374ec296ef2000b4497c0`** (matches the published `.sha256`) |
| window it covers | `START_TIMESTAMP` 2026-09-05 00:00:02 UTC → `END_TIMESTAMP` 2026-09-06 00:00:02 UTC; `SCHEMA_SEQUENCE` 1 |
| where it lives | `D:\unsung-large-data\incremental-2653\` — the tar and its extracted directory. **Not in git**: 392 MB |
| licence | the dump ships `COPYING` = **CC0 1.0 Universal**, read from the file |
| source of the dump | `https://data.metabrainz.org/pub/musicbrainz/listenbrainz/incremental/listenbrainz-dump-2653-20260906-000002-incremental/` |

Also downloaded and kept, not measured further: the **sample dump**
`listenbrainz-sample-dump-20250610-094311.tar.zst` (235 MB, `D:\unsung-large-data\sample-20250610\`).
It contains **no listens** — metadata caches, popularity CSVs, and MusicBrainz-derived
parquet frames (`artist_credit`, `recording_length`, `recording_artist`, each ~450k rows, so
sample-restricted). It confirms the *shape* of the two side-tables the similarity job joins
(`artist_credit_id, artist_mbid, position, join_phrase` and `recording_mbid, length,
recording_id, is_redirect`); the full tables come from MusicBrainz's `mbdump.tar.bz2`.

The **full** dump the exploration will use is dump 2647 (cut 2026-09-01), landing at
`D:\unsung-large-data\listenbrainz-spark-dump-2647-20260901-000002-full.tar`, 213 GB, published
sha256 `53a638f77795aaba2a8528a62c13984a4eb908d887704bda50ced2843f91bc42`. **Verify against
that before reading it**; nothing here was measured on it.

## `LBD-P1` — MBID coverage of the parquet dump (`coverage_probe.py`)

**Plain sentence:** *of the listens ListenBrainz publishes in the file its own similarity job
reads, how many say which MusicBrainz artist was played?*

| | count | share |
|---|---:|---:|
| listens in the day | 7,774,140 | |
| distinct users | 21,267 | |
| **with a mapped `recording_mbid`** | **5,740,267** | **73.8 %** |
| **with non-empty `artist_credit_mbids`** | **5,749,512** | **74.0 %** |
| distinct artist MBIDs touched | 142,683 | |
| artists with ≥ 2 / ≥ 5 / ≥ 10 / ≥ 50 listens that day | 94,213 / 56,571 / 39,749 / 15,071 | |
| listens per user: median / p90 / max | 23 / 114 / **1,512,318** | |

Schema of a listen row: `listened_at, created, user_id, recording_msid, artist_name,
artist_credit_id, release_name, release_mbid, recording_name, recording_mbid,
artist_credit_mbids (list<string>)`. The MBID columns are populated by
`listenbrainz/listenstore/dump_listenstore.py`, which joins LB's `mbid_mapping`, the
user's own manual mapping, other users' top manual mapping, and `mb_metadata_cache` at
dump time — i.e. **the parquet dump carries LB's mapping; the JSON listens dump carries
only what the client submitted.**

**Read.** The 0.03 % in `findings/2026-07-19-listenbrainz-probe.md` §6c was measured on the
JSON incremental and is correct *for that file*. It was then generalised — "raw listen dumps
carry MBIDs on 0.03 % of records" in the alpha design — and that generalisation is what this
probe overturns. **The two documents are frozen; the correction goes forward** in the
findings document and their `docs/README.md` rows.

**The max-listens user is a bot** (1.5 M listens in a day is 17 a second). LB's own
`contribution` cap bounds what any one user can add to a pair; whether LB filters such
accounts upstream of its similarity job is **not checked here** and is a stage-2 question.

## `LBD-P2` — cost of the session/pair stages per day (`session_cost_probe.py`)

**Plain sentence:** *how much work is it to do what ListenBrainz's similarity job does, for
one day of listening, on this machine?*

Machine: i7-13700K (16 cores / 24 threads), 32 GB RAM, DuckDB with 16 threads, reading the
parquet from D:. Production parameters for gap (300 s) and skip (30 s); **every track assumed
180 s** because the recording-length table was not an input; featured-artist weighting and
the artist-credit inequality omitted. This is a cost probe, not a reimplementation.

| stage | figure |
|---|---:|
| mapped listens entering the job | 4,903,673 (rows after the skip filter, artist-credits unnested) |
| sessions | 958,935 |
| session length: median / p99 / max listens | 3 / 37 / 691 |
| distinct artists per session, median | 2 |
| **pair rows, LB's listen-level self-join** | **101,478,622** |
| **pair rows, distinct-artists-per-session** | **17,557,636** |
| grouped `(user, pair)` rows | 8,708,107 |
| distinct pairs | 7,538,306 |
| `(user, pair)` rows already at `ALG-B`'s cap of 3 | 1,074,446 |
| **wall-clock, both queries** | **~6 s** (6.2–6.4 s over four runs) |

**`LBD-P2a` — the order LB's SQL uses is not a total order, and it showed.** The first two runs
of this probe ordered listens by `listened_at` alone, as `artist.py` does, and **disagreed in the
fourth significant figure** (sessions 958,930 vs 958,934; listen-level pair rows 101,518,928 vs
101,530,534). One user can log several listens in the same second — the day's top user logs
seventeen a second — and `LAG`/`LEAD` then depend on scan order. Ordering on
`(listened_at, recording_msid)` made two further runs **identical**, and those are the figures
in the table. **The reimplementation inherits this rule** (`LBD-D5`): byte-identical output for
identical input is a project requirement (spec §9), and LB's own job does not meet it.

**Read.** The per-day stages are linear in listens; the sitewide total is 2.70 billion
listens (LB sitewide listening-activity API, all-time, read 2026-09-06), i.e. ~350
day-equivalents of this file. The only step that is not linear is the **all-history**
`(user, pair)` aggregation, whose row count grows sub-linearly (a user's pairs repeat) but is
unmeasured. **Estimate for one full-history run on this machine: one to a few hours,
defensible to no better than 3×** until a full run exists.

**The 6× gap between the two pair-row figures is a semantic choice, not an optimisation.**
LB self-joins listens, so playing A twice and B once in one session contributes 2 to the
pair before the per-user cap; the distinct-artist join contributes 1. With a cap of 3 or 5
the difference saturates fast, but it is a difference. Stage 2 decides which to keep and
says so.

## What is NOT established here

- Anything about the **full** dump — not opened.
- The size of the all-history `(user, pair)` table, and hence the real run time.
- How close a reimplementation gets to LB's served lists (that is the stage-2 fidelity
  question, and the crawl archive under `builder/scratch/` is its ground truth).
- Whether removing the list cap or lowering the threshold changes the degree of the
  `CXR-` added artists — the question the whole track exists to answer.
