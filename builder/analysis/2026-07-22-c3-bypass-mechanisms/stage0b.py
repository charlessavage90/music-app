"""Stage 0 v2 - test BOTH redesigned `known` mechanisms (owner chose 'build
both, Stage 0 decides'). The multiplicative discount is dead (wrong shape:
cannot beat near-zero-cost ceiling hub hops). Two candidates:

  Form A - additive bounded node reward, cap lets edge cost reach 0.
           Selection DECOUPLED from sim*dpop: qualify on a pop-drop gate,
           reward proportional to sim(K,v) alone (fresh review Q4/finding 4).
  Form C - hard waypoint: route source -> best obscure cousin -> target.
           Binds by construction.

Reads: binding (differs from V0?), interior-below-floor (does the floor term
reactivate -> two-knob confound, review finding 3), and a coherence read via
the shipped path_metrics (AA + overlap-coeff + mean_common_neighbours, the
degree-independent backstop from review finding 5).
"""
import sys, hashlib, heapq
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0, r"C:\Users\charl\OneDrive\Claude Projects\music-app\api\src")
from artistpath_api.graph_store import GraphStore
from artistpath_api.pathfinding import find_path, Exclusion, DISLIKE, KNOWN, avoidance_map
from artistpath_api.config import ApiConfig
from artistpath_api.evaluation import path_metrics, hub_node_set

GRAPH = r"C:\Users\charl\OneDrive\Claude Projects\music-app\builder\scratch\graph-t15-capfix.bin"
EXPECT = "c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237"
assert hashlib.sha256(open(GRAPH, "rb").read()).hexdigest() == EXPECT, "WRONG ARTIFACT"
print(f"graph identity OK: {EXPECT[:12]}...")

store = GraphStore.load(GRAPH)
cfg = ApiConfig()
pop = store.popularity
name = lambda i: store.names[i]
HUBS = hub_node_set(store, 0.01)   # frozen top-1% degree set
DELTA = 0.10                        # min pop drop for a node to qualify as a substitute


def substitute_reward(known_ids):
    """v qualifies if some known K has it as a direct neighbour >= DELTA more
    obscure. reward[v] = max sim(K,v) over such K. Reward is pure similarity;
    the pop drop is only a GATE (decoupled from the product - review finding 4)."""
    r = {}
    for K in known_ids:
        popK = float(pop[K])
        for v, s in store.neighbours_of(K):
            if popK - float(pop[v]) >= DELTA:
                if float(s) > r.get(v, 0.0):
                    r[v] = float(s)
    return r


def dijkstra(store, source, target, excludes, cfg, reward, w_reward):
    """V0-equivalent base (w_floor term dropped, w_hub=0) plus an ADDITIVE node
    reward: cost = max(0, base + w_hop - w_reward*reward[v]). Cost can reach 0
    (Dijkstra needs >=0, not >w_hop - review finding 2). reward={} -> find_path."""
    if source == target:
        return [source]
    hard = {e.node for e in excludes} - {source, target}
    avoid = avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)
    dist = {source: 0.0}; prev = {}; pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_u = float(pop[u])
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            base = (cfg.w_sim * (1.0 - float(sim))
                    + cfg.w_jump * abs(pop_u - float(pop[v]))
                    + cfg.w_avoid * avoid.get(v, 0.0))
            cost = max(0.0, base + cfg.w_hop - w_reward * reward.get(v, 0.0))
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def waypoint_path(store, source, target, excludes, cfg, known_ids):
    """Form C: route source -> v* -> target through the best obscure cousin.
    v* = argmax sim(K,v) over qualifying (K,v). Legs use the no-reward base."""
    best_v, best_s = None, -1.0
    for K in known_ids:
        popK = float(pop[K])
        for v, s in store.neighbours_of(K):
            if popK - float(pop[v]) >= DELTA and float(s) > best_s:
                if v not in ({e.node for e in excludes} | {source, target}):
                    best_v, best_s = v, float(s)
    if best_v is None:
        return dijkstra(store, source, target, excludes, cfg, {}, 0.0), None
    leg1 = dijkstra(store, source, best_v, excludes, cfg, {}, 0.0)
    leg2 = dijkstra(store, best_v, target, excludes, cfg, {}, 0.0)
    if leg1 is None or leg2 is None:
        return None, best_v
    return leg1 + leg2[1:], best_v


def parse_url(url):
    q = parse_qs(urlparse(url).query)
    src_m, tgt_m = urlparse(url).path.split("/path/")[1].split("/")
    def ids(key, reason):
        out = []
        for m in (x for x in unquote(q.get(key, [""])[0]).split(",") if x):
            j = store.id_by_mbid.get(m)
            if j is not None:
                out.append(Exclusion(j, reason))
        return out
    return (store.id_by_mbid[src_m], store.id_by_mbid[tgt_m],
            ids("dislike", DISLIKE) + ids("known", KNOWN))


urls = [u.strip() for u in sys.stdin if u.strip()]

# self-check: additive reward OFF must equal production find_path
ok = all(find_path(store, *parse_url(u)[:2], parse_url(u)[2], cfg)
         == dijkstra(store, *parse_url(u)[:2], parse_url(u)[2], cfg, {}, 0.0)
         for u in urls)
print(f"[self-check] dijkstra(reward off) == find_path: {'PASS' if ok else 'FAIL'}\n")


def below_floor(path, floor):
    return sum(1 for i in path[1:-1] if float(pop[i]) < floor)


def row(tag, path, floor, p0):
    m = path_metrics(store, path, HUBS)
    diff = "-" if path == p0 else "DIFF"
    print(f"  {tag:<14}{m.length:>4}{diff:>6}{below_floor(path, floor):>7}"
          f"{m.ceiling_hops:>8.2f}{m.mean_interior_pop:>8.2f}{m.hubfrac:>8.2f}"
          f"{m.adamic_adar:>8.3f}{m.overlap_coefficient:>8.3f}{m.mean_common_neighbours:>8.2f}")


for n, u in enumerate(urls, 1):
    s, t, exc = parse_url(u)
    known_ids = [e.node for e in exc if e.reason == KNOWN]
    floor = min(float(pop[s]), float(pop[t]))
    reward = substitute_reward(known_ids)
    p0 = find_path(store, s, t, exc, cfg)
    pA5 = dijkstra(store, s, t, exc, cfg, reward, 0.5)
    pA10 = dijkstra(store, s, t, exc, cfg, reward, 1.0)
    pC, vstar = waypoint_path(store, s, t, exc, cfg, known_ids)
    lab = f"{len(exc)-len(known_ids)}d/{len(known_ids)}k"
    print(f"state {n} [{lab}] floor={floor:.2f} rewardPool={len(reward)}"
          f"{' waypoint=' + name(vstar) if vstar else ''}")
    print(f"  {'form':<14}{'len':>4}{'vsV0':>6}{'<flr':>7}{'ceilHp':>8}"
          f"{'mPop':>8}{'hubfr':>8}{'AA':>8}{'OC':>8}{'meanCN':>8}")
    row("V0", p0, floor, p0)
    row("A additive.5", pA5, floor, p0)
    row("A additive1.0", pA10, floor, p0)
    row("C waypoint", pC, floor, p0)
    print()

# paths on the most-bypassed state
s, t, exc = parse_url(urls[-1])
known_ids = [e.node for e in exc if e.reason == KNOWN]
reward = substitute_reward(known_ids)
mark = lambda i: f"{name(i)}[{float(pop[i]):.2f}{'+R' if i in reward else ''}]"
print("--- most-bypassed state, paths ---")
for tag, p in [("V0", find_path(store, s, t, exc, cfg)),
               ("A@1.0", dijkstra(store, s, t, exc, cfg, reward, 1.0)),
               ("C", waypoint_path(store, s, t, exc, cfg, known_ids)[0])]:
    print(f"{tag:<7}", " -> ".join(mark(i) for i in p))
