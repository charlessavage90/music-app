# Handoff — the `TCR-` re-run computed, 2026-08-06

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-06-HANDOFF-tce-void.md`](2026-08-06-HANDOFF-tce-void.md) on next actions. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff.** The probe ran to completion under its committed pre-registration,
everything is committed and pushed, nothing is in flight, and the degradation tell did not
fire.

Branch `cocredit-relationship-probe`, **draft PR #87**, pushed. Reasoning:
[`2026-08-06-tcr-rerun-execution-log.md`](2026-08-06-tcr-rerun-execution-log.md). Figures:
`builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/`, which **owns them**. **No shipped
code was touched.**

---

## Documents that are now wrong, and in which direction

**None that I know of.** `docs/README.md` gained two rows (the `TCR-` prereg and its
results directory) and had one **pre-existing staleness corrected**: the `TCE-` spec's row
still said "NOT YET EXECUTED" after the void run. `NEXT.md` was rewritten at this closeout.

## Claims that must NOT be reverted by a well-meaning editor

- **`TCR-` is COMPUTED and nothing reads enriched.** Arm A: `C1` null, `C3`/`C4` depleted,
  `C5` *below* its own null. Arm B: `C1` `no_read_licensed` (`TCR-G3`), `C3` null, `C4`
  depleted. **Do not retro-assign a branch label** — the results README's §4 records that
  no pre-registered branch fires as written (a gap in the carried branch table) and why
  the closure consequence is licensed anyway.
- **`no_read_licensed` is not `null`.** Arm B's pinned median is a finding about the drop
  filters (85 % of its reference artists have no thin neighbour), never a null result.
- **`TCE-` remains VOID and `TCR-` inherited no outcome from it** — none existed.
- **The same-name population question is STILL OPEN.** The eyeball read found correctly
  resolved personnel dominating, not same-name junk — that neither closes nor surfaces
  the population question, and the isolated common-name candidates license no rate.
- **Depletion is not evidence for widening the drop rule** (closed by the owner) and not
  evidence about journeys — no journeys were run, and the barred reads travel.
- **The regression-anchor labelling in `TCR-G1`** (Leon Bridges, Khruangbin) is
  deliberate honesty, not a defect to tidy away.

## Already updated — do not redo

`docs/README.md` (two new rows, one correction), `NEXT.md` (rewritten at closeout), the
previous handoff's role line, the execution log, `.gitignore` (two cache rules for the new
directory).

## What I know that is not in the durable record

**Empty, checked rather than asserted:** every figure reported to the owner was verified
present in a committed file (`tcr_result.json`, `tcr_runstate.json`,
`tcr_eyeball_top20.json`, the results README) before retirement. The instrument
verification (tie machinery vs brute force, band assert shown red) is recorded in the
execution log §4.

## Anything in flight

**Nothing.** No subagents, no background jobs, no listeners: ports 8000/5173/5174 are all
clear, and **the stale Vite server the previous handoff flagged (PID 249084) is gone** —
nothing further is owed on it.

## What I would do if I were continuing

Nothing in this track — it is closed. The one thing the closure changes elsewhere: **the
owner's deferred Option C (same-name population probe) was waiting on this re-run and is
now unblocked.** Whether to spend a session on it is his call; the eyeball read's
contributor dump (`tcr_eyeball_top20.json`) would be a cheap starting corpus for it if he
takes it.
