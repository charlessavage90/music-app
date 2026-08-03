# Repo-check review of the CRE pre-registration — as delivered, 2026-08-03

**Provenance:** produced by a general-purpose subagent dispatched 2026-08-03 at the
owner's instruction, in the "check this document's claims against the repo" form,
against the pre-registration as first committed (`c047d06` + same-day self-review
fixes), before any CRE arm was built or run. Reproduced verbatim below. The prereg's
§9 records the disposition of each finding.

---

## Wrong-claim findings (ranked)

### 1. HIGH — §3.2's tag-limited build contradicts the S1 implementation it claims to be "identical to", and as written reproduces the measured unbounded-degree defect

- **Prereg** (§3.2): "For each artist whose union candidate list exceeds the budget (50), keep the 50 candidates ranked by LB similarity re-weighted by rarity-weighted `W4` agreement… **Symmetrise keep-stronger as production does, then largest-component prune** as production does. **Everything else identical to `CRE-S1`.**" — i.e. per-node truncation of union lists, **then** symmetrise.
- **Source** (`builder\analysis\2026-07-30-track-b-cap-selection\cb_build_variants.py:167–256`): `CRE-S1`'s committed shape (`cap_trimmed_union`) is union → **symmetrise → degree ceiling applied by deleting WHOLE EDGES from both endpoints**. Its docstring is explicit about why: *"Union alone bounds nothing… which is exactly the defect that killed the pre-symmetrise cap — configured 50, observed max degree 11,243… it is applied by deleting WHOLE EDGES rather than truncating one endpoint's row, because per-node truncation breaks symmetry again."* `builder/src/artistpath_builder/config.py:74–78` records the same lesson for the deleted `pre_symmetrise` strategy.
- **Consequences:** (a) "Everything else identical to `CRE-S1`" is false — trim placement (pre- vs post-symmetrise) and trim mechanism (row truncation vs whole-edge deletion) both differ; (b) §0.2's E-S2-P0 row "trim device isolated … same union source, same budget" and §0.1's no-separate-tag-knob argument therefore claim a one-column difference that the text as written does not deliver; (c) degree ≤ 50 is **not** guaranteed by §3.2's order — a hub trimmed to 50 own-kept candidates is restored to unbounded degree at keep-stronger symmetrisation, the exact defect Phase 2 measured. The §3.1 edge-*count* bound (kept ⊆ union) survives; the degree bound and the isolation claim do not.
- **Severity rationale:** spec-level confound in the only new build device; cheap to amend now, poisons every D1-branch attribution after results exist.

### 2. MEDIUM-HIGH — "the mirror already exposes per-term stats" is false, and the missing capability is load-bearing but absent from the declared dependency list

- **Prereg** (§0.3 dormant-term paragraph): "`CRE-D2` term-level cost accounting runs in every cell (per-depth, per-term contribution shares along chosen paths — **the mirror already exposes per-term stats**)."
- **Source:** `builder\analysis\2026-07-23-track2-sweep\mirror.py` exposes exactly three counters — `examined`, `floor_active`, `guard_fired` (lines 272–275, 341–342) — search-wide tallies, not per-term contribution shares, and not along chosen paths. Every consumer confirms the shape (`run_arms_t3.py:119`, `run_arms_tb.py:113`). `dd_p3`-era review even *recommends* adding per-term reporting "the way `floor_active` already is" (`DD-P3-analyst-review.md:497`) — i.e. it was known not to exist.
- **Consequence:** `CRE-D2` is the named handling for the disclosed `w_floor` uncontrolled variable and gates every knob-attribution sentence, yet it needs new harness code that §2's "named not-yet-built dependencies" list (items 1–4) does not include. A `CRE-G1`-gated executor discovers this mid-sweep.
- **Severity rationale:** exactly the "document asserting something about the repo that isn't true" class; the false clause hides a fifth dependency.

### 3. MEDIUM — `CRE-G1`'s baseline "production routing on the adopted substrate" is unachievable under the most natural reading of "adopted substrate"

- **Prereg** (§4): "At E-S0-P0, d0 paths bit-identical to **production routing on the adopted substrate** for all pairs"; §0.2 anchor note: "Must reproduce production routing bit-identically."
- **Source:** "adopted" is the term of record for `graph-t15-tiebreakfix.bin`, 74,193 artists, pre-cleanup (`fi_union_snapshot.manifest.json` `"adopted"` entry; `api/src/artistpath_api/config.py:12–21`). E-S0-P0 lives on the **cleaned** substrate (both drop flags on — §0.3 row 1, §2), which provably differs: `pipeline.py:210–232` removes both drop lists before the mass computation, and `BuilderConfig`'s own comments (config.py:152–158, 170–174) record that each drop "moves every surviving artist's popularity marginal." Bit-identity against routing on the adopted artifact therefore cannot hold; the achievable gate matching the cited `TAS-AM5a` precedent is mirror-vs-production-router-code **on the same cleaned substrate**.
- **Severity rationale:** this is the gate that blocks all reads ("no read opens until it is fixed"); if built against the literal reading it fires unconditionally, and the A0-vs-P lesson the prereg itself cites is about exactly this. One word ("cleaned", or "same substrate") fixes it now.

## Unresolved / inaccurate references

### 4. LOW — the design-inputs precedence rule is cited as "§0 there"; the design-inputs doc has no §0

- **Prereg**: "this document governs (its own rule, **§0 there**)." The rule exists but lives in the unnumbered role header of `2026-08-02-cap-reeval-design-inputs.md` (lines 3–9: "Where this document and a governing spec disagree, the spec governs"). Sections there run §1–§8. Wrong address, right rule.

### 5. LOW — `algorithm="contribution_5"` in §0.3 reads as a literal config value

- **Prereg** §0.3 BuilderConfig row. Actual default: `algorithm = PRODUCTION_ALGORITHM`, a long string *containing* `contribution_5` (`builder/src/artistpath_builder/config.py:17–20, 54`). NEXT.md's careful wording is "still carries `contribution_5`"; the prereg's `=` is a drift a cold reader could act on (e.g. grepping for the literal).

## Internal inconsistencies

### 6. MEDIUM — §0.2 marks E-S2-P0 "(D1-branch)", contradicting §4 and §6, which make it branch-proof

- §0.2 legend: "Cells marked *(D1-branch)* **exist only if** `CRE-D1`'s branch fires that way" — and E-S2-P0 carries the mark. §4: not-supported/unreadable branches "reduce family (c) **to the single probe cell E-S2-P0**… *The single probe cell survives every branch*." §6 repeats that it is part of the specified run. Table and text contradict; an executor reading the table alone drops the probe cell on a not-supported branch — the same specified-run-kept-alive-by-prose failure the document's §6 preamble warns against. (B-S2-P0, E-S2-P1a, B-S2-P1a are correctly branch-conditional.)

### 7. LOW-MEDIUM — §0.3 row 1 says "Carried as two deliberate rows, not one, per the 2026-08-03 handoff's instruction" — but it is itself one row, and the handoff permits one

- **Source** `2026-08-03-HANDOFF-featured-credit-filter.md:67–68`: "the factor table should carry them **as one row or two** deliberately, not by omission." The one-row form actually complies with the instruction; the sentence describing it is false about both the table and the source.

### 8. LOW-MEDIUM — bare foreign identifiers collide with the CRE- namespace in running text

- §0.2 rows E-S0b-P0 / B-S0b-P0 cite bare "`R0`" (Track B's read) while `CRE-R0` is defined in §6; §6's standing bars cite "`R2`'s ALG-E null" (Track B's `R2`) four lines below `CRE-R2`'s definition. §3.1 at least qualifies "Track B (`C4`)". The intro's namespace check covers series prefixes but the body then uses unprefixed tokens from the colliding series — the exact retrieval failure the Track 2 `R1` postmortem in CLAUDE.md describes. (Wording is inherited from NEXT.md's closed list, but NEXT.md defines no competing `R2`.)

### 9. LOW — design inputs §3 names `REQ-27` as the device the gradient acts through; the prereg never cites REQ-27

- `2026-08-02-cap-reeval-design-inputs.md:66–68` lists it as a consequence beside the `TB-P5H-7` consumption; the prereg consumed `TB-P5H-7` (§3.3) but dropped REQ-27 entirely. Omission, not contradiction — noted because the P1 ramp is a global per-press repricing, not a relative-to-the-bypassed-artist device, so this is where a design reviewer will look.

### 10. LOW — dependency (2)'s re-plumb of `mirror.py` sits next to two frozen-record hazards it does not name

- NEXT.md "must not be changed": the mirror's device knobs stay 0.0 — the prereg complies (arms override per-run, `run_arms_t3.py` precedent), but does not say so; and `mirror.py:99–101` claims committed Track 2/2F figures reproduce "from this file", which an in-place currency re-plumb complicates for Track 3/3b's committed pctl-based outputs (closed, so reproduction is not owed — but the prereg is silent on in-place-vs-copy). Checks out only barely; one sentence in the execution plan resolves it.

## Verified clean (coverage list)

**Files/functions/configs — all resolve as described:**
- Four drop lists exist byte-for-name in `builder/src/artistpath_builder/data/` (`no_release_drop_20260801.json`, `no_release_drop_algb_20260802.json`, `featured_credit_drop_20260803_am1.json`, `featured_credit_drop_algb_20260803_am1.json`); sha-pinned (`no_release_drop.py:59–67`, `featured_credit_drop.py:39–52`), selected by `config.algorithm`, applied by MBID **before capping** (`pipeline.py:210–232` precede `mutual_knn_cap` at line 311).
- `fi_union_snapshot.json` + manifest sidecar with sha256 (`d9d6d5d3…`), union population 93,067, nulls preserved per FAM-AM1.8.
- `cb_pairs.json`: famous classes ff-top1pct 12 + ff-top01pct 10 = **22, all kept routable everywhere** (drawn 82 → kept 39).
- `cb_build_variants.py`: `TUw-50-50` = `("trimmed_union", {j:50,d:50})` weight trim; reads through `ReadOnlyArchive` (GRT-A1 complied).
- `mirror.py`: `w_known_ramp_pctl` exists, additive, default 0.0, relaxation-target-only; currently reads popularity percentile (so dependency (2) is correctly declared as a re-plumb).
- `run_arms_t3.py:109`: `guard_min_intermediary=True` — matches the held-constant row.
- `wgt_grid.py`: `rarity` scheme and `W4`/`W6` frames exist; "rarity-weighted agreement over W4" resolves.
- `api/config.py:44–48` = `w_sim, w_jump, w_floor, w_hop, w_avoid`; line 54 = `w_degree_hub: float = 0.0`; weights are dataclass constants, **not env-driven** (only `graph_path`/sha/CORS/cache are).
- `builder/config.py`: `max_neighbours_per_artist=50`, `cap_strategy="mutual_knn"` (enforced by `__post_init__`), both drop flags default on and documented as factor-table controls.

**Cross-document citations — say what the prereg says they say:**
- Design inputs §1–§8: goal wording, families (a)–(d), tag constraints (LB-sim sole source of edge existence; tags re-order/re-weight/remove; W6 barred; λ-Jaccard stays closed; scrambled-labels control mandatory), owner's hypothesis + cheap read → CRE-D1, coverage guard ~10,000, hubness-rising-with-depth kill, C4-flag re-weighting, ordering ruling discharged (PR #67 merged, `eecc361`), Track-B-reuse, seams-at-authoring, blind-listen primacy — all implemented without contradiction found (beyond findings 1, 9).
- FAM-AM1.3 (step 0.0015, 10× floor = 0.015), FAM-AM1.7 (6.1× = 2,501/409, factor-table obligation), FAM-AM1.8 (all-interiors AND matched-only, null = hole in denominator), FAM-AM2.2 (no within-remainder ordering), FAM-AM2.3 (re-fetch = new instrument, corroborating AM1.7) — all quoted accurately.
- Track B results note: TU loses 1 vs MK50's 800; hub/degree mass falling ~40%; UC top-1% mass ≈5× any capped cell, hub transit 0.97–1.00; CRS-C5 zero on every ALG-E cell incl. quota cells, nonzero on ALG-B incl. MK50; R0 null on ALG-E / decisive on ALG-B; C4 fired on bound-100 at d0; weakest-link note on own-graph vs production top-degree sets (CRE-C2's primary-set choice matches); CRS-C6's 5-point materiality precedent for CRE-C1's −0.05.
- CRS-G3 floor: ≥ 8 pairs per band, from the Track B prereg — matches CRE-G3.
- TB-P5H-7 (`2026-07-29-track3b-execution-log.md:171–173, 182–185`): the unconsumed joint outcome is descent-pass + TB-C2-miss (payload ratio 0.475/0.213 vs 0.5); CRE-C4 (floor 0.5, read jointly with C1, C1-pass+C4-fail = R3 never success) is a faithful consumption.
- REQ-13, REQ-14, REQ-18 (an Expect; no press-count optimisation), REQ-38, REQ-42 (gradient, never band-reaching), and the Definitions section (`fame_lb_pctl`, novelty-likelihood, adopted 2026-08-02, worldly-fame claims barred) — all as quoted.
- NEXT.md: edge-growth deferral row satisfied per its own condition; the corrected `w_degree_hub` row (decide-deliberately, no self-activation control needed) implemented as written; isolated post-drop-listen decomposition branch quoted accurately incl. `drop_no_release_tail` as the preserved instrument; closed list (Track 2/2F/ceiling-toll, Track 3/3b, TAS-6, MKS-5b, PS100≡MK100, proximity_select, pair-set attrition, quota-null citation rule, PLA-R1, CS-P0e closed enum) — nothing reopened; "mirror knobs stay 0.0" not violated (see finding 10); Track-B-cells-never-re-run honoured; DD-A2 parked decision left parked.
- `TAS-AM3b` (stronger null holding labelled-set fixed), `TAS-AM5a/b/c` precedents, `SYN-6`, `COH-2` (94–100%), `GRT-A1`, `CS-P0e`, `NOV-2`/`NOV-AM1`, fame log §8 (~73%) — all resolve and are quoted accurately.

**Factor table (§0.2), checked mechanically:** all 17 rows differ from their named isolating baseline in exactly one column (E-S0b, E-S1, E-S2, E-S3 vs their supply baselines; all P1a/P1b vs their pricing baselines; B-S0 vs E-S0 on data set only). No multi-column row found. The barred-comparison rule is stated. `CRE-` identifier series is unique in `docs/` (no external collision); every `CRE-` identifier used is defined; all § cross-references resolve; arithmetic consistency holds (0.015 = 10×0.0015; C1's −0.05 = 3⅓× floor; C6's 0.15 = 10× floor; R4's 0.015 lead = floor). Plain sentences beside C1, C2, C4, C5, C6, G1–G3, D1, R0, R3 neither broaden nor narrow their statistics, with one hair: C4's plain "after ten presses" vs C1's "ten or more" for the same d10–20 band — trivial.
