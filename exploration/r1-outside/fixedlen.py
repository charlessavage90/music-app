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


def exact_hops(ctx, s, t, hard, node_cost, hmin, hmax):
    """Min-cost s->t walk with exactly h hops for h in [hmin, hmax]; returns best simple path."""
    n = ctx.n
    owner, nbr, off = ctx.A_owner, ctx.A_nbr, ctx.A_off
    ecost = ctx.A_static + node_cost[owner]
    dist = np.full(n, np.inf)
    dist[s] = 0.0
    blocked = np.zeros(n, bool)
    blocked[list(hard)] = True
    blocked[s] = True
    blocked[s] = True
    bps = []
    best = []
    for h in range(1, hmax + 1):
        cand = dist[nbr] + ecost
        new = np.minimum.reduceat(cand, off[:-1])
        # backpointer: first argmin per segment
        hit = np.flatnonzero(cand == new[owner])
        own = owner[hit]
        first = np.unique(own, return_index=True)[1]
        bp = np.full(n, -1, dtype=np.int64)
        bp[own[first]] = nbr[hit[first]]
        bps.append(bp)
        if h >= hmin and np.isfinite(new[t]):
            best.append((float(new[t]), h))
        new[blocked] = np.inf
        new[t] = np.inf  # t never interior
        dist = new
    for cost, h in sorted(best):
        p = [t]
        for layer in range(h - 1, -1, -1):
            p.append(int(bps[layer][p[-1]]))
        p = p[::-1]
        if p[0] == s and len(set(p)) == len(p):
            return p
    return None


def make(b=0.3, pen="logwdeg", slack=2, floor=True, ramp=True):
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
        return exact_hops(ctx, s, t, set(pressed) - {s, t}, nc, max(2, L0), max(2, L0) + slack)

    return setup, journey
