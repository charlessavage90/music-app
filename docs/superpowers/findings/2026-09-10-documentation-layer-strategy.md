# Documentation layer strategy — what sessions pay for context, and what should move where, 2026-09-10

**Role: ACTIVE — AUTHORITATIVE for its own measurements (`DLS-M1`–`DLS-M7`) and for the
`DLS-T1` pre-registration (§6).** Owns no scoring or path-quality figures. It proposes and
decides nothing: the six questions in §5 are the owner's. Scripts:
[`builder/analysis/2026-09-10-dls-context-layer/`](../../../builder/analysis/2026-09-10-dls-context-layer/README.md).
Item 1 of §4 has already landed as PR #117.

Written by an advisory session asked to optimise the documentation layers for cost, speed and
accuracy, and then to check the project's conventions against the current Claude Code
documentation rather than assume them correct. The conventions examined were largely written
with older models.

---

## 0. Scope and method

- **Repository:** sizes at `341faf5` (after PR #117). Characters are counted with CRs stripped.
- **Session transcripts:** every `.jsonl` retained on 2026-09-10 under this project's two
  Claude Code project directories (the current one and the pre-migration OneDrive one): **28 main
  sessions and 45 subagent transcripts**, mostly from August and September. Older sessions have
  been pruned by retention, so this is a sample of recent work, not the project's history.
- **Tokens** are estimated at about 3.8 characters per token. Summed input tokens count cached
  tokens at full weight; cached tokens are billed at a discount, so **a share of tokens is not a
  share of cost**.
- **Current guidance** was read on 2026-09-10 from code.claude.com: *Best practices*, *How Claude
  remembers your project*, *Skills*, *Hooks*, *Settings* and *Subagents*.
- **Harness facts** marked *verified* were observed on this machine (Claude Code 2.1.268) by
  starting sessions with `claude -p --output-format stream-json --verbose` in the unchanged tree
  and in a branch, and comparing their startup inventories. That is PR #117's evidence.

## 1. Measured

| ID | What | Measurement |
|---|---|---|
| `DLS-M1` | Always-loaded instructions | `CLAUDE.md` **578 lines**, 39,650 chars, 150 bolded phrases. `~/.claude/CLAUDE.md` 108 lines, 5,802 chars. `closeout` D6's unconditional total **51,694 → 50,843** chars across PR #117 |
| `DLS-M2` | Shape of session cost | 7,889 turns; 2.06 billion summed input tokens; **mean 261k tokens of context per turn**; first-turn context 62–81k; peak 665k; **0 compactions** in 28 sessions |
| `DLS-M2a` | Shares of summed input | Always-loaded text the project controls ≈ **5.3 %**; `CLAUDE.md` alone ≈ 4.1 %; its "Writing and reviewing plans here" section ≈ 0.9 %; every `.md` Read result, carried across later turns ≈ 2 % (heuristic) |
| `DLS-M3` | `docs/README.md` (the map) | 392,781 bytes, 538 lines. "Active" is 323,151 chars (82 %), 243 rows, median 1,296 chars. 130 Active rows contain SUPERSEDED / HISTORICAL / COMPLETE / DONE / CLOSED (a loose match that overcounts); 95 name July documents. "Current state" is 10,045 chars and says of itself that it has lagged since 2026-07-26. **The Read tool refused the whole file 10 times.** Touched by 48 of 184 commits since 2026-08-20 |
| `DLS-M4` | `NEXT.md` | 60,438 bytes, 377 lines. "Deferred, with conditions" is 36,495 chars: 67 rows, **24 already discharged (17,075 chars)**. Read in full twice on 2026-09-10. Touched by 43 of 184 commits since 2026-08-20 |
| `DLS-M5` | Rituals | `closeout` 931 lines (~14.7k tokens); `session-start` 360 lines. `doc-auditor`: 20 dispatches, median 109 turns and 6.6M summed input tokens per run, the most per run of any subagent type |
| `DLS-M6` | Harness, *verified* | (a) `session-start`'s frontmatter was **invalid YAML from `7ec8eab` (2026-07-25) until PR #117**, so its description never loaded; (b) a session started inside a git worktree loads the main repository's memory directory; (c) `permissions.deny: Agent(consultant)` refuses dispatch while `claude --agent consultant` still runs; (d) settings `env` reaches Bash commands; (e) disabling the Notion plugin for the project removed 43 tools, 10 slash commands, 1 MCP server and 1 plugin from every session |
| `DLS-M7` | Notion usage | 0 tool calls in 7,889 turns |

## 2. What I infer from it

In plain terms, for someone who has not read the numbers:

- **Most of what a session costs is the conversation it drags along, not the documents it opens.**
  Sessions here run very long without ever being compacted, so everything already in context is
  re-sent on every turn. Reading a large document is expensive mainly because it then rides along
  for hundreds of turns. The next-largest piece the project controls is the text loaded into every
  session before it reads anything.
- **The map has become a status log that nobody can read whole.** Its rows narrate progress and
  supersession, every closeout rewrites them, and they are where concurrent sessions collide. A
  session reading from the top meets a section that says it is out of date.
- **`NEXT.md`'s deferral table is growing the same way its status blocks once did**: discharged
  rows are struck and kept in place, so they never leave.
- **Several conventions here disagree with the current Claude Code guidance.**
  - That guidance targets **under 200 lines** per CLAUDE.md and says long files lower adherence.
  - It calls CLAUDE.md **advisory**, and says "must happen every time" belongs in hooks or
    permission rules.
  - It says to **prune and test by observing behaviour**, where this project's rule is that rules
    never expire.
  - It keeps SKILL.md files **under 500 lines**.
  - It offers `disable-model-invocation` for user-only skills.
  - It **strips HTML comments** from CLAUDE.md before Claude sees them.
  - It loads **subdirectory CLAUDE.md files and path-scoped rules only when matching files are
    read**.

  The project's rule against rewording live prose came from two real losses. The guidance suggests
  that the remedy is to **move text word for word to where it loads when needed**, not to keep
  everything loaded everywhere.
- **Instructions the harness can enforce are carried as prose.** About fifteen rules here are
  mechanical: environment variables, git staging, a denied agent, frozen-document edits,
  pre-registration structure, the builder/API format lockstep. Each can be a setting, hook, lint
  check or test, which also removes the audit work of checking them.

## 3. Weakest link

- **The adherence claim is the vendor's general finding, not measured here.** This project has two
  recorded cases where shortening an instruction cost the clause that made it work. Before any
  removal: move text verbatim, check mechanically that every sentence still exists somewhere, log
  which instruction files load (`DLS-T1`'s instrument), and watch the failure each moved rule
  targets.
- **Path-scoped rules load when a matching file is *read*.** A session writing a brand-new plan
  without opening any existing one might never load it. `DLS-T1` tests this before item 4 relies
  on it.
- **The sample is 28 recent sessions on one machine.** The shares in `DLS-M2a` would move with a
  different mix of work. The ordering (conversation length ≫ always-loaded text > document reads)
  would survive a lot of movement; the individual percentages would not.

## 4. The plan of work

| Item | What | State | Gated by |
|---|---|---|---|
| 1 | Settings: `env` block, Notion off here, consultant dispatch denied, `session-start` owner-only | **Done — PR #117** | — |
| 2 | Guard tests: builder/API format lockstep (golden bytes), no new code against pre-rename aliases | In progress, branch `guard-tests` | — |
| 3 | Hooks: git staging safety and stop-and-ask rules (user level); context-size reminder; repo-state report at session start | Git safety in progress at user level; the other two wait on `DLS-Q6` | `DLS-Q6` |
| 4 | `CLAUDE.md` restructure: package-level CLAUDE.md files, `.claude/rules/`, narrative out of the always-loaded file, ≤200 lines | Not started | `DLS-T1` read, `DLS-Q3`, `DLS-Q4`, the live `LBD-` session's next closeout |
| 5 | `NEXT.md` deferral demotion; map rebuilt around each document's own role line; lint checks for map/role agreement, frozen-document diffs and pre-registration sections | Not started | `DLS-Q1`, `DLS-Q2`, the `LBD-` closeout |
| 6 | Skills: `closeout` under 500 lines with supporting files, command output injected into both rituals, the D6 measurement as a script | Not started | Items 4 and 5 |
| 7 | Memory: remove entries that repeat `CLAUDE.md` | Not started | — |

**Items 4–6 get a written plan** because they change the rules every future session runs on and
depend on each other in a fixed order. At roughly twelve tasks, the plan must name its handoff
points; they fall between items 4, 5 and 6, one PR each. **The plan should be written by a fresh
session from this document and the owner's answers to §5**, not by the session that wrote this.

## 5. Questions that are the owner's

Each changes a governing convention or what sessions may read, which is why it is his.

| ID | Question, in plain terms |
|---|---|
| `DLS-Q1` | May a frozen document get a banner at its top pointing at what supersedes it, with a lint check that nothing below the banner changed? Git history already preserves the original. |
| `DLS-Q2` | Should the map stop carrying a hand-written row per document, and be generated from each document's own role line, keeping hand-written text only for warnings? |
| `DLS-Q3` | Where do incident stories go when they leave `CLAUDE.md`: HTML comments, which the owner and editors see but Claude never does, or relocated rule and skill files, which Claude sees only when relevant? |
| `DLS-Q4` | Should "rules never expire" and "never compress live prose" become "move verbatim, then remove a rule only after observing that sessions no longer need it"? |
| `DLS-Q5` | Should reading `docs/reference/` and the narrative journal be blocked by a permission rule, rather than asked of sessions in prose? |
| `DLS-Q6` | Two hooks: one that reports repo state (other worktrees, uncommitted files) when a session starts, reversing the preference recorded in memory; and one that tells a session when its context has grown past a threshold. |

## 6. `DLS-T1` — does a path-scoped rule load by itself? (pre-registration)

**Committed before the instrument exists on `main`; the commit timestamp is the evidence.**

**Plain sentence, fixed here and quoted thereafter:** *when a session opens a plan or a spec, does
a rule scoped to those folders arrive in its context without anyone asking for it?*

**Instrument.**
- `.claude/rules/plans.md`, scoped to `docs/superpowers/plans/**` and `docs/superpowers/specs/**`.
  It is **a pointer only**, about 80 tokens: `CLAUDE.md`'s plan-writing section is untouched and
  stays authoritative, so nothing a session is told changes during the test.
- `.claude/hooks/log-instructions-loaded.mjs`, registered on the `InstructionsLoaded` event. It
  appends one line per instruction file loaded to `.claude/logs/instructions-loaded.jsonl`
  (gitignored), with the load reason.

**Unit.** A *qualifying session* is a main session started in `C:\dev\music-app` whose transcript
shows a Read of any file under either path.

**Sample and window.** The first **three** qualifying sessions after this merges to `main`, or
**14 days** (to 2026-09-24), whichever comes first.

**`DLS-T1-C1` — primary** (*does the rule load in every session that opens a plan or spec*). It
passes only if every qualifying session has a log line for `plans.md` with load reason
`path_glob_match`, at or after its first matching Read. **Any one miss fails it.** Why any
difference is decisive: the documentation describes the mechanism as deterministic, and item 4
would move guidance that sessions must not lose. A mechanism that misses one session in three is
not one to move load-bearing text onto.

**`DLS-T1-C2` — descriptive, no threshold** (*does creating a new plan, without opening an
existing one, load the rule*). Read from any qualifying or probe session that Writes a new file
under either path before any matching Read.

**`DLS-T1-C3` — descriptive, no threshold** (*do subagents load it when they open a plan*).
Recorded from log lines carrying an `agent_type`.

**Held constant, and why.**
- **The instruction text sessions receive.** The rule is a pointer and `CLAUDE.md` is not edited
  by this track. The live `LBD-` session may edit `CLAUDE.md` at its closeout, but that changes
  content, not whether a path-scoped rule loads.
- **The Claude Code version is not constant.** The CLI can update itself during the window, and
  loading behaviour could change with it. Each transcript records its version; the read reports
  the version of every qualifying session.

**Positive control, before merge.** On the branch, one probe session that reads only a
non-matching file must log **no** `plans.md` load; one that reads a plan must log it. A logger that
cannot be shown to stay silent proves nothing by speaking.

**Reads.**
- **C1 passes** → item 4 may move guidance that applies to one part of the tree into path-scoped
  rules. For guidance about *creating* plans, C2 decides whether a one-line pointer stays in the
  root file.
- **C1 fails in any session** → item 4 does not rely on path-scoped rules for load-bearing text; it
  uses skills, or keeps the text in the root file. The read names the session and its version.
- **Fewer than three qualifying sessions and the window still open** → "not yet readable". Nothing
  in item 4 may rely on the result yet.
- **Window closes with no qualifying session** → no read from real use. Five probe sessions that
  each open a different plan are run as a substitute sample, and the read says it is a substitute.

**The instrument stays in place until C1 is read.** No session removes the logging hook or the
rule before three qualifying sessions have run or the window has closed, whichever comes first.

### 6a. Instrument check, 2026-09-10, before merge

These probes ran on the `doc-strategy` branch after the pre-registration above was written and
before it was committed (`a00d484`). The sample `DLS-T1-C1` reads is sessions after merge, which
none of this could have seen. Three `claude -p` probe sessions ran in the branch worktree on
Claude Code 2.1.268:

| Probe | What the session did | Log lines for `.claude/rules/plans.md` |
|---|---|---|
| Negative control | Read `builder/README.md` only | **none**: only the two CLAUDE.md files, at session start |
| Positive control | Read a plan under `docs/superpowers/plans/` | **one**, load reason `path_glob_match` |
| `DLS-T1-C2` probe (substitute, descriptive) | Wrote a new file under `docs/superpowers/plans/` without reading anything first | **none** |

**Read:**
- The instrument stays silent when it should and fires when it should, so a result from real use
  will mean something.
- The `C2` probe suggests, provisionally, that *creating* a plan without opening one does not bring
  the rule in. It is one probe session, not the pre-registered sample.
- **`DLS-T1-C1` is not yet readable**, because its sample starts at merge.

§4's *State* column is as of this document's first commit; status lives in `NEXT.md`.
