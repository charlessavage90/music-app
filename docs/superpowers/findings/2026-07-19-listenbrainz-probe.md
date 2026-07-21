# ListenBrainz API Probe — Findings

**Date:** 2026-07-19
**Task:** Plan 1, Task 1 (gate) — `docs/superpowers/plans/2026-07-19-graph-builder.md`
**Verdict:** **GO**, with a required amendment to seed acquisition.

All results below are from live calls made on 2026-07-19. Recorded responses are committed under `builder/tests/fixtures/`.

---

## 1. Similarity endpoint — works as assumed

**Endpoint:** `https://labs.api.listenbrainz.org/similar-artists/json`
**Algorithm string confirmed working:** `session_based_days_7500_session_300_contribution_5_threshold_10_limit_100_filter_True_skip_30`

Probed with Radiohead (`a74b1b7f-71a5-4011-9441-d0b5e4122711`). HTTP 200, 21,151 bytes.

**Response shape:** a bare JSON array. Fields per row:

```json
{
  "artist_mbid": "5b11f4ce-a62d-471e-81fc-a69a8278c7da",
  "name": "Nirvana",
  "comment": "1980s–1990s US grunge band",
  "type": "Group",
  "gender": null,
  "score": 11156,
  "reference_mbid": "a74b1b7f-71a5-4011-9441-d0b5e4122711"
}
```

- Returns exactly **100 neighbours**.
- Every row has an MBID. No nulls observed.
- The plan's assumed `FIELD_MBID`/`FIELD_NAME`/`FIELD_SCORE` constants are **correct as written**. `_rows()`'s bare-array branch is the one that fires.

**Bonus:** `comment` carries MusicBrainz disambiguation ("1980s–1990s US grunge band"). Spec §3.1 step 6 wants disambiguation in the artist table and this supplies it free — no extra call needed.

### Scores need normalisation, as specced

Scores are unbounded co-occurrence counts, not a unit interval. For Radiohead the top-100 range was **4,223 – 11,156**.

Note the floor is high: dividing by the row maximum yields 0.38–1.0, not 0–1. Similarity differences are therefore compressed into the upper third of the range. This does not block anything, but **`w_sim` will need tuning against this real distribution**, and an alternative normalisation may prove better. Carry into Plan 2's tuning task; do not pre-optimise now.

---

## 2. Seed acquisition — BROKEN. The plan's approach does not work.

**Endpoint:** `https://api.listenbrainz.org/1/stats/sitewide/artists`

Response shape is exactly as assumed (`payload.artists[]` with `artist_mbid`, `artist_name`, `listen_count`), and `payload.total_artist_count` reports **10,469,538** artists.

**But the endpoint returns at most 1,000 artists, total.**

| Request | Artists returned |
|---|---|
| `count=100&offset=0` | 100 |
| `count=1000&offset=0` | 1000 |
| `count=2000&offset=0` | **1000** (silently capped) |
| `count=100&offset=900` | 100 |
| `count=100&offset=950` | **50** (hits the wall at 1000) |
| `count=1000&offset=1000` | **0** |
| `count=1000&offset=10000` | 0 |
| `count=1000&offset=74000` | 0 |

The cap is hard and silent — HTTP 200 with an empty array, never an error. `total_artist_count` advertises 10.4M while serving 1,000, which is a trap for anyone who trusts it.

**Consequence:** Plan Task 5, `cmd_seeds` in Task 11, and the `target_artist_count: 75_000` seeding strategy are all invalid as written. 1,000 artists is 1.3% of target.

---

## 3. The fix: snowball expansion, verified working

Discover artists by traversing the similarity graph itself, rather than requesting a ranked list.

1. Bootstrap from the top 1,000 (the sitewide endpoint's full output).
2. Breadth-first: each artist's 100 neighbours are candidates; add unseen MBIDs to the frontier.
3. Continue until 75,000 distinct artists are discovered.

**Verified:** five artists taken from the *tail* of Radiohead's neighbour list (Black Sabbath, Simon & Garfunkel, The Chemical Brothers, CAKE, Snow Patrol) each returned a full 100 neighbours and had listener statistics. Expansion does not dead-end.

This is arguably better than a popularity-ranked seed: it discovers exactly the artists that are *reachable*, which is what the graph needs, rather than a popularity list whose tail might not be connected.

**Caveat:** the artists probed were still fairly popular, being one hop from Radiohead. Coverage several hops out is unverified. **The 200-artist trial run in Task 11 step 5 must report component retention before the full crawl** — that remains the real test.

---

## 4. Popularity source found

Seeds no longer carry popularity, since snowballing bypasses the ranked list. Replacement:

**Endpoint:** `https://api.listenbrainz.org/1/stats/artist/{mbid}/listeners`

```json
{"payload": {
  "artist_mbid": "a74b1b7f-...",
  "artist_name": "Radiohead",
  "total_listen_count": 7088378,
  "total_user_count": 28057,
  "listeners": [ ... ]
}}
```

Works for any MBID. One call per artist.

### Recommendation: use `total_user_count`, not `total_listen_count`

Listen count is distorted by superfans. In Radiohead's own data, the single heaviest listener accounts for **135,184 of 7,088,378 listens** — one user is ~2% of the artist's entire total, and the top nine visible listeners account for a substantial further share.

`total_user_count` ("how many people listen to this artist") is a truer measure of *how well known* an artist is, which is precisely what spec §4.1's popularity term is for — it exists to keep paths among comparably-famous artists and to stop routes diving into obscurity. Obsessive-listener skew actively corrupts that.

**This is a change from the spec**, which says "log-scaled listen count". It should be amended to user count, with this rationale recorded.

---

## 5. Rate limits

Headers observed on `api.listenbrainz.org`:

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 26
X-RateLimit-Reset-In: 5
```

**30 requests per 5-second window ≈ 6 requests/second.** The plan's `requests_per_second: 5.0` default is appropriately conservative — keep it.

`labs.api.listenbrainz.org` returned no rate-limit headers; assume the same budget and stay polite.

### Revised crawl cost

Two calls per artist (similarity + listener stats) × 75,000 artists = **150,000 requests**.

At 5 req/s that is **~8.3 hours**. Overnight, resumable, checkpointed. Acceptable — and it runs exactly once, because every response is archived.

---

## 6. Required plan amendments

| Plan element | Change |
|---|---|
| Task 5 | Rewrite. `parse_seed_page` survives as the *bootstrap* parser (top 1,000 only). Its 75k-pagination role is gone. |
| Task 5 (new) | Add `parse_artist_stats(payload) -> ArtistStats` for the listeners endpoint. |
| Task 6 | Crawler becomes snowball-aware: the frontier grows from parsed responses rather than iterating a fixed list. Needs a discovery cap and a second archive keyspace, `stats/{mbid}.json`. |
| Task 2 | `SeedArtist.listen_count` → `user_count`. Add `max_discovered_artists`. |
| Task 7 | `_log_scaled` input becomes user count. Logic unchanged. |
| Task 9 | `build_from_archive` reads popularity from archived stats responses instead of a `seeds.json`. |
| Task 11 | `cmd_seeds` becomes `cmd_bootstrap` (top 1,000). Crawl subsumes discovery. |
| Spec §4.1 | "log-scaled listen count" → "log-scaled distinct-listener count", with the superfan rationale. |

Tasks 3, 4, 8, 10 are unaffected.

---

## 6a. Measured latency — supersedes the §5 crawl estimate

**Added 2026-07-20 after an instrumented trial crawl.** The §5 projection of ~8.3 hours was wrong because it assumed both endpoints were equally fast. They are not.

```
similar    0.37 – 1.94s    (mean ~1.1s)    no rate-limit headers present
stats     18.08 – 26.76s   (mean ~22.8s)   X-RateLimit-Remaining: 29 of 30
```

**We are not being throttled.** `remaining=29` shows one request consumed from a 30-per-window budget. The per-artist listeners endpoint is simply slow — it appears to compute the aggregate on demand. The Labs similarity endpoint, which §8.1 named as the primary risk, is fast and returns no rate-limit headers at all.

Observed end-to-end: ~25s per artist, i.e. ~0.27 req/s. At that rate 75,000 artists would take **~21 days**, not 8.3 hours.

The similarity crawl alone, with the stats call removed, is ~1.3s per artist: **~27 hours serial, ~7 hours at 4-way concurrency** (still only ~3 req/s against Labs).

### Why the §5 estimate was wrong

It was derived from request *count* without measuring request *cost*. Two endpoints were assumed interchangeable because both returned quickly to a handful of manual probes against very popular artists. Any future throughput estimate in this project must come from a timed run, not from arithmetic.

## 6b. Bulk popularity: no cheap source exists

Searched for a way to avoid 75,000 slow stats calls. Findings:

| Candidate | Result |
|---|---|
| `popular-artists-by-listeners` bulk endpoint | **HTTP 500.** Broken. |
| ListenBrainz spark dump | **191GB** (`listenbrainz-spark-dump-2593-20260712`) |
| MLHD+ (`/mlhd/`) | 16 × 15GB ≈ **240GB**, dated 2023 |
| `labs/artist-credit-artist-credit-relations` | Dated 2019–2020; six years stale |
| MusicBrainz postgres dumps | Full artist list and disambiguation, but **no popularity data** |

**Decision: process the 191GB ListenBrainz spark dump.** Chosen over cheaper proxies (similarity-graph in-degree, Deezer `nb_fan`) because it is authoritative, it is genuinely Tier-1 data ownership per §1, and it ends the dependency rather than working around it. Cost is a one-time AWS processing job, estimated $30–50.

**Consequence:** the similarity crawl and the popularity job become fully independent pipelines that both feed the graph build. The crawl no longer fetches stats and can run before the dump pipeline exists.

## 6c. The spark-dump plan is also wrong: raw listens carry no MBIDs

**Added 2026-07-20 after inspecting real dump files.** Before committing to the 191GB spark dump, two dumps were downloaded and inspected — the 235MB sample dump and a 216MB daily incremental listens dump.

**Raw listen records almost never carry a MusicBrainz artist ID.** In a 200,000-listen sample from the incremental dump:

| Field | Coverage |
|---|---|
| non-empty `mbid_mapping` | 65 / 200,000 = **0.03%** |
| any `artist_mbids` (incl. `additional_info`) | ~6.7% |

The rest carry only a free-text `artist_name` and Spotify IDs. Aggregating raw listens to per-artist popularity is therefore not viable: it would be biased toward whichever submitting clients happen to include MBIDs, and would miss 93%+ of listens outright.

**This invalidates the §6b decision** to process the spark dump — at least via raw listens. Whether the full spark dump ships a pre-computed, MBID-keyed popularity table (as the *sample* dump does) is unverified.

### What the sample dump does contain

The 235MB sample dump is not listens — it is metadata plus pre-aggregated tables:

- `popularity/top_recording.csv` — **keyed by `artist_mbid`** with `total_listen_count` and `total_user_count` per recording. Rolling up to per-artist max gives **5,255 distinct artists** with real distinct-listener counts. Values are sane (top artists: Nirvana, Gorillaz, Radiohead).
- `metadata/artists_cache.jsonl` — per-artist name, area, type, and **`tag_data`** (genre tags — the descriptive-edge data for the future "why" feature).
- `spark/*.parquet` — artist_credit, artist_genre, artist_tag, recording_artist, etc.

The sample covers only ~5k artists, so it cannot *be* the popularity source for a 75k graph. But it provides **two ground-truth sets for validating any popularity proxy**: these 5,255 artists with `total_user_count`, plus the 993 bootstrap artists with `listen_count` from §4.

### Decision: validate similarity-graph in-degree against ground truth

Rather than download 191GB on an unverified assumption, test the zero-cost proxy first. In-degree (how often an artist appears in others' similar-lists) is derived from data the crawl already fetches. Correlate it against the 5,255 known listener counts; adopt it only if the rank correlation is strong, fall back otherwise. Result recorded in §6d.

## 6d. In-degree validation: moderate, and does not scale up

**Added 2026-07-20.** Crawled real similarity data and correlated in-degree against the 5,255 ground-truth artists (Spearman rank correlation; the cost function cares about popularity *ordering*, not linear fit).

| Sources crawled | Overlap with truth | Spearman |
|---|---|---|
| 400 | 913 | 0.501 |
| 800 | 1,171 | 0.519 |
| 1,200 | 1,432 | 0.505 |
| 1,600 | 1,603 | 0.482 |
| 2,000 | 1,745 | 0.455 |

**The correlation does not improve with more sources — it drifts down.** The hypothesis that full-graph in-degree (75k sources) would be markedly stronger is falsified: adding less-popular source artists injects noise faster than it consolidates signal. In-degree caps around 0.5.

Score-weighted in-degree (sum of similarity scores rather than a count) scored 0.521 vs 0.501 at 400 sources — marginally better, so the formula is not the limiter.

**The top of the ranking is excellent, the mid-tail is noisy.** The ten highest-in-degree artists were Radiohead, Coldplay, The Beatles, Red Hot Chili Peppers, Muse, Gorillaz, Nirvana, Pink Floyd, Linkin Park, Arctic Monkeys — every one a genuine household name with a high listener count. In-degree reliably separates the famous from the obscure; it is imprecise in the middle.

**Also measured (a positive surprise):** the similarity endpoint runs at ~0.46s per call including politeness delay, not the 1.3s estimated. A full 75k similarity crawl is ~5.5–9.5h serial depending on politeness, feasibly less with modest concurrency.

## 6e. Deezer nb_fan is disqualified by population mismatch

**Added 2026-07-20.** Before adopting the moderate in-degree proxy, tested whether Deezer's `nb_fan` — a real popularity figure — does better. Looked up 250 ground-truth artists on Deezer by name (250/250 matched) and correlated `nb_fan` against ListenBrainz listener counts.

**Spearman: 0.089.** Effectively no correlation.

The cause is not bad data — it is the *wrong* data. Deezer's audience (large in France, Europe, Brazil) has a different shape from ListenBrainz's (Western, tech-forward). An artist's Deezer standing predicts almost nothing about their ListenBrainz standing.

This is decisive, and not only against Deezer. **The similarity graph is built from ListenBrainz listening sessions, so popularity must be measured on the same population to be coherent** in the cost function's `|pop(a) − pop(b)|` and floor terms. Any external popularity source imports a population mismatch. In-degree, computed from the similarity graph itself, is the only measure guaranteed to be population-consistent.

## 6f. Decision: in-degree is popularity for alpha

Every alternative has been empirically eliminated:

| Source | Measured result | Verdict |
|---|---|---|
| Per-artist stats API | ~23s/call → ~3 weeks (§6a) | too slow |
| Raw listen dumps | 0.03% carry MBIDs (§6c) | unusable |
| 191GB spark dump | unverified it has MBID-keyed popularity | not pursued |
| Deezer `nb_fan` | 0.089 correlation (§6e) | wrong population |
| **Similarity in-degree** | **~0.50, free, population-consistent** | **adopted** |

**Score-weighted in-degree** (sum of neighbour similarity scores) is adopted as the popularity signal for alpha: marginally better than a plain count, still free, computed from the archive during the graph build. No spark dump, no popularity pipeline, no external table.

The 0.50 correlation is against a noisy ground truth (max-listeners-on-top-recording from a partial sample), so it likely understates true quality. This is an alpha decision, not a permanent one: §2.1 blesses later work that *deepens* pathing, and a genuine ListenBrainz artist-popularity table — should one become obtainable — would be a drop-in improvement validated against the same ground truth. The archive retains everything needed to recompute.

## 6g. First real graph (5,000 artists): the approach works end-to-end

**Added 2026-07-20.** Crawled 5,000 artists (snowball from the top-1000 bootstrap, 0 failures) and built the first graph-scale artifact.

**Connectivity — excellent.** 4,998 of 5,000 artists in the largest connected component (99.96%); only 2 islands dropped. 335,142 edges, ~67 per artist, 3.5MB. Far above the ~80% retention that would have signalled a data problem.

**Popularity (in-degree) — sane.** Radiohead tops out at 1.0; the ordering matches intuition across the graph.

**Path quality — smooth journeys are achievable, and it was a tuning question, not a graph question.** Naive starting weights (`w_hop=0.3`) produced short paths that jumped through popular hubs — e.g. Miles Davis → Radiohead → Daft Punk, the exact shortest-path failure the original tool avoided. Rewarding strong similarity and making hops cheap fixed it. With `w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`:

- **Miles Davis → Duke Ellington → Louis Armstrong → Ella Fitzgerald → Frank Sinatra → Michael Bublé → Mariah Carey → Britney Spears → Rihanna → Kendrick Lamar → The Weeknd → Daft Punk** — jazz through crooner, pop, R&B, hip-hop to electronic, every step adjacent.
- **The Beatles → Fleetwood Mac → David Bowie → Brian Eno → Aphex Twin** — classic rock to electronic, with Eno as the natural bridge.

These are musically literate paths — the Boil the Frog effect, reproduced.

**Starting point for stage-2 tuning:** `w_sim=3, w_jump=1, w_floor=1, w_hop=0.02`. Not final — real tuning happens in stage 2 against the full graph — but a validated place to begin, not a guess.

**Caveat.** This 5k graph is top-heavy (snowballed from the most popular artists), so it does not yet test obscure-artist paths — the case where behavioural data is thinnest and structural edges (deferred, §1) may later be needed. That is the open question the full 75k crawl answers.

**UTF-8 verified** end to end: "Michael Bublé", "Beyoncé", "Sigur Rós" round-trip correctly through the artifact; earlier console mojibake was display-only.

## 7. Verdict

**GO.** Both data dependencies are live, CC0, well-shaped and adequately fast. The similarity data is richer than assumed (disambiguation included free). No fallback to MusicBrainz relationship data is needed.

The one broken assumption — seed pagination — has a verified replacement that is arguably better suited to building a *connected* graph.

**The genuine remaining unknown is coverage at depth.** Snowballing was confirmed one hop from a very popular artist. Whether it stays healthy 4–5 hops out, among artists with few listeners, is not yet known, and it is the thing that determines whether 75,000 artists is achievable or whether the graph plateaus lower. The 200-artist trial run must report component retention before the full crawl is authorised.

## 8. External corroboration — Korzeniowski et al. (2022), GNN artist similarity

**Added 2026-07-20.** Reviewed *"Artist Similarity for Everyone: A Graph Neural Network Approach"* (Korzeniowski, Oramas, Gouyon; Pandora/SiriusXM; TISMIR 5(1), DOI 10.5334/tismir.143), stored at `docs/reference/similarity.md`. Their *method* — training a GNN with triplet loss to embed artists — is not ours (we crawl the raw graph and do weighted pathfinding, no learned model), so the architecture does not transfer. Two of their **empirical findings** do, and both bear directly on decisions already recorded above.

**8a. Topology beats content — independent confirmation of the behavioural-only alpha bet (see §6f, §1).** Their headline result (Table 1): a GNN using *random features* — pure graph topology, no content whatsoever — outperforms a DNN using real audio/musicological features (NDCG@200 0.45 vs 0.24 on the open OLGA dataset; 0.52 vs 0.44 on their proprietary dataset). Their own summary: *"the graph topology is more predictive of artist similarity than content-based features."* We reached "behavioural graph first, layer structural/descriptive later" empirically from this probe; this is a second, orthogonal, peer-reviewed source landing on the same conclusion. Treat as corroboration, not new evidence — it does not change the plan.

**8b. Long-tail degradation — a named warning for the deferred obscure-artist question (see §6g caveat, [[crawl-resume]]).** Their central contribution is diagnosing that topology-reliant models degrade sharply for sparsely-connected (long-tail) artists, and their fix ("connection dropout") is an ML training trick that does **not** transfer literally to our pathfinding. What transfers is the *diagnosis*: obscure artists with few edges are exactly where topology-based similarity gets unreliable. This is the same open question §6g flags — the 5k graph is top-heavy and does not yet test obscure-artist paths. Concrete implications for the stage-2 weight-tuning pass on the full 75k graph:
- Expect path quality to degrade through low-degree nodes; that degradation is a known, documented effect, not a bug in our data.
- Consider whether the weights (`w_sim`, `w_jump`, `w_floor`, `w_hop`) should adapt to node degree, and whether obscure-artist paths lean on too many low-similarity jumps (their "similarity clique" finding: ~71% of true similarity links sit within 2 graph hops, so paths built from many weak long hops are suspect).
- If ear-testing stops scaling, **NDCG@200** is the field-standard quality metric (robust to sparsity/popularity bias); `builder/scratch/ground_truth.json` could feed it. Deferred, not alpha.
