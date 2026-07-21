# How Do You Map Similar Artists?

*Notes from rebuilding a dead music tool, and the six ways we got it wrong first.*

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
>
> Factual errors here get corrected when found. See the coda, *Trap 7*, for two
> conclusions below that were themselves later overturned — the essay's own thesis,
> proving itself once more.

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

Picture 75,000 dots, one per artist, with lines between artists whose listeners overlap. Four million lines.

Two wrinkles made this harder than it sounds:

**Nobody has a list of all the artists.** There's no downloadable roster. So we started from the thousand most-listened artists and crawled outward — look up an artist, see who they're connected to, add those to the queue, repeat. Like exploring a city by walking every street from a few starting points.

**Similarity isn't mutual.** An obscure band might list Radiohead as similar; Radiohead doesn't list them back. Left alone, these one-way streets become dead ends. So we made every connection two-way, then kept only the largest fully-connected region — which guarantees that a route always exists between any two artists we offer.

Result: 75,000 artists, 99.997% of them reachable from each other. Finding a route is then a solved problem — a classic "cheapest path" algorithm from the 1950s, where each step's cost reflects how similar the two artists are, how big a fame gap you're crossing, and a small toll per hop to stop it rambling.

The whole thing lives in a single 43 MB file loaded into memory. No database. Routes come back in milliseconds.

---

## Part 4: Six traps

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

So is the hub problem topological or self-inflicted? **Still open.** The honest answer is that the experiment which settles it — rewiring the graph at random while preserving each artist's number of connections, then re-running the router — has not been run yet. It is the next thing on the list. What we do know is that the naive router, which reads no scores at all, seeks hubs nearly as hard as the smart one; and that a large fraction of routing decisions are currently being made on a coin-flip, because a percentile clip we added for tidiness made ~35,000 connections score identically at maximum and cost the router nothing to cross.

The lesson is not that the earlier reviews were careless. Each was a real improvement on the one before, and each was believed because it was better. The lesson is narrower and more annoying: **a measurement with no control is a story, and stories are very hard to stop telling once written down.** Trap 5 and Trap 6 both read as satisfying reversals — the twist where the bug was ours all along, the twist where the law of nature was self-inflicted. Satisfying is not the same as true.

Six traps, then a seventh made of the fixes to two of them. We now keep every measured number in exactly one file, and every graph records the commit that built it.

---

## Part 5: What we didn't use

**Audio analysis.** The original tool chose songs partly by matching *energy* between neighbours, so the playlist flowed sonically. That data source is dead with no free replacement. We lost something real here.

**Machine-learned embeddings.** The modern approach is to place every artist as a point in mathematical space and draw a straight line between your two endpoints. It's elegant, and it's what a fresh team would probably reach for. We stayed with the explicit map because it's interpretable — when a path looks odd, you can ask *why* and get an answer. That matters for a tool whose next feature is explaining its own choices.

**Fancier route-finding.** We use the plain 1950s algorithm. A cleverer variant was considered and rejected: it would have doubled the speed of something already fast enough, while introducing subtle correctness risks.

---

## Part 6: What actually worked

Four habits, all learned the hard way:

**Measure before you build.** Every big decision here was settled by a cheap test that took under an hour: timing an endpoint, sampling a data file, correlating 250 artists. Each one killed an approach that would have cost days or weeks.

**Metrics and eyeballs — never just one.** Judging by eye alone missed a systematic flaw for weeks. Judging by metrics alone confidently endorsed a router that produced nonsense. Both checks catch what the other misses, and you need both every time.

**Beware your own confounds.** Twice we drew a firm conclusion from an experiment that had a bug or an uncontrolled variable in it — and both times built further reasoning on top before catching it.

**Use the thing.** Three expert reviewers examined the code and found genuine problems. Then we spent twenty minutes actually *using* the app and found the worst bug of the entire project: the 30-second music clips are served from links that **expire after about an hour**, while we were caching them for **thirty days**. Every clip quietly died and nobody noticed, because the automated tests use fake clips, and reading code can't reveal that a URL has a shelf life.

No amount of code review would have caught it. Ten minutes of listening did.

---

## Where it stands

75,000 artists. Four million connections. Routes in milliseconds. Paths that mostly feel like the original — jazz drifting through soul into hip-hop, black metal easing out to country over seven or eight steps.

Still on the list: two structural defects in how the graph is built — a percentile clip that makes a large share of routing decisions free, and a neighbour limit applied at the wrong stage, which trims the obscure artists it was meant to protect while leaving the famous ones unbounded. Then the open question of whether the hub problem is the data's shape or our own doing. Then some stubbornly repetitive routing, and those expiring clips.

The honest summary is that "which artists are similar?" has no single correct answer — only a series of defensible choices, each with a failure mode you won't see until you look for it in the right way. Most of the work wasn't building the thing. It was finding out what we'd got wrong, and being willing to check.
