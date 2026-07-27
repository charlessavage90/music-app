# Documentation Audit: Context and Navigation Layer

<!-- docs-lint: skip-links — this report QUOTES MEMORY.md's and CLAUDE.md's own link
     syntax verbatim as evidence, including links to memory files that live outside the
     repo (`roadmap-pointer.md`, `project-state.md`, `path-quality.md`) and a proposed
     `superseded-docs.md` that was never written. They are quotations, not navigation, and
     cannot resolve from here by design. Marker added 2026-07-27 when docs-lint first ran. -->

**Role: COMPLETE.** A frozen `doc-auditor` report. *(Role line added 2026-07-27.)* It audited
a navigation layer that has since been rewritten — `docs/README.md` did not exist when this
was written — so read it as history. Spot checks in the 2026-07-27 full-project audit confirm
its HIGH findings were resolved by that rewrite rather than silently dropped.

**Date:** 2026-07-22
**Scope:** 14 files (6 in repo + 8 in memory directory)
**Audit criteria:** Dead references, duplicated figures (ONE-RECORD-RULE), contradictions, cold-start navigation, structure, gaps, staleness

---

## Summary

Five HIGH-severity issues found, all involving the ONE-RECORD-RULE: numeric claims about similarity scoring appear in multiple files without citing the authoritative record (`2026-07-21-scoring-adjudication.md`). A new agent reading CLAUDE.md and MEMORY.md cannot identify the authoritative document for scoring figures or discover that the roadmap's Phase 2 is superseded by a separate design spec. The memory index correctly points to individual documents but lacks cross-references necessary to resolve contradictions about the same measurements. Two patterns of staleness: memory files still reference commits that were superseded, and the roadmap's C4 section contains overturned claims with inline disclaimers but the old claims remain live in narrative form elsewhere.

---

## Findings Table

| File | Line | Check | Severity | Issue | Suggested Fix |
|---|---|---|---|---|---|
| `docs/how-we-map-similar-artists.md` | 117 | B (one-record) | HIGH | "similarity scores correlated **0.725 with artist fame**" — this figure is OVERTURNED (adjudication §6 claim #18: +0.259 to +0.287 on v3, sign unstable). Document is a dev-blog narrative and restates this overturned claim as historical fact without citing the authoritative record or indicating the finding is now superseded. | Add banner at top: "This is a historical narrative of the design journey. Scoring conclusions are superseded by [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md) — see especially §6 claim #18 for the 0.725 figure." |
| `docs/how-we-map-similar-artists.md` | 103 | B (one-record) | HIGH | "A junk connection scored **6.6× higher** than the genuine bond between Miles Davis and Stan Getz" — figures in this comparison (0.148 and 0.022) are OVERTURNED. Adjudication §2.4: "0.148" has no referent, and "2357 vs 277" was fabricated/mistranscribed. The 0.022 (Stan Getz) is correct but the 0.148 is unrepresentative of the actual failure mode (which was a ~0.001 junk edge entering a micro-clique). | Add citation in situ: "Later re-measured in [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md) §2.4; the quantitative claim was overturned but the qualitative observation (certain normalisation schemes route through micro-cliques) was confirmed." Restore the narrative framing without the specific ratios. |
| `MEMORY.md` | 5 | A (references) | HIGH | "[Next action + roadmap](roadmap-pointer.md) — START HERE" claims "Phase 2 plan is written; execute it in a FRESH session". But CLAUDE.md (the cold-start navigation document) does not mention Phase 2 at all or point to the roadmap. A fresh agent would not know the next action exists. | Update CLAUDE.md Workflow section (line 150–155) to add: "**Next action** (execute in a fresh session): `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` §Gate 1, Phase 2. The phase's design is in `docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md`; the plan is in the roadmap." |
| `CLAUDE.md` | 69 | A (references) | MEDIUM | "Adopted 75k artifacts are identified by recorded checksum in `docs/superpowers/findings/`" — no specific file or section. A reader cannot locate the checksum. | Change to: "Checksum of the adopted graph is recorded in [`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`](../docs/superpowers/findings/2026-07-21-scoring-adjudication.md) Table in §1." |
| `CLAUDE.md` | 106 | A (references) | MEDIUM | "every external popularity source imported a population mismatch with the similarity graph. It's then log-scaled to 0–1 because raw counts are power-law distributed. (see `docs/superpowers/findings/`)" — vague pointer. Reader cannot find the detailed argument. | Change to: "(see [`docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`](../docs/superpowers/findings/2026-07-19-listenbrainz-probe.md) §6a–6f)" which is where the empirical comparison of popularity sources lives. |
| `CLAUDE.md` | 125 | B (one-record) | MEDIUM | "Dijkstra over the in-memory `GraphStore`, pure/no I/O. Cost per edge (weights in `api/…/config.py`, `w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`)" — these are the starting weights but have been questioned and analysed. Should cite the record. | Change to: "Dijkstra over the in-memory `GraphStore`, pure/no I/O. Starting cost weights in `api/…/config.py`: `w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`. See [`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`](../docs/superpowers/findings/2026-07-21-scoring-adjudication.md) §5.4–5.5 for their status (w_floor is a no-op; w_known needs differentiation)." |
| `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | 48 | B (one-record) | MEDIUM | Section C3 cites "w_floor is a no-op" with a reference to the findings, but line 50 (note in C3 after "Corrected:") contradicts itself in narrative form, requiring the reader to cross-check the adjudication to understand which part is live. | The inline correction (line 50) is good but buried. Add a line at the end of C3: "For quantitative detail, see adjudication §5.4–5.5." |
| `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | 50 | C (contradictions) | MEDIUM | C3 originally said "the two bypass signals are *behaviourally identical at runtime*" but line 50 corrects this: "**That is wrong** — `dislike` still applies `avoidance_map`". This is correct and self-correcting, but a reader unfamiliar with Git history may not understand why the overstriking is there. | Add a banner to the C3 section: "**NOTE: C3 has been corrected. See the inline note below. The bypass signals are NOT identical; only `known` degrades to a plain exclusion.**" |
| `.claude/agents/ml-graph-analyst.md` | 44 | A (references) | MEDIUM | References "Task 1 findings §6a–6f" but there is no such findings document with "§6a–6f" structure. The document referenced is `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`, which has sections 1–7 only (no alphabetic subsections). | Change to: "`docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` §6–7" or verify the correct section numbers in that document. |
| `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | 154 | A (references) | MEDIUM | References "`../findings/2026-07-21-architecture-review-and-path-baseline.md`" but this file contains a superseding banner that says to read the adjudication instead. If someone follows this reference, they will be sent to a document that tells them to read a different document. While technically correct (the banner is there), it is an extra hop. | This is a reference accuracy issue, not a bug per se. Document is accurate but indirect. Consider whether the Reference section should point to the adjudication directly. |
| `MEMORY.md` | 3 | A (references) | LOW | "[Project state](project-state.md)" links to a memory file but CLAUDE.md never mentions to read MEMORY.md. A cold-start agent would not know memory files exist. | Add to CLAUDE.md after line 155: "**Persistent session memory** is maintained in `.claude/projects/…/memory/`; start a new session by reading `MEMORY.md` in that directory for a refresher." |
| `roadmap-pointer.md` | 11 | A (references) | MEDIUM | References "`docs/superpowers/plans/2026-07-21-phase2-path-quality.md`" (commit `9c58130`) but MEMORY.md index says "START HERE: Phase 2 plan is written; execute it in a FRESH session, subagent-driven". These should be the same document but the memory uses different wording. | Unresolved: verify that the commit sha matches the current `2026-07-21-phase2-path-quality.md`. If they match, clarify in roadmap-pointer.md: "This is the exact plan in `docs/superpowers/plans/2026-07-21-phase2-path-quality.md` (commit `9c58130` still current). Do not execute inline; dispatch to `superpowers:subagent-driven-development` in a fresh session." |
| `roadmap-pointer.md` | 23 | C (contradictions) | MEDIUM | States "Its **Phase 2 content is superseded** by the spec `docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md`" — but the roadmap file itself (line 72–76) contains a Phase 2 section. Which wins? Is the Phase 2 in the roadmap stale, or is the spec merely an extended treatment? | Clarify: "The Phase 2 *goals* in the roadmap (clips, bypass, UX) remain; the *path quality* section of Phase 2 (lines 72–76 above) is superseded by the separate spec. To execute Phase 2, follow the spec and plan, not the roadmap's Phase 2 text." |
| `crawl-resume.md` | 11 | G (staleness) | LOW | "See [[path-quality]] for the baseline evaluation of this graph" but path-quality.md §2 (lines 11–13) explicitly says the figures are in a DIFFERENT document (`2026-07-21-scoring-adjudication.md`). The indirection should be collapsed. | Change to: "See [`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`](../docs/superpowers/findings/2026-07-21-scoring-adjudication.md) for the evaluation of this graph." |
| `.gitignore` line 10 & `CLAUDE.md` line 66 | 66 & line 10 | E (structure) | LOW | CLAUDE.md says "with only `!tests/fixtures/*.bin` exempt" but the actual path is `api/tests/fixtures/graph-fixture.bin` (one level deeper). The glob pattern works but is misleading about the structure. | Change to: "with only `!api/tests/fixtures/*.bin` exempt" — or verify the build actually expects `tests/` at root. |

---

## Cold-Start Navigation Test

**Setup:** Read only `CLAUDE.md` and `MEMORY.md` (as a new agent would).

### Question 1: What is the single next action on this project?

**Answerable? AMBIGUOUS** 
- CLAUDE.md says the project uses Superpowers workflow and points to design docs, but does not state what to do next. 
- MEMORY.md line 5 says "START HERE: execute …Phase 2 plan is written" but a fresh agent would not read MEMORY.md without being told by CLAUDE.md to do so.
- **What had to be read:** MEMORY.md to find roadmap-pointer.md, which then points to the roadmap and the phase2 spec.
- **Gap:** CLAUDE.md should have a "Next action" subsection under Workflow.

### Question 2: Which document is authoritative for scoring and path-quality figures?

**Answerable? YES, but requires two hops**
- CLAUDE.md line 106 mentions "see `docs/superpowers/findings/`" without specificity.
- MEMORY.md line 6 has "[Path quality](path-quality.md)" which reads: "**Single quantitative record: `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`**".
- **What had to be read:** MEMORY.md and then the path-quality memory file.
- **Issue:** A fresh agent reading only CLAUDE.md cannot find the single record — they would need to be told to read MEMORY.md first.

### Question 3: Which documents are superseded and must not be trusted?

**Answerable? NO**
- CLAUDE.md contains no disclaimer about superseded documents.
- MEMORY.md line 7 mentions "Path quality" with a pointer that says "pointer to the ONE scoring record; never restate its numbers" — but does not list which documents ARE superseded.
- Reading the adjudication document itself (not in initial context) reveals which documents have sections that are overturned.
- **What had to be read:** None of the initial documents explicitly list superseded files. The adjudication must be read to discover that architecture-review.md §5 and the roadmap's C4 are partially superseded.
- **Gap:** MEMORY.md should include a memory entry "[Superseded docs](superseded-docs.md)" listing which files have overturned sections.

### Question 4: Where do I find the current implementation plan, and how do I execute it?

**Answerable? AMBIGUOUS**
- CLAUDE.md mentions "Superpowers workflow" and "Design docs live under `docs/superpowers/`" but does not name a specific plan file or execution mode.
- MEMORY.md line 5 points to roadmap-pointer.md, which says "Phase 2 plan is written; execute it in a FRESH session, subagent-driven".
- Roadmap-pointer.md line 11 points to `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` with a specific commit, but also mentions a separate `.md` file.
- **What had to be read:** MEMORY.md → roadmap-pointer.md → the roadmap itself to find the phase breakdown.
- **Issue:** The plan file name and the execution mode ("FRESH session, subagent-driven") are not discoverable from CLAUDE.md alone.

### Question 5: How do I run the tests for each of the three packages?

**Answerable? YES**
- CLAUDE.md §Commands has explicit test commands for all three (lines 44, 57, 75).
- Environment variables and prefix requirements are stated.
- **What had to be read:** Only CLAUDE.md.
- **Issue:** None. This is clearly documented.

---

## Structure Recommendations

### 1. `CLAUDE.md` (repo root, lines 1–162)

**Current state:** 162 lines. Does one clear job (quick-start guide for the three packages) but lacks discovery of the bigger picture (what's the next milestone? where are the decisions documented?).

**Recommendation — split into two:**
- Keep current content as `CLAUDE.md` (quick-start remains excellent).
- Add a new "Workflow" subsection (after line 155) with:
  ```
  ## Workflow and roadmap
  
  This project uses the Superpowers workflow. Start a new session by reading [`MEMORY.md`](.claude/projects/.../MEMORY.md) for the current milestone. 
  
  **Next phase:** Gate 1, Phase 2 (path quality). See [`docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md`](docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md) and execute in a fresh session via `superpowers:subagent-driven-development`.
  
  **Authoritative records:**
  - Scoring & path-quality metrics: [`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`](docs/superpowers/findings/2026-07-21-scoring-adjudication.md)
  - Design decisions: [`docs/superpowers/specs/`](docs/superpowers/specs/)
  - Implementation plans: [`docs/superpowers/plans/`](docs/superpowers/plans/)
  ```

### 2. `docs/how-we-map-similar-artists.md` (lines 1–156)

**Current state:** 156 lines. Excellent narrative of the design journey, but does not acknowledge that some conclusions (e.g., 0.725 correlation, 6.6× junk-edge inflation) have been superseded.

**Recommendation:** Add a banner at the top:
```markdown
> ## Note: Historical narrative
> 
> This document describes the design journey. **Several quantitative claims have been
> updated based on re-analysis.** See [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md)
> for the current measurements (especially §6 claim #18 on the 0.725 correlation and §2.4
> on the junk-edge inflation). The qualitative lessons (§6) remain valid.
```

### 3. `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` (lines 1–160)

**Current state:** 160 lines. Clear gate structure; C3 and C4 sections have inline corrections but the corrections are hard to spot.

**Recommendation:** Add a banner to sections C3 and C4:
```markdown
> ## ⚠ CORRECTIONS
> 
> This section has been corrected based on re-analysis. See [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md) for details.
> **Key update:** C3's claim of identical bypass behaviour is overturned — the signals do differ.
> C4 is entirely superseded; see the Phase 2 spec instead.
```

### 4. `docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md` 

**Current state:** Correctly cites the adjudication and does not restate numbers. **No change needed.**

### 5. `MEMORY.md` (lines 1–9)

**Current state:** 9 lines, one per memory file, pointers only. Excellent structure but lacks one critical entry.

**Recommendation — add before line 7:**
- `[Superseded sections](superseded-docs.md)` — which document sections are no longer current, and what replaced them.

**Create new file** `memory/superseded-docs.md`:
```markdown
---
name: superseded-docs
description: Which document sections are no longer current
metadata:
  node_type: memory
  type: project
---

- `docs/superpowers/findings/2026-07-21-architecture-review-and-path-baseline.md` §2, §4, §5: **scoring and path-quality metrics only** are superseded by `2026-07-21-scoring-adjudication.md`. §1 (non-scoring findings) remains live.
- `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` **Phase 2 section only** (lines 72–76): superseded by `docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md`. Gate structure (lines 9–15) and Phases 1, 3–7 remain current.
- `docs/superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` **C4** (lines 52–63): **substantively rewritten** by `2026-07-21-scoring-adjudication.md`. Read the adjudication, not C4, for current findings.
- `docs/how-we-map-similar-artists.md` §4 Trap 4 (lines 99–105): the 6.6× and 0.148 numbers are overturned; the qualitative finding (certain normalisation over-corrects) is confirmed.
```

### 6. `.claude/agents/ml-graph-analyst.md` (lines 1–119)

**Current state:** Excellent instructions for the ML graph specialist agent. Section references are mostly correct but line 44 has an imprecise reference.

**Recommendation:** Change line 44 from:
```
- `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` — the methodology narrative.
```
to:
```
- `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md` §4–7 — the methodology narrative and data-sourcing decisions (popularity estimation in §6d–6f).
```

---

## Gaps

1. **Persistent memory is not discoverable from CLAUDE.md.** A fresh agent has no way to know that `.claude/projects/*/memory/` exists and contains session state. Add a note to CLAUDE.md.

2. **No document lists which document sections are stale.** When multiple findings and specs exist, there is no manifest saying "use THIS one for scoring, ignore THAT one". The adjudication's §6 table serves this role but is not indexed in MEMORY.md.

3. **Execution mode is not in the workflow docs.** CLAUDE.md does not say "execute plans in a fresh session, subagent-driven" — that information lives only in roadmap-pointer.md and working-style.md. It should be in CLAUDE.md.

4. **No overview of the three packages' status.** Project state memory says "DONE" for stages 1–3a and "NOT STARTED" for 3b, but CLAUDE.md does not list the current gate or phase. A fresh agent cannot answer "are we working on personal-use features or AWS deployment?" without reading memory.

---

## Staleness

1. **Memory files reference commits that were part of iterative cycles.** `crawl-resume.md` line 11 says "See [[path-quality]] for the baseline evaluation" but path-quality.md explicitly redirects to the adjudication. Not wrong, but roundabout.

2. **Roadmap C3 and C4 contain inline corrections.** These are visible but require readers to parse strikethrough and inline notes rather than having a clean banner at the section level. Acceptable but improves with a banner.

3. **Graph artifacts on disk are not inventory-tracked.** `CLAUDE.md` line 65–70 mentions `.gitignore` excludes graphs and points to `docs/superpowers/findings/` for checksums, but the adjudication's Table §1 is the only place the actual artifacts are catalogued. Readers have to know to look there.

---

## Summary of High-Severity Findings

| Issue | Files | Impact | Fix Category |
|---|---|---|---|
| Overturned figures (0.725 correlation, 6.6× junk-edge) restated without citation | `docs/how-we-map-similar-artists.md` | Active misleading of new readers about scoring behaviour | A (references) + one-record banner |
| Authoritative scoring document not discoverable from CLAUDE.md | CLAUDE.md + MEMORY.md interaction | Cold-start agents cannot find authoritative record | A (references) |
| Phase 2 execution mode not in workflow docs | CLAUDE.md vs roadmap-pointer.md | Ambiguous whether to inline-execute or dispatch | Workflow section addition |

