# Tie-break fix verification — Track 1 of the repair+retune spec

`verify.py` asserts that `graph-t15-tiebreakfix.bin` (built by the fixed
builder: `mutual_knn_cap` ranking unclipped strengths) reproduces the
Phase 1 log §2.8 Arm 2 topology, and that emitted scores on shared edges
and popularity ordering are unchanged against adopted `capfix`.

Expected values inside the script are copies for execution — **cite the
Phase 1 log §2.8 and the adoption findings doc, not this script.**

Needs `builder/scratch/graph-t15-capfix.bin` and
`builder/scratch/graph-t15-tiebreakfix.bin` (gitignored; identified by
sha256, asserted in-script). Paths hardcoded deliberately: this is a
record of what was executed, not a maintained tool.

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-23-tiebreak-fix-verification/verify.py` (from `builder/`).
