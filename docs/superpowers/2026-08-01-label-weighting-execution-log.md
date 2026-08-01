# Execution log — the label weighting and evidence probe (`WGT-`), 2026-08-01

**RETAINED EXECUTION LOG. Owns no figures** — those live in
[`findings/2026-08-01-label-weighting-probe.md`](findings/2026-08-01-label-weighting-probe.md),
cited by section. One session: pre-registration written, committed, executed through every
reading, extended twice at the owner's direction, and closed. Branch
`label-weighting-probe`, stacked on `tas-frame-split-and-routing` (PR #58, open at the
time).

## §1 Decisions taken, with reasoning

1. **Weighting schemes are named by words (`plain`/`rarity`/`evidence`), not letter-number
   tokens.** The collision grep found bare `Q1`-style tokens already load-bearing in the
   Gate 2→3 review documents. Words cost nothing and cannot collide with any existing
   series.
2. **Evidence is frame-independent** — `e(a, l)` computed once per (artist, label) over
   all sources; frames only select membership. This is an implementation clarification of
   the evidence table's "(genre or style, per frame)" parenthetical, whose literal reading
   would have made every frame isolation two-knob (membership *and* evidence basis. The
   grid's factor table promises one-knob isolations; this preserves them.)
3. **`EV-G` counts release groups whose genres OR tags carry the label.** The table fixed
   "distinct RGs carrying ℓ" without naming the column; counting `g` only would undercount
   support for labels MusicBrainz has not yet whitelisted. Documented at the definition in
   `wgt_grid.py`.
4. **`WGT-1`'s leak population is labelled artists with a fame value** — matching the
   committed reading B population the 0.37 anchor came from. The pre-registration did not
   pin this; the choice is recorded rather than silent.
5. **The release pass was stopped ~20 min in and restarted from zero** to add the
   descriptive side-collection (record labels, countries, years) after a parallel session
   observed the window would close when the pass finished. Restart, not resume: a
   checkpoint predating the schema would have produced a collection inconsistent across
   the stream, so the checkpoint schema is versioned and the old one voided. Cost: ~20
   elapsed minutes, once, against a second full stream later.
6. **Execution-order deviation, recorded:** §9's order lists the release pass after the
   fifteen cells; it was *started* concurrently with the grid so the owner's manual-review
   hour overlapped the machine time. No `WGT-4` reading was taken before the grid
   completed, which is what the order exists to protect.
7. **The style-filter follow-up ran as a bar-less diagnostic** (`wgt_style_filters.py`)
   rather than an amendment — it changes no committed verdict, tests two rival
   *mechanisms* for one, and reproduces the committed baselines before reading anything.
   Owner-directed; the fold rules were unit-checked against his named cases before the
   run.
8. **The tail sample and its packet sit outside the pre-registration** by its §8:
   descriptive product research, fixed seed in the script header, no criterion. The
   owner's 20 verdicts are recorded beside the draw in `TAIL-SAMPLE.md`, and his
   style-vocabulary calibration read in `STYLE-VOCABULARY.md` — both his words, marked as
   preference records in the `WHAT-GOOD-LOOKS-LIKE` sense.

## §2 Defects found in the design itself, before or during execution

- **`WGT-AM1`** (pre-results, committed before any script existed): §2's gloss of the
  rarity denominator contradicted the committed definition the same sentence pinned to.
  The pin governs; found by reading the committed code before building the harness.
- **The evidence-table parenthetical** (decision 2 above) would have broken the one-knob
  property the factor table promises. Caught at implementation, resolved toward the
  factor table, documented in the module header.
- **The old probe plan's cwd assumption bit three times operationally** — background
  launches with `cd builder` failed or ran from the wrong directory because the shell's
  working directory persists across calls. No science affected; noted because it will
  bite the next session too.

## §3 Gate and check outcomes

All four instrument checks passed, with the reproduction check (`WGT-0b`) passing in both
its forms — committed turnovers at every λ, and bit-identical fields elementwise. `WGT-1`
degraded nothing; the RG ingredient missed the bar by 0.0017 and findings §2 says so
plainly. `WGT-4` fired **Branch 3** of its four-branch rule (findings §4). The
style-filter diagnostic's reproduction guard passed on both baselines before its variants
were read. No gate failed; no bar moved after results existed; no red check was left
unexplained.

**Red-capacity note (B3-adjacent):** the identity checks were never observed red in
production runs. Their capacity to fire was demonstrated separately at closeout — the
`WGT-0b` comparison logic raises on a perturbed committed value, and the nonzero λ > 0
turnovers show the same code path visibly distinguishing weighted from plain fields, which
is what `WGT-0a` would trip on.

## §4 Corrections to the prior record made by this session

- **The 345 GB MB release dump was never deleted.** `NEXT.md`'s closed `REL-` row and the
  frozen `REL-` spec §7 both said it was; it is on disk (322 GiB), and the row now carries
  a dated correction. The frozen spec stays frozen; the closure itself never depended on
  the deletion.
- **"~600 Discogs styles" is 737**, corrected in the findings and the vocabulary table.
- **Mechanistic predictions about label sources are now 0-for-3 in this record** —
  §15.5's two, plus this session's fragmentation hypothesis (findings §3a), which was
  measured dead the same day it was raised.

## §5 Deferrals opened or updated (conditions in `NEXT.md`'s table)

Discogs alias expansion (frame-amendment trigger; artists dump already on disk); the
Discogs **masters** export (irrelevant to presence-based uses; correct substrate iff
Discogs support-counting is ever wanted); the no-release-tail product decision (owner's
trigger; his 20 verdicts are the evidence); the label-affinity / clustering data asset
(side-collection on disk, nothing consumes it); four new accepted Snyk Lows (the standing
CLI-path class).

## §6 Operational measurements with no other home

- Capture regeneration: 471.8 s, byte-identical to the recorded sha (third consecutive
  deterministic regeneration, second cross-session).
- Artist-dump vote pass: 2.3 min at ~131 MB/s. Release pass: 48.7 min at ~117 MB/s,
  1,754,672 single-credit releases kept for 60,422 artists.
- The grid (five frames × five measures in one pass per frame): ~35 min. The style-filter
  diagnostic (nine plain passes): ~25 min.
- Snyk over the probe directory: 4 Low, all the accepted class (`wgt_grid.py` ×2,
  `wgt_release_read.py` ×2).
- Standing context layer (D6): unconditional **44,183 characters**, conditional **2,154
  lines** — both identical to the `TAS-` log §14.2 record; delta zero, verified from the
  diff and the totals.

## §7 Closeout outcomes (SS15)

- **A4**: no config knob was added anywhere — `ApiConfig`/`BuilderConfig` untouched;
  nothing shipped, so nothing to flip. Stated, not skipped.
- **A5**: ports 8000/5173/8138/8139 all empty; no listener existed to disposition; no
  background task survives the session.
- **B2**: no orphans. `wgt_grid` ← `wgt_release_read` and `wgt_style_filters` (imports);
  `wgt_tables` ← `wgt_style_filters`; `wgt_evidence`'s outputs are read by `wgt_grid`;
  `tail_sample.py` is deliberately standalone (owner-facing packet, same standing as the
  frozen probe scripts, which the record already classes as not-orphans).
- **B3**: this work added no pytest tests by design (probe scripts, matching the
  committed-probe precedent); the instrument checks are its tests — red capacity
  demonstrated per §3.
- **B4**: docstrings re-read against code; one cosmetic inaccuracy found and accepted:
  `wgt_evidence.py`'s resumed-pass progress line computes its rate against the post-resume
  clock (overstates MB/s on resume; the completed run never resumed). Prose otherwise
  matches code, including the `EV-G` column decision and the vote-clamp claim.
- **B5**: no shape claims invalidated — the graph, artifact and cost function are
  untouched, so `.claude/` needed no edits; grep found the new figures restated nowhere
  outside their owners (the `docs/README.md` findings row quotes two as hazard warnings,
  the map's established pattern, citing the owning document).
- **D2**: fixtures untouched — no artifact changed.
- **D3**: every conclusion in the findings names its substrate; the capture sha and the
  adopted artifact sha are recorded in `wgt_grid.json` / `tail_sample.json` respectively,
  each verified in-run against the recorded values.
