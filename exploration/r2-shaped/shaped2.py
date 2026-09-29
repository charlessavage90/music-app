"""EXPLORATORY engine v2 for r2-shaped: soft fame charge shaped by POSITION IN THE JOURNEY.

Graph distance to an endpoint (engine v1, shaped.py) fails because famous artists are all within
1-2 hops of each other: O'Jays > Earth, Wind & Fire > Men at Work > INXS > Midnight Oil is "free"
since every middle artist is a graph neighbour of one endpoint. Here the position is the artist's
place in the journey, found by meeting in the middle:

- forward search from s over states (artist, steps from s), backward search from t over (artist,
  steps from t), both on the same (symmetric) graph with per-request weights;
- the artist at step i from its nearer endpoint e has target
      T(i) = max(centre_k, fame(e) + A - (G + Gk*k)*(i-1) - Ak*k*[i==1]... , lb_k)
  with centre_k the compounding press ceiling (r1-rules v7) and lb_k = min(fame_s, fame_t) - X*k;
- charge(v, i) = B * max(0, log((1-T)/(1-fame(v))))  (steep at the top);
- the two halves meet at an artist m with |i - j| <= 1 (so each half's artists really are nearer
  their own endpoint); m pays the looser of its two charges.

Steps weaker than MINSIM cost SIMPEN extra (soft, local). Pressed artists are excluded; nothing else.
Press 0 = today's shipped cost exactly.
"""
from __future__ import annotations

import numpy as np

from shaped import BIG, centre_ceiling, setup_arrays

DEFAULTS = dict(mult=3.0, A=0.005, G=0.10, Gk=0.0, Ak=0.0, X=0.08, B=3.0, minsim=0.7, simpen=3.0,
                H=8, Blow=0.0, junk=0.0, hopk=0.0, minlen=0, maxlen=99, relief=1.0, relief_sim=0.5, relief_d=0.02)
# relief: charge multiplier for close (sim >= relief_sim), less famous (by relief_d) neighbours of the
# latest pressed artist -- the local stand-in for the artist just pressed.
# minlen / maxlen: journey hops must lie in [L0 + minlen, L0 + maxlen], L0 = press-0 journey's hops.


def base_costs(ctx, s, t, k):
    cfg = ctx.cfg
    pl, pop = ctx.S_pl, ctx.S_pop
    floor = max(0.0, min(pop[s], pop[t]) - cfg.floor_relax_known * k)
    return cfg.w_floor * np.maximum(0.0, floor - pop) + cfg.w_known_ramp_fame_pctl * k * pl, floor


def side_targets(ctx, e, k, c, lb, P):
    """T[i] for i = 1..H (index 0 unused)."""
    fe = ctx.S_pl[e]
    g = P["G"] + P["Gk"] * k
    T = np.empty(P["H"] + 1)
    for i in range(1, P["H"] + 1):
        x = fe + P["A"] - g * (i - 1) - (P["Ak"] * k if i == 1 else 0.0)
        T[i] = min(1.0, max(c, x, lb))
    T[0] = 1.0
    return T


def charge_matrix(ctx, T, lb, P):
    """(H+1, n) charge for artist v at step i."""
    pl = ctx.S_pl
    r_v = np.maximum(1.0 - pl, 1e-3)
    r_t = np.maximum(1.0 - T, 1e-3)[:, None]
    ch = P["B"] * np.maximum(0.0, np.log(r_t / r_v[None, :]))
    if P["Blow"] > 0:   # soft lower bound: charge for sitting far below the pair's own fame
        ch = ch + P["Blow"] * np.maximum(0.0, (lb - 0.15) - pl)[None, :] / 0.1
    if P["junk"] > 0:   # bottom-of-the-map junk (non-artists) and unmeasured fame
        ch = ch + P["junk"] * ((pl < 0.05))[None, :]
    return ch


def layered_search(ctx, src, nc, P, k):
    """Exact-step DP (by layers) from src, NON-BACKTRACKING (never u -> v -> u): two labels per
    (step, artist) with different predecessors. dist[i, v] = cheapest such walk of exactly i steps
    ending at v, each arrival at v on step i paying nc[i, v]. Returns dist, (pred1, pred2, dist2)."""
    n, H = ctx.n, P["H"]
    off, nbr, owner = ctx.S_off, ctx.S_nbr, ctx.S_owner
    stat = ctx.S_static + (P["hopk"] * k)
    if k > 0 and P["minsim"] > 0:
        stat = stat + np.where(ctx.S_sc < P["minsim"], P["simpen"], 0.0)
    d1 = np.full((H + 1, n), np.inf); d2 = np.full((H + 1, n), np.inf)
    p1 = np.full((H + 1, n), -1, dtype=np.int32); p2 = np.full((H + 1, n), -1, dtype=np.int32)
    d1[0, src] = 0.0
    starts = off[:-1]
    for i in range(1, H + 1):
        # entry (row v = owner, col u = nbr): extend u's label whose predecessor is not v
        use2 = p1[i - 1][nbr] == owner
        cand = np.where(use2, d2[i - 1][nbr], d1[i - 1][nbr]) + stat
        m1 = np.minimum.reduceat(cand, starts)
        hit = np.flatnonzero(cand == m1[owner])
        own = owner[hit]
        first = np.unique(own, return_index=True)[1]
        a1 = np.full(n, -1, dtype=np.int64); a1[own[first]] = hit[first]
        cand2 = cand.copy(); cand2[a1[a1 >= 0]] = np.inf
        m2 = np.minimum.reduceat(cand2, starts)
        hit2 = np.flatnonzero((cand2 == m2[owner]) & np.isfinite(cand2))
        own2 = owner[hit2]
        first2 = np.unique(own2, return_index=True)[1]
        a2 = np.full(n, -1, dtype=np.int64); a2[own2[first2]] = hit2[first2]
        p1[i] = np.where(a1 >= 0, nbr[np.maximum(a1, 0)], -1)
        p2[i] = np.where(a2 >= 0, nbr[np.maximum(a2, 0)], -1)
        d1[i] = m1 + nc[i]
        d2[i] = m2 + nc[i]
    return d1, (p1, p2, d2)


def unwind(pr, v, i):
    """Walk back from label 1 of (i, v)."""
    p1, p2, _ = pr
    out = [v]; slot = 1
    while i > 0:
        u = int(p1[i, v] if slot == 1 else p2[i, v])
        if u < 0:
            return None
        slot = 2 if p1[i - 1, u] == v else 1
        out.append(u); v = u; i -= 1
    return out[::-1]


def press0(ctx, s, t):
    cache = ctx.__dict__.setdefault("S2_L0", {})
    if (s, t) not in cache:
        res = ctx.find_journey(ctx.store, s, t, [], ctx.cfg)
        cache[(s, t)] = res[0] if res else None
    return cache[(s, t)]


def journey_k(ctx, s, t, pressed, P):
    k = len(pressed)
    p0 = press0(ctx, s, t)
    L0 = len(p0) - 1 if p0 else 2
    lo, hi = L0 + P["minlen"], L0 + P["maxlen"]
    base, _ = base_costs(ctx, s, t, k)
    c = centre_ceiling(ctx, pressed, P["mult"])
    lb = min(ctx.S_pl[s], ctx.S_pl[t]) - P["X"] * k
    H = P["H"]
    Ts, Tt = side_targets(ctx, s, k, c, lb, P), side_targets(ctx, t, k, c, lb, P)
    chs, cht = charge_matrix(ctx, Ts, lb, P), charge_matrix(ctx, Tt, lb, P)
    if P["relief"] != 1.0:
        x = pressed[-1]
        a, b = ctx.S_off[x], ctx.S_off[x + 1]
        nb, sc = ctx.S_nbr[a:b], ctx.S_sc[a:b]
        near = nb[(sc >= P["relief_sim"]) & (ctx.S_pl[nb] < ctx.S_pl[x] - P["relief_d"])]
        chs[:, near] *= P["relief"]
        cht[:, near] *= P["relief"]
    ncs = base[None, :] + chs
    nct = base[None, :] + cht
    hard = [x for x in pressed if x != s and x != t]
    for x in hard:
        ncs[:, x] = BIG
        nct[:, x] = BIG
    ncs[:, t] = BIG   # forward half never passes through t
    nct[:, s] = BIG
    ncs[:, s] = BIG
    nct[:, t] = BIG
    Df, pf = layered_search(ctx, s, ncs, P, k)
    Db, pb = layered_search(ctx, t, nct, P, k)
    n = ctx.n
    cands = []
    for i in range(1, H + 1):
        for j in range(1, H + 1):
            if abs(i - j) > 1 or i + j > hi:
                continue
            short = int(i + j < lo)   # shorter than press 0: only if nothing else is simple
            tot = Df[i] + Db[j] - np.maximum(ncs[i], nct[j])
            tot[s] = tot[t] = np.inf
            m = int(np.argmin(tot))
            if np.isfinite(tot[m]) and tot[m] < BIG:
                # keep a few best meeting artists for this (i, j) in case of overlap
                best = np.argpartition(tot, 19)[:20]
                for mm in best:
                    if np.isfinite(tot[mm]) and tot[mm] < BIG:
                        cands.append((short, float(tot[mm]), i, j, int(mm)))
    cands.sort()
    for short, tot, i, j, m in cands:
        a = unwind(pf, m, i)
        b = unwind(pb, m, j)
        if a is None or b is None:
            continue
        p = a + b[::-1][1:]
        if len(set(p)) == len(p) and len(p) > 2:
            return p
    import os   # no simple journey found at all: today's router (logged to runs/fallbacks.log if R2_LOG set)
    if os.environ.get("R2_LOG"):
        from pathlib import Path
        with open(Path(__file__).resolve().parent / "runs" / "fallbacks.log", "a", encoding="utf-8") as fh:
            fh.write(f"fallback {s} {t} k={k}\n")
    res = ctx.find_journey(ctx.store, s, t, ctx.known(pressed), ctx.cfg)
    return res[0] if res else None


def make(**over):
    P = dict(DEFAULTS, **over)

    def setup(ctx):
        setup_arrays(ctx)

    def journey(ctx, s, t, pressed, prev):
        setup_arrays(ctx)
        if s == t:
            return [s]
        if not pressed:
            return press0(ctx, s, t)
        return journey_k(ctx, s, t, pressed, P)

    journey.params = P
    return setup, journey
