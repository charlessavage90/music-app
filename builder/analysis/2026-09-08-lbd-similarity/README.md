# `LBD-` Tasks 3–4 — the reimplementation, and what it measures

**Role: FIGURES OWNER for the Task 3 verification, and for `LBD-C1`, `LBD-C2`, `LBD-C3` and
`LBD-M1` WHEN THEY ARE MEASURED. ACTIVE.** ⚠ **Task 4 is unfinished: `LBD-C1`, `LBD-C2` and
`LBD-M1` are not measured at all yet, and `LBD-C3` only partly.** This document owns them in
the sense that they will be recorded here and nowhere else — not in the sense that it already
holds them. §§4–7 mark each one's true state. Every number below is owned here and **cited elsewhere, never restated** — by
[`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../../docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
which governs the criteria and owns no figures of its own, and by the retained execution log
[`2026-09-08-lbd-task34-execution-log.md`](../../docs/superpowers/2026-09-08-lbd-task34-execution-log.md).

**Task 1's inputs are owned by [`../2026-09-07-lbd-inputs/README.md`](../2026-09-07-lbd-inputs/README.md)
and are not restated here** — including the dump's identity and row count, the credit frame's
`R-FEAT` join-phrase distribution, and the `CXR` set sizes and shas.

The scripts are **frozen** — stdlib plus DuckDB, no project imports — except
`lbd_c1_sample.py`, which deliberately uses the **shipped** `GraphStore` so the sample cannot
disagree with what the API loads. Everything they produce lands under `D:\unsung-large-data\`;
**nothing is written into `builder/scratch/`** (`LBD-D8`), which is read by absolute path.

| script | what it does |
|---|---|
| `lbd_similarity.py` | ListenBrainz's `build_sessioned_index`, transcribed into DuckDB |
| `lbd_fixture.py` | the synthetic sub-check, expected values hand-derived from LB's SQL |
| `lbd_redirect_frame.py` | `LBDR-F4`'s missing `recording_gid_redirect` arm of the duration frame |
| `lbd_c1_sample.py` | draws and pins the `LBD-C1` fidelity sample |
| `lbd_derive.py` | `LBD-A0`–`LBD-A3` as derivations of the one materialised table `T` |
| `lbd_reads.py` | the `LBD-C1` and `LBD-C2a` reads |

---

## 1. The transcription, and what it is faithful to

### The source

`listenbrainz_spark/similarity/artist.py`, re-fetched from
metabrainz/listenbrainz-server **master** by URL on 2026-09-08.

| | |
|---|---|
| sha256 | `7a8516be7fb0c25b99ef63f3210029c348cf69c987a3ce540f325262e4b90de3` |
| lines | 161 |
| matches the pre-registration's 2026-09-07 pin | **yes, byte-identical** |

**So master has not moved**, and the structural finding in the pre-registration's §1 — that
`threshold` and `limit` are the only two tokens applied after the cross-user aggregation —
still holds against today's source. That is what licenses deriving `LBD-A0`–`LBD-A3` from one
materialised table rather than running four full-history passes.

**Deliberately not vendored.** It is third-party material, and re-fetching is what makes the
check reproducible.

### Eight declared deviations

Full text in `lbd_similarity.py`'s docstring, namespaced `T3-D1`–`T3-D8` (the design already
owns `LBD-D1`–`LBD-D8` as decisions; collision-checked across every ref). Three were not
foreseen by the plan or the review, and **two of those would have corrupted the fidelity run
silently**:

| | what a literal transcription would have done |
|---|---|
| **`T3-D3`** | DuckDB's `CAST(<double> AS BIGINT)` **rounds**; Spark's **truncates**. The cast sits immediately above `HAVING score > threshold`, so scores cross a strict boundary — a pair scoring 10.7 passes a threshold of 10 that LB fails it on |
| **`T3-D8`** | DuckDB's `count_if` returns NULL over an all-NULL frame; Spark's returns 0. That is **every user's first row**, and a NULL `session_id` never satisfies `USING (user_id, session_id)` — so every user's first listen vanishes from every pair. Found by the fixture, not by reading |
| **`T3-D2`** | LB's `session_id` aggregate has no explicit frame, so it is RANGE over `listened_at` and **is** well-defined under LB's own nondeterministic order. Re-ordering it by our tiebreak would have silently converted it to ROWS |

### Three properties reproduced rather than fixed

`T3-P1` the fan-out eats its own first row (on a two-artist credit over `skip` seconds exactly
one artist survives); `T3-P2` every user's last listen is discarded by three-valued logic;
`T3-P3` the self-join counts every pair twice, so `contribution` bites at half the co-listens
it appears to. Each is LB's behaviour and each is deliberate.

### The redirect arm changes almost nothing — measured, on identical users

`LBDR-F4`'s mechanism is real and the correction is kept. **Its magnitude is negligible**, and
this is the figure Task 1's §5 deferred and the plan asked to be recorded.

Same 1-in-256 user slice, run twice, differing **only** in whether the redirect arm is present:

| | pairs in `T` |
|---|---:|
| redirects applied | 5,970,451 |
| redirects absent | 5,970,495 |
| **net delta** | **−44 (−0.001 %)** |
| rows present only with redirects | 126 |
| rows present only without | 170 |

So **about 0.005 % of pairs move at all**, and the net effect on the pair count is four
hundredths of a tenth of a percent. `LBDR-F4` said the omission would be "a systematic,
one-directional divergence in exactly the stage `LBDR-F3` shows is already fragile" — the
direction is real (the net is negative) and the size is not material.

**What this does and does not license.** It discharges `LBDR-F4` with a number instead of a
caveat, and it means the redirect omission **cannot account for any meaningful `LBD-C1` gap**
— which is worth knowing before the fidelity read, because design §6 pre-authorises calling an
unexplained gap "lineage". It is measured on one user slice at `LBD-A0`'s parameters, so it is
not a claim about every arm. The correct frame is used from here on regardless: fidelity to
LB's behaviour is the requirement whether the term moves the answer or not, which is the same
reasoning `R-FEAT` applies to the featured-artist weight.

### The redirect arm of the duration frame (`T3-D6` / `LBDR-F4`)

Task 1 extracted only `recording`, so every listen on a **redirected** recording MBID fell to
the 180-second default instead of its real length — which shifts `difference`, and therefore
session boundaries *and* the skip test, one way. Task 1's §5 deferred this to `LBD-S2` because
the unmatched share is only measurable against the frame that consumes it. This is `LBD-S2`.

`recording_gid_redirect` was extracted from the pinned `mbdump.tar.bz2` and joined to
`recording` exactly as LB's `data/postgres/recording.py:16-33` does.

| | |
|---|---|
| output | `D:\unsung-large-data\lbd-inputs\recording_gid_redirect_length.parquet` |
| sha256 | `87cc25298143ba14cb40beabd1cb67d3f27fb77dc3a843f2e1700eb64b680941` |
| rows | 615,188 |
| rows carrying a length | 613,140 |
| **gids appearing in BOTH arms** | **0** |
| schema sequence | 31, matching the dump and MusicBrainz master |

**The zero matters and was checked rather than assumed.** LB combines the two arms with
`UNION ALL`, not `UNION`, so a gid present in both would fan out every listen on it and
silently double that listen's weight. It does not happen here.

`--no-redirects` reproduces the un-redirected frame, so the size of this input difference is
**measured rather than argued** — which is what turns `LBDR-F4` from a caveat into a figure.

---

## 2. The synthetic sub-check — and the evidence it can fail

Design §6 makes this the only thing separating "we implemented it wrong" from "the inputs
differ", and §7 retires `LBD-R2` on it. The pre-registration's §6 requires its expected values
to be **derived by executing LB's SQL by hand**; the derivation is written out stage by stage
in `lbd_fixture.py`'s docstring so it can be checked without trusting either file.

**Six users, twenty-four listens, eight assertions — all pass.** Beyond the five below, two
prove `T3-D13`'s algebraic collapse equals the naive self-join for **both** pairing modes, and
one proves `LBD-D2`'s chunked form equals the one-shot form — each **demonstrated**, not
argued from the algebra.

Both specifics the pre-registration names by hand are asserted:

- **the window frame** — for "A feat. B" with the phrase stored **unspaced**, `after_ft_jp` is
  true for **A**, the main artist, because MusicBrainz's join phrase is the text *following*
  that artist and the default frame includes the row's own; and true for **B** through the
  cumulative frame. **Both weighted 0.25.** The plan's prose describes the opposite.
- **the untrimmed comparison** — the same credit stored `' feat. '` matches none of LB's eight
  literals and **both artists stay at weight 1**.

**The check is shown to go RED before it is allowed to go green.** Seven mutants each patch
one thing into the generated SQL; **all seven move the answer.** Two of them patch the CREDIT
FRAME rather than the query, because `T3-D11` and `T3-D12` moved the featured-artist logic out
of the query text — and both times the mutants silently stopped being able to find what they
mutate. They did not fail; they had nothing to report. The runner asserts its patch target is
present, which is the only reason either was caught.

| mutant | what it breaks |
|---|---|
| `T3-M1` | trims the join phrase (`LBDR-F2b`) |
| `T3-M2` | strictly-preceding window frame (`LBDR-F2a`) |
| `T3-M3` | `CAST` instead of `TRUNC` (`T3-D3`) |
| `T3-M4` | `row_number()` instead of `rank()` (`artist.py:95`) |
| `T3-M5` | drops the mapped-listen filter (`artist.py:34-35`) |
| `T3-M6` | literal `COUNT_IF` for `session_id` (`T3-D8`) |
| `T3-M7` | drops the same-credit exclusion (`T3-D9`, `artist.py:73`) |

`T3-M6` is there because that mutant is the defect the fixture actually caught on its first
run. **A fixture that has never failed is not evidence that anything passed.**

**`T3-M7` earned its place by failing.** Added to guard the same-credit exclusion, it did NOT
move the answer — so the fixture had never been testing `artist.py:73` at all. The cause: the
only two-artist credit in it was a *featured* pair at weight 0.25, so the pair the rule
suppresses was worth 0.125 and `TRUNC` at the cross-user sum absorbed it entirely. A sixth
user was added whose two-artist credit carries no join phrase, making the suppressed pair
worth 2. **A rounding step downstream of an assertion can make that assertion untestable, and
it does so silently.**

Making `T3-M2` detectable required a deliberate fixture design decision: every featured credit
long enough to trigger `T3-P1` loses the very row the frame question is about, so user 4's
track is **20 seconds** — under `skip` — and both members of the credit survive.

---

## 3. The `LBD-C1` fidelity sample, pinned before Task 4 ran

Per the pre-registration's §2 and `LBDR-F7`. Drawn by `lbd_c1_sample.py`, committed to this
directory as `lbd_c1_sample.tsv` **before any arm read was taken**.

| | |
|---|---|
| **sample sha256** | `59747e416428fb16be44d4f04a6d58d820ddbffa7c0c87e99fdcdf702344ba12` |
| n | 3,000 — 600 in each of 5 bands |
| seed | `random.Random(20260907)` over the sorted MBID list |
| drawn from | `C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot`, **the pinned pre-CEX snapshot**, identity confirmed against `../2026-09-05-lux-e1-armb/README.md` §2 (`AM2`) |
| algorithm dir | `session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30` |
| banded by | `fame_lb_raw` from `graph-msw-tu50.bin`, sha256 `43dd82bb…` — **matched** its manifest sidecar |

**Population and exclusions**, so the denominator is visible rather than implied:

| | count |
|---|---:|
| artists in the snapshot | 75,000 |
| artists in the served artifact | 58,838 |
| excluded — no snapshot response file | 0 |
| excluded — `fame_lb` null, so unbandable | 92 |
| **eligible** | **58,746** |

Band boundaries in `fame_lb_raw`, equal-count quintiles of the eligible population:

| band | pool | `fame_lb_raw` range |
|---:|---:|---|
| 0 | 11,749 | 1 – 526 |
| 1 | 11,749 | 526 – 1,466 |
| 2 | 11,750 | 1,466 – 3,584 |
| 3 | 11,749 | 3,584 – 9,761 |
| 4 | 11,749 | 9,761 – 455,551 |

**Band 4 is `LBD-G1`'s subject** — the gate fires on its pooled row-level rate below 0.60.

### Why this script reads the metadata blob directly, and why that is not a second parser

The shipped `GraphStore` **discards the raw listener counts** (`graph_store.py:52`: *"the raw
counts are not kept, since nothing routes on them"*), and `fame_percentiles` gives null fame
the value 0.0 — so a null and a genuinely least-listened artist are indistinguishable through
it. The pre-registration bands on `fame_lb_raw` and the draw must exclude nulls, so the raw
list is required.

The blob is therefore read directly **and then proved to agree** with the shipped parser on
both things it could disagree about: `meta["mbids"]` is identical in order to `store.mbids`,
and `GraphStore.fame_percentiles(raw)` reproduces `store.fame_lb_pctl` exactly. Both proofs
passed; the script refuses if either fails. That is stronger than either route alone.

---

## 4. `LBD-C3` — cost, and the scale of the full-history pass

**Partial. The full pass has not run.** What is measured is the hardware the track runs on,
which nothing in the plan, the design, the pre-registration or Task 1 records.

### The dump is on a spinning disk

| | |
|---|---|
| `D:` | `ST3000DM008`, 3 TB **SATA HDD**, volume label **"Slow Storage"** |
| `C:` | Samsung 980 PRO **NVMe**, ~582 GB free |
| `E:` | Samsung 970 EVO **NVMe**, ~300 GB free |
| dump directory | 214 GB, 1,409 parquet files |

### Read throughput against thread count

Same two-column query, a different 18-file span per setting so nothing came from the OS
cache, disk otherwise idle. Rates are over total file bytes spanned.

| DuckDB threads | throughput |
|---:|---:|
| 12 | 128.9 MB/s |
| 2 | 245.9 MB/s |
| **1** | **253.6 MB/s** |

**DuckDB defaults to one thread per core — 24 on this machine — and that default costs a
factor of two here.** More concurrent readers on a platter converts sequential streaming into
seek thrash; on an SSD the same setting is free. Measured mid-scan under contention from two
other `D:` readers, throughput fell to ~35 MB/s at a disk queue length of 13.

### What this does to the pre-registration's fallback

`LBD-D2`'s chunked form is exact, and the pre-registration names it as the safe option when
the full pass is too large. **On this hardware it is the expensive path**: each chunk re-reads
the whole dump, because `user_id % k` prunes rows rather than bytes, so sixteen chunks is
sixteen full scans of the slowest device in the machine. The pre-registration predates this
measurement and could not have known.

### The 1-in-256 probe, and what it does NOT establish

| | |
|---|---:|
| rows in `T` | 5,970,495 |
| wall clock | 63.7 min |
| spill | none, at a 16 GB limit |
| configuration | `--no-redirects`, 12 threads — **a cost measurement only, no criterion read off it** |

Extrapolating rows linearly in users, as `LBD-G4` directs, gives roughly **1.5 billion** rows
for a full pass — against the gate's 20 billion bar, which it clears by more than an order of
magnitude, and the pre-registration notes linear extrapolation over-estimates here because
pairs repeat across users.

**The wall clock does NOT extrapolate the same way, and treating it as though it does is
wrong in both directions.** `user_id % 256 = 0` prunes rows but not bytes, so the probe read
the same columns a full pass would; most of its 63.7 minutes was scan, not per-user work.
**The split between the two is not yet measured** — it is what `LBD-G4`'s slice is for, run at
a fixed thread count so it differs from the probe by the slice fraction alone.

### The pair pass, measured on 2026-09-09 — the bucket that failed was not an outlier

**Buckets are `user_id % 64` over the stage-0 intermediate** (`C:\unsung-fast\lbd-listens.parquet`,
sha256 `6d77a681…07707c08`). Its row-group statistics show it is **not clustered by user** (0 of
2,646 row groups span a narrow `user_id` range), so every bucket pass reads the whole file;
the previous session measured that as cheap on the NVMe. Sizes read from the file:

| bucket | listens | heaviest user's listens | 6 GB limit (2026-09-08) |
|---:|---:|---:|---|
| 0 | 37,035,986 | 1,133,854 | passed |
| 1 | 42,150,182 | 618,596 | passed — the largest that did |
| 2 | 38,884,229 | 1,383,570 | passed |
| 3 | 37,777,357 | 939,768 | passed |
| **4** | **45,277,966** | 1,312,155 | **out of memory** |
| 7 | 56,654,604 | 4,779,043 | not run — the largest bucket |

Across all 64: **8 buckets are larger than bucket 4** (7, 9, 12, 14, 45, 50, 51, 53) and **13
more lie between bucket 1 and bucket 4**. Bucket 4 is a 7 % step up from the largest pass and
its heaviest account is smaller than bucket 2's — so the failure was the pipeline at the
margin of its memory limit, not a heavy-tail account.

**One knob changed — the memory limit, 6 GB → 12 GB — everything else as the 2026-09-08 runs
(script sha `40f9ee03…`, mod 64, spill on the NVMe, DuckDB's default thread count):**

| bucket | partial rows | wall | peak RSS | spill | sha256 |
|---:|---:|---:|---:|---:|---|
| 4 | 34,652,332 | 2.1 min | 11.99 GB | 30.6 GB | `2cc2b1b3…` |
| 7 | 32,996,182 | 2.4 min | 12.03 GB | 26.3 GB | `f6a1a3f7…` |

Both pass, both sit at the limit, and bucket 7 is the largest there is — so every bucket passes
at mod 64 with no code change. For comparison, buckets 0–3 at 6 GB: 23.4–27.5 M rows, 109–117 s,
19–25 GB spill each.

**The pass completed 2026-09-09, 64 of 64 buckets, no failures, no sub-bucket splits.**
Buckets 0–3 are the 2026-09-08 runs at 6 GB; the other 60 ran at 12 GB in one detached loop.

| | |
|---|---:|
| partial rows, all buckets | 1,769,954,945 |
| partial parquet on disk | 17.1 GiB, `C:\unsung-fast\lbd-partials\p0..p63.parquet` |
| wall, summed | 118.2 min |
| per bucket at 12 GB | 81–154 s; 22.2–34.7 M rows; peak RSS 11.86–12.03 GB |
| spill per bucket at 12 GB | 20–42 GB |
| **spill, summed over the pass** | **1,724 GB** |

Every bucket at 12 GB peaks within 0.15 GB of the limit, so 12 GB is the floor at which this
query runs at mod 64, not a margin. **The summed spill is 3.4× `LBD-G3`'s 500 GB bar** — see
the gate reading below. Each bucket's manifest carries its own sha256, rows and timings.

**The combine, sized before it was run in anger.** The six partials on disk (buckets 0–4 and 7,
~166 M partial rows) combined with `--aggregate-only` (`HAVING score > 0`, no rank cut):

| | |
|---|---:|
| distinct pairs (`score ≥ 1`) | 121,136,088 |
| wall | 0.4 min |
| peak RSS / limit | 8.03 GB / 8 GB |
| spill | 12.2 GB |
| output | 1.62 GB |

Trial output `C:\unsung-fast\lbd-review\T6.parquet`, sha256 `ba83760a…`; **it is a sizing
artefact, not `T`, and nothing is read off it.** The full combine has ~11× the input and is
expected to fit a 12 GB limit with spill in the low hundreds of GB; the partition-by-`mbid0`
fallback is exact and was not needed here.

**Cumulative spill across the pass will exceed `LBD-G3`'s 500 GB bar** (≈ 64 × 20–30 GB). The
gate's prescribed response is the chunked form, which is what is running; recorded here so the
gate is read honestly when §4 is completed rather than reported as clear.

## 5. `LBD-C1` — fidelity: **`LBD-G1` FIRES**

Read 2026-09-09 on `LBD-A0` (`C:\unsung-fast\lbd-pairs\A0\A0.parquet`, sha256 `f9bd1f83…`,
11,340,639 rows), derived from `T` (`…\aggregate\T.parquet`, sha256 `03d47b05…`, 689,603,622
rows at `score ≥ 1`, 21.0 GB). `T` combined in 8.0 min at 12 GB with 199 GB spill; the four
derivations took 0.2–7.5 min each (`A1` 72,014,611 rows, `A2` 80,578,844, `A3` = `T`).

**Pooled row-level rate by band** (matched rows ÷ archive rows; the definition is the
pre-registration's §2 — the union of both partitions, cut at the archive's own N):

| band | archive rows | pooled rate |
|---:|---:|---:|
| 0 | 16,382 | 0.3943 |
| 1 | 25,098 | 0.5363 |
| 2 | 34,212 | 0.5644 |
| 3 | 47,107 | 0.6039 |
| **4 (the gate's subject)** | 57,692 | **0.5844** |

**`LBD-G1` fires: 0.5844 < 0.60.** Per result `R1`, the reimplementation is presumed wrong,
**`LBD-C2a` is NOT read**, and the diagnosis below is what `R1` demands. 2,945 of the 3,000
sampled artists appear in our table; 8 have an empty archive list (5, 2, 1, 0, 0 by band).

⚠ **The per-artist quantiles `lbd_reads.py` printed alongside are WRONG and are not
reproduced here**: an artist with an empty archive list yields a NaN share, and a NaN inside
`sorted()` scrambles the order, which is why three bands showed a p75 below the median. The
pooled rate does not touch those values and is unaffected. Corrected distribution, empty
lists excluded (`lbd_c1_diagnose.py`):

| band | artists | median | p10 | p25 | p75 |
|---:|---:|---:|---:|---:|---:|
| 0 | 595 | 0.552 | 0.000 | 0.250 | 0.714 |
| 1 | 598 | 0.547 | 0.200 | 0.400 | 0.660 |
| 2 | 599 | 0.600 | 0.319 | 0.480 | 0.707 |
| 3 | 600 | 0.630 | 0.416 | 0.530 | 0.705 |
| 4 | 600 | 0.640 | 0.470 | 0.570 | 0.710 |

### 5a. The diagnosis — where each archive entry went, and what our score is against theirs

`lbd_c1_diagnose.py`, 2026-09-10, over `A0` and `T`. Every archive entry for a sampled artist
is placed in exactly one bin; `T` is a superset of every arm, so "absent" means the pair never
co-occurred in our corpus in a form that survives sessioning.

| band | matched | in our list, past N | score > 10, cut by rank | 1 ≤ score ≤ 10 | absent from `T` |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.401 | 0.111 | 0.066 | 0.100 | 0.322 |
| 1 | 0.544 | 0.134 | 0.173 | 0.053 | 0.096 |
| 2 | 0.587 | 0.125 | 0.155 | 0.039 | 0.093 |
| 3 | 0.619 | 0.100 | 0.164 | 0.029 | 0.089 |
| 4 | 0.631 | 0.076 | 0.158 | 0.027 | 0.108 |

**Our score against ListenBrainz's own `score` on the same pair** (every archive pair present
in `T`):

| band | pairs | median ratio ours ÷ LB | p10 | p90 | share where ours is lower |
|---:|---:|---:|---:|---:|---:|
| 0 | 11,102 | 2.33 | 0.15 | 5.88 | 0.179 |
| 1 | 22,686 | 3.31 | 0.92 | 9.07 | 0.104 |
| 2 | 31,018 | 2.93 | 1.14 | 8.85 | 0.077 |
| 3 | 42,923 | 2.61 | 1.31 | 6.33 | 0.055 |
| 4 | 51,449 | 2.98 | 1.28 | 6.32 | 0.082 |

**Overlap of our top-k with theirs**, pooled by band over artists whose list has ≥ k entries:

| band | k=10 | k=25 | k=50 | k=100 |
|---:|---:|---:|---:|---:|
| 0 | 0.454 | 0.439 | 0.330 | 0.181 |
| 1 | 0.503 | 0.535 | 0.545 | 0.538 |
| 2 | 0.540 | 0.576 | 0.587 | 0.587 |
| 3 | 0.566 | 0.610 | 0.622 | 0.629 |
| 4 | 0.567 | 0.605 | 0.625 | 0.635 |

**List length and the score at the cut** (medians): LB's N is 14 / 28 / 54 / 100 / 100 by
band with a minimum score of 11–12 (41 in band 4); our `A0` union list is 52 / 113 / 117 /
134 / 214 long, and our score at LB's rank N is 38 / 48 / 36 / 40 / 137.

**The corpus, dated by the dump's `created` column** (insertion time; mapped listens inside
the 7,500-day window, 2,347,045,263 rows). `created` begins in 2023-Q4, where everything older
was backfilled, so the cumulative share is a *lower* bound on how much of today's corpus
existed at a date after that:

| existed by | share of today's mapped listens |
|---|---:|
| 2023-12-31 (backfill floor) | 0.29 |
| 2024-09-30 | 0.35 |
| 2024-12-31 | 0.39 |
| 2025-12-31 | 0.59 |
| 2026-03-31 | 0.68 |
| 2026-06-30 | 0.85 |

**The absent partners**, band 4 (6,243 rows): 2,308 name an artist that exists in
MusicBrainz's `artist` table but has **no `artist_credit_name` row at all** (only 1 is a
merged or deleted MBID); 1,086 have credits but appear in no pair in `T`; 2,849 appear in `T`
with other artists, just not with this one. Of the 1,086, 311 are artists whose **every**
credit line is a non-last member of a multi-artist credit — rows `T3-P1` drops under our
deterministic tiebreak (`T3-D2`), where LB's nondeterministic order would drop each member
some of the time. That last mechanism is **ours**, and it is ≈ 0.5 % of band-4 rows.

### 5b. What is inferred, and the test that decides it — stated before the test ran

*Inference, labelled as such.* The systematic ~3× score ratio in every band is not a
reshuffle and not a few months of new listens: it says the deployed dataset was computed on
roughly a third of today's co-listens. The `created` histogram makes that date **around
autumn 2024** if insertion alone explains it, and later if the msid→mbid mapping also improved.
That is the design's §6 "unknown dataset date" — a lineage difference, and the largest term.
The rank-cut and past-N bins (a quarter of band-4 rows) are the same effect seen from the
list end: with three times the mass, more pairs clear the threshold, lists lengthen, and the
archive's tail entries are crowded out. What the ratio does **not** explain is the
credit-less partners: an artist ListenBrainz paired with a famous artist, that today has no
credit line in MusicBrainz, is a mapping or MusicBrainz-edit difference of a kind not yet
identified, ≈ 4 % of band-4 rows.

**The test, `C1-DIAG-1`, pre-stated:** rebuild the corpus as it stood on **2024-10-01** using
`created < 2024-10-01` (`--created-before`; a diagnostic filter, not an arm), rerun the pair
pass, derive `A0`, and re-take the `LBD-C1` read and this diagnosis on it.

- **If the top-band pooled rate rises to ≥ 0.60 and the median score ratio falls toward 1**,
  the gap is the dataset date and the reimplementation is not presumed wrong on that
  account. **This does not un-fire `LBD-G1`**: the gate was read on the pinned corpus as
  pre-registered and the reading stands. Whether the arms may then be read is an amendment
  (`LBD-AM3`) made *after* a result exists, which spends that gate's commit-before-results
  property, and **that is the owner's call**, not a session's.
- **If the ratio falls toward 1 but the rate stays below 0.60**, the reshuffle has a cause the
  corpus size does not explain, and the diagnosis continues from the credit-less partners.
- **If the ratio does not fall**, `created` is not measuring what it appears to, and the
  dataset-date inference is withdrawn.

The dated corpus loses deletions (invisible in a dump) and carries today's mapping, so a
residual below the ceiling is expected even on a perfect date match.

## 6. `LBD-C2a` — pair-table candidate supply

*Pending, and conditional on `LBD-G1` not firing.*

## 6b. `LBD-M1` — population

*Not measured.* Pre-registration §5: how many artists each arm produces, by fame band, against
the served map's. Descriptive, decides nothing here, and it **discharges `LBDR-F6`** by
supplying the artist and neighbour counts the Task 6/7 scale budget needs. It requires the
derived arms, which do not exist yet.

## 7. What is NOT established here

- **Nothing about routing or path quality.** No graph is built by this work and no path is
  scored. `LBD-C2b` is graph-level and is Task 7's, which is conditional on the owner's read.
- **The dump's byte-identity to the published tar** — Task 1's §1 warning stands unchanged.
- **Anything about adoption**, the population rule, the cap rule or the degree ceiling. Each
  is outside this pre-registration and each would need its own.
