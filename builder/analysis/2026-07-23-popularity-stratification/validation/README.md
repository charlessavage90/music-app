# Validation of §2.9 — the scripts behind §2.10

Written by `ml-graph-analyst`, briefed that §2.9 was an **unverified outside claim** and
that overturning it was the useful outcome. These produced every figure in **§2.10** of
`docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`.

**Cite figures from §2.10.** §2.9's own numbers are partly struck — see its banner.

| Script | Answers |
|---|---|
| `p1_fixedref.py` | The circularity confound. Recomputes assortativity for all arms against a single fixed popularity reference, and against two alternative references as a robustness check. |
| `p1_nulls.py` | **The one §2.9 was missing.** Structure-preserving nulls — uniform pruning to capfix density, score-greedy pruning, union-thinned, and degree-sequence-matched rewiring. Produces the 15.6× depletion ratio. |
| `p1_ctrlnull.py` | The same null applied to `control`, which is what shows control sits at chance (ratio 1.01) rather than being genuinely disassortative. |
| `p1_addendum.py` | The 2×2 attribution factorial: reciprocity vs ranking vs density, one knob per axis. |
| `p1_exits.py` | Obscure-exit counts per popularity band — the existence-vs-competition distinction. |

## Two things to know before re-running

- **They need `precap.npz` sitting in _this_ directory.** Every script here does
  `np.load(Path(__file__).parent / "precap.npz")`, so it must be **beside the script**, not
  wherever it was generated. It is ~75 MB and deliberately not committed.

  It is written by `../../2026-07-22-cap-ranking-replay/decompose.py`, whose `SCR` constant
  points at a **session-specific temp directory that no longer exists**. Change that constant
  to this directory, or generate it and copy it here. *(Recorded rather than fixed: these
  scripts are a record of what was executed, and the hardcoded paths are part of that record.
  Found by closeout B4.)*
- **Run them from the `api` venv, not `builder`** — `api` has scipy and `builder` does not:

  ```bash
  cd api && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u <script>
  ```

## The known weakness, recorded rather than buried

The degree-sequence null in `p1_nulls.py` is a **randomised greedy b-matching, not an exact
configuration-model sample** — 3.9% of control's degree quota and 7.7% of capfix's went
unmet. Two seeds agree to three decimals and the achieved max degree is exactly 50, so it is
unlikely to matter. **If anyone leans hard on the 15.6× figure, an exact rewiring is the
stronger instrument** and this is the thing to rebuild first.

## Note for a reachability sweep

Nothing imports these — research tooling invoked manually, same category as the sibling
`analysis/` directories. See Phase 2 execution log §18's B2 check.
