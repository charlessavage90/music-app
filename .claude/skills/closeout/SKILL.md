---
name: closeout
description: Post-execution hygiene ritual for artistpath. Run this after finishing any significant chunk of development work — a completed phase, a plan executed to its last task, a track of work about to be merged, or a long session about to be retired. Use it whenever the user says a phase or plan is done, asks to wrap up or close out work, is about to merge a development branch, or is handing work to a fresh session. Also use it proactively when you are the session that just finished substantial work and are about to end. Use its mid-flight scaling when a session is being retired before its work reaches a natural seam — the owner says to hand over now, or the degradation tell fires (being asked for figures it already computed, an item dropping out of a tracking document, or revising a firm claim under mild questioning with no new information). This is mechanical hygiene, not a code review — it takes about half an hour and answers yes/no questions only.
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

#### A2-mid — when the retirement is mid-flight rather than at a seam

**The last bullet changes form.** "What you know that is not in the durable record" is a
self-report. It works at a seam, because the session is intact. But a mid-flight retirement
is usually triggered by the opposite: the degradation tell in `CLAUDE.md` is a
**completeness** failure, so the session's judgement about what is complete is precisely
the faculty you have stopped trusting. Ask it to certify itself and you get a confident
"everything's captured," and you lose whatever nobody thought to ask about.

Replace the judgement with an enumeration. Ask for lists, not assessments:

- **Every number computed that is not written down somewhere.** Enumerate; do not filter
  for relevance. Being *asked* for a figure it already had is the named tell, so this is
  the first place to look.
- **Everything decided against, and why** — including options entertained for a moment and
  dropped. Negative decisions leave no artifact and evaporate first. The successor
  re-derives them, or does the rejected thing.
- **Anything the owner said in conversation that is not yet in a file.** This has cost
  something real here: the F3/F6 bypass URLs were recorded as living in the PR thread, and
  no PR carried a comment. The deferral was accepted on the strength of a durable copy that
  was never made.

Two categories a seam-time closeout never needs, because at a seam the work concluded:

- **The open decision** — the options, and **what you would do if you were continuing.**
  Not "the owner's call." A successor inheriting a position can argue with it; one
  inheriting a menu has to redo the reasoning that produced the menu.
- **Anything in flight** — dispatched subagents, background jobs, half-written directories.
  A cold session that finds an unexplained partial artifact in the tree cannot tell
  abandoned from running, and will usually guess wrong in the expensive direction.

**Do not settle the open question on the way out.** The pull to resolve one last thing so
the handoff looks tidy is strong, and retirement is the worst moment to decide anything: a
shaky conclusion reached while packing up enters the record as settled.

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

### A5. Release the processes this session started

**Sweep the ports, stop what this session owns, close what nothing needs, and leave a fresh
detached server behind only if C1 queued something that requires one.** The default for a
listener with no queued test behind it is **off** — a running server is not free, it is a
stale artifact waiting to be tested against.

A session that starts a dev server in a background shell stays *subscribed* to it: retiring
the session does not end the subscription, and only closing its terminal does. The terminal
is deliberately kept open across a handover so the outgoing session can still be asked what
it knew — so the wake path has to be closed here rather than by closing the window. This
sits in Part A because **only the owning session can stop its own tasks**, and by Part B the
closeout may be in a fresh one.

1. **Sweep by listener, not by task list.** A session sees only the tasks it owns, so
   `TaskList` reports an empty machine while yesterday's servers are still serving.

   ```powershell
   Get-NetTCPConnection -State Listen -LocalPort 8000,5173 | Select-Object LocalPort,OwningProcess
   ```

   Report each with its **start time against the HEAD commit date**. A listener older than
   the work being closed out serves code that predates it, so a manual test against it is
   invalid and looks entirely normal.

2. **Stop what this session owns** (`TaskStop`), and **name the listeners it does not** —
   those outlived a session that is gone, `TaskStop` cannot reach them, and freeing the port
   needs the PID. Stopping a task does not disturb the conversation, so the terminal stays
   answerable afterwards.

3. **Give every surviving listener a disposition — a recommendation, not an observation.**
   Two conditions, and they compose:

   | | **Fresh** (started at or after HEAD) | **Stale** (started before HEAD) |
   |---|---|---|
   | **C1 queued an item** | Keep it. Say what it is for. | **Ask: restart or close.** It serves code that predates the work, so the queued test would pass or fail for the wrong reason. |
   | **Nothing queued** | **Recommend closing it.** Nothing needs it. | **Close it**, and report that you did. |

   The bottom-right cell is not a question. No queued test needs the server *and* the code
   it serves is wrong: there is no case for keeping it, so do not table it as an option —
   tabling it manufactures a decision out of a foregone conclusion, which is its own tax.
   Closing a listener this session did not start is `Stop-Process -Id <pid>`; say in the
   closing message that you stopped something you did not launch, and how to get it back
   (the commands are in `CLAUDE.md`).

   **Reporting a stale unowned listener without a disposition is the failure this step
   exists to prevent.** On 2026-07-26 a closeout did exactly that: it reported both ports,
   both PIDs, and correctly noted the API predated the origin-secret middleware — and then
   left both running, with nothing queued that needed them. Every fact was right and no
   action followed from any of them. The owner got a table.

4. **If C1 queued an item that needs a local server and none survives, relaunch detached**,
   per the commands in `CLAUDE.md` — cite them, do not restate them. **Not every queued item
   needs one, since the cutover of 2026-07-27**: an item exercising the deployed site needs
   nothing running here, and a server started for it is a stale artifact by morning. Detached means no session owns
   it, so nothing can be woken by it; it equally means nothing is watching, so **a failure to
   bind is silent. Verify both ports answer before believing it started.** Record PID and
   port in the C1 entry.

**Then say so in the closing message** — ports, PIDs, what you stopped, and what you left
running *and why*. A detached server outlives every session and every terminal, so the
failure mode is the owner not knowing it is there; a table of PIDs with no disposition is
that same failure with more words.

---

## Part B — Fresh session, mechanical

These want fresh eyes, and none of them need the finishing session's context. Run
them in a new session with the handoff note in hand — **except B1, whose eyes are a
subagent's rather than the session's; see "Who runs B1" below.**

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

**Escalate for want of evidence, never for want of authority.** A finding you have the
facts to fix is yours to fix, and that includes `CLAUDE.md`, `.claude/` and `memory/` —
D6 governs *growing* the standing layer, not *correcting* it. On 2026-07-26 the audit found
`CLAUDE.md`'s next-action row still describing 2026-07-25 and unaware that three Gate 2
tracks had landed; the session had every fact needed to fix it, escalated on authority
grounds, and the row stayed wrong. An escalation list is a measurement of a thin record. A
known-false statement parked on it is just a defect with a nicer name — and in the
auto-loaded layer it misdirects every cold session before that session reads anything else.

Check whether previous audit findings were ever actioned. A stale audit finding is
worse than none, because it reads as settled.

#### Who runs B1 — the one item in Part B the retiring session may do itself

**The fresh eyes B1 needs are the auditor's, not the dispatching session's.**
`doc-auditor` is a subagent and reads cold whoever spawns it, so the state of the session
that pressed the button cannot contaminate the report. B2, B3 and B4 are different in kind
— those are checks a session performs *with its own eyes*, and a warm session performs them
badly. B1 was grouped with them by topic, not by mechanism.

Both saves above confirm it: each was a case of **no cold reader being involved at all** —
one skipped audit, one self-run grep. Neither was a warm session dispatching the auditor
and getting a worse report for it.

**So the retiring session may run B1, and at a mid-flight handoff it should.** Handing the
audit forward puts documentation remediation on the successor's critical path and makes its
first substantive read of the governing documents an audit brief rather than the work. That
cost is observed, not theoretical: an incoming session on 2026-07-24 audited a
pre-registration's bookkeeping sections adversarially, corrected a High-severity status
defect — and came away unable to state what the experiment's own outcome criteria were. The
successor should be *reading* a completed, remediated audit in the handoff note, not
inheriting one.

**Exception — when the degradation tell triggered the retirement.** Then the session's
judgement about completeness is the faculty you have just stopped trusting, and adjudicating
findings is judgement. Dispatch the auditor, fix only what is unambiguous from the record,
and hand the remainder to the successor as a **named list** rather than as a task to
rediscover. A scope-driven handoff carries no such problem.

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
restatements to citations. Where a figure is deliberately inline as a hazard warning at the
point of use, it **cites the section that owns it, and the next sweep re-checks it against
that section** rather than skipping it. An exemption that suppresses its own re-detection is
how a correct restatement becomes a stale one — the drift the one-document rule exists to
prevent.

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

**Write the entry for someone holding a mouse, not for the session that wrote the code.**
Every step is a thing to *do* and a thing to *look at*. This is where an entry goes wrong:

- **Never name an identifier, file or function in the steps.** "Press *know them already*
  five or six times" is a step. "The floor relaxation is the part with the most renamed
  variables (`base_floor_raw`, `floor_raw`, …)" is the author narrating their diff, and it
  actively misleads — a reader reasonably asks whether it means one *kind* of bypass
  matters more, which is a question the sentence raised and did not answer.
- **If one variant of an action really is more revealing, say which and say so plainly**
  ("use that button rather than the other one — it pushes hardest on what changed"). Half
  an explanation is worse than none: it creates a decision the reader cannot make.
- **Do not restate a test count.** It is stale within the session that wrote it.
- Put implementation detail behind a single pointer to the execution log, for the reader
  who wants it. Nobody testing the app needs it inline.

The tell is a step the owner cannot act on without asking what a term means. Reread each
step as a person who has not seen the diff — that pass takes a minute and is the whole
difference between an entry that gets run and one that gets queried.

The forcing function sits on the other end: **`session-start` checks the queue and flags
anything sitting untested** — so it fires when the owner runs that ritual, not on every
session. That keeps it honest without gating anything.

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
- `builder/scratch/` and `*.bin` — every graph artifact, with `!**/tests/fixtures/*.bin`
  the sole exemption. The `**/` is load-bearing: a pattern containing a slash is anchored
  to the gitignore's own directory, so the `!tests/fixtures/*.bin` **this file quoted until
  2026-07-26** exempted nothing, and both fixtures were silently ignored for months.
- `api/uv.lock` and `builder/uv.lock` are **committed**, deliberately, and must stay that
  way: with no CI the Docker image is the release artifact, so `uv sync --frozen` has to
  install what the tests ran against (DEP-32, 2026-07-26). They were ignored until Track B,
  and this file said "never tracked" for a day after that stopped being true.

If work touched anything near those paths, `git status --ignored` over them takes
seconds and prevents a silent loss.

**Mid-flight exception — D1 inverts.** If work is being handed over rather than finished,
the tree is *supposed* to be dirty, and cleaning it destroys the state the successor needs.
Commit what is coherent, then **name every remaining untracked path in the handoff note:
what it is, who wrote it, and whether it is still being written.** An unexplained partial
directory is exactly what makes a cold session guess.

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

### D6. The standing context layer is the owner's to grow

**Report two numbers, never one. They are not the same layer and they do not cost the same.**

```bash
M=~/.claude/projects/C--Users-charl-OneDrive-Claude-Projects-music-app/memory

# 1. UNCONDITIONAL — loads in every session before it reads anything. Characters.
#    `tr -d '\r' | wc -m`, never `wc -c`: this tree is core.autocrlf=true so every line
#    carries a phantom byte, and `wc -c` counts bytes, so every em-dash and § costs 3.
#    Together that was 2% of the total — and the CR half moves when prose is rewrapped,
#    which is the exact blindness characters were adopted to remove.
{ cat CLAUDE.md "$M/MEMORY.md"; \
  sed -n '/^description:/p' .claude/skills/*/SKILL.md .claude/agents/*.md; } \
  | tr -d '\r' | wc -m

# 2. CONDITIONAL — loads only on invocation, dispatch or recall. Lines.
cat .claude/skills/*/SKILL.md .claude/agents/*.md \
    $(ls $M/*.md | grep -v MEMORY.md) | wc -l
```

**What is in each, verified by observation on 2026-07-26 rather than assumed:**

| Unconditional | Conditional |
|---|---|
| `CLAUDE.md`, in full | `SKILL.md` **bodies** — only on invocation |
| `MEMORY.md` — the index **only** | Agent definition **bodies** — only on dispatch |
| The `description:` line of every skill **and** every agent | `memory/*.md` **bodies** — only on recall, which is *unpredictable*: they load when not needed and miss when needed |

**Two things this corrects, and both had been wrong for a while.** The rule used to name
"`memory/` and both `SKILL.md` bodies" as unconditional. Neither is. And skill *descriptions*
— which genuinely are unconditional, one per skill, and `closeout`'s is a full paragraph —
were not counted at all.

**The units differ deliberately.** The unconditional layer is written almost entirely in
very long single lines — `CLAUDE.md`'s orient table is one row per line, and every
`description:` is one line — so `wc -l` is blind to it. Rewriting the next-action row as a
pointer on 2026-07-26 cut it from 2,135 characters to 637, roughly 375 tokens off every
future session, and `git diff --numstat` reported `1 insertion, 1 deletion`. **Net zero.**
A check that cannot see its largest available win is not a check. The conditional layer is
ordinary wrapped prose, so lines are fine there.

Record **both** deltas in the retained log. **If the unconditional one is positive, the
commit message states the cost and the case** — what fires the new rule, and why it was
worth it. A positive conditional delta is worth recording and is not the same alarm: those
lines are paid by the sessions that ask for them. It
need not name a removal: a displacement counts only where the thing removed had stopped
earning its place, and **compressing live prose to make any of these numbers go down is not
a displacement, it is damage with a receipt.**

**That guardrail got more important when the unit got finer, not less.** Lines were coarse
enough to resist the move — you could not shave a sentence off a paragraph and book a
saving, because the paragraph still occupied its lines. Characters have no such friction:
every tightened clause books a real-looking reduction, and the two occasions this project
lost the exact wording that made a check usable were both paid for with arithmetic that
looked like a win. **So the rule is on the edit, not the number.** Rewording to say the same
thing in less space is the damaging move whatever it measures at; deleting something that
has stopped earning its place is the legitimate one whatever it measures at. If you cannot
say which of those you just did, you did the first. Net-new is the owner's call, not the session's, and it needed his
agreement before it landed. A justification written by the session that wanted the lines is
not a check; that is how this layer reached 1,436 lines with every individual addition
justified. **That 1,436 was measured under the old, over-broad definition** — it counted
whole `SKILL.md` bodies as unconditional. The incident is real and the lesson stands; the
number is not comparable to what the commands above produce, so do not diff against it.

**Correcting this layer is not growing it, and it is not optional.** Three edits, three
different owners, and conflating the first two leaves the layer accurate-but-frozen, which
is the same harm as inaccurate:

| The edit | Whose call | The test |
|---|---|---|
| A statement in the layer is **false about the world** | **The session, here, now** | Net size ≈ 0 in that layer's own unit; no new rule, no new narrative, no new claim — the true statement replacing the false one |
| A **new** rule, row, narrative or check | The owner, given the cost and the case | Net size positive |
| The same facts in **different words** | The owner | This is where compressing live prose does its damage; it has twice cost the clause that made a check usable |

A false statement in the auto-loaded layer is read by every cold session before it opens a
single project document — it is the most expensive kind of stale text this project has, and
the budget rule exists to protect that layer's value, not to freeze its contents. So the
question is never *may I touch `CLAUDE.md`*; it is **which row of that table am I in.**

**A correction that cannot be made in roughly the same number of lines is not a
correction.** Report it as growth, with the wording you would use and the delta it costs,
and let him decide. That is the honest escape hatch, and it is a sentence in the closing
message rather than a decision withheld.

**Both commands read `memory/`, which lives outside the repo and is not in git** — a diff
cannot see it, yet `MEMORY.md` loads into every session. That is why these are totals
compared against the last figures in the log rather than a `git diff`, and why the figures
go in the **log** and not only in a commit message: the log is the only place the two halves
of this layer can be tracked together.

**Only the first number is a standing tax.** The unconditional layer is paid by every
session before it reads anything else, whether or not that session needs a word of it — so
growth there is the owner's call. The conditional layer is paid on demand by the session
that invoked the skill, dispatched the agent, or had the memory recalled; a session that
never touches graph analysis never pays for `ml-graph-analyst`. `docs/` is conditional too,
and routes around its own bulk — half the corpus is COMPLETE plans that cost nothing — which
is why a large `docs/` has never been the problem.

The failure mode is the same in both, and it is that the asymmetry is invisible per-commit
and only visible in the total: this layer once went 661 → 1,436 lines in two days while
every individual addition was justified.

Two traps, both already sprung here:

- **Budget the layer, not a file.** A soft ceiling was once proposed on `CLAUDE.md` alone.
  It was never adopted, and in the same period `CLAUDE.md` grew 38% while `session-start`
  — unbudgeted, and the file whose own text promises "five minutes" — grew **53%**. Naming
  one file relocates growth to the next one.
- **The check is on the addition, not on a threshold.** A line count recorded against a
  limit produces a number with no owner, read by nobody, at the moment the session that
  added the lines is least motivated to act on it. Displacement fires at the point of
  addition, in the artifact that records it, and is checkable from a diff.

**Do not respond to a positive delta by giving rules expiry dates.** See `CLAUDE.md`,
"Two rituals bracket every chunk of work" — rules here are invariants; the growth is in the
narrative attached to them, and that narrative is what makes a rule transfer to a case it
was not written for.

### D7. Mark the session retired — the last thing you write

**Close with a `/rename` line prefixing `RETIRED-` to the session's current name.** You
cannot run it yourself — `/rename` is a built-in command, not a skill — so hand him the
finished line with nothing to compose:

```
/rename RETIRED-track2f-toll-builder (handoff, mid-flight)
```

**Prefix only.** Keep the name and any suffix `session-start` §E set, so a chain of handoffs
still reads as one chain in the `/resume` picker.

The terminal of a retired session is deliberately left open — to confirm the handoff landed,
and to ask it what it knew. Nothing else marks it as finished: in the picker and the window
title it is indistinguishable from a session still working, which is the same confusion
`session-start` §C has to resolve from the other side. **If you do not know the current
name, ask rather than guess** — a session renamed to a name it never had is worse than an
unprefixed one.

Put it in the same closing message as A5's dev-server statement: one message carrying
everything he has to act on.

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

**Minimum** after a small self-contained track — A4, **A5**, B2, C1, D1. Default-flip,
release the shells, reachability, use it, clean tree. Half an hour combined, and they catch
most of what matters. A5 travels with C1: a queued test that needs a server fails against a
stale one for the wrong reason.

**Mid-flight retirement**, when a session is being handed over before its work reaches a
natural seam — A1, **A2-mid**, A3, **A5**, B1, B5, **D1-mid**, D3, **D6**, **D7**. A5 matters most
here: a mid-flight handover is precisely when the old terminal is kept open, which is the
only condition under which an owned shell can wake a retired session. D6 belongs here
specifically: a mid-flight handoff usually happens *because* a governing document changed,
so the standing-layer delta is both non-zero and exactly what the successor needs recorded.

B2 (reachability), B3 (vacuous tests) and B4 (prose-versus-code) all want a finished
artifact; run against something half-built they produce noise and false alarms, so they
**travel with the work to the successor** rather than being run now. B1 and B5 stay, and
matter more than usual: a mid-flight handoff normally happens because a governing document
just changed, which is exactly when descriptions elsewhere go stale. **B1 is run by the
retiring session, not handed forward** — per "Who runs B1", with its degradation-tell
exception. A4 is usually inapplicable — unshipped work is the premise, not a defect — but
say so rather than skipping it silently.

**Do not make B1 conditional on a document having changed.** That was proposed and the
evidence killed it: on 2026-07-24 an audit at a handoff where no governing document had
obviously changed found a High-severity defect anyway — a prerequisite recorded as open in
three documents whose machinery had existed since execution-order step 2, each document
having copied the list forward rather than re-checked it. The check a session would
naturally run came back clean **and confirmed the wrong answer**, because the machinery sat
inside the harness and nothing in shipped code referenced it. A change-triggered audit
would have skipped the run that caught it. Propagating defects do not need a change to
become live.

Part D runs every time regardless of size, with D1 inverted per its mid-flight exception.
An unopened PR is not a judgement call; a dirty tree is one only when it is handed over
explained.

## What this is not

**Do not put a comprehensive review in the closeout.** Hygiene asks *did we leave a
mess*; review asks *did we do the right thing*. Running the second one at every
boundary is how a project ends up commissioning review after review, each one finding
real-but-marginal issues that generate more work than they prevent.

Reviews should be rare, targeted at genuinely uncertain and hard-to-reverse decisions,
and — where the question is about the product rather than the code — scheduled *after*
a period of real use rather than before it.
