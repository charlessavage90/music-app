# Making Dig deeper actually dig — exploration report (EXPLORATORY, 2026-09-29)

**Nothing here is evidence.** Every figure comes from 20 artist pairs (15 famous, 5 mid-fame, listed
in `pairs-used.txt`) and a model rating each step of a journey. Anything worth pursuing goes to formal
testing on other pairs. Two rounds were run, with ten explorers in all. The brief's stopping rule was
met after round 2, so there was no round 3.

## Open the practice room

```
cd C:\Users\charl\worktrees\music-app\sturgeon\api
$env:PYTHONIOENCODING="utf-8"; uv run python -u ..\exploration\practice-room\server.py
```
Then open **http://127.0.0.1:8765**. It takes about 30 s to load. Pick two artists and press **Build
journeys**. Each column is one way of answering Dig deeper. You can press Dig deeper on any middle card,
in any column, and every card plays a clip. "Dig deeper everywhere" presses the most famous middle
artist in every column at once. Set `$env:PR_ALL="1"` before starting to add four runners-up.
Every pair you build is appended to `pairs-used.txt`, so formal testing can avoid it.
*I checked every endpoint the page uses, including clips, and nine variants loaded together. I could
not look at the page itself, because the browser extension was not connected.*

## What I tried and what died (one line each)
- **Stronger pull on today's price for the step between two artists:** dead. A charge on how much fame *changes* between two neighbours can only discourage change; it can never favour obscurity. This explains nine weeks of nulls.
- **Reworking how steps are priced** (ranks, lift, popularity-divided scores, penalties on well-connected artists): dead. Journeys shrank or stayed famous.
- **Splicing a small bridge around the pressed artist:** dead. Two famous neighbours almost never share a less famous artist.
- **Picking the most obscure of many near-cheapest journeys:** dead. They are all famous.
- **Routing through an obscure waypoint:** dead. Everything funnelled through the same few "connector" artists.
- **Plain map-wide fame ceilings:** dead. When blocked they let the stars back in, or jump straight from a star to unknowns.
- **Pulling toward the pressed artist's less famous neighbours:** dead. A star's close neighbours are also stars.
- **Any fallback that rebuilds the journey from scratch:** dead. It undoes every earlier press.

## The four finalists, as you would hear them
All four are today's journey at press 0. Figures are the typical middle artist's fame percentile on
famous pairs (100 = most listened) at presses 3, 5 and 10, and the coherence screen (today ≈ 0.67).

| column | idea | famous pairs 3 / 5 / 10 | coherence | kept from last journey | pressed artist → similar & less famous |
|---|---|---|---|---|---|
| Today's app | — | 99 / 100 / 99 | 0.67 | 34 % | 62 % |
| **Fame ladder** | each press lowers a fame ceiling one step, set from your two artists; the rest of the journey is held | 82 / 73 / 63 | 0.68–0.72 | 54 % | 60 % |
| **Shared neighbours** | judges a step by how many neighbours two artists share, then eases toward less famous ones | 78 / 68 / 59 | 0.64–0.72 | — | 48 % |
| **Local repair** | keeps the journey and re-routes only the few cards around the one pressed | 87 / 79 / 75 | 0.66–0.69 | most (by design) | 62 % |
| **Fame toll** | today's router plus a toll on famous artists that grows per press, and no weak steps | 83 / 76 / 74 | 0.68–0.71 | — | 40 % |

- **Fame ladder** is the most balanced. It changes the journey near where you pressed first and drifts the rest. For example, Explosions in the Sky → Sepultura at press 10 runs toe > Delta Sleep > Hail the Sun > … > Power Trip > Havok, and every step lands.
- **Shared neighbours** digs deepest. Its idea may matter beyond Dig deeper: how many neighbours two artists share predicts the rater far better than the map's similarity score. It also exposes junk links, such as Louis Prima → BROCKHAMPTON, which scores a perfect 1.0.
- **Local repair** is the most predictable. It only ever changes what you pressed, though journeys grow to about 11 cards.
- **Fame toll** is the smallest change to today's code and routes as fast as today. It levels off by press 5.

All four keep some famous artists: 20–40 % of middle artists are still from the top 10 % at press 10.
On mid-fame pairs, the ladder and the repair stay near their two artists. Shared neighbours digs below
both of them by press 10.

## The strongest thing cutting against them
**They were tuned and judged on the same 20 pairs, by the same model rater.** Every explorer iterated
until its numbers looked good on those pairs, and the rater is a model's opinion, not your ear.

- **Where the rater holds up:** it separates real journeys from shuffled ones on both famous and obscure artists, checked three times.
- **What the rater can't catch:** it cannot tell whether a journey *feels* like a journey, and it grades each step on its own.
- **The numbers flatter them,** so treat the coherence parity as "not obviously broken", not as "as good as today".

Three more things cut against them:
- **Coarse fame measure.** The drop often lands in the 60th–85th percentile, a band that still holds current big names the measure under-rates, such as Chappell Roan (89) and Morgan Wallen (81). It may sound less like digging than the numbers say.
- **Stars that cannot be left.** About half the famous artists have no similar artist even 10 points less famous. Cards next to them stay stars in every variant; Louis Armstrong → Ozzy Osbourne stays famous in at least three of the four.
- **Harsh test.** The kit always pressed the most famous middle artist, often the card next to an endpoint. That makes the variants look slower than a listener pressing mid-journey would find them.

## What I'd try next with another round
1. **Combine the fame ladder with the shared-neighbours measure.** The ladder gives the pace and continuity; shared neighbours gives better steps and catches junk links. This is the obvious round-3 candidate.
2. **Loosen the limit only where the route is blocked, not across the whole map.** Most remaining snap-backs to famous journeys, such as Louis Armstrong → Ozzy Osbourne, happen when the map-wide limit rises.
3. **Stop the router preferring a short all-famous hop over a long obscure detour.** That preference causes the plateau and the ~7 % of presses that briefly get more famous.
4. **Put shared neighbours into the formal edge-price track, whatever happens to Dig deeper.**

**After the report:** the owner's own notes from using the practice room are in
`practice-room/logs/2026-09-29-notes.md` (verbatim, each beside its journey), and `HANDOFF.md` is the
starting point for the session that reviews all of this with him.

Files: `ROUND1.md` is the round-1 digest; each `r*/NOTES.md` has an explorer's full notes; `kit/` holds
the measuring tools and their fail-checks; the finalist files are `r2-tiers/tiers_keep.py`,
`r2-nsim/dig_overlap_gentle.py`, `r2-repair/finalist_repair.py` and `r2-simple/final_gentle.py`.
