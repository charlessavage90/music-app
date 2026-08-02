# Execution log — drop-list wiring, harness repair, candidate census, 2026-08-02

**Role: RETAINED EXECUTION LOG.** Records decisions and their reasoning. **Owns no
figures** — the census and clip figures live in
`builder/analysis/2026-08-02-candidate-tail-census/ctc_census.json`,
`ctc_clips.json` and `ctc_droplist.json`; today's list stays in
`builder/analysis/2026-08-01-label-weighting/tail_droplist.json`. Cited, never restated.

Three pieces of work, one session, in this order: the adopted drop rule was wired into
the builder (PR #62), the pipeline/mirror divergence that wiring opened was closed
(PR #63), and the candidate (`ALG-B`) population was censused and its own drop list
frozen (this branch).

---

## §1 The ordering decision, and a disagreement with the handoff that governed

The 2026-08-01 handoff closed with an explicit instruction: **do not wire the list into
the builder before the cap re-evaluation resolves**, on the grounds that the cap track
"may reshape the build, and a drop rule landing first would make its attributions
ambiguous — the same reasoning that keeps the tag-based degree limiter separate."

**That reasoning was examined and judged not to transfer, and the owner ruled to wire
first.** The tag-based degree limiter is ruled separate because it would be a *second
varying device inside one experiment* — two knobs turned, no attribution. The drop is not
a knob the cap experiment turns: it is adopted, and applies identically to every arm
including the baseline. A constant applied to all arms is what a control is. The confound
the handoff feared arises only if the drop lands *mid-experiment*, with some arms built
before it and some after.

**One half of its concern was real and is carried forward.** Track B — the cap track's
measured input — ran on the pre-drop population. A pre-registration comparing new
post-drop arms against Track B's committed figures would be a cross-substrate comparison.
The fix is a design constraint on that pre-registration (name Track B as input-only, build
a fresh baseline arm), not a different order.

**Recorded because it reverses a committed instruction**: a successor reading the
2026-08-01 handoff will find advice that was deliberately not followed. It was not
overlooked.

## §2 Why the drop is a config flag rather than an unconditional step

`filter_special_purpose` is a flag; the nameless drop is unconditional. The drop rule
resembles the second — adopted, not optional — so the default is on and the flag is never
a shipping choice.

It exists for two reasons, and **both were used within the same session**, which is the
argument for it:

1. A build-side experiment can name it in a factor table and hold it explicitly constant,
   rather than comparing across a silent substrate change.
2. Frozen probes that call `build_from_archive` can be **era-pinned** to reproduce their
   own committed figures. Without the flag that would have been impossible, and two
   probes would have silently disagreed with their own record.

## §3 A cheap screen that was vacuous by construction — caught before it entered the record

A screen was proposed and run: *are the artists today's connection rule cuts off the same
artists the cleanup deletes?* If they overlapped, the challenger rule's main advantage
would evaporate post-cleanup and the ranking could flip.

It returned **zero overlap in all three cells** — and the zero is guaranteed, not measured.
The tail census ran over the *adopted* graph, which is already built with today's
connection rule, so only artists that survived that rule were ever census candidates.
Artists the rule cut off could not appear on the drop list. The answer was fixed before the
question was asked.

**Same shape as `TAS-6`'s routing half**: a number that reads as a clean pass but is a
division by something that was always empty. The run did independently reproduce Track B's
committed exclusion figures, so the measurement method was sound and the population was
not.

**The real question — does the cleanup change which connection rule wins — remains open**,
and needs rebuilds rather than set arithmetic. It was deliberately not run: see §6.

## §4 The pipeline/mirror divergence

Wiring the drop added a stage to `build_from_archive`. Its copies under `builder/analysis/`
did not gain it, **and nothing failed**, which is the hazard.

Two classes, treated oppositely:

- **Mirrors** (`cb_build_variants.py`, `replay.py`, `reciprocity.py`) reimplement the stage
  order to inject a different cap step. **Deliberately not updated** — a mirror's value is
  reproducing its committed cells byte for byte, and a cleaned build would not. Track B's
  harness now carries the divergence at its head.
- **Callers** (`grt_score.py`, `calibrate.py`) invoke the pipeline directly, so the new
  default silently changed what they build. **Era-pinned** to `drop_no_release_tail=False`.

**Track B's identity gate could not catch this, and the reason is worth keeping.** It pins
`_assemble` against the shas *it produced in July*. That proves faithful **reproduction**;
it says nothing about **fidelity to a live build**. The gate's own docstring claimed it
"proves the mirror is faithful", which was true when written and is the sentence that made
the divergence invisible. Corrected in place.

The durable guard is `builder/tests/test_pipeline_mirrors.py`: it fails when
`BuilderConfig` gains a field and names every mirror and pinned caller. **Its limit is
stated in the test** — it catches a build rule arriving as a config knob, which is the
usual shape and was this one; a stage added with no knob still needs a human.

## §5 Owner ruling: the drop rule is not re-validated on the candidate population

Raised as a possible second twenty-artist hand sample, on the grounds that a third of the
candidate population is unseen artists and the rule was validated only against today's.

**Ruled against, 2026-08-02, and the reasoning is durable rather than circumstantial.** The
rule does not rest on which artists are in the graph. It rests on three claims that hold
for any population: release-less artists are generally poor recommendations to surface; the
reason not to drop all of them is that MusicBrainz is incomplete rather than that they are
good — **both keepers in the owner's 20 were real artists MB had failed to document**; and
the DSP-link-plus-clip check is the best false-positive catcher available.

**The decisive point closed it:** a measured false-positive rate would change nothing,
because no second refinement mechanism exists. The follow-up question — *and then what?* —
has no answer, so the measurement is cost without consequence. This is the project's own
review filter applied to a measurement, and the session had failed to apply it.

Recorded in `NEXT.md` as a struck row so a successor does not re-propose it.

**Distinct and deliberately kept separate: the *magnitude* question.** A far larger
candidate tail would be a different-sized intervention, not merely a noisier one. That is
what the census measured, and it did not fire.

## §6 Corrections to this session's own claims

Four, all made and corrected within the session:

- **"The router declines those edges, so re-pricing is the cheap first move."** Wrong twice
  over. Router tuning on today's graph was already closed by Track 3b — even with obscure
  interiors toll-free the router shortens rather than substitutes. And the reserved
  famous→obscure edges exist only in Track B's *rebuilt quota cells*, not in the map the
  app serves, so pricing them cannot be rebuild-free. Withdrawn.
- **"The four-minute pass."** That figure covered the artist dump alone. The full local
  census is three passes; timings are in the census log.
- **"The candidate population is 68,467."** That was one cell. The census population is the
  union of all twelve built `ALG-B` cells, each manifest-verified.
- **"The clip stage is ~5.4 hours."** The script's own printed estimate assumed the clip
  stage runs on the whole tail. It does not: the rule cuts an artist with no commercial
  link without any lookup, verified against `tail_clips.py:162` rather than assumed.

## §7 The candidate census

Figures in `ctc_census.json`, `ctc_clips.json`, `ctc_droplist.json`.

**Population** is the union of the twelve built `ALG-B` cells rather than one cell, because
the connection rule is undecided and a capped cell would under-cover whatever wins. A
superset is safe: MBIDs absent from a given build are no-ops.

**Reuse over recomputation.** The `REL-` probe had already censused today's population, and
it covers a large majority of the candidate's. Only the remainder needed fresh dump passes.
Re-scanning the covered artists would have risked two readers disagreeing about the same
artists.

**The clip pass imports `name_path`, `id_path` and the pauses from `tail_clips.py`**, which
imports `same_artist` from the app. Two resolvers would be two chances for the candidate
list and today's to disagree for reasons unrelated to the artists. The ID path is the
instrument check on the name path, so the run measures **this population's own `BYP-13`
rate** rather than inheriting today's.

**Zero service refusals**, so no "we do not know" bucket and every denominator is clean.

**The output is a 2026-08-02 snapshot** and carries the same constraint as the first list:
never re-resolved at build time, because `build_from_archive` is offline by a hard rule and
spec §9 requires byte-identical builds.

## §8 Operational

- Local dump passes: MB artist ~2.0–2.2 min (16 GB), MB release-group ~2.2 min (17 GB),
  Discogs releases ~20.7 min (57 GB). All offline.
- Clip pass: 491 lookups, checkpoint every 25, no refusals.
- `PYTHONIOENCODING=utf-8` is required throughout — the tail is full of CJK names.
- Both graph dumps and the Discogs dumps are on disk under `builder/scratch/`; nothing was
  downloaded.

## §9 Checks

- **Default flip (A4):** `drop_no_release_tail` defaults **on**. The knob is the shipped
  behaviour, not a dormant switch.
- **Fixtures (D2):** both committed 500-node fixtures contain **zero** MBIDs from either
  drop list, so neither needs regenerating and no fixture-dependent assertion moves.
- **Vacuous-test check (B3):** the drop list was truncated to empty and three tests went
  red, then green on revert. An earlier truncation to ten left the behavioural tests green
  because the retained MBIDs included the one under test — worth noting, since it is
  exactly how a weak break produces false confidence. `test_pipeline_mirrors.py` was
  likewise shown red by adding a config field.
- **Snyk:** clean over `builder/src`. Over all of `builder/`, 31 findings, all
  pre-existing and none in any file this work touched. **One is unrecorded** — see
  `NEXT.md`.
