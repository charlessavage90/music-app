# Cap re-evaluation — pre-registration (`CRE-`)

**Role: ACTIVE — the governing document for the cap re-evaluation experiment.**
Committed before any arm is built or run; the commit timestamp is the evidence that
every criterion, bar and read below preceded every result. Authored cold by a fresh
session from the single design-input address,
[`../2026-08-02-cap-reeval-design-inputs.md`](../2026-08-02-cap-reeval-design-inputs.md),
whose §8 ordering ruling (featured-credit filter first) was discharged 2026-08-03
(PR #67 merged). Where this document and the design-inputs note disagree, **this
document governs** (its own rule, §0 there).

**Identifier namespace: `CRE-`.** Checked disjoint against every document cited here
(`REQ-`, `FCF-`, `FAM-`, `NOV-`, `RCS-`, `TAS-`, `REL-`, `WGT-`, `COH-`, `FPC-`,
`CRS-`, `CB-`, `TB-`, `DD-`, `LBS-`, `GRT-`, `SYN-`, `BTF-`, `AS-`, `MKS-`, `PLA-`).
Sub-series: `CRE-G` instrument gates, `CRE-D` descriptive reads, `CRE-C` criteria,
`CRE-R` reads of results, `CRE-S`/`CRE-P` supply/pricing arm axes. Forward-only;
nothing here is renumbered after commit.

**What this experiment is for, in the owner's terms (design inputs §1):** no matter
which two starting artists you pick, use of the bypass button should overall create a
gradient that trends toward obscure — `REQ-42`'s shape: movement with depth, never
band-reaching, and a famous–famous gradient of zero fails `REQ-13`. Candidate
architectures are evaluated **on both data sets (`ALG-E` and `ALG-B`) until a clear
winner emerges** (`CRE-R4` defines "clear"). This pre-registration licenses **a
recommendation input to the owner's parked decisions and nothing else**: no adoption,
no default change, no shipped-code change, and a blind listen (`REQ-38`) is owed
before any adoption regardless of the numbers here.

---

## §0 — Factor table

### §0.1 The knobs

| Knob | Values in this design |
|---|---|
| **data set** | `ALG-E` (production archive) / `ALG-B` (candidate archive) |
| **supply rule** | `CRE-S0` incumbent mutual k-NN, at bound 50 (`MK50`) or 100 (`MK100` — family (a)'s other ruled bound) / `CRE-S1` trimmed union `TUw-50-50` / `CRE-S2` tag-limited union / `CRE-S3` unbounded `UC` *(staged reference, barred from candidacy)* |
| **pricing** | `CRE-P0` production weights / `CRE-P1` depth-graduated `known` ramp in the adopted currency, at ramp setting r₁ = 0.05 or r₂ = 0.15 per press |

*(There is deliberately no separate "tag device" knob: the construction-side limiter
is what distinguishes the `CRE-S2` supply value from `CRE-S1`, so it lives inside the
supply column — a separate column would make every `S2` row look like a two-column
change when the real change is one knob. A router-side tag device, if `CRE-D1` ever
licenses one, would be a new `CRE-P` value defined by amendment.)*

Arm definitions are §3. `TUw-50-50` is Track B's committed weight-trim cell shape
(`cb_build_variants.py`); `MK50` is production (`cap_strategy="mutual_knn"`,
`max_neighbours_per_artist=50` — `builder/src/artistpath_builder/config.py`, cited
not restated).

### §0.2 The cells, one row each, isolating baseline named per row

A cell's isolating baseline differs from it in **exactly one column**. Where none
exists the row says what conclusion is barred. Cells marked *(D1-branch)* exist only
if `CRE-D1`'s branch fires that way (§4).

| Cell | data set | supply | pricing | Isolating baseline | Note |
|---|---|---|---|---|---|
| E-S0-P0 | ALG-E | MK50 | prod | — (anchor) | Must reproduce production routing bit-identically (`CRE-G1`) |
| E-S0b-P0 | ALG-E | MK100 | prod | E-S0-P0 | bound isolated (family (a); `R0` measured no material structural k-step on `ALG-E` — the sweep asks whether the *gradient* differs, which no track has measured) |
| E-S1-P0 | ALG-E | TU | prod | E-S0-P0 | supply isolated |
| E-S1-P1a | ALG-E | TU | ramp r₁ | E-S1-P0 | pricing isolated |
| E-S1-P1b | ALG-E | TU | ramp r₂ | E-S1-P1a | ramp size isolated |
| E-S2-P0 *(D1-branch)* | ALG-E | tag-limited | prod | E-S1-P0 | trim device isolated (numeric trim → tag limiter; same union source, same budget) |
| E-S2-P1a *(D1-branch)* | ALG-E | tag-limited | ramp r₁ | E-S2-P0 | pricing isolated |
| E-S3-P0 | ALG-E | UC | prod | E-S1-P0 | bound presence isolated. **Staged comparison data only** — barred from candidacy (§3.1) |
| B-S0-P0 | ALG-B | MK50 | prod | E-S0-P0 | data set isolated — **carries the population confound row (§0.4)** |
| B-S0b-P0 | ALG-B | MK100 | prod | B-S0-P0 | bound isolated (family (a); structurally decisive on `ALG-B` per `R0` — committed figures consumed, sweep new) |
| B-S1-P0 | ALG-B | TU | prod | B-S0-P0 | supply isolated within ALG-B |
| B-S0-P1a | ALG-B | MK50 | ramp r₁ | B-S0-P0 | pricing isolated. *(Legitimate here, unlike on ALG-E — see §3.3's closed-cell rule)* |
| B-S1-P1a | ALG-B | TU | ramp r₁ | B-S1-P0 | pricing isolated |
| B-S1-P1b | ALG-B | TU | ramp r₂ | B-S1-P1a | ramp size isolated |
| B-S2-P0 *(D1-branch)* | ALG-B | tag-limited | prod | B-S1-P0 | trim device isolated |
| B-S2-P1a *(D1-branch)* | ALG-B | tag-limited | ramp r₁ | B-S2-P0 | pricing isolated |
| B-S3-P0 | ALG-B | UC | prod | B-S1-P0 | staged comparison data only |

Every tag cell additionally has a **scrambled-labels companion** (same cell, labels
permuted among labelled artists — `TAS-AM3b`'s stronger null form, which holds
*which* artists are labelled fixed). Companions are instrument cells for `CRE-C5`,
not candidates, and do not appear in `CRE-R` winner logic.

**Barred comparison, named per this table's own rule:** no cell pair differing in
both data set and any other column supports any attribution. Cross-data-set reads go
through B-S0-P0 vs E-S0-P0 only, and only as §0.4 allows.

### §0.3 Held constant — and why each is genuinely constant under the intervention

The Track 2 lesson (its §0): a term inert in the baseline *for a reason the
intervention removes* is not a constant. Each row states why the interventions above
cannot change its state — or, for the one that fails the test, what handles it.

| Held constant | Why it is genuinely constant |
|---|---|
| **Cleanup: both drop flags on in every cell** (`drop_no_release_tail`, `drop_featured_credit`), applying the four frozen per-population lists (`builder/src/artistpath_builder/data/no_release_drop_20260801.json`, `no_release_drop_algb_20260802.json`, `featured_credit_drop_20260803_am1.json`, `featured_credit_drop_algb_20260803_am1.json`) | The lists are frozen, sha-pinned package data, selected by `config.algorithm`, applied by MBID before capping. No cap or pricing choice can resurrect a dropped MBID or drop a kept one. Carried as **two deliberate rows, not one**, per the 2026-08-03 handoff's instruction — a cell with either flag off is not "the cleaned substrate" and is not in this design. This is precisely the dormant class the featured-credit track was ordered ahead of this document to neutralise: without the filter, ghost contributors would activate only in arms that succeed at pushing obscure, and the adopted currency would score their delivery as success. |
| **The fame ruler**: `fame_lb_pctl` over the frozen union snapshot `builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json` (sha in its manifest sidecar) | The snapshot is a committed file; every cell reads the same one. Any re-fetch is a **new instrument** (`FAM-AM2.3`'s corroboration of `FAM-AM1.7`) and would be an amendment, never a quiet swap. The interventions touch graphs and weights, not the snapshot. |
| **The pair set**: the committed Track B draw, `builder/analysis/2026-07-30-track-b-cap-selection/cb_pairs.json`, famous classes (22 common-routable famous-pair journeys) | Committed before this document; no intervention redraws it. **One thing the interventions *can* change is endpoint survival** — the cleanup could in principle have dropped a pair endpoint — so endpoint survival on both cleaned substrates is verified at `CRE-G3` before any sweep, rather than assumed. |
| **Router weights other than the device** (`w_sim`, `w_jump`, `w_floor`, `w_hop`, `w_avoid` — values cited to `api/src/artistpath_api/config.py:44-48`, never restated) | Identical numbers in every cell. **But see the dormant-term row below: identical numbers do not mean identical firing.** |
| **`w_degree_hub` = 0.0 in every cell — a deliberate, recorded decision, not an omission** (`api/src/artistpath_api/config.py:54`) | At a zero coefficient the term is a multiplication by zero and cannot self-activate whatever the graph's top-degree set becomes (`NEXT.md`'s corrected deferral row). The *reason* it is zero rests on the current graph's top-degree set, and union rules change that set — so this design measures hub behaviour with `CRE-C2` instead of repricing it, and **deciding `w_degree_hub` for a winning arm's graph is a named follow-up decision at `CRE-R1`/`R2`, never a mid-sweep tweak.** |
| **`guard_min_intermediary` on in every sweep cell** (the mirror guard `run_arms_t3.py` ran with) | Fixed harness configuration, matching the committed Track 3 ladder; no intervention touches it. |
| **The ladder**: scripted all-`known` walk, depths 0–20, victim = the interior with the highest `fame_lb_pctl`, ties and ruler-null interiors ranked by `pop_raw` then lowest MBID | Fixed here, identically in every cell. The victim rule is deterministic, so cells differ only by their knob columns. *(Currency note: prior ladders picked victims by in-graph popularity or the retired proxy; this one is fixed in the adopted currency at definition time — it is part of the instrument, not a result.)* |
| **`BuilderConfig` defaults**: `algorithm="contribution_5"`, `max_neighbours_per_artist=50`, `cap_strategy="mutual_knn"` | Analysis-only track: variant graphs are built by the harness (`cb_build_variants.py` pattern), never by moving a shipped default. `NEXT.md`'s "must not be changed" rows bind throughout; Track B held this and so does this design. |

**The term that fails the constancy test, disclosed as the design's known
uncontrolled variable: `w_floor`.** It prices dives below the endpoint-derived raw
floor, and *diving below the floor is what a successful descent arm does* — so it
fires more in exactly the arms that succeed. This is the same shape Track 2's §0
caught before its sweep. It cannot be held constant without changing the production
cost function in every cell (which would un-anchor E-S0-P0). Handling, fixed here:
**`CRE-D2` term-level cost accounting runs in every cell** (per-depth, per-term
contribution shares along chosen paths — the mirror already exposes per-term stats),
and **no findings sentence may attribute an outcome to a single knob unless `CRE-D2`
shows the attribution is not carried by differential `w_floor` firing.** A gradient
achieved *with* heavy floor-term participation is still a real gradient of the
system; what it is barred from claiming is "the supply rule alone did this."

### §0.4 The population-vs-descent confound (`FAM-AM1.7`'s named obligation)

An `ALG-B` arm's interior percentiles differ partly because **the populations
differ**: median `fame_lb_raw` is 6.1× between adopted artists in/not-in `ALG-B`
(measured on the adopted side; `FAM-AM1.7`, cited not restated). Consequences, fixed
here: primary gradient reads (`CRE-C1`) are **within-data-set** — each arm against
its own data set's baseline; cross-data-set statements are descriptive, must be
stratum-aware (the `AS-H2` lesson: a pooled read and a per-stratum read can
disagree), and must carry this row when quoted. Additionally the ruler **cannot
order candidate-only artists within the 1–5-listener clump** (`FAM-AM2.2`), so **no
read here consumes within-remainder ordering** — `ALG-B` interiors are read at the
mapped-percentile grain only.

---

## §1 — Currency and instrument obligations

- **Currency:** `fame_lb_pctl` (Definitions, `PRODUCT-REQUIREMENTS.md`; adopted
  2026-08-02 under the novelty-likelihood construct, `NOV-2`/`NOV-AM1`). "Obscure"
  below always means "low `fame_lb_pctl`". Worldly-fame claims are barred from every
  criterion (Definitions ruling). No prior fame-scored result is re-read; no
  cross-currency comparison is made (owner ruling 2026-08-02).
- **Quantisation floor (`FAM-AM1.3`, binding):** no claimed gradient below **10× the
  ruler's measured quantisation step, i.e. 0.015 in `fame_lb_pctl` units** (step
  0.0015). Anything smaller is "no measured movement", in either direction.
- **Null rule (`FAM-AM1.8` shape):** every aggregate is reported **all-interiors AND
  matched-only, with the null count per depth**. A ruler-null interior is a hole in
  the denominator, never a floor value.
- **Design note carried from the marks (fame log §8):** famous-band interiors are
  ~73% novel to the owner — the famous band is not a novelty dead zone, so the
  gradient's *practical* value does not start at zero even where `CRE-C1`'s movement
  starts small. This informs interpretation; it moves no bar.

---

## §2 — Substrates and dependencies

- **Two cleaned substrates**, one per data set: a build from the production archive
  and one from the candidate (`ALG-B`) archive, each with both drop flags on
  (§0.3 row 1). Gitignored artifacts; **identity is by manifest sidecar sha256 in
  every committed output**, per the standing artifact-identity rule.
- **Variant graphs** (TU, tag-limited, UC) are built by the analysis harness in
  `cb_build_variants.py`'s committed pattern, reading the archive through
  `ReadOnlyArchive` (the standing `GRT-A1` condition, which fires again here and is
  complied with by construction).
- **Track B's committed cells are reused, never re-run** (byte-deterministic;
  `NEXT.md` closed list). Where a Stage-1 screen input equals a committed Track B
  measurement (coverage, stranding, hub mass, `CRS-C5` presence), the committed
  figure is consumed by citation.
- **Named not-yet-built dependencies** (the execution plan owns them; each is
  harness-side only, no shipped code changes): (1) MBID-join of `fi_union_snapshot`
  percentiles onto arm graphs; (2) the mirror's `w_known_ramp_pctl` device
  (`builder/analysis/2026-07-23-track2-sweep/mirror.py`, additive and default-off)
  re-plumbed to read `fame_lb_pctl` instead of the popularity percentile — gated by
  `CRE-G1`/`G2` before any read; (3) the tag-limited union build variant (§3.2);
  (4) scrambled-label frames per tag cell (`TAS-AM3b` pattern).

---

## §3 — The arms

### §3.1 Supply

- **`CRE-S0` — incumbent** mutual k-NN, at bound 50 (`MK50`) and, as family (a)'s
  other ruled bound, 100 (`MK100`). *Plain: today's rule — two artists must each
  rank the other highly, keep at most 50 (or 100) connections.* `MK50` is the
  baseline anchor in each data set. The bound-100 first-path hub-transit flag from
  Track B (`C4`) is re-weighted by owner ruling — first-path hub transit is
  tolerable; `CRE-C2` measures the depth behaviour that now matters.
- **`CRE-S1` — trimmed union** `TUw-50-50`. *Plain: pool both artists' suggestion
  lists, then trim back to the same 50-connection budget.* Track B's coverage winner
  (loses 1 artist where `MK50` loses 800, hub mass falling, no edge explosion — the
  trim bounds degree by construction; results note §1–§2).
- **`CRE-S2` — tag-limited union** (family (c); D1-branch). *Plain: pool both lists
  as in `S1`, but instead of a flat "keep 50", use style-label agreement to decide
  which connections a very-connected artist keeps.* Constraints fixed by owner
  ruling (design inputs §5): **LB similarity is the sole source of edge existence;
  tags only re-order, re-weight, or remove** — under the union source this bounds
  edge count above by the union and every tag operation moves it down, which is what
  satisfies `NEXT.md`'s edge-growth deferral row by construction. The agreement
  device is the `WGT-` recommendation verbatim: **rarity-weighted agreement over
  `W4`** (`wgt_grid.py`'s committed implementation). **`W6` is not the frame and must
  not become it** (`NEXT.md`). Where labels are dark, the default is LB similarity
  untouched — the limiter does bounding work only where labels are good (famous
  bands, 94–100% coverage, `COH-2`). The λ-Jaccard reordering device stays closed
  (`TAS-6` selection ADVERSE); this is a new device, not a revival, and its
  famous→obscure supply effect is measured (`CRE-C6`, Stage 1), never assumed
  complementary.
- **`CRE-S3` — unbounded** `UC`. *Plain: no cap at all; the journey-builder does all
  the bounding.* **Staged comparison data behind the structural screen, barred from
  candidacy and from `CRE-R` winner logic** (owner: "more data is worth it, if only
  for comparison"). Two halves that must always be quoted together (design inputs
  §4, `SYN-6`): its prior condemnation is confounded evidence under a superseded
  definition of good (neither blind listen separated reciprocity from the degree
  bound); its structural cost is measured fact (top-1% degree mass ≈5× any capped
  cell, famous-pair hub transit 0.97–1.00 — Track B results §1). Any future (d)
  candidacy owes its own blind listen (`NEXT.md` parked row) and is not advanced
  here.

### §3.2 The tag-limited build, concretely

For each artist whose union candidate list exceeds the budget (50), keep the 50
candidates ranked by LB similarity **re-weighted by rarity-weighted `W4` agreement
with the anchor artist**; candidates with no label data are ranked by LB similarity
alone and compete in the same pool (tags re-order, they never create or veto by
absence). Symmetrise keep-stronger as production does, then largest-component prune
as production does. Everything else identical to `CRE-S1`. *(This is one member of
family (c), chosen because it is the minimal change from `S1` that uses the ruled
device; it is not "family (c) exhausted", and no read may claim family exhaustion —
the Track 2 lesson.)*

### §3.3 Pricing

- **`CRE-P0` — production weights.** Cited to `ApiConfig`, never restated.
- **`CRE-P1` — the descent device.** *Plain: each "I know them" press makes the
  journey-builder a little more willing than the press before to route through less
  famous artists.* The mirror's additive default-off `known`-ramp term with its
  percentile input replaced by `fame_lb_pctl`, at per-press ramp settings
  **r₁ = 0.05** and **r₂ = 0.15**, `guard_min_intermediary` on. This device
  **consumes `TB-P5H-7`** as the closed toll-family ruling requires: the joint
  descent × delivered-payload outcome has its own pre-registered read (`CRE-C4`,
  read jointly with `CRE-C1` in every `CRE-R`), so the outcome Track 3b left
  unconsumed — descent achieved while the path stops delivering — cannot go unread
  here.
- **Closed-cell rule:** `CRE-P1` never runs on (`ALG-E` × incumbent supply). That
  cell is Track 3's closed record and the parked DD-A2 product decision — re-running
  it would re-litigate both. On `ALG-B`, incumbent-supply pricing (B-S0-P1a) is
  unmeasured and in scope: the untested cell is **new supply × new pricing**, and a
  new data set is new supply.
- **Router-side tag pricing** is *eligible* only if `CRE-D1` supports the premise,
  enters as at most one arm defined by amendment before it is built (with its
  scrambled-labels control, `TAS-AM5c`'s lesson, mandatory), and is otherwise out of
  scope. The previously-designed genre pricing stays closed.

---

## §4 — Staging, and the seams

Depth sweeps are the cost that scales; everything cheaper runs first, and each stage
is a committed artifact before the next begins.

**Stage 0 — descriptive reads, no builds.**
- **`CRE-D1` — the owner's hypothesis, labelled as his guesswork** (design inputs
  §6). *Plain: on today's map, do two very popular connected artists share fewer
  meaningful style labels than two obscure connected artists do?* Statistic:
  rarity-weighted `W4` agreement per existing edge, edges banded by endpoint
  `fame_lb_pctl` — popular↔popular = both ≥ 0.75; obscure↔obscure = both ≤ 0.50,
  labelled edges only. **Readability floor: ≥ 500 edges per band** (the `REL-3`
  lesson — no bar over an unfloored denominator). **Effect size: the band median
  difference must exceed 2× the standard deviation of a 1,000-draw band-label
  permutation null, in the hypothesised direction.** Branch: **supported** → the
  D1-branch cells run (family (c) in full, and a router-side tag arm becomes
  eligible by amendment); **not supported** → family (c) is reduced to the single
  probe cell E-S2-P0 and no router-side tag arm exists; **unreadable** (band floor
  fails) → same reduction as not-supported, recorded as unreadable rather than
  adverse. *The single probe cell survives every branch: it is part of the specified
  run in all three, and `CRE-R0` is not readable while it is unrun.*
- **`CRE-D2` — term-level cost accounting** (§0.3): collected in every sweep cell,
  no bar, licenses knob-level attribution sentences.

**Stage 1 — builds and the structural screen** (per cell, cheap, no depth sweeps).
- **`CRE-C3` — coverage guard (owner-fixed).** *Plain: does this rule cut around ten
  thousand artists or more off the map entirely?* **Effect size: ≥ 10,000 artists
  lost vs the cell's cleaned substrate population → the arm is disqualified.** Below
  that: reported, never disqualifying (even `ALG-B`-`MK50`'s exclusion count — Track
  B results note §1 — survives; the ~10,000 line and that calibration are the
  owner's, design inputs §7). Committed Track B coverage figures are consumed by citation
  where the cell shape matches.
- **`CRE-C6` — supply screen.** *Plain: does this map even offer these journeys
  somewhere meaningfully less famous to go?* Statistic: over the famous-pair class,
  count of edges from each pair's d0 path node set to artists with `fame_lb_pctl` at
  least **0.15 below that path's d0 interior median** (10× the instrument floor,
  deliberately). **Effect size: a class-total of zero such edges → the cell cannot
  exhibit the primary outcome and is screened out of Stage 2** — with one carve-out:
  a screened cell that is a named isolating baseline still runs its sweep, because
  its arm's read needs it (a baseline is instrument, not candidate). Cells whose
  supply+pricing equals a committed Track B production-weights cell consume the
  committed `CRS-C5` result here instead of re-measuring.
- **`CRE-G3` — readability.** *Plain: we only compare journeys that exist in every
  variant being compared, and only when enough survive to say anything.* Endpoint
  survival on both cleaned substrates is verified for all 22 pairs; any pair losing
  an endpoint is removed from every cell. **Floor: a class is readable in a
  comparison only with ≥ 8 routable pairs common to the cells compared**; below
  that the comparison is recorded unreadable (the `CRS-G3` precedent). The obscure-
  endpoint classes are **already known unreadable at the committed draw**; nothing
  here reads them, and if any future bar is proposed that leans on obscure-endpoint
  behaviour, the parked redraw (owner's trigger, `NEXT.md`) is part of its price.

**Stage 2 — instrument gates, then depth sweeps** (the expensive stage).
- **`CRE-G1` — mirror equivalence.** *Plain: our measuring copy of the
  journey-builder returns exactly what the real app returns before we touch
  anything.* At E-S0-P0, d0 paths bit-identical to production routing on the adopted
  substrate for all pairs (the `TAS-AM5a` precedent). **Effect size: any divergence
  = instrument failure; no read opens until it is fixed.** *(A gate, and it carries
  its own effect size — the `A0-vs-P` lesson: an identity gate without one fired on
  a single cell and demanded a doubling.* Here the response to divergence is fixed
  and cheap — fix the harness — *not a sweep expansion, so exact identity is the
  right bar.)*
- **`CRE-G2` — device liveness.** *Plain: when we turn the new knob to an absurd
  extreme, journeys actually change — so a "no effect" answer is real, not a dead
  wire.* At an instrument-only extreme ramp (r = 1.0, never a candidate), ≥ half of
  famous-pair journeys change at d1 vs `P0` in the same cell (the `TAS-AM5b`
  precedent). **Effect size: < half → dead wire; no `P1` null is readable.**
- **Sweeps:** the §0.3 ladder over every surviving cell. Committed as one JSON per
  cell (artifact sha, arm id, per-depth paths and per-term stats), so any session
  can stop and hand off between cells.

**Stage 3 — findings note**, four-part shape (Measured / inferred in plain language /
weakest link / options), summary naming whatever cuts against it, every identifier
carrying its plain sentence.

**Seams, named now (the >8-task rule):** Seam 1 after Stage 0+1 (screen JSONs
committed); Seam 2 between the two data sets' Stage-2 sweeps (each data set's sweep
JSONs are a complete committed artifact); Seam 3 before Stage 3. A material
amendment mid-flight is also a seam. Per-task appends to the retained execution log
throughout.

---

## §5 — Criteria

Each carries its threshold and its plain sentence, fixed here before any result.

- **`CRE-C1` — primary outcome: the bypass novelty gradient.** *Plain: after ten or
  more presses of "I know them", is the typical artist in the middle of the journey
  meaningfully less famous than the ones shown before any press?* Statistic, per
  pair: median interior `fame_lb_pctl` pooled over depths 10–20 minus the same at
  depth 0; arm statistic: median of per-pair deltas over the readable famous class;
  reported all-interiors and matched-only with per-depth null counts (§1). **Material
  bar: ≤ −0.05** (five percentile points obscurer — the Track B `C6` materiality
  precedent, and 3⅓× the instrument floor). **Instrument floor: |Δ| < 0.015 = no
  measured movement** (`FAM-AM1.3`). Between the two: "movement below the material
  bar", reported as such. A delta of ~0 on famous pairs is the `DD-F1`/`REQ-13`
  defect persisting in that arm, stated in those terms. Depth band 3–5 is
  additionally reported descriptively (the `REQ-18` "handful of presses" window) and
  is **never a bar** — `REQ-18` is an Expect, and nothing here optimises toward a
  press count.
- **`CRE-C2` — per-arm kill: hubness rising with depth (owner-fixed).** *Plain: as
  you keep pressing, does the journey lean more and more on the map's most-connected
  artists?* Statistic: share of interior slots in the top-1%-by-degree set, pooled
  per depth band, **using the production artifact's top-degree set as the primary
  set** (the well-defined variant — Track B's weakest-link note: own-graph sets are
  selection-order arbitrary at ceiling ties; the own-graph share is reported beside
  it). **Kill: band d10–20 share exceeds band d0–2 share by ≥ +0.10 absolute.**
  Below: reported. First-path hub transit is tolerable by owner ruling and is
  reported, never gated — this deliberately re-weights Track B's `C4` flag, which
  was a d0 measurement.
- **`CRE-C3`, `CRE-C6`, `CRE-G1`–`G3`** — defined in §4 with their effect sizes.
- **`CRE-C4` — delivered payload floor (the `TB-P5H-7` consumption).** *Plain: after
  ten presses, is the journey still delivering a comparable number of artists, or
  has it mostly just got shorter?* Statistic, per pair: mean interior count over
  depths 10–20 divided by interior count at d0; arm statistic: median over pairs.
  **Floor: ≥ 0.5.** Read **jointly with `CRE-C1` in every result read**: `C1` pass +
  `C4` fail is `CRE-R3` (descent by deletion), never a success. Lengthening is
  likewise reported and never rewarded (`REQ-14`: no bypass mechanism may treat
  added length as its objective).
- **`CRE-C5` — tag attribution (every tag cell).** *Plain: is the improvement
  actually coming from what the labels say — or would scrambled labels have done the
  same?* Statistic: Δgain = (tag cell's `C1` statistic) − (its isolating baseline's
  `C1` statistic), compared against the same computed for its scrambled-labels
  companion. **Attribution holds only if the companion's Δgain ≤ 50% of the real
  Δgain, and the real Δgain ≥ 0.015** (else attribution is unreadable). Attribution
  failing does not delete the cell's measured outcome; it bars every sentence of the
  form "tags did this" (`TAS-AM5c`'s any-cost artifact, pre-empted).

---

## §6 — Reads of results

Every read names the run state it presupposes. Instructions that keep specified runs
alive stand as their own sentences (the R0/stage-2 lesson).

- **Run state for any `CRE-R`:** every non-branch-reduced Stage-2 cell in §0.2 has a
  committed sweep JSON on both data sets, and every gate (`G1`–`G3`) has a recorded
  outcome. **The `S3` (UC) comparison cells are part of the specified run even
  though they cannot win; no `CRE-R` is readable while either is unrun.** **The
  family-(c) probe cell that survives every `CRE-D1` branch is part of the specified
  run; no `CRE-R` is readable while it is unrun.** **Both `P1` ramp settings are
  part of the specified run in every cell that carries them; a read before both have
  run says so and names what is owed.** A read opened at any earlier state must name
  the unrun cells and licenses nothing beyond instrument claims.
- **`CRE-R0` — the null.** *Plain: nothing we tried makes the bypass button dig, on
  either data set.* Fires iff no non-staged arm reaches `C1`'s material bar on any
  readable class on either data set. Licenses: the incumbent stands; `DD-F1` remains
  a standing defect; the measured deltas and `D2` accounting go to the owner as the
  map of where movement was and was not found. **Barred: "the family space is
  exhausted"** — this design ran two bounds of family (a), one member each of
  families (b) and (c), two ramp settings of one pricing device, and family (d) as
  reference only; the unrun remainder is named in the findings note, not waved at.
- **`CRE-R1` — a winner on `ALG-E`.** Presupposes the full run state. Fires iff a
  non-staged `ALG-E` arm passes `C1` (material) with `C2` not killed, `C3` passed,
  `C4` ≥ floor. Licenses: a recommendation input to the parked **cap-rule decision**
  (owner's), carrying: the blind listen owed before adoption (`REQ-38`), the
  `w_degree_hub` follow-up decision for that arm's graph (§0.3), and `D2`-licensed
  attribution sentences only.
- **`CRE-R2` — a winner only on `ALG-B`.** Same bars on an `ALG-B` arm. Licenses: a
  recommendation input to the parked **`ALG-B` adoption decision** (owner's),
  always quoted with: the §0.4 population confound; adoption retires every existing
  path-quality figure and owes a blind listen (`NEXT.md` standing notes); switching
  is the `BuilderConfig.algorithm` re-crawl decision (closed enum, `CS-P0e`).
- **`CRE-R3` — descent by deletion.** *Plain: the journey got "less famous" mainly
  by getting shorter — fewer artists delivered, not more discoveries.* Fires per
  arm on `C1` pass + `C4` fail. Never a success; reported to the owner as a shape
  finding only if no `R1`/`R2` winner exists, because the shape question (is a
  shorter-but-obscurer journey ever wanted?) is his parked candidate-pool decision,
  not this experiment's.
- **`CRE-R4` — the clear-winner rule (the owner's "until a clear winner emerges",
  made mechanical).** A **clear winner** is a non-staged arm that (i) meets `R1`'s
  bars on **both** data sets, or meets them on one while no other non-staged arm
  meets them anywhere, and (ii) leads the best other passing arm's `C1` statistic by
  ≥ 0.015 (the instrument floor — a lead the ruler cannot see is not a lead).
  Anything short of that: the findings note presents the passing arms as options
  with consequences, no recommendation dressed as a finding, and the decision line
  states why it is the owner's (adoption, his ear, his risk acceptance).
- **Standing bars on every read:** no worldly-fame sentence; no within-remainder
  ordering; the quota-null citation rule (`R2`'s ALG-E null is "the router declines
  the quota edges *at production weights*", never "the quota rule cannot fix
  `DD-F1`"); `S3` sentences always carry both §3.1 halves; famous-pair first-path
  fame is not a scoring criterion (`PLA-R1`).

---

## §7 — What this pre-registration does not do

No adoption, no default change, no shipped-code edit, no rebuild of the served
artifact, no blind listen spent, no re-read of any prior result in a retired
currency, no re-validation of either drop rule (both closed), no calibration
hand-review re-proposal (declined 2026-08-03), no re-litigation of: Track 2/2F/
ceiling-toll nulls, Track 3/3b, `TAS-6`, `MKS-5b`, `PS100`≡`MK100`,
`proximity_select`, the pair-set attrition decision. The blind listen (`REQ-38`)
remains the primary evaluation for any adoption; **if a combined rebuild is later
adopted and sounds worse, the preserved decomposition branch in `NEXT.md`'s
deferral table (the isolated post-drop listen, held by `drop_no_release_tail` as an
experimental control) is the named instrument — this design keeps both flags as
factor-table controls precisely so that branch stays runnable.**

Decisions this document deliberately leaves with the owner, each with the reason it
is his: **adoption of any rule or data set** (his ear and his risk); **whether a
`CRE-R3`-shaped candidate has product value** (what counts as better is his);
**spending the blind listen** (one-shot resource); **triggering the obscure-endpoint
redraw** (his recorded trigger). Everything else in this document — methodology,
cells, bars, read order — is the author's column and is fixed here.

## §8 — Amendments

None at commit. Rules: amendments are appended, never edited in place; an amendment
written after any result exists says so at its head and names the hazard (the
`TAS-AM3`/`NOV-AM1`/`FCF-AM1` disclosure precedent); a router-side tag arm, if
`CRE-D1` licenses one, is defined by amendment **before** it is built, with its
scrambled-labels control named in the same amendment.
