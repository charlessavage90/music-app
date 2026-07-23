"""Is 'Radiohead absent / Beatles deg 7' a capfix (mutual-kNN) effect, or a
data-coverage issue present in every build? Triangulate across graphs."""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore

B = r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch"
GRAPHS = {
  "capfix (ADOPTED, mutual-kNN)": B + r"\graph-t15-capfix.bin",
  "control (t15, legacy cap)":    B + r"\graph-t15-control.bin",
  "d025 (t15, damped)":           B + r"\graph-t15-d025.bin",
  "original 75k":                 B + r"\graph-75k.bin",
}
WATCH = ["Radiohead", "The Beatles", "Thom Yorke", "Coldplay", "Nirvana", "Leavv", "saib."]

for label, path in GRAPHS.items():
    try:
        s = GraphStore.load(path)
    except Exception as e:
        print(f"\n### {label}: LOAD FAILED {e}"); continue
    deg = np.diff(s.offsets); N = len(s.names)
    idx = {nm.lower(): j for j, nm in enumerate(s.names)}
    p99 = int(np.percentile(deg, 99))
    print(f"\n### {label}  N={N:,}  E={int(deg.sum()):,}  median-deg={int(np.median(deg))}  p99-deg={p99}  max-deg={int(deg.max())}")
    for nm in WATCH:
        j = idx.get(nm.lower())
        if j is None:
            print(f"    {nm:<14} ABSENT")
        else:
            print(f"    {nm:<14} deg={int(deg[j]):>4}  pop={float(s.popularity[j]):.2f}  "
                  f"{'>=p99 HUB' if deg[j]>=p99 else ''}")
