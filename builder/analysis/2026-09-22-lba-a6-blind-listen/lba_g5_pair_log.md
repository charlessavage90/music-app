# `LBA-G5` pair log — the artist pairs used during the use gate

**What this is (`LBA-AM5`):** one line per journey the owner ran on the `LBA-A6` candidate during
`LBA-G5`, the unblinded use gate — the two endpoint artists, in the order entered. It records
**pairs, not verdicts per journey**. It yields no figure that may enter the record as a
measurement of path quality (`LBA-AM4` bar 1). Pairs here carry the memory tell and are
exclusions for any later listen (`GBL-AM1`, `lbl_pairs.py` step 2).

**Created 2026-09-24, after the `LAL-R1` verdict existed and before any journey was run on the
candidate under the gate.** The candidate served was `LBA-A6-candidate.bin`, sha256
`28311d81…`, booted with `ARTISTPATH_GRAPH_SHA256` read from its sidecar.

**Gate period:** 2 days of actual app use, maximum (`LBA-AM4`). Started 2026-09-24.

**How this file is filled — DERIVED, never hand-written (owner's ruling 2026-09-24: tracking pairs
by hand is not realistic).** The API already emits one telemetry event per journey request with both
endpoint names (`api/src/artistpath_api/telemetry.py`), and during the gate its stdout is captured to
`C:/unsung-fast/lbd-artifacts/lba-g5-logs/*.log` (outside the repo, beside the candidate). At the
closeout after the gate, `lal_g5_pairs.py` in this directory folds those events into the lines below:
one per journey in the order requested, with the number of rerolls that followed it. A journey is a
request with no exclusions; rerolls are the same pair. `api-part1.log` covers the gate's first hours,
captured before the restart that pointed the server at that folder; nothing was lost between them.
**One gap is known:** the servers were killed when the session that started them was retired in
Orca, so **no telemetry exists between the last request in `api-part3.log` (about 10:14 on
2026-09-24, a Guster journey) and the first in `api-part4.log` (started 10:55)**. Journeys the owner
ran in that window, if any, are missing from the derived lines; he was asked for them by hand on
2026-09-24 and any he supplies are appended below marked `(hand-recorded, gap)`. A restart must keep
appending to this folder — `start-servers.ps1` there does.

## Pairs, one per line: `from → to  (rerolls: N)` — written at the closeout after the gate

