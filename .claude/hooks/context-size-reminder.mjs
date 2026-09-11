#!/usr/bin/env node
// Context-size reminder — UserPromptSubmit hook (owner ruling DLS-Q6a, 2026-09-11;
// docs/superpowers/findings/2026-09-10-documentation-layer-strategy.md §5a).
//
// CLAUDE.md: "Nothing triggers on session state", so the degradation tell has depended on
// someone noticing. This notices one proxy for it: once the session's context passes a
// threshold, it adds a single line of context, ONCE per session. It never blocks.
//
// Context size is the last assistant turn's input + cache-read + cache-creation tokens, read
// from the tail of the transcript. Threshold: DLS_CONTEXT_REMIND_TOKENS, default 400000. The
// 28 retained sessions of 2026-09-10 averaged 261k tokens per turn and peaked at 665k with no
// compaction; 400k is a starting point, not a measured degradation onset.
//
// The once-per-session marker lives in .claude/logs/ (gitignored). Any failure is swallowed.

import { readFileSync, openSync, readSync, fstatSync, closeSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const TAIL_BYTES = 4 * 1024 * 1024;
const markerDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'logs', 'context-reminded');

function lastContextTokens(transcriptPath) {
  const fd = openSync(transcriptPath, 'r');
  try {
    const size = fstatSync(fd).size;
    const start = Math.max(0, size - TAIL_BYTES);
    const buf = Buffer.alloc(size - start);
    readSync(fd, buf, 0, buf.length, start);
    const lines = buf.toString('utf8').split('\n');
    for (let i = lines.length - 1; i >= 0; i--) {
      if (!lines[i].includes('"usage"')) continue;
      try {
        const o = JSON.parse(lines[i]);
        const u = o?.message?.usage;
        if (o.type === 'assistant' && u) {
          return (u.input_tokens || 0) + (u.cache_read_input_tokens || 0) + (u.cache_creation_input_tokens || 0);
        }
      } catch {
        // a partial first line from the tail cut; keep scanning
      }
    }
    return 0;
  } finally {
    closeSync(fd);
  }
}

try {
  const p = JSON.parse(readFileSync(0, 'utf8') || '{}');
  const threshold = Number(process.env.DLS_CONTEXT_REMIND_TOKENS) || 400000;
  const sid = String(p.session_id || '').replace(/[^A-Za-z0-9-]/g, '');
  if (sid && p.transcript_path && existsSync(p.transcript_path)) {
    const marker = join(markerDir, sid);
    if (!existsSync(marker)) {
      const tokens = lastContextTokens(p.transcript_path);
      if (tokens >= threshold) {
        mkdirSync(markerDir, { recursive: true });
        writeFileSync(marker, String(tokens));
        const fmt = (n) => (n >= 1000 ? `${Math.round(n / 1000)}k` : `${n}`);
        process.stdout.write(
          `Context note (project hook, once per session): this session's context is about ` +
          `${fmt(tokens)} tokens, past the ${fmt(threshold)}-token reminder ` +
          `threshold. Long contexts degrade here (CLAUDE.md, "The degradation tell"). Finish the ` +
          `current step, then prefer handing off at the next natural stopping point over starting ` +
          `new work; say so to the owner, whose call it is.\n`,
        );
      }
    }
  }
} catch {
  // never break a prompt over a reminder
}
