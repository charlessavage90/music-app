# Telemetry preservation across the `MSW-` adoption, 2026-08-06

**Role: RAW RECORD. This directory owns its own counts.** It computes no metric and licenses
no read. Cite it; never restate a figure from it elsewhere.

## Why this exists

App Runner log groups carry **90-day retention**. The **pre-adoption** telemetry corpus is
therefore **fixed, finite and shrinking** — it can only get smaller, with the earliest events
(2026-07-26) expiring around **2026-10-24**. The post-adoption corpus grows. That asymmetry is
the entire argument for pulling: **this is preservation, not analysis.**

Requested by the owner 2026-08-06, immediately after the adoption deployed, on the reasoning
that the live app records what he does to CloudWatch while a local dev server does not.

## Files

| File | What |
|---|---|
| `telemetry_events.jsonl` | The **1,105 telemetry events** only — every `path` and `clip` event, era-tagged. Readable and greppable. |
| `raw_all_events.jsonl.gz` | The **complete corpus**, 95,428 events including App Runner's own operational noise. Gzipped: ~99% of the raw corpus is health checks, and 17 MB of those do not belong in git history uncompressed. |
| `manifest.json` | Counts per era and per stream, the deploy's identity, and the caveats below. |
| `pull_telemetry.py` | The extractor. Re-runnable, but **it cannot recover what has already expired.** |

## Era is assigned by LOG STREAM, never by timestamp

**App Runner rolls deployments, so the outgoing and incoming instances serve concurrently.** On
2026-08-06 the new instance began at **09:37:22** while the old one kept answering until
**09:46:13** — a ~9-minute window in which a timestamp filter attributes old-graph journeys to
the new graph. Each instance is its own log stream and each stream ran exactly one artifact, so
the stream is unambiguous where the clock is not.

**The mapping was verified, not inferred from timing:** a journey run against a `/health` that
had already reported the new sha appears only in stream `2e9ff5f0…`.

## What the corpus contains

Counts are in `manifest.json` and are not restated here. Two shapes matter:

- **`path`** events carry source, target, the full exclusion list, `bypass_depth`,
  `dislike_count`, `known_count`, the full resulting path, `path_length`, `stop_rule` and
  `duration_ms`.
- **`clip`** events carry mbid, `resolved`, which catalogue answered, and `duration_ms`.

Both record **facts, never computed metrics** — `api/…/telemetry.py` says so deliberately
(`DEP-7`: choosing which metric production computes is a scoring decision).

## ⚠ Caveats that travel with any use of this data

1. **The pre-adoption corpus is heavily synthetic.** One journey at each consecutive
   `bypass_depth` from 26 to 46, plus clusters at exactly 50 and 100, are a script walking one
   press at a time — not use. A large majority of the pre-adoption `path` events fall on
   **2026-07-28 alone**.
2. **Some post-adoption events are a session's own deploy verification** (a Radiohead → Miles
   Davis journey pressed five times), not owner use.
3. **The two eras differ in MORE than the graph.** The owner's usage pattern changes
   deliberately after adoption — the queued hand test asks for ten or more `known` presses,
   where pre-adoption use was mostly depth 0 — and the deploy moved several knobs at once, which
   the owner accepted when he tabled the production-data rebuild. **A before/after difference is
   not attributable to any one of them.**
4. **No metric has been chosen.** Choosing one after seeing both eras is the fishing the
   pre-registration discipline exists to prevent. **A comparison names its metric, its effect
   size and its read first**, per `CLAUDE.md`. The one most likely to survive that discipline is
   clip resolution rate **at matched depth**, because it is a fact rather than a taste judgement
   and is well-defined on both eras — but it is not pre-registered and nothing here licenses it.

## One extraction defect, recorded because it nearly shipped

The first run **silently dropped 38 of the 271 pre-adoption `path` events** — a ~14% undercount
that looked like a complete pull and would have been committed with a manifest asserting the
wrong count. Cause: `get-log-events` can return an **empty page with a valid forward token**
while more data remains, and the loop treated an empty page as end-of-stream. Caught only by
cross-checking totals against Log Insights, which is now the standing check: **a preservation
pull is not believed until its counts are reconciled against an independent query.**
