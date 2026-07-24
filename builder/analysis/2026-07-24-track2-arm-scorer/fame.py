"""Fame resolution for the Stage A scorer, under amendment A11's encoding.

**The resolver is imported, not reimplemented.** A11 names
`../2026-07-24-track2-fame-proxy-wikipedia/fetch_pageviews.py` canonical for the
name -> article rules, and it took two corrections to get right (the bare-top-hit rule
fails acts named after places; musicality-alone accepts fuzzy garbage). A second copy
would drift from the one the proxy was validated with, and the validation would no
longer describe the thing doing the scoring.

**A11's encoding.**

    F(a) = log10(1 + english wikipedia annual pageviews)      matched
    F(a) = 0                                                   unmatched -- the fame floor

An unmatched artist is *reach*, not indeterminate. That is the owner's adopted decision,
resting on absence having predicted "never heard of" 9/9 on the labelled sample.

**The guard that makes it safe (A11, partly discharging analyst D4).** The one way
"absence = obscure" breaks is a foreign-language or historically-notable artist the owner
would know but who has no English article. So an unmatched interior that is *potentially
notable* is flagged for a one-glance owner check before it counts as maximal reach. Two
independent signals, both cheap:

  - `non_latin_name`  -- the name carries non-Latin script (local, no network)
  - `foreign_article` -- a Wikidata entity satisfying the same identity + performer +
                         musical clauses exists and has a sitelink to a NON-English
                         Wikipedia

The second is the load-bearing one and is why this module talks to Wikidata separately:
the canonical resolver walks *English* opensearch, so when English has no article it
never sees the entity at all, and the very case the guard exists for is invisible to it.

Cached to disk by artist name. Re-runs cost nothing, which matters because the scorer is
re-run whenever a criterion changes and the network half must not be repeated.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"
sys.path.insert(0, str(PROXY))

from fetch_pageviews import (  # noqa: E402
    PAUSE_S,
    TIMEOUT_S,
    UA,
    WIKIDATA,
    is_musical,
    is_performer,
    name_matches,
    resolve,
)

CACHE = HERE / "fame_cache.json"
FAME_FLOOR = 0.0

# Languages whose label index we search when English has no article. Chosen to cover the
# strata §5 stressed (regional/off-platform fame) without an unbounded fan-out.
SEARCH_LANGS = ("en", "ja", "ko", "zh", "de", "fr", "es", "pt", "ru")


def fame(row: dict) -> float:
    """A11's fame scale. Unmatched -> the floor, which is 0 and below every matched act."""
    if not row.get("matched"):
        return FAME_FLOOR
    return math.log10(1.0 + int(row["pageviews"]))


def has_non_latin(name: str) -> bool:
    """True if any letter in the name is outside the Latin script.

    Deliberately letters-only: punctuation and digits say nothing about the artist's
    likely constituency, and 'saib.' should not be flagged for its full stop.
    """
    for ch in name:
        if not ch.isalpha():
            continue
        if "LATIN" not in unicodedata.name(ch, ""):
            return True
    return False


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as fh:  # noqa: S310 - fixed hosts
        return json.loads(fh.read().decode("utf-8"))


def _wikidata_search(name: str, lang: str) -> list[str]:
    q = urllib.parse.urlencode({
        "action": "wbsearchentities", "search": name, "language": lang,
        "uselang": lang, "type": "item", "limit": 5, "format": "json",
    })
    try:
        data = _get_json(f"{WIKIDATA}?{q}")
    except Exception:
        return []
    return [h["id"] for h in data.get("search", []) if h.get("id")]


def _entity_with_sitelinks(qid: str) -> dict:
    q = urllib.parse.urlencode({
        "action": "wbgetentities", "ids": qid,
        "props": "labels|aliases|claims|sitelinks", "format": "json",
    })
    try:
        data = _get_json(f"{WIKIDATA}?{q}")
    except Exception:
        return {}
    return data.get("entities", {}).get(qid, {})


def _wikidata_musical_matches(name: str):
    """Yield (qid, entity) for Wikidata entities matching name+performer+musical.

    The SAME three clauses the canonical resolver applies, so a hit means exactly what an
    English-opensearch match would have meant. The only thing that differs is the index
    searched: Wikidata's label/alias index instead of English opensearch's top-5 article
    titles. That difference is the whole point -- it is what finds an act whose bare name
    is a common word (Justice -> 'Justice (band)'), which opensearch buries.
    """
    seen: set[str] = set()
    for lang in SEARCH_LANGS:
        for qid in _wikidata_search(name, lang):
            if qid in seen:
                continue
            seen.add(qid)
            time.sleep(PAUSE_S)
            ent = _entity_with_sitelinks(qid)
            if not ent:
                continue
            claims = ent.get("claims", {})
            if name_matches(name, ent) and is_performer(claims) and is_musical(claims):
                yield qid, ent


def english_article_fallback(name: str) -> dict:
    """When English opensearch misses, does an English article exist after all?

    A RECALL fix, not a match-criteria change. It accepts nothing the canonical resolver
    would reject -- identity, performer, and musical must all still hold -- but it reaches
    the entity via Wikidata's label index instead of opensearch's top-5, so it recovers
    famous acts with ambiguous short names (Justice, Rainbow, Ye) that opensearch buries
    under the bare common word. Verified in `verify_resolver_equivalence.py` to leave the
    §5 validation sample's matched/unmatched split byte-identical: it only ever ADDS a
    match the validated resolver missed, never changes one it made.
    """
    for _qid, ent in _wikidata_musical_matches(name):
        en = ent.get("sitelinks", {}).get("enwiki")
        if en and en.get("title"):
            from fetch_pageviews import pageviews_sum  # canonical, imported not copied
            views, months = pageviews_sum(en["title"])
            return {"found": True, "article": en["title"], "wikidata": _qid,
                    "pageviews": views, "months_present": months}
    return {"found": False}


def foreign_article(name: str) -> dict:
    """Does a NON-English Wikipedia carry an article for this musical act?

    Runs only after `english_article_fallback` has already failed, so by here the act has
    no English article by either route. Same three clauses. This is the A11 guard's
    load-bearing signal: an unmatched act that a foreign Wikipedia knows is 'potentially
    notable' and needs the owner's glance before it counts as reach.
    """
    for qid, ent in _wikidata_musical_matches(name):
        wikis = [s for s in ent.get("sitelinks", {}) if s.endswith("wiki")]
        non_en = sorted(w for w in wikis if w != "enwiki")
        if non_en:
            return {"found": True, "wikidata": qid, "non_english_wikis": non_en[:8],
                    "n_non_english": len(non_en)}
    return {"found": False}


def load_cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def save_cache(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True),
                     encoding="utf-8")


def resolve_all(names: list[str], cache: dict, verbose: bool = True) -> dict:
    """Resolve every name, using and extending the on-disk cache.

    Saves after each new resolution: a few hundred artists at ~1s each is long enough
    that an interrupted run must not lose the work already paid for.
    """
    todo = [n for n in names if n not in cache]
    if verbose and todo:
        print(f"resolving {len(todo)} uncached name(s) of {len(names)}")
    for i, name in enumerate(todo, 1):
        row = resolve(name)
        if not row.get("matched"):
            # RECALL fallback first: an English article opensearch's top-5 missed.
            # A recovered match is a real match and is scored, not floored.
            fb = english_article_fallback(name)
            if fb["found"]:
                row.update(matched=True, article=fb["article"], wikidata=fb["wikidata"],
                           pageviews=fb["pageviews"], months_present=fb["months_present"],
                           via="wikidata_fallback")
            else:
                # Genuinely no English article: guard it (the expensive half runs only here).
                row["guard"] = {
                    "non_latin_name": has_non_latin(name),
                    "foreign": foreign_article(name),
                }
                row["guard"]["potentially_notable"] = bool(
                    row["guard"]["non_latin_name"] or row["guard"]["foreign"]["found"]
                )
        row["F"] = fame(row)
        cache[name] = row
        save_cache(cache)
        if verbose:
            mark = "ok " if row.get("matched") else ("FLAG" if row["guard"]["potentially_notable"] else "----")
            print(f"  [{i:>3}/{len(todo)}] {mark} {name}  F={row['F']:.3f}")
        time.sleep(PAUSE_S)
    return cache


def names_from_paths(paths_doc: dict) -> list[str]:
    """Every distinct artist name across all arms, pairs and snapshots.

    Interiors AND endpoints. Endpoints are never scored by C1-C4 (§2.1 -- the scorer uses
    interiors only), but the A14 endpoint-tracking diagnostic (WGLL value 9) needs their
    fame, and resolving ~16 extra famous names is nearly free. Including them in the fame
    table cannot leak into a scored statistic, because every scoring path slices path[1:-1].
    """
    names = paths_doc["node_names"]
    out: set[str] = set()
    for by_pair in paths_doc["paths"].values():
        for by_depth in by_pair.values():
            for path in by_depth.values():
                if path:
                    out.update(names[str(n)] for n in path)  # includes endpoints
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", default=str(HERE / "paths.json"))
    ap.add_argument("--out", default=str(HERE / "fame.json"))
    ap.add_argument("--names", nargs="*", help="resolve these names instead (for testing)")
    args = ap.parse_args()

    if args.names:
        names = list(args.names)
    else:
        doc = json.loads(Path(args.paths).read_text(encoding="utf-8"))
        names = names_from_paths(doc)
        print(f"{len(names)} distinct interior artists across all arms/pairs/snapshots")

    cache = resolve_all(names, load_cache())

    rows = {n: cache[n] for n in names}
    matched = sum(1 for r in rows.values() if r.get("matched"))
    flagged = [n for n, r in rows.items()
               if not r.get("matched") and r["guard"]["potentially_notable"]]

    out = {
        "encoding": "A11: F = log10(1 + en.wikipedia annual pageviews); unmatched -> 0",
        "n": len(rows), "matched": matched, "unmatched": len(rows) - matched,
        "coverage": matched / len(rows) if rows else 0.0,
        "potentially_notable_unmatched": sorted(flagged),
        "fame": {n: r["F"] for n, r in rows.items()},
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"\nmatched {matched}/{len(rows)} = {out['coverage']*100:.1f} %  (reported, "
          f"NOT gated — amendment A12)")
    if flagged:
        print(f"\nA11 guard — unmatched but potentially notable ({len(flagged)}):")
        for n in flagged:
            g = rows[n]["guard"]
            why = []
            if g["non_latin_name"]:
                why.append("non-Latin name")
            if g["foreign"]["found"]:
                why.append(f"{g['foreign']['n_non_english']} non-English article(s)")
            print(f"  - {n}  ({'; '.join(why)})")
        print("  -> these need the owner's one-glance check before counting as reach.")
    else:
        print("\nA11 guard: no unmatched interior looks potentially notable.")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
