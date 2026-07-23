"""PART 1 item 1 — recompute assortativity against a SINGLE FIXED popularity reference.

Reference: pre-cap score-weighted in-degree over the full uncapped archive edge
set (damping 0.0, p99_log_clip computed once over the whole uncapped array).
That is the project's own definition of popularity evaluated at the last point
in the pipeline BEFORE any arm diverges (pipeline.py:206-217 runs before
mutual_knn_cap at :218), so it is independent of every knob under test.

Percentiles are computed once over the 74,993-node reference population and the
SAME value is used for every artifact.
"""
import sys, math, hashlib, json
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr, spearmanr

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
SCR = Path(__file__).parent
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

SCRATCH = ROOT / "builder" / "scratch"
EXPECT = {
    "graph-75k.bin":         "478426753de39282f99c0b8955a846d159deb656576026b265bec9060977d5ff",
    "graph-t15-control.bin": "d3016bc06dd9e62de9e6edff3206ca9a3d8366243ca18b2588c0a7063042f57a",
    "graph-t15-d050.bin":    "6fb52ff8e918cf14da6e4fc6fa52052a66d7bfdb35a7f910460c2c8868c80a20",
    "graph-t15-capfix.bin":  "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237",
    "graph-t15-rankfix.bin": "87d9bf7edfc51fb13ee0fdf6a4216d01df7d3aa7f38b66ea9b7b8c2e7addae05",
}
for fn, want in EXPECT.items():
    h = hashlib.sha256((SCRATCH / fn).read_bytes()).hexdigest()
    assert h == want, f"{fn}: {h} != {want}"
print("all 5 artifact checksums verified", flush=True)

# ---- reference popularity from the pre-cap archive edge set -----------------
z = np.load(SCR / "precap.npz", allow_pickle=True)
esrc, edst, estr = z["esrc"], z["edst"], z["estr"]
mbids = list(z["mbids"])
NREF = len(mbids)
raw = np.expm1(np.maximum(0.0, estr))
scale = float(np.percentile(raw, 99))
log_scale = math.log1p(scale)
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / log_scale)
print(f"precap: N={NREF} E={len(edst)} p99raw={scale:.4f} ceilfrac={(clip>=1.0).mean():.4f}", flush=True)

REFS = {
    "A_precap_clip_indeg": np.bincount(edst, weights=clip, minlength=NREF),
    "B_precap_edgecount":  np.bincount(edst, minlength=NREF).astype(float),
    "C_precap_rawcooc":    np.bincount(edst, weights=raw, minlength=NREF),
}
ref_index = {m: i for i, m in enumerate(mbids)}


def pct_of(vals):
    order = np.argsort(vals, kind="stable")
    p = np.empty(len(vals))
    p[order] = np.arange(len(vals)) / (len(vals) - 1)
    return p


ARTIFACTS = [
    ("graph-75k.bin", "original"),
    ("graph-t15-control.bin", "control"),
    ("graph-t15-d050.bin", "d050"),
    ("graph-t15-capfix.bin", "capfix"),
    ("graph-t15-rankfix.bin", "rankfix"),
]

stores = {}
for fn, label in ARTIFACTS:
    stores[label] = GraphStore.load(SCRATCH / fn)

# sanity: how close is capfix's shipped popularity to reference A?
g = stores["capfix"]
gi = np.array([ref_index.get(m, -1) for m in g.mbids])
ok = gi >= 0
print(f"capfix nodes present in precap ref: {ok.sum()}/{len(gi)}", flush=True)
print("  spearman(capfix shipped pop, refA) =",
      round(spearmanr(g.popularity[ok], REFS['A_precap_clip_indeg'][gi[ok]]).statistic, 6), flush=True)
c = stores["control"]
ci = np.array([ref_index.get(m, -1) for m in c.mbids]); cok = ci >= 0
print(f"control nodes present in precap ref: {cok.sum()}/{len(ci)}", flush=True)
print("  spearman(control shipped pop, refA) =",
      round(spearmanr(c.popularity[cok], REFS['A_precap_clip_indeg'][ci[cok]]).statistic, 6), flush=True)


def measure(label, pct_ref, top_set_mask_ref, p90, p50, use_own_pop=False):
    g = stores[label]
    gi = np.array([ref_index.get(m, -1) for m in g.mbids])
    miss = (gi < 0)
    deg = np.diff(g.offsets)
    src = np.repeat(np.arange(g.artist_count), deg)
    dst = g.neighbours
    if use_own_pop:
        p = pct_of(g.popularity)
        ps, pd = p[src], p[dst]
        keep = np.ones(len(src), bool)
        top = np.argsort(-g.popularity)[:500]
        tmask = np.zeros(g.artist_count, bool); tmask[top] = True
        thr90, thr50 = 0.90, 0.50
    else:
        # drop edges touching a node absent from the reference population
        keep = ~miss[src] & ~miss[dst]
        ps = pct_ref[gi[src[keep]]]
        pd = pct_ref[gi[dst[keep]]]
        tmask = np.zeros(g.artist_count, bool)
        tmask[np.where(~miss)[0]] = top_set_mask_ref[gi[~miss]]
        thr90, thr50 = p90, p50
    r = pearsonr(ps, pd)[0]
    # top-500 outgoing edges
    sel = tmask[src] & keep
    nb = (pct_ref[gi[dst[sel]]] if not use_own_pop else pct_of(g.popularity)[dst[sel]])
    # node-weighted variant: mean neighbour percentile per node vs own percentile
    if not use_own_pop:
        pv = np.full(g.artist_count, np.nan)
        pv[~miss] = pct_ref[gi[~miss]]
    else:
        pv = pct_of(g.popularity)
    sums = np.add.reduceat(np.where(np.isnan(pv[dst]), 0.0, pv[dst]), g.offsets[:-1]) if len(dst) else np.zeros(g.artist_count)
    cnts = np.add.reduceat((~np.isnan(pv[dst])).astype(float), g.offsets[:-1])
    sums = np.where(deg == 0, np.nan, sums); cnts = np.where(cnts == 0, np.nan, cnts)
    mean_nb = sums / cnts
    good = ~np.isnan(pv) & ~np.isnan(mean_nb)
    r_node = pearsonr(pv[good], mean_nb[good])[0]
    return dict(label=label, N=g.artist_count, E=int(len(g.neighbours)),
                edges_used=int(keep.sum()), r_edge=r, r_node=r_node,
                top500_edges=int(sel.sum()),
                below_p90=float(np.mean(nb < thr90) * 100) if sel.sum() else float("nan"),
                below_p50=float(np.mean(nb < thr50) * 100) if sel.sum() else float("nan"))


for refname, refvals in REFS.items():
    pct_ref = pct_of(refvals)
    top500 = np.zeros(NREF, bool)
    top500[np.argsort(-refvals)[:500]] = True
    print(f"\n=== FIXED REFERENCE {refname} (percentiles over all {NREF} precap nodes) ===")
    print(f"{'artifact':10s} {'N':>7s} {'E':>9s} {'edgesUsed':>10s} {'r_edge':>8s} {'r_node':>8s} "
          f"{'t500edges':>10s} {'<p90':>7s} {'<p50':>7s}")
    for _fn, label in ARTIFACTS:
        d = measure(label, pct_ref, top500, 0.90, 0.50)
        print(f"{d['label']:10s} {d['N']:7d} {d['E']:9d} {d['edges_used']:10d} "
              f"{d['r_edge']:+8.3f} {d['r_node']:+8.3f} {d['top500_edges']:10d} "
              f"{d['below_p90']:6.1f}% {d['below_p50']:6.1f}%")

print("\n=== REPRODUCTION of §2.9 (each artifact's OWN popularity, own top-500) ===")
print(f"{'artifact':10s} {'r_edge':>8s} {'r_node':>8s} {'<p90':>7s} {'<p50':>7s}")
for _fn, label in ARTIFACTS:
    d = measure(label, None, None, None, None, use_own_pop=True)
    print(f"{d['label']:10s} {d['r_edge']:+8.3f} {d['r_node']:+8.3f} "
          f"{d['below_p90']:6.1f}% {d['below_p50']:6.1f}%")
