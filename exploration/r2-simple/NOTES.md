# r2-simple: the simplest thing that could ship (EXPLORATORY, not evidence)

The idea is today's router, unchanged, with two additions: **a per-artist fame toll that grows with each
press** and **a floor on step similarity that applies from press 1**. There is no fixed length, no special
search and no journey state. Press 0 is exactly today's journey.

Code:
- `simple.py` is the engine. Every idea in it is a parameter. `var.py`/`run.sh` sweep it through env `R2`.
- `final_*.py` are the self-contained finalists.
- `stats.py`, `fallbacks.py`, `hubs.py` and `timeit_r2.py` are the checks.
- Each sweep run's parameters are on the last line of `<name>.txt`.

No pairs beyond the kit's 20. With the toll switched off, the engine reproduces today's table and today's
62 % replacement rate exactly.

## What I tried (one line each)
- **The r1-outside control (no fixed length; −log(1−fame) toll at 0.15/press; 0.7 floor), `log15f7`: kill.** It drops slowly: 96.6 at press 3 and 83 at press 10. Journeys shrink from 8 to 6 artists, because the toll falls on everyone and the router pays it by cutting stops. So fixed length *was* doing work for that curve. With a curve that is steep at the top, the problem goes away (next lines).
- **The r1-edgecost knee `ftB`, rerun: plateaus at 84–86**, as in round 1. Mini-hubs sit just under the 90th percentile: Chappell Roan, PinkPantheress and Rina Sawayama each appear in 6 of the 20 pairs.
- **A continuous steep curve, toll ∝ fame^p (p = 8–16): the working shape.** It costs almost nothing below the 70th percentile and rises steeply through the top 10 %. Journeys lengthen a little instead of shrinking. Mini-hubs recur less often (at most 4–5 pairs) and sit lower, at 60–75. p = 12, lin, b = 0.8 gives 83 at press 3 and 74 at press 10. Unrated: p8 and p16 behave alike; p16 lengthens more.
- **Per-press growth:** linear is slow at press 1. √k is too violent at press 1 (84) and then plateaus. Saturating growth plateaus by design. **"Boost" (linear plus an early kick worth about two presses, reached by press 3) is the keeper.**
- **Similarity floor 0.6 / 0.65 / 0.7 / 0.75 / none:**
  - With no floor, the weakest step falls to 0.46 and middle artists over-dive on mid pairs: kill.
  - 0.65 goes deeper (64 at press 10) but with weaker steps.
  - 0.75 keeps more famous artists (top-10 % share 33 %) but flattens after press 3 (71–74), with the same rated coherence.
  - 0.7 is the middle, and I kept it.
  - Note: 58k of the 87k artists have no link ≥ 0.7. The floor effectively confines journeys to the better-connected third of the map. That third includes some obscure artists, and it is also why junk never appears.
- **A floor against junk at the bottom (< 5th percentile), `e_pow16f7j`: no effect at all.** With the similarity floor on, no bottom-5 % artist ever reached a journey. Dropped.
- **Keep or zero today's `known` ramp and floor-relaxation, `e_pow16f7nf`: indistinguishable** (±1 point). I kept them so that press 0 stays exactly today's journey and the change is purely additive.
- **Floor fallback.** A step below the floor costs +20, so it is used only when unavoidable, and a pair can never become unroutable. On top of that, each endpoint's floor drops to its best link to a not-yet-pressed neighbour. The first version used a plain "no step below 0.7" and cost 1–10 s per journey on weakly linked pairs.
- **Speed.** A one-sided Dijkstra with the toll explores far more of the map (median 1.8 s solo). Switching to **bidirectional Dijkstra** over the same costs brought it to **0.2–0.3 s solo median, max 2.6 s**. That is faster than today's router measured in the same loaded session (0.46 s median, max 3.3 s). It finds the same least cost, and 68–80 of 80 journeys are identical to the one-sided search (the rest are ties).
- **A second per-artist term, a toll discount for the pressed artist's close, less famous neighbours (`rd`): kill.** Replacement jumped to 82 %, but fame stalled at 93–96: the discount keeps the journey in the famous neighbourhood, because a star's close neighbours are stars at the 97–99th percentile. Requiring the replacement to be ≥ 10–15 points less famous made the discount inert (replacement 44 %).

## Kit table: finalists vs today (famous-pair middle fame / mid-pair middle fame / length / weakest step / top-10 % share / coherence / bad steps)
| press | today | **final_gentle** (p12, 0.8/press + kick) | **final_bold** (p10, 1.2/press + kick) |
|---|---|---|---|
| 0 | 99.5 / 98.9 / 8.1 / .98 / 94 % / .65 / 25 % | identical to today | identical to today |
| 3 | 99.3 / 98.6 / 8.1 / .98 / 97 % / .68 / 19 % | 83.3 / 72.4 / 8.7 / .72 / 35 % / .69 / 20 % | 77.7 / 71.4 / 9.1 / .72 / 32 % / .72 / 21 % |
| 5 | 99.6 / 97.0 / 7.5 / .94 / 98 % / .68 / 21 % | 75.7 / 70.2 / 10.2 / .72 / 19 % / .71 / 16 % | 71.6 / 62.4 / 10.5 / .71 / 22 % / .70 / 18 % |
| 10 | 99.3 / 98.0 / 7.2 / .92 / 99 % / .67 / 23 % | 73.6 / 64.8 / 10.6 / .71 / 21 % / .68 / 20 % | 67.7 / 60.2 / 10.9 / .71 / 17 % / .66 / 26 % |

Both finalists already drop at press 1: famous-pair middle artists go to 91, and to 77 on mid pairs.

**Mid pairs do not over-dive.** Their middle artists stay at 60–72, while the endpoints sit at 31–69. Very few middle artists fall more than 20 points below the less famous endpoint (0–3 %).

Other figures for both finalists:
- **Replacement check** (the pressed artist is replaced by a close, less famous neighbour; today 62 %): gentle 40 %, bold 36 %. Mismatched fail-check 4 %. **This is the weak spot.**
- **Fallbacks** (a journey that had to use a step below the floor, presses 1–10): gentle 36/200, bold 39/200.
  - Almost all of them fall in 4 of the 5 mid-fame pairs, whose obscure endpoints have only weak links a hop out. Examples: Soul Seekerz's best link is 0.43; Emscherkurve 77 → Stomper 98 → Sham 69 runs at 0.45/0.48, and today's own journey already contains that step.
  - Among famous pairs, only Comeback Kid → Ivy is affected, via a 0.45 link into Ivy.
  - Fail-check: at a floor of 0.99, 196/200 journeys count.
- **Routing time, solo:** gentle median 0.20 s (p90 0.96, max 1.8); bold 0.31 s (p90 1.7, max 2.6). Today's router measured in the same session: 0.46 s (max 3.3).
- **Rated coherence** is at or above today's at every press except bold's press 10: 0.66, with 26 % bad steps.

## Examples (final_bold; fame percentile in brackets, screen step ratings 0–3)
- **Janet Jackson → 311.**
  - Press 0: TLC (99) > Alanis Morissette (100) > Third Eye Blind (99) [2122].
  - Press 10: Tony! Toni! Toné! (81) > Mint Condition (85) > Jagged Edge (95) > Eryn Allen Kane (70) > Benjamin Earl Turner (42) > Phoelix (70) > Chronixx (78) > Protoje (70) > Stick Figure (81) > Sublime with Rome (88) [33312213332].
  - This is a real R&B → neo-soul → reggae → reggae-rock slide.
- **Explosions in the Sky → Sepultura.**
  - Press 0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82) > Ghost (96) > Gojira (98).
  - Press 10: Random Forest (56) > Those Who Ride With Giants (46) > Silent Island (48) > CLANN (47) > Kalandra (54) > Myrkur (66) > Zeal & Ardor (71) > Rivers of Nihil (58) > Cattle Decapitation (91) > Obituary (96) [21322222322].
  - Ambient → dark folk → black metal → death metal. It hangs together.
- **Survivor → Nas.**
  - Press 0: Men at Work (99) > Earth, Wind & Fire (99) > OutKast (100) [2122].
  - Press 10: Huey Lewis and the News (98) > Lou Gramm (85) > Jimmy Barnes (87) > Kirin J Callinan (62) > Genesis Owusu (69) > Paris Texas (59) > Sideshow (54) > Chuck Strangers (57) > Joey Bada$$ (92) [3320223233].
  - It has one jarring seam: Jimmy Barnes > Kirin J Callinan, an Aussie link only.
- **Failure to know about: Louis Armstrong → Ozzy Osbourne at press 10.** Burl Ives > Liz Gillies > Natalie Taylor > Annika Wells > Jaira Burns > Pentakill > Ghost [202330222]. That is a Broadway/TikTok-pop seam, then League of Legends' virtual metal band.
- **Built to Spill → Billie Holiday at press 10** runs through video-game connectors: OMORI > Super Guitar Bros. > Alberto Baldan Bembo.

## Verdicts
- **final_gentle: promising (finalist).**
  - It drops at press 1–3, and journeys stay coherent at today's level through press 10.
  - Length grows 8 → 10.6.
  - It plateaus around 74 after press 5.
- **final_bold: promising (finalist).**
  - It drops further and keeps falling slowly to 68 at press 10.
  - Coherence equals today's through press 9, then softens at press 10 (0.66, 26 % bad).
- **Killed:** the log curve without fixed length, the 90th-percentile knee, √k and saturating growth, no floor, the junk floor, and the replacement discount.

## For the coordinator
- **Files:**
  - `exploration/r2-simple/final_gentle.py`
  - `exploration/r2-simple/final_bold.py`
  - Both are self-contained, with settings baked in and the standard interface.
- **Shipping cost.** The change is two per-artist arrays and a per-edge floor flag inside today's cost. The bidirectional search is optional for correctness but is what keeps it fast. It is worth porting regardless, because it also speeds up today's router.
- **The plateau moved from 78–86 down to about 68–74.** It still exists: once p10 journeys reach the floor-connected obscure layer, a few connector artists recur. Robohands appears in 6 of 20 pairs under bold; MAVI, Orion Sun and RIOPY each appear in 4–5 under gentle. These are the new mini-hubs. They are lower and rarer than AURORA and co., but they are there.
- **Replacement is 36–40 %, against today's 62 %.** A star's close neighbours are stars, so a per-artist term cannot make "replace with someone similar and less famous" happen without stalling the descent. This needs press-local logic (r1-press style), which is outside "simple".
- **Security scan.** Snyk flags low-severity path-traversal on the CLI arguments of the analysis scripts, even after a containment check to `exploration/`; it is the same pattern as r1-rules' `replace_check.py`. The two variant files are clean.
- **Rated runs used: 6.**
  - `A_pow12`: linear growth, gentle.
  - `B_pow12boost`: equal to final_gentle before the endpoint-fallback refinement.
  - `C_pow10boost12`: equal to bold.
  - `D_pow10boost12_f75`: bold with a 0.75 floor.
  - `final_gentle`.
  - `final_bold`.
