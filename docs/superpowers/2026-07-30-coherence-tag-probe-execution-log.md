# Execution log — coherence tag probe, 2026-07-30

**Role: ACTIVE record of how the probe ran.** Findings of record:
[`findings/2026-07-30-coherence-tag-probe.md`](findings/2026-07-30-coherence-tag-probe.md)
(`COH-1`–`COH-6`) — figures live there and are cited here, never restated. Probes:
`builder/analysis/2026-07-30-coherence-tag-probe/`. Branch `coherence-tag-probe`.

## §1 What this was, and the discipline that shaped it

A one-day falsification probe of the §7 coherence thread (fame-proxy execution log §7),
owner-directed. Two steps with a kill gate between them: banded tag/genre coverage
first, and only if the tail cleared a committed 50% bar, a pre-registered retrodiction
of one tag-based path score against the 11 blind-listen verdicts (Phase 1 §3.8–§3.9).

Every gate, threshold and prediction was committed before its run. The step 2 scoring
rule was committed **before step 1's numbers existed** — stronger than the gate
required, and deliberate: whatever step 1 said, nothing in the rule could have been
shaped by it.

## §2 Gate outcome: KILLED, and the kill is the result

The gate fired: lower-half union-genre coverage measured 14.7 points under the bar,
outside sampling noise (`COH-2`). **The pre-registered retrodiction (`COH-4`) was never
run; the 11 verdicts remain an unconsumed falsifier.** Running that rule against them
later is a second attempt and must be reported as one.

Predictions: five committed, five confirmed (`COH-1` genre-given-item falls with band;
`COH-2` union beats Wikipedia's tail figure while still failing the gate; `COH-5`'s
fidelity, coverage and speed). The probe's design question — is tag coverage the same
failure mode as Wikipedia's fame floor — answered **yes** at band level, with the
`COH-3` route-level counterpoint recorded beside it rather than buried.

## §3 Decisions taken, with reasoning

- **The instrument was fixed as the genre union (MB genres ∪ P136), not raw tags,
  before any fetch** — vocabulary hygiene over coverage maximisation. The owner's
  post-hoc question then closed the alternative honestly: the widest possible
  vocabulary moves the tail by +3.4 points and the kill stands (`COH-6`).
- **The gate population was the band, not the routable set.** `COH-3` (74.2% on the
  LIMIT interiors) is the recorded argument that a future design might gate on
  delivered population instead — a *future pre-registration's* argument, not a re-read
  of this one.
- **MB sampled rather than dumped** (1 req/s makes the full graph ~21 h); the owner's
  LB-transport suggestion, tested as `COH-5`, retires that constraint for any future
  full-graph build (~47 min).
- **Step 1 ran its two collectors concurrently**; the MB summary printed once against
  a partial P136 file and was disregarded and recomputed from complete data. The gate
  was already frozen, so nothing could be reshaped by the glimpse; recorded for
  honesty.

## §4 Defects and near-misses in my own work

- Two run logs (`ct_mb_sample.log`, `ct_wikidata_genres.log`) were swept into the
  results commit against the template convention (FPC leaves logs untracked). Removed
  from tracking at closeout; the convention is now stated in the directory
  `.gitignore`.
- The first two background launches failed instantly on a stale `cd builder` (the
  shell's cwd already persisted there). Cost: one relaunch; noted because the failure
  mode — a background task dying at line 1 while looking launched — is the
  `python -u` trap's quieter cousin.

## §5 Operational measurements with no other home

- WDQS P136 over the full artifact: ~123 batches of 600, mostly ~1 s per batch,
  ~4 minutes wall clock — far under the fp_wikidata experience (its variability note
  still stands; this run just got a quiet service).
- MB web service: 1,275 artists in ~24 min (~0.9 artists/s including the enforced
  1.1 s pause), zero 404s in the sample.
- LB metadata endpoint: 50-MBID batches accepted without complaint; throughput figure
  is `COH-5`'s.

## §6 Closeout measurements

**D6 — the standing context layer:** unconditional **44,183 characters**, conditional
**2,154 lines** — **both deltas exactly zero** against the fame-proxy closeout's figures.
This work touched neither `CLAUDE.md`, `memory/`, nor any skill or agent file.

**A5 — ports:** 8000 and 5173 both empty at closeout; this session started no listeners
(its network activity was outbound API clients only).

## §7 What was decided against, and why

- **Gating on raw-tag coverage** — tags are a dirtier vocabulary and the instrument
  should not inherit "seen live"-class noise; `COH-6` later showed the choice cost at
  most 3.4 points in the tail.
- **Running `ct_retrodict.py` "just descriptively" after the kill** — that would burn
  the falsifier corpus for nothing; it stays unconsumed.
- **A second gate on the `COH-3` population after seeing it** — exactly what
  pre-commitment forbids; recorded as the weakest link instead.
