# Coherence tag probe — can an independent-currency metric track the owner's ear?

**Role: ACTIVE analysis record. Owns its figures.** Identifier series: `COH-`
(checked free across `docs/` before allocation). Scoring and path-quality figures
belong to `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`; nothing here
restates them.

**Scope: a ONE-DAY FALSIFICATION PROBE, descriptive in the `CS-P0` sense.** It fixes no
criterion, adopts nothing, and changes no weight, default, or document that defines
"better". A pre-registration is owed before any criterion is built on whatever survives.
It does **not** settle either open owner decision in `NEXT.md` (fame-instrument
sequencing; currency re-read policy) and must not be reported as if it did.

## The argument under test

Phase 1 §3.8: the two metrics built to guard coherence (Adamic–Adar, overlap
coefficient) were the **worst** predictors of the owner's blind-listen verdicts — 3/11
each, below the ~33% chance line. That hardened into "do not proxy coherence with a
metric." The record supports something narrower (fame-proxy execution log §7): both were
co-neighbour counts on the similarity graph — **the topology auditing itself**. The
owner's verbatim verdict notes (§3.9) are genre/era/scene judgments. An
independent-currency instrument has never been tried. Tags/genres are that currency —
**if** they cover the graph, which is exactly what Wikipedia's fame proxy fails at in
the obscure tail (`FPC-3`: 27.4% EN-article coverage in the lower-half band).

## Two steps, kill gate between them

| File | Step | Question |
|---|---|---|
| `ct_common.py` | — | Shared loading; **frozen genre normalisation** (step 2 cites it) |
| `ct_wikidata_genres.py` | 1A | P136 genre presence, full artifact, banded, both denominators |
| `ct_mb_sample.py` | 1B | MB genre/tag coverage, stratified 300/band sample — **carries the kill gate** |
| `ct_limit_interiors.py` | 1C | Genre union coverage on `FPC-9`'s LIMIT-arm interiors (descriptive) |
| `ct_lb_metadata.py` | 1D | LB batched metadata as a transport for MB tags (owner's question; outside the gate) |
| `ct_retrodict.py` | 2 | **Only if the gate passes.** Pre-registered path score vs the 11 verdicts |

**Outcome (2026-07-30): the gate KILLED** — lower-half union coverage 35.3% against the
50% bar. `ct_retrodict.py` was never run and must not be run against these verdicts
without being reported as a second attempt. Findings of record:
`docs/superpowers/findings/2026-07-30-coherence-tag-probe.md` (`COH-1`–`COH-5`).

**Kill gate (fixed in `ct_mb_sample.py` before any fetch):** step 2 runs only if
union-genre coverage (≥1 MB genre or ≥1 P136; all-sampled denominator) in the **lower
half** band is **≥ 50%**. Below that, tags thin in the tail the way Wikipedia does —
the same failure mode twice, §7's own warning — and the kill **is** the result.

**Step 2 discipline:** the 11 verdicts (Phase 1 §3.9, machine-readable in
`../2026-07-22-c3-bypass-mechanisms/listen_secret.json`) are a **falsifier, never a
training set** — n=11 has no held-out set, so the exact scoring rule is committed before
anything is scored, then scored **once**. A failed first rule is the result; any second
rule is a new commit reported as a second attempt. Bar: beat Adamic–Adar / overlap
coefficient (3/11, §3.8). **n=11 can refute, it cannot confirm** — beating the bar
promotes the idea to "worth a real test", never to adopted, never to a criterion.

**SYN-7 binds:** both listening verdicts date to 2026-07-22, before five of the nine
calibration values existed. Anything validated against them is validated against the
owner's preferences **as of then**.

## Imported, not reimplemented

`fame_frame`, `BANDS`, `band_of`, `ADOPTED`, `ADOPTED_SHA` via `fp_common` →
`cb_metrics` (`sys.path` insertion, the established precedent); the adopted artifact's
sha assertion travels with the import. Band membership has exactly one definition.
`deserialise` from `artistpath_builder.artifact`. Route A's second denominator reads the
FPC collector output `fp_wikidata.json` (regenerable, ~35 min — command in the
fame-proxy README).

## What this directory CANNOT conclude

- **Nothing about whether tags measure coherence correctly.** Coverage is not validity,
  and retrodiction on n=11 is falsification-only.
- **Nothing that licenses a criterion, weight, or currency change.**
- **Nothing about artists absent from the graph.**
- The MB sample is seeded and deterministic, but MB tag data itself moves over time —
  a re-run months later is a new measurement, not a reproduction.

## Cost notes

MB web service is 1 req/s (~21 h full graph — hence the sample; ~24 min). WDQS batched
P136 over 74k MBIDs is minutes-to-an-hour depending on load; both collectors resume
from disk. Raw collector outputs are gitignored (directory `.gitignore`); derived
summaries are committed.
