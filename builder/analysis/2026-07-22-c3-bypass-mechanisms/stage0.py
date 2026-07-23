"""Stage 0 binding pre-check for the C3 bypass diagnostic.

Two questions, one script (protocol section 3):
  Q1  Does the `known` obscure-substitution discount BIND at all, or is it
      inert like w_floor? -> compare V0 vs V1 paths on the owner trace.
  Q2  Is the w_floor-deletion factor-table confound real? -> fraction of
      interior nodes with pop(v) < floor on the produced paths.

V0 = the real production find_path (ground truth).
V1 = same Dijkstra, w_floor term dropped, w_hub=0, plus the corrected
     throughput discount toward similar-but-more-obscure neighbours of each
     `known` node. My V1 Dijkstra is verified to reproduce V0 when the
     discount is off, so any V0<->V1 difference is the mechanism, not a
     reimplementation artifact.
"""
import sys, hashlib, heapq
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path, Exclusion, DISLIKE, KNOWN, avoidance_map
from artistpath_api.config import ApiConfig
import numpy as np

GRAPH = r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch\graph-t15-capfix.bin"
EXPECT_SHA = "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"

sha = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
assert sha == EXPECT_SHA, f"WRONG ARTIFACT: {sha}"
print(f"graph identity OK: {sha[:12]}...")

store = GraphStore.load(GRAPH)
cfg = ApiConfig()
pop = store.popularity
name = lambda i: store.names[i]


def sub_discount_map(known_ids, store, pop):
    """For each `known` K, its direct neighbours v with pop(v) < pop(K)
    become substitutes. d(v) = clip(sim(K,v)*(pop(K)-pop(v)), 0, 1), taking
    the max over all K a node qualifies under. K itself stays excluded."""
    sub = {}
    for K in known_ids:
        popK = float(pop[K])
        for v, s in store.neighbours_of(K):
            popv = float(pop[v])
            if popv < popK:
                d = max(0.0, min(1.0, float(s) * (popK - popv)))
                if d > sub.get(v, 0.0):
                    sub[v] = d
    return sub


def v1_dijkstra(store, source, target, excludes, cfg, sub, w_known):
    """Mirror of find_path. w_floor term DROPPED, w_hub=0 (default), plus a
    throughput discount: an edge's positive cost is scaled by
    (1 - w_known*0.5*(sub[u]+sub[v])), floored so cost stays > w_hop.
    With w_known=0 or empty `sub` this is identical to find_path."""
    if source == target:
        return [source]
    hard = {e.node for e in excludes} - {source, target}
    avoid = avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)
    dist = {source: 0.0}
    prev = {}
    pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_u = float(pop[u])
        su = sub.get(u, 0.0)
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            pop_v = float(pop[v])
            base = (cfg.w_sim * (1.0 - float(sim))
                    + cfg.w_jump * abs(pop_u - pop_v)
                    + cfg.w_avoid * avoid.get(v, 0.0))
            factor = 1.0 - min(w_known * 0.5 * (su + sub.get(v, 0.0)), 0.99)
            cost = base * factor + cfg.w_hop
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def parse_url(url):
    q = parse_qs(urlparse(url).query)
    src_m, tgt_m = urlparse(url).path.split("/path/")[1].split("/")
    def ids(key, reason):
        raw = unquote(q.get(key, [""])[0])
        out = []
        for m in (x for x in raw.split(",") if x):
            j = store.id_by_mbid.get(m)
            if j is not None:
                out.append(Exclusion(j, reason))
        return out
    return (store.id_by_mbid[src_m], store.id_by_mbid[tgt_m],
            ids("dislike", DISLIKE) + ids("known", KNOWN))


urls = [u.strip() for u in sys.stdin if u.strip()]

# --- self-check: V1 with discount OFF must equal find_path ---
print("\n[self-check] v1_dijkstra(w_known=0) == find_path ?")
ok = True
for u in urls:
    s, t, exc = parse_url(u)
    p0 = find_path(store, s, t, exc, cfg)
    p1 = v1_dijkstra(store, s, t, exc, cfg, {}, 0.0)
    same = p0 == p1
    ok = ok and same
    if not same:
        print(f"  MISMATCH on a state (len {len(p0)} vs {len(p1)})")
print(f"  {'PASS' if ok else 'FAIL'} - V1 reimplementation is faithful to V0\n")

def interior_below_floor(path, floor):
    interior = path[1:-1]
    below = [i for i in interior if float(pop[i]) < floor]
    return len(below), len(interior), below

print(f"{'state':<14}{'V0len':>6}{'V1@.5':>7}{'V1@.9':>7}{'same@.5':>9}{'same@.9':>9}"
      f"{'nsubs':>7}{'subsOnV1':>9}{'flr<V0':>8}{'flr<V1':>8}")
for n, u in enumerate(urls, 1):
    s, t, exc = parse_url(u)
    known_ids = [e.node for e in exc if e.reason == KNOWN]
    floor = min(float(pop[s]), float(pop[t]))
    sub = sub_discount_map(known_ids, store, pop)
    p0 = find_path(store, s, t, exc, cfg)
    p1a = v1_dijkstra(store, s, t, exc, cfg, sub, 0.5)
    p1b = v1_dijkstra(store, s, t, exc, cfg, sub, 0.9)
    same_a = p0 == p1a
    same_b = p0 == p1b
    subs_on_v1 = sum(1 for i in (p1b or [])[1:-1] if i in sub)
    b0, _, _ = interior_below_floor(p0, floor)
    b1, _, _ = interior_below_floor(p1b or p0, floor)
    lab = f"{len(exc)-len(known_ids)}d/{len(known_ids)}k"
    print(f"{lab:<14}{len(p0):>6}{len(p1a):>7}{len(p1b):>7}{str(same_a):>9}{str(same_b):>9}"
          f"{len(sub):>7}{subs_on_v1:>9}{b0:>8}{b1:>8}")

# detail on the most-bypassed state: show where V1@.9 diverges
print("\n--- most-bypassed state, V0 vs V1@0.9 paths ---")
s, t, exc = parse_url(urls[-1])
known_ids = [e.node for e in exc if e.reason == KNOWN]
sub = sub_discount_map(known_ids, store, pop)
p0 = find_path(store, s, t, exc, cfg)
p1 = v1_dijkstra(store, s, t, exc, cfg, sub, 0.9)
mark = lambda i: f"{name(i)}[pop{float(pop[i]):.2f}{'*SUB' if i in sub else ''}]"
print("V0:", " -> ".join(mark(i) for i in p0))
print("V1:", " -> ".join(mark(i) for i in p1))
print(f"\nsubstitute pool size: {len(sub)}  "
      f"max d: {max(sub.values()) if sub else 0:.3f}  "
      f"mean d: {np.mean(list(sub.values())) if sub else 0:.3f}")
