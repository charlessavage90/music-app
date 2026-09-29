"""EXPLORATORY. Shared router for the rules-not-prices variants.

A copy of the shipped find_path cost (w_sim, w_jump, w_floor, w_hop, known ramp; avoid and
degree_hub are 0 / unused for `known`-only presses) over list-based CSR, with a per-node
fame cap: node v (interior) is allowed iff pctl[v] <= cap(v). cap is either a float (global
ceiling) or a list indexed by node (journey-shaped ceilings).
"""
from __future__ import annotations

import heapq

INF = float("inf")


def setup_common(ctx):
    if getattr(ctx, "_rc", False):
        return
    ctx.popl = [float(x) for x in ctx.store.pop_raw]
    ctx._rc = True


def sim_default(ctx):
    return ctx.sc


def find_path(ctx, s, t, pressed, cap=1.0, k=None, forbidden=None, sims=None,
              w_sim=None, ramp=True):
    """Shipped cost; interiors with pctl > cap (float or per-node list) are skipped."""
    cfg = ctx.cfg
    if s == t:
        return [s]
    k = len(pressed) if k is None else k
    hard = set(pressed) - {s, t}
    off, nbr, pl, pop = ctx.off, ctx.nbr, ctx.pl, ctx.popl
    sc = ctx.sc if sims is None else sims
    ws = cfg.w_sim if w_sim is None else w_sim
    wj, wf, wh = cfg.w_jump, cfg.w_floor, cfg.w_hop
    floor = max(0.0, min(pop[s], pop[t]) - cfg.floor_relax_known * k)
    rampw = cfg.w_known_ramp_fame_pctl * k if ramp else 0.0
    percap = not isinstance(cap, float)
    dist = {s: 0.0}
    prev = {}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            break
        if d > dist.get(u, INF):
            continue
        pu = pop[u]
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard:
                continue
            if forbidden is not None and ((u == forbidden[0] and v == forbidden[1]) or (u == forbidden[1] and v == forbidden[0])):
                continue
            if v != t:
                if percap:
                    if pl[v] > cap[v]:
                        continue
                elif pl[v] > cap:
                    continue
            pv = pop[v]
            fl = floor - pv
            c = ws * (1.0 - sc[j]) + wj * abs(pu - pv) + (wf * fl if fl > 0 else 0.0) + wh
            if rampw and v != t:
                c += rampw * pl[v]
            nd = d + c
            if nd < dist.get(v, INF):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if t not in prev:
        return None
    p = [t]
    while p[-1] != s:
        p.append(prev[p[-1]])
    return p[::-1]


def find_journey(ctx, s, t, pressed, cap=1.0, **kw):
    p = find_path(ctx, s, t, pressed, cap, **kw)
    if p is None:
        return None
    if len(p) != 2:
        return p
    d = find_path(ctx, s, t, pressed, cap, forbidden=(s, t), **kw)
    return d if d is not None else p


def bottleneck(ctx, s, t, excl):
    """Smallest achievable max interior pctl over s-t paths with >=1 interior (drp_common copy)."""
    off, nbr, pl = ctx.off, ctx.nbr, ctx.pl
    excl = set(excl) - {s, t}
    best, pq, done = {}, [], set()
    for w in nbr[off[s]:off[s + 1]]:
        if w == t or w in excl:
            continue
        if pl[w] < best.get(w, 2.0):
            best[w] = pl[w]
            heapq.heappush(pq, (pl[w], w))
    while pq:
        lu, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        row = nbr[off[u]:off[u + 1]]
        if t in row:
            return lu
        for w in row:
            if w == s or w in excl or w in done:
                continue
            lw = lu if lu >= pl[w] else pl[w]
            if lw < best.get(w, 2.0):
                best[w] = lw
                heapq.heappush(pq, (lw, w))
    return INF


def ceiling_journey(ctx, s, t, pressed, c, **kw):
    """Route under global ceiling c; if blocked (no interior-bearing journey), relax to the
    minimum ceiling that admits one (the bottleneck). Returns (path, used_ceiling)."""
    p = find_journey(ctx, s, t, pressed, float(c), **kw)
    if p is not None and len(p) > 2:
        return p, c
    h = bottleneck(ctx, s, t, pressed)
    if h == INF:
        return find_journey(ctx, s, t, pressed, 1.0, **kw), 1.0
    c2 = max(c, h)
    p = find_journey(ctx, s, t, pressed, float(c2), **kw)
    return p, c2


def bfs_hops(ctx, src, excl, limit=6):
    off, nbr = ctx.off, ctx.nbr
    d = {src: 0}
    fr = [src]
    for h in range(1, limit + 1):
        nx = []
        for u in fr:
            for v in nbr[off[u]:off[u + 1]]:
                if v not in d and v not in excl:
                    d[v] = h
                    nx.append(v)
        fr = nx
    return d


def rank_sims(ctx):
    """Rank-based similarity: for edge u->v, 1 - rank(v in u's list by score)/deg(u).
    Undoes the saturation at the top (many 1.0s) by spreading each artist's list evenly."""
    if getattr(ctx, "_rs", None) is not None:
        return ctx._rs
    off, sc = ctx.off, ctx.sc
    rs = [0.0] * len(sc)
    for u in range(ctx.n):
        a, b = off[u], off[u + 1]
        n = b - a
        order = sorted(range(a, b), key=lambda j: -sc[j])
        for r, j in enumerate(order):
            rs[j] = 1.0 - r / n
    ctx._rs = rs
    return rs
