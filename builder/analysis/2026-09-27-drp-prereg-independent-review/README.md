# Independent review — `2026-09-27-issue-200-depth-remedy-preregistration.md` at `1070acc`

*Provenance, added by the dispatching session and not part of the review: the owner's brief was
passed verbatim to a `general-purpose` subagent on a different model (fable), with only the path and
SHA filled in. It ran in parallel with the `ml-graph-analyst` critique
(`../2026-09-27-drp-prereg-critique-2/`), and neither reviewer saw the other's output. Its final
report is reproduced below verbatim. The one change is that the harness's hand-back indentation has
been removed.*

---

**Scope kept:** fidelity to source, design logic, executability, owner material, direction. Mathematics (noise floors, effect sizes, graph derivations) left to the analyst. **Nothing was run on any variant.** What I ran: `sed`/`awk`/`grep` over the cited source lines; `git log`/`git grep` across all refs; `gh issue view 200/244` and `gh issue list --search DRP`; `sha256sum` on `C:/dev/music-app/builder/scratch/graph-lba-a6.bin` and `C:/unsung-fast/lbd-archives/S4-A6/MANIFEST.json` (read-only); an exact-line diff of the three quoted rulings against the #200 comment.

---

## Ranked findings

### 1. BLOCKS-ARMS — The body carries superseded text with no legend saying §14 governs; executing §6 as written runs an arm at stage 3a.

**Claim as written:** §14 `DRP-AM1` preamble (line 909–911): *"Every changed clause stays in place in the body with a ⚑ marker pointing here, and its original wording is quoted below."* The body then retains the *original* wording everywhere a ⚑ appears; nothing in §0–§13 tells a reader that ⚑-marked text is superseded rather than annotated. `grep -n -i "legend|marker means|superseded original|§14 governs"` → no hits.

**Evidence, body text still in force by its own words:**
- Line 628, `DRP-G1r`: *"re-run with `w_known_ramp_fame_pctl` doubled"* — doubled is 0.02 = `DRP-P1`. A cold session executing §6 produces `DRP-S0P1` on the `DRP-C8` set at stage 3a, before `DRP-G6` — exactly the breach `DRP-AM1-F6` (line 976) exists to prevent. The 0.015 value lives only in §14.
- Line 178–179, §2.3: *"The 60 bound is the ceiling plus R, so no partner can absorb more added edges than a centre can give"* — §14 `DRP-AM1-F8` (line 994) says of this sentence: *"That is false for partners."* The false sentence is still the body.
- Line 400, §2.10: *"Statistic — both, either firing"* — `DRP-AM1-F4` made statistic 1 alone the trigger.
- Line 116 (*"= six cells"*), line 128 (§2.2 heading *"The six cells"*), line 525–526 (§4 drop rule *"any of the six cells … dropped from all six"*), line 635 (`DRP-G8` *"in all six cells"*), line 644 (§7 *"complete = all six cells swept"*) — all eight-cell facts live only in §14 `DRP-AM2` (lines 1284–1295).
- Line 161 (R = 10 rule), line 323 (floor flag "its isolating baseline"), line 573 (bootstrap "upper bound" unpinned) — same pattern.

**Amendment:** one sentence at the top of §0 or §14: *"Wherever ⚑ appears, the body keeps the original wording for the record and the §14 entry it names is the governing text."* Plus a short governing-values index in §14 (gate → current value/wording) so a session can execute from one place. Mechanical, changes no bar. (`docs/README.md:220` already describes the convention as body = original, so the legend only states what is already true.)

### 2. SHOULD-FIX (before stage 2) — `DRP-D4` has no record outside this document; the same holds for `DRP-AM2`'s and `DRP-AM4`'s sources.

**Claim as written:** line 103: *"`DRP-D4` — where `REQ-33` bites, HIS, 2026-09-27: recorded verbatim"*; line 1321–1329 quotes a question *"put to him in these words"* and his answer *"REQ-33 bites on the first path and after 1-3 presses"*. Line 1087: `DRP-AM2` source is *"the owner, relaying an outside review"*. Line 1474: `DRP-AM4` *"Asked by the owner."*

**Evidence:** `git grep -n "REQ-33 bites" $(git for-each-ref …)` excluding this file → **no hits in any ref**. `gh issue view 200 --comments` and `gh issue view 244 --json body,comments` → neither contains the D4 words, the outside review, or the AM4 request. `docs/superpowers/2026-09-27-HANDOFF-drp-prereg.md` → no match for D4/REQ-33/AM2/AM4. By contrast `DRP-D1`–`D3` (lines 79, 87, 96) are **exact line matches** against the #200 comment beginning *"Owner rulings, 2026-09-27"*.

**Why it matters:** §1 line 74–75 sets the document's own standard — rulings quoted *"from the record rather than from a conversation."* D4 materially changed the design (`DRP-C6` scope, the ceiling schedule, two struck caveats, `DRP-R12`'s prior clause) and it is a conversation. The owner's stage-2 go is also a conversation unless posted.

**Amendment:** the owner posts D4 verbatim (and, in one line each, that he asked for AM2's additions and AM4's red control) as a comment on #244 before stage 2; §1 and §14 cite that comment URL. His stage-2 go lands the same way.

### 3. SHOULD-FIX — `DRP-D2` ("depth zero … not scored") and the re-scoped `DRP-C6` (gated at depth 0) are not reconciled; the collision is live for the `DRP-S1` cells.

**Claims as written:** line 87 (D2, his): *"Depth zero is measured and reported in every arm, not scored."* Line 89–90 (consequence): *"No criterion rewards or penalises a first path."* Line 608 (`DRP-C5`): first-path fame *"barred as a scoring criterion … `PLA-R1`"* (`NEXT.md:233` confirms). Line 609 (`DRP-C6` after AM3): *"gated at each of depths 0, 1, 2 and 3 separately"*; line 665: ELIMINATES = `DRP-C6` fires *"(whatever else holds)"*.

**Evidence of reach:** pricing cells cannot fire at depth 0 (`DRP-G4`, `ramp_fame_on` false at k = 0, `pathfinding.py:130-132`). `DRP-S1P0`'s press-0 journeys *can* differ from A0's (§2.3 reason 2; `DRP-AM1-F13`), so `DRP-C6` at depth 0 is a first-path criterion that can disqualify the supply arm — on a stratum (`DRP-T2`) where A0's depth-0 share of ≥ 0.99 interiors may itself be small.

**Amendment:** add to §1 D2's consequence and to the `DRP-C6` row: D4 is later and specific; D2 bars *scoring descent* at depth 0 and `PLA-R1` bars first-path *fame* as a scoring criterion, while `DRP-C6` is a `REQ-33` *floor*; state that at depth 0 only the `DRP-S1` cells can fire it, and say what would have to be true of an added-edge-only change for a first path to lose every ≥ 0.99 interior. If the owner did not mean D4 to reach depth 0 of the supply arm, that is his to say on the record (finding 2).

### 4. SHOULD-FIX — `DRP-R8`'s "step, not a gradient" classification has no effect size.

**Claim as written:** line 687: *"A cell whose `D` reaches its band value by press 3 and stays flat after is reported as 'a step, not a gradient'."* "Reaches" and "flat" carry no tolerance; the owner reads this label (`REQ-42`, `REQ-16`), and `CRE-`'s strong arm was marked down on exactly this shape (CRE results §3, line 396–402).

**Amendment:** fix it now, e.g. *step* = `D(k)` within `N_noise` of `D(band)` for every k in 3…20, else *gradient*; state it as a choice with no prior calibration, as the document does elsewhere.

### 5. SHOULD-FIX (overlaps the analyst; flagged, not duplicated) — `DRP-G5` cannot observe the router's ramp; both sides are harness arithmetic.

**Claim as written:** line 632, plain sentence: *"the pull the harness applies is exactly what the formula says."* `DRP-AM1-F11` (line 1017–1021) makes the left side *"k = the number of `KNOWN` exclusions actually passed"* and the right *"k = the ladder depth."*

**Evidence:** `find_path` returns only the path (`pathfinding.py:177-182`); `find_journey` returns `(path, rule)` (`:200`). No cost is returned, so *"the ramp's contribution recomputed along the returned path"* is the harness multiplying its own inputs on both sides. The gate checks that the harness passed k `KNOWN` exclusions equal to the ladder depth and that no ceiling exclusion leaked into `KNOWN` (the `DRP-AM2` check (c) use, which is real and valuable). It cannot see a mis-applied ramp inside the router.

**Amendment:** re-word the plain sentence to what it tests (*"the number of presses the harness told the router about is the number the ladder is at, and the ceiling never counts as a press"*), and leave the router's arithmetic to `DRP-G1`/`DRP-G1r`, which do see it through the committed output.

### 6. NOTE — §7's run-state vocabulary is internally inconsistent.

Line 643: *"gated = `DRP-G1`–`G7` recorded and passing."* `DRP-G4` and `DRP-G5` are measured during the 3b/3c sweeps (lines 729, 732), so they cannot be recorded at a "gated" state that precedes sweeping; `DRP-G9`/`G10` are absent from the vocabulary. *gated* is never used as a precondition by any read (grep: three hits, none a precondition). **Amendment:** *gated* = `G1`, `G1r`, `G2`, `G3`, `G6`, `G7`, `G10` (the Seam-A set); `G4`/`G5`/`G9` belong to *swept*.

### 7. NOTE — `DRP-G10` routes on the `DRP-S1` map at stage 3a and does not say what it records.

Line 637 and line 728: `DRP-G10` calls the shipped `find_journey` with ceiling exclusions *"on both supply maps"* at 3a, before Seam A and before the S1 row. `DRP-G1r` and `DRP-AM4`'s red control both state *"only diverged: yes/no … no journey is kept"*; `G10` does not. **Amendment:** add the same sentence.

### 8. NOTE — two statistics are left to the executor.

(a) `DRP-C2` in the `DRP-P3` cells, line 605: *"ratio ≥ 0.70 at each band depth separately"* — the per-depth form is not defined (per pair: interior count at depth d ÷ count at press 0; median over pairs; ÷ A0's same at that depth is the natural reading). (b) `DRP-R13`, line 692: *"median band `r`"* — `r` is per (pair, depth); median over all band (pair, depth) cells or over per-pair band means? **Amendment:** write both out.

### 9. NOTE — three citations are slightly off; none changes a conclusion.

- Line 370: *"`EdgeType` has `BEHAVIOURAL = 0` and a reserved `STRUCTURAL = 1` (`models.py:9-17`)"* — this is **`builder/src/artistpath_builder/models.py`** (the api has a `models.py` too, cited bare at line 1276 for a different fact), and `:18` adds `DESCRIPTIVE = 2`, so a `DRP-SW` edge type must avoid 1 *and* 2.
- Line 447: *"Today's reader refuses only on a `FORMAT_VERSION` mismatch (`graph_store.py:247-248`)"* — it also refuses on bad magic (`:245-246`) and length mismatch (`:254-262`); the point (no refusal on edge-type values) stands.
- Line 1276: `models.py:24-27` — the api comment runs `:24-28`.

### 10. NOTE — one measured figure is restated from a figures owner.

Line 415–416: *"for 96–100 % of pairs by press five on another map's pairs (`JFX-AM1` §`AM1.9`)"* is verbatim `2026-08-09-journey-fame-exposure-preregistration.md:253`. The document's own rule (line 17–19) is cite-by-section. **Amendment:** drop the number; the §14 `DRP-AM1-O2` entry already does this correctly for this map's figure.

### 11. NOTE — `docs/README.md:220` describes the document through `DRP-AM3` and does not mention `DRP-AM4`.

Map row stale by one amendment (the `1070acc` commit touched only the spec).

### 12. NOTE — handed to the analyst, not assessed here.

`DRP-C6`'s "one quarter of A0's share, per depth" on `DRP-T2` at depths 1–3 has no minimum-count guard; with a small A0 share the quarter can be a fraction of one pair. Effect-size territory.

### 13. NOTE — untracked `builder/analysis/2026-09-27-drp-prereg-critique-2/` is in the working tree.

Not part of the committed record; not read (per the brief). Presumably the concurrent analyst's.

---

## Design logic — what checked out

- **Factor table (§2.2):** every non-anchor row differs from each named baseline by exactly one column, including the two `DRP-P3` rows (`P3` keeps the ramp at 0.01 = `P0`, so `S0P3`↔`S0P0` and `S1P3`↔`S1P0` differ by the ceiling alone; `S1P3`↔`S0P3` by supply alone). No row compares `P3` with `P1`/`P2`, and no read claims that comparison.
- **Held constants (§2.6):** each verified against source — `w_avoid` empty without `DISLIKE` (`pathfinding.py:105-107`), floor counts only `KNOWN`/`DISLIKE` (`:42-43`), ramp counts only `KNOWN` (`:130`), `Exclusion.reason` is a plain `str` (`:19-22`) so a third reason string is runtime-safe, `hard` set built reason-blind (`:93`) and skipped before any cost (`:146`), detour re-reads the same list (`:226-228`). `pop_raw` summed pre-cap (`pipeline.py:379-389`), rescale pre-cap (`:369-377`), fame post-cap (`:448`), `_log_scaled` (`graph.py:285-300`).
- **§2.7 dormant term:** the floor arithmetic is as stated (`effective_floor_raw`, `config.py:117` = 0.15).
- **Ceiling search monotonicity (executability):** raising `c` only adds admissible nodes; if an interior-bearing journey exists at `c`, `find_journey` at any `c' > c` returns one (direct path → detour with the direct edge banned, `:222-231`). So "lowest distinct percentile admitting an interior-bearing journey" is well-defined and equals the minimax bottleneck `DRP-G9`(d) compares it to.
- **Unrun cells:** §7 lines 650–659 carry one standalone sentence per cell class keeping it alive; `DRP-R11` names its run state (*swept* for `DRP-S1P0`); no read is reachable on a partial lattice.
- **Pair draw and replication rule:** §4 matches `graph_descriptives.py:58-67, 185-195, 231-234` (measured pool, ascending id, one `Random(SEED)`, FAMOUS then MID, `sample(pool, 2)`, unordered-pair rejection).

## Executability — points a cold session would still have to decide (beyond findings 1, 4, 8)

- How `DRP-C9`'s per-term shares are computed along a returned path (no cost is returned; the recomputation from path + cfg + k is implied, not written).
- Whether the ceiling exclusion set is "pctl > c" (implied by `DRP-G9`(b) "above its recorded `c`") — say it.
- `DRP-G9`(a) with `F_max ≡ 1.0` passes an empty exclusion list (clip at `graph_store.py:193`), so it tests plumbing only; fine, but say so.

## Owner material

- `DRP-D1`–`D3`: **exact line matches** against #200. D4/AM2/AM4: finding 2.
- Requirements: `REQ-12/13/14/16/17/18/27/33/34/35/37/38/39/41/42` all paraphrased accurately (`PRODUCT-REQUIREMENTS.md:175-204, 254-257, 290-312, 388-400`); `REQ-18` is an Expect (§ "Expect", `:201`); `REQ-17`'s "dozens of presses … stress cases" (`:197-199`); `REQ-27` quoted correctly (`:254-255`); §8 forward note of 2026-09-27 exists (`:361-368`).
- Every criterion, gate and read carries a plain sentence; the `DRP-R8` label is the one place the sentence has no number behind it (finding 4).
- No figure restated from the five owners; one from `JFX-` (finding 10).

## Direction

If every cell ran as specified, the owner learns, per famous tier, whether extra exits, a stronger ramp, a per-press ceiling, or combinations make presses 7–10 land on less-famous middles than today's app under the same pressing, without shortening (`DRP-C2`) and without removing famous artists at presses 0–3 (`DRP-C6`), plus a per-press shape and a supply-vs-pricing diagnostic. That is the #200 depth question in fame currency.

What #200 needs that this design cannot answer, and mostly says so:
1. **Coherence and `REQ-27`'s "highly similar" half** — nothing offline (§10); the ceiling in particular forces descent by construction (`DRP-R9`(vii)), so a ceiling MOVES says nothing about whether the journeys hang together until stage 5.
2. **The `DRP-T2` tier gets no exits of its own** — centres are top-1 % only (§2.3), so a `DRP-S1` null on `DRP-T2` does not test "give the 0.95–0.99 tier exits"; `DRP-R0`'s "leaves open" should name that explicitly.
3. **The owner's own pairs and presses** (`DRP-X2`, `DRP-X3`) — random pairs under a mechanical press rule.
4. **#200's definition question** (audience size / Spotify) — out of scope by `DRP-D3`, correctly.
5. **`DRP-D2`'s condition** is evaluated at adoption, not by any read; and `DRP-C6` no longer tests the ceiling at all (the document says so, line 1406).
6. **A ceiling candidate's shipped form** — an identity gate is owed and undesigned (`DRP-AM4` item 2).
7. **The use-gate criterion** — owed (§9); stage 5 cannot start without it.

## Claims verified true

- api `config.py`: `graph_path` default `graph-lba-a6.bin` `:55-57`; `w_sim`–`w_avoid` `:79-83`; `w_degree_hub` = 0.0 `:89`; "adds a toll on widely-listened-to artists" `:93-95`; `w_known_ramp_fame_pctl` = 0.01 `:114`; `floor_relax_known` 0.15 / `dislike` 0.08 `:117-118`; `:174` is `clip_cache` (so `DRP-AM1-O6` is right).
- `pathfinding.py`: `effective_floor_raw` `:25-49`; reasons `:42-43`; `hard` `:93`; floor applied `:103-104`; avoidance `:105-107`; ramp `:130-132`; skip `:146`; cost terms `:156-161`; ramp added, target exempt `:169-170`; strict `<` `:172`; `find_journey` `:194-231`; detour `:226-228`; last changed `a4ff9c6` 2026-08-05.
- `graph_store.py`: `fame_percentiles` `:148`; nulls → 0.0 `:190-192`; clip `:193`; `neighbours_of` row order `:218-221`; version refusal `:247-248`; `edge_types` discarded `:282`.
- builder `config.py`: `cap_strategy` `:106`; `union_top_j`/`union_degree_ceiling` 50 `:110-111`; cosine "film cast list" `:154-157`; damping-with-clip note `:166-170`; `similarity_damping` 0.0 `:174`; `p99_log_clip` `:191`.
- `graph.py`: `trimmed_union_cap` `:175`; union/symmetrise `:228-234`; `strength` key `:238-242`; `_log_scaled` `:285-300`; ids sorted by MBID `:328-329`; `pop_raw` `:337`; row sort `:349`; one `edge_type` `:363`.
- `pipeline.py`: `damped_strength` `:61-81`; raise on damping > 0 `:103-107`; rescale `:369-377`; indegree `:379-389`; ranking unclipped `:396`; cap `:404-414`; fame after cap `:448`.
- `artifact.py`: `FORMAT_VERSION = 1` `:85`; `edge_types` uint8 `:171`. `models.py` (api) fallback comment `:24-28`; `app.py:_to_exclusions` `:31`.
- `cre_ladder.victim_key` `:44-53`; `graph_descriptives.py` module-identity asserts `:100, 106-107`, print fields `:249-261`, `.out.txt:4` from worktree `dogfish`; `cb_build_variants.py` `:163-256`, `quota=0.2` `:166`, docstring `:182-187`, `:195-202`, `:228-233`, `reserve` `:234`, `:238`, `:248-249`; `trim_supply.py` pins `:64-65`, `SUP-S3` `:31`; `cand_build.py:82` pin.
- `graph-lba-a6.bin` sha256 `28311d81…` = sidecar = pin; `S4-A6/MANIFEST.json` sha256 `950e3ee8…` = pins. `C:\unsung-fast\` exists.
- `DRP-` free on every other ref; `397b022` exists and is an ancestor of HEAD; `ba6fdb5` is the critique commit; issues #244, #246, #247 exist; `acceptance.py` exists.
- `NEXT.md`: toll family closed `:228-230`; exhausted nulls `:225`; `PLA-R1` `:233`; no revert trigger `:201`; `LAL-R1`/`LBA-G5` run-once `:204-205`; `R2`/`ALG-E`/`DD-F1` bar `:210`; router-side pricing track corrected 2026-09-27 `:147-152`; `NEXT-ARCHIVE.md:2990` `TB-P5H-7` discharged 2026-08-03.
- Track 3b log: `TB-R2` `:63`, `TB-P5H-7` `:171, 182`, §5 `:175`. `CRE-` prereg: 0.015 floor `:160`; `CRE-C1` conjunction `:447-454`; `CRE-C4` ≥ 0.70 baseline-relative `:479-491`; `CRE-D3` `:336`; `CRE-D2` `:350`; `CRE-C6` `:361`; `_log_scaled` low/high row `:103, 379`; 0.05 null trigger `:138`; `CRE-R0` "no viable pricing regime" `:532`; bracket 0.01/0.03 vs drafted 0.05/0.15 `:272-277`; `CRE-G2`(b) `:413-416`; `CRE-AM2` anchor rule `:731`. CRE results: `B-S1-P1a/b` on `ALG-B` §0 `:27`; §3 "lands within a handful of presses" `:396-402`. Track B results: `CRS-C4` `:85-90`, `CRS-C5`/`R2` router took none at production weights `:92-99`, `CRS-G3` `:111`. `JFX-AM1` §`AM1.2` `:82`, `AM1.3` `:106`, `AM1.9` `:249-253`. `LBA-D3` `:100`, `LBA-AM4` insert `:954-960`, `LBA-AM5` `:966`, contamination `:1702`.
- Figure owners: sections §1 A/§1 B/§2/§3/§4 of graph-descriptives, §1–§4 of trim-supply ("Why the strongest are the famous ones" `:246`, "Treat it as a routing question" `:305`, "Measure the quality of the discarded candidates first" `:309`), squeeze README "Materiality" `:82-87` and by-band table `:157-168`, served-fame depth rows `:48-53` — all exist where cited.
- Critique README: `F1`–`F14`, `O1`–`O6`, Measured table, "§13 claims that do not resolve" (none failed) — present.

## Could not verify

- The words of `DRP-D4`, the "outside review" behind `DRP-AM2`, and the request behind `DRP-AM4` (finding 2) — no committed record.
- `LBA-AM4`'s four bars verbatim and `GBL-` §5's run-once rule text (pointers found at `LBA` prereg `:954-960, :1702`; texts not read). `CRS-G3`'s bar value. `CRE-` §9 as the origin of 0.70 (not read).
- That `trim_supply.py`'s pass-through capture exposes the `ranking` and rescaled `adjacency` inputs `DRP-S1` needs (docstring `:9-12` says wrappers record inputs; body not read).
- The analyst's measured figures and every effect size — out of scope by the brief.
