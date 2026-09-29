"""EXPLORATORY variant factory. Each vN.py calls make(kind, **params)."""
import bisect
import math
import os

import router


def _today_terms(ctx, s, t, k):
    cfg = ctx.cfg
    pop = ctx.pop
    floor = min(pop[s], pop[t]) - cfg.floor_relax_known * k
    return cfg, pop, floor


def make(kind, **P):
    def setup(ctx):
        router.precompute(ctx)
        if kind.startswith("mp"):
            # mutual proximity (Schnitzer et al. 2012), empirical: F_u(s) = share of u's
            # neighbour scores below s (ties count half)
            rows = []
            for u in range(ctx.n):
                a, b = ctx.off[u], ctx.off[u + 1]
                rows.append(sorted(ctx.sc[a:b]))
            ctx.sorted_rows = rows

    def F(ctx, u, s):
        r = ctx.sorted_rows[u]
        lo = bisect.bisect_left(r, s)
        hi = bisect.bisect_right(r, s)
        return (lo + 0.5 * (hi - lo)) / len(r)

    def journey(ctx, s, t, pressed, prev):
        k = len(pressed)
        beta = P.get("b0", 0.0) + P.get("b", 0.0) * k
        cfg, pop, floor = _today_terms(ctx, s, t, k)
        pl = ctx.pl
        lw = ctx.logwdeg
        ramp = cfg.w_known_ramp_fame_pctl * k
        pen = P.get("pen", "logwdeg")
        if pen == "logwdeg":
            pv = lw
        elif pen == "logdeg":
            pv = ctx.logdeg
        elif pen == "fame":  # -log(1 - pctl): popularity as fame percentile, RP3-style
            pv = ctx._fpen = getattr(ctx, "_fpen", None) or [-math.log(max(1.0 - x, 1e-3)) for x in pl]
        if kind == "rp3":
            # transition u->v ∝ sim/rowsum_u / pop_v^beta ; cost = -log of it (+ hop)
            hop = P.get("hop", 0.0)

            def cost(u, v, sim):
                c = -math.log(max(sim, 1e-6)) + lw[u] + hop
                if v != t:
                    c += beta * pv[v]
                return c
        elif kind == "today_pen":
            # today's cost + beta * pop_v penalty
            def cost(u, v, sim):
                c = (cfg.w_sim * (1 - sim) + cfg.w_jump * abs(pop[u] - pop[v])
                     + cfg.w_floor * max(0.0, floor - pop[v]) + cfg.w_hop)
                if v != t:
                    c += ramp * pl[v] + beta * pv[v]
                return c
        elif kind == "mp":
            wmp = P.get("wmp", cfg.w_sim)

            def cost(u, v, sim):
                mp = F(ctx, u, sim) * F(ctx, v, sim)
                c = (wmp * (1 - mp) + cfg.w_jump * abs(pop[u] - pop[v])
                     + cfg.w_floor * max(0.0, floor - pop[v]) + cfg.w_hop)
                if v != t:
                    c += ramp * pl[v] + beta * pv[v]
                return c
        return router.find_journey(ctx, s, t, pressed, cost)

    return setup, journey
