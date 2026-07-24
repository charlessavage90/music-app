# A0-gate review — floor arm-invariance and the d1–d5 asymmetry

**Run 2026-07-23 by the `ml-graph-analyst` subagent, reviewing the step-4 A0-vs-P result
before the owner picks between the three options in the repair+retune execution log
("Track 2 → Steps 2–4 executed"). This README owns every figure below.**

Artifact: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted at the top of
every script. N = 74,193, E = 898,006 directed CSR entries.

**Nothing here is scored.** No fame proxy is touched, no ΔF, no C1/C2/C3 outcome. Every
quantity is mechanical: floor-term firing during Dijkstra relaxation, path identity,
in-graph raw popularity of path interiors. In-graph popularity is **not** fame (Phase 1 log
§2.11) and none of these numbers can stand in for a sweep result.

## Files

| File | What it does |
|---|---|
| `floor_asymmetry.py` | Parts 1–3: floor arithmetic per pair; an arm-independent upper bound on firing; six routed arms (three floor-ON/floor-OFF one-knob twins) walked to d20 |
| `trajectory_carryover.py` | Reads `raw_results.json`; asks whether floor-induced differences at d0–d2 survive into the scored window |
| `second_slice.py` | The same twin contrast under a **different** deterministic victim policy (least-popular interior), as a stability check |
| `raw_results.json` | Every walk, every depth, written by `floor_asymmetry.py` |

Run from `api/`:

```bash
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
  ../builder/analysis/2026-07-23-track2-a0-review/floor_asymmetry.py
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
  ../builder/analysis/2026-07-23-track2-a0-review/trajectory_carryover.py
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \
  ../builder/analysis/2026-07-23-track2-a0-review/second_slice.py
```

Total runtime under a minute; a single `find_path_mirror` call on these pairs examines
~60 k relaxations and takes ~10 ms.

## Arms routed

All carry guard G. `P` and `A0` are the pre-registered anchors. **`A6r` and `Xr` are not
pre-registered arms** — they are floor-ON counterfactual twins of A6 and X, built here
solely to measure what a raw floor would do inside a diving arm. They are diagnostics and
are not candidates for anything.

| Label | J-cur | `w_jump` | `w_sim` | floor | Note |
|---|---|---|---|---|---|
| `P` | raw | 1.0 | 3.0 | raw, `w_floor` 1.0 | production |
| `A0` | raw | 1.0 | 3.0 | off | pre-registered anchor |
| `A6r` | raw | 0.3 | 1.5 | raw, `w_floor` 1.0 | diagnostic twin |
| `A6` | raw | 0.3 | 1.5 | off | pre-registered factorial cell |
| `Xr` | pctl | 0.0 | 1.5 | raw, `w_floor` 1.0 | diagnostic twin |
| `X` | pctl | 0.0 | 1.5 | off | pre-registered corner |

## 1. The relaxed raw floor by depth — arithmetic

`floor_raw(d) = max(0, min(pop_raw[s], pop_raw[t]) − 0.15·d)` under an all-`known` walk
(`ApiConfig.floor_relax_known`, cited not restated). The value depends only on the two
endpoints and the bypass counts — **not** on which artists were bypassed.

| pair | base_raw | floor@d5 | floor@d6 | floor@d7 | first zero depth |
|---|---|---|---|---|---|
| Miles Davis → Daft Punk | 0.6726 | 0 | 0 | 0 | 5 |
| The Shins → Wishbone Ash | 0.4744 | 0 | 0 | 0 | 4 |
| Metallica → Taylor Swift | 0.7199 | 0 | 0 | 0 | 5 |
| Radiohead → The Beatles | 0.9982 | 0.2482 | **0.0982** | 0 | 7 |
| Muse → Coldplay | 0.9313 | 0.1813 | **0.0313** | 0 | 7 |
| Madonna → Bob Dylan | 0.8286 | 0.0786 | 0 | 0 | 6 |
| Pink Floyd → Aphex Twin | 0.9307 | 0.1807 | **0.0307** | 0 | 7 |
| Nirvana → CROOVE | 0.4571 | 0 | 0 | 0 | 4 |
| Arctic Monkeys → Johnny Cash | 0.9285 | 0.1785 | **0.0285** | 0 | 7 |
| Michael Jackson → Gorillaz | 0.9396 | 0.1896 | **0.0396** | 0 | 7 |
| System of a Down → R.E.M. | 0.9280 | 0.1780 | **0.0280** | 0 | 7 |
| The Rolling Stones → Linkin Park | 0.9403 | 0.1903 | **0.0403** | 0 | 7 |

**7 of 12 pairs still carry a strictly positive raw floor at d6.** The unconditional
arithmetic bound is **d7**, not d6.

Two currencies the all-`known` figure does not cover:

- **all-`dislike`** (`floor_relax_dislike = 0.08`): the largest base floor gives
  `ceil(0.9982 / 0.08) = 13`, so the raw floor is alive through **d12** on that pair.
- **any mix**: 0.08 is the smaller per-bypass step, so **d13** is the universal
  all-mixes bound on this pair set.

Percentile floor (FL arms, relax 0.05 per amendment A2): base percentile is ≥ 0.9895 on ten
of twelve pairs, so `pctl_floor(d5) ≈ 0.74–0.75` and `pctl_floor(d20) = 0` on **all twelve**.

## 2. Arm-independent upper bound on floor-term firing

Fraction of all 898,006 directed CSR entries whose **head** sits below `floor_raw(d)`. No
arm can exceed this at that depth, whatever it routes through.

| pair | d0 | d1 | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|---|
| Miles Davis → Daft Punk | 97.44 | 84.02 | 40.77 | 7.25 | 0.49 | 0 | 0 | 0 |
| The Shins → Wishbone Ash | 73.51 | 26.37 | 3.40 | 0.28 | 0 | 0 | 0 | 0 |
| Metallica → Taylor Swift | 98.52 | 90.88 | 56.81 | 14.09 | 1.32 | 0 | 0 | 0 |
| Radiohead → The Beatles | 99.99 | 99.68 | 98.13 | 88.13 | 49.25 | **10.44** | **0.914** | 0 |
| Muse → Coldplay | 99.94 | 99.23 | 95.86 | 75.18 | 28.26 | 3.75 | 0.315 | 0 |
| Madonna → Bob Dylan | 99.56 | 97.64 | 85.08 | 42.72 | 7.95 | 0.62 | 0 | 0 |
| Pink Floyd → Aphex Twin | 99.94 | 99.22 | 95.82 | 75.04 | 28.09 | 3.72 | 0.311 | 0 |
| Nirvana → CROOVE | 68.74 | 21.94 | 2.53 | 0.12 | 0 | 0 | 0 | 0 |
| Arctic Monkeys → Johnny Cash | 99.93 | 99.21 | 95.69 | 74.51 | 27.57 | 3.60 | 0.304 | 0 |
| Michael Jackson → Gorillaz | 99.96 | 99.32 | 96.23 | 77.04 | 30.56 | 4.33 | 0.349 | 0 |
| System of a Down → R.E.M. | 99.92 | 99.21 | 95.63 | 74.36 | 27.44 | 3.58 | 0.304 | 0 |
| The Rolling Stones → Linkin Park | 99.96 | 99.33 | 96.25 | 77.20 | 30.82 | 4.37 | 0.351 | 0 |

Units: % of directed edges. Read the d6 column against §3's measured zeros.

## 3. Measured firing rate, floor-ON arms, pooled over 12 pairs

| depth | P | A6r | Xr |
|---|---|---|---|
| d0 | 370,247 / 722,312 = **51.259 %** | 356,321 / 708,022 = 50.326 % | 364,589 / 708,459 = 51.462 % |
| d1 | 109,077 / 763,151 = 14.293 % | 113,984 / 781,236 = 14.590 % | 125,179 / 798,062 = **15.685 %** |
| d2 | 16,411 / 774,619 = 2.119 % | 18,315 / 799,650 = 2.290 % | 28,770 / 842,422 = **3.415 %** |
| d3 | 972 / 784,909 = 0.124 % | 1,126 / 808,438 = 0.139 % | 3,884 / 877,082 = **0.443 %** |
| d4 | 37 / 786,577 = 0.005 % | 55 / 813,923 = 0.007 % | 552 / 883,761 = **0.062 %** |
| d5 | 8 / 788,361 = 0.001 % | 13 / 817,861 = 0.002 % | 30 / 891,276 = 0.003 % |
| d6 | **0** / 791,702 | **0** / 822,517 | **0** / 889,825 |
| d7 | **0** / 792,241 | **0** / 827,941 | **0** / 888,931 |

P's column reproduces the sweep directory's step-4 figures exactly, which is an independent
re-run of that measurement. Per-pair, the only pairs firing at all at d5 are the six with
base floor ≥ 0.9280; every pair fires zero at d6 and d7 in all three arms.

## 4. Path-level floor exposure — the asymmetry Q2 asks about

For each arm's chosen path: interiors strictly below `floor_raw(d)`, the largest single
shortfall, and the floor cost the path would pay (`Σ max(0, floor − pop_raw_v)` over every
node after the source). `w_hop = 0.02`, so divide by 0.02 for hop units.

| arm | depth | interiors | below floor | max shortfall | mean path floor cost | in w_hop |
|---|---|---|---|---|---|---|
| P | d0 | 35 | 4 | 0.0518 | 0.0086 | 0.43 |
| A0 | d0 | 34 | 4 | 0.0518 | 0.0094 | 0.47 |
| A6r | d0 | 31 | 2 | 0.0518 | 0.0055 | 0.28 |
| A6 | d0 | 31 | 4 | 0.0518 | 0.0094 | 0.47 |
| Xr | d0 | 27 | 2 | 0.0518 | 0.0055 | 0.28 |
| **X** | **d0** | 27 | **12** | **0.3701** | **0.2298** | **11.5** |
| P | d1 | 38 | 0 | 0 | 0 | 0 |
| **X** | **d1** | 28 | **9** | **0.2264** | **0.0905** | **4.5** |
| P | d2 | 38 | 0 | 0 | 0 | 0 |
| X | d2 | 28 | 1 | 0.0443 | 0.0037 | 0.19 |
| every arm | d3–d7 | — | **0** | **0** | **0** | 0 |

X's d0 shadow floor cost is **26.7×** P's. Its largest single-hop shortfall, 0.3701, would
cost 18.5 `w_hop` — between the two pre-registered toll magnitudes (7.5× and 30× `w_hop`).
From **d3 onward the exposure is exactly zero for every arm tested, including X.**

Median-of-cell-medians of interior raw popularity, as evidence that X does in fact dive
(structural only, *not* a fame statement): d0 — P 0.9095, A0 0.9095, X 0.6516; d20 —
P 0.8397, A6 0.8303, X 0.7717.

## 5. Cells where the floor changes the path — one-knob twins, both slices

Slice 1 = pre-registered victim policy (most-popular interior). Slice 2 = least-popular
interior, an off-protocol stability check.

| depth | P vs A0 (s1) | (s2) | A6r vs A6 (s1) | (s2) | Xr vs X (s1) | (s2) |
|---|---|---|---|---|---|---|
| d0 | 1/12 | 1/12 | 2/12 | 2/12 | 9/12 | 9/12 |
| d1 | 0/12 | 1/12 | 2/12 | 1/12 | 9/12 | 8/12 |
| d2 | 0/12 | 1/12 | 2/12 | 0/12 | 9/12 | 9/12 |
| d3 | 0/12 | 0/12 | 1/12 | 0/12 | 5/12 | 9/12 |
| d5 | 0/12 | 0/12 | 1/12 | 0/12 | 5/12 | 7/12 |
| d7 | 0/12 | 0/12 | 0/12 | 0/12 | 5/12 | 4/12 |
| **d10** | **0/12** | **0/12** | 1/12 | 0/12 | **5/12** | **4/12** |
| **d15** | **0/12** | **0/12** | 1/12 | 0/12 | **2/12** | **2/12** |
| **d20** | **0/12** | **0/12** | 1/12 | 0/12 | **2/12** | **2/12** |

The floor term is identically **zero** at every depth ≥ 7, yet the Xr/X twins still differ
there. The difference is **inherited through the bypass trajectory**: a path the floor
changed at d0–d2 changes which artist is bypassed, and the walks never re-converge. The two
pairs still differing at d20 are **Radiohead → The Beatles and Muse → Coldplay on both
slices** — the two direct-edge (guard-G) pairs, where the walk enumerates single
intermediaries and one different first pick permanently reorders the enumeration.

Stability: the P/A0 result (zero carry-over past d2) and the Xr/X result (2 of 12 pairs at
d20, same two pairs) reproduce on both slices. **A6r/A6's carry-over does not** — 1/12 at
d9–d20 on slice 1, 0/12 from d2 on slice 2. Treat the A6 family figure as unstable.

## 6. Incidental facts worth having

- **No walk terminated early.** All 6 arms × 12 pairs produced 21 depths. Analyst **D7**
  (guard-infeasible cells) did not fire anywhere in 1,512 routed calls across two slices.
- The d0 divergent cell of the step-4 run reproduces exactly, and two more appear in the
  diagnostic twins: `A6r/A6` on Pink Floyd → Aphex Twin (Gorillaz vs Depeche Mode as the
  first interior), and nine `Xr/X` cells at d0.
- `MirrorContext.jump_scale_pctl` on this artifact = **0.536495** (amendment A3's
  mean-matching ratio, computed from the artifact rather than stored).
