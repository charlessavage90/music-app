# Documentation map

**Read this before citing any document in `docs/`.** It says which documents are
authoritative, which are historical, and which must never be used as context.

Every document here has exactly one **role**. The role determines how much you can
trust it and whether you may act on it.

| Role | Meaning |
|---|---|
| **AUTHORITATIVE** | Current and correct. Cite it. If another document disagrees, this one wins. |
| **ACTIVE** | Work in progress. Current intent, but not yet reality. |
| **COMPLETE** | Describes work that shipped. Accurate as history; may not describe the code today. |
| **HISTORICAL** | Superseded. Retained so the reasoning can be audited. **Do not cite. Do not act on.** |
| **NARRATIVE** | Written for humans, not for engineering. **Never use as context for development.** |
| **EXTERNAL** | Not ours. Third-party reference material. **Not project documentation.** |

---

## The one rule that matters most

**Measured figures about similarity scoring, hub-seeking, and path quality live in
exactly one file:**

> ### `superpowers/findings/2026-07-21-scoring-adjudication.md`

Every other document **cites it by section number and does not restate its numbers.**
Its **§6** is a table marking 27 prior claims as upheld, overturned, or unresolved —
check there before trusting any scoring claim you find anywhere else.

This rule exists because five documents each kept their own copy of the same figures
and drifted into three mutually contradictory positions. Two separate analyses were
invalidated before anyone noticed. **Restating a correct number is still a violation** —
that is how the drift began.

---

## Current state

- ⛔ **The owner decided 2026-07-23: repair + retune. Track 1 is DONE and adopted; Track 2
  is next.** The defect record and diagnosis below remain essential reading before touching
  Phase 1 — the three conflated quantities it warns about are still live hazards.
  **Read [`superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`](superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md)
  §2 before any Phase 1 work — and read §2.12 first, because it retracts a central claim of
  §2.9 and corrects §2.10 and §2.11.**
  - **What is settled.** Two real defects in the **adopted-at-the-time** artifact (figures
    owned by the sections cited, not restated here): the most popular artists were among
    the least connected, caused by an MBID tie-break over p99-clipped scores (§2.8); and
    famous→obscure edges were depleted well below a structure-preserving null, caused by
    the mutual-k-NN reciprocity rule (§2.10). Routed paths never present an artist below a
    very high popularity percentile, at any bypass depth, on either graph tested (§2.9).
  - **What it is NOT.** Not primarily a graph problem. Obscure artists are a small, fixed
    number of hops from every famous artist tested, and even the most-connected famous
    artists have a handful of admissible `known` substitutes (exact counts: §2.12).
    **§2.12 concludes this is a cost-function problem** — the router prices the exits
    correctly and declines them.
  - **Three quantities that are not interchangeable** and have each caused an error here:
    **degree ≠ fame** (§2.6), **popularity ≠ fame** at the top of the distribution (§2.11),
    and **raw popularity ≠ percentile** (§2.12). Do not trust any `hubfrac`/payload figure,
    and check which currency a claim is in before acting on it.
  - **Decided 2026-07-23:** the owner chose **repair + retune** — governing design
    `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md`; its §1
    also records the nine-names verdict (in-graph popularity ≠ fame at the top,
    confirmed) and the owner's relaxation of the listening-test prohibition.
  - **Track 1 is DONE, 2026-07-23: the §2.8 tie-break is fixed and the rebuilt artifact
    is adopted.** The app now routes on `graph-t15-tiebreakfix.bin` — identity and
    verification in `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` (the
    authoritative record for the adopted artifact's checksum). Radiohead is back;
    famous-artist neighbourhoods are score-ranked, not MBID-ranked. Track 2 (cost-function
    retune) is next and has its own plan.
- **Gate 1 (personal use).** Phase 2 (path quality) is **COMPLETE**, 2026-07-22. All 16
  tasks executed on branch `phase2-path-quality`. The blind listening test was run and the
  owner adopted the **`capfix`** arm — `cap_strategy="mutual_knn"`,
  `similarity_rescale="p99_log_clip"`, `similarity_damping=0.0`. See execution log §16
  (verdict) and §17 (adoption). **That adoption is not overturned** — but §2 of the Phase 1
  log is information that was not available when it was made.
- **Phase 1 resumed 2026-07-23; Track 1 is done and adopted, Track 2 is next.** C3
  (`w_floor` is a no-op; `known` degrades to a bare hard exclusion — a *pathfinding*
  defect rather than the UX item it was filed as) is now folded into Track 2's
  cost-function retune, per
  `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §4. Current
  sequencing: see that spec and
  `superpowers/2026-07-23-repair-and-retune-execution-log.md`. Clips (C1, C2) and frontend
  UX remain queued behind it. Two items carry in from Phase 2 with success conditions; see
  the roadmap's Phase 1 section.
- **Two Phase 2 predictions did not survive measurement**, and older prose still asserts
  them. Damping ("C4") was tested at 0.25 / 0.5 / 0.75 and **rejected** — the undamped arm
  won. Neighbour-set Jaccard was **not** adopted as the primary objective; the
  overlap-family metrics sign-flip between slices at these effect sizes (adjudication §6
  claims 41–42). The p99 ceiling defect **survives adoption** and is carried to Phase 1.
- `superpowers/plans/2026-07-22-phase2-revised-plan.md` governed Tasks 14–16 and supersedes
  the remaining tasks of the 2026-07-21 plan. Both are now historical.

---

## Every document, by role

### Authoritative

| Document | Covers |
|---|---|
| `superpowers/findings/2026-07-21-scoring-adjudication.md` | **All** scoring, hub-seeking, and path-quality figures. The single quantitative record. |
| `superpowers/WHAT-GOOD-LOOKS-LIKE.md` | **What the owner means by a better path.** Calibration for the blind listening test — this project's strongest evidence class, which decided the graph twice where the offline metrics decided it zero times. Read before interpreting any listening verdict. |
| `superpowers/findings/2026-07-22-phase2-sweep-results.md` | Every figure from the Phase 2 six-arm sweep. Owns its numbers; linked from the adjudication's §6 (claims 41–45). |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | Gate structure and phase ordering. Its C4 is a pointer only — it holds no figures. |
| `superpowers/findings/2026-07-23-tiebreak-fix-adoption.md` | Identity (sha256) and verification record of the **adopted** 75k artifact, post tie-break fix. |
| `superpowers/findings/2026-07-22-configuration-model-null.md` | Authoritative for its own figures — the exact configuration-model null referenced by Phase 1 log §2.10/§7.1 item 1. |
| `../CLAUDE.md` | How to work in this repo: commands, architecture, conventions. |

### Active

| Document | Covers |
|---|---|
| `superpowers/2026-07-21-phase2-execution-log.md` | **The audit trail for Phase 2.** Every decision and why, defects found in the plan and in the prior record, gate pass/fail state, open items, deferred findings. **§16 is the blind-test verdict; §17 the adoption; §18 the closeout triage; §19 the fixture-seed defect found after closeout — which supersedes §17's checksums.** Where any other document disagrees with §16–19 **on Phase 2**, this wins. **No longer the freshest truth in this directory** — as of 2026-07-23 that is `2026-07-23-repair-and-retune-execution-log.md` and `findings/2026-07-23-tiebreak-fix-adoption.md`, which govern current status and the adopted artifact. Marked ACTIVE rather than COMPLETE because Phase 1 consumes its carried-forward items. |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | *(also listed as Authoritative)* Its Phase 1 section gives the **phase structure**, including the two items carried in from Phase 2 with success conditions; current sequencing within Phase 1 is governed by the 2026-07-23 repair+retune spec, not this document. |
| `superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md` | ⛔ **Start here for Phase 1, and read §2 before any implementation.** One document by design: the **graph-structure defect that halted the work** (§2 — facts, discovery mechanism, suspected cause; deliberately no solutioning) **plus** the full Phase 1 progress record (§3 — including two independent ML-analyst reviews and what each overturned), what is closed (§4), artifacts (§5), and state of play (§6). Splitting it would let the progress record be picked up without the context that stopped it. **Owns its figures** — cite from here, do not restate. |
| `superpowers/2026-07-22-HANDOFF-phase1.md` | Written at Phase 2 closeout for a cold session: what was overturned and must not be reverted, and what the previous session knew that is not otherwise in the record. **Superseded on Phase 1 status by the log above** — that document governs where they disagree. Still valid on Phase 2 outcomes. |
| `superpowers/TEST-QUEUE.md` | The async **use-the-app queue**. `closeout` appends; `session-start` reads it and flags stale entries. Catches the defect class tests structurally cannot. |
| `superpowers/specs/2026-07-23-defect-remediation-and-cost-retune-design.md` | **The governing design for resuming Phase 1** (owner-approved 2026-07-23). Track 1: builder fix for the §2.8 tie-break, rebuild, adopt by structural equivalence. Track 2: cost-function retune (currencies included) on the repaired graph, `known` mechanism, one blind listen. Records the owner's 2026-07-23 decisions in §1. |
| `superpowers/2026-07-23-repair-and-retune-execution-log.md` | Retained execution log for the repair+retune work. Track 1 record, the pre-Track-2 guards, and Track 2 continues it. |
| `superpowers/specs/2026-07-23-track2-preregistration.md` | **The Track 2 pre-registration.** Fixes the factor table, primary outcome, effect sizes, pair set, and the read of every possible result *including the null*, before any arm runs — the commit timestamp is the evidence it came first. Where it disagrees with the repair+retune design spec it says so inline (its §8 indexes the five disagreements); those are design corrections, not scope changes. Also the worked example for two CLAUDE.md rules (dormant-term check, pre-registration gate). Its §7 lists prerequisites P1–P8, which block running arms, not writing the plan. |
| `superpowers/plans/2026-07-23-pre-track2-guards.md` | Six structural guards (G1–G6) that had to land between the pre-registration and the Track 2 sweep. **Executed 2026-07-23; do not execute again.** Outcomes in the repair+retune execution log under "Pre-Track-2 guards". |

### Complete

| Document | Covers |
|---|---|
| `superpowers/specs/2026-07-21-phase2-path-quality-design.md` | Phase 2 design. **IMPLEMENTED and adopted 2026-07-22** (`capfix`); §8 risk 4 discharged. Supersedes the roadmap's Phase 2 content only. Its open questions were answered by the sweep — do not read it as a live agenda. |
| `superpowers/plans/2026-07-21-phase2-path-quality.md` | Phase 2 implementation, 16 tasks. **All executed; do not execute again.** Tasks 14–16 were superseded mid-flight by the revised plan below. Several of its inline test fixtures are arithmetically wrong — see the execution log §3 before trusting one. |
| `superpowers/plans/2026-07-22-phase2-revised-plan.md` | The mid-flight amendment governing Phase 2 Tasks 14–16, written by the owner after a full review. **Retained as the record of *why* the last three tasks differ from the original plan** — its §6 is what reclassified C3 into Phase 1. |
| `superpowers/specs/2026-07-19-artist-path-alpha-design.md` | Original alpha design. Still the reference for determinism (§9) and the `APG1` format. |
| `superpowers/specs/2026-07-20-stage3-web-frontend-design.md` | Frontend design. |
| `superpowers/plans/2026-07-19-graph-builder.md` | Builder implementation. Shipped. |
| `superpowers/plans/2026-07-20-path-engine-api.md` | API implementation. Shipped. |
| `superpowers/plans/2026-07-20-stage3-web-frontend.md` | Frontend implementation. Shipped. |
| `superpowers/findings/2026-07-22-doc-audit-context-layer.md` | Documentation audit, navigation layer. |
| `superpowers/findings/2026-07-22-doc-audit-technical-record.md` | Documentation audit, specs and plans. |
| `superpowers/plans/2026-07-23-track1-tiebreak-remediation.md` | Track 1 implementation plan. **Executed 2026-07-23; do not execute again.** Outcomes in `2026-07-23-repair-and-retune-execution-log.md`. |
| `superpowers/specs/2026-07-22-c3-bypass-diagnostic-experiment.md` | C3 diagnostic protocol. **Executed** (Stage 0); Stage 1 superseded by Track 2. Results in the Phase 1 log §3. |
| `superpowers/specs/2026-07-22-c3-known-mechanism-blind-listen.md` | C3 `known`-mechanism blind-listen protocol. **Executed**, verdicts recorded. Results in the Phase 1 log §3.6–§3.9; the A-vs-C re-run condition is the 2026-07-23 spec §4.4. |

### Partly historical — check before citing

| Document | Status |
|---|---|
| `superpowers/findings/2026-07-19-listenbrainz-probe.md` | **Superseded for scoring and normalisation** (it describes per-artist normalisation, deleted in `284366c`). Everything else — endpoint schema, rate limits, the 1,000-artist sitewide cap, the §6d–6f popularity-source eliminations — is still valid and load-bearing. |
| `superpowers/findings/2026-07-21-architecture-review-and-path-baseline.md` | **Superseded for scoring and metrics.** Retained as narrative history of how the reviews unfolded. Its architect and QA findings in §1 (clip 500s, artifact length validation, sync boto3 on the event loop) are **not** superseded and remain actionable. |

### Narrative — never use as context

| Document | Status |
|---|---|
| `how-we-map-similar-artists.md` | A dev-blog journal of the modelling journey, written for humans. **Never cite it, never use it as context, never instruct development from it.** It is not maintained to the standard of project context and will lag reality. Update it when there is major progress worth journalling; correct factual errors when found. |

### External — not project documentation

| Document | Status |
|---|---|
| `reference/` | Third-party material consulted during early planning. **Not project documentation and not for routine context.** See `reference/README.md`. |

---

## Where else information lives

- **Persistent memory** — outside the repo, loaded into every session, at
  `~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app/memory/`. The
  `MEMORY.md` *inside that directory* is the index; each sibling file holds one fact.
  Memory holds **pointers and working preferences, not figures**.
- **`.claude/agents/ml-graph-analyst.md`** — a reusable analysis-only subagent for graph,
  scoring, and metric questions. It has no `Edit` tool by design.
- **The code is the truth about the code.** Where a document and the source disagree
  about behaviour, the source wins — and the document is a defect to be fixed.

---

## Adding a document

State its role in the first ten lines. Add it to the table above. If it supersedes
something, put a banner on what it supersedes **and mark the superseded claims inline**,
not only at the top of the file — a reader who lands mid-document never sees the banner.
