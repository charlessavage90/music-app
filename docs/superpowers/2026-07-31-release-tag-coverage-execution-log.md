# Release-tag coverage probe — retained execution log

**Role: RETAINED EXECUTION LOG.** Records decisions and reasoning, not narration — git has
what each step did and the code has how. **Owns no figures**: every number lives in
[`findings/2026-07-31-release-tag-coverage.md`](findings/2026-07-31-release-tag-coverage.md)
and is cited by criterion, never restated here.

Governing document:
[`specs/2026-07-31-release-tag-coverage-preregistration.md`](specs/2026-07-31-release-tag-coverage-preregistration.md).

---

## §1 How the work was scoped, and what that changed

**Commissioned by the owner 2026-07-31** as a read-only parallel investigation while the
`TAS-` session was parked. The `TAS-` execution log §12.2 carries four constraints from that
session; the owner asked that they be **validated rather than adopted as written**. All four
survived validation, and one turned out sharper than written:

- **The unlabelled-only sample (item a)** was right, and it has a consequence the constraint
  did not name: banding it `COH-2`'s way leaves the **top two bands empty by construction** —
  0 unlabelled artists in the top 0.1% and 1 in the top 1%. Only three bands carry a
  population, and the headline can only ever be a lower-half figure. Better fixed in the
  design than discovered in the table.
- **The validity problem (item b)** was real, and the constraint's remedy — decide which
  release types count in advance — is necessary but weak: it prevents a known failure without
  measuring whether the labels are any good. **`REL-3` is the addition**: run the identical
  aggregation over artists whose labels we already have, hold those out, and score against
  them. No human in the loop, population of 40,437.
- **The Discogs mapping (item c)** was right and became the *whole* Discogs arm — see §3.
- **A fourth ceiling neither party had named:** aggregation needs releases to aggregate.
  Measured before designing anything, because it could have killed the idea for the cost of
  one run.

**Deliberately not done: a plan.** The project's `cheapest-experiment-first` memory says that
on a question ending in a number, the cheapest decisive experiment comes *before* a plan. The
endpoint-shape probes and the release-existence ceiling both ran first, and the ceiling
reshaped the design.

## §2 Cheap experiments first, and one of them was decisive

Five endpoint-shape probes ran before any design existed. Two changed it:

- **ListenBrainz's batched endpoint does not carry release tags.** `inc=release_group`
  returns release-group *identity* with no tag field. `COH-5`'s 29× transport does not extend
  here, and the correction in `TAS-` §12.2 item 3 — that `COH-5` is a claim about a transport,
  not about what data exists — is confirmed from the other side.
- **LB's `rels` block carries no Discogs link** (0/50). MusicBrainz's own `url-rels` does.

The **release-existence ceiling** then ran as a census over all unlabelled artists, ~8 minutes
via the batched endpoint. **It cleared, and my first reading of it was wrong** — I compared a
ceiling measured over *unlabelled* artists against a bar defined over *all* artists, which
made 55.0% look like it sat exactly on a stop threshold when there were 21 points of headroom.
Corrected in the same message it was reported in. The lesson is the project's own recurring
one: **check which population a figure is denominated in before comparing it to anything.**

## §3 The design decision that mattered most: measure the two sources separately

Discogs `<genres>` is **100% filled** — a schema constraint, not volunteer effort; a release
cannot be submitted without one. That makes the two arms structurally different questions:

- **MusicBrainz** — genuinely open. Did anyone bother to tag the album?
- **Discogs** — not a tagging question at all. It collapses entirely to `REL-2`'s two
  ceilings: can we find the artist, and do they have releases listed.

So `REL-2` is not a caveat on the Discogs figures; it **is** the Discogs arm. The findings
record shows the arithmetic closing to the decimal, which is the strongest confirmation the
design got.

**Vocabularies are measured separately and never merged.** Discogs `genre` is a closed
15-value list and `style` a ~600-value one; MusicBrainz is a folksonomy. Merging genre into
any agreement statistic would inflate it — nearly every guitar band agrees on "Rock". `F4`
and `F5` stay separate columns, and neither enters the frozen `TAS-` vocabulary.

## §4 Decided against

Recorded because negative decisions leave no artifact and get re-derived otherwise.

- **Name-based Discogs matching — rejected, not deferred.** It is the population-mismatch
  trap that killed every external popularity source. Unnecessary once MusicBrainz's `url-rels`
  proved to carry the ID.
- **The MusicBrainz `release` dump (345 GB) — out of scope.** Release-level tags measured far
  sparser than release-*group* tags, inverting a claim I had made from a single worked example.
  Tagging attaches to the album concept, not the pressing. Kept as a §7 lever with a
  **single firing condition** (`REL-1` in 45.0–49.9%); the file has since been deleted.
- **A minimum support of ≥ 2 releases — rejected.** The median unlabelled lower-half artist
  has 2 release groups, so a ≥ 2 threshold would have discarded most of the target population
  by construction and measured prolificacy rather than tagging. Support counts are emitted
  instead, so the fragility stays visible.
- **Redefining `F0` from the artist dump — rejected, and it is §1's held-constant row.** The
  MusicBrainz artist dump carries artist-level tags for every artist. Using them would have
  silently moved "unlabelled" and every coverage figure with it, for a reason unrelated to
  aggregation. This is the dormant-term hazard in its data form.
- **Running a second pre-registration-free probe** after the ceiling run. Tempting (a
  300-artist tag-rate spot check, five minutes) and declined: doing it once is defensible
  because a ceiling can only kill, never license; doing it twice is how a habit starts.

## §5 Defects found in the design, by the design

**Both instrument checks earned their place, and `REL-C1` went red.**

- **`REL-AM1`** — `REL-7` compared MusicBrainz genres against `F0` (LB ∪ Wikidata P136).
  Those differ by an entire source, so its "drift" figure was P136's contribution. It matters
  because `REL-C1`'s tolerance *is* that figure: left alone, the liveness check would have
  admitted a pipeline mislabelling one artist in nine — it could not have gone red, which is
  the only property an instrument check has. **Written before any criterion had a number.**
- **`REL-AM2`** — `REL-C1` carried the same conflation *and* was a weak check anyway: fixing
  only the comparand would have made it duplicate `REL-7` and exercise **no code**. It now
  runs the real aggregation path and requires **set equality**, not a count match — a pipeline
  labelling the right number of artists with the wrong labels must fail. **Written after
  `REL-1`'s passing figure was known**, which is a weaker disclosure position and is stated as
  such at the amendment's head.

**The generalisable lesson:** a check that reproduces another measurement is a second copy of
a number, not a check. Ask what *code* it exercises.

**`REL-C2` behaved exactly as pre-registered, including the part that looks wrong.** Its
shuffled coverage came back *higher* than the real figure. §4 predicted that in advance and
barred it from being read as evidence about `REL-1`: shuffling ownership relocates coverage
rather than destroying it. Had this not been written down first, a session would have had to
decide after the fact whether an odd number was a bug — and `TAS-AM3` is this project's worked
example of that going wrong.

**One pre-registered bar turned out worthless and is reported as such:** `REL-3`'s "≥ 3× the
null" is satisfied by a division by zero, the null median being exactly 0.000. The criterion
is carried entirely by its zero-overlap half. Recorded rather than quietly dropped, because a
bar that cannot discriminate is a design defect worth carrying forward into the next
pre-registration.

## §6 Harness failures, none bearing on a figure

- **The Discogs collector was killed by the OS** after accumulating ~5M per-release records
  (729 MB free of 33 GB). Nothing downstream needed that granularity — `REL-C2`'s shuffle
  operates on release *groups*, never on Discogs releases — so it now folds each release into
  the artist's running union. Pure cost, removed.
- **A comment described a substring pre-filter that was never implemented.** Corrected to
  explain why every line *is* parsed: a textual "is this ours" test would match an MBID
  appearing inside a relation to a *different* artist and would silently keep the wrong rows.
  This is the project's named failure class — confident prose about correct code — caught in
  its own harness.
- **`iterparse` cleared each `<release>` but left the emptied shells attached to the root**,
  so the tree would still have grown without bound. Found by inspection before the run, not
  after it.

## §7 Operational measurements

Whole investigation is **offline and re-runnable from local files**: no API, no rate limits,
no sampling. Pass costs and file sizes are recorded in the analysis directory's README; the
three dumps total ~97 GB and under an hour of single-threaded compute for a full census of
74,193 artists.

**Provenance for the gitignored inputs (`closeout` D3).** These cannot be committed and a
future session cannot otherwise tell which snapshot a conclusion was drawn from:

| Input | Identity |
|---|---|
| Adopted artifact | `graph-t15-tiebreakfix.bin`, sha256 asserted on every load via `cb_metrics.ADOPTED_SHA`; the run aborts on mismatch |
| MB artist dump | `mbdump/artist`, 17,239,240,131 bytes |
| MB release-group dump | `mbdump/release-group`, 17,993,321,216 bytes; `TIMESTAMP` 2026-07-29 13:42:34 UTC, `SCHEMA_SEQUENCE` 31, `REPLICATION_SEQUENCE` 187816 |
| Discogs releases | `discogs_20260601_releases.xml`, 61,590,487,061 bytes, 19,192,301 `<release>` elements |
| `F0` label frame | `tas_tags_raw.json` + `tas_wikidata_raw.json`, untracked working-tree files collected live 2026-07-30 |

The MB `release` dump (345,409,291,647 bytes) was measured, ruled out of scope, and deleted
with its tar. Its identity is recorded here so the exclusion can be audited rather than
retaken on trust.

The MusicBrainz `release` dump was downloaded (345 GB), measured, ruled out of scope, and
deleted along with its tar. Disk peaked near capacity and was reported at the time.

## §8 Standing context layer (`closeout` D6)

**Unchanged by this work.** No `CLAUDE.md` edit, no new skill or agent, no memory file
added or modified. Deltas: unconditional **0**, conditional **0**. The one correction made to
the shared record was in `docs/README.md`, which is not part of either layer.
