# Phase 2 Sweep Results — six arms, two slices

**Date:** 2026-07-22 · **Role: AUTHORITATIVE** for every figure in this document.
Produced by Task 15 of `plans/2026-07-22-phase2-revised-plan.md`. Linked from
`2026-07-21-scoring-adjudication.md` §6 (claims 41–45).

**No adoption decision is recorded here.** At the time of writing the arm to adopt was
undecided and a blind listening test was pre-registered but not run — see execution log
§15. The findings below stand regardless of which arm is adopted, and are the most
durable product of this task.

---

## 0. The four findings that outlive the decision

1. **Adamic–Adar and the overlap coefficient are unstable at these effect sizes.** Among
   `capfix`, `rankfix` and `d025` the differences are small and **sign-flip between the
   analysis and held-out slices**. They cannot support a reproducibility criterion here.
2. **Correction — "the rescale costs overlap" is an analysis-slice artifact.** On the
   analysis slice `rankfix` loses to `capfix` on AA and OC, both significant. On held-out
   the same comparison is null and the *means reverse* (`rankfix` AA 0.7630 vs `capfix`
   0.7561). The earlier claim is **overturned**.
3. **`hubfrac` and `ceiling_hops` reproduce significantly across both slices** and are the
   trustworthy channel for this comparison.
4. **`d025` is never worse than `capfix` on any metric on either slice.**

And a fifth, about the instrument rather than the arms:

5. **The held-out slice at n = 29 is underpowered for small effects.** This is a **panel
   design** weakness, not a property of any arm. It is input to Phase 1's bypass telemetry,
   which is the instrument that actually settles this class of question — real usage data
   at volume, rather than a 130-pair frozen panel split 100/30.

---

## 1. The arms

All six built from the same archive at commit `f7583b8`, entity filter on, differing only
in the columns shown. Retention is measured against `control`; the gate is ≥ 90 %.

| Arm | `cap_strategy` | `similarity_rescale` | damping | artists | retention | edges | sha256 |
|---|---|---|---|---|---|---|---|
| `control` | `pre_symmetrise` | `p99_log_clip` | 0.0 | 74,991 | 100 % | 4,101,222 | `d3016bc06dd9e62de9e6edff3206ca9a3d8366243ca18b2588c0a7063042f57a` |
| `capfix` | `mutual_knn` | `p99_log_clip` | 0.0 | 74,191 | 98.93 % | 898,314 | `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` |
| `rankfix` | `mutual_knn` | `percentile_rank` | 0.0 | 74,193 | 98.94 % | 898,006 | `87d9bf7edfc51fb13ee0fdf6a4216d01df7d3aa7f38b66ea9b7b8c2e7addae05` |
| `d025` | `mutual_knn` | `percentile_rank` | 0.25 | 74,750 | 99.68 % | 1,294,810 | `2811e87d1c900e4ec233317c05143ccaec5a3f0e1fb3c531c04455594bb27e65` |
| `d050` | `mutual_knn` | `percentile_rank` | 0.5 | 74,761 | 99.69 % | 1,419,996 | `6fb52ff8e918cf14da6e4fc6fa52052a66d7bfdb35a7f910460c2c8868c80a20` |
| `d075` | `mutual_knn` | `percentile_rank` | 0.75 | 74,762 | 99.69 % | 1,461,038 | `964342e393690bc30bbf212b3f3fa417891dd6edb27f5324de3ecfc36389c305` |

**All six pass the retention gate.** Artifacts are gitignored; the sha256 is their identity.

**Both byte-identity gates passed.** `control` and `capfix`, rebuilt after Task 14's
log-space change, reproduce their pre-Task-14 hashes exactly — so all six arms are built by
the same code and the Task 0 listening verdict applies to the artifact under consideration.

**Note on damping and density.** The damping arms carry *more* edges than the undamped ones
(1.29–1.46 M vs 0.90 M) and retain more artists. Damping down-weights pairs involving
high-mass artists, changing who appears in whose top-K, so more pairs mutually agree. This
is an effect of the knob under test, not a confound — but it means the damping arms differ
from `rankfix` in density as well as in scores.

## 2. Frozen hub diagnostics

Criterion 3's replacement guard (revised plan §4 amendment 8). The frozen hub set is 751
MBIDs anchored on `control`.

| Arm | frozen hubs present | mean degree over them |
|---|---|---|
| `control` | 751 / 751 | 941.0 |
| `capfix` | 750 / 751 | 29.2 |
| `rankfix` | 751 / 751 | 31.7 |
| `d025` | 751 / 751 | 39.4 |
| `d050` | 751 / 751 | 44.6 |
| `d075` | 751 / 751 | 43.2 |

**No arm's `hubfrac` gain is definitional.** Hub presence is essentially complete
everywhere, and mean hub degree *rises* across the damping arms rather than falling. The
guard does not fire for any arm.

As predicted, mean hub degree reports the cap (max 50) for every capped arm and is
near-constant across arms 3–6 — descriptive, not discriminating.

## 3. Means, FULL router

**Analysis slice, n = 98** (fixed six-way intersection):

| Arm | AA | OC | hubfrac | ceiling | mean CN | length |
|---|---|---|---|---|---|---|
| `control` | 11.6635 | 0.2335 | 0.7187 | 0.4591 | 161.79 | 7.76 |
| `capfix` | 0.7480 | 0.1135 | 0.3620 | 0.3424 | 6.99 | 12.78 |
| `rankfix` | 0.5902 | 0.0977 | 0.3040 | 0.0000 | 6.58 | 12.11 |
| `d025` | 1.2680 | 0.1628 | 0.2602 | 0.0000 | 9.04 | 11.64 |
| `d050` | 0.7411 | 0.1331 | 0.0255 | 0.0000 | 6.07 | 10.07 |
| `d075` | 0.3931 | 0.0784 | 0.0017 | 0.0000 | 4.45 | 10.21 |

**Held-out slice, n = 29:**

| Arm | AA | OC | hubfrac | ceiling |
|---|---|---|---|---|
| `control` | 7.8728 | 0.2302 | 0.6411 | 0.3912 |
| `capfix` | 0.7561 | 0.1171 | 0.3561 | 0.3310 |
| `rankfix` | **0.7630** | 0.1233 | 0.2291 | 0.0000 |
| `d025` | 0.8314 | 0.1224 | 0.2065 | 0.0000 |
| `d050` | 0.4720 | 0.1025 | 0.0043 | 0.0000 |
| `d075` | 0.3330 | 0.0922 | 0.0000 | 0.0000 |

**The mean-CN column is why the AA collapse from `control` to `capfix` is not a quality
regression.** Common neighbours per hop fall from 161.8 to 7.0 — a 23× density drop — so
common-neighbour metrics fall mechanically. Every `mutual_knn` arm inherits this.

**`rankfix`'s held-out AA (0.7630) exceeds `capfix`'s (0.7561)** — the reverse of the
analysis slice. This is finding 2.

## 4. Isolating chain — each arm vs the arm it differs from by one knob

Paired Wilcoxon, Holm-corrected, median deltas.

**Analysis slice, n = 98:**

| Comparison | AA | OC | hubfrac | ceiling | mean CN | length |
|---|---|---|---|---|---|---|
| `capfix` vs `control` | −10.3752 (5.0e−17) | −0.0869 (2.4e−12) | −0.3604 (4.2e−16) | −0.1119 (1.4e−10) | −112.97 (5.0e−17) | +5.00 (5.1e−17) |
| `rankfix` vs `capfix` | −0.0568 (3.2e−4) | −0.0069 (6.7e−3) | −0.0216 (0.0128) | −0.3636 (8.6e−17) | −0.2788 (0.0305) | +0.00 (0.0140) |
| `d025` vs `rankfix` | **+0.3294 (2.0e−11)** | **+0.0325 (7.3e−8)** | +0.0000 (0.319 ns) | +0.0000 (1 ns) | +2.3301 (7.3e−15) | +0.00 (0.319 ns) |
| `d050` vs `rankfix` | +0.0037 (0.418 ns) | +0.0042 (0.138 ns) | −0.2899 (2.0e−15) | +0.0000 (1 ns) | −0.9083 (0.193 ns) | −2.00 (1.6e−9) |
| `d075` vs `rankfix` | −0.0840 (0.0165) | −0.0112 (0.109 ns) | −0.2971 (2.4e−16) | +0.0000 (1 ns) | −2.2637 (1.8e−10) | −1.50 (7.6e−7) |

**Held-out slice, n = 29:**

| Comparison | AA | OC | hubfrac | ceiling |
|---|---|---|---|---|
| `capfix` vs `control` | −4.8263 (8.2e−7) | −0.1099 (0.0129) | −0.2333 (5.6e−5) | −0.0635 (0.177 ns) |
| `rankfix` vs `capfix` | **−0.0205 (1 ns)** | **−0.0002 (1 ns)** | −0.0667 (0.0120) | −0.3333 (1.2e−5) |
| `d025` vs `rankfix` | **+0.1338 (0.853 ns)** | **+0.0050 (1 ns)** | +0.0000 (1 ns) | +0.0000 (1 ns) |
| `d050` vs `rankfix` | −0.0419 (0.507 ns) | −0.0052 (1 ns) | −0.2222 (4.1e−5) | +0.0000 (1 ns) |
| `d075` vs `rankfix` | −0.0916 (0.152 ns) | −0.0233 (0.716 ns) | −0.2222 (4.1e−5) | +0.0000 (1 ns) |

**`d025` was the only arm to pass criteria 1–4 on the analysis slice, and its AA/OC gains
do not reproduce on held-out.** Under the pre-registered rule that is criterion 6 failing.
Note the channel it fails on is the one finding 1 shows to be unstable.

## 5. Package comparison vs `capfix` — the incumbent to beat

Required by revised plan §4 amendment 3: arms 3–6 against `capfix` as *rescale-plus-damping
as a package*, separately from the isolating chain.

**Analysis slice, n = 98:**

| Arm vs `capfix` | AA | OC | hubfrac | ceiling | mean CN | length |
|---|---|---|---|---|---|---|
| `rankfix` | −0.0568 (3.2e−4) | −0.0069 (6.7e−3) | −0.0216 (0.0128) | −0.3636 (8.6e−17) | −0.2788 (0.0305) | +0.00 (0.0140) |
| `d025` | **+0.2842 (5.2e−8)** | **+0.0266 (7.0e−6)** | −0.0896 (4.5e−4) | −0.3636 (8.6e−17) | +1.8016 (2.2e−10) | −1.00 (1.1e−5) |
| `d050` | −0.0215 (0.616 ns) | +0.0046 (0.512 ns) | −0.3604 (2.5e−16) | −0.3636 (8.6e−17) | −0.9641 (0.0295) | −3.00 (3.9e−12) |
| `d075` | −0.1367 (2.1e−5) | −0.0185 (1.1e−3) | −0.3923 (1.6e−16) | −0.3636 (8.6e−17) | −2.5317 (3.0e−11) | −3.00 (3.2e−10) |

**Held-out slice, n = 29:**

| Arm vs `capfix` | AA | OC | hubfrac | ceiling | mean CN | length |
|---|---|---|---|---|---|---|
| `rankfix` | −0.0205 (1 ns) | −0.0002 (1 ns) | **−0.0667 (0.0160)** | **−0.3333 (1.8e−5)** | −1.2222 (0.102 ns) | −1.00 (1.5e−3) |
| `d025` | +0.0828 (0.672 ns) | +0.0091 (0.672 ns) | **−0.1176 (0.0211)** | **−0.3333 (1.8e−5)** | +1.2556 (0.137 ns) | −2.00 (0.0147) |
| `d050` | −0.0768 (0.184 ns) | −0.0140 (0.417 ns) | −0.3750 (1.6e−5) | −0.3333 (1.6e−5) | −3.1222 (1.3e−3) | −3.00 (2.5e−3) |
| `d075` | −0.0766 (0.107 ns) | −0.0160 (0.381 ns) | −0.3750 (1.3e−5) | −0.3333 (1.3e−5) | −3.4000 (5.6e−7) | −3.00 (7.7e−3) |

**`d025` is never worse than `capfix` on any metric on either slice** (finding 4). Its
`hubfrac` and `ceiling_hops` advantages reproduce significantly on both (finding 3); its
overlap advantages are significant on analysis and directionally positive but null on
held-out (finding 1).

## 6. Criterion 3 — per-arm BFS nulls

The v3-family null does not describe a graph with a different degree sequence, so each arm
gets its own. BFS = unweighted shortest path on that arm's graph, same panel slice.

| Arm | FULL `hubfrac` | own BFS null | **excess** | null len | null max-int-deg |
|---|---|---|---|---|---|
| `control` | 0.7187 | 0.4540 | **+0.265** | 4.75 | 4,751 |
| `capfix` | 0.3620 | 0.0336 | **+0.328** | 8.40 | 34 |
| `rankfix` | 0.3040 | 0.0330 | +0.271 | 8.38 | 34 |
| `d025` | 0.2602 | 0.0306 | +0.230 | 7.41 | 41 |
| `d050` | 0.0255 | 0.0215 | **+0.004** | 7.22 | 44 |
| `d075` | 0.0017 | 0.0195 | −0.018 | 7.17 | 44 |

**The cap fix reduces hub traversal without reducing hub-*seeking*.** `capfix` roughly
halves absolute `hubfrac`, but its own null falls further still — capping degree removes
hub edges wholesale — so measured against what its graph makes available, its router seeks
hubs *slightly more* than `control`'s does. Against the old v3 null, `capfix` would have
looked like it solved hub-seeking outright. It did not; it changed the graph so there are
fewer hubs to reach. That is a real improvement in output and a different thing from the
router behaving better.

**`d050` is the only arm where the excess essentially vanishes** — its router routes almost
exactly like a blind shortest-path walker on its own graph. `d075` overshoots below its
null (defined as passing criterion 3, per the pre-registration; guarded by criteria 1–2,
which it fails).

This is also the first honest measurement bearing on adjudication §6 claim 35: the excess
is not the popularity term, and it survives the cap fix nearly intact.

## 7. `w_jump = 0` router, analysis slice

| Arm | AA | OC | hubfrac | ceiling | length |
|---|---|---|---|---|---|
| `control` | 9.6244 | 0.2769 | 0.6322 | 0.438 | 7.1 |
| `capfix` | 0.6258 | 0.1001 | 0.3450 | 0.362 | 12.4 |
| `rankfix` | 0.7100 | 0.1124 | 0.3937 | 0.000 | 12.5 |
| `d025` | 1.2292 | 0.1550 | 0.3901 | 0.000 | 12.0 |
| `d050` | 0.5434 | 0.1363 | 0.0295 | 0.000 | 12.6 |
| `d075` | 0.2618 | 0.0866 | 0.0031 | 0.000 | 12.7 |

**Removing the popularity term *raises* `hubfrac` on the rank arms** (`rankfix`
0.3040 → 0.3937, `d025` 0.2602 → 0.3901) while *lowering* it on `control`
(0.7187 → 0.6322). The popularity channel works in opposite directions depending on the
rescale — unexplained, and recorded as such.

## 8. Panel resolution

| Arm | panel pairs resolved | unresolvable |
|---|---|---|
| `control` | 100 | — |
| `capfix`, `rankfix` | 98 | `51711e2f-…` (obscure), `0bb88ccf-…` (popularity-weighted) |
| `d025`, `d050`, `d075` | 99 | `51711e2f-…` (obscure) |

Fixed six-way intersection: **n = 98** (analysis), **n = 29** (held-out). Every paired test
above runs on the fixed set, so medians are comparable across arms.

## 9. Reproduction

Artifacts `builder/scratch/graph-t15-<arm>.bin`, each with a manifest sidecar recording
config, git commit, elapsed time and sha256. Built at commit `f7583b8` from
`builder/scratch/graph-archive`.

Routing: `api/eval/run_baseline.py <graph> <label> [--held-out]`, which freezes the hub set
from `api/eval/hub-nodes-control.json` (committed), resolves the panel by MBID, runs the
FULL and `w_jump = 0` routers, and writes per-pair metric vectors to
`api/eval/results-<label>.json`. Paired tests use `api/eval/stats.py`
(`paired_comparison`, `holm_correct`).

Per-arm BFS nulls use `bfs_shortest_path` from `api/src/artistpath_api/evaluation.py` over
the same slice and the same frozen hub set.
