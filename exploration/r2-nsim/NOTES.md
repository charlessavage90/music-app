# r2-nsim — fix the similarity, then dig (EXPLORATORY, not evidence)

Pairs: only the kit's 20. Press 0 is today's router in every variant.

## The finding that drove everything
"How many of their similar-artist lists do two artists share" (shared-neighbour overlap) predicts the
coherence screen better than the raw similarity score or r1-search's fame-neutral score. It also works
among famous artists, where the raw score is saturated and predicts nothing. Measured on 8.8k cached
step ratings, then re-checked on 13k:
- steps whose two artists share < 2 % of neighbours: 46 % rated a stretch or worse;
- steps sharing 20–30 %: 14 %.

This holds regardless of the raw score. A link with raw score ≥ 0.9 but overlap < 2 % is still rated
a stretch 38 % of the time. Overlap does not depend on fame: the median is ~0.15 from the bottom 5 %
to the top 1 %.

Junk links have near-zero overlap: Louis Prima → BROCKHAMPTON is raw 1.0, fame-neutral 1.0,
overlap 0.04. So **fame-neutral similarity does not remove junk edges; overlap does.** Fail-check:
random non-linked pairs average 0.0004 (`probe_ratings.py`, `probe_jac.py`, `probe_junkedge.py`).

## What I tried (one line each)
- **Overlap added to r1-search's soft ceiling (falling target from the less famous endpoint):**
  killed. Coherence was fine, but famous pairs stayed at 98–99: the famous cluster has the highest
  overlap.
- **Much stronger soft charge:** digs (35 at press 10), but some famous pairs **rebound** to
  all-famous journeys. With a per-artist charge, three famous middle artists cost less than eight
  artists on a slow descent. Killed as a soft-only design.
- **Journey-shaped soft ceiling by graph distance:** too loose, because famous pairs are only 2–4
  hops apart. Killed.
- **Hard journey-shaped ceiling, 10 points per hop (r1-rules v7 shape) plus overlap:** plateaus at
  ~71–78, like v7. Too gentle.
- **Hard journey-shaped ceiling, 20 points per hop, soft pull, band floor: the design that works.**
  Artists next to an endpoint may be as famous as it. The allowance drops 20 points for each hop
  further in. No rebound.
- **"One famous bridge per journey" at genre seams:** killed. It chose the bridge too often (famous
  pairs back to 78 by press 10) and took 4.6 s.
- **Anchoring the target on the pressed artist, not the less famous endpoint:** fixes the mid-pair
  crash at press 1 (72 instead of 23). Each press takes the target to min(previous target, pressed
  artist's fame) minus 8 points, and never lower than half the less famous endpoint. It is stateless,
  so it ratchets.
- **Pull toward stand-ins:** artists that are not close, less famous neighbours of the pressed artist
  pay a small charge. It raised "the pressed artist's replacement is similar and less famous" from 28 %
  to 42–48 %, still below today's 62 %.
- **Extra charge on links sharing < 5 % of neighbours:** fame unchanged, fewer bad steps late.
  Louis Prima → BROCKHAMPTON disappeared.
- Junk floor (charge below the 5th percentile) and a length guard (a longer-than-11 journey pays
  extra per hop, never gets a higher ceiling): kept; each is small.
- Not done: nsim with r1-rules v7's position-in-journey layering. The graph-hop version (above)
  covered the idea at a tenth of the cost.

## Table (rated; famous-pair middle fame / mid-pair middle fame / length / coherence / bad steps)
| press | today | **A: dig_overlap** | **B: dig_overlap_gentle** |
|---|---|---|---|
| 0 | 99.5 / 98.9 / 8.1 / .65 / 25% | same | same |
| 1 | — | 87.4 / 71.5 / 7.7 / .70 / 23% | 92.3 / 71.5 / 7.6 / .70 / 24% |
| 3 | 99.3 / 98.6 / 8.1 / .68 / 19% | 70.3 / 53.3 / 8.8 / .70 / 22% | 77.7 / 55.4 / 8.7 / .72 / 18% |
| 5 | 99.6 / 97.0 / 7.5 / .68 / 21% | 58.4 / 29.8 / 8.8 / .67 / 27% | 68.1 / 41.4 / 9.2 / .69 / 22% |
| 10 | 99.3 / 98.0 / 7.2 / .67 / 23% | 53.1 / 17.8 / 9.5 / .65 / 25% | 59.3 / 27.3 / 9.6 / .64 / 27% |

- Top-10 % share at press 10: A 24 %, B 23 % (today 99 %). Famous artists are reduced, not gone.
- Similar-and-less-famous replacement: A 39 %, B 48 % (today 62 %). The check's fail-check scores
  0 %.
- Routing: median 0.13 s, max 2.8 s.

Runs: `A2_R.txt` / `G2_R.txt`. Earlier rated: `e8_l11_R.txt`, `A_R.txt`, `G_R.txt`. Five rated runs
in all.

## Examples (A; fame percentile in brackets; the rater's 0–3 per step)
- **Explosions in the Sky → Sepultura**
  - p0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82)
    > Ghost (96) > Gojira (98).
  - p10: sleepmakeswaves (93) > Meniscus (79) > Bossk (83) > Conjurer (45) > Birds in Row (82)
    > Code Orange (82) > Power Trip (74) > Havok (82) > Sodom (96). Steps 3322221333: post-rock
    into sludge, hardcore, thrash.
- **The O'Jays → Midnight Oil**
  - p0: Earth, Wind & Fire > Phil Collins > INXS (99–100).
  - p10: The Impressions (97) > Archie Bell & the Drells (60) > Darrell Banks (72) > Billy Butler (52)
    > Nancy Ames (48) > S.F. Seals (28) > Chain Gang (46) > The Psycho Surgeons (42)
    > The Celibate Rifles (54) > The Meanies (27) > Magic Dirt (73) > The Superjesus (71).
    Northern soul into Aussie punk. One seam (Nancy Ames > S.F. Seals, rated 0). Long, at 14 artists.
- **Too $hort → The Wallflowers**
  - p0: Ice Cube > Busta Rhymes > Nelly > TLC > Alanis > Barenaked Ladies (99–100).
  - p10: G-Eazy (90) > Marc E. Bassy (69) > Christian French (55) > Jake Scott (45)
    > Nathan Angelo (68) > O.A.R. (96). Steps 2322223.
- **Failure: Louis Armstrong → Ozzy Osbourne.** At p10 it is back to Michael Bublé > Meghan Trainor
  > Ava Max > BTS > … > Def Leppard (88–100). The ceiling was blocked and relaxed for the whole map,
  the same failure r1-rules named. Also Compton's Most Wanted → Alabina p10 (steps 330030222) and
  Emscherkurve 77's 13-artist chain at the 7–14th percentile.

## Verdicts
- **A `dig_overlap.py`: promising, finalist.** It is visibly less famous by press 3 (70) and
  keeps going (53 at press 10, past round 1's 78–86 plateau). Coherence holds at or above today at
  every press. The costs are +1.5 artists of length and weaker replacements than today.
- **B `dig_overlap_gentle.py`: promising, finalist.** It is the smoother, more familiar version: 78 at
  press 3, 59 at press 10, bad steps ≤ 24 % through press 8, 48 % replacements. The mid-pair floor
  holds better (27 at press 10).
- Killed: soft ceiling alone (rebound), graph-hop soft shaping, 10-point hard shaping (plateau),
  single famous bridge (too famous, too slow).

## For the coordinator
- Both finalists import `r2nsim_core.py` from this folder. Its module name is unique, and state is
  kept on ctx under per-file keys, so it can sit beside r1-search's `common.py` in the practice room.
  First use per process computes neighbour overlap for all 2.5 M links (~2–5 s).
- Overlap belongs in the formal track's edge price whatever happens to Dig deeper. It is the one
  signal here that explains the screen among famous artists.
- Open: (1) blocked → global relax still lets stars back (Louis Armstrong p10); relax only near the
  bottleneck. (2) Replacements are 39–48 % against today's 62 %. (3) Mid pairs still reach 18–27 by
  press 10, which is below both endpoints, though not at presses 1–3. (4) The exit step from a famous
  endpoint into the obscure world is the commonest remaining bad step.
- Caveat: later cached ratings include steps my overlap-priced runs chose. The overlap finding was
  first established on the 8.8k ratings cached before this work.
- Exploration machinery: `eng.py` (env-driven, all the killed modes), `sweep.py` (overrides for the
  core), `proxy.py` (unrated early warning: share of low-overlap steps; tracked the rated result on
  every run checked), `run.sh` / `runv.sh` / `sum.sh`.
