---
name: closeout
description: Post-execution hygiene ritual for artistpath. Run this after finishing any significant chunk of development work — a completed phase, a plan executed to its last task, a track of work about to be merged, or a long session about to be retired. Use it whenever the user says a phase or plan is done, asks to wrap up or close out work, is about to merge a development branch, or is handing work to a fresh session. Also use it proactively when you are the session that just finished substantial work and are about to end. This is mechanical hygiene, not a code review — it takes about half an hour and answers yes/no questions only.
---

# Closeout

A short, mechanical pass after significant work. Every item is a yes/no check that
takes minutes. Nothing here requires judgement about whether the work was *good* —
that is a review, and reviews belong at decision points, not at every boundary.

**Keep this cheap or it will not get run.** The whole value is that it is boring
enough to do every time. If an item starts requiring hours of adjudication, the item
is wrong — fix the item.

## Why each of these exists

Every check below earned its place by catching something real on this project. The
short reason is given inline, because knowing what a check is *for* is what lets you
apply it sensibly to a case it was not written for.

Two failure classes dominate AI-authored work, and most of this list targets them:

- **Things built but never wired in.** Each task produces a module; nothing prunes.
- **Confident prose about correct code.** The code gets reviewed; the sentence next
  to it does not.

---

## Part A — Before the finishing session retires

Only the session that did the work can do these. Once it is gone, the context is
gone with it, so these come first.

### A1. Distil the execution log

Subagent-driven development always writes a ledger to `.superpowers/sdd/progress.md`,
and that directory is **gitignored** — briefs, reports, and ledger all evaporate on
`git clean -fdx`. If nothing is distilled out of it, the reasoning behind the work is
lost the moment the branch merges.

Write or update a retained log in `docs/superpowers/` covering:

- Decisions taken, with reasoning, including any that reversed an earlier decision
- Defects found **in the plan itself** (distinct from defects in the code)
- Gate outcomes — passed, failed, or never reached
- Corrections to the prior record: which previously-recorded claims are now overturned
- Operational measurements with no other home (timings, counts)

What does **not** belong: what each task did (git has it), how it was implemented (the
code has it), per-task review chatter. Aim for a small fraction of the ledger's length —
signal density is the point.

**Figures live in one document only.** Cite `docs/superpowers/findings/` by section;
never copy a number into the log.

### A2. Write the handoff note

Thirty lines, aimed at a session that has never seen this work:

- Which documents are now wrong, and in which direction
- Which claims were overturned and must **not** be reverted by a well-meaning editor
- What has already been updated, so the next session does not re-edit it
- **What you know that is not in the durable record**

That last line is the important one. If it comes back non-empty, the retained log has
a hole and the note is the patch — fold it in rather than leaving it in a scratch file.

### A3. Give every deferred finding an address

A deferral without a success condition is not a decision, it is an unranked backlog
that makes closing anything feel irresponsible. On this project, findings were once
deferred to a rework that was later cancelled; they closed only because the
cancellation happened to name them.

For each open finding, confirm it has a **success condition**: "before Gate 2", "when
X is reworked", "accepted, won't fix". That last one is a legitimate terminal state
that clears the item with no work.

This is cheap *because it happens at deferral time*, not here. The closeout check is
two mechanical questions: does every open finding have a condition, and has any
condition now come due?

### A4. The default-flip check

**For every config knob this work added: was the default flipped and the loser
deleted, or was the knob removed?**

A knob sitting at its old default is unshipped work wearing a completion badge. This
project once finished thirteen tasks — tested, reviewed, gate-passed — while the
running application behaved identically throughout, because the knob that would have
changed it still pointed at the old behaviour.

If the answer is "we haven't decided yet", that is fine, but it means the work is not
closed. Say so plainly rather than marking it complete.

---

## Part B — Fresh session, mechanical

These want fresh eyes, and none of them need the finishing session's context. Run
them in a new session with the handoff note in hand.

### B1. Documentation audit

Dispatch the `doc-auditor` agent. It reports; it does not edit.

**This step is not skippable, and that is a finding rather than a caution.** It has now
been weighed and nearly skipped twice, and on both occasions running it immediately found
High-severity defects the session had no other way to see:

- **2026-07-23, Track 1.** The session judged the audit unnecessary; the owner overruled
  it. The audit found six High-severity defects in files that session never touched, the
  worst class being auto-loaded memory carrying stale status into every cold session.
- **2026-07-23, pre-Track-2 guards.** The session had already run its own targeted sweep
  of `docs/` and `.claude/` for stale identifiers and found it clean. The audit then found
  two High-severity defects **caused by that session's own work**: `CLAUDE.md`'s orient
  table still naming renamed identifiers *in the row warning about that exact confusion*,
  and the auto-loaded `ml-graph-analyst` definition describing the cost function with a
  term missing.

The second case is the one that generalises. **A self-run grep cannot find a defect of
omission** — the sweep searched for wrong content and the defect was absent content, so it
passed clean and the session believed it. A fresh reader checking whether each description
is *complete* is a different operation from searching for known-bad strings, and only the
first catches this class. **The strongest predictor that the audit will find something is
a session concluding it does not need one.**

Fix what the durable record can adjudicate. **Anything you cannot resolve from the
record goes on an escalation list rather than being guessed at** — that list is also a
precise measurement of where the record is too thin, which is worth having.

Check whether previous audit findings were ever actioned. A stale audit finding is
worse than none, because it reads as settled.

### B2. Reachability sweep

For every module this work created: does anything import it?

Two minutes of grepping for inbound imports. Orphans accumulate fast — a cancelled
component on this project remained imported and called by the export tool, and was
still emitting its output into the evaluation harness, after the decision to drop it.

An orphan is not automatically a deletion. It is a question: is this unfinished, or
abandoned? Both answers are fine; leaving it unasked is not.

### B3. Vacuous-test spot check

**Take the tests guarding the most important invariants, deliberately break the code
they cover, and confirm they go red.**

This is the highest-yield item on the list for AI-authored work. This project has
multiple documented instances of tests that passed while testing nothing: one that
passed via a different signal than the one it named, one whose guard clause was
unreachable in its fixture, one asserting symmetry against a fixture that was already
symmetric, one that never constructed the two orderings its entire purpose required.

All of them were green. None of them tested what its name claimed.

You do not need to do this for every test — only the ones whose failure would matter.
Five minutes on the invariants beats an hour on the whole suite.

### B4. Prose-versus-code check

Read the docstrings, module headers, and any task reports this work produced, and
check each assertion against the code beside it.

Corrections on this project have repeatedly been of this exact shape: a docstring
claiming values are carried through code that discards them; a report whose prose
contradicted its own clean implementation; a fixture named for a property it does not
have. In each case the code was right and the sentence was wrong.

Pay particular attention to names. A fixture or function named for behaviour it does
not have will mislead every future reader, and renaming is cheap.

### B5. Stale-description sweep — and it must include `.claude/`

**Which files restate a measured figure or describe the system's shape, and did this
work invalidate them?**

Two mechanical questions, both grep-shaped.

First, the one rule: figures live in `docs/superpowers/findings/` and everything else
cites them by section. **A restatement that is currently correct is still a violation** —
that is how drift starts. Five documents once each kept their own copy of the same
figures and drifted into three mutually contradictory positions, invalidating two
analyses before anyone noticed.

Second, and the one that gets missed: **`.claude/` is context, and nothing else audits
it.** Agent definitions and skill files are loaded into future sessions as authoritative
description of the world. When the graph changed shape on 2026-07-22, the
`ml-graph-analyst` definition went on describing the previous graph — node count, edge
count and max degree all wrong by roughly a factor of five — while also asserting an
equivalence between popularity and degree that the new graph falsifies, and pointing at a
document the doc map names as never-use-as-context. It survived a full closeout because
the sweep that ran covered `docs/` and `config.py` and stopped there.

So grep both `docs/` and `.claude/` for restated numbers and for shape claims. Convert
restatements to citations. Where a figure is deliberately inline as a hazard warning at
the point of use, say so in the file so the next sweep does not re-open it.

**This is the same failure class as D2 and as the fixture-seed defect**: a change removes
a property that something unrelated had silently come to depend on. Nothing breaks, no
test fails, no error is raised — a guarantee that was never stated simply stops holding.
Descriptions are the most common thing to depend on it.

---

## Part C — Queued for the owner, asynchronously

### C1. Use the application

**Boot it and use it.** Not the test suite — the app.

This catches the class of defect that code review and tests structurally cannot. On
this project, clip URLs that expire within the hour were invisible to both, because
tests mock HTTP and a URL that dies is indistinguishable from one that does not. Three
expert reviewers, all reading carefully, missed an entire defect class that twenty
minutes of use surfaced immediately.

**This is asynchronous and does not block closeout.** The owner will not always have
twenty minutes when a session ends. Write a short **test queue** instead: what changed,
what to exercise, and what "wrong" would look like. Mark the item *queued*, and finish.

The forcing function sits on the other end: **a session starting new work checks the
queue first and flags anything that has been sitting untested.** That keeps it honest
without gating anything.

All path state lives in the URL, so a bug found weeks later is still one paste away
from being reproducible.

---

## Part D — Git finalisation

Run last, after Part B's fixes have landed. The finishing session should commit its own
work before retiring rather than leaving a dirty tree for the next session to interpret.

### D1. The tree is clean, and nothing was silently swallowed

`git status --short` comes back empty. Anything untracked is either committed
deliberately or added to `.gitignore` deliberately — leaving strays is how unrelated
files get swept into a scoped commit by someone else's `git add -A`.

**Then check the other direction: did `.gitignore` swallow something you meant to keep?**
This repo ignores more than is obvious:

- `.superpowers/sdd/` — all briefs, reports and the progress ledger. This is why A1
  exists; without distillation they are gone.
- `builder/scratch/` and `*.bin` — every graph artifact, with `!tests/fixtures/*.bin`
  the sole exemption.
- `api/uv.lock` — never tracked. A plan once instructed staging it; the step was
  unsatisfiable as written and the dependency had to be pinned in `pyproject.toml`
  instead.

If work touched anything near those paths, `git status --ignored` over them takes
seconds and prevents a silent loss.

### D2. Regenerate committed fixtures if the artifact changed

`tests/fixtures/*.bin` are the only binaries in git, and **both packages carry a copy**.
If this work changed the graph, those fixtures are stale and every fixture-dependent
assertion is quietly testing the previous world.

If regenerating them changes a test's expected result, update the expectation and say so
in the commit message. Do not weaken the assertion to make it pass.

### D3. Record provenance for anything that cannot be committed

Graph artifacts are gitignored and always will be, so a checksum is the only identity
they will ever have. If this work adopted or compared artifacts, their sha256s and the
commits that built them belong in the retained record — otherwise a future session
cannot tell which artifact a conclusion was drawn from.

This is not hypothetical: several artifacts once sat in `scratch/` with no provenance and
were compared as a single-variable pair. They differed in two, and it invalidated two
analyses.

### D4. Run the suites and paste the output

```bash
cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../api  && UV_LINK_MODE=copy uv run --extra dev pytest -q
cd ../frontend && npm test
```

Run them; do not assert green from memory. Evidence before assertions.

### D5. Open the PR

Development here is **pull-request driven against `origin`** — see `CLAUDE.md`, "How work
lands". Nothing goes directly to `main`, and the branch should already have been pushed
long before closeout; if it has not been, push it now and note that it was late.

The PR body is where a reviewer picks up the context, so it carries:

- A link to the retained execution log
- **Gate outcomes, including failures** — a failed gate that was worked around is the
  single most important thing a reviewer needs to know
- Deferred findings with their success conditions (A3)
- Checksums for any adopted artifact (D3)
- **What is closed and should not be re-litigated** — decisions already taken with
  reasoning recorded. Without this, review reopens settled questions, which is expensive
  and demoralising

---

## Two standing rules

These prevent rather than detect, and they are the same rule seen from two ends:
**a deferral must have an address.**

### Deferral requires a success condition

Stated at A3. The cost is thirty seconds at the moment of deferring, and it converts
an open-ended list into something that can be mechanically checked.

### Kill when the path is closed — never on a count

**Do not kill work because it failed twice.** Something can fail repeatedly for
environmental or sequencing reasons and still be a good idea, and a counting rule
would discard it.

Kill when the condition named at deferral becomes **known-unreachable**. On this
project, a component was deferred twice — both times for defensible reasons — and the
second deferral arrived alongside evidence that its only viable approach would stop
working. That was a kill signal being read as a reschedule signal. The count was never
the problem; the unreachability was, and nobody checked for it.

Record killed work in the retained log with its reasoning, so that if the premise
changes later, revival is a decision rather than an archaeology project.

---

## Scaling

**Full ritual** after a phase, or after anything touching the graph, the artifact
format, or the cost function.

**Minimum** after a small self-contained track — A4, B2, C1, D1. Default-flip,
reachability, use it, clean tree. Half an hour combined, and they catch most of what
matters.

Part D runs every time regardless of size. A dirty tree or an unopened PR is not a
judgement call.

## What this is not

**Do not put a comprehensive review in the closeout.** Hygiene asks *did we leave a
mess*; review asks *did we do the right thing*. Running the second one at every
boundary is how a project ends up commissioning review after review, each one finding
real-but-marginal issues that generate more work than they prevent.

Reviews should be rare, targeted at genuinely uncertain and hard-to-reverse decisions,
and — where the question is about the product rather than the code — scheduled *after*
a period of real use rather than before it.
