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

### 2. `DLP-S1.2` — the two harness-enforced passages removed (`DLP-Q5`, owner 2026-09-24)

Commit `afe502e`, **made by the owner by hand**: the auto-mode classifier refused both the
session's commit of `.claude/settings.json` and a skill file as self-modification, including after
the owner's in-session approval.

- Allowlist widened: `Bash(uv run --extra dev pytest *)` and `Bash(uv run python -m pytest *)`
  added; the prefixed forms kept.
- `CLAUDE.md`: never-use paragraph reduced to the journal half, in the plan's words; the
  `UV_LINK_MODE` instruction, its example and the "Hardlinking" paragraph deleted; the prefix dropped
  from the four `uv run` command lines. `session-start` §D: the `UV_LINK_MODE` bullet deleted.
- **Ruling:** §D's lead-in "Only the first is in `CLAUDE.md`; the other two live in" became "They
  live in". With the first bullet gone it would have named `PYTHONIOENCODING` as the trap in
  `CLAUDE.md`, which is false. The removed clause is in the allow-file. Cost if wrong: one clause.
- **Ruling, not touched:** `.claude/agents/ml-graph-analyst.md` and `closeout` still write the
  prefix in their commands. `DLP-Q5` covered the `CLAUDE.md` passage, and the prefixed forms stay
  on the allowlist, so those commands still run unprompted. Cost if wrong: redundant text in two
  conditional bodies.
- Survival with `scripts/prose-survival-allow/dlp-s1.txt`: `CLAUDE.md` **302 of 302, 0 missing**;
  `session-start` **216 of 216, 0 missing**. Without the allow-file, 8 and 3 missing, every one a
  ruled removal.
- Bare `uv run --extra dev pytest -q -k nothing_matches` in `builder/`: ran, `292 deselected`,
  no prompt. **Caveat:** this session runs in auto mode, which could have allowed it regardless. The
  no-prompt check is proven for auto mode only; for default mode it rests on the rule's text.
- D6 after: unconditional **51,564** characters (**−437**); conditional **2,822** lines (**−2**).

### 3. `DLP-S1.3` — the plan-writing rules moved to the `plan-discipline` skill

- Split exactly as the plan fixes it. **Moved, in order:** from "Five review rounds…" through
  "…a plan that was under-recorded.", then "How to ask for a plan review". **Stays**, under the new
  heading `### Long sessions degrade — the tell`: "The degradation tell…" through "…twice been the
  owner who spotted it." The pointer paragraph and the skill's frontmatter are the plan's text,
  copied from the plan file rather than retyped.
- Survival: `--before HEAD:CLAUDE.md --after CLAUDE.md --after …/plan-discipline/SKILL.md` →
  **298 of 298, 0 missing**. Retained half still **visible**: its 9 sentences against `CLAUDE.md`
  with `--strip-comments` → **9 of 9**. Control, so that green means something: the same 9 against
  the skill alone → **0 of 9**, so the check could have gone red.
- Active references (`git grep "Writing and reviewing plans here"`): one, this plan's own header
  line, now names the skill. The rest are execution logs, a findings table (the spec, which records
  a measurement of the section) and completed plans, so frozen or historically true. A wider grep for
  "`CLAUDE.md` + factor table / seams / grep every function" found only dated logs, handoffs, plans
  and specs, and no skill or agent.
- D6 after: unconditional **44,550** characters (**−7,014**); conditional **2,953** lines
  (**+131**). The new description is 360 characters of the unconditional figure. `CLAUDE.md` now 459
  lines, 32,317 characters.

### 4. `DLP-S1.4` — the `DLS-Q4` amendment

- `CLAUDE.md`'s "Rules here do not expire…" paragraph replaced by the plan's "Rules here move; they
  are not reworded…" text, copied from the plan file. `closeout` D6 gains the plan's one sentence as
  its own paragraph, after "…damage with a receipt." (the paragraph with D6's first "compress").
  Nothing in D6 removed.
- The five replaced sentences are exactly what survival reported missing, and nothing else. They
  are appended to `scripts/prose-survival-allow/dlp-s1.txt` under
  `# DLS-Q4, owner ruling 2026-09-11: replaced, not moved`.
- **Cumulative stage check**, against the stage base `3053e1f` (ruled in pre-flight in place of the
  plan's `HEAD~2`): `CLAUDE.md` → `CLAUDE.md` + `plan-discipline` with the allow-file: **302 of 302,
  0 missing**. `session-start`, same base and allow-file: **216 of 216**. `closeout`, an addition
  only, against its own `HEAD` with no allow-file: **515 of 515**.
- D6 after: unconditional **44,498** characters (**−52**); conditional **2,955** lines (**+2**).

### 5. `DLP-S1.5` — close the stage

- `bash scripts/docs-lint.sh --quiet` → `docs-lint: hard checks passed.` (before this log had its
  map row: 1 hard failure, "not classified in docs/README.md", which the row fixed). No candidate
  names a file this stage touched.
- `bash scripts/docs-lint-selftest.sh` → `self-test: 7 passed, 0 failed.`
- `bash scripts/prose-survival-selftest.sh` → `self-test: 5 passed, 0 failed.`
- `docs/README.md`: a hand row for this log (until `DLP-S2` generates the map), and the plan's row
  and its own role line now say `DLP-S1` is executed. Both add to `docs/README.md`'s line count, which
  #145 already tracks as over budget.
- **Stage D6, base `3053e1f` → end:** unconditional **52,001 → 44,498** characters (**−7,503**);
  conditional **2,824 → 2,955** lines (**+131**). The conditional growth is the moved section
  (now paid only by sessions that invoke `plan-discipline`), plus D6's added sentence.
- **`DLP-G1` start condition:** the observation window opens at **PR #231's merge commit** (`M1`).
  Exposure is by branch ancestry from `M1`, not by date (plan §1). No edit to the skill's name,
  description or body, or to the `CLAUDE.md` pointer, until the gate is read. Any such edit restarts it.

### 6. Final review and closeout B1

- **Whole-branch review** (fresh reviewer, read-only): no Critical, no Important. Its own checks were
  a `diff` of the moved block against the skill body (identical but for the H3→H1 heading and edge
  blank lines) and survival without the allow-file (13 missing, exactly the 8 `DLP-Q5` and 5 `DLS-Q4`
  sentences). **Minor 1, fixed:** `ISSUES.md` cited `CLAUDE.md` for the pre-registration rule. A
  follow-up sweep found two more live pointers of the same kind, both fixed as well: `ISSUES.md`'s
  namespacing/collision check, and `docs/README.md`'s row for the Track 2 pre-registration. The
  `doc-auditor` (B1) reported no defects and **missed all three**, which is worth knowing about its
  coverage of pointers phrased as "(`CLAUDE.md`)". **Minor 3:** frozen specs and a handoff still say
  "`CLAUDE.md` requires"; they are historically true, so no action.
- **Minor 2, carried to `DLP-S3` as a condition:** `prose-survival --allow` applies every entry to
  every `--before` file, not only the file it was written for. Harmless here, because every entry is
  file-specific in practice and the reviewer checked none is unused. **`DLP-S3` must either use one
  allow-file per `--before` file or key entries by file before it runs a multi-file allow-list.**
  Success condition: `DLP-S3.3`'s survival run uses per-file allow-lists.

### 7. Owner follow-up — the prefix dropped from `ml-graph-analyst` and `closeout` too

The owner reversed the §2 "not touched" ruling in-session: *"fix the ml-graph-analyst agent's and
closeout's commands"*. The agent's bold "Prefix every `uv` command…" sentence is removed (its location
and `.venv` sentences stay), and the prefix is dropped from its two commands and from `closeout` D4's
two. The three removed units are in the allow-file under their own header. Survival against each file's
own `HEAD`: agent **113/113**, `closeout` **516/516**. No `UV_LINK_MODE` remains under `.claude/`
except `settings.json`'s `env` and the kept prefixed allow rules. Agent and skill bodies only, and no
description changed, so the unconditional layer is unchanged (conditional −3 lines).

---

## Stage `DLP-S2` — issue #260, branch `charlessavage90/docs-layer`

Stage base: `28c9da7` (#251's merge, `origin/main` at session start). **The issue was opened by this
session on 2026-09-28**: plan §1 says each stage's issue opens when its predecessor merges, and
`DLP-S2`'s never was after PR #231. A second session was live in its own worktree throughout
(`DRP-stage-3c`, PR #259); it touches `docs/README.md` and `NEXT.md` only at its closeout.

### 1. `DLP-S2.1` — the retrofit measured before building anything (2026-09-28)

The plan's generator (Task `DLP-S2.3` step 3) was extracted verbatim and its classifier run dry over
`docs/**/*.md`, skipping `README.md` and `reference/`. Scripts are throwaway, in the session scratchpad.

| step | what | at plan time | measured |
|---|---|---|---|
| 1 | documents with no classifiable role line | 22 | **23** |
| 2b | superseded documents whose bold role line names no replacement | 25 of 62 | **26** |
| 2 | `⚠` segments of map rows that do not survive into their own document | — | **219 of 219** (plan's segment: `⚠` to the next `⚠` or cell end), **211 of 219 across 144 documents** (the warning sentence alone) |

- **Why two figures for step 2.** The plan's segment runs to the end of the cell, so it carries the
  row's summary along with the warning and fails whenever the summary is not verbatim in the
  document — which is almost always, since that is #152's complaint. All 219 failing looked like an
  instrument fault, so it was re-run on the warning sentence only (to the closing `**` when the
  warning opens bold, else its first sentence) and one case checked by hand: `findings/2026-09-13-
  lbl-listen2-results.md`'s "Endpoint familiarity was NEVER confirmed" warning is in the map row and
  nowhere in the document. The tighter figure is the real work; the gate fires on either.
- **Gate `DLP-G2` FIRES** (*does the retrofit fit in one session?* fires above 120 judged edits):
  23 + 26 + 211 = **260**. **Ruling, per the step's own text:** `DLP-S2.4` splits at a seam. **This
  PR:** `S2.1`–`S2.3` and `S2.4` step 2 (role lines and banners). **The next PR:** `S2.4` step 1 (archive
  the old map), step 3 (the warnings), steps 4–7 (migrate) and `S2.5`. **Step 1 moves to the second PR**
  so the archive copy is taken at the moment the map is replaced, and **the map is not regenerated
  in this PR**, because regenerating before the warnings move would drop 211 of them from view.
- **Ruling — the generator accepts `**⚠ Role:`.** 8 of the 23 open with `**⚠ Role: …`, the house
  pattern for a warned role line, and the plan's code matches only `**Role:`. That is a gap in the
  tool, not in the documents, so the generator's pattern is widened to an optional `⚠` and the 8 need
  no edit. **15 remain**: 5 open with `**Status:**` (not a role line, and not accepted as one: its
  text often carries no role word) and 10 have neither.
- **Ruling — 36 map rows point outside `docs/`** (`../CLAUDE.md`, `../frontend/design/…`, and
  `../builder/analysis/…` folders and READMEs); plus the `reference/` entry. The generator scans
  `docs/` only, so migrating as written would drop them. They move **verbatim** to a hand-written
  section above the markers in the second PR. Step 4's list of hand-written sections is extended by
  that one; nothing else about the migration changes.
- **Step 1's list and step 2b's list** are those printed by the dry run; the second PR re-measures
  rather than copying them, since documents land daily.

### 2. `DLP-S2.2` — frozen-document banners and lint check 8

- Control 8 written from the plan's text without change and run **before** the check existed:
  `8 passed, 1 failed` — "a banner over an untouched body passes" green, "check 8 did NOT fire (rc=0)"
  red. After check 8 (plan text, unchanged): `self-test: 9 passed, 0 failed.` Real tree:
  `docs-lint: hard checks passed` (no banner exists yet, so check 8 has nothing to compare).
- Banner format documented in `docs/README.md` §"Adding a document", appended; the section's
  existing "add it to the table above" sentence is left for the migration PR, where it goes stale.
- **Deferred to `S2.5`, which edits the same header:** `docs-lint.sh`'s header says "Checks 4-6 emit
  CANDIDATES"; it becomes "4-6 and 9" when check 9 lands.

### 3. `DLP-S2.3` — `scripts/gen-docs-map.py` and lint check 7

- Controls 7 and 7b written from the plan's text and run **before** the generator existed: both red
  (`check 7 did NOT fire (rc=1)`, `replacement check did NOT fire (rc=2)`).
- **Added control 7c** (a `**⚠ Role:` line must be classified, and its row must keep the `⚠`). With the
  plan's generator installed **verbatim**, 7 and 7b behaved and **7c went red**
  (`no classifiable **Role:** line … warned.md`), which is the `DLP-S2.1` ruling's gap reproduced in a
  fixture. The generator was then widened, the one change from the plan's text: a module-level
  `ROLE = re.compile(r'\*\*(?:⚠\s*)?Role:')` used in `role_paragraph`, `bold_span` and `classify`,
  with a docstring paragraph saying why. Check 7 added from the plan's text, unchanged.
- **Result:** `self-test: 13 passed, 0 failed.` Real tree: `docs-lint: hard checks passed`; check 7
  reports `skipped (no generated block yet)`, check 8 `ok`.
- **Snyk (`snyk_code_scan` on `gen-docs-map.py`):** 1 issue, **Low**, `python/PT` (CWE-23): `--root`
  flows into path concatenation. **Not fixed — the same ruling as `DLP-S1.1`'s for
  `prose-survival.py`, for the same reason:** the root *is* the tool's input, given by the person
  running it with their own permissions, and confining it to the repository would break controls 7,
  7b and 7c, whose fixtures live in `mktemp -d` outside the tree.
- **The generator's own list on the real tree, after the widening** (this is `S2.4` step 2's input):
  **15** with no classifiable role line and **27** superseded without a named replacement (the dry
  run's 26 plus `2026-07-30-HANDOFF-track-b-runs.md`, which the widening newly classified).

### 4. `DLP-S2.4` step 2 — role lines and banners for the 42 (the seam's last task)

Applied by one throwaway script from an explicit table (one row per document, wording taken from its
current `docs/README.md` row, every named replacement checked to exist; the script refuses a dirty
file). Diff: **42 files, +83 −1**, exactly 39 two-line banners, two inserted role lines and one
in-place edit.

- **39 banners** in the `DLP-S2.2` format, each `frozen-below` the SHA of the file's last commit:
  - the **27** superseded handoffs, each naming its replacement as a link in its own folder, from its
    map row. Two needed more than the row: `2026-07-27-HANDOFF-onedrive-migration.md`'s row says "the
    handoff above", resolved from its own role paragraph to `2026-07-27-HANDOFF-migration-phase-d.md`;
    `2026-09-12-HANDOFF-lbl-listen2-prep.md`'s row names only a results note, and
    `2026-09-13-HANDOFF-lbl-listen2-read.md` says it supersedes the prep note on next actions, so
    that is named rather than `NEXT.md` (the plan's default applies only when no successor handoff
    exists);
  - **12** of the 15 unplaced documents, the frozen ones by their map row: five superseded handoffs,
    two HISTORICAL findings (the map's "Partly historical" section; the row's "Superseded for …"
    kept in sentence case, so it is not the all-caps `SUPERSEDED` that demands a replacement — they
    are superseded in part, not replaced), and five COMPLETE/EXECUTED plans, specs and records.
- **Two EXECUTED plans the map files under Active** (`plans/2026-07-26-track-a-…`, `plans/2026-07-26-
  track-d-frontend.md`): their rows themselves say "EXECUTED 2026-07-26; do not execute again", so the
  banner says EXECUTED and they will generate under Complete. A section change for the migration
  PR's step-5 table, where the map was wrong.
- **3 role lines into active documents**: the scoring adjudication (**AUTHORITATIVE**, from its row),
  the configuration-model null (**AUTHORITATIVE for its own figures**), and the `WGT-` execution log,
  whose existing bold `RETAINED EXECUTION LOG.` span gained the `Role:` prefix and nothing else.
- **Verified:** `gen-docs-map.py --check` now classifies every document and names none as missing a
  replacement (it stops at the absent markers, exit 2, which is this PR's intended state).
  `docs-lint.sh --quiet`: hard checks passed, check 8 over all 39 banners. Check 8 was also shown
  red on a real CRLF file (one byte appended below the reciprocity handoff's banner) and green once
  restored — the fixtures are LF, so this was the one case the self-test could not cover.

**Seam.** This PR ends here. The second PR starts from `S2.4` step 1 (archive the map) and runs step
3 (the 211 warnings; re-measure first), steps 4–7 and `S2.5`, carrying the two rulings in §1 (the 36
outside-`docs/` rows move verbatim to a hand section; `S2.5` updates the lint header's "Checks 4-6").

### 5. Closeout (maintenance tier) for part 1

- **D6**, memory directory `~/.claude/projects/C--dev-music-app/memory`: unconditional **46,650**
  characters, conditional **3,538** lines. **Delta 0 in both**: neither this PR nor the same session's
  #262 touches `CLAUDE.md`, `.claude/` or memory (`git diff --name-only origin/main...` over those
  paths is empty for both branches). These totals are not comparable to §1's `DLP-S1` baseline:
  other PRs have landed in between.
- **B1:** `docs-lint.sh` hard checks pass on both branches. `doc-auditor`, scoped to both diffs:
  **no defects**. It sampled 6 of the 39 banners in full (replacement confirmed from the successor's
  side in 3 cases) and relied on check 8 for the rest's bodies.
- **B1-mt:** nothing under `.claude/` changed. The frozen documents touched are the 39 banners, the
  one edit `DLS-Q1` permits and check 8 guards; and `NEXT-ARCHIVE.md` in #262, where a block was
  inserted by the `A2-next` procedure and `prose-survival` shows its 1,887 existing sentences
  unchanged. No identifier series was minted.
- **A3:** #260 released (`claimed` off) at this seam; part 2 is dispatchable only after this PR
  merges. #145 and #152 stay open, with progress comments on #145 and #260. **A5:** no process
  started, none listening. **C1:** nothing the owner can press, so no `TEST-QUEUE.md` entry.
