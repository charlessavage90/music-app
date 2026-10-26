# #270: where the famous-to-famous defect lives, map or router — what the record already establishes

**Role: SYNTHESIS, from the committed record only.** No new computation went into this page. It owns
**no figures**: every claim cites the document that owns its numbers, and the numbers stay there. Where
a sentence below uses a proportion, it is quoting that owner's own plain-language inference. **It
decides nothing.** Which lead to pursue, or whether to accept the defect, is the owner's (#270, *Whose*).

**The defect, in one sentence:** pick two famous artists, press Dig deeper many times, and the artists
in the middle of the journey stay famous (#270).

## What is established

**1. The map has a wall at the very top, and the wall is in the connections, not in how fame is
measured.** Close to half of the most-listened 1 % of artists have no connection at all to anyone
outside the most-listened tenth. On the previous map almost none did. Re-judging the current map's
connections with the previous map's fame ruler leaves the wall in place, and re-judging the previous
map's connections with the current ruler leaves it open. *Source:*
`builder/analysis/2026-09-27-issue-200-ruler-vs-map/README.md` §1 (attribution table) and §2. *Not
established there:* which part of building the map made the wall, the new similarity scores or the
artists the current map added competing for each famous artist's top slots (same README, §3 first
bullet).

**2. The wall is made by the fifty-connection limit, not by missing data.** Before the limit, all but
one of the most-listened 1 % have less-listened artists among their candidates, and the typical one
has hundreds. After it, close to half have none. The pre-fixed rule read this as `SUP-R1`: *most famous
artists do have less-listened similar artists in the data, and the fifty-connection rule is what throws
them away.* The mechanism is the famous artist's **own** limit: it keeps its fifty strongest
connections, ranked on raw co-listening with no correction for how much an artist is played overall,
and those are the famous ones. *Source:*
`builder/analysis/2026-09-27-issue-200-trim-supply/README.md` §1 (reading-rule table, deletions by
whose limit) and §2. *Its own weakest link:* the discarded candidates were counted, not judged. Some
may name the famous artist only because everyone plays it (same README, §3).

**3. Where the exits do exist, the router declines them at today's pull, and at twice and three times
it.**
- On an earlier map and data source, Track B built graphs where every famous artist was
  force-connected to its ten strongest obscure partners, confirmed the connections existed, and the
  router took none of them at production weights. Its inference was that the router's price on jumps
  in popularity outranks the new connections. *Source:*
  `docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md` §1 `CRS-C5` (*do journeys
  between famous artists pass through anyone below the top tenth*) and §2, fourth bullet. *Caveat:*
  this was on that period's two crawl archives (`ALG-E`, *the production data then*, and `ALG-B`,
  *the candidate data then*), under that period's fame frame, not on today's map. On the candidate
  data, journeys between famous artists did sometimes pass below the top tenth, even under the rule
  then in production (same section): it cuts against reading the router as the only constraint.
- On today's map, pressing twice or three times as hard did nothing on either famous tier: after
  seven to ten presses, the middle of the journey was exactly as famous as today's app gives. *Source:*
  `docs/superpowers/findings/2026-09-28-drp-lattice-results.md` §1.2 (every ramp cell reads NO
  MOVEMENT) and §2, first paragraph.
- Giving the most-listened 1 % their deleted less-listened connections back (up to ten each) also did
  nothing at today's pull or the stronger pulls. Every famous journey passed within one step of an
  added connection, and few took one. *Source:* lattice results §1.2 and §2, second paragraph.
- **Which of the two binds, by tier:** `DRP-R13` (*if a fame ceiling had to rise a lot to find any
  route, the map is missing the connections; if it hardly had to rise, yet stronger pulls moved
  nothing, the connections exist and the pull does not take them*) read **missing supply** for the
  most-listened 1 % on today's map, and **pricing** for the next four percent on today's map and for
  both tiers once the extra connections were added. *Source:* lattice results §1.6.

**4. Only a hard cap on fame moved anything, and the version that moved both tiers failed the
listen on coherence.**
- A ceiling that, from the fourth press, lowers the most famous artist a journey may pass through
  moved the next-four-percent tier on today's map. It fell short on the most-listened 1 %, because
  there the map lacks the routes (`DRP-S0P3`, *the ceiling on today's map*). With the extra connections
  added it moved both tiers (`DRP-S1P3`, *the ceiling with the extra connections*). The lattice's own
  reading is that the ceiling moved fame **because it forbids famous artists**, not because the router
  found less-listened ones. The router accepted weaker steps to obey it, and journeys got longer.
  *Source:* lattice results §1.2, §2 third to fifth paragraphs, and §3.
- **What it cost:** in the blind listen of today's app against `DRP-S1P3`, the owner picked today's
  app on coherence by a margin past the pre-set bar, and the candidate on novelty on every row. The
  pre-registered read is a split, which reads as FAIL: *"After several presses, today's app gives
  better journeys on coherence."* *Source:* `docs/superpowers/findings/2026-10-01-dsl-listen-results.md`
  §0.
- **What that result does not license** (same note, §4): that the ceiling alone, the extra connections
  alone, or any single cost term caused the coherence loss; any per-tier reading; any claim about the
  first path. The listen also could not separate "the candidate's steps fit worse" from "the
  candidate's journeys are longer" (§0, item 4).

**5. The exploration's outside-literature pass killed most re-pricings and kept one direction.**
Exploratory by its own brief, and not evidence.
- **Killed:** popularity-divided random-walk scoring (journeys shrank and fame barely moved); a penalty
  on how many connections an artist has (it cannot tell a superstar from a mid-level artist, because
  connections top out at fifty, and the router paid it by cutting stops); rescaling similarity by how
  unusual it is for both artists (the first journey got weaker and fame did not move); splicing a less
  famous artist in around the pressed one (two famous neighbours almost never share a less famous one).
- **Kept as promising:** a per-press penalty in fame-percentile currency, with the journey's length held
  fixed and a floor on each step's similarity.
- *Source:* `exploration/r1-outside/NOTES.md`, "What I tried" table and "Best variant". The wider
  exploration's own summary of what died is `exploration/REPORT.md`, "What I tried and what died".

**6. The map's similarity score did not track the owner's ear on weak steps.** Against his "this step
doesn't fit" marks from the listen, neither the map's similarity nor shared neighbours scored his
marked steps worse clearly enough to pass the bar. The exploration's model rater did. *Source:*
`docs/superpowers/findings/2026-10-03-snw-marks-test.md` §0. This bears on any measure of link
quality that uses the map's own similarity, including the descriptive now running for #270.

## Read together (inference, labelled)

The record supports a two-layer reading. At the very top, **the map** withholds the exits: the limit
deletes them before the router ever sees them (items 1–2, and `DRP-R13`'s "missing supply" on the top
tier). Wherever exits exist, whether on the next tier or because they were restored, **the router's
pricing** declines them at every pull strength tried (item 3). Only forbidding famous artists outright
moved fame, and the one version that did so on both tiers was heard as less coherent (item 4). Neither
layer has been changed alone and listened to.

## Open questions the record names and has not run

- **Are the deleted exits good connections or noise?** Named by trim-supply §4 (fourth bullet) and by
  the depth-remedy pre-registration's `DRP-X1` (*supply counts candidates, not good ones*). **Its
  map-currency half has since run** (`builder/analysis/2026-10-26-issue-270-discarded-exit-quality/`,
  design committed before the run, which owns its figures and its four-part read). Its by-ear half (a listen or a coherence measure, trim-supply §3)
  is not.
- **The ceiling on today's map without the extra connections was never listened to** (#270, "What
  neither record closes").
- **Which part of building the map made the wall:** the new similarity scores or the wider crawl
  (ruler-vs-map §3; trim-supply §3, "One map"). Also what the upstream cut on each artist's list bounds,
  which was not measured (trim-supply §3).
- **Whether journeys forced under a fame cap still hang together** is not measured offline by anything
  (lattice results §3).
- **Journeys between obscure artists under the trimming rule** were unreadable in Track B (Track B
  results §3).
- **Whether the exploration's length guard is needed:** its similarity floor without the fixed length
  was never tried (`exploration/r1-outside/NOTES.md`, "For round 2", item 1). Also *stop the router
  preferring a short all-famous hop over a long obscure detour* (`exploration/REPORT.md`, "What I'd try
  next", item 3).
- **Parked on the owner's trigger:** #271's second clause (whether an edge-price pre-registration for
  shared neighbours follows; an analyst critique was recommended and not run); #272 (a listen of two
  digging variants side by side); #273 (whether the fame measure under-ranks well-known artists just
  below the top); #249 (a ceiling that varies along the journey).
