"""Who has zero obscure exits — the famous artists, or the micro-genre hubs?

Prompted by the owner asking whether §2.10's zero-exit nodes are the
lo-fi/chiptune cap-set artists or the Beatles-like ones. The answer is that the
question has a false premise, and establishing that is the point of this probe:
the lo-fi artists sit in the top 1-3% BY POPULARITY, so they are not a separate
population from the famous ones.

Produces §2.11. Artifact-only, seconds.

Note on the reference: §2.10 established that capfix's shipped popularity is
Spearman 1.000000 against the fixed pre-cap reference, so for capfix alone the
artifact's own popularity IS the fixed reference. Do not reuse that shortcut for
control, whose popularity was contaminated by its cap.
"""
import sys, hashlib
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

CAP = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"
assert hashlib.sha256(CAP.read_bytes()).hexdigest() == \
    "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"
g = GraphStore.load(CAP)
pop = g.popularity
order = np.argsort(pop)
pct = np.empty(len(pop)); pct[order] = np.arange(len(pop)) / (len(pop) - 1)
deg = np.diff(g.offsets)

EXIT_THRESHOLD = 0.90   # an "exit" is a neighbour below this popularity percentile
exits = np.array([int((pct[g.neighbours[int(g.offsets[i]):int(g.offsets[i + 1])]]
                       < EXIT_THRESHOLD).sum()) for i in range(g.artist_count)])
zero = (exits == 0) & (deg > 0)

print(f"nodes with ZERO sub-p{int(EXIT_THRESHOLD*100)} exits: {zero.sum()} "
      f"of {g.artist_count} ({zero.mean()*100:.1f}%)")
print(f"  their popularity percentile: median={np.median(pct[zero]):.3f} "
      f"p10={np.percentile(pct[zero],10):.3f} min={pct[zero].min():.3f}")

POP_BANDS = [(0.999, 1.001, "top 0.1%"), (0.99, 0.999, "p99-99.9"),
             (0.95, 0.99, "p95-99"), (0.90, 0.95, "p90-95"),
             (0.50, 0.90, "p50-90"), (0.0, 0.50, "below p50")]
DEG_BANDS = [(45, 10**9, "deg>=45"), (20, 45, "deg 20-44"), (0, 20, "deg<20")]

print("\nZERO-EXIT RATE, popularity band x degree band")
print(f"{'popularity':14s} " + " ".join(f"{l:>20s}" for _, _, l in DEG_BANDS))
for lo, hi, lbl in POP_BANDS:
    m = (pct >= lo) & (pct < hi) & (deg > 0)
    cells = []
    for dlo, dhi, _ in DEG_BANDS:
        s = m & (deg >= dlo) & (deg < dhi)
        cells.append(f"{zero[s].mean()*100:5.1f}% (n={s.sum():5d})" if s.sum() else "       --       ")
    print(f"{lbl:14s} " + " ".join(f"{c:>20s}" for c in cells))

def show(title, names):
    print(f"\n{title}")
    for n in names:
        hits = [i for i, x in enumerate(g.names) if x.strip().lower() == n.lower()]
        if not hits:
            print(f"  {n:20s} (not found)"); continue
        i = max(hits, key=lambda j: pop[j])
        print(f"  {n:20s} deg={deg[i]:3d}  pop pctile={pct[i]:.3f}  exits={exits[i]:3d}")

show("Named in §2.2 as the top-25 by DEGREE (the 'micro-genre' set):",
     ["Leavv", "saib.", "Lazerhawk", "CROOVE", "Toonorth", "idealism",
      "sleepy fish", "Miami Nights 1984", "Purrple Cat", "Kobaryo", "USAO", "Stonebank"])
show("Famous artists, for contrast:",
     ["The Beatles", "Coldplay", "Metallica", "Nirvana", "Taylor Swift",
      "The Shins", "Pink Floyd", "Aphex Twin"])

print("""
Reading: zero-exit rate rises monotonically with popularity inside every degree
band and effectively vanishes below p90, so it is a popularity property rather
than a degree one. The top row is U-shaped in degree because there are two
routes into it: too few edges to have any obscure ones (the §2.8 tie-break
victims, e.g. The Beatles at degree 7), and all 50 slots consumed by same-band
peers (the saturated ones, e.g. Metallica at degree 50).""")
