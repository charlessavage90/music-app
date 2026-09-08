# `LUX-E6` — tag vocabulary sanity: are the labels fit to show as written?

**Role: FIGURES OWNER for `LUX-E6`. ACTIVE. Never restate its numbers elsewhere.**
Governing document: `docs/superpowers/specs/2026-09-03-launch-ux-scope.md` §5, `LUX-E6`,
whose plain sentence was fixed before this ran: *are these labels fit to show the public as
written, or do they need an allowlist first?* **Threshold: descriptive.** This adopts nothing,
fixes no criterion and changes no vocabulary. It is the **entry condition** for the deferred
genre-tag work (spec §4.6); whether that work starts is the owner's decision, not this read's.

Run 2026-09-08 by `lux_e6.py` (one pass, no network, ~1 min). Derived outputs committed:
`lux_e6.json` (the census) and `lux_e6_sample.md` (forty real cards). Inputs are the three
frozen raw collections named in the script, which are gitignored and live only in the main
working tree.

## The frame, and the population

**The frame read is `F1`, unchanged from the release-tag coverage record** —
`docs/superpowers/findings/2026-07-31-release-tag-coverage.md` (`REL-1`): `F0` (ListenBrainz
genre-whitelisted tags ∪ Wikidata P136) plus MusicBrainz release-group *genres* over
attributable release groups only. Normalisation is the frozen `ct_common.norm_genre`, imported.

**The population is the served one — `graph-lux4.bin`, sha256 asserted against its manifest** —
not the 74,193-node artifact the `REL-` census ran over. That matters for one number:

| | artists |
|---|---|
| served | 58,838 |
| absent from **every** collection (entered via the extended ALG-B crawl, after the collections froze) | 13,488 |
| reached by at least one collection | 45,350 |

An artist in the second row carries no label here **by construction** — a gap in the frozen
collections, not a measured absence of tags. A production aggregation re-fetches them. Every
coverage figure below is therefore given against both denominators.

## (a) The vocabulary

| | value |
|---|---|
| artists with ≥ 1 label, of all served | 41,371 / 58,838 = **70.3 %** |
| artists with ≥ 1 label, of those reached | 41,371 / 45,350 = **91.2 %** |
| labels per labelled artist — median / p90 / max | 6 / 14 / 105 |
| labelled artists with more than 6 labels | 43.8 % |
| distinct label strings | **2,024** |
| of which in the MusicBrainz genre vocabulary (contributed by ListenBrainz or a release group) | 1,378 |
| of which contributed **only** by Wikidata P136 | 646 |

Where the chips would actually land — share of all (artist, label) impressions by how many
artists carry the label:

| label appears on | distinct labels | share of chip impressions |
|---|---|---|
| ≥ 100 artists | 347 | 92.0 % |
| 10–99 | 596 | 7.0 % |
| 2–9 | 608 | 0.9 % |
| exactly 1 | 473 | 0.2 % |

*(Plain: what a visitor would see is dominated by a few hundred ordinary genre names —
electronic, rock, pop, hip hop, ambient, jazz, house. The long tail exists but is rarely on
screen.)*

## (b) The odd ones — and they come from one source

Mechanical heuristics over all 2,024 strings, each tagged with its sources (`l` ListenBrainz,
`r` release group, `w` Wikidata):

| heuristic | count | every example |
|---|---|---|
| longer than 28 characters | 10 | contemporary singer songwriter ·w, drum and bass electronic rock ·w, electroacoustic improvisation ·w, historically informed performance ·w, indigenous music of north america ·w, **lgbt related television series ·w**, musique concrete instrumentale ·r, **national socialist black metal ·w**, new wave of british heavy metal ·w, **post apocalyptic television series ·w** |
| contains a digit | 6 | 2 step ·lr, 2 step garage ·w, 2 tone ·lrw, 20th century classical ·w, c86 ·lr, uk82 ·lr |
| odd characters | 3 | bass music (edm) ·w, glitch hop (edm) ·w, oi! ·w |

The heuristics are crude; the source column is the finding. **Every string a curator would
stop on is Wikidata-only.** P136 is "genre" on *any* Wikidata item, so it carries film and
television genres wherever an artist item is conflated with a work, and non-musical
descriptors wherever an editor stretched the property. From the seeded lists in `lux_e6.json`:
*adventure film, body horror film, german television comedy, historical drama film, splatter
film, supernatural horror film, environmentalist, leftist, lgbt, bacardi, yellow, hipster,
canon, cruise, haul, game, epic, wind, tenor, monologue, conceptual art, postmodernism, rock
alternative music prize.* Also among the Wikidata-only labels are real genres MusicBrainz
spells differently (*rhythm and blues* ×601, *traditional folk* ×301, *electronic dance*
×246, *intelligent dance* ×69 — i.e. R&B, folk, EDM, IDM), which read as near-duplicates of
chips the same card already shows.

The two MusicBrainz-vocabulary sources produced **no string the heuristics or the eye stopped
on**: MusicBrainz genres are a curated list, and ListenBrainz's genre field is a transport for
it (`COH-5`). *2 step*, *c86* and *uk82* are real genres spelled as
their scenes spell them.

**What dropping the Wikidata-only labels costs:**

| | value |
|---|---|
| chip impressions carried by Wikidata-only labels | 1.6 % |
| artists whose **last** label is Wikidata-only (would lose their chip row) | 147 |

## (c) The cards

`lux_e6_sample.md`: forty artists, ten per popularity quartile of the served population
(seed 20260908; `pop_raw`, raw currency, used only to spread the sample). Two things to read
off it rather than off a number:

- **The empty state is real and lands where the app routes.** In the least-popular quartile,
  six of ten sampled cards carry no label at all; in the top quartile, one of ten.
- **The chip row needs a cap and an order.** Median six labels, p90 fourteen, and the most
  frequent labels (*electronic, rock, pop*) are the least informative — a row ordered by
  frequency would open with the same three words on most cards. That is a design decision for
  the genre track, not for this read.

## The read, in the spec's own sentence

*Are these labels fit to show the public as written, or do they need an allowlist first?*

**The MusicBrainz-vocabulary labels are fit to show as written. The Wikidata P136 labels are
not.** The allowlist the spec asked about already exists — it is the MusicBrainz genre list —
and the cheapest curation is to admit a Wikidata label only where that list contains the same
string, which costs 1.6 % of chip impressions and un-labels 147 artists. Anything beyond that
(spelling reconciliation, a cap, an order, the empty state) is the genre track's design work
and is **not** an entry condition.

**Weakest link.** The heuristics are crude by design and the eyeballed lists are seeded
samples, not a full curation pass; a Wikidata-only label that is both plausible-looking and
wrong would pass all three. That risk is bounded by the impressions figure above, and it is
removed entirely by the allowlist rule rather than by a better heuristic.

## What this does not conclude

- Nothing about whether genres **should** ship — spec §4.6's deferral stands until the owner
  lifts it. Coverage in the obscure half is `REL-`'s figure and lives there.
- Nothing about the 13,488 unreached artists' tags: they were never fetched.
- Nothing about Discogs (`F4`/`F6`): out of the frame read.

## Files

| file | owns |
|---|---|
| `lux_e6.py` | the read — frame, census, heuristics, sample |
| `lux_e6.json` | the census and every list quoted above |
| `lux_e6_sample.md` | the forty cards |
