# Why the low-degree artists are low-degree — measurements, 2026-07-26

Follow-on to `../2026-07-25-mutual-knn-stranding/` and
`../2026-07-26-low-degree-census/`. Backs
`docs/superpowers/findings/2026-07-26-stranding-causes.md`, which owns the
interpretation. **`REPORT.md` is the deliverable and owns every figure — cite it,
do not restate its numbers.**

**All four scripts are read-only.** They read the adopted artifact and the crawl
archive, and write only into this directory. No rebuild, no routing change, no
config change, nothing adopted, nothing proposed.

| script | run from | reads | produces |
|---|---|---|---|
| `dump_artifact_nodes.py` | `api/` | adopted APG1 artifact | `artifact_nodes.json` |
| `split_causes.py` | `builder/` | crawl archive + that dump | `causes.json` |
| `report_split.py` | `builder/` | `causes.json` | `REPORT.md` |
| `verify_residual.py` | `builder/` | crawl archive + that dump | the residual check, stdout only |

```bash
# from api/
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-26-stranding-causes/dump_artifact_nodes.py

# from builder/
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  analysis/2026-07-26-stranding-causes/split_causes.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  analysis/2026-07-26-stranding-causes/report_split.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONPATH=analysis/2026-07-26-stranding-causes \
  uv run python -u analysis/2026-07-26-stranding-causes/verify_residual.py
```

The archive scan takes several minutes: 75,000 files under OneDrive.

## Why there are two processes

`builder/` and `api/` **share no code by design** — the APG1 contract is the
interface. The reader lives in `api/`; `is_special_purpose`, which `split_causes`
must import rather than reimplement, lives in `builder/`. One of them has to
cross the gap, and data is the safer direction, so the artifact's node table is
dumped to JSON and read back.

## What is committed and what is not

`causes.json` **is committed** — it is the measurement, and regenerating it costs
a full archive scan. `artifact_nodes.json` is **not**: it is a mechanical re-dump
of the artifact, regenerated in seconds, and it is listed in this directory's own
`.gitignore`.

**That `.gitignore` is inside this directory, so whether it applies depends on
which branch you are standing on** — a session checking from a branch where this
directory does not exist will see nothing and may report the file as unbacked.
That is `CLM-13`, and this paragraph exists so it does not happen twice.

## The model, and the correction this directory makes to it

The candidate model is `../2026-07-25-mutual-knn-stranding/reciprocity.py`,
**imported rather than copied**, so there is still exactly one implementation of
the builder's cap and its validation gate still guards it.

**One correction, and it is load-bearing.** That model takes the candidate
population to be the set of archived responses. The builder does not:
`build_from_archive` computes `known = set(payloads)` and then `known -=
excluded`, dropping MusicBrainz special-purpose placeholders **before** any
ranking (`pipeline.py:131–152`). Modelling the population one member too large
lets a placeholder occupy a slot in someone's top-50 and push a real candidate
out. `split_causes.py` imports the builder's own `is_special_purpose` and applies
it, and runs the six-artist gate **before and after** the correction so neither
version is taken on trust.

This is a limitation of the 2026-07-25 model that its own six-artist gate did not
catch, because none of those six is affected. **It is not a defect in the
findings that model backs** — the placeholders are 7 artists in 75,000, far too
few to move a distribution — but any future reuse of `reciprocity.py` should
apply the same correction.

## Gates

Four, and all four print. Gate 3 is the one that matters: the candidate count is
the quantity the split keys on, and it is exact for all 12,088 artists. Gate 4
leaves a ten-artist residual that `verify_residual.py` accounts for and
`REPORT.md` explains — it cannot move the split, and every degree in the report
is the artifact's own rather than the model's.
