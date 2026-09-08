# `LBD-` Tasks 3–4 — the reimplementation, and what it measures

**Role: FIGURES OWNER for `LBD-C1`, `LBD-C2`, `LBD-C3`, `LBD-M1` and the Task 3 verification.
ACTIVE.** Every number below is owned here and **cited elsewhere, never restated** — by
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

**Five users, twenty-one listens, five assertions — all pass.**

Both specifics the pre-registration names by hand are asserted:

- **the window frame** — for "A feat. B" with the phrase stored **unspaced**, `after_ft_jp` is
  true for **A**, the main artist, because MusicBrainz's join phrase is the text *following*
  that artist and the default frame includes the row's own; and true for **B** through the
  cumulative frame. **Both weighted 0.25.** The plan's prose describes the opposite.
- **the untrimmed comparison** — the same credit stored `' feat. '` matches none of LB's eight
  literals and **both artists stay at weight 1**.

**The check is shown to go RED before it is allowed to go green.** Six mutants each patch one
thing into the generated SQL; **all six move the answer.**

| mutant | what it breaks |
|---|---|
| `T3-M1` | trims the join phrase (`LBDR-F2b`) |
| `T3-M2` | strictly-preceding window frame (`LBDR-F2a`) |
| `T3-M3` | `CAST` instead of `TRUNC` (`T3-D3`) |
| `T3-M4` | `row_number()` instead of `rank()` (`artist.py:95`) |
| `T3-M5` | drops the mapped-listen filter (`artist.py:34-35`) |
| `T3-M6` | literal `COUNT_IF` for `session_id` (`T3-D8`) |

`T3-M6` is there because that mutant is the defect the fixture actually caught on its first
run. **A fixture that has never failed is not evidence that anything passed.**

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

## 5. `LBD-C1` — fidelity

*Pending. Read before `LBD-C2a`, because result `R1` says a `LBD-G1` failure means the arms
derived from `T` are not read at all.*

## 6. `LBD-C2a` — pair-table candidate supply

*Pending, and conditional on `LBD-G1` not firing.*

## 7. What is NOT established here

- **Nothing about routing or path quality.** No graph is built by this work and no path is
  scored. `LBD-C2b` is graph-level and is Task 7's, which is conditional on the owner's read.
- **The dump's byte-identity to the published tar** — Task 1's §1 warning stands unchanged.
- **Anything about adoption**, the population rule, the cap rule or the degree ceiling. Each
  is outside this pre-registration and each would need its own.
