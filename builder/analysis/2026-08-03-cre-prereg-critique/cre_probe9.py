"""CRE critique probe 9 -- CORRECTED FRAME. READ-ONLY.

fi_validation.json records percentile_definition as
"... / N_nonnull over the ADOPTED FRAME's non-null fame_lb_raw" (N = 74,151),
NOT over the union snapshot's 88,953 non-null values. Probes 1-8 used the union
frame. This probe rebuilds every frame-sensitive figure on the correct frame and
prints both, so the size of my own error is on the record.
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

R = "C:/dev/music-app/builder/analysis/"
GA = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
GB = "C:/dev/music-app/builder/scratch/graph-algb-full.bin"
assert hashlib.sha256(open(GA, "rb").read()).hexdigest().startswith("4cb84ef9")
assert hashlib.sha256(open(GB, "rb").read()).hexdigest().startswith("d008a2b5")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


snap = load(R + "2026-08-02-fame-instrument/fi_union_snapshot.json")
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


adopted_vals = np.array([snap[m] for m in store.mbids if snap.get(m) is not None],
                        dtype=np.int64)
union_vals = np.array([v for v in snap.values() if v is not None], dtype=np.int64)
F_ADOPT, F_UNION = Frame(adopted_vals), Frame(union_vals)
print(f"ADOPTED frame N_nonnull = {F_ADOPT.n}  (fi_validation says 74151)")
print(f"UNION   frame N_nonnull = {F_UNION.n}")
cnt = Counter(adopted_vals.tolist())
big = max(cnt.values())
print(f"  largest tie atom on the adopted frame: {big} artists -> "
      f"{big/F_ADOPT.n:.6f}  (CRE section 1 quotes step 0.0015, floor 0.015)")
cntu = Counter(union_vals.tolist())
print(f"  largest tie atom on the UNION frame:   {max(cntu.values())} -> "
      f"{max(cntu.values())/F_UNION.n:.6f}  -> 10x = "
      f"{10*max(cntu.values())/F_UNION.n:.4f}")


def pctls(mbid_list, F):
    out = {}
    for m in mbid_list:
        v = snap.get(m)
        if v is not None:
            out[m] = float(F.pctl(np.array([v]))[0])
    return out


pa = pctls(store.mbids, F_ADOPT)
pu = pctls(store.mbids, F_UNION)
d = np.array([pu[m] - pa[m] for m in pa])
print(f"  frame choice shifts a node's fame_lb_pctl by median {np.median(d):+.4f}, "
      f"max {np.abs(d).max():.4f}  (union minus adopted, adopted-artifact nodes)")

# ---- C1 deltas on the corrected frame ----
print("\n== CORRECTED: Track 3 / 3b per-pair C1 deltas, ADOPTED frame ==")
for tag, f in (("Track 3", R + "2026-07-28-track3-depth-descent/t3_paths.json"),
               ("Track 3b", R + "2026-07-29-track3b-thresholded-toll/tb_paths.json")):
    doc = load(f)
    nm, anch = doc["node_mbids"], set(doc.get("unscored_anchor_pairs", []))
    ramps = doc.get("ramps") or doc.get("ws")
    for arm, pp in doc["paths"].items():
        ds, an = [], []
        for pair, pd in pp.items():
            if pd.get("0") is None:
                continue
            bd = [x for x in (10, 15, 20) if pd.get(str(x))]
            if not bd:
                continue
            def vals(p):
                return [pa[nm[str(n)]] for n in p[1:-1] if nm.get(str(n)) in pa]
            v0 = vals(pd["0"])
            vb = [x for dd in bd for x in vals(pd[str(dd)])]
            if not v0 or not vb:
                continue
            delta = float(np.median(vb)) - float(np.median(v0))
            ds.append(delta)
            if pair in anch:
                an.append(delta)
        ds = np.array(ds)
        print(f"  {tag} {arm:8s} (w={ramps.get(arm)}) n={len(ds)} "
              f"median={np.median(ds):+.4f} sd={ds.std(ddof=1):.4f} "
              f"share|d|<0.015={np.mean(np.abs(ds)<0.015):.2f} "
              f"share<=-0.05={np.mean(ds<=-0.05):.2f} | all-famous anchors: "
              + " ".join(f"{x:+.4f}" for x in an))

# ---- C6 screen + headroom on the corrected frame ----
cbp = load(R + "2026-07-30-track-b-cap-selection/cb_pairs.json")
fam = [t for t in cbp["triples"] if t[0] in ("ff-top01pct", "ff-top1pct")]
cfg = ApiConfig()
for label, path in (("ALG-E adopted", GA), ("ALG-B MK50 cell", GB)):
    st = GraphStore.load(path)
    n = st.artist_count
    fp = np.full(n, np.nan)
    for i, m in enumerate(st.mbids):
        v = snap.get(m)
        if v is not None:
            fp[i] = float(F_ADOPT.pctl(np.array([v]))[0])
    idx = st.id_by_mbid
    tot0 = tot1 = zero0 = zero1 = 0
    meds, h1 = [], []
    for klass, a, b in fam:
        p = find_path(st, idx[a], idx[b], [], cfg)
        iv = [fp[i] for i in p[1:-1] if not np.isnan(fp[i])]
        if not iv:
            continue
        med = float(np.median(iv))
        meds.append(med)
        thr = med - 0.15
        hop1 = set(p)
        for uu in list(p):
            for vv, _ in st.neighbours_of(uu):
                hop1.add(vv)
        c0 = sum(1 for uu in p for vv, _ in st.neighbours_of(uu)
                 if not np.isnan(fp[vv]) and fp[vv] <= thr)
        c1 = sum(1 for uu in hop1 for vv, _ in st.neighbours_of(uu)
                 if not np.isnan(fp[vv]) and fp[vv] <= thr)
        tot0 += c0
        tot1 += c1
        zero0 += c0 == 0
        zero1 += c1 == 0
        f1 = [fp[i] for i in hop1 if not np.isnan(fp[i])]
        h1.append(min(f1) if f1 else np.nan)
    meds, h1 = np.array(meds), np.array(h1)
    print(f"\n== CORRECTED {label}: CRE-C6 + headroom, ADOPTED frame, "
          f"{len(meds)} pairs with a d0 interior ==")
    print(f"  d0 interior median fame_lb_pctl: median over pairs={np.median(meds):.4f}")
    print(f"  CRE-C6 class total (d0 node set) = {tot0}; pairs reading zero = "
          f"{zero0}/{len(meds)}")
    print(f"  same at the 1-hop frontier      = {tot1}; pairs reading zero = "
          f"{zero1}/{len(meds)}")
    print(f"  lowest fame_lb_pctl within 1 hop of the d0 path: "
          f"median={np.nanmedian(h1):.4f} -> headroom {np.nanmedian(meds-h1):+.4f}")
