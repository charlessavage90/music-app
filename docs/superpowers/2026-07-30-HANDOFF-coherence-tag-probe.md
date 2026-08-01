# Handoff — coherence tag probe, 2026-07-30

**Role: ⚠ SUPERSEDED 2026-07-30 on next actions by
[`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md)** —
the owner picked up the third coherence strand (tag-aware selection) that this handoff
parked, and that probe is now the live work. **Everything below about the coherence tag
probe itself remains accurate and is not superseded**: the kill gate fired, `COH-2` and
`COH-3` must still be quoted together, and `ct_retrodict.py` is still committed and unrun.
Supersedes
[`2026-07-30-HANDOFF-fame-proxy-coverage.md`](2026-07-30-HANDOFF-fame-proxy-coverage.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a seam handoff, not mid-flight.** The probe ran to its committed kill gate,
the gate fired, and everything after it is recorded. Nothing is in flight, no subagent
is running, and ports 8000/5173 are swept in the closing message. The tree is clean.

## What happened

The owner directed a one-day falsification probe of the §7 coherence thread. Branch
`coherence-tag-probe`. Record:
[`2026-07-30-coherence-tag-probe-execution-log.md`](2026-07-30-coherence-tag-probe-execution-log.md);
findings [`findings/2026-07-30-coherence-tag-probe.md`](findings/2026-07-30-coherence-tag-probe.md)
(`COH-1`–`COH-6`); probes `builder/analysis/2026-07-30-coherence-tag-probe/`.

**The kill gate fired: step 2 never ran.** Descriptive scope only — no criterion, no
adoption, no weight or currency change, and neither open owner decision in `NEXT.md` is
settled by any of it.

## What the next session must not revert

- **`ct_retrodict.py` is committed, pre-registered, and UNEXECUTED — that is the
  outcome, not an omission.** Running it against the 11 verdicts later is a *second
  attempt* and must be reported as one. The verdicts remain an unconsumed falsifier.
- **The kill was decisive and vocabulary-robust** (`COH-2`, `COH-6`). Do not soften it
  to "coverage was borderline"; do not re-gate on the `COH-3` population after the
  fact — that argument belongs to a future pre-registration designed cold.
- **`COH-3` cuts against the kill's severity and must travel with it** — the same
  pairing discipline as `FPC-2`/`FPC-9`: band coverage killed the probe while the
  delivered-route spot check was twice as covered. Either alone misleads.
- **`COH-5` retires the 21-hour cost assumption** for MB tag collection (LB transport,
  ~29×, 99.9% fidelity). Older cost notes (fame-proxy README, §7's "1 req/s / bulk
  dump" framing) describe the constraint as it was — true then, superseded as a cost
  claim now.

## Already updated — do not re-edit

`NEXT.md`, `docs/README.md` (rows for the findings, log, and this handoff), the
previous handoff's role line, `TEST-QUEUE.md` (N/A entry), and the probe directory
README (outcome note).

## What I know that is not otherwise in the durable record

- **The LB metadata endpoint accepted 50-MBID batches without complaint**; no
  documented cap was found, and larger batches were not probed. If someone needs the
  full graph fast, 50 works today at ~26 artists/s.
- **The single fidelity miss** (1 of 872 genre sets) was an upper-half artist; it
  looked like sync lag, not filtering, and was not chased.
- **The one-day scope had no casualties**: nothing was cut from step 1 to fit the day;
  step 2's non-run was the gate, not the clock.
