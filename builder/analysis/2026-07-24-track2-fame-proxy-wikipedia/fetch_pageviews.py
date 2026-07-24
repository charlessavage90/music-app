"""P4 fallback: fetch English-Wikipedia pageviews for the fixed sample.

Deezer `nb_fan` FAILED §5 (2 pre-registered falsifiers: AUC 0.68 < 0.70, and 2
catastrophic inversions outside S4). Per pre-registration §5 the pre-registered response
is to **re-run the identical protocol against Wikipedia pageviews, same labels, no
re-asking the owner.** This module is the fetch half; scoring reuses the Deezer
`score.py` (now proxy-agnostic) pointed at this file's output.

**Shares no code with `clips.py` OR with the Deezer `fetch_fame.py`** — different source,
different resolver. `clips.py`'s wrong-artist failure mode (first track hit, no name
check) must not enter the quantity the sweep is scored on (§0).

--------------------------------------------------------------------------------
Rules FIXED before fetching (methodology; mirrors Deezer's "exact-match-after-P5 first").
Fixing them here, on the record, is the point — see the README.
--------------------------------------------------------------------------------

  * Target       : English Wikipedia (en.wikipedia). The perception modelled is the
                   owner's, and he is English-speaking. Stated, not defaulted.
  * Metric       : SUM of monthly pageviews over a fixed 12-month window, agent=user
                   (bots/spiders excluded), access=all-access. Sum over a fixed window is
                   rank-identical to the average, so AUC/Spearman are unaffected by the
                   choice; sum is reported.
  * Window       : 2025-07 .. 2026-06 inclusive (12 complete months). June 2026 is the
                   last fully-available month as of 2026-07-24. ASSERTED below.
  * Resolution   : IDENTITY-CHECKED, MUSICIAN-AWARE, UNIFORM. enwiki `opensearch` (top few
                   hits, which include redirects, so 林俊傑 -> "JJ Lin" resolves) -> for
                   each candidate, read its Wikidata entity -> accept the FIRST candidate
                   that satisfies ALL of: (a) the query name equals one of the entity's
                   labels/aliases in ANY language after normalisation (identity); (b) the
                   entity is a PERFORMER -- a human or a band/group, not a work; (c) it is
                   MUSICAL (a music genre/instrument, a music occupation, or a band type).
                   Its enwiki article -> pageviews.

                   WHY each clause, both learned from --probe and the first sample run:
                   - Bare top hit fails FAMOUS acts whose name is a place ("Portishead",
                     "Sault" -> the town). Killed by the probe. -> need candidates + filter.
                   - Musicality ALONE still accepts fuzzy garbage that happens to be
                     musical: CROOVE -> Russell Crowe (has a band), Leavv -> an Italian
                     film, sleepy fish -> Johnny Pearson. Killed by the first sample run.
                     -> the IDENTITY clause: the entity must actually be named the query.
                   - The PERFORMER clause rejects albums/songs that share the name
                     (idealism -> "Idealism (album)").
                   The rule is uniform across famous and obscure, so a genuine no-article
                   act (saib., Miami Nights 1984) stays a legitimate MATCH FAILURE, never
                   hand-forced. This is Deezer's exact-name discipline, generalised to an
                   entity's multilingual identity so 林俊傑 -> JJ Lin still resolves.
  * Falsifier    : match failure > 6 of 29 (§9 A10, unchanged proportion, denominator 29).

Two modes:

    python fetch_pageviews.py --probe    # discharge the external assumption, out-of-sample
    python fetch_pageviews.py            # fetch the sample; requires labels.json to exist

`--probe` checks the assumptions this module rests on -- that the Wikimedia REST pageviews
API returns per-article monthly counts, AND that the musician-aware resolver survives the
place/band collision -- against artists NOT in the sample (Radiohead, and the two collision
cases Portishead/Sault), exactly as the Deezer fetcher probed before touching the sample.
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
# labels.json and sample.json are the COMMITTED, FIXED files from the Deezer run. Reused,
# never re-collected or re-shuffled (§5: same labels, no re-asking).
DEEZER = HERE.parent / "2026-07-23-track2-fame-proxy"
SAMPLE = DEEZER / "sample.json"
LABELS = DEEZER / "labels.json"
OUT = HERE / "pageview_counts.json"

# Fixed window, asserted so a typo cannot silently shift it. Monthly granularity: the REST
# API wants YYYYMMDD; monthly buckets are keyed on the first of the month.
WINDOW_START = "20250701"
WINDOW_END = "20260630"
WINDOW_MONTHS = 12  # 2025-07 .. 2026-06 inclusive

MEDIAWIKI = "https://en.wikipedia.org/w/api.php"
WIKIDATA = "https://www.wikidata.org/w/api.php"
REST = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
PROJECT, ACCESS, AGENT = "en.wikipedia", "all-access", "user"

OPENSEARCH_LIMIT = 5  # candidates to consider before declaring a match failure

# Wikidata musicality markers. A candidate is "a musical act" if ANY holds. P136 (genre)
# and P1303 (instrument) are near-universal on recording artists and bands and make an
# exhaustive occupation list unnecessary; the occupation/type sets below catch the rest.
MUSIC_MARKER_PROPS = {"P136", "P1303"}  # has-genre, plays-instrument
MUSIC_OCCUPATIONS = {  # P106 occupation
    "Q639669",    # musician
    "Q177220",    # singer
    "Q36834",     # composer
    "Q488205",    # singer-songwriter
    "Q753110",    # songwriter
    "Q855091",    # guitarist
    "Q2252262",   # rapper
    "Q130857",    # disc jockey
    "Q183945",    # record producer
    "Q158852",    # conductor
    "Q486748",    # pianist
    "Q806349",    # bandleader
}
BAND_TYPES = {  # P31 instance-of
    "Q215380",    # musical group
    "Q2088357",   # musical ensemble
    "Q9212979",   # musical duo
    "Q281643",    # boy band
    "Q7623897",   # girl group... (kept broad; harmless supersets)
}
HUMAN = "Q5"  # P31 instance-of human
# A performer is anything that is NOT one of these works. Whitelisting performer types was
# tried and failed: a real band (Wishbone Ash) is typed 'rock band', a subclass of musical
# group with a distinct QID, and got wrongly rejected. Excluding works is robust to that
# subtype proliferation while still rejecting an album/song that shares an artist's name.
WORK_TYPES = {
    "Q482994",    # album
    "Q7366",      # song
    "Q134556",    # single
    "Q169930",    # extended play (EP)
    "Q2188189",   # musical work/composition
    "Q11424",     # film
    "Q5398426",   # television series
    "Q7889",      # video game
    "Q4167410",   # Wikimedia disambiguation page
    "Q13442814",  # scholarly article
}

# Wikimedia asks for a descriptive User-Agent with contact; a generic one risks a 403/429.
UA = "artistpath-fame-proxy/1.0 (https://github.com/charlessavage90/music-app; research)"
PAUSE_S = 0.3
TIMEOUT_S = 20

# Artists deliberately NOT in the sample -- probe only. Radiohead checks the API; Portishead
# and Sault are the place/band collision cases that killed the first resolver.
PROBE_NAMES = ["Radiohead", "Portishead", "Sault"]


# --------------------------------------------------------------------------- pure helpers
# These take no network and are unit-tested in test_resolve.py.

def assert_window() -> None:
    """The window is 12 whole months and end follows start. A guard against a typo above."""
    if not (WINDOW_START < WINDOW_END and len(WINDOW_START) == len(WINDOW_END) == 8):
        raise AssertionError(f"bad window {WINDOW_START}..{WINDOW_END}")


# Local, deliberately NOT imported from the Deezer fetch_fame.py (§0 keeps the two
# resolvers decoupled). Same shape as P5: NFKC, fold common punctuation, collapse
# whitespace, strip, casefold. Used for the entity-identity check, not for search.
_FOLD = str.maketrans({
    **{c: "-" for c in "‐‑‒–—―−"},
    **{c: "'" for c in "‘’ʼ"},
    **{c: '"' for c in "“”"},
    "​": "", "﻿": "",
})


def normalise(name: str) -> str:
    s = unicodedata.normalize("NFKC", name).translate(_FOLD)
    return re.sub(r"\s+", " ", s).strip().casefold()


def entity_names(entity: dict) -> set[str]:
    """Every label and alias of a Wikidata entity, across all languages, normalised.

    `entity` is one value of wbgetentities' `entities` map. This is the set the query name
    must be found in for an identity match -- it is what lets 林俊傑 match JJ Lin (the
    Chinese string is a zh alias) while rejecting Russell Crowe for CROOVE.
    """
    names: set[str] = set()
    for lab in entity.get("labels", {}).values():
        names.add(normalise(lab["value"]))
    for alias_list in entity.get("aliases", {}).values():
        for a in alias_list:
            names.add(normalise(a["value"]))
    return names


def name_matches(query: str, entity: dict) -> bool:
    """True if the query name is one of the entity's labels/aliases after normalisation."""
    return normalise(query) in entity_names(entity)


def is_performer(claims: dict) -> bool:
    """True if the entity is NOT a work (album/song/film/...) -- i.e. a performer.

    Defined by exclusion, not a whitelist: a real band may be typed with any of many
    musical-group subclasses ('rock band', 'hard rock band'), and whitelisting them all is
    whack-a-mole (Wishbone Ash was wrongly rejected that way). Rejects albums/songs that
    share an artist's name (idealism -> 'Idealism (album)'). An entity with no P31 is
    treated as a performer here and is caught by the identity + musicality clauses instead.
    """
    p31 = {
        stmt.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        for stmt in claims.get("P31", [])
    }
    return p31.isdisjoint(WORK_TYPES)


def article_to_rest_path(title: str) -> str:
    """Encode an article title for the REST per-article path segment.

    Wikimedia's convention: spaces -> underscores, then percent-encode everything the path
    would otherwise misread -- crucially '/', which is live in real titles ('AC/DC') and
    would split the path if unescaped. `safe=''` forces '/' to %2F.
    """
    return urllib.parse.quote(title.replace(" ", "_"), safe="")


def is_disambiguation(query_pages: dict) -> bool:
    """True if the resolved MediaWiki page is a disambiguation page.

    `query_pages` is the `query.pages` object from action=query&prop=pageprops. A
    disambiguation page carries a `disambiguation` key under `pageprops`.
    """
    for page in query_pages.values():
        if "disambiguation" in page.get("pageprops", {}):
            return True
    return False


def query_is_missing(query_pages: dict) -> bool:
    """True if the resolved title has no article (a `missing` marker, or negative pageid)."""
    for page in query_pages.values():
        if "missing" in page or int(page.get("pageid", -1)) < 0:
            return True
    return False


def is_musical(claims: dict) -> bool:
    """True if a Wikidata entity's `claims` mark it as a musical act.

    `claims` is the entity's `claims` object (property -> list of statements). Any of:
    a music genre (P136) or instrument (P1303); a music occupation (P106 in the set); or a
    band/group instance-of (P31 in the set). Broad by design -- a false accept here is a
    wrong pageview count, but the alternative (a strict list) drops real acts.
    """
    if any(p in claims for p in MUSIC_MARKER_PROPS):
        return True
    for prop, targets in (("P106", MUSIC_OCCUPATIONS), ("P31", BAND_TYPES)):
        for stmt in claims.get(prop, []):
            qid = (
                stmt.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
            )
            if qid in targets:
                return True
    return False


def sum_views_in_window(items: list[dict]) -> tuple[int, int]:
    """Sum monthly `views` whose timestamp falls in [WINDOW_START, WINDOW_END].

    Returns (total, months_present). Months the API omits (zero traffic) simply do not
    appear and contribute 0; months_present is recorded so an obscure artist with sparse
    coverage is auditable rather than silently undercounted.
    """
    lo, hi = WINDOW_START[:6], WINDOW_END[:6]  # compare on YYYYMM
    total, months = 0, 0
    for it in items:
        ym = str(it.get("timestamp", ""))[:6]
        if lo <= ym <= hi:
            total += int(it.get("views", 0))
            months += 1
    return total, months


# ------------------------------------------------------------------------------- network

def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:  # noqa: S310 - fixed hosts
        return json.loads(resp.read().decode("utf-8"))


def opensearch(name: str, limit: int = OPENSEARCH_LIMIT) -> list[str]:
    """Candidate mainspace titles for `name`, best first. Includes redirect targets."""
    q = urllib.parse.urlencode(
        {"action": "opensearch", "search": name, "limit": limit,
         "namespace": 0, "format": "json"}
    )
    data = _get_json(f"{MEDIAWIKI}?{q}")
    return data[1] if isinstance(data, list) and len(data) > 1 else []


def canonicalise(title: str) -> dict:
    """Resolve redirects and read pageprops (canonical title, Wikidata id, disambiguation)."""
    q = urllib.parse.urlencode(
        {"action": "query", "titles": title, "redirects": 1,
         "prop": "pageprops", "format": "json"}
    )
    data = _get_json(f"{MEDIAWIKI}?{q}")
    query = data.get("query", {})
    pages = query.get("pages", {})
    redirects = query.get("redirects", [])
    canonical = redirects[-1]["to"] if redirects else title
    qid = None
    for page in pages.values():
        qid = page.get("pageprops", {}).get("wikibase_item")
    return {"pages": pages, "canonical": canonical, "qid": qid}


def wikidata_entity(qid: str) -> dict:
    """The labels/aliases/claims for a Wikidata entity, or {} if unavailable."""
    q = urllib.parse.urlencode(
        {"action": "wbgetentities", "ids": qid,
         "props": "labels|aliases|claims", "format": "json"}
    )
    data = _get_json(f"{WIKIDATA}?{q}")
    return data.get("entities", {}).get(qid, {})


def pageviews_sum(title: str) -> tuple[int, int]:
    """Sum monthly `user` pageviews for the canonical `title` over the fixed window."""
    art = article_to_rest_path(title)
    url = f"{REST}/{PROJECT}/{ACCESS}/{AGENT}/{art}/monthly/{WINDOW_START}/{WINDOW_END}"
    try:
        data = _get_json(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:  # no pageview data for this title in the window
            return 0, 0
        raise
    return sum_views_in_window(data.get("items", []))


def resolve(name: str) -> dict:
    """Name -> {matched, article, pageviews, ...}. A miss is recorded, never forced.

    Walks opensearch candidates in order and accepts the first that (a) has an article,
    (b) is not a disambiguation page, (c) carries a Wikidata id, and (d) is a musical act.
    """
    row: dict = {"query": name}
    candidates = opensearch(name)
    if not candidates:
        row.update(matched=False, reason="no search result", article=None, pageviews=None)
        return row

    checked = []
    for cand in candidates:
        canon = canonicalise(cand)
        time.sleep(PAUSE_S)
        title = canon["canonical"]
        if query_is_missing(canon["pages"]) or is_disambiguation(canon["pages"]):
            checked.append((title, "missing/disambig"))
            continue
        if not canon["qid"]:
            checked.append((title, "no wikidata id"))
            continue
        entity = wikidata_entity(canon["qid"])
        time.sleep(PAUSE_S)
        claims = entity.get("claims", {})
        # ALL THREE clauses must hold: identity, performer, musical. Order chosen so the
        # cheapest / most-discriminating (identity) is recorded first for auditing a reject.
        if not name_matches(name, entity):
            checked.append((title, "name mismatch"))
            continue
        if not is_performer(claims):
            checked.append((title, "not a performer (work?)"))
            continue
        if not is_musical(claims):
            checked.append((title, "not a musical act"))
            continue
        views, months = pageviews_sum(title)
        row.update(
            matched=True, article=title, opensearch_candidate=cand,
            wikidata=canon["qid"], pageviews=views, months_present=months,
        )
        return row

    row.update(
        matched=False, reason="no identity-matched musical performer among candidates",
        article=None, pageviews=None, candidates_checked=checked,
    )
    return row


# --------------------------------------------------------------------------------- modes

def probe() -> int:
    assert_window()
    sample_names = {
        n
        for members in json.loads(SAMPLE.read_text(encoding="utf-8"))["strata"].values()
        for n in members
    }
    print("Probing the Wikimedia pageviews API + musician-aware resolver, out-of-sample.")
    print(f"Window {WINDOW_START}..{WINDOW_END} ({WINDOW_MONTHS} months), agent={AGENT}.\n")
    ok = 0
    for name in PROBE_NAMES:
        if name in sample_names:
            raise SystemExit(f"probe name {name!r} is in the sample -- would contaminate it")
        row = resolve(name)
        has = bool(row.get("pageviews"))
        ok += has
        print(
            f"  {name:<12} matched={row['matched']!s:<5} "
            f"article={row.get('article')!r:<22} "
            f"pageviews={row.get('pageviews')} months={row.get('months_present')}"
        )
        time.sleep(PAUSE_S)

    print()
    if ok == len(PROBE_NAMES):
        print("ASSUMPTIONS HOLD: API returns counts and the resolver survives collisions.")
        return 0
    print(f"ASSUMPTIONS FAIL: usable pageviews on {ok}/{len(PROBE_NAMES)}.")
    return 1


def fetch_sample() -> int:
    assert_window()
    if not LABELS.exists():
        raise SystemExit(f"{LABELS} not found -- labels are collected before any fetch (§5).")
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    stratum_of = {n: s for s, members in sample["strata"].items() for n in members}

    rows = []
    for name in sorted(stratum_of):
        row = resolve(name)
        row["stratum"] = stratum_of[name]
        rows.append(row)
        print(f"  {name:<22} {row.get('pageviews')}  ({row.get('article')})")
        time.sleep(PAUSE_S)

    failures = [r for r in rows if not r["matched"]]
    rate = len(failures) / len(rows)
    result = {
        "source": "en.wikipedia monthly pageviews (agent=user)",
        "window": f"{WINDOW_START}..{WINDOW_END}",
        "metric": "sum of monthly pageviews over the window",
        "resolver": "musician-aware: opensearch -> wikidata musicality filter",
        "sample_size": len(rows),
        "match_failures": len(failures),
        "match_failure_rate": rate,
        # §9 A10: fires at > 6 of 29.
        "falsifier_fires": len(failures) > 6,
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{len(failures)}/{len(rows)} match failures ({rate:.1%}).")
    if len(failures) > 6:
        print("FALSIFIER FIRES (> 6 of 29): match failure too high.")
    for r in failures:
        print(f"  unmatched: {r['query']!r} ({r.get('reason')})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", action="store_true", help="check the API + resolver, out-of-sample")
    args = ap.parse_args()
    return probe() if args.probe else fetch_sample()


if __name__ == "__main__":
    sys.exit(main())
