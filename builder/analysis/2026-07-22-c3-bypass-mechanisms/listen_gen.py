"""Blind-listen generator (scoped P1: all-known, hub-targeted).

For each pair and each arm (V0, A additive, C naive waypoint), walk the policy
'at each step bypass the highest-hub_penalty interior artist with known', and
capture the path at snapshots. Emit blind tokens + a sealed mapping + hidden
PathMetrics. Nothing here is shipped; it reuses the running API's routing/metric
code and, later, its clip endpoint.
"""
import sys, hashlib, heapq, json, random
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
hp = store.hub_penalty
DELTA, SIM_GATE = 0.10, 0.70
SNAPSHOTS = [5, 10, 15, 20]


def base_cost(u, v, sim, avoid):
    return (cfg.w_sim*(1.0-float(sim)) + cfg.w_jump*abs(float(pop[u])-float(pop[v]))
            + cfg.w_avoid*avoid.get(v, 0.0) + cfg.w_hop)


def dij(source, target, hard, avoid, reward=None, w_reward=0.0):
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
            c = base_cost(u, v, sim, avoid)
            if reward:
                c = max(0.0, c - w_reward*reward.get(v, 0.0))
            nd = d + c
            if nd < dist.get(v, 1e18):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    p = [target]
    while p[-1] != source:
        p.append(prev[p[-1]])
    return p[::-1]


def sub_reward(known_ids, blocked):
    r = {}
    for K in known_ids:
        popK = float(pop[K])
        for v, s in store.neighbours_of(K):
            if popK - float(pop[v]) >= DELTA and v not in blocked and float(s) > r.get(v, 0.0):
                r[v] = float(s)
    return r


def route(arm, s, t, excludes):
    hard = {e.node for e in excludes} - {s, t}
    avoid = avoidance_map(store, [e.node for e in excludes if e.reason == DISLIKE], cfg)
    if arm == "V0":
        return find_path(store, s, t, excludes, cfg)
    known_ids = [e.node for e in excludes if e.reason == KNOWN]
    if arm == "A":
        return dij(s, t, hard, avoid, sub_reward(known_ids, hard | {s, t}), 1.0)
    if arm == "C":
        cous = {}
        for K in known_ids:
            popK = float(pop[K])
            for v, sc in store.neighbours_of(K):
                if popK-float(pop[v]) >= DELTA and float(sc) >= SIM_GATE and v not in (hard | {s, t}):
                    cous[v] = max(cous.get(v, 0.0), float(sc))
        if not cous:
            return dij(s, t, hard, avoid)
        vstar = max(cous, key=lambda v: cous[v])
        l1 = dij(s, vstar, hard, avoid); l2 = dij(vstar, t, hard, avoid)
        return l1 + l2[1:] if l1 and l2 else dij(s, t, hard, avoid)


def walk(arm, s, t, steps=20):
    """All-known hub-targeted policy. Returns {depth: path} at SNAPSHOTS."""
    excludes = []; snaps = {}
    for step in range(1, steps + 1):
        p = route(arm, s, t, excludes)
        if p is None:
            break
        interior = p[1:-1]
        if not interior:
            break
        victim = max(interior, key=lambda i: float(hp[i]))
        excludes.append(Exclusion(victim, KNOWN))
        if step in SNAPSHOTS:
            snaps[step] = route(arm, s, t, excludes)  # path AFTER this bypass
    return snaps


def nid(n):
    i = store.id_by_mbid.get(n) if n in store.id_by_mbid else None
    if i is None:
        for j, nm in enumerate(store.names):
            if nm.lower() == n.lower():
                return j
    return i


PAIRS = [
    ("pop-pop cross-genre", "Miles Davis", "Daft Punk"),
    ("pop-obscure (owner's trace pair)", "The Shins", "Wishbone Ash"),
    ("pop-pop distant", "Metallica", "Taylor Swift"),
]

rng = random.Random(20260722)
out = {"graph": EXPECT[:12], "snapshots": SNAPSHOTS, "pairs": []}
for label, a, b in PAIRS:
    s, t = nid(a), nid(b)
    if s is None or t is None:
        print(f"SKIP {label}: missing {a if s is None else b}")
        continue
    print(f"\n=== {label}: {name(s)}(pop{float(pop[s]):.2f}) -> {name(t)}(pop{float(pop[t]):.2f}) ===")
    arms = {}
    for arm in ("V0", "A", "C"):
        arms[arm] = walk(arm, s, t)
    # sanity print at depths 5/10/20
    for depth in [5, 10, 20]:
        print(f" depth {depth}:")
        for arm in ("V0", "A", "C"):
            p = arms[arm].get(depth)
            if p:
                m = path_metrics(store, p, HUBS)
                names = " -> ".join(name(i) for i in p)
                print(f"   {arm}: hubfr={m.hubfrac:.2f} pay={sum(1 for i in p[1:-1] if i not in HUBS)} len={len(p)} | {names}")
    # sealed blind mapping per (pair): shuffle arm->token
    tokens = ["X", "Y", "Z"]; rng.shuffle(tokens)
    mapping = dict(zip(("V0", "A", "C"), tokens))
    pair_rec = {"label": label, "from": name(s), "to": name(t),
                "mapping": mapping, "depths": {}}
    for depth in SNAPSHOTS:
        pair_rec["depths"][depth] = {}
        for arm in ("V0", "A", "C"):
            p = arms[arm].get(depth)
            if not p:
                continue
            m = path_metrics(store, p, HUBS)
            pair_rec["depths"][depth][mapping[arm]] = {
                "artists": [{"mbid": store.mbids[i], "name": name(i),
                             "pop": round(float(pop[i]), 3)} for i in p],
                "_hidden_metrics": {"hubfrac": round(m.hubfrac, 3),
                    "payload": sum(1 for i in p[1:-1] if i not in HUBS),
                    "length": len(p), "adamic_adar": round(m.adamic_adar, 3),
                    "overlap_coeff": round(m.overlap_coefficient, 3),
                    "mean_cn": round(m.mean_common_neighbours, 2),
                    "ceiling_hops": round(m.ceiling_hops, 3)}}
    out["pairs"].append(pair_rec)

BASE = r"C:\Users\charl\AppData\Local\Temp\claude\C--Users-charl-OneDrive-Claude-Projects-music-app\e36528b7-26df-4a5f-9b8a-4dd6f76d459c\scratchpad"

# PUBLIC (blinded): tokens + artist names/mbids only. NO mapping, NO metrics.
public = {"graph": out["graph"], "snapshots": SNAPSHOTS, "pairs": []}
for p in out["pairs"]:
    depths = {}
    for depth, arms in p["depths"].items():
        depths[depth] = {tok: {"artists": [{"mbid": a["mbid"], "name": a["name"]}
                                           for a in rec["artists"]]}
                         for tok, rec in arms.items()}
    public["pairs"].append({"label": p["label"], "from": p["from"], "to": p["to"],
                            "depths": depths})
import os
SERVE = BASE + r"\listen_serve"   # served dir: page + blinded data ONLY
os.makedirs(SERVE, exist_ok=True)
with open(SERVE + r"\listen_public.json", "w", encoding="utf-8") as f:
    json.dump(public, f, indent=1, ensure_ascii=False)

# SECRET (kept OUT of the served dir): mapping + hidden metrics, for un-blinding after.
with open(BASE + r"\listen_secret.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(f"\nwrote listen_public.json (blinded) + listen_secret.json ({len(out['pairs'])} pairs)")
