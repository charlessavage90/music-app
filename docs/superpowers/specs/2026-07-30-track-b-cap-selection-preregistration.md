# Pre-registration — Track B, cap-rule selection at production scale

**Role: ACTIVE pre-registration.** Governing plan:
[`plans/2026-07-30-graph-rebuild-track-b.md`](../plans/2026-07-30-graph-rebuild-track-b.md)
(task `CB-4`; its §0 scope rulings are incorporated here and not restated). Identifiers
**`CRS-`**, collision-checked against `docs/`, `builder/` and `api/` 2026-07-30.
**Committed before any comparative cell is scored.** The git timestamp is the part that
cannot be reconstructed afterward.

**What this licenses when complete: a recommendation input to two owner decisions** (the
cap rule for any rebuild; the `ALG-B` adoption) — never the decisions themselves, and
never an adoption. A blind listen (`REQ-38`) is owed before any adoption regardless of
how decisive these results are. **There is no offline proxy for listening coherence**;
hub metrics here price the *mechanism* the blind listen condemned, not the experience.

## §0 Design record — what was consumed, what is constant, and what can bear on what

### Run state at commitment

`CB-1`–`CB-3`'s instrument gates ran and passed, green and red halves
(`cb_gate.json`, `cb_metrics_gate.json`, `cb_paths_gate.json`, `cb_bound_check.json`).
The design probe `CB-P1` ran **before** this document was written, as a design input —
it probes the **input archives**, not built cells, so it pre-empts no read below.
`CB-1`'s bound check built one cell per selectable configuration (four, after the
`banded_quota` trim was added) and emitted comparative-looking numbers; **they remain
unread** — cells are scored only under this document's reads (builds are
byte-deterministic, so nothing is lost by having built early).

### Consumed at design time

| Input | What it fixed here |
|---|---|
| `CS-P0c` + **`CB-P1`** | The per-family DD-F1 bearing table below. `CS-P0c`'s "no cap rule can select one" scoped rules choosing from a node's **own** list; `CB-P1` measured the reverse direction it never covered. |
| `CS-P0f` | The symmetry premise behind the trim derivation: reverse-only edges score below the target's own-list tail. **Checked, not argued** — true in all 10 `CB-P1` rows, both archives. |
| `RC-A2` | Famous artists sit at rank 50–97 in their candidates' lists under `ALG-B` — why the k axis extends to 100 and why the both-ways window is evaluated on both sides. |
| `LBS-3` | Source lists cap at 100, so `k = 100` is the sweep ceiling; beyond it the cap stops binding. |
| `LBS-4` | `CRS-C6`'s pre-committed direction: survivors should tilt famous if the contribution mechanism reshapes edge existence. |
| `GRT-P3` / `GRT-P4` | Effect-size calibration: the trial k-curve (26.4% → 7.5% below-floor across k 50→100) and the production anchors (`ALG-E` vs `ALG-B` at `mutual_knn(50)`: exclusion 1.07% vs 8.67%, lower-half stranding 0.08% vs 7.00%). |
| `MKS-5b` | What "price the hub cost" must mean: degree concentration (`CRS-C3`) and hub transit (`CRS-C4`), plus the plain statement that neither is coherence. |
| `SYN-6` + plan §0 rulings | The degree bound as scoping constraint; the uncapped row barred from selection; bounded-degree re-evaluation open, owner's trigger. |
| `BTF-4` | `proximity_select`'s key, pinned: order by `\|Δpop\|` ascending (monotone in the reference's `1 + pop_weight·\|Δpop\|/100` for any positive `pop_weight`), MBID tie-break. **Adaptation ratified:** the reference applies its key to an undirected union that its ≤20-entry source lists happen to bound; a union here is unbounded (`CB-P1`: Radiohead alone has 12,776 sub-decile listers under `ALG-E`), so the rule keeps the both-ways mechanism and swaps only the ordering key. |
| The `rc_raw_records.json` re-scoring deferral | **Superseded, discharged**: both full archives are on disk, so re-scoring a 200-artist sample would answer a strictly weaker question than the cells below answer directly. |

### Which family can bear on DD-F1 — fixed from `CB-P1`, not assumed

`DD-F1` (famous-pair journeys structurally cannot contain obscure artists) is a defect
per `PRODUCT-REQUIREMENTS.md`, and the plan's widening changed which families can even
address it:

| Family | Can it create famous→obscure edges at superstars? | Ground |
|---|---|---|
| `mutual_knn(k)` | **No on `ALG-E`** (superstars' own lists contain zero sub-decile candidates — `CS-P0c`, reproduced by `CB-P1`'s mutual column: 0 for all five). **Marginally on `ALG-B`** (4–15 mutual sub-decile listers per superstar exist; whether they survive depends on both rank windows). | `CS-P0c`, `CB-P1` |
| `proximity_select(k)` | **Same candidate space as `mutual_knn`** — both-ways membership in own lists — so identical bearing; the key only reorders. At superstars the proximity key *prefers similar-popularity partners*, so its expected direction is **anti**-obscure at the top (the reference's own author built it to suppress "back alleys"). | `BTF-2`, construction |
| `trimmed_union(…, weakest_first)` | **Provably no** wherever the node's own list supplies ≥ d edges: by `CS-P0f` symmetry + the 100-cap, every reverse-only edge scores below the own-list tail, so weakest-first trim deletes all of them. Checked: all 10 `CB-P1` rows, margins recorded. A popularity-proximity trim shares the blindness (reverse-only sub-decile edges carry the largest fame gap by construction) and is deliberately not a cell. | derivation + `CB-P1` |
| `trimmed_union(…, banded_quota)` | **Yes — the only selectable configuration that can.** Reserves `floor(0.2·d)` slots at over-degree nodes for the strongest sub-decile partners. Raw material measured: 9,065 reverse-only sub-decile listers within top-50 for Radiohead alone (`ALG-E`). | `CB-P1` |
| `uncapped` | Yes trivially, and barred from selection (plan §0 ruling 3). | — |

**Consequence, fixed now:** `CRS-C5` (famous-pair sub-decile presence) is a *bearing*
read for the families marked yes/marginal; a null on it for `weakest_first` or
`mutual_knn`-on-`ALG-E` cells is **confirmation of the table, not a finding**, and must
not be reported as one.

### `PLA-R1` applicability — resolved from its grounds

`PLA-R1` barred famous-pair first-path **fame** as a scoring criterion because on the
adopted graph those interiors are structurally forced (geodesic-null). The bar's ground
is the forcing, which is a property of *that* graph. Resolution here: **the letter of
the bar is kept everywhere** — no cell is scored on mean interior fame of famous pairs —
and `CRS-C5` instead counts **presence of any sub-decile interior**, a structural-
possibility measure the bar's ground does not reach, on graphs whose whole purpose is to
change the structure the bar was derived on.

### Held constant, and why each is genuinely constant under the intervention

| Term | Why constant |
|---|---|
| Drop rule, `filter_special_purpose`, rescale strategy, unclipped ranking into the cap | Upstream of the injected cap step in `_assemble`; byte-identity of the `mutual_knn(50)` cells against both reference builds proves the shared stages are untouched. |
| Popularity (`pop_raw`, and the harness `pop` used by `banded_quota`/proximity) | Computed **before** any cap, over the full uncapped adjacency — no rule cell can move it. **Not constant across archives**, which is why band membership everywhere uses the adopted frame. |
| Fame frame (band membership, `CRS-C5`/`C6` currencies) | Percentile rank over the **adopted artifact** (sha asserted), fixed across every cell. |
| Path pair set | Fixed seed (20260730), stratified over the adopted frame, restricted to pairs routable in **every compared cell** (`GRT-P4`'s 31% coverage divergence), drawn once. |
| Router weights | **Production `ApiConfig()` defaults, single set, stated in every output.** `w_degree_hub = 0.0` is a dormant term — inert because the *current* graph's top-degree set is insular micro-genre artists, a property a cap change removes. Resolved by pre-commitment: no second weight set runs under this document; a router-side hub remedy is the plan §0 ruling-2 future track and needs its own pre-registration. |
| Noise floor | **None exists — builds are byte-deterministic**, so every threshold below is a *materiality* bar, not a significance bar. Identical inputs give identical outputs; any difference is real, and the bars say which differences are worth acting on. |

### Hazards

- **`CRS-H1` — integer-score ties at the cut.** `ALG-B` scores are small integers
  (`LBS-1`), so rank ties at the k-cut are common and the MBID tie-break decides
  survivors. Every cell reports tie prevalence at its cut (descriptive); a cell where
  >20% of cut-adjacent edges are tied is flagged **tie-dominated** and its k-sensitivity
  read carries the flag.
- **`CRS-H2` — `banded_quota`'s decile frame is the build's own population**, not the
  adopted frame — deliberate, because a shipped rule can only consult its own graph.
  Cross-cell reads still use the adopted frame; the two frames' disagreement is reported
  once per cell (share of quota-reserved partners that are sub-decile under the adopted
  frame).
- **`CRS-H3` — coverage divergence.** All cross-archive reads restrict to
  common-crawled artists and carry both denominators (`GRT-P4`'s confound, kept
  visible).

## §1 Factor table

24 cells: 12 per archive (`ALG-E`, `ALG-B`), identical grids. Within one archive, every
row's isolating baseline differs by exactly one column. Cross-archive, the isolating
partner is the same-named cell in the other archive (one column: archive).

| Cell (per archive) | family | k / (j, d) | trim | Isolating baseline |
|---|---|---|---|---|
| `MK50` | mutual_knn | 50 | — | *(anchor: production's own rule; on `ALG-E` this is the shipped graph)* |
| `MK60` | mutual_knn | 60 | — | `MK50` — k only |
| `MK75` | mutual_knn | 75 | — | `MK60` — k only |
| `MK100` | mutual_knn | 100 | — | `MK75` — k only |
| `TUw-50-50` | trimmed_union | (50, 50) | weakest_first | `MK50` at matched bound — mechanism only |
| `TUw-50-100` | trimmed_union | (50, 100) | weakest_first | `TUw-50-50` — d only |
| `TUw-100-100` | trimmed_union | (100, 100) | weakest_first | `TUw-50-100` — j only |
| `TUq-50-50` | trimmed_union | (50, 50) | banded_quota (q=0.2) | `TUw-50-50` — trim only |
| `TUq-50-100` | trimmed_union | (50, 100) | banded_quota (q=0.2) | `TUw-50-100` — trim only; also `TUq-50-50` — d only |
| `PS50` | proximity_select | 50 | — | `MK50` — selection key only |
| `PS100` | proximity_select | 100 | — | `MK100` — key only; `PS50` — k only |
| `UC` | uncapped | — | — | **REFERENCE ROW — barred from selection** (plan §0 ruling 3). Appears in *measured*, never in *options*. |

**Matched-bound rule for cross-family comparisons:** comparative reads only between
cells with the same **configured** ceiling on the same archive (bound 50: `MK50`,
`TUw-50-50`, `TUq-50-50`, `PS50`; bound 100: `MK100`, `TUw-50-100`, `TUq-50-100`,
`PS100`, `TUw-100-100`). Realized max degree is reported per cell; the configured value
is the matching key. A cross-family pair not matched on bound is descriptive only.

**`q` is a fixed design constant (0.2), not an axis.** One value, chosen so a bound-50
node reserves at most 10 sub-decile slots; sweeping it is a follow-up only if `CRS-R2`
fires. Adding it as an axis now would double the union cells to chase a number no read
below needs.

## §2 Criteria — every one carries its effect size and its plain sentence, fixed now

Anchors are the published `GRT-P4` figures for the two `MK50` cells; "the gap" means the
`ALG-E`-vs-`ALG-B` difference at `MK50`.

- **`CRS-C1` — lower-half stranding** (`stranded_share_of_crawled`, lower-half band).
  *Plain: of the obscure artists we actually collected data for, what share end up cut
  off the map entirely?* Anchors 0.08% / 7.00%. **Material:** ≥ 1.0 point movement
  against the cell's isolating baseline. **Decisive:** closes or opens ≥ half the gap
  (≥ 3.46 points).
- **`CRS-C2` — component exclusion** (absolute count **and** rate — the absolute is the
  zero-baseline-capable half, `GRT-P1`'s lesson). *Plain: how many artists does the map
  lose entirely, before anyone routes anything?* Anchors 1.07% / 8.67%. **Material:**
  ≥ 1.0 point vs isolating baseline. **Decisive:** ≥ 3.80 points (half the gap).
- **`CRS-C3` — hub concentration** (`top1pct_degree_mass_frac`, plus p99 and max
  degree). *Plain: do a handful of artists own a disproportionate share of all
  connections?* **This is a flag, not a gate** — no offline threshold for "too much"
  exists (`SYN-6`), and pretending one does would be inventing calibration. **Flag:**
  a candidate cell whose `top1pct_degree_mass_frac` exceeds its archive's `MK50` by
  ≥ 50% relative. A flagged cell stays a candidate; the flag must appear beside every
  mention of it in the report and in any recommendation, and it raises the priority of
  the blind listen for that rule.
- **`CRS-C4` — hub transit** (`top1pct_degree_frac_own`, common pair set, production
  weights). *Plain: when the router builds journeys, how often does it pass through the
  most-connected artists?* **Material:** ≥ 50% relative increase vs the archive's
  `MK50` cell. The 50% figure is a design choice with no prior calibration — stated as
  such; the blind listen owns coherence.
- **`CRS-C5` — famous-pair sub-decile presence** (count of famous-famous pairs whose
  first path contains ≥ 1 interior below the adopted frame's 90th percentile). *Plain:
  between two very famous artists, does the journey ever pass through anyone genuinely
  obscure?* Baseline is **exactly zero on `ALG-E`-`MK50`, structurally** (`CS-P0`/
  `CS-P0b`: superstars have zero sub-decile edges), so **any nonzero count is
  decisive** — legitimate here because the zero is structural rather than sampled, an
  absolute count rather than a ratio (`GRT-P1`'s pathology does not apply). Read under
  the bearing table in §0: a zero on a family marked "no" **confirms the table and is
  not a finding**.
- **`CRS-C6` — the survival-split tilt** (consultant item 3, pre-registered rather than
  descriptive). Population: edges of `ALG-E`-`MK50` between artists crawled by **both**
  archives and present in **both** `MK50` components; split by whether the same pair is
  an edge of `ALG-B`-`MK50`; compare the two groups' **max-endpoint adopted-frame
  percentile**, medians. *Plain: among artists that keep their connections under the
  new setting, do the connections that survive lean toward more-popular partners than
  the ones that vanish?* **Direction pre-committed** (`LBS-4`: survivors tilt famous).
  **Material:** ≥ 5 percentile points on the median — a design choice, stated as such
  (first measurement of its kind here). A material tilt means `ALG-B` buys stranding
  relief partly by re-pricing "similar" toward popularity everywhere — which cuts
  against its candidacy and must appear in any summary of `ALG-B`'s costs.

## §3 Gates

- **`CRS-G1` — instruments.** The three module gates (green **and** red halves) pass at
  the harness commit that scores cells. Any harness edit re-runs them. Already run once;
  committed outputs are the record.
- **`CRS-G2` — the bound.** Every selectable cell's realized max degree ≤ its
  configured ceiling. **Any violation is decisive** — a bound is definitional — and
  excludes the cell from candidacy; the violation itself is reported, not patched.
- **`CRS-G3` — band readability.** After the common-routable restriction, a fame band
  with < 8 pairs is **unreadable** for path criteria and says so (`RC-G2`'s shape —
  refuse to pool, refuse to squint). 8 because below that one pair is > 12% of a band's
  read.
- **`CRS-G4` — the reference row builds at all.** An `UC` cell that exhausts memory or
  30 minutes (≈ 20× a normal build) is reported **unbuildable, with its pre-cap degree
  diagnostics as the degraded reference row**. The read below says which form it got.

## §4 Reads — each names the run state it presupposes

- **`CRS-R0` — the k-curve at production scale.** Presupposes: all four `MK` cells of
  the archive being read. `CRS-C1`/`C2` against k, per archive, with `GRT-P3`'s trial
  curve beside it. This is the read that prices "is `ALG-B`'s stranding a k artifact"
  at full scale. **Null pre-commitment:** if no k step is material, the cap is not the
  operative lever for stranding at production scale and `GRT-P3`'s trial-scale
  sensitivity did not transfer — say so; do not escalate to k > 100, which does not
  exist (`LBS-3`).
- **`CRS-R1` — the rule effect at matched bound.** Presupposes: the four bound-50 cells
  (and separately the bound-100 set) of one archive, all scored. `CRS-C1`–`C4` across
  families. **Null pre-commitment:** if no family beats `MK` materially at either bound
  on `C1`/`C2` without a `C3`/`C4` flag, the incumbent mechanism survives its first
  real competition and the recommendation says so plainly.
- **`CRS-R2` — DD-F1 bearing.** Presupposes: both `TUq` cells and their `TUw`
  isolating baselines built, and the path module run on the famous-pair subset.
  `CRS-C5` on quota cells vs weakest-first baselines. **If `TUq` lifts `C5` from zero**
  on `ALG-E`: the union-with-quota family is the first *rule-side* device to touch
  `DD-F1`, and the finding carries its `C3`/`C4` columns with it. **Null
  pre-commitment:** if `C5` stays zero even under the quota, the reserved edges exist
  in the graph but the router does not take them at production weights — which is a
  *router* finding (the `w_floor`/`w_jump` pricing outranks the new structure), feeds
  the plan §0 ruling-2 future track, and is **not** a licence to retune weights inside
  this track.
- **`CRS-R3` — the archive tilt.** Presupposes: both `MK50` cells scored and the
  survival split computed. `CRS-C6` as fixed above. Whatever the direction, the figure
  goes beside `RC-R1`'s stranding figures in any future `ALG-B` discussion — the two
  halves of `LBS-4`'s prediction, reported together.
- **`CRS-R4` — the reference row.** Presupposes: `UC` built or `CRS-G4` excused it.
  `UC` figures appear in *measured* only. Any sentence recommending un-bounded
  operation from them is out of scope by plan §0 ruling 2 — the row exists so the
  future track starts calibrated.

**Order:** `R0` → `R1` → `R2` → `R3` → `R4`, nulls included, each read written before
the next is opened. An exposure map (criterion × changed knob) accompanies the report
per `CLAUDE.md` before anything is escalated.

## §5 What results license

A **recommendation input**, with the four-part presentation (measured / inferred in
plain language / weakest link / options). Explicitly not licensed: adoption of any
cell, any change to `BuilderConfig` or `ApiConfig` defaults, any re-crawl, any weight
retune, any claim about listening quality. The blind listen (`REQ-38`) is owed before
any adoption whatever these numbers say — and `CRS-C3`/`C4` flags raise its priority,
never substitute for it.

## §8 Amendments — append-only

*(none yet)*
