# Issue #200 step 1: served artists during `LBA-G5`, listener rank beside an outside audience count

**Role: FIGURES OWNER for this tabulation.** Every number below is owned here. Cite it; do not restate it.

**What this is:** step 1 of issue #200, the cheapest experiment the issue names. For every artist
between the two endpoints on every journey the owner ran during the `LBA-G5` use gate, it puts the
map's own listener rank beside an outside audience count, split by how many *Dig deeper* presses came
first (the owner's refinement on the issue, 2026-09-25). **It decides nothing.** It asks one scoping
question for step 2: does the **definition** disagree with the owner's ear, or does the **routing**?

**Bars that still stand.** `LBA-AM4` bar 1: no figure here enters the record as a measurement of path
quality. Nothing was re-routed, no alternative weights ran, and nothing is proposed for adoption.
Resuming path-quality work, and anything in step 2, is the owner's trigger.

**Currencies. Three of them, never interchangeable:**
- **`fame_lb_pctl`**: where the artist's ListenBrainz listener count ranks among the map's 87,394
  artists, 0 to 1. This is the adopted novelty-likelihood proxy (`PRODUCT-REQUIREMENTS.md`
  Definitions). Plain sentence: **0.99 means only 1 % of the map's artists have more listeners.**
- **Deezer fans** (`nb_fan`): fetched by the Deezer id the map already carries, with no name
  matching. **This is not Spotify monthly listeners**, which is what the owner looked up. No public
  API exposes that figure. Deezer is used here only as "the size of the audience elsewhere".
- **`deezer_fan_pctl`**: the same fan count ranked within a seeded random 400-artist sample of the
  map. All 400 had a fan count. It exists so the two ranks can be read side by side.

Files: `served_fame_vs_listeners.py` produces every figure. `served_fame_vs_listeners.out.txt` is its
output from this run and holds the full per-artist table (168 rows). `deezer_cache.json` holds the
fetched fan counts, so a rerun makes no network calls. Rerun it from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-25-issue-200-served-fame-vs-listeners/served_fame_vs_listeners.py

**Inputs and identity.**
- **Map:** `C:/dev/music-app/builder/scratch/graph-lba-a6.bin`, sha256 `28311d81d264b8ee…`. The
  script checks this against the file's sidecar and against the sha the gate served, and refuses on
  a mismatch.
- **Telemetry:** `C:/unsung-fast/lbd-artifacts/lba-g5-logs/api-part*.log`, the same logs
  `../2026-09-22-lba-a6-blind-listen/lba_g5_pair_log.md` was derived from. Every `Miles Davis → Daft
  Punk` event is dropped (issue #215), exactly as the pair log drops it.
- **Every press in the gate was *Dig deeper*.** The script asserts that `known_count` equals
  `bypass_depth` on every request, so "presses" below means Dig-deeper presses.
- **Totals:** 85 requests, 410 interior cards, 168 distinct artists.

## 1. Measured

**By depth.** Each card served counts once, including repeats. "≥ 0.5 on both" means at or above the
map's median on both ranks.

| Dig-deeper presses | cards | distinct | median `fame_lb_pctl` | median Deezer fans | median `deezer_fan_pctl` | ≥ 0.5 on both | < 0.5 LB, ≥ 0.5 Deezer | ≥ 0.5 LB, < 0.5 Deezer | < 0.5 on both | no Deezer count |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 55 | 39 | 0.993 | 115,798 | 0.935 | 54 | 0 | 0 | 0 | 1 |
| 1–4 | 145 | 77 | 0.993 | 69,893 | 0.920 | 143 | 0 | 2 | 0 | 0 |
| 5–9 | 92 | 58 | 0.992 | 69,893 | 0.920 | 92 | 0 | 0 | 0 | 0 |
| 10–21 | 118 | 66 | 0.994 | 102,938 | 0.932 | 112 | 0 | 6 | 0 | 0 |

**How closely the two ranks agree (Spearman's ρ):** 0.61 across the 167 served artists that have a
Deezer count, and 0.45 across the 400-artist map sample.

**Cards served below 0.9 `fame_lb_pctl`:** 9 of 55 at 0 presses, 13 of 145 at 1–4 presses, 1 of 92 at
5–9, and 1 of 118 at 10–21. The less-listened artists that were served (Thee Sacred Souls, Sampa the
Great, Quelle Chris, Mach-Hommy and others) all come at 0–3 presses, on the WITCH, Young Gun Silver
Fox and Goose journeys.

**Endpoints picked.**

| `fame_lb_pctl` | endpoints |
|---|---|
| ≥ 0.95 | Radiohead, Pink Floyd, Coheed and Cambria, The Format, Guster, Wishbone Ash |
| 0.74 | Commander Cody & His Lost Planet Airmen |
| 0.67 | WITCH |
| 0.39 | Young Gun Silver Fox |
| 0.01 | Goose, the *Ohio-born, Chicago-based rapper* (MBID `c4e94958…`) |

**Which Goose.** The journey's source is the rapper, per the logged MBID. The map holds exactly two
artists named Goose: that rapper and a Belgian dance/electro-rock band (0.965). **The American jam
band is not on the map at all.** If the owner meant the jam band, the search offered him neither. The
rapper's journey is where the underground-rap artists in the list above come from.

The deep presses (9 to 21 of them) all came on journeys between two endpoints at 0.74 or above: Guster
→ Wishbone Ash, Radiohead → The Format, Commander Cody → Pink Floyd, Guster → WITCH, and Coheed and
Cambria → The Format.

**What sits next to the served artists on the map.** These are the graph neighbours of the distinct
served artists.

| Dig-deeper presses | distinct served | median neighbour count | median share of an artist's neighbours < 0.9 | median share < 0.5 |
|---|---|---|---|---|
| 0 | 39 | 50 | 0.020 | 0.000 |
| 1–4 | 77 | 49 | 0.021 | 0.000 |
| 5–9 | 58 | 49 | 0.000 | 0.000 |
| 10–21 | 66 | 49 | 0.000 | 0.000 |

Pooled over all 168 served artists:

| distance | distinct artists reached | share < 0.9 `fame_lb_pctl` | share < 0.5 |
|---|---|---|---|
| exactly 1 hop | 2,416 | 0.317 | 0.069 |
| exactly 2 hops | 15,936 | 0.741 | 0.265 |

## 2. What I infer from it (inference)

- **The definition agrees with the owner's ear.** The artists he found heavily listened on Spotify
  are the artists the app's own listener measure already calls among the most listened on the map:
  the typical one has more listeners than 99 % of it. Deezer says the same thing independently. No
  served artist sits in the "the app thinks they're obscure but the world doesn't" cell. So adopting
  a different listener measure would not, by itself, change what he hears. What he noticed is about
  **which artists the journey picks**, not about how the app ranks them.
- **Dig deeper is not moving journeys toward smaller audiences.** After 10 to 21 presses, the typical
  artist in the middle of a journey is just as widely listened as before any press. Almost none of
  the deep cards are outside the top 10 % (the 10–21 row above).
- **The likeliest reason is what surrounds those artists on the map, more than any single weight.**
  The typical artist served on a deep journey has essentially no less-listened artists among its
  roughly 50 neighbours. Such artists do exist nearby: pooled over everything served, about a third
  of the artists one step away, and three-quarters two steps away, are outside the top 10 %. But
  reaching them means a journey that leaves the famous neighbourhood and has to come back to a
  famous endpoint. Every one of the deep-press journeys ran between two widely listened endpoints.
- **Journeys that start somewhere less-listened already reach smaller artists.** Goose, WITCH and
  Young Gun Silver Fox produced the served artists with the smallest audiences, with few or no
  presses.

## 3. Weakest link

- **Depth is tangled with which pair was chosen.** Every deep journey ran between famous endpoints,
  and every journey that reached smaller artists had a less-famous endpoint. "Dig deeper doesn't
  move it" is measured only on famous-to-famous journeys. A journey between two mid-scale artists
  pressed ten times was never run. What would falsify it: one such journey, pressed ten or more
  times, that ends up in the lower half of the map. I would drop this point cheaply if that happened.
- **Deezer is not Spotify.** The owner read monthly listeners and this reads Deezer fans. My case
  that the definition agrees rests on two separate outside-ish counts (ListenBrainz and Deezer)
  agreeing with each other about these artists, not on the figure he actually looked at. I would
  defend it anyway: the served artists sit near the top of the map on both ranks, which leaves no
  room for Spotify to call them small.
- **"The map, more than the weights" is inferred from the neighbour tables, not tested.** No
  alternative weights were run; that would be step 2, and it needs a pre-registration. This is the
  inference I would abandon most readily. A strong enough push could still route through the
  less-listened two-step neighbourhood; this table cannot say at what cost to coherence.
- **One of the three less-famous-endpoint journeys may not be the one he meant.** Its "Goose" is a
  rapper with almost no listeners, so its low-listener artists say what the router does from a
  genuinely obscure start. They do not say what it would do from the jam band, which is not on the map.
- **The sample is small.** It covers 10 journeys, two days and one listener.

## 4. Options and their consequences

**Why the decision is his:** issue #200 names whether "better" includes audience size, and whether to
spend a pre-registration on it, as the owner's call (*Whose*, and `CLAUDE.md`'s "what counts as
better" row).

- **(a) The current definition stands; close #200 as not planned, linking this page.** The app keeps
  delivering artists he may not know, but mostly from the top few percent of the map on
  famous-to-famous journeys, and Dig deeper keeps doing little there.
- **(b) Keep the definition; pre-register a routing change aimed at deep presses on famous-to-famous
  journeys.** The knobs are in `ApiConfig` (the "know them already" ramp, the popularity floor and
  jump terms), plus the three fixes parked in `../2026-09-01-cxr-regression-diagnosis/README.md`. On
  the tables above, the change would need to be strong enough to leave a famous neighbourhood. That
  is where the `CXR-` history of use-detected regressions applies: obscurity retunes have twice
  regressed in ways only use caught.
- **(c) Treat it as a map question rather than a weights question.** This means build-time neighbour
  selection that gives famous artists some less-listened neighbours. It is larger and slower, and
  touches the same territory as the parked `TAS-` / selection strands.
- **(d) Before choosing, run the one journey the weakest link names.** Pick a mid-scale-to-mid-scale
  pair on unsung.fm and press Dig deeper ten or more times. That costs the owner a few minutes, it is
  his hands, and it separates "Dig deeper is weak" from "famous endpoints trap the journey".
