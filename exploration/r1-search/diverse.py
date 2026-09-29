"""r1-search 'diverse': generate many near-cheapest journeys under TODAY's cost (penalty method:
each round, artists already used cost PEN more), then pick the one with the least famous middle
among those whose true cost is within EPS*k of the cheapest. Press 0 = today's router.
EXPLORATORY."""
import os
import numpy as np
from scipy.sparse.csgraph import dijkstra
from common import setup_common, exclude, mat, walk, forbid_edge, BIG

ROUNDS = int(os.environ.get("R1_ROUNDS", "15"))
PEN = float(os.environ.get("R1_PEN", "0.5"))
EPS = float(os.environ.get("R1_EPS", "0.3"))


def setup(ctx):
    setup_common(ctx)
    r = ctx._r1
    pr = np.asarray(ctx.store.pop_raw, dtype=np.float64)
    r["pr"] = pr


def today_cost(ctx, s, t, k):
    r, cfg = ctx._r1, ctx.cfg
    pr = r["pr"]
    floor = max(0.0, min(pr[s], pr[t]) - cfg.floor_relax_known * k)
    u, v = r["src"], r["nbr"]
    w = (cfg.w_sim * (1 - r["sc"]) + cfg.w_jump * np.abs(pr[u] - pr[v])
         + cfg.w_floor * np.maximum(0.0, floor - pr[v]) + cfg.w_hop)
    ramp = cfg.w_known_ramp_fame_pctl * k * r["pc"][v]
    w = w + np.where(v == t, 0.0, ramp)
    return w


def journey(ctx, s, t, pressed, prev):
    k = len(pressed)
    if k == 0:
        res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
        return res[0] if res else None
    r = ctx._r1
    w0 = exclude(ctx, today_cost(ctx, s, t, k), pressed, keep=(s, t))
    w0 = forbid_edge(ctx, w0, s, t)
    nodepen = np.zeros(ctx.n)
    cands = []
    for _ in range(ROUNDS):
        w = w0 + nodepen[r["nbr"]]
        d, pr = dijkstra(mat(ctx, w), indices=s, return_predecessors=True)
        if not np.isfinite(d[t]) or d[t] >= BIG:
            break
        path = walk(pr, s, t)
        true = sum(w0[r["off"][a] + np.searchsorted(r["nbr"][r["off"][a]:r["off"][a + 1]], b)]
                   for a, b in zip(path, path[1:]))
        cands.append((true, path))
        for v in path[1:-1]:
            nodepen[v] += PEN
    if not cands:
        return None
    best = min(c[0] for c in cands)
    ok = [c for c in cands if c[0] <= best + EPS * k]
    ok.sort(key=lambda c: (np.median([ctx.pl[v] for v in c[1][1:-1]]), c[0]))
    return ok[0][1]
