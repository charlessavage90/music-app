# Track 2F — the similarity-ceiling toll as a dose-response ladder

**Role: ACTIVE analysis record. Owns its figures.** Nothing here restates a figure from
`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`, the Phase 1 log, the Track 2
arm-scorer directory, or `../2026-07-23-track2-toll-calibration/`. Those are cited.

**Governing document:**
[`docs/superpowers/specs/2026-07-25-track2f-toll-full-strength-preregistration.md`](../../../docs/superpowers/specs/2026-07-25-track2f-toll-full-strength-preregistration.md),
committed at `8074a32` **before any arm ran**.

Artifact `4cb84ef9…b061dc8` — the same one Track 2 ran on, **unchanged**. No rebuild, no
shipped code touched, nothing adopted.

## What was asked

Track 2 amendment **A17(b)**: the ceiling toll ran at `w_sim · (1 − toll_s)`, which yields
§1.4's intended 7.5× / 30× `w_hop` only at `w_sim` 3.0. R1's fallback `W = A7` carries 1.5,
so `T1a` and `T1b` ran at **3.75× and 15×** — half strength — and the intended top was never
tested. This runs the mechanism at full strength and past it, to its asymptote.

## Result in one line

**`TFR0` — null on the primary criterion, at `M* = −0.198` against a −0.25 continuation
trigger and `C1`'s −1.0 bar. But the ladder is monotone, it saturates exactly at §1.4's
intended top, its corner genuinely bounds it, and the winning arm beats production on
every other criterion.**

## Files

| File | What it is |
|---|---|
| `toll_ladder.py` | The seven ladder arms as data, plus `P`/`A0`/`A7`. Prints its own factor table. Magnitudes in multiples of `w_hop`, never `toll_s` — the A17(b) fix. |
| `paths.json` | 10 arms × 12 pairs × 21 depths, snapshots only. Zero guard-infeasible cells. |
| `fame.json` | A11 fame resolution (Wikipedia pageviews, unmatched → 0). 392/397 = 98.7 % matched. |
| `scores.json` | `C1`–`C4`, the isolating one-column contrasts, and the `C5`/A14/F5 diagnostics. |
| `diagnostics.py` / `diagnostics.json` | `TF-D1` (ceiling-hop usage) and `TF-D2` (path length). |

Reproduce, from `api/`:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-23-track2-sweep/verify_mirror.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-07-24-track2-arm-scorer/run_arms.py \
    --arms-module ../builder/analysis/2026-07-25-track2f-toll-ladder/toll_ladder.py \
    --inherit-drops ../builder/analysis/2026-07-24-track2-arm-scorer/paths.json \
    --out ../builder/analysis/2026-07-25-track2f-toll-ladder/paths.json
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-07-24-track2-arm-scorer/fame.py \
    --paths ../builder/analysis/2026-07-25-track2f-toll-ladder/paths.json \
    --out   ../builder/analysis/2026-07-25-track2f-toll-ladder/fame.json
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-07-24-track2-arm-scorer/score.py \
    --paths ../builder/analysis/2026-07-25-track2f-toll-ladder/paths.json \
    --fame  ../builder/analysis/2026-07-25-track2f-toll-ladder/fame.json \
    --arms-module ../builder/analysis/2026-07-25-track2f-toll-ladder/toll_ladder.py \
    --out   ../builder/analysis/2026-07-25-track2f-toll-ladder/scores.json
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-25-track2f-toll-ladder/diagnostics.py
```

**Nothing here is imported by shipped code, by design** — it is offline analysis.
`toll_ladder.py` is loaded **by path** through `--arms-module`, so a grep for the module
name finds no inbound import; the commands above are its only entry point, which is why
they are written out in full rather than abbreviated.

## The harness change, and the proof it changed nothing

`mirror.py` gained **`toll_hops`** (toll = `toll_hops × w_hop`), additive and default-off.
It exists because `toll_s` is `w_sim`-dependent, which is the root cause of A17(b): one
`toll_s` means two different tolls under two different `W`. `toll_hops` names its own basis,
per the currency-in-the-name convention.

Three independent non-regression proofs, all passed **before anything was scored**:

1. **`verify_mirror.py`: BYTE-IDENTICAL on all 212 cells.** Production behaviour untouched.
2. **The reproduction gate.** `P`, `A0`, `A7`, `T1a_rpt` and `T1b_rpt` are **byte-identical
   to the committed `paths_stage2.json`**, on node ids *and* on names. The Track 2 figures
   are reproducible from the modified script, so every number below is directly comparable
   to `scores_stage2.json`.
3. The two reproduction arms deliberately keep the **original `toll_s` specification** —
   the two forms are not bit-identical at the same nominal magnitude
   (`1.5*(1-0.80)` = 0.29999999999999993 against `15*0.02` = 0.30000000000000004), so an arm
   whose job is reproduction must be specified exactly as the run it reproduces.

## The ladder — gating criteria

`C1`–`C4` are Track 2 §2.2's, cited unchanged, scored by the same code. `P` = production.

| arm | toll (× `w_hop`) | C1 mean ΔF | C1 frac | C2 | C3 drop | C4 int | cov % | gates |
|---|---|---|---|---|---|---|---|---|
| `P` | — | 0.000 | 0.00 | **4/8** | 0.164 | 5.38 | 96.4 | (baseline) |
| `A0` | — | 0.000 | 0.00 | 4/8 | 0.164 | 5.38 | 96.4 | — |
| `A7` (= W) | 0 | −0.053 | 0.54 | 1/8 | 0.066 | 3.58 | 95.1 | none |
| `T1a_rpt` | 3.75 | −0.052 | 0.46 | 2/8 | −0.066 | 3.79 | 94.8 | none |
| `TF1` | **7.5** | −0.139 | 0.67 | **5/8** ✓ | 0.022 | 5.08 ✓ | 96.8 | C2, C4 |
| `T1b_rpt` | 15 | −0.177 | 0.71 | 3/8 | 0.092 | 6.54 ✓ | 97.5 | C4 |
| **`TF2`** | **30** | **−0.198** | **0.83** | **5/8** ✓ | **0.232** | **7.12** ✓ | **97.7** | **C2, C4** |
| `TF3` | 60 | −0.198 | 0.83 | 5/8 ✓ | 0.193 | 7.12 ✓ | 97.7 | C2, C4 |
| `TF4` | 120 | −0.198 | 0.83 | 5/8 ✓ | 0.193 | 7.12 ✓ | 97.7 | C2, C4 |
| `TFX` | 7,500 | −0.198 | 0.83 | 5/8 ✓ | 0.232 | 7.12 ✓ | 97.7 | C2, C4 |

`C1` requires ≤ −1.0 at ≥ 75 % negative; `C3` requires a drop ≥ 0.5. **No arm passes `C1` or
`C3`, so nothing is adoptable and no threshold moves.**

### Isolating one-column contrasts (each arm vs the arm one magnitude below)

| arm | vs | mean ΔF | reading |
|---|---|---|---|
| `T1a_rpt` | `A7` | **+0.001** | inert at 3.75×, exactly as Track 2 recorded |
| `TF1` | `A7` | **−0.086** | the largest single step on the ladder |
| `T1b_rpt` | `TF1` | −0.038 | |
| `TF2` | `T1b_rpt` | −0.022 | the last step that does anything |
| `TF3` | `TF2` | **0.000** | |
| `TF4` | `TF3` | **0.000** | |
| `TFX` | `TF4` | **0.000** | |

## `TF-D1` — ceiling-hop usage, and why the ladder saturates

The direct mechanism measurement: what fraction of the hops a path actually takes are edges
whose stored similarity is exactly 1.0. Analysis pairs, all snapshot depths.

| arm | ceiling hops | of total | % |
|---|---|---|---|
| `P` | 334 | 391 | **85.42 %** |
| `A0` | 333 | 390 | 85.38 % |
| `A7` | 251 | 303 | 82.84 % |
| `T1a_rpt` | 207 | 316 | 65.51 % |
| `TF1` | 175 | 375 | 46.67 % |
| `T1b_rpt` | 148 | 484 | 30.58 % |
| `TF2` | 144 | 499 | **28.86 %** |
| `TF3` | 144 | 499 | 28.86 % |
| `TF4` | 144 | 499 | 28.86 % |
| `TFX` | 144 | 499 | **28.86 %** |

**This is the result that explains every other one.** Production takes **85 % of its hops on
ceiling edges**. The toll drives that down monotonically to **28.86 %** — and then it stops
dead. At 7,500 × `w_hop` the router is paying 150 cost units rather than detour, and it
**still takes those 144 hops**, because there is no alternative to take: those edges are
structurally forced.

**This is §1's bound 2 confirmed to the hop.** The toll-calibration README's Q4 records that
eight of the twenty-four pre-registered endpoints are *fully* saturated — all 50 neighbours at
exactly 1.0 — so their first hop is a ceiling edge at any price. 144 forced hops over 72
scored cells is **exactly 2.0 per path**: one leaving a saturated endpoint, one arriving at
another.

**So the ladder's limit is set by graph structure, not by price.** No router-side knob can go
further, and 30× — §1.4's intended top — is exactly where it lands.

## `TF-D2` — path length

Mean / max interior count at d ≥ 10: `P` 5.38 / 11; `TF2` 7.12 / 14; `TFX` 7.12 / 14.
`TF2` is **1.32×** production's mean, below the 2× reporting trigger (the author's, stated as
such — WHAT-GOOD value 3 records an attention ceiling and holds **no** threshold). Longer
paths carrying more interiors is what `C4` asks for. **Whether 14 stops still feels like a
journey is a use-the-app question and is queued as one.**

## `TF-D3` — coverage and the A11 guard

Coverage rises with toll strength and is highest at the top (`TF2`–`TFX` at 97.7 %, against
`P`'s 96.4 %). Two unmatched-but-potentially-notable artists were flagged graph-wide
(`CROOVE`, `M2U`, one non-English article each). **No arm's `C2` pass rests on a flagged
interior** — `rests_only_on_flagged_notable` is empty for every arm — so A11's d15/d20 guard
is discharged without needing the owner's glance.

**Zero blank-named interiors**, so the pre-registration §0 non-constant did not fire and
A13/A18's uniform cell drop was never invoked. **Zero guard-infeasible cells**, as predicted:
a toll re-prices edges and never removes them, so reachability is unchanged.

## `TFR4` — the bound check, and it holds

Track 2's corner arm `X` failed to bound its family (A17(c)), which is why this check was
pre-registered. Here:

- **Monotone from 7.5× upward**, without exception. The single inversion is `T1a_rpt` vs
  `A7` (−0.0518 against −0.0525, a gap of 0.0007) at the magnitude Track 2 already recorded
  as inert.
- **`TFX` is tied-lowest** on `C1` and identical to `TF2` on `TF-D1`, `C2` and `C4`.

**So the corner does bound the family, and the null may be stated at mechanism strength:**
*tolling ceiling edges cannot move the primary outcome further than −0.198, at any price.*
That is a stronger and cleaner statement than Track 2 was entitled to make about its own
null, and it is the difference a working bound makes.

## `C5` — the d0 inspection

d0 paths change on **5 of 8 pairs** for `TF2` (and identically for `TF3`/`TF4`/`TFX`), several
with zero interior overlap. Listed in `scores.json` under `diagnostics.<arm>.C5_d0_changes`.
Per A14 the question is whether d0 fame still **tracks the endpoints** (WGLL value 9). It
does, on inspection: `Madonna → Pet Shop Boys → Kate Bush → Joni Mitchell → Tom Waits → Bob
Dylan` and `Miles Davis → Nat King Cole → Etta James → Al Green → Bobby Womack → Little Dragon
→ Hot Chip → Klaxons → Justice → Daft Punk` are well-known throughout. **This is inspection,
not a pass** — coherence is the listening test's call, not a metric's, and no listen was run.

## What this does and does not license

**Does:** the pre-registered `TFR0` read — the ceiling's **cheapness** is not what holds paths
in famous territory, and no router-side toll goes further. Recommending against spending a
rebuild *on the cheapness hypothesis*.

**Does not:** "the p99 ceiling is fine." §1 bound 1 is verified in the builder
(`pipeline.py` stores `min(1.0, …)`, so the artifact retains no information distinguishing
saturated edges): **the ordering half of the ceiling hypothesis is untestable router-side and
is untouched by this null.** `TF-D1` now gives it a measured target — 28.86 % of hops that no
price can avoid, and 85 % in production today.

**Also does not:** address F2's "progressively" clause. Every arm here is depth-independent by
construction, and `C3` — the depth gradient — fails on all of them. `TF2` improves it
(0.232 against production's 0.164) but the bar is 0.5. The depth carrier remains an open
problem, and the only depth-graduated device in the cost function is dead (Track 2 stage 2).
