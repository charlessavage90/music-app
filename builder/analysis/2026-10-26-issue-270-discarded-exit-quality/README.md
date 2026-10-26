# Issue #270: the less-listened exits the fifty-connection limit deleted, against the connections it kept

**Role: FIGURES OWNER for this measurement, once §1 is filled.** Until then this file is the design,
fixed and committed **before any figure was computed**. The git timestamp of the commit that adds this
file without a §1 is the evidence of that order.

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

*(Empty until the run. Written by the analyst from `dxq.out.txt` and `dxq_results.json` only.)*
