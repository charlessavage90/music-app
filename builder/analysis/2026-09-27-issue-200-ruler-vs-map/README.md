# Issue #200: is the walled-in top of the current map in the map, or in the ruler?

**Role: FIGURES OWNER for this decomposition.** Every number below is owned here. Cite it; do not
restate it.

**What this is:** the measurement that `../2026-09-27-issue-200-graph-descriptives/README.md` §3, first
bullet, names as its own falsifier: "score lba-a6's edges with lux4's percentiles over the artists the
two maps share". It re-scores each map's connections with each map's fame ruler, over the artists
both maps contain, and splits any difference between the connections and the ruler. **It decides
nothing.** No journey was routed, no weight was run, `ApiConfig` was not read or changed, and nothing
is proposed. Resuming path-quality work is the owner's trigger.

**Currency on every figure: fame percentile.** This is an artist's ListenBrainz listener count ranked
0 to 1 **within a named frame**. Every table and column below names its frame, because the frame is
the thing being varied. It is not `pop_raw`, not degree, and not Spotify monthly listeners.

Files:
- `ruler_vs_map.py` produces every figure. It refuses (exit 2) on a sha mismatch before reading
  anything. It takes no command-line arguments.
- `ruler_vs_map.out.txt` is its full output from the run recorded here (1.3 s wall time).

Rerun it from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-issue-200-ruler-vs-map/ruler_vs_map.py

## Inputs and identity

Each file was hashed and matched against the `sha256` field of its own manifest sidecar **and**
against the value pinned in the script.

| role | file (in `C:/dev/music-app/builder/scratch/`) | sha256 |
|---|---|---|
| adopted map | `graph-lba-a6.bin` | `28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b` |
| previous map | `graph-lux4.bin` | `fd92a7352afb7321e80f3818262d08169fcfb3af1d6841d7ccfca0f5e5740369` |

The shared population, its null counts and the only-in-one-map counts agree with
`../2026-09-25-cxr-squeeze-on-lba-a6/README.md` §1 "Populations" and "Measured nulls", where they are
owned. The script reprints them as a check.

## Instrument

- **Parsing and every percentile:** the shipped `GraphStore.from_bytes` and
  `GraphStore.fame_percentiles` (`api/src/artistpath_api/graph_store.py`, loaded from this worktree's
  `api/src`, asserted). The script asserts that each map's stored `fame_lb_pctl` equals
  `fame_percentiles` applied to its raw `fame_lb`. The two recomputed frames call `fame_percentiles` on
  the sub-list of raw `fame_lb` values for the shared artists. Nothing is reimplemented.
- **Metrics:** Measurement A of `../2026-09-27-issue-200-graph-descriptives/README.md`, logic copied
  from `graph_descriptives.py`. For each centre: share of its counted neighbours below 0.9 and below
  0.5 fame percentile; the count and fraction of centres with zero such neighbours.
- **Nulls:** as in that README's "Instrument". A null in the frame's snapshot cannot be a centre and is
  dropped as a neighbour from numerator and denominator.
- **Shared restriction:** "shared" is by MBID. Centres **and** neighbours must both be shared and
  measured in the frame used. An edge to a non-shared artist is dropped. A centre left with no counted
  neighbour is excluded and counted (one top-decile centre in two variants; no top-1 % centre).

### Factor table (fixed before the run)

| id | edges | frame: population ranked over | frame: fame snapshot | artist set | plain sentence |
|---|---|---|---|---|---|
| RVM-1 | lux4 | lux4 full | lux4 (2026-08) | all lux4 | the previous map, measured as it was served |
| RVM-2 | lba-a6 | lba-a6 full | lba-a6 (2026-09-21) | all lba-a6 | the current map, measured as it is served |
| RVM-1s | lux4 | lux4 full | lux4 | shared | the previous map, as served, looking only at artists both maps have |
| RVM-2s | lba-a6 | lba-a6 full | lba-a6 | shared | the current map, as served, looking only at artists both maps have |
| RVM-3 | lba-a6 | lux4 full | lux4 | shared | the current map's connections, judged with the previous map's fame ruler |
| RVM-6 | lux4 | lba-a6 full | lba-a6 | shared | the previous map's connections, judged with the current map's fame ruler |
| RVM-4 | lba-a6 | shared only (recomputed) | lba-a6 | shared | current connections, ruler rebuilt from the shared artists only, current listener counts |
| RVM-5 | lba-a6 | shared only (recomputed) | lux4 | shared | current connections, ruler rebuilt from the shared artists only, previous listener counts |

**Held constant, and why:** the two neighbour bars (0.9, 0.5) and the two centre thresholds (0.90,
0.99) are fixed numbers. The **set** of centres moves with the frame by design: which artists count
as "the most-listened 1 %" is part of the ruler.

### Attribution rule (fixed before the run)

Headline metric: **fraction of top-1 % centres with zero neighbours below 0.9 fame percentile**
(count beside it). From the shared variants:
- total change = RVM-2s minus RVM-1s;
- edges and frame shares along both orderings (edges first: 1s → 3 → 2s; frame first: 1s → 6 → 2s),
  and their average (two-factor Shapley);
- verdict: if one move accounts for ≥ 2/3 of the total in **both** orderings, the wall belongs to
  that move; otherwise "both", with the averaged shares;
- the restriction effect (RVM-2 against RVM-2s) reported separately;
- the frame part on lba-a6's connections split along RVM-2s → RVM-4 (population: full → shared only)
  → RVM-5 (snapshot: lba-a6 → lux4 counts) → RVM-3 (lux4's 929 non-shared artists re-enter the
  ranking).

The same arithmetic is reported, without a verdict, for the top-1 % < 0.5 zero fraction and the
top-decile < 0.9 zero fraction.

## 1. Measured

### The three requested columns: most-listened 1 % (≥ 0.99 in the column's own frame), zero neighbours below 0.9

| | RVM-1 | RVM-2 | RVM-3 |
|---|---:|---:|---:|
| connections | lux4 | lba-a6 | lba-a6 |
| ruler (frame) | lux4 full, lux4 counts | lba-a6 full, lba-a6 counts | lux4 full, lux4 counts |
| artists | all lux4 | all lba-a6 | shared |
| centres | 588 | 874 | 588 |
| zero < 0.9: count (fraction) | 9 (0.0153) | 381 (0.4359) | 274 (0.4660) |
| zero < 0.5: count (fraction) | 84 (0.1429) | 706 (0.8078) | 506 (0.8605) |
| share < 0.9: median / mean | 0.1429 / 0.1952 | 0.0208 / 0.1075 | 0.0204 / 0.0859 |

**RVM-1 and RVM-2 reproduce `../2026-09-27-issue-200-graph-descriptives/README.md` §1 A exactly** in
every checked cell (zero count, zero fraction, median share, mean share, both bars, both tiers;
`all reproduced: True` in the output). Those figures are owned there.

### All variants, most-listened 1 % (≥ 0.99 in each variant's own frame)

| | RVM-1 | RVM-2 | RVM-1s | RVM-2s | RVM-3 | RVM-6 | RVM-4 | RVM-5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| connections | lux4 | lba-a6 | lux4 | lba-a6 | lba-a6 | lux4 | lba-a6 | lba-a6 |
| frame | lux4 full | lba-a6 full | lux4 full | lba-a6 full | lux4 full | lba-a6 full | shared only, lba-a6 counts | shared only, lux4 counts |
| artists | all | all | shared | shared | shared | shared | shared | shared |
| centres | 588 | 874 | 588 | 872 | 588 | 872 | 580 | 580 |
| counted neighbours median (p10, p90) | 49 (34, 50) | 49 (42, 50) | 48 (33, 50) | 48 (39, 50) | 48 (41, 50) | 48 (26, 50) | 48 (41, 50) | 48 (41, 50) |
| share < 0.9: median | 0.1429 | 0.0208 | 0.1348 | 0.0208 | 0.0204 | 0.1200 | 0.0204 | 0.0204 |
| share < 0.9: p10 / p90 | 0.0408 / 0.4000 | 0.0000 / 0.3689 | 0.0406 / 0.3971 | 0.0000 / 0.3000 | 0.0000 / 0.2670 | 0.0222 / 0.4146 | 0.0000 / 0.2659 | 0.0000 / 0.2659 |
| share < 0.9: mean | 0.1952 | 0.1075 | 0.1841 | 0.0935 | 0.0859 | 0.1705 | 0.0860 | 0.0860 |
| **zero < 0.9: count** | **9** | **381** | **11** | **383** | **274** | **29** | **270** | **270** |
| **zero < 0.9: fraction** | **0.0153** | **0.4359** | **0.0187** | **0.4392** | **0.4660** | **0.0333** | **0.4655** | **0.4655** |
| share < 0.5: median | 0.0482 | 0.0000 | 0.0412 | 0.0000 | 0.0000 | 0.0400 | 0.0000 | 0.0000 |
| share < 0.5: mean | 0.0751 | 0.0230 | 0.0622 | 0.0148 | 0.0150 | 0.0522 | 0.0152 | 0.0152 |
| zero < 0.5: count | 84 | 706 | 111 | 723 | 506 | 221 | 500 | 500 |
| zero < 0.5: fraction | 0.1429 | 0.8078 | 0.1888 | 0.8291 | 0.8605 | 0.2534 | 0.8621 | 0.8621 |

Top-decile (≥ 0.90) rows for all eight variants, p10/p90 of every share, raw degree, and neighbour
entries dropped per variant are in `ruler_vs_map.out.txt` under "Measurement A metrics per variant".
The top-decile zero < 0.9 fractions are: RVM-1 0.0107, RVM-2 0.0720, RVM-1s 0.0116, RVM-2s 0.0817,
RVM-3 0.0794, RVM-6 0.0213, RVM-4 0.0794, RVM-5 0.0794.

**Centre-set overlap (lba-a6 nodes, shared).** Most-listened 1 %: RVM-3's 588 centres are all inside
RVM-2s's 872 (284 only in RVM-2s, 0 only in RVM-3; Jaccard 0.6743). Top decile: RVM-3's 5,871 are all
inside RVM-2s's 8,541 (Jaccard 0.6874). RVM-4 and RVM-5 have 580 top-1 % and 5,791 top-decile centres.

### Attribution (shared variants; differences in fraction units)

| metric | total (1s → 2s) | edges-first: edges / frame | frame-first: edges / frame | average: edges / frame | restriction (2 − 2s) |
|---|---:|---:|---:|---:|---:|
| **top-1 % zero < 0.9** | **+0.4205** | +0.4473 (1.064) / −0.0268 (−0.064) | +0.4060 (0.965) / +0.0145 (0.035) | +0.4266 (**1.015**) / −0.0061 (**−0.015**) | −0.0033 |
| top-1 % zero < 0.5 | +0.6404 | +0.6718 (1.049) / −0.0314 (−0.049) | +0.5757 (0.899) / +0.0647 (0.101) | +0.6237 (0.974) / +0.0166 (0.026) | −0.0213 |
| top-decile zero < 0.9 | +0.0701 | +0.0678 (0.966) / +0.0024 (0.034) | +0.0604 (0.861) / +0.0097 (0.139) | +0.0641 (0.914) / +0.0060 (0.086) | −0.0098 |

Shares of the total in brackets. **Verdict by the fixed rule, headline metric: EDGES** (≥ 2/3 in both
orderings: 1.064 and 0.965).

**Ruler split of the edges-first frame part, on lba-a6's connections:**

| metric | frame part (3 → 2s) | population (4 → 2s) | snapshot (5 → 4) | 929 re-enter (3 → 5) |
|---|---:|---:|---:|---:|
| top-1 % zero < 0.9 | −0.0268 | −0.0263 | **0.0000** | −0.0005 |
| top-1 % zero < 0.5 | −0.0314 | −0.0329 | **0.0000** | +0.0015 |
| top-decile zero < 0.9 | +0.0024 | +0.0023 | **0.0000** | +0.0001 |

**The snapshot move is exactly zero because the two snapshots are identical on shared artists.** All
57,909 shared artists have the same raw `fame_lb` in both artifacts, and the two recomputed frames
are `np.array_equal` (output, "Populations" block). This was not assumed; the script measures it. By
hand, one record (`00006766-a163-44eb-b6f1-1d82973b95ec`) carries `fame_lb_raw` 380 with `fetched`
2026-08-02 in `grt-archive-algb.pre-cex-snapshot/fame/` and 380 with `fetched` 2026-09-21 in
`C:\unsung-fast\lbd-archives\S4-A6-fame\fame\`. So the fetch dates differ, but the counts returned
did not.

### What the shared restriction drops

| | CSR entries: total / kept / dropped | undirected edges: total / kept / dropped | top-1 % centres dropped (own frame) | top-decile centres dropped (own frame) |
|---|---|---|---:|---:|
| lba-a6 | 2,490,728 / 1,547,476 / 943,252 | 1,245,364 / 773,738 / 471,626 | 2 of 874 | 198 of 8,740 |
| lux4 | 1,315,684 / 1,295,274 / 20,410 | 657,842 / 647,637 / 10,205 | 0 of 588 | 4 of 5,875 |

For lba-a6's top-1 % centres specifically, 998 neighbour entries were dropped as non-shared in
RVM-2s, against a median of 48 counted neighbours per centre that remain.

**Stability.** This is deterministic arithmetic over two fixed files, not a sample. There is no second
slice to take. No degree-preserving random null was built: the counterfactual variants are the
baselines this brief asked for.

## 2. What I infer (inference)

- **The wall is in the current map's connections, not in how fame is measured.** Take the
  most-listened 1 % of artists, and count those with no connection at all to anyone outside the most-listened
  tenth. On the artists both maps share, that goes from about 1 in 50 on the previous map to about 4
  in 9 on the current one. Keep the current map's connections but judge fame with the previous map's
  ruler (RVM-3, the current map's connections judged with the previous map's fame ruler), and the
  wall is still there: slightly *higher*, not lower. Do the reverse (RVM-6, the previous map's
  connections judged with the current map's fame ruler), and the previous map stays open. **By the
  rule fixed before the run, the top-1 % wall belongs to the map's connections: they account for all
  of the change (about 97 % to 106 % depending on the order the two moves are taken, 101 % averaged),
  and the ruler for between −6 % and +4 %.**
- **What a user would see.** Starting a journey from a household name on the current map, close to half
  the time every artist it links to is also in the most-listened tenth. That is a property of who the
  map says sounds like whom, and it would not go away by re-ranking fame differently.
- **Dropping the lba-a6-only artists does not explain it either.** Those artists are mostly
  less-listened, so I expected removing them to strip exits from the top and inflate the wall. For the
  most-listened 1 % it moves the figure by a third of a percentage point (restriction effect row). The
  top 1 % barely link to them in the first place.
- **The ruler did move, and the prior worry was aimed at the right place in the wrong tier.** The
  ruler's effect is visible where the bar sits in the middle of the distribution (below 0.5; and in
  the frame-first ordering, previous-map connections go from about 1 in 50 to 1 in 30 walled when
  judged by the current ruler). It is small beside the change in connections at every tier measured.
  What little frame effect exists is entirely the population change (the ~29,500 added, mostly
  less-listened artists). None of it is listener counts ageing.
- **The fame snapshots are not different snapshots.** Every shared artist has the same listener count
  in both maps, despite fetch dates seven weeks apart. This cuts against a forward note in
  `../2026-09-25-cxr-squeeze-on-lba-a6/README.md` ("Forward notes", second bullet), which says the
  paired shift "bundles the population change with about seven weeks of snapshot age" and calls that
  contribution unmeasured. It is now measured, and it is zero. **So the whole of that README's shift
  is the population change.** That README is its figures' owner; a dated forward note there now points
  here. The coordinating session re-checked the identity independently (0 of 57,909 shared artists
  differ in raw `fame_lb`; two further records read by hand in both archives, same counts, fetch
  dates 2026-08-02 and 2026-09-21). Why ListenBrainz returned identical counts is not established here.
- **For 2026-09-27's §2:** its first bullet ("the very top of the map is walled in again") **survives
  its own falsifier.** The §3 first-bullet worry ("could be partly or wholly the ruler moving") is
  answered: at the most-listened 1 %, it is not the ruler.

## 3. Weakest link

- **"Edges" is a bundle, and this does not open it.** lba-a6's connections differ from lux4's in two
  ways at once: the similarity scores were re-derived (a different pairing form, per the lba-a6
  sidecar), and ~29,500 added artists competed for every artist's top slots before trimming. Both are
  "the map" here. Restricting to shared artists removes the added artists as neighbours, but not their
  influence on which shared artists survived in a famous artist's list. So "it is the map" is
  established; "it is the new similarity scores" or "it is the wider crawl" is not.
  - **What would falsify the verdict:** a frame that is not a rank within either map's population
    (for instance raw listener counts with a fixed cut) showing the current map's most-listened 1 %
    open. I would not expect that: the two rulers here disagree at the top by very little
    (`../2026-09-25-cxr-squeeze-on-lba-a6/README.md` §1, the by-band table's top row), and both
    orderings agree.
  - **I would defend** "the connections, not the ruler" at the most-listened 1 %, on both bars. The
    margins are large and the two orderings agree.
  - **I would give up cheaply** the exact shares. They are ratios of differences in fractions over
    different centre sets (588 against 872), and in edges-first order they exceed 100 %.
- **The centre set moves with the ruler by design.** Under the previous ruler, the current map's
  most-listened 1 % is 588 artists, all inside the 872 the current ruler picks. RVM-3's slightly
  higher wall is consistent with that being the most famous core of the 872, not with the ruler adding
  walls. This was not separated further.
- **Nothing here routes.** A wall in the connections is a statement about the first step out of a
  famous artist, not about the journeys delivered. `../2026-09-27-issue-200-graph-descriptives/README.md`
  §2 already notes that the flatness it measured also holds a tier below the wall. That link remains
  inferred.

## 4. Options and their consequences

**Why the decision is his:** whether the current map's walled-in top is acceptable, and whether to
spend a map rebuild or a pre-registration on it, is a judgement about what the app should do
(issue #200 *Whose*; `CLAUDE.md`, "what counts as better"). Nothing here is a recommendation.

- **Leave it.** The wall is documented, and its owner is now the map, not the ruler. Nothing is spent.
  Famous-to-famous journeys stay as `../2026-09-27-issue-200-graph-descriptives/README.md` §1 B
  measured them.
- **Treat it as a map question** (that README's §4 option (d)). This decomposition says such a change
  would be aimed at something real. It does not say which part of the map construction to change
  (§3 above, first bullet), and that would need its own measurement before a pre-registration.
- **Treat it as a routing question** (that README's §4 option (c)). This result neither supports nor
  rules it out. The wall constrains the first step. The cost function decides the rest.
- **A standing sentence goes stale.** `docs/superpowers/PRODUCT-REQUIREMENTS.md` §8's boxed note says,
  in fame currency, "the barrier is gone". On the current map, at the most-listened 1 %, this
  decomposition says the barrier is back, and in the connections. That document is his
  requirements layer. Whether it needs a forward note is his call now that this exists. This
  directory does not edit it.

## What is NOT established here

- **Which part of the map construction built the wall** (the re-derived similarity scores or the wider
  population competing for top slots). §3, first bullet.
- **Anything about delivered journeys.** No routing ran.
- **Why ListenBrainz returned identical counts seven weeks apart**, or whether a later fetch would
  differ.
- **Whether the wall is audible or matters to the owner.** No listening test is implied or replaced.
- **Anything in Spotify listener currency**, which is the currency of the observation in #200.
