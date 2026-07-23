"""Null at CONTROL's degree sequence, so the 83%-vs-5% comparison has a null at
both densities and the ratio is reportable on both sides."""
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
esrc, edst, estr = z["esrc"], z["edst"], z["estr"]
mbids = list(z["mbids"]); N = len(mbids)
raw = np.expm1(np.maximum(0.0, estr)); scale = float(np.percentile(raw, 99))
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / math.log1p(scale))
popref = np.bincount(edst, weights=clip, minlength=N)
order = np.argsort(popref, kind="stable"); PCT = np.empty(N); PCT[order] = np.arange(N)/(N-1)
TOP500 = np.zeros(N, bool); TOP500[np.argsort(-popref)[:500]] = True

u = np.minimum(esrc, edst).astype(np.int64); v = np.maximum(esrc, edst).astype(np.int64)
key = u*N+v; o = np.argsort(key, kind="stable"); ks = key[o]
first = np.empty(len(ks), bool); first[0]=True; first[1:] = ks[1:]!=ks[:-1]
M = int(first.sum()); UU = u[o][first]; VV = v[o][first]
log(f"undirected precap M={M}")

ridx = {m:i for i,m in enumerate(mbids)}
def degvec(fn):
    g = GraphStore.load(ROOT/"builder"/"scratch"/fn)
    dv = np.zeros(N, np.int64)
    for m, d in zip(g.mbids, np.diff(g.offsets)):
        if m in ridx: dv[ridx[m]] = d
    return dv, g

def degseq_prune(target, seed, passes=6):
    rem = target.copy(); keep = np.zeros(M, bool)
    rg = np.random.default_rng(seed); idx_all = np.arange(M)
    for _ in range(passes):
        cand = idx_all[~keep]; rg.shuffle(cand)
        uu, vv = UU[cand], VV[cand]
        for j in range(len(cand)):
            a,b = uu[j], vv[j]
            if rem[a] > 0 and rem[b] > 0:
                rem[a]-=1; rem[b]-=1; keep[cand[j]]=True
        if rem.sum()==0: break
    return keep, rem

def report(label, keep):
    uu, vv = UU[keep], VV[keep]
    A = coo_matrix((np.ones(len(uu)),(uu,vv)), shape=(N,N))
    _, lab = connected_components(A, directed=False)
    big = int(np.argmax(np.bincount(lab))); inl = lab==big
    m2 = inl[uu]&inl[vv]; uu,vv = uu[m2],vv[m2]
    src = np.concatenate([uu,vv]); dst = np.concatenate([vv,uu])
    r = pearsonr(PCT[src],PCT[dst])[0]
    deg = np.bincount(src,minlength=N); sums = np.bincount(src,weights=PCT[dst],minlength=N)
    nz = deg>0; rn = pearsonr(PCT[nz],sums[nz]/deg[nz])[0]
    sel = TOP500[src]; nb = PCT[dst[sel]]
    print(f"{label:26s} N={int(nz.sum()):6d} E={len(src):8d} r_edge={r:+.3f} r_node={rn:+.3f} "
          f"t500edges={int(sel.sum()):7d} <p90={np.mean(nb<0.90)*100:5.1f}% n={int((nb<0.90).sum()):7d} "
          f"maxdeg={int(deg.max()):6d}")

cdeg, cg = degvec("graph-t15-control.bin")
log(f"control degseq sum={cdeg.sum()} max={cdeg.max()}")
for sd in (20260723, 555):
    k, rem = degseq_prune(cdeg, sd)
    log(f"seed {sd}: kept {k.sum()} und edges, unmet quota {rem.sum()} ({rem.sum()/cdeg.sum():.3f})")
    report(f"DEGSEQ_control s={sd}", k)
log("done")
