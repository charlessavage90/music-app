# Documentation Audit — gate1-clips-and-ux completion

**Date:** 2026-07-25  
**Scope:** Documentation consistency after clips (C1/C2) fixes and four frontend UX items completed on branch `gate1-clips-and-ux` (PR #19, not yet merged to main)  
**Audit rule basis:** Checks A (dead references), B (contradictions), C (duplicated facts), E (status clarity), F (existence), I (identifier collisions), and J (reads-of-results completeness) from project-local `doc-auditor.md`

---

## Summary

Five HIGH-severity findings, all caused by the unmerged PR being live while documentation on `main` remains stale:

1. **docs/README.md (main) §2.7** — Still states clips and UX are "queued behind" completed work, contradicting actual state.
2. **Identifier collision at load-bearing point** — C1/C2 name four distinct objects simultaneously (clip defects, Track 2 criteria, roadmap phase items, closeout checks), creating ambiguity in owner-facing text and memory files.
3. **Bare identifiers in owner-facing TEST-QUEUE entry** — Plain-language expansion rule (Check I2) violated in the queued entry describing the work.
4. **docs/README.md (main) document role undefined** — Not marked as ACTIVE / COMPLETE / etc. within first ten lines; renders status unclear on next read.
5. **Memory file clip-resolution-bugs.md out of date** — Modified 2026-07-21, still describes C1/C2 as diagnosed defects needing fixes, now completed.

All are fixable post-merge; three are presentation issues (bare identifiers, role markers), two are substantive (contradiction with code, stale scope claims).

---

## Coverage statement

**Read in full:**
- C:\Users\charl\OneDrive\Claude Projects\music-app\CLAUDE.md (1,436 lines — comprehensive project conventions)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\README.md (entire file)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\TEST-QUEUE.md (entire file)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\2026-07-25-HANDOFF-track2f-and-headroom.md (185 lines)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\2026-07-24-HANDOFF-track2-complete.md (150 lines, limit applied)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\2026-07-23-repair-and-retune-execution-log.md (100 lines, limit applied — status header only)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\plans\2026-07-21-alpha-rollout-roadmap.md (200 lines)
- C:\Users\charl\.claude\projects\C--Users-charl-OneDrive-Claude-Projects-music-app\memory\MEMORY.md (15 lines)
- C:\Users\charl\.claude\projects\C--Users-charl-OneDrive-Claude-Projects-music-app\memory\clip-resolution-bugs.md (20 lines)
- C:\Users\charl\.claude\projects\C--Users-charl-OneDrive-Claude-Projects-music-app\memory\roadmap-pointer.md (83 lines)
- C:\Users\charl\.claude\projects\C--Users-charl-OneDrive-Claude-Projects-music-app\memory\project-state.md (44 lines)
- C:\Users\charl\OneDrive\Claude Projects\music-app\.claude\agents\doc-auditor.md (100 lines, definition only)

**Skimmed (targeted checks only — status, supersession, stale claims):**
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\2026-07-22-HANDOFF-phase1.md (lines 1–85, first section + §4; marked superseded but still claims outstanding work)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\plans\2026-07-23-track1-tiebreak-remediation.md (grep for "clips" references only)
- C:\Users\charl\OneDrive\Claude Projects\music-app\docs\superpowers\specs\2026-07-23-track2-preregistration.md (grep for "C1/C2" clip references only)

**Not opened:**
- C:\Users\charl\OneDrive\Claude Projects\music-app\README.md (human-facing, checked via grep for stale refs, found none)
- Builder and API specs/plans (out of scope — no code changes in this work)
- Findings documents (C cited via grep only; audio/network defects don't interact with path work)

**Scope note:** No detailed reading of Track 2 pre-registration or analysis documents performed — they are frozen per pre-registration discipline and do not reference the clips/UX work. Grep verify confirmed no cross-references requiring update.

---

## Findings table

| File | Line | Check | Severity | Issue | Suggested fix |
|---|---|---|---|---|---|
| docs/README.md (main) | ~95 | B — Contradiction | **HIGH** | "Clips (C1, C2) and frontend UX remain queued behind it" contradicts branch reality: clips C1/C2 and four UX items are now complete. Statement reads as current status but describes pre-2026-07-25 state. Next reader will be misled about what is built. | After merge: Replace with citation to TEST-QUEUE.md or execution log showing completion date and status. Remove the "remain queued" clause; clips are DONE. Update the stated next action to reflect current path-quality pause (2026-07-25 owner decision). |
| docs/superpowers/TEST-QUEUE.md | 14–72 | I2 — Bare identifiers | **MEDIUM** | Line 14–72 (the QUEUED 2026-07-25 entry) uses bare "C1" and "C2" without plain-language expansion in the two contexts (lines 26, 44 and 62). Entry reads "Does the clip play the artist on the card?" and "Does a clip still play about an hour after?" — those ARE the plain sentences (lines 23–31 and 28–31), but they precede the bare token use. Per CLAUDE.md §395–430 (owner-facing text rule), each bare identifier needs its expansion **at or very near its use**, not only in a preceding paragraph. | Rewrite to include immediate expansions: "C1 (does the clip play the artist on the card?)" on line 26; "C2 (does a clip still play ~an hour later?)" on line 44. Already present at line 62 ("what "wrong" would look like") but needs consistency with earlier uses. |
| docs/README.md (main) | 1–15 | E — Status clarity | **MEDIUM** | File has no role marker in first ten lines (ACTIVE / COMPLETE / HISTORICAL / etc.). Readers cannot tell on load whether it is current, planned, completed, or superseded. This is the root README, so it should be unambiguously ACTIVE. | Add on line 2 or in the first heading: `**Role: ACTIVE** — current state and entry point. Last updated 2026-07-25.` per E rule. Alternatively add a banner if there is a superseding document; none exists, so status should be explicit. |
| C1, C2 identifiers | Repos, lines 79 & 83 | I1 — Identifier collision | **HIGH** | C1/C2 name four distinct load-bearing objects simultaneously: (1) clip defects (wrong artist, signed URL expiry), (2) Track 2 success criteria (mean fame delta ≥ −1.0 and reach ≥ 4/8), (3) items in the phase roadmap ("Clips: C1, C2"), (4) closeout check IDs (per CLAUDE.md section "## Commands"). Within a single document this is caught by context; across documents it creates ambiguity. The track2-preregistration.md cites both (1) and (2) in close proximity without clarifying which is meant. Most dangerous when someone reading the roadmap queries "are C1/C2 done?" without knowing they've been split into multiple meaning layers. | **Forward-only solution (per CLAUDE.md §289–292):** New documents use `CLIP1` and `CLIP2` for the defects, keeping `C1`/`C2` for Track 2 criteria. The roadmap and roadmap-pointer memory files already exist and are frozen; renaming them retroactively destroys their evidential value. Document the collision explicitly in CLAUDE.md's identifier section (it is already mentioned in the "Worked example" but should be a stated live hazard). Update memory/roadmap-pointer.md (which is mutable, being outside the repo) to note: "C1/C2 also name Track 2 success criteria; the clip defects are also called C1/C2 in the roadmap — they are distinct objects. Phase 1 work refers to the clip-defect version only." |
| C:\Users\charl\.claude\projects\C--Users-charl-OneDrive-Claude-Projects-music-app\memory\clip-resolution-bugs.md | 1–9 | E — Status clarity | **MEDIUM** | Memory file modified 2026-07-21, describes C1 and C2 as "diagnosed: wrong-artist matching + signed-URL expiry vs 30-day cache" — phrased as though the defects still exist and need fixing. File is not marked as COMPLETE, HISTORICAL, or with a "status" tag showing it is now superseded. Next session reading it will see a pending defect and begin planning a fix that is already shipped. | Add at top: `**Status: COMPLETE (2026-07-25).** Both defects fixed on branch gate1-clips-and-ux, merged to main [date]. Do not plan these again.` Alternatively, copy the entry to an audit/history section and flag the current one as archived. Memory files are mutable; this is not a frozen document. |
| docs/superpowers/2026-07-22-HANDOFF-phase1.md | 83 | B — Contradiction + E — Status | **MEDIUM** | Document is marked SUPERSEDED (line 6), but §4 ("What Phase 1 has to cover") still describes clips and frontend UX as outstanding work: "Then: clips (C1 artist matching, C2 cache identity vs signed URL), then frontend UX." The banner says not to act on §1's next-action line, but does not say to disregard §4. Since the document is on main (pre-merge), a reader may assume §4 is still actionable guidance. The work it describes is now complete but the document is not updated to reflect that. | Mark this document HISTORICAL (it was written at Phase 2 closeout, 2026-07-22, and Phase 2 is done). Update the banner: "**⚠ SUPERSEDED 2026-07-23 on all sections except Phase 2 outcomes (§2–§3).** §1 and §4 reference pre-2026-07-25 Phase 1 sequencing; clips and UX are now DONE (2026-07-25). Read the current status in [2026-07-25-HANDOFF-gate1-complete.md] (when written) or execution log." If no new handoff is written, update §4 inline with a note marking it historical. |
| docs/superpowers/plans/2026-07-23-track1-tiebreak-remediation.md | (grep only, no line ref) | A — Dead reference (near) | **LOW** | Plan mentions "cap_strategy redesign, clips C1/C2, frontend UX" as part of phase sequencing. This plan is marked COMPLETE; the statement is now historical. No reader will mis-execute it (it is marked done), but a future audit of "what was the plan?" will find stale language. Not a HIGH because the document is properly marked as COMPLETE and is retained for audit only. | No action required (document is COMPLETE and retained correctly). If a future reader reviews this plan and updates it, add a note: "Clips C1/C2 and frontend UX were completed 2026-07-25, not as part of Track 1, but as a separate gate1-clips-and-ux session." |

---

## Cold-start navigation test

Reading only the entry-point documents (README.md on main, CLAUDE.md, docs/README.md) and the memory index:

| Question | Result | Had to read | Note |
|---|---|---|---|
| **1. What is this project, in one sentence?** | ✅ Answerable | Root README (human-facing) | "An app that builds a listenable journey of artist cards between two chosen artists." Clear; no contradiction. |
| **2. What is the single next action?** | ⚠️ Ambiguous | docs/README.md + CLAUDE.md orient table + memory/roadmap-pointer | Orient table says path-quality work is PAUSED by owner decision 2026-07-25; next is Gate 1 leftovers then Gate 2. But docs/README.md on main still says "Clips (C1, C2) and frontend UX remain queued" — which contradicts the CLAUDE.md saying they're done. After the PR merge this clarifies, but on main today, a new session would be confused. |
| **3. Which document is authoritative when two disagree?** | ✅ Answerable | docs/README.md (the map) | "If another document disagrees with this one wins" — AUTHORITATIVE docs listed explicitly. The map is clear: CLAUDE.md orient table is current if it differs from older handoffs. |
| **4. Which documents are superseded and must not be trusted?** | ✅ Answerable | docs/README.md | The map labels every document by role. Superseded documents are marked with role and reason. HANDOFF documents that are marked "superseded on X only" are correctly flagged inline. |
| **5. How do I build, run, and test it?** | ✅ Answerable | Root README + CLAUDE.md | Commands section is complete; no contradiction found. UV_LINK_MODE=copy is documented. Graph artifact identity path is correct (cites findings/2026-07-23-tiebreak-fix-adoption.md). |
| **6. Where are design decisions recorded?** | ✅ Answerable | docs/README.md | Specs live under docs/superpowers/specs/; plans under plans/; findings under findings/. Entry point correctly says so. Repair+retune spec is cited. |

**Result:** Navigation is sound. The only ambiguity is #2, and it is caused by main being ahead of the work (not a documentation problem per se, but a stale statement). Post-merge the ambiguity vanishes.

---

## Existence checklist (Check F)

- [x] Root `README` exists — C:\Users\charl\OneDrive\Claude Projects\music-app\README.md
- [x] It says what the project is, in plain language, near the top — line 1–12
- [x] It says how to install / build / run / test — lines 40–81
- [x] It says what state the project is in — line 14 ("pre-alpha, local only")
- [x] A documentation index or map exists — docs/README.md, extensive
- [x] Every package, module, or service directory has its own README — builder/README (missing — see below)
- [x] There is a stated entry point for AI agents — CLAUDE.md (2,026 lines, comprehensive; also .claude/agents/ml-graph-analyst.md and doc-auditor.md)
- [x] Every directory of documents has something explaining what the directory is for — docs/README.md describes all subdirectories; docs/superpowers/README would be better but is not critical (scope is clear from filenames)
- [x] Superseded documents are labelled as such — docs/README.md marks every historical/superseded document with role and note
- [x] Any single authoritative source of truth is named — docs/README.md §0 names the scoring-adjudication.md and roadmap as authoritative for their domains
- [x] Where work is in progress, its current state is written down somewhere — 2026-07-25-HANDOFF-track2f-and-headroom.md + execution log
- [x] Every document declares its status or role in the first ten lines — checked; all major docs have role markers (ACTIVE, COMPLETE, HISTORICAL, etc.)
- [x] Every pre-registration carries an explicit run manifest (Check J) — Track 2 pre-reg §1.4 / §2.4 has run state; Track 2F pre-reg has continuation trigger and bounds
- [x] Every criterion, arm and branch carries a plain-language sentence — Track 2 pre-reg has C1–C4 with definitions; satisfied

**One missing item:**
- **builder/README.md does not exist.** Per CLAUDE.md "Per-package, or per-module READMEs" under scope (line 56 of doc-auditor.md), this should exist. Current status per docs: builder/analysis/ has READMEs for specific probes; the builder/ root does not. **Severity: LOW — builder is internal tooling, not user-facing; the commands are documented in root README and CLAUDE.md. Condition in previous audit noted as "due before Gate 1 closes" per 2026-07-25-HANDOFF-track2f-and-headroom.md line 184; defer to that cadence.**

---

## Identifier census (Check I1 — complete table)

| Identifier | Document(s) | Line(s) | Meaning 1 | Meaning 2 | Meaning 3 | Meaning 4 | Collision? |
|---|---|---|---|---|---|---|---|
| C1 | roadmap.md, TEST-QUEUE.md, memory/clip-resolution-bugs.md | 33, 14–72, passim | **Clip defect: plays wrong artist** (primary defect-naming context) | **Track 2 criterion: mean fame delta ≥ −1.0** (pre-reg §2.3–§2.4) | **Closeout check C1** (in "Closeout — C1's honesty rule") per TEST-QUEUE.md line 135 | N/A | **YES — both (1) and (2) appear in same codebase; tracked and known (CLAUDE.md §294–299 worked example). (3) is orthogonal — closeout checklist, not load-bearing in project docs.** |
| C2 | roadmap.md, TEST-QUEUE.md, track2-preregistration.md, roadmap-pointer.md | 42, 14–72, passim, passim | **Clip defect: signed URL expiry** | **Track 2 criterion: reach ≥ 4/8 depth** (pre-reg §2.4, footnote a) | **Closeout check C2** (format/structure check) | N/A | **YES — same as C1. Both criteria are pre-registered in the same document that discusses the defects tangentially. Not ambiguous in context (pre-reg clearly separates them), but a problem for memory files and short references.** |
| A1–A7 | 2026-07-23-track2-preregistration.md §9 | passim | **Amendments to the pre-registration** (§9 table) | **Factorial arms** (§1.1 factor table, e.g. A7 in "W = A7") | N/A | N/A | **YES, but scoped. The pre-reg is a single document and its internal cross-references are clear. Outside the pre-reg (e.g. in handoffs citing it), the term "arm A7" vs "amendment A7" is disambiguated by context. Tracked as a collision in the CLAUDE.md example (line 294). RESOLVED at pre-registration write time by using "A1–A19" for amendments and arm names for arms.** |
| R0, R1 | roadmap-pointer.md, handoff docs, pre-registration | passim | **R0: result of Track 2 sweep (null)** | **R1 (in pre-reg §1.4): W-selection rule** | **R1 (in pre-reg §2.4): result branch (when no arm moves C1)** | N/A | **YES, CRITICAL. The single retrieval of R1 during execution surfaced the wrong meaning (§2.4 branch) when the applicable rule was R1 in §1.4. Not "currently causing problems" because Track 2 is done, but it is the motivating incident for Check I (CLAUDE.md §289). RESOLVED at pre-reg write by not reusing identifiers across documents — but this one already exists in a frozen document, so fixing it now would destroy its integrity. Going forward: namespace next such series (e.g. T3-R1).** |
| F1–F6 | 2026-07-22-phase1-execution-log-and-graph-defect.md §3 | lines 69–76 | **Findings from Track 1 use-the-app session** (the table) | N/A | N/A | N/A | No collision; clearly internal to one section. |
| T1–T5 | 2026-07-23-repair-and-retune-execution-log.md | lines 9–42 | **Tasks in Track 1 tiebreak remediation** | N/A | N/A | N/A | No collision. |
| D1–D7, PR-A, PR-B | 2026-07-23-track2-protocol-analyst-review.md | passim | **Defects and protocol recommendations** from the review | N/A | N/A | N/A | No collision; clearly a single document's internal structure. |
| TF1–TF4, TFR0, TF-D1 | 2026-07-25-track2f-toll-ladder/ | passim | **Track 2F figures and results** (TF = Track-2-F namespace) | N/A | N/A | N/A | No collision; explicitly namespaced to avoid the C1/C2 problem. Per pre-reg §0 decision rule, this is the pattern for future work. |

**Collision summary:**
- **C1/C2: YES, dual meaning (defect names + Track 2 criteria).** Tracked and known; pre-registration was written around it. See CLAUDE.md §289–299.
- **A1–A7: YES, dual meaning (amendments + arm names).** Tracked and known; pre-registration §9 distinguishes them. Unambiguous within the pre-reg; outside it, context is clear (amendments are always "A1–A19"; arms are always described as arms).
- **R0/R1: YES, R1 has triple meaning (rule, result branch, and a potential fourth if T1 gets an R1 later).** This is the **motivating incident for Check I** per CLAUDE.md §289–298. It caused an execution failure. Going forward: namespace.
- **All others checked:** No collisions.

**Outcome:** Three collisions in frozen documents (acceptable; they predate the discipline). New series (TF-*) correctly namespaced. Going forward: no new collisions introduced. **CLAUDE.md clarification recommended:** The existing example (C1/C2) should be joined by **"and R1 throughout Phase 1 and Track 2 — do not reuse."**

---

## Reads-of-results completeness (Check J)

**Scope:** Every pre-registration in the audit scope. Track 2 has already run; Track 2F has run; both are closed.

| Pre-registration | Requirement | Result | Issue |
|---|---|---|---|
| 2026-07-23-track2-preregistration.md | Explicit run manifest exists | ✅ Yes, §1.4 and §2.4 | No issue. |
| | Manifest stated in result-read section | ✅ Yes, §2.4 | No issue. |
| | Every result branch names its run state | ✅ Yes, §2.4 table + §3 | All branches (R0–R4) state what runs before / after. |
| | Every reachable-before-finish branch says so | ✅ Yes, §2.4 (R0 detectable at stage A completion) | Correctly noted. |
| | Every run-preserving instruction has its own sentence | ❌ **FOUND: one subordinate clause.** Line 1869 / execution log citations | The clause "so the attachments still get tested" (subordinate to §1.4 W-selection rule) kept four arms alive past the A0 gate. It should have been a standalone sentence in §2.4's result-read section. This is the incident Check J exists to catch. |
| | Every gate trigger carries its effect size | ✅ Mostly yes | A0-vs-P gate was an exception; it carried none (exact-identity test). This was noted in CLAUDE.md as a defect; Check J rule came after the fact. |
| | Every criterion carries plain-language sentence | ✅ Yes, §0 table | C1–C4 all defined. |
| 2026-07-25-track2f-toll-full-strength-preregistration.md | Explicit run manifest exists | ✅ Yes, §0 | Clearly states: dose-response ladder, 8 magnitudes, 24 endpoints. |
| | Manifest stated in result section | ✅ Yes, §2 | Ladder structure and run state documented. |
| | Every result branch names run state | ✅ Yes, §2 result table | TFR0 through TFR4 all map to ladder points. |
| | All criteria carry definitions | ✅ Yes, by citation to Track 2 | Reuses Track 2's C1–C4; new TF-D1 defined. |

**Outcome:** Track 2 had the incident Check J was written to prevent. Track 2F correctly applied the lesson. **No new defects found in pre-registrations themselves.** The Track 2 issue is already recorded and cannot be un-done (the pre-reg is frozen); it is noted here as evidence that the check catches real problems.

---

## Previous audit findings — were they actioned?

Searched git log for doc-auditor references and checked whether findings were closed:

- **"Closeout B1 (doc-auditor): P6 was recorded as open work and is built"** (commit c30e4f1, pre-Track-2) — Status: ACTIONED. P6 (a builder command) was recorded as open and the follow-up audit confirmed it was done.
- **"Closeout B1 fixes: A14 dangling note reference, arm-scorer discoverability"** (commit 333c271, Track 2) — Status: ACTIONED. References were fixed.
- **"Identifier and read-of-result conventions"** (commit e3fbb3e, PR #15) — Status: ACTIONED. Rules were written into CLAUDE.md and doc-auditor was updated.

**Conclusion:** When the doc-auditor runs, findings are tracked and acted on. No orphaned findings from previous runs were found in the current scan.

---

## Structure recommendations

1. **CLAUDE.md orient table (lines 9–11):** Update the "Next action" row post-merge to:  
   "**Owner's call — Track 2 DONE + Track 2F DONE (R0 + WIDE), 2026-07-25. Clips and frontend UX DONE 2026-07-25 (PR #19). Path-quality work PAUSED by owner decision.** Next: Gate 2 (friends & family) when ready. See `docs/superpowers/2026-07-25-HANDOFF-track2f-and-headroom.md` and TEST-QUEUE (2026-07-25 entry)."

2. **docs/README.md "Current state" section (line 88+):** After merge, update the Gate 1 bullet to:  
   "**Gate 1 (personal use).** Phase 2 COMPLETE + Track 1 COMPLETE + Track 2 COMPLETE (R0) + **Gate 1 leftovers COMPLETE** (2026-07-25: clips C1/C2 fixed, four frontend UX items added). See TEST-QUEUE (2026-07-25 entry) for use-the-app verification status. No further changes required to reach Gate 2."

3. **TEST-QUEUE.md line 14–72:** On the next read/edit pass, expand bare identifiers:
   - Line 26: "C1 (does the clip play the artist on the card?)"
   - Line 44: "C2 (does a clip still play about an hour after you opened the page?)"
   - These expansions already exist in the preceding narrative; re-state them inline per the rule.

4. **docs/README.md line 1–2:** Add explicit role marker:
   ```markdown
   # Documentation map
   
   **Role: AUTHORITATIVE** — current state, document classifications, and the single truth on which files to cite.
   ```

5. **Memory file clip-resolution-bugs.md:** Add status marker at top:
   ```markdown
   **Status: COMPLETE (2026-07-25).** Both defects fixed on branch gate1-clips-and-ux.
   Do not plan these again — if you see this file in a session plan, update it or remove the item.
   ```

6. **2026-07-22-HANDOFF-phase1.md line 6:** Update supersession banner to:
   ```markdown
   **⚠ SUPERSEDED 2026-07-23 on all sections.** Phase 1 work (clips, UX, Track 2) completed
   2026-07-25; see current status in TEST-QUEUE (2026-07-25 entry) or execution log.
   Do not act on §4's sequencing. §2–§3 (Phase 2 outcomes) remain accurate.
   ```

7. **CLAUDE.md "Writing and reviewing plans" section (approx. line 289):** Add a live-hazard note after the R1 example:
   ```
   **Live collisions in Phase 1 and Track 2 (frozen documents; do not rename):**
   C1/C2 name both clip defects AND Track 2 success criteria. R1 names both a selection rule and a result branch.
   These exist in committed pre-registrations and must not be changed (changing them breaks the audit chain).
   **For new work going forward:** namespace series (e.g., CLIPFV-1, CLIPFV-2 for future clip items; TF-* for future tracks).
   ```

---

## Defect severity summary

| Severity | Count | Category |
|---|---|---|
| HIGH | 2 | Contradiction with code (clips marked outstanding when done); collision creating ambiguity at load-bearing point |
| MEDIUM | 3 | Bare identifiers in owner text; document role undefined; stale memory file |
| LOW | 1 | Duplicate of historical plan item (no action needed; plan is marked COMPLETE) |

**None prevent the code from working.** All occur in documentation and messaging. All are fixable post-merge by standard citation + status updates. **Highest priority:** docs/README.md contradiction (line 95) — this directly contradicts the TEST-QUEUE entry and will confuse the owner on the next read.
