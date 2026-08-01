# Handoff — `TAS-4`, `TAS-6`'s selection half, `TAS-AM3` and `TAS-AM4`, 2026-07-31

**⚠ Role: SUPERSEDED 2026-08-01 on next actions by
[`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md)**, which continues
this same track and is the CURRENT handoff. **This document remains authoritative for the
`TAS-AM3`/`TAS-AM4` work's own internals**, but its status claims are stale: it says "Tasks 5–8
NOT started" and treats the routing-side instrument question as owed. **Tasks 5–7 have since
run** — `TAS-AM5a`/`b` passed, `TAS-AM5c` fired, and `TAS-6`'s routing half is vacuous. Its
"open decision" section is also settled: `TAS-5` ran, and it was the right call.

*(Original role line, retained:)* Supersedes
[`2026-07-31-HANDOFF-release-tag-coverage.md`](2026-07-31-HANDOFF-release-tag-coverage.md)
and [`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md)
on **next actions only** — both remain authoritative for their own tracks' internals. It does
**not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**This is a SEAM handoff, not mid-flight.** Everything is committed and pushed, nothing is in
flight, no subagent is running, no background job survives, no port is listening, and the tree
is clean. It is not the seam the *plan* named — Seam A sat after Task 4 and this went past it
— but two material §8 amendments landed, and `CLAUDE.md` makes a material mid-flight amendment
a seam in its own right: there is a new governing document and the next session reads it cold.

## What this work is

Continuation of the `TAS-` probe from Task 4. Governing document:
[`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md).
Record: [`2026-07-30-tag-discrimination-execution-log.md`](2026-07-30-tag-discrimination-execution-log.md),
**§9–§13** (this session; §1–§8 are the previous one's).
Probes: `builder/analysis/2026-07-30-tag-discrimination/`.

**Tasks 1–4 done, plus Task 7's two selection-side halves. Tasks 5–8 NOT started.**

## The three things that must not be reverted

1. **`TAS-6` is ADVERSE and that bars an adoption recommendation for the BUILD-TIME
   architecture** — §5's read, and it holds whatever `TAS-4` and `TAS-5` show. **It is not
   softened by the `REL-` frame existing.** Its denominator is thin and that is recorded as
   information, **not** as grounds to revisit the bar. No bar may move now that results exist.
2. **The §4 red check is WITHDRAWN AS UNACHIEVABLE** (`TAS-AM3`), not merely unfired. For a
   Jaccard-overlap device, randomising labels destroys overlap rather than randomising it, so
   *every* correct null control must report a small number. Do not "fix" the harness to make
   it fire. The withdrawn text stays visible per the `TAS-AM1` precedent — **do not tidy it.**
3. **`TAS-AM3` and `TAS-AM4` were appended AFTER results existed** and disclose it at their
   heads. Do not remove those disclosures to make the document read more cleanly; they are the
   only thing a later reader has to price the amendments with.

## Status of the instrument question

**Discharged for the SELECTION side only.** `TAS-AM3a` passed at every λ — bit-identical masks
against `td_turnover.mask_multiplicative` and exact reproduction of the committed `TD-2`
figures. **The ROUTING side still owes its own**, and `TAS-AM3` already specifies it: the same
pair with `find_path_coh` in place of the ranking path. Conflating the two is the defect most
likely to be introduced next.

## The open decision, and what I would do

**Whether to spend on a `TAS-4`/`TAS-6` re-run against the `REL-` enriched frame.** `TAS-AM4`
measured the candidates and **licensed a recommendation only** — no re-run, no adoption.

**If I were continuing: run `TAS-5` next, not the re-run.** Three reasons. The router-side
architecture is untouched by the adverse `TAS-6`, whose two halves measure the two
architectures separately and are never combined. The owner's stated instinct — recorded in
§12.1 as an instinct, **not** a directive — favours routing. And §5 says a `TAS-5` read
without `TAS-4` beside it is uninterpretable, so the comparison the architecture decision
needs does not exist until `TAS-5` runs.

**If the re-run happens anyway, use `W1` (MusicBrainz release groups only), not `W6`.** The
Discogs increment buys the smaller share of remaining reach for roughly as much spread again;
the trade is clearly diminishing. Which cells to run is the session's call; whether to spend
at all is the owner's.

**What I would not do:** treat `TAS-AM4`'s favourable reads as licence to re-run without
asking, or let the coverage gain lead the reporting. `TAS-AM4` read 2 pre-commits the spread
*fall* to being the headline, and it fell on a fixed population — the control was run
expecting it might overturn that, and it did not.

## Already updated — do not re-edit

`NEXT.md`, the execution log (§9–§13), the pre-registration's §4 and §8, the plan's role line
and Task 4 Step 5, the probe directory `README.md`, `TEST-QUEUE.md`, and the two previous
handoffs' role lines.

## What I know that is not otherwise in the durable record

- **The capture is in a session scratchpad and will not survive.** Regenerate with
  `td_capture.py` (~6.5 min cold, not the ~2 min the previous handoff estimated — that figure
  was warm-cache). `td_turnover.py --verify` makes a stale one impossible to use silently.
  sha256 of the one this session used is in execution log §14.
- **`td_turnover.py` runs its full 37-arm sweep *after* the `--verify` block.** Point `--out`
  at scratch or it overwrites the committed `TD-` record. This is now in the plan's Task 4
  Step 5, but it is easy to miss.
- **`np.load` on an `.npz` is LAZY** — indexing `z["key"]` inside a loop decompresses the whole
  array each time. It cost a run here (§13.5). Materialise every array once.
- **Do not pipe a long unattended run through `tail`** — it buffers all progress away and a
  slow run becomes indistinguishable from a hung one. That is how the above went unnoticed.
- **The `doc-auditor` reported clean on this work, but three defects in the probe directory's
  `README.md` were found by a plain file-existence check** — two scripts listed that do not
  exist, and a description of a check that had been withdrawn. Whether the auditor read the
  file before or after the fix cannot be determined. **Treat "audit clean" as not covering
  whether a named file exists.**
- **Nothing about tags has been measured against the owner's ear, and cannot be offline.** The
  11 blind verdicts remain unconsumed; `ct_retrodict.py` remains committed and unrun.
