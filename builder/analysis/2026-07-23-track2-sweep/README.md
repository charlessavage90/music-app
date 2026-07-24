# Track 2 Stage A — the mirror, and its verification gate

**Execution-order step 2, run 2026-07-23. Gate PASSED.** No arm has been run; this
directory currently contains only the router mirror and the gate that licenses it.

Artifact: `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`, asserted before every
run.

## What the gate asserted

`mirror.py`'s `SweepConfig.production()` must reproduce `api.pathfinding.find_path`
**byte-identically**. Log §3.10: a non-identical path means *stop, the harness is wrong*.
Per the pre-registration §1.2 note (guards G5a), that instruction scopes to this step,
which runs with **guard G disabled**; G is enabled uniformly afterwards.

Protocol: for each of the 12 pre-registered pairs, walk the scripted policy (all-`known`,
victim = most-popular interior by in-graph popularity, ties → lowest node id) to 20
bypasses, calling production and mirror at every depth with identical inputs and
comparing the node lists exactly. The exclusion sequence is driven by production's own
paths, so both are asked the same question at every step.

```
cells compared: 212
BYTE-IDENTICAL on every cell. Gate passed (guard G off).
```

**Ten pairs walked the full 21 depths. Two walked zero** — Radiohead → The Beatles and
Muse → Coldplay resolve to a direct edge, so with guard G off there is no interior and
therefore no victim. That is the F1 surface, and it is the empirical form of the
contradiction G5a identified in the design: those two pairs cannot be both G-guarded and
byte-compared against shipped behaviour. Verifying with G off and enabling it afterwards
is what makes both requirements satisfiable.

## Why byte-identity needed care

Reproducing the algorithm is not enough to reproduce the *output*:

1. **Term order.** Floating-point addition is not associative. The six cost terms are
   summed in production's exact order; reordering can flip the last bit of a cost and so
   flip which of two near-equal paths wins.
2. **Optional terms are never added as `+ 0.0`.** The toll is applied inside a branch, so
   the production configuration executes the identical expression rather than an
   arithmetically-equal one.
3. **Heap entries are `(cost, node)`, as production**, so ties break on node id
   identically, and neighbours are visited in CSR order.

## Knobs implemented

Per pre-registration §1.3–§1.4 as amended (A1–A3):

| Knob | Field | Levels |
|---|---|---|
| J-cur | `jump_currency` | `raw` / `pctl` (mean-matched by default, A3) |
| J-mag | `w_jump` | 1.0 / 0.3 |
| S-mag | `w_sim` | 3.0 / 1.5 |
| F | `floor_mode` | `raw` / `pctl` / `off`; pctl relax = 0.05 (A2, **not** ApiConfig's 0.15) |
| toll | `toll_s` | `None` / 0.95 / 0.80 (additive on score-1.0 edges, A1) |
| guard G | `guard_min_intermediary` | off for this step, then on everywhere |

`jump_scale_pctl` (A3's mean-matching ratio) is computed from the artifact at
`MirrorContext.build`, not copied into source — deterministic given the asserted sha256.

## Not yet done

Steps 3–5: enable G uniformly, run **A0 vs P** as a gate (PR-A / O7), then build scoring
and the remaining arms. Nothing in this directory scores anything yet — there is no fame
proxy until P4 runs.
