#!/usr/bin/env node
// Orca archive hook (orca.yaml scripts.archive): before Orca deletes a session worktree, rename every
// Claude Code session run in it to `[retired-pr-<n>] <branch>`, so retired sessions are recognisable
// in `claude --resume` and Orca's session history after the worktree is gone. The branch, not the
// session's own title: an auto title describes the latest request ("Merge PR"), not the work.
// <branch> drops Orca's `<owner>/` prefix; with no branch (detached HEAD) the current title is kept.
//
// It does what `/rename` does: appends a `custom-title` record to the session transcript under
// <claude config dir>/projects/<slug of the worktree path>/. That record format is Claude Code's
// internal one, not a documented API — if an update changes it, renames stop taking effect.
//
// It must NEVER exit non-zero: a failed archive hook blocks Orca from deleting the worktree.
// Every failure is logged (Orca shows hook output) and swallowed.
//
//   node scripts/orca-retire-session-titles.mjs [--dry-run]
//   env: ORCA_WORKTREE_PATH (set by Orca; defaults to cwd), CLAUDE_CONFIG_DIR (defaults to ~/.claude)

import { execFileSync } from 'node:child_process'
import { appendFileSync, existsSync, readdirSync, readFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'

const PREFIX_MARK = '[retired-'
const dryRun = process.argv.includes('--dry-run')
const log = (msg) => console.log(`[retire-session-titles] ${msg}`)

// Orca exports MSYS-form paths (/c/...) when its runner is Git Bash; Claude Code slugs the
// Windows form.
function toNativePath(p) {
  const msys = /^\/([a-zA-Z])(\/.*)?$/.exec(p)
  if (process.platform === 'win32' && msys) {
    return `${msys[1].toUpperCase()}:${(msys[2] ?? '/').replaceAll('/', '\\')}`
  }
  return resolve(p)
}

function run(cmd, args, cwd) {
  return execFileSync(cmd, args, {
    cwd,
    encoding: 'utf8',
    timeout: 30_000,
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  }).trim()
}

function branchAndPr(worktree) {
  let branch = ''
  try {
    branch = run('git', ['branch', '--show-current'], worktree)
    if (!branch) return { branch, pr: 'none' }
    const out = run(
      'gh',
      ['pr', 'list', '--head', branch, '--state', 'all', '--limit', '1', '--json', 'number', '--jq', '.[0].number // ""'],
      worktree,
    )
    return { branch, pr: out || 'none' }
  } catch (err) {
    log(`could not look up the branch or PR (${err.message.split('\n')[0]}); using PR "none"`)
    return { branch, pr: 'none' }
  }
}

// The title the session shows now: the last /rename if any, else the last auto-generated title.
function currentTitle(lines) {
  let custom, ai, sessionId
  for (const line of lines) {
    if (!line.includes('-title"')) continue
    let rec
    try {
      rec = JSON.parse(line)
    } catch {
      continue
    }
    if (rec.type === 'custom-title' && rec.customTitle) {
      custom = rec.customTitle
      sessionId = rec.sessionId ?? sessionId
    } else if (rec.type === 'ai-title' && rec.aiTitle) {
      ai = rec.aiTitle
      sessionId = rec.sessionId ?? sessionId
    }
  }
  return { title: custom ?? ai, sessionId }
}

function main() {
  const worktree = toNativePath(process.env.ORCA_WORKTREE_PATH || process.cwd())
  const configDir = process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude')
  const projectDir = join(configDir, 'projects', worktree.replace(/[^a-zA-Z0-9]/g, '-'))
  if (!existsSync(projectDir)) {
    log(`no Claude Code sessions for ${worktree} (looked in ${projectDir})`)
    return
  }

  const { branch, pr } = branchAndPr(worktree)
  const name = branch.split('/').pop()
  const files = readdirSync(projectDir).filter((f) => f.endsWith('.jsonl'))
  for (const file of files) {
    const path = join(projectDir, file)
    const content = readFileSync(path, 'utf8')
    const { title, sessionId = file.replace(/\.jsonl$/, '') } = currentTitle(content.split('\n'))
    if (!name && !title) {
      log(`${file}: no branch and no title, skipped`)
      continue
    }
    if (title?.startsWith(PREFIX_MARK)) {
      log(`${file}: already retired ("${title}"), skipped`)
      continue
    }
    const renamed = `[retired-pr-${pr}] ${name || title}`
    const record = JSON.stringify({ type: 'custom-title', customTitle: renamed, sessionId })
    const sep = content === '' || content.endsWith('\n') ? '' : '\n'
    if (!dryRun) appendFileSync(path, `${sep}${record}\n`)
    log(`${file}: "${title ?? '(untitled)'}" -> "${renamed}"${dryRun ? ' (dry run)' : ''}`)
  }
}

try {
  main()
} catch (err) {
  log(`failed, worktree removal continues: ${err.stack ?? err}`)
}
process.exit(0)
