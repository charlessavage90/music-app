# Common brief for every exploration subagent (EXPLORATORY)

## The product and the problem
artistpath builds a listenable "journey" of artist cards between two artists A and B: the least-cost
path through a similarity map (87k artists, 2.5M edges, `C:\dev\music-app\builder\scratch\graph-lba-a6.bin`).
Each card has a **Dig deeper** button. Pressing it on a card excludes that artist and reroutes the whole
journey. The owner wants **each press to lead to journeys whose middle artists are less famous**, while
the journey **still hangs together** (each step plausibly follows the last). His requirements
(`docs/superpowers/PRODUCT-REQUIREMENTS.md` REQ-9, 13, 18, 27, 33): coherence first, never traded away;
obscurity must increase with presses; noticeably within a handful of presses (3–5), not dozens; the
pressed artist should be replaced by someone similar and less famous; famous artists must not be wiped
out entirely (the first journey between two famous artists may well be famous).

For nine weeks, attempts have failed. Today's router (`api/src/artistpath_api/pathfinding.py`,
`find_journey` → `find_path`, Dijkstra) prices each edge u→v as
`3·(1−sim) + 1·|pop_raw_u − pop_raw_v| + 1·max(0, floor_raw − pop_raw_v) + 0.02 (per hop)
 + 0.01·k·fame_pctl_v (k = presses so far, v ≠ target)`, where the floor starts at the less popular
endpoint's pop_raw and drops 0.15 per press. Defaults in `api/src/artistpath_api/config.py`.
Latest formal result (`docs/superpowers/findings/2026-09-28-drp-lattice-results.md`): doubling or
tripling the per-press pull did nothing, adding extra connections to the map did nothing; only a hard
fame ceiling (exclude every artist above a falling fame percentile) moved journeys — nobody knows if
those journeys hang together.

## Facts measured this session (use them)
- Today's baseline (`exploration/baseline/today.txt`): middle artists of famous-pair journeys sit at the
  **99th fame percentile at press 0 and still at press 10**; even mid-fame pairs route through
  Kylie Minogue, Michael Bublé, John Williams. Coherence ≈ 0.68; ~20% of steps rated a stretch or worse.
  Journeys ~7–8 artists.
- Similarity scores are rescaled and **saturate at the top**: median edge 0.52, 1% of edges exactly 1.0,
  and baseline journeys' weakest link is ~0.98 — the router walks along saturated edges between famous
  artists. An artist's single most-similar neighbour is **more famous 87% of the time** (the map's edges
  point up only 50% of the time). Degree rises with fame (mean 21 for the bottom 30% → 47 for the top 1%;
  lists are capped at 50).
- Routing is fast: ~0.14 s per journey in Python.

## The kit (reuse it; do not rebuild it)
Read `exploration/README.md` and `exploration/kit/qlook.py` first. A variant is a Python file defining
`journey(ctx, s, t, pressed, prev) -> list[int] | None` (optional `setup(ctx)` for precomputation,
called once per worker process). `pressed` = node ids pressed so far (cumulative, oldest first; never
show them again); `prev` = the journey before the latest press. `ctx` gives: `store` (GraphStore:
`neighbours_of`, `offsets`, `neighbours`, `scores`, `pop_raw`, `fame_lb_pctl`, `names`), `pctl`/`pl`
(fame percentile 0–1, numpy/list), `off`/`nbr`/`sc` (CSR as lists; neighbour lists are sorted by id),
`row(u)`, `sim(u, v)`, `names`, `cfg` (ApiConfig), `find_journey`, `find_path`, `known(pressed)`
(→ Exclusion list), `key` (sort key, most famous first), `lookup(name)`. Example: `exploration/baseline/today.py`.
To change routing, **copy** `find_path` / `find_journey` into your folder and modify the copy.

Run (from `api/`):
`PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ../exploration/<dir>/v1.py --out ../exploration/<dir>/runs/v1.json [--rate] [--quiet] > ../exploration/<dir>/v1.txt`
Without `--rate` it is ~1 minute and free: iterate this way. Add `--rate` (the model coherence screen,
cached per artist pair, costs model calls) only for variants that move fame — at most ~6 rated runs.
Set `RATER_WORKERS=2` in the environment when rating (other agents rate concurrently).
The table: `fame mid-artists` = median fame percentile of middle artists (famous pairs / mid pairs);
`weakest link` = median over journeys of the lowest similarity step; `top10% share` = share of middle
artists from the top 10% (famous artists not wiped out); `coherence` = mean step rating ÷ 3;
`bad steps` = share rated a stretch or worse. Baseline to beat on fame; baseline to *match* on coherence.
**Read the journeys themselves** — you know music. A variant that drops fame by routing through
unrelated obscurities is dead regardless of numbers.

## Rules
- EXPLORATORY: speed and breadth over rigor. No pre-registration, no plan documents, no ceremony.
  Try many things, kill fast, go deeper on what shows signal. Think outside the box.
- Write **only** inside `exploration/<your-dir>/`. Never edit `api/`, `frontend/`, `builder/`, `docs/`,
  or anything in `C:\dev\music-app\builder\scratch\`. Never run installs. Do **not** git commit, push
  or switch branches — the coordinator commits.
- If you use any artist pair beyond the kit's 20, append it (names, one pair per line, tab-separated,
  plus a short note) to `exploration/<your-dir>/pairs-used.txt`.
- A new measuring tool must be shown to fail before you trust it passing (one quick check).
- Time box: about two hours of work.

## Return (under one page, plain language — what a listener would hear, not metric names)
- what you tried (one line each, including what died and why);
- the kit table rows at presses 0, 3, 5, 10 for your best variant(s) vs today's baseline;
- three example journeys at press 0 and press 10, with names and fame percentiles;
- verdict per variant: kill / promising / unclear, one sentence why;
- the file path of your best variant(s), and anything the coordinator should know for round 2.
Also write the same as `exploration/<your-dir>/NOTES.md`.
