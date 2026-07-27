#!/usr/bin/env bash
#
# docs-lint — mechanical documentation checks for artistpath.
#
# WHY THIS EXISTS. The 2026-07-27 full-project doc audit needed ten parallel subagents
# because the corpus is ~11x the auditor's single-pass budget. Sorting its findings
# afterwards showed roughly three quarters were mechanically checkable, and that every
# convention violated was ALREADY WRITTEN DOWN — the role-marker rule in two places, the
# map's completeness claim on its own line 3. The failure was never missing prose. It was
# that nothing checked the prose.
#
# So this runs the checkable part in seconds, deterministically, at zero context cost, and
# leaves `doc-auditor` its budget for the half a script cannot see.
#
# WHAT IT DELIBERATELY DOES NOT DO. It does not adjudicate. Checks 4-6 emit CANDIDATES for
# a human or the auditor to judge, and never fail the run. A green lint is NOT a clean
# audit: this script could not have caught the 2026-07-27 audit's most valuable finding
# (a provenance banner attached to the one section it did not cover), and treating green
# as clean is the false-clean failure that audit recorded as DAF-4.
#
# Usage:
#   scripts/docs-lint.sh                 # lint this repo
#   scripts/docs-lint.sh --root DIR      # lint an alternate tree (used by the self-test)
#   scripts/docs-lint.sh --quiet         # failures only
#
# Exit: 0 all hard checks passed (candidates may still be printed); 1 a hard check failed;
#       2 bad invocation.
#
# Positive control: scripts/docs-lint-selftest.sh — proves each hard check can go RED.
# Per the standing rule that a green result from a new instrument is not evidence until it
# has been shown to go red.

set -uo pipefail

ROOT="."
QUIET=0

while [ $# -gt 0 ]; do
  case "$1" in
    --root)  ROOT="${2:?--root needs a directory}"; shift 2 ;;
    --quiet) QUIET=1; shift ;;
    -h|--help) sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "docs-lint: unknown argument: $1" >&2; exit 2 ;;
  esac
done

DOCS="$ROOT/docs"
MAP="$DOCS/README.md"

[ -d "$DOCS" ] || { echo "docs-lint: no docs/ under '$ROOT'" >&2; exit 2; }

FAILURES=0
note()  { [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"; }
fail()  { printf 'FAIL  %s\n' "$*"; FAILURES=$((FAILURES + 1)); }
cand()  { [ "$QUIET" -eq 1 ] || printf 'CAND  %s\n' "$*"; }

# Every markdown file that is project record. docs/reference/ is third-party and is
# excluded by standing instruction, not by oversight.
docs_files() {
  find "$DOCS" -name '*.md' -not -path "*/reference/*" | sort
}

# ----------------------------------------------------------------------------------
note "== 1. Every document declares a role or status in its first 12 lines =="
# Convention: docs/README.md "State its role in the first ten lines"; doc-auditor check F.
# Found 11 violations on 2026-07-27, including one doc-audit report — the very defect
# class that report existed to check for in others.
C1=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if ! head -12 "$f" | grep -qiE '\*\*Role:|\*\*Status:|EXECUTED|SUPERSEDED'; then
    fail "no role/status marker in first 12 lines: ${f#"$ROOT"/}"
    C1=$((C1 + 1))
  fi
done <<EOF
$(docs_files)
EOF
[ "$C1" -eq 0 ] && note "      ok"

# ----------------------------------------------------------------------------------
note "== 2. docs/README.md classifies every document, as it claims to =="
# The map's own line 3 says it is "the current classification of every document in docs/".
# Three were missing on 2026-07-27, one of them absent entirely — while that document's
# own closeout recorded the doc-auditor step as "CLEAN ... docs/README.md entry complete".
C2=0
if [ -f "$MAP" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [ "$f" = "$MAP" ] && continue
    b=$(basename "$f")
    if ! grep -qF "$b" "$MAP"; then
      fail "not classified in docs/README.md: ${f#"$ROOT"/}"
      C2=$((C2 + 1))
    fi
  done <<EOF
$(docs_files)
EOF
  [ "$C2" -eq 0 ] && note "      ok"
else
  fail "docs/README.md is missing entirely"
fi

# ----------------------------------------------------------------------------------
note "== 3. Every relative markdown link resolves =="
# Three did not on 2026-07-27 — bare 'findings/x.md' cited from plans/, which resolves to
# plans/findings/x.md and does not exist. Invisible to a reader, fatal to an agent Read.
C3=0
# Collected first, then reported — a `... | while read` would run the loop in a subshell
# and silently lose every increment to FAILURES, which is its own vacuous-check pattern.
DEAD=$(
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    d=$(dirname "$f")
    # A document may opt out when it QUOTES other documents' link syntax rather than
    # navigating. Used once, by the 2026-07-22 context-layer audit, which reproduces
    # MEMORY.md's and CLAUDE.md's own links verbatim as evidence — including links to
    # memory files that live outside the repo and can never resolve from here.
    grep -q '<!-- docs-lint: skip-links' "$f" 2>/dev/null && continue
    # Fenced code blocks are skipped: a link inside one is a sample, not navigation.
    awk '/^[[:space:]]*```/{fence=!fence; next} !fence{print}' "$f" 2>/dev/null \
      | grep -o ']([^)]*\.md[^)]*)' \
      | sed -e 's/^](//' -e 's/)$//' -e 's/#.*$//' \
      | grep -v '^http' | sort -u \
      | while IFS= read -r target; do
          [ -n "$target" ] || continue
          [ -f "$d/$target" ] || printf '%s -> %s\n' "${f#"$ROOT"/}" "$target"
        done
  done <<EOF
$(docs_files)
EOF
)
if [ -n "$DEAD" ]; then
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    fail "dead link: $line"
    C3=$((C3 + 1))
  done <<EOF
$DEAD
EOF
fi
[ "$C3" -eq 0 ] && note "      ok"

# ----------------------------------------------------------------------------------
note "== 4. CANDIDATE: plans claiming to be live =="
# Warn-only and heuristic by design. On 2026-07-27 five merged plans read as pending, the
# worst a 13-task non-idempotent AWS plan marked "Role: ACTIVE, not yet executed" while the
# stack was deployed. Exactly one plan should be live at a time (the roadmap).
if [ -d "$DOCS/superpowers/plans" ]; then
  LIVE=""
  n=0
  for f in "$DOCS"/superpowers/plans/*.md; do
    [ -f "$f" ] || continue
    # The negation is stripped FIRST and deliberately. A plain `grep -i EXECUTED` matches
    # "not yet executed", so the check would clear exactly the plan it exists to catch —
    # `track-b-infrastructure.md` read "Role: ACTIVE, not yet executed" while deployed.
    # Caught by the positive control, not by review.
    if ! head -12 "$f" | grep -viE 'not[- ](yet[- ])?executed' \
         | grep -qiE 'EXECUTED|HISTORICAL|Role: COMPLETE'; then
      LIVE="$LIVE  ${f#"$ROOT"/}
"
      n=$((n + 1))
    fi
  done
  if [ "$n" -gt 1 ]; then
    cand "$n plans do not declare themselves executed; at most one should be live:"
    [ "$QUIET" -eq 1 ] || printf '%s' "$LIVE"
  else
    note "      ok ($n live)"
  fi
fi

# ----------------------------------------------------------------------------------
note "== 5. CANDIDATE: bare identifiers minted in more than one document =="
# The 2026-07-27 audit registered 11 previously unrecorded collisions. EVERY one was a bare
# letter-and-digit token; every hyphenated namespaced series (DEP-, TKA-, MKS-, ...) was
# clean. So the signal worth surfacing is a bare token given a DEFINITION (bolded) in two
# or more documents. Judgement stays with the reader: many are legitimate citations.
DEFS=$(
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    grep -oE '\*\*[A-Z]{1,2}[0-9]{1,2}[a-z]?\*\*' "$f" 2>/dev/null \
      | tr -d '*' | sort -u | while IFS= read -r tok; do
          [ -n "$tok" ] && printf '%s\t%s\n' "$tok" "$(basename "$f")"
        done
  done <<EOF
$(docs_files)
EOF
)
if [ -n "$DEFS" ]; then
  COLL=$(printf '%s\n' "$DEFS" | cut -f1 | sort | uniq -c | awk '$1 >= 2 {print $2}')
  if [ -n "$COLL" ]; then
    cand "bare tokens bolded in 2+ documents (review, do not auto-fix; never rename a committed one):"
    printf '%s\n' "$COLL" | while IFS= read -r tok; do
      [ -n "$tok" ] || continue
      files=$(printf '%s\n' "$DEFS" | awk -F'\t' -v t="$tok" '$1 == t {print $2}' | sort -u | tr '\n' ' ')
      [ "$QUIET" -eq 1 ] || printf '        %-6s %s\n' "$tok" "$files"
    done
  else
    note "      ok"
  fi
fi

# ----------------------------------------------------------------------------------
note "== 6. CANDIDATE: figures restated outside the document that owns them =="
# All scoring / path-quality figures live in exactly one file and are cited by section.
# Restating a CORRECT number is still a violation, because that is how drift starts — and
# it had already started: a plan said 0.7% where the adjudication says 0.73%.
ADJ="$DOCS/superpowers/findings/2026-07-21-scoring-adjudication.md"
if [ -f "$ADJ" ]; then
  # One alternation over one pass. The obvious nested loop is ~5,000 greps and takes
  # minutes on this tree (OneDrive); a lint nobody waits for is a lint nobody runs.
  NUMS=$(grep -oE '[0-9]+\.[0-9]{2,}' "$ADJ" | sort -u | head -60)
  if [ -n "$NUMS" ]; then
    PAT=$(printf '%s' "$NUMS" | tr '\n' '|' | sed 's/|$//' | sed 's/\./\\./g')
    TARGETS=$(docs_files | grep -v '/findings/')
    HITS=$(
      [ -n "$TARGETS" ] && printf '%s\n' "$TARGETS" | tr '\n' '\0' \
        | xargs -0 grep -oHE "$PAT" 2>/dev/null | sort -u
    )
    if [ -n "$HITS" ]; then
      printf '%s\n' "$HITS" | while IFS= read -r h; do
        [ -n "$h" ] || continue
        cand "figure ${h##*:} from the adjudication also appears in ${h%%:*}"
      done
    else
      note "      ok"
    fi
  fi
fi

# ----------------------------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  echo "docs-lint: $FAILURES hard failure(s)."
  echo "Candidates above are for review and did not affect this exit code."
  exit 1
fi
echo "docs-lint: hard checks passed."
echo "This is NOT a clean bill of documentation health — see the header. Candidates above still need a reader."
exit 0
