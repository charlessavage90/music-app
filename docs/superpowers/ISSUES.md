# How this project uses GitHub issues

**Role: AUTHORITATIVE for issue conventions** — what becomes an issue, how one is written, labelled,
dispatched and closed. Adopted 2026-09-24. `CLAUDE.md` points here and does not restate it; the
`closeout` (A3) and `session-start` (§B, MT2) skills consume it.

**Why issues, and why now.** The owner works in Orca, which dispatches an agent session *from an
issue*. So an issue is not a note to self — **it is the whole brief a cold session starts from.**
Before 2026-09-24 task-like work lived in `NEXT.md`'s *Deferred, with conditions* table, which no
tool could dispatch from and which had grown past `NEXT.md`'s line budget.

## 1. What is an issue, and what stays in a document

| An issue | Stays in a document |
|---|---|
| A **bug or defect** — something the app, the build or the apparatus does wrong | **What to do next and in what order** — `NEXT.md` (sequencing is not a backlog) |
| A **deferred finding** with a success condition (`closeout` A3) | **Gate state, closed decisions, must-not-change rules, PARKED owner triggers** — `NEXT.md`'s registries |
| **Task-like work** a session could pick up: a fix, a measurement, a doc repair | **Accepted residuals and standing conditions** that bind future work but are not work — `NEXT.md` |
| An **open security finding** | **The use-the-app checklist** — `TEST-QUEUE.md` stays a file. A press that *finds* a defect files a `bug` |
| | **Findings, figures, decisions, pre-registrations** — `docs/superpowers/`. An issue **links** them |

**Figures still live in one document.** An issue cites the document that owns a figure; it never
becomes a second home for one. The one exception is a **moved record**: an item migrated from a
frozen registry quotes that registry text verbatim, dated and permalinked, so the dispatched session
sees exactly what was tracked. A quote with provenance is a citation, not a restatement.

**Project identifiers survive.** The title leads with the item's own ID when it has one —
`[G3-A1] …`, `[LUX-E2] …` — so `git grep` and `gh issue list --search` meet in the same token. An
issue number is an *address*, never a replacement for a project identifier. New ID series still
follow `CLAUDE.md`'s namespacing and collision check.

## 2. Labels

**Every issue carries exactly one kind, at most one whose, and one or more areas.** `research` is a
modifier on top of the kind, not a kind.

| Group | Labels | Meaning |
|---|---|---|
| kind | `bug` · `deferred` · `task` · `security` · `documentation` | |
| modifier | `research` | An analysis or experiment: needs a committed pre-registration before any arm runs (`CLAUDE.md`) |
| whose | `owner-decision` · `owner-hands` | **No whose-label means it is a session's.** `owner-decision`: a session prepares the decision and presents it per `CLAUDE.md` "How to present results", **never makes it**. `owner-hands`: blocked on something only he can physically do |
| readiness | `agent-ready` | **The condition is met AND it is a session's.** This is the dispatch signal for Orca. Never on an `owner-decision` issue |
| area | `area:api` · `area:frontend` · `area:builder` · `area:infra` · `area:apparatus` | Which package, or the project's own docs/skills/agents |

**Milestone `Gate 3 — public`** holds everything that must close before sharing beyond friends and
family — the Gate 2→3 review's blocking set and anything that joins it.

## 3. How to write one — it is a dispatch brief

A session dispatched from the issue has **nothing else**. It has not read this conversation, the
handoff, or the execution log. Write for that reader. The templates in `.github/ISSUE_TEMPLATE/`
enforce the shape:

- **What** — one paragraph, in plain language: what a user, operator or future session would
  experience. The `CLAUDE.md` "could the owner disagree with this?" test applies.
- **Source** — a path (or permalink) to the document that owns the finding. Mandatory.
- **Condition** *(deferred only)* — when this becomes actionable, testable by a cold reader.
- **Whose** — a session's, the owner's decision, or the owner's hands, and one line on why.
- **Done when** — the observable end state. A PR that says `Closes #N` must be able to satisfy it.

**The repository is public, so issues are public.** Everything here is already public in the
committed docs, but an issue is more discoverable. **A `security` issue names the finding and cites
the document; it never spells out a reproduction.**

## 4. Lifecycle

1. **Filed** at the moment of noticing — a deferral files its issue at deferral time (`closeout` A3),
   not at closeout.
2. **`agent-ready` added** when a `deferred` issue's condition comes due and the work is a session's.
   `session-start` and `closeout` both re-test conditions (§5). If it comes due and is the owner's,
   say so to him instead.
3. **Worked** on a branch; the PR body says `Closes #N` so the merge closes it.
4. **Closed** — *completed* by the PR, or **by hand with a comment** saying what satisfied it (the
   strike-in-place rule from `closeout` A3: the closed issue *is* the evidence it was tracked).
   **Killed** (condition known-unreachable) or **accepted, won't fix** → close as *not planned* with
   the reason. **Never delete an issue.**

## 5. The two rituals

**`session-start`** (§B and MT2) lists open deferrals and re-tests each condition against reality:

```bash
gh issue list --state open --label deferred --limit 100 --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\([.labels[].name] | join(","))]"'
gh issue list --state open --label agent-ready --limit 50
```

**`closeout`** (A3) files every new deferral as an issue, closes every discharged one with a comment,
and lists both in the PR body (D5) by number.

**A session dispatched by Orca from an issue** is still acting on repository state. `session-start` is
owner-invoked and a session never runs it itself; if it owes it and was not given it, it **says so
once and proceeds** (`CLAUDE.md`). It reads the issue, then `CLAUDE.md`'s orient table, then works.

## 6. The migration, 2026-09-24

`NEXT.md`'s deferral registry was moved into issues on 2026-09-24. **The registry as it stood is
frozen in `NEXT-ARCHIVE.md`** (the block dated 2026-09-24). Each migrated issue quotes its row and
permalinks it. Rows already struck or discharged were not filed. Accepted residuals and standing
conditions stayed in `NEXT.md`. The Gate 2→3 review's findings were each re-checked against the
current code before filing; only the open ones were filed.
