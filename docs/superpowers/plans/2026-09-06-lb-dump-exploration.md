# `LBD-` exploration — implementation plan, stages `S1`–`S3`

**Role: ACTIVE implementation plan for the `LBD-` track. UNSTARTED.** Operational document for
[`../specs/2026-09-06-own-similarity-design.md`](../specs/2026-09-06-own-similarity-design.md),
**which governs where the two disagree.** Written 2026-09-06 in the exploratory session that
produced the assessment; every file, function and config value named below was grepped in the
worktree at `75d9642` (`origin/main`) the same day — the exceptions are marked. Owns no figures:
each task's analysis README owns its own.

**Eight tasks, two seams.** Strictly sequential — every task consumes its predecessor's
committed output. Recommended execution: **inline**, one session per seam-bounded stretch; the
tasks are sequential so subagent fan-out buys nothing and each cold subagent would re-derive the
same six files. Effort in sessions is the assessment's estimate and is **not** a commitment.

## Global constraints

- **Worktree, not the main tree.** This plan runs from a worktree beside a live builder session.
  Read `builder/scratch/` by absolute path (`C:\dev\music-app\builder\scratch\…`); **never write
  into it** (`LBD-D8`). Everything this track produces lives under `D:\unsung-large-data\`.
- **No `.venv` needed for the analysis scripts.** They are frozen: `uv run --with duckdb --with
  pyarrow python -u <script>`. Only Task 7 imports the builder, and it does so from the worktree's
  `builder/` after `UV_LINK_MODE=copy uv sync --extra dev` there.
- **`python -u` and `PYTHONIOENCODING=utf-8`** on every long run and on anything printing artist
  names. A buffered log looks dead while a job runs perfectly.
- **Nothing here is serialised as a servable artifact.** Builds go through `build_from_archive`
  in-process, which does not run `check_acceptance`; `PRODUCTION_ACCEPTANCE` is never touched
  (`LBD-D7`).
- **No currency change** (`LBD-D4`). `require_fame=False` on every build in this plan; no
  routing read is made without the existing `fame` stage over the arm's population, and that is
  Task 8, which this ruling does not schedule.
- **Pre-registration before any arm.** Task 2 is committed before Task 3 runs anything beyond
  its synthetic check.
- **Every analysis directory** carries a `README.md` in the figures-owner shape (role line;
  inputs pinned by id and sha; plain sentence per measurement; "what is NOT established").

---

## Stage `S1` — inputs

### Task 1: verify, extract and pin the inputs — `builder/analysis/2026-09-NN-lbd-inputs/`

**Effort:** ~1 session, excluding download time (the owner's).

**Steps**

1. **The parquet dump.** `D:\unsung-large-data\listenbrainz-spark-dump-2647-20260901-000002-full.tar`;
   published sha256 `53a638f77795aaba2a8528a62c13984a4eb908d887704bda50ced2843f91bc42`. Verify
   (`sha256sum`, minutes) **before** extracting; refuse on mismatch. Extract to
   `D:\unsung-large-data\spark-2647\`. Record `START_TIMESTAMP`, `END_TIMESTAMP`,
   `SCHEMA_SEQUENCE` (expect `1`, matching the incremental `LBD-P1` opened) and the parquet file
   count. **If `SCHEMA_SEQUENCE` differs from 1, stop and read the schema before anything else.**
2. **Incrementals — deliberately NOT applied in `S1`–`S3`.** The 2026-09-01 cut is the pinned
   input for the whole exploration; freshness is an `S4` question. Say so in the README.
3. **MusicBrainz side-tables.** Download
   `https://data.metabrainz.org/pub/musicbrainz/data/fullexport/20260905-002519/mbdump.tar.bz2`
   (7 GB; verify against the `SHA256SUMS` / `MD5SUMS` file in the same directory). Extract only
   `mbdump/recording`, `mbdump/artist_credit_name`, `mbdump/artist` and `mbdump/artist_credit`.
   The TSVs have **no header**; column order is `admin/sql/CreateTables.sql` in
   metabrainz/musicbrainz-server at the dump's schema sequence, and `\N` is NULL. Read at
   master 2026-09-06 (re-check against the dump's `SCHEMA_SEQUENCE`): `recording` = `id, gid,
   name, artist_credit, length, comment, edits_pending, last_updated, video`;
   `artist_credit_name` = `artist_credit, position, artist, name, join_phrase`; `artist` =
   `id, gid, name, sort_name, begin_date_year … gender, area, comment (14th), …`. Convert each
   to parquet with DuckDB `read_csv` (tab-delimited, `quote=''`, `escape='\'`), keeping only:
   - `recording`: `gid` (the MBID), `length` (ms, nullable) → the `recording_length` frame;
   - `artist_credit_name`: `artist_credit`, `position`, `artist` (integer id), `join_phrase`;
     joined to `artist` on `id` to carry `gid` → the `artist_credit` frame with
     `artist_credit_id, artist_mbid, position, join_phrase` (the shape the sample dump's
     `artist_credit.parquet` showed, `LBD-P1` README);
   - `artist`: `gid, name, comment` → the identity frame Task 6 needs. **Use `mbdump`'s
     `artist`, not the 2026-07-28 JSON artist dump**, so every MB-derived input carries one
     snapshot date.
4. **Row counts and shas of every produced parquet** go in the README. Name the MB dump's
   schema sequence and the LB dump's; they are different numbers and both matter.
5. **Bot check (`LBD-R9`, the cheap half).** Count users by listens over the whole dump; report
   the top 20 and the share of all listens they hold. Decide nothing — the pre-registration
   decides whether a user filter is an arm.

**Deliverable:** `inputs_extract.py` (frozen) and the README. Commit with a pathspec; push.

---

## Stage `S2` — faithful reimplementation and fidelity

### Task 2: the pre-registration — `docs/superpowers/specs/2026-09-NN-lbd-fidelity-and-supply-preregistration.md`

**Effort:** half a session. **Committed before Task 3 runs on real data.**

It fixes the *values* whose *shape* the design's §4 fixed. Minimum contents, each with its
plain sentence beside it:

1. **`LBD-C1` fidelity.** The sample: a fixed list of archive artists drawn by MBID from the
   served map's archive across fame bands (use `fame_lb_raw` from the served artifact's
   metadata to band them; the list is committed). The metric: overlap of our top-N (N = the
   archive list's length for that artist) with the archive's list. **The floor below which
   `LBD-R2` (we implemented it wrong) is presumed over lineage drift**, and the read of a figure
   above it. State the run state each read presupposes.
2. **The synthetic sub-check.** A hand-computed listen set (three users, ~30 listens,
   featured credits included, one same-second tie) with its expected pair scores under LB's
   semantics, committed as a fixture. Task 3 must match it **exactly** before Task 4 runs.
3. **`LBD-C2` supply.** The fixed artist set: MBIDs present in
   `C:\dev\music-app\builder\scratch\graph-cxa-adopted.bin` and absent from
   `…\graph-msw-tu50.bin`, read via the shipped `GraphStore` as `cxr_census.py` does; both shas
   verified against their manifest sidecars before reading. The measurement: median degree and
   share with ≤ 2 edges of that set in each arm's built graph; the `CXR-P2`/`M5` figures cited
   from their README as the reference. **The effect size that counts as movement**, and the
   read of the null.
4. **The arms**, as a factor table: one row per arm, one column per token that varies
   (`limit`, `threshold`, `contribution`, pairing semantics per `LBD-D6`), and the isolating
   baseline named per row. **The baseline for every arm is our own `ALG-B`-parameter run
   (`A0`), never the archive** (design §6). Then the **held-constant** section, copied from
   design §0 and extended with anything Task 1 revealed.
5. **`LBD-C3` cost** — the run time above which `LBD-D2`'s chunking fallback is built before
   any more arms run.
6. **`LBD-M1` population** — descriptive, by fame band where fame is known from the served
   artifact and "unknown" otherwise.

Collision-check any new sub-series it introduces (`git grep` across refs, never the working
tree).

### Task 3: `lbd_similarity.py` — LB's job in DuckDB, frozen — `builder/analysis/2026-09-NN-lbd-similarity/`

**Effort:** ~1 session including the synthetic check.

**Transcribe `listenbrainz_spark/similarity/artist.py`'s `build_sessioned_index` stage for stage**
(the SQL is quoted in `findings/2026-07-30-lb-algorithm-semantics.md` `LBS-1`/`LBS-2` and the
file was re-fetched 2026-09-06). Parameters: `--days --session --contribution --threshold
--limit --skip`, plus `--limit none` and `--pairing listen|distinct` (`LBD-D6`). Inputs: the
parquet glob, the `recording_length` and `artist_credit` frames from Task 1. Output: parquet
`(mbid0, mbid1, score)` with `mbid0 < mbid1`, **sorted on `(mbid0, mbid1)`**.

Points that are easy to get wrong, each already known:

- **`to_date` is pinned to the dump's `END_TIMESTAMP`, not `today()`.** LB's `main` uses
  today; a reproducible run cannot. `from_date = to_date − days`.
- **Total ordering** on `(user_id, listened_at, recording_msid)` in both windows (`LBD-D5`,
  `LBD-P2a`).
- **Listens with no `recording_mbid` are excluded before sessioning** — exactly as LB's
  `WHERE l.recording_mbid IS NOT NULL AND != ''` does. LB's own TODO notes this breaks sessions
  at unmatched recordings; we inherit that behaviour deliberately for the fidelity run and may
  make it an arm later, never silently.
- **Duration** = `COALESCE(length/1000, 180)` from the `recording_length` frame, joined on
  `recording_mbid`. Redirected recording MBIDs: LB's frame carries `is_redirect`; the `mbdump`
  `recording` table does not resolve redirects, so join on `gid` and record the unmatched share.
- **Featured weight 0.25** applied to artists whose credit position follows a join phrase in
  LB's list (`'feat.', 'ｆｅａｔ.', 'ft.', 'συμμ.', 'duet with', 'featuring', 'συμμετέχει',
  'ｆｅａｔｕｒｉｎｇ'`), computed over the credit's positions per listen as `any(...) OVER
  (PARTITION BY user_id, listened_at, recording_mbid ORDER BY position)`.
- **Pairs exclude same-artist AND same-credit** (`s1.artist_mbid != s2.artist_mbid AND
  s1.artist_credit_mbids != s2.artist_credit_mbids`).
- **Per-user cap** `LEAST(SUM(similarity), contribution)` per `(user, pair)` over the whole
  window; **cross-user sum cast to integer**; `HAVING score > threshold` strict; `rank()` over
  `PARTITION BY mbid0 ORDER BY score DESC` then `rank <= limit` — **per lexical partition**,
  which is why the endpoint's lists reach 2× (`LBS-3`). For `--limit none`, skip the rank cut.
- **Memory.** Run the `(user, pair)` aggregation with `PRAGMA memory_limit` set below physical
  RAM and a `temp_directory` on D:; if it spills badly, chunk by `user_id % k` (the per-user
  cap makes user-range chunks exact) and union the chunk results before thresholding.

**Steps:** 1. write the SQL; 2. run the synthetic fixture and match exactly (red until it
does); 3. run on the one-day incremental as a smoke test and compare shape figures against
`LBD-P2` (they will differ because durations are now real — record by how much); 4. commit
script + fixture + README.

### Task 4: the fidelity run — **HANDOFF SEAM after this task**

**Effort:** the session's remainder plus hours of wall-clock.

1. Run `A0` = `ALG-B`'s parameters (`days 7500, session 300, contribution 3, threshold 10,
   limit 100, skip 30`, listen pairing) over the full dump. Record wall-clock, peak memory,
   spill → **`LBD-C3`**.
2. Compute **`LBD-C1`** against the served map's archive — the ALG-B tree the live map was
   built from, `C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot`
   (the snapshot `LUX-E1` pinned; confirm the path and its identity in the `LUX-E1` README
   before reading). Overlap per sampled artist, by fame band; the distribution, not one mean.
3. **`LBD-D6`:** rerun `A0` with `--pairing distinct`; report the delta in `LBD-C1` and in edge
   count. Record which semantics every later arm uses, and why.
4. README in `builder/analysis/2026-09-NN-lbd-fidelity/` owning `C1`, `C3`, the `D6` delta, and
   the pair table's identity (path, sha, row count). Handoff note per `closeout` A2.

**What a bad `C1` means:** below the pre-registered floor, stop and find the defect (the
synthetic check passed, so it is an input or join difference — durations, credits, redirects,
mapping); do not proceed to arms on a reimplementation whose gap is unexplained. Above it, the
gap is recorded as lineage and the track proceeds.

---

## Stage `S3` — the forbidden knobs

### Task 5: run the arms

**Effort:** hours of wall-clock per arm, little session time.

Run each pre-registered arm to a pair table under `D:\unsung-large-data\lbd-pairs\<arm>\`,
each with a `MANIFEST.json` (parameters; dump id and sha; `mbdump` timestamp; script sha;
wall-clock). **The arm set is the pre-registration's, not this document's** — the assessment
suggested the cap removed, and the threshold below 10, as the two that test `LBD-R1`
directly.

### Task 6: the bulk source and the archive emitter — `lbd_source.py`, `emit_archive.py`

**Effort:** ~half a session.

**The source.** A subclass of `ListenBrainzSource` (`sources/listenbrainz.py:57`) with
`name = "lbd"`, inheriting `parse` and `edge_type`, and `request_url` raising — it is never
fetched. Because it *is* a `SimilaritySource` with a different `name`, `similar_prefix`
(`pipeline.py:129`) reads `similar/lbd/<algorithm>/` and nothing in `build` changes (`LBD-D3`).

**The algorithm token — decided here, and the reasoning matters.** Three loaders key drop
lists on `config.algorithm` and **raise** on an unknown token: `load_drop_mbids`
(`no_release_drop.py:93`, `NoDropListForAlgorithm`), `load_featured_credit_drop_mbids`
(`featured_credit_drop.py:72`), `load_unlistenable_list` (`unlistenable_drop.py:116`, which
alone has an `override_path`). So every arm's `BuilderConfig` uses **`CANDIDATE_ALGORITHM`
(the `ALG-B` string) as `config.algorithm`**, which makes all three resolve to the served map's
lists — held constant per design §0 — with `unlistenable_list_path` pinned to
`unlistenable_drop_algb_20260805.json` so HEAD's repointed default cannot leak in. **The token
therefore names the drop-list lineage, not the arm's parameters**; the arm's parameters live in
the archive root's `MANIFEST.json`, and **each arm gets its own archive root**
(`D:\unsung-large-data\lbd-archives\<arm>\`) so nothing collides under one prefix. Write this
into the README so the next reader does not "fix" the token.

**The emitter.** For each artist with ≥ 1 pair: a JSON payload in the endpoint's own shape —
the field names are the `FIELD_*` constants at the top of `sources/listenbrainz.py` (read
them; do not transcribe from memory) — one row per neighbour, with `name`/`comment` from
Task 1's identity frame, written to `similar/lbd/<ALG-B token>/<mbid>.json`. Union each pair's
two directions (the endpoint serves both partitions; `LBS-3`). Deterministic: neighbours
sorted `(-score, mbid)`, files written in sorted MBID order, `json.dumps(sort_keys=True)`.
**Artists with no identity row** get an empty name and are dropped by `build`'s nameless rule
(`pipeline.py:219`) — count them and report; if it is more than a handful, the identity join is
wrong.

### Task 7: build each arm and read `LBD-C2` — **OWNER STOP at the end**

**Effort:** ~1 session.

```python
# builder/analysis/2026-09-NN-lbd-supply/lbd_build_census.py  (sketch; grep before use)
cfg = BuilderConfig(
    algorithm=CANDIDATE_ALGORITHM,            # drop-list lineage, see Task 6
    unlistenable_list_path=Path(".../unlistenable_drop_algb_20260805.json"),
    require_fame=False,                       # LBD-D4; grt_score.py:157 is the precedent
    # cap_strategy, top_j, degree_ceiling, similarity_rescale: DEFAULTS, held constant (§0)
)
graph = build_from_archive(cfg, LocalArchive(arm_root), BulkSource(cfg))
```

1. Build `A0` and every arm. Record node and edge counts, largest-component retention, and
   the p99 rescale's saturated-edge share from `rescale_scores`' log line → **`LBD-M1`**.
2. **`LBD-C2`:** degree of every MBID in the pre-registered `CXR` added set, per arm — median,
   share ≤ 2, share absent from the graph entirely (an artist with no above-threshold pair is
   *absent*, which is a different outcome from *present with degree 1* and must be reported
   separately). Same figures for the pre-existing 58,793 as the control that they were not
   harmed — the shape `CXR-P2` used.
3. Write the reads in pre-registration order, each with its run-state sentence. Present per
   `CLAUDE.md`: measured; inferred in app terms; weakest link; options — **and stop.** The
   `S4` decision is the owner's.

### Task 8: routing read — **NOT SCHEDULED; described so the stop is informed**

If the owner's `S3` read asks what a journey would actually deliver, the arm's population needs
fame from the **existing** `fame` stage (`artistpath-build fame`, per-artist LB API, hours for
a population this size), then an in-process `serialise` under scaled criteria, then the `JFX`
routing harness (`builder/analysis/2026-08-09-jfx-prereg-critique/jfx_route.py`, ~2.6 h on
the old artifact). It carries the population confound of design §0 in full and needs its own
pre-registration amendment. Dump-derived fame is **not** a shortcut here (`LBD-D4`).

---

## Self-review

**Spec coverage.** `LBD-D1` → Tasks 3–4 (faithful first). `D2` → Task 3 (DuckDB; chunking
fallback). `D3` → Task 6. `D4` → global constraint; Task 8's fence. `D5` → Task 3 (`to_date`,
ordering) and Task 6 (`MANIFEST.json`). `D6` → Task 4 step 3. `D7` → global constraint
(`build_from_archive` only). `D8` → global constraint. `C1`/`C3` → Task 4. `C2`/`M1` → Task 7.
Seams: after Task 4; owner stop at Task 7 — design §5.

**Claims a reader should grep before executing** (all resolved 2026-09-06 at `75d9642` unless
marked): `ListenBrainzSource` and `FIELD_*` — `sources/listenbrainz.py`; `similar_prefix`,
`build_from_archive`, the nameless drop — `pipeline.py:129,167,219`; `require_fame`,
`unlistenable_list_path`, `CANDIDATE_ALGORITHM` — `config.py:132,259,26`; the three drop-list
loaders and their exceptions — `no_release_drop.py:93`, `featured_credit_drop.py:72`,
`unlistenable_drop.py:116`; `LocalArchive` — `archive.py:31`; `grt_score.py:150-158` for the
config-pinning precedent; `cxr_census.py` for reading two artifacts through `GraphStore`;
`grt-archive-algb.pre-cex-snapshot` — **a path under gitignored `builder/scratch/`, confirm it
exists and matches the `LUX-E1` README before Task 4**; `resolve_build_inputs` — **on the
`LUX-4` branch only**, not required.

**What this plan does not close.** The population rule, API sizing, fame source and refresh
procedure — all `S4`, all the owner's to open. The one-day probes' `~6 s` says nothing about
the all-history aggregation; Task 4 is where that estimate is either confirmed or replaced.
