"""EXPLORATORY. 'Fixed-length journey' (after Flexer et al. 2008, whose playlists have a set number
of songs) + an RP3beta-style popularity penalty (Christoffel/Paudel et al. 2015: transition / pop^beta).

Why: a per-artist fame penalty in a shortest-path router is cheapest to pay by having FEWER
stops (measured: v3 journeys shrank from 8 to 5.5 artists and the weakest step collapsed). Holding
the number of stops at least at the press-0 count removes that escape: the penalty can only be
paid by picking less famous stops.

Press 0 = today's journey exactly. Press k >= 1: exact-h-hop DP (vectorised Bellman-Ford over
layers), h in [L0, L0 + slack], today's edge cost + beta_k * pen(v) for interior v.
"""
import math

import numpy as np

import router


def setup_arrays(ctx):
    if hasattr(ctx, "A_off"):
        return
    router.precompute(ctx)
    ctx.A_off = np.asarray(ctx.off, dtype=np.int64)
    ctx.A_nbr = np.asarray(ctx.nbr, dtype=np.int64)
    ctx.A_sc = np.asarray(ctx.sc, dtype=np.float64)
    ctx.A_owner = np.repeat(np.arange(ctx.n), np.diff(ctx.A_off))
    ctx.A_pop = np.asarray(ctx.store.pop_raw, dtype=np.float64)
    ctx.A_pl = np.asarray(ctx.pl, dtype=np.float64)
    ctx.A_logwdeg = np.asarray(ctx.logwdeg)
    ctx.A_famepen = -np.log(np.maximum(1.0 - ctx.A_pl, 1e-3))
    # edge cost parts that do not depend on the request (edge u->v, v = owner, u = nbr)
    cfg = ctx.cfg
    ctx.A_static = (cfg.w_sim * (1 - ctx.A_sc) + cfg.w_jump * np.abs(ctx.A_pop[ctx.A_nbr] - ctx.A_pop[ctx.A_owner])
                    + cfg.w_hop)
    ctx.L0 = {}


def exact_hops(ctx, s, t, hard, node_cost, hmin, hmax, min_sim=0.0):
    """Min-cost s->t NON-BACKTRACKING walk with exactly h hops, h in [hmin, hmax] (top-2 labels per
    node so u->v may not use the label that came from v). Returns the cheapest walk that is a
    simple path, else None."""
    n = ctx.n
    owner, nbr, off = ctx.A_owner, ctx.A_nbr, ctx.A_off
    ecost = ctx.A_static + node_cost[owner]
    if min_sim > 0:
        ecost = np.where(ctx.A_sc < min_sim, np.inf, ecost)
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


def make(b=0.3, pen="logwdeg", slack=2, floor=True, ramp=True, min_sim=0.0):
    def setup(ctx):
        setup_arrays(ctx)

    def journey(ctx, s, t, pressed, prev):
        k = len(pressed)
        if k == 0:
            res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
            p = res[0]
            ctx.L0[(s, t)] = len(p) - 1
            return p
        L0 = ctx.L0.get((s, t))
        if L0 is None:
            L0 = len(ctx.find_journey(ctx.store, s, t, [], ctx.cfg)[0]) - 1
            ctx.L0[(s, t)] = L0
        cfg = ctx.cfg
        fl = min(ctx.A_pop[s], ctx.A_pop[t]) - cfg.floor_relax_known * k
        pv = ctx.A_logwdeg if pen == "logwdeg" else ctx.A_famepen if pen == "fame" else ctx.A_pl
        nc = b * k * pv
        if ramp:
            nc = nc + cfg.w_known_ramp_fame_pctl * k * ctx.A_pl
        nc = nc.copy()
        nc[t] = 0.0
        if floor:
            nc = nc + cfg.w_floor * np.maximum(0.0, fl - ctx.A_pop)
        p = exact_hops(ctx, s, t, set(pressed) - {s, t}, nc, max(2, L0), max(2, L0) + slack, min_sim)
        if p is None and min_sim > 0:
            p = exact_hops(ctx, s, t, set(pressed) - {s, t}, nc, max(2, L0), max(2, L0) + slack)
        if p is None:  # no simple walk of that length: fall back to Dijkstra with the same penalty
            ctx.fallbacks = getattr(ctx, "fallbacks", 0) + 1
            pc = nc.tolist()
            st = ctx.A_static  # not indexable by (u, v) cheaply; recompute inline
            pop = ctx.pop
            def cost(u, v, sim):
                return cfg.w_sim * (1 - sim) + cfg.w_jump * abs(pop[u] - pop[v]) + cfg.w_hop + pc[v]
            p = router.find_journey(ctx, s, t, pressed, cost)
        return p

    return setup, journey
