"""Does 2.9's plain-language claim hold literally -- 'no cost function can route to
an obscure artist along edges that do not exist'? Count the obscure exits per node
by popularity band in capfix, and how many nodes have exactly zero."""
import sys, math
from pathlib import Path
import numpy as np
SCR = Path(__file__).parent
ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

z = np.load(SCR / "precap.npz", allow_pickle=True)
esrc, edst, estr = z["esrc"], z["edst"], z["estr"]
mbids = list(z["mbids"]); N = len(mbids)
raw = np.expm1(np.maximum(0.0, estr)); scale = float(np.percentile(raw, 99))
clip = np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / math.log1p(scale))
popref = np.bincount(edst, weights=clip, minlength=N)
order = np.argsort(popref, kind="stable"); PCT = np.empty(N); PCT[order] = np.arange(N)/(N-1)
ridx = {m: i for i, m in enumerate(mbids)}

bands = [(0.999,1.001,"top 0.1%"),(0.99,0.999,"p99-p99.9"),(0.95,0.99,"p95-p99"),
         (0.90,0.95,"p90-p95"),(0.50,0.90,"p50-p90")]

for fn, lab in [("graph-t15-capfix.bin","capfix"), ("graph-t15-control.bin","control")]:
    g = GraphStore.load(ROOT/"builder"/"scratch"/fn)
    gi = np.array([ridx[m] for m in g.mbids])
    deg = np.diff(g.offsets)
    src = gi[np.repeat(np.arange(g.artist_count), deg)]
    dst = gi[g.neighbours]
    d = np.bincount(src, minlength=N)
    lo90 = np.bincount(src, weights=(PCT[dst]<0.90).astype(float), minlength=N)
    lo50 = np.bincount(src, weights=(PCT[dst]<0.50).astype(float), minlength=N)
    print(f"\n=== {lab} — obscure exits per node (fixed-ref percentiles) ===")
    print(f"{'band':12s} {'n':>6s} {'medDeg':>7s} {'med #<p90':>10s} {'mean #<p90':>11s} "
          f"{'% nodes 0 exits<p90':>20s} {'med #<p50':>10s} {'% 0 exits<p50':>14s}")
    for a,b,name in bands:
        s = (PCT>=a)&(PCT<b)&(d>0)
        print(f"{name:12s} {int(s.sum()):6d} {np.median(d[s]):7.0f} {np.median(lo90[s]):10.0f} "
              f"{lo90[s].mean():11.2f} {np.mean(lo90[s]==0)*100:19.1f}% "
              f"{np.median(lo50[s]):10.0f} {np.mean(lo50[s]==0)*100:13.1f}%")
