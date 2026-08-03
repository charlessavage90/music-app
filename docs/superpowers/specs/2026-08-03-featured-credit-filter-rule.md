# The featured-credit filter rule (`FCF-`)

**Role: ACTIVE — the governing rule document for the featured-credit filter track.**
Committed **before any clip lookup for this class exists** — the census
(`fcf_census.json`, `fcf_discogs.json`) is detector-design input and precedes this
document; the keep-check's network results do not, and every mechanical outcome below is
fixed here so no result can reshape it. Identifier series `FCF-`, namespaced per the
plan-writing conventions; no existing series uses it.

**What this document does and does not do.** It fixes the rule, its detector, its
mechanics, and the read of every outcome — the same standing the adopted no-release drop
rule's census gave its decision. It **adopts nothing**: adoption is the owner's product
decision, taken on the presented result. It extends the adopted rule and must never be
read as re-litigating it.

**Owner inputs this document consumes** (all pre-existing, none created here): the
ordering ruling and rule shape (`NEXT.md` top block, 2026-08-02 night — *"a keep-check
(commercial-DSP presence + something plays), not a purge"*); the class mechanism and both
worked instances (fame-instrument execution log §5/§5a); his MB-inconsistency observation
(this track's execution log §3a).

---

## FCF-1 — The class (the detector)

**Plain sentence: an artist is in the class when MusicBrainz credits them on at least one
release group but never as the sole artist, and Discogs lists no release with them as a
main credited artist.**

Predicate, per artist, fixed from the committed census:

- `total > 0` and `sole == 0` over the MB release-group dump, where sole is
  `rg_artist_id(record) == mbid` **alone** — exactly one credited artist, no type
  exclusions (`fcf_census.py`'s docstring records why `rel_rg_raw.json`'s flag is not
  this);
- **and** no Discogs release whose release-level `<artists>` block carries the artist's
  MB-recorded Discogs id (`fcf_discogs.json`; features and session credits live in
  `<extraartists>` and track blocks, so this is Discogs' own main-credit signal).

The Discogs clause mirrors the adopted rule's dual-source release signal — the adopted
tail required "no MB release group AND no Discogs release"; the class requires "no sole
MB credit AND no Discogs main-artist release". Same two sources, same roles, and the
clause's error direction is **exemption, never an extra drop** — which is also the
mitigation for the owner's measured MB-missing-data concern: a real act MB
under-documents gets a second chance to be exempted by Discogs.

**First-listed multi-artist credits (`first > 0`) do NOT exempt.** "A feat. B" puts A
first, but the census shows both worked instances at `first == 0` and the keep-check —
not the detector — is the instrument this rule trusts to separate real acts from ghosts.
A first-listed ghost exempted at the detector would never reach it.

## FCF-2 — The rule

**Plain sentence: inside the class, an artist is kept only if MusicBrainz records a page
for them on a commercial streaming service AND the app's own clip search actually plays
something by an artist of that name; everyone else in the class is dropped from the next
map build.**

Mechanics, verbatim from the adopted rule with the class as the population:

- keep iff a commercial-DSP link exists in the MB artist record (`tail_signals.py`'s
  host set) **and** `name_path(name)["resolves"]` — the app's own Deezer→iTunes
  resolution order with its own `same_artist` rule, **imported, never restated**
  (`tail_clips.py:98`). The id path is run where an id exists as instrument data only;
  it is not the criterion (`tail_droplist.py:112` semantics).
- Names are what the app would display: read from the sha-verified adopted artifact for
  adopted-population members, from the manifest-verified ALG-B cells for the rest.

## FCF-3 — Refusals are not evidence

**Plain sentence: an artist whose lookup the service refused to answer is not dropped on
that refusal.** A refused lookup is re-run (the script is resumable and keeps its
checkpoint while any refusal remains); the drop lists are frozen only when every class
member's outcome is a real answer. The adopted rule's run completed with zero refusals;
this rule inherits the discipline rather than the luck.

## FCF-4 — Populations, freezing, wiring

One frozen list per censused population (adopted / `ALG-B`), computed from the same
census, shipped as sha-pinned package data beside the no-release lists, selected by
`config.algorithm`, applied in `build_from_archive` **before the mass computation**, with
an uncensused population refusing to build when the flag is on — every property mirrors
`no_release_drop.py`, and the mirrors-guard / era-pinning obligations that come with a
new `BuilderConfig` field are part of this track's wiring work. The lists are dated
snapshots for the same reason the adopted rule's are: `build_from_archive` is offline by
a hard rule and spec §9 requires byte-identical builds.

## FCF-5 — The worked instances: mechanical outcomes, fixed before any lookup

- **田島賢 (`7e4f57b3…`)** — in class (census-verified), `dsp=[]` → **mechanically
  dropped** with no lookup needed. This is the drop-shaped instance behaving as designed.
- **TJ Brown (`f62c24cd…`)** — in class (census-verified), `dsp=[]` → **mechanically
  dropped**, and this is a **known false positive, named in advance**: his Spotify page
  exists (8,274 monthly listeners, §5a) and MusicBrainz never recorded it. The rule
  accepts this residual for the same recorded reasons the adopted rule accepted its own —
  the DSP-link-plus-clip check is the best false-positive catcher available and no second
  refinement mechanism exists — and the residual's *size* is exactly what the owner's
  flagged calibration hand-review would measure. **A result showing TJ Brown dropped must
  not be presented as a surprise, and must not be quietly repaired** (no post-hoc
  keep-list; the adopted rule's closure argument bars inventing a second mechanism here).

## FCF-AM1 — The Discogs clause requires a sole credit (2026-08-03, owner-ruled)

**Post-result disclosure, maximal, per this project's amendment discipline.** This
amendment was written **after** the first keep-check capture and both frozen lists
existed. Its evidence base is **not** those results: it is the owner's spot checks at
the presentation — exempted artists whose Discogs record is "credited on" / "one song
on a collaboration album" — and the split measurement they prompted
(`fcf_discogs_split.json`): a majority of exemptions in both populations rest on
shared album-level credits alone. No clip result influenced it, and no artist dropped
under the original predicate changes status under this one — the amended class is a
strict superset, so the amendment can only *add* drops and keeps, never reverse one.
The owner ruled "amend" with the affected counts and the false-drop trade in front of
him.

**The amended clause: a Discogs exemption requires at least one release credited to
the artist alone** (sole entry in the release-level `<artists>` block, not Various
Artists) — restoring symmetry with the MB half of FCF-1, which always required a sole
credit. Plain sentence: **being one of several named artists on someone's album no
longer counts as having your own releases.**

Everything else stands unchanged: the keep-check (FCF-2) is the instrument that
separates the real collaboration acts this moves into the class from the ghosts, the
refusal rule (FCF-3) applies to the incremental capture, and the FCF-5 worked-instance
outcomes are unaffected (neither instance was exempt under either predicate). The
known cost, named rather than dismissed: the newly evaluated artists with no MB DSP
link are mechanically dropped without a lookup, and that set will contain genuine
duos MusicBrainz under-documents — the §3a false-drop residual applied to a
population on average more real than the original class. The calibration hand-review
(FCF-6) remains the owner's instrument for pricing exactly that, and its case is
strengthened, not weakened, by this amendment.

Mechanics of the incremental run: the amendment adds the shared-credit-only members
(`fcf_discogs_split.json`'s list) to the evaluated class; their keep-check runs as a
separate capture (`fcf_clips_am1.json`) under the same imported resolver; the frozen
lists are re-frozen whole, under new dated filenames and new pinned shas, and the
originals remain in the record as the pre-amendment freeze.

## FCF-6 — Not decided here, and by whom

- **Adoption** — the owner's, on the presented result (four-part format, the TJ Brown
  residual named).
- **The calibration hand-review** — the owner's spend, flagged not decided
  (`NEXT.md`). The census gives it a concrete shape if he wants it: a small hand sample
  of the mechanical drop side, measuring how often "no MB DSP link" means "no page"
  versus "page MB never recorded".
- **Snapshot refresh** — as with every frozen list, a deliberate future act, no
  automatic trigger.
