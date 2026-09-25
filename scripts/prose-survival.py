#!/usr/bin/env python3
"""prose-survival: does every sentence of the old text still exist somewhere in the new?

WHY THIS EXISTS. Owner ruling DLS-Q4 (2026-09-11, docs/superpowers/findings/
2026-09-10-documentation-layer-strategy.md §5a): text leaving an always-loaded file MOVES VERBATIM,
"with a check that every sentence still exists somewhere". This is that check.

WHAT IT CANNOT DO. It proves text EXISTS, never that a session SEES it. A sentence moved into a skill
body or an HTML comment survives here and is still conditional or invisible; delivery is §7's
question. --strip-comments refuses credit for a sentence that survives only inside <!-- -->, which
is how the always-loaded "stays" set is checked.

Usage:
  python scripts/prose-survival.py --before REV:PATH|PATH [--before ...] --after PATH [--after ...]
                                   [--allow FILE] [--strip-comments] [--min-chars N]
  REV:PATH reads a committed version (git show); a plain PATH reads the working tree.
  --allow lists sentences whose removal the owner signed off, one per line; '#' lines are comments.
Exit: 0 every sentence survives or is allowed; 1 at least one is missing; 2 bad invocation.
Positive control: scripts/prose-survival-selftest.sh.
"""
import argparse
import re
import subprocess
import sys


def read(spec):
    # REV:PATH, but never mistake a Windows drive ("C:\...", "C:/...") for a revision.
    if ':' in spec and not re.match(r'^[A-Za-z]:[\\/]', spec):
        rev, path = spec.split(':', 1)
        r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
        if r.returncode != 0:
            print(f'prose-survival: cannot read {spec}: '
                  f'{r.stderr.decode(errors="replace").strip()}', file=sys.stderr)
            sys.exit(2)
        return r.stdout.decode('utf-8')
    with open(spec, encoding='utf-8') as fh:
        return fh.read()


def norm(text):
    # Markup is not content: headings, list markers, quote bars, table pipes, emphasis, code ticks
    # and comment delimiters are dropped, and all whitespace collapses, so rewrapping is invisible.
    text = text.replace('\r', '')
    text = re.sub(r'^[ \t]*(?:#+|[-*+]|\d+\.|>+|\|)[ \t]*', '', text, flags=re.M)
    text = re.sub(r'<!--|-->', ' ', text)
    text = re.sub(r'[*_`|]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def sentences(text, min_chars):
    out = []
    for block in re.split(r'\n[ \t]*\n', text.replace('\r', '')):
        for s in re.split(r'(?<=[.!?:])\s+(?=[A-Z0-9("\'\[⚠])', norm(block)):
            if len(s) >= min_chars:
                out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description='Does every old sentence still exist somewhere?')
    ap.add_argument('--before', action='append', required=True)
    ap.add_argument('--after', action='append', required=True)
    ap.add_argument('--allow')
    ap.add_argument('--strip-comments', action='store_true')
    ap.add_argument('--min-chars', type=int, default=25)
    a = ap.parse_args()

    after = '\n\n'.join(read(p) for p in a.after).replace('\r', '')
    if a.strip_comments:
        after = re.sub(r'<!--.*?-->', ' ', after, flags=re.S)
    hay = norm(after)
    allowed = set()
    if a.allow:
        allowed = {norm(line) for line in read(a.allow).splitlines()
                   if line.strip() and not line.lstrip().startswith('#')}

    total, missing = 0, []
    for spec in a.before:
        for s in sentences(read(spec), a.min_chars):
            total += 1
            if s not in hay and s not in allowed:
                missing.append(s)
    for s in missing:
        print(f'MISSING  {s}')
    print(f'prose-survival: {total - len(missing)} of {total} sentences survive; '
          f'{len(missing)} missing.')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
