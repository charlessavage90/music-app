# `DRP-` lattice results — the #200 depth remedy, stage 3d

**Role: AUTHORITATIVE for the `DRP-` lattice's results**: the stage-3d results note that §8 of
[`../specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`) requires, **written by a session that ran no sweep**, from the committed per-cell JSON and
never from a sweep session's prose. **Raw record:**
[`../../../builder/analysis/2026-09-28-drp-stage3d/drp_results.json`](../../../builder/analysis/2026-09-28-drp-stage3d/drp_results.json)
(sha256 `a453e0f2101e23700a9cc50ddbcd1873372980d4c1beb5472eb40949044f3a4a`), written by `drp_read.py`
beside it and committed (`0b80dab`) before this note was opened. Cite that file or this note for any
`DRP-` result. Execution log: [`../2026-09-28-drp-stage3d-execution-log.md`](../2026-09-28-drp-stage3d-execution-log.md);
the choices the design leaves to 3d were committed there (`1c1e874`) before any figure was computed.

**It names no candidate** (`DRP-R10`). Stage 4 — at most one cell, or none — is the owner's.
**Sealing (§8):** no artist is named here; endpoint and interior identities stay in the committed
node-id files.

**Run state: *complete*** (§7): all eight cells *swept* (`DRP-G4`, `G5`, `G9` passing; stage-3b and
stage-3c READMEs), `N_noise` measured (stage 3a: 0.015 on both famous strata), `DRP-G8` recorded
below, and the drop set committed in the raw record. **Every read in §7 is reachable.**

**How to read the identifiers.** Each is given with its plain sentence from the pre-registration. The
ones used throughout:

- **the band** — *the journeys you would see after pressing Dig deeper seven to ten times*.
- **`DRP-T1`** — *two artists from the most-listened 1 % of the map*; **`DRP-T2`** — *two artists from
  the next four percent*. Each is 40 pairs, and they are read separately.
- **`DRP-S0P0`, "today's app"** — *the map exactly as it is served today, at today's per-press pull*.
- **`DRP-C1`** — *after seven to ten presses, is the typical artist in the middle of a journey between
  two famous artists noticeably less famous than on the same journey in today's app, pressed the same
  way, and is that because of the pressing and not because the first path already changed?* `D` is
  *how much less famous the middle of this journey is than today's, at depth*, in percentile points of
  the map's listener ranking. Its bar is five points.
- **`DRP-C2`** — *after seven to ten presses, is the journey still delivering a comparable number of
  artists, or has it mostly just got shorter?* Its bar is 70 % of today's app's figure.
- **`DRP-C6`** — *have famous artists been pushed out of the middle of journeys?* It is gated on the
  first path and presses 1–3 (the owner's `DRP-D4`).

---

## 1. Measured

### 1.1 Readability and drops

- **`DRP-G8`** (*enough journeys survive in every cell to compare*): **40 of 40** band-readable pairs
  on `DRP-T1` and **40 of 40** on `DRP-T2`, under the primary press rule. Both strata are readable.
- **§4's drop set** is the union of the eight cells' own lists, and it matched a recomputation from
  the journeys. It holds **2** (pair, depth) entries under the primary rule, both on one `DRP-T2`
  pair at presses 19 and 20, so no band depth is affected, and **29** under the random rule.

### 1.2 The per-cell outcome, per famous stratum (§7, applied mechanically)

Primary press rule. `D` and `G` are medians over 40 pairs. "UB" is `DRP-C1`(2)'s one-sided 95 %
bootstrap upper bound on the median `D`, and it must be ≤ −0.015. "≤ −0.05" is the number of pairs
past the five-point bar. `DRP-C2` is the cell's figure ÷ today's app's; in the two ceiling cells it
must also hold at each band depth, and the lowest per-depth value is shown. `DRP-C6` held at every
gated depth in every cell (it never fired, and no (stratum, depth) was unreadable).

| cell | plain sentence (§2.1) | stratum | outcome | median `D` | UB | median `G` | ≤ −0.05 | `DRP-C2` (band; lowest depth) | qualifiers (`DRP-R9`) |
|---|---|---|---|---|---|---|---|---|---|
| `DRP-S0P1` | *each press pushes twice as hard toward less-listened artists as today* | `DRP-T1` | **NO MOVEMENT** | 0.000 | +0.0001 | 0.000 | 0 | 0.93 | (vi) |
| | | `DRP-T2` | **NO MOVEMENT** | −0.0003 | 0.000 | −0.0003 | 2 | 0.91 | (vi) |
| `DRP-S0P2` | *each press pushes three times as hard* | `DRP-T1` | **NO MOVEMENT** | 0.000 | +0.0001 | 0.000 | 0 | 0.90 | (vi) |
| | | `DRP-T2` | **NO MOVEMENT** | −0.0006 | 0.000 | −0.0006 | 1 | 0.86 | (vi) |
| `DRP-S0P3` | *from the fourth press, each press lowers the most famous artist the journey may pass through by one and a half percentile points* | `DRP-T1` | **BELOW BAR** | −0.032 | −0.024 | −0.032 | 16 | 1.80; 1.65 | (vi), (vii) |
| | | `DRP-T2` | **MOVES** | −0.150 | −0.143 | −0.150 | 40 | 1.39; 1.27 | (vii) |
| `DRP-S1P0` | *the extra connections at today's pull* | `DRP-T1` | **NO MOVEMENT** | 0.000 | 0.000 | 0.000 | 0 | 0.93 | (vi) |
| | | `DRP-T2` | **NO MOVEMENT** | 0.000 | 0.000 | 0.000 | 0 | 0.98 | (vi) |
| `DRP-S1P1` | *the extra connections, each press pushing twice as hard* | `DRP-T1` | **NO MOVEMENT** | 0.000 | 0.000 | 0.000 | 0 | 0.92 | (vi) |
| | | `DRP-T2` | **NO MOVEMENT** | −0.0003 | 0.000 | 0.000 | 1 | 0.89 | (vi) |
| `DRP-S1P2` | *the extra connections, each press pushing three times as hard* | `DRP-T1` | **NO MOVEMENT** | 0.000 | +0.0001 | 0.000 | 0 | 0.83 | (vi) |
| | | `DRP-T2` | **NO MOVEMENT** | −0.0004 | 0.000 | −0.0003 | 1 | 0.87 | (vi) |
| `DRP-S1P3` | *the ceiling with the extra connections* | `DRP-T1` | **MOVES** | −0.149 | −0.141 | −0.149 | 40 | 1.87; 1.55 | (vii) |
| | | `DRP-T2` | **MOVES** | −0.150 | −0.143 | −0.148 | 40 | 1.43; 1.27 | (vii) |

The qualifiers that attach:

- **(vi)** on every NO MOVEMENT and on `DRP-S0P3`/`DRP-T1`'s BELOW BAR: *"the scale is capped here:
  this result cannot rule out that the cell made famous journeys more famous."* Only 2 of 40
  `DRP-T1` pairs and 8 of 40 `DRP-T2` pairs have room to rise.
- **(vii)** on every ceiling-cell `DRP-C1`: *"the ceiling forced this descent; it says nothing about
  whether the journeys still hang together, which no offline number here measures."*
- **(i)–(v) attach nowhere.** (i): the random-press companion also moves wherever `DRP-C1` passes.
  (ii): the replication set agrees in sign. (iii): no null interior appears in any cell. (iv): the
  floor-attribution flag never fires (below). (v): no band similarity cost reaches the yardstick
  (below).

**`DRP-C1`(4)'s companions** for the three MOVES rows: `|D|` < 0.015 on **0** pairs in each, and the
leave-one-out range of the median is −0.152 to −0.145 (`DRP-S1P3`/`T1`) and −0.150 to −0.149 (both
`T2` rows). For `DRP-S0P3`/`T1` it is −0.033 to −0.031, with 10 pairs inside ±0.015. Every other row's
leave-one-out range sits within ±0.001 of zero.

### 1.3 The reads (§7)

| read | plain sentence | fires? |
|---|---|---|
| **`DRP-R0`** | *none of the changes we tried makes Dig deeper dig on famous pairs* | **No** — three (cell, stratum) rows MOVE |
| **`DRP-R1`–`DRP-R4`** | read over the ramp cells only (§7) | **None fires**: no ramp cell and no extra-connections-at-today's-pull cell MOVES on either stratum |
| **`DRP-R5`** | *the change works for one tier of famous artist and not the other* | **Yes, for `DRP-S0P3`**: MOVES on `DRP-T2`, BELOW BAR on `DRP-T1` |
| **`DRP-R6`** | *the journey got less famous mainly by getting shorter* | No |
| **`DRP-R7`** | *famous artists have been all but pushed out of the middle of journeys* (at the first path and presses 1–3) | No |
| **`DRP-R8`** | *does the change build press by press, or arrive all at once?* | **Gradient** in all three MOVES rows (§1.5) |
| **`DRP-R11`** | *`DRP-SW`'s trigger* | **Does not fire** (§1.4) |
| **`DRP-R12`** | *lowering the ceiling press by press makes famous-pair journeys less famous without shrinking them, and famous artists still appear* | **Yes**: `DRP-S0P3`/`T2`, `DRP-S1P3`/`T1`, `DRP-S1P3`/`T2` |
| **`DRP-R13`** | *what binds, supply or pricing* | see §1.6 |

**"Succeeds on famous pairs"** (§7's operationalisation, MOVES on both `DRP-T1` and `DRP-T2`): **one
cell, `DRP-S1P3`.** `DRP-D2`'s condition is evaluated at adoption, not here.

### 1.4 `DRP-SW`'s trigger, `DRP-R11` (§2.10) and `DRP-C5`'s first-path half

*Plain: did the extra connections change more than one first path in ten on famous pairs?* This reads
`DRP-S1P0` against today's app at press 0. The denominator is every drawn pair with a first path in
both. It fires below 0.90.

| stratum | first paths identical | share | changed, using an added connection | changed, without one (a cost tie) | median shift of the first path's typical middle artist |
|---|---|---|---|---|---|
| `DRP-T1` | 39 of 40 | 0.975 | 1 | 0 | 0.000 |
| `DRP-T2` | 36 of 40 | **0.900** | 4 | 0 | 0.000 |
| `DRP-MID` (not read) | 37 of 40 | 0.925 | 3 | 0 | 0.000 |

**It does not fire**: *"the extra connections leave famous-pair first paths essentially as they are, so
a switch would have nothing to protect."* **`DRP-T2` sits exactly on the line**: one more changed first
path would have fired it. It is deterministic, so no noise enters. Barred: treating the quiet trigger
as evidence that the added connections go unused at depth (§1.7 measures that).

### 1.5 The shape across presses (`DRP-R8`), and the stress companion

The per-depth median `D` for the three MOVES rows (primary rule; press 0–3 are 0.000 by construction,
`DRP-G9`(e)):

| press | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| ceiling in force | 0.985 | 0.97 | 0.955 | 0.94 | 0.925 | 0.91 | 0.895 | 0.865 | 0.82 | 0.745 |
| `DRP-S1P3` / `T1` | −0.032 | −0.100 | −0.130 | −0.136 | −0.144 | −0.154 | −0.157 | −0.190 | −0.240 | −0.327 |
| `DRP-S1P3` / `T2` = `DRP-S0P3` / `T2` | −0.020 | −0.077 | −0.108 | −0.124 | −0.145 | −0.156 | −0.158 | −0.207 | −0.247 | −0.335 |
| `DRP-S0P3` / `T1` (BELOW BAR, for contrast) | −0.023 | −0.061 | −0.051 | −0.054 | −0.044 | −0.026 | −0.024 | −0.062 | −0.034 | −0.021 |

**`DRP-C1s`** (*the same comparison after twenty presses*; stress companion, never a bar): the press-20
column above. The ramp and extra-connections cells sit within ±0.007 of zero at press 20 on both strata.

### 1.6 What binds: relaxation (`DRP-C13`) and `DRP-R13`

*`DRP-C13`: how far above its scheduled ceiling did the journey have to go?* *`DRP-R13`: if the
ceiling had to rise a lot to find any route, the map is missing the connections; if it hardly had to
rise, yet the stronger pulls moved nothing, the connections exist and the pull does not take them.*

| supply | stratum | median band relaxation `r` | share of journeys relaxed at press 7 / 10 / 20 | both ramp cells null? | `DRP-R13` |
|---|---|---|---|---|---|
| today's map | `DRP-T1` | **0.062** | 0.70 / 0.75 / 0.93 | yes | **missing supply** |
| today's map | `DRP-T2` | 0.000 | 0.05 / 0.18 / 0.31 | yes | **pricing** |
| extra connections | `DRP-T1` | 0.000 | 0.00 / 0.00 / 0.38 | yes | **pricing** |
| extra connections | `DRP-T2` | 0.000 | 0.05 / 0.18 / 0.31 | yes | **pricing** |

### 1.7 Companions, for every MOVES row and its baselines

- **`DRP-C7`** (*the same comparison when presses remove a random artist instead of the most famous
  one*): median `D` −0.153 (`DRP-S1P3`/`T1`), −0.159 (`DRP-S1P3`/`T2`), −0.154 (`DRP-S0P3`/`T2`);
  −0.057 on `DRP-S0P3`/`T1`. Every other cell within ±0.001 of zero.
- **`DRP-C8`** (*the same comparison on the pairs the 2026-09-27 measurement used*): median `D` −0.155
  (`DRP-S1P3`), −0.150 (`DRP-S0P3`), and 0.000 in every other cell.
- **`DRP-C2`** (payload) in absolute terms, the band's mean interior count ÷ the first path's: today's
  app 1.25 (`T1`) and 0.89 (`T2`); `DRP-S1P3` 2.33 and 1.27. **So the ceiling journeys carry roughly
  1.4 to 1.9 times as many middle artists as today's at the same depth** (ratios in §1.2). `REQ-14`:
  lengthening is reported and never rewarded. The ramp cells deliver slightly fewer (0.83–0.93).
- **`DRP-C6`, descriptive from press 4** (`REQ-12`, `REQ-27` territory under `DRP-D4`): journeys with
  at least one top-1 % artist in the middle, cell ÷ today's app —

  | | press 3 | press 4 | press 7 | press 10 | press 20 |
  |---|---|---|---|---|---|
  | `DRP-S1P3` / `T1` | 39 / 39 | **0 / 39** | 0 / 40 | 0 / 37 | 1 / 37 |
  | `DRP-S1P3` / `T2` | 39 / 39 | **0 / 36** | 0 / 34 | 0 / 37 | 0 / 30 |
  | `DRP-S0P3` / `T1` | 39 / 39 | 2 / 39 | 8 / 40 | 11 / 37 | 18 / 37 |

  Out of 40 pairs with a journey in both. In the ramp and extra-connections cells the counts stay
  within a few pairs of today's at every depth.
- **`DRP-C11`** (*the lowest the most famous artist in the middle of this journey could possibly be,
  on this map, whatever the router does*), as a fraction of headroom taken, in highest-interior
  currency (no sentence may read it as `D`): median **0.34** (`DRP-S1P3`/`T1`), **0.26** (both `T2`
  rows), 0.49 (`DRP-S0P3`/`T1`, over the 30 pairs with headroom). The ramp and extra-connections cells:
  0.00.
- **`DRP-C12`** (*did each press make the middle of the journey less famous, more famous, or neither,
  and when neither, did it just swap in an equally famous artist?*), share of band presses (7–10) —

  | | fell | rose | substituted | shortened |
  |---|---|---|---|---|
  | today's app, `T1` / `T2` | 0.08 / 0.10 | 0.04 / 0.08 | **0.89 / 0.82** | 0.00 / 0.01 |
  | `DRP-S1P3`, `T1` / `T2` | 0.33 / 0.44 | 0.17 / 0.16 | 0.50 / 0.39 | 0.00 / 0.01 |

  The ramp and extra-connections cells: substituted 0.77–0.94, much as today.
- **`DRP-C3`** (*as you press, do journeys lean more on the map's most-connected artists?*), share of
  band interior slots in today's top 1 % by connections: today's app 0.32 (`T1`) / 0.48 (`T2`);
  `DRP-S1P3` 0.48 / 0.52; `DRP-S0P3` 0.49 / 0.52; the other cells 0.33–0.51. Descriptive, no bar.
- **`DRP-C4`** (*how many artists in the middle have no listener measurement?*): **none**, at any
  depth, in any cell, on either famous stratum.
- **`DRP-C9`** (*which parts of the router's cost are doing the work?*): the band's median realised
  similarity cost on chosen edges is **0.000** in today's app and in every ramp and extra-connections
  cell except the two strongest pulls on `T2` (0.021, 0.022); **0.120** (`DRP-S1P3`/`T1`) and **0.346**
  (both `T2` ceiling rows). All sit below both yardsticks of 3d choice 7 (CRE critique F7's figures at
  ramps 0.03 and 0.10). **The floor term fires on no chosen path at presses 1–6 in any cell**, only
  on first paths, so the floor-attribution flag (§2.7) is zero against every baseline.
- **`DRP-C10`** (*did the extra connections get built, and are they reachable from the journeys?*):
  every band-readable famous pair's band journeys touch at least one added connection, in every
  `DRP-S1` cell, by either count (endpoints in or out). Journeys that **traverse** one: 7 of 40
  (`T1`) and 7 of 40 (`T2`) at today's pull, 8 and 12 at the strongest pull, **35 of 40 on `T1` and 0
  of 40 on `T2` under the ceiling**. §2.4's jump-relaxation deferral condition needs `DRP-R0`, which
  did not fire, so it is not reached by either count.
- **`DRP-C5`, first path** (descriptive, unscored): the typical middle artist of a famous-pair first
  path sits at about the 99.7th percentile (`T1`) and 99.3rd (`T2`) in every cell. On `DRP-MID` the
  first path climbs above both endpoints on **40 of 40** pairs in every cell, by either reading (3d
  choice 9). No cell changes the mid-scale first-path climb.
- **`DRP-MID`**, descriptive: in both ceiling cells its band median `D` is −0.108; in every other cell
  it is within ±0.001 of zero.

---

## 2. What I infer from it — inference, labelled, in plain language

**A stronger per-press pull does nothing on famous pairs, on either map.** After seven to ten presses,
a journey between two famous artists passes through artists exactly as famous as today's app gives,
whether each press pushes twice or three times as hard. The median change is zero to three decimal
places, and most presses (roughly eight or nine in ten) still just swap one famous middle artist for
another equally famous one. On the most-listened tier this is **the prior confirmed**, not a finding (§2.5: those artists'
less-listened connections are not on the map). On the next tier the prior was open, and the answer is
the same null.

**Giving famous artists their less-listened connections back does nothing either, unless something
forces the journey to use them.** At today's pull the extra connections change almost no first path
and nothing at depth. Every famous journey passes within one step of an added connection, and at
depth only about one journey in six takes one. The stronger pulls do not change that. This is the
shape Track B saw on another map (the router declines the new connections); it recurs here.

**Only the ceiling moves anything, and it moves things because it forbids famous artists, not because
the router finds its way to less-listened ones.** From the fourth press on, the most famous artist a
journey may pass through drops by one and a half points per press. The journeys follow it down, and
the typical middle artist ends up about fifteen percentile points less famous than today's by presses
7–10, and about thirty-three points less famous by press 20. It builds press by press rather than arriving at once. But
this is the ceiling's own schedule showing through: the descent tracks the cap, the router takes
roughly a quarter to a third of the room the map offers, and in the band about half the presses still
swap one middle artist for an equally famous one.

**On the most-listened tier the ceiling needs the extra connections, and on the next tier it does
not use them.** On today's map the most-famous pairs could not get under the cap: the ceiling had to
be lifted on most journeys, and descent fell short of the bar. The extra connections remove that: 35 of
40 journeys use one, and no lift was needed. On the next tier, the extra connections are all anchored
on top-1 % artists, whom the ceiling forbids from the fourth press. So those journeys never touch them,
and the combined cell's result there **is** the ceiling-alone result.

**What someone using `DRP-S1P3` would see.** The first path and the first three presses are exactly
what the extra-connections map gives at today's pull: identical to today's on 39 of 40 most-famous
pairs and 36 of 40 next-tier pairs. From the fourth press on, **no top-1 % artist appears anywhere in
the middle of the journey** (none of the 34–40 journeys at presses 4, 7 and 10, on either tier), and each journey
carries roughly half again to nearly twice as many middle artists as today's does at the same depth.
Whether those longer, cap-driven journeys still hang together is exactly what nothing here measures.

## 3. Weakest link

**The load-bearing assumption is that a journey forced under the cap is still a journey.** Nothing
offline measures coherence (§10). Three measured things lean against it, and none decides it:

- **The router pays to obey.** The similarity cost it accepts in the band goes from zero in today's app
  to 0.12–0.35 in the ceiling cells. That stays below both yardsticks, so no qualifier attaches, but
  the direction is plainly "weaker links".
- **The journeys lengthen**, roughly 1.4 to 1.9 times today's middle count at the same depth.
  `REQ-14` says that is never a goal.
- **On the most-listened tier the result rests on the unvetted extra connections** (35 of 40 journeys
  use one; `DRP-X1`, the weakest link §10 already named). Their quality descriptive is unrun, by the
  owner's ruling.

**What would falsify the reading that `DRP-S1P3` is a candidate worth listening to:** the stage-5
blind listen preferring today's app after several presses, or the use gate firing (his `DRP-AM6`
criterion, (a) and (d) above all).

**Other soft spots, named:**

- **`DRP-SW`'s trigger sat exactly on its line on `DRP-T2`.** One more changed first path would have
  made the switched-connections amendment spendable. The count is exact, not noisy, but it is a
  knife-edge reading and it goes to the owner as one.
- **The press rule is the most-famous-first rule**, which no one uses on purpose (`DRP-X2`). The
  random-press companion and the replication set both agree, so this does not carry the result.
- **`DRP-G9`(d) was weakened by stage 3b's certified search.** It is no longer two independent
  searches meeting at one number (execution log, orientation). That changes no journey, and 3d accepts
  it.
- **The pairs are random, not the owner's** (`DRP-X3`).

**What I would defend:** the nulls. The ramp and extra-connections cells did not move by a little;
they moved by nothing, on 40 pairs a stratum, with the ceiling cells showing the instrument can see
movement when it happens. **What I would abandon cheaply:** any sentence that says the ceiling cells
found less-famous routes. They were made to take them.

## 4. Options and their consequences

**Why this is the owner's:** stage 4 decides whether his ear and his use are spent on a candidate, and
what the app does (§8; `DRP-R10`). This note names no candidate.

- **Go on `DRP-S1P3`**, the one cell that MOVES on both tiers. **Consequences:** the stage-5 blind listen
  is designed cold by a session that has seen no journey; his use gate follows it. Before any deploy it
  owes **both** adoption obligations: a shipping build rule for the added connections that defines their
  band on a pre-cap frame and reproduces this edge set or is re-measured (`DRP-X4`), and an identity gate
  between this harness's ceiling and a shipped in-router ceiling, with a red control (`DRP-AM4`). His
  use-gate clause (c) applies, because its first path can differ (1 and 4 of 40 here). `DRP-R12` requires
  the sentence to name both changes on the most-listened tier, since the ceiling alone fell short there.
- **Go on `DRP-S0P3`**, the ceiling on today's map. **Consequences:** no map rebuild, and the first path
  never changes, so clause (c) cannot fire. It still owes the ceiling identity gate. But it MOVES on the
  next tier only: `DRP-R5` bars saying it works "on famous pairs", and on the most-listened tier it falls
  short because the map lacks the routes (`DRP-R13`).
- **None.** Today's app stands, and #200's famous-to-famous defect stays open. `DRP-R0` did not fire, so
  its "leaves open" list is not the design's conclusion. What the ramp and extra-connections nulls do
  close is **this form of each**: a ramp up to 0.03, and top-1 % extra connections at production
  pricing. Neither closes the family.
- **Carried, whatever he chooses:**
  - **`DRP-SW` is not spendable** (its trigger did not fire). #246 closes with this reading.
  - **#249** (a ceiling that varies along the journey) had two conditions. Its first, a ceiling cell
    reaching MOVES, **has now come due.** Its second is his: naming at stage 4 *where within a journey*
    the famous artists sit as the remaining problem.
