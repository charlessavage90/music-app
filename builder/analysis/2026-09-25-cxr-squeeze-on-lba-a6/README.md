# `CXR-M3` / `CXR-M4` repeated on the adopted map: lux4 → lba-a6

**Role: FIGURES OWNER for this re-measurement.** Every number below is owned here. Cite it; do not restate it.

**What this closes:** `docs/superpowers/findings/2026-09-16-cxr-revert-and-the-s4-population.md` §5 item 2.
That item was open because §3b of the same note was an argument from how the map was built, with no
figure under it. This directory supplies the figure. **Nothing else is closed, proposed or recommended here.**

**Scope: a descriptive probe over two artifact files.** No journey was routed, no arm ran, no
threshold is set and nothing is adopted. **Resuming path-quality work is the owner's trigger, never a
session's.** Issue #200 (the owner's request to explore deeper obscurity after several *Dig deeper*
presses) is the context. This is not step 1 of that issue.

**Currency on every figure: FAME PERCENTILE** (`fame_lb_pctl`). That is each artist's ListenBrainz
listener count ranked within its own map's measured population. It is **not** `pop_raw` and **not**
degree. It is also **not** Spotify monthly listeners, which is the currency the owner looked up in #200.

Files:
- `squeeze_lba_a6.py`: every figure below. It refuses (exit 2) on a sha mismatch before it reads anything.
- `squeeze_lba_a6.out.txt`: its output from the run recorded here.

Rerun it from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-25-cxr-squeeze-on-lba-a6/squeeze_lba_a6.py

## Artifact identity

Both files were hashed and matched against the `sha256` field of their own manifest sidecars. The
script refuses to continue on a mismatch, and both matched.

| role | file (in `C:/dev/music-app/builder/scratch/`) | sha256 (matches its sidecar) |
|---|---|---|
| **old**: served before 2026-09-25 | `graph-lux4.bin` | `fd92a7352afb7321e80f3818262d08169fcfb3af1d6841d7ccfca0f5e5740369` |
| **new**: adopted 2026-09-25 | `graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` |
| comparability only | `graph-msw-tu50.bin` (the `CXR-` old map) | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` |

**Comparability check.** lux4 has the same MBIDs, in the same order, and a byte-identical `fame_lb`
list as `graph-msw-tu50.bin`, which was `CXR-M4`'s old map. So the old frame used here **is**
`CXR-M4`'s old frame. The two measurements differ only in the new map.

Both were parsed through the **shipped** `GraphStore.load`, and the percentiles are the shipped
`GraphStore.fame_percentiles` (`api/src/artistpath_api/graph_store.py:148`). They were not
reimplemented. The ramp weight is `ApiConfig.w_known_ramp_fame_pctl`
(`api/src/artistpath_api/config.py:114`), read by the script at run time. Its cost term is
`api/src/artistpath_api/pathfinding.py:131` (the scale, weight × `known` presses) and `:170` (added
per interior artist, target exempt).

**Method.** Copied from `../2026-09-01-cxr-regression-diagnosis/cxr_census.py` (`M3`) and
`cxr_compression.py` (`M4`). The pairing is by MBID, in new-map order. The shift is new percentile
minus old, each in its own map's frame. The eight position bins are unchanged. The gap is the mean of
old-frame ≥ 0.99 minus the mean of old-frame 0.40–0.60, priced as weight × presses × gap.
**One departure:** `CXR-M3`/`M4` paired over every shared artist, measured nulls included. The brief
here drops any shared artist that is null in either map. Both versions are reported. They differ by
one artist, and no figure below changes at the precision shown.

### Forward notes, 2026-09-25, added after the run; nothing was re-run

- **What the figures measure.** "Fame percentile" is the adopted proxy for the *novelty-likelihood*
  construct: how unlikely a typical user is to already know an artist
  (`docs/superpowers/PRODUCT-REQUIREMENTS.md` Definitions, "Obscurity / novelty-likelihood"). No
  figure here is a popularity figure.
- **Fame snapshots differ, and this derivation does not separate their effects.** Each map's
  `fame_lb` comes from a different fetch. The dates below come from the records' own `fetched`
  field, read from a random sample of 400 records per archive:
  - **lux4:** built from `grt-archive-algb.pre-cex-snapshot` (sidecar `build_inputs.archive_dir`).
    Its `fame/` records were fetched **2026-08-02 to 2026-08-05**. This is the served lineage's
    snapshot: the comparability check above found lux4's `fame_lb` byte-identical to `msw-tu50`'s.
  - **lba-a6:** every one of its 87,764 records was fetched fresh on **2026-09-21** into
    `C:\unsung-fast\lbd-archives\S4-A6-fame` (`../2026-09-21-lbd-s4-a6-candidate/README.md` §2–§3),
    shared artists included.

  So the paired shift **bundles the population change with about seven weeks of snapshot age**. The
  two were not separated. Percentiles are rank-based, so growth that is uniform across artists does
  not move them. Only growth that differs from artist to artist could contribute. The size of that
  contribution is unmeasured. The added artists' low median percentile (§1) is the population
  change, and it is consistent with the rise being driven by that change.
- **Materiality, carried from `CXR-M4`.** `../2026-09-01-cxr-regression-diagnosis/README.md`,
  section "`CXR-M4` — the shift is a SQUEEZE…", "Materiality": at twenty presses the ramp is worth
  about five hops of cost and the squeeze about one. **So the 20 % is a real force weakened, not a
  dominant one.** `w_hop` is unchanged (`config.py:82`), so the comparison with hop cost transfers to
  this map. The comparison with similarity cost does not transfer, because lba-a6 replaces every
  similarity score (§3).

---

## 1. Measured

### Populations

| | artists (N) | CSR entries |
|---|---:|---:|
| lux4 | 58,838 | 1,315,684 |
| lba-a6 | 87,394 | 2,490,728 |
| **shared** (by MBID) | **57,909** | |
| only in lux4 | 929 | |
| only in lba-a6 | 29,485 | |

### Measured nulls (`fame_lb` is `None`: ListenBrainz was asked and reported no listeners)

| | nulls | of |
|---|---:|---:|
| lux4 | 92 | 58,838 |
| **lba-a6** | **3** | 87,394 |
| shared, null in lux4 | 1 | |
| shared, null in lba-a6 | 1 | |
| shared, null in both | 1 (the same artist) | |
| **shared, null in either: drops out of the pairing** | **1** | |
| only-in-lba-a6, null | 2 | |
| only-in-lux4, null | 91 | |

The lba-a6 count of 3 agrees with `../2026-09-21-lbd-s4-a6-candidate/README.md` §3.

**Nulls are outside the percentile frame. This was confirmed from source and on the data.**
- *Source:* `graph_store.py:176` builds the frame from non-null values only. `:192` then writes each
  null back as 0.0.
- *Data, both maps* (script, "MEASURED NULLS" block):
  - every null is 0.0, and no NaN survives;
  - recomputing each measured artist's rank against a measured-only frame reproduces the shipped
    percentile **exactly** (`np.array_equal`, asserted);
  - if the nulls had been framed as zeros, the largest rank change would have been 1.56e-03 on lux4
    and 3.43e-05 on lba-a6. So the exclusion is real, and at these null counts it is also immaterial.
- 54 measured lux4 artists and 4 measured lba-a6 artists also sit at 0.0. They are ties at the lowest
  measured count (`side="left"` ranking), not nulls.

### `CXR-M3`: how far each shared artist's fame percentile moved (lba-a6 minus lux4)

| pairing | n | median | mean | rose | fell | p10 | p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **nulls-in-either dropped** | 57,908 | **+0.0745** | **+0.0675** | **99.14 %** | 0.86 % | +0.0186 | +0.1028 |
| CXR-literal (all shared) | 57,909 | +0.0745 | +0.0675 | 99.14 % | 0.86 % | +0.0186 | +0.1028 |
| *`CXR-M3` for reference (msw-tu50 → cxa-adopted)* | *58,793* | *+0.0791* | *+0.0712* | *99.30 %* | | *+0.0199* | *+0.1073* |

The reference row is cited from `../2026-09-01-cxr-regression-diagnosis/README.md`, section
"`CXR-P1` — CONFIRMED…", where it is owned.

### `CXR-M4`: the shift by position in the OLD (lux4) frame, fame percentile, nulls-in-either dropped

| old-frame band | n | old mean | new mean | shift |
|---|---:|---:|---:|---:|
| 0.00–0.20 | 11,074 | 0.1042 | 0.1405 | +0.0363 |
| 0.20–0.40 | 11,656 | 0.3001 | 0.3830 | +0.0829 |
| **0.40–0.60** | 11,718 | 0.5000 | 0.6024 | **+0.1024** |
| 0.60–0.80 | 11,720 | 0.7000 | 0.7830 | +0.0830 |
| 0.80–0.90 | 5,869 | 0.8500 | 0.8966 | +0.0466 |
| 0.90–0.95 | 2,933 | 0.9250 | 0.9491 | +0.0240 |
| 0.95–0.99 | 2,350 | 0.9700 | 0.9797 | +0.0097 |
| **0.99–1.00** | 588 | 0.9950 | 0.9966 | **+0.0016** |

The 59 artists at ≥ 0.999 in the old frame moved +0.0002. The CXR-literal pairing is identical except
that the lowest band has n = 11,075 and a new mean of 0.1404.

### `CXR-M4`: the top-1 % versus mid-scale gap, priced in ramp units (fame percentile × weight × presses)

| | old (lux4) | new (lba-a6) | change |
|---|---:|---:|---:|
| gap, top-1 % minus mid-scale | 0.4950 | **0.3942** | **−20.4 %** |
| *`CXR-M4` for reference (msw-tu50 → cxa-adopted)* | *0.4950* | *0.3897* | *−21.3 %* |

| *Dig deeper* presses | ramp preference for the mid-scale artist, old | new (lba-a6) | *`CXR-M4` extended map, for reference* |
|---:|---:|---:|---:|
| 5 | 0.02475 | **0.01971** | *0.01949* |
| 10 | 0.04950 | **0.03942** | *0.03897* |
| 20 | 0.09899 | **0.07884** | *0.07794* |

The 21.3 % figure the owner quotes is confirmed. It is in
`../2026-09-01-cxr-regression-diagnosis/README.md`, section "`CXR-M4` — the shift is a SQUEEZE, not a
level change, and that is what costs". **The squeeze on lba-a6 is 20.4 / 21.3 ≈ 0.96 of `CXR-M4`'s.**
The weight used is 0.01, read at run time from `config.py:114`.

Where the artists only in lba-a6 sit, in the lba-a6 frame: their median fame percentile is **0.3332**,
against **0.6105** for the shared artists.

This is deterministic arithmetic over two fixed files, not a sample. The analysis-versus-held-out
slice instability that affects routing metrics here does not arise, and no second slice exists to take.

---

## 2. What I infer (inference, labelled)

- **`CXR-M3` (does every artist who was already on the map now look more famous by comparison?)** Yes,
  almost all of them, and by about as much as last time. Adding ~29,500 mostly less-listened-to artists
  pushes nearly every existing artist up the fame scale. They did not become more famous; they now
  have more obscure company below them.
- **`CXR-M4` (is that rise bigger in the middle than at the top, so the "unknown" end and the "famous"
  end get squeezed closer together?)** Yes, in the same shape and at about 96 % of the size. Here is
  what a user would feel. After several *Know them already* / *Dig deeper* presses, the only thing
  still nudging the journey toward artists fewer people listen to is the ramp. On the new map, that
  nudge separates a household-name artist from a middle-of-the-road one about a fifth less strongly
  than it did on the old map. The loss is almost exactly the one measured when the extended map was
  reverted.
- **§3b of the 2026-09-16 note (the construction argument that the squeeze would recur at about the
  same size) is confirmed, with a magnitude:** −20.4 % against −21.3 %.
- **What cuts against reading this as "the new map is worse at depth".** On the reverted map, the
  squeeze did its damage *together with* the added artists being dead ends the router could not pass
  through. That note's §3a measured the dead-end half as largely removed on this population. The owner
  has also passed this map in use, reporting novel artists *more* often (issue #200). So the squeeze
  recurring is one half of the old mechanism coming back, not the old regression coming back. The same
  scale that got squeezed also gained the ~29,500 cheaper-to-want artists, which now sit at a median
  percentile of 0.33 against 0.61, and which the ramp can now reach.
- **And against reading it as the answer to #200.** The owner's observation is about Spotify listener
  counts. Nothing here measures that currency, so this does not show that the squeeze is why his novel
  artists turned out popular on Spotify.

## 3. Weakest link

- **This is a property of two files, not measured routing.** It prices a *static* preference between
  two groups of artists. It does not show which artists a journey actually delivers at 5, 10 or 20
  presses on either map. A routing run on lba-a6 could find that depth journeys land on less-famous
  interior artists than lux4's did, squeeze notwithstanding. That would not falsify the arithmetic,
  but it would falsify any reading of it as a user-visible loss.
- **The load-bearing assumption is that the ramp's pull scales with this particular gap** (top-1 %
  mean minus 0.40–0.60 mean, in the old frame). That choice was inherited from `CXR-M4` for
  comparability. A different pair of bands would give a different percentage. The by-band table shows
  that the shape holds everywhere (largest rise mid-scale, near zero at the top), so I would defend
  the *shape* and give up the exact *percentage* cheaply.
- **Materiality is inherited too, and not re-derived here.** `CXR-M4`'s argument (roughly: at 20
  presses the loss is worth about one hop and a small similarity difference) used the same weights.
  This map changes every similarity score, so how the ramp compares with the other cost terms on
  lba-a6 is **unmeasured**.

## 4. Options and their consequences (no recommendation)

Why this is the owner's: whether a smaller "go obscure" nudge at depth is acceptable is a judgement on
what the app should do (`CLAUDE.md` "Whose decision is it"). He has already ruled the current
behaviour a pass (issue #200, comment of 2026-09-25).

- **Leave it.** §5 item 2 is closed with a figure. The ramp stays about a fifth weaker at depth than it
  would be on a population-stable map. Nothing is spent.
- **Take this into #200 step 1** (the per-artist table split by depth). That would test whether the
  squeeze shows up in what journeys actually deliver. It costs a session. Measuring it this way needs
  no pre-registration, because it decides nothing.
- **Open one of the three parked candidate fixes** from the `CXR-` README's "What is NOT established
  here". These are a degree floor on what the crawl admits, a fame ruler framed on something other than
  the shipped population, and a deeper rather than wider crawl. Of the three, a differently framed
  ruler is the only one that bears directly on the squeeze. **Each needs its own pre-registration and
  his trigger.** Obscurity retunes here have twice regressed in ways only use detected.

## What is NOT established here

- **No figure here says which artists a journey actually delivers** at any depth, on either map. That
  would take a routing harness run on lba-a6.
- **Nothing here says the squeeze is user-visible.** The owner's use gate passed on this map. These
  figures neither contradict nor explain that.
- **Nothing here bears on Spotify listener counts**, which are issue #200's observation. That is a
  different currency.
- **Nothing here says a fix works**, or that one is needed.
- **The depth-0 half** (2026-09-16 note §3c) is untouched.
