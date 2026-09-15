# `LBD-S4` stage 2 — seven cells emitted, six built, `LBA-G2` stops the corner, `LBA-M1` taken

**Role: FIGURES OWNER for `LBA-D8` stage 2.** Every quantity stage 2 measured lives here and is
**cited from elsewhere, never restated.** Stage 1's figures are owned by
[`../2026-09-14-lbd-s4-stage1/README.md`](../2026-09-14-lbd-s4-stage1/README.md) and are not
repeated here either. Reasoning is
[`../../../docs/superpowers/2026-09-14-lbd-s4-stage2-execution-log.md`](../../../docs/superpowers/2026-09-14-lbd-s4-stage2-execution-log.md).

**Governing:** [`../../../docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../../../docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), §11's `LBA-AM1` and `LBA-AM2` before §3 or §5.

> ## ⛔ What this stage did NOT do
>
> **`LBA-M2`, `LBA-M3`, `LBA-M4` and `LBA-M5` are not taken.** **No census was run** — `LBA-G3`
> fired at stage 1, which is a resource fact about a pass's wall clock and **not a finding about
> any arm**. **No listen was designed** (`LBA-D3`). **No fame was fetched** (`LBA-D5`). **No arm is
> selected, no threshold is preferred and no route is recommended** — `LBA-D2` reserves the
> threshold to the owner at the go/no-go stop, and §7 gives him the numbers rather than a
> recommendation.
>
> **Reads reached:** `LBA-R0`, and `LBA-R1` of the three mutually exclusive hosting reads.
> **Nothing else in §7 is reachable** and nothing else is read — see §7 of this document.

---

## 0. Inputs, verified by this session before anything was read

`LBA-D9`. `stage1_verify.py` re-run here, output `_pins/stage2_verify_pins.json`. **All 14 pins
match; nothing refused**, including the 21 GB `T.parquet`. Digests are stage 1's §0 and are not
restated. **`T_A4.parquet` is absent from every searched path** — §10 pins it only to be excluded
(`LBA-D1`), and absence is a stronger exclusion guarantee than a match.

**Scripts.** `s4_emit.py`, `s4_build.py`, `s4_instrument.py`, `s4_common.py`, `s4_bare_copy.py`,
`s4_boot_rss.py`, `s4_pairset.py`, `s4_query_cost.py`, `s4_sizing.py`, all in this directory, all
forward copies. **No shipped code under `builder/src` was touched and nothing was written under
`builder/scratch/`.** The frozen emitter `../2026-09-10-lbd-supply/emit_archive.py` was run
**unedited**, its population constants repointed by wrapper — the `lbv_emit.py:58` pattern — and
its sha checked before anything was repointed.

⚠ **`s4_instrument.py` supersedes stage 1's `stage2_build_instrument.py` for any future use.**
That module raises `TypeError: 'Event' object is not callable` on **every real build**: `_Sampler`
assigns `self._stop = threading.Event()`, shadowing `threading.Thread._stop`, which CPython calls
from `join()`. Stage 1's self-test could not reach it — its only call to `instrumented_build` hits
the double-call guard, which raises before the sampler is constructed. The forward copy **imports**
`project_peak_rss`, `LBA_G2_BAR_BYTES`, `BuildPoint` and the counters from the stage-1 module
unchanged, so **`LBA-AM2`(d)'s fit rule and the 24 GiB bar are provably untouched**; only
`_Sampler` and `instrumented_build` are redefined. Its self-test runs a build end to end and was
shown **red on stage 1's module and green on this one**.

---

## 1. The seven archives (`LBA-D8` stage 2, emit)

Emitted by the frozen Task 6 emitter, one process per arm, ~37 min total. Each cell has its own
`S4-<arm>` root; the frozen `A0`, `A2`, `A0V` and `A5V` archives were not written into.

| arm | rule | population | payloads | **archive neighbour rows** | absent | wall |
|---|---|---:|---:|---:|---:|---:|
| `LBA-A2` | `V` | 58,838 | 57,852 | **8,936,730** | 986 | 80 s |
| `LBA-A4` | `P` | 88,685 | 86,854 | **11,274,938** | 1,831 | 117 s |
| `LBA-A5` | `P` | 88,685 | 87,227 | **12,523,016** | 1,458 | 119 s |
| `LBA-A6` | `P` | 88,685 | 87,764 | **14,793,382** | 921 | 119 s |
| `LBA-A7` | `U` | 366,996 | 366,996 | **22,681,278** | 0 | 407 s |
| `LBA-A8` | `U` | 456,469 | 456,469 | **29,308,892** | 0 | 526 s |
| `LBA-A9` | `U` | 679,232 | 679,232 | **52,254,182** | 0 | 848 s |

⚠ **UNIT: archive neighbour rows are PRE-CAP, two per pair. They are not CSR entries and not
connections.** Three edge units are in play in this track.

**All 21 counts reproduce stage 1 exactly** — payloads, neighbour rows and population-absent for
every cell. **Not a criterion; the instrument's green check**, and `s4_emit.py` refuses to finish on
disagreement. `LBA-A4` is a re-emission of the archive the supply work committed as `A0`, so its
three counts were matched against a **frozen record** rather than another figure from this session.

**On every `U` cell, payloads equal the population and absent is 0** — both follow from the rule
(`U` is derived *from* the arm's own table) and were asserted rather than assumed. **Every `U`
population member has an identity row** (0 without, against 10 on each `P` cell), so
`pipeline.py`'s nameless-artist rule removes nobody from a `U` arm at build time.

---

## 2. The builds, and `LBA-G2`

One process per build — `PeakWorkingSetSize` never falls — in **ascending archive-neighbour-row
order** (`LBA-AM2`(c)). `LBA-G2` read **before** each build from all builds instrumented so far.

| # | arm | rule | filter (`LBA-D7`) | **nodes after prune** | **CSR entries** | median deg | max deg | **peak RSS** | projection | residual | wall |
|---:|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| 1 | `LBA-A2` | `V` | `on, inert (20260805)` | 57,466 | 1,616,598 | 26 | 50 | **5.376 GiB** | *silent* | — | 0.9 m |
| 2 | `LBA-A4` | `P` | `on, inert (20260809)` | 86,086 | 2,204,856 | 22 | 50 | **6.823 GiB** | 6.783 GiB, 1 pt | **+0.6 %** | 7.0 m |
| 3 | `LBA-A5` | `P` | `on, inert (20260809)` | 86,649 | 2,326,654 | 24 | 50 | **7.534 GiB** | 7.595 GiB, 2 pt | **−0.8 %** | 8.4 m |
| 4 | `LBA-A6` | `P` | `on, inert (20260809)` | 87,394 | 2,490,728 | 26 | 50 | **8.840 GiB** | 8.922 GiB, 3 pt | **−0.9 %** | 7.8 m |
| 5 | `LBA-A7` | `U` | **`off, uncensused`** | 311,335 | 4,869,706 | 9 | 50 | **13.911 GiB** | 13.521 GiB, 4 pt | **+2.9 %** | 25.9 m |
| 6 | `LBA-A8` | `U` | **`off, uncensused`** | 390,404 | 6,132,790 | 9 | 50 | **17.868 GiB** | 17.975 GiB, 5 pt | **−0.6 %** | 32.9 m |
| — | **`LBA-A9`** | `U` | **`off, uncensused`** | **UNBUILT** | — | — | — | — | **32.044 GiB, 6 pt** | — | — |

**The two reused arms** (`LBA-D9`, not rebuilt — a rebuild would add a build-date column the factor
table does not have): `LBA-A1` 57,142 nodes / 1,569,214 CSR entries; `LBA-A3` 57,932 / 1,681,254.
Read here by **decoding their artifacts**, not restated from the served-population README.

### 2a. `LBA-G2` fired on `LBA-A9` — and that is a resource fact, not a finding

> **Plain sentence (§5): we cannot build this map on this machine.** Bar: projected build peak RSS
> above 24 GiB. `LBA-A9`'s projection from the least-squares line over all six instrumented builds,
> intercept free, in archive neighbour rows: **32.044 GiB.**

**The cell is reported as *unbuilt for a resource reason*** and §2.6's three barred conclusions are
attached to its own record verbatim. The second is the one most easily got backwards:

> **"We could not build it here" and "it is too big to serve" are different claims, and the second
> needs `LBA-M1`.** `build_from_archive` holds neighbour objects in a Python dict during its first
> pass — a property of the **builder**, not of `GraphStore`. Nothing here says a service could not
> hold this map.

Also barred for this cell: **no map-level read** (`LBA-M1`, `LBA-M2`, `LBA-M3` are simply unread —
its table-level population and pair counts stand), and **no cross-population comparison at the
two-listener bar at map level.**

**`LBA-D8`'s prohibition held.** No cell was stopped on any other ground — not for being dominated,
not for cost, not for looking uninteresting.

### 2b. The fit rule was fixed before any build and turns out to model this well

`LBA-AM2`(d) fixed the fit **before any build existed**, and no document had established that build
peak memory is linear in archive neighbour rows. Five projections against subsequently measured
actuals: **+0.6 %, −0.8 %, −0.9 %, +2.9 %, −0.6 %.**

⚠ **Signed, not absolute, because the sign is what matters.** An **under**-predicting fit is the one
that admits a cell it should have stopped. The only residual above 1 % is the single
under-prediction, on the `U` row — the row `LBA-A9` sits on. **`LBA-A9`'s projection exceeds the bar
by about a third**, an order of magnitude more headroom than that residual, **so the stop does not
turn on the fit's precision.**

### 2c. An incidental precision estimate for the calibration point

`LBA-A2` was built twice — a rerun forced by a defective assertion, see the execution log — and the
two peaks agree to **0.011 %**: 5,771,968,512 B against 5,772,615,680 B. `LBA-AM2`(b) makes the
first build the **sole basis** of the one-point projection and every later line still carries it,
and nothing in the design measured how repeatable a peak is. **So the fit's residual is a property
of the row-count model, not of the instrument.** Obtained by accident; **no criterion rests on it.**

### 2d. Acceptance, and two bounds that are deliberately weak

Scaled per arm from quantities known **independently of the build**; `PRODUCTION_ACCEPTANCE` is
never used, because its bands are centred on the served artifact and **every arm above `V` breaches
them by construction** — widening a production bound to admit a new artifact is risk acceptance and
**the owner's** (§8). At rule `V` the function reproduces `lbv_build.py`'s committed bounds exactly
— `(47070, 58838)` nodes, `(1052547, 2941900)` CSR entries — which is its green check.

⚠ **On the `U` row the node floor is 50 % of the arm's own table count and the edge floor is
`CSR ≥ N`, and both are labelled GROSS-LOSS TRIPWIRES, not calibrated bounds.** §2.4 records the
prune's effect over `U` as **unmeasured**, so no calibrated floor existed; a tight one invented here
would have refused a *correct* build after half an hour. **The stated cost: on that row the edge
floor cannot see a silent cap-rule revert**, which `acceptance.py`'s `CXA-` note calls the one thing
it exists to catch. Protection there falls to the physical upper bound and the median-degree bound.
The four §2.8 detectors are unscaled at every rule — they describe a defect's **shape**, not a
population's size.

### 2e. The prune's effect over `U`, measured for the first time

| rule | arms | retention of the arm's own table population |
|---|---|---|
| `V` | `LBA-A2` | 57,466 of 57,852 — **99.3 %** |
| `P` | `LBA-A4`–`A6` | 86,086 / 86,854, 86,649 / 87,227, 87,394 / 87,764 — **99.1–99.6 %** |
| **`U`** | `LBA-A7`, `LBA-A8` | 311,335 / 366,996 and 390,404 / 456,469 — **84.8 % and 85.5 %** |

**Two cells is not a calibration**, and the `U` node floor stays at 50 % and stays labelled
uncalibrated. An 80 % floor would in fact have passed on both — but nothing before these builds
said so, a looser threshold has more fringe to lose, and a floor that refuses a correct build costs
a rebuild while a loose one costs nothing here.

---

## 3. `LBA-M1` — map size and what it costs to serve

> **Plain sentence (§4): how big is the map — how many artists, how many connections, how large a
> file — and can the machine we run on still serve it?**

### 3a. The two calibrations, taken before the gate was read

**`metadata_ratio` = 1.60334** — median `GraphStore`-only load peak of `graph-lux4.bin`
(161,390,592 / 161,169,408 / 162,070,528 B) ÷ the same for `graph-msw-tu50.bin` (100,458,496 /
100,777,984 / 100,659,200 B). The pair is **identical in artist count and CSR entries** and differs
only in the three `LUX-4` keys, so the ratio isolates the metadata term. **Measured, not assumed:
metadata costs about 1.6× in resident memory while adding about a third to serialised bytes**,
because `GraphStore` holds those keys as Python `list[str]` and `list[dict]` while the CSR arrays
stay as numpy.

**`framework_rss`** is stage 1's, used as its **decomposition** — `42,680,320 B + 23.5 B × N` — and
never as the single figure, because `ArtistSearch` holds one normalised string per artist. Stage 1
records the per-artist term as an **order of magnitude, not a precise rate**.

⚠ **Every arm's boot memory is measured on a BARE re-serialisation**, the six built and the two
reused alike. `require_fame=False` removes **fame only** — `deezer_ids` and the three `LUX-4` keys
load from frozen package data, not a fetch — so a census build carries **four of the five** additive
keys and the reused artifacts carry all five. Applying `metadata_ratio` to either would scale
metadata **already present**, double-counting the exact term the ratio measures. This is §4's own
treatment of the **bytes** half applied to the **memory** half; **no bar moved.**

### 3b. The table

| arm | rule | filter | **artists** | **CSR entries** | connections | **bare bytes** | boot peak | **projected shipped peak RSS** | d0 p50 | d0 p95 | **`LBA-G1`(b) ratio** |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `LBA-A1` *control* | `V` | `on, inert` | 57,142 | 1,569,214 | 784,607 | 19.3 MB | 91.9 MiB | **189.4 MiB** | 646.4 ms | 1115.6 ms | **1.059** |
| `LBA-A2` | `V` | `on, inert` | 57,466 | 1,616,598 | 808,299 | 19.7 MB | 92.6 MiB | **190.5 MiB** | 612.5 ms | 1062.7 ms | **1.070** |
| `LBA-A3` | `V` | `on, inert` | 57,932 | 1,681,254 | 840,627 | 20.3 MB | 94.1 MiB | **192.9 MiB** | 619.6 ms | 1123.5 ms | **1.077** |
| `LBA-A4` | `P` | `on, inert` | 86,086 | 2,204,856 | 1,102,428 | 27.6 MB | 120.8 MiB | **236.3 MiB** | 657.4 ms | 1336.5 ms | **1.192** |
| `LBA-A5` | `P` | `on, inert` | 86,649 | 2,326,654 | 1,163,327 | 28.7 MB | 123.2 MiB | **240.1 MiB** | 648.5 ms | 1350.1 ms | **1.210** |
| `LBA-A6` | `P` | `on, inert` | 87,394 | 2,490,728 | 1,245,364 | 30.3 MB | 126.1 MiB | **244.9 MiB** | 657.7 ms | 1430.4 ms | **1.206** |
| `LBA-A7` | `U` | **`off, uncensused`** | 311,335 | 4,869,706 | 2,434,853 | 71.5 MB | 309.1 MiB | **543.3 MiB** | 965.4 ms | 2720.2 ms | **1.792** |
| `LBA-A8` | `U` | **`off, uncensused`** | 390,404 | 6,132,790 | 3,066,395 | 89.9 MB | 379.2 MiB | **657.4 MiB** | 1003.4 ms | 3065.2 ms | **1.860** |
| **`LBA-A9`** | `U` | **`off, uncensused`** | **unbuilt for a resource reason — `LBA-M1` unread** | | | | | | | | |

⚠ **UNITS.** *CSR entries* count each connection in **both** directions and are what every sidecar's
`"edges"` records; *connections* is the same quantity counted once. Neither is archive neighbour
rows (§1).

**Each arm's plain sentence is §2.2's, fixed before any result existed**, and is quoted in §6 below
rather than abbreviated here.

### 3c. The query-cost half, and what it rests on

200 pairs, `random.Random(20260914)`, drawn from the **57,013 artists present in every built arm
and in the served map**, any pair adjacent in any map redrawn. **Written and sha-pinned before any
timing was taken**: `s4_pairset.tsv`, sha256
`2713e5369719dd39091363d8d0977b8ae2339b4df6a56ad707ca67a967528cc9`.

**d0 only, and the reason is read from source rather than assumed.** `pathfinding.py:130-132`
computes `ramp_fame = w_known_ramp_fame_pctl × n_known` with `n_known` the count of `KNOWN`
exclusions; at `excludes=[]` that is exactly `0.0`, so the ramp is **off** and a fame-free build
takes the production cost function's exact values. **At any deeper depth the ramp is live and fame
is absent, so no deeper depth is measurable here.** Stated, not worked around.

**Timed per pair, served then arm, in one process**, so drift cancels within each pair rather than
only in aggregate.

**The served map's own local median d0 — a quantity §5 records as being on no document — is
supplied here as a by-product: 536.2–610.4 ms across the eight runs.** ⚠ **That 13.8 % spread
between runs minutes apart on one machine is itself the argument for the gate being a RATIO
measured back to back**, and not a comparison against any stored figure. It is also a caution
against any later document quoting a single served-map d0 as *the* figure: this stage measured it
eight times and it moved by a seventh.

---

## 4. `LBA-G1` — and it fires on NOTHING

> **Plain sentence (§5): this map is too big, or too slow, for the machine the app runs on.**

| half | bar | worst built arm | fires |
|---|---|---|---|
| **(a)** projected shipped peak RSS | **1.6 GB** (1,525.9 MiB) — 80 % of the App Runner instance's 2 GB | `LBA-A8` at **657.4 MiB**, **43 % of the bar** | **No, on every arm** |
| **(b)** median d0 wall clock vs the served map's | **2×**, same process, same pairs | `LBA-A8` at **1.860** | **No, on every arm** |

⚠ **The gate reads the MEDIAN alone; p95 is reported beside it because §5 requires it**, and the two
must not be confused. On the `U` row p95 is where the cost concentrates: **2720 ms and 3065 ms,
against 1063–1430 ms on every `V` and `P` arm.**

⚠ **`LBA-A8`'s 1.860 is 93 % of the (b) bar**, and the ratio is monotone in population across the
eight sized arms. **`LBA-A9` was never sized**, so "no arm fires `LBA-G1`" is a statement about the
**eight sized arms** and says nothing about the corner.

⚠ **`LBA-X8`, and it now has two halves.** Every size figure here is a **lower bound** on a shipped
artifact: these builds carry no fame and no clip ids. `metadata_ratio` carries back only the three
`LUX-4` keys, **not `fame_lb` or `deezer_ids`**, so the projected resident figures are lower bounds
too. The margin under (a) is large enough that this is unlikely to be decisive; it is stated rather
than assumed away.

⚠ **`LBA-AM1-O1` holds and is visible in the table.** The cap bounds every arm by its population, so
this statistic moves far more with the **population** column than the threshold column — across the
`V` row the whole threshold range moves projected RSS by 3.5 MiB, while `V`→`P` moves it by ~46 MiB
and `P`→`U` by ~300–410 MiB. **`LBA-G1` is in practice a population gate, and a `V`-row null here is
not evidence that the threshold does not affect size.**

---

## 5. The filter column, said rather than inferred (`LBA-D7`, §2.4)

| rule | arms | `drop_unlistenable` | what the zero means |
|---|---|---|---|
| `V` | `A1`–`A3` | `True`, `…20260805.json` | **inert because applicable** — the payload censused `V` and drops none of it |
| `P` | `A4`–`A6` | `True`, `…20260809.json` | **inert because applicable** — the payload censused `P` and drops none of it |
| **`U`** | `A7`–`A9` | **`False`** | **absent because REFUSED** — `unlistenable_drop.py` raises `PopulationNotCensused` for any archive holding artists the census never evaluated |

**In a configuration dump those look identical and mean opposite things**, which is why the state is
written in words into every arm's result JSON and archive manifest.

⚠ **The other two drop stages have NO guard at all.** `drop_no_release_tail` and
`drop_featured_credit` do not raise on an uncensused population — over `U` they **silently
under-filter** rather than refusing. Both were left at their defaults and the fact is recorded per
arm.

⚠ **The shipped code labels this configuration itself.** `pipeline.py:303-318`'s refusal text says
the alternative is to *"build with `drop_unlistenable=False`, **which is an experimental control and
never a shipping configuration**."* **Every `U` arm here is built in that configuration.** That is
§2.4's warning in the source's own words, and it travels with every `U` sentence.

---

## 6. Each arm's plain sentence, quoted verbatim from §2.2

Fixed before any result existed, so a report whose wording drifts is as visible as a moved number.

- **`LBA-A1`** *(control)* — *the artists the app serves today, connected by our own recomputation
  at the same strength bar ListenBrainz used.*
- **`LBA-A2`** — *the same artists, but a connection is kept when three different people's listening
  supports it instead of four.*
- **`LBA-A3`** — *the same artists, but two people are enough.*
- **`LBA-A4`** — *every artist the deeper crawl found, at ListenBrainz's own bar.*
- **`LBA-A5`** — *every artist the deeper crawl found, at the three-listener bar.*
- **`LBA-A6`** — *every artist the deeper crawl found, at the two-listener bar.*
- **`LBA-A7`** — *every artist anywhere in ListenBrainz's listening data who gets a connection at
  ListenBrainz's own bar — not just the ones our crawl happened to discover.*
- **`LBA-A8`** — *the same, at the three-listener bar.*
- **`LBA-A9`** — *the same, at the two-listener bar.* **The corner**, and the only cell that can say
  *"there is no bigger map to have inside these rules."* **Unbuilt for a resource reason.**

---

## 7. Which §7 reads this stage reaches, and which it does not

**Recorded in the execution log BEFORE any build ran**, with the commit timestamp as the evidence.

| read | run state it needs | reached? |
|---|---|---|
| **`LBA-R0`** | *derived* | **YES** — `LBA-G2`'s projection exceeded the bar for `LBA-A9`; that cell is not built, the lattice is reported **with a hole rather than silently reduced**, and §2.6's barred conclusions apply |
| **`LBA-R1`** | *complete* **and** *sized* | **YES** — **no arm fires `LBA-G1`** |
| `LBA-R2`, `LBA-R3` | *complete* and *sized* | **No — mutually exclusive with `LBA-R1`**, which is why exactly one of the three is read |
| `LBA-R4`, `LBA-R5`–`LBA-R7` | *complete* | **No** — they rest on `LBA-M2` and `LBA-M3`, which this stage does not take |
| `LBA-R8` | *complete* and *censused* | **No** — `LBA-G3` fired; nothing is censused |
| `LBA-R9` | *complete*, *sized* and *censused* | **No** — same |
| `LBA-R4-V` | *derived* | **Not reported as a finding of this design.** §7's own row records it as settled on the committed record **before stage 1**, precisely so it cannot be |

**The lattice is `complete`**: every cell either built or **stopped by `LBA-G2` with its bar
recorded**. It was not reduced by judgement, which §7 says would have put `complete` out of reach
and barred these reads.

### `LBA-R1`, read

> *Plain: every map we could build still fits the machine the app runs on, so size is not what
> decides this.*

⚠ **`LBA-R1`'s text continues *"the decision then rests on `LBA-M2`, `LBA-M3` and `LBA-M4` alone"* —
a statement about where the decision sits, and those three are UNMEASURED here.** No sentence in
this document presents that clause as evidence about them.

⚠ **And it is a statement about the eight SIZED arms.** `LBA-A9` was never built and never sized.

---

## 8. Files

| file | what |
|---|---|
| `s4_build_<arm>.json` | one per cell — the build, its peak, the projection read before it, acceptance, bare size, the filter column |
| `s4_sizing.json` | `LBA-M1`'s table, the calibrations, and `LBA-G1` read per arm |
| `s4_query_cost_<arm>.json` | per-arm d0 timings and `LBA-G1`(b) |
| `s4_pairset.json`, `s4_pairset.tsv` | the pair set, its rule and its sha, pinned before any timing |
| `_points.json` | the six instrumented build points `LBA-G2` projected from |
| `_projections.json` | every projection taken, in order, whether or not it fired |
| `_pins/stage2_verify_pins.json` | the 14 pins, re-verified by this session |
| `_logs/machine_state.tsv` | free physical memory every 20 s across the build chain |
| `_logs/discarded_point_A2_attempt2.json` | the discarded second `LBA-A2` measurement (§2c) |

**Artifacts are gitignored and live at `C:\unsung-fast\lbd-artifacts\`** — `LBA-<arm>.bin` per built
cell, plus `LBA-<arm>-bare.bin` per sized arm. Their sha256s are in each cell's `s4_build_*.json`
and in `s4_sizing.json`.
