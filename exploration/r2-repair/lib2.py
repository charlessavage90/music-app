"""EXPLORATORY helpers for r2-repair: hop-bounded constrained Dijkstra (Pareto on hops) over the kit ctx."""
import heapq


def route_h(ctx, s, t, allowed, nodecost=None, max_hops=4, w_sim=3.0, w_jump=1.0, w_hop=0.02,
            banned_edge=None, max_pops=40000, minsim=0.0, minsim_s=None, minsim_t=None):
    """Cheapest s->t path with at most max_hops hops; interior v must satisfy allowed(v, h) where h is
    the hop index at which v is entered (1-based). If allowed returns 2, v is admitted only as the
    last stop before t (it may expand to t and nothing else). Pareto pruning: a node popped with h hops is skipped
    if it was already popped with <= h hops (Dijkstra pops in cost order, so that label dominates).
    Returns (path, cost) or (None, None)."""
    pop = ctx.store.pop_raw
    off, nbr, sc = ctx.off, ctx.nbr, ctx.sc
    # lookahead: a node entered at hop max_hops-1 must touch t; at max_hops-2 it must be 2 steps away
    L1 = set(nbr[off[t]:off[t + 1]])
    L2 = set()
    if max_hops >= 3:
        for y in L1:
            L2.update(nbr[off[y]:off[y + 1]])
    best_h = {}                      # node -> min hops popped so far
    pq = [(0.0, 0, s, -1, False)]    # (cost, hops, node, parent label idx, last-only)
    labels = []                      # (node, parent label idx)
    pops = 0
    while pq:
        d, h, u, par, lastonly = heapq.heappop(pq)
        bh = best_h.get(u)
        if bh is not None and bh <= h:
            continue
        if not lastonly:
            best_h[u] = h
        labels.append((u, par))
        me = len(labels) - 1
        if u == t:
            p = []
            i = me
            while i != -1:
                p.append(labels[i][0])
                i = labels[i][1]
            return p[::-1], d
        pops += 1
        if pops > max_pops or h >= max_hops:
            continue
        pu = float(pop[u])
        h1 = h + 1
        last = h1 == max_hops
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            lo = False
            if v == t:
                pass
            else:
                if last or lastonly:
                    continue
                if h1 == max_hops - 1:
                    if v not in L1:
                        continue
                elif h1 == max_hops - 2 and v not in L2:
                    continue
                ok = allowed(v, h1)
                if not ok:
                    continue
                lo = ok == 2
            if banned_edge and u in banned_edge and v in banned_edge:
                continue
            ms = minsim
            if minsim_s is not None and u == s:
                ms = minsim_s
            elif minsim_t is not None and v == t:
                ms = minsim_t
            if sc[j] < ms:
                continue
            bv = best_h.get(v)
            if bv is not None and bv <= h1:
                continue
            c = w_sim * (1.0 - sc[j]) + w_jump * abs(pu - float(pop[v])) + w_hop
            if nodecost is not None and v != t:
                c += nodecost(v)
            heapq.heappush(pq, (d + c, h1, v, me, lo))
    return None, None


def baseline(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None
