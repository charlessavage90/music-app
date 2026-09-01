# `CXS-` growth subsets — does growing the crawl thin the obscure tail? 2026-08-08

**This directory OWNS the figures below.** Cite them; never restate them elsewhere.

**Governing document:**
[`docs/superpowers/specs/2026-08-08-crawl-growth-subset-preregistration.md`](../../../docs/superpowers/specs/2026-08-08-crawl-growth-subset-preregistration.md)
— committed at `7f4b77b` and amended (`CXS-AM1`) at `43f0ce0`, **both before this ran.**

Raw output: `cxs_growth.json`. Harness: `growth_subsets.py`.

```bash
UV_LINK_MODE=copy uv run --project ../../ python -u growth_subsets.py
```

## Result: the tail gets BETTER connected as the crawl grows

**`CXS-C1` (primary) — median connections of a frozen cohort of 10,783 less-famous artists:**

| Cell | Population | Cohort median degree | Cohort mean |
|---|---|---|---|
| `CXS-25` | 25,000 | 14 | 14.81 |
| `CXS-50` | 50,000 | 17 | 18.97 |
| `CXS-75` | 75,000 | **19** | 21.36 |

**+35.7 %, material against the pre-registered ≥ 10 % bar, and monotonic across both steps.**

Pre-registered read for this branch, quoted from §6 before any figure existed: *"growth
thickens the tail. The competition mechanism is dominated by obscure-to-obscure linking.
**Read:** the extension is straightforwardly good for discovery and the withdrawn worry is
closed."*

**`CXS-C2` — cohort absent from the built graph:** 0 / 6 / 6 artists (0.00 % / 0.06 % / 0.06 %).
**Below the 1 % material bar (`CXS-AM1`) — null.** Growth does not push the tail off the map.

## `CXS-C3` — descriptive, a report row and never a gate

No threshold was pre-registered for these and none may be invented now.

| Cell | Nodes | Edges | Share at the degree ceiling | Share with exactly 1 connection |
|---|---|---|---|---|
| `CXS-25` | 21,566 | 615,612 | 17.29 % | 1.23 % |
| `CXS-50` | 42,638 | 1,066,060 | 15.06 % | 2.75 % |
| `CXS-75` | 63,056 | 1,379,944 | **12.98 %** | **4.92 %** |

**Two movements, in opposite directions, and both belong in any citation of this work:**

- **Hub saturation FALLS** as the population grows — 17.3 % → 13.0 % of artists sit at the
  degree ceiling. This is the direct contradiction of the hub-competition mechanism this probe
  was built to test.
- **Artists with exactly one connection RISE**, 1.23 % → 4.92 %, roughly quadrupling. **An
  artist with one connection can start or end a journey but can never appear in the middle
  of one**, so a growing minority of new arrivals are searchable without being discoverable
  through a journey.

## What this does NOT establish

Carried from the pre-registration's §7, written before the run:

- **No path was walked, no journey scored, no clip played.** This says nothing about how the
  app sounds, and nothing about `DD-F1` (famous journeys never routing through anyone
  genuinely obscure), which is a **router** finding.
- **It removes an objection; it does not supply a benefit.**
- **Every cell is at or below today's population.** Whether the direction continues to
  117,302 is an assumption, not a measurement.
- **No cell is production's configuration** (`drop_unlistenable=False`, `require_fame=False`,
  held constant across all three). **No absolute figure here is comparable to any shipped
  artifact** — only the three cells to each other.

## Provenance of the subsets

Not proxies. File mtimes in the ALG-B archive recover the **true crawl order** — 75,000
responses over 8.15 hours at a steady ~10,000/hour — so each cell is the archive **exactly as
it stood** at that moment of the real crawl. Archives were supplied through an in-memory
read-only overlay; **nothing was written to the archive.**
