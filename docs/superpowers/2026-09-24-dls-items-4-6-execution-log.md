# `DLS-` items 4–6 — execution log

**Role: RETAINED EXECUTION LOG for plan [`2026-09-24-dls-items-4-6`](plans/2026-09-24-dls-items-4-6.md)** —
decisions and reasoning per task, appended before each task's commit, so any stage can be picked up
cold. Owns no figures beyond the measurements its own tasks take (D6 counts, check outputs).

**D6 measurement, used throughout:** `closeout` D6's inline block, run with the memory directory
`~/.claude/projects/C--dev-music-app/memory` (keyed on the repository, not the worktree, per plan
§2). Unconditional layer in characters (`tr -d '\r' | wc -m`), conditional layer in lines.

---

## Stage `DLP-S1` — issue #230, branch `charlessavage90/dlp-s1-move-the-plan-writing-rules-out-of-claude`

Stage base: `3053e1f` (#229's merge, `origin/main` at session start).

### 1. `DLP-S1.1` — `scripts/prose-survival.py` and its positive control (2026-09-24)

- **D6 baseline, at `3053e1f`:** unconditional **52,001** characters; conditional **2,824** lines.
  (`CLAUDE.md` alone: 580 lines, 40,128 characters with CR stripped.)
- Self-test and script written from the plan's text without change. The self-test ran **before**
  the script existed: `0 passed, 5 failed` (each control failed on the missing file). After the
  script: `self-test: 5 passed, 0 failed.`
- Real tree, where it has to be green before any move exists:
  `python scripts/prose-survival.py --before HEAD:CLAUDE.md --after CLAUDE.md` →
  `302 of 302 sentences survive; 0 missing.` So splitting agrees across the committed (LF from
  `git show`) and working-tree (CRLF) sides; the plan's CRLF worry (§5.2) did not fire here.
- Ruling (pre-flight): `DLP-S1.4` step 3's `HEAD~2` is replaced by the stage base `3053e1f`, as that
  step itself instructs.
- **Snyk (`snyk_code_scan` on `scripts/`):** 2 issues, both **Low**, both `python/PT` (CWE-23, path
  traversal): a command-line path flows into `open()` (lines 37 and 80). **Not fixed — ruling:** the
  path *is* the tool's input, supplied by the person running it with their own file permissions, so
  there is no privilege boundary for a traversal to cross. The only available fix (confining reads
  to the repository) would break the self-test, whose fixtures live in `mktemp -d` outside the tree,
  and buys nothing. `git show` is called with an argument list, never a shell. Cost if wrong: none
  beyond reading a file the invoker could already read.
