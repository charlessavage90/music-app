# Handoff — requirements baseline + Track 3b executed, 2026-07-29

**Role: SUPERSEDED — this is NOT the current handoff.** Superseded on **next actions only**
by [`2026-07-29-HANDOFF-algorithm-selection.md`](2026-07-29-HANDOFF-algorithm-selection.md),
which is current. Everything below about what completed in *this* session's work remains
accurate; its "what the next session does" is stale — that session ran, and re-sequenced
the task order it names (the cap-selection simulation moved from first to third). Supersedes
[`2026-07-28-HANDOFF-track3-executed.md`](2026-07-28-HANDOFF-track3-executed.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a seam handoff, not mid-flight.** Two bodies of work ran to completion in one
session and one branch (`requirements-track3b`, PR to be opened at closeout): the owner's
requirements rewrite, and Track 3b executed end-to-end under it — pre-registration,
protocol review (15 findings amended in pre-arm), ceiling gate, arms, harness review
(complete independent reproduction), verdict read. Nothing is in flight; no server is up.

## What the next session does

**Plan the graph rebuild — the owner's instruction, 2026-07-29.** Entry points, in order:
the DD-F1 defect ruling in `PRODUCT-REQUIREMENTS.md` §8 (superstars have no downward
edges; ruled a defect, not a limitation); `MKS-5b` (any cap alternative must demonstrate
its degree bound by simulation first — the agreed cap-selection simulation from the
archive is that demonstration and the natural first task); `STC-6` (the co-occurrence
threshold lever, needs re-crawl not rebuild); `BTF-4` (the cap-selection option, measured
on a different graph, carried as an option not a candidate); and the resume brief's §2
confound, **now stratified**: pricing was the mid-band barrier (removed by devices —
Tracks 3/3b prove delivery where edges exist) and structure is the superstar barrier
(DD-F1, device-confirmed). **The nameless-artist drop rule comes due inside this plan** —
its condition is "before the next production rebuild" and this is that plan; schedule it
as a task, and `acceptance.py` stays unweakened.

## Which documents are now wrong, and in which direction

- **`WHAT-GOOD-LOOKS-LIKE.md` is partially superseded** — banner in place; where it and
  `PRODUCT-REQUIREMENTS.md` disagree, the latter governs; §10 there lists the
  disagreements (value 2's lengthening clause first; value 5 promoted to a Must).
- **Track 3's verdict wording** (`NEXT.md` until today, and its execution log) rests the
  trade on value 2's lengthening half. That framing is superseded by the requirements;
  the Track 3 *figures* stand untouched.
- **The Track 3b pre-registration was amended pre-arm** per TB-P1 (its §9 is the index)
  and twice corrected post-run per TB-P5H-3/4 — read it with its markers; the original
  unamended claims must not be quoted.

## Overturned or corrected claims a well-meaning editor must not revert

- **Value 2's "both, or neither counts" was a documentation conflation** — owner-stated;
  do not restore it to WGLL.
- **TB-A4/TB-A5 do not exist and DD-A4/DD-A5 stay struck**; the floor axis is dead on
  `pairs_v2` from k = 3 — do not re-add floor arms to either track.
- **"The gradient is non-monotone again" was corrected in place** (execution log §3):
  Track 3b's primary gradient is strictly monotone decreasing — the opposite shape to
  Track 3's.
- **The ceiling is not a per-cell bound in either direction** (TB-P5H-4/5): 23-cell
  denominator vs the arms' 24, and arms cross it on up to 7/23 cells.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (rows for the REQ doc, the
prereg, the execution log), WGLL's banner and value-2 note, `CLAUDE.md`'s
what-is-better orient row (minimal correction, delta reported in the closeout), the
Track 3 handoff's role line, `TEST-QUEUE.md` (N/A entry).

## What this session knows that is not otherwise in the durable record

- **The candidate-pool recompute is about an hour and needs no new walks** — both tracks'
  paths and fame tables are committed; rescoring DD arms under TB statistics is the whole
  job. Parked with the decisions it serves.
- **This session's position on the pool, if it is ever picked up:** TB-A2 is out on
  TB-P5H-1 (pass carried by two pairs); the real comparison is TB-A3 (deepest, roughest,
  most floor-exposed) vs TB-A1 (gentler, keeps growing with presses) vs DD-A2 — and the
  choice is taste, not measurement.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) both
  default 0.0 and must stay there** — analysis-only; production expressions unchanged;
  TB-G1 at 212/212 is the evidence.
- **The shared fame name-cache** (`2026-07-24-track2-arm-scorer/fame_cache.json`) grew by
  several hundred names this session (committed). Future fame fetches on these pair
  families are mostly cache hits.
- **The one-day cadence worked because reviews ran first** — TB-P1 before anything was
  built (its top findings needed no measurements), TB-P5 before the read. Same lesson as
  Track 3's closeout, now confirmed twice; still a recommendation, not a CLAUDE.md rule.
