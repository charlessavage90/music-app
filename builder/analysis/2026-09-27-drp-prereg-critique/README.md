# `DRP-AM1` stage-1 critique: derivation only (`ml-graph-analyst`)

**Subject:** `docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md` as committed
in `ed01422`, questions `DRP-Q1` to `DRP-Q6` (§8). The claims were checked against source, against
the artifact, and against committed outputs. The prose was not reviewed.

**Not done, as the brief bars it:** no arm was built, no added edge was constructed, no routing was
run on any configuration other than A0 at `ApiConfig()` defaults, the `DRP` pair set (seed
20260928) was not drawn, no `DRP-SW` code was written, and no file in `docs/` or any shipped module
was edited. Nothing is committed.

**Artifact:** A0 = `C:/dev/music-app/builder/scratch/graph-lba-a6.bin`, sha256
`28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b`. Both probes check it against the
sidecar and against that pin before reading anything. `S4-A6/MANIFEST.json` hashed to
`950e3ee8…` (matches the `cand_build.py:82` and `trim_supply.py:64` pins).

## Files

| file | what it is | run |
|---|---|---|
| `drp_structural_probe.py` / `.out.txt` | A0 structure: pop_raw range, the floor by press, degrees, pools. Parses the committed `graph_descriptives.out.txt` (not re-run). Arithmetic for `DRP-C1`(2) and `DRP-SW`. Routes nothing. | `cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-27-drp-prereg-critique/drp_structural_probe.py` |
| `drp_noise_proxy.py` / `.out.txt` | A0 only, `ApiConfig()` defaults. Routes graph-descriptives' own FAMOUS draw (seed 20260927, which is the `DRP-C8` replication set), not the `DRP` draw, to press 10 under three rules: `victim_key`, random s=1 and random s=2. It computes a **proxy** for `N_noise` and runs a partial `DRP-G1`. Wall time 540 s. | same, with `drp_noise_proxy.py` |

## Measured (analyst's figures, on A0 unless stated)

| quantity | value | source |
|---|---|---|
| N / CSR entries | 87,394 / 2,490,728 | structural `.out.txt` |
| `edge_types` values present | `[0]` only | same |
| degree min / median / max; nodes at 50 | 1 / 26 / 50; 14,778 | same |
| CSR symmetric, scores equal in both directions, rows sorted by neighbour id | True, True, True | same |
| `pop_raw` dtype, min, max; nodes at exactly 1.0 / 0.0 | float32, 0.0, 1.0; 1 / 12 | same |
| `0.15*6`, `0.15*7` in float64 | `0.8999999999999999`, `1.05` | same |
| shipped `effective_floor_raw(1.0, k KNOWN)` at k = 6 / 7 | `0.10000000000000009` / `0.0` | same |
| pools: T1 (≥ 0.99) / T2 ([0.95, 0.99)) / MID | 874 / 3,496 / 34,957 | same |
| share of all within-pool pairs whose floor is still non-zero at press k = 4 / 5 / 6 / 7 | T1: 0.686 / 0.129 / 0.001 / 0.000. T2: 0.183 / 0.001 / 0.000 / 0.000 | same |
| T1 centres' shipped degree min / median / max | 2 / 49 / 50 | same |
| possible partners (measured < 0.90): share with shipped degree ≤ 49 | 0.8580 of 78,651 | same |
| pop_raw median by fame band: [0.99, 1] / [0.85, 0.90) / [0.5, 0.7) | 0.704 / 0.524 / 0.482 | same |
| committed A0 FAMOUS d10: median, sd; d10 − d0 sd | 0.992, 0.0132; 0.0133 | parsed from `graph_descriptives.out.txt` |
| **Partial `DRP-G1`:** this tree's `victim_key` ladder against the committed output (d0/d5/d10 at 3 dp, d0 interior n, d0 stop rule) | **40 of 40 FAMOUS pairs match** | noise-proxy `.out.txt` |
| victim_key `M_A0(band 7–10)` on the FAMOUS draw: median; pairs > 0.985 | 0.9921; **35 of 40** | same |
| random press, s=1 vs s=2: per-pair `Δ` median, sd; pairs \|Δ\| ≥ 0.05 | −0.0004, 0.0046; 0 | same |
| **`U`** (97.5th pct of \|bootstrap median Δ\|, 10,000 resamples, `default_rng(20260928)`) | **0.0012**, so `N_noise` proxy = max(0.015, U) = **0.015** | same |
| FAMOUS-draw pairs with both ends T1-like / both T2-like | 2 / 21 (the rest straddle the two) | same |

**Stability.** The `U` proxy comes from **one** draw of 40 pairs, and that draw mixes the two
`DRP` famous strata (only 2 pairs are T1–T1). It was not reproduced on a second slice. Everything
else in the table is deterministic arithmetic over one artifact.

---

## Findings

### `DRP-AM1-F1`: `N_noise` is not derived from the harness on the famous strata. It collapses to the carried 0.015, and `DRP-G6` cannot fire (`DRP-Q4`)
- **Claim (§5):** *"Noise floor `N_noise`, derived from the harness, not by feel"*. `DRP-G6` stops the
  design if `N_noise` > 0.025.
- **Measured:** on the `DRP-C8` draw, `U` = 0.0012, which is about 12× below the 0.015 floor and
  about 20× below `DRP-G6`'s 0.025. The per-pair `Δ` has sd 0.0046, and no pair moves 0.05. The
  cause is the top of the frame (inferred): famous-pair interiors all sit in roughly the top 1 %, so
  whichever artist a random press removes, the pooled median stays near 0.994.
- **Also a mismatch in kind (derivation):** `Δ` measures press-rule randomness, which does not exist
  in the statistic `DRP-C1` scores. `victim_key` is deterministic. The sampling uncertainty over
  pairs is already carried by conjunct (2)'s bootstrap.
- **Where:** `drp_noise_proxy.out.txt` lines 17–18.
- **Smallest change:** in §5, state that on the famous strata `N_noise` is expected to equal the
  carried 0.015 (citing this proxy), so the operative floor is `CRE-`'s, not one derived here.
  Re-label `DRP-G6` as a tripwire that is not expected to fire, or replace `U` with a quantity tied
  to the primary rule.
- **Changes:** a gate (`DRP-G6`'s role) and a bar's stated basis (`N_noise`). The number likely
  stays at 0.015.

### `DRP-AM1-F2`: `RISES` cannot be reached on famous pairs, because M is capped at 1.0 (`DRP-Q4`, reads)
- **Claim (§7):** RISES = median `D` ≥ +`N_noise`.
- **Measured:** 35 of 40 FAMOUS pairs have `M_A0(band)` > 0.985. For those pairs
  `D` = `M_cell` − `M_A0` < 1 − 0.985 = 0.015 whatever the cell does. So a median `D` ≥ +0.015 would
  need at least 20 pairs with headroom, and only 5 have it. The same holds in the committed
  graph-descriptives d10 column (8 of 40 at or below 0.985).
- **Where:** `drp_noise_proxy.out.txt` line 14. The d10 column is in `graph_descriptives.out.txt`
  lines 56–95.
- **Smallest change:** state in §7 that RISES is structurally unreachable on `DRP-T1`/`DRP-T2`, or
  redefine it as a count (for example "≥ N pairs with `D` ≥ +`N_noise`"). Note that because the scale
  is capped, a result that makes famous journeys more famous would be read as NO MOVEMENT.
- **Changes:** a read (RISES, and by consequence NO MOVEMENT).

### `DRP-AM1-F3`: `DRP-C1`(2)'s bootstrap is under-specified, and the choice moves the bar by one pair (`DRP-Q4`)
- **Claim:** *"the 95 % pair-bootstrap upper bound of that median ≤ −`N_noise`"*.
- **Source:** the document does not give the side (one-sided 95th percentile, or the upper end of a
  two-sided interval at the 97.5th), the resample count, the seed, or the generator. The `N_noise`
  bootstrap gives a seed and a count but no generator (`random.Random` or numpy).
- **Arithmetic** (structural `.out.txt`, "what DRP-C1(2) demands"): with m movers whose `D` is well
  below −`N_noise` and the rest near 0, the bound passes only at **m ≥ 26 of 40 (one-sided) or
  m ≥ 27 (two-sided)**.
- **Smallest change:** fix it as "97.5th percentile of 10,000 pair resamples,
  `numpy.random.default_rng(<seed>)`, median = mean of the two middle order statistics", and do the
  same for `N_noise`.
- **Changes:** a bar, by one pair.

### `DRP-AM1-F4`: `DRP-SW`'s second statistic can never fire on its own (`DRP-Q5`)
- **Claim (§2.10):** *"both, either firing"*.
- **Derivation:** an identical first path gives a difference of exactly 0. With ≥ 21 of 40
  differences at 0 the median is 0. So statistic 2 can fire only if ≤ 20 of 40 first paths are
  identical, a share of ≤ 0.50. At that point statistic 1 (< 0.90) has already fired. The same
  holds at any denominator.
- **Where:** structural `.out.txt`, last block.
- **Consequence:** `DRP-R11`'s fire wording *"…or moved the first path's middle by five points or
  more"* can never be the sole reason the trigger fires.
- **Smallest change:** make statistic 2 a reported companion, or define it over the pairs whose
  path changed.
- **Changes:** the trigger's content and `DRP-R11`'s wording. Its outcome does not change.

### `DRP-AM1-F5`: the trigger's denominator is unspecified, and "tolerates up to four" holds only at n = 40 (`DRP-Q5`)
- **Source:** statistic 1 is *"the share of the stratum's pairs"*. The uniform drop rule (§4)
  removes pairs from band statistics, and the text does not say whether it also shrinks the trigger's
  denominator.
- **Arithmetic:** < 0.90 fires at ≥ 5 changed of 40, but at ≥ 4 changed of 36 or of 30. A single
  pair still cannot fire it at any of these sizes.
- **Can it be computed:** yes. Seams B and C record per-depth journeys as node ids, and press 0 is
  the same under both press rules.
- **Smallest change:** "denominator = every drawn pair of the stratum with a press-0 journey in both
  `DRP-S1P0` and A0, independent of the band drop rule".
- **Changes:** the trigger.

### `DRP-AM1-F6`: `DRP-G1r`'s perturbation is exactly `DRP-P1`, so it produces an arm result at stage 3a (`DRP-Q6`)
- **Source:** `DRP-G1r` re-runs the harness with the ramp doubled, i.e. 0.02 = `DRP-P1` (§2.1),
  over graph-descriptives' 80 pairs. Its FAMOUS 40 are the `DRP-C8` replication set. The run
  therefore **is** `DRP-S0P1` on that set, and it happens at stage 3a before `N_noise` and
  `DRP-G6`. That contradicts `DRP-G6`'s *"any remedy … is an amendment written before any arm result
  exists"*.
- **Would it fire:** not measured. Routing at ramp 0.02 is barred to this analyst. (Inferred: 80
  pairs × 20 presses almost certainly diverge somewhere.)
- **Smallest change:** perturb with a value outside the lattice (for example 0.011, or a
  `floor_relax_known` change), and record only "diverged: yes/no", never the journeys.
- **Changes:** a gate.

### `DRP-AM1-F7`: `DRP-G1` names fields the committed output does not print, and overstates what reproducing press 20 proves (`DRP-Q6`)
- **Source:** `graph_descriptives.py:249-261` prints the medians at d0/d5/d10/d20 to 3 dp, the
  interior count **at d0 and d20 only**, the stop rule **at d0 only**, and the ladder stop. `DRP-G1`
  says *"interior counts, stop rules"* without naming depths. It also claims *"reproducing press 20
  requires every earlier press's victim to be identical"*. At 3 dp that is not strictly true: a
  different victim chain can round to the same medians. It is likely, not required.
- **Measured:** the gate is feasible in this tree. 40 of 40 FAMOUS pairs match on d0/d5/d10, d0
  interior n and d0 rule. The reference output was produced from the `dogfish` worktree
  (`graph_descriptives.out.txt:4`); `pathfinding.py` has not changed since `a4ff9c6`.
- **Smallest change:** list the printed fields exactly, and replace "requires" with "makes it very
  likely".
- **Changes:** a gate's wording. Its discriminating power is unchanged.

### `DRP-AM1-F8`: the 60-bound rationale is false for most possible partners (`DRP-Q3`)
- **Claim (§2.3):** *"The 60 bound is the ceiling plus R, so no partner can absorb more added edges
  than a centre can give."*
- **Measured:** a partner's headroom is 60 − its shipped degree, not R. 85.8 % of possible partners
  (measured < 0.90) have shipped degree ≤ 49, so each could take more than 10 added edges. (Centres
  never receive edges: partners are < 0.90 and centres ≥ 0.99, so the sets are disjoint. A centre
  adds at most 10 to a shipped degree ≤ 50. The "≤ 60 for every node" bound itself holds.)
- **Smallest change:** restate it as "a partner may take up to 60 − its shipped degree added edges",
  and add to `DRP-C10` the maximum and the distribution of added edges per partner.
- **Changes:** a descriptive (`DRP-C10`) and the rationale. No bar changes.

### `DRP-AM1-F9`: R = 10 is ambiguous when the 60 bound skips a candidate (`DRP-Q3`)
- **Source:** *"adds, strongest first …, up to R = 10 candidates — skipping any candidate whose
  current degree … is already 60"*. There are two readings. Either the walk continues past a skipped
  candidate until 10 are added, or only the first 10 candidates are considered. The two give
  different edge sets, and `DRP-C10`'s "candidates refused by the 60 bound" means different things
  under each.
- **Smallest change:** "walk the candidate list in order; add until 10 have been added or the list is
  exhausted; a skipped candidate does not count toward R".
- **Changes:** a cell (the edge set of `DRP-S1`).

### `DRP-AM1-F10`: `DRP-G3` covers the five named quantities but cannot see a mis-built rule (`DRP-Q3`)
- **Answer to the question as asked:** **no.** Under `DRP-G3`, the rule cannot change the node set,
  the largest component, `pop_raw`, the fame percentiles or any shipped edge's score without firing
  the gate. Each is asserted directly, the last row for row with score bytes. Adding edges among
  existing nodes cannot split a component (source: `graph.py:257-282`).
- **Blind spots (source):** `DRP-G3` checks each added edge's *eligibility* (centre ≥ 0.99, partner
  < 0.90, both nodes, not already shipped). It does not check that the edge was *selected by the
  rule*. The following all pass it:
  - a partner not in the centre's `SUP-S3`;
  - more than 10 additions for one centre;
  - selection out of strength order;
  - an added edge's score not equal to max(`trim_in[c][p]`, `trim_in[p][c]`) cast to float32;
  - an added edge written in one direction only (A0 is symmetric, measured; the router follows rows
    as written, `graph_store.py:218-221`);
  - rows not sorted by neighbour id (unspecified; the shipped builder sorts at `graph.py:349`);
  - raw `fame_lb` changed while its percentiles stay equal. That leaves routing unaffected but
    breaks the §3 `log10(1 + fame_lb)` companion.
- **Smallest change:** add to `DRP-G3`:
  - CSR symmetric, with equal scores in both directions;
  - rows sorted by neighbour id;
  - an independent re-derivation of the added-edge set and scores from the capture equals the
    artifact's;
  - raw `fame_lb` equal by MBID.
- **Changes:** a gate.

### `DRP-AM1-F11`: `DRP-G5` has no independent side as written (`DRP-Q1`/`Q6`, instruments)
- **Source:** `find_journey` returns `(path, rule)` and no cost (`pathfinding.py:194-231`). So *"the
  ramp's contribution recomputed along the returned path"* is the harness's own recomputation. If
  both sides take `k` from the ladder depth, the check is a tautology and cannot see the k-indexing
  bug it names.
- **Smallest change:** compute the left side with `k` = the number of `KNOWN` exclusions **actually
  passed** to `find_journey`, and the right side with the ladder depth.
- **Changes:** a gate.

### `DRP-AM1-F12`: the random-press rule and the drop rule are not reproducible from the text (`DRP-Q4`)
- **Source (§4):** `random.Random(f"DRP:{s}:{stratum}:{i}")` does not say:
  - whether there is one instance per pair (consumed across presses) or one per press;
  - whether `i` is 0- or 1-based;
  - which call draws the victim (`choice` or `randrange`).

  Each choice changes `DRP-C7` and `N_noise`. (The proxy used one instance per pair, 0-based,
  `randrange`, and is labelled so.) The uniform drop rule is defined over "the six cells", and does
  not cover the A0 s=2 run that `N_noise` needs.
- **Smallest change:** pin all four.
- **Changes:** a companion (`DRP-C7`) and `N_noise`.

### `DRP-AM1-F13`: a mechanism §2.7 did not list: neighbour order under exact cost ties (`DRP-Q1`)
- **Source:** Dijkstra relaxes on strict `<` (`pathfinding.py:172`) in row order
  (`graph_store.py:218-221`). `DRP-S1` inserts edges into centre and partner rows. Where two paths
  cost exactly the same, the first path can therefore change **without using any added edge**. That
  contradicts §2.3 reason (2), *"any first-path change is by addition only"*. The effect is inert in
  A0 for a reason the intervention removes (row composition). Its frequency was not measured.
  Derivation: without exact ties, a changed optimum must use an added edge.
- **No missed cost term.** Every term in `pathfinding.py:155-170` is accounted for in §2.6/§2.7
  (see "checked and sound").
- **Smallest change:** for every changed first path, `DRP-C5` records whether it traverses at least
  one added edge. That is computable from the committed node-id journeys plus the added-edge list.
- **Changes:** a descriptive (`DRP-C5`) and the reading of the `DRP-SW` trigger.

### `DRP-AM1-F14`: the floor-attribution flag names "its isolating baseline", and the crossed cells have two (`DRP-Q6`)
- **Source:** §2.2 lists two baselines each for `DRP-S1P1` and `DRP-S1P2`. §2.7(b) compares against
  "its isolating baseline" in the singular. (`DRP-C1`'s `D` is always taken against A0, which is two
  columns away for the crossed cells. `DRP-R3` already bars one-knob attribution there, so the reads
  are consistent.)
- **Smallest change:** compute the flag against each listed baseline, and let it fire if either
  crosses 10 points.
- **Changes:** a read qualifier (`DRP-R9`(iv)).

---

## Observations (no document change required unless the caller chooses)

- **`DRP-AM1-O1` (derivation, `DRP-Q4`): what 40 pairs can see.** Taken together, `DRP-C1`'s
  conjunction needs:
  - at least 20–21 of 40 pairs at `D` ≤ −0.05 (conjunct 1);
  - about two thirds of pairs (26–27, `DRP-AM1-F3`) past −`N_noise` (conjunct 2).

  Against A0's own variability (proxy `U` 0.0012; committed d10 − d0 sd 0.0133) noise is not the
  binding constraint. The binding constraint is how broadly an effect spreads across pairs. A
  remedy that moves a minority of famous pairs strongly will fail `DRP-C1` at any size.
- **`DRP-AM1-O2` (measured, `DRP-Q2`): the band's lower edge is correct, and conservative.**
  - pop_raw lies in [0.0, 1.0], exactly one node is at 1.0, and 0.15 × 7 = 1.05 in float64, so the
    floor is 0 for every pair at k ≥ 7 with a 0.05 margin. There is no floating-point edge case at 7.
  - At k = 6 the only live pairs are those with min pop_raw > 0.8999999999999999: 0.1 % of T1
    within-pool pairs and none of T2.
  - The floor is already dead for most famous pairs earlier. At k = 5 it is live for 12.9 % of T1
    within-pool pairs and 0.1 % of T2.
  - So the §2.10 `N` input (i) on this map reads "T1: 87 % by press five", not the other map's
    96–100 %.
  - `DRP-G7`'s assertion is implementable with the shipped function (the probe calls it).
- **`DRP-AM1-O3` (inferred, unmeasured): where the added exits will land in fame.** Selection is
  strongest-first on `log1p(cooc)` with damping 0 (`pipeline.py:61-81`), so strength grows with the
  partner's own audience. The ten selected will likely concentrate just below 0.90 rather than deep
  in the tail. `DRP-C10` does not report the added partners' fame distribution. Adding it would make
  a `DRP-R0` or BELOW BAR result interpretable. Falsifier: the distribution itself.
- **`DRP-AM1-O4` (measured, `DRP-Q1`): the jump term prices every added hop at every press.** Its
  raw pop gap between the fame bands is 0.704 (T1) vs 0.524 ([0.85, 0.90)) and 0.482 ([0.5, 0.7)),
  as medians. No press relaxes it. It is the same in every `DRP-S1` cell, so it is part of the
  supply knob rather than a confound. It is the natural term for `DRP-C9` to name if `DRP-R0` fires
  (§2.4's deferral condition).
- **`DRP-AM1-O5`: `DRP-G4` has no red control.** Source guarantees it (`pathfinding.py:130-132`),
  and the `MSW-G2` precedent had a perturbation that turned three tests red. The document's own rule
  elsewhere is that a gate shows it can go red.
- **`DRP-AM1-O6`:** §2.6 cites `config.py:106`, `:110-111` and `:174` without naming the package.
  They are `builder/src/artistpath_builder/config.py`. In `api/…/config.py`, `:174` is `clip_cache`.

## §13 claims that do not resolve

None failed. One is only **partly** resolved: *"module-identity asserts carried: `pathfinding`
loaded from this tree's `api/src`"* — the committed reference output was produced from a different
worktree (`dogfish`, `graph_descriptives.out.txt:4`). It reproduces in this tree
(`DRP-AM1-F7`, measured), so this is provenance, not a defect.

## Checked and found sound

- **§2.6, every row against source:**
  - `pop_raw` is summed pre-cap (`pipeline.py:389`, from rescaled lists built at `:375-389`) and
    log-scaled over the kept node set (`graph.py:328, 337, 285-300`);
  - the rescale runs before the cap (`pipeline.py:375`, cap at `:405`);
  - fame is loaded after the cap (`pipeline.py:448`);
  - fame percentiles depend only on the raw list (`graph_store.py:148-193`);
  - api `config.py:79-83`, `:89`, `:114`, `:117-118`;
  - the avoidance map is empty without dislikes (`pathfinding.py:105-107`);
  - `w_degree_hub` × a finite clipped penalty = 0 (`:160`, `graph_store.py:206-212`);
  - `find_journey` `:194-231`.
- **`DRP-S1` cannot create adjacency between two drawn endpoints** in any stratum or in the
  replication set (partners < 0.90, and every endpoint is ≥ 0.95 or in [0.30, 0.70]). So F1's
  forced-stop rule cannot be switched on by the added edges.
- **`DRP-G4`'s identity at press 0** follows from source: `ramp_fame_on` is false at `k` = 0.
- **§2.2:** every listed baseline is one column away in configuration. That rests on `DRP-G2`
  (rebuild == file) plus `DRP-G3`. The routing-relevant state compared (CSR, scores, `pop_raw`,
  percentiles) is covered by the two gates; the remaining differences are display-only metadata,
  degree-hub penalty (weight zero) and row order (`DRP-AM1-F13`).
- **§2.3 rule 4 (the score) is fully specified and deterministic.** The union condition is
  symmetric in the pair, so both directions are present whenever one is (`graph.py:231-234`), and
  the maximum is well defined.
- **Other §2.3 pins:** ties on lowest MBID and centres in ascending id = ascending MBID
  (`graph.py:328-329`); the strength key (`graph.py:238-242`); `quota` 0.2 and
  `reserve = int(quota*d)` (`cb_build_variants.py:166`, `:234`); `SUP-S3` as defined in
  `trim_supply.py:289-299`.
- **Pools:** T1 = 874 centres = the top 1 %. A0 carries `edge_type` 0 only, so "every edge 0" is
  the shipped value.
- **§13 rows spot-checked:**
  - `models.py:9-17`;
  - `artifact.py:85`, `:171`;
  - `graph_store.py:247-248`, `:282`;
  - `pathfinding.py` last changed at `a4ff9c6`;
  - `cre_ladder.py:44-53`;
  - `graph_descriptives.py:95-107`;
  - the `cand_build.py:82` and `trim_supply.py:64-65` pins;
  - `NEXT.md` now reads "carry", per its 2026-09-27 correction (`NEXT.md:157-158`).
- **The `DRP-SW` trigger** can be computed from what Seams B and C record, and a single odd pair
  cannot fire it at n = 40, 36 or 30.
