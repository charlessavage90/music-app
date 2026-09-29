"""Shared machinery for r1-search variants. EXPLORATORY.

Vectorised per-request edge costs + scipy's C Dijkstra, so full shortest-path trees from A and
from B cost ~tens of ms. Edge cost is on u->v (charged at the destination v).
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

BIG = 1e6


def setup_common(ctx):
    if getattr(ctx, "_r1", None) is not None:
        return
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = ctx.n
    src = np.repeat(np.arange(n), np.diff(off))
    # transpose permutation: edge (u,v) at position i; its reverse (v,u) at position rev[i]
    order = np.lexsort((src, nbr))  # sorted by (nbr, src) == CSR order of the transpose
    # the transpose CSR has rows = nbr, cols = src; since the graph is symmetric the transpose's
    # structure equals the original's, so position j of the original holds edge (src[j], nbr[j])
    # and order[j] is the original index of the edge (nbr[order[j]] == src[j], src[order[j]] == nbr[j]).
    assert np.array_equal(nbr[order], src) and np.array_equal(src[order], nbr)
    deg = np.diff(off)
    rank = None
    rowmax = np.maximum.reduceat(sc, off[:-1])
    # fame-neutral similarity: a link is as strong as the weaker endpoint's best link allows
    nsim = np.minimum(1.0, sc / np.minimum(rowmax[src], rowmax[nbr]))
    ctx._r1 = dict(off=off, nbr=nbr, sc=sc, src=src, rev=order, deg=deg, rank=rank,
                   pc=np.asarray(ctx.pctl, dtype=np.float64), rowmax=rowmax, nsim=nsim)


def mat(ctx, w):
    r = ctx._r1
    return csr_matrix((w, r["nbr"], r["off"]), shape=(ctx.n, ctx.n))


def rev_weights(ctx, w):
    """Weights for the reversed graph laid out in the original CSR order (row v, col u -> cost u->v)."""
    return w[ctx._r1["rev"]]


def trees(ctx, w, s, t):
    """Distances from s (forward) and to t (reverse graph). Returns (dA, predA, dB, predB)."""
    M = mat(ctx, w)
    dA, pA = dijkstra(M, directed=True, indices=s, return_predecessors=True)
    MB = mat(ctx, rev_weights(ctx, w))
    dB, pB = dijkstra(MB, directed=True, indices=t, return_predecessors=True)
    return dA, pA, dB, pB


def walk(pred, s, v):
    out = [v]
    while out[-1] != s:
        p = pred[out[-1]]
        if p < 0:
            return None
        out.append(int(p))
    return out[::-1]


def sp(ctx, w, s, t):
    d, p = dijkstra(mat(ctx, w), directed=True, indices=s, return_predecessors=True)
    if not np.isfinite(d[t]) or d[t] >= BIG:
        return None
    return walk(p, s, t)


def exclude(ctx, w, nodes, keep=()):
    """Price every edge INTO an excluded node at BIG (copy)."""
    r = ctx._r1
    w = w.copy()
    nodes = [v for v in nodes if v not in keep]
    if nodes:
        mask = np.isin(r["nbr"], np.asarray(nodes))
        w[mask] = BIG
    return w


def forbid_edge(ctx, w, a, b):
    r = ctx._r1
    w = w.copy()
    for u, v in ((a, b), (b, a)):
        lo, hi = r["off"][u], r["off"][u + 1]
        j = lo + np.searchsorted(r["nbr"][lo:hi], v)
        if j < hi and r["nbr"][j] == v:
            w[j] = BIG
    return w


def journey_from(ctx, w, s, t):
    """Shortest path with >=1 interior (forbid direct edge if needed)."""
    p = sp(ctx, w, s, t)
    if p is not None and len(p) == 2:
        p2 = sp(ctx, forbid_edge(ctx, w, s, t), s, t)
        return p2 or p
    return p


def weakest(ctx, path):
    return min(ctx.sim(u, v) for u, v in zip(path, path[1:]))


def mid_fame(ctx, path):
    inner = path[1:-1]
    return float(np.median([ctx.pl[v] for v in inner])) if inner else 1.0
