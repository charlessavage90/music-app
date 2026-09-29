"""Each press moves the middle of the journey one step down a ladder of fame levels set by how famous your two artists are, keeping the parts of the journey that already fit.

EXPLORATORY (r2-tiers). Today's Dijkstra (similarity + fame-cliff + hop cost per edge) plus a
per-artist charge:
  * band: press k sets a ceiling c(k) = G + (1-G)*rho[k] and a floor b(k) = max(c(k)-W, G-gdrop),
    where G is the pair's "home" fame level (famous pairs ~0.5, mid pairs near their endpoints).
    Artists above the ceiling pay w_above per 10 points (steep); below the floor pay w_below per
    10 points (gentle). The artists right next to an endpoint get a relaxed ceiling: the endpoint's own fame
    brought down the same number of tiers, or the fame of the endpoint's 3rd least famous
    neighbour if that is higher (a star whose every neighbour is famous can still be left).
    From press 1 no step may be weaker than similarity 0.7 (dropped if no journey exists then).
    Home level here: G = m - 0.5*m^3, m = mean endpoint fame (famous pairs ~0.5, mid pairs just
    under their endpoints). Kept artists pay only 30 % of the above-band charge.
  * continuity: artists not in the previous journey pay c_new; neighbours of it pay c_adj;
    artists in it pay nothing (pressed ones are excluded outright).
  * optional scene: the pressed artist's less famous neighbours count as "in the journey".
Finalist from exploration/r2-tiers (rated kit run t23R); settings baked in, no env vars.
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
    near_pow=0.0,
    avail_q=-1,        # >=0: next to an endpoint, allow at least the fame of its (avail_q+1)-th least famous
                       #      unpressed neighbour (so a star whose every neighbour is famous can still be left)
    near_disc=0.0,
    e_keep=1.0,        # step cost multiplier for a step the previous journey already took (0 = free)     # artists let in only by the avail_q allowance still pay this share of the full charge
    g_pow=2,           # home level G = m - g_slope*m^g_pow (m = mean endpoint fame)      # >0: the allowance next to an endpoint also descends, as G + (fe-G)*rho^near_pow
    c_new=0.3, c_adj=0.15, adj_sim=0.5,
    scene=0, keep_floor=0, keep_ramp=0,
    gamma=1.0,         # above-band charge multiplier for artists kept from the previous journey
    min_sim=0.0,
    min_len=0,         # >0: if the journey would have fewer than (press-0 length - min_len) cards, re-route
                       #     with a hop-counting search that forbids that (never shorter than that)       # no step weaker than this after press 0 (falls back to no floor if no route)
)
P.update({"bfs_depth": 1, "w_above": 3, "min_sim": 0.7, "near_pow": 1.0, "rho": [1, 0.9, 0.75, 0.6, 0.48, 0.38, 0.3, 0.23, 0.17, 0.12, 0.08], "avail_q": 2, "g_pow": 3, "w_below": 0.5, "gamma": 0.3, "c_new": 0.3, "c_adj": 0.15})


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
    ctx.r2tiers_T = dict(off=off.tolist(), nbr=nbr.tolist(), sc=sc.tolist(), A=static.tolist(), n=n,
                 pop=pop, fame=np.asarray(ctx.pctl, dtype=np.float64))


def home(fs, ft):
    m = (fs + ft) / 2
    return m - P["g_slope"] * m ** P["g_pow"]


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
    ceil_s = np.full(n, c)  # same without the avail_q allowance
    rho = P["rho"][min(k, len(P["rho"]) - 1)]
    for e, fe in ((s, fs), (t, ft)):
        if fe <= c:
            continue
        top = G + (fe - G) * rho ** P["near_pow"] if P["near_pow"] else fe
        top_s = top
        if P["avail_q"] >= 0:
            pr = set(pressed)
            fn = sorted(fame[v] for v in T["nbr"][T["off"][e]:T["off"][e + 1]] if v not in pr)
            if fn:
                top = max(top, fn[min(P["avail_q"], len(fn) - 1)])
        for v, d in bfs(T, e, P["bfs_depth"], P["bfs_sim"]).items():
            allow = top - P["step"] * (d - 1)
            if allow > ceil_v[v]:
                ceil_v[v] = allow
            allow = top_s - P["step"] * (d - 1)
            if allow > ceil_s[v]:
                ceil_s[v] = allow
    b = max(c - P["W"], G - P["gdrop"])
    above = P["w_above"] * (np.maximum(0.0, fame - ceil_v) / 0.1) ** P["above_pow"]
    if P["near_disc"]:
        full = P["w_above"] * (np.maximum(0.0, fame - ceil_s) / 0.1) ** P["above_pow"]
        above += P["near_disc"] * (full - above)
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


def dijkstra(T, s, t, nc, hard, banned=None, min_sim=0.0, keep=None):
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
            a = A[j]
            if keep is not None and keep.get(u) == v:
                a *= P["e_keep"]
            nd = d + a + (0.0 if v == t else nc[v])
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


def dijkstra_minhops(T, s, t, nc, hard, hmin, min_sim=0.0):
    """Cheapest s->t walk with at least hmin hops (state = node, hops so far capped at hmin);
    immediate back-steps forbidden. Returns None if the walk repeats an artist."""
    off, nbr, A, sc = T["off"], T["nbr"], T["A"], T["sc"]
    hard = set(hard) - {s, t}
    H = hmin
    start = (s, 0, -1)
    dist = {start: 0.0}
    prv = {}
    pq = [(0.0, s, 0, -1)]
    goal = None
    while pq:
        d, u, h, w = heapq.heappop(pq)
        if u == t and h >= H:
            goal = (u, h, w)
            break
        if d > dist.get((u, h, w), 1e18):
            continue
        if u == t:
            continue
        h2 = min(h + 1, H)
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard or v == w or v == s:
                continue
            if sc[j] < min_sim and v != t and u != s:
                continue
            if v == t and h2 < H:
                continue
            nd = d + A[j] + (0.0 if v == t else nc[v])
            key = (v, h2, u if h2 < H else -1)
            if nd < dist.get(key, 1e18):
                dist[key] = nd
                prv[key] = (u, h, w)
                heapq.heappush(pq, (nd, v, h2, key[2]))
    if goal is None:
        return None
    p = [goal]
    while p[-1] != start:
        p.append(prv[p[-1]])
    path = [x[0] for x in reversed(p)]
    return path if len(set(path)) == len(path) else None


def journey(ctx, s, t, pressed, prev):
    p = _journey(ctx, s, t, pressed, prev)
    if not pressed:
        ctx.r2tiers_T.setdefault("L0", {})[(s, t)] = len(p) if p else 0
        return p
    if P["min_len"] and p:
        L0 = ctx.r2tiers_T.setdefault("L0", {}).get((s, t))
        if L0 is None:
            q = _journey(ctx, s, t, [], None)
            L0 = ctx.r2tiers_T["L0"][(s, t)] = len(q) if q else 0
        need = L0 - P["min_len"]
        if len(p) < need:
            nc = node_costs(ctx, s, t, pressed, prev).tolist()
            for m in ((P["min_sim"], 0.0) if P["min_sim"] else (0.0,)):
                q = dijkstra_minhops(ctx.r2tiers_T, s, t, nc, pressed, need - 1, m)
                if q:
                    return q
    return p


def _journey(ctx, s, t, pressed, prev):
    setup(ctx)
    T = ctx.r2tiers_T
    nc = node_costs(ctx, s, t, pressed, prev).tolist()
    ms = P["min_sim"] if pressed else 0.0
    keep = None
    if prev and P["e_keep"] != 1.0:
        pr = set(pressed)
        keep = {u: v for u, v in zip(prev, prev[1:]) if u not in pr and v not in pr}
    for m in ((ms, 0.0) if ms else (0.0,)):
        p = dijkstra(T, s, t, nc, pressed, min_sim=m, keep=keep)
        if p is None:
            continue
        if len(p) != 2:
            return p
        d = dijkstra(T, s, t, nc, pressed, banned={(s, t), (t, s)}, min_sim=m, keep=keep)
        return d if d is not None else p
    return None
