# Handoff — the un-listenable filter (`ULF-`) is built, censused and wired, 2026-08-05

**Role: SUPERSEDED on next actions by
[`2026-08-05-HANDOFF-msw-seam2.md`](2026-08-05-HANDOFF-msw-seam2.md)** — every action this
note owed is discharged: PR #78 merged (`7961530`), the `ulc-filter-fix` PR merged as #80
(`fd6b140`), and the owner took the map-switch decision on 2026-08-05, choosing the full
`ULC-A4` package. **Remains authoritative for the `ULF-` filter work's own internals**, and
its "must not be reverted" list still binds. *(Original role line:)* **ACTIVE — this is the
CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-05-HANDOFF-ulc.md`](2026-08-05-HANDOFF-ulc.md) on next actions. It does **not**
state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam handoff.** The remit ran to its end, both lists are frozen and shipped, the tree is
clean, no listener on any port, nothing in flight.

**Branch** `ulc-filter-fix` (off the `ULC-` track's tip, so it merges after PR #78), draft PR
open. **The next action is the owner's** — two merges and the map-switch decision; `NEXT.md`
owns the detail.

---

## What is done

The filter fix, `ULC-F1` and `ULC-F2`, and the re-census of both drop lists — the whole
remit. Governing document:
[`specs/2026-08-05-unlistenable-filter-rule.md`](specs/2026-08-05-unlistenable-filter-rule.md).
Reasoning: [`2026-08-05-ulf-filter-fix-execution-log.md`](2026-08-05-ulf-filter-fix-execution-log.md).
Figures: the frozen payloads under `builder/src/artistpath_builder/data/` and
`builder/analysis/2026-08-05-ulf-census/ulf_census.json` — cited, never restated.

## Which documents are now wrong, and in which direction

- **None known to overstate.** `NEXT.md`, `docs/README.md`, and the `ULC-` results §5
  deferral strikes are updated; the previous handoff's role line names this one.
- **`no_release_drop.py`'s docstring identity claim** was the one shipped-code sentence the
  work overturned; it now carries the supersession inline rather than being rewritten,
  because its lists remain frozen-era data.

## Claims that must NOT be reverted by a well-meaning editor

1. **The owner's cut-line ruling stands: `ULC-D2` as ruled.** Keith Scott is a *named
   residual false negative* (spec ULF-6). Do not "improve" the predicate to catch him, and
   do not carve soundtracks in to rescue CROOVE — both were declined with costs in view.
2. **CROOVE is struck from the acceptance canonical list by owner ruling** — the reasoning
   is at the site in `acceptance.py`. Do not restore the name; equally, do not remove the
   four §2.8 deletion detectors, which are untouched and load-bearing.
3. **The frozen verdicts carried, deliberately un-re-run.** Re-resolving a prior keep or
   drop could reverse an adopted verdict; the mixed snapshot is the design, not a shortcut
   (payload `snapshot_warning`).
4. **`keep_clip_provenance` is instrument data for `ULC-F4` and no read of it is licensed**
   (spec ULF-2). Do not summarise it into a finding.
5. **The two old flags and lists remain functional on purpose** (era-pinned probes construct
   configs with them). Retirement has a success condition (ULF-3); do not delete them early,
   and do not treat their redundancy as an accident.
6. **A keep among the six worked instances would be a report-not-absorb event** (ULF-6) —
   none occurred: all six are dropped in both populations.

## What has already been updated — do not re-edit

`NEXT.md` (rewritten, new top block); `docs/README.md` (rows for the spec, this handoff,
the execution log); `ULC-` results §5 (`ULC-F1`/`F2` struck in place); the previous
handoff's role line; `builder/analysis/README.md` (the `census-coverage/` live-store
exception).

## What I know that is not in the durable record

**Nothing load-bearing.** Two small operational facts, folded here so the record is whole:
the clip stage's single refusal was Deezer HTTP-shaped and settled on the first re-run
(one artist, no pattern); and the coverage store plus worklist are untracked by design
(the `REL-` template) but sit on this machine only — `census-coverage/README.md` carries
the warning, and regenerating costs about an hour.

## Owed, and by whom

- **Owner:** merge draft PR #78, then the `ulc-filter-fix` draft PR (that order — the
  second branches off the first); decide the map-switch form (results §4.1) — the filter
  fix makes either variant a genuinely new candidate under the `GBL-` run-once rule.
- **Nobody yet:** `ULC-F3` (crawl resume cannot extend) still blocks any crawl extension;
  `ULC-F4` (keep-check name resolution) is its own track and now has its measurement
  waiting in the payloads.
