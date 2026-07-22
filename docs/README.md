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

- **Gate 1 (personal use).** Phase 2 (path quality) is **nearly complete** — Tasks 0–15
  executed on branch `phase2-path-quality` (open PR). Phase 1 (clips, bypass, frontend UX)
  is not yet planned.
- **Next action:** run the blind listening test in
  `superpowers/2026-07-22-HANDOFF-blind-test.md`, which decides the adopted arm. Then
  Task 16 (adopt), then the `closeout` skill.
- The governing plan is `superpowers/plans/2026-07-22-phase2-revised-plan.md`, which
  supersedes the remaining tasks of the 2026-07-21 plan.

---

## Every document, by role

### Authoritative

| Document | Covers |
|---|---|
| `superpowers/findings/2026-07-21-scoring-adjudication.md` | **All** scoring, hub-seeking, and path-quality figures. The single quantitative record. |
| `superpowers/findings/2026-07-22-phase2-sweep-results.md` | Every figure from the Phase 2 six-arm sweep. Owns its numbers; linked from the adjudication's §6 (claims 41–45). |
| `superpowers/plans/2026-07-21-alpha-rollout-roadmap.md` | Gate structure and phase ordering. Its C4 is a pointer only — it holds no figures. |
| `../CLAUDE.md` | How to work in this repo: commands, architecture, conventions. |

### Active

| Document | Covers |
|---|---|
| `superpowers/specs/2026-07-21-phase2-path-quality-design.md` | Phase 2 design. Supersedes the roadmap's Phase 2 content only. |
| `superpowers/plans/2026-07-21-phase2-path-quality.md` | Phase 2 implementation, 16 tasks. **Execute in a fresh session.** Several of its inline test fixtures are arithmetically wrong — see the execution log §3 before trusting one. |
| `superpowers/2026-07-22-HANDOFF-blind-test.md` | **Next action:** run the blind listening test that decides Phase 2's adopted arm. Written for a session with no prior context. Delete once the verdict is recorded and Task 16 is done. |
| `superpowers/2026-07-21-phase2-execution-log.md` | **Running record of Phase 2 execution:** every decision and why, defects found in the plan and in the prior record, gate pass/fail state, open items, and deferred review findings. Read it before continuing or auditing Phase 2. |

### Complete

| Document | Covers |
|---|---|
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
