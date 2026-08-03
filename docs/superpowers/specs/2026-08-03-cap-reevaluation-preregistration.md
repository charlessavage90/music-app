# Cap re-evaluation — pre-registration (`CRE-`)

**Role: ACTIVE — the governing document for the cap re-evaluation experiment.**
Committed before any arm is built or run; the commit timestamp is the evidence that
every criterion, bar and read below preceded every result. Authored cold by a fresh
session from the single design-input address,
[`../2026-08-02-cap-reeval-design-inputs.md`](../2026-08-02-cap-reeval-design-inputs.md),
whose §8 ordering ruling (featured-credit filter first) was discharged 2026-08-03
(PR #67 merged). Where this document and the design-inputs note disagree, **this
document governs** (the rule in that note's role header). **Revised once before
freeze, 2026-08-03, on two pre-run reviews — see §9**, which also discloses the two
review measurements that existed before this revision. The freeze point is this
revision's commit; from here, changes are §8 amendments only.

**Identifier namespace: `CRE-`.** Checked disjoint against every document cited here
(`REQ-`, `FCF-`, `FAM-`, `NOV-`, `RCS-`, `TAS-`, `REL-`, `WGT-`, `COH-`, `FPC-`,
`CRS-`, `CB-`, `TB-`, `DD-`, `LBS-`, `GRT-`, `SYN-`, `BTF-`, `AS-`, `MKS-`, `PLA-`).
Sub-series: `CRE-G` instrument gates, `CRE-D` descriptive reads, `CRE-C` criteria,
`CRE-R` reads of results, `CRE-S`/`CRE-P` supply/pricing arm axes. Bare tokens from
colliding series are always written qualified here (e.g. **Track B's `R0`**, never
`R0`). Forward-only; nothing here is renumbered after commit.

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
| **pricing** | `CRE-P0` production weights / `CRE-P1` depth-graduated `known` ramp in the adopted currency, at ramp setting **r₁ = 0.01** or **r₂ = 0.03** per press (§3.3 for why these two) |

*(There is deliberately no separate "tag device" knob: the tag-guided ceiling is what
distinguishes the `CRE-S2` supply value from `CRE-S1`, so it lives inside the supply
column — a separate column would make every `S2` row look like a two-column change
when the real change is one knob. A router-side tag device, if `CRE-D1` ever licenses
one, would be a new `CRE-P` value defined by amendment.)*

### §0.2 The cells, one row each, isolating baseline named per row

A cell's isolating baseline differs from it in **exactly one column**. Where none
exists the row says what conclusion is barred. Cells marked *(D1-branch)* exist only
if `CRE-D1`'s branch fires "supported" (§4). **E-S2-P0 carries no mark: it is the
family-(c) probe cell and part of the specified run on every `CRE-D1` branch.**

| Cell | data set | supply | pricing | Isolating baseline | Note |
|---|---|---|---|---|---|
| E-S0-P0 | ALG-E | MK50 | prod | — (anchor) | `CRE-G1` identity cell (mirror vs production router code, same substrate) |
| E-S0b-P0 | ALG-E | MK100 | prod | E-S0-P0 | bound isolated (family (a); Track B's `R0` measured no material structural k-step on `ALG-E` — the sweep asks whether the *gradient* differs, which no track has measured) |
| E-S1-P0 | ALG-E | TU | prod | E-S0-P0 | supply isolated |
| E-S1-P1a | ALG-E | TU | ramp r₁ | E-S1-P0 | pricing isolated |
| E-S1-P1b | ALG-E | TU | ramp r₂ | E-S1-P1a | ramp size isolated |
| E-S2-P0 | ALG-E | tag-limited | prod | E-S1-P0 | ceiling device isolated (numeric ceiling → tag-guided ceiling; same union source, same budget, same placement — §3.2). **Branch-proof probe cell.** |
| E-S2-P1a *(D1-branch)* | ALG-E | tag-limited | ramp r₁ | E-S2-P0 | pricing isolated |
| E-S3-P0 | ALG-E | UC | prod | E-S1-P0 | bound presence isolated. **Staged comparison data only** — barred from candidacy (§3.1) |
| B-S0-P0 | ALG-B | MK50 | prod | E-S0-P0 | data set isolated — **carries the §0.4 confound rows** |
| B-S0b-P0 | ALG-B | MK100 | prod | B-S0-P0 | bound isolated (family (a); structurally decisive on `ALG-B` per Track B's `R0` — committed figures consumed, sweep new) |
| B-S1-P0 | ALG-B | TU | prod | B-S0-P0 | supply isolated within ALG-B |
| B-S0-P1a | ALG-B | MK50 | ramp r₁ | B-S0-P0 | pricing isolated. *(Legitimate here, unlike on ALG-E — see §3.3's closed-cell rule)* |
| B-S1-P1a | ALG-B | TU | ramp r₁ | B-S1-P0 | pricing isolated |
| B-S1-P1b | ALG-B | TU | ramp r₂ | B-S1-P1a | ramp size isolated |
| B-S2-P0 *(D1-branch)* | ALG-B | tag-limited | prod | B-S1-P0 | ceiling device isolated |
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
cannot change its state — or, where the test fails, what handles it.

| Held constant | Why it is genuinely constant |
|---|---|
| **Cleanup: both drop flags on in every cell** (`drop_no_release_tail`, `drop_featured_credit`), applying the four frozen per-population lists (`builder/src/artistpath_builder/data/no_release_drop_20260801.json`, `no_release_drop_algb_20260802.json`, `featured_credit_drop_20260803_am1.json`, `featured_credit_drop_algb_20260803_am1.json`) | The lists are frozen, sha-pinned package data, selected by `config.algorithm`, applied by MBID before capping. No cap or pricing choice can resurrect a dropped MBID or drop a kept one. Carried deliberately as this **one row naming both flags** (the 2026-08-03 handoff permits one row or two, and requires only that neither flag is held by omission). A cell with either flag off is not "the cleaned substrate" and is not in this design. This is precisely the dormant class the featured-credit track was ordered ahead of this document to neutralise: without the filter, ghost contributors would activate only in arms that succeed at pushing obscure, and the adopted currency would score their delivery as success. |
| **The fame ruler** — `fame_lb_pctl` = mid-rank percentile over the **adopted artifact's non-null `fame_lb_raw` frame (N = 74,151)**, with `builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json` (sha in its manifest sidecar) supplying **raw values** for artists outside that frame, which are **mapped into it**; values above the frame maximum take the maximum's percentile (`FAM-AM1.6`). This is `fi_validation.json`'s `percentile_definition`, restated here because the shorthand "percentiles over the union snapshot" mis-built the ruler once already (§9). **`CRE-G1c`: the sweep harness asserts its frame N equals 74,151 before any cell is scored.** | The frame and snapshot are committed files; every cell reads the same ones. Any re-fetch is a **new instrument** (`FAM-AM2.3`'s corroboration of `FAM-AM1.7`) and would be an amendment, never a quiet swap. The interventions touch graphs and weights, not the snapshot. |
| **The pair set**: the committed Track B draw, `builder/analysis/2026-07-30-track-b-cap-selection/cb_pairs.json`, famous classes (22 common-routable famous-pair journeys) | Committed before this document; no intervention redraws it. **One thing the interventions *can* change is endpoint survival** — the cleanup could in principle have dropped a pair endpoint — so endpoint survival on both cleaned substrates is verified at `CRE-G3` before any sweep, rather than assumed. |
| **The ladder**: scripted all-`known` walk, depths 0–20, **journey semantics** — the harness mirrors `find_journey`, the function the app actually calls, so a directly-adjacent pair yields a forced-detour interior rather than vanishing from the record (the `find_path` harness precedent silently unreads exactly the pairs union arms make adjacent — §9). Victim = the interior with the highest `fame_lb_pctl`; ties and ruler-null interiors ranked by `pop_raw` then lowest MBID. **The uniform-drop rule binds: a (pair, depth) cell infeasible in any compared cell is dropped from every compared cell, and the dropped set is committed** (the Track 3 `dropped_cells_d7` precedent, adopted at authoring time instead of mid-flight). | Fixed here, identically in every cell. The victim rule is deterministic, so cells differ only by their knob columns. *(Currency note: prior ladders picked victims by in-graph popularity or the retired proxy; this one is fixed in the adopted currency at definition time — it is part of the instrument, not a result.)* |
| **Router weights other than the device** (`w_sim`, `w_jump`, `w_floor`, `w_hop`, `w_avoid` — values cited to `api/src/artistpath_api/config.py:44-48`, never restated) | Identical numbers in every cell. **See the `w_floor` paragraph below: identical numbers do not mean identical firing, and the two knob axes are differently exposed.** |
| **`w_degree_hub` = 0.0 in every cell — a deliberate, recorded decision, not an omission** (`api/src/artistpath_api/config.py:54`) | At a zero coefficient the term is a multiplication by zero and cannot self-activate whatever the graph's top-degree set becomes (`NEXT.md`'s corrected deferral row). The *reason* it is zero rests on the current graph's top-degree set, and union rules change that set — so this design measures hub behaviour with `CRE-C2` instead of repricing it, and **deciding `w_degree_hub` for a winning arm's graph is a named follow-up decision at `CRE-R1`/`R2`, never a mid-sweep tweak.** |
| **`guard_min_intermediary` on in every sweep cell** (the mirror guard `run_arms_t3.py` ran with) | Fixed harness configuration, matching the committed Track 3 ladder; no intervention touches it. |
| **`BuilderConfig` defaults**: `algorithm` still carries `contribution_5` (the default is `PRODUCTION_ALGORITHM`, a full parameter string — cited, not restated), `max_neighbours_per_artist=50`, `cap_strategy="mutual_knn"` | Analysis-only track: variant graphs are built by the harness (`cb_build_variants.py` pattern), never by moving a shipped default. `NEXT.md`'s "must not be changed" rows bind throughout; Track B held this and so does this design. |
| **`pop_raw`'s normalisation endpoints, instrumented per cell.** `pop_raw` is min-max log-scaled over the kept node set (`graph.py::_log_scaled`), so a supply rule that changes which artists survive shifts every `pop_raw`, hence `floor_raw` and every `w_jump` term, by an affine renormalisation. Expected tiny (inference, not measurement — §9). | Not assumed constant: **Stage 1 records `_log_scaled`'s `low` and `high` per built cell and reports the affine map between arms**, so a non-trivial shift is visible rather than silent. Two floats per cell. |

**The term that fails the constancy test, disclosed with its measured exposure:
`w_floor`.** It prices dives below the endpoint-derived raw floor, and diving below
the floor is what a successful descent arm does — the Track 2 §0 shape. Its exposure
is **asymmetric across the two knob axes** (measured, §9): on the 22 famous pairs the
`known` relaxation drives the floor to 0.0 by press 5–6 for every pair, and the ramp
term is identically zero at d0 by construction — so at `CRE-C1`'s two read points
(d0, d10–20) the floor either fires identically across pricing arms or is identically
dead, and **differential `w_floor` firing cannot carry a `C1` attribution across the
pricing knob**. It **can** carry one across the **supply** knob, where d0 routing
genuinely differs. Handling, fixed here: **`CRE-D2` term-level cost accounting runs
in every cell** (per-depth, per-term contribution shares along chosen paths — **new
harness code, dependency (5) in §2**; the mirror's existing counters are search-wide
tallies only), and **no findings sentence may attribute an outcome to the supply knob
alone unless `CRE-D2` shows the attribution is not carried by differential floor-term
firing.** A gradient achieved *with* heavy floor-term participation is still a real
gradient of the system; what it is barred from claiming is "the supply rule alone did
this."

### §0.4 Population confounds (`FAM-AM1.7`'s named obligation, plus two measured rows)

- **Composition:** an `ALG-B` arm's interior percentiles differ partly because the
  populations differ — median `fame_lb_raw` is 6.1× between adopted artists
  in/not-in `ALG-B` (`FAM-AM1.7`, cited not restated). Primary gradient reads
  (`CRE-C1`) are **within-data-set**; cross-data-set statements are descriptive,
  stratum-aware (the `AS-H2` lesson), and carry this section when quoted. The ruler
  cannot order candidate-only artists within the 1–5-listener clump (`FAM-AM2.2`),
  so no read consumes within-remainder ordering.
- **Differential ruler-null censoring (measured, §9):** ruler-null share is ~0.06%
  of `ALG-E` nodes but ~6% of `ALG-B` nodes and ~21.6% of `ALG-B`-only artists,
  and the null rate is higher in the obscure decile — so a descending `ALG-B` arm
  delivers artists that drop out of its own score at an increasing rate, biasing its
  `C1` toward zero *within* the within-data-set read. Obligation: **every `C1`
  figure reports the per-depth null count and the null-share trend d0 → d20; an arm
  whose null share rises by more than 0.05 from d0 to the d10–20 band has its `C1`
  reported as "descent partly unmeasurable", never as a clean pass.**
- **Descent headroom (measured, §9):** the obscurest artist within one hop of a
  famous d0 path sits ~0.16 below the interior median on `ALG-E` and ~1.00 below on
  `ALG-B` — the same absolute bar asks a far harder question of `ALG-E`. Handling:
  `CRE-C1` is also reported as a **fraction of that cell's own measured 1-hop
  headroom** (`CRE-C6`'s reporting output) as a *descriptive companion* — never a
  bar — which is the only honest way the findings note may put arms from the two
  data sets in one sentence.

---

## §1 — Currency and instrument obligations

- **Currency:** `fame_lb_pctl` under the novelty-likelihood construct (Definitions,
  `PRODUCT-REQUIREMENTS.md`; adopted 2026-08-02, `NOV-2`/`NOV-AM1`), **computed
  exactly as the §0.3 ruler row defines it — adopted-artifact frame (N = 74,151),
  union snapshot supplying raw values, mapped percentiles for out-of-frame artists
  (`FAM-AM1.6`).** "Obscure" below always means "low `fame_lb_pctl`". Worldly-fame
  claims are barred from every criterion (Definitions ruling). No prior fame-scored
  result is re-read; no cross-currency comparison is made (owner ruling 2026-08-02).
- **Quantisation floor (`FAM-AM1.3`, binding):** no claimed gradient below **10× the
  ruler's measured quantisation step, i.e. 0.015 in `fame_lb_pctl` units** (adopted
  frame step 0.00147). Anything smaller is "no measured movement", in either
  direction.
- **Null rule (`FAM-AM1.8` shape):** every aggregate is reported **all-interiors AND
  matched-only, with the null count per depth** — and the null-share *trend*, per
  §0.4. A ruler-null interior is a hole in the denominator, never a floor value.
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
  raw values onto arm graphs under the §0.3 frame definition; (2) the mirror's
  `w_known_ramp_pctl` device (`builder/analysis/2026-07-23-track2-sweep/mirror.py`,
  additive and default-off) re-plumbed to read `fame_lb_pctl` — **as a copy or a
  strictly additive switch that leaves the frozen file's committed reproductions
  intact, with the device knobs' defaults staying 0.0** (`NEXT.md`'s must-not-change
  row); gated by `CRE-G1`/`G2` before any read; (3) the tag-limited union build
  variant (§3.2); (4) scrambled-label frames per tag cell (`TAS-AM3b` pattern);
  **(5) per-term cost accounting along chosen paths** (the mirror's existing
  counters are search-wide tallies; `CRE-D2` needs per-term contribution shares —
  new code); **(6) journey-semantics ladder** (the committed `walk` helpers mirror
  `find_path` and break on empty interiors; the ladder here needs `find_journey`
  behaviour, §0.3).

---

## §3 — The arms

### §3.1 Supply

- **`CRE-S0` — incumbent** mutual k-NN, at bound 50 (`MK50`) and, as family (a)'s
  other ruled bound, 100 (`MK100`). *Plain: today's rule — two artists must each
  rank the other highly, keep at most 50 (or 100) connections.* `MK50` is the
  baseline anchor in each data set. The bound-100 first-path hub-transit flag from
  Track B (its `C4`) is re-weighted by owner ruling — first-path hub transit is
  tolerable; `CRE-C2` measures the depth behaviour that now matters.
- **`CRE-S1` — trimmed union** `TUw-50-50`. *Plain: pool both artists' suggestion
  lists, then trim back to the same 50-connection budget.* Track B's coverage winner
  (loses 1 artist where `MK50` loses 800, hub mass falling, no edge explosion — the
  trim bounds degree by construction; results note §1–§2). The committed
  implementation (`cb_build_variants.py::cap_trimmed_union`) trims **after**
  symmetrisation, by deleting whole edges at over-budget nodes — the order matters
  and §3.2 inherits it.
- **`CRE-S2` — tag-limited union** (family (c)). *Plain: pool both lists as in
  `S1`, but where a very-connected artist must give connections up, use style-label
  agreement instead of raw similarity rank to decide which ones it keeps.*
  Constraints fixed by owner ruling (design inputs §5): **LB similarity is the sole
  source of edge existence; tags only re-order, re-weight, or remove** — under the
  union source this bounds edge count above by the union and every tag operation
  moves it down, which is what satisfies `NEXT.md`'s edge-growth deferral row by
  construction. The agreement device is the `WGT-` recommendation verbatim:
  **rarity-weighted agreement over `W4`** (`wgt_grid.py`'s committed
  implementation). **`W6` is not the frame and must not become it** (`NEXT.md`).
  Where labels are dark, the default is LB similarity untouched. The λ-Jaccard
  reordering device stays closed (`TAS-6` selection half ADVERSE); this is a new
  device, not a revival, and its famous→obscure supply effect is measured
  (`CRE-C6`), never assumed complementary.
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

**Identical to `CRE-S1`'s committed shape in structure and order** — union →
symmetrise keep-stronger → largest-component prune → **degree ceiling at budget 50
applied by deleting whole edges from both endpoints at over-budget nodes** (per-node
row truncation before symmetrisation bounds nothing; that is the deleted
`pre_symmetrise` defect, configured 50 / observed max degree 11,243, recorded in
`cb_build_variants.py`'s docstring and `builder/src/artistpath_builder/config.py`).
**The single difference from `CRE-S1` is the ranking that decides which edges an
over-budget node loses:** `S1` deletes the weakest by LB similarity; `S2` deletes
the weakest by LB similarity re-weighted by rarity-weighted `W4` agreement between
the edge's endpoints, with unlabelled-endpoint edges ranked by LB similarity alone
in the same pool (tags re-order the deletion ranking; they never create an edge or
veto by absence). One knob — the ceiling's ranking function — which is what keeps
E-S2-P0's isolating baseline one column away. *(This is one member of family (c),
chosen as the minimal change from `S1` that uses the ruled device; it is not
"family (c) exhausted", and no read may claim family exhaustion — the Track 2
lesson.)*

### §3.3 Pricing

- **`CRE-P0` — production weights.** Cited to `ApiConfig`, never restated.
- **`CRE-P1` — the descent device.** *Plain: each "I know them" press makes the
  journey-builder a little more willing than the press before to route through less
  famous artists.* The mirror's additive default-off `known`-ramp term with its
  percentile input replaced by `fame_lb_pctl` (dependency (2)), at per-press ramp
  settings **r₁ = 0.01** and **r₂ = 0.03**, `guard_min_intermediary` on. **Why this
  bracket (revised at review, §9):** the currency translation factor is ≈1.03, so
  these reproduce Track 3's `DD-A1`/`DD-A2` regime almost exactly — the strongest
  settings whose measured similarity cost on chosen edges stays below the dominating
  regime; the originally drafted 0.05/0.15 sit at 130×–780× the median chosen-edge
  similarity cost by ten-plus presses, where the toll is no longer "a little more
  willing". **Both settings are known from the pre-run prior (`CRE-D3`) to move
  nothing at incumbent `ALG-E` supply — the arms exist to test whether changed
  supply unlocks them, which is the untested cell this design is for.** The device
  operates through the `known` reroll, whose governing semantics are `REQ-27`
  (highly similar AND more obscure): the ramp is a global per-press repricing, not a
  per-victim substitution device, so `REQ-27` compliance of what it actually serves
  is judged at the blind listen, while `CRE-C1` measures the more-obscure half. This
  device **consumes `TB-P5H-7`** as the closed toll-family ruling requires: the
  joint descent × delivered-payload outcome has its own pre-registered read
  (`CRE-C4`, read jointly with `CRE-C1` in every `CRE-R`), so the outcome Track 3b
  left unconsumed — descent achieved while the path stops delivering — cannot go
  unread here.
- **Closed-cell rule:** `CRE-P1` never runs **as a candidate** on (`ALG-E` ×
  incumbent supply). That cell is Track 3's closed record and the parked DD-A2
  product decision — re-running it as a candidate would re-litigate both. **One
  instrument exception, defined at §4: the Stage-0 prior cell `CRE-D3`**, which runs
  the ladder there once per ramp setting as a *prior*, is barred from candidacy and
  from all `CRE-R` winner logic, and re-opens neither the closed verdict nor the
  parked decision. On `ALG-B`, incumbent-supply pricing (B-S0-P1a) is unmeasured and
  in scope: the untested cell is **new supply × new pricing**, and a new data set is
  new supply.
- **Router-side tag pricing** is *eligible* only if `CRE-D1` fires "supported",
  enters as at most one arm defined by amendment before it is built (with its
  scrambled-labels control, `TAS-AM5c`'s lesson, mandatory), and is otherwise out of
  scope. The previously-designed genre pricing stays closed.

---

## §4 — Staging, and the seams

Depth sweeps are the cost that scales; everything cheaper runs first, and each stage
is a committed artifact before the next begins.

**Stage 0 — descriptive reads and the pricing prior.**
- **`CRE-D1` — the owner's hypothesis, labelled as his guesswork** (design inputs
  §6). *Plain: on today's map, do two very popular connected artists share fewer
  meaningful style labels than two obscure connected artists do?* **Substrate,
  now stated: the adopted artifact's surviving edge set.** Statistic (revised at
  review, §9): rarity-weighted `W4` agreement per labelled edge, edges banded by
  endpoint `fame_lb_pctl` (popular↔popular = both ≥ 0.75; obscure↔obscure = both
  ≤ 0.50), **compared size-matched** — within cells of matched endpoint label-set
  sizes (`(min,max)` cells with ≥ 30 edges), the edge-weighted mean of per-cell
  band differences. This is deterministic; no permutation draw. **Effect size,
  absolute and directional: supported iff the size-matched difference is ≤ −0.05
  (popular agreement lower) — the hypothesised direction.** Readability: ≥ 500
  labelled edges per band, **and every `D1` sentence carries the labelled-edge
  share per band** (label coverage thins with obscurity — `COH-2` — so the obscure
  band's statistic describes its labelled subset, and a reader must see how big
  that subset is). **Disclosure (§9): the pre-run critique measured this statistic
  at +0.08 — the opposite direction — on this substrate. The committed
  confirmatory run is still specified** (the critique's probe is a review
  instrument, not a committed record; the run is one pass over committed frames),
  **but the expected branch is "not supported".** Branch: **supported** → the
  D1-branch cells run and a router-side tag arm becomes eligible by amendment;
  **not supported** or **unreadable** → the D1-branch cells do not exist and no
  router-side tag arm does. *The probe cell E-S2-P0 is not on this branch: it is
  part of the specified run in all three outcomes, and `CRE-R0` is not readable
  while it is unrun.*
- **`CRE-D3` — the pricing prior (added at review, §9).** *Plain: before building
  anything, confirm on today's map that the new pricing knob alone still does
  nothing for famous-pair journeys — so that if nothing moves later, we know the
  question was always supply.* The §0.3 ladder at r₁ and at r₂ on the **adopted
  artifact** (sha per `tiebreak-fix-adoption` findings; no build), 22 `cb_pairs`
  famous pairs. **Instrument prior, barred from candidacy and from every `CRE-R`
  winner clause** (§3.3's carve-out). Pre-registered consequence: if its `C1`
  statistic shows no measured movement (|Δ| < 0.015) at both settings — the
  expected outcome, per the critique's re-scoring of Track 3's committed ladders in
  the adopted currency — then a later `CRE-R0` must be worded as *"the pricing
  device is inert on famous pairs at incumbent supply, as Track 3 found; the open
  question was and is supply"*, never as an undifferentiated joint null. If it
  shows material movement (≤ −0.05), that contradicts the committed prior and goes
  to the owner as a flag before Stage 2 begins.
- **`CRE-D2` — term-level cost accounting** (§0.3): collected in every sweep cell,
  no bar; licenses supply-knob attribution sentences.

**Stage 1 — builds and the structural screen** (per cell, cheap, no depth sweeps).
- **`CRE-C3` — coverage guard (owner-fixed).** *Plain: does this rule cut around ten
  thousand artists or more off the map entirely?* **Effect size: ≥ 10,000 artists
  lost vs the cell's cleaned substrate population → the arm is disqualified.** Below
  that: reported, never disqualifying (even `ALG-B`-`MK50`'s exclusion count — Track
  B results note §1 — survives; the ~10,000 line and that calibration are the
  owner's, design inputs §7). Committed Track B coverage figures are consumed by
  citation where the cell shape matches.
- **`CRE-C6` — supply screen and headroom report (revised at review, §9).** *Plain:
  for each journey, does this map offer anywhere meaningfully less famous to go,
  within one step of the journey?* Statistic, per pair: count of edges from the
  **1-hop neighbourhood of the d0 path node set** to artists with `fame_lb_pctl` at
  least **0.15 below that path's d0 interior median** (10× the instrument floor,
  deliberately) — the d0 node set alone was measured to false-negative 10 of 21
  pairs that its 1-hop neighbourhood clears, and the ladder reroutes whole paths,
  so the 1-hop frontier is the honest floor of what a press can reach. **Screen: a
  cell is screened out of Stage 2 iff its count of zero-supply pairs makes a
  `CRE-C1` median pass arithmetically impossible — more than half of the readable
  pairs (≥ 12 of 22 at the full draw, recomputed if `CRE-G3` drops pairs).**
  Otherwise the cell proceeds and the per-pair count distribution and per-pair
  1-hop headroom are **reported** — they are the supply diagnostic `CRE-R0` needs
  to say *where* movement was not found, and the denominator for §0.4's headroom
  companion. One carve-out: a screened cell that is a named isolating baseline
  still runs its sweep (a baseline is instrument, not candidate). Cells whose
  supply+pricing equals a committed Track B production-weights cell consume the
  committed `CRS-C5` result here instead of re-measuring.
- **Instrumentation row (§0.3):** record `_log_scaled` `low`/`high` per built cell.
- **`CRE-G3` — readability.** *Plain: we only compare journeys that exist in every
  variant being compared, and only when enough survive to say anything.* Endpoint
  survival on both cleaned substrates is verified for all 22 pairs; any pair losing
  an endpoint is removed from every cell. **Floor: a class is readable in a
  comparison only with ≥ 8 pairs having a non-empty d0 interior in every cell being
  compared** (journey semantics make forced-detour interiors count — §0.3); below
  the floor the comparison is recorded unreadable (the `CRS-G3` precedent). The
  obscure-endpoint classes are **already known unreadable at the committed draw**;
  nothing here reads them, and if any future bar is proposed that leans on
  obscure-endpoint behaviour, the parked redraw (owner's trigger, `NEXT.md`) is
  part of its price.

**Stage 2 — instrument gates, then depth sweeps** (the expensive stage).
- **`CRE-G1` — mirror equivalence.** *Plain: our measuring copy of the
  journey-builder returns exactly what the real app's router code returns on the
  same map, before we touch anything.* Three parts, each with its effect size:
  **(a)** at E-S0-P0, d0 journeys from the mirror bit-identical to the production
  router code run on the **same cleaned substrate**, all pairs (the `TAS-AM5a`
  precedent — the comparison is same-code-vs-mirror, same graph; the cleaned
  substrate is not the adopted artifact and no identity across *different* graphs
  is claimed). Any divergence = instrument failure; no read opens until fixed. The
  response to divergence is fixed and cheap — fix the harness — not a sweep
  expansion, so exact identity is the right bar. **(b)** every `P1` cell's d0
  journey is bit-identical to its `P0` isolating baseline's (the ramp term is zero
  at k = 0 by construction; Track 3 verified 16/16). Any divergence = the device
  fires at the wrong depth; instrument failure. **(c)** the ruler-frame assertion
  (§0.3: frame N = 74,151).
- **`CRE-G2` — device liveness and scale.** *Plain: when we turn the new knob to an
  absurd extreme, journeys actually change — and the toll the harness charges is
  exactly the toll the formula says, so a "no effect" answer is neither a dead wire
  nor a mis-indexed one.* Two parts: **(a)** at an instrument-only extreme ramp
  (r = 1.0, never a candidate), ≥ half of famous-pair journeys change at d1 vs
  `P0` in the same cell (the `TAS-AM5b` precedent). Below half → dead wire; no `P1`
  null is readable. **(b)** the recorded per-cell toll equals
  `r · k · Σ fame_lb_pctl` over the returned interiors, asserted at k = 1 and
  k = 10 (a `k`-indexing bug passes (a) and `G1` both; Track 3's realised-toll
  arithmetic is the precedent).
- **Sweeps:** the §0.3 ladder over every surviving cell. Committed as one JSON per
  cell (artifact sha, arm id, per-depth journeys, per-term stats, dropped-cell
  set), so any session can stop and hand off between cells.

**Stage 3 — findings note**, four-part shape (Measured / inferred in plain language /
weakest link / options), summary naming whatever cuts against it, every identifier
carrying its plain sentence.

**Seams, named now (the >8-task rule):** Seam 1 after Stage 0+1 (prior, D1 and
screen JSONs committed); Seam 2 between the two data sets' Stage-2 sweeps (each data
set's sweep JSONs are a complete committed artifact); Seam 3 before Stage 3. A
material amendment mid-flight is also a seam. Per-task appends to the retained
execution log throughout.

---

## §5 — Criteria

Each carries its threshold and its plain sentence, fixed here before any result.

- **`CRE-C1` — primary outcome: the bypass novelty gradient.** *Plain: after ten or
  more presses of "I know them", is the typical artist in the middle of the journey
  meaningfully less famous than the ones shown before any press?* Statistic, per
  pair: median interior `fame_lb_pctl` over the **pooled interior slots** of depths
  10–20 minus the same at depth 0 (pooling stated deliberately: it weights depths
  by path length, which interacts with `CRE-C4`'s shortening, and the alternative
  aggregation moves the statistic by up to ~0.025 — §9; one aggregation is fixed
  here so no result can pick between them). Arm statistic: median of per-pair
  deltas over the readable famous class; reported all-interiors and matched-only
  with per-depth null counts and the null-share trend (§0.4). **Pass is a
  conjunction (revised at review, §9): (i) arm median ≤ −0.05** (five percentile
  points obscurer — the Track B `C6` materiality precedent, and 3⅓× the instrument
  floor); **(ii) the 95% pair-level bootstrap upper bound of that median ≤ −0.015**
  (the arm is not merely point-estimated past the bar — computed on this design's
  own pairs at run time, no transfer needed); **(iii) reported beside it, always:
  the count of pairs at ≤ −0.05, the count at |Δ| < 0.015, and the leave-one-out
  range of the arm median** (a median at n = 22 can clear a bar by one pair; the
  knife-edge must be visible). Instrument floor: |Δ| < 0.015 = no measured
  movement. Between floor and material: "movement below the material bar",
  reported as such. A delta of ~0 on famous pairs is the `DD-F1`/`REQ-13` defect
  persisting in that arm, stated in those terms. Depth band 3–5 is additionally
  reported descriptively (the `REQ-18` "handful of presses" window) and is
  **never a bar** — `REQ-18` is an Expect, and nothing here optimises toward a
  press count.
- **`CRE-C2` — per-arm kill: hubness at depth (owner-fixed trigger, bar revised at
  review, §9).** *Plain: as you keep pressing, does the journey lean more and more
  on the map's most-connected artists — or park on them outright?* Statistic: share
  of interior slots in the top-1%-by-degree set, pooled per depth band, **using the
  production artifact's top-degree set as the primary reference** (own-graph sets
  are selection-order arbitrary at ceiling ties — Track B's weakest-link note — and
  the two references were measured disagreeing by as much as **0.61 on the same
  paths**, six times this kill's margin, so the choice is load-bearing and made
  here; the own-graph share is reported beside it). **Kill: band d10–20 share
  exceeds band d0–2 share by ≥ +0.10 absolute, OR band d10–20 share exceeds 0.50
  absolute.** The second clause exists because every measured descent arm moves the
  delta *negative* (base rates −0.06 to −0.01, clustered sd 0.012–0.026 — §9): a
  delta-only kill polices a direction the device does not travel, while the level
  clause catches what it actually could do — a union or unbounded arm parking
  depth journeys on hubs. Below both: reported, with the base rates quoted so a
  null is not mistaken for reassurance. First-path hub transit is tolerable by
  owner ruling and is reported, never gated.
- **`CRE-C3`, `CRE-C6`, `CRE-G1`–`G3`** — defined in §4 with their effect sizes.
- **`CRE-C4` — delivered payload floor (the `TB-P5H-7` consumption; bar revised at
  review, §9).** *Plain: after ten or more presses, is the journey still delivering
  a comparable number of artists, or has it mostly just got shorter?* Statistic,
  per pair: mean interior count over depths 10–20 divided by interior count at d0;
  arm statistic: median over pairs. **The binding form is baseline-relative — arm
  `C4` ÷ its isolating baseline's `C4` ≥ 0.70** — because the ladder itself
  lengthens paths as exclusions accumulate (the production arm's own ratio was
  measured at ~1.28, so an absolute ratio near 1 can hide a one-third payload loss
  against what the ladder does undisturbed; the relative form self-normalises on
  each substrate and needs no recalibration). The absolute median is **reported**
  beside it against a 0.75 reference line (the value separating the coherent-regime
  arm from the dominating-regime ones on the only measured ladder data — §9).
  Read **jointly with `CRE-C1` in every result read**: `C1` pass + `C4` fail is
  `CRE-R3` (descent by deletion), never a success. Lengthening is likewise
  reported and never rewarded (`REQ-14`).
- **`CRE-C5` — tag attribution (every tag cell; bar revised at review, §9).**
  *Plain: is the improvement actually coming from what the labels say — or would
  scrambled labels have done the same?* Statistic: Δgain = (tag cell's `C1`
  statistic) − (its isolating baseline's `C1` statistic), and the same for its
  scrambled-labels companion. **Entry condition: real Δgain ≤ −0.05** (an
  attribution question about a sub-material effect is not worth asking, and the
  originally drafted 0.015 entry sits at ~1 sd of the quantity itself).
  **Attribution holds iff the 95% pair-level bootstrap CI of the paired difference
  (real Δgain − companion Δgain) excludes zero** (the drafted 50%-ratio test was a
  ratio of two near-zero noisy quantities — heavy-tailed, effectively unbounded —
  §9). Attribution failing does not delete the cell's measured outcome; it bars
  every sentence of the form "tags did this" (`TAS-AM5c`'s any-cost artifact,
  pre-empted).

---

## §6 — Reads of results

Every read names the run state it presupposes. Instructions that keep specified runs
alive stand as their own sentences (the Track 2 stage-2 lesson).

- **Run state for any `CRE-R`:** `CRE-D3` and `CRE-D1` have committed outcomes;
  every non-branch-conditional Stage-2 cell in §0.2 has a committed sweep JSON on
  both data sets; every gate (`G1`–`G3`) has a recorded outcome. **The `S3` (UC)
  comparison cells are part of the specified run even though they cannot win; no
  `CRE-R` is readable while either is unrun.** **The probe cell E-S2-P0 is part of
  the specified run on every `CRE-D1` branch; no `CRE-R` is readable while it is
  unrun.** **Both `P1` ramp settings are part of the specified run in every cell
  that carries them; a read before both have run says so and names what is owed.**
  A read opened at any earlier state must name the unrun cells and licenses nothing
  beyond instrument claims.
- **`CRE-R0` — the null.** *Plain: nothing we tried makes the bypass button dig, on
  either data set.* Fires iff no non-staged arm passes `C1` on any readable class
  on either data set. **Its wording is constrained by `CRE-D3`:** with the prior
  confirmed, the null is stated as *"the pricing device is inert on famous pairs at
  incumbent supply, as Track 3 found, and changed supply did not unlock it — the
  open question the design tested is answered against supply-side unlocking"*,
  never as an undifferentiated failure. **It has a named sub-outcome the original
  draft lacked: "no viable pricing regime"** — the coherent-regime settings
  (r₁/r₂) moved nothing and the dominating regime is barred by the measured record
  (Track 3's similarity collapse), so no ramp setting both moves the gradient and
  stays plausibly coherent; that outcome, if it fires, goes to the owner as a
  statement about the device family, with the blind listen unspent. Licenses: the
  incumbent stands; `DD-F1` remains a standing defect; the measured deltas, `D2`
  accounting and `C6` headroom reports go to the owner as the map of where
  movement was and was not found. **Barred: "the family space is exhausted"** —
  this design ran two bounds of family (a), one member each of families (b) and
  (c), two ramp settings of one pricing device, and family (d) as reference only;
  the unrun remainder is named in the findings note, not waved at.
- **`CRE-R1` — a winner on `ALG-E`.** Presupposes the full run state. Fires iff a
  non-staged `ALG-E` arm passes `C1` (both binding clauses) with `C2` not killed,
  `C3` passed, `C4` ≥ its binding floor. Licenses: a recommendation input to the
  parked **cap-rule decision** (owner's), carrying: the blind listen owed before
  adoption (`REQ-38`), the `w_degree_hub` follow-up decision for that arm's graph
  (§0.3), and `D2`-licensed attribution sentences only.
- **`CRE-R2` — a winner only on `ALG-B`.** Same bars on an `ALG-B` arm. Licenses: a
  recommendation input to the parked **`ALG-B` adoption decision** (owner's),
  always quoted with: the §0.4 rows (composition, censoring, headroom); adoption
  retires every existing path-quality figure and owes a blind listen (`NEXT.md`
  standing notes); switching is the `BuilderConfig.algorithm` re-crawl decision
  (closed enum, `CS-P0e`).
- **`CRE-R3` — descent by deletion.** *Plain: the journey got "less famous" mainly
  by getting shorter — fewer artists delivered, not more discoveries.* Fires per
  arm on `C1` pass + `C4` fail. Never a success; reported to the owner as a shape
  finding only if no `R1`/`R2` winner exists, because the shape question (is a
  shorter-but-obscurer journey ever wanted?) is his parked candidate-pool decision,
  not this experiment's.
- **`CRE-R4` — the clear-winner rule (the owner's "until a clear winner emerges",
  made mechanical; margins revised at review, §9).** A **clear winner** is a
  non-staged arm that (i) meets `R1`'s bars on **both** data sets, or meets them on
  one while no other non-staged arm meets them anywhere; and (ii) **within its own
  data set**, leads every other passing arm by a **paired** `C1` difference on the
  common pair set of ≥ 0.05 whose 95% bootstrap CI excludes zero (the drafted
  unpaired 0.015 margin sits inside the sampling noise of the statistic it is
  applied to — §9; **no lead is ever computed across data sets, per §0.4** — a
  cross-data-set choice is presented as options with the headroom figures attached,
  never as a lead); and (iii) **was explored on no fewer ramp settings than any arm
  it beats** (no clear-winner call from an asymmetrically explored pricing axis).
  Anything short of that: the findings note presents the passing arms as options
  with consequences, no recommendation dressed as a finding, and the decision line
  states why it is the owner's (adoption, his ear, his risk acceptance).
- **Standing bars on every read:** no worldly-fame sentence; no within-remainder
  ordering; the quota-null citation rule (Track B's `R2` `ALG-E` null is "the
  router declines the quota edges *at production weights*", never "the quota rule
  cannot fix `DD-F1`"); `S3` sentences always carry both §3.1 halves; famous-pair
  first-path fame is not a scoring criterion (`PLA-R1`).

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

Rules: amendments are appended, never edited in place; an amendment written after
any result exists says so at its head and names the hazard (the
`TAS-AM3`/`NOV-AM1`/`FCF-AM1` disclosure precedent); a router-side tag arm, if
`CRE-D1` licenses one, is defined by amendment **before** it is built, with its
scrambled-labels control named in the same amendment.

### `CRE-AM1` — `S2`'s ceiling ranking gains within-artist vote weighting; appended 2026-08-03, AFTER the `WAV-` results existed and BEFORE any `CRE` stage ran

**Disclosure first, per this section's own rule.** This amendment is written with
the `WAV-` read's figures on the table
(`builder/analysis/2026-08-03-within-artist-votes/`, run earlier today): movement
0.1126 turnover vs rarity at λ = 1, redundancy −0.0072 vs rarity, mean-weight fame
correlation −0.5221. The hazard of amending post-result is fitting the design to a
known number; what bounds it here is that **the change adopts a scheme whose own
one-shot read FAILED its pre-registered conjunction**, on an owner ruling that
supersedes the failed bar's *consequence*, not its *figures* — nothing below
re-reads, re-runs, or re-scores anything in the closed `WAV-` record.

**The owner's ruling, 2026-08-03, verbatim in substance:** within-artist vote
weighting — an artist's higher-voted tags treated as more relevant than its
drive-by tags, relative to that artist's own vote distribution — is an obviously
sound way to discriminate between tags in this format, and is to be pursued.
Recorded context for the ruling: he had understood vote weighting to be part of
the previously assessed (`WGT-`) mechanism; it was not — `WGT-` assessed only the
absolute-scale scheme, so its "no evidence strength" recommendation was never a
verdict on this formulation. The direction question — the weighting pattern leans
*away* from famous artists (ρ = −0.52), which is what tripped `WAV-3`'s
undirected bar — **is ruled acceptable by the owner**: what counts as better is
his column, and the hazard `WAV-3`'s plain sentence named (leaning *toward* fame)
is the direction that did not occur. The `WAV-` README's closure stands as
written; a one-line pointer there marks this ruling.

**The change.** §3.2's single differing knob — the ranking that decides which
edges an over-budget node loses — becomes: **LB similarity re-weighted by the
`evidence_rel` agreement measure** (rarity-weighted `W4` agreement with
within-artist vote strength: `Σ idf·min(e_rel) over ∩ ÷ Σ idf·max(e_rel) over ∪`,
with `e_rel(a,l) = log1p(s)/log1p(s_max(a))` capped at 1, exactly as committed
and instrument-verified in `wav_read.py` — `WAV-0d`'s degeneracy check is the
proof that this measure reduces to rarity wherever votes are absent, which keeps
the dark-tail rule intact by construction). Everything else in §3.2 — union
source, post-symmetrise whole-edge ceiling, budget, largest-component prune,
unlabelled edges competing on LB similarity alone — is unchanged, so the
one-column isolation of every `S2` row survives: the knob is still "the ceiling's
ranking function", now with votes inside it.

**The empirically open question, gated rather than assumed.** `WAV-1`/`WAV-2`
establish the scheme moves selections materially without restating similarity.
What no read has measured is **attribution**: whether the movement comes from
*which tags the votes sit on*, or whether any within-artist weight spread of the
same shape would move selections the same way. That is `TAS-AM5c`'s any-cost
lesson at the vote layer, and it is gated at the sweep with `CRE-C5`'s existing
machinery: **every `S2` cell now carries a second companion — the within-artist
vote scramble** (each artist's label strengths permuted among its own labels
before `e_rel` is built, preserving the artist's vote-distribution shape and
therefore the mean-weight fame profile, destroying only which tag each vote
attaches to). `CRE-C5` applies to it verbatim — same entry condition (real
Δgain ≤ −0.05), same paired-difference CI test. Sentence licensing: **"tags did
this" requires beating the label-scrambled companion; "votes did this" requires
beating the vote-scrambled companion**; a cell that beats neither has its outcome
reported with no attribution sentence at all. `CRE-D1` is untouched — it tests
the owner's banding hypothesis, not this device — and the probe cell E-S2-P0
remains branch-proof and part of the specified run.

*Plain, for the record: the map-builder will now let a very-connected artist keep
the connections its own listeners' votes say are most representative of it —
and before any conclusion credits the votes for an improvement, we check that
shuffling each artist's votes among its own tags would not have produced the
same improvement.*

## §9 — Revision record (2026-08-03, before freeze, before any run)

The document as first committed (`c047d06`) was reviewed twice at the owner's
instruction before any arm was built: a repo-check review ("check the claims against
the repo") and an `ml-graph-analyst` critique. **Both reports, and the critique's
probe scripts, are the committed record at
`builder/analysis/2026-08-03-cre-prereg-critique/`.** This revision folded the
surviving findings in; the git diff against `c047d06` is the exact delta. Because
these are pre-run, pre-freeze corrections, they are revisions, not §8 amendments —
§8 governs from this commit forward.

**Result-bearing measurements that existed before this revision, disclosed:**

1. **The `CRE-D1` direction** (critique F3): the size-matched band difference on the
   adopted artifact measured **+0.08 — opposite to the owner's hypothesis** (popular
   pairs agree *more*). `CRE-D1`'s branch is therefore expected "not supported";
   the confirmatory run stands, and its criterion was re-specified knowing this
   figure — which is exactly the hazard the disclosure convention exists to name.
   The redesign (size-matching, absolute bar, coverage reporting) follows the
   critique's pre-specified proposals rather than anything fitted to a desired
   outcome, and the expected branch *removes* cells rather than adding any.
2. **The pricing prior** (critique F1): re-scoring Track 3's committed ladders in
   the adopted currency showed the ramp inert on famous-famous pairs at incumbent
   supply at every strength ever run. `CRE-D3` and `CRE-R0`'s constrained wording
   were added knowing this.

**Material changes, each traceable to a finding:** §3.2 rebuilt on the committed
post-symmetrise whole-edge-deletion order (repo-check #1 — the drafted order
reproduced the deleted `pre_symmetrise` defect and broke the one-column isolation);
`CRE-D2` declared as new code, dependency (5) (repo-check #2); `CRE-G1` restated as
same-substrate code-vs-mirror identity plus the d0-identity and frame assertions
(repo-check #3, critique F12a/F5); ruler frame definition corrected to the adopted
frame with mapped out-of-frame values (critique F5); ladder fixed to journey
semantics with the uniform-drop rule and per-cell-comparison readability floor
(critique F2); ramp bracket moved to 0.01/0.03 (critique F7); `CRE-G2` gained the
toll-arithmetic assertion (critique F7); `CRE-C1` became a conjunction with
bootstrap bound and knife-edge reporting, aggregation fixed (critique F6); `CRE-C2`
gained the absolute-level clause and base-rate reporting (critique F4); `CRE-C4`'s
binding form became baseline-relative at 0.70 (critique F8 — the relative form
self-normalises, making F8's proposed pre-registered recalibration unnecessary,
which is the one place this revision deliberately diverges from the critique's
exact proposal); `CRE-C5` re-based on a paired-difference CI at a material entry
bar (critique F11); `CRE-C6` made per-pair on the 1-hop frontier — with the
screen-out threshold set at arithmetic impossibility of a `C1` median pass (> half
the readable pairs) rather than the critique's proposed ≥ 8, the second deliberate
divergence, chosen because the ≥ 8 form would screen cells that could still pass
on their readable majority; §0.4 gained the censoring and headroom rows (critique
F10); `CRE-R4` margins re-based paired, within-data-set, with the
equal-exploration clause (critique F6/F10/F12c); `CRE-R0` gained the `D3`-worded
null and the no-viable-pricing-regime sub-outcome (critique F1); `w_floor`
exposure re-scoped to the supply knob (critique F12a); `_log_scaled`
instrumentation row added (critique F12b); §3.3 gained the `REQ-27` sentence
(repo-check #9) and the `D3` carve-out; E-S2-P0 unmarked as branch-conditional
(repo-check #6); plus the smaller wording corrections in repo-check #4, #5, #7,
#8 and #10.
