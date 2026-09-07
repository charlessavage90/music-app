"""Q2 ceiling test + Q4 supply decomposition, over the ALG-B archive snapshot.

1. Is the served list a SCORE-ordered truncation of the union? If yes, a faithful
   reimplementation can reproduce it and LBD-C1's ceiling is 1.0; if no, the ceiling
   is below 1.0 by construction.
2. Where does the sparsity come from: LB's rules, our top_j=50, or our ceiling=50?
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np

ARCH = Path(r"C:\dev\music-app\builder\scratch\grt-archive-algb.pre-cex-snapshot"
            r"\similar\listenbrainz"
            r"\session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30")
GRAPH = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")
TOP_J = 50

def main() -> None:
    idx: dict[str, int] = {}
    mb_of: list[str] = []
    def gid(m):
        v = idx.get(m)
        if v is None:
            v = len(idx); idx[m] = v; mb_of.append(m)
        return v
    nbrs: dict[int, np.ndarray] = {}
    scs: dict[int, np.ndarray] = {}
    n = 0
    for entry in os.scandir(ARCH):
        if not entry.name.endswith(".json"):
            continue
        mb = entry.name[:-5]; me = gid(mb)
        rows = json.loads(open(entry.path, "rb").read())
        a, s = [], []
        for r in rows:
            am = r.get("artist_mbid")
            if not am or am == mb:
                continue
            a.append(gid(am)); s.append(int(r.get("score") or 0))
        nbrs[me] = np.asarray(a, dtype=np.int32); scs[me] = np.asarray(s, dtype=np.int64)
        n += 1
    print(f"payloads {n:,}  distinct mbids {len(idx):,}", flush=True)

    smap = {i: dict(zip(nbrs[i].tolist(), scs[i].tolist())) for i in nbrs}
    nset = {i: set(nbrs[i].tolist()) for i in nbrs}
    minsc = {i: (int(scs[i].min()) if scs[i].size else None) for i in nbrs}
    L = {i: len(nbrs[i]) for i in nbrs}

    # ---- score symmetry where BOTH directions are served ----
    same = diff = 0
    for i in nbrs:
        for y, sv in smap[i].items():
            if y in smap and i in smap[y]:
                if smap[y][i] == sv: same += 1
                else: diff += 1
    print(f"\n=== score symmetry, rows served in BOTH directions ===")
    print(f"  equal {same:,}   unequal {diff:,}   ({100.0*same/(same+diff):.4f}% equal)")

    # ---- is non-reciprocity explained by the partner's list being FULL and the
    #      omitted score being BELOW the partner's served minimum? ----
    nonrec = 0; partner_full = 0; below_min = 0; below_min_given_full = 0
    partner_notfull = 0; notfull_examples = []
    for i in nbrs:
        for y, sv in smap[i].items():
            if y not in nbrs:
                continue
            if i in nset[y]:
                continue
            nonrec += 1
            full = L[y] >= 100
            if full:
                partner_full += 1
                if minsc[y] is not None and sv <= minsc[y]:
                    below_min_given_full += 1
            else:
                partner_notfull += 1
                if len(notfull_examples) < 5:
                    notfull_examples.append((mb_of[i], mb_of[y], sv, L[y], minsc[y]))
            if minsc[y] is not None and sv <= minsc[y]:
                below_min += 1
    print(f"\n=== (Q2) non-reciprocal rows: is the partner's list truncated at 100 by SCORE? ===")
    print(f"  non-reciprocal rows (both crawled): {nonrec:,}")
    print(f"    partner's list is FULL (>=100):   {partner_full:,} ({100.0*partner_full/nonrec:.2f}%)")
    print(f"    partner's list NOT full:          {partner_notfull:,} ({100.0*partner_notfull/nonrec:.2f}%)")
    print(f"    omitted score <= partner's served minimum: {below_min:,} "
          f"({100.0*below_min/nonrec:.2f}%)")
    print(f"    ... among FULL partners:          {below_min_given_full:,} "
          f"({100.0*below_min_given_full/partner_full:.2f}% of full)")
    for e in notfull_examples:
        print(f"      not-full example: {e[0][:8]}->{e[1][:8]} score {e[2]} "
              f"partner list len {e[3]} partner min {e[4]}")

    # ---- (Q4) supply decomposition ----
    payload = GRAPH.read_bytes()
    meta_len = int(np.frombuffer(payload[16:20], dtype="<u4")[0])
    meta = json.loads(payload[len(payload)-meta_len:])
    g_mbids = meta["mbids"]
    gset = {idx[m] for m in g_mbids if m in idx}
    off = np.frombuffer(payload[20:20+4*(len(g_mbids)+1)], dtype="<i4")
    final_deg = {idx[m]: int(off[k+1]-off[k]) for k, m in enumerate(g_mbids) if m in idx}
    print(f"\n=== (Q4) supply decomposition over the served map's {len(gset):,} nodes ===")

    for pool_name, pool in (("candidate pool = 75k crawled", set(nbrs)),
                            ("candidate pool = 58,838 final nodes", gset)):
        raw = {i: set() for i in gset}
        topj = {i: set() for i in gset}
        for i in gset:
            order = sorted(range(len(nbrs[i])),
                           key=lambda t: (-int(scs[i][t]), mb_of[int(nbrs[i][t])]))
            kept = set()
            c = 0
            for t in order:
                y = int(nbrs[i][t])
                if y not in pool:
                    continue
                c += 1
                if c <= TOP_J:
                    kept.add(y)
            for t in order:
                y = int(nbrs[i][t])
                if y in gset:
                    raw[i].add(y); raw[y].add(i)
            for y in kept:
                if y in gset:
                    topj[i].add(y); topj[y].add(i)
        ids = sorted(gset)
        r = np.array([len(raw[i]) for i in ids])
        t = np.array([len(topj[i]) for i in ids])
        f = np.array([final_deg[i] for i in ids])
        print(f"\n  [{pool_name}]")
        for lbl, v in (("archive union, no cap", r), ("after top_j=50 union", t),
                       ("final artifact degree", f)):
            print(f"    {lbl:<26} median {np.median(v):>5.0f}  mean {v.mean():>7.2f}  "
                  f"share<=2 {100*np.mean(v<=2):>6.2f}%  share==1 {100*np.mean(v==1):>6.2f}%  "
                  f"share>50 {100*np.mean(v>50):>6.2f}%  max {v.max():,}")

main()
