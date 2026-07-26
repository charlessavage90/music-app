"""Bulk candidate lookup: which names could possibly have an English article?

**This module never decides a fame value. It only decides who does not need asking.**

The rate-limit problem. The canonical A11/A15 resolver costs ~10 HTTP requests per
name against the MediaWiki and Wikidata Action APIs. Over 12,041 names that is
~120,000 requests, and `Wikipedia:Database_download` asks for "at least a second
delay between requests" and "no more than one or two simultaneous HTTP
connections". Run at a compliant rate that is a day and a half; run faster and it
degrades — measured, at 4 workers: sustained load produced repeated hard failures
that a burst of the same 4 workers does not (the failures were cumulative, not
per-request).

**Why this is a filter and not a replacement.** A SPARQL transcription of A11's
three clauses (identity, performer, musical) is fast — 1.4 s for 20 names on the
indexed exact-label form — but it is much less PRECISE than the canonical
resolver, and the reason is instructive: the canonical resolver walks
**opensearch's top-5 in rank order and accepts the first candidate that passes**,
so English opensearch's ranking is doing most of the disambiguation work. The
clauses alone are broad — Wikidata's P136 "genre" applies to paintings and novels,
so a bulk query for `Justice` returns a Titian, a DC Comics character and a
Star Trek episode alongside `Justice (band)`.

Choosing between those candidates would be a NEW disambiguation rule, and A11's
§5 validation would no longer describe the instrument producing the figures. So
this module does not choose. It answers only the one-sided question:

    does ANY musical-performer entity with an English Wikipedia article carry
    this name as a label or alias?

  - **No** -> the canonical resolver cannot match it either, so it is floored
    without being asked. This is the saving.
  - **Yes** -> the canonical resolver runs on it, unchanged, and its answer is
    the answer.

The saving is sound only if this query's recall is at least the canonical
resolver's. That is not assumed: `verify_sparql_recall.py` checks it against every
name the canonical resolver has already matched, and a single miss invalidates the
filter.

Case handling: Wikidata's label index is exact, while A11's `normalise` casefolds.
Each name is therefore submitted in several case variants, which keeps the query
indexed (and fast) while recovering the case-insensitivity the canonical rule has.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

WDQS = "https://query.wikidata.org/sparql"
UA = "artistpath-fame-proxy/1.0 (https://github.com/charlessavage90/music-app; research)"
BATCH = 120
PAUSE_S = 1.0  # WDQS is a donated service; one query per second, serial.

# Transcribed from fetch_pageviews.py's constants — the SAME QIDs. Kept as literal
# text so the query is readable, and asserted against the canonical sets on import
# so a drift in either becomes an error rather than a silent divergence.
MUSIC_OCCUPATIONS = ("Q639669", "Q177220", "Q36834", "Q488205", "Q753110", "Q855091",
                     "Q2252262", "Q130857", "Q183945", "Q158852", "Q486748", "Q806349")
BAND_TYPES = ("Q215380", "Q2088357", "Q9212979", "Q281643", "Q7623897")
WORK_TYPES = ("Q482994", "Q7366", "Q134556", "Q169930", "Q2188189", "Q11424",
              "Q5398426", "Q7889", "Q4167410", "Q13442814")


def _assert_clauses_match_canonical() -> None:
    """Fail loudly if the canonical QID sets ever diverge from this transcription."""
    import fetch_pageviews as fp

    for name, mine, theirs in (
        ("MUSIC_OCCUPATIONS", set(MUSIC_OCCUPATIONS), fp.MUSIC_OCCUPATIONS),
        ("BAND_TYPES", set(BAND_TYPES), fp.BAND_TYPES),
        ("WORK_TYPES", set(WORK_TYPES), fp.WORK_TYPES),
    ):
        if mine != set(theirs):
            raise AssertionError(
                f"{name} has drifted from fetch_pageviews.py: "
                f"only here {mine - set(theirs)}, only there {set(theirs) - mine}"
            )
    if fp.MUSIC_MARKER_PROPS != {"P136", "P1303"}:
        raise AssertionError(f"MUSIC_MARKER_PROPS drifted: {fp.MUSIC_MARKER_PROPS}")


def case_variants(name: str) -> list[str]:
    """The case forms to submit, since Wikidata's label index is exact.

    A11's identity rule casefolds, so 'BUMPER' and 'Bumper' are the same name to
    it. Submitting a handful of variants recovers that without abandoning the
    indexed exact-match form, which is the only form that does not time out.
    """
    out = {name, name.lower(), name.upper(), name.title()}
    if name and name[0].islower():
        out.add(name[0].upper() + name[1:])
    return [v for v in out if v.strip()]


def build_query(names: list[str]) -> str:
    variants: list[str] = []
    for n in names:
        variants.extend(case_variants(n))
    # SPARQL string literals: escape backslash and quote only.
    vals = " ".join(
        '"%s"@en' % v.replace("\\", "\\\\").replace('"', '\\"') for v in sorted(set(variants))
    )
    occ = " ".join(f"wd:{q}" for q in MUSIC_OCCUPATIONS)
    band = " ".join(f"wd:{q}" for q in BAND_TYPES)
    work = " ".join(f"wd:{q}" for q in WORK_TYPES)
    return f"""
SELECT DISTINCT ?lbl ?article WHERE {{
  VALUES ?lbl {{ {vals} }}
  {{ ?item rdfs:label ?lbl }} UNION {{ ?item skos:altLabel ?lbl }}
  {{ ?item wdt:P136 [] }} UNION {{ ?item wdt:P1303 [] }}
  UNION {{ ?item wdt:P106 ?o . VALUES ?o {{ {occ} }} }}
  UNION {{ ?item wdt:P31 ?b . VALUES ?b {{ {band} }} }}
  FILTER NOT EXISTS {{ ?item wdt:P31 ?w . VALUES ?w {{ {work} }} }}
  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
}}"""


def run_batch(names: list[str], timeout_s: int = 120) -> dict[str, list[str]]:
    """name (as given) -> the English article titles any case variant matched."""
    query = build_query(names)
    data = urllib.parse.urlencode({"query": query, "format": "json"}).encode()
    req = urllib.request.Request(
        WDQS, data=data,
        headers={"User-Agent": UA, "Accept": "application/sparql-results+json",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as fh:  # noqa: S310 - fixed host
        doc = json.loads(fh.read().decode("utf-8"))

    # Fold the case variants back onto the caller's spelling.
    by_variant: dict[str, set[str]] = {}
    for b in doc["results"]["bindings"]:
        lbl = b["lbl"]["value"]
        title = urllib.parse.unquote(b["article"]["value"].rsplit("/", 1)[-1]).replace("_", " ")
        by_variant.setdefault(lbl, set()).add(title)
    out: dict[str, list[str]] = {}
    for n in names:
        hits: set[str] = set()
        for v in case_variants(n):
            hits |= by_variant.get(v, set())
        out[n] = sorted(hits)
    return out


def candidates_for(names: list[str], verbose: bool = True) -> dict[str, list[str]]:
    _assert_clauses_match_canonical()
    result: dict[str, list[str]] = {}
    batches = [names[i:i + BATCH] for i in range(0, len(names), BATCH)]
    for i, chunk in enumerate(batches, 1):
        for attempt in range(4):
            try:
                result.update(run_batch(chunk))
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt == 3:
                    raise
                if verbose:
                    print(f"    batch {i} retry {attempt + 1}: {type(exc).__name__}")
                time.sleep(3 * (attempt + 1))
        if verbose:
            hits = sum(1 for n in chunk if result.get(n))
            print(f"  batch {i}/{len(batches)}: {hits}/{len(chunk)} name(s) have a candidate")
        time.sleep(PAUSE_S)
    return result
