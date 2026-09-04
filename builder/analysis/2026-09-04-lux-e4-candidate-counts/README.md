# `LUX-E4` — how many cards can offer another track

**This directory OWNS these figures.** Cite this file; never restate its numbers anywhere else.

- Script: `candidate_counts.py` — run from `api/`
- Raw output: `candidate_counts.json` (every row, plus the summary tables below)
- Governing spec: `docs/superpowers/specs/2026-09-03-launch-ux-scope.md` §5 (`LUX-E4`)
- Plan: `docs/superpowers/plans/2026-09-04-launch-ux-1-3.md`, task `LUX-T7`

**What this measures, in the words fixed in the scope document before any result existed:**

> *for how many of the cards a user sees does a "try another track" button appear at all — and
> does it disappear exactly for the obscure artists?*

**Threshold, also pre-registered (spec §5):** if fewer than **half** of lower-half cards carry
≥ 2 candidates, `LUX-3` serves famous artists and not the ones the app is for. That is a
**re-prioritisation trigger and the owner's call.**

---

## 1. Run state

| | |
|---|---|
| Artifact | `builder/scratch/graph-msw-tu50.bin`, 58,838 artists |
| sha256 | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` — read from the manifest sidecar and enforced by `load_graph`; the script refuses on a mismatch |
| Pair sample | `builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json` — the committed 120 `TAS-` pairs (40 ff / 40 fo / 40 oo) |
| Weights | production `ApiConfig` defaults, no exclusions, no bypass presses |
| Catalogues | live Deezer and iTunes through the real `ClipResolver`, serial, ≥ 0.34 s between outbound calls, resolver circuit breaker in place |
| Live calls | 309, across 304 distinct artists |
| Wall clock | 125.6 s end to end (17.0 s of it routing) |
| Catalogue refusals | none — no 429 and no 5xx; the run completed on its registered terms |
| Date | 2026-09-04 |

**Interiors only.** Endpoints are excluded because they are the user's own picks, not what the
app delivered — the rule and its reasoning come from `../2026-08-02-dsp-ids/delivered_coverage.py`.

**One live resolution per distinct artist, attributed to each of its card impressions.** The
candidate list is a property of the artist and the cache makes a second resolution of the same
mbid return the first one's count, so this is identical in outcome to resolving per card and
costs several hundred fewer live calls.

---

## 2. Measured

### 2a. Sample attrition — read this before the tables

`tas_pairs.json` was drawn against the **pre-MSW** artifact. On the adopted artifact **49 of the
120 pairs cannot be routed at all**, because at least one endpoint is no longer in the graph:

| class | pairs | routable | endpoint absent |
|---|---|---|---|
| `ff` (famous × famous) | 40 | 40 | 0 |
| `fo` (famous × obscure) | 40 | 22 | 18 |
| `oo` (obscure × obscure) | 40 | 9 | 31 |
| **all** | **120** | **71** | **49** |

The loss falls almost entirely on the obscure classes. **71 pairs routed → 443 interior cards →
304 distinct interior artists.**

Lower-half artists are still present in the surviving sample **as endpoints**: of the 142
endpoints of the 71 routed pairs, 32 are lower half, 25 upper half, 24 top 10%, 56 top 1%,
5 top 0.1%.

### 2b. Cards (impressions) by popularity band

Bands are the fixed fame frame — percentile rank of `pop_raw` over the adopted artifact
(`cb_metrics.BANDS`). Percentile, not value.

| band | cards | ≥ 1 candidate | ≥ 2 candidates | fraction ≥ 2 | mean count |
|---|---|---|---|---|---|
| top 0.1% | 15 | 15 | 15 | 100.0% | 23.13 |
| top 1% | 243 | 243 | 243 | 100.0% | 23.32 |
| top 10% | 137 | 135 | 128 | 93.4% | 21.64 |
| upper half | 48 | 48 | 47 | 97.9% | 19.79 |
| **lower half** | **0** | — | — | **—** | — |
| **all** | **443** | **441** | **433** | **97.7%** | 22.41 |

**No card in any of the 71 routed journeys was a lower-half artist.** The least popular interior
artist delivered anywhere in the run sits at the **59.5th percentile**.

### 2c. Distinct artists by popularity band

| band | artists | ≥ 1 | ≥ 2 | fraction ≥ 2 | mean count |
|---|---|---|---|---|---|
| top 0.1% | 10 | 10 | 10 | 100.0% | 22.40 |
| top 1% | 135 | 135 | 135 | 100.0% | 22.99 |
| top 10% | 112 | 111 | 107 | 95.5% | 22.08 |
| upper half | 47 | 47 | 46 | 97.9% | 19.68 |
| lower half | 0 | — | — | — | — |
| **all** | **304** | **303** | **298** | **98.0%** | 22.12 |

### 2d. Cards by resolution route

| route | cards | ≥ 1 | ≥ 2 | fraction ≥ 2 | mean count |
|---|---|---|---|---|---|
| `deezer-id` | 414 | 414 | 407 | 98.3% | 22.97 |
| `deezer-name` | 26 | 26 | 25 | 96.2% | 16.04 |
| `itunes` | 1 | 1 | 1 | 100.0% | 2.00 |
| none (nothing found) | 2 | 0 | 0 | 0.0% | 0.00 |

93.5% of cards were answered by the Deezer **id** path. The name path answered 26 and iTunes
exactly one; the two cards with nothing at all are one artist (a diacritic-heavy name, top 10%
band) shown twice.

### 2e. Cards by band and route

| band / route | cards | ≥ 2 | fraction ≥ 2 | mean count |
|---|---|---|---|---|
| top 0.1% / `deezer-id` | 15 | 15 | 100.0% | 23.13 |
| top 1% / `deezer-id` | 237 | 237 | 100.0% | 23.58 |
| top 1% / `deezer-name` | 6 | 6 | 100.0% | 12.83 |
| top 10% / `deezer-id` | 124 | 118 | 95.2% | 22.70 |
| top 10% / `deezer-name` | 10 | 9 | 90.0% | 14.80 |
| top 10% / `itunes` | 1 | 1 | 100.0% | 2.00 |
| top 10% / none | 2 | 0 | 0.0% | 0.00 |
| upper half / `deezer-id` | 38 | 37 | 97.4% | 19.95 |
| upper half / `deezer-name` | 10 | 10 | 100.0% | 19.20 |

### 2f. Cards by pair class

| class | cards | ≥ 1 | ≥ 2 | fraction ≥ 2 | mean count |
|---|---|---|---|---|---|
| `ff` | 177 | 177 | 174 | 98.3% | 22.34 |
| `fo` | 193 | 191 | 188 | 97.4% | 22.37 |
| `oo` | 73 | 73 | 71 | 97.3% | 22.67 |

---

## 3. The read against the pre-registered threshold

**The threshold cannot be read, because its denominator is empty: there were zero lower-half
cards.** 443 cards, none of them a lower-half artist. "Fewer than half of lower-half cards carry
≥ 2 candidates" is neither true nor false here; it is undefined.

**It did not fire, and it was not cleared either.** Recording it as "passed" would be the same
error as recording it as "failed" — both claim a measurement that does not exist. What the run
does establish, on the bands it did reach: **97.7% of all cards, and 97.9% of the most obscure
band reached (upper half, 48 cards), carry ≥ 2 candidates.**

**The plain-sentence answer, restricted to what was measured:** on the journeys these 71 pairs
produce, a "try another track" button would appear on 433 of 443 cards. It does **not** disappear
for obscure artists in the region measured — the fraction is flat across every band from the top
0.1% down to the upper half. Whether it disappears for genuinely obscure artists is the part
this run could not observe, because the router did not put one on a card.

---

## 4. What is NOT established

- **Nothing about lower-half artists.** Zero cards, so zero evidence either way. The registered
  threshold is about exactly that population, and this run does not speak to it.
- **The obscure end of the sample was largely lost before routing began** — 31 of 40 `oo` pairs
  and 18 of 40 `fo` pairs have an endpoint that is not in the adopted artifact (§2a). The `oo`
  row in §2f rests on 9 pairs, not 40.
- **Depth zero only.** These are the paths a user sees *before pressing anything*. The one bypass
  control reachable from the UI (`known`, "Dig deeper" — `LUX-1` removed the other) pushes a
  journey toward more obscure artists; every figure here is from the un-pressed path, which is
  the popular end of what the app produces.
- **Counts are censored at 25** (`ApiConfig.clip_search_limit`). 319 of 443 cards read exactly
  25, which means "at least 25", not "25". Every mean above is a censored mean and understates
  the true one. Nothing here depends on the difference — the question is ≥ 2, far from the
  ceiling — but do not read the means as catalogue depth.
- **De-duplication is by normalised title only.** "Song" and "Song (Remastered 2011)" are two
  candidates, not one. A count of 3 means three distinct titles, not three distinct recordings.
  This is a known limitation of `clips._dedupe_by_title`, stated here as a bound and deliberately
  not fixed.
- **This is what the resolver finds today**, on 120 pairs, against one artifact. Catalogue
  contents move, and a user's own journeys are not these journeys.
- **`deezer-name` and `itunes` are barely exercised** — 26 and 1 card. Their columns are reported
  because the split was asked for, not because they carry weight at this n.
