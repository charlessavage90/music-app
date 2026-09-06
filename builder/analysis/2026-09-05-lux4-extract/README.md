# `LUX-4` extraction — Spotify/Apple ids and structured artist facts, 2026-09-05

**Role: FIGURES OWNER for `LUX-E3` and for the `LUX-4` payload coverage. ACTIVE.**
**Cited elsewhere, never restated.** Produced by `L4-T2` of
[`plans/2026-09-05-lux-4-links-and-info-card.md`](../../../docs/superpowers/plans/2026-09-05-lux-4-links-and-info-card.md).

Reproduce with `lux4_extract.py` — read-only, offline, no network, minutes over the 17 GB
MusicBrainz dump. Run it with `python -u`; buffered output makes a live job look dead.

## 1. Why this is a new script, and the coverage defect that forced it

The plan said to modify `../2026-08-02-dsp-ids/dsp_ids.py` and reuse the population it already
builds. **Both halves are wrong.**

That script scans the union of `graph-t15-tiebreakfix.bin` and `graph-algb-full.bin` — the
artifacts adopted and under test on **2026-08-02**. The served map `graph-msw-tu50.bin` was
built four days later from a **later** ALG-B crawl:

| set | artists |
|---|---|
| served map (`graph-msw-tu50.bin`) | 58,838 |
| the 2026-08-02 union | 93,067 |
| **served artists in NEITHER** | **2,687 (4.6%)** |
| population used here (all three unioned) | 95,754 |

`dsp_ids.py`'s docstring claims its ALG-B build is *"a superset of anything a final ALG-B build
produces"*. **That is true for a build from the 2026-07-30 archive and false across the crawl
extension that followed.** Reusing it would have shipped links and facts missing for 4.6% of
every journey, with nothing going red.

Its outputs are also **pinned**: `deezer_ids.py` ships a map whose sha that script reproduces,
so re-running it over a different population breaks the shipped map's reproduction claim. So it
is left untouched and this directory owns the `LUX-4` payloads.

**Population here is the union of all three artifacts**, each sha-verified before it is read. A
superset is safe by construction — an MBID absent from a given build is a no-op — and it keeps
a future build of either lineage covered. 95,719 of the 95,754 were found in the dump.

## 2. `LUX-E3` — Spotify id coverage, and how it compares to Apple

**Plain sentence, from the spec:** *how many artists have a Spotify link recorded in
MusicBrainz, and is it better or worse than Apple's?*

**Threshold: descriptive — none.** It decides whether the feature is "both services" or "Apple
plus search", and nothing else.

Coverage over the **served map**, by popularity percentile band. (`pop_pctl` here is a rank
computed in the script; `pop_raw` in the artifact is a value and never a rank.)

| band | artists | spotify | apple | spotify % | apple % |
|---|---|---|---|---|---|
| top 1% | 589 | 581 | 554 | **98.6%** | 94.1% |
| 90–99% | 5,295 | 4,955 | 4,382 | **93.6%** | 82.8% |
| 50–90% | 23,535 | 17,661 | 13,546 | **75.0%** | 57.6% |
| 10–50% | 23,535 | 14,155 | 9,406 | **60.1%** | 40.0% |
| bottom 10% | 5,884 | 3,290 | 2,034 | **55.9%** | 34.6% |
| **SERVED** | **58,838** | **40,642** | **29,922** | **69.1%** | **50.9%** |

**Read: Spotify is better than Apple in every band, and the gap widens as artists get more
obscure** — 4.5 points apart in the top 1%, 21.3 points apart in the bottom 10%. Both are
comfortably above zero everywhere, so the feature is **"both services"**, with a search-URL
fallback wherever an id is missing (spec §4.1's option A).

Across the whole extraction population: 52,421 Spotify ids and 35,888 Apple ids.

## 3. Fact coverage, per field — informative for `L4-D3`, and NOT a `LUX-E2` read

89,090 artists in the population carry at least one fact; **57,204 of the 58,838 served
artists do (97.2%)**. Per field, over the served map and over its lower half by popularity
percentile:

| field | all served | % | lower half | % |
|---|---|---|---|---|
| `type` | 56,795 | 96.5% | 27,828 | 94.6% |
| `country` | 52,167 | 88.7% | 24,511 | 83.3% |
| `area` | 52,173 | 88.7% | 24,513 | 83.3% |
| `begin` | 37,496 | 63.7% | 15,582 | **53.0%** |
| `end` / `ended` | 37,631 | 64.0% | 15,662 | 53.2% |
| **any fact at all** | **57,204** | **97.2%** | **28,122** | **95.6%** |

**⚠ This does NOT discharge `LUX-E2`, and must not be cited as if it did.** `LUX-E2`'s
threshold — *any field below 50% in the lower half needs a designed empty state* — is stated
over **delivered cards on a sample**, not over the raw population. `LUX-E2` remains BLOCKED on
its damaged `TAS-` sample.

What this *does* support, labelled as inference rather than measurement: **every field clears
50% in the population's lower half**, the lowest being `begin` at 53.0%. Routing skews famous,
so delivered interiors should carry *better* coverage than the population — which makes this a
conservative floor rather than an optimistic one. On that basis `L4-D3` ("render only what is
present, no placeholder rows") is not obviously wrong, and the artifact carries the data either
way, so a designed empty state stays a frontend change and never another rebuild.

## 3a. Three data defects the extraction rejects, and why none is visible to a shape test

**Found by inspecting the extracted values, not by the plan's tests.** The plan's check was
*an id contains no `http` and no `/`* — **every one of these passes that** and is still wrong.
All three guards run **during** extraction rather than as a post-pass over the payload, because
the maps keep the FIRST value per artist: a rejected relation must not consume the slot and
block a later valid one.

| defect | scale before the guard | what would have shipped |
|---|---|---|
| **Apple ids in two shapes** — MusicBrainz records the same artist as `music.apple.com/…/657515` and `itunes.apple.com/…/id657515` | **20,777** bare-numeric vs **15,140** `id`-prefixed | one frontend URL template correct for only 58% of Apple links |
| **Album and playlist URLs on artist records** — a Spotify *album* id is also 22-char base62, so id shape cannot tell them apart | 27 album + 2 playlist URLs per 200,000 dump records (vs 80,549 artist ones) | a card deep-linking to an album instead of the artist |
| **Dates with no year** — MusicBrainz partial dates may omit the year: `????-06-05` | **404 artists** | literally `????-06-05` rendered on a card |

Guards, in the order they run: `is_artist_url` (entity kind from the URL path, since both
services put it there), `normalise_id` (Apple → bare numeric, Spotify → 22-char base62 or
reject), `clean_date` (no 4-digit year → treated as absent, and a life span with no usable date
produces no `end`/`ended` pair either).

**Rejected in the final run: 167 Spotify and 47 Apple relations.** The shipped maps now satisfy
*every* Apple id is bare numeric, *every* Spotify id is 22-char base62, and no date lacks a
year — asserted over the whole map in `tests/test_dsp_links.py`, not over a sample. A sample of
50 could not have seen a 42%-of-the-map shape split.

**Process note, recorded because it is the reusable part:** all three were found in one pass
over the *value distributions* after the first extraction, but each was fixed in its own re-run
— three passes over a 17 GB dump where one would have done. **Survey the distribution of an
extracted field before trusting it, and do it once, before the first consumer is written.**

## 4. ⚠ A LIVE DEFECT, found here and deliberately NOT fixed by `LUX-4`

**The shipped Deezer id map was extracted over that same short population, so all 2,687 served
artists outside it carry no Deezer id — zero of them** — against **55.2%** coverage across the
served map as a whole.

Consequence: for those 4.6% of artists the API cannot take its identity-first path
(`clips.py` `_search`: *"Identity before name"*) and falls back to **name search**, which is
precisely the `BYP-13` exposure — a card playing a different artist of the same name — that the
id path exists to close.

**Why it is not fixed here.** Refreshing the Deezer map changes the artifact's **existing**
`deezer_ids` key, which would break `L4-T7`'s control arm — the arm whose entire job is to
prove `LUX-4` touches nothing that already existed. It is a **metadata-only** fix, so it does
not need a listening test or acceptance gates, but it does need its own rebuild and its own
control. **It is a session's to do, not a decision to put to the owner** — the fix is obvious,
the sequencing is methodology, and the only part that ever reaches him is the deploy, which is
hands rather than a judgement. *(Corrected 2026-09-06: this read "the owner's call, and its own
track", which is the flag-instead-of-a-state failure the condition below exists to close.)*

**Deferred, with a success condition — not merely flagged.** *Condition: the first rebuild
after `LUX-4` merges.* At that point the control arm has served its purpose and a changed
`deezer_ids` key costs nothing. The work is: re-run an extraction with `deezer` added to
`KEPT_PLATFORMS` over this same three-artifact population, ship it as dated package data
beside `deezer_artist_ids_20260802.json`, rebuild, and take the new checksum to a deploy.
Roughly 40 minutes plus a deploy; **no listening test and no acceptance risk**, because it
changes metadata and not one node, edge or score.

**Sized, so the deferral is not open-ended.** Of the 2,687, **1,616 (60.1%) carry a Spotify or
Apple id** — against a map-wide 69.1% / 50.9%, so they skew obscure. Inference rather than
measurement: DSP presence on one service is not a direct predictor of a Deezer relation, but it
indicates a real released artist with a footprint. **Expect to recover on the order of 1,300 to
1,600, not 2,687**; the remaining ~1,071 likely have nothing to link to anywhere and stay on
name search whatever is done.

Related but distinct, and recorded separately at
[`../2026-09-05-lux-e1-drift-source/README.md`](../2026-09-05-lux-e1-drift-source/README.md) §6:
`ULC-F4`, where the un-listenable rule's keep-check measures the **name** route while the app
resolves by **identity** first. Three findings now point at the same seam between what was
extracted and what is served.

## 5. Identity

| payload | entries | sha256 over sorted items |
|---|---|---|
| `spotify_ids` | 52,421 | `e618b286ae93d6b5…` |
| `apple_ids` | 35,888 | `e33f67d22485c181…` |
| `artist_facts` | 89,090 | `f55d3369986db8b4…` |

Substrates, each verified by sha before reading: `graph-msw-tu50.bin` (`43dd82bb…`),
`graph-algb-full.bin` (`d008a2b5…`), `graph-t15-tiebreakfix.bin` (`4cb84ef9…`). Dump: the
2026-07-28 MusicBrainz JSON artist export.

**The payloads are written compactly and the script pins those separators**, so `lux4_extract.py`
reproduces the committed bytes exactly. A payload whose generator no longer reproduces it is not
frozen data.
