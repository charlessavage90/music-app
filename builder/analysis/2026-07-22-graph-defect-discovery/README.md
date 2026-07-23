# Graph-defect discovery — the scripts that found §2

These produced the measurements in **§2.2** of
`docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`: that in the
**adopted** graph the most popular artists are among the *least* connected, and that the
degree-based hub metric does not mean "famous."

They are the **discovery** scripts, not the diagnosis. The cause was determined separately
by one-knob intervention — see `../2026-07-22-cap-ranking-replay/` and the log's **§2.8**,
which supersedes the earlier suspicion in §2.4.

**Cite figures from §2.2, not from here** — the document owns them, and §2.2 carries two
correction notices about what these comparisons can and cannot be attributed to. Read those
before reusing any of this.

## What each one does

| Script | Answers |
|---|---|
| `hubcheck.py` | Is "hub" (our metric: top-1% by **degree**) the same as "famous" (**popularity**)? Prints degree/popularity percentiles for the artists the owner perceived as hubs, and measures the overlap between the two top-1% sets. |
| `beatles.py` | Is Radiohead in the graph at all? What are The Beatles' surviving neighbours, and what *are* the current top-degree nodes? |
| `compare_graphs.py` | Cross-artifact presence and degree for a watch-list across capfix / control / `d025` / the original 75k. **Has a known bug:** its name→id lookup keeps only the *last* match, so duplicate artist names (e.g. two "Nirvana" entries) are misreported. `dropped.py` supersedes it. |
| `dropped.py` | Duplicate-aware version, plus the decisive question: **which artists did capfix drop, and were they famous?** Compares MBID sets and reports the popularity distribution of the drops. |

## How this was found — worth knowing

Nothing automated caught it. All 209 tests pass; neither ML-analyst review found it; the
Phase 2 sweep did not surface it. It was found by **the owner questioning a metric's output
against his own perception** — a path reported as `hubfrac = 0.0` that contained Kylie
Minogue, Whitney Houston, Prince and Paul Simon. `hubcheck.py` was written to check that
one objection, and everything else followed from it.

The generalisable lesson is in §2.3: **no structural test asserts that famous artists remain
well-connected**, and no offline metric in the suite would have revealed it.

## Before you re-run them

- **Paths are hardcoded.** These are a record of what was executed, not a maintained tool.
- They need `graph-t15-capfix.bin`, `graph-t15-control.bin`, `graph-t15-d025.bin` and
  `graph-75k.bin` in `builder/scratch/` — all gitignored, identified by checksum only.
- **Do not cite `d025` as a witness for anything** — §2.2's second correction notice
  explains why (it differs in three knobs and is not `p99_log_clip` at all).
- Use `python -u`.

## Note for a reachability sweep

Nothing imports these, and that is correct — **research tooling invoked manually**, same
category as the sibling analysis directories. See Phase 2 execution log §18's B2 check.
