# Issue #270: the less-listened exits the fifty-connection limit deleted, against the connections it kept

**Role: FIGURES OWNER for this measurement.** Its design (everything above §1) was fixed and
committed **before any figure was computed**. The git timestamp of the commit that adds this file
without a §1 (`9d48176`) is the evidence of that order. A pre-run code exercise came after that
commit, and no figure from it is reported (§1, run notes).

**What this is.** The descriptive that
`../2026-09-27-issue-200-trim-supply/README.md` §4, fourth bullet, names and nobody has run: *"measure the
quality of the discarded candidates first"*. The same measurement is named as unrun in the `DRP-`
pre-registration's `DRP-X1` (`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`
§2.8). **It decides nothing.** No journey is routed, no weight, config, archive or shipped code is changed,
and nothing is proposed. Which remedy for #270 to pursue, if any, is the owner's.

**What it can and cannot answer. This is fixed now, before the result exists.** Every measure below is
in the map's own currencies: the listening data's score for a pair, the similarity the app would show,
degree, and fame percentile. It can say **how far below the kept connections the map's own data puts
the deleted ones**, how far down the famous artist's own list they sat, and **what a step onto one would
cost the router today**. It **cannot** say whether the deleted ones *sound* right. The record says why
that is a real limit and not a formality: on the `DSL-` listen's weak-step marks, the map's similarity
score did not track the owner's ear (`docs/superpowers/findings/2026-10-03-snw-marks-test.md` §0,
`SNW-R4`). So "good links or noise" in the sense of the trim-supply falsifier (*a listen or a coherence
measure*, trim-supply §3) is **not** reachable here. One measure (`DXQ-M3b`) is a structural proxy for
the specific noise mechanism trim-supply §3 names, and it is labelled as a proxy.

## Currencies (each figure names one)

| name | what it is | plain sentence |
|---|---|---|
| **listening score** | the integer score on the pair in the archived ListenBrainz list (`emit_archive.py`, `FIELD_SCORE`) | *how strongly the listening data links the two* |
| **cap ranking value** | `log1p(listening score)`, the pair's stronger direction: the key the ceiling deletes by (`trim_supply.py` `strength()`; `pipeline.py` "Rank the cap on UNCLIPPED strengths"); damping is 0.0 | *the number the fifty-connection limit sorts by* |
| **emitted similarity** | the pipeline's 0–1 rescaled score (`p99_log_clip`), symmetrised on the stronger direction, exactly as the build would have written the edge (`DRP-S1` rule 4) | *the similarity the app would show for this step* |
| **degree** | connection count, served (`lba-a6`, ≤ 50) or pre-ceiling (`SUP-S3` size) | *how many connections an artist has* |
| **fame percentile** | `fame_lb_pctl`, lba-a6's own frame, the shipped `GraphStore` | *how listened-to an artist is, ranked 0 to 1 on this map* |
| **raw popularity** | `pop_raw`, the shipped `GraphStore` | used only inside the router price |

## Inputs and identity

| role | location | sha256 | checked against |
|---|---|---|---|
| served map | `C:/dev/music-app/builder/scratch/graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` | its sidecar **and** the pin, by `trim_supply.py` |
| similarity archive | `C:\unsung-fast\lbd-archives\S4-A6\MANIFEST.json` | `950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3` | pin, before and after, by `trim_supply.py` |
| population P | `C:\unsung-fast\lbd-archives\population_cxa_mbids.txt` | `1bbff8fc…` | the archive manifest, by `trim_supply.py` |
| extra-connections map | `C:\unsung-fast\drp-stage3a\graph-drp-s1.bin` | `418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f` | its sidecar **and** this pin (`../2026-09-27-drp-stage3a/README.md`) |

## Instrument

- **The build and every reproduction assertion are `trim_supply.py`'s, executed unmodified.** The script
  here runs it with `runpy.run_path` and computes on the globals it leaves (`CAP`, `S3`, `keep`,
  `remover`, `store`, `pctl`, `measured`, `mbids`, `idx`, `ranking`, `trim_out`, …). `trim_supply.py`
  refuses (exit 2 or 3) on any sha mismatch or failed reproduction, and that refusal propagates. Its full
  output goes into this run's raw output, so this run also re-checks trim-supply's figures. Nothing in
  the build is reimplemented here.
- **Centres:** lba-a6 nodes with measured fame percentile ≥ 0.99 (trim-supply's top 1 %).
- **Router weights** are read from `ApiConfig()` at run time and printed. `api/` is imported, never
  edited.
- **Additional assertions (exit 3 otherwise):**
  - `DXQ-A1`: for every kept edge at every centre, the emitted similarity computed from the captured
    pre-cap adjacency equals the served score as float32.
  - `DXQ-A2`: every deleted exit is in the centre's own ranked list (`ranking[c]`). The archive is
    two-directional (trim-supply, "The brief's archive description"), so the expected count of misses is
    0. If not, the misses are counted and reported, not dropped silently.
  - `DXQ-A3`: every edge in `graph-drp-s1.bin` and not in lba-a6 that touches a centre is in that
    centre's `DXQ-D`. The count of such edges is printed beside `DRP-C10`'s, which
    `../2026-09-27-drp-stage3a/README.md` owns.
  - `DXQ-A4`: a negative gap (`DXQ-M6`) occurs only at a centre where at least one below-0.9 edge was
    deleted by the **neighbour's** ceiling (`remover`). See the by-construction facts below.

## Groups (identifier series `DXQ-`, checked free across all refs 2026-10-26)

Per centre `c`. "Below 0.9" means a **measured** fame percentile < 0.9. Null-fame neighbours are
excluded everywhere and counted.

| id | members | plain sentence |
|---|---|---|
| `DXQ-K` | `c`'s served neighbours (`SUP-S4` = `SUP-S5`) | *the connections the famous artist kept* |
| `DXQ-KL` | `DXQ-K` below 0.9 | *the less-listened exits it kept* |
| `DXQ-D` | `SUP-S3(c)` minus `SUP-S4(c)`, below 0.9 | *the less-listened exits the fifty-connection limit deleted* |
| `DXQ-DH` | `SUP-S3(c)` minus `SUP-S4(c)`, at or above 0.9 | *the famous connections the limit also deleted* |
| `DXQ-DS1` | the `DXQ-D` edges that `graph-drp-s1.bin` added | *the deleted exits the extra-connections experiment put back, which the `DSL-` listen heard* |

### Factor table

| comparison | survived the limit? | neighbour's fame band | what it can isolate |
|---|---|---|---|
| `DXQ-D` vs `DXQ-KL` | no / yes | below 0.9 / below 0.9 | **survival alone** (one column differs) |
| `DXQ-D` vs `DXQ-DH` | no / no | below 0.9 / at or above 0.9 | **fame band alone** (one column differs) |
| `DXQ-D` vs `DXQ-K` | no / yes | below 0.9 / mostly famous | **neither alone.** Barred from attributing any difference to survival or to fame band by itself. Reported because it is the comparison a build change would actually face: what a restored exit competes with. |
| `DXQ-DS1` vs `DXQ-D` | subset | subset | how the ten-strongest-per-centre selection differs from all deleted exits |

`DXQ-KL` is empty at the centres with no kept exit (trim-supply: close to half the top 1 %). The
survival comparison is therefore reported **over centres with both a `DXQ-D` and a `DXQ-KL` member**,
and the centre count is printed beside it.

### Held constant, and why each is genuinely constant

- **One map, one archive, one config, one fame frame.** Every group comes from the same deterministic
  build that `trim_supply.py` asserts reproduces the served map.
- **Emitted similarity of a deleted edge.** The rescale runs over the whole pre-cap list before any cap
  (`pipeline.py` `rescale_scores`, before `trimmed_union_cap`), so a deleted edge's emitted similarity is
  exactly what the build would write if the edge survived. Restoring edges cannot change it.
- **Raw popularity.** `pop_raw` is the score-weighted in-degree summed over the **pre-cap** adjacency
  (`pipeline.py` `score_weighted_indegree`, before the cap), so the trim does not change it and neither
  would restoring an edge.
- **Fame percentile.** It is computed from `fame_lb`, not from edges.
- **Not constant, and named:** the hub term `degree_hub_penalty` depends on served degree, which
  restoring edges would change. Its weight is read from `ApiConfig`. If it is 0.0, as `config.py` sets
  it today, the term is inert in the price below. If it is not 0.0, the script refuses (exit 3) and the
  price is not reported, because it would rest on a degree that the counterfactual changes.

### By-construction facts, stated before the run so they are not read as findings

- **F1. The direction of `DXQ-D` against `DXQ-K` in cap ranking value is fixed by the code.** The ceiling
  deletes a centre's weakest edges by cap ranking value (`graph.py` `trimmed_union_cap`). So every exit
  deleted by the centre's own ceiling ranks at or below every connection it kept. Emitted similarity is
  a non-decreasing function of the same value, clipped at 1.0, so the same holds there. **"Deleted exits
  are weaker than kept connections" is a tautology here.** The information is in **how much** weaker,
  and in the measures the ceiling did not sort by.
- **F2. A negative gap is possible only through the neighbour's ceiling**, which can delete an edge that
  outranks one the centre kept (`DXQ-A4`). Trim-supply §1 owns how rare those deletions are.
- **F3. Ties at 1.0.** The rescale saturates the strongest scores at exactly 1.0. A gap of exactly 0 in
  emitted similarity can therefore hide a positive gap in cap ranking value. Both are reported.

## Measures, and the summary statistics fixed for each

**Two summaries for every measure and every group:**
- **(i) centre-weighted (primary):** take the median within each centre, then report the median, p10 and
  p90 of those per-centre medians across centres, with the centre count. *Each famous artist counts
  once.*
- **(ii) pooled (secondary):** over all edges in the group: median, p10, p25, p75, p90, mean, n. *This is
  dominated by the centres with the most deletions*, which is why it is secondary.

For comparisons, the **paired per-centre difference** of medians (`DXQ-D` minus the other group) is
reported as median, p10, p90 and the share of centres where it is negative, over the centres that have
both groups.

| id | measure | groups | extra statistic | plain sentence |
|---|---|---|---|---|
| `DXQ-M1` | cap ranking value, and the listening score beside it | all five | — | *how strongly the listening data links the famous artist to this one* |
| `DXQ-M2` | emitted similarity | all five | pooled share in bins [0, 0.5), [0.5, 0.6), [0.6, 0.7), [0.7, 0.8), [0.8, 0.9), [0.9, 1.0), exactly 1.0 | *the similarity the app would show for this step* |
| `DXQ-M3a` | the neighbour's served degree on lba-a6, and its pre-ceiling degree | all five | — | *how many connections the less-listened artist has on the map, and had before the limit* |
| `DXQ-M3b` | the number of top-1 % centres in the neighbour's **own** top-50 (`keep[v]`) | `DXQ-D`, `DXQ-KL`, `DXQ-DS1` | share of edges where it is ≥ 10 | *how many of the most-listened 1 % this artist names among its own fifty most similar. A high count is a proxy for "names famous artists because everyone plays them", the noise trim-supply §3 worries about. It is a proxy, not a measure of sound* |
| `DXQ-M4` | the neighbour's fame percentile | all five | pooled share in bands [0.8, 0.9), [0.5, 0.8), [0, 0.5) | *how far below the top the exit sits* |
| `DXQ-M5` | the neighbour's 1-based rank in `c`'s own ranked list (`ranking[c]` sorted by value descending, ties on lowest MBID, as the top-50 step sorts), and that rank ÷ the list's length | `DXQ-D`, `DXQ-DS1` (and `DXQ-K` for reference) | pooled share in rank buckets 1–50, 51–100, 101–250, 251–500, 501–1,000, > 1,000; per centre, the rank of its **best-ranked** deleted exit, summarised across centres | *how far down the famous artist's own list of similar artists the lost exit sat* |
| `DXQ-M6` | per centre: the weakest kept connection's value minus the strongest deleted exit's, in emitted similarity **and** in cap ranking value | centres with ≥ 1 `DXQ-K` and ≥ 1 `DXQ-D` | median, p10, p90 across centres; share exactly 0; share negative (with `DXQ-A4`). For scale, beside it: the per-centre spread of `DXQ-K` (strongest minus weakest kept), same summary | *how far below the famous artist's weakest kept connection its best lost exit sits* |
| `DXQ-M7` | the router's price for one step `c → v` at today's weights: `w_sim·(1 − s) + w_jump·|pop_raw_c − pop_raw_v| + w_hop` | all five | reported separately: the floor term's **upper bound** `w_floor·max(0, pop_raw_c − pop_raw_v)` at zero presses, which is its value for a pair whose less-famous endpoint is `c` itself; dislikes are absent, so the avoid term is 0 | *what the router would charge for stepping from the famous artist to this one, before any press* |
| `DXQ-M8` | single-step break-even: for each deleted exit `v`, `k*(v) = (M7(v) − M7(e*)) / (w_ramp·(fame(e*) − fame(v)))`, where `e*` is `c`'s cheapest kept connection by `DXQ-M7` and `w_ramp` is `w_known_ramp_fame_pctl`; infinite when the denominator ≤ 0. Per centre, the smallest `k*` over its `DXQ-D` | centres with ≥ 1 `DXQ-D` | median, p10, p90 across centres; share of centres with `k*` ≤ 10, ≤ 20, finite; the same divided by 2 and by 3 for the 2× and 3× pulls, as arithmetic only | *how many Dig deeper presses before the best lost exit would be cheaper, as a single step, than the famous artist's cheapest kept connection* |

**`DXQ-M8` is single-step arithmetic, not a routing prediction.** The router compares whole journeys,
and the lattice already routed them (`docs/superpowers/findings/2026-09-28-drp-lattice-results.md`). It
shows the size of the price gap that the per-press pull must overcome. It may not be read as "the router
would take this exit after `k*` presses". The floor term is excluded from `M8` because it depends on the
journey's endpoints.

## Reads — descriptive, fixed now

**No read here has a threshold, because none gates or triggers anything.** This measurement decides
nothing (above), so there is no branch for an effect size to fire. The plain sentences above are the
reads. Each is reported as measured, with the summary statistics fixed above and no others promoted to
the headline.

**Barred, whatever the figures say:**
- that the deleted exits are **good** or **noise** in the sense of how they sound. The measures are the
  map's own. `SNW-R4` says the map's similarity did not track his ear on the `DSL-` marks.
- that `DXQ-D` is weaker than `DXQ-K` as a **finding** (F1: by construction).
- any attribution of a `DXQ-D`-versus-`DXQ-K` difference to survival alone or to fame band alone
  (factor table).
- any reading of `DXQ-M8` as a routing outcome.
- anything about the `DSL-` verdict from `DXQ-DS1`. The listen judged the candidate whole
  (`docs/superpowers/findings/2026-10-01-dsl-listen-results.md` §4).

**Run state.** Every figure comes from one complete run. No partial output is read. If the run refuses,
its refusal is recorded and nothing is reported in §1.

## Files (written by the run)

- `dxq.py` produces every figure. No command-line arguments. Run from `builder/`:

      cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
        uv run python -u analysis/2026-10-26-issue-270-discarded-exit-quality/dxq.py

- `dxq.out.txt`: its full stdout, including `trim_supply.py`'s.
- `dxq_results.json`: every summary above, machine-readable.
- `dxq_centres.csv`: one row per centre, MBID only (no names): group sizes, per-centre medians, the
  gaps, best deleted-exit rank, smallest `k*`.

## 1. Measured

*Written from `dxq.out.txt` and `dxq_results.json` of the one recorded run (exit 0 and wall time 20.0 min as reported by the analyst's shell; neither is printed in `dxq.out.txt`). Every figure below is a value in `dxq_results.json`; the key path is given per table. Measured only.*

### Identity

| input | sha256 as printed by the run | check |
|---|---|---|
| `graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` | == sidecar == pin (`trim_supply.py`) |
| S4-A6 `MANIFEST.json`, before | `950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3` | == pin (`trim_supply.py`) |
| S4-A6 `MANIFEST.json`, after | `950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3` | unchanged (`trim_supply.py`) |
| `graph-drp-s1.bin` | `418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f` | == sidecar == pin (`dxq.py`, before anything else was read) |
| `trim_supply.py` (executed unmodified) | `ace57c262aec0ebb2888a1d928e2cab1634ea079c4cb15502ec71ea3fd3da7f9` | — |

Population file `1bbff8fcfde78a07d276f727ccaf048c73da4bfd27709b64f6f6894d6d4d2d7b` == archive manifest (`trim_supply.py`). `trim_supply.py`'s own reproductions all printed True, including its four graph-descriptives §1 A zero counts (`dxq.out.txt`).

**Router weights, `ApiConfig()` at run time:** `w_sim` 3.0, `w_jump` 1.0, `w_floor` 1.0, `w_hop` 0.02, `w_avoid` 1.0, `w_degree_hub` 0.0, `w_known_ramp_fame_pctl` 0.01.

**Centres:** 874 (lba-a6 nodes with measured fame percentile ≥ 0.99).

**Excluded and counted** (`exclusions`): null-fame served neighbours of centres 0; null-fame deleted neighbours 17; deleted neighbours that are not lba-a6 nodes (no fame percentile; lost to the largest-component prune) 2,015.

### Assertions

- `DXQ-A1`: **pass** — 40,776 kept edges at the centres checked, 0 mismatches.
- `DXQ-A2`: deleted exits missing from the centre's own ranked list: `DXQ-D` 0, `DXQ-DS1` 0 (expected 0); `DXQ-K`, for `DXQ-M5` reference, 0.
- `DXQ-A3`: **pass** — 0 violations. Edges in `graph-drp-s1.bin` not in lba-a6: 7,998; touching a centre 7,998; touching none 0; `DRP-C10` added edges (`drp_g3.json`) 7,998.
- `DXQ-A4`: **pass** — negative-gap centres with no below-0.9 edge deleted by the neighbour's ceiling: 0 (emitted similarity), 0 (cap ranking value). Negative-gap centres: 57 (emitted similarity), 62 (cap ranking value).
- Listening score is reconstructed as `round(expm1(cap ranking value))`; max absolute deviation from an integer 2.5e-11.

### How to read the tables

**Centre-weighted (primary):** median within each centre, then median / p10 / p90 of those per-centre medians, with the centre count. **Pooled (secondary):** over all edges in the group. **Paired:** per-centre median of `DXQ-D` minus the other group's, over centres with both; "share < 0" is the share of those centres where the difference is negative. Group sizes in edges are the pooled `n`.

### `DXQ-M1` — cap ranking value

*how strongly the listening data links the famous artist to this one* — `results.groups.M1_cap_ranking_value`, `results.comparisons.M1_cap_ranking_value`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 7.848 | 6.053 | 8.992 | 7.946 | 5.994 | 7.188 | 8.594 | 9.157 | 7.702 | 40,776 |
| `DXQ-KL` | 493 | 6.812 | 3.611 | 8.430 | 5.100 | 2.890 | 3.871 | 6.976 | 7.908 | 5.309 | 4,132 |
| `DXQ-D` | 817 | 3.401 | 2.833 | 4.007 | 3.401 | 2.079 | 2.565 | 4.331 | 5.226 | 3.558 | 639,186 |
| `DXQ-DH` | 874 | 6.554 | 5.727 | 7.997 | 6.267 | 4.691 | 5.361 | 7.324 | 8.152 | 6.335 | 187,651 |
| `DXQ-DS1` | 817 | 6.080 | 4.076 | 7.633 | 6.158 | 4.205 | 5.313 | 6.960 | 7.767 | 6.058 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -3.600 | -4.753 | -1.580 | 0.9863 |
| `DXQ-D` − `DXQ-DH` | 817 | -3.035 | -4.682 | -2.272 | 0.9976 |
| `DXQ-D` − `DXQ-K` | 817 | -4.447 | -5.527 | -3.160 | 0.9951 |
| `DXQ-D` − `DXQ-DS1` | 817 | -2.647 | -3.962 | -0.847 | 0.9559 |

### `DXQ-M1` — listening score (beside it)

*how strongly the listening data links the famous artist to this one* — `results.groups.M1_listening_score`, `results.comparisons.M1_listening_score`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 2558.8 | 424.6 | 8033.9 | 2822.0 | 400.0 | 1322.0 | 5396.0 | 9482.0 | 4024.6 | 40,776 |
| `DXQ-KL` | 493 | 916.0 | 36.0 | 4584.2 | 163.0 | 17.0 | 47.0 | 1069.2 | 2716.9 | 916.0 | 4,132 |
| `DXQ-D` | 817 | 29.0 | 16.0 | 54.0 | 29.0 | 7.0 | 12.0 | 75.0 | 185.0 | 97.4 | 639,186 |
| `DXQ-DH` | 874 | 701.0 | 305.9 | 2971.6 | 526.0 | 108.0 | 212.0 | 1515.0 | 3471.0 | 1253.0 | 187,651 |
| `DXQ-DS1` | 817 | 436.0 | 58.0 | 2077.9 | 471.5 | 66.0 | 202.0 | 1053.0 | 2361.1 | 961.7 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -1053.8 | -4961.8 | -57.3 | 0.9863 |
| `DXQ-D` − `DXQ-DH` | 817 | -633.5 | -2857.3 | -274.1 | 0.9976 |
| `DXQ-D` − `DXQ-K` | 817 | -2741.5 | -8091.4 | -541.6 | 0.9951 |
| `DXQ-D` − `DXQ-DS1` | 817 | -401.5 | -2026.5 | -27.9 | 0.9559 |

### `DXQ-M2` — emitted similarity

*the similarity the app would show for this step* — `results.groups.M2_emitted_similarity`, `results.comparisons.M2_emitted_similarity`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 1.000 | 0.794 | 1.000 | 1.000 | 0.787 | 0.943 | 1.000 | 1.000 | 0.939 | 40,776 |
| `DXQ-KL` | 493 | 0.894 | 0.474 | 1.000 | 0.669 | 0.379 | 0.508 | 0.916 | 1.000 | 0.685 | 4,132 |
| `DXQ-D` | 817 | 0.446 | 0.372 | 0.526 | 0.446 | 0.273 | 0.337 | 0.568 | 0.686 | 0.467 | 639,186 |
| `DXQ-DH` | 874 | 0.860 | 0.752 | 1.000 | 0.823 | 0.616 | 0.704 | 0.961 | 1.000 | 0.816 | 187,651 |
| `DXQ-DS1` | 817 | 0.798 | 0.535 | 0.997 | 0.808 | 0.552 | 0.697 | 0.914 | 1.000 | 0.786 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -0.444 | -0.549 | -0.207 | 0.9840 |
| `DXQ-D` − `DXQ-DH` | 817 | -0.398 | -0.577 | -0.298 | 0.9951 |
| `DXQ-D` − `DXQ-K` | 817 | -0.529 | -0.594 | -0.408 | 0.9927 |
| `DXQ-D` − `DXQ-DS1` | 817 | -0.347 | -0.494 | -0.111 | 0.9559 |

Pooled share by bin (`pooled_bin_shares`):

| group | [0.0, 0.5) | [0.5, 0.6) | [0.6, 0.7) | [0.7, 0.8) | [0.8, 0.9) | [0.9, 1.0) | exactly 1.0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 0.0249 | 0.0183 | 0.0256 | 0.0379 | 0.0776 | 0.1912 | 0.6244 |
| `DXQ-KL` | 0.2430 | 0.1583 | 0.1375 | 0.1055 | 0.0825 | 0.1251 | 0.1481 |
| `DXQ-D` | 0.6194 | 0.1827 | 0.1095 | 0.0518 | 0.0221 | 0.0096 | 0.0049 |
| `DXQ-DH` | 0.0176 | 0.0642 | 0.1607 | 0.2091 | 0.1983 | 0.1589 | 0.1912 |
| `DXQ-DS1` | 0.0688 | 0.0655 | 0.1202 | 0.2229 | 0.2439 | 0.1558 | 0.1229 |

### `DXQ-M3a` — the neighbour's served degree on lba-a6

*how many connections the less-listened artist has on the map, and had before the limit* — `results.groups.M3a_served_degree`, `results.comparisons.M3a_served_degree`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 49.0 | 40.8 | 50.0 | 49.0 | 26.0 | 46.0 | 50.0 | 50.0 | 44.4 | 40,776 |
| `DXQ-KL` | 493 | 46.0 | 14.0 | 50.0 | 27.0 | 9.0 | 14.0 | 49.0 | 50.0 | 29.6 | 4,132 |
| `DXQ-D` | 817 | 16.0 | 12.0 | 20.0 | 17.0 | 6.0 | 10.0 | 28.0 | 45.0 | 20.6 | 639,186 |
| `DXQ-DH` | 874 | 47.0 | 35.0 | 49.0 | 46.0 | 11.0 | 23.0 | 50.0 | 50.0 | 36.8 | 187,651 |
| `DXQ-DS1` | 817 | 33.5 | 13.5 | 50.0 | 34.0 | 9.0 | 17.0 | 50.0 | 50.0 | 32.3 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -28.8 | -34.6 | -0.5 | 0.9018 |
| `DXQ-D` − `DXQ-DH` | 817 | -29.0 | -34.5 | -19.0 | 0.9963 |
| `DXQ-D` − `DXQ-K` | 817 | -33.0 | -36.0 | -27.0 | 0.9927 |
| `DXQ-D` − `DXQ-DS1` | 817 | -16.5 | -34.0 | 0.0 | 0.8482 |

### `DXQ-M3a` — the neighbour's pre-ceiling degree (`SUP-S3` size)

*how many connections the less-listened artist has on the map, and had before the limit* — `results.groups.M3a_pre_ceiling_degree`, `results.comparisons.M3a_pre_ceiling_degree`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 308.5 | 71.8 | 1149.3 | 305.0 | 60.0 | 108.0 | 864.0 | 2156.0 | 837.3 | 40,776 |
| `DXQ-KL` | 493 | 84.0 | 51.0 | 505.0 | 57.0 | 50.0 | 51.0 | 100.0 | 253.9 | 129.1 | 4,132 |
| `DXQ-D` | 817 | 52.0 | 51.0 | 53.0 | 53.0 | 50.0 | 51.0 | 58.0 | 72.0 | 59.3 | 639,186 |
| `DXQ-DH` | 874 | 99.0 | 70.0 | 2449.7 | 89.0 | 54.0 | 62.0 | 207.0 | 1198.0 | 594.0 | 187,651 |
| `DXQ-DS1` | 817 | 65.5 | 52.0 | 182.7 | 65.0 | 51.0 | 54.0 | 112.8 | 234.0 | 128.7 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -47.8 | -455.0 | -2.0 | 0.9498 |
| `DXQ-D` − `DXQ-DH` | 817 | -42.0 | -2322.8 | -18.0 | 1.0000 |
| `DXQ-D` − `DXQ-K` | 817 | -280.0 | -1130.0 | -31.8 | 0.9927 |
| `DXQ-D` − `DXQ-DS1` | 817 | -12.0 | -122.3 | -1.0 | 0.9364 |

### `DXQ-M3b` — top-1 % centres in the neighbour's own top-50 (a proxy, not a measure of sound)

*how many of the most-listened 1 % this artist names among its own fifty most similar. A high count is a proxy for "names famous artists because everyone plays them", the noise trim-supply §3 worries about. It is a proxy, not a measure of sound* — `results.groups.M3b_centres_in_own_top50`, `results.comparisons.M3b_centres_in_own_top50`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-D` | 817 | 18.0 | 11.6 | 25.0 | 16.0 | 5.0 | 9.0 | 24.0 | 32.0 | 17.3 | 639,186 |
| `DXQ-KL` | 493 | 21.0 | 9.0 | 32.0 | 19.0 | 6.0 | 11.0 | 28.0 | 36.0 | 20.2 | 4,132 |
| `DXQ-DS1` | 817 | 19.5 | 9.0 | 31.0 | 20.0 | 7.0 | 12.0 | 28.0 | 36.0 | 20.7 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -3.0 | -13.6 | 6.0 | 0.6233 |
| `DXQ-D` − `DXQ-DS1` | 817 | -1.5 | -8.5 | 4.0 | 0.5863 |

Pooled share of edges with ≥ 10 (`pooled_share_ge_10`): `DXQ-D` 0.7299; `DXQ-KL` 0.8018; `DXQ-DS1` 0.8253.

### `DXQ-M4` — the neighbour's fame percentile

*how far below the top the exit sits* — `results.groups.M4_fame_percentile`, `results.comparisons.M4_fame_percentile`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 0.991 | 0.946 | 0.998 | 0.991 | 0.898 | 0.975 | 0.997 | 0.999 | 0.955 | 40,776 |
| `DXQ-KL` | 493 | 0.804 | 0.632 | 0.882 | 0.769 | 0.316 | 0.584 | 0.854 | 0.884 | 0.683 | 4,132 |
| `DXQ-D` | 817 | 0.576 | 0.455 | 0.661 | 0.567 | 0.150 | 0.329 | 0.756 | 0.848 | 0.532 | 639,186 |
| `DXQ-DH` | 874 | 0.967 | 0.952 | 0.999 | 0.962 | 0.914 | 0.934 | 0.986 | 0.997 | 0.959 | 187,651 |
| `DXQ-DS1` | 817 | 0.821 | 0.647 | 0.878 | 0.823 | 0.529 | 0.708 | 0.875 | 0.892 | 0.756 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | -0.275 | -0.386 | -0.120 | 0.9635 |
| `DXQ-D` − `DXQ-DH` | 817 | -0.392 | -0.531 | -0.309 | 1.0000 |
| `DXQ-D` − `DXQ-K` | 817 | -0.414 | -0.509 | -0.327 | 0.9976 |
| `DXQ-D` − `DXQ-DS1` | 817 | -0.237 | -0.340 | -0.062 | 0.9364 |

Pooled share by band (`pooled_band_shares`):

| group | [0.8, 0.9) | [0.5, 0.8) | [0.0, 0.5) |
|---|---:|---:|---:|
| `DXQ-K` | 0.0425 | 0.0394 | 0.0195 |
| `DXQ-KL` | 0.4192 | 0.3884 | 0.1924 |
| `DXQ-D` | 0.1804 | 0.3942 | 0.4254 |
| `DXQ-DH` | 0.0000 | 0.0000 | 0.0000 |
| `DXQ-DS1` | 0.5651 | 0.3455 | 0.0894 |

### `DXQ-M5` — 1-based rank in the centre's own ranked list

*how far down the famous artist's own list of similar artists the lost exit sat* — `results.groups.M5_rank_in_centre_list`, `results.comparisons.M5_rank_in_centre_list`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-D` | 817 | 703.0 | 201.5 | 3536.0 | 2863.0 | 547.0 | 1197.0 | 6258.0 | 11358.0 | 4688.6 | 639,186 |
| `DXQ-DS1` | 817 | 196.5 | 119.8 | 387.8 | 194.0 | 110.0 | 148.0 | 268.0 | 386.0 | 229.5 | 7,998 |
| `DXQ-K` | 874 | 43.5 | 26.5 | 113.9 | 43.0 | 9.0 | 22.0 | 80.0 | 128.0 | 56.8 | 40,776 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-K` | 817 | 656.0 | 114.5 | 3509.8 | 0.0049 |
| `DXQ-D` − `DXQ-DS1` | 817 | 494.0 | 30.5 | 3218.8 | 0.0000 |

Pooled share by rank bucket (`pooled_bucket_shares`):

| group | 1-50 | 51-100 | 101-250 | 251-500 | 501-1000 | > 1000 |
|---|---:|---:|---:|---:|---:|---:|
| `DXQ-D` | 0.0001 | 0.0009 | 0.0228 | 0.0643 | 0.1207 | 0.7912 |
| `DXQ-DS1` | 0.0091 | 0.0678 | 0.6332 | 0.2418 | 0.0454 | 0.0028 |
| `DXQ-K` | 0.5829 | 0.2318 | 0.1839 | 0.0014 | 0.0000 | 0.0000 |

Per centre, rank of its best-ranked `DXQ-D` exit (`best_ranked_D_exit_per_centre`): median 145.0, p10 60.6, p90 249.0, over 817 centres.

### `DXQ-M5` — rank ÷ list length

*how far down the famous artist's own list of similar artists the lost exit sat* — `results.groups.M5_rank_over_list_length`, `results.comparisons.M5_rank_over_list_length`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-D` | 817 | 0.575 | 0.489 | 0.776 | 0.538 | 0.205 | 0.342 | 0.748 | 0.893 | 0.543 | 639,186 |
| `DXQ-DS1` | 817 | 0.181 | 0.035 | 0.630 | 0.165 | 0.031 | 0.069 | 0.344 | 0.609 | 0.245 | 7,998 |
| `DXQ-K` | 874 | 0.043 | 0.005 | 0.403 | 0.034 | 0.003 | 0.009 | 0.129 | 0.378 | 0.118 | 40,776 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-K` | 817 | 0.518 | 0.423 | 0.587 | 0.0049 |
| `DXQ-D` − `DXQ-DS1` | 817 | 0.386 | 0.119 | 0.490 | 0.0000 |

### `DXQ-M7` — router price `w_sim·(1 − s) + w_jump·|Δpop_raw| + w_hop`

*what the router would charge for stepping from the famous artist to this one, before any press* — `results.groups.M7_router_price`, `results.comparisons.M7_router_price`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 0.157 | 0.093 | 0.734 | 0.166 | 0.047 | 0.087 | 0.314 | 0.771 | 0.307 | 40,776 |
| `DXQ-KL` | 493 | 0.493 | 0.101 | 1.699 | 1.125 | 0.139 | 0.397 | 1.603 | 2.018 | 1.081 | 4,132 |
| `DXQ-D` | 817 | 1.948 | 1.665 | 2.221 | 2.045 | 1.275 | 1.656 | 2.397 | 2.653 | 1.993 | 639,186 |
| `DXQ-DH` | 874 | 0.625 | 0.289 | 1.014 | 0.821 | 0.196 | 0.380 | 1.215 | 1.506 | 0.836 | 187,651 |
| `DXQ-DS1` | 817 | 0.820 | 0.263 | 1.539 | 0.796 | 0.227 | 0.473 | 1.091 | 1.496 | 0.840 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | 1.461 | 0.664 | 1.809 | 0.0160 |
| `DXQ-D` − `DXQ-DH` | 817 | 1.266 | 0.969 | 1.659 | 0.0061 |
| `DXQ-D` − `DXQ-K` | 817 | 1.721 | 1.327 | 1.997 | 0.0037 |
| `DXQ-D` − `DXQ-DS1` | 817 | 1.110 | 0.354 | 1.612 | 0.0000 |

### `DXQ-M7` — floor term upper bound `w_floor·max(0, pop_raw_c − pop_raw_v)`, reported separately

*what the router would charge for stepping from the famous artist to this one, before any press* — `results.groups.M7_floor_upper_bound`, `results.comparisons.M7_floor_upper_bound`

| group | centres | centre-wtd median | p10 | p90 | pooled median | p10 | p25 | p75 | p90 | mean | n edges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `DXQ-K` | 874 | 0.057 | 0.000 | 0.132 | 0.051 | 0.000 | 0.000 | 0.119 | 0.179 | 0.070 | 40,776 |
| `DXQ-KL` | 493 | 0.109 | 0.027 | 0.199 | 0.110 | 0.043 | 0.082 | 0.142 | 0.189 | 0.114 | 4,132 |
| `DXQ-D` | 817 | 0.241 | 0.133 | 0.384 | 0.377 | 0.239 | 0.304 | 0.442 | 0.500 | 0.373 | 639,186 |
| `DXQ-DH` | 874 | 0.150 | 0.000 | 0.298 | 0.261 | 0.000 | 0.168 | 0.338 | 0.395 | 0.243 | 187,651 |
| `DXQ-DS1` | 817 | 0.171 | 0.101 | 0.268 | 0.166 | 0.093 | 0.123 | 0.224 | 0.276 | 0.176 | 7,998 |

| paired (per-centre medians) | centres | median | p10 | p90 | share < 0 |
|---|---:|---:|---:|---:|---:|
| `DXQ-D` − `DXQ-KL` | 438 | 0.097 | 0.037 | 0.212 | 0.0137 |
| `DXQ-D` − `DXQ-DH` | 817 | 0.088 | 0.060 | 0.164 | 0.0000 |
| `DXQ-D` − `DXQ-K` | 817 | 0.182 | 0.090 | 0.294 | 0.0037 |
| `DXQ-D` − `DXQ-DS1` | 817 | 0.057 | 0.020 | 0.144 | 0.0012 |

### `DXQ-M6` — weakest kept connection minus strongest deleted exit, per centre

*how far below the famous artist's weakest kept connection its best lost exit sits* — `results.M6`. Gap over centres with ≥ 1 `DXQ-K` and ≥ 1 `DXQ-D`; spread of `DXQ-K` (strongest minus weakest kept) beside it, for scale.

| currency | quantity | centres | median | p10 | p90 | share exactly 0 | share < 0 |
|---|---|---:|---:|---:|---:|---:|---:|
| emitted similarity | gap | 817 | 0.0085 | 0.0000 | 0.1158 | 0.2656 | 0.0698 |
| emitted similarity | `DXQ-K` spread | 874 | 0.0491 | 0.0000 | 0.5480 | 0.3844 | 0.0000 |
| cap ranking value | gap | 817 | 0.1810 | 0.0000 | 1.2690 | 0.0269 | 0.0759 |
| cap ranking value | `DXQ-K` spread | 874 | 1.5408 | 0.9751 | 4.6279 | 0.0000 | 0.0000 |

### `DXQ-M8` — single-step break-even `k*`, smallest per centre

*how many Dig deeper presses before the best lost exit would be cheaper, as a single step, than the famous artist's cheapest kept connection* — `results.M8`. Single-step arithmetic, not a routing prediction. `w_known_ramp_fame_pctl` 0.01. Centres with ≥ 1 `DXQ-D`: 817; of those excluded for having no `DXQ-K`: 0. The 2× and 3× rows are `k*` ÷ 2 and ÷ 3, arithmetic only.

| pull | centres | median | p10 | p90 | share `k*` ≤ 10 | share ≤ 20 | share finite |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1× | 817 | 146.68 | 43.10 | 205.22 | 0.0294 | 0.0477 | 0.9976 |
| 2× | 817 | 73.34 | 21.55 | 102.61 | 0.0477 | 0.0918 | 0.9976 |
| 3× | 817 | 48.89 | 14.37 | 68.41 | 0.0698 | 0.1457 | 0.9976 |

`k*` is reported as computed by the formula, including values ≤ 0 (the best lost exit already cheaper at zero presses and less famous than the cheapest kept connection): centres with smallest `k*` ≤ 0: 8 (`diagnostic_centres_kstar_le_0`). These fall inside the ≤ 10 and ≤ 20 shares.

### Run notes

- Emitted similarity is taken as float32, the width the artifact stores (`DXQ-A1` shows it equals the served score on every kept edge); `DXQ-M2`'s bins and `DXQ-M7`'s price use that value for every group.
- `DXQ-M3a`'s pre-ceiling degree is `|SUP-S3(v)|` restricted to lba-a6 nodes, as `SUP-S3` is defined in trim-supply's stage table. Groups are drawn from `SUP-S3` likewise restricted to nodes; the non-node deleted neighbours are the excluded count above.
- `DXQ-M8`'s `e*` ties on price would break on lowest MBID.
- Before the recorded run, `dxq.py`'s post-build code was exercised once against a namespace reconstructed from the `DRP-` stage-3a capture (`capture.pkl`), to catch code errors without spending a 20-minute build. Its outputs were written outside this directory and deleted; no figure here comes from it.

## 2. What I infer from it (inference, labelled)

*Written by the coordinating session after §1 was committed (`930697d`). The analyst's brief was
derivation only.* Each sentence names the measure it rests on, so it can be disagreed with.

- **Most of what the limit throws away is weak by the map's own data. The best of it is not.** The
  typical lost exit sits about seven hundred places down the famous artist's own list of similar
  artists. Its listening score is a small fraction of a kept connection's, and the app would show it
  as under half-similar. (`DXQ-M5`, *how far down the famous artist's own list of similar artists the
  lost exit sat*; `DXQ-M1`, *how strongly the listening data links the famous artist to this one*;
  `DXQ-M2`, *the similarity the app would show for this step*.) But at the median famous artist, the
  best lost exit sits just under the weakest connection it kept. On the app's similarity scale the gap
  is under a hundredth; on the cap ranking value (the score the limit sorts by) it is a small fraction
  of how much the kept connections vary among themselves. At the far end of famous artists (the p90
  row of the §1 table) the gap is much wider (`DXQ-M6`, *how far below the famous artist's weakest kept
  connection its best lost exit sits*). **So, for most famous artists, the limit cuts through a
  continuum, not at a cliff.** "Hundreds of discarded candidates per famous artist" (trim-supply §2)
  overstates what a build change would have to work with: what sits near the kept connections is a
  short top slice of each list (`DXQ-M5`, best deleted-exit rank per centre), not the hundreds.
- **The ten the earlier experiment put back were that top slice.** Those exits (`DXQ-DS1`, *the deleted
  exits the extra-connections experiment put back, which the listen heard*) are far stronger than the
  lost exits as a whole on listening score, shown similarity and list position (`DXQ-M1`, `DXQ-M2`,
  `DXQ-M5`, sentences above), and closer to the fame of what was kept (`DXQ-M4`, *how far below the
  top the exit sits*). That is by their selection rule: strongest first. They are not separated on the
  noise proxy below.
- **The one noise proxy does not single out the lost exits.** At a typical famous artist, its lost
  exits name slightly *fewer* of the most-listened 1 % among their own fifty most similar than its
  kept less-listened connections do. The difference is small and leans that way at only somewhat more
  than half the famous artists (`DXQ-M3b`, *how many of the most-listened 1 % this artist names among
  its own fifty most similar*; §1 paired rows). So the proxy gives no sign that the lost exits are
  more "famous-because-everyone-plays-them" than what was kept. It is a proxy, not a measure of sound.
- **What the router would charge to use them is far above what it charges now.** Stepping from a
  famous artist to a typical lost exit costs roughly twelve times what a kept connection costs before
  any press. Even the restored top ten cost about five times as much (`DXQ-M7`, *what the router would
  charge for stepping from the famous artist to this one, before any press*). At today's per-press
  pull, the best lost exit at a typical famous artist would need on the order of 150 presses to become
  cheaper, as a single step, than the cheapest kept connection, and about 50 at three times the pull
  (`DXQ-M8`, *how many Dig deeper presses before the best lost exit would be cheaper, as a single step,
  than the famous artist's cheapest kept connection*). This is single-step arithmetic, not a routing
  outcome (§ "Reads", barred). The lattice did route, and found the stronger pulls did not make famous
  journeys less famous (lattice results §1.2, with its qualifier (vi): *"the scale is capped here: this
  result cannot rule out that the cell made famous journeys more famous"*). This shows **how large the
  single-step gap is** that a per-press pull on fame would have to close.

**In the app's terms:** a map change that only lets famous artists keep a few more less-listened
connections would be giving them links the listening data rates almost as highly as ones they keep
today. But the router would price each of those links, as a single step, far above its current
choices, and a fame pull of the size tried closes that single-step gap only after far more presses
than anyone makes (§3 says why one step is not a journey). A larger map change would mostly be promoting links the data rates
weakly, and nothing here says whether they *sound* right.

## 3. Weakest link

- **Every measure is the map's own.** The map's similarity did not track the owner's ear on the
  `DSL-` weak-step marks (`SNW-R4`, *"On his marked steps, map similarity did not score worse than on
  the unmarked steps of the same journey clearly enough to pass the bar."*). So "weak by the map's data" is not "sounds
  wrong", and "close to the kept edges" is not "sounds right". **I would defend** the structural
  reading: the limit cuts a continuum, the usable slice is short, and the price gap is large. All of it
  is arithmetic over one build that reproduces the served map. **I would give up cheaply** any
  sentence that calls the lost exits good or bad links.
- **The price is one step, not a journey.** `DXQ-M7` and `M8` leave out the floor term (its upper bound
  is reported separately) and every downstream step. A route can pay one expensive exit and then
  travel cheaply.
- **Saturation.** Over a quarter of famous artists show a gap of exactly 0 on the app's similarity
  scale, because both edges sit at the 1.0 clip (`DXQ-M6`, share exactly 0). On the cap ranking value,
  where few are tied, the gap is still small beside the spread of kept connections. So
  "continuum" does not rest on the clip, but its exact size on the app's scale does.
- **The price is not decomposed.** Whether the exit price is mostly the similarity term or mostly
  the popularity-jump term was not in the fixed statistics, so it is not reported. It matters for the
  routing option below.
- **What would falsify "the usable slice is short":** a listen or a coherence measure that finds the
  lost exits ranked a few hundred places down sound as good as the top ten. Nothing in the record has
  measured that.

## 4. Options and their consequences

**Which of these to pursue, if any, is the owner's decision:** it is a choice about what the app
should do and what to spend his ear and others' time on (`CLAUDE.md`, "Whose decision is it"). Nothing
here is a recommendation. Each option names the cheapest experiment that could decide it, and its cost.

- **A build-side change at the trim**, for example reserving a few of a famous artist's fifty slots
  for its strongest less-listened partners, displacing famous ones rather than adding beside them.
  - *What this measurement says:* there is a short top slice to promote (`DXQ-M6`, *how far below the
    famous artist's weakest kept connection its best lost exit sits*). The record already holds the
    **additive** version at today's pull, and it did not make famous journeys less famous (lattice
    results §1.2, the extra connections at today's pull, qualifier (vi) attached).
  - *Cheapest decisive experiment:* one displacing rebuild from the trim-supply instrumented build,
    then one lattice cell at today's pull on the existing `DRP-T1` and `DRP-T2` famous-pair strata
    (`drp_pairs.json`) with the stage-3b harness. It reads whether a map change alone makes famous
    journeys less famous; like every lattice null, a no-movement result there could not rule out
    journeys getting more famous (lattice qualifier (vi)). It cannot read whether the journeys still
    hang together.
  - *Cost:* a cold pre-registration, about 20 minutes of build, and a fraction of the stage-3b sweep's
    2.5 hours for eight cells (`builder/analysis/2026-09-28-drp-stage3b/README.md`). No listening
    unless it moves. The prior from this measurement and the lattice is that the router prices the
    promoted exits out.
- **A routing change that prices the exits, rather than pulling on fame per press.**
  - *What this measurement says:* the exit price is many times a kept step's (`DXQ-M7`, *what the
    router would charge for stepping from the famous artist to this one, before any press*). The fame
    pull of the size tried would need on the order of 150 presses to close it as a single step
    (`DXQ-M8`, *how many Dig deeper presses before the best lost exit would be cheaper, as a single
    step, than the famous artist's cheapest kept connection*).
  - *Cheapest decisive experiment, in two steps.* First, split the exit price into its similarity and
    popularity-jump parts. That is about 20 minutes of compute with no listening, a new descriptive with
    its statistics fixed first, and it says which term a routing change would act on. Then one lattice
    cell on the existing extra-connections map, with that term changed. On that map `DRP-R13` (*if a
    fame ceiling hardly had to rise to find a route, yet stronger pulls moved nothing, the connections
    exist and the pull does not take them*) already reads the binding constraint as pricing (lattice
    results §1.6).
  - *Cost:* a pre-registration for the cell, compute as above, and the owner's ear only if it moves.
    The `DSL-` barred reads still bind: the earlier coherence loss cannot be pinned on any single cost
    term (dsl-listen results §4).
- **A second similarity source not derived from co-listening: audio embeddings of the Deezer preview
  clips the app already resolves.**
  - *What the record holds:* nothing.
  - *Cheapest decisive experiment:* embed the clips of the artists on the journeys behind the 11
    unconsumed blind verdicts, then test, under a cold pre-registration and once, whether embedding
    similarity between neighbouring cards predicts those verdicts. That corpus is the record's named
    falsifier for any coherence instrument (#165, reopened 2026-10-03). `ct_retrodict.py`'s
    committed-but-unrun rule counts as the first attempt.
  - *Cost:* a few hundred clips through the existing clip resolver, an off-the-shelf audio model on
    CPU (roughly an hour; not measured here), and the pre-registration. No listening. **It spends the
    11 verdicts, a one-shot resource, which is the owner's to spend.** Whether Deezer's terms allow
    deriving features from previews is unchecked and is his question.
- **Evaluation by more than one listener.**
  - *What the record holds:* nothing.
  - *Cheapest decisive experiment:* present the frozen `DSL-` stimulus (`dsl_page_data.json`, 24 rows,
    harness existing) to one or two other listeners, blind, with the same questions. It reads whether
    the coherence verdict holds beyond one ear.
  - *Cost:* a pre-registration stating that it cannot re-read or overturn `DSL-R3` (run-once and final,
    dsl-listen results §4), and an hour or two of each listener's time. Recruiting them is the owner's
    hands. The tell that let him identify the new side, longer journeys with no stars, would reach them
    too (dsl-listen results §0, item 1).
