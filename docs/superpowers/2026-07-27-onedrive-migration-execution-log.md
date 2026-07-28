# Execution log — OneDrive migration, 2026-07-27

**Role: ACTIVE.** The retained execution log for
[`plans/2026-07-27-onedrive-migration.md`](plans/2026-07-27-onedrive-migration.md). Appended
**per task**, not at closeout, so a successor session can pick up cold. Identifiers `MIG-`.

**Owns no figures about scoring or path quality** — this work touches none. It does own the
migration's own inventory numbers, which live nowhere else.

**Source tree** (authoritative until Phase D):
`C:\Users\charl\OneDrive\Claude Projects\music-app`
**Destination:** `C:\dev\music-app`

> **While Phases A–C run, the source tree is authoritative and is the one being edited.** This
> log is committed and pushed from the source tree, then pulled into the new tree. The plan's
> "do not edit both" rule (Task 10) governs Phase D onward, not this.

---

## §1 — Task 0: land the working tree. DONE (already satisfied).

Discharged before this session started, by the merge of PR #35. Verified rather than assumed:

- `git status --short` — empty.
- `git log origin/main..HEAD` — empty.
- `main` at `4c58e7d`, tracking `origin/main`, no local-only branches, no stashes.

The plan's Task 0 text says "four documentation files are currently modified and uncommitted."
That was true when the plan was written and is no longer. **Task 2's safety precondition
therefore holds**: the clone cannot be silently lossy, because there is nothing unpushed for it
to lose.

## §2 — Task 1: pause sync, take the baseline. DONE.

**OneDrive sync paused by the owner for 24 hours**, 2026-07-27, before any inventory ran. The
numbers below therefore describe a still tree, which is the whole point of the ordering.

**Baseline written to `C:\dev\migration-baseline-2026-07-27.txt`** — deliberately outside both
trees, so it survives the move and cannot be destroyed by the thing it is checking. It is the
comparand for Task 4 and must not be regenerated from the destination.

Figures are in that file. Recorded here as the durable copy:

| Quantity | Value |
|---|---|
| `builder/scratch` file count | **75,052** |
| `builder/scratch` total bytes | **1,460,266,074** |
| `graph-archive` file count | **75,000** |
| `graph-archive` total bytes | **900,518,765** |
| Everything outside `graph-archive` | **52 files, 559,747,309 bytes** |
| `.bin` count | **18** |

The 18 `.bin` checksums are in the baseline file and in `C:\dev\bin-SOURCE-fresh.txt`. **Read
them from the latter** — see §12 for why the baseline file is not the copy to trust.

> **Measured throughput matters for anyone repeating this: ~2,000 files per 20 s on the
> OneDrive tree** (`sys` 11.9 s against `user` 0.5 s — filesystem-bound, not CPU-bound). A full
> traversal of `builder/scratch` is therefore ~12 minutes, and the destination walk on `C:\dev`
> took 7.5 minutes for the same 75,052 files. Budget for it; do not assume a hung job.

## §3 — Task 2: clone, do not copy. DONE.

```
git clone https://github.com/charlessavage90/music-app.git /c/dev/music-app
```

*Verified:*

- Destination HEAD `4c58e7d8570eb1b165600d7787d4c766cf3228c1`, **string-identical** to the
  source tree's `origin/main`.
- `git status --short` clean; branch `main` tracking `origin/main`.
- **Tracked file count 439 in both trees.**
- **Both 500-node test fixtures present** (`api/tests/fixtures/graph-fixture.bin`,
  `builder/tests/fixtures/graph-fixture.bin`) — the `!**/tests/fixtures/*.bin` exemption
  fixed on 2026-07-22 survived the clone, which is the first independent confirmation of that
  fix on a genuinely fresh clone.

`MIG-5` is now structurally dead for the new tree: its `.git` was created by origin and has
never been under OneDrive, so it cannot carry `ReadOnly` or reparse-point state. The source
tree's stale `.git/worktrees/lfcheck` was **not** repaired, per the handoff.

## §4 — Task 3 widened: the plan named two gitignored files and there are six

**This is a defect of omission in the plan, found in execution, and it is the class
`CLAUDE.md` warns is unfindable by grep.** `MIG-4` is framed as "secrets left behind" and
names `infra/.env.deploy` and `.claude/settings.local.json`. Enumerating what a clone actually
drops — `git status --ignored`, minus `builder/scratch`, minus everything regenerable — returns
**four more**:

| Path | Bytes | Why it is not disposable |
|---|---|---|
| `.superpowers/` (68 files) | 824,759 | **Contains `sdd/BLIND-MAPPING.json`** — the arm-to-identity key for the blind listening tests. See below. |
| `builder/analysis/2026-07-26-stranding-causes/artifact_nodes.json` | 5,871,522 | Input/output of a committed `STC-` measurement whose `REPORT.md` is tracked. |
| `builder/analysis/2026-07-26-low-degree-census/resolve.log` | 106,077 | Run record of the `CNS-` census. |
| `api/eval/baseline-results.txt` | 1,081 | Recorded baseline output. |

**`BLIND-MAPPING.json` is the one that matters.** The blind listening test is described in
`CLAUDE.md` and `WHAT-GOOD-LOOKS-LIKE.md` as this project's strongest evidence class — it
"decided the graph twice where the offline metrics decided it zero times." The mapping from
blind arm label to real configuration is what makes a past verdict auditable. It is gitignored
by design (a tracked copy would unblind the test), which is precisely why nothing in git
protects it and why a clone-based migration is the moment it would vanish.

**Resolution: carry all six, not two.** Total extra ~6.8 MB against a 1.6 GB job — the cost of
deciding which of these matter exceeds the cost of carrying all of them, and the downside is
asymmetric. This is bookkeeping, not a change of plan scope.

**The three `builder/analysis/` and `api/eval/` files land inside directories the clone already
created**, so they are copied file-by-file rather than as a tree.

*Verified 2026-07-27* — all six copied with `cp -p` (data + timestamps, **not** Windows
attributes, matching `/COPY:DT`'s intent so no `ReadOnly`/reparse state carries):

- Five individual files byte-identical by `stat -c%s`.
- `.superpowers/`: **68 files → 68 files, 824,759 bytes → 824,759 bytes**, and a digest over
  every file's `sha256sum` matches on both sides
  (`1fccf36f0aadb5e92fcae392d21e10f5c6f07b6a1f5f5c33c608190d819c2fc4`) — so this is content
  equality across the whole tree, not a size coincidence.
- `BLIND-MAPPING.json` specifically:
  `f3b0797076ac97516b912718165590853944885138a24cc25fcdfdb35624cf5f` on both sides.

## §4a — A seventh thing the clone drops: git identity itself

**Found the only way it could be found — the first commit from the new tree failed.**

```
Author identity unknown
fatal: unable to auto-detect email address (got 'charl@DESKTOP-4070.(none)')
```

`user.name` and `user.email` were set with **`git config --local`** in the OneDrive tree, and
**there is no global identity on this machine**. Local config lives in `.git/config`, which
Task 2 deliberately does not copy — so a fresh clone cannot commit at all until identity is
reproduced.

*Resolution:* set `--local` in the new tree to the same two values, reproducing the arrangement
rather than changing it. `git config --local --list` is now identical between the trees apart
from remotes and branch tracking. **Deliberately not set globally** — that would alter this
machine's behaviour for every other repository, which is outside a migration's remit.

> **Same shape as §4, different category, which is why it is separate.** §4 is about files git
> *ignores*; this is state git keeps *inside `.git`*, and cloning rather than copying `.git` is
> exactly what discards it. **The two mitigations are in tension: `MIG-5`'s fix caused this.**
> The trade is still right — a failed commit is loud and cost one minute, where imported
> reparse-point corruption is quiet — but it means **anything else in `.git/config` is silently
> gone too.** Checked: nothing else in the old tree's local config is non-default beyond
> identity and remotes.

## §5 — Task 1 method correction: one traversal, and a manifest instead of a total

**The first inventory script was wrong in a way worth recording, because it is the same class
of error as `MIG-9`'s bad count.** It computed six figures with six separate `find` passes.
Measured throughput on this tree is **~2,000 files per 20 s** — filesystem-bound (`sys` 11.9 s
against `user` 0.5 s), which is the OneDrive tax the handoff predicted. Six passes over 75,052
files is roughly 40 minutes for numbers one pass yields.

Killed and replaced with a **single `find` pass emitting `<bytes>\t<relpath>` per file**, with
every figure derived from that file afterwards.

> **The replacement is not just faster — it is a stronger instrument, and that is the reason to
> prefer it.** The plan's Task 4 compares *totals*. A per-file manifest compares *files*, so
> `MIG-1`/`MIG-7`'s silent failure — count matches, bytes do not — surfaces as a diff naming
> the offending path, instead of a two-number disagreement across 75,052 candidates. Manifest:
> `C:\dev\migration-manifest-SOURCE-2026-07-27.tsv`.

## §6 — Task 5: recreate the regenerable. DONE.

Three `.venv`s via `uv sync --extra dev`, `node_modules` via `npm ci`. Nothing copied.

> **Run deliberately WITHOUT `UV_LINK_MODE=copy`, to gather the evidence Task 12 asks for
> rather than infer it.** The plan says the guard must be tested before being removed from any
> document, because "the reason is gone" is an inference. **All three synced clean outside
> OneDrive** — builder installed 24 packages in 5.23 s with no hardlink error. That is the
> observation Task 12 needs; the edit itself is still Task 12's.

## §7 — Task 6: prove the new tree works. PARTIAL — four of five suites.

Run from `C:\dev\music-app`, all without `UV_LINK_MODE=copy`:

| Suite | Result | Plan's pass condition |
|---|---|---|
| builder | **115 passed** | 115 ✓ |
| api | **195 passed** (1 pre-existing deprecation warning) | 195 ✓ |
| infra | **58 passed** | 58 ✓ |
| frontend unit/component | **80 passed**, 13 files | 80 ✓ |
| frontend e2e | **NOT YET RUN** | 5 — blocked, see below |
| `npm run build` | clean, 38 modules, built in 147 ms | ✓ |
| `npm run lint` | clean; one pre-existing `vite.config.ts` triple-slash **warning**, not an error | ✓ |

**e2e was blocked at this point, and it is a real ordering dependency the plan does not name.**
`npm run test:e2e` requires the API on `:8000`, and the API boots
`../builder/scratch/graph-t15-tiebreakfix.bin` — which lives in the archive tree Task 3 had not
yet copied. **So Task 6 cannot fully pass before Task 3 and Task 4.** The plan orders it after
them anyway, so this cost nothing; it is recorded because the four fast suites were
deliberately run early to get signal cheaply, and a successor doing the same should know why
the fifth cannot follow.

**Completed after Task 4 — see §10.**

## §8 — Task 3 archive copy. DONE.

```
robocopy <src>\builder\scratch C:\dev\music-app\builder\scratch /E /COPY:DT /R:2 /W:2 /MT:16
```

| | Total | Copied | Skipped | Mismatch | FAILED | Extras |
|---|---|---|---|---|---|---|
| Dirs | 4 | 4 | 0 | 0 | **0** | 0 |
| Files | 75,052 | 75,052 | 0 | 0 | **0** | 0 |
| Bytes | 1.359 g | 1.359 g | 0 | 0 | **0** | 0 |

38 s of copy at 37.8 MB/s. Log: `C:\dev\robocopy-scratch-2026-07-27.log`.

> **`robocopy` exit code 1 means "files were copied successfully."** Codes below 8 are all
> success. The harness reports any non-zero exit as a failure, so this run was surfaced as
> FAILED when it had in fact succeeded completely. **Do not read a robocopy non-zero exit as
> an error without checking the code**; a successor automating this will meet the same thing.

## §9 — Task 4: verify by bytes, per file. PASS.

| Quantity | Source | Destination | |
|---|---|---|---|
| `builder/scratch` file count | 75,052 | 75,052 | ✅ |
| `builder/scratch` total bytes | 1,460,266,074 | 1,460,266,074 | ✅ |
| `graph-archive` file count | 75,000 | 75,000 | ✅ |
| `graph-archive` total bytes | 900,518,765 | 900,518,765 | ✅ |
| Per-file manifest diff | — | **0 differing files** | ✅ |
| `.bin` count | 18 | 18 | ✅ |
| `.bin` sha256, all 18 | recomputed fresh | identical | ✅ |

**`graph-t15-tiebreakfix.bin` = `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`**
at the destination, matching both its manifest sidecar and the plan's stated value.
`MIG-1` and `MIG-7` are discharged: a placeholder copy cannot produce matching per-file sizes
across 75,052 files *and* 18 matching content hashes.

Artifacts kept outside both trees: `migration-manifest-SOURCE-2026-07-27.tsv`,
`migration-manifest-DEST-2026-07-27.tsv`, `migration-verify-2026-07-27.txt`,
`bin-SOURCE-fresh.txt`, `bin-DEST-fresh.txt`, all under `C:\dev\`.

> **The 18 source `.bin` checksums were recomputed from the source tree rather than read out of
> the baseline file, because that file had been corrupted — see §12.** The corrupted region did
> not touch the checksum block, but reading figures out of a file with a known corruption
> incident is exactly the shortcut this project keeps finding in its own postmortems.

## §10 — Tasks 6 and 7 completed. PASS.

**Task 7 — the new tree serves the same graph.** API booted from `C:\dev\music-app\api`:

```json
{"status":"ok","graph_sha256":"4cb84ef9…b061dc8","artists":74193,"edges":898006}
```

The wire field is `graph_sha256`, as the plan says. This closes the loop from artifact bytes
through to a running service. **Server stopped afterwards; both `:8000` and `:5173` confirmed
free.** No detached server is left running — the plan owes no test-queue entry (§5), so there
is nothing for the owner to press and nothing should be left listening.

**Task 6 — e2e: 5 passed** (15.2 s, 4 workers), against that API. Full Task 6 result:

**builder 115 · api 195 · infra 58 · frontend 80 + 5 e2e — all four suites green, all matching
the plan's stated pass conditions**, plus `npm run build` and `npm run lint` clean.

## §11 — Task 8: project memory. DONE non-destructively; ONE STEP STILL OWED.

`~/.claude/projects/` is keyed by slugified absolute path, so the move orphans memory silently
(`MIG-2`).

**Copied rather than renamed**, to the *predicted* slug `C--dev-music-app`:

- 356 files, 162,102,474 bytes, both sides.
- Content digest identical: `b6bc8aea33218c288c2cd976740129d71b65aa4365356f3a5e15014262d981ad`.
- 12 files in `memory/` (11 memories + `MEMORY.md`), 72 session-history files.

> **Copy, not rename, is the point.** The plan says to confirm the slug **by observation**
> rather than derive it, and a rename would have to guess before observing. A copy makes a
> wrong guess free: the old directory still serves the old path, the new one is either found or
> ignored, and nothing is lost either way.
>
> **⚠ STILL OWED, and it needs the owner:** start a session in `C:\dev\music-app` and confirm
> Claude Code reads `C--dev-music-app`. If it creates a *different* directory, that name is the
> right one and the copy moves there. **Until that observation, `MIG-2` is mitigated, not
> closed.** The duplicate is harmless and should be deleted only after confirmation.

> **`MIG-2` says "ten memory files"; there are eleven.** Minor, but it is stated as a
> *verification criterion* ("`MEMORY.md` and all ten files present"), and a successor checking
> for ten against eleven gets an ambiguous pass. The eleven are indexed in `MEMORY.md`.

## §12 — Incident: two writers raced on the baseline file, and `TaskStop` is why

**Recorded because the failure is the project's own standing hazard — an instrument that
returns a plausible wrong number — and because the mitigation is not obvious.**

The first inventory script (§5) was killed via `TaskStop` and *kept running*. `TaskStop` reaped
the wrapper task; the `bash` process (PID 90820) and its `find` (PID 268576) survived and went
on writing to the same output path the replacement script was writing to. The result
interleaved mid-line:

```
# Per-file manifest: /c/dev/migration-manifes4
archive_file_count=s=1460266074
```

`archive_file_count=` from one writer, `…s=1460266074` — the tail of `total_bytes=` — from the
other.

**Detected by eye, which is not a control.** The corruption happened to be visible. Had the two
writers interleaved on whitespace or between lines, the file would have looked clean and been
wrong.

**What made it recoverable was redundancy that existed for another reason.** The per-file
manifest was written to a *separate, uniquely-named* file with a single writer, so it was
intact; every figure was rebuilt from it. And the leaked value cross-validated the rebuild:
900,518,765 + 559,747,309 = **1,460,266,074**, the dead script's independently-computed
whole-tree total. Two separate traversals agreeing.

**Lessons, both cheap:**

1. **`TaskStop` does not kill the process tree on Windows.** Verify with
   `Get-CimInstance Win32_Process` and `Stop-Process` the survivors by PID. Both were killed
   before the destination walk, so no destination figure is exposed.
2. **A long job's output file should be uniquely named per run**, not a fixed path a retry will
   share with its own zombie.

## §13 — Task 9: Backblaze coverage. NOT RUN — the owner's, and it gates Task 11.

`MIG-3` cannot be verified from here: it needs the Backblaze account. Three things, and the
third is the one that is usually assumed:

1. `C:\dev` is in the backup selection.
2. `.bin` and `.json` are not caught by an exclusion rule.
3. The archive has **completed** an upload rather than merely been queued.

**This gates Task 11** (deleting the OneDrive tree). Until it passes, OneDrive remains the only
second copy and must not be deleted. Retention note: Backblaze purges a deleted file after
~30 days on the default plan, weaker than OneDrive's behaviour — so `MIG-1` and `MIG-3` are not
independent risks.

## §14 — Stopping at the Phase D seam

Phases A, B and C are complete apart from Task 9. **Two complete copies exist and everything so
far is reversible.** Phase D deletes the rollback and is not started.

**State at the seam:**

- Old tree: untouched, clean, at `4c58e7d`. **Still the rollback.** Archive intact, 75,000 files.
- New tree: `C:\dev\music-app`, on branch `onedrive-migration-phases-abc`, clean, archive
  intact, verified by tests, by checksum, and by a running service. PR #36.
- OneDrive sync: **paused by the owner for 24 h from 2026-07-27.** It will resume on its own.
  Nothing in Phases A–C depends on it staying paused, and Task 11 is where it matters again.
- This session started nothing that is still running: `:8000` and `:5173` both free, no
  subagents, no background jobs.

### ⚠ `MIG-11` — two API servers from the OLD tree are running, and they will block Task 11

**Found during the closing sweep. Not started by this session, and this log does not speculate
about where they came from.**

| Port | Listening PID | Process started |
|---|---|---|
| 8138 | 60412 | 2026-07-20 19:41 |
| 8139 | 97220 | 2026-07-20 19:44 |

Both run `artistpath_api.app:build_default_app` from
**`C:\Users\charl\OneDrive\Claude Projects\music-app\api\.venv\Scripts\uvicorn.exe`** — the
*old* tree's virtualenv. They are on non-standard ports, so every port check in this project's
rituals (`:8000` and `:5173`) has been reporting "nothing running" while they were up.

**Why it matters, and it is not the obvious reason.** They are harmless today — nothing routes
through them. But **a live process holds open file handles on the old tree's `.venv`, and Task
11 deletes that tree.** On Windows an open handle makes deletion fail partially and noisily,
leaving a half-deleted tree — which is the worst state for a rollback copy, since it is neither
present nor gone.

**Deliberately left running.** They are not this session's, and stopping another session's
processes is not a call to make silently. **Kill both before Task 11**, and re-check for
non-standard ports rather than only `:8000`/`:5173`.

> **Second-order finding worth more than the incident: the port sweep in `closeout` A5 and
> `session-start` §C only ever looks at `:8000` and `:5173`.** These two survived a week and
> multiple sweeps precisely because they were not on those ports. A sweep that checks two known
> ports cannot find a process on a third, and it reports "clean" either way.
