---
name: session-start
disable-model-invocation: true
description: >-
  Orientation ritual for artistpath. INVOKED BY THE OWNER ONLY — run it when he asks for it by name ("run session-start", "/session-start", "orient yourself first"). Do NOT invoke it on your own initiative, and do not suggest it: not when a session opens, not when handed a plan or a handoff note, not before executing work you did not plan. It is owed by any session that will act on repository state — edit, commit, run a job — not only by builders; but many sessions here only read and advise, and the owner starts the ones that act with it instinctively. A session that owes it and was not given it says so once and proceeds — a fact about itself, never a recommendation to run it. This is mechanical orientation, not exploration — about five minutes, with separate tracks for changing the app and changing the project's own apparatus.
---

# Session start

> ## The owner's scope for this session, if he gave one
>
> $ARGUMENTS
>
> **If the line above is empty, or still reads `$ARGUMENTS` verbatim, he gave none.** Run the
> ritual, then hand back and ask what the work is. That is the normal `/session-start` case and
> nothing is wrong.
>
> **If it names the work, that is your scope.** Use it to pick the track immediately below, to
> decide which of §A–§E or §MT actually apply, and to write §E's `/rename` line. Orient *for
> that work* — do not re-derive it, and do not treat it as the whole instruction, since he may
> add to it in the same breath.
>
> **He reaches this line by typing the scope after the command** — `/session-start continue the
> documentation layer strategy work`. He cannot reach it by asking in prose: this skill is
> marked `disable-model-invocation: true`, so a session **cannot** invoke it, however plainly it
> is asked. **If he asks in prose, do not apologise and do not explain the mechanism** — reply
> with the one line he can paste, `/session-start <his words>`, and nothing else.

The mirror of the `closeout` skill: closeout writes, startup reads. Every check below
consumes something a previous closeout produced, which is what keeps both cheap.

**Answer four questions, name the session, then start.** This is not codebase exploration
— `CLAUDE.md` already covers architecture, and re-deriving it is what makes fresh sessions
expensive. Five minutes, then work.

> **Pick a track first. §A–§E are written for a session that changes the app.** If this
> session changes the project's own **apparatus** instead — documentation, skills, agents,
> the map, `NEXT.md`, memory, bookkeeping — **run §MT, then §C and §E, and skip §A, §B and
> §D.** Roughly half of A–E is inert for that work, and the four checks that catch its
> characteristic damage are not in A–E at all.

> ## ⛔ How to pick it — and **the checked-out branch is not the answer**
>
> **Scope above, if he gave one. Otherwise ask, in one line.** Those are the only two sources.
>
> **The branch you find yourself on may belong to another session, not to you.** He runs two
> sessions in one tree routinely — maintenance in one, the app in the other — and the second to
> arrive lands on whatever branch the first checked out. Reading the track off that branch name
> gets it confidently, articulately wrong, and **nothing downstream will correct it**, because
> every later check is scoped by the track you picked.
>
> *(Recorded 2026-09-12, from the live case: a session launched for the `LBD-`/`LBL-` listen work
> found a `DLS-` branch in the tree, reasoned correctly from it to "apparatus, therefore the
> maintenance track", and oriented for the wrong body of work. The inference was sound. The
> premise was another session's.)*
>
> **So the branch is evidence about your track only if this session created it, or a handoff note
> names it.** Otherwise: **one line to the owner naming what you would assume, then proceed on his
> answer.** That is cheaper than it looks and far cheaper than orienting twice.

---

## A. What governs this work?

This repo has a supersession chain — original plan → revised plan → amendments → a
CLOSED section. Reading the wrong layer produces confidently wrong work, and a document
that says "where this and the original disagree, this governs" only helps once you have
found the newer one.

- Read `CLAUDE.md`'s orient table, and **the handoff note** if the last session left one.
- Identify the governing document and **follow its supersession chain to the end.** Check
  `docs/README.md` — it classifies every document by role and names which are superseded.
- **Never treat `docs/how-we-map-similar-artists.md` or anything under `docs/reference/`
  as context.** The first is a narrative journal, the second is third-party material.
  Neither is maintained, and a cold session has no way to know that from the filenames.
- **Figures live in exactly one document.** If you are about to write a number, confirm
  you are copying it from `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`
  and not from a plan that copied it earlier. Restatement is how figures drift.

## B. What is already decided that I must not reopen?

A revised plan on this project needed an explicit "do not re-argue" section because the
likeliest failure of a cold session was a well-reasoned proposal to revive a component
that had been deliberately cancelled. Good reasoning applied to a settled question is
still waste, and it is expensive to detect.

- **Read the CLOSED decisions** in the governing plan before proposing anything adjacent
  to them. If one looks wrong, say so once, briefly, and proceed as instructed unless the
  owner reverses it.
- **Read the deferred findings and their success conditions**, and check whether any
  condition has now come due. That check is the entire forcing function behind the
  closeout deferral rule — without it, deferral is just an unranked backlog.

## C. What state is the repo in, and is anyone else in it?

```bash
git status --short && git log --oneline -3 && git branch -vv
gh pr list --state all --limit 5 --json number,title,state,mergedAt
```

> ### ⚠ If another session is already live here, take your worktree BEFORE you finish orienting
>
> The `SessionStart` repo-state report and the owner both tell you this at the top. **Act on it
> first, not after §C.** Orienting inside a tree someone else is working in is what produces the
> two failures below, and both are avoided entirely by moving first:
>
> - **You orient against their branch** and pick the wrong track — see the track-picker warning
>   above.
> - **`HEAD` moves between two of your own commands**, and it looks like corruption. **It is
>   not.** In a shared tree the other session is committing, cherry-picking and pushing while you
>   read, so two commands a minute apart *should* disagree. **Do not spend turns establishing the
>   facts of a moving HEAD** — note it, move, and re-run §C once in your own tree, where the
>   answer holds still.
>
> **The command and the full rule are in the "Uncommitted work you did not create" bullet below
> — this block only moves them earlier.** One thing that is *not* a worry, because a first draft of
> this block got it wrong: **your hooks and settings are bound where the session was launched and
> do not follow you across a `git worktree add`.** A session started in the main tree keeps writing
> its `.claude/logs/` there and stays eligible for the `DLS-T1` count. Only a session *launched*
> with its working directory already inside a worktree would use that worktree's copy.
>
> *(Added 2026-09-12, from a live two-session case that hit both failures in one orientation.)*

- **Derive merge state; do not expect `NEXT.md` to carry it, and do not report its absence
  as a finding.** The cadence is work → `closeout` → *then* the owner merges, so the status
  document is written before the merge every time. It therefore names the branch and PR as
  **addresses** and lists his remaining actions as an ordered sequence, deliberately without
  saying where in that sequence he is — that is `closeout` A2-next, and it is the design.
  **A PR merged since the last closeout is the process working.** What *is* worth raising is
  the opposite: a branch with no PR, an unpushed branch, or a merge that contradicts what
  `NEXT.md` says the work *was*.

- **Uncommitted work you did not create means another session is live in this tree.**
  This is not hypothetical here — HEAD has moved mid-conversation while two sessions were
  open. If so: do not run builds, do not start long jobs, and above all do not
  `git add -A`, which sweeps their work into your commit.

  **Why this bites even when the two sessions touch disjoint files.** Concurrent *edits*
  really are near-harmless — nothing overwrites, nothing conflicts. Two things are shared
  by *processes* rather than by paths, and both surface at commit time:

  - **Git records content, not authorship of uncommitted work.** `git status` shows you
    modified paths with no way to tell yours from theirs. The boundary of "my work" lives
    only in your memory of what you did. So `git add -A` — which substitutes *everything
    present* for *what I did* — is a guess that happens to be correct whenever you are
    alone, which is every previous time, which is exactly what makes it a habit.
  - **The index, HEAD and the branch ref are one per tree.** `git add` stages into a shared
    buffer, so their `add` lands inside your `commit`. `--amend`, `rebase`, `stash`, `reset`
    and `checkout <other-branch>` all operate on the whole tree, including their
    uncommitted work.

  **So commit with a pathspec — `git commit -- <paths>` — which takes those paths from the
  worktree and ignores the index entirely.** No `-A`, no `-a`, no `--amend`, no `rebase`,
  no `stash`, no branch switch while another session is live. Under those constraints
  concurrent commits are genuinely fine: git serialises them and nothing is lost.

  **Simpler, if you would rather not carry that list — one session owns committing and the
  other only edits.** This is a simplification, not a requirement; its value is removing a
  standing judgement call at the moment a session is wrapping up and least careful. An
  advisory or consulting session is the natural non-committer, since its output is analysis
  and it can leave edits on disk for the owning session to land under an honest message.

  **Ask the owner to tell the session already running that you exist** — it cannot detect
  you the way you just detected it, because its own §C check ran before you arrived.

  **Non-negotiable regardless of who commits: if you find changes you did not make, leave
  them, name them to the owner, and commit around them.** Do not commit them, and do not
  describe where they came from. On 2026-07-23 a session swept a second session's
  `CLAUDE.md` edit into its own commit under the message *"written by the owner from this
  session"* — entirely plausible from where it sat, and false. The mixing took seconds to
  unwind; the invented provenance did not, because it reads as settled history. **No amount
  of git discipline prevents this one.** It is prevented by a session declining to narrate
  something it cannot know.

  **If both sessions genuinely need to commit, the one arriving second takes a worktree:**

  ```bash
  git worktree add C:/Users/charl/worktrees/music-app-<purpose> -b <branch>
  git worktree remove C:/Users/charl/worktrees/music-app-<purpose>   # when done
  ```

  **The OneDrive reason for this path has expired** — the tree moved to `C:\dev` on
  2026-07-27, so a sibling of the main tree is no longer synced and any location works. The
  path above is kept because it is what the commands say. Note that **gitignored files do not come
  along**: no `*.bin` artifacts, no `builder/scratch/`, no per-package `.venv`.

  **"Needs the graph" is NOT a reason to keep a session out of a worktree, and this rule used
  to say it was.** The artifact is read once at boot and never written (`Path(path).read_bytes()`
  in `graph_store.py`), and `ARTISTPATH_GRAPH` takes any absolute path (`ApiConfig`), so a
  worktree session points at the main tree's artifact and two sessions read it concurrently
  without interfering. What actually bars a worktree is **needing to WRITE gitignored state** —
  a crawl filling `builder/scratch/`, or a build emitting a new artifact — plus the `uv sync`
  each package's `.venv` costs. **So the worktree goes to whichever session does not write
  gitignored state** — normally the advisory one, which needs no setup at all if it is only
  reading documents. *(Corrected 2026-08-05: the old wording contradicted the second-arriver
  rule directly above it whenever the second arriver was the one needing the graph, and a
  cold reader hit that contradiction and had no way to resolve it.)* For a consulting session
  there is a second reason beyond hygiene: a shared tree lets it read the other session's
  half-finished reasoning, and a second opinion that has absorbed the first one's working
  notes is not independent evidence.
- **Check the test queue.** Anything sitting untested gets flagged to the owner now. That
  flag is the only forcing function on the async use-the-app check, which is the one item
  that catches defects tests structurally cannot. **Since 2026-09-05 a discharged entry LEAVES
  the file** — `closeout` `C1-demote` moves it to `archive/TEST-QUEUE-discharged.md` — so
  `TEST-QUEUE.md` holds only what is still to be pressed. **Read only the topmost heading of
  each entry anyway.** That rule is now a safety net rather than a necessity here, and it is
  still load-bearing in the two archives, where discharged entries do keep their old
  `## QUEUED` heading beneath their `## DONE` one: greping for the former is what made six
  consecutive closeouts report a backlog that did not exist. **An empty file is a valid and common state**: since 2026-08-05 an entry is written
  only when there is something to press, so **absence of entries means nothing is owed — it is
  never evidence that a session forgot.**
  **If the entry records a detached dev server, check it is still alive and started after
  HEAD** — closeout leaves one running deliberately, owned by nobody, and a stale one fails
  the queued test for a reason that has nothing to do with the work.
- **Confirm artifact identity before drawing any conclusion from one.** Several graphs
  exist in `builder/scratch/` and **they are not interchangeable.** They cannot be
  committed, so a sha256 against the manifest sidecar is the only way to know which one
  you have. A conclusion drawn from the wrong artifact looks exactly like a correct one.

## D. What would stop me?

- **Named gates in the governing plan, and their current state** — including any that
  *failed* and were worked around. A failed gate that someone routed around is the single
  most important thing to know before adding work on top of it.
- **Environment traps.** Only the first is in `CLAUDE.md`; the other two live in
  `memory/deploy-environment-traps.md` and the execution logs. They are still the first
  thing that breaks:
  - `UV_LINK_MODE=copy` on every `uv` command — hardlinking still fails at `C:\dev`. Not
    strictly required since the move off OneDrive (uv falls back to copying), but keep it.
  - `PYTHONIOENCODING=utf-8` on anything printing artist names.
  - Python buffers stdout when redirected here, so a long background job writes a 0-byte
    log and looks dead while running perfectly. Use `python -u` or `PYTHONUNBUFFERED=1`.
    Three subagents lost real time to this one.

## E. Name this session

**Close your orientation with a `/rename` line for the owner to paste.** You cannot run it
yourself — `/rename` is a built-in command, not a skill — so give him the finished line and
nothing to compose.

Name the **body of work, not the task**, in two to four words, taken from the governing
document or the branch (A) — whichever a stranger would recognise faster, and end it
`-builder` if this session is one: `/rename track2f-toll-builder`,
`/rename clip-cache-fix-builder`, `/rename p99-rescale-prereg-builder`.

Two suffixes, and they are most of why this is worth doing:

- `(handoff)` — you are continuing work a previous session retired **at a seam**.
- `(handoff, mid-flight)` — the handoff note says the previous session was retired
  **before** a seam. Same signal the cold-read check below keys off.

So: `/rename track2f-toll-builder (handoff, mid-flight)`.

It costs one line and no tracking anywhere. What it buys is a `/resume` picker where a
chain of handoffs reads as one chain rather than three unrelated entries — and a prompt box
that tells you which body of work a window belongs to weeks later.

---

## Three checks unique to session start

These cannot fire later. By the time there is a plan, or a conclusion built on a report,
the cost has already been paid.

### Cold-read a mid-flight handoff back before acting on it

**If the handoff note says the previous session was retired mid-work rather than at a
seam, state back — before doing anything else — what you believe the situation is, what is
decided, what is in flight, and what you would do next. Then wait for the owner to
confirm.**

A seam handoff is written from a finished position, and the committed artifacts corroborate
it. A mid-flight handoff is written by a session retired *because* its completeness was
suspect (`closeout` A2-mid), which makes it the document least able to vouch for itself.
The successor is the only instrument that can test it — and only in the first minute, since
after that you have absorbed the note's framing and can no longer see what it failed to say.

Costs one message. Every gap it exposes is a handoff defect caught before anything is built
on it, and it doubles as a measurement of which document was too thin: the note, or the
retained log the note was supposed to be a delta against.

### The scope check — before any planning

**If the task ends in a number, name the cheapest experiment that could change the
decision, and propose running it first.**

This is the standing rule in `CLAUDE.md`, and session start is the only moment it can
fire. Its absence cost this project most of a phase: a sixteen-task plan was written to
decide a scoring question, and the forty-five-minute experiment that actually answered it
was never scheduled at all.

The instinct to resist is the one that feels responsible — building an apparatus that
could answer the question rigorously. Ask instead what the crudest decisive test is.

**It fires on a plan you inherited too — harder, not less.** The header says "before any
planning", and the incident it records *is a plan that already existed*; inheriting the
apparatus does not change the question, it only adds the sunk cost that suppresses the check.
This is safe to run at the start of an execution session because **the output is a proposal,
not a reorder** — you name the cheaper test and hand the owner the choice. Spending the plan
anyway is his call, and often the right one. *(Resolved 2026-08-05; the header and the body
had been readable in opposite directions.)*

### Verify one claim before building on a report

**If you are picking up from a task report, a summary, or another session's conclusion,
check one load-bearing claim against the code before building on it.**

This project's characteristic failure is not bad code — it is confident prose about
correct code. Three separate corrections in one phase were reports describing
implementations that were fine; each was caught late, and one of them had already
propagated into a findings document.

The same applies to plans: **grep every function, file, and config value a plan names
before executing it.** Anything that does not resolve is either not-yet-built — state the
dependency — or stale.

---

## MT. The maintenance track — the apparatus, not the app

**Replaces §A, §B and §D** when the work is documentation, skills, agents, `docs/README.md`,
`NEXT.md`, memory or project bookkeeping. **§C and §E still apply** — repo state and the
`/rename` line are the two checks no session type is exempt from. Two details, because
"unchanged" would over-claim: **§C's artifact-identity bullet is inert here** — a
documentation session draws no conclusion from a graph, so say that rather than performing a
check that cannot fail — and **§E takes no `-builder` suffix**, because this is not one. So:
**MT1–MT4, then C, then E.** When this session finishes, its closeout is `closeout`'s
**maintenance tier**, not the full ritual — the mirror of this one.

**Of the three checks unique to session start:** the cold-read applies if you are picking up
a mid-flight handoff, the cheapest-experiment scope check does not (no maintenance task ends
in a number), and verify-one-claim is folded into **MT2** in the form this work actually meets
it — a forwarded flag rather than a task report.

*Added 2026-08-05 from a live baseline. A maintenance session ran the full ritual and
reported the supersession chain and the closed-decisions list to the owner, who needed
neither. Meanwhile it had to derive MT1, MT2 and MT3 for itself, and got MT2 right only because
the outstanding item happened to sit in `NEXT.md`'s top block.*

### MT1. What am I forbidden to edit?

**§A asks what governs so you can obey it. Ask the opposite question — what is frozen.** Same
source, `docs/README.md`'s role column; different purpose.

- **COMPLETE and HISTORICAL documents are never edited**, however wrong they have become. A
  frozen document's value is that it is frozen.
- **A correction goes forward** into the governing document, and `docs/README.md`'s row for
  the frozen one points at it. **Change that row even when the frozen document contains no
  stale identifier to grep for** — the defect is usually that the row fails to *warn*, and no
  grep finds an absence.
- **Figures live in exactly one document.** Restating one is a defect even when it is right.

### MT2. What is outstanding — and is the flag true?

Maintenance work does not arrive in a plan. It accumulates in four places and **nothing
collects them**:

- `NEXT.md`'s **current top block** — older blocks are history, never act on them
- the current handoff's **"Owed, and by whom"**
- `TEST-QUEUE.md` — **an item is live only if its topmost heading says so**
- deferred findings whose **success condition has now come due**

**Then verify one flag against source before acting on it.** A flag forwarded through several
closeouts is a claim about the repo that nobody has re-checked, and the forwarding is exactly
what makes it feel settled. Both flags carried into 2026-08-05 were wrong: one said a rule-out
was in no citable document when it was in two, and one had mis-counted a queue for six
consecutive closeouts.

### MT3. Am I about to touch the standing context layer?

**`CLAUDE.md`, `memory/MEMORY.md`, and the `description:` of any skill or agent load into
every future session whether or not it needs them** — except the description of a skill
marked `disable-model-invocation: true`, which never loads. Growing that layer is the owner's call,
never a session's.

**Check before writing, not after.** `closeout` D6 measures the delta — but by then the text
exists and he is reviewing a finished thing instead of deciding whether to buy it. If the work
touches any of those four, say so up front and report the cost from the diff, **lines *and*
characters**: these files are written in long single lines that `wc -l` cannot see change in.

**Bodies are free, descriptions are not.** A `SKILL.md` body, an agent definition body and a
memory file's body all load on invocation or recall only. Put the detail there.

### MT4. Which documents will collide?

§C tells you whether another session is live. This asks the sharper question: **which files
will you both write?** `NEXT.md`, `docs/README.md` and `CLAUDE.md` are touched by nearly every
session, and are where concurrent work actually conflicts — not in the code.

Name them to the owner with your sequencing, and keep each edit as small as the change allows.
A one-paragraph strike reconciles in either merge order; a wholesale rewrite does not.

---

## What to skip

- **"Read the docs."** That is the failure mode, not the fix. The orient table exists so
  you read four things rather than forty.
- **Codebase exploration.** `CLAUDE.md` covers the architecture and the three packages.
- **Reviewing the previous session's work.** That is review, not orientation. Reviews are
  rare, targeted, and belong at decision points — running one at every session boundary
  is how a project ends up relitigating its direction weekly.

## Scaling

**Which track first, then how much of it.** The old two tiers scaled on *size* only, which
had no answer for a session doing a different kind of work rather than a smaller amount of it.

**The three checks unique to session start run on every tier unless a tier says otherwise.**
Only the maintenance track says otherwise, and it adjudicates all three explicitly in §MT.
They are not part of the A–E lettering, so a tier that names only letters does not thereby
exclude them.

**Maintenance track — §MT, C, E** when the session changes the project's apparatus rather than
the app: documentation, skills, agents, the map, `NEXT.md`, memory, bookkeeping. §B and §D are
inert there.

**Full ritual — A–E** when executing a plan you did not write, resuming a phase, or acting on
another session's conclusions.

**Minimum — A, C, E** for a small, self-contained builder task in familiar territory (the
`/rename` line costs one line and is worth more on a short session, not less). Two minutes,
and A and C catch the two failures that are expensive to unwind — working from a superseded
document, and colliding with a live session.
