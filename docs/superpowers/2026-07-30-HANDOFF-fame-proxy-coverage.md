# Handoff — fame-proxy coverage probes, 2026-07-30

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-30-HANDOFF-track-b-runs.md`](2026-07-30-HANDOFF-track-b-runs.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a seam handoff, not mid-flight.** The work was scoped, executed to its last
probe, and read. Nothing is in flight, no subagent is running, **no listener on 8000 or
5173 and no Python process survives this session** (swept, both empty). The tree is clean.

## What happened

A discussion about data sources, similarity, fame and coherence produced one measurable
question, and it was measured. Branch `fame-proxy-coverage`, **PR #53**. Record:
[`2026-07-30-fame-proxy-coverage-execution-log.md`](2026-07-30-fame-proxy-coverage-execution-log.md);
findings [`findings/2026-07-30-fame-proxy-coverage.md`](findings/2026-07-30-fame-proxy-coverage.md)
(`FPC-1`–`FPC-11`); probes `builder/analysis/2026-07-30-fame-proxy-coverage/`.

**Descriptive scope probes only. Nothing adopted, no criterion fixed, no currency changed,
no shipped code touched. Track B is untouched.**

## What the next session must not revert

- **The Wikipedia fame floor is NOT actively corrupting fame-currency measurements**, and
  §0 of the findings document leads with that correction. It was the premise the work
  started from and the measurement refuted it. **No Track 2 or Track 3 verdict changes.**
  Do not restore any wording implying past fame-scored results are suspect.
- **Three pre-committed predictions were REFUTED and are recorded as refuted** (`FPC-2`
  floor reach falls rather than rises with depth; `FPC-1` resolution failure is 5.6% not a
  large share; `FPC-5` multilingual adds 7.1/6.8 points against a <5-point prediction). A
  well-meaning editor tidying these into confirmations would destroy the point.
- **`FPC-2` and `FPC-9` must travel together.** Quoting either alone gives the wrong
  answer: the ruler is adequate for what the router does today (`FPC-2`), and blind on
  38.7% of what it would deliver on the most obscure route the graph admits (`FPC-9`).
- **`CNS-2` is confirmed and quantified, not superseded.** `FPC-10` did not discover the
  misidentification class; the 2026-07-26 census did, including its direction.
- **`FPC-9`/`FPC-10`/`FPC-11` were allocated after `FPC-8`**, and `FPC-9` is *placed*
  between `FPC-2` and `FPC-3` because it tests `FPC-2`. Forward-only, nothing renumbered.
  **Cite by identifier, never assume numeric order is chronological.**

## Already updated — do not re-edit

`NEXT.md`, `docs/README.md` (one new row), the previous handoff's role line,
`TEST-QUEUE.md` (N/A entry), and the findings document's two doc-auditor fixes.

## What I know that is not otherwise in the durable record

- **The two raw collector outputs are gitignored and regenerable**, not lost:
  `fp_wikidata.json` (~35 min) and `fp_listenbrainz.json` (~3 min). Every derived summary
  **is** committed. Commands are in the directory README.
- **`fp_fame_mbid --build` has never been run.** It would produce full-graph fame values
  (~33k pageview requests, ~3–4 h). Deliberately deferred — the `--validate` path answered
  the decision-relevant question far more cheaply. It is resumable.
- **42 artists returned null from ListenBrainz** and 24 MBIDs were refused as ambiguous by
  `fp_fix_duplicates`. Both are small, both are recorded in the JSON, neither was chased.
- **The doc-auditor was run and its two actionable findings were fixed in place** (the
  `CNS-2` citation, and a conditionality warning at `FPC-2`). Two remaining are recorded
  as deferrals rather than fixed: the `PRODUCT-REQUIREMENTS.md` Definitions question, and
  the pre-existing `DAF-C2` `P1`–`P4` identifier collision, **which is not this work's and
  is still open from the 2026-07-27 audit**.
- **The owner's framing was right and mine was wrong**, on a point that matters for how
  this is picked up: the case for the ListenBrainz table is **coverage**, not bias. On bias
  it adds nothing — it shares Wikipedia's population blind spot, measured at ~10× on one
  pair. Anyone arguing it is a better *fame* source is arguing something this record does
  not support.

## The open decisions, and what I would do

**Both are the owner's and neither is settled. What follows is a position, not a menu.**

- **A — does the instrument work happen, and before or after the graph work?** I would do
  it **before**. `FPC-9` is the reason: the criteria that would judge a successful
  obscurity push are the ones that go blind during it, so the instrument is upstream of the
  graph and router work rather than a follow-up. It is also cheap relative to a rebuild.
- **B — does a currency change re-read prior results?** I would **leave them standing**.
  `FPC-1` and `FPC-2` say nothing currently needs re-reading, and that is the cheap and
  honest default — but it must be fixed *in advance* of any recompute, not after seeing one.

**Separately, and needing neither decision: MBID keying is right regardless.** It removes a
silent-error class rather than improving a number. `fp_fame_mbid.py` is the working
implementation.

## The largest thing NOT done

**The coherence thread — execution log §7.** Two halves, both the owner's trigger, neither
proposed: that the past failure of coherence metrics was *misdiagnosed* (both failed
metrics were topological, auditing the graph they came from), and that the cost function
assumes coherence is **additive along edges** while the requirement's second clause is not.
It is the most substantial open idea this session produced and it is recorded there in
full so it survives the conversation.
