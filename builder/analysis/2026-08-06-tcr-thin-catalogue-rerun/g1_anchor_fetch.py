"""`TCR-G1` anchor fetch -- live MusicBrainz counts, fetched BEFORE any band was set.

The `TCE-` probe voided because its instrument-validation gate carried a
threshold guessed from a *recording* count. The owner ruled the re-run's gate
thresholds be anchored on externally measured values. This script IS that
anchoring step, and the order is the point:

  1. candidate validation artists chosen for unambiguous catalogues
     (no known same-name collisions);
  2. THIS SCRIPT fetches their release-group counts from the live
     MusicBrainz API and records them in g1_anchors.json;
  3. the pre-registration sets tight bands around those counts, with a
     stated tolerance for drift between live MB and the 2026-07-29 dump;
  4. the pre-registration (with this script and its output) is committed;
  5. only then does the dump counter run against these artists.

The dump counter counts release-groups on which an artist appears in
`artist-credit`. The live equivalent is the release-group browse endpoint
(`release-group?artist=MBID`), which returns release-groups directly linked
to the artist's credit -- the same semantics the void run's independent check
used when it found exact agreement (16 and 37;
`../2026-08-06-tce-thin-catalogue/README.md` section 2).

Unambiguity check: an artist-name search, recording every returned artist
whose name matches exactly (case-insensitive). One exact match = no known
same-name collision. Both Laura Lees fail this by construction, which is why
they are demoted to reported run state in the re-run.

Run from anywhere:
  PYTHONIOENCODING=utf-8 python -u g1_anchor_fetch.py
"""
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "g1_anchors.json")
UA = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"

# Candidates. `expect_thin` marks the zero-detection candidates; the
# pre-registration picks its four gate cells from what this fetch returns.
CANDIDATES = [
    {"key": "andrew_vanwyngarden", "name": "Andrew VanWyngarden", "expect_thin": True},
    {"key": "alana_haim", "name": "Alana Haim", "expect_thin": True},
    {"key": "leon_bridges", "name": "Leon Bridges", "expect_thin": False},
    {"key": "khruangbin", "name": "Khruangbin", "expect_thin": False},
    {"key": "radiohead", "name": "Radiohead", "expect_thin": False},
]


def get(url, tries=6):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as fh:
                return json.load(fh)
        except Exception as exc:  # noqa: BLE001
            print("  retry %d: %s" % (attempt + 1, exc))
            time.sleep(3 * (attempt + 1))
    raise SystemExit("live MusicBrainz unreachable; no anchor may be guessed instead")


def search_exact(name):
    d = get("https://musicbrainz.org/ws/2/artist?query=artist:%s&fmt=json&limit=25"
            % urllib.parse.quote('"%s"' % name))
    exact = [{"mbid": a["id"], "name": a["name"],
              "disambiguation": a.get("disambiguation", ""),
              "score": a.get("score")}
             for a in d.get("artists", [])
             if a["name"].casefold() == name.casefold()]
    return exact, d.get("count")


def rg_count(mbid):
    d = get("https://musicbrainz.org/ws/2/release-group?artist=%s&limit=1&fmt=json"
            % mbid)
    return d["release-group-count"]


def main():
    out = {
        "what": ("live MusicBrainz release-group counts for TCR-G1 anchor "
                 "candidates, fetched BEFORE any gate band was set and BEFORE "
                 "the dump counter ran against any of them"),
        "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "endpoint_semantics": ("release-group browse by artist = release-groups "
                               "on whose artist-credit the artist appears; same "
                               "as the dump counter"),
        "candidates": {},
    }
    for c in CANDIDATES:
        print("== %s" % c["name"])
        exact, total = search_exact(c["name"])
        time.sleep(1.2)
        row = {"name": c["name"], "expect_thin": c["expect_thin"],
               "search_result_count": total,
               "exact_name_matches": exact,
               "unambiguous": len(exact) == 1}
        if len(exact) == 1:
            row["mbid"] = exact[0]["mbid"]
            row["live_release_group_count"] = rg_count(row["mbid"])
            time.sleep(1.2)
            print("   unambiguous, mbid %s, live release-groups %d"
                  % (row["mbid"], row["live_release_group_count"]))
        else:
            print("   NOT unambiguous: %d exact-name matches -- unusable as a "
                  "gate anchor" % len(exact))
        out["candidates"][c["key"]] = row

    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
