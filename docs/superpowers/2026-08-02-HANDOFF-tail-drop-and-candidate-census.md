# Handoff — drop-list wiring, harness repair and the candidate census, 2026-08-02

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-01-HANDOFF-no-release-tail.md`](2026-08-01-HANDOFF-no-release-tail.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff, not mid-flight.** Everything is committed and pushed, nothing is
in flight, no subagent is running, no background job survives, no port is listening, and
the tree is clean. Three pieces of work reached their end: the adopted drop rule is wired
into the builder (PR #62, merged), the divergence that wiring opened between the pipeline
and its probe mirrors is closed (PR #63, merged), and the candidate (`ALG-B`) population is
censused with its own drop list frozen (this branch).

Reasoning: [`2026-08-02-tail-drop-wiring-execution-log.md`](2026-08-02-tail-drop-wiring-execution-log.md).

## The six claims that must not be reverted

1. **The wiring deliberately contradicts the previous handoff's closing instruction.** That
   handoff said not to wire before the cap track resolved. The reasoning was examined,
   judged not to transfer, and the owner ruled to wire first — execution log §1. A
   successor will find that advice and must not "restore" it.
2. **`drop_no_release_tail` is an experimental control, never a shipping option.** Default
   on. It exists so an experiment can hold the drop constant in a factor table, and so
   frozen probes can be era-pinned. Both uses were exercised the day it landed.
3. **The probe mirrors must NOT gain the drop step.** Their value is byte-identical
   reproduction of committed cells. Track B's grid is all pre-drop and must be read that
   way. A post-drop comparison needs a *new* harness, never an edit to `cb_build_variants.py`.
4. **Track B's identity gate proves reproduction, not fidelity.** It pins the harness
   against shas it produced itself, so it structurally cannot detect the pipeline gaining a
   stage. Do not cite it as evidence the mirror matches the builder.
5. **No candidate-side hand sample** (owner, 2026-08-02). The rule is population-independent
   and a measured false-positive rate would change nothing, because no second refinement
   mechanism exists. Execution log §5. **Do not re-propose it on transferability grounds.**
6. **Both drop lists are dated snapshots** and must never be re-resolved at build time —
   the builder is offline by a hard rule and spec §9 requires byte-identical builds.

## Already updated — do not re-edit

`NEXT.md` (status block, the wiring row struck, two new rows, the ruling recorded),
`builder/analysis/README.md` (new section on the pipeline divergence), Track B's harness
docstrings, `TEST-QUEUE.md` (new entry), and this log. The `2026-08-01` handoff's role line
now names this one.

## What I know that is not otherwise in the durable record

- **The vacuous screen in §3 was my own error, and the mechanism generalises.** Any
  question of the form "do the artists rule X loses overlap with the drop list" is
  unanswerable from the committed lists, because the census population was itself produced
  by rule X. A successor tempted by that comparison should stop.
- **The candidate tail is deader than today's on two independent axes** — a lower share
  carries any commercial link, and fewer of those have anything that plays. Figures in
  `ctc_clips.json`. It cuts in favour of the rule rather than against it, and it is the
  closest thing to independent corroboration the transferability ruling has.
- **The `BYP-13` rate measured here rests on a denominator of 49.** It reads lower than
  today's, and that difference is not meaningful. What it supports is that the fault is
  present in this population too, at the same order.
- **The candidate population figure is a union of twelve cells, not a graph anyone will
  build.** Whatever connection rule wins delivers fewer artists, so the list over-covers by
  design.

## The open decision, and what I would do

**Two, and the first is small and blocking.**

**The builder applies one drop list to whichever archive it is handed.** With two lists now
in existence this is an active hazard: a candidate build would half-apply today's list,
silently, which is the exact asymmetry this whole thread existed to remove. If I were
continuing I would close it first — select the list by archive, or refuse to build rather
than half-apply. It is small, it owes tests, and it should land before anything is built
from `ALG-B`.

**The cap re-evaluation pre-registration is the substantial next step**, and it should be
written cold rather than by this session. Its inputs all exist now: Track B's results as
measured input, the `WGT-` device recommendation, and both drop lists so the cleanup can be
held genuinely constant. **What it needs from the owner is his half** — how much better a
connection rule must be to justify a rebuild, and whether the data-set switch is inside its
scope or a separate question. Both are "what counts as better", which is his.
