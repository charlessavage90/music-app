"""EXPLORATORY. Shared engine for r1-edgecost variants: precomputed per-edge arrays and a
Dijkstra copied from api pathfinding.find_path, generalised to take a per-edge cost array
(indexed by CSR edge position) plus a per-node cost (target exempt)."""
import heapq
import numpy as np


def prep(ctx):
    if hasattr(ctx, "E"):
        return ctx.E
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = len(off) - 1
    deg = np.diff(off)
    src = np.repeat(np.arange(n), deg)
    pop = np.asarray(st.pop_raw, dtype=np.float64)
    fame = np.asarray(ctx.pctl, dtype=np.float64)
    # rank of v in u's list by score desc (0 = best), ties by position
    rank = np.empty(len(nbr), dtype=np.float64)
    order = np.lexsort((-sc, src))  # grouped by src, score desc within
    pos_in_row = np.arange(len(nbr)) - off[src[order]]
    rank[order] = pos_in_row
    # reverse edge index
    key = src * n + nbr
    rkey = nbr * n + src
    srt = np.argsort(key)
    ridx = srt[np.searchsorted(key[srt], rkey)]
    assert np.all(key[ridx] == rkey)
    rank_rev = rank[ridx]
    # mean incoming similarity per node (= mean of its own row since symmetric)
    rowsum = np.add.reduceat(sc, off[:-1]) if len(sc) else np.zeros(n)
    mean_sim = rowsum / np.maximum(deg, 1)
    E = dict(off=off, nbr=nbr, sc=sc, src=src, n=n, deg=deg, pop=pop, fame=fame,
             rank=rank, rank_rev=rank_rev, mean_sim=mean_sim,
             off_l=off.tolist(), nbr_l=nbr.tolist())
    ctx.E = E
    return E


def today_static(E, cfg):
    """today's edge cost minus floor and ramp (w_avoid unused; w_degree_hub = 0)."""
    return (cfg.w_sim * (1 - E["sc"]) + cfg.w_jump * np.abs(E["pop"][E["src"]] - E["pop"][E["nbr"]])
            + cfg.w_hop)


def today_node(E, cfg, s, t, k):
    """today's per-node terms: floor (relaxed per press) and fame ramp."""
    base = min(E["pop"][s], E["pop"][t])
    floor = max(0.0, base - cfg.floor_relax_known * k)
    return cfg.w_floor * np.maximum(0.0, floor - E["pop"]) + cfg.w_known_ramp_fame_pctl * k * E["fame"]


def dijkstra(E, s, t, ecost, ncost, hard, banned=None):
    """ecost: (A, D, m, C, k) -> per-edge cost A[j] + m*D[j] + k*C[j]; ncost: list per node
    (not applied to target)."""
    A, D, m, C, k = ecost
    if s == t:
        return [s]
    off, nbr = E["off_l"], E["nbr_l"]
    hard = set(hard) - {s, t}
    dist = {s: 0.0}
    prev = {}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            break
        if d > dist.get(u, 1e18):
            continue
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard:
                continue
            if banned is not None and (u, v) in banned:
                continue
            nd = d + A[j] + m * D[j] + k * C[j] + (0.0 if v == t else ncost[v])
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if t not in prev:
        return None
    p = [t]
    while p[-1] != s:
        p.append(prev[p[-1]])
    return p[::-1]


def journey_with(E, s, t, ecost, ncost, hard):
    p = dijkstra(E, s, t, ecost, ncost, hard)
    if p is None or len(p) != 2:
        return p
    d = dijkstra(E, s, t, ecost, ncost, hard, banned={(s, t), (t, s)})
    return d if d is not None else p
