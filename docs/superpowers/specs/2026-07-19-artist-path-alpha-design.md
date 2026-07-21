# Artist Path — Alpha Design

**Date:** 2026-07-19
**Status:** Approved, ready for implementation planning
**Scope:** Alpha only — a faithful rebuild of Boil the Frog, for personal use, deployed on AWS.

---

## 1. Background

[Boil the Frog](https://musicmachinery.com/2013/01/02/boil-the-frog-2/) (Paul Lamere, 2013) let you name two artists and generated a smooth listening path between them — a grid of artists, each with a representative song clip, where every step sounded like a small move from the last. If you already knew an artist, or didn't like them, you could bypass them and the path rebuilt around them.

It worked by building a similarity graph of ~100,000 artists from The Echo Nest, then routing between endpoints with a preference for **paths through artists of similar popularity** rather than shortest paths. Songs were chosen to be well-known while minimising energy difference between neighbours.

The tool no longer works. The Echo Nest was acquired by Spotify and shut down, and on [2024-11-27 Spotify deprecated](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api) related-artists, recommendations, audio-features, audio-analysis and 30-second preview URLs for all newly registered applications. Rebuilding on Spotify is not possible for an app created today.

### Replacement data sources

| Need | Source | Notes |
|---|---|---|
| Artist similarity | [ListenBrainz Labs `similar-artists`](https://labs.api.listenbrainz.org/similar-artists) | CC0, MusicBrainz-keyed, session-based collaborative filtering. Published by MetaBrainz [explicitly in response](https://blog.metabrainz.org/2024/11/28/pissed-off-by-spotify-enshittifying-more-api-endpoints-we-can-help/) to the Spotify deprecation. |
| Artist popularity | **Score-weighted in-degree** of the similarity graph | Computed from the graph itself — see §4.1. Every external popularity source was eliminated empirically (Task 1 findings §6a–6f): the per-artist API takes ~23s/call, raw dumps lack MBIDs, and Deezer measures the wrong population. In-degree is the only measure computed on the same population as the similarity data. |
| Track clips + art | Deezer API (primary), iTunes Search API (fallback) | 30s previews, no authentication. |

Audio *energy* features have no free replacement. See §5.3.

### Source durability and licensing

Sources fall into two tiers, and the distinction drives §3.1 and §8.1:

**Tier 1 — datasets you possess.** Cannot be revoked or rate-limited once downloaded.

- [MusicBrainz](https://metabrainz.org/datasets/postgres-dumps) — full PostgreSQL dumps, twice weekly. Artist relationships (band membership, collaboration, aliases) plus community genre tags. Core data CC0; note derived data carries CC-BY-NC-SA and must be handled separately if used commercially.
- [Discogs](https://data.discogs.com/) — monthly XML dumps, **CC0**. Group membership, aliases, label and release co-credits.

**Tier 2 — live APIs.** Convenient, revocable, guest status.

- ListenBrainz Labs — CC0. Alpha's primary source.
- Deezer — used for clips; artist-relatedness available but undocumented.
- Last.fm `artist.getSimilar` — broad coverage, **but [free for non-commercial use only](https://www.last.fm/api/tos)**. Commercial use requires a negotiated agreement and Last.fm reserves the right to a revenue share.

**Last.fm must never become load-bearing.** The roadmap includes paid subscribers, and a structural dependency on Last.fm would create a licensing obligation exactly when the product begins earning. It is permitted only as optional enrichment that can be disabled without degrading core routing.

### Multi-source strategy: behavioural spine first, layer later

Similarity comes in three flavours, matching the edge types in §3.1:

- **Behavioural** — listener co-occurrence (ListenBrainz Labs). Best signal for *taste*; weakest for obscure artists. Alpha's sole source.
- **Structural** — factual links: band membership, collaboration, label, influence. Sources: MusicBrainz relationships, Discogs (both CC0 bulk we own), Wikidata. Sparse but precise, strongest exactly where behavioural is thin.
- **Descriptive** — shared genre/tags. Bulk CC0 parquet, **already downloaded** in the Task 1 sample dump (`artist_genre.parquet`, `artist_tag.parquet`). The cheapest augmentation, and the data behind a future per-hop "why".

**Decision (2026-07-20): alpha ships behavioural-only, then layers.** Rationale: mixing edge types changes what a "path" *means*, and a blend cannot be tuned before a pure path can be heard; §2.1 wants one source excellent before enrichment; and typed edges make later addition configuration, not a rebuild — so waiting costs nothing.

Evaluated and rejected as sources: **Spotify Million Playlist Dataset** (download withdrawn, request-only, non-commercial), **Last.fm** (non-commercial), **OLGA/AllMusic graph** (only 17k artists, murky licence).

Queued for the iteration after path quality is judged, cheapest first: genre/tag descriptive edges, then MusicBrainz structural edges if the behavioural graph proves thin for obscure artists.

---

## 2. Scope

### 2.1 Governing principle: depth over breadth

**Excellent artist pathing beats mediocre artist, album and track pathing.** Where a decision trades quality of the artist path against a new capability, quality wins — including against features listed as future scope below.

This principle outranks the future-phase list. Anything on that list that would degrade or merely distract from artist-path quality should be deferred again, however long it has been waiting. Work that *deepens* artist pathing — better routing, better coverage, explaining a hop — is compatible with this principle. Work that *widens* the product to new node types or new modes is not, until artist pathing is genuinely good.

### In scope (alpha)

- Two artist inputs with autocomplete
- Generate a popularity-smoothed path between them
- Render an ordered grid of artist cards: image, name, track title, play control
- Sequential autoplay across the whole path
- Two bypass controls per artist — "not for me" and "know them already" — each rebuilding the whole path, shaped differently (§4.3)
- Shareable URLs encoding the path and its exclusions
- Deployed on AWS, CI/CD from GitHub

### Explicitly out of scope (future phases)

Multi-artist pathing ("centre of these three artists"); album-level and track-level pathing as selectable modes; full-track playback via connected streaming accounts; playlist export; per-hop explanations of *why* two artists connect; user accounts; subscriptions and billing; GenAI natural-language querying.

Per-hop explanation is the **highest-priority** of these (§10.2) — it deepens artist pathing rather than widening the product, so it is consistent with §2.1. The granularity items are the least urgent, by the same principle.

Four seams are built now to keep these cheap later (§7). Nothing else is anticipated.

---

## 3. Architecture

Three components with hard boundaries.

```
┌─────────────────┐   graph-v{n}.bin   ┌──────────────┐
│  Builder        │ ─────────────────► │  S3          │
│  (Python, CI)   │                    └──────┬───────┘
└─────────────────┘                           │ fetch at boot
                                              ▼
┌─────────────────┐    HTTP     ┌──────────────────────────┐
│  Web app        │ ◄─────────► │  API (Node/TS, Fastify)  │
│  (React + Vite) │             │  graph resident in RAM   │
└─────────────────┘             └───────────┬──────────────┘
                                            │ cache
                                            ▼
                                     ┌──────────────┐
                                     │  DynamoDB    │
                                     └──────────────┘
```

**The graph is an immutable build artifact, never a database.** This is the decision the rest of the design rests on: it is what makes pathfinding sub-10ms, makes bypass-and-reroll feel instant, and makes deploys reproducible.

### 3.1 Builder (offline)

Python. Runs in CI on demand or schedule — **never at request time**. Emits one versioned artifact to S3.

Pipeline:

1. **Acquire similarity data.** Behind a `SimilaritySource` interface with two implementations: bulk dump if one exists, otherwise a resumable rate-limited crawl of the Labs endpoint that checkpoints to disk, so a long fetch can be interrupted and resumed. The builder takes a **list** of sources; alpha configures exactly one.
2. **Archive raw responses to S3, unmodified, as they are fetched.** Every subsequent rebuild replays from this archive rather than the network. This converts the crawl from a recurring dependency into a one-time event and is the primary mitigation for §8.1. Expected size a few GB; cost negligible. Non-negotiable — it must not be deferred as an optimisation.
3. **Discover artists by snowball expansion.** Bootstrap from the top 1,000 artists (the most the sitewide stats endpoint will serve — it caps hard at 1,000 while advertising 10.4M), then expand breadth-first through the similarity graph itself until ~75,000 distinct artists are found. Verified in the Task 1 probe; see `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`.

3a. **Derive popularity from the similarity graph itself** — score-weighted in-degree (the summed similarity of edges pointing at an artist). No separate data source: it is computed during the graph build from the archive the crawl produces. Validated against 5,255 ground-truth artists at Spearman ~0.50, and chosen because it is the only popularity measure computed on the same listener population as the similarity data (Task 1 findings §6d–6f). Adequate for alpha; a genuine ListenBrainz artist-popularity table would be a drop-in improvement later.
4. **Symmetrise edges.** Similarity is not mutual; one-way edges create dead ends. Where an edge exists in one direction only, mirror it.
5. **Keep the largest connected component.** Guarantees a path exists between any two artists the UI can offer, so "no path found" can only ever result from user exclusions.
6. **Emit** CSR arrays (`offsets: Int32Array`, `neighbours: Int32Array`, `scores: Float32Array`, `edgeType: Uint8Array`), an artist table (MBID, name, popularity, disambiguation), and a normalised-name index for autocomplete.

Expected artifact size: 40–80MB.

#### Typed edges

Every edge carries a source/type tag. Alpha emits a single type (`behavioural`, from ListenBrainz), so the cost function's type weighting is a no-op — but the format, the builder's source list, and the routing weights all accommodate more from day one.

This is deliberate: adding a second source later is configuration and tuning, not a change to the artifact format or a re-render of the graph. It also means the eventual per-hop explanation feature has real provenance to draw on rather than a generated guess.

Anticipated types, none built in alpha: `structural` (shared band membership or collaboration, from MusicBrainz/Discogs) and `descriptive` (shared genre tags).

### 3.2 API

Node + TypeScript, Fastify, in a container. Loads the graph into typed arrays at boot, pinned by a `GRAPH_VERSION` environment variable. Pathfinding touches no database and makes no network calls.

| Endpoint | Purpose |
|---|---|
| `GET /api/artists/search?q=` | Prefix autocomplete over the name index |
| `POST /api/path` | `{ sources: [id, id], exclude: { id, reason }[] }` → ordered artist list |
| `GET /api/artists/:mbid/track` | Resolve clip URL, cover art, track title |

### 3.3 Web app

React + Vite, served by the same container.

Two autocomplete artist inputs lead to an ordered run of artist cards. Each card carries artist image, name, track title, a play control, and **two bypass controls** (§4.3) — "not for me" and "know them already".

Clicking play walks the entire path, auto-advancing on track end.

A reroll can return a path of any length, longer or shorter than the one on screen (§4.3). The UI must present it as **a new path**, not as an edit of the old one — no animating a single card out and another in, since that would misrepresent what happened and imply a swap the engine deliberately does not perform. Card layout must stay readable as the path grows.

All state lives in the URL — `/path/:from/:to?dislike=…&known=…` — so paths are shareable, and the browser back button naturally undoes a bypass. This is also the groundwork for saved paths later.

---

## 4. Pathfinding

### 4.1 Cost function

Traversing edge `a → b`:

```
cost = w_type[type(a,b)] · (1 − similarity(a,b))  // prefer strong links
     + w_jump  · |pop(a) − pop(b)|                // punish popularity cliffs
     + w_floor · max(0, floor(b) − pop(b))        // don't dive into obscurity
     + w_avoid · avoidance(b)                     // steer clear of disliked regions
     + w_hop                                      // tunes path length
```

- `pop` = log-scaled **score-weighted in-degree**, normalised to 0–1.

  In-degree is the summed similarity of every edge pointing at an artist — how central it is to other artists' listening. This term exists to keep a path among comparably *well-known* artists and to stop routes diving into obscurity, and in-degree measures exactly that centrality. Two properties make it the right choice: it is **free** (computed from the graph, no extra data), and it is **population-consistent** — measured on the same ListenBrainz listening behaviour the similarity edges come from. Every external popularity source was empirically eliminated: the per-artist listener API costs ~23s/call, raw listen dumps carry MBIDs on 0.03% of records, and Deezer `nb_fan` correlated only 0.089 with ListenBrainz popularity because it measures a different audience. In-degree validated at Spearman ~0.50 against 5,255 ground-truth artists, with a near-perfect ranking at the popular end (Task 1 findings §6d–6f). Adequate for alpha; the 0.50 is against a noisy ground-truth proxy and likely understates true quality. A real ListenBrainz artist-popularity table, should one become obtainable, is a drop-in improvement.
- `floor(b)` = the lower popularity of the two endpoint artists, **softened globally with each successive bypass** (§4.3). Ordinarily this is what prevents a route between two household names detouring through an artist with 400 listeners; as the user keeps bypassing, that guard progressively lifts.
- `avoidance(b)` = penalty decaying with graph distance from any "not for me" bypass, zero beyond two hops (§4.3).
- `w_hop` is the primary lever on path length. There is **no specified target** — see §10.3. It is tuned empirically by listening to real paths, and the range that results is an output of tuning, not a requirement imposed on it. It must stay weak enough that a bypass can lengthen the path (§4.3).
- `w_type` is a per-edge-type multiplier. Alpha has one type, so this is effectively a constant; it exists so that later sources can be weighted relative to each other, which is also the mechanism behind future path-steering ("prefer factual connections over taste ones").

Weights are configuration, tuned against the fixture graph and a set of hand-checked real paths.

### 4.2 Algorithm

**Bidirectional Dijkstra.** Not A\* — an abstract similarity graph has no coordinates, so no admissible heuristic is available, and an inadmissible one would silently return non-optimal paths. Bidirectional Dijkstra is exact, needs no heuristic, and runs in single-digit milliseconds at 75k nodes.

Ties break on artist ID, so identical queries always return identical paths.

### 4.3 Bypass — two kinds

The original had a single bypass button, but in practice it was pressed for two opposite reasons: *this artist is wrong for me*, and *this artist is right, I just already know them*. Collapsing both into one exclusion throws away the more useful of the two signals.

Alpha therefore has **two controls, carrying opposite signals**. Both trigger a full path reconfiguration, not a one-for-one substitution.

| Control | Meaning | Effect on routing |
|---|---|---|
| **Not for me** | Negative. The region is wrong. | Hard-exclude the artist, **and** apply `avoidance` — a soft penalty to nearby artists decaying over two hops. The path routes around the stylistic region instead of offering a near-identical substitute. |
| **Know them already** | Positive. The region is right; the artist is just not *new*. | Hard-exclude the artist, apply **no** neighbourhood penalty, and **relax `floor` locally** so the path may reach less famous artists in that style. Same neighbourhood, dug into more deeply. |

**Only the clicked artist is ever a hard exclusion.** Neighbourhood effects are soft costs. This matters: soft costs can bend a path but can never disconnect the graph, so the two modifiers cannot produce a spurious "no path" failure. Only the hard exclusion set can, and that failure mode is handled below.

A reroll is simply another search — no cache invalidation, no recomputation of anything else.

#### Regeneration is total, and the path may grow

This is a load-bearing behaviour of the original, not an incidental one. Bypassing an artist regenerated the entire path, and a six-artist path could come back as nine. Because a popular artist often sits on the *only* direct route, removing one forces the search into longer, stranger territory — and those circuitous routes were where genuinely unfamiliar artists surfaced. **The expansion is the discovery mechanism.**

Three rules follow, all of them prohibitions on things an implementer would otherwise do naturally:

1. **No local repair.** Every reroll is a fresh search between the original endpoints. Patching the path around the removed artist, or reusing the previous path as a starting point, is forbidden — it is cheaper and it makes the UI feel more stable, which is exactly why it is tempting. It also reduces the feature to a one-for-one swap.
2. **No length cap, and no preference for the previous length.** Path length is unconstrained (§10.3). A reroll that doubles the path is a correct result.
3. **No stability bias.** Nothing rewards keeping previously-shown artists. Artists other than the bypassed one may vanish from the path; that is expected, not a bug.

`w_hop` must be tuned weakly enough that rerolls can lengthen the path. If bypassing rarely changes path length, `w_hop` is too strong — treat that as a tuning failure, not as evidence the graph is sparse.

#### Progressive relaxation

Successive bypasses are cumulative evidence that the user wants something further from the obvious route. Each reroll therefore **softens `floor` globally**, not just near the bypassed artist, admitting progressively less famous artists as the user keeps pressing.

Relaxation is stronger for "know them already" than for "not for me": knowing the artists means the popular route is exhausted and novelty is the goal, whereas disliking them is about direction, not fame.

This is what produces the deliberately circuitous later rerolls. Without it, the `floor` term would fight the exact behaviour this section exists to protect.

#### Tuning sequence (important)

These modifiers are tuned **after** the base cost function is tuned and judged good, never alongside it. Tuning three interacting behaviours simultaneously makes it impossible to attribute a bad path to a cause. The base weights are frozen before `w_avoid` and floor-relaxation are touched.

#### Failure handling

Hard exclusions can disconnect the graph. When no path exists the API returns an explicit "no path avoiding those artists" result and the UI says so, offering to clear exclusions. It must never fail silently or return a partial path.

#### Future value

"Know them already" is a durable statement of taste, not a transient routing instruction. Accumulated across sessions it is the seed of a genuine taste profile — the foundation of personalisation and real subscriber value. Alpha does not persist it (no accounts exist yet), but the signal is captured as a distinct type from day one so that nothing needs reinterpreting later.

---

## 5. Tracks and playback

### 5.1 Resolution

Artist → Deezer artist search → top track → preview URL, cover art, title. iTunes Search API as fallback. If neither yields a preview, the card renders as unplayable but **remains in the path** — a missing clip must not alter routing.

Cached in DynamoDB keyed by artist MBID, 30-day TTL.

### 5.2 Loading behaviour

`POST /api/path` returns immediately with artists only. The client resolves clips per-card in parallel. The path therefore renders instantly rather than blocking on the slowest external lookup.

### 5.3 Deviation from the original

The original minimised *energy* difference between adjacent songs using Echo Nest audio features. Those features are gone and have no free equivalent (AcousticBrainz is frozen). Alpha keeps the other half of the original rule — pick a **well-known** track — and drops energy smoothing. Revisit if a viable feature source appears; not a blocker.

### 5.4 Playback

30-second clips in an HTML `<audio>` element, no authentication. Clicking play walks the entire path, auto-advancing on track end. The player sits behind a `Player` interface (§7).

---

## 6. Infrastructure

| Concern | Choice | Rationale |
|---|---|---|
| Compute | **App Runner** (ECR image) | Warm container required — an 80MB resident graph plus cold starts rules out Lambda. App Runner gives TLS, custom domain, autoscaling and deploys without ECS/ALB wiring. ~$10–20/mo. Plain container, so ECS Fargate later is a deploy change, not a rewrite. |
| Graph storage | **S3**, version-pinned | Decouples data releases from code releases. Rebuild and roll forward without touching the app; roll back by changing one env var. |
| Cache | **DynamoDB** on-demand | Clip cache is pure key→value. Costs pennies and **nothing while idle**; RDS would bill ~$15/mo to sit empty. Postgres arrives with accounts and billing, which are genuinely relational. |
| Secrets | SSM Parameter Store | Free tier; Secrets Manager charges per secret. |
| IaC | AWS CDK (TypeScript) | Same language as the application. |
| CI/CD | GitHub Actions with **OIDC role assumption** | No long-lived AWS credentials in the repository, ever. |

Workflows: `ci` (lint, typecheck, test on PRs) · `deploy` (main → build, push to ECR, release) · `build-graph` (manual/scheduled → run pipeline, upload to S3).

### 6.1 Local development

`docker-compose` runs the app against DynamoDB Local and a **~500-artist fixture graph committed to the repository**. A fresh clone runs without fetching the 80MB artifact. The same fixture is the test fixture.

---

## 7. Seams for future phases

Four, costing nothing now:

1. **`POST /api/path` takes `sources: id[]`**, not `from`/`to`. Alpha passes two. Multi-artist pathing passes three without an API change.
2. **Playback sits behind a `Player` interface** (`play(url)`, `pause()`, `onEnded`). A Spotify Web Playback SDK implementation drops in without touching UI or routing.
3. **Node IDs are opaque integers** mapped to MBIDs at the edges. Track-level pathing changes what a node *is* without changing the search.
4. **Edges are typed and the builder takes a source list** (§3.1). A second similarity source is a pipeline addition and a weight-tuning exercise, not a format migration. This is also what makes per-hop explanations and path steering tractable later.

---

## 8. Risks

### 8.1 Similarity data acquisition (primary risk)

No bulk similarity dump was confirmed to exist; the data may only be available per-artist from the Labs endpoint. A 75k-artist crawl is feasible if run politely and resumably, but is slow and depends on a third-party endpoint's continued availability and tolerance.

**The runtime exposure is nil.** The graph is a baked artifact; if ListenBrainz disappeared after a successful build, the app would serve paths indefinitely. The failure mode is staleness, not outage.

Two genuine exposures remain, with mitigations:

| Exposure | Mitigation |
|---|---|
| Source disappears **before** a first successful build | Build the graph first, before any application code. Nothing downstream is worth writing until the data is proven. |
| Source disappears later, and a rebuild needs re-crawling | Raw responses archived to S3 (§3.1 step 2). Rebuilds replay the archive; the network is never required twice. |

Longer-term independence comes from Tier 1 datasets (§1): MusicBrainz and Discogs publish full bulk dumps that, once downloaded, cannot be revoked. Alpha does not ingest them, but the typed-edge format (§3.1) means adopting one is additive. If ListenBrainz were permanently lost, MusicBrainz relationship data is a viable structural substitute — a different flavour of similarity, not a dead end.

**Implementation should begin with the builder.** Everything downstream assumes this data exists and is good; that assumption should be tested first, on real data, before the API or UI exist.

### 8.2 Path quality is subjective

The cost-function weights determine whether paths feel smooth. There is no automated metric for "sounds right".

*Mitigation:* weights are configuration, not code; tuning uses a set of hand-checked real paths; the smoothness test (§9) catches regressions against plain shortest-path but does not certify quality.

### 8.3 Catalogue coverage

75k artists is smaller than the original's 100k, and ListenBrainz's listener base skews differently from Echo Nest's. Obscure or non-Western artists may be missing.

*Mitigation:* accepted for a personal-use alpha. Autocomplete only offers artists that are in the graph, so the failure mode is "not found", never a broken path.

---

## 9. Testing

| Layer | Coverage |
|---|---|
| Builder | CSR construction, edge symmetrisation, largest-component extraction, name normalisation, edge-type tagging |
| Archive replay | A rebuild sourced entirely from the S3 archive, with the network unavailable, produces a byte-identical graph to the original crawl |
| Pathfinding | Against the fixture graph: every adjacent pair is a real edge; exclusions respected; identical queries deterministic; disconnection returns an explicit error; popularity smoothing measurably beats plain shortest-path on a smoothness metric |
| Bypass semantics | "Not for me" measurably reduces average similarity to the bypassed artist across the new path; "know them already" does not, and admits lower-popularity artists that the base floor would have rejected. Neither soft modifier can ever cause a "no path" result — only hard exclusion can. |
| Bypass regeneration | A reroll is free to change path length in either direction, and to drop artists other than the bypassed one. At least one fixture case must produce a **longer** path after a bypass — this is the regression test for `w_hop` being tuned too strongly and for local-repair creeping in. Successive bypasses must admit progressively lower-popularity artists. |
| API | Integration against fixture graph with mocked Deezer |
| Clip resolver | Mocked HTTP — fallback chain, cache hit/miss, missing-preview handling |
| E2E | One Playwright run: search → path renders → bypass → new path excludes the artist and is fully reconfigured, not a one-for-one substitution |

---

## 10. Evidence from prior art: the stopgap LLM prompt

After Boil the Frog went down, the author used a hand-written LLM prompt as a substitute ([`docs/reference/sample-ai-prompt`](../../reference/sample-ai-prompt)). It covers three use cases: artist-to-artist paths with bypass, the "centre" of three or more artists, and album-to-album recommendation. It worked with "varying success."

It is the best available evidence of what this product is actually for, and it drives four decisions.

### 10.1 The graph selects; the model narrates

Every use case in the prompt asks the model to *choose* the artists. That is almost certainly the source of the "varying success" — a language model asked to pick artists will hallucinate acts, misattribute genres, and cannot guarantee that what it names exists, is correctly identified, or has a playable clip.

**Constraint for all future GenAI work: the model must never select nodes.** Path selection belongs to the graph, which is verifiable, deterministic and guaranteed playable. The model's only job is to explain a path it has been handed. This inverts the prompt's structure while preserving its value, and it is the difference between a narration feature that works and a reproduction of the failure mode the prompt already exhibited.

The prompt's voice and format guidance remain directly reusable as a drafting brief for that narration layer.

### 10.2 Per-hop explanation is the priority future feature

All three use cases require a stated connection between neighbours, and the prompt's general guidelines are concerned almost entirely with explanation quality. Explanation is not decoration on top of the path — for this author it is a substantial part of the value.

Alpha still ships without it, deliberately: routing quality must be proven before meaning is layered on it, and an explanation of a bad path is worse than no explanation. But it should be the first feature considered after alpha, ahead of multi-artist pathing.

Note the dependency: a *factual* explanation ("both tagged shoegaze", "shared band member") needs the typed-edge and genre-tag data from a Tier 1 source (§1). This is a second reason the MusicBrainz ingest is the most likely next pipeline addition.

### 10.3 Path length is not specified

The prompt asks for 3–7 artists. **This was the author's guesswork at replicating the original and carries no evidential weight.** It must not be treated as a requirement, and an earlier draft of this spec wrongly adopted it as one.

Path length is an emergent property of the cost function, tuned by listening. Implementation should start `w_hop` at a value producing roughly five-artist paths purely as a place to begin, then tune on whether the *transitions* feel smooth — a longer path with good steps beats a short one that lurches. If tuning for smoothness consistently yields eight-artist paths, that is the answer, not a problem to correct.

### 10.4 Node granularity is genuinely distant

Use case 3 is album-based and the author has separately mentioned track-based pathing. Both are wanted eventually, as selectable modes.

They are, however, explicitly subordinate to §2.1. Albums and tracks are not scheduled and should not be planned toward. The opaque-node-ID seam (§7.3) is retained only because it costs nothing — internal IDs are integers regardless — and not as preparation for imminent work.

---

## 11. Open decisions

None blocking. Product name is undecided; the repository working name is `music-app`.
