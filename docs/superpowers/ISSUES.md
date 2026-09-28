# How this project uses GitHub issues

**Role: AUTHORITATIVE for issue conventions** — what becomes an issue, how one is written, labelled,
dispatched, claimed and closed. Adopted 2026-09-24; the agent-ready checklist, contracts and claiming
were added 2026-09-28. `CLAUDE.md` points here and does not restate it; the `closeout` (A3, D5) and
`session-start` (§B, MT2) skills consume it. **`scripts/issues.py` enforces the mechanical half**
(positive control: `scripts/issues-selftest.py`); where it and this document disagree, this document
governs and the script is fixed.

**Why issues, and why now.** The owner works in Orca, which dispatches an agent session *from an
issue*. So an issue is not a note to self — **it is the whole brief a cold session starts from.**
Before 2026-09-24 task-like work lived in `NEXT.md`'s *Deferred, with conditions* table, which no
tool could dispatch from and which had grown past `NEXT.md`'s line budget.

**Why the 2026-09-28 additions.** Several sessions now run at once, each in its own worktree.
Worktrees stop two sessions writing the same *file*; nothing stopped two sessions making
*incompatible assumptions* in different files — one changes what popularity means while another
writes an analysis assuming the old meaning, both PRs merge cleanly, and the repository is now
inconsistent with no conflict ever shown. Git is no help there, which is exactly why it is
dangerous. Alongside that: nothing said an issue was already being worked (§7), `agent-ready` sat on
issues blocked on the owner's hands, and blocking relationships lived only in prose.

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
follow the `plan-discipline` skill's namespacing and collision check.

## 2. Labels — and what is deliberately NOT a label

**Every issue carries exactly one kind, at most one whose, and one or more areas.** `research` is a
modifier on top of the kind, not a kind.

| Group | Labels | Meaning |
|---|---|---|
| kind | `bug` · `deferred` · `task` · `security` · `documentation` | `deferred` means **not actionable until its condition comes due**; when it does, the kind becomes `task` or `bug` (§8) |
| modifier | `research` | An analysis or experiment: needs a committed pre-registration before any arm runs (the `plan-discipline` skill) |
| whose | `owner-decision` · `owner-hands` | **No whose-label means it is a session's.** `owner-decision`: a session prepares the decision and presents it per `CLAUDE.md` "How to present results", **never makes it**. `owner-hands`: blocked on something only he can physically do |
| state | `agent-ready` · `claimed` | `agent-ready`: **passes the §4 checklist — dispatch it.** This is Orca's signal. `claimed`: a session is working it (§7). **At most one of the two, ever**, and **never either on an issue carrying a whose-label** |
| area | `area:api` · `area:frontend` · `area:builder` · `area:infra` · `area:apparatus` | Which package, or the project's own docs/skills/agents. **Not a collision signal** — §5 is |

**Milestone `Gate 3 — public`** holds everything that must close before sharing beyond friends and
family — the Gate 2→3 review's blocking set and anything that joins it.

**Three states are deliberately carried by GitHub's native relationships, not by labels**, because
a label is stored state that someone must remember to remove, and a stale label is worse than none —
the dispatcher trusts it:

| State | Carried by | Why not a label |
|---|---|---|
| **Blocked by another issue or PR** | Native **"blocked by"** dependency | Clears itself when the blocker closes; a `blocked` label would outlive it |
| **Has parallel parts** | Native **sub-issues** under a parent | The delegation plan in a form GitHub counts; each part is dispatchable and has its own state. A "parallelizable" label only says the plan is somewhere in the prose |
| **Is one session's work** | **The definition of `agent-ready`** (§4, J2) | An `atomic` label would be a second name for "ready"; anything larger is a parent |

**Blocked on the owner is a whose-label, not a fourth state.** `owner-decision` and `owner-hands`
differ in what a session may do — prepare, or nothing — so they stay two labels. **An issue that is
part-session, part-owner is split** (§7): the session's part becomes an `agent-ready` sub-issue, the
owner's part keeps its label, and a "blocked by" link says which waits for which.

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
- **Reads contracts / Changes contracts** — from the §5 vocabulary, or `none`. An issue written by
  hand rather than from a template uses the same two headings — `**Reads contracts:** quantities` —
  because that is what `scripts/issues.py` parses.

**The repository is public, so issues are public.** Everything here is already public in the
committed docs, but an issue is more discoverable. **A `security` issue names the finding and cites
the document; it never spells out a reproduction.**

## 4. What `agent-ready` means — the checklist

**`agent-ready` is a claim that a cold session can take this issue and finish it, alone, in one PR,
without asking anyone anything.** It is applied only after every item below passes, and **removed by
anyone who finds one failing** — no permission needed; a wrong `agent-ready` is a defect.

**Mechanical — `python scripts/issues.py lint N` checks these:**

| # | Item |
|---|---|
| M1 | No `owner-decision` or `owner-hands` label |
| M2 | Not `claimed` |
| M3 | Kind is not `deferred` — a condition that came due changed the kind (§8) |
| M4 | No open native "blocked by" issue |
| M5 | No open sub-issues — dispatch the parts, not the parent |
| M6 | Has a *Source* and a *Done when* |
| M7 | Declares *Reads contracts* and *Changes contracts*, every token from the §5 vocabulary (`none` counts) |

**Judgement — the labeller confirms these and says so in one comment**, `Ready-checked <date> at
<sha>: J1–J7`, naming any that needed work:

| # | Item |
|---|---|
| J1 | **The condition was re-tested against reality**, not against the title — a deferral's condition, or a bug's still-reproduces |
| J2 | **One session, one PR.** *Done when* can be satisfied without another session's output; if not, it is a parent (§7) |
| J3 | ***Done when* is checkable by a cold session** — an observable end state, not "improve" or "review" |
| J4 | **No owner decision is hidden inside.** If any step needs his call, split it off. **`Changes contracts: requirements` always does** — what counts as better is his (`CLAUDE.md`, "Whose decision is it") |
| J5 | **A `research` issue links its committed pre-registration** — or writing that pre-registration *is* the issue |
| J6 | **The Source resolves at current `main` and one load-bearing claim in it was verified against the code** (`session-start`'s verify-one-claim, applied at labelling time) |
| J7 | **Prerequisites a fresh worktree lacks are named** — a gitignored graph artifact and its path (`ARTISTPATH_GRAPH`), an archive, credentials. Orca starts sessions in new worktrees, which carry none of these (`session-start` §C) |

## 5. Contracts — the logical-collision check

**A contract is a shared meaning that several pieces of work rely on and that one piece of work can
change.** Each issue declares which it **reads** (would this work be wrong if the meaning changed
while it ran?) and which it **changes**. Two live issues **conflict** when one changes a contract the
other reads or changes; two readers never conflict. Conflicts are *derived* by
`scripts/issues.py conflicts`, never hand-listed on either issue — a hand list is knowledge about a
pair written on one side, and goes stale when either side changes.

| Contract | What it means, plainly | Where its current value lives |
|---|---|---|
| `graph-identity` | Which graph the app serves, and the rule that built it (cap rule, trim, component pruning). Anything quoted "against the graph" reads this | `ApiConfig.graph_path` and the artifact's manifest sidecar (sha256); the build rule in `BuilderConfig` |
| `apg1-format` | The binary layout and metadata keys the builder writes and the API reads | `builder/…/artifact.py` and `api/…/graph_store.py` (kept in lockstep by hand, `CLAUDE.md`) |
| `quantities` | What a shipped number *means* and how it is computed — `pop_raw`, the degree-derived terms, fame and its percentile. **The popularity-semantics case in the preamble is this contract** | `CLAUDE.md` "Quantities carry their currency"; `PRODUCT-REQUIREMENTS.md` "Definitions — the currencies"; the builder code that computes them |
| `cost-function` | How a path is chosen: the cost terms, their weights, what a bypass press does | `ApiConfig` and `api/…/pathfinding.py` |
| `requirements` | What counts as better | `PRODUCT-REQUIREMENTS.md` (`REQ-`), `WHAT-GOOD-LOOKS-LIKE.md`. **Changing it is always his call** (§4 J4) |
| `api-wire` | The JSON shapes the API returns and the frontend consumes | `api/…/models.py` |
| `url-state` | The routes and query parameters — every link already shared must keep resolving | `frontend/src/App.tsx` and the URL decoder; the API router's parameters |
| `edge-behaviour` | What the edge serves, caches and adds for each route: cache behaviours and policies, response headers, edge functions. **Not** capacity or logging, which nobody else's work assumes | `infra/src/artistpath_infra/stack.py` (the distribution), `infra/README.md` |
| `deploy-path` | How an artifact or image reaches production and is verified there: S3 keys, the boot-time sha256 check, the deploy runbook | `infra/app.py`, `ARTISTPATH_GRAPH_SHA256` (`CLAUDE.md`), `infra/README.md` |
| `rituals` | The apparatus's own interfaces: these conventions, `closeout`/`session-start`, `NEXT.md`'s structure, `docs/README.md`'s roles | This file, `.claude/skills/`, `docs/README.md` |

**Declare honestly in both directions.** Under-declaring is the hole this check cannot see: **it
catches only assumptions that were written down.** Over-declaring makes everything conflict with
everything, and a check that always fires gets ignored. The test for *reads* is the question above,
not "does it open the file". **The test for *changes* is: could work that never opens these files
be made wrong by this change?** Editing a file a contract lives in is not changing the contract —
adding access logging to the stack changes nothing anyone else assumes. *(Learned on the first run,
2026-09-28: the list then had one `infra-stack` contract, every issue that edited `infra/` declared
it changed, and seven dispatchable issues produced fifteen conflicting pairs — a check nobody would
have kept reading. Splitting it and applying this test left four, each a real interaction.)*

**Not a contract: two sessions both editing `NEXT.md` or `docs/README.md`.** That is a *physical*
collision, and git reports it as a merge conflict. Contracts exist for the collisions git is silent on.

**When a collision escapes this check, add the contract that would have caught it**, in the same
change to this table, `CONTRACTS` in `scripts/issues.py`, and all three templates' dropdowns —
`scripts/issues-selftest.py` fails if the three disagree. Growing the list is how the check earns
coverage; it never shrinks without evidence (the removal rule in `CLAUDE.md`).

**Where it is checked:**

1. **Before dispatch and at claim** — `python scripts/issues.py conflicts N`. A conflict with a
   `claimed` issue means **do not start**: say so and pick something else. A conflict with another
   `agent-ready` issue means you now hold the contract; the other must wait for your merge.
2. **At merge** — a PR that changes a contract says so in its body (`Changes contracts: …`), and
   `closeout` D5 runs `python scripts/issues.py readers <contract>` and comments on each open issue
   listed: *"`<contract>` changed in #PR — re-check before starting (§4 J1, J6)"*, removing
   `agent-ready` from any whose Source or *Done when* it invalidates. **This step is what catches the
   preamble's case when the second issue was queued but not yet started** — the case the claim-time
   check cannot see.

## 6. The migration, 2026-09-24

*(Kept at §6 because the frozen `NEXT-ARCHIVE.md` cites it by that number.)*

`NEXT.md`'s deferral registry was moved into issues on 2026-09-24. **The registry as it stood is
frozen in `NEXT-ARCHIVE.md`** (the block dated 2026-09-24). Each migrated issue quotes its row and
permalinks it. Rows already struck or discharged were not filed. Accepted residuals and standing
conditions stayed in `NEXT.md`. The Gate 2→3 review's findings were each re-checked against the
current code before filing; only the open and partial ones were filed (fixed: `G3-A4`, `A5`, `A7`,
`S3`, `S7`, `Q6`; decided: `A3`, `Q5`; not filed as deliberate per the review itself: `Q7`).
**Security-sensitive issues withhold the detail** and give file references instead; the dispatched
session re-derives it from the review. `BYP-13` is an umbrella issue linking its three residuals.

## 7. Claiming, and splitting work for parallel sessions

**A claim is the first thing a dispatched session does**, before orienting further — it is what stops
a second dispatcher picking up the same issue:

```bash
python scripts/issues.py conflicts N          # a conflict with a claimed issue: stop (§5)
gh issue edit N --add-label claimed --remove-label agent-ready
gh issue comment N --body "Claimed: branch <branch>, worktree <path>, <date>."
```

**Re-confirm the contract declaration as you claim**: the labeller declared it from the brief, and you
are the first to read the code with the fix in mind. If it changes, edit the body and re-run
`conflicts N` before going further.

Then push the first commit and open a **draft PR saying `Closes #N`** — from then on the linked PR is
the stronger evidence of the claim, and it survives the session.

- **Releasing without finishing:** remove `claimed`, comment where it stopped and what is owed, and
  re-add `agent-ready` only if `lint N` passes and the J-items still hold.
- **A stale claim** (`python scripts/issues.py stale` — claimed, no open PR, no activity for 3 days)
  **may be a live session in another window.** A session releases one only after `git worktree list`
  shows no worktree on the claim's branch; otherwise it names it to the owner.
- **One session may claim several issues** when none conflict, and delegate them to its own
  subagents. That is the "lead delegates" case — it needs no special label.

**Splitting.** When an issue is too big for one PR, or part of it is the owner's, it becomes a
**parent with sub-issues**: the parent keeps the *What* and the overall *Done when* and is never
`agent-ready`; each sub-issue is a full brief (§3) with its own contracts. **Parts that can run at
once are siblings; a part that needs another's output is "blocked by" it.** The native relationships
take an issue's internal id, not its number:

```bash
id() { gh api "repos/{owner}/{repo}/issues/$1" --jq .id; }
gh api -X POST "repos/{owner}/{repo}/issues/PARENT/sub_issues" -F sub_issue_id="$(id CHILD)"
gh api -X POST "repos/{owner}/{repo}/issues/N/dependencies/blocked_by" -F issue_id="$(id BLOCKER)"
```

**Sibling sub-issues that conflict on a contract are not parallel**, whatever the tree says — the
`conflicts` check applies to them like any other pair, and a "blocked by" link between them records
the order.

## 8. Lifecycle

1. **Filed** at the moment of noticing — a deferral files its issue at deferral time (`closeout` A3),
   not at closeout.
2. **Comes due.** When a `deferred` issue's condition is met, **swap the kind** — `deferred` →
   `task` or `bug` — and comment what met it. `session-start` and `closeout` both re-test conditions
   (§9). If it comes due and is the owner's, say so to him instead.
3. **`agent-ready` added** only when the §4 checklist passes, with its `Ready-checked` comment.
4. **Claimed** by the session that takes it (§7); `agent-ready` comes off in the same command.
5. **Worked** on a branch; the PR body says `Closes #N` so the merge closes it, and names any
   contract it changes (§5).
6. **Closed** — *completed* by the PR, or **by hand with a comment** saying what satisfied it (the
   strike-in-place rule from `closeout` A3: the closed issue *is* the evidence it was tracked).
   **Killed** (condition known-unreachable) or **accepted, won't fix** → close as *not planned* with
   the reason. **Never delete an issue.** Closing a blocker unblocks its dependants natively; §9
   finds them.

## 9. The two rituals

**`session-start`** (§B and MT2) lists open deferrals and re-tests each condition against reality,
then runs the mechanical checks:

```bash
gh issue list --state open --label deferred --limit 100 --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\([.labels[].name] | join(","))]"'
python scripts/issues.py lint        # every agent-ready issue against §4's M-items
python scripts/issues.py conflicts   # contract collisions among agent-ready and claimed issues
python scripts/issues.py stale       # claims with no PR (§7)
python scripts/issues.py unblocked   # issues whose blockers have all closed: run §4 on them
```

**`closeout`** (A3) files every new deferral as an issue, closes every discharged one with a comment,
and lists both in the PR body (D5) by number. **D5 also names the contracts the PR changes and runs
§5's merge-time notification** for each.

**A session dispatched by Orca from an issue** is still acting on repository state. `session-start` is
owner-invoked and a session never runs it itself; if it owes it and was not given it, it **says so
once and proceeds** (`CLAUDE.md`). It reads the issue, **claims it (§7)**, then reads `CLAUDE.md`'s
orient table, then works. **In practice the owner starts these as `/session-start <issue URL>`**
(Orca lets him edit the dispatch prompt), and `session-start` claims the issue at the top, before
choosing a track — so the claim needs no line in `CLAUDE.md`.
