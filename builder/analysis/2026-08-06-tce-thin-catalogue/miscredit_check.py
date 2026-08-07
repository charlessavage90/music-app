"""The same-name mis-filing `TCE-G1` surfaced, recorded reproducibly.

MusicBrainz files the RECORDING of "Not Up for Discussion" under one Laura Lee
and the RELEASE-GROUP of the same name under the OTHER Laura Lee. This script
demonstrates that inconsistency from the live API so the claim in this
directory's README rests on a re-runnable check rather than on prose.

Why it is here and not in the Laura Lee closure: the closure ruled the
same-name COLLISION dead for Laura Lee at the level it examined (ListenBrainz
resolving listens to MBIDs). This is a different level -- MusicBrainz's own
artist credits -- and it is why TCE-G1 cell 1 passed. See
docs/superpowers/2026-08-06-cocredit-investigation-execution-log.md section 6
item 1, whose POPULATION half the closure left explicitly OPEN.

  n = 1. This licenses no rate, in either direction, and it is NOT evidence for
  the thin-catalogue mechanism.

Run from anywhere:
  PYTHONIOENCODING=utf-8 python -u miscredit_check.py
"""
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "miscredit.json")
UA = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"

LL_KHRUANGBIN = "50ef58c4-a61a-4b83-9e54-ad66cd4672c7"
LL_SOUL = "70a65cf5-9dee-4132-8e0e-143dcf3b8dcb"
TITLE = "Not Up for Discussion"


def get(url, tries=6):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as fh:
                return json.load(fh)
        except Exception as exc:  # noqa: BLE001
            print("  retry %d: %s" % (attempt + 1, exc))
            time.sleep(3 * (attempt + 1))
    return None


def credits(entity, query):
    d = get("https://musicbrainz.org/ws/2/%s?query=%s&fmt=json&limit=5"
            % (entity, urllib.parse.quote(query)))
    rows = []
    for r in (d or {}).get(entity + "s", []):
        if r["title"] != TITLE:
            continue
        rows.append({
            "title": r["title"],
            "credited": [{"name": c["artist"]["name"],
                          "mbid": c["artist"]["id"],
                          "disambiguation": c["artist"].get("disambiguation", "")}
                         for c in r.get("artist-credit", [])],
        })
    return rows


def main():
    out = {
        "what": "same-name mis-filing between the two Laura Lees, MB's own credits",
        "n": 1,
        "licenses_no_rate": True,
        "bears_on": ("docs/superpowers/2026-08-06-cocredit-investigation-"
                     "execution-log.md section 6 item 1 (population half, OPEN)"),
        "not_evidence_for": "the thin-catalogue mechanism (TCE-)",
    }
    print("recording credited to the Khruangbin Laura Lee:")
    out["recording_by_khruangbin_laura_lee"] = credits(
        "recording", "arid:%s AND recording:\"%s\"" % (LL_KHRUANGBIN, TITLE))
    print(json.dumps(out["recording_by_khruangbin_laura_lee"], indent=1))
    time.sleep(2)

    print("release-group credited to the soul Laura Lee:")
    out["release_group_by_soul_laura_lee"] = credits(
        "release-group", "arid:%s AND releasegroup:\"%s\"" % (LL_SOUL, TITLE))
    print(json.dumps(out["release_group_by_soul_laura_lee"], indent=1))

    rec = {c["mbid"] for r in out["recording_by_khruangbin_laura_lee"]
           for c in r["credited"]}
    rg = {c["mbid"] for r in out["release_group_by_soul_laura_lee"]
          for c in r["credited"]}
    out["inconsistent"] = bool(rec and rg and (LL_KHRUANGBIN in rec)
                               and (LL_SOUL in rg))
    out["consequence_for_TCE_G1"] = (
        "TCE-G1 cell 1 required the Khruangbin Laura Lee to hold 0 credited "
        "release-groups and she does. Had this release-group been filed under "
        "her rather than under the soul singer, her count would be >= 1 and "
        "that cell would have FAILED instead. The instrument is sound; the "
        "ground truth the gate was checked against is contaminated.")

    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\ninconsistent across levels:", out["inconsistent"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
