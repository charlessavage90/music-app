import sys, numpy as np
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore

store = GraphStore.load(r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch\graph-t15-capfix.bin")
deg = np.diff(store.offsets)
N = len(store.names)

def find(sub):
    return [j for j in range(N) if sub.lower() in store.names[j].lower()]

# 1. Radiohead present? Any name containing it?
print("=== name search 'radiohead' ===")
for j in find("radiohead"):
    print(f"  id{j}  '{store.names[j]}'  deg={int(deg[j])}  pop={float(store.popularity[j]):.2f}")
print("=== name search 'beatles' ===")
for j in find("beatles"):
    print(f"  id{j}  '{store.names[j]}'  deg={int(deg[j])}  pop={float(store.popularity[j]):.2f}")

# 2. The Beatles' actual neighbours
def dump(name):
    ids = [j for j in find(name) if store.names[j].lower() == name.lower()]
    if not ids:
        print(f"\n[{name}] exact match not found"); return
    i = ids[0]
    print(f"\n=== {store.names[i]} (id{i}) deg={int(deg[i])} pop={float(store.popularity[i]):.2f} — neighbours: ===")
    for v, s in store.neighbours_of(i):
        print(f"   {store.names[v]:<30} score={float(s):.3f} deg={int(deg[v])} pop={float(store.popularity[v]):.2f}")
dump("The Beatles")

# 3. What ARE the actual top-degree hubs?
print("\n=== top 25 by degree (the current 'hubs') ===")
order = np.argsort(-deg)[:25]
for j in order:
    print(f"   {store.names[j]:<30} deg={int(deg[j])} pop={float(store.popularity[j]):.2f}")

# 4. degree distribution sanity
print(f"\ndegree: min={int(deg.min())} median={int(np.median(deg))} mean={deg.mean():.1f} "
      f"p99={int(np.percentile(deg,99))} max={int(deg.max())}")
print(f"nodes with degree < 8: {int((deg<8).sum())} ({100*(deg<8).sum()//N}%)")
