"""EXPLORATORY r2-simple engine: today's Dijkstra (find_path/find_journey copied) with
(a) a per-artist fame toll that grows with presses, (b) a soft-lexicographic similarity floor
(a step below the floor costs FLOOR_PEN, so it is only used when no journey avoids it),
(c) an optional junk toll on the very bottom of the fame scale. Params via env R2 (JSON) or make(**P).

node cost(v) = [today floor + ramp, optional] + g(k) * h(fame_v) + junk(v)       (target exempt)
  h: 'log'  -> -log(1 - min(f, 0.999))        (r1-outside)
     'knee' -> max(0, f - thr)/(1 - thr)       (r1-edgecost ftB)
     'pow'  -> f ** p                          (steep continuous)
     'logx' -> max(0, -log(1-f) - (-log(1-thr)))  (log, zero below thr)
  g(k): b * k  ('lin') or b * kcap * (1 - exp(-k / tau))  ('sat') or b * sqrt(k) ('sqrt')
edge cost(u,v) = 3(1-sim) + |dpop_raw| + 0.02 + FLOOR_PEN * [sim < min_sim]
"""
import heapq
import json
import math
import os

import numpy as np

DEFAULTS = dict(bidi=1, h="log", b=0.15, g="lin", tau=3.0, kcap=10.0, thr=0.9, p=8.0, min_sim=0.0,
                floor_pen=20.0, junk_pct=0.0, junk_pen=0.0, keep_floor=1, keep_ramp=1,
                mid_rel=0.0, floor_from=0, rd=0.0, rd_sim=0.5, rd_last=0, rd_gap=0.0)


def prep(ctx):
    if hasattr(ctx, "S"):
        return ctx.S
    st = ctx.store
    off = np.asarray(st.offsets, dtype=np.int64)
    nbr = np.asarray(st.neighbours, dtype=np.int64)
    sc = np.asarray(st.scores, dtype=np.float64)
    n = len(off) - 1
    src = np.repeat(np.arange(n), np.diff(off))
    pop = np.asarray(st.pop_raw, dtype=np.float64)
    fame = np.asarray(ctx.pctl, dtype=np.float64)
    meas = np.asarray(ctx.measured, dtype=bool)
    base = 3.0 * (1 - sc) + np.abs(pop[src] - pop[nbr]) + 0.02
    best = np.maximum.reduceat(sc, off[:-1])
    key = src * n + nbr
    srt = np.argsort(key)
    ridx = srt[np.searchsorted(key[srt], nbr * n + src)]
    ctx.S = dict(off=off.tolist(), nbr=nbr.tolist(), sc_np=sc, base_np=base, pop=pop, fame=fame,
                 meas=meas, n=n, cache={}, best=best, ridx=ridx, off_np=off, sc=sc.tolist(),
                 base=base.tolist())
    return ctx.S


def edge_costs(S, min_sim, floor_pen):
    key = (min_sim, floor_pen)
    if key not in S["cache"]:
        S["cache"][key] = (S["base_np"] + floor_pen * (S["sc_np"] < min_sim)).tolist()
    return S["cache"][key]


def h_of(P, f):
    if P["h"] == "log":
        return -np.log(1 - np.minimum(f, 0.999))
    if P["h"] == "knee":
        return np.maximum(0.0, f - P["thr"]) / (1 - P["thr"])
    if P["h"] == "pow":
        return f ** P["p"]
    if P["h"] == "logx":
        return np.maximum(0.0, -np.log(1 - np.minimum(f, 0.999)) + np.log(1 - P["thr"]))
    raise ValueError(P["h"])


def g_of(P, k):
    if P["g"] == "lin":
        return P["b"] * k
    if P["g"] == "sat":
        return P["b"] * P["kcap"] * (1 - math.exp(-k / P["tau"]))
    if P["g"] == "boost":  # linear plus an early kick of size tau presses' worth, reached by ~3 presses
        return P["b"] * (k + P["tau"] * (1 - math.exp(-k / 1.5)))
    if P["g"] == "sqrt":
        return P["b"] * math.sqrt(k) * math.sqrt(P["kcap"])
    raise ValueError(P["g"])


def node_costs(ctx, P, s, t, k, pressed=()):
    S = prep(ctx)
    pop, fame = S["pop"], S["fame"]
    nc = np.zeros(S["n"])
    if P["keep_floor"]:
        floor = max(0.0, min(pop[s], pop[t]) - ctx.cfg.floor_relax_known * k)
        nc += ctx.cfg.w_floor * np.maximum(0.0, floor - pop)
    if P["keep_ramp"]:
        nc += ctx.cfg.w_known_ramp_fame_pctl * k * fame
    if k:
        hf = h_of(P, fame)
        if P["mid_rel"]:
            # no toll below the less famous endpoint's fame (minus mid_rel): mid pairs don't dive
            ref = max(0.0, min(fame[s], fame[t]) - P["mid_rel"])
            hf = np.maximum(0.0, hf - float(h_of(P, np.array([ref]))[0]))
        tol = g_of(P, k) * hf
        if P["rd"]:
            # the pressed artist's close, less famous neighbours pay a reduced toll
            off, nbr, sc = S["off"], S["nbr"], S["sc"]
            for x in (pressed[-1:] if P["rd_last"] else pressed):
                for j in range(off[x], off[x + 1]):
                    v = nbr[j]
                    if sc[j] >= P["rd_sim"] and fame[v] < fame[x] - P["rd_gap"]:
                        tol[v] *= (1 - P["rd"])
        nc += tol
    if P["junk_pen"]:
        nc += P["junk_pen"] * ((fame < P["junk_pct"]) | ~S["meas"])
    return nc.tolist()


def endpoint_relaxed(S, ec, s, t, min_sim, floor_pen):
    """An endpoint whose best link is below the floor may use links at least as good as its best:
    the floor never makes a pair unroutable just because an endpoint is weakly linked."""
    patch = {}
    for e in (s, t):
        fl = min(min_sim, S["best"][e])
        if fl >= min_sim:
            continue
        a, b = S["off"][e], S["off"][e + 1]
        for j in range(a, b):
            if fl <= S["sc"][j] < min_sim:
                patch[j] = S["base"][j]
                patch[int(S["ridx"][j])] = S["base"][j]
    if not patch:
        return ec
    ec = list(ec)
    for j, c in patch.items():
        ec[j] = c
    return ec


def find_path(S, s, t, hard, ec, nc, banned=None):
    if s == t:
        return [s]
    off, nbr = S["off"], S["nbr"]
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
            nd = d + ec[j] + (0.0 if v == t else nc[v])
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


def find_path_bidi(S, s, t, hard, ec, nc, banned=None):
    """Bidirectional Dijkstra, same costs as find_path (graph and edge costs are symmetric;
    arriving at v pays nc[v] except at t). Same least cost; ties may pick another path."""
    if s == t:
        return [s]
    off, nbr = S["off"], S["nbr"]
    hard = set(hard) - {s, t}
    df, db = {s: 0.0}, {t: 0.0}
    pf, pb = {}, {}
    qf, qb = [(0.0, s)], [(0.0, t)]
    donef, doneb = set(), set()
    mu, meet = 1e18, None
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
                if nd < df.get(v, 1e18):
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
                if nd < db.get(u, 1e18):
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


def find_journey(S, s, t, hard, ec, nc, fp=None):
    fp = fp or find_path_bidi
    p = fp(S, s, t, hard, ec, nc)
    if p is None or len(p) != 2:
        return p
    d = fp(S, s, t, hard, ec, nc, banned={(s, t), (t, s)})
    return d if d is not None else p


def make(**over):
    P = dict(DEFAULTS)
    P.update(over)

    def setup(ctx):
        prep(ctx)
        edge_costs(ctx.S, P["min_sim"], P["floor_pen"])

    def journey(ctx, s, t, pressed, prev):
        S = prep(ctx)
        ms = P["min_sim"] if len(pressed) >= P["floor_from"] else 0.0
        ec = edge_costs(S, ms, P["floor_pen"])
        if ms > 0:
            ec = endpoint_relaxed(S, ec, s, t, ms, P["floor_pen"])
        nc = node_costs(ctx, P, s, t, len(pressed), pressed)
        return find_journey(S, s, t, pressed, ec, nc, None if P["bidi"] else find_path)

    return setup, journey, P
