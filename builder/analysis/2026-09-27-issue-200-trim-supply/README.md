# Issue #200: is the top-1 % wall on lba-a6 already in the archived supply, or made by the trim?

**Role: FIGURES OWNER for this decomposition.** Every number below is owned here. Cite it; do not
restate it.

**Answer by the fixed reading rule: `SUP-R1`, supply present, trim removed it.** Almost every
most-listened-1 % artist's archived list names artists below 0.9 fame percentile who are on the map
(1 of 874 has none). The `trimmed_union` step (its own top-50 selection and then the 50-connection
ceiling) is what leaves 381 of 874 with none.

**What this is:** a look inside the one build that produced `graph-lba-a6.bin`. It follows up the
first bullet of `../2026-09-27-issue-200-ruler-vs-map/README.md` §3, "'Edges' is a bundle". **It
decides nothing.** No journey was routed, `ApiConfig` was not read or changed, no shipped code,
config or archive was changed, and nothing is proposed. Resuming path-quality work is the owner's
trigger. There is no pre-registration. The reading rule below was fixed by the coordinating session
before the run.

**Currency on every figure: fame percentile, lba-a6 frame.** That is an artist's ListenBrainz
listener count ranked 0 to 1 within lba-a6's own measured population, via the shipped
`GraphStore`. It is not `pop_raw`, not degree, and not Spotify monthly listeners.

Files:
- `trim_supply.py` produces every figure. It refuses (exit 2) on a sha mismatch before reading
  anything, and (exit 3) if any reproduction assertion fails. It takes no command-line arguments.
- `trim_supply.out.txt` is its full output from the run recorded here: 20.3 min wall time, of
  which 16.2 min was the build.

Rerun it from `builder/`:

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-27-issue-200-trim-supply/trim_supply.py

## Inputs and identity

| role | location | sha256 | checked against |
|---|---|---|---|
| similarity archive | `C:\unsung-fast\lbd-archives\S4-A6\MANIFEST.json` | `950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3` | pin (`../2026-09-21-lbd-s4-a6-candidate/cand_build.py`), before **and** after the run |
| fame overlay | `C:\unsung-fast\lbd-archives\S4-A6-fame` | not hashed (as in `cand_build.py`) | the build's output is asserted equal to the served map |
| population P | `C:\unsung-fast\lbd-archives\population_cxa_mbids.txt` | `1bbff8fcfde78a07d276f727ccaf048c73da4bfd27709b64f6f6894d6d4d2d7b` | the archive manifest's `population.file_sha256` |
| served map | `C:/dev/music-app/builder/scratch/graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` | its sidecar **and** the pin |

## Instrument

- **Build: shipped code, not a reimplementation.** The shipped `build_from_archive`, with
  `cand_build.py`'s exact config: `CANDIDATE_ALGORITHM`, `require_fame=True`,
  `drop_unlistenable=True`, drop list `unlistenable_drop_algb_20260809.json`, and every other field
  at its default. The printed config is `trimmed_union`, `union_top_j` 50, `union_degree_ceiling`
  50, damping 0.0, `p99_log_clip`, and all four drop flags on. The archive is wrapped the same way:
  `ReadOnlyArchive` on both halves, composed by `FameOverlayArchive` (copied from `cand_build.py`),
  source `LbdBulkSource`.
- **Capture.** Pass-through wrappers were placed in the `artistpath_builder.pipeline` module
  namespace. Each records its inputs and outputs and returns the original's result unchanged. The
  wrapped names are `trimmed_union_cap`, `largest_component`, `harvest_identities`,
  `load_drop_mbids`, `load_featured_credit_drop_mbids` and `load_unlistenable_list`. All were
  restored after the build.
- **Reproduction assertions (all passed; exit 3 otherwise).**
  - The built node order and CSR `offsets` and `neighbours` equal `graph-lba-a6.bin` as read by the
    shipped api `GraphStore`.
  - The `largest_component` output equals lba-a6's node set.
  - Every node's row after the ceiling trim equals its served row.
  - The pre-Pass-1 drop sets, rebuilt from the captured identities and drop lists with the shipped
    `is_special_purpose`, give exactly the cap's input node set.
  - `fame_lb_pctl` equals `GraphStore.fame_percentiles` on the raw `fame_lb`.
  - The SUP-S5 zero counts reproduce `../2026-09-27-issue-200-graph-descriptives/README.md` §1 A in
    all four tier × bar cells. Those figures are owned there.
- **Trim re-implementation (attribution only).** The body of `trimmed_union_cap` was copied with
  instrumentation added. It exposes the pre-ceiling union (SUP-S3) and records which endpoint's
  ceiling processing deleted each edge. Its output was **asserted identical to the shipped
  function's output on all 87,764 input nodes**. The loop order follows the shipped code: nodes are
  sorted by `(-degree, mbid)` on the union degree *before* any deletion.
- **Percentiles and nulls.** Every fame percentile comes from the shipped `GraphStore` in lba-a6's
  frame. Only lba-a6 nodes have one, so every stage from SUP-S1 onwards counts nodes only. The null
  rule is the one in the graph-descriptives README. A null (3 on lba-a6) cannot be a centre. As a
  candidate it is excluded from every count and reported ("null-fame candidates excluded").
- **Centres.** Top 1 % = fame percentile ≥ 0.99 (874). Top decile = ≥ 0.90 (8,740). Bars are 0.9
  and 0.5.
- **S0.** The centre's payload is parsed with the shipped `LbdBulkSource.parse`, with the centre
  itself excluded (0 self-rows were found).

### The brief's archive description, against the code (found by this run)

The brief said each archived list is "at most 100 long". **It is not.** The top-1 % lists have a
median length of 1,144 and a maximum of 32,646 (§1 (a)). The emitter
(`../2026-09-10-lbd-supply/emit_archive.py`, its DuckDB query under "the neighbour lists are
assembled INSIDE DuckDB, both directions") writes every P-filtered pair **in both directions**
(`UNION ALL` of `(mbid0, mbid1)` and `(mbid1, mbid0)`). So an artist's archived list is every pair it
takes part in, from either end. It is not only the artist's own ranked cut. Whatever `limit` 100
bounds upstream in the derived pair table, it does not bound the archived list of a much-listed
artist. That is not measured here. Two consequences are measured:
- Every "rescuer" (an artist ranking the centre in its own top 50) is already in the centre's
  SUP-S1: "rescue, not already in S1" is 0 in every cell.
- The "union candidate set" (S1 ∪ rescue) therefore equals S1 in every cell.

### Stages (identifier series `SUP-`, checked free across all refs; fixed before the run)

| stage | what it is | plain sentence |
|---|---|---|
| `SUP-S0` | the centre's raw archived list (P-filtered), all entries | *everyone the listening data names as similar, as it arrived in the archive* |
| `SUP-S1` | S0 restricted to lba-a6 nodes. **This is "pre-trim supply".** | *the similar artists who are on the map at all* |
| `SUP-S2` | the centre's own top-50 (`top_j`) by the cap's ranking | *the ones it ranks highly enough to claim itself* |
| `SUP-S3` | the union before the ceiling: own top-50 plus rescued edges (other artists who rank the centre in THEIR top 50) | *everyone connected before the fifty-connection limit is applied* |
| `SUP-S4` | after the ceiling trim | |
| `SUP-S5` | after the component prune = served (asserted equal to lba-a6's row) | |

**Held constant:** one map, one archive, one config. The stages are successive steps of one
deterministic build: S0→S1 node restriction, S1→S2 top-j, S2→S3 union rescue, S3→S4 ceiling, S4→S5
component prune. The frame is lba-a6's at every stage, with no re-ranking between stages.

**How the S4→S5 prune and the S0→S1 restriction interact.** An artist removed by the
largest-component prune is not a node, so it has no percentile in lba-a6's frame. It is therefore
absent from S1 and every later stage, and is counted once among S0's non-node entries as "lost to
largest-component prune". Every centre is a node, and a node's post-ceiling neighbours are all in
its own component. So SUP-S4 equals SUP-S5 for every centre, and the prune removes nothing at the
centre stage. This was asserted for each centre, not assumed.

### Reading rule (fixed before the run, by the coordinating session; applied here verbatim)

Headline metric, top 1 %, bar 0.9: `Z_pre` = fraction of top-1 % centres with zero below-0.9
candidates in `SUP-S1`; `Z_post` = the same at `SUP-S5` (should reproduce 0.4359 / 381 of 874 — owned
by graph-descriptives; reproduce, don't restate as new).
- `SUP-R1` **"supply present, trim removed it"** — the median top-1 % centre has ≥ 1 below-0.9
  candidate in S1 AND `Z_pre ≤ Z_post / 3` (the trim creates at least two-thirds of the wall). Plain:
  *most famous artists do have less-listened similar artists in the data, and the fifty-connection
  rule is what throws them away.*
- `SUP-R2` **"supply absent"** — `Z_pre ≥ 2·Z_post / 3` (at least two-thirds of the wall exists before
  any trimming). Plain: *for most walled-in famous artists, the listening data never named a
  less-listened similar artist in the first place, so the trim had nothing to remove.*
- `SUP-R3` — neither clause holds: say "both", with the shares. Plain: *the wall is partly in the data
  and partly made by the trim.*

The 2/3 share matches the ruler-vs-map attribution rule. Report the same arithmetic for bar 0.5 and
for the top decile, without a verdict. **Scope bar (LBA-X3 and the manifest fact above):** `SUP-R2`
may only be stated as "absent from the archived limit-100 list", never as "not in the listening data"
— the upstream limit-100 cut and P-filter are not visible here.

## 1. Measured only

All figures are in fame percentile, lba-a6 frame. The source is `trim_supply.out.txt`.

### Reading rule result

| tier | bar | `Z_pre` (SUP-S1): count / fraction | `Z_post` (SUP-S5): count / fraction | median S1 below-bar count | Z_pre ÷ Z_post | R1 clause | R2 clause | verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| **top 1 %** | **0.9** | **1 / 874 = 0.0011** | **381 / 874 = 0.4359** | **786** | **0.0026** | **true** | **false** | **`SUP-R1`** |
| top 1 % | 0.5 | 7 / 874 = 0.0080 | 706 / 874 = 0.8078 | 296 | 0.0099 | true | false | no verdict (not headline) |
| top decile | 0.9 | 32 / 8,740 = 0.0037 | 629 / 8,740 = 0.0720 | 121 | 0.0509 | true | false | no verdict (not headline) |
| top decile | 0.5 | 275 / 8,740 = 0.0315 | 3,106 / 8,740 = 0.3554 | 43 | 0.0885 | true | false | no verdict (not headline) |

The `Z_post` figures reproduce graph-descriptives §1 A, where they are owned.

### Zero fraction at every stage (centres with no candidate below the bar)

| stage | top 1 %, < 0.9 | top 1 %, < 0.5 | top decile, < 0.9 | top decile, < 0.5 |
|---|---:|---:|---:|---:|
| SUP-S1 | 1 (0.0011) | 7 (0.0080) | 32 (0.0037) | 275 (0.0315) |
| SUP-S2 | 617 (0.7059) | 868 (0.9931) | 2,279 (0.2608) | 6,965 (0.7969) |
| SUP-S3 | 2 (0.0023) | 14 (0.0160) | 93 (0.0106) | 512 (0.0586) |
| SUP-S4 | 381 (0.4359) | 706 (0.8078) | 629 (0.0720) | 3,106 (0.3554) |
| SUP-S5 | 381 (0.4359) | 706 (0.8078) | 629 (0.0720) | 3,106 (0.3554) |
| rescue candidates (before the ceiling) | 3 (0.0034) | 14 (0.0160) | 116 (0.0133) | 524 (0.0600) |
| rescue candidates surviving to S5 | 381 (0.4359) | 706 (0.8078) | 644 (0.0737) | 3,121 (0.3571) |
| union S1 ∪ rescue | 1 (0.0011) | 7 (0.0080) | 32 (0.0037) | 275 (0.0315) |

### Below-bar candidate counts per centre: median (p10, p90), mean

| stage | top 1 %, < 0.9 | top 1 %, < 0.5 | top decile, < 0.9 | top decile, < 0.5 |
|---|---|---|---|---|
| SUP-S1 | 786 (64, 5,171), 1,898.08 | 296 (23, 2,116), 752.72 | 121 (15, 849), 411.84 | 43 (3, 353), 165.71 |
| SUP-S2 | 0 (0, 3), 0.79 | 0 (0, 0), 0.01 | 4 (0, 20), 7.08 | 0 (0, 2), 0.53 |
| SUP-S3 | 298 (27, 1,879), 736.06 | 116 (10, 828), 312.04 | 59 (7, 360), 174.29 | 21 (1, 157), 73.49 |
| SUP-S4 = S5 | 1 (0, 15), 4.73 | 0 (0, 3), 0.91 | 17 (1, 37), 18.19 | 2 (0, 11), 3.77 |
| rescue (before the ceiling) | 297 (27, 1,879), 735.88 | 116 (10, 828), 312.04 | 56 (6, 359), 172.41 | 20 (1, 157), 73.41 |
| rescue, not already in S1 | 0 (0, 0), 0.00 | 0 (0, 0), 0.00 | 0 (0, 0), 0.00 | 0 (0, 0), 0.00 |
| rescue surviving to S5 | 1 (0, 15), 4.65 | 0 (0, 3), 0.91 | 17 (1, 35), 17.32 | 2 (0, 11), 3.72 |

The minimum S1 below-bar count is 0 in every cell. The maximum is 27,558 below 0.9 and 12,726
below 0.5, identical in both tiers (whether it is the same centre was not checked).

### What happens to the S1 below-bar candidates (pooled over centres)

| | top 1 %, < 0.9 | top 1 %, < 0.5 | top decile, < 0.9 | top decile, < 0.5 |
|---|---:|---:|---:|---:|
| S1 below-bar entries | 1,658,922 | 657,881 | 3,599,445 | 1,448,340 |
| … in the centre's own top-50 (S2) | 694 | 10 | 61,877 | 4,667 |
| … outside its own top-50 but rescued | 642,624 | 272,710 | 1,461,386 | 637,622 |
| … neither (never enter the union) | 1,015,604 | 385,161 | 2,076,182 | 806,051 |
| survive to S5: count (share) | 4,132 (0.0025) | 795 (0.0012) | 158,955 (0.0442) | 32,963 (0.0228) |
| survive to S5: per-centre share, median (over centres with ≥ 1) | 0.0007 (873 centres) | 0.0000 (867) | 0.1944 (8,708) | 0.0488 (8,465) |
| S3 below-bar deleted by the ceiling | 639,186 | 271,925 | 1,364,308 | 609,326 |
| … by the centre's own ceiling | 639,100 | 271,925 | 1,355,522 | 609,128 |
| … by the neighbour's ceiling | 86 | 0 | 8,786 | 198 |
| rescue direction: below-bar rescuers | 643,161 | 272,720 | 1,506,878 | 641,635 |
| … surviving the ceiling (share) | 4,061 (0.0063) | 795 (0.0029) | 151,356 (0.1004) | 32,507 (0.0507) |

### SUP-S0: raw archived list, and the fate of its entries

| | top 1 % (874 centres) | top decile (8,740 centres) |
|---|---|---|
| S0 length: median (p10, p90), mean, min–max | 1,144 (180, 6,491), 2,496.86, 100–32,646 | 225 (109, 1,081), 581.45, 3–32,646 |
| S1 length: median (p10, p90), mean, min–max | 1,144 (180, 6,482), 2,493.11, 100–32,604 | 225 (109, 1,079), 580.87, 3–32,604 |
| self-rows in S0 / centres with duplicate MBIDs | 0 / 0 | 0 / 0 |
| S0 entries, pooled | 2,182,258 | 5,081,848 |
| → lba-a6 node (enters S1) | 2,178,981 (0.9985) | 5,076,804 (0.9990) |
| outside P | 0 | 0 |
| special-purpose (excluded before Pass 1) | 0 | 0 |
| nameless / no identity row (excluded before Pass 1) | 0 | 0 |
| no archived payload of its own | 0 | 0 |
| no-release-tail drop | 0 | 0 |
| featured-credit drop | 0 | 0 |
| un-listenable drop (20260809) | 0 (recorded as inert on P; confirmed) | 0 |
| lost to largest-component prune | 3,277 (0.0015), at 582 centres | 5,044 (0.0010), at 1,666 centres |
| null-fame candidates excluded: S1 / S3 / S5 | 17 / 17 / 0 | 33 / 33 / 0 |

**Build-wide (not per centre).** The run found 87,764 payloads. Every pre-Pass-1 drop removed 0
payload-holders (special-purpose, nameless, no-release, featured-credit, un-listenable). All 87,764
entered the cap, and 370 were lost to the largest-component prune. That leaves 87,394 nodes and
2,490,728 CSR entries. P has 88,685 MBIDs.

**Stability.** This is deterministic arithmetic over one build of one archive, not a sample. There
is no second slice to take. No random null was built: the stages are the baselines.

**Note on the scope bar above (coordinating session, after the run).** It says "the archived limit-100
list" because the brief misdescribed the archive (see "The brief's archive description, against the
code"). The correct wording is "the archived two-direction list". `SUP-R2` did not fire, so no
sentence here depends on it. The rule is left as it was fixed.

## 2. What I infer from it (inference)

*Written by the coordinating session, not the analyst. The analyst's brief was derivation only.*

- **The listening data does connect famous artists to less-listened ones. The map-building step
  throws those connections away.** Take the most-listened 1 % of artists, the Radiohead and Pink
  Floyd tier. Before trimming, all but one of them has less-listened artists among its
  similar-artist candidates, and the typical one has hundreds. After trimming, close to half have
  none. By the rule fixed before the run (`SUP-R1`: *most famous artists do have less-listened
  similar artists in the data, and the fifty-connection rule is what throws them away*), the wall is
  made by the trim, not by missing data. The same held, without a verdict, at the 0.5 bar and across
  the wider top tenth.
- **How it happens, in two steps.** First, when a famous artist picks its own fifty closest
  artists, it picks almost only other famous artists: seven in ten of the top 1 % pick no
  less-listened artist at all. Second, many less-listened artists pick the famous one among *their*
  fifty. The build's rule keeps a connection if either side picks the other, so those would survive.
  But each artist is then held to fifty connections, and the famous artist has hundreds. It keeps
  its strongest fifty, which are the famous ones. Nearly every deletion happens at the famous
  artist's own limit, not at the smaller artist's.
- **Why the strongest are the famous ones.** The build ranks connections on raw co-listening
  strength, with no correction for how much an artist is played overall (damping is 0.0, §2.3 of the
  adoption pre-registration). A famous artist is co-listened with other famous artists more than with
  anyone else, simply because more people play both. So under a fifty-connection limit, the
  less-listened connections always lose.
- **What a user would see.** A journey starting from a household name has, in about half of cases,
  no first step that leaves the most-listened tenth. The data that could provide that step exists.
  It is not on the map.
- **Against the ruler-vs-map README's open question.** That README's §3 first bullet left "the
  map's connections" as a bundle of new similarity scores and the wider crawl crowding the top
  slots. This result shows the mechanism inside the current map: competition for fifty slots at the
  famous artist's own limit, ranked on raw co-listening. It does **not** say why the previous map
  was open, because nothing here was measured on lux4.

## 3. Weakest link

- **"Supply" counts candidates, not good candidates.** The archive holds pairs that at least two
  listeners support (threshold 3). A less-listened artist that lists a famous one among its fifty
  may be naming the famous artist because everyone plays it, not because they sound alike. So some
  of the hundreds of discarded connections are probably noise, and nothing here measures how many.
  - **What would falsify "the data is there" in the sense that matters:** the discarded below-bar
    candidates of top-1 % artists turning out, on a listen or a coherence measure, to be no more
    similar than random artists at the same fame level. I would expect a sizeable fraction to be
    weak. I would **not** expect that of all of them, given the numbers involved (a median of 786
    per famous artist).
  - **I would defend** the structural claim: the trim, not missing data, makes the wall. That is
    arithmetic over one deterministic build that reproduces the served map exactly.
  - **I would give up cheaply** any suggestion that the discarded connections are *good* ones.
- **The archive is two-directional, which the brief did not expect.** Each list is every pair the
  artist takes part in, from either end (`emit_archive.py`'s `UNION ALL`). So "pre-trim supply" is
  mostly other artists naming the famous one, and much less the famous artist's own cut. This is
  what the build actually consumes, so the verdict stands. But what the upstream `limit` 100 bounds
  was not measured.
- **Structure, not routing.** This is about the first step out of a famous artist. No journey was
  routed. The link to what Dig deeper delivers (graph-descriptives §1 B) is still inferred.
- **One map.** Nothing here is measured on lux4, so it does not explain why the previous map was
  open at the top 1 %.
- **The fame-overlay directory was not hashed.** It was trusted because the build reproduced the
  served map byte for byte in node order and connections, as `cand_build.py` did.

## 4. Options and their consequences

**Why the decision is his:** whether the walled-in top is acceptable, and whether to spend a map
rebuild or a pre-registration on it, is a judgement about what the app should do (issue #200
*Whose*; `CLAUDE.md`, "what counts as better"). The cap rule itself is parked and his (adoption
pre-registration §2.4, `LBD-X1`). Nothing here is a recommendation.

- **Leave it.** Nothing is spent. Famous-to-famous journeys stay as graph-descriptives §1 B measured
  them. The wall is now explained, not merely located.
- **Treat it as a map question aimed at the famous artist's own limit.** This result says a
  build-time change would have real material to work with: hundreds of less-listened candidates per
  famous artist are already being discarded. The kinds of change in view are reserving some of a
  famous artist's fifty slots for less-listened partners, raising the limit for the top tier, or
  ranking with some correction for overall play. Each needs its own pre-registration and a rebuild.
  **Consequences on the record:** Track B's quota cells held reserved obscure edges at famous nodes.
  On `ALG-E` the router took none of them at production weights. On `ALG-B`, sub-decile presence on
  famous pairs was nonzero nearly everywhere, even under the production rule. Figures are owned by
  `docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md` §1 `CRS-C5`. Raising a
  degree limit also raised hub transit there (`CRS-C4`).
- **Treat it as a routing question.** This result narrows that option. Where a famous artist has no
  below-bar connection (381 of 874), no routing weight can take the first step out of the famous
  tier, because the connection is not on the map. Routing can only act on the rest, and there the
  typical famous artist has a single such exit (§1, SUP-S4 median).
- **Measure the quality of the discarded candidates first.** This is descriptive: how strongly
  supported the below-bar connections that the limit deleted are, compared with the famous ones it
  kept. It decides whether the map option is aimed at good connections or at noise. It needs no
  routing and no listen, and would precede any pre-registration.
- **#200's definition question is unchanged.** Whether "better" includes audience size is still his.
  This result is about whether the map *can* offer less-listened steps from the top, not whether it
  should.
