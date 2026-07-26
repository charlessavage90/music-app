# Execution log — context-layer maintenance, 2026-07-26

**Role: COMPLETE.** The retained record for the skills-and-agents work on branch
`skills-scope-updates` (PR #26). Touches no code, no graph, no weight, no config knob, and
restates no figure it does not own.

Identifiers are namespaced **`CLM-`** — censused against `ASC-`, `BYP-`, `DRV-`, `FMS-D`,
`FMS-N`, `FMS-P`, `MKS-` and `TF-D` before use, and free.

This log exists mainly because **closeout D6 requires the standing-layer delta to land in a
retained log rather than only in commit messages** — the log is the only place the repo half
and the `memory/` half can be added together. §4 is that record. The rest is what would
otherwise have evaporated with the session.

---

## 1. What changed

Four files in the standing context layer, all owner-directed. Reasoning is in the commit
messages, which were written to be the record; this section is an index, not a restatement.

| Change | Commits |
|---|---|
| `session-start` scoped by what a session does, not what it is; plus the flag permission | `112303b`, `990a36e` |
| `closeout` **A5** — release the processes this session started | `12a0496`, `ba29981` |
| `closeout` **D7** — hand over the `RETIRED-` rename line | `a5c5a72` |
| `consultant` — full structure fires once per decision; prompt delineation specified | `9b8ff51`, `cfbbc81` |
| `ml-graph-analyst` — F1, and the harness that does not have it | `e9688f6` |

Two commits carry a discussion session's work, committed here because that session did not
own commits in this tree: `c3f9202`, `37a11e6`. Its messages are verbatim and its
attribution is its own.

## 2. Decided against — no other artifact records these

**`CLM-1`. "Closeout should tell the owner to close retired terminals" — proposed, then
withdrawn.** The owner keeps a retired session's terminal open deliberately: to confirm the
handoff landed, and to ask the old session what it knew, which is cheaper than `/resume`.
The recommendation was wrong, and it is recorded because it is an obvious-looking
improvement that a future session will propose again. **What makes the habit safe is A5
(removing the wake path) and D7 (removing the ambiguity), not closing the window.**

**`CLM-2`. Stopping the dev server at closeout and leaving it down** — rejected; it costs a
restart every closeout. Superseded by A5's detached relaunch.

**`CLM-3`. An `— end of prompt —` marker for the consultant** — rejected. The closing fence
already ends the block, and such a marker is exactly the token that ends up *inside* the
fence, where it would be pasted into the receiving session as an instruction.

**`CLM-4`. Adding `-discussion` to `session-start` §E's naming convention** — declined.
`-builder` is a positive marker precisely because everything else is unmarked; a second one
starts a taxonomy that wants completing. It stays in commit messages. **Revisit if
discussion sessions start being resumed and the `/resume` picker becomes ambiguous.**

## 3. Corrections to the prior record

**`CLM-5`. A claim this session committed and then corrected.** `FMS-N1` originally stated
that the eval harness divergence left *"aggregate baselines essentially unmoved — the eval
samples pairs from a 75k-node graph, where adjacency is rare."* **Both halves were wrong.**
The pair set is the frozen `panel.json`, not a random sample; and the three callers do not
treat the two-card case alike — `run_baseline.py:98` discards it, `tune_weights.py:65` keeps
it with an empty interior, `export_paths.py:244` exports it as a one-hop cell. Corrected in
place, with the size of the effect marked **unmeasured**. The original was an inference
presented as fact, which is the failure `ml-graph-analyst`'s own "say unmeasured rather than
likely" rule exists to stop.

**`CLM-6`. `CLAUDE.md` may be wrong about what loads unconditionally.** It asserts that
"`CLAUDE.md` + `memory/` + both `SKILL.md` bodies load unconditionally." On this session's
evidence the **bodies do not** — the skill and agent listings carried descriptions only, and
all four files had to be opened with `Read` to be seen. If that holds, **closeout D6
over-counts**, because its diff sweeps `CLAUDE.md`, `.claude/skills/` and `.claude/agents/`
as equivalents, hiding the two layers that genuinely are unconditional inside a larger
number. **Not acted on** — it is a `CLAUDE.md` change and therefore the owner's, and the
evidence is one session on one client, where the rendering was not even uniform (`closeout`
listed with its full description, `session-start` as the bare label). **Cheap check:** ask a
fresh session, before it reads anything, to state `closeout`'s A5 without opening the file.

## 4. Standing context layer (closeout D6)

**Repo half**, `git diff --numstat main..HEAD`:

| File | Net |
|---|---|
| `.claude/skills/closeout/SKILL.md` | +63 |
| `.claude/agents/consultant.md` | +52 |
| `.claude/agents/ml-graph-analyst.md` | +12 |
| `.claude/skills/session-start/SKILL.md` | +3 |
| `CLAUDE.md` | +3 |
| **Total** | **+133** |

Every addition was owner-directed. The two `docs/` commits contribute nothing.

**`memory/` half: 469 lines — and `CLM-7`, a gap this measurement found.** The last recorded
figure is **435**, in `2026-07-25-f1-minimum-stop-execution-log.md` §7. The
`low-degree-census` branch's own log still reads 435. **So 34 lines were added to the layer
that loads unconditionally, by work between the F1 closeout and 2026-07-26, and the delta
was recorded nowhere.** This is precisely what D6 names `memory/` for: it lives outside the
repo, so no diff can see it, and only a line count compared against the last recorded figure
will catch it. Not attributed here — attribution needs the session that did it, not a
guess. **Success condition:** closed when a session reconciles the 435 → 469 growth against
what was added, or accepts it explicitly with the reasoning recorded.

## 5. What the session knew that is not otherwise written down

**`CLM-8`. The owner's evidence that a detached server survives its terminal closing.**
**A5 step 3 depends entirely on this**, and it existed only in conversation. His reasoning,
recorded because re-deriving it is not cheap: he knows which Claude sessions he has open,
none of them started the dev servers that are currently listening, and he has never started
one manually. A session's own test (a detached ticker surviving across turns, `TaskList`
empty) is weaker — it never tested the terminal closing at all.

**`CLM-9`. Why an open terminal beats `/resume` for knowledge questions.** Resuming a
retired session is more token-expensive than asking one whose window is still open. This is
the reason the habit exists; D7 records *that* terminals stay open, not *why* the
alternative is worse.

**`CLM-10`. The two-batch commit-on-behalf was verified for scope, not for content.** For
both discussion-session batches, what was checked was diff scope, append position, and one
quoted claim each — the probe's §6 phrasing, and `WHAT-GOOD-LOOKS-LIKE.md:137–139`. The
75-line and 48-line entries were **not read in full**. "Clean" meant *no third-party content
and no interleaving*; it did not mean the reasoning was reviewed.

## 6. Operational measurements with no other home

- **The stale worktree, resolved.** `.git/worktrees/wt-bypass` printed
  `Permission denied` on every git command for the whole session. Cause:
  `logs/` and `refs/` carried `ReadOnly` **and** were OneDrive Files On-Demand
  `ReparsePoint` placeholders, so git's own delete failed while
  `git worktree prune` was already trying to remove it ("gitdir file does not exist").
  Cleared the attributes, removed the directory, prune now exits silently. **Generalises:
  any `.git` internal git cannot delete under OneDrive is worth checking for `ReadOnly` +
  `ReparsePoint` before assuming a lock.**
- **A pre-F1 dev API was serving on `:8000` throughout.** Started 2026-07-25 13:52; PR #23
  merged 21:20. Probed live: HTTP 200, and its path response exposes `['artists']` with no
  `stop_rule`. **The queued F1 use-the-app check run against it would show no forced stop on
  any journey and look like a failure of the feature.** Left running at the owner's
  instruction. **Success condition:** closed when the queued F1 check runs against a server
  started after `5ffd60d`.
- Roughly twenty orphaned `python` / `node` / `uvicorn` processes date from 2026-07-19
  onward. A5 is the forward fix; it does not sweep the existing backlog.
- `builder/analysis/2026-07-26-low-degree-census/resolve.log` exists in no branch — every
  other file in that directory is committed on `low-degree-census`. Left untouched.
