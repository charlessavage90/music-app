"""RCS §2 candidate W -- MBID-keyed EN Wikipedia pageviews over the 30-row corpus.

RESOLUTION AND WINDOW ARE THE ADOPTED PROXY'S, NOT NEW ONES
  MBID -> Wikidata P434 -> EN sitelink -> pageviews. The SPARQL is
  fp_wikidata.QUERY imported verbatim, and the pageview window, endpoint and
  retry policy are fp_fame_mbid.fetch_views / .WINDOW / .PV imported verbatim.
  Nothing about the instrument is re-derived here: if this probe's numbers
  differ from the graph-wide ones it must be because of the artists, not
  because of a second implementation drifting from the first.

NULL RULE (RCS §2)
  No P434 item -> null. P434 item with no EN sitelink -> null. An EN article
  that the pageviews API has no data for inside the window is a real ZERO, not
  a null -- fp_fame_mbid.fetch_views already draws that line at its 404 branch,
  and it is drawn the same way here so the two are comparable.

  The distinction matters for RCS's readability floor: nulls consume the floor,
  zeros do not.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/rcs_wikipedia.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
_FP = HERE.parent / "2026-07-30-fame-proxy-coverage"
if str(_FP) not in sys.path:
    sys.path.insert(0, str(_FP))

from fp_common import USER_AGENT, post_json  # noqa: E402
from fp_fame_mbid import PV, WINDOW, article_of, fame_from_views, fetch_views  # noqa: E402
from fp_wikidata import ENDPOINT, QUERY  # noqa: E402

CORPUS = HERE / "fi_corpus.json"
RAW_OUT = HERE / "rcs_wikipedia_raw.json"
VALUES_OUT = HERE / "rcs_wikipedia.json"

# 30 MBIDs is one WDQS batch. The graph-wide probe used 600.
BATCH = 30


def wdqs(mbids: list[str]) -> tuple[list[dict], dict[str, dict]]:
    """One batched SPARQL call. Returns (raw bindings, mbid -> record).

    The binding -> record collapse mirrors fp_wikidata.fetch's rule: an MBID on
    two Wikidata items is an upstream data error, so keep the richer item and
    flag it rather than silently pick one.
    """
    raw: list[dict] = []
    out: dict[str, dict] = {}
    duplicated: set[str] = set()
    for start in range(0, len(mbids), BATCH):
        chunk = mbids[start:start + BATCH]
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
            timeout=240,
        )
        bindings = payload["results"]["bindings"]
        raw.extend(bindings)
        for row in bindings:
            mbid = row["mbid"]["value"]
            record = {
                "qid": row["item"]["value"].rsplit("/", 1)[-1],
                "wikis": int(row["wikis"]["value"]),
                "enwiki": row["enwiki"]["value"] if "enwiki" in row else None,
            }
            prior = out.get(mbid)
            if prior is not None:
                duplicated.add(mbid)
                if record["wikis"] <= prior["wikis"]:
                    continue
            out[mbid] = record
        time.sleep(1.0)
    for mbid in duplicated:
        out[mbid]["duplicate_item"] = True
    return raw, out


def main() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["rows"]
    mbids = [r["mbid"] for r in corpus]

    print(f"WDQS: one batch of {len(mbids)} MBIDs against P434", flush=True)
    raw_bindings, wikidata = wdqs(mbids)
    print(f"  {len(wikidata)}/{len(mbids)} MBIDs carry a Wikidata item", flush=True)

    rows, raw_per_artist = [], {}
    for r in corpus:
        rec = wikidata.get(r["mbid"])
        title = article_of(rec)
        if title is None:
            reason = "no_wikidata_item_with_P434" if rec is None else "wikidata_item_but_no_en_article"
            value, views, url = None, None, None
        else:
            reason = None
            views = fetch_views(title)
            value = round(fame_from_views(views), 6)
            url = PV.format(
                title=urllib.parse.quote(title.replace(" ", "_"), safe=""),
                start=WINDOW[0], end=WINDOW[1],
            )
            time.sleep(1.0)
        rows.append({
            "mbid": r["mbid"], "name": r["name"], "region": r["region"],
            "hand_value": r["hand_value"],
            "article": title, "qid": (rec or {}).get("qid"),
            "wikipedias": (rec or {}).get("wikis"),
            "pageviews": views, "W": views, "F_log10": value,
            "null_reason": reason,
        })
        raw_per_artist[r["mbid"]] = {
            "name": r["name"],
            "wikidata_record": rec,
            "pageviews_request": url,
            "pageviews_window": list(WINDOW),
            "pageviews_total": views,
        }
        mark = "null" if views is None else str(views)
        print(f"  {r['region']:6} {r['name'][:34]:34} {str(title)[:34]:34} {mark}", flush=True)

    RAW_OUT.write_text(json.dumps({
        "wdqs_endpoint": ENDPOINT,
        "wdqs_query": QUERY,
        "wdqs_raw_bindings": raw_bindings,
        "pageviews_endpoint_template": PV,
        "pageviews_window": list(WINDOW),
        "pageviews_note": "totals fetched by fp_fame_mbid.fetch_views (imported, not "
                          "reimplemented); the request URL is recorded so any total is "
                          "re-checkable against the same window",
        "per_artist": raw_per_artist,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    VALUES_OUT.write_text(json.dumps({
        "candidate": "W -- MBID-keyed EN Wikipedia pageviews",
        "governing_document":
            "docs/superpowers/specs/2026-08-02-ruler-candidate-shootout-preregistration.md",
        "resolution": "MBID -> Wikidata P434 -> EN sitelink -> pageviews",
        "window": list(WINDOW),
        "null_rule": "no P434 item or no EN sitelink -> null; an article with no "
                     "pageview data in the window is a value of 0",
        "non_null": {
            region: sum(1 for x in rows if x["region"] == region and x["W"] is not None)
            for region in ("famous", "tail")
        },
        "rows": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    for region in ("famous", "tail"):
        got = sum(1 for x in rows if x["region"] == region and x["W"] is not None)
        print(f"{region}: {got}/15 non-null")
    print(f"\n-> {RAW_OUT.name}, {VALUES_OUT.name}")


if __name__ == "__main__":
    main()
