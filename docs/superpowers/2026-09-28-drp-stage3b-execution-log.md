# Execution log — `DRP-` stage 3b, the `DRP-S0` row (#200)

**Role: ACTIVE — the retained execution log for stage 3b** of
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8. Appended per task. It owns no status (`NEXT.md` does) and restates no figure the
committed outputs own: each entry points at its output file.

**Governs:** the pre-registration's body (execute-from-body since `DRP-AM5`). **Starts from:** the
stage-3a log's "Seam A" entry ([`2026-09-27-drp-stage3a-execution-log.md`](2026-09-27-drp-stage3a-execution-log.md)),
read cold by a fresh session. **Go:** the owner's stage-2 go (recorded in the stage-3a log); his scope
for this session, 2026-09-28: stages 3b and 3c, with 3c in a separate session (he confirmed Seam B
as a handoff).

**Seam B (the end of this log's scope):** one committed JSON per `DRP-S0` cell (artifact sha, cell id,
per-depth journeys as node ids, per-term stats, dropped set), `DRP-G4`, `DRP-G5` and `DRP-G9` recorded
and passing. Nothing in 3c or 3d runs from this session.

**Code and outputs:** [`builder/analysis/2026-09-28-drp-stage3b/`](../../builder/analysis/2026-09-28-drp-stage3b/).
Shards and logs live under `C:\unsung-fast\drp-stage3b\`; the committed per-cell files are the merge of
the shards.

---

## Orientation. 2026-09-28

- Repo clean at `92b52b6` (= `origin/main`, #250 merged); no other live session (the stage-3a worktree
  is gone, the main tree is clean). `graph-lba-a6.bin` sha `28311d81…` matches its sidecar; the
  `DRP-S1` artifact matches `418fe666…`. Deferred issues #246, #247, #249 re-tested: none due (each
  waits on 3d or stage 4).
- Verified one handoff claim against code: `drp_common.py` carries `ladder`, `bottleneck`,
  `ceiling_excludes` as the Seam-A entry says.

## Task 1 — the harness. 2026-09-28

- `drp_sweep.py`: one generalised ladder over the eight cells (the `DRP-S1` rows are listed so 3c reuses
  it; none is run here). Sharded per (cell, set, rule); `merge` writes the Seam-B file.
- **Decision (mine, methodology): both press rules are run on all four pair sets, `DRP-C8` included.**
  §4 names the primary rule for the replication set and lists `DRP-C8` among the random rule's stratum
  identifiers; §7 *swept* reads "under both press rules on all three strata plus the replication set".
  The extra runs are descriptive and cost minutes.
- **Decision (mine): the relaxation search is a bisection over the distinct percentiles above
  `F_max(k)`, after testing `F_max(k)` itself** (`DRP-AM5-F1`). It relies on admissibility being
  monotone in `c`, argued from source in the function's docstring (`find_journey` returns an
  interior-bearing journey exactly when some s–t path with an interior avoids the excluded set) and
  checked per relaxed press by `DRP-G9`(c) and, independently, (d).
- **Decision (mine): `DRP-C9`'s terms are recomputed at sweep time** from `cfg`, the `KNOWN` count on
  the list actually passed and the shipped `effective_floor_raw`, per edge as `pathfinding.py:155-170`
  writes them; per-edge similarity is kept so 3d can take the band's realised median.
- **Decision (mine): each press's victim is recorded** (a node id), so the gates rebuild every press's
  user list without replaying the random generator.
- `drp_gates_3b.py`: `DRP-G4`, `DRP-G5`, `DRP-G9` (a)–(f) with every red control, and **H0**, a
  harness-identity check of this stage's own: the generalised ladder against stage 3a's
  `drp_common.ladder` (which `DRP-G1` validated) on A0, primary rule, `DRP-T1`/`T2`/`C8`, and against
  stage 3a's seed-1 random journeys.

## Task 2 — the sweeps, `DRP-S0` row. 2026-09-28

- **Timing probe:** A0 on `DRP-T1`, primary rule, 108 s for 40 pairs. The ceiling cell takes 10–60 s per
  famous pair, because of the relaxation search at presses ≥ 4. Accepted as is: sharded 14 at a time,
  under this machine's free memory at about 250 MB per process. The search was not changed for speed.
- **Harness defect found and fixed before any shard was used:** at `F_max` = 1.0 (presses 0–3, and every
  press of `DRP-G9`(a)'s identity run) where no journey with an interior exists at all, the search
  indexed an empty list of percentiles above 1.0. Fixed: it returns "no ceiling admits one" (`c`, `r`
  None) and keeps the user-exclusions-only journey, which §2.1's relaxation rule already specifies.
  **Every shard was discarded and re-run on the fixed harness**, so each cell is a single harness version
  (the gate script refuses mixed versions).
- `harness_sha256` in every shard is the sha of `drp_sweep.py` as committed (LF). A Windows checkout
  with CRLF conversion hashes differently; compare against `git show <commit>:<path> | sha256sum`.
- **Second restart: the bisection was too slow on `DRP-T2`** (one pair ~19 min; one shard finished no
  pair in 20 min). Every refused `find_journey` call exhausts the reachable map, and bisection spends
  about nine of them per relaxed press; next-tier endpoints fall under the ceiling from press 4 on.
- **Decision (mine, methodology), and it departs from `DRP-AM3` item 4's wording, so it is stated here
  and in the PR for the owner or 3d to weigh:** the relaxation now takes a **candidate** `c` from stage
  3a's own minimax search (`drp_common.bottleneck`) and **certifies** it with the shipped `find_journey`:
  an interior-bearing journey at the candidate, and none at the next-lower distinct percentile (or at
  `F_max(k)`, already refused). Under the monotonicity the bisection itself relied on, those two calls
  fix `c` exactly as the bisection would. A failed certification falls back to the full bisection, and
  each press records which route it took (`search`: `fmax` / `certified` / `bisected` / `none`).
  - **What this does to `DRP-G9`(d).** Its purpose (`DRP-AM3` item 4) was that `find_journey`'s
    admission threshold and the independent minimax bottleneck are computed separately and must agree.
    Under certification the agreement is **tested by the certifying `find_journey` calls themselves**:
    a wrong bottleneck fails certification, drops to bisection, and (d) then reports the mismatch. So
    (d) still has force, but it is no longer two separate searches meeting at the same number. **Any
    `bisected` press is a finding for the gate, not noise.**
  - **The gate script re-routes both sides of every relaxed `c` itself** ((c): the next-lower ceiling
    must admit nothing, and the recorded `c` must admit a journey), rather than trusting the sweep's
    record.
  - **Why not stop at a seam for this:** no bar, definition, pair or criterion changes; `c` is the same
    quantity, and the gate keeps an independent side. A change to what is measured would be a material
    amendment and a seam. A change to how the same quantity is found, checked from both sides, is not.
- All shards discarded again and re-run on this harness.
- 40 shards, all exit 0, one harness version (`6213bb1e…`, as committed). Merged into the four cell
  files; shas in the directory README.

## Task 3 — gates. 2026-09-28

- `DRP-G9` run as eight parallel partials (one per set × rule), then H0, `DRP-G4`, `DRP-G5` and the
  combination in one process. **All PASS; every red control fired.** Outcomes:
  [`builder/analysis/2026-09-28-drp-stage3b/README.md`](../../builder/analysis/2026-09-28-drp-stage3b/README.md),
  counts in `drp_gates_DRP-S0.json`.
- **Every relaxed ceiling press was certified; none fell back to bisection.** So the task-2 decision
  never had to lean on its fallback, and `DRP-G9`(d) found nothing to report.
- **Decision (mine): the Seam-B README reads no result.** No criterion is computed and no outcome
  assigned: §7 bars any read before *complete*, §4's drop rule needs all eight cells, and §8 gives the
  reading to 3d, a session that ran no sweep. A sweep session's framing of its own row is exactly what
  that rule keeps out.

## Seam B — reached 2026-09-28

**The `DRP-S0` row is *swept*** (§7): four cells, both press rules, all four pair sets, `DRP-G4`, `G5`,
`G9` passing. One committed JSON per cell. **Nothing from 3c runs from this session** (the owner's
choice, 2026-09-28: 3c in a separate session).

**What 3c inherits and must not redo:** everything stage 3a's Seam A lists, plus `drp_sweep.py` (the
`DRP-S1` cells are already in its table, and its map loader refuses unless `DRP-G3` passed on the pinned
artifact) and `drp_gates_3b.py` (run with `DRP-S1`; H0 is `DRP-S0`-only by design, since the `DRP-S1`
ladder is the same code). **What 3c must build or run:** the eight `DRP-S1` shards per cell plus the
eight `DRP-S1P3` identity shards; the merges; the gates; **`DRP-C10`'s per-pair frontier count** (still
3c's, per the Seam-A handoff: it needs the band journeys); and `DRP-C5`'s `DRP-S1P0` half is computable
from the committed files once `DRP-S1P0` exists. **Cost to budget:** the `DRP-S0` row took about 2.5 h
wall at 14 processes; the ceiling cell dominated (48–75 min per shard). On `DRP-S1` the famous pairs have
more room (stage 3a's headroom), which may change the ceiling cell's cost in either direction.
