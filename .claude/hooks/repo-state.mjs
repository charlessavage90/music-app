#!/usr/bin/env node
// Repo-state report — SessionStart hook (owner ruling DLS-Q6b, 2026-09-11;
// docs/superpowers/findings/2026-09-10-documentation-layer-strategy.md §5a).
//
// Prints facts only, which Claude Code adds to the session's context: this tree's branch, its
// uncommitted paths, and the other worktrees of this repository. It exists because another
// live session is detectable only at the start (session-start §C), and that skill runs only
// when the owner invokes it. It does not run or suggest that skill.
//
// git is invoked with fixed arguments and no shell. Silent outside a git repository; any
// failure is swallowed.

import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';

const MAX_PATHS = 8;

function git(cwd, args) {
  return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 5000 });
}

try {
  const p = JSON.parse(readFileSync(0, 'utf8') || '{}');
  const cwd = p.cwd || process.cwd();
  const top = git(cwd, ['rev-parse', '--show-toplevel']).trim();
  const branch = git(top, ['branch', '--show-current']).trim() || '(detached HEAD)';
  const dirty = git(top, ['status', '--porcelain']).split('\n').filter(Boolean);

  const others = [];
  let path = null;
  for (const line of git(top, ['worktree', 'list', '--porcelain']).split('\n')) {
    if (line.startsWith('worktree ')) path = line.slice(9).trim();
    else if (line.startsWith('branch ') && path && resolve(path) !== resolve(top)) {
      others.push(`${path} [${line.slice(7).replace('refs/heads/', '')}]`);
    }
  }

  const out = [`Repo state at session start (project hook, facts only):`];
  out.push(`- This tree: ${top} on ${branch}; ${dirty.length} uncommitted path(s)` +
    (dirty.length ? `: ${dirty.slice(0, MAX_PATHS).map((l) => l.slice(3)).join(', ')}` +
      (dirty.length > MAX_PATHS ? `, +${dirty.length - MAX_PATHS} more` : '') : ''));
  out.push(`- Other worktrees: ${others.length ? others.join('; ') : 'none'}`);
  if (dirty.length) {
    out.push(`- Uncommitted work present at start was not made by this session: leave it, and commit only named paths.`);
  }
  process.stdout.write(out.join('\n') + '\n');
} catch {
  // not a git repository, or git unavailable: say nothing
}
