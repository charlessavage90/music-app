# Popularity stratification — the scripts behind §2.9

These produced every figure in **§2.9** of
`docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md`, which found that
**mutual k-NN inverted the graph's popularity assortativity** — and that this, not the
tie-break defect of §2.8, is why the product does not surface obscure artists.

**Cite figures from §2.9, not from here.** The document owns them.

## What each one does

| Script | Answers |
|---|---|
| `assortativity.py` | **The load-bearing one.** Across five artifacts: is the graph popularity-assortative, and can the router step from a famous artist toward an obscure one at all? Artifact-only, runs in seconds. |
| `tail_probe.py` | Does bypassing ever reach obscure artists? `capfix` vs `rankfix`, one knob (the graph), shipped router, 3 pairs × 20 bypasses, two victim policies. Produced the null that redirected the work. |
| `coherence_probe.py` | Are the hops the owner called incoherent the MBID-arbitrary ceiling edges? **Designed as a contrast and it failed to discriminate** — coherent and incoherent hops are identical in the graph. Kept because the failure is the finding. |

`tail_probe.log` is the run record for `tail_probe.py`.

## Why two victim policies in `tail_probe.py`

The §3.8 blind listen bypassed the highest-`hub_penalty` interior artist. `hub_penalty` is
**degree-based**, and §2.6 established that degree does not mean famous. The owner's actual
complaint is about fame. Running both policies separates "the test's definition of a hub"
from "what the owner is asking for", and the answer is flat under both.

## Before you re-run them

- **Paths are hardcoded.** These are a record of what was executed, not maintained tooling.
- **Checksums are asserted before anything is measured.** Keep that — several graphs exist
  in `builder/scratch/` and they are not interchangeable.
- `assortativity.py` needs five artifacts; it reports which are missing rather than failing.
- `tail_probe.py` runs ~250 `find_path` calls at ~1.5 s each. Minutes, not seconds. Use
  `python -u`.
- `coherence_probe.py` needs `precap.npz`, the pre-cap cache written by
  `../2026-07-22-cap-ranking-replay/decompose.py`. Regenerate it there first.
- One row of `coherence_probe.py` (Avril Lavigne → blink-182) fails to resolve because the
  MusicBrainz name uses a Unicode hyphen. That is the punctuation trap in Phase 2 log §9;
  the row is untested rather than negative.

## Note for a reachability sweep

Nothing imports these, and that is correct — research tooling invoked manually, the same
category as `nulls.py`, `stats.py` and the sibling `analysis/` directories. See Phase 2
execution log §18's B2 check.
