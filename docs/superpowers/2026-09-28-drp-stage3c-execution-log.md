# Execution log — `DRP-` stage 3c, the `DRP-S1` row (#200)

**Role: ACTIVE — the retained execution log for stage 3c** of
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8. Appended per task. It owns no status (`NEXT.md` does) and restates no figure the
committed outputs own: each entry points at its output file.

**Governs:** the pre-registration's body (execute-from-body since `DRP-AM5`). **Starts from:** the
stage-3b log's "Seam B" entry ([`2026-09-28-drp-stage3b-execution-log.md`](2026-09-28-drp-stage3b-execution-log.md)),
read cold by a fresh session, as the owner chose. **Go:** the owner's stage-2 go (stage-3a log); his
scope for this session, 2026-09-28: *"Pick up DRP stage 3c"*.

**Seam C (the end of this log's scope):** one committed JSON per `DRP-S1` cell, `DRP-G4`, `DRP-G5` and
`DRP-G9` recorded and passing, and `DRP-C10`'s per-pair frontier count. Nothing in 3d runs from this
session.

**Code and outputs:** the sweep and gate scripts are stage 3b's, run unmodified in what they measure
(below), so the `DRP-S1` cell files and `drp_gates_DRP-S1.json` land beside the `DRP-S0` ones in
[`builder/analysis/2026-09-28-drp-stage3b/`](../../builder/analysis/2026-09-28-drp-stage3b/). This stage's
own code and README: [`builder/analysis/2026-09-28-drp-stage3c/`](../../builder/analysis/2026-09-28-drp-stage3c/).
Shard logs under `C:\unsung-fast\drp-stage3c\logs\`; shards and gate partials in stage 3b's
`C:\unsung-fast\drp-stage3b\` folders, where the harness writes them.

---

## Orientation. 2026-09-28

- Repo clean at `28c9da7` (= `origin/main`, #251 merged); no other live session (the main tree is
  clean). `graph-lba-a6.bin` sha `28311d81…` and `graph-drp-s1.bin` sha `418fe666…` each match their
  sidecar. Deferred issues #246, #247, #249 re-tested: none due (#246's trigger is read by 3d; the other
  two wait on stage 4). Three unticked `TEST-QUEUE.md` boxes, the owner's, named to him.
- Verified one handoff claim against code: `drp_sweep.py` lists the four `DRP-S1` cells and its
  `load_map` refuses the `DRP-S1` map unless `drp_g3.json` passed on the pinned sha.

## Task 1 — the harness, unchanged; one gate-script defect fixed. 2026-09-28

- **The harness sha has to be the committed one, and a fresh Windows checkout is not.** With
  `core.autocrlf=true` the worktree's `drp_sweep.py` hashed `171e2a24…`, not the committed LF sha
  `6213bb1e…` that every `DRP-S0` shard carries. Normalised the three harness files to LF on disk
  (content-neutral: `git diff` empty) before any shard ran, so **both rows are the same harness
  version, byte for byte**, and the handoff's "3c uses the same harness" holds by sha, not by claim.
- **Defect found and fixed in `drp_gates_3b.py` before any gate ran: `DRP-G9`'s partials were not
  keyed by row.** They were written as `g9__SET__RULE.json`, so the `DRP-S1` partials would have
  overwritten the `DRP-S0` ones, and — because both rows share one harness sha, which is the only thing
  the combining step checked — a `DRP-S1` combining run finding the `DRP-S0` partials would have
  accepted them. Now `g9__ROW__SET__RULE.json`, each partial records its row, and the combining step
  refuses a partial from another row. Stage 3b's eight partials were renamed to the new form (outside
  the repository; contents untouched). What `DRP-G9` computes is unchanged. **Check that the edit
  changed no verdict:** the `DRP-S0` combining run is re-run after the sweeps and must reproduce
  `drp_gates_DRP-S0.json` byte for byte.
- `drp_c10_frontier.py` (new): `DRP-C10`'s per-pair frontier count, over all eight cells (`DRP-R2`
  asks for it on A0). **Decisions (mine, methodology):** the band journeys are the band depths (7–10)
  at which the cell returned an interior-bearing journey, recorded per row, so 3d can apply §4's
  cross-cell drop rule; the count is kept two ways, `incident_all` (endpoints included) and
  `incident_interior` (endpoints out), because a `DRP-T1` pair's endpoints are themselves added-edge
  centres and "within one hop of the band journeys' nodes" does not say which — **the read picks, not
  this script**; `used` counts added edges the journeys traverse, and is refused if non-zero on a
  `DRP-S0` cell. The added-edge set comes from the two CSRs and must equal `drp_g3.json`'s count. **Red
  control** through the same counter: a synthetic band journey over one added edge must count it used;
  the same journey outside the band must count nothing. Dry-run on the four `DRP-S0` cells: control
  fired, added-edge count matched, every row written.

## Task 2 — the sweeps, `DRP-S1` row. 2026-09-28

- 40 shards (32 sweep, 8 `DRP-G9`(a) identity runs), 14 at a time, ceiling cell first; launch pattern
  `C:\unsung-fast\drp-stage3c\logs\jobs_all.txt` and `run1.sh`.
- Merged the four cells (per-cell shas in the stage-3c README; each merge refuses mixed graph or
  harness shas). **All 40 shards exit 0, one harness version, `6213bb1e…`.** About 2 h wall.

## Task 3 — gates and the frontier count. 2026-09-28

- `DRP-G9`'s eight partials on `DRP-S1` in parallel (about 18 min), then the combining run: **`DRP-G4`,
  `DRP-G5`, `DRP-G9` (a)–(f) all PASS; every red control fired.** Every relaxed press certified; none
  bisected. Outcomes and counts: the stage-3c README and `drp_gates_DRP-S1.json`.
- **The gate-script edit changed no verdict:** the `DRP-S0` combining run, re-run on the edited script
  and the renamed partials, reproduced `drp_gates_DRP-S0.json` **byte for byte** (`a8ebe145…`, the sha
  stage 3b committed), H0 included.
- Launch trap met here, for the next session: `cd api && (A) & (B) & wait` runs the `cd` inside the
  first background job only, so B started in the worktree root and failed to find its script. Run both
  from an explicit `cd` each, or one after the other.
- `drp_c10_frontier.py` over all eight cells: red control fired, added-edge count matched stage 3a's,
  320 rows per cell. **No fraction computed; no result read** (the Seam-B decision, kept).

## Seam C — reached 2026-09-28

**The `DRP-S1` row is *swept*** (§7), so **all eight cells are**: four cells here, both press rules, all
four pair sets, `DRP-G4`, `G5`, `G9` passing, one committed JSON per cell, plus `DRP-C10`'s frontier
count. **Nothing from 3d runs from this session** (§8: 3d is a session that ran no sweep).

**What 3d inherits:** the eight cell files (all in `builder/analysis/2026-09-28-drp-stage3b/cells/`),
both gate verdicts, stage 3a's instruments (`N_noise`, `b₀`, the pair set), `drp_c10_frontier.json`,
and two choices left to it by design: which frontier count (`incident_all` or `incident_interior`)
§2.4's condition reads, and forming §4's cross-cell drop set from the eight `dropped_in_this_cell`
lists. It also reads `DRP-R11` (`DRP-SW`'s trigger, #246) from `DRP-S1P0`, and weighs stage 3b's
search departure from `DRP-AM3` item 4, which this row inherited unchanged.
