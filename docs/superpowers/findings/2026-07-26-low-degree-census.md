# Artists the app can never introduce you to — the degree-1 / degree-2 census, 2026-07-26

**Role: AUTHORITATIVE for its own interpretation. Owns no figures.** Every number
behind the claims below is owned by
[`builder/analysis/2026-07-26-low-degree-census/`](../../../builder/analysis/2026-07-26-low-degree-census/)
— its `REPORT.md` is the deliverable and its `README.md` records the method. **Cite that
directory, not this document, for any quantity.** A second copy would restate figures,
which `docs/README.md`'s one rule forbids.

**Nothing was rebuilt, routed, adopted or proposed.** Read-only throughout: no arm, no
config change, no threshold touched. **Path-quality work is paused by owner decision and
this census does not resume it.**

Identifiers are namespaced **`CNS-n`** — checked collision-free against the `C`, `F`, `A`,
`R`, `T3-`, `TF-`, `TFR`, `MKS-`, `ASC-`, `BYP-`, `DRV-`, `FMS-`, `P`, `G`, `O-` and `PR-`
series already in use.

---

## 1. What the census answers

**Which artists can never appear in the middle of a journey.** An interior card needs a
neighbour on each side, so an artist holding exactly one connection can only ever appear
as one of the two artists the user typed — **the app can never introduce anyone to it.**
`DRV-4` states this as structural and unmeasured; this is the measurement. Artists with
exactly two connections are reachable, but by exactly one route, so they are deliverable
only when the router happens to price that single detour.

**Three questions the record left open are closed by it**, all cited to the directory:

- **`DRV-4`'s denominator.** The two candidate populations are **nested, not
  alternatives**: `build_from_archive` sets `known = set(payloads)`
  (`builder/src/artistpath_builder/pipeline.py:131`) and keeps a neighbour edge only
  `if n.mbid in known` (line 184), so **every artifact node is a crawled artist**. An
  artist discovered in someone else's similarity list but never crawled is never a node.
  Both fractions are reported and they differ immaterially.
- **Counted after the largest-component prune.** Necessarily so — the artifact is written
  from `pruned`, built from `keep = largest_component(...)` (`pipeline.py:231-238`) — and
  confirmed observationally from the artifact rather than argued from the code.
- **Non-artist entities are excluded.** The build's only type filter matches the literal
  `special purpose` in the MusicBrainz disambiguation (`pipeline.py:42-47`), so this was
  checked rather than assumed. The one real contaminant is the nameless nodes, which are
  excluded from every list and reported separately: a node with no name floors at the fame
  floor for an artifact defect rather than for obscurity.

**Fame is the adopted proxy, unchanged** — pre-registration §5 with **A11**
(English-Wikipedia pageviews, absence scored at the fame floor) and **A15**'s recall
fallback, imported from the Track 2 modules rather than reimplemented. **The graph's own
popularity ranks nothing** (Phase 1 log §2.11). It was used only to screen who to ask,
which is sound here for a reason worth keeping: popularity is accumulated *before* the
mutual-kNN cap, so the reciprocity rule destroys a stranded artist's degree and leaves its
popularity untouched — the screen rides on the stage the defect never reaches.

## 2. What the census does not establish

The ranked lists are the top of a **screened** set, not provably the top of all low-degree
artists, and the cut was **deliberately not deepened** (owner's call, 2026-07-26): the
ranking is instrumental, its question was already answered by the known cases piling up at
the very top, and a better ordering *below* the reliable zone buys a marginally better
eyeball sample and nothing else.

A **famous artist with low in-graph popularity is not merely a screen imperfection.** Low
score-weighted in-degree means few crawled artists named that act as similar at all, which
is evidence about **what the snowball crawl reached** — the same class of question as the
census itself. Those artists are reported as candidate crawl-coverage gaps with two
cheaper explanations named (fame earned outside music; a name collision outside the
graph). **The check that would settle it is per-artist and manual, and was not run.**

## 3. Recorded in passing, not investigated

**`CNS-1` — an artist can be unfindable under the name users know it by, because the graph
stores one name and no aliases.** *(Plain: if you type the name you know a band by and the
graph stores a different spelling of it, the app tells you the band isn't there.)*

Observed by the owner, 2026-07-26. MusicBrainz names the band **Pretenders**; Wikipedia's
main article and Discogs both use **The Pretenders**. Searching the shipped app for *The
Pretenders* returns nothing, and the user must search *Pretenders*. MusicBrainz holds
aliases for artists and *The Pretenders* is among them, **so the information exists
upstream and is not reaching the app.**

**Why it is worth keeping.** Search is the only entry point to the app. An artist that
cannot be found under the name a user knows is, for that user, absent from the graph — a
different route to the same outcome as this census, and reached **without any graph defect
at all**. Leading definite articles are the obvious large subclass and are unlikely to be
the only one.

**Size is unknown and this finding does not estimate it.** Nothing here was investigated,
sized, or fixed.

**Related but distinct — do not merge them.**

- **`MKS-7`** (names shared by several artists) is the **collision** case: one name,
  several entities.
- **`CNS-1`** is the **inverse**: one entity, several names, one indexed.
- **`BYP-15`** (the card does not show the MusicBrainz disambiguation, though search does)
  is the same family of identity-presentation gaps.

**Cheapest first check, named and NOT run.** Establish whether alias data is already
present anywhere in the pipeline — in the crawl archive's raw responses, or in the APG1
metadata blob. `CLAUDE.md`'s "APG1 artifact" section *describes* that blob as carrying
mbids, names, disambiguations and popularity, with no alias field; **verify that against
`builder/src/artistpath_builder/artifact.py` rather than trusting the document** — the code
is the truth about the code, and this document deliberately does not assert what the blob
contains. If aliases are absent from both, adding them is a **data-source** question rather
than a search-tuning one, which changes the cost by an order of magnitude. A search-side
normalisation of leading articles would cover the largest subclass with no new data; that
is an **untested suggestion, not a recommendation**.

---

*`CNS-1` was found by an independent consulting session, 2026-07-26, and logged here
rather than by that session, which does not edit.*
