# Plan — move the project out of OneDrive

**Role: ACTIVE, not yet executed.** Identifier series `MIG-`, verified disjoint from `RMD-`,
`DEP-`, `TR-`, `TKA-`, `TKD-`, `TKB-`, `FMS-`, `CNS-`, `ARC-`, `SEC-`, `QUA-`, `FRO-`,
`BYP-`, `DAF-` by repo-wide grep, 2026-07-27 (no matches).

**Destination: `C:\dev\music-app`.** Owner's decision, 2026-07-27.

**Governing inputs:**

1. This document. Nothing supersedes it yet.
2. [`../2026-07-26-context-layer-maintenance-execution-log.md`](../2026-07-26-context-layer-maintenance-execution-log.md)
   §177–181 — the `.git`-under-OneDrive corruption incident this plan is shaped to avoid.
3. [`../2026-07-26-gate2-track-d-execution-log.md`](../2026-07-26-gate2-track-d-execution-log.md)
   §72, §251 — `TKD-3`, OneDrive file locking, and the note that a checkout outside OneDrive
   never had the problem.

---

## 0. What this is, and the one thing it is really about

Moving 2.4 GB of files is not the risk. **Every tracked byte is already on GitHub**, verified
pushed with no stashes and no local-only branches. A total loss of this machine today costs
nothing that git knows about.

The risk is entirely in the **1.6 GB git deliberately ignores**, and within that, almost
entirely in one thing:

> **`builder/scratch/graph-archive/` — 75,000 JSON files, 1.1 GB.** It is the source every
> graph rebuilds from in ~30 seconds. It cost a rate-limited crawl at 5 req/s: **4¼ hours
> minimum**. And it **cannot be reproduced** — the project's determinism guarantee is
> "identical output for identical *input*", and a fresh crawl of a live third-party API is a
> different input. Re-crawling would not restore it; it would replace it, and silently break
> comparability with every measurement in the record.

The graph artifacts (18 `.bin`, ~500 MB) are second in value and **are not fully derivable
from the archive**, because several were built by since-changed code — one by
`builder/scratch/build_legacy_control.py`. Do not reason about them as "rebuildable".

**OneDrive is currently the only backup of both.** This plan therefore treats the OneDrive
tree as the rollback copy and does not delete it until the new tree has been proven *and*
independently backed up.

## 1. Risk register

Ordered by expected cost, not by likelihood. "Detection" is the column that matters — three
of these fail silently.

| ID | Risk | Likelihood | Impact | Detection |
|---|---|---|---|---|
| `MIG-1` | **Archive lost or partially copied.** 75,000 small files is the worst case for any copy tool; a truncated copy looks identical by name and count. | Low | **Severe** — 4¼ h to re-crawl, and the result is a *different* archive | **Silent** unless byte totals are compared. Task 4. |
| `MIG-2` | **Project memory silently orphaned.** `~/.claude/projects/` is keyed by the slugified absolute path. Move the repo and Claude Code looks up `C--dev-music-app`, finds nothing, and starts with no memory. Ten memory files plus all session history. | **Certain** if unhandled | High | **Silent — nothing errors.** Task 8. |
| `MIG-3` | **Backblaze does not actually cover the new location**, or excludes `.bin`/`.json` by policy. The backup is assumed, not verified. | Unknown | **Severe** — combines with `MIG-1` into total loss | **Silent.** Task 9, and it gates Task 11. |
| `MIG-4` | **Secrets left behind.** `infra/.env.deploy` and `.claude/settings.local.json` are gitignored, so a `git clone` does not carry them. | **Certain** if unhandled | Medium — deploys fail | Loud (failed deploy), but late. Task 3. |
| `MIG-5` | **`.git` corruption carried across.** `.git/logs/` and `refs/` have previously held `ReadOnly` + Files On-Demand attributes that git could not delete. Copying `.git` risks importing that state. | **Observed, not estimated — see below** | Medium | Loud, but awkward to unpick. **Avoided structurally** — Task 2 clones instead of copying. |

> **`MIG-5` is not hypothetical. It fired during the writing of this plan**, 2026-07-27, on
> the push that created the branch carrying this document:
>
> ```
> error: failed to delete '.git/worktrees/lfcheck': Permission denied
> ```
>
> `.git/worktrees/lfcheck/` is a stale registration for a worktree that no longer exists —
> `git worktree list` shows only the main tree — which git tried to prune and could not.
> Its `logs/` and `refs/` carry `0x431` = `ReadOnly` + `Directory` + `Archive` +
> `ReparsePoint`: **the same two directory names and the same attribute combination** the
> 2026-07-26 incident recorded.
>
> **Deliberately not repaired.** Clearing `ReadOnly` inside `.git` under OneDrive to fix
> something Task 2 erases by construction is the wrong trade, and the commit and push both
> succeeded regardless — it is noise, not damage. It will keep printing on operations that
> prune, until the move. **This is the strongest single argument for cloning rather than
> copying**, and it arrived unprompted.
| `MIG-6` | **OneDrive fights the operation**, or deletion of the old tree propagates to the cloud before the new tree is proven. | Medium | Medium | Loud. Mitigated by pausing sync (Task 1) and by never using `move`. |
| `MIG-7` | **Some archive files are OneDrive placeholders** (`RecallOnDataAccess`), so a copy produces empty stubs. | **Low** — a 2,000-file sample showed 0 dehydrated, attribute `0x420` = `Archive`+`ReparsePoint` only | Severe if true | **Silent.** Folded into `MIG-1`'s byte-total check, which does not rely on the sample. |
| `MIG-8` | **Virtualenvs break.** Windows venvs embed absolute paths in their shims; they are not relocatable. | **Certain** | Trivial | Loud and immediate. Recreated in Task 5, not copied. |
| `MIG-9` | **26 frozen `builder/analysis/` scripts stop resolving** — they hardcode `C:\Users\charl\OneDrive\...`. | **Certain** | Low | Silent until one is run. **Accepted** — see §4. |
| `MIG-10` | **Documentation still says "the project lives under OneDrive"** in ~8 places including `CLAUDE.md`, both rituals and three READMEs. | **Certain** if unhandled | Low, but it is the standing context layer | Loud to a reader, silent to a tool. Task 12. |

**Not risks, checked and dismissed:**

- `ApiConfig.graph_path` is **relative** (`"../builder/scratch/graph-t15-tiebreakfix.bin"`),
  so the API default survives the move untouched.
- Disk space. C: has 1030 GB free against a 2.4 GB tree.
- Path length. `C:\dev\music-app` is **33 characters shorter** than the current root (49 → 16),
  so every `MAX_PATH` margin improves.

## 2. Two things that get better, and are worth stating as objectives

1. **`infra/.env.deploy` stops syncing to the cloud.** The site password currently lives in
   OneDrive. After this it does not.
2. **The `.git` failure class becomes impossible**, along with OneDrive file locking
   (`TKD-3`) and whatever is making a `du -sh` of this tree exceed two minutes.

## 3. Tasks

**Do not start until Task 0 is clean.** Every task states how it is verified; a task without
a passing verification is not done.

### Phase A — preconditions (nothing destructive)

**Task 0 — land the working tree.** Four documentation files are currently modified and
uncommitted. Branch, PR and merge them first. Migrating with uncommitted work makes the
clone in Task 2 silently lossy.
*Verify:* `git status --short` empty; `git log origin/main..HEAD` empty.

**Task 1 — pause OneDrive sync**, and take the pre-move inventory *after* pausing so the
numbers describe a still tree.
*Verify:* record and keep — total bytes and file count of `builder/scratch`, and
`sha256sum` of all 18 `.bin` files. This is the baseline every later check compares against.

### Phase B — build the new tree (old tree still authoritative)

**Task 2 — clone, do not copy, the tracked tree.**

```bash
git clone https://github.com/charlessavage90/music-app.git /c/dev/music-app
```

This is deliberate and is the mitigation for `MIG-5`: a fresh `.git` from origin cannot carry
OneDrive reparse points or `ReadOnly` flags. It is only safe because Task 0 proved nothing is
unpushed.
*Verify:* `git -C /c/dev/music-app log -1` matches `origin/main`; `git status` clean.

**Task 3 — copy the untracked treasure**, and only it. Never `move`.

```
robocopy "C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch" ^
         "C:\dev\music-app\builder\scratch" /E /COPY:DT /R:2 /W:2 /MT:16
```

Then the two gitignored files a clone cannot carry (`MIG-4`): `infra/.env.deploy` and
`.claude/settings.local.json`.

`/COPY:DT` copies data and timestamps but **not attributes** — deliberate, so the `ReadOnly`
and reparse-point state that caused the `.git` incident is not carried forward. **Never
`/MIR`**, which deletes at the destination.
*Verify:* Task 4.

**Task 4 — verify the copy by bytes, not by eye** (`MIG-1`, `MIG-7`).
*Verify:* file count and total byte size of `builder/scratch` match Task 1's baseline
exactly; all 18 `.bin` checksums match; `graph-t15-tiebreakfix.bin` is
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, matching its sidecar.
A count match with a byte mismatch is the placeholder failure — treat it as a stop.

**Task 5 — recreate, do not copy, the regenerable 670 MB** (`MIG-8`): three `.venv`s via
`uv sync`, `node_modules` via `npm ci`. `cdk.out`, `__pycache__`, `.pytest_cache`,
`dist` and `test-results` are build output and are simply not carried.

**Task 6 — prove the new tree works.** All four suites, from the new location: builder
**115**, api **195**, infra **58**, frontend **80** + **5** e2e. These counts are Track C's
and are the pass condition.
*Verify:* four green runs, plus `npm run build` and `npm run lint`.

**Task 7 — prove it serves the same graph.** Boot the API from the new tree and read
`/health`. **The wire field is `graph_sha256`** (`api/…/models.py`, `HealthOut`) — not
`source_sha256`, which is the internal `GraphStore` attribute it is populated from and does
not appear in the response.
*Verify:* it reports `4cb84ef9…`. This closes the loop from artifact bytes through to a
running service without trusting any intermediate step.

### Phase C — out-of-tree state

**Task 8 — rename the Claude project directory** (`MIG-2`), from
`~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app` to the slug the new
path produces. **Confirm the exact new slug by observation** — start a session in the new
location and see which directory it creates — rather than deriving it by hand.
*Verify:* a fresh session in the new tree recalls memory; `MEMORY.md` and all ten files
present.

> **`clamp` was evaluated for this task and CANNOT be used on this machine.**
> [`wsagency/claude-move-project`](https://github.com/wsagency/claude-move-project) exists to
> do exactly this — "move Claude Code projects while preserving session history" — and its
> README lists Windows as supported "via WSL or Git Bash". **It is not**, for this path.
>
> Its `encode_path()` is one substitution, `${path//\//-}`, which handles `/` and nothing
> else. Measured on this tree, 2026-07-27:
>
> | | |
> |---|---|
> | `clamp` computes | `-c-Users-charl-OneDrive-Claude Projects-music-app` |
> | Claude Code uses | `C--Users-charl-OneDrive-Claude-Projects-music-app` |
>
> Three independent mismatches: the drive (`C:\` encodes to `C--`, not `/c/` to `-c-`), the
> drive-letter case, and **spaces are never converted** though Claude Code converts them to
> `-`. WSL does not help — there `pwd` yields `/mnt/c/...`, wrong a third way. The
> destination is broken the same way: `C:\dev\music-app` would give `-c-dev-music-app` where
> Claude Code will read `C--dev-music-app`, so the tool would relocate history into a
> directory nothing ever opens — **`MIG-2`'s exact silent failure, performed by the tool
> hired to prevent it.**
>
> The likely failure mode is a safe one (it cannot find the source, so it errors), but do not
> rely on that. **Do Task 8 by hand.** The space-handling gap is probably not
> Windows-specific — Claude Code converted the spaces in this very path — but that has not
> been verified on macOS and is not this plan's business.

**Task 9 — verify Backblaze actually covers `C:\dev`** (`MIG-3`). Confirm the folder is
included, that `.bin` and `.json` are not caught by an exclusion rule, and that the archive
has *completed* an upload rather than merely been queued. **This task gates Task 11.**
*Verify:* Backblaze reports the new location backed up, with the archive included by count
or size. Note its retention: a deleted file is purged after 30 days on the default plan,
which is weaker than OneDrive's behaviour and worth knowing.

### Phase D — cut over (destructive; nothing here is reversible)

> **⛔ Handoff seam. Stop here.** Phases A–C leave two complete copies and are fully
> reversible. Everything below deletes the rollback. Per `CLAUDE.md`'s handoff rule this is
> the natural boundary: the new tree is a committed, verified artifact rather than a live
> understanding, so a fresh session can pick up from Task 10 cold. **Use the app from the new
> location for a few days before proceeding.**

**Task 10 — work from `C:\dev\music-app` exclusively** for an agreed period. The OneDrive
tree stays untouched as rollback. Do not edit both.

**Task 11 — delete the OneDrive tree and resume sync.** Only after Task 9 passed and Task 10
found nothing.
*Verify:* deletion propagates; the new tree still passes Task 6.

**Task 12 — correct the record** (`MIG-10`). `CLAUDE.md`'s environment note, `README.md`,
`api/README.md`, `builder/README.md`, `.claude/agents/ml-graph-analyst.md`, and
`.claude/skills/session-start/SKILL.md` (both the worktree guidance and the `UV_LINK_MODE`
trap) all assert the project is under OneDrive.

> **Project memory is on this list too, and it is the easy one to miss.**
> `memory/env-onedrive-uv.md:11` says "The project lives under `C:\Users\charl\OneDrive\...`"
> verbatim, and `MEMORY.md`'s index line points at it. **Task 8 renames the memory
> *directory*, which makes it feel handled — its *contents* are a separate gap.** That file is
> also where `UV_LINK_MODE=copy` is justified, so it is the document the test above actually
> settles. Found by the doc audit, 2026-07-27; it was absent from this list, which is a defect
> of omission and the class no grep finds.

> **Test `UV_LINK_MODE=copy` before removing it from anywhere.** It exists because OneDrive
> breaks hardlinks; that reason is gone, but "the reason is gone" is an inference and this
> project does not remove a working guard on one. Run `uv sync` without it, confirm, then
> edit. If it turns out still to be needed, that is a finding worth recording.

*Verify:* `bash scripts/docs-lint.sh` passes; no `grep -ri onedrive` hit in `CLAUDE.md`,
`.claude/`, or any README describes present-tense reality wrongly.

## 4. Accepted, not fixed

**`MIG-9` — the 26 frozen `builder/analysis/` scripts will stop resolving.** Owner's
decision, 2026-07-27: leave them broken and record it.

> **The count was 16 in the first version of this plan and 16 is wrong.** Recorded because the
> error is more instructive than the figure. The original grep used a regex alternation across
> both slash styles; the backslash branch silently matched **nothing**, so the number returned
> was the forward-slash form alone and looked entirely plausible. The doc audit caught that it
> was wrong — and proposed 27, which is also wrong.
>
> **Count each variant separately with `grep -F`, which has no escaping to get wrong:**
> 16 forward-slash + 10 backslash, **no overlap, 26 total**, across seven directories.
> This is the project's own standing rule about instruments — a green result from one that has
> never been shown to go red is not evidence — applied to a one-line grep, which is exactly
> where it is easiest to skip.

The tension is real and is recorded here so nobody rediscovers it as a defect: `CLAUDE.md`
keeps read-only aliases in *shipped* code specifically so these scripts keep executing. After
this move they will not execute regardless of the aliases. **The aliases' stated justification
is therefore weakened by this plan** — they are already marked "deferred for removal, not
permanent", and this is evidence toward that condition, not an argument to remove them now.

The scripts remain accurate records of what was executed, which is their primary value.
Anything needing to re-run one fixes that one script at that time.

## 5. What this plan deliberately does not do

- **It does not touch the app, the graph, the routing, or any config default.** Nothing a
  user could see changes. No test-queue entry is owed.
- **It does not consolidate or delete any of the 18 graph artifacts.** They are not
  interchangeable and several are not rebuildable; culling them is a separate decision with
  its own evidence requirement.
- **It does not change the S3 archive support** (`--s3-bucket`/`--s3-prefix`). It remains
  available and unused; Backblaze is the chosen backup.
- **It does not move `~/.claude/`**, which is already outside OneDrive.
