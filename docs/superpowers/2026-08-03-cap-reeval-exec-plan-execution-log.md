# Execution log — the cap re-evaluation EXECUTION PLAN track, 2026-08-03 (night)

**Role: RETAINED EXECUTION LOG.** Owns no figures — the plan-review measurements live in
`builder/analysis/2026-08-03-cre-plan-critique/` (whose analyst report owns what it
states), and the plan's own claims-vs-repo results live in the plan's "Verification
record" section. Reasoning and decisions only.

## §1 — Scope, and what stands

One session: verified the frozen `CRE-` prereg against the repo, authored the execution
plan (`plans/2026-08-03-cap-reeval-execution-plan.md`, draft PR #69), dispatched the
`ml-graph-analyst` for a quantitative plan review at the owner's instruction, and folded
all sixteen surviving findings in pre-run. No CRE stage ran; no code was executed; the
diff is documentation plus the frozen critique probes. The prereg is untouched — the one
prereg change the review forced (`CRE-AM2`) is *specified* in the plan and committed by
the **executor** at T1 Step 2, so its git timestamp sits on the run branch, before any
result exists.

## §2 — The verification pass, and the two findings that shaped the plan

Every file, function, config value and commit the prereg names resolves (plan
§Verification record — the claims-vs-repo half of the review split, run by the authoring
session during authoring). Two findings were load-bearing:

- **`cb_build_variants._assemble` is deliberately frozen pre-drop** (its own docstring).
  So the cleaned substrates get a **new** assembly mirror — and because the live
  pipeline's defaults now *are* the cleaned MK50 cell, the mirror is gated
  byte-identically against a direct `build_from_archive` run (green ×2 archives, red at
  k=49). The gate is what makes the copy trustworthy; no transcription is trusted.
- **`fame_frame()` (`tas_common` / `cb_metrics`) is the retired currency.** It is barred
  from every CRE module by name, in the plan's global constraints. The ruler is
  `fi_stats.Frame` over the adopted frame + union snapshot, imported not copied.

## §3 — The executor pins

The prereg left a small number of device-level details to the executor; the plan fixes
each pre-run in its own section ("Decisions this plan fixes", pins 1–9 after revision),
each with a committed precedent. The reasoning lives there, not here. The design rule
followed: **a pin is recorded where the executor will read it, with the reason attached,
before any result can bias it** — the same discipline as a pre-registration, one level
down.

## §4 — The review dispatch, and one deviation from the recorded split

The prereg handoff recommended reusing the two-dispatch split (claims-vs-repo +
quantitative critique; zero duplicate findings across twenty-two). **Deviation, with
reasoning:** the claims-vs-repo half was run by the authoring session *during* authoring
— the plan could not have been written without it, and its results are the plan's own
Verification record — so only the quantitative half was dispatched, with an explicit
instruction not to repeat the other half or re-raise findings the prereg's §9 already
folded. The halves stayed disjoint by construction rather than by luck.

Outcome: **1 BLOCKING, 7 MATERIAL, 8 minor, 9 verified-clean** (the report owns the
figures). All sixteen surviving findings folded into the plan in one revision
(`da9e49e`); the plan's own Revision record maps each finding to its change and records
the two deliberate divergences from the analyst's exact proposals — the never-fetched
device price pinned at the neutral prior rather than left open, and `CRE-AM2` written
pre-run rather than stopping mid-run at the contradiction.

## §5 — The defect class this session contributed, named so it transfers

The blocking finding (B1) was this session's own: `assert_toll_arithmetic` computed the
same closed form on both sides of its comparison and **could not fail** — and it was the
only device check `CRE-D3` had, on the read whose expected null feeds `CRE-R0`'s wording
verbatim. The general shape: **an instrument check authored beside the instrument it
checks trends tautological, because the author reaches for the formula they just wrote.**
The fix pattern that works: the check must compare against a quantity produced by a
*different mechanism* — here, the search's own accumulated cost (`stats["path_cost"]`),
which the decomposition does not share. This is the `WAV-0d` / `TAS-AM5b` lesson
recurring on the author's side of the fence: a green from a check never shown able to go
red is not evidence, and a check that *cannot* go red is the limiting case. The plan now
also requires the red half in T2's tests (break the breakdown, assert `SystemExit`).

## §6 — Execution mode, and the owner's model ruling

Recommended and concurred (conversation, 2026-08-03 night): **fresh sessions on Opus,
executing inline (`superpowers:executing-plans`), retiring at the plan's three seams** —
not subagent-driven, and not this session switched mid-stream. Reasons of record: the
tasks are strictly sequential, so fan-out buys nothing; subagent execution keeps the
dispatching model as the controller, which defeats the owner's model preference and
pays the expensive model for judgment it wanted moved; the plan was written for a cold
executor, so a fresh session loses nothing; and the seams already exist as designed
session boundaries — the findings note at Seam 3 **must** be a session that did not run
the sweeps. Sequence: owner merges PR #69, then a fresh Opus session branches
`cap-reeval-run` off `main`; its first commit is `CRE-AM2`.

## §7 — Corrections to the prior record

- `NEXT.md` stated the owner's one action was merging draft PR #68; that merge was
  already on `main` (`cdf0033`) when this session started. Corrected at this closeout —
  the stale sentence survived because the merge happened between the prereg session's
  closeout and this session's start, which is exactly the window `NEXT.md`'s own
  role-header rule (fresher record wins) exists for.
- The plan's first-commit runtime estimates ("~8–15 min per capped cell") were wrong by
  roughly two orders of magnitude, conservative direction; replaced with the analyst's
  measurements (critique V1) in the revision. Recorded here because a future session
  scheduling against plan prose should know the estimates are measured, not guessed —
  and measured on **pre-drop** cells, the critique's stated weakest link.

## §8 — Operational measurements with no other home

- The analyst dispatch: ~242k subagent tokens, 35 tool uses, ~22 minutes, on the
  agent-definition default model. It wrote five probe scripts + JSONs + README; its
  report text was returned in-response (its output rules bar report files) and committed
  verbatim by the controller with provenance stated at its head.
- The plan itself: 1,251 lines at first commit, +371/−84 at revision.

## §9 — Closeout outcomes (SS16)

- **A3**: every deferral this track created has an address inside the plan (CRE-AM2 at
  T1 Step 2; the findings note at Seam 3; the C6-heuristic caveat assigned to the
  findings note's weakest-link section). One prior condition found due: `NEXT.md`'s
  PR #68 action — discharged, struck at this closeout (§7).
- **A4**: no config knob added — not applicable, stated rather than skipped.
- **A5**: ports 8000/5173/8138/8139 all empty; this session started no process and left
  none. Nothing queued needs a server (C1 entry is N/A).
- **B2/B3**: no importable module and no test was created (the plan *contains* test code;
  nothing executed) — travel with the work to the executor, per the mid-flight scaling
  note's logic applied to a not-yet-started artifact.
- **B5**: `NEXT.md`, `TEST-QUEUE.md`, `docs/README.md` updated at this closeout;
  `.claude/` and `memory/` untouched by this work and re-checked untouched.
- **D1**: tree clean; diff verified docs + frozen probes only (13 files).
- **D4**: suites not run, with the reason on the record rather than asserted green: the
  diff contains no file any suite collects — documentation plus `builder/analysis/`
  probe scripts, which `testpaths = ["tests"]` excludes by the owner's 2026-08-01
  ruling. No code path any test exercises changed.
- **D6**: standing layer delta **exactly 0 on both units** — unconditional 44,494 chars,
  conditional 2,155 lines, both equal to the figures at the previous closeout
  (2026-08-03 later). This session touched neither `CLAUDE.md`, `.claude/`, nor
  `memory/`.
- **B1**: lint + doc-auditor outcome recorded below after the run.

### §9a — B1 outcome

`docs-lint.sh`: **hard checks passed**; its CAND list (small decimals in many
specs/plans) was handed to the auditor, which confirmed the new files' instances are
thresholds **owned by the `CRE-` prereg** (ramp settings, the §9 disclosure direction,
the `C2` margin), not restatements of the adjudication's figures. `doc-auditor`
(scoped to this track's diff plus citing documents, told the lint ran): **CLEAN — no
HIGH or MEDIUM findings.** Verified explicitly: the supersession chain reads both
directions; no document claims `CRE-AM2` is already appended (grep of the spec: zero
matches — correct, it is the executor's first commit); no document still owes PR #68;
the review-outcome counts and the two divergences agree across plan, handoff, log and
map rows; cold-start navigation answers all six entry questions without dead ends; no
identifier collisions among the new `CRE-T` series and the critique's `B/M/m/V`
labels.
