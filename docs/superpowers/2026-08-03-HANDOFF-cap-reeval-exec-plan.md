# Handoff — the cap re-evaluation execution plan, 2026-08-03 (night)

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-03-HANDOFF-cap-reeval-prereg.md`](2026-08-03-HANDOFF-cap-reeval-prereg.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff.** The track completed: the frozen prereg verified accurate
against the repo, the execution plan authored
([`plans/2026-08-03-cap-reeval-execution-plan.md`](plans/2026-08-03-cap-reeval-execution-plan.md)),
reviewed quantitatively by the `ml-graph-analyst` at the owner's instruction
(record: `builder/analysis/2026-08-03-cre-plan-critique/`), and revised pre-run with all
sixteen surviving findings folded in (`da9e49e`). Nothing is in flight, no port is
listening, the tree is clean and pushed, draft **PR #69** carries the branch. Reasoning:
[`2026-08-03-cap-reeval-exec-plan-execution-log.md`](2026-08-03-cap-reeval-exec-plan-execution-log.md).

## The next session's work: execute the plan

**After the owner merges PR #69** (the executor consumes the plan and the critique
record; durability requires `main`): a **fresh session on Opus** — the owner's explicit
model ruling, 2026-08-03 — branches `cap-reeval-run` off `main` and executes the plan
**inline** (`superpowers:executing-plans`), retiring at the plan's three seams. Not
subagent-driven: the tasks are sequential and the owner wants Opus doing the judgment,
not just the typing (log §6). The prereg governs wherever the plan disagrees; the plan
governs operationally. **The first commit of execution is `CRE-AM2`** (plan T1 Step 2 —
text is in the plan verbatim, appended to the prereg's §8 before any stage runs).

## Claims that must not be reverted

1. **The plan's revision (`da9e49e`) is review output, not drift.** Its Revision record
   maps every analyst finding to its change. Do not "simplify" the S2 deletion key back
   to a bare product (M4), un-split pin 2's two unmeasured classes (M2), or restore the
   first-draft toll check — it was a tautology (B1), and the replacement's value is that
   it compares against the search's own accumulated cost.
2. **The two divergences from the analyst's exact proposals are decisions with recorded
   reasons** (plan Revision record): never-fetched nodes priced at the neutral 0.5, and
   `CRE-AM2` written pre-run instead of a mid-run stop.
3. **`CRE-AM2` is specified but NOT yet appended.** The prereg on `main` does not carry
   it until the executor's first commit. Do not treat the plan's quotation of it as
   already-appended, and do not append it outside the run branch's T1 Step 2 — the
   commit timestamp on the run branch, before any result, is the point.
4. **The critique record is frozen as-executed** (`builder/analysis/2026-08-03-cre-plan-critique/`):
   probe scripts are records, not maintained instruments; the report owns its figures;
   its cell-level counts were measured on **pre-drop** Track B builds (its stated
   weakest link) and must be quoted with that provenance.
5. **The plan's runtime prose is measured, not estimated** (critique V1) — and measured
   pre-drop. Do not restore the first-draft estimates; do not schedule against either
   without noting the substrate caveat.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `TEST-QUEUE.md` (new N/A entry),
`docs/README.md` (rows for the plan, the critique record, this handoff and the log; the
prereg handoff's role line), the prereg handoff's role line itself, and the retained log
through §9.

## What I know that is not in the durable record

- Nothing load-bearing. The owner's Opus ruling and the execution-mode reasoning are in
  the log (§6); the analyst's report text is committed verbatim with provenance; the
  subagent's transcript dies with this session but its durable outputs (probes, JSONs,
  report) are all committed.
- One convenience worth a line: the owner saved **Fable** as his default model earlier
  on 2026-08-03, so the executing session needs `/model opus` explicitly.
