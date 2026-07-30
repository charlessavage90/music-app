# Graph rebuild Track B — cap-rule selection simulation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Role: ACTIVE — the governing plan for Track B**, the cap-selection simulation owed under
`MKS-5b` and re-scoped by the owner on 2026-07-30 (§0). The successor plan that
`plans/2026-07-29-graph-rebuild-track-a.md` deferred strand 3 to. Identifiers **`CB-`**,
collision-checked against `docs/` 2026-07-30. Six tasks, one named seam after `CB-4`.

**Goal:** measure, offline and at production scale, what each candidate edge-cap rule
costs and buys — stranding, component exclusion, hub structure, and hub transit — on both
the production (`ALG-E`) and candidate (`ALG-B`) archives, so the cap rule for any future
rebuild is chosen on data rather than inherited.

**Architecture:** an analysis-only harness under `builder/analysis/2026-07-30-track-b-cap-selection/`
that mirrors `build_from_archive`'s stages with an injectable cap step, builds one graph
per (rule, parameter, archive) cell, and scores every cell with one shared metrics module
plus a path-level module that routes the real `find_path` over each candidate graph.
Nothing in `builder/src/` or `api/src/` changes.

**Tech stack:** Python via `uv` from `builder/`; imports `artistpath_builder` and (for the
path module) `artistpath_api` by `sys.path` insertion, the `as_run_arms.py` precedent.

## Global constraints

- **Analysis only.** No file under `builder/src/` or `api/src/` is modified. All shipped
  defaults stay: `BuilderConfig.max_neighbours_per_artist = 50`,
  `cap_strategy = "mutual_knn"`, `BuilderConfig.algorithm` carrying `contribution_5`,
  every `ApiConfig` weight. A change to any of these *is* an adoption decision and is the
  owner's.
- **Nothing is adopted by any result here**, and any eventual `ALG-B`/cap adoption still
  owes a blind listen (`REQ-38`) regardless of how decisive the simulation is.
- **Archives are read-only** (`GRT-A1`): the harness may call `.keys()`/`.get()` and must
  not construct a `Crawler` or write under `builder/scratch/graph-archive/` or
  `builder/scratch/grt-archive-algb/`. Reuse the read-only wrapper pattern from
  `builder/analysis/2026-07-29-algb-trial-build/grt_run.py`.
- **No comparative arm runs before the `CB-4` pre-registration is committed.** `CB-1`'s
  instrument gates run on the production cell only, which is measurement of the harness,
  not of any comparison.
- **Environment:** `UV_LINK_MODE=copy` on every `uv` command; `PYTHONIOENCODING=utf-8`
  on anything printing artist names; `python -u` on anything long-running.
- **Currency in the name** for every new quantity (`top1pct_degree_frac` style; `pop_pctl`
  only ever a percentile). The fame-band frame is the **adopted artifact's** percentile
  ranking (the `RC` precedent), fixed across all cells so band membership never moves with
  the thing being measured.

## §0 Scope rulings — owner, 2026-07-30, recorded so no session re-litigates them

1. **This track is cap-RULE selection, not k-tuning.** Grounds, all in the record:
   `SYN-6` (neither blind listen varied the both-ways rule against a bounded-degree
   alternative — the ear endorsed the *bound*), `CS-P0f` (the source score is symmetric,
   so reciprocity adds no similarity evidence and cuts the famous→obscure direction 87.4%
   of the time), `BTF-4` (a reciprocity-free bounded selection measured to halve max
   degree and cut stranding, on a different graph — an option, not a candidate, until
   this simulation measures it here). Mutual k-NN is **one candidate family among
   several, not the incumbent to be tuned.**
2. **The degree bound is a scoping constraint of this track, not a settled product
   conclusion.** Three claims travel together and are supported unequally: unbounded hubs
   degraded listening quality (supported — the blind listen, plus the saturated-node
   mechanism in `builder/analysis/2026-07-25-ceiling-ordering-headroom/`); bounding degree
   fixed it (supported only in one n=1 comparison whose arms differed in more than the
   bound); bounding degree is the *only* remedy (never tested). Every **candidate** here
   must demonstrate its degree bound, because an unbounded candidate re-imports the one
   risk with ear-evidence against it and no offline price. But **re-evaluating
   bounded-degree itself — e.g. router-priced unbounded graphs — is an open future track**,
   owner's trigger, and it would owe its own blind listen since ear-evidence is what
   condemned hubs. No summary of this track may cite `MKS-5b`/`SYN-6` as having closed it.
3. **The uncapped graph runs as a descriptive REFERENCE ROW, barred from selection.**
   Same metrics, zero candidacy. It exists so ruling 2's future track starts with measured
   baselines instead of a remembered fear, and so the cost of un-boundedness is a column
   rather than an assumption.
4. **Why re-questioning the early choice is legitimate** (owner, verbatim intent): the
   product requirements became well-defined only after the cap was adopted
   (`PRODUCT-REQUIREMENTS.md` is 2026-07-29; mutual k-NN is Phase 2), and the project is
   now data-driven in a way it was not at the start. Neither reason licenses skipping
   `MKS-5b`'s simulation requirement — this plan *is* that requirement being met.

## What decision this feeds, and whose it is

The simulation prices the cap rule for **any** rebuild and quantifies the `RC-A2`
interaction (the cap and the source algorithm interact; `GRT-P3` measured `ALG-B`'s
headline costs as largely `k = 50` artifacts). The decisions it feeds — adopt `ALG-B`,
rebuild under a different rule, or neither — are the owner's, parked, and out of scope.
The deliverable is a read against pre-registered criteria plus the four-part presentation
(measured / inferred / weakest link / options).

## Candidate space (the pre-registration fixes the exact grid)

| Family | Parameter | Bound mechanism | Notes |
|---|---|---|---|
| `mutual_knn(k)` | k ∈ {50, 60, 75, 100} | degree ≤ k by construction | Incumbent family; k = 50 on `ALG-E` is production and is every cell's anchor. Ceiling 100 per `LBS-3` (source lists cap at 100). |
| `trimmed_union(j, D)` | top-j union, hard ceiling D | edge-deletion trim to D, both endpoints, weakest-first, MBID tie-break | Non-reciprocal. Symmetrise first (keep stronger), then delete whole edges at over-D nodes — deletion preserves symmetry where per-node truncation (the deleted legacy strategy) does not. |
| `proximity_select(k)` | k, selection key per `BTF-4` | degree ≤ k by construction | Mutual k-NN shape with a different selection key (popularity-proximity-weighted, the `BTF-4` shape). **The prereg pins the exact key from `builder/analysis/2026-07-27-boilthefrog-reconstruction/` before any cell runs** — this plan deliberately does not invent the formula. |
| *(reference)* `uncapped` | — | **none — barred from selection** | §0 ruling 3. Descriptive row only. |

Two axes beside the family: **archive** ∈ {`ALG-E` production flat layout, `ALG-B`
`grt-archive-algb`} — both on disk, both read-only — and nothing else. Cross-family
comparisons are made **at matched realized bound** (the prereg fixes the matching rule);
a cross-family cell without a matched-bound partner is descriptive, not comparative.

## Held constant, and the two known dormant terms

The prereg's §0 must carry the full table; these two are known now and are the reason the
section exists:

- **Popularity is computed BEFORE the cap** (`pipeline.py` — `score_weighted_indegree`
  accumulates over the full uncapped adjacency, upstream of `mutual_knn_cap`), so
  `pop_raw` and the fame frame are **cap-invariant within an archive**. Genuinely
  constant across rule cells; **not** constant across archives — which is why the fame
  frame is fixed to the adopted artifact for band membership.
- **`w_degree_hub = 0.0` is inert in production *for a reason a cap change removes*.**
  Its comment records that the current top-1%-by-degree set is insular micro-genre
  artists, so the term was tuned to no-op **on the current capped graph**. Looser caps
  move famous artists into the top-degree set — the path module must not silently inherit
  the production value as if it were neutral, and any path-level read must state which
  weights it ran under. Same shape as the `w_floor` worked example in `CLAUDE.md`.
- Also fixed within every cell: the drop rule (`GR-1`), `filter_special_purpose`, the
  rescale strategy and the **unclipped ranking** input to the cap (Phase 1 §2.8). One
  hazard to name in the prereg: `ALG-B` scores are small integers (`LBS-1`), so low-score
  rank ties are common and the MBID tie-break decides who survives the cut — a rule-level
  artifact worth a sensitivity note, not a design change.

## Tasks

### CB-1: Variant-builder harness, gated on reproducing production

**Files:**
- Create: `builder/analysis/2026-07-30-track-b-cap-selection/cb_build_variants.py`
- Create: `builder/analysis/2026-07-30-track-b-cap-selection/README.md` (what is imported
  vs reimplemented; what the directory cannot conclude)

**Interfaces — produces:** `build_variant(archive_dir: Path, algorithm: str, rule: str,
params: dict) -> Graph` mirroring `build_from_archive`'s stages (identity harvest → drops
→ mass → damped strength → rescale → **injectable cap step** → `symmetrise` →
`largest_component` → `build_graph`), importing `damped_strength`, `rescale_scores`,
`harvest_identities`, `mutual_knn_cap`, `symmetrise`, `largest_component` from
`artistpath_builder` rather than copying them. Writes each cell's artifact to
`builder/scratch/cb-cells/<archive>-<rule>-<params>.bin` (gitignored) with a manifest
JSON (sha256, node/edge counts, params) beside it.

- [ ] Implement `build_variant` with `rule="mutual_knn"` delegating to `mutual_knn_cap`
      unchanged; `trimmed_union` and `proximity_select` as harness-local functions with
      the determinism rules (sorted iteration, MBID tie-break) stated in their docstrings.
- [ ] **Instrument gate, green half:** `build_variant(production archive, ALG-E,
      mutual_knn, k=50)` must reproduce the `GR-4` verification build byte-for-byte —
      compare sha256 against the value recorded in
      `2026-07-29-graph-rebuild-track-a-execution-log.md` §7b (cited, not restated here).
- [ ] **Instrument gate, red half:** rerun with `k=49` and confirm the sha256 *changes*.
      A green identity from an instrument never shown to go red is not evidence
      (`working-style` memory; the `RC-H3` vacuous-test lesson took three attempts).
- [ ] Commit.

### CB-2: Structural metrics module

**Files:**
- Create: `builder/analysis/2026-07-30-track-b-cap-selection/cb_metrics.py`

**Interfaces — produces:** `score_cell(graph: Graph, fame_frame: dict[str, float]) ->
dict` with: stranding per fame band **with both denominators** (each arm's crawled
population and the adopted frame — the `GRT-P4` first-draft confound, kept visible);
component exclusion as **absolute difference and ratio** (the `GRT-P1` lesson: a ratio
against a zero baseline returns nothing); degree profile (`mean`, `median`, `p99`,
`max`, `top1pct_degree_frac`, `top_degree_node_set` overlap vs production); the five
named tracers (R.E.M., Pixies, The xx, PJ Harvey, Radiohead — the `RC-A2`/`GRT-P2`
artists) with degree and popularity rank per cell; and a descriptive
`check_acceptance`-clause evaluation per cell (would the guard pass? — context for
`GRT-P2`, never a criterion).

- [ ] Implement; fame bands read from the adopted artifact (sha `4cb84ef9…` asserted, the
      `as_run_arms.py` pattern).
- [ ] **Instrument gate:** run against the `GR-4` `ALG-E` build and the `GRT-P4` `ALG-B`
      build and confirm it reproduces the already-published figures for both (stranding
      by band, exclusion rates, tracer degrees — the values in the execution log §7b).
      Two independently produced graphs agreeing with published numbers is this module's
      green-and-red in one step: a bug that moves numbers cannot match both.
- [ ] Commit.

### CB-3: Path-level module (hub transit under the real router)

**Files:**
- Create: `builder/analysis/2026-07-30-track-b-cap-selection/cb_paths.py`

**Interfaces — produces:** `route_sample(artifact_path: Path, pairs: list[tuple[str, str]],
config: ApiConfig) -> dict` — loads the cell's artifact through the API's own
`GraphStore` (`api/src/artistpath_api/graph_store.py:23`) and routes each pair with
`find_path` (`api/src/artistpath_api/pathfinding.py:76`), no server, no network.
Measures per cell: hub-transit rate (share of interior hops through that graph's
`top_degree_node_set`), sub-decile interior presence, path length distribution, and
no-path count. Pair sample: stratified over the adopted frame, fixed seed, **only pairs
whose endpoints exist in every compared cell** (else the read confounds routing with
coverage — the 31% frontier-divergence lesson from `GRT-P4`).

- [ ] Implement. Weights: production `ApiConfig()` defaults, **stated in the output**, per
      the `w_degree_hub` dormancy note above; the prereg decides whether any second
      weight-set runs and pre-commits its read.
- [ ] **Instrument gate:** route 20 pairs on the production artifact and confirm
      determinism (identical paths on a re-run) and at least one pair reproducing a
      known journey (the live-vs-local identity check pattern from the mockup-adoption
      log §15).
- [ ] The prereg (CB-4) must resolve `PLA-R1` applicability explicitly: the bar on
      famous-pair first-path fame as a criterion was derived under `ALG-E` structure,
      where those interiors are forced; whether it binds reads on non-`ALG-E` cells is a
      question for the prereg, answered from `PLA-R1`'s own grounds, not assumed either
      way.
- [ ] Commit.

### CB-4: The pre-registration — **SEAM: commit, then hand off or continue fresh**

**Files:**
- Create: `docs/superpowers/specs/2026-07-30-track-b-cap-selection-preregistration.md`

The document that makes the runs evidence. Committed before any comparative cell runs;
its git timestamp is the part that cannot be reconstructed. It must contain, per
`CLAUDE.md`'s plan rules:

- [ ] The **factor table** — every cell, one column per knob, isolating baseline per row;
      the matched-bound rule for cross-family comparisons; the `uncapped` row marked
      barred from selection (§0 ruling 3).
- [ ] The **held-constant section** carrying the two dormant terms above plus anything
      found while building CB-1..3.
- [ ] **Criteria with effect sizes and plain-language sentences fixed at definition
      time** — every gate and branch trigger with its own effect size. Calibration
      sources: `GRT-P3`'s trial k-curve (the only prior k-sensitivity data) and the
      production-vs-`ALG-B` gap from `GRT-P4`. Note the determinism point explicitly:
      builds are byte-deterministic, so there is no noise floor and every threshold is a
      **materiality** bar, not a significance bar.
- [ ] **Consumes at design time, by ID:** `RC-A2` (rank 50–97 mechanism), `LBS-3` (the
      100 ceiling), `LBS-4` (contribution mechanism, labelled inference), `MKS-5b` (what
      "price the hub cost" must mean here: `top1pct_degree_frac`, max degree, and
      hub-transit rate are the offered proxies, and **no offline coherence proxy exists**
      — the prereg says so plainly), `SYN-6`/§0 ruling 2, `PLA-R1` applicability (CB-3),
      and the re-scoring deferral on `rc_raw_records.json`.
- [ ] **Every read names the run state it presupposes**, one sentence per read; any
      instruction keeping a cell alive gets its own sentence (the Track 2 §1.4 lesson).
- [ ] New identifier series for cells/criteria/gates/reads, namespaced and
      collision-checked (the `CB-` series is this plan's; the prereg picks its own,
      disjoint).
- [ ] Commit. **This is the plan's named seam** — the natural handoff point if the
      session is long: the next session reads the prereg cold, which is the condition it
      was written for.

### CB-5: Run the cells and score them

- [ ] **Dry-run the scorer against the cheapest cell first** (production `ALG-E`
      mutual/k=50 — already built by CB-1's gate) *before* the full sweep, per the Track A
      scorer-defect lesson: the fix cannot be shaped by a result that does not exist yet.
- [ ] Run all cells (`python -u`, log to the analysis dir). Builds are ~78 s at production
      scale (`GRT-P4`), so the full grid is minutes-to-an-hour of compute, not overnight.
- [ ] Write `cb_scores.json` + per-cell manifests; commit raw outputs before any read.

### CB-6: Read, and the report

- [ ] Read every pre-registered criterion in the prereg's own order, nulls included, with
      the run-state sentence checked per read.
- [ ] **Exposure map before any escalation**: one row per criterion × changed knob, per
      `CLAUDE.md`.
- [ ] Report in the four-part shape (measured / inferred-in-plain-language / weakest link
      / options), naming whatever cuts against the headline. The `uncapped` row appears
      in *measured* and never in *options*.
- [ ] Closeout per the skill: execution log retained per task, `NEXT.md` rewrite,
      docs-map rows, `TEST-QUEUE.md` entry (expected N/A — the app is untouched), Snyk
      scan on the new harness code.

## What this plan does not do

No adoption, no re-crawl, no blind listen, no default change, no shipped-code change, no
`acceptance.py` strengthening (a design question of its own, `GRT-P2`), and no
router-side hub remedy work (§0 ruling 2's future track, owner's trigger).

## Self-review record (plan author, 2026-07-30)

Checked per `CLAUDE.md`: every named function/file resolves (`build_from_archive`,
`mutual_knn_cap`, `symmetrise`, `largest_component`, `damped_strength`, `rescale_scores`,
`harvest_identities` in `builder/src/artistpath_builder/`; `GraphStore` at
`graph_store.py:23`; `find_path` at `pathfinding.py:76`; both archives and both reference
builds present in `builder/scratch/`; `rc_raw_records.json` and `as_raw_records.json`
committed). `CB-` collides with nothing under `docs/`. The factor table's third section
carries the two known dormant terms. Six tasks — under the ~8-task handoff threshold,
with the seam named at CB-4 anyway.
