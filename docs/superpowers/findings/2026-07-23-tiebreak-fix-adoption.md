# Adoption record — `graph-t15-tiebreakfix.bin` (the §2.8 tie-break fix)

**Role: AUTHORITATIVE for the adopted 75k artifact's identity.** Written
2026-07-23. This document owns the new artifact's identity figures; the
defect and the intervention that validated this fix are owned by the
Phase 1 log §2.8 — cite mechanism claims from there, not from here.

## What was adopted

The 75k artifact built by the fixed builder — `mutual_knn_cap` ranks top-k
on unclipped damped strengths; emitted scores stay `p99_log_clip`;
popularity unchanged (summed pre-cap). Governing design:
`../specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §3.

| artifact | sha256 |
|---|---|
| `builder/scratch/graph-t15-tiebreakfix.bin` **(ADOPTED)** | `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` |

Supersedes `graph-t15-capfix.bin` (sha `c8af6eac…`) as the artifact the app
routes on. capfix remains on disk as the §2 baseline.

Its checksum does not, and could never, match `graph-t15-rankfix.bin`'s: rankfix was
built with `similarity_rescale="percentile_rank"` against this build's `p99_log_clip`,
so a checksum match was never possible and the spec's §3.2 item 3 expectation of one
was wrong (corrected there 2026-07-23) — topology assertions plus bit-identical
shared-edge scores against capfix governed adoption instead.

## Adoption basis — why no listening test

Phase 1 log §4.1 closed this: the fix's topology (= §2.8 Arm 2 = rankfix's)
is identical to capfix on stratification and tail behaviour; a listen would
burn the owner's ear on a null. What changes is confined to
ceiling-saturated famous artists' neighbourhoods (~0.4 % of nodes), verified
below. The owner's ordinary use is the post-adoption check (TEST-QUEUE).

## Verification (script: `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`)

All §2.8 Arm 2 topology assertions passed; shared-edge scores bit-identical
to capfix; popularity ordering preserved. Run output:

```
ALL CHECKS PASSED
graph-t15-tiebreakfix.bin sha256 = 4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8
N=74193 E=898006
nodes only in new: ['a74b1b7f-71a5-4011-9441-d0b5e4122711', 'cbe7746f-d4b4-4f0d-a435-1aa181d97b1b', 'd71c2b20-616a-4bb8-a848-e6edac412c3b']
shared edges: 891690  (capfix E=898314)
Radiohead: degree 50, popularity 1.000
The Beatles: degree 50, popularity 0.998
Coldplay: degree 50, popularity 0.984
R.E.M.: degree 47, popularity 0.953
```

## Dev default

`ApiConfig.graph_path` now defaults to this artifact (spec §1 decision 4 —
the 5k dev fixture is retired; unit tests keep the committed 500-node
fixtures). Smoke-checked through the default: Radiohead and The Beatles
findable; Radiohead → The Beatles routes.
