"""Reconstruct the owner's bypass trace against the full graph."""
import sys, os
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..",
    "OneDrive", "Claude Projects", "music-app", "api", "src"))
# fallback absolute
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path, Exclusion, DISLIKE, KNOWN
from artistpath_api.config import ApiConfig
import numpy as np

GRAPH = r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch\graph-t15-capfix.bin"
store = GraphStore.load(GRAPH)
cfg = ApiConfig()
name = lambda i: store.names[i]
deg = np.diff(store.offsets)
hubp = store.hub_penalty

def rank_by_degree(node):
    # 1 = biggest hub
    return int((deg > deg[node]).sum()) + 1

def info(mbid):
    i = store.id_by_mbid.get(mbid)
    if i is None: return f"[NOT IN GRAPH {mbid}]"
    return f"{name(i)} (pop={store.popularity[i]:.3f} deg={int(deg[i])} hubP={hubp[i]:.2f} degRank#{rank_by_degree(i)})"

urls = [line.strip() for line in sys.stdin if line.strip()]

for n, url in enumerate(urls, 1):
    q = parse_qs(urlparse(url).query)
    path_part = urlparse(url).path.split("/path/")[1]
    src_m, tgt_m = path_part.split("/")
    src, tgt = store.id_by_mbid[src_m], store.id_by_mbid[tgt_m]
    dislikes = unquote(q.get("dislike", [""])[0]).split(",") if q.get("dislike") else []
    knowns = unquote(q.get("known", [""])[0]).split(",") if q.get("known") else []
    dislikes = [d for d in dislikes if d]
    knowns = [k for k in knowns if k]
    exc = []
    for d in dislikes:
        j = store.id_by_mbid.get(d)
        if j is not None: exc.append(Exclusion(j, DISLIKE))
    for k in knowns:
        j = store.id_by_mbid.get(k)
        if j is not None: exc.append(Exclusion(j, KNOWN))
    path = find_path(store, src, tgt, exc, cfg)
    print(f"\n=== URL {n}: {len(dislikes)} dislike, {len(knowns)} known ===")
    if path is None:
        print("  NO PATH")
    else:
        print(f"  len={len(path)}: " + " -> ".join(
            f"{name(i)}[deg{int(deg[i])}/hp{hubp[i]:.2f}]" for i in path))

# Adjacency question: Smiths <-> Shins
print("\n\n=== ADJACENCY CHECKS ===")
def find_id(substr):
    return [i for i in range(len(store.names)) if substr.lower() in store.names[i].lower()]
for label, sub in [("Smiths","the smiths"),("Shins","the shins")]:
    ids = find_id(sub)
    print(f"{label}: " + "; ".join(f"{store.names[i]}(id{i} deg{int(deg[i])})" for i in ids[:5]))

def edge_between(a, b):
    for v, s in store.neighbours_of(a):
        if v == b: return float(s)
    return None
smiths = [i for i in find_id("the smiths") if store.names[i].lower()=="the smiths"]
shins = [i for i in find_id("the shins") if store.names[i].lower()=="the shins"]
if smiths and shins:
    a, b = smiths[0], shins[0]
    print(f"Smiths(id{a}) -> Shins(id{b}) edge score: {edge_between(a,b)}")
    print(f"Shins(id{b}) -> Smiths(id{a}) edge score: {edge_between(b,a)}")
