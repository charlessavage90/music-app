"""CRE pre-registration critique, probe 2. READ-ONLY.

Runs over the adopted artifact graph-t15-tiebreakfix.bin (sha asserted) plus the
frozen fame snapshot and the committed Track 3 ladder paths. Nothing is written.

Answers, in order:
  A. currency translation for the CRE-P1 ramp: mean |delta| per edge in
     pop_raw-percentile (Track 3's currency) vs fame_lb_pctl (CRE's currency)
  B. CRE-C4 delivered-payload ratios for the committed Track 3 / 3b arms
  C. CRE-C2 base rates: top-1%-by-degree share of interiors, d0-2 vs d10-20
  D. CRE-C6: the supply screen over the 22 cb famous pairs, d0 frontier vs
     1-hop / 2-hop frontiers
"""
import hashlib
import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "C:/dev/music-app/api/src")
from artistpath_api.config import ApiConfig            # noqa: E402
from artistpath_api.graph_store import GraphStore      # noqa: E402
from artistpath_api.pathfinding import find_path       # noqa: E402

ROOT = "C:/dev/music-app/"
GRAPH = ROOT + "builder/scratch/graph-t15-tiebreakfix.bin"
SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
SNAP = ROOT + "builder/analysis/2026-08-02-fame-instrument/fi_union_snapshot.json"
T3 = ROOT + "builder/analysis/2026-07-28-track3-depth-descent/t3_paths.json"
TB = ROOT + "builder/analysis/2026-07-29-track3b-thresholded-toll/tb_paths.json"
CBP = ROOT + "builder/analysis/2026-07-30-track-b-cap-selection/cb_pairs.json"

h = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
assert h == SHA, h
print(f"artifact graph-t15-tiebreakfix.bin sha256 OK ({SHA[:12]}...)")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


store = GraphStore.load(GRAPH)
N = store.artist_count
E_dir = len(store.neighbours)
deg = np.diff(store.offsets).astype(np.int64)
print(f"N={N}  directed edge slots={E_dir}  undirected E={E_dir//2}  "
      f"degree: mean={deg.mean():.2f} median={np.median(deg):.0f} max={deg.max()}")

# ---------- fame_lb_pctl over the graph ----------
snap = load(SNAP)


class Frame:
    def __init__(self, values):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n
        self.max_pctl = float(self.pctl_at[-1])

    def pctl(self, values):
        v = np.asarray(values, dtype=np.int64)
        idx = np.searchsorted(self.uniq, v, side="left")
        below = np.where(idx > 0,
                         self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (
            self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        return np.where(v > self.uniq[-1], self.max_pctl, out)


frame = Frame(np.array([v for v in snap.values() if v is not None], dtype=np.int64))

fame_raw = np.full(N, -1, dtype=np.int64)
status = np.zeros(N, dtype=np.int8)  # 0 ok, 1 ruler-null, 2 unmapped
for i, m in enumerate(store.mbids):
    v = snap.get(m, "MISS")
    if v == "MISS":
        status[i] = 2
    elif v is None:
        status[i] = 1
    else:
        fame_raw[i] = v
ok = status == 0
fpctl = np.full(N, np.nan)
fpctl[ok] = frame.pctl(fame_raw[ok])
print(f"fame join onto adopted artifact: ok={ok.sum()} "
      f"ruler_null={(status==1).sum()} unmapped={(status==2).sum()}")

# pop_raw percentile exactly as mirror.MirrorContext.build does
order = np.argsort(store.pop_raw, kind="stable")
ranks = np.empty(N, dtype=np.float64)
s = store.pop_raw[order]
i = 0
while i < N:
    j = i
    while j + 1 < N and s[j + 1] == s[i]:
        j += 1
    ranks[order[i:j + 1]] = (i + j) / 2.0
    i = j + 1
poppctl = ranks / (N - 1)

# ---------- A. currency translation for the ramp ----------
src = np.repeat(np.arange(N), deg)
dst = store.neighbours.astype(np.int64)
mean_raw = float(np.abs(store.pop_raw[src] - store.pop_raw[dst]).mean())
mean_poppctl = float(np.abs(poppctl[src] - poppctl[dst]).mean())
both = ok[src] & ok[dst]
mean_fpctl = float(np.abs(fpctl[src][both] - fpctl[dst][both]).mean())
print("\n== A. currency translation (per directed edge) ==")
print(f"  mean |d pop_raw|      = {mean_raw:.5f}")
print(f"  mean |d pop_pctl|     = {mean_poppctl:.5f}   (Track 3 ramp currency)")
print(f"  mean |d fame_lb_pctl| = {mean_fpctl:.5f}   (CRE ramp currency, "
      f"{both.sum()} of {len(src)} edges with both ends ruler-ok)")
print(f"  scale fame/pop_pctl   = {mean_fpctl/mean_poppctl:.3f}  "
      f"-> a CRE ramp r behaves like Track 3 w = r*{mean_fpctl/mean_poppctl:.3f}")
for lab, arr in (("pop_pctl", poppctl), ("fame_lb_pctl", fpctl[ok])):
    q = np.nanpercentile(arr, [1, 25, 50, 75, 99])
    print(f"  {lab:13s} node distribution p1/p25/p50/p75/p99 = "
          + "/".join(f"{x:.3f}" for x in q) + f"  sd={np.nanstd(arr):.3f}")
# per-hop cost scale for reference
cfg = ApiConfig()
print(f"  w_hop={cfg.w_hop}  w_sim={cfg.w_sim}  w_jump={cfg.w_jump} "
      f"w_floor={cfg.w_floor}")
print(f"  mean w_sim*(1-sim) over edges = "
      f"{cfg.w_sim*float((1.0-store.scores).mean()):.5f}; "
      f"mean w_jump*|d pop_raw| = {cfg.w_jump*mean_raw:.5f}")

# ---------- B/C. ladder-derived statistics ----------
top1 = np.zeros(N, dtype=bool)
k1 = max(1, int(round(0.01 * N)))
top1[np.argsort(-deg, kind="stable")[:k1]] = True
print(f"\n  top-1%-by-degree set: {k1} nodes, degree cutoff "
      f"{deg[np.argsort(-deg, kind='stable')[k1-1]]}, "
      f"share of all node-slots = {top1.mean():.4f}")

for tag, path_file in (("Track 3", T3), ("Track 3b", TB)):
    doc = load(path_file)
    nm = doc["node_mbids"]
    groups = doc["groups"]
    print(f"\n== B/C. {tag} ==")
    for arm, per_pair in doc["paths"].items():
        ratios, hub_lo, hub_hi, tot_lo, tot_hi = [], 0, 0, 0, 0
        for pair, per_depth in per_pair.items():
            p0 = per_depth.get("0")
            if p0 is None:
                continue
            band = [d for d in (10, 15, 20) if per_depth.get(str(d))]
            if not band:
                continue
            n0 = len(p0) - 2
            if n0 <= 0:
                continue
            ratios.append(np.mean([len(per_depth[str(d)]) - 2 for d in band]) / n0)
            for d in (0, 1, 2):
                p = per_depth.get(str(d))
                if p:
                    ids = [int(x) for x in p[1:-1]]
                    hub_lo += sum(top1[i] for i in ids)
                    tot_lo += len(ids)
            for d in band:
                ids = [int(x) for x in per_depth[str(d)][1:-1]]
                hub_hi += sum(top1[i] for i in ids)
                tot_hi += len(ids)
        r = np.array(ratios)
        s_lo = hub_lo / max(tot_lo, 1)
        s_hi = hub_hi / max(tot_hi, 1)
        print(f"  arm {arm:8s} C4 payload ratio: median={np.median(r):.3f} "
              f"mean={r.mean():.3f} min={r.min():.3f} n={len(r)} | "
              f"C2 hub share d0-2={s_lo:.4f} (n={tot_lo}) "
              f"d10-20={s_hi:.4f} (n={tot_hi}) delta={s_hi-s_lo:+.4f}")

# ---------- D. CRE-C6 supply screen ----------
print("\n== D. CRE-C6 supply screen on the 22 cb famous pairs ==")
cbp = load(CBP)
fam = [t for t in cbp["triples"] if t[0] in ("ff-top01pct", "ff-top1pct")]
print(f"  famous triples: {len(fam)}  classes={Counter(t[0] for t in fam)}")
idx = store.id_by_mbid
rows = []
for klass, a, b in fam:
    if a not in idx or b not in idx:
        print(f"  MISSING endpoint {a} {b}")
        continue
    p = find_path(store, idx[a], idx[b], [], cfg)
    interior = p[1:-1]
    iv = [fpctl[i] for i in interior if ok[i]]
    if not iv:
        rows.append((klass, len(p), None, 0, 0, 0))
        continue
    med = float(np.median(iv))
    thr = med - 0.15
    nodeset = set(p)

    def count_below(frontier):
        c = 0
        for u in frontier:
            for v, _ in store.neighbours_of(u):
                if ok[v] and fpctl[v] <= thr:
                    c += 1
        return c

    # 1-hop expansion of the d0 node set
    hop1 = set(nodeset)
    for u in list(nodeset):
        for v, _ in store.neighbours_of(u):
            hop1.add(v)
    rows.append((klass, len(p), med, count_below(nodeset), count_below(hop1),
                 len(hop1)))

print(f"  {'class':13s} {'len':>3s} {'d0_int_med':>10s} {'edges<thr(d0set)':>17s} "
      f"{'edges<thr(1hop)':>16s} {'|1hop|':>7s}")
tot0 = tot1 = 0
for klass, ln, med, c0, c1, n1 in rows:
    tot0 += c0
    tot1 += c1
    print(f"  {klass:13s} {ln:3d} {('%.4f' % med) if med is not None else '  n/a':>10s} "
          f"{c0:17d} {c1:16d} {n1:7d}")
print(f"  CLASS TOTAL: d0-set edges below threshold = {tot0}   "
      f"1-hop-set edges below threshold = {tot1}")
print(f"  per-pair zero counts: d0set={sum(1 for r in rows if r[3]==0)}/{len(rows)}  "
      f"1hop={sum(1 for r in rows if r[4]==0)}/{len(rows)}")
