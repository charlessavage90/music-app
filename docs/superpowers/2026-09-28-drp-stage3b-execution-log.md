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
