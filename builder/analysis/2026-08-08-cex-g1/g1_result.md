# `CEX-G1` — frontier reconstruction checked against the baseline

**Role: FROZEN RECORD.** One-shot operational gate, executed 2026-08-08. Never in CI, never
re-run: **it cannot pass again once the archive is extended**, because the archive it reads is
the thing the next step changes. Plan Task 9.

**Outcome: `CEX-G1` PASSES.** Reconstruction reproduces the baseline census exactly.

---

## 1. The gate

| Quantity | Baseline (`2026-08-07-cex-frontier/cex_frontier.json`) | This run | Agrees |
|---|---|---|---|
| `responses_read` | 75,000 | 75,000 | ✅ |
| `distinct_mbids_referenced` | 117,294 | 117,294 | ✅ |
| **`frontier_size`** | **42,302** | **42,302** | ✅ **the gate** |
| `unparseable` | 0 | 0 (no warnings logged) | ✅ |

Command (offline — reads archived responses only, never the network):

```
artistpath-build refrontier \
  --checkpoint scratch/checkpoint-algb-full.json \
  --archive-dir scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30
```

Output: `done 75000 | discovered 117302 | frontier 42302`. Runtime **4m16s** (75,000 file
reads).

## 2. Checkpoint state, before and after

| | `done` | `discovered` | frontier (`discovered − done`) | `exhausted` |
|---|---|---|---|---|
| Before | 75,000 | 75,000 | **0** | key absent |
| After | 75,000 | 117,302 | **42,302** | `false` |

The "before" row **is the `ULC-F3` signature**: everything discovered had been done, so a resume
rebuilt an empty queue and the crawl exited `0 processed` reading as success.

`exhausted: false` is correct and load-bearing — this checkpoint was written before `CEX-3`
existed, and a crawl in the `ULC-F3` state is exactly what must NOT be read as a graph that was
crawled out (`CEXR-5`).

## 3. Step 5 — the invariant `CEX-G1` cannot see (`CEXR-7b`)

`done ⊆ discovered`: **OK.**

**The 8 artists are real and were counted directly, not inferred:** 117,294 MBIDs are named as
a neighbour by some response, and 8 members of `done` are named by **no** response at all
(75,000 done ∪ 117,294 referenced = 117,302 discovered). First three:
`09720eec-3871-49d5-932d-eb7542768cd3`, `0c502791-4ee9-4c5f-9696-0602b721ff3b`,
`0d8b0d50-e4cf-4da4-965d-f24c58ec3268`.

**This is why the rewrite unions rather than replaces, and why the gate alone could not have
caught a replacing rewrite:** a replace would drop those 8 from `discovered`, breaking
`done ⊆ discovered` — while still reporting `frontier 42302`, because the 8 are in `done` and
excluded from the difference either way. Confirmed by mutation at implementation time.

## 4. Step 1 — the archive snapshot (the owner's precondition)

**After the crawl appends, today's graph cannot be rebuilt from source** — `build_from_archive`
reads everything under the algorithm prefix and has no "build only this population" option. The
snapshot is what makes the extension reversible.

| | Path | Verified |
|---|---|---|
| Archive snapshot | `builder/scratch/grt-archive-algb.pre-cex-snapshot` | **75,000** `similar/**/*.json`; all 173,056 files and 890,728,140 bytes identical to source |
| Checkpoint backup | `builder/scratch/checkpoint-algb-full.json.pre-cex` | sha256 `3a6f0804…f9f4b532c` |

Both are **gitignored and cannot be committed**, which is why their identity is recorded here.
The post-`refrontier` checkpoint is sha256 `b89d3aff…0f66a055`; `rewrite_checkpoint` also left
its own `checkpoint-algb-full.json.bak`.

**To revert the whole track:** delete `grt-archive-algb`, rename the snapshot back, and restore
`checkpoint-algb-full.json.pre-cex`.

> **⚠ One durability caveat on `.bak`, recorded rather than fixed.** `rewrite_checkpoint`
> overwrites its `.bak` on every call, so a second `refrontier` run would replace the backup
> with the already-rewritten state. It is not load-bearing here — `.pre-cex` is an independent
> copy made before the first run, per plan Step 3 — but a future caller relying on `.bak` alone
> would be relying on a one-deep backup that erases itself.

## 5. What this gate does and does not license

- **Does:** the reconstruction is correct, so the crawl may proceed to a target of 117,302.
- **Does not:** say anything about what the extended graph will look like, whether acceptance
  will pass (it will reject on both bounds, by design), or whether path quality changes. §5 of
  the spec bars the comparison from supporting any per-artist or path-quality read.
