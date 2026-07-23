"""Are the hops the owner called INCOHERENT the MBID-arbitrary ceiling edges?

Contrast design: hops he flagged as jarring vs hops he flagged as fine (from
Phase 1 log 3.9). If the defect degrades path quality, the incoherent set should
be enriched for ceiling edges between ceiling-saturated endpoints.
"""
import sys, math, hashlib
from pathlib import Path
import numpy as np

ROOT = Path("C:/Users/charl/OneDrive/Claude Projects/music-app")
SCR = Path("C:/Users/charl/AppData/Local/Temp/claude/"
           "C--Users-charl-OneDrive-Claude-Projects-music-app/"
           "938e040a-82a4-4782-bdf6-a8373a2970ae/scratchpad")
sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.graph_store import GraphStore

CAP = ROOT / "builder" / "scratch" / "graph-t15-capfix.bin"
h = hashlib.sha256(CAP.read_bytes()).hexdigest()
assert h == "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237", h
g = GraphStore.load(CAP)
deg = np.diff(g.offsets)
print(f"capfix verified  N={g.artist_count}  E={len(g.neighbours)}\n", flush=True)

# pre-cap ceiling pool per node, from the cached arrays
z = np.load(SCR / "precap.npz", allow_pickle=True)
esrc, edst, estr, offsets, pre_mbids = z["esrc"], z["edst"], z["estr"], z["offsets"], list(z["mbids"])
raw = np.expm1(np.maximum(0.0, estr))
log_scale = math.log1p(float(np.percentile(raw, 99)))
isceil_pre = (np.minimum(1.0, np.log1p(np.maximum(0.0, raw)) / log_scale) >= 1.0)
L = np.diff(offsets).astype(np.int64)
ceilpool = np.add.reduceat(isceil_pre.astype(np.int64), offsets[:-1]) * (L > 0)
pre_idx = {m: i for i, m in enumerate(pre_mbids)}
K = 50

by_name = {}
for i, n in enumerate(g.names):
    by_name.setdefault(n.strip().lower(), []).append(i)

def find(name):
    hits = by_name.get(name.strip().lower(), [])
    if not hits:
        return None
    return max(hits, key=lambda i: g.popularity[i])   # most popular homonym

def sat(i):
    j = pre_idx.get(g.mbids[i])
    return None if j is None else (int(ceilpool[j]), int(L[j]), ceilpool[j] > K)

def hop(a, b):
    ia, ib = find(a), find(b)
    if ia is None or ib is None:
        return f"{a:24s} -> {b:24s}  MISSING ({a if ia is None else b})"
    lo, hi = int(g.offsets[ia]), int(g.offsets[ia + 1])
    nbrs = g.neighbours[lo:hi]
    pos = np.where(nbrs == ib)[0]
    if len(pos) == 0:
        return f"{a:24s} -> {b:24s}  NOT ADJACENT   (deg {deg[ia]}/{deg[ib]})"
    s = float(g.scores[lo:hi][pos[0]])
    sa, sb = sat(ia), sat(ib)
    satstr = ""
    if sa and sb:
        satstr = f"  ceilpool {sa[0]:3d}/{sb[0]:3d} of |out| {sa[1]:3d}/{sb[1]:3d}"
        both = sa[2] and sb[2]
        satstr += "  BOTH-SATURATED" if both else ("  one-saturated" if (sa[2] or sb[2]) else "  neither")
    return (f"{a:24s} -> {b:24s}  score={s:.4f}{' CEILING' if s >= 1.0 else '        '}"
            f"  deg {deg[ia]:2d}/{deg[ib]:2d}{satstr}")

INCOHERENT = [  # hops the owner explicitly called jarring / wrong (3.9)
    ("Metallica", "Oasis"), ("Metallica", "Bob Dylan"),
    ("Bon Iver", "Ye"), ("Ye", "Taylor Swift"),
    ("Taylor Swift", "Daft Punk"),
    ("Kylie Minogue", "Justin Timberlake"),
    ("The Shins", "The White Stripes"),
    ("Avril Lavigne", "Blink-182"),
    ("Fall Out Boy", "Marilyn Manson"),
]
COHERENT = [  # hops he explicitly endorsed or accepted
    ("The Shins", "The Flaming Lips"), ("The Flaming Lips", "The White Stripes"),
    ("Florence + the Machine", "Sia"),
    ("The Shins", "Kings of Leon"),
]

print("=== hops the owner called INCOHERENT ===", flush=True)
for a, b in INCOHERENT:
    print("  " + hop(a, b), flush=True)
print("\n=== hops the owner called COHERENT / acceptable ===", flush=True)
for a, b in COHERENT:
    print("  " + hop(a, b), flush=True)

# --- Metallica's actual neighbour list -------------------------------------
mi = find("Metallica")
lo, hi = int(g.offsets[mi]), int(g.offsets[mi + 1])
nb = g.neighbours[lo:hi]; sc = g.scores[lo:hi]
o = np.argsort(-sc)
print(f"\n=== Metallica's {len(nb)} capfix neighbours (ceilpool "
      f"{sat(mi)[0]} of |out| {sat(mi)[1]}) ===", flush=True)
print("  " + ", ".join(f"{g.names[int(nb[i])]}({sc[i]:.2f})" for i in o), flush=True)

# --- how much of the graph is fully arbitrary? -----------------------------
print("\n=== exposure: how many capfix edges are MBID-arbitrary on both ends? ===", flush=True)
satmask = np.zeros(g.artist_count, bool)
for i in range(g.artist_count):
    s = sat(i)
    if s and s[2]:
        satmask[i] = True
src_ids = np.repeat(np.arange(g.artist_count), deg)
ceil_edges = g.scores >= 1.0
both_sat = satmask[src_ids] & satmask[g.neighbours]
print(f"  nodes ceiling-saturated pre-cap        : {satmask.sum()} ({satmask.mean()*100:.2f}% of nodes)", flush=True)
print(f"  directed edges at ceiling              : {ceil_edges.sum()} ({ceil_edges.mean()*100:.2f}%)", flush=True)
print(f"  edges ceiling AND both ends saturated  : {(ceil_edges & both_sat).sum()} "
      f"({(ceil_edges & both_sat).mean()*100:.2f}%)", flush=True)
# weight by popularity: what a path actually traverses
top = np.argsort(-g.popularity)[:500]
topmask = np.zeros(g.artist_count, bool); topmask[top] = True
inc = topmask[src_ids] | topmask[g.neighbours]
print(f"  ...restricted to edges touching a top-500-popularity artist:", flush=True)
print(f"     {inc.sum()} such edges; ceiling share {ceil_edges[inc].mean()*100:.1f}%; "
      f"saturated-both share {both_sat[inc].mean()*100:.1f}%", flush=True)
print(f"  fraction of top-500 popularity artists that are saturated: "
      f"{satmask[top].mean()*100:.1f}%", flush=True)
