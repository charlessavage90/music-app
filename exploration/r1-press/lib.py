"""EXPLORATORY helpers for r1-press: a constrained Dijkstra over the kit ctx."""
import heapq


def route(ctx, s, t, allowed, w_sim=3.0, w_jump=1.0, w_hop=0.02, w_fame=0.0, banned_edge=None,
          bonus=None, max_hops=None, minsim=0.0):
    """Least-cost s->t path where every interior node v satisfies allowed(v).
    cost(u,v) = w_sim(1-sim) + w_jump|pop_u-pop_v| + w_hop + w_fame*pctl_v (v != t) - bonus.get(v,0).
    max_hops: optional cap on hops (state carries hop count if set)."""
    pop = ctx.store.pop_raw
    pl = ctx.pl
    off, nbr, sc = ctx.off, ctx.nbr, ctx.sc
    bonus = bonus or {}
    if max_hops is None:
        dist = {s: 0.0}
        prv = {}
        pq = [(0.0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == t:
                break
            if d > dist.get(u, 1e18):
                continue
            pu = float(pop[u])
            for j in range(off[u], off[u + 1]):
                v = nbr[j]
                if v != t and not allowed(v):
                    continue
                if banned_edge and {u, v} == banned_edge:
                    continue
                if sc[j] < minsim:
                    continue
                c = w_sim * (1.0 - sc[j]) + w_jump * abs(pu - float(pop[v])) + w_hop
                if v != t:
                    c += w_fame * pl[v] - bonus.get(v, 0.0)
                nd = d + max(c, 1e-6)
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
    # hop-limited: state (node, hops)
    dist = {(s, 0): 0.0}
    prv = {}
    pq = [(0.0, s, 0)]
    end = None
    while pq:
        d, u, h = heapq.heappop(pq)
        if u == t:
            end = (u, h)
            break
        if d > dist.get((u, h), 1e18) or h >= max_hops:
            continue
        pu = float(pop[u])
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v != t and not allowed(v):
                continue
            if banned_edge and {u, v} == banned_edge:
                continue
            if sc[j] < minsim:
                continue
            c = w_sim * (1.0 - sc[j]) + w_jump * abs(pu - float(pop[v])) + w_hop
            if v != t:
                c += w_fame * pl[v] - bonus.get(v, 0.0)
            nd = d + max(c, 1e-6)
            if nd < dist.get((v, h + 1), 1e18):
                dist[(v, h + 1)] = nd
                prv[(v, h + 1)] = (u, h)
                heapq.heappush(pq, (nd, v, h + 1))
    if end is None:
        return None
    p = [end]
    while p[-1][0] != s or p[-1][1] != 0:
        p.append(prv[p[-1]])
    return [x[0] for x in p[::-1]]


def baseline(ctx, s, t, pressed):
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


def route2(ctx, s, t, allowed, nodecost=None, w_sim=3.0, w_jump=1.0, w_hop=0.02, banned_edge=None,
           max_pops=30000):
    """Unbounded constrained Dijkstra with an optional per-node cost (applied to v != t);
    gives up after max_pops expansions. Returns (path, cost) or (None, None)."""
    pop = ctx.store.pop_raw
    off, nbr, sc = ctx.off, ctx.nbr, ctx.sc
    dist = {s: 0.0}
    prv = {}
    pq = [(0.0, s)]
    pops = 0
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            break
        if d > dist.get(u, 1e18):
            continue
        pops += 1
        if pops > max_pops:
            return None, None
        pu = float(pop[u])
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v != t and not allowed(v):
                continue
            if banned_edge and u in banned_edge and v in banned_edge:
                continue
            c = w_sim * (1.0 - sc[j]) + w_jump * abs(pu - float(pop[v])) + w_hop
            if nodecost is not None and v != t:
                c += nodecost(v)
            nd = d + c
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prv[v] = u
                heapq.heappush(pq, (nd, v))
    if t not in prv:
        return None, None
    p = [t]
    while p[-1] != s:
        p.append(prv[p[-1]])
    return p[::-1], dist[t]
