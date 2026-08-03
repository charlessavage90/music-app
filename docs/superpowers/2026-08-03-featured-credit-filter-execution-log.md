# Execution log — the featured-credit filter track (2026-08-03)

**Role: ACTIVE — the retained execution log for this track.** Appended per task, not at
closeout. Branch: `featured-credit-filter`. Session: `featured-credit-filter-builder`.

**Governing inputs, all pre-existing:** the owner's ordering ruling and track description
in [`NEXT.md`](NEXT.md) (top block, 2026-08-02 night), and the fame-instrument execution
log [§5/§5a](2026-08-02-fame-instrument-execution-log.md) — the class mechanism, the two
worked instances (田島賢 `7e4f57b3`, TJ Brown), and the FAM-6 no-page rows. The rule shape
is **ruled, not open**: a keep-check extending the adopted no-release drop rule
(commercial-DSP presence + something plays), never a purge. What this track designs is the
**detector** and produces the frozen lists and wiring; whether the class gets its own
small calibration hand-review is **the owner's spend, flagged not decided**.

## §1 — Orientation and setup (2026-08-03)

- Session-start ritual run by the owner; seam handoff, clean tree, no concurrent session.
- One stale line found and fixed in `NEXT.md`: PR #66 is merged (`f9f42ce`), so the
  "owed decision" line is discharged. Landed as this branch's first commit per the
  document's own fresher-record rule.
- Verified before building on the record: `drop_no_release_tail` /
  `NoDropListForAlgorithm` resolve in `pipeline.py`, `no_release_drop.py`, `config.py`,
  with the twelve-test file and the mirrors guard — `NEXT.md`'s "the wiring machinery all
  exists" claim is true.
- Exploration (two subagents, reports retained in session): the cheap detector is a
  ~2.4 min pass over the 18 GB **release-group** dump using `rel_common`'s existing
  credit-split machinery (`rel_rg_dump.collect()` idiom), not the 48.7 min release-dump
  pass. `rel_rg_raw.json`'s `"a"` flag is NOT the clean split — it folds in
  compilation/live/broadcast type exclusions — so the census re-derives sole-credit as
  `rg_artist_id(record) == mbid` alone.

## §2 — Census design decisions (2026-08-03, before the run)

*(to be appended as taken)*
