# Track B — cap-rule selection simulation

**AUTHORITATIVE for its own measurements.** Governing plan:
`docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md`. Criteria and reads are
fixed by `CB-4`'s pre-registration, which is committed before any comparative cell runs;
nothing in this directory is a verdict until that document exists.

**Nothing here is adopted, and nothing here changes shipped code.** Both archives are
opened through `ReadOnlyArchive`, whose `put()` raises (`GRT-A1`). Every shipped default
is untouched: `max_neighbours_per_artist = 50`, `cap_strategy = "mutual_knn"`,
`BuilderConfig.algorithm` on `contribution_5`, and every `ApiConfig` weight.

## The three scope rulings this directory is built around

Owner, 2026-07-30 — recorded in full in the plan's §0, summarised here because they
decide what the code does:

1. **Cap-RULE selection, not k-tuning.** `mutual_knn` is one candidate family among
   three, not the incumbent being tuned. Grounds: `SYN-6`, `CS-P0f`, `BTF-4`.
2. **The degree bound is a scoping constraint of this track, not a settled product
   conclusion.** Every *candidate* here must demonstrate its bound — an unbounded
   candidate re-imports the one risk with ear-evidence against it and no offline price.
   But **re-evaluating bounded-degree itself (e.g. router-priced unbounded graphs) is an
   open future track**, owner's trigger, owing its own blind listen. No summary of this
   work may cite `MKS-5b`/`SYN-6` as having closed it.
3. **`uncapped` is a descriptive REFERENCE ROW, barred from selection** — same metrics,
   zero candidacy, so a future re-evaluation starts from measured baselines.

## Files

| File | What it is |
|---|---|
| `cb_build_variants.py` | `CB-1`. Builds one graph per (archive, rule, params) cell. Mirrors `build_from_archive` stage for stage with an injectable cap step, importing every stage function rather than copying it. Carries the four cap rules and the instrument gate. |
| `cb_metrics.py` | `CB-2`. Structural metrics for one built cell: stranding by fame band with **both** denominators, component exclusion as **absolute and ratio**, degree/hub profile, the six tracer artists, and a descriptive `check_acceptance` evaluation. |
| `cb_paths.py` | `CB-3`. Path-level metrics — loads a cell through the API's own `GraphStore` and routes with the API's own `find_path`. Hub transit, sub-decile interiors, length distribution. |
| `cb_gate.json`, `cb_metrics_gate.json`, `cb_paths_gate.json` | Instrument-gate outputs, committed. |

## What is imported rather than reimplemented

From `artistpath_builder`: `damped_strength`, `rescale_scores`, `harvest_identities`,
`is_special_purpose`, `mutual_knn_cap`, `symmetrise`, `largest_component`, `build_graph`,
`serialise`, `deserialise`, `check_acceptance`, `PRODUCTION_ACCEPTANCE`. From
`artistpath_api`: `GraphStore`, `find_path`, `ApiConfig`.

**Only the stage ORDER is restated**, in `cb_build_variants._assemble`, because
`build_from_archive` has no seam to inject a different cap step into. That restatement is
the module's one real risk, which is exactly what the byte-identity gate exists to
retire.

## Instrument gates — each has a green half AND a red half

A green result from an instrument never shown to go red is not evidence. All three gates
ran before any comparative cell.

- **`CB-1` green:** `mutual_knn(k=50)` on each archive reproduces that archive's published
  reference build **byte for byte** — sha256, node count and edge count — against
  `GR-4` (`ALG-E`) and the `GRT-P4` overnight build (`ALG-B`). This is what proves
  `_assemble` is a faithful mirror rather than a plausible one.
- **`CB-1` red:** the same rule at `k=49` must produce a *different* sha256.
- **`CB-2` green+red in one step:** the scorer must reproduce the already-published
  `GRT-P4` figures for **both** reference builds. A scorer bug that moves a number cannot
  match two independently produced graphs at once.
- **`CB-3` green:** routing is deterministic across runs, and every emitted path is a
  valid walk in that graph's own CSR.
- **`CB-3` red:** at `w_sim = 0` the paths must **move**. A router harness that returns
  the same answer under any weights is wired to nothing.

## What this directory cannot conclude

- **Nothing about listening quality.** There is **no validated offline proxy for
  coherence** in this project. Hub-transit rate is a structural proxy for the mechanism
  the blind listen condemned; it is not a substitute for the ear, and `REQ-38`'s blind
  listen is owed before any adoption regardless of what these figures say.
- **Nothing about `ALG-B` adoption.** That is the owner's, parked, and a different
  decision from the cap rule.
- **Nothing cross-archive in one column.** `ALG-E` and `ALG-B` differ in crawl coverage
  by 31% (`GRT-P4`), so cross-archive comparisons carry both denominators and
  path samples are restricted to pairs routable in every compared cell.
- **Nothing about `acceptance.py`.** `GRT-P2` established the guard is blind to a severe
  collapse; the descriptive column here is context, never a criterion, and strengthening
  the guard is a design question of its own that this track does not open.

## Weights, and the one term that is not a constant

Every path-level output states the weight set it ran under. `ApiConfig.w_degree_hub`
defaults to `0.0` **for a reason a cap change removes**: it was tuned to no-op against
the *current capped* graph's top-degree set (largely insular micro-genre artists, §2.6).
A looser cap moves famous artists into that set, so the default cannot be treated as
neutral across cells. `CB-4` decides whether a second weight set runs and pre-commits its
read.
