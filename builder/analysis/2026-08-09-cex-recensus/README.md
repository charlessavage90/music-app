# `CEX-` re-census and Task 11 build — 2026-08-09

**Role: frozen record of what was executed.** Plan Task 11 (`docs/superpowers/plans/2026-08-08-crawl-extension.md`),
Steps 1–5. **This directory owns every figure below — cite them, never restate them.**

The scripts are forward copies of `../2026-08-05-ulf-census/`; each carries a header
saying what differs and why re-running the originals in place was refused. Raw
`*.log` output is gitignored per this directory's `.gitignore`; the log lines that
carry figures are reproduced verbatim below, which is what makes them durable.

---

## Step 3 — re-census over the extended population

Offline half **5,819 s**. Archive union **129,746**; only **31,450** needed dump
evaluation (`ULC-F2` coverage store). The `ULF-3` subset assertion held over the new
population — that is Task 11 Step 3's "re-verify rather than inherit".

Network half: **3,905 of 5,684 resolve**, zero refusals, 2h01m.

| Population | Artists | Class | Drop | Keep |
|---|---:|---:|---:|---:|
| ALG-B (the adopted lineage) | 117,302 | 31,823 | 27,262 | 4,561 |
| ALG-E (unchanged) | 75,000 | 16,600 | 13,342 | 3,258 |

**Class rate rose with depth**, on a controlled comparison — same algorithm, same
detector, same dumps, only the population grew, and the pre-crawl set is a strict
subset (0 artists dropped out):

| | In the class | Rate |
|---|---:|---:|
| the 75,000 pre-crawl artists | 18,557 | 24.74 % |
| the 42,302 newly crawled | 13,266 | 31.36 % |

### ⚠ The ALG-E payload here is a by-product and must not be shipped

Its population is byte-identical to 2026-08-05, yet its drop list moved
13,355 → 13,342: **30 artists became drops and 43 stopped being drops**. Prior `ULF-`
verdicts are not carried, so those members were re-resolved against Deezer today and
clip availability moves. ALG-B shows the same churn on its shared 75,000 (32 in, 30
out). The sha pin in `unlistenable_drop.py` is what stops this shipping by accident.

**This churn is not a defect** — it is why these lists are frozen payloads shipped as
package data rather than computed at build time. `build_from_archive` is offline by a
hard rule and spec §9 requires byte-identical output.

## Step 4 — the build, rejected on both bounds

```
INFO filtered 7 special-purpose entities
INFO dropped 54 nameless artists
INFO dropped 9501 no-release-tail artists
INFO dropped 1940 featured-credit artists
INFO dropped 15774 un-listenable artists
INFO rescale p99 scale=769 | saturated edges 37053 of 3698308 (1.002%)
INFO largest component: 88685 of 90026 artists
ArtifactRejected: artifact rejected; not written:
  - artist count 88685 outside bounds [47000, 71000]
  - edge count 1618164 outside bounds [1050000, 1580000]
```

**Bounds were NOT widened.** That is the owner stop (`MSW-G3` precedent).

## Step 5 — `CEX-M1`, against a baseline that reproduces the adopted artifact

The comparison the plan asks for was not available: Task 8 *added* this logging, so
the adopted build predates it. Rebuilt from `grt-archive-algb.pre-cex-snapshot` using
ALG-B's **shipped** list — no override needed, because that default still points at
the 75,000-artist payload.

```
INFO dropped 4248 un-listenable artists
INFO rescale p99 scale=850 | saturated edges 31073 of 3105184 (1.001%)
INFO largest component: 58838 of 59277 artists
INFO wrote graph-cex-baseline-75k.bin: 58838 artists, 1315684 edges (22.4 per artist), 1029s
```

**58,838 / 1,315,684 reproduces the adopted artifact exactly**, so this is a true
baseline and nothing in the build path has moved since adoption.

| | Baseline (adopted) | Extended (117k) |
|---|---:|---:|
| p99 scale | 850 | 769 (−9.5 %) |
| saturated share | 1.0007 % | 1.0019 % |
| largest-component prune | 439 of 59,277 (0.74 %) | 1,341 of 90,026 (1.49 %) |
| mean degree | 22.4 | 18.2 |

### ⚠ `CEX-M1`'s saturated-edge share is vacuous by construction

Found by running it. `pipeline.py:99-112`: `scale = percentile(raw, 99)`, and an edge
saturates iff `raw >= scale`. **~1 % of any distribution sits at or above its own 99th
percentile**, so this figure reads ~1 % for any crawl at any size. The 1.0007 → 1.0019
movement is `np.percentile` interpolation, not a population effect.

It **cannot detect what it was pre-registered to detect** (spec §"the p99 similarity
rescale moves"). Recording this rather than the reading, because a future session
reading "1.0 % both times, no change" would draw a conclusion the instrument cannot
support.

### The p99 half is informative, and points opposite to the spec's worry

The divisor fell 1.48 % in log space, so **every similarity is 1.50 % higher for the
same raw co-occurrence**. Cost is `w_sim·(1−similarity)`, so the discount is uneven:

| similarity | cost term (1−sim) | change |
|---:|---|---:|
| 0.2 | 0.8000 → 0.7970 | −0.4 % |
| 0.5 | 0.5000 → 0.4925 | −1.5 % |
| 0.8 | 0.2000 → 0.1880 | −6.0 % |

Strong links get the larger discount, absolutely and proportionally. So the extension
mildly sharpens the router **toward** strong links — the opposite direction from the
spec's stated concern that more of the route would be decided by tie-breaks. The
magnitude is small: ≤6 % on one term of six.

**Derived, not observed on routes.** No 117k artifact exists to route over, because
acceptance rejected before serialising.

### The connected-component prune roughly doubled, which the spec asked for

Spec: benign *"at every population up to 75,000... not a guarantee at 117,302."* Now
measured at 117,302 — **0.74 % → 1.49 %**. Artists reached but not connectable to the
main body, so they cannot appear in any journey.
