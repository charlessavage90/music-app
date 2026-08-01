"""Wikidata P136 genre LABELS for the whole artifact — the union's second half.

WHY THIS EXISTS AT ALL, AND WHY IT IS NOT ct_wikidata_genres.py
  COH-1 asked whether an artist carries *any* genre statement, so its query is
  `SELECT ?mbid (COUNT(DISTINCT ?genre) AS ?genres)` and its output stores
  counts: {"genres": 10}. Correct for a coverage question, useless for a
  Jaccard: TAS needs to know *which* genres, not how many.

  So the labels were never persisted and are not recoverable from the COH-
  output. This collector fetches them. ct_wikidata_genres.py is left FROZEN
  and untouched -- editing a committed probe script to serve a later question
  is how a record stops reproducing what it claims to have measured.

WHY P136 IS WORTH AN EXTRA COLLECTION RATHER THAN DROPPING IT
  COH-2 measured the lower-half band at 24.0% for MusicBrainz genres alone
  and 35.3% for the union -- P136 contributes ~11 points there. The naive
  objection is that the tail is where the device is silent anyway, so the
  extra labels buy nothing. That is wrong in the case that matters:
  agreement needs labels at BOTH ends, and the pairs a binding (famous,
  long-listed) artist has to choose between include obscure candidates.
  P136 labels on those candidates are exactly what makes a famous->obscure
  pair resolvable rather than neutral -- the population TAS-6 guards.

Run from `builder/` (batched, resumable, minutes to an hour depending on
WDQS load):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_wikidata.py
"""

from __future__ import annotations

import argparse
import time
import urllib.parse
from typing import Any

from tas_common import HERE, graph_mbids, load_partial, save_partial

import sys

_FPC = HERE.parent / "2026-07-30-fame-proxy-coverage"
if str(_FPC) not in sys.path:
    sys.path.insert(0, str(_FPC))
from fp_common import USER_AGENT, post_json  # noqa: E402

ENDPOINT = "https://query.wikidata.org/sparql"
OUT_RAW = HERE / "tas_wikidata_raw.json"

# rdfs:label with an explicit English filter rather than the label service:
# the service is unreliable inside large VALUES batches, and an artist whose
# genre has no English label is genuinely unusable for a shared-vocabulary
# Jaccard anyway.
QUERY = """SELECT ?mbid ?genreLabel
WHERE {
  VALUES ?mbid { %s }
  ?item wdt:P434 ?mbid .
  ?item wdt:P136 ?genre .
  ?genre rdfs:label ?genreLabel .
  FILTER(LANG(?genreLabel) = "en")
}"""


def parse_label_rows(payload: Any) -> dict[str, dict]:
    """Group SPARQL rows into {mbid: {"genres": [labels]}}.

    Sorted and deduplicated so the stored frame is deterministic: WDQS row
    order is not stable between runs, and an unsorted list would make the
    raw file churn without the data changing.
    """
    grouped: dict[str, set[str]] = {}
    for row in payload["results"]["bindings"]:
        grouped.setdefault(row["mbid"]["value"], set()).add(row["genreLabel"]["value"])
    return {mbid: {"genres": sorted(labels)} for mbid, labels in grouped.items()}


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
        # WDQS latency is highly variable under load (fp_wikidata measured
        # 4.5s and 109s on adjacent batches of the same shape).
        timeout=240,
    )
    return parse_label_rows(payload)


def main() -> None:
    ap = argparse.ArgumentParser()
    # Smaller than COH-1's 600: this query returns one row per (artist, genre)
    # instead of one per artist, so the result set is several times larger for
    # the same batch.
    ap.add_argument("--batch", type=int, default=250)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=0, help="first N artists, for a smoke run")
    args = ap.parse_args()

    mbids = graph_mbids()
    if args.limit:
        mbids = mbids[: args.limit]
    done: dict[str, Any] = load_partial(OUT_RAW)
    pending = [m for m in mbids if m not in done]
    print(f"{len(done)} already done, {len(pending)} to fetch", flush=True)

    for start in range(0, len(pending), args.batch):
        chunk = pending[start : start + args.batch]
        got = fetch(chunk)
        for mbid in chunk:
            # Absent from the result = no P136 statement. Recorded as an
            # explicit empty answer so a resume does not re-fetch it.
            done[mbid] = got.get(mbid, {"genres": []})
        save_partial(OUT_RAW, done)
        seen = min(start + args.batch, len(pending))
        print(f"  wikidata {seen}/{len(pending)}", flush=True)
        time.sleep(args.pause)

    with_genres = sum(1 for v in done.values() if v and v.get("genres"))
    print(f"{with_genres}/{len(done)} carry >=1 English-labelled P136 genre")


if __name__ == "__main__":
    main()
