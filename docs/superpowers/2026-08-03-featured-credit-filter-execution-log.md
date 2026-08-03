# Execution log — the featured-credit filter track (2026-08-03)

**Role: ACTIVE — the retained execution log for this track.** Appended per task, not at
closeout. Branch: `featured-credit-filter`. Session: `featured-credit-filter-builder`.

**Governing inputs, all pre-existing:** the owner's ordering ruling and track description
in [`NEXT.md`](NEXT.md) (top block, 2026-08-02 night), and the fame-instrument execution
log [§5/§5a](2026-08-02-fame-instrument-execution-log.md) — the class mechanism, the two
worked instances (田島賢 `7e4f57b3`, TJ Brown), and the FAM-6 no-page rows. The rule shape
is **ruled, not open**: a keep-check extending the adopted no-release drop rule
(commercial-DSP presence + something plays), never a purge. What this track designs is the
**detector** and produces the frozen lists and wiring; whether the class gets its own
small calibration hand-review is **the owner's spend, flagged not decided**.

## §1 — Orientation and setup (2026-08-03)

- Session-start ritual run by the owner; seam handoff, clean tree, no concurrent session.
- One stale line found and fixed in `NEXT.md`: PR #66 is merged (`f9f42ce`), so the
  "owed decision" line is discharged. Landed as this branch's first commit per the
  document's own fresher-record rule.
- Verified before building on the record: `drop_no_release_tail` /
  `NoDropListForAlgorithm` resolve in `pipeline.py`, `no_release_drop.py`, `config.py`,
  with the twelve-test file and the mirrors guard — `NEXT.md`'s "the wiring machinery all
  exists" claim is true.
- Exploration (two subagents, reports retained in session): the cheap detector is a
  ~2.4 min pass over the 18 GB **release-group** dump using `rel_common`'s existing
  credit-split machinery (`rel_rg_dump.collect()` idiom), not the 48.7 min release-dump
  pass. `rel_rg_raw.json`'s `"a"` flag is NOT the clean split — it folds in
  compilation/live/broadcast type exclusions — so the census re-derives sole-credit as
  `rg_artist_id(record) == mbid` alone.

## §2 — Census design decisions (2026-08-03, before the run)

`fcf_census.py`, no CLI path args (the Snyk-clean shape), run before the rule document
exists — the census is detector design input; the freeze point is before any **clip**
result exists, mirroring how the adopted rule's census preceded its decision.

1. **The sole-credit split is re-derived clean, not read off `rel_rg_raw.json`.** That
   file's `"a"` flag folds in the REL- type exclusions (compilation, live, broadcast…),
   so an artist whose only sole credits are live albums would read as featured-credit
   while being a real act. Sole here is `rg_artist_id(record) == mbid` alone.
2. **Three counters per artist — `total`, `sole`, `first`** (first-listed on a
   multi-artist credit: "A feat. B" puts A first). `first` exists so the rule document
   can decide whether first-listed-only artists belong in the class with the data
   visible, rather than re-running the pass.
3. **Class candidates = ≥ 1 credit, zero sole**, computed over the **union** of both
   censused populations (adopted artifact sha-verified via `cb_metrics`; ALG-B union via
   `ctc_census.candidate_population`, manifest-verified), so one artist-dump pass covers
   both — the same union reasoning as the Deezer id map.
4. **Disjointness instrument check**: the class must not intersect either shipped
   no-release drop list (those artists have *zero* RG credits). Non-empty intersection
   aborts the run.
5. **Discogs is a recorded column, not yet a predicate input**: members' discogs ids are
   joined against `rel_discogs_raw.json`; ids that file has never censused are counted
   separately so the cost of resolving them (the 57 GB XML pass, ~21 min) is priced
   before deciding whether Discogs presence counts as primary existence.
6. **Worked-instance check is part of the run**: 田島賢 (`7e4f57b3…`) and TJ Brown
   (`f62c24cd…`) must come out in-class, with their full counter rows printed. A detector
   that misses either is wrong regardless of what else it finds.

## §3 — Census results, and two findings that shape the rule (2026-08-03)

Figures: `builder/analysis/2026-08-03-featured-credit-filter/fcf_census.json` — cited,
never restated. Run took 4.3 min; the disjointness check against both shipped drop lists
came back clean, and **both worked instances are detected in-class** (both all-shared
credits, neither ever first-listed).

**Finding 1 — the worked keeper case fails the mechanical keep-check.** TJ Brown carries
**no DSP link in MusicBrainz** (`dsp=[]`): his Spotify page exists (8,274 monthly
listeners, §5a) but MB never recorded it — he took a four-link chain to find, which is
§5a's detection-effort caveat measured again, now inside the keep-check's first clause.
So the adopted rule's check, applied verbatim, drops the artist `NEXT.md` names as the
worked keeper. This does not change the rule shape (the owner accepted exactly this
false-positive class for the adopted rule: DSP-link-plus-clip is "the best
false-positive catcher available", and no second refinement mechanism exists) — but it
is the concrete case for the **calibration hand-review he flagged as his spend**, and it
goes to him named, not buried.

**Finding 2 — Discogs presence is the predicate-deciding column.** 2,558 of the adopted
class's 3,961 members have a *known* Discogs release-level artist credit; treating that
as primary existence (the faithful mirror of the adopted rule's dual-source release
signal) roughly halves the class. 2,167 ids across the union are uncensused by the REL-
raw — **including both worked instances** — so `fcf_discogs.py` (57 GB XML pass, ~21 min)
resolves them before the rule document freezes the predicate. Error direction of the
Discogs signal: exemption, never an extra drop.

Also recorded for the rule document: the class is overwhelmingly `Person` (77%), the
share the adopted-population tail never approached; ~28% are first-listed on at least
one multi-artist credit; the clip stage prices at ~1.5 h for 2,711 DSP-linked members
across the union.

## §3a — Owner observation, recorded as design input (2026-08-03)

From his manual fame hand-checks the night before: **MusicBrainz data for less-popular
artists is often missing and sometimes incorrect — including wrong DSP links (a wrong
Spotify link observed by hand).** Bearing on the keep-check's error model, worked out
with him in conversation:

- **Missing links under-fire the DSP-presence clause → false drops.** TJ Brown is the
  measured instance (§3 finding 1). This is the check's real exposure in this class,
  and the concrete case for the calibration hand-review he has flagged as his spend.
- **Wrong links over-fire the DSP-presence clause → false keeps, partially caught.**
  The clip clause resolves by name search plus the app's `same_artist` rule, never by
  following the recorded link, so a wrong link produces a keep only when a same-named
  artist also has playable clips — the BYP-13 collision shape, the same inherited-link-
  accuracy property the Deezer id path's deferral row records.
- **Deliberately not changed in response:** the check is not widened to search-only
  evidence, because name-search-only keeps are exactly where wrong-artist collisions
  live — the reason the adopted rule kept the DSP clause.

## §4 — The Discogs resolution fixes the predicate (2026-08-03)

Figures: `fcf_discogs.json` — cited, never restated. The 57 GB pass resolved every
class-member Discogs id the REL- census had never seen, and it was decisive both ways:

- A substantial majority of the class carries a Discogs main-artist release — exempting
  them roughly **thirds** the class — so the clause is load-bearing, not decorative.
- **Both worked instances have no Discogs release**, so both remain in the class under
  the exemption. The drop-shaped instance is not exempted by the clause that shrinks the
  class, which is the outcome that had to hold for the predicate to be usable.

**Predicate fixed accordingly** (the faithful mirror of the adopted rule's dual-source
release signal): in the class iff ≥ 1 MB release-group credit, none sole, and no Discogs
main-artist release. Rationale, plain-language sentences, mechanics, refusal handling,
and the pre-fixed worked-instance outcomes — including TJ Brown as a **named-in-advance
false positive** — are owned by the rule document, committed before any clip lookup:
[`specs/2026-08-03-featured-credit-filter-rule.md`](specs/2026-08-03-featured-credit-filter-rule.md)
(`FCF-`). Snyk on the probe directory: clean (0 findings; no CLI path args, the
predicted shape).

## §5 — Keep-check run, freeze, and wiring (2026-08-03)

Figures: `fcf_clips.json`, `fcf_droplist.json`, `fcf_droplist_algb.json` — cited, never
restated. The keep-check ran to completion with **zero refusals** (FCF-3 satisfied on the
first pass), and `fcf_droplist.py` applied the committed rule with **both FCF-5
worked-instance checks passing** — 田島賢 and TJ Brown drop exactly as the rule document
fixed in advance, the latter as the named false positive.

**One instrument read worth carrying: the BYP-13 wrong-artist rate inside this class is
the highest yet measured** (`fcf_clips.json` `byp13_wrong_artist`; the two prior
measurements are in the 2026-08-01 and 2026-08-02 captures). Consistent with what the
class *is* — people named like other people, discoverable mainly by name collision. It
strengthens the drop rule's premise and is recorded here as corroboration, not acted on.

**Wiring, mirroring `no_release_drop.py` end to end:** `featured_credit_drop.py`
(per-population sha-pinned package data, refusal for uncensused algorithms),
`drop_featured_credit: bool = True` beside the earlier flag with the same factor-table
rationale, the pipeline block **before the mass computation**, era-pins extended in
`grt_score.py` / `calibrate.py` (both flags now pinned off), `RECORDED_FIELDS` updated
with the per-mirror decision recorded in place, and the analysis README's era section
extended. The old suite's uncensused-builds test needed both flags off — updated with a
comment saying why; that interaction was the only cross-suite change.

**Verification: 164 builder tests pass; mutation-tested rather than merely green.**
Deleting the pipeline stage turns **6** tests red; reinstating one-list behaviour turns
**5** red including both leak canaries. No mutation residue (grep-checked). Snyk: clean
on `src/artistpath_builder`, `tests/`, and the probe directory.

**Standing decision preserved:** nothing here is adopted. The branch merging is the
adoption act, and the presentation to the owner names it.

## §6 — Owner spot checks challenge the Discogs exemption; the split is measured (2026-08-03)

At the presentation the owner asked how Discogs releases were checked, because his spot
checks found exempted-looking artists whose Discogs record is "credited on" / "one song
on a collaboration album." The precise answer, from the code rather than the intent:
presence in a release-level `<artists>` block — which does exclude track-level credits
and the extra-credits block, but carries **no sole-credit requirement**, an asymmetry
with the MB half of the class predicate (sole release-group credit). A collaboration
album crediting several artists at album level exempts all of them. Error direction is
exemption-only (a ghost escapes; nothing is extra-dropped), but its **size was never
measured**, and under-cleaning bears directly on this track's purpose.

`fcf_discogs_split.py` (owner-prompted, run immediately): one more Discogs pass
splitting every exempted member into *sole-credit* (≥ 1 release credited to them alone,
not Various) vs *shared-credit-only*. **If the predicate is amended on this evidence,
that is an explicit `FCF-` amendment with post-result disclosure, never a quiet edit** —
the amendment would rest on the owner's spot checks and this split, not on the
keep-check results the freeze protects against.

**Result (figures: `fcf_discogs_split.json` — cited, never restated): the owner's spot
checks were representative, not unlucky draws.** A majority of the exemptions are
shared-credit-only, at nearly the same share in both populations. The frozen lists
therefore **under-clean**: an artist whose whole Discogs main-credit existence is joint
albums is currently exempted without ever reaching the keep-check. The amendment
decision — whether the Discogs clause requires a sole credit, restoring symmetry with
the MB half of the predicate — is **the owner's**, because it moves ~2,000 artists from
"exempt" into exposure to the keep-check's known false-drop residual (§3a). Presented
with options; nothing amended yet, PR #67 stands as-committed while he decides.

## §7 — FCF-AM1 executed end to end (2026-08-03)

**The owner ruled "amend."** Sequence, with the freeze discipline preserved: the
amendment text (`FCF-AM1`, full post-result disclosure) was committed **before** the
incremental keep-check ran; the increment resolved with **zero refusals**;
`fcf_droplist_am1.py` re-applied the amended rule whole, **asserting the superset
claim** — no pre-amendment drop or keep flipped — and both FCF-5 worked-instance checks
passed again. Figures: `fcf_clips_am1.json`, `fcf_droplist_am1.json`,
`fcf_droplist_algb_am1.json`.

The package data now carries the `_am1` lists under new dated filenames with new pinned
shas (adopted `0f337de2…`, candidate `b8d230e6…`, 945 MBIDs shared); the pre-amendment
freezes remain in the probe directory as the record. Test constants and the
production-only leak canary were re-derived (the old canary had entered the amended
candidate list, which is the superset property working as designed). **164 builder
tests pass** against the amended lists.

**Snyk on the probe directory: one Medium, and it is the third instance of an already
owner-accepted finding** — the insecure-XML-parser rule (CWE-611) on
`fcf_discogs_split.py`'s `iterparse`, identical to `rel_discogs.py:87` and
`ctc_census.py:173`, both investigated empirically 2026-08-02 (XXE not reachable on
this interpreter; entity-expansion reachable in principle but the input is a local
57 GB dump read by an offline probe). The fix (`defusedxml`) was deliberately declined
there; adding it here alone would make the three instances inconsistent for no
exposure change. Recorded for the NEXT.md deferral row at closeout rather than fixed.
`src/` and `tests/` remain clean.

## §8 — Closeout (2026-08-03)

**The owner ruled ADOPTION, 2026-08-03, without the calibration hand-review** — the
flagged decision is discharged as DECLINED, with the amendment's enlarged no-lookup drop
population in front of him. Merging PR #67 is the enactment. He also ruled closeout runs
*before* the merge so its documentation updates ride the PR — which is this section.

**Gate outcomes, complete:** FCF-3 zero refusals, both captures, first pass each. FCF-5
passed twice (first freeze and re-freeze). The `FCF-AM1` superset assertion passed on
both populations. Mutation checks: stage deletion 6 red, one-list behaviour 5 red. No
gate failed; none was worked around.

**Closeout check outcomes:**
- **A4 (default-flip):** `drop_featured_credit` defaults **on** — the new behaviour
  ships with the merge; no knob left at old behaviour. The filter is inert until a
  rebuild, which is the track's designed relationship to the cap re-evaluation, not
  unshipped work.
- **A5 (processes):** all four ports checked, no listeners; every background task this
  session started ran to completion. Nothing left running.
- **B1:** lint run — 2 hard failures, both the new documents unclassified in
  `docs/README.md`, fixed at this closeout. `doc-auditor` (diff-scoped) reported two
  HIGHs. **One real and fixed:** the fame-instrument handoff's `docs/README.md` row
  still claimed CURRENT after its own role line was updated — the exact defect class
  this map's history warns about, caught by the audit as designed. **One adjudicated
  FALSE with evidence:** "田島賢 missing from both droplists violating FCF-5" — the
  audit checked the *adopted*-population files for an artist the census records as
  **candidate-population-only** (`in_adopted=false`, `fcf_census.json` worked-instance
  block); verified at adjudication that he is in `drop_mbids` of both candidate lists
  including the shipped package file, and in neither adopted list, which is exactly
  what FCF-5 plus the per-population freeze require. The audit's cold-start navigation
  test passed all six questions; identifier census clean, no `FCF-` collisions.
- **B2 (reachability):** `featured_credit_drop.py` is imported by `pipeline.py` and the
  test file; every probe script is reachable from the probe README. No orphans.
- **B3 (vacuous tests):** discharged by the two mutation runs above, which are exactly
  this check performed deliberately.
- **B5:** `.claude/` greps clean — nothing there describes the pipeline's drop stages
  or restates a figure this work moved. `docs/` references to the class all live in
  documents this track owns or in `NEXT.md`, rewritten at this closeout.
- **D2 (fixtures):** not applicable — no graph artifact changed; the committed 500-node
  test fixtures are inputs, not outputs, of this work.
- **D3 (provenance):** the frozen lists are committed as package data with shas pinned
  three ways (module constants, in-file keys, tests); no uncommittable artifact was
  produced.
- **Kill check:** nothing killed; the one closed path is the hand-review, closed by
  owner ruling rather than unreachability.

**Operational measurements with no other home:** release-group dump pass 2.2 min at
~130 MB/s; Discogs XML pass 20.6 min (presence) and 19.5 min (split); the clip-stage
pricing figure (~45 min / 1,400) held within minutes across both captures.

**D6 standing-layer measurement:** unconditional **44,494 chars**, conditional **2,155
lines** — both deltas exactly **zero** against the fame-instrument closeout's recorded
figures (its §10 table, including the owner-approved +249 orient-table pointer). This
track changed neither `CLAUDE.md`, nor `.claude/`, nor `memory/`.

**D4 suite outcomes, run at this closeout:** builder 164 passed, api 230 passed,
frontend 107 passed (18 files).
