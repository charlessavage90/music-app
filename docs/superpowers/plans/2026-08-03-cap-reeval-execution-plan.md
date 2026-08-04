# Cap re-evaluation (`CRE-`) execution plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Role: ACTIVE — the operational plan for executing the frozen `CRE-` pre-registration.**
The governing *experimental* document is
[`../specs/2026-08-03-cap-reevaluation-preregistration.md`](../specs/2026-08-03-cap-reevaluation-preregistration.md)
(frozen `3d7b7d6`, amended once by `CRE-AM1`, `eec67a8`), which **wins wherever this plan
disagrees with it.** This plan adds no criterion, moves no bar, and decides only
operational matters the prereg left to the executor — plus the small number of
device-level pins that §"Decisions this plan fixes" records explicitly, each with its
reason and its committed precedent.

**Goal:** Run the `CRE-` experiment end to end — Stage 0 reads, cleaned-substrate and
variant builds, structural screens, instrument gates, and the depth sweeps on both data
sets — leaving one committed JSON per cell and a criteria file, so a fresh session can
write the Stage-3 findings note from the committed record alone.

**Architecture:** All harness-side, no shipped code (prereg §2). A new analysis directory
imports the frozen instruments (`mirror.py`'s cost function as a marked copy with one
added fame-currency device term; `fi_stats.Frame` as the ruler; `cb_build_variants`'s cap
rules; `wav_read`'s vote machinery) and gates every copy against the committed original
before any figure is read.

**Tech Stack:** Python 3.12, numpy, `uv`; the builder venv (run from `builder/`), with
`api/src` on `sys.path` for `GraphStore`/`find_journey` (the `run_arms_t3.py` pattern).

**Task identifiers are `CRE-T1`…`CRE-T11`** — verified unused across the repo
(2026-08-03). They are tasks, not criteria (`CRE-C`), gates (`CRE-G`), reads (`CRE-D`,
`CRE-R`), or arm axes (`CRE-S`, `CRE-P`). Forward-only; nothing committed is renamed.

**New directory:** `builder/analysis/2026-08-03-cap-reevaluation/` (below: `analysis/…`).
Frozen directories are **never edited** — everything is imported or copied with a gate.

---

## Verification record (2026-08-03, before this plan was written)

Every function, file, config value and commit the prereg names was checked against the
repo by the authoring session. All resolve: the four drop lists under
`builder/src/artistpath_builder/data/`, `fi_union_snapshot.json` + manifest sidecar
(sha `d9d6d5d3…`), `fi_validation.json` (`frame_n_nonnull` 74,151 and the
`percentile_definition` string), `cb_pairs.json` (triples `[class, mbid_a, mbid_b]`;
famous classes `ff-top01pct` 10 + `ff-top1pct` 12 = 22), `api/src/artistpath_api/config.py:44-48`
and `:54`, `cb_build_variants.py::cap_trimmed_union`, `mirror.py::w_known_ramp_pctl`,
`graph.py::_log_scaled`, `wav_read.py`'s `e_rel` machinery, `fi_stats.Frame`,
`tas_guard.permuted_labels_among_labelled`, `pathfinding.py::find_journey`, and commits
`3d7b7d6` / `c047d06` / `eec67a8` on `main`.

Two facts found during verification that shape this plan:

1. **`cb_build_variants._assemble` is deliberately frozen PRE-drop** (its own docstring:
   "A post-drop comparison needs a NEW harness, not an edit to this one"). The cleaned
   substrates therefore need a new assembly mirror — and the live pipeline's defaults
   *are* the cleaned mutual-kNN k=50 cell, so the mirror is gated byte-identically
   against a direct `build_from_archive` run (Task `CRE-T5`).
2. **`tas_common.fame_frame` / `cb_metrics.fame_frame` are the RETIRED currency**
   (pop-percentile / worldly-fame era). No CRE module may consume either; the ruler is
   `fi_stats.Frame` over the adopted frame + union snapshot, exactly per prereg §0.3.

---

## Global Constraints

Copied from the pre-registration; every task's requirements implicitly include this
section. Values are cited to their owning file, never re-derived.

- **The prereg governs.** Frozen at `3d7b7d6`; changes from here are §8 amendments only,
  appended never edited, with post-result disclosure if any result exists.
- **Stage order is fixed (§4): `CRE-D3` and `CRE-D1` run before any build; screens
  before any sweep.** The expected `CRE-D1` branch is "not supported" (§9 disclosure) —
  the run is confirmatory, not exploratory.
- **Currency:** `fame_lb_pctl` per the §0.3 ruler row — adopted-artifact non-null
  `fame_lb_raw` frame (**N = 74,151**, asserted before any cell is scored: `CRE-G1c`),
  union snapshot supplying raw values, mapped percentiles out-of-frame, above-max takes
  the max percentile. Quantisation floor **0.015**; |Δ| < 0.015 is "no measured
  movement". Every aggregate reports all-interiors AND matched-only with per-depth null
  counts and the null-share trend. No worldly-fame sentence anywhere.
- **Ramp bracket r₁ = 0.01, r₂ = 0.03** (§3.3, revised at review). The instrument-only
  extreme for `CRE-G2`(a) is **r = 1.0, never a candidate**. Do not "strengthen" arms
  back toward the drafted 0.05/0.15 — those sit in the measured dominating regime.
- **Closed-cell rule:** `CRE-P1` never runs as a candidate on (`ALG-E` × incumbent
  supply). The one carve-out is `CRE-D3`, instrument prior only, barred from candidacy
  and every `CRE-R` winner clause.
- **Cleanup constant:** both drop flags on in every cell (`drop_no_release_tail`,
  `drop_featured_credit` — both default `True` in `BuilderConfig`; assert, don't set).
- **No shipped code changes.** `ApiConfig` and `BuilderConfig` defaults untouched;
  the frozen `mirror.py`'s device knobs stay 0.0; variant graphs are harness-built.
- **Track B's committed cells are never re-run.** Committed figures are consumed by
  citation only where the cell shape matches — the cleaned-substrate cells here do
  **not** match Track B's pre-drop cells, so `CRE-C3`/`CRE-C6` are measured fresh.
- **Every archive open goes through `ReadOnlyArchive`** (`GRT-A1`, standing).
- **Frozen analysis files are never edited** — `mirror.py`, `run_arms.py`, `wgt_grid.py`,
  `wav_read.py`, `cb_build_variants.py`, `cb_metrics.py`, `fi_stats.py`, everything under
  the critique directory. Import them, or copy with a gate. A new measurement starts a
  new script.
- **`W6` is not the frame and must not become it. The λ-Jaccard blend
  (`tas_select.mask_tag`) is closed and is not the `S2` device.**
- **Retired-currency bar:** no CRE module reads `tas_common.fame_frame` or
  `cb_metrics.fame_frame`.
- **Artifact identity by sha256 in every committed output** (manifest sidecars for
  builds; `artifact_sha256` in every sweep JSON).
- **Environment:** `UV_LINK_MODE=copy` on every `uv` command; `PYTHONIOENCODING=utf-8`
  on anything printing artist names; `python -u` on every long run; never pipe a long
  unattended run through `tail`. `np.load` on an `.npz` is lazy — not used here, but the
  rule stands for any capture work.
- **Snyk:** any new CLI `--out`/path argument uses the `in_dir()` bare-filename pattern
  (`run_arms_t3.py:57`), which closes the traversal finding class; scan at closeout per
  the standing instruction.
- **Git:** branch `cap-reeval-run` off `main`, pushed at the first commit; draft PR
  early; all commits use a pathspec (`git commit -- <paths>`), never `-A`, never
  `--amend`. **Append to the retained execution log per task**, not only at closeout.
- **Seams (prereg §4):** Seam 1 after Stage 0+1 (Tasks T1–T7); Seam 2 between the two
  data sets' sweeps (after T9); Seam 3 before Stage 3 (after T11). A session may retire
  at any seam; the committed JSONs are the handoff.
- **No `CRE-R` read is licensed by this plan.** T11 produces figures and the run-state
  map; the Stage-3 findings note is the next session's work, written cold from the
  committed record (prereg §6's run-state rule).

---

## Decisions this plan fixes (executor's column, pinned before any run)

The prereg deliberately left these at the device level. Each is fixed here, pre-run,
with its precedent — they are operational pins, not new criteria.

1. **The `S2` deletion key** (§3.2 "LB similarity re-weighted by … agreement", `CRE-AM1`
   form). At an over-budget node `u`, edges are deleted ascending by the tuple
   **`(strength(u,v) × a_eff(u,v), strength(u,v), _desc(v))`** where `strength` is
   `cap_trimmed_union`'s symmetric unclipped pair strength, `a(u,v)` is the
   `evidence_rel` rarity-weighted `W4` agreement (`wav_read`'s exact measure), and
   `a_eff` = `a(u,v)` where both endpoints carry `W4` labels, else **the median of
   `u`'s measured `a` values (≥ 2 of them, else `GLOBAL_NEUTRAL_FALLBACK`)**. *Why the
   neutral-median:* it is the committed missing-label rule (`frame_pass` /
   `tas_select`), and it realises §3.2's sentence exactly — unlabelled-endpoint edges
   rank by LB similarity alone among themselves, at a neutral level in the same pool,
   and tags never veto by absence. *Why the middle tuple element (analyst M4):*
   agreement is exactly 0 on 3.85 % of the adopted graph's measured edges, and a bare
   product key collapses that whole block onto the MBID tie-break — similarity playing
   no part, which strains §3.2's "tags only re-order" constraint. The `strength`
   element restores LB-similarity order inside the zero block and inside any product
   tie, and it makes the degeneracy gate's byte-identity **exact by construction**
   rather than empirically true (a constant multiplier is only monotone
   *non-decreasing* in IEEE doubles — distinct strengths can collapse to equal
   products; measured at 0 collapses on today's 1,445 distinct edge scores, but the
   gate must not rest on that).
2. **Device pricing of ruler-null nodes — two classes, priced separately (analyst
   M2).** The union snapshot's key set is exactly (adopted node set) ∪ (`ALG-B`-MK50
   node set), so a node a union/uncapped cell keeps that the snapshot lacks was
   **never in the fetch population** — a population artifact, not a listener count.
   Accordingly: a **present-but-null** node (fetched; LB recorded no listeners) is
   priced at `frame.pctl(0)` ≈ 6.7e-6 — below the measurement floor, which for that
   class genuinely is maximal obscurity under the novelty-likelihood construct; an
   **absent-from-snapshot** node is priced at **0.5**, the no-information neutral
   prior (the committed neutral-rule shape), so the device neither seeks nor avoids
   artists whose obscurity is simply unknown. The analyst measured the *value* choice
   within the null class as operationally inert (alternatives differ by < 0.25 % of
   one hop), but the *class* choice as worth 1–2.5 whole hops against measured
   p5–p10 artists at r₂ and depth — pricing never-fetched nodes as maximally obscure
   would steer the device into exactly the class its own score cannot read. This is a
   **device** input only — scoring never treats either class as a value (`FAM-AM1.8`)
   — and every sweep JSON reports `interiors_null_in_snapshot` and
   `interiors_absent_from_snapshot` **separately, per depth**, with §0.4's d0→d20
   trend reported for both.
3. **The victim rule's tie order, implemented:** victims sort by measured
   `fame_lb_pctl` descending with ruler-null interiors after every measured one, ties
   by `pop_raw` descending then lowest MBID — the §0.3 sentence, made a total order.
   **Named consequence (analyst M5):** under this order a ruler-null interior is never
   bypassed while any measured interior exists, so the victim rule itself pushes the
   null share of interiors upward with depth, independent of any descent — §0.4's
   "descent partly unmeasurable" trigger can fire mechanically. The mirror pin (nulls
   first) would instead purge unmeasurable artists immediately and never deliver them
   at depth; neither is neutral, this one is chosen, and to keep the mechanical
   component separable every sweep JSON also reports, per depth, the count of
   null interiors present-and-unbypassable (`null_interior_unbypassable`).
4. **`CRE-C1`'s two reporting populations, implemented:** *all-interiors* = medians over
   every measured interior value in the band (nulls are holes, counted per depth);
   *matched-only* = the same statistic over the pairs whose d0 **and** d10–20 interiors
   contain no ruler-null. The findings note must state this definition beside the figure.
5. **`CRE-D1`'s `n_artists` for the idf table** = the adopted artifact's node count, and
   the aggregation follows `cre_probe3b.py` (the origin of §4's wording). The
   implementer reads that probe before implementing; **where the probe and the prereg's
   words disagree, the words govern and the divergence is recorded in the run log.**
6. **`CRE-C2`'s primary reference set, made deterministic:** the adopted artifact's top
   1% by degree, ranked `(degree desc, mbid asc)`, top ⌈N × 0.01⌉ nodes, membership
   applied by MBID in every cell. Own-graph share computed the same way and reported
   beside it, never gated on.
7. **Bootstrap procedure** for `CRE-C1`(ii), `CRE-C5` and `CRE-R4`(ii): pair-level
   resampling with replacement, B = 10,000, seed `20260803`, percentile method. Fixed
   here so no result can pick a procedure.
8. **The guard is realised by `journey()`, and the mirror's flag stays off (analyst
   M7).** §0.3 holds `guard_min_intermediary` constant *as a mechanism*; the ladder's
   `journey()` performs the same masked re-run the guard performs, **plus** the
   `adjacent_only` fallback the guard lacks — with the mirror's flag also on, a
   two-node path whose detour does not exist would return `None` instead of the
   two-card journey, and the uniform-drop rule would then delete that pair from every
   compared cell: precisely the vanishing-adjacent-pair failure §0.3's
   journey-semantics row exists to prevent. So `cfg.guard_min_intermediary` is `False`
   in every ladder run, `journey()` asserts it, and the §0.3 row is honoured through
   the journey semantics that subsume it. Measured d0 exposure today: zero pairs
   (`crp_kinds.py`); the at-depth exposure is why the assert exists.
9. **Uniform-drop comparison groups, pinned (analyst M3).** One **canonical group per
   data set** = that data set's non-staged cells plus their named isolating baselines;
   every reported per-arm `CRE-C1` comes from its data set's canonical group. Each
   staged `S3` cell is compared **only in its own two-cell group** against its §0.2
   baseline — a cell barred from candidacy must not delete (pair, depth) cells from
   the candidates' record (the `walk_journey` break-and-pad shape makes one early UC
   termination contagious otherwise, and UC is where d0 adjacency concentrates:
   6 of 22 pairs, all in `ff-top01pct`). Scramble companions are dropped within their
   tag cell's canonical group. All group memberships and all dropped sets are
   committed in `cre_scores.json`, and every reported figure names its group.

---

## File structure

| File (in `analysis/…` = `builder/analysis/2026-08-03-cap-reevaluation/`) | Responsibility |
|---|---|
| `analysis/…/cre_common.py` | Paths, shas, constants, the fame ruler (dependency (1)), pair loading, `in_dir`. |
| `analysis/…/cre_mirror.py` | Marked copy of the frozen `mirror.py` + the fame-currency ramp (dependency (2)) + per-edge term breakdown (dependency (5)). |
| `analysis/…/cre_ladder.py` | Journey-semantics walk (dependency (6)), victim rule, toll-arithmetic assertion. |
| `analysis/…/cre_d3.py` | Stage 0: the pricing prior. Writes `cre_d3.json`. |
| `analysis/…/cre_d1.py` | Stage 0: the owner's banding hypothesis, confirmatory. Writes `cre_d1.json`. |
| `analysis/…/cre_build.py` | Cleaned-substrate assembly mirror + cap seam (green/red gated), all cell builds, manifests with `_log_scaled` low/high. |
| `analysis/…/cre_tags.py` | `W4`/idf/`e_rel` agreement tables, the `S2` deletion key input, label-scramble and vote-scramble tables (dependencies (3)/(4), `CRE-AM1`). |
| `analysis/…/cre_screen.py` | Stage 1: `CRE-G3`, `CRE-C3`, `CRE-C6`, the affine `pop_raw` report. Writes `cre_screen.json`. |
| `analysis/…/cre_gates.py` | Stage 2 entry: `CRE-G1`(a)(c), `CRE-G2`(a). Writes `cre_gates.json`. |
| `analysis/…/cre_sweep.py` | The ladder over one named cell per invocation; `CRE-G1`(b)/`G2`(b) asserted in-run; `CRE-D2` per-term stats. One JSON per cell. |
| `analysis/…/cre_score.py` | `CRE-C1`/`C2`/`C4`/`C5`/`C6`-companion figures + uniform-drop sets + the run-state map. Writes `cre_scores.json`. |
| `analysis/…/test_cre_*.py` | Unit tests per module (properties that must not drift). |
| `docs/superpowers/<start-date>-cre-run-execution-log.md` | The retained execution log, created at T1, dated the day execution starts, appended per task. |

Graph cells land in `builder/scratch/cre-cells/` (gitignored) with `.bin.json` manifest
sidecars; the manifests' shas are quoted in every downstream JSON.

---

### Task `CRE-T1`: Branch, log, and the fame ruler

**Files:**
- Create: `analysis/…/cre_common.py`
- Test: `analysis/…/test_cre_common.py`
- Create: `docs/superpowers/<start-date>-cre-run-execution-log.md`

**Interfaces:**
- Consumes: `fi_stats.Frame` (imported from the frozen fame-instrument directory);
  `fi_union_snapshot.json` (+ manifest sha); `cb_pairs.json`; the adopted artifact.
- Produces: `use_frozen(*names)` (sys.path helper), `ADOPTED`, `ADOPTED_SHA`,
  `load_adopted() -> GraphStore` (sha-asserted), `Ruler` with
  `.pctl_of(mbid) -> float | None`, `.device_pctl_of(mbid) -> float`,
  `.status_of(mbid) -> str` (`"measured"` / `"null"` / `"absent"` — pin 2's two
  unmeasured classes, kept separable end to end),
  `.arrays(store) -> tuple[np.ndarray, np.ndarray]` (measured-with-nan, device),
  `.frame_n`, `famous_pairs() -> list[tuple[str, str, str]]` (22 `(class, a, b)`
  triples), constants `RAMPS = {"P1a": 0.01, "P1b": 0.03}`, `EXTREME_RAMP = 1.0`,
  `MAX_DEPTH = 20`, `C1_BAND = range(10, 21)`, `QUANT_FLOOR = 0.015`,
  `MATERIAL = 0.05`, `BOOTSTRAP_B = 10_000`, `BOOTSTRAP_SEED = 20260803`, `in_dir`.

- [ ] **Step 1: Branch and log**

```bash
git checkout -b cap-reeval-run main && git push -u origin cap-reeval-run
```

Create the retained execution log (dated the day this runs) with a role header naming
the prereg as governing and this plan as operational, and a §1 recording T1's start.

- [ ] **Step 2: Append `CRE-AM2` to the prereg's §8 and commit it before anything else runs**

The analyst review (M6) found a contradiction the plan must not mechanise through:
§0.2 names **E-S0-P0's** isolating baseline as "—" and **B-S0-P0's** as **E-S0-P0**,
while `CRE-C4`'s binding form divides by the isolating baseline's `C4` — undefined for
the first, and a **cross-data-set ratio §0.4 bars** for the second. The fix changes how
a frozen criterion is computed for two cells, so it is a §8 amendment, written now,
**before any stage has run and before any result exists** (the `TAS-AM5` timing
pattern — the git timestamp is the evidence). Append verbatim:

```markdown
### `CRE-AM2` — `C4`'s binding form is undefined at the two anchors; appended before any stage ran

**No `CRE` stage has run and no result exists at this commit** — this resolves a
mechanisation contradiction found in pre-run review of the execution plan (analyst
critique M6, `builder/analysis/2026-08-03-cre-plan-critique/`), and moves no bar.

§5's `CRE-C4` binding form — arm `C4` ÷ its isolating baseline's `C4` ≥ 0.70 — cannot
be computed for **E-S0-P0** (its §0.2 baseline is "—") and must not be computed for
**B-S0-P0** (its §0.2 baseline is E-S0-P0, a different data set; §0.4 bars the ratio,
and §9's rationale for the relative form — "self-normalises on each substrate" —
presupposes a within-substrate denominator).

**Resolution: the two anchor cells (E-S0-P0, B-S0-P0) carry no binding `C4`.** Their
`C4` is reported **absolute** against the 0.75 reference line, marked "no binding
form (anchor)". Every other cell's binding `C4` uses its §0.2 isolating baseline,
which is within-data-set everywhere else. B-S0-P0's §0.2 baseline row is untouched
for its own purpose — the data-set-isolated comparison under §0.4's rules; only its
role in `C4`'s binding denominator is removed. No other criterion, bar, cell or read
changes.
```

```bash
git commit -m "CRE-AM2: C4's binding form is undefined at the two anchors; appended before any stage ran" -- docs/superpowers/specs/2026-08-03-cap-reevaluation-preregistration.md
```

**Do not proceed until this commit exists.**

- [ ] **Step 3: Write the failing tests**

```python
# test_cre_common.py
"""The ruler and pair set -- the properties that must not drift."""
from __future__ import annotations

import numpy as np
import pytest

from cre_common import FRAME_N, Ruler, famous_pairs


def test_frame_n_is_the_prereg_frame(ruler):
    # CRE-G1c. 74,151 is the adopted artifact's non-null fame_lb_raw count
    # (fi_validation.json frame_n_nonnull) -- NOT the artifact's 74,193 nodes
    # and NOT the snapshot's 93,067 keys.
    assert ruler.frame_n == FRAME_N == 74_151


def test_midrank_formula_on_a_toy_frame():
    # pctl(v) = (|{f<v}| + (|{f=v}|+1)/2) / N over [1,1,2,5]:
    #   pctl(1) = (0 + 1.5)/4, pctl(2) = (2 + 1)/4, pctl(5) = (3 + 1)/4
    from fi_stats import Frame
    f = Frame(np.array([1, 1, 2, 5], dtype=np.int64))
    got = f.pctl(np.array([1, 2, 5, 3, 999]))
    assert got[0] == pytest.approx(1.5 / 4)
    assert got[1] == pytest.approx(3.0 / 4)
    assert got[2] == pytest.approx(4.0 / 4)
    # absent value 3: (|{f<3}| + 0.5)/4
    assert got[3] == pytest.approx(3.5 / 4)
    # FAM-AM1.6: above the frame maximum takes the maximum's percentile.
    assert got[4] == got[2]


def test_null_price_sits_below_every_measured_value(ruler):
    # Plan pin 2, present-but-null class: priced at frame.pctl(0). Asserted
    # against the frame minimum DIRECTLY (analyst m10: a loose absolute bound
    # let the name claim more than the assertion checked).
    assert ruler.device_null_pctl < ruler.min_measured_pctl


def test_absent_class_is_priced_at_the_neutral_prior(ruler):
    # Plan pin 2, absent-from-snapshot class: never fetched, obscurity unknown,
    # priced at 0.5 so the device neither seeks nor avoids it.
    assert ruler.device_absent_pctl == 0.5
    assert ruler.status_of("00000000-0000-0000-0000-000000000000") == "absent"


def test_famous_pairs_are_the_22_committed_ones():
    pairs = famous_pairs()
    assert len(pairs) == 22
    assert {p[0] for p in pairs} == {"ff-top01pct", "ff-top1pct"}
    assert all(a != b for _, a, b in pairs)
```

(`ruler` is a module-scoped fixture constructing `Ruler()` once — it loads the snapshot
and the adopted artifact, several seconds.)

- [ ] **Step 4: Run tests to verify they fail**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-08-03-cap-reevaluation/test_cre_common.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'cre_common'`

- [ ] **Step 5: Implement `cre_common.py`**

Module docstring states: governing document, the ruler row restated by citation, the
retired-currency bar, and plan pin 2 (null device pricing) with its reason. Core:

```python
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

_FROZEN = {
    "track2_sweep": ROOT / "builder/analysis/2026-07-23-track2-sweep",
    "track_b": ROOT / "builder/analysis/2026-07-30-track-b-cap-selection",
    "tag_disc": ROOT / "builder/analysis/2026-07-30-tag-discrimination",
    "rel": ROOT / "builder/analysis/2026-07-31-release-tag-coverage",
    "wgt": ROOT / "builder/analysis/2026-08-01-label-weighting",
    "fame": ROOT / "builder/analysis/2026-08-02-fame-instrument",
    "wav": ROOT / "builder/analysis/2026-08-03-within-artist-votes",
    "api_src": ROOT / "api/src",
}


def use_frozen(*names: str) -> None:
    for n in names:
        p = str(_FROZEN[n])
        if p not in sys.path:
            sys.path.insert(0, p)


ADOPTED = ROOT / "builder/scratch/graph-t15-tiebreakfix.bin"
# Source: the tiebreak-fix-adoption findings' checksum, as pinned by
# run_arms_t3.py and fi_union_snapshot.manifest.json. Asserted, never trusted.
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

SNAPSHOT = _FROZEN["fame"] / "fi_union_snapshot.json"
SNAPSHOT_MANIFEST = _FROZEN["fame"] / "fi_union_snapshot.manifest.json"
PAIRS = _FROZEN["track_b"] / "cb_pairs.json"
FAMOUS_CLASSES = ("ff-top01pct", "ff-top1pct")

FRAME_N = 74_151                    # CRE-G1c
RAMPS = {"P1a": 0.01, "P1b": 0.03}  # prereg §3.3
EXTREME_RAMP = 1.0                  # CRE-G2(a), instrument-only
MAX_DEPTH = 20
C1_BAND = range(10, 21)
QUANT_FLOOR = 0.015
MATERIAL = 0.05
BOOTSTRAP_B = 10_000
BOOTSTRAP_SEED = 20260803


def in_dir(arg: str) -> Path:
    """run_arms_t3.py's bare-filename rule; closes the Snyk traversal class."""
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename in {HERE}, got {arg!r}")
    return HERE / arg


def load_adopted():
    use_frozen("api_src")
    from artistpath_api.graph_store import GraphStore

    payload = ADOPTED.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != ADOPTED_SHA:
        raise SystemExit(f"WRONG ARTIFACT: expected {ADOPTED_SHA}, got {got}")
    return GraphStore.from_bytes(payload)


class Ruler:
    """The §0.3 ruler row, and nothing else."""

    def __init__(self) -> None:
        use_frozen("fame", "track_b")
        from fi_stats import Frame  # the committed FAM-AM1.6 implementation

        manifest = json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))
        digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
        if digest != manifest["sha256"]:
            raise SystemExit("fi_union_snapshot.json does not match its manifest")
        raw = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

        store = load_adopted()
        vals = np.array(
            [raw[m] for m in sorted(store.mbids) if raw.get(m) is not None],
            dtype=np.int64,
        )
        self._frame = Frame(vals)
        self.frame_n = self._frame.n
        if self.frame_n != FRAME_N:
            raise SystemExit(
                f"CRE-G1c FAILED: ruler frame N {self.frame_n} != {FRAME_N}"
            )
        # Pin 2's two unmeasured classes, priced separately. A key PRESENT with
        # value null was fetched and LB recorded no listeners: below the
        # measurement floor, frame.pctl(0). A key ABSENT was never in the fetch
        # population (the snapshot is exactly adopted UNION ALG-B-MK50 -- a
        # population artifact, not a listener count): neutral prior 0.5.
        self.device_null_pctl = float(self._frame.pctl(np.array([0]))[0])
        self.device_absent_pctl = 0.5
        self._null_keys = {m for m, v in raw.items() if v is None}

        keys = [m for m in raw if raw[m] is not None]
        pctls = self._frame.pctl(np.array([raw[m] for m in keys], dtype=np.int64))
        self._pctl = dict(zip(keys, (float(p) for p in pctls)))
        self.min_measured_pctl = float(min(self._pctl.values()))

    def pctl_of(self, mbid: str) -> float | None:
        return self._pctl.get(mbid)

    def status_of(self, mbid: str) -> str:
        if mbid in self._pctl:
            return "measured"
        return "null" if mbid in self._null_keys else "absent"

    def device_pctl_of(self, mbid: str) -> float:
        p = self._pctl.get(mbid)
        if p is not None:
            return p
        return (self.device_null_pctl if mbid in self._null_keys
                else self.device_absent_pctl)

    def arrays(self, store) -> tuple[np.ndarray, np.ndarray]:
        """(measured-with-nan, device) fame arrays aligned to node ids."""
        measured = np.full(len(store.mbids), np.nan)
        device = np.empty(len(store.mbids))
        for i, m in enumerate(store.mbids):
            p = self._pctl.get(m)
            if p is not None:
                measured[i] = p
            device[i] = self.device_pctl_of(m)
        return measured, device


def famous_pairs() -> list[tuple[str, str, str]]:
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    pairs = [tuple(t) for t in doc["triples"] if t[0] in FAMOUS_CLASSES]
    if len(pairs) != 22:
        raise SystemExit(f"expected 22 famous pairs, got {len(pairs)}")
    return pairs
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-08-03-cap-reevaluation/test_cre_common.py -v`
Expected: PASS (5 tests). The frame-N test passing **is** `CRE-G1c`'s machinery working.

- [ ] **Step 7: Append to the run log; commit**

```bash
git commit -m "CRE-T1: the fame ruler and shared constants, frame N asserted" -- builder/analysis/2026-08-03-cap-reevaluation/ docs/superpowers/
```

---

### Task `CRE-T2`: The mirror copy with the fame-currency device, and the journey ladder

**Files:**
- Create: `analysis/…/cre_mirror.py` (marked copy of `builder/analysis/2026-07-23-track2-sweep/mirror.py`)
- Create: `analysis/…/cre_ladder.py`
- Test: `analysis/…/test_cre_mirror.py`, `analysis/…/test_cre_ladder.py`

**Interfaces:**
- Consumes: `cre_common.{use_frozen, MAX_DEPTH}`; `artistpath_api.pathfinding.{DISLIKE, KNOWN, Exclusion}`.
- Produces: `cre_mirror.SweepConfig` (frozen file's fields **plus**
  `w_known_ramp_fame_pctl: float = 0.0`), `cre_mirror.MirrorContext.build(store, fame_device)`
  (gains a `fame_pctl` array), `cre_mirror.find_path_mirror(...)` (same signature),
  `cre_mirror.term_breakdown(store, ctx, cfg, excludes, path) -> list[dict]` (per-edge
  term contributions — dependency (5)); `cre_ladder.journey(store, s, t, excludes, cfg,
  ctx, stats) -> tuple[list[int] | None, str]` (kinds `natural`/`forced`/`adjacent_only`/`none`),
  `cre_ladder.walk_journey(store, s, t, cfg, ctx, fame_measured, pop, mbids, stats)
  -> list[tuple[list[int] | None, str]]` (length `MAX_DEPTH + 1`),
  `cre_ladder.victim_key(fame_measured, pop, mbids)`,
  `cre_ladder.assert_cost_decomposition(store, ctx, cfg, excludes, path, masked_edge=None)`.

- [ ] **Step 1: Copy the frozen mirror verbatim, then apply exactly five deltas**

Copy `builder/analysis/2026-07-23-track2-sweep/mirror.py` → `cre_mirror.py` unchanged,
then:

1. **Docstring**: replace with one stating this is the `CRE-` marked copy, the frozen
   original is untouched and still owns every Track 2/2F/3/3b reproduction, and the
   single functional addition is the fame-currency ramp (prereg §2 dependency (2));
   `CRE-G1`(a) is what proves `production()` behaviour survived the copy.
2. **`SweepConfig`** gains one field, immediately after `w_known_thresh_pctl`:

```python
    # CRE- (prereg §3.3): the SAME shape as w_known_ramp_pctl above, in the
    # ADOPTED currency -- fame_lb_pctl, not pop-percentile. Currency is in the
    # name. 0.0 = off; at k = 0 the term is exactly zero AND not added at all,
    # so CRE-G1(b) holds by construction. Ruler-null nodes are priced at
    # frame.pctl(0) (plan pin 2; disclosed per sweep JSON).
    w_known_ramp_fame_pctl: float = 0.0
```

3. **`MirrorContext`** gains a `fame_pctl: np.ndarray` field, and `build` gains a
   required `fame_device: np.ndarray` parameter storing it (the device array from
   `Ruler.arrays`).
4. **`_dijkstra`**: alongside the existing ramp/thresh constants add
   `ramp_fame = cfg.w_known_ramp_fame_pctl * n_known; ramp_fame_on = ramp_fame != 0.0`,
   and immediately after the `thresh_on` block in the edge loop:

```python
            # CRE-: fame-currency ramp. Same rules as the two terms above:
            # relaxation target only (DD-D7), target endpoint exempt, added
            # only when live -- never as `+ 0.0`.
            if ramp_fame_on and v != target:
                cost += ramp_fame * float(ctx.fame_pctl[v])
```

5. **`_dijkstra` records the search's own accumulated cost** — immediately before the
   `if target not in prev` return block:

```python
    # CRE-G2(b)'s independent reference: the cost the SEARCH accumulated, so a
    # post-hoc decomposition is checked against the instrument rather than
    # against its own formula (analyst B1 -- the first draft compared a closed
    # form to itself and could not fail).
    if stats is not None:
        stats["path_cost"] = dist.get(target)
```

Then add `term_breakdown` at module bottom (new code, dependency (5)):

```python
def term_breakdown(store, ctx, cfg, excludes, path) -> list[dict]:
    """Per-edge cost decomposition along a RETURNED path (CRE-D2).

    Recomputed post-hoc from the same expressions _dijkstra uses, so a term's
    share is exact, not sampled. The mirror's stats counters are search-wide
    tallies; this is per chosen edge, which is what §0.3's w_floor attribution
    rule needs.

    THE FIVE TERMS CARRIED ARE EXHAUSTIVE ONLY UNDER THE ENTRY ASSERTIONS
    BELOW (analyst m14). assert_cost_decomposition compares this breakdown's
    total against the search's own accumulated cost, so any live term omitted
    here would fire that check spuriously -- the assertions make the omission
    impossible rather than argued.
    """
    assert all(e.reason == KNOWN for e in excludes), "ladder is all-known"
    assert cfg.toll_s is None and cfg.toll_hops is None
    assert cfg.w_known_thresh_pctl == 0.0 and cfg.w_known_ramp_pctl == 0.0
    assert cfg.w_degree_hub == 0.0, "held at 0.0 in every cell (prereg s0.3)"
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    base = min(float(store.pop_raw[path[0]]), float(store.pop_raw[path[-1]]))
    floor_val = _relaxed_floor(base, excludes, cfg.floor_relax_known,
                               cfg.floor_relax_dislike)
    ramp_fame = cfg.w_known_ramp_fame_pctl * n_known
    out = []
    for u, v in zip(path, path[1:]):
        sim = dict(store.neighbours_of(u))[v]
        pop_u, pop_v = float(store.pop_raw[u]), float(store.pop_raw[v])
        row = {
            "sim": cfg.w_sim * (1.0 - float(sim)),
            "jump_raw": cfg.w_jump * abs(pop_u - pop_v),
            "floor_raw": cfg.w_floor * max(0.0, floor_val - pop_v),
            "hop": cfg.w_hop,
            "ramp_fame": (ramp_fame * float(ctx.fame_pctl[v])
                          if ramp_fame != 0.0 and v != path[-1] else 0.0),
        }
        out.append(row)
    return out
```

(The ladder is all-`known`, so the avoid term is identically zero and deliberately
omitted from the breakdown; `w_degree_hub` is 0.0 in every cell per §0.3 and likewise
omitted. Both facts are stated in the docstring.)

- [ ] **Step 2: Diff the copy against the frozen original**

Run: `git diff --no-index builder/analysis/2026-07-23-track2-sweep/mirror.py builder/analysis/2026-08-03-cap-reevaluation/cre_mirror.py`
Expected: exactly the five deltas plus `term_breakdown`. Anything else is drift — remove it.

- [ ] **Step 3: Write `cre_ladder.py`**

```python
"""The §0.3 ladder: journey semantics, fame-currency victim rule, uniform drop.

JOURNEY SEMANTICS (dependency (6)): the harness mirrors find_journey, the
function the app actually calls -- a directly-adjacent pair yields a
forced-detour interior rather than vanishing from the record. The committed
`walk` helpers mirror find_path and break on empty interiors; that precedent
silently unread exactly the pairs union arms make adjacent (prereg §9).

The mirror cfg runs with guard_min_intermediary=False here BECAUSE journey()
itself performs the guard's masked re-run (the same mechanism), plus the
adjacent_only fallback the guard lacks. CRE-G1(a) proves the combination
reproduces production find_journey exactly.
"""
from __future__ import annotations

from cre_common import MAX_DEPTH, use_frozen
from cre_mirror import _avoidance_map, _dijkstra, find_path_mirror

use_frozen("api_src")
from artistpath_api.pathfinding import DISLIKE, KNOWN, Exclusion  # noqa: E402


def journey(store, s, t, excludes, cfg, ctx, stats=None):
    # Pin 8: journey() IS the guard (same masked re-run) plus the
    # adjacent_only fallback the guard lacks; both live at once would turn
    # adjacent-only pairs into None and cascade through the uniform drop.
    assert cfg.guard_min_intermediary is False
    path = find_path_mirror(store, s, t, excludes, cfg, ctx, stats)
    if path is None:
        return None, "none"
    if len(path) != 2:
        return path, "natural"
    hard = {e.node for e in excludes} - {s, t}
    # Production's own predicate (pathfinding.py), not its complement: this is
    # a byte-identity harness, and the two differ the moment a third exclusion
    # reason exists (analyst m16). Identically empty on the all-known ladder.
    avoid = _avoidance_map(store, [e.node for e in excludes
                                   if e.reason == DISLIKE], cfg)
    detour = _dijkstra(store, s, t, hard, avoid, cfg, ctx, excludes,
                       (s, t), stats)
    return (path, "adjacent_only") if detour is None else (detour, "forced")


def victim_key(fame_measured, pop, mbids):
    """Highest fame_lb_pctl first; ruler-null interiors after every measured
    one; ties by pop_raw desc then lowest MBID (§0.3, plan pin 3)."""
    import math

    def key(v: int):
        f = float(fame_measured[v])
        return ((-f) if not math.isnan(f) else 1.0, -float(pop[v]), mbids[v])

    return key


def walk_journey(store, s, t, cfg, ctx, fame_measured, pop, mbids, stats=None):
    """All-`known` journey ladder, depths 0..MAX_DEPTH. Always MAX_DEPTH+1
    entries; infeasible cells are (None, "none"), never a short list."""
    key = victim_key(fame_measured, pop, mbids)
    excludes: list = []
    out: list[tuple[list[int] | None, str]] = []
    for _ in range(MAX_DEPTH + 1):
        path, kind = journey(store, s, t, excludes, cfg, ctx, stats)
        out.append((path, kind))
        if path is None:
            break
        interior = path[1:-1]
        if not interior:
            break  # adjacent_only: no victim to press
        victim = min(interior, key=key)
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    out.extend([(None, "none")] * (MAX_DEPTH + 1 - len(out)))
    return out


def assert_cost_decomposition(store, ctx, cfg, excludes, path,
                              masked_edge=None, tol=1e-9):
    """CRE-G2(b), the independent form (analyst B1 replaced the first draft,
    which compared the toll formula to itself and could not fail).

    Two clauses, both against references the decomposition does not share:
    (1) the breakdown's TOTAL equals the SEARCH's own accumulated cost for
        this exact path (a fresh deterministic _dijkstra call records
        stats["path_cost"]) -- a wrong k inside the search, a term added or
        omitted inside the search, or a mis-plumbed array all fire here;
    (2) the breakdown's ramp component equals r * k * sum(fame_pctl) over the
        returned interiors -- the prereg's stated formula, now anchored to a
        total that clause (1) has tied to the instrument.
    `masked_edge` replays a forced-detour journey's second search exactly.
    """
    from cre_mirror import term_breakdown

    hard = {e.node for e in excludes} - {path[0], path[-1]}
    avoid = _avoidance_map(store, [e.node for e in excludes
                                   if e.reason == DISLIKE], cfg)
    stats: dict = {"examined": 0, "floor_active": 0}
    replay = _dijkstra(store, path[0], path[-1], hard, avoid, cfg, ctx,
                       excludes, masked_edge, stats)
    if replay != path:
        raise SystemExit("CRE-G2(b) FAILED: replay returned a different path")

    rows = term_breakdown(store, ctx, cfg, excludes, path)
    total = sum(sum(r.values()) for r in rows)
    if abs(total - stats["path_cost"]) > tol:
        raise SystemExit(
            f"CRE-G2(b) FAILED: decomposition {total} != search cost "
            f"{stats['path_cost']}"
        )
    n_known = sum(1 for e in excludes if e.reason == KNOWN)
    expected = (cfg.w_known_ramp_fame_pctl * n_known
                * sum(float(ctx.fame_pctl[v]) for v in path[1:-1]))
    got = sum(r["ramp_fame"] for r in rows)
    if abs(got - expected) > tol:
        raise SystemExit(
            f"CRE-G2(b) FAILED: ramp component {got} != r*k*sum(fame) {expected}"
        )
```

- [ ] **Step 4: Write the failing tests, then run them**

`test_cre_mirror.py` and `test_cre_ladder.py`, on a synthetic 4-node store (the
`FakeStore` pattern from `test_tas_route.py` — line graph 0–1–2 with detour 0–3–2,
`pop_raw` and a fame array set per test):

```python
# test_cre_ladder.py -- the properties that must not drift
from __future__ import annotations

import numpy as np
import pytest

from cre_ladder import journey, victim_key, walk_journey
from cre_mirror import MirrorContext, SweepConfig


class FakeStore:
    """0 -- 1 -- 2 line, detour 0 -- 3 -- 2; CSR-ish surface for the mirror."""

    def __init__(self, sims=None):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.9, 0.5, 0.9, 0.4], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        s = sims or {}
        self._adj = {
            0: [(1, s.get((0, 1), 0.9)), (3, s.get((0, 3), 0.8))],
            1: [(0, s.get((0, 1), 0.9)), (2, s.get((1, 2), 0.9))],
            2: [(1, s.get((1, 2), 0.9)), (3, s.get((2, 3), 0.8))],
            3: [(0, s.get((0, 3), 0.8)), (2, s.get((2, 3), 0.8))],
        }
        self.offsets = np.array([0, 2, 4, 6, 8])
        self.neighbours = np.array([1, 3, 0, 2, 1, 3, 0, 2])

    def neighbours_of(self, u):
        return iter(self._adj[u])


def ctx_for(store, fame_device):
    return MirrorContext.build(store, np.asarray(fame_device, dtype=np.float64))


def test_adjacent_pair_yields_forced_detour_not_a_vanished_cell():
    store = FakeStore()
    store._adj[0].append((2, 0.95)); store._adj[2].append((0, 0.95))
    store.offsets = np.array([0, 3, 5, 8, 10])
    store.neighbours = np.array([1, 3, 2, 0, 2, 1, 3, 0, 0, 2])
    cfg = SweepConfig.production()
    path, kind = journey(store, 0, 2, [], cfg, ctx_for(store, [0.5] * 4))
    assert kind == "forced" and len(path) == 3


def test_victim_is_the_highest_fame_interior_nulls_last():
    fame = np.array([np.nan, 0.2, np.nan, np.nan])
    pop = np.array([0.9, 0.5, 0.9, 0.99])
    key = victim_key(fame, pop, ["a", "b", "c", "d"])
    # 1 is measured (0.2); 3 is null with higher pop -- measured wins.
    assert min([1, 3], key=key) == 1


def test_fame_ramp_reaches_the_cost_function():
    # Make node 1 famous in FAME currency only (pop equal on both routes):
    # at a dominating ramp and k=1, the walk's d1 must route via 3.
    store = FakeStore()
    store.pop_raw = np.array([0.9, 0.5, 0.9, 0.5], dtype=np.float32)
    fame = [0.5, 0.99, 0.5, 0.01]
    cfg = SweepConfig.production().with_(w_known_ramp_fame_pctl=1000.0)
    ctx = ctx_for(store, fame)
    from artistpath_api.pathfinding import KNOWN, Exclusion
    ex = [Exclusion(node=1, reason=KNOWN)]
    path, _ = journey(store, 0, 2, ex, cfg, ctx)
    assert path == [0, 3, 2], "the fame term did not reach the cost function"


def test_walk_always_returns_max_depth_plus_one_entries():
    store = FakeStore()
    cfg = SweepConfig.production()
    fame = np.array([0.5, 0.5, 0.5, 0.5])
    out = walk_journey(store, 0, 2, cfg, ctx_for(store, fame), fame,
                       store.pop_raw, store.mbids)
    from cre_common import MAX_DEPTH
    assert len(out) == MAX_DEPTH + 1
```

`test_cre_mirror.py` additionally pins: `w_known_ramp_fame_pctl=0.0` produces a path
identical to `SweepConfig.production()`'s on the fake store (the G1(b) property);
`assert_cost_decomposition` passes on a correct configuration; and — the red half —
it **fails** on a deliberately broken one (monkeypatch `term_breakdown` to drop the
`hop` term and assert `SystemExit`), so the check is shown able to go red before any
run leans on its green.

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-08-03-cap-reevaluation/test_cre_mirror.py analysis/2026-08-03-cap-reevaluation/test_cre_ladder.py -v`
Expected: FAIL first (`ModuleNotFoundError`), then PASS after implementation.

- [ ] **Step 5: Append to the run log; commit**

```bash
git commit -m "CRE-T2: mirror copy with the fame-currency ramp, journey ladder, term breakdown" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T3`: `CRE-D3` — the pricing prior (Stage 0, runs before any build)

**Files:**
- Create: `analysis/…/cre_d3.py`

**Interfaces:**
- Consumes: `cre_common.{load_adopted, Ruler, famous_pairs, RAMPS, EXTREME_RAMP, C1_BAND, QUANT_FLOOR, MATERIAL, in_dir}`;
  `cre_mirror.{SweepConfig, MirrorContext}`; `cre_ladder.{walk_journey, assert_cost_decomposition}`.
- Produces: `cre_d3.json` — the committed Stage-0 prior.

- [ ] **Step 1: Implement**

On the **adopted artifact** (no build — §3.3's carve-out), for each of
`{"P0": 0.0} | RAMPS`: run `walk_journey` over the 22 famous pairs (endpoints resolved
by MBID; any endpoint absent from the artifact is a hard error — these pairs were drawn
from it). Then:

- **d0 identity assertion** (G1(b) shape): every arm's d0 journey identical to `P0`'s,
  every pair. Any divergence = the device fires at k = 0; abort.
- **Device liveness at the instrument extreme** (G2(a) form, run HERE because `CRE-D3`
  is otherwise the one device run with no live check between "inert" and "not
  connected" — analyst B1): at r = `EXTREME_RAMP` = 1.0, never a candidate, ≥ half of
  the 22 famous-pair journeys change at d1 vs `P0`'s d1. Below half → dead wire; the
  prior is unreadable and execution stops. Seconds of cost (22 pairs × 2 depths).
  Recorded in `cre_d3.json` beside the prior, so the null and its liveness proof
  travel together.
- **Cost decomposition** (G2(b) shape): `assert_cost_decomposition` at k = 1 and
  k = 10 on every ramp arm's returned journeys at those depths (`masked_edge` set for
  forced-detour journeys).
- **`C1` statistic per ramp arm**, per the prereg: per pair, median interior
  `fame_lb_pctl` pooled over depths 10–20 minus the same at d0; arm statistic = median
  of per-pair deltas; all-interiors and matched-only per plan pin 4; per-depth null
  counts (expected ≈ 0 on `ALG-E`).
- **The pre-registered consequence, written into the JSON**: if |Δ| < 0.015 at both
  settings (the expected outcome), the stored `consequence` field carries the §4
  wording verbatim — *"the pricing device is inert on famous pairs at incumbent supply,
  as Track 3 found; the open question was and is supply"* — which `CRE-R0` is bound to.
  If Δ ≤ −0.05 at either setting, the stored field says the committed prior is
  contradicted and **execution pauses for the owner's flag before Stage 2 begins**
  (prereg §4); the run log records the stop.

Docstring carries `CRE-D3`'s plain sentence from the prereg verbatim, plus: *instrument
prior, barred from candidacy and from every `CRE-R` winner clause; re-opens neither the
Track 3 closed verdict nor the parked DD-A2 decision.*

- [ ] **Step 2: Run it**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_d3.py`
Expected: d0-identity PASS, extreme-ramp liveness PASS (share ≥ 0.5 reported),
cost-decomposition PASS, then per-arm `C1` figures and the consequence field. Expected
branch per §9: no measured movement at both settings. A few minutes of compute — the
analyst measured production-weight journeys at ~5 ms each on the adopted-shape graph
(critique V1), so the 3 × 22 × 21 ladder is dominated by load time, not routing.

- [ ] **Step 3: Append to the run log (the figures and the branch taken); commit**

```bash
git commit -m "CRE-D3 (CRE-T3): the pricing prior on the adopted artifact, committed" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T4`: `CRE-D1` — the banding read (Stage 0, confirmatory)

**Files:**
- Create: `analysis/…/cre_d1.py`

**Interfaces:**
- Consumes: `cre_common.{load_adopted, Ruler, in_dir}`; `tas_frame_split.five_frames`;
  `tas_weighting.idf_table`; the frozen `cre_probe3b.py` **read, never imported or
  edited** (plan pin 5).
- Produces: `cre_d1.json` — the committed branch decision every later task reads.

- [ ] **Step 1: Read `builder/analysis/2026-08-03-cre-prereg-critique/cre_probe3b.py`**

It is the origin of §4's statistic wording. Match its aggregation exactly in new code;
where its behaviour and the prereg's words disagree, **the words govern** and the
divergence is recorded in the run log and in `cre_d1.json`.

- [ ] **Step 2: Implement**

Substrate: the adopted artifact's surviving edge set (undirected, u < v). Statistic,
per the prereg §4 exactly: rarity-weighted `W4` agreement per labelled edge (**the
`rarity` measure — Σ idf over ∩ ÷ Σ idf over ∪; no vote weighting — `CRE-AM1` leaves
`CRE-D1` untouched**), edges banded by endpoint `fame_lb_pctl` (popular↔popular = both
≥ 0.75; obscure↔obscure = both ≤ 0.50; ruler-null endpoints belong to no band),
compared size-matched: `(min, max)` endpoint label-set-size cells with ≥ 30 edges in
each band contribute; per-cell difference = popular-band mean − obscure-band mean;
overall = edge-weighted mean of per-cell differences (weights = the cell's contributing
edge count). `idf_table(frames["W4"], n_artists=<adopted node count>)` (plan pin 5).

Output fields: the size-matched difference; per-band labelled-edge counts and the
**labelled-edge share per band** (every `D1` sentence must carry it); readability
(≥ 500 labelled edges per band); the branch —
`supported` iff difference ≤ −0.05 and readable; else `not_supported` / `unreadable`;
and the §9 disclosure restated: *the pre-run critique measured +0.08 on this substrate;
the expected branch is "not supported"*.

- [ ] **Step 3: Run it**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_d1.py`
Expected: the committed confirmatory figure (expected near +0.08, branch
`not_supported`). **Branch consequences, applied from here on:** `supported` → the
*(D1-branch)* cells of §0.2 exist (B-S2-P0, E-S2-P1a, B-S2-P1a) and a router-side tag
pricing arm becomes *eligible by §8 amendment written before it is built* — that
amendment is **not** this plan's to write; pause and hand to the owner-facing flow.
`not_supported`/`unreadable` → those cells do not exist. **E-S2-P0 is branch-proof and
runs regardless.**

- [ ] **Step 4: Append to the run log; commit**

```bash
git commit -m "CRE-D1 (CRE-T4): the banding read, confirmatory run committed" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T5`: The cleaned-substrate build harness and the non-tag cells

**Files:**
- Create: `analysis/…/cre_build.py`
- Test: `analysis/…/test_cre_build.py`

**Interfaces:**
- Consumes: `artistpath_builder.pipeline.build_from_archive` (and the body of that
  function, copied); `cb_build_variants.{ReadOnlyArchive, cap_trimmed_union, cap_uncapped,
  ARCHIVES, ALGORITHMS}` (imported from the frozen file); `artistpath_builder.{artifact.serialise,
  config.BuilderConfig, graph.*, sources.listenbrainz.*}`.
- Produces: `assemble_cleaned(config, archive, source, cap_step) -> tuple[Graph, dict]`
  (diagnostics include `nodes_entering_cap` and `_log_scaled`-equivalent `pop_log_low`
  / `pop_log_high` over kept nodes); `build_cell(data_set, supply, params) -> dict`
  (manifest; writes `builder/scratch/cre-cells/<cell>.bin` + `.bin.json`);
  `gate() -> dict` (green ×2 + red).

- [ ] **Step 1: Copy the live pipeline body, inject the one seam**

`assemble_cleaned` is the body of `pipeline.build_from_archive` **as it stands today**
(both drop flags applied — copy it verbatim, do not reconstruct from memory), with
exactly one change: the cap invocation (the `cap_strategy`/`mutual_knn_cap` site) is
replaced by `cap_step(adjacency, ranking, pop)`, computing `pop` upstream of the cap the
way `cb_build_variants._assemble:444-448` does (log-scaled score-weighted in-degree —
a VALUE, not a rank). Assert `config.drop_no_release_tail and config.drop_featured_credit`
at entry (they are the defaults; a cell with either off is not in this design).
Record `nodes_entering_cap` (len of the adjacency handed to `cap_step`) and, over the
kept node set, `pop_log_low`/`pop_log_high` (the §0.3 instrumentation row — the affine
map inputs).

- [ ] **Step 2: The instrument gate — green twice, red once**

`gate()`: for each data set, `assemble_cleaned` with `cap_step` = shipped
`mutual_knn_cap` at k = 50 must serialise **byte-identical** to a direct
`build_from_archive(BuilderConfig(algorithm=<data set's>), ReadOnlyArchive(...), source)`
run (green — proves the copy is the live pipeline, drops included). Then k = 49 must
differ (red — proves the gate can fail). The `cb_build_variants.gate()` shape, upgraded
to the live pipeline. Write `cre_build_gate.json`.

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_build.py --gate`
Expected: `GREEN ALG-E: PASS`, `GREEN ALG-B: PASS`, `RED k=49: PASS`. **A green failure
means the copy is not the live pipeline — find the drift; do not adjust the gate.**

- [ ] **Step 3: Build the non-tag cells**

Every cell through `assemble_cleaned` (uniformly, so every manifest carries the same
diagnostics), cap steps: `MK50`/`MK100` = shipped `mutual_knn_cap` at k; `TU` =
`cap_trimmed_union(j=50, d=50, trim="weakest_first")` (the committed `TUw-50-50` shape,
imported); `UC` = `cap_uncapped` (staged reference, barred from candidacy — say so in
the manifest). Per data set: `S0` (MK50), `S0b` (MK100), `S1` (TU), `S3` (UC) — eight
builds into `builder/scratch/cre-cells/` with sidecars beside the bins, **and every
manifest mirrored into a committed `analysis/…/cre_builds.json`** — `.gitignore`
ignores `builder/scratch/` wholesale, so a sidecar there can never reach git and the
artifact-identity rule would silently lose its record (analyst m11; the Track B
precedent).

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_build.py --all-nontag`
Expected: eight manifests, ~30–90 s each.

- [ ] **Step 4: Unit test** — `test_cre_build.py` pins: the entry assertion fires when a
flag is off (`pytest.raises` on a config with `drop_no_release_tail=False`), and
`nodes_entering_cap` / `pop_log_low` / `pop_log_high` appear in diagnostics. Run the
module tests. Expected: PASS.

- [ ] **Step 5: Append to the run log (shas of all eight cells); commit**

```bash
git commit -m "CRE-T5: cleaned-substrate build harness (gated) and the eight non-tag cells" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T6`: The `S2` device, its companions, and the tag cells

**Files:**
- Create: `analysis/…/cre_tags.py`
- Modify: `analysis/…/cre_build.py` (add `cap_tag_limited`; nothing existing changes)
- Test: `analysis/…/test_cre_tags.py`

**Interfaces:**
- Consumes: `wav_read.{masses, rel_table, rel_for}` and `wgt_grid.S_CAP` (imported from
  the frozen files — the `wav_read` import precedent); `tas_frame_split.five_frames`;
  `tas_weighting.idf_table`; `tas_guard.permuted_labels_among_labelled`;
  `tas_common.GLOBAL_NEUTRAL_FALLBACK`.
- Produces: `agreement_table(kind) -> EdgeAgreement` for `kind` in
  `{"real", "label_scramble", "vote_scramble"}` — an object with
  `.a(mbid_u, mbid_v) -> float | None` (None where either endpoint has no `W4` label)
  and `.kind`; `cap_tag_limited(adjacency, ranking, pop, *, j, d, agree)`.

- [ ] **Step 1: Implement `cre_tags.py`**

One agreement table per kind, built **once** on the committed machinery and applied by
MBID in every cell (held constant across cells — the factor-table discipline):

- `real`: `W4` = `five_frames()["W4"]`; `idf = idf_table(W4, n_artists=<adopted node
  count>)`; per-artist `e_rel` via `wav_read.masses()` → `rel_table` → `rel_for`;
  `a(u,v) = Σ idf·min(r_u, r_v) over ∩ ÷ Σ idf·max(r_u, r_v) over ∪` — `wav_read`'s
  `evidence_rel` expression verbatim (its `WAV-0d` degeneracy proof is what guarantees
  the dark-tail rule: where votes are absent the measure reduces to rarity).
- `label_scramble`: `permuted_labels_among_labelled(W4, seed=20260803)` — `TAS-AM3b`'s
  stronger null form, labelled-artist set held fixed — then the same machinery.
- `vote_scramble` (`CRE-AM1`): per artist, permute the label→strength assignment among
  **its own** labels (seeded `20260803`, `random.Random(seed + mbid)` per artist for
  determinism under any iteration order) **before** `rel_table`; label sets untouched.
  Preserves each artist's vote-distribution shape, destroys which tag each vote
  attaches to — the amendment's sentence, implemented.

- [ ] **Step 2: Implement `cap_tag_limited` in `cre_build.py`**

`cap_trimmed_union`'s exact structure and order (union → symmetrise keep-stronger →
ceiling by whole-edge deletion at over-budget nodes, node order `(-degree, mbid)`), with
**only** the deletion ranking changed, per plan pin 1:

```python
def cap_tag_limited(adjacency, ranking, pop, *, j, d, agree):
    """CRE-S2 (prereg §3.2 + CRE-AM1). ONE knob differs from cap_trimmed_union:
    the ranking that decides which edges an over-budget node loses.
    Deletion key ascending: (strength(u,v) * a_eff(u,v), strength(u,v), _desc(v));
      a_eff = agree.a(u,v) where measured, else the median of u's measured
      values (>= 2, else GLOBAL_NEUTRAL_FALLBACK) -- the committed neutral rule,
      so unlabelled edges rank by LB similarity alone at a neutral level in the
      same pool. Tags re-order the deletion ranking; they never create an edge
      or veto by absence.
    THE MIDDLE KEY ELEMENT IS LOAD-BEARING (analyst M4): agreement is exactly 0
    on ~3.9% of measured edges, and a bare product would order that whole block
    by MBID with similarity playing no part. The strength element keeps
    LB-similarity order inside the zero block and every product tie, and makes
    the degeneracy gate's byte-identity exact by construction."""
```

Body: copy `cap_trimmed_union`'s union/symmetrise/ceiling loop; in the over-budget
branch compute `a_eff` per neighbour and
`doomed = sorted(result[node], key=lambda v: (strength(node, v) * a_eff[v], strength(node, v), _desc(v)))[:excess]`.

- [ ] **Step 3: The degeneracy and liveness gates (the `WAV-0d` pattern)**

In `test_cre_tags.py`, on a small synthetic adjacency: (a) **degeneracy** — with an
`agree` whose `.a` returns `None` everywhere, `cap_tag_limited` output equals
`cap_trimmed_union(trim="weakest_first")` output exactly. This holds **by
construction** under the tuple key: every `a_eff` collapses to one constant, so the
first element ties wherever strengths tie or products collapse, and the second
element is the strength order itself. (Do not restate the earlier "a constant
multiplier preserves the order" argument — in IEEE doubles it is only monotone
non-decreasing, and distinct strengths can collapse to equal products; the tuple is
what makes the identity exact rather than empirically true — analyst M4a.) (b)
**liveness** — with an `agree` that ranks one specific strong-similarity edge at
agreement 0, that edge is deleted first at an over-budget node. Plus: the vote-scramble
table preserves each artist's multiset of strengths, and the label-scramble table
preserves exactly which artists are labelled.

Then the same degeneracy check **on the real build**: `--degeneracy-gate` builds
E-S2 with the all-None table and asserts byte-identity to the committed E-S1 cell sha.
A mismatch means the S2 builder is not one knob away from S1 — the §0.2 isolation is
broken; stop.

- [ ] **Step 4: Build the tag cells and companions**

E-S2 (real), E-S2-labelscramble, E-S2-votescramble. If `cre_d1.json` fired
`supported`: also B-S2 (real + both companions). Manifests as in T5 (mirrored into
`cre_builds.json`), each naming its `agree` kind and seed — **and, per analyst M8,
each `S2` manifest records the cell's labelled-node share and its share of nodes with
≥ 2 measured agreements** (below that a node's whole pool collapses to one constant
and the device is structurally inert there — ~35–39 % of `ALG-B` nodes on the
pre-drop measurement, vs 18 % on `ALG-E`). T11 stores these shares beside any `CRE-C5`
attribution field for a `B-S2` cell, as a licensing constraint the findings note must
quote.

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_build.py --tag-cells`
Expected: 3 builds (or 6 on the supported branch), manifests committed.

- [ ] **Step 5: Append to the run log; commit**

```bash
git commit -m "CRE-T6: tag-limited ceiling (degeneracy-gated), scramble companions, tag cells built" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T7`: Stage 1 — screens (`CRE-G3`, `CRE-C3`, `CRE-C6`), then SEAM 1

**Files:**
- Create: `analysis/…/cre_screen.py`
- Test: `analysis/…/test_cre_screen.py`

**Interfaces:**
- Consumes: every `cre-cells` manifest; `cre_common.{Ruler, famous_pairs}`;
  `cre_mirror`/`cre_ladder` for d0 journeys at production weights.
- Produces: `cre_screen.json` — per cell: `CRE-G3` endpoint survival, `CRE-C3`
  coverage, `CRE-C6` per-pair supply counts and 1-hop headroom, the screen decision,
  and the cross-cell `pop_raw` affine report.

- [ ] **Step 1: Implement, exactly per §4**

- **`CRE-G3`:** endpoint survival for all 22 pairs on both cleaned substrates (the S0
  cells); any pair losing an endpoint is removed from every cell, and the readable-pair
  floor (≥ 8 pairs with a non-empty d0 interior in every compared cell — journey
  semantics, so forced-detour interiors count) is recomputed and recorded per
  comparison.
- **`CRE-C3`:** per cell, `nodes_entering_cap` (that data set's cleaned pre-cap
  population, identical across its cells — assert this) minus the cell's kept count;
  **≥ 10,000 → disqualified**; below, reported never disqualifying.
- **`CRE-C6`:** per cell, per pair: run the d0 journey at production weights; interior
  median `fame_lb_pctl` (measured only); the 1-hop frontier = path nodes ∪ their
  neighbours; count edges from the frontier to artists with measured `fame_lb_pctl`
  ≤ median − 0.15; per-pair headroom = median − min measured `fame_lb_pctl` in the
  frontier. **Screen out iff the zero-supply pair count makes a `CRE-C1` median pass
  arithmetically impossible — more than half the readable pairs (≥ 12 of 22 at the
  full draw, recomputed under `CRE-G3` drops).** A screened cell that is a named
  isolating baseline still sweeps (baseline is instrument, not candidate) — encode
  §0.2's baseline column so this is mechanical. Three pins from analyst m12:
  **(a)** "readable pairs" in the screen denominator = the pairs surviving `CRE-G3`'s
  **endpoint-survival** device (the per-comparison ≥ 8 floor is a different device
  and plays no part here); **(b)** the frontier's `absent` and `null` artist counts
  (pin 2's classes) are reported beside the measured-only supply count, since the
  device can route into them while the count cannot see them; **(c)** a pair whose d0
  journey has no measured interior has no median and its `C6` is recorded
  `c6_undefined` — excluded from the screen denominator, reported, never silently
  zero.
- **Affine report:** the `(pop_log_low, pop_log_high)` pairs from every manifest, and
  the affine map between each arm and its isolating baseline (§0.3's instrumentation
  row — two floats per cell, reported not gated).

Unit test: the screen-out arithmetic (12 of 22 screens; 11 of 22 does not; the
baseline carve-out survives a screen).

- [ ] **Step 2: Run it; commit; SEAM 1**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_screen.py`

```bash
git commit -m "CRE-T7: Stage 1 screens committed (G3, C3, C6, affine report) -- Seam 1" -- builder/analysis/2026-08-03-cap-reevaluation/
```

**This is Seam 1 (prereg §4).** Stage 0 + Stage 1 are committed artifacts. A session
retiring here leaves a complete handoff: the next session starts at `CRE-T8` reading
`cre_d3.json`, `cre_d1.json`, `cre_screen.json` and the manifests cold.

---

### Task `CRE-T8`: Stage 2 entry — `CRE-G1`(a)(c) and `CRE-G2`(a)

**Files:**
- Create: `analysis/…/cre_gates.py`

**Interfaces:**
- Consumes: the E-S0 cell bin; `artistpath_api.pathfinding.find_journey` +
  `artistpath_api.config.ApiConfig` (production code, imported); `cre_ladder.journey`.
- Produces: `cre_gates.json`.

- [ ] **Step 1: Implement and run**

- **`G1`(a):** on the **E-S0 cleaned substrate** (same graph both sides), for all 22
  pairs: `cre_ladder.journey` under `SweepConfig.production()` must return the same
  node sequence and stop-kind as production
  `find_journey(store, s, t, [], ApiConfig())`. **Any divergence = instrument failure;
  no read opens until fixed** — fix the harness, never widen the bar. Also run on
  B-S0 and report (the prereg gates E only; the B run is reported QA, not a bar).
- **`G1`(c):** re-assert the ruler frame N (constructing `Ruler` does this; record it).
- **`G2`(a):** per cell that carries a `P1` arm (E-S1; B-S0, B-S1; plus S2 `P1` cells
  on the supported branch): at r = 1.0 (instrument-only), ≥ half of famous-pair
  journeys change at d1 vs the same cell's `P0` d1. Below half → dead wire; no `P1`
  null in that cell is readable. d0–d1 only; cheap.

(`G1`(b) and `G2`(b) are per-sweep-run assertions and live in `cre_sweep.py` — T9.)

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_gates.py`
Expected: `G1a: PASS (22/22 identical, kinds match)`, frame N recorded, `G2a` per cell
≥ 0.5.

- [ ] **Step 2: Append to the run log; commit**

```bash
git commit -m "CRE-T8: Stage 2 instrument gates (G1a/G1c/G2a) committed" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T9`: Stage 2 sweeps — `ALG-E`, one committed JSON per cell, then SEAM 2

**Files:**
- Create: `analysis/…/cre_sweep.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `cre_sweep_<cell>.json` per §0.2 cell (and per companion), each carrying:
  `artifact_sha256`, cell id, supply/pricing coordinates, per-pair per-depth journeys
  **with stop kinds**, per-depth `CRE-D2` term shares (from `term_breakdown`),
  per-depth `interiors_null_in_snapshot` and `interiors_absent_from_snapshot`
  (pin 2's two classes, separately) and `null_interior_unbypassable` (pin 3's
  mechanical component), the in-run `G1`(b) and `G2`(b) assertion results,
  `pop_log_low/high`, and the cell's own infeasible set.

- [ ] **Step 1: Implement `cre_sweep.py --cell <id>`**

One cell per invocation (prereg: "committed as one JSON per cell, so any session can
stop and hand off between cells"). Per cell: load its bin (sha-asserted against its
manifest), build `MirrorContext` with the ruler's device array, run `walk_journey`
over the readable pairs at the cell's pricing (`P0` = production config; `P1a`/`P1b` =
`w_known_ramp_fame_pctl` at 0.01/0.03). In-run assertions, hard failures:

- **`G1`(b):** a `P1` cell's d0 journey bit-identical to its **supply-matched `P0`
  cell's** d0 journey (read from that cell's committed JSON; it always sweeps first —
  §0.2's baseline column plus this rule gives the order mechanically). The
  supply-matched form is pinned deliberately (analyst m9): a `P1b` cell's §0.2
  isolating baseline is its `P1a` sibling, and identity against a device-off cell is
  what makes this a device test rather than a ramp-size test — the two are equivalent
  at d0 only if `P1a` itself passed, so assert against the device-off cell directly.
- **`G2`(b):** `assert_cost_decomposition` at k = 1 and k = 10 on every `P1` pair
  (`masked_edge` set for forced-detour journeys).

`CRE-D2` per depth: `term_breakdown` over the returned journey; store per-term shares
of total path cost — the accounting §0.3's `w_floor` rule and any supply-attribution
sentence will need.

- [ ] **Step 2: Run every surviving `ALG-E` cell**

From `cre_screen.json`'s surviving set (plus screened-but-baseline cells): E-S0-P0,
E-S0b-P0, E-S1-P0, E-S1-P1a, E-S1-P1b, E-S2-P0 (+ its two companions), E-S3-P0
(+ E-S2-P1a and companions on the supported branch). One command per cell, committed
per cell:

```bash
cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-03-cap-reevaluation/cre_sweep.py --cell E-S1-P1a
git commit -m "CRE-T9: sweep JSON for E-S1-P1a" -- builder/analysis/2026-08-03-cap-reevaluation/
```

Cost, now measured rather than guessed (analyst V1, on the pre-drop Track B cells):
production-weight journeys run ~5 ms on a capped cell and ~0.4–0.6 s on UC, so a full
22 × 21 ladder projects to **seconds on a capped cell and ~4–5 minutes on UC** —
the plan's earlier "~8–15 min per capped cell" was conservative by two orders of
magnitude and must not be used for scheduling. UC still runs last and never through
`tail`; the discipline costs nothing and the cleaned rebuilds could shift the
constants.

- [ ] **Step 3: SEAM 2.** All `ALG-E` sweep JSONs committed; append the run log. A
session retiring here hands off cleanly; the next starts at T10 cold.

---

### Task `CRE-T10`: Stage 2 sweeps — `ALG-B`

Same harness, same per-cell commits: B-S0-P0, B-S0b-P0, B-S1-P0, B-S0-P1a, B-S1-P1a,
B-S1-P1b, B-S3-P0 (+ B-S2 cells and companions on the supported branch). `G2`(a) for
B `P1` cells was recorded in T8; `G1`(b)/`G2`(b) assert in-run as before. Expect the
§0.4 censoring row to be visible here: per-depth null counts will be material
(~6% of `ALG-B` nodes are ruler-null) — that is the pre-registered reporting
obligation working, not a defect.

```bash
git commit -m "CRE-T10: sweep JSON for <cell>" -- builder/analysis/2026-08-03-cap-reevaluation/
```

---

### Task `CRE-T11`: Criteria figures and the run-state map, then SEAM 3

**Files:**
- Create: `analysis/…/cre_score.py`
- Test: `analysis/…/test_cre_score.py`

**Interfaces:**
- Consumes: every `cre_sweep_*.json`, `cre_screen.json`, `cre_d3.json`, `cre_d1.json`,
  `cre_gates.json`; `cre_common` constants.
- Produces: `cre_scores.json`. **Figures only, no verdict sentences** — the `fi_stats`
  "FIGURES ONLY, NO VERDICTS" precedent. The Stage-3 findings note (four-part shape,
  §4) is the next session's work at Seam 3, written from the committed record.

- [ ] **Step 1: Implement, one function per criterion, unit-tested on synthetic ladders**

- **Uniform drop, over pin 9's committed partition:** `drop_infeasible_uniformly`'s
  rule (a (pair, depth) cell infeasible in any compared cell is dropped from every
  compared cell), computed over the **canonical group per data set** (non-staged cells
  + named isolating baselines), each `S3` cell only in its own two-cell group against
  its §0.2 baseline, companions inside their tag cell's group. Group memberships and
  dropped sets committed; every reported figure names its group. (Analyst M3: an
  undefined partition leaves the headline `C1` unpinned, and a staged UC cell inside
  the candidates' group would delete (pair, depth) cells from every candidate — UC is
  where d0 adjacency concentrates, 6 of 22 pairs pre-drop.)
- **`CRE-C1` per non-staged cell:** per-pair delta (pooled d10–20 interior median −
  d0 interior median, measured values only), arm median; all-interiors AND matched-only
  (plan pin 4); per-depth null counts and the d0 → d10–20 null-share trend, with the
  §0.4 rule applied: **null share rising > 0.05 → the stored `C1` carries
  `"descent_partly_unmeasurable": true`**, never a clean pass. Conjunction fields:
  (i) median ≤ −0.05; (ii) bootstrap 95% upper bound ≤ −0.015 (plan pin 7); (iii) the
  knife-edge trio — count of pairs ≤ −0.05, count |Δ| < 0.015, leave-one-out range.
  Also the d3–5 band, descriptive, marked `"never_a_bar": true`. Also `C1` as a
  fraction of the cell's own `C6` 1-hop headroom (§0.4's descriptive companion) —
  **always stored with its denominator and the cell's mean frontier size beside it**
  (analyst m13: frontier size is set by the supply knob, ~130 nodes on MK50 vs ~8,850
  on UC pre-drop, so this companion is readable across *data sets* — its §0.4
  purpose — and never across supply arms; the findings note quotes the denominator or
  does not quote the ratio).
- **`CRE-C2`:** interior share in the top-1%-by-degree set per depth band (d0–2 vs
  d10–20 pooled), **primary = the adopted artifact's set by MBID (plan pin 6),
  own-graph share reported beside it**; kill fields for the two clauses (Δ ≥ +0.10, or
  d10–20 level > 0.50); the measured base rates quoted so a null is not read as
  reassurance.
- **`CRE-C4`:** per pair, mean interior count over d10–20 ÷ d0 interior count; arm
  median; **binding = ratio to the isolating baseline's `C4` ≥ 0.70, except the two
  anchors (E-S0-P0, B-S0-P0), which carry no binding form per `CRE-AM2`** (T1 Step 2
  — E-S0-P0 has no baseline and B-S0-P0's is cross-data-set, which §0.4 bars) and are
  reported absolute against the 0.75 reference line, marked `"no_binding_form":
  "anchor"`. The absolute median is reported for every cell. Stored jointly with `C1`
  per cell (the `CRE-R3` shape is computed here as a flag, not a sentence). Per-pair
  d0 denominators are stored too — d0 adjacency is arm-correlated (1/22 on MK50/TU
  vs 6/22 on UC pre-drop), so the smallest denominators sit on the arms that add
  connections, and the findings note needs that visible.
- **Empty-interior depths, pinned (analyst m15):** an `adjacent_only` depth records
  its two-node path — it is feasible, so the uniform drop does not touch it; it
  contributes an interior count of **0** to `C4` and no slots to `C1`'s pools. The
  `run_arms.py` precedent, stated here because union arms create adjacency far more
  often than the committed tracks did.
- **`CRE-C5`, per tag cell and per companion kind:** Δgain = cell `C1` − isolating
  baseline `C1`; entry condition real Δgain ≤ −0.05; paired-difference bootstrap CI
  (real − companion, per pair, plan pin 7) excluding zero. **Two companions, two
  licences (`CRE-AM1`):** label-scramble → "tags did this"; vote-scramble → "votes did
  this"; both stored as booleans with their CIs. A cell beating neither keeps its
  outcome and gets `"attribution_licensed": false`. For any `B-S2` cell, the T6
  manifest's labelled-node and ≥ 2-measured-agreement shares are stored beside the
  attribution fields (analyst M8: the device is structurally inert on ~a third of
  `ALG-B` nodes for a population reason, and no attribution sentence may omit that).
- **The `w_floor` attribution guard (§0.3):** per supply-knob comparison, the `D2`
  floor-term shares of both cells, and a boolean
  `"supply_attribution_carried_by_floor_term"` — the findings note may not attribute
  to the supply knob alone where this is true.
- **The run-state map (§6's precondition, made mechanical):** every §0.2 cell (branch
  cells per `cre_d1.json`), its sweep JSON present/absent, every gate outcome,
  `CRE-D3`/`CRE-D1` committed — and `"cre_r_readable": true/false`. **If any specified
  cell is unrun (both `S3` cells and E-S2-P0 included), the map names it; no `CRE-R`
  is readable and the output says so.**

- [ ] **Step 2: Run tests, then the scorer; commit; SEAM 3**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-08-03-cap-reevaluation/test_cre_score.py -v`
Then: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-08-03-cap-reevaluation/cre_score.py`

```bash
git commit -m "CRE-T11: criteria figures and the run-state map committed -- Seam 3" -- builder/analysis/2026-08-03-cap-reevaluation/
```

**This is Seam 3.** Retire the session here. The findings note — Stage 3, the
four-part shape, every identifier with its plain sentence, the summary naming whatever
cuts against it, `CRE-R` reads under §6's wording constraints — is written by a fresh
session from `cre_scores.json` + the prereg, never from this session's memory. Closeout
per the skill (including the Snyk scan over the new scripts and the `--out`-argument
row in the deferral table).

---

## What is NOT in this plan, and why

- **The Stage-3 findings note and every `CRE-R` sentence.** §6's run-state rule plus
  the seam discipline: the reader of results must be a session that did not run them.
- **The router-side tag pricing arm.** Eligible only on a `CRE-D1` "supported" branch,
  and then only by a §8 amendment written before it is built, with its scrambled
  control named in the same amendment. Writing that amendment is not an executor task.
- **Any adoption, default change, rebuild of the served artifact, or blind listen.**
  Prereg §7. The blind listen (`REQ-38`) stands before any adoption regardless of
  numbers.
- **Re-running Track B cells, re-validating either drop rule, re-litigating any closed
  track.** All closed (`NEXT.md`; prereg §7).
- **The `w_degree_hub` decision for a winning arm's graph** — a named follow-up at
  `CRE-R1`/`R2`, the findings note flags it, nobody reprices mid-sweep.

## Handoff and degradation

Seams 1–3 are the planned handoff points; per-cell sweep commits make unplanned ones
cheap everywhere in T9/T10. A material mid-flight amendment is also a seam. If the
degradation tell fires (asked for a figure already computed; an item dropping from a
tracking file; a firm claim revised under mild questioning with no new information),
that is a mid-flight closeout per the standing rule — retire at the next cell boundary.

## Revision record (2026-08-03, after the analyst review, before any run)

The plan as first committed (`e69efa0`, PR #69) was reviewed by the `ml-graph-analyst`
at the owner's instruction, **before any task ran** — the committed record, probe
scripts included, is `builder/analysis/2026-08-03-cre-plan-critique/`. This revision
folded every surviving finding in; the git diff against `e69efa0` is the exact delta.
These are pre-run corrections to an unfrozen operational plan, so they are revisions;
the prereg itself is touched only by `CRE-AM2`, which T1 Step 2 has the executor
append pre-run with the §8 disclosure rules.

Folded, each traceable: `assert_toll_arithmetic` was a tautology and `CRE-D3` had no
live device check — replaced by `assert_cost_decomposition` against the search's own
accumulated cost, plus the extreme-ramp liveness run inside `cre_d3.py` (B1); pin 2
split into two priced classes after the analyst proved the snapshot's key set is
exactly the two MK50 node sets, with separate per-depth counters (M2); the uniform-drop
partition pinned as pin 9, staged `S3` cells quarantined in their own groups (M3);
the `S2` deletion key gained its middle tuple element and the degeneracy gate became
exact by construction (M4); pin 3's mechanical null-share inflation named, with the
`null_interior_unbypassable` counter (M5); `C4`'s two anchor cells resolved by
`CRE-AM2` (M6); the guard/journey resolution promoted to pin 8 with an assert (M7);
`S2` coverage shares recorded and made a `C5` licensing constraint (M8); the `G1`(b)
comparator pinned supply-matched-`P0` (m9); the null-price test asserts against the
frame minimum (m10); manifests mirrored into a committed `cre_builds.json` (m11);
`C6`'s denominator, frontier-class reporting and undefined-median case pinned (m12);
the headroom companion carries its denominator (m13); `term_breakdown` gained entry
assertions making its five terms exhaustive (m14); empty-interior depths pinned to
the `run_arms.py` treatment (m15); `journey()` uses production's `DISLIKE` predicate
(m16); runtime estimates replaced with the analyst's measurements (V1).

**Divergences from the analyst's exact proposals, both deliberate:** M2's fix 2 left
the never-fetched device price an open choice between maximal obscurity and the frame
median — this revision pins the **neutral 0.5**, because the committed neutral-rule
precedent prices missing information at a neutral level, and steering the device into
a class the score cannot read would manufacture §0.4's disclosure condition. M6's fix
said "stop before it" — this revision resolves it instead with a pre-run §8 amendment
(`CRE-AM2`, the `TAS-AM5` timing pattern), because the contradiction is knowable now
and a mid-run stop would spend a seam on it.

**Known and accepted:** the analyst's cell-level figures were measured on pre-drop
Track B builds (its stated weakest link); every count quoted above is labelled with
that provenance where it appears. Its "inherited, named once" note — the `C6` screen's
"arithmetically impossible" is a d0-frontier heuristic, not an identity over a
20-press ladder — is frozen prereg wording, faithfully copied, and belongs to the
findings note's weakest-link section, not to this plan.

## Self-review (run by the author, 2026-08-03)

**Spec coverage.** §0.2's seventeen cells + companions → T5/T6 builds, T9/T10 sweeps,
branch cells gated on `cre_d1.json`. §0.3's held-constant rows → asserted (drop flags,
ruler, pair set, weights via `production()`), instrumented (`pop_log_low/high`), or
implemented (ladder, victim rule, uniform drop); the `w_floor` handling → `term_breakdown`
+ the T11 guard boolean. §0.4 → null counts/trend in every sweep JSON and `C1`, the
headroom companion in T11. §1 → `Ruler`, `QUANT_FLOOR`, plan pin 4. §2's six
dependencies → (1) T1, (2) T2, (3) T6, (4) T6, (5) T2 `term_breakdown`, (6) T2
`journey`/`walk_journey`. §3.1/§3.2/`CRE-AM1` → T5/T6 with the degeneracy gate proving
one-column isolation. §3.3 → `RAMPS`, the closed-cell rule (no E-S0 `P1` candidate cell
is ever built; `CRE-D3` runs on the adopted artifact), `TB-P5H-7` consumption via `C4`
stored jointly with `C1`. §4's stages and seams → T3/T4 before T5 (Stage 0 before any
build), T7 screens before sweeps, gates T8 + in-run assertions, seams after T7/T9/T11.
§5's five criteria → T11 (C3/C6 in T7). §6 → the run-state map; no verdict sentences
anywhere in the harness output. §7 → the exclusions section above.

**Placeholder scan.** Two deliberate non-code steps remain: T2 Step 1 and T5 Step 1 are
copy-with-named-delta instructions — the copies' fidelity is proven by executable gates
(the `--no-index` diff + `CRE-G1`(a); the green/red build gate), not by transcription
into this document, which is the same reasoning `TAS-R3` Step 5 recorded. T4 pins its
aggregation to a committed probe read at execution time, with the governing-words rule
stated. No TBDs, no "handle edge cases", no test named without its content or its
gate.

**Type consistency.** `journey(store, s, t, excludes, cfg, ctx, stats)` and
`walk_journey(store, s, t, cfg, ctx, fame_measured, pop, mbids, stats)` are defined in
T2 and consumed with those signatures in T3/T7/T8/T9. `Ruler.arrays(store)` returns
`(measured, device)` in that order everywhere. `agreement_table(kind).a(u, v)` is the
one agreement surface T6's `cap_tag_limited` consumes. `RAMPS` keys (`P1a`/`P1b`)
match the §0.2 cell suffixes used in T9/T10's `--cell` ids.
