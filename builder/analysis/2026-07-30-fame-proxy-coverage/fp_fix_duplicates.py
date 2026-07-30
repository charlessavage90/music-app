"""Repair pass: MBIDs claimed by more than one Wikidata item.

THE DEFECT THIS FIXES IS MINE, AND IT WAS CAUGHT BY VALIDATION
  fp_wikidata.py's fetch() broke ties between two items claiming the same
  P434 by keeping the one with MORE sitelinks. That is not a correctness
  signal, and on at least one case it is actively wrong: MBID
  75167b8b-... is Neil Young, and it is claimed both by Q633 (Neil Young) and
  by Q25820 (Thomas Young, the physicist -- an erroneous claim upstream).
  Thomas Young carries more language Wikipedias, so the tie-break chose the
  physicist and would have scored his readership as Neil Young's fame.

  Exactly the silent-error class this directory exists to complain about,
  reproduced by the instrument built to remove it. Caught by
  fp_fame_mbid.py --validate flagging a QID disagreement, not by review.

THE REPLACEMENT RULE
  Prefer the item carrying a MUSIC signal -- an occupation (P106) that is a
  musical one, an instance-of (P31) that is a musical group, a genre (P136),
  a record label (P264), or any of the common music-service identifiers.
  Sitelink count is not used to decide anything.

  When BOTH or NEITHER candidate carries a music signal, the MBID is recorded
  as UNRESOLVED rather than guessed. A refused answer is auditable; a guess
  that happens to be wrong is the thing being fixed.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_fix_duplicates.py
"""

from __future__ import annotations

import json
import urllib.parse

from fp_common import HERE, USER_AGENT, post_json

OUT = HERE / "fp_wikidata.json"
REPORT = HERE / "fp_fix_duplicates.json"

# One row per (mbid, item) with a boolean music signal and the EN sitelink, so
# the chooser never has to consult sitelink counts again.
QUERY = """SELECT ?mbid ?item (SAMPLE(?en) AS ?enwiki)
       (COUNT(DISTINCT ?sl) AS ?wikis) (COUNT(DISTINCT ?sig) AS ?music)
WHERE {
  VALUES ?mbid { %s }
  ?item wdt:P434 ?mbid .
  OPTIONAL { ?sl schema:about ?item ; schema:isPartOf/wikibase:wikiGroup "wikipedia" . }
  OPTIONAL { ?en schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }
  OPTIONAL {
    ?item ?sigp ?sig .
    VALUES ?sigp { wdt:P136 wdt:P264 wdt:P1902 wdt:P1953 wdt:P1728 wdt:P412 }
  }
}
GROUP BY ?mbid ?item"""

MUSIC_OCCUPATION = """ASK { VALUES ?item { wd:%s }
  { ?item wdt:P106/wdt:P279* wd:Q639669 } UNION
  { ?item wdt:P106 ?occ . VALUES ?occ { wd:Q177220 wd:Q36834 wd:Q486748
        wd:Q855091 wd:Q158852 wd:Q1259917 wd:Q130857 } } UNION
  { ?item wdt:P31/wdt:P279* wd:Q2088357 } UNION
  { ?item wdt:P31/wdt:P279* wd:Q215380 } }"""


def sparql(query: str) -> dict:
    return post_json(
        "https://query.wikidata.org/sparql",
        urllib.parse.urlencode({"query": query, "format": "json"}).encode(),
        {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json",
         "Content-Type": "application/x-www-form-urlencoded"},
        timeout=240,
    )


def main() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    dupes = sorted(m for m, v in data.items() if v and v.get("duplicate_item"))
    print(f"{len(dupes)} MBIDs claimed by more than one Wikidata item")
    if not dupes:
        return

    rows = sparql(QUERY % " ".join('"%s"' % m for m in dupes))["results"]["bindings"]
    by_mbid: dict[str, list[dict]] = {}
    for r in rows:
        by_mbid.setdefault(r["mbid"]["value"], []).append({
            "qid": r["item"]["value"].rsplit("/", 1)[-1],
            "enwiki": r["enwiki"]["value"] if "enwiki" in r else None,
            "wikis": int(r["wikis"]["value"]),
            "music": int(r["music"]["value"]) > 0,
        })

    # Second signal, per item, for the ones the property test left tied.
    for mbid, cands in by_mbid.items():
        if sum(1 for c in cands if c["music"]) != 1:
            for c in cands:
                c["music"] = c["music"] or bool(
                    sparql(MUSIC_OCCUPATION % c["qid"])["boolean"])

    changed, refused, kept = [], [], 0
    for mbid, cands in by_mbid.items():
        musical = [c for c in cands if c["music"]]
        before = data[mbid]["qid"]
        if len(musical) == 1:
            pick = musical[0]
            data[mbid] = {"qid": pick["qid"], "wikis": pick["wikis"],
                          "enwiki": pick["enwiki"], "duplicate_item": True,
                          "resolved_by": "music-signal"}
            if pick["qid"] != before:
                changed.append({"mbid": mbid, "from": before, "to": pick["qid"]})
            else:
                kept += 1
        else:
            # Refuse rather than guess: recorded unresolved, scored at the floor.
            data[mbid] = {"qid": None, "wikis": 0, "enwiki": None,
                          "duplicate_item": True, "resolved_by": "REFUSED-ambiguous",
                          "candidates": [c["qid"] for c in cands]}
            refused.append({"mbid": mbid, "candidates": [c["qid"] for c in cands]})

    OUT.write_text(json.dumps(data), encoding="utf-8")
    REPORT.write_text(json.dumps(
        {"duplicates": len(dupes), "corrected": changed,
         "already_correct": kept, "refused": refused}, indent=1), encoding="utf-8")

    print(f"  corrected (tie-break had picked the non-music item): {len(changed)}")
    for c in changed[:12]:
        print(f"    {c['mbid'][:8]}  {c['from']} -> {c['to']}")
    print(f"  already correct: {kept}")
    print(f"  REFUSED as ambiguous (scored at the floor): {len(refused)}")
    print(f"\n-> {OUT.name} rewritten; report in {REPORT.name}")


if __name__ == "__main__":
    main()
