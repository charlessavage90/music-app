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
| 50–90% | 23,535 | 17,662 | 13,553 | **75.0%** | 57.6% |
| 10–50% | 23,535 | 14,161 | 9,419 | **60.2%** | 40.0% |
| bottom 10% | 5,884 | 3,291 | 2,038 | **55.9%** | 34.6% |
| **SERVED** | **58,838** | **40,650** | **29,946** | **69.1%** | **50.9%** |

**Read: Spotify is better than Apple in every band, and the gap widens as artists get more
obscure** — 4.5 points apart in the top 1%, 21.3 points apart in the bottom 10%. Both are
comfortably above zero everywhere, so the feature is **"both services"**, with a search-URL
fallback wherever an id is missing (spec §4.1's option A).

Across the whole extraction population: 52,431 Spotify ids and 35,919 Apple ids.

## 3. Fact coverage, per field — informative for `L4-D3`, and NOT a `LUX-E2` read

89,090 artists in the population carry at least one fact; **57,204 of the 58,838 served
artists do (97.2%)**. Per field, over the served map and over its lower half by popularity
percentile:

| field | all served | % | lower half | % |
|---|---|---|---|---|
| `type` | 56,795 | 96.5% | 27,828 | 94.6% |
| `country` | 52,167 | 88.7% | 24,511 | 83.3% |
| `area` | 52,173 | 88.7% | 24,513 | 83.3% |
| `begin` | 37,698 | 64.1% | 15,707 | **53.4%** |
| `end` / `ended` | 37,833 | 64.3% | 15,787 | 53.7% |
| **any fact at all** | **57,204** | **97.2%** | **28,122** | **95.6%** |

**⚠ This does NOT discharge `LUX-E2`, and must not be cited as if it did.** `LUX-E2`'s
threshold — *any field below 50% in the lower half needs a designed empty state* — is stated
over **delivered cards on a sample**, not over the raw population. `LUX-E2` remains BLOCKED on
its damaged `TAS-` sample.

What this *does* support, labelled as inference rather than measurement: **every field clears
50% in the population's lower half**, the lowest being `begin` at 53.4%. Routing skews famous,
so delivered interiors should carry *better* coverage than the population — which makes this a
conservative floor rather than an optimistic one. On that basis `L4-D3` ("render only what is
present, no placeholder rows") is not obviously wrong, and the artifact carries the data either
way, so a designed empty state stays a frontend change and never another rebuild.

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
control. **The owner's call, and its own track.**

Related but distinct, and recorded separately at
[`../2026-09-05-lux-e1-drift-source/README.md`](../2026-09-05-lux-e1-drift-source/README.md) §6:
`ULC-F4`, where the un-listenable rule's keep-check measures the **name** route while the app
resolves by **identity** first. Three findings now point at the same seam between what was
extracted and what is served.

## 5. Identity

| payload | entries | sha256 over sorted items |
|---|---|---|
| `spotify_ids` | 52,431 | `738e85c3b02da628…` |
| `apple_ids` | 35,919 | `d6d7a0719d0a8095…` |
| `artist_facts` | 89,090 | `dbe168f54f5a23f0…` |

Substrates, each verified by sha before reading: `graph-msw-tu50.bin` (`43dd82bb…`),
`graph-algb-full.bin` (`d008a2b5…`), `graph-t15-tiebreakfix.bin` (`4cb84ef9…`). Dump: the
2026-07-28 MusicBrainz JSON artist export.

**The payloads are written compactly and the script pins those separators**, so `lux4_extract.py`
reproduces the committed bytes exactly. A payload whose generator no longer reproduces it is not
frozen data.
