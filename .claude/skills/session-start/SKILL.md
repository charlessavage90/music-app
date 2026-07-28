---
name: session-start
description: Orientation ritual for artistpath. INVOKED BY THE OWNER ONLY — run it when he asks for it by name ("run session-start", "/session-start", "orient yourself first"). Do NOT invoke it on your own initiative, and do not suggest it: not when a session opens, not when handed a plan or a handoff note, not before executing work you did not plan. It is owed by any session that will act on repository state — edit, commit, run a job — not only by builders; but many sessions here only read and advise, and the owner starts the ones that act with it instinctively. A session that owes it and was not given it says so once and proceeds — a fact about itself, never a recommendation to run it. This is mechanical orientation, not exploration — about five minutes: four questions, then a name for the session.
---

# Session start

The mirror of the `closeout` skill: closeout writes, startup reads. Every check below
consumes something a previous closeout produced, which is what keeps both cheap.

**Answer four questions, name the session, then start.** This is not codebase exploration
— `CLAUDE.md` already covers architecture, and re-deriving it is what makes fresh sessions
expensive. Five minutes, then work.

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
```

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
  along**: no `*.bin` artifacts, no `builder/scratch/`, no per-package `.venv`. So the
  worktree goes to whichever session does not need the graph — normally the advisory one,
  which needs no setup at all if it is only reading documents. For a consulting session
  there is a second reason beyond hygiene: a shared tree lets it read the other session's
  half-finished reasoning, and a second opinion that has absorbed the first one's working
  notes is not independent evidence.
- **Check the test queue** left by the last closeout. Anything sitting untested gets
  flagged to the owner now. That flag is the only forcing function on the async
  use-the-app check, which is the one item that catches defects tests structurally cannot.
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

## What to skip

- **"Read the docs."** That is the failure mode, not the fix. The orient table exists so
  you read four things rather than forty.
- **Codebase exploration.** `CLAUDE.md` covers the architecture and the three packages.
- **Reviewing the previous session's work.** That is review, not orientation. Reviews are
  rare, targeted, and belong at decision points — running one at every session boundary
  is how a project ends up relitigating its direction weekly.

## Scaling

**Full ritual** when executing a plan you did not write, resuming a phase, or acting on
another session's conclusions.

**Minimum** for a small, self-contained task in familiar territory: **A** (what governs),
**C** (repo state), and **E** (the `/rename` line — it costs one line and is worth more on
a short session, not less). Two minutes, and A and C catch the two failures that are
expensive to unwind — working from a superseded document, and colliding with a live
session.
