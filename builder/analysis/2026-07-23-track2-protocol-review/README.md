# Track 2 pre-registration — protocol review measurements

`probe.py` holds the measurements taken for the `ml-graph-analyst` review of the
Track 2 pre-registration, discharging prerequisite **P8**
(`docs/superpowers/specs/2026-07-23-track2-preregistration.md` §7) and the review
gate in the repair+retune design §4.6.

**The findings document owns these figures** —
`docs/superpowers/findings/2026-07-23-track2-protocol-analyst-review.md`. Cite it,
not this script, and do not restate its numbers elsewhere.

What it measures:

- **M1** — ceiling and score grid: how many edges sit at exactly 1.0, and the
  largest non-ceiling score (which is what a `s_max` toll would have to clear).
- **M2** — currency geometry: mean raw vs percentile popularity gap per edge,
  split into lateral / exit / deep strata. This is the quantitative form of the
  §2.12 currency argument.
- **M3** — popularity tie structure, which is what makes P6's average-rank
  tie-handling rule necessary rather than cosmetic.
- **M4** — floor saturation on the twelve pre-registered pairs: how many `known`
  bypasses each pair needs before the floor relaxes to zero.

Scope was the **protocol only**. The harness did not exist when this ran and is a
separate review (P8b). No sweep arm, no `find_path` call, no network fetch, no
rebuild.

Reads `builder/scratch/graph-t15-tiebreakfix.bin` (gitignored; sha256 asserted
in-script before any measurement). Paths hardcoded deliberately: this is a record
of what was executed, not a maintained tool.

Run, from `api/`:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-23-track2-protocol-review/probe.py
```

Note it runs from `api/` and imports `artistpath_api.graph_store` — it reads
`store.pop_raw`, the post-2026-07-23 name. See `../README.md` for the rename
mapping if you are comparing its output against an older probe.
