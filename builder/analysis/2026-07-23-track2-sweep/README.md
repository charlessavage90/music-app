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

---

# Step 4 — A0 vs P: the pre-registered branch fired

**Run 2026-07-23, guard G enabled in both arms (step 3). `run_a0.py`. This README owns
the figures below.** The pre-registered expectation was **path-identity to P on the full
pair × depth grid** (§1.4). It did not hold.

```
cells compared: 252   identical: 251
Miles Davis -> Daft Punk  DIVERGES @ d0
```

Every other pair is identical at every depth 0–20, and Miles Davis → Daft Punk is
identical at d1–d20. **Exactly one cell in 252 differs.**

## The divergent cell

Un-relaxed floor at d0 = `min(pop_raw[Miles Davis], pop_raw[Daft Punk])` = **0.6726**.

| | interiors | path |
|---|---|---|
| **P** (`w_floor=1`) | 6 | Ella Fitzgerald → **Dean Martin (0.6668)** → Mariah Carey → Alicia Keys → John Legend → Ye |
| **A0** (`w_floor=0`) | 5 | Ella Fitzgerald → **Michael Bublé (0.6563)** → Meghan Trainor → John Legend → Ye |

**Both paths dip below the floor.** The floor did not prevent the dip — it selected the
*shallower* one (Dean Martin, 0.0058 under) over the deeper (Michael Bublé, 0.0163 under),
and bought a sixth interior doing it.

## Where the floor is alive, by depth

Pooled over all 12 pairs, P's Dijkstra relaxations:

| depth | relaxations | floor term non-zero | % |
|---|---|---|---|
| d0 | 722,312 | 370,247 | **51.259** |
| d1 | 763,151 | 109,077 | 14.293 |
| d2 | 774,619 | 16,411 | 2.119 |
| d3 | 784,909 | 972 | 0.124 |
| d4 | 786,577 | 37 | 0.005 |
| d5 | 788,361 | 8 | 0.001 |
| **d6 – d20** | 12,506,000 | **0** | **0.000** |

Global: 496,752 of 16,924,346 relaxations (2.94 %).

## What this establishes

1. **Adjudication claim 23's mechanism is falsified; its conclusion very nearly survives.**
   Claim 23 held that `w_floor` never fires because `w_jump` prevents paths dipping below
   the floor. Paths *do* dip below it — both arms do, in the one cell that differs. The
   floor fires on **half of all relaxations at d0**. What is nearly true is the outcome:
   it changes the chosen path in 1 cell of 252.
2. **The §0 confound cannot occur in the scored window — measured, not argued.** §0's worry
   was that a weight-1.0 raw counter-term, inert in the baseline, would "switch on only in
   the arms that work" at depth. The floor term is **exactly zero from d6 through d20**,
   and C1 scores at d ≥ 10 with C2 at d15/d20. This is not a property of P: the relaxed
   floor reaches 0 after `ceil(base_floor / 0.15)` `known` bypasses regardless of arm, and
   `max(0, 0 − pop_raw_v) = 0` for every node thereafter. **It is zero for every raw-floor
   arm at every scored depth, unconditionally.**
3. **Where the floor is live is d0–d2, which is exactly where C5's no-regression
   inspection looks** — so the term is not irrelevant, it is relevant somewhere no
   *scored* criterion operates.

Point 2 applies to the **raw** floor only. The FL arms use a **percentile** floor with the
A2 relax constant (0.05), deliberately calibrated to stay alive to ~d18–20; that is a
different device and this result says nothing about it.

## Not yet done — and deliberately stopped here

§1.4 requires a design revision to be **recorded before proceeding**, so no further arm has
run. The decision is the owner's; options are in the execution log. Steps remaining: settle
the factorial's shape, then build scoring and run the arms. Nothing scores anything until
P4 delivers a validated fame proxy.
