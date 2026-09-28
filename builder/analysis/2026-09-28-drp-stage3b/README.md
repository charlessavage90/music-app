# `DRP-` stage 3b — the `DRP-S0` row (#200). Seam B.

**Role: COMPLETE at Seam B, and the owner of the per-cell files and gate outcomes below.** Governing
document: [`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../../../docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8 stage 3b, executed from the body. Execution log:
[`docs/superpowers/2026-09-28-drp-stage3b-execution-log.md`](../../../docs/superpowers/2026-09-28-drp-stage3b-execution-log.md).

**What this is:** the four cells on today's map, swept, with their gates. **What it deliberately is
not: a read of any result.** No criterion (`DRP-C1`–`C13`) is computed here and no outcome (MOVES,
NO MOVEMENT, …) is assigned. Three reasons: §7 says no read is reachable before *complete* (all eight
cells); §4's drop rule is a union over all eight cells, so no band statistic exists yet; and §8 gives
the results note to **3d, a session that ran no sweep, working from the committed JSON, never from a
sweep session's prose**. This README therefore states only gate outcomes and bookkeeping.

**Sealing (§8):** the cell files hold node ids only. No interior artist is named in any committed
file. Endpoint names are in stage 3a's `drp_pairs.json`, as before.

## The cells (§2.1, §2.2)

| cell | plain sentence (§2.1) | file | sha256 |
|---|---|---|---|
| `DRP-S0P0` (A0) | *the map exactly as it is served today, at today's per-press pull* | `cells/DRP-S0P0.json` | `339998556fcd91f9287a026746e2fe7185cbaa44eb25129135a61b35d588a113` |
| `DRP-S0P1` | *each press pushes twice as hard toward less-listened artists as today* (ramp 0.02) | `cells/DRP-S0P1.json` | `f4dd248ddee3969a790a2857c430289dad7777906a104e58054a7949a3ea1aac` |
| `DRP-S0P2` | *each press pushes three times as hard* (ramp 0.03) | `cells/DRP-S0P2.json` | `d54dd214dd707db966bb81596ba7419413211c40b1a4171bca47a4b0ca327ffe` |
| `DRP-S0P3` | *from the fourth press, each press lowers the most famous artist the journey may pass through by one and a half percentile points; if the map cannot route that low, it goes as low as it can and says by how much* | `cells/DRP-S0P3.json` | `25262a0a9baf2a4bd23159b35b8f4216baa8ed437567933f4a04d5e10039e006` |

Every cell: the four pair sets (`DRP-T1`, `DRP-T2`, `DRP-MID`, `DRP-C8`, 40 pairs each, stage 3a's
committed draw) × both press rules (primary `victim_key`; random, seed 1), presses 0–20. Map
`graph-lba-a6.bin`, sha `28311d81…` (verified against its sidecar in every process). Harness
`drp_sweep.py`, sha `6213bb1e71075511b09e7c48906ebbba917759961f4a7f2c0d67f69aa02e46fe` as committed
(LF; one harness version across every shard, enforced by the gate script).

### What each cell file holds, per (set, rule, pair, depth)

- `path` (node ids) and `stop` (the shipped stop rule); `victim` (the pressed node id); `n_known_passed`.
- `terms`: each cost term of `pathfinding.py:155-170` summed along the path, **recomputed** from `cfg`,
  the `KNOWN` count actually passed and the shipped `effective_floor_raw` (`DRP-C9`, `DRP-AM5-I14`);
  `sim_edges` (each edge's similarity, for the band's realised median); `floor_raw`.
- Ceiling cell only: `fmax` (the schedule), `c`, `r`, `search` (`fmax` / `certified` / `bisected` /
  `none`), `calls`, `n_ceiling`, `g9f_ok`.
- Per cell: `dropped_in_this_cell`, the (set, rule, pair, depth) this cell cannot route. **§4's drop set
  is the union of these over all eight cells**, formed at *complete*.

## Gate outcomes — the `DRP-S0` row's share of §7 *swept*

| gate | plain sentence (§6) | outcome |
|---|---|---|
| **H0** (this stage's own) | *the generalised harness is the ladder `DRP-G1` validated* | **PASS**: `drp_common.ladder` re-run on A0, primary rule, `DRP-T1`/`T2`/`C8`, identical path for path; A0 random-rule `DRP-T1`/`T2` identical to stage 3a's seed-1 journeys |
| `DRP-G4` | *a stronger pull changes nothing before the first press* (and the ceiling nothing before the fourth) | **PASS**, 0 violations over every pair, set and rule |
| `DRP-G4` red | *the same comparison at press 1 sees the stronger pull* | **fired** in both ramp cells |
| `DRP-G5` | *the number of presses the harness told the router about is the number the ladder is at, and the ceiling never counts as a press* | **PASS**, presses 1 and 10, all three non-anchor cells |
| `DRP-G5` red | the ceiling passed as `KNOWN` | **fired** |
| `DRP-G9` (a)–(f) | *the ceiling removes only what it says, and nothing else about the router changes* | **PASS**, 0 violations on every condition; every relaxed press re-checked from both sides |
| `DRP-G9` reds | ceiling 0.99 at press 1; the real schedule diverges somewhere; the ceiling passed as `DISLIKE` at press 10 | **all fired** |

Counts behind each line: `drp_gates_DRP-S0.json` (sha
`a8ebe1457e5eeb74432a1e0ae7b4287e99510f81fd6f985840b8b0327035a4cc`).

**How `c` was found, and what it costs `DRP-G9`(d).** The ceiling's relaxed height was taken from stage
3a's minimax search and **certified** by the shipped `find_journey` from both sides, instead of found by
bisecting with `find_journey` alone as `DRP-AM3` item 4 words it. Bisection cost about 20 minutes per
next-tier pair. **Every relaxed press certified; none fell back to bisection.** Under certification,
(d)'s agreement between the router's threshold and the minimax bottleneck is tested by the certifying
router calls rather than by two searches meeting at one number, and the gate script re-routes both
sides of every relaxed `c` itself. Reasoning and what would have made it a seam: execution log task 2.

## Reproduce

```bash
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_sweep.py shard CELL SET RULE [--identity]
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_sweep.py merge CELL
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_gates_3b.py DRP-S0 g9 SET RULE   # x8
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3b/drp_gates_3b.py DRP-S0
```

40 shards (32 sweep, 8 `DRP-G9`(a) identity runs), 14 at a time on 24 cores; about 2.5 h wall. Outside
the repository (`C:\unsung-fast\drp-stage3b\`): `shards/`, `gates/` (the `DRP-G9` partials) and `logs/`.
The committed cell files are the shards' merge, so the shards themselves carry no information the
cells lack, except the identity runs, which only the gate reads.

**For 3c:** `drp_sweep.py` already lists the `DRP-S1` cells and loads the `DRP-S1` map behind
`DRP-G3`'s verdict; `drp_gates_3b.py DRP-S1 …` runs the same gates on that row (H0 is `DRP-S0`-only).

**Stage 3c ran it (2026-09-28).** The `DRP-S1` cell files and `drp_gates_DRP-S1.json` now sit beside
this row's, written by the same harness version; their shas and gate outcomes are owned by
[`../2026-09-28-drp-stage3c/README.md`](../2026-09-28-drp-stage3c/README.md), not by this file. Stage 3c
also keyed the `DRP-G9` partials by row (`g9__ROW__SET__RULE.json`) and renamed this row's eight to
match; the verdict above is unchanged (3c's log, task 1).
