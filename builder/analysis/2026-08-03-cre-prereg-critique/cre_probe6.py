"""CRE critique probe 6. READ-ONLY. Q7 (floor death depth) + Q5 (size-matched D1)."""
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict

import numpy as np

B = "C:/dev/music-app/builder/analysis/"
for p in (B + "2026-07-30-tag-discrimination", B + "2026-07-31-release-tag-coverage",
          B + "2026-07-30-coherence-tag-probe", B + "2026-07-30-track-b-cap-selection",
          B + "2026-07-30-fame-proxy-coverage"):
    sys.path.insert(0, p)
sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig        # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402

GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
store = GraphStore.load(GA)
N = store.artist_count
cfg = ApiConfig()


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


cbp = load(B + "2026-07-30-track-b-cap-selection/cb_pairs.json")
fam = [t for t in cbp["triples"] if t[0] in ("ff-top01pct", "ff-top1pct")]
idx = store.id_by_mbid
print("== Q7: the w_floor term's DEATH DEPTH on the 22 famous pairs "
      "(floor_relax_known per press, raw currency) ==")
deaths = []
for klass, a, b in fam:
    f0 = min(float(store.pop_raw[idx[a]]), float(store.pop_raw[idx[b]]))
    d = math.ceil(f0 / cfg.floor_relax_known)
    deaths.append(d)
    print(f"  {klass:12s} base floor_raw={f0:.4f} -> floor hits 0.0 after "
          f"{d} `known` presses")
deaths = np.array(deaths)
print(f"  death depth: min={deaths.min()} median={np.median(deaths):.0f} "
      f"max={deaths.max()};  share dead by depth 10 = "
      f"{(deaths <= 10).mean():.2f}; by depth 3 = {(deaths <= 3).mean():.2f}")
print(f"  pop_raw over the whole graph: p50={np.median(store.pop_raw):.4f} "
      f"p99={np.percentile(store.pop_raw,99):.4f} max={store.pop_raw.max():.4f}")

# ---------- Q5: size-matched D1 ----------
print("\n== Q5: CRE-D1 with label-set size matched ==")
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
fp = np.full(N, np.nan)
for i, m in enumerate(store.mbids):
    v = snap.get(m)
    if v is not None:
        fp[i] = float(frame.pctl(np.array([v]))[0])

from tas_frame_split import five_frames  # noqa: E402
W4 = five_frames()["W4"]
labels = [W4.get(m, set()) for m in store.mbids]
size = np.array([len(s) for s in labels])
df = Counter()
for s in labels:
    for lab in s:
        df[lab] += 1
idf = {lab: math.log(N / c) for lab, c in df.items()}

deg = np.diff(store.offsets).astype(np.int64)
src = np.repeat(np.arange(N), deg)
dst = store.neighbours.astype(np.int64)
und = src < dst
u, v = src[und], dst[und]
lab_ok = (size[u] > 0) & (size[v] > 0)
POP = lab_ok & (fp[u] >= 0.75) & (fp[v] >= 0.75)
OBS = lab_ok & (fp[u] <= 0.50) & (fp[v] <= 0.50)


def wag(a, b):
    wu = sum(idf.get(x, 0.0) for x in (a | b))
    return sum(idf.get(x, 0.0) for x in (a & b)) / wu if wu > 0 else None


def cell_vals(mask):
    out = defaultdict(list)
    for e in np.flatnonzero(mask):
        a, b = labels[u[e]], labels[v[e]]
        w = wag(a, b)
        if w is None:
            continue
        key = (min(len(a), len(b)), max(len(a), len(b)))
        out[key].append(w)
    return out


cp, co = cell_vals(POP), cell_vals(OBS)
shared = [k for k in cp if k in co and len(cp[k]) >= 30 and len(co[k]) >= 30]
np_, no_, diffs, wts = 0, 0, [], []
for k in shared:
    dmed = float(np.median(cp[k]) - np.median(co[k]))
    w = min(len(cp[k]), len(co[k]))
    diffs.append(dmed)
    wts.append(w)
    np_ += len(cp[k])
    no_ += len(co[k])
diffs, wts = np.array(diffs), np.array(wts, dtype=float)
print(f"  shared (min,max) label-size cells with >=30 edges on both sides: "
      f"{len(shared)}  (pop edges {np_}, obs edges {no_})")
print(f"  size-matched band median difference (weighted mean over cells) = "
      f"{float((diffs*wts).sum()/wts.sum()):+.4f}")
print(f"  unweighted mean over cells = {diffs.mean():+.4f}; "
      f"median over cells = {np.median(diffs):+.4f}; "
      f"cells favouring popular = {(diffs>0).sum()}/{len(diffs)}")
top = sorted(zip(wts, shared, diffs), reverse=True)[:8]
print("  largest cells:")
for w, k, d in top:
    print(f"    sizes {k}: n_pop={len(cp[k])} n_obs={len(co[k])} "
          f"med_pop={np.median(cp[k]):.4f} med_obs={np.median(co[k]):.4f} "
          f"diff={d:+.4f}")
