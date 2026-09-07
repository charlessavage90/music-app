# Own similarity from ListenBrainz's listens — design (`LBD-`)

> ## ⚠ REVIEWED 2026-09-06 — §0 CONTAINS A FALSE CLAIM AND §4 RESTS ON IT.
>
> Outcome: [`../findings/2026-09-06-lbd-plan-review.md`](../findings/2026-09-06-lbd-plan-review.md).
> **This document is unedited below this banner** — the corrections belong to the
> pre-registration (plan Task 2), which is committed before results exist and is therefore
> where a threshold or control can still be fixed honestly. Do not "fix" §0 or §4 in place.
>
> - **§0: "`LBD-C2` … in degree, which is population-independent for a given cap rule" is
>   false**, measured. Same MBIDs, same cap rule, no knob turned — a larger population alone
>   moves the supply reading, in the direction that flatters every arm. Magnitude and the
>   free control are owned by
>   [`builder/analysis/2026-09-06-lbd-plan-review/`](../../../builder/analysis/2026-09-06-lbd-plan-review/README.md).
> - **§0's drop-list row cannot hold.** Every arm must set `drop_unlistenable=False` or the
>   build refuses outright; the lists then stay constant across arms but are no longer the
>   served map's filtering.
> - **§0's held-constant degree ceiling is a dormant term.** Its *effect* grows in exactly
>   the arms that succeed — the shape §0 was written to catch, inside §0 itself.
> - **§4's `LBD-C1` does not define "our top-N"**, and the two readings differ by more than
>   any plausible lineage gap. §4's supply criterion also names `CXR-P2` as the baseline;
>   per §6 the baseline is the arm's own run, and `CXR-P2` is context.
>
> **What the review did not touch:** the track's ruling, its stages, `LBD-D1`–`D8`, and §9's
> closed list all stand.

**Role: ACTIVE, governing for the `LBD-` track.** Written 2026-09-06 from the assessment in
[`../findings/2026-09-06-lb-dump-route-assessment.md`](../findings/2026-09-06-lb-dump-route-assessment.md)
and the owner's ruling on it the same day. The operational document is
[`../plans/2026-09-06-lb-dump-exploration.md`](../plans/2026-09-06-lb-dump-exploration.md);
**this document governs where the two disagree.** Owns no figures —
[`builder/analysis/2026-09-06-lb-dump-feasibility/README.md`](../../../builder/analysis/2026-09-06-lb-dump-feasibility/README.md)
owns today's; later stages own theirs under `builder/analysis/`. Identifiers **`LBD-`**
(design decisions `LBD-D`, criteria `LBD-C`, measurements `LBD-M`, stages `LBD-S`,
risks `LBD-R`), collision-checked across every ref 2026-09-06.

**The owner's ruling, 2026-09-06, verbatim in substance:** *worth investigating through stage
3 or 4; the estimated sessions are not a huge scope against the potential improvement; the
risks are noted and will be planned for if adopted to production.* Read here as: **`LBD-S1`
through `LBD-S3` are approved; `LBD-S4` is a separate decision taken on `S3`'s read.** He has
started the dump download (his precondition, `D:\unsung-large-data\`).

---

## §0 — What this track holds constant, and why each is genuinely constant

Every comparison the track makes is between two **graphs built from different similarity
tables**. Per `CLAUDE.md`'s rule, the constants are enumerated with the reason the
intervention cannot move them — and the one term that is *not* constant is named first,
because it is the confound every read must carry.

**NOT constant — the population.** A similarity table computed from the dump names a
different artist set from the crawl's, and every population-relative quantity recomputes over
it: `pop_raw` (score-weighted in-degree), `fame_lb_pctl` (percentile within the artifact,
`graph_store.fame_percentiles`), `degree_hub_penalty` (top-1 %-by-degree), and the p99
rescale of every similarity score. This is exactly `CEX-` design §5's situation, and the
same rule applies: **no read may attribute a difference to the similarity parameters alone
while the population also moved.** `LBD-C2` is therefore stated over a *fixed* artist set
(the `CXR` added artists) and in degree, which is population-independent for a given cap rule.

| held constant | why the intervention cannot change it |
|---|---|
| cap strategy `trimmed_union`, `top_j`, `degree_ceiling` (`BuilderConfig`) | applied by `build` after the similarity table; a bulk archive enters `build` at the same point as a crawled one |
| similarity rescale `p99_log_clip` | the only strategy `BuilderConfig.__post_init__` permits; the scale is recomputed per build and that recomputation is part of the population confound above, not a knob |
| the drop lists (`ULF-` unlistenable, no-release, featured-credit) — **pinned per invocation to the lists the served map was built with** | `build` applies them by MBID before the mass computation; the track passes `unlistenable_list_path` explicitly (`SEL-` override) rather than relying on the default — `L4-T1` repointed that default back to the 2026-08-05 list on 2026-09-06, and pinning makes the build independent of it either way |
| router weights and cost function (`ApiConfig`) | nothing in `builder/` writes them |
| the fame source for any routing measurement — the existing `fame` stage (LB per-artist API) | dump-derived listener counts are a different currency; **`LBD-D4` bars their use for routing reads inside this track** |
| the endpoint archive under `builder/scratch/` | read only, as the fidelity ground truth |

**A term inert today for a reason the intervention removes:** `w_floor`'s dormancy and the
ramp's frame both depend on the *population*, which moves. They are not knobs the track
turns, but they are not constants either — they are the second half of the `CXR` mechanism,
and any routing read in `S3` (if reached) must say which of its effect is theirs.

## §1 — What this is

Today's similarity edges come from one closed source: the Labs `similar-artists` endpoint,
whose `algorithm` is a six-value enum with a hard 100-neighbour cap and a threshold no lower
than 10 (`config.py:12-49`, `CS-P0e`). `STC-6` established that the threshold, not the cap, is
what leaves an obscure artist with almost no neighbours — and that the remedy was outside our
control. The `CXR-` diagnosis then showed the added 29,892 artists arriving with a fraction of
the connections the existing population has, one fifth with exactly one.

ListenBrainz publishes both the listens its similarity job reads (Spark/parquet dump, CC0,
with its MBID mapping applied — `LBD-P1`) and the job itself (`listenbrainz_spark/similarity/artist.py`).
**This track reimplements that job locally, validates it against the lists we already hold,
and then turns the knobs the enum forbade** — to find out whether the obscure artists' low
degree is a property of the rules or of the listening.

It is **supply-side only.** The `CXR` README names two mechanisms; the fame-ramp squeeze is
router-side and is not this track's (§9).

## §2 — Stages

| stage | deliverable | owner stop? |
|---|---|---|
| **`LBD-S0`** — feasibility probes | done: `LBD-P1`, `LBD-P2` | — |
| **`LBD-S1`** — inputs | the full parquet dump verified by sha; `mbdump`'s `recording` (length) and `artist_credit_name` (position, join phrase) extracted to parquet; the MB artist names source identified; all identities pinned in an analysis README | — |
| **`LBD-S2`** — faithful reimplementation and fidelity | `lbd_similarity.py` (DuckDB, frozen, parameterised on LB's six tokens); a full-history run at `ALG-B`'s parameters; **`LBD-C1`** read against the crawl archive; **`LBD-C3`** run-time recorded | **handoff seam** |
| **`LBD-S3`** — the forbidden knobs | pre-registered arms (cap removed; threshold below 10; others per pre-registration); per-arm pair tables → archives via the bulk source → builds → **`LBD-C2`** read over the `CXR` added artists | **owner stop: the `S3` read and the `S4` decision** |
| **`LBD-S4`** — adoption (not approved by this ruling) | population rule; manifest pinning; refresh procedure; API sizing; `REQ-38` blind listen | owner's |

## §3 — Design decisions fixed now

**`LBD-D1` — Reimplement LB's job first, faithfully; design nothing new until it matches.**
The fidelity check is the only calibration available, and a novel formulation would have no
ground truth. Any new similarity formulation is a separate pre-registered track (§9).

**`LBD-D2` — DuckDB on the owner's machine, not Spark, not AWS.** `LBD-P2` measured the
per-day cost at seconds; the machine has 32 GB and >1 TB free on D:. Spark on Windows and an
AWS job are both cost without a reason. If the all-history aggregation does not fit, the fix
is chunking by user-id range, which DuckDB and the data's shape both allow.

**`LBD-D3` — Outputs land as an archive in the existing key scheme; `build` is untouched.** A
bulk source writes `similar/<name>/<algorithm>/<mbid>.json` payloads in the endpoint's own
shape (`artist_mbid`, `name`, `comment`, `score`) so that `ListenBrainzSource.parse` and
`harvest_identities` read them unchanged. Names and disambiguations come from the MusicBrainz
artist dump (`builder/scratch/mb-json-dumps/artist`, 2026-07-28), which `LUX-4`'s extractor
already parses. **The bulk source is a *second* `SimilaritySource` with its own `name`** — it
must not be a seventh `PERMITTED_ALGORITHMS` value, because that enum documents what the
endpoint accepts and a bulk token would falsify the comment above it.

**`LBD-D4` — No currency changes inside this track.** Fame for any routing read is the
existing `fame` stage over the arm's population, or the read is not made. Dump-derived
listener counts, in-degree redefinitions and any ramp re-framing are each their own
pre-registration. Exploration builds that need no fame (degree census) pin
`require_fame=False`, as the three harnesses under `builder/analysis/` already do
(`config.py:128-132`).

**`LBD-D5` — Determinism: a total order, and every input pinned.** LB's SQL orders listens
by `listened_at` alone, which is not a total order; `LBD-P2` showed two runs differing on it.
`lbd_similarity.py` orders on `(listened_at, recording_msid)` and its output on
`(mbid0, mbid1)`. The archive's manifest records the dump id and sha, the incremental ids
applied, the `mbdump` timestamp, the MB artist dump timestamp, and the parameter string —
in a `MANIFEST.json` at each archive root, written by the emitter. `resolve_build_inputs`
(`manifest.py`, landed on `main` with `LUX-4`, PR #105, 2026-09-06) is the builder-side
pattern for recording build inputs; the archive manifest is what a future `S4` integration
would feed it. `S1`–`S3` build in-process and do not call it.

**`LBD-D6` — The pairing semantics are decided in `S2`, explicitly, once.** LB self-joins
listens within a session; the obvious optimisation self-joins distinct artists. `LBD-P2`
measured the row-count gap at ~6×. The fidelity run uses LB's semantics; `S2` then measures
the delta of the cheaper form on the same input and records which one every later arm uses.

**`LBD-D7` — Acceptance is never widened; exploration builds pass their own criteria
in-process.** `check_acceptance` runs before `serialise` with production bounds (`cli.py:268`),
and `criteria` is deliberately not a flag (`cli.py:303`). The track calls `main(argv,
criteria=…)` or `build_from_archive` directly with scaled criteria, as the tests do, and never
touches `PRODUCTION_ACCEPTANCE`. Nothing built here is a candidate for serving.

**`LBD-D8` — Nothing here writes into `builder/scratch/`.** The dump, extracts, pair tables
and archives live under `D:\unsung-large-data\`; the endpoint archive and the graphs under
`builder/scratch/` are read by absolute path. This is what lets the track run from a worktree
beside a live builder session.

## §4 — Criteria the pre-registration must fix (shape here, values there)

The pre-registration is `S2`'s first task (`plans/…` Task 2) and is committed **before**
the reimplementation runs. It owns the thresholds and effect sizes. This section fixes only
the *shape* and the plain sentence of each, so a pre-registration that drifts from them is
visible.

- **`LBD-C1` — fidelity.** *Plain sentence: when we compute similarity the way ListenBrainz
  says it does, using their own listens, how much of what they told us about each artist do
  we get back?* Measured as the overlap between our top-N for an artist and the archive's
  list for that artist, over a fixed, pre-named sample of archive artists spanning fame
  bands. **The pre-registration must state the read of a low overlap** — it is *expected* to
  be imperfect (§6), and a low figure is a finding about the gap, not a failure of the track,
  unless it falls below a floor the pre-registration names.
- **`LBD-C2` — supply.** *Plain sentence: do the ~29,900 artists the crawl extension added —
  the ones that arrived with almost no connections — get more connections when the list cap
  and the threshold are ours?* Measured as the median degree and the share with ≤ 2 edges of
  **exactly the `CXR` added set** (its MBIDs are read from the two artifacts, not re-derived),
  in each arm's built graph, against the `CXR-P2` figures cited from their owner. The
  pre-registration fixes the effect size that counts as movement.
- **`LBD-C3` — cost.** *Plain sentence: how long does one full run take on this machine?*
  Descriptive; the pre-registration names the figure above which `LBD-D2` is revisited.
- **`LBD-M1` — population.** *Plain sentence: how many artists does each arm produce, and
  how does that compare with the served map's 58,838?* Descriptive; feeds `S4`, decides
  nothing here.

Every arm carries its own plain sentence beside its parameters, per `CLAUDE.md`.

## §5 — Seams and owner stops

- **Seam after `S2`'s fidelity run.** Its outputs are committed artifacts (the pair table's
  identity, `LBD-C1`'s figures, `LBD-C3`); the next session reads them cold.
- **Owner stop at the end of `S3`.** The `LBD-C2` read is his; so is whether `S4` opens. A
  session does not begin `S4` work on its own reading of `S3`.
- **Mid-flight seams** on the usual triggers (`CLAUDE.md`, the degradation tell).

## §6 — The comparison to LB's own lists is confounded, and no read may pretend otherwise

Our recomputation at `ALG-B`'s parameters will **not** reproduce the archive's lists, for
reasons that are not knobs: the archive was fetched from a dataset computed on an unknown
date, over listens as mapped then; the deployed algorithm carries a `filter_True` token
current source does not emit (`LBS-2`); deletions are absent from incrementals; bot handling
upstream of LB's job is unknown; the endpoint serves a union of two lexical partitions
(`LBS-3`). **So `LBD-C1` measures a gap, and the gap is a fact about the data lineage, not
about our code — unless a controlled sub-check says otherwise.** The pre-registration must
include one such sub-check: a tiny synthetic listen set whose LB-style scores are computable
by hand, which the reimplementation must match exactly. That separates "we implemented it
wrong" from "the inputs differ".

**Consequently every `S3` arm's baseline is *our own* `ALG-B`-parameter run**, differing from
it by exactly the columns the factor table shows, and never the archive.

## §7 — Risks, and the stage that retires each

| id | risk | retired by |
|---|---|---|
| `LBD-R1` | the low degree is the listening, not the rules — nothing moves | `S3`'s first arm; the null read is pre-registered |
| `LBD-R2` | the reimplementation is wrong in a way the lineage gap hides | §6's synthetic sub-check, `S2` |
| `LBD-R3` | all-history aggregation does not fit or takes days | `LBD-C3` in `S2`; `LBD-D2`'s chunking fallback |
| `LBD-R4` | semantic drift from the cheaper pairing form | `LBD-D6`, measured in `S2` |
| `LBD-R5` | a currency change rides along unnoticed | `LBD-D4`; the factor table's held-constant section |
| `LBD-R6` | scope creep into algorithm design | `LBD-D1`; §9 |
| `LBD-R7` | a much larger population makes the API slow or the artifact large | not this track's — named as an `S4` input with the Gate 2→3 review's figures as its baseline |
| `LBD-R8` | the mapping bias (unmapped 26 %, concentrated at the obscure end) limits the gain | inherited from the endpoint, not new; `LBD-M1` by fame band will show its extent |
| `LBD-R9` | bots and heavy users distort pairs | LB's `contribution` cap bounds it; whether LB filters upstream is an `S2` check, and a user-level filter is an `S3` arm only if pre-registered |

## §8 — What adoption would change about operating the app (for `S4`'s reader)

Recorded from the assessment so `S4` starts from a list, not a memory. No live dependency on
the Labs endpoint, the bootstrap endpoint, the rate limit or the enum; refresh becomes a
local batch pinned to a dump id and parameter string; a standing stage of hours in front of
the archive replay, which itself takes minutes (`LUX-4` measured 297 s and 616 s on
2026-09-06; the earlier ~40 s figure is overturned); ~213 GB + ~135 GB/yr on local disk, a full re-download twice monthly if deletions
matter; LB's Sunday regeneration no longer reaches us; the population rule becomes a product
decision; the API's hosting or router may need to change with it; fame and popularity could
come from the same pass, each behind its own decision.

## §9 — CLOSED for this track — what it does not reopen

- **The fame-currency rulings** (2026-08-02: no cross-currency re-reads; `FPC-` pairing
  rule). Dump-derived fame is a future pre-registration, not an `LBD-` arm.
- **`ALG-B` as the adopted lineage**, and `BuilderConfig.algorithm`'s deliberate ALG-E default
  (`CEX-R5`). This track adds a source; it does not touch that enum or that default.
- **`DD-F1`** and the depth-0 ruling of 2026-09-04. Nothing here is evidence about either.
- **The router-side `CXR` candidate fixes** (degree floor at admission; a fame ruler framed
  off the shipped population; a deeper crawl). Each needs its own pre-registration; `S3`'s
  read may *motivate* one and must not *run* one.
- **The cap-rule decision** (Track B's `R1` as its input; parked). `trimmed_union` and its
  knobs are held constant here.
- **MLHD+ and any other corpus.** Named in the assessment as a door; not opened.
- **A new similarity formulation.** `LBD-D1`.

## §10 — Out of scope, deliberately

Serving anything built here; changing `PRODUCTION_ACCEPTANCE`; the population rule beyond
what `LBD-M1` needs to describe; API performance work; the "Unsung" rename; anything under
`frontend/`.

## §11 — Claims check (grepped 2026-09-06, re-resolved after `LUX-4` merged at `422530b`)

`SimilaritySource` — `builder/src/artistpath_builder/sources/base.py`. `ListenBrainzSource`
(`:54`), its `parse` (`:65`), `harvest_identities` (`:25`) — `sources/listenbrainz.py`.
`Crawler.similar_key` — `crawl.py:109`. `similar_prefix`, `archive_artists`,
`build_from_archive` — `pipeline.py:131,147,169`; the nameless drop — `pipeline.py:235`.
`require_fame` — `config.py:132`; `load_fame` — `fame.py:198`; `fame_key` — `fame.py:91`.
`AcceptanceCriteria`, `PRODUCTION_ACCEPTANCE`, `check_acceptance` — `acceptance.py:54,118,259`;
the call site and the not-a-flag docstring — `cli.py:268,301`. `CANDIDATE_ALGORITHM`,
`PERMITTED_ALGORITHMS`, `PERMITTED_CAP_STRATEGIES`, `unlistenable_list_path` —
`config.py:26,35,55,259`. The three drop-list loaders — `no_release_drop.py:93`,
`featured_credit_drop.py:72`, `unlistenable_drop.py:151`; `LocalArchive` — `archive.py:28`.
`resolve_build_inputs`, `log_build_inputs` — `manifest.py:67,133`, on `main` since PR #105.
`fame_percentiles` — `api/src/artistpath_api/graph_store.py:95`. `build_from_archive` does **not** call
`check_acceptance` — only `cmd_build` does (`cli.py:268`) — so harness builds are never
acceptance-checked and never written as servable artifacts; the five harnesses under
`builder/analysis/` that call it directly are the precedent
(`2026-07-29-algb-trial-build/grt_score.py:244` pins `require_fame=False` and all three drop
flags explicitly).
`cxr_census.py` — `builder/analysis/2026-09-01-cxr-regression-diagnosis/`. `lux4_extract.py` —
`builder/analysis/2026-09-05-lux4-extract/`. The `JFX` routing harness —
`builder/analysis/2026-08-09-jfx-prereg-critique/jfx_route.py`. LB source:
`listenbrainz_spark/similarity/artist.py`, `listenbrainz/listenstore/dump_listenstore.py` at
metabrainz/listenbrainz-server master, fetched 2026-09-06.
