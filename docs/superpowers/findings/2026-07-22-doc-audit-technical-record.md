# Technical Record Audit — 2026-07-22

**Scope:** Audit of design specs, findings, and implementation plans for consistency with the authoritative quantitative record.

**Status:** CRITICAL ISSUES FOUND. Two files violate the ONE-RECORD-RULE and contain claims contradicted by the adjudication. The Phase 2 plan is internally consistent and execution-ready.

---

## Summary

The project established a ONE-RECORD-RULE after discovering that five documents each kept their own copy of quantitative figures, which drifted into mutual contradictions. The adjudication (`2026-07-21-scoring-adjudication.md`) is now the single source. 

**Three high-severity findings:**

1. **Architecture review §5 restates overturned claims as fact.** The document has a banner marking it superseded, but then §5 contains specific numbers that are not merely superseded—they are measured and found false by the adjudication. Example: §5.1 states "+0.725" correlation, which the adjudication refutes as "unreproducible" (+0.26 to +0.29 instead). This violates both the ONE-RECORD-RULE and basic accuracy.

2. **Phase 2 spec cites the adjudication correctly and never restates numbers** — but simultaneously other documents do. The one-record-rule only works if enforcement is consistent.

3. **Architecture review §5's "provenance note" explains the staleness but does not excuse the accuracy problems.** The note says figures "are projections, not observed results" and should be "re-measured before treating as current," yet the findings section presents them as findings, not projections.

**The Phase 2 plan is well-structured and internally consistent.** No blocking issues detected. Build sequence, task dependencies, and adoption criteria are sound.

---

## Findings Table

| File | Line | Check | Severity | Issue | Suggested Fix |
|---|---|---|---|---|---|
| `2026-07-21-architecture-review-and-path-baseline.md` | 3-20 | G | HIGH | Banner says "superseded" but §5 contains numbers refuted (not superseded) by adjudication. Violation of accuracy principle. | Replace §5 entirely with a note: "§5 is a historical record of one analysis session. See adjudication §5–§6 for the corrected measurements and verdicts. Do not cite figures from §5." |
| `2026-07-21-architecture-review-and-path-baseline.md` | 184-189 | A | HIGH | §5.1 claims "+0.725 score/degree correlation" — adjudication §5.1 refutes as "+0.259 to +0.287 on v3; sign unstable." Directly contradicts authoritative record. | Remove the claim entirely. Cite adjudication §5.1 instead. |
| `2026-07-21-architecture-review-and-path-baseline.md` | 183-244 | B | HIGH | §5 contains 12 numeric claims (correlations, null baselines, path improvements) restated without citation to adjudication. Violates ONE-RECORD-RULE. | Every numeric claim in §5 must be removed or replaced with "See adjudication §X" citations. Do not restate numbers. |
| `2026-07-21-architecture-review-and-path-baseline.md` | 216-217 | A | MEDIUM | §5.3 claims "two bypass signals are behaviourally identical" — adjudication §5.5 refutes: `dislike` still applies `avoidance_map`; only `known` degrades to hard exclusion. | Remove. Cite adjudication §5.5 instead. |
| `2026-07-21-architecture-review-and-path-baseline.md` | 219-235 | A | MEDIUM | §5.4 diagnoses damping-before-log1p as cause of cosine failure — adjudication §2.1 refutes: the artifact was built by code with no `log1p` to apply damping to. Explanation is wrong though conclusion partially correct. | Replace with: "§4's conclusion (cosine over-corrects) is correct, but §4's explanation is refuted. See adjudication §2.1–§2.4 for the correct diagnosis." |
| `2026-07-21-architecture-review-and-path-baseline.md` | 63-64 | C | MEDIUM | References "spec §9" (determinism requirement) — this document is dated 2026-07-21 and spec is `2026-07-19-artist-path-alpha-design.md`. Verify that §9 exists and is determinism. | Verify reference: `2026-07-19-artist-path-alpha-design.md` does have §9 covering determinism. Reference is valid. |
| `2026-07-21-phase2-path-quality-design.md` | 10-15 | B | NONE (CORRECT) | Correctly declares adjudication as quantitative record and commits to citing section numbers instead of restating. | No issue. Model to follow. |
| `2026-07-21-phase2-path-quality-design.md` | 48-50 | A | NONE (CORRECT) | Correctly cites adjudication §2.5 for the p99 clip defect (30-82% ceiling hops) without restating the number. | No issue. Correct citation practice. |
| `docs/superpowers/plans/2026-07-21-phase2-path-quality.md` | 19-21 | B | NONE (CORRECT) | Declares that "numbers live in one document" (the adjudication) and mandates citations, never copying figures into code comments. | No issue. Correct policy. |
| `docs/superpowers/plans/2026-07-21-phase2-path-quality.md` | Various | D | MEDIUM | Plan assumes build timing unknown (§8 risk 1) and asks Task 1 Step 7 to "write it into Task 15 notes." Task 15's notes (lines ~3064–3380) do not have a labeled timing field; timing would need to be inferred from context. | Task 1 Step 7 should store timing in a dedicated location (e.g. `.claude/build-timing.txt` or inline in Task 15 Step 2's build command with a comment marker) so it is discoverable. Current plan requires manual search. |
| `2026-07-21-listenbrainz-probe.md` | 3-16 | G | NONE (CORRECT) | Has supersession banner but carefully preserves non-scoring content (rate limits, endpoint schema, popularity-source eliminations). Does not restate superseded numbers. | No issue. Correct use of banner. |
| `2026-07-19-artist-path-alpha-design.md` | 109 | C | NONE (VERIFIED) | Cites determinism as spec §9. Cross-checked: document does have §9 "Determinism" subsection. | No issue. |

---

## Phase 2 Plan Internal-Consistency Report

**Verdict: EXECUTION-READY**. The plan is large (3,465 lines, 16 tasks) and tightly coordinated. No blocking internal contradictions found.

### Checked Elements:

**Task dependency chain:**
- Track A (Tasks 1–10, measurement infrastructure) has no inter-task dependencies that would block execution. Task 1 establishes timing; Tasks 2–10 each produce one component (metrics, nulls, panel, diagnostics, etc.). These can run in any order once dependencies (GraphStore, config) are available.
- Track B (Tasks 11–16, artifact building and evaluation) is properly sequenced: config changes (11–14) before builds (15).
- Task 15 (build and evaluate) correctly depends on Track A completion and properly gates adoption on human review before Task 16.

**Task interfaces ("Consumes/Produces"):**
- Verified 12 critical interfaces: all backward references are consistent with when components are first produced.
- Example: Task 3 consumes Task 2's `adamic_adar`, `overlap_coefficient`; Task 2 produces these. ✓
- Example: Task 15 consumes Tasks 1–9; all are sequenced before. ✓
- No forward references, no missing interfaces.

**Code function signatures:**
- Task 2 defines `adamic_adar(store, u, v) -> float` (lines 402–414); Task 3 consumes it in `path_metrics` (line 612) with same signature. ✓
- Task 1 produces `build_manifest(graph, config, payload, elapsed_seconds) -> dict` (lines 167–179); Task 15 wires it in without signature mismatch. ✓
- No naming conflicts, no undefined consumers.

**File mutations (concurrent writes):**
- Task 11 modifies `builder/config.py` (add knob)
- Task 12 modifies `builder/config.py` (add entity filter toggle)
- Task 13 modifies `builder/config.py` (add rescale knob)
- Task 14 modifies `builder/config.py` (ditto)
  All modifications are to different config fields; no conflicting edits. ✓

**Special constraints:**
- Task 13 Step 7 requires byte-identity check: `control` arm must reproduce `graph-75k-v3.bin` exactly. Plan provides command for verification.
- Task 14 Step 5 re-verifies byte-identity after log-space refactoring. This is essential (the exact failure the project is guarding against) and is properly placed. ✓
- Task 15 Step 1's `run_baseline.py` rewrite is intentional (note at line 672: "discarded for Task 15"). Good pattern.

**Panel and held-out slice:**
- Panel generation (Task 6) uses seed 42, frozen to JSON, committed. ✓
- Held-out slice is 30 of 130 pairs, marked in JSON, held to final verification (Task 15 Step 7). ✓
- Adoption criterion §6 requires held-out reproducibility. Plan enforces this.

**Adoption criterion enforcement:**
- All six criteria are explicitly listed (spec §B9; plan lines 3346–3353).
- Task 15 Step 6 is a "STOP — human decision point" that requires manual confirmation before proceeding.
- Criterion 2 (`w_jump = 0` control arm) is evaluated alongside `full` config to detect gaming along min-degree axis. ✓
- Criterion 4 (ceiling hops below 30%) is computed but plan does not auto-reject. Task 15 Step 6 requires human review.

**Snyk integration:**
- Plan lists "Snyk: run snyk_code_scan on new or modified Python and fix what it reports before committing" (lines 20).
- Task 14 Step 6 explicitly runs Snyk before commit. Task 1 step content blocks should do likewise (unverified for Tasks 2–10).

**Unresolved**: Whether every new-code task includes Snyk in its "Step 6: commit" block. Code snippets are present, test coverage is good, but Snyk step is not called out in Tasks 2–10.

---

## Spec-to-Plan Coverage

**Spec: `2026-07-21-phase2-path-quality-design.md`**

| Spec Section | Requirement | Plan Task | Coverage |
|---|---|---|---|
| §A1 | Path-export tool (HTML, rank/score/degree per hop) | Task 9 | ✓ Complete |
| §A3 | Configuration-model rewire null model | Task 4 | ✓ Complete |
| §4 | Step A: adjudication (already done in real adjudication) | Task 1–10 setup | ✓ Verified as completed |
| §B1 | Adamic–Adar metric (primary objective) | Task 2 | ✓ Implemented |
| §B1 | Overlap coefficient (mandatory guard) | Task 2 | ✓ Implemented |
| §B1 | Jaccard (diagnostic) | Task 2 | ✓ Implemented |
| §B1 | Geometric mean aggregation | Task 2 | ✓ Implemented |
| §B1 | Bad-path detector (screen, not objective) | Task 5 | ✓ Separate file; cannot be optimised |
| §B2 | Frozen MBID panel (130 pairs) | Task 6 | ✓ Committed JSON |
| §B2 | Held-out slice (30 pairs, 6-9-12 per stratum) | Task 6 | ✓ Marked in JSON |
| §B3 | Entity filter (drop 7 special-purpose nodes) | Task 11 | ✓ Unit test asserts removal + survival |
| §B4 Precondition 1 | Mutual k-NN cap fix | Task 12 | ✓ Implemented; max-degree invariant tested |
| §B4 Precondition 2 | Percentile-rank rescale (Factor R) | Task 13 | ✓ Byte-identity verified for control arm |
| §B4 Factor d | Damping in log space, no centring (rank rescale) | Task 14 | ✓ Implemented; negative values handled |
| §B5 | Grid: 6-arm sequence (control → cap → rescale → d sweep) | Task 15 | ✓ Build sequence specified, adoption criteria enforced |
| §B6 | Support axis deferred | Deferred | ✓ Acknowledged as future work (spec lines 416–419) |
| §B7 | Diagnostics (degree p50/p99, saturated edges, corrr, etc.) | Task 7 | ✓ Complete list matches spec §B7 |
| §B8 | Paired Wilcoxon, Holm correction | Task 8 | ✓ Implemented with scipy.stats |
| §B9 | Six adoption criteria | Task 15 Step 6 | ✓ All listed; human gate enforces |
| §B10 | Adoption: regenerate 5k fixture, update config | Task 16 | ✓ Fixture regeneration + config commit |
| §6.1 | w_jump = 0 control arm (resolve popularity confound) | Task 15 Step 1 | ✓ Evaluation arm (no extra build) |
| §7 Testing | Entity filter tests, cap invariant, degeneracy guard, etc. | Task 11-14 | ✓ Tests specified; some Snyk integration incomplete |
| §9 Out of scope | w_hub tuning, support/shrinkage | Deferred | ✓ Acknowledged |

**Coverage verdict: COMPLETE.** Every spec requirement has a corresponding plan task or is explicitly deferred.

---

## Structure and Size Recommendations

**High-quality structure; minimal changes needed:**

1. **Architecture review document.**
   - **Issue:** §5 is stale and self-contradictory (marked superseded but then contains refuted claims).
   - **Recommendation:** Delete §5 in its entirety and replace with one paragraph:
     > §5 (analysis, overturned) — This section was reconstructed from an earlier session and contains measurements that the adjudication (`2026-07-21-scoring-adjudication.md`) has refuted or superseded. Do not cite figures from §5 directly; instead consult the adjudication's §5–§6 for the correct measurements and verdicts.
   - **Result:** Document becomes "narrative history only" (as banner claims) without contradicting the record.

2. **Phase 2 plan document.**
   - **Current state:** 3,465 lines, well-organized into 16 tasks with clear checkboxes and step-by-step instructions.
   - **Minor issue:** Timing from Task 1 Step 7 is referenced as "write it into the plan's Task 15 notes" but Task 15 has no dedicated timing field. Plan would benefit from a `.claude/build-timing.txt` or similar.
   - **Recommendation:** No split needed. The file is long but serves a single purpose (implementation guide) and is well-indexed by task number. Readability is good.

3. **Specifications (phase2-path-quality-design, stage3-frontend-design, alpha-design).**
   - These are properly scoped (one feature/stage each) and correctly cite the adjudication.
   - No restructuring recommended.

---

## Summary of Recommendations

**Priority 1 (before Phase 2 execution):**
- **Fix or quarantine architecture review §5.** The current state violates accuracy. Either delete and replace with a redirect to the adjudication, or add a prominent "SECTION RETRACTED" banner at the top of §5 with links to adjudication corrections.

**Priority 2 (during Phase 2 execution):**
- Ensure all new-code tasks (2–10) include Snyk scanning in their commit steps (Task 14 Step 6 does; others should too per global constraints line 20).
- Task 1 Step 7 timing should be captured to a discoverable location (currently requires manual context inference in Task 15).

**Priority 3 (post-Phase 2):**
- Revisit the ONE-RECORD-RULE in post-Phase-2 handoff documents. This project has now enforced it once; the habit must persist in future phases.

---

## High Findings Summary

**Execution risk: LOW.** The Phase 2 plan is well-structured and ready for implementation. No critical inconsistencies between spec and plan.

**Documentation risk: MEDIUM.** Architecture review §5 violates accuracy and the ONE-RECORD-RULE in ways that could mislead future readers or agents. This should be fixed before the project moves into other phases where old documents are consulted for context.

**Most important recommendation:** Replace architecture review §5 with a redirect to the adjudication. The section currently reads as current but describes a state the project has moved past and proven wrong.
