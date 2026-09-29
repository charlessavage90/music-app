# r1-rules: making obscurity a rule, not a price (EXPLORATORY, nothing here is evidence)

Pairs: only the kit's 20. Every variant uses a copy of the shipped router (`rules_common.py`,
`v6_layered.py`). The copy was checked first: with no ceiling it reproduces today's journeys
exactly (`v0_copy.txt`, same table as the baseline).

## What I tried (one line each)
- **v1 press-relative ceiling** (no middle artist more famous than the least famous artist
  pressed so far): **kill.** It works but is far too slow. Famous pairs stay in the 99th
  percentile until about press 6, and only reach about 94 by press 10.
- **v2 compounding-rarity ceiling (global)** and **v3 fast fixed schedule (95, 90, 80 … 30)**
  and **v4 "median of the previous journey"**: **kill as-is.** Fame drops fast, but once a
  ceiling cuts every route, relaxing it for the whole map lets famous artists flood back.
  Famous pairs rebound from about 80 up to about 90 by press 10. With no protection near the
  endpoints, some journeys also jump from a famous artist straight into a chain of near-unknowns
  (SOFI (95) > Gallya (9) > … > Jack Starr (5) > New York Dolls; Comeback Kid (97) > Northcote (26)
  > German singer-songwriters > Ivy). Only 26 % of replacements were a similar, less famous artist.
- **v5/v6 journey-shaped ceiling**: the hard ceiling applies in the middle of the journey. The
  artists next to each chosen artist may still be as famous as it, and the limit tightens 10
  percentile points per step away from it. **The core idea that works.** Journeys now walk down
  gradually from a famous endpoint, and famous pairs settle at a steady middle fame of about 78
  with no rebound. Allowing 20 points per step lost coherence (weakest step 0.41), so killed.
  Limiting by graph distance (v5) and by position in the journey (v6) gave almost the same results.
- **Minimum step similarity rule (no step weaker than 0.4)**: harmless and cheap. It barely moves
  anything. It needs a fallback: without it one mid pair ended up with no journey at all.
- **"Centre ceiling never below the less famous endpoint"**: **kill.** For famous pairs it pins the
  ceiling at about 97, so it switches the whole mechanism off.
- **Rank-based similarity instead of raw scores (v6f)**: **kill.** It gets more obscure but weaker:
  the weakest step fell to 0.39 and fewer replacements were similar to the pressed artist.
- **v7 = press-relative, compounding ceiling + journey-shaped + min step similarity**: **best.**
  Each press shrinks the artist's "rarity allowance" threefold (pressing a 99.8 artist allows at
  most 99.4, then 98.2, 94.6, 83.8 …). So press 1 barely changes anything, and the drop is clear by
  presses 3–5.
- **v8 = v7 + length cap (journey at most 3 longer than the first one)**: **kill in this form.** It
  kept journeys short (8.4 artists) but did it by raising the ceiling for the whole map. Several
  famous pairs snapped back to all-famous journeys at press 10 (Louis Armstrong > Otis Redding >
  Simon & Garfunkel > Led Zeppelin > Ozzy).
- Also v6g: the journey-shaped rule with a gentler fixed schedule (97, 93, 88 … 45). **Promising**,
  a close second to v7: the drop is smoother, and mid-pair journeys stay somewhat more famous.

## The table (rated runs; baseline = today)
| press | today: famous / mid, len, coh, bad | **v7** (`v7m3R`) | v6g (`v6gR`) | v3 plain ceiling (`v3R`) |
|---|---|---|---|---|
| 0 | 99.5 / 98.9, 8.1, 0.65, 25 % | 99.5 / 96.1, 8.1, 0.64, 25 % | same as v7 | 99.5 / 98.9, 8.1, 0.65, 25 % |
| 3 | 99.3 / 98.6, 8.1, 0.68, 19 % | 85.9 / 70.8, 9.2, 0.68, 24 % | 85.9 / 83.4, 9.6, 0.66, 24 % | 83.0 / 64.8, 10.3, 0.70, 19 % |
| 5 | 99.6 / 97.0, 7.5, 0.68, 21 % | 78.3 / 31.7, 9.4, 0.67, 25 % | 81.4 / 65.0, 9.4, 0.68, 21 % | 87.2 / 49.9, 10.2, 0.64, 28 % |
| 10 | 99.3 / 98.0, 7.2, 0.67, 23 % | 78.1 / 31.2, 10.2, 0.66, 26 % | 77.6 / 39.3, 9.7, 0.66, 25 % | 91.3 / 23.2, 9.6, 0.64, 31 % |

Columns: median fame percentile of middle artists (famous pairs / mid pairs), journey length,
coherence, and the share of steps rated a stretch or worse. At press 10, v7 still draws 29 % of
famous-pair middle artists from the top 10 %, against 99 % today: famous artists are reduced but
not wiped out. At press 0, v7 and v6g differ from today only on mid pairs, where the similarity
rule changed a few journeys. How often the new journey holds a similar, less famous stand-in for
the pressed artist: today 62 %, v7 48 %, v6g 41 %, v3 26 %.

**Is the screen trustworthy on obscure journeys?** Yes, checked
(`screen_check_v3R_p10.txt`, the kit's fail-check run on v3's obscure press-10 journeys). The real
journeys score 1.88/3. The same artists shuffled score 1.17, and random artists of the same fame
score 0.71. The real journey beat its shuffled version in 18 of 20 and its random version in 20 of
20. The rater is not simply generous about artists it doesn't know. My replacement check was also
shown to fail: pairing the pressed artist with an unrelated journey scores 2–12 %.

## Example journeys (v7; percentile in brackets)
- **Explosions in the Sky → Sepultura.**
  - p0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82) > Ghost (96) > Gojira (98).
  - p10: Pelican (98) > Amenra (90) > Full of Hell (79) > Power Trip (74) > Havok (82) > Exodus (97). Post-metal into hardcore into thrash, and every step lands.
- **The Shirelles → Wire.**
  - p0: Sam Cooke (99) > Stevie Wonder (100) > Phil Collins (100) > Cyndi Lauper (100) > Blondie (100) > XTC (99).
  - p3: The Marvelettes (97) > Brenda Holloway (90) > Jonathan Richman & The Modern Lovers (84) > The Modern Lovers (97) > Television (98), rated 3,3,1,3,3,3.
  - p10: The Crystals (98) > The Paris Sisters (82) > The Cactus Blossoms (45) > Kacy & Clayton (43) > F. J. McMahon (34) > Jonathan Richman (84) > The Modern Lovers (97).
- **Janet Jackson → 311 (the failure mode).**
  - p0: TLC > Alanis Morissette > Third Eye Blind, all 99–100.
  - p5 is lovely: Sade (99) > Thee Sacred Souls (74) > Cleo Sol (77) > Chronixx (78) > Protoje (70) > Rebelution (94).
  - p10 goes astray through library music: Vanessa-Mae (96) > John Cameron (83) > Janko Nilović (71) > YĪN YĪN (64) > Psychedelic Porn Crumpets (76) > Desert Sessions (69) > Primus (99), with the first steps rated 1,1.

## Verdicts
- **v7 `v7_pressrel_shaped.py`** (MULT=3, MINSIM=0.4): **promising.** It is the first thing that
  makes famous journeys drop clearly by presses 3–5 while holding the screen at today's coherence.
- **v6g `v6_layered.py`** (gentler schedule): **promising**, and the fallback if v7 is too harsh on
  mid pairs.
- v1, v2, v3, v4, v5 with 20 points per step, v6f, "centre ceiling never below the less famous
  endpoint", v8: **kill**, reasons above.

## For round 2
1. The **journey-shaped** part is what matters. A plain global ceiling rebounds and dives off
   cliffs. Any ceiling approach should limit fame by distance from the endpoints.
2. **Relaxation must be local, not global.** Every failure I saw came from raising the ceiling for
   the whole map when routing was blocked or a journey was too long: v3's rebound, v8's snap-back,
   and Soul Seekerz at press 10 returning to Spice Girls > Cardigans > Yann Tiersen. Next step:
   relax only near the bottleneck, or widen the zone near the endpoints rather than raising the
   middle ceiling.
3. **Mid pairs go too deep.** Their middle ends at about 30, below both endpoints, and some journeys
   get long and geographically scattered: Emscherkurve 77 → Juçara Marçal reaches 22 artists,
   through German punk, German pop, Italian pop and Brazilian funk. A per-pair lower bound is
   needed, but not the one I tried.
4. Journeys get about 2 artists longer. A length rule that doesn't work by raising the ceiling for
   the whole map is still open.
5. The raw similarity data has junk edges: Louis Prima → BROCKHAMPTON = 1.000. No fame rule fixes
   those. That belongs to the edge-price track.
6. Runtime is 1–3 s per journey (Python layered search with retries). Fine for exploring, not for
   shipping as is.

`replace_check.py` has one remaining low-severity Snyk "path traversal" finding (a command-line
path passed to open). The file is only run locally, and it refuses paths outside `exploration/`.
Snyk does not recognise that check.
