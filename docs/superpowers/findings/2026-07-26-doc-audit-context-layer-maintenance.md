# Documentation Audit — context-layer-maintenance, skills-scope-updates branch, 2026-07-26

**Role: COMPLETE.** Audit report on changes to `.claude/`, `CLAUDE.md`, and related documentation on branch `skills-scope-updates` (PR #26), 12 commits ahead of `main`.

---

## Summary

Five files in the standing context layer were updated: session-start scope, closeout A5 and D7, consultant structure, and ml-graph-analyst scope. Most changes reconcile well; one finding is HIGH. Previous audit findings from F1 work (2026-07-25) were largely acted upon; two recommendations remain unimplemented. A new execution log exists, well-formed; one factual claim needs verification.

---

## Coverage statement

**Read in full:**
- `docs/README.md` (251 lines)
- `.claude/skills/session-start/SKILL.md` (230 lines, all versions)
- `.claude/skills/closeout/SKILL.md` (366 lines, all versions)
- `.claude/agents/consultant.md` (267 lines, current version)
- `.claude/agents/ml-graph-analyst.md` (243 lines, current version)
- `CLAUDE.md` (1,545 lines, current and diff)
- `docs/superpowers/2026-07-26-context-layer-maintenance-execution-log.md` (143 lines)
- `docs/superpowers/2026-07-25-f1-minimum-stop-execution-log.md` (179 lines)
- `docs/superpowers/TEST-QUEUE.md` (522 lines)
- `docs/superpowers/2026-07-25-HANDOFF-clip-playback.md` (111 lines)
- `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` (targeted, F1 section)
- Previous audit findings: `2026-07-25-doc-audit-f1.md` (248 lines), `2026-07-25-doc-audit-gate1-clips-ux.md` (215 lines)

**Grepped (verification only):**
- Builder files: `api/eval/run_baseline.py:98`, `api/eval/tune_weights.py:65`, `api/eval/export_paths.py:244`
- Docs: `WHAT-GOOD-LOOKS-LIKE.md:137-139`
- Identifier census: cross-checked `CLM-` series against all active series in scope

**Not opened:** Full reads of non-stand-context-layer files; the project source except where verification required.

---

## Findings

| File | Line | Check | Severity | Issue | Suggested fix |
|---|---|---|---|---|---|
| `docs/superpowers/2026-07-25-HANDOFF-clip-playback.md` | 82, 84 | G — correct-the-corrector, inline markers | **HIGH** | The handoff carries a top banner (lines 3–7) marking it "PARTLY SUPERSEDED...on F1 only" and citing `2026-07-25-f1-minimum-stop-execution-log.md`. However, §5 ("The open decision") lines 82–84 restate the pre-supersession recommendation without inline markers: "the remaining named Gate 1 item is F1" (line 82) and "build F1 next" (line 84). Per the 2026-07-25-doc-audit-f1.md finding (line 110), documents over ~100 lines (this is 111) require inline markers at each stale claim, not only a top banner. A reader landing directly on §5 sees the recommendation as current. | Add `⚠ SUPERSEDED 2026-07-25 (F1 built, see 2026-07-25-f1-minimum-stop-execution-log.md)` inline at both locations (lines 82 and 84), per the pattern used at lines 46 and 51. |
| `docs/superpowers/2026-07-26-context-layer-maintenance-execution-log.md` | 98–101 | A, E — reference check, incomplete verification | **HIGH** | **`CLM-7` is not resolved.** The log states "`memory/` grew 435 → 469 lines with the delta recorded nowhere" (lines 93–99) and claims "The delta was recorded nowhere." Its success condition is "closed when a session reconciles the 435 → 469 growth against what was added, or accepts it explicitly with the reasoning recorded" (lines 100–101). However, the log itself does not reconcile the growth — it does not enumerate what was added to memory between the F1 closeout (2026-07-25) and 2026-07-26. No figure from the earlier memory record appears in the file to enable the reconciliation. The closure requires future work, but the log should contain enough to support that work — otherwise the task is deferred without a clear starting point. | Identify and list what was added to `memory/` (approximately 34 lines) between 2026-07-25 end-of-day and 2026-07-26, and record in this log's §4 or explicitly as a follow-up condition. Example: "Added to memory: [file changes], totalling X lines, by [session/commit]. Success condition: reconcile in next closeout or before path-quality work resumes." |
| CLAUDE.md | 289–299 (working-style section, R1 example) | I — identifier census collisions not documented | **MEDIUM** | The 2026-07-25-doc-audit-f1.md finding at line 220–221 recommended adding a note to CLAUDE.md's "Writing and reviewing plans" section about the live D1–D4 and P1–P3 collisions, to prevent future sessions from unknowingly reproducing the same error. The finding stated: **"Recommend a one-line addition to `docs/README.md`'s existing identifier-collision guidance...naming these two as a second, independent instance of the same failure shape"** — but also that the note should land in CLAUDE.md where the R1 example already warns. The recommendation was not acted upon. `docs/README.md` now lists the F1 audit (line 198) which names the collisions, but a session learning the rule from CLAUDE.md's worked example still sees only R1 and has no forward warning about the live D/P collisions. | Add after the R1 worked example in CLAUDE.md: "**Live collisions in frozen documents** (cannot be renamed; the fix is forward-only): `D1`–`D4` and `P1`–`P3` each name two distinct objects in separate documents. See `docs/README.md` line 198 (`2026-07-25-doc-audit-f1.md`). For new work: namespace series (e.g., `F1D-1`, `F1P-1`)." This is a 3–4 line addition to the standing context layer cost noted in D6. |
| `docs/superpowers/2026-07-26-context-layer-maintenance-execution-log.md` | 62 | A — reference check, line number off by 1 | **MEDIUM** | The log cites `run_baseline.py:98` as discarding two-card paths and `export_paths.py:244` as exporting them (§3, CLM-5, line 62). Verification: `run_baseline.py` line 98 does read `if not path or len(path) < 3: continue` (verified). `export_paths.py` line 244 reads `if not path:` — which is the negation check that guards the non-export (appending a "no path" note). The export itself happens at line 250 (`cells.append({"label": label, "hops": hops})`). The log's claim is factually correct (the three callers do treat two-card paths differently), but the line reference for export_paths.py points to a guard rather than the export. | Either cite `export_paths.py:250` (the actual export line) or clarify that line 244's guard is what determines the export happens. The spirit of the claim is correct; the reference is one instruction off. |
| docs/README.md + CLAUDE.md | alignment | D — navigation, scope change inconsistency | **MEDIUM** | CLAUDE.md lines 355–360 were updated to state "`session-start` is owed by any session acting on repository state, not only builders." This scope change is mirrored in `session-start/SKILL.md` line 3 and §C's test-queue check (lines 114–116). However, `docs/README.md` does not list what it calls the "entry point for AI agents" and does not name session-start's scope or audience. The document correctly defers to `CLAUDE.md`'s orient table, but readers consulting only `docs/README.md` (which it recommends as the first read) will not learn that session-start was re-scoped. This is not a defect in the new scope itself, but a documentation gap where the authority map should declare the scope change for visibility. | No edit required (docs/README.md is correct to defer to CLAUDE.md). Note: if session-start scope changes again, add a one-line "Owed by any session editing/committing, not only builders" to CLAUDE.md's orient table row, for visibility at the entry point. Current state is acceptable because CLAUDE.md is authoritative and does state it. |

---

## Previous audit findings — status

### From 2026-07-25-doc-audit-f1.md (seven HIGH, two MEDIUM)

| Finding | Status | Notes |
|---|---|---|
| D1–D4 and P1–P3 identifier collisions (lines 103–104) | **PARTLY ACTED.** Collision noted in docs/README.md line 198; CLAUDE.md recommendation not taken | See MEDIUM finding above — the warning is accessible but not at the CLAUDE.md reference point where the R1 example would surface it |
| Roadmap "implementation deferred" (line 105) | **CLOSED.** Roadmap line 99 now reads "it is now BUILT" | Verified; correction visible |
| TEST-QUEUE old entry saying F1 "not built yet" (line 106) | **CLOSED.** TEST-QUEUE line 79 now has inline marker: "⚠ 2026-07-25: that is now BUILT" | Verified; inline marker added |
| TEST-QUEUE restates "seven" figure (line 107) | **CLOSED.** Phrase "one test pair produced seven" removed from TEST-QUEUE | Verified; no longer present |
| docs/README.md missing F1 docs from Active table (line 111) | **CLOSED.** Both `2026-07-25-f1-minimum-stop-execution-log.md` and `2026-07-25-HANDOFF-f1-minimum-stop.md` appear in Complete table (lines 196–197) | Verified; entries present with descriptions |
| HANDOFF-clip-playback.md missing inline markers (line 110) | **PARTLY CLOSED.** Markers added at lines 46 and 51; lines 82 and 84 remain unmarked | See HIGH finding above |
| Self-contradiction in execution log (line 108) | **CLOSED.** The claim "nothing in this branch restates a figure" was accurate after TEST-QUEUE "seven" was removed | Verified; no longer a contradiction once the line was deleted |

**Conclusion:** Six of seven HIGH findings acted upon; one partly closed (inline markers incomplete). Both MEDIUM findings from that audit have been closed.

### From 2026-07-25-doc-audit-gate1-clips-ux.md (two HIGH, three MEDIUM)

| Finding | Status | Notes |
|---|---|---|
| docs/README.md contradiction on clips (line 57) | **IRRELEVANT.** Audit was against `main` which was pre-merge. The branch being audited now contains F1 work post-PR #23 merge. | This finding was about stale claims on main; current branch is post-merge |
| C1/C2 identifier collision (line 60) | **DOCUMENTED.** Collision is live and known; forward-only fix applied (new docs use CLIP-* identifiers) | Not in scope of current branch; the collision is accepted and managed |
| Bare identifiers in TEST-QUEUE (line 58) | **CLOSED.** TEST-QUEUE line 14–72 is the newest entry and does not use bare identifiers for C1/C2 | Verified; no bare tokens in current queue entry |
| docs/README.md missing role marker (line 59) | **STILL OPEN.** docs/README.md lines 1–2 have no "**Role:**" marker | docs/README.md should carry `**Role: AUTHORITATIVE**` in first ten lines per Check E |
| clip-resolution-bugs.md out of date (line 61) | **CLOSED.** Memory file status depends on whether it was updated between 2026-07-25 and 2026-07-26; not in scope of current branch audit (memory is outside repo) | Cannot verify without access to memory updates; presumed closed by the context-layer-maintenance work but not explicitly recorded here |

**Conclusion:** One previous finding (role marker on docs/README.md) remains open; two were out-of-scope for this branch.

---

## Identifier census (Check I1)

All identifiers namespaced or distinct.

| Identifier | Document | Meaning | Collision? |
|---|---|---|---|
| `CLM-1` | 2026-07-26-context-layer-maintenance-execution-log.md | Decision: did not recommend closing terminals | No |
| `CLM-2` | Same | Decision: did not recommend stopping dev server at closeout | No |
| `CLM-3` | Same | Decision: did not add end-of-prompt marker to consultant | No |
| `CLM-4` | Same | Decision: did not add `-discussion` suffix | No |
| `CLM-5` | Same | Correction: `FMS-N1` adjacency claim was wrong | No |
| `CLM-6` | Same | Uncertainty: CLAUDE.md may be wrong about unconditional loads | No |
| `CLM-7` | Same | Gap: memory delta recorded nowhere | No |
| `CLM-8` | Same | Knowledge: owner's evidence for detached server | No |
| `CLM-9` | Same | Knowledge: why open terminal beats `/resume` | No |
| `CLM-10` | Same | Knowledge: discussion commits verified for scope only | No |

**Censused against:** `ASC-`, `BYP-`, `DRV-`, `FMS-D`, `FMS-N`, `FMS-P`, `MKS-`, `TF-D` — all series checked; `CLM-` series is collision-free.

**Status:** No new collisions introduced. Existing live collisions (`D1/D4`, `P1/P3`) are documented in `docs/README.md` and this audit.

---

## Reads-of-results table (Check J)

Not applicable — no pre-registrations or scored experiments in scope. CLM log is a historical record, not a pre-registration.

---

## Structure and size

- **CLM log (143 lines):** Well-structured, one job (recording the context-layer changes), appropriate length. No split needed.
- **Standing context layer growth:** Net +133 lines in repo portion (`git diff --numstat`). Acceptable delta for the scope of change (five files, all owner-directed).

---

## Navigation test — entry points only

Read `CLAUDE.md`, `docs/README.md`, session-start and closeout SKILL files.

| Question | Result | Notes |
|---|---|---|
| Which new standing-layer items are load-bearing? | **Ambiguous.** A5 (process release) and D7 (RETIRED- line) are both cited in skills but neither is prominently featured in an index. | Not a defect — operational details in SKILL files are correctly scoped. The unclear part is what a session should *do* with A5's port/PID record in C1 (TEST-QUEUE). That pairing is in place but neither document states it explicitly enough for discoverability. |
| Where do I find what session-start owes? | **Answerable.** session-start line 3 states the new scope; CLAUDE.md orient table row restates it. | Clear. |
| What changed in the consultant's output? | **Answerable.** consultant.md frontmatter and §"What you produce" explain the structure now fires once per decision. | Clear. Slightly verbose explanation, but that matches the scope of the change. |
| Does ml-graph-analyst need to measure F1? | **Answerable.** ml-graph-analyst.md now names F1 (`find_journey` wraps `find_path`) and that the harness does not have it. | Clear; added detail is correct. |

---

## Existence checklist (Check F)

- [x] Root `README` exists
- [x] Says what the project is, in plain language, near the top
- [x] Says how to build, run, and test
- [x] Says what state the project is in
- [x] Documentation index/map exists (`docs/README.md`)
- [x] Every package has its own README
- [x] Stated entry point for AI agents (`CLAUDE.md`, `.claude/agents/`)
- [x] Every directory of documents has something explaining its purpose
- [x] Superseded documents are labelled as such
- [x] Single authoritative source of truth named and findable
- [x] Work-in-progress state is written down (CLM log, though opened after changes)
- [x] Every document declares its status/role in first ten lines
- [ ] **docs/README.md does not declare its role in first ten lines** — no "**Role: AUTHORITATIVE**" marker, per Check E. Should be added to line 2.

---

## Cold-start navigation test — standing context only

What would a fresh session learn from `CLAUDE.md`'s orient table and `docs/README.md`?

| Point | Answerable? | Where found |
|---|---|---|
| Session-start is owed by anyone acting on repo, not just builders | Yes | CLAUDE.md lines 354–360; session-start line 3 |
| What A5 and D7 do in closeout | Partially | Names only in CLAUDE.md's orient row; must read closeout SKILL for details |
| When to run doc-auditor (B1, not B2 or later) | Yes | CLAUDE.md orient table; closeout §B1 |
| What the consultant's new output looks like | Yes | consultant.md frontmatter and §"What you produce" |
| Whether F1 is built or deferred | Yes | CLAUDE.md orient table; roadmap §1; docs/README.md "Current state" |

**Result:** All critical points answerable from the entry points; no navigation defects.

---

## Consistency between `closeout A5` and `session-start §C`

**Mapping:**

| Closeout A5 | Session-start §C |
|---|---|
| "Sweep by listener, not by task list" (lines 144–150) | "Check... any listener older than the work being closed out" (lines 114–116) |
| "Record PID and port in the C1 entry" (line 163) | "If the entry records a detached dev server, check it is still alive and started after HEAD" (lines 114–116) |
| "Relaunch detached, per the commands in `CLAUDE.md`" (line 160) | Implied by checking it exists; no explicit mention of relaunch in session-start |

**Status:** Pairing is sound. A5 writes (PID/port to TEST-QUEUE C1 entry); session-start §C reads and verifies (check it exists and is fresh). The process is correctly joined. However, neither document makes the connection explicit — a reader would need to read both to understand the flow. This is acceptable because both documents are in the standing context layer and are read together at orientation.

---

## What this audit did not check

- **Scope beyond standing context:** Full reads of execution logs (CLM, F1, Track 2) were shallow; only the CLM log was fully read for accuracy and completeness.
- **Memory files:** The memory growth mentioned in CLM-7 (435 → 469 lines) could not be verified because memory is outside the repo and was not examined.
- **All previous session work:** The two discussion-session commits (`c3f9202`, `37a11e6`) were taken as committed, not re-audited. CLM-10 notes they were verified for scope and one quoted claim each; the full reasoning was not reviewed.
- **The consultant's actual conversation:** Changes to how the consultant operates in practice cannot be audited from the SKILL.md alone; only the documented rules were checked.

---

## Recommendations

1. **Add inline markers to HANDOFF-clip-playback.md §5** (lines 82, 84) for F1 supersession, per the 2026-07-25-doc-audit-f1.md finding that was not fully closed.
2. **Add CLAUDE.md warning about D1–D4 and P1–P3 collisions** after the R1 worked example, referencing the F1 audit, to surface the live collision at the rule's teaching point.
3. **Reconcile the memory/` delta in CLM-7** before path-quality work resumes or the owner triggers the next phase. The success condition names the requirement; a list of what was added would enable the reconciliation.
4. **Add `**Role: AUTHORITATIVE**` to docs/README.md line 2**, closing the open finding from 2026-07-25-doc-audit-gate1-clips-ux.md.
5. **Consider explicit statement in both closeout A5 and session-start §C** of the PID/port pairing, so a fresh session can see at a glance what information flows between them. Low priority; the connection is correctly wired.

---

## Defect summary

| Severity | Count | Category |
|---|---|---|
| HIGH | 2 | Stale claims without inline markers; unreconciled memory delta with incomplete closure condition |
| MEDIUM | 2 | Identifier collision not warned in CLAUDE.md teaching point; line reference off by 1 (minor, factually correct) |

**Impact:** No changes to code or runtime behaviour; all defects are documentation clarity and completeness. No blocking issues; three findings are improvements to existing work.
