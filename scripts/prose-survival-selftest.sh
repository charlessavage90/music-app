#!/usr/bin/env bash
#
# Positive control for prose-survival. A survival check that cannot go red is the vacuous-check
# pattern this project has recorded four times (FMS-P1, TR-2, TKD-2, TKB-4). So: a rewrapped move
# must go GREEN, and a reworded sentence, a comment-only survival under --strip-comments, and an
# ignored allow-list must each behave.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY="${PYTHON:-python}"
PS="$HERE/prose-survival.py"
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t prosesurv)
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAILED=0
ok()  { printf '  PASS  %s\n' "$1"; PASS=$((PASS + 1)); }
bad() { printf '  FAIL  %s\n' "$1"; FAILED=$((FAILED + 1)); }

cat > "$TMP/before.md" <<'MD'
## A rule

**Never compress live prose to free lines.** It has twice cost the clause that made a check usable.
- A list item that is long enough to count as a sentence here.
MD
cat > "$TMP/moved.md" <<'MD'
# Somewhere else

**Never compress live prose
to free lines.** It has twice cost the clause that made a
check usable.

* A list item that is long enough to count as a sentence here.
MD

echo "== control 0: a rewrapped move under a new heading must PASS =="
if "$PY" "$PS" --before "$TMP/before.md" --after "$TMP/moved.md" >/dev/null; then ok "rewrapped move survives"
else bad "rewrapped move reported missing"; fi

echo "== control 1: a reworded sentence must FAIL and be named =="
sed 's/twice cost/cost, twice,/' "$TMP/moved.md" > "$TMP/reworded.md"
OUT=$("$PY" "$PS" --before "$TMP/before.md" --after "$TMP/reworded.md"); RC=$?
if [ "$RC" -eq 1 ] && printf '%s' "$OUT" | grep -q 'MISSING  It has twice cost'; then ok "rewording goes red"
else bad "rewording NOT caught (rc=$RC)"; fi

echo "== control 2: survival only inside an HTML comment =="
{ echo '<!--'; cat "$TMP/moved.md"; echo '-->'; } > "$TMP/commented.md"
if "$PY" "$PS" --before "$TMP/before.md" --after "$TMP/commented.md" >/dev/null; then ok "comment text counts as existing"
else bad "comment text not counted"; fi
"$PY" "$PS" --before "$TMP/before.md" --after "$TMP/commented.md" --strip-comments >/dev/null; RC=$?
if [ "$RC" -eq 1 ]; then ok "--strip-comments refuses comment-only survival"
else bad "--strip-comments did not fire (rc=$RC)"; fi

echo "== control 3: an allow-listed removal must PASS =="
printf '%s\n' 'It has twice cost the clause that made a check usable.' > "$TMP/allow.txt"
if "$PY" "$PS" --before "$TMP/before.md" --after "$TMP/reworded.md" --allow "$TMP/allow.txt" >/dev/null; then ok "allow-list honoured"
else bad "allow-list ignored"; fi

echo
echo "self-test: $PASS passed, $FAILED failed."
[ "$FAILED" -eq 0 ] || { echo "prose-survival's green result is NOT evidence until this passes."; exit 1; }
