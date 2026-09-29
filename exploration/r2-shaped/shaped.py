"""EXPLORATORY engine for r2-shaped: a soft, journey-shaped fame charge.

Cost of stepping u -> v = today's edge cost (3(1-sim) + |pop_u - pop_v| + 0.02, the raw floor and
today's small ramp) + a per-artist charge when v is more famous than a *target* for v's place:

    target(v) = max( centre_k,                                     # compounding press ceiling (r1-rules v7)
                     fame(e) + A - G*(hops(e, v) - 1)  for e in {s, t},   # endpoint neighbours may be as famous
                     min(fame_s, fame_t) - X*k )                   # never aim far below the pair itself
    charge(v) = B * max(0, log((1 - target) / (1 - fame(v))))      # steep at the top (r1-outside's -log(1-f))

Steps weaker than MINSIM cost an extra SIMPEN (soft, so a blocked region relaxes only locally).
Nothing is excluded except pressed artists; no fallback regenerates anything; press 0 = today's cost.
Routing: scipy Dijkstra over the CSR with per-request edge weights (~0.1-0.3 s).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra, shortest_path

BIG = 1e6


def setup_arrays(ctx):
    if hasattr(ctx, "S_static"):
        return
    cfg = ctx.cfg
    off = np.asarray(ctx.off, dtype=np.int64)
    nbr = np.asarray(ctx.nbr, dtype=np.int32)
    sc = np.asarray(ctx.sc, dtype=np.float64)
    owner = np.repeat(np.arange(ctx.n, dtype=np.int32), np.diff(off))
    pop = np.asarray(ctx.store.pop_raw, dtype=np.float64)
    ctx.S_off, ctx.S_nbr, ctx.S_sc, ctx.S_owner, ctx.S_pop = off, nbr, sc, owner, pop
    ctx.S_pl = np.asarray(ctx.pl, dtype=np.float64)
    ctx.S_static = cfg.w_sim * (1.0 - sc) + cfg.w_jump * np.abs(pop[owner] - pop[nbr]) + cfg.w_hop
    ctx.S_unit = csr_matrix((np.ones(len(nbr)), nbr, off), shape=(ctx.n, ctx.n))
    ctx.S_hops = {}


def hops_from(ctx, e):
    h = ctx.S_hops.get(e)
    if h is None:
        h = shortest_path(ctx.S_unit, unweighted=True, directed=False, indices=e)
        ctx.S_hops[e] = h
    return h


def centre_ceiling(ctx, pressed, mult):
    c = 1.0
    for x in pressed:
        c = min(c, ctx.pl[x])
        c = max(0.0, 1.0 - mult * (1.0 - c))
    return c


def targets(ctx, s, t, pressed, P):
    k = len(pressed)
    pl = ctx.S_pl
    c = centre_ceiling(ctx, pressed, P["mult"])
    tgt = np.full(ctx.n, c)
    for e in (s, t):
        h = hops_from(ctx, e)
        g = P["G"] + P["Gk"] * k
        np.maximum(tgt, pl[e] + P["A"] - g * (h - 1), out=tgt)
    lb = min(pl[s], pl[t]) - P["X"] * k
    np.maximum(tgt, lb, out=tgt)
    return np.minimum(tgt, 1.0), c, lb


def node_costs(ctx, s, t, pressed, P):
    cfg = ctx.cfg
    k = len(pressed)
    pl, pop = ctx.S_pl, ctx.S_pop
    floor = max(0.0, min(pop[s], pop[t]) - cfg.floor_relax_known * k)
    nc = cfg.w_floor * np.maximum(0.0, floor - pop) + cfg.w_known_ramp_fame_pctl * k * pl
    if k > 0:
        tgt, _, _ = targets(ctx, s, t, pressed, P)
        r_t = np.maximum(1.0 - tgt, 1e-3)
        r_v = np.maximum(1.0 - pl, 1e-3)
        nc = nc + P["B"] * np.maximum(0.0, np.log(r_t / r_v))
    nc[t] = cfg.w_floor * max(0.0, floor - pop[t])   # target: floor only (as shipped), no ramp/charge
    for x in pressed:
        if x != s and x != t:
            nc[x] = BIG
    return nc


def route(ctx, s, t, nc, P, k, forbid_direct=False):
    data = ctx.S_static + nc[ctx.S_nbr]
    if k > 0 and P["minsim"] > 0:
        data = data + np.where(ctx.S_sc < P["minsim"], P["simpen"], 0.0)
    if forbid_direct:
        a, b = ctx.S_off[s], ctx.S_off[s + 1]
        j = a + np.searchsorted(ctx.S_nbr[a:b], t)
        if j < b and ctx.S_nbr[j] == t:
            data[j] = BIG
    g = csr_matrix((data, ctx.S_nbr, ctx.S_off), shape=(ctx.n, ctx.n))
    dist, pred = dijkstra(g, directed=True, indices=s, return_predecessors=True)
    if not np.isfinite(dist[t]) or dist[t] >= BIG:
        return None
    p = [t]
    while p[-1] != s:
        p.append(int(pred[p[-1]]))
    return [int(x) for x in p[::-1]]


DEFAULTS = dict(mult=3.0, A=0.005, G=0.10, Gk=0.0, X=0.08, B=1.0, minsim=0.7, simpen=1.0)


def make(**over):
    P = dict(DEFAULTS, **over)

    def setup(ctx):
        setup_arrays(ctx)

    def journey(ctx, s, t, pressed, prev):
        setup_arrays(ctx)
        if s == t:
            return [s]
        k = len(pressed)
        nc = node_costs(ctx, s, t, pressed, P)
        p = route(ctx, s, t, nc, P, k)
        if p is not None and len(p) == 2:
            p = route(ctx, s, t, nc, P, k, forbid_direct=True) or p
        return p

    journey.params = P
    return setup, journey
