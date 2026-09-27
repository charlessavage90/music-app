# Issue #200: what surrounds famous artists on the map, and what Dig deeper does from famous vs mid-scale pairs

**Role: FIGURES OWNER for these two measurements.** Every number below is owned here. Cite it; do not
restate it.

**What this is:** two descriptive measurements over the adopted map. They address two weakest links in
`../2026-09-25-issue-200-served-fame-vs-listeners/README.md` §3: link 1 (depth was tangled with famous
endpoints, and no mid-scale pair was pressed ten or more times) and link 3 (the "map, not weights"
inference rested only on neighbour tables of served artists). **It decides nothing.** No alternative
weights ran, `ApiConfig` was not changed, and nothing is proposed. Resuming path-quality work is the
owner's trigger.

**Currency on every figure: fame percentile** (`fame_lb_pctl`). This is the artist's ListenBrainz
listener count ranked within **its own map's** measured population, 0 to 1. It is not `pop_raw`, not
degree, and not Spotify monthly listeners.

**Forward note, 2026-09-27 later: §3's first bullet has been tested.** Its falsifier ran in
`../2026-09-27-issue-200-ruler-vs-map/README.md`, which owns the result: at the top 1 % the wall
belongs to lba-a6's edges, not to the ruler. Nothing here was re-run or changed.

Files:
- `graph_descriptives.py` produces every figure. It refuses (exit 2) on a sha mismatch before reading
  anything. It takes no command-line arguments.
- `graph_descriptives.out.txt` is its full output from the run recorded here (about 36 minutes, most of
  it the mid-scale routing).

Rerun it from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-issue-200-graph-descriptives/graph_descriptives.py

## Inputs and identity

Each file was hashed and matched against the `sha256` field of its own manifest sidecar. lba-a6 was
also matched against the pinned value in the script.

| role | file (in `C:/dev/music-app/builder/scratch/`) | sha256 |
|---|---|---|
| adopted map (A and B) | `graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` |
| previous map (A only) | `graph-lux4.bin` | `fd92a7352afb7321e80f3818262d08169fcfb3af1d6841d7ccfca0f5e5740369` |
| comparability only | `graph-msw-tu50.bin` | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` |

**Comparability check (why the third file is here).** The JFX reachability measurement
(`../2026-08-09-jfx-prereg-critique/README.md`, "Result") was run on `graph-msw-tu50.bin`, not on
lux4. The script checked that lux4 and msw-tu50 have the same MBIDs in the same order, identical CSR
`offsets` and `neighbours`, and identical `fame_lb_pctl`. All three were true. So Measurement A on lux4
measures the same graph and the same frame that the JFX critique measured.

## Instrument

- **Parsing and percentiles:** the shipped `GraphStore.from_bytes` and `GraphStore.fame_percentiles`
  (`api/src/artistpath_api/graph_store.py:148`). Not reimplemented. The script asserts that the store's
  `fame_lb_pctl` equals `fame_percentiles` applied to the artifact's raw `fame_lb` list. Each map is
  in its own frame, which is what production does.
- **Nulls** (`fame_lb` is `None`, stored by the shipped code as 0.0 and excluded from the frame):
  identified from the raw metadata blob. lba-a6 has 3; lux4 has 92.
  - *As a centre (A):* only measured artists can be centres. A null is stored as 0.0, so it could
    never reach the 0.90 bar anyway.
  - *As a neighbour (A):* excluded from both numerator and denominator in the headline shares and zero
    counts. This is the JFX critique's rule. A variant column keeps them in and counts them below both
    bars.
  - *As an endpoint (B):* pairs are drawn from measured artists only.
  - *As an interior (B):* excluded from the per-journey median and counted.
- **Routing (B):** the shipped `artistpath_api.pathfinding.find_journey` with the default `ApiConfig()`,
  as in `../2026-08-09-jfx-prereg-critique/jfx_route.py`. The script prints the ramp, hop and floor
  weights at run time. It imports only `victim_key` from
  `../2026-08-03-cap-reevaluation/cre_ladder.py`, after the shipped modules. It asserts that
  `artistpath_api.pathfinding` resolves under this worktree's `api/src` and is the same module object
  after that import. `cre_ladder.journey` / `find_path_mirror` are not called.
- **Press convention (B):** every press is KNOWN ("Dig deeper"). After each journey, the interior
  artist chosen by `victim_key` is added as a KNOWN exclusion. Exclusions are cumulative. The ladder
  runs from 0 to 20 presses and is recorded at 0, 5, 10 and 20. `victim_key` takes the highest fame
  percentile first, with nulls last, ties broken by `pop_raw` and then MBID. It uses fame with NaN at
  nulls, built as in `../2026-08-09-jfx-prereg-critique/jfx_g1a_reverify.py`. **As `jfx_route.py`
  warns, this deletes the most famous interior at every press, so part of any descent is mechanical.**
- **Pair draw (B), fixed in the script before the run:** seed `20260927`, one `random.Random`, FAMOUS
  drawn first and then MID. The pool is measured artists in the band, in ascending node id. Each draw is
  `rng.sample(pool, 2)` taken as (source, target), and a repeated unordered pair is rejected. There are
  40 pairs per set. FAMOUS means both endpoints have fame percentile ≥ 0.95 (pool 4,370). MID means both
  are in [0.30, 0.70] (pool 34,957).

## 1. Measured only

### A. Neighbours of top artists below two fame-percentile bars, each map in its own frame

| | lba-a6 | lux4 |
|---|---:|---:|
| artists (N) | 87,394 | 58,838 |
| CSR entries | 2,490,728 | 1,315,684 |
| null fame | 3 | 92 |

**Top decile (fame percentile ≥ 0.90).**

| | lba-a6 | lux4 |
|---|---:|---:|
| artists | 8,740 | 5,875 |
| median neighbour count (p10, p90) | 49 (15, 50) | 48 (13, 50) |
| centres with ≥ 1 null neighbour | 0 | 277 |
| share of neighbours < 0.9 fame percentile: median | 0.4861 | 0.4600 |
| — p10 | 0.0400 | 0.1111 |
| — p90 | 0.8049 | 0.7857 |
| — mean | 0.4554 | 0.4541 |
| **zero neighbours < 0.9 fame percentile: count (fraction)** | **629 (0.0720)** | **63 (0.0107)** |
| median count of neighbours < 0.9 | 17 | 15 |
| share < 0.9, nulls kept and counted below: median | 0.4861 | 0.4600 |
| share of neighbours < 0.5 fame percentile: median | 0.0440 | 0.0606 |
| — p10 | 0.0000 | 0.0000 |
| — p90 | 0.3061 | 0.2222 |
| — mean | 0.1071 | 0.0939 |
| **zero neighbours < 0.5 fame percentile: count (fraction)** | **3,106 (0.3554)** | **1,097 (0.1867)** |
| median count of neighbours < 0.5 | 2 | 2 |
| share < 0.5, nulls kept and counted below: median | 0.0440 | 0.0612 |

**Top 1 % (fame percentile ≥ 0.99).**

| | lba-a6 | lux4 |
|---|---:|---:|
| artists | 874 | 588 |
| median neighbour count (p10, p90) | 49 (42, 50) | 49 (34, 50) |
| centres with ≥ 1 null neighbour | 0 | 28 |
| share of neighbours < 0.9 fame percentile: median | 0.0208 | 0.1429 |
| — p10 | 0.0000 | 0.0408 |
| — p90 | 0.3689 | 0.4000 |
| — mean | 0.1075 | 0.1952 |
| **zero neighbours < 0.9 fame percentile: count (fraction)** | **381 (0.4359)** | **9 (0.0153)** |
| median count of neighbours < 0.9 | 1 | 6 |
| share < 0.9, nulls kept and counted below: median | 0.0208 | 0.1429 |
| share of neighbours < 0.5 fame percentile: median | 0.0000 | 0.0482 |
| — p10 | 0.0000 | 0.0000 |
| — p90 | 0.0609 | 0.1667 |
| — mean | 0.0230 | 0.0751 |
| **zero neighbours < 0.5 fame percentile: count (fraction)** | **706 (0.8078)** | **84 (0.1429)** |
| median count of neighbours < 0.5 | 0 | 2 |
| share < 0.5, nulls kept and counted below: median | 0.0000 | 0.0482 |

On lux4, the < 0.9 rows reproduce the JFX critique's figures ("Result" section of
`../2026-08-09-jfx-prereg-critique/README.md`): the zero counts 63 of 5,875 and 9 of 588, and the mean
share. That was checked against that section; the figures are owned there.

### B. Routing on lba-a6: median interior fame percentile by Dig-deeper presses

Every ladder in both sets reached 20 presses. None stopped on an empty interior or on no path. Stop
rule at 0 presses: FAMOUS 39 natural and 1 forced (Motörhead → ZZ Top); MID 40 natural. No null fame
artist appeared in any interior at the recorded depths (0 excluded in every cell).

**Summary by set and depth.** Each pair contributes one value: the median fame percentile of its
interior artists.

| set | Dig-deeper presses | pairs | median of pair medians (fame percentile) | p10 | p90 | median interior count |
|---|---:|---:|---:|---:|---:|---:|
| FAMOUS | 0 | 40 | 0.994 | 0.977 | 0.998 | 6 |
| FAMOUS | 5 | 40 | 0.993 | 0.980 | 0.996 | 6 |
| FAMOUS | 10 | 40 | 0.991 | 0.969 | 0.997 | 6 |
| FAMOUS | 20 | 40 | 0.992 | 0.928 | 0.996 | 5 |
| MID | 0 | 40 | 0.966 | 0.787 | 0.992 | 9 |
| MID | 5 | 40 | 0.933 | 0.762 | 0.983 | 8 |
| MID | 10 | 40 | 0.906 | 0.750 | 0.990 | 8 |
| MID | 20 | 40 | 0.877 | 0.713 | 0.979 | 8 |

**Paired change from 0 to 20 presses.** For each pair: its 20-press interior median minus its 0-press
interior median, in fame percentile.

| set | pairs | median change | p10 | p90 | fell | rose | unchanged | two-sided sign test p (fell vs rose) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAMOUS | 40 | −0.003 | −0.063 | +0.006 | 28 | 11 | 1 | 0.0095 |
| MID | 40 | −0.028 | −0.202 | +0.018 | 30 | 10 | 0 | 0.0022 |

The sign-test p was computed after the run, from the fell and rose counts in the table (exact binomial,
ties dropped). It is not in `graph_descriptives.out.txt`.

**Pairs whose 20-press interior median is below a fame-percentile bar.**

| set | < 0.9 | < 0.5 |
|---|---:|---:|
| FAMOUS | 4 of 40 (0.100) | 0 of 40 (0.000) |
| MID | 23 of 40 (0.575) | 0 of 40 (0.000) |

**Per-pair tables** (source, target and their fame percentiles; the interior median at 0, 5, 10 and 20
presses; interior counts; stop rule) are in `graph_descriptives.out.txt` under "FAMOUS: per pair" and
"MID: per pair". They are not repeated here.

**Scope of these figures.** They come from one seeded draw of 40 pairs per set, on one map. No second
slice was run.

## 2. What I infer from it (inference)

*Written by the coordinating session, not the analyst. The analyst's brief was derivation only.*

- **The very top of the map is walled in again.** Take the most-listened 1 % of artists, the
  Radiohead and Pink Floyd tier. On the previous map almost every one of them had several connections
  to artists outside the top tenth. On the map now serving, close to half have **none**. From there,
  a journey's first step can only go to another top-tenth artist. The JFX critique found this wall
  gone on the previous map, and **§1 A shows it is present on lba-a6 at the top 1 %**. It is only
  weakly present across the wider top tenth: the typical top-tenth artist still has about half its
  connections outside that tier, and only a small minority have none.
- **The famous-to-famous gradient is near zero.** Take two artists who are both more listened than
  95 % of the map and press *Dig deeper* twenty times. The artists in the middle end up as widely
  listened as they started. Most journeys drift down a little and a few drift up; the typical drift
  is too small to hear. That is the flatness #238 saw in the owner's own use, and it now holds on
  randomly drawn famous pairs, not only the ones he chose. **The gradient is not exactly zero, but it
  is close enough that REQ-13's "a press that swaps one famous artist for another equally famous one
  has delivered nothing" describes what happens.**
- **Mid-scale pairs do descend, but from the top, and they never get down to their own level.** Take
  two mid-table artists, each listened to by about half the map. Before any press, the journey
  between them runs through artists in roughly the top few percent: far more famous than either
  artist the user picked. Twenty presses bring the middle down noticeably, but it still sits in
  roughly the top eighth of the map. No journey in either set ended with a typical middle artist in
  the less-listened half. So *Dig deeper* has some grip when the endpoints are not famous. What it
  starts from is a journey that has already climbed to the famous core.
- **Both measurements point the same way, and neither separates map from weights.** A says the
  neighbourhood of the very top has few exits. B says a journey climbs to the famous core even from
  mid-scale endpoints, and presses barely pull it out from famous ones. The famous endpoints in B are
  mostly in the top 5 %, not the top 1 %, and A says that tier is *not* walled in. That makes it
  less likely the wall alone explains the flatness, and more likely the route's cost also favours
  the famous core. This is inference, not a test.
- **For #200 step 1's weakest links:**
  - **Link 1** (depth tangled with famous endpoints) is answered. Pairs chosen at random behave like
    the owner's, and mid-scale pairs behave differently.
  - **Link 3** ("the map, more than the weights") is **weakened, not confirmed**. The map does wall
    in the top 1 %. But the flatness also holds a tier below that, where the map is not walled in.

## 3. Weakest link

- **A does not separate the ruler from the map.** Every fame percentile is measured in its own map's
  population. lba-a6's population is larger and differently made, and
  `../2026-09-25-cxr-squeeze-on-lba-a6/README.md` measured mid and upper-mid artists rising in
  percentile on it. So a neighbour who sat just below the 0.9 bar on lux4 can sit above it on
  lba-a6 with no edge changing. "The top 1 % is walled in again" could be partly or wholly the
  ruler moving.
  - **What would falsify it:** score lba-a6's edges with lux4's percentiles over the artists the two
    maps share. If the top-1 % zero count falls back near lux4's, it is the ruler, not the map.
  - **I would abandon this cheaply.** It is the claim in §2 that most needs the decomposition.
- **The press rule favours descent.** Each press removes the most famous artist in the middle, which
  no real user does on purpose (`jfx_route.py`'s warning).
  - **The famous-pair flatness is therefore conservative:** a real user's presses would move it less,
    not more. I would defend that part.
  - **Part of the mid-scale descent is mechanical, by an amount not measured.** I would give up the
    size of that descent readily, and "it descends at all" less readily.
- **The pairs are random, not chosen.** Users pick endpoints they know. 40 pairs per set came from
  one seeded draw on one map, with no second draw.
- **The link from A to B is inferred, not measured.** Nothing here routes with the wall removed, and
  nothing re-prices a route. Saying which of map and cost does the work needs an arm, and an arm
  needs a pre-registration and the owner's trigger.

## 4. Options and their consequences

**Why the decision is his:** whether "better" includes audience size, and whether to spend a
pre-registration or a map rebuild on it, is the owner's (issue #200 *Whose*; `CLAUDE.md`'s "what
counts as better").

- **(a) Rule on #200's definition question with this and step 1 in hand.** Step 1's option (a) or
  (b) still applies. What changes: "Dig deeper does little on famous pairs" is now established on
  random pairs, not only on his, and the famous-to-famous defect ruling (`PRODUCT-REQUIREMENTS.md`
  §8, 2026-07-29) is visibly live on the map now serving.
- **(b) Run the ruler-versus-map decomposition first** (§3, first bullet). It is analysis only, with
  no routing, about the size of Measurement A. It decides whether "the top is walled in again"
  belongs to the map or to the ruler, which decides whether step 1's option (c), a map-construction
  change, is even aimed at something real.
- **(c) Pre-register a routing change** (step 1's option (b)). On §1 B, it would be aimed at famous
  pairs, where presses currently deliver nothing. It would need to be tested against the
  mid-scale-pair behaviour too, since those pairs already climb above their endpoints before any
  press. The `CXR-` history applies: obscurity retunes have twice regressed in ways only use caught.
- **(d) Treat it as a map question** (step 1's option (c)): give the very top some less-listened
  neighbours at build time. §1 A names the tier where the wall is (top 1 %), and (b) above says
  whether it is real. This is larger and slower, and touches the parked `SEL-` / `TAS-` strands.
- **(e) One journey by hand** (step 1's option (d), his hands). §1 B now answers its question
  in-process for random pairs. Pressing a mid-scale pair himself would still test what the press
  rule cannot: whether a real user's choice of what to press moves it more or less.
- **A standing sentence goes stale either way.** `PRODUCT-REQUIREMENTS.md` §8's boxed note says, in
  fame currency, "the barrier is gone". That was measured on the previous map. At the top 1 % on
  lba-a6 it does not hold (§1 A), pending (b). The document is his requirements layer, so this
  session has not edited it. `docs/README.md`'s row for this directory carries the warning.
