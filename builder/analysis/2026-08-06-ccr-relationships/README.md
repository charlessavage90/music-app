# `CCR-` — do the class's top similarity edges point at collaborators?

**Date:** 2026-08-06 · **Governing document:**
`docs/superpowers/specs/2026-08-06-cocredit-relationship-preregistration.md`
(committed `dd2f53f`, **before any relationship data was fetched**).

**This directory OWNS its figures. Cite it; never restate them.**
Raw: `ccr_raw.json` (400 records). Scored: `ccr_result.json`.

## Artifact and archive (verified)

- Graph `builder/scratch/graph-msw-tu50.bin`, sha256 `43dd82bb…`, verified **in-process**
  before arm membership was read.
- Archive `grt-archive-algb/…/…contribution_3…/` — the crawl this graph was built from.

## Verdict: `null` — and the instrument is the reason, which is a defect in this probe

**`CCR-G1` fired.** Median documented relations: CLASS 2.0, CONTROL 1.0 — ratio exactly 2.0,
the pre-registered confound threshold. So `CCR-C2` (conditional) became primary, as the
pre-registration specified.

**Primary outcome `CCR-C2`: CLASS 2.52 %, CONTROL 5.26 %, Δ = −2.75 points → `null`.**
`CCR-C1` (raw) agrees: 2.0 % vs 3.0 %. The class is **not** enriched in "my top similarity
partner is a documented MusicBrainz relation" — it is marginally lower. Run state complete:
200 per arm, **zero fetch errors**.

## ⚠ The null does NOT refute the hypothesis, because this instrument cannot see it

**`inc=artist-rels` records band membership and formal artist-to-artist links. It does not
record that two artists share a credit on a recording.** The hypothesis is about *recording*
co-credit. This probe tested the wrong relation type.

**The proof is the case that motivated the whole probe.** Laura Lee:

| | |
|---|---|
| MusicBrainz `artist-rels` | exactly one: `member of band → Khruangbin` |
| Top similarity partner | **Leon Bridges**, score 214 |
| Scored by this instrument | **`top_partner_related = False`** |

**The canonical positive case scores negative on this test.** Her Leon Bridges edge comes from
a shared recording (*Texas Sun*), which `artist-rels` does not carry.

The pattern repeats across the sample: `Audrey Riley → Ed O'Brien (3152)`,
`Brian Robertson → Led Zeppelin (1637)`, `Gerry Beckley → The Beatles (1599)` — all
`related = False`, and in several the top partner is plainly not the artist's own band.

**Read this as: the hypothesis remains UNTESTED at population scale, not as evidence against
it.** Equally, this probe supplies no support for it. Both statements travel together.

## What the run DID establish, and it is not nothing

**The class is far more likely to have any documented relationship at all: 79.5 % (159/200)
vs 57.0 % (114/200).** That is a real difference in the pre-registered gate's own data, and
`member of band` is the dominant type. It confirms **who these artists are** — band members
and credited musicians — while saying nothing about **why the algorithm scores them similar**.

## Defects in this probe, recorded rather than fixed

1. **The instrument mismatch above.** The pre-registration's plain sentence for `CCR-C1` read
   *"in a band with **or have recorded with**"*, but §3 fetched only `artist-rels`, which
   cannot answer the second half. **The plain sentence overclaimed relative to what was
   measured** — the exact drift the plain-sentence rule exists to prevent.
2. **`CCR-C3` miscounts.** It tallies *every* relation type held by an artist whose top
   partner matched, not the type of the matching relation. Its "21 × member of band" is
   therefore not a breakdown of matches. `CCR-C3` carries no branch, so no read depends on it.
   **Left uncorrected**; the number is void, not adjusted.

## The corrected instrument, if this is taken further

One MusicBrainz request per pair answers it directly:

```
/ws/2/recording?query=arid:{artist}%20AND%20arid:{top_partner}&fmt=json&limit=1
```

A non-zero count means the two share a recording credit. Same cost as this run (~400
requests). **It needs its own pre-registration** — this document's `null` stands for what it
measured and is not amendable into a different test.

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-08-06-ccr-relationships/ccr_fetch.py
```

Resumes from `ccr_raw.json`; delete it to refetch. MusicBrainz answers in ~3 s, so a full run
is ~60 minutes.
