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

> **`CNS-` is this document's series, and attribution is per item, not per prefix.** The
> prefix originated with `CNS-1`, which an independent **c**o**ns**ulting session found;
> `CNS-2` and `CNS-3` are this session's own. One series per document is deliberate — a new
> prefix per finding is how a document accumulates collisions — so read the attribution line
> on each item rather than inferring it from the letters. Nothing here is renamed or
> renumbered.

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

## 3. `CNS-2` — the fame proxy's scope limit, and Track 2's exposure to it

*(This session's finding, 2026-07-26. Found while reading the census results, not sought.)*

**`CNS-2` — the adopted fame proxy misidentifies artists where names are short and
generic, and the error inflates fame rather than deflating it.** *(Plain: the proxy looks
an artist up by name only. Where the name is a common word, it can land on a different,
more famous subject — and then reports that subject's popularity as the artist's.)*

The resolver matches a Wikidata label or alias, requires the entity to be a musical
performer, and **never consults the disambiguation the graph already holds.** At the
low-degree end of the artifact the names are short and generic — *War*, *Sparks*,
*Shining*, *Proof*, *Psycho*, *Ariel*, *God*, *Meth* — so a collision is likely, and when
one occurs the **more famous** subject wins the pageview count *by construction*. Because
fame is the sort key, the wrong row then **sorts to the top of any ranked list**, which is
the part a reader eyeballs.

Worked examples, with the graph's own disambiguation contradicting the match: *War* (*US
funk/rock band*) → **Axl Rose**; *WATERS* (*2010s US-Norwegian band*) → **Roger Waters**;
*Cassidy* (*US rapper Barry Reese*) → **David Cassidy**; *Meth* (*UK drum & bass artist*) →
**Method Man**. And two where the graph holds **no** disambiguation at all: *Gosling* →
**Ryan Gosling**; *Kny* → **Demon Slayer: Kimetsu no Yaiba**.

**Why A11's validation did not see this.** A11 was validated on a purposively-chosen
sample of mostly-recognisable acts (§5's four strata), where a short-generic-name collision
barely arises. The limit is therefore a **property of the population the proxy is applied
to**, not a defect in the resolver's own logic and not a defect in this census's use of it.
Rates are owned by `builder/analysis/2026-07-26-low-degree-census/REPORT.md`.

**What it cost here, stated plainly:** two readings of this census were **withdrawn**, not
caveated — the screen-leak estimates, and the candidate crawl-coverage-gap reading built on
them. Leak and misidentification cannot be separated with this instrument. **What survived:**
the census's actual question, because the correctly-identified rows answer it on their own.

### Track 2's exposure, measured and bounded — not re-scored

The same resolver scored Track 2's path interiors at depth, so the exposure is real and was
checked rather than assumed. **Measured over Track 2's own committed fame tables**
(`builder/analysis/2026-07-24-track2-arm-scorer/fame.json`, `fame_stage2.json`) with the
identical classifier this census uses — **nothing was re-scored and no figure of Track 2's
was recomputed.** Rates are owned by this census's `REPORT.md`; the two error cases are
named because they are the finding.

**`R0` is not materially exposed.** Five reasons, each independent:

1. **The rate is an order of magnitude lower.** The differently-named-article rate over
   Track 2's interiors is a small fraction of the low-degree set's — which is the mechanism
   confirming itself, since Track 2's interiors are drawn from the mostly-recognisable
   population. **Phase 1 log §2.9 records every judged interior above the 90th popularity
   percentile**, with 57 % above the 99th; short generic names are rare there.
2. **Only two of Track 2's cases are genuine errors** — *Phoenix* → **Joaquin Phoenix** and
   *Love* → **Sean Combs**. The rest are the resolver working as designed on aliases: *Ye* →
   *Kanye West*, *P!nk* → *Pink (singer)*, *Caribou* → *Dan Snaith*, *The Jacksons* → *The
   Jackson 5*, *Florence + the Machine*, *Hall & Oates*, *Sly and the Family Stone*.
3. **`C1` is a difference of medians**, which two extreme outliers move barely at all.
4. **The error largely cancels in a paired contrast.** Fame is keyed by mbid with one value
   per artist, so an inflated artist contributes the *same* inflated value to whichever arms
   contain it; it fails to cancel only where the artist appears in one arm and not the other.
5. **The margin is far too large to close.** `R0`'s best arm reached a fraction of its
   pre-registered threshold — a gap two misidentified interiors cannot bridge by shifting a
   median.

**Bound, stated as a falsifier rather than a reassurance:** this would need revisiting if a
misidentified interior were **pivotal to a specific cell** — appearing in one arm's path and
not its baseline's at a scored depth. That was **not** checked, because checking it means
re-reading Track 2's per-cell paths, which is re-scoring. **Success condition:** if any
future work re-opens `R0` or re-scores Track 2, it re-runs this classifier per cell first.
Until then the exposure is recorded as **bounded and not material**, not as absent.

## 4. Open question — no owner, no schedule

**Does the crawl under-cover artists who are famous in populations the snowball barely
reached?** *(Plain: the graph was built by following similarity links outward from a
starting set. Whole regions of music — non-English-language, older, or simply distant from
where it started — may be thinly represented, and an artist there would look obscure to
every measurement this project has.)*

**This is recorded because it was nearly answered wrongly.** The consulting session asked
for it to be read off this census's screen leak: an artist with real fame and low
score-weighted in-degree means few crawled artists named them as similar at all, which
looked like direct evidence. **That reading is wrong and is withdrawn** — by `CNS-2`, leak
and misidentification are inseparable with this instrument, and the strongest apparent
leaks turned out to be *Ryan Gosling* and an anime. The reasoning was sound; the instrument
could not carry it.

**It needs a different instrument**, and naming which is not attempted here. What is
recorded is that in-graph popularity and Wikipedia pageviews **share a blind spot in the
same direction** — both under-report an artist outside the crawled population — so neither
can audit the other, and any answer needs a third source.

**No owner and no schedule, deliberately.** It is not a deferral with a due date; it is a
question the record should not lose. **Success condition — the terminal state that clears
it:** either a measurement using a population-independent source, or an explicit owner
decision that alpha does not need the answer. It blocks nothing.

## 5. Recorded in passing, not investigated

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

**The check's blast radius is wider than one file, and it is a description problem rather
than a grep problem.** If aliases *are* present, then two auto-loaded documents describe the
metadata blob incompletely — `CLAUDE.md`'s "APG1 artifact" section **and**
`.claude/agents/ml-graph-analyst.md`, which carries the same four-field list and is loaded
into every session that consults the analyst. Neither would contain a wrong *string* to
search for; both would be wrong **by omission**, which is the failure mode `CLAUDE.md`
records for the 2026-07-23 rename and the reason a stale-name grep cannot close this. Found
by the closeout B5 sweep, which covers `.claude/` for exactly this reason.

---

*`CNS-1` was found by an independent consulting session, 2026-07-26, and logged here
rather than by that session, which does not edit.*
