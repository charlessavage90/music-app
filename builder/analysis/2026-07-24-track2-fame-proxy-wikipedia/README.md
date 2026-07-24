# P4 fallback — the Wikipedia-pageviews fame proxy

**Role: ACTIVE analysis record. Owns its figures** (the Deezer run's figures live in
`../2026-07-23-track2-fame-proxy/`; the scoring-adjudication doc owns Phase-1 figures).
This directory is the second proxy in pre-registration §5's decision tree: Deezer `nb_fan`
FAILED, so the pre-registered response was to re-run the **identical scoring protocol**
against English-Wikipedia pageviews, **same committed labels, no re-asking the owner**.

## Result — the coverage falsifier fires; the discrimination falsifiers clear

Scored with the parametrised Deezer `score.py` (`--value-key pageviews`), so the four §5
falsifiers are computed by the *same* code. Full output in `score.json`.

| §5 test | Result | Falsifier | |
|---|---|---|---|
| Primary — AUC(know-well > heard-of), S4 excluded | **0.720** (n=5 vs 5) | < 0.70 | clear |
| Catastrophic inversions outside S4 | **0** | > 1 | clear |
| Band separation B_unk | valid at **239,239** (80% never-heard below) | none exists | clear |
| Secondary Spearman (diagnostic, non-gating) | 0.653 pooled | — | — |
| **Match failure** | **9 of 29 (31.0%)** | **> 6 of 29** | **FIRES** |

**One falsifier fires, so `pageviews` is unfit per §5 — but note *which*.** Wikipedia
passes the two tests Deezer **failed** (Deezer: AUC 0.68, 2 inversions) and fails the one
Deezer passed (Deezer match failure 3.4%). The two proxies are unfit for **opposite**
reasons:

- **Deezer** sees everyone but **misranks the mid-fame band** (market/genre skew:
  Paul Simon and Death Cab below Diana Krall).
- **Wikipedia** ranks well where it has data but is **blind to the obscure tail** — the
  9 failures are 8 of the 9 S1 lo-fi/synthwave acts plus the S4 off-platform CROOVE.

That is the decisive point: an artist absent from English Wikipedia is exactly the kind of
artist Track 2 wants to route **toward** at depth (F2). A proxy that cannot score the
obscure stratum cannot set C1/C2's reach criteria, however well it ranks the artists it
*can* see. The coverage falsifier is measuring the real deficiency, not an artifact — so it
is not argued away, exactly as Deezer's near-miss AUC was not argued away.

**All 9 failures verified genuine** (audit in the execution log): for every one, no
opensearch candidate satisfies identity + performer + musicality. Miami Nights 1984 returns
no article at all; `idealism` has only the philosophy concept and an unrelated album; the
rest resolve only to wrong-spelling or wrong-entity candidates that the identity clause
correctly rejects.

## Rules fixed before fetching (methodology; the header of `fetch_pageviews.py` is canonical)

- **Target:** English Wikipedia. The perception modelled is the owner's; he is
  English-speaking. Stated, not defaulted.
- **Metric:** sum of monthly `user`-agent pageviews (bots excluded) over a **fixed
  12-month window, 2025-07 .. 2026-06**. Sum is rank-identical to average over a fixed
  window, so AUC/Spearman are unaffected. Window asserted in code.
- **Falsifier:** match failure > 6 of 29 (§9 A10, unchanged proportion).
- **Shares no code with `clips.py` or the Deezer `fetch_fame.py`** (§0) — different source,
  different resolver, a locally-defined normaliser.

## The resolver, and the two corrections the probe + first run forced

Name → article resolution is the hard part Deezer did not have (its artist search returns
artists; Wikipedia is general). The rule that survived is **identity-checked, musician-aware,
uniform**: opensearch candidates → for each, read its Wikidata entity → accept the first
that satisfies **all three**: (a) the query name is one of the entity's labels/aliases in
any language after normalisation; (b) the entity is **not a work** (album/song/film — a
performer); (c) it is **musical** (genre/instrument/occupation/band-type). Two corrections
got it there, both caught before any score was computed and both **identity-directed, not
outcome-directed** (the AUC was not looked at until the resolver was correct):

1. **The `--probe` killed the bare-top-hit rule.** Portishead and Sault resolve to the
   *town*, not the band; a strict top-hit rule fails famous acts whose name is a place,
   biasing the signal against fame. → candidates + a musicality filter.
2. **The first sample run killed musicality-alone.** It accepted fuzzy garbage that happens
   to be musical: CROOVE → Russell Crowe (has a band), Leavv → an Italian film, sleepy fish
   → Johnny Pearson, idealism → "Idealism (album)". → the **identity** clause (the entity
   must actually be named the query) and the **performer** clause (not a work). This is
   Deezer's exact-name discipline generalised to an entity's multilingual identity, which is
   also what lets 林俊傑 → JJ Lin resolve via its zh alias.

A **third** fix, inside correction 2: the performer test is defined by **excluding works**,
not by whitelisting band types — a real band (Wishbone Ash) is typed "rock band", a
musical-group subclass with its own QID, and a whitelist wrongly rejected it.

## Where this leaves Track 2 — the terminal fallback, and it is the owner's call

Both pre-registered proxies have now fired at least one falsifier. Per §5 the terminal
fallback is **owner-labelling of the evaluated-path artists only** (bounded: the sweep
touches at most a few hundred distinct interiors; labels are reusable across arms), with
C1's statistic degrading to the labelled ordinal scale. **That fallback spends real owner
time and is his decision — it must not be entered without putting it to him** (§5; handoff
§2). No sweep arm has run. Adopted artifact untouched, sha256 `4cb84ef9…b061dc8`.

## Post-hoc exploration (owner-requested; NOT pre-registered — `explore_absence.py`)

Run *after* the falsifier fired, to test the idea the coverage failure hinted at: is
Wikipedia **absence itself** a usable obscurity signal? These figures are exploratory and
do not change the pre-registered verdict above.

- **Absence perfectly predicts "never heard of" on this sample: P(never heard of | absent)
  = 1.00** (all 9 misses). No miss was an artist the owner knew.
- Encoding **absent = fame floor (0)**, the proxy separates *known-at-all* from *never
  heard of* at **AUC 0.954** (S4 excluded) — vs 0.880 using matched artists only. The
  absence signal carries most of the obscure-tail mass.
- **Hybrid (Option B) burden on this sample:** Wikipedia covers 20/29 (69 %); the owner
  would hand-label only the **9 misses (31 %)**.

**Caveat, stated because the sample cannot test the failure mode.** The one way
"absence = obscure" breaks is a *foreign-language / historically-notable* artist the owner
would know but who has no English article. This sample contains almost no such opportunity:
its one off-platform-famous case (林俊傑 / JJ Lin) **matched**, and its one absent S4 case
(CROOVE — a Korean rhythm-game producer) was genuinely never-heard-of. So "0 counterexamples"
is weak evidence about the sweep's broader population, where such artists will appear. The
0.954 is also partly "easy": 9 of 13 never-heard are floored to 0 by absence, so the
construction of the sample does much of the separating.

## Files

- `fetch_pageviews.py` — the fetcher (`--probe` and sample modes). Rules canonical in its header.
- `test_resolve.py` — 26 offline tests for the pure resolver helpers (no network).
- `pageview_counts.json` — the fetched counts, shaped like Deezer's `fan_counts.json`.
- `score.json` — the four falsifiers, written by the shared `../2026-07-23-track2-fame-proxy/score.py`.
- Reused, never copied: `labels.json`, `sample.json`, `blind_order.json` in the Deezer dir.
