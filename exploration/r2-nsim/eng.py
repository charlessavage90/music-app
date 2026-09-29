"""EXPLORATORY engine for r2-nsim (env-configurable; finalists bake settings into their own files).

Edge price u->v:  A_NSIM*(1-nsim) + A_JAC*(1-min(1,jac/J0)) + HOP
                  + BETA*max(0, fame_v - cap_v)          (soft, journey-shaped fame ceiling)
                  + GAMMA*max(0, low - fame_v)            (band floor: don't dive far below target)
                  + JUNK if fame_v < JUNKP                (bottom-of-scale junk)
cap_v = max(c, e_s - SLOPE*(hops_s(v)-1), e_t - SLOPE*(hops_t(v)-1)),  c = centre target.
Centre target c ratchets per press, stateless: for each pressed x: c=min(c, fame_x); c=1-MULT*(1-c).
"""
import os
import numpy as np
from scipy.sparse.csgraph import shortest_path
from common import setup_common, journey_from, exclude, mat, BIG
from shared import edge_jaccard

E = os.environ.get
A_NSIM = float(E("R2_ANSIM", "3"))
A_RAW = float(E("R2_ARAW", "0"))
A_JAC = float(E("R2_AJAC", "0"))
J0 = float(E("R2_J0", "0.25"))
HOP = float(E("R2_HOP", "0.3"))
BETA = float(E("R2_BETA", "4"))
GAMMA = float(E("R2_GAMMA", "0"))
LOWD = float(E("R2_LOWD", "0.35"))
LOWMID = float(E("R2_LOWMID", "0"))  # low >= LOWMID * less-famous endpoint
LOWF = float(E("R2_LOWF", "0"))
JUNKP = float(E("R2_JUNKP", "0"))
JUNK = float(E("R2_JUNK", "2"))
SLOPE = float(E("R2_SLOPE", "0"))
MULT = float(E("R2_MULT", "3"))
SCHED = E("R2_SCHED", "mult")  # mult | lin
CF = float(E("R2_CF", "0"))   # centre target never below CF * less-famous endpoint
STEP = float(E("R2_STEP", "0.06"))
FLOOR = float(E("R2_FLOOR", "0.1"))
P0 = E("R2_P0", "today")  # today | own
HARD = E("R2_HARD", "0") == "1"   # hard journey-shaped cap (graph hops), v5/v7 style
G = float(E("R2_G", "0.1"))
AH = float(E("R2_AH", "0.005"))
RPL = float(E("R2_RPL", "0"))       # stand-in pull: every interior node NOT a less-famous close neighbour of the latest pressed artist pays RPL
LMAX = int(E("R2_LMAX", "0"))       # if journey longer than LMAX artists, reroute with extra per-hop cost
BRIDGE = float(E("R2_BRIDGE", "0"))  # >0: allow ONE above-cap "bridge" artist per journey at this extra charge
RAMP = float(E("R2_RAMP", "0"))     # gentle pull: RAMP*fame_v on every interior node
MINJAC = float(E("R2_MINJAC", "0"))  # hard-ish: steps with jac below this cost +MJPEN
MJPEN = float(E("R2_MJPEN", "3"))


def setup(ctx):
    setup_common(ctx)
    r = ctx._r1
    jac = edge_jaccard(r["off"], r["nbr"], ctx.n).astype(np.float64)
    r["jac"] = jac
    base = A_NSIM * (1 - r["nsim"]) + A_RAW * (1 - r["sc"]) + A_JAC * (1 - np.minimum(1.0, jac / J0)) + HOP
    if MINJAC > 0:
        base = base + MJPEN * (jac < MINJAC)
    r["base2"] = base
    r["unw"] = mat(ctx, np.ones(len(r["nbr"])))


def centre(ctx, s, t, pressed):
    if SCHED == "lin":
        e = min(ctx.pl[s], ctx.pl[t])
        return max(FLOOR, e - STEP * len(pressed)) if pressed else 1.0
    c = 1.0
    if SCHED == "plin":
        for x in pressed:
            c = max(FLOOR, min(c, ctx.pl[x]) - STEP)
        return max(c, CF * min(ctx.pl[s], ctx.pl[t]))
    for x in pressed:
        c = min(c, ctx.pl[x])
        c = max(FLOOR, 1.0 - MULT * (1.0 - c))
    return c


def weights(ctx, s, t, pressed):
    r = ctx._r1
    pc = r["pc"]
    c = centre(ctx, s, t, pressed)
    if SLOPE > 0:
        h = shortest_path(r["unw"], unweighted=True, indices=[s, t])
        hs, ht = h[0], h[1]
        cap = np.maximum(c, np.maximum(pc[s] - SLOPE * (hs - 1), pc[t] - SLOPE * (ht - 1)))
    else:
        cap = np.full(ctx.n, c)
    cap = np.minimum(cap, 1.0)
    node = BETA * np.maximum(0.0, pc - cap)
    if GAMMA > 0 and pressed:
        low = LOWF * min(c, pc[s], pc[t]) if LOWF > 0 else max(c - LOWD, LOWMID * min(pc[s], pc[t]))
        node = node + GAMMA * np.maximum(0.0, low - pc)
    if JUNKP > 0:
        node = node + JUNK * (pc < JUNKP)
    node[t] = 0.0
    w = r["base2"] + node[r["nbr"]]
    return w


def hard_weights(ctx, s, t, pressed, c):
    r = ctx._r1
    pc = r["pc"]
    if "hops" not in r or r["hops"][0] != (s, t):
        h = shortest_path(r["unw"], unweighted=True, indices=[s, t])
        r["hops"] = ((s, t), h)
    hs, ht = r["hops"][1]
    cap = np.maximum(c, np.maximum(pc[s] + AH - G * (hs - 1), pc[t] + AH - G * (ht - 1)))
    node = RAMP * pc + BETA * np.maximum(0.0, pc - c)
    if GAMMA > 0:
        low = LOWF * min(c, pc[s], pc[t])
        node = node + GAMMA * np.maximum(0.0, low - pc)
    if JUNKP > 0:
        node = node + JUNK * (pc < JUNKP)
    if RPL > 0 and pressed:
        x = pressed[-1]
        lo, hi = r["off"][x], r["off"][x + 1]
        nb = r["nbr"][lo:hi]
        ok = nb[(r["sc"][lo:hi] >= 0.5) & (pc[nb] < pc[x])]
        extra = np.full(ctx.n, RPL)
        extra[ok] = 0.0
        node = node + extra
    node = np.where(pc > cap, BIG, node)
    node[s] = 0.0
    node[t] = 0.0
    return r["base2"] + node[r["nbr"]]


def bridged(ctx, s, t, pressed, w_capped, w_open, p_plain):
    """Best journey using exactly one otherwise-forbidden artist b (above the cap) as a bridge,
    if it beats the capped journey by more than the bridge charge. Else the capped journey."""
    from scipy.sparse.csgraph import dijkstra
    r = ctx._r1
    src, nbr = r["src"], r["nbr"]
    M = mat(ctx, w_capped)
    dA, pA = dijkstra(M, directed=True, indices=s, return_predecessors=True)
    MB = mat(ctx, w_capped[r["rev"]])
    dB, pB = dijkstra(MB, directed=True, indices=t, return_predecessors=True)
    forb = w_capped >= BIG
    cand = np.full(ctx.n, np.inf)
    arr_u = np.full(ctx.n, -1)
    # into b: dA[u] + w_open(u->b); out of b: w_open(b->v) + dB[v]
    into = dA[src] + w_open
    into[~forb] = np.inf  # only edges that the cap forbade (i.e. into a capped node)
    order = np.argsort(into, kind="stable")
    best_in = np.full(ctx.n, np.inf); best_in_u = np.full(ctx.n, -1)
    o = order[np.isfinite(into[order])]
    bn = nbr[o]
    first = np.unique(bn, return_index=True)
    best_in[first[0]] = into[o[first[1]]]; best_in_u[first[0]] = src[o[first[1]]]
    out = w_capped + dB[nbr]
    out[nbr == s] = np.inf
    order = np.argsort(out, kind="stable"); o = order[np.isfinite(out[order])]
    sn = src[o]
    first = np.unique(sn, return_index=True)
    best_out = np.full(ctx.n, np.inf); best_out_v = np.full(ctx.n, -1)
    best_out[first[0]] = out[o[first[1]]]; best_out_v[first[0]] = nbr[o[first[1]]]
    tot = best_in + best_out + BRIDGE
    tot[[s, t]] = np.inf
    if pressed:
        tot[np.asarray(pressed)] = np.inf
    b = int(np.argmin(tot))
    plain_cost = dA[t] if p_plain is not None else np.inf
    if not np.isfinite(tot[b]) or tot[b] >= plain_cost or tot[b] >= BIG:
        return p_plain
    from common import walk
    left = walk(pA, s, int(best_in_u[b]))
    v = int(best_out_v[b])
    right = [v]
    while right[-1] != t:
        q = pB[right[-1]]
        if q < 0:
            return p_plain
        right.append(int(q))
    p = left + [b] + right
    if len(set(p)) != len(p):
        return p_plain
    return p


def journey(ctx, s, t, pressed, prev):
    if not pressed and P0 == "today":
        res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
        return res[0] if res else None
    if HARD:
        c = centre(ctx, s, t, pressed) if pressed else 1.0
        while True:
            w0 = exclude(ctx, hard_weights(ctx, s, t, pressed, c), pressed, keep=(s, t))
            for extra in ((0.0, 0.5, 1.0, 2.0) if LMAX else (0.0,)):
                w = w0 + extra
                p = journey_from(ctx, w, s, t)
                if p is None or len(p) <= LMAX:
                    break
            if p is not None and len(p) > 2 and max(w[0:0].tolist() + [0]) < BIG:
                # reject paths that used a BIG edge (blocked)
                pass
            if BRIDGE > 0:
                w_open = np.where(w >= BIG, ctx._r1["base2"] + (w - w0)[0] if len(w) else 0, w)
                pb = bridged(ctx, s, t, pressed, w, w_open, p if (p is not None and not _uses_big(ctx, w, p)) else None)
                if pb is not None and len(pb) > 2:
                    return pb
            if p is not None and len(p) > 2 and not _uses_big(ctx, w, p):
                return p
            if c >= 1.0:
                return p
            c = min(1.0, c + 0.05)
    w = weights(ctx, s, t, pressed)
    w = exclude(ctx, w, pressed, keep=(s, t))
    return journey_from(ctx, w, s, t)


def _uses_big(ctx, w, p):
    r = ctx._r1
    off, nbr = r["off"], r["nbr"]
    for u, v in zip(p, p[1:]):
        lo, hi = off[u], off[u + 1]
        j = lo + np.searchsorted(nbr[lo:hi], v)
        if w[j] >= BIG:
            return True
    return False
