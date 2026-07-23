"""Stage 0 v3 - route-aware waypoint selection.

Naive C picked the single globally-highest-sim cousin (Cat Power for every
state), which sat well on the high-bypass path but forced incoherent detours
on the easy states. Fix: pick the qualifying obscure cousin cheapest to route
THROUGH -- run Dijkstra distances from both endpoints once, choose the cousin
minimising dist_source[v] + dist_target[v] among quality substitutes. So the
waypoint lands on the natural path instead of dragging it sideways.
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
assert hashlib.sha256(open(GRAPH, "rb").read()).hexdigest() == EXPECT
store = GraphStore.load(GRAPH)
cfg = ApiConfig(); pop = store.popularity; name = lambda i: store.names[i]
HUBS = hub_node_set(store, 0.01)
DELTA = 0.10       # min pop drop to qualify as a substitute
SIM_GATE = 0.70    # min similarity to K to be a quality substitute


def base_cost(u, v, sim, avoid):
    return (cfg.w_sim * (1.0 - float(sim)) + cfg.w_jump * abs(float(pop[u]) - float(pop[v]))
            + cfg.w_avoid * avoid.get(v, 0.0) + cfg.w_hop)


def dijkstra(source, target, hard, avoid):
    if source == target:
        return [source]
    dist = {source: 0.0}; prev = {}; pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, 1e18):
            continue
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            nd = d + base_cost(u, v, sim, avoid)
            if nd < dist.get(v, 1e18):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    p = [target]
    while p[-1] != source:
        p.append(prev[p[-1]])
    return p[::-1]


def sssp(source, hard, avoid):
    dist = {source: 0.0}; pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e18):
            continue
        for v, sim in store.neighbours_of(u):
            if v in hard:
                continue
            nd = d + base_cost(u, v, sim, avoid)
            if nd < dist.get(v, 1e18):
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return dist


def quality_cousins(known_ids, blocked):
    c = {}
    for K in known_ids:
        popK = float(pop[K])
        for v, s in store.neighbours_of(K):
            if popK - float(pop[v]) >= DELTA and float(s) >= SIM_GATE and v not in blocked:
                c[v] = max(c.get(v, 0.0), float(s))
    return c


def waypoint_routeaware(source, target, excludes, known_ids):
    hard = {e.node for e in excludes} - {source, target}
    avoid = avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)
    cousins = quality_cousins(known_ids, hard | {source, target})
    if not cousins:
        return dijkstra(source, target, hard, avoid), None
    ds = sssp(source, hard, avoid)
    dt = sssp(target, hard, avoid)
    reachable = [(ds[v] + dt[v], v) for v in cousins if v in ds and v in dt]
    if not reachable:
        return dijkstra(source, target, hard, avoid), None
    _, vstar = min(reachable)
    l1 = dijkstra(source, vstar, hard, avoid)
    l2 = dijkstra(vstar, target, hard, avoid)
    if l1 is None or l2 is None:
        return dijkstra(source, target, hard, avoid), None
    return l1 + l2[1:], vstar


def waypoint_naive(source, target, excludes, known_ids):
    hard = {e.node for e in excludes} - {source, target}
    avoid = avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)
    cousins = quality_cousins(known_ids, hard | {source, target})
    if not cousins:
        return dijkstra(source, target, hard, avoid), None
    vstar = max(cousins, key=lambda v: cousins[v])   # global best sim
    l1 = dijkstra(source, vstar, hard, avoid); l2 = dijkstra(vstar, target, hard, avoid)
    return (l1 + l2[1:], vstar) if l1 and l2 else (dijkstra(source, target, hard, avoid), None)


def parse_url(url):
    q = parse_qs(urlparse(url).query)
    sm, tm = urlparse(url).path.split("/path/")[1].split("/")
    def ids(k, r):
        return [Exclusion(store.id_by_mbid[m], r)
                for m in (x for x in unquote(q.get(k, [""])[0]).split(",") if x)
                if m in store.id_by_mbid]
    return store.id_by_mbid[sm], store.id_by_mbid[tm], ids("dislike", DISLIKE) + ids("known", KNOWN)


def rowm(tag, path, p0):
    m = path_metrics(store, path, HUBS)
    print(f"  {tag:<16}{m.length:>4}{'-' if path==p0 else 'DIFF':>6}{m.ceiling_hops:>8.2f}"
          f"{m.mean_interior_pop:>8.2f}{m.hubfrac:>8.2f}{m.adamic_adar:>8.3f}"
          f"{m.overlap_coefficient:>8.3f}{m.mean_common_neighbours:>8.2f}")


for n, u in enumerate([x.strip() for x in sys.stdin if x.strip()], 1):
    s, t, exc = parse_url(u)
    known_ids = [e.node for e in exc if e.reason == KNOWN]
    p0 = find_path(store, s, t, exc, cfg)
    pcn, vn = waypoint_naive(s, t, exc, known_ids)
    pcr, vr = waypoint_routeaware(s, t, exc, known_ids)
    lab = f"{len(exc)-len(known_ids)}d/{len(known_ids)}k"
    print(f"state {n} [{lab}]  naive v*={name(vn) if vn else '-'}  routeaware v*={name(vr) if vr else '-'}")
    print(f"  {'form':<16}{'len':>4}{'vsV0':>6}{'ceilHp':>8}{'mPop':>8}{'hubfr':>8}{'AA':>8}{'OC':>8}{'meanCN':>8}")
    rowm("V0", p0, p0)
    rowm("C naive", pcn, p0)
    rowm("C routeaware", pcr, p0)
    if n == 3:
        mk = lambda i: f"{name(i)}[{float(pop[i]):.2f}]"
        print("   route-aware path:", " -> ".join(mk(i) for i in pcr))
    print()
