# How Do You Know Which Artists Are Similar?

*Notes from rebuilding a dead music toy.*

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

**What this is.** A short narrative account of the journey, written for a non-technical
reader who wants to understand *how the thinking went*. It is an article, not an archive:
**keep it under about 2,000 words.** The detailed accounting lives in the execution logs.

**What this is not.** Not a ledger, not a changelog, not a status report. If an update
reads as "and then we did X, then Y, then Z," it belongs in the execution log. This
document only wants X, Y or Z if one of them **changed the direction** or **taught us
something we had believed wrongly** — and even then, only the two or three best examples
of each. We have made far more mistakes than belong in one essay.

**How to update it.** Not by appending. A phase of work usually invalidates something
already written here, and the honest version requires revising it — a prediction that
didn't survive, a conclusion overturned. **Expect to edit the middle, and to cut
something old to make room.**

**Two standing rules.** Keep measured figures approximate and point at the authoritative
record for the real ones — precise numbers restated here drift and then mislead. And
preserve the failures: the wrong turns are the substance of this document, and a revision
that quietly tidies one away destroys the only thing it is for.

</details>

---

## The toy that disappeared

There was a small, perfect thing on the internet called **Boil the Frog**. You gave it two
artists — Miles Davis and Daft Punk, say — and it built a playlist that walked from one to
the other. Every step was a small move from the last, and by the end you had crossed fifty
years and half a dozen genres without a jolt.

It was not a recommendation engine. Those give you more of what you already like, which is
precisely their limitation: they keep you where you are. Boil the Frog moved you somewhere.

The company behind it was bought by Spotify, and in late 2024 Spotify closed the same doors
to everyone else. Rebuilding it meant answering the question the toy had never needed to
explain: **how do you know which artists are similar?**

## The question is harder than it sounds

Three questions hide inside that one. Do they sound alike? Do they come from the same
scene? Do the same people listen to both? Only the third can be answered at scale, because
it requires nobody to hold an opinion — only for people to have been listening. So the
similarity underneath this project is *the same people play both*, not *these sound alike*.
That choice explains most of what follows.

It also carries a property that cost us months: similarity is not mutual. An obscure band
from Leeds sits in the data alongside Radiohead; Radiohead's own listening data has never
heard of them. That is not a flaw — it is what fame looks like from below. But it fills the
map with one-way streets, and a one-way street is a dead end if you are planning a journey.

## What we built

The data comes from **ListenBrainz**, an open non-profit archive that publishes artist
similarity into the public domain — released, pointedly, in response to Spotify closing its
doors.

We also needed to know how well known each artist is, because a good journey holds a steady
altitude of fame: a route between two household names should not drop through somebody with
four hundred listeners. We tested Deezer's published fan counts and found no relationship to
our data at all — not because Deezer is wrong, but because it describes a **different
audience**, enormous in France and Brazil where ours skews Western. Importing those numbers
would have blended two populations into one map, and nothing about the result would have
looked broken. So fame came from the map itself: an artist is popular if many others point
at them, measured on exactly the population the similarity came from. That was the right
call, and it contained a landmine that took a year to go off.

There is no list of all recorded artists to download, so we started from the thousand
most-listened and walked outward. Seventy-five thousand artists, four million connections —
about four times too many. The rule that fixed the one-way streets is that **a connection
survives only if each artist ranks the other among their closest**: mutual agreement, not
one-sided claim. It deleted three-quarters of the map and made the journeys better in two
blind listening tests. What it removed was aspiration rather than similarity.

A route through what remains takes milliseconds to find. Each step is priced: how similar
the two artists are, how large a gap in fame you are crossing, and a small toll per step to
stop the journey rambling. Remember the price list.

## How we fooled ourselves

The first routes were beautiful. Miles Davis through Ellington, Armstrong, Fitzgerald,
Sinatra and out to Daft Punk, every step adjacent to the last. We declared victory. In fact
we had no way to tell a good route from a bad one. We simply liked that one.

So we built proper measurements and let the computer tune the route-finder until those
measurements were as good as they could be. Every number improved. Here is a route it
produced:

> Miles Davis → J. K. Simmons → Hank Levy → Justin Hurwitz → Emma Stone → Daft Punk

Two of those are actors. The tuner had discovered that the casts and composers of
*Whiplash* and *La La Land* are tightly bound together in listening data, and routed a jazz
journey straight through them. It had done exactly what we asked.

Rounds of correction followed, and each needed correcting in turn. Twice we diagnosed a
cause with confidence and were wrong, having compared two versions of the map that differed
in two ways while believing they differed in one. **A measurement with no control is a
story, and a satisfying story is very hard to give up once it is written down.**

One of those corrections matters for what comes next. Connection strengths were squeezed
onto a fixed scale by a method that pins everything above a threshold at the maximum, and a
maximum-strength connection costs the route-finder nothing to cross — so tens of thousands
of steps were free, and many decisions were being made by coin-flip. We built the fix,
which removes the ceiling entirely, and tested it blind against the flawed version.

The flawed version won. We kept the flaw, and it is still there today, deliberately. *This
measurement has an obviously wrong property* and *fixing it will improve the product* are
different claims, and we had spent months treating them as one.

## The day Radiohead disappeared

Every problem so far was eventually caught by a measurement. This one was invisible to every
measurement we had, and was caught by a person reading a list of names.

During a blind listening session the app reported that a particular journey contained no
famous artists at all. The journey contained Kylie Minogue, Whitney Houston, Prince and
Paul Simon.

That gap — between what the measurement said and what a person could plainly see — was the
loose thread. Pulling it showed that our definition of "famous" was *the number of
connections an artist has*, and by that definition Kylie Minogue is not famous. Which
raised the next question: then who does the map think is well connected?

The Beatles had fewer connections than a typical obscure artist. And Radiohead was not in
the map at all. Not poorly connected — **absent**. The band whose omnipresence was the
founding complaint of the entire project had vanished from seventy-five thousand artists,
and nothing had noticed: two hundred automated tests passed, three expert code reviews and
two rounds of specialist analysis found nothing, and the map without Radiohead had *won a
blind listening test* and been adopted.

The cause was three reasonable decisions in a row. Recall the ceiling that pins strong
connections at the maximum: for an ordinary artist it affects a connection or two, but for
a world-famous artist *every* connection sits up there, all identical. Now ask that artist
to keep only their fifty closest neighbours. There is no closest — everything is tied — so
the code fell back on its tiebreaker, which sorted by each artist's internal catalogue
reference, a meaningless string of letters and digits. Fifty neighbours chosen at random.
And the mutual-agreement rule requires the neighbour to have made the same arbitrary choice
back: two coin-flips, both of which must land the same way.

The Beatles won that toss a handful of times. Radiohead won it never, was left connected to
nothing, and was swept away when we trimmed the map to its largest joined-up region.

The repair was small: choose your fifty neighbours on the true underlying strengths, before
the flattening is applied. Radiohead is back with a full complement of connections, as are
The Beatles, Coldplay and R.E.M. The map now refuses to be built at all if canonical artists
are missing or implausibly isolated — the check nobody had thought to write, because nobody
had imagined the failure.

**The defect was found by a human comparing a measurement against his own knowledge of the
artists in front of him, and refusing to let the discrepancy go.** No automated check could
have caught it, because no automated check asserted that famous artists stay well connected
— and nobody writes that assertion until the day it fails.

## Three quantities we had been treating as one

Chasing that defect turned up something more uncomfortable than the defect.

**How connected an artist is, is not how famous they are.** The most connected artists in
the map turned out to be lo-fi, synthwave and chiptune producers, who live in tight scenes
where everybody genuinely does list everybody. Every claim we had made about a route
"avoiding the famous" was really about avoiding members of small devoted genres.

**Our popularity score is not fame either, at the top.** An artist is popular if many
others point at them — honest, and measured on the right population. But lo-fi is *playlist*
music and accumulates enormous shared listening, so a lo-fi producer and a Beatle score
alike. We tested this the only way it can be tested: we showed nine of the map's
highest-scoring artists, unlabelled, to the person the app is being built for. Mostly
unknown to him.

**And a fall in that score is not a fall in fame.** The scores crowd at the bottom, so the
famous tenth of artists occupies half the range on its own. Step down from The Beatles by
what the number calls half the scale and you land on Paul Simon.

## The map was not the problem. The price list was.

With the vocabulary sorted out, the original complaint could finally be measured: *why is
every artist you show me one I already know?*

Across an entire listening test — every pairing, every reroll — every artist offered in the
middle of a journey sat in the top tenth by popularity. The most obscure artist the app
offered anybody, anywhere, was **Whitney Houston**. Twenty consecutive rerolls never dipped
below that band.

The first explanation was structural: famous artists are connected mostly to other famous
artists, so the roads out to obscurity are not there. Then somebody checked whether they
were really missing. They are not. From The Beatles, from Metallica, from Taylor Swift,
genuinely obscure territory is **two or three steps away**.

The route-finder is not failing to find the exits. It is reading the price and walking past.
A single dive from a superstar to somebody unknown costs about two dozen ordinary steps'
worth of toll, so it stays up on the ridge among the famous, where every step is nearly
free. It is behaving exactly as we priced it. We had never looked closely at what we had
priced.

That is the work in front of us, and it cannot be judged by our own popularity score: a
"fix" could satisfy that number by routing from Metallica into synthwave — a colossal drop
by the measurement, and no discovery at all by ear.

## Where it stands

Seventy-five thousand artists, under a million connections, routes in milliseconds. Most
journeys feel like the original: jazz drifting through soul into hip-hop, black metal
easing out into country over seven or eight steps.

Repairing Radiohead exposed something nobody had anticipated. Now that famous artists are
properly connected to one another, Radiohead to The Beatles is often a single hop — a
two-card journey with nothing in between and nothing to discover. Which forced a rule that
had never needed stating: every journey must contain at least one artist in the middle.
Otherwise it is not a journey, only a fact.

The quality that decides every verdict is **coherence**, whether each step feels like a
sensible move from the last, and we cannot measure it. The two measurements we built
specifically to guard coherence turned out to be the worst predictors of what the listener
actually chose. What we have instead is his own language: *"The Shins to The White Stripes
feels like a leap that should have a step in between"* — and the winning version put The
Flaming Lips exactly there. That sentence is a better specification than anything numerical
we own.

**"Which artists are similar?" has no correct answer** — only defensible choices, each with
a failure mode you will not see until you look for it the right way. Choose *the same people
listen to both* and you inherit the shape of who happens to be listening, which is not the
shape of music: lo-fi producers rank beside The Beatles, and the cast of a film binds
tightly together. Both are true facts about listening that are not facts about music.

The pull towards the famous is not something we introduced either. Fame is structurally the
middle of the map — everyone is near a famous artist, and famous artists are near each
other — so the terrain slopes upward towards the household names, and a journey that does
not fight that slope rolls to the top and stays there. Which is a fair description of how
popular culture works, arrived at accidentally by a route-finder trying to get from Miles
Davis to Daft Punk.

We are not getting better at being right the first time. We are getting better at finding
out sooner.
