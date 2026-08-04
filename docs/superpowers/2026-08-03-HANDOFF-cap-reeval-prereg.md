# Handoff — the cap re-evaluation pre-registration, 2026-08-03

**Role: ⚠ SUPERSEDED 2026-08-03 (night) on next actions by
[`2026-08-03-HANDOFF-cap-reeval-exec-plan.md`](2026-08-03-HANDOFF-cap-reeval-exec-plan.md)**
— the execution plan it named as the next work has been written, reviewed and revised
(PR #69), and PR #68 has since MERGED (`cdf0033`), so its "merging PR #68 is the owner's
action" is discharged. Remains authoritative for the prereg track's internals and its
claims-not-to-revert. *(Original role:)* **ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-03-HANDOFF-featured-credit-filter.md`](2026-08-03-HANDOFF-featured-credit-filter.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff.** The track completed: the `CRE-` pre-registration authored
cold, reviewed twice pre-run, revised, frozen (`3d7b7d6`), the `WAV-` read run and
closed, and `CRE-AM1` appended on the owner's ruling (`eec67a8`). Nothing is in flight,
no port is listening, the tree is clean and pushed, draft **PR #68** carries the branch.
Reasoning:
[`2026-08-03-cap-reeval-prereg-execution-log.md`](2026-08-03-cap-reeval-prereg-execution-log.md).
Governing document:
[`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md)
(`CRE-`, one amendment).

## The next session's work: the execution plan

Write the plan that executes the `CRE-` prereg, reading it cold — the prereg governs
wherever the plan would disagree. Its §2 names **six harness-side dependencies** (none
in shipped code); `CRE-AM1` adds the vote-scramble companion but no new machinery
beyond it (`e_rel` is already implemented and instrument-verified in
`builder/analysis/2026-08-03-within-artist-votes/wav_read.py`). Stage order is fixed
(§4): `CRE-D3` and `CRE-D1` before any build, screens before any sweep, seams named.
**Merging PR #68 first is the owner's action** — the plan consumes a frozen document,
and the freeze is only durable once it is on `main`.

## Claims that must not be reverted

1. **The prereg's freeze point is `3d7b7d6`; §8 amendments govern from there.** Its §9
   is the revision record and carries two result-bearing disclosures — the `CRE-D1`
   direction (measured opposite to the owner's hypothesis; the confirmatory run's
   expected branch is "not supported") and the pricing prior (ramp inert on famous
   pairs at incumbent supply). **Do not tidy these disclosures away**, and do not read
   either as a prediction — both were measured before the design froze, and the
   document says so precisely so that cannot be mistaken later.
2. **The `WAV-` read is CLOSED as FAIL and stays closed.** `CRE-AM1` supersedes the
   consequence mapping's *product effect* on the owner's authority (the direction
   question was his column); it does not reopen, re-run or re-score the read. A future
   session must not "fix" `WAV-3` retroactively, and must not cite the `WGT-` "no
   evidence strength" clause against `CRE-AM1` — that clause governs the absolute
   scheme only, which is the correction to the owner's own recollection recorded in
   the amendment.
3. **The two deliberate divergences from the analyst's proposals are decisions, not
   oversights** (prereg §9): `CRE-C4`'s binding form is baseline-relative, and
   `CRE-C6`'s screen-out is arithmetic-impossibility, not ≥ 8 zero-supply pairs.
4. **The ramp bracket is 0.01/0.03 deliberately** — the drafted 0.05/0.15 sit in the
   measured dominating regime (critique F7). Do not "strengthen" the arms back.
5. **The closed-cell rule has exactly one carve-out**: `CRE-D3` runs pricing on
   (ALG-E × incumbent) as an instrument prior, barred from candidacy and winner logic.
   It does not reopen Track 3 or the parked DD-A2 decision.
6. **The critique record is frozen as-executed** (`builder/analysis/2026-08-03-cre-prereg-critique/`):
   the probe scripts are records, not maintained instruments, and the analyst report
   owns the figures it states. Do not edit them; a new measurement starts a new script.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout, including three deferral rows struck as
discharged), `docs/README.md` (rows for the prereg, this handoff, the execution log;
the featured-credit handoff's role line), `TEST-QUEUE.md` (new N/A entry), the
featured-credit handoff's role line, the `WAV-` README (closure banner + the owner-
ruling pointer), and the execution log through §8.

## What I know that is not in the durable record

- **The ALG-E capture in this session's scratchpad dies with the session** — by
  design; regeneration is byte-identical (~7.5 min) and the command is in the `WAV-`
  README. Nothing else transient survives worth naming: the two PR body/comment
  scratch files are spent.
- **The analyst's probe outputs were never captured as JSONs** — the report's tables
  are the only record of those figures, which its README states. If a CRE stage wants
  one of those numbers load-bearing, re-derive it inside the stage rather than citing
  the critique as a data source.
- **The review-dispatch split that worked**: claims-vs-repo and quantitative-critique
  produced zero duplicate findings across twenty-two. Recorded in the log §3; worth
  reusing when the execution plan is reviewed.
- **PR #68 is a draft and its body predates the revision** — the revision, `WAV-` and
  `CRE-AM1` are in comments. Whoever readies it for merge should refresh the body from
  the execution log rather than the original description.
