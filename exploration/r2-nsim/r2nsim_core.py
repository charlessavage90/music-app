"""EXPLORATORY. Router core for the r2-nsim finalists (self-contained: numpy + scipy only).

Similarity is rebuilt from the map itself, two ways that do not depend on fame:
  * nsim  - a link's score measured against the weaker artist's own best link (r1-search);
  * overlap - the share of the two artists' neighbour lists they have in common (Jaccard).
Overlap is the better predictor of the coherence screen (r2-nsim NOTES) and is ~0 for junk links
(Louis Prima -> BROCKHAMPTON: raw 1.0, nsim 1.0, overlap 0.04).

Edge price u->v = A_NSIM*(1-nsim) + A_JAC*(1-min(1, overlap/J0)) + HOP
                 + LOWJPEN if overlap < LOWJ (links sharing almost no neighbours: rated a stretch 30-51%)
                 + node charge(v), where
node charge = BETA*max(0, fame_v - c)               soft pull toward the press target c
            + GAMMA*max(0, LOWF*min(c, fame_ends) - fame_v)   don't dive far below it
            + JUNK if fame_v < JUNKP                 bottom-of-scale junk
            + RPL unless v is a close (raw>=0.5), less famous neighbour of the latest pressed artist
and v is excluded outright if fame_v > cap_v = max(c, fame_s + AH - G*(hops_s(v)-1),
fame_t + AH - G*(hops_t(v)-1))  (journey-shaped hard ceiling: endpoint neighbourhoods stay free).
Press target c: each press takes c to min(c, fame of pressed) - STEP, never below
max(FLOOR, CF * less famous endpoint). Blocked -> c rises 0.05 at a time. Too long -> extra per-hop
charge (never a higher ceiling). Press 0 = today's router.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra, shortest_path

BIG = 1e6

DEFAULTS = dict(A_NSIM=3.0, A_JAC=2.0, J0=0.15, HOP=0.3, BETA=4.0, GAMMA=6.0, LOWF=0.6,
                JUNKP=0.05, JUNK=2.0, RPL=0.4, G=0.2, AH=0.005, STEP=0.08, FLOOR=0.1, CF=0.5,
                LMAX=11, LOWJ=0.0, LOWJPEN=0.0)


def _shared(ctx):
    """Map-derived arrays shared by every r2-nsim router (read-only)."""
    sh = getattr(ctx, "_r2nsim_shared", None)
    if sh is not None:
        return sh
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = ctx.n
    deg = np.diff(off)
    src = np.repeat(np.arange(n), deg)
    rev = np.lexsort((src, nbr))
    assert np.array_equal(nbr[rev], src) and np.array_equal(src[rev], nbr)
    rowmax = np.maximum.reduceat(sc, off[:-1])
    nsim = np.minimum(1.0, sc / np.minimum(rowmax[src], rowmax[nbr]))
    # common-neighbour counts on existing edges, row blocks
    A = csr_matrix((np.ones(len(nbr), dtype=np.float32), nbr, off), shape=(n, n))
    inter = np.zeros(len(nbr), dtype=np.float64)
    B = 4000
    for a in range(0, n, B):
        b = min(n, a + B)
        C = (A[a:b] @ A).multiply(A[a:b]).tocsr()
        C.sort_indices()
        for u in range(a, b):
            cs, ce = C.indptr[u - a], C.indptr[u - a + 1]
            if ce > cs:
                lo, hi = off[u], off[u + 1]
                inter[lo + np.searchsorted(nbr[lo:hi], C.indices[cs:ce])] = C.data[cs:ce]
    jac = inter / np.maximum(1, deg[src] + deg[nbr] - inter)
    unw = csr_matrix((np.ones(len(nbr)), nbr, off), shape=(n, n))
    sh = dict(off=off, nbr=nbr, sc=sc, src=src, rev=rev, nsim=nsim, jac=jac, unw=unw,
              pc=np.asarray(ctx.pctl, dtype=np.float64), n=n)
    ctx._r2nsim_shared = sh
    return sh


class Router:
    def __init__(self, ctx, **params):
        self.ctx = ctx
        self.p = {**DEFAULTS, **params}
        self.sh = _shared(ctx)
        P, sh = self.p, self.sh
        self.base = (P["A_NSIM"] * (1 - sh["nsim"]) + P["A_JAC"] * (1 - np.minimum(1.0, sh["jac"] / P["J0"]))
                     + P["HOP"] + P["LOWJPEN"] * (sh["jac"] < P["LOWJ"]))
        self._hops = None

    # -- helpers
    def _mat(self, w):
        sh = self.sh
        return csr_matrix((w, sh["nbr"], sh["off"]), shape=(sh["n"], sh["n"]))

    def _eidx(self, u, v):
        off, nbr = self.sh["off"], self.sh["nbr"]
        lo, hi = off[u], off[u + 1]
        j = lo + np.searchsorted(nbr[lo:hi], v)
        return j if j < hi and nbr[j] == v else -1

    def _sp(self, w, s, t):
        d, pr = dijkstra(self._mat(w), directed=True, indices=s, return_predecessors=True)
        if not np.isfinite(d[t]) or d[t] >= BIG:
            return None
        out = [t]
        while out[-1] != s:
            out.append(int(pr[out[-1]]))
        return out[::-1]

    def _journey(self, w, s, t):
        p = self._sp(w, s, t)
        if p is not None and len(p) == 2:
            w2 = w.copy()
            for a, b in ((s, t), (t, s)):
                j = self._eidx(a, b)
                if j >= 0:
                    w2[j] = BIG
            p = self._sp(w2, s, t) or p
        return p

    def centre(self, s, t, pressed):
        P, pl = self.p, self.ctx.pl
        c = 1.0
        for x in pressed:
            c = max(P["FLOOR"], min(c, pl[x]) - P["STEP"])
        return max(c, P["CF"] * min(pl[s], pl[t]))

    def weights(self, s, t, pressed, c):
        P, sh = self.p, self.sh
        pc = sh["pc"]
        if self._hops is None or self._hops[0] != (s, t):
            self._hops = ((s, t), shortest_path(sh["unw"], unweighted=True, indices=[s, t]))
        hs, ht = self._hops[1]
        cap = np.maximum(c, np.maximum(pc[s] + P["AH"] - P["G"] * (hs - 1), pc[t] + P["AH"] - P["G"] * (ht - 1)))
        node = P["BETA"] * np.maximum(0.0, pc - c)
        node += P["GAMMA"] * np.maximum(0.0, P["LOWF"] * min(c, pc[s], pc[t]) - pc)
        node += P["JUNK"] * (pc < P["JUNKP"])
        if P["RPL"] > 0 and pressed:
            x = pressed[-1]
            lo, hi = sh["off"][x], sh["off"][x + 1]
            nb = sh["nbr"][lo:hi]
            ok = nb[(sh["sc"][lo:hi] >= 0.5) & (pc[nb] < pc[x])]
            extra = np.full(sh["n"], P["RPL"])
            extra[ok] = 0.0
            node += extra
        node = np.where(pc > cap, BIG, node)
        hard = [v for v in pressed if v not in (s, t)]
        if hard:
            node[np.asarray(hard)] = BIG
        node[s] = 0.0
        node[t] = 0.0
        return self.base + node[sh["nbr"]]

    def _uses_big(self, w, p):
        return any(w[self._eidx(u, v)] >= BIG for u, v in zip(p, p[1:]))

    def journey(self, s, t, pressed, prev):
        ctx = self.ctx
        if not pressed:
            res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
            return res[0] if res else None
        c = self.centre(s, t, pressed)
        LMAX = self.p["LMAX"]
        while True:
            w0 = self.weights(s, t, pressed, c)
            p = None
            for extra in ((0.0, 0.5, 1.0, 2.0) if LMAX else (0.0,)):
                w = w0 + extra
                p = self._journey(w, s, t)
                if p is None or len(p) <= LMAX:
                    break
            if p is not None and len(p) > 2 and not self._uses_big(w, p):
                return p
            if c >= 1.0:
                return p if (p is not None and not self._uses_big(w, p)) else None
            c = min(1.0, c + 0.05)
