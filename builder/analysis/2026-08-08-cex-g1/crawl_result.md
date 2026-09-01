# The `CEX-` crawl — 75,000 → 117,302

**Role: FROZEN RECORD.** Operational, executed once on 2026-08-08 (plan Task 10). The archive
and its log are gitignored, so this file is the durable record of what happened.

**Outcome: completed clean. 42,292 fetched this run, 0 failures, every response HTTP 200.**

---

## 1. What was asked for, and what happened

| | Value |
|---|---|
| Target (`--target`, caps **fetches** under `CEX-2`) | 117,302 |
| Archived responses, after | **117,302** — counted, exact |
| Checkpoint `done`, after | **117,302** |
| Fetched this run | 42,292 (+ 10 in a prior smoke run = **42,302**) |
| Permanent failures | **0** |
| HTTP status spread | 42,292 × **200**, nothing else |
| Warnings, tracebacks | **0** |
| Elapsed | **3.86 hours** (~3.0 fetches/s, steady throughout) |
| Algorithm | ALG-B (`contribution_3`), passed explicitly |

Target arithmetic held exactly: 75,000 done + 42,302 reconstructed frontier = 117,302.

## 2. `CEXR-11` — the composition question, answered

`CEXR-11` warned that permanent failures keep `_done` below target, so the loop dips into
**newly discovered** artists to make up the shortfall, making the final population's
composition depend on the failure count.

**Failures were 0, so it did not dip.** Measured against the pre-crawl checkpoint rather than
assumed: exactly **42,302** artists were added to `done`, which is the reconstructed frontier
exactly. **The extended population is the frontier and nothing else.**

## 3. State afterwards

| | Before | After |
|---|---|---|
| `done` | 75,000 | **117,302** |
| `discovered` | 117,302 | **128,595** |
| frontier (`discovered − done`) | 42,302 | **11,293** |
| `exhausted` | `false` | **`false`** |

**`exhausted: false` is correct, not a defect.** The run stopped on the fetch cap with a
non-empty queue, so the graph was not crawled out. `CEX-3` will therefore not refuse a future
resume, and `CEX-2` means the 11,293-artist frontier is **recorded** — a further extension needs
no `refrontier`, which is the whole point of the `ULC-F3` fix.

## 4. Ordering — what decided who got crawled

No quality signal. Two rules, both deterministic (spec §9):

- The resumed frontier drained in **sorted MBID order** (`crawl.py:128`). Confirmed empirically
  mid-run: at 21,510 fetched, the MBIDs formed a clean prefix of the ID space — roughly 2,600
  in each of buckets `0`–`7`, 438 in `8`, none above.
- Within one response, neighbours queue **strongest-score-first** (`parse` sorts on
  `(-score, mbid)`), which orders one artist's neighbours only and never jumps the queue.

So the frontier was sampled **without bias toward famous or well-connected artists**. Whatever
bias exists is in *who the first 75,000 named at all*, not in the order they were fetched.

## 5. Reversibility — still intact

| | Path | Verified after the crawl |
|---|---|---|
| Archive snapshot | `builder/scratch/grt-archive-algb.pre-cex-snapshot` | **75,000** responses — untouched |
| Checkpoint backup | `builder/scratch/checkpoint-algb-full.json.pre-cex` | sha256 `3a6f0804…f9f4b532c` |
| Crawl log | `builder/scratch/cex-crawl.log` | 2.5 MB, gitignored |

Disk after: 478 GB free. No stray `.tmp` files — `CEX-4`'s atomic write completed cleanly across
roughly 85 checkpoint rewrites.

## 6. What this does NOT establish

**No graph has been built and nothing is adopted.** This step only enlarged the archive.

Per spec §5 the eventual comparison against the adopted map is **confounded on six columns** and
cannot support any per-artist or path-quality read. Still owed before any artifact exists: fame
over the new population, an `unlistenable` re-census with the subset relation re-verified, and a
build that **will be rejected by acceptance on both bounds** — an owner stop, not a bound to
widen.
