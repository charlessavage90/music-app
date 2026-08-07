"""Laura Lee closure — the evidence that settles (and does not settle) the
same-name MBID collision hypothesis.

Discharges the success condition at
  docs/superpowers/2026-08-06-cocredit-investigation-execution-log.md §6 item 1.

This is DIAGNOSIS of a single motivating case, not a probe. It carries no
pre-registration and no criteria BY DESIGN: it reads facts about two named
artists. Do not retro-fit criteria to it, and do not read n=1 as a population
result. The population question it leaves open is stated in the README.

Run from `api/` (it loads the adopted artifact through the API's GraphStore):

  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
    ../builder/analysis/2026-08-06-laura-lee-closure/ll_closure.py

The MusicBrainz half is cached into ll_closure.json; re-runs are offline unless
that file is deleted. MusicBrainz 503s freely, hence the backoff.

This directory OWNS its figures. Cite it; never restate them.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT = os.path.join(HERE, "ll_closure.json")

ARCHIVE = ("../builder/scratch/grt-archive-algb/similar/listenbrainz/"
           "session_based_days_7500_session_300_contribution_3_threshold_10_"
           "limit_100_filter_True_skip_30/")
GRAPH = "../builder/scratch/graph-msw-tu50.bin"
GRAPH_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
PAYLOADS = "../builder/src/artistpath_builder/data/"

USER_AGENT = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"
MB_SEARCH = "https://musicbrainz.org/ws/2/recording?query={q}&fmt=json&limit=12"

# The four artists this case turns on. The two Laura Lees are the whole point:
# same name, different MBIDs, and the hypothesis was that listens for one were
# landing on the other.
SUBJECTS = {
    "laura_lee_khruangbin": ("50ef58c4-a61a-4b83-9e54-ad66cd4672c7",
                             "Laura Lee (Khruangbin member, b.1986)"),
    "laura_lee_soul": ("70a65cf5-9dee-4132-8e0e-143dcf3b8dcb",
                       "Laura Lee (soul & gospel, b.1945)"),
    "leon_bridges": ("69d9dfd7-19b7-4a75-8a53-9f733fb5d774", "Leon Bridges"),
    "khruangbin": ("aea4c9b9-9f8d-49dc-b2ca-57d6f26e8634", "Khruangbin"),
}


def archived(mbid):
    p = os.path.join(ARCHIVE, mbid + ".json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def mb_recordings(mbid, tries=6):
    """Recordings on which this MBID appears in artist-credit.

    NOT 'recordings they played on' — a sideman credited only by relationship
    does not appear. That is the right measure here precisely because it is
    what a LISTEN can key to: a play of a track credited to someone else does
    not accrue to this artist.
    """
    q = urllib.parse.quote("arid:" + mbid)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(MB_SEARCH.format(q=q),
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=40) as fh:
                d = json.load(fh)
            titles = [{"title": r["title"],
                       "credit": " / ".join(c["artist"]["name"]
                                            for c in r.get("artist-credit", []))}
                      for r in d.get("recordings", [])]
            return {"count": d["count"], "sample": titles}
        except Exception as exc:  # noqa: BLE001 - any failure is a retry here
            print("   mb retry %d for %s: %s" % (attempt + 1, mbid[:8], exc))
            time.sleep(3 * (attempt + 1))
    return None


def list_position(lst, mbid):
    """1-based rank of mbid in a similar-list, or None."""
    for i, row in enumerate(lst):
        if row["artist_mbid"] == mbid:
            return {"rank": i + 1, "score": row["score"]}
    return None


def main():
    cached = {}
    if os.path.exists(RESULT):
        cached = json.load(open(RESULT, encoding="utf-8")).get("musicbrainz", {})

    out = {
        "what": "Laura Lee closure - diagnosis of one case, not a probe",
        "governing": ("docs/superpowers/2026-08-06-cocredit-investigation-"
                      "execution-log.md section 6 item 1"),
        "graph": {"path": GRAPH, "expected_sha256": GRAPH_SHA},
        "archive": ARCHIVE,
        "subjects": {},
        "musicbrainz": {},
        "cross_lists": {},
        "drop_payloads": {},
    }

    # --- archive: each subject's own similar-list -------------------------
    lists = {}
    for key, (mbid, label) in SUBJECTS.items():
        lst = archived(mbid)
        lists[key] = lst
        if lst is None:
            out["subjects"][key] = {"mbid": mbid, "label": label,
                                    "archived": False}
            continue
        scores = [r["score"] for r in lst]
        out["subjects"][key] = {
            "mbid": mbid, "label": label, "archived": True,
            "list_length": len(lst),
            "top_score": scores[0],
            "median_score": scores[len(scores) // 2],
            "min_score": scores[-1],
            "top10": [{"rank": i + 1, "name": r["name"], "score": r["score"],
                       "mbid": r["artist_mbid"]} for i, r in enumerate(lst[:10])],
        }

    # --- who appears on whose list, and where -----------------------------
    # This is the direction that matters: the owner met Laura Lee by looking
    # at LEON BRIDGES, so his list is the user-facing one.
    for a in SUBJECTS:
        for b in SUBJECTS:
            if a == b or lists.get(a) is None:
                continue
            pos = list_position(lists[a], SUBJECTS[b][0])
            out["cross_lists"]["%s__on__%s" % (b, a)] = pos

    # --- MusicBrainz catalogue size ---------------------------------------
    for key, (mbid, _label) in SUBJECTS.items():
        if key in cached and cached[key]:
            out["musicbrainz"][key] = cached[key]
            print("cached  %s" % key)
            continue
        print("fetch   %s" % key)
        out["musicbrainz"][key] = mb_recordings(mbid)
        time.sleep(2)

    # --- drop payload membership ------------------------------------------
    for name in ("unlistenable_drop_algb_20260805",
                 "no_release_drop_algb_20260802"):
        with open(os.path.join(PAYLOADS, name + ".json"), encoding="utf-8") as fh:
            payload = json.load(fh)
        row = {}
        for key, (mbid, _l) in SUBJECTS.items():
            found = []
            for field, val in payload.items():
                if isinstance(val, list) and mbid in val:
                    found.append(field)
                elif isinstance(val, dict) and mbid in val:
                    found.append(field)
            row[key] = found
        out["drop_payloads"][name] = row

    # --- adopted graph presence -------------------------------------------
    try:
        from artistpath_api.graph_store import GraphStore
        g = GraphStore.load(GRAPH)
        out["graph"]["artist_count"] = int(g.artist_count)
        pres = {}
        for key, (mbid, _l) in SUBJECTS.items():
            idx = g.id_by_mbid.get(mbid)
            pres[key] = ({"present": False} if idx is None else
                         {"present": True,
                          "degree": len(list(g.neighbours_of(idx))),
                          "pop_raw": round(float(g.pop_raw[idx]), 4)})
        out["graph"]["presence"] = pres
    except Exception as exc:  # noqa: BLE001
        out["graph"]["error"] = repr(exc)

    with open(RESULT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    # --- summary ----------------------------------------------------------
    print("\n=== catalogue size (recordings credited to the MBID) ===")
    for key, (_m, label) in SUBJECTS.items():
        mb = out["musicbrainz"].get(key)
        print("  %-40s %s" % (label, mb["count"] if mb else "FETCH FAILED"))
    print("\n=== Laura Lee (Khruangbin) on Leon Bridges' list ===")
    print("  ", out["cross_lists"].get("laura_lee_khruangbin__on__leon_bridges"))
    print("=== ... on Khruangbin's list ===")
    print("  ", out["cross_lists"].get("laura_lee_khruangbin__on__khruangbin"))
    print("\n=== adopted graph presence ===")
    for key, val in out["graph"].get("presence", {}).items():
        print("  %-24s %s" % (key, val))
    print("\nwrote", RESULT)


if __name__ == "__main__":
    main()
