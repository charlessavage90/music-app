# `DRP-` stage 3c — the `DRP-S1` row (#200). Seam C.

**Role: COMPLETE at Seam C, and the owner of the per-cell file shas, gate outcomes and frontier-count
file below.** Governing document:
[`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../../../docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8 stage 3c, executed from the body. Execution log:
[`docs/superpowers/2026-09-28-drp-stage3c-execution-log.md`](../../../docs/superpowers/2026-09-28-drp-stage3c-execution-log.md).

**What this is:** the four cells on the extra-exits map, swept, with their gates, plus `DRP-C10`'s
per-pair frontier count over all eight cells. **What it deliberately is not: a read of any result**,
for stage 3b's three reasons (its README): §7 bars a read before *complete*, §4's drop set is a union
over all eight cells, and §8 gives the reading to **3d, a session that ran no sweep**. The lattice is
now *swept* in all eight cells; 3d forms the drop set and reads.

**Where the files are.** The sweep and gate scripts are stage 3b's (`../2026-09-28-drp-stage3b/`), run
unchanged in what they measure, and they write beside their `DRP-S0` outputs: **the `DRP-S1` cell files
are in `../2026-09-28-drp-stage3b/cells/` and the gate verdict is
`../2026-09-28-drp-stage3b/drp_gates_DRP-S1.json`.** This folder holds only what stage 3c added.

**Sealing (§8):** node ids and counts only. No interior artist is named in any committed file.

## The cells (§2.1, §2.2)

Map `graph-drp-s1.bin`, sha `418fe666…` (stage 3a; loaded only behind `DRP-G3`'s verdict, verified
against its sidecar in every process). Harness `drp_sweep.py`, sha
`6213bb1e71075511b09e7c48906ebbba917759961f4a7f2c0d67f69aa02e46fe` — **the same version, byte for
byte, as every `DRP-S0` shard**, so both rows were routed and relaxed by one harness. Pair sets, press
rules, depths and file layout as stage 3b's README describes.

| cell | plain sentence (§2.1, §2.2) | file (in `../2026-09-28-drp-stage3b/cells/`) | sha256 |
|---|---|---|---|
| `DRP-S1P0` | *the extra exits at today's pull* | `DRP-S1P0.json` | `a35b9fd3a0e61bc91dd9ded4c3f083d2b390bf6532a42e05e8c2353837ca42b9` |
| `DRP-S1P1` | *the extra exits, each press pushing twice as hard toward less-listened artists* (ramp 0.02) | `DRP-S1P1.json` | `113b8d926cb4a031eacfc7f411ffcef98eb9f842bc7d8667db1f154a90623814` |
| `DRP-S1P2` | *the extra exits, each press pushing three times as hard* (ramp 0.03) | `DRP-S1P2.json` | `a8fb47ef4bd77ff28331488635be991e1ffdf65161f7201527435afdea44e78e` |
| `DRP-S1P3` | *the ceiling with the extra exits* | `DRP-S1P3.json` | `2937eee2a38026259d3a9e3d50b8b4cca58a6d50f7e1cd11789303268400d4ad` |

## Gate outcomes — the `DRP-S1` row's share of §7 *swept*

H0 (stage 3b's harness-identity check) is `DRP-S0`-only by design; the sha above is what carries it to
this row.

| gate | plain sentence (§6) | outcome |
|---|---|---|
| `DRP-G4` | *a stronger pull changes nothing before the first press* (and the ceiling nothing before the fourth) | **PASS**, 0 violations over every pair, set and rule |
| `DRP-G4` red | *the same comparison at press 1 sees the stronger pull* | **fired** in both ramp cells |
| `DRP-G5` | *the number of presses the harness told the router about is the number the ladder is at, and the ceiling never counts as a press* | **PASS**, presses 1 and 10, all three non-anchor cells |
| `DRP-G5` red | the ceiling passed as `KNOWN` | **fired** |
| `DRP-G9` (a)–(f) | *the ceiling removes only what it says, and nothing else about the router changes* | **PASS**, 0 violations on every condition; every relaxed press re-checked from both sides |
| `DRP-G9` reds | ceiling 0.99 at press 1; the real schedule diverges somewhere; the ceiling passed as `DISLIKE` at press 10 | **all fired** |

**Every relaxed ceiling press certified; none fell back to bisection**, as on `DRP-S0` (stage 3b's README
says what that means for `DRP-G9`(d)). Counts behind each line: `drp_gates_DRP-S1.json` (sha
`8f10344e9600e04d637cf09021e3adbf1ca53183a481660879b2bf223fc7b101`).

## `DRP-C10`'s per-pair frontier count

`drp_c10_frontier.json` (sha `a99f793d6239a2bb3ec69e1d23cdd5f3502b9bd6fad80b3cc784408719e94669`), from
`drp_c10_frontier.py`. **All eight cells**, since `DRP-R2` asks for it on A0. Per (cell, set, rule,
pair), over the band presses (7–10) at which the cell returned an interior-bearing journey: added edges
touching the journeys' nodes, counted **with and without the endpoints** (a `DRP-T1` pair's endpoints
are themselves centres, and §5 does not say which count the read uses — 3d's choice), and added edges
the journeys traverse. The added-edge set is re-derived from the two CSRs and checked against stage
3a's `drp_g3.json`; a red control through the same counter must fire before any row is written. **No
fraction or summary is computed here**; §2.4's deferral condition is a read.

## Reproduce

```bash
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_sweep.py shard CELL SET RULE [--identity]
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_sweep.py merge CELL
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_gates_3b.py DRP-S1 g9 SET RULE   # x8
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_gates_3b.py DRP-S1
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3c/drp_c10_frontier.py
```

**On Windows, check the harness sha before sweeping.** With `core.autocrlf=true` a checkout writes
`drp_sweep.py` with CRLF and it hashes differently from the committed LF file that every shard records;
normalise it to LF first (execution log, task 1).

40 shards (32 sweep, 8 `DRP-G9`(a) identity runs), 14 at a time on 24 cores, ceiling cell first:
about 2 h wall. The `DRP-G9` partials took about 18 min at 8 in parallel. Outside the repository:
shards and partials in `C:\unsung-fast\drp-stage3b\` (`shards/`, `gates/` — partials now named
`g9__ROW__SET__RULE.json`), logs in `C:\unsung-fast\drp-stage3c\logs\`.
