# r1-press: what a press does (EXPLORATORY, not evidence)

## The idea that worked: a press is a local repair, not a regeneration
The press keeps the journey. Only the stretch around the pressed artist is re-routed, going from
the card before it to the card after it (or two or three cards either side if that fails). The
replacement stretch may only use artists **at least 10 percentile points less famous than the
pressed one**, and it can be at most 2–3 cards longer than what it replaces. The rest of the
journey stays as it was. So the journey gets more obscure wherever the listener presses, the
change starts locally and spreads with further presses (REQ-16), and no press brings back a
famous route the listener already dug past. The press doesn't depend on which artist is pressed.
In the app, `journey(pressed)` = repair(`journey(pressed[:-1])`, `pressed[-1]`). Replaying the URL's
`known` list reproduces it deterministically, with k routings at ~0.1–0.5 s each.

## What I tried (one line each)
- v1 repair, replacement just "less famous than the pressed artist": **kill**. At the top of
  the fame scale, 100th → 99th changes nothing, and failed repairs fell back to a full
  regeneration, which reset everything.
- v1b–d / v2 substitute-then-stitch (the pressed artist's own less famous neighbour, stitched in
  ≤2 links): **kill as built**. Most stitches failed, and the fallback (today's router) reset the
  journey. Lesson: **the fallback must never be a fresh regeneration.** One reset undoes every
  earlier press.
- v3 repair with an escalation ladder (wider window, more extra cards, smaller margin):
  **promising**, rated. Famous pairs reached the 87th percentile by press 2, and coherence held.
- v4 (length budget + "whole journey below the pressed artist's fame" fallback): **kill**. The
  fallback fired 68 times and put fame back up to 96 by press 10. Slow.
- v5 (hop-limited search ladder): **kill**. Too slow (>100 s per journey).
- v6 (pull toward a target fame band): **kill**. It slowed the descent (famous pairs 97 at press 5).
- v7 (v3 made fast, never resets): **promising**, rated three ways.
- v8 "pressed artist as a direction" (full reroute that makes the pressed artist's less famous
  neighbours cheaper): **kill**. It doesn't move (famous pairs 99 at press 10), the same failure as
  today's per-press pull, because the map always has a famous alternative that costs nothing.
- v9 (v7 plus two fixes found by reading journeys): **best**. (1) A repair may never make any slot
  more famous. v7 widened windows and swapped already-obscured artists back for famous ones:
  Anastacia→Mungo Jerry was obscure at press 3 and back to The Corrs / Simply Red at press 10.
  (2) When nothing less famous fits next to a famous endpoint, it picks the least famous option,
  and as a last resort a window swap with no fame cap, never a reset.

## Table (kit, 20 pairs; coherence = model screen)
| variant | press | fame mid-artists famous / mid pairs | len | weakest link | top10% share | coherence | bad steps |
|---|---|---|---|---|---|---|---|
| today | 0 / 3 / 5 / 10 | 99.5/98.9 · 99.3/98.6 · 99.6/97.0 · 99.3/98.0 | 8.1→7.2 | 0.98→0.92 | 94→99% | 0.65/0.68/0.68/0.67 | 25/19/21/23% |
| **v9b** `v9_repair.py` defaults | 0 / 3 / 5 / 10 | 99.5/98.9 · 86.0/82.1 · 84.6/77.4 · 77.3/65.7 | 8.1→11.0→13.4→18.5 | →0.48 | 94→43→39→30% | 0.65/0.66/0.68/0.71 | 25/23/20/18% |
| **v9c** (EXTRA1=1 MAXEXTRA=1 WHOP=1) | 0 / 3 / 5 / 10 | 99.5/98.9 · 97.7/77.1 · 86.7/72.6 · 86.0/44.4 | 8.1→9.4→10.7→13.0 | →0.51 | 94→57→47→42% | 0.65/0.68/0.69/0.68 | 25/23/18/21% |
| v7a `v7_repair.py` MAXEXTRA=2 | 0 / 3 / 5 / 10 | 99.5/98.9 · 86.6/82.1 · 86.0/75.7 · 85.8/62.2 | 8.1→10.6→12.7→16.6 | →0.55 | 94→51→43→40% | 0.65/0.66/0.68/0.73 | 25/22/21/14% |

## Examples (v9b; fame percentile in brackets; step ratings 0–3)
- Built to Spill → Billie Holiday. p0: Broken Social Scene (100) > Feist (100) > Norah Jones (100). p10: Car Seat Headrest (84) > Snail Mail (77) > Jay Som (74) > Yumi Zouma (74) > Empress Of (78) > ABRA (71) > NAO (74) > Kojey Radical (66) > Ezra Collective (73) > Zara McFarlane (47) > Cécile McLorin Salvant (54) > Catherine Russell (65) > Jeri Southern (69) > John Cacavas (31) > Gerhard Trede (73) > Bob Crosby and the Bob Cats (61). Steps 33322322232321112. Indie rock drifts into UK jazz and then vintage jazz. It flows, but it runs to 18 cards.
- Comeback Kid → Ivy. p0: Turnstile (82) > Blood Orange (97) > Daniel Caesar (88) > Santigold (100) > Metric (100) > Imogen Heap (100) > Frou Frou (99). p10: Incendiary (54) > Fiddlehead (47) > ovlov (64) > Wednesday (69) > Water From Your Eyes (59) > bar italia (57) > Salami Rose Joe Louis (63) > … > Luna Li (67) > Okay Kaya (67) > JFDR (67) > Mammút (49). A real dig, with a soft patch in the middle (steps 111).
- Louis Armstrong → Ozzy Osbourne (the plateau case). p0: Bill Withers > Hall & Oates > Journey. p10: Carpenters (99) > Bread (96) > Seals & Crofts (94) > Doobie Brothers (99) > Steely Dan (99) > 10cc (99) > Player (91) > Robbie Dupree (82) > Steve Perry (93) > REO Speedwagon (99) > Poison (99) > Skid Row (99). It reads well (steps 1332232323232), but it is still mostly famous: a yacht-rock dig rather than an obscure one.
- Failure example (v9c, Lupe Fiasco → Kid Rock, press 5): Nikki Jean (77) > Henry Canyons (9) > Beneficence (13) > MindsOne (8) > Chris Orrick (16) > Pueblo Café (8) > Kid Rock. It dives into underground rap and ends on a 0-rated step into Kid Rock.

## Verdicts
- **v9b: promising.** Fame drops within 2–3 presses and keeps falling to press 10. Coherence
  matches today or beats it at every press, no press resets the journey, and about a third of the
  middle artists are still top-10% at press 10. Cost: journeys grow 8 → 18 on average by press 10
  (11–26 across the 20 pairs), which is over REQ-22's "roughly doubling".
- **v9c: promising.** Length is held (8 → 13, max 18), but famous pairs need about 4 presses
  before they move and then stall around the 86th percentile. Mid pairs dig hardest here (44 at
  press 10).
- **v7a: promising, superseded by v9.** Its windows can re-fame slots the listener had already
  dug past.

## For round 2
1. **The screen hasn't been shown to fail on obscure journeys.** Its fail-check ran on today's
   famous journeys. A rater that doesn't know Henry Canyons or Pueblo Café may rate by genre
   guesswork. Before trusting "coherence held", re-run `validate_screen.py`'s shuffle/random-twin
   check on v9 press-10 journeys.
2. **Plateau near famous endpoints.** A famous endpoint's whole neighbour list is famous, so
   presses on the card next to it can only swap one 99 for another. v9 then takes the least famous
   option, but those presses deliver little (REQ-13). This is a map property, and REQ-18 expects
   it ("popular endpoints take more presses").
3. **Length vs dig is the one knob** (`R1_EXTRA1`, `R1_MAXEXTRA`, `R1_WHOP`). v9b digs more and
   runs longer, v9c the opposite. Something in between is untested.
4. **Dives.** The cap only says "at least 10 points less famous", with no limit on how far below.
   A soft penalty for dropping more than ~40 points in one press might stop Lupe Fiasco-style
   dives. It is untested; v6's band pull was too strong.
5. Six rated runs in all: v3a, v7a, v7b, v7d, v9b and v9c. No extra pairs were used.

Files: `v9_repair.py` (best), `v7_repair.py`, `lib.py` (constrained Dijkstra `route2`). Runs are
in `runs/`, printed journeys in `*_rated.txt`.
