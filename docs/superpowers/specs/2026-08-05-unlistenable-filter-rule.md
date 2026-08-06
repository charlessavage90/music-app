# The un-listenable filter rule (`ULF-`)

**Role: ACTIVE — the governing rule document for the filter fix (the `ULC-` track's
successor work).** Committed **before any census or clip lookup under this rule exists** —
the `ULC-` census (`ulc_census.json`) is detector-design input and precedes this document;
no keep-check has run for any artist this rule newly evaluates, and every mechanical
outcome below is fixed here so no result can reshape it. Identifier series `ULF-`,
collision-checked across all refs 2026-08-05 (silent).

**What this document does and does not do.** It fixes the rule, its detector, its
mechanics, its relation to the two adopted drop rules, and the read of every outcome. It
**adopts nothing**: no shipped build changes until the owner's already-ruled ordering
(write-up → filters → map switch) reaches its next step, and nothing here reopens the
`GBL-` null or takes a position on which package sounds better (`ULC-B2` travels).

**Owner inputs this document consumes** (all pre-existing or ruled before this text was
written, none created by a result):

- the remit (`NEXT.md` top block, 2026-08-05 evening; `2026-08-05-HANDOFF-ulc.md` "Owed"):
  the filter fix plus `ULC-F1` and `ULC-F2`, then re-censusing both drop lists;
- **the cut-line ruling (2026-08-05, this session): `ULC-D2` as ruled, unchanged.** Keith
  Scott is thereby a **named residual false negative** — he escapes the class on a single
  1993 television-theme release and stays on the map; the owner declined a stricter bar
  with the costs in front of him;
- `ULC-AM3`'s definition of `ULC-D2` and its two executor decisions (track count is the
  maximum across a release group's releases; an unknown track count is not substantial),
  inherited verbatim;
- the `ULC-` results note §1.4 — the two exemption mechanisms this rule closes, and the
  demonstration that requiring a *sole* Discogs credit would still not catch Joey Kramer.

---

## ULF-1 — The class (the detector)

**Plain sentence: an artist is in the class when they have never put out anything of
their own that is more than a single track.**

Predicate, per artist, verbatim from `ULC-AM3` (`ULC-D2`): the artist is the sole
credited artist on **no** MusicBrainz release group that is **both**

- (a) `primary-type` ∈ {Album, EP, Single} with no secondary types, **and**
- (b) carries at least one release whose total track count across all media is **≥ 2**,
  where a release group's track count is the **maximum** across its releases, and a
  release group with no release in the dump has an **unknown** count, which is **not**
  substantial (the keep-check, not the detector, is what softens that reading —
  `ULC-AM3`'s named tension is resolved the same way here as there).

**There is no Discogs clause, and its absence is the fix, not an omission.** Both adopted
rules let a Discogs credit exempt an artist, and the `ULC-` results §1.4 shows both
mechanisms passing the class through: any-credit Discogs guarded the emptiest class (four
of the six known cases), and even a sole-credit requirement admits a drum sample library
(Joey Kramer). A genuinely listenable artist MusicBrainz under-documents is rescued by
the keep-check — which is evidence something *plays*, not evidence a credit *exists* —
and that is the only exemption an availability rule can trust.

## ULF-2 — The rule

**Plain sentence: inside the class, an artist is kept only if MusicBrainz records a page
for them on a commercial streaming service AND the app's own clip search actually plays
something by an artist of that name; everyone else in the class is dropped from the next
map build.**

Mechanics, verbatim from the adopted rules with the class as the population: keep iff a
commercial-DSP link exists in the MB artist record (`tail_signals.py`'s host set) **and**
the app's own Deezer→iTunes resolution resolves a clip, **imported, never restated**.

**One addition, instrument data only, never a criterion: every keep records whether its
clip resolved via a recorded artist id or by name alone.** The name-only path is the
`BYP-13` exposure, and for this class specifically a false rescue is the failure mode —
a session drummer whose name matches someone playable is exactly who this rule exists to
remove. Fixing the instrument is `ULC-F4`, **deferred by the owner to its own track**;
this field is that track's measurement, collected for free, and no read of it is licensed
here.

## ULF-3 — Relation to the two adopted rules: supersession without reversal

**Plain sentence: everyone the two existing filters drop stays dropped, everyone they
keep stays kept, and this rule only widens the net.**

Both adopted classes are strict subsets of ULF-1's class: a no-release-tail artist has
zero release groups, a featured-credit artist has release-group credits but never a sole
one, and neither therefore has a sole substantial release group. Their frozen keep/drop
verdicts — same keep-check instrument — **carry forward unre-run** (the mixed-snapshot
precedent is the `ALG-B` no-release list, which carries the 2026-08-01 verdicts for its
overlap). Fresh evaluation is owed only to class members neither census ever keep-checked.
**No adopted verdict is reversed by this rule, so nothing adopted is reopened** — the
`FCF-` adoption, its declined calibration hand-review, and the no-release rule's closure
argument all stand untouched.

**Wiring consequence:** one new `BuilderConfig` flag, `drop_unlistenable` (default on,
factor-table control like its siblings). The two existing flags and their frozen lists
**remain functional and unchanged** — era-pinned probes construct configs with them, and
under the subset property applying all three is identical to applying this rule alone.
Their retirement is **deferred, not implied**: success condition, a shipped build has
routed on a `ULF-` list and the era-pinned probes that name the old flags are themselves
retired or re-pinned.

## ULF-4 — Refusals are not evidence

`FCF-3` verbatim: an artist whose lookup the service refused to answer is not dropped on
that refusal; the run is resumable and the lists freeze only when every newly-evaluated
member's outcome is a real answer.

## ULF-5 — Populations, freezing, and the two census obligations

One frozen list per censused population, shipped as sha-pinned package data, selected by
`config.algorithm`, applied in `build_from_archive` before the mass computation, an
uncensused population refusing to build when the flag is on — every property mirrors the
existing modules, and the mirrors-guard and era-pinning obligations of a new
`BuilderConfig` field are part of this track's wiring work.

Two properties are new, and they discharge the `ULC-` deferrals this session owns:

- **`ULC-F1` — population identity.** The census emits a **manifest per population**:
  the archive's full artist set (count and sha256 over the sorted MBIDs, members
  included), shipped beside the list. A build whose archive contains artists outside the
  censused set **refuses to build** exactly as an uncensused algorithm already does —
  discharged when a mismatched population refuses, which is this rule's acceptance test,
  not a hope. The identity is the **archive** artist set, not any built graph's: the
  archive is what a crawl extension grows, and what `build_from_archive` reads.
- **`ULC-F2` — the census writes back what it learns.** Per-artist signals land in a
  coverage store keyed by signal (this rule needs sole-credit, type and track-count
  signals the `REL-`/`CTC-` coverage never collected, so old coverage is only partially
  reusable and the store must say per-signal what it knows). Discharged when a second
  census over an extended population passes the dumps only for genuinely new artists.

## ULF-6 — Worked instances: mechanical outcomes, fixed before any lookup

- **The six availability cases** (Rick Davies, John McVie, Dallas Taylor, Joey Kramer,
  Max Martin, Brad Delson) are **in the class**, census-verified (`ulc_census.json`
  `ULC_V1_capture`, 6 of 6). Their keep-check outcomes are **not** fixed here — each
  turns on a DSP link and a live resolution — and a keep among them is **not** a rule
  failure: it is either a genuine rescue or the `BYP-13` exposure, and the id-verified
  field will say which. **A keep among the six must be reported, never quietly absorbed.**
- **Keith Scott is mechanically outside the class** — the named residual false negative,
  owner-accepted 2026-08-05. A result showing him on a journey must not be presented as
  a surprise, and must not be quietly repaired with a stricter bar this document's
  ruling declined.
- **Nathan East and Billie Joe Armstrong are outside the class** on sole substantial
  release groups of their own — correct behaviour, and the reason a stricter bar was
  declined. **Audrey Riley is outside** on one solo record; she was a `ULC-V2` miss and
  remains one, accepted with the cut-line ruling.

## ULF-7 — Not decided here, and by whom

- **Adoption into a shipped build** — the owner's, inside his already-ruled ordering
  (write-up → filters → map switch). The re-censused lists are what a yes ships;
  producing them decides nothing.
- **`ULC-F4`** (the keep-check's name-resolution defect) — its own track, per the
  owner's deferral. ULF-2's id-verified field feeds it and licenses no read here.
- **Snapshot refresh** — as with every frozen list, a deliberate future act, no
  automatic trigger.
- **Retiring the two superseded flags and lists** — deferred with the success condition
  in ULF-3.
