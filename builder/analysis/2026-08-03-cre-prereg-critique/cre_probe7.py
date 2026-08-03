"""CRE critique probe 7. READ-ONLY. Q6: is a common absolute C1 bar cross-population?

Routes the 22 cb famous pairs at production weights on BOTH Track B MK50 cells
(ALG-E adopted-equivalent and ALG-B graph-algb-full = the ALG-B-MK50 cell) and
reports the descent HEADROOM each data set offers: d0 interior median, and the
lowest fame_lb_pctl reachable within the d0 path's 1- and 2-hop neighbourhood.
"""
import hashlib
import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig        # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import find_path   # noqa: E402

B = "C:/dev/music-app/builder/analysis/"
CELLS = {
    "ALG-E adopted (4cb84ef9)": ("C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin",
                                 "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"),
    "ALG-B MK50 cell (d008a2b5)": ("C:/dev/music-app/builder/scratch/graph-algb-full.bin",
                                   "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f"),
}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


snap = load(B + "2026-08-02-fame-instrument/fi_union_snapshot.json")


class Frame:
    def __init__(self, values):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n

    def pctl(self, v):
        v = np.asarray(v, dtype=np.int64)
        i = np.searchsorted(self.uniq, v, side="left")
        below = np.where(i > 0, self.less[np.clip(i-1, 0, None)]
                         + self.counts[np.clip(i-1, 0, None)], 0)
        pres = (i < len(self.uniq)) & (self.uniq[np.clip(i, 0, len(self.uniq)-1)] == v)
        eq = np.where(pres, self.counts[np.clip(i, 0, len(self.uniq)-1)], 0)
        return (below + (eq + 1) / 2.0) / self.n


frame = Frame(np.array([v for v in snap.values() if v is not None], dtype=np.int64))
cbp = load(B + "2026-07-30-track-b-cap-selection/cb_pairs.json")
fam = [t for t in cbp["triples"] if t[0] in ("ff-top01pct", "ff-top1pct")]
cfg = ApiConfig()

for label, (path, sha) in CELLS.items():
    assert hashlib.sha256(open(path, "rb").read()).hexdigest() == sha
    st = GraphStore.load(path)
    n = st.artist_count
    fp = np.full(n, np.nan)
    for i, m in enumerate(st.mbids):
        v = snap.get(m)
        if v is not None:
            fp[i] = float(frame.pctl(np.array([v]))[0])
    idx = st.id_by_mbid
    print(f"\n== {label}  N={n} ==")
    print(f"  ruler-null nodes: {int(np.isnan(fp).sum())} ({np.isnan(fp).mean():.4f})")
    d0meds, h1, h2, miss = [], [], [], 0
    for klass, a, b in fam:
        if a not in idx or b not in idx:
            miss += 1
            continue
        p = find_path(st, idx[a], idx[b], [], cfg)
        iv = [fp[i] for i in p[1:-1] if not np.isnan(fp[i])]
        if not iv:
            continue
        d0meds.append(float(np.median(iv)))
        hop1 = set(p)
        for u in list(p):
            for v_, _ in st.neighbours_of(u):
                hop1.add(v_)
        hop2 = set(hop1)
        for u in list(hop1):
            for v_, _ in st.neighbours_of(u):
                hop2.add(v_)
        f1 = [fp[i] for i in hop1 if not np.isnan(fp[i])]
        f2 = [fp[i] for i in hop2 if not np.isnan(fp[i])]
        h1.append(min(f1) if f1 else np.nan)
        h2.append(min(f2) if f2 else np.nan)
    d0meds, h1, h2 = np.array(d0meds), np.array(h1), np.array(h2)
    print(f"  pairs with both endpoints present: {len(fam)-miss} of {len(fam)}; "
          f"pairs with a d0 interior: {len(d0meds)}")
    print(f"  d0 interior median fame_lb_pctl: median over pairs = "
          f"{np.median(d0meds):.4f}  min={d0meds.min():.4f}")
    print(f"  lowest fame_lb_pctl within 1 hop of the d0 path: "
          f"median={np.nanmedian(h1):.4f}  -> headroom {np.nanmedian(d0meds-h1):+.4f}")
    print(f"  lowest fame_lb_pctl within 2 hops of the d0 path: "
          f"median={np.nanmedian(h2):.4f}  -> headroom {np.nanmedian(d0meds-h2):+.4f}")
    print(f"  graph-wide fame_lb_pctl p1/p10/p50 = "
          + "/".join(f"{x:.3f}" for x in np.nanpercentile(fp, [1, 10, 50])))
