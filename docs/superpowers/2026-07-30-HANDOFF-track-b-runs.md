# Handoff — Track B runs and reads complete, 2026-07-30

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-30-HANDOFF-track-b-design.md`](2026-07-30-HANDOFF-track-b-design.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a seam handoff** — Track B is complete through `CB-6`: all 24 cells built and
scored, raw outputs committed before any read, the six reads written in the prereg's own
order with both nulls, and the four-part report committed. Nothing in flight, no server
on any port, tree clean.

## What happened

`CB-5`/`CB-6` per the handoff above: gates re-run green and red at the scoring commit,
`CRS-A2` baseline measured zero in both famous classes (so §2 stood unamended), all
reads resolved under their pre-registered bars. **Results of record:**
[`findings/2026-07-30-track-b-cap-selection-results.md`](findings/2026-07-30-track-b-cap-selection-results.md)
(the four-part report). Raw record: `builder/analysis/…/cb_scores.json`. Retained log:
[`2026-07-30-track-b-runs-execution-log.md`](2026-07-30-track-b-runs-execution-log.md).
Branch `track-b-runs`.

## What the next session does

**Nothing is queued for a working session.** The next action is the owner's: the two
parked decisions (cap rule for any rebuild; `ALG-B` adoption) now have the
recommendation input the track existed to produce, and both still owe the blind listen
(`REQ-38`). `NEXT.md` carries the state.

## Claims settled here that a well-meaning editor must not revert

- **The two nulls are pre-committed nulls, not failures.** `R1a`: reciprocity *alone*
  is nearly free at k = 100 on both archives. `R2` on `ALG-E`: the quota cells' reserved
  famous→obscure edges were verified present at famous nodes and the router takes none
  at production weights — **a router finding**, not "the quota rule cannot work", and
  explicitly not a licence to retune weights.
- **`PS100` is byte-identical to `MK100` on both archives** (`LBS-3`: no list exceeds
  100, so the selection key never fires). Never treat them as two data points.
- **The incumbent's loss at bound 50 is on coverage criteria** (stranding, exclusion),
  with path evidence from famous pairs only after the `CRS-G3` attrition; nothing
  offline measures listening coherence, and the bound-100 cells carry a measured
  hub-transit increase in the direction the ear condemned.
- **The pair-set attrition decision is closed**: 82 → 39 under the committed
  routable-everywhere restriction; the five `× lower` classes are unreadable per
  `CRS-G3` and were NOT redrawn — a redraw is a new §8 amendment designed cold, not a
  patch.
- **Tie-domination is measured** (`CRS-H1`): every `MK`/`TU` cut is decided ≥ 32 % by
  the MBID tie-break. The shares are stable; single named artists' degrees are not
  load-bearing.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (rows for the results note,
runs log and this handoff; prereg/plan/design-handoff rows updated), `TEST-QUEUE.md`
(N/A entry), the plan's checkboxes (`CB-5`/`CB-6` annotated, plus `CB-3`'s two
checkboxes that were left unticked by the design session for work that was in fact
done and recorded under `CB-4`), and the design handoff's role line.

## What I know that is not otherwise in the durable record

- **Per-path raw walks** for every cell live in `builder/scratch/cb-cells/cb_paths_raw.json`
  (gitignored, regenerable byte-identically by `--phase score`).
- **The `CRS-A5` companion resolved "max-endpoint" in count currency as
  max(total_user_count of the two endpoints)** — the percentile criterion is untouched;
  the companion is descriptive and this choice can only affect the companion.
- **Runtimes:** builds 27–37 s per cell; full scoring pass ≈ 7 min including both UC
  cells; the A5 companion fetch was 50 batched requests, ~2 min, no 429s.
- The `cb5_*.log` files beside the JSON outputs are the run transcripts, committed.
