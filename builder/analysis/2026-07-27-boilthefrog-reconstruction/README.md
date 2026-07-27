# BoilTheFrog reconstruction — 2026-07-27

**Frozen record, not a tool.** Per this directory's parent `README.md`: hardcoded
assumptions, no maintenance, kept so the result can be re-derived and audited.

**`REPORT.md` is the deliverable and owns every figure.** Interpretation lives in
`docs/superpowers/findings/2026-07-27-boilthefrog-source-review.md`, which owns none.

## What this is

A reconstruction of the **original BoilTheFrog project's** built graph and router from the
crawl data that project commits to its own repository. It is the only directory here that
**reads no artistpath artifact** — no `.bin`, no archive, no config. Nothing in this project
was rebuilt, routed, adopted or proposed.

Subject: `github.com/plamere/BoilTheFrog` at **`1f2cb60`** (2020-06-12, repo HEAD).

## Running it

```bash
git clone https://github.com/plamere/BoilTheFrog.git btf   # then: git -C btf checkout 1f2cb60
# btf/ must sit in this directory, beside the scripts
python btf_graph_measure.py     # REPORT §(a) §(b), and the A-vs-B edge overlap in §(i)
python btf_degree_vs_fame.py    # REPORT §(c)
python btf_factor_table.py      # REPORT §(d)
python btf_bypass_ladder.py     # REPORT §(e)
```

Pure standard library — no networkx, no numpy, no artistpath imports, no network access.
The three later scripts import `btf_graph_measure` for its loaders. `btf/` is **not**
committed here; it is a third-party repository and is cloned on demand.

## The one thing that could not be reproduced

`skip_artists_with_no_tracks` — the per-artist Spotify track lists lived in a RocksDB the
original does not commit. Every artist is therefore treated as having tracks, making the
reconstruction an **upper bound** on node count and on the low-degree share. `REPORT.md` §(a)
states which findings this touches and in which direction; §(c)'s fame result is unaffected.

## Two hazards for a reader

- **Currency.** `popularity` here is **Spotify's 0–100 figure**, not artistpath's `pop_raw`
  (score-weighted in-degree, log-scaled). They are different quantities and no figure was
  carried between them. See `CLAUDE.md` on currency-in-the-name.
- **§(d) contains a deliberately retained vacuous cell.** Variants C and D are byte-identical
  by construction. It is kept, and labelled, as an instance of the `FMS-P1` class rather than
  quietly deleted.
