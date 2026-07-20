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

## 7. Verdict

**GO.** Both data dependencies are live, CC0, well-shaped and adequately fast. The similarity data is richer than assumed (disambiguation included free). No fallback to MusicBrainz relationship data is needed.

The one broken assumption — seed pagination — has a verified replacement that is arguably better suited to building a *connected* graph.

**The genuine remaining unknown is coverage at depth.** Snowballing was confirmed one hop from a very popular artist. Whether it stays healthy 4–5 hops out, among artists with few listeners, is not yet known, and it is the thing that determines whether 75,000 artists is achievable or whether the graph plateaus lower. The 200-artist trial run must report component retention before the full crawl is authorised.
