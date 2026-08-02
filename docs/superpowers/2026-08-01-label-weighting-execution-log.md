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

---

## §8 The no-release tail, from open question to adopted drop rule

**A later session the same day, 2026-08-01, owner-directed.** It began as the `NEXT.md`
question this probe's `tail_sample.py` had opened and **ended in an adopted decision**.
Appended here rather than in a new document because the tail sample is this directory's,
outside the `WGT-` pre-registration by its §8, and the thread is continuous.

**Nothing in the `WGT-` record moved.** No `WGT-` criterion, bar, weighting scheme, frame
or figure changed; `wgt_grid.json` and the `WGT-` findings are untouched.

### §8.1 The scope check fired, and it reframed the question

The owner's 20 verdicts were a **population** fact — 18 of 20 not journey-worthy — and
nobody had asked whether the app ever *delivers* such an artist. That question was
answerable in minutes from data already on disk, and it decides what kind of problem this
is: a live defect, or a prerequisite for the obscurity push. `tail_exposure.py` answered
it. Figures in `tail_exposure.json`; the finding is that delivery is real but rare and
rises steeply with endpoint obscurity, and **zero across 800 famous-to-famous journeys**
(reported as a rule-of-three bound, never as "never").

### §8.2 This session drew a wrong conclusion, and the owner refuted it

**Recorded prominently because the refutation is the most valuable thing in this section.**

The session found real musicians among the delivered artists — Sara Quin, Reed Mullin,
Mike Kerr, Jason Evigan, Gabriela Robin — verified them against their graph neighbourhoods,
and concluded a "has a release" filter would cut real artists and was **the wrong
instrument**.

**The owner refuted it on the product's own terms:** the app recommends things to *listen
to*, so the unit is a body of work, not a person. Sara Quin as an entity has ~1 solo track;
the catalogue belongs to Tegan and Sara. Cutting her is correct. **Every name on the
counter-example list was the same shape** — a performer catalogued apart from the band that
holds the releases — so the class collapsed entirely rather than shrinking.

The residual false-positive class is much narrower and his own verdicts had already named
it: artists with genuine releases that MusicBrainz does not document. That is **source
coverage**, not a flaw in the signal. Recorded in `tail_exposure.py`'s docstring beside the
delivered-artist list, because that list is committed and will tempt the next reader into
the same error.

### §8.3 What the counts changed, including one nobody asked for

`tail_signals.py`, one pass over the 17.2 GiB MB artist dump. Every count reported for the
tail **and** the rest of the graph, because a bare tail figure is uninterpretable — the
tail is thinner on every field by construction, since an artist nobody curated has thin
everything.

**The sharpest discriminator was not a link count but MusicBrainz artist *type*:** the tail
is overwhelmingly individual people and untyped entries rather than bands. That is the
owner's credits-not-acts thesis holding across all 7,686 instead of across 20, arrived at
independently of the release signal. Figures in `tail_signals.json`.

### §8.4 The instrument check found a live product defect

`tail_clips.py` ran two paths per artist: the app's own name-based resolver, and — where
MusicBrainz supplies a Deezer artist ID — a direct lookup with no name matching. Their
disagreement is a **measured `BYP-13` rate**: the app's resolver lands on a different
artist of the same name at a material rate. `BYP-13` was a known live exception; it is now
measured rather than suspected, and it is **independent of the tail decision entirely**.

The rate carries error in both directions and `tail_clips.json` says so rather than picking
the flattering one: some mismatches are Deezer *duplicates* of one artist (inflating it),
while the comparable subset is artists MusicBrainz curated well enough to carry a link
(deflating it relative to the uncurated tail). Two further findings cut against the DSP
link alone — about half of MB-linked Deezer artists have no playable top track at all, and
the app's name path *misses* artists whose exact page does have audio.

**Refusals were bucketed separately and excluded from every denominator** (`G3-A4`: a 429
means "we do not know", never "nothing plays"). The run completed with zero refusals, so no
figure is depressed by throttling.

### §8.5 The decision, and the constraint that shapes its implementation

**The owner adopted the rule and the population: 7,035 of 7,686 dropped, 651 kept.**
Frozen at `tail_droplist.json` with a sha over the sorted MBIDs.

**The list must be frozen rather than recomputed per build, and that is a constraint rather
than a preference.** Spec §9 requires byte-identical output for identical input, and
`build_from_archive` is offline by a hard rule with a replay test that injects a raising
fetcher to prove it. A drop rule calling Deezer during a build would make two builds of one
archive disagree. So the network half is resolved once and committed — which makes the list
a **snapshot**, and a rebuild later applies this date's answer.

Two consequences measured rather than assumed: the drop additionally strands **127**
artists on the built graph (a lower bound — a real build re-selects), and because the drop
lands *before* the mass computation in `pipeline.py`, every surviving artist's popularity
marginal moves. **The rebuild is a different graph, not the old one minus rows.**

**The builder was deliberately not modified.** No build is pending, wiring owes tests, and
the cap re-evaluation track may reshape the build. The condition lives in `NEXT.md` marked
as adopted-not-open, so a successor applies the rule rather than re-litigating it.

### §8.6 A requirements clarification, and the drift it corrects

The owner clarified that **obscurity is a proxy for novelty-to-the-user and the requirement
is a gradient with bypass depth, not an absolute floor** — "deliver the bottom 10% of the
graph" was never it. Recorded as `REQ-42`.

**Checking before writing it changed what was written.** `PRODUCT-REQUIREMENTS.md` already
said this: `REQ-13` is a **Must** that bypasses increase delivered novelty, `REQ-35` and
`REQ-37` are trend statements, and the Definitions section already separates novelty from
obscurity-as-proxy. **The requirements were right; the operationalisation drifted** — the
`DD-F1` structural-conflict note makes the problem concrete as "zero edges below the top
popularity decile", and that decile hardened into the goal itself downstream. `REQ-42`
exists to be citable against that, and the note is annotated in place.

It names two affected instances, one of them **this session's own Task 8 wording**, which
called the `TAS-` routing guard's zero bottom-decile result the sharpest corroboration of
the defect. Under `REQ-42` that overstates it. The `DD-F1` defect ruling is unaffected and
the annotation says so: a gradient of zero fails `REQ-13` without reference to any band.

### §8.7 Closeout outcomes

- **A4 default-flip: inapplicable, and said rather than skipped.** No config knob was
  added. `ApiConfig` and `BuilderConfig` are untouched; the drop list is data, and wiring it
  is future work with its own condition.
- **A5:** no listener on 8000/5173/4173/3000. This session started no server and left none
  running; the queued item needs none.
- **B2:** all four new modules have zero inbound imports and are **not orphans** — each is a
  command-line entry point with `main()` and a `__main__` guard, the shape of `tas_signal`,
  `tail_sample` and `wgt_grid`. Asked rather than assumed.
- **B3:** the directory has no pytest tests by design; its instrument checks are the tests.
  **Their red capacity was demonstrated, not asserted:** a wrong artifact sha and a
  population disagreeing with `TAIL-SAMPLE.md`'s committed 7,686 were each injected and
  each aborted the run.
- **D3:** adopted artifact `4cb84ef9…`, verified in-run by every script. Drop-list sha256
  over sorted MBIDs `d876c7ba…`. No artifact was built, adopted or modified.
- **D4:** builder 129, api 217, frontend 107 across 18 files, analysis 106. All pass.
- **D6:** unconditional **44,183 characters**, conditional **2,154 lines** — **delta zero on
  both, verified from the diff**: `git diff main..HEAD -- CLAUDE.md .claude/` is empty and
  every `memory/*.md` predates this session. `REQ-42`, four probe modules and two log
  sections all live in conditional `docs/` and `builder/analysis/`.
- **Snyk:** 6 Low findings in this directory, all the accepted CLI-path class and all
  pre-existing. **The four new modules contribute none** — none takes a command-line
  argument, so no input reaches a path. The `NEXT.md` count is unchanged at 6, itself
  corrected from a stale 4 earlier in this session.
