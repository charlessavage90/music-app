# Cap-ranking replay — the scripts behind §2.8

These four scripts produced every figure in **§2.8** of
`docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`, which determined
why the most popular artists collapsed to near-zero degree in the adopted graph.

They are committed because a checksum-only artifact plus a prose description is not
enough to re-run an experiment, and these were about to be lost with a scratchpad
directory. **Cite figures from §2.8, not from here** — the document owns them.

## What each one does

| Script | Answers |
|---|---|
| `part1_probe.py` | Is Radiohead absent from the node set or pruned by the largest-connected-component step? Does the collapse track control degree, popularity, or neither? |
| `precheck_mbid.py` | Is the MBID tie-break active? Compares destination-MBID percentile in `capfix` against `d025` as a no-tie-mass null arm. |
| `replay.py` | **The decisive experiment.** Replays the build from the archive to `pipeline.py:218`, then branches on exactly one knob — whether the top-k selection ranks clipped or unclipped scores. Arm 1 must reproduce `capfix` exactly; that check is what makes Arm 2 interpretable. |
| `decompose.py` | How wide is the blast radius, and does a corrected survival model account for the observed degrees without a third mechanism? |

`replay.log` is the run record for `replay.py`.

## Before you re-run them

- **Paths are hardcoded**, including a scratchpad path in `decompose.py`. That is
  deliberate: these are a record of what was actually executed, not a maintained tool, and
  refactoring them would weaken them as evidence. Adjust the constants at the top.
- **`precap.npz` is not committed.** It is a ~75 MB cache of the pre-cap edge arrays that
  `decompose.py` writes on first run and reuses afterwards. Delete-and-regenerate is
  always safe; it is derived entirely from the archive.
- **They need `builder/scratch/graph-archive/` and the comparison artifacts**, none of
  which are in git. Artifacts are identified by checksum only — verify before drawing any
  conclusion, since several graphs exist and they are not interchangeable.
- `replay.py` reads all 75,000 archive files and rescales ~7.5M edges. Minutes, not
  seconds. Use `python -u` — a buffered job writes a 0-byte log and looks hung.

## Note for a reachability sweep

Nothing imports these, and that is correct. They are **research tooling invoked manually**,
in the same category as `nulls.py` and `stats.py` — see Phase 2 execution log §18's B2
check, which records that category explicitly so a future sweep does not read them as
orphans. They produced findings that are in the record, which is the test that matters.
