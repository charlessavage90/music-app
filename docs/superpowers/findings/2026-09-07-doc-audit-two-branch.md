# Doc audit — the `DCF-` and `LBD-` branches, together, 2026-09-07

**Role: ACTIVE — the `doc-auditor` report for `closeout` B1 on PR #108, widened to cover
PR #109 as well.** Filed here rather than at `docs/` root to match the seven prior
`doc-audit-*` reports. **Discharges the success condition** recorded in
[`../2026-09-07-dcf-degree-ceiling-execution-log.md`](../2026-09-07-dcf-degree-ceiling-execution-log.md)
§6, where B1 was recorded as partially run after a first attempt terminated on a rate limit.

**Why two branches in one report:** the two sessions ran concurrently and each deliberately
avoided reading the other, to keep the `LBD-` pre-registration independent of the `DCF-`
measurement. That independence was correct — and it meant nobody had ever checked the two
diffs against each other.

> ## ⚠ ONE FINDING IN THIS REPORT IS WRONG. Verified before filing; corrected here rather
> than edited out of the body below.
>
> The report states that the `NEXT.md` collision means **"whichever merges second will revert
> the DCF correction"**, that **"automated merge will produce incorrect documentation"**, and
> recommends **manually resolving on `main` before either PR merges**. All three are wrong:
>
> - **Git conflicts on this; it does not silently pick a side.** Verified with
>   `git merge-tree --write-tree origin/lb-dump-exploration origin/dcf-degree-ceiling-falsifier`,
>   which reports `CONFLICT (content)` in **both** `docs/superpowers/NEXT.md` and
>   `docs/README.md`. The merge stops and a human resolves. Nothing is reverted silently.
> - **Resolving on `main` is not available here.** Nothing is committed directly to `main` on
>   this project (`CLAUDE.md`, "How work lands"); the resolution belongs in the second PR.
> - **The underlying risk is real and the remedy is different:** merge `LBD-` (#109) first —
>   which preserves the pre-registration's "committed before results existed" property — then
>   resolve the conflict inside `DCF-` (#108), keeping the corrected wording.
>
> **Everything else in this report stands**, including both HIGH cross-branch findings, the
> identifier census, and the Check J structural gap.

---

## Summary

Two HIGH-severity cross-branch contradictions exist that will mislead readers when merged:

1. **LBD-X1 claims the degree ceiling's effect on the added set is "genuinely unmeasured", but DCF measures exactly that effect, making the claim stale.** This reaches two documents: the pre-registration and docs/README.md's pre-registration row.

2. **LBD's NEXT.md still carries the uncorrected claim "most of today's sparsity is attributable to our own degree ceiling", but DCF has measured it as the minority cause.** Both branches edit this section and will collide on merge; whichever merges second will revert the DCF correction.

Both contradictions flow from concurrent sessions—one deliberately read-blind of the other—and each branch is internally consistent. Merge requires manual resolution and amendment of LBD's pre-registration to reflect DCF's measurement.

## Coverage statement

**Scope:** Git diffs between `main` and each branch, plus all documents citing files either diff changes.

**Read in full:**
- `docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md` (LBD)
- `docs/superpowers/2026-09-07-dcf-degree-ceiling-execution-log.md` (DCF)
- `builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md` (DCF)
- `builder/analysis/2026-09-07-lbd-inputs/README.md` (LBD)
- All docs/superpowers/NEXT.md and docs/README.md diffs on both branches

**Skimmed for status/role only:** existing execution logs and plan documents.

**Not opened:** builder/analysis Python scripts (figures owner documents carry the findings).

**`scripts/docs-lint.sh` run:** Yes, DCF branch passed hard checks. Noted: lint does not scan `builder/analysis/`, so both new README files (DCF and LBD) had no mechanical checks until this audit.

## Findings table

| File | Line | Check | Severity | Issue | Suggested fix |
|---|---|---|---|---|---|
| `docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md` (LBD #109) | 199 | A | HIGH | LBD-X1 explicitly claims: "the ceiling's effect *on them* is genuinely unmeasured." DCF measures exactly that set and finds it is the minority cause (34.36% → 19.96% when ceiling raised), making this claim stale on merge. | On DCF merge, record amendment in §10: "2026-09-07 — ceiling's effect measured by DCF probe; was unknown, now recorded as minority cause of added-set sparsity." Cite `builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md` §4. Do not edit the pre-registration values; register the material change only. |
| `docs/README.md` (LBD #109) | 199 | A | HIGH | Row for `2026-09-07-lbd-fidelity-and-supply-preregistration.md` reads: "its effect on the added set is unmeasured — the two point opposite ways and neither is discharged." DCF measures this effect. Readers will find the stale row after merge. | Add forward-correction banner dated 2026-09-07 pointing to pre-registration's §10 as the register. Cite figures owner (`builder/analysis/.../README.md` §4) without restating numbers. |
| `docs/superpowers/NEXT.md` (LBD #109) | 105 | A, B | HIGH | LBD branch reads: "most of today's sparsity...is attributable to our own degree ceiling." DCF branch corrected to: "from a majority to a minority." Both edit same section; merge in either order reverts one correction. Current state: LBD's version is stale once DCF lands. | Resolve collision before either PR merges. On main, manually take DCF's version (the one with "⚠ CORRECTED 2026-09-07" banner). Then merge both PRs to the resolved main. Automated merge will produce incorrect documentation. |
| `docs/superpowers/NEXT.md` (DCF #108) | varies | A | HIGH | DCF added: "On merge it fires a condition the concurrent LBD pre-registration left for it — LBD-X1 claims the ceiling's effect on the added set is unmeasured, and this measures it." This condition is now owed at merge time. | No fix needed; recorded and deliberate. Before LBD Task 3 runs, confirm LBD-X1 has been amended and §10 records the change. |
| `docs/README.md` (LBD #109) | 392–393 | E | MEDIUM | LBD clarifies role markers to distinguish "current handoff for the LBD track" vs. "current handoff for LUX-4 track" vs. system-wide sequence. No contradiction with DCF. After merge, exactly two documents claim ACTIVE/CURRENT (one per track), and NEXT.md sequences them. | No fix required. Documentation is now accurate: two independent tracks exist, each with its own handoff. |
| `builder/analysis/2026-09-07-degree-ceiling-falsifier/README.md` (DCF #108) | 1–3 | F | LOW | Role marker and links correct. All relative links verify. | None. |
| `builder/analysis/2026-09-07-lbd-inputs/README.md` (LBD #109) | 1–3 | F | LOW | Role marker and links correct. All relative links verify. | None. |

## Identifier census (Check I)

| Identifier | Branch | Document | What it names | Collision? |
|---|---|---|---|---|
| LBD-A0–A4 | LBD | pre-registration | Five arms (control, cap removed, threshold floored, corner, pairing delta) | No |
| LBD-C1–C3 | LBD | pre-registration | Three criteria (archive match, added-set supply, pre-existing supply) | No |
| LBD-G1–G4 | LBD | pre-registration | Four gates (build success, gate structure, barred read, answered risk) | No |
| LBD-X1–X3 | LBD | pre-registration | Three named exposures (degree ceiling, population shift, drop-list difference) | No |
| LBD-D1–D8, LBD-P1–P2, LBD-R1–R2, LBD-R9 | LBD | various | Design decisions, probe results, read conditions | No |
| DCF- | DCF | multiple | Series name only; no numeric identifiers | No |
| CRS-C3, CRS-C4, CRS-C5 | DCF | README | Existing Track B criteria (cited, not defined) | No |
| CXR-P1, CXR-P2, CXR-M4, CXR-M5 | DCF | README | Existing CXA findings (cited, not defined) | No |

**Collision check:** LBD identifiers collision-checked on 2026-09-07 across every ref and found free. DCF uses only existing series. No identifier appears with two meanings within a branch or across branches.

**Opacity check (Check I2):** LBD pre-registration carries plain-language sentences for every arm and criterion in §0, §1, §4. Every identifier in owner-facing text uses both token and sentence. DCF README uses identifiers only with context. ✓

## Reads-of-results table (Check J)

**LBD pre-registration**

| Item | Status | Notes |
|---|---|---|
| An explicit run manifest exists | PARTIAL | §0 factor table present. Missing: explicit statement of which stages are conditional (pair-table vs. graph-level builds). |
| Stated in results section, not only design | FAIL | Run-stage facts (what's complete, what's conditional) are in §0 (design). §2 (reads) does not state "pair-table is complete; graph builds are future and barred for this question." Reader opening §2 cannot learn stage status from the pre-registration alone. |
| Every result branch names the run state it presupposes | FAIL | Pair-table (LBD-R1) and graph-level (LBD-R2) reads lack opening sentences naming their stage presuppositions. |
| Every branch reachable before design finishes says so | FAIL | Pair-table is reachable at Task 4; graph is not. §2 never states this separation. |
| Every run-preserving instruction has its own sentence | PARTIAL | Condition that graph builds are pending lives in design §9 (owner stop). Pre-registration §10 registers this as an amendment but doesn't restate it. Acceptable via pointer, but Check J exists to catch this shape. |
| Every gate and branch trigger carries its own effect size | PASS | Gates are boolean (build succeeds or fails); no threshold needed. ✓ |
| Every criterion, arm and branch carries a plain-language sentence | PASS | §0, §1, §4: all present. ✓ |

**Architectural issue:** The run's stage structure and conditionals are split across two documents (design + pre-registration). This is correct deference to the design as governing. However, a standalone pre-registration should restate the conditional structure in the reads section so a reader opening §2 learns what stages are complete and what await.

**DCF:** Descriptive measurement-only. No pre-registration. No Check J.

## Structure recommendations

1. **LBD pre-registration §2 (reads section) — add run-stage preamble:**
   Before LBD-R1, insert: "All five arms' pair tables have been built (Task 4). The graph-level validation is conditional pending the pair-table read's verdict. This section reads pair-table results; the graph-level read is future work and barred (§4) from this track's central question."
   
2. **On PR merge (before either branch merges):**
   Manually resolve NEXT.md collision in main by taking DCF's version (which corrects "mostly" to "minority"). Then merge both PRs. Automated merge will produce stale documentation.

3. **After merge, before LBD Task 3 runs:**
   Amend LBD-X1 via §10 entry: "2026-09-07 — ceiling's effect on added set measured by DCF probe (moved from unmeasured to measured: minority cause of sparsity). Pair-table LBD-C2 stands unchanged; graph-level read barred per §4."
   
4. **docs/README.md — no further edits needed for roles:**
   LBD branch already clarified track-specific handoffs. After merge, both rows will be correct and clear.

## Cross-branch consistency note

The two branches' contradictions are not defects in either branch alone; they are artifacts of deliberate read-independence. DCF ran measurement; LBD wrote pre-registration without reading DCF (to keep LBD-X1 independent). On merge, LBD's pre-registration becomes incomplete and NEXT.md contains two incompatible statements of the same fact. Both need amendment/resolution, and the necessary edits are structural (adding a preamble, resolving a collision, registering an amendment) rather than content rewrites.
