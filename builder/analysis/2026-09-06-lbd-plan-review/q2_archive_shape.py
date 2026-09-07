"""Q2/Q4: shape of the ALG-B archive's served lists, and headroom against our own cap.

Reads the endpoint archive snapshot the served map was built from. No network,
no build. Answers:
  (a) list-length distribution / the 100 ceiling
  (b) reciprocity of served lists  -> the construction ceiling on an overlap metric
  (c) reciprocity by list length and by fame band
  (d) pre-cap union degree vs degree_ceiling=50 -> how much supply our cap already drops
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import numpy as np

ARCH = Path(r"C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot"
            r"\similar\listenbrainz"
            r"\session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30")
GRAPH = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")

def load_archive():
    idx: dict[str, int] = {}
    lists: list[np.ndarray] = []
    owners: list[str] = []
    scores: list[np.ndarray] = []
    def gid(m: str) -> int:
        v = idx.get(m)
        if v is None:
            v = len(idx); idx[m] = v
        return v
    n = 0
    for entry in os.scandir(ARCH):
        if not entry.name.endswith(".json"):
            continue
        mb = entry.name[:-5]
        me = gid(mb)
        with open(entry.path, "rb") as fh:
            rows = json.loads(fh.read())
        nb, sc = [], []
        for r in rows:
            am = r.get("artist_mbid")
            if not am or am == mb:
                continue
            nb.append(gid(am)); sc.append(r.get("score") or 0)
        while len(lists) <= me:
            lists.append(None); scores.append(None); owners.append(None)
        lists[me] = np.asarray(nb, dtype=np.int32)
        scores[me] = np.asarray(sc, dtype=np.int64)
        owners[me] = mb
        n += 1
        if n % 15000 == 0:
            print(f"  ...{n:,} payloads", flush=True)
    while len(lists) < len(idx):
        lists.append(None); scores.append(None); owners.append(None)
    return idx, lists, scores, n

def main() -> None:
    print("loading archive...", flush=True)
    idx, lists, scores, n_payload = load_archive()
    have = np.array([l is not None for l in lists])
    print(f"payloads: {n_payload:,}   distinct mbids seen (owners + neighbours): {len(idx):,}   "
          f"with a payload: {int(have.sum()):,}")

    L = np.array([len(lists[i]) if lists[i] is not None else -1 for i in range(len(idx))])
    Lp = L[have]
    print("\n=== (a) served list length, over the 75k crawled artists ===")
    print(f"  median {np.median(Lp):.0f}  mean {Lp.mean():.2f}  min {Lp.min()}  max {Lp.max()}")
    for t in (100, 99, 50, 20, 10, 5, 2, 1, 0):
        print(f"    share with length {'==' if t in (0,) else '>='} {t}: "
              f"{100.0*np.mean(Lp >= t if t else Lp == 0):.2f}%")
    print(f"  share exactly at 100: {100.0*np.mean(Lp == 100):.2f}%")

    # neighbour sets for reciprocity
    print("\n=== (b) reciprocity of the served lists ===", flush=True)
    sets = [set(lists[i].tolist()) if lists[i] is not None else None for i in range(len(idx))]
    tot = rec = tot_both = rec_both = 0
    per_owner_rate = np.full(len(idx), np.nan)
    for i in range(len(idx)):
        li = lists[i]
        if li is None:
            continue
        k = both = r = 0
        for y in li.tolist():
            k += 1
            sy = sets[y]
            if sy is None:
                continue
            both += 1
            if i in sy:
                r += 1
        tot += k; tot_both += both; rec += r
        if both:
            per_owner_rate[i] = r / both
    print(f"  neighbour rows over all crawled owners: {tot:,}")
    print(f"  rows whose neighbour is ALSO crawled  : {tot_both:,} ({100.0*tot_both/tot:.2f}%)")
    print(f"  of those, reciprocal (owner in neighbour's list): {rec:,} "
          f"({100.0*rec/tot_both:.2f}%)")
    r_ok = per_owner_rate[~np.isnan(per_owner_rate)]
    print(f"  per-artist reciprocity rate: median {np.median(r_ok):.4f}  mean {r_ok.mean():.4f} "
          f" p10 {np.percentile(r_ok,10):.4f}  p90 {np.percentile(r_ok,90):.4f}")

    print("\n=== (c) reciprocity by served-list length ===")
    print(f"{'list length':<16}{'n artists':>10}{'median recip':>14}{'mean recip':>12}")
    bands = [("== 100", Lp_mask := None)]
    for label, m in [("1-4", (L >= 1) & (L <= 4)), ("5-9", (L >= 5) & (L <= 9)),
                     ("10-24", (L >= 10) & (L <= 24)), ("25-49", (L >= 25) & (L <= 49)),
                     ("50-99", (L >= 50) & (L <= 99)), ("== 100", L == 100)]:
        m = m & have & ~np.isnan(per_owner_rate)
        if m.sum() == 0:
            continue
        v = per_owner_rate[m]
        print(f"{label:<16}{int(m.sum()):>10,}{np.median(v):>14.4f}{v.mean():>12.4f}")

    # fame bands from the served artifact
    print("\n=== (c2) reciprocity and list length by fame band (served map's fame_lb) ===")
    payload = GRAPH.read_bytes()
    meta_len = int(np.frombuffer(payload[16:20], dtype="<u4")[0])
    meta = json.loads(payload[len(payload)-meta_len:])
    g_mbids = meta["mbids"]; fame = meta.get("fame_lb") or []
    pairs = [(m, f) for m, f in zip(g_mbids, fame) if f is not None and m in idx]
    fv = np.array([f for _, f in pairs], dtype=np.float64)
    gi = np.array([idx[m] for m, _ in pairs])
    qs = np.percentile(fv, [20, 40, 60, 80])
    print(f"  fame_lb quintile cuts: {qs}")
    print(f"{'fame band':<14}{'n':>8}{'med listlen':>13}{'share len=100':>15}{'med recip':>12}{'mean recip':>12}")
    edges = [-np.inf] + list(qs) + [np.inf]
    for b in range(5):
        m = (fv > edges[b]) & (fv <= edges[b+1])
        sel = gi[m]
        sel = sel[have[sel] & ~np.isnan(per_owner_rate[sel])]
        if sel.size == 0:
            continue
        print(f"{'Q'+str(b+1):<14}{sel.size:>8,}{np.median(L[sel]):>13.0f}"
              f"{100*np.mean(L[sel]==100):>14.2f}%{np.median(per_owner_rate[sel]):>12.4f}"
              f"{per_owner_rate[sel].mean():>12.4f}")

    print("\n=== (d) pre-cap UNION degree from the archive vs our degree_ceiling=50 ===")
    # union degree restricted to artists that are nodes of the served map
    gset = set(idx[m] for m in g_mbids if m in idx)
    udeg = np.zeros(len(idx), dtype=np.int64)
    nbr_union = [None] * len(idx)
    acc = {}
    for i in range(len(idx)):
        li = lists[i]
        if li is None:
            continue
        if i not in gset:
            continue
        s = acc.setdefault(i, set())
        for y in li.tolist():
            if y in gset:
                s.add(y)
                acc.setdefault(y, set()).add(i)
    for i, s in acc.items():
        udeg[i] = len(s)
    gi_all = np.array(sorted(gset))
    u = udeg[gi_all]
    print(f"  nodes considered (served map's nodes present in archive index): {u.size:,}")
    print(f"  union degree: median {np.median(u):.0f}  mean {u.mean():.2f}  "
          f"p90 {np.percentile(u,90):.0f}  max {u.max():,}")
    print(f"  share with union degree > 50 (our ceiling bites): {100.0*np.mean(u > 50):.2f}%")
    excess = np.maximum(0, u - 50).sum()
    print(f"  endpoint-slots above the ceiling, summed: {int(excess):,} of {int(u.sum()):,} "
          f"({100.0*excess/u.sum():.2f}%)")
    print(f"  share with union degree <= 2: {100.0*np.mean(u <= 2):.2f}%   "
          f"== 1: {100.0*np.mean(u == 1):.2f}%")

main()
