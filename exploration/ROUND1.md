# Round 1 digest (coordinator's, EXPLORATORY)

Each direction's full notes: `exploration/r1-*/NOTES.md`. Figures below are the kit's (20 pairs, press
most-famous middle artist). "Fame" = median fame percentile of middle artists, famous pairs / mid pairs.
Today: p0 99.5/98.9 · p3 99.3/98.6 · p5 99.6/97.0 · p10 99.3/98.0; coherence ~0.67; length 8→7.

## What died (one line each)
- More pull on the edge price in any symmetric or one-sided *difference* form (climb charge, jump removal): a
  charge on fame *differences* can only discourage change, never favour obscurity (r1-edgecost's telescoping argument).
- Per-edge reforms alone — mutual rank, lift/PMI, RP3beta as cost, Mutual Proximity, degree penalties: journeys
  shrink or stay famous (degree is capped at 50, so it can't tell a star from a mid act).
- Splicing a 1–2 artist bridge around the pressed artist (two places): famous neighbours share no obscure bridge.
- K-near-cheapest paths then pick the obscurest: all near-cheapest paths are famous.
- Obscure waypoint on raw similarity: funnels through connector artists (salvia palth in 13/20 pairs).
- Plain global fame ceilings: rebound when blocked (relaxing for the whole map lets stars back) and cliff-dive.
- Press-relative ceiling alone: too slow (94 at press 10). Relative (non-ratcheting) schedules bounce back.
- "Pressed artist as a direction" (cheaper less-famous neighbours of the pressed artist): stays at 99.
- Any fallback that regenerates the whole journey from scratch undoes earlier presses.

## What showed signal
| variant | idea | p3 | p5 | p10 | coherence p10 | length p10 |
|---|---|---|---|---|---|---|
| r1-edgecost ftB | charge on top-10% artists, 0.3·k·(fame−0.9)/0.1 | 88.8/84.2 | 87.1/82.5 | 84.3/82.9 | 0.68 | 10.6 |
| r1-outside best | −log(1−fame) charge ·0.15k, keep length, no step < 0.7 sim | 90.2/68.0 | 88.6/59.4 | 81.0/35.7 | 0.65 | 8.3 |
| r1-rules v7 | journey-shaped hard ceiling (endpoint neighbours free, −10 pts per hop inward), compounding per press | 85.9/70.8 | 78.3/31.7 | 78.1/31.2 | 0.66 | 10.2 |
| r1-press v9b | press = local repair of the pressed stretch; replacements ≥10 pts less famous; never regenerate | 86.0/82.1 | 84.6/77.4 | 77.3/65.7 | 0.71 | 18.5 |
| r1-search softceil+nsim | fame-neutral similarity (score vs weaker artist's best link) + falling soft ceiling | 92.5/19.5 | 69.0/17.8 | 45.8/23.3 | 0.63 | 7.8 |

Coherence screen re-checked on obscure journeys twice (kit README; r1-rules): it still separates real from
shuffled/random, so these coherence figures are not the rater being generous about unknowns.

## Shared problems to fix in round 2
- **Plateau ~78–86 on famous pairs** after press 5: a famous endpoint's whole neighbour list is famous.
- **Mid pairs over-dive** (to 20–35, below both endpoints) in several variants.
- **Length growth** (repair: 8→18).
- **Mini-hubs just below a cutoff** (AURORA, Poppy, SYML, Japanese Breakfast recur).
- **Junk at the bottom** (<~5th pct includes non-artists like jesus2099) and junk edges (Louis Prima→BROCKHAMPTON = 1.0).
- The 80–90th percentile band holds current big names the fame measure under-rates (Chappell Roan 89, Morgan Wallen 81).
- **Genre seams**: most bad steps are where two genre regions meet through obscure artists.
