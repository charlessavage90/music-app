"""RCS-AM1 execution: recording-title corroboration for the five blocked rows.

Committed AFTER the amendment (prereg §6) and run per its fixed procedure. The
five-row list is closed; no third widening exists. No CLI arguments.

For each row: browse MusicBrainz recordings (the truth side that exists for
recordings-only artists); Deezer candidates are the exact-normalised-name
matches already in the retained search responses (no new search); fetch each
candidate's top and album track titles; accept iff >= 1 exact normalised
recording-title match. Multiple matching candidates -> most matches; tie ->
ambiguous, reject. No match -> null stays, final.

Then the AM1 tail re-read: RCS-2's unchanged bar (Spearman >= 0.70) and floor
(>= 12 non-null), reported beside the as-committed result, never replacing it.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

import numpy as np

from fi_stats import spearman

HERE = Path(__file__).resolve().parent
UA = "artistpath-analysis/1.0 (charlessavagemiller@gmail.com)"
BLOCKED = ["Muelas de Gallo", "Jess Okoro", "Acer", "DTX", "Dorona Alberti"]
OUT = HERE / "rcs_am1.json"


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as fh:
        data = json.loads(fh.read().decode("utf-8"))
    time.sleep(1.1)
    return data


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).casefold()
    return re.sub(r"[^0-9a-zÀ-ɏ぀-ヿ一-鿿]+", "", s)


def mb_recording_titles(mbid: str) -> list[str]:
    titles, offset = [], 0
    while True:
        d = get(f"https://musicbrainz.org/ws/2/recording?artist={mbid}"
                f"&limit=100&offset={offset}&fmt=json")
        recs = d.get("recordings", [])
        titles += [r["title"] for r in recs]
        offset += len(recs)
        if offset >= d.get("recording-count", 0) or not recs:
            return titles


def deezer_candidate_tracks(artist_id: int) -> list[str]:
    titles = [t["title"] for t in get(
        f"https://api.deezer.com/artist/{artist_id}/top?limit=50").get("data", [])]
    for alb in get(f"https://api.deezer.com/artist/{artist_id}/albums?limit=50").get("data", [])[:10]:
        titles += [t["title"] for t in get(
            f"https://api.deezer.com/album/{alb['id']}/tracks?limit=100").get("data", [])]
    return titles


def main() -> None:
    raw = json.loads((HERE / "rcs_deezer_raw.json").read_text(encoding="utf-8"))
    corpus = json.loads((HERE / "fi_corpus.json").read_text(encoding="utf-8"))
    crows = corpus["rows"] if isinstance(corpus, dict) and "rows" in corpus else corpus
    name2mbid = {r["name"]: r["mbid"] for r in crows}

    # Idempotent: the corroboration half is API work; if it already ran, reuse
    # its recorded resolutions and only recompute the read.
    if OUT.exists():
        resolutions = json.loads(OUT.read_text(encoding="utf-8"))["resolutions"]
        rescore(crows, resolutions)
        return

    resolutions = []
    for name in BLOCKED:
        mbid = name2mbid[name]
        entry = raw[mbid]
        mb_titles = {norm(t) for t in mb_recording_titles(mbid)}
        cands = [c for c in entry["deezer_search"].get("data", [])
                 if norm(c.get("name", "")) == norm(name)]
        scored = []
        for c in cands:
            tracks = deezer_candidate_tracks(int(c["id"]))
            matches = sorted({t for t in tracks if norm(t) in mb_titles})
            scored.append({"deezer_id": int(c["id"]), "nb_fan_from_search": c.get("nb_fan"),
                           "matches": matches, "n_tracks_checked": len(tracks)})
        best = max(scored, key=lambda s: len(s["matches"]), default=None)
        accept = (best is not None and best["matches"]
                  and sum(1 for s in scored
                          if len(s["matches"]) == len(best["matches"])) == 1)
        row = {"name": name, "mbid": mbid,
               "mb_recording_count": len(mb_titles),
               "candidates": scored,
               "accepted": bool(accept)}
        if accept:
            page = get(f"https://api.deezer.com/artist/{best['deezer_id']}")
            row |= {"accepted_deezer_id": best["deezer_id"],
                    "nb_fan": page.get("nb_fan"),
                    "evidence_matched_titles": best["matches"]}
        else:
            row["null_reason"] = ("no_recording_title_match" if not best or not best["matches"]
                                  else "ambiguous_tie_between_candidates")
        resolutions.append(row)
        print(name, "->", "ACCEPT" if accept else row["null_reason"])

    rescore(crows, resolutions)


def rescore(crows: list[dict], resolutions: list[dict]) -> None:
    dz = json.loads((HERE / "rcs_deezer.json").read_text(encoding="utf-8"))
    dz_vals = {r["mbid"]: r for r in dz["rows"]}
    tail = [r for r in crows if r["region"] == "tail"]
    scored_rows = []
    for r in tail:
        v = dz_vals.get(r["mbid"], {}).get("D")  # the candidate value field is "D"
        am1 = next((x for x in resolutions if x["mbid"] == r["mbid"] and x["accepted"]), None)
        if v is None and am1:
            v = am1["nb_fan"]
        if v is not None:
            scored_rows.append({"name": r["name"], "hand": r["hand_value"], "nb_fan": v})
    n = len(scored_rows)
    rho = float(spearman(np.array([r["hand"] for r in scored_rows], dtype=np.int64),
                         np.array([r["nb_fan"] for r in scored_rows], dtype=np.int64)))
    from itertools import combinations
    pairs = agree = 0
    for a, b in combinations(scored_rows, 2):
        hi, lo = (a, b) if a["hand"] >= b["hand"] else (b, a)
        if lo["hand"] <= 0 or hi["hand"] / lo["hand"] < 10:
            continue
        pairs += 1
        agree += hi["nb_fan"] > lo["nb_fan"]

    result = {
        "amendment": "RCS-AM1",
        "resolutions": resolutions,
        "am1_tail_read": {
            "non_null": n, "of": 15,
            "readability_floor_12": "READABLE" if n >= 12 else "UNREADABLE",
            "spearman": round(rho, 4), "bar": ">= 0.70",
            "read": ("UNREADABLE" if n < 12 else "PASS" if rho >= 0.70 else "FAIL"),
            "pair_companion_no_bar": {"pairs": pairs,
                                      "agreement": None if not pairs else round(agree / pairs, 4)},
            "rows": scored_rows,
        },
        "as_committed_tail_read_unchanged": {"non_null": 10, "status": "UNREADABLE"},
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["am1_tail_read"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
