"""CRE critique probe 5. READ-ONLY.

(a) Runs the CRE ladder shape (all-`known`, victim = highest fame_lb_pctl,
    production weights) on the 22 cb famous pairs over the ADOPTED artifact,
    and reports how many pairs survive to each depth under find_path (the
    harness) vs find_journey (the app).
(b) ALG-B ruler-null concentration by in-graph popularity.
"""
import hashlib
import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig                        # noqa: E402
from artistpath_api.graph_store import GraphStore                  # noqa: E402
from artistpath_api.pathfinding import Exclusion, KNOWN, find_journey, find_path  # noqa: E402

R = "C:/dev/music-app/builder/analysis/"
GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
GB = "C:/dev/music-app/builder/scratch/graph-algb-full.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
assert hashlib.sha256(open(GB, "rb").read()).hexdigest().startswith("d008a2b5")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


snap = load(R + "2026-08-02-fame-instrument/fi_union_snapshot.json")


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
        idx = np.searchsorted(self.uniq, v, side="left")
        below = np.where(idx > 0, self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (
            self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        return (below + (eq + 1) / 2.0) / self.n


frame = Frame(np.array([v for v in snap.values() if v is not None], dtype=np.int64))
store = GraphStore.load(GA)
N = store.artist_count
fp = np.full(N, np.nan)
for i, m in enumerate(store.mbids):
    v = snap.get(m)
    if v is not None:
        fp[i] = float(frame.pctl(np.array([v]))[0])

cfg = ApiConfig()
cbp = load(R + "2026-07-30-track-b-cap-selection/cb_pairs.json")
fam = [t for t in cbp["triples"] if t[0] in ("ff-top01pct", "ff-top1pct")]
idx = store.id_by_mbid


def victim_of(interior):
    # CRE section 0.3: highest fame_lb_pctl; ruler-nulls and ties by pop_raw
    # then lowest mbid.
    def key(v):
        f = fp[v]
        return (-(f if not np.isnan(f) else -1.0),
                -float(store.pop_raw[v]), store.mbids[v])
    return min(interior, key=key)


print("== (a) ladder survival on the 22 famous pairs, adopted artifact, "
      "production weights ==")
alive_fp = np.zeros(21, dtype=int)
alive_fj = np.zeros(21, dtype=int)
rows = []
for klass, a, b in fam:
    s, t = idx[a], idx[b]
    # find_path ladder (what the harness does)
    exc, dfp = [], 0
    for d in range(21):
        p = find_path(store, s, t, exc, cfg)
        if p is None or len(p) <= 2:
            break
        alive_fp[d] += 1
        dfp = d
        exc = exc + [Exclusion(node=victim_of(p[1:-1]), reason=KNOWN)]
    # find_journey ladder (what the app does)
    exc, dfj, stops = [], 0, Counter()
    for d in range(21):
        r = find_journey(store, s, t, exc, cfg)
        if r is None:
            break
        p, rule = r
        stops[rule] += 1
        if len(p) <= 2:
            break
        alive_fj[d] += 1
        dfj = d
        exc = exc + [Exclusion(node=victim_of(p[1:-1]), reason=KNOWN)]
    rows.append((klass, dfp, dfj, dict(stops)))

print(f"  {'depth':>5s} {'pairs with a nonempty interior (find_path)':>44s} "
      f"{'(find_journey)':>16s}")
for d in (0, 1, 2, 3, 5, 10, 15, 20):
    print(f"  {d:5d} {alive_fp[d]:44d} {alive_fj[d]:16d}")
print("  per-pair last live depth (find_path / find_journey):")
for klass, dfp, dfj, stops in rows:
    print(f"    {klass:12s} {dfp:3d} / {dfj:3d}   stop rules seen: {stops}")
n_fail = sum(1 for r in rows if r[1] < 10)
print(f"  pairs that do NOT reach depth 10 under find_path: {n_fail} of {len(rows)}")
for k in ("ff-top01pct", "ff-top1pct"):
    sub = [r for r in rows if r[0] == k]
    ok = sum(1 for r in sub if r[1] >= 10)
    print(f"    class {k}: {ok} of {len(sub)} reach depth 10 "
          f"-> CRE-G3 floor (>=8): {'PASS' if ok >= 8 else 'FAIL'}")

print("\n== (b) ALG-B ruler-null concentration ==")
sb = GraphStore.load(GB)
nb = sb.artist_count
isnull = np.array([snap.get(m, "MISS") is None for m in sb.mbids])
missing = np.array([snap.get(m, "MISS") == "MISS" for m in sb.mbids])
pop = np.asarray(sb.pop_raw, dtype=np.float64)
order = pop.argsort(kind="stable")
pctl = np.empty(nb)
pctl[order] = np.arange(nb) / (nb - 1)
print(f"  ALG-B nodes={nb} ruler-null={isnull.sum()} ({isnull.mean():.4f}) "
      f"absent from snapshot={missing.sum()}")
print(f"  in-graph popularity percentile of ruler-null nodes: "
      f"median={np.median(pctl[isnull]):.3f}  p90={np.percentile(pctl[isnull],90):.3f}")
print(f"  null rate by in-graph popularity decile:")
for i in range(10):
    m = (pctl >= i / 10) & (pctl < (i + 1) / 10 + (1e-9 if i == 9 else 0))
    print(f"    decile {i/10:.1f}-{(i+1)/10:.1f}: null rate="
          f"{isnull[m].mean():.4f} (n={m.sum()})")
na = np.array([snap.get(m, "MISS") is None for m in store.mbids])
print(f"  ALG-E adopted nodes={N} ruler-null={na.sum()} ({na.mean():.5f})")
