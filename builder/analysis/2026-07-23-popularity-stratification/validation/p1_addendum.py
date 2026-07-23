"""PART 1 addendum:
 (a) stability — second RNG seeds, split-half SE on the whole-artifact figures
 (b) is the STRATIFICATION caused by 2.8's tie-break defect? one-knob arm
     (top-k ranked on UNCLIPPED scores = replay.py ARM2)
 (c) obscure-exit counts by popularity band, capfix vs control vs the
     degree-sequence null — the routing-relevant form of 2.9's top-500 metric
"""
import sys, math, time
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

SCR = Path(__file__).parent
ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

z = np.load(SCR / "precap.npz", allow_pickle=True)
esrc, edst, estr, offsets = z["esrc"], z["edst"], z["estr"], z["offsets"]
mbids = list(z["mbids"]); N = len(mbids); E = len(edst)
raw = np.expm1(np.maximum(0.0, estr))
scale = float(np.percentile(raw, 99)); log_scale = math.log1p(scale)
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / log_scale)
K = 50
popref = np.bincount(edst, weights=clip, minlength=N)
order = np.argsort(popref, kind="stable")
PCT = np.empty(N); PCT[order] = np.arange(N) / (N - 1)
TOP500 = np.zeros(N, bool); TOP500[np.argsort(-popref)[:500]] = True

u = np.minimum(esrc, edst).astype(np.int64); v = np.maximum(esrc, edst).astype(np.int64)
key = u * N + v; o = np.argsort(key, kind="stable")
key_s = key[o]
first = np.empty(len(key_s), bool); first[0] = True; first[1:] = key_s[1:] != key_s[:-1]
grp = np.cumsum(first) - 1; M = int(grp[-1]) + 1
UU = u[o][first]; VV = v[o][first]
RECIP = np.bincount(grp, minlength=M) >= 2
gid = np.empty(E, np.int64); gid[o] = grp

def topk_mask(rank_values, rng=None):
    m = np.zeros(E, bool)
    for i in range(N):
        a, b = int(offsets[i]), int(offsets[i + 1]); L = b - a
        if L == 0: continue
        if L <= K: m[a:b] = True
        elif rng is None: m[a + np.lexsort((edst[a:b], -rank_values[a:b]))[:K]] = True
        else: m[a + rng.choice(L, size=K, replace=False)] = True
    return m

def mutual(mask):
    return (np.bincount(gid[mask], minlength=M) >= 2) & RECIP
def union(mask):
    return np.bincount(gid[mask], minlength=M) >= 1

def lcc_edges(keep_mask):
    uu, vv = UU[keep_mask], VV[keep_mask]
    A = coo_matrix((np.ones(len(uu)), (uu, vv)), shape=(N, N))
    _, lab = connected_components(A, directed=False)
    big = int(np.argmax(np.bincount(lab))); inl = lab == big
    m2 = inl[uu] & inl[vv]
    uu, vv = uu[m2], vv[m2]
    return np.concatenate([uu, vv]), np.concatenate([vv, uu])

def stats(label, src, dst, note=""):
    r = pearsonr(PCT[src], PCT[dst])[0]
    deg = np.bincount(src, minlength=N)
    sums = np.bincount(src, weights=PCT[dst], minlength=N); nz = deg > 0
    rn = pearsonr(PCT[nz], sums[nz] / deg[nz])[0]
    sel = TOP500[src]
    nb = PCT[dst[sel]]
    print(f"{label:22s} {int(nz.sum()):7d} {len(src):9d} {r:+8.3f} {rn:+8.3f} "
          f"{int(sel.sum()):8d} {np.mean(nb<0.90)*100:6.1f}% {int((nb<0.90).sum()):7d} {int(deg.max()):6d}  {note}")
    return r

print(f"\n{'arm':22s} {'N_lcc':>7s} {'E_dir':>9s} {'r_edge':>8s} {'r_node':>8s} "
      f"{'t500edg':>8s} {'<p90':>7s} {'nSubP90':>7s} {'maxdeg':>6s}  note")

TKc = topk_mask(clip)
s, d = lcc_edges(mutual(TKc)); stats("MUTUAL_TOPK_clipped", s, d, "= capfix")
TKu = topk_mask(estr)
s2, d2 = lcc_edges(mutual(TKu)); stats("MUTUAL_TOPK_unclipped", s2, d2, "= replay ARM2: 2.8 fixed")

for sd in (20260723, 555, 8675309):
    rng = np.random.default_rng(sd)
    RK = topk_mask(None, rng=rng)
    s3, d3 = lcc_edges(mutual(RK)); stats(f"MUTUAL_RANDK s={sd}", s3, d3, "random-k, AND")
    s4, d4 = lcc_edges(union(RK)); stats(f"UNION_RANDK  s={sd}", s4, d4, "random-k, OR")

# ---- split-half stability of r_edge on capfix and control -------------------
print("\n--- split-half stability of r_edge (fixed reference) ---")
SCRATCH = ROOT / "builder" / "scratch"
ridx = {m: i for i, m in enumerate(mbids)}
for fn, lab in [("graph-t15-capfix.bin", "capfix"), ("graph-t15-control.bin", "control"),
                ("graph-t15-rankfix.bin", "rankfix"), ("graph-75k.bin", "original")]:
    g = GraphStore.load(SCRATCH / fn)
    gi = np.array([ridx.get(m, -1) for m in g.mbids])
    deg = np.diff(g.offsets); src = np.repeat(np.arange(g.artist_count), deg); dst = g.neighbours
    ok = (gi[src] >= 0) & (gi[dst] >= 0)
    ps, pd = PCT[gi[src[ok]]], PCT[gi[dst[ok]]]
    full = pearsonr(ps, pd)[0]
    rr = np.random.default_rng(1)
    # split by NODE, not by edge, so the halves are structurally independent
    half = rr.random(g.artist_count) < 0.5
    hs = half[src[ok]] & half[dst[ok]]
    a = pearsonr(ps[hs], pd[hs])[0]
    b = pearsonr(ps[~half[src[ok]] & ~half[dst[ok]]], pd[~half[src[ok]] & ~half[dst[ok]]])[0]
    boot = [pearsonr(ps[i], pd[i])[0] for i in
            (np.random.default_rng(k).integers(0, len(ps), len(ps)) for k in range(20))]
    print(f"{lab:10s} full={full:+.4f}  node-half-A={a:+.4f}  node-half-B={b:+.4f}  "
          f"bootstrapSD={np.std(boot):.5f}")

# ---- (c) obscure exits by popularity band ----------------------------------
print("\n--- fraction of a node's neighbours below fixed-ref p90, by popularity band ---")
print(f"{'band (pct of pop)':22s} {'n':>6s} {'capfix meanD':>12s} {'capfix f<p90':>12s} "
      f"{'DEGSEQnull f<p90':>16s} {'control meanD':>13s} {'control f<p90':>13s}")

def per_node_frac(src, dst):
    deg = np.bincount(src, minlength=N)
    lo = np.bincount(src, weights=(PCT[dst] < 0.90).astype(float), minlength=N)
    return deg, lo

cap_s, cap_d = s, d
deg_c, lo_c = per_node_frac(cap_s, cap_d)
g = GraphStore.load(SCRATCH / "graph-t15-control.bin")
gi = np.array([ridx.get(m, -1) for m in g.mbids])
dg = np.diff(g.offsets); csrc = gi[np.repeat(np.arange(g.artist_count), dg)]; cdst = gi[g.neighbours]
okc = (csrc >= 0) & (cdst >= 0)
deg_k, lo_k = per_node_frac(csrc[okc], cdst[okc])

# degree-sequence null, same construction as p1_nulls
cap = GraphStore.load(SCRATCH / "graph-t15-capfix.bin")
capdeg = np.zeros(N, np.int64)
for m, dd in zip(cap.mbids, np.diff(cap.offsets)): capdeg[ridx[m]] = dd
rem = capdeg.copy(); keep = np.zeros(M, bool); rg = np.random.default_rng(20260723)
idx_all = np.arange(M)
for p in range(6):
    cand = idx_all[~keep]; rg.shuffle(cand)
    uu, vv = UU[cand], VV[cand]
    for j in range(len(cand)):
        a_, b_ = uu[j], vv[j]
        if rem[a_] > 0 and rem[b_] > 0:
            rem[a_] -= 1; rem[b_] -= 1; keep[cand[j]] = True
    if rem.sum() == 0: break
ns, nd = lcc_edges(keep)
deg_n, lo_n = per_node_frac(ns, nd)

bands = [(0.999,1.001,"top 0.1%"),(0.99,0.999,"p99-p99.9"),(0.95,0.99,"p95-p99"),
         (0.90,0.95,"p90-p95"),(0.50,0.90,"p50-p90"),(0.0,0.50,"below p50")]
for lo_b, hi_b, name in bands:
    sel = (PCT >= lo_b) & (PCT < hi_b) & (deg_c > 0)
    selk = (PCT >= lo_b) & (PCT < hi_b) & (deg_k > 0)
    seln = (PCT >= lo_b) & (PCT < hi_b) & (deg_n > 0)
    print(f"{name:22s} {int(sel.sum()):6d} {deg_c[sel].mean():12.1f} "
          f"{(lo_c[sel]/deg_c[sel]).mean()*100:11.1f}% {(lo_n[seln]/deg_n[seln]).mean()*100:15.1f}% "
          f"{deg_k[selk].mean():13.1f} {(lo_k[selk]/deg_k[selk]).mean()*100:12.1f}%")
log("done")
