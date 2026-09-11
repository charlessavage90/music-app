# `LBD-AM5` Step 2 — `LBD-A5`, and the two maps over the served population, `LBD-A0V` and `LBD-A5V`

**Role: ACTIVE — FIGURES OWNER for `LBD-AM5`'s builds: `LBD-A5`'s derived table, the two emitted
archives, the maps' node and edge counts, their retention against `V`, the pre-existing set's degree
against the served map, the three `LBD-AM5-4` fame checks, and the serialised artifacts' identity.
Cite by section; never restate a number from here.** The two measurements `LBD-AM5` was written on
— the drop lists over `V` and the pair draw — are owned by the amendment's own block
(`docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`, §10) and their JSON
(`lbv_coverage.json`, `../2026-09-10-lbd-blind-listen/lbl_pairs.json`). Reasoning:
[`docs/superpowers/2026-09-10-lbd-listen-prep-execution-log.md`](../../../docs/superpowers/2026-09-10-lbd-listen-prep-execution-log.md).

**Nothing here is about journeys.** No path was routed on either map by this session, and nothing
below says anything about which map a listener would prefer — that is the `LBL-` listen's question,
and its materials are in `../2026-09-10-lbd-blind-listen/`.

**Scripts, frozen research code:** `lbv_coverage.py` (the `LBD-AM5-3` pre-measurement),
`lbv_derive_a5.py` (runs `../2026-09-08-lbd-similarity/lbd_derive.py` unedited), `lbv_emit.py` (runs
`../2026-09-10-lbd-supply/emit_archive.py` unedited, sha-checked), `lbv_build.py` (the census build,
the fame checks, scaled acceptance, serialisation). Everything they produced outside this directory
sits under `C:\unsung-fast\`, gitignored and identified only by the checksums below. Committed beside
this file: `lbv_coverage.json`, `lbv_build_A0V.json` / `.degrees.json`, `lbv_build_A5V.json` /
`.degrees.json`.

> ⚠ **Two edge-count units appear below, and they differ by a factor of two.** "Connections" counts
> each connection once (degree sum ÷ 2, `hub_stats`' `edges`). Every manifest sidecar's `"edges"` —
> the served map's included — and `Graph.edge_count` count CSR entries, i.e. each connection in
> **both** directions. This document labels every edge figure with its unit. The first build run was
> refused by acceptance because a bound was written in one unit and checked in the other (§5).

## 0. Inputs, pinned, every one verified before it was read

| input | identity |
|---|---|
| `V`, the served population | node set of `builder/scratch/graph-msw-tu50.bin`, sha256 `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` (matched its sidecar; `ApiConfig.graph_path`'s default), **58,838** artists, read through the shipped `GraphStore`; written as `C:\unsung-fast\lbd-archives\population_msw_mbids.txt`, sha256 `b5e0cb94…` |
| the pre-existing set / `V − P` | `cxr_preexisting_mbids.txt` `768054b7…` (58,793) — **equal to `V ∩ P` exactly** (`lbv_coverage.json`) — and the 45 artists of `V − P`, listed in `lbv_coverage.json`; the build script refuses unless the two partition `V` |
| production's twin | `builder/scratch/graph-lux4.bin`, sha256 `fd92a735…` (matched its sidecar) — **routing-identical to `V`'s artifact** on every array `find_journey` reads (execution log, Step 3) |
| `T` | `C:\unsung-fast\lbd-pairs\aggregate\T.parquet`, sha256 `03d47b05…` (Task 4 README §5) |
| `LBD-A0` derived | `…\lbd-pairs\A0\A0.parquet`, sha256 `f9bd1f83…`, 11,340,639 rows (Task 4 README §6) |
| identity frame | `D:\unsung-large-data\lbd-inputs\artist_identity.parquet`, sha256 `02b4c8dd…` (Task 1) |
| drop lists | the served lineage's own, pinned by override (`LBD-AM5-3`), bytes asserted equal to the shas `graph-lux4.bin.json` records: `unlistenable_drop_algb_20260805.json` `106ae420…`, `no_release_drop_algb_20260802.json` `88c7f0b7…`, `featured_credit_drop_algb_20260803_am1.json` `458f9b23…` |
| fame records | `builder/scratch/grt-archive-algb.pre-cex-snapshot/fame/`, read-only, the archive the served map rebuilds from byte-identically (`../2026-09-05-lux-e1-armb/README.md` §1–§2) |

## 1. `LBD-A5`, the derived table

*Plain sentence (`LBD-AM5-2`): keep ListenBrainz's hundred-connection cut, and accept a connection
only when at least two different people's listening supports it.*

| | |
|---|---|
| definition | `T` filtered `score > 3`, ranked per `mbid0`, `rank <= 100` — `lbd_derive.py`'s SQL, unedited (script sha256 `0cacf931…`; wrapper `d6ab7528…`) |
| output | `C:\unsung-fast\lbd-pairs\A5\A5.parquet`, sha256 **`f34cd88957d3ab42b000fb33d23ae7f9aad1dbdb72d2d0b1cab5d34f024a19ff`** |
| rows | **26,127,091** |
| wall clock | 87 s |
| green check | **reproduces the committed curve's (3, 100) cell on all four pinned sets** — dead-end share, absent share and median partners, to float precision (the curve's figures are owned by `../2026-09-08-lbd-similarity/README.md` §6c and are not restated here). The script refuses to write its manifest otherwise. |

## 2. The archives — `LBD-A0` and `LBD-A5` emitted over `V`

*Plain sentence (`LBD-AM5-1`): the two similarity tables written out in the form the app's builder
reads, over exactly the artists the app serves today.* Emitted by the Task 6 emitter unedited
(sha256 `484f9415…`, checked by the wrapper); the population filter is applied to the derived table
after its own threshold and rank cut, never re-ranked inside `V`.

| | `LBD-A0V` | `LBD-A5V` |
|---|---:|---:|
| rows in the derived table | 11,340,639 | 26,127,091 |
| … with **both** ends in `V` (written) | **4,175,136** | **4,970,814** |
| … with one end in `V` (dropped) | 5,199,057 | 14,616,812 |
| … with neither (dropped) | 1,966,446 | 6,539,465 |
| payloads written (artists of `V` with ≥ 1 partner in `V`) | **57,620** | **58,197** |
| neighbour rows written (= 2 × pairs) | 8,350,272 | 9,941,628 |
| artists of `V` **absent** from the table | 1,218 | 641 |
| artists of `V` with no identity row | 5 (all among the absent; none emitted nameless) | 5 (same) |
| archive root | `C:\unsung-fast\lbd-archives\A0V\`, `MANIFEST.json` sha256 `7f555e14…` | `…\A5V\`, `MANIFEST.json` sha256 `41b66372…` |
| wall clock | 76 s | 78 s |

**Read the middle rows the way the supply README's §1 asks.** Over the whole table `LBD-A5` is
2.3× `LBD-A0`; restricted to the artists the app serves it is **1.19×**. Most of what the lower bar
admits is pairs with an artist outside `V`.

## 3. The builds, against the served map

*Plain sentence: how big are the two maps we could build over the app's own artists, and how do they
compare with the map the app serves?* Both through the shipped `build_from_archive`, in-process,
`LBD-AM5-3`'s configuration — asserted equal to the served map's recorded configuration, knob by knob,
and the three drop lists' bytes asserted equal to the served lineage's (`lbv_build.py`, sha256
`877e8161…`, the same script for both). The served map's column is measured by the same script
through the shipped `GraphStore`; **no earlier document states these figures for this map** — the
`CXR-P2` row for the pre-existing set is measured on the *extended* map and must not be compared with
the column below.

| | served — `graph-msw-tu50.bin` | **`LBD-A0V`** | **`LBD-A5V`** |
|---|---:|---:|---:|
| **nodes** (largest component) | 58,838 | **57,142** of 57,620 with a payload | **57,932** of 58,197 |
| retention against `V`'s 58,838 | 1 | 0.9712 | 0.9846 |
| served artists **absent from the map** | 0 | 1,696 (1,218 with no pair in `V`, 478 pruned) | 906 (641 + 265) |
| **connections** (degree sum ÷ 2) | 657,842 | 784,607 | 840,627 |
| CSR entries — the sidecar's `"edges"` unit | 1,315,684 | 1,569,214 | 1,681,254 |
| mean / median degree | 22.36 / 17 | 27.46 / 25 | 29.02 / 27 |
| max degree — the ceiling binds | 50 — yes | 50 — yes | 50 — yes |
| p99 rescale: scale / saturated edges | — | 2,926 / 83,534 of 8,350,272 (1.000 %) | 2,634 / 99,454 of 9,941,628 (1.000 %) |
| drop stages: special-purpose / nameless / no-release / featured / un-listenable | — | **0 / 0 / 0 / 0 / 0** | **0 / 0 / 0 / 0 / 0** |
| build wall clock: census / listenable | — | 47 s / 52 s (archive warm in the OS cache) | 277 s / 59 s |

*The drop stages are read off the builder's log, which prints only non-zero counts: neither build
printed one. That is `LBD-AM5-3`'s "measured inert on `V`", observed in the build as well as in the
probe. `top1pct_degree_mass_frac` is in the JSON and is not read, because the ceiling binds in all
three maps (the ceiling probe's §3 forward correction).*

### 3a. The pre-existing set — the served map's own artists that both maps share with the extended map

Share at ≤ 2 connections over **all 58,793**, an absent artist counted as 0 (the pre-registration's
statistic, `set_stats`' `share_le_2_or_absent`), the share absent, and the median degree of those
present. Paired figures compare each artist's degree with its own degree in the other map (absent = 0).

| | served | **`LBD-A0V`** | **`LBD-A5V`** |
|---|---:|---:|---:|
| **share ≤ 2 (absent = 0)** | **0.0886** | **0.0540** | **0.0280** |
| share = 1, of those present | 0.0469 | 0.0119 | 0.0063 |
| share absent | 0 | 0.0288 | 0.0154 |
| **median degree** (present) | **17** | **25** | **27** |
| paired against the served map: gained / lost / same | — | 34,216 / 16,354 / 8,223 | 37,346 / 14,057 / 7,390 |
| … median / mean change | — | +2 / +4.31 | +4 / +6.21 |
| paired against `LBD-A0V` — **listen 2's comparison**: gained / lost / same | — | — | 25,835 / 1,165 / 31,793 |
| … median / mean change | — | — | 0 / +1.90 |

*The last two rows are computed from the two committed `.degrees.json` files, artist by artist.*

**`V − P`, the 45 served artists the extended map lacks** — descriptive only; n = 45 carries no
resolution: share ≤ 2 (absent = 0) served 0.4667, `LBD-A0V` 0.2667 (5 absent), `LBD-A5V` 0.0889 (2 absent);
median degree 3 / 8 / 12.

*Plain, and labelled as a reading of the table rather than a finding about journeys:* in a map built
from our own recomputation at ListenBrainz's settings, the artists the app serves today are dead ends
about 5 times in 100 instead of about 9, typically hold 25 connections instead of 17 — and about 3 in
100 of them are not in that map at all. The two-listener bar roughly halves both the dead-end share and
the absent share again, and moves the typical artist from 25 connections to 27. **Denser is not
better** until a listener says so (`REQ-38`), and ⚠ **the served-vs-`LBD-A0V` difference is a bundle
(`LBD-X5`) plus `LBD-X4`** — never a statement about the reimplementation or "the data" alone.

## 4. Fame — `LBD-AM5-4`'s three checks

*Plain sentence: the new maps route on the same listener counts, artist by artist, as the map the app
serves.* Each check is a refusal in `lbv_build.py`; each ran on both maps.

| check | `LBD-A0V` | `LBD-A5V` |
|---|---|---|
| **(i)** a fame record in the snapshot for every member of `V` (58,838); every map node in `V` | **0 missing**; nodes ⊆ `V` | **0 missing**; nodes ⊆ `V` |
| **(ii)** every such record equals the served artifact's own `fame_lb` | **0 differ** | **0 differ** |
| **(iii)** the fame-carrying build is structurally identical to the census build (node order, names, ids, CSR arrays, scores, `pop_raw`) | **identical** | **identical** |
| artists in the map whose record is a measured null | 1 | 1 |

**So `LBD-D4` is met rather than worked around: no fame stage was re-run, and the factor table's
fame column is constant.** The listenable map's `fame_lb_raw` was also asserted equal to the served
map's value for every one of its nodes.

## 5. Acceptance and the artifacts

`check_acceptance` with **scaled criteria defined in the script from quantities known before either
build** — never `PRODUCTION_ACCEPTANCE`:

| criterion | value | where it comes from |
|---|---|---|
| canonical names | Radiohead, The Beatles, Coldplay, R.E.M. | the §2.8 failure-signature detectors (`acceptance.py`, group 1) |
| famous sample / median floor / minimum floor | 25 / 25.0 / 8 | the same detector; describes a defect's shape, not the population's size |
| node count | 47,070 – 58,838 | −20 % of the served sidecar's count; `V`'s size is the hard upper bound |
| edge count — **CSR entries** | 1,052,547 – 2,941,900 | −20 % of the served sidecar's count; every node of `V` at the ceiling, both directions |
| median degree | 1 – 50 | only a value outside what the ceiling permits is a defect here |

**The first run was refused**, on `LBD-A0V`, because the edge ceiling was written as `N × c ÷ 2`
(connections) and checked against CSR entries: *"edge count 1569214 outside bounds [1052547,
1470950]"*. Nothing was written. The bound was corrected from the unit, not from the build's value,
and the refusal is recorded in the execution log (Step 2). Both maps then passed, with no blank name.

| artifact | sha256 | bytes | artists | CSR entries |
|---|---|---:|---:|---:|
| `C:\unsung-fast\lbd-artifacts\LBD-A0V.bin` | **`494c53d52654f6918a4176eef91f291558b0e56d71a4ea16c8070ad8ba3e34bb`** | 25,738,850 | 57,142 | 1,569,214 |
| `C:\unsung-fast\lbd-artifacts\LBD-A5V.bin` | **`2d34746e2cc8a6596ee15e390eea5a14ea7f13ede4ec2ba0608475157653ae63`** | 26,892,406 | 57,932 | 1,681,254 |

Each has a `.bin.json` sidecar written by the shipped `build_manifest` / `write_manifest`, whose
`build_inputs` names the archive, its manifest sha, the fame-record source and the three drop lists.
Each was reloaded through the shipped `GraphStore`: sha, node count, CSR offsets and a non-null fame
percentile all round-trip. **Neither is deployed, and neither is under `builder/scratch/`.**
`LBD-A0V`'s sha is pinned for the listen in `../2026-09-10-lbd-blind-listen/lbl_maps.json`; `LBD-A5V`'s
is added there only when listen 2 is prepared.

## 6. What is NOT established here

- **Anything about journeys or preference.** No path was routed on either map. A denser map with fewer
  dead ends is not a better journey until the `LBL-` listen says so, and that spends the owner's ear.
- **Which part of the served-vs-`LBD-A0V` difference is corpus age, `filter_True`, mapping, the
  band-member class or tie-break** (`LBD-X5`), **or the 439 artists the served build's cap step saw and
  ours did not** (`LBD-X4`). No arm here separates them.
- **Who the 1,696 (`LBD-A0V`) and 906 (`LBD-A5V`) absent served artists are, or whether any of them
  sits in the owner's journeys.** Counted, not investigated. In a listen, an endpoint absent from
  either map is replaced mechanically (`LBD-AM5-5`, gate (a)); an interior artist the served map would
  have used is simply unavailable in ours, which is part of what is being heard.
- **The 16,354 pre-existing artists that lose connections in `LBD-A0V`** — the cap rule re-selecting from
  different candidates; counted, not examined.
- **Adoption, the population rule, API sizing, a refresh procedure** — all `S4`, all the owner's. `V`
  is an experimental control.
- **Fidelity** — `LBD-C1` fired and was overridden (`LBD-AM3`); these maps inherit whatever the
  reimplementation gets wrong that the synthetic sub-check cannot see.
