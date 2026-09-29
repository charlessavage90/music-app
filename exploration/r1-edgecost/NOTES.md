# r1-edgecost — change what an edge costs (EXPLORATORY, not evidence)

Code: `engine.py` (Dijkstra copied from `find_path`, per-edge cost arrays; with `R1='{}'` it reproduces
today's table exactly, so the engine is faithful), `var.py` (every idea is a parameter, set via env `R1`
as JSON), `sweep.sh` (runs several). Each run's params are on the last line of `<name>.txt`.
No pairs used beyond the kit's 20.

## What I tried
- **Mutual-rank similarity** (an edge is cheap only if each artist ranks the other near the top of its
  list; raw score ignored) — `rank1`, `rank05s`, `rankonly_mix`: dies. Famous artists rank *each other*
  highly, so the famous highway is still cheap. Most-famous middle artists barely move.
- **PMI-style lift** (charge a hop by how similar the next artist is to everyone on average) — `lift3`:
  dies. Journeys shrink to ~5 artists, famous pairs unmoved.
- **Charging climbs more than descents**, scaled by presses — `climb05`: dies, and makes it *worse*
  (100 % of middle artists from the top 10 %). **Why, and why it can never work:** along any journey,
  total climbing = (total up-and-down)/2 + (end fame − start fame)/2. So a climb charge is exactly a
  symmetric "don't change fame" charge plus a constant — it punishes the dip into obscurity as much as the
  climb back. Same algebra explains the July finding that no symmetric term moved the bias; any
  asymmetric *difference* term is secretly symmetric. Only a charge on the artist itself can pull down.
- **Removing today's "no fame cliffs" charge as presses grow** — `nojump`: does nothing on its own.
- **Degree charge** (well-connected artists cost more) — `deg02k`: dies; acts as a per-stop toll, so
  journeys shorten to ~6 through the same stars.
- **A per-press toll on artists above the 90th fame percentile only**, scaled 0→1 across the top 10 %
  (`w_fame_k·k·max(0, fame−0.9)/0.1`) — `ftA` (0.15/press), `ftB` (0.3/press), plus variants `fk03t9`,
  `ftC` (+hop cost), `ftD` (+mutual rank: weakest links collapse), `ftE` (threshold 0.95: weaker).
  **This is the one that moves.** The threshold is essential: `ftF`/`ftG` lowered the threshold with
  presses, so everyone pays, and journeys shortened back through famous hubs — killed.

## Table (kit, 20 pairs; famous-pair middle fame pctl / mid-pair / length / weakest link / top-10 % share / coherence / bad steps)
| press | today | ftA (0.15/press, top-10 % only) | ftB (0.3/press, top-10 % only) |
|---|---|---|---|
| 0 | 99.5 / 98.9 / 8.1 / .984 / 94 % / .65 / 25 % | identical to today | identical to today |
| 3 | 99.3 / 98.6 / 8.1 / .975 / 97 % / .68 / 19 % | 95.3 / 83.2 / 8.1 / .891 / 64 % / .67 / 18 % | 88.8 / 84.2 / 8.9 / .827 / 46 % / .66 / 19 % |
| 5 | 99.6 / 97.0 / 7.5 / .937 / 98 % / .68 / 21 % | 88.5 / 83.2 / 8.4 / .862 / 47 % / .64 / 26 % | 87.1 / 82.5 / 9.4 / .749 / 34 % / .67 / 20 % |
| 10 | 99.3 / 98.0 / 7.2 / .923 / 99 % / .67 / 23 % | 85.8 / 81.4 / 9.2 / .664 / 31 % / .65 / 26 % | 84.3 / 82.9 / 10.6 / .685 / 15 % / .68 / 20 % |

Screen-rated coherence stays at today's level for both; ftB already shifts after one press (top-10 %
share 60 % at press 1).

## Example journeys (ftB, fame percentile in brackets, screen step ratings 0–3)
- Janet Jackson → 311. p0: TLC (99) > Alanis Morissette (100) > Third Eye Blind (99) [2122].
  p10: Zhané (86) > Lucy Pearl (91) > Teedra Moses (85) > Charlotte Day Wilson (79) > Syd (81) > Chronixx
  (78) > Protoje (70) > Iration (88) > Sublime with Rome (88) [3333313332] — lovely R&B-to-reggae slide.
- She & Him → Andrew Bird. p0: Feist (100) [22]. p10: Daniela Andrade (77) > Zella Day (77) > Allie X
  (79) > Magdalena Bay (84) > Japanese Breakfast (84) > Courtney Barnett (84) > Kevin Morby (77) [22222322].
- Built to Spill → Billie Holiday. p0: Broken Social Scene > Feist > Norah Jones (all 100) [2211].
  p10: Car Seat Headrest (84) > Japanese Breakfast (84) > Chappell Roan (89) > Morgan Wallen (81) >
  Hank Williams Jr. (71) > Johnny Paycheck > Johnny Horton > Guy Mitchell > Bob Crosby (61) [3310232212]
  — the Chappell Roan → Morgan Wallen hop is the typical failure: a "both big right now" link.

## Verdicts
- mutual rank, lift, climb/descent asymmetry, jump removal, degree charge: **kill** (none moves famous pairs; asymmetry provably cannot).
- falling-threshold toll (ftF, ftG): **kill** — when everyone pays, journeys get shorter, not obscurer.
- **ftB** (`R1='{"w_fame_k":0.3,"fame_thr":0.9}'`): **promising** — press 0 unchanged, a clear shift
  from press 1–3, coherence held on the screen. ftA is the gentler slope of the same thing.

## For round 2
- The working lever is a toll on *the artist*, not on the edge, and only on the top slice — it is a
  soft, press-scaled version of the formal "fame ceiling". Worth pairing with whoever tests the hard ceiling.
- **Caution on what "less famous" means here.** The drop lands mostly in the 80–90th percentile, and that
  band is full of *current* big names the fame measure under-rates (Lizzo 87, Chappell Roan 89, Martin
  Garrix 89, Lewis Capaldi 85, Morgan Wallen 81). A listener may hear "today's pop" rather than
  "deeper cuts". New mini-hubs appear just under the threshold (AURORA, Poppy, SYML, Japanese Breakfast
  recur across pairs) — the same climb, one tier down.
- Journeys lengthen (8 → 10–11 artists at press 10) and the weakest step weakens (.98 → .69), though the
  screen did not rate them worse.
- Speed: ~1.5 s/journey here only because the exploratory engine is un-vectorised; the toll is a
  per-artist array, so in the shipped router it costs the same as today's ramp.
