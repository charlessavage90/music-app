"""MBID-keyed fame resolution -- a drop-in replacement for the name-search resolver.

WHAT THIS IS
  The adopted proxy computes F = log10(1 + en.wikipedia annual pageviews),
  unmatched -> 0 (A11). This module computes THE SAME F with THE SAME window,
  changing exactly one thing: how an artist is resolved to an article.

    adopted    artist NAME -> opensearch -> candidate articles -> identity /
               performer / musicality clauses -> article
    here       artist MBID -> Wikidata P434 (which IS the MusicBrainz artist
               ID) -> sitelink -> article

  One knob. The formula, the window (2025-07..2026-06) and the floor rule are
  deliberately untouched so that any difference is attributable to resolution
  and nothing else.

WHY IT MATTERS BEYOND COVERAGE -- THE FAILURE THAT IS NOT A NULL
  Name search fails in two directions. It can MISS an artist, which shows up
  as a floor score you can see. It can also resolve to the WRONG artist and
  return a confident, plausible fame value, which shows up as nothing at all.
  The graph carries a live instance: it holds GOOSE (Belgian dance/electro,
  6849ebec-...) and NOT Goose (the US jam band, b925a474-...), so a name-keyed
  lookup for "Goose" scores a different band's readership.

  Track 2's committed fame_cache.json records the Wikidata QID its name search
  arrived at. That makes the second failure mode measurable directly, with no
  new requests: where the name-search QID and the P434 QID disagree, the old
  resolver was reading a different entity.

THE FROZEN PROBE IS NOT EDITED
  ../2026-07-24-track2-fame-proxy-wikipedia/fetch_pageviews.py stays exactly
  as committed. It is one of the frozen probes covered by the accepted Snyk
  deferral, whose reopening condition is that a probe be un-frozen and edited.
  This module supersedes it forward-only; the old figures remain readable
  against the code that produced them.

WHAT IT DOES NOT DO
  It does not change the currency, adopt anything, or fix the floor. An artist
  with no article still scores 0 -- FPC-1 measured that as almost always
  correct. It removes a resolution defect, which is a separate and smaller
  claim than the currency question, and true regardless of how that is decided.

Run from `builder/`:
    # measure what MBID keying buys, against Track 2's frozen cache (no network)
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_fame_mbid.py --validate

    # produce F for every artist in the artifact (resumable; ~33k requests)
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_fame_mbid.py --build
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request

from artistpath_builder.artifact import deserialise

from fp_common import (ADOPTED, ADOPTED_SHA, HERE, USER_AGENT, band_of,
                       fame_frame, load_partial, save_partial)

TRACK2 = HERE.parent / "2026-07-24-track2-arm-scorer"
PAGEVIEWS_OUT = HERE / "fp_fame_pageviews.json"
VALIDATE_OUT = HERE / "fp_fame_mbid_validation.json"

# Matched to the adopted proxy's asserted window. A different window would
# confound resolution with period, which is the one thing this must not do.
WINDOW = ("2025070100", "2026063000")
PV = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
      "/en.wikipedia/all-access/user/{title}/monthly/{start}/{end}")


def article_of(rec: dict | None) -> str | None:
    """Sitelink URL -> article title. None when the artist has no EN article."""
    if not rec or not rec.get("enwiki"):
        return None
    return urllib.parse.unquote(rec["enwiki"].rsplit("/", 1)[-1]).replace("_", " ")


def fame_from_views(views: int) -> float:
    """A11's formula, unchanged: F = log10(1 + annual pageviews)."""
    return math.log10(1 + views)


def fetch_views(title: str) -> int:
    url = PV.format(
        title=urllib.parse.quote(title.replace(" ", "_"), safe=""),
        start=WINDOW[0], end=WINDOW[1],
    )
    delay = 1.5
    for _ in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return sum(i["views"] for i in payload.get("items", []))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 0  # no data in window: a real zero, not a failure
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay *= 2
    return 0


def name_to_mbids() -> dict[str, list[str]]:
    payload = ADOPTED.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    graph = deserialise(payload)
    out: dict[str, list[str]] = collections.defaultdict(list)
    for mbid, name in zip(graph.mbids, graph.names):
        out[name].append(mbid)
    return out


def validate() -> None:
    """Compare against Track 2's frozen cache. No network; QIDs are committed."""
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    cache = json.loads((TRACK2 / "fame_cache.json").read_text(encoding="utf-8"))
    by_name = name_to_mbids()
    frame = fame_frame()

    agree, wrong_entity, recovered, lost, ambiguous, absent = [], [], [], [], [], []
    for name, old in cache.items():
        candidates = by_name.get(name, [])
        if not candidates:
            absent.append(name)
            continue
        if len(candidates) > 1:
            # Name non-uniqueness IS the hazard under examination, so these are
            # counted rather than resolved by a guess.
            ambiguous.append(name)
            continue
        mbid = candidates[0]
        new_article = article_of(wikidata.get(mbid))
        new_qid = (wikidata.get(mbid) or {}).get("qid")
        old_qid, old_matched = old.get("wikidata"), bool(old.get("matched"))
        row = {"name": name, "mbid": mbid, "band": band_of(frame[mbid]),
               "old_article": old.get("article"), "new_article": new_article,
               "old_qid": old_qid, "new_qid": new_qid,
               "old_pageviews": old.get("pageviews")}
        if old_matched and new_article and old_qid and new_qid and old_qid != new_qid:
            wrong_entity.append(row)
        elif old_matched and not new_article:
            lost.append(row)
        elif not old_matched and new_article:
            recovered.append(row)
        elif old_matched and new_article:
            agree.append(row)

    comparable = len(agree) + len(wrong_entity) + len(recovered) + len(lost)
    summary = {
        "population": "Track 2 fame_cache.json, resolvable to a unique artifact name",
        "cached_artists": len(cache), "comparable": comparable,
        "agree_same_entity": len(agree),
        "wrong_entity_under_name_search": len(wrong_entity),
        "recovered_by_mbid": len(recovered),
        "lost_by_mbid": len(lost),
        "name_ambiguous_in_artifact": len(ambiguous),
        "not_in_artifact": len(absent),
        "wrong_entity_rows": wrong_entity,
        "recovered_rows": sorted(recovered, key=lambda r: r["name"]),
        "lost_rows": lost,
        "ambiguous_names": sorted(ambiguous),
    }
    VALIDATE_OUT.write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print(f"Track 2 cache: {len(cache)} artists; {comparable} comparable by unique name")
    print(f"  same entity, both resolved      : {len(agree)}")
    print(f"  WRONG ENTITY under name search  : {len(wrong_entity)}")
    print(f"  recovered by MBID (was floored) : {len(recovered)}")
    print(f"  lost by MBID (was matched)      : {len(lost)}")
    print(f"  name ambiguous in artifact      : {len(ambiguous)}  (excluded)")
    print(f"  not in artifact                 : {len(absent)}  (excluded)")
    if wrong_entity:
        print("\n  name search read a DIFFERENT Wikidata entity than the MBID:")
        for r in wrong_entity[:15]:
            print(f"    {r['name'][:26]:26} old={r['old_qid']:>10} -> {r['new_qid']:>10} "
                  f"| article {str(r['old_article'])[:22]:22} -> "
                  f"{str(r['new_article'])[:22]:22} (old views {r['old_pageviews']})")
    if lost:
        print("\n  matched by name but no P434 link (MBID keying's own cost):")
        for r in lost[:10]:
            print(f"    {r['name'][:30]:30} was {str(r['old_article'])[:28]}")
    print(f"\n-> {VALIDATE_OUT.name}")


def build(pause: float) -> None:
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    frame = fame_frame()
    done = load_partial(PAGEVIEWS_OUT)
    todo = [m for m in sorted(frame) if m not in done]
    print(f"{len(done)} cached, {len(todo)} to resolve", flush=True)
    for n, mbid in enumerate(todo, 1):
        title = article_of(wikidata.get(mbid))
        done[mbid] = {"article": title,
                      "views": fetch_views(title) if title else 0}
        if title:
            time.sleep(pause)
        if n % 500 == 0:
            save_partial(PAGEVIEWS_OUT, done)
            print(f"  {n}/{len(todo)}", flush=True)
    save_partial(PAGEVIEWS_OUT, done)
    scored = {m: round(fame_from_views(v["views"]), 6) for m, v in done.items()}
    (HERE / "fp_fame_mbid.json").write_text(
        json.dumps({"formula": "A11 unchanged: F = log10(1 + en pageviews); "
                               "unresolved -> 0. Resolution by Wikidata P434.",
                    "window": WINDOW, "n": len(scored), "F": scored}),
        encoding="utf-8")
    print(f"\nwrote {len(scored)} fame values -> fp_fame_mbid.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--pause", type=float, default=0.12)
    args = ap.parse_args()
    if args.validate:
        validate()
    if args.build:
        build(args.pause)
    if not (args.validate or args.build):
        ap.error("pick --validate or --build")


if __name__ == "__main__":
    main()
