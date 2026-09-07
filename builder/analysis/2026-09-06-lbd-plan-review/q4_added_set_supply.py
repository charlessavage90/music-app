"""Q4: for the CXR added set, is the low degree LB's rules or OUR cap rule?

Decomposes supply over the EXTENDED archive (117,302 payloads), the one
graph-cxa-adopted.bin was built from:
   archive union (no cap)  ->  after our top_j=50  ->  final degree in the artifact
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np

ARCH = Path(r"C:\dev\music-app\builder\scratch\grt-archive-algb"
            r"\similar\listenbrainz"
            r"\session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30")
NEW = Path(r"C:\dev\music-app\builder\scratch\graph-cxa-adopted.bin")
OLD = Path(r"C:\dev\music-app\builder\scratch\graph-msw-tu50.bin")
TOP_J = 50

def meta_of(p: Path):
    b = p.read_bytes()
    ml = int(np.frombuffer(b[16:20], dtype="<u4")[0])
    m = json.loads(b[len(b)-ml:])
    n = int(np.frombuffer(b[8:12], dtype="<u4")[0])
    off = np.frombuffer(b[24:24+4*(n+1)], dtype="<i4")  # header is <4sIIIQ = 24 bytes
    return m, off

def stats(v: np.ndarray) -> str:
    return (f"median {np.median(v):>6.1f}  mean {v.mean():>7.2f}  share<=2 {100*np.mean(v<=2):>6.2f}%"
            f"  share==1 {100*np.mean(v==1):>6.2f}%  share==0 {100*np.mean(v==0):>6.2f}%"
            f"  p90 {np.percentile(v,90):>5.0f}  max {v.max():,}")

def main() -> None:
    new_meta, new_off = meta_of(NEW)
    old_meta, _ = meta_of(OLD)
    new_mbids = new_meta["mbids"]; old_set = set(old_meta["mbids"])
    added = [m for m in new_mbids if m not in old_set]
    common = [m for m in new_mbids if m in old_set]
    print(f"artifact: {len(new_mbids):,} nodes   added {len(added):,}   pre-existing {len(common):,}")

    idx: dict[str, int] = {}; mb_of: list[str] = []
    def gid(m):
        v = idx.get(m)
        if v is None:
            v = len(idx); idx[m] = v; mb_of.append(m)
        return v
    nbrs: dict[int, list[int]] = {}; scs: dict[int, list[int]] = {}
    n = 0
    for e in os.scandir(ARCH):
        if not e.name.endswith(".json"):
            continue
        mb = e.name[:-5]; me = gid(mb)
        rows = json.loads(open(e.path, "rb").read())
        a, s = [], []
        for r in rows:
            am = r.get("artist_mbid")
            if not am or am == mb:
                continue
            a.append(gid(am)); s.append(int(r.get("score") or 0))
        nbrs[me] = a; scs[me] = s; n += 1
        if n % 30000 == 0:
            print(f"  ...{n:,}", flush=True)
    print(f"payloads {n:,}  distinct mbids {len(idx):,}", flush=True)

    gset = {idx[m] for m in new_mbids if m in idx}
    final_deg = {idx[m]: int(new_off[k+1]-new_off[k]) for k, m in enumerate(new_mbids) if m in idx}
    pool = set(nbrs)  # every crawled artist is a candidate (upper bound on the pool)

    raw = {i: set() for i in gset}
    topj = {i: set() for i in gset}
    for i in gset:
        a = nbrs[i]; s = scs[i]
        order = sorted(range(len(a)), key=lambda t: (-s[t], mb_of[a[t]]))
        c = 0
        for t in order:
            y = a[t]
            if y not in pool:
                continue
            c += 1
            if y in gset:
                raw[i].add(y); raw[y].add(i)
                if c <= TOP_J:
                    topj[i].add(y); topj[y].add(i)
    # union rule: keep if EITHER endpoint ranks the other top_j -> already symmetric above

    print("\n=== supply decomposition, EXTENDED archive -> graph-cxa-adopted.bin ===")
    for label, mbs in (("ADDED (the CXR set)", added), ("PRE-EXISTING", common)):
        ids = [idx[m] for m in mbs if m in idx]
        missing = len(mbs) - len(ids)
        r = np.array([len(raw[i]) for i in ids])
        t = np.array([len(topj[i]) for i in ids])
        f = np.array([final_deg[i] for i in ids])
        print(f"\n  {label}  n={len(ids):,} (no archive payload: {missing:,})")
        print(f"    archive union, no cap   : {stats(r)}")
        print(f"    after our top_j=50 union: {stats(t)}")
        print(f"    final artifact degree   : {stats(f)}")
        print(f"    share of union-degree lost to the ceiling trim: "
              f"{100.0*(1 - f.sum()/t.sum()):.2f}% of endpoint slots")
        # how many of the added set have >2 union candidates but <=2 final edges
        print(f"    have >2 union candidates but <=2 final edges: "
              f"{int(np.sum((t > 2) & (f <= 2))):,} ({100.0*np.mean((t>2)&(f<=2)):.2f}%)")
        print(f"    have <=2 union candidates at all (LB-side sparse): "
              f"{int(np.sum(t <= 2)):,} ({100.0*np.mean(t<=2):.2f}%)")

main()
