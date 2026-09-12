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
| `DLS-M8` | **Item 1's invocation consequences, *verified* 2026-09-12** | (a) `session-start`'s description has **never** loaded into any session: invalid YAML from `7ec8eab` (2026-07-25) until PR #117, and `disable-model-invocation: true` from PR #117 onward — so its **837 chars have never been standing context**, and the owner-only behaviour observed for seven weeks came from `CLAUDE.md` prose alone. Restoring model invocation would load that description for the **first** time, not restore a prior cost. (b) The flag blocks **prose** invocation absolutely — "run the session-start skill" cannot be honoured, however plainly asked — and **trailing arguments after the slash command are the only single-message route** to skill + scope. (c) Frontmatter sweep of all skills and agents: **all valid**, so `DLS-M6`(a) stays a single instance. (d) The global `doc-auditor` is fully shadowed by the project one and does **not** double-load its 335 chars |
| `DLS-M9` | **Why the rituals feel slower, *measured* 2026-09-12** | `session-start`'s body: **7,132 chars (2026-07-22) → 22,083 (2026-09-10)**, a 3.1× growth, of which the single largest step is **+5,338 on 2026-08-05** (the `MT` maintenance track). **PR #117 added 130 chars of frontmatter and no body**, so it is not a cause. Hook wall-clock, 3 runs each: `repo-state` **340 ms** (once, at startup), `context-size-reminder` **244 ms** (every prompt), `log-instructions-loaded` **240 ms** (per instruction file loaded) — together **≈1.1 s** added across a session's opening, and ~0.24 s on every turn thereafter. The dominant cost is the body and the checks it prescribes, not the hooks |

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
| 1 | Settings: `env` block, Notion off here, consultant dispatch denied, `session-start` owner-only | **Done — PR #117.** ⚠ **One unanticipated consequence, found in use 2026-09-12 and repaired the same day (`DLS-M8`):** making the skill owner-only also blocked the owner's own *prose* request for it, so "run session-start, your scope is X" could not be honoured in one message. **Repaired in the skill body, at no standing-context cost**, by consuming `$ARGUMENTS` so `/session-start <scope>` carries the scope. **What is still open is `DLS-Q7`** | — |
| 2 | Guard tests: builder/API format lockstep (golden bytes), no new code against pre-rename aliases | **Done — PR #118** (verified 2026-09-12: `test_apg1_fixture_lockstep.py` and `test_no_alias_use.py` in both packages, plus `test_frozen_script_aliases.py`). ⚠ Its coverage deferral is live in `NEXT.md`: the tests pin only the fixture's four **base** metadata keys | — |
| 3 | Hooks: git staging safety and stop-and-ask rules (user level); context-size reminder; repo-state report at session start | **Done — PR #117 for the two project hooks** (both in `.claude/settings.json`, verified 2026-09-12), git safety live in user-level settings. ⚠ **One piece remains unbuilt and unasked**: a hook refusing commits on `main`. It is carried in `NEXT.md`'s item 4–6 deferral | `DLS-Q6` — **answered** |
| 4 | `CLAUDE.md` restructure: package-level CLAUDE.md files, `.claude/rules/`, narrative out of the always-loaded file, ≤200 lines | Not started | ⛔ **Still gated, and only by the `DLS-T1` read** — at **1 qualifying session of 3** as of 2026-09-12, window closing 2026-09-24. `DLS-Q3`, `DLS-Q4` answered; the `LBD-` closeout landed 2026-09-11 |
| 5 | `NEXT.md` deferral demotion; map rebuilt around each document's own role line; lint checks for map/role agreement, frozen-document diffs and pre-registration sections | Not started | ✅ **Gates all cleared** — `DLS-Q1` and `DLS-Q2` answered 2026-09-11, the `LBD-` closeout landed 2026-09-11. It is held only by the items 4–6 plan, which §4 requires and which item 4's gate delays |
| 6 | Skills: `closeout` under 500 lines with supporting files, command output injected into both rituals, the D6 measurement as a script | Not started. **`DLS-M9` now sizes its case**: `session-start` is on the same growth curve at 363 lines, and the ritual latency the owner noticed is the body, not the hooks | Items 4 and 5 |
| 7 | Memory: remove entries that repeat `CLAUDE.md` | Not started. ⚠ **`DLS-Q4`'s ruling applies to it**: a removal needs evidence that sessions no longer need the text **plus his sign-off**, so this item proposes and does not delete | — |

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
| `DLS-Q7` | *(Raised 2026-09-12 by the owner, from use.)* The `$ARGUMENTS` repair covers `/session-start <scope>` but **not** a prose ask, which the flag blocks absolutely. The instruction has to reach a session that has **not** invoked the skill, so the skill body cannot carry it — a body loads only on invocation, which is the one moment it is not needed. Three homes, and they trade certainty against standing cost: **(a)** `CLAUDE.md`'s `session-start` bullet, one sentence, certain, **+147 chars on every future session (39,766 → 39,913)**; **(b)** project memory, **free** and already done — `memory/no-session-start-hook.md` carries it in its body and description — but recall is unpredictable, so it is a good bet rather than a guarantee; **(c)** neither, and accept one round trip on the rare prose ask. **(b) is in place, so the live question is only whether to buy (a) on top of it.** His call: it is the layer that taxes every session. |

### 5a. The owner's answers, 2026-09-11

| ID | Answer | What it unlocks |
|---|---|---|
| `DLS-Q1` | **Allow top banners** on frozen documents, with a lint check that nothing below the banner changed | Item 5: the frozen-document diff check; map rows stop carrying warnings |
| `DLS-Q2` | **Generate the map from each document's own role line**; hand-written text only for warnings | Item 5 |
| `DLS-Q3` | **Stories move word for word, with their rule, into the rule or skill file that loads when it is relevant**; pure history may become HTML comments | Item 4. The path-scoped half waits on the `DLS-T1` read |
| `DLS-Q4` | **Move verbatim**, with a check that every sentence still exists somewhere; **remove a rule only on evidence that sessions no longer need it, plus his sign-off** | Item 4, which also carries the amendment to `CLAUDE.md`'s "rules never expire" and `closeout` D6's "compressing live prose" wording |
| `DLS-Q5` | **Deny reads of `docs/reference/**` only**; the narrative journal stays readable, since a session may be asked to update it | Item 3, landed with the instrument |
| `DLS-Q6a` | **Add the context-size reminder** | Item 3, landed with the instrument |
| `DLS-Q6b` | **Add the repo-state report at session start** (facts only; it never runs or suggests `session-start`) | Item 3, landed with the instrument. Reverses the preference recorded in memory against a session-start hook |

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

### 6b. Instrument log after merge — observations, exclusions and confounds

**Not part of the pre-registration.** §6 is frozen and nothing here amends it. This is the running
record the read will consume, kept here so `NEXT.md` can point rather than grow. **Opened
2026-09-12.**

**Observations so far.** The underlying log is `.claude/logs/instructions-loaded.jsonl`, which is
gitignored, so this table is the durable copy.

| # | when (UTC) | session | `agent_type` | trigger | result | counts toward `C1`? |
|---|---|---|---|---|---|---|
| 1 | 2026-09-11 | the `LBL-` write-up session | none | specs, opened **via Bash** | no load | **No** — not a qualifying session; see the confound below |
| 2 | 2026-09-12 15:59 | `58bcc7f5` | `consultant` | the `LBD-` fidelity spec | `path_glob_match` | **Unruled** — the read must settle it |
| 3 | 2026-09-12 16:02 | `652d311c` | none | the alpha rollout roadmap | `path_glob_match` | **Yes — qualifying session 1 of 3** |
| 4 | 2026-09-12 16:28 | `fb3fe80b` | none | none; read via Bash | no load | **No** — same confound as #1 |

**`DLS-T1-X1` — the Bash-reading confound, and what it does and does not mean.** Sessions here
often run under an instruction to read files with `cat`/`sed` through Bash rather than the `Read`
tool. §6's unit is *"whose transcript shows a **Read** of any file under either path"*, so such a
session is **not a qualifying session at all**: it contributes nothing, and it is **not** a miss
against `C1`. **For `C1`'s scoring the danger is in the reading** — corrected 2026-09-12 from "entirely in the
reading", which understated it; see `DLS-T1-X4`, where the rule turns out not to reach such a
session at all. A log showing a session that plainly
worked on specs, with no rule load beside it, looks exactly like a failure. Two of the four rows
above are already of that shape. **The read must exclude any session whose spec and plan opens
were not `Read`-tool opens, and say how many it excluded.** *(Raised by a session that hit it,
2026-09-12; its own framing was "a silent false negative against `C1`", corrected here to
"not a qualifying session", which is the difference between repairing the instrument and
documenting an exclusion.)*

**Why sessions differ, established 2026-09-12. It is configuration, not chance, and it changes the
forecast.** Two separate causes, both verifiable:

- **Tool grant.** `.claude/agents/consultant.md` declares `tools: Read, Grep, Glob` — **no Bash**.
  A consultant session therefore *cannot* read through the shell, so every file it opens is a
  `Read`-tool open. That is why the only non-authoring `path_glob_match` in the log came from one.
- **An injected preference on main sessions, which belongs to `Auto Mode` and NOT to the browser
  integration.** ⚠ *Corrected 2026-09-12, same day, after a probe quoted both blocks in full. The
  first version of this bullet and of §7 said the Chrome integration delivered it. That was wrong,
  and it was wrong because in the authoring session's own prompt the sentence sits directly below
  the `claude-in-chrome` instructions. Adjacency was read as ownership.* The instruction is
  *"Do your work through the Bash tool wherever it can accomplish the job: read files with cat,
  head, or sed -n… rather than using the dedicated Read, Edit, or Write tools."* It lives in a
  distinct **`## Auto Mode Active`** system-reminder, alongside that mode's bias against stopping
  to ask and its git-safety guidance. **Neither block references the other and there is no
  dependency between them.** It is not a project setting and appears in no repository config.

**Consequence for the read, and it is not small.** A qualifying session is in practice *a main
session that overrode its own default*. Of the two main sessions on 2026-09-12, one qualified, and
only because it chose `Read` deliberately for one plan. **So the 2026-09-24 window is considerably
more likely to close on fewer than three qualifying sessions than the bare count suggests**, which
sends `C1` to §6's substitute-probe branch. Deliberately opening a plan or spec with the `Read`
tool is **not** gaming the result: `C1` asks whether the rule loads *on such an open*, not how
often sessions choose one, and §6's own positive control did exactly that.

**`DLS-T1-X2` — working in a worktree does NOT make a session invisible. Where it was *launched*
is what decides.** ⚠ *This entry replaces a wrong version committed earlier the same day, which
said a session working in a worktree writes to `<worktree>/.claude/logs/` and loses it. That is
false for the common case and the correction is the point of the entry.*

**Verified 2026-09-12.** Session `e9f8ccc4` was launched in `C:\dev\music-app`, took a worktree as
its first action, and did all its work there. Its log lines are in the **main tree's** log, stamped
`cwd: C:\dev\music-app`. A session's settings and hooks are bound at launch and do not follow it
across a `git worktree add`. So:

- **A session launched in the main tree that then takes a worktree keeps logging to the main tree,
  and stays eligible under §6's unit**, which asks where it was *started*. This is the pattern the
  owner uses, so the count is not leaking.
- **A session launched with its working directory already inside a worktree** would load that
  worktree's settings, and its log would be gitignored and destroyed with the worktree. **Untested
  — stated as inference, not observation.** Consistent with the `music-app-lbl` worktree having no
  `.claude/logs/` directory at all as of 2026-09-12, which is what a hook that never ran there
  looks like.

**The log is not being repointed**: §6 freezes the instrument until `C1` is read.

**`DLS-T1-X3` — three synthetic rows to exclude, and they are mine.** Lines 15–17, timestamped
**2026-09-12T16:16:01.650Z, 16:16:02.023Z and 16:16:02.400Z**, have every field null. They are not
harness output. **This session produced them** by piping an empty JSON object into the hook three
times while measuring its wall-clock for `DLS-M9`. **The read excludes all three.** They cannot be
mistaken for a qualifying session, since they carry no session id, but they do mean a line count
of the log overstates by three. It also establishes that the hook will append a blank row rather
than reject malformed input, which is worth knowing before anyone treats the log as self-validating.

**`DLS-T1-X4` — a Bash read defeats the RULE, not merely the logging. This is the finding that
bears on item 4.** *(Owner's question, 2026-09-12; answered by a controlled pair rather than by
reasoning.)*

**Design.** Two fresh subagents, same file, same 40 lines, **one variable: the tool**. Both barred
from touching `.claude/` so neither could obtain the rule text by reading it. Each was asked what
had appeared in its own context.

| arm | tool | rule in context? |
|---|---|---|
| A | `head -40` via Bash | **No** |
| B | `Read`, limit 40 | **Yes** — quoted verbatim, delivered as a system-reminder immediately after the read result |

**Arm A is a real negative, not a failure to observe.** It reported four *other* system-reminders
arriving alongside its Bash output, including the auto-mode guidelines, so the injection channel
was demonstrably working in that session. The rule specifically did not fire.

**So the mechanism is defeated by how a file is opened, and the text simply never arrives.**

⚠ **`C1` can pass and still not license item 4, and this is a blind spot in §6 rather than a
defect in it.** `C1` measures reliability **conditional on a `Read`-open**. It says nothing about
what share of real sessions open plans that way — and under `DLS-T1-X1` most sessions here do not.
A rule that loads in 100 % of qualifying sessions while reaching almost no real ones is a mechanism
item 4 must not move load-bearing text onto. **The decision item 4 needs is coverage; `C1` measures
fidelity.** Whoever reads `C1` must state which of the two they are reporting.

**`DLS-T1-X5` — subagent loads are attributed to the parent session and carry no agent marker, so
`C3` is not readable from this log and `C1`'s count can be inflated.** Arm B above was an
Agent-tool subagent. Its load was written as
`2026-09-12T17:00:45.843Z`, `session_id: 652d311c…` — **the parent's id** — with `agent_type: null`,
indistinguishable from a main session's own Read. Two consequences:

- **`DLS-T1-C3`** says subagent behaviour is *"recorded from log lines carrying an `agent_type`"*.
  Agent-tool subagents carry none, so **C3 cannot be read this way**. The one row that does carry
  `agent_type: consultant` is a *launched session* using an agent flag, not a subagent, which is
  why it looked as though the field worked.
- **A session that never opens a plan itself, but dispatches a subagent that does, produces a
  `path_glob_match` row under its own id** and reads as a qualifying session. **The read must
  confirm from the transcript, not the log, that a counted session made the open itself.** The one
  qualifying session counted so far, at `16:02:16`, was a direct `Read` by the main session before
  any subagent had been dispatched in it.

## 7. Proposal for item 4's delivery mechanism, 2026-09-12

**Proposes; decides nothing.** Item 4 changes the rules every future session runs on, so adoption
is the owner's. What is settled here is methodology: which mechanisms can carry load-bearing text
and which cannot.

### 7.1 Measured

| | |
|---|---|
| `Bash` tool calls, all project transcripts | **3,205** |
| `Read` tool calls, same | **185** |
| ratio | **about 17 to 1** |
| `Skill` invocations, same | 32 |
| browser tool calls, all time | **26**, on two days, in 3 of 33 transcripts |
| `CLAUDE.md`, total | 39,766 chars |
| its "Writing and reviewing plans here" section | **9,048 chars, 22.8 %** |

*(Transcript counts by the method `DLS-M7` used for Notion, over the same 33 transcripts.)*

### 7.2 What I infer, in plain terms

- **Path-scoped rules cannot carry load-bearing text here.** `DLS-T1-X4` showed the rule simply
  does not arrive when a file is opened through the shell, and sessions here open files through the
  shell about seventeen times for every once they use the `Read` tool. The guidance would be absent
  for most sessions, **with nothing in the session to indicate anything was missed.**
- **The disqualifying property is not the ratio, it is the invisibility.** Even if the ratio
  changed tomorrow, delivery would still depend on a session mode that is set outside the
  repository, is not recorded in it, and gives no signal when it flips. A mechanism that can be
  switched off silently by something the project does not control is not one to move text onto that
  a session must not lose.
- **Disabling the Chrome integration would NOT fix this, and that is the load-bearing correction.**
  *(Owner asked directly, 2026-09-12, and said he was comfortable removing it.)* A probe quoted
  both injected blocks in full: the Bash preference is in **`## Auto Mode Active`**, not in the
  `claude-in-chrome` instructions, and neither block references the other. **Removing the extension
  would cost the browser tooling and change reading behaviour not at all.** Two earlier entries here
  said otherwise and are corrected above.
- **The switch is `Auto Mode`, and that makes the mechanism *worse* to depend on, not better.** Auto
  Mode is toggled for reasons that have nothing to do with documentation — it also governs whether a
  session presses on without asking. So whether guidance reaches a session would be a side effect of
  an unrelated operating choice, made per session, recorded nowhere in the repository. **That is the
  definition of conditional and silent**, and it is a stronger argument against path-scoped rules
  than the raw ratio was.
- *(Separately, on the extension's own merits: it is in genuine if rare use — 26 calls on two days
  across 3 of 33 transcripts, the substantive run being 23 calls on 2026-09-11 driving the
  blind-listen page at `127.0.0.1:8765` with screenshots, clicks and page scripting. Removing it
  would cost that harness and save little. It is not this problem's lever either way.)*
- **There is no free mechanism, and the honest framing is certainty against cost.** Always-loaded
  text is the only delivery that is certain, and it is certain *because* it is always loaded, which
  is the cost item 4 exists to reduce. A skill is cheap because only its `description` is standing,
  but invocation is a judgement rather than a trigger. Path-scoped rules looked like the best of
  both and are in fact the worst: conditional *and* silent.

### 7.3 What I propose

0. **Change nothing in the environment. Neither switch is worth pulling, and that is now checked
   rather than assumed.** Disabling the browser integration does not touch reading behaviour
   (§7.2). `Auto Mode` does, but it is **a permission classifier** whose job is letting routine
   operations run without an approval prompt; the Bash preference merely rides along with it.
   **Turning off a session's permission handling to change how it opens files is a bad trade by a
   wide margin.** *(Per-project mechanisms exist for both, if ever wanted for their own reasons:
   `deniedMcpServers` for the integration, `/auto-mode-setup` for the mode. Documented, untested
   here, and deliberately not applied.)*
1. **Item 4 does not use path-scoped rules for anything a session must not lose.** This is `C1`'s
   own failure branch, reached by measurement rather than by the read. **With step 0 settled there
   is no configuration that rescues the mechanism**, so this is a determination rather than a
   preference.
2. **Sort text by one question: what happens if a session never sees it?** *Silent wrong work* →
   it stays in `CLAUDE.md` and the cost is accepted. *Work that visibly stalls or asks* → a skill.
3. **The first move is the plan-writing section**, because it is the largest single block with a
   natural trigger and the ruling for it already exists (`DLS-Q3`: stories move word for word with
   their rule). Moving it to a skill body trades **9,048 standing chars for a description of
   roughly 300** — most of item 4's target in one step, with nothing reworded.
4. **Keep reading `DLS-T1`, and report fidelity and coverage separately.** It is nearly free now,
   it still answers whether the mechanism is *reliable when it fires*, and `DLS-T1-X4` records why
   a pass must not be read as licence.

### 7.4 Weakest link

**That a skill is invoked when it is relevant.** It is a judgement, not a path match, and 32
invocations across 28,292 records is thin evidence either way. What makes it acceptable where a
path-scoped rule is not: **a skill that should have been invoked and was not is visible in the
transcript**, whereas a rule that did not load leaves no trace anywhere. **What would falsify this:**
a session writing a plan, with the skill available, that neither invokes it nor asks. That is worth
watching for before the second and third blocks move, and it is the cheap reason to move one block
first rather than all of them.

**What I would abandon cheaply:** the claim that ~300 chars is the right description size, and the
ordering of blocks after the first. **What I would defend:** that path-scoped rules are
disqualified for load-bearing text, which rests on a controlled pair and a 17-to-1 ratio.

## 8. Item 7 — memory entries that repeat the always-loaded file, 2026-09-12

**Proposes; deletes nothing.** `DLS-Q4`'s ruling governs: a removal needs evidence that sessions no
longer need the text **plus his sign-off**. Every claim below was checked against the file it
duplicates, not assumed.

**First, a correction to item 7's own framing.** Item 7 is worth doing, but **not for the reason it
was written.** Deleting a memory file saves **nothing** in standing context — bodies load on recall
only. The only standing cost is the one-line entry in `MEMORY.md`, and the four candidates are
**750 of its 3,092 bytes**. **The real argument is contradiction:** a memory that restates
`CLAUDE.md` is a second copy that can go stale, and when it does, a session gets two answers and no
way to tell which is current. That is the same failure as restating a figure.

| memory file | what it duplicates | verified | index line |
|---|---|---|---|
| `no-commercialization-ruling.md` | **The ruling is in the repo**, `PRODUCT-REQUIREMENTS.md` `REQ-43`. The memory says so itself. | `REQ-43` present, 6 mentions | 311 ch |
| `path-quality.md` | *"figures live in exactly one file, cite it, never restate"* — `CLAUDE.md`'s orient table says this **twice** | "Exactly one file" ×2 | 97 ch |
| `roadmap-pointer.md` | *"status and the next action live in `NEXT.md`"* — said by `CLAUDE.md`'s orient table **and** by `MEMORY.md`'s own header | both present | 244 ch |
| `env-onedrive-uv.md` | `UV_LINK_MODE=copy`, in `CLAUDE.md` 7 times — **and now enforced by the harness**, `settings.json` sets it in `env` | both confirmed | 98 ch |

**Two cautions, because three of these are load-bearing in a way a bare count misses.**

- **`CLAUDE.md` points *at* `env-onedrive-uv.md` by name** (*"detail in `memory/env-onedrive-uv.md`"*).
  Deleting it dangles that pointer. **Either keep it or edit `CLAUDE.md` in the same change** — and
  the latter touches the standing layer, so it is his either way.
- **`roadmap-pointer.md` is `MEMORY.md`'s designated "START HERE".** Removing it needs the index
  line rewritten to point somewhere, not simply dropped.
- **`no-commercialization-ruling.md` is the one clean removal**: the ruling lives in a governing
  repository document, and the memory's own index line already says so. *(Its `REQ-44` gate — confirm
  with the owner before building on it — would need to survive into whatever replaces it.)*

**Not proposed for removal, and why, since the value is in the ruling-out:** `deploy-environment-traps`
(richer than `session-start` §D, and that is a skill body which loads only on invocation),
`working-style`, `stop-refining-instrumental-artifacts`, `cheapest-experiment-first` (duplicated in
a skill body, not in `CLAUDE.md`), `clip-resolution-bugs`, `crawl-resume`, `no-session-start-hook`
(rewritten today), and `project-state` — whose *deferred product ideas* half appears nowhere else.

**Done without asking, because it is a correction rather than a removal:** `MEMORY.md`'s line for
`no-session-start-hook` said a repo-state `SessionStart` hook *"IS wanted (2026-09-11)"*. It was
built and shipped; the line now says so. `D6` governs *growing* the standing layer, not correcting
it.

⚠ **A first attempt at that line also added the prose-invocation fact, growing the index by 72
bytes, and was rolled back to a pure correction.** Growing the always-loaded layer is the owner's
call and this session had just written a check saying so. **The fact is not lost** — it is in
`no-session-start-hook.md`'s body and `description`, which cost nothing standing. **Whether it is
worth an index line too is part of `DLS-Q7`**, as its cheapest variant.

**One measurement caveat, stated rather than smoothed over.** `MEMORY.md` was **3,092 bytes** at
this session's start and is **3,092 bytes** now, but it read **3,072** immediately before the edit
above. Something outside this session changed it in between. The edit was a single targeted
replacement of one line and preserved every other, so nothing was clobbered — but **the net delta
attributable to this session is not cleanly measurable**, and the figure should not be cited as if
it were.

§4's *State* column is as of this document's first commit; status lives in `NEXT.md`.
