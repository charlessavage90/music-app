# Track 2 Stage A — the C1–C6 arm scorer

**Role: ACTIVE analysis record. Owns its figures.** Nothing here restates a figure from
`docs/superpowers/findings/2026-07-21-scoring-adjudication.md` or from the two fame-proxy
directories; those own theirs.

**No factorial arm has run.** This directory currently holds only the pre-arm checks.

## What lives here

| File | What it is |
|---|---|
| `band_gap.py` / `band_gap.json` | Two checks that had to run **before** any arm: §2.2's permitted recalibration, and the coverage-by-bucket measurement that amendment **A12** rests on. Inputs are the already-committed blind labels and pageview counts — no new owner time, no network. |

The scorer itself is not built yet. Sequence, per the execution log's seam entry: build it,
commit it, **P8b review**, then arms.

## §2.2's permitted recalibration — checked, does not fire

The pre-registration allows exactly one threshold adjustment before arms run: if the
owner's *know well* and *never heard of* bands sit closer than **1.0 log10** apart, every
log10 threshold rescales. Two defensible readings, reported because they differ by 5× and
the conservative one is close to the trigger:

| Reading | Band gap | Fires? |
|---|---|---|
| **As scored** (A11's encoding — unmatched artists at F = 0) | **6.161** | no |
| **Matched only** (drops the zeros; separation among artists the proxy can see) | **1.093** | no |

**Neither fires, so every §2.2 threshold stands as written.** The conservative reading is
the one worth carrying forward: at 1.093, **C1's −1.0 log10 threshold is almost exactly one
of the owner's perception bands wide.** So C1 asks, in his units, for the middle artist to
drop about one full step in how well he would know them — which is a more defensible thing
to have pre-registered than a bare number looked like.

## Coverage by label bucket — why C6 could not stay a gate

| Bucket | Matched to an English Wikipedia article |
|---|---|
| *know well* | 7 / 7 |
| *heard of* | 6 / 6 |
| *never heard of* | **7 / 16** |

| Stratum | Matched |
|---|---|
| S1 — the nine anchor unknowns (lo-fi / synthwave) | **1 / 9** |
| S2 — judged-listen interiors | 12 / 12 |
| S3 — the two likely reaches | 2 / 2 |
| S4 — off-platform stress cases | 5 / 6 |

Everything the owner recognises resolves. Only the stratum he does not recognise fails to,
and it fails almost completely. **Under A11 an unmatched artist is scored at the fame floor
rather than dropped, so match failure is now a marker of the obscurity the sweep exists to
reach** — which is what makes C6's ≥ 90 % coverage gate untenable as written. Full argument
and the owner's decision: pre-registration **A12**.

## Determinism

`band_gap.py` reads only committed JSON, asserts that every labelled artist appears in the
pageview fetch, and takes no network calls. Re-running it reproduces `band_gap.json` byte
for byte.
