# `CEX-` frontier census — the pre-extension baseline, 2026-08-07

**This directory OWNS the figures below.** Cite them; never restate them elsewhere.
Governing document: [`docs/superpowers/specs/2026-08-07-crawl-extension-design.md`](../../../docs/superpowers/specs/2026-08-07-crawl-extension-design.md).

`frontier_census.py` is offline and read-only. It reconstructs the ALG-B crawl frontier
that `ULC-F3` records as lost, splits the 75,000 → artifact gap, and places the two
artists the owner named as missing on 2026-08-07. Output: `cex_frontier.json`.

**Run it as:**

```bash
UV_LINK_MODE=copy uv run --project ../../ python -u frontier_census.py
```

## Why it exists before the code does

`ULC-F3`'s recovery is "rebuild the frontier from the archive, since every archived
response lists its neighbours". This script does that once, by hand, to establish the
baseline **before** `artistpath-build refrontier` exists. `CEX-T1` then requires the
command to reproduce `reconstruction.frontier_size` exactly. A reconstruction that
disagrees with this number is wrong, and without this file there would be nothing to
disagree with.

## What it establishes

- **The frontier is 42,302** — artists referenced by an archived response and never
  crawled. That is the ceiling on an extension that does no new discovery.
- **`ULC-F3` reproduced directly:** `checkpoint.recorded_frontier` is **0**, with
  `done` and `discovered` both at exactly 75,000. A resume today processes nothing and
  exits 0.
- **The 75,000 → artifact gap is almost entirely deliberate:** of 16,162 artists
  crawled but not shipped, 15,708 are on an applied drop list and only 454 are lost to
  anything else (component prune, nameless, no surviving edges).
- **Goose (the Norwalk jam band) has zero inbound references** across all 75,000
  responses. Its only two ALG-B neighbours, Phish and Fleet Foxes, are both crawled and
  shipped, and neither points back: Goose scores 15 against Phish, whose own
  hundred-artist list bottoms out at 62. **Growth cannot reach an artist nobody names**
  (`CEX-R1`).

  > **⚠ FORWARD POINTER, added 2026-08-08 — this bullet originally ended "— only seeding
  > can", and that half is now FALSIFIED.** Seeding was tested the next day and **does not
  > work either**: a matched-pair build produced a zero-node, zero-edge delta, and Goose is
  > absent at all three degree ceilings including the most permissive selectable one. See
  > `docs/superpowers/specs/2026-08-07-crawl-extension-design.md` §3 and `CEX-R4`.
  > **The figures in this file are unchanged and remain correct**; only the remedy the
  > sentence proposed was wrong.
- **Commander Cody was never missing.** Crawled, shipped, 4 inbound references. The
  owner could not find him because search is literal-substring and the map spells him
  *"& His Lost Planet Airmen"* against the queried *"and the Lost Planet Airmen"*. That
  is a search defect (`CEX-R3`) and is **out of scope here** — recorded so the crawl is
  not credited with fixing it.

## Era-pinning

The script names the 2026-08-07 state: the ALG-B archive at 75,000 responses,
`checkpoint-algb-full.json`, and `graph-msw-tu50.bin` as the adopted artifact. **Do not
repoint it at an extended archive.** Its whole value is that it records the state before
the extension; a post-extension census is a new script in a new directory.
