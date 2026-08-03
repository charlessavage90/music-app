"""CRE pre-registration critique, probe 3 -- CRE-D1's null. READ-ONLY.

Builds W4 through the committed five_frames() helper, joins fame_lb_pctl onto
the adopted artifact, bands edges as CRE-D1 specifies, and compares three nulls:

  N0  the observed band difference in rarity-weighted W4 agreement
  N1  CRE-D1 as written (my best reading): permute the BAND LABEL among the
      pooled labelled edges of the two bands
  N2  the size-preserving label scramble: permute label SETS among labelled
      artists WITHIN label-set-size strata, so band x size correlation is
      preserved and only the semantics are destroyed

If N2's band difference is materially non-zero in the hypothesised direction,
differential label supply alone manufactures CRE-D1's gradient and N1 cannot see it.
"""
import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

B = Path("C:/dev/music-app/builder/analysis")
for p in (B / "2026-07-30-tag-discrimination", B / "2026-07-31-release-tag-coverage",
          B / "2026-07-30-coherence-tag-probe", B / "2026-07-30-track-b-cap-selection",
          B / "2026-07-30-fame-proxy-coverage"):
    sys.path.insert(0, str(p))
sys.path.insert(0, "C:/dev/music-app/api/src")

from artistpath_api.graph_store import GraphStore  # noqa: E402
from tas_frame_split import five_frames            # noqa: E402

GRAPH = "C:/dev/music-app/builder/scratch/graph-t15-tiebreakfix.bin"
SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SNAP = ("C:/dev/music-app/builder/analysis/2026-08-02-fame-instrument/"
        "fi_union_snapshot.json")
assert hashlib.sha256(open(GRAPH, "rb").read()).hexdigest() == SHA
print("artifact sha OK")

store = GraphStore.load(GRAPH)
N = store.artist_count
deg = np.diff(store.offsets).astype(np.int64)

with open(SNAP, encoding="utf-8") as f:
    snap = json.load(f)


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
        idx = np.searchsorted(self.uniq, v, side="left")
        below = np.where(idx > 0, self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (
            self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        return np.where(v > self.uniq[-1], self.max_pctl, out)


# CORRECTED FRAME: fi_validation.json -- percentiles are over the ADOPTED
# artifact's non-null fame_lb_raw (N=74151), not the union snapshot's 88953.
frame = Frame(np.array([snap[m] for m in store.mbids if snap.get(m) is not None],
                       dtype=np.int64))
print(f"frame N_nonnull={frame.n} (must be 74151)")
fp = np.full(N, np.nan)
raw = np.zeros(N, dtype=np.int64)
okm = np.zeros(N, dtype=bool)
for i, m in enumerate(store.mbids):
    v = snap.get(m, "MISS")
    if v not in ("MISS", None):
        raw[i] = v
        okm[i] = True
fp[okm] = frame.pctl(raw[okm])
print(f"fame join: ok={okm.sum()} of {N}")

t0 = time.time()
frames = five_frames()
W4 = frames["W4"]
print(f"W4 built in {time.time()-t0:.0f}s; artists={len(W4)}")

labels = [W4.get(m, set()) for m in store.mbids]
size = np.array([len(s) for s in labels], dtype=np.int64)
print(f"W4 coverage over the adopted artifact: "
      f"{(size > 0).sum()} of {N} = {(size>0).mean():.4f}")

# rarity weights over W4, exactly tas_weighting.idf_table's shape
df = Counter()
for s in labels:
    for lab in s:
        df[lab] += 1
idf = {lab: math.log(N / c) for lab, c in df.items()}


def wagree(a, b):
    if not a or not b:
        return None
    wu = sum(idf.get(x, 0.0) for x in (a | b))
    if wu <= 0:
        return None
    return sum(idf.get(x, 0.0) for x in (a & b)) / wu


# ---- band the undirected edges ----
src = np.repeat(np.arange(N), deg)
dst = store.neighbours.astype(np.int64)
und = src < dst
u, v = src[und], dst[und]
print(f"undirected edges: {len(u)}")

fam_ok = okm[u] & okm[v]
POP = fam_ok & (fp[u] >= 0.75) & (fp[v] >= 0.75)
OBS = fam_ok & (fp[u] <= 0.50) & (fp[v] <= 0.50)
lab_ok = (size[u] > 0) & (size[v] > 0)
print("\n== CRE-D1 band supply (fame_lb_pctl bands, W4 labels) ==")
for name, mask in (("popular<->popular (both >= 0.75)", POP),
                   ("obscure<->obscure (both <= 0.50)", OBS)):
    tot = int(mask.sum())
    lab = int((mask & lab_ok).sum())
    print(f"  {name}: all edges={tot}  labelled edges={lab} "
          f"({lab/max(tot,1):.3f})  >=500 floor: {'PASS' if lab>=500 else 'FAIL'}")
    if lab:
        m = mask & lab_ok
        su, sv = size[u][m], size[v][m]
        print(f"      label-set size: median u={np.median(su):.0f} v={np.median(sv):.0f} "
              f"mean pair-min={np.minimum(su,sv).mean():.2f} "
              f"share of edges with min size==1: "
              f"{(np.minimum(su,sv)==1).mean():.3f}  "
              f"both sizes==1: {((su==1)&(sv==1)).mean():.3f}")

popE = np.flatnonzero(POP & lab_ok)
obsE = np.flatnonzero(OBS & lab_ok)


def band_vals(edge_idx, lab_list):
    out = []
    for e in edge_idx:
        a = lab_list[u[e]]
        b = lab_list[v[e]]
        w = wagree(a, b)
        if w is not None:
            out.append(w)
    return np.array(out)


pv = band_vals(popE, labels)
ov = band_vals(obsE, labels)
obs_diff = float(np.median(pv) - np.median(ov))
print(f"\n== N0 observed ==")
print(f"  popular band  n={len(pv)} median={np.median(pv):.4f} "
      f"mean={pv.mean():.4f} share exactly 0={np.mean(pv==0):.3f} "
      f"share exactly 1={np.mean(pv==1):.3f} distinct values={len(set(pv.round(6)))}")
print(f"  obscure band  n={len(ov)} median={np.median(ov):.4f} "
      f"mean={ov.mean():.4f} share exactly 0={np.mean(ov==0):.3f} "
      f"share exactly 1={np.mean(ov==1):.3f} distinct values={len(set(ov.round(6)))}")
print(f"  observed band median difference (popular - obscure) = {obs_diff:+.4f}")
print(f"  hypothesis direction (popular share FEWER) => expect negative")

# ---- N1: CRE-D1 as written -- permute band labels across pooled edges ----
rng = np.random.default_rng(20260803)
pool = np.concatenate([pv, ov])
n_p = len(pv)
d1 = np.empty(1000)
for i in range(1000):
    perm = rng.permutation(pool)
    d1[i] = np.median(perm[:n_p]) - np.median(perm[n_p:])
print(f"\n== N1 band-label permutation (CRE-D1 as written), 1000 draws ==")
print(f"  mean={d1.mean():+.5f} sd={d1.std(ddof=1):.5f} "
      f"2*sd bar={2*d1.std(ddof=1):.5f}  |observed|/sd = "
      f"{abs(obs_diff)/max(d1.std(ddof=1),1e-12):.1f}")

# ---- N2: size-preserving label scramble ----
lab_idx = np.flatnonzero(size > 0)
by_size = defaultdict(list)
for i in lab_idx:
    by_size[int(size[i])].append(i)
DRAWS = 100
d2 = np.empty(DRAWS)
t0 = time.time()
for i in range(DRAWS):
    shuffled = list(labels)
    for sz, members in by_size.items():
        if len(members) < 2:
            continue
        perm = rng.permutation(len(members))
        vals = [labels[members[k]] for k in perm]
        for k, mm in enumerate(members):
            shuffled[mm] = vals[k]
    pvn = band_vals(popE, shuffled)
    ovn = band_vals(obsE, shuffled)
    d2[i] = float(np.median(pvn) - np.median(ovn))
    if i == 0:
        print(f"  (one draw took {time.time()-t0:.1f}s)")
print(f"\n== N2 size-preserving label scramble, {DRAWS} draws ==")
print(f"  mean={d2.mean():+.5f} sd={d2.std(ddof=1):.5f} "
      f"p2.5={np.percentile(d2,2.5):+.5f} p97.5={np.percentile(d2,97.5):+.5f}")
print(f"  observed {obs_diff:+.4f};  observed - N2 mean = "
      f"{obs_diff - d2.mean():+.5f}; z vs N2 = "
      f"{(obs_diff-d2.mean())/max(d2.std(ddof=1),1e-12):+.2f}")
