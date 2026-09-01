# `CXA-` Task 1 — the fourth acceptance artifact

**Role: FIGURES OWNER for the fourth row of the `CXA-` acceptance-bounds recalibration.**
Cited, never restated. The other three rows are owned by their own manifest sidecars and by
the `MSW-` execution log's Task 9 section.

**What was run.** `mknn_build.py` — one build of the extended ALG-B archive
(`scratch/grt-archive-algb`, 117,302 responses) under `cap_strategy="mutual_knn"`, then
`check_acceptance` twice: once against `PRODUCTION_ACCEPTANCE` as shipped, once against the
bounds proposed at `CXA-S1`. It builds through `build_from_archive` and calls the shipped
`check_acceptance` unchanged, so it owns no build logic and no criteria of its own.

**It does not serialise.** The row needs counts and a verdict, not a 23 MB artifact that
would never be deployed. There is therefore no artifact and no sha to cite for this row —
`mknn_result.json` is the record.

## The one knob

Everything matches the `JFX-B` build — algorithm ALG-B, the recensused `ULF-` payload
(`analysis/2026-08-09-cex-recensus/ulf_droplist_algb.json`), `require_fame=True`,
`max_neighbours_per_artist=50` — and differs in `cap_strategy` alone. That is what makes it
an isolating baseline for the **cap rule** rather than a second build differing in two ways.

## Result

| | artists | edges | median degree |
|---|---:|---:|---:|
| mutual k-NN over the 117k archive | 81,749 | 905,558 | 7 |

Build time 1,478 s. Largest component 81,749 of 90,026 artists.

**Verdicts:**

- **Against the shipped (unwidened) bounds — REJECTED** on both artist count and edge count.
- **Against the proposed bounds — REJECTED on the edge count only** (905,558 against a floor
  of 1,295,000). Its artist count, 81,749, sits **inside** the proposed node band
  [70,900, 106,400].

## What it establishes, and what it does not

**Establishes:** the proposed band discriminates the cap rule on the population it will
govern. This was not previously true — the `MSW-` comment in `acceptance.py` records mutual
k-NN on the 75k archive at 732,832 edges, **inside** the then-current band.

**⚠ The edge floor is doing all of that work alone.** The node bound cannot see a cap-rule
revert: a mutual-kNN build of this archive passes it comfortably. Anyone later widening the
edge floor to admit a build removes the only bound that distinguishes the two cap rules.

**Does not establish** anything about path quality, journey length, or what a user would
see. It is a structural tripwire calibration and nothing more. It also says nothing about
the crawl-size dimension, which the other three rows cover.
