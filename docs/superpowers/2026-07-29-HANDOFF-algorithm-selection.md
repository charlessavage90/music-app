# Handoff — source algorithm selection measured, 2026-07-29

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-29-HANDOFF-requirements-track3b.md`](2026-07-29-HANDOFF-requirements-track3b.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a seam handoff, not mid-flight.** The measurement ran to completion and was read
against a pre-registration committed before it. Nothing is in flight, no server is up, no
subagent is running, the tree is clean.

## What the next session does

**Write the graph rebuild plan, cold, from the committed record.** Everything needed is in
[`2026-07-29-algorithm-selection-execution-log.md`](2026-07-29-algorithm-selection-execution-log.md)
and its pre-registration. The plan now has four strands, and their order changed this
session — read the next section before assuming the old order.

**The owner's agreed next action is `AS-H2`'s trial crawl** (below). It is the cheapest
thing that could change the rebuild's shape, and it was recommended but **not run** — this
session seamed first.

## The re-sequencing, and why

**The cap-selection simulation is no longer the first task.** It was the agreed first move
under `MKS-5b`. `CS-P0c` then showed **superstars are offered zero sub-decile candidates by
the crawl itself**, so no cap rule can select one — the simulation cannot fix `DD-F1`, the
defect that motivated it. It moves to third. It still discharges `MKS-5b` and still
addresses the top-1% band, where candidates do exist and the current rule discards 72.8%.

The owner was told and agreed. **Do not restore the old order.**

Strands, in the order now intended:

1. **Algorithm selection** — measured this session. `ALG-B` is the named re-crawl candidate.
2. **`AS-H2`'s trial crawl** — a `--target`-capped crawl on `ALG-B`, built, to measure
   stranding before committing 4¼ hours. **Recommended, not run.**
3. **Cap selection under `MKS-5b`** — unchanged, still owed, now third.
4. **The nameless-artist drop rule** — still comes due inside this plan; `acceptance.py`
   stays unweakened. Unchanged from the previous handoff.

## Which documents are now wrong, and in which direction

- **`STC-6` is dead and `NEXT.md` still lists it.** Its lever was "re-crawl at a lower
  co-occurrence threshold". The `algorithm` parameter is a **closed enum of six values**
  (validated live: `threshold_5` → 400), only `threshold_10` and `threshold_15` exist, and
  production is already on 10. **There is nothing lower to ask for.** Per the closeout
  standing rule this is a *kill* — the condition became known-unreachable — not a
  reschedule. Struck in `NEXT.md` at this closeout.
- **"Re-crawl asking for longer candidate lists" does not exist either.** `limit` cannot
  exceed 100 (`limit_500` → 400). Any document proposing it is wrong. This was *this
  session's own* recommendation earlier in the day, and it is retracted.
- **`docs/README.md`'s two new rows were added at this closeout** and are current.

## Overturned or corrected claims a well-meaning editor must not revert

- **Neither `AS-R1` nor `AS-R5` fires.** Both reads assumed the popularity strata would
  agree about `ALG-A`; they do not (it clears the noise bar at top 1%, not at top 0.1%).
  Recorded as `AS-H1`, **not-fired** — do not re-label the result toward whichever read
  looks cleaner. Same shape as `TB-P5H-7`.
- **`ALG-B` is not unambiguously better.** `AS-H2`: it returns **58% fewer candidates**
  below the median, so it plausibly strands *more* obscure artists while fixing the
  famous-pair defect. Do not summarise `ALG-B` as a win.
- **`AS-C1` is a lower bound for `ALG-B`, not a measurement.** 16.8 of its candidates per
  top artist are absent from the current artifact and therefore have no percentile.
- **The cap-selection simulation was not cancelled**, only re-ordered. It is still owed.
- **`CS-P0f`: the source `score` is symmetric** (99.99% of reciprocated pairs identical
  both directions; rank correlation between directions 0.12). So mutual k-NN adds no
  similarity evidence — it re-tests the same number against each endpoint's *other* scores,
  and where it rejects an edge the refusing end is the **more popular** one 87.4% of the
  time. This derives Phase 1 log §2.10's depletion finding arithmetically from source data.
  **It is not a proposal to change the rule** — `MKS-5b` still requires a simulated degree
  bound first.

## Already updated — do not re-edit

`docs/README.md` (two rows), the pre-registration's §7 (amendments `AS-H1`, `AS-H2`,
appended not edited), `NEXT.md` (rewritten at this closeout), `TEST-QUEUE.md` (N/A entry),
the previous handoff's role line. PR #48 body carries the full summary.

## What this session knows that is not otherwise in the durable record

- **The trial crawl is the right next experiment and I did not run it.** `--target` caps
  discovery (see `CLAUDE.md`'s builder commands); a few thousand artists on `ALG-B`, built,
  would expose the degree and stranding distributions. It answers `AS-H2` without the full
  4¼ hours. Nothing about it is written down beyond this line and the execution log's
  deferral row.
- **The raw records are committed** (`as_raw_records.json`, 5.6 MB) so `as_score.py` can be
  re-run, re-scored, or scored differently **without re-hitting the service**. A successor
  wanting the rate-based version of `AS-C1` (see `AS-H2`) needs no new requests.
- **The endpoint is slower than its rate limit suggests** — ~0.85 s per request on top of
  any throttle, so 1,200 requests took ~18 minutes rather than the 10 estimated. Budget
  accordingly.
- **`ALG-D` (75-day window) is useless and `ALG-C` is near-identical to production**
  (Jaccard 0.80, Spearman 0.994 at the top). Neither needs re-measuring; both were run and
  are in the raw records.
- **The one asymmetric score pair** in `CS-P0f` (1 of 9,487, ratio 2.4) is most likely a
  crawl-time artifact — the two responses were fetched at different moments — but that is
  an inference and was not chased.
- **Decided against, and why:** raising `limit` (impossible, closed enum); lowering
  `threshold` (impossible, same); a 200-artist sample of ALG-B *alone* without the noise
  pair (rejected — it would have had no calibrated effect size, which is the failure mode
  this repo keeps hitting); running the cap-selection simulation first (rejected on
  `CS-P0c`).
- **Nothing the owner said in conversation is missing from a file.** His algorithm-enum
  research is captured in `CS-P0e`'s docstring and the pre-registration §0; his `score`
  symmetry question is captured in `CS-P0f`'s docstring; his note that the forum's
  `contribution` mapping does not cleanly match the parameter is in the execution log's
  weakest-link section.
