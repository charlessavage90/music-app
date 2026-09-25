---
name: plan-discipline
description: >-
  artistpath's rules for plans, specs and pre-registrations. Use BEFORE writing, amending,
  reviewing or executing any plan, spec or pre-registration here, and before designing any
  comparison of variants, gate, branch trigger or read-of-result: factor tables, held
  constants, effect sizes, run state, identifier namespaces, handoff seams.
---

# Writing and reviewing plans here

Five review rounds on the Phase 2 plans produced ten findings, and nine were two shapes.
Both have cheap structural fixes; neither is caught by writing more carefully.

**1. Comparisons with an uncontrolled variable.** Most findings were two things compared
that differed in more ways than the author believed — a baseline anchored on the wrong
arm, an artifact built by different code, variants differing by two knobs when the
comparison assumed one.

> **Any plan comparing variants must contain a factor table**: one row per variant, one
> column per knob that varies, and the isolating baseline named per row.
>
> **A variant's baseline is the variant differing by exactly one column.** If none exists,
> either build one or name the conclusion the comparison is barred from supporting — and
> check that no read-of-results in the document then claims it. A disclaimer nothing later
> reads is not a control.

The table is what makes this mechanical. You don't have to *notice* a confound — you read
across the row and count the differences. This is not hypothetical rigour: a two-knob
confound survived three rounds of prose review, including one written immediately after
the reviewer had named that exact pattern. The table found it in a single pass.

**The factor table needs a third section, because it cannot see a dormant term.** The
table asks *which knobs did I turn* — and the confound that nearly broke the Track 2 sweep
was a knob nobody turned.

> **Held constant, and why each is genuinely constant under the intervention.** Enumerate
> every term the comparison holds fixed, and for each, state why the intervention cannot
> change its state. A term that is inert in the baseline *for a reason the intervention
> removes* is not a constant — it is an uncontrolled variable that appears only in the
> arms that succeed.

Worked example: `specs/2026-07-23-track2-preregistration.md` §0. `w_floor` never fires in
production because `w_jump` stops paths dipping below the floor — and diving below the
floor is precisely what the sweep's successful arms do. Left alone it would have switched
itself on in the winners only, making every "one-knob" attribution in the sweep wrong.
Caught before the sweep rather than after, which is the difference between a design
correction and a retraction.

**No experimental arm runs until a pre-registration is committed.** It fixes the primary
outcome, the effect size, the pair or sample set, and the read of every possible result
including the null. The git commit timestamp is the evidence that it preceded the result —
that is the part that cannot be reconstructed afterward. Worked example:
`specs/2026-07-23-track2-preregistration.md`. The discipline is credited in the Phase 1 log
(§2.13 C5) with turning a disappointing null into an actionable one and with saving a blind
listen that would have burned the owner's ear on nothing.

> **Every gate and branch trigger needs its own effect size, not just every outcome.**
> Fix the size of difference that fires it — or state that any difference at all is
> decisive, and why. A trigger without one cannot tell the finding it was written for from
> noise, and it fires the expensive response either way.

Worked example, and it is the same document: Track 2's A0-vs-P gate was an exact-identity
test over 252 cells whose failure branch roughly doubles the sweep. It fired on **one**
cell, at a depth no criterion scores — the identical reading a 200-cell divergence would
have got. Every *outcome* criterion in that pre-registration carries a threshold; its gates
carried none, and nobody noticed until one fired and demanded a doubling on the strength of
a single path.

> **And every read-of-result names the run state it presupposes.** A read reachable before
> the design has finished running says so, and names what is still owed. Any instruction
> that keeps a specified run alive gets **its own sentence there** — never a subordinate
> clause of a rule about something else, because that is the half that degrades first.

Same document again: R0's read presupposes all fifteen arms ("no arm, including corner X"),
but R0 was detectable after eleven. The session got the null, opened §2.4 — the disciplined
move, and it said so — found nothing about the four unrun arms, and recommended skipping
them. What kept them alive was the tail of §1.4's rule for *selecting* W: "so the
attachments still get tested". It recalled that rule's main clause accurately from memory;
the subordinate clause did not survive. The owner asking what stage 2 was is what caught it,
and those four arms produced the only signal in fifteen.

> **No two load-bearing objects share an identifier, and new identifier series are
> namespaced.** Prefix them (`T3-C1`) or pick disjoint letters. **Collision-check by sweeping
> every ref — never the working directory**, which walks `builder/scratch/`'s multi-GB dumps
> and takes minutes, and never your own HEAD, where a concurrent session's series is invisible
> (2026-08-05: `ULC-` read free from a branch cut hours before the one using it):
> ```bash
> git grep -lE '\bULC-' $(git for-each-ref --format='%(refname)' refs/remotes refs/heads) -- '*.md'
> ```
> Silence means free; ~0.2 s. **Forward-only — never rename anything committed**; a frozen
> document's value is that it is frozen.

Track 2's pre-registration accumulated eleven collisions: `A1`–`A7` are simultaneously
factorial arms and amendment IDs, `C1`–`C3` simultaneously success criteria and Phase 1
defect IDs, and `R1` both the W-selection rule and a result branch. That last one cost the
session above the rule that governed: its single retrieval surfaced the `R1` requiring
corner X to have moved — X hadn't — so the applicable `R1` was never in view.

**2. Documents asserting things about the world that aren't true.** Plans have referenced
functions that did not exist yet, and cross-references have gone stale after renumbering.

> **Before executing a plan, grep every function, file, and config value it names.**
> Anything that doesn't resolve is either not-yet-built — state the dependency — or stale.

**3. Plans over ~8 tasks must name their own handoff points.** Subagent-driven execution
caps how *wide* the controller's context gets — the code stays out — but not how *long*.
The controller still reads one report per task and decides on most of them, so its context
grows with **task count**, not with effort or delegation quality. Past roughly 8–12 tasks
it is in long-context territory however well the work was delegated.

> Choose the handoff seams **at authoring time**, where a track's output is a committed
> artifact rather than a live understanding — then hand off there, retire the session, and
> start the next track fresh. A **material mid-flight amendment is also a seam**: there is a
> new governing document, and the next session reads it cold, which is the condition the
> amendment was written for.

A boundary you planned is cheap. One you discover at task 15 is expensive, and it gets
deferred past the point it should have happened because handing off then feels like an
admission. Phase 2 had a perfect seam at the Track A/Track B split and did not use it.

**What makes handoffs cheap:** append to the retained execution log **per task**, not only
at closeout. Decisions and reasoning, not narration. That is what makes sessions
interchangeable rather than making one of them precious — and "the controller is warm" is
never a reason to keep going, since a plan only its executor can continue is a plan that
was under-recorded.

**How to ask for a plan review.** "Review this plan" finds prose problems. **"Check this
plan's claims against the repo"** finds the confounds. Every high-value finding in Phase 2
came from a reader with the *code* open, because a plan can be perfectly self-consistent
and still wrong relative to `config.py`. Same cost, very different yield.
