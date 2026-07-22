# How Do You Map Similar Artists?

*Notes from rebuilding a dead music tool, and the many ways we got it wrong first.*

> **Role: NARRATIVE. Not project documentation.**
>
> This is a journal, written for people, about how the modelling went. **Do not use it as
> context for development work, do not cite it, and do not instruct any change from it.**
> It is not maintained to the standard of the project's technical documents and it will
> lag reality between updates.
>
> For anything measured — scores, correlations, hub statistics, path quality — the single
> authoritative record is
> [`superpowers/findings/2026-07-21-scoring-adjudication.md`](superpowers/findings/2026-07-21-scoring-adjudication.md).
> Start at [`README.md`](README.md) for the documentation map.

<details>
<summary><strong>How to update this document</strong> — read before editing</summary>

**What this is.** A narrative account of the journey: the major directional changes, the
things we tried, the mistakes, the traps, and what each one taught us. It is written for a
non-technical reader who wants to understand *how the thinking went*, not what the code does.

**What this is not.** Not a ledger. Not a day-by-day account of decisions or tasks. Not a
changelog. Not a status report. If an update reads as "and then we did X, then Y, then Z,"
it belongs in the execution log instead — this document only cares about X, Y and Z if one
of them **changed the direction** or **taught us something we had believed wrongly.**

**How to update it.** Not by appending. A phase of work usually invalidates something
already written here, and the honest version requires going back and revising it — a
prediction that didn't survive, a conclusion that was overturned, a number that moved.
**Expect to edit the middle of the essay, not just the end.** The running thread is that
each round of corrections has itself contained errors, so a new section that only reports
good news is almost certainly incomplete.

**Two standing rules.** Keep measured figures approximate and point at the authoritative
record for the real ones — precise numbers restated here drift and then mislead. And
preserve the failures: the traps are the substance of this document, and a revision that
quietly tidies away a wrong turn destroys the only thing it is for.

</details>

---

## The premise

There used to be a wonderful toy called **Boil the Frog**. You gave it two artists — say Miles Davis and Daft Punk — and it built you a playlist that walked gradually from one to the other. Every step sounded like a small, sensible move from the last, but by the end you'd travelled from jazz to French house without ever feeling a jolt. Hence the name.

It died. The music-data company behind it was bought by Spotify and switched off, and in late 2024 Spotify closed the equivalent doors to everyone else. So rebuilding it meant answering the question that tool quietly depended on:

**How do you know which artists are similar?**

That turns out to be much harder, and much more interesting, than it sounds.

---

## Part 1: Finding the data

You cannot compute similarity from nothing. Somebody has to have observed which artists go together. Our options, and what happened to each:

**Spotify** — closed. The relevant endpoints were deprecated for all new applications in November 2024.

**Last.fm** — works, and is good. But it's free *for non-commercial use only*. If this ever has paying users, that becomes a licensing problem exactly when the project starts earning. Ruled out — not because it's bad, but because building on it would create a trap for later.

**Spotify's Million Playlist Dataset** — a million real playlists, which would have been ideal. No longer downloadable, and research-only.

**ListenBrainz** — an open, non-profit alternative that publishes artist-similarity data under a public-domain licence. They released it, pointedly, *in response to* Spotify closing its doors. This is what we used.

The similarity itself comes from listening behaviour: not "these two artists sound alike" but "the same people play both." That distinction matters later.

---

## Part 2: The popularity problem, or how to waste a week

Similarity alone isn't enough. The original tool's insight was that a good path also keeps a *steady level of fame* — you don't want a route from two household names to detour through somebody with four hundred listeners. So we needed to know how popular each artist is.

This took four attempts.

**Attempt one: just ask.** There's an endpoint that returns listener counts per artist. It works. It takes **23 seconds per artist.** For 75,000 artists that's three weeks of continuous requests. We only knew this because we timed it before building on it — the estimate we'd written down beforehand was eight hours.

**Attempt two: download everything.** There are bulk data dumps — 191 GB of raw listening records. Before downloading, we grabbed a small sample and looked inside. Of 200,000 listening records, **0.03% contained a usable artist ID.** The rest were free text. Aggregating them was impossible. That inspection cost twenty minutes and saved a 191 GB download and days of processing.

**Attempt three: borrow it from elsewhere.** Deezer publishes fan counts. We tested how well they predicted ListenBrainz popularity across 250 artists. The correlation was **0.089** — essentially none.

That failure was the most instructive one. Deezer's data isn't wrong; it describes a *different audience*. Deezer is big in France and Brazil; ListenBrainz skews Western and tech-forward. An artist's standing in one says almost nothing about the other. And since our similarity data came from ListenBrainz listeners, mixing in Deezer's popularity would have quietly blended two different universes.

**Attempt four: use the map itself.** In the end, popularity came from the similarity data we already had: an artist is popular if lots of other artists point at them. Free to compute, and — crucially — measured on exactly the same population as the similarity. No universe-mixing.

---

## Part 3: Building the map

Picture 75,000 dots, one per artist, with lines between artists whose listeners overlap. Four million lines — a number that later turned out to be about four times too many.

Two wrinkles made this harder than it sounds:

**Nobody has a list of all the artists.** There's no downloadable roster. So we started from the thousand most-listened artists and crawled outward — look up an artist, see who they're connected to, add those to the queue, repeat. Like exploring a city by walking every street from a few starting points.

**Similarity isn't mutual.** An obscure band might list Radiohead as similar; Radiohead doesn't list them back. Left alone, these one-way streets become dead ends.

Our first answer was to make every connection two-way and keep only the largest fully-connected region — which guarantees a route always exists between any two artists we offer. That second half was right and has never changed. The first half was quietly wrong from the very beginning, and *Part 5* is the story of finding out.

The current rule is stricter: **a connection survives only if each artist ranks the other among their closest**. Mutual agreement, not one-sided assertion. Everything else is discarded before the map is drawn.

Result: roughly 75,000 artists, very nearly all of them reachable from each other. Finding a route is then a solved problem — a classic "cheapest path" algorithm from the 1950s, where each step's cost reflects how similar the two artists are, how big a fame gap you're crossing, and a small toll per hop to stop it rambling.

The whole thing lives in a single file loaded into memory — now about a third the size it was, for reasons *Part 5* explains. No database. Routes come back in milliseconds.

---

## Part 4: Seven traps

This is the interesting part.

### Trap 1: Trusting our own eyes

The first real paths were beautiful. Miles Davis → Duke Ellington → Louis Armstrong → Ella Fitzgerald → Frank Sinatra → … → Daft Punk. Jazz to electronica, every step adjacent. We declared victory.

We had no way to tell a good path from a bad one. We just liked that one.

### Trap 2: The 1013× lie

Buried in the code was a line that scaled each artist's connection strengths relative to *their own strongest connection*. It seemed sensible. It was catastrophic.

It meant every artist's best connection scored a perfect 1.0 — whether the underlying evidence was 11 shared listeners or 11,147. **A 1013-fold difference, flattened to identical.** An unknown band's tenuous best-friendship looked exactly as strong as Radiohead's deepest bond.

Every quality measurement we built on top of that was measuring a lie.

### Trap 3: Optimizing the metric instead of the product

So we built proper measurements, then used a smart search algorithm to tune the routing settings against them. It worked beautifully. Every number improved.

The paths it produced:

> Miles Davis → J. K. Simmons → Hank Levy → Justin Hurwitz → Emma Stone → Daft Punk

Two of those are **actors**. It had discovered that the cast and composers of *Whiplash* and *La La Land* are tightly linked in listening data, and cheerfully routed through them. Elsewhere it found `jesus2099` — not a musician at all, but a database editor whose account had leaked into the artist list.

The optimizer did precisely what we asked. We'd asked for the wrong thing.

### Trap 4: The textbook fix that over-corrected

The standard remedy for the 1013× problem is a formula that divides by each artist's overall listening volume — it stops famous artists looking similar to everyone simply by virtue of being famous.

It over-corrected. Because it rewards connections that are *surprising* relative to how obscure both artists are, it inflated tiny scenes. Ask it for a path out of Miles Davis and it routed through the cast of *La La Land* — Miles Davis, then an actor, then a composer, then another actor.

There's a real lesson here: raw numbers over-favour the famous, and the correction over-favours the obscure. The answer is somewhere in between, and where exactly is an empirical question, not a theoretical one.

*(The specific figure this section originally quoted turned out not to reproduce against any graph we built. The conclusion survived; the number didn't. See Trap 7.)*

*(We eventually ran that empirical question properly — a quarter of the correction, half, three-quarters, and none — and the answer came back **none**. Not somewhere in between. See Part 5.)*

### Trap 5: Blaming the maths for our own bug

We concluded the textbook formula was simply wrong for our data and moved on.

A later review found what looked like the actual cause: we'd applied two adjustments in the wrong order, silently cancelling one of them. The formula was fine, we decided. Our arithmetic wasn't. We'd blamed a well-established method for a bug we'd written ourselves — and nearly discarded the right approach because of it.

*(This is where the essay originally ended this section. It is wrong. See Trap 7.)*

### Trap 6: Mistaking a symptom for a law of nature

Paths kept routing through famous artists. Radiohead turned up *everywhere* — the universal connector. We measured that every routing strategy did this, even the dumbest possible one, and concluded it was simply the shape of the data. Unfixable. A law of nature.

Then a second analysis reported that our similarity scores were strongly correlated with artist fame — meaning what we called "similarity" was substantially a popularity measure in disguise. The router wasn't drawn to hubs because of the map's shape, we concluded; it was drawn to them because we'd accidentally told it to be.

We'd also taken a single experiment — run on the broken data, changing five things at once — and elevated it into a principle. It didn't survive contact with a clean test.

*(Nor, it turned out, did the correction. See Trap 7.)*

### Trap 7: The corrections were traps too

Traps 5 and 6 are both wrong. We found out the way we found out everything else here — by finally building the control we should have built first.

**Trap 5's diagnosis was impossible.** The ordering bug is real and still sits in the code. But we went back and checked *which commit built which graph file*, and the graph that produced the bad paths predated the code containing the bug. It cannot have been the cause. We had four graph files sitting in one folder with no record of what built them, and we'd compared two that differed in **two** ways as though they differed in one. Both analyses built on that comparison collapsed.

**And the formula was not fine.** Trap 4 was right all along: the textbook correction really does over-correct on this data. Trap 5 exonerated it on the strength of a bug that wasn't there, and very nearly shipped the film-soundtrack paths as an improvement.

**Trap 6's correlation didn't reproduce.** Re-measured, it came out far weaker, and it flipped sign depending on which graph we measured. Worse, it was close to circular by construction: we define an artist's popularity as the sum of its own similarity scores, so correlating similarity with popularity partly correlates a quantity with itself. A positive number there is the *expected* result of the null hypothesis, not evidence against it.

So is the hub problem topological or self-inflicted? At the time of writing this section, **still open** — the experiment that settles it, rewiring the graph at random while preserving each artist's number of connections and re-running the router, had not been run. *It has since been run, and the answer is the fourth twist in this story. See Part 5.*

What we knew even then: the naive router, which reads no scores at all, seeks hubs nearly as hard as the smart one; and a large fraction of routing decisions were being made on a coin-flip, because a percentile clip we added for tidiness made tens of thousands of connections score identically at maximum and cost the router nothing to cross.

The lesson is not that the earlier reviews were careless. Each was a real improvement on the one before, and each was believed because it was better. The lesson is narrower and more annoying: **a measurement with no control is a story, and stories are very hard to stop telling once written down.** Trap 5 and Trap 6 both read as satisfying reversals — the twist where the bug was ours all along, the twist where the law of nature was self-inflicted. Satisfying is not the same as true.

Six traps, then a seventh made of the fixes to two of them. We now keep every measured number in exactly one file, and every graph records the commit that built it.

---

## Part 5: Fixing the two real defects, and what happened when we did

Two structural problems had been sitting on the list for months, both known, both
genuinely wrong, both waiting for someone to build the apparatus to settle them.

**The neighbour limit was applied at the wrong moment.** We capped each artist at fifty
connections — then made everything two-way, which quietly added them all back. The cap
bounded nothing. Worse, it bounded the wrong people: it trimmed the obscure artists it was
meant to protect, while the famous ones ended up connected to everything. A configured
limit of fifty produced artists with over eleven thousand connections.

**The percentile clip made a large share of routing decisions free.** Connection strengths
were squashed into a 0-to-1 scale by a formula that pinned everything above a threshold at
exactly 1.0. A connection scoring a perfect 1.0 costs the router *nothing* to cross. Tens
of thousands of connections sat at that ceiling, so on a large fraction of steps the router
was choosing between options it considered identically free — a coin-flip wearing the
costume of a decision.

We fixed both. And here the story stops being a repair job.

### The fix that worked

Requiring **mutual** agreement — a connection survives only if each artist ranks the other
among their closest — fixed the cap properly. It is the only formulation that both bounds
how connected an artist can be *and* stays symmetric. It is also brutal: it deleted roughly
three-quarters of the map, taking four million connections down to under a million, while
keeping almost 99% of the artists.

Deleting three-quarters of a map sounds like vandalism. It made the paths better, in two
separate blind listening tests. The connections it removed were overwhelmingly one-sided
assertions — an obscure band claiming kinship with Radiohead that Radiohead's own data
never returned. Those aren't similarity. They're aspiration.

### The fix that made things worse

The clip fix worked too, in the sense that it did exactly what we designed it to do. A rank
transform removes the ceiling entirely: no ties at the top, no free steps, every routing
decision an actual decision. The defect we'd been complaining about for months, gone.

We built it, put it head-to-head against the version that still had the defect, and listened
to both without knowing which was which.

**The version with the defect won.**

We kept the defect. It is still in the code today, deliberately, and it is written into
Phase 1's list as an unresolved problem rather than a solved one.

This is the most uncomfortable result in the project, and we have no satisfying explanation
for it. The honest reading is that "this metric has an obviously wrong property" and "fixing
that property improves the product" are different claims, and we had been treating them as
the same claim for months.

### The correction to the correction to the correction

We finally ran the rewiring experiment that Trap 7 said was next on the list: shuffle the
map at random, keep every artist's number of connections exactly the same, destroy all the
real community structure, and see whether the router still gravitates to hubs.

It did. Just as much. Slightly more, in fact.

So **Trap 6's original instinct was right after all** — for simple routing, hub-seeking
really is the shape of the data, not something we told the router to do. The sophisticated
correction that overturned it in Trap 7 was itself wrong. That is now three layers: a naive
read, a clever reversal of it, and a control experiment reinstating the naive read.

But not cleanly, and this is the part that matters. Our *actual* router — the one with the
full cost function — seeks hubs substantially harder than that topological baseline. The
experiment cannot say why, because rewiring the map destroys the very scores that router
depends on. So there is a real excess, over and above the shape of the data, and it remains
unexplained. The most plausible suspect is the term that penalises fame *gaps* between
consecutive steps: told to keep the journey smooth, the router may be routing through many
moderately famous artists precisely to avoid a jolt. That is a hypothesis read off the
configuration, not a measurement.

The lesson is not "we were right all along." It is that the original conclusion was right
**for reasons nobody had established at the time** — it was a lucky guess wearing the
clothes of a finding, and it took two reversals and a proper control to earn what we had
already believed.

### The measurement that disqualified itself

The comparison ran six versions of the map at once, scored on a battery of metrics, with
the whole thing planned in advance so we couldn't move the goalposts afterwards.

One family of metrics — the ones measuring how much two artists' neighbourhoods overlap —
**changed sign depending on which half of the test set we looked at.** Same versions, same
data, opposite conclusions. That is not a close result. It is an instrument that cannot be
trusted at the size of difference we were trying to detect.

The saving grace was that we noticed this while it was pointing *against* the version we
ended up choosing. Had it favoured our preference, the temptation to accept it and move on
would have been considerable, and we would never have learned the instrument was broken.

### And then the thing that actually decided it

The final choice between the last two candidates came down to a blind listening session.
Two identical copies of the app, two different maps, no labels, one question: which produces
better paths?

The verdict was clear. It also had almost nothing to do with anything we had measured.

The difference showed up in the **reroll** feature — the "not for me" button that rebuilds
the path around an artist you don't want. On first paths, generated fresh with no rerolls,
the two maps were judged largely similar. It was only after four, seven, nine rerolls that
they diverged sharply: one kept opening up, growing longer and reaching genuinely unfamiliar
artists; the other just swapped one famous name for another famous name and stayed the same
length no matter how hard it was pushed.

**Every metric in the six-way comparison measured first paths.** The entire apparatus was
pointed at the one part of the experience that turned out to be least informative.

That is Trap 3 again — optimizing the metric instead of the product — but wearing a much
better disguise. We hadn't chosen a bad metric this time. We'd chosen reasonable metrics and
pointed them at the wrong moment in the user's journey.

---

## Part 6: What we didn't use

**Audio analysis.** The original tool chose songs partly by matching *energy* between neighbours, so the playlist flowed sonically. That data source is dead with no free replacement. We lost something real here.

**Machine-learned embeddings.** The modern approach is to place every artist as a point in mathematical space and draw a straight line between your two endpoints. It's elegant, and it's what a fresh team would probably reach for. We stayed with the explicit map because it's interpretable — when a path looks odd, you can ask *why* and get an answer. That matters for a tool whose next feature is explaining its own choices.

**Fancier route-finding.** We use the plain 1950s algorithm. A cleverer variant was considered and rejected: it would have doubled the speed of something already fast enough, while introducing subtle correctness risks.

---

## Part 7: What actually worked

Six habits, all learned the hard way:

**Measure before you build.** Every big decision here was settled by a cheap test that took under an hour: timing an endpoint, sampling a data file, correlating 250 artists. Each one killed an approach that would have cost days or weeks.

**Metrics and eyeballs — never just one.** Judging by eye alone missed a systematic flaw for weeks. Judging by metrics alone confidently endorsed a router that produced nonsense. Both checks catch what the other misses, and you need both every time.

**Beware your own confounds.** Twice we drew a firm conclusion from an experiment that had a bug or an uncontrolled variable in it — and both times built further reasoning on top before catching it.

**Use the thing.** Three expert reviewers examined the code and found genuine problems. Then we spent twenty minutes actually *using* the app and found the worst bug of the entire project: the 30-second music clips are served from links that **expire after about an hour**, while we were caching them for **thirty days**. Every clip quietly died and nobody noticed, because the automated tests use fake clips, and reading code can't reveal that a URL has a shelf life.

No amount of code review would have caught it. Ten minutes of listening did.

**Decide what counts as a win before you look.** The six-way comparison was written down in
advance: which metrics, which thresholds, and what each possible outcome would mean. That
sounds bureaucratic until you are staring at a result you dislike. Twice in this project a
disappointing number was followed by an entirely reasonable-sounding argument for gathering
more evidence — and the only thing separating that from moving the goalposts is whether the
rule was fixed beforehand. The final listening test was pre-registered down to *a second
test is forbidden*, precisely so that a result we didn't like couldn't quietly become a
first draft.

**Judge blind, and keep the judge ignorant.** For the final comparison the person running
the test was deliberately kept from knowing which version was which, what the metrics said,
or what any outcome would imply — and the verdict was written down and locked before any of
that was read. This felt excessive. It stopped being excessive the moment the verdict came
back contradicting the metrics: because nobody could have been nudged, there was no version
of the argument where the result got explained away.

---

## Where it stands

75,000 artists. Under a million connections now, and better for it. Routes in milliseconds. Paths that mostly feel like the original — jazz drifting through soul into hip-hop, black metal easing out to country over seven or eight steps.

The map itself is settled. Both structural defects were investigated properly: the neighbour limit is fixed, and the percentile clip is **knowingly still there**, because the version without it was worse to listen to. The hub question has a partial answer — for simple routing it really is the shape of the data, but our actual router seeks hubs harder than that explains, and nobody yet knows why.

What's left is no longer about the map. It's about what happens when you *use* it: the reroll button doesn't yet do what it should, the clips still expire, and the interface has a handful of things that only reveal themselves in use. The reroll work leads, because the blind test showed that rerolling is where the whole experience is actually decided — and because we have exactly one measurement of it, which is a person's opinion.

The honest summary is that "which artists are similar?" has no single correct answer — only a series of defensible choices, each with a failure mode you won't see until you look for it in the right way. Most of the work wasn't building the thing. It was finding out what we'd got wrong, and being willing to check.

And the running joke of this document is that every round of checking has itself needed checking. Seven traps became a trap about the corrections to the traps, which has now become a correction to *that* — the naive answer reinstated, but only after a control experiment nobody had run when the naive answer was first believed. We are not getting better at being right the first time. We are getting better at finding out sooner.
