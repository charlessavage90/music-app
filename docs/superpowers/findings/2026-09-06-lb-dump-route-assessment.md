# Computing our own artist similarity from ListenBrainz's listens — assessment (`LBD-`)

**Role: ACTIVE findings — the assessment that opened the `LBD-` track.** Written 2026-09-06 in
an exploratory session, at the owner's request, before any design existed; the owner's ruling
on it is recorded in `specs/2026-09-06-own-similarity-design.md`, which governs the track.
**Owns no figures**: every number is cited from
[`builder/analysis/2026-09-06-lb-dump-feasibility/README.md`](../../../builder/analysis/2026-09-06-lb-dump-feasibility/README.md)
(`LBD-P1`, `LBD-P2`) or from the document named beside it. Identifiers **`LBD-`**,
collision-checked across every ref 2026-09-06.

> ## ⚠ FORWARD CORRECTION to two frozen documents
>
> `findings/2026-07-19-listenbrainz-probe.md` §6c measured MBID coverage of ListenBrainz's
> listens at **0.03 %** and concluded "raw listen dumps … unusable"; the alpha design
> (`specs/2026-07-19-artist-path-alpha-design.md` §1 and §4.1) restated it as "raw listen dumps
> carry MBIDs on 0.03 % of records". **Both figures were measured on the JSON *listens* dump
> and are correct for that file.** They do not describe the **Spark/parquet** dump, which LB
> writes with its own MBID mapping joined in (`listenbrainz/listenstore/dump_listenstore.py`)
> and which its similarity job reads. `LBD-P1` measured that file at **73.8 %**. The two
> documents stay frozen; their `docs/README.md` rows now carry this warning. Nothing else in
> either document is affected — in particular §6d–6f's elimination of external *popularity*
> from the routing cost stands on its own reasons.

## The question

The owner asked (2026-09-06) for information, not a decision: what would it take to stop
consuming ListenBrainz's Labs `similar-artists` endpoint and instead compute similarity from
ListenBrainz's published listens — the effort, the benefits, downsides and risks of the
exploration, and what adopting the result would change about operating the app. Two motives:
the endpoint's algorithm is a closed enum with a hard 100-neighbour cap, and the crawl
extension (`CXA-`, reverted `CXR-`) made the app worse at surfacing obscure artists even
though it added exactly the artists the app wants. He asked that download size and time be
ignored.

## 1. Measured

**What we consume.** `builder/src/artistpath_builder/config.py:12-49`: the endpoint's
`algorithm` parameter is a closed enum of six strings, validated live 2026-07-29 (`CS-P0e`);
every value carries `limit_100`; only `threshold_10` and `threshold_15` exist.
`findings/2026-07-26-stranding-causes.md` §6 (`STC-6`) records that the **threshold**, not the
limit, is what leaves an obscure artist with a short list, and that its remedy — a lower
threshold — was **killed 2026-07-29** solely because the enum offers none.

**LB's algorithm is public.** `listenbrainz_spark/similarity/artist.py` at master
(metabrainz/listenbrainz-server, fetched 2026-09-06) is one Spark-SQL query; its semantics are
already the project's record in `findings/2026-07-30-lb-algorithm-semantics.md` (`LBS-`), which
still matches master. Inputs: mapped listens (`user_id, listened_at, recording_mbid,
artist_credit_mbids`) plus two MusicBrainz side-tables — recording length, and artist-credit
rows with `position` / `join_phrase` for the 0.25 featured-artist weight. Last substantive
commit to the file: 2023-03-18. The `filter_True` token in every deployed algorithm name has
no counterpart in current source (`LBS-2`, unchanged).

**Coverage, corpus, cadence, licence** — `LBD-P1` and the README's pinned inputs: 73.8 % of
one day's parquet listens carry a mapped recording MBID; 7.77 M listens, 21,267 users and
142,683 distinct artists in that day; the full parquet dump is 213 GB, cut on the 1st and
15th; daily incrementals ~370 MB; deletions are absent from incrementals (LB docs); sitewide
total 2.70 billion listens; LB regenerates its own similarity every Sunday; the dump ships
`COPYING` = CC0 1.0. The MusicBrainz side-tables come from `mbdump.tar.bz2` (7 GB).

**Cost** — `LBD-P2`: the session and pair stages over one day run in 6.4 s on the owner's
machine in DuckDB; median session 3 listens; LB's listen-level self-join yields ~101 M pair
rows per day, a distinct-artist join ~17.6 M. **Two runs ordered on `listened_at` alone
differed in the fourth significant figure** — the order is not total when a user logs several
listens in one second — and the probe now orders on `(ts, recording_msid)`.

**Integration seam.** `sources/base.py` is a `SimilaritySource` protocol; the alpha design
(step 1 of §3) anticipated "bulk dump if one exists". The archive is keyed
`similar/<source>/<algorithm>/<mbid>.json` (`crawl.py:109-118`), `build` reads only the archive
and is offline by test, and names/disambiguations are harvested from neighbour rows
(`sources/listenbrainz.py:25`, `harvest_identities`) — a bulk source has no such rows and
would take them from the MusicBrainz artist dump already on disk. `build` refuses without
fame records unless `require_fame=False` is pinned (`config.py:132`,
`pipeline.py:446`), and `check_acceptance` runs before `serialise` with bounds keyed to the
production population (`cli.py:268`; `criteria` is deliberately not a flag, `cli.py:303`).

**API-side constraints a larger graph meets.** App Runner at 1 vCPU / 2 GB
(`infra/README.md:534`); pure-Python `heapq` Dijkstra (`api/…/pathfinding.py:9`); the Gate 2→3
review measured median 419 ms / max 859 ms between random or obscure pairs on the 75k
artifact, on a laptop (`findings/2026-07-27-gate2-gate3-team-review.md`).

**What the expansion did** — `builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`,
cited not restated: the added artists' median degree was a fraction of the existing
population's and a fifth of them had exactly one edge (`CXR-P2`, `CXR-M5`); the fame ramp's
top-to-middle gap shrank by about a fifth (`CXR-M4`); the popularity currency did not move
(`CXR-P3`); **the depth-0 half of the owner's report is unexplained** (closed as an item by
owner ruling 2026-09-04, measurement untouched).

## 2. What I infer — labelled, in app terms

**The route is far smaller than the record made it look.** The one blocker written into the
design was false for the file that matters, and the Spark job fits in one DuckDB query that
runs in seconds per day of listens. My estimate for one full-history run on the owner's
machine is one to a few hours, defensible to no better than 3× until one exists. No AWS, no
Spark: the alpha design's "$30–50 AWS job" is obsolete.

**Which half of the degradation this addresses.** The added artists are cul-de-sacs because
under LB's fixed rules an obscure artist rarely makes anyone's top-100 and most of its pairs
fall below the strict `score > 10` bar — three devoted co-listeners under production, four
under `ALG-B` (`LBS-4`, inference). Owning the computation removes both constraints — the
remedy `STC-6` named and had to kill. **It does nothing for the other half:** the fame ramp
re-frames itself on whatever population it is given, so a larger population squeezes it again
unless the router changes too (the `CXR` README's second candidate fix). Nothing here touches
the depth-0 complaint. *This route can give the app many more roads into obscure artists; it
cannot by itself make the app choose to drive down them.*

**The ceiling is the listener population, not the algorithm.** ~21k active listeners a day is
a small town. Lowering the threshold trades "three people co-listened" for "two"; past some
point there is no more signal. The one thing that moves that ceiling is a larger behavioural
corpus — the same pipeline, once source-agnostic, could ingest MLHD+ (27 B listens, 583k
last.fm users, MBID-keyed, ≤ 2014), which LB itself uses for recording similarity. A door,
not a proposal.

**"Apply drop lists before similarity" mostly dissolves.** Today an unlistenable artist
consumes a top-100 slot; without a cap there is no slot, and a pair's score does not depend on
any third artist, so dropping X before or after pairing leaves everyone else's scores
unchanged. What becomes possible instead: filtering *listens* (bots — the day's top user
logged 1.5 M) or users before sessioning, and choosing the featured-artist weight ourselves.
A real but modest gain.

**Population becomes a decision instead of an accident.** Today it is whatever a snowball
from the top 1,000 reaches; from the dump it is every artist with any above-threshold pair —
plausibly several hundred thousand at threshold 10, more below. The API figures above say a
5–10× larger graph is seconds per request on 1 vCPU in pure Python, so **adoption at scale
carries a router-performance or hosting change with it**, or the population rule keeps the
graph near today's size and the gain is *which* artists are in it.

**Fame comes free, and that is a currency hazard.** Distinct-listener counts fall out of the
same pass, population-consistent, and would retire the per-artist `fame` API stage. But
`fame_lb` is an adopted proxy with rulings around it (no cross-currency re-reads, 2026-08-02),
and `CXR-M4` shows what moving the ruler under the router costs. A separate decision with its
own pre-registration.

## 3. Level of effort

| stage | what | effort | settles |
|---|---|---|---|
| `LBD-S0` | coverage and per-day cost probes | **done 2026-09-06 (~1 h)** | data does not block the route |
| `LBD-S1` | acquire the parquet dump and `mbdump`; extract recording length and artist-credit rows | ~1 session (download excluded) | inputs exist locally |
| `LBD-S2` | faithful DuckDB reimplementation; full-history run at `ALG-B`'s parameters; fidelity check against the crawl archive we hold | 1–2 sessions, several multi-hour runs | how close "ours" is to "theirs"; whether the cost estimate holds |
| `LBD-S3` | vary what the enum forbade; emit archives in the existing key scheme; census with existing instruments | 2–3 sessions, behind a pre-registration | whether the `CXR` added artists stop being cul-de-sacs |
| `LBD-S4` | adoption: population rule, manifest pinning, refresh procedure, blind listen (`REQ-38`) | 2–3 sessions plus the owner's ear | whether it ships |

**Cheapest decisive experiment** (the project's standing rule): `S2` plus one `S3` arm —
recompute at `ALG-B`'s parameters with the cap removed and the threshold lowered, and measure
the degree of exactly the `CXR` added artists. If their median does not move, the route cannot
fix the cul-de-sac problem and the rest need not be built.

## 4. Benefits, downsides, risks

### Exploration

**Benefits.** Every parameter LB fixed becomes ours, including the two the record identifies
as the supply constraint. The crawl archive is a free ground truth for the reimplementation.
Iteration drops from a rate-limited multi-hour crawl to a local batch. All inputs are CC0 and
possessed — Tier 1 in the alpha design's own terms.

**Downsides.** New tooling surface (DuckDB, parquet, `mbdump` TSV). ~230 GB local. Each
full-history run is hours, so a sweep is a day or more of wall-clock.

**Risks.** (1) **No one-knob baseline against the served map** — our recomputation at LB's
parameters will not reproduce LB's lists (snapshot date, `filter_True`, mapping churn,
deletions); the design makes *our* LB-parameter run the baseline for every arm and reports
the LB-vs-ours gap as a separate measured fact. (2) **Scope creep into algorithm design** —
reimplement LB's first; any new formulation is its own pre-registered track. (3) **Semantic
drift** — the distinct-artist join is a 6× saving and a different count; decided explicitly,
once. (4) The all-history cost estimate may be off by a few ×.

### If adopted — operating the app

**Benefits.** No live dependency on the Labs endpoint, the bootstrap endpoint, the rate limit
or the enum; LB changing its dataset can no longer alter our graph unasked (the `RC-H3`
class goes away). Refresh becomes a local, reproducible batch pinned to a dump id and a
parameter string in the manifest — `resolve_build_inputs` already exists for this. Fame and
popularity can come from the same pass. Determinism holds given a total ordering; `build`'s
offline rule is untouched because the bulk source writes an archive.

**Downsides.** A standing stage that takes hours, not 40 s; 213 GB + ~135 GB/yr local disk,
and a full re-download twice monthly if deletions matter. LB's Sunday regeneration no longer
reaches us. The mapping bias is inherited, not fixed — the unmapped 26 % concentrate where
MusicBrainz is thin, the obscure end, exactly as with the endpoint. Bot and user filtering
becomes ours.

**Risks.** (1) **API cost and hosting** — decided by the population rule. (2) **The
population rule is a product decision** with no precedent in the record. (3) **Currency
changes ride along unless fenced** — fame source, popularity basis, the ramp's frame. (4) The
gain is supply-side; with the router unchanged `CXR-M4` predicts the squeeze recurs.

## 5. Weakest link

The case rests on one inference: *that the added artists' low degree is caused by LB's
threshold and cap rather than by there not being enough co-listening to find.* If the second
is true, removing the constraints yields edges resting on two people, the cap rule prunes
them, and nothing improves. `S2` plus one arm falsifies this before any integration work.
Defended: the coverage figure, the per-day cost, the licence, the seam. Abandoned cheaply:
the full-run time and any guess at the resulting population size.

## 6. Not checked

LB's production bot/user filtering; the all-history `(user, pair)` row count; row counts of
`recording` and `artist_credit_name` in `mbdump`; whether the deployed `filter_True` dataset
differs from master beyond the token.

## 7. Outcome

The owner ruled the same day: **worth investigating through `S3`, with `S4` a separate
decision on `S3`'s read.** The governing document is `specs/2026-09-06-own-similarity-design.md`;
the operational one is `plans/2026-09-06-lb-dump-exploration.md`.
