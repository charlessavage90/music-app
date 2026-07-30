# Handoff — Track B designed through its seam (CB-4), 2026-07-30

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-29-HANDOFF-graph-rebuild-track-a.md`](2026-07-29-HANDOFF-graph-rebuild-track-a.md)
on next actions. It does **not** state project status: for that read
[`NEXT.md`](NEXT.md), which owns it.

**This is a seam handoff, not mid-flight** — the seam is the one the plan named at
authoring time (`CB-4`): the pre-registration is committed, every instrument gate has
run green **and** red, and nothing is in flight. No subagent running, no server on any
port, tree clean.

## What happened

Track B (the cap-rule selection simulation, `MKS-5b`'s owed pricing instrument) was
designed and instrumented end to end: the `LBS` source-semantics findings note, the plan
(`plans/2026-07-30-graph-rebuild-track-b.md`, owner's scope rulings in §0), the
`CB-1`–`CB-3` harness with all gates passed, the `CB-P1` design probe, and the committed
pre-registration (`specs/2026-07-30-track-b-cap-selection-preregistration.md`, `CRS-`,
amended `A1`–`A5` after a second consultant round, all before any scoring). Retained
log: [`2026-07-30-track-b-design-execution-log.md`](2026-07-30-track-b-design-execution-log.md).
Branch `lb-source-semantics`, PR #51.

## What the next session does

**`CB-5`: build and score all 24 cells** — offline, deterministic, well under an hour of
compute — **then `CB-6`: the reads, in the prereg's own order.** Non-negotiables the
prereg already fixes, listed here only because they are order-sensitive:

1. **Dry-run the scorer on `ALG-E`-`MK50` first** (already built by the gates), per the
   Track A scorer-defect lesson.
2. **`ALG-E`-`MK50`'s `CRS-C5` is scored before any other cell's `C5` is opened**
   (`CRS-A2`), per class; a nonzero class gets its bar fixed blind in a further §8
   entry before proceeding.
3. Reads run `R0 → R1 → R1a → R2 → R3 → R4`, nulls included, exposure map before any
   escalation.

The owner said a fresh session picks this up. It reads the prereg cold — which is the
condition the seam was designed for.

## Claims settled here that a well-meaning editor must not revert

- **The `limit` token is the instructive top-N and the observed list ceiling is 100 in
  every arm** (`LBS-3`) — an earlier in-session read ("limit is not list length") was
  retracted when the source's "upto 2x" clause reconciled the data; do not resurrect it.
- **`session_300` is 300 seconds, not minutes; the per-pair cap is `contribution`, per
  user** (`LBS-5`/`LBS-6`) — the staff forum comment is corrected by source and must not
  be re-imported over it.
- **Weakest-first (and popularity-proximity) trims provably delete every reverse-only
  famous→obscure edge** — checked in all 10 `CB-P1` rows. `banded_quota` is the only
  selectable union configuration bearing on `DD-F1`. A `CRS-C5` null on a family the
  prereg's §0 table marks "no" is **confirmation, not a finding**.
- **`CS-P0c`'s bar does not cover the union family** — its own text scopes it to
  own-list selection. Do not re-cite it as "no cap rule can fix DD-F1".
- **The famous-pair baseline is not "structurally zero" for band pools** — even the
  top-0.1% band is only 87.5% zero-downward (`CS-P0b`); the superstars' zero was five
  artists, not a band. `CRS-A2` owns the corrected protocol.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (three new rows),
`TEST-QUEUE.md` (N/A entry), the Track A handoff's role line, the plan's checkboxes
(annotated through `CB-4`), and the `rc_raw_records.json` re-scoring deferral
(discharged by supersession, recorded in the prereg §0 and struck in `NEXT.md`).

## What I know that is not otherwise in the durable record

- **The bound-check and gate builds left cell artifacts in `builder/scratch/cb-cells/`**
  (gitignored, manifest sidecars with sha256s beside each). They are byte-deterministic
  and `CB-5` may keep or rebuild them identically; the comparative-looking numbers in
  `cb_bound_check.json` remain deliberately unread and must stay unread until the
  prereg's reads consume them.
- **`CRS-A5`'s endpoint claim (`POST /1/popularity/artist`, 200/200, zero nulls) is the
  consultant's report, not this session's verification.** One re-verifying request at
  scoring time before using it, descriptive only, per the amendment.
- **The `CB-3` gate's 20-triple slice covers only two pair classes** — deliberate (it
  gates the instrument, not the sample); the real run uses the full draw, whose famous
  classes exist only after `routable_everywhere` filtering, so `CRS-G3`'s readability
  flags are the thing to watch on `ALG-B` cells.
- **Snyk ran clean (0 issues) on every new analysis file, via the MCP server** — the
  CLI is still not on PATH here; nothing security-shaped is owed on this track.
