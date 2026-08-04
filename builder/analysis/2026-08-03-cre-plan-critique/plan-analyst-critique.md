# CRE execution-plan critique — `ml-graph-analyst` report (2026-08-03)

**Provenance:** dispatched by the plan's authoring session as the quantitative half of
the review split (the claims-vs-repo half is the plan's own "Verification record"
section). The agent ran the probes in this directory and returned this report text in
its final response; its output rules bar it from writing report files, so the
controller committed the text **verbatim** — nothing below was edited beyond
un-escaping HTML entities introduced in transport. The probe scripts and their JSON
outputs are the agent's own writes; `README.md` (the agent's) describes what each
measures and the artifacts/shas each reads.

**Consumed by:** the plan's revision record
(`docs/superpowers/plans/2026-08-03-cap-reeval-execution-plan.md`), which names each
finding folded in and each divergence.

All cell figures come from the **pre-drop** Track B `.bin` cells in
`builder/scratch/cb-cells/` (the only existing artifacts with union/uncapped supply)
and from the adopted artifact, sha `4cb84ef9…b061dc8`, asserted.

---

# BLOCKING

## B1 — `CRE-G2`(b) as implemented is a tautology, and it is the *only* device check `CRE-D3` has

**Plan:** T2 `cre_ladder.assert_toll_arithmetic`; T3 Step 1; T9 Step 1.

**Claim checked:** that the plan's realised-toll assertion catches the k-indexing bug class the prereg names (`CRE-G2`(b), Track 3 precedent).

**Check:** source reading of the plan's own code block against `mirror.py::_dijkstra`.

**Result — it cannot fail.** `assert_toll_arithmetic` computes `got = Σ rows["ramp_fame"]` from `term_breakdown`, where each row is `cfg.w_known_ramp_fame_pctl * n_known * fame_pctl[v]` over `v ∈ path[1:-1]`, and compares it to `expected = cfg.w_known_ramp_fame_pctl * n_known * Σ fame_pctl[v]` over the same `v`, with `n_known` recomputed by the identical expression in both. That is the same closed form on both sides of the `==`. It never touches `_dijkstra`. It is an algebraic identity up to floating-point associativity, and `tol=1e-9` absorbs that. The plan's own docstring describes a different check — *"Recompute the full path cost with the device on and with it off; the difference must equal the formula"* — which the code does not do.

**Why this is blocking rather than material:** the other two device checks are also inert by construction.
- `CRE-G1`(b) (d0 identity) holds because `ramp_fame_on = ramp_fame != 0.0` is False at k = 0, so the term is not added. It is true whether or not the term is plumbed correctly.
- `CRE-G2`(a) (r = 1.0 liveness) is run in T8 only on the eight sweep cells that carry a `P1` arm. **`CRE-D3` is not one of them** — it runs on the adopted artifact in Stage 0, before T8 exists.

So `CRE-D3` — whose expected null is written *verbatim* into `CRE-R0`'s null wording (prereg §4, §6) — currently has **zero** live checks distinguishing "the device is inert on famous pairs" from "the device is not connected".

**Minimal fix, two lines and one call:**
1. Add to `_dijkstra` in the marked copy: after the loop, `if stats is not None: stats["path_cost"] = dist.get(target)`. Then assert `abs(Σ over all term_breakdown rows of Σ terms − stats["path_cost"]) < 1e-9`. This is the cheapest genuinely independent form: it compares the breakdown against the *search's own accumulated cost*, so a wrong `k` inside the search, a term added or omitted inside the search, or a wrong fame array all fail it. It requires `term_breakdown` to carry every live term (see M14).
2. Run `CRE-G2`(a)'s r = 1.0 liveness inside `cre_d3.py` (22 pairs × 2 depths, seconds). Record it in `cre_d3.json` beside the null.

---

# MATERIAL

## M2 — On union/uncapped cells the ruler-null class is dominated by **never-fetched** artists, and plan pin 2 prices exactly those at maximal obscurity

**Plan:** "Decisions this plan fixes" pin 2; T1 `Ruler.device_pctl_of` / `.arrays`.

**Claim checked:** pin 2's stated reason — *"an LB null is an absence of recorded listeners, i.e. below the measurement floor; under the novelty-likelihood construct that is maximal obscurity."*

**Check:** `crp_absent.py` (is the snapshot's key set exactly the two MK50 node sets?), `crp_ruler.py` (per-cell coverage split into *absent key* vs *present-but-null*).

**Result.** The union snapshot is **exactly** (adopted node set) ∪ (ALG-B-MK50 node set): 93,067 keys, 0 in the snapshot not in that union, 0 in the union not in the snapshot. So a node a union or uncapped cell keeps but both MK50 builds stranded **was never in the fetch population** — "absent" is a population artifact, not a listener count. Pin 2's justification is false for that class.

| cell (Track B, pre-drop) | nodes | absent from snapshot | present but null | ruler-null share |
|---|---|---|---|---|
| adopted `graph-t15-tiebreakfix` | 74,193 | 0 | 42 | **0.06 %** |
| ALG-E-MK50 | 74,157 | 0 | 33 | 0.04 % |
| ALG-E-MK100 | 74,732 | 315 | 33 | 0.47 % |
| ALG-E-TUw-50-50 | 74,956 | 527 | 33 | **0.75 %** |
| ALG-E-UC | 74,956 | 527 | 33 | 0.75 % |
| ALG-B-MK50 | 68,467 | 0 | 4,080 | **5.96 %** |
| ALG-B-TUw-50-50 | 74,428 | 4,546 | 4,081 | **11.59 %** |
| ALG-B-UC | 74,960 | 4,971 | 4,081 | **12.08 %** |

The censoring is **supply-knob-correlated**: ×19 from MK50 to TU/UC on ALG-E, ×2 on ALG-B. §0.4's censoring row is written data-set-wise, at the measured MK50 figure of ~6 % — it does not cover this, and the plan's `Ruler` merges absent and null into one bucket so the sweep JSONs cannot separate them after the fact.

**Direct answer to the question as asked (does the pin's *value* matter?): no — it is inert.** The three candidate values are within each other by less than a quarter of one hop:

| device price of a null | toll advantage over the alternative, r₂ = 0.03, k = 20 | as a share of `w_hop` = 0.02 |
|---|---|---|
| exempt entirely (0) vs `frame.pctl(0)` = 6.743e-06 | 4.0e-06 | 0.02 % |
| `frame.pctl(0)` vs min measured pctl (8.092e-05) | 4.5e-05 | 0.22 % |

So exempting nulls, pricing at `pctl(0)`, and pricing at the minimum measured value are **operationally identical**. The pin cannot change a result through its value.

**What does matter is the class, not the value.** Against the *measured* obscure tail:

| null's ramp advantage over… | r₁ = 0.01, k = 10 | r₂ = 0.03, k = 10 | r₂ = 0.03, k = 20 |
|---|---|---|---|
| p1 measured (pctl 0.00242) | 0.0002 (0.01 hops) | 0.0007 (0.04 hops) | 0.0014 (0.07 hops) |
| p5 measured (pctl 0.0362) | 0.0036 (0.18 hops) | 0.0109 (0.54 hops) | 0.0217 (**1.09 hops**) |
| p10 measured (pctl 0.0818) | 0.0082 (0.41 hops) | 0.0245 (**1.23 hops**) | 0.0491 (**2.45 hops**) |
| p50 measured (pctl 0.4715) | 0.047 | 0.141 | 0.283 |

At r₂ and ten-plus presses, an unmeasured node is worth **one to two and a half whole hops** more than a genuinely-measured 5th-to-10th-percentile artist. On a TU/UC cell the device therefore preferentially routes into precisely the class its own score cannot read, and §0.4's response is to label the result "descent partly unmeasurable" — i.e. the pin manufactures the condition the disclosure was written to report.

Structural profile of the ALG-E-TU absent class (`crp_absent.py`): 527 nodes, median degree 7 vs 17 for the rest, max degree 50, 0.30 % of edge endpoints — peripheral, not hubs, but reachable.

**Minimal fix (no bar moves; a re-fetch is barred by `FAM-AM2.3`):**
1. Split the counter. Every sweep JSON reports `interiors_absent_from_snapshot` and `interiors_null_in_snapshot` separately, and §0.4's d0→d20 trend is reported for both. One extra integer per depth.
2. Decide the device treatment of the never-fetched class deliberately and record it as its own pin. Pricing it at maximal obscurity is the choice that maximises steering into unmeasurable territory; pricing it at the frame median is the choice that makes the device ignore it. Either is defensible; the plan currently makes the first choice under a justification that is factually wrong for that class.

## M3 — The uniform-drop comparison groups are never defined, and the staged `S3` cells are not excluded from them

**Plan:** T11 Step 1, *"Uniform drop, per comparison … computed over each comparison group"*; and `CRE-C1`'s per-cell figures immediately below it.

**Claim checked:** whether the plan's scoring-time application is equivalent to the committed in-run `drop_infeasible_uniformly` + `inherited` mechanism, and whether any group spans sweep files.

**Check:** source reading of `run_arms.py::drop_infeasible_uniformly` and `walk`, against the plan's T9/T10/T11 structure; `crp_kinds.py` for the leading indicator.

**Result — the placement is fine; the partition is the gap.** The `inherited` machinery exists because a drop set computed inside one invocation spans only that invocation. T11 reads *every* sweep JSON, so no group can span an unread file, and the scoring-time application is strictly stronger than `inherited`. **Q6's headline concern does not fire.**

But two things are unpinned and both can move a knife-edge result:

- **`CRE-C1` has no canonical drop set.** C1's pass/fail is a per-arm bar; "per comparison group" leaves the headline number undefined, and F6's leave-one-out swing (0.019, larger than `CRE-R4`'s pre-revision margin) says one pair moves it.
- **If the staged `S3` cells sit in the candidates' group, a cell barred from candidacy deletes data from every candidate.** `walk_journey` **breaks** at the first empty interior and pads the rest with `(None, "none")`, so one early termination in UC removes every deeper depth for that pair from *all* compared cells.

Measured leading indicator for that risk — direct adjacency at d0 (`crp_kinds.py`), which is what makes interiors run out:

| cell | `natural` | `forced` (adjacent at d0) | `adjacent_only` |
|---|---|---|---|
| adopted | 21 | 1 | 0 |
| ALG-E-MK50 | 21 | 1 | 0 |
| ALG-E-MK100 | 18 | **4** | 0 |
| ALG-E-TUw-50-50 | 21 | 1 | 0 |
| ALG-E-UC | 16 | **6** | 0 |
| ALG-B-MK50 / MK100 / TU | 22 | 0 | 0 |
| ALG-B-UC | 20 | 2 | 0 |

All six ALG-E-UC adjacencies are in `ff-top01pct` — 6 of that class's 10 pairs. (This also confirms the critique's F2 integer bound of "at least 5 and at most 7 of 10", exactly, at 6.)

**Minimal fix:** pin one canonical group per data set = that data set's non-staged cells plus their named isolating baselines; compute every `S3` comparison in its own separate group; compute the scramble companions inside the tag cell's group. Commit all group memberships and all dropped sets, and state which group produced each reported `C1`.

## M4 — Plan pin 1's multiplicative key collapses the zero-agreement block onto the MBID tie-break

**Plan:** pin 1; T6 Step 2, `doomed = sorted(result[node], key=lambda v: (strength(node, v) * a_eff[v], _desc(v)))[:excess]`; T6 Step 3's degeneracy claim *"a constant multiplier preserves the order and the tie rule"*.

**Check:** `crp_key.py` (agreement distribution over the adopted artifact's 449,003 undirected edges, using the committed `five_frames()` `W4` and `log(N/df)` idf); `crp_absent.py` part C (IEEE double behaviour of `x → fl(x·0.15)`); `crp_uc.py` part C (zero block vs excess in the UC union pool).

**Result — two distinct order problems, one of them large.**

*(a) The floating-point half of the question is safe but the stated argument is wrong.* `x → fl(x·c)` for `c > 0` is monotone **non-decreasing**, so an inversion is impossible — two equal strengths can never separate. A **collapse** of two distinct strengths is possible, and at `c = GLOBAL_NEUTRAL_FALLBACK = 0.15` it happens on **13.36 %** of adjacent double pairs (26,714 of 200,000 tested). On realistic inputs it does not bite: **0 collapses** among the adopted artifact's 1,445 distinct edge scores. So the degeneracy gate will pass today; the sentence justifying it ("a constant multiplier preserves the order") is not true in IEEE arithmetic and should not be relied on as the reason.

*(b) The arithmetic half is the real one.* Agreement is exactly 0 whenever the label intersection is empty, and `strength × 0 = 0` annihilates similarity:

| quantity (adopted artifact, `W4`, rarity-weighted) | value |
|---|---|
| undirected edges | 449,003 |
| edges with an unlabelled endpoint (→ neutral rule) | 74,671 (16.63 %) |
| edges with a measured agreement | 374,332 |
| **measured edges with agreement exactly 0** | **14,426 = 3.85 %** of measured, 3.21 % of all edges |

Every one of those gets key `0.0` and is ordered by `_desc(v)` — **highest MBID first, LB similarity playing no part whatsoever**. At an over-budget node the zero block is always the first tranche deleted, and within it a strength-0.99 edge and a strength-0.01 edge are indistinguishable. In the ALG-E-UC union pool there are 37,056 nodes above degree 50 (median excess 52, median zero-agreement edges 1), and at **2.08 %** of them the zero block is at least as large as the excess — meaning *every* deletion at those nodes is decided by MBID alone. (UC's pool is a superset of TU's top-50-union pool, so this is indicative, not exact.)

This also strains prereg §3.2's constraint that "tags only re-order, re-weight, or remove" and never "veto by absence": a zero factor is a veto by *presence of disagreement*, and it discards the ordering the prereg says the pool retains.

**Minimal fix, free and behaviour-preserving where products are distinct:** change the sort key to `(strength(node, v) * a_eff[v], strength(node, v), _desc(v))`. This (i) restores LB-similarity ordering inside the zero block and inside any product tie, (ii) makes the degeneracy gate's byte-identity **exact** rather than empirically-true, and (iii) changes nothing anywhere the products already differ. It is a device pin, not a bar.

## M5 — Plan pin 3 (nulls sorted last in the victim rule) mechanically inflates §0.4's null-share trend

**Plan:** pin 3; T2 `cre_ladder.victim_key`.

**Claim checked:** whether pin 3 is a faithful operationalisation of prereg §0.3's *"Victim = the interior with the highest `fame_lb_pctl`; ties and ruler-null interiors ranked by `pop_raw` then lowest MBID."*

**Check:** source reading of the plan's `victim_key` against the prereg sentence; exposure from `crp_ruler.py`'s per-cell null shares.

**Result.** The prereg sentence is genuinely underspecified — it says nulls are ranked by `pop_raw`, but never says *where* the null group sits relative to the measured group. The plan pins them **last**. The implementation is correct for the pin (`key[0] = 1.0` for nulls, `−f ≤ 0` for measured, `min()` over the tuple). But the pin has a consequence the plan does not name:

**a ruler-null interior can never be bypassed while any measured interior exists**, so the exclusion set is composed exclusively of measured artists, and the null share of interiors is pushed upward with depth by the victim rule itself, independent of any descent. §0.4's trigger — *"an arm whose null share rises by more than 0.05 from d0 to the d10–20 band has its `C1` reported as 'descent partly unmeasurable'"* — can therefore fire on an arm that did not descend. Exposure: 6 % of ALG-B-MK50 nodes, 12 % of ALG-B-TU/UC nodes, and (M2) the union arms' null class is the arm-added one. Magnitude on realised paths is **unmeasured** — it needs the cells.

The opposite pin (nulls first) has the mirror problem: it bypasses the unmeasurable artists immediately and never delivers them at depth. Neither is "right"; the point is that one of them is being chosen silently and it interacts with a pre-registered reporting trigger.

**Minimal fix:** keep the pin, name the interaction in the plan, and record beside every §0.4 trend the count of depths at which a null interior was present and un-bypassable. That makes the mechanical component of the trend separable from the descent component at read time.

## M6 — `CRE-C4`'s baseline-relative denominator is cross-data-set for B-S0-P0 and undefined for E-S0-P0

**Plan:** T11 Step 1, *"binding = ratio to the isolating baseline's `C4` ≥ 0.70"*, mechanised off §0.2's baseline column.

**Check:** reading §0.2's baseline column against the plan's mechanisation; `crp_kinds.py` for the denominator-size half.

**Result.** §0.2 gives **B-S0-P0's** isolating baseline as **E-S0-P0** — a different data set. Mechanising the plan's rule yields `C4(B-S0-P0) ÷ C4(E-S0-P0)`, a cross-data-set ratio, which §0.4 bars for reads and which defeats the exact rationale §9 records for adopting the relative form ("self-normalises on each substrate"). And **E-S0-P0** has no isolating baseline at all ("—"), so the anchor cell has no binding `C4`.

Separately, `C4`'s per-pair denominator is the d0 interior count, and a `forced` d0 journey has very few interiors. Adjacency at d0 is arm-correlated: 1/22 (MK50, TU) → 4/22 (MK100) → 6/22 (UC). So the supply knob itself sets the smallest, least stable denominators on the arms that add connections.

**Minimal fix:** name both cases explicitly in the plan. E-S0-P0's `C4` is reported absolutely against the 0.75 reference line with "no binding form" stated. B-S0-P0's cross-data-set denominator is a §8 amendment question for the owner (it changes how a frozen criterion is computed), not something to mechanise silently — and the plan should stop before it, not through it.

## M7 — The guard/journey conflict is resolved correctly but only in a docstring, contradicting a held-constant row

**Plan:** T2 `cre_ladder.py` docstring, *"The mirror cfg runs with `guard_min_intermediary=False` here BECAUSE `journey()` itself performs the guard's masked re-run."*

**Claim checked:** whether this is a divergence from prereg §0.3's held-constant row *"`guard_min_intermediary` on in every sweep cell"*, and what happens if it is not honoured.

**Check:** source reading of `mirror.py::find_path_mirror` against `pathfinding.py::find_journey`; `crp_kinds.py` for exposure.

**Result — the plan's resolution is right and it is load-bearing.** The mirror's guard, on a two-node path, re-runs with the edge masked and returns whatever that gives, **including `None`**. `find_journey` returns `(path, "adjacent_only")` in that case. So with the guard *on*, `journey()` would receive `None`, report `"none"`, and `walk_journey` would break and pad — deleting the pair from that depth onward, and then (via the uniform drop) from **every compared cell**. That is precisely the vanishing-adjacent-pair failure prereg §0.3's journey-semantics row exists to prevent.

But it is a divergence from an explicit held-constant row, and it lives only in a docstring — not in "Decisions this plan fixes", where the plan records its other seven pins.

**Measured exposure at d0: zero.** `adjacent_only` occurred on 0 of 22 pairs in all nine cells checked (`pairs_lost_under_mirror_guard_true` = 0 everywhere). The risk is at depth, after exclusions remove the detour nodes — unmeasured.

**Minimal fix:** promote it to pin 8 with its reason, and add `assert cfg.guard_min_intermediary is False` at the top of `journey()` so the two mechanisms can never both be live.

## M8 — On the D1-supported branch, the `S2` device is structurally inert on a third of ALG-B nodes

**Plan:** T6 Step 1, *"One agreement table per kind, built **once** on the committed machinery and applied by MBID in every cell."*

**Check:** `crp_key.py` part D — the committed frames are built over `graph_mbids()`, i.e. the **adopted artifact's** MBIDs (`tas_common` → `ct_common`), so any artist outside that set has no `W4` entry by construction, not because it lacks tags.

**Result.**

| cell | nodes | outside the adopted MBID set | no `W4` label at all |
|---|---|---|---|
| ALG-E-TUw-50-50 | 74,956 | 797 (1.06 %) | 13,651 (18.2 %) |
| ALG-B-MK50 | 68,467 | 18,874 (27.6 %) | 24,097 (**35.2 %**) |
| ALG-B-TUw-50-50 | 74,428 | 23,420 (31.5 %) | 28,899 (**38.8 %**) |

At every node with fewer than two measured agreements, `a_eff` is the single constant `GLOBAL_NEUTRAL_FALLBACK = 0.15` and `cap_tag_limited` degenerates to `cap_trimmed_union`. That is 24.3 % of adopted nodes overall — but only **5.3 %** of nodes at degree ≥ 40, so on ALG-E the device is live where it matters. On ALG-B it is not: a third of the population is unlabelled for a population reason.

Reachable only on the `CRE-D1` "supported" branch (expected not to fire), which is why this is material-conditional rather than blocking.

**Minimal fix:** record the labelled-node share and the ≥2-measured-agreement share in every `S2` manifest, and make it a stated licensing constraint on any `CRE-C5` attribution sentence for a B-S2 cell.

---

# MINOR

**m9 — `CRE-G1`(b)'s comparator does not resolve for the two `P1b` cells.** §0.2's isolating baseline for E-S1-P1b and B-S1-P1b is the **P1a** cell, not a P0 cell, so T9's "bit-identical to its **P0** isolating baseline's d0 journey … which §0.2's baseline column gives you mechanically" is self-contradictory for those two. Pin the comparator as the supply-matched P0 cell (E-S1-P0 / B-S1-P0) so the assertion is against a device-off cell, which is what makes it a device test rather than a ramp-size test. *Ordering itself is clean — see V2.*

**m10 — a test whose name claims more than its assertion.** `test_device_pctl_prices_nulls_below_every_measured_value` asserts `ruler.device_null_pctl < 0.001`. Measured: null price **6.743e-06**, minimum measured pctl **8.092e-05**. The property holds, but a value of 5e-4 would pass the test and violate the name. Assert against the frame minimum directly.

**m11 — the manifest sidecars cannot be committed.** T5 Step 3 and T6 Step 4 say "manifest sidecars committed to git (the bins are gitignored)", but `.gitignore:25` ignores `builder/scratch/` **wholesale**. `git check-ignore -v builder/scratch/cb-cells/ALG-E-uncapped-none.bin.json` → ignored; `git ls-files builder/scratch/` → empty. The T5/T6 commit pathspecs name only `builder/analysis/…`, so the manifests will silently not be committed, and the standing artifact-identity rule depends on them. Follow Track B's own precedent: mirror every manifest into a committed `analysis/…/cre_builds.json`.

**m12 — `CRE-C6`'s "readable pairs" denominator is ambiguous, and its null treatment contradicts pin 2.** (a) `CRE-G3` has two devices — global endpoint-survival removal and the *per-comparison* ≥8 floor. The C6 screen is per-cell, so "more than half the readable pairs … recomputed under `CRE-G3` drops" must mean the endpoint-survival set; the plan does not say so. (b) qualifying artists are "measured-only", which removes 6–12 % of the ALG-B frontier from the supply count while pin 2 prices exactly that class as maximally obscure for routing. (c) a d0 path with no measured interior has no median and the statistic is undefined — possible on ALG-B. Pin all three. *The ≥12-of-22 arithmetic itself is correct and copies §4 verbatim (V6).*

**m13 — the §0.4 headroom companion is not comparable across supply arms.** Measured 1-hop frontier size (`crp_uc.py`): ALG-E-MK50 mean **130** nodes, ALG-E-UC mean **8,853** (max 22,350 ≈ 30 % of the graph) — a factor of 68. §0.4 introduced "C1 as a fraction of the cell's own measured 1-hop headroom" to make the two *data sets* commensurable; computing it per cell (T11) produces a ratio whose denominator the supply knob sets, so it cannot be read across supply arms either. State the denominator beside every companion figure.

**m14 — `term_breakdown` omits four live-in-principle terms and hardcodes the RAW floor branch.** It carries `sim`, `jump_raw`, `floor_raw`, `hop`, `ramp_fame` only; `avoid`, `w_degree_hub`, `toll_s`/`toll_hops` and `w_known_thresh_pctl` are absent, and `_relaxed_floor` is called with the RAW constants unconditionally. All correct for this design, and the plan says so — but if B1's total-cost cross-check is adopted they must be included, or asserted zero/off at function entry, or the cross-check will fail spuriously.

**m15 — empty-interior depths are not pinned.** An `adjacent_only` depth records a two-node path (not `None`), so `drop_infeasible_uniformly`'s rule does not drop it. It then contributes **0** to `CRE-C4`'s mean interior count and nothing at all to `CRE-C1`'s pooled slots. Consistent with the `run_arms.py` precedent, but CRE's union arms create adjacency far more often (M3's table), so say explicitly which of the three treatments applies.

**m16 — a silently widened production predicate.** `journey()` builds avoidance from `[e.node for e in excludes if e.reason != KNOWN]`; production uses `if e.reason == DISLIKE`. Equivalent for the two defined reasons and identically empty on the all-`known` ladder — but this is a byte-identity harness, and the two differ the moment a third reason exists.

**Inherited, named once and not a plan defect:** §4's C6 screen says zero-supply pairs make a `CRE-C1` median pass "arithmetically impossible". That is a heuristic, not an identity — C6 is measured on the **d0** 1-hop frontier, which §4 itself calls "the honest **floor** of what a press can reach", while the ladder reroutes whole paths over twenty presses. Zero supply at d0 does not bound the d10–20 delta. Frozen prereg wording; the plan copies it faithfully; out of scope for a fix.

---

# Verified clean

**V1 — Q8, feasibility.** Measured production-weight `find_journey` per famous pair (`crp_uc.py`): ALG-E-MK50 **0.005 s** (max degree 50, 448,810 edges), ALG-E-UC **0.436 s** (max degree 15,631, 3,118,832 edges), ALG-B-UC **0.568 s** (max degree 17,883). Projected to the full 22 × 21 ladder: **2.5 s / 202 s / 262 s**. UC is 87–114× the capped cost, exactly as the plan says — but the whole UC ladder is under five minutes. **No stated budget or background discipline is needed beyond what the plan already says.** For calibration, the plan's own "~8–15 min per capped cell" is roughly 200× the measured capped cost, so the T9/T10 time estimates are conservative by two orders of magnitude and should not be used for scheduling.

**V2 — Q7, baseline ordering, both `CRE-D1` branches.** Every `P1` cell's §0.2 isolating baseline is swept earlier in T9/T10's stated order: E-S1-P1a←E-S1-P0 ✓, E-S1-P1b←E-S1-P1a ✓, E-S2-P1a←E-S2-P0 ✓ (branch), B-S0-P1a←B-S0-P0 ✓, B-S1-P1a←B-S1-P0 ✓, B-S1-P1b←B-S1-P1a ✓, B-S2-P1a←B-S2-P0 ✓ (branch). Non-P1 dependencies also resolve: E-S3-P0←E-S1-P0, B-S1-P0←B-S0-P0, B-S3-P0←B-S1-P0, and B-S0-P0←E-S0-P0 which T9 sweeps before T10 begins. All 17 §0.2 cells plus companions are covered by T5/T6 builds and T9/T10 sweeps. *(The P1b comparator **wording** is m9; the ordering is sound.)*

**V3 — journey semantics are load-bearing and correctly required.** `crp_kinds.py` measures direct adjacency at d0 at 6/22 on ALG-E-UC (all six in `ff-top01pct`, i.e. 6 of that class's 10 pairs), 4/22 on ALG-E-MK100, 1/22 on MK50 and TU, 2/22 on ALG-B-UC, 0/22 on the ALG-B capped cells. This confirms the critique's F2 integer bound (5–7 of 10) exactly. `find_journey` recovers all of them as `forced`; `adjacent_only` is 0/22 everywhere at d0.

**V4 — the plan's masked-detour call is equivalent to production's `forbidden_edge`.** Production bans `{(a,b),(b,a)}`; `_dijkstra` masks only `(source → target)`. The reverse direction can never be relaxed because the loop breaks the moment `target` is popped. No divergence.

**V5 — the ruler reproduces `CRE-G1c` and `FAM-AM1.6` exactly.** Measured on the adopted artifact + committed snapshot: frame **N = 74,151** ✓ (= 74,193 nodes − 42 nulls); `frame.pctl(0)` = **6.743e-06**, matching the plan's stated "≈ 6.7e-6"; the snapshot is exactly the two MK50 node sets so no key is unaccounted for. The plan's toy-frame test is arithmetically correct in all five of its expected values, including the above-maximum clause.

**V6 — `CRE-C6`'s screen arithmetic and the baseline carve-out.** T7 copies §4's screen sentence verbatim; "more than half of 22" = ≥ 12 ✓, and the unit test's 12-screens / 11-does-not pinning is right for an even readable count. The screened-but-baseline carve-out appears in both T7 ("encode §0.2's baseline column so this is mechanical") and T9's cell list ("plus screened-but-baseline cells"), so a screened isolating baseline still sweeps and `C4`'s relative form and `C5`'s Δgain remain computable. *(Ambiguities are m12.)*

**V7 — Q2(b), the neutral-median rule against §3.2's sentence.** It preserves the promise. At a node with fewer than two measured agreements every `a_eff` is one constant, so its edges rank by LB similarity alone — that is literally §3.2's "unlabelled-endpoint edges ranked by LB similarity alone in the same pool". At a labelled node the unlabelled block enters at that node's own median, i.e. neutrally in rank terms. The asymmetry is real and measured — the two endpoints of an unlabelled edge apply multipliers differing by a median of **0.050**, p90 **0.150**, and by more than 0.10 on **26.4 %** of such edges; node-local medians span p10 0.050 / p50 0.180 / p90 0.381 and are weakly fame-correlated (Pearson +0.094; median 0.150 at `fame_lb_pctl ≤ 0.50` vs 0.216 at ≥ 0.75) — so an unlabelled edge can be doomed at one endpoint and safe at the other, and the stricter endpoint wins. **But that breaks nothing the prereg promises**: whole-edge deletion already means the stricter endpoint decides in `cap_trimmed_union`, tags still never create an edge, and absence still does not veto. The order problem in pin 1 is M4 (zero agreement), not the neutral median.

**V8 — Q6's placement question.** Applying the uniform drop in the scorer rather than the walker is equivalent to the committed `inherited` mechanism, because T11 reads every sweep JSON and no comparison group can span an unread file. The gap is the undefined partition (M3), not the placement.

**V9 — pin 1's neutral rule is faithful to the committed source.** `wav_pass`/`frame_pass` resolve a `None` agreement to the median of the owner's own measured values when there are ≥ 2, else `GLOBAL_NEUTRAL_FALLBACK = 0.15`. Plan pin 1 restates this exactly, and `agreement_table.a` returning `None` when either endpoint is unlabelled matches `wav_pass`'s `if not own or not cand` branch.

---

## Weakest link in the above

The cell-level figures (M2's coverage table, M4's zero block in the UC pool, M8's ALG-B tag coverage, V1's runtimes, V3's adjacency counts) come from **pre-drop Track B builds**, not from CRE's cleaned substrates, which do not exist yet. What would falsify them: the cleaned rebuilds changing which artists strand, which would move the absent-node counts and the adjacency counts. I would defend the *structural* claims regardless — that the snapshot is exactly the two MK50 node sets (so absent means never fetched), that `strength × 0` is MBID-ordered, that `assert_toll_arithmetic` is a tautology, and that the guard and `journey()` cannot both be live — because none of those depends on a build. I would abandon cheaply any specific count.

Everything above was measured on one slice: one pair draw (the committed 22), one set of cells. Nothing here has been reproduced on a second slice, and I have not measured any ladder at depth — every depth-dependent claim (M3's cascade magnitude, M5's null-share inflation, M7's at-depth exposure) is **derived from mechanism, with magnitude unmeasured**, and I have labelled each as such rather than quoting a point estimate.
