"""Did mutual k-NN invert the graph's popularity assortativity?

This is the load-bearing measurement behind Phase 1 log 2.9. Artifact-only,
no archive, runs in seconds.

Assortativity here = Pearson correlation of popularity PERCENTILE across the two
endpoints of every directed edge. Negative means famous artists are connected to
obscure ones (what a discovery journey needs); positive means famous artists are
connected to each other.

Percentile rather than raw popularity because the raw distribution differs
between artifacts (popularity is score-weighted in-degree, so it is a function
of the edge set under test). Percentile makes the arms comparable; raw values
would not be.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

SCRATCH = ROOT / "builder" / "scratch"
ARTIFACTS = [
    ("graph-75k.bin",           "original",  "pre-Phase-2"),
    ("graph-t15-control.bin",   "control",   "pre_symmetrise cap"),
    ("graph-t15-d050.bin",      "d050",      "mutual_knn + rank + damping 0.50"),
    ("graph-t15-capfix.bin",    "capfix",    "mutual_knn + p99_log_clip  ADOPTED"),
    ("graph-t15-rankfix.bin",   "rankfix",   "mutual_knn + percentile_rank"),
]

print(f"{'artifact':10s} {'assort':>8s} {'top500 nbrs <p90':>17s} {'<p50':>7s} "
      f"{'all-edge mean nbr pct':>22s}  note")
for fn, label, note in ARTIFACTS:
    p = SCRATCH / fn
    if not p.exists():
        print(f"{label:10s}  (absent from builder/scratch/)")
        continue
    g = GraphStore.load(p)
    pop = g.popularity
    order = np.argsort(pop)
    pct = np.empty(len(pop)); pct[order] = np.arange(len(pop)) / (len(pop) - 1)
    deg = np.diff(g.offsets)
    src = np.repeat(np.arange(g.artist_count), deg)
    dst = g.neighbours

    r = pearsonr(pct[src], pct[dst])[0]
    top = np.argsort(-pop)[:500]
    mask = np.zeros(g.artist_count, bool); mask[top] = True
    nb = pct[dst[mask[src]]]
    print(f"{label:10s} {r:+8.3f} {np.mean(nb < 0.90)*100:16.1f}% "
          f"{np.mean(nb < 0.50)*100:6.1f}% {pct[dst].mean():22.3f}  {note}")

print("""
Reading: 'top500 nbrs <p90' is the share of edges out of the 500 most popular
artists that land on an artist below the 90th popularity percentile. It is the
direct answer to "can the router step from a famous artist toward an obscure
one at all". Under the adopted artifact it is ~5%; before mutual k-NN it was
~83%.""")
