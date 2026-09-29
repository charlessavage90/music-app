"""Journey-shaped ceiling by POSITION IN THE JOURNEY (not graph distance): the i-th artist after
the source may reach fame E_s + A - G*(i-1); approaching the target, an artist whose graph hop
distance to t is h may reach E_t + A - G*(h-1); everywhere else the press ceiling c applies.
Search state = (node, hops from source, capped at H). Blocked -> c rises 0.05 at a time.
Optional rank-based similarity (R1_RANK=1)."""
import heapq, os
from rules_common import setup_common, bfs_hops, rank_sims
SCHED = [float(x) for x in os.environ.get("R1_SCHED", "1.0,0.95,0.90,0.80,0.70,0.60,0.50,0.45,0.40,0.35,0.30").split(",")]
G = float(os.environ.get("R1_G", "0.1"))
A = float(os.environ.get("R1_A", "0.005"))
RANK = os.environ.get("R1_RANK", "0") == "1"
WSIM = float(os.environ.get("R1_WSIM", "3.0"))
MINSIM = float(os.environ.get("R1_MINSIM", "0.0"))   # hard rule: no step weaker than this (raw sim)
ENDFLOOR = os.environ.get("R1_ENDFLOOR", "0") == "1"   # centre ceiling never below the less famous endpoint
INF = float("inf")

def setup(ctx):
    setup_common(ctx)
    if RANK:
        rank_sims(ctx)

def route(ctx, s, t, pressed, c, forbidden=None):
    cfg = ctx.cfg
    k = len(pressed)
    hard = set(pressed) - {s, t}
    off, nbr, pl, pop = ctx.off, ctx.nbr, ctx.pl, ctx.popl
    sc = ctx._rs if RANK else ctx.sc
    es, et = pl[s], pl[t]
    H = max(1, int((es + A - c) / G) + 2) if G > 0 else 50
    dt = bfs_hops(ctx, t, hard, H + 1)
    floor = max(0.0, min(pop[s], pop[t]) - cfg.floor_relax_known * k)
    rampw = cfg.w_known_ramp_fame_pctl * k
    wj, wf, wh = cfg.w_jump, cfg.w_floor, cfg.w_hop
    start = (s, 0)
    dist = {start: 0.0}
    prev = {}
    pq = [(0.0, s, 0)]
    end = None
    while pq:
        d, u, i = heapq.heappop(pq)
        if u == t:
            end = (u, i); break
        if d > dist.get((u, i), INF):
            continue
        pu = pop[u]
        ni = i + 1 if i < H else H
        capi = es + A - G * (ni - 1)
        for j in range(off[u], off[u + 1]):
            v = nbr[j]
            if v in hard:
                continue
            if ctx.sc[j] < MINSIM:
                continue
            if forbidden and u == s and v == t:
                continue
            if v != t:
                cap = c
                if capi > cap: cap = capi
                h = dt.get(v)
                if h is not None:
                    x = et + A - G * (h - 1)
                    if x > cap: cap = x
                if pl[v] > cap:
                    continue
            pv = pop[v]
            fl = floor - pv
            cost = WSIM * (1.0 - sc[j]) + wj * abs(pu - pv) + (wf * fl if fl > 0 else 0.0) + wh
            if v != t:
                cost += rampw * pl[v]
            nd = d + cost
            key = (v, ni)
            if nd < dist.get(key, INF):
                dist[key] = nd
                prev[key] = (u, i)
                heapq.heappush(pq, (nd, v, ni))
    if end is None:
        return None
    p = [end]
    while p[-1] != start:
        p.append(prev[p[-1]])
    return [x[0] for x in p[::-1]]

def journey(ctx, s, t, pressed, prev):
    c = SCHED[min(len(pressed), len(SCHED) - 1)]
    if ENDFLOOR:
        c = max(c, min(ctx.pl[s], ctx.pl[t]))
    while True:
        p = route(ctx, s, t, pressed, c)
        if p is not None and len(p) == 2:
            p = route(ctx, s, t, pressed, c, forbidden=True) or p
        if (p is not None and len(p) > 2) or c >= 1.0:
            return p
        c = min(1.0, c + 0.05)
