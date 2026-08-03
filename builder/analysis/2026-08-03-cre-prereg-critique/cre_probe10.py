"""CRE critique probe 10 -- corrected frame: currency translation + population."""
import hashlib
import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig        # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

R = "C:/dev/music-app/builder/analysis/"
GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
GB = "C:/dev/music-app/builder/scratch/graph-algb-full.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
assert hashlib.sha256(open(GB, "rb").read()).hexdigest().startswith("d008a2b5")

with open(R + "2026-08-02-fame-instrument/fi_union_snapshot.json", encoding="utf-8") as f:
    snap = json.load(f)
store = GraphStore.load(GA)
N = store.artist_count


class Frame:
    def __init__(self, values):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n
        self.max_pctl = float(self.pctl_at[-1])

    def pctl(self, v):
        v = np.asarray(v, dtype=np.int64)
        i = np.searchsorted(self.uniq, v, side="left")
        below = np.where(i > 0, self.less[np.clip(i-1, 0, None)]
                         + self.counts[np.clip(i-1, 0, None)], 0)
        pres = (i < len(self.uniq)) & (self.uniq[np.clip(i, 0, len(self.uniq)-1)] == v)
        eq = np.where(pres, self.counts[np.clip(i, 0, len(self.uniq)-1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        return np.where(v > self.uniq[-1], self.max_pctl, out)


F = Frame(np.array([snap[m] for m in store.mbids if snap.get(m) is not None],
                   dtype=np.int64))
print(f"adopted frame N={F.n}")

fp = np.full(N, np.nan)
for i, m in enumerate(store.mbids):
    v = snap.get(m)
    if v is not None:
        fp[i] = float(F.pctl(np.array([v]))[0])

deg = np.diff(store.offsets).astype(np.int64)
src = np.repeat(np.arange(N), deg)
dst = store.neighbours.astype(np.int64)
order = np.argsort(store.pop_raw, kind="stable")
ranks = np.empty(N)
s = store.pop_raw[order]
i = 0
while i < N:
    j = i
    while j + 1 < N and s[j + 1] == s[i]:
        j += 1
    ranks[order[i:j+1]] = (i + j) / 2.0
    i = j + 1
poppctl = ranks / (N - 1)
both = ~np.isnan(fp[src]) & ~np.isnan(fp[dst])
mp = float(np.abs(poppctl[src] - poppctl[dst]).mean())
mf = float(np.abs(fp[src][both] - fp[dst][both]).mean())
print(f"mean |d pop_pctl| per directed edge  = {mp:.5f}  (Track 3 ramp currency)")
print(f"mean |d fame_lb_pctl| per directed edge = {mf:.5f}  (CRE ramp currency)")
print(f"ratio fame/pop = {mf/mp:.3f}")

print("\n== populations in the ADOPTED frame ==")
sb = GraphStore.load(GB)
A, Bs = set(store.mbids), set(sb.mbids)
for lab, mb in (("adopted (ALG-E MK50)", A), ("candidate (ALG-B MK50)", Bs),
                ("ALG-B only", Bs - A), ("adopted only", A - Bs)):
    vals = np.array([float(F.pctl(np.array([snap[m]]))[0])
                     for m in mb if snap.get(m) is not None])
    nulls = sum(1 for m in mb if snap.get(m) is None)
    q = np.percentile(vals, [10, 50, 90])
    print(f"  {lab:24s} n={len(mb):6d} ruler-null={nulls:5d} "
          f"({nulls/len(mb):.4f})  fame_lb_pctl p10/p50/p90 = "
          + "/".join(f"{x:.3f}" for x in q))
