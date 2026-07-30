# Execution log — reciprocity sampling (RC), 2026-07-29

**Role: COMPLETE.** The retained record of the `RC` track: what was decided, what was
found against this session's own output, and what it corrects in the prior record.

**Owns no figures.** `RC`'s measurements belong to
`builder/analysis/2026-07-29-reciprocity-sampling/` (`rc_scores.json` — the pre-registered
read; `rc_posthoc.json` — the post-hoc corrections) and
`builder/analysis/2026-07-29-trial-crawl-calibration/`. Scoring and path-quality figures
live in `findings/2026-07-21-scoring-adjudication.md` and are cited by section, never
restated.

Governing document: [`specs/2026-07-29-reciprocity-sampling-preregistration.md`](specs/2026-07-29-reciprocity-sampling-preregistration.md),
committed **before any arm ran** (`b9e9f61`), with amendments `RC-A1` (pre-run) and `RC-A2`
(post-run). Branch `graph-rebuild-trial-crawl`.

---

## §1 What this track was asked to do, and what it did instead

The entry brief was the previous handoff's: **write the graph rebuild plan**, with the
owner's agreed next experiment being `AS-H2`'s **`--target`-capped trial crawl on `ALG-B`**.
The plan was not written. The experiment ran, on a **different instrument**, and its result
changes what the plan should say.

**The task order the owner agreed at the start of this session** was: run the trial crawl
first, then write the plan with its number in hand. That ordering held; only the instrument
changed.

## §2 Decisions taken, with reasoning

- **The capped trial crawl was retired as the instrument for `AS-H2`.** Not on judgement —
  on a measurement taken before any pre-registration existed
  (`builder/analysis/2026-07-29-trial-crawl-calibration/`, harness committed at `6cee90e`
  before it produced anything). A capped crawl's *readable* core — artists all of whose own
  candidates were also fetched, so their degree is decided by the data rather than by where
  the crawl stopped — is **structurally famous**, because BFS closes the famous core first
  and obscure artists are permanently on the frontier. At a 3,000-artist target the readable
  set held 3 artists below the median; at 5,000, 19. The question is *about* obscure artists,
  so reaching a usable number needs tens of thousands of fetches — the full re-crawl the
  trial existed to avoid.
- **Replaced by sampled reciprocity.** A built edge needs each endpoint inside the other's
  top-50 (mutual k-NN), so degree is `|top50(u)|` times the share of those that rank `u`
  back. Sampling ten of `u`'s candidates estimates the share directly, which lets the artists
  be **chosen** by fame band instead of hoped for. It is also closer to a real full re-crawl
  than a capped crawl is (`RC-H4`).
- **The seed set was taken from the AS sample** (`RC-A1`, before any arm ran). Both arms'
  seed lists were already committed in
  `analysis/2026-07-29-cap-selection-sim/as_raw_records.json`, fetched the same day in one
  interleaved pass. That made the seed side free, removed any drift exposure on it, and put
  the **rate** on the same artists `AS-C1` measured the **count** on — which is what `AS-H2`
  asked a successor for.
- **Nothing was written to any archive.** The AS precedent, and here it also sidesteps
  `RC-H3`: the archive key is `similar/listenbrainz/{mbid}.json` and does **not** encode the
  algorithm, so `ALG-B` responses stored beside production ones would be returned to every
  future build as if they were production data.
- **Collection and scoring are separate scripts**, so scoring is re-runnable without
  re-hitting the service. The post-hoc corrections went in a **third** file rather than
  editing the pre-registered scorer, so `rc_scores.json` still shows what the committed
  design produced.
- **No builder source change was needed.** The earlier session-start finding — that
  `BuilderConfig` is frozen with no `--algorithm` flag, so a trial crawl on `ALG-B` could not
  be requested — was real, and it dissolved with the instrument: the harness constructs the
  algorithm string itself. **A real re-crawl still has no way to select the algorithm** other
  than changing the config default, which `NEXT.md` records as being the re-crawl decision.
- **Decided against:** raising `k` in response to `RC-A2`'s rank finding (`MKS-5b` rejects
  loosening the both-ways cap without a simulated bound; it is strand 3's territory);
  re-fetching the 200 seed lists to capture disambiguation exactly (≈8 minutes, but it would
  have reintroduced a drift question the amendment had just removed); a seeded
  closed-neighbourhood crawl (costed at ~2.4 h against ~40 min, and blind to component
  structure either way).

## §3 Defects found in the design itself

All three are `RC-A2`, all post-hoc, and the first is the one that matters:

- **`RC-P1` — the pre-registered scorer's denominator biased toward the null.** It skipped
  any seed with no usable sampled candidate. Ten of forty below-median seeds returned **zero
  candidates** under `ALG-B`, so the pre-registered read silently dropped the maximally
  stranded artists from the arm that strands them. An artist with no candidates has no edges
  and is dropped by `largest_component`: degree 0, not missing. Corrected on the full
  denominator the effect roughly doubles. **Both readings cross the pre-registered
  thresholds**, so this is a correction of magnitude, not of verdict — and both are reported
  together wherever either is.
- **`RC-P2` — `RC-C3` pre-registered only one of the acceptance clauses it should have.** It
  fixed the median against `famous_median_degree_floor`, which **passes**. It never named
  `famous_min_degree_floor` (8, over the top 25) or the 24 `canonical_names` that must be in
  the largest component. Four top-0.1% seeds reciprocate nothing under `ALG-B`, one of them
  **R.E.M.**, a canonical name — so an `ALG-B` artifact is predicted to be **refused by
  `check_acceptance`** on two clauses the design never mentioned.
- **`RC-P3` — a mechanism was proposed and this session's own data does not support it.** The
  hypothesis was that `ALG-B`'s appeal is self-cancelling because mutual k-NN would delete
  precisely the new obscure edges. Split by whether the candidate exists in the adopted
  artifact at all, reciprocation is indistinguishable between the two sides. **Candidate
  obscurity is not the discriminator.** Recorded because it was proposed before it was
  tested.
- **What the famous-side collapse actually is.** Verified by hand rather than inferred: under
  `ALG-B` those four artists appear in their own candidates' lists at **rank 50–97, or not at
  all** — just outside the top-50 cut, so mutual k-NN rejects the edge correctly and the
  estimator is not at fault. This is a `k` interaction, and it is evidence that the
  **cap-selection simulation and any algorithm change interact** rather than composing.

## §4 Gate outcomes

| Gate | Outcome |
|---|---|
| **`RC-G1`** — archive drift | **Not fired**, and reported with its figure: 0 of 200 seeds differ from their archived top-50 by more than 5 members. The nine-day-old archive is sound as the production arm's candidate source. |
| **`RC-G2`** — band sufficiency | **All five bands readable.** The lower half sat **exactly at its floor of 30** in the pre-registered read — `RC-P1`'s correction is what restores it to 40. |
| **`RC-R1`** — material stranding | **Fired**, on the pre-registered read and on the corrected one. |
| **`RC-C3`** — famous side vs the median floor | **Passes.** See `RC-P2` for the clauses it did not cover. |

Collection: zero fetch failures, zero unresolved sampled candidates, zero placeholder
entities drawn.

## §5 Corrections to the prior record

- **The capped trial crawl is retired for this question**, and it was named as the agreed
  next experiment in `NEXT.md` and in the 2026-07-29 algorithm-selection handoff. Both are
  superseded on that point. It is retired **as an instrument for `AS-H2`**, not for all
  questions.
- **`AS-H2` is discharged for its connection-count half** and remains open for the
  component-membership half (`RC-H1`), which no sampling estimator can reach.
- **`ALG-B` must not be summarised as "worse" either.** It does what `AS-C1` said it does,
  and by the measure the build actually checks the typical famous artist still clears the
  floor. What is new is a measured price and a predicted build failure.
- **The session-start claim that a trial crawl needed a builder change is superseded** — see
  §2. The underlying gap in `BuilderConfig` is real and still applies to a real re-crawl.

## §6 Operational measurements with no other home

- **`--target N` fetches N artists.** `crawl.py` stops *discovering* at the cap but keeps
  fetching everything already discovered, so `done == discovered == target`. Verified against
  the production checkpoint, where both are 75,000. An earlier reading of the stopping rule —
  that a capped crawl would fetch only ~N/50 artists — was wrong.
- **Per-request cost.** The production crawl's own log gives a mean fetch latency of 0.141 s
  (median 0.130, p99 0.280, max 29.78 over 70,000 logged fetches), plus the fixed 0.2 s
  inter-request delay. The AS session measured ~0.85 s on the same endpoint on 2026-07-29, so
  **budget on the fresher figure**: today the endpoint is several times slower than during
  the crawl.
- **Collection cost, actual:** 2,717 candidate lists — 1,345 served from the archive, 1,372
  fetched live, 0 failures. Wall clock ≈ 25 minutes at a 0.4 s pause. Raw records 19.0 MB.
- **The production archive is intact:** 75,000 responses under
  `builder/scratch/graph-archive/similar/listenbrainz/`.
- ~~**A full build from the archive takes ~2 minutes**~~ and reproduces the adopted
  artifact's node and edge counts exactly.
  ⚠ **CORRECTED 2026-07-30: the build takes ~29 seconds** (78 s for the larger `ALG-B`
  archive), measured twice on real full builds —
  `2026-07-29-graph-rebuild-track-a-execution-log.md` §5 and §7b. `CLAUDE.md`'s "~30 s"
  was right all along and needs no edit; this line was the outlier. Annotated in place
  rather than rewritten, per the convention for COMPLETE records. The node/edge
  reproduction claim stands.

## §7 Provenance (D3)

- **Adopted artifact used as the popularity ruler and the sampling frame:**
  `graph-t15-tiebreakfix.bin`, sha256
  `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, **verified against its
  manifest sidecar at the start of this session** and re-verified by both harnesses at run
  time (each refuses to run on a mismatch). 74,193 artists, 898,006 edges.
- **No artifact was built or adopted by this track.** `BuilderConfig.algorithm` is unchanged
  and still carries `contribution_5`.
- Popularity strata are `pop_pctl_full` — a percentile **rank** over that artifact. `pop_raw`
  is a value and was not used as a rank (log §2.12).

## §8 Standing context layer (D6)

Measured, not asserted — the `memory/` slug was confirmed to resolve first:

| Layer | Unit | Total | Delta this track |
|---|---|---|---|
| Unconditional | characters | **44,113** | **0** |
| Conditional | lines | **2,122** | **0** |

Neither layer was touched: no `CLAUDE.md` edit, no new or changed skill or agent, nothing
written to `memory/`. The one `.gitignore` change is in neither layer. **These are the totals
for the next closeout to compare against**, and the conditional figure is not comparable with
the historical 1,436, which was measured under the old over-broad definition that counted
whole `SKILL.md` bodies as unconditional.
