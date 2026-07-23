"""Pre-check: MBID tie-break signature in capfix vs d025 (no-tie-mass null)."""
import sys, hashlib
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path("C:/Users/charl/OneDrive/Claude Projects/music-app/api/src")))
from artistpath_api.graph_store import GraphStore

SCRATCH = Path("C:/Users/charl/OneDrive/Claude Projects/music-app/builder/scratch")

def load(name):
    p = SCRATCH / name
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    g = GraphStore.load(p)
    print(f"{name}  sha256={h[:16]}  N={g.artist_count}  E={len(g.neighbours)}", flush=True)
    return g

def report(g, label, popstrat=True):
    n = g.artist_count
    # MBIDs are already sorted lexicographically by build_graph (sorted-MBID id order).
    assert g.mbids == sorted(g.mbids), "mbid order assumption broken"
    r = np.arange(n, dtype=np.float64) / max(n - 1, 1)   # uniform by construction
    rv = r[g.neighbours]                                  # percentile of destination
    ceil = g.scores >= 1.0
    print(f"\n--- {label} ---", flush=True)
    def line(tag, mask):
        k = int(mask.sum())
        if k == 0:
            print(f"  {tag:34s} n=0"); return
        m = rv[mask].mean(); se = rv[mask].std(ddof=1) / np.sqrt(k)
        print(f"  {tag:34s} n={k:7d}  mean r(v)={m:.4f}  SE={se:.4f}  z vs 0.5={(m-0.5)/se:+7.2f}", flush=True)
    line("all edges", np.ones(len(rv), bool))
    line("ceiling edges (score==1.0)", ceil)
    line("sub-ceiling edges", ~ceil)
    if popstrat:
        deg = np.diff(g.offsets)
        order = np.argsort(-g.popularity)
        for lo, hi in [(0, 25), (0, 100), (0, 500)]:
            idx = order[lo:hi]
            sel = np.zeros(len(rv), bool)
            for i in idx:
                sel[int(g.offsets[i]):int(g.offsets[i + 1])] = True
            line(f"edges out of top-{hi} popularity", sel)
        # source-side: r(u) of nodes at the cap
        at50 = np.where(deg >= 50)[0]
        if len(at50):
            print(f"  {'r(u) of nodes at cap 50':34s} n={len(at50):7d}  mean r(u)={r[at50].mean():.4f}", flush=True)
        # spearman(degree, r)
        from scipy.stats import spearmanr
        print(f"  spearman(degree, r(u)) all nodes      = {spearmanr(deg, r).statistic:+.4f}", flush=True)
        top = order[:2000]
        print(f"  spearman(degree, r(u)) top-2000 pop   = {spearmanr(deg[top], r[top]).statistic:+.4f}", flush=True)
        print(f"  spearman(popularity, r(u)) [null~0]   = {spearmanr(g.popularity, r).statistic:+.4f}", flush=True)

cap = load("graph-t15-capfix.bin")
d025 = load("graph-t15-d025.bin")
report(cap, "capfix (clipped ranking, tie mass present)")
report(d025, "d025 (rank transform, no tie mass) — NULL ARM")
