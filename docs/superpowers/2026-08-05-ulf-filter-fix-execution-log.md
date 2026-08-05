# Execution log — the un-listenable filter fix (`ULF-`), 2026-08-05

**Role: RETAINED EXECUTION LOG. Owns no figures and no status** — figures live in the
census JSONs this track produces and in `findings/2026-08-05-unlistenable-class-results.md`
(cited by section); status lives in `NEXT.md`. Appended per task, per the handoff-cheapness
rule.

Session: `filter-work-builder (handoff)`, branch `ulc-filter-fix` off the `ULC-` track's
tip (draft PR #78 unmerged at branch time; branching off the tip rather than `main` because
the tip carries the census tooling and `no_release_drop.py` state this work extends, and it
merges cleanly in either order).

Governing document: `specs/2026-08-05-unlistenable-filter-rule.md` (`ULF-`).

---

## §1 — Orientation and the one claim verified before building (session start)

Seam handoff, clean tree, no concurrent session, zero live test-queue items. Verified
before building: `ULC-F1`'s citation resolves — `no_release_drop.py:30-33` does argue "a
build's algorithm is its archive identity", and `crawl.py:115` does rebuild the frontier as
`discovered − done`. Both accurate.

## §2 — Design decisions, with reasoning (pre-spec)

1. **Design before mechanics, reversing the order proposed at session start.** Reading the
   code showed the fix's shape determines the `ULC-F1`/`F2` machinery: with a `ULC-D2`
   entry condition the featured-credit class is a strict subset of the new class, so the
   fix merges both filters into one, which changes how many lists and manifests exist.
   Building `F1` first would have built it twice.
2. **The merge itself** (methodology, mine): one rule, one list per population. Licensed by
   the subset property plus verdict carry-forward — no adopted verdict reverses, so neither
   adoption reopens. The alternative — patching each filter's exemption clause separately —
   leaves two rules whose classes overlap after the patch (a `ULC-D2` artist with a
   featured credit is in both), which is a coherence debt with no offsetting benefit.
3. **The Discogs exemption goes entirely** (methodology, mine): results §1.4's Joey Kramer
   case shows no credit-existence test on Discogs separates listenable from not; the
   keep-check tests that something *plays*, which is the actual question. Genuine
   Discogs-only artists are rescued there, not at the detector.
4. **Keep-check instrument unchanged; id-verification recorded per keep** (methodology,
   mine): fixing the name-resolution path is `ULC-F4`, owner-deferred to its own track.
   Recording which keeps are id-verified collects that track's measurement for free without
   changing any criterion here. The `BYP-13` false-rescue hazard is named in ULF-2 and in
   the weakest-link presentation to the owner rather than silently accepted.
5. **Population identity = the archive artist set, not any built graph's** (methodology,
   mine): the archive is what a crawl extension grows and what `build_from_archive` reads
   (`pipeline.py`, `known = set(payloads)`). The prior censuses used built-graph
   populations, which would false-refuse at build time because pre-prune `known` exceeds
   any post-prune graph population.
6. **The owner ruled the cut line (his column — it decides which real artists leave the
   map, and the residual is a risk acceptance): `ULC-D2` as ruled.** Presented with three
   options and costs (class sizes and clip-stage hours from `ulc_census.json`, cited);
   stricter bars declined with Nathan East / Billie Joe Armstrong / debut-album artists as
   the counter-cases. Keith Scott is thereby the named residual false negative, fixed in
   ULF-6 before any lookup.
7. **Old config flags stay functional** — era-pinned probes under `builder/analysis/`
   construct `BuilderConfig` with them (`cre_build.py`, `calibrate.py`, `grt_score.py`).
   Retirement deferred with a success condition in ULF-3, following the read-only-aliases
   precedent.

## §3 — Decided against, and why

- **A stricter entry bar to catch Keith Scott** — declined by the owner with the trade in
  front of him (a debut-album artist has exactly one sole substantial release group, and
  dropping those on a failed clip lookup removes exactly the artists journeys exist to
  surface).
- **Re-running prior keep-checks under the new census** — would reverse adopted verdicts
  wherever clip availability drifted since the snapshots, reopening both adoptions this
  track has no license to touch. Mixed snapshots have explicit precedent (the `ALG-B`
  no-release list carries 2,712 verdicts from 2026-08-01).
- **A fresh keep-check design for the new class** — is `ULC-F4` by another name;
  owner-deferred.

## §4 — `ULC-F1` machinery (task: population identity)

Built test-first: `unlistenable_drop.py` (loader with the population identity block and
two self-consistency refusals), `drop_unlistenable: bool = True` in `BuilderConfig`, the
pipeline stage after the two sibling drops with the `PopulationNotCensused` refusal
checked against the **pre-drop archive population** (the censused set was recorded over
the raw archive, so a drop-shrunken `known` would mask an extension), and 12 tests in
`test_pipeline_unlistenable_drop.py` — including the two payload-corruption refusals,
because a payload that cannot vouch for its population must not be trusted for a refusal
decision.

**The refusal is new semantics, and 36 existing tests met it.** Every pipeline test
builds synthetic archives with fake MBIDs; the old drops' intersection semantics never
refuse, the manifest check does. Resolution per file, all mechanical: files testing
*other* features pin `drop_unlistenable=False` (the factor-table-control idiom, with a
one-line comment each); `test_cli` — which builds through `main` and has no flag surface,
deliberately — installs a fixture list censusing its two-artist population via a new
shared `conftest.py` fixture.

**The mirrors guard fired as designed and its obligations were discharged:** all three
pipeline mirrors stay deliberately frozen (same recorded reason as both prior drops);
`grt_score.py` and `calibrate.py` gain `drop_unlistenable=False` beside their earlier
pins; and **`cre_build.py` was found to be an unlisted era-pinned caller** — it postdates
the guard's list, builds through defaults, and once ULF- lists exist for its two
algorithms a re-run would have applied the third drop and silently disagreed with the
committed cell shas. Pinned, and added to `ERA_PINNED_CALLERS`. Suite: 176 passed.

## §5 — Census design (tasks: `ULC-F2` + the re-census)

Three scripts in `builder/analysis/2026-08-05-ulf-census/`, and the design decisions
that are not obvious from reading them:

1. **The `ULC-` census's committed output cannot say who was evaluated and found
   negative** — `ulc_flags.json` holds class *members* only, and the universe membership
   was never written. Re-derived here from the same five sha-verified artifacts rather
   than trusted from a count. That gap is itself an instance of `ULC-F2`, and the
   coverage store closes it for the future: absence of a field means unknown, never
   false.
2. **The artist-dump pass runs over the full archive union, not a delta**, because the
   prior censuses read that dump and discarded what they learned (`ctc_census.py`'s
   `artists` dict was never persisted) — there is nothing to reuse. ~2.5 min; the store
   now keeps it.
3. **Verdicts carry per ARTIST, not per population.** Clip resolution is an artist-level
   fact; the 2026-08-02 census already carried 2,712 verdicts across populations this
   way. The two prior classes are globally disjoint on release-group counts, so a
   verdict conflict is structurally impossible — asserted anyway, `SystemExit` on
   violation, because that disjointness is what licenses the merge.
4. **The ULF-3 subset property is asserted against data before anything freezes**, not
   assumed from the argument: every prior-verdict artist present in an archive must be
   in that archive's `ULC-D2` class. Same dumps as every prior census, so containment
   must be exact; a violation would mean a frozen list reverses an adopted verdict.
5. **The ALG-B no-release keeps are not in any packaged payload** (the payload records a
   count, 486, and no list); reconstructed as `tail_mbids − drop_mbids` from the two
   committed census outputs, which is their defining construction.
6. **Population identity is the archive artist set** (75,000 production files counted at
   input verification), not any graph's node set — a graph-population identity would
   false-refuse every build on pre-prune artists.
