"""Each Dig deeper press makes famous artists more expensive to pass through, so the journey drifts to lesser-known but still closely linked artists (bolder setting).

EXPLORATORY (r2-simple). Today's router, unchanged, plus two things:

1. A per-artist fame toll, from press 1 on:  g(k) * fame_pctl ** P_CURVE   (target exempt)
   g(k) = B * (k + KICK * (1 - exp(-k / 1.5)))   -- linear in presses, plus an early kick of about
   KICK presses' worth reached by press ~3, so the first few presses are noticeable.
   The curve is continuous and steep: at P_CURVE = 10 a 99th-pct artist pays 0.90, 95th 0.60,
   90th 0.35, 80th 0.11, 70th 0.03 -- no hard knee for mini-hubs to sit just under.
2. A similarity floor, from press 1 on: a step weaker than MIN_SIM costs FLOOR_PEN extra, i.e. it is
   used only when no journey avoids it (lexicographic in practice), so the floor can never make a
   pair unroutable. Each endpoint's own floor is lowered to its best link to a not-yet-pressed
   neighbour, so a weakly linked endpoint is not charged for being weakly linked.

Press 0 is exactly today's journey. Today's raw-popularity floor (relaxed per press) and the tiny
fame ramp are kept as they are. Routing is bidirectional Dijkstra over the same costs (same least
cost as the one-sided search; ties may resolve differently).
Interface: journey(ctx, s, t, pressed, prev) with optional setup(ctx), per exploration/README.md.
"""
import heapq
import math

import numpy as np

P_CURVE = 10       # steepness of the fame toll
B = 1.2            # toll per press
KICK = 2.0         # early kick, in presses' worth
MIN_SIM = 0.70     # similarity floor (from press 1)
FLOOR_PEN = 20.0   # cost of one sub-floor step
FLOOR_FROM = 1     # press from which the floor applies (press 0 = today's journey)


def setup(ctx):
    if hasattr(ctx, "R2S"):
        return ctx.R2S
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = len(off) - 1
    src = np.repeat(np.arange(n), np.diff(off))
    pop = np.asarray(st.pop_raw, dtype=np.float64)
    fame = np.asarray(st.fame_lb_pctl, dtype=np.float64) if st.fame_lb_pctl is not None else np.zeros(n)
    fame = np.nan_to_num(fame, nan=0.0)
    cfg = ctx.cfg
    # today's static edge cost (w_avoid unused by `known`; w_degree_hub = 0 by default but kept)
    hub = np.asarray(st.degree_hub_penalty, dtype=np.float64)[nbr] if cfg.w_degree_hub else 0.0
    base = cfg.w_sim * (1 - sc) + cfg.w_jump * np.abs(pop[src] - pop[nbr]) + cfg.w_hop + cfg.w_degree_hub * hub
    key = src * n + nbr
    srt = np.argsort(key)
    ridx = srt[np.searchsorted(key[srt], nbr * n + src)]
    S = dict(n=n, off=off.tolist(), nbr=nbr.tolist(), sc=sc.tolist(), base=base.tolist(),
             floored=(base + FLOOR_PEN * (sc < MIN_SIM)).tolist(), ridx=ridx.tolist(),
             pop=pop, fame=fame, curve=fame ** P_CURVE)
    ctx.R2S = S
    return S


def _node_costs(S, cfg, s, t, k):
    pop, fame = S["pop"], S["fame"]
    floor_raw = max(0.0, min(pop[s], pop[t]) - cfg.floor_relax_known * k)
    nc = cfg.w_floor * np.maximum(0.0, floor_raw - pop) + cfg.w_known_ramp_fame_pctl * k * fame
    if k:
        nc = nc + B * (k + KICK * (1 - math.exp(-k / 1.5))) * S["curve"]
    return nc.tolist()


def _edge_costs(S, s, t, hard, k):
    if k < FLOOR_FROM:
        return S["base"]
    ec = S["floored"]
    patch = {}
    off, nbr, sc, base, ridx = S["off"], S["nbr"], S["sc"], S["base"], S["ridx"]
    for e in (s, t):
        a, b = off[e], off[e + 1]
        avail = [sc[j] for j in range(a, b) if nbr[j] not in hard]
        fl = min(MIN_SIM, max(avail)) if avail else 0.0
        if fl >= MIN_SIM:
            continue
        for j in range(a, b):
            if fl <= sc[j] < MIN_SIM:
                patch[j] = base[j]
                patch[ridx[j]] = base[j]
    if patch:
        ec = list(ec)
        for j, c in patch.items():
            ec[j] = c
    return ec


def _find_path(S, s, t, hard, ec, nc, banned=None):
    """Bidirectional Dijkstra. Graph and edge costs are symmetric; arriving at v pays nc[v] (not at t)."""
    if s == t:
        return [s]
    off, nbr = S["off"], S["nbr"]
    df, db = {s: 0.0}, {t: 0.0}
    pf, pb = {}, {}
    qf, qb = [(0.0, s)], [(0.0, t)]
    donef, doneb = set(), set()
    mu, meet = float("inf"), None
    while qf and qb:
        if qf[0][0] + qb[0][0] >= mu:
            break
        if qf[0][0] <= qb[0][0]:
            d, u = heapq.heappop(qf)
            if u in donef:
                continue
            donef.add(u)
            for j in range(off[u], off[u + 1]):
                v = nbr[j]
                if v in hard or (banned is not None and (u, v) in banned):
                    continue
                nd = d + ec[j] + (0.0 if v == t else nc[v])
                if nd < df.get(v, float("inf")):
                    df[v] = nd
                    pf[v] = u
                    heapq.heappush(qf, (nd, v))
                    if v in db and nd + db[v] < mu:
                        mu, meet = nd + db[v], v
        else:
            d, v = heapq.heappop(qb)
            if v in doneb:
                continue
            doneb.add(v)
            add = 0.0 if v == t else nc[v]
            for j in range(off[v], off[v + 1]):
                u = nbr[j]
                if u in hard or (banned is not None and (u, v) in banned):
                    continue
                nd = d + ec[j] + add
                if nd < db.get(u, float("inf")):
                    db[u] = nd
                    pb[u] = v
                    heapq.heappush(qb, (nd, u))
                    if u in df and df[u] + nd < mu:
                        mu, meet = df[u] + nd, u
    if meet is None:
        return None
    p = [meet]
    while p[-1] != s:
        p.append(pf[p[-1]])
    p.reverse()
    while p[-1] != t:
        p.append(pb[p[-1]])
    return p


def journey(ctx, s, t, pressed, prev):
    S = setup(ctx)
    k = len(pressed)
    hard = set(pressed) - {s, t}
    ec = _edge_costs(S, s, t, hard, k)
    nc = _node_costs(S, ctx.cfg, s, t, k)
    p = _find_path(S, s, t, hard, ec, nc)
    if p is None or len(p) != 2:
        return p
    d = _find_path(S, s, t, hard, ec, nc, banned={(s, t), (t, s)})
    return d if d is not None else p
