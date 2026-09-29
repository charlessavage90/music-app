# `DRP-` stage 3d — the reader (#200)

**Role: COMPLETE. The raw record behind the results note**, which owns the reading:
[`docs/superpowers/findings/2026-09-28-drp-lattice-results.md`](../../../docs/superpowers/findings/2026-09-28-drp-lattice-results.md).
Governing document: [`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](../../../docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §3–§7, executed from the body. Execution log:
[`docs/superpowers/2026-09-28-drp-stage3d-execution-log.md`](../../../docs/superpowers/2026-09-28-drp-stage3d-execution-log.md)
(task 1 fixes the choices the body leaves to 3d, committed before this script first ran).

| file | what |
|---|---|
| `drp_read.py` | every criterion (`DRP-C1`–`C13`), `DRP-G8`, §4's drop set, the per-cell outcomes and the reads (`DRP-R0`–`R13`), from the eight committed cell files. **Routes nothing.** |
| `drp_results.json` | its output, sha256 `a453e0f2101e23700a9cc50ddbcd1873372980d4c1beb5472eb40949044f3a4a` |
| `drp_read.out.txt` | its console output |

**Inputs, each identity-checked before use:** the eight cell files against the shas the stage-3b and
stage-3c READMEs pin (hashed after CRLF→LF normalisation, since `core.autocrlf` checkouts hash
differently); `drp_c10_frontier.json` likewise; both map artifacts against sidecar and pin, loaded
read-only for lba-a6's fame frame and the added-edge set (checked against `drp_g3.json`'s count).

**Sealing (§8):** pair indices, node ids and counts only. No artist is named.

**Verified by a second path:** `DRP-S1P3`/`DRP-T1`'s median `D` and its count past −0.05 were
recomputed by separate code straight from the cell JSON and the `GraphStore`, and agree exactly.
Snyk code scan: 0 issues.

## Reproduce

```bash
cd api && PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-28-drp-stage3d/drp_read.py
```

About a minute. Needs `graph-lba-a6.bin` (`C:\dev\music-app\builder\scratch\`) and `graph-drp-s1.bin`
(`C:\unsung-fast\drp-stage3a\`).
