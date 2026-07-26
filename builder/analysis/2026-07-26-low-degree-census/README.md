# Degree-1 / degree-2 census with an external fame figure — 2026-07-26

Who the app **can never introduce you to**. A degree-1 artist needs a neighbour on
each side to be an interior card and has only one, so it can only ever appear as one
of the two artists the user typed (`DRV-4`, stated there as structural and
unmeasured — this is the measurement). Degree-2 artists are reachable, but by
exactly one route.

**Everything here is read-only.** The artifact is read, never written; no rebuild, no
routing, no arm, no config change, no adoption, no proposal. Path-quality work is
paused by owner decision and this census does not resume it.

`REPORT.md` is the deliverable. `flagged_unmatched.md` is its companion omission list.

| script | reads | produces |
|---|---|---|
| `extract_low_degree.py` | adopted APG1 artifact, crawl archive key count | `low_degree.json` — every degree-1 and degree-2 node with name, disambiguation, degree, `pop_raw`, neighbours, and in-graph name collisions |
| `verify_screen.py` | `low_degree.json` | validates the popularity screen (`S1`–`S3`), the post-prune question, and the non-artist-entity question |
| `select_poll_set.py` | `low_degree.json` | `poll_set.json` — the top 400 by popularity per set (`screen`) plus a seeded random 200 from below the cut (`control`) |
| `resolve_fame.py` | `poll_set.json` | `fame_cache.json` — canonical A11/A15 fame rows |
| `report.py` | all of the above | `REPORT.md`, `flagged_unmatched.md` |
| `transport.py` | — | retry wrapper installed into the canonical resolver's network layer |
| `verify_pool_equivalence.py` | `low_degree.json` | asserts the thread pool changes throughput only |
| `verify_sparql_recall.py` | ground-truth caches | **records a FAILED approach — see below** |

```bash
# from api/ (imports the API's artifact reader — the code the app runs)
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-26-low-degree-census/extract_low_degree.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-26-low-degree-census/verify_screen.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-26-low-degree-census/select_poll_set.py

# from this directory (the network half is resumable; re-runs cost only what is left)
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --project ../.. python -u \
  resolve_fame.py --workers 2 --passes 8
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --project ../.. python -u report.py --top 200
```

## The artifact is asserted, not assumed

`extract_low_degree.py` checks the adopted **sha256** before reading a byte, as the
other scripts here do. `DRV-1` is the record of what happens when a measurement
forgets: every table in Phase 1 log §2.9–§2.12 was computed on `graph-t15-capfix.bin`
while the app had been running `graph-t15-tiebreakfix.bin` for hours. `report.py`
re-checks the checksum recorded in both JSON inputs, so a stale intermediate cannot
reach the report either.

## The fame proxy is imported, never reimplemented

`fetch_pageviews.py` (A11-canonical) and `fame.py`'s `english_article_fallback` (A15)
are called unchanged. **A15 matters more here than anywhere it has been used**: the
deliverable is a fame-*ranked* list, so the exact defect it fixed — a household name
with an ambiguous short name (Justice, Rainbow, Ye) floored because opensearch buries
it — would drop that artist out of the list entirely rather than misplace it.

## Three silent-flooring mechanisms, all found the same way

Every one of these makes an artist look **maximally obscure** and disappear from a
ranked list without leaving a trace in the output. That is the worst available failure
shape for this deliverable, and none of them was found by reading code carefully —
each was found by a check that compared two things.

1. **Throttling becomes obscurity.** `fame._wikidata_search` and
   `_entity_with_sitelinks` both end in `except Exception: return []`, so a 429 is
   indistinguishable from "no such entity" — and under A11 an unresolvable artist is
   scored at the fame floor. `verify_pool_equivalence.py` caught it live:
   `Compulsion` resolved to `Compulsion (band)` (3,801 pageviews) serially and to the
   floor pooled. `transport.py` fixes it by retrying transient failures and **raising**
   rather than returning empty; 404 is re-raised immediately, since `pageviews_sum`
   relies on it meaning "no data". No accept criterion is touched.
2. **A bulk shortcut lost real matches.** `sparql_candidates.py` transcribes A11's
   three clauses into SPARQL to decide who does not need asking.
   `verify_sparql_recall.py` **failed it**: 15 of 438 canonically-matched names had no
   candidate, including Guns N' Roses, Destiny's Child, Roxy Music, Cat Stevens and
   林俊傑 → JJ Lin. Three causes — punctuation folding A11's `normalise` does and
   SPARQL does not, cross-language aliases missed by the `@en` tag, and a third that
   was never explained. **Abandoned, not patched.** Both files are retained as the
   record of a rejected approach; neither feeds the report.
3. **The same query reached the album and missed the band.** For `Roxy Music`,
   `?article schema:about ?item` returned `Roxy_Music_(album)` while the band was
   unreachable by the label pattern. This is why (2) was abandoned rather than
   debugged: the clauses alone are broad — Wikidata's P136 "genre" applies to
   paintings and novels — and the canonical resolver's precision comes largely from
   **opensearch's ranking**, which it walks in order, accepting the first pass. Any
   bulk replacement must invent a disambiguation rule, and then A11's §5 validation no
   longer describes the instrument producing the figures.

**A fourth, avoided by design:** a name left unresolved by network failure is *not*
cached and *not* floored. `resolve_fame.py` runs repeat passes until one resolves
nothing new, and `report.py` counts whatever survives as **unresolved**, separately
from artists that genuinely have no English article.

## Why in-graph popularity may screen this set but not rank it

Polling all 12,041 names costs ~120,000 API requests, and
`Wikipedia:Database_download` asks for "at least a second delay between requests" and
"one or two simultaneous HTTP connections". Measured attrition at 2 workers is ~19 %
per pass; at 4 it degrades badly, and the degradation is cumulative rather than
per-request.

So the set is screened by `pop_raw` — the owner's methodology call, 2026-07-26 — and
the screen is sound for a specific reason worth keeping: popularity is score-weighted
in-degree accumulated at `pipeline.py:206-216`, **before** `mutual_knn_cap` (227),
`symmetrise` (230) and `largest_component` (231), so it is summed over the **full
uncapped neighbour lists**. The reciprocity rule destroys a stranded artist's degree
and leaves its popularity untouched. Degree and popularity are not merely different
currencies (§2.6); they are read at different **stages of the build**, and the screen
rides on the stage the defect never reaches.

`verify_screen.py` validates it on ground truth nobody chose for it: all five `MKS-2`
artists present in this set rank in the **top 11 of 6,396** — Nada Surf 1st, The Cult
4th, Meat Loaf 7th, Elbow 8th, The Streets 11th — against a cut at 400.

**But `pop_raw` is never used to order any output** (§2.11: at the top of the
distribution it disagrees with household fame — a lo-fi producer and a Beatle score
alike). It selects who to ask; pageviews rank.

**The screen's ground truth is mildly circular**, which is why the `control` role
exists: `MKS-2` found its six artists by noticing *recognisable* names among
low-degree ones, already correlating with being well-connected pre-cap. The control is
a seeded random sample from below the cut, selected on nothing, and the report states
its verdict either way. What neither can see is the screen's one known failure
direction — an artist famous in a population this snowball crawl under-covers sits low
on popularity while being a household name. That is the **same blind-spot direction
A11 already accepts** for Wikipedia-absence, so the two instruments do not
cross-check each other.
