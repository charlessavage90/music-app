# `DRP-` stage 3a — the instruments (#200). Seam A.

**Role: COMPLETE at Seam A, and the owner of every figure below.** Governing document:
[`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../../../docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8 stage 3a, executed from the body. Execution log:
[`docs/superpowers/2026-09-27-drp-stage3a-execution-log.md`](../../../docs/superpowers/2026-09-27-drp-stage3a-execution-log.md).

**What this is:** the instruments and gates that must hold before any arm is swept. **No arm was
routed.** The only routing here is on A0 (today's map at today's weights) for `DRP-G1`, `N_noise` and
`DRP-G10`; `DRP-G1r` at the ramp 0.015, outside the lattice, which keeps a count only; and
`DRP-G10`'s ceiling checks on both maps, which keep pass/fail only. **No interior artist is named in
any committed file** (§8 sealing); per-journey outputs hold node ids, and the A0 random-press
journeys sit outside the repository (sha below).

## Gate outcomes — the Seam-A set (§7 *gated*)

| gate | plain sentence (§6) | outcome | output |
|---|---|---|---|
| `DRP-G1` | *our measuring harness reproduces a result a different script already committed on today's map* | **PASS**: 80 of 80 pairs identical on every printed field | `drp_g1.json` |
| `DRP-G1r` | *the same check can see a change in the ramp* | **fired**: diverged on 78 of 80 pairs | `drp_g1r.json` |
| `DRP-G2` | *our rebuild of today's map is today's map* | **PASS** — node order, offsets, neighbours, score bytes, `pop_raw`, raw `fame_lb` all equal; the rebuild also serialises **byte-identical** to `graph-lba-a6.bin` (sha `28311d81…`) | `drp_g2.json` |
| `DRP-G2` red | *the rebuild check can see a change* | **fired** (`union_top_j` 49 differs) | `drp_g2_red.json` |
| `DRP-G3` | *the extra-exits map is today's map plus the extra connections, and nothing else* | **PASS**, 0 violations; the independent re-derivation matches edge for edge and byte for byte | `drp_g3.json` |
| `DRP-G3` red | one added edge dropped; one added score moved one float32 ulp | **both fired** (1 violation each, condition (i)) | `drp_g3.json` |
| `DRP-G6` | *today's app, pressed two arbitrary ways, differs so much that the design cannot see a five-point change* | **PASS** (did not fire): `N_noise` = 0.015 in both famous strata | `drp_noise.json` |
| `DRP-G7` | *the obscurity floor contributes nothing from press 7 on* | **PASS**: zero at `k` = 7 for every drawn pair (all strata and `DRP-C8`); max `pop_raw` 1.0; `floor_relax_known` 0.15 | `drp_noise.json` |
| `DRP-G10` | *the headroom figure really is the lowest possible ceiling* | **PASS** on 320 of 320 (pair, map) | `drp_headroom.json` |

## Measured

**The `DRP-S1` artifact** — `C:\unsung-fast\drp-stage3a\graph-drp-s1.bin`,
sha256 `418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f` (39,841,313 bytes; sidecar
beside it). Built from the capture `capture.pkl`, sha256 recorded in `drp_s1_build.json`. **Not for
production** (§8: a shipping build rule owes `DRP-X4`).

**`DRP-C10`, structural half** (`drp_g3.json`): 874 centres; 7,998 added edges; 817 centres gained
at least one; 205 candidates skipped at the 60 bound; 3,855 distinct partners, added edges per
partner median 1, p90 4, max 37; partners' `fame_lb_pctl` median 0.781 (p10 0.396, p90 0.886), 593
below 0.5. **Top-1 % artists with no neighbour below 0.9: 381 on lba-a6** (reproducing trim-supply's
and graph-descriptives §1 A's post-trim count) **and 2 on `DRP-S1`.** The per-pair frontier count
needs the band journeys and is computed at 3c.

**`N_noise`** (`drp_noise.json`; §5's formula, bootstrap pinned as `DRP-C1`(2)'s):

| stratum | pairs with all four band depths feasible under both seeds | median Δ | `U` | `N_noise` |
|---|---|---|---|---|
| `DRP-T1` | 40 | −0.00002 | 0.00027 | **0.015** |
| `DRP-T2` | 39 | +0.00017 | 0.00122 | **0.015** |

As §5 and `DRP-AM1-F1` expected: `U` is more than an order of magnitude below the carried floor, so
the operative `N_noise` is `CRE-`'s 0.015.

**`DRP-C11` headroom, `b₀`** (`drp_headroom.json`; *the lowest the most famous artist in the middle
of this journey could possibly be, on this map, whatever the router does*):

| map | stratum | finite | min | p10 | median | p90 | max |
|---|---|---|---|---|---|---|---|
| `DRP-S0` | `DRP-T1` | 40/40 | 0.179 | 0.754 | 0.962 | 0.988 | 0.994 |
| `DRP-S0` | `DRP-T2` | 40/40 | 0.116 | 0.213 | 0.612 | 0.924 | 0.946 |
| `DRP-S0` | `DRP-MID` | 40/40 | 0.080 | 0.128 | 0.237 | 0.435 | 0.564 |
| `DRP-S0` | `DRP-C8` | 40/40 | 0.098 | 0.420 | 0.821 | 0.952 | 0.988 |
| `DRP-S1` | `DRP-T1` | 40/40 | 0.133 | 0.435 | 0.659 | 0.837 | 0.883 |
| `DRP-S1` | `DRP-T2` | 40/40 | 0.116 | 0.213 | 0.612 | 0.924 | 0.946 |
| `DRP-S1` | `DRP-MID` | 40/40 | 0.080 | 0.128 | 0.237 | 0.435 | 0.564 |
| `DRP-S1` | `DRP-C8` | 40/40 | 0.098 | 0.202 | 0.673 | 0.894 | 0.951 |

Per pair, `DRP-S1` against `DRP-S0`: `DRP-T1` lower on 37, identical on 3; `DRP-T2` and `DRP-MID`
identical on all 40; `DRP-C8` lower on 16, identical on 24; **higher on none** (adding edges can only
lower a bottleneck, and nothing contradicted that).

## What I infer from it (inference, labelled)

- **The instruments are sound enough to sweep with.** Every Seam-A gate passed and every red control
  that exists fired. The one place the harness could have drifted from the committed record — the
  router and the victim chain — is what `DRP-G1` checks.
- **The extra connections open room on the most-famous pairs and nowhere else.** On today's map the
  typical most-famous pair could not, on any route, keep its most famous middle artist below about the
  96th percentile. With the extra connections that bound falls to about the 66th. For the next tier
  and the middle of the map nothing changes, because only the top 1 % were given connections. **This
  is what the map allows, not what the router will pick** — whether today's pull, a stronger one or a
  ceiling takes those routes is exactly what 3b and 3c measure.
- **The next-tier pairs already have room on today's map** (typical bound near the 61st percentile).
  So if pricing moves anything on famous pairs, the next tier is where it would show, which is what
  §2.5's prior already said.

## Weakest link

`DRP-C11` is a bound on the **most famous** middle artist, not the typical one (`DRP-AM2` item 2), and
it says nothing about whether a route through those artists hangs together (§10). A reader who takes
"room to go lower" as "the journeys will be better" has read past both limits.

## Reproduce

```bash
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-27-drp-stage3a/drp_pairs.py
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-27-drp-stage3a/drp_g1.py g1    # and g1r
cd builder && PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-09-27-drp-stage3a/drp_build_s1.py build  # and red
cd builder && PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-09-27-drp-stage3a/drp_g3.py
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-27-drp-stage3a/drp_noise.py
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-27-drp-stage3a/drp_headroom.py
```

Outside the repository (`C:\unsung-fast\drp-stage3a\`): `graph-drp-s1.bin` (sha above),
`capture.pkl` (sha in `drp_s1_build.json`), `drp_noise_journeys.json` (sha256
`3d71ed00d76ccfd8b92b67ec50fe62941ccbb26775aac79c24834b6bedb802d1`), and the run logs.
