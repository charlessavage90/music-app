# `LBD-` Tasks 6–7 — the fixed-population builds of `LBD-A0` and `LBD-A2`, and what they measure

**Role: ACTIVE — FIGURES OWNER for the `LBD-` build stage under `LBD-AM4`: the emitted archives'
identity, `LBD-M1`, `LBD-C2b`, `R8`, `R9`, and the comparison against the ceiling probe's §4
bridge control. Cite by section; never restate a number from here.** The threshold curve is
owned by [`../2026-09-08-lbd-similarity/README.md`](../2026-09-08-lbd-similarity/README.md)
§6c, not here. Reasoning is in
[`docs/superpowers/2026-09-10-lbd-task67-execution-log.md`](../../../docs/superpowers/2026-09-10-lbd-task67-execution-log.md);
the governing text is the pre-registration's `LBD-AM4` block (§10) and register row (§12).

**Scripts, frozen research code:** `lbd_population_coverage.py` (the `LBD-AM4-3` measurement),
`lbd_source.py` (the `lbd` bulk source), `emit_archive.py` (Task 6, sha256 `484f9415…`),
`lbd_build_census.py` (Task 7, sha256 `18047e72…`), `lbd_c2b_compare.py` (the reads).
Everything they produced sits under `C:\unsung-fast\lbd-archives\`, gitignored and identified
only by the checksums below. The JSON results beside this file are committed:
`lbd_population_coverage.json`, `lbd_build_A0.json` / `.degrees.json`, `lbd_build_A2.json` /
`.degrees.json`, `lbd_c2b_compare.json`.

## 0. Inputs, pinned, every one verified before it was read

| input | identity |
|---|---|
| `P`, the fixed population | node set of `graph-cxa-adopted.bin`, sha256 `bc0431c4b55a2137e945b280270de7e7dc700e3dcf60f3656f6f97598e7ece46` (matched its sidecar), **88,685** artists, read through the shipped `GraphStore`; written as `C:\unsung-fast\lbd-archives\population_cxa_mbids.txt`, sha256 `1bbff8fc…` |
| the added set / pre-existing set / residual stratum | `cxr_added_mbids.txt` `bfed95ef…` (29,892), `cxr_preexisting_mbids.txt` `768054b7…` (58,793), `cxr_residual_mbids.txt` `fa8d85cc…` (5,967) — the pre-registration's §3 files; the census script refuses unless added + pre-existing partition `P` exactly, and they do |
| `T` | `C:\unsung-fast\lbd-pairs\aggregate\T.parquet`, sha256 `03d47b05…`, 689,603,622 rows (Task 4 README §5) |
| `LBD-A0` derived | `…\lbd-pairs\A0\A0.parquet`, sha256 `f9bd1f83…`, 11,340,639 rows |
| `LBD-A2` derived | `…\lbd-pairs\A2\A2.parquet`, sha256 `34f92de7…`, 80,578,844 rows |
| identity frame | `D:\unsung-large-data\lbd-inputs\artist_identity.parquet`, sha256 `02b4c8dd…` (Task 1; the MusicBrainz `artist` table of the 2026-09-05 `mbdump`) |
| the drop lists | `unlistenable_drop_algb_20260809.json` via the shipped `unlistenable_list_path` override; `no_release_drop_algb_20260802.json` and `featured_credit_drop_algb_20260803_am1.json` by `config.algorithm = CANDIDATE_ALGORITHM` |

**`LBD-AM4-3`'s measurement** (`lbd_population_coverage.py`, its JSON beside this file): the
coverage counts it produced are owned by the pre-registration's `LBD-AM4-3` block — the
amendment turns on them and was committed before this document existed, so it carries them and
this document cites it. In one sentence: the re-censused list covers `P` and no list removes
anyone from it; the current default list does not cover `P`. **Observed again in the builds
(§2): no drop stage removed anyone.**

## 1. The archives — Task 6

*Plain: our own similarity tables, written out in the exact form the app's builder already
reads, over exactly the artists the current extended map contains.* Each pair's two directions
are unioned; neighbours sorted `(-score, mbid)`; payload rows carry the four `FIELD_*` keys the
builder reads and nothing fabricated (the live endpoint also returns `type`, `gender`,
`reference_mbid`, none of which the builder consumes). The population filter is applied to the
**derived** parquet, after its threshold and rank cut — never re-ranked inside `P`
(`LBD-AM4-1`).

| | `LBD-A0` | `LBD-A2` |
|---|---:|---:|
| rows in the derived arm | 11,340,639 | 80,578,844 |
| … with **both** ends in `P` (written) | **5,637,469** | **8,819,528** |
| … with one end in `P` (dropped) | 4,391,887 | 49,896,440 |
| … with neither (dropped) | 1,311,283 | 21,862,876 |
| payloads written (artists of `P` with ≥ 1 partner in `P`) | **86,854** | **88,285** |
| neighbour rows written (= 2 × pairs) | 11,274,938 | 17,639,056 |
| artists of `P` **absent** from the arm | 1,831 | 400 |
| artists of `P` with no identity row | 10 (all among the absent; none emitted nameless) | 10 (same) |
| archive root | `C:\unsung-fast\lbd-archives\A0\`, `MANIFEST.json` sha256 `d6f79076…` | `…\A2\`, `MANIFEST.json` sha256 `78c31d29…` |
| wall clock | 1.8 min | 2.1 min |

**Read that middle row before anything else.** Most of what `LBD-A2` adds over `LBD-A0` at the
pair-table level is pairs with an artist *outside* `P`: restricted to `P`, `A2` is 1.6× `A0`,
not 7×. That is the population confound `LBD-X2` names, made visible — and removed — by fixing
`P`.

**Determinism (`LBD-D5`), observed.** The `A0` archive was emitted three times — by the
emitter's first version (pairs sorted in Python), by its third (one sorted stream out of
DuckDB), and by the final committed script — and the sha256 over every payload's path and bytes
is identical each time: **`c13c2250…` over 86,854 files.** The manifest's wall clock and
script sha differ; nothing the builder reads does.

**The 10 artists with no identity row** are listed in each `MANIFEST.json`
(`P_with_no_identity_row_mbids`). They are absent from both arms — nobody in the corpus
co-listens to them in a form that survives sessioning — so they reached no build and no
nameless drop fired. Not investigated further; a merged or deleted MusicBrainz id is the likely
class (the served map carries three such, `pipeline.py`'s nameless-rule comment).

## 2. The builds — Task 7, and `LBD-M1`

Both through the shipped `build_from_archive`, in-process, nothing serialised, no acceptance
check; `BuilderConfig(algorithm=CANDIDATE_ALGORITHM, require_fame=False, drop_unlistenable=True,
unlistenable_list_path=…20260809.json)` and every other knob at its default — the ceiling
probe's §4 bridge-arm configuration plus `require_fame=False`. The archive is opened
read-only (`GRT-A1`).

| | `LBD-A0` | `LBD-A2` |
|---|---:|---:|
| **nodes** (largest component) | **86,086** of 86,854 with a payload | **88,132** of 88,285 |
| retention against `P`'s 88,685 | 0.9707 | 0.9938 |
| **edges** | 1,102,428 | 1,310,518 |
| max degree / mean / median | 50 / 25.6 / 22 | 50 / 29.7 / 28 |
| the ceiling binds (max degree = 50) | yes | yes |
| p99 rescale: scale / saturated edges | 2,437 / 112,820 of 11,274,938 (1.001 %) | 1,805 / 176,432 of 17,639,056 (1.000 %) |
| drop stages: special-purpose / nameless / no-release / featured / un-listenable | **0 / 0 / 0 / 0 / 0** | **0 / 0 / 0 / 0 / 0** |
| build wall clock | 5.9 min | 7.1 min |

*Because the ceiling binds in both, `top1pct_degree_mass_frac` is not a concentration
measurement here (the ceiling probe's §3 forward correction); it is in the JSON and is not
read.*

**`LBD-M1` — population, by the served artifact's fame band.** *Plain: how many of the
extended map's artists does each arm's map keep, and does it lose the obscure ones first?*
Five equal-count bands by `fame_lb` from the `CXA` metadata (band 0 least-listened, 4 most;
"unknown" where null). Descriptive; feeds `S4`.

| band | in `P` | built, `A0` | share | built, `A2` | share |
|---:|---:|---:|---:|---:|---:|
| 0 | 17,711 | 15,917 | 0.899 | 17,376 | 0.981 |
| 1 | 17,711 | 17,337 | 0.979 | 17,664 | 0.997 |
| 2 | 17,711 | 17,529 | 0.990 | 17,689 | 0.999 |
| 3 | 17,711 | 17,631 | 0.995 | 17,699 | 0.999 |
| 4 | 17,715 | 17,670 | 0.997 | 17,701 | 0.999 |
| unknown | 126 | 2 | 0.016 | 3 | 0.024 |

Loss is concentrated in the least-listened band under `A0` and nearly closed under `A2`. The
126 "unknown" artists — `P` members the `CXA` build recorded no fame for — are almost all absent
from both arms; not investigated here.

## 3. `LBD-C2b`, with both controls; `R8`; `R9`

*Plain sentence (pre-registration §3): how many connections do the added artists actually end
up with in a map we could ship?* Share at ≤ 2 connections over **all 29,892**, an absent
artist counted as 0 (the pre-registered quantity; `set_stats`' `share_le_2_or_absent`), versus
`LBD-A0`; `LBD-G2`'s graph-level bar is **≥ 1 percentage point, admissible only with both
controls reported** — the pre-existing 58,793 as the within-arm reference, and the arm's own
`LBD-C2a` figure (Task 4 README §6). Paired sign test over the fixed set, as the pair-level
read reported it. `lbd_c2b_compare.json`.

| set | arm | **share ≤ 2 (absent = 0)** | Δ vs `A0` (pp) | gained / lost / same | share = 1 | absent | median degree (reported, not gated) |
|---|---|---:|---:|---|---:|---:|---:|
| **added, all 29,892** | `A0` | **0.0964** | — | — | 0.0318 | 0.0323 | 14 |
| | **`A2`** | **0.0129** | **−8.35** | 23,424 / 256 / 6,212 | 0.0031 | 0.0059 | 22 |
| residual (`LBD-AM1`), 5,967 *(descriptive)* | `A0` | 0.2673 | — | — | 0.1130 | 0.0675 | 6 |
| | `A2` | 0.0144 | **−25.29** | 5,469 / 17 / 481 | 0.0034 | 0.0079 | 18 |
| complement, 23,925 *(descriptive)* | `A0` | 0.0538 | — | — | 0.0125 | 0.0234 | 16 |
| | `A2` | 0.0126 | −4.13 | | 0.0031 | 0.0054 | 23 |
| **pre-existing, 58,793 — control 1** | `A0` | 0.0496 | — | — | 0.0104 | 0.0278 | 29 |
| | `A2` | 0.0116 | **−3.80** | | 0.0023 | 0.0064 | 34 |
| **`LBD-C2a`, same arm — control 2** (Task 4 README §6, cited) | `A0` | 0.0374 | — | | | | |
| | `A2` | 0.0044 | −3.30 | | | | |

The sign test is trivially significant (two-sided p rounds to 0) and is reported because the
pre-registration names it. **256 added artists have *fewer* connections in `A2` than in `A0`**:
the cap rule re-selects each artist's list from a larger candidate set, and an edge that was
in someone's top-*j* under `A0` can be displaced under `A2`. It is small, it is real, and it is
`LBD-X1`'s mechanism seen from the other side.

**The reads, each against its row in §9:**

- **`LBD-G2`, graph level: `LBD-A2` clears the 1-point bar, with both controls reported**
  (−8.35 pp on the whole set). *Plain: in a map we could ship, the share of added artists who
  are dead ends falls from about one in ten to about one in eighty when the strength bar is
  dropped.*
- **`R8` does NOT fire.** `LBD-C2a` moved (−3.30 pp) and `LBD-C2b` moved (−8.35 pp). Our own
  degree ceiling is *not* absorbing the gain at this population — the graph-level movement is
  larger than the pair-level one, because `A0`'s map has more dead ends than `A0`'s pair table
  (9.6 % against 3.7 %) and `A2` hands the cap rule enough candidates to close most of that
  gap. `LBD-X1` is untouched as a bar: it still forbids reading a graph-level *null* as a
  supply null; no null occurred.
- **`R9` does NOT fire.** The pre-existing set moves by −3.80 pp, less than half the added
  set's −8.35 pp, so the movement is not a uniform artefact of a denser table.
- **`R12`'s shape, read descriptively (no gate):** the residual stratum — the artists our own
  ceiling cannot reach — moves **most**, −25.29 pp, from about one in four dead ends to about
  one in seventy. The loosened bar reaches the artists this track exists to help, first of all,
  at the graph level as at the pair level.

## 4. Against `CXR-P2` and the ceiling probe's §4 bridge control

The bridge control (ceiling 50, the re-censused list via the override, `require_fame=False`,
ListenBrainz's deployed lists) reproduces the `CXA` population exactly and lands on `CXR-P2` to
the decimal — its README §4 says so and owns both sets of figures. So it is the same 88,685
artists under the served lineage's data, and it differs from `LBD-A0` in the **data column
alone** (`LBD-AM4`'s factor table). **Only differences are stated here; the control's own
figures are its README's** (`dcf_results_bridge.json`, ceiling-50 row), and `CXR-P2`'s are the
`CXR` diagnosis's.

| `LBD-` arm minus the bridge control (= minus `CXR-P2`) | `LBD-A0` | `LBD-A2` |
|---|---:|---:|
| added — dead-end share (≤ 2, absent = 0) | **−24.72 pp** | **−33.07 pp** |
| added — median degree | +10 | +18 |
| added — share absent | +3.23 pp | +0.58 pp |
| pre-existing — dead-end share | −3.11 pp | −6.91 pp |
| pre-existing — median degree | +10 | +15 |
| nodes | −2,599 | −553 |
| edges | +293,346 | +501,436 |

*Plain: at ListenBrainz's own settings, recomputed by us on today's listening data, the extended
map's added artists are already far less often dead ends than they are in the map we serve —
by about twenty-five points — and dropping the strength bar takes another eight. The one thing
that gets slightly worse under `A0` is absence: about 3 in 100 added artists have no pair at
all in our `A0` table, where ListenBrainz's lists gave every one of them at least something.*

⚠ **What the `A0`-vs-control difference is a difference OF.** The "data" column bundles
everything the Task 4 README's §5a–5c diagnosed: a corpus roughly three times the size the
deployed lists were computed on, the absent `filter_True` stage (`LBD-X3`), today's msid→mbid
mapping, the band-member class, and our deterministic tie-break. None of them is separated
here. Read this row as *"ListenBrainz's rules on today's data, by us"* against *"ListenBrainz's
lists as deployed"*, and nothing finer.

## 5. What is NOT established here

- **Nothing about routing or path quality.** No path was built; `CRS-C4` hub transit was not
  re-measured; the max degree is at the ceiling in both arms and no journey has been scored.
  A denser map is not a better journey until a blind listen says so (`REQ-38`), and that
  spends the owner's ear and is his decision.
- **Whether the pairs threshold 0 admits are connections anyone wants.** The Task 4 README's
  §6c shows "threshold 0" means *one listener, one session* (score 2 is the floor in practice)
  and that most of the dead-end reduction arrives before the floor. That is context for the
  owner, not a finding about listening quality.
- **Anything about adoption, the population rule, API sizing, the fame source, or a refresh
  procedure** — all `S4`, all the owner's. `P` is an experimental control: a shipped map from
  our own table would not be confined to the artists a crawl happened to discover.
- **Fidelity.** `LBD-C1` fired and was overridden (`LBD-AM3`); these arms inherit whatever the
  reimplementation gets wrong that the synthetic sub-check cannot see.
- **Which part of the `A0`-vs-control gap is corpus age, which is `filter_True`, which is
  mapping** — §4's warning; no arm here separates them, and the dated-corpus `A0` of the Task 4
  README §6 is pair-level only.
- **The 256 added artists that lose connections under `A2`**, the 126 fame-unknown artists,
  and the 10 identity-less MBIDs — each counted, none investigated.
- **`LBD-A1` and `LBD-A3` at the graph level** — not built (`LBD-AM4-2`); `LBD-A4` not run.
