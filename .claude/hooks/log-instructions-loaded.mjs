#!/usr/bin/env node
// InstructionsLoaded logger — the instrument for `DLS-T1`
// (docs/superpowers/findings/2026-09-10-documentation-layer-strategy.md §6).
//
// Appends one JSON line per instruction file Claude Code loads (CLAUDE.md files and
// .claude/rules/*.md, at session start and lazily) to .claude/logs/instructions-loaded.jsonl
// in the tree this script lives in. The directory is gitignored. The event cannot block or
// add context, and this script never writes to stdout; any failure is swallowed so a log
// line can never break a session.

import { readFileSync, appendFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const logDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'logs');

try {
  const p = JSON.parse(readFileSync(0, 'utf8') || '{}');
  const record = {
    ts: new Date().toISOString(),
    session_id: p.session_id ?? null,
    cwd: p.cwd ?? null,
    agent_type: p.agent_type ?? null,
    agent_id: p.agent_id ?? null,
    file_path: p.file_path ?? null,
    load_reason: p.load_reason ?? null,
    globs: p.globs ?? null,
    trigger_file_path: p.trigger_file_path ?? null,
    parent_file_path: p.parent_file_path ?? null,
  };
  mkdirSync(logDir, { recursive: true });
  appendFileSync(join(logDir, 'instructions-loaded.jsonl'), JSON.stringify(record) + '\n');
} catch {
  // never break a session over a log line
}
