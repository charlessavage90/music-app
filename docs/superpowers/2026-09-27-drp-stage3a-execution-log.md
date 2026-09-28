# Execution log — `DRP-` stage 3a, the instruments (#200)

**Role: ACTIVE — the retained execution log for stage 3a** of
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8. Appended per task. It owns no status (`NEXT.md` does) and restates no figure the
committed outputs own: each entry points at its output file.

**Governs:** the pre-registration's body (execute-from-body since `DRP-AM5`). **Go:** the owner's
stage-2 go, 2026-09-27, in session ("Just go as designed", after being shown §10's weakest link and
the option of stopping at Seam A); relayed to
[#244](https://github.com/charlessavage90/music-app/issues/244#issuecomment-5861972775) by this
session. ⚠ `DRP-AM5-I2` says his go lands on #244 **posted by him**; the session's relay does not
meet that, and the owner has been asked to post his own line. Until he does, cite the relay as a
relay.

**Seam A (the end of this log's scope):** every gate outcome (`DRP-G1`, `G1r`, `G2`, `G3`, `G6`,
`G7`, `G10`), the `DRP-S1` artifact sha and `N_noise` committed. Nothing in 3b–3d runs from this
session's context unless the seam is crossed cleanly.

**Code and outputs:** [`builder/analysis/2026-09-27-drp-stage3a/`](../../builder/analysis/2026-09-27-drp-stage3a/).
Gitignored state (the `DRP-S1` artifact, the build capture, anything name-bearing past the
endpoints) lives under `C:\unsung-fast\drp-stage3a\`; its sha256s are committed.

---

## Task 1 — the pair set (§4). 2026-09-27

- `drp_pairs.py` drew `DRP-T1`, `DRP-T2`, `DRP-MID` (40 each, seed 20260928, §4's rule) and
  regenerated the `DRP-C8` replication set (graph-descriptives' FAMOUS draw, seed 20260927).
  Output: `drp_pairs.json` (endpoints only: node ids, MBIDs, names, percentiles). Its sha256 is
  printed by the script and recorded in the commit that adds it.
- **Committed before any cell is swept**, as §4 requires. No journey was routed to draw it.
- Snyk code scan of the directory: 0 issues.

## Task 2 — `DRP-G2`, the `DRP-S1` artifact, `DRP-G3`, `DRP-C10`. 2026-09-27

- `drp_build_s1.py build`: the shipped `build_from_archive` with `trim_supply.py`'s pinned config
  (17.6 min). **`DRP-G2` PASS** on all six fields, and the rebuild serialises byte-identical to
  `graph-lba-a6.bin`. The red control (`union_top_j` 49) **fired**. Outputs `drp_g2.json`,
  `drp_g2_red.json`.
- **Decision (mine, methodology):** G2 compares against the builder's own `deserialise` of the file,
  not the api `GraphStore`, because `GraphStore` does not keep `edge_types` or raw `fame_lb`.
- `DRP-S1` built by §2.3 and serialised by the shipped `serialise`; sha and construction record in
  `drp_s1_build.json` (added edges as node-id pairs with float32 score bytes; no names). The capture
  (`capture.pkl`) is saved outside the repo so `DRP-G3` could re-derive from the same capture.
- **Decision (mine):** the added edge's score is the max of the two directed rescaled scores in the
  cap's input, with 0.0 for an absent direction, which is `graph.symmetrise`'s own arithmetic
  (§2.3 rule 4). `DRP-G3`(i) re-derives it independently and agreed byte for byte.
- `drp_g3.py`: **`DRP-G3` PASS**, 0 violations; both red controls fired. `DRP-C10`'s structural
  half written to `drp_g3.json`. **Deferred to 3c, by necessity, not choice:** `DRP-C10`'s per-pair
  frontier count, which needs the band journeys.

## Task 3 — `N_noise`, `DRP-G6`, `DRP-G7`. 2026-09-27

- `drp_noise.py`: A0 at `ApiConfig()` defaults, random press rule, seeds 1 and 2, on `DRP-T1` and
  `DRP-T2`. **Decision (mine):** only the two famous strata are run, because §5 defines `N_noise`
  per famous stratum and nothing reads it elsewhere; the seed-1 runs on every stratum are the A0
  cell's `DRP-C7` companion and belong to 3b.
- **`DRP-G7` PASS** (every drawn pair, all four sets). **`DRP-G6` PASS**: `N_noise` = 0.015 in both
  famous strata, as §5 expected. Figures: the directory README.
- The random-press journeys (node ids) are in `C:\unsung-fast\drp-stage3a\drp_noise_journeys.json`,
  sha in the README; committed output holds per-pair M values only.

## Task 4 — `DRP-C11` and `DRP-G10`, both maps. 2026-09-27

- `drp_headroom.py`, run only after `DRP-G3` passed (it refuses otherwise). **`DRP-G10` PASS** on
  every (pair, map). **Decision (mine):** where `b₀` would be infinite, G10's check becomes "no
  interior-bearing journey exists with no exclusions"; it did not arise (every `b₀` finite).
- §2.5 gains a pointer to the distribution (the row says it is appended at Seam A); the figures stay
  in the README, since the pre-registration owns none.

## Task 5 — `DRP-G1` and `DRP-G1r`. 2026-09-27

- `drp_g1.py g1`: **`DRP-G1` PASS**, 80 of 80 of graph-descriptives' pairs identical on every field
  `graph_descriptives.py:249-261` prints, routed by this worktree's shipped `find_journey`.
- `drp_g1.py g1r`: **`DRP-G1r` fired** at the ramp 0.015 (78 of 80 pairs diverged); count only.
- **Decision (mine):** a G1 divergence would have printed the two rows (endpoint names and interior
  medians only, the same content as the committed graph-descriptives output). None occurred.

## Seam A — reached 2026-09-27

**Every Seam-A gate passed** (§7 *gated*: `DRP-G1`, `G1r`, `G2`, `G3`, `G6`, `G7`, `G10`), every red
control fired, the `DRP-S1` artifact sha and `N_noise` are committed. Outcomes and figures:
[`builder/analysis/2026-09-27-drp-stage3a/README.md`](../../builder/analysis/2026-09-27-drp-stage3a/README.md).
**No arm was swept.** Next is stage 3b, the `DRP-S0` row, from a fresh session reading this log, the
README and the pre-registration's body cold (§8's seams; `plan-discipline` rule 3).

**What 3b inherits and must not redo:** the committed pair set; `N_noise` = 0.015 per famous
stratum; `drp_common.py`'s ladder, press rules, `bottleneck` and `ceiling_excludes` (the latter two
for `DRP-P3`'s relaxation search and `DRP-G9`(d)). **What 3b must build:** the per-cell sweep
under both press rules on all three strata plus `DRP-C8`, the Seam-B JSON per cell (§8), `DRP-G4`,
`DRP-G5`, `DRP-G9` with its red controls, and the `DRP-P3` relaxation search by the shipped
`find_journey` (§2.1 row; `DRP-AM5-F1`: test `F_max(k)` first). **Cost to budget:** an A0 ladder
takes about 5–10 s per famous pair and about 50 s per middle-of-the-map pair at 21 presses on one
core; the ceiling cells multiply that by the relaxation search at presses ≥ 4.
