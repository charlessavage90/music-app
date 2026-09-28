#!/usr/bin/env python3
"""gen-docs-map: generate docs/README.md's classification from each document's own bold role line.

WHY THIS EXISTS. Owner ruling DLS-Q2 (2026-09-11, docs/superpowers/findings/
2026-09-10-documentation-layer-strategy.md §5a): the map is generated from each document's own role
line; hand-written text survives only as warnings. A hand-written row restated its document and
drifted from it. A generated row cannot, because the document holds the only copy. The row grain
is the owner's DLP-Q2 answer (2026-09-24, plan 2026-09-24-dls-items-4-6): the path plus the bold
"**Role: ...**" span only. A reader who needs more reads the document's opening. A superseded
document's bold line must name its replacement: that is the one fact the map must never get wrong.

MERGE CONFLICTS in the generated block are resolved by re-running this script, never by hand.

A role line may open "**⚠ Role:", the house pattern for a role line carrying a warning; the plan's
text matched only "**Role:" and 8 documents failed on it (DLP-S2.1, 2026-09-28; self-test control 7c).

Usage: python scripts/gen-docs-map.py [--root DIR] [--check]
Exit: 0 written, or current under --check; 1 stale under --check, or a document has no classifiable
**Role:** line in its first 40 lines, or is superseded and names no replacement; 2 bad invocation or
missing markers.
"""
import argparse
import pathlib
import posixpath
import re
import sys

BEGIN = '<!-- map:generated:begin -->'
END = '<!-- map:generated:end -->'
ROLE = re.compile(r'\*\*(?:⚠\s*)?Role:')
# A role paragraph is classified by whichever keyword appears EARLIEST in its first 200 characters
# from "**Role:", so "ACTIVE — AUTHORITATIVE for its own measurements" is Active and
# "SUPERSEDED — was ACTIVE" is Superseded. Case-sensitive on purpose: "not yet executed" must not
# read as EXECUTED. Output sections follow this list's order.
SECTIONS = [
    ('Authoritative', ('AUTHORITATIVE', 'GOVERNING')),
    ('Active', ('ACTIVE', 'RETAINED', 'REASONING RECORD', 'RESULTS OF RECORD', 'OPERATIONAL',
                'PRE-REGISTRATION')),
    ('Complete', ('COMPLETE', 'EXECUTED', 'FULLY DISCHARGED')),
    ('Superseded or historical — check before citing', ('SUPERSEDED', 'HISTORICAL')),
    ('Narrative — never use as context', ('NARRATIVE',)),
]


def role_paragraph(text):
    lines = text.replace('\r', '').split('\n')[:40]
    for i, line in enumerate(lines):
        if not ROLE.search(line):
            continue
        para = []
        for l in lines[i:]:
            if not l.strip() or l.lstrip().startswith(('#', '<!--')):
                break
            para.append(re.sub(r'^\s*>\s?', '', l).strip())
        return ' '.join(para)
    return None


def bold_span(para):
    m = re.search(ROLE.pattern + r'.*?\*\*', para)
    return m.group(0) if m else None


def names_replacement(span):
    return bool(re.search(r'\]\(|`[^`]+\.md`', span))


def classify(para):
    head = para[ROLE.search(para).start():][:200]
    best = None
    for n, (_, words) in enumerate(SECTIONS):
        for w in words:
            m = re.search(r'\b' + re.escape(w) + r'\b', head)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), n)
    return None if best is None else best[1]


def rebase_links(para, rel):
    # Links in a role paragraph resolve against the document's folder; in the map, against docs/.
    base = posixpath.dirname(rel)

    def fix(m):
        target = m.group(1)
        if re.match(r'^(?:[a-z][a-z0-9+.-]*:|#|/)', target):
            return m.group(0)
        path, sep, frag = target.partition('#')
        return '](' + posixpath.normpath(posixpath.join(base, path)) + sep + frag + ')'

    return re.sub(r'\]\(([^)\s]+)\)', fix, para)


def main():
    ap = argparse.ArgumentParser(description='Generate the docs map from role paragraphs.')
    ap.add_argument('--root', default='.')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    docs = pathlib.Path(a.root) / 'docs'
    mp = docs / 'README.md'

    rows = {n: [] for n in range(len(SECTIONS))}
    unclassified, unnamed = [], []
    for f in sorted(docs.rglob('*.md')):
        rel = f.relative_to(docs).as_posix()
        if rel == 'README.md' or rel.startswith('reference/'):
            continue
        para = role_paragraph(f.read_text(encoding='utf-8'))
        span = bold_span(para) if para else None
        n = classify(span) if span else None
        if n is None:
            unclassified.append(rel)
            continue
        if re.search(r'\bSUPERSEDED\b', span[:200]) and not names_replacement(span):
            unnamed.append(rel)
            continue
        cell = rebase_links(span, rel).replace('|', '\\|')
        if '⚠' in para:
            cell += ' ⚠ *its opening carries a warning*'
        rows[n].append(f'| [`{rel}`]({rel}) | {cell} |')
    for rel in unclassified:
        print(f'FAIL  no classifiable **Role:** line in its first 40 lines: docs/{rel}')
    for rel in unnamed:
        print(f'FAIL  superseded, but its bold role line names no replacement: docs/{rel}')
    if unclassified or unnamed:
        return 1

    out = [BEGIN, '']
    for n, (name, _) in enumerate(SECTIONS):
        if rows[n]:
            out += [f'### {name}', '', '| Document | Its role line |', '|---|---|',
                    *rows[n], '']
    out.append(END)

    text = mp.read_text(encoding='utf-8').replace('\r', '')
    if BEGIN not in text or END not in text:
        print(f'gen-docs-map: {mp} lacks the {BEGIN} / {END} markers', file=sys.stderr)
        return 2
    new = text[:text.index(BEGIN)] + '\n'.join(out) + text[text.index(END) + len(END):]
    if a.check:
        if new != text:
            print('FAIL  docs/README.md generated block is stale — run: python scripts/gen-docs-map.py')
            return 1
        return 0
    mp.write_text(new, encoding='utf-8', newline='\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
