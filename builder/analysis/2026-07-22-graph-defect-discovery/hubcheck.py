"""Is 'hub' (our metric = top-1% by DEGREE) the same as 'famous' (popularity)?
The owner perceived Prince/Whitney/Kylie/Paul Simon as hubs; hubfrac said 0."""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore
from artistpath_api.evaluation import hub_node_set

store = GraphStore.load(r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch\graph-t15-capfix.bin")
pop = store.popularity
deg = np.diff(store.offsets)
HUBS = hub_node_set(store, 0.01)
N = len(store.names)

# thresholds
deg_sorted = np.sort(deg)
thr = deg_sorted[int(N * 0.99)]     # top-1% degree cutoff
print(f"N={N}  top-1% DEGREE hub cutoff = {thr} neighbours  (hub set size={len(HUBS)})\n")

def deg_pct(d): return 100.0 * (deg < d).sum() / N
def pop_pct(p): return 100.0 * (pop < p).sum() / N

names = ["The Shins", "Kylie Minogue", "Whitney Houston", "Prince", "Paul Simon",
         "EELS", "Nick Cave & the Bad Seeds", "Electric Light Orchestra", "Wishbone Ash",
         # contrast: artists that ARE structural hubs
         "Aerosmith", "The Beatles", "Radiohead", "Kings of Leon"]
print(f"{'artist':<28}{'deg':>5}{'degPct':>8}{'pop':>7}{'popPct':>8}{'isHub?':>8}")
for nm in names:
    i = next((j for j in range(N) if store.names[j].lower() == nm.lower()), None)
    if i is None:
        print(f"{nm:<28} NOT FOUND"); continue
    print(f"{store.names[i]:<28}{int(deg[i]):>5}{deg_pct(deg[i]):>7.1f}%"
          f"{float(pop[i]):>7.2f}{pop_pct(pop[i]):>7.1f}%{('HUB' if i in HUBS else '-'):>8}")

# how much do degree-rank and popularity-rank actually agree?
from scipy.stats import spearmanr
r, _ = spearmanr(deg, pop)
print(f"\nSpearman(degree, popularity) across all {N} nodes = {r:.3f}")
# among the top-1% most POPULAR, how many are also top-1% by degree?
pop_thr = np.sort(pop)[int(N*0.99)]
top_pop = set(np.where(pop >= pop_thr)[0])
overlap = len(top_pop & HUBS)
print(f"top-1% by popularity: {len(top_pop)} artists; of those, {overlap} are also top-1% by degree ({100*overlap//max(len(top_pop),1)}%)")
