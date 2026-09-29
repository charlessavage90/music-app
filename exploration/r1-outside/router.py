"""EXPLORATORY. A copy of find_path/find_journey with a pluggable per-edge cost.

cost_fn(u, v, sim) -> float, built per request by a variant. Hard exclusions = pressed artists.
"""
import heapq
import math

import numpy as np


def precompute(ctx):
    """Degree, score-weighted degree (== raw popularity before log scaling), row sums."""
    if hasattr(ctx, "deg"):
        return
    off, sc = ctx.off, ctx.sc
    n = ctx.n
    deg = [off[u + 1] - off[u] for u in range(n)]
    wdeg = [sum(sc[off[u]:off[u + 1]]) for u in range(n)]
    ctx.deg, ctx.wdeg = deg, wdeg
    ctx.logdeg = [math.log(max(d, 1)) for d in deg]
    ctx.logwdeg = [max(0.0, math.log(max(w, 1e-3))) for w in wdeg]  # clipped: Dijkstra needs costs >= 0
    ctx.pop = ctx.store.pop_raw.tolist()


def find_path(ctx, s, t, hard, cost_fn, banned=None):
    if s == t:
        return [s]
    hard = set(hard) - {s, t}
    off, nbr, sc = ctx.off, ctx.nbr, ctx.sc
    dist = {s: 0.0}
    prev = {}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            break
        if d > dist.get(u, float("inf")):
            continue
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard:
                continue
            if banned and (u, v) in banned:
                continue
            nd = d + cost_fn(u, v, sc[j])
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if t not in prev:
        return None
    p = [t]
    while p[-1] != s:
        p.append(prev[p[-1]])
    return p[::-1]


def find_journey(ctx, s, t, hard, cost_fn):
    p = find_path(ctx, s, t, hard, cost_fn)
    if p is None or len(p) != 2:
        return p
    d = find_path(ctx, s, t, hard, cost_fn, banned={(s, t), (t, s)})
    return d or p
