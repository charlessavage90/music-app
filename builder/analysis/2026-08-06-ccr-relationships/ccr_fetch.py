"""`CCR-` — are the class's top similarity edges pointing at collaborators?

Governing document:
  docs/superpowers/specs/2026-08-06-cocredit-relationship-preregistration.md
committed at dd2f53f BEFORE this script fetched anything.

Run from `api/`:
  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
    ../builder/analysis/2026-08-06-ccr-relationships/ccr_fetch.py

Writes ccr_raw.json (per-artist records) and ccr_result.json (the criteria).
Re-running reuses ccr_raw.json, so an interrupted run resumes rather than
re-fetching. This directory OWNS its figures - cite it, never restate them.
"""
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request

import numpy as np

from artistpath_api.graph_store import GraphStore

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = "../builder/scratch/graph-msw-tu50.bin"
GRAPH_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
ARCHIVE = ("../builder/scratch/grt-archive-algb/similar/listenbrainz/"
           "session_based_days_7500_session_300_contribution_3_threshold_10_"
           "limit_100_filter_True_skip_30/")
USER_AGENT = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"
MB = "https://musicbrainz.org/ws/2/artist/{mbid}?inc=artist-rels&fmt=json"
RAW = os.path.join(HERE, "ccr_raw.json")
RESULT = os.path.join(HERE, "ccr_result.json")

N_PER_ARM = 200
SEED = 20260806


def verify_artifact():
    """Prereg section 0: identity is checked before arm membership is read."""
    import hashlib
    h = hashlib.sha256()
    with open(GRAPH, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != GRAPH_SHA:
        raise SystemExit(f"ARTIFACT MISMATCH: {got} != {GRAPH_SHA}")
    print(f"artifact verified: {got[:12]}")


def archived(mbid):
    p = ARCHIVE + mbid + ".json"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def fetch_rels(mbid, tries=4):
    """MB artist-rels, rate-limited to 1/sec per MusicBrainz's terms."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                MB.format(mbid=mbid), headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (503, 429):
                time.sleep(2.0 * (attempt + 1))
                continue
            if e.code == 404:
                return None
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return "ERROR"


def related_mbids(doc):
    out = set()
    types = []
    for rel in (doc or {}).get("relations", []) or []:
        art = rel.get("artist") or {}
        mb = art.get("id")
        if mb:
            out.add(mb)
            types.append(rel.get("type") or "?")
    return out, types


def main():
    verify_artifact()
    g = GraphStore.load(GRAPH)
    fame = g.fame_lb_pctl
    N = g.artist_count
    pop_pctl = np.argsort(np.argsort(g.pop_raw)) / (N - 1)

    # Prereg section 2 - arms. CONTROL holds audience low, varies centrality.
    cls_pool = np.where((fame < 0.20) & (pop_pctl > 0.80))[0]
    ctl_pool = np.where((fame < 0.20) & (pop_pctl < 0.40))[0]
    print(f"CLASS pool={len(cls_pool)}  CONTROL-OBSCURE pool={len(ctl_pool)}")

    rng = random.Random(SEED)

    def pick(pool, n):
        """Sample n usable artists; skip those the archive cannot serve."""
        order = list(int(i) for i in pool)
        rng.shuffle(order)
        out, skipped = [], 0
        for i in order:
            if len(out) >= n:
                break
            rows = archived(g.mbids[i])
            if not rows or len(rows) < 10:
                skipped += 1
                continue
            out.append((i, rows[0]["artist_mbid"], rows[0]["name"],
                        rows[0]["score"]))
        return out, skipped

    cls, cls_skip = pick(cls_pool, N_PER_ARM)
    ctl, ctl_skip = pick(ctl_pool, N_PER_ARM)
    print(f"sampled CLASS n={len(cls)} (skipped {cls_skip}), "
          f"CONTROL n={len(ctl)} (skipped {ctl_skip})")

    cache = {}
    if os.path.exists(RAW):
        with open(RAW, encoding="utf-8") as fh:
            cache = {r["mbid"]: r for r in json.load(fh)}
        print(f"resuming: {len(cache)} already fetched")

    # Interleave the arms so a mid-run MB change cannot land on one only.
    work = []
    for k in range(max(len(cls), len(ctl))):
        if k < len(cls):
            work.append(("CLASS",) + cls[k])
        if k < len(ctl):
            work.append(("CONTROL",) + ctl[k])

    records = list(cache.values())
    done = 0
    for arm, node, top_mbid, top_name, top_score in work:
        mbid = g.mbids[node]
        if mbid in cache:
            continue
        doc = fetch_rels(mbid)
        time.sleep(1.1)
        rels, types = related_mbids(doc if doc != "ERROR" else None)
        records.append({
            "arm": arm, "mbid": mbid, "name": g.names[node],
            "fame_lb_pctl": float(fame[node]),
            "pop_raw_pctl": float(pop_pctl[node]),
            "top_partner_mbid": top_mbid, "top_partner_name": top_name,
            "top_partner_score": top_score,
            "n_relations": len(rels),
            "top_partner_related": top_mbid in rels,
            "relation_types": types,
            "fetch_error": doc == "ERROR",
        })
        done += 1
        if done % 25 == 0:
            print(f"  fetched {done} / {len(work) - len(cache)}")
            with open(RAW, "w", encoding="utf-8") as fh:
                json.dump(records, fh, indent=1)

    with open(RAW, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=1)
    print(f"fetched {len(records)} records total")
    score(records)


def score(records):
    from collections import Counter
    res = {"governing": "specs/2026-08-06-cocredit-relationship-preregistration.md",
           "artifact_sha256": GRAPH_SHA, "n_per_arm_target": N_PER_ARM}
    arms = {}
    for arm in ("CLASS", "CONTROL"):
        rs = [r for r in records if r["arm"] == arm]
        ok = [r for r in rs if not r["fetch_error"]]
        errs = len(rs) - len(ok)
        rels = [r["n_relations"] for r in ok]
        withrel = [r for r in ok if r["n_relations"] > 0]
        arms[arm] = {
            "n": len(ok), "fetch_errors": errs,
            "error_rate": (errs / len(rs)) if rs else 0.0,
            "median_relations": float(np.median(rels)) if rels else 0.0,
            "mean_relations": float(np.mean(rels)) if rels else 0.0,
            "n_with_any_relation": len(withrel),
            "CCR_C1_raw": (100.0 * sum(r["top_partner_related"] for r in ok)
                           / len(ok)) if ok else 0.0,
            "CCR_C2_conditional": (
                100.0 * sum(r["top_partner_related"] for r in withrel)
                / len(withrel)) if withrel else 0.0,
        }
    res["arms"] = arms

    # CCR-G1 first and alone: which outcome is primary?
    mc, mo = arms["CLASS"]["median_relations"], arms["CONTROL"]["median_relations"]
    ratio = (max(mc, mo) / min(mc, mo)) if min(mc, mo) > 0 else math.inf
    confounded = ratio >= 2.0
    res["CCR_G1"] = {
        "plain": "does MusicBrainz simply know more about one group than the other?",
        "median_relations_CLASS": mc, "median_relations_CONTROL": mo,
        "ratio": None if ratio == math.inf else round(ratio, 3),
        "documentation_confound": confounded,
        "primary_outcome": "CCR_C2_conditional" if confounded else "CCR_C1_raw",
    }
    primary = res["CCR_G1"]["primary_outcome"]
    delta = arms["CLASS"][primary] - arms["CONTROL"][primary]
    res["primary"] = {
        "outcome": primary, "delta_points": round(delta, 2),
        "branch": ("supported" if delta >= 20 else
                   "equivocal" if delta >= 10 else "null"),
    }
    # CCR-C3 descriptive only, no branch.
    tc = Counter()
    for r in records:
        if r["arm"] == "CLASS" and r["top_partner_related"]:
            tc.update(r["relation_types"])
    res["CCR_C3_relation_types_CLASS"] = dict(tc.most_common(12))
    res["run_state_complete"] = all(
        arms[a]["error_rate"] <= 0.10 and arms[a]["n"] > 0 for a in arms)

    with open(RESULT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
