# r2-shaped: a soft fame charge shaped like the journey (EXPLORATORY, nothing here is evidence)

Pairs: only the kit's 20. No pair added to `pairs-used.txt`.

## The idea
Every middle artist pays a charge when it is more famous than a target for its place in the journey.
There is no hard exclusion, so nothing rebounds and nothing relaxes for the whole map.
- **The target.** Artists next to the two chosen artists may be as famous as them. The target falls
  with each step inward, and falls more steeply with each press. It never drops far below the less
  famous of the two chosen artists. It also sits under r1-rules v7's compounding press ceiling.
- **The charge** is `B·log((1−target)/(1−fame))`. It is steep at the top, so a 99.9 artist pays far
  more than an 85 one.
- **Weak steps.** A step below 0.7 similarity costs extra, but it is not forbidden.
- **The stand-in.** Close, less famous neighbours of the artist just pressed pay no charge.

## What I tried (one line each)
- **v1: target set by graph distance to the nearer endpoint** (`shaped.py`, runs a1–a3, b1–b3): **kill.**
  Famous artists all sit one or two hops from each other, so a journey made only of endpoint
  neighbours pays nothing: O'Jays > Earth, Wind & Fire > Men at Work > INXS > Midnight Oil at press 10.
  Journeys also shrank to about 6.7 artists and the weakest step fell to 0.46.
- **v2: target set by the artist's place in the journey** (`shaped2.py`): **the core that works.**
  A search from each end runs through the map in exact step counts, and the two halves meet in the
  middle, so every artist's place is known. Most journeys are 1–2.5 s.
- A first version of v2 used 27 of 200 fallbacks to today's app. The halves were bouncing back and
  forth between two artists, and each fallback undid the presses. **Fixed.** The search now never
  steps straight back, and it keeps 20 candidate meeting artists. It logged no fallbacks across
  9 runs. The fallback counter was shown to fail: on the no-charge copy it counts 200/200 as identical
  to today.
- **Length rule "at most press-0 length + 3 or 4"** (w3, w4, y4): **kill.** It slows the drop (press 5
  at 84–86 against 76), and v2 journeys only grow by about 1.5 artists without it. "At least press-0
  length" is kept, as a preference.
- **Junk guard** (charge for artists below the 5th fame percentile, y6): **no effect.** They are
  already almost never used.
- **"Stand-in" relief** (the pressed artist's close, less famous neighbours pay no charge, y8):
  **keep.** It raises similar-and-less-famous replacements from 40 % to 60 % (today 62 %) with no
  loss of fame drop.
- **Stronger press steepening** (Gk 0.012, y5 and y9): deeper at press 10, but coherence slips there.

## Why the plateau: which places stay famous
Median fame by place, famous pairs (place 1 = next to a chosen artist):

| | place 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| r1-rules v7, press 10 | 97 | 83 | 66 | 64 | 64 |
| **f1, press 5** | 97 | 84 | 70 | 61 | 56 |
| **f1, press 10** | 97 | 84 | 62 | 50 | 44 |

Places 3 and deeper keep getting less famous with every press. The plateau in the kit's
all-middle figure is places 1 and 2. Place 1 is by design (REQ-18/34: famous artists are not wiped
out). Place 2 is held by the one-step-in allowance (−16 points at press 10). With ~7 middle artists
per journey, those four artists set the median. Tightening place 2 is the lever if the headline
figure must fall further. That is a product call: the artist right after Survivor would stop being
a Huey Lewis.

## Table (rated runs; famous / mid-pair middle fame, length, coherence, steps rated a stretch or worse)
| press | today | **f1 `f1_shaped_charge.py`** (y8R) | f2 `f2_shaped_charge_deeper.py` (y9R) | r1-rules v7 |
|---|---|---|---|---|
| 0 | 99.5 / 98.9, 8.1, 0.65, 25 % | same as today | same as today | 99.5 / 96.1 |
| 3 | 99.3 / 98.6, 8.1, 0.68, 19 % | 84.5 / 70.8, 10.2, 0.67, 20 % | 84.5 / 70.8, 10.2, 0.67, 22 % | 85.9 / 70.8, 9.2, 0.68, 24 % |
| 5 | 99.6 / 97.0, 7.5, 0.68, 21 % | 76.4 / 54.6, 10.0, 0.70, 19 % | 76.0 / 54.6, 10.4, 0.69, 20 % | 78.3 / 31.7, 9.4, 0.67, 25 % |
| 10 | 99.3 / 98.0, 7.2, 0.67, 23 % | 72.5 / 47.8, 9.7, 0.67, 26 % | 68.3 / 42.9, 9.7, 0.64, 30 % | 78.1 / 31.2, 10.2, 0.66, 26 % |

More figures for f1:
- **Middle-of-journey fame** (places 2 and deeper), famous pairs: 83.7 at press 3, 74.5 at press 5,
  64.0 at press 10.
- **Top-10 % share at press 10:** 38 %.
- **Mid pairs:** at presses 1–3 the middle stays 16–53 points *above* the less famous endpoint (no
  over-dive). By press 10 the median sits 11 points above it. The worst case is Compton's Most Wanted
  → Alabina, 38 points below, through Yaggfu Front (25) and Mista Sinista (25).
- **Replacements:** 60 % (today 62 %, v7 48 %).
- **Speed:** 1.3–2 s per journey alone; 2.5 s with 3 workers on a loaded machine.

The famous-pair figure is not smooth between presses 5 and 9: f1 goes 76, 77, 78, 78, 80, then 72.5.
The places-3-and-deeper figures fall steadily.

## Example journeys (f1; fame percentile; screen step ratings 0–3)
- **Explosions in the Sky → Sepultura.**
  - p0: Helios (98) > Max Richter (99) > SYML (84) > AURORA (90) > Poppy (87) > Sleep Token (82) > Ghost (96) > Gojira (98) [222212222].
  - p10: toe (94) > CHON (75) > Jason Richardson (62) > Within Destruction (45) > Brand of Sacrifice (50) > Archspire (55) > Dying Fetus (95) > Cannibal Corpse (98) [323232332]. Math-rock into tech-death, and every step lands.
- **Built to Spill → Billie Holiday.**
  - p0: Broken Social Scene > Feist > Norah Jones (all 100) [2211].
  - p10: Car Seat Headrest (84) > Modern Baseball (73) > McCafferty (59) > Patrick Schneeweis (40) > Amigo the Devil (51) > Colter Wall (68) > Marty Robbins (96) > The Ink Spots (97) [323222212]. Indie to emo to dark folk to old country to the Ink Spots.
- **Comeback Kid → Ivy (a failure).**
  - p0: Turnstile (82) > Blood Orange (97) > … > Frou Frou (99).
  - p10: Stray From the Path (85) > Thornhill (60) > Ocean Grove (51) > Running Touch (50) > Boo Seeka (47) > Kita Alexander (62) > Obongjayar (79) > Scott Hardkiss (49) [333133011]. The metalcore half is lovely, then it crosses a genre seam through junk-ish edges.

Other zero-rated steps at press 10 are junk edges that the similarity floor cannot catch, because
their similarity is high: Donny Hathaway > Brett Eldredge, Greta Svabo Bech > Gerard Way, Mack 10 > E.S.G.
Mini-hubs in the 80–89 band still recur around press 3: I DONT KNOW HOW BUT THEY FOUND ME, Jack
Stauber, Kero Kero Bonito, Laufey, and Lost Years > David Hasselhoff.

## Verdicts
- **f1 `f1_shaped_charge.py`: promising, finalist.**
  - It holds today's coherence at every press, and replacements match today's.
  - On famous pairs the middle is visibly less famous by press 3. From place 3 inward it keeps
    getting less famous to press 10. It beats round 1's ~78 at press 10.
  - No over-dive early on mid pairs, and journeys run about 1.5 artists longer than today.
- **f2 `f2_shaped_charge_deeper.py`: promising but second.** It is identical to f1 through press 5
  and deeper after (68 at press 10). At press 10, though, 30 % of steps are rated a stretch or worse,
  which is over the bar.
- **Kill:** graph-distance targets; length caps; junk charge.

## For the coordinator
- Both files are self-contained, with settings baked in, and import only numpy. `journey(ctx, s, t,
  pressed, prev)` ignores `prev`; the result depends only on the pressed list, so Back and re-press
  are consistent.
- Press 1 barely moves (98.6), because the compounding centre starts from the pressed artist's own
  fame. The drop is clear by presses 2–3.
- **Open levers:**
  - the place-2 allowance (the headline plateau);
  - a mid-pair floor that also holds at press 10 (the lower bound only binds early, since X·k grows
    past the pair's fame);
  - junk edges (the edge-price track);
  - 80–89 mini-hubs.
- **Code.** `shaped2.py` + `var2.py` (env `R2` JSON) is the sweep engine. `analyze.py` gives the
  middle-of-journey and mid-pair dive figures; its all-middle column was checked equal to the kit's.
  `fbcount.py` is the fallback detector.
- **Snyk:** three low "path traversal" findings remain, on command-line paths in the local analysis
  scripts (`analyze.py`, `fbcount.py`). Both scripts refuse paths outside `exploration/`, and Snyk
  does not recognise that check. The finalist files are clean.
