# Fame-proxy coverage — what the Wikipedia floor hides, and what covers it

**Role: ACTIVE analysis record. Owns its figures.** Scoring and path-quality figures
belong to `docs/superpowers/findings/2026-07-21-scoring-adjudication.md`; Track 2's fame
work is owned by `../2026-07-23-track2-fame-proxy/` (Deezer) and
`../2026-07-24-track2-fame-proxy-wikipedia/` (pageviews). Nothing here restates them.

**Scope: DESCRIPTIVE SCOPE PROBES, in the `CS-P0` sense.** They measure coverage and
agreement of candidate fame instruments. **They fix no criterion, run no arm, adopt
nothing, and license no currency change.** A pre-registration is owed before any criterion
is built on any instrument measured here. Track B is untouched — it scores in in-graph
popularity percentiles against a fixed adopted frame, and none of these instruments enters
it.

## Why this directory exists

The adopted fame proxy **failed its own pre-registered coverage falsifier** — 9 of 29
match failures against a `> 6` bar, recorded verbatim in
`../2026-07-24-track2-fame-proxy-wikipedia/README.md` as *"pageviews is unfit per §5"*.
It was adopted anyway via **A11**, which scores unresolvable artists at the fame **floor**
rather than dropping them.

That floor has cost twice since:

- **A12** stripped `C6` (the coverage guard) from gating, because under the floor rule
  match failure became *"a marker of the obscurity the sweep exists to reach"* — left
  gating, `C6` would have capped an arm at ≈5.6% obscure interiors and penalised success.
- **A18** recorded the blank-name confound: 33 nameless nodes score at the floor, read as
  maximal obscurity, sit 2.7× concentrated in the bottom decile, and are absent from the
  control.

Underneath both: **the floor collapses the entire obscure tail into a single value**, and
that tail is the region the product exists to serve.

## What each probe does

| File | Step | Question |
|---|---|---|
| `fp_common.py` | — | Shared loading, batching, backoff, resume |
| `fp_floor_reach.py` | 1 | What share of **routed interiors** sits at the floor, by bypass depth? |
| `fp_listenbrainz.py` | 2 | Full-graph `POST /1/popularity/artist` coverage |
| `fp_wikidata.py` | 3 | Full-graph join on `P434`; sitelinks and English article |
| `fp_agreement.py` | 4 | Banded coverage and agreement across the three instruments |
| `fp_magnitude.py` | 5 | Does multilingual pageview data change **magnitude**? |

**Every probe's expectations and read thresholds are fixed in its module docstring and
committed before it runs.** That is the honest analogue of pre-registration for a
descriptive probe, and the commit timestamps are the part that cannot be reconstructed.

## Imported, not reimplemented

- `fame_frame`, `BANDS`, `band_of`, `ADOPTED`, `ADOPTED_SHA` come from
  `../2026-07-30-track-b-cap-selection/cb_metrics.py` by `sys.path` insertion (the
  `as_run_arms.py` precedent). **Band membership must have exactly one definition** or
  nothing here is comparable with Track B — and the adopted artifact's sha assertion
  travels with the import.
- `deserialise` comes from `artistpath_builder.artifact`.
- Paths come from `../2026-07-24-track2-arm-scorer/paths.json`, whose `artifact_sha256`
  is the adopted artifact's, so its node indices resolve directly. **Nothing is
  re-routed and no arm is re-scored.**

Reimplemented deliberately: `spearman` in `fp_agreement.py`, because the builder has no
stats dependency and adding one for a rank correlation is not worth the surface.

## What this directory CANNOT conclude

- **Nothing about coherence.** No offline proxy for listening coherence exists
  (`SYN-6`, and the Track B prereg says so plainly). Fame is not coherence.
- **Nothing about whether any instrument is "right".** Coverage is not validity. An
  instrument can cover every artist and still order them wrongly.
- **Nothing about population bias.** Measured the same day on one pair: ListenBrainz and
  English Wikipedia under-represent the same artists by ~10× against outside references,
  so **their agreement is a shared blind spot, not corroboration**. Neither can audit the
  other. Settling that needs an outside ruler this project does not have.
- **Nothing that licenses a currency change.** Swapping what "obscure" means touches every
  fame-scored criterion and forces a decision about whether prior results get re-read.
  That is a pre-registration and an owner decision, not a consequence of these numbers.
- **Nothing about artists absent from the graph.** Goose (`b925a474`, the US jam band) is
  not in the artifact at all, so no instrument here scores it. The coverage figures are
  over the artifact's own population, which is already ListenBrainz-skewed — this biases
  the multilingual reads **toward** confirmation, and is stated in
  `fp_agreement.py` before the run rather than after.

## The identity finding, which is separable from the currency question

`P434` **is** the MusicBrainz artist ID, so the Wikidata join is exact and removes name
resolution entirely. That matters beyond coverage: name search can also resolve to the
**wrong** artist and return a confident, bogus fame value. The graph carries the live
instance — it holds **GOOSE** (Belgian dance/electro, `6849ebec-b385-4b41-b5a1-125f91e46119`)
and **not** Goose (US jam band, `b925a474-d245-4217-bc13-2e153d82bebb`), so a name-keyed
lookup for "Goose" scores the wrong band. A missing value is a null you can see; a wrong
value is not.

**This holds whatever is decided about the currency**, and it is the cheapest thing in
this directory to act on.

## Cost note for anyone repeating this

Go **to** Wikidata for `P434`, not to MusicBrainz for its external links. The MusicBrainz
web service is 1 req/s — about 21 hours for the artifact. Batched against the Wikidata
Query Service the same join is minutes. WDQS latency is highly variable under load (the
same query shape measured 4.5 s and 109 s on adjacent batches), so the collectors resume
from disk and back off rather than retrying tightly.

Raw outputs (`fp_wikidata.json`, `fp_listenbrainz.json`) are gitignored — they are
regenerable from the two commands above and are large. The derived summaries are
committed.
