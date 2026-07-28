# Track 3 pre-registration — the depth-descent device

**Role: ACTIVE pre-registration. No experimental arm runs until this document is
committed, and its commit timestamp is the evidence of ordering.** Identifiers are
namespaced **`DD-`** — verified unused across the repository before allocation
(2026-07-28), disjoint from `C`/`F`/`A`/`R`/`T3-` examples, `TF-`, `PLA-`, `ASC-`,
`MKS-`, `CNS-`, `STC-`, `SYN-`, `CWD-`. Forward-only; nothing committed is renamed.

**Commissioned** by the owner's 2026-07-28 unpause with the goal: more obscure /
fewer very-famous artists in path interiors, **especially under bypass**. Motivating
evidence, cited not restated: `builder/analysis/2026-07-28-asc5-path-ascent/`
(famous-pair first paths are structurally forced; the bypass ladder's popularity
profile is flat to d20; the climb is carried by the similarity term), P8b F6/F7 (the
floor device only *permits* descent, never rewards it, and is dead where the criteria
score), and Tracks 2/2F (symmetric repricing and the ceiling toll are exhausted nulls
— **not re-run here**).

**What is new, in one sentence:** every prior arm repriced *transitions* or *permitted*
descent; this device is the first term that **rewards descent itself, growing with
bypass depth** — the mechanism shape WGLL value 9 describes ("the more bypasses, the
more obscure the path becomes") and no committed arm has ever had.

**Scope guards.** No shipped code changes: everything runs in the committed mirror
harness. No rebuild (no builder change, so the `acceptance.py` nameless-artist gate is
not in play). No blind listen is scheduled by this document — a candidate surfacing one
is the owner's decision at DD-R1. Track 2's C-series thresholds are reused where
stated, but **no figure from this track is comparable to Track 2's** — the pair set
differs by design, and any cross-track quotation must say so.

---

## §0 — Held constant, and why each is genuinely constant under the intervention

Enumerated per the CLAUDE.md rule, because the confound that nearly broke Track 2 was
a term inert in the baseline *for a reason the intervention removes*.

| term | held at | why it stays constant under this intervention |
|---|---|---|
| `w_sim = 3.0`, similarity scores | production | the device adds a node toll; it never touches the sim term's weight or the scores. The *realised* mean hop similarity will move — that is an outcome (DD-C4), not a knob. |
| `w_jump = 1.0`, raw currency | production | untouched by every arm. Licensed constant by PLA-R4: the jump price is immaterial at path level in both currencies, so leaving it fixed cannot mask a device effect. |
| `w_degree_hub = 0.0` | production | no arm touches degree; degree appears nowhere in the device. |
| `w_hop = 0.02` | production | the unit all magnitudes below are stated in. |
| guard G (min one intermediary) | ON everywhere incl. P | same as Track 2 §1.2. |
| victim rule, all-`known` walk, snapshots {0,1,2,3,5,7,10,15,20}, max depth 20 | Track 2's exactly | the walk is imported from the committed `run_arms.py`, not reimplemented. The `dislike` ramp is out of scope (value 6 makes it a different mechanism); noted, not smuggled in. |
| **the raw floor** | **NOT constant — a live, interacting term, and it is a factor axis** | production's floor penalises routing *below* the endpoints' min `pop_raw`, relaxing 0.15 per `known` and dying at k ≈ 4–7 (P8b F6). The device pushes down exactly where the floor pushes back at k < 7. Declaring it constant would repeat Track 2's §0 near-miss in mirror image: a brake that is weak in P *because nothing ever dives* becomes load-bearing only in the arms that dive. So it is varied explicitly (axis **F** below), not assumed away. |

## §1 — The device

One added node toll, in **percentile currency** (named per the currency rule):

> `cost(u→v) += w_known_ramp_pctl · k · pop_pctl(v)` for every relaxed node `v`
> except the target endpoint, where `k` = number of `known` bypasses so far.

- **At k = 0 the term is exactly zero**, so the first path is production's **by
  construction** — WGLL value 9's first-path clause is preserved structurally, and
  DD-G2 verifies it rather than assuming it.
- Linear in k, no saturation knob (one device, one magnitude knob; a saturation would
  be a second column). Realised magnitude is bounded: at k = 20, pctl ≈ 1, the toll is
  `20 · w`, stated per arm below in `w_hop` units.
- Exempting the target endpoint: the final hop into B is on every complete path
  exactly once, so tolling it adds a constant to all alternatives and distorts
  nothing; exempting keeps the arithmetic clean. The start has no in-hop.
- `pop_pctl` is `MirrorContext.pctl` (P6: average rank, deterministic) — a percentile
  *of* `pop_raw`, never a fame claim (§2.11).

## §2 — Factor table

Two axes. Every variant's isolating baseline differs by exactly one column.

| arm | `w_known_ramp_pctl` | floor | baseline | reading | realised toll at k=10, pctl=1 (in `w_hop`) |
|---|---|---|---|---|---|
| **P** | 0 (off) | production RAW | — | user-facing baseline | 0 |
| **DD-A1** | 0.01 | production RAW | P | does a small ramp move anything against the floor | 5× |
| **DD-A2** | 0.03 | production RAW | DD-A1 | dose | 15× |
| **DD-A3** | 0.10 | production RAW | DD-A2 | dose; at k=20 the toll (2.0) is commensurate with the whole sim term (≤3.0) | 50× |
| **DD-A4** | 0.03 | **off** (`w_floor=0`) | DD-A2 | is the floor a material brake on the device | 15× |
| **DD-A5** | 0.10 | **off** | DD-A3 | same, at the strong dose | 50× |

DD-A4 vs DD-A1 and DD-A5 vs DD-A1 are **package comparisons** (two columns) and may
not be attributed to a single knob. The dose ladder exists because Track 2F's lesson
is that a null at one magnitude is evidence about nothing; a null across 5×–50× with
DD-P1's headroom present is a mechanism-strength statement (DD-R2).

## §3 — Instrument gates (failure voids the run; not findings)

- **DD-G1** — mirror byte-identity vs `pathfinding.find_path` with the device knob at
  0.0, re-run on this harness before any arm (the Track 2 mirror gate, re-earned
  because `mirror.py` gains a term).
- **DD-G2** — every arm's d0 path byte-identical to P's on every pair. *(Plain: the
  first journey you see is untouched — verified, not assumed.)*
- **DD-G3** — artifact sha256 `4cb84ef9…` asserted everywhere; `paths` outputs record
  it (P8b F13's rule).
- **DD-G4** — fame keyed by MBID, not name, and an assertion that no scored interior
  is blank-named (P8b F8's success condition — the arms that dive are aimed exactly
  where blank names concentrate, so F8's hazard is live in this track and the fix is
  a precondition, not a deferral).

## §4 — Prerequisites, all discharged before any arm

**Discharge order: DD-P2 → DD-P1 → DD-P3 → DD-P4.** The headroom measurement runs on
the pair set, so DD-P2 precedes DD-P1 despite the numbering; the numbering is kept
because identifiers are forward-only once committed. (DD-P1 needs P walks on the
eight new pairs — P is production and walking it is validation, not an experimental
arm, per the P8b precedent.)

- **DD-P1 — depth headroom.** For every pair × C-window depth cell on a P walk: does
  a guard-compliant path exist, within **+2 hops** of P's delivered length at that
  cell, whose interiors all sit below **pctl 0.90**, honouring that cell's exclusion
  set? Measured by BFS on the induced subgraph (top-decile nodes removed, endpoints
  exempt, exclusions applied). Cells without headroom are dropped **uniformly from
  all arms** (A13's discipline). **Branch trigger with its own effect size:** if more
  than **30 %** of C1-window cells lack headroom, the pair set is re-drawn once under
  DD-P2's rule before any arm runs; a second failure stops the track at DD-R3 without
  running arms.
- **DD-P2 — the pair set.** Twelve pairs, fixed before arms: the **4 Track 2 analysis
  pairs with famous endpoints** carried over (cross-track anchors), plus **4
  famous→mid** and **4 mid→mid** pairs drawn deterministically — endpoints sampled by
  seeded rule (seed 20260728, sorted-MBID order) from popularity bands, *mid* =
  endpoint pctl in [0.50, 0.90], excluding pairs with no guard-compliant path and
  excluding degree-1 endpoints' no-detour cases (`MKS-6`). Held-out split: 8 analysis
  / 4 held-out, assigned by the same seed. The PLA-R1 existence proof (movement shows
  where endpoints leave headroom) is why the set deliberately leaves the all-famous
  slice in the minority.
- **DD-P3 — `ml-graph-analyst` protocol review** of this document (P8's precedent),
  then **harness review** once the toll lands in the mirror (P8b's precedent).
  Derivation only, per its remit.
- **DD-P4 — harness.** `mirror.py` gains the toll behind a config field defaulting to
  off; the walker and scorer are the committed Track 2 ones extended, not rewritten.
  Snyk scan on changed code before first run.

## §5 — Criteria, each with its plain sentence fixed now

Fame is the committed A11 instrument (F = log10(1+pageviews), unmatched → floor),
MBID-keyed per DD-G4. Thresholds reuse Track 2's committed calibration (band gap
1.093 ≈ one owner perception band) — reused, not re-derived.

- **DD-C1 (primary).** Paired mean ΔF vs P over cells at d ∈ {10,15,20} ≤ **−1.0**
  log10, with ≥ **75 %** of cells negative. *(Plain: after ten or more presses, the
  typical artist in the middle is about one full step less known than today's app
  would give you, and this holds across most journeys rather than being bought by a
  few.)*
- **DD-C2 (depth gradient).** Median interior F drop d5 → d20 ≥ **0.5** log10.
  *(Plain: the journey measurably gets more obscure as you keep pressing — today's
  app manages about a third of that.)* Production's own figure is owned by
  `scores.json` (C3 = 0.164).
- **DD-C3 (gate, not criterion).** DD-G2 holds. *(Plain: the first journey is
  untouched.)*
- **DD-C4 (coherence tripwire — reported, gates nothing).** Median per-hop similarity
  of interior hops at d ≥ 10, per arm vs P. A drop > **0.10** absolute flags the arm
  in every table it appears in. It cannot gate: the record shows offline coherence
  metrics were the *worst* predictors of the owner's verdict (Phase 1 log §3.8), so
  the blind listen remains the only coherence instrument this project trusts.
  *(Plain: if the steps stop sounding like neighbours, the number won't prove it —
  but a big drop is a warning worth a flag.)*
- **DD-C5 (deliverability, reported).** Distinct interior artists below pctl 0.90 at
  d ≥ 10, per arm. *(Plain: how many genuinely less-popular artists actually appeared
  on screen.)*

## §6 — Reads. Each names the run state it presupposes.

- **DD-R1 — a candidate exists.** Presupposes: all 6 walks scored, uniform drop
  applied, DD-P1 discharged. If any adoptable arm passes DD-C1 **and** DD-C2 with
  DD-C3 holding: present to the owner with an exposure map (one row per criterion ×
  the changed knob), the DD-C4/DD-C5 tables, and the realised toll figures. **A blind
  listen and any adoption are his decisions; this document schedules neither.**
- **DD-R2 — null with headroom.** Presupposes: same full run state, and DD-P1 found
  headroom in ≥ 70 % of scored C1-window cells. If no arm moves DD-C1 past **−0.3**
  (chosen now: a third of the primary effect, ≈ a clearly-visible-but-insufficient
  move): the router declines obscurity **it is being paid to take** at up to 50×
  `w_hop` per node — a mechanism-strength statement that direct depth-graduated
  pricing cannot deliver the goal on this graph, licensing the move to graph-side
  candidates (the parked rescale, the `STC-6` re-crawl) with this figure as the
  design input. **Magnitude escalation is barred** — DD-A3's k=20 toll already rivals
  the entire similarity term, so "not strong enough" is not an available reading.
- **DD-R3 — the pair set cannot ask the question.** Presupposes: DD-P1 only (fires
  before any arm). If headroom fails twice per DD-P1's trigger: the graph does not
  offer obscure middles near these journeys at all; the answer to the owner's goal is
  graph-side by demonstration, arms are **not run**, and the record says why with the
  headroom figures.
- **Partial states:** any read taken before its presupposed state is reached must say
  so in the execution log **in its own sentence**, naming what is still owed (the
  Track 2 stage-2 lesson, applied in advance).

## §7 — Closed questions this document may not reopen

Loosening the both-ways cap (`MKS-5b`); re-running Track 2, 2F, or the ceiling toll;
scoring anything on famous-pair first-path fame (PLA-R1: structurally unable to
move); growing `CLAUDE.md`; spending a blind listen or a rebuild — both the owner's,
and the rebuild additionally sits behind his open nameless-artist decision.
