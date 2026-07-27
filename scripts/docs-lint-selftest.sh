#!/usr/bin/env bash
#
# Positive control for docs-lint.
#
# WHY THIS EXISTS. This project has recorded the same defect four times under three names
# (FMS-P1, TR-2, TKD-2, TKB-4): a verification that passes before the fix, and therefore
# proves nothing. A lint script is exactly the shape that fails this way — it greps, finds
# nothing, prints ok, and everyone believes it.
#
# So every HARD check in docs-lint gets a fixture that makes it go RED, and this script
# asserts it does. A green run of docs-lint is only evidence because of this file.
#
# It also asserts the clean fixture goes GREEN, so a check that fires on everything
# (equally useless) is caught too.
#
# Usage: scripts/docs-lint-selftest.sh
# Exit:  0 all controls behaved; 1 a check failed to fire, or fired when it should not.

set -uo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
LINT="$HERE/docs-lint.sh"
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t docslint)
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAILED=0
ok()   { printf '  PASS  %s\n' "$1"; PASS=$((PASS + 1)); }
bad()  { printf '  FAIL  %s\n' "$1"; FAILED=$((FAILED + 1)); }

# --- a minimal, valid docs/ tree -------------------------------------------------
build_clean() {
  local r="$1"
  rm -rf "$r"; mkdir -p "$r/docs/superpowers/plans" "$r/docs/superpowers/findings"
  cat > "$r/docs/README.md" <<'MD'
# Documentation map

**Role: AUTHORITATIVE.** Classifies every document.

| Document | Covers |
|---|---|
| `superpowers/NEXT.md` | status |
| `superpowers/plans/live-plan.md` | the one live plan |
| `superpowers/findings/2026-07-21-scoring-adjudication.md` | figures |
MD
  cat > "$r/docs/superpowers/NEXT.md" <<'MD'
# Next

**Role: AUTHORITATIVE for status.** Read [`plans/live-plan.md`](plans/live-plan.md).
MD
  cat > "$r/docs/superpowers/plans/live-plan.md" <<'MD'
# Live plan

**Role: AUTHORITATIVE and ACTIVE.** The only live plan.
MD
  cat > "$r/docs/superpowers/findings/2026-07-21-scoring-adjudication.md" <<'MD'
# Adjudication

**Role: AUTHORITATIVE.** Owns every figure. Zero rate is 0.73 % of adjacent pairs.
MD
}

run_lint() { "$LINT" --root "$1" 2>&1; }

# --- control 0: the clean tree must go GREEN -------------------------------------
echo "== control 0: clean fixture must PASS =="
build_clean "$TMP/clean"
OUT=$(run_lint "$TMP/clean"); RC=$?
if [ "$RC" -eq 0 ]; then ok "clean fixture exits 0"
else bad "clean fixture exited $RC — a check is firing on valid input"; printf '%s\n' "$OUT" | sed 's/^/        /'; fi

# --- control 1: missing role marker ----------------------------------------------
echo "== control 1: missing role marker must FAIL =="
build_clean "$TMP/c1"
printf '# Orphan doc\n\nNo marker anywhere near the top of this file.\n' > "$TMP/c1/docs/superpowers/no-marker.md"
printf '| `superpowers/no-marker.md` | listed, but declares no role |\n' >> "$TMP/c1/docs/README.md"
OUT=$(run_lint "$TMP/c1"); RC=$?
if [ "$RC" -ne 0 ] && printf '%s' "$OUT" | grep -q 'no role/status marker'; then ok "check 1 goes red"
else bad "check 1 did NOT fire (rc=$RC)"; fi

# --- control 2: document missing from the map -------------------------------------
echo "== control 2: unclassified document must FAIL =="
build_clean "$TMP/c2"
printf '# Unmapped\n\n**Role: COMPLETE.** Real doc, never added to the map.\n' > "$TMP/c2/docs/superpowers/unmapped.md"
OUT=$(run_lint "$TMP/c2"); RC=$?
if [ "$RC" -ne 0 ] && printf '%s' "$OUT" | grep -q 'not classified in docs/README.md'; then ok "check 2 goes red"
else bad "check 2 did NOT fire (rc=$RC)"; fi

# --- control 3: dead relative link ------------------------------------------------
echo "== control 3: dead link must FAIL =="
build_clean "$TMP/c3"
# The real defect shape: a bare 'findings/x.md' cited from plans/, which resolves to
# plans/findings/x.md. Found three times on 2026-07-27.
printf '\nSee [`findings/2026-07-21-scoring-adjudication.md`](findings/2026-07-21-scoring-adjudication.md).\n' \
  >> "$TMP/c3/docs/superpowers/plans/live-plan.md"
OUT=$(run_lint "$TMP/c3"); RC=$?
if [ "$RC" -ne 0 ] && printf '%s' "$OUT" | grep -q 'dead link'; then ok "check 3 goes red"
else bad "check 3 did NOT fire (rc=$RC)"; fi

# --- control 4: two plans claiming to be live (candidate, must NOT fail the run) ---
echo "== control 4: second live plan must be flagged, without failing the run =="
build_clean "$TMP/c4"
printf '# Second plan\n\n**Role: ACTIVE, not yet executed.** Already merged in reality.\n' \
  > "$TMP/c4/docs/superpowers/plans/second-plan.md"
printf '| `superpowers/plans/second-plan.md` | a second live plan |\n' >> "$TMP/c4/docs/README.md"
OUT=$(run_lint "$TMP/c4"); RC=$?
if printf '%s' "$OUT" | grep -q 'plans do not declare themselves executed'; then
  if [ "$RC" -eq 0 ]; then ok "check 4 flags as candidate and keeps exit 0"
  else bad "check 4 fired but failed the run — candidates must not gate"; fi
else bad "check 4 did NOT fire (rc=$RC)"; fi

# --- control 5: same bare identifier defined twice (candidate) ---------------------
echo "== control 5: duplicate bare identifier must be flagged =="
build_clean "$TMP/c5"
printf '\n- **C4** — the damping criterion.\n' >> "$TMP/c5/docs/superpowers/plans/live-plan.md"
printf '\n- **C4** — the payload guard, an unrelated thing.\n' >> "$TMP/c5/docs/superpowers/NEXT.md"
OUT=$(run_lint "$TMP/c5"); RC=$?
if printf '%s' "$OUT" | grep -q 'bare tokens bolded in 2+ documents' && printf '%s' "$OUT" | grep -q 'C4'; then
  if [ "$RC" -eq 0 ]; then ok "check 5 flags C4 as candidate and keeps exit 0"
  else bad "check 5 fired but failed the run"; fi
else bad "check 5 did NOT fire (rc=$RC)"; fi

# --- control 6: figure restated outside its owner (candidate) ---------------------
echo "== control 6: restated figure must be flagged =="
build_clean "$TMP/c6"
printf '\nMeasured zero-rate on the 75k graph is 0.73 %% (adjudication).\n' \
  >> "$TMP/c6/docs/superpowers/plans/live-plan.md"
OUT=$(run_lint "$TMP/c6"); RC=$?
if printf '%s' "$OUT" | grep -q 'from the adjudication also appears in'; then
  if [ "$RC" -eq 0 ]; then ok "check 6 flags the restatement and keeps exit 0"
  else bad "check 6 fired but failed the run"; fi
else bad "check 6 did NOT fire (rc=$RC)"; fi

echo
echo "self-test: $PASS passed, $FAILED failed."
[ "$FAILED" -eq 0 ] || { echo "A control did not behave. docs-lint's green result is NOT evidence until this passes."; exit 1; }
echo "Every hard check has been shown to go red, and the clean fixture goes green."
exit 0
