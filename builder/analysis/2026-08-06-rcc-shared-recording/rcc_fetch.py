"""`RCC-` — is the top similarity edge a SHARED RECORDING credit?

Governing document:
  docs/superpowers/specs/2026-08-06-shared-recording-preregistration.md
committed at d478c84 BEFORE this script fetched anything.

Within-artist control: each artist is asked about their rank-1 partner AND
the neighbour at 80% depth of their OWN list (`RCC-AM1`), so recording count
and coverage are identical across the comparison by construction.

The tail is a RELATIVE position, not an absolute rank. That is the amendment:
an absolute rank-50-100 tail needs a list of >=100, and list length is itself
a property of the arm, so it left CONTROL with 15 of 200.

Run from `api/`:
  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
    ../builder/analysis/2026-08-06-rcc-shared-recording/rcc_fetch.py

This directory OWNS its figures. Cite it; never restate them.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CCR_RAW = os.path.join(HERE, "..", "2026-08-06-ccr-relationships", "ccr_raw.json")
ARCHIVE = ("../builder/scratch/grt-archive-algb/similar/listenbrainz/"
           "session_based_days_7500_session_300_contribution_3_threshold_10_"
           "limit_100_filter_True_skip_30/")
USER_AGENT = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"
SEARCH = "https://musicbrainz.org/ws/2/recording?query={q}&fmt=json&limit=1"
RAW = os.path.join(HERE, "rcc_raw.json")
RESULT = os.path.join(HERE, "rcc_result.json")
# No RNG: RCC-AM1 makes the tail a deterministic position in each list.
# RCC-AM1: the tail is a RELATIVE position in the artist's own list, not an
# absolute rank. Requiring absolute ranks 50-100 required a list of >=100,
# and list length is itself a property of the arm - it left CONTROL with
# 15 of 200. See the prereg's RCC-AM1 section.
TAIL_FRAC = 0.8
MIN_LIST = 10


def archived(mbid):
    p = ARCHIVE + mbid + ".json"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def shares_recording(a, b, tries=4):
    """count>0 => a and b are credited on at least one common recording."""
    q = urllib.parse.quote(f"arid:{a} AND arid:{b}")
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                SEARCH.format(q=q), headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=40) as r:
                doc = json.loads(r.read().decode("utf-8"))
            if "count" not in doc:
                return None
            return int(doc["count"]) > 0
        except urllib.error.HTTPError as e:
            if e.code in (503, 429):
                time.sleep(2.5 * (attempt + 1))
                continue
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def main():
    with open(CCR_RAW, encoding="utf-8") as fh:
        ccr = json.load(fh)
    print(f"reusing the CCR- sample: {len(ccr)} artists")

    work, skipped = [], 0
    for r in ccr:
        rows = archived(r["mbid"])
        if not rows or len(rows) < MIN_LIST:
            skipped += 1
            continue
        tail = rows[int(TAIL_FRAC * (len(rows) - 1))]
        work.append({
            "arm": r["arm"], "mbid": r["mbid"], "name": r["name"],
            "rank1_mbid": r["top_partner_mbid"],
            "rank1_name": r["top_partner_name"],
            "rank1_score": r["top_partner_score"],
            "tail_mbid": tail["artist_mbid"], "tail_name": tail["name"],
            "tail_score": tail["score"],
        })
    print(f"usable {len(work)}, skipped {skipped} (archived list < {MIN_LIST})")

    cache = {}
    if os.path.exists(RAW):
        with open(RAW, encoding="utf-8") as fh:
            cache = {r["mbid"]: r for r in json.load(fh)}
        print(f"resuming: {len(cache)} already done")

    records = list(cache.values())
    todo = [w for w in work if w["mbid"] not in cache]
    for i, w in enumerate(todo, 1):
        w["rank1_shared"] = shares_recording(w["mbid"], w["rank1_mbid"])
        time.sleep(1.1)
        w["tail_shared"] = shares_recording(w["mbid"], w["tail_mbid"])
        time.sleep(1.1)
        records.append(w)
        if i % 20 == 0:
            print(f"  {i} / {len(todo)}")
            with open(RAW, "w", encoding="utf-8") as fh:
                json.dump(records, fh, indent=1)

    with open(RAW, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=1)
    score(records)


def score(records):
    res = {"governing": "specs/2026-08-06-shared-recording-preregistration.md",
           "within_artist_control": f"rank 1 vs the neighbour at {int(TAIL_FRAC*100)}% depth "
                                    f"of the SAME list (RCC-AM1)"}
    arms = {}
    for arm in ("CLASS", "CONTROL"):
        rs = [r for r in records if r["arm"] == arm]
        ok = [r for r in rs
              if r.get("rank1_shared") is not None
              and r.get("tail_shared") is not None]
        p1 = 100.0 * sum(r["rank1_shared"] for r in ok) / len(ok) if ok else 0.0
        pt = 100.0 * sum(r["tail_shared"] for r in ok) / len(ok) if ok else 0.0
        arms[arm] = {
            "n_attempted": len(rs), "n_answered": len(ok),
            "answer_rate": (len(ok) / len(rs)) if rs else 0.0,
            "pct_shared_rank1": round(p1, 2),
            "pct_shared_tail": round(pt, 2),
            "lift_points": round(p1 - pt, 2),
        }
    res["arms"] = arms
    res["RCC_G1"] = {
        "plain": "did the search actually answer, for both partners, for most artists?",
        "answer_rate_CLASS": round(arms["CLASS"]["answer_rate"], 3),
        "answer_rate_CONTROL": round(arms["CONTROL"]["answer_rate"], 3),
        "run_readable": all(a["answer_rate"] >= 0.90 for a in arms.values()),
    }
    lift = arms["CLASS"]["lift_points"]
    res["RCC_C1"] = {
        "plain": ("is the artist the app rates as most similar more likely to be "
                  "someone they are credited on a recording with, than an artist "
                  "further down that same list?"),
        "lift_points_CLASS": lift,
        "branch": ("supported" if lift >= 20 else
                   "equivocal" if lift >= 10 else "null"),
    }
    d = lift - arms["CONTROL"]["lift_points"]
    res["RCC_C2"] = {
        "plain": ("does this happen more to the central-but-unlistened artists "
                  "than to ordinary obscure ones?"),
        "class_minus_control_points": round(d, 2),
        "branch": "class_specific" if d >= 15 else "general",
    }
    with open(RESULT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
