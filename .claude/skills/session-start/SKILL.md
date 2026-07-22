---
name: session-start
description: Orientation ritual for artistpath, run before doing substantive work in a fresh session. Use it whenever a session begins real work on this repo — the user says "pick up where we left off", "continue Phase 2", "execute the plan", "what's the status", "carry on with X", hands over a plan or handoff note, or asks you to start a task an earlier session set up. Also use it proactively when you are about to execute a plan you did not write, or act on a report you did not produce. This is mechanical orientation, not exploration — about five minutes, answering four questions.
---

# Session start

The mirror of the `closeout` skill: closeout writes, startup reads. Every check below
consumes something a previous closeout produced, which is what keeps both cheap.

**Answer four questions, then start.** This is not codebase exploration — `CLAUDE.md`
already covers architecture, and re-deriving it is what makes fresh sessions expensive.
Five minutes, then work.

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
- **Check the test queue** left by the last closeout. Anything sitting untested gets
  flagged to the owner now. That flag is the only forcing function on the async
  use-the-app check, which is the one item that catches defects tests structurally cannot.
- **Confirm artifact identity before drawing any conclusion from one.** Several graphs
  exist in `builder/scratch/` and **they are not interchangeable.** They cannot be
  committed, so a sha256 against the manifest sidecar is the only way to know which one
  you have. A conclusion drawn from the wrong artifact looks exactly like a correct one.

## D. What would stop me?

- **Named gates in the governing plan, and their current state** — including any that
  *failed* and were worked around. A failed gate that someone routed around is the single
  most important thing to know before adding work on top of it.
- **Environment traps.** These are in `CLAUDE.md` and in the execution log, and they are
  still the first thing that breaks:
  - `UV_LINK_MODE=copy` on every `uv` command — OneDrive breaks hardlinks.
  - `PYTHONIOENCODING=utf-8` on anything printing artist names.
  - Python buffers stdout when redirected here, so a long background job writes a 0-byte
    log and looks dead while running perfectly. Use `python -u` or `PYTHONUNBUFFERED=1`.
    Three subagents lost real time to this one.

---

## Two checks unique to session start

These cannot fire later. By the time there is a plan, or a conclusion built on a report,
the cost has already been paid.

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

**Minimum** for a small, self-contained task in familiar territory: **A** (what governs)
and **C** (repo state). Two minutes, and they catch the two failures that are expensive
to unwind — working from a superseded document, and colliding with a live session.
