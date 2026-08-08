# Does growing the crawl thin the obscure tail? — pre-registration (`CXS-`)

**Role: ACTIVE pre-registration.** Committed **before any cell is built**; the git timestamp
is the evidence it preceded the result. Identifiers **`CXS-`**, collision-checked across every
ref (`refs/remotes` + `refs/heads`, `*.md`) — free, and disjoint from `CEX-` (the crawl-extension
design) and `CEXR-` (its review).

**Owns no figures.** Results will be owned by `builder/analysis/2026-08-08-cxs-growth/`.

**Descriptive.** Adopts nothing, changes no default, no weight, no currency, and touches no
shipped code. It licenses a **go/no-go input** on the `CEX-` crawl extension and nothing else.

---

## §1 — The question, in one sentence

**As the crawl grows, do the artists at the obscure end of the map end up better or worse
connected?**

Plain-language form, fixed here so it cannot be reshaped by a result: *if we had stopped the
crawl a third of the way through, would the less-famous artists have had more connections each,
or fewer, than they do now?*

**Why it is worth running:** the owner's decision on extending the crawl rests on this, and it
is currently an **expectation, not a measurement** — asserted by this session and then withdrawn
as overstated. Two mechanisms pull opposite ways and nobody has measured which dominates:
growth adds competition at the hubs (thinning the tail), and growth adds obscure artists who
connect to *each other* (thickening it).

## §2 — Method

**The subsets are not proxies.** File mtimes in the ALG-B archive recover the **true crawl
order** — 75,000 responses written over 8.15 hours at a steady ~10,000/hour. Taking the
*n* oldest files reconstructs the archive **exactly as it stood** at that point in the real
crawl.

Three cells, built with the real `build_from_archive`:

| Cell | Archive | Population | Cap rule | Baseline |
|---|---|---|---|---|
| `CXS-25` | 25,000 oldest responses | 25,000 | `TUw-50-50` | — |
| `CXS-50` | 50,000 oldest responses | 50,000 | `TUw-50-50` | `CXS-25` |
| `CXS-75` | all 75,000 | 75,000 | `TUw-50-50` | `CXS-50` |

**One column varies: population.** Each cell's baseline differs from it by exactly that.

Archives are supplied through an in-memory read-only overlay implementing the `RawArchive`
protocol. **Nothing is written to the archive**, deliberately: an earlier probe in this track
wrote one file and restored it in a `finally` block, and a timeout kill bypassed that and left
the archive at 75,001.

## §3 — Held constant, and why each is genuinely constant

| Held | Why the intervention cannot change it |
|---|---|
| `algorithm` = ALG-B | Set per-invocation; identical string in all three cells. |
| `cap_strategy` = `trimmed_union`, `union_top_j` = 50, `union_degree_ceiling` = 50 | The adopted cell. The question is about population, not cap. |
| `drop_unlistenable` = `False`, `require_fame` = `False` | **Held across all three cells.** Required: the frozen `ULF-` census population matches none of the subsets, so the `ULC-F1` guard refuses — that guard working correctly is why neither arm can run at production settings. Neither arm is production's configuration, and no cell here is a candidate artifact. |
| `similarity_damping`, `similarity_rescale` | Untouched. |

**⚠ Terms that are NOT constant, named before the run:**

- **`pop_raw` is population-dependent by construction** — it is score-weighted in-degree over
  rescaled scores (`pipeline.py:365-375`), and `rescale_scores` normalises on the p99 of *this
  build's* edges. **This is the moving-ruler confound, and `CXS-4` below is the control for it.**
- **The `no_release` and `featured_credit` drop lists are 75k-era snapshots** applied to each
  subset via `& known`, so a subset drops proportionally fewer artists. It shifts node counts
  slightly; it does not bias degree within the cohort, because the cohort is fixed.
- **The degree ceiling is the mechanism under test, not a confound.** More nodes at the ceiling
  as population grows is the effect being measured.

**Dormant-term check.** `rescale_scores`'s p99 does **not** reach the trim: `ranking` is built
from the **unclipped** strengths (`pipeline.py:377-385`), so a population-dependent normaliser
cannot silently change which edges are cut. Verified in source before writing this.

## §4 — The cohort, which is the whole control

**Defined once, at the `CXS-25` frame, and frozen.** The cohort is every artist that

1. has a response among the 25,000 oldest (so it exists in all three cells), **and**
2. falls in the **bottom half by `pop_raw` in the `CXS-25` build.**

Measuring "the obscure half" separately per cell would re-derive the boundary against a moving
population and measure the ruler rather than the artists. **The same named artists are tracked
across all three cells.**

## §5 — Outcomes, with thresholds fixed before any result exists

| | Outcome | Material |
|---|---|---|
| **`CXS-C1`** *(primary)* | **Median degree of the cohort.** Plain: *how many connections does a typical less-famous artist have?* | **≥ 10 % relative change**, `CXS-25` → `CXS-75` |
| **`CXS-C2`** | **Share of the cohort absent from the built graph for structural reasons** (excluding drop-list removals). Plain: *how often does a less-famous artist fall off the map entirely?* | **≥ 50 % relative change** |
| **`CXS-C3`** *(descriptive, no threshold)* | Nodes, edges, share at the ceiling, share at degree 1, cohort mean degree | — |

`CXS-C3` is **a report row, not a gate**; no threshold was pre-registered for it and none may be
invented afterwards.

## §6 — The read of every result, including the null

**`CXS-C1` falls ≥ 10 %** — *growth thins the tail.* Extending the crawl makes the typical
less-famous artist **less** connected, which works against what the app is for. **Read:** the
cap question becomes primary and should be settled *before* any crawl, not after.

**`CXS-C1` rises ≥ 10 %** — *growth thickens the tail.* The competition mechanism is dominated
by obscure-to-obscure linking. **Read:** the extension is straightforwardly good for discovery
and the withdrawn worry is closed.

**`CXS-C1` within ±10 % — the null, and it is a real result.** Growth is **neutral** for the
tail. **Read:** the extension neither helps nor harms discovery-through-journeys, so the
decision rests entirely on the searchable-artists benefit (`#1`), and **no cap change is
justified by this evidence.** The null must not be reported as "no problem found" — it is
"the mechanism does not dominate at this scale".

**`CXS-C2`** moves ≥ 50 % up — corroborates hub competition; down — contradicts it; otherwise
null. `CXS-C2` **cannot overturn `CXS-C1`**: presence and connectedness are different failures,
and `C1` is primary.

**A trend that reverses between 25k→50k and 50k→75k** is read as **non-monotonic and
inconclusive at this scale**, whatever the endpoints do, and licenses no extrapolation to
117,302.

## §7 — What this cannot answer, stated before the run

- **It does not measure what a user hears.** No path is walked, no journey is scored, no clip is
  played. `DD-F1` — that famous journeys never route through anyone genuinely obscure — is a
  **router** finding and nothing here touches it.
- **It cannot license the extension on quality grounds.** A favourable result removes an
  objection; it does not supply a benefit.
- **It extrapolates from 75,000 to nothing.** All three cells are at or below today's
  population. Whether the direction continues to 117,302 is an assumption, not a measurement.
- **Neither cell is production's configuration** (`drop_unlistenable=False`), so no absolute
  figure here is comparable to any shipped artifact — only the three cells to each other.
