# r1-outside — ideas from outside (EXPLORATORY, not evidence)

## Literature, half a page
- **RP3beta** (Christoffel, Paudel, Newell, Bernstein, RecSys 2015; [paper](https://dl.acm.org/doi/10.1145/2955101), [ZORA](http://www.zora.uzh.ch/id/eprint/131338/)).
  It is a random walk over an item graph where each step's probability is divided by the popularity of the
  item it lands on, raised to a power β. It lifts long-tail items at almost no cost in accuracy. The same
  move on our map is "a stop costs β·(how famous it is)", with β rising with each press.
- **Hubness / Mutual Proximity** (Schnitzer, Flexer, Schedl, Widmer, JMLR 2012; [pdf](https://jmlr.org/papers/v13/schnitzer12a.html)).
  In music-similarity spaces a few "hub" items turn up as everyone's near neighbour. Their fix rescales each
  similarity by how unusual it is for both endpoints. That maps directly onto our saturated 1.0 edges
  between famous artists.
- **Flexer et al., "Playlist generation using start and end songs"** (ISMIR 2008; [pdf](https://ismir2008.ismir.net/papers/ISMIR2008_143.pdf)).
  Their start-to-end playlists have a **fixed number of songs**, and the songs in between move gradually
  from the start song towards the end song. The idea taken from it: fix the length, so a router cannot
  dodge a penalty by skipping stops.
- **Celma, "Music recommendation and discovery in the long tail"** (PhD 2008; [pdf](http://www.mtg.upf.edu/static/media/PhD_ocelma.pdf)).
  Treats the artist-similarity network and popularity together, and has the user navigate from the head
  (the famous artists) down into the tail (the little-known ones) one similar step at a time. The idea
  taken from it: replace the pressed artist with a similar, less famous one.
- **Abdollahpouri et al., popularity-bias re-ranking** (xQuAD; [arXiv 1901.07555](https://arxiv.org/abs/1901.07555)).
  Re-ranks a finished list after it is built. It is mostly about fairness in lists, and I did not port it.
- **BoilTheFrog** (`docs/superpowers/findings/2026-07-27-boilthefrog-source-review.md`). Its famous artists
  have only about four connections each, so a route has almost nowhere to go through them. It solves our
  problem by deleting the structure, which we cannot copy.

## What I tried (20 kit pairs; press the most famous middle artist each time)
| file | idea | result |
|---|---|---|
| `v0_copycheck.py` | my copy of the router, with no penalty | reproduces today's journeys exactly (no journey differs at any press); a check that the copy is faithful |
| `v1/v2_rp3_*.py` | pure RP3beta: cost = −log(sim / the artist's total similarity) + β·k·log(popularity) | **kill**. Journeys shrink to about 5 artists with weak links (weakest step 0.3–0.5), and famous pairs barely move (98→96) |
| `v3_todaypen_b03.py` | today's cost + 0.3·k·log(degree) | **kill**. Degree tops out at 50, so it cannot tell a superstar from a mid-level artist. The router pays the penalty by **cutting stops** (8→5.5 artists), not by choosing obscure ones |
| `v4/v5_mp*.py` | Mutual Proximity rescaling of similarity | **kill**. Even the first journey gets weaker (weakest step 0.98→0.84), and fame does not move after presses |
| `s0/s1/s2_splice*.py` | Celma-style: swap only the pressed artist for a less famous artist who links both of its neighbours | **kill**. Two famous neighbours almost never share a less famous neighbour, so it falls back to today's router nearly every time. This is the map's "most similar neighbour is more famous" property again |
| `v6/v7_todaypen_fame_*.py` | today's cost + β·k·(−log(1 − fame percentile)) | **moves fame**. A penalty in fame currency separates the top 1% where degree cannot. But journeys still shorten (8→6 artists) |
| `f1..f5` (`fixedlen.py`) | **fixed-length journey + the fame penalty above.** Press 0 is today's journey; from press 1 the journey must have at least as many stops as at press 0 (up to 2 more). Found with a layered search that never steps straight back | **promising**. See below |

Changing the penalty's currency from degree to fame percentile did most of the work. Fixing the length
added a little: at press 3 it gave slightly lower fame and slightly better coherence than the same penalty
without it (`f3` vs `v7`). A similarity floor of 0.7 on every step (`f5`) was what held coherence.
The floor is my addition, not from the literature: the rater marks about 35–44% of steps below similarity
0.8 as a stretch or worse, against 20% above 0.9 (`simvsrating.py`).

## Best variant: `f5_fame_b015_sim07.py` (fixed length, β = 0.15 per press on −log(1 − fame percentile), no step weaker than 0.7)
| press | fame of middle artists, famous pairs | mid pairs | length | weakest step | share of middle artists in the top 10% | coherence | steps rated a stretch or worse |
|---|---|---|---|---|---|---|---|
| today 0 | 99.5 | 98.9 | 8.1 | 0.98 | 94% | 0.65 | 25% |
| today 3 | 99.3 | 98.6 | 8.1 | 0.98 | 97% | 0.68 | 19% |
| today 5 | 99.6 | 97.0 | 7.5 | 0.94 | 98% | 0.68 | 21% |
| today 10 | 99.3 | 98.0 | 7.2 | 0.92 | 99% | 0.67 | 23% |
| f5 3 | 90.2 | 68.0 | 8.2 | 0.77 | 54% | 0.68 | 22% |
| f5 5 | 88.6 | 59.4 | 8.3 | 0.74 | 53% | 0.68 | 18% |
| f5 10 | 81.0 | 35.7 | 8.3 | 0.71 | 45% | 0.65 | 26% |

The same design without the floor (`f4`, β = 0.15): at press 3, 90.2 / 0.67 / 26% bad; at press 10, 66.5 / 0.63 / 30%.
Gentler (`f3`, β = 0.1): 92.5 / 0.65 / 29% at press 3.

### Examples (f5; fame percentile in brackets)
- **Explosions in the Sky → Sepultura**
  - Press 0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82) > Ghost (96) > Gojira (98).
  - Press 10: Random Forest (56) > Those Who Ride With Giants (46) > Silent Island (48) > CLANN (47) > Kalandra (54) > SKÁLD (56) > Wind Rose (66) > Powerwolf (92) > Amon Amarth (99).
  - The press-10 journey goes from post-rock through dark folk into folk-metal and on to death metal. A listener can follow it.
- **Lupe Fiasco → Kid Rock**
  - Press 0: John Legend > Mariah Carey > TLC > Alanis > Third Eye Blind > Silverchair > Chris Cornell (all 99–100).
  - Press 10: Ab-Soul (92) > Childish Major (51) > Landstrip Chip (20) > Cozz (56) > Prof (63) > Chris Webby (75) > Rittz (72).
  - It becomes an underground-rap descent, rated 3,3,2,2,2,2,3,2.
- **The O'Jays → Midnight Oil**
  - Press 0: Earth, Wind & Fire > Phil Collins > INXS.
  - Press 10: The Brothers Johnson (88) > The Lively Ones (97) > The Atlantics (77) > The Masters Apprentices (29) > Cold Chisel (84) > The Superjesus (71).
  - Mostly surf rock and then Aussie rock. One step is rated jarring: Brothers Johnson > Lively Ones.

Failures to know about:
- With β = 0.3 (`f2`) the drop is far too fast, and some journeys cross through Lithuanian or Ukrainian pop.
- Even in f4 and f5, Pete Townshend → Silverstein wanders (Vince Clarke > Linnea Olsson …).
- Anastacia → Mungo Jerry detours through Eurovision.
- Famous pairs level off around the 81st–92nd percentile after press 3.

## For round 2
1. Combine **a fame-currency penalty (RP3beta-style, −log(1 − percentile))**, **a floor on step similarity**
   and **a guard on journey length**. Fix the length or use a stop quota, but never let the penalty be paid
   by cutting stops. I did not test the similarity floor without the fixed length (the 0.7 floor on
   today's router plus the fame penalty). That control would show whether fixing the length is needed.
2. When there is no simple path of that length, `fixedlen.py` drops the similarity floor first and then falls
   back to Dijkstra. Aged in Harmony → Tilman Sillescu fell to 7 artists at press 10 this way. The number
   of fallbacks is not counted.
3. The layered search takes about 2–5 s per journey in numpy on a loaded machine. That is fine for exploring,
   but it would need work before it could be served.
4. β between 0.1 and 0.15 per press and the floor between 0.7 and 0.75 are worth a small sweep. Another
   option is a ceiling that falls with each press, so fame keeps dropping after press 5.
