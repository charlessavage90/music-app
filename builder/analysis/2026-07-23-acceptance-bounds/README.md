# Acceptance bounds — the G1 guard, demonstrated at full scale

`check.py` runs `artistpath_builder.acceptance.PRODUCTION_ACCEPTANCE` against
both real 75k artifacts and asserts the criteria **accept** the adopted graph
and **reject** the defective one.

`graph-t15-capfix.bin` serves as the negative case because Phase 1 log §2.8
records that its Arm 1 replay reproduced capfix exactly — N, E, MBID set, and
every per-artist degree. It is the §2.8 defect, at full scale, on disk.

**Why this exists alongside the unit tests.** `builder/tests/test_acceptance.py`
reproduces the defect in miniature through the same one-knob intervention
(clipped vs unclipped top-k ranking), but there `k = 4` caps every degree at 4,
so the only signature available is *deletion*. This script is where the
famous-degree collapse is visible too, and it is what the chosen bounds were
selected against.

**What separates the two artifacts, and what does not.** The top-25-by-popularity
median degree differs by roughly a factor of five; the whole-graph median degree,
N and E differ by a fraction of a percent. That is not a defect in the bounds —
log §2.8 states it directly ("the global shape does not move"). The global shape
bounds in `PRODUCTION_ACCEPTANCE` are therefore a **regression tripwire for a
different failure** (a build that silently loses a large share of the graph), not
a §2.8 detector. The §2.8 detectors are canonical presence and the famous-degree
floors.

Needs `builder/scratch/graph-t15-tiebreakfix.bin` and
`builder/scratch/graph-t15-capfix.bin` (gitignored; identified by sha256,
asserted in-script). Paths hardcoded deliberately: this is a record of what was
executed, not a maintained tool.

Run, from `builder/`:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-23-acceptance-bounds/check.py
```
