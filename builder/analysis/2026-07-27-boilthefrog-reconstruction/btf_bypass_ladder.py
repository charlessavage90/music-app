"""Does BoilTheFrog's bypass make paths progressively MORE OBSCURE?

WHAT-GOOD-LOOKS-LIKE value 2 says bypass should "progressively lengthen the path
AND increase novelty -- both, or neither counts", and names boilthefrog as the
reference product. Value 9 says "the more bypasses, the more obscure the path
becomes". This tests that against the reference product's actual code.

Faithful to new_crawler/artist_graph.py::path:
    weight(u,v) = 10000 if u in skipset or v in skipset else base
    base(u,v)   = 1 + pop_weight * |pop_u - pop_v| / 100.0
    (base is stored per-edge at build time from the SOURCE's perspective; the
     undirected graph keeps whichever was written -- we recompute symmetrically,
     which is identical since |pop_u - pop_v| is symmetric)

SIMULATION, not the live app. The user's click is modelled two ways:
  'known-like'  -- bypass the most POPULAR interior artist (you know them)
  'random'      -- bypass a uniformly random interior artist
"""

import heapq
import random
import statistics
from collections import defaultdict

import btf_graph_measure as M


def build_graph():
    artist_bl, edge_bl = M.load_blacklist()
    popularity, names = M.load_nodes()
    edge_lists = M.load_edges()
    adj = defaultdict(set)
    nodes = set()
    for node, raw in edge_lists.items():
        if node in artist_bl or popularity.get(node, 0) < M.MIN_POPULARITY:
            continue
        nodes.add(node)
        good = [e for e in raw
                if e not in artist_bl and e not in edge_bl[node]
                and popularity.get(e, 0) >= M.MIN_POPULARITY]
        pop = popularity[node]
        weighted = sorted(
            (1 + M.POP_WEIGHT * abs(pop - popularity[e]) / 100.0, e) for e in good)
        for _, t in weighted[:M.MAX_EDGES_PER_ARTIST]:
            nodes.add(t)
            adj[node].add(t)
            adj[t].add(node)
    for n in nodes:
        adj.setdefault(n, set())
    return adj, popularity, names


def base_w(u, v, popularity):
    return 1 + M.POP_WEIGHT * abs(popularity.get(u, 0) - popularity.get(v, 0)) / 100.0


def dijkstra(adj, popularity, src, dst, skipset):
    dist = {src: 0.0}
    prev = {}
    pq = [(0.0, src)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        if u == dst:
            break
        for v in adj[u]:
            w = 10000.0 if (u in skipset or v in skipset) else base_w(u, v, popularity)
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dst not in dist:
        return None
    path, cur = [], dst
    while cur != src:
        path.append(cur)
        cur = prev[cur]
    path.append(src)
    path.reverse()
    return path


def find(names, want):
    want_l = want.lower()
    for aid, n in names.items():
        if n.lower() == want_l:
            return aid
    return None


def interior_stats(path, popularity):
    interior = path[1:-1]
    if not interior:
        return None
    pops = [popularity.get(a, 0) for a in interior]
    return {
        "len": len(path),
        "n_int": len(interior),
        "min": min(pops),
        "mean": statistics.mean(pops),
        "median": statistics.median(pops),
    }


def ladder(adj, popularity, names, a, b, presses, mode, seed=0):
    rng = random.Random(seed)
    src, dst = find(names, a), find(names, b)
    if src is None or dst is None or src not in adj or dst not in adj:
        print(f"  !! endpoint missing: {a}={src} {b}={dst}")
        return
    skipset = set()
    rows = []
    for i in range(presses + 1):
        p = dijkstra(adj, popularity, src, dst, skipset)
        if p is None:
            rows.append((i, None))
            break
        st = interior_stats(p, popularity)
        rows.append((i, st))
        interior = p[1:-1]
        if not interior:
            break
        if mode == "known-like":
            pick = max(interior, key=lambda x: popularity.get(x, 0))
        else:
            pick = rng.choice(interior)
        skipset.add(pick)

    print(f"\n  {a} -> {b}   [{mode}]  "
          f"(pop {popularity.get(src,0)} -> {popularity.get(dst,0)})")
    print(f"  {'press':>5} {'cards':>5} {'min pop':>8} {'med pop':>8} {'mean pop':>9}")
    for i, st in rows:
        if st is None:
            print(f"  {i:>5}   NO PATH")
            break
        print(f"  {i:>5} {st['len']:>5} {st['min']:>8} {st['median']:>8.1f} "
              f"{st['mean']:>9.2f}")
    ok = [r for _, r in rows if r]
    if len(ok) > 1:
        print(f"    -> cards {ok[0]['len']} to {ok[-1]['len']}   "
              f"min-pop {ok[0]['min']} to {ok[-1]['min']}   "
              f"mean-pop {ok[0]['mean']:.1f} to {ok[-1]['mean']:.1f}")


def main():
    adj, popularity, names = build_graph()
    print(f"graph: {len(adj):,} nodes\n")
    print("=" * 74)
    print("BYPASS LADDER -- 12 presses per pair")
    print("=" * 74)

    pairs = [
        ("Bob Dylan", "Metallica"),      # artistpath's own BYP-run pair
        ("Miley Cyrus", "Miles Davis"),  # plamere's headline example
        ("Weezer", "Lady Gaga"),         # the app's default
        ("Kenny G", "Cannibal Corpse"),  # plamere's "perverse" example
    ]
    for a, b in pairs:
        for mode in ("known-like", "random"):
            ladder(adj, popularity, names, a, b, 12, mode)


if __name__ == "__main__":
    main()
