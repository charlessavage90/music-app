# `LBD-S4` stage 1 — the nine cells counted, `LBA-G3` read, two instruments taken

**Role: ACTIVE — FIGURES OWNER for `LBA-D8` stage 1.** Every number below is measured here and
**must not be restated elsewhere**; cite by section. Reasoning is
[`docs/superpowers/2026-09-14-lbd-s4-stage1-execution-log.md`](../../../docs/superpowers/2026-09-14-lbd-s4-stage1-execution-log.md).
The governing document is
[`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../../../docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), including §11's `LBA-AM1` and `LBA-AM2`.

**Nothing was emitted, built or censused.** No archive, no graph, no census pass, no journey, no
listen. **`LBA-G2` has no result here** and this document claims none.

**Scripts, frozen research code:** `stage1_verify.py` (task 1), `stage1_u_probe.py`,
`stage1_derive_t7.py` (runs `../2026-09-08-lbd-similarity/lbd_derive.py` unedited),
`stage1_counts.py`, `stage1_framework_rss.py`, `stage2_build_instrument.py` (step 2(b), for
stage 2's use). Committed beside this file: `verify_T.json`, `u_probe.json`, `counts.json`,
`framework_rss.json`.

> ⚠ **Three edge units are in play in this track.** Everything below is in **archive neighbour
> rows** — **pre-cap, two per pair** — which is `LBA-G2`'s unit and **not** CSR entries and **not**
> connections. The served-population README §0 records a build refused once for writing a bound in
> one unit and checking it in another.

---

## 0. Inputs, every one verified before it was read

`LBA-D9`. `stage1_verify.py`, output `verify_T.json`. **All 14 match; nothing was refused.** *(The `--skip-large` run's `verify.json` was a strict subset of it and is not kept.)*

| input | sha256 | bytes |
|---|---|---:|
| `T.parquet` | `03d47b05afd781d48ff6dab2784c9fbfcba30740e5d7e87b22e9aee2620aa08a` | 21,049,671,376 |
| `A0.parquet` (threshold 10) | `f9bd1f835076f22f1b1da444e1aff92dc2ef8f34667a579c82a0848e7fe4821e` | 80,282,502 |
| `A5.parquet` (threshold 3) | `f34cd88957d3ab42b000fb33d23ae7f9aad1dbdb72d2d0b1cab5d34f024a19ff` | 214,892,336 |
| `LBD-A0V.bin` = **`LBA-A1`** | `494c53d52654f6918a4176eef91f291558b0e56d71a4ea16c8070ad8ba3e34bb` | 25,738,850 |
| `LBD-A5V.bin` = **`LBA-A3`** | `2d34746e2cc8a6596ee15e390eea5a14ea7f13ede4ec2ba0608475157653ae63` | 26,892,406 |
| `A0V/MANIFEST.json` | `7f555e1439b97487…` (full digest in `verify_T.json`) | 3,405 |
| `A5V/MANIFEST.json` | `41b663720c69c0d0…` (full digest in `verify_T.json`) | 3,404 |
| `graph-msw-tu50.bin` (`V`) | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` | 17,773,958 |
| `graph-cxa-adopted.bin` (`P`) | `bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46` | 23,410,720 |
| `population_msw_mbids.txt` (`V`) | **`b5e0cb9436208341…`** | 2,235,844 |
| `population_cxa_mbids.txt` (`P`) | **`1bbff8fcfde78a07…`** | 3,370,030 |
| `cxr_added_mbids.txt` | `bfed95ef74b0665c50b1532708091b4e43fab36247db391d04064870659a4339` | 1,135,896 |
| `cxr_preexisting_mbids.txt` | `768054b7e84769346193336ec7e9b3496af92d0d3e8d4ae2fb287057912b5229` | 2,234,134 |
| `cxr_residual_mbids.txt` | `fa8d85cc12131f3cd39ecebeb5da0d52a1236104acbcbabf20232c72b4f43a08` | 226,746 |

**Two of these pins exist on the record only as 8-character prefixes** (the two population files;
the served-population README §0 and the supply README §0 each truncate). Each was therefore
**also** checked against an independently recorded line count — **58,838** for `V` and **88,685**
for `P` — and both match. **Their full digests are recorded in `verify_T.json`** so this does not
have to be repeated.

**`T_A4.parquet` is absent from every path it could occupy.** §10 pins it *"only to be excluded"*
(`LBA-D1`). Absence is a stronger exclusion guarantee than a match: no arm can derive from a file
that is not there.

**The threshold-7 table, derived here:** `C:\unsung-fast\lbd-pairs\T7\T7.parquet`, sha256
`252b88d9e2f8e304e035a0befd709ad87c2753d2af4675a0139e71b076520c6c`, **14,654,446 rows, 54 s**.
`lbd_derive.py` run unedited via the `LBD-AM5-2` wrapper pattern; both script sha256s are in
`T7.manifest.json`.

---

## 1. The nine cells

*Plain sentence of the stage (`LBA-D8`): derive every combination of strength bar and population
rule, and count how many artists and how many connections each one would have.*

Each arm's sentence is **quoted verbatim from §2.2**, fixed before any result existed. The
`filter` column is `LBA-D7`'s, said rather than inferred from a config dump.

| arm | plain sentence (§2.2) | threshold | listeners | rule | filter | **artists** | **pairs** | **archive neighbour rows** |
|---|---|---:|---:|---|---|---:|---:|---:|
| **`LBA-A1`** | *the artists the app serves today, connected by our own recomputation at the same strength bar ListenBrainz used* | 10 | 4 | `V` | `on, inert (20260805)` | **57,620** | 4,175,136 | **8,350,272** |
| **`LBA-A2`** | *the same artists, but a connection is kept when three different people's listening supports it instead of four* | 7 | 3 | `V` | `on, inert (20260805)` | **57,852** | 4,468,365 | **8,936,730** |
| **`LBA-A3`** | *the same artists, but two people are enough* | 3 | 2 | `V` | `on, inert (20260805)` | **58,197** | 4,970,814 | **9,941,628** |
| **`LBA-A4`** | *every artist the deeper crawl found, at ListenBrainz's own bar* | 10 | 4 | `P` | `on, inert (20260809)` | **86,854** | 5,637,469 | **11,274,938** |
| **`LBA-A5`** | *every artist the deeper crawl found, at the three-listener bar* | 7 | 3 | `P` | `on, inert (20260809)` | **87,227** | 6,261,508 | **12,523,016** |
| **`LBA-A6`** | *every artist the deeper crawl found, at the two-listener bar* | 3 | 2 | `P` | `on, inert (20260809)` | **87,764** | 7,396,691 | **14,793,382** |
| **`LBA-A7`** | *every artist anywhere in ListenBrainz's listening data who gets a connection at ListenBrainz's own bar — not just the ones our crawl happened to discover* | 10 | 4 | `U` | **`off, uncensused`** | **366,996** | 11,340,639 | **22,681,278** |
| **`LBA-A8`** | *the same, at the three-listener bar* | 7 | 3 | `U` | **`off, uncensused`** | **456,469** | 14,654,446 | **29,308,892** |
| **`LBA-A9`** | *the same, at the two-listener bar* | 3 | 2 | `U` | **`off, uncensused`** | **679,232** | 26,127,091 | **52,254,182** |

> ⚠ **`LBA-X6` travels with every `U` row.** `V` and `P` are pinned MBID files; `U` is a
> consequence of the arm, so an `LBA-A7`↔`A8`↔`A9` comparison has the **population as a dependent
> variable** and is not one-column in the sense the `V` and `P` rows are.
>
> ⚠ **Every `U` figure above is TABLE-LEVEL and is an upper bound on the built node count.** §2.1
> defines `U` after the drop lists and after the largest-component prune, and the prune needs a
> build. Conservative in the right direction for a feasibility gate.
>
> ⚠ **§2.1's drop-filter column, restated because it is what a reader reads.** `V` → `P` also
> changes the drop-list **payload**; `P` → `U` changes the filter's **state**, from inert-because-
> applicable to absent-because-refused. No read may call an `A7`/`A8`/`A9` result a *population*
> effect without naming the filter state beside it.

**Artists of the population absent from the arm's own table** — `V`: 1,218 / 986 / 641 at
thresholds 10 / 7 / 3. `P`: 1,831 / 1,458 / 921.

### 1a. The instrument's green check — not a criterion

`LBA-A1` and `LBA-A3` are `LBD-A0V` and `LBD-A5V`, whose emitted figures are owned by the
served-population README §2 and §3. `stage1_counts.py` reproduces **all eight** — pairs, payloads,
neighbour rows and absent counts for both — and **refuses to write its output otherwise**. Both
matched exactly. A disagreement would have been an instrument defect caught before any cell was
read.

### 1b. The threshold nesting

A pair kept at a tighter bar is kept at a looser one, because lowering the bar adds only
strictly-lower-scored pairs and `rank()` counts strictly-greater rows. **Checked, not assumed:**
members of `U`(10) outside `U`(7): **0**; of `U`(7) outside `U`(3): **0**; of `U`(10) outside
`U`(3): **0**. So the union of all nine populations is `U`(3) ∪ `V` ∪ `P`.

---

## 2. The union, and the coverage store

| | |
|---|---:|
| union of all nine populations (table level) | **680,032** |
| … in `U`(3) only | 591,302 |
| … in `V` but not `U`(3) | 551 |
| … in `P` but not `U`(3) | 799 |
| census coverage store, artists | **129,746** |
| **union members absent from the coverage store** | **559,759** |

**Per arm, population members absent from the coverage store:**

| arm | `LBA-A1` | `LBA-A2` | `LBA-A3` | `LBA-A4` | `LBA-A5` | `LBA-A6` | `LBA-A7` | `LBA-A8` | `LBA-A9` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| uncovered | **0** | **0** | **0** | **0** | **0** | **0** | 249,587 | 338,138 | 559,759 |

**Every artist in `V` and in `P` is already in the store. The census cost is created by the three
`U` arms alone.**

**Coverage store state, before and after** (the handoff flags it as active data the census scripts
read **and** write): sha256 `385f7c04072ddf375ac2f7ba0dd496b8c70093754e86582ab0ec41839b02321a`
before and after, 32,737,635 bytes, 129,746 artists. **This session read it and did not write it**;
no census was run.

---

## 3. `LBA-G3` — and it **FIRES**

> **Plain sentence (§5): working out which artists are unplayable would take too long.**
> **Bar: a projected offline census pass above 6 hours.** `LBA-AM1`'s finding `LBA-AM1-A11` moved
> this read to stage 1 so it could not be discovered six hours into a pass.

The two committed offline census passes each record their own elapsed time **and** their own count
of freshly evaluated artists, so the scan floor and the marginal rate are **solved rather than
assumed**:

| census | elapsed | artists freshly evaluated |
|---|---:|---:|
| `ulc-census-2026-08-05` | 3,638.0 s | 8,137 |
| `cex-recensus-2026-08-09` | 5,819.7 s | 31,450 |

| projection | basis | result |
|---|---|---:|
| **two-point fit** | scan floor **2,876.5 s**, marginal **0.0936 s/artist** | **15.35 h** |
| single-point sensitivity | the 2026-08-09 pass alone, whole elapsed ÷ its fresh artists, no floor | **28.77 h** |

**Both are multiples of the 6-hour bar, so the read does not depend on which is preferred.**

**Consequence, per §5, and it is a resource fact rather than a finding about anything.** The pass is
**not started**. `LBA-M4`'s class share for the uncovered part is **estimated** from the class rates
the committed censuses measured, labelled as such, and the report says which arms carry an estimated
class rather than a measured one.

> ⚠ **The six `V` and `P` arms do NOT thereby get a *measured* class share.** With no pass run,
> nothing is freshly evaluated, so **every verdict those arms would read is a carried one** — from
> the 2026-08-05 and 2026-08-09 censuses, against **earlier MusicBrainz snapshots than the pinned
> `20260905-002519` one**. `LBA-M4`'s own ⚠ requires the split by verdict source and reserves
> *exact* for the fresh share; after this read **there is no fresh share at all.**

---

## 4. `framework_rss` — measured for the first time in this project

*Plain sentence: how much memory the web service itself uses, on top of the map, so that the size
limit is about the thing we would actually run.* §4 records that it **has never been measured** and
that **`LBA-G1`(a) cannot be evaluated without it**.

Measured on the served artifact (58,838 artists), three repeats, medians. Working set differenced
at stage boundaries **within one process**, framework imported first; the kernel's peak is reported
and never differenced (§5 of the execution log says why both mattered).

| stage | median delta | |
|---|---:|---|
| framework modules — fastapi, starlette, pydantic, httpx, the api package | **38,207,488 B** | 36.4 MiB |
| the store — `load_graph` over the served artifact | 35,151,872 B | 33.5 MiB |
| `ArtistSearch` | **1,380,352 B** | **23.5 B/artist — SCALES** |
| app objects — httpx client, in-memory clip cache, resolver, FastAPI, middleware | **4,472,832 B** | 4.3 MiB |
| **`framework_rss`** = modules + search + app objects | **44,060,672 B** | **42.0 MiB** |

Median final working set of the whole booted process: **97,574,912 B** (93.1 MiB).

> ⚠ **`framework_rss` is NOT population-independent, and §4's single-figure definition hides it.**
> `ArtistSearch.__init__` holds one normalised Python string per artist (`search.py:27`). Applying
> **this** figure to an arm several times larger understates it. **Use the decomposition:**
> **42,680,320 B constant + 23.5 B × N.** At `LBA-A9`'s 679,232 table-level artists that is about
> 55.9 MiB rather than 42.0 MiB — small against a 1.6 GB bar, but it is a term that grows with
> exactly the arms the bar is there to test.
>
> ⚠ **The search term is the noisiest quantity here** — its three repeats spanned 0.29–1.45 MB,
> because the working set is page-granular and allocator timing moves it. The per-artist figure is
> a median of three and should be treated as an order of magnitude, not a precise rate.

---

## 5. The peak-RSS instrument for stage 2 (`LBA-G2`'s missing half)

`stage2_build_instrument.py`, a **forward copy** in this directory. It touches **no shipped code**
under `builder/src` and does not modify `lbv_build.py`, whose outputs are a frozen record.

- `instrumented_build(...)` mirrors `lbv_build.run_build` — same `LogCapture` seam — and adds the
  peak. It **refuses a second call in one process**: `PeakWorkingSetSize` never falls, so two
  builds in one process contaminate the second. **Stage 2 runs one build per process.**
- `rows_from_archive_manifest(...)` takes the x-axis from the emitter's own
  `counts.neighbour_rows_written`, so the unit cannot be re-derived wrongly at the call site.
- `project_peak_rss(...)` implements `LBA-AM2`(d): **0 points → silent, not permissive; 1 point →
  proportional through the origin, labelled; 2+ → least-squares line, intercept free.** Bar 24 GB,
  unchanged.

**Self-test, run and passing** (`--self-test`): the instrument sees a deliberately allocated
256 MiB as 256.0 MiB; the double-call guard fires; and the projection is shown going **red as well
as green** — 16.676 GiB under one slope and 31.353 GiB under a steeper one at the same row count.
*A green reading from a new instrument is not evidence until it has been shown to move.*

> ### ⚠ CORRECTION, 2026-09-15 — this module raises on every real build; use the stage-2 copy
>
> **Everything the self-test above asserts is true, and it is INCOMPLETE in the one way that
> matters.** `stage2_build_instrument.py` raises `TypeError: 'Event' object is not callable` at
> teardown on **every real build**: `_Sampler` assigns `self._stop = threading.Event()`, shadowing
> `threading.Thread._stop`, which CPython calls internally from `join()`.
>
> **The self-test could not reach it.** Its only call to `instrumented_build` pre-populates the
> double-call guard, which raises at the top of the function — before `_Sampler` is constructed. So
> no path in it ever reached `sampler.stop()`, and the instrument was pronounced self-tested having
> never run a build to completion. *"Shown to go red" is necessary and not sufficient — it has to
> go red on the path the instrument is actually used on.*
>
> **Use `../2026-09-14-lbd-s4-stage2/s4_instrument.py`**, a corrected forward copy which **imports**
> the fit rule, the 24 GiB bar and the counters from this module unchanged, so no bar moved. Its own
> self-test drives a build end to end and was shown red on this module and green on that one.
>
> **This block is a forward pointer, not a revision.** Nothing else in this document changes, no
> figure here moves, and the paragraph above stands as the record of what was believed on
> 2026-09-14. Added because this README is **ACTIVE**, not frozen — a reader reaching for the
> instrument arrives here.

**No build has been instrumented.** `LBA-G2` has **no result**, and §7's `LBA-R0` is not reachable
from this stage — `LBA-AM2`(a).

---

## 6. What stage 2 inherits

Ascending archive-neighbour-row order, per `LBA-AM2`(c), with the two reused cells needing no
build:

| # | arm | archive neighbour rows | note |
|---:|---|---:|---|
| — | `LBA-A1` | 8,350,272 | **reused**, `LBD-A0V` (`LBA-D9`) |
| **1** | **`LBA-A2`** | **8,936,730** | first build; **bracketed** by the two reused archives, both of which built on this machine |
| — | `LBA-A3` | 9,941,628 | **reused**, `LBD-A5V` (`LBA-D9`) |
| 2 | `LBA-A4` | 11,274,938 | |
| 3 | `LBA-A5` | 12,523,016 | |
| 4 | `LBA-A6` | 14,793,382 | the `P` row completes here — the only two one-column threshold reads `LBA-AM1-A9` admits |
| 5 | `LBA-A7` | 22,681,278 | |
| 6 | `LBA-A8` | 29,308,892 | |
| 7 | `LBA-A9` | 52,254,182 | the corner; **5.3× the largest archive ever built here** (`LBD-A5V`'s 9,941,628) |

**The `V` row is complete after the first build**, because `LBA-A1` and `LBA-A3` already exist.
