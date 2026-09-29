# r1-search — a different search for Dig deeper (EXPLORATORY, not evidence)

## What I tried (press 0 is today's router in every variant)
- **splice** (`splice.py`): treat a press as a local repair. The pressed artist is swapped for a 1–2 artist bridge between its two neighbours, and the rest of the journey is kept. **Killed.** Around famous artists there are no short bridges through less famous ones. With a replacement allowed to be as famous as the pressed artist, it replaced a 100 with a 99. When I required the replacement to be at least 10 or 20 points less famous, no bridge was ever found and it fell back to today's route.
- **localwp** (`localwp.py`): the same idea with an unlimited bridge. It picks an obscure stand-in near the pressed artist's slot and routes through it. **Killed.** Journeys grew to about 29 artists by press 10, and the detours kept visiting the same few connector artists.
- **diverse** (`diverse.py`): generate 15 near-cheapest journeys under today's cost (a penalty is added to artists already used), then pick the one whose middle artists are least famous. **Killed.** Every near-cheapest journey is famous. Middle-artist fame for famous pairs stayed at 97–98 through press 10.
- **waypoint** (`waypoint.py`): pick one obscure artist w, below a fame target that falls each press. w must sit near the middle of A→B and near the pressed artist. Then route A→w→B, with a penalty on artists above the target. With raw similarity it moves fame, but the waypoint is nearly always one of a handful of "connector" artists. salvia palth appeared in 13 of 20 pairs, followed by Machine Girl, clipping., Ho99o9 and BROCKHAMPTON, which gave jumps like Louis Prima > BROCKHAMPTON. **Killed with raw similarity.**
- **Fame-neutral similarity** (common.py `nsim`): the most useful thing I found. Similarity scores depend on fame. A top-1% artist's links score about 1.0, while a bottom-20% artist's best link is only about 0.5. My fix scores each link against the weaker end's own best link. With it, the connector funnelling disappears: no artist appears in more than 3 of 20 pairs. **Promising.**
- **waypoint + nsim** (best waypoint variant): moves fame, and coherence drops moderately (numbers below).
- **softceil + nsim** (`softceil.py`, a control with no special search, only a cost that falls with presses): it matches waypoint+nsim on fame and on coherence, and it is 3× faster. **So the search structure added nothing. The lever is fame-neutral similarity plus a falling fame target.**
- **Relative schedule** (target = the previous journey's middle fame minus 0.08): **killed.** It has no ratchet, so a famous route comes straight back on the next press. Famous pairs stayed at about 98 through press 10.

## Table (famous-pair middle fame / mid-pair middle fame / length / weakest link / top-10% share / coherence / bad steps)
| press | today | waypoint+nsim | softceil+nsim |
|---|---|---|---|
| 0 | 99.5 / 98.9 / 8.1 / .98 / 94% / .65 / 25% | same | same |
| 3 | 99.3 / 98.6 / 8.1 / .98 / 97% / .68 / 19% | 93.0 / 32.9 / 8.2 / .58 / 63% / .61 / 31% | 92.5 / 19.5 / 6.9 / .61 / 57% / .63 / 29% |
| 5 | 99.6 / 97.0 / 7.5 / .94 / 98% / .68 / 21% | 73.9 / 23.2 / 9.6 / .42 / 23% / .61 / 34% | 69.0 / 17.8 / 7.8 / .43 / 47% / .61 / 34% |
| 10 | 99.3 / 98.0 / 7.2 / .92 / 99% / .67 / 23% | 47.1 / 20.0 / 10.4 / .33 / 26% / .61 / 29% | 45.8 / 23.3 / 7.8 / .37 / 46% / .63 / 33% |

Runs: `wp_nsim_rated.txt` and `sc_nsim_rated.txt`. Also rated: `wp_mu2hop_rated.txt` (raw similarity: fame 99 → 92 → 86 → 87, coherence .66/.62/.61), `wp_rel_rated.txt` and `sc_rel_rated.txt` (relative schedule, no fame movement for famous pairs).

## Example journeys (waypoint+nsim, fame percentile in brackets; the steps string is the rater's 0–3 score per step)
- **SOFI → New York Dolls**
  - p0: deadmau5 (100) > The Chemical Brothers (100) > Primal Scream (99) > The Jam (99) > Buzzcocks (99)
  - p10: EDDIE (56) > Eekkoo (27) > REID (15) > Woman's Hour (45) > Lyla Foy (38) > Ralph Carney (42) > The Bizarros (12) > Electric Eels (20) > Hollywood Brats (39)
  - steps at p10: 2222312323. The run from Ralph Carney onward is a real proto-punk descent. The EDM front half is loose.
- **The Shirelles → Wire**
  - p0: Sam Cooke (99) > Stevie Wonder (100) > Phil Collins (100) > Cyndi Lauper (100) > Blondie (100) > XTC (99)
  - p10: Four Tops (99) > Kim Weston (95) > Martha Reeves (30) > Ike & Tina Turner (98) > NNB (6) > The Gizmos (43) > Nikki and the Corvettes (46) > Richard Hell & the Voidoids (63)
  - steps at p10: 233211212. The Motown half and the punk half are each coherent. The seam between them (Ike & Tina > NNB) is a jump.
- **Compton's Most Wanted → Alabina** (mid pair; the failure case)
  - p10: Yaggfu Front (25) > Finsta Bundy (40) > 大野えり (26) > Đàm Vĩnh Hưng (7) > jesus2099 (0) > Shahyad (0) > أنغام (10) > نانسي عجرم (47) > Mazagan (3) > Khaled (94)
  - steps at p10: 22000013123. This is random obscurity. The bottom of the fame scale holds junk entries: jesus2099 looks like a MusicBrainz editor, not an artist.

## Verdicts
- splice / localwp / diverse / relative schedule: **kill** (reasons above).
- waypoint with raw similarity: **kill**. It funnels through a few internet-era connector artists.
- waypoint + nsim: **unclear, leaning kill as a search**. It gives the same result as the plain control at 3× the cost.
- **fame-neutral similarity (nsim) + a falling fame target: promising.** It is the first thing here that takes famous-pair middles from the 99th percentile to about the 70th by press 5 and about the 46th by press 10. The cost is a coherence drop from about .67 to about .61–.63, with 29–34% of steps rated a stretch or worse against today's 19–23%.

## For round 2
- Best files: `exploration/r1-search/softceil.py` run with env `R1_BASE=nsim R1_HOP=0.3 R1_STEP=0.06 R1_BETA=4`, and `waypoint.py` with `R1_BASE=nsim R1_MU=2 R1_HOP=0.3`. Machinery, including scipy-based full shortest-path trees at about 50 ms, is in `common.py`.
- **The fame drop is too abrupt for mid-fame pairs.** They go from 99 to about 20–30 at press 1, because the target starts from the less famous endpoint. Famous pairs barely move until press 3, then drop fast. The fame schedule needs shaping, e.g. start from the previous journey's middle but never rise above the last target.
- Add a junk floor. Artists below about the 5th percentile include non-artists, so exclude them from the middle; `R1_JUNK` does this in waypoint.py but was only run with the failed relative schedule.
- Most bad steps now sit at **genre seams**: the one place where two genre regions meet through obscure artists. A search that keeps a famous or mid-fame bridge at the seam and digs obscure within each genre might recover coherence. That idea is untested.
- Caveat on the screen: its fail-check was done on famous journeys only. It may rate steps between obscure artists it doesn't know as a stretch, which would understate coherence for every obscurity variant. Nobody has checked this.
