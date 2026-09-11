# `DLS-` context-layer measurements, 2026-09-10

**Role: COMPLETE — the frozen scripts behind `DLS-M1`–`DLS-M7`.** The figures are owned by
[`docs/superpowers/findings/2026-09-10-documentation-layer-strategy.md`](../../../docs/superpowers/findings/2026-09-10-documentation-layer-strategy.md);
cite that document, not this directory.

The scripts read Claude Code session transcripts under `~/.claude/projects/`, which are
**machine-local and pruned by retention**. Re-running them later measures a different sample;
the figures record what was on disk on 2026-09-10 (28 main sessions, 45 subagent transcripts).

| Script | Measures |
|---|---|
| `transcripts.py <project-dir> [...]` | Read calls and Read refusals by document class; per-session first and peak context |
| `costs.py` | Read result size per file; subagent cost by agent type; per-session token sums |
| `carry.py` | Tokens each source keeps re-sending on later turns (heuristic: chars/4 × turns until compaction) |
| `compact.py` | Compactions per session, and whether `closeout` ran after one |
| `probe.py <stream.jsonl>` | Startup inventory (tools, skills, agents, MCP servers, plugins) and the result of a `claude -p --output-format stream-json --verbose` run — the verification instrument for PR #117 |

`costs.py`, `carry.py` and `compact.py` hardcode this machine's two project directories.
