# `LBD-` plan review — claims against the repo, and the measurement derivation

**Role: FIGURES OWNER for the `LBD-` plan review. ACTIVE.** Every new figure produced by
this review is owned in [`measurement-derivation.md`](measurement-derivation.md) beside this
file and is **cited elsewhere, never restated** — including by
[`findings/2026-09-06-lbd-plan-review.md`](../../../docs/superpowers/findings/2026-09-06-lbd-plan-review.md),
which is the readable entry point and deliberately carries no numbers of its own.

Two reviews of the committed `LBD-` design and plan, run 2026-09-06 at the owner's request
before any arm executes. **Neither review changed a project document**: the design's §0 and
§4, and the plan's tasks, are exactly as they were. What the reviews found is recorded here
and pointed at from the documents they concern.

| review | what it checked | verdict |
|---|---|---|
| [`claims-review.md`](claims-review.md) | every path, function, flag and line number the design's §11 and the plan's self-review cite; three load-bearing mechanisms; Task 3's SQL against ListenBrainz's own source | **not executable as written** — 8 findings, `F1` and `F2` are false premises |
| [`measurement-derivation.md`](measurement-derivation.md) | whether `LBD-C2` is population-independent; whether overlap is the right shape for `LBD-C1`; the effect size distinguishable from rebuild noise; whether Task 5's arms separate `LBD-R1` from the rules | **§0's population-independence claim is false**, and the two suggested arms cannot support the conclusion they exist to test |

**The two reviews were run independently and did not see each other's work.** They converged
on the same blocker by different routes — `claims-review.md` `F1` by tracing the mechanism,
`measurement-derivation.md` Q4 by grep while measuring supply. That convergence is the
strongest single result here, and it is why the blocker is stated as certain rather than
likely.

## Inputs, pinned

Artifacts under `builder/scratch/` are **gitignored and not interchangeable**; every one was
sha256-verified against its own `.bin.json` manifest sidecar before being read. The full
table with hashes, node counts and CSR entry counts is
[`measurement-derivation.md`](measurement-derivation.md) § "Artifacts and inputs used" —
owned there, not restated here.

| input | identity |
|---|---|
| artifacts read | `graph-msw-tu50.bin` (the served map), `graph-cxa-adopted.bin`, `graph-lux4.bin`, and the two byte-identical duplicates used as controls |
| archives read | `grt-archive-algb.pre-cex-snapshot` (75,000 payloads) and `grt-archive-algb` (117,302), ALG-B sub-tree — **read-only** |
| ListenBrainz's algorithm | `listenbrainz_spark/similarity/artist.py` plus its two upstream input builders, fetched from `metabrainz/listenbrainz-server` **master** by `curl` on 2026-09-06 — **not transcribed from the plan**, which was the point of the check |
| MusicBrainz | one live web-service query, to confirm `join_phrase` spacing for `F2`'s second half |
| repo state | `main` at `da6a846`, clean; both `LUX-4` (#105) and the `LBD-` docs (#106) merged |

**ListenBrainz's source is deliberately NOT vendored here.** It is third-party material, it
would fall under the `docs/reference/` "never used as context" rule if it were, and pinning
the URL and the date is what makes the check reproducible. Re-fetch it rather than trusting
any copy.

## The probes

Six scripts, written for this review and committed beside their results. They read artifacts
through the shipped `GraphStore` (the `cxr_census.py` precedent) and **write nothing**.

| script | what it measures |
|---|---|
| `q1_degree_drift.py` | degree movement for a fixed MBID set across two populations under the same cap rule |
| `q2_archive_shape.py` | reciprocity of the endpoint's served rows, and the truncation that explains it |
| `q3_truncation_and_cap.py` | the tie-break loss at the truncation boundary, by fame band |
| `q4_added_set_supply.py` | candidate supply for the `CXR` added set, before and after each of our graph rules |
| `q5_tie_ceiling.py` | the upper-bound overlap ceiling a perfect reimplementation could score |
| `q6_partition_and_stability.py` | build-to-build stability, and the bootstrap over the added set |

Run them with `UV_LINK_MODE=copy`, and `PYTHONIOENCODING=utf-8` for anything printing artist
names. `q4` reproduces `CXR-P2`/`CXR-M5` exactly, which is the validation that the read is
being taken correctly — treat a failure to reproduce those as a broken environment, not a
new finding.

## What is NOT established here

Both reports carry their own limitations sections and those govern; the four that most often
get read as more than they are:

- **Nothing about the parquet dump itself.** `D:\unsung-large-data\…` was not visible to
  either reviewer. The schema ListenBrainz writes *on master* was verified; the file on the
  owner's disk was not. Task 1 step 1 is the right place and already refuses on mismatch.
- **The population-drift figure is an order of magnitude, not a constant.** One artifact
  pair, one population ratio, and that pair differs in a second column (the un-listenable
  list was re-censused between them). The isolating pair of builds is named and costed in
  `measurement-derivation.md` Q1; **it was not run.**
- **No arm was run, and no graph was built.** Every statement about what an arm would
  produce is inference from today's artifacts. `LBD-M1` is what would settle it.
- **Whether the featured-credit weight is dead on the real corpus.** The *mechanism* is
  verified from ListenBrainz's source; the *share* of `join_phrase` values that would match
  is a one-line count in Task 1 and was not made.

## What this review does not decide

**Nothing.** It is derivation and verification. Whether the `LBD-` track is still the right
place to spend — given Q4's measurement that most of today's sparsity is attributable to our
own degree ceiling rather than to missing listening data — is the owner's call, and it is
recorded as open in
[`findings/2026-09-06-lbd-plan-review.md`](../../../docs/superpowers/findings/2026-09-06-lbd-plan-review.md).
