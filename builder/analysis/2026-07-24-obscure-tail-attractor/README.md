# Obscure-tail attractor test — is the chillhop blob a cross-genre attractor?

**Date:** 2026-07-24 · **Author:** ml-graph-analyst (analysis only) ·
**For:** Track 2 tuning-vs-graph-limited decision.

This directory **owns its figures.** Do not restate them elsewhere; cite this dir.

## Artifact (verified)

`builder/scratch/graph-t15-tiebreakfix.bin`, the adopted 75k graph.
sha256 `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`
(matches the value in the tie-break-fix adoption finding; verified before every run).

Reader: shipped `api/src/artistpath_api/graph_store.py`. Routing: shipped
`api/src/artistpath_api/pathfinding.py` `find_path` + `ApiConfig` defaults
(`w_sim=3.0, w_jump=1.0, w_floor=1.0, w_hop=0.02, w_avoid=1.0, w_degree_hub=0.0`).
Community detection: igraph Louvain (`community_multilevel`, weighted by similarity),
pulled ephemerally with `uv run --with igraph` (not added to pyproject).

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --with igraph python \
  ../builder/analysis/2026-07-24-obscure-tail-attractor/01_structure_communities.py
# then 02_locate_blob.py, 03_insularity_bridges.py, 05_attractor_descent.py,
# 06_where_interiors_land.py  (04_pick_seeds.py is seed selection only)
```
`01`/`02` write `membership.npy`, `communities.json`, `blob_global_ids.npy`,
`blob.json`, consumed by later scripts.

## The question

Is there a **dominant dense community in the low-external-fame region** that acts as a
**cross-genre attractor for fame-reducing paths**, and does `w_sim` wall it off or drift
into it? Decides whether Track 2's goal (descend in fame while staying genre-coherent) is
**tuning-achievable** or **graph-limited**.

## Verdict: TUNING-ACHIEVABLE. The hypothesised attractor does not exist.

Every element of the premise fails against measurement:

1. **No dominant low-fame attractor.** The graph is cleanly genre-modular (Louvain
   modularity **0.884**, 68 communities). The chillhop/lo-fi-hip-hop community (comm40)
   is real and dense but **small (424 nodes, 0.57% of the graph)** and **not** in the
   low-`pop_raw` region — its members sit at the **96th–99th `pop_raw` percentile**
   (mean `pop_raw` 0.428; the 130-node core "blob" 0.491). It is low **external** fame,
   high **in-graph** popularity — the §2.11 divergence, exactly.
2. **The blob cannot bridge distant genres.** comm40 is **97.1% internal** by edge-slot;
   its 213 bridge edges reach only musically-**adjacent** electronic/downtempo/jazzy-hip-hop
   communities (vaporwave, Nujabes-style, IDM), at lower similarity (bridge mean 0.573 vs
   internal 0.760). It is structurally incapable of being a cross-genre corridor.
3. **`w_sim` walls it off — completely.** Across **110 cross-genre pairs** among 12 famous
   seeds spanning 12 distinct genre communities, **0 of 586 interior nodes** landed in
   comm40 (enrichment **0.00x** vs a 0.83% degree-weighted null). **0/110** paths touch it.
4. **Fame-descent does not funnel in.** Simulating the app's repeated `known` bypass
   (exclude all interiors each round → floor relaxes 0.15/exclusion, reuse forbidden) for
   8 cross-genre pairs over 6 rounds: **still 0 comm40 interiors in every round**, while
   min interior `pop_raw` fell from ~0.80 to ~0.50 (the descent is working; it just
   descends **within** each genre corridor). Control: `idm→chillhop` (Aphex Twin's
   community is adjacent, and saib. *is* the destination) does enter comm40 (1–2/round) —
   so the router enters it precisely when chillhop is the goal, never as a shortcut.
5. **The real cross-genre attractor is in the HIGH-fame region** — the opposite of the
   premise. Cross-genre interiors concentrate in **comm13** (Radiohead/Beatles/Coldplay/
   Metallica/Johnny Cash — the canonical-famous-rock hub, highest-`pop_raw` community):
   **49.8% of all interiors, 24.4x enrichment.** Then comm0 (post-rock/ambient, 5.7x) and
   comm28 (mainstream pop/rap, 2.1x). Distant genres bridge through broadly-similar famous
   canon, which is the expected and musically-sensible behaviour of a similarity graph.

**Implication for Track 2.** The specific graph-structural obstacle the question worried
about — a low-fame blob swallowing fame-reducing paths — is **absent**. Descent already
stays in-genre-community. So a null in the cost-function sweep **cannot** be blamed on a
cross-genre attractor; the coherence goal is not graph-limited on this axis. Track 2 can
proceed as a tuning exercise. (This is a derivation, not a recommendation to proceed —
that call is the owner's.)

## Load-bearing assumptions / what would falsify this

- **Currency.** Every figure is in **raw `pop_raw`** (the shipped floor). "Fame-reducing"
  is operationalised as floor relaxation = `pop_raw` reduction. Because the blob is
  **high** `pop_raw`, floor relaxation points *away* from it — which is part of *why* the
  funnel is zero. **The Track 2 sweep's actual subject is repricing the floor to
  percentile/fame currency; this test does NOT pre-judge that arm.** A fame- or
  percentile-based floor could begin surfacing the high-`pop_raw`/low-fame chillhop
  artists on downtempo paths. Falsifier: re-run 05/06 under a percentile floor and find a
  non-zero comm40 funnel. **This is the one result most likely to move under Track 2's
  intervention and is worth watching in the sweep.**
- **Coherence = same Louvain community** is a structural proxy for genre, and Louvain
  used the same similarity scores Dijkstra routes on, so the two share an input. The
  score-independent cross-check is the decoded paths: each community is genre-recognisable
  by its top members (Beatles / Aphex Twin / Louis Armstrong / ClariS). It is **not** the
  owner's ear — this test certifies "stays in the genre cluster", not "sounds coherent".
  Per project record, offline coherence metrics have agreed with blind verdicts <1/3 of
  the time; a listening test remains the arbiter of coherence.
- **One seed set, but 110 internally-replicated pairs**, all 12 genres, all zero — the
  0.00x is stable across every genre pair, not a point estimate. Measured on the adopted
  artifact only (in scope).
- **Descent is aggressive** (all interiors excluded per round) — a *stronger* funnel test
  than one-card bypass, so the zero result is conservative-safe.

## Prior claims this touches

- **Upholds** Phase 1 log §2.11 (top-degree/high-`pop_raw` sets are insular micro-genre
  clusters; `pop_raw` ≠ fame at the top): comm40 is that phenomenon, measured.
- **Corrects a framing** carried into this task's own premise (and my motivating cheap
  probe): the 10 lo-fi/synthwave "unknowns" are **not one blob** — they split across
  chillhop (comm40, 6), synthwave/outrun (comm20, 2: Lazerhawk, Miami Nights 1984), EDM
  (comm38, 1: Stonebank) and K-pop-adjacent (comm34, 1: CROOVE). Lo-fi and synthwave are
  distinct communities. And the community is **not** in the low-`pop_raw` region.
- **No prior scoring-adjudication numbers restated.**
