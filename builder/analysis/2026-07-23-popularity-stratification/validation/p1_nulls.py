"""PART 1 items 2 and 3 — null models and one-knob attribution.

All arms are built from the SAME pre-cap archive edge set (damping 0.0, clipped
scores) and all use the SAME fixed popularity reference (pre-cap clipped
in-degree, percentiled once over 74,993 nodes). Every arm runs the same
symmetrise + largest-component tail, so arms differ only in the pruning rule.

Factorial:                score-ranked top-k       random-k
  AND (mutual)            MUTUAL_TOPK (=capfix)    MUTUAL_RANDK
  OR  (union)             UNION_TOPK               UNION_RANDK

Nulls (all pruning PRECAP_SYM to capfix's edge count / degree sequence):
  RAND_E      uniform random edge removal to capfix E          (density only)
  DEGSEQ      random edges, capfix's per-node degree sequence   (structure-preserving)
  STRONGEST   globally strongest edges to capfix E              (score-greedy)
  UNION_TOPK_E  uniform subsample of UNION_TOPK to capfix E     (density control for OR)
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

# ---- fixed popularity reference -------------------------------------------
popref = np.bincount(edst, weights=clip, minlength=N)
order = np.argsort(popref, kind="stable")
PCT = np.empty(N); PCT[order] = np.arange(N) / (N - 1)
TOP500 = np.zeros(N, bool); TOP500[np.argsort(-popref)[:500]] = True
log(f"precap N={N} E={E}")

# ---- capfix reference: degree sequence in precap index space ---------------
cap = GraphStore.load(ROOT / "builder" / "scratch" / "graph-t15-capfix.bin")
ridx = {m: i for i, m in enumerate(mbids)}
capdeg = np.zeros(N, np.int64)
cd = np.diff(cap.offsets)
for m, d in zip(cap.mbids, cd):
    capdeg[ridx[m]] = d
E_CAPFIX_DIR = int(len(cap.neighbours))
log(f"capfix directed E={E_CAPFIX_DIR}  sum(capdeg)={capdeg.sum()}")

# ---- undirected pre-cap edge list (u<v), score = max of the two directions -
u = np.minimum(esrc, edst).astype(np.int64)
v = np.maximum(esrc, edst).astype(np.int64)
key = u * N + v
o = np.argsort(key, kind="stable")
key_s, u_s, v_s, sc_s = key[o], u[o], v[o], clip[o]
first = np.empty(len(key_s), bool); first[0] = True
first[1:] = key_s[1:] != key_s[:-1]
grp = np.cumsum(first) - 1
M = int(grp[-1]) + 1
UU = u_s[first]; VV = v_s[first]
SC = np.zeros(M); np.maximum.at(SC, grp, sc_s)
# reciprocity flag per undirected edge: present in both directions?
cnt = np.bincount(grp, minlength=M)
RECIP = cnt >= 2
log(f"undirected precap edges M={M}  reciprocal={RECIP.sum()} ({RECIP.mean():.4f})")

# ---- top-k sets (score-ranked, MBID tie-break) as a boolean over directed E -
def topk_mask(rank_values, rng=None):
    """Boolean over the directed edge array: is this edge in its source's top-k?"""
    m = np.zeros(E, bool)
    for i in range(N):
        a, b = int(offsets[i]), int(offsets[i + 1])
        L = b - a
        if L == 0:
            continue
        if L <= K:
            m[a:b] = True
        elif rng is None:
            sel = np.lexsort((edst[a:b], -rank_values[a:b]))[:K]
            m[a + sel] = True
        else:
            sel = rng.choice(L, size=K, replace=False)
            m[a + sel] = True
    return m

TK = topk_mask(clip)
log(f"top-k mask: {TK.sum()} directed edges in some top-k")
rng = np.random.default_rng(20260723)
RK = topk_mask(None, rng=rng)

# map directed edge -> undirected group id
gid = np.empty(E, np.int64); gid[o] = grp

def in_topk_both(mask):
    """For each undirected edge: is it selected from BOTH ends / from EITHER end?"""
    # a directed edge (a->b) selected means "b is in a's top-k"
    sel_cnt = np.bincount(gid[mask], minlength=M)
    # AND requires both directions present AND both selected
    both = (sel_cnt >= 2) & RECIP
    either = sel_cnt >= 1
    return both, either

MUT_TK, UNI_TK = in_topk_both(TK)
MUT_RK, UNI_RK = in_topk_both(RK)
log(f"MUTUAL_TOPK undirected edges={MUT_TK.sum()} (x2 = {2*MUT_TK.sum()})")

# ---- degree-sequence-matched random pruning (structure-preserving null) ----
def degseq_prune(target_deg, seed=20260723, passes=6):
    rem = target_deg.copy()
    keep = np.zeros(M, bool)
    r = np.random.default_rng(seed)
    idx_all = np.arange(M)
    for p in range(passes):
        cand = idx_all[~keep]
        r.shuffle(cand)
        # greedy sequential accept (python loop over ~4M, acceptable once)
        uu = UU[cand]; vv = VV[cand]
        for j in range(len(cand)):
            a = uu[j]; b = vv[j]
            if rem[a] > 0 and rem[b] > 0:
                rem[a] -= 1; rem[b] -= 1; keep[cand[j]] = True
        if rem.sum() == 0:
            break
    return keep, rem

# ---- evaluation ------------------------------------------------------------
def evaluate(label, keep_mask, note=""):
    uu = UU[keep_mask]; vv = VV[keep_mask]
    n_und = len(uu)
    if n_und == 0:
        print(f"{label:16s} EMPTY"); return
    # largest connected component
    A = coo_matrix((np.ones(n_und), (uu, vv)), shape=(N, N))
    ncomp, lab = connected_components(A, directed=False)
    sizes = np.bincount(lab)
    big = int(np.argmax(sizes))
    inlcc = lab == big
    m2 = inlcc[uu] & inlcc[vv]
    uu, vv = uu[m2], vv[m2]
    src = np.concatenate([uu, vv]); dst = np.concatenate([vv, uu])
    r_edge = pearsonr(PCT[src], PCT[dst])[0]
    deg = np.bincount(src, minlength=N)
    sums = np.bincount(src, weights=PCT[dst], minlength=N)
    nz = deg > 0
    r_node = pearsonr(PCT[nz], (sums[nz] / deg[nz]))[0]
    sel = TOP500[src]
    b90 = np.mean(PCT[dst[sel]] < 0.90) * 100 if sel.sum() else float("nan")
    b50 = np.mean(PCT[dst[sel]] < 0.50) * 100 if sel.sum() else float("nan")
    print(f"{label:16s} {int(nz.sum()):7d} {len(src):9d} {r_edge:+8.3f} {r_node:+8.3f} "
          f"{int(sel.sum()):9d} {b90:6.1f}% {b50:6.1f}% {int(deg.max()):6d} {int(np.median(deg[nz])):5d}  {note}")

ALL = np.ones(M, bool)
r_uni = np.random.default_rng(7)

print(f"\n{'arm':16s} {'N_lcc':>7s} {'E_dir':>9s} {'r_edge':>8s} {'r_node':>8s} "
      f"{'t500edg':>9s} {'<p90':>7s} {'<p50':>7s} {'maxdeg':>6s} {'medD':>5s}  note")
evaluate("PRECAP_SYM", ALL, "no cap at all")
evaluate("MUTUAL_TOPK", MUT_TK, "= capfix rule")
evaluate("UNION_TOPK", UNI_TK, "OR instead of AND")
evaluate("MUTUAL_RANDK", MUT_RK, "random k instead of top-k")
evaluate("UNION_RANDK", UNI_RK, "random k, OR")

# nulls at capfix density
target_und = E_CAPFIX_DIR // 2
def uniform_to(mask, n_target, seed):
    idx = np.where(mask)[0]
    rr = np.random.default_rng(seed)
    pick = rr.choice(len(idx), size=min(n_target, len(idx)), replace=False)
    out = np.zeros(M, bool); out[idx[pick]] = True
    return out

evaluate("RAND_E", uniform_to(ALL, target_und, 11), "NULL: density only, uniform")
evaluate("UNION_TOPK_E", uniform_to(UNI_TK, target_und, 12), "NULL: union thinned to capfix E")
ordS = np.argsort(-SC, kind="stable")
strong = np.zeros(M, bool); strong[ordS[:target_und]] = True
evaluate("STRONGEST_E", strong, "NULL: globally strongest edges")

log("degree-sequence null (slow greedy)...")
ks, rem = degseq_prune(capdeg)
log(f"degseq: kept {ks.sum()} und edges (target {target_und}); unmet quota {rem.sum()}")
evaluate("DEGSEQ", ks, "NULL: capfix degree sequence, random edges")

# second seed for stability
ks2, rem2 = degseq_prune(capdeg, seed=99991)
evaluate("DEGSEQ_s2", ks2, "NULL: same, seed 2")
evaluate("RAND_E_s2", uniform_to(ALL, target_und, 4242), "NULL: density only, seed 2")
log("done")
