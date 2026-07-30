"""COH-1 route A: Wikidata P136 (genre) presence for the whole artifact.

WHAT THIS MEASURES
  Which artists carry at least one genre statement on Wikidata, joined
  exactly by P434 = MBID (the FPC identity finding: no name resolution, so
  no wrong-artist class). Banded against the imported fame frame, with BOTH
  denominators (GRT-P4): all artists in the band, and artists that have a
  Wikidata item at all (from the FPC collector output, fp_wikidata.json).

EXPECTATIONS, FIXED BEFORE THE RUN
  - This route is capped by construction at Wikidata item coverage itself
    (FPC-3: 36.7% of the lower-half band has an item). 36.7% < the 50% kill
    bar, so ROUTE A ALONE CANNOT PASS THE GATE in the tail -- the gate rides
    on the MusicBrainz route and the union. Stated here so nobody reads a
    low route-A tail figure as the gate outcome.
  - Prediction: P136-given-item will be high (>= 80%) in the top two bands
    and will fall with band, because genre statements are editor effort.
    Refuting condition: P136-given-item flat across bands (within 5 points),
    which would mean genre presence is a property of having an item, not of
    fame -- worth knowing, and cheaper coverage claims would follow.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_wikidata_genres.py
"""

from __future__ import annotations

import argparse
import json
import urllib.parse

from ct_common import (
    BAND_ORDER,
    FPC_WIKIDATA,
    HERE,
    USER_AGENT,
    band_of,
    fame_frame,
    graph_mbids,
    load_partial,
    post_json,
    run_batches,
)

ENDPOINT = "https://query.wikidata.org/sparql"
OUT = HERE / "ct_wikidata_genres.json"
SUMMARY = HERE / "ct_wikidata_genres_summary.json"

# Only MBIDs with >= 1 genre come back; run_batches records the rest as null,
# which is exactly the "no P136" answer. Genre count kept as a descriptive
# column, not a signal.
QUERY = """SELECT ?mbid (COUNT(DISTINCT ?genre) AS ?genres)
WHERE {
  VALUES ?mbid { %s }
  ?item wdt:P434 ?mbid .
  ?item wdt:P136 ?genre .
}
GROUP BY ?mbid"""


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
    out: dict[str, dict] = {}
    for row in payload["results"]["bindings"]:
        out[row["mbid"]["value"]] = {"genres": int(row["genres"]["value"])}
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
    done = run_batches(mbids, args.batch, done, fetch, OUT, pause=args.pause, label="p136")

    frame = fame_frame()
    items = json.loads(FPC_WIKIDATA.read_text(encoding="utf-8"))
    if len(items) != len(frame):
        raise SystemExit(
            f"fp_wikidata.json holds {len(items)} artists, frame holds {len(frame)}"
            " -- regenerate it (fame-proxy README) before reading this probe"
        )

    by_band: dict[str, dict[str, int]] = {
        b: {"artists": 0, "has_item": 0, "has_p136": 0} for b in BAND_ORDER
    }
    for mbid, pctl in frame.items():
        row = by_band[band_of(pctl)]
        row["artists"] += 1
        if items.get(mbid):
            row["has_item"] += 1
        if done.get(mbid):
            row["has_p136"] += 1

    print(f"\n{'band':>12} {'artists':>8} {'P136/all':>9} {'item/all':>9} {'P136/item':>10}")
    for b in BAND_ORDER:
        r = by_band[b]
        print(
            f"{b:>12} {r['artists']:>8} {r['has_p136'] / r['artists']:>8.1%} "
            f"{r['has_item'] / r['artists']:>8.1%} "
            f"{(r['has_p136'] / r['has_item']) if r['has_item'] else 0:>9.1%}"
        )
    SUMMARY.write_text(json.dumps(by_band, indent=1), encoding="utf-8")
    print(f"\n-> {OUT.name}, {SUMMARY.name}")


if __name__ == "__main__":
    main()
