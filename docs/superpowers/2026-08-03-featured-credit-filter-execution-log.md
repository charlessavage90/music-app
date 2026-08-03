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
