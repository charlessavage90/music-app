# CRE execution-plan critique — probe scripts (2026-08-03)

**Role: COMPLETE, frozen.** The probe scripts behind the `ml-graph-analyst` review of
`docs/superpowers/plans/2026-08-03-cap-reeval-execution-plan.md`, run **before any CRE
stage executed**. The findings themselves were delivered as the review's session output
(not written here, per the reviewing session's output instruction); this directory is the
record of *what was measured and how*, so any figure quoted from that review can be
reproduced.

Read-only by construction: every script opens committed JSONs and existing gitignored
`.bin` artifacts. **No graph was built, no Track B cell was re-run, no repo file outside
this directory was written.**

## Artifacts read (sha256 asserted where a script depends on identity)

| Artifact | sha256 / identity |
|---|---|
| `builder/scratch/graph-t15-tiebreakfix.bin` (adopted) | `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` — asserted in `crp_ruler.py` and `crp_key.py` |
| `builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json` | committed; 93,067 keys |
| `builder/scratch/cb-cells/*.bin` (Track B cells, **pre-drop**) | identity by each cell's committed `.bin.json` manifest; read only |
| `builder/analysis/2026-07-30-track-b-cap-selection/cb_pairs.json` | committed; 22 famous pairs |

**Caveat carried by every cell figure below:** the Track B cells are **pre-drop** builds
(`cb_build_variants.py`'s docstring, diverged 2026-08-02). CRE's cleaned substrates are a
different build. They are used here as the only existing artifacts with union / uncapped
supply, and every conclusion drawn from them is structural, not a substitute for a CRE
cell.

## Scripts

| Script | Output | What it measures |
|---|---|---|
| `crp_ruler.py` | `crp_ruler.json` | The `fi_stats.Frame` ruler over the adopted frame (N asserted = 74,151); the device null price `frame.pctl(0)`; the mapped-percentile quantiles of the whole snapshot; the ramp-toll advantage a null node enjoys over measured artists at r₁/r₂ × k ∈ {1,10,20}; and per-cell snapshot coverage split into **absent key** vs **present-but-null**. |
| `crp_absent.py` | `crp_absent.json` | Whether the union snapshot is exactly (adopted ∪ ALG-B-MK50) node sets — i.e. whether a snapshot-absent node was ever fetched at all; the degree / `pop_raw` profile of the absent nodes on the ALG-E TU cell; and whether `x → fl(x·c)` at `c = GLOBAL_NEUTRAL_FALLBACK = 0.15` preserves strict order in IEEE double (artifact scores and adjacent-double worst case). |
| `crp_key.py` | `crp_key.json` | The `CRE-S2` deletion key: `W4` label coverage; the share of labelled–labelled edges whose rarity-weighted agreement is **exactly 0** (the multiplicative key's tie mass); the node-local neutral median's spread and its fame correlation; the endpoint-multiplier gap on unlabelled edges; and the tag-frame coverage of the ALG-B cells (the frames are built over the **adopted** graph's mbids only). |
| `crp_uc.py` | `crp_uc.json` | Runtime of production-weight `find_journey` per famous pair on MK50 / ALG-E-UC / ALG-B-UC, projected to the 22 × 21 ladder; the `CRE-C6` 1-hop frontier size per cell; and the zero-agreement block size relative to the excess at over-budget nodes of the UC union pool. |
| `crp_kinds.py` | `crp_kinds.json` | d0 stop kinds (`natural` / `forced` / `adjacent_only`) for the 22 famous pairs on nine cells, and how many pairs the mirror's `guard_min_intermediary=True` loses where `find_journey` returns a two-card path. |

Run from `builder/`, e.g.

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-03-cre-plan-critique/crp_ruler.py
```

`crp_key.py` builds `W4` through the committed `tas_frame_split.five_frames()` (~5 s) and
then walks every node's row; it takes a couple of minutes. The others are seconds to a
minute.

## Not maintained

Like `2026-08-03-cre-prereg-critique/`, these are committed **as executed** and frozen:
hardcoded paths, no tests, not collected by any suite (`testpaths` stays `["tests"]`). Do
not edit them; a future measurement starts a new script in a new directory.
