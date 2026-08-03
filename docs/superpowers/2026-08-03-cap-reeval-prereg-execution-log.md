# Execution log — the cap re-evaluation pre-registration track, 2026-08-03

**Role: RETAINED EXECUTION LOG.** Owns no figures: the `WAV-` figures live in
`builder/analysis/2026-08-03-within-artist-votes/wav_read.json` (banner summary in that
directory's README); the review measurements live in
`builder/analysis/2026-08-03-cre-prereg-critique/cre-analyst-critique.md`, which owns
what it states; Track B, `FAM-`, `WGT-` figures stay with their owners. The governing
document this track produced is
[`specs/2026-08-03-cap-reevaluation-preregistration.md`](specs/2026-08-03-cap-reevaluation-preregistration.md)
(`CRE-`, frozen at `3d7b7d6`, amended once by `CRE-AM1` at `eec67a8`).

## §1 — What this track was, and the shape of the session

One session, five deliverables, each committed before the next depended on it: the
pre-registration authored cold from the design-inputs address (`c047d06`); two owner-
dispatched pre-run reviews (repo-check and `ml-graph-analyst`), their reports committed;
the revision folding the surviving findings in (`3d7b7d6`, the freeze point); the `WAV-`
within-artist vote read, criteria committed before it ran (`8811510`), result committed
(`c910ddf`); and `CRE-AM1` on the owner's ruling (`eec67a8`). Everything is analysis- and
document-side: no shipped code, no default, no artifact, no blind listen.

## §2 — Authoring decisions (the prereg as first committed)

- **Pricing arms only on changed supply.** The (ALG-E × incumbent × pricing) cell is
  Track 3's closed record and the parked DD-A2 decision; the design-inputs synthesis
  names new-supply × new-pricing as the untested cell. Later refined by the review
  (§3.3's closed-cell rule + the `CRE-D3` instrument carve-out).
- **`TB-P5H-7` consumed** by giving the joint descent × payload outcome its own read
  (`CRE-C4` + `CRE-R3`), rather than by adding a constraint knob.
- **`w_degree_hub` stays 0.0 in every cell as a recorded decision** with the follow-up
  decision named at the winner reads — implementing `NEXT.md`'s corrected row rather
  than designing a control against a confound that cannot occur.
- **`w_floor` disclosed as the design's known uncontrolled variable** (the Track 2
  dormant-term shape), handled by term accounting rather than by changing production
  weights in the anchor. The review later *narrowed* the exposure to the supply knob
  (critique F12a) — the original disclosure over-warned on pricing.
- **Family (a) nearly omitted.** The first draft had no `MK100` cells; the self-review
  spec-coverage pass against the design-inputs families caught it. A factor-table
  column defect (a redundant "tag device" column making `S2` rows read as two-column
  changes) was caught the same pass.

## §3 — The two pre-run reviews, and their disposition

Both dispatched at the owner's instruction, both against the as-first-committed prereg,
both before any arm was built. Reports and probe scripts:
`builder/analysis/2026-08-03-cre-prereg-critique/`. The prereg's **§9** is the
disposition record — every material change traceable to a finding. Not repeated here;
what belongs in this log:

- **The repo-check's HIGH was a real spec defect this session wrote**: §3.2 specified
  per-node trim before symmetrisation, which is the deleted `pre_symmetrise` defect
  (bounds nothing) and would also have broken the `S2` rows' one-column isolation. The
  reviewer found it by reading `cb_build_variants.py`'s docstring — confident prose
  about correct code, in reverse: confident spec prose contradicting committed code.
- **The analyst's highest-value findings were calibration, not correctness**: both
  drafted ramp settings sat in the dominating regime; the drafted hub kill policed a
  direction the device provably moves away from; the drafted payload floor of 0.5
  passed every arm Track 3 flagged; the drafted winner margin sat inside sampling
  noise. All four bars were re-based on measured base rates.
- **Two deliberate divergences from the analyst's exact proposals**, named in §9: the
  payload floor's binding form is baseline-relative (self-normalising, so the proposed
  pre-registered recalibration is unnecessary), and `CRE-C6`'s screen-out threshold is
  arithmetic impossibility of a median pass rather than the proposed ≥ 8 (which would
  screen cells still able to pass on their readable majority).
- **Two review measurements became result-bearing disclosures** (prereg §9): the
  `CRE-D1` direction (opposite to the owner's hypothesis, so the confirmatory run's
  expected branch is "not supported") and the pricing prior (the ramp inert on famous
  pairs at incumbent supply in the adopted currency). Neither invalidates the runs;
  both are disclosed so they cannot later read as predictions.
- **Process note for future review dispatches:** the two-reviewer split (claims-vs-repo
  and quantitative-critique) produced disjoint findings with almost no overlap — ten
  findings from one, twelve from the other, zero duplicates. The split is worth
  reusing.

## §4 — The `WAV-` read: decisions and outcome

The owner asked whether tagging is vote-weighted; the record's answer (rarity-weighted
per the `WGT-` recommendation; absolute vote weighting measured and declined) surfaced
that his within-artist formulation had **never been measured** — `WGT-`'s evidence
scheme is absolute-scale. He ordered the read before `CRE-S2` is built.

- **Criteria committed before the run** (`8811510`), with the consequence mapping
  fixed: three-bar conjunction, one shot, no reweighing after numbers exist.
- **Instrument-first design paid for itself**: the marked copies were pinned to the
  frozen `wgt_grid.py` originals by equivalence checks (committed `W4` cells to 5e-5;
  exact `e(a,l)` table equality) and an all-ones degeneracy red check, all of which
  passed before any reading was taken.
- **Outcome: FAIL on the conjunction** — movement and non-redundancy passed, the fame-
  shape bar failed **in the opposite direction from its hazard** (the weighting leans
  away from fame, largely the mechanical all-ones default on unvoted artists). Read as
  written per the one-shot rule; the direction observation recorded honestly in the
  README banner, explicitly not relitigated.
- **Defect in this session's own bar, recorded**: `WAV-3` had no direction clause and
  measured weight-pattern correlation rather than agreement-level contamination — found
  only after the result existed, which is exactly why the one-shot rule exists and why
  the bar was not patched.

## §5 — The owner's ruling and `CRE-AM1`

The owner ruled the scheme pursued: within-artist vote discrimination is sound for this
format, and the anti-fame direction is acceptable (his column). **Correction to his
recollection, recorded in the amendment**: he believed vote weighting was part of the
previously assessed mechanism; it was not — `WGT-` assessed only the absolute scheme,
so its "no evidence strength" clause was never a verdict on his formulation.

`CRE-AM1` (appended per §8, post-result disclosure at head): `S2`'s ceiling ranking
becomes `evidence_rel`; the `WAV-` record stays closed and un-re-read; the open
attribution question (vote content vs any within-artist weight spread) is gated at the
sweep by a second `CRE-C5` companion — the within-artist vote scramble — with sentence
licensing split between the label-scramble and vote-scramble companions. The `S2` rows'
one-column isolation survives (the knob is still the ceiling's ranking function).

## §6 — Corrections to the prior record made this session

- `WGT-`'s "no evidence strength" recommendation is **scoped**: it governs the
  absolute-scale scheme it measured, not within-artist normalisation (`WAV-` README).
- The fame-ruler shorthand "percentiles over the union snapshot" is **wrong as a build
  instruction** (adopted frame N = 74,151; union supplies raw values, mapped) — it
  mis-built the ruler once inside the critique itself; the prereg §0.3 now carries the
  full definition.
- The featured-credit handoff's "one action owed: merging PR #67" was discharged before
  this session started (`eecc361`); recorded at session-start, now in `NEXT.md`.

## §7 — Operational measurements with no other home

- ALG-E capture regeneration (`td_capture.py`): **451.5 s**, 74,957 nodes, 3,989,754
  directed candidates; sha reproduced the recorded `893609e9…` byte-identically, as the
  `WGT-` handoff first established.
- The `WAV-` read end-to-end (masses + W0 restricted pass + W4 five-measure pass):
  runtime recorded in `wav_read.json` (`runtime_min`); the whole background job
  (capture + read) ran ~48 min wall.
- Snyk: the critique directory scans clean (0); the `WAV-` directory adds **2 Lows**,
  both the accepted CLI-path class — `NEXT.md`'s standing row extended.

## §8 — Closeout record (2026-08-03)

- **A4 — inapplicable, stated not skipped**: no shipped config knob was added; the two
  drop flags were untouched; `CRE-` defaults nothing.
- **A5 — no listeners on 8000/5173/8138/8139**; the one background job this session
  started (capture + `WAV-` read) completed and exited. Nothing left running.
- **B1 — lint: 1 hard failure** (the new prereg unclassified in `docs/README.md`),
  fixed at this closeout. **Auditor outcome: one MEDIUM, and it was this section's own
  first draft** — the B1 entry promised the audit's findings would be "folded into the
  same commit" before the audit had returned, a forward reference to an outcome that
  had not occurred; corrected here to state the outcome instead. Everything else
  verified clean: the supersession chain, the `WAV-` story consistent across its four
  tellings, all three struck deferral rows checked against their sources, cold-start
  navigation, and a full identifier census (no collisions). The auditor's report file
  was folded into this entry and removed rather than left as an unclassified stray;
  this entry is its record.
- **B2 — reachability**: `wav_read.py` is a CLI entry documented in its README; the
  eleven critique probes are frozen as-executed records, deliberately uncollected
  (`testpaths` ruling), documented in their README. No orphaned imports.
- **B3 — inapplicable as tests**: no suite tests were written; the `WAV-` instrument
  checks carried the red-capacity burden (WAV-0d is a genuine failure-capable check and
  the equivalence checks pin the copies).
- **B5 — sweep outcome**: the new documents cite figures to their owners; `.claude/`
  untouched by this work and nothing in it describes the cap re-evaluation.
- **D4 — suites, all green**: builder 164 passed, api 230 passed, frontend 107 passed
  (run at closeout; no shipped code changed this track).
- **D6 — standing layer, delta exactly 0 on both units**: unconditional 44,494 chars,
  conditional 2,155 lines — identical to the featured-credit closeout's figures, as
  expected since nothing auto-loaded was edited.
