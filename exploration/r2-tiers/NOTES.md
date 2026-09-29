# r2-tiers: fame drops one level per press, and each new journey stays close to the last (EXPLORATORY, not evidence)

This uses today's Dijkstra router with a charge on each artist (not on fame differences), following
round 1's argument. When you press, the journey's middle moves one step down a ladder of fame levels.
The ladder is set from how famous your two chosen artists are:
- Famous pairs aim for roughly 95, 88, 80, 74, 69 and so on, down to a home level of about 50 by press 10.
- Mid pairs have a home level just below their endpoints, so they descend more slowly and stop near their endpoints.

Artists above the current level pay a steep charge. Artists far below it pay a gentle one. From press 1,
no step may have similarity below 0.7. The artists directly next to an endpoint are allowed to be more
famous, so a famous endpoint can still be left.

To keep continuity, artists already in the previous journey are cheaper, and steps the previous journey
already took are free to keep. That makes a press change the area around the pressed card first. The
rest of the journey drifts as the fame level keeps falling. No pairs were used beyond the kit's 20.

## What I tried (one line each)
- Band charge with a wide "near the endpoint" allowance (up to 4 steps out): **kill**. In this map almost everything is within 2–3 steps of a star, so the allowance covered the whole middle and famous pairs stayed at 92–98.
- Continuity as a flat toll on every new artist (c_new up to 1.0): **kill**. It fights the descent (famous pairs stayed at 94–97) and hardly raised continuity, because a toll on each stop also shortens journeys.
- Fixed-length layered search (`tiers2.py`, reusing r1-outside's code): **kill**. It took 7–25 s per journey and often fell back to a plain search anyway.
- A "never shorter than the first journey" search that counts steps: **kill**. One journey took 204 s, and fame did not change.
- "Stay in the scene" (the pressed artist's less famous neighbours count as already in the journey, `scene=1`): **no effect**. Results were within noise of the same variant without it (t15 vs t11, t19 vs t18). Not kept.
- Letting the level next to an endpoint also fall, with an exception so a star whose every neighbour is famous can still be left: **kept**. This is what made famous pairs keep falling after press 5.
- **tiers_fast** (t23R) and **tiers_keep** (t26R): the finalists. tiers_keep adds "steps you already had are free" and makes the famous artists allowed next to an endpoint still pay 30 % of the charge.

## Table (kit; famous pairs / mid pairs = median fame percentile of middle artists; coherence = model screen)
| press | today | tiers_fast (t23R) | tiers_keep (t26R) |
|---|---|---|---|
| 0 | 99.5/98.9 · len 8.1 · coh .65 · bad 25% · top10 94% | same as today | same as today |
| 3 | 99.3/98.6 · 8.1 · .68 · 19% · 97% | 83.6/76.5 · 8.2 · .69 · 21% · 41% | 81.7/76.4 · 8.9 · .70 · 20% · 34% |
| 5 | 99.6/97.0 · 7.5 · .68 · 21% · 98% | 71.8/64.8 · 8.8 · .70 · 21% · 36% | 72.9/64.0 · 9.8 · .72 · 17% · 30% |
| 10 | 99.3/98.0 · 7.2 · .67 · 23% · 99% | 58.3/44.7 · 10.7 · .71 · 17% · 43% | 63.3/56.1 · 10.7 · .68 · 22% · 40% |

| | today | tiers_fast | tiers_keep |
|---|---|---|---|
| middle artists kept from the previous journey (mean over presses) | 34 % | 42 % | **54 %** |
| pressed artist replaced by a similar, less famous one (`replace_check.py`) | 62 % | 54 % | 60 % |
| presses that make the middle >5 points *more* famous | 3 % (it never moves) | 8 % | 7 % |
| routing time per journey, median / max | 0.14 / 2.4 s | 0.18 / 2.6 s | 0.14 / 2.2 s |

The new measuring tools were each checked to fail. The continuity measure scores 0–1 % when a journey
is compared with a different pair's previous journey. The "more famous" measure scores 33 % when the
press order is shuffled.

## Examples (tiers_keep; fame percentile in brackets; screen step ratings 0–3)
- **Explosions in the Sky → Sepultura.**
  - p0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82) > Ghost (96) > Gojira (98).
  - p1 changes only the first half: toe (94) > CHON (75) > Polyphia (83), then the same Poppy > Sleep Token > Ghost > Gojira.
  - p10: toe (94) > Delta Sleep (63) > Hail the Sun (63) > Fleshwater (60) > Vein.fm (52) > Incendiary (54) > Power Trip (74) > Havok (82) > Annihilator (97), rated 3221333322. Math-rock into hardcore into thrash.
- **Too $hort → The Wallflowers.**
  - p0: Ice Cube > Busta Rhymes > Nelly > TLC > Alanis > Barenaked Ladies (all 99+).
  - p10: Che Ecru (46) > Sonder (60) > Mac Ayres (55) > Bruno Major (70) > khai dreams (65) > Rav (56) > nelward (56) > bill wurtz (58) > Jonathan Coulton (97) > Ben Folds Five (99), rated 22322112222.
- **Built to Spill → Billie Holiday.**
  - p0: Broken Social Scene > Feist > Norah Jones (all 100).
  - p10: Car Seat Headrest (84) > Naked Giants (46) > The Murlocs (59) > Orions Belte (54) > The Olympians (60) > Gizmo Varillas (57) > Bremer/McCoy (56) > Bobby Hutcherson (93) > Beegie Adair (80) > Oscar Peterson (97), rated 32213012132.
  - The middle has one jarring step and one weak step.
- **Failures.**
  - Janet Jackson → 311 at p10: Des'ree > Eagle-Eye Cherry > Sugar Ray, all famous.
  - The Shirelles → Wire at p10: Isley Brothers > Funkadelic > Can.
  - Louis Armstrong → Ozzy stays famous in both variants.
  - In these, the kit keeps pressing the card next to a star endpoint, and every neighbour of that star is famous. The router then takes a short 2–3-card famous route rather than a long obscure one. That route is coherent, but it does not dig.
  - Survivor → Nas grows to 17 cards at p10. Emscherkurve 77 (36) → Juçara Marçal (32) ends at 14–35, slightly below both endpoints.

## Verdicts
- **tiers_keep (`tiers_keep.py`): promising, and my pick.**
  - Famous pairs fall steadily (95 → 87 → 82 → 80 → 73 → 66 by press 6, then flat around 63–66 to press 10). Mid pairs stop near their own endpoints.
  - Coherence is at or above today's at every press shown.
  - More than half of each journey survives a press (today: a third).
- **tiers_fast (`tiers_fast.py`): promising.**
  - It digs further by press 10 (58 on famous pairs), and coherence is the same.
  - It keeps less of the previous journey and replaces the pressed artist with a similar one less often (54 %).
- `tiers.py` is the sweep file (settings via env `R2`); `tiers2.py`, the fixed-length version, is dead.

## For the coordinator
1. The remaining plateau and rebounds are one mechanism. The router's total cost favours short journeys, so when the pressed card sits next to a star endpoint, a 2-card famous hop can beat a long obscure detour. It shows up as 7–8 % of presses making the middle more famous for one press, mostly on She & Him, Soul Seekerz and Survivor. Things that did not fix it: fixed length (too slow), counting steps (too slow), and a flat toll per new stop (fights the descent). An untested idea: count the ladder level against the *journey's* least famous stretch, rather than letting a 2-card journey escape the charge.
2. The kit always presses the card next to a famous endpoint. That is the harshest case for continuity (a new start is forced every time). With free choice of card, continuity should be higher than 54 %.
3. The ladder is a single list (`rho`) and the home level is one formula (G = m − 0.5·m³). Both are easy to retune if the owner wants a different pace.
4. Snyk flags low-severity "path traversal" in the local analysis scripts (a command-line path is opened). Each script refuses paths outside `exploration/`, but Snyk does not recognise the guard. Same as r1-rules.
