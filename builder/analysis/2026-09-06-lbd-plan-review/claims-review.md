# `LBD-` claims-against-the-repo review

Reviewed at `da6a846` (`main`, clean). Inputs: the design (`docs/superpowers/specs/2026-09-06-own-similarity-design.md`),
the plan (`docs/superpowers/plans/2026-09-06-lb-dump-exploration.md`), the builder source, and
`listenbrainz_spark/similarity/artist.py` **plus its two upstream input builders**, fetched from
metabrainz/listenbrainz-server master by `curl` on 2026-09-06 (not transcribed).

---

## 1. Verdict

**Not executable as written. One hard false premise, and one soft one that is worse.**

The hard one: **Task 7's build config raises `PopulationNotCensused` on every arm, including
`A0`.** `build_from_archive` checks the archive's *whole* artist population against the `ULF-`
census attached to `config.algorithm`, and that census is a frozen list of exactly the 75,000
MBIDs of the pre-CEX ALG-B crawl. Any `LBD-` arm contains artists outside it — by construction,
since `LBD-C2` measures the 29,892 `CXR` added artists, and those are provably not in the 75,000.
The plan's ALG-B-token workaround is sound about *selection* (I grepped every read of
`config.algorithm`; the token steers only the archive prefix and the three drop lists, nothing
else) — but selecting the ALG-B `ULF-` list also selects its *population identity*, which is the
half `LBD-D3`/Task 6 does not account for. Task 6's reasoning paragraph cites
`grt_score.py:150-158` as the precedent and copies one line of it (`require_fame=False`, `:157`),
omitting the three lines beside it (`:153-155`) that are the reason that harness runs at all.
Fix is one line and the plan should say why: `drop_unlistenable=False`, which then makes design
§0's "the drop lists ... pinned per invocation to the lists the served map was built with" a
row the factor table cannot hold. This surfaces at **Task 7**, after Task 4's full-history run
and Task 5's per-arm hours.

The soft one, and the more expensive: **Task 3's featured-weight bullet describes a different
computation from the SQL it quotes**, and Task 2's hand-computed synthetic fixture — the
sub-check design §6 exists to separate "we implemented it wrong" from "the inputs differ" —
would be computed from the same prose. So the synthetic check passes, `LBD-R2` is recorded as
retired, and the error is booked as lineage gap at `LBD-C1`. That surfaces **never**, which is
worse than surfacing at Task 7.

---

## 2. Findings, most severe first

### LBDR-F1 — `drop_unlistenable` at its default refuses every `LBD-` build. Task 7 fails on `A0`.

**Claimed** (plan, Task 6):

> Three loaders key drop lists on `config.algorithm` and **raise** on an unknown token […] So
> every arm's `BuilderConfig` uses **`CANDIDATE_ALGORITHM` (the `ALG-B` string) as
> `config.algorithm`**, which makes all three resolve to the served map's lists — held constant
> per design §0 — with `unlistenable_list_path` pinned to `unlistenable_drop_algb_20260805.json`
> explicitly

and the Task 7 sketch, which sets `algorithm`, `unlistenable_list_path` and `require_fame` and
leaves the three `drop_*` flags at their defaults (all `True`).

**What the code does.** The three loaders do raise on an unknown token, as claimed — but that is
not the failure that fires. `unlistenable_drop.py:151` returns a payload carrying **both** a drop
list and the population it censused, and `pipeline.py` checks the archive against it:

```python
# builder/src/artistpath_builder/pipeline.py:303-318
if config.drop_unlistenable:
    ulf = load_unlistenable_list(
        config.algorithm, config.unlistenable_list_path
    )
    unevaluated = archive_population - ulf.censused_mbids
    if unevaluated:
        ...
        raise PopulationNotCensused(
            f"this archive contains {len(unevaluated)} artist(s) the "
            f"ULF- census for {config.algorithm!r} never evaluated ...
```

`archive_population` is the *whole* archive, captured pre-drop (`pipeline.py:196-200`):

```python
    known = set(payloads)
    archive_population = frozenset(known)
```

and `censused_mbids` is a fixed literal set in the pinned payload —
`builder/src/artistpath_builder/data/unlistenable_drop_algb_20260805.json`, whose
`population.count` is **75,000** (`unlistenable_drop.py:189-202` reads `population["mbids"]`,
verifies count and sha, and returns it as `censused_mbids`).

Pinning `unlistenable_list_path` does not help; the loader's own docstring says so
(`unlistenable_drop.py:170-172`): *"The population check downstream is NOT bypassed."*

This is not a marginal risk, it is guaranteed by `LBD-C2`'s own definition. Measured here:

| set | size |
|---|---|
| `unlistenable_drop_algb_20260805.json` census (the pin) | 75,000 |
| `unlistenable_drop_algb_20260809.json` census (post-extension) | 117,302 |
| in the 117k census, **not** in the 75k pin | **42,302** |

The ~29,892 `CXR` added artists live in that 42,302. `LBD-C2` is *"do the ~29,900 artists the
crawl extension added […] get more connections"* — so an arm that could answer it necessarily
contains artists the pinned census never evaluated, and refuses to build. An arm that *doesn't*
contain them answers `LBD-C2` with a vacuous zero.

**Breaks:** Task 7 (and Task 6's written-down reasoning, which the plan tells the next reader not
to "fix").

**Surfaces:** at the first `build_from_archive` call in Task 7 — i.e. after Task 4's full-history
`A0` run, Task 5's hours-per-arm pair tables, and Task 6's archive emission. Everything upstream
is wasted only in the sense of a stalled session, but the *design* consequence (F1b) is worse.

**F1b — the fix invalidates a held-constant row.** With `drop_unlistenable=False` the `ULF-` rule
is not applied at all, and the two older rules (`load_drop_mbids`, `load_featured_credit_drop_mbids`,
`pipeline.py:266,285`) intersect a 75k-population list with a different, larger population —
`load_drop_mbids(config.algorithm) & known` — which is a *partial* application, silently. Design
§0's row

> the drop lists (`ULF-` unlistenable, no-release, featured-credit) — **pinned per invocation to
> the lists the served map was built with**

is therefore not achievable in any configuration: either the build refuses, or the lists are
half-applied over a population they were never censused over. That is exactly the defect class
`no_release_drop.py`'s `NoDropListForAlgorithm` docstring calls *"the defect this module exists to
remove"* — it only refuses on a missing *key*, never on a mismatched *population*. The honest
statement for the factor table is that the drop rules are **not** held constant across the
`LBD-`/served comparison, and `LBD-C2`'s reference figures (`CXR-P2`) were taken on graphs where
they were applied. The pre-registration (Task 2 item 4, "held-constant section, copied from design
§0") is the place to fix this, and it is committed before Task 3 — so this needs deciding now, not
at Task 7.

---

### LBDR-F2 — the featured-weight bullet contradicts the SQL it quotes, and the synthetic check cannot catch it.

**Claimed** (plan, Task 3):

> **Featured weight 0.25** applied to artists whose credit position **follows** a join phrase in
> LB's list (`'feat.', 'ｆｅａｔ.', 'ft.', …`), computed over the credit's positions per listen as
> `any(...) OVER (PARTITION BY user_id, listened_at, recording_mbid ORDER BY position)`.

**What LB does** (`listenbrainz_spark/similarity/artist.py:28,36,43`, fetched from master):

```sql
, any(ac.join_phrase IN ('feat.', 'ｆｅａｔ.', 'ft.', 'συμμ.', 'duet with', 'featuring', 'συμμετέχει', 'ｆｅａｔｕｒｉｎｇ')) OVER w AS after_ft_jp
...
WINDOW w AS (PARTITION BY l.user_id, listened_at, l.recording_mbid ORDER BY ac.position)
...
, COALESCE(IF(after_ft_jp, 0.25, 1), 1) AS similarity
```

Two separate divergences:

**(a) Frame.** A window with `ORDER BY` and no explicit frame defaults to `RANGE BETWEEN UNBOUNDED
PRECEDING AND CURRENT ROW` (Spark and DuckDB alike). So `after_ft_jp` is true when *any join phrase
at position ≤ the row's own* is in the list — **including the row's own**. In MusicBrainz an artist's
`join_phrase` is the text that *follows* that artist, so for the credit "A feat. B" it is A's row
that carries `feat.`, and A — the **main** artist — is the one flagged 0.25; B is flagged too, via
the cumulative frame. The plan's word "follows" describes a strictly-preceding frame, which would
weight B and not A. Transcribing the quoted SQL literally is correct; transcribing the sentence is
not, and the sentence is what a reader building a hand-computed fixture will use.

**(b) Whitespace.** LB compares raw, untrimmed. Its `artist_credit` frame comes from
`data/postgres/artist_credit.py`:

```sql
SELECT ac.id AS artist_credit_id
     , a.gid::text AS artist_mbid
     , acn.position
     , acn.join_phrase
  FROM musicbrainz.artist_credit ac
  JOIN musicbrainz.artist_credit_name acn ON acn.artist_credit = ac.id
  JOIN musicbrainz.artist a ON acn.artist = a.id
```

— `acn.join_phrase` verbatim. MusicBrainz stores join phrases **with their surrounding spaces**;
verified against the live MB web service during this review:

```
'Empire State of Mind'
   name= 'Max Mutzke' jp= ' feat. '
   name= 'monoPunk'   jp= None
```

`' feat. ' IN ('feat.', …)` is false. So in LB's production job `FEATURED_ARTIST_WEIGHT = 0.25`
fires only on the rare credit whose join phrase has no spacing — it is close to dead code. A
faithful reimplementation must reproduce that. An implementer who trims (the natural thing to do
when the constants "obviously" mean featured artists) diverges from LB on every multi-artist
credit in the corpus.

Note this also puts a question mark over a standing project reading: `LBS-1` says *"0.25 for a
featured artist"*, and `config.py:216-218` (`drop_featured_credit`) reasons from *"quarter-weight
co-listens on other artists' tracks (LBS-1)"*. Neither is wrong about the code; both are about a
term that, on real MB data, is inert. That is a `LBS-` document question, not this plan's, but the
plan is where it becomes load-bearing.

**Breaks:** Task 3 (the transcription), and Task 2 item 2 (the fixture's expected values).

**Surfaces:** worst case, **never**. Task 2's fixture is *"a hand-computed listen set (three users,
~30 listens, **featured credits included**, one same-second tie) with its expected pair scores under
LB's semantics"* — computed by the same reader from the same sentence. It will agree with the
implementation and disagree with LB. Design §6 says that fixture is what *"separates 'we implemented
it wrong' from 'the inputs differ'"*, and §7 retires `LBD-R2` on it. If it is derived from the prose
rather than from the fetched SQL, both guarantees are void and the residual shows up at `LBD-C1` as
an unexplained gap that §6 has pre-authorised calling lineage.

**Cheap fix:** Task 2 should require the fixture's expected values to be derived by *executing the
quoted SQL by hand*, and Task 1 should report the exact distribution of `join_phrase` values that
match LB's eight literals — a one-line count over the extracted parquet, before any of this matters.

---

### LBDR-F3 — `LBD-D5`'s "total order" is not total, and the credit fan-out is missing from the checklist.

**Claimed** (design `LBD-D5`; plan Task 3):

> LB's SQL orders listens by `listened_at` alone, which is not a total order; `LBD-P2` showed two
> runs differing on it. `lbd_similarity.py` orders on `(listened_at, recording_msid)` …
> **Total ordering** on `(user_id, listened_at, recording_msid)` in both windows

**What the code does.** The `listens` CTE **fans one listen out into one row per credited artist**
(`artist.py:32-33`: `JOIN {artist_credit_table} ac USING (artist_credit_id)`). The `ordered` and
`sessions` windows then run over those fanned-out rows:

```sql
, listened_at - LAG(listened_at, 1) OVER w - LAG(duration, 1) OVER w AS difference
    ...
  WINDOW w AS (PARTITION BY user_id ORDER BY listened_at)      -- artist.py:40,45
```

The N rows of one N-artist credit share `user_id`, `listened_at` **and `recording_msid`**. Adding
`recording_msid` to the `ORDER BY` therefore breaks no tie at all for exactly the rows `LBD-P2`
observed differing. To get a total order the key must include `ac.position` (or `artist_mbid`).

There is a second, larger consequence the plan never names. Because the duplicate rows share a
timestamp, for a 2-artist credit at time *t* after a listen *P*:

- row 1: `difference = t − t_P − dur_P` (normal)
- row 2: `difference = t − t − dur = −dur`
- `skipped = LEAD(difference,1) OVER w < skip_threshold` (`artist.py:50`, `skip_threshold = −skip`,
  `artist.py:136`), so **row 1's `skipped` is `(−dur < −30)` → TRUE for any track over 30 s**, and
  `sessions_filtered` (`artist.py:56-63`, `WHERE NOT skipped`) drops it.

So on real data LB systematically keeps only the *last-ordered* artist row of a multi-artist credit
— and which one that is, is exactly what the untied ordering decides. This is the mechanism behind
`LBD-P2`'s non-determinism, and it interacts directly with LBDR-F2: it is these rows the featured weight
is about. A "sensible" transcription (dedup listens before sessioning, or partition the `ordered`
window by recording as well) would silently deviate from LB in the same direction.

Two smaller inherited quirks in the same stages, neither in the checklist: `LEAD` is NULL on a
user's last row, so `NOT skipped` is NULL and **the last listen of every user is always dropped**;
and duration is `CAST(COALESCE(r.length / 1000, 180) AS BIGINT)` (`artist.py:23`) — **truncated to
whole seconds** — while the plan's bullet writes `COALESCE(length/1000, 180)` with no cast.

**Breaks:** Task 3 (both the ordering and the transcription); `LBD-D5`'s determinism guarantee.

**Surfaces:** as run-to-run instability at Task 3's step 3 or Task 4 — i.e. the exact symptom
`LBD-D5` claims to have removed, re-appearing after the full-history run. The truncation surfaces at
Task 3 step 2 as a synthetic-fixture mismatch (cheap), if the fixture has a boundary case.

---

### LBDR-F4 — Task 1 omits `recording_gid_redirect`; the resulting gap is pre-booked as irreducible lineage.

**Claimed** (plan, Task 1 step 3 and Task 3):

> Extract only `mbdump/recording`, `mbdump/artist_credit_name`, `mbdump/artist` and
> `mbdump/artist_credit`.

> Redirected recording MBIDs: LB's frame carries `is_redirect`; the `mbdump` `recording` table does
> not resolve redirects, so join on `gid` and record the unmatched share.

**What LB does** (`data/postgres/recording.py:16-33`, the query behind `RECORDING_LENGTH_DATAFRAME`):

```sql
SELECT r.gid::text AS recording_mbid, r.length, r.id AS recording_id, false AS is_redirect
  FROM musicbrainz.recording r
 UNION ALL
SELECT rgr.gid::text AS recording_mbid, r.length, rgr.new_id AS recording_id, true AS is_redirect
  FROM musicbrainz.recording_gid_redirect rgr
  JOIN musicbrainz.recording r ON rgr.new_id = r.id
```

LB's frame **does resolve redirects** — a redirected gid carries the *target recording's* length.
`recording_gid_redirect` is a table in `mbdump`, so this is reproducible; the plan simply does not
extract it. The consequence is that every listen on a redirected recording MBID falls to
`DEFAULT_TRACK_LENGTH = 180` instead of its real length, which shifts `difference`, which shifts
session boundaries **and** the `skipped` test — a systematic, one-directional divergence in exactly
the stage LBDR-F3 shows is already fragile.

The plan's second sentence turns this from an omission into a mis-attribution: it instructs the
session to *record the unmatched share* rather than eliminate it, so a reproducible input difference
gets written up under design §6's pre-authorisation as part of the lineage gap.

**Breaks:** Task 1 (extraction list), Task 3 (the duration join), Task 4 (`LBD-C1`'s read).

**Surfaces:** at Task 4's `LBD-C1`, as a gap that §6 licenses calling lineage — so, plausibly, never
as a *defect*. Cost to fix now: one more table in Task 1's extraction, one `UNION ALL` in Task 3.

---

### LBDR-F5 — the `skipped` / `sessions_filtered` stage is absent from Task 3's "easy to get wrong" list.

Task 3 says *"Transcribe […] `build_sessioned_index` stage for stage"* and lists `--skip` as a
parameter, but its twelve bullets of "points that are easy to get wrong, each already known" never
mention `sessions` (`artist.py:46-55`), `sessions_filtered` (`:56-63`), the `NOT skipped` filter, or
the sign flip `skip_threshold = -skip` (`artist.py:136`) — so the token reads `skip_30` while the SQL
compares `< -30`. Nor is the session-boundary construction itself named: `COUNT_IF(difference >
{session}) OVER w AS session_id` (`:49`), a running count over the ordered stream, computed **before**
the skip filter is applied.

Partially mitigated: `LBS-2` (`findings/2026-07-30-lb-algorithm-semantics.md`) does record
`skip_threshold = −skip` correctly, and Task 3 points at `LBS-1`/`LBS-2` for the SQL. So this is an
omission from the checklist, not from the record. Given that every other stage of the job *is* in
that list, its absence reads as "already handled".

**Surfaces:** Task 3, cheaply, if the synthetic fixture contains a skip case — Task 2 item 2 does not
say it must. Worth adding one.

---

### LBDR-F6 — Task 6 and Task 7 have no scale budget, and `build_from_archive` reads the whole archive into RAM.

Task 6 (*"~half a session"*) writes one JSON file per artist, and Task 7 (*"~1 session"*) reads them
through `LocalArchive`:

```python
# archive.py:50-53
def keys(self) -> Iterator[str]:
    for path in sorted(self._root.rglob("*")):
```

```python
# pipeline.py:182-193
payloads: dict[str, bytes] = {}
for key in sorted(archive.keys()):
    ...
    payloads[mbid] = payload
```

`rglob` materialises and sorts every path, and every payload is held in memory simultaneously. The
served ALG-B archive is 75,000 files (counted on disk) and that is fine. An `LBD-` arm's population
is the point of `LBD-M1` — expected to be *larger* than 58,838 — and the two arms the assessment
names are **the cap removed** and **the threshold below 10**, both of which multiply neighbours per
artist as well. `--limit none` has no ceiling at all. Small-file creation on NTFS is the other half.

Nothing here is a false claim; it is an unbudgeted cost that lands on the two tasks after Task 5's
compute, and the plan's effort estimates presume the served map's scale.

Also worth one line in Task 7: `LocalArchive.__init__` does `self._root.mkdir(parents=True,
exist_ok=True)` (`archive.py:31-33`), so a mistyped `arm_root` yields an empty archive and a
zero-node build rather than an error.

---

### LBDR-F7 — Task 2 fixes `LBD-C1`'s sample from an unpinned archive while Task 4 reads a pinned one.

Task 4 step 2 **does** pin the fidelity archive, correctly and with a verification instruction:

> Compute **`LBD-C1`** against the served map's archive — the ALG-B tree the live map was built
> from, `C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot` (the snapshot `LUX-E1`
> pinned; confirm the path and its identity in the `LUX-E1` README before reading).

Confirmed on disk, and the gap `NEXT.md` warns about is real:

| tree | `similar/**/*.json` files |
|---|---|
| `builder/scratch/grt-archive-algb.pre-cex-snapshot` | **75,000** |
| `builder/scratch/grt-archive-algb` | **117,302** |

So the prompt's suspicion does not hold for Task 4. It does hold one task earlier: **Task 2** is
where the sample is frozen, and it says only

> a fixed list of archive artists drawn by MBID from **the served map's archive** across fame bands

with no path. Task 2 is committed before Task 3 runs; a sample drawn from `grt-archive-algb` would
put up to 42,302 out-of-lineage candidates in the draw, and `LBD-C1` would then be measured against
lists that postdate the map it is calibrating to. One-word fix, in the document that is written
first. Design §0's held-constant row (*"the endpoint archive under `builder/scratch/`"*) is likewise
unpinned; it should name the snapshot.

---

### LBDR-F8 — minor citation drift (both documents), no execution consequence.

- Design §11: *"the **five** harnesses under `builder/analysis/` that call it directly"*. Actual: **eight**
  files, nine call sites (`grt_score.py:244`, `calibrate.py:209,286`, `cre_build.py:424`,
  `growth_subsets.py:66`, `jfx_build_diagnostic.py:145`, `mknn_build.py:98`,
  `control_empty_maps.py:78`, `armb_sha.py:52`).
- Design `LBD-D4`: *"as the **three** harnesses under `builder/analysis/` already do
  (`config.py:128-132`)"*. Actual: **four** pin `require_fame=False` (`grt_score.py`, `calibrate.py`,
  `cre_build.py`, `growth_subsets.py`). The "three" is inherited from `config.py:130-131`'s own
  comment, which is itself now stale — pre-existing, not the plan's doing, and out of scope here.

---

## 3. Citations checked and clean

Every symbol below exists, sits at the cited line (exact unless noted), and does what the citing
sentence says.

**Plan's own self-review list**

- `ListenBrainzSource` — `sources/listenbrainz.py:54` ✓; `parse` `:65` ✓; `harvest_identities` `:25` ✓.
- `FIELD_*` — `sources/listenbrainz.py:19-22`: `FIELD_MBID="artist_mbid"`, `FIELD_NAME="name"`,
  `FIELD_SCORE="score"`, `FIELD_COMMENT="comment"` ✓ — exactly design `LBD-D3`'s four field names.
- `similar_prefix` — `pipeline.py:131` ✓; `archive_artists` `:147` ✓; `build_from_archive` `:169` ✓.
- the nameless drop — `pipeline.py:235` ✓, and it drops on **empty name specifically**:
  `nameless = {mbid for mbid, (name, _disambiguation) in identities.items() if not name.strip()}`
  (`:235-239`), plus `nameless |= known - identities.keys()` (`:242`) for an artist with a response
  but no identity row. Task 6's claim is exact on both halves.
- `require_fame` — `config.py:132` ✓ (default `True`); `unlistenable_list_path` — `config.py:259` ✓;
  `CANDIDATE_ALGORITHM` — `config.py:26` ✓ (the ALG-B string, `contribution_3`).
- `load_drop_mbids` / `NoDropListForAlgorithm` — `no_release_drop.py:93` / `:83` ✓, raises on an
  unknown token ✓. `load_featured_credit_drop_mbids` — `featured_credit_drop.py:72` ✓,
  `NoFeaturedCreditListForAlgorithm` `:62` ✓. `load_unlistenable_list` — `unlistenable_drop.py:151` ✓,
  `override_path` present and it alone has one ✓ (`NoUnlistenableListForAlgorithm` `:123`). Keying and
  raise-on-unknown are as described for all three; the population check is the part not described (LBDR-F1).
- `LocalArchive` — `archive.py:28` ✓.
- `grt_score.py:150-158` ✓ — `BuilderConfig(algorithm=ALG_B, …, drop_no_release_tail=False,
  drop_featured_credit=False, drop_unlistenable=False, cap_strategy="mutual_knn", require_fame=False)`;
  `require_fame=False` is `:157` exactly ✓.
- `cxr_census.py` — `builder/analysis/2026-09-01-cxr-regression-diagnosis/cxr_census.py` ✓, and its
  README owns the 29,892 / 58,793 / 58,838 figures the plan cites ✓.
- `grt-archive-algb.pre-cex-snapshot` — **exists on disk** at
  `C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot`, with `similar/` and `fame/`
  subtrees, 75,000 similarity responses. Distinct from `grt-archive-algb` (117,302). See LBDR-F7.
- `resolve_build_inputs` — `manifest.py:67` ✓; `log_build_inputs` — `manifest.py:133` ✓; both called
  only from `cmd_build` (`cli.py:254,257`), so `S1`–`S3` genuinely do not touch them ✓.

**Design §11's additional citations**

`SimilaritySource` — `sources/base.py:11` ✓. `Crawler.similar_key` — `crawl.py:109` ✓.
`load_fame` — `fame.py:198` ✓; `fame_key` — `fame.py:91` ✓. `AcceptanceCriteria` /
`PRODUCTION_ACCEPTANCE` / `check_acceptance` — `acceptance.py:54,118,259` ✓. `cli.py:268` (call site)
and `cli.py:301,303` (the not-a-flag parameter and docstring) ✓. `PERMITTED_ALGORITHMS` /
`PERMITTED_CAP_STRATEGIES` — `config.py:35,55` ✓. `fame_percentiles` —
`api/src/artistpath_api/graph_store.py:95` ✓. `jfx_route.py`, `lux4_extract.py` ✓.
`config.py:12-49` for the closed enum ✓ (block runs 12-50; ±1).

**Mechanism (a): does `build_from_archive` bypass `check_acceptance`? — YES, confirmed.**
`check_acceptance` is defined at `acceptance.py:259` and invoked from exactly one place in shipped
code, `cli.py:268`, inside `cmd_build` (`cli.py:250`), *after* `build_from_archive` at `cli.py:263`
and *before* `serialise` at `cli.py:269`. `build_from_archive` (`pipeline.py:169-474`) contains no
reference to it and no import of `acceptance`. Every other caller is a test or a frozen analysis
harness that calls it deliberately. There is no path by which an in-process
`build_from_archive(...)` reaches the gate. Design `LBD-D7` and the plan's global constraint are
correct.

**Mechanism (b): does the ALG-B token do anything else? — NO, the token itself is free.**
Grepped every read of `config.algorithm` in `builder/`: `crawl.py:116,118,245,249,269` (crawl and
resume only), `frontier.py:83,86,97` (frontier only), `manifest.py:101,105,111` (only reached via
`cmd_build`), `pipeline.py:142,144` (the archive prefix), `pipeline.py:266,285,305` (the three drop
lists), `sources/listenbrainz.py:62` (`request_url`, overridden to raise). Within `S1`–`S3` the token
steers exactly two things: the archive prefix — `similar/lbd/<ALG-B token>/`, which is what the plan
says and what Task 6's emitter writes — and drop-list selection. It does **not** touch source
selection, scoring, the cap strategy, the rescale, or manifest contents. The plan's *"the token names
the drop-list lineage, not the arm's parameters"* is correct as a statement about the token. The
defect in LBDR-F1 is not the token; it is that the list the token selects carries a population identity.

**Mechanism (c): are `parse` and `harvest_identities` source-agnostic? — YES.**
`parse` (`listenbrainz.py:65-100`) requires only: the payload is JSON (bytes accepted); rows are
dicts reachable via `_rows` (bare array, `[[...]]`, or an object under `similar_artists`/`data`/
`results`); each row has a truthy `artist_mbid` and a non-`None` `score` coercible by `float(...)`.
`name` is optional (`row.get(FIELD_NAME) or ""`), `comment` is not read by `parse` at all — it is read
by `harvest_identities` (`:45`). A payload carrying exactly `artist_mbid`, `name`, `comment`, `score`
parses cleanly. Neither function branches on `name`, URL, or any field the plan does not mention;
`harvest_identities` calls `ListenBrainzSource._rows` as a **staticmethod** (`:40`), so it does not
even need an instance. `build_from_archive` touches the source only via `source.name` (through
`similar_prefix`), `source.parse(...)` (`:334`) and `source.edge_type` (`:467`) — all inherited by a
`ListenBrainzSource` subclass; `__init__(self, config)` is inherited too, so `BulkSource(cfg)` in the
Task 7 sketch works. `request_url` is never called on the build path. `SimilarArtist` is
`(mbid, name, score)` (`models.py:22-27`). The Task 6 design is sound.

Determinism of the inherited path also checks out: `parse` sorts `(-score, mbid)` (`:99`);
`build_from_archive` iterates `sorted(archive.keys())` (`:183`) so `harvest_identities`' documented
"first non-empty name wins, deterministic because callers pass payloads in sorted order" holds; the
emitter's own `(-score, mbid)` neighbour order and sorted-MBID file order are consistent with it.

**LB's job, stage by stage against master** (`similarity/artist.py`, 161 lines, fetched by curl;
`similarity/` contains only `artist.py`, `user.py` and a `recording` subdir — there is no separate
post-processing module the plan omits, and nothing in the job filters users or bots, which is what
design §6 and `LBD-R9` already say).

| LB stage | plan | verdict |
|---|---|---|
| `listens` — `WHERE recording_mbid IS NOT NULL AND != ''` (`:34-35`) | bullet 3 | ✓ exact, including the inherited TODO |
| `listens` — duration `COALESCE(r.length/1000, 180)` (`:23`) | bullet 4 | ✓ value, ✗ the `CAST(… AS BIGINT)` truncation (LBDR-F3) |
| `listens` — redirect resolution in the upstream frame | bullet 4 | ✗ **omitted input** (LBDR-F4) |
| `listens` — `after_ft_jp` window (`:28,36`) | bullet 5 | ✗ prose ≠ SQL (LBDR-F2) |
| `ordered` — `difference = listened_at − LAG(listened_at) − LAG(duration)` (`:40`) | implied | ✓ semantics; ordering not total (LBDR-F3) |
| `ordered` — `similarity = IF(after_ft_jp, 0.25, 1)` (`:43`) | bullet 5 | ✓ value |
| `sessions` — `session_id = COUNT_IF(difference > {session}) OVER w` (`:49`) | — | ✗ **not named** (LBDR-F5) |
| `sessions` — `skipped = LEAD(difference) < {skip_threshold}`, `skip_threshold = −skip` (`:50,136`) | — | ✗ **not named** (LBDR-F5); correct in `LBS-2` |
| `sessions_filtered` — `WHERE NOT skipped` (`:56-63`) | — | ✗ **not named** (LBDR-F5) |
| `user_grouped_mbids` — lexical `mbid0/mbid1`, `s1.sim * s2.sim`, `WHERE artist_mbid != AND artist_credit_mbids !=` (`:66-73`) | bullets 6, output spec | ✓ exact |
| `user_contribtion_mbids` — `LEAST(SUM(similarity), {contribution})` grouped `(user, mbid0, mbid1)` (`:74-82`) | bullet 7 | ✓ exact, including "over the whole window" |
| `thresholded_mbids` — `BIGINT(SUM(part_score))`, `HAVING score > {threshold}` (`:83-90`) | bullet 7 | ✓ exact, including the integer cast and strict `>` |
| `ranked_mbids` — `rank() OVER (PARTITION BY mbid0 ORDER BY score DESC)`, `WHERE rank <= {limit}` (`:91-102`) | bullet 7 | ✓ exact, including the per-lexical-partition read behind `LBS-3`'s 2× |
| `main` — `to_date = midnight today`, `from_date = to_date − days` (`:121-122`) | bullet 1 | ✓, and the pin to the dump's `END_TIMESTAMP` is a stated, correct deviation |

Also confirmed against master, in LB's favour and consistent with the plan: the listens schema
(`listenbrainz_spark/schema.py:36-48`) carries `listened_at` (timestamp), `user_id`,
`recording_msid`, `artist_credit_id`, `recording_mbid` and `artist_credit_mbids` — every column
Tasks 1 and 3 assume; `BIGINT(l.listened_at)` at `:22` is the epoch-second conversion `LBS-2`
describes. The `artist_credit` frame's four columns (`artist_credit_id, artist_mbid, position,
join_phrase`) match Task 1's extraction shape exactly.

Two `main()` defaults the plan does not mention but does not violate: `get_listens_from_dump`
defaults `include_incremental=True` (the plan deliberately excludes incrementals, Task 1 step 2 —
declared, and consistent with design §6) and `remove_deleted=False` (matches). Its range filter is
`listened_at >= start AND listened_at <= end` — **inclusive at both ends**
(`listens/data.py:58-64`); with `days=7500` the lower bound is inert, and the plan should state the
upper bound's inclusivity when it pins `to_date` to `END_TIMESTAMP`.

---

## 4. What I could not verify, and why

- **The parquet dump itself.** `D:\unsung-large-data\…` is the owner's machine and not visible from
  here. Everything about `START_TIMESTAMP` / `END_TIMESTAMP` / `SCHEMA_SEQUENCE`, the published
  sha256, and whether the dumped listens match `listens_new_schema` is unchecked. I verified the
  *schema LB writes on master*, not the *file he downloaded*. Task 1 step 1 is the right place and
  already refuses on mismatch.
- **`mbdump` column orders.** Task 1 step 3 quotes column orders for `recording`,
  `artist_credit_name` and `artist` read from `CreateTables.sql` at master. I did not re-fetch that
  file; the plan already instructs re-checking them against the dump's own schema sequence, which is
  the correct control. My LBDR-F4 finding adds a table to the extraction list; it does not depend on those
  orders.
- **`builder/scratch/mb-json-dumps/artist` (design `LBD-D3`)** exists on disk (`artist`, `release`,
  `release-group` subdirs) but I did not open it. Note the plan's Task 1 step 3 supersedes that
  design sentence — it directs `mbdump`'s `artist` table instead, *"so every MB-derived input carries
  one snapshot date"*. That is a deliberate plan-over-design refinement, not a conflict, but design
  §3's `LBD-D3` still names the 2026-07-28 JSON dump and the design governs where the two disagree
  (§ header). Worth one amending sentence in whichever document is next touched.
- **`LUX-E1` README's identity block for the pinned snapshot.** I confirmed the directory
  `builder/analysis/2026-09-05-lux-e1-armb/` exists and the snapshot path exists with 75,000
  responses; I did not read the README's sha/identity claims. Task 4 already instructs confirming
  them.
- **Whether `after_ft_jp` is truly near-dead on the real corpus.** I established the mechanism
  (untrimmed comparison) and confirmed MusicBrainz's ' feat. ' spacing from the live web service on
  one credit. I did not measure the share of `artist_credit_name.join_phrase` values in `mbdump`
  matching LB's eight literals exactly — that is a one-line count in Task 1 and is the right place
  for it. The LBDR-F2 finding about prose-vs-SQL (the window frame) does not depend on this and is
  verified from source.
- **Task 6/7 scale (LBDR-F6).** I did not estimate the artist count or neighbour count of any arm — that
  is `LBD-M1`, which the track has not run. The finding is that no budget exists, not that a
  specific number is wrong.
