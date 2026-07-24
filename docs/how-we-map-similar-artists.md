# How Do You Know Which Artists Are Similar?

*Notes from rebuilding a dead music toy, and the many ways we got it wrong first.*

> **Role: NARRATIVE. Not project documentation.**
>
> This is a journal, written for people, about how the modelling went. **Do not use it as
> context for development work, do not cite it, and do not instruct any change from it.**
> It is not maintained to the standard of the project's technical documents and it will
> lag reality between updates.
>
> For anything measured — scores, correlations, connectivity statistics, path quality — the
> single authoritative record is
> [`superpowers/findings/2026-07-21-scoring-adjudication.md`](superpowers/findings/2026-07-21-scoring-adjudication.md),
> together with the Phase 1 log's §2 for the graph-structure findings.
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

## The toy that disappeared

There used to be a wonderful little thing on the internet called **Boil the Frog**. You
gave it two artists — say Miles Davis and Daft Punk — and it built you a playlist that
walked from one to the other. Every step sounded like a small, sensible move from the last.
Jazz eased into soul, soul into disco, disco into something electronic, and by the end
you'd crossed half a century and two continents without ever feeling a jolt. Hence the
name: drop a frog into boiling water and it jumps; warm the water slowly and it never
notices.

It was not a recommendation engine. Recommendation engines are built to hand you more of
what you already like, and they're rather good at it, which is the problem — they keep you
where you are. Boil the Frog took you somewhere. The pleasure of it was watching the
music change underneath you while each individual step felt obvious.

Then it died. The small music-data company behind it was bought by Spotify, and in late
2024 Spotify shut the equivalent doors on everyone else too. The toy still loads. It just
doesn't work.

So we set out to rebuild it. Which meant answering the one question it had quietly
depended on, and never had to explain:

**How do you know which artists are similar?**

That turns out to be much harder, and much more interesting, than it sounds.

---

## The question is worse than it looks

Ask a room full of music lovers whether two artists are similar and you'll get an
argument, because at least three different questions are hiding inside that one.

*Do they sound alike?* Nick Drake and José González, maybe. *Do they come from the same
place?* Motown, Two-Tone, the Manchester of 1989. *Do the same people love both?* That
last one is a different question entirely, and it's the one that turns out to be
answerable, because it doesn't require anybody to have an opinion. It only requires
somebody to have been listening.

So the similarity underneath this whole project isn't "these two sound alike." It's
**"the same people play both."** Keep that in your pocket. It explains almost every strange
thing that happens later.

And it comes with a property that caused us months of trouble: **similarity isn't mutual.**
An obscure band from Leeds will happily be listed alongside Radiohead. Radiohead's own
listening data has never heard of the band from Leeds. Ask each of them who their
neighbours are and you get two entirely different answers. That is not a flaw in the data;
it is the shape of fame. But it means the "map" of music you're trying to draw is full of
one-way streets — and a one-way street, if you're trying to plan a journey through it, is
mostly a dead end.

---

## Part 1: Finding someone who was listening

You cannot compute similarity out of thin air. Somebody, somewhere, has to have observed
which artists go together. Our options, and what became of each:

**Spotify.** Closed. The relevant doors were shut to new applications in November 2024.

**Last.fm.** Works, and is genuinely good — but it's free *for non-commercial use only*.
If this ever earned a penny, that becomes a licensing problem at exactly the moment the
project starts making money. Ruled out not because it's bad, but because building on it
would set a trap for a future version of ourselves.

**Spotify's Million Playlist Dataset.** A million real playlists made by real people, which
would have been close to ideal. No longer downloadable, and research-only anyway.

**ListenBrainz.** An open, non-profit alternative that publishes artist-similarity data
into the public domain. They released it, pointedly, *in response to* Spotify closing its
doors. This is what we used, and it's what the whole thing runs on today.

---

## Part 2: How famous is famous? (or, how to waste a week)

Similarity alone isn't enough. Boil the Frog's real insight was that a good journey also
holds a **steady altitude of fame**. You don't want a route between two household names
that detours through somebody with four hundred listeners — that isn't a gentle
transition, it's a hole in the road. So we needed to know how well-known each artist is.

This took four attempts.

**One: just ask.** There's a way to look up an artist's listener count directly. It works.
It takes **twenty-three seconds per artist**. For seventy-five thousand artists that's
about three weeks of continuous asking. We only knew this because we timed it before
building anything on it; the estimate we'd written down beforehand was eight hours.

**Two: download the lot.** There are bulk downloads of raw listening history — a hundred
and ninety-one gigabytes of them. Before starting that download we grabbed a small sample
and looked inside. Of two hundred thousand listening records, **three in ten thousand**
identified the artist in a way a computer could reliably use. The rest were free text —
"beatles", "The Beatles", "beatles, the", every misspelling a human hand can produce.
Twenty minutes of looking saved a 191 GB download and days of processing.

**Three: borrow it from a neighbour.** Deezer publishes fan counts, and fan counts sound
like fame. We checked how well they predicted ListenBrainz popularity across 250 artists.
The answer was: essentially not at all.

That was the most instructive failure of the three, because Deezer's numbers aren't
*wrong*. They describe a **different audience**. Deezer is enormous in France and Brazil;
ListenBrainz skews Western, tech-literate, and a bit obsessive. An artist's standing in one
world says almost nothing about their standing in the other. Since our similarity data came
from ListenBrainz listeners, importing Deezer's fame rankings would have quietly blended
two different populations into one map — and nothing about the result would have looked
broken.

**Four: use the map itself.** In the end, fame came from the similarity data we already
had. If lots of other artists point at you, you're popular. It costs nothing to compute
and — the crucial part — it's measured on exactly the same population as the similarity.
No blending of worlds.

That was the right call. It also contains a landmine that took a year to go off, and
Part 6 is the story of it detonating.

---

## Part 3: Drawing the map

Picture seventy-five thousand dots, one per artist, with lines drawn between artists whose
listeners overlap. Four million lines — a number that later turned out to be roughly four
times too many.

Two things made this harder than it sounds.

**Nobody has a list of all the artists.** There is no downloadable roster of recorded
music. So we started from the thousand most-listened artists and walked outward: look up an
artist, see who they're connected to, add those to the queue, repeat. It's how you'd map a
city with no street plan — pick a few landmarks and walk every road out of them until you
stop finding new ones.

**And similarity isn't mutual**, as above. Our first answer to the one-way-street problem
was simply to make every connection two-way: if the band from Leeds claims Radiohead,
Radiohead now claims them back. Then we kept only the largest fully-joined region of the
map, so that a route is guaranteed to exist between any two artists we offer you — meaning
"no path found" can only ever be your own fault, never the map's.

That second decision was right and has never changed. The first was quietly wrong from the
very beginning, and Part 4 is the story of finding out.

Today's rule is stricter: **a connection survives only if each artist ranks the other among
their closest.** Mutual agreement, not one-sided assertion. Everything else is thrown away
before the map is drawn.

The result is a single file, held in memory, that a route can be found through in
milliseconds. No database. Finding the cheapest route through it is a solved problem — a
famous piece of arithmetic from the 1950s, where each step's price reflects how similar the
two artists are, how big a fame gap you're crossing, and a small toll per step to stop the
journey rambling.

That price list is going to matter enormously later. Hold on to it.

---

## Part 4: Seven ways to fool yourself

This is the interesting part.

### 1. Trusting our own eyes

The first real routes were beautiful. Miles Davis → Duke Ellington → Louis Armstrong →
Ella Fitzgerald → Frank Sinatra → … → Daft Punk. Jazz to electronica, every step adjacent
to the last. We declared victory.

We had no way whatsoever to tell a good route from a bad one. We simply liked that one.

### 2. Everybody's best friend

Buried in the code was a line that measured each artist's connections *relative to their
own strongest connection*. It sounds reasonable. It was catastrophic.

It meant every artist's best friend scored a perfect ten out of ten — whether the evidence
underneath was eleven shared listeners or eleven thousand. A thousandfold difference,
flattened into "identical." An unknown band's most tenuous acquaintance looked exactly as
strong as Radiohead's deepest bond.

Every measurement of quality we built on top of that was measuring a fiction.

### 3. Optimising the score instead of the thing

So we built proper measurements, and then had the computer tune the route-finder's
settings until those measurements were as good as they could be. It worked beautifully.
Every number improved.

Here is a route it produced:

> Miles Davis → J. K. Simmons → Hank Levy → Justin Hurwitz → Emma Stone → Daft Punk

Two of those are **actors**. The tuner had discovered that the cast and composers of
*Whiplash* and *La La Land* are tightly bound together in listening data — people who play
one play the others — and cheerfully routed a jazz journey straight through them.
Elsewhere it found something called `jesus2099`: not a musician at all, but a database
volunteer whose account had leaked into the list of artists.

The tuner did exactly what we asked. We had asked for the wrong thing.

### 4. The textbook cure that over-corrected

The standard remedy for the everybody's-best-friend problem is a well-known formula that
adjusts each connection by how much listening the two artists get overall. It stops famous
artists looking similar to everybody simply by virtue of being famous.

It over-corrected. Because it rewards connections that are *surprising* — two obscure
artists sharing listeners is more remarkable than two famous ones — it inflated tiny scenes
into significance. Ask it for a way out of Miles Davis and you got the cast of *La La Land*
again: Miles Davis, then an actor, then a composer, then another actor.

There's a real lesson in that pair of failures. Raw numbers over-favour the famous; the
textbook correction over-favours the obscure. The answer is somewhere in between, and
exactly where is a question you have to go and measure, not one you can reason your way to.

*(We did eventually measure it properly — a quarter of the correction, a half,
three-quarters, and none — and the answer came back **none**. Not somewhere in between
after all.)*

### 5. Blaming the mathematics for our own arithmetic

We concluded that the textbook formula was simply wrong for our data, and moved on.

A later review found what looked like the real culprit: we'd applied two adjustments in the
wrong order, so one silently cancelled the other. The formula was fine, we decided. *We*
weren't. We had blamed a well-established method for a bug of our own making, and very
nearly thrown out the right approach because of it.

A satisfying twist. Also wrong — see number seven.

### 6. Mistaking a symptom for a law of nature

Routes kept passing through the same enormous names. Radiohead turned up *everywhere*, the
universal junction through which all roads ran. We measured this, found that every
routing strategy did it — including the dumbest possible one, which reads no similarity
scores at all — and concluded it was simply the shape of the data. Unfixable. A law of
nature.

Then a second analysis reported that our similarity scores were themselves strongly tangled
up with fame — meaning what we'd been calling "similarity" was substantially a popularity
measure wearing a disguise. The route-finder wasn't drawn to the big names because of the
map's shape, we now concluded; it was drawn to them because we'd accidentally instructed it
to be.

We'd also taken a single experiment — run on the broken data, changing five things at
once — and promoted it to a principle. It didn't survive a clean test.

Nor, it turned out, did the correction.

### 7. The corrections were traps too

Numbers five and six are both wrong. We found out the way we found out everything else
here: by finally building the control experiment we should have built first.

**The fifth trap's diagnosis was impossible.** The ordering bug is real and still sits in
the code. But we went back and checked which version of the code had built which map file —
and the map that produced the bad routes was made *before* the bug existed. It cannot have
been the cause. We had four map files sitting in one folder with no record of what had
built them, and we had compared two that differed in **two** ways as though they differed
in one. Both conclusions built on that comparison collapsed.

**And the textbook formula was not fine after all.** The fourth trap had been right all
along: the standard correction really does over-correct on this data. The fifth trap
exonerated it on the strength of a bug that wasn't there, and came within a whisker of
shipping the film-soundtrack routes as an improvement.

**And the tangle between similarity and fame didn't reproduce.** Re-measured, it came out
far weaker — and it changed direction depending on which map we measured. Worse, it was
close to circular by construction: we *define* an artist's popularity as the sum of their
own similarity scores, so testing whether similarity correlates with popularity partly
tests whether a quantity correlates with itself. Finding a connection there is what you'd
expect if nothing were wrong at all.

So which was it — is the pull towards famous artists the shape of the data, or something we
did to ourselves? At that point: genuinely unknown, because the experiment that settles it
hadn't been run. (It has now. It's in Part 5, and it is not the end of the story either.)

The lesson isn't that the earlier reviews were careless. Each was a real improvement on the
one before, and each was believed *because* it was better. The lesson is narrower and more
annoying: **a measurement with no control is a story, and stories are very hard to stop
telling once they're written down.** Traps five and six both read as satisfying reversals —
the twist where the bug was ours all along, the twist where the law of nature was
self-inflicted. Satisfying is not the same as true.

We now keep every measured number in exactly one file, and every map records the version of
the code that built it.

---

## Part 5: Two real defects, and what happened when we fixed them

Two structural problems had been sitting on the list for months. Both were known, both were
genuinely wrong, and both were waiting for somebody to build the apparatus to settle them.

**The neighbour limit was applied at the wrong moment.** We capped each artist at fifty
connections — and then made everything two-way, which quietly added them all back. The cap
bounded nothing. Worse, it bounded the wrong people: it trimmed the obscure artists it was
meant to protect, while the famous ones ended up connected to almost everybody. A
configured limit of fifty produced artists with over eleven thousand connections.

**And a large share of routing decisions were free.** Connection strengths were squeezed
onto a nought-to-ten scale by a method that pinned everything above a certain threshold at
exactly ten. A perfect-ten connection costs the route-finder *nothing* to cross. Tens of
thousands of connections sat at that ceiling, so on a great many steps the route-finder was
choosing between options it considered identically free — a coin-flip in the costume of a
decision.

We fixed both. And here the story stops being a repair job.

### The fix that worked

Requiring **mutual agreement** — a connection survives only if each artist ranks the other
among their closest — fixed the cap properly. It's the only formulation that both limits
how connected an artist can be *and* stays even-handed about it. It is also brutal: it
deleted roughly three-quarters of the map, taking four million connections down to under a
million, while keeping almost all of the artists.

Deleting three-quarters of a map sounds like vandalism. It made the routes better, in two
separate blind listening tests. What it removed was overwhelmingly one-sided claims — the
band from Leeds asserting kinship with Radiohead that Radiohead's own listeners never
returned. Those aren't similarity. They're aspiration.

### The fix that made things worse

The ceiling fix worked too, in the sense that it did precisely what we designed it to do.
Rank the connections instead of scoring them and the ceiling vanishes entirely: no ties at
the top, no free steps, every routing decision an actual decision. The defect we'd been
complaining about for months, gone.

We built it, put it head-to-head against the version that still had the defect, and
listened to both without knowing which was which.

**The version with the defect won.**

We kept the defect. It is still in the code today, deliberately, and it is written into the
current phase's list as an unresolved problem rather than a solved one.

This remains the most uncomfortable result in the project, and we have no satisfying
explanation for it. The honest reading is that *"this measurement has an obviously wrong
property"* and *"fixing that property improves the product"* are two different claims, and
we had been treating them as one claim for months.

### The control experiment, finally

We ran the test that trap seven said was next: shuffle the whole map at random, keeping
every artist's *number* of connections exactly as it was, so that all genuine musical
community is destroyed but the shape of the crowd is preserved. Then see whether the
route-finder still gravitates to the big names.

It did. Just as much. Slightly more, in fact.

So **the sixth trap's original instinct was right all along** — for simple routing, the
pull towards famous artists really is the shape of the data, not something we told the
route-finder to do. The clever reversal that overturned it was itself wrong. That's three
layers: a naive reading, a sophisticated reversal of it, and a control experiment putting
the naive reading back.

But not cleanly, and this is the part that matters. Our *actual* route-finder — the one
with the full price list — seeks out big names considerably harder than the shuffled map
explains. There is a real excess, over and above the shape of the data, and the shuffle
experiment can't say why, because shuffling the map destroys the very scores that
route-finder depends on.

The lesson is not "we were right all along." It's that the original conclusion was right
**for reasons nobody had established at the time.** It was a lucky guess wearing the
clothes of a finding, and it took two reversals and a proper control to earn what we'd
already believed.

### The measurement that disqualified itself

The comparison that chose between six versions of the map scored them on a battery of
different measures, all planned in advance so we couldn't move the goalposts afterwards.

One family of measures — the ones that ask how much two artists' neighbourhoods overlap —
**gave opposite answers depending on which half of the test set we looked at.** Same
versions, same data, contradictory conclusions. That isn't a close result. It's an
instrument that cannot be trusted at the size of difference we were trying to detect.

The saving grace is that we noticed while it was pointing *against* the version we ended up
choosing. Had it flattered our preference, the temptation to accept it and move on would
have been considerable — and we'd never have learned the instrument was broken.

### And then the thing that actually decided it

The final choice came down to a blind listening session. Two identical copies of the app,
two different maps, no labels, one question: which gives better journeys?

The verdict was clear. It also had almost nothing to do with anything we had measured.

The difference showed up in the **reroll** — the "not for me" button that rebuilds the
journey around an artist you don't want. On first attempts, generated fresh, the two maps
were judged much of a muchness. It was only after four, seven, nine rerolls that they
diverged sharply: one kept opening up, growing longer, reaching genuinely unfamiliar
artists; the other just swapped one famous name for another famous name and stayed exactly
the same length no matter how hard it was pushed.

**Every measurement in the six-way comparison had looked at first attempts.** The entire
apparatus was pointed at the one part of the experience that turned out to be least
informative.

That's the third trap again — optimising the score instead of the thing — but wearing a far
better disguise. We hadn't chosen bad measurements this time. We'd chosen reasonable ones
and pointed them at the wrong moment in the listener's evening.

---

## Part 6: The day Radiohead disappeared

Every failure up to here was found by somebody being suspicious of a number. This one was
found by somebody being suspicious of a *name*.

During one of the blind listening sessions, the app reported that a particular journey
contained no big famous landmarks at all. The journey contained Kylie Minogue, Whitney
Houston, Prince and Paul Simon.

That gap — between what the measurement said and what a human being could plainly see —
was the loose thread. Pulling it revealed that our definition of "a big name" was *the
number of connections an artist has*, and by that definition Kylie Minogue isn't one. Which
led to the obvious next question: fine, then who *does* the map think is well-connected?

The Beatles had fewer connections than most obscure artists in the map. Fewer than the
typical artist, by a wide margin.

And Radiohead was not in the map at all.

Not poorly connected. **Absent.** Deleted. The band whose omnipresence was the founding
complaint of this entire project — "everything is Radiohead" — had vanished from our
seventy-five thousand artists, and nothing had noticed. Two hundred and nine automated
tests passed. Three expert code reviews had found nothing. Two rounds of specialist
analysis had found nothing. The map with Radiohead missing had *won a blind listening test*
and been adopted.

### How it happened

The cause is a chain of three individually reasonable decisions.

Remember the ceiling — the scoring method that pins everything above a threshold at exactly
ten out of ten. For an ordinary artist that affects a connection or two. For a
world-famous artist, *every single one* of their connections is up there in the flattened
band. All identical. All perfect tens.

Now ask that artist to keep only their fifty closest neighbours. There is no "closest" —
everything is tied. So the code fell back on its tiebreaker, which was to sort by each
artist's internal catalogue reference number: a meaningless string of letters and digits.
Fifty neighbours chosen essentially at random.

And then the mutual-agreement rule — the fix we were so pleased with in Part 5 — requires
the *neighbour* to have made the same arbitrary choice back. Two coin-flips, and both have
to land the same way. Usually they don't.

The Beatles won that coin toss a handful of times. Radiohead won it zero times, was left
connected to nothing at all, and was swept away when we trimmed the map to its largest
joined-up region.

There is an epilogue that makes it worse: the identifiers themselves aren't evenly
distributed, and famous artists tend to sit at the wrong end of the alphabet for a
tiebreaker that keeps the earliest ones. A coin toss that was already arbitrary may have
been quietly weighted against fame. That last part is measured but unverified, and we've
written it down as such.

### The fix, and what it didn't fix

The repair was small: choose your fifty neighbours by their *true* underlying strengths
before the flattening is applied, then flatten as before for the journey pricing. Decide
who your friends are using the real evidence; present the scores as you always did.

Radiohead is back, with a full complement of connections. So are The Beatles, Coldplay,
R.E.M. Famous artists' neighbourhoods are now genuinely their closest neighbours rather
than an alphabetical accident. And the map now *refuses to be built* if a handful of
canonical artists are missing or implausibly isolated — the check nobody had thought to
write, because nobody had imagined the failure.

But here is the thing about the fix: outside the top fraction of a percent of artists, it
changed almost nothing. The map's overall shape barely moved. Which was the first clue that
the real problem lived somewhere else entirely.

### The generalisable lesson

**The defect was found by a human comparing a measurement to his own perception of the
artists in the result, and refusing to let the discrepancy go.** No automated check could
have found it, because no automated check asserted that famous artists stay well-connected
— and nobody writes that check until the day it fails.

Ten minutes of a person looking at a list of names and saying *hang on* beat everything
else we had.

---

## Part 7: Three words we had been using as though they meant the same thing

Chasing the disappearance turned up something more embarrassing than the disappearance.
There were three different quantities in play, we'd been treating them as one, and each had
already caused a wrong conclusion.

**How connected an artist is, is not how famous they are.** Our "big name" measurement
counted connections. But the most-connected artists in the map turned out to be lo-fi,
synthwave and chiptune producers — musicians who exist mostly inside tight, mutually
devoted little scenes where everybody genuinely does list everybody. Meanwhile The Beatles,
connected to almost nobody after the coin-toss disaster, didn't count as a big name at all.
Every "this path avoids the famous artists" claim we'd made was really saying "this path
avoids members of tightly-knit micro-genres."

**And our popularity score is not fame either — not at the top.** Remember Part 2: an
artist is popular if lots of others point at them. It's an honest measure and it's measured
on the right population. But lo-fi and synthwave are *playlist* music. They accumulate
enormous co-listening. So a lo-fi producer and a Beatle score identically, and the score
cannot tell them apart.

We tested this the only way it can be tested. We took nine of the artists the map ranks
among its most popular and showed them, unlabelled, to the person the app is being built
for. The verdict: mostly unknown to him. Confirmed — our number for fame is not fame.

**And a drop in the popularity number is not a drop in fame.** This is the subtlest and the
most consequential. The popularity scores are crowded down at the bottom, so the famous
tenth of artists occupies *half the entire range* on its own. Which means you can take a
step that looks enormous by the number — a drop of half the scale from a superstar — and
land on somebody like Paul Simon. Enormous by the measurement; nothing at all by the ear.

Three currencies, freely exchanged, never reconciled. Each one had already produced a
confident conclusion that turned out to be about something other than what we thought.

---

## Part 8: The map wasn't the problem. The price list was.

With the currencies sorted out, we went back and asked the question the owner had been
asking all along, in the form he'd been asking it: *why is every artist you show me one I
already know?*

The measurement is stark. Across every journey judged in an entire listening test — three
starting pairs, every reroll depth, every version of the mechanism — **every single artist
offered in the middle of a journey sat in the top tenth by popularity.** The most obscure
artist the app offered anybody, anywhere in that test, was **Whitney Houston**. And when
one journey was deliberately pointed at an obscure destination, the route climbed *above*
its own destination's fame and stayed there until the last step.

Rerolling didn't help. Twenty rerolls, two different maps, two different strategies for
choosing whom to reject: flat. It never dipped.

The first explanation was structural, and it was wrong in an interesting way. Under the
mutual-agreement rule, famous artists are connected almost entirely to other famous
artists — and we concluded that no pricing scheme can route somewhere the roads don't go.

Then somebody checked whether the roads actually don't go there. **They do.** From The
Beatles, from Metallica, from Pink Floyd, from Taylor Swift, genuinely obscure territory is
**two or three steps away.** Not missing. Not distant. Two or three steps.

So the route-finder isn't failing to find the exits. It's reading the price and walking
past.

Here's the arithmetic that decides it. Every step costs a small toll, to stop journeys
rambling. Crossing a fame gap costs in proportion to the size of the gap. And a single dive
from a superstar down to somebody genuinely unknown costs about **two dozen ordinary steps'
worth of toll**. Faced with that, the route-finder does the sensible thing: it stays up on
the ridge among the famous, where every step is nearly free, and takes twenty-four cheap
steps rather than one expensive one.

It is behaving perfectly. It is doing exactly what we priced it to do. We had simply never
noticed what we'd priced.

There was even a safeguard meant to prevent this — a term that was supposed to push
journeys downward towards the unknown. It has never once fired, for the beautifully
circular reason that it only activates when a journey dips below a certain fame level, and
the fame-gap pricing prevents journeys from ever dipping. One defect wearing two faces.

**So the current work isn't about the map at all. It's about the price list.** And its
success can't be scored on our own popularity number, for all the reasons in Part 7 — it
has to be scored against fame as an actual person recognises it. Otherwise a "fix" could
satisfy us by routing from Metallica into synthwave: a colossal drop by the measurement,
and quite possibly indistinguishable from the current behaviour to the listener.

---

## Part 9: What we chose not to do

**Audio analysis.** Boil the Frog chose its *songs* partly by matching energy between
neighbours, so the playlist flowed sonically as well as conceptually. That data source is
dead with no free replacement. We lost something real here, and we know it.

**Teaching a machine its own private idea of similarity.** The modern approach is to let a
model place every artist as a point in an invented mathematical space and draw a straight
line between your two endpoints. It's elegant, and it's what a fresh team would probably
reach for. We stayed with the explicit map of who-is-near-whom because you can *interrogate*
it — when a journey looks strange you can ask why and get an answer, which matters for a
tool whose next ambition is explaining its own choices. Reading this essay, you may notice
that nearly every discovery in it came from being able to ask a map why.

**Cleverer route-finding.** We use the plain 1950s method. A more sophisticated variant was
considered and rejected: it would have doubled the speed of something already fast enough,
in exchange for subtle risks to correctness.

---

## Part 10: What actually worked

Seven habits, all learned the hard way.

**Measure before you build.** Every big decision here was settled by a cheap test that took
under an hour: timing a lookup, sampling a data file, checking 250 artists. Each one killed
an approach that would have cost days or weeks.

**Numbers and ears — never just one.** Judging by ear alone missed a systematic flaw for
weeks. Judging by numbers alone confidently endorsed a route-finder that produced actors.
Each catches what the other misses, and you need both every single time.

**Beware your own confounds.** Twice we drew a firm conclusion from an experiment that had
a bug or an uncontrolled variable in it, and both times built further reasoning on top
before catching it.

**Use the thing.** Three expert reviewers examined the code and found genuine problems.
Then somebody spent twenty minutes actually *using* the app and found the worst bug of the
project: the thirty-second clips are served from links that **expire after about an hour**,
while we were caching them for **thirty days**. Every clip quietly died and nobody noticed,
because the automated tests use pretend clips, and no amount of reading code will tell you
that a web address has a shelf life.

**Decide what counts as a win before you look.** The six-way comparison was written down in
advance — which measurements, which thresholds, what each possible outcome would mean.
That sounds bureaucratic right up until you are staring at a result you dislike. Twice in
this project a disappointing number was followed by an entirely reasonable-sounding
argument for gathering more evidence, and the only thing separating that from moving the
goalposts is whether the rule was fixed beforehand.

**Judge blind, and keep the judge ignorant.** For the deciding comparison the listener was
deliberately kept from knowing which version was which, what the numbers said, or what any
outcome would imply — and the verdict was written down and sealed before any of that was
revealed. This felt excessive. It stopped feeling excessive the moment the verdict came
back contradicting the numbers, because nobody could have been nudged, and so there was no
version of the argument in which the result got explained away.

**Trust the person who says "hang on, that's not right."** Radiohead's disappearance, the
dying clips, the discovery that our most "popular" artists were unknown to the person we're
building for — all three came from somebody looking at a result and finding it implausible.
Not one came from a test. It is the cheapest instrument we have and the only one that has
never yet been wrong.

---

## Where it stands

Seventy-five thousand artists. Under a million connections now, and better for it. Routes
in milliseconds. Journeys that mostly feel like the original — jazz drifting through soul
into hip-hop, black metal easing out into country over seven or eight steps.

Radiohead is back, along with everyone else the coin toss had swallowed, and the map now
refuses to be built if that ever happens again. Fixing it immediately exposed a problem
nobody had anticipated: now that the famous are properly connected to each other, asking
for Radiohead to The Beatles frequently produces a direct hop — a two-card "journey" with
nothing in between and nothing to discover. Which prompted a rule that had never needed
stating: **every journey must have at least one artist in the middle.** Otherwise there's
no journey, only a fact.

The open problem is the price list, and it is well understood: journeys stay up among the
famous because that's what we priced them to do, and the unknown is two or three steps away
the whole time, marked expensive. Retuning that is the work in front of us. The reroll
buttons lead, because rerolling is where the whole experience is actually decided — and
because we have exactly one trustworthy measurement of it, which is a person's opinion.

The clips still expire. The interface still has a handful of things that only reveal
themselves in use.

And one thing we have learned to be careful about: **the quality that decides every verdict
is coherence** — whether each step feels like a sensible move from the last — and we cannot
measure it. Not for want of trying. The two measurements we built specifically to guard
coherence turned out to be the *worst* predictors of what the listener actually chose. What
we have instead is his own language: *"The Shins to The White Stripes feels like a leap that
should have a step in between"* — and the winning version inserted The Flaming Lips exactly
there. *"It feels like it got gravitationally pulled towards a famous name around step three
or four, then had to fight its way back."* Those sentences are currently a better
specification than anything numerical we own.

---

## Why any of this is interesting

The honest summary is that **"which artists are similar?" has no correct answer.** There is
only a series of defensible choices, each with a failure mode you will not see until you
look for it in the right way.

Choose "sounds alike" and you need somebody to define what that means. Choose "the same
people listen to both" — as we did — and you inherit the shape of who happens to be
listening, which is not the same as the shape of music. You get lo-fi producers ranked
alongside The Beatles, because playlists are where lo-fi lives. You get the cast of a film
bound tightly together, because people who watch a film play its soundtrack. Neither of
those is an error in the data. They're both true facts about listening that simply aren't
facts about *music*, and no amount of cleverness downstream can separate them.

There's a broader thing here about taste, too. The reason the pull towards the famous is so
hard to escape isn't a bug we introduced — it's that fame is genuinely, structurally the
middle of the map. Everybody is near a famous artist. Famous artists are near each other.
The whole terrain slopes upward toward the household names, and a journey that doesn't
actively fight that slope will roll to the top and stay there. Which is, more or less, an
account of how popular culture works, discovered accidentally by a route-finder trying to
get from Miles Davis to Daft Punk.

And the running joke of this document is that every round of checking has itself needed
checking. Seven traps became a trap about the corrections to the traps, which became a
correction to *that*, which became a year-long conviction that we had a map problem when
what we had was a pricing problem. We are not getting better at being right the first time.
We are getting better at finding out sooner.

Most of the work, it turns out, was never building the thing. It was finding out what we'd
got wrong, and being willing to look.
