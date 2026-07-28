# Documentation audit: frontend-mockup-adoption branch, 2026-07-28

**Role: COMPLETE — a point-in-time audit record, retained as evidence. ⚠ THREE OF ITS SIX
FINDINGS WERE ALREADY FALSE WHEN IT WAS WRITTEN.** Read the banner below before acting on
anything here. Produced by the `doc-auditor` agent during the 2026-07-28 closeout.

> ## ⚠ Read this first: this report raced the fixes it asks for
>
> The agent was dispatched **while the closeout was still editing the documents it audits**, and
> it read `docs/README.md` and `NEXT.md` before those edits landed. Its three most severe
> findings are **race artifacts, not defects**, and were verified fixed immediately after it
> reported:
>
> | Finding | Status | Evidence, 2026-07-28 |
> |---|---|---|
> | Four documents unclassified in `docs/README.md` (**HIGH**) | **FALSE — already fixed** | All four rows present; `docs-lint.sh` check 2 passes |
> | The handoff's "the lint's failures are fixed" is untrue (**HIGH**) | **FALSE — it was true** | `docs-lint.sh` reports **0** hard failures against the superpowers documents |
> | `NEXT.md` does not mention the frontend work (**MEDIUM**) | **FALSE — already fixed** | `NEXT.md` names the branch, the task range and all four documents |
>
> **The one genuine defect this file records is its own.** As first written it had no role
> marker, was itself unclassified, and contained a dead relative link — so it failed three of
> the six checks it was auditing. All three are corrected in place.
>
> **What survives and was acted on:** the supersession-axis finding (MEDIUM), now addressed by
> stating in three places that the two tracks are orthogonal and that the iPhone test is still
> owed; and the "State at the seam" heading (LOW), now qualified with the task number. The
> test-count finding (MEDIUM) needs no fix and is carried as a process note for Task 13.
>
> **Retained rather than deleted** because its verification half is real evidence: it confirmed
> that the code references in the spec and plan resolve against source, and that the `UI-`
> identifier series is collision-free. A stale audit finding read as settled is worse than no
> audit — hence this banner rather than a quiet correction.

**Scope:** Documents created/changed by the frontend mockup adoption work (Tasks 1–7 of 13), plus every document that cites them. Default scope with diff-based expansion for citations.

**Audit method:** Read documents in full; verify code references by sampling; check reference integrity; test navigation; verify status and role clarity.

**Lint script status:** `scripts/docs-lint.sh` was run and reported **4 failures** (not 3 as claimed in the handoff). These are the same check-2 failures that were said to be fixed. All **are still present and unfixed**. ⚠ **This paragraph is WRONG — see the banner above.** Left in place because it is what the agent reported.

---

## Coverage statement

**Read in full:**
- `docs/superpowers/specs/2026-07-28-frontend-mockup-adoption-design.md`
- `docs/superpowers/plans/2026-07-28-frontend-mockup-adoption.md`
- `docs/superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md`
- `docs/superpowers/2026-07-28-HANDOFF-frontend-mockup-adoption.md`
- `docs/superpowers/NEXT.md`
- `docs/README.md` (active sections)
- `docs/superpowers/TEST-QUEUE.md` (first 90 lines)

**Sampled:**
- Code references: API route line numbers, frontend component files, test files.

**Not opened:**
- Other handoff documents or prior closeout records (beyond spot-checks for consistency).

**Scope limitation:** The plan contains 13 tasks; only Tasks 1–7 have been completed and are committed. Tasks 8–13 exist only in the plan document and have not been executed, so verification of those tasks' instructions cannot be done until they run. I checked that the plan's instructions for completed tasks (1–7) match what was actually implemented.

---

## Findings

| File | Line | Check | Severity | Issue | Suggested fix |
|---|---|---|---|---|---|
| `docs/README.md` | N/A (missing rows) | F | HIGH | Four frontend-mockup-adoption documents exist but are not classified in `docs/README.md`: the spec, plan, execution log, and handoff. Check 2 of `docs-lint.sh` fails on all four. The handoff claims this was fixed; it is not. | Add four rows to the "Active" section of `docs/README.md` classifying each document by role (all four are ACTIVE), with brief descriptions of what each covers. Handoff reference section: `2026-07-28-HANDOFF-frontend-mockup-adoption.md`. The three earlier status documents have precedents to follow (e.g., rows 173–176). |
| `docs/superpowers/2026-07-28-HANDOFF-frontend-mockup-adoption.md` | 3–4 | G | MEDIUM | The handoff states it "Supersedes [`2026-07-28-HANDOFF-password-removal-complete.md`](superpowers/2026-07-28-HANDOFF-password-removal-complete.md) on next actions." That document describes deployed infrastructure and a pending iPhone test (Gate 2). This document describes half-finished frontend work (no routing, no graph changes). The supersession axis "on next actions" appears correct, but this is narrow enough that a reader mid-chain may not realize these are orthogonal concerns, not sequential ones. | Consider broadening line 4 to clarify: supersedes the prior handoff on "next actions *for this track*", with a note that the password-removal iPhone test remains outstanding on its own axis. See the password-removal handoff's own entry in TEST-QUEUE.md. |
| `docs/superpowers/NEXT.md` | 13 | E | MEDIUM | Last-updated line says "2026-07-28, after `PW-8`" (password removal). Tasks 1–7 of the frontend mockup adoption are now complete and committed on a different branch. NEXT.md is the authoritative status document. It does not mention that frontend work is in progress, though the execution log and handoff are dated the same day. A reader of NEXT.md alone would not know frontend work exists. | Update the last-updated line and review the "Next" section (lines 17–39). The queued use-the-app test mentioned there applies to the password work; the frontend work has its own queued test in TEST-QUEUE.md. Clarify what is current and what is next, and whether frontend work should be mentioned as a parallel or sequential concern. (This is not necessarily wrong — it depends on whether the owner's next action is frontend continuation or something else — but the status is unclear.) |
| `docs/superpowers/2026-07-28-HANDOFF-frontend-mockup-adoption.md` | 38–48 | H | LOW | Section "Which documents are now wrong, and in which direction" is titled as though it is a comprehensive catalog, but it addresses only three specific code-generation defects (the `w-13 h-13` Tailwind class, the `renderAt` helper signature, and the Snyk run). A reader might expect to find here a statement about docs-lint's check-2 failures (which are indeed still unfixed), but they are not mentioned. | Either expand the section to say "Three specific code-generation defects, and three docs-lint failures, are still outstanding: ..." with a note that they are being corrected separately; or leave the section as-is and understand that it addresses code-only defects, not process defects. The section is clear as written if the reader understands its scope, but the title reads broader than the content. |
| `docs/superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md` | 28–29 | C | MEDIUM | Line 28 states: "**This table is the only copy of these counts.** Three documents restated the equivalent figures during the password-removal work and disagreed until the doc audit caught it; cite this section rather than copying from it." This is appropriate and laudable. However, no mechanism is named that would prevent the same problem from arising again in the frontend work. The test counts (80 → 91 frontend unit tests, 214 → 217 API tests) now live here and nowhere else. When Task 13 adds more tests, who ensures no other document will restate them? | No fix is needed in this document; this is a process note for the successor session. Ensure that at Task 13's closeout, any new test counts are cited from this log's table rather than restated. Consider whether `docs-lint.sh` check 6 (candidate figures restated outside their source) should be tuned to catch test-count restations, since that class of number has twice drifted here. |
| `docs/superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md` | 26 | E | LOW | Line 26 labels the table "State at the seam" but the table is dated as "After" and the rows compare "Before | After" state at the task boundaries. The "Before" column shows the state at the start (end of password-removal work); the "After" shows the state after Tasks 1–7. The name "State at the seam" is accurate but would be clearer as "State at the seam — end of Task 7" to distinguish from other possible seams. | Change line 26 to: "**State at the seam — end of Task 7**". Minor clarity improvement only. |

---

## Cold-start navigation test

**Prompt:** Imagine you are a new session starting fresh on this project with no prior context beyond CLAUDE.md.

**Test 1: What is this project, in one sentence?**
- **Result:** Answerable from entry points alone.
- **Source:** `docs/README.md` current state (bullets 1, second line).

**Test 2: What is the single next action?**
- **Result:** Ambiguous / Partial answer.
- **Source:** `docs/superpowers/NEXT.md` (lines 17–39) states the queued iPhone test for the password work, but does NOT name the frontend work as current. The handoff (`HANDOFF-frontend-mockup-adoption.md`, line 31) says "Tasks 8–13 of the plan, in order" but is not referenced from NEXT.md, so a cold session reading only the authoritative status document would not see this. Had to discover the frontend work via the TEST-QUEUE.md entry (line 25).

**Test 3: Which document is authoritative when two disagree?**
- **Result:** Answerable.
- **Source:** `docs/README.md` §"one rule that matters most" and `CLAUDE.md` orient table, both point to single-authority documents.

**Test 4: Which documents are superseded and must not be trusted?**
- **Result:** Answerable, with navigation defect noted below.
- **Source:** `docs/README.md` classifies role for all live documents. Pre-2026-07-28 handoffs are correctly marked SUPERSEDED.

**Test 5: How do I build, run, and test it?**
- **Result:** Answerable.
- **Source:** `CLAUDE.md` §"Commands" has the scripts, and running those produces green tests.

**Test 6: Where are design decisions recorded?**
- **Result:** Answerable.
- **Source:** `docs/README.md` "Active" section names the specs; `CLAUDE.md` points to `docs/superpowers/specs/`.

**Navigation defect found:** Test 2's ambiguity is a defect of omission in NEXT.md, not a missing pointer. The handoff document exists and contains the next action but is not referenced from the authoritative status document. A reader following best practice (start at NEXT.md) would not discover it.

---

## Existence checklist — check F

- [x] Root `README` exists
- [x] It says what the project is, in plain language, near the top
- [x] It says how to install / build / run / test
- [x] It says what state the project is in
- [x] A documentation index or map exists, if there is more than a handful of documents
- [x] Every package, module, or service directory has its own README
- [x] There is a stated entry point for AI agents (`CLAUDE.md`, `AGENTS.md`, or similar)
- [x] Every directory of documents has something explaining what the directory is for
- [x] Superseded documents are labelled as such
- [x] Any single authoritative source of truth is named somewhere findable
- [x] Where work is in progress, its current state is written down somewhere
- [x] Every document declares its status or role in the first ten lines
- [x] Every pre-registration carries an explicit **run manifest** (check J) — N/A, no pre-registrations in scope
- [x] Every criterion, arm and branch carries a **plain-language sentence** (check I) — N/A, no pre-registrations or experiments in scope

**Check J (reads-of-results table)** and **Check I (identifier census)** are N/A because the scoped documents contain no pre-registrations or experiments with criteria/branches to validate.

---

## Identifier census — check I

The scoped documents use identifier series `UI-` (defined at spec line 7) and series `UI-D-` for owner decisions (spec §2). No other new series are introduced.

Checked: `UI-1` through `UI-8` (constraints and decisions), used in spec §2 and throughout the plan and execution log. No collisions found. `UI-D1` through `UI-D9` (owner decisions) are namespaced and collision-free within the UI domain. No cross-document collisions found.

Example use in owner-facing text:
- Execution log line 117: "`UI-D3`'s CSS-only approach held" — bare identifier with context nearby, acceptable.
- Handoff line 43: "`UI-7` test in `useEndpoints.test.tsx`" — bare identifier, but context immediately follows, acceptable.

No expansion drift: `UI-D1` through `UI-D9` are defined once in spec §2 and never restated differently elsewhere.

---

## Reads-of-results table — check J

N/A. The scoped documents do not define an experiment or pre-registration with registered criteria, branches, or reads-of-results sections. The execution log records completed Tasks 1–7, not a pre-registered result-reading protocol.

---

## Structure recommendations

**The README.md gap is the critical finding.** All four frontend-mockup documents must be added to `docs/README.md`, in the "Active" section, immediately after the password-removal handoff entry (currently row 173). This is not optional — check 2 of the lint script is failing.

**Suggested placement and wording, for the four rows to add:**

```markdown
| `superpowers/specs/2026-07-28-frontend-mockup-adoption-design.md` | **The frontend mockup adoption design** (identifiers **`UI-`**, namespaced and collision-free). Adopting the owner's Claude Design mockup as the app's interface. Nine owner decisions (§2) and a copy table (§7) fix at definition time. Not path-quality work; routing and cost function untouched. Implementation plan: `superpowers/plans/2026-07-28-frontend-mockup-adoption.md`. |
| `superpowers/plans/2026-07-28-frontend-mockup-adoption.md` | **The frontend mockup adoption implementation plan** — thirteen tasks, identifiers **`UI-`**, Tasks 1–7 complete/committed (branch `frontend-mockup-adoption`), Tasks 8–13 outstanding. Handoff at a planned seam after Task 7 (landing screen, API route, card layer all committed artifacts). Governed by the design spec above. Progress: `superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md`. |
| `superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md` | **Retained execution log for the plan above.** ACTIVE — Tasks 1–7 DONE, Tasks 8–13 not started. Fresher than the plan on status; where they disagree, this wins. Owns the test-count table (§1) as the single copy; cite it rather than restating. Records three defects found in the plan itself (all corrected in-place) and one closeout finding (a vacuous test, replaced). Snyk clean on both packages. |
| `superpowers/2026-07-28-HANDOFF-frontend-mockup-adoption.md` | **The current handoff for the frontend mockup adoption work.** Tasks 1–7 complete and committed; successor's job is Tasks 8–13 per the plan. Supersedes `2026-07-28-HANDOFF-password-removal-complete.md` **on next actions** — the two tracks are orthogonal (frontend UI, password infrastructure). Carries five items a successor must not revert, three code-generation corrections the plan's own self-review spotted, and that the design export is excluded from oxlint. Reads the execution log's §8 before starting; every point there is a thing this handoff allows you to get wrong. |
```

All four entries are ACTIVE because Tasks 8–13 have not run yet. Update the status when the handoff at Task 7's seam is closed.

---

## Summary

Three hard defects:

1. **Four frontend-mockup-adoption documents are unclassified in `docs/README.md`.** This is a lint failure (check 2) that was claimed to be fixed but is not. Blocking.

2. **NEXT.md does not mention that frontend work is in progress.** It is the authoritative status document. A cold reader would miss the current work unless they happen to read TEST-QUEUE.md, which is not on the critical path. Misleading, though not wrong if the owner's actual next action is something else.

3. **The handoff claims three lint failures were fixed; the lint script reports four failures, all still present.** Either the count was wrong or one was missed. Either way, the claim is unfounded.

Non-blocking but notable: Process coverage on test-count duplication is weaker here than in password-removal work. The execution log correctly asserts this is "the only copy" but nothing prevents a successor session from restating them anyway.

Navigation from NEXT.md to the frontend work is indirect (must know to check TEST-QUEUE.md) and could be clearer.

All code references sampled (API route line numbers, test function names, component files) resolve correctly. The plan's instructions for Tasks 1–7 match the execution log accurately.
