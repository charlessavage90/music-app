"""Each press lowers a fame band for the middle of the journey one tier, keeps the journey about as long as the first one, and stays close to the previous journey.

EXPLORATORY (r2-tiers). Today's Dijkstra (similarity + fame-cliff + hop cost per edge) plus a
per-artist charge:
  * band: press k sets a ceiling c(k) = G + (1-G)*rho[k] and a floor b(k) = max(c(k)-W, G-gdrop),
    where G is the pair's "home" fame level (famous pairs ~0.5, mid pairs near their endpoints).
    Artists above the ceiling pay w_above per 10 points (steep); below the floor pay w_below per
    10 points (gentle). Near a famous endpoint the ceiling relaxes: at hop distance d from an
    endpoint, the ceiling is at least endpoint_fame - step*(d-1) (journey-shaped, r1-rules).
  * continuity: artists not in the previous journey pay c_new; neighbours of it pay c_adj;
    artists in it pay nothing (pressed ones are excluded outright).
  * optional scene: the pressed artist's less famous neighbours count as "in the journey".
From press 1 the journey is found by a layered search that holds its length between the press-0
length and that plus `slack` (r1-outside's fixed-length idea), so the charges cannot be dodged by
cutting stops; falls back to plain Dijkstra with the same charges.
Settings via env R2 (JSON) for sweeping; finalist files bake them in.
"""
import heapq
import json
import os
from collections import deque

import numpy as np

P = dict(
    rho=[1.0, 0.95, 0.85, 0.72, 0.58, 0.45, 0.35, 0.27, 0.20, 0.14, 0.10],
    g_slope=0.5,       # home level G = mean endpoint fame - g_slope*mean^2 (famous 0.5, mid ~0.3-0.4)
    W=0.30, gdrop=0.10,
    w_above=1.0, above_pow=1.0, w_below=0.2,
    step=0.10, bfs_depth=4, bfs_sim=0.0,
    c_new=0.3, c_adj=0.15, adj_sim=0.5,
    scene=0, keep_floor=0, keep_ramp=0,
    gamma=1.0,         # above-band charge multiplier for artists kept from the previous journey
    min_sim=0.0,
    slack=2, shrink=0,       # no step weaker than this after press 0 (falls back to no floor if no route)
)
P.update(json.loads(os.environ.get("R2", "{}")))


def setup(ctx):
    if hasattr(ctx, "r2tiers_T"):
        return
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = len(off) - 1
    src = np.repeat(np.arange(n), np.diff(off))
    pop = np.asarray(st.pop_raw, dtype=np.float64)
    cfg = ctx.cfg
    static = cfg.w_sim * (1 - sc) + cfg.w_jump * np.abs(pop[src] - pop[nbr]) + cfg.w_hop
    # layered search runs over edges u->v stored at v's row: owner = v, nbr = u (map is symmetric)
    ctx.r2tiers_T = dict(off=off.tolist(), nbr=nbr.tolist(), sc=sc.tolist(), A=static.tolist(), n=n,
                 pop=pop, fame=np.asarray(ctx.pctl, dtype=np.float64),
                 owner=src, nbr_a=nbr, off_a=off, sc_a=sc,
                 static=cfg.w_sim * (1 - sc) + cfg.w_jump * np.abs(pop[nbr] - pop[src]) + cfg.w_hop,
                 L0={})


def home(fs, ft):
    m = (fs + ft) / 2
    return m - P["g_slope"] * m * m


def ceiling(k, G):
    rho = P["rho"][min(k, len(P["rho"]) - 1)]
    return G + (1 - G) * rho


def bfs(T, s, depth, minsim):
    off, nbr, sc = T["off"], T["nbr"], T["sc"]
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        if d[u] >= depth:
            continue
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v not in d and sc[j] >= minsim:
                d[v] = d[u] + 1
                q.append(v)
    return d


def node_costs(ctx, s, t, pressed, prev):
    T = ctx.r2tiers_T
    k = len(pressed)
    fame = T["fame"]
    n = T["n"]
    nc = np.zeros(n)
    if k == 0:  # press 0 = today's journey (today's floor; the ramp is 0 at k=0)
        cfg = ctx.cfg
        base = min(T["pop"][s], T["pop"][t])
        return cfg.w_floor * np.maximum(0.0, base - T["pop"])
    fs, ft = fame[s], fame[t]
    G = home(fs, ft)
    c = ceiling(k, G)
    ceil_v = np.full(n, c)
    for e, fe in ((s, fs), (t, ft)):
        if fe <= c:
            continue
        for v, d in bfs(T, e, P["bfs_depth"], P["bfs_sim"]).items():
            allow = fe - P["step"] * (d - 1)
            if allow > ceil_v[v]:
                ceil_v[v] = allow
    b = max(c - P["W"], G - P["gdrop"])
    above = P["w_above"] * (np.maximum(0.0, fame - ceil_v) / 0.1) ** P["above_pow"]
    if prev and P["gamma"] != 1.0:
        kept = [v for v in prev[1:-1] if v not in set(pressed)]
        above[kept] *= P["gamma"]
    nc += above
    nc += P["w_below"] * np.maximum(0.0, b - fame) / 0.1
    if P["keep_floor"]:
        cfg = ctx.cfg
        base = min(T["pop"][s], T["pop"][t])
        nc += cfg.w_floor * np.maximum(0.0, max(0.0, base - cfg.floor_relax_known * k) - T["pop"])
    if P["keep_ramp"]:
        nc += ctx.cfg.w_known_ramp_fame_pctl * k * fame
    if prev and (P["c_new"] or P["c_adj"]):
        cont = np.full(n, P["c_new"])
        off, nbr, sc = T["off"], T["nbr"], T["sc"]
        keep = [v for v in prev[1:-1] if v not in set(pressed)]
        anchors = keep + [prev[0], prev[-1]]
        if P["scene"]:
            x = pressed[-1]
            for j in range(off[x], off[x + 1]):
                if fame[nbr[j]] < fame[x] and sc[j] >= P["adj_sim"]:
                    keep.append(nbr[j])
        for u in anchors:
            for j in range(off[u], off[u + 1]):
                if sc[j] >= P["adj_sim"]:
                    cont[nbr[j]] = min(cont[nbr[j]], P["c_adj"])
        cont[keep] = 0.0
        nc += cont
    return nc


def dijkstra(T, s, t, nc, hard, banned=None, min_sim=0.0):
    if s == t:
        return [s]
    off, nbr, A, sc = T["off"], T["nbr"], T["A"], T["sc"]
    hard = set(hard) - {s, t}
    dist = {s: 0.0}
    prv = {}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            break
        if d > dist.get(u, 1e18):
            continue
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard or (banned is not None and (u, v) in banned):
                continue
            if sc[j] < min_sim and v != t and u != s:
                continue
            nd = d + A[j] + (0.0 if v == t else nc[v])
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prv[v] = u
                heapq.heappush(pq, (nd, v))
    if t not in prv:
        return None
    p = [t]
    while p[-1] != s:
        p.append(prv[p[-1]])
    return p[::-1]


def exact_hops(ctx, s, t, hard, node_cost, hmin, hmax, min_sim=0.0):
    # copied from r1-outside/fixedlen.py (vectorised layered search, no immediate back-steps)
    """Min-cost s->t NON-BACKTRACKING walk with exactly h hops, h in [hmin, hmax] (top-2 labels per
    node so u->v may not use the label that came from v). Returns the cheapest walk that is a
    simple path, else None."""
    n = ctx.r2tiers_T["n"]
    owner, nbr, off = ctx.r2tiers_T["owner"], ctx.r2tiers_T["nbr_a"], ctx.r2tiers_T["off_a"]
    ecost = ctx.r2tiers_T["static"] + node_cost[owner]
    if min_sim > 0:
        ecost = np.where(ctx.r2tiers_T["sc_a"] < min_sim, np.inf, ecost)
    d1 = np.full(n, np.inf); d1[s] = 0.0
    d2 = np.full(n, np.inf)
    p1 = np.full(n, -1, dtype=np.int64); p2 = np.full(n, -1, dtype=np.int64)
    blocked = np.zeros(n, bool)
    if hard:
        blocked[list(hard)] = True
    blocked[s] = True
    layers = [(d1, d2, p1, p2)]
    best = []
    starts = off[:-1]
    for h in range(1, hmax + 1):
        use2 = p1[nbr] == owner
        cand = np.where(use2, d2[nbr], d1[nbr]) + ecost
        m1 = np.minimum.reduceat(cand, starts)
        hit = np.flatnonzero(cand == m1[owner])
        own = owner[hit]
        first = np.unique(own, return_index=True)[1]
        a1 = np.full(n, -1, dtype=np.int64); a1[own[first]] = hit[first]
        cand2 = cand.copy(); cand2[a1[a1 >= 0]] = np.inf
        m2 = np.minimum.reduceat(cand2, starts)
        hit2 = np.flatnonzero((cand2 == m2[owner]) & np.isfinite(cand2))
        own2 = owner[hit2]
        first2 = np.unique(own2, return_index=True)[1]
        a2 = np.full(n, -1, dtype=np.int64); a2[own2[first2]] = hit2[first2]
        nd1, nd2 = m1.copy(), m2.copy()
        np1 = np.where(a1 >= 0, nbr[np.maximum(a1, 0)], -1)
        np2 = np.where(a2 >= 0, nbr[np.maximum(a2, 0)], -1)
        if h >= hmin and np.isfinite(nd1[t]):
            best.append((float(nd1[t]), h))
        for arr in (nd1, nd2):
            arr[blocked] = np.inf
            arr[t] = np.inf
        layers.append((nd1, nd2, np1, np2))
        d1, d2, p1, p2 = nd1, nd2, np1, np2
    for cost, h in sorted(best):
        p = [t]; slot = 1
        for layer in range(h, 0, -1):
            _, _, lp1, lp2 = layers[layer]
            u = int(lp1[p[-1]] if slot == 1 else lp2[p[-1]])
            if u < 0:
                break
            prev_p1 = layers[layer - 1][2]
            slot = 2 if prev_p1[u] == p[-1] else 1
            p.append(u)
        p = p[::-1]
        if p[0] == s and len(set(p)) == len(p):
            return p
    return None



def journey_dijkstra(ctx, s, t, pressed, nc):
    T = ctx.r2tiers_T
    ms = P["min_sim"] if pressed else 0.0
    for m in ((ms, 0.0) if ms else (0.0,)):
        p = dijkstra(T, s, t, nc, pressed, min_sim=m)
        if p is None:
            continue
        if len(p) != 2:
            return p
        d = dijkstra(T, s, t, nc, pressed, banned={(s, t), (t, s)}, min_sim=m)
        return d if d is not None else p
    return None


def journey(ctx, s, t, pressed, prev):
    setup(ctx)
    T = ctx.r2tiers_T
    ncv = node_costs(ctx, s, t, pressed, prev)
    if not pressed:
        p = journey_dijkstra(ctx, s, t, [], ncv.tolist())
        if p:
            T["L0"][(s, t)] = len(p) - 1
        return p
    L0 = T["L0"].get((s, t))
    if L0 is None:
        p0 = journey_dijkstra(ctx, s, t, [], node_costs(ctx, s, t, [], None).tolist())
        L0 = T["L0"][(s, t)] = len(p0) - 1 if p0 else 2
    lo = max(2, L0 - P["shrink"])
    ncv = ncv.copy()
    ncv[t] = 0.0
    hard = set(pressed) - {s, t}
    p = exact_hops(ctx, s, t, hard, ncv, lo, max(2, L0) + P["slack"], P["min_sim"])
    if p is None and P["min_sim"] > 0:
        p = exact_hops(ctx, s, t, hard, ncv, lo, max(2, L0) + P["slack"])
    if p is None:
        p = journey_dijkstra(ctx, s, t, pressed, ncv.tolist())
    return p


def _unused(ctx, s, t, pressed, prev):
    setup(ctx)
    T = ctx.r2tiers_T
    nc = node_costs(ctx, s, t, pressed, prev).tolist()
    ms = P["min_sim"] if pressed else 0.0
    for m in ((ms, 0.0) if ms else (0.0,)):
        p = dijkstra(T, s, t, nc, pressed, min_sim=m)
        if p is None:
            continue
        if len(p) != 2:
            return p
        d = dijkstra(T, s, t, nc, pressed, banned={(s, t), (t, s)}, min_sim=m)
        return d if d is not None else p
    return None
