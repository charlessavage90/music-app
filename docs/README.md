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

- ⛔ **Phase 1 is PAUSED, 2026-07-22.** A defect was found in the connectivity structure of
  the **adopted** graph artifact — the most popular artists are among the *least* connected
  (The Beatles degree 7; Radiohead absent from the graph), and the degree-based hub metric
  does **not** mean "famous." **Read
  [`superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`](superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md)
  §2 before any Phase 1 work, and before trusting any `hubfrac`/payload figure anywhere.**
  The owner's decision on how to handle it was outstanding when work stopped.
- **Gate 1 (personal use).** Phase 2 (path quality) is **COMPLETE**, 2026-07-22. All 16
  tasks executed on branch `phase2-path-quality`. The blind listening test was run and the
  owner adopted the **`capfix`** arm — `cap_strategy="mutual_knn"`,
  `similarity_rescale="p99_log_clip"`, `similarity_damping=0.0`. See execution log §16
  (verdict) and §17 (adoption). **That adoption is not overturned** — but §2 of the Phase 1
  log is information that was not available when it was made.
- **Phase 1 leads with C3** — `w_floor` is a no-op and `known` degrades to a bare hard
  exclusion, a *pathfinding* defect rather than the UX item it was filed as — then clips
  (C1, C2), then frontend UX. **Partially investigated, nothing implemented; see the Phase 1
  log §3 and §6.** Two items
  carry in from Phase 2 with success conditions; see the roadmap's Phase 1 section.
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
| `../CLAUDE.md` | How to work in this repo: commands, architecture, conventions. |

### Active

| Document | Covers |
|---|---|
| `superpowers/2026-07-21-phase2-execution-log.md` | **The audit trail for Phase 2, and the freshest truth in this directory.** Every decision and why, defects found in the plan and in the prior record, gate pass/fail state, open items, deferred findings. **§16 is the blind-test verdict; §17 the adoption; §18 the closeout triage; §19 the fixture-seed defect found after closeout — which supersedes §17's checksums.** Where any other document disagrees with §16–19, this wins. Marked ACTIVE rather than COMPLETE because Phase 1 consumes its carried-forward items. |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | *(also listed as Authoritative)* Its **Phase 1 section is the live work queue**, including the two items carried in from Phase 2 with success conditions. |
| `superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md` | ⛔ **Start here for Phase 1, and read §2 before any implementation.** One document by design: the **graph-structure defect that halted the work** (§2 — facts, discovery mechanism, suspected cause; deliberately no solutioning) **plus** the full Phase 1 progress record (§3 — including two independent ML-analyst reviews and what each overturned), what is closed (§4), artifacts (§5), and state of play (§6). Splitting it would let the progress record be picked up without the context that stopped it. **Owns its figures** — cite from here, do not restate. |
| `superpowers/2026-07-22-HANDOFF-phase1.md` | Written at Phase 2 closeout for a cold session: what was overturned and must not be reverted, and what the previous session knew that is not otherwise in the record. **Superseded on Phase 1 status by the log above** — that document governs where they disagree. Still valid on Phase 2 outcomes. |
| `superpowers/TEST-QUEUE.md` | The async **use-the-app queue**. `closeout` appends; `session-start` reads it and flags stale entries. Catches the defect class tests structurally cannot. |

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
