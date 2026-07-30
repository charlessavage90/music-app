"""Step 1: join the adopted artifact to Wikidata by MBID, at full scale.

WHAT THIS REPLACES, AND WHY IT IS NOT ONLY A COVERAGE QUESTION
  The adopted proxy resolves artists by NAME SEARCH (see
  ../2026-07-24-track2-fame-proxy-wikipedia/fetch_pageviews.py). Name search
  fails in two directions: it misses artists (recorded, 31% match failure),
  and it can silently resolve to the WRONG artist and return a confident,
  bogus fame value. The graph itself carries the live instance of that class:
  it holds GOOSE (Belgian dance/electro, 6849ebec-...) and not Goose (the US
  jam band, b925a474-...), so a name-keyed lookup for "Goose" scores the wrong
  band. A missing value is a null you can see; a wrong value is not.

  Wikidata's P434 IS the MusicBrainz artist ID, so this join is exact. It
  eliminates the second failure mode entirely rather than reducing it.

DIRECTION MATTERS FOR COST
  Going MBID -> Wikidata via the MusicBrainz web service is 1 req/s, i.e.
  ~21 hours for the artifact. Querying Wikidata FOR P434 instead answers in
  batches: same join, minutes rather than a day. Nothing is fetched from
  MusicBrainz here.

WHAT IT DOES NOT ESTABLISH
  Nothing about whether Wikipedia is the right fame currency, and nothing
  about magnitude -- only which artists are reachable at all, and in how many
  languages. Sitelink COUNT is recorded as a candidate signal, not adopted as
  one.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_wikidata.py
"""

from __future__ import annotations

import argparse
import urllib.parse
from pathlib import Path

from fp_common import HERE, USER_AGENT, graph_mbids, load_partial, post_json, run_batches

ENDPOINT = "https://query.wikidata.org/sparql"
OUT = HERE / "fp_wikidata.json"

# GROUP BY (?mbid ?item) rather than ?mbid alone: an MBID mapping to two
# Wikidata items is a data error upstream, and collapsing it here would hide
# it. Duplicates are kept and counted in the summary.
QUERY = """SELECT ?mbid ?item (COUNT(DISTINCT ?sl) AS ?wikis) (SAMPLE(?en) AS ?enwiki)
WHERE {
  VALUES ?mbid { %s }
  ?item wdt:P434 ?mbid .
  OPTIONAL { ?sl schema:about ?item ; schema:isPartOf/wikibase:wikiGroup "wikipedia" . }
  OPTIONAL { ?en schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }
}
GROUP BY ?mbid ?item"""


def fetch(chunk: list[str]) -> dict[str, dict]:
    values = " ".join('"%s"' % m for m in chunk)
    body = urllib.parse.urlencode({"query": QUERY % values, "format": "json"}).encode()
    payload = post_json(
        ENDPOINT,
        body,
        {
            "User-Agent": USER_AGENT,
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        # WDQS latency is highly variable under load: the same query shape
        # measured 4.5s and 109s on adjacent batches. The ceiling is generous
        # on purpose, with backoff behind it.
        timeout=240,
    )
    out: dict[str, dict] = {}
    duplicated: set[str] = set()
    for row in payload["results"]["bindings"]:
        mbid = row["mbid"]["value"]
        record = {
            "qid": row["item"]["value"].rsplit("/", 1)[-1],
            "wikis": int(row["wikis"]["value"]),
            "enwiki": row["enwiki"]["value"] if "enwiki" in row else None,
        }
        prior = out.get(mbid)
        if prior is not None:
            # An MBID on two Wikidata items is an upstream data error. Keep the
            # richer one so coverage is not understated, and flag it so the
            # summary can count them rather than hide them.
            duplicated.add(mbid)
            if record["wikis"] <= prior["wikis"]:
                continue
        out[mbid] = record
    for mbid in duplicated:
        out[mbid]["duplicate_item"] = True
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=600)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0, help="first N artists, for a smoke run")
    args = ap.parse_args()

    mbids = graph_mbids()
    if args.limit:
        mbids = mbids[: args.limit]
    done = load_partial(OUT)
    run_batches(
        mbids, args.batch, done, fetch, OUT, pause=args.pause, label="wikidata"
    )

    hit = sum(1 for m in mbids if done.get(m))
    print(f"\nresolved {hit}/{len(mbids)} ({hit / len(mbids):.1%}) -> {OUT.name}")


if __name__ == "__main__":
    main()
